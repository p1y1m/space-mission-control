import { FormEvent, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Bell, BellOff, Plus, Save, Trash2 } from 'lucide-react'
import { api } from '../api'
import type { SatellitePage, WatchItem } from '../types'
import { Empty, Loading, PageHeader, Panel } from '../components/UI'

export default function Watchlist() {
  const qc = useQueryClient(); const [addOpen, setAddOpen] = useState(false)
  const watch = useQuery({ queryKey: ['watchlist'], queryFn: () => api<WatchItem[]>('/watchlist') })
  const catalog = useQuery({ queryKey: ['satellites', 'watch-picker'], queryFn: () => api<SatellitePage>('/satellites?page_size=50') })
  const remove = useMutation({ mutationFn: (id: number) => api(`/watchlist/${id}`, { method: 'DELETE' }), onSuccess: () => qc.invalidateQueries({ queryKey: ['watchlist'] }) })
  const add = useMutation({ mutationFn: (satellite_id: number) => api('/watchlist', { method: 'POST', body: JSON.stringify({ satellite_id }) }), onSuccess: () => { qc.invalidateQueries({ queryKey: ['watchlist'] }); setAddOpen(false) } })
  return <><PageHeader eyebrow="Personal intelligence / watchlist" title="Tracked assets" description="Private notes and alert preferences for the spacecraft that matter to you." actions={<button className="button primary" onClick={() => setAddOpen(true)}><Plus/> Add asset</button>}/>
    {addOpen && <div className="modal-backdrop" role="dialog" aria-modal="true"><div className="modal"><header><div><span className="eyebrow">CATALOG</span><h2>Add tracked asset</h2></div><button className="icon-button" onClick={() => setAddOpen(false)}>×</button></header><div className="picker">{catalog.data?.items.filter(s => !watch.data?.some(w => w.satellite.id === s.id)).map(s => <button key={s.id} onClick={() => add.mutate(s.id)}><span className={`orbit-badge ${s.orbital_class.toLowerCase()}`}>{s.orbital_class}</span><strong>{s.name}</strong><small>NORAD {s.norad_id}</small><Plus/></button>)}</div>{add.error && <p className="form-error">{add.error.message}</p>}</div></div>}
    {watch.isLoading ? <Loading/> : !watch.data?.length ? <Empty title="No assets under watch" text="Add a satellite to begin your private operations watchlist."/> : <div className="watch-grid">{watch.data.map(item => <WatchCard key={item.id} item={item} onDelete={() => remove.mutate(item.id)}/>)}</div>}
  </>
}

function WatchCard({ item, onDelete }: { item: WatchItem; onDelete: () => void }) {
  const qc = useQueryClient(); const [notes, setNotes] = useState(item.notes); const [notify, setNotify] = useState(item.notify)
  const update = useMutation({ mutationFn: () => api(`/watchlist/${item.id}`, { method: 'PATCH', body: JSON.stringify({ notes, notify }) }), onSuccess: () => qc.invalidateQueries({ queryKey: ['watchlist'] }) })
  function submit(e: FormEvent) { e.preventDefault(); update.mutate() }
  return <Panel className="watch-card" title={item.satellite.name} kicker={`NORAD ${item.satellite.norad_id}`} action={<span className={`orbit-badge ${item.satellite.orbital_class.toLowerCase()}`}>{item.satellite.orbital_class}</span>}><div className="watch-stats"><div><span>Altitude</span><strong>{item.satellite.altitude_km?.toLocaleString()} km</strong></div><div><span>Velocity</span><strong>{item.satellite.velocity_kps} km/s</strong></div></div><form onSubmit={submit}><label>Private operator notes<textarea value={notes} maxLength={2000} onChange={e => setNotes(e.target.value)} placeholder="Pass windows, context, or observations…"/></label><label className="toggle"><button type="button" aria-pressed={notify} onClick={() => setNotify(!notify)}>{notify ? <Bell/> : <BellOff/>}<i/></button><span><strong>Alert preference</strong><small>{notify ? 'Enabled for this asset' : 'Notifications disabled'}</small></span></label><div className="card-actions"><button type="button" className="danger-link" onClick={onDelete}><Trash2/> Remove</button><button className="button secondary" disabled={update.isPending}><Save/> {update.isPending ? 'Saving…' : 'Save notes'}</button></div></form></Panel>
}
