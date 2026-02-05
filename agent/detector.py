"""Scam detection module."""
import re
from typing import List, Dict, Optional
from models.schemas import DetectionResult
from utils.ai_client import AIClient
from config import config

# Import enhanced detector (optional - will use if available)
try:
    from agent.enhanced_detector import EnhancedScamDetector
    ENHANCED_DETECTOR_AVAILABLE = True
except ImportError:
    ENHANCED_DETECTOR_AVAILABLE = False


class ScamDetector:
    """Detects scam intent in messages using AI and pattern matching."""
    
    def __init__(self, use_enhanced_detector: bool = True):
        self.ai_client = AIClient()
        self.use_enhanced = use_enhanced_detector and ENHANCED_DETECTOR_AVAILABLE
        
        # Initialize enhanced detector if available
        if self.use_enhanced:
            try:
                self.enhanced_detector = EnhancedScamDetector()
                print(f"✓ Enhanced detector loaded: {self.enhanced_detector.get_statistics()}")
            except Exception as e:
                print(f"Warning: Could not initialize enhanced detector: {e}")
                self.use_enhanced = False
        
        # Common scam keywords and patterns (legacy - kept for fallback)
        self.scam_keywords = [
            r'\b(urgent|immediately|act now|limited time|expire|hurry|don\'?t miss|hurry up)\b',
            r'\b(won|winner|prize|lottery|reward|gift|claim|congratulations)\b',
            r'\b(bank|account|credit card|debit card|cvv|pin|password|otp)\b',
            r'\b(verify|confirm|update|suspend|locked|blocked|compromised)\b',
            r'\b(refund|tax|customs|clearance|fee|payment|transfer)\b',
            r'\b(click here|link|website|download|install|app)\b',
            r'\b(investment|profit|returns|earn|income|opportunity|passive income)\b',
            r'\b(cryptocurrency|bitcoin|crypto|trading|forex|stocks|bot)\b',
            r'\b(loan|debt|credit score|financial help)\b',
            r'\b(romance scam|dating scam|love scam|lonely|soulmate)\b',
            r'\b(government|irs|tax authority|police|legal action)\b',
            r'\b(tech support|virus|infected|hacked|security)\b',
            r'\b(made \$\d+|earned \$\d+|join now|limited spots|guaranteed|risk[- ]?free)\b',
        ]
        
        # URL patterns
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        
    async def detect_scam(
        self,
        message: str,
        conversation_history: List[Dict],
        sender_info: Optional[Dict] = None
    ) -> DetectionResult:
        """
        Detect if a message is a scam attempt using hybrid detection.
        
        Args:
            message: The message to analyze
            conversation_history: Previous messages in the conversation
            sender_info: Optional sender metadata (phone, email, etc.)
            
        Returns:
            DetectionResult with detection outcome
        """
        # Fast-path detection for obvious scams (banking/OTP)
        fast_result = self._fast_path_detection(message)
        if fast_result:
            return fast_result
        
        # If enhanced detector is available, use hybrid approach
        if self.use_enhanced:
            return await self._hybrid_detection(message, conversation_history, sender_info)
        
        # Fallback to legacy detection
        return await self._legacy_detection(message, conversation_history)
    
    def _fast_path_detection(self, message: str) -> Optional[DetectionResult]:
        """
        Fast-path detection for obvious scams (banking, OTP, urgent account issues).
        Returns DetectionResult immediately for clear scams, None otherwise.
        """
        message_lower = message.lower()
        
        # Banking + OTP = Obvious phishing scam
        has_banking = any(word in message_lower for word in [
            'bank', 'account', 'sbi', 'hdfc', 'icici', 'axis', 
            'debit card', 'credit card', 'atm'
        ])
        has_otp = any(word in message_lower for word in [
            'otp', 'one time password', 'one-time password', 'verification code',
            'security code', 'pin', 'cvv'
        ])
        has_urgency = any(word in message_lower for word in [
            'urgent', 'immediately', 'blocked', 'suspended', 'locked',
            'compromised', 'expire', 'within', 'hours', 'minutes'
        ])
        
        # Banking phishing: bank + (OTP or urgency + account details)
        if has_banking and (has_otp or (has_urgency and 'account' in message_lower)):
            return DetectionResult(
                is_scam=True,
                confidence=0.95,
                indicators=['banking_keywords', 'otp_request', 'urgency', 'account_verification'],
                scam_type='banking_phishing'
            )
        
        # Another common pattern: Share/send + account number/OTP
        if ('share' in message_lower or 'send' in message_lower or 'provide' in message_lower):
            if (has_otp or 'account number' in message_lower or 'card number' in message_lower):
                return DetectionResult(
                    is_scam=True,
                    confidence=0.92,
                    indicators=['credential_request', 'otp_phishing', 'urgent_action'],
                    scam_type='phishing'
                )
        
        return None
    
    async def _hybrid_detection(
        self,
        message: str,
        conversation_history: List[Dict],
        sender_info: Optional[Dict] = None
    ) -> DetectionResult:
        """
        Hybrid detection combining enhanced pattern matching and AI.
        
        This provides the best of both worlds:
        - Fast pattern matching for known scam types
        - AI analysis for sophisticated/novel scams
        - Confidence score combining both methods
        """
        # 1. Enhanced pattern-based detection
        enhanced_result = self.enhanced_detector.detect_scam(
            message,
            conversation_history,
            sender_info
        )
        
        # 2. AI-based detection for sophisticated analysis
        ai_result = await self._ai_detection(message, conversation_history)
        ai_is_scam = ai_result.get("is_scam", False)
        ai_confidence = ai_result.get("confidence", 0.0)
        
        # 3. Combine results intelligently
        # If both agree on scam, take the higher confidence
        if enhanced_result.is_scam and ai_is_scam:
            final_confidence = max(enhanced_result.confidence, ai_confidence)
            is_scam = True
        
        # If one detects scam with high confidence, trust it
        elif enhanced_result.confidence >= 0.75:
            final_confidence = enhanced_result.confidence
            is_scam = True
        elif ai_confidence >= 0.75:
            final_confidence = ai_confidence
            is_scam = True
        
        # If both detect scam but with lower confidence, average them
        elif enhanced_result.is_scam or ai_is_scam:
            final_confidence = (enhanced_result.confidence + ai_confidence) / 2
            is_scam = final_confidence >= 0.50
        
        # If neither detects scam, not a scam
        else:
            final_confidence = min(enhanced_result.confidence, ai_confidence)
            is_scam = False
        
        # Combine indicators from both methods
        combined_indicators = list(set(
            enhanced_result.indicators +
            ai_result.get("indicators", [])
        ))
        
        # Prefer enhanced detector's scam type, fallback to AI
        scam_type = enhanced_result.scam_type or ai_result.get("scam_type")
        
        return DetectionResult(
            is_scam=is_scam,
            confidence=round(final_confidence, 3),
            indicators=combined_indicators,
            scam_type=scam_type
        )
    
    async def _legacy_detection(
        self,
        message: str,
        conversation_history: List[Dict]
    ) -> DetectionResult:
        """Legacy detection method (original implementation)."""
        # Quick pattern-based detection
        pattern_score, pattern_indicators = self._pattern_detection(message)
        
        # AI-based detection for more sophisticated analysis
        ai_result = await self._ai_detection(message, conversation_history)
        
        # Prioritize AI analysis over pattern matching
        ai_is_scam = ai_result.get("is_scam", False)
        ai_confidence = ai_result.get("confidence", 0.0)
        
        # Trust AI first - only use patterns if AI agrees or patterns are very strong
        if ai_is_scam:
            # AI detected scam - trust it
            is_scam = True
            confidence = max(ai_confidence, pattern_score)
        elif pattern_score >= 0.6:
            # Very high pattern score (multiple indicators) - likely scam even without AI
            is_scam = True
            confidence = pattern_score
        else:
            # AI says not scam and pattern score is low - trust AI
            is_scam = False
            confidence = ai_confidence
        
        indicators = list(set(pattern_indicators + ai_result.get("indicators", [])))
        scam_type = ai_result.get("scam_type")
        
        return DetectionResult(
            is_scam=is_scam,
            confidence=confidence,
            indicators=indicators,
            scam_type=scam_type
        )
    
    def _pattern_detection(self, message: str) -> tuple[float, List[str]]:
        """
        Pattern-based scam detection using keywords and heuristics.
        
        Returns:
            Tuple of (confidence_score, indicators_list)
        """
        message_lower = message.lower()
        indicators = []
        score = 0.0
        
        # Check for scam keywords - reduced from 0.2 to 0.15
        for pattern in self.scam_keywords:
            if re.search(pattern, message_lower):
                score += 0.15
                indicators.append(pattern.replace(r'\b', '').replace('(', '').replace(')', ''))
        
        # Check for URLs
        if self.url_pattern.search(message):
            score += 0.2
            indicators.append("contains_url")
        
        # Check for phone numbers
        phone_pattern = r'\b\d{10,15}\b|\b\+\d{1,3}[\s-]?\d{10,15}\b'
        if re.search(phone_pattern, message):
            score += 0.1
            indicators.append("contains_phone")
        
        # Check for urgency indicators
        urgency_words = ['urgent', 'immediately', 'now', 'hurry', 'asap', 'expire', 'deadline', 'limited time', 'act now']
        if any(word in message_lower for word in urgency_words):
            score += 0.3
            indicators.append("urgency_tactic")
        
        # Check for money-related terms
        money_words = ['money', 'payment', 'transfer', 'send', 'pay', 'bank', 'account', 'upi', 'paytm', 'prize', 'won', 'claim', '$', '₹', 'paid', 'profit', 'returns']
        if any(word in message_lower for word in money_words):
            score += 0.25
            indicators.append("money_request")
        
        # Check for testimonial/success story patterns
        testimonial_patterns = [
            r'i made \$?\d+',
            r'i earned \$?\d+', 
            r'\d+ in \d+ (days?|weeks?|months?)',
            r'join (now|today|us)',
            r'limited (spots?|members?|time)',
        ]
        for pattern in testimonial_patterns:
            if re.search(pattern, message_lower):
                score += 0.2
                indicators.append("testimonial_scam_pattern")
                break
        
        # Cap score at 1.0
        score = min(score, 1.0)
        
        return score, indicators
    
    async def _ai_detection(
        self,
        message: str,
        conversation_history: List[Dict]
    ) -> Dict:
        """
        AI-based scam detection using language model.
        
        Returns:
            Dictionary with detection results
        """
        # Build conversation context
        history_text = ""
        for msg in conversation_history[-5:]:  # Last 5 messages for context
            role = msg.get("role", "unknown")
            content = msg.get("message", "")
            history_text += f"{role}: {content}\n"
        
        # Prepare prompt
        messages = [
            {
                "role": "system",
                "content": config.DETECTION_PROMPT
            },
            {
                "role": "user",
                "content": f"""Conversation History:
{history_text}

Latest Message to Analyze:
{message}

Analyze this message and respond with JSON."""
            }
        ]
        
        try:
            result = await self.ai_client.generate_json_completion(messages)
            return result
        except Exception as e:
            # Fallback to safe defaults
            return {
                "is_scam": False,
                "confidence": 0.0,
                "indicators": [],
                "scam_type": None
            }
