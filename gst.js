import { useState } from 'react';
import NavBar from '../components/NavBar';

/**
 * Page for uploading GST/IT notices and receiving AI‑generated draft replies.
 * Users can upload the notice file and optional supporting documents.
 */
export default function GSTNotice() {
  const [noticeFile, setNoticeFile] = useState(null);
  const [supportFiles, setSupportFiles] = useState([]);
  const [reply, setReply] = useState('');
  const [missing, setMissing] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!noticeFile) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('notice', noticeFile);
    supportFiles.forEach((file) => {
      formData.append('additional_documents', file);
    });
    try {
      const backendURL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const res = await fetch(`${backendURL}/gst_notice`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setReply(data.reply);
      setMissing(data.missing_documents || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '1rem' }}>
      <NavBar />
      <h1>GST Notice Analysis</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: '1rem' }}>
        <div style={{ marginBottom: '0.5rem' }}>
          <label>
            Notice File:
            <input
              type="file"
              accept=".pdf,.txt"
              onChange={(e) => setNoticeFile(e.target.files[0])}
            />
          </label>
        </div>
        <div style={{ marginBottom: '0.5rem' }}>
          <label>
            Supporting Documents:
            <input
              type="file"
              multiple
              onChange={(e) => setSupportFiles(Array.from(e.target.files))}
            />
          </label>
        </div>
        <button type="submit">Submit</button>
      </form>
      {loading && <p>Processing…</p>}
      {missing.length > 0 && (
        <div>
          <h2>Missing Documents</h2>
          <ul>
            {missing.map((d) => (
              <li key={d}>{d}</li>
            ))}
          </ul>
        </div>
      )}
      {reply && (
        <div>
          <h2>Draft Reply</h2>
          <pre style={{ whiteSpace: 'pre-wrap' }}>{reply}</pre>
        </div>
      )}
    </div>
  );
}