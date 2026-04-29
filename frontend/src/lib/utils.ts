import { clsx, type ClassValue } from 'clsx'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

export function formatMs(ms: number): string {
  if (ms < 1) return `${(ms * 1000).toFixed(1)} µs`
  if (ms >= 1000) return `${(ms / 1000).toFixed(2)} s`
  return `${ms.toFixed(2)} ms`
}

export function formatThroughput(mbps: number): string {
  return `${mbps.toFixed(2)} MB/s`
}

export function truncate(str: string, maxLen = 64): string {
  if (str.length <= maxLen) return str
  return `${str.slice(0, maxLen)}…`
}

export function downloadText(content: string, filename: string, mimeType = 'text/plain') {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export function copyToClipboard(text: string): Promise<void> {
  return navigator.clipboard.writeText(text)
}

export function riskColor(level: string): string {
  switch (level.toLowerCase()) {
    case 'critical': return 'text-red-400'
    case 'high': return 'text-orange-400'
    case 'medium': return 'text-amber-400'
    case 'low': return 'text-emerald-400'
    default: return 'text-slate-400'
  }
}

export function riskBg(level: string): string {
  switch (level.toLowerCase()) {
    case 'critical': return 'bg-red-500/10 border-red-500/30 text-red-400'
    case 'high': return 'bg-orange-500/10 border-orange-500/30 text-orange-400'
    case 'medium': return 'bg-amber-500/10 border-amber-500/30 text-amber-400'
    case 'low': return 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
    default: return 'bg-slate-500/10 border-slate-500/30 text-slate-400'
  }
}

export function algoColor(algo: string): string {
  if (algo.toLowerCase().includes('kyber') || algo.toLowerCase() === 'pqc') return 'text-cyan-400'
  if (algo.toLowerCase().includes('rsa')) return 'text-amber-400'
  if (algo.toLowerCase().includes('ecc') || algo.toLowerCase().includes('ec')) return 'text-violet-400'
  return 'text-slate-400'
}
