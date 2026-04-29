import { type ReactNode } from 'react'
import { cn } from '../../lib/utils'

type BadgeVariant = 'default' | 'cyan' | 'violet' | 'emerald' | 'amber' | 'red' | 'orange'

const variants: Record<BadgeVariant, string> = {
  default: 'bg-slate-500/10 border-slate-500/30 text-slate-400',
  cyan: 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400',
  violet: 'bg-violet-500/10 border-violet-500/30 text-violet-400',
  emerald: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
  amber: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
  red: 'bg-red-500/10 border-red-500/30 text-red-400',
  orange: 'bg-orange-500/10 border-orange-500/30 text-orange-400',
}

interface BadgeProps {
  children: ReactNode
  variant?: BadgeVariant
  className?: string
}

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  return (
    <span className={cn(
      'inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border',
      variants[variant],
      className,
    )}>
      {children}
    </span>
  )
}

export function AlgoBadge({ algo }: { algo: string }) {
  const lower = algo.toLowerCase()
  if (lower.includes('kyber') || lower === 'pqc' || lower.includes('ml-kem')) {
    return <Badge variant="cyan">{algo}</Badge>
  }
  if (lower.includes('rsa')) return <Badge variant="amber">{algo}</Badge>
  if (lower.includes('ecc') || lower.includes('ecdsa') || lower.includes('ec')) {
    return <Badge variant="violet">{algo}</Badge>
  }
  if (lower === 'unknown') return <Badge variant="default">{algo}</Badge>
  return <Badge variant="default">{algo}</Badge>
}

export function RiskBadge({ level }: { level: string }) {
  const map: Record<string, BadgeVariant> = {
    critical: 'red',
    high: 'orange',
    medium: 'amber',
    low: 'emerald',
  }
  return <Badge variant={map[level.toLowerCase()] ?? 'default'}>{level}</Badge>
}
