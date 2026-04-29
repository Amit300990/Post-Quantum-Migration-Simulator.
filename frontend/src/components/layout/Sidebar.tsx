import { NavLink } from 'react-router-dom'
import {
  Activity, BarChart2, GitMerge, HardDrive, Key, LayoutDashboard,
  Lock, Network, Shield, ShieldCheck, Shuffle, Zap,
} from 'lucide-react'
import { cn } from '../../lib/utils'

const nav = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard },
  { label: 'Encrypt / Decrypt', to: '/crypto', icon: Lock },
  { label: 'Benchmark', to: '/benchmark', icon: BarChart2 },
  { label: 'Handshake', to: '/handshake', icon: Shuffle },
  { label: 'Inventory', to: '/inventory', icon: Key },
  { label: 'Readiness', to: '/readiness', icon: ShieldCheck },
  { label: 'Profiles', to: '/profiles', icon: Shield },
  { label: 'Negotiate', to: '/negotiate', icon: Network },
  { label: 'HSM Simulator', to: '/hsm', icon: HardDrive },
  { label: 'Results', to: '/results', icon: Activity },
]

export function Sidebar() {
  return (
    <aside className="w-60 flex-shrink-0 bg-surface-800 border-r border-surface-600 flex flex-col h-screen sticky top-0">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-surface-600">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center">
            <Zap className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <p className="text-sm font-bold text-slate-100 leading-none">PQMS</p>
            <p className="text-[10px] text-slate-500 mt-0.5 leading-none">Post-Quantum Simulator</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto space-y-0.5">
        <p className="px-2 mb-2 text-[10px] font-semibold text-slate-600 uppercase tracking-widest">
          Workspace
        </p>
        {nav.map(({ label, to, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 group',
                isActive
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-surface-700 border border-transparent',
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon className={cn('w-4 h-4 flex-shrink-0 transition-colors', isActive ? 'text-cyan-400' : 'text-slate-500 group-hover:text-slate-300')} />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-surface-600">
        <div className="flex items-center gap-2">
          <GitMerge className="w-3 h-3 text-slate-600" />
          <span className="text-[10px] text-slate-600">v1.0.0 · NIST PQC Ready</span>
        </div>
      </div>
    </aside>
  )
}
