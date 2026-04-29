import { type ReactNode } from 'react'
import { cn } from '../../lib/utils'

interface StatCardProps {
  label: string
  value: string | number
  sub?: string
  icon: ReactNode
  trend?: 'up' | 'down' | 'neutral'
  accent?: 'cyan' | 'violet' | 'emerald' | 'amber'
  className?: string
}

const accents = {
  cyan: {
    icon: 'bg-cyan-500/10 border-cyan-500/20 text-cyan-400',
    value: 'text-cyan-400',
    glow: 'shadow-cyan-500/10',
  },
  violet: {
    icon: 'bg-violet-500/10 border-violet-500/20 text-violet-400',
    value: 'text-violet-400',
    glow: 'shadow-violet-500/10',
  },
  emerald: {
    icon: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
    value: 'text-emerald-400',
    glow: 'shadow-emerald-500/10',
  },
  amber: {
    icon: 'bg-amber-500/10 border-amber-500/20 text-amber-400',
    value: 'text-amber-400',
    glow: 'shadow-amber-500/10',
  },
}

export function StatCard({ label, value, sub, icon, accent = 'cyan', className }: StatCardProps) {
  const a = accents[accent]
  return (
    <div className={cn(
      'bg-surface-800 border border-surface-600 rounded-xl p-5 flex items-start gap-4',
      'hover:border-surface-500 transition-all duration-200',
      className,
    )}>
      <div className={cn('w-10 h-10 rounded-lg border flex items-center justify-center flex-shrink-0', a.icon)}>
        {icon}
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-1">{label}</p>
        <p className={cn('text-2xl font-bold tabular-nums leading-none', a.value)}>{value}</p>
        {sub && <p className="text-xs text-slate-500 mt-1.5">{sub}</p>}
      </div>
    </div>
  )
}
