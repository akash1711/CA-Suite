import { useState, useEffect } from 'react';
import axios from 'axios';
import NavBar from '../components/NavBar';

export default function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState('');
  const [clientId, setClientId] = useState('');
  const [assignedTo, setAssignedTo] = useState('');

  const backendURL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const res = await axios.get(`${backendURL}/tasks`);
      setTasks(res.data);
    } catch (error) {
      console.error('Error fetching tasks', error);
    }
  };

  const createTask = async () => {
    try {
      await axios.post(`${backendURL}/tasks`, {
        title,
        description,
        status,
        client_id: clientId ? parseInt(clientId) : undefined,
        assigned_to: assignedTo || undefined,
      });
      setTitle('');
      setDescription('');
      setStatus('');
      setClientId('');
      setAssignedTo('');
      fetchTasks();
    } catch (error) {
      console.error('Error creating task', error);
    }
  };

  return (
    <div>
      <NavBar />
      <h1>Task Management</h1>
      <div>
        <input
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <input
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <input
          placeholder="Status"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        />
        <input
          placeholder="Client ID"
          value={clientId}
          onChange={(e) => setClientId(e.target.value)}
        />
        <input
          placeholder="Assigned To"
          value={assignedTo}
          onChange={(e) => setAssignedTo(e.target.value)}
        />
        <button onClick={createTask}>Add Task</button>
      </div>
      <ul>
        {tasks.map((task) => (
          <li key={task.id}>
            {task.title} ({task.status}) - Client: {task.client_id || 'N/A'}, Assigned to: {task.assigned_to || 'N/A'}
          </li>
        ))}
      </ul>
    </div>
  );
}
