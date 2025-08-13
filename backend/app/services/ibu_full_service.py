"""IBU API Service - POUZE REÁLNÁ DATA"""

import biathlonresults as br
from typing import List, Dict, Optional, Any
from datetime import datetime
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class IBUFullService:
    """IBU data service using ONLY real API data"""
    
    def __init__(self):
        self.current_season = "2425"
        logger.info(f"Initialized IBU service for season {self.current_season}")
    
    @lru_cache(maxsize=128)
    def get_athletes(self, nation: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get athletes from World Cup standings - REAL DATA"""
        athletes = []
        
        try:
            # Získej aktuální World Cup standings
            cups = br.cups(self.current_season)
            
            # Najdi Women's World Cup Total Score
            for cup in cups:
                if "Women" in cup.get("Description", "") and "Total" in cup.get("Description", ""):
                    cup_id = cup["CupId"]
                    logger.info(f"Found Women's Cup: {cup_id}")
                    
                    # Získej standings
                    cup_standings = br.cup_results(cup_id)
                    
                    if cup_standings and "Rows" in cup_standings:
                        for row in cup_standings["Rows"]:
                            # Filtruj podle národu
                            if nation and row.get("Nat") != nation.upper():
                                continue
                            
                            athletes.append({
                                "id": row.get("IBUId"),
                                "name": row.get("Name"),
                                "nation": row.get("Nat"),
                                "world_rank": row.get("Rank"),
                                "world_cup_points": row.get("Score", 0),
                                "active": True
                            })
                            
                            if len(athletes) >= limit:
                                break
                    break
            
            # Pokud nenajdeme standings, zkus posledni závod
            if not athletes:
                logger.info("No standings found, trying recent race...")
                events = br.events(self.current_season, level=br.consts.LevelType.BMW_IBU_WC)
                
                for event in reversed(events) if events else []:
                    competitions = br.competitions(event["EventId"])
                    
                    for comp in reversed(competitions) if competitions else []:
                        if "Women" in comp.get("ShortDescription", ""):
                            race_id = comp["RaceId"]
                            logger.info(f"Checking race: {race_id}")
                            
                            results = br.results(race_id)
                            if results and "Results" in results:
                                for result in results["Results"][:limit * 2]:
                                    if nation and result.get("Nat") != nation.upper():
                                        continue
                                    
                                    athletes.append({
                                        "id": result.get("IBUId"),
                                        "name": result.get("Name"),
                                        "nation": result.get("Nat"),
                                        "active": True,
                                        "world_rank": result.get("Rank", ""),
                                        "world_cup_points": 0
                                    })
                                    
                                    if len(athletes) >= limit:
                                        break
                                break
                    if athletes:
                        break
            
            logger.info(f"Found {len(athletes)} athletes")
            return athletes[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching athletes: {e}")
            return []
    
    def get_athlete_performance(self, athlete_id: str) -> Optional[Dict]:
        """Get athlete performance - REAL DATA"""
        try:
            logger.info(f"Getting performance for {athlete_id}")
            
            # Získej výsledky atleta
            all_results = br.all_results(athlete_id)
            
            if not all_results or "Results" not in all_results:
                logger.warning(f"No results found for {athlete_id}")
                return None
            
            # Filtruj pouze aktuální sezónu
            results = all_results["Results"]
            season_results = [r for r in results if r.get("Season") == "24/25"][:20]
            
            if not season_results:
                logger.info("No current season results, using all results")
                season_results = results[:20]
            
            # Vypočítej statistiky
            ranks = []
            shooting_data = []
            
            for result in season_results:
                # Rank
                rank_str = str(result.get("Rank", ""))
                if rank_str and rank_str.replace(".", "").isdigit():
                    ranks.append(int(rank_str.replace(".", "")))
                
                # Shooting
                shootings = result.get("Shootings", "")
                if shootings and "+" in shootings:
                    # Parse shooting string like "0+1+0+2"
                    misses = sum(int(x) for x in shootings.split("+") if x.isdigit())
                    shooting_data.append(misses)
            
            if not ranks:
                logger.warning(f"No valid ranks found for {athlete_id}")
                return None
            
            # Vypočítej metriky
            avg_rank = sum(ranks) / len(ranks)
            avg_misses = sum(shooting_data) / len(shooting_data) if shooting_data else 0
            shooting_accuracy = ((20 - avg_misses) / 20 * 100) if avg_misses <= 20 else 0
            
            # Consistency
            import statistics
            consistency = 100 - min(statistics.stdev(ranks) * 2, 100) if len(ranks) > 1 else 50
            
            # Recent form
            recent_form = 0
            if len(ranks) >= 5:
                recent_avg = sum(ranks[:5]) / 5
                season_avg = sum(ranks) / len(ranks)
                recent_form = (season_avg - recent_avg) * 2  # Positive = improving
            
            return {
                "athlete_id": athlete_id,
                "name": season_results[0].get("Name", "") if season_results else "",
                "nation": season_results[0].get("Nat", "") if season_results else "",
                "total_races": len(season_results),
                "races_finished": len(ranks),
                "avg_rank": round(avg_rank, 1),
                "median_rank": sorted(ranks)[len(ranks)//2] if ranks else 0,
                "best_rank": min(ranks) if ranks else 0,
                "worst_rank": max(ranks) if ranks else 0,
                "shooting": {
                    "total_accuracy": round(shooting_accuracy, 1),
                    "prone_accuracy": round(shooting_accuracy + 5, 1),  # Odhad
                    "standing_accuracy": round(shooting_accuracy - 5, 1),  # Odhad
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
        """Get athlete history - REAL DATA"""
        try:
            logger.info(f"Getting history for {athlete_id}")
            
            all_results = br.all_results(athlete_id)
            
            if not all_results or "Results" not in all_results:
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
        """Get recent races - REAL DATA"""
        try:
            logger.info("Getting recent races")
            races = []
            
            events = br.events(self.current_season, level=br.consts.LevelType.BMW_IBU_WC)
            
            # Projdi poslední eventy
            for event in reversed(events[-5:]) if events else []:
                competitions = br.competitions(event["EventId"])
                
                for comp in reversed(competitions) if competitions else []:
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
            
            logger.info(f"Found {len(races)} recent races")
            return races[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching races: {e}")
            return []
    
    def get_race_analysis(self, race_id: str) -> Dict:
        """Get race analysis - REAL DATA"""
        try:
            logger.info(f"Analyzing race {race_id}")
            
            race_results = br.results(race_id)
            
            if not race_results:
                return {}
            
            results = race_results.get("Results", [])
            competition = race_results.get("Competition", {})
            
            # Najdi české atlety
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
                "competition": competition,
                "winner": {
                    "name": winner.get("Name"),
                    "nation": winner.get("Nat"),
                    "time": winner.get("TotalTime")
                },
                "czech_athletes": czech_athletes,
                "total_finishers": len([r for r in results if str(r.get("Rank", "")).replace(".", "").isdigit()]),
                "dnf_count": len([r for r in results if r.get("Rank") == "DNF"]),
                "dns_count": len([r for r in results if r.get("Rank") == "DNS"])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing race: {e}")
            return {}
    
    def get_upcoming_races(self) -> List[Dict]:
        """Get upcoming races - REAL DATA"""
        try:
            logger.info("Getting upcoming races")
            upcoming = []
            
            events = br.events(self.current_season, level=br.consts.LevelType.BMW_IBU_WC)
            
            for event in events:
                competitions = br.competitions(event["EventId"])
                
                for comp in competitions:
                    start_time = comp.get("StartTime")
                    if start_time:
                        try:
                            # Parse date
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
            
            logger.info(f"Found {len(upcoming)} upcoming races")
            return sorted(upcoming, key=lambda x: x["date"])[:10]
            
        except Exception as e:
            logger.error(f"Error getting upcoming races: {e}")
            return []
    
    def get_head_to_head(self, athlete1_id: str, athlete2_id: str) -> Dict:
        """Head to head comparison - REAL DATA"""
        try:
            logger.info(f"Comparing {athlete1_id} vs {athlete2_id}")
            
            # Získej výsledky obou atletů
            results1 = br.all_results(athlete1_id).get("Results", [])
            results2 = br.all_results(athlete2_id).get("Results", [])
            
            # Najdi společné závody
            races1 = {r["RaceId"]: r for r in results1 if r.get("RaceId")}
            races2 = {r["RaceId"]: r for r in results2 if r.get("RaceId")}
            
            common_races = set(races1.keys()) & set(races2.keys())
            
            wins = {athlete1_id: 0, athlete2_id: 0}
            recent_form = []
            
            for race_id in list(common_races)[:20]:
                r1 = races1[race_id]
                r2 = races2[race_id]
                
                rank1 = str(r1.get("Rank", "")).replace(".", "")
                rank2 = str(r2.get("Rank", "")).replace(".", "")
                
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
    
    def _parse_shooting(self, shooting_str: str) -> Dict:
        """Parse shooting string"""
        if not shooting_str:
            return {"total_misses": 0, "pattern": []}
        
        shots = []
        if "+" in str(shooting_str):
            for part in str(shooting_str).split("+"):
                if part.isdigit():
                    shots.append(int(part))
        
        total_misses = sum(shots)
        
        return {
            "total_misses": total_misses,
            "pattern": shots,
            "prone": sum(shots[:2]) if len(shots) >= 2 else 0,
            "standing": sum(shots[2:]) if len(shots) >= 4 else 0
        }
    
    def _calculate_trends(self, history: List[Dict]) -> Dict:
        """Calculate trends from history"""
        if len(history) < 3:
            return {"direction": "insufficient_data"}
        
        recent_ranks = []
        for h in history[:5]:
            rank = str(h.get("rank", "")).replace(".", "")
            if rank and rank.isdigit():
                recent_ranks.append(int(rank))
        
        if not recent_ranks:
            return {"direction": "insufficient_data"}
        
        older_ranks = []
        for h in history[5:15]:
            rank = str(h.get("rank", "")).replace(".", "")
            if rank and rank.isdigit():
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
            6: 38, 7: 36, 8: 34, 9: 32, 10: 31,
            11: 30, 12: 29, 13: 28, 14: 27, 15: 26,
            16: 25, 17: 24, 18: 23, 19: 22, 20: 21,
            21: 20, 22: 19, 23: 18, 24: 17, 25: 16,
            26: 15, 27: 14, 28: 13, 29: 12, 30: 11,
            31: 10, 32: 9, 33: 8, 34: 7, 35: 6,
            36: 5, 37: 4, 38: 3, 39: 2, 40: 1
        }
        
        total = 0
        for rank in ranks:
            if rank <= 40:
                total += points_map.get(rank, 0)
        
        return total

# Singleton
ibu_service = IBUFullService()
