from pydantic import BaseModel
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    user_message: str
    assistant_message: str
    emotion: str
    recommendations: list[str]
    crisis_detected: bool
    crisis_resources: list[str]
    redaction_applied: bool
    detected_sensitive_types: list[str]
    created_at: str
    risk_level: str
    risk_type: str
    safety_triggered: bool
    ai_called: bool