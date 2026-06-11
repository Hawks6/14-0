import uuid
from sqlalchemy import String, Integer, ForeignKey, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Match(Base):
    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    draft_session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("draft_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    match_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="SCHEDULED", nullable=False)
    user_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user_wickets: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    opponent_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    opponent_wickets: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    winner: Mapped[str] = mapped_column(String(50), nullable=True) # "USER", "OPPONENT", "TIE"
    opponent_team: Mapped[str] = mapped_column(String(100), nullable=True)
    user_team: Mapped[str] = mapped_column(String(100), default="Your XI", server_default="Your XI", nullable=False)
    user_overs: Mapped[float] = mapped_column(Float, default=0.0, server_default="0.0", nullable=False)
    opponent_overs: Mapped[float] = mapped_column(Float, default=0.0, server_default="0.0", nullable=False)

    draft_session: Mapped["DraftSession"] = relationship("DraftSession")
    events: Mapped[list["MatchEvent"]] = relationship(back_populates="match", cascade="all, delete-orphan")


class MatchEvent(Base):
    __tablename__ = "match_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    ball_number: Mapped[int] = mapped_column(Integer, nullable=False)
    over_number: Mapped[int] = mapped_column(Integer, nullable=False)
    
    batter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    bowler_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    
    runs_scored: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    extras: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wicket_type: Mapped[str] = mapped_column(String(50), nullable=True)
    event_meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    match: Mapped["Match"] = relationship(back_populates="events")
    batter: Mapped["Player"] = relationship("Player", foreign_keys=[batter_id])
    bowler: Mapped["Player"] = relationship("Player", foreign_keys=[bowler_id])
