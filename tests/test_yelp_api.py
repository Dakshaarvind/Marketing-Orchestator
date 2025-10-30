
"""
Test script to verify Yelp API access
Run this first to make sure your API key works
"""
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

def test_yelp_search():
    """Test Yelp Business Search API"""
    
    api_key = os.getenv("YELP_API_KEY")
    
    if not api_key:
        print(" YELP_API_KEY not found in .env file")
        print("\nGet your key from: https://www.yelp.com/developers/v3/manage_app")
        return False
    
    print("=" * 60)
    print("TESTING YELP API")
    print("=" * 60)
    print(f"API Key: {api_key[:20]}...")
    
    # Test parameters
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    params = {
        "term": "donut shop",
        "location": "Los Angeles, CA",
        "limit": 5,
        "sort_by": "rating"
    }
    
    print(f"\nSearching for: {params['term']} in {params['location']}")
    print("Requesting...")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            businesses = data.get('businesses', [])
            
            print(f"\n SUCCESS! Found {len(businesses)} businesses")
            print("\n" + "-" * 60)
            
            for i, biz in enumerate(businesses, 1):
                print(f"\n{i}. {biz['name']}")
                print(f"   Rating: {biz['rating']} ({biz['review_count']} reviews)")
                print(f"   Price: {biz.get('price', 'N/A')}")
                print(f"   Location: {', '.join(biz['location']['display_address'])}")
                print(f"   Categories: {', '.join([c['title'] for c in biz['categories']])}")
            
            return True
            
        elif response.status_code == 401:
            print("\n ERROR: Invalid API key")
            print("Check your YELP_API_KEY in .env")
            return False
            
        else:
            print(f"\n ERROR: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"\n ERROR: {e}")
        return False

def test_yelp_reviews():
    """Test Yelp Reviews API"""
    
    api_key = os.getenv("YELP_API_KEY")
    
    print("\n" + "=" * 60)
    print("TESTING YELP REVIEWS API")
    print("=" * 60)
    
    # First get a business ID
    search_url = "https://api.yelp.com/v3/businesses/search"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    search_response = requests.get(
        search_url,
        headers=headers,
        params={"term": "donut", "location": "Los Angeles", "limit": 1}
    )
    
    if search_response.status_code != 200:
        print(" Could not search for business")
        return False
    
    business = search_response.json()['businesses'][0]
    business_id = business['id']
    business_name = business['name']
    
    print(f"Getting reviews for: {business_name}")
    
    # Get reviews
    reviews_url = f"https://api.yelp.com/v3/businesses/{business_id}/reviews"
    reviews_response = requests.get(reviews_url, headers=headers)
    
    if reviews_response.status_code == 200:
        reviews_data = reviews_response.json()
        reviews = reviews_data.get('reviews', [])
        
        print(f"\n SUCCESS! Found {len(reviews)} reviews")
        print("\n" + "-" * 60)
        
        for i, review in enumerate(reviews, 1):
            print(f"\nReview {i}:")
            print(f"Rating: {review['rating']}")
            print(f"Text: {review['text'][:100]}...")
            
        return True
    else:
        print(f"\n ERROR: {reviews_response.status_code}")
        return False

if __name__ == "__main__":
    print("\n Yelp API Test Script\n")
    
    # Test 1: Search
    search_ok = test_yelp_search()
    
    if search_ok:
        # Test 2: Reviews
        test_yelp_reviews()
        
        print("\n" + "=" * 60)
        print(" ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYou're ready to build the Competitor Agent!")
    else:
        print("\n" + "=" * 60)
        print(" TESTS FAILED")
        print("=" * 60)
        print("\nFix the errors above before continuing.")