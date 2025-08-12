"""Test endpoint to verify API connection"""

from fastapi import APIRouter, HTTPException
import biathlonresults as br
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Správná IBU ID českých biatlonistek
CZECH_WOMEN_IDS = {
    "VOBORNIKOVA": "BTCZE23105200001",
    "DAVIDOVA": "BTCZE20301199701",
    "JISLOVA": "BTCZE22807199401",
    "CHARVATOVA": "BTCZE20102199301",
    "OTCOVSKA": "BTCZE22107200001"
}

@router.get("/test-connection")
async def test_api_connection():
    """Test if biathlonresults API is working"""
    try:
        current_season = "2425"
        
        # Test cups
        cups = br.cups(current_season)
        cup_count = len(cups) if cups else 0
        
        # Test events
        events = br.events(current_season, level=br.consts.LevelType.BMW_IBU_WC)
        event_count = len(events) if events else 0
        
        # Get sample race results
        sample_results = None
        czech_found = 0
        czech_athletes = []
        
        if events:
            # Get latest event
            for event in reversed(events):
                competitions = br.competitions(event["EventId"])
                if competitions:
                    race_id = competitions[-1]["RaceId"]
                    results = br.results(race_id)
                    sample_results = len(results.get("Results", []))
                    
                    # Find Czech athletes
                    for r in results.get("Results", []):
                        if r.get("Nat") == "CZE":
                            czech_found += 1
                            czech_athletes.append({
                                "name": r.get("Name"),
                                "ibu_id": r.get("IBUId"),
                                "rank": r.get("Rank")
                            })
                    
                    if sample_results:
                        break
        
        return {
            "status": "connected",
            "api_working": True,
            "current_season": current_season,
            "cups_found": cup_count,
            "events_found": event_count,
            "sample_race_results": sample_results,
            "czech_athletes_in_sample": czech_found,
            "czech_athletes": czech_athletes,
            "known_czech_ids": CZECH_WOMEN_IDS
        }
        
    except Exception as e:
        logger.error(f"API test failed: {e}")
        return {
            "status": "error",
            "api_working": False,
            "error": str(e)
        }

@router.get("/test-athlete/{athlete_name}")
async def test_athlete_data(athlete_name: str):
    """Test getting specific athlete data by name"""
    try:
        # Get IBU ID from name
        athlete_name_upper = athlete_name.upper()
        ibu_id = CZECH_WOMEN_IDS.get(athlete_name_upper)
        
        if not ibu_id:
            # Try with actual ID if passed
            ibu_id = athlete_name
        
        # Get all athlete results
        all_results = br.all_results(ibu_id)
        
        if not all_results or not all_results.get("Results"):
            raise HTTPException(status_code=404, detail=f"No results found for athlete {athlete_name} (ID: {ibu_id})")
        
        # Get recent results
        recent = all_results["Results"][:10] if all_results.get("Results") else []
        
        return {
            "athlete_id": ibu_id,
            "name": recent[0].get("Name") if recent else "Unknown",
            "nation": recent[0].get("Nat") if recent else "Unknown",
            "total_results": len(all_results.get("Results", [])),
            "recent_results": recent
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Athlete test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
