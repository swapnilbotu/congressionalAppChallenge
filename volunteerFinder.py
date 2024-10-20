import requests
import json

def search_volunteer_opportunities(params=None):
    base_url = "https://www.volunteerconnector.org/api/search/"
    
    if params is None:
        params = {}
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

def display_opportunities(opportunities):
    for opp in opportunities['results']:
        print(f"Title: {opp['title']}")
        print(f"Organization: {opp['organization']['name']}")
        print(f"Description: {opp['description'][:100]}...")  # Truncate description
        print(f"Remote/Online: {'Yes' if opp['remote_or_online'] else 'No'}")
        print(f"Dates: {opp['dates']}")
        print(f"More info: {opp['url']}")
        print("-" * 50)

def main():
    # Example search parameters
    params = {
        "ac": [5, 131, 59],  # Activity codes
        "cc": 64  # Category code
    }
    
    results = search_volunteer_opportunities(params)
    
    if results:
        print(f"Total opportunities found: {results['count']}")
        display_opportunities(results)

if __name__ == "__main__":
    main()