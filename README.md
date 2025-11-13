# Marketing Orchestrator

An AI-powered marketing content generation system that creates complete, Instagram-ready posts from natural language input. Built with Fetch.ai's uAgents framework and CrewAI, the system orchestrates multiple specialized AI agents to deliver professional, SEO-optimized social media content.

## 🚀 Key Highlights

- ⚡ **Fast**: Complete campaigns generated in 10-15 seconds
- 🎯 **Intelligent**: 4-stage AI pipeline with competitor analysis
- 🖼️ **Visual**: Automatic DALL-E 3 image generation
- 📊 **Data-Driven**: SEO scores, metrics, and strategic insights
- 📋 **Ready-to-Use**: Copy-paste format for immediate posting
- 🔗 **Easy Integration**: ASI1 Chat Protocol, no complex setup

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
- **AI Image Generation**: Automatic DALL-E 3 image generation for Instagram posts
- **Competitor Intelligence**: Automatically finds and analyzes local competitors via Yelp API
- **SEO Optimization**: Strategic hashtag mix and keyword optimization (typically 85-90/100 SEO score)
- **Location-Aware**: Incorporates location-based keywords and tags
- **Copy-Ready Format**: Pre-formatted content ready for direct paste into Instagram
- **Performance Metrics**: Real-time processing time, SEO scores, and campaign summaries
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
- **OpenAI DALL-E 3**: AI image generation for Instagram posts
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

**Output Includes:**
- **📊 Campaign Summary**: 
  - SEO Score: 88/100 ⭐
  - Hashtags: 17 optimized
  - Competitors: 5 analyzed
  - Generated in: 12.3 seconds

- **💡 Strategic Business Insights**:
  - Business Strength: "Unique community atmosphere, perfect for socializing and studying"
  - Content Tone: "Casual and friendly"
  - Target Audience: "Young professionals and students aged 18-35 in San Jose"
  - Competitive Advantage: "Differentiate through community engagement and special promotions"

- **📸 Instagram Post**:
  - Caption: SEO-optimized with location keywords
  - Hashtags: 17 strategic tags (#CoffeeLovers, #SanJoseEats, etc.)
  - Post Type: Photo
  - Optimal Time: 3:00 PM
  - Call to Action: "Tag a friend you want to share this treat with!"

- **🖼️ Generated Image**: 
  - AI-created DALL-E 3 image (1024x1024)
  - Professional food photography style
  - Alt text included for accessibility

- **📋 Copy-Ready Format**: Pre-formatted block ready for paste

- **📊 Performance Metrics**: SEO breakdown, keywords, optimizations

- **📈 Content Strategy**: Posting frequency, engagement times, content ideas

### Example 2: Donut Shop

**Input:**
```
I have a donut shop in LA, want to post about buy 1 get 1 free donut
```

**Output Includes:**
- **Campaign Summary**: SEO 88/100, 15 hashtags, 5 competitors, 10.8s processing
- **Instagram Post**: LA-optimized caption, location tags (#LosAngeles, #LADonuts)
- **Generated Image**: DALL-E 3 image of donuts with BOGO offer
- **Posting Strategy**: Engagement times (11:00, 15:00, 19:00, 20:00, 21:00)
- **Copy-Ready Format**: Ready to paste directly into Instagram

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
- **Image prompt**: Detailed description for DALL-E generation
- **Generated image**: Automatic DALL-E 3 image creation (1024x1024, Instagram-optimized)

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
| `OPENAI_API_KEY` | OpenAI API key (for GPT-4 and DALL-E 3) | Yes | - |
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

The final output is professionally formatted with clear sections, metrics, and ready-to-use content. The response is structured for maximum clarity and usability:

### Visual Structure

```
🎯 Instagram Marketing Campaign Ready!
├── 📊 Campaign Summary (Quick metrics at a glance)
├── 💡 Strategic Business Insights (4 key insights)
├── 📸 Your Instagram Post (Main content)
│   ├── Caption
│   ├── Hashtags (formatted for readability)
│   └── Post Details
├── 🖼️ Generated Visual Content (AI image)
├── 📊 Performance Metrics (SEO breakdown)
├── 📈 Content Strategy Recommendations
└── 📋 Copy-Ready Format (One-click copy)
```

The final output is professionally formatted and includes:

### 1. Campaign Summary (Top Section)
- SEO Score (e.g., 88/100 ⭐)
- Number of hashtags optimized
- Competitors analyzed
- Processing time (e.g., "Generated in 12.3 seconds")

### 2. Strategic Business Insights
- **Business Strength**: Key differentiators and unique value
- **Recommended Content Tone**: Optimal communication style
- **Target Audience**: Detailed demographic and psychographic profile
- **Competitive Advantage**: How to differentiate from competitors

### 3. Instagram Post Content
- **Caption**: SEO-optimized, engaging, ready-to-use
- **Hashtags**: 15-20 strategic tags (high/medium/low competition mix)
- **Post Details**: Type, optimal posting time, call-to-action

### 4. Generated Visual Content
- **AI-Generated Image**: DALL-E 3 image (1024x1024, Instagram-ready)
- **Alt Text**: Accessibility-friendly image description
- **Image Prompt**: Description used for generation

### 5. Performance Metrics
- **SEO Score**: 0-100 rating with detailed breakdown
- **Primary Keywords**: Top keywords for discoverability
- **Optimizations Applied**: List of SEO improvements made

### 6. Content Strategy Recommendations
- **Posting Frequency**: Recommended posts per week
- **Optimal Posting Times**: Best engagement windows
- **Additional Content Ideas**: Media prompts for future posts

### 7. Copy-Ready Format
- Pre-formatted text block ready for direct copy-paste into Instagram
- Includes caption and hashtags in one clean block

## 🐛 Troubleshooting

### Image Not Generating

**Issue:** No image appears in the response

**Solution:**
- Verify `OPENAI_API_KEY` has DALL-E access (most accounts include it)
- Check terminal logs for: "Generating image with DALL-E..."
- If you see errors, verify API key is valid and has sufficient credits
- Image generation is optional - content will still be generated without it

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

## 🎨 Image Generation

The system automatically generates Instagram-ready images using DALL-E 3:

- **Model**: DALL-E 3
- **Size**: 1024x1024 (square format, perfect for Instagram)
- **Quality**: Standard
- **Style**: Enhanced with "professional food photography, Instagram-worthy" keywords
- **Cost**: ~$0.04 per image

**How it works:**
1. Content Agent creates a detailed `image_prompt` describing the visual
2. DALL-E 3 generates the image automatically
3. Image URL is included in the response
4. Image displays in ASI1 UI via markdown rendering

**Note**: DALL-E image URLs are temporary (expire after a few hours). Users should download images if they want to keep them.

## 🚧 Future Work

- [x] **Image Generation**: DALL-E 3 integration with automatic image creation ✅
- [ ] **Scheduler Agent**: Instagram Graph API integration for automatic posting
- [ ] **Image Hosting**: Permanent image storage (currently URLs expire)
- [ ] **Multi-platform Support**: Extend to Twitter, LinkedIn, Facebook
- [ ] **Analytics Integration**: Track post performance and optimize based on engagement
- [ ] **A/B Testing**: Generate multiple content variations
- [ ] **Content Calendar**: Plan content weeks in advance
- [ ] **Review Analysis**: Analyze competitor reviews for deeper insights
- [ ] **Batch Processing**: Generate multiple posts at once
- [ ] **Custom Image Styles**: Business-specific image generation styles

## 📝 License

[Add your license here]

## 👥 Contributors

- Chayan - Main Developer

## 📈 Performance Metrics

### Processing Times
- **Average Total Time**: 10-15 seconds for complete campaign
- **Analysis Agent**: ~3-4 seconds
- **Competitor Research**: ~2-3 seconds (finds 5 competitors)
- **Content Generation**: ~4-5 seconds (including image generation)
- **SEO Optimization**: ~2-3 seconds
- **Image Generation**: ~3-5 seconds per image (DALL-E 3)

### Quality Metrics
- **SEO Score Range**: Typically 85-90/100
- **Hashtag Optimization**: 15-20 strategic tags per post
- **Competitor Analysis**: 5 competitors analyzed per campaign
- **Image Quality**: 1024x1024, Instagram-optimized

### System Efficiency
- **Total Pipeline**: End-to-end in under 20 seconds
- **Success Rate**: High (with proper API keys)
- **Error Handling**: Graceful fallbacks at each stage

## 🙏 Acknowledgments

- Fetch.ai for uAgents framework and ASI1 Chat Protocol
- CrewAI for multi-agent orchestration
- OpenAI for GPT-4 and DALL-E 3
- Yelp for Fusion API

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with ❤️ using Fetch.ai uAgents and CrewAI**
