import { type ReactNode } from 'react'
import { AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react'
import { cn } from '../../lib/utils'

type AlertVariant = 'info' | 'success' | 'warning' | 'error'

const config: Record<AlertVariant, { icon: ReactNode; className: string }> = {
  info: {
    icon: <Info className="w-4 h-4" />,
    className: 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300',
  },
  success: {
    icon: <CheckCircle className="w-4 h-4" />,
    className: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300',
  },
  warning: {
    icon: <AlertCircle className="w-4 h-4" />,
    className: 'bg-amber-500/10 border-amber-500/30 text-amber-300',
  },
  error: {
    icon: <XCircle className="w-4 h-4" />,
    className: 'bg-red-500/10 border-red-500/30 text-red-300',
  },
}

interface AlertProps {
  variant?: AlertVariant
  title?: string
  children: ReactNode
  className?: string
}

export function Alert({ variant = 'info', title, children, className }: AlertProps) {
  const { icon, className: variantClass } = config[variant]
  return (
    <div className={cn('flex gap-3 p-4 rounded-lg border text-sm animate-slide-in', variantClass, className)}>
      <span className="flex-shrink-0 mt-0.5">{icon}</span>
      <div>
        {title && <p className="font-semibold mb-0.5">{title}</p>}
        <div className="opacity-90">{children}</div>
      </div>
    </div>
  )
}
