import { useCallback, useRef, useState } from 'react'
import { CloudUpload, KeyRound, Lock, Unlock } from 'lucide-react'
import { api } from '../lib/api'
import { formatBytes } from '../lib/utils'
import type { EncryptResponse } from '../types'
import { Button } from '../components/ui/Button'
import { Card, CardHeader } from '../components/ui/Card'
import { Alert } from '../components/ui/Alert'
import { CodeBlock } from '../components/ui/CodeBlock'
import { Badge } from '../components/ui/Badge'

type Algorithm = 'rsa' | 'kyber'

function AlgoSelect({ value, onChange }: { value: Algorithm; onChange: (v: Algorithm) => void }) {
  return (
    <div className="flex gap-2">
      {(['rsa', 'kyber'] as Algorithm[]).map(a => (
        <button
          key={a}
          onClick={() => onChange(a)}
          className={`px-4 py-1.5 rounded-lg text-sm font-medium border transition-all ${
            value === a
              ? a === 'rsa'
                ? 'bg-amber-500/20 border-amber-500/50 text-amber-300'
                : 'bg-cyan-500/20 border-cyan-500/50 text-cyan-300'
              : 'bg-surface-700 border-surface-600 text-slate-400 hover:text-slate-200'
          }`}
        >
          {a.toUpperCase()}
        </button>
      ))}
    </div>
  )
}

export default function Crypto() {
  const [encAlgo, setEncAlgo] = useState<Algorithm>('kyber')
  const [encFile, setEncFile] = useState<File | null>(null)
  const [encLoading, setEncLoading] = useState(false)
  const [encResult, setEncResult] = useState<EncryptResponse | null>(null)
  const [encError, setEncError] = useState<string | null>(null)
  const [dragging, setDragging] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  const [decAlgo, setDecAlgo] = useState<Algorithm>('kyber')
  const [decPayload, setDecPayload] = useState('')
  const [decKey, setDecKey] = useState('')
  const [decLoading, setDecLoading] = useState(false)
  const [decResult, setDecResult] = useState<string | null>(null)
  const [decError, setDecError] = useState<string | null>(null)

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) setEncFile(f)
  }, [])

  const handleEncrypt = async () => {
    if (!encFile) return
    setEncLoading(true)
    setEncError(null)
    setEncResult(null)
    try {
      const result = await api.encryptFile(encAlgo, encFile)
      setEncResult(result)
    } catch (e: any) {
      setEncError(e.response?.data?.detail ?? e.message ?? 'Encryption failed')
    } finally {
      setEncLoading(false)
    }
  }

  const handleDecrypt = async () => {
    setDecLoading(true)
    setDecError(null)
    setDecResult(null)
    try {
      const payload = JSON.parse(decPayload)
      const result = await api.decryptPayload(decAlgo, decKey.trim(), payload)
      setDecResult(atob(result.plaintext))
    } catch (e: any) {
      setDecError(e.response?.data?.detail ?? e.message ?? 'Decryption failed')
    } finally {
      setDecLoading(false)
    }
  }

  const loadEncryptResult = () => {
    if (!encResult) return
    const { private_key, public_key, ...rest } = encResult
    setDecAlgo(encResult.algorithm as Algorithm)
    setDecPayload(JSON.stringify(rest, null, 2))
    setDecKey(private_key)
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 animate-fade-in">
      {/* Encrypt */}
      <div className="space-y-4">
        <Card>
          <CardHeader title="Encrypt File" subtitle="Hybrid encryption using RSA-OAEP+AES-GCM or Kyber-KEM+AES-GCM" icon={<Lock className="w-4 h-4" />} />

          <div className="space-y-4">
            <div>
              <label className="block text-xs text-slate-500 mb-2 font-medium uppercase tracking-wider">Algorithm</label>
              <AlgoSelect value={encAlgo} onChange={setEncAlgo} />
            </div>

            <div>
              <label className="block text-xs text-slate-500 mb-2 font-medium uppercase tracking-wider">File</label>
              <div
                className={`relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
                  dragging ? 'border-cyan-500 bg-cyan-500/5' : 'border-surface-600 hover:border-surface-500 hover:bg-surface-700/30'
                }`}
                onDragOver={e => { e.preventDefault(); setDragging(true) }}
                onDragLeave={() => setDragging(false)}
                onDrop={onDrop}
                onClick={() => fileRef.current?.click()}
              >
                <input
                  ref={fileRef}
                  type="file"
                  className="hidden"
                  onChange={e => setEncFile(e.target.files?.[0] ?? null)}
                />
                <CloudUpload className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                {encFile ? (
                  <div>
                    <p className="text-sm text-slate-200 font-medium">{encFile.name}</p>
                    <p className="text-xs text-slate-500 mt-1">{formatBytes(encFile.size)}</p>
                  </div>
                ) : (
                  <div>
                    <p className="text-sm text-slate-400">Drop a file here or <span className="text-cyan-400">browse</span></p>
                    <p className="text-xs text-slate-600 mt-1">Max 50 MB</p>
                  </div>
                )}
              </div>
            </div>

            <Button onClick={handleEncrypt} loading={encLoading} disabled={!encFile} className="w-full">
              <Lock className="w-4 h-4" /> Encrypt File
            </Button>

            {encError && <Alert variant="error">{encError}</Alert>}
          </div>
        </Card>

        {encResult && (
          <Card>
            <CardHeader
              title="Encrypted Payload"
              subtitle="Save the key — it cannot be recovered later"
              icon={<KeyRound className="w-4 h-4" />}
              action={
                <Button size="sm" variant="secondary" onClick={loadEncryptResult}>
                  Load into Decrypt
                </Button>
              }
            />
            <div className="space-y-3">
              <div className="flex gap-2 flex-wrap">
                <Badge variant="cyan">{encResult.algorithm.toUpperCase()}</Badge>
                <Badge variant="default">{encResult.mode}</Badge>
                <Badge variant="default">{encResult.key_size} bits</Badge>
              </div>
              <div>
                <p className="text-xs text-slate-500 mb-1.5 font-medium uppercase tracking-wider">Private Key (base64)</p>
                <CodeBlock code={encResult.private_key} language="text" filename="private.key" downloadable maxHeight="80px" />
              </div>
              <div>
                <p className="text-xs text-slate-500 mb-1.5 font-medium uppercase tracking-wider">Full Payload</p>
                <CodeBlock
                  code={JSON.stringify({ ...encResult, private_key: '(omitted — see above)', public_key: '(omitted)' }, null, 2)}
                  filename="payload.json"
                  downloadable
                />
              </div>
            </div>
          </Card>
        )}
      </div>

      {/* Decrypt */}
      <div className="space-y-4">
        <Card>
          <CardHeader title="Decrypt Payload" subtitle="Provide the payload JSON and matching private key" icon={<Unlock className="w-4 h-4" />} />

          <div className="space-y-4">
            <div>
              <label className="block text-xs text-slate-500 mb-2 font-medium uppercase tracking-wider">Algorithm</label>
              <AlgoSelect value={decAlgo} onChange={setDecAlgo} />
            </div>

            <div>
              <label className="block text-xs text-slate-500 mb-1.5 font-medium uppercase tracking-wider">Payload JSON</label>
              <textarea
                className="input-base font-mono min-h-[140px] resize-y text-xs"
                placeholder='{"ciphertext": "...", "nonce": "...", ...}'
                value={decPayload}
                onChange={e => setDecPayload(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-xs text-slate-500 mb-1.5 font-medium uppercase tracking-wider">Private Key (base64)</label>
              <textarea
                className="input-base font-mono min-h-[80px] resize-y text-xs"
                placeholder="Paste base64-encoded private key…"
                value={decKey}
                onChange={e => setDecKey(e.target.value)}
              />
            </div>

            <Button onClick={handleDecrypt} loading={decLoading} disabled={!decPayload || !decKey} className="w-full">
              <Unlock className="w-4 h-4" /> Decrypt
            </Button>

            {decError && <Alert variant="error">{decError}</Alert>}
          </div>
        </Card>

        {decResult !== null && (
          <Card>
            <CardHeader title="Decrypted Content" icon={<Unlock className="w-4 h-4" />} />
            <Alert variant="success" title="Decryption successful">
              Plaintext recovered and displayed below.
            </Alert>
            <div className="mt-3">
              <CodeBlock code={decResult} language="text" filename="plaintext.txt" downloadable maxHeight="240px" />
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}
