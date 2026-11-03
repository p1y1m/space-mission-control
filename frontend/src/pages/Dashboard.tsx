import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Area, AreaChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { ArrowUpRight, Clock3, Gauge, Radio, Satellite as SatelliteIcon, ShieldCheck } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import type { Satellite, SatellitePage } from '../types'
import { SatelliteMap } from '../components/SatelliteMap'
import { Loading, PageHeader, Panel, QualityBadge, Status } from '../components/UI'

const COLORS = ['#26d9ff', '#7c6cff', '#21df9a']
const altitudeSeries = [{ t: '00', v: 402 }, { t: '04', v: 407 }, { t: '08', v: 416 }, { t: '12', v: 410 }, { t: '16', v: 419 }, { t: '20', v: 417 }, { t: '24', v: 421 }]

export default function Dashboard() {
  const { data, isLoading, isError } = useQuery({ queryKey: ['satellites', 'dashboard'], queryFn: () => api<SatellitePage>('/satellites?page_size=50') })
  const [selectedId, setSelectedId] = useState<number>()
  const selected = data?.items.find(s => s.id === selectedId) || data?.items[0]
  const orbit = useMemo(() => Object.entries((data?.items || []).reduce<Record<string, number>>((a, s) => ({ ...a, [s.orbital_class]: (a[s.orbital_class] || 0) + 1 }), {})).map(([name, value]) => ({ name, value })), [data])
  if (isLoading) return <Loading/>
  return <>
    <PageHeader eyebrow="Mission control / overview" title="Orbital operations" description="A unified view of tracked assets, propagation estimates, and planning activity." actions={<><div className="live-pill"><i/> SYSTEM ONLINE</div><span className="utc"><Clock3/> UTC {new Date().toISOString().slice(11, 16)}</span></>}/>
    {isError && <div className="banner error">API link unavailable. Start the backend to load current catalog data.</div>}
    <div className="metric-grid">
      <Metric label="Tracked assets" value={data?.total ?? 0} meta="Bounded catalog" icon={<SatelliteIcon/>}/>
      <Metric label="Operational state" value="Nominal" meta="All services" icon={<ShieldCheck/>} accent="green"/>
      <Metric label="Mean altitude" value={`${Math.round((data?.items.reduce((a, s) => a + (s.altitude_km || 0), 0) || 0) / (data?.items.length || 1)).toLocaleString()} km`} meta="Estimated" icon={<Gauge/>}/>
      <Metric label="Active alerts" value="02" meta="Demo advisories" icon={<Radio/>} accent="orange"/>
    </div>
    <div className="dashboard-grid">
      <Panel className="map-panel" title="Orbital position matrix" kicker="GLOBAL TRACKING" action={<div className="legend"><span><i className="leo"/>LEO</span><span><i className="meo"/>MEO</span><span><i className="geo"/>GEO</span></div>}>
        <QualityBadge/>
        <SatelliteMap satellites={data?.items || []} selected={selected?.id} onSelect={(s) => setSelectedId(s.id)}/>
      </Panel>
      <Panel className="selected-panel" kicker="SELECTED ASSET" title={selected?.name || 'No asset selected'} action={<Status/>}>
        {selected && <Selected satellite={selected}/>} 
      </Panel>
      <Panel title="Orbit distribution" kicker="CATALOG COMPOSITION"><div className="chart-wrap pie"><ResponsiveContainer><PieChart><Pie data={orbit} dataKey="value" innerRadius={55} outerRadius={76} paddingAngle={5}>{orbit.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]}/>)}</Pie><Tooltip contentStyle={tooltipStyle}/></PieChart></ResponsiveContainer><div className="chart-center"><strong>{data?.total}</strong><span>ASSETS</span></div></div><div className="orbit-rows">{orbit.map((o, i) => <div key={o.name}><i style={{background: COLORS[i]}}/><span>{o.name}</span><strong>{o.value}</strong></div>)}</div></Panel>
      <Panel className="trend" title="Altitude variance" kicker="ISS REFERENCE / 24H" action={<span className="positive">+0.8% <ArrowUpRight/></span>}><div className="chart-wrap"><ResponsiveContainer><AreaChart data={altitudeSeries}><defs><linearGradient id="alt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#26d9ff" stopOpacity={0.3}/><stop offset="1" stopColor="#26d9ff" stopOpacity={0}/></linearGradient></defs><CartesianGrid stroke="#15263b" vertical={false}/><XAxis dataKey="t" stroke="#5d7089" tickLine={false}/><YAxis domain={[390, 430]} stroke="#5d7089" tickLine={false}/><Tooltip contentStyle={tooltipStyle}/><Area type="monotone" dataKey="v" stroke="#26d9ff" fill="url(#alt)" strokeWidth={2}/></AreaChart></ResponsiveContainer></div></Panel>
      <Panel title="Operations log" kicker="RECENT ACTIVITY"><div className="activity-list"><Activity dot="blue" time="02 min" title="Catalog synchronized" text="16 asset records validated"/><Activity dot="green" time="18 min" title="Propagation window computed" text="ISS orbital estimate refreshed"/><Activity dot="orange" time="43 min" title="Advisory threshold" text="GOES-17 sample age exceeds target"/></div></Panel>
    </div>
  </>
}

const tooltipStyle = { background: '#091423', border: '1px solid #1c3855', borderRadius: 8, color: '#d9e8f5' }
function Metric({ label, value, meta, icon, accent = 'blue' }: { label: string; value: string | number; meta: string; icon: React.ReactNode; accent?: string }) { return <div className={`metric ${accent}`}><div className="metric-icon">{icon}</div><span>{label}</span><strong>{value}</strong><small>{meta}</small></div> }
function Selected({ satellite: s }: { satellite: Satellite }) { return <div className="selected-body"><div className="sat-visual"><div className="planet-ring"/><SatelliteIcon/></div><div className="coords"><div><span>LATITUDE</span><strong>{s.latitude?.toFixed(2)}°</strong></div><div><span>LONGITUDE</span><strong>{s.longitude?.toFixed(2)}°</strong></div></div><dl><div><dt>NORAD ID</dt><dd>{s.norad_id}</dd></div><div><dt>ORBIT</dt><dd>{s.orbital_class}</dd></div><div><dt>ALTITUDE</dt><dd>{s.altitude_km?.toLocaleString()} km</dd></div><div><dt>VELOCITY</dt><dd>{s.velocity_kps} km/s</dd></div></dl><p className="data-note">Position is a bundled demonstration propagation estimate, not observed telemetry.</p><Link className="button secondary" to={`/satellites/${s.id}`}>Open asset dossier <ArrowUpRight/></Link></div> }
function Activity({ dot, time, title, text }: { dot: string; time: string; title: string; text: string }) { return <div className="activity"><i className={dot}/><div><strong>{title}</strong><span>{text}</span></div><time>{time}</time></div> }
