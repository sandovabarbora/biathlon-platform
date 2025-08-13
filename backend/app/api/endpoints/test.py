"""Test endpoints for data verification"""

from fastapi import APIRouter
from typing import Dict
import biathlonresults as br
from datetime import datetime

router = APIRouter()

@router.get("/test-connection")
async def test_connection() -> Dict:
    """Test if server is running and IBU API is accessible"""
    try:
        # Test IBU API connection
        cups = br.cups("2425")
        has_data = len(cups) > 0 if cups else False
        
        return {
            "status": "connected",
            "timestamp": datetime.now().isoformat(),
            "ibu_api": "connected" if has_data else "no data",
            "season": "2024/2025",
            "data_source": "REAL IBU API"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/data-status")
async def data_status() -> Dict:
    """Get detailed status of data sources"""
    try:
        # Check athletes
        from app.services.ibu_full_service import ibu_service
        athletes = ibu_service.get_athletes(nation="CZE", limit=5)
        
        # Check races
        races = ibu_service.get_recent_races(limit=5)
        
        return {
            "status": "operational",
            "data_sources": {
                "athletes": {
                    "status": "connected",
                    "count": len(athletes),
                    "sample": athletes[0] if athletes else None
                },
                "races": {
                    "status": "connected",
                    "count": len(races),
                    "sample": races[0] if races else None
                },
                "api_version": "IBU Datacenter API v1",
                "last_update": datetime.now().isoformat()
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
