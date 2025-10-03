from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SKU(Base):
    __tablename__ = "skus"
    __table_args__ = (UniqueConstraint("code", name="uq_sku_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    barcodes: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    uom: Mapped[str] = mapped_column(String(16), default="EA", nullable=False)
    weight_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    length_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    width_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_file_id: Mapped[int | None] = mapped_column(ForeignKey("files.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
