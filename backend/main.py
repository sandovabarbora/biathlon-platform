"""
Biathlon Pro - Backend API
Optimized for coaches and sports professionals
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import json
import logging
from functools import lru_cache
import hashlib

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global data cache
data_cache = {}
analysis_cache = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Starting Biathlon Pro API...")
    load_all_data()
    logger.info(f"✅ Loaded {len(data_cache)} datasets")
    yield
    logger.info("👋 Shutting down...")

app = FastAPI(
    title="Biathlon Pro API",
    description="Professional Analytics Platform for Biathlon Coaches",
    version="2.0.0",
    lifespan=lifespan
)

# CORS - allow all for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data paths
DATA_DIR = Path("../data")

# ==================== MODELS ====================

class AthleteBase(BaseModel):
    """Basic athlete information"""
    id: str
    name: str
    nation: str
    birth_year: Optional[int] = None

class AthleteStats(AthleteBase):
    """Extended athlete statistics"""
    avg_rank: float = Field(description="Average rank across all races")
    median_rank: float = Field(description="Median rank (more stable than average)")
    best_rank: int
    worst_rank: int
    total_races: int
    races_finished: int
    dnf_rate: float = Field(description="Did Not Finish rate %")
    
    # Performance metrics
    top3_rate: float = Field(description="Podium finish rate %")
    top10_rate: float = Field(description="Top 10 finish rate %")
    points_per_race: float = Field(description="Average World Cup points per race")
    
    # Shooting metrics
    shooting_accuracy: float = Field(description="Overall shooting accuracy %")
    prone_accuracy: float = Field(description="Prone shooting accuracy %")
    standing_accuracy: float = Field(description="Standing shooting accuracy %")
    avg_shooting_time: Optional[float] = Field(description="Average time per shooting")
    
    # Skiing metrics
    avg_ski_rank: Optional[float] = Field(description="Average ski time rank")
    ski_speed_index: Optional[float] = Field(description="Relative ski speed (100 = average)")
    
    # Consistency metrics
    consistency_score: float = Field(description="Lower = more consistent (std dev of ranks)")
    improvement_trend: float = Field(description="Recent form vs season average")
    
    # Tactical metrics
    start_position_impact: Optional[float] = Field(description="How start position affects result")
    pressure_handling: Optional[float] = Field(description="Performance in high-pressure situations")

class RaceAnalysis(BaseModel):
    """Detailed race analysis"""
    race_id: str
    date: str
    location: str
    race_type: str
    weather_conditions: Optional[str]
    
    # Results
    winner: str
    winner_time: str
    winner_nation: str
    
    # Statistics
    total_starters: int
    total_finishers: int
    dnf_count: int
    avg_shooting_misses: float
    
    # Our athlete performance
    athlete_rank: Optional[int]
    athlete_time_behind: Optional[str]
    athlete_shooting: Optional[str]
    
    # Relative performance
    percentile: Optional[float] = Field(description="Athlete's percentile in this race")
    vs_personal_average: Optional[float] = Field(description="Performance vs personal average")

class TrainingRecommendation(BaseModel):
    """AI-generated training recommendations"""
    priority: str = Field(description="HIGH, MEDIUM, LOW")
    area: str = Field(description="SHOOTING, SKIING, PHYSICAL, MENTAL, TACTICAL")
    specific_focus: str
    recommendation: str
    expected_impact: str
    time_frame: str = Field(description="Days/weeks to see improvement")
    exercises: List[str]
    metrics_to_track: List[str]

class PerformanceTrend(BaseModel):
    """Performance trend analysis"""
    period: str
    direction: str = Field(description="IMPROVING, STABLE, DECLINING")
    change_percentage: float
    key_factors: List[str]
    races_analyzed: int
    confidence_level: float = Field(description="Statistical confidence 0-100%")

# ==================== DATA LOADING ====================

def load_all_data():
    """Load all CSV files into memory with proper parsing"""
    global data_cache
    
    files_to_load = {
        'results': 'results.csv',
        'course_time': 'analytics_course_time.csv',
        'range_time': 'analytics_range_time.csv',
        'shooting_time': 'analytics_shooting_time.csv',
        'cups': 'world_cup_standings.csv'
    }
    
    for key, filename in files_to_load.items():
        filepath = DATA_DIR / filename
        if filepath.exists():
            try:
                df = pd.read_csv(filepath, low_memory=False)
                
                # Clean column names
                df.columns = df.columns.str.strip().str.replace(' ', '')
                
                # Parse numeric columns
                numeric_columns = ['Rank', 'ShootingTotal', 'ResultOrder', 'StartOrder']
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Parse date columns if present
                if 'StartTime' in df.columns:
                    df['StartTime'] = pd.to_datetime(df['StartTime'], errors='coerce')
                
                data_cache[key] = df
                logger.info(f"✅ Loaded {filename}: {len(df)} rows, {len(df.columns)} columns")
                
            except Exception as e:
                logger.error(f"❌ Error loading {filename}: {e}")
        else:
            logger.warning(f"⚠️ File not found: {filename}")

# ==================== ANALYSIS FUNCTIONS ====================

@lru_cache(maxsize=128)
def calculate_athlete_stats(athlete_name: str) -> Optional[AthleteStats]:
    """Calculate comprehensive statistics for an athlete"""
    
    if 'results' not in data_cache:
        return None
    
    df = data_cache['results']
    athlete_df = df[df['Name'] == athlete_name].copy()
    
    if athlete_df.empty:
        return None
    
    # Basic stats
    total_races = len(athlete_df)
    races_finished = len(athlete_df[athlete_df['Rank'].notna()])
    dnf_rate = ((total_races - races_finished) / total_races * 100) if total_races > 0 else 0
    
    # Only use finished races for statistics
    finished_df = athlete_df[athlete_df['Rank'].notna()]
    
    if finished_df.empty:
        return None
    
    # Rank statistics
    avg_rank = finished_df['Rank'].mean()
    median_rank = finished_df['Rank'].median()
    best_rank = finished_df['Rank'].min()
    worst_rank = finished_df['Rank'].max()
    
    # Performance rates
    top3_rate = (finished_df['Rank'] <= 3).sum() / races_finished * 100
    top10_rate = (finished_df['Rank'] <= 10).sum() / races_finished * 100
    
    # Points calculation (top 40 get points)
    points_map = {i: 61-i for i in range(1, 41)}  # 1st=60pts, 40th=1pt
    finished_df['Points'] = finished_df['Rank'].map(points_map).fillna(0)
    points_per_race = finished_df['Points'].mean()
    
    # Shooting analysis
    shooting_accuracy = 100  # Default
    prone_accuracy = 100
    standing_accuracy = 100
    
    if 'Shootings' in finished_df.columns:
        # Parse shooting strings (format: "0+1 0+2" = prone+standing)
        prone_misses = []
        standing_misses = []
        
        for shooting_str in finished_df['Shootings'].dropna():
            parts = str(shooting_str).split()
            for part in parts:
                if '+' in part:
                    p, s = part.split('+')
                    if p.isdigit():
                        prone_misses.append(int(p))
                    if s.isdigit():
                        standing_misses.append(int(s))
        
        if prone_misses:
            prone_accuracy = (1 - np.mean(prone_misses) / 5) * 100
        if standing_misses:
            standing_accuracy = (1 - np.mean(standing_misses) / 5) * 100
        
        total_misses = pd.to_numeric(finished_df['ShootingTotal'], errors='coerce').fillna(0)
        avg_misses = total_misses.mean()
        shooting_accuracy = (1 - avg_misses / 20) * 100 if avg_misses > 0 else 100
    
    # Consistency
    consistency_score = finished_df['Rank'].std()
    
    # Trend analysis (last 5 vs overall)
    improvement_trend = 0
    if len(finished_df) >= 5:
        recent_avg = finished_df.tail(5)['Rank'].mean()
        overall_avg = finished_df['Rank'].mean()
        improvement_trend = overall_avg - recent_avg  # Positive = improving
    
    # Ski performance
    ski_rank = None
    ski_speed_index = None
    if 'course_time' in data_cache:
        course_df = data_cache['course_time']
        athlete_course = course_df[course_df['Name'] == athlete_name]
        if not athlete_course.empty and 'Rank' in athlete_course.columns:
            ski_rank = athlete_course['Rank'].mean()
            # Calculate relative speed (100 = average)
            avg_course_rank = course_df.groupby('RaceId')['Rank'].mean()
            ski_speed_index = (avg_course_rank.mean() / ski_rank * 100) if ski_rank > 0 else 100
    
    return AthleteStats(
        id=athlete_df['IBUId'].iloc[0] if 'IBUId' in athlete_df.columns else str(hash(athlete_name)),
        name=athlete_name,
        nation=athlete_df['Nat'].iloc[0] if 'Nat' in athlete_df.columns else 'Unknown',
        avg_rank=round(avg_rank, 1),
        median_rank=round(median_rank, 1),
        best_rank=int(best_rank),
        worst_rank=int(worst_rank),
        total_races=total_races,
        races_finished=races_finished,
        dnf_rate=round(dnf_rate, 1),
        top3_rate=round(top3_rate, 1),
        top10_rate=round(top10_rate, 1),
        points_per_race=round(points_per_race, 1),
        shooting_accuracy=round(shooting_accuracy, 1),
        prone_accuracy=round(prone_accuracy, 1),
        standing_accuracy=round(standing_accuracy, 1),
        avg_ski_rank=round(ski_rank, 1) if ski_rank else None,
        ski_speed_index=round(ski_speed_index, 1) if ski_speed_index else None,
        consistency_score=round(consistency_score, 1),
        improvement_trend=round(improvement_trend, 1)
    )

def generate_training_recommendations(stats: AthleteStats) -> List[TrainingRecommendation]:
    """Generate specific training recommendations based on athlete statistics"""
    
    recommendations = []
    
    # Shooting analysis
    if stats.shooting_accuracy < 80:
        priority = "HIGH" if stats.shooting_accuracy < 75 else "MEDIUM"
        recommendations.append(TrainingRecommendation(
            priority=priority,
            area="SHOOTING",
            specific_focus="Overall accuracy improvement",
            recommendation=f"Shooting accuracy at {stats.shooting_accuracy}% needs improvement. Focus on breathing techniques and trigger control.",
            expected_impact=f"Could improve average ranking by {int((80 - stats.shooting_accuracy) * 0.5)} positions",
            time_frame="2-3 weeks",
            exercises=[
                "Dry firing practice 30 min daily",
                "Breathing exercises between shots",
                "Heart rate control training",
                "Visualization before shooting"
            ],
            metrics_to_track=["Shots on target", "Time per shot", "Heart rate at trigger"]
        ))
    
    # Standing vs Prone analysis
    if stats.standing_accuracy < stats.prone_accuracy - 10:
        recommendations.append(TrainingRecommendation(
            priority="HIGH",
            area="SHOOTING",
            specific_focus="Standing shooting stability",
            recommendation=f"Standing accuracy ({stats.standing_accuracy}%) significantly lower than prone ({stats.prone_accuracy}%). Focus on core stability.",
            expected_impact="2-3 position improvement per race",
            time_frame="3-4 weeks",
            exercises=[
                "Core strengthening exercises",
                "Balance board training with rifle",
                "Standing position hold practice",
                "Wind reading exercises"
            ],
            metrics_to_track=["Standing hit rate", "Sway amplitude", "Shot grouping"]
        ))
    
    # Ski performance
    if stats.ski_speed_index and stats.ski_speed_index < 95:
        recommendations.append(TrainingRecommendation(
            priority="MEDIUM",
            area="SKIING",
            specific_focus="Ski speed improvement",
            recommendation=f"Ski speed index at {stats.ski_speed_index} (100 = average). Focus on technique and endurance.",
            expected_impact="1-2 minutes time gain per race",
            time_frame="4-6 weeks",
            exercises=[
                "Interval training 3x/week",
                "Technique video analysis",
                "Strength training for legs",
                "Uphill specific training"
            ],
            metrics_to_track=["Lap times", "Heart rate zones", "Power output"]
        ))
    
    # Consistency
    if stats.consistency_score > 10:
        recommendations.append(TrainingRecommendation(
            priority="MEDIUM",
            area="MENTAL",
            specific_focus="Performance consistency",
            recommendation=f"High variability in results (std dev: {stats.consistency_score}). Work on mental preparation.",
            expected_impact="More predictable performance",
            time_frame="4-8 weeks",
            exercises=[
                "Pre-race routine development",
                "Pressure situation training",
                "Mental imagery practice",
                "Competition simulation training"
            ],
            metrics_to_track=["Rank variance", "Emotional state scores", "Recovery time"]
        ))
    
    # High pressure performance
    if stats.top10_rate < 20 and stats.avg_rank < 30:
        recommendations.append(TrainingRecommendation(
            priority="LOW",
            area="TACTICAL",
            specific_focus="Race tactics and positioning",
            recommendation="Good average performance but low top 10 rate. Focus on race tactics and key moments.",
            expected_impact="Increase podium chances",
            time_frame="Immediate",
            exercises=[
                "Race video analysis",
                "Pacing strategy development",
                "Competition planning",
                "Risk/reward decision training"
            ],
            metrics_to_track=["Position changes during race", "Split times", "Tactical decisions"]
        ))
    
    return recommendations

# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    """API status and documentation"""
    return {
        "name": "Biathlon Pro API",
        "version": "2.0.0",
        "status": "running",
        "data_loaded": list(data_cache.keys()),
        "total_records": sum(len(df) for df in data_cache.values()),
        "endpoints": {
            "athletes": "/api/athletes - List all athletes",
            "athlete_detail": "/api/athlete/{name} - Detailed athlete statistics",
            "training": "/api/athlete/{name}/training - Training recommendations",
            "trends": "/api/athlete/{name}/trends - Performance trends",
            "comparison": "/api/compare?athletes=name1,name2 - Compare athletes",
            "export": "/api/export/{name} - Export athlete data",
            "documentation": "/docs - Interactive API documentation"
        }
    }

@app.get("/api/athletes")
async def get_athletes(
    nation: Optional[str] = Query(None, description="Filter by nation code (e.g., CZE)"),
    min_races: int = Query(5, description="Minimum number of races"),
    sort_by: str = Query("avg_rank", description="Sort field: avg_rank, name, nation, total_races")
):
    """Get list of athletes with comprehensive statistics"""
    
    if 'results' not in data_cache:
        raise HTTPException(404, "No results data available")
    
    df = data_cache['results']
    
    # Filter by nation if specified
    if nation:
        df = df[df['Nat'] == nation.upper()]
    
    # Group by athlete
    athlete_groups = df.groupby('Name')
    
    athletes = []
    for name, group in athlete_groups:
        if len(group) >= min_races:
            stats = calculate_athlete_stats(name)
            if stats:
                athletes.append(stats.dict())
    
    # Sort results
    if sort_by == "avg_rank":
        athletes.sort(key=lambda x: x['avg_rank'])
    elif sort_by == "name":
        athletes.sort(key=lambda x: x['name'])
    elif sort_by == "total_races":
        athletes.sort(key=lambda x: x['total_races'], reverse=True)
    
    return {
        "total": len(athletes),
        "athletes": athletes[:100]  # Limit to top 100
    }

@app.get("/api/athlete/{name}", response_model=AthleteStats)
async def get_athlete_detail(name: str):
    """Get detailed statistics for a specific athlete"""
    
    stats = calculate_athlete_stats(name)
    if not stats:
        raise HTTPException(404, f"Athlete '{name}' not found")
    
    return stats

@app.get("/api/athlete/{name}/training", response_model=List[TrainingRecommendation])
async def get_training_recommendations(name: str):
    """Get AI-generated training recommendations"""
    
    stats = calculate_athlete_stats(name)
    if not stats:
        raise HTTPException(404, f"Athlete '{name}' not found")
    
    recommendations = generate_training_recommendations(stats)
    
    # Sort by priority
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    recommendations.sort(key=lambda x: priority_order[x.priority])
    
    return recommendations

@app.get("/api/athlete/{name}/trends")
async def get_performance_trends(
    name: str,
    period: str = Query("season", description="Period: last5, last10, month, season")
):
    """Analyze performance trends over time"""
    
    if 'results' not in data_cache:
        raise HTTPException(404, "No results data available")
    
    df = data_cache['results']
    athlete_df = df[df['Name'] == name].copy()
    
    if athlete_df.empty:
        raise HTTPException(404, f"Athlete '{name}' not found")
    
    # Filter by period
    if period == "last5":
        athlete_df = athlete_df.tail(5)
    elif period == "last10":
        athlete_df = athlete_df.tail(10)
    elif period == "month":
        # Assuming we have date information
        pass
    
    finished_df = athlete_df[athlete_df['Rank'].notna()]
    
    if len(finished_df) < 2:
        return {
            "period": period,
            "direction": "INSUFFICIENT_DATA",
            "races_analyzed": len(finished_df)
        }
    
    # Calculate trend
    ranks = finished_df['Rank'].values
    x = np.arange(len(ranks))
    
    # Linear regression for trend
    from scipy import stats as scipy_stats
    slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(x, ranks)
    
    # Determine direction
    if slope < -0.5:
        direction = "IMPROVING"
    elif slope > 0.5:
        direction = "DECLINING"
    else:
        direction = "STABLE"
    
    # Key factors
    factors = []
    
    # Shooting trend
    if 'ShootingTotal' in finished_df.columns:
        shooting_trend = finished_df['ShootingTotal'].tail(3).mean() - finished_df['ShootingTotal'].head(3).mean()
        if abs(shooting_trend) > 0.5:
            factors.append(f"Shooting {'deteriorating' if shooting_trend > 0 else 'improving'}")
    
    # Consistency trend
    recent_std = finished_df.tail(min(5, len(finished_df)))['Rank'].std()
    overall_std = finished_df['Rank'].std()
    if recent_std < overall_std * 0.8:
        factors.append("Increased consistency")
    elif recent_std > overall_std * 1.2:
        factors.append("Decreased consistency")
    
    return PerformanceTrend(
        period=period,
        direction=direction,
        change_percentage=round(slope * len(ranks), 1),
        key_factors=factors if factors else ["No significant factors identified"],
        races_analyzed=len(finished_df),
        confidence_level=round(abs(r_value) * 100, 1)
    )

@app.get("/api/compare")
async def compare_athletes(
    athletes: str = Query(..., description="Comma-separated athlete names")
):
    """Compare multiple athletes side by side"""
    
    athlete_names = [name.strip() for name in athletes.split(',')]
    
    if len(athlete_names) < 2:
        raise HTTPException(400, "Please provide at least 2 athletes to compare")
    
    comparisons = []
    for name in athlete_names:
        stats = calculate_athlete_stats(name)
        if stats:
            comparisons.append(stats.dict())
    
    if len(comparisons) < 2:
        raise HTTPException(404, "Not enough valid athletes found for comparison")
    
    # Calculate relative metrics
    metrics = ['avg_rank', 'shooting_accuracy', 'consistency_score', 'top10_rate']
    
    for metric in metrics:
        values = [c[metric] for c in comparisons if c.get(metric) is not None]
        if values:
            best = min(values) if metric in ['avg_rank', 'consistency_score'] else max(values)
            worst = max(values) if metric in ['avg_rank', 'consistency_score'] else min(values)
            
            for comp in comparisons:
                if comp.get(metric) is not None:
                    comp[f'{metric}_relative'] = 'BEST' if comp[metric] == best else 'WORST' if comp[metric] == worst else 'MIDDLE'
    
    return {
        "athletes": comparisons,
        "comparison_metrics": metrics
    }

@app.get("/api/export/{name}")
async def export_athlete_data(
    name: str,
    format: str = Query("json", description="Export format: json, csv")
):
    """Export athlete data for external analysis"""
    
    if 'results' not in data_cache:
        raise HTTPException(404, "No results data available")
    
    df = data_cache['results']
    athlete_df = df[df['Name'] == name]
    
    if athlete_df.empty:
        raise HTTPException(404, f"Athlete '{name}' not found")
    
    if format == "csv":
        # Save to temp file and return
        temp_file = f"/tmp/{name.replace(' ', '_')}_export.csv"
        athlete_df.to_csv(temp_file, index=False)
        return FileResponse(temp_file, media_type="text/csv", filename=f"{name}_data.csv")
    else:
        # Return as JSON
        return athlete_df.to_dict('records')

@app.get("/api/search")
async def search_athletes(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, description="Maximum results")
):
    """Search for athletes by name or nation"""
    
    if 'results' not in data_cache:
        raise HTTPException(404, "No results data available")
    
    df = data_cache['results']
    query_lower = q.lower()
    
    # Search in names and nations
    mask = (df['Name'].str.lower().str.contains(query_lower, na=False) | 
            df['Nat'].str.lower().str.contains(query_lower, na=False))
    
    matches = df[mask]['Name'].unique()[:limit]
    
    results = []
    for name in matches:
        athlete_nat = df[df['Name'] == name]['Nat'].iloc[0] if 'Nat' in df.columns else 'Unknown'
        results.append({
            "name": name,
            "nation": athlete_nat
        })
    
    return {
        "query": q,
        "results": results,
        "total": len(results)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
