from celery import Celery

from backend.core.config import settings


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
    """
    Background document-processing task.

    The actual OCR and question extraction pipeline
    will be connected here next.
    """

    return {
        "document_id": document_id,
        "status": "processing_started",
    }