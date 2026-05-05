from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import CHAR, Boolean, ForeignKey, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    language: Mapped[str] = mapped_column(String(10))
    text_hash: Mapped[Optional[str]] = mapped_column(CHAR(64), default=None)
    coverage_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), default=None)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    )


class AnalysisToken(Base):
    __tablename__ = "analysis_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id", ondelete="CASCADE"))
    surface: Mapped[str] = mapped_column(Text)
    lemma: Mapped[str] = mapped_column(Text)
    grade_level: Mapped[Optional[int]] = mapped_column(default=None)
    is_known: Mapped[Optional[bool]] = mapped_column(Boolean, default=None)
