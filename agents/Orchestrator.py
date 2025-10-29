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
from datetime import datetime
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
        payload = message.payload
        
        logger.info(f"From: {sender_address}")
        logger.info(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Handle Agentverse UI format (content array with text field)
        raw_user_input = None
        if isinstance(payload, dict) and 'content' in payload:
            content = payload.get('content', [])
            if content and len(content) > 0:
                # Get the text from first content item
                text_data = content[0].get('text', '{}')
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
        request_id = f"{user_id}_{int(datetime.utcnow().timestamp())}"
        active_requests[request_id] = {
            "payload": payload,
            "sender": sender_address,
            "status": "processing",
            "created_at": datetime.utcnow().isoformat()
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
        
        # === STAGE 2: Content Generation ===
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
            )
            content_data = content_result.dict()
            logger.info(f"[{request_id}] ✓ Content generated!")
        except Exception as e:
            logger.error(f"[{request_id}] ✗ Content generation failed: {e}")
            content_data = {
                "status": "error",
                "message": str(e),
            }

        # === STAGE 3-4: Future agents (placeholders) ===
        logger.info(f"[{request_id}]  Competitor Research - Coming soon")
        logger.info(f"[{request_id}]  Scheduling - Coming soon")
        
        # Prepare response
        response_payload = {
            "request_id": request_id,
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_data": analysis_data,
            "competitor_data": {
                "status": "pending",
                "message": "Competitor Research Agent not yet implemented"
            },
            "content_plan": content_data,
            "schedule_data": {
                "status": "pending",
                "message": "Scheduler Agent not yet implemented"
            }
        }
        
        # Update request status
        active_requests[request_id]["status"] = "completed"
        active_requests[request_id]["response"] = response_payload
        
        # Send response back to sender
        logger.info(f"\n[{request_id}] Sending response back to {sender_address}")
        
        try:
            send_message_to_agent(
                orchestrator_identity,
                sender_address,
                response_payload
            )
            logger.info(f"[{request_id}] ✓ Response sent successfully!")
        except Exception as e:
            logger.error(f"[{request_id}] ✗ Failed to send response: {e}")
            # Still return success to webhook caller even if response send fails
        
        logger.info("=" * 60)
        logger.info("✓ CAMPAIGN REQUEST PROCESSED")
        logger.info("=" * 60 + "\n")
        
        return jsonify({"status": "success", "request_id": request_id})
        
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
        request_id = f"{user_id}_{int(datetime.utcnow().timestamp())}"
        
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
                "timestamp": datetime.utcnow().isoformat(),
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