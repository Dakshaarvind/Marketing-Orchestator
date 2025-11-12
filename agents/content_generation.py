"""
Content Generation Agent: Produces Instagram-ready content using analysis insights
"""
from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import json
import os
import logging

logger = logging.getLogger(__name__)


class ContentOutput(BaseModel):
    caption: str = Field(description="Primary Instagram caption text")
    hashtags: List[str] = Field(description="List of relevant hashtags")
    post_type: str = Field(description="Recommended post type: Reel | Story | Carousel | Photo")
    call_to_action: str = Field(description="Clear CTA for users")
    suggested_post_time: Optional[str] = Field(default=None, description="Suggested time to post (HH:MM)")
    media_prompts: List[str] = Field(default_factory=list, description="Prompts/ideas for images or short videos")
    image_prompt: Optional[str] = Field(default=None, description="Detailed prompt for DALL-E image generation")
    image_url: Optional[str] = Field(default=None, description="URL of generated image from DALL-E")
    notes: Optional[str] = Field(default=None, description="Additional implementation notes for the marketer")


class ContentAgentConfig:
    """Configuration and creation of the Content Generation Agent"""

    @staticmethod
    def create_agent(llm: ChatOpenAI) -> Agent:
        return Agent(
            role="Instagram Content Strategist",
            goal=(
                "Generate high-performing, platform-native Instagram content that aligns with "
                "the provided audience insights and campaign goals."
            ),
            backstory=(
                "You are a seasoned social media strategist for food & beverage SMBs. "
                "You create concise, scroll-stopping Instagram content (captions, hashtags, "
                "post type) that converts. You follow Instagram best practices, stay within "
                "platform norms, and write in the specified tone."
            ),
            verbose=True,
            allow_delegation=False,
            llm=llm,
        )

    @staticmethod
    def create_task(
        agent: Agent,
        business_type: str,
        campaign_goals: str,
        analysis: Dict,
    ) -> Task:
        """Create the generation task informed by analysis and competitor data"""
        """Create the generation task informed by analysis"""
        target_audience = analysis.get("target_audience", "local audience")
        engagement_times = analysis.get("engagement_times", [])
        content_tone = analysis.get("content_tone", "friendly")
        competitor_themes = analysis.get("competitor_themes", [])
        competitor_hashtags = analysis.get("competitor_hashtags", [])
        market_position = analysis.get("market_positioning", "")
        price_point = analysis.get("suggested_price_point", "")

        task_description = f"""
        Using the insights below, generate a single Instagram-ready post.

        Business Type: {business_type}
        Campaign Goal: {campaign_goals}

        Audience Insight: {target_audience}
        Engagement Times: {', '.join(engagement_times) if engagement_times else 'not specified'}
        Recommended Tone: {content_tone}

        Market Context:
        - Competitor Themes: {', '.join(competitor_themes) if competitor_themes else 'Not available'}
        - Market Position: {market_position}
        - Price Point: {price_point}

        Requirements:
        - Produce a concise, engaging caption matching the tone
        - Include a clear call-to-action aligned with the goal
        - Recommend the best post type (Reel | Story | Carousel | Photo) for this content
        - Provide 10-15 relevant, non-spammy hashtags (no banned hashtags)
          Consider these competitor hashtags: {', '.join(competitor_hashtags) if competitor_hashtags else 'Not available'}
        - Suggest 2-4 media prompts (image or short reel ideas)
        - Create a detailed image_prompt for DALL-E image generation (describe the visual: colors, composition, mood, key elements)
          Example: "A beautifully styled latte with latte art next to a plate of fresh chocolate chip cookies on a wooden table, warm natural lighting, cozy cafe atmosphere, Instagram-worthy food photography style"
        - If engagement times are provided, pick one as suggested_post_time
        - Avoid ALL caps and excessive emojis; use at most 1-2 where appropriate
        - Position content uniquely against competitors while staying authentic

        Return a JSON object matching this schema exactly:
        {{
          "caption": "string",
          "hashtags": ["#tag1", "#tag2", ...],
          "post_type": "Reel|Story|Carousel|Photo",
          "call_to_action": "string",
          "suggested_post_time": "HH:MM" | null,
          "media_prompts": ["prompt1", "prompt2"],
          "image_prompt": "detailed description for DALL-E image generation",
          "notes": "optional string"
        }}
        """

        return Task(
            description=task_description,
            agent=agent,
            expected_output=(
                "A JSON object containing: caption, hashtags[], post_type, call_to_action, "
                "suggested_post_time, media_prompts[], image_prompt (detailed description for DALL-E), notes"
            ),
        )


def generate_instagram_image(image_prompt: str, business_type: str, api_key: Optional[str] = None) -> Optional[str]:
    """
    Generate an Instagram-ready image using DALL-E 3
    
    Args:
        image_prompt: Detailed prompt for image generation
        business_type: Type of business (for prompt enhancement)
        api_key: OpenAI API key (optional, uses env var if not provided)
        
    Returns:
        URL of the generated image, or None if generation fails
    """
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        
        # Enhance prompt for Instagram-style images
        enhanced_prompt = f"{image_prompt}, professional food photography, Instagram-worthy, high quality, vibrant colors, appealing composition"
        
        logger.info(f"Generating image with DALL-E: {enhanced_prompt[:100]}...")
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size="1024x1024",  # Square format for Instagram
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        logger.info(f"✓ Image generated successfully: {image_url}")
        return image_url
        
    except Exception as e:
        logger.error(f"Failed to generate image: {e}")
        return None


def parse_content_output(raw_output: str) -> ContentOutput:
    """Extract JSON block from LLM output and validate."""
    start_idx = raw_output.find("{")
    end_idx = raw_output.rfind("}") + 1
    if start_idx != -1 and end_idx > start_idx:
        data = json.loads(raw_output[start_idx:end_idx])
        return ContentOutput(**data)
    # Minimal safe fallback
    return ContentOutput(
        caption="Try our latest offer today!",
        hashtags=["#local", "#food", "#instagood"],
        post_type="Photo",
        call_to_action="Visit us today and mention this post.",
        suggested_post_time=None,
        media_prompts=["Close-up of product", "Customer enjoying the item"],
        image_prompt=None,
        image_url=None,
        notes="Fallback content used due to parsing issue.",
    )


def run_content_agent(
    business_type: str,
    campaign_goals: str,
    analysis_data: Dict,
    competitor_data: Optional[Dict] = None,
    api_key: Optional[str] = None,
) -> ContentOutput:
    """Run content generation using the same OpenAI key as analysis."""
    import os
    from crewai import Crew

    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    agent = ContentAgentConfig.create_agent(llm)
    # Merge analysis and competitor data for richer insights
    combined_data = {**analysis_data}
    if competitor_data:
        # Add competitor insights to analysis data
        combined_data.update({
            "competitor_themes": competitor_data.get("trending_themes", []),
            "competitor_hashtags": competitor_data.get("recommended_hashtags", []),
            "market_positioning": competitor_data.get("market_positioning", ""),
            "suggested_price_point": competitor_data.get("suggested_price_point", "")
        })
    
    task = ContentAgentConfig.create_task(
        agent=agent,
        business_type=business_type,
        campaign_goals=campaign_goals,
        analysis=combined_data,
    )

    crew = Crew(agents=[agent], tasks=[task], verbose=True)
    result = crew.kickoff()
    content_output = parse_content_output(str(result))
    
    # Generate image if image_prompt is available
    if content_output.image_prompt:
        logger.info("Generating Instagram image with DALL-E...")
        image_url = generate_instagram_image(
            image_prompt=content_output.image_prompt,
            business_type=business_type,
            api_key=api_key
        )
        if image_url:
            content_output.image_url = image_url
            logger.info("✓ Image generated and added to content output")
        else:
            logger.warning("⚠ Image generation failed, continuing without image")
    else:
        # Fallback: try to generate from first media_prompt if available
        if content_output.media_prompts and len(content_output.media_prompts) > 0:
            logger.info("No image_prompt provided, generating from first media_prompt...")
            image_url = generate_instagram_image(
                image_prompt=content_output.media_prompts[0],
                business_type=business_type,
                api_key=api_key
            )
            if image_url:
                content_output.image_url = image_url
                content_output.image_prompt = content_output.media_prompts[0]
                logger.info("✓ Image generated from media_prompt")
    
    return content_output


if __name__ == "__main__":
    # Quick manual test
    demo_analysis = {
        "target_audience": "Young professionals 22-34 in downtown area",
        "engagement_times": ["11:00", "14:00", "19:00"],
        "content_tone": "playful",
    }
    out = run_content_agent(
        business_type="donut shop",
        campaign_goals="Promote BOGO donut offer",
        analysis_data=demo_analysis,
    )
    print(json.dumps(out.dict(), indent=2))


