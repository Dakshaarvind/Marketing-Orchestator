# Marketing Orchestrator

An AI-powered marketing content generation system that creates complete, Instagram-ready posts from natural language input. Built with Fetch.ai's uAgents framework and CrewAI, the system orchestrates multiple specialized AI agents to deliver professional, SEO-optimized social media content.

## 🎯 Overview

The Marketing Orchestrator takes a simple natural language description of your business and campaign goals, then automatically:
- Analyzes your target audience
- Researches competitors
- Generates engaging Instagram content
- Optimizes for SEO and discoverability

**Result:** A complete Instagram post ready to copy-paste and publish, including caption, hashtags, posting time, and business insights.

## ✨ Features

- **Natural Language Input**: Describe your business and goals in plain English
- **4-Stage AI Pipeline**: Analysis → Competitor Research → Content Generation → SEO Optimization
- **Competitor Intelligence**: Automatically finds and analyzes local competitors via Yelp API
- **SEO Optimization**: Strategic hashtag mix and keyword optimization (typically 85-90/100 SEO score)
- **Location-Aware**: Incorporates location-based keywords and tags
- **ASI1 Integration**: Chat with the agent directly via ASI1 UI
- **No Infrastructure Required**: Uses Mailbox connection (no ngrok needed)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              ASI1 / Agentverse UI                       │
│         (User sends natural language)                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         uAgents Framework (Orchestrator.py)              │
│  • ASI1 Chat Protocol Handler                           │
│  • Mailbox Connection (no ngrok)                        │
│  • Message Routing                                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         CrewAI Agents (Internal Processing)             │
│  1. NL Parser → 2. Analysis → 3. Competitor →           │
│     4. Content Gen → 5. SEO                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Final Instagram Post (Markdown)                  │
│         Sent back via uAgents Chat Protocol             │
└─────────────────────────────────────────────────────────┘
```

### Framework Stack

- **uAgents (Fetch.ai)**: Agent-to-agent communication, ASI1 Chat Protocol, Mailbox connection
- **CrewAI**: Multi-agent orchestration with structured outputs
- **OpenAI GPT-4**: Content generation and analysis
- **Yelp Fusion API**: Competitor research data

## 📁 Project Structure

```
Marketing-Orchestator/
├── agents/
│   ├── Orchestrator.py          # Main orchestrator (uAgents + ASI1 Chat Protocol)
│   ├── analysis_agent.py         # Audience analysis agent
│   ├── Competitor_Agent.py      # Competitor research agent (Yelp API)
│   ├── content_generation.py     # Instagram content generation agent
│   ├── seo_agent.py             # SEO optimization agent
│   └── nl_parser.py             # Natural language parsing
├── tests/                        # Test files
├── fetch_setup.py                # Agent credential generator
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (create this)
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Yelp Fusion API key (for competitor research)
- Fetch.ai Agentverse account (optional, for ASI1 UI)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Marketing-Orchestator
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   # Agent Configuration
   AGENT_SECRET_KEY_1=your_agent_seed_phrase_here
   AGENT_PORT=8000
   USE_MAILBOX=true
   
   # API Keys
   OPENAI_API_KEY=your_openai_api_key_here
   YELP_API_KEY=your_yelp_api_key_here
   
   # Optional: Agentverse API (for deployment)
   AGENTVERSE_API_KEY=your_agentverse_api_key_here
   ```

5. **Generate agent credentials** (if you don't have a seed phrase)
   ```bash
   python fetch_setup.py
   ```
   Choose option 1 to generate a new seed phrase, then add it to your `.env` file.

### Running the Orchestrator

1. **Start the agent**
   ```bash
   python agents/Orchestrator.py
   ```

2. **Verify connection**
   You should see:
   ```
   INFO: Using Mailbox connection (mailbox=True) - no public endpoint needed
   INFO: Orchestrator agent address: agent1q...
   INFO: Mailbox access token acquired
   INFO: Registration on Almanac API successful
   ```

3. **Access via ASI1**
   - Go to [ASI1 UI](https://asi1.ai) or [Agentverse](https://agentverse.ai)
   - Search for your agent by address or name "Marketing Orchestrator"
   - Start chatting!

## 💬 Usage Examples

### Example 1: Cafe Promotion

**Input:**
```
I have a cafe named Nirvana Soul at San Jose State University. 
Tomorrow is Sunday, I want to post about a free cookie offer 
with any latte purchase.
```

**Output:**
- SEO-optimized caption with location keywords
- 17 strategic hashtags (mix of high/medium/low competition)
- Post type: Photo
- Suggested posting time: 3:00 PM
- Business insights and competitor analysis
- SEO Score: 88/100

### Example 2: Donut Shop

**Input:**
```
I have a donut shop in LA, want to post about buy 1 get 1 free donut
```

**Output:**
- Caption optimized for Los Angeles market
- Location tags: #LosAngeles, #LADonuts
- Engagement times: 11:00, 15:00, 19:00, 20:00, 21:00
- SEO Score: 88/100

## 🤖 Agent Details

### 1. Natural Language Parser (`nl_parser.py`)

**Purpose:** Converts natural language input into structured data

**Input:** 
```
"I have a donut shop in LA, want to post about buy 1 get 1 free donut"
```

**Output:**
```json
{
  "business_type": "donut shop",
  "location": "Los Angeles, CA",
  "campaign_goals": "Promote buy 1 get 1 free donut offer"
}
```

---

### 2. Analysis Agent (`analysis_agent.py`)

**Purpose:** Analyzes target audience and engagement strategy

**Output:**
- Target audience demographics
- Optimal posting times (3-5 times)
- Recommended content tone
- Post frequency (posts per week)
- Platform insights (Stories, Reels, Carousels)

**Example Output:**
```json
{
  "target_audience": "Primarily millennials and Gen Z (ages 18-34)...",
  "engagement_times": ["11:00", "15:00", "19:00", "20:00", "21:00"],
  "content_tone": "Playful and inviting...",
  "recommended_post_frequency": 4,
  "platform_insights": {
    "story_frequency": "Post daily stories...",
    "reel_priority": "high",
    "carousel_usage": "Use carousels to showcase..."
  }
}
```

---

### 3. Competitor Research Agent (`Competitor_Agent.py`)

**Purpose:** Finds and analyzes local competitors

**Features:**
- Uses Yelp Fusion API to find competitors
- Analyzes ratings, categories, locations
- Extracts market positioning and trends
- Identifies content opportunities
- Generates competitor hashtags

**Output:**
- List of competitors with ratings
- Market positioning analysis
- Common success factors
- Service gaps and opportunities
- Target audience preferences
- Recommended hashtags

---

### 4. Content Generation Agent (`content_generation.py`)

**Purpose:** Generates Instagram-ready content

**Output:**
- Engaging caption
- 10-15 relevant hashtags
- Post type recommendation (Photo/Reel/Carousel/Story)
- Call-to-action
- Suggested posting time
- Media prompts (ideas for visuals)
- Optional: Image generation via DALL-E

**Example Output:**
```json
{
  "caption": "Double the sweetness, double the fun! 🍩✨...",
  "hashtags": ["#DonutLovers", "#SweetTreats", ...],
  "post_type": "Photo",
  "call_to_action": "Tag a friend to share your donut love...",
  "suggested_post_time": "15:00",
  "media_prompts": ["Close-up of two donuts...", ...]
}
```

---

### 5. SEO Optimization Agent (`seo_agent.py`)

**Purpose:** Optimizes content for maximum discoverability

**Features:**
- Optimizes caption with natural keyword placement
- Creates strategic hashtag mix:
  - 3-5 high-competition hashtags
  - 5-7 medium-competition hashtags
  - 3-5 low-competition hashtags
- Calculates SEO score (0-100)
- Suggests alt text for accessibility
- Adds location-based tags

**Output:**
```json
{
  "optimized_caption": "Double the sweetness and fun in Los Angeles! 🍩✨...",
  "optimized_hashtags": ["#DonutLovers", "#LosAngelesEats", ...],
  "keyword_suggestions": ["Los Angeles donuts", "buy 1 get 1 free donuts", ...],
  "seo_score": 88,
  "improvements": [
    "Added location-based keywords for local SEO",
    "Optimized hashtag mix for better reach",
    ...
  ],
  "alt_text_suggestion": "A colorful assortment of artisan donuts...",
  "location_tags": ["#LosAngeles", "#LADonuts"]
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `AGENT_SECRET_KEY_1` | Agent seed phrase | Yes | - |
| `AGENT_PORT` | Port for local agent | No | 8000 |
| `USE_MAILBOX` | Enable Mailbox connection | No | true |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `YELP_API_KEY` | Yelp Fusion API key | Yes | - |
| `AGENTVERSE_API_KEY` | Agentverse API key (for deployment) | No | - |
| `AGENT_ENDPOINT_URL` | Public endpoint URL (if not using mailbox) | No | - |

### Mailbox vs Public Endpoint

**Mailbox (Recommended):**
- No ngrok needed
- Outbound connection to Agentverse Mailroom
- Set `USE_MAILBOX=true` in `.env`

**Public Endpoint:**
- Requires ngrok or public URL
- Set `AGENT_ENDPOINT_URL` in `.env`
- Set `USE_MAILBOX=false`

## 🧪 Testing

### Test Individual Agents

```bash
# Test NL Parser
python -m pytest tests/test_nl_parser.py

# Test Analysis Agent
python tests/direct_tests.py
```

### Test Full Pipeline

1. Start the orchestrator: `python agents/Orchestrator.py`
2. Send a message via ASI1 UI
3. Check terminal logs for execution flow

## 📊 Output Format

The final output includes:

1. **Instagram Post**
   - SEO-optimized caption
   - Strategic hashtags (15-20 tags)
   - Post type recommendation
   - Suggested posting time
   - Call-to-action

2. **Media Information**
   - Media prompts for visuals
   - Alt text for accessibility
   - Image URL (if generated)

3. **Business Insights**
   - Target audience description
   - Content tone recommendation
   - Post frequency suggestion
   - Engagement times

4. **SEO Metrics**
   - SEO score (0-100)
   - Keyword suggestions
   - Improvements made
   - Location tags

## 🐛 Troubleshooting

### Agent Not Connecting

**Issue:** "Mailbox access token acquired" but agent not visible in ASI1

**Solution:**
- Verify `AGENT_SECRET_KEY_1` is correct
- Check agent is registered: Look for "Registration on Almanac API successful"
- Wait 30-60 seconds for registration to propagate

### Import Errors

**Issue:** `ModuleNotFoundError: No module named 'analysis_agent'`

**Solution:**
- Ensure you're running from the project root
- Check all agent files are in `agents/` directory
- Verify virtual environment is activated

### API Key Errors

**Issue:** `401 Unauthorized` for OpenAI or Yelp

**Solution:**
- Verify API keys in `.env` file
- Check keys are not truncated
- Ensure `.env` file is in project root

### Port Already in Use

**Issue:** `Address already in use` on port 8000

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change port in .env
AGENT_PORT=8001
```

## 🚧 Future Work

- [ ] **Scheduler Agent**: Instagram Graph API integration for automatic posting
- [ ] **Image Generation**: Enhanced DALL-E integration with automatic image creation
- [ ] **Multi-platform Support**: Extend to Twitter, LinkedIn, Facebook
- [ ] **Analytics Integration**: Track post performance and optimize based on engagement
- [ ] **A/B Testing**: Generate multiple content variations
- [ ] **Content Calendar**: Plan content weeks in advance
- [ ] **Review Analysis**: Analyze competitor reviews for deeper insights

## 📝 License

[Add your license here]

## 👥 Contributors

- Chayan - Main Developer

## 🙏 Acknowledgments

- Fetch.ai for uAgents framework
- CrewAI for multi-agent orchestration
- OpenAI for GPT-4 and DALL-E
- Yelp for Fusion API

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with ❤️ using Fetch.ai uAgents and CrewAI**
