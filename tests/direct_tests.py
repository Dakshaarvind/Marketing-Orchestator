# direct_test.py
"""
Direct test of the Analysis Agent without Fetch.ai agent communication
This bypasses the agent messaging issues and directly tests the CrewAI agent
"""
import sys
import os
from pathlib import Path

# Add agents directory to path
agents_dir = Path(__file__).parent / "agents"
sys.path.insert(0, str(agents_dir))

from dotenv import load_dotenv
import json

# Load environment
load_dotenv()

def test_analysis_agent():
    """Test the Analysis Agent directly"""
    print("=" * 60)
    print("TESTING ANALYSIS AGENT (DIRECT)")
    print("=" * 60)
    
    # Check OpenAI key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n ERROR: OPENAI_API_KEY not found in .env file")
        print("\nPlease add your OpenAI API key to .env:")
        print("OPENAI_API_KEY=sk-your-key-here")
        return
    
    print(f"\n✓ OpenAI API key found: {api_key[:20]}...")
    
    # Test parameters
    test_cases = [
        {
            "name": "Donut Shop - Los Angeles",
            "business_type": "donut shop",
            "location": "Los Angeles, CA",
            "campaign_goals": "Increase local foot traffic and build Instagram following among young professionals"
        },
        {
            "name": "Bakery - San Francisco",
            "business_type": "artisan bakery",
            "location": "San Francisco, CA",
            "campaign_goals": "Promote catering services and expand corporate client base"
        }
    ]
    
    # Import the analysis agent
    try:
        from analysis_agent import run_analysis_agent
        print("✓ Analysis agent imported successfully\n")
    except ImportError as e:
        print(f"\n ERROR: Could not import analysis_agent: {e}")
        print("\nMake sure you have analysis_agent.py in the agents/ directory")
        return
    
    # Run tests
    for i, test_case in enumerate(test_cases, 1):
        print("\n" + "=" * 60)
        print(f"TEST {i}: {test_case['name']}")
        print("=" * 60)
        print(f"Business Type: {test_case['business_type']}")
        print(f"Location: {test_case['location']}")
        print(f"Goals: {test_case['campaign_goals']}")
        print("\n Running analysis (this may take 30-60 seconds)...")
        
        try:
            # Run the analysis
            result = run_analysis_agent(
                business_type=test_case['business_type'],
                location=test_case['location'],
                campaign_goals=test_case['campaign_goals'],
                api_key=api_key
            )
            
            print("\n ANALYSIS COMPLETE!")
            print("-" * 60)
            print(f" Target Audience:")
            print(f"   {result.target_audience}")
            print(f"\n Best Posting Times:")
            print(f"   {', '.join(result.engagement_times)}")
            print(f"\n Content Tone:")
            print(f"   {result.content_tone}")
            print(f"\n Recommended Frequency:")
            print(f"   {result.recommended_post_frequency} posts per week")
            
            if result.platform_insights:
                print(f"\n Platform Insights:")
                for key, value in result.platform_insights.items():
                    print(f"   - {key}: {value}")
            
            print("\n" + "-" * 60)
            print("✓ Test passed!")
            
            # Ask if user wants to continue
            if i < len(test_cases):
                response = input("\nRun next test? (y/n): ").strip().lower()
                if response != 'y':
                    break
            
        except Exception as e:
            print(f"\n ERROR during analysis: {str(e)}")
            print("\nFull error:")
            import traceback
            traceback.print_exc()
            
            # Check common issues
            if "api_key" in str(e).lower():
                print("\n Tip: Check your OpenAI API key is valid and has credits")
            elif "rate limit" in str(e).lower():
                print("\n Tip: You may have hit OpenAI's rate limit. Wait a minute and try again")
            elif "timeout" in str(e).lower():
                print("\n Tip: Request timed out. Check your internet connection")
            
            break
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

def test_campaign_flow():
    """Simulate the full campaign flow without agent messaging"""
    print("\n" + "=" * 60)
    print("SIMULATING FULL CAMPAIGN FLOW")
    print("=" * 60)
    
    from analysis_agent import run_analysis_agent
    
    # Simulate user request
    campaign_request = {
        "business_type": "donut shop",
        "location": "Los Angeles, CA",
        "campaign_goals": "Increase local foot traffic and Instagram following",
        "auto_publish": False,
        "user_id": "test_user_123"
    }
    
    print("\n Campaign Request:")
    print(json.dumps(campaign_request, indent=2))
    
    print("\n Processing stages:")
    
    # Stage 1: Analysis
    print("\n  [1/4]  Running Analysis Agent...")
    try:
        analysis_result = run_analysis_agent(
            business_type=campaign_request['business_type'],
            location=campaign_request['location'],
            campaign_goals=campaign_request['campaign_goals']
        )
        print("        ✓ Analysis complete")
        analysis_data = analysis_result.dict()
    except Exception as e:
        print(f"        ✗ Analysis failed: {e}")
        return
    
    # Stage 2-4: Placeholders
    print("  [2/4]  Competitor Research (not implemented)")
    print("  [3/4]  Content Generation (not implemented)")
    print("  [4/4]  Scheduling (not implemented)")
    
    # Prepare response
    campaign_response = {
        "request_id": f"{campaign_request['user_id']}_001",
        "status": "success",
        "analysis_data": analysis_data,
        "competitor_data": {"status": "pending"},
        "content_plan": {"status": "pending"},
        "schedule_data": {"status": "pending"}
    }
    
    print("\n Campaign Response:")
    print(json.dumps(campaign_response, indent=2))
    
    print("\n✅ Flow simulation complete!")

def main():
    """Main menu"""
    print("\n" + "=" * 60)
    print("MARKETING ORCHESTRATOR - DIRECT TESTING")
    print("=" * 60)
    print("""
This bypasses the Fetch.ai agent communication and directly tests
the CrewAI Analysis Agent. Use this to verify everything works
before troubleshooting agent messaging.

Options:
  1. Test Analysis Agent only
  2. Simulate full campaign flow
  3. Exit
""")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        test_analysis_agent()
    elif choice == "2":
        test_campaign_flow()
    elif choice == "3":
        print("\nGoodbye!")
        return
    else:
        print("\nInvalid choice!")
        return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Interrupted by user")
    except Exception as e:
        print(f"\n\n Unexpected error: {e}")
        import traceback
        traceback.print_exc()