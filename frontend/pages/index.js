import { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [input, setInput] = useState('');
  const [reply, setReply] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/generate', { prompt: input });
      setReply(response.data.reply);
    } catch (error) {
      console.error(error);
      setReply('Error generating reply');
    }
  };

  return (
    <div style={{ margin: '2rem' }}>
      <h1>CA Suite Frontend</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          rows="4"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter your query here"
          style={{ width: '100%', padding: '0.5rem' }}
        />
        <button type="submit" style={{ marginTop: '1rem' }}>
          Generate Reply
        </button>
      </form>
      {reply && (
        <div style={{ marginTop: '2rem', whiteSpace: 'pre-wrap' }}>
          <h2>Reply:</h2>
          <p>{reply}</p>
        </div>
      )}
    </div>
  );
}
