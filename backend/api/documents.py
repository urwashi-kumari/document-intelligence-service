from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.api.auth import get_current_user
from backend.core.config import settings
from backend.core.database import get_db
from backend.models.document import Document
from backend.models.user import User
from backend.schemas.document import DocumentResponse
from backend.workers.tasks import process_document


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}

CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A filename is required.",
        )

    original_filename = Path(file.filename).name
    extension = Path(original_filename).suffix.lower()

    # Validate file extension
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Allowed types: PDF, JPG, JPEG, PNG.",
        )

    # Validate MIME type when provided
    expected_content_type = CONTENT_TYPES[extension]

    if file.content_type and file.content_type != expected_content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid content type. Expected {expected_content_type} "
                f"for {extension} files."
            ),
        )

    # Prepare upload directory
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate a unique stored filename
    stored_filename = f"{uuid4().hex}{extension}"
    file_path = upload_dir / stored_filename

    max_size = settings.max_file_size_mb * 1024 * 1024
    total_size = 0

    try:
        with file_path.open("wb") as output_file:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > max_size:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=(
                            f"File size exceeds the maximum allowed size "
                            f"of {settings.max_file_size_mb} MB."
                        ),
                    )

                output_file.write(chunk)

    except HTTPException:
        if file_path.exists():
            file_path.unlink()

        raise

    except Exception:
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store the uploaded document.",
        )

    finally:
        await file.close()

    document = Document(
        user_id=current_user.id,
        filename=original_filename,
        file_path=str(file_path),
        file_type=extension.lstrip("."),
        file_size=total_size,
        status="uploaded",
    )

    db.add(document)
    db.commit()
    db.refresh(document)
    process_document.delay(document.id)

    return document