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
        # PRIORITY 1: OTP/Verification (most specific and critical)
        if any(word in message_lower for word in ['otp', 'verify', 'code', 'verification']):
            responses = [
                "Wait, I received a code on my phone. That's the OTP? All of it?",
                "Oh! I got an OTP just now. Is that what you mean? Which digits exactly?",
                "I see a 6-digit code here. Should I tell you this?",
                "OTP? I just received something. What exactly do I share?"
            ]
            return random.choice(responses)
        
        # PRIORITY 2: Banking/Account (after OTP check)
        if any(word in message_lower for word in ['bank', 'account', 'blocked', 'suspended', 'locked']):
            responses = [
                "Oh no! Which bank is this? What happened to my account?",
                "Wait, what? My account is having issues? Which one?",
                "This is serious! What do I need to do? Which bank are you from?",
                "I'm worried now. Can you tell me more about this?"
            ]
            return random.choice(responses)
        
        # PRIORITY 3: Urgent/Time pressure
        if any(word in message_lower for word in ['urgent', 'immediately', 'now', 'hurry', 'minutes', 'hours']):
            responses = [
                "Oh gosh, this sounds urgent! What do I need to do?",
                "Okay, I'm here now. What's the emergency?",
                "This sounds serious. Tell me what I should do right away.",
                "I'm paying attention! What are the steps I need to follow?"
            ]
            return random.choice(responses)
        
        # PRIORITY 4: Prize/Money/Investment
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
            # Use contextual fallback - ALWAYS check keywords for engagement
            from random import Random
            rng = Random(hash(message))
            
            # Context-aware responses based on message content
            message_lower = message.lower()
            
            # Priority 1: OTP/Code mentions (most common scam element)
            if any(word in message_lower for word in ['otp', 'code', 'verification code', 'pin code']):
                responses = [
                    "Wait, I received a code on my phone. That's the OTP? All of it?",
                    "Oh! I got an OTP just now. Is that what you mean? Which digits exactly?",
                    "I see a 6-digit code here. Should I tell you this?",
                    "The code on my screen - that's what you need? All 6 numbers?",
                    "I'm looking at the OTP. Do I read it to you or type it?"
                ]
                return rng.choice(responses)
            
            # Priority 2: UPI/PIN requests (high-risk)
            if any(word in message_lower for word in ['upi', 'pin', 'atm pin', 'cvv', 'card']):
                responses = [
                    "UPI PIN? I use PhonePe. Is it safe to share that?",
                    "My ATM PIN? I thought we should never share that...",
                    "Wait, you need my card details? Which ones exactly?",
                    "UPI ID or UPI PIN? I'm confused which one to give."
                ]
                return rng.choice(responses)
            
            # Priority 3: Account/Transfer mentions
            if 'transfer' in message_lower or 'transaction' in message_lower:
                responses = [
                    "A transfer? I didn't make any! How do I stop it?",
                    "Wait, someone is transferring money? From which account?",
                    "Oh no! What transaction? Tell me how to cancel it!",
                    "Transfer of how much money? This is scary!"
                ]
                return rng.choice(responses)
            
            # Priority 4: Account/Bank mentions (very common)
            if any(word in message_lower for word in ['account', 'bank', 'blocked', 'suspended', 'locked']):
                responses = [
                    "My account? Which one - SBI or HDFC? I have both.",
                    "Oh no! What's wrong with my account? Which bank?",
                    "Account blocked? Why? What should I do right now?",
                    "Wait, which account number do you need? I have several."
                ]
                return rng.choice(responses)
            
            # Priority 5: Email/Contact requests
            if 'email' in message_lower or '@' in message_lower or 'send to' in message_lower:
                responses = [
                    "Email to where? What's the address I should use?",
                    "Should I email the details? To which address?",
                    "What do I need to send via email? Everything?",
                    "I can send it now. What's your email address?"
                ]
                return rng.choice(responses)
            
            # Priority 6: Urgency/Time pressure (common tactic)
            if any(word in message_lower for word in ['urgent', 'immediately', 'now', 'quickly', 'minutes', 'hours', 'hurry']):
                responses = [
                    "Oh god, this is urgent! What do I do first?",
                    "Right now? Okay, I'm ready! Tell me what to send!",
                    "I'm worried now! Walk me through this quickly!",
                    "Okay okay, I'm here! What information exactly?"
                ]
                return rng.choice(responses)
            
            # Priority 7: Direct questions/instructions from scammer
            if any(word in message_lower for word in ['send', 'share', 'provide', 'give', 'tell']):
                responses = [
                    "Send what exactly? Can you list everything you need?",
                    "OK, I'm ready to share. What details first?",
                    "Tell me step by step what I should provide.",
                    "I'll give you whatever you need. What information?"
                ]
                return rng.choice(responses)
            
            # Default: Still contextual and helpful (never generic)
            responses = [
                "I'm listening carefully. What should I do?",
                "Can you explain more? I want to get this right.",
                "I'm ready to help fix this. What's the next step?",
                "Tell me exactly what information you need from me.",
                "I'm a bit confused but willing to help. Guide me?"
            ]
            return rng.choice(responses)
    
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
        
        # Check message keywords for context (comprehensive)
        has_otp = any(word in message_lower for word in ['otp', 'code', 'verification'])
        has_account = any(word in message_lower for word in ['account', 'bank'])
        has_transfer = any(word in message_lower for word in ['transfer', 'transaction'])
        has_urgent = any(word in message_lower for word in ['urgent', 'immediately', 'minutes', 'now', 'quickly'])
        has_upi = any(word in message_lower for word in ['upi', 'pin', 'cvv'])
        has_email = 'email' in message_lower or '@' in message_lower
        
        responses = []
        
        # ALWAYS prioritize OTP/Code mentions (most critical)
        if has_otp:
            responses = [
                "Wait, I received a code on my phone. That's the OTP? All of it?",
                "Oh! I got an OTP just now. Is that what you mean? Which digits exactly?",
                "I see a 6-digit code here. Should I tell you this?",
                "The code just came. Do I share all the numbers or just some?",
                "OTP received! Should I read it out or type it somewhere?"
            ]
        # UPI/PIN requests (high priority)
        elif has_upi:
            responses = [
                "UPI PIN? I use PhonePe. Is it safe to share that?",
                "My UPI ID is something like myname@paytm. That one?",
                "Do you need my UPI PIN or UPI ID? I have both.",
                "ATM PIN or UPI PIN? Tell me which one exactly."
            ]
        # Transfer/Transaction alerts
        elif has_transfer:
            responses = [
                "A transfer? I didn't make any! How do I stop it?",
                "Wait, someone is transferring money? From which account?",
                "Transaction? What amount? Tell me how to cancel it!",
                "Oh no! When did this transfer happen? Can we reverse it?"
            ]
        # Account/Bank mentions
        elif has_account:
            responses = [
                "My account? Which one - SBI or HDFC? I have both.",
                "Oh no! What's wrong with my account? Which bank?",
                "Account blocked? Why? What do I do to fix it?",
                "Which account number do you need? Savings or current?"
            ]
        # Email requests
        elif has_email:
            responses = [
                "Email to where? What's the address?",
                "Should I email everything? To which ID?",
                "What do I send via email? All my details?",
                "I can email now. What's your email address?"
            ]
        # Urgency/Time pressure
        elif has_urgent:
            responses = [
                "Oh god, this is urgent! What do I do first?",
                "Right now? I'm ready! Tell me what to send!",
                "I'm worried! Guide me through this quickly!",
                "Okay okay! What information do you need immediately?"
            ]
        # Default: Still contextual based on turn count
        elif turn_count <= 3:
            responses = [
                "I'm listening carefully. What should I do?",
                "Wait, I don't fully understand. Can you explain?",
                "Tell me more details. I want to help.",
                "What information do you need from me?"
            ]
        elif turn_count <= 7:
            responses = [
                "I'm ready to do whatever you need. Just guide me.",
                "Tell me the exact steps. I don't want to mess this up.",
                "What information do you need first?",
                "I have all my details ready. What should I share?"
            ]
        else:
            responses = [
                "Please help me fix this quickly! What do I send?",
                "I'm getting more messages. Should I forward them all?",
                "How much more information do you need?",
                "Just tell me exactly what to do. I'm ready."
            ]
        
        # Choose response based on seed for variety
        return responses[seed % len(responses)]
    
    def _get_fallback_response(self, turn_count: int) -> str:
        """Legacy fallback - kept for compatibility."""
        return self._get_contextual_fallback("", turn_count, None)
