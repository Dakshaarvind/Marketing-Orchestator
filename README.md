# Marketing-Orchestator

┌─────────────────┐
│  Agentverse UI  │ (User inputs campaign details)
└────────┬────────┘
         │ HTTP POST
         ▼
┌─────────────────────────┐
│  Orchestrator Agent     │ (Flask webhook receives message)
│  Port: 5000             │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Analysis CrewAI Agent  │ (Python function call - no messaging)
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Orchestrator Agent     │ (Send response back to Agentverse)
└─────────────────────────┘