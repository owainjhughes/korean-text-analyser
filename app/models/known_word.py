from datetime import datetime
from typing import Any, Optional

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class KnownWord(Base):
    __tablename__ = "known_words"
    __table_args__ = (UniqueConstraint("user_id", "language", "lemma"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    language: Mapped[str] = mapped_column(String(10))  # 'ko', 'ja', 'de', ...
    lemma: Mapped[str] = mapped_column(Text)
    grade_level: Mapped[Optional[int]] = mapped_column(default=None)
    status: Mapped[str] = mapped_column(String(20), server_default=text("'unknown'"))
    extra: Mapped[Optional[dict[str, Any]]] = mapped_column("metadata", JSONB, default=None)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    )
