from app.tasks.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.shipping import generate_label


@celery_app.task
def create_label(shipment_id: int) -> None:
    with SessionLocal() as db:
        generate_label(db, shipment_id=shipment_id)


@celery_app.task
def poll_tracking() -> None:  # pragma: no cover - placeholder
    return None
