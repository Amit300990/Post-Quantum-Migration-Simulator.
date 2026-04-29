import { useState } from 'react'
import { Cloud, HardDrive, Key, ScanLine, Server } from 'lucide-react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { CryptoAsset, EnvironmentInventory } from '../types'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Alert } from '../components/ui/Alert'
import { AlgoBadge, Badge } from '../components/ui/Badge'
import { StatCard } from '../components/ui/StatCard'
import { PageSpinner } from '../components/ui/Spinner'

const ENV_ICONS: Record<string, any> = {
  aws: Cloud,
  azure: Cloud,
  gcp: Cloud,
  on_prem: Server,
}

const ENV_LABELS: Record<string, string> = {
  aws: 'AWS',
  azure: 'Azure',
  gcp: 'GCP',
  on_prem: 'On-Premises',
}

function AssetTable({ assets }: { assets: CryptoAsset[] }) {
  if (assets.length === 0) return (
    <p className="text-sm text-slate-600 text-center py-6">No assets found in this environment</p>
  )
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr className="text-left text-slate-500 border-b border-surface-700">
            {['Name', 'Type', 'Algorithm', 'Exposure', 'Criticality', 'Source'].map(h => (
              <th key={h} className="pb-2 pr-4 font-medium uppercase tracking-wider">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {assets.map((a, i) => (
            <tr key={i} className="border-b border-surface-700/40 hover:bg-surface-700/30 transition-colors">
              <td className="py-2 pr-4 text-slate-200 font-medium max-w-[160px] truncate">{a.name}</td>
              <td className="py-2 pr-4">
                <Badge variant={a.asset_type === 'key' ? 'violet' : 'cyan'}>{a.asset_type}</Badge>
              </td>
              <td className="py-2 pr-4"><AlgoBadge algo={a.algorithm} /></td>
              <td className="py-2 pr-4">
                <Badge variant={a.exposure === 'public' ? 'orange' : a.exposure === 'internal' ? 'emerald' : 'default'}>
                  {a.exposure}
                </Badge>
              </td>
              <td className="py-2 pr-4">
                <Badge variant={a.criticality === 'critical' ? 'red' : a.criticality === 'high' ? 'orange' : a.criticality === 'medium' ? 'amber' : 'default'}>
                  {a.criticality}
                </Badge>
              </td>
              <td className="py-2 font-mono text-slate-500 max-w-[180px] truncate">{a.source}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function Inventory() {
  const qc = useQueryClient()
  const [tab, setTab] = useState<string>('')
  const [error, setError] = useState<string | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['inventory'],
    queryFn: api.getInventory,
    retry: false,
  })

  const { mutate: scan, isPending } = useMutation({
    mutationFn: api.scanInventory,
    onSuccess: (d) => {
      qc.setQueryData(['inventory'], d)
      if (d.environments.length > 0) setTab(d.environments[0].environment)
      setError(null)
    },
    onError: (e: any) => setError(e.response?.data?.detail ?? e.message ?? 'Scan failed'),
  })

  const envs: EnvironmentInventory[] = data?.environments ?? []
  const activeEnv = envs.find(e => e.environment === tab) ?? envs[0]

  if (isLoading) return <PageSpinner label="Loading inventory…" />

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Controls */}
      <Card>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <div className="flex-1">
            <p className="text-sm font-semibold text-slate-100 mb-1">Crypto Asset Inventory</p>
            <p className="text-xs text-slate-500">
              Scan AWS, Azure, GCP, and on-premises environments for cryptographic keys and certificates.
              Results are derived from configured inventory JSON files and on-prem file-system scanning.
            </p>
          </div>
          <Button onClick={() => scan()} loading={isPending}>
            <ScanLine className="w-4 h-4" />
            Scan Inventory
          </Button>
        </div>
        {error && <Alert variant="error" className="mt-3">{error}</Alert>}
      </Card>

      {data && (
        <>
          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard label="Total Keys" value={data.total_keys} icon={<Key className="w-5 h-5" />} accent="cyan" />
            <StatCard label="Certificates" value={data.total_certificates} icon={<HardDrive className="w-5 h-5" />} accent="violet" />
            <StatCard label="Ready to Migrate" value={data.total_ready_to_migrate} icon={<ScanLine className="w-5 h-5" />} accent="emerald"
              sub={`of ${data.total_keys + data.total_certificates} total`} />
            <StatCard label="Environments" value={envs.filter(e => e.keys + e.certificates > 0).length} icon={<Cloud className="w-5 h-5" />} accent="amber" />
          </div>

          {/* Environment tabs */}
          {envs.length > 0 && (
            <Card>
              <div className="flex gap-0 border-b border-surface-700 mb-4 -mx-5 px-5">
                {envs.map(env => {
                  const Icon = ENV_ICONS[env.environment] ?? Server
                  const isActive = (tab || envs[0]?.environment) === env.environment
                  return (
                    <button
                      key={env.environment}
                      onClick={() => setTab(env.environment)}
                      className={`flex items-center gap-1.5 px-4 py-2.5 text-xs font-medium border-b-2 transition-colors -mb-px ${
                        isActive ? 'border-cyan-500 text-cyan-400' : 'border-transparent text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      {ENV_LABELS[env.environment] ?? env.environment}
                      <span className="ml-1 px-1.5 py-0.5 rounded text-[10px] bg-surface-700 text-slate-500">
                        {env.keys + env.certificates}
                      </span>
                    </button>
                  )
                })}
              </div>

              {activeEnv && (
                <div>
                  <div className="flex gap-4 mb-4 text-xs text-slate-500">
                    <span><span className="text-slate-300 font-medium">{activeEnv.keys}</span> keys</span>
                    <span><span className="text-slate-300 font-medium">{activeEnv.certificates}</span> certs</span>
                    <span><span className="text-emerald-400 font-medium">{activeEnv.ready_to_migrate}</span> ready to migrate</span>
                  </div>
                  <AssetTable assets={activeEnv.assets} />
                </div>
              )}
            </Card>
          )}

          {envs.length === 0 && (
            <Card className="text-center py-12">
              <ScanLine className="w-8 h-8 text-slate-600 mx-auto mb-3" />
              <p className="text-sm text-slate-500">Click Scan Inventory to discover crypto assets</p>
            </Card>
          )}
        </>
      )}

      {!data && !isLoading && (
        <Card className="text-center py-12">
          <ScanLine className="w-8 h-8 text-slate-600 mx-auto mb-3" />
          <p className="text-sm text-slate-500 mb-4">No inventory data yet</p>
          <Button onClick={() => scan()} loading={isPending}>
            <ScanLine className="w-4 h-4" /> Scan Now
          </Button>
        </Card>
      )}
    </div>
  )
}
