# agents/orchestrator_flask.py
"""
Flask-based Orchestrator Agent for Marketing Campaign System
Uses Fetch.ai SDK pattern with webhooks for Agentverse integration
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from uagents.crypto import Identity
from fetchai import fetch
from fetchai.registration import register_with_agentverse
from fetchai.communication import parse_message_from_agent, send_message_to_agent
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, UTC
import json

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

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global variables
orchestrator_identity = None
active_requests = {}

def format_response_for_ui(final_post: dict, analysis_data: dict, content_data: dict, seo_data: dict) -> str:
    """
    Format the final Instagram post and all agent outputs into a readable markdown response
    for Agentverse UI
    
    Args:
        final_post: Consolidated Instagram post
        analysis_data: Analysis agent output
        content_data: Content generation output
        seo_data: SEO optimization output
        
    Returns:
        Formatted markdown string
    """
    markdown = "# 🎯 Instagram Post Ready!\n\n"
    
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
    
    # SEO Info
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
    
    # Audience Insights
    if final_post.get('target_audience'):
        markdown += "## 👥 Audience Insights\n\n"
        markdown += f"**Target Audience:** {final_post.get('target_audience')}\n"
        markdown += f"**Content Tone:** {final_post.get('content_tone')}\n"
        markdown += f"**Recommended Frequency:** {final_post.get('post_frequency')} posts/week\n"
        if final_post.get('engagement_times'):
            markdown += f"**Best Posting Times:** {', '.join(final_post.get('engagement_times', []))}\n"
        markdown += "\n"
    
    # SEO Improvements
    if final_post.get('seo_improvements'):
        markdown += "## ✨ SEO Optimizations\n\n"
        for improvement in final_post.get('seo_improvements', []):
            markdown += f"- {improvement}\n"
        markdown += "\n"
    
    markdown += "---\n\n"
    markdown += "✅ *Your Instagram post is ready to use! Copy the caption and hashtags above.*\n"
    
    return markdown

def create_final_instagram_post(analysis_data: dict, content_data: dict, seo_data: dict) -> dict:
    """
    Consolidate all agent outputs into a final Instagram-ready post format
    
    Args:
        analysis_data: Output from Analysis Agent
        content_data: Output from Content Generation Agent
        seo_data: Output from SEO Agent
        
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
        # Core Instagram post content
        "caption": final_caption,
        "hashtags": all_hashtags,
        "hashtag_string": ' '.join(all_hashtags),  # For easy copy-paste
        "post_type": content_data.get('post_type', 'Photo'),
        "call_to_action": content_data.get('call_to_action', ''),
        
        # Posting details
        "suggested_post_time": content_data.get('suggested_post_time'),
        "engagement_times": analysis_data.get('engagement_times', []) if isinstance(analysis_data, dict) else [],
        
        # Media/Image information
        "media_prompts": content_data.get('media_prompts', []),  # Ideas for images/videos
        "image_prompt": content_data.get('image_prompt') or (seo_data.get('alt_text_suggestion') if isinstance(seo_data, dict) else None),  # Image generation prompt
        "alt_text": seo_data.get('alt_text_suggestion') if isinstance(seo_data, dict) else None,  # For accessibility
        "image_url": content_data.get('image_url'),  # Generated image URL if available
        
        # SEO & Optimization
        "keywords": seo_data.get('keyword_suggestions', []) if isinstance(seo_data, dict) else [],
        "seo_score": seo_data.get('seo_score', 0) if isinstance(seo_data, dict) else 0,
        "seo_improvements": seo_data.get('improvements', []) if isinstance(seo_data, dict) else [],
        
        # Audience insights (for reference)
        "target_audience": analysis_data.get('target_audience', '') if isinstance(analysis_data, dict) else '',
        "content_tone": analysis_data.get('content_tone', '') if isinstance(analysis_data, dict) else '',
        "post_frequency": analysis_data.get('recommended_post_frequency', 0) if isinstance(analysis_data, dict) else 0,
        
        # Additional notes
        "notes": content_data.get('notes', ''),
    }
    
    return final_post

def init_orchestrator():
    """Initialize and register the orchestrator agent with Agentverse"""
    global orchestrator_identity
    
    try:
        # Create agent identity from seed
        agent_seed = os.getenv("AGENT_SECRET_KEY_1")
        if not agent_seed:
            raise ValueError("AGENT_SECRET_KEY_1 not found in .env file")
        
        orchestrator_identity = Identity.from_seed(agent_seed, 0)
        logger.info(f"Orchestrator agent address: {orchestrator_identity.address}")
        
        # Agent README for Agentverse
        readme = """
![domain:marketing](https://img.shields.io/badge/marketing-orchestrator-blue)

<description>
AI-powered Marketing Orchestrator for food industry Instagram campaigns.
Just describe your business and goals in plain English - I'll handle the rest!
</description>

<use_cases>
<use_case>Analyze target audience and optimal posting times</use_case>
<use_case>Research competitor strategies and trending content</use_case>
<use_case>Generate Instagram-ready posts with captions and hashtags</use_case>
<use_case>Schedule posts at optimal engagement times</use_case>
</use_cases>

<examples>
<example>I have a donut shop in Los Angeles and want to increase local foot traffic</example>
<example>Help me market my bakery in SF. I need more corporate catering clients.</example>
<example>I run a coffee shop and want to grow my Instagram following</example>
<example>My restaurant in Brooklyn needs better social media presence</example>
</examples>

<payload_requirements>
<description>Send your message in natural language OR as structured JSON</description>

<natural_language>
Just type naturally! Example:
"I have a donut shop in Los Angeles and want to increase foot traffic"
</natural_language>

<structured_json>
Or send JSON with these fields:
</structured_json>

<payload>
<requirement>
<parameter>business_type</parameter>
<description>Type of food business (e.g., "donut shop", "bakery")</description>
</requirement>
<requirement>
<parameter>location</parameter>
<description>Business location (optional)</description>
</requirement>
<requirement>
<parameter>campaign_goals</parameter>
<description>What you want to achieve</description>
</requirement>
</payload>
</payload_requirements>
"""
        
        # Register with Agentverse
        webhook_url = os.getenv("WEBHOOK_URL", "http://localhost:5000/api/webhook")
        agentverse_token = os.getenv("AGENTVERSE_API_KEY")
        
        if not agentverse_token:
            raise ValueError("AGENTVERSE_API_KEY not found in .env file")
        
        register_with_agentverse(
            identity=orchestrator_identity,
            url=webhook_url,
            agentverse_token=agentverse_token,
            agent_title="Marketing Orchestrator",
            readme=readme
        )
        
        logger.info("✓ Orchestrator registration complete!")
        logger.info(f"✓ Webhook URL: {webhook_url}")
        logger.info(f"✓ Agent visible at: https://agentverse.ai/agents/local")
        
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise

@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Handle incoming campaign requests from Agentverse or other agents"""
    try:
        # Parse incoming message
        data = request.get_data().decode("utf-8")
        logger.info("=" * 60)
        logger.info(" NEW CAMPAIGN REQUEST RECEIVED")
        logger.info("=" * 60)
        
        message = parse_message_from_agent(data)
        sender_address = message.sender
        original_payload = message.payload  # Keep original for metadata extraction
        payload = message.payload
        
        logger.info(f"From: {sender_address}")
        logger.info(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Handle Agentverse UI format (content array with text field)
        raw_user_input = None
        if isinstance(payload, dict) and 'content' in payload:
            content = payload.get('content', [])
            if content and len(content) > 0:
                # Find the text content item (not start-session or metadata)
                text_data = None
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text_data = item.get('text', '')
                        break
                
                if text_data:
                    raw_user_input = text_data
                    logger.info(f"Raw user input: {text_data}")
                    
                    # Try to parse as JSON first
                    try:
                        payload = json.loads(text_data)
                        logger.info(f"Parsed as JSON: {json.dumps(payload, indent=2)}")
                    except json.JSONDecodeError:
                        # Not JSON - treat as natural language
                        logger.info("Input is natural language, parsing...")
                        try:
                            from nl_parser import parse_user_input
                            payload = parse_user_input(text_data)
                            logger.info(f"Parsed from natural language: {json.dumps(payload, indent=2)}")
                        except Exception as e:
                            logger.error(f"Failed to parse natural language: {e}")
                            return jsonify({"error": "Could not understand input"}), 400
                else:
                    logger.warning("No text content found in message")
                    return jsonify({"error": "No text content in message"}), 400
        
        # Extract campaign parameters
        business_type = payload.get('business_type')
        location = payload.get('location')
        campaign_goals = payload.get('campaign_goals')
        auto_publish = payload.get('auto_publish', False)
        user_id = payload.get('user_id', 'anonymous')
        
        # Validate required fields
        if not business_type or not campaign_goals:
            error_msg = "Missing required fields: business_type and campaign_goals"
            logger.error(error_msg)
            response_payload = {
                "status": "error",
                "error_message": error_msg
            }
            send_message_to_agent(orchestrator_identity, sender_address, response_payload)
            return jsonify({"status": "error", "message": error_msg}), 400
        
        # Generate request ID
        request_id = f"{user_id}_{int(datetime.now(UTC).timestamp())}"
        active_requests[request_id] = {
            "payload": payload,
            "sender": sender_address,
            "status": "processing",
            "created_at": datetime.now(UTC).isoformat()
        }
        
        # === STAGE 1: Run Analysis Agent ===
        logger.info(f"\n[{request_id}]  Running Analysis Agent...")
        
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
                location=location or "United States"  # Fallback if no location
            )
            
            logger.info(f"[{request_id}] ✓ Competitor research completed!")
            logger.info(f"   Found {len(competitor_result.competitors)} competitors")
            
            # Log some competitor names for verification
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
        logger.info(f"[{request_id}]  Content Generation - Starting")
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

        # === STAGE 4: SEO Optimization ===
        logger.info(f"[{request_id}]  SEO Optimization - Starting")
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
            seo_data = {
                "status": "error",
                "message": str(e),
            }

        # === STAGE 5: Create Final Instagram Post ===
        logger.info(f"[{request_id}]  Consolidating final Instagram post...")
        
        # Create consolidated final post
        final_post = create_final_instagram_post(analysis_data, content_data, seo_data)
        
        logger.info(f"[{request_id}] ✓ Final Instagram post ready!")
        logger.info(f"   Caption: {final_post['caption'][:80]}...")
        logger.info(f"   Hashtags: {len(final_post['hashtags'])} tags")
        logger.info(f"   Post Type: {final_post['post_type']}")
        logger.info(f"   Post Time: {final_post['suggested_post_time']}")
        logger.info(f"   SEO Score: {final_post['seo_score']}/100")

        # === STAGE 6: Scheduling (placeholder) ===
        logger.info(f"[{request_id}]  Scheduling - Coming soon")
        
        # Prepare response with both detailed data and final post
        response_payload = {
            "request_id": request_id,
            "status": "success",
            "timestamp": datetime.now(UTC).isoformat(),
            "instagram_post": final_post,  # Main consolidated post ready to use
            "analysis_data": analysis_data,
            "competitor_data": competitor_data,
            "content_plan": content_data,
            "seo_optimization": seo_data,
            "schedule_data": {
                "status": "pending",
                "message": "Scheduler Agent not yet implemented"
            }
        }
        
        # Update request status
        active_requests[request_id]["status"] = "completed"
        active_requests[request_id]["response"] = response_payload
        
        # Format response for Agentverse UI (markdown text)
        formatted_response_text = format_response_for_ui(final_post, analysis_data, content_data, seo_data)
        
        # Log the formatted response preview
        logger.info(f"\n[{request_id}] Formatted response preview (first 500 chars):")
        logger.info(formatted_response_text[:500] + "...")
        logger.info(f"[{request_id}] Total response length: {len(formatted_response_text)} characters")
        
        # Extract msg_id and session_id from incoming message if available
        incoming_msg_id = None
        session_id = None
        if isinstance(original_payload, dict):
            incoming_msg_id = original_payload.get('msg_id')
            # Check content array for session metadata
            if 'content' in original_payload:
                for item in original_payload.get('content', []):
                    if isinstance(item, dict) and item.get('type') == 'metadata':
                        metadata = item.get('metadata', {})
                        if 'x-session-id' in metadata:
                            session_id = metadata.get('x-session-id')
        
        # Send response back to sender in Agentverse format
        logger.info(f"\n[{request_id}] Sending response back to {sender_address}")
        
        try:
            # Format response as Agentverse expects: content array with text
            agentverse_response = {
                "content": [
                    {
                        "type": "text",
                        "text": formatted_response_text
                    }
                ]
            }
            
            # Include msg_id and session_id if available (for correlation)
            if incoming_msg_id:
                agentverse_response["msg_id"] = incoming_msg_id
            if session_id:
                agentverse_response["session"] = session_id
            agentverse_response["timestamp"] = datetime.now(UTC).isoformat()
            
            logger.info(f"[{request_id}] Sending formatted response to Agentverse UI...")
            logger.info(f"[{request_id}] Response structure: {json.dumps(agentverse_response, indent=2, ensure_ascii=False)[:500]}...")
            logger.info(f"[{request_id}] Response text length: {len(formatted_response_text)} chars")
            logger.info(f"[{request_id}] First 200 chars of text: {formatted_response_text[:200]}")
            
            # Send via send_message_to_agent (async messaging)
            send_message_to_agent(
                orchestrator_identity,
                sender_address,
                agentverse_response
            )
            logger.info(f"[{request_id}] ✓ Response sent successfully via send_message_to_agent!")
        except Exception as e:
            logger.error(f"[{request_id}] ✗ Failed to send response: {e}")
            import traceback
            traceback.print_exc()
            # Still return success to webhook caller even if response send fails
        
        logger.info("=" * 60)
        logger.info("✓ CAMPAIGN REQUEST PROCESSED")
        logger.info("=" * 60 + "\n")
        
        # Return response in HTTP body - Agentverse expects this format
        # Match the incoming message structure exactly
        http_response = {
            "content": [
                {
                    "type": "text",
                    "text": formatted_response_text
                }
            ]
        }
        
        # Include correlation IDs
        if incoming_msg_id:
            http_response["msg_id"] = incoming_msg_id
        if session_id:
            http_response["session"] = session_id
        http_response["timestamp"] = datetime.now(UTC).isoformat()
        
        logger.info(f"[{request_id}] Returning HTTP response with content...")
        logger.info(f"[{request_id}] HTTP Response structure: {json.dumps(http_response, indent=2, ensure_ascii=False)[:500]}...")
        logger.info(f"[{request_id}] Response text length: {len(formatted_response_text)} characters")
        logger.info(f"[{request_id}] First 300 chars of response: {formatted_response_text[:300]}...")
        
        # Set proper headers for Agentverse
        response = jsonify(http_response)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response
        
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/test', methods=['POST'])
def test_endpoint():
    """
    Simple test endpoint for local testing WITHOUT agent authentication
    Use this for debugging - accepts plain JSON
    """
    try:
        logger.info("=" * 60)
        logger.info(" TEST REQUEST RECEIVED (No auth)")
        logger.info("=" * 60)
        
        # Get JSON directly
        payload = request.get_json()
        
        if not payload:
            return jsonify({"error": "No JSON payload"}), 400
        
        logger.info(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Extract campaign parameters
        business_type = payload.get('business_type')
        location = payload.get('location')
        campaign_goals = payload.get('campaign_goals')
        user_id = payload.get('user_id', 'test_user')
        
        # Validate
        if not business_type or not campaign_goals:
            return jsonify({
                "status": "error",
                "message": "Missing business_type or campaign_goals"
            }), 400
        
        # Generate request ID
        request_id = f"{user_id}_{int(datetime.now(UTC).timestamp())}"
        
        # Run Analysis
        logger.info(f"[{request_id}]  Running Analysis Agent...")
        
        try:
            # Try importing from same directory
            import sys
            from pathlib import Path
            
            # Ensure agents directory is in path
            agents_dir = Path(__file__).parent
            if str(agents_dir) not in sys.path:
                sys.path.insert(0, str(agents_dir))
            
            from analysis_agent import run_analysis_agent
            
            analysis_result = run_analysis_agent(
                business_type=business_type,
                location=location,
                campaign_goals=campaign_goals
            )
            
            logger.info(f"[{request_id}] ✓ Analysis completed!")
            
            response = {
                "request_id": request_id,
                "status": "success",
                "timestamp": datetime.now(UTC).isoformat(),
                "analysis_data": analysis_result.dict()
            }
            
            logger.info("=" * 60)
            logger.info("✓ TEST REQUEST PROCESSED")
            logger.info("=" * 60 + "\n")
            
            return jsonify(response)
            
        except ImportError as e:
            logger.error(f"Import failed: {e}")
            logger.error(f"Current directory: {Path.cwd()}")
            logger.error(f"Script directory: {Path(__file__).parent}")
            logger.error(f"sys.path: {sys.path}")
            return jsonify({
                "status": "error",
                "message": f"Could not import analysis_agent: {str(e)}",
                "hint": "Make sure analysis_agent.py is in the agents/ directory"
            }), 500
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
    
    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "agent_address": orchestrator_identity.address if orchestrator_identity else None,
        "active_requests": len([r for r in active_requests.values() if r["status"] == "processing"]),
        "total_requests": len(active_requests)
    })

@app.route('/api/requests', methods=['GET'])
def get_requests():
    """Get all requests (for debugging)"""
    return jsonify({
        "requests": active_requests
    })

if __name__ == "__main__":
    logger.info("\n" + "=" * 60)
    logger.info("MARKETING ORCHESTRATOR - STARTING")
    logger.info("=" * 60)
    
    # Initialize and register agent
    init_orchestrator()
    
    logger.info("\n" + "=" * 60)
    logger.info(" ORCHESTRATOR READY")
    logger.info("=" * 60)
    logger.info(f"Agent Address: {orchestrator_identity.address}")
    logger.info("Webhook: http://localhost:5000/api/webhook")
    logger.info("Status: http://localhost:5000/api/status")
    logger.info("\nView in Agentverse: https://agentverse.ai/agents/local")
    logger.info("\nPress Ctrl+C to stop")
    logger.info("=" * 60 + "\n")
    
    # Start Flask server
    app.run(host="0.0.0.0", port=5000, debug=False)