import { useQuery } from '@tanstack/react-query'
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Activity, Gauge, Radar, Satellite } from 'lucide-react'
import { api } from '../api'
import type { Analytics as AnalyticsType } from '../types'
import { Loading, PageHeader, Panel } from '../components/UI'

const colors = ['#26d9ff', '#7c6cff', '#21df9a', '#ff9f43']
export default function Analytics() {
  const { data, isLoading } = useQuery({ queryKey: ['analytics'], queryFn: () => api<AnalyticsType>('/analytics') })
  if (isLoading) return <Loading label="Computing mission analytics"/>
  const orbit = Object.entries(data?.satellites_by_orbit || {}).map(([name, value]) => ({ name, value }))
  const missions = Object.entries(data?.mission_status || {}).map(([name, value]) => ({ name, value }))
  const watch = Object.entries(data?.watchlist_by_orbit || {}).map(([name, value]) => ({ name, value }))
  return <><PageHeader eyebrow="Intelligence cell / analytics" title="Operational analytics" description="Database-backed insights across the catalog, watchlist, and mission portfolio."/><div className="metric-grid analytics-metrics"><Metric icon={<Satellite/>} label="Catalog assets" value={data?.tracked_satellites || 0}/><Metric icon={<Gauge/>} label="Average altitude" value={`${data?.average_altitude_km.toLocaleString()} km`}/><Metric icon={<Radar/>} label="Mission states" value={missions.length}/><Metric icon={<Activity/>} label="Watchlist classes" value={watch.length}/></div><div className="analytics-grid"><Panel title="Catalog by orbital class" kicker="GLOBAL DISTRIBUTION"><ChartPie data={orbit}/></Panel><Panel title="Mission status distribution" kicker="PRIVATE PORTFOLIO"><div className="chart-wrap"><ResponsiveContainer><BarChart data={missions.length ? missions : [{name:'No missions',value:0}]}><CartesianGrid stroke="#15263b" vertical={false}/><XAxis dataKey="name" stroke="#6c8199"/><YAxis allowDecimals={false} stroke="#6c8199"/><Tooltip contentStyle={tip}/><Bar dataKey="value" fill="#26d9ff" radius={[5,5,0,0]}/></BarChart></ResponsiveContainer></div></Panel><Panel title="Watchlist composition" kicker="PRIVATE ASSET MIX"><ChartPie data={watch}/></Panel><Panel title="Interpretation notes" kicker="DATA SCOPE"><div className="insights"><p><strong>Catalog scope</strong><span>The included catalog is bounded for a responsive portfolio demonstration.</span></p><p><strong>Position quality</strong><span>Map coordinates are labeled propagated demo estimates, not live telemetry.</span></p><p><strong>Private metrics</strong><span>Mission and watchlist aggregates are scoped to the authenticated operator.</span></p></div></Panel></div></>
}
const tip = { background: '#091423', border: '1px solid #1c3855', borderRadius: 8, color: '#d9e8f5' }
function Metric({icon,label,value}:{icon:React.ReactNode;label:string;value:string|number}) {return <div className="metric blue"><div className="metric-icon">{icon}</div><span>{label}</span><strong>{value}</strong><small>Database snapshot</small></div>}
function ChartPie({data}:{data:{name:string;value:number}[]}) { const d=data.length?data:[{name:'No data',value:1}];return <><div className="chart-wrap pie"><ResponsiveContainer><PieChart><Pie data={d} dataKey="value" innerRadius={48} outerRadius={78}>{d.map((_,i)=><Cell key={i} fill={data.length?colors[i%colors.length]:'#243449'}/>)}</Pie><Tooltip contentStyle={tip}/></PieChart></ResponsiveContainer></div><div className="orbit-rows">{data.map((x,i)=><div key={x.name}><i style={{background:colors[i]}}/><span>{x.name}</span><strong>{x.value}</strong></div>)}</div></>}
