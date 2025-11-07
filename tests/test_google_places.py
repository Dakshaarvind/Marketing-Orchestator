# test_google_places.py
"""
Test Google Places API and compare with Yelp for competitor analysis
"""
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

def test_google_text_search():
    """Test Google Places Text Search (find competitors)"""
    
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_PLACES_API_KEY not found in .env")
        print("\nGet your key from: https://console.cloud.google.com/")
        print("Enable: Places API (New)")
        return None
    
    print("=" * 60)
    print("TESTING GOOGLE PLACES TEXT SEARCH")
    print("=" * 60)
    print(f"API Key: {api_key[:20]}...")
    
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        'query': 'donut shop in Los Angeles, CA',
        'key': api_key
    }
    
    print(f"\nSearching for: {params['query']}")
    print("Requesting...")
    
    try:
        response = requests.get(url, params=params)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'OK':
                results = data.get('results', [])
                print(f"\n✅ SUCCESS! Found {len(results)} businesses")
                print("\n" + "-" * 60)
                
                place_ids = []
                
                for i, place in enumerate(results[:5], 1):  # Show top 5
                    print(f"\n{i}. {place['name']}")
                    print(f"   Rating: {place.get('rating', 'N/A')}⭐ ({place.get('user_ratings_total', 0)} reviews)")
                    print(f"   Address: {place.get('formatted_address', 'N/A')}")
                    print(f"   Place ID: {place['place_id'][:20]}...")
                    
                    if place.get('price_level'):
                        price = '$' * place['price_level']
                        print(f"   Price: {price}")
                    
                    place_ids.append(place['place_id'])
                
                return place_ids
            else:
                print(f"\n❌ ERROR: {data.get('status')} - {data.get('error_message', '')}")
                return None
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None

def test_google_place_details(place_id):
    """Test Google Places Details API (get reviews)"""
    
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    
    print("\n" + "=" * 60)
    print("TESTING GOOGLE PLACES DETAILS (REVIEWS)")
    print("=" * 60)
    print(f"Place ID: {place_id[:30]}...")
    
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'place_id': place_id,
        'fields': 'name,rating,reviews,user_ratings_total,price_level,opening_hours',
        'key': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'OK':
                result = data.get('result', {})
                reviews = result.get('reviews', [])
                
                print(f"\n✅ SUCCESS!")
                print(f"Business: {result.get('name')}")
                print(f"Rating: {result.get('rating')}⭐ ({result.get('user_ratings_total')} total reviews)")
                print(f"\nFound {len(reviews)} reviews (Google returns up to 5)")
                
                print("\n" + "-" * 60)
                
                for i, review in enumerate(reviews, 1):
                    print(f"\nReview {i}:")
                    print(f"Author: {review.get('author_name')}")
                    print(f"Rating: {review.get('rating')}⭐")
                    print(f"Text: {review.get('text')[:150]}...")
                    print(f"Time: {review.get('relative_time_description')}")
                
                return len(reviews)
            else:
                print(f"\n❌ ERROR: {data.get('status')}")
                return 0
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            return 0
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return 0

def compare_yelp_vs_google():
    """Compare results from both APIs"""
    
    print("\n" + "=" * 60)
    print("COMPARISON: YELP vs GOOGLE PLACES")
    print("=" * 60)
    
    comparison = {
        "Yelp API": {
            "Cost": "FREE (5000/day)",
            "Search": "✅ Works well",
            "Reviews Access": "❌ Often 404",
            "Reviews per Business": "Max 3 (when available)",
            "Additional Data": "Categories, phone, price"
        },
        "Google Places": {
            "Cost": "$0.032 (search) + $0.017 (details) = $0.05 per competitor",
            "Search": "✅ Works well",
            "Reviews Access": "✅ More reliable (testing...)",
            "Reviews per Business": "Up to 5",
            "Additional Data": "Popular times, opening hours, photos"
        }
    }
    
    for api, features in comparison.items():
        print(f"\n{api}:")
        for feature, value in features.items():
            print(f"  {feature}: {value}")
    
    print("\n" + "=" * 60)
    print("COST ESTIMATE")
    print("=" * 60)
    print("\nPer campaign request (5 competitors):")
    print("  Yelp: $0")
    print("  Google: $0.25")
    print("\nFor 1000 requests/month:")
    print("  Yelp: $0")
    print("  Google: $250")

if __name__ == "__main__":
    print("\n🔍 Google Places API Test & Comparison\n")
    
    # Test 1: Search for businesses
    place_ids = test_google_text_search()
    
    if place_ids:
        # Test 2: Get details for first business
        input("\n\nPress Enter to test Place Details (this costs $0.017)...")
        test_google_place_details(place_ids[0])
        
        # Show comparison
        input("\n\nPress Enter to see Yelp vs Google comparison...")
        compare_yelp_vs_google()
        
        print("\n" + "=" * 60)
        print("RECOMMENDATION")
        print("=" * 60)
        print("""
Based on testing:

Option 1: HYBRID APPROACH (Recommended)
- Use Yelp for search (free)
- Fallback to Google for reviews if Yelp returns 404
- Keeps costs low (~$0.05 per request only when needed)

Option 2: GOOGLE ONLY
- More reliable, consistent data
- Costs ~$0.25 per request
- Better if budget allows

Option 3: KEEP YELP ONLY
- Free
- Analyze business metadata instead of reviews
- Current working solution
""")
    else:
        print("\n❌ Tests failed - check API key and billing")