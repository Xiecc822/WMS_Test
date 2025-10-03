from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PickTask(Base):
    __tablename__ = "pick_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    so_id: Mapped[int] = mapped_column(ForeignKey("sales_orders.id"), nullable=False, index=True)
    task_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        Enum("OPEN", "IN_PROGRESS", "DONE", name="pick_task_status"),
        default="OPEN",
        nullable=False,
    )
    picker_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    lines: Mapped[list["PickTaskLine"]] = relationship(back_populates="task")
    sales_order: Mapped["SalesOrder"] = relationship("SalesOrder", backref="pick_tasks")


class PickTaskLine(Base):
    __tablename__ = "pick_task_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("pick_tasks.id", ondelete="CASCADE"), nullable=False)
    sku_id: Mapped[int] = mapped_column(ForeignKey("skus.id"), nullable=False)
    from_location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)

    task: Mapped[PickTask] = relationship(back_populates="lines")


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    so_id: Mapped[int] = mapped_column(ForeignKey("sales_orders.id"), nullable=False, index=True)
    ship_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        Enum("READY", "LABELED", "SHIPPED", name="shipment_status"),
        default="READY",
        nullable=False,
    )
    weight_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parcels: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    label_file_id: Mapped[int | None] = mapped_column(ForeignKey("files.id"), nullable=True)
    tracking_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    sales_order: Mapped["SalesOrder"] = relationship("SalesOrder", backref="shipments")
