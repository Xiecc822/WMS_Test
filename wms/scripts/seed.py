from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.org import Customer, Location, Supplier, Warehouse
from app.models.product import SKU
from app.models.rbac import Permission, Role
from app.models.user import User
from app.utils.hashing import get_password_hash


def seed() -> None:
    with SessionLocal() as db:
        # Permissions
        perm_codes = [
            "view_users",
            "manage_users",
            "view_roles",
            "manage_roles",
            "manage_master",
            "view_inventory",
            "adjust_inventory",
            "create_po",
            "receive_inbound",
            "allocate",
            "pick",
            "ship",
            "view_logs",
        ]
        perms = {}
        for code in perm_codes:
            perm = db.execute(select(Permission).where(Permission.code == code)).scalar_one_or_none()
            if not perm:
                perm = Permission(code=code, description=code.replace("_", " ").title())
                db.add(perm)
                db.flush()
            perms[code] = perm

        admin_role = db.execute(select(Role).where(Role.name == "Administrator")).scalar_one_or_none()
        if not admin_role:
            admin_role = Role(name="Administrator", description="Superuser", permissions=list(perms.values()))
            db.add(admin_role)

        # Admin user
        admin_user = db.execute(select(User).where(User.email == "admin@example.com")).scalar_one_or_none()
        if not admin_user:
            admin_user = User(
                email="admin@example.com",
                full_name="Admin",
                password_hash=get_password_hash("Admin123!"),
                is_superuser=True,
            )
            admin_user.roles.append(admin_role)
            db.add(admin_user)

        warehouse = db.execute(select(Warehouse).where(Warehouse.code == "SFO-1")).scalar_one_or_none()
        if not warehouse:
            warehouse = Warehouse(code="SFO-1", name="San Francisco Warehouse", address_json={"city": "San Francisco"})
            db.add(warehouse)
            db.flush()

        location = db.execute(select(Location).where(Location.code == "STAGE-01")).scalar_one_or_none()
        if not location:
            location = Location(warehouse_id=warehouse.id, code="STAGE-01", type="STAGING")
            db.add(location)

        supplier = db.execute(select(Supplier).where(Supplier.code == "SUP-001")).scalar_one_or_none()
        if not supplier:
            supplier = Supplier(code="SUP-001", name="Default Supplier")
            db.add(supplier)

        customer = db.execute(select(Customer).where(Customer.code == "CUST-001")).scalar_one_or_none()
        if not customer:
            customer = Customer(code="CUST-001", name="Default Customer")
            db.add(customer)

        for idx in range(1, 4):
            code = f"SKU-{idx:03d}"
            sku = db.execute(select(SKU).where(SKU.code == code)).scalar_one_or_none()
            if not sku:
                db.add(SKU(code=code, name=f"Sample SKU {idx}", uom="EA"))

        db.commit()


if __name__ == "__main__":
    seed()
