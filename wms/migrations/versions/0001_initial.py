"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2024-01-01 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=32), nullable=False, unique=True),
        sa.Column("name", sa.String(length=100), nullable=False),
    )

    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("description", sa.String(length=255)),
    )

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=64), nullable=False, unique=True),
        sa.Column("description", sa.String(length=255)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255)),
        sa.Column("dept_id", sa.Integer(), sa.ForeignKey("departments.id")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column(
            "permission_id",
            sa.Integer(),
            sa.ForeignKey("permissions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "login_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("ip", sa.String(length=64)),
        sa.Column("user_agent", sa.String(length=255)),
        sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "op_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("entity", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.Integer()),
        sa.Column("before_json", sa.JSON()),
        sa.Column("after_json", sa.JSON()),
        sa.Column("at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "warehouses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=32), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address_json", sa.JSON()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )

    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("warehouse_id", sa.Integer(), sa.ForeignKey("warehouses.id"), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False, server_default="STORAGE"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.UniqueConstraint("warehouse_id", "code", name="uq_location_code"),
    )

    op.create_table(
        "suppliers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=32), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("contact_json", sa.JSON()),
    )

    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=32), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("contact_json", sa.JSON()),
        sa.Column("ship_to_json", sa.JSON()),
    )

    op.create_table(
        "files",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=255), nullable=False, unique=True),
        sa.Column("bucket", sa.String(length=128), nullable=False),
        sa.Column("mime", sa.String(length=128), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("uploader_id", sa.Integer()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("meta_json", sa.JSON()),
    )

    op.create_table(
        "skus",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("barcodes", sa.JSON()),
        sa.Column("uom", sa.String(length=16), nullable=False, server_default="EA"),
        sa.Column("weight_g", sa.Integer()),
        sa.Column("length_mm", sa.Integer()),
        sa.Column("width_mm", sa.Integer()),
        sa.Column("height_mm", sa.Integer()),
        sa.Column("image_file_id", sa.Integer(), sa.ForeignKey("files.id")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )

    op.create_table(
        "inventory_balance",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("warehouse_id", sa.Integer(), sa.ForeignKey("warehouses.id"), nullable=False),
        sa.Column("sku_id", sa.Integer(), sa.ForeignKey("skus.id"), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("on_hand", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reserved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("available", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.UniqueConstraint("warehouse_id", "sku_id", "location_id", name="uq_inventory_balance"),
    )

    op.create_table(
        "inventory_ledger",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ts", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("type", sa.Enum("IN", "OUT", "ADJ", "ALLOC", "DEALLOC", "MOVE", name="ledger_type"), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), sa.ForeignKey("warehouses.id"), nullable=False),
        sa.Column("sku_id", sa.Integer(), sa.ForeignKey("skus.id"), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("ref_type", sa.String(length=64)),
        sa.Column("ref_id", sa.Integer()),
        sa.Column("ref_no", sa.String(length=64)),
        sa.Column("idempotency_key", sa.String(length=64), unique=True),
    )

    op.create_table(
        "purchase_orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("po_no", sa.String(length=64), nullable=False, unique=True),
        sa.Column("supplier_id", sa.Integer(), sa.ForeignKey("suppliers.id"), nullable=False),
        sa.Column("status", sa.Enum("DRAFT", "OPEN", "RECEIVING", "CLOSED", "CANCELLED", name="po_status"), nullable=False, server_default="OPEN"),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "purchase_order_lines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("po_id", sa.Integer(), sa.ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sku_id", sa.Integer(), sa.ForeignKey("skus.id"), nullable=False),
        sa.Column("qty_ordered", sa.Integer(), nullable=False),
        sa.Column("qty_received", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "receipts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("po_id", sa.Integer(), sa.ForeignKey("purchase_orders.id"), nullable=False),
        sa.Column("receipt_no", sa.String(length=64), nullable=False, unique=True),
        sa.Column("status", sa.Enum("OPEN", "PUTAWAY", "CLOSED", name="receipt_status"), nullable=False, server_default="OPEN"),
        sa.Column("received_at", sa.DateTime()),
    )

    op.create_table(
        "receipt_lines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("receipt_id", sa.Integer(), sa.ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sku_id", sa.Integer(), sa.ForeignKey("skus.id"), nullable=False),
        sa.Column("qty_received", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("to_location_id", sa.Integer(), sa.ForeignKey("locations.id")),
    )

    op.create_table(
        "sales_orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("so_no", sa.String(length=64), nullable=False, unique=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("status", sa.Enum("DRAFT", "OPEN", "ALLOCATED", "PICKING", "PACKED", "SHIPPED", "CANCELLED", name="so_status"), nullable=False, server_default="OPEN"),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("ship_to_json", sa.JSON()),
        sa.Column("carrier_service", sa.String(length=64)),
    )

    op.create_table(
        "sales_order_lines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("so_id", sa.Integer(), sa.ForeignKey("sales_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sku_id", sa.Integer(), sa.ForeignKey("skus.id"), nullable=False),
        sa.Column("qty_ordered", sa.Integer(), nullable=False),
        sa.Column("qty_allocated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("qty_shipped", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "pick_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("so_id", sa.Integer(), sa.ForeignKey("sales_orders.id"), nullable=False),
        sa.Column("task_no", sa.String(length=64), nullable=False, unique=True),
        sa.Column("status", sa.Enum("OPEN", "IN_PROGRESS", "DONE", name="pick_task_status"), nullable=False, server_default="OPEN"),
        sa.Column("picker_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "pick_task_lines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("pick_tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sku_id", sa.Integer(), sa.ForeignKey("skus.id"), nullable=False),
        sa.Column("from_location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
    )

    op.create_table(
        "shipments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("so_id", sa.Integer(), sa.ForeignKey("sales_orders.id"), nullable=False),
        sa.Column("ship_no", sa.String(length=64), nullable=False, unique=True),
        sa.Column("status", sa.Enum("READY", "LABELED", "SHIPPED", name="shipment_status"), nullable=False, server_default="READY"),
        sa.Column("weight_g", sa.Integer()),
        sa.Column("parcels", sa.JSON()),
        sa.Column("label_file_id", sa.Integer(), sa.ForeignKey("files.id")),
        sa.Column("tracking_no", sa.String(length=64)),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("shipments")
    op.drop_table("pick_task_lines")
    op.drop_table("pick_tasks")
    op.drop_table("sales_order_lines")
    op.drop_table("sales_orders")
    op.drop_table("receipt_lines")
    op.drop_table("receipts")
    op.drop_table("purchase_order_lines")
    op.drop_table("purchase_orders")
    op.drop_table("inventory_ledger")
    op.drop_table("inventory_balance")
    op.drop_table("skus")
    op.drop_table("files")
    op.drop_table("customers")
    op.drop_table("suppliers")
    op.drop_table("locations")
    op.drop_table("warehouses")
    op.drop_table("op_log")
    op.drop_table("login_log")
    op.drop_table("user_roles")
    op.drop_table("role_permissions")
    op.drop_table("users")
    op.drop_table("roles")
    op.drop_table("permissions")
    op.drop_table("departments")
