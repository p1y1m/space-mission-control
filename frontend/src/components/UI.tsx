import { ReactNode } from 'react'
import { AlertTriangle, CheckCircle2, LoaderCircle, Radio } from 'lucide-react'

export function PageHeader({ eyebrow, title, description, actions }: { eyebrow: string; title: string; description: string; actions?: ReactNode }) {
  return <header className="page-header"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{description}</p></div>{actions && <div className="page-actions">{actions}</div>}</header>
}
export function Panel({ title, kicker, children, className = '', action }: { title?: string; kicker?: string; children: ReactNode; className?: string; action?: ReactNode }) {
  return <section className={`panel ${className}`}>{(title || action) && <header className="panel-head"><div>{kicker && <span>{kicker}</span>}{title && <h2>{title}</h2>}</div>{action}</header>}{children}</section>
}
export function Status({ online = true }: { online?: boolean }) { return <span className={`status ${online ? 'online' : 'warning'}`}>{online ? <CheckCircle2/> : <AlertTriangle/>}{online ? 'Nominal' : 'Attention'}</span> }
export function Loading({ label = 'Synchronizing orbital data' }: { label?: string }) { return <div className="state"><LoaderCircle className="spin"/><p>{label}</p></div> }
export function Empty({ title, text }: { title: string; text: string }) { return <div className="state empty"><Radio/><h3>{title}</h3><p>{text}</p></div> }
export function QualityBadge() { return <span className="quality"><i/> DEMO PROPAGATION</span> }
