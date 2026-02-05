"""Example usage and integration patterns."""

# Example 1: Basic Python Integration
# -----------------------------------

import requests

def analyze_scam_message(message: str, conversation_id: str):
    """Send a message to the honey-pot API for analysis."""
    url = "http://localhost:8000/api/analyze"
    headers = {
        "X-API-Key": "your-secret-api-key-here",
        "Content-Type": "application/json"
    }
    
    payload = {
        "conversation_id": conversation_id,
        "message": message,
        "conversation_history": []
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


# Example 2: Multi-turn Conversation
# -----------------------------------

class ScamConversationHandler:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.conversations = {}
    
    def process_message(self, conversation_id: str, message: str):
        """Process a message and maintain conversation history."""
        # Get existing history
        history = self.conversations.get(conversation_id, [])
        
        # Make API call
        url = f"{self.base_url}/api/analyze"
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "conversation_id": conversation_id,
            "message": message,
            "conversation_history": history
        }
        
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        
        # Update history
        history.append({"role": "scammer", "message": message})
        history.append({"role": "agent", "message": result["response"]})
        self.conversations[conversation_id] = history
        
        return result


# Example 3: Integration with Web Framework (Flask)
# --------------------------------------------------

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

HONEYPOT_API = "http://localhost:8000/api/analyze"
HONEYPOT_API_KEY = "your-secret-api-key-here"

@app.route('/webhook/message', methods=['POST'])
def handle_incoming_message():
    """Webhook to receive messages from messaging platforms."""
    data = request.json
    
    # Extract message details
    sender_id = data.get('sender_id')
    message_text = data.get('message')
    
    # Analyze with honey-pot
    response = requests.post(
        HONEYPOT_API,
        headers={"X-API-Key": HONEYPOT_API_KEY},
        json={
            "conversation_id": sender_id,
            "message": message_text,
            "conversation_history": []
        }
    )
    
    result = response.json()
    
    # Log if scam detected
    if result['scam_detected']:
        log_scam_attempt(sender_id, result['extracted_intelligence'])
    
    # Return response to messaging platform
    return jsonify({
        "response": result['response']
    })


# Example 4: Async Integration with asyncio
# ------------------------------------------

import asyncio
import aiohttp

async def analyze_message_async(session, message: str, conversation_id: str):
    """Async version of message analysis."""
    url = "http://localhost:8000/api/analyze"
    headers = {
        "X-API-Key": "your-secret-api-key-here",
        "Content-Type": "application/json"
    }
    
    payload = {
        "conversation_id": conversation_id,
        "message": message,
        "conversation_history": []
    }
    
    async with session.post(url, headers=headers, json=payload) as response:
        return await response.json()


async def process_multiple_messages():
    """Process multiple messages concurrently."""
    messages = [
        ("conv1", "You won a prize!"),
        ("conv2", "Urgent: Your account is locked"),
        ("conv3", "Invest in crypto for high returns")
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            analyze_message_async(session, msg, conv_id)
            for conv_id, msg in messages
        ]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            print(f"Scam detected: {result['scam_detected']}")
            print(f"Response: {result['response']}\n")


# Example 5: Integration with Discord Bot
# ----------------------------------------

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

HONEYPOT_API = "http://localhost:8000/api/analyze"
HONEYPOT_API_KEY = "your-secret-api-key-here"

@bot.event
async def on_message(message):
    """Analyze messages for scams."""
    if message.author == bot.user:
        return
    
    # Check suspicious messages
    if any(word in message.content.lower() for word in ['urgent', 'prize', 'won', 'invest']):
        response = requests.post(
            HONEYPOT_API,
            headers={"X-API-Key": HONEYPOT_API_KEY},
            json={
                "conversation_id": str(message.author.id),
                "message": message.content,
                "conversation_history": []
            }
        )
        
        result = response.json()
        
        if result['scam_detected'] and result['confidence_score'] > 0.7:
            await message.channel.send("⚠️ Warning: This message may be a scam!")
            
            # Log to admin channel
            admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)
            await admin_channel.send(
                f"Scam detected from {message.author.mention}\n"
                f"Confidence: {result['confidence_score']:.0%}\n"
                f"Type: {result['extracted_intelligence'].get('scam_type', 'Unknown')}"
            )


# Example 6: Batch Processing
# ----------------------------

def process_message_batch(messages: list):
    """Process multiple messages in batch."""
    results = []
    
    for msg in messages:
        result = analyze_scam_message(
            message=msg['text'],
            conversation_id=msg['id']
        )
        
        if result['scam_detected']:
            results.append({
                'message_id': msg['id'],
                'confidence': result['confidence_score'],
                'intelligence': result['extracted_intelligence'],
                'type': result['extracted_intelligence'].get('scam_type')
            })
    
    return results


# Example 7: Integration with Telegram Bot
# -----------------------------------------

from telegram import Update
from telegram.ext import Application, MessageHandler, filters

async def handle_telegram_message(update: Update, context):
    """Handle incoming Telegram messages."""
    message_text = update.message.text
    user_id = update.message.from_user.id
    
    # Analyze with honey-pot
    response = requests.post(
        "http://localhost:8000/api/analyze",
        headers={"X-API-Key": "your-secret-api-key-here"},
        json={
            "conversation_id": str(user_id),
            "message": message_text,
            "conversation_history": []
        }
    )
    
    result = response.json()
    
    if result['scam_detected']:
        await update.message.reply_text(
            "🚨 SCAM ALERT!\n\n"
            f"Confidence: {result['confidence_score']:.0%}\n"
            f"This message has been flagged as a potential scam."
        )


# Example 8: Real-time Dashboard Data
# ------------------------------------

def get_scam_statistics():
    """Get aggregated scam statistics."""
    # This would typically query a database
    # For demo purposes, showing the structure
    
    return {
        "total_conversations": 1523,
        "scams_detected": 847,
        "detection_rate": 0.556,
        "top_scam_types": [
            {"type": "prize_scam", "count": 234},
            {"type": "investment", "count": 198},
            {"type": "tech_support", "count": 176}
        ],
        "intelligence_extracted": {
            "bank_accounts": 432,
            "upi_ids": 567,
            "phishing_urls": 789,
            "phone_numbers": 345
        }
    }


# Example 9: Custom Intelligence Extraction
# ------------------------------------------

def extract_custom_patterns(text: str):
    """Extract additional custom patterns from text."""
    import re
    
    patterns = {
        'wallet_addresses': re.compile(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'),  # Bitcoin
        'ifsc_codes': re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b'),  # Indian IFSC
        'pan_numbers': re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'),  # Indian PAN
    }
    
    results = {}
    for name, pattern in patterns.items():
        matches = pattern.findall(text)
        if matches:
            results[name] = matches
    
    return results


if __name__ == "__main__":
    # Test basic integration
    result = analyze_scam_message(
        message="Congratulations! You won $10,000! Send your bank details.",
        conversation_id="test_123"
    )
    
    print(f"Scam Detected: {result['scam_detected']}")
    print(f"Agent Response: {result['response']}")
    print(f"Extracted Intelligence: {result['extracted_intelligence']}")
