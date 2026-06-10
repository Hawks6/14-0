import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class DraftSession(Base):
    __tablename__ = "draft_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), default="IN_PROGRESS", nullable=False)
    budget_remaining: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    picks: Mapped[list["DraftPick"]] = relationship(back_populates="draft_session", cascade="all, delete-orphan")


class DraftPick(Base):
    __tablename__ = "draft_picks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    draft_session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("draft_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    pick_number: Mapped[int] = mapped_column(Integer, nullable=False)

    draft_session: Mapped["DraftSession"] = relationship(back_populates="picks")
    player: Mapped["Player"] = relationship(back_populates="draft_picks")
