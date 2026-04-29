import { useState } from 'react'
import { ArrowLeftRight, Clock, KeyRound, Layers, Play, Shuffle } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { api } from '../lib/api'
import { formatBytes, formatMs, truncate } from '../lib/utils'
import { Button } from '../components/ui/Button'
import { Card, CardHeader } from '../components/ui/Card'
import { Alert } from '../components/ui/Alert'
import { Badge } from '../components/ui/Badge'

type Mode = 'classical' | 'pqc'

function ResultCard({ result, mode }: { result: any; mode: Mode }) {
  return (
    <Card glow>
      <CardHeader
        title={mode === 'pqc' ? 'Post-Quantum Handshake' : 'Classical Handshake'}
        subtitle={result.algorithm}
        icon={<ArrowLeftRight className="w-4 h-4" />}
        action={
          <Badge variant={mode === 'pqc' ? 'cyan' : 'amber'}>
            {mode === 'pqc' ? 'PQC' : 'Classical'}
          </Badge>
        }
      />
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-surface-700/50 rounded-lg p-3 text-center">
          <p className="text-xs text-slate-500 mb-1">Latency</p>
          <p className="text-lg font-bold text-cyan-400 font-mono">{formatMs(result.handshake_latency_ms)}</p>
        </div>
        <div className="bg-surface-700/50 rounded-lg p-3 text-center">
          <p className="text-xs text-slate-500 mb-1">Payload Size</p>
          <p className="text-lg font-bold text-violet-400 font-mono">{formatBytes(result.payload_size)}</p>
        </div>
        <div className="bg-surface-700/50 rounded-lg p-3 text-center">
          <p className="text-xs text-slate-500 mb-1">Shared Secret</p>
          <p className="text-lg font-bold text-emerald-400 font-mono">{result.shared_secret_size} bytes</p>
        </div>
        <div className="bg-surface-700/50 rounded-lg p-3 text-center">
          <p className="text-xs text-slate-500 mb-1">Mode</p>
          <p className="text-lg font-bold text-slate-200 capitalize">{result.mode}</p>
        </div>
      </div>
      <div className="space-y-2 text-xs">
        <div>
          <p className="text-slate-500 mb-1">Client Payload (base64)</p>
          <p className="font-mono text-slate-400 bg-surface-700/50 rounded p-2 break-all">{truncate(result.client_payload, 80)}</p>
        </div>
        <div>
          <p className="text-slate-500 mb-1">Shared Secret (base64)</p>
          <p className="font-mono text-slate-400 bg-surface-700/50 rounded p-2 break-all">{truncate(result.shared_secret, 80)}</p>
        </div>
      </div>
    </Card>
  )
}

export default function Handshake() {
  const [classical, setClassical] = useState<any>(null)
  const [pqc, setPqc] = useState<any>(null)

  const { mutate: runHandshake, isPending, variables } = useMutation({
    mutationFn: (mode: Mode) => api.simulateHandshake(mode),
    onSuccess: (data, mode) => {
      if (mode === 'classical') setClassical(data)
      else setPqc(data)
    },
  })

  const [error, setError] = useState<string | null>(null)

  const run = (mode: Mode) => {
    setError(null)
    runHandshake(mode, {
      onError: (e: any) => setError(e.response?.data?.detail ?? e.message),
    })
  }

  const bothDone = classical && pqc
  const latencyImprovement = bothDone
    ? ((classical.handshake_latency_ms - pqc.handshake_latency_ms) / classical.handshake_latency_ms) * 100
    : null

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Controls */}
      <Card>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <div className="flex-1">
            <p className="text-sm font-semibold text-slate-100 mb-1">Handshake Simulation</p>
            <p className="text-xs text-slate-500">
              Simulate a TLS-like key exchange using RSA (classical) or Kyber KEM (PQC) and compare
              latency, payload size, and shared secret properties.
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => run('classical')}
              loading={isPending && variables === 'classical'}
              disabled={isPending}>
              <Shuffle className="w-3.5 h-3.5" />
              Run Classical
            </Button>
            <Button onClick={() => run('pqc')}
              loading={isPending && variables === 'pqc'}
              disabled={isPending}>
              <Play className="w-3.5 h-3.5" />
              Run PQC (Kyber)
            </Button>
          </div>
        </div>
        {error && <Alert variant="error" className="mt-3">{error}</Alert>}
      </Card>

      {/* Comparison summary */}
      {bothDone && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card className="text-center">
            <Clock className="w-5 h-5 text-cyan-400 mx-auto mb-2" />
            <p className="text-xs text-slate-500 mb-1">Latency delta</p>
            <p className={`text-xl font-bold font-mono ${(latencyImprovement ?? 0) > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {latencyImprovement !== null ? `${latencyImprovement > 0 ? '-' : '+'}${Math.abs(latencyImprovement).toFixed(1)}%` : '—'}
            </p>
            <p className="text-[10px] text-slate-600 mt-1">PQC vs classical</p>
          </Card>
          <Card className="text-center">
            <Layers className="w-5 h-5 text-violet-400 mx-auto mb-2" />
            <p className="text-xs text-slate-500 mb-1">Payload ratio</p>
            <p className="text-xl font-bold font-mono text-violet-400">
              {(pqc.payload_size / classical.payload_size).toFixed(2)}×
            </p>
            <p className="text-[10px] text-slate-600 mt-1">PQC / classical</p>
          </Card>
          <Card className="text-center">
            <KeyRound className="w-5 h-5 text-emerald-400 mx-auto mb-2" />
            <p className="text-xs text-slate-500 mb-1">Secret size parity</p>
            <p className="text-xl font-bold font-mono text-emerald-400">
              {classical.shared_secret_size === pqc.shared_secret_size ? 'Equal' : `${pqc.shared_secret_size}B`}
            </p>
            <p className="text-[10px] text-slate-600 mt-1">Shared secret bytes</p>
          </Card>
        </div>
      )}

      {/* Results */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {classical && <ResultCard result={classical} mode="classical" />}
        {pqc && <ResultCard result={pqc} mode="pqc" />}
        {!classical && !pqc && (
          <div className="xl:col-span-2">
            <Card className="text-center py-12">
              <Shuffle className="w-8 h-8 text-slate-600 mx-auto mb-3" />
              <p className="text-sm text-slate-500">Run a handshake to see results here</p>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
