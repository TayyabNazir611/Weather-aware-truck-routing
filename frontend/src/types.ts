import type { LineString } from 'geojson'
export type Location = { label: string; coordinates: [number, number] }
export type Risk = 0 | 1 | 2 | 3 | 4
export const levels = ['Low', 'Moderate', 'High', 'Severe', 'No Travel', 'Unknown'] as const
export const colors = ['#23865c', '#c49a13', '#e47e23', '#d94444', '#761a33', '#7b8797']
export type Weather = { wind_mph: number; rain_in_hr: number; snow_in_hr: number; risk: Risk; interval_end: number }
export type Checkpoint = { id: string; coordinates: [number, number]; mile: number; eta: string; risk: Risk | null; weather: Weather | null; exposure_miles: number }
export type Route = {
  id: string; name: string; provider: string; rank: number;
  geometry: LineString; distance_miles: number; duration_seconds: number; arrival: string;
  checkpoints: Checkpoint[];
  summary: { exposure: Record<string, number>; counts: Record<string, number>; average_risk: number | null; max_risk: Risk | null; eligible: boolean }
}
export type Analysis = {
  routes: Route[]; recommended_id: string | null; explanation: string; warnings: string[];
  mode: 'live' | 'demo'; departure: string; load_lb: number; interval_miles: number;
  heatmap: { times: string[]; points: { coordinates: [number, number]; risk: (Risk | null)[] }[]; spacing_miles: number };
  attribution: string; limitations: string;
}
export type Trip = { origin: Location; destination: Location; departure: string; load_lb: number; interval_miles: number }
