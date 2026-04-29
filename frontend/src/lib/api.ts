import axios from 'axios'
import type {
  BenchmarkResult, DecryptResponse, EncryptResponse, HealthResponse,
  HsmKeyResponse, HsmOperationResponse, InventoryScanResponse,
  NegotiationResponse, NistProfile, ReadinessReport, ResultsResponse,
} from '../types'

const client = axios.create({
  baseURL: '/api',
  timeout: 120_000,
})

export const api = {
  health: (): Promise<HealthResponse> =>
    client.get('/health').then(r => r.data),

  listAlgorithms: (): Promise<{ algorithms: string[]; mode: string }> =>
    client.get('/algorithms').then(r => r.data),

  encryptFile: (algorithm: string, file: File): Promise<EncryptResponse> => {
    const form = new FormData()
    form.append('file', file)
    return client.post(`/encrypt?algorithm=${algorithm}`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data)
  },

  decryptPayload: (algorithm: string, privateKey: string, payload: Record<string, unknown>): Promise<DecryptResponse> =>
    client.post('/decrypt', { algorithm, private_key: privateKey, payload }).then(r => r.data),

  runBenchmark: (algorithm: string): Promise<{ results: BenchmarkResult[] }> =>
    client.post(`/benchmark?algorithm=${algorithm}`).then(r => r.data),

  simulateHandshake: (mode: string) =>
    client.post(`/handshake?mode=${mode}`).then(r => r.data),

  getResults: (): Promise<ResultsResponse> =>
    client.get('/results').then(r => r.data),

  exportResults: (fmt: 'json' | 'csv'): Promise<string> =>
    client.get(`/export?fmt=${fmt}`, { responseType: fmt === 'csv' ? 'text' : 'json' })
      .then(r => fmt === 'csv' ? r.data : JSON.stringify(r.data, null, 2)),

  scanInventory: (): Promise<InventoryScanResponse> =>
    client.post('/inventory/scan').then(r => r.data),

  getInventory: (): Promise<InventoryScanResponse> =>
    client.get('/inventory/environments').then(r => r.data),

  getReadiness: (): Promise<ReadinessReport> =>
    client.get('/readiness').then(r => r.data),

  getProfiles: (): Promise<NistProfile[]> =>
    client.get('/profiles').then(r => r.data),

  negotiate: (
    profile: string,
    client_kex: string[],
    client_sig: string[],
    server_kex: string[],
    server_sig: string[],
  ): Promise<NegotiationResponse> =>
    client.post('/negotiate', {
      profile,
      client: { key_exchange_algorithms: client_kex, signature_algorithms: client_sig },
      server: { key_exchange_algorithms: server_kex, signature_algorithms: server_sig },
    }).then(r => r.data),

  generateHsmKey: (
    label: string,
    algorithm: string,
    key_size: number,
    exportable: boolean,
    provider: string,
  ): Promise<HsmKeyResponse> =>
    client.post('/hsm/keys', { label, algorithm, key_size, exportable, provider }).then(r => r.data),

  wrapHsmKey: (
    label: string,
    algorithm: string,
    key_size: number,
    provider: string,
    plaintext_key_hex: string,
  ): Promise<HsmOperationResponse> =>
    client.post('/hsm/wrap', { label, algorithm, key_size, provider, plaintext_key_hex }).then(r => r.data),
}
