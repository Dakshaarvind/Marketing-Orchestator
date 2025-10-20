# agents/nl_parser.py
"""
Natural Language Parser for Campaign Requests
Extracts structured data from user's natural language input
"""
from openai import OpenAI
import json
import os
from typing import Dict, Optional
from pydantic import BaseModel

class CampaignRequest(BaseModel):
    """Structured campaign request"""
    business_type: str
    location: Optional[str] = None
    campaign_goals: str
    
class NaturalLanguageParser:
    """Parses natural language into structured campaign requests"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    
    def parse(self, user_input: str) -> CampaignRequest:
        """
        Parse natural language input into structured format
        
        Args:
            user_input: User's natural language message
            
        Returns:
            CampaignRequest with extracted fields
        """
        
        system_prompt = """You are a helpful assistant that extracts structured information from user messages about marketing campaigns.

Extract these fields from the user's message:
1. business_type: The type of business (e.g., "donut shop", "bakery", "restaurant", "coffee shop")
2. location: The location of the business (city, state, country) - if mentioned
3. campaign_goals: What the user wants to achieve with their marketing campaign

IMPORTANT:
- If business_type isn't explicitly mentioned, infer it from context
- If location isn't mentioned, set it to null
- For campaign_goals, capture the essence of what they want to achieve
- Return ONLY valid JSON, no additional text

Example inputs and outputs:

Input: "I have a donut shop in Los Angeles and want to increase local foot traffic"
Output: {"business_type": "donut shop", "location": "Los Angeles, CA", "campaign_goals": "Increase local foot traffic"}

Input: "Help me market my bakery, I'm in San Francisco and need more corporate catering clients"
Output: {"business_type": "bakery", "location": "San Francisco, CA", "campaign_goals": "Attract more corporate catering clients"}

Input: "I run a coffee place and want more Instagram followers"
Output: {"business_type": "coffee shop", "location": null, "campaign_goals": "Increase Instagram following"}

Now extract from the user's input."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = result_text[start_idx:end_idx]
                data = json.loads(json_str)
                return CampaignRequest(**data)
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            # Fallback: return a generic request
            return CampaignRequest(
                business_type="food business",
                location=None,
                campaign_goals=user_input
            )

def parse_user_input(user_input: str) -> Dict:
    """
    Helper function to parse user input
    
    Args:
        user_input: Natural language or JSON string
        
    Returns:
        Dict with business_type, location, campaign_goals
    """
    # Check if input is already JSON
    try:
        data = json.loads(user_input)
        if 'business_type' in data and 'campaign_goals' in data:
            return data
    except json.JSONDecodeError:
        pass
    
    # Parse as natural language
    parser = NaturalLanguageParser()
    request = parser.parse(user_input)
    return request.dict()

# Test examples
if __name__ == "__main__":
    parser = NaturalLanguageParser()
    
    test_inputs = [
        "I have a donut shop in Los Angeles and want to increase local foot traffic",
        "Help me create an Instagram campaign for my bakery in SF. Need more corporate clients.",
        "I run a taco food truck in Austin and want more followers",
        "Coffee shop owner here, need help with social media marketing",
        "My restaurant in Brooklyn needs better Instagram presence"
    ]
    
    print("=" * 60)
    print("NATURAL LANGUAGE PARSER TEST")
    print("=" * 60)
    
    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        result = parser.parse(user_input)
        print(f"Output: {result.dict()}")
        print("-" * 60)