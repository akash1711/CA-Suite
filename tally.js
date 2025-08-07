import { useState } from 'react';
import NavBar from '../components/NavBar';

/**
 * Page for importing transaction data exported from Tally or other accounting
 * software and viewing a simple summary of numeric totals.  Users can upload
 * a CSV or JSON file; the backend will return sums of numeric columns.
 */
export default function TallyImport() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
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
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '1rem' }}>
      <NavBar />
      <h1>Tally Data Import</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: '1rem' }}>
        <input
          type="file"
          accept=".csv,.json"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button type="submit">Upload</button>
      </form>
      {loading && <p>Uploading…</p>}
      {result && (
        <div>
          <h2>Summary</h2>
          <p>Rows processed: {result.row_count}</p>
          <h3>Totals</h3>
          <ul>
            {result.totals &&
              Object.entries(result.totals).map(([key, value]) => (
                <li key={key}>
                  {key}: {value}
                </li>
              ))}
          </ul>
        </div>
      )}
    </div>
  );
}