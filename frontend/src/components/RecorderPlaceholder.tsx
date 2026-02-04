import React, { useState, useRef } from 'react';

// --- TYPES DEFINITIONS (Fixed for Phase 5 & 9) ---

interface DialogueLine {
  speaker: string;
  text: string;
}

// Updated interface to support both Phase 4 (Nested) and Phase 5 (Flat) formats
interface AIResponse {
  // Phase 4 Structure
  dialogue?: DialogueLine[];
  medical_notes?: {
    subjective?: string;
    objective?: string;
    assessment?: string;
    plan?: string;
  };

  // Phase 5 Structure (New properties to fix TS error)
  chief_complaint?: string;
  symptoms?: string[];
  assessment?: string; // Phase 5 uses a flat string here too
  plan?: string[];     // Phase 5 uses an array of strings
}

const RecorderPlaceholder: React.FC = () => {
  // --- STATE ---
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [status, setStatus] = useState<string>('Idle');
  const [result, setResult] = useState<AIResponse | null>(null);
  
  // Phase 9: Consent State
  const [consent, setConsent] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  // 1. Start Recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      chunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        setStatus('Recorded. Ready to Process.');
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setStatus('Recording...');
      setResult(null);
    } catch (err) {
      console.error(err);
      setStatus('Error accessing microphone');
    }
  };

  // 2. Stop Recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      mediaRecorderRef.current.stream.getTracks().forEach(t => t.stop());
    }
  };

  // 3. Process Logic (Upload -> Transcribe -> Clean -> Extract)
  const processRecording = async () => {
    if (!audioBlob) return;

    // Phase 9: Consent Check
    if (!consent) {
        alert("You must confirm patient consent before processing.");
        return;
    }

    setStatus('Uploading Audio...');

    try {
      // Step A: Upload
      const formData = new FormData();
      formData.append("audio", new File([audioBlob], "recording.webm", { type: "audio/webm" }));
      formData.append("consent", "true"); // Phase 9: Send Consent Flag
      
      const uploadRes = await fetch('http://127.0.0.1:8000/upload-audio', { method: 'POST', body: formData });
      
      if (!uploadRes.ok) {
          const err = await uploadRes.json();
          throw new Error(err.detail || "Upload failed");
      }
      const { session_id } = await uploadRes.json();

      // Step B: Transcribe
      setStatus('Transcribing (Listening)...');
      await fetch(`http://127.0.0.1:8000/transcribe/${session_id}`, { method: 'POST' });

      // Step C: Clean
      setStatus('Cleaning Transcript...');
      await fetch(`http://127.0.0.1:8000/clean-transcript/${session_id}`, { method: 'POST' });

      // Step D: AI Extraction (Using Phase 5 Endpoint)
      setStatus('Generating Medical Notes (Thinking)...');
      const genRes = await fetch(`http://127.0.0.1:8000/extract-notes/${session_id}`, { method: 'POST' });
      
      if (!genRes.ok) throw new Error("AI Extraction failed");
      const genData = await genRes.json();

      setResult(genData.data);
      setStatus('Complete');
      
      // Optional: Redirect to Phase 6 Review Page automatically
      // window.location.href = `/review/${session_id}`;

    } catch (error) {
      console.error(error);
      setStatus('Error during processing');
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      
      {/* --- RECORDER PANEL --- */}
      <div style={{ 
        border: '2px solid #e0e0e0', padding: '30px', textAlign: 'center', 
        borderRadius: '12px', background: '#f9f9f9', marginBottom: '30px'
      }}>
        <div style={{ fontSize: '3rem', marginBottom: '15px' }}>{isRecording ? '🔴' : '🎙️'}</div>
        <h2 style={{ margin: '0 0 10px 0' }}>{status}</h2>
        
        <div style={{ display: 'flex', gap: '15px', justifyContent: 'center', marginTop: '20px' }}>
          {!isRecording ? (
            <button onClick={startRecording} style={btnStyle('#28a745')}>Start Recording</button>
          ) : (
            <button onClick={stopRecording} style={btnStyle('#dc3545')}>Stop Recording</button>
          )}

          <button 
            onClick={processRecording} 
            disabled={!audioBlob || isRecording}
            style={btnStyle(audioBlob && !isRecording ? '#007bff' : '#ccc')}
          >
            ⚡ Process Recording
          </button>
        </div>

        {/* Phase 9: Consent Checkbox */}
        <div style={{ marginTop: '20px', textAlign: 'left', display: 'inline-block' }}>
            <label style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.9rem' }}>
                <input 
                    type="checkbox" 
                    checked={consent} 
                    onChange={(e) => setConsent(e.target.checked)} 
                />
                I confirm that I have obtained necessary patient consent to record and process this consultation.
            </label>
        </div>

      </div>

      {/* --- RESULTS DISPLAY --- */}
      {result && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          
          {/* Left Column: Dialogue / Transcript */}
          <div style={cardStyle}>
            <h3>🗣️ Transcript</h3>
            <div style={{ maxHeight: '500px', overflowY: 'auto', background: '#fff', padding: '15px', borderRadius: '8px', border: '1px solid #eee' }}>
              {/* Conditional rendering: Dialogue vs Raw Text */}
              {result.dialogue ? (
                result.dialogue.map((line, idx) => (
                  <div key={idx} style={{ marginBottom: '12px' }}>
                    <strong style={{ color: line.speaker === 'Doctor' ? '#0056b3' : '#28a745' }}>
                      {line.speaker}:
                    </strong>
                    <span style={{ marginLeft: '8px', color: '#444' }}>{line.text}</span>
                  </div>
                ))
              ) : (
                <p style={{ color: '#666', fontStyle: 'italic' }}>
                  (Dialogue diarization not available in strict extraction mode. See raw transcript in review.)
                </p>
              )}
            </div>
          </div>

          {/* Right Column: Medical Notes */}
          <div style={cardStyle}>
            <h3>📋 Medical Notes (SOAP)</h3>
            <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', border: '1px solid #eee' }}>
              
              {/* 
                  Hybrid Rendering: 
                  Checks if we have Phase 4 (nested) OR Phase 5 (flat) data 
                  This fixes the TypeScript errors you were seeing.
              */}

              <Section 
                title="Subjective" 
                content={result.medical_notes?.subjective || result.chief_complaint || ''} 
              />
              
              <Section 
                title="Objective" 
                content={
                  result.medical_notes?.objective || 
                  (result.symptoms ? result.symptoms.join(', ') : '')
                } 
              />
              
              <Section 
                title="Assessment" 
                content={result.medical_notes?.assessment || result.assessment || ''} 
              />
              
              <Section 
                title="Plan" 
                content={
                  result.medical_notes?.plan || 
                  (result.plan ? result.plan.join(', ') : '')
                } 
              />

            </div>
          </div>

        </div>
      )}
    </div>
  );
};

// --- HELPER COMPONENTS ---

const Section = ({ title, content }: { title: string, content: string }) => {
  // If content is empty, don't show the section or show placeholder
  if (!content) return null;
  
  return (
    <div style={{ marginBottom: '20px' }}>
      <h4 style={{ margin: '0 0 5px 0', color: '#333', textTransform: 'uppercase', fontSize: '0.85rem' }}>{title}</h4>
      <p style={{ margin: 0, color: '#555', lineHeight: '1.5' }}>{content}</p>
    </div>
  );
};

const btnStyle = (bg: string) => ({
  padding: '12px 24px', fontSize: '1rem', cursor: 'pointer',
  backgroundColor: bg, color: 'white', border: 'none', borderRadius: '6px', fontWeight: 'bold'
});

const cardStyle = {
  background: '#f8f9fa', padding: '20px', borderRadius: '12px', border: '1px solid #ddd'
};

export default RecorderPlaceholder;