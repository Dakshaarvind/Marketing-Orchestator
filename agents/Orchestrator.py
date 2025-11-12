"""
Marketing Orchestrator Agent - ASI1 Chat Protocol Compatible
Updated to display enhanced SEO agent business insights
"""
import os
import sys
import json
import logging
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
from typing import Any

from uagents import Agent, Context, Protocol
from dotenv import load_dotenv

# Import ASI1 chat protocol components
from uagents_core.contrib.protocols.chat import (
    chat_protocol_spec,
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    StartSessionContent,
    EndSessionContent,
)

# Add agents directory to path for imports
agents_dir = Path(__file__).parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create agent from seed
agent_seed = os.getenv("AGENT_SECRET_KEY_1")
if not agent_seed:
    raise ValueError("AGENT_SECRET_KEY_1 not found in .env file")

# Agent configuration
agent_port = int(os.getenv("AGENT_PORT", "8000"))
use_mailbox = os.getenv("USE_MAILBOX", "true").lower() == "true"
agent_endpoint = os.getenv("AGENT_ENDPOINT_URL")

agent_kwargs = {
    "name": "Marketing Orchestrator",
    "seed": agent_seed,
    "port": agent_port,
}

if use_mailbox:
    agent_kwargs["mailbox"] = True
    logger.info("Using Mailbox connection (mailbox=True) - no public endpoint needed")
elif agent_endpoint:
    agent_kwargs["endpoint"] = [f"{agent_endpoint}/submit"]
    logger.info(f"Using public endpoint: {agent_endpoint}")
else:
    logger.info("Running locally - will register with Agentverse")

agent = Agent(**agent_kwargs)

logger.info(f"Orchestrator agent address: {agent.address}")

# ============================================================================
# Helper Functions
# ============================================================================

def format_response_for_ui(final_post: dict, analysis_data: dict, content_data: dict, seo_data: dict) -> str:
    """
    Format the final Instagram post and all agent outputs into a readable markdown response
    for Agentverse UI - NOW WITH BUSINESS INSIGHTS!
    
    Args:
        final_post: Consolidated Instagram post
        analysis_data: Analysis agent output
        content_data: Content generation output
        seo_data: SEO optimization output (now includes business insights)
        
    Returns:
        Formatted markdown string
    """
    markdown = "# 🎯 Instagram Marketing Campaign Ready!\n\n"
    
    # === NEW: BUSINESS STRATEGY INSIGHTS ===
    if isinstance(seo_data, dict) and seo_data.get('business_strength'):
        markdown += "## 💡 Strategic Business Insights\n\n"
        
        markdown += f"**🎯 Business Strength:**\n{seo_data.get('business_strength', 'N/A')}\n\n"
        
        markdown += f"**📝 Content Tone:**\n{seo_data.get('content_tone', 'N/A')}\n\n"
        
        markdown += f"**👥 Target Audience:**\n{seo_data.get('target_audience', 'N/A')}\n\n"
        
        markdown += f"**🔍 Competitor Insight:**\n{seo_data.get('competitor_takeaway', 'N/A')}\n\n"
        
        markdown += "---\n\n"
    
    # Main Instagram Post
    markdown += "## 📸 Your Instagram Post\n\n"
    markdown += f"**Caption:**\n{final_post.get('caption', 'N/A')}\n\n"
    
    hashtags = final_post.get('hashtags', [])
    if hashtags and isinstance(hashtags, list):
        markdown += f"**Hashtags:**\n{' '.join(hashtags)}\n\n"
    else:
        markdown += "**Hashtags:** N/A\n\n"
    
    markdown += f"**Post Type:** {final_post.get('post_type', 'N/A')}\n"
    markdown += f"**Suggested Post Time:** {final_post.get('suggested_post_time', 'N/A')}\n"
    markdown += f"**Call to Action:** {final_post.get('call_to_action', 'N/A')}\n\n"
    
    # Image URL (if generated)
    if final_post.get('image_url'):
        markdown += f"**Generated Image:**\n![Instagram Post]({final_post.get('image_url')})\n\n"
    
    # SEO Score
    if final_post.get('seo_score', 0) > 0:
        markdown += f"**SEO Score:** {final_post.get('seo_score')}/100 ⭐\n\n"
    
    # Media Prompts
    if final_post.get('media_prompts'):
        markdown += "## 🎨 Media Ideas\n\n"
        for i, prompt in enumerate(final_post.get('media_prompts', []), 1):
            markdown += f"{i}. {prompt}\n"
        markdown += "\n"
    
    # Alt Text
    if final_post.get('alt_text'):
        markdown += f"**Alt Text:** {final_post.get('alt_text')}\n\n"
    
    # Audience Insights (from analysis agent)
    if final_post.get('post_frequency'):
        markdown += "## 📊 Posting Strategy\n\n"
        markdown += f"**Recommended Frequency:** {final_post.get('post_frequency')} posts/week\n"
        if final_post.get('engagement_times'):
            markdown += f"**Best Posting Times:** {', '.join(final_post.get('engagement_times', []))}\n"
        markdown += "\n"
    
    # SEO Improvements
    if final_post.get('seo_improvements'):
        markdown += "## ✨ SEO Optimizations Made\n\n"
        for improvement in final_post.get('seo_improvements', []):
            markdown += f"- {improvement}\n"
        markdown += "\n"
    
    # Keywords
    if final_post.get('keywords'):
        markdown += f"**Primary Keywords:** {', '.join(final_post.get('keywords', []))}\n\n"
    
    markdown += "---\n\n"
    markdown += "✅ *Your Instagram post is ready to use! Copy the caption and hashtags above.*\n"
    
    return markdown

def create_final_instagram_post(analysis_data: dict, content_data: dict, seo_data: dict) -> dict:
    """
    Consolidate all agent outputs into a final Instagram-ready post format
    NOW INCLUDES BUSINESS INSIGHTS from enhanced SEO agent
    
    Args:
        analysis_data: Output from Analysis Agent
        content_data: Output from Content Generation Agent
        seo_data: Output from SEO Agent (now with business insights)
        
    Returns:
        Dict with complete Instagram post ready to use
    """
    # Use SEO-optimized content if available, otherwise fall back to original
    final_caption = seo_data.get('optimized_caption') if isinstance(seo_data, dict) and seo_data.get('optimized_caption') else content_data.get('caption', '')
    final_hashtags = seo_data.get('optimized_hashtags') if isinstance(seo_data, dict) and seo_data.get('optimized_hashtags') else content_data.get('hashtags', [])
    
    # Combine location tags from SEO with main hashtags
    location_tags = seo_data.get('location_tags', []) if isinstance(seo_data, dict) else []
    all_hashtags = final_hashtags + location_tags
    
    # Build final post - everything needed for Instagram posting
    final_post = {
        # === NEW: Business Strategy Insights ===
        "business_strength": seo_data.get('business_strength', '') if isinstance(seo_data, dict) else '',
        "content_tone": seo_data.get('content_tone', '') if isinstance(seo_data, dict) else '',
        "target_audience": seo_data.get('target_audience', '') if isinstance(seo_data, dict) else '',
        "competitor_takeaway": seo_data.get('competitor_takeaway', '') if isinstance(seo_data, dict) else '',
        
        # Core Instagram post content
        "caption": final_caption,
        "hashtags": all_hashtags,
        "hashtag_string": ' '.join(all_hashtags),
        "post_type": content_data.get('post_type', 'Photo'),
        "call_to_action": content_data.get('call_to_action', ''),
        
        # Posting details
        "suggested_post_time": content_data.get('suggested_post_time'),
        "engagement_times": analysis_data.get('engagement_times', []) if isinstance(analysis_data, dict) else [],
        
        # Media/Image information
        "media_prompts": content_data.get('media_prompts', []),
        "image_prompt": content_data.get('image_prompt') or (seo_data.get('alt_text_suggestion') if isinstance(seo_data, dict) else None),
        "alt_text": seo_data.get('alt_text_suggestion') if isinstance(seo_data, dict) else None,
        "image_url": content_data.get('image_url'),
        
        # SEO & Optimization
        "keywords": seo_data.get('keyword_suggestions', []) if isinstance(seo_data, dict) else [],
        "seo_score": seo_data.get('seo_score', 0) if isinstance(seo_data, dict) else 0,
        "seo_improvements": seo_data.get('improvements', []) if isinstance(seo_data, dict) else [],
        
        # Analysis insights (for reference)
        "post_frequency": analysis_data.get('recommended_post_frequency', 0) if isinstance(analysis_data, dict) else 0,
        
        # Additional notes
        "notes": content_data.get('notes', ''),
    }
    
    return final_post

async def process_campaign_request(
    ctx: Context,
    business_type: str,
    location: str,
    campaign_goals: str,
    request_id: str
) -> tuple[dict, dict, dict, dict]:
    """
    Process a campaign request through all agents (Analysis → Competitor → Content → SEO)
    
    Returns:
        Tuple of (analysis_data, competitor_data, content_data, seo_data)
    """
    # === STAGE 1: Run Analysis Agent ===
    logger.info(f"\n[{request_id}] 🔍 Running Analysis Agent...")
    
    try:
        from analysis_agent import run_analysis_agent
        
        analysis_result = run_analysis_agent(
            business_type=business_type,
            location=location,
            campaign_goals=campaign_goals
        )
        
        logger.info(f"[{request_id}] ✓ Analysis completed!")
        logger.info(f"   Target Audience: {analysis_result.target_audience}")
        logger.info(f"   Engagement Times: {', '.join(analysis_result.engagement_times)}")
        
        analysis_data = analysis_result.dict()
        
    except ImportError as e:
        logger.error(f"[{request_id}] ✗ Could not import analysis_agent: {e}")
        analysis_data = {
            "error": "Analysis agent not available",
            "message": "Please ensure analysis_agent.py is in the agents directory"
        }
    except Exception as e:
        logger.error(f"[{request_id}] ✗ Analysis failed: {str(e)}")
        analysis_data = {
            "error": str(e),
            "message": "Analysis execution failed"
        }
        
    # === STAGE 2: Run Competitor Research Agent ===
    logger.info(f"[{request_id}] 🔍 Running Competitor Research Agent...")
    
    try:
        from Competitor_Agent import run_competitor_agent
        
        competitor_result = run_competitor_agent(
            business_type=business_type,
            location=location or "United States"
        )
        
        logger.info(f"[{request_id}] ✓ Competitor research completed!")
        logger.info(f"   Found {len(competitor_result.competitors)} competitors")
        
        if competitor_result.competitors:
            competitor_names = [c.business_name for c in competitor_result.competitors[:3]]
            logger.info(f"   Top competitors: {', '.join(competitor_names)}")
        
        competitor_data = competitor_result.dict()
        
    except ImportError as e:
        logger.error(f"[{request_id}] ✗ Could not import competitor_agent: {e}")
        competitor_data = {
            "status": "error",
            "message": "Competitor agent not available",
            "competitors": []
        }
    except Exception as e:
        logger.error(f"[{request_id}] ✗ Competitor research failed: {e}")
        import traceback
        traceback.print_exc()
        competitor_data = {
            "status": "error",
            "message": str(e),
            "competitors": []
        }
    
    # === STAGE 3: Content Generation ===
    logger.info(f"[{request_id}] ✍️ Content Generation - Starting")
    content_data = {
        "status": "pending",
        "message": "Content Generation Agent not executed",
    }
    try:
        from content_generation import run_content_agent
        content_result = run_content_agent(
            business_type=business_type,
            campaign_goals=campaign_goals,
            analysis_data=analysis_data if isinstance(analysis_data, dict) else {},
            competitor_data=competitor_data if isinstance(competitor_data, dict) else {},
        )
        content_data = content_result.dict()
        logger.info(f"[{request_id}] ✓ Content generated!")
    except Exception as e:
        logger.error(f"[{request_id}] ✗ Content generation failed: {e}")
        content_data = {
            "status": "error",
            "message": str(e),
        }
    
    # === STAGE 4: SEO Optimization (NOW WITH BUSINESS INSIGHTS!) ===
    logger.info(f"[{request_id}] 🚀 SEO Optimization with Business Insights - Starting")
    seo_data = {
        "status": "pending",
        "message": "SEO Agent not executed",
    }
    try:
        from seo_agent import run_seo_agent
        # Only run SEO if content generation was successful
        if isinstance(content_data, dict) and "caption" in content_data:
            seo_result = run_seo_agent(
                business_type=business_type,
                location=location,
                content_data=content_data,
                campaign_goals=campaign_goals,
            )
            seo_data = seo_result.dict()
            logger.info(f"[{request_id}] ✓ SEO optimization completed!")
            logger.info(f"   SEO Score: {seo_result.seo_score}/100")
            logger.info(f"   Optimized Hashtags: {len(seo_result.optimized_hashtags)} tags")
            # === NEW: Log business insights ===
            logger.info(f"   Business Strength: {seo_result.business_strength[:50]}...")
            logger.info(f"   Content Tone: {seo_result.content_tone}")
            logger.info(f"   Target Audience: {seo_result.target_audience[:50]}...")
        else:
            logger.warning(f"[{request_id}] ⚠ Skipping SEO - content generation failed or incomplete")
            seo_data = {
                "status": "skipped",
                "message": "Content generation incomplete, cannot optimize",
            }
    except ImportError as e:
        logger.error(f"[{request_id}] ✗ Could not import seo_agent: {e}")
        seo_data = {
            "status": "error",
            "message": "seo_agent module not found",
        }
    except Exception as e:
        logger.error(f"[{request_id}] ✗ SEO optimization failed: {e}")
        import traceback
        traceback.print_exc()
        seo_data = {
            "status": "error",
            "message": str(e),
        }
    
    return analysis_data, competitor_data, content_data, seo_data

# ============================================================================
# ASI1 Chat Protocol Setup
# ============================================================================

# Create the chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)

@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """
    Handle incoming chat messages from ASI1 LLM or Agentverse UI
    """
    logger.info("=" * 60)
    logger.info(" NEW CAMPAIGN REQUEST RECEIVED")
    logger.info("=" * 60)
    logger.info(f"From: {sender}")
    logger.info(f"Message ID: {msg.msg_id}")
    
    # Store session sender for response
    ctx.storage.set(str(ctx.session), sender)
    
    # Send acknowledgement immediately
    await ctx.send(
        sender,
        ChatAcknowledgement(
            acknowledged_msg_id=msg.msg_id,
            timestamp=datetime.now(timezone.utc)
        ),
    )
    logger.info(f"✓ Sent acknowledgement for message {msg.msg_id}")
    
    # Process message content
    user_input = None
    for content in msg.content:
        if isinstance(content, StartSessionContent):
            logger.info(f"Got a start session message from {sender}")
            continue
        elif isinstance(content, TextContent):
            user_input = content.text
            logger.info(f"Got text message from {sender}: {user_input[:100]}...")
            break
        elif isinstance(content, EndSessionContent):
            logger.info(f"Got end session message from {sender}")
            continue
        else:
            logger.info(f"Got unexpected content type: {type(content)}")
    
    if not user_input:
        error_response = ChatMessage(
            content=[TextContent(text="Sorry, I couldn't understand your message. Please describe your business and campaign goals.")],
            msg_id=uuid4(),
            timestamp=datetime.now(timezone.utc)
        )
        await ctx.send(sender, error_response)
        return
    
    # Generate request ID
    request_id = f"req_{int(datetime.now(timezone.utc).timestamp())}"
    
    try:
        # Parse user input (natural language or JSON)
        try:
            # Try parsing as JSON first
            payload = json.loads(user_input)
            logger.info(f"[{request_id}] Parsed as JSON: {json.dumps(payload, indent=2)}")
        except json.JSONDecodeError:
            # Not JSON - treat as natural language
            logger.info(f"[{request_id}] Input is natural language, parsing...")
            try:
                from nl_parser import parse_user_input
                payload = parse_user_input(user_input)
                logger.info(f"[{request_id}] Parsed from natural language: {json.dumps(payload, indent=2)}")
            except Exception as e:
                logger.error(f"[{request_id}] Failed to parse natural language: {e}")
                error_response = ChatMessage(
                    content=[TextContent(text="Sorry, I couldn't understand your request. Please try describing your business and what you want to achieve.")],
                    msg_id=uuid4(),
                    timestamp=datetime.now(timezone.utc)
                )
                await ctx.send(sender, error_response)
                return
        
        # Extract campaign parameters
        business_type = payload.get('business_type')
        location = payload.get('location')
        campaign_goals = payload.get('campaign_goals')
        
        # Validate required fields
        if not business_type or not campaign_goals:
            error_msg = "Missing required fields: business_type and campaign_goals"
            logger.error(f"[{request_id}] {error_msg}")
            error_response = ChatMessage(
                content=[TextContent(text=f"Sorry, I need more information. {error_msg}")],
                msg_id=uuid4(),
                timestamp=datetime.now(timezone.utc)
            )
            await ctx.send(sender, error_response)
            return
        
        # Process campaign through all agents
        analysis_data, competitor_data, content_data, seo_data = await process_campaign_request(
            ctx, business_type, location, campaign_goals, request_id
        )
        
        # Create final Instagram post (now with business insights!)
        logger.info(f"[{request_id}] 📦 Consolidating final Instagram post with business insights...")
        final_post = create_final_instagram_post(analysis_data, content_data, seo_data)
        
        logger.info(f"[{request_id}] ✓ Final Instagram post ready!")
        logger.info(f"   Caption: {final_post['caption'][:80]}...")
        logger.info(f"   Hashtags: {len(final_post['hashtags'])} tags")
        logger.info(f"   Post Type: {final_post['post_type']}")
        logger.info(f"   SEO Score: {final_post['seo_score']}/100")
        logger.info(f"   Business Strength: {final_post.get('business_strength', 'N/A')[:50]}...")
        
        # Format response for UI (now includes business insights!)
        formatted_response_text = format_response_for_ui(final_post, analysis_data, content_data, seo_data)
        
        logger.info(f"[{request_id}] Formatted response length: {len(formatted_response_text)} characters")
        
        # Send response back to sender
        response = ChatMessage(
            content=[TextContent(text=formatted_response_text)],
            msg_id=uuid4(),
            timestamp=datetime.now(timezone.utc)
        )
        
        logger.info(f"[{request_id}] Sending response back to {sender}...")
        await ctx.send(sender, response)
        logger.info(f"[{request_id}] ✓ Response sent successfully!")
        
        logger.info("=" * 60)
        logger.info("✓ CAMPAIGN REQUEST PROCESSED")
        logger.info("=" * 60 + "\n")
    
    except Exception as e:
        logger.error(f"[{request_id}] Error processing request: {e}")
        import traceback
        traceback.print_exc()
        
        error_response = ChatMessage(
            content=[TextContent(text=f"Sorry, an error occurred while processing your request: {str(e)}")],
            msg_id=uuid4(),
            timestamp=datetime.now(timezone.utc)
        )
        await ctx.send(sender, error_response)

@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle acknowledgements from other agents"""
    logger.info(f"Got acknowledgement from {sender} for message {msg.acknowledged_msg_id}")

# Register the chat protocol
agent.include(chat_proto, publish_manifest=True)

# ============================================================================
# Agent Initialization
# ============================================================================

if __name__ == "__main__":
    logger.info("\n" + "=" * 60)
    logger.info("MARKETING ORCHESTRATOR - STARTING")
    logger.info("=" * 60)
    logger.info(f"Agent Address: {agent.address}")
    logger.info(f"Agent Name: {agent.name}")
    logger.info("\n" + "=" * 60)
    logger.info(" ORCHESTRATOR READY")
    logger.info("=" * 60)
    logger.info("\nView in Agentverse: https://agentverse.ai/agents/local")
    logger.info("\nPress Ctrl+C to stop")
    logger.info("=" * 60 + "\n")
    
    # Run the agent
    agent.run()