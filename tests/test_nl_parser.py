# test_nl_parser.py
"""
Test the natural language parser
"""
from agents.nl_parser import parse_user_input
import json

# Test cases
test_inputs = [
    # Natural language
    "I have a donut shop in Los Angeles and want to increase local foot traffic",
    "Help me market my bakery in SF. I need more corporate catering clients.",
    "I run a taco food truck in Austin and want more Instagram followers",
    "Coffee shop owner, need social media help",
    
    # Already JSON
    '{"business_type":"donut shop","location":"LA","campaign_goals":"increase sales"}',
]

print("=" * 70)
print("NATURAL LANGUAGE PARSER TESTS")
print("=" * 70)

for i, user_input in enumerate(test_inputs, 1):
    print(f"\nTest {i}:")
    print(f"Input: {user_input[:80]}...")
    
    try:
        result = parse_user_input(user_input)
        print(f"✓ Success!")
        print(f"  Business Type: {result['business_type']}")
        print(f"  Location: {result.get('location', 'Not specified')}")
        print(f"  Goals: {result['campaign_goals']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("-" * 70)

print("\n✓ All tests complete!")