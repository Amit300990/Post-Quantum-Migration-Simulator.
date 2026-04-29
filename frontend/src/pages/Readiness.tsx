import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, CheckCircle, RefreshCw, ShieldCheck } from 'lucide-react'
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { api } from '../lib/api'
import { AlgoBadge, RiskBadge } from '../components/ui/Badge'
import { Card, CardHeader } from '../components/ui/Card'
import { StatCard } from '../components/ui/StatCard'
import { Button } from '../components/ui/Button'
import { Alert } from '../components/ui/Alert'
import { PageSpinner } from '../components/ui/Spinner'

const RISK_COLORS: Record<string, string> = {
  critical: '#f85149',
  high: '#f97316',
  medium: '#e3b341',
  low: '#56d364',
}

function ScoreBar({ value, max = 100, color }: { value: number; max?: number; color: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-surface-700 rounded-full h-1.5">
        <div className="h-1.5 rounded-full transition-all duration-500" style={{ width: `${(value / max) * 100}%`, backgroundColor: color }} />
      </div>
      <span className="text-xs font-mono text-slate-300 w-8 text-right">{value}</span>
    </div>
  )
}

export default function Readiness() {
  const { data, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['readiness'],
    queryFn: api.getReadiness,
    retry: false,
  })

  if (isLoading) return <PageSpinner label="Scoring readiness…" />

  if (!data) return (
    <div className="space-y-4 animate-fade-in">
      <Alert variant="info" title="No inventory data">
        Run an inventory scan first, then return here for the readiness assessment.
      </Alert>
    </div>
  )

  const riskCounts = ['critical', 'high', 'medium', 'low'].map(level => ({
    name: level.charAt(0).toUpperCase() + level.slice(1),
    value: data.assets.filter(a => a.risk_level === level).length,
    color: RISK_COLORS[level],
  })).filter(d => d.value > 0)

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header action */}
      <div className="flex justify-between items-center">
        <div />
        <Button variant="secondary" size="sm" onClick={() => refetch()} loading={isRefetching}>
          <RefreshCw className="w-3.5 h-3.5" /> Refresh
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Assets" value={data.total_assets} icon={<ShieldCheck className="w-5 h-5" />} accent="cyan" />
        <StatCard label="Critical" value={data.total_critical_assets} icon={<AlertTriangle className="w-5 h-5" />} accent="amber"
          sub="Migrate first" />
        <StatCard label="Avg Risk Score" value={`${data.average_risk_score.toFixed(0)}/100`} icon={<AlertTriangle className="w-5 h-5" />} accent="amber" />
        <StatCard label="Avg Readiness" value={`${data.average_readiness_score.toFixed(0)}/100`} icon={<CheckCircle className="w-5 h-5" />} accent="emerald" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Risk distribution */}
        <Card>
          <CardHeader title="Risk Distribution" subtitle="Assets by risk level" icon={<AlertTriangle className="w-4 h-4" />} />
          {riskCounts.length === 0 ? (
            <div className="h-40 flex items-center justify-center text-slate-600 text-sm">No data</div>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={riskCounts} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" paddingAngle={2}>
                  {riskCounts.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Pie>
                <Tooltip formatter={(v, n) => [v, n]} contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8, fontSize: 12 }} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </Card>

        {/* Environment summary */}
        <Card className="xl:col-span-2">
          <CardHeader title="Environment Breakdown" icon={<ShieldCheck className="w-4 h-4" />} />
          <div className="space-y-4">
            {data.environments.filter(e => e.asset_count > 0).map(env => (
              <div key={env.environment} className="p-3 bg-surface-700/40 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-slate-200 capitalize">{env.environment.replace('_', ' ')}</p>
                  <span className="text-xs text-slate-500">{env.asset_count} assets · {env.ready_to_migrate} ready</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <p className="text-[10px] text-slate-600 mb-1">Risk</p>
                    <ScoreBar value={Math.round(env.average_risk_score)} color="#e3b341" />
                  </div>
                  <div>
                    <p className="text-[10px] text-slate-600 mb-1">Readiness</p>
                    <ScoreBar value={Math.round(env.average_readiness_score)} color="#56d364" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Asset table */}
      <Card>
        <CardHeader title={`Asset Assessments (${data.assets.length})`} icon={<ShieldCheck className="w-4 h-4" />} />
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-left text-slate-500 border-b border-surface-700">
                {['Asset', 'Type', 'Algorithm', 'Risk', 'Risk Score', 'Readiness', 'Priority'].map(h => (
                  <th key={h} className="pb-2 pr-4 font-medium uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.assets.map((a, i) => (
                <tr key={i} className="border-b border-surface-700/40 hover:bg-surface-700/30">
                  <td className="py-2 pr-4 text-slate-200 font-medium max-w-[140px] truncate">{a.asset_name}</td>
                  <td className="py-2 pr-4 capitalize text-slate-400">{a.asset_type}</td>
                  <td className="py-2 pr-4"><AlgoBadge algo={a.algorithm} /></td>
                  <td className="py-2 pr-4"><RiskBadge level={a.risk_level} /></td>
                  <td className="py-2 pr-4">
                    <ScoreBar value={a.risk_score} color={RISK_COLORS[a.risk_level] ?? '#8b949e'} />
                  </td>
                  <td className="py-2 pr-4">
                    <ScoreBar value={a.readiness_score} color="#56d364" />
                  </td>
                  <td className="py-2 text-slate-400 max-w-[160px]">{a.migration_priority}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
