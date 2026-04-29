import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import Crypto from './pages/Crypto'
import Benchmark from './pages/Benchmark'
import Handshake from './pages/Handshake'
import Inventory from './pages/Inventory'
import Readiness from './pages/Readiness'
import Profiles from './pages/Profiles'
import Negotiate from './pages/Negotiate'
import HSM from './pages/HSM'
import Results from './pages/Results'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="crypto" element={<Crypto />} />
        <Route path="benchmark" element={<Benchmark />} />
        <Route path="handshake" element={<Handshake />} />
        <Route path="inventory" element={<Inventory />} />
        <Route path="readiness" element={<Readiness />} />
        <Route path="profiles" element={<Profiles />} />
        <Route path="negotiate" element={<Negotiate />} />
        <Route path="hsm" element={<HSM />} />
        <Route path="results" element={<Results />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
