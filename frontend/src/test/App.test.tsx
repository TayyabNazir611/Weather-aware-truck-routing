import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import App from '../App'
import { ForecastControl } from '../components/ForecastControl'
import demo from '../../public/demo.json'
import type { Analysis } from '../types'

vi.mock('../components/WeatherMap', () => ({ WeatherMap: () => <div aria-label="Test map"/> }))
vi.mock('../api', () => ({ loadDemo: vi.fn(async () => demo), analyzeTrip: vi.fn(), searchLocations: vi.fn(async () => ({ results: [] })) }))

describe('trip workflow', () => {
  it('requires selected locations', () => {
    render(<App/>); fireEvent.submit(document.getElementById('trip-form')!)
    expect(screen.getByRole('alert')).toHaveTextContent('Select an origin and destination')
  })
  it('loads an explicitly labeled demo and switches routes', async () => {
    render(<App/>); fireEvent.click(screen.getByRole('button', { name: /Explore a recorded trip/ }))
    await waitFor(() => expect(screen.getByText(/Not a current travel assessment/)).toBeInTheDocument())
    expect(screen.getByText(/The best weather fit/)).toBeInTheDocument()
    const cards = screen.getAllByRole('button').filter(b => b.classList.contains('route-card'))
    expect(cards).toHaveLength(3)
    fireEvent.click(cards[1]); expect(cards[1]).toHaveAttribute('aria-pressed', 'true')
    fireEvent.change(screen.getByRole('slider'), { target: { value: '48' } })
    expect(screen.getByText('+48h')).toBeInTheDocument()
  })
  it('slider updates client state without a network action', () => {
    const setHour = vi.fn()
    render(<ForecastControl data={demo as unknown as Analysis} hour={0} setHour={setHour} visible setVisible={vi.fn()}/>)
    fireEvent.change(screen.getByRole('slider'), { target: { value: '24' } })
    expect(setHour).toHaveBeenCalledWith(24)
  })
})
