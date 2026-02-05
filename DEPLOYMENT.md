# Deployment Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager
- OpenAI API key OR Anthropic API key

## Quick Start

### 1. Setup

Run the setup script to install dependencies and configure the environment:

```bash
python setup.py
```

### 2. Configure Environment Variables

Edit the `.env` file with your credentials:

```env
# API Configuration
API_KEY=your-secret-api-key-here

# Choose your AI provider (openai or anthropic)
AI_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview

# OR Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### 3. Run the Application

```bash
python main.py
```

The API will start on `http://localhost:8000`

### 4. Test the API

Run the test client to verify everything works:

```bash
python test_client.py
```

## API Usage

### Authentication

All requests require an API key in the header:

```
X-API-Key: your-secret-api-key-here
```

### Endpoint: POST /api/analyze

**Request:**
```json
{
  "conversation_id": "unique-conversation-id",
  "message": "Hi, I need your help with something urgent",
  "conversation_history": [
    {
      "role": "scammer",
      "message": "Previous message"
    },
    {
      "role": "agent",
      "message": "Previous response"
    }
  ]
}
```

**Response:**
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
    "phone_numbers": ["9876543210"],
    "email_addresses": ["scammer@fake.com"],
    "scam_indicators": ["urgency", "money_request"],
    "scam_type": "prize_scam"
  },
  "metadata": {
    "engagement_duration_seconds": 45.2,
    "detection_method": "ai_analysis",
    "agent_strategy": "extract",
    "model_used": "gpt-4-turbo-preview"
  }
}
```

## Production Deployment

### Using Gunicorn (Linux/Mac)

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

Build and run:

```bash
docker build -t honeypot-api .
docker run -p 8000:8000 --env-file .env honeypot-api
```

### Cloud Deployment Options

#### Heroku
```bash
# Create Procfile
echo "web: python main.py" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
heroku config:set API_KEY=your-key
heroku config:set OPENAI_API_KEY=your-openai-key
```

#### AWS EC2
1. Launch an EC2 instance
2. Install Python and dependencies
3. Configure security groups (open port 8000)
4. Run the application with a process manager (systemd or supervisor)

#### Google Cloud Run
```bash
gcloud run deploy honeypot-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Security Best Practices

1. **API Key Management**
   - Use strong, random API keys
   - Rotate keys regularly
   - Never commit keys to version control

2. **Rate Limiting**
   - Implement rate limiting for production
   - Use Redis for distributed rate limiting

3. **HTTPS**
   - Always use HTTPS in production
   - Use a reverse proxy (nginx) with SSL certificates

4. **Monitoring**
   - Log all API requests
   - Monitor for unusual patterns
   - Set up alerts for errors

## Monitoring and Logging

### Add Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('honeypot.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics to Track

- Total conversations
- Scam detection rate
- Average engagement duration
- Intelligence extraction success rate
- API response time

## Troubleshooting

### Common Issues

**Issue: API key error**
- Check that API_KEY is set in .env
- Verify the X-API-Key header is sent with requests

**Issue: AI provider errors**
- Verify OPENAI_API_KEY or ANTHROPIC_API_KEY is valid
- Check API quota and rate limits
- Ensure internet connectivity

**Issue: Port already in use**
- Change PORT in .env file
- Kill the process using the port: `lsof -ti:8000 | xargs kill -9`

## Scaling Considerations

1. **Horizontal Scaling**
   - Deploy multiple instances behind a load balancer
   - Use Redis for shared conversation memory

2. **Database**
   - Replace in-memory storage with PostgreSQL/MongoDB
   - Store conversation history persistently

3. **Caching**
   - Cache AI responses for similar inputs
   - Use Redis for caching

4. **Queue System**
   - Use Celery/RabbitMQ for async processing
   - Handle long-running conversations in background

## Support

For issues or questions:
- Check the documentation
- Review logs for error messages
- Verify environment configuration
