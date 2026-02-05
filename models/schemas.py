"""Data models and schemas for the honey-pot system."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    """A single message in a conversation."""
    role: str = Field(..., description="Role of the message sender (scammer or agent)")
    message: str = Field(..., description="The message content")


class AnalyzeRequest(BaseModel):
    """Request model for message analysis."""
    conversation_id: str = Field(..., description="Unique identifier for the conversation")
    message: str = Field(..., description="The incoming message to analyze")
    conversation_history: Optional[List[ConversationMessage]] = Field(
        default=[],
        description="Previous messages in the conversation"
    )


class ExtractedIntelligence(BaseModel):
    """Intelligence extracted from the conversation."""
    bank_accounts: List[str] = Field(default=[], description="Extracted bank account numbers")
    upi_ids: List[str] = Field(default=[], description="Extracted UPI IDs")
    phishing_urls: List[str] = Field(default=[], description="Extracted phishing URLs")
    phone_numbers: List[str] = Field(default=[], description="Extracted phone numbers")
    email_addresses: List[str] = Field(default=[], description="Extracted email addresses")
    scam_indicators: List[str] = Field(default=[], description="Detected scam indicators")
    scam_type: Optional[str] = Field(None, description="Type of scam detected")


class ResponseMetadata(BaseModel):
    """Metadata about the response and engagement."""
    engagement_duration_seconds: float = Field(..., description="Duration of engagement")
    detection_method: str = Field(..., description="Method used for detection")
    agent_strategy: str = Field(..., description="Strategy used by the agent")
    model_used: str = Field(..., description="AI model used")


class AnalyzeResponse(BaseModel):
    """Response model for message analysis."""
    conversation_id: str = Field(..., description="Unique identifier for the conversation")
    scam_detected: bool = Field(..., description="Whether a scam was detected")
    confidence_score: float = Field(..., description="Confidence score (0.0-1.0)")
    response: str = Field(..., description="Agent's response to the scammer")
    engagement_active: bool = Field(..., description="Whether engagement is still active")
    turn_count: int = Field(..., description="Number of conversation turns")
    extracted_intelligence: ExtractedIntelligence = Field(..., description="Extracted intelligence")
    metadata: ResponseMetadata = Field(..., description="Response metadata")


class DetectionResult(BaseModel):
    """Result of scam detection analysis."""
    is_scam: bool
    confidence: float
    indicators: List[str]
    scam_type: Optional[str] = None
