from sqlalchemy import Boolean, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class ConfigurationModel(Base):
    __tablename__ = "configurations"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cycle_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    signal_timings: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_preset: Mapped[bool] = mapped_column(Boolean, nullable=False,
                                            default=False)
    cycle_utilization: Mapped[float | None] = mapped_column(Float,
                                                            nullable=True)
    times_simulated: Mapped[int] = mapped_column(Integer, nullable=False,
                                                 default=0)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True),
                                            nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True),
                                            nullable=False)
