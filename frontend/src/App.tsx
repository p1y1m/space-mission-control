import { Navigate, Outlet, Route, Routes } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { Layout } from './components/Layout'
import { Loading } from './components/UI'
import { useAuth } from './components/AuthProvider'
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Satellites = lazy(() => import('./pages/Satellites'))
const SatelliteDetail = lazy(() => import('./pages/SatelliteDetail'))
const Watchlist = lazy(() => import('./pages/Watchlist'))
const Missions = lazy(() => import('./pages/Missions'))
const Analytics = lazy(() => import('./pages/Analytics'))
const Account = lazy(() => import('./pages/Account'))
const Login = lazy(() => import('./pages/Login'))
const NotFound = lazy(() => import('./pages/NotFound'))

function Protected() { const { user, loading } = useAuth(); if (loading) return <Loading label="Establishing secure session"/>; return user ? <Outlet/> : <Navigate to="/login" replace/> }
function AppShell() { return <Layout><Outlet/></Layout> }

export default function App() { return <Suspense fallback={<Loading/>}><Routes>
  <Route path="/login" element={<Login/>}/>
  <Route element={<AppShell/>}>
    <Route index element={<Dashboard/>}/><Route path="satellites" element={<Satellites/>}/><Route path="satellites/:id" element={<SatelliteDetail/>}/>
    <Route element={<Protected/>}><Route path="watchlist" element={<Watchlist/>}/><Route path="missions" element={<Missions/>}/><Route path="analytics" element={<Analytics/>}/><Route path="account" element={<Account/>}/></Route>
  </Route>
  <Route path="*" element={<NotFound/>}/>
  </Routes></Suspense> }
