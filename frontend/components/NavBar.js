import Link from 'next/link';

export default function NavBar() {
  const navStyle = {
    display: 'flex',
    gap: '1rem',
    padding: '1rem',
    borderBottom: '1px solid #ccc',
    marginBottom: '1rem',
    alignItems: 'center',
  };

  return (
    <nav style={navStyle}>
      <Link href="/">Dashboard</Link>
      <Link href="/clients">Clients</Link>
      <Link href="/tasks">Tasks</Link>
      <Link href="/appointments">Appointments</Link>
      <Link href="/gst">GST Notice</Link>
      <Link href="/tally">Tally Import</Link>
      <Link href="/login">Login</Link>
    </nav>
  );
}
