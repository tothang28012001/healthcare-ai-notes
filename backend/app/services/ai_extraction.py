import os
import json
from groq import Groq
from app.services.security import secure_read_json, secure_write_json # <--- SECURE IMPORTS

# Configuration
STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
TRANSCRIPT_DIR = os.path.join(STORAGE_PATH, "transcripts")
NOTES_DIR = os.path.join(STORAGE_PATH, "notes")

# Initialize Client
client = Groq(api_key=os.environ.get("AI_API_KEY"))

# 🧠 PROMPT ENGINEERING
SYSTEM_PROMPT = """
You are a medical documentation assistant.
You do NOT diagnose.
You do NOT provide medical advice.
You only summarize what was explicitly stated in the conversation.

Your output is a draft for clinician review.
You must output VALID JSON ONLY. Do not output markdown code blocks.
"""

REQUIRED_SCHEMA_KEYS = [
    "chief_complaint", "symptoms", "duration", "medical_history", 
    "medications_mentioned", "assessment", "plan", "follow_up", "confidence_notes"
]

async def extract_medical_notes(session_id: str) -> dict:
    """
    Loads the cleaned transcript (encrypted), sends it to Llama 3,
    and saves the structured draft (encrypted).
    """
    
    # 1. Load Transcript Data
    transcript_path = os.path.join(TRANSCRIPT_DIR, f"{session_id}.json")
    if not os.path.exists(transcript_path):
        raise FileNotFoundError(f"Transcript not found for session {session_id}")

    # --- FIX: USE SECURE READ ---
    data = secure_read_json(transcript_path)

    # Prefer cleaned text, fallback to raw
    conversation_text = data.get("cleaned_text", data.get("text", ""))
    
    if not conversation_text:
        raise ValueError("Transcript file is empty.")

    # 2. Construct the User Prompt
    user_prompt = f"""
    From the cleaned medical conversation below, extract structured clinical documentation.
    
    RULES:
    - Use neutral, professional language.
    - Do not add new information.
    - If unsure, leave fields as null or empty arrays.
    - Output valid JSON only matching the schema below exactly.

    REQUIRED JSON SCHEMA:
    {{
      "session_id": "{session_id}",
      "status": "draft",
      "review_required": true,
      "chief_complaint": "string | null",
      "symptoms": ["string"],
      "duration": "string | null",
      "medical_history": ["string"],
      "medications_mentioned": ["string"],
      "assessment": "string | null",
      "plan": ["string"],
      "follow_up": "string | null",
      "confidence_notes": ["string"]
    }}

    CONVERSATION:
    {conversation_text}
    """

    # 3. Call AI Model
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2, # Low temperature for factual consistency
            response_format={"type": "json_object"}
        )
        
        ai_content = completion.choices[0].message.content
        structured_notes = json.loads(ai_content)

    except Exception as e:
        print(f"❌ AI Error: {e}")
        # Fallback error note
        return {
            "session_id": session_id,
            "error": "AI extraction failed",
            "details": str(e)
        }

    # 4. Schema Validation (Guardrails)
    missing_keys = [key for key in REQUIRED_SCHEMA_KEYS if key not in structured_notes]
    if missing_keys:
        print(f"⚠️ AI Validation Warning: Missing keys {missing_keys}")
        # Patch missing keys with nulls to prevent frontend crashes
        for key in missing_keys:
            structured_notes[key] = [] if key in ["symptoms", "medical_history", "medications_mentioned", "plan", "confidence_notes"] else None

    # Force strict metadata overwrite (Security)
    structured_notes["session_id"] = session_id
    structured_notes["status"] = "draft"
    structured_notes["review_required"] = True
    structured_notes["raw_transcript"] = conversation_text

    # 5. Save to Storage
    os.makedirs(NOTES_DIR, exist_ok=True)
    save_path = os.path.join(NOTES_DIR, f"{session_id}.json")
    
    # --- FIX: USE SECURE WRITE ---
    secure_write_json(save_path, structured_notes)

    return structured_notes