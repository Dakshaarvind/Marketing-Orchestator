# agents/orchestrator.py
"""
Simplified Orchestrator Fetch Agent for LOCAL testing
No mailbox required - uses direct agent communication
"""
from uagents import Agent, Context, Protocol, Model
from typing import Optional, Dict, Any
from pydantic import Field
import json
from datetime import datetime
from loguru import logger
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Message Models
class CampaignRequest(Model):
    """Incoming request from user/frontend"""
    business_type: str
    location: Optional[str] = None
    campaign_goals: str
    auto_publish: bool = False
    user_id: str

class CampaignResponse(Model):
    """Response sent back to user/frontend"""
    request_id: str
    status: str
    analysis_data: Optional[Dict[str, Any]] = None
    competitor_data: Optional[Dict[str, Any]] = None
    content_plan: Optional[Dict[str, Any]] = None
    schedule_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

# Get seed from environment or generate one
seed = os.getenv("FETCH_AGENT_SEED")
if not seed:
    import secrets
    seed = secrets.token_hex(16)
    logger.warning(f"No FETCH_AGENT_SEED found. Generated temporary seed.")
    logger.info(f"Add this to your .env file:\nFETCH_AGENT_SEED={seed}")

# Create the orchestrator agent (NO MAILBOX for local testing)
orchestrator = Agent(
    name="marketing_orchestrator",
    seed=seed,
    port=8000,
    endpoint=["http://localhost:8000/submit"]
)

logger.info(f"Orchestrator Agent Address: {orchestrator.address}")
logger.info(f"Orchestrator Wallet Address: {orchestrator.wallet.address()}")

# State management
active_requests: Dict[str, Dict] = {}

@orchestrator.on_event("startup")
async def startup(ctx: Context):
    """Startup event handler"""
    logger.info("=" * 60)
    logger.success(" ORCHESTRATOR AGENT STARTED")
    logger.info("=" * 60)
    logger.info(f"Name: {ctx.name}")
    logger.info(f"Address: {ctx.agent.address}")
    logger.info(f"Port: 8000")
    logger.info(f"Endpoint: http://localhost:8000/submit")
    logger.info("=" * 60)
    logger.info("\n✓ Ready to receive campaign requests!")
    logger.info("\nTo send a request, use client.py:")
    logger.info(f"  python client.py {ctx.agent.address}\n")

@orchestrator.on_message(model=CampaignRequest)
async def handle_campaign_request(ctx: Context, sender: str, msg: CampaignRequest):
    """
    Main handler for incoming campaign requests
    """
    request_id = f"{msg.user_id}_{int(datetime.utcnow().timestamp())}"
    
    logger.info("\n" + "=" * 60)
    logger.info(" NEW CAMPAIGN REQUEST RECEIVED")
    logger.info("=" * 60)
    logger.info(f"Request ID: {request_id}")
    logger.info(f"From: {sender}")
    logger.info(f"Business: {msg.business_type}")
    logger.info(f"Location: {msg.location or 'Not specified'}")
    logger.info(f"Goals: {msg.campaign_goals}")
    logger.info("=" * 60)
    
    # Store request
    active_requests[request_id] = {
        "campaign": msg.dict(),
        "status": "processing",
        "created_at": datetime.utcnow().isoformat()
    }
    
    try:
        # === STAGE 1: Run Analysis Agent ===
        logger.info(f"\n[{request_id}]  Running Analysis Agent...")
        
        # Import and run analysis agent
        try:
            import sys
            from pathlib import Path
            
            # Add agents directory to path
            agents_dir = Path(__file__).parent
            if str(agents_dir) not in sys.path:
                sys.path.insert(0, str(agents_dir))
            
            from analysis_agent import run_analysis_agent
            
            # Run analysis in executor to avoid blocking
            import asyncio
            loop = asyncio.get_event_loop()
            analysis_result = await loop.run_in_executor(
                None,
                run_analysis_agent,
                msg.business_type,
                msg.location,
                msg.campaign_goals
            )
            
            logger.success(f"[{request_id}] ✓ Analysis completed!")
            logger.info(f"   Target Audience: {analysis_result.target_audience}")
            logger.info(f"   Engagement Times: {', '.join(analysis_result.engagement_times)}")
            logger.info(f"   Posting Frequency: {analysis_result.recommended_post_frequency}/week")
            
            analysis_data = analysis_result.dict()
            
        except ImportError as e:
            logger.error(f"[{request_id}] ✗ Could not import analysis_agent: {e}")
            analysis_data = {
                "error": "Analysis agent not available",
                "target_audience": "General food enthusiasts",
                "engagement_times": ["08:00", "12:00", "17:00"],
                "content_tone": "warm and inviting",
                "recommended_post_frequency": 5
            }
        except Exception as e:
            logger.error(f"[{request_id}] ✗ Analysis failed: {str(e)}")
            raise
        
        # === Future stages (placeholders) ===
        logger.info(f"\n[{request_id}] Competitor Research - Coming soon")
        logger.info(f"[{request_id}]  Content Generation - Coming soon")
        logger.info(f"[{request_id}]  Scheduling - Coming soon")
        
        # === Prepare Response ===
        response = CampaignResponse(
            request_id=request_id,
            status="success",
            analysis_data=analysis_data,
            competitor_data={"status": "pending", "message": "Competitor agent not yet implemented"},
            content_plan={"status": "pending", "message": "Content agent not yet implemented"},
            schedule_data={"status": "pending", "message": "Scheduler agent not yet implemented"}
        )
        
        # Update state
        active_requests[request_id]["status"] = "completed"
        active_requests[request_id]["completed_at"] = datetime.utcnow().isoformat()
        
        # Send response
        await ctx.send(sender, response)
        
        logger.info("\n" + "=" * 60)
        logger.success(f"✓ Response sent to {sender}")
        logger.info("=" * 60 + "\n")
        
    except Exception as e:
        logger.error(f"\n[{request_id}] ✗ Error: {str(e)}")
        
        error_response = CampaignResponse(
            request_id=request_id,
            status="error",
            error_message=str(e)
        )
        
        await ctx.send(sender, error_response)
        logger.error("Error response sent\n")

@orchestrator.on_interval(period=30.0)
async def status_update(ctx: Context):
    """Periodic status update"""
    active = len([r for r in active_requests.values() if r.get("status") == "processing"])
    total = len(active_requests)
    
    if total > 0:
        logger.info(f" Status: {active} active, {total} total requests")

if __name__ == "__main__":
    logger.info("\nStarting Orchestrator Agent...")
    logger.info("Press Ctrl+C to stop\n")
    
    try:
        orchestrator.run()
    except KeyboardInterrupt:
        logger.info("\n\n Orchestrator stopped")
    except Exception as e:
        logger.error(f"\n\n Error: {e}")
        import traceback
        traceback.print_exc()