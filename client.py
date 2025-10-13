
"""
Simple client that actually works for sending campaign requests
"""
from uagents import Agent, Context, Model
from pydantic import Field
from typing import Optional, Dict, Any
import sys

# Message models
class CampaignRequest(Model):
    business_type: str
    location: Optional[str] = None
    campaign_goals: str
    auto_publish: bool = False
    user_id: str

class CampaignResponse(Model):
    request_id: str
    status: str
    analysis_data: Optional[Dict[str, Any]] = None
    competitor_data: Optional[Dict[str, Any]] = None
    content_plan: Optional[Dict[str, Any]] = None
    schedule_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    timestamp: str

# Get orchestrator address from command line
if len(sys.argv) < 2:
    print("Usage: python simple_client.py <orchestrator_address>")
    print("\nExample:")
    print("  python simple_client.py agent1qds7nkx95cnjg9v8v9sh8f28hjctv5pn4h9wjpc9acruvfq6zpmu5tj35kz")
    sys.exit(1)

ORCHESTRATOR_ADDRESS = sys.argv[1]

# Create client agent
client = Agent(
    name="client",
    seed="client_seed_simple_123",
    port=8001,
    endpoint=["http://localhost:8001/submit"]
)

print(f"Client Agent Address: {client.address}")
print(f"Orchestrator Address: {ORCHESTRATOR_ADDRESS}")
print("="*60)

# Track if we've sent the request
request_sent = False

@client.on_event("startup")
async def startup(ctx: Context):
    """Send request on startup"""
    global request_sent
    
    print("\n Client started!")
    print(" Sending campaign request...\n")
    
    request = CampaignRequest(
        business_type="donut shop",
        location="Los Angeles, CA",
        campaign_goals="Increase local foot traffic and build Instagram following among young professionals",
        auto_publish=False,
        user_id="test_user_001"
    )
    
    await ctx.send(ORCHESTRATOR_ADDRESS, request)
    request_sent = True
    print("✓ Request sent! Waiting for response...\n")

@client.on_message(model=CampaignResponse)
async def handle_response(ctx: Context, sender: str, msg: CampaignResponse):
    """Handle response from orchestrator"""
    print("\n" + "="*60)
    print(" RESPONSE RECEIVED!")
    print("="*60)
    print(f"Request ID: {msg.request_id}")
    print(f"Status: {msg.status}")
    print(f"Timestamp: {msg.timestamp}\n")
    
    if msg.status == "success":
        if msg.analysis_data:
            print(" ANALYSIS DATA:")
            print("-"*60)
            print(f"Target Audience: {msg.analysis_data.get('target_audience', 'N/A')}")
            print(f"Engagement Times: {', '.join(msg.analysis_data.get('engagement_times', []))}")
            print(f"Content Tone: {msg.analysis_data.get('content_tone', 'N/A')}")
            print(f"Post Frequency: {msg.analysis_data.get('recommended_post_frequency', 'N/A')}/week")
            
            if 'platform_insights' in msg.analysis_data:
                print(f"\nPlatform Insights:")
                for key, value in msg.analysis_data['platform_insights'].items():
                    print(f"  - {key}: {value}")
        
        if msg.competitor_data and msg.competitor_data.get('status') != 'pending':
            print("\n COMPETITOR DATA:")
            print("-"*60)
            print(msg.competitor_data)
        
        if msg.content_plan and msg.content_plan.get('status') != 'pending':
            print("\n CONTENT PLAN:")
            print("-"*60)
            print(msg.content_plan)
    
    elif msg.status == "error":
        print(f" ERROR: {msg.error_message}")
    
    print("\n" + "="*60)
    print("✓ Test complete! Press Ctrl+C to exit.")
    print("="*60 + "\n")

@client.on_interval(period=30.0)
async def check_status(ctx: Context):
    """Periodic check"""
    if request_sent:
        ctx.logger.info("Still waiting for response...")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SIMPLE CLIENT - Campaign Request Test")
    print("="*60)
    print("\nThis will:")
    print("  1. Send a donut shop campaign request")
    print("  2. Wait for the orchestrator's response")
    print("  3. Display the analysis results")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")
    
    try:
        client.run()
    except KeyboardInterrupt:
        print("\n\n Client stopped")