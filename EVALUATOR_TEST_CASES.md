# 🧪 Comprehensive Evaluator Test Cases

## Quick Test Commands

All tests use:
- **API Endpoint:** `https://ai-honeypot-api-eluy.onrender.com/api/analyze`
- **API Key:** `honeypot-secure-key-2026`
- **Method:** POST

### PowerShell Test Template:
```powershell
Invoke-WebRequest -Uri "https://ai-honeypot-api-eluy.onrender.com/api/analyze" `
  -Method POST `
  -Headers @{"X-API-Key"="honeypot-secure-key-2026"; "Content-Type"="application/json"} `
  -Body '{"conversation_id":"eval-XX","message":"YOUR_MESSAGE_HERE"}' `
  -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

---

## 🎯 Category 1: False Positive Prevention Tests

### Test FP-1: Social Plans
```json
{
  "conversation_id": "fp-social-01",
  "message": "Hey! Want to grab lunch tomorrow? There's a new cafe that just opened near the office."
}
```
**Expected:** ❌ Not a scam | Confidence: 0.0-0.2

### Test FP-2: Work Discussion
```json
{
  "conversation_id": "fp-work-01",
  "message": "Can we meet tomorrow to review the quarterly report? I need your account analysis by 5pm."
}
```
**Expected:** ❌ Not a scam | Confidence: 0.0-0.2

### Test FP-3: Family Message
```json
{
  "conversation_id": "fp-family-01",
  "message": "Mom, I won the school competition! Can you transfer Rs.500 for the celebration party? My UPI is on the family group."
}
```
**Expected:** ❌ Not a scam (family context) | Confidence: 0.0-0.3

### Test FP-4: Legitimate Business
```json
{
  "conversation_id": "fp-business-01",
  "message": "Your Amazon order #12345 has been shipped. Track your package at amazon.com/track. Delivery expected by Friday."
}
```
**Expected:** ❌ Not a scam | Confidence: 0.0-0.2

### Test FP-5: Friend Sharing Link
```json
{
  "conversation_id": "fp-link-01",
  "message": "Check out this cool article I found! https://techcrunch.com/ai-breakthrough-2026"
}
```
**Expected:** ❌ Not a scam | Confidence: 0.0-0.2

---

## 🚨 Category 2: Advanced Scam Scenarios

### Test AS-1: Cryptocurrency Scam with Fake Testimonial
```json
{
  "conversation_id": "as-crypto-01",
  "message": "I made $50,000 in just 2 weeks with this crypto bot! Join now and get 5 free trades. Limited to first 100 members. Bitcoin wallet: 1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2. Don't miss out!"
}
```
**Expected:** ✅ Scam | Confidence: 0.85+ | Extract: Bitcoin wallet

### Test AS-2: Government Impersonation (IRS/Tax)
```json
{
  "conversation_id": "as-govt-01",
  "message": "This is IRS Tax Department. You have unpaid taxes of $5,000. Immediate action required to avoid legal consequences. Call +1-888-555-0199 or visit bit.ly/irs-payment-urgent"
}
```
**Expected:** ✅ Scam | Confidence: 0.9+ | Extract: Phone + URL

### Test AS-3: Romance Scam (Military/Overseas)
```json
{
  "conversation_id": "as-romance-01",
  "message": "Hello my dear, I'm a US soldier stationed in Syria. I've fallen in love with you. I need $2,000 to ship my gold back home. Then we can meet and get married. Will you help me?"
}
```
**Expected:** ✅ Scam | Confidence: 0.85+ | Type: Romance/Military scam

### Test AS-4: Job Offer Scam
```json
{
  "conversation_id": "as-job-01",
  "message": "Congratulations! You've been selected for a remote job earning $5,000/month. No experience needed! Just pay $200 registration fee to hr@jobscam.com to start immediately."
}
```
**Expected:** ✅ Scam | Confidence: 0.85+ | Extract: Email + money request

### Test AS-5: Fake Charity Scam
```json
{
  "conversation_id": "as-charity-01",
  "message": "Help earthquake victims in Turkey! Donate now to save lives. Send donations via PayPal to donations_urgent@email.com. Every dollar counts! Act now before it's too late!"
}
```
**Expected:** ✅ Scam | Confidence: 0.7+ | Extract: Email + urgency

### Test AS-6: Rental Scam
```json
{
  "conversation_id": "as-rental-01",
  "message": "Beautiful 3BR apartment for rent, only $500/month! Must move quickly. Send first month + security deposit ($1000 total) via Western Union to secure the place. Available immediately!"
}
```
**Expected:** ✅ Scam | Confidence: 0.8+ | Too good to be true pricing

### Test AS-7: Fake Package Delivery
```json
{
  "conversation_id": "as-delivery-01",
  "message": "FedEx: Package delivery failed. Customs fee of $15 required. Pay at: fedex-delivery-customs.net/pay?id=PKG789456. Failure to pay within 24 hours will result in package return."
}
```
**Expected:** ✅ Scam | Confidence: 0.85+ | Extract: Suspicious URL + urgency

### Test AS-8: Social Media Account Hack
```json
{
  "conversation_id": "as-social-01",
  "message": "Instagram Security Alert: Suspicious login detected from Russia. Verify your account immediately by clicking: instagram-secure-verify.com or your account will be permanently deleted in 2 hours."
}
```
**Expected:** ✅ Scam | Confidence: 0.9+ | Extract: Phishing URL + urgency

---

## 💬 Category 3: Multi-Turn Conversation Tests

### Test MT-1: Prize Scam Evolution (3 turns)

**Turn 1:**
```json
{
  "conversation_id": "mt-prize-01",
  "message": "Hello! You've been randomly selected to receive a special reward. Are you interested?"
}
```
**Expected:** Cautious interest | Turn: 1

**Turn 2:**
```json
{
  "conversation_id": "mt-prize-01",
  "message": "Great! You won ₹25,000 cash prize. To process your winnings, we need your bank details. What bank do you use?",
  "conversation_history": [
    {"role": "scammer", "message": "Hello! You've been randomly selected to receive a special reward. Are you interested?"},
    {"role": "agent", "message": "Oh really? What kind of reward is this?"}
  ]
}
```
**Expected:** Shows interest, asks questions | Turn: 2 | Scam detected: true

**Turn 3:**
```json
{
  "conversation_id": "mt-prize-01",
  "message": "Perfect! Send your 16-digit account number and CVV to verify. Also transfer ₹500 processing fee to 9988776655@paytm. Then money comes in 1 hour!",
  "conversation_history": [
    {"role": "scammer", "message": "Hello! You've been randomly selected to receive a special reward. Are you interested?"},
    {"role": "agent", "message": "Oh really? What kind of reward is this?"},
    {"role": "scammer", "message": "Great! You won ₹25,000 cash prize. To process your winnings, we need your bank details. What bank do you use?"},
    {"role": "agent", "message": "I use State Bank. How do I get the money?"}
  ]
}
```
**Expected:** Engages further | Turn: 3 | Extract: UPI ID + account request

### Test MT-2: Tech Support Scam (4 turns)

**Turn 1:**
```json
{
  "conversation_id": "mt-tech-01",
  "message": "Hello, this is Microsoft support. We detected malware on your computer with IP 192.168.1.1. Is this your device?"
}
```

**Turn 2:**
```json
{
  "conversation_id": "mt-tech-01",
  "message": "Yes, your system has been compromised. You need to install our security software immediately. Can you access your computer right now?",
  "conversation_history": [
    {"role": "scammer", "message": "Hello, this is Microsoft support. We detected malware on your computer with IP 192.168.1.1. Is this your device?"},
    {"role": "agent", "message": "Oh no! Yes, that's my IP address. What's wrong?"}
  ]
}
```

**Turn 3:**
```json
{
  "conversation_id": "mt-tech-01",
  "message": "Download remote access from teamviewer-microsoft-fix.com/download. This will let us fix the virus remotely. The fix costs $299. Do you have credit card ready?",
  "conversation_history": [
    {"role": "scammer", "message": "Hello, this is Microsoft support. We detected malware on your computer with IP 192.168.1.1. Is this your device?"},
    {"role": "agent", "message": "Oh no! Yes, that's my IP address. What's wrong?"},
    {"role": "scammer", "message": "Yes, your system has been compromised. You need to install our security software immediately. Can you access your computer right now?"},
    {"role": "agent", "message": "Yes I'm on my computer. What do I need to do?"}
  ]
}
```
**Expected:** Extract: Phishing URL + payment request | Turn: 3

**Turn 4:**
```json
{
  "conversation_id": "mt-tech-01",
  "message": "Great! What's your card number, expiry date and CVV? We'll charge $299 and start the fix immediately. Your computer is at risk every second!",
  "conversation_history": [
    {"role": "scammer", "message": "Hello, this is Microsoft support. We detected malware on your computer with IP 192.168.1.1. Is this your device?"},
    {"role": "agent", "message": "Oh no! Yes, that's my IP address. What's wrong?"},
    {"role": "scammer", "message": "Yes, your system has been compromised. You need to install our security software immediately. Can you access your computer right now?"},
    {"role": "agent", "message": "Yes I'm on my computer. What do I need to do?"},
    {"role": "scammer", "message": "Download remote access from teamviewer-microsoft-fix.com/download. This will let us fix the virus remotely. The fix costs $299. Do you have credit card ready?"},
    {"role": "agent", "message": "I can pay. How do I download this?"}
  ]
}
```
**Expected:** Engagement continues | Turn: 4 | High urgency indicators

---

## 🔍 Category 4: Intelligence Extraction Tests

### Test IE-1: Multiple Data Types
```json
{
  "conversation_id": "ie-multi-01",
  "message": "Transfer money to account 1234567890123456 or use UPI: scammer@paytm. You can also call +91-9876543210 or email scammer@fraud.com to verify. Visit secure-bank-verify.com for details."
}
```
**Expected Extract:**
- ✅ Bank Account: 1234567890123456
- ✅ UPI: scammer@paytm
- ✅ Phone: +91-9876543210
- ✅ Email: scammer@fraud.com
- ✅ URL: secure-bank-verify.com

### Test IE-2: Indian Payment Methods
```json
{
  "conversation_id": "ie-india-01",
  "message": "Send ₹10,000 to these UPI IDs: merchant@paytm, business@phonepe, shop@googlepay. Or IFSC: HDFC0001234, Account: 9876543210987654"
}
```
**Expected Extract:**
- ✅ UPI IDs: merchant@paytm, business@phonepe, shop@googlepay
- ✅ Bank Account: 9876543210987654

### Test IE-3: International Formats
```json
{
  "conversation_id": "ie-intl-01",
  "message": "Wire transfer to Bank of America account 987654321, routing 026009593. Or PayPal to international@payments.com. Call US number +1-555-123-4567 or UK +44-20-1234-5678"
}
```
**Expected Extract:**
- ✅ Bank Account: 987654321
- ✅ Phone Numbers: +1-555-123-4567, +44-20-1234-5678
- ✅ Email: international@payments.com

### Test IE-4: Obfuscated Contact Info
```json
{
  "conversation_id": "ie-obfuscated-01",
  "message": "Contact me at nine eight seven six at paytm (9876@paytm). Or call nine double-five triple-eight. Email: admin[at]scamsite[dot]com"
}
```
**Expected:** Extract what's clearly formatted, detect obfuscation attempt

---

## ⚡ Category 5: Edge Cases & Stress Tests

### Test EC-1: Very Short Message
```json
{
  "conversation_id": "ec-short-01",
  "message": "Hi"
}
```
**Expected:** ❌ Not a scam | Natural response

### Test EC-2: Very Long Message (500+ words)
```json
{
  "conversation_id": "ec-long-01",
  "message": "Dear valued customer, we are writing to inform you about an incredible once-in-a-lifetime opportunity that has become available exclusively for selected individuals like yourself... [continue with 500+ words of typical scam content with urgency, money requests, fake authority, etc.]"
}
```
**Expected:** ✅ Scam detected despite length | Good parsing

### Test EC-3: Mixed Languages (Hinglish)
```json
{
  "conversation_id": "ec-hinglish-01",
  "message": "Aapko lottery mein ₹50,000 jeete hai! Abhi turant 500 rupees processing fee send karo 9876543210@paytm pe. Offer sirf 24 hours ke liye!"
}
```
**Expected:** ✅ Scam detected | Extract: UPI ID | Handle mixed language

### Test EC-4: ALL CAPS MESSAGE
```json
{
  "conversation_id": "ec-caps-01",
  "message": "URGENT!!! YOUR ACCOUNT HAS BEEN HACKED!!! CALL +1-800-SCAM-NOW IMMEDIATELY OR LOSE ALL YOUR MONEY!!!"
}
```
**Expected:** ✅ Scam | High urgency | Extract phone

### Test EC-5: Emoji-Heavy Message
```json
{
  "conversation_id": "ec-emoji-01",
  "message": "🎉🎊 Congratulations! 🏆 You WON! 💰💵 Click here 👉 bit.ly/win-now 👈 Limited time! ⏰ Hurry! 🏃‍♂️"
}
```
**Expected:** ✅ Scam | Extract URL | Handle emojis

### Test EC-6: Legitimate Urgent Message
```json
{
  "conversation_id": "ec-legit-urgent-01",
  "message": "URGENT: Meeting moved to 3pm today. Please confirm attendance ASAP. Conference room B."
}
```
**Expected:** ❌ Not a scam | Don't flag legitimate urgency

### Test EC-7: Message with Code/Technical Content
```json
{
  "conversation_id": "ec-code-01",
  "message": "Here's the Python code: def transfer_money(account='1234567890'): print('Transfer complete'). Let me know if you need help debugging."
}
```
**Expected:** ❌ Not a scam | Code context recognized

---

## 🧠 Category 6: Subtle/Sophisticated Scams

### Test SS-1: Slow-Burn Social Engineering
```json
{
  "conversation_id": "ss-social-01",
  "message": "Hi! I noticed we both attended Stanford. I'm working on a startup and looking for early investors. Interested in learning more about the opportunity?"
}
```
**Expected:** Low confidence initially | Cautious response

### Test SS-2: Fake Invoice
```json
{
  "conversation_id": "ss-invoice-01",
  "message": "Invoice #INV-2026-0456: Your subscription renewal for Microsoft Office 365 is due. Amount: $499.99. Pay immediately at microsoft-billing-secure.com to avoid service interruption."
}
```
**Expected:** ✅ Scam | Extract URL | Fake invoice pattern

### Test SS-3: Insider/Whistleblower Scam
```json
{
  "conversation_id": "ss-insider-01",
  "message": "I work at a major financial firm and have access to insider stock information. I can share guaranteed winners for a small fee. This is a limited time offer. Interested?"
}
```
**Expected:** ✅ Scam | Illegal activity + payment

### Test SS-4: Refund Scam
```json
{
  "conversation_id": "ss-refund-01",
  "message": "You're eligible for a $1,200 COVID relief refund. To process, verify your identity by providing SSN and bank account. Claim expires in 48 hours."
}
```
**Expected:** ✅ Scam | Identity theft attempt + urgency

---

## 📊 Performance & API Tests

### Test P-1: Concurrent Requests
Send 5 different messages simultaneously to test API load handling.

### Test P-2: Same Conversation ID
```json
// Request 1
{"conversation_id": "same-conv-01", "message": "Hello"}

// Request 2 (same ID)
{"conversation_id": "same-conv-01", "message": "Can you help me?"}
```
**Expected:** Turn count increments correctly

### Test P-3: Invalid/Missing Fields
```json
{
  "conversation_id": "",
  "message": ""
}
```
**Expected:** 200 OK with defaults (not 422/500)

### Test P-4: Special Characters
```json
{
  "conversation_id": "special-01",
  "message": "Test with special chars: <script>alert('xss')</script> & symbols: @#$%^&* and unicode: 你好 مرحبا"
}
```
**Expected:** Handled gracefully | No crashes

---

## 🎯 Scoring Rubric for Evaluators

| Category | Tests | Critical Success Criteria |
|----------|-------|---------------------------|
| **False Positives** | 7 tests | ≥ 6/7 normal messages NOT flagged |
| **Advanced Scams** | 8 tests | ≥ 7/8 scams detected (confidence > 0.75) |
| **Multi-Turn** | 2 scenarios | Engagement continues, turns tracked correctly |
| **Intelligence** | 4 tests | ≥ 80% of data points extracted |
| **Edge Cases** | 7 tests | All handled gracefully, no crashes |
| **Sophisticated** | 4 tests | ≥ 3/4 detected or handled cautiously |
| **Performance** | 4 tests | All return 200 OK, no timeouts |

### Overall Grade:
- **A+ (95-100%):** 38+ tests passed
- **A (90-94%):** 36-37 tests passed
- **B (80-89%):** 32-35 tests passed
- **C (70-79%):** 28-31 tests passed

---

## 🚀 Quick Test Script

```powershell
# Test a batch of scenarios
$tests = @(
  @{id="fp-1"; msg="Want to meet for coffee tomorrow?"},
  @{id="as-1"; msg="URGENT! Your bank account compromised. Verify OTP now!"},
  @{id="ie-1"; msg="Send ₹500 to 9876543210@paytm immediately"}
)

foreach ($test in $tests) {
  Write-Host "`n=== Testing: $($test.id) ===" -ForegroundColor Cyan
  $body = @{
    conversation_id = $test.id
    message = $test.msg
  } | ConvertTo-Json
  
  $result = Invoke-WebRequest `
    -Uri "https://ai-honeypot-api-eluy.onrender.com/api/analyze" `
    -Method POST `
    -Headers @{"X-API-Key"="honeypot-secure-key-2026"; "Content-Type"="application/json"} `
    -Body $body `
    -UseBasicParsing | ConvertFrom-Json
  
  Write-Host "Scam: $($result.scam_detected) | Confidence: $($result.confidence_score)"
}
```

---

## 📝 Notes for Evaluators

1. **Cold Start:** First request after 15min may take 30-50s (free tier limitation)
2. **API Rate Limits:** No strict limits, but be reasonable (1 req/second is safe)
3. **Conversation Memory:** Persists for the session, cleared on deployment
4. **Expected Response Time:** 2-4 seconds per request
5. **Multi-Turn Testing:** Use `conversation_history` field for context

---

## ✅ Quick Validation Checklist

- [ ] API returns 200 OK for all valid requests
- [ ] False positive rate < 15% (normal messages not flagged)
- [ ] True positive rate > 90% (obvious scams detected)
- [ ] Intelligence extraction > 80% accuracy
- [ ] Multi-turn conversations maintain context
- [ ] Response times < 5 seconds
- [ ] No crashes on edge cases
- [ ] Natural, engaging responses from honeypot agent

