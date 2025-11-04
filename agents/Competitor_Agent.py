# agents/competitor_agent.py
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
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # 404 is common - reviews not available for this business
                return []
            print(f"HTTP Error getting reviews: {e}")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Error getting reviews: {e}")
            return []

# Review Analysis
def analyze_competitors_with_llm(competitors_data: List[Dict], business_type: str) -> Dict:
    """
    Use LLM to analyze competitors and extract insights
    Uses business data (ratings, categories, review counts) instead of review text
    
    Args:
        competitors_data: List of competitor business info
        business_type: Type of business being analyzed
        
    Returns:
        Dict with themes, priorities, complaints, opportunities
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Build competitor summary from business data
    competitor_summary = []
    for comp in competitors_data:
        summary = f"""
Business: {comp['name']}
Rating: {comp['rating']}/5.0 ({comp['review_count']} reviews)
Price: {comp.get('price', 'N/A')}
Categories: {', '.join([cat['title'] for cat in comp.get('categories', [])])}
Location: {', '.join(comp['location']['display_address'])}
"""
        competitor_summary.append(summary)
    
    competitors_text = "\n---\n".join(competitor_summary)
    
    prompt = f"""Analyze these competing {business_type} businesses and extract Instagram marketing insights:

{competitors_text}

Based on their ratings, review counts, pricing, and categories, provide insights in JSON format:

1. trending_themes: What themes/strategies are working? (3-5 strings, e.g., "High ratings indicate quality focus", "Multiple locations suggest strong brand")
2. customer_priorities: What do customers value? (3-5 strings, inferred from high-rated businesses)
3. common_complaints: Potential weaknesses to avoid (2-4 strings, inferred from lower ratings or gaps)
4. content_opportunities: Instagram content ideas based on competitor positioning (3-5 strings)
5. recommended_hashtags: Relevant hashtags for {business_type} (5-8 hashtags with #)

Return ONLY valid JSON with these exact keys. Be specific and actionable.
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert at competitive analysis and Instagram marketing strategy."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=600
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
            # Fallback based on business data
            return generate_fallback_insights(competitors_data, business_type)
            
    except Exception as e:
        print(f"Error analyzing with LLM: {e}")
        return generate_fallback_insights(competitors_data, business_type)

def generate_fallback_insights(competitors_data: List[Dict], business_type: str) -> Dict:
    """Generate basic insights when LLM fails"""
    avg_rating = sum(c['rating'] for c in competitors_data) / len(competitors_data) if competitors_data else 0
    
    # Extract unique categories
    all_categories = []
    for comp in competitors_data:
        all_categories.extend([cat['title'] for cat in comp.get('categories', [])])
    unique_categories = list(set(all_categories))
    
    return {
        "trending_themes": [
            f"Average competitor rating: {avg_rating:.1f}/5.0 - quality is important",
            f"Common categories: {', '.join(unique_categories[:3])}"
        ],
        "customer_priorities": [
            "Quality and consistency",
            "Good value for price",
            "Convenient location"
        ],
        "common_complaints": [
            "Competition is strong in this area",
            "Differentiation needed"
        ],
        "content_opportunities": [
            "Highlight unique offerings",
            "Showcase quality ingredients",
            "Share customer testimonials",
            "Behind-the-scenes content"
        ],
        "recommended_hashtags": [
            f"#{business_type.replace(' ', '')}",
            "#foodie",
            "#local",
            "#instafood",
            "#delicious"
        ]
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
    
    print(f"\n🔍 Searching for {business_type} competitors in {location}...")
    
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
        print("⚠️  No competitors found on Yelp")
        return CompetitorInsights(
            competitors=[],
            trending_themes=["No data available"],
            customer_priorities=["No data available"],
            common_complaints=["No data available"],
            content_opportunities=["Focus on unique value proposition"],
            recommended_hashtags=[f"#{business_type.replace(' ', '')}"]
        )
    
    print(f"✓ Found {len(businesses)} competitors")
    
    # Build competitor profiles
    competitors = []
    
    for biz in businesses:
        # Get reviews for this business (but don't fail if 404)
        reviews = yelp.get_reviews(biz['id'], limit=3)
        
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
            popular_items=[]
        )
        
        competitors.append(competitor)
        
        print(f"  • {biz['name']}: {biz['rating']}⭐ ({biz['review_count']} reviews)")
    
    # Analyze competitors using business data (not reviews)
    print(f"\n🤖 Analyzing {len(businesses)} competitors...")
    
    insights = analyze_competitors_with_llm(businesses, business_type)
    
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
    
    print(f"\n📊 Found {len(result.competitors)} Competitors:")
    for comp in result.competitors:
        print(f"\n  • {comp.business_name}")
        print(f"    Rating: {comp.rating}⭐ ({comp.review_count} reviews)")
        print(f"    Price: {comp.price or 'N/A'}")
        print(f"    Location: {comp.location}")
    
    print(f"\n🔥 Trending Themes:")
    for theme in result.trending_themes:
        print(f"  • {theme}")
    
    print(f"\n⭐ Customer Priorities:")
    for priority in result.customer_priorities:
        print(f"  • {priority}")
    
    print(f"\n⚠️  Common Complaints:")
    for complaint in result.common_complaints:
        print(f"  • {complaint}")
    
    print(f"\n💡 Content Opportunities:")
    for opp in result.content_opportunities:
        print(f"  • {opp}")
    
    print(f"\n#️⃣ Recommended Hashtags:")
    print(f"  {' '.join(result.recommended_hashtags)}")