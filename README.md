# Healthcare AI Notes - MVP (Phase 1)

## Project Overview
A web-based system to record audio, transcribe speech, and extract structured healthcare notes using AI.

**Phase 1 Status:** Project setup and scaffolding only.

## Setup
1. Backend:
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   uvicorn main:app --reload

2. Frontend:
   cd frontend
   npm install
   npm run dev

## Phase 2: Audio Recording & Storage
**Status:** ✅ Complete

### Features
- Browser-based audio recording (MediaRecorder API).
- Real-time upload to Backend via REST API.
- Local storage of audio files in `/storage/audio`.

### How to Test
1. Ensure Backend is running (`uvicorn main:app --reload`).
2. Ensure Frontend is running (`npm run dev`).
3. Open http://localhost:3000.
4. Click **Start Recording**, speak, then click **Stop Recording**.
5. Click **Upload to Backend**.
6. Check the `storage/audio` folder in your project directory. You should see a `.webm` or `.wav` file there.

## Phase 3: Speech-to-Text Integration
**Status:** ✅ Complete

### Features
- Integration with Groq Whisper Large v3.
- Automatic lookup of audio files by `session_id`.
- JSON storage of transcripts in `/storage/transcripts`.

### How to Test (API Only)
Since the UI is not updated yet, you can test via Curl or Swagger UI.

1. **Upload Audio** (via Frontend) -> Copy the `session_id` from the response (e.g., `abc-123`).
2. **Trigger Transcription** (via Terminal):
   ```bash
   # Replace {session_id} with your actual UUID
   curl -X POST http://127.0.0.1:8000/transcribe/{session_id}

   ... (Previous Sections)

## Phase 4: Transcript Cleaning
**Status:** ✅ Complete

### Features
- Removes filler words (um, uh, you know).
- Normalizes punctuation and spacing.
- Saves a separate `_clean.txt` file to preserve original raw data.
- Applies basic heuristic speaker labeling.

### How to Test (API Only)
1. **Ensure you have a transcribed session** (from Phase 3).
2. **Trigger Cleaning:**
   ```bash
   curl -X POST http://127.0.0.1:8000/clean-transcript/{your_session_id}

## Phase 5: Structured AI Extraction
**Status:** ✅ Complete

### Objective
Convert cleaned transcripts into structured JSON clinical drafts using Llama 3.

### Features
- **Strict Schema:** Outputs explicitly defined fields (Chief Complaint, Symptoms, Plan, etc.).
- **Safety:** Explicit system prompts prevent diagnosis or hallucination.
- **Validation:** Python-side verification ensures missing keys don't break the system.

### How to Test (API)
1. **Ensure you have a cleaned transcript** (Run Phase 4 first).
2. **Trigger Extraction:**
   ```bash
   curl -X POST http://127.0.0.1:8000/extract-notes/{session_id}

## Phase 6: Human-in-the-Loop Review
**Status:** ✅ Complete

### Objective
Provide a UI for clinicians to review, edit, and approve AI-generated drafts. This ensures AI never acts autonomously.

### Features
- **Review UI:** `/review/[session_id]`
- **Draft Management:** Edit any field (Symptoms, Assessment, Plan).
- **Approval Workflow:** Explicit "Approve" action locks the note.
- **Side-by-Side:** View the original transcript while editing the note.

### How to Test (Frontend)
1. **Generate a Note** (using the main page or API).
2. **Copy the Session ID** (e.g., `CAR0002`).
3. **Navigate to:** `http://localhost:3000/review/CAR0002`
4. **Interact:**
   - Modify the "Chief Complaint".
   - Click **Save Draft** (Check `storage/notes/CAR0002.json` to see updates).
   - Click **Approve Note** (Status changes to `approved`).

   ... (Previous Sections)

## Phase 7: PDF Export & Finalization
**Status:** ✅ Complete

### Objective
Generate secure, immutable PDF documents from approved medical notes.

### Features
- **Validation:** Server rejects export requests for "draft" notes.
- **PDF Generation:** Uses `reportlab` to render clinical data.
- **Storage:** Saves files to `/storage/exports`.

### How to Test (API)
1. **Ensure note is Approved:** Use the Review UI (`/review/{id}`) to click "Approve".
2. **Trigger Export:**
   ```bash
   curl -X POST http://127.0.0.1:8000/export/{session_id}

   ## Phase 8: Audit Logging & Versioning
**Status:** ✅ Complete

### Features
- **Audit Logs:** Every action (Upload, AI Gen, Edit, Export) is logged to `/storage/audit/{session_id}.jsonl`.
- **Versioning:** Every time a note is edited, a backup of the previous version is saved (e.g., `_v1.json`).
- **Traceability:** Logs capture the "Actor" (System vs Human) and timestamps.

### How to Test (API)
1. **Perform Actions:** Upload, Process, Edit, Approve, Export.
2. **View Log:**
   ```bash
   curl -X GET http://127.0.0.1:8000/audit/{session_id}

   ## Phase 9: Compliance Hardening (HIPAA/PIPEDA)
**Status:** ✅ Complete

### Security Measures
- **Encryption at Rest:** All data is encrypted using AES-128 (Fernet) before writing to disk.
- **Data Retention:** Automated startup tasks delete audio > 24h and transcripts > 7 days old.
- **Consent Enforcement:** API rejects uploads without explicit consent flag.
- **Audit Trails:** Immutable logging of all access and modifications.

### Disclaimer
This software implements **technical safeguards** required by healthcare regulations (HIPAA/PIPEDA). However, using this software does not automatically make you compliant. Organizational policies, BAAs, and physical security are also required.