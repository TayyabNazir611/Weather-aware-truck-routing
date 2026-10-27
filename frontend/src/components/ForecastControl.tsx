import { CloudSun } from 'lucide-react'
import { levels, type Analysis } from '../types'

export function ForecastControl({ data, hour, setHour, visible, setVisible }: { data: Analysis | null; hour: number; setHour: (n: number) => void; visible: boolean; setVisible: (v: boolean) => void }) {
  return <section className="forecast-panel" aria-label="Corridor weather forecast">
    <div className="forecast-heading"><div><CloudSun size={20}/><strong>Corridor forecast</strong></div><label className="toggle"><input type="checkbox" checked={visible} onChange={e => setVisible(e.target.checked)}/> Show overlay</label></div>
    <div className="forecast-time"><span>{data ? new Date(data.heatmap.times[hour]).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZoneName: 'short' }) : 'Analyze a trip to load weather'}</span><b>+{hour}h</b></div>
    <input aria-label="Forecast hour" type="range" min="0" max="48" step="1" value={hour} disabled={!data} onChange={e => setHour(Number(e.target.value))}/>
    <div className="range-labels"><span>0h</span><span>12h</span><span>24h</span><span>36h</span><span>48h</span></div>
    <div className="legend">{levels.map((level, i) => <span key={level}><i className={`risk-bg-${i}`}/>{level}</span>)}</div>
    <p>{data ? `Sampled corridor · ~${data.heatmap.spacing_miles} mi along-route spacing. Smoothed forecast, not precise observations.` : 'Arrival-time route risk and corridor forecast are separate.'} Scrubbing does not change the recommendation.</p>
  </section>
}
