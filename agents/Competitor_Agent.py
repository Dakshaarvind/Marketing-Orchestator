# agents/competitor_agent.py
"""
Competitor Research Agent using Yelp Fusion API and Crew AI
Finds real competitors and analyzes their reviews for insights
"""
import os
import json
import requests
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI

load_dotenv()

# Initialize tools
search_tool = DuckDuckGoSearchRun()

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
    # Fields that align with content generation agent
    target_audience: str = Field(default="Local food enthusiasts")
    engagement_times: List[str] = Field(default_factory=list)
    content_tone: str = Field(default="authentic and engaging")
    market_positioning: str = Field(default="Analyzing competitor positioning...")
    suggested_price_point: Optional[str] = Field(default=None)

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
# Define Crew AI Agents
def create_competitor_research_crew(competitors_data: List[Dict], business_type: str) -> Dict:
    """
    Create and run a Crew AI workflow for competitor analysis
    """
    # Create LLM
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create Agents
    market_researcher = Agent(
        role='Market Research Analyst',
        goal='Analyze competitor data and identify market trends',
        backstory="""You are an expert market researcher specializing in the food industry. 
        Your analysis helps businesses understand their competitive landscape and market positioning.""",
        tools=[search_tool],
        llm=llm,
        verbose=True
    )
    
    social_strategist = Agent(
        role='Social Media Strategist',
        goal='Develop actionable social media insights from competitor analysis',
        backstory="""You are an Instagram marketing specialist who helps food businesses grow their presence.
        You turn competitor insights into practical content strategies.""",
        tools=[search_tool],
        llm=llm,
        verbose=True
    )
    
    # Build competitor summary
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
    
    # Create Tasks
    analyze_market = Task(
        description=f"""Analyze these {business_type} competitors and identify key trends:
        
        {competitors_text}
        
        Identify:
        1. Market positioning
        2. Common success factors
        3. Service gaps and opportunities
        4. Target audience preferences
        
        Format as clear bullet points.""",
        agent=market_researcher
    )
    
    create_strategy = Task(
        description="""Using the market analysis, create an Instagram strategy plan with:
        
        1. trending_themes: 3-5 key themes that are working in this market
        2. customer_priorities: 3-5 things customers value most
        3. common_complaints: 2-4 pain points to address
        4. content_opportunities: 3-5 specific content ideas
        5. recommended_hashtags: 5-8 relevant hashtags (with #)
        
        Return ONLY as a JSON object with these exact keys.""",
        agent=social_strategist
    )
    
    # Create and run crew
    crew = Crew(
        agents=[market_researcher, social_strategist],
        tasks=[analyze_market, create_strategy],
        verbose=True,
        process=Process.sequential
    )
    
    result = crew.kickoff()
    
    try:
        # Extract JSON from the final result
        start_idx = result.find('{')
        end_idx = result.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            json_str = result[start_idx:end_idx]
            return json.loads(json_str)
    except:
        pass
    
    # Fallback if JSON parsing fails
    return generate_fallback_insights(competitors_data, business_type)

def generate_fallback_insights(competitors_data: List[Dict], business_type: str) -> Dict:
    """Generate basic insights when LLM fails"""
    avg_rating = sum(c['rating'] for c in competitors_data) / len(competitors_data) if competitors_data else 0
    
    # Extract unique categories
    all_categories = []
    for comp in competitors_data:
        all_categories.extend([cat['title'] for cat in comp.get('categories', [])])
    unique_categories = list(set(all_categories))
    
    # Get price range
    prices = [c.get('price', '') for c in competitors_data if c.get('price')]
    if prices:
        price_range = f"{min(prices, key=len)} - {max(prices, key=len)}"
    else:
        price_range = "Competitive pricing"

    # Determine peak times (simplified)
    peak_times = ["11:30", "13:30", "18:30"]  # Common meal times
    
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
        ],
        # Additional fields for content generation alignment
        "target_audience": f"Local {business_type} enthusiasts seeking quality dining experiences",
        "engagement_times": peak_times,
        "content_tone": "authentic and engaging",
        "market_positioning": f"Competitive {business_type} market with focus on quality and service",
        "suggested_price_point": price_range
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
    
    insights = create_competitor_research_crew(businesses, business_type)
    
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