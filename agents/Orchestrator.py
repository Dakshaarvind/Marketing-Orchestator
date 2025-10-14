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
Multi-Agent Marketing Orchestrator for food industry Instagram campaigns.
Coordinates AI agents to analyze audiences, research competitors, generate content, and schedule posts.
</description>

<use_cases>
<use_case>Analyze target audience and optimal posting times for food businesses</use_case>
<use_case>Research competitor strategies and trending content</use_case>
<use_case>Generate Instagram-ready content with captions and hashtags</use_case>
<use_case>Schedule and auto-publish posts at optimal times</use_case>
</use_cases>

<payload_requirements>
<description>Send a campaign request with business details</description>
<payload>
<requirement>
<parameter>business_type</parameter>
<description>Type of food business (e.g., "donut shop", "bakery", "restaurant")</description>
</requirement>
<requirement>
<parameter>location</parameter>
<description>Business location (e.g., "Los Angeles, CA") - optional</description>
</requirement>
<requirement>
<parameter>campaign_goals</parameter>
<description>Marketing objectives (e.g., "Increase foot traffic and Instagram following")</description>
</requirement>
<requirement>
<parameter>auto_publish</parameter>
<description>Whether to auto-publish posts (true/false) - optional, defaults to false</description>
</requirement>
<requirement>
<parameter>user_id</parameter>
<description>Unique identifier for tracking - optional</description>
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
        
        # === STAGE 2-4: Future agents (placeholders) ===
        logger.info(f"[{request_id}]  Competitor Research - Coming soon")
        logger.info(f"[{request_id}]  Content Generation - Coming soon")
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
            "content_plan": {
                "status": "pending",
                "message": "Content Generation Agent not yet implemented"
            },
            "schedule_data": {
                "status": "pending",
                "message": "Scheduler Agent not yet implemented"
            }
        }
        
        # Update request status
        active_requests[request_id]["status"] = "completed"
        active_requests[request_id]["response"] = response_payload
        
        # Send response back to sender
        logger.info(f"\n[{request_id}]  Sending response back to {sender_address}")
        send_message_to_agent(
            orchestrator_identity,
            sender_address,
            response_payload
        )
        
        logger.info("=" * 60)
        logger.info("✓ CAMPAIGN REQUEST PROCESSED")
        logger.info("=" * 60 + "\n")
        
        return jsonify({"status": "success", "request_id": request_id})
        
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        import traceback
        traceback.print_exc()
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