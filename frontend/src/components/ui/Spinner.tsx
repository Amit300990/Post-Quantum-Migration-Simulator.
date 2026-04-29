import { cn } from '../../lib/utils'

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  label?: string
}

const sizes = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-10 h-10' }

export function Spinner({ size = 'md', className, label }: SpinnerProps) {
  return (
    <div className={cn('flex flex-col items-center gap-3', className)}>
      <svg
        className={cn('animate-spin text-cyan-400', sizes[size])}
        viewBox="0 0 24 24"
        fill="none"
      >
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
        />
      </svg>
      {label && <p className="text-sm text-slate-500">{label}</p>}
    </div>
  )
}

export function PageSpinner({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex items-center justify-center min-h-[300px]">
      <Spinner size="lg" label={label} />
    </div>
  )
}

export function SkeletonLine({ className }: { className?: string }) {
  return <div className={cn('bg-surface-700 rounded animate-pulse', className)} />
}
