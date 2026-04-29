import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { Wifi, WifiOff } from 'lucide-react'
import { api } from '../../lib/api'

const titles: Record<string, { label: string; sub: string }> = {
  '/':          { label: 'Dashboard', sub: 'Overview of cryptographic migration status' },
  '/crypto':    { label: 'Encrypt & Decrypt', sub: 'RSA and Kyber hybrid cryptographic operations' },
  '/benchmark': { label: 'Benchmark', sub: 'Key generation, encryption, and throughput analysis' },
  '/handshake': { label: 'Handshake Simulator', sub: 'Classical and post-quantum TLS-like key exchange' },
  '/inventory': { label: 'Crypto Inventory', sub: 'Cloud and on-premises cryptographic asset discovery' },
  '/readiness': { label: 'PQC Readiness', sub: 'Per-asset risk scoring and migration prioritisation' },
  '/profiles':  { label: 'Migration Profiles', sub: 'NIST-aligned post-quantum migration profiles' },
  '/negotiate': { label: 'Algorithm Negotiation', sub: 'TLS-style algorithm negotiation with profile enforcement' },
  '/hsm':       { label: 'HSM Simulator', sub: 'Software HSM key generation and wrapping' },
  '/results':   { label: 'Results & History', sub: 'Stored benchmark and handshake records' },
}

export function Header() {
  const { pathname } = useLocation()
  const [apiOnline, setApiOnline] = useState<boolean | null>(null)
  const page = titles[pathname] ?? { label: 'PQMS', sub: '' }

  useEffect(() => {
    let cancelled = false
    const check = () =>
      api.health()
        .then(() => { if (!cancelled) setApiOnline(true) })
        .catch(() => { if (!cancelled) setApiOnline(false) })
    check()
    const id = setInterval(check, 30_000)
    return () => { cancelled = true; clearInterval(id) }
  }, [])

  return (
    <header className="h-14 flex-shrink-0 bg-surface-800 border-b border-surface-600 px-6 flex items-center justify-between sticky top-0 z-10">
      <div>
        <h1 className="text-sm font-semibold text-slate-100 leading-none">{page.label}</h1>
        <p className="text-[11px] text-slate-500 mt-0.5 leading-none hidden sm:block">{page.sub}</p>
      </div>
      <div className="flex items-center gap-2">
        <span className={`text-[11px] font-medium ${apiOnline === null ? 'text-slate-600' : apiOnline ? 'text-emerald-400' : 'text-red-400'}`}>
          {apiOnline === null ? 'Checking…' : apiOnline ? 'API Online' : 'API Offline'}
        </span>
        {apiOnline === null
          ? <div className="w-2 h-2 rounded-full bg-slate-600 animate-pulse-slow" />
          : apiOnline
          ? <Wifi className="w-3.5 h-3.5 text-emerald-400" />
          : <WifiOff className="w-3.5 h-3.5 text-red-400" />
        }
      </div>
    </header>
  )
}
