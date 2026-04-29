import { useQuery } from '@tanstack/react-query'
import { CheckCircle, Shield, XCircle } from 'lucide-react'
import { api } from '../lib/api'
import type { NistProfile } from '../types'
import { Card } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { PageSpinner } from '../components/ui/Spinner'
import { Alert } from '../components/ui/Alert'

const PROFILE_ACCENT: Record<string, { badge: string; border: string; label: string }> = {
  baseline: { badge: 'default', border: 'border-slate-600', label: 'Stage 1' },
  hybrid_transition: { badge: 'amber', border: 'border-amber-500/30', label: 'Stage 2' },
  pqc_preferred: { badge: 'cyan', border: 'border-cyan-500/30', label: 'Stage 3' },
  strict_pqc: { badge: 'emerald', border: 'border-emerald-500/30', label: 'Stage 4' },
}

function BoolRow({ label, value }: { label: string; value: boolean }) {
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-surface-700/50 last:border-0">
      <span className="text-xs text-slate-400">{label}</span>
      {value
        ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
        : <XCircle className="w-3.5 h-3.5 text-slate-600" />
      }
    </div>
  )
}

function ProfileCard({ profile }: { profile: NistProfile }) {
  const accent = PROFILE_ACCENT[profile.name] ?? { badge: 'default', border: 'border-surface-600', label: '' }
  return (
    <Card className={`border ${accent.border} hover:shadow-lg transition-all`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-slate-500" />
          <p className="text-sm font-bold text-slate-100 capitalize">{profile.name.replace(/_/g, ' ')}</p>
        </div>
        <Badge variant={accent.badge as any}>{accent.label}</Badge>
      </div>

      <p className="text-xs text-slate-400 mb-4 leading-relaxed">{profile.description}</p>

      <div className="space-y-3 mb-4">
        <BoolRow label="Allow classical-only" value={profile.allow_classical_only} />
        <BoolRow label="Require hybrid mode" value={profile.require_hybrid} />
        <BoolRow label="Require PQC" value={profile.require_pqc} />
      </div>

      <div className="space-y-2">
        {profile.allowed_kems.length > 0 && (
          <div>
            <p className="text-[10px] text-slate-600 uppercase tracking-wider mb-1.5">Allowed KEMs</p>
            <div className="flex flex-wrap gap-1">
              {profile.allowed_kems.map(k => <Badge key={k} variant="cyan">{k}</Badge>)}
            </div>
          </div>
        )}
        {profile.allowed_signatures.length > 0 && (
          <div>
            <p className="text-[10px] text-slate-600 uppercase tracking-wider mb-1.5">Allowed Signatures</p>
            <div className="flex flex-wrap gap-1">
              {profile.allowed_signatures.map(s => <Badge key={s} variant="violet">{s}</Badge>)}
            </div>
          </div>
        )}
        {profile.allowed_classical_key_exchange.length > 0 && (
          <div>
            <p className="text-[10px] text-slate-600 uppercase tracking-wider mb-1.5">Classical KEX Allowed</p>
            <div className="flex flex-wrap gap-1">
              {profile.allowed_classical_key_exchange.map(k => <Badge key={k} variant="amber">{k}</Badge>)}
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 pt-3 border-t border-surface-700">
        <p className="text-[10px] text-slate-600 uppercase tracking-wider mb-1">Target State</p>
        <p className="text-xs text-slate-300">{profile.target_state}</p>
      </div>

      {profile.retirement_guidance.length > 0 && (
        <div className="mt-3">
          <p className="text-[10px] text-slate-600 uppercase tracking-wider mb-1.5">Retirement Guidance</p>
          <ul className="space-y-1">
            {profile.retirement_guidance.map((g, i) => (
              <li key={i} className="text-xs text-slate-400 flex gap-1.5">
                <span className="text-cyan-600 flex-shrink-0">›</span>
                {g}
              </li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  )
}

export default function Profiles() {
  const { data: profiles, isLoading, error } = useQuery({
    queryKey: ['profiles'],
    queryFn: api.getProfiles,
  })

  if (isLoading) return <PageSpinner label="Loading profiles…" />
  if (error) return (
    <Alert variant="error" title="Failed to load profiles">
      {(error as any).message}
    </Alert>
  )

  return (
    <div className="space-y-6 animate-fade-in">
      <Alert variant="info" title="NIST PQC Migration Profiles">
        These profiles define the algorithm constraints and enforcement levels for each stage of the
        post-quantum migration journey, aligned with NIST IR 8547 and SP 800-227 guidance.
      </Alert>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {(profiles ?? []).map(p => <ProfileCard key={p.name} profile={p} />)}
      </div>
    </div>
  )
}
