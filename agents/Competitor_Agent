
"""
Competitor Research Agent using Yelp Fusion API
Finds real competitors and analyzes their reviews for insights
"""
import requests
import os
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Pydantic Models
class CompetitorProfile(BaseModel):
    """Individual competitor information"""
    business_name: str
    yelp_url: str
    rating: float
    review_count: int
    price: Optional[str] = None
    categories: List[str]
    location: str
    phone: Optional[str] = None
    popular_items: List[str] = Field(default_factory=list)

class CompetitorInsights(BaseModel):
    """Complete competitor analysis output"""
    competitors: List[CompetitorProfile]
    trending_themes: List[str]
    customer_priorities: List[str]
    common_complaints: List[str]
    content_opportunities: List[str]
    recommended_hashtags: List[str]

# Yelp API Client
class YelpClient:
    """Client for interacting with Yelp Fusion API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("YELP_API_KEY")
        if not self.api_key:
            raise ValueError("YELP_API_KEY not found in environment variables")
        
        self.base_url = "https://api.yelp.com/v3"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def search_businesses(
        self, 
        term: str, 
        location: str, 
        limit: int = 5,
        sort_by: str = "rating"
    ) -> List[Dict]:
        """
        Search for businesses on Yelp
        
        Args:
            term: Business type (e.g., "donut shop")
            location: Location to search (e.g., "Los Angeles, CA")
            limit: Number of results (max 50)
            sort_by: Sort criteria ("rating", "review_count", "distance")
            
        Returns:
            List of business dictionaries
        """
        url = f"{self.base_url}/businesses/search"
        params = {
            "term": term,
            "location": location,
            "limit": limit,
            "sort_by": sort_by
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('businesses', [])
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching Yelp: {e}")
            return []
    
    def get_reviews(self, business_id: str, limit: int = 3) -> List[Dict]:
        """
        Get reviews for a specific business
        
        Args:
            business_id: Yelp business ID
            limit: Number of reviews to fetch (max 3 on free tier)
            
        Returns:
            List of review dictionaries
        """
        url = f"{self.base_url}/businesses/{business_id}/reviews"
        params = {"limit": limit}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('reviews', [])
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting reviews: {e}")
            return []

# Review Analysis
def analyze_reviews_with_llm(all_reviews: List[str], business_type: str) -> Dict:
    """
    Use LLM to analyze competitor reviews and extract insights
    
    Args:
        all_reviews: List of review texts
        business_type: Type of business being analyzed
        
    Returns:
        Dict with themes, priorities, complaints, opportunities
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Combine reviews
    reviews_text = "\n\n".join([f"Review {i+1}: {review}" for i, review in enumerate(all_reviews)])
    
    prompt = f"""Analyze these customer reviews from competing {business_type} businesses:

{reviews_text}

Extract the following insights in JSON format:

1. trending_themes: What themes/topics appear most frequently? (list of 3-5 strings)
2. customer_priorities: What do customers care about most? (list of 3-5 strings)
3. common_complaints: What issues appear across multiple reviews? (list of 2-4 strings)
4. content_opportunities: Based on gaps/unmet needs, what Instagram content would resonate? (list of 3-5 strings)
5. recommended_hashtags: Based on popular items and themes mentioned (list of 5-8 hashtags with #)

Return ONLY valid JSON with these exact keys.
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing customer reviews and extracting marketing insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Extract JSON
        start_idx = result_text.find('{')
        end_idx = result_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = result_text[start_idx:end_idx]
            insights = json.loads(json_str)
            return insights
        else:
            # Fallback
            return {
                "trending_themes": ["Quality and freshness", "Variety"],
                "customer_priorities": ["Taste", "Value"],
                "common_complaints": ["Long wait times"],
                "content_opportunities": ["Showcase daily fresh items", "Behind-the-scenes content"],
                "recommended_hashtags": [f"#{business_type.replace(' ', '')}", "#foodie", "#local"]
            }
            
    except Exception as e:
        print(f"Error analyzing reviews with LLM: {e}")
        return {
            "trending_themes": [],
            "customer_priorities": [],
            "common_complaints": [],
            "content_opportunities": [],
            "recommended_hashtags": []
        }

# Main function
def run_competitor_agent(
    business_type: str,
    location: Optional[str] = None,
    api_key: Optional[str] = None
) -> CompetitorInsights:
    """
    Run the competitor research agent
    
    Args:
        business_type: Type of business (e.g., "donut shop")
        location: Business location (e.g., "Los Angeles, CA")
        api_key: Yelp API key (optional, reads from env if not provided)
        
    Returns:
        CompetitorInsights object with full analysis
    """
    
    # Default location if not provided
    if not location:
        location = "United States"
    
    print(f"\n Searching for {business_type} competitors in {location}...")
    
    # Initialize Yelp client
    yelp = YelpClient(api_key)
    
    # Search for competitors
    businesses = yelp.search_businesses(
        term=business_type,
        location=location,
        limit=5,
        sort_by="rating"
    )
    
    if not businesses:
        print("  No competitors found on Yelp")
        return CompetitorInsights(
            competitors=[],
            trending_themes=["No data available"],
            customer_priorities=["No data available"],
            common_complaints=["No data available"],
            content_opportunities=["Focus on unique value proposition"],
            recommended_hashtags=[f"#{business_type.replace(' ', '')}"]
        )
    
    print(f"✓ Found {len(businesses)} competitors")
    
    # Build competitor profiles and collect reviews
    competitors = []
    all_reviews = []
    
    for biz in businesses:
        # Get reviews for this business
        reviews = yelp.get_reviews(biz['id'], limit=3)
        
        # Extract review texts
        review_texts = [r['text'] for r in reviews]
        all_reviews.extend(review_texts)
        
        # Create competitor profile
        competitor = CompetitorProfile(
            business_name=biz['name'],
            yelp_url=biz['url'],
            rating=biz['rating'],
            review_count=biz['review_count'],
            price=biz.get('price'),
            categories=[cat['title'] for cat in biz.get('categories', [])],
            location=', '.join(biz['location']['display_address']),
            phone=biz.get('phone'),
            popular_items=[]  # Will be extracted from reviews
        )
        
        competitors.append(competitor)
        
        print(f"  • {biz['name']}: {biz['rating']} ({biz['review_count']} reviews)")
    
    # Analyze all reviews with LLM
    print(f"\n Analyzing {len(all_reviews)} reviews...")
    
    if all_reviews:
        insights = analyze_reviews_with_llm(all_reviews, business_type)
    else:
        insights = {
            "trending_themes": [],
            "customer_priorities": [],
            "common_complaints": [],
            "content_opportunities": [],
            "recommended_hashtags": []
        }
    
    print("✓ Analysis complete!")
    
    # Build final output
    result = CompetitorInsights(
        competitors=competitors,
        trending_themes=insights.get('trending_themes', []),
        customer_priorities=insights.get('customer_priorities', []),
        common_complaints=insights.get('common_complaints', []),
        content_opportunities=insights.get('content_opportunities', []),
        recommended_hashtags=insights.get('recommended_hashtags', [])
    )
    
    return result

# Test execution
if __name__ == "__main__":
    # Test with donut shop
    result = run_competitor_agent(
        business_type="donut shop",
        location="Los Angeles, CA"
    )
    
    print("\n" + "=" * 60)
    print("COMPETITOR ANALYSIS RESULTS")
    print("=" * 60)
    
    print(f"\n Found {len(result.competitors)} Competitors:")
    for comp in result.competitors:
        print(f"\n  • {comp.business_name}")
        print(f"    Rating: {comp.rating} ({comp.review_count} reviews)")
        print(f"    Price: {comp.price or 'N/A'}")
        print(f"    Location: {comp.location}")
    
    print(f"\n Trending Themes:")
    for theme in result.trending_themes:
        print(f"  • {theme}")
    
    print(f"\n Customer Priorities:")
    for priority in result.customer_priorities:
        print(f"  • {priority}")
    
    print(f"\n  Common Complaints:")
    for complaint in result.common_complaints:
        print(f"  • {complaint}")
    
    print(f"\n Content Opportunities:")
    for opp in result.content_opportunities:
        print(f"  • {opp}")
    
    print(f"\n#️ Recommended Hashtags:")
    print(f"  {' '.join(result.recommended_hashtags)}")