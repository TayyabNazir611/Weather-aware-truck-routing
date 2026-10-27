import { lazy, Suspense, useRef, useState } from 'react'
import { ArrowRight, ArrowUpRight, Check, CloudSun, Compass, LoaderCircle, MapPinned, Route as RouteIcon, ShieldCheck, Truck, X } from 'lucide-react'
import { analyzeTrip, loadDemo } from './api'
import { TripForm } from './components/TripForm'
import { RouteCard, duration } from './components/RouteCard'
import { ForecastControl } from './components/ForecastControl'
import { levels, type Analysis, type Checkpoint, type Trip } from './types'

const date = (value: string) => new Date(value).toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZoneName: 'short' })
const WeatherMap = lazy(() => import('./components/WeatherMap').then(module => ({ default: module.WeatherMap })))
export default function App() {
  const [data, setData] = useState<Analysis | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [point, setPoint] = useState<Checkpoint | null>(null)
  const [hour, setHour] = useState(0)
  const [overlay, setOverlay] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const controller = useRef<AbortController | null>(null)
  const selected = data?.routes.find(r => r.id === selectedId)
  function apply(result: Analysis) {
    setData(result); setSelectedId(result.recommended_id || result.routes[0]?.id || null); setPoint(null); setHour(0)
  }
  async function submit(trip: Trip) {
    controller.current?.abort()
    const current = new AbortController(); controller.current = current
    setBusy(true); setError(''); setData(null); setPoint(null)
    try { const result = await analyzeTrip(trip, current.signal); if (!current.signal.aborted) apply(result) }
    catch (e) { if (!current.signal.aborted) setError(e instanceof Error ? e.message : 'Unable to analyze this trip.') }
    finally { if (!current.signal.aborted) setBusy(false) }
  }
  async function demo() {
    controller.current?.abort()
    const current = new AbortController(); controller.current = current
    setError(''); setBusy(true)
    try { const result = await loadDemo(current.signal); if (!current.signal.aborted) apply(result) }
    catch (e) { if (!current.signal.aborted) setError(e instanceof Error ? e.message : 'Demo unavailable.') }
    finally { if (!current.signal.aborted) setBusy(false) }
  }
  return <div className="app-shell">
    <header className="app-header">
      <a className="brand" href="/" aria-label="Spotter home">
        <span className="brand-icon">
          <Compass size={25} />
        </span>spotter
        <span className="brand-divider" />
        <small>Route intelligence</small>
      </a>
      <div className="header-context">
        <Truck size={16} />
        <span>Weather-aware truck routing</span>
        <span className="version">ASSESSMENT / 01</span>
      </div>
    </header>
    <main className="workspace">
      <aside className="sidebar">
        <div className="sidebar-content">
          <div className="sidebar-title">
            <h1>A clearer road ahead.</h1>
            <p>Compare the weather along your route,<br />before you get behind the wheel.</p>
          </div>
          <div className="section-heading">
            <span className="step-number">01</span>
            <h2>Trip details</h2>
            <RouteIcon size={17} />
          </div>
          <TripForm busy={busy} onSubmit={submit} onDirty={() => { setData(null); setPoint(null); setSelectedId(null) }} />
          {error && <div className="error-banner" role="alert">{error}</div>}
          {data && <section className="route-options" aria-label="Route alternatives">
            <div className="section-heading">
              <span className="step-number">02</span>
              <h2>Compare routes</h2>
              <span className="count">{data.routes.length}</span>
            </div>
            <p className="field-hint">{data.load_lb.toLocaleString()} lb cargo · Every {data.interval_miles} mi</p>
            {data.routes.map(route =>
              <RouteCard key={route.id}
                route={route}
                selected={route.id === selectedId}
                recommended={route.id === data.recommended_id}
                onSelect={() => { setSelectedId(route.id); setPoint(null) }}
              />
            )}
          </section>
          }
          <div className="sidebar-note">
            <ShieldCheck size={18} />
            <p>Weather guidance for the road ahead.<br />Always verify road and truck restrictions.</p>
          </div>
        </div>
        <div className="sidebar-actions">
          <button className="primary" type="submit" form="trip-form" disabled={busy}>
            {busy ? <><LoaderCircle size={17} className="spin"/> Analyzing forecasts…</> : <>Find routes & compare <ArrowRight size={17}/></>}
          </button>
          {busy ?
            <button type="button" className="text-button" onClick={() => { controller.current?.abort(); setBusy(false); setError('Analysis canceled. Update your trip and try again.') }}>Cancel analysis</button> :
            <button type="button" className="text-button" onClick={demo}>Explore a recorded trip <span>↗</span></button>
          }
        </div>
      </aside>
      <section className="map-workspace">
        <div className="map-frame">
          <Suspense fallback={
            <div className="map" role="status" aria-label="Loading map" />
          }>
            <WeatherMap
              data={data}
              selectedId={selectedId}
              hour={hour}
              overlay={overlay}
              onCheckpoint={setPoint}
            />
          </Suspense>
          <div className="map-top-label">
            <span className="status-dot" />
            {busy ? 'Analyzing your trip' :
              data ? data.mode === 'demo' ?
                'Recorded demonstration' :
                'Live forecast analysis' :
                'Your route, in context'
            }
            <span className="map-label-divider" />
            {data ? `${data.routes.length} truck routes` : 'United States'}
          </div>
          {!data && !busy && <div className="map-welcome">
            <MapPinned size={25} />
            <h2>Every mile has a forecast.</h2>
            <p>Set your trip details to see truck routes,
              <br />arrival-time weather and the road ahead.
            </p>
            <button className="welcome-link" onClick={demo}>
              Explore the recorded trip <ArrowUpRight size={15} />
            </button>
          </div>
          }
          {busy && <div className="map-welcome loading" role="status">
            <CloudSun size={30} />
            <h2>Checking the road ahead.</h2>
            <p>Finding truck routes and matching forecasts
              <br />to your arrival at every checkpoint.
            </p>
            <div className="loading-line" />
          </div>
          }
          {point && <section className="checkpoint-popup" aria-label="Checkpoint details">
            <button
              className="close"
              aria-label="Close checkpoint"
              onClick={() => setPoint(null)}>
              <X size={16} />
            </button>
            <span className="eyebrow">ARRIVAL-TIME FORECAST</span>
            <h3>Mile {point.mile.toFixed(1)}
              <span className={`risk-text-${point.risk ?? 5}`}>{levels[point.risk ?? 5]}
              </span>
            </h3>
            <p>{date(point.eta)}</p>
            {point.weather ?
              <dl>
                <div>
                  <dt>Wind</dt>
                  <dd>{point.weather.wind_mph.toFixed(1)} mph</dd>
                </div>
                <div>
                  <dt>Rain</dt>
                  <dd>{point.weather.rain_in_hr.toFixed(3)} in/hr</dd>
                </div>
                <div>
                  <dt>Snow</dt>
                  <dd>{point.weather.snow_in_hr.toFixed(2)} in/hr</dd>
                </div>
              </dl>
              :
              <p>Forecast unavailable. This route is not eligible for recommendation.</p>
            }
          </section>
          }
          <div className="map-caption">
            <span className="route-key" /> Selected route
            <span>● Checkpoints show arrival-time risk</span>
          </div>
        </div>
        <ForecastControl
          data={data}
          hour={hour}
          setHour={setHour}
          visible={overlay}
          setVisible={setOverlay}
        />
        {data && <div className="analysis-details">
          {data.mode === 'demo' &&
            <p className="demo-notice">Recorded demonstration · Real provider route geometry with saved forecasts from {date(data.departure)}. Not a current travel assessment.</p>
          }
          <div className={`recommendation ${!data.recommended_id ? 'no-recommendation' : ''}`}>
            <ShieldCheck size={23} />
            <div>
              <h2>{data.recommended_id ?
                'The best weather fit for this trip' : 'No eligible route'}
              </h2>
              <p>{data.explanation}</p>
            </div>
          </div>
          {data.warnings.length > 0 &&
            <ul className="warnings">
              {data.warnings.map(w =>
                <li key={w}>{w}</li>)
              }
            </ul>
          }
          {selected && <section className="route-detail">
            <div className="detail-heading">
              <div>
                <span className="eyebrow">SELECTED ROUTE</span>
                <h2>{selected.name}
                  <span>{selected.summary.eligible ?
                    <Check size={17} /> : 'Not eligible'
                  }
                  </span>
                </h2>
              </div>
              <div>
                <strong>{duration(selected.duration_seconds)}</strong>
                <p>Arrival {date(selected.arrival)}</p>
              </div>
            </div>
            <div className="exposure-grid">
              {levels.map((level, i) =>
                <div key={level}>
                  <span>
                    <i className={`risk-bg-${i}`} />
                    {level}
                  </span>
                  <b>{selected.summary.exposure[level].toFixed(1)}
                    <small> mi</small>
                  </b>
                  <small>{selected.summary.counts[level]} checkpoints</small>
                </div>
              )}
            </div>
            <details>
              <summary>Inspect {selected.checkpoints.length} weather checkpoints</summary>
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Mile</th>
                      <th>Arrival</th>
                      <th>Wind</th>
                      <th>Rain</th>
                      <th>Snow</th>
                      <th>Risk</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selected.checkpoints.map(p =>
                      <tr key={p.id}>
                        <td>
                          <button className="table-link"
                            onClick={() => setPoint(p)}>
                            {p.mile.toFixed(1)}
                          </button>
                        </td>
                        <td>
                          {date(p.eta)}
                        </td>
                        <td>{p.weather ? `${p.weather.wind_mph.toFixed(1)} mph` : '—'}</td>
                        <td>{p.weather ? `${p.weather.rain_in_hr.toFixed(3)} in/hr` : '—'}</td>
                        <td>{p.weather ? `${p.weather.snow_in_hr.toFixed(2)} in/hr` : '—'}</td>
                        <td className={`risk-text-${p.risk ?? 5}`}>{levels[p.risk ?? 5]}</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </details>
            <p className="provider-note">{selected.provider} · {data.limitations}</p>
          </section>}
          <p className="attribution">{data.attribution}</p>
        </div>}
        <footer className="app-footer"><span>SPOTTER / ROUTE INTELLIGENCE</span><span>Forecasts inform. Drivers decide.</span></footer>
      </section>
    </main>
  </div>
}
