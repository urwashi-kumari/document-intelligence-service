from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.auth import get_current_user
from backend.core.database import get_db
from backend.models.document import Document
from backend.models.question import Question
from backend.models.user import User


router = APIRouter(
    prefix="/documents",
    tags=["Questions"],
)


@router.get("/{document_id}/questions")
def get_document_questions(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Make sure the document belongs to the logged-in user
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    questions = (
        db.query(Question)
        .filter(Question.document_id == document_id)
        .order_by(Question.id)
        .all()
    )

    return {
        "document_id": document_id,
        "count": len(questions),
        "questions": [
            {
                "id": question.id,
                "question_number": question.question_number,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "options": question.options_json,
                "answer": question.answer,
                "answer_confidence": question.answer_confidence,
                "extraction_confidence": question.extraction_confidence,
                "review_status": question.review_status,
                "source_pages": question.source_pages,
            }
            for question in questions
        ],
    }