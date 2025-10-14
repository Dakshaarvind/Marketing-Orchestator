# agents/analysis_agent.py
"""
Analysis Agent: Identifies target audience, posting windows, and behavioral trends
"""
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List, Optional
import json

# Output schema for Analysis Agent
class AnalysisOutput(BaseModel):
    target_audience: str = Field(description="Description of the target audience demographics")
    engagement_times: List[str] = Field(description="Optimal posting times in HH:MM format")
    content_tone: str = Field(description="Recommended tone for content")
    recommended_post_frequency: int = Field(description="Number of posts per week")
    platform_insights: Optional[dict] = Field(default={}, description="Additional Instagram-specific insights")

class AnalysisAgentConfig:
    """Configuration and creation of the Analysis Agent"""
    
    @staticmethod
    def create_agent(llm: ChatOpenAI) -> Agent:
        """
        Creates the Analysis Agent with specific role and capabilities
        
        Args:
            llm: Language model instance
            
        Returns:
            Configured CrewAI Agent
        """
        return Agent(
            role="Social Media Audience Analyst",
            goal="Analyze target audience behavior and identify optimal posting strategies for food businesses on Instagram",
            backstory="""You are an expert social media analyst specializing in the food industry.
            You understand Instagram's algorithm, audience behavior patterns, and how food content performs.
            You analyze business types, locations, and goals to provide data-driven insights about:
            - Who the target audience is (age, interests, location)
            - When they are most active on Instagram
            - What content tone resonates with them
            - How frequently to post for maximum engagement
            
            You base your analysis on Instagram best practices, food industry trends, and local market dynamics.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    @staticmethod
    def create_task(agent: Agent, business_type: str, location: Optional[str], 
                   campaign_goals: str) -> Task:
        """
        Creates the analysis task with specific inputs
        
        Args:
            agent: The Analysis Agent
            business_type: Type of food business (e.g., "donut shop", "bakery")
            location: Optional location for local targeting
            campaign_goals: User's campaign objectives
            
        Returns:
            Configured CrewAI Task
        """
        location_info = f"located in {location}" if location else "with general regional appeal"
        
        task_description = f"""
        Analyze the target audience and engagement strategy for a {business_type} {location_info}.
        
        Campaign Goals: {campaign_goals}
        
        Provide a comprehensive analysis including:
        1. Target Audience: Define the primary demographic (age range, interests, lifestyle)
        2. Engagement Times: Identify 3-5 optimal posting times based on when food content performs best
        3. Content Tone: Recommend the tone and style (e.g., casual, professional, playful, inspiring)
        4. Post Frequency: Suggest how many posts per week for optimal engagement without oversaturation
        5. Platform Insights: Any Instagram-specific recommendations (Stories, Reels, carousel posts)
        
        Consider:
        - Instagram's algorithm favors consistent posting and high engagement
        - Food content performs well during meal times and evening browsing hours
        - Local businesses benefit from community-focused content
        - Visual appeal is critical for food industry success
        
        Format your response as a structured JSON that matches this schema:
        {{
            "target_audience": "description of audience",
            "engagement_times": ["HH:MM", "HH:MM", ...],
            "content_tone": "recommended tone",
            "recommended_post_frequency": number,
            "platform_insights": {{
                "story_frequency": "recommendation",
                "reel_priority": "high/medium/low",
                "carousel_usage": "recommendation"
            }}
        }}
        """
        
        return Task(
            description=task_description,
            agent=agent,
            expected_output="""A JSON object containing:
            - target_audience: string describing demographics
            - engagement_times: array of time strings in HH:MM format
            - content_tone: string describing recommended tone
            - recommended_post_frequency: integer (posts per week)
            - platform_insights: object with Instagram-specific recommendations"""
        )

# Utility function to parse agent output
def parse_analysis_output(raw_output: str) -> AnalysisOutput:
    """
    Parse the agent's output into structured format
    
    Args:
        raw_output: Raw text output from the agent
        
    Returns:
        Parsed AnalysisOutput object
    """
    try:
        # Try to extract JSON from the output
        start_idx = raw_output.find('{')
        end_idx = raw_output.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            json_str = raw_output[start_idx:end_idx]
            data = json.loads(json_str)
            return AnalysisOutput(**data)
        else:
            # Fallback: create a default output
            return AnalysisOutput(
                target_audience="General food enthusiasts",
                engagement_times=["08:00", "12:00", "17:00", "20:00"],
                content_tone="warm and inviting",
                recommended_post_frequency=5
            )
    except Exception as e:
        print(f"Error parsing analysis output: {e}")
        raise

# Example usage function
def run_analysis_agent(business_type: str, location: Optional[str] = None, 
                       campaign_goals: str = "Increase brand awareness and engagement",
                       api_key: Optional[str] = None) -> AnalysisOutput:
    """
    Run the Analysis Agent with given parameters
    
    Args:
        business_type: Type of food business
        location: Optional location
        campaign_goals: Campaign objectives
        api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        
    Returns:
        AnalysisOutput with recommendations
    """
    from crewai import Crew
    import os
    
    # Initialize LLM
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",  # Using gpt-4o-mini 
        temperature=0.7
    )
    
    # Create agent and task
    agent = AnalysisAgentConfig.create_agent(llm)
    task = AnalysisAgentConfig.create_task(agent, business_type, location, campaign_goals)
    
    # Create crew and execute
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True
    )
    
    result = crew.kickoff()
    
    # Parse and return structured output
    return parse_analysis_output(str(result))

if __name__ == "__main__":
    # Test the agent
    result = run_analysis_agent(
        business_type="donut shop",
        location="Los Angeles",
        campaign_goals="Increase local foot traffic and build Instagram following"
    )
    
    print("\n=== Analysis Agent Output ===")
    print(json.dumps(result.dict(), indent=2))