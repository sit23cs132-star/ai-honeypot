"""Intelligence extraction module."""
import re
from typing import List, Dict, Set
from models.schemas import ExtractedIntelligence


class IntelligenceExtractor:
    """Extracts actionable intelligence from scam conversations."""
    
    def __init__(self):
        # Regex patterns for different types of intelligence
        self.patterns = {
            # Bank account: 9-18 digits
            "bank_account": re.compile(r'\b\d{9,18}\b'),
            
            # UPI ID: username@bank (e.g., john@paytm, user@oksbi)
            "upi_id": re.compile(r'\b[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\b'),
            
            # Phone numbers: various formats (including alphanumeric like 800-FAKE)
            "phone": re.compile(r'(\+?\d{1,3}[-\.\s]?)?\(?\d{3}\)?[-\.\s]?[\d]{3,4}[-\.\s]?[\d]{4}|\+?\d{1,3}[-\.\s]?\d{3}[-\.\s]?\d{3}[-\.\s]?[A-Z]{4}|\b\d{10,15}\b'),
            
            # Email addresses
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            
            # URLs (http/https)
            "url": re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            
            # Shortened URLs (bit.ly, tinyurl, etc.)
            "short_url": re.compile(r'\b(?:bit\.ly|tinyurl\.com|goo\.gl|t\.co|ow\.ly)/[a-zA-Z0-9]+\b'),
        }
        
        # Common UPI bank handles
        self.upi_handles = [
            'paytm', 'phonepe', 'googlepay', 'amazonpay', 'freecharge',
            'oksbi', 'okicici', 'okhdfc', 'okaxis', 'ybl', 'ibl', 'axl'
        ]
        
        # Keywords that indicate phishing/scam URLs
        self.suspicious_url_keywords = [
            'verify', 'secure', 'update', 'confirm', 'account', 'login',
            'banking', 'refund', 'prize', 'winner', 'claim', 'urgent'
        ]
    
    async def extract_intelligence(
        self,
        conversation_history: List[Dict],
        scam_indicators: List[str]
    ) -> ExtractedIntelligence:
        """
        Extract actionable intelligence from the conversation.
        
        Args:
            conversation_history: List of conversation messages
            scam_indicators: List of detected scam indicators
            
        Returns:
            ExtractedIntelligence object with all extracted data
        """
        # Combine all messages into text for analysis
        full_text = self._combine_messages(conversation_history)
        
        # Extract different types of intelligence
        bank_accounts = self._extract_bank_accounts(full_text)
        upi_ids = self._extract_upi_ids(full_text)
        phone_numbers = self._extract_phone_numbers(full_text)
        email_addresses = self._extract_emails(full_text)
        phishing_urls = self._extract_phishing_urls(full_text)
        
        return ExtractedIntelligence(
            bank_accounts=list(bank_accounts),
            upi_ids=list(upi_ids),
            phishing_urls=list(phishing_urls),
            phone_numbers=list(phone_numbers),
            email_addresses=list(email_addresses),
            scam_indicators=scam_indicators,
            scam_type=None  # Will be set by the caller
        )
    
    def _combine_messages(self, conversation_history: List[Dict]) -> str:
        """Combine all messages into a single text for extraction."""
        messages = []
        for msg in conversation_history:
            # Only extract from scammer messages
            if msg.get("role") == "scammer":
                messages.append(msg.get("message", ""))
        return " ".join(messages)
    
    def _extract_bank_accounts(self, text: str) -> Set[str]:
        """Extract bank account numbers from text."""
        accounts = set()
        
        # Find all number sequences
        matches = self.patterns["bank_account"].findall(text)
        
        for match in matches:
            # Filter out common false positives
            if len(match) >= 9 and len(match) <= 18:
                # Bank accounts are usually 12-18 digits
                # 10-11 digits are more likely phone numbers
                # 12+ digits are more likely bank accounts
                if len(match) >= 12 or not self._is_likely_phone(match):
                    accounts.add(match)
        
        return accounts
    
    def _extract_upi_ids(self, text: str) -> Set[str]:
        """Extract UPI IDs from text."""
        upi_ids = set()
        
        matches = self.patterns["upi_id"].findall(text)
        
        for match in matches:
            # Verify it's a UPI ID by checking the handle
            handle = match.split('@')[-1].lower()
            
            # Check if it matches known UPI handles
            if any(upi_handle in handle for upi_handle in self.upi_handles):
                upi_ids.add(match)
            # Also accept if it looks like a bank domain
            elif any(bank in handle for bank in ['bank', 'pay', 'wallet', 'upi']):
                upi_ids.add(match)
        
        return upi_ids
    
    def _extract_phone_numbers(self, text: str) -> Set[str]:
        """Extract phone numbers from text."""
        phone_numbers = set()
        
        # More comprehensive phone pattern including alphanumeric
        phone_patterns = [
            r'\+?\d{1,3}[-\.\s]?\d{3}[-\.\s]?\d{3}[-\.\s]?\d{4}',  # +1-800-555-1234
            r'\+?\d{1,3}[-\.\s]?\d{3}[-\.\s]?\d{3}[-\.\s]?[A-Z]{4}',  # +1-800-555-FAKE
            r'\+?\d{1,3}[-\.\s]?\(\d{3}\)[-\.\s]?\d{3}[-\.\s]?\d{4}',  # +1-(800)-555-1234
            r'\b\d{10}\b(?!\d)',  # 10 digits standalone (not part of longer number)
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Keep original format for alphanumeric
                phone_numbers.add(match)
        
        return phone_numbers
    
    def _extract_emails(self, text: str) -> Set[str]:
        """Extract email addresses from text."""
        emails = set()
        
        matches = self.patterns["email"].findall(text)
        
        for match in matches:
            # Filter out UPI IDs (already captured separately)
            if not any(upi_handle in match.lower() for upi_handle in self.upi_handles):
                emails.add(match)
        
        return emails
    
    def _extract_phishing_urls(self, text: str) -> Set[str]:
        """Extract phishing/malicious URLs from text."""
        phishing_urls = set()
        
        # Extract regular URLs
        url_matches = self.patterns["url"].findall(text)
        for url in url_matches:
            # Check if URL contains suspicious keywords
            if self._is_suspicious_url(url):
                phishing_urls.add(url)
            else:
                # Add all URLs from scammer messages as potentially suspicious
                phishing_urls.add(url)
        
        # Extract shortened URLs
        short_url_matches = self.patterns["short_url"].findall(text)
        for url in short_url_matches:
            phishing_urls.add(url)
        
        return phishing_urls
    
    def _is_suspicious_url(self, url: str) -> bool:
        """Check if a URL contains suspicious keywords."""
        url_lower = url.lower()
        return any(keyword in url_lower for keyword in self.suspicious_url_keywords)
    
    def _is_likely_phone(self, number_str: str) -> bool:
        """Check if a number string is likely a phone number (conservative check)."""
        length = len(number_str)
        
        # If it's exactly 10 or 11 digits, could be phone
        if length in [10, 11]:
            # Check if it starts with common phone prefixes
            if number_str.startswith(('91', '1', '44', '86', '7', '8', '9')):
                return True
        
        # 12+ digits are more likely bank accounts
        return False
