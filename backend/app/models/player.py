import uuid
from typing import List
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Season(Base):
    __tablename__ = "seasons"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    year: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    player_seasons: Mapped[List["PlayerSeason"]] = relationship(back_populates="season")
    franchise_seasons: Mapped[List["FranchiseSeason"]] = relationship(back_populates="season")


class Franchise(Base):
    __tablename__ = "franchises"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)

    player_seasons: Mapped[List["PlayerSeason"]] = relationship(back_populates="franchise")
    franchise_seasons: Mapped[List["FranchiseSeason"]] = relationship(back_populates="franchise")


class Player(Base):
    __tablename__ = "players"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # 'BAT', 'BOWL', 'ALLROUNDER', 'WK'
    is_overseas: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    player_seasons: Mapped[List["PlayerSeason"]] = relationship(back_populates="player")
    draft_picks: Mapped[List["DraftPick"]] = relationship(back_populates="player")


class PlayerSeason(Base):
    __tablename__ = "player_seasons"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    player_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    season_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False, index=True)
    franchise_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("franchises.id", ondelete="CASCADE"), nullable=False, index=True)

    balls_faced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    runs_scored: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    balls_bowled: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wickets_taken: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    raw_batting_rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    raw_bowling_rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    percentile_batting: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    percentile_bowling: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    credit_cost: Mapped[float] = mapped_column(Float, default=6.0, nullable=False)

    player: Mapped["Player"] = relationship(back_populates="player_seasons")
    season: Mapped["Season"] = relationship(back_populates="player_seasons")
    franchise: Mapped["Franchise"] = relationship(back_populates="player_seasons")

    __table_args__ = (
        UniqueConstraint("player_id", "season_id", "franchise_id", name="uq_player_season_franchise"),
    )
