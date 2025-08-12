"""Test endpoint to verify data loading"""

from fastapi import APIRouter
from app.services.data_service import data_service

router = APIRouter()

@router.get("/test")
async def test_data():
    """Test that data loads correctly"""
    
    # Get Czech athletes
    czech = data_service.get_athletes(nation="CZE", limit=5)
    
    return {
        "status": "ok",
        "data_loaded": {
            "results": len(data_service.results_df) if data_service.results_df is not None else 0,
            "czech_athletes": len(czech),
            "sample_athlete": czech[0] if czech else None
        }
    }
