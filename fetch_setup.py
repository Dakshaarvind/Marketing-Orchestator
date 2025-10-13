"""
Script to generate Fetch.ai agent credentials
Run this to get your FETCH_AGENT_SEED and agent address
"""

def generate_fetch_credentials():
    """Generate new Fetch.ai agent credentials"""
    from uagents import Agent
    from uagents.setup import fund_agent_if_low
    import secrets
    
    print("=" * 60)
    print("FETCH.AI AGENT CREDENTIAL GENERATOR")
    print("=" * 60)
    
    # Generate a secure random seed phrase
    seed_phrase = secrets.token_hex(16)  # 32 character hex string
    
    print(f"\n📝 Generated Seed Phrase:")
    print(f"   {seed_phrase}")
    print(f"\n⚠️  IMPORTANT: Save this seed phrase securely!")
    print(f"   You'll need it to recreate your agent.")
    
    # Create agent with the seed
    agent = Agent(
        name="test_agent",
        seed=seed_phrase,
        port=8000
    )
    
    print(f"\n🔑 Agent Address:")
    print(f"   {agent.address}")
    
    print(f"\n💰 Wallet Address:")
    print(f"   {agent.wallet.address()}")
    
    # Try to fund the agent (testnet)
    print(f"\n💸 Attempting to fund agent on testnet...")
    try:
        fund_agent_if_low(agent.wallet.address())
        print("   ✓ Agent funded successfully!")
    except Exception as e:
        print(f"   ⚠️  Funding failed (this is normal): {e}")
        print(f"   You can fund manually at: https://faucet.fetch.ai")
    
    # Generate .env content
    print(f"\n" + "=" * 60)
    print("ADD TO YOUR .env FILE:")
    print("=" * 60)
    print(f"FETCH_AGENT_SEED={seed_phrase}")
    print(f"# Agent address: {agent.address}")
    print(f"# Wallet address: {agent.wallet.address()}")
    print("=" * 60)
    
    return seed_phrase, agent.address, agent.wallet.address()

def verify_existing_seed(seed_phrase: str):
    """Verify an existing seed phrase and show agent info"""
    from uagents import Agent
    
    print("\n" + "=" * 60)
    print("VERIFYING EXISTING SEED PHRASE")
    print("=" * 60)
    
    try:
        agent = Agent(
            name="verify_agent",
            seed=seed_phrase,
            port=8000
        )
        
        print(f"\n✓ Seed phrase is valid!")
        print(f"\n🔑 Agent Address: {agent.address}")
        print(f"💰 Wallet Address: {agent.wallet.address()}")
        
        return True
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

def get_mailbox_key_info():
    """Information about mailbox keys"""
    print("\n" + "=" * 60)
    print("ABOUT MAILBOX KEYS (AGENTVERSE)")
    print("=" * 60)
    print("""
For production use with Agentverse, you need a mailbox key.

OPTIONS:

1. FOR TESTING (Local Development):
   - You DON'T need a mailbox key
   - Remove the 'mailbox' parameter from Agent()
   - Agents communicate directly via local network
   
   Example:
   agent = Agent(name="my_agent", seed="my_seed", port=8000)

2. FOR PRODUCTION (Agentverse):
   - Go to: https://agentverse.ai
   - Create an account
   - Navigate to: "My Agents" → "Create Agent"
   - Click on your agent → "Mailbox" tab
   - Copy the API key
   
   Add to .env:
   FETCH_MAILBOX_KEY=your_mailbox_api_key_here

NOTE: For this project, START WITHOUT a mailbox key for local testing!
""")

def create_test_agent():
    """Create a simple test agent to verify setup"""
    from uagents import Agent, Context
    import asyncio
    
    print("\n" + "=" * 60)
    print("CREATING TEST AGENT")
    print("=" * 60)
    
    seed = input("\nEnter seed phrase (or press Enter to generate new): ").strip()
    
    if not seed:
        print("Generating new seed...")
        seed = generate_fetch_credentials()[0]
    
    # Create agent WITHOUT mailbox for local testing
    agent = Agent(
        name="test_agent",
        seed=seed,
        port=8000,
        endpoint=["http://localhost:8000/submit"]
    )
    
    print(f"\n✓ Test agent created!")
    print(f"Address: {agent.address}")
    
    @agent.on_event("startup")
    async def startup(ctx: Context):
        print(f"\n✓ Agent started successfully!")
        print(f"Agent name: {ctx.name}")
        print(f"Agent address: {ctx.agent.address}")
        print(f"\nPress Ctrl+C to stop")
    
    @agent.on_interval(period=5.0)
    async def heartbeat(ctx: Context):
        ctx.logger.info("Agent is running... ❤️")
    
    try:
        print("\nStarting agent (press Ctrl+C to stop)...")
        agent.run()
    except KeyboardInterrupt:
        print("\n\nAgent stopped.")

def main():
    """Main menu"""
    print("\n" + "=" * 60)
    print("FETCH.AI AGENT SETUP UTILITY")
    print("=" * 60)
    print("""
Choose an option:

1. Generate new agent credentials (seed + address)
2. Verify existing seed phrase
3. Learn about mailbox keys
4. Create and test a simple agent
5. Exit
""")
    
    choice = input("Enter choice (1-5): ").strip()
    
    if choice == "1":
        generate_fetch_credentials()
        
    elif choice == "2":
        seed = input("\nEnter seed phrase to verify: ").strip()
        if seed:
            verify_existing_seed(seed)
        else:
            print("No seed phrase provided.")
    
    elif choice == "3":
        get_mailbox_key_info()
    
    elif choice == "4":
        create_test_agent()
    
    elif choice == "5":
        print("\nGoodbye!")
        return
    
    else:
        print("\nInvalid choice!")
    
    # Ask to continue
    continue_choice = input("\n\nRun again? (y/n): ").strip().lower()
    if continue_choice == 'y':
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()