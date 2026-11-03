import L from 'leaflet'
import { MapContainer, Marker, Popup, TileLayer, ZoomControl } from 'react-leaflet'
import type { Satellite } from '../types'

function icon(selected: boolean, orbit: string) {
  return L.divIcon({ className: '', html: `<span class="map-marker ${selected ? 'selected' : ''} ${orbit.toLowerCase()}"><i></i></span>`, iconSize: [24, 24], iconAnchor: [12, 12] })
}

export function SatelliteMap({ satellites, selected, onSelect }: { satellites: Satellite[]; selected?: number; onSelect: (satellite: Satellite) => void }) {
  return <MapContainer center={[15, 0]} zoom={2} minZoom={2} maxZoom={7} zoomControl={false} worldCopyJump className="map">
    <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
    <ZoomControl position="bottomright" />
    {satellites.filter(s => s.latitude != null && s.longitude != null).map(s => <Marker key={s.id} position={[s.latitude!, s.longitude!]} icon={icon(selected === s.id, s.orbital_class)} eventHandlers={{ click: () => onSelect(s) }}>
      <Popup><strong>{s.name}</strong><br/>NORAD {s.norad_id} · {s.orbital_class}<br/>{s.altitude_km?.toLocaleString()} km estimated</Popup>
    </Marker>)}
  </MapContainer>
}
