import { FormEvent, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ArrowUpRight, Filter, Search, Satellite as SatelliteIcon } from 'lucide-react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../api'
import type { SatellitePage } from '../types'
import { Empty, Loading, PageHeader, QualityBadge } from '../components/UI'

export default function Satellites() {
  const [params, setParams] = useSearchParams()
  const [term, setTerm] = useState(params.get('search') || '')
  const page = Number(params.get('page') || 1), orbit = params.get('orbit') || ''
  const query = `/satellites?page=${page}&page_size=12&search=${encodeURIComponent(params.get('search') || '')}${orbit ? `&orbit=${orbit}` : ''}`
  const { data, isLoading } = useQuery({ queryKey: ['satellites', query], queryFn: () => api<SatellitePage>(query) })
  function submit(e: FormEvent) { e.preventDefault(); setParams(p => { if (term) p.set('search', term); else p.delete('search'); p.set('page', '1'); return p }) }
  function setOrbit(value: string) { setParams(p => { if (value) p.set('orbit', value); else p.delete('orbit'); p.set('page', '1'); return p }) }
  return <>
    <PageHeader eyebrow="Asset intelligence / catalog" title="Satellite explorer" description="Search and inspect the bounded orbital asset catalog." actions={<QualityBadge/>}/>
    <div className="filterbar"><form onSubmit={submit}><Search/><input aria-label="Search satellites" value={term} onChange={e => setTerm(e.target.value)} placeholder="Search name or NORAD ID…"/><button>Search</button></form><div className="select-wrap"><Filter/><select aria-label="Filter by orbit" value={orbit} onChange={e => setOrbit(e.target.value)}><option value="">All orbital classes</option><option>LEO</option><option>MEO</option><option>GEO</option></select></div></div>
    {isLoading ? <Loading/> : !data?.items.length ? <Empty title="No matching assets" text="Adjust your search or orbital class filter."/> : <><div className="catalog-grid">{data.items.map(s => <Link to={`/satellites/${s.id}`} className="asset-card" key={s.id}><div className="asset-top"><span className={`orbit-badge ${s.orbital_class.toLowerCase()}`}>{s.orbital_class}</span><ArrowUpRight/></div><div className="asset-symbol"><SatelliteIcon/></div><h2>{s.name}</h2><p>NORAD {s.norad_id}</p><div className="asset-data"><div><span>ALTITUDE</span><strong>{s.altitude_km?.toLocaleString()} km</strong></div><div><span>VELOCITY</span><strong>{s.velocity_kps} km/s</strong></div><div><span>INCLINATION</span><strong>{s.inclination_deg}°</strong></div><div><span>PERIOD</span><strong>{s.period_minutes} min</strong></div></div><small><i/> Demo propagation estimate</small></Link>)}</div><div className="pagination"><button disabled={page <= 1} onClick={() => setParams(p => { p.set('page', String(page - 1)); return p })}>Previous</button><span>Page {data.page} / {data.pages} · {data.total} assets</span><button disabled={page >= data.pages} onClick={() => setParams(p => { p.set('page', String(page + 1)); return p })}>Next</button></div></>}
  </>
}
