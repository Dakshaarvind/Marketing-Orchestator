"""
SEO Agent: Optimizes Instagram content for search and discoverability
Takes output from Content Generation Agent and enhances it for SEO
"""
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import json
import os


class SEOOutput(BaseModel):
    """SEO-optimized content output"""
    optimized_caption: str = Field(description="SEO-optimized caption with keywords")
    optimized_hashtags: List[str] = Field(description="SEO-optimized hashtags (mix of high, medium, low competition)")
    keyword_suggestions: List[str] = Field(description="Primary keywords for this content")
    seo_score: int = Field(description="SEO score out of 100")
    improvements: List[str] = Field(description="List of SEO improvements made")
    alt_text_suggestion: Optional[str] = Field(default=None, description="Alt text for image accessibility and SEO")
    location_tags: Optional[List[str]] = Field(default_factory=list, description="Location-based tags for local SEO")


class SEOAgentConfig:
    """Configuration and creation of the SEO Agent"""
    
    @staticmethod
    def create_agent(llm: ChatOpenAI) -> Agent:
        """
        Creates the SEO Agent with specific role and capabilities
        
        Args:
            llm: Language model instance
            
        Returns:
            Configured CrewAI Agent
        """
        return Agent(
            role="Instagram SEO Specialist",
            goal="Optimize Instagram content for maximum discoverability, search visibility, and engagement through strategic keyword placement, hashtag optimization, and SEO best practices",
            backstory="""You are an expert Instagram SEO specialist who understands how Instagram's search algorithm works.
            You know that Instagram SEO involves:
            - Strategic keyword placement in captions
            - Mix of high, medium, and low competition hashtags
            - Location-based optimization for local businesses
            - Alt text optimization for accessibility and search
            - Content structure that encourages engagement (which boosts search ranking)
            - Trending vs. niche hashtag balance
            
            You optimize content to appear in:
            - Instagram search results (hashtags, keywords)
            - Explore page recommendations
            - Location-based discovery
            - Reels/Stories discovery
            
            You balance SEO optimization with natural, engaging content that doesn't feel keyword-stuffed.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    @staticmethod
    def create_task(
        agent: Agent,
        business_type: str,
        location: Optional[str],
        content_data: Dict,
        campaign_goals: str
    ) -> Task:
        """
        Creates the SEO optimization task
        
        Args:
            agent: The SEO Agent
            business_type: Type of business
            location: Business location (for local SEO)
            content_data: Output from Content Generation Agent
            campaign_goals: Campaign objectives
            
        Returns:
            Configured CrewAI Task
        """
        caption = content_data.get('caption', '')
        hashtags = content_data.get('hashtags', [])
        post_type = content_data.get('post_type', 'Photo')
        
        location_info = f"located in {location}" if location else "general location"
        
        task_description = f"""
        Optimize the following Instagram content for maximum SEO and discoverability.
        
        Business Type: {business_type} {location_info}
        Campaign Goals: {campaign_goals}
        Post Type: {post_type}
        
        Original Content:
        - Caption: {caption}
        - Hashtags: {', '.join(hashtags) if hashtags else 'None'}
        
        Your task is to:
        1. Optimize the caption by naturally incorporating relevant keywords without making it feel forced
        2. Create a strategic hashtag mix:
           - 3-5 high-competition hashtags (popular, trending)
           - 5-7 medium-competition hashtags (niche but active)
           - 3-5 low-competition hashtags (specific, less competitive)
           - Total: 15-20 hashtags maximum
        3. Identify 5-8 primary keywords that should be emphasized
        4. Suggest alt text for the image (important for accessibility and SEO)
        5. If location is provided, suggest location-based tags
        6. Calculate an SEO score (0-100) based on:
           - Keyword optimization
           - Hashtag strategy
           - Content structure
           - Discoverability potential
        
        Requirements:
        - Keep the caption natural and engaging (don't keyword stuff)
        - Ensure hashtags are relevant and not banned
        - Balance trending hashtags with niche ones
        - Optimize for Instagram's search algorithm
        - Consider local SEO if location is provided
        
        Return a JSON object matching this schema exactly:
        {{
            "optimized_caption": "SEO-optimized version of the caption with natural keyword placement",
            "optimized_hashtags": ["#hashtag1", "#hashtag2", ...],
            "keyword_suggestions": ["keyword1", "keyword2", ...],
            "seo_score": 85,
            "improvements": [
                "Added location-based keywords",
                "Optimized hashtag mix for better reach",
                "Improved keyword density in caption"
            ],
            "alt_text_suggestion": "Descriptive alt text for the image",
            "location_tags": ["#location1", "#location2"] or []
        }}
        """
        
        return Task(
            description=task_description,
            agent=agent,
            expected_output="""A JSON object containing:
            - optimized_caption: SEO-optimized caption string
            - optimized_hashtags: array of optimized hashtags
            - keyword_suggestions: array of primary keywords
            - seo_score: integer (0-100)
            - improvements: array of improvement descriptions
            - alt_text_suggestion: string or null
            - location_tags: array of location-based tags"""
        )


def parse_seo_output(raw_output: str) -> SEOOutput:
    """
    Parse the agent's output into structured format
    
    Args:
        raw_output: Raw text output from the agent
        
    Returns:
        Parsed SEOOutput object
    """
    try:
        # Try to extract JSON from the output
        start_idx = raw_output.find('{')
        end_idx = raw_output.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = raw_output[start_idx:end_idx]
            data = json.loads(json_str)
            return SEOOutput(**data)
        else:
            # Fallback: create a default output
            return SEOOutput(
                optimized_caption="SEO optimization failed - using original content",
                optimized_hashtags=[],
                keyword_suggestions=[],
                seo_score=0,
                improvements=["SEO parsing failed"],
                alt_text_suggestion=None,
                location_tags=[]
            )
    except Exception as e:
        print(f"Error parsing SEO output: {e}")
        raise


def run_seo_agent(
    business_type: str,
    location: Optional[str],
    content_data: Dict,
    campaign_goals: str,
    api_key: Optional[str] = None
) -> SEOOutput:
    """
    Run the SEO Agent to optimize content
    
    Args:
        business_type: Type of business
        location: Business location (optional)
        content_data: Output from Content Generation Agent (dict with caption, hashtags, etc.)
        campaign_goals: Campaign objectives
        api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        
    Returns:
        SEOOutput with optimized content
    """
    # Initialize LLM
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.5  # Lower temperature for more consistent SEO optimization
    )
    
    # Create agent and task
    agent = SEOAgentConfig.create_agent(llm)
    task = SEOAgentConfig.create_task(
        agent=agent,
        business_type=business_type,
        location=location,
        content_data=content_data,
        campaign_goals=campaign_goals
    )
    
    # Create crew and execute
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True
    )
    
    result = crew.kickoff()
    
    # Parse and return structured output
    return parse_seo_output(str(result))


if __name__ == "__main__":
    # Test the agent
    test_content = {
        "caption": "Check out our new donuts! 🍩",
        "hashtags": ["#donuts", "#food", "#yum"],
        "post_type": "Photo"
    }
    
    result = run_seo_agent(
        business_type="donut shop",
        location="Los Angeles, CA",
        content_data=test_content,
        campaign_goals="Increase local foot traffic"
    )
    
    print("\n=== SEO Agent Output ===")
    print(json.dumps(result.dict(), indent=2))

