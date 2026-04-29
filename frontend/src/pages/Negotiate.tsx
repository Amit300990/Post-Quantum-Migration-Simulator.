import { useState } from 'react'
import { CheckCircle, Network, Play, XCircle } from 'lucide-react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { NegotiationResponse } from '../types'
import { Button } from '../components/ui/Button'
import { Card, CardHeader } from '../components/ui/Card'
import { Alert } from '../components/ui/Alert'
import { Badge } from '../components/ui/Badge'

const DEFAULT_CLIENT_KEX = 'x25519+ml-kem-768,x25519,rsa-2048'
const DEFAULT_CLIENT_SIG = 'ecdsa-p256-sha256,ml-dsa-65'
const DEFAULT_SERVER_KEX = 'x25519+ml-kem-768,ecdhe-p256,rsa-3072'
const DEFAULT_SERVER_SIG = 'ecdsa-p256-sha256,ml-dsa-65'

function AlgoListInput({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <div>
      <label className="block text-[10px] text-slate-600 uppercase tracking-wider mb-1">{label}</label>
      <input
        className="input-base font-mono text-xs"
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder="algo1,algo2,algo3"
      />
      <p className="text-[10px] text-slate-600 mt-0.5">Comma-separated, preference order</p>
    </div>
  )
}

export default function Negotiate() {
  const { data: profiles } = useQuery({ queryKey: ['profiles'], queryFn: api.getProfiles })
  const [profile, setProfile] = useState('hybrid_transition')
  const [clientKex, setClientKex] = useState(DEFAULT_CLIENT_KEX)
  const [clientSig, setClientSig] = useState(DEFAULT_CLIENT_SIG)
  const [serverKex, setServerKex] = useState(DEFAULT_SERVER_KEX)
  const [serverSig, setServerSig] = useState(DEFAULT_SERVER_SIG)
  const [result, setResult] = useState<NegotiationResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const { mutate: negotiate, isPending } = useMutation({
    mutationFn: () =>
      api.negotiate(
        profile,
        clientKex.split(',').map(s => s.trim()).filter(Boolean),
        clientSig.split(',').map(s => s.trim()).filter(Boolean),
        serverKex.split(',').map(s => s.trim()).filter(Boolean),
        serverSig.split(',').map(s => s.trim()).filter(Boolean),
      ),
    onSuccess: (data) => { setResult(data); setError(null) },
    onError: (e: any) => setError(e.response?.data?.detail ?? e.message),
  })

  const profileNames = (profiles ?? []).map(p => p.name)

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 animate-fade-in">
      {/* Config */}
      <div className="space-y-4">
        <Card>
          <CardHeader title="Negotiation Parameters" icon={<Network className="w-4 h-4" />} />
          <div className="space-y-4">
            <div>
              <label className="block text-[10px] text-slate-600 uppercase tracking-wider mb-1">Profile</label>
              <select className="select-base" value={profile} onChange={e => setProfile(e.target.value)}>
                {profileNames.length === 0
                  ? <option>hybrid_transition</option>
                  : profileNames.map(p => <option key={p} value={p}>{p.replace(/_/g, ' ')}</option>)
                }
              </select>
            </div>

            <div className="p-3 bg-surface-700/40 rounded-lg space-y-3">
              <p className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                <span className="w-5 h-5 rounded bg-amber-500/20 text-amber-400 text-[10px] flex items-center justify-center font-bold">C</span>
                Client Capabilities
              </p>
              <AlgoListInput label="Key Exchange" value={clientKex} onChange={setClientKex} />
              <AlgoListInput label="Signatures" value={clientSig} onChange={setClientSig} />
            </div>

            <div className="p-3 bg-surface-700/40 rounded-lg space-y-3">
              <p className="text-xs font-semibold text-slate-300 flex items-center gap-2">
                <span className="w-5 h-5 rounded bg-cyan-500/20 text-cyan-400 text-[10px] flex items-center justify-center font-bold">S</span>
                Server Capabilities
              </p>
              <AlgoListInput label="Key Exchange" value={serverKex} onChange={setServerKex} />
              <AlgoListInput label="Signatures" value={serverSig} onChange={setServerSig} />
            </div>

            <Button onClick={() => negotiate()} loading={isPending} className="w-full">
              <Play className="w-4 h-4" /> Negotiate
            </Button>

            {error && <Alert variant="error">{error}</Alert>}
          </div>
        </Card>
      </div>

      {/* Result */}
      <div className="space-y-4">
        {result ? (
          <Card glow>
            <CardHeader
              title="Negotiation Result"
              icon={result.status === 'negotiated' ? <CheckCircle className="w-4 h-4 text-emerald-400" /> : <XCircle className="w-4 h-4 text-red-400" />}
              action={
                <Badge variant={result.status === 'negotiated' ? 'emerald' : 'red'}>
                  {result.status.toUpperCase()}
                </Badge>
              }
            />

            {result.status === 'negotiated' ? (
              <div className="space-y-4">
                <Alert variant="success">
                  Algorithms successfully negotiated under profile <strong>{result.profile.replace(/_/g, ' ')}</strong>.
                </Alert>
                <div className="grid grid-cols-1 gap-3">
                  <div className="p-3 bg-surface-700/40 rounded-lg">
                    <p className="text-[10px] text-slate-600 uppercase tracking-wider mb-2">Selected Key Exchange</p>
                    <div className="flex items-center gap-2">
                      <Badge variant="cyan">{result.selected_key_exchange}</Badge>
                      {result.protocol_mode && <Badge variant="violet">{result.protocol_mode}</Badge>}
                    </div>
                  </div>
                  <div className="p-3 bg-surface-700/40 rounded-lg">
                    <p className="text-[10px] text-slate-600 uppercase tracking-wider mb-2">Selected Signature</p>
                    <Badge variant="emerald">{result.selected_signature}</Badge>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <Alert variant="error" title="Negotiation failed">
                  {result.failure_reason}
                </Alert>
                <div className="text-xs text-slate-500">
                  <p className="mb-1">Try widening client or server algorithm lists, or switching to a less restrictive profile.</p>
                </div>
              </div>
            )}

            <div className="mt-4 pt-4 border-t border-surface-700 grid grid-cols-2 gap-3 text-xs">
              <div>
                <p className="text-slate-600 mb-1.5">Client offered KEX</p>
                <div className="flex flex-wrap gap-1">
                  {result.client_supported.key_exchange_algorithms.map(k => (
                    <span key={k} className={`px-1.5 py-0.5 rounded text-[10px] ${k === result.selected_key_exchange ? 'bg-cyan-500/20 text-cyan-400' : 'bg-surface-700 text-slate-500'}`}>{k}</span>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-slate-600 mb-1.5">Server offered KEX</p>
                <div className="flex flex-wrap gap-1">
                  {result.server_supported.key_exchange_algorithms.map(k => (
                    <span key={k} className={`px-1.5 py-0.5 rounded text-[10px] ${k === result.selected_key_exchange ? 'bg-cyan-500/20 text-cyan-400' : 'bg-surface-700 text-slate-500'}`}>{k}</span>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        ) : (
          <Card className="text-center py-16">
            <Network className="w-8 h-8 text-slate-600 mx-auto mb-3" />
            <p className="text-sm text-slate-500">Configure parameters and click Negotiate</p>
          </Card>
        )}
      </div>
    </div>
  )
}
