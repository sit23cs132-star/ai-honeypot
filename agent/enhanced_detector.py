"""Enhanced scam detection module with production-grade rules and patterns."""
import re
import json
from typing import List, Dict, Tuple, Set, Optional
from pathlib import Path
from models.schemas import DetectionResult


class EnhancedScamDetector:
    """
    Production-grade scam detector with comprehensive pattern matching,
    psychological trigger analysis, and adaptive confidence scoring.
    """
    
    def __init__(self, library_path: str = "scam_case_library.json"):
        """Initialize detector with scam case library."""
        self.library = self._load_scam_library(library_path)
        self.scam_types = self.library.get("scam_types", [])
        self.compiled_patterns = self._compile_patterns()
        
        # Contextual weights for different indicators (increased regex weight)
        self.indicator_weights = {
            "keyword_match": 0.12,
            "regex_match": 0.35,  # Increased from 0.25
            "psychological_trigger": 0.18,
            "intent_signal": 0.20,
            "entity_extraction": 0.15
        }
        
        # Dynamic thresholds by risk level
        self.confidence_thresholds = {
            "critical": 0.40,  # Lower threshold for critical risks
            "high": 0.48,
            "medium": 0.55,
            "low": 0.60
        }
        
        # Whitelist patterns for false positive reduction
        self.whitelist = self._initialize_whitelist()
    
    def _load_scam_library(self, library_path: str) -> Dict:
        """Load scam case library from JSON file."""
        try:
            path = Path(library_path)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load scam library: {e}")
        
        return {"scam_types": []}
    
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Pre-compile all regex patterns for performance."""
        compiled = {}
        
        for scam_type in self.scam_types:
            scam_id = scam_type.get("scam_type", "UNKNOWN")
            patterns = scam_type.get("regex_patterns", [])
            
            compiled[scam_id] = []
            for pattern in patterns:
                try:
                    compiled[scam_id].append(re.compile(pattern, re.IGNORECASE))
                except re.error as e:
                    print(f"Warning: Invalid regex in {scam_id}: {pattern} - {e}")
        
        return compiled
    
    def _initialize_whitelist(self) -> Dict[str, List[str]]:
        """Initialize whitelist patterns for legitimate communications."""
        return {
            "domains": [
                r"\.gov\.in$",  # Government domains
                r"^(www\.)?(hdfc|icici|sbi|axis)bank\.com$",  # Major banks
                r"^(www\.)?(amazon|flipkart)\.in$",  # E-commerce
                r"^(www\.)?(paytm|phonepe|googlepay)\.com$"  # Payment apps
            ],
            "sender_ids": [
                "HDFCBK", "ICICIB", "SBINB", "AXIBNK",  # Bank SMS sender IDs
                "AMZNIN", "FLIPKT", "PAYTM", "PHONEPE"
            ],
            "keywords": [
                "order confirmed", "booking confirmed", "payment successful",
                "transaction alert", "OTP for login", "your appointment"
            ]
        }
    
    def detect_scam(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None,
        sender_info: Optional[Dict] = None
    ) -> DetectionResult:
        """
        Comprehensive scam detection with multi-layer analysis.
        
        Args:
            message: The message to analyze
            conversation_history: Previous messages (for context)
            sender_info: Sender metadata (phone, email, sender_id, etc.)
        
        Returns:
            DetectionResult with detection outcome
        """
        # Quick whitelist check
        if self._is_whitelisted(message, sender_info):
            return DetectionResult(
                is_scam=False,
                confidence=0.1,
                indicators=["whitelisted"],
                scam_type=None
            )
        
        # Multi-layer detection
        keyword_score, keyword_indicators = self._keyword_detection(message)
        regex_score, regex_indicators, matched_scams = self._regex_detection(message)
        psych_score, psych_triggers = self._psychological_trigger_detection(message)
        entity_score, entities = self._entity_extraction(message)
        
        # Determine most likely scam type
        scam_type, type_confidence = self._identify_scam_type(matched_scams)
        
        # Calculate composite confidence score
        confidence = self._calculate_confidence(
            keyword_score,
            regex_score,
            psych_score,
            entity_score,
            type_confidence,
            scam_type
        )
        
        # Apply multi-indicator bonus
        num_indicators = len(regex_indicators) + len(psych_triggers) + len(entities)
        if num_indicators >= 3:
            confidence += 0.10  # Bonus for multiple strong indicators
        if num_indicators >= 5:
            confidence += 0.08  # Additional bonus
        
        # Apply contextual adjustments
        confidence = self._apply_contextual_adjustments(
            confidence,
            message,
            conversation_history,
            sender_info
        )
        
        # Collect all indicators
        all_indicators = list(set(
            keyword_indicators +
            regex_indicators +
            psych_triggers +
            [f"entities: {', '.join(entities)}" if entities else ""]
        ))
        
        # Determine threshold based on scam risk level
        threshold = self._get_threshold_for_scam_type(scam_type)
        
        # Determine if scam based on dynamic threshold
        is_scam = confidence >= threshold
        
        return DetectionResult(
            is_scam=is_scam,
            confidence=round(confidence, 3),
            indicators=[ind for ind in all_indicators if ind],
            scam_type=scam_type if is_scam else None
        )
    
    def _keyword_detection(self, message: str) -> Tuple[float, List[str]]:
        """Detect scam keywords across all scam types."""
        message_lower = message.lower()
        indicators = []
        score = 0.0
        keyword_matches = 0
        
        for scam_type in self.scam_types:
            keywords = scam_type.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    keyword_matches += 1
                    indicators.append(f"keyword: {keyword}")
        
        # Score based on number of keyword matches
        if keyword_matches > 0:
            # More matches = higher confidence, but with diminishing returns
            score = min(keyword_matches * 0.08, 0.9)
        
        return score, indicators[:10]  # Limit to top 10 indicators
    
    def _regex_detection(self, message: str) -> Tuple[float, List[str], List[str]]:
        """Apply regex patterns from scam library."""
        indicators = []
        matched_scams = []
        total_matches = 0
        
        for scam_type in self.scam_types:
            scam_id = scam_type.get("scam_type", "UNKNOWN")
            patterns = self.compiled_patterns.get(scam_id, [])
            
            matches_in_type = 0
            for pattern in patterns:
                if pattern.search(message):
                    matches_in_type += 1
                    total_matches += 1
                    indicators.append(f"pattern: {scam_id}")
            
            # If this scam type has multiple pattern matches, record it
            if matches_in_type >= 2:
                matched_scams.append((scam_id, matches_in_type))
        
        # Score based on total pattern matches (increased weight)
        score = min(total_matches * 0.30, 0.95)  # Increased from 0.15 - patterns are strong signals
        
        # Sort matched scams by number of matches
        matched_scams.sort(key=lambda x: x[1], reverse=True)
        matched_scam_ids = [scam_id for scam_id, _ in matched_scams]
        
        return score, indicators[:10], matched_scam_ids
    
    def _psychological_trigger_detection(self, message: str) -> Tuple[float, List[str]]:
        """Detect psychological manipulation tactics."""
        message_lower = message.lower()
        triggers = []
        score = 0.0
        
        # Define psychological trigger patterns
        trigger_patterns = {
            "urgency": [
                r"\b(urgent|immediately|right now|within \d+ hour|hurry|quick|asap|today only|expires today|last chance)\b",
                r"\b(before|deadline|limited time|act now|don't wait|time running out)\b"
            ],
            "fear": [
                r"\b(blocked|suspended|arrested|seized|frozen|terminated|cancelled|deactivate)\b",
                r"\b(lose|lost|theft|hack|fraud|scam|stolen|illegal|crime|police|court)\b"
            ],
            "authority": [
                r"\b(bank|rbi|government|police|court|officer|official|department|ministry)\b",
                r"\b(compliance|mandatory|required|regulation|law|legal|authorized)\b"
            ],
            "greed": [
                r"\b(won|winner|prize|reward|free|cashback|bonus|profit|earn|income)\b",
                r"\b(\d+%|guaranteed|risk-free|passive income|double|triple|jackpot)\b"
            ],
            "secrecy": [
                r"\b(don't tell|keep secret|confidential|private|between us|don't inform)\b",
                r"\b(don't call|don't contact|don't share|only you)\b"
            ],
            "social_proof": [
                r"\b(i made|i earned|my friend|everyone|thousands of people|success story)\b",
                r"\b(testimonial|proven|verified|trusted|recommended|join us)\b"
            ]
        }
        
        for trigger_type, patterns in trigger_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    triggers.append(f"trigger: {trigger_type}")
                    score += 0.18  # Increased from 0.15
                    break  # Count each trigger type only once
        
        score = min(score, 0.95)  # Cap at 0.95 (increased from 0.9)
        return score, list(set(triggers))
    
    def _entity_extraction(self, message: str) -> Tuple[float, List[str]]:
        """Extract suspicious entities (UPI IDs, phone numbers, URLs)."""
        entities = []
        score = 0.0
        
        # UPI ID pattern
        upi_pattern = r'\b[a-zA-Z0-9._-]+@(paytm|phonepe|okaxis|okicici|okhdfc|oksbi|ybl|axl|ibl|apl)\b'
        upi_matches = re.findall(upi_pattern, message, re.IGNORECASE)
        if upi_matches:
            entities.append(f"UPI_ID")
            score += 0.35  # Increased from 0.3
        
        # Phone number pattern (10-15 digits)
        phone_pattern = r'\b\d{10,15}\b'
        phone_matches = re.findall(phone_pattern, message)
        if phone_matches:
            entities.append("PHONE_NUMBER")
            score += 0.25  # Increased from 0.2
        
        # URL pattern
        url_pattern = r'http[s]?://[a-zA-Z0-9.-]+\.[a-z]{2,}'
        url_matches = re.findall(url_pattern, message, re.IGNORECASE)
        if url_matches:
            entities.append("URL")
            score += 0.35  # Increased from 0.3
        
        # Short URL pattern (high suspicion)
        short_url_pattern = r'\b(bit\.ly|tinyurl\.com|goo\.gl|t\.co|ow\.ly)/[a-zA-Z0-9]+'
        short_url_matches = re.findall(short_url_pattern, message, re.IGNORECASE)
        if short_url_matches:
            entities.append("SHORT_URL")
            score += 0.50  # Increased from 0.4 - short URLs very suspicious
        
        # Suspicious domain extensions
        suspicious_domain = r'\.(xyz|online|club|top|site|co\.in)\b'
        if re.search(suspicious_domain, message, re.IGNORECASE):
            entities.append("SUSPICIOUS_DOMAIN")
            score += 0.35  # Increased from 0.3
        
        # Bank account number (9-18 digits)
        account_pattern = r'\b\d{9,18}\b'
        account_matches = re.findall(account_pattern, message)
        if account_matches:
            entities.append("ACCOUNT_NUMBER")
            score += 0.25
        
        score = min(score, 0.95)  # Cap at 0.95
        return score, list(set(entities))
    
    def _identify_scam_type(self, matched_scams: List[str]) -> Tuple[Optional[str], float]:
        """Identify the most likely scam type."""
        if not matched_scams:
            return None, 0.0
        
        # Get the scam type with most matches
        top_scam = matched_scams[0]
        
        # Find confidence weight for this scam type
        for scam_type in self.scam_types:
            if scam_type.get("scam_type") == top_scam:
                confidence = scam_type.get("confidence_weight", 0.8)
                return top_scam, confidence
        
        return top_scam, 0.8
    
    def _calculate_confidence(
        self,
        keyword_score: float,
        regex_score: float,
        psych_score: float,
        entity_score: float,
        type_confidence: float,
        scam_type: Optional[str] = None
    ) -> float:
        """Calculate composite confidence score with critical scam boosting."""
        # Weighted average
        confidence = (
            keyword_score * self.indicator_weights["keyword_match"] +
            regex_score * self.indicator_weights["regex_match"] +
            psych_score * self.indicator_weights["psychological_trigger"] +
            entity_score * self.indicator_weights["entity_extraction"] +
            type_confidence * self.indicator_weights["intent_signal"]
        )
        
        # Apply boost for critical scam types with known detection issues
        critical_boost_types = [
            "CRYPTO_INVESTMENT_FRAUD",
            "QR_CODE_PAYMENT_TRAP",
            "PHISHING_LINKS",
            "TECH_SUPPORT_SCAM",
            "FAKE_REFUND_CHARGEBACK"
        ]
        
        if scam_type in critical_boost_types:
            confidence *= 1.20  # 20% boost for problematic types
        
        return min(confidence, 1.0)
    
    def _get_threshold_for_scam_type(self, scam_type: Optional[str]) -> float:
        """Get appropriate threshold based on scam type risk level."""
        if not scam_type:
            return 0.50  # Default threshold
        
        # Find risk level for this scam type
        for scam in self.scam_types:
            if scam.get("scam_type") == scam_type:
                risk = scam.get("risk_level", "medium")
                return self.confidence_thresholds.get(risk, 0.50)
        
        return 0.50  # Default
    
    def _apply_contextual_adjustments(
        self,
        confidence: float,
        message: str,
        conversation_history: Optional[List[Dict]],
        sender_info: Optional[Dict]
    ) -> float:
        """Apply contextual adjustments to confidence score."""
        adjusted_confidence = confidence
        
        # Adjustment 1: New vs established conversation
        if conversation_history and len(conversation_history) > 5:
            # Established conversation - slightly reduce sensitivity
            adjusted_confidence *= 0.95
        
        # Adjustment 2: Message length (very short messages less reliable)
        if len(message) < 20:
            adjusted_confidence *= 0.85
        
        # Adjustment 3: ALL CAPS (indicates urgency/scam)
        if message.isupper() and len(message) > 20:
            adjusted_confidence *= 1.1
        
        # Adjustment 4: Multiple exclamation marks
        if message.count('!') >= 3:
            adjusted_confidence *= 1.15
        
        # Adjustment 5: Sender info verification
        if sender_info:
            sender_id = sender_info.get("sender_id", "")
            # Known legitimate sender IDs
            if sender_id in self.whitelist["sender_ids"]:
                adjusted_confidence *= 0.5  # Significantly reduce
        
        # Adjustment 6: Time-based patterns (scammers often operate at odd hours)
        # This would require timestamp analysis - placeholder for future
        
        return min(adjusted_confidence, 1.0)
    
    def _is_whitelisted(self, message: str, sender_info: Optional[Dict]) -> bool:
        """Check if message matches whitelist patterns."""
        message_lower = message.lower()
        
        # Check whitelisted keywords
        for keyword in self.whitelist["keywords"]:
            if keyword in message_lower:
                return True
        
        # Check sender ID
        if sender_info:
            sender_id = sender_info.get("sender_id", "")
            if sender_id in self.whitelist["sender_ids"]:
                return True
        
        # Check domains
        for domain_pattern in self.whitelist["domains"]:
            if re.search(domain_pattern, message_lower):
                return True
        
        return False
    
    def get_scam_type_info(self, scam_type: str) -> Optional[Dict]:
        """Retrieve detailed information about a specific scam type."""
        for scam in self.scam_types:
            if scam.get("scam_type") == scam_type:
                return scam
        return None
    
    def get_statistics(self) -> Dict:
        """Get statistics about loaded scam library."""
        return {
            "total_scam_types": len(self.scam_types),
            "total_patterns": sum(
                len(scam.get("regex_patterns", []))
                for scam in self.scam_types
            ),
            "total_keywords": sum(
                len(scam.get("keywords", []))
                for scam in self.scam_types
            ),
            "library_version": self.library.get("metadata", {}).get("version", "unknown"),
            "last_updated": self.library.get("metadata", {}).get("last_updated", "unknown")
        }


class SmartRuleEngine:
    """
    Smart detection rule engine with adaptive thresholds and
    false positive prevention.
    """
    
    def __init__(self):
        self.detection_history = []
        self.false_positive_patterns = set()
        
    def add_detection_result(
        self,
        message: str,
        result: DetectionResult,
        is_false_positive: bool = False
    ):
        """Record detection result for continuous learning."""
        self.detection_history.append({
            "message": message,
            "result": result,
            "is_false_positive": is_false_positive,
            "timestamp": None  # Add timestamp in production
        })
        
        if is_false_positive:
            # Learn from false positives
            self._update_false_positive_patterns(message, result)
    
    def _update_false_positive_patterns(
        self,
        message: str,
        result: DetectionResult
    ):
        """Update false positive patterns to improve accuracy."""
        # Extract patterns that led to false positive
        for indicator in result.indicators:
            self.false_positive_patterns.add(indicator)
    
    def get_adjusted_confidence(
        self,
        result: DetectionResult,
        message: str
    ) -> float:
        """Adjust confidence based on historical false positive patterns."""
        adjusted_confidence = result.confidence
        
        # Check if current indicators match known false positive patterns
        fp_matches = sum(
            1 for ind in result.indicators
            if ind in self.false_positive_patterns
        )
        
        if fp_matches > 0:
            # Reduce confidence based on false positive matches
            reduction_factor = 1.0 - (fp_matches * 0.1)
            adjusted_confidence *= max(reduction_factor, 0.5)
        
        return adjusted_confidence
    
    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics from detection history."""
        if not self.detection_history:
            return {}
        
        total = len(self.detection_history)
        false_positives = sum(
            1 for record in self.detection_history
            if record["is_false_positive"]
        )
        
        return {
            "total_detections": total,
            "false_positives": false_positives,
            "false_positive_rate": false_positives / total if total > 0 else 0,
            "accuracy": 1 - (false_positives / total) if total > 0 else 0
        }
