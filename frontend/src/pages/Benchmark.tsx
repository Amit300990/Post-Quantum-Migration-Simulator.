import { useState } from 'react'
import { BarChart2, Play, Zap } from 'lucide-react'
import {
  Bar, BarChart, CartesianGrid, Legend, Line, LineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import { formatBytes, formatMs, formatThroughput } from '../lib/utils'
import type { BenchmarkResult } from '../types'
import { Button } from '../components/ui/Button'
import { Card, CardHeader } from '../components/ui/Card'
import { Alert } from '../components/ui/Alert'
import { AlgoBadge } from '../components/ui/Badge'
import { PageSpinner } from '../components/ui/Spinner'

const COLORS = { rsa: '#f59e0b', kyber: '#06b6d4' }

function buildChartData(results: BenchmarkResult[], key: keyof BenchmarkResult) {
  const sizes = [...new Set(results.map(r => r.file_size))].sort((a, b) => a - b)
  return sizes.map(size => {
    const rsa = results.filter(r => r.algorithm === 'rsa' && r.file_size === size)
    const kyber = results.filter(r => r.algorithm === 'kyber' && r.file_size === size)
    return {
      size,
      rsa: rsa.length ? rsa.reduce((a, r) => a + (r[key] as number), 0) / rsa.length : null,
      kyber: kyber.length ? kyber.reduce((a, r) => a + (r[key] as number), 0) / kyber.length : null,
    }
  })
}

const TT = ({ active, payload, label, fmt }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-surface-800 border border-surface-600 rounded-lg p-3 text-xs shadow-xl">
      <p className="text-slate-400 mb-1.5 font-medium">{formatBytes(Number(label))}</p>
      {payload.map((p: any) => <p key={p.name} style={{ color: p.color }}>{p.name}: {fmt(p.value)}</p>)}
    </div>
  )
}

export default function Benchmark() {
  const qc = useQueryClient()
  const [algo, setAlgo] = useState<'rsa' | 'kyber'>('kyber')
  const [error, setError] = useState<string | null>(null)

  const { data, isLoading } = useQuery({ queryKey: ['results'], queryFn: api.getResults })
  const results = data?.benchmarks ?? []

  const { mutate: runBenchmark, isPending } = useMutation({
    mutationFn: (a: string) => api.runBenchmark(a),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['results'] }); setError(null) },
    onError: (e: any) => setError(e.response?.data?.detail ?? e.message ?? 'Benchmark failed'),
  })

  const encryptData = buildChartData(results, 'encrypt_time_ms')
  const throughputData = buildChartData(results, 'throughput_mb_s')

  if (isLoading) return <PageSpinner label="Loading results…" />

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Controls */}
      <Card>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <div className="flex-1">
            <p className="text-sm font-semibold text-slate-100 mb-1">Run Benchmark</p>
            <p className="text-xs text-slate-500">
              Measures keygen, encryption, decryption latency and throughput across{' '}
              configured file sizes (1 KB · 1 MB · 10 MB).
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex gap-1.5">
              {(['rsa', 'kyber'] as const).map(a => (
                <button key={a} onClick={() => setAlgo(a)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                    algo === a
                      ? a === 'rsa' ? 'bg-amber-500/20 border-amber-500/40 text-amber-300' : 'bg-cyan-500/20 border-cyan-500/40 text-cyan-300'
                      : 'bg-surface-700 border-surface-600 text-slate-400'
                  }`}
                >
                  {a.toUpperCase()}
                </button>
              ))}
            </div>
            <Button onClick={() => runBenchmark(algo)} loading={isPending}>
              <Play className="w-3.5 h-3.5" />
              Run {algo.toUpperCase()} Benchmark
            </Button>
          </div>
        </div>
        {error && <Alert variant="error" className="mt-3">{error}</Alert>}
        {isPending && (
          <Alert variant="info" className="mt-3">
            Benchmark running — this may take 30–60 seconds for large files…
          </Alert>
        )}
      </Card>

      {/* Charts */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <Card>
          <CardHeader title="Encrypt Latency" subtitle="Average ms per algorithm / file size" icon={<Zap className="w-4 h-4" />} />
          {encryptData.length === 0 ? (
            <div className="h-48 flex items-center justify-center text-slate-600 text-sm">No data yet</div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={encryptData} margin={{ top: 4, right: 8, left: -8, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                <XAxis dataKey="size" tickFormatter={v => formatBytes(v)} tick={{ fill: '#8b949e', fontSize: 10 }} />
                <YAxis tickFormatter={v => `${v.toFixed(0)}ms`} tick={{ fill: '#8b949e', fontSize: 10 }} />
                <Tooltip content={<TT fmt={formatMs} />} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="rsa" name="RSA" fill={COLORS.rsa} radius={[3, 3, 0, 0]} />
                <Bar dataKey="kyber" name="Kyber" fill={COLORS.kyber} radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Card>

        <Card>
          <CardHeader title="Throughput" subtitle="MB/s — higher is better" icon={<BarChart2 className="w-4 h-4" />} />
          {throughputData.length === 0 ? (
            <div className="h-48 flex items-center justify-center text-slate-600 text-sm">No data yet</div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={throughputData} margin={{ top: 4, right: 8, left: -8, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                <XAxis dataKey="size" tickFormatter={v => formatBytes(v)} tick={{ fill: '#8b949e', fontSize: 10 }} />
                <YAxis tick={{ fill: '#8b949e', fontSize: 10 }} />
                <Tooltip content={<TT fmt={formatThroughput} />} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Line type="monotone" dataKey="rsa" name="RSA" stroke={COLORS.rsa} strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="kyber" name="Kyber" stroke={COLORS.kyber} strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </Card>
      </div>

      {/* Results Table */}
      {results.length > 0 && (
        <Card>
          <CardHeader title={`All Results (${results.length})`} icon={<BarChart2 className="w-4 h-4" />} />
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-left text-slate-500 border-b border-surface-700">
                  {['Algorithm', 'File Size', 'Keygen', 'Encrypt', 'Decrypt', 'Ciphertext', 'Throughput'].map(h => (
                    <th key={h} className="pb-2 pr-4 font-medium uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {results.map((r, i) => (
                  <tr key={i} className="border-b border-surface-700/50 hover:bg-surface-700/30 transition-colors">
                    <td className="py-2 pr-4"><AlgoBadge algo={r.algorithm} /></td>
                    <td className="py-2 pr-4 font-mono text-slate-300">{formatBytes(r.file_size)}</td>
                    <td className="py-2 pr-4 font-mono text-slate-300">{formatMs(r.keygen_time_ms)}</td>
                    <td className="py-2 pr-4 font-mono text-slate-300">{formatMs(r.encrypt_time_ms)}</td>
                    <td className="py-2 pr-4 font-mono text-slate-300">{formatMs(r.decrypt_time_ms)}</td>
                    <td className="py-2 pr-4 font-mono text-slate-300">{formatBytes(r.ciphertext_size)}</td>
                    <td className="py-2 font-mono text-cyan-400">{formatThroughput(r.throughput_mb_s)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}
