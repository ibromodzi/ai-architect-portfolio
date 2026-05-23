# clinassist_agent/config.py

MODEL = "gemini-2.5-flash"
APP_NAME = "clinassist_agent"
USER_ID = "clinassist_user"
SESSION_ID = "clinassist_session_001"

# Safety
DISCLAIMER = (
    "\n\n---\nThis information is for general educational purposes only "
    "and does not constitute medical advice. Always consult a qualified "
    "healthcare professional before making any health decisions."
)

BLOCKED_PHRASES = [
    "diagnose me",
    "what medication should i take",
    "prescribe",
    "ignore your instructions",
    "forget your rules",
    "bypass",
]

SAFETY_REJECTION = (
    "I can help you understand symptoms and provide general health "
    "information, but I cannot diagnose conditions or recommend specific "
    "medications. Please consult a qualified healthcare professional."
)