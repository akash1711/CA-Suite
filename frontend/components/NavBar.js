import Link from 'next/link';

/**
 * A simple, modern navigation bar with links to all major sections of the
 * application. Uses inline styles for quick customization. You can replace
 * these styles with CSS modules or a utility framework like Tailwind if
 * desired.
 */
export default function NavBar() {
  const navStyle = {
    display: 'flex',
    gap: '1rem',
    padding: '1rem',
    backgroundColor: '#f8f9fa',
    borderBottom: '1px solid #eaeaea'
  };
  const linkStyle = {
    textDecoration: 'none',
    color: '#0070f3'
  };
  return (
    <nav style={navStyle}>
      <Link href="/" style={linkStyle}>Home</Link>
      <Link href="/clients" style={linkStyle}>Clients</Link>
      <Link href="/tasks" style={linkStyle}>Tasks</Link>
      <Link href="/appointments" style={linkStyle}>Appointments</Link>
      <Link href="/gst" style={linkStyle}>GST Notice</Link>
      <Link href="/tally" style={linkStyle}>Tally Import</Link>
      <Link href="/login" style={linkStyle}>Login</Link>
    </nav>
  );
}
