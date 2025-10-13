# client.py
"""
Simple client to send campaign requests to the Orchestrator Agent
"""
from uagents import Agent, Context, Model
from pydantic import Field
from typing import Optional, Dict, Any
import asyncio
from loguru import logger
import json

# Import message models (same as orchestrator)
class CampaignRequest(Model):
    """Request message to orchestrator"""
    business_type: str = Field(description="Type of food business")
    location: Optional[str] = Field(default=None, description="Business location")
    campaign_goals: str = Field(description="Campaign objectives")
    auto_publish: bool = Field(default=False, description="Whether to auto-publish posts")
    user_id: str = Field(description="Unique identifier for the requesting user")

class CampaignResponse(Model):
    """Response from orchestrator"""
    request_id: str
    status: str
    analysis_data: Optional[Dict[str, Any]] = None
    competitor_data: Optional[Dict[str, Any]] = None
    content_plan: Optional[Dict[str, Any]] = None
    schedule_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    timestamp: str

class MarketingClient:
    """Client for interacting with the Marketing Orchestrator"""
    
    def __init__(self, orchestrator_address: str, client_seed: str = "client_seed_123"):
        """
        Initialize the client
        
        Args:
            orchestrator_address: Address of the orchestrator agent
            client_seed: Seed phrase for client agent identity
        """
        self.orchestrator_address = orchestrator_address
        self.client = Agent(
            name="marketing_client",
            seed=client_seed,
            port=8001,
            endpoint=["http://localhost:8001/submit"]
        )
        
        self.responses = []
        self.pending_requests = {}
        
        # Setup response handler
        @self.client.on_message(model=CampaignResponse)
        async def handle_response(ctx: Context, sender: str, msg: CampaignResponse):
            logger.info(f"\n{'='*60}")
            logger.success(f"📨 RESPONSE RECEIVED")
            logger.info(f"{'='*60}")
            logger.info(f"Request ID: {msg.request_id}")
            logger.info(f"Status: {msg.status}")
            logger.info(f"Timestamp: {msg.timestamp}\n")
            
            if msg.status == "success":
                if msg.analysis_data:
                    logger.info("📊 ANALYSIS DATA:")
                    logger.info(json.dumps(msg.analysis_data, indent=2))
                
                if msg.competitor_data:
                    logger.info("\n🔍 COMPETITOR DATA:")
                    logger.info(json.dumps(msg.competitor_data, indent=2))
                
                if msg.content_plan:
                    logger.info("\n📝 CONTENT PLAN:")
                    logger.info(json.dumps(msg.content_plan, indent=2))
                
                if msg.schedule_data:
                    logger.info("\n📅 SCHEDULE DATA:")
                    logger.info(json.dumps(msg.schedule_data, indent=2))
            
            elif msg.status == "error":
                logger.error(f"\n❌ ERROR: {msg.error_message}")
            
            self.responses.append(msg)
            logger.info(f"\n{'='*60}\n")
        
        logger.info(f"Client initialized with address: {self.client.address}")
    
    async def send_campaign_request(
        self,
        business_type: str,
        location: str,
        campaign_goals: str,
        auto_publish: bool = False,
        user_id: str = "demo_user"
    ):
        """
        Send a campaign request to the orchestrator
        
        Args:
            business_type: Type of food business
            location: Business location
            campaign_goals: Campaign objectives
            auto_publish: Whether to auto-publish
            user_id: User identifier
        """
        request = CampaignRequest(
            business_type=business_type,
            location=location,
            campaign_goals=campaign_goals,
            auto_publish=auto_publish,
            user_id=user_id
        )
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📤 SENDING CAMPAIGN REQUEST")
        logger.info(f"{'='*60}")
        logger.info(f"Business Type: {business_type}")
        logger.info(f"Location: {location}")
        logger.info(f"Goals: {campaign_goals}")
        logger.info(f"Auto-Publish: {auto_publish}")
        logger.info(f"To: {self.orchestrator_address}")
        logger.info(f"{'='*60}\n")
        
        # Create context and send
        ctx = Context(
            agent_address=self.client.address,
            storage=self.client._storage
        )
        
        await ctx.send(self.orchestrator_address, request)
        logger.success("✓ Request sent successfully!")
        logger.info("⏳ Waiting for response...\n")
    
    def run(self):
        """Start the client agent"""
        self.client.run()

# Pre-defined campaign examples
CAMPAIGN_EXAMPLES = {
    "donut_shop": {
        "business_type": "donut shop",
        "location": "Los Angeles, CA",
        "campaign_goals": "Increase local foot traffic and build Instagram following among young professionals",
    },
    "bakery": {
        "business_type": "artisan bakery",
        "location": "San Francisco, CA",
        "campaign_goals": "Promote weekend catering services and expand corporate client base",
    },
    "coffee_shop": {
        "business_type": "specialty coffee shop",
        "location": "Brooklyn, NY",
        "campaign_goals": "Build community engagement and increase morning rush traffic",
    },
    "restaurant": {
        "business_type": "farm-to-table restaurant",
        "location": "Portland, OR",
        "campaign_goals": "Showcase seasonal menu items and attract food enthusiasts",
    },
    "food_truck": {
        "business_type": "taco food truck",
        "location": "Austin, TX",
        "campaign_goals": "Announce daily locations and build loyal follower base",
    }
}

async def interactive_mode(client: MarketingClient):
    """Interactive mode for sending requests"""
    print("\n" + "="*60)
    print("INTERACTIVE CAMPAIGN REQUEST MODE")
    print("="*60)
    print("\nAvailable examples:")
    for key, example in CAMPAIGN_EXAMPLES.items():
        print(f"  {key}: {example['business_type']} in {example['location']}")
    print("\nCommands:")
    print("  'example <name>' - Send a pre-defined example")
    print("  'custom' - Create a custom request")
    print("  'quit' - Exit")
    print("="*60 + "\n")
    
    while True:
        try:
            command = input("Enter command: ").strip().lower()
            
            if command == "quit":
                logger.info("Exiting...")
                break
            
            elif command.startswith("example "):
                example_name = command.split(" ", 1)[1]
                
                if example_name in CAMPAIGN_EXAMPLES:
                    example = CAMPAIGN_EXAMPLES[example_name]
                    await client.send_campaign_request(**example)
                    await asyncio.sleep(2)  # Wait for response
                else:
                    print(f"Unknown example: {example_name}")
            
            elif command == "custom":
                print("\nCreate custom campaign request:")
                business_type = input("Business type: ").strip()
                location = input("Location: ").strip()
                campaign_goals = input("Campaign goals: ").strip()
                
                if business_type and location and campaign_goals:
                    await client.send_campaign_request(
                        business_type=business_type,
                        location=location,
                        campaign_goals=campaign_goals
                    )
                    await asyncio.sleep(2)
                else:
                    print("All fields are required!")
            
            else:
                print("Unknown command. Try 'example <name>', 'custom', or 'quit'")
        
        except KeyboardInterrupt:
            logger.info("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")

async def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python client.py <orchestrator_address>")
        print("\nExample:")
        print("  python client.py agent1qw5jq3y9z8k...")
        print("\nTo get the orchestrator address:")
        print("  1. Run: python agents/orchestrator_agent.py")
        print("  2. Copy the agent address from the output")
        sys.exit(1)
    
    orchestrator_address = sys.argv[1]
    
    # Create client
    client = MarketingClient(orchestrator_address=orchestrator_address)
    
    # Check for quick test mode
    if len(sys.argv) > 2 and sys.argv[2] == "--quick-test":
        # Send a quick test request
        logger.info("Running quick test...")
        await client.send_campaign_request(
            business_type="donut shop",
            location="Los Angeles",
            campaign_goals="Increase brand awareness",
            user_id="quick_test_user"
        )
        
        # Wait for response
        await asyncio.sleep(10)
        
        if client.responses:
            logger.success("✓ Quick test completed!")
        else:
            logger.warning("⚠ No response received")
    else:
        # Interactive mode
        await interactive_mode(client)

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        format="<level>{message}</level>",
        colorize=True
    )
    
    asyncio.run(main())