"""Kompletní test všech API endpointů"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_endpoint(name, url, method="GET", data=None):
    """Test jednotlivého endpointu"""
    print(f"\n{'='*50}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
            
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ Success - Found {len(data)} items")
                if data:
                    print(f"Sample: {json.dumps(data[0], indent=2)[:200]}...")
            else:
                print(f"✅ Success")
                print(f"Data: {json.dumps(data, indent=2)[:200]}...")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("BIATHLON ANALYTICS - API ENDPOINT TEST")
    print("="*60)
    
    results = {}
    
    # Test všech endpointů
    tests = [
        ("Athletes - Czech Team", f"{BASE_URL}/athletes?nation=CZE"),
        ("Athletes - All", f"{BASE_URL}/athletes?limit=5"),
        ("Athlete Performance - Davidova", f"{BASE_URL}/athletes/BTCZE20301199701/performance"),
        ("Athlete History - Davidova", f"{BASE_URL}/athletes/BTCZE20301199701/history"),
        ("Recent Races", f"{BASE_URL}/races/recent"),
        ("Upcoming Races", f"{BASE_URL}/races/upcoming"),
        ("Race Analysis", f"{BASE_URL}/races/BT2425SWRLCP07SWSP/analysis"),
        ("Head to Head", f"{BASE_URL}/athletes/compare?athlete1=BTCZE20301199701&athlete2=BTCZE23105200001"),
        ("Test Connection", f"{BASE_URL}/test/test-connection"),
    ]
    
    for name, url in tests:
        results[name] = test_endpoint(name, url)
    
    # Souhrn
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    working = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print(f"\n{working}/{total} endpoints working")
    
    if working < total:
        print("\n⚠️  Some endpoints are not working!")
        print("Let's fix them...")

if __name__ == "__main__":
    main()
