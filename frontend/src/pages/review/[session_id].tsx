import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';

// --- Types ---
interface MedicalNote {
  session_id: string;
  status: string;
  raw_transcript?: string;
  chief_complaint: string | null;
  symptoms: string[];
  duration: string | null;
  medical_history: string[];
  medications_mentioned: string[];
  assessment: string | null;
  plan: string[];
  follow_up: string | null;
  updated_at?: string;
  approved_at?: string;
}

const ReviewPage: React.FC = () => {
  const router = useRouter();
  const { session_id } = router.query;

  const [note, setNote] = useState<MedicalNote | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saveStatus, setSaveStatus] = useState('');

  // Fetch Note Data
  useEffect(() => {
    if (!session_id) return;

    fetch(`http://127.0.0.1:8000/notes/${session_id}`)
      .then(res => {
        if (!res.ok) throw new Error("Note not found");
        return res.json();
      })
      .then(data => {
        setNote(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [session_id]);

  // Handle Input Changes
  const handleChange = (field: keyof MedicalNote, value: any) => {
    if (!note) return;
    setNote({ ...note, [field]: value });
  };

  const handleListChange = (field: keyof MedicalNote, value: string) => {
    if (!note) return;
    const listArray = value.split('\n');
    setNote({ ...note, [field]: listArray });
  };

  // Save Draft
  const saveDraft = async () => {
    if (!note || !session_id) return;
    setSaveStatus('Saving...');
    try {
      const res = await fetch(`http://127.0.0.1:8000/notes/${session_id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(note)
      });
      if (!res.ok) throw new Error("Failed to save");
      setSaveStatus('Draft Saved ✅');
      setTimeout(() => setSaveStatus(''), 3000);
    } catch (err) {
      setSaveStatus('Error saving ❌');
    }
  };

  // Approve Note
  const approveNote = async () => {
    if (!session_id) return;
    if (!confirm("Are you sure you want to approve this note? This will lock the status.")) return;
    
    try {
      const res = await fetch(`http://127.0.0.1:8000/notes/${session_id}/approve`, { method: 'POST' });
      if (!res.ok) throw new Error("Failed to approve");
      
      // Update local state immediately
      setNote(prev => prev ? { ...prev, status: 'approved' } : null);
      alert("Note Approved Successfully!");
    } catch (err) {
      alert("Error approving note");
    }
  };

  // Download PDF (Triggers Browser Save Dialog)
  const downloadPDF = async () => {
    if (!session_id) return;
    
    try {
      // 1. Trigger Generation (POST) to ensure latest version exists
      const genRes = await fetch(`http://127.0.0.1:8000/export/${session_id}`, { method: 'POST' });
      if (!genRes.ok) {
        const text = await genRes.text();
        throw new Error(`Generation failed: ${text}`);
      }

      // 2. Trigger Download (GET)
      // We perform a fetch to get the 'blob' (binary data)
      const downloadRes = await fetch(`http://127.0.0.1:8000/export/${session_id}/download`, { method: 'GET' });
      
      if (!downloadRes.ok) throw new Error("Download failed");

      // 3. Create a blob URL and click it
      const blob = await downloadRes.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Set the filename
      link.setAttribute('download', `Medical_Note_${session_id}.pdf`);
      
      // Append to body, click, and cleanup
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url); // Free up memory

    } catch (err: any) {
      console.error(err);
      alert("Error downloading PDF: " + err.message);
    }
  };

  if (loading) return <div style={{ padding: '20px' }}>Loading session...</div>;
  if (error) return <div style={{ padding: '20px', color: 'red' }}>Error: {error}</div>;
  if (!note) return null;

  const isApproved = note.status === 'approved';

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px', fontFamily: 'sans-serif' }}>
      
      {/* --- Header & Navigation --- */}
      <div style={{ marginBottom: '20px' }}>
        <Link href="/" style={{ textDecoration: 'none', color: '#666', fontSize: '0.9rem' }}>
          ← Back to Dashboard
        </Link>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ margin: 0 }}>🩺 Clinical Review</h1>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
          
          {/* Status Badge */}
          <div style={{ 
            padding: '5px 15px', 
            borderRadius: '20px', 
            background: isApproved ? '#d4edda' : '#fff3cd',
            color: isApproved ? '#155724' : '#856404',
            fontWeight: 'bold',
            fontSize: '0.9rem'
          }}>
            Status: {note.status.toUpperCase()}
          </div>

          {/* Download Button (Only if Approved) */}
          {isApproved && (
            <button 
              onClick={downloadPDF}
              style={{ ...btnStyle, background: '#6610f2', fontSize: '0.9rem', padding: '8px 16px' }}
            >
              📄 Download PDF
            </button>
          )}

        </div>
      </div>

      {/* Safety Banner */}
      {!isApproved && (
        <div style={{ background: '#fff3cd', border: '1px solid #ffeeba', padding: '15px', marginBottom: '20px', borderRadius: '5px', color: '#856404' }}>
          ⚠️ <strong>AI Draft:</strong> This note was generated by AI. Please review and edit carefully before approving.
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px' }}>
        
        {/* Left Column: Transcript */}
        <div>
          <h3>📜 Clean Transcript</h3>
          <div style={{ 
            background: '#f8f9fa', padding: '15px', borderRadius: '5px', 
            height: '600px', overflowY: 'auto', border: '1px solid #ddd', 
            fontSize: '0.9rem', lineHeight: '1.5', whiteSpace: 'pre-wrap'
          }}>
            {note.raw_transcript || "No transcript available."}
          </div>
        </div>

        {/* Right Column: Editable Form */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>📝 Medical Note Draft</h3>
            <span style={{ fontSize: '0.8rem', color: '#666' }}>{saveStatus}</span>
          </div>

          <div style={{ background: 'white', padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
            
            <FormRow label="Chief Complaint">
              <input 
                type="text" 
                value={note.chief_complaint || ''} 
                onChange={e => handleChange('chief_complaint', e.target.value)}
                style={inputStyle}
                disabled={isApproved}
              />
            </FormRow>

            <FormRow label="Duration">
              <input 
                type="text" 
                value={note.duration || ''} 
                onChange={e => handleChange('duration', e.target.value)}
                style={inputStyle}
                disabled={isApproved}
              />
            </FormRow>

            <FormRow label="Symptoms (One per line)">
              <textarea 
                value={note.symptoms ? note.symptoms.join('\n') : ''} 
                onChange={e => handleListChange('symptoms', e.target.value)}
                style={textareaStyle}
                rows={4}
                disabled={isApproved}
              />
            </FormRow>

            <FormRow label="Assessment">
              <textarea 
                value={note.assessment || ''} 
                onChange={e => handleChange('assessment', e.target.value)}
                style={textareaStyle}
                rows={3}
                disabled={isApproved}
              />
            </FormRow>

            <FormRow label="Plan (One per line)">
              <textarea 
                value={note.plan ? note.plan.join('\n') : ''} 
                onChange={e => handleListChange('plan', e.target.value)}
                style={textareaStyle}
                rows={4}
                disabled={isApproved}
              />
            </FormRow>
            
            {/* Action Buttons */}
            <div style={{ marginTop: '20px', display: 'flex', gap: '10px', paddingTop: '20px', borderTop: '1px solid #eee' }}>
              {!isApproved ? (
                <>
                  <button onClick={saveDraft} style={{ ...btnStyle, background: '#6c757d' }}>
                    Save Draft
                  </button>
                  <button onClick={approveNote} style={{ ...btnStyle, background: '#007bff' }}>
                    Approve Note
                  </button>
                </>
              ) : (
                <button disabled style={{ ...btnStyle, background: '#28a745', cursor: 'default' }}>
                  Approved ✅
                </button>
              )}
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

// --- Styles & Helpers ---
const FormRow: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <div style={{ marginBottom: '15px' }}>
    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', fontSize: '0.9rem', color: '#333' }}>
      {label}
    </label>
    {children}
  </div>
);

const inputStyle = {
  width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc', fontSize: '1rem'
};

const textareaStyle = {
  width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ccc', fontSize: '1rem', fontFamily: 'inherit'
};

const btnStyle = {
  padding: '10px 20px', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontSize: '1rem'
};

export default ReviewPage;