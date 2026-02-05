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
            # Log the error for debugging
            print(f"⚠️  AI generation failed (turn {turn_count}): {str(e)[:100]}")
            # Fallback response with variety based on message content
            return {
                "response": self._get_contextual_fallback(message, turn_count, scam_type),
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
        except Exception as e:
            print(f"⚠️  Neutral response AI failed: {str(e)[:100]}")
            # Vary the fallback based on hash of message
            seed = hash(message) % 5
            fallbacks = [
                "I'm here! What's going on? Can you explain?",
                "Yes, I saw your message. What do you need from me?",  
                "I'm available now. Tell me what this is about?",
                "Hello! I'm paying attention. What happened?",
                "I'm listening. Can you give me more details?"
            ]
            return fallbacks[seed]
    
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
    
    def _get_contextual_fallback(self, message: str, turn_count: int, scam_type: Optional[str]) -> str:
        """Get a contextual fallback response based on message content and turn."""
        message_lower = message.lower()
        
        # Hash message and turn to get consistent but varied responses
        seed = hash(message + str(turn_count)) % 100
        
        # Check message keywords for context
        has_otp = 'otp' in message_lower or 'code' in message_lower
        has_account = 'account' in message_lower or 'bank' in message_lower
        has_urgent = 'urgent' in message_lower or 'immediately' in message_lower or 'minutes' in message_lower
        has_upi = 'upi' in message_lower
        
        responses = []
        
        # Early turns (1-3) - confusion and questions
        if turn_count <= 3:
            if has_otp:
                responses = [
                    "Oh! I got an OTP just now. Is that what you mean? Which digits exactly?",
                    "Wait, I received a code on my phone. That's the OTP? All of it?",
                    "I see a 6-digit code here. Should I tell you this?"
                ]
            elif has_account:
                responses = [
                    "My account? Which one - SBI or HDFC? I have both.",
                    "Oh no! What's wrong with my account? Which bank?",
                    "Wait, which account number - savings or current?"
                ]
            elif has_urgent:
                responses = [
                    "Oh my god, this is urgent? What should I do first?",
                    "I'm worried now! Tell me quickly what to do!",
                    "Okay okay, I'm here! What details do you need?"
                ]
            else:
                responses = [
                    "I'm listening. Can you explain what happened?",
                    "Wait, I don't understand. What is this about?",
                    "Can you tell me more? I want to help."
                ]
        
        # Middle turns (4-7) - showing willingness
        elif turn_count <= 7:
            if has_upi:
                responses = [
                    "UPI ID? Mine is something like myname@paytm I think. Is that right?",
                    "I use PhonePe. What UPI details do you need exactly?",
                    "Should I give you my UPI ID? What's yours so I can send?"
                ]
            elif has_otp:
                responses = [
                    "The OTP is 6 digits. Should I read all of them?",
                    "It says 'OTP: XXXXXX valid for 10 minutes' - that one?",
                    "I'm ready to share the code. Where should I send it?"
                ]
            elif has_account:
                responses = [
                    "My account number... it starts with 4571. Is that the right one?",
                    "Should I get my passbook? The number is written there.",
                    "I think it's a 16-digit number. Which format do you need?"
                ]
            else:
                responses = [
                    "I'm ready to do whatever you need. Just guide me.",
                    "Tell me the exact steps. I don't want to mess this up.",
                    "What information do you need first?"
                ]
        
        # Later turns (8+) - urgency and compliance
        else:
            responses = [
                "I don't have much time! Just tell me - what exact details?",
                "Please help me fix this quickly! What do I send where?",
                "I'm getting more SMS codes. Should I forward them all to you?",
                "Can we do this on WhatsApp? What's your number?",
                "My friend said I should verify with bank first, but you ARE the bank right?",
                "How much more information do you need? I want to close this today."
            ]
        
        # Choose response based on seed for variety
        if responses:
            return responses[seed % len(responses)]
        
        # Ultimate fallback
        return "Tell me what you need. I'm ready to help."
    
    def _get_fallback_response(self, turn_count: int) -> str:
        """Legacy fallback - kept for compatibility."""
        return self._get_contextual_fallback("", turn_count, None)
