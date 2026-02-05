"""Conversation memory management."""
from typing import Dict, Optional
import time


class ConversationMemory:
    """Manages conversation state and history."""
    
    def __init__(self):
        # In-memory storage for conversations
        # In production, this should use Redis or a database
        self.conversations: Dict[str, Dict] = {}
        
        # Cleanup old conversations periodically
        self.max_age = 3600  # 1 hour
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Retrieve conversation context by ID.
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            Conversation context dictionary or None
        """
        if conversation_id in self.conversations:
            conversation = self.conversations[conversation_id]
            
            # Check if conversation is still valid
            if time.time() - conversation.get("start_time", 0) < self.max_age:
                return conversation
            else:
                # Remove expired conversation
                del self.conversations[conversation_id]
                return None
        
        return None
    
    def update_conversation(self, conversation_id: str, context: Dict) -> None:
        """
        Update conversation context.
        
        Args:
            conversation_id: Unique conversation identifier
            context: Updated conversation context
        """
        self.conversations[conversation_id] = context
    
    def delete_conversation(self, conversation_id: str) -> None:
        """
        Delete a conversation from memory.
        
        Args:
            conversation_id: Unique conversation identifier
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def cleanup_expired(self) -> int:
        """
        Remove expired conversations.
        
        Returns:
            Number of conversations removed
        """
        current_time = time.time()
        expired = []
        
        for conv_id, context in self.conversations.items():
            if current_time - context.get("start_time", 0) >= self.max_age:
                expired.append(conv_id)
        
        for conv_id in expired:
            del self.conversations[conv_id]
        
        return len(expired)
    
    def get_active_count(self) -> int:
        """
        Get the number of active conversations.
        
        Returns:
            Number of active conversations
        """
        return len(self.conversations)
    
    def get_conversation_summary(self, conversation_id: str) -> Optional[Dict]:
        """
        Get a summary of the conversation.
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            Summary dictionary with key metrics
        """
        conversation = self.get_conversation(conversation_id)
        
        if not conversation:
            return None
        
        current_time = time.time()
        duration = current_time - conversation.get("start_time", current_time)
        
        return {
            "conversation_id": conversation_id,
            "turn_count": conversation.get("turn_count", 0),
            "duration_seconds": round(duration, 2),
            "scam_detected": conversation.get("scam_detected", False),
            "engagement_active": conversation.get("engagement_active", False),
            "scam_type": conversation.get("scam_type"),
            "strategy": conversation.get("strategy", "assess")
        }
