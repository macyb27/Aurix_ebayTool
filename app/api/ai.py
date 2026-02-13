"""AI Integration API Endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_current_user_id
from app.database import get_db
from app.services.ai_integration_service import AIIntegrationService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class AnalyzeRequest(BaseModel):
    """Request für AI-Analyse."""

    prompt: str


@router.post("/analyze")
async def analyze(
    data: AnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """AI-Analyse: LLM aufrufen, gegen FullAIResult validieren, in DB speichern."""
    service = AIIntegrationService(db)
    result = await service.analyze(data.prompt, user_id=user_id)
    return result.model_dump(mode="json")
