#!/usr/bin/env python3
"""Load biathlon data using existing scraper"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from data.scraper import download_race_data, download_cup_data, load_config, load_state, save_state
import biathlonresults

def main():
    print("📊 Loading biathlon data...")

    config = load_config()
    state = load_state()

    # Get some recent races
    for season_id in config['seasons_to_track']:
        print(f"Loading season {season_id}...")

        events = biathlonresults.events(season_id, level=1)
        for event in events[:5]:  # Last 5 events
            if event_id := event.get("EventId"):
                competitions = biathlonresults.competitions(event_id)
                for comp in competitions:
                    if race_id := comp.get("RaceId"):
                        download_race_data(race_id)

    print("✅ Data loading complete!")

if __name__ == "__main__":
    main()
