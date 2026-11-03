import { Activity, BarChart3, Binoculars, CircleUserRound, Command, LogOut, Menu, Radar, Satellite, ShieldCheck, X } from 'lucide-react'
import { ReactNode, useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from './AuthProvider'

const nav = [
  ['/', Command, 'Overview'], ['/satellites', Satellite, 'Satellite Explorer'],
  ['/watchlist', Binoculars, 'Watchlist'], ['/missions', Radar, 'Missions'],
  ['/analytics', BarChart3, 'Analytics'], ['/account', CircleUserRound, 'Account'],
] as const

export function Layout({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false)
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  async function signOut() { await logout(); navigate('/login') }
  return <div className="shell">
    <header className="mobile-header"><Logo /><button className="icon-button" onClick={() => setOpen(!open)} aria-label="Toggle navigation">{open ? <X /> : <Menu />}</button></header>
    <aside className={`sidebar ${open ? 'open' : ''}`}>
      <Logo />
      <div className="sector"><span>CONTROL SECTOR</span><strong>ORBITAL / 07</strong></div>
      <nav>{nav.map(([to, Icon, label]) => <NavLink key={to} to={to} end={to === '/'} onClick={() => setOpen(false)}><Icon size={18}/><span>{label}</span></NavLink>)}</nav>
      <div className="sidebar-foot">
        <div className="security"><ShieldCheck size={16}/><div><strong>SECURE LINK</strong><span>Encrypted session</span></div><i /></div>
        {user && <div className="operator"><div className="avatar">{user.display_name.slice(0, 2).toUpperCase()}</div><div><strong>{user.display_name}</strong><span>Mission operator</span></div><button onClick={signOut} aria-label="Log out"><LogOut size={17}/></button></div>}
      </div>
    </aside>
    <main className="workspace">{children}</main>
  </div>
}

function Logo() { return <div className="logo"><div className="logo-orbit"><Activity size={20}/></div><div><strong>ASTRA</strong><span>COMMAND</span></div></div> }
