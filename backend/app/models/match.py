import uuid
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class MatchLog(Base):
    __tablename__ = "match_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    ball_number: Mapped[int] = mapped_column(Integer, nullable=False)
    over_number: Mapped[int] = mapped_column(Integer, nullable=False)
    
    batter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    bowler_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    
    runs_scored: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    extras: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wicket_type: Mapped[str] = mapped_column(String(50), nullable=True)
    event_meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    batter: Mapped["Player"] = relationship("Player", foreign_keys=[batter_id])
    bowler: Mapped["Player"] = relationship("Player", foreign_keys=[bowler_id])
