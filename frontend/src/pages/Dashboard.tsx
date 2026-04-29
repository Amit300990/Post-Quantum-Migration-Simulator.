import { useQuery } from '@tanstack/react-query'
import { Activity, BarChart2, Cpu, Layers, Shuffle, TrendingUp, Zap } from 'lucide-react'
import {
  Bar, BarChart, CartesianGrid, Legend, Line, LineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import { api } from '../lib/api'
import { formatBytes, formatMs, formatThroughput } from '../lib/utils'
import { StatCard } from '../components/ui/StatCard'
import { Card, CardHeader } from '../components/ui/Card'
import { PageSpinner } from '../components/ui/Spinner'
import { AlgoBadge } from '../components/ui/Badge'

const CHART_COLORS = { rsa: '#f59e0b', kyber: '#06b6d4' }

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-surface-800 border border-surface-600 rounded-lg p-3 shadow-xl text-xs">
      <p className="text-slate-400 mb-2 font-medium">{formatBytes(Number(label))}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color }} className="font-medium">
          {p.name}: {formatMs(p.value)}
        </p>
      ))}
    </div>
  )
}

const ThroughputTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-surface-800 border border-surface-600 rounded-lg p-3 shadow-xl text-xs">
      <p className="text-slate-400 mb-2 font-medium">{formatBytes(Number(label))}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color }} className="font-medium">
          {p.name}: {formatThroughput(p.value)}
        </p>
      ))}
    </div>
  )
}

export default function Dashboard() {
  const { data, isLoading } = useQuery({ queryKey: ['results'], queryFn: api.getResults, refetchInterval: 30000 })

  const benchmarks = data?.benchmarks ?? []
  const handshakes = data?.handshakes ?? []

  const rsaBest = benchmarks.filter(b => b.algorithm === 'rsa').reduce((a, b) => b.throughput_mb_s > a ? b.throughput_mb_s : a, 0)
  const kyberBest = benchmarks.filter(b => b.algorithm === 'kyber').reduce((a, b) => b.throughput_mb_s > a ? b.throughput_mb_s : a, 0)

  const encryptChartData = (() => {
    const sizes = [...new Set(benchmarks.map(b => b.file_size))].sort((a, b) => a - b)
    return sizes.map(size => {
      const rsa = benchmarks.filter(b => b.algorithm === 'rsa' && b.file_size === size)
      const kyber = benchmarks.filter(b => b.algorithm === 'kyber' && b.file_size === size)
      return {
        size,
        rsa: rsa.length ? rsa.reduce((a, b) => a + b.encrypt_time_ms, 0) / rsa.length : null,
        kyber: kyber.length ? kyber.reduce((a, b) => a + b.encrypt_time_ms, 0) / kyber.length : null,
      }
    })
  })()

  const throughputChartData = (() => {
    const sizes = [...new Set(benchmarks.map(b => b.file_size))].sort((a, b) => a - b)
    return sizes.map(size => {
      const rsa = benchmarks.filter(b => b.algorithm === 'rsa' && b.file_size === size)
      const kyber = benchmarks.filter(b => b.algorithm === 'kyber' && b.file_size === size)
      return {
        size,
        rsa: rsa.length ? rsa.reduce((a, b) => a + b.throughput_mb_s, 0) / rsa.length : null,
        kyber: kyber.length ? kyber.reduce((a, b) => a + b.throughput_mb_s, 0) / kyber.length : null,
      }
    })
  })()

  if (isLoading) return <PageSpinner label="Loading dashboard…" />

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Hero */}
      <div className="relative rounded-xl overflow-hidden border border-surface-600 bg-gradient-to-br from-surface-800 via-surface-800 to-cyan-950/30 p-6">
        <div className="absolute inset-0 bg-grid opacity-40" />
        <div className="relative">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-5 h-5 text-cyan-400" />
            <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">Enterprise Platform</span>
          </div>
          <h2 className="text-2xl font-bold text-slate-100 text-glow-cyan mb-1">
            Post-Quantum Migration Simulator
          </h2>
          <p className="text-sm text-slate-400 max-w-xl">
            Analyse, benchmark, and plan your organisation's migration from classical RSA/ECC to NIST-standardised
            post-quantum Kyber-based encryption.
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Benchmark Runs" value={benchmarks.length} icon={<BarChart2 className="w-5 h-5" />} accent="cyan" sub="Stored results" />
        <StatCard label="Handshakes" value={handshakes.length} icon={<Shuffle className="w-5 h-5" />} accent="violet" sub="Simulated sessions" />
        <StatCard label="Best Kyber" value={kyberBest > 0 ? formatThroughput(kyberBest) : '—'} icon={<Zap className="w-5 h-5" />} accent="emerald" sub="Peak throughput" />
        <StatCard label="Best RSA" value={rsaBest > 0 ? formatThroughput(rsaBest) : '—'} icon={<Cpu className="w-5 h-5" />} accent="amber" sub="Peak throughput" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <Card>
          <CardHeader title="Encrypt Latency Comparison" subtitle="RSA vs Kyber — avg across runs" icon={<BarChart2 className="w-4 h-4" />} />
          {encryptChartData.length === 0 ? (
            <div className="h-48 flex items-center justify-center text-slate-600 text-sm">
              Run <code className="mx-1 text-cyan-500">/benchmark</code> to populate this chart
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={encryptChartData} margin={{ top: 4, right: 8, left: -8, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                <XAxis dataKey="size" tickFormatter={v => formatBytes(v)} tick={{ fill: '#8b949e', fontSize: 10 }} />
                <YAxis tickFormatter={v => `${v.toFixed(0)}ms`} tick={{ fill: '#8b949e', fontSize: 10 }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="rsa" name="RSA" fill={CHART_COLORS.rsa} radius={[3, 3, 0, 0]} />
                <Bar dataKey="kyber" name="Kyber" fill={CHART_COLORS.kyber} radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Card>

        <Card>
          <CardHeader title="Throughput vs File Size" subtitle="MB/s — higher is better" icon={<TrendingUp className="w-4 h-4" />} />
          {throughputChartData.length === 0 ? (
            <div className="h-48 flex items-center justify-center text-slate-600 text-sm">
              Run <code className="mx-1 text-cyan-500">/benchmark</code> to populate this chart
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={throughputChartData} margin={{ top: 4, right: 8, left: -8, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                <XAxis dataKey="size" tickFormatter={v => formatBytes(v)} tick={{ fill: '#8b949e', fontSize: 10 }} />
                <YAxis tickFormatter={v => `${v.toFixed(1)}`} tick={{ fill: '#8b949e', fontSize: 10 }} />
                <Tooltip content={<ThroughputTooltip />} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Line type="monotone" dataKey="rsa" name="RSA" stroke={CHART_COLORS.rsa} strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="kyber" name="Kyber" stroke={CHART_COLORS.kyber} strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <Card>
          <CardHeader title="Recent Benchmarks" icon={<Activity className="w-4 h-4" />} />
          {benchmarks.length === 0 ? (
            <p className="text-sm text-slate-600 text-center py-6">No benchmark results yet</p>
          ) : (
            <div className="space-y-2">
              {benchmarks.slice(0, 5).map((b, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b border-surface-700 last:border-0">
                  <div className="flex items-center gap-2">
                    <AlgoBadge algo={b.algorithm} />
                    <span className="text-xs text-slate-500">{formatBytes(b.file_size)}</span>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-slate-300 font-mono">{formatMs(b.encrypt_time_ms)}</p>
                    <p className="text-[10px] text-slate-600">{formatThroughput(b.throughput_mb_s)}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card>
          <CardHeader title="Recent Handshakes" icon={<Layers className="w-4 h-4" />} />
          {handshakes.length === 0 ? (
            <p className="text-sm text-slate-600 text-center py-6">No handshake results yet</p>
          ) : (
            <div className="space-y-2">
              {handshakes.slice(0, 5).map((h, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b border-surface-700 last:border-0">
                  <div className="flex items-center gap-2">
                    <AlgoBadge algo={h.algorithm} />
                    <span className="text-xs text-slate-500 capitalize">{h.mode}</span>
                  </div>
                  <p className="text-xs text-slate-300 font-mono">{formatMs(h.handshake_latency_ms)}</p>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
