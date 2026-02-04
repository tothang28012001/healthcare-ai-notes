import React, { useEffect, useState } from 'react';
import Link from 'next/link';

interface SessionSummary {
  session_id: string;
  created_at: string;
  chief_complaint: string;
  status: string;
  preview: string;
}

export default function Dashboard() {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSessions = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/sessions');
      const data = await res.json();
      setSessions(data.sessions || []);
    } catch (error) {
      console.error("Failed to load sessions", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '40px 20px', fontFamily: 'sans-serif' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
        <div>
          <h1 style={{ margin: 0, color: '#2c3e50' }}>MediScribe AI</h1>
          <p style={{ margin: '5px 0 0 0', color: '#7f8c8d' }}>Clinician Dashboard</p>
        </div>
        
        <Link href="/record" style={{ textDecoration: 'none' }}>
          <button style={primaryBtnStyle}>
            + New Session
          </button>
        </Link>
      </div>

      {/* Session List */}
      <div style={{ background: 'white', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <div style={{ padding: '15px 20px', background: '#f8f9fa', borderBottom: '1px solid #eee', fontWeight: 'bold', color: '#555', display: 'grid', gridTemplateColumns: '2fr 3fr 1fr 1fr 1fr', gap: '10px' }}>
          <span>Date</span>
          <span>Chief Complaint</span>
          <span>Status</span>
          <span>Details</span>
          <span>Action</span>
        </div>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#888' }}>Loading sessions...</div>
        ) : sessions.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#888' }}>
            No sessions found. Start a new recording!
          </div>
        ) : (
          sessions.map((session) => (
            <div key={session.session_id} style={{ padding: '15px 20px', borderBottom: '1px solid #eee', display: 'grid', gridTemplateColumns: '2fr 3fr 1fr 1fr 1fr', gap: '10px', alignItems: 'center' }}>
              <span style={{ fontSize: '0.9rem', color: '#555' }}>
                {new Date(session.created_at).toLocaleString()}
              </span>
              <span style={{ fontWeight: '500', color: '#2c3e50' }}>
                {session.chief_complaint || "—"}
              </span>
              <span>
                <span style={statusBadgeStyle(session.status)}>
                  {session.status.toUpperCase()}
                </span>
              </span>
              <span style={{ fontSize: '0.85rem', color: '#888' }}>
                {session.preview}
              </span>
              <Link href={`/review/${session.session_id}`} style={{ textDecoration: 'none', color: '#007bff', fontWeight: 'bold', fontSize: '0.9rem' }}>
                Open →
              </Link>
            </div>
          ))
        )}
      </div>

      <div style={{ marginTop: '30px', textAlign: 'center', fontSize: '0.8rem', color: '#aaa' }}>
        <p>Phase 10: Full Product UX • Encrypted & Audited</p>
      </div>
    </div>
  );
}

// Styles
const primaryBtnStyle = {
  padding: '12px 24px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '6px', fontSize: '1rem', cursor: 'pointer', fontWeight: 'bold', boxShadow: '0 2px 4px rgba(0,123,255,0.3)'
};

const statusBadgeStyle = (status: string) => ({
  padding: '4px 8px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 'bold' as 'bold',
  backgroundColor: status === 'approved' ? '#d4edda' : '#fff3cd',
  color: status === 'approved' ? '#155724' : '#856404',
  textTransform: 'uppercase' as 'uppercase'
});