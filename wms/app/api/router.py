from fastapi import APIRouter

from app.api.v1 import (
    auth,
    carriers,
    customers,
    files,
    inbound,
    inventory,
    locations,
    logs,
    purchase,
    roles,
    sales,
    skus,
    suppliers,
    warehouses,
    users,
)

router = APIRouter()
router.include_router(auth.router, prefix="/v1")
router.include_router(users.router, prefix="/v1")
router.include_router(roles.router, prefix="/v1")
router.include_router(roles.permissions_router, prefix="/v1")
router.include_router(warehouses.router, prefix="/v1")
router.include_router(locations.router, prefix="/v1")
router.include_router(suppliers.router, prefix="/v1")
router.include_router(customers.router, prefix="/v1")
router.include_router(skus.router, prefix="/v1")
router.include_router(inventory.router, prefix="/v1")
router.include_router(files.router, prefix="/v1")
router.include_router(purchase.router, prefix="/v1")
router.include_router(inbound.router, prefix="/v1")
router.include_router(sales.router, prefix="/v1")
router.include_router(carriers.router, prefix="/v1")
router.include_router(logs.router, prefix="/v1")


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
