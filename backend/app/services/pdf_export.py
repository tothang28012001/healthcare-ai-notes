import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from app.services.security import secure_read_json # <--- FIX: Import Secure Reader

# Configuration
STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
NOTES_DIR = os.path.join(STORAGE_PATH, "notes")
EXPORTS_DIR = os.path.join(STORAGE_PATH, "exports")

def generate_pdf(session_id: str) -> str:
    """
    Validates that a note is approved, then generates a PDF summary.
    Returns the relative path to the generated file.
    """
    # 1. Load the Note
    note_path = os.path.join(NOTES_DIR, f"{session_id}.json")
    if not os.path.exists(note_path):
        raise FileNotFoundError(f"Note not found for session {session_id}")

    # --- FIX: Decrypt the file instead of reading raw JSON ---
    data = secure_read_json(note_path)

    # 2. Strict Validation: APPROVED ONLY
    if data.get("status") != "approved":
        raise ValueError("Cannot export unapproved notes. Clinician review required.")

    # 3. Setup PDF File
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    filename = f"{session_id}.pdf"
    file_path = os.path.join(EXPORTS_DIR, filename)

    # 4. Draw PDF
    c = canvas.Canvas(file_path, pagesize=LETTER)
    width, height = LETTER
    
    # Helper for cursor management
    y_position = height - 50
    left_margin = 50

    def draw_line(text, font="Helvetica", size=12, gap=15):
        nonlocal y_position
        c.setFont(font, size)
        c.drawString(left_margin, y_position, text)
        y_position -= gap

    def draw_section(title, content):
        nonlocal y_position
        y_position -= 10
        draw_line(title, "Helvetica-Bold", 12)
        
        c.setFont("Helvetica", 11)
        if isinstance(content, list):
            for item in content:
                c.drawString(left_margin + 15, y_position, f"• {item}")
                y_position -= 15
        elif content:
            # Simple truncation for safety
            text_str = str(content)
            if len(text_str) > 90: text_str = text_str[:90] + "..."
            c.drawString(left_margin + 15, y_position, text_str)
            y_position -= 15
        else:
            c.drawString(left_margin + 15, y_position, "None")
            y_position -= 15
        
        y_position -= 10 # Extra gap after section

    # --- Header ---
    c.setFont("Helvetica-Bold", 16)
    c.drawString(left_margin, y_position, "Clinical Visit Summary")
    y_position -= 20
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(left_margin, y_position, "(Drafted with AI, Reviewed by Clinician)")
    y_position -= 30
    
    # --- Metadata ---
    draw_line(f"Session ID: {session_id}", size=10)
    draw_line(f"Date: {datetime.now().strftime('%Y-%m-%d')}", size=10)
    draw_line(f"Status: {data.get('status', 'APPROVED').upper()}", size=10)
    y_position -= 20
    c.line(left_margin, y_position, width - left_margin, y_position)
    y_position -= 30

    # --- Clinical Content ---
    draw_section("Chief Complaint:", data.get("chief_complaint"))
    draw_section("Duration:", data.get("duration"))
    draw_section("Symptoms:", data.get("symptoms"))
    draw_section("Medical History:", data.get("medical_history"))
    draw_section("Medications:", data.get("medications_mentioned"))
    draw_section("Assessment:", data.get("assessment"))
    draw_section("Plan:", data.get("plan"))
    draw_section("Follow-up:", data.get("follow_up"))

    # --- Footer ---
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.grey)
    c.drawString(left_margin, 30, "This document was generated using AI and reviewed by a licensed clinician.")
    
    c.save()

    return f"exports/{filename}"