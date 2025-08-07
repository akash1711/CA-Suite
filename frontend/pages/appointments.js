import { useState, useEffect } from 'react';
import axios from 'axios';
import NavBar from '../components/NavBar';

export default function Appointments() {
  const [appointments, setAppointments] = useState([]);
  const [clientId, setClientId] = useState('');
  const [scheduledTime, setScheduledTime] = useState('');

  const backendURL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      const res = await axios.get(`${backendURL}/appointments`);
      setAppointments(res.data);
    } catch (error) {
      console.error('Error fetching appointments', error);
    }
  };

  const scheduleAppointment = async () => {
    try {
      await axios.post(`${backendURL}/appointments`, {
        client_id: clientId ? parseInt(clientId) : undefined,
        scheduled_time: scheduledTime,
      });
      setClientId('');
      setScheduledTime('');
      fetchAppointments();
    } catch (error) {
      console.error('Error scheduling appointment', error);
    }
  };

  return (
    <div>
      <NavBar />
      <h1>Appointment Scheduling</h1>
      <div>
        <input
          placeholder="Client ID"
          value={clientId}
          onChange={(e) => setClientId(e.target.value)}
        />
        <input
          type="datetime-local"
          value={scheduledTime}
          onChange={(e) => setScheduledTime(e.target.value)}
        />
        <button onClick={scheduleAppointment}>Schedule</button>
      </div>
      <ul>
        {appointments.map((app) => (
          <li key={app.id}>
            Client {app.client_id || 'N/A'} at {new Date(app.scheduled_time).toLocaleString()}
          </li>
        ))}
      </ul>
    </div>
  );
}
