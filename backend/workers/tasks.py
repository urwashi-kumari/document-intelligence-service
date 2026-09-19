import json

from celery import Celery
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.models.document import Document
from backend.models.question import Question
from backend.services.document_processor import extract_text_from_document
from backend.services.question_extractor import extract_questions


celery_app = Celery(
    "document_intelligence",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(
    name="process_document",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_document(self, document_id: int):
    db: Session = SessionLocal()

    try:
        document = db.get(Document, document_id)

        if document is None:
            raise ValueError(
                f"Document {document_id} was not found."
            )

        document.status = "processing"
        document.processing_error = None
        db.commit()

        # Extract text from PDF or image
        extracted_text = extract_text_from_document(
            document.file_path,
            document.file_type,
        )

        # Store extracted text
        document.extracted_text = extracted_text

        # Extract questions from the text
        questions = extract_questions(extracted_text)

        # Remove previously extracted questions if reprocessing
        db.query(Question).filter(
            Question.document_id == document.id
        ).delete()

        # Save extracted questions
        for question_data in questions:
            question = Question(
                document_id=document.id,
                question_number=question_data["question_number"],
                question_text=question_data["question_text"],
                question_type=question_data["question_type"],
                options_json=json.dumps(question_data["options"]),
                extraction_confidence=question_data[
                    "extraction_confidence"
                ],
                review_status=question_data["review_status"],
                source_pages=question_data["source_pages"],
            )

            db.add(question)

        # Determine final document status
        if not extracted_text.strip():
            document.status = "review"
            document.processing_error = (
                "No text could be extracted from the document."
            )
        else:
            document.status = "processed"

        db.commit()

        return {
            "document_id": document_id,
            "status": document.status,
            "text_length": len(extracted_text),
            "questions_extracted": len(questions),
        }

    except Exception as exc:
        db.rollback()

        document = db.get(Document, document_id)

        if document is not None:
            document.status = "failed"
            document.processing_error = str(exc)
            db.commit()

        raise

    finally:
        db.close()