"""Vision API Endpoints - Bildanalyse."""

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

from app.services.vision_service import VisionService

router = APIRouter()


class AnalyzeUrlRequest(BaseModel):
    """Request für URL-basierte Analyse."""

    image_url: str


@router.post("/analyze-url")
async def analyze_image_url(data: AnalyzeUrlRequest):
    """Produkt aus Bild-URL analysieren."""
    service = VisionService()
    try:
        result = await service.analyze_image(image_url=data.image_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-upload")
async def analyze_image_upload(file: UploadFile):
    """Produkt aus hochgeladenem Bild analysieren."""
    import tempfile
    import os

    service = VisionService()
    suffix = os.path.splitext(file.filename or "image")[1] or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    try:
        result = await service.analyze_image(image_path=tmp_path)
        return result
    finally:
        os.unlink(tmp_path)
