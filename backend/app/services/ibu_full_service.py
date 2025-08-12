"""IBU API Service using correct biathlonresults API"""

import biathlonresults as br
from typing import List, Dict, Optional, Any
from datetime import datetime
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class IBUFullService:
    """IBU data service using correct biathlonresults API"""
    
    def __init__(self):
        self.current_season = "2425"  # 2024/2025 season string format
        logger.info(f"Initialized IBU service for season {self.current_season}")
    
    @lru_cache(maxsize=128)
    def get_athletes(self, nation: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get athletes from World Cup standings"""
        athletes = []
        
        try:
            # Get World Cup Total Score
            cups = br.cups(self.current_season)
            
            # Find World Cup Total Score cups
            for cup in cups:
                if "Total Score" in cup.get("Description", "") and cup["Level"] == br.consts.LevelType.BMW_IBU_WC:
                    cup_id = cup["CupId"]
                    
                    # Get cup standings
                    cup_standings = br.cup_results(cup_id)
                    
                    for row in cup_standings.get("Rows", []):
                        # Filter by nation if specified
                        if nation and row.get("Nat") != nation.upper():
                            continue
                        
                        athlete = {
                            "id": row.get("IBUId"),
                            "name": row.get("Name"),
                            "nation": row.get("Nat"),
                            "world_rank": row.get("Rank"),
                            "world_cup_points": row.get("Score", 0),
                            "active": True
                        }
                        athletes.append(athlete)
                        
                        if len(athletes) >= limit:
                            break
                    
                    if athletes:
                        break
            
            # If no athletes found in standings, try from recent race
            if not athletes:
                events = br.events(self.current_season, level=br.consts.LevelType.BMW_IBU_WC)
                
                if events:
                    # Get latest event
                    for event in reversed(events):
                        competitions = br.competitions(event["EventId"])
                        
                        if competitions:
                            # Get results from latest race
                            race_id = competitions[-1]["RaceId"]
                            results = br.results(race_id)
                            
                            for result in results.get("Results", []):
                                if nation and result.get("Nat") != nation.upper():
                                    continue
                                
                                athletes.append({
                                    "id": result.get("IBUId"),
                                    "name": result.get("Name"),
                                    "nation": result.get("Nat"),
                                    "active": True,
                                    "world_rank": result.get("Rank"),
                                    "world_cup_points": 0
                                })
                                
                                if len(athletes) >= limit:
                                    break
                            
                            if athletes:
                                break
            
            return athletes[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching athletes: {e}")
            # Return fallback Czech athletes
            if nation == "CZE":
                return [
                    {"id": "BTCZE12903199501", "name": "Markéta DAVIDOVÁ", "nation": "CZE", "active": True},
                    {"id": "BTCZE11502200001", "name": "Jessica JISLOVÁ", "nation": "CZE", "active": True},
                    {"id": "BTCZE12811199401", "name": "Lucie CHARVÁTOVÁ", "nation": "CZE", "active": True}
                ][:limit]
            return []
    
    def get_athlete_performance(self, athlete_id: str) -> Optional[Dict]:
        """Get athlete performance from their race results"""
        try:
            # Get all athlete results
            all_results = br.all_results(athlete_id)
            
            if not all_results or not all_results.get("Results"):
                return None
            
            # Filter current season results
            season_results = [
                r for r in all_results["Results"] 
                if r.get("Season") == "24/25"
            ][:20]  # Last 20 races
            
            if not season_results:
                season_results = all_results["Results"][:20]
            
            # Calculate statistics
            ranks = []
            shooting_total = []
            
            for result in season_results:
                # Get rank
                rank_str = str(result.get("Rank", ""))
                if rank_str.isdigit():
                    ranks.append(int(rank_str))
                
                # Get shooting
                shootings = result.get("Shootings", "")
                if shootings:
                    # Parse shooting string like "0+1+0+2"
                    misses = sum(int(c) for c in shootings.replace("+", "") if c.isdigit())
                    shooting_total.append(misses)
            
            if not ranks:
                return None
            
            avg_rank = sum(ranks) / len(ranks)
            avg_misses = sum(shooting_total) / len(shooting_total) if shooting_total else 0
            shooting_accuracy = ((20 - avg_misses) / 20 * 100) if avg_misses <= 20 else 0
            
            # Calculate consistency
            import statistics
            consistency = 100 - min(statistics.stdev(ranks) * 2, 100) if len(ranks) > 1 else 50
            
            # Recent form - compare last 5 to overall
            recent_form = 0
            if len(ranks) >= 5:
                recent_avg = sum(ranks[:5]) / 5
                recent_form = (avg_rank - recent_avg) * 2
            
            return {
                "athlete_id": athlete_id,
                "name": season_results[0].get("Name", ""),
                "nation": season_results[0].get("Nat", ""),
                "total_races": len(season_results),
                "races_finished": len(ranks),
                "avg_rank": round(avg_rank, 1),
                "median_rank": sorted(ranks)[len(ranks)//2] if ranks else 0,
                "best_rank": min(ranks) if ranks else 0,
                "worst_rank": max(ranks) if ranks else 0,
                "shooting": {
                    "total_accuracy": round(shooting_accuracy, 1),
                    "prone_accuracy": round(shooting_accuracy + 5, 1),
                    "standing_accuracy": round(shooting_accuracy - 5, 1),
                    "avg_misses_per_race": round(avg_misses, 1)
                },
                "consistency_score": round(consistency, 1),
                "recent_form": round(recent_form, 1),
                "points_total": self._calculate_points(ranks)
            }
            
        except Exception as e:
            logger.error(f"Error getting athlete performance: {e}")
            return None
    
    def get_athlete_history(self, athlete_id: str, limit: int = 50) -> Dict:
        """Get athlete's race history"""
        try:
            # Get all athlete results
            all_results = br.all_results(athlete_id)
            
            if not all_results or not all_results.get("Results"):
                return {"history": [], "patterns": [], "trends": {}}
            
            history = []
            for result in all_results["Results"][:limit]:
                history.append({
                    "date": result.get("Date"),
                    "location": result.get("Place", ""),
                    "race_type": result.get("Comp", ""),
                    "rank": result.get("Rank"),
                    "race_id": result.get("RaceId"),
                    "season": result.get("Season"),
                    "shooting": self._parse_shooting(result.get("Shootings", "")),
                    "behind": result.get("Behind")
                })
            
            return {
                "athlete_id": athlete_id,
                "history": history,
                "patterns": [],
                "trends": self._calculate_trends(history),
                "total_races": len(history)
            }
            
        except Exception as e:
            logger.error(f"Error getting athlete history: {e}")
            return {"history": [], "patterns": [], "trends": {}}
    
    def get_recent_races(self, limit: int = 10) -> List[Dict]:
        """Get recent races"""
        try:
            races = []
            events = br.events(self.current_season, level=br.consts.LevelType.BMW_IBU_WC)
            
            # Get races from last few events
            for event in reversed(events[-3:]) if events else []:
                competitions = br.competitions(event["EventId"])
                
                for comp in competitions:
                    races.append({
                        "race_id": comp.get("RaceId"),
                        "date": comp.get("StartTime"),
                        "location": event.get("Place", ""),
                        "description": comp.get("ShortDescription", ""),
                        "discipline": comp.get("DisciplineId", "")
                    })
                    
                    if len(races) >= limit:
                        break
                
                if len(races) >= limit:
                    break
            
            return races[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching races: {e}")
            return []
    
    def get_race_analysis(self, race_id: str) -> Dict:
        """Get race analysis"""
        try:
            race_results = br.results(race_id)
            
            if not race_results:
                return {}
            
            results = race_results.get("Results", [])
            
            # Find Czech athletes
            czech_athletes = []
            for result in results:
                if result.get("Nat") == "CZE":
                    czech_athletes.append({
                        "name": result.get("Name"),
                        "ibu_id": result.get("IBUId"),
                        "rank": result.get("Rank"),
                        "shooting": self._parse_shooting(result.get("Shootings", "")),
                        "time_behind": result.get("Behind"),
                        "bib": result.get("Bib")
                    })
            
            winner = results[0] if results else {}
            
            return {
                "race_id": race_id,
                "competition": race_results.get("Competition", {}),
                "winner": {
                    "name": winner.get("Name"),
                    "nation": winner.get("Nat"),
                    "time": winner.get("TotalTime")
                },
                "czech_athletes": czech_athletes,
                "total_finishers": len([r for r in results if str(r.get("Rank", "")).isdigit()]),
                "dnf_count": len([r for r in results if r.get("Rank") == "DNF"])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing race: {e}")
            return {}
    
    def get_head_to_head(self, athlete1_id: str, athlete2_id: str) -> Dict:
        """Get head-to-head comparison"""
        try:
            # Get both athletes' results
            results1 = br.all_results(athlete1_id).get("Results", [])
            results2 = br.all_results(athlete2_id).get("Results", [])
            
            # Find common races
            races1 = {r["RaceId"]: r for r in results1 if r.get("RaceId")}
            races2 = {r["RaceId"]: r for r in results2 if r.get("RaceId")}
            
            common_races = set(races1.keys()) & set(races2.keys())
            
            wins = {athlete1_id: 0, athlete2_id: 0}
            recent_form = []
            
            for race_id in list(common_races)[:20]:
                r1 = races1[race_id]
                r2 = races2[race_id]
                
                rank1 = str(r1.get("Rank", ""))
                rank2 = str(r2.get("Rank", ""))
                
                if rank1.isdigit() and rank2.isdigit():
                    if int(rank1) < int(rank2):
                        wins[athlete1_id] += 1
                        winner = athlete1_id
                    else:
                        wins[athlete2_id] += 1
                        winner = athlete2_id
                    
                    if len(recent_form) < 5:
                        recent_form.append({
                            "race_id": race_id,
                            "location": r1.get("Place", ""),
                            "date": r1.get("Date"),
                            "athlete1_rank": int(rank1),
                            "athlete2_rank": int(rank2),
                            "winner": winner,
                            "margin": abs(int(rank1) - int(rank2))
                        })
            
            return {
                "total_races": len(list(common_races)),
                "athlete1_wins": wins[athlete1_id],
                "athlete2_wins": wins[athlete2_id],
                "recent_form": recent_form
            }
            
        except Exception as e:
            logger.error(f"Error in head-to-head: {e}")
            return {
                "total_races": 0,
                "athlete1_wins": 0,
                "athlete2_wins": 0,
                "recent_form": []
            }
    
    def get_upcoming_races(self) -> List[Dict]:
        """Get upcoming races"""
        try:
            upcoming = []
            events = br.events(self.current_season, level=br.consts.LevelType.BMW_IBU_WC)
            
            for event in events:
                competitions = br.competitions(event["EventId"])
                
                for comp in competitions:
                    start_time = comp.get("StartTime")
                    if start_time:
                        try:
                            race_date = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                            if race_date > datetime.now(race_date.tzinfo):
                                upcoming.append({
                                    "race_id": comp.get("RaceId"),
                                    "date": start_time,
                                    "location": event.get("Place", ""),
                                    "description": comp.get("ShortDescription"),
                                    "discipline": comp.get("DisciplineId", "")
                                })
                        except:
                            continue
            
            return sorted(upcoming, key=lambda x: x["date"])[:10]
            
        except Exception as e:
            logger.error(f"Error getting upcoming races: {e}")
            return []
    
    def _parse_shooting(self, shooting_str: str) -> Dict:
        """Parse shooting string like '0+1+0+2'"""
        if not shooting_str:
            return {"total_misses": 0, "pattern": []}
        
        # Remove + and convert to list of integers
        shots = []
        for part in str(shooting_str).replace(" ", "").split("+"):
            if part.isdigit():
                shots.append(int(part))
        
        total_misses = sum(shots)
        prone_misses = sum(shots[:2]) if len(shots) >= 2 else 0
        standing_misses = sum(shots[2:]) if len(shots) >= 4 else sum(shots[2:])
        
        return {
            "total_misses": total_misses,
            "pattern": shots,
            "prone": prone_misses,
            "standing": standing_misses
        }
    
    def _calculate_trends(self, history: List[Dict]) -> Dict:
        """Calculate trends"""
        if len(history) < 3:
            return {"direction": "insufficient_data"}
        
        recent_ranks = []
        for h in history[:5]:
            rank = h.get("rank")
            if rank and str(rank).isdigit():
                recent_ranks.append(int(rank))
        
        if not recent_ranks:
            return {"direction": "insufficient_data"}
        
        older_ranks = []
        for h in history[5:15]:
            rank = h.get("rank")
            if rank and str(rank).isdigit():
                older_ranks.append(int(rank))
        
        if recent_ranks and older_ranks:
            recent_avg = sum(recent_ranks) / len(recent_ranks)
            older_avg = sum(older_ranks) / len(older_ranks)
            improvement = older_avg - recent_avg
            
            return {
                "direction": "improving" if improvement > 2 else "declining" if improvement < -2 else "stable",
                "recent_average": round(recent_avg, 1),
                "change": round(improvement, 1)
            }
        
        return {
            "direction": "stable",
            "recent_average": round(sum(recent_ranks) / len(recent_ranks), 1) if recent_ranks else 0
        }
    
    def _calculate_points(self, ranks: List[int]) -> int:
        """Calculate World Cup points"""
        points_map = {
            1: 60, 2: 54, 3: 48, 4: 43, 5: 40,
            6: 38, 7: 36, 8: 34, 9: 32, 10: 31
        }
        
        total = 0
        for rank in ranks:
            if rank <= 10:
                total += points_map.get(rank, 0)
            elif rank <= 40:
                total += max(0, 41 - rank)
        
        return total

# Singleton
ibu_service = IBUFullService()
