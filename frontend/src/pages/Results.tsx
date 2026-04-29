import { useState } from 'react'
import { Activity, Download, RefreshCw } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import { downloadText, formatBytes, formatMs, formatThroughput } from '../lib/utils'
import { AlgoBadge } from '../components/ui/Badge'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { PageSpinner } from '../components/ui/Spinner'

type Tab = 'benchmarks' | 'handshakes'

export default function Results() {
  const [tab, setTab] = useState<Tab>('benchmarks')
  const [exporting, setExporting] = useState(false)

  const { data, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['results'],
    queryFn: api.getResults,
    refetchInterval: 60_000,
  })

  const handleExport = async (fmt: 'json' | 'csv') => {
    setExporting(true)
    try {
      const content = await api.exportResults(fmt)
      downloadText(
        typeof content === 'string' ? content : JSON.stringify(content, null, 2),
        `pqms-results.${fmt}`,
        fmt === 'csv' ? 'text/csv' : 'application/json',
      )
    } finally {
      setExporting(false)
    }
  }

  if (isLoading) return <PageSpinner label="Loading results…" />

  const benchmarks = data?.benchmarks ?? []
  const handshakes = data?.handshakes ?? []

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Controls */}
      <Card>
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <p className="text-sm font-semibold text-slate-100 mb-1">Historical Results</p>
            <p className="text-xs text-slate-500">
              {benchmarks.length} benchmark records · {handshakes.length} handshake records
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" onClick={() => refetch()} loading={isRefetching}>
              <RefreshCw className="w-3.5 h-3.5" />
            </Button>
            <Button variant="secondary" size="sm" onClick={() => handleExport('csv')} loading={exporting}>
              <Download className="w-3.5 h-3.5" /> CSV
            </Button>
            <Button variant="secondary" size="sm" onClick={() => handleExport('json')} loading={exporting}>
              <Download className="w-3.5 h-3.5" /> JSON
            </Button>
          </div>
        </div>
      </Card>

      {/* Tabs */}
      <Card>
        <div className="flex gap-0 border-b border-surface-700 mb-5 -mx-5 px-5">
          {(['benchmarks', 'handshakes'] as Tab[]).map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-5 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors capitalize ${
                tab === t ? 'border-cyan-500 text-cyan-400' : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              {t} ({t === 'benchmarks' ? benchmarks.length : handshakes.length})
            </button>
          ))}
        </div>

        {tab === 'benchmarks' && (
          benchmarks.length === 0 ? (
            <div className="py-12 text-center">
              <Activity className="w-8 h-8 text-slate-600 mx-auto mb-3" />
              <p className="text-sm text-slate-500">No benchmark results yet. Run a benchmark to populate.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-left text-slate-500 border-b border-surface-700">
                    {['#', 'Algorithm', 'File Size', 'Keygen', 'Encrypt', 'Decrypt', 'Ciphertext', 'Throughput', 'Recorded'].map(h => (
                      <th key={h} className="pb-2 pr-4 font-medium uppercase tracking-wider">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {benchmarks.map((r, i) => (
                    <tr key={i} className="border-b border-surface-700/40 hover:bg-surface-700/20 transition-colors">
                      <td className="py-2 pr-4 text-slate-600">{i + 1}</td>
                      <td className="py-2 pr-4"><AlgoBadge algo={r.algorithm} /></td>
                      <td className="py-2 pr-4 font-mono text-slate-300">{formatBytes(r.file_size)}</td>
                      <td className="py-2 pr-4 font-mono text-slate-300">{formatMs(r.keygen_time_ms)}</td>
                      <td className="py-2 pr-4 font-mono text-slate-300">{formatMs(r.encrypt_time_ms)}</td>
                      <td className="py-2 pr-4 font-mono text-slate-300">{formatMs(r.decrypt_time_ms)}</td>
                      <td className="py-2 pr-4 font-mono text-slate-300">{formatBytes(r.ciphertext_size)}</td>
                      <td className="py-2 pr-4 font-mono text-cyan-400">{formatThroughput(r.throughput_mb_s)}</td>
                      <td className="py-2 text-slate-600">{r.created_at ? new Date(r.created_at).toLocaleString() : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        )}

        {tab === 'handshakes' && (
          handshakes.length === 0 ? (
            <div className="py-12 text-center">
              <Activity className="w-8 h-8 text-slate-600 mx-auto mb-3" />
              <p className="text-sm text-slate-500">No handshake results yet. Simulate a handshake to populate.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-left text-slate-500 border-b border-surface-700">
                    {['#', 'Algorithm', 'Mode', 'Latency', 'Payload', 'Secret Size', 'Recorded'].map(h => (
                      <th key={h} className="pb-2 pr-4 font-medium uppercase tracking-wider">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {handshakes.map((h, i) => (
                    <tr key={i} className="border-b border-surface-700/40 hover:bg-surface-700/20 transition-colors">
                      <td className="py-2 pr-4 text-slate-600">{i + 1}</td>
                      <td className="py-2 pr-4"><AlgoBadge algo={h.algorithm} /></td>
                      <td className="py-2 pr-4 capitalize text-slate-400">{h.mode}</td>
                      <td className="py-2 pr-4 font-mono text-cyan-400">{formatMs(h.handshake_latency_ms)}</td>
                      <td className="py-2 pr-4 font-mono text-slate-300">{formatBytes(h.payload_size)}</td>
                      <td className="py-2 pr-4 font-mono text-slate-300">{h.shared_secret_size} bytes</td>
                      <td className="py-2 text-slate-600">{h.created_at ? new Date(h.created_at).toLocaleString() : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        )}
      </Card>
    </div>
  )
}
