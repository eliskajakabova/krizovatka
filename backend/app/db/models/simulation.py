from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class SimulationModel(Base):
    __tablename__ = "simulations"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    config_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("configurations.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    simulation_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    traffic_intensity: Mapped[dict] = mapped_column(JSON, nullable=False)

    started_at: Mapped[str] = mapped_column(DateTime(timezone=True),
                                            nullable=False, index=True)
    completed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True),
                                                     nullable=True)
    elapsed_time: Mapped[float | None] = mapped_column(Float, nullable=True)

    total_vehicles_generated: Mapped[int | None] = mapped_column(Integer,
                                                                 nullable=True)
    total_vehicles_passed: Mapped[int | None] = mapped_column(Integer,
                                                              nullable=True)
    total_vehicles_waiting: Mapped[int | None] = mapped_column(Integer,
                                                               nullable=True)
    average_wait_time: Mapped[float | None] = mapped_column(Float,
                                                            nullable=True)
    max_wait_time: Mapped[float | None] = mapped_column(Float, nullable=True)
    average_queue_length: Mapped[float | None] = mapped_column(Float,
                                                               nullable=True)
    max_queue_length: Mapped[int | None] = mapped_column(Integer,
                                                         nullable=True)
    intersection_utilization: Mapped[float | None] = mapped_column(
        Float, nullable=True)
