from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas import AnalysisResponse
from utils.database import get_db
from services.analysis_service import get_analysis_by_id

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: int, db: AsyncSession = Depends(get_db)):
    analysis = await get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis
