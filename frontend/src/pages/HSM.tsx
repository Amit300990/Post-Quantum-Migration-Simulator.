import { useState } from 'react'
import { HardDrive, Key, Lock, Plus } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { HsmKeyResponse, HsmOperationResponse } from '../types'
import { Button } from '../components/ui/Button'
import { Card, CardHeader } from '../components/ui/Card'
import { Alert } from '../components/ui/Alert'
import { Badge } from '../components/ui/Badge'
import { CodeBlock } from '../components/ui/CodeBlock'

const PROVIDERS = ['software', 'pkcs11', 'aws-cloudhsm', 'azure-managed-hsm', 'gcp-cloud-hsm']
const ALGORITHMS = ['aes-256', 'rsa-2048', 'rsa-4096', 'ec-p256', 'ml-kem-768', 'ml-dsa-65']

export default function HSM() {
  const [keyLabel, setKeyLabel] = useState('migration-key')
  const [keyAlgo, setKeyAlgo] = useState('ml-kem-768')
  const [keySize, setKeySize] = useState(256)
  const [exportable, setExportable] = useState(false)
  const [provider, setProvider] = useState('software')
  const [genResult, setGenResult] = useState<HsmKeyResponse | null>(null)
  const [genError, setGenError] = useState<string | null>(null)

  const [wrapLabel, setWrapLabel] = useState('wrap-key')
  const [wrapAlgo, setWrapAlgo] = useState('aes-256')
  const [wrapSize, setWrapSize] = useState(256)
  const [wrapProvider, setWrapProvider] = useState('software')
  const [plaintextHex, setPlaintextHex] = useState('0102030405060708090a0b0c0d0e0f10')
  const [wrapResult, setWrapResult] = useState<HsmOperationResponse | null>(null)
  const [wrapError, setWrapError] = useState<string | null>(null)

  const { mutate: generateKey, isPending: genPending } = useMutation({
    mutationFn: () => api.generateHsmKey(keyLabel, keyAlgo, keySize, exportable, provider),
    onSuccess: (d) => { setGenResult(d); setGenError(null) },
    onError: (e: any) => setGenError(e.response?.data?.detail ?? e.message),
  })

  const { mutate: wrapKey, isPending: wrapPending } = useMutation({
    mutationFn: () => api.wrapHsmKey(wrapLabel, wrapAlgo, wrapSize, wrapProvider, plaintextHex),
    onSuccess: (d) => { setWrapResult(d); setWrapError(null) },
    onError: (e: any) => setWrapError(e.response?.data?.detail ?? e.message),
  })

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 animate-fade-in">
      {/* Generate Key */}
      <div className="space-y-4">
        <Card>
          <CardHeader title="Generate HSM Key" subtitle="Create a key inside the software HSM simulator" icon={<Plus className="w-4 h-4" />} />
          <div className="space-y-3">
            <div>
              <label className="block text-[10px] text-slate-600 uppercase tracking-wider mb-1">Label</label>
              <input className="input-base" value={keyLabel} onChange={e => setKeyLabel(e.target.value)} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[10px] text-slate-600 uppercase tracking-wider mb-1">Algorithm</label>
                <select className="select-base" value={keyAlgo} onChange={e => setKeyAlgo(e.target.value)}>
                  {ALGORITHMS.map(a => <option key={a} value={a}>{a}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-[10px] text-slate-600 uppercase tracking-wider mb-1">Key Size (bits)</label>
                <input className="input-base font-mono" type="number" value={keySize} onChange={e => setKeySize(Number(e.target.value))} />
              </div>
            </div>
            <div>
              <label className="block text-[10px] text-slate-600 uppercase tracking-wider mb-1">Provider</label>
              <select className="select-base" value={provider} onChange={e => setProvider(e.target.value)}>
                {PROVIDERS.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 accent-cyan-500" checked={exportable} onChange={e => setExportable(e.target.checked)} />
              <span className="text-sm text-slate-400">Exportable</span>
            </label>
            <Button onClick={() => generateKey()} loading={genPending} className="w-full">
              <Key className="w-4 h-4" /> Generate Key
            </Button>
            {genError && <Alert variant="error">{genError}</Alert>}
          </div>
        </Card>

        {genResult && (
          <Card>
            <CardHeader title="Key Generated" icon={<Key className="w-4 h-4" />} />
            <div className="space-y-2">
              <div className="flex gap-2 flex-wrap mb-3">
                <Badge variant="cyan">{genResult.algorithm}</Badge>
                <Badge variant="violet">{genResult.hsm_provider}</Badge>
                {genResult.exportable && <Badge variant="amber">Exportable</Badge>}
              </div>
              <CodeBlock
                code={JSON.stringify(genResult, null, 2)}
                filename={`${genResult.label}.json`}
                downloadable
              />
            </div>
          </Card>
        )}
      </div>

      {/* Wrap Key */}
      <div className="space-y-4">
        <Card>
          <CardHeader title="Wrap Key" subtitle="Wrap plaintext key material inside the HSM" icon={<Lock className="w-4 h-4" />} />
          <div className="space-y-3">
            <div>
              <label className="block text-[10px] text-slate-600 uppercase tracking-wider mb-1">Wrapping Key Label</label>
              <input className="input-base" value={wrapLabel} onChange={e => setWrapLabel(e.target.value)} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[10px] text-slate-600 uppercase tracking-wider mb-1">Algorithm</label>
                <select className="select-base" value={wrapAlgo} onChange={e => setWrapAlgo(e.target.value)}>
                  {ALGORITHMS.map(a => <option key={a} value={a}>{a}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-[10px] text-slate-600 uppercase tracking-wider mb-1">Key Size (bits)</label>
                <input className="input-base font-mono" type="number" value={wrapSize} onChange={e => setWrapSize(Number(e.target.value))} />
              </div>
            </div>
            <div>
              <label className="block text-[10px] text-slate-600 uppercase tracking-wider mb-1">Provider</label>
              <select className="select-base" value={wrapProvider} onChange={e => setWrapProvider(e.target.value)}>
                {PROVIDERS.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-[10px] text-slate-600 uppercase tracking-wider mb-1">Plaintext Key (hex)</label>
              <input className="input-base font-mono text-xs" value={plaintextHex} onChange={e => setPlaintextHex(e.target.value)} />
            </div>
            <Button onClick={() => wrapKey()} loading={wrapPending} className="w-full">
              <Lock className="w-4 h-4" /> Wrap Key
            </Button>
            {wrapError && <Alert variant="error">{wrapError}</Alert>}
          </div>
        </Card>

        {wrapResult && (
          <Card>
            <CardHeader title="Wrap Result" icon={<HardDrive className="w-4 h-4" />} />
            <div className="flex gap-2 flex-wrap mb-3">
              <Badge variant="cyan">{wrapResult.algorithm}</Badge>
              <Badge variant="violet">{wrapResult.provider}</Badge>
              <Badge variant="emerald">{wrapResult.operation}</Badge>
            </div>
            <div className="grid grid-cols-2 gap-3 mb-3 text-xs">
              <div className="bg-surface-700/40 rounded p-2 text-center">
                <p className="text-slate-500 mb-1">Input Size</p>
                <p className="text-slate-200 font-mono font-medium">{wrapResult.payload_size} bytes</p>
              </div>
              <div className="bg-surface-700/40 rounded p-2 text-center">
                <p className="text-slate-500 mb-1">Result Size</p>
                <p className="text-slate-200 font-mono font-medium">{wrapResult.result_size} bytes</p>
              </div>
            </div>
            <CodeBlock code={JSON.stringify(wrapResult, null, 2)} filename="wrap-result.json" downloadable />
          </Card>
        )}

        {!wrapResult && (
          <Card className="text-center py-12">
            <HardDrive className="w-8 h-8 text-slate-600 mx-auto mb-3" />
            <p className="text-sm text-slate-500">Wrap result will appear here</p>
          </Card>
        )}
      </div>
    </div>
  )
}
