# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

An AI-powered system that detects scam messages and autonomously engages scammers to extract actionable intelligence through multi-turn conversations.

## Features

- **Scam Detection**: Analyzes incoming messages to detect scam intent using AI
- **Autonomous Agent**: Engages scammers with realistic human-like conversations
- **Intelligence Extraction**: Extracts bank accounts, UPI IDs, and phishing links
- **Multi-turn Conversations**: Maintains conversation history and context
- **Secure API**: Protected with API key authentication
- **Low Latency**: Optimized for stable and fast responses

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the application:
```bash
python main.py
```

## API Endpoint

**POST /api/analyze**

Headers:
- `X-API-Key`: Your API key for authentication

Request Body:
```json
{
  "conversation_id": "unique-conversation-id",
  "message": "Hi, I need your help with something urgent",
  "conversation_history": [
    {"role": "scammer", "message": "Previous message"},
    {"role": "agent", "message": "Previous response"}
  ]
}
```

Response:
```json
{
  "conversation_id": "unique-conversation-id",
  "scam_detected": true,
  "confidence_score": 0.95,
  "response": "Oh no, what happened? How can I help?",
  "engagement_active": true,
  "turn_count": 2,
  "extracted_intelligence": {
    "bank_accounts": ["1234567890"],
    "upi_ids": ["scammer@paytm"],
    "phishing_urls": ["https://fake-site.com"],
    "scam_indicators": ["urgency", "money_request"]
  },
  "metadata": {
    "engagement_duration_seconds": 45,
    "detection_method": "ai_analysis",
    "agent_strategy": "build_trust"
  }
}
```

## Project Structure

```
ai-honeypot/
├── main.py                 # Application entry point
├── api/
│   └── routes.py          # API endpoints
├── agent/
│   ├── detector.py        # Scam detection
│   ├── conversation.py    # AI conversation agent
│   └── extractor.py       # Intelligence extraction
├── models/
│   └── schemas.py         # Data models
├── utils/
│   ├── ai_client.py       # AI provider interface
│   └── memory.py          # Conversation memory
└── config.py              # Configuration

```

## Architecture

1. **API Layer**: Receives messages and returns structured responses
2. **Detection Layer**: Analyzes messages for scam indicators
3. **Agent Layer**: Autonomous AI agent for scammer engagement
4. **Extraction Layer**: Parses and extracts intelligence
5. **Memory Layer**: Maintains conversation context

## Evaluation Metrics

- Scam detection accuracy
- Engagement duration
- Number of conversation turns
- Quality of extracted intelligence
- Response latency

## Security

- API key authentication
- Input validation
- Rate limiting (optional)
- Secure credential handling

## License

MIT License
