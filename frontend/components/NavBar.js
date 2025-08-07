import Link from 'next/link';

/**
 * Simple navigation bar component. Displays links to the main sections of
 * the application. Uses Next.js <Link> for client-side navigation.
 */
export default function NavBar() {
  const navStyle = {
    display: 'flex',
    gap: '1rem',
    padding: '1rem 0',
    borderBottom: '1px solid #ccc',
    marginBottom: '1rem',
  };

  return (
    <nav style={navStyle}>
      <Link href="/">Home</Link>
      <Link href="/clients">Clients</Link>
      <Link href="/tasks">Tasks</Link>
      <Link href="/appointments">Appointments</Link>
    </nav>
  );
}
