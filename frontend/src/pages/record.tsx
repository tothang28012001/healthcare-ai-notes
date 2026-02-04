import React, { useState, useRef } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';

export default function RecordPage() {
  const router = useRouter();
  
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [fileName, setFileName] = useState<string>('recording.webm');
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [progressStep, setProgressStep] = useState(0); 
  const [consent, setConsent] = useState(false);
  const [error, setError] = useState('');

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // --- 1. RECORDING ---
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      chunksRef.current = [];
      mediaRecorderRef.current.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data); };
      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        setFileName('microphone_recording.webm');
      };
      mediaRecorderRef.current.start();
      setIsRecording(true);
      setError('');
    } catch (err) {
      setError('Microphone access denied. Try uploading a file or using the Sample.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      mediaRecorderRef.current.stream.getTracks().forEach(t => t.stop());
    }
  };

  // --- 2. UPLOAD ---
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('audio/')) {
        setError('Invalid file type.');
        return;
      }
      setAudioBlob(file);
      setFileName(file.name);
      setError('');
    }
  };

  // --- 3. SAMPLE DATA (For Public Demo) ---
  const loadSample = async () => {
    try {
      setError('');
      // Fetch a small dummy audio file (100KB) hosted publicly
      // This is a 10s clip of a person counting or speaking
      const res = await fetch('https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav');
      const blob = await res.blob();
      setAudioBlob(blob);
      setFileName('demo_sample_patient.wav');
      setConsent(true); // Auto-consent for demo data
    } catch (err) {
      setError('Could not load sample data. Please check internet connection.');
    }
  };

  // --- PROCESS PIPELINE ---
  const processSession = async () => {
    if (!audioBlob || !consent) return;
    setIsProcessing(true);
    setProgressStep(1);

    try {
      const formData = new FormData();
      if (audioBlob instanceof File) {
        formData.append("audio", audioBlob);
      } else {
        formData.append("audio", new File([audioBlob], fileName, { type: audioBlob.type || "audio/wav" }));
      }
      formData.append("consent", "true");
      
      const upRes = await fetch('https://healthcare-ai-notes.onrender.com/upload-audio', { method: 'POST', body: formData });
      if (!upRes.ok) throw new Error("Upload failed");
      const { session_id } = await upRes.json();

      setProgressStep(2);
      await fetch(`https://healthcare-ai-notes.onrender.com/transcribe/${session_id}`, { method: 'POST' });

      setProgressStep(3);
      await fetch(`https://healthcare-ai-notes.onrender.com/clean-transcript/${session_id}`, { method: 'POST' });

      setProgressStep(4);
      await fetch(`https://healthcare-ai-notes.onrender.com/extract-notes/${session_id}`, { method: 'POST' });

      router.push(`/review/${session_id}`);

    } catch (err: any) {
      console.error(err);
      setError(err.message || "Processing failed");
      setIsProcessing(false);
      setProgressStep(0);
    }
  };

  // --- UI ---
  return (
    <div style={{ maxWidth: '600px', margin: '40px auto', fontFamily: 'sans-serif', textAlign: 'center' }}>
      <div style={{ marginBottom: '20px', textAlign: 'left' }}>
        <Link href="/" style={{ textDecoration: 'none', color: '#666' }}>← Back to Dashboard</Link>
      </div>

      <div style={{ background: 'white', padding: '40px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        
        {/* PUBLIC DEMO BANNER */}
        <div style={{ background: '#e3f2fd', color: '#0d47a1', padding: '10px', borderRadius: '6px', marginBottom: '20px', fontSize: '0.85rem' }}>
          <strong>ℹ️ PUBLIC DEMO MODE:</strong> Do not upload real patient data. <br/>
          All data is encrypted and automatically deleted after 15 minutes.
        </div>

        <h1 style={{ margin: '0 0 20px 0' }}>New Session</h1>
        
        {error && <div style={{ background: '#ffebee', color: '#c62828', padding: '10px', borderRadius: '6px', marginBottom: '20px' }}>{error}</div>}

        {isProcessing ? (
          <div>
            <div style={{ fontSize: '3rem', marginBottom: '20px' }}>⚙️</div>
            <h3>Processing...</h3>
            <div style={{ textAlign: 'left', marginTop: '20px', background: '#f9f9f9', padding: '15px', borderRadius: '8px' }}>
              <Step label="Uploading & Encrypting" active={progressStep >= 1} />
              <Step label="Transcribing Audio" active={progressStep >= 2} />
              <Step label="Cleaning Transcript" active={progressStep >= 3} />
              <Step label="Generating Medical Draft" active={progressStep >= 4} />
            </div>
          </div>
        ) : (
          <div>
            <div style={{ fontSize: '4rem', marginBottom: '20px' }}>
              {isRecording ? '🔴' : (audioBlob ? '✅' : '🎙️')}
            </div>

            {!audioBlob && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', alignItems: 'center' }}>
                <button 
                  onClick={isRecording ? stopRecording : startRecording}
                  style={{ ...primBtnStyle, backgroundColor: isRecording ? '#dc3545' : '#007bff' }}
                >
                  {isRecording ? 'Stop Recording' : 'Start Recording'}
                </button>

                {!isRecording && (
                  <>
                    <div style={{ display: 'flex', gap: '10px' }}>
                      <input type="file" accept="audio/*" ref={fileInputRef} style={{ display: 'none' }} onChange={handleFileUpload} />
                      <button onClick={() => fileInputRef.current?.click()} style={secBtnStyle}>
                        📁 Upload File
                      </button>
                      
                      {/* SAMPLE BUTTON */}
                      <button onClick={loadSample} style={{ ...secBtnStyle, background: '#fff3cd', borderColor: '#ffeeba', color: '#856404' }}>
                        🧪 Load Sample
                      </button>
                    </div>
                  </>
                )}
              </div>
            )}

            {audioBlob && (
              <div>
                <div style={{ marginBottom: '5px', color: '#28a745', fontWeight: 'bold' }}>Audio Ready</div>
                <div style={{ marginBottom: '20px', fontSize: '0.9rem', color: '#666' }}>{fileName}</div>
                
                <div style={{ margin: '20px 0', textAlign: 'left', background: '#f8f9fa', padding: '15px', borderRadius: '6px' }}>
                    <label style={{ cursor: 'pointer', display: 'flex', alignItems: 'start', gap: '10px', fontSize: '0.9rem' }}>
                        <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />
                        <span>I confirm this is demo data or I have obtained consent.</span>
                    </label>
                </div>

                <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
                  <button onClick={() => { setAudioBlob(null); setConsent(false); }} style={{ ...secBtnStyle, width: '100%' }}>
                    Reset
                  </button>
                  <button onClick={processSession} disabled={!consent} style={{ ...primBtnStyle, width: '100%', opacity: consent ? 1 : 0.5 }}>
                    Process Session →
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

const Step = ({ label, active }: { label: string, active: boolean }) => (
  <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', color: active ? '#007bff' : '#ccc' }}>
    <span style={{ marginRight: '10px' }}>{active ? '✔' : '○'}</span>
    <span style={{ fontWeight: active ? 'bold' : 'normal' }}>{label}</span>
  </div>
);

const primBtnStyle = { padding: '12px 24px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '6px', fontSize: '1rem', cursor: 'pointer', fontWeight: 'bold' };
const secBtnStyle = { padding: '12px 20px', backgroundColor: '#fff', color: '#555', border: '1px solid #ddd', borderRadius: '6px', fontSize: '0.95rem', cursor: 'pointer' };