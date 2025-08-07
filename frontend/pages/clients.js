import { useState, useEffect } from 'react';
import axios from 'axios';
import NavBar from '../components/NavBar';

/**
 * Client management page. Lists existing clients and provides a simple form
 * for creating new ones. Communicates directly with the backend API using
 * the NEXT_PUBLIC_BACKEND_URL environment variable.
 */
export default function Clients() {
  const [clients, setClients] = useState([]);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');

  const baseURL =
    process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000';

  const fetchClients = async () => {
    try {
      const { data } = await axios.get(`${baseURL}/clients`);
      setClients(data);
    } catch (err) {
      console.error(err);
      setError('Failed to load clients');
    }
  };

  useEffect(() => {
    fetchClients();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name) return;
    try {
      const { data } = await axios.post(`${baseURL}/clients`, {
        name,
        email: email || undefined,
      });
      setClients([...clients, data]);
      setName('');
      setEmail('');
      setError('');
    } catch (err) {
      console.error(err);
      setError('Failed to create client');
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '1rem' }}>
      <NavBar />
      <h1>Clients</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: '1rem' }}>
        <div style={{ marginBottom: '0.5rem' }}>
          <label>
            Name:{' '}
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </label>
        </div>
        <div style={{ marginBottom: '0.5rem' }}>
          <label>
            Email:{' '}
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>
        </div>
        <button type="submit">Add Client</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <h2>Client List</h2>
      {clients.length === 0 ? (
        <p>No clients yet.</p>
      ) : (
        <ul>
          {clients.map((client) => (
            <li key={client.id}>
              {client.name} {client.email ? `(${client.email})` : ''}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
