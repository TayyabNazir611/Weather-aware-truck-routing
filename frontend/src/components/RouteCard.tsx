import { Check, ChevronRight, Ban } from 'lucide-react'
import { levels, type Route } from '../types'

export const duration = (seconds: number) => `${Math.floor(seconds / 3600)}h ${Math.round(seconds % 3600 / 60)}m`
export function RouteCard({ route, selected, recommended, onSelect }: { route: Route; selected: boolean; recommended: boolean; onSelect: () => void }) {
  const summary = route.summary
  return <button className={`route-card ${selected ? 'selected' : ''}`} aria-pressed={selected} onClick={onSelect}>
    <div className="route-card-top"><strong>{route.name}</strong>{recommended ? <span className="recommended"><Check size={13}/> Recommended</span> : !summary.eligible ? <span className="blocked"><Ban size={13}/> Not eligible</span> : <span className="muted">Option {route.rank}</span>}</div>
    <div className="route-stats"><b>{duration(route.duration_seconds)}</b><span>{route.distance_miles.toFixed(1)} mi</span><ChevronRight size={16}/></div>
    <div className="risk-bar" aria-label="Weather exposure">{levels.map((label, i) => <span key={label} className={`risk-bg-${i}`} style={{ width: `${summary.exposure[label] / route.distance_miles * 100}%` }}/>)}</div>
    <div className="route-caption"><span>{summary.exposure.Severe.toFixed(1)} mi Severe</span><span>{summary.exposure.High.toFixed(1)} mi High</span><span>{summary.average_risk?.toFixed(2) ?? '—'} / 4</span></div>
  </button>
}
