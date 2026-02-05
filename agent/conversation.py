"""Conversation agent for engaging scammers."""
import random
from typing import List, Dict, Optional
from utils.ai_client import AIClient
from config import config


class ConversationAgent:
    """AI agent that engages scammers in conversation to extract intelligence."""
    
    def __init__(self):
        self.ai_client = AIClient()
        
        # Different personas the agent can adopt
        self.personas = {
            "elderly": "You are a 65-year-old retiree who is not very tech-savvy but wants to be helpful. You're cautious but trusting of authority figures.",
            "young": "You are a 25-year-old professional who is busy and excited about opportunities. You tend to act quickly when something seems good.",
            "busy_parent": "You are a 40-year-old parent who is very busy and looking for quick solutions. You're stressed and might not think things through.",
            "tech_novice": "You are someone who doesn't understand technology well and gets confused easily. You ask a lot of basic questions."
        }
        
        # Strategy templates
        self.strategies = {
            "assess": "Be cautious but curious. Ask clarifying questions.",
            "build_trust": "Show interest and willingness to help. Build rapport.",
            "extract": "Ask specific questions about payment methods, accounts, and links.",
            "urgent_response": "Express concern and urgency. Ask what to do next.",
            "confused": "Act confused and ask for more details and clarification."
        }
    
    async def generate_response(
        self,
        message: str,
        conversation_history: List[Dict],
        turn_count: int,
        scam_type: Optional[str] = None,
        strategy: str = "assess"
    ) -> Dict[str, str]:
        """
        Generate an engaging response to the scammer.
        
        Args:
            message: The scammer's message
            conversation_history: Previous conversation
            turn_count: Current turn number
            scam_type: Type of scam detected
            strategy: Current engagement strategy
            
        Returns:
            Dictionary with response and next strategy
        """
        # Select persona based on scam type
        persona = self._select_persona(scam_type, turn_count)
        
        # Determine next strategy based on turn count
        next_strategy = self._determine_next_strategy(turn_count, strategy)
        
        # Build conversation context
        history_text = self._format_history(conversation_history[-8:])
        
        # Create strategy-specific instructions
        strategy_instruction = self._get_strategy_instruction(strategy, turn_count)
        
        # Prepare prompt
        messages = [
            {
                "role": "system",
                "content": f"""{config.AGENT_SYSTEM_PROMPT}

PERSONA: {persona}

CURRENT STRATEGY: {strategy_instruction}

CONVERSATION TURN: {turn_count}

Remember:
- Keep responses natural and concise (1-3 sentences)
- Never break character or reveal detection
- Gradually escalate engagement
- Extract information naturally through questions
- Show appropriate emotions for the situation"""
            },
            {
                "role": "user",
                "content": f"""Conversation History:
{history_text}

Scammer's Latest Message:
{message}

Generate a natural response that maintains your persona and follows the current strategy."""
            }
        ]
        
        try:
            response = await self.ai_client.generate_completion(
                messages=messages,
                temperature=0.8,
                max_tokens=200
            )
            
            # Clean up response
            response = response.strip().strip('"').strip("'")
            
            return {
                "response": response,
                "next_strategy": next_strategy,
                "persona": persona
            }
            
        except Exception as e:
            # Fallback response
            return {
                "response": self._get_fallback_response(turn_count),
                "next_strategy": next_strategy,
                "persona": persona
            }
    
    async def generate_neutral_response(self, message: str) -> str:
        """
        Generate a neutral response before scam detection.
        
        Args:
            message: The incoming message
            
        Returns:
            Neutral response string
        """
        message_lower = message.lower()
        
        # Context-aware responses based on message content
        # Banking/Account related
        if any(word in message_lower for word in ['bank', 'account', 'blocked', 'suspended', 'locked']):
            responses = [
                "Oh no! Which bank is this? What happened to my account?",
                "Wait, what? My account is having issues? Which one?",
                "This is serious! What do I need to do? Which bank are you from?",
                "I'm worried now. Can you tell me more about this?"
            ]
            return random.choice(responses)
        
        # OTP/Verification related
        if any(word in message_lower for word in ['otp', 'verify', 'code', 'verification']):
            responses = [
                "OTP? I just received something. What is this for?",
                "Wait, what verification? Can you explain what's happening?",
                "I'm not sure I understand. What do I need to verify?",
                "I got some code on my phone. Is that what you mean?"
            ]
            return random.choice(responses)
        
        # Urgent/Time pressure
        if any(word in message_lower for word in ['urgent', 'immediately', 'now', 'hurry', 'minutes', 'hours']):
            responses = [
                "Oh gosh, this sounds urgent! What do I need to do?",
                "Okay, I'm here now. What's the emergency?",
                "This sounds serious. Tell me what I should do right away.",
                "I'm paying attention! What are the steps I need to follow?"
            ]
            return random.choice(responses)
        
        # Prize/Money/Investment
        if any(word in message_lower for word in ['won', 'prize', 'money', 'earn', 'profit', 'investment']):
            responses = [
                "Really? That sounds interesting! How does this work?",
                "Wow! Can you tell me more about this?",
                "This sounds great! What do I need to do to get started?",
                "I could use some extra money. What's involved?"
            ]
            return random.choice(responses)
        
        # For simple greetings
        if any(word in message_lower for word in ['hi', 'hello', 'hey', 'greetings']) and len(message) < 20:
            return random.choice([
                "Hello! How can I help you?",
                "Hi there! What's this about?",
                "Hello! Yes, I'm here. What's going on?"
            ])
        
        # Otherwise, generate contextual response with AI
        messages = [
            {
                "role": "system",
                "content": "You are a concerned person responding to a message. Show interest and ask a clarifying question. Be helpful and engaged. Keep it brief (1-2 sentences)."
            },
            {
                "role": "user",
                "content": f"Respond naturally to this message: {message}"
            }
        ]
        
        try:
            response = await self.ai_client.generate_completion(
                messages=messages,
                temperature=0.8,
                max_tokens=100
            )
            return response.strip()
        except:
            # Better fallback that shows engagement
            return "I'm here! Can you explain what this is about? What do you need from me?"
    
    def _select_persona(self, scam_type: Optional[str], turn_count: int) -> str:
        """Select appropriate persona based on scam type."""
        if scam_type == "tech_support":
            return self.personas["tech_novice"]
        elif scam_type == "investment" or scam_type == "cryptocurrency":
            return self.personas["young"]
        elif scam_type == "government" or scam_type == "authority":
            return self.personas["elderly"]
        elif turn_count <= 3:
            return self.personas["busy_parent"]
        else:
            return random.choice(list(self.personas.values()))
    
    def _determine_next_strategy(self, turn_count: int, current_strategy: str) -> str:
        """Determine the next engagement strategy."""
        if turn_count <= 2:
            return "assess"
        elif turn_count <= 4:
            return "build_trust"
        elif turn_count <= 8:
            return "extract"
        elif turn_count % 3 == 0:
            return "confused"
        else:
            return "extract"
    
    def _get_strategy_instruction(self, strategy: str, turn_count: int) -> str:
        """Get detailed instructions for the current strategy."""
        instructions = {
            "assess": f"Ask clarifying questions to understand what they want. Show curiosity but not commitment. This is turn {turn_count}, so be naturally cautious.",
            
            "build_trust": f"Show interest and willingness to help. Express emotions (excitement, concern). Start showing you're willing to participate. Ask 'how does this work?'",
            
            "extract": f"Ask specific questions about: payment methods (which bank? UPI ID?), where to send money, which links to click, contact information. Be direct but natural: 'What's your UPI ID?' or 'Which website should I use?'",
            
            "urgent_response": "Mirror their urgency. Say you want to help but need specific details to proceed. Ask 'what exactly should I do right now?'",
            
            "confused": "Act confused about technical details or process. This prompts them to over-explain and share more information. Ask for clarification on every step."
        }
        
        return instructions.get(strategy, instructions["extract"])
    
    def _format_history(self, history: List[Dict]) -> str:
        """Format conversation history for context."""
        formatted = []
        for msg in history:
            role = "Them" if msg.get("role") == "scammer" else "You"
            content = msg.get("message", "")
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)
    
    def _get_fallback_response(self, turn_count: int) -> str:
        """Get a fallback response if AI generation fails."""
        # Early turns - show interest and confusion
        if turn_count <= 2:
            responses = [
                "Oh my! This sounds serious. What bank is this regarding?",
                "Wait, I need to understand this better. Can you explain what's happening?",
                "I'm concerned now. What exactly do I need to do?"
            ]
        # Middle turns - ask for specifics
        elif turn_count <= 5:
            responses = [
                "Okay, I want to help. Which account number do you need? The one ending in what?",
                "I'm ready to fix this. What information exactly do you need from me?",
                "Should I check my bank app? Which bank are we talking about?",
                "The OTP I received - is that what you need? What number?",
                "Tell me step by step what I should do. I don't want to make a mistake."
            ]
        # Later turns - show urgency and willingness
        else:
            responses = [
                "I don't want my account blocked! Where do I send the details?",
                "I have the OTP here. Should I share it now? What's your number?",
                "How much time do I have left? I'm ready to do this now.",
                "Which website should I use? Can you send me the link?",
                "What's your UPI ID? I can send the payment right away.",
                "Should I go to the bank? Or can we fix this now?"
            ]
        
        return random.choice(responses)
