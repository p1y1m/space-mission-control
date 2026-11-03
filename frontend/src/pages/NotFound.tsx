import { Orbit } from 'lucide-react'
import { Link } from 'react-router-dom'
export default function NotFound(){return <main className="fatal"><Orbit/><span className="eyebrow">NAVIGATION ANOMALY</span><h1>Lost in orbit</h1><p>The requested flight path does not exist.</p><Link className="button primary" to="/">Return to mission control</Link></main>}
