export interface User { id: string; email: string; display_name: string; created_at: string }
export interface Satellite {
  id: number; norad_id: number; name: string; orbital_class: 'LEO' | 'MEO' | 'GEO';
  latitude: number | null; longitude: number | null; altitude_km: number | null; velocity_kps: number | null;
  period_minutes: number | null; inclination_deg: number | null; data_source: string; data_quality: string; updated_at: string;
}
export interface SatellitePage { items: Satellite[]; total: number; page: number; page_size: number; pages: number }
export interface WatchItem { id: number; satellite: Satellite; notes: string; notify: boolean; created_at: string }
export interface Mission { id: string; name: string; description: string; status: string; priority: string; satellites: Satellite[]; created_at: string; updated_at: string }
export interface Analytics { satellites_by_orbit: Record<string, number>; mission_status: Record<string, number>; watchlist_by_orbit: Record<string, number>; average_altitude_km: number; tracked_satellites: number; generated_at: string }
