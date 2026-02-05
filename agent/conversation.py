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
        neutral_responses = [
            "Hello! How can I help you?",
            "Hi there! What's this about?",
            "Hello! I'm here. What do you need?",
            "Hi! Yes, I'm available. What's going on?",
            "Hello! What can I do for you?",
            "Hi! I just saw your message. What's up?"
        ]
        
        # For simple greetings, use a template
        message_lower = message.lower()
        if any(word in message_lower for word in ['hi', 'hello', 'hey', 'greetings']):
            return random.choice(neutral_responses)
        
        # Otherwise, generate contextual response
        messages = [
            {
                "role": "system",
                "content": "You are a helpful person responding to a message. Be polite and neutral. Keep it brief (1-2 sentences)."
            },
            {
                "role": "user",
                "content": f"Respond to this message naturally: {message}"
            }
        ]
        
        try:
            response = await self.ai_client.generate_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=100
            )
            return response.strip()
        except:
            return random.choice(neutral_responses)
    
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
        responses = [
            "I'm interested, but can you explain more about how this works?",
            "That sounds good! What do I need to do exactly?",
            "I want to help, but I'm not sure I understand. Can you clarify?",
            "Okay, I'm listening. What's the next step?",
            "I'm a bit confused. Can you walk me through this step by step?",
            "Which bank account should I use for this?",
            "What website do I need to go to?",
            "How much time do I have to do this?",
            "Is there a specific link you can send me?",
            "What information do you need from me?"
        ]
        
        # Choose based on turn count for variety
        return responses[turn_count % len(responses)]
