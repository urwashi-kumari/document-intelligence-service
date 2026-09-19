from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    question_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    question_type: Mapped[str] = mapped_column(
        String(50),
        default="unknown",
        nullable=False,
    )

    options_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    answer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    answer_confidence: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    extraction_confidence: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    review_status: Mapped[str] = mapped_column(
        String(30),
        default="review",
        nullable=False,
    )

    source_pages: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )