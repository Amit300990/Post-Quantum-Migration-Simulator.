export interface BenchmarkResult {
  algorithm: string
  mode: string
  file_size: number
  keygen_time_ms: number
  encrypt_time_ms: number
  decrypt_time_ms: number
  ciphertext_size: number
  throughput_mb_s: number
  created_at?: string
}

export interface HandshakeResult {
  algorithm: string
  mode: string
  handshake_latency_ms: number
  payload_size: number
  shared_secret_size: number
  client_payload: string
  shared_secret: string
  timestamp: string
  created_at?: string
}

export interface EncryptResponse {
  algorithm: string
  mode: string
  timestamp: string
  key_size: number
  ciphertext: string
  nonce: string
  associated_data: string | null
  encrypted_key: string | null
  encapsulated_key: string | null
  private_key: string
  public_key: string
}

export interface DecryptResponse {
  algorithm: string
  plaintext: string
  message: string
}

export interface ResultsResponse {
  benchmarks: BenchmarkResult[]
  handshakes: HandshakeResult[]
}

export interface CryptoAsset {
  environment: string
  asset_type: string
  name: string
  source: string
  algorithm: string
  key_size: number | null
  ready_to_migrate: boolean
  exposure: string
  criticality: string
  owner: string | null
  service: string | null
}

export interface EnvironmentInventory {
  environment: string
  keys: number
  certificates: number
  ready_to_migrate: number
  assets: CryptoAsset[]
}

export interface InventoryScanResponse {
  scanned_at: string
  total_keys: number
  total_certificates: number
  total_ready_to_migrate: number
  environments: EnvironmentInventory[]
}

export interface AssetReadinessAssessment {
  environment: string
  asset_name: string
  asset_type: string
  source: string
  algorithm: string
  risk_score: number
  readiness_score: number
  risk_level: string
  migration_priority: string
  factors: string[]
  recommended_actions: string[]
}

export interface EnvironmentReadinessSummary {
  environment: string
  asset_count: number
  average_risk_score: number
  average_readiness_score: number
  critical_assets: number
  high_risk_assets: number
  ready_to_migrate: number
}

export interface ReadinessReport {
  scanned_at: string
  total_assets: number
  total_critical_assets: number
  total_high_risk_assets: number
  average_risk_score: number
  average_readiness_score: number
  environments: EnvironmentReadinessSummary[]
  assets: AssetReadinessAssessment[]
}

export interface NistProfile {
  name: string
  description: string
  allowed_kems: string[]
  allowed_signatures: string[]
  allowed_classical_key_exchange: string[]
  allowed_classical_signatures: string[]
  preferred_key_exchange_order: string[]
  min_rsa_bits: number
  allow_classical_only: boolean
  require_hybrid: boolean
  require_pqc: boolean
  target_state: string
  retirement_guidance: string[]
}

export interface NegotiationParty {
  key_exchange_algorithms: string[]
  signature_algorithms: string[]
}

export interface NegotiationResponse {
  status: 'negotiated' | 'failed'
  profile: string
  selected_key_exchange: string | null
  selected_signature: string | null
  protocol_mode: string | null
  failure_reason: string | null
  client_supported: NegotiationParty
  server_supported: NegotiationParty
}

export interface HsmKeyResponse {
  key_id: string
  label: string
  algorithm: string
  key_size: number
  exportable: boolean
  hsm_provider: string
}

export interface HsmOperationResponse {
  provider: string
  operation: string
  key_id: string
  algorithm: string
  payload_size: number
  result_size: number
}

export interface HealthResponse {
  status: string
  version: string
}
