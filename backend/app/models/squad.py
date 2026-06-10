import uuid
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class FranchiseSeason(Base):
    __tablename__ = "franchise_seasons"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    franchise_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("franchises.id", ondelete="CASCADE"), nullable=False, index=True)
    season_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False, index=True)

    franchise: Mapped["Franchise"] = relationship(back_populates="franchise_seasons")
    season: Mapped["Season"] = relationship(back_populates="franchise_seasons")

    __table_args__ = (
        UniqueConstraint("franchise_id", "season_id", name="uq_franchise_season"),
    )
