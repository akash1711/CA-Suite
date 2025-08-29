import React, { useState } from 'react';
import NavBar from '../components/NavBar';

/**
 * Tally import page. Allows CAs to upload a CSV or JSON export from Tally.
 * Sends the file to the backend `/import_tally` endpoint and displays simple totals and record count.
 */
export default function TallyImport() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);
    try {
      const backendURL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const res = await fetch(`${backendURL}/import_tally`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setResult({ error: 'Failed to import file' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <NavBar />
      <div style={{ padding: '1rem' }}>
        <h1>Tally Import</h1>
        <form onSubmit={handleSubmit} style={{ marginBottom: '1rem' }}>
          <input type="file" accept=".csv,.json" onChange={handleFileChange} />
          <button type="submit" disabled={loading} style={{ marginLeft: '0.5rem' }}>
            {loading ? 'Processing...' : 'Upload'}
          </button>
        </form>
        {result && (
          <div>
            <h2>Summary</h2>
            {result.error && <p style={{ color: 'red' }}>{result.error}</p>}
            {result.rows !== undefined && <p>Rows: {result.rows}</p>}
            {result.totals && (
              <div>
                <h3>Totals</h3>
                <ul>
                  {Object.entries(result.totals).map(([col, total]) => (
                    <li key={col}>
                      {col}: {total}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}
