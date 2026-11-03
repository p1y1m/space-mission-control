import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Clock, Database, Gauge, Navigation2, Orbit, Satellite as SatelliteIcon } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api'
import type { Satellite } from '../types'
import { Loading, PageHeader, Panel, QualityBadge } from '../components/UI'
import { SatelliteMap } from '../components/SatelliteMap'

export default function SatelliteDetail() {
  const { id } = useParams()
  const { data: s, isLoading, isError } = useQuery({ queryKey: ['satellite', id], queryFn: () => api<Satellite>(`/satellites/${id}`) })
  if (isLoading) return <Loading/>
  if (isError || !s) return <div className="state"><h1>Asset not found</h1><Link to="/satellites">Return to catalog</Link></div>
  return <><Link className="back" to="/satellites"><ArrowLeft/> Back to asset catalog</Link><PageHeader eyebrow={`Asset dossier / NORAD ${s.norad_id}`} title={s.name} description="Orbital identity, propagated location, and source provenance." actions={<QualityBadge/>}/><div className="detail-grid"><Panel className="detail-hero"><div className="detail-symbol"><span/><SatelliteIcon/></div><div><span className={`orbit-badge ${s.orbital_class.toLowerCase()}`}>{s.orbital_class}</span><h2>{s.name}</h2><p>{s.data_source}</p></div></Panel><Panel title="Current estimated position" kicker="PROPAGATED / NOT TELEMETRY" className="detail-map"><SatelliteMap satellites={[s]} selected={s.id} onSelect={() => {}}/></Panel><Panel title="Orbital parameters" kicker="ASSET PROFILE"><div className="parameter-grid"><Parameter icon={<Gauge/>} label="Altitude" value={`${s.altitude_km?.toLocaleString()} km`}/><Parameter icon={<Navigation2/>} label="Velocity" value={`${s.velocity_kps} km/s`}/><Parameter icon={<Orbit/>} label="Period" value={`${s.period_minutes} min`}/><Parameter icon={<SatelliteIcon/>} label="Inclination" value={`${s.inclination_deg}°`}/></div></Panel><Panel title="Data provenance" kicker="TRANSPARENCY"><dl className="provenance"><div><dt><Database/> Source</dt><dd>{s.data_source}</dd></div><div><dt><Clock/> Catalog timestamp</dt><dd>{new Date(s.updated_at).toLocaleString()}</dd></div><div><dt>Quality classification</dt><dd>{s.data_quality.replaceAll('_', ' ')}</dd></div></dl><div className="banner warning">This portfolio catalog uses bundled illustrative propagation estimates. It does not ingest spacecraft telemetry or provide command capability.</div></Panel></div></>
}
function Parameter({icon, label, value}: {icon: React.ReactNode; label: string; value: string}) { return <div>{icon}<span>{label}</span><strong>{value}</strong></div> }
