import { FormEvent, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CalendarClock, Pencil, Plus, Radar, Satellite, Trash2, X } from 'lucide-react'
import { api } from '../api'
import type { Mission, SatellitePage } from '../types'
import { Empty, Loading, PageHeader, Panel } from '../components/UI'

type MissionForm = { name: string; description: string; status: string; priority: string; satellite_ids: number[] }
const blank: MissionForm = { name: '', description: '', status: 'planned', priority: 'medium', satellite_ids: [] }

export default function Missions() {
  const qc = useQueryClient(); const [editing, setEditing] = useState<Mission | 'new' | null>(null)
  const missions = useQuery({ queryKey: ['missions'], queryFn: () => api<Mission[]>('/missions') })
  const catalog = useQuery({ queryKey: ['satellites', 'mission-picker'], queryFn: () => api<SatellitePage>('/satellites?page_size=50') })
  const remove = useMutation({ mutationFn: (id: string) => api(`/missions/${id}`, { method: 'DELETE' }), onSuccess: () => qc.invalidateQueries({ queryKey: ['missions'] }) })
  return <><PageHeader eyebrow="Planning cell / missions" title="Mission portfolio" description="Plan simulated observation campaigns and associate catalog assets." actions={<button className="button primary" onClick={() => setEditing('new')}><Plus/> New mission</button>}/>
    {editing && <MissionModal mission={editing === 'new' ? undefined : editing} satellites={catalog.data?.items || []} close={() => setEditing(null)}/>} 
    {missions.isLoading ? <Loading/> : !missions.data?.length ? <Empty title="No missions planned" text="Create a mission to organize satellites around an operational objective."/> : <div className="mission-grid">{missions.data.map(m => <Panel key={m.id} className="mission-card"><div className="mission-top"><span className={`mission-status ${m.status}`}>{m.status}</span><span className={`priority ${m.priority}`}>{m.priority} priority</span></div><div className="mission-icon"><Radar/></div><h2>{m.name}</h2><p>{m.description || 'No mission brief supplied.'}</p><div className="mission-meta"><span><Satellite/> {m.satellites.length} assigned assets</span><span><CalendarClock/> Updated {new Date(m.updated_at).toLocaleDateString()}</span></div><div className="assigned">{m.satellites.slice(0, 3).map(s => <span key={s.id}>{s.name}</span>)}{m.satellites.length > 3 && <span>+{m.satellites.length - 3}</span>}</div><div className="card-actions"><button className="danger-link" onClick={() => remove.mutate(m.id)}><Trash2/> Delete</button><button className="button secondary" onClick={() => setEditing(m)}><Pencil/> Edit mission</button></div></Panel>)}</div>}
  </>
}

function MissionModal({ mission, satellites, close }: { mission?: Mission; satellites: SatellitePage['items']; close: () => void }) {
  const qc = useQueryClient(); const [form, setForm] = useState<MissionForm>(mission ? { name: mission.name, description: mission.description, status: mission.status, priority: mission.priority, satellite_ids: mission.satellites.map(s => s.id) } : blank)
  const save = useMutation({ mutationFn: () => api(mission ? `/missions/${mission.id}` : '/missions', { method: mission ? 'PATCH' : 'POST', body: JSON.stringify(form) }), onSuccess: () => { qc.invalidateQueries({ queryKey: ['missions'] }); close() } })
  function submit(e: FormEvent) { e.preventDefault(); save.mutate() }
  function toggle(id: number) { setForm(f => ({ ...f, satellite_ids: f.satellite_ids.includes(id) ? f.satellite_ids.filter(x => x !== id) : [...f.satellite_ids, id] })) }
  return <div className="modal-backdrop" role="dialog" aria-modal="true"><form className="modal mission-form" onSubmit={submit}><header><div><span className="eyebrow">SIMULATED PLANNING</span><h2>{mission ? 'Edit mission' : 'Create mission'}</h2></div><button type="button" className="icon-button" onClick={close}><X/></button></header><label>Mission name<input required minLength={2} value={form.name} onChange={e => setForm({...form, name: e.target.value})}/></label><label>Mission brief<textarea value={form.description} onChange={e => setForm({...form, description: e.target.value})}/></label><div className="form-row"><label>Status<select value={form.status} onChange={e => setForm({...form, status: e.target.value})}><option value="planned">Planned</option><option value="active">Active</option><option value="paused">Paused</option><option value="completed">Completed</option></select></label><label>Priority<select value={form.priority} onChange={e => setForm({...form, priority: e.target.value})}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option></select></label></div><fieldset><legend>Assign catalog assets</legend><div className="asset-checks">{satellites.map(s => <label key={s.id}><input type="checkbox" checked={form.satellite_ids.includes(s.id)} onChange={() => toggle(s.id)}/><span>{s.name}<small>{s.orbital_class} · {s.norad_id}</small></span></label>)}</div></fieldset>{save.error && <p className="form-error">{save.error.message}</p>}<footer><button type="button" className="button ghost" onClick={close}>Cancel</button><button className="button primary" disabled={save.isPending}>{save.isPending ? 'Transmitting…' : 'Save mission'}</button></footer></form></div>
}
