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

For personal ref:
run python orchestrator.py on one terminal
run .\ngrok.exe http 5000 on another (this can expire)
