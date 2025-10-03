import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user
from app.db.session import get_db
from app.models.file import FileObject
from app.schemas.file import FileRead
from app.utils import s3

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileRead)
async def upload_file(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> FileObject:
    data = await file.read()
    key = f"uploads/{uuid.uuid4()}_{file.filename}"
    content_type = file.content_type or "application/octet-stream"
    s3.upload_bytes(key, data, content_type)
    record = FileObject(
        key=key,
        bucket=s3.settings.s3_bucket,
        mime=content_type,
        size=len(data),
        uploader_id=current_user.id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{file_id}")
def download_file(file_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_active_user)) -> Response:
    record = db.get(FileObject, file_id)
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    data = s3.download_bytes(record.key, record.bucket)
    return Response(content=data, media_type=record.mime)
