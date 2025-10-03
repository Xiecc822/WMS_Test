from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    po_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("DRAFT", "OPEN", "RECEIVING", "CLOSED", "CANCELLED", name="po_status"),
        default="OPEN",
        nullable=False,
    )
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    lines: Mapped[list["PurchaseOrderLine"]] = relationship(back_populates="purchase_order")


class PurchaseOrderLine(Base):
    __tablename__ = "purchase_order_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    po_id: Mapped[int] = mapped_column(ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    sku_id: Mapped[int] = mapped_column(ForeignKey("skus.id"), nullable=False)
    qty_ordered: Mapped[int] = mapped_column(Integer, nullable=False)
    qty_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    purchase_order: Mapped[PurchaseOrder] = relationship(back_populates="lines")


class Receipt(Base):
    __tablename__ = "receipts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    po_id: Mapped[int] = mapped_column(ForeignKey("purchase_orders.id"), nullable=False)
    receipt_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        Enum("OPEN", "PUTAWAY", "CLOSED", name="receipt_status"), default="OPEN", nullable=False
    )
    received_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    lines: Mapped[list["ReceiptLine"]] = relationship(back_populates="receipt")


class ReceiptLine(Base):
    __tablename__ = "receipt_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    receipt_id: Mapped[int] = mapped_column(ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False)
    sku_id: Mapped[int] = mapped_column(ForeignKey("skus.id"), nullable=False)
    qty_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    to_location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"), nullable=True)

    receipt: Mapped[Receipt] = relationship(back_populates="lines")


class SalesOrder(Base):
    __tablename__ = "sales_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    so_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(
            "DRAFT",
            "OPEN",
            "ALLOCATED",
            "PICKING",
            "PACKED",
            "SHIPPED",
            "CANCELLED",
            name="so_status",
        ),
        default="OPEN",
        nullable=False,
    )
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    ship_to_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    carrier_service: Mapped[str | None] = mapped_column(String(64), nullable=True)

    lines: Mapped[list["SalesOrderLine"]] = relationship(back_populates="sales_order")


class SalesOrderLine(Base):
    __tablename__ = "sales_order_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    so_id: Mapped[int] = mapped_column(ForeignKey("sales_orders.id", ondelete="CASCADE"), nullable=False)
    sku_id: Mapped[int] = mapped_column(ForeignKey("skus.id"), nullable=False)
    qty_ordered: Mapped[int] = mapped_column(Integer, nullable=False)
    qty_allocated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    qty_shipped: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    sales_order: Mapped[SalesOrder] = relationship(back_populates="lines")
