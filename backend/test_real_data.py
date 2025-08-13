"""
KOMPLETNÍ TEST REÁLNÝCH DAT Z IBU API
======================================
"""

import requests
import json
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:8000/api/v1"

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}{text}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

def print_success(text):
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")

def print_data(label, data):
    print(f"{Fore.BLUE}{label}:{Style.RESET_ALL} {data}")

def test_endpoint(name, url, expected_fields=None):
    """Test jednotlivého endpointu a ověř reálná data"""
    print(f"\n{Fore.YELLOW}Testing: {name}{Style.RESET_ALL}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Kontrola, že máme data
            if isinstance(data, list):
                if len(data) > 0:
                    print_success(f"Received {len(data)} items")
                    
                    # Ukázka prvního záznamu
                    first_item = data[0]
                    print(f"\n{Fore.CYAN}Sample data:{Style.RESET_ALL}")
                    
                    # Kontrola očekávaných polí
                    if expected_fields:
                        for field in expected_fields:
                            if field in first_item:
                                value = first_item[field]
                                print_data(f"  {field}", value)
                            else:
                                print_warning(f"  Missing field: {field}")
                    else:
                        # Zobraz všechna pole
                        for key, value in list(first_item.items())[:5]:
                            print_data(f"  {key}", value)
                    
                    # Ověření, že data jsou reálná (ne mock)
                    if 'name' in first_item:
                        czech_names = ['DAVIDOVÁ', 'VOBORNÍKOVÁ', 'JISLOVÁ', 'CHARVÁTOVÁ', 'OTCOVSKÁ']
                        is_real = any(name in first_item['name'].upper() for name in czech_names)
                        if is_real:
                            print_success("REAL DATA CONFIRMED - Czech athlete found!")
                        else:
                            print_warning("Data found but no Czech athletes")
                else:
                    print_warning("Empty list returned")
                    
            elif isinstance(data, dict):
                print_success("Received object data")
                print(f"\n{Fore.CYAN}Data structure:{Style.RESET_ALL}")
                for key in list(data.keys())[:5]:
                    print_data(f"  {key}", type(data[key]).__name__)
                    
            return True, data
            
        else:
            print_error(f"HTTP {response.status_code}: {response.text[:100]}")
            return False, None
            
    except requests.exceptions.Timeout:
        print_error("Request timeout - server might be slow")
        return False, None
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server - is it running?")
        return False, None
    except Exception as e:
        print_error(f"Exception: {e}")
        return False, None

def main():
    print_header("BIATHLON ANALYTICS - REAL DATA VERIFICATION")
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: {BASE_URL}")
    
    # Test connectivity
    print_header("1. TESTING SERVER CONNECTION")
    try:
        response = requests.get(f"{BASE_URL}/test/test-connection", timeout=5)
        if response.status_code == 200:
            print_success("Server is running!")
        else:
            print_error(f"Server returned: {response.status_code}")
    except:
        print_error("Cannot connect to server at http://localhost:8000")
        print_warning("Please start the backend: uvicorn app.main:app --reload")
        return
    
    # Test athletes endpoints
    print_header("2. TESTING ATHLETES ENDPOINTS")
    
    # Czech athletes
    success, czech_athletes = test_endpoint(
        "Czech Athletes",
        f"{BASE_URL}/athletes?nation=CZE&limit=10",
        expected_fields=['id', 'name', 'nation', 'world_rank', 'world_cup_points']
    )
    
    if success and czech_athletes:
        # Test performance endpoint pro prvního atleta
        athlete_id = czech_athletes[0].get('id')
        if athlete_id:
            test_endpoint(
                f"Athlete Performance ({athlete_id})",
                f"{BASE_URL}/athletes/{athlete_id}/performance",
                expected_fields=['athlete_id', 'avg_rank', 'shooting']
            )
            
            test_endpoint(
                f"Athlete History ({athlete_id})",
                f"{BASE_URL}/athletes/{athlete_id}/history",
                expected_fields=['history', 'trends']
            )
    
    # Test races endpoints
    print_header("3. TESTING RACES ENDPOINTS")
    
    success, races = test_endpoint(
        "Recent Races",
        f"{BASE_URL}/races/recent",
        expected_fields=['race_id', 'date', 'location', 'description']
    )
    
    test_endpoint(
        "Upcoming Races",
        f"{BASE_URL}/races/upcoming",
        expected_fields=['race_id', 'date', 'location', 'description']
    )
    
    if success and races and len(races) > 0:
        race_id = races[0].get('race_id')
        if race_id:
            test_endpoint(
                f"Race Analysis ({race_id})",
                f"{BASE_URL}/races/{race_id}/analysis",
                expected_fields=['race_id', 'czech_athletes', 'winner']
            )
    
    # Test comparison
    print_header("4. TESTING COMPARISON ENDPOINT")
    
    if czech_athletes and len(czech_athletes) >= 2:
        athlete1_id = czech_athletes[0].get('id')
        athlete2_id = czech_athletes[1].get('id')
        
        if athlete1_id and athlete2_id:
            test_endpoint(
                "Head to Head Comparison",
                f"{BASE_URL}/athletes/compare?athlete1={athlete1_id}&athlete2={athlete2_id}",
                expected_fields=['total_races', 'athlete1_wins', 'athlete2_wins']
            )
    
    # Summary
    print_header("5. DATA VERIFICATION SUMMARY")
    
    if czech_athletes:
        print_success(f"Found {len(czech_athletes)} Czech athletes")
        print("\n🇨🇿 Czech Team Roster:")
        for i, athlete in enumerate(czech_athletes[:5], 1):
            name = athlete.get('name', 'Unknown')
            rank = athlete.get('world_rank', 'N/A')
            points = athlete.get('world_cup_points', 0)
            print(f"  {i}. {name:25} Rank: #{rank:3}  Points: {points:4}")
    
    # Check for mock data indicators
    print_header("6. MOCK DATA CHECK")
    
    mock_indicators = ['test', 'mock', 'example', 'demo']
    has_mock = False
    
    if czech_athletes:
        for athlete in czech_athletes:
            name = athlete.get('name', '').lower()
            if any(indicator in name for indicator in mock_indicators):
                has_mock = True
                print_warning(f"Possible mock data detected: {athlete.get('name')}")
    
    if not has_mock:
        print_success("No mock data indicators found - appears to be REAL DATA!")
    
    print_header("TEST COMPLETE")
    print(f"\n{Fore.GREEN}✅ All tests completed!{Style.RESET_ALL}")
    print(f"\n💡 To see this data in the frontend:")
    print(f"   1. Make sure backend is running: uvicorn app.main:app --reload")
    print(f"   2. Start frontend: npm run dev")
    print(f"   3. Open http://localhost:3000")

if __name__ == "__main__":
    # Nainstaluj colorama pokud chybí
    try:
        from colorama import init, Fore, Style
    except ImportError:
        print("Installing colorama for colored output...")
        import subprocess
        subprocess.check_call(["pip", "install", "colorama"])
        from colorama import init, Fore, Style
    
    main()
