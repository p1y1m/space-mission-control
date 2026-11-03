import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'
import App from '../App'
import { AuthProvider } from '../components/AuthProvider'

const satellites = { items: [{ id:1,norad_id:25544,name:'ISS (ZARYA)',orbital_class:'LEO',latitude:1,longitude:1,altitude_km:419,velocity_kps:7.66,period_minutes:92,inclination_deg:51.6,data_source:'Demo',data_quality:'demo_propagated_estimate',updated_at:new Date().toISOString()}], total:1,page:1,page_size:12,pages:1 }
function mount(path='/satellites') { const qc=new QueryClient({defaultOptions:{queries:{retry:false}}}); return render(<QueryClientProvider client={qc}><MemoryRouter initialEntries={[path]}><AuthProvider><App/></AuthProvider></MemoryRouter></QueryClientProvider>) }

test('renders searchable satellite catalog', async () => {
  vi.stubGlobal('fetch', vi.fn((url:string) => Promise.resolve(url.includes('/auth/me') ? new Response(JSON.stringify({detail:'no'}),{status:401,headers:{'Content-Type':'application/json'}}) : new Response(JSON.stringify(satellites),{status:200,headers:{'Content-Type':'application/json'}}))))
  mount(); expect(await screen.findByText('Satellite explorer')).toBeInTheDocument(); expect(await screen.findByText('ISS (ZARYA)')).toBeInTheDocument(); expect(screen.getByLabelText('Search satellites')).toBeInTheDocument()
})

test('shows login interface', async () => {
  vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(new Response(JSON.stringify({detail:'no'}),{status:401,headers:{'Content-Type':'application/json'}}))))
  mount('/login'); expect(await screen.findByText('Welcome back, operator')).toBeInTheDocument(); expect(screen.getByRole('button',{name:/enter mission control/i})).toBeInTheDocument()
})
