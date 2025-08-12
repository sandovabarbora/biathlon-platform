"""Test script to discover biathlonresults API"""

import biathlonresults as br
import json

print("=== Testing biathlonresults API ===")
print("\nAvailable methods:")
print(dir(br))

# Test basic functions
try:
    # Get cups for season
    print("\n1. Testing Cups:")
    cups = br.Cups(2425)
    print(f"   Found {len(cups.cups)} cups")
    if cups.cups:
        print(f"   Sample: {cups.cups[0]}")
    
    # Get cup results
    print("\n2. Testing Cup Results:")
    if cups.cups:
        cup_id = cups.cups[0]['CupId']
        results = br.CupResults(cup_id)
        print(f"   Results type: {type(results)}")
        if hasattr(results, 'results'):
            print(f"   Found {len(results.results)} results")
            if results.results:
                print(f"   Sample athlete: {results.results[0]}")
    
    # Get events
    print("\n3. Testing Events:")
    events = br.Events(2425)
    print(f"   Found {len(events.events)} events")
    if events.events:
        print(f"   Sample event: {events.events[0]}")
        
        # Get competitions for event
        event_id = events.events[0]['EventId']
        print(f"\n4. Testing Competitions for event {event_id}:")
        comps = br.Competitions(event_id)
        print(f"   Found {len(comps.competitions)} competitions")
        if comps.competitions:
            print(f"   Sample: {comps.competitions[0]}")
            
            # Get results for competition
            race_id = comps.competitions[0]['RaceId']
            print(f"\n5. Testing Results for race {race_id}:")
            results = br.Results(race_id)
            print(f"   Found {len(results.results)} results")
            if results.results:
                print(f"   Winner: {results.results[0]}")
    
    # Get athlete
    print("\n6. Testing Athlete:")
    # Try to find Czech athlete from results
    for result in results.results[:50]:
        if result.get('Nat') == 'CZE':
            ibu_id = result.get('IBUId')
            print(f"   Found Czech athlete: {ibu_id}")
            
            # Get athlete info
            athlete = br.Athlete(ibu_id)
            print(f"   Athlete type: {type(athlete)}")
            if hasattr(athlete, '__dict__'):
                print(f"   Athlete data: {athlete.__dict__}")
            break
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
