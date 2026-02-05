"""API routes for the honey-pot system."""
from fastapi import APIRouter, Header, HTTPException, Depends
from typing import Optional
import time

from models.schemas import AnalyzeRequest, AnalyzeResponse
from agent.detector import ScamDetector
from agent.conversation import ConversationAgent
from agent.extractor import IntelligenceExtractor
from utils.memory import ConversationMemory
from config import config

router = APIRouter()

# Initialize components
scam_detector = ScamDetector()
conversation_agent = ConversationAgent()
intelligence_extractor = IntelligenceExtractor()
conversation_memory = ConversationMemory()


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify the API key from request headers."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key is required")
    
    if x_api_key != config.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return x_api_key


@router.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_message(
    request: Optional[AnalyzeRequest] = None,
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze an incoming message for scam detection and generate appropriate response.
    
    This endpoint:
    1. Detects if the message is a scam
    2. Engages the scammer if detected
    3. Extracts intelligence from the conversation
    4. Returns structured response
    """
    start_time = time.time()
    
    try:
        # Handle missing request body (for basic endpoint testers)
        if request is None:
            request = AnalyzeRequest(
                conversation_id="test",
                message="test message"
            )
        
        # Get or initialize conversation context
        conversation_context = conversation_memory.get_conversation(request.conversation_id)
        if not conversation_context:
            conversation_context = {
                "turn_count": 0,
                "start_time": start_time,
                "scam_detected": False,
                "engagement_active": False,
                "strategy": "assess"
            }
        
        # Update conversation history - convert Pydantic models to dicts
        conversation_history = []
        for msg in (request.conversation_history or []):
            if isinstance(msg, dict):
                conversation_history.append(msg)
            else:
                conversation_history.append(msg.model_dump())
        
        conversation_history.append({
            "role": "scammer",
            "message": request.message
        })
        
        # Update turn count
        conversation_context["turn_count"] += 1
        turn_count = conversation_context["turn_count"]
        
        # Detect scam intent
        detection_result = await scam_detector.detect_scam(
            message=request.message,
            conversation_history=conversation_history
        )
        
        # Update scam detection status
        if detection_result.is_scam and not conversation_context["scam_detected"]:
            conversation_context["scam_detected"] = True
            conversation_context["engagement_active"] = True
            conversation_context["scam_type"] = detection_result.scam_type
        
        scam_detected = conversation_context["scam_detected"]
        engagement_active = conversation_context["engagement_active"]
        
        # Generate response
        if scam_detected and engagement_active:
            # Engage scammer with AI agent
            agent_response = await conversation_agent.generate_response(
                message=request.message,
                conversation_history=conversation_history,
                turn_count=turn_count,
                scam_type=detection_result.scam_type,
                strategy=conversation_context["strategy"]
            )
            
            # Update strategy for next turn
            conversation_context["strategy"] = agent_response.get("next_strategy", "extract")
            
            response_text = agent_response["response"]
        else:
            # Neutral response before detection
            response_text = await conversation_agent.generate_neutral_response(
                message=request.message
            )
        
        # Extract intelligence from entire conversation
        extracted_intelligence = await intelligence_extractor.extract_intelligence(
            conversation_history=conversation_history + [{
                "role": "agent",
                "message": response_text
            }],
            scam_indicators=detection_result.indicators if scam_detected else []
        )
        
        # Add scam type to extracted intelligence
        if scam_detected and detection_result.scam_type:
            extracted_intelligence.scam_type = detection_result.scam_type
            extracted_intelligence.scam_indicators = detection_result.indicators
        
        # Check if engagement should end
        engagement_duration = time.time() - conversation_context["start_time"]
        if turn_count >= config.MAX_CONVERSATION_TURNS or engagement_duration >= config.ENGAGEMENT_TIMEOUT:
            conversation_context["engagement_active"] = False
            engagement_active = False
        
        # Update conversation memory
        conversation_memory.update_conversation(request.conversation_id, conversation_context)
        
        # Build response
        response = AnalyzeResponse(
            conversation_id=request.conversation_id,
            scam_detected=scam_detected,
            confidence_score=detection_result.confidence if scam_detected else 0.0,
            response=response_text,
            engagement_active=engagement_active,
            turn_count=turn_count,
            extracted_intelligence=extracted_intelligence,
            metadata={
                "engagement_duration_seconds": round(engagement_duration, 2),
                "detection_method": "ai_analysis",
                "agent_strategy": conversation_context["strategy"],
                "model_used": config.OPENAI_MODEL if config.AI_PROVIDER == "openai" else config.ANTHROPIC_MODEL
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "ai_provider": config.AI_PROVIDER
    }
