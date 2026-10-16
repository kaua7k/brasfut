// O lado da pagina do modo navegador: conversa com o worker do motor.
//
// `api.ts` chama `pedirAoMotor` no lugar do fetch quando o build e o do
// GitHub Pages. O worker so nasce no primeiro pedido, e o primeiro pedido
// espera o Pyodide subir (alguns segundos; a tela de abertura mostra a etapa).

import type { Medicao, PedidoAoMotor, RespostaDoMotor, TemposCarga } from './protocolo'

type Pendente = { ok: (r: RespostaDoMotor) => void; falha: (e: Error) => void }
type DistribuirPedido<T> = T extends unknown ? Omit<T, 'id'> : never

let worker: Worker | null = null
let proximo = 1
let pronto: Promise<TemposCarga> | null = null
const pendentes = new Map<number, Pendente>()
const ouvintes = new Set<(etapa: string) => void>()
let ultimaEtapa = ''

/** Avisa a etapa da carga do motor (para a tela de "abrindo o jogo"). */
export function aoProgresso(cb: (etapa: string) => void): () => void {
  ouvintes.add(cb)
  if (ultimaEtapa) cb(ultimaEtapa)
  return () => ouvintes.delete(cb)
}

function enviar(msg: DistribuirPedido<PedidoAoMotor>): Promise<RespostaDoMotor> {
  if (!worker) {
    worker = new Worker(new URL('./worker.ts', import.meta.url), { type: 'module', name: 'motor-brasfut' })
    worker.onmessage = (ev: MessageEvent<RespostaDoMotor>) => {
      const r = ev.data
      if (r.tipo === 'progresso') {
        ultimaEtapa = r.etapa
        ouvintes.forEach((cb) => cb(r.etapa))
        return
      }
      const p = pendentes.get(r.id)
      if (!p) return
      pendentes.delete(r.id)
      if (r.tipo === 'falha') p.falha(new Error(r.erro))
      else p.ok(r)
    }
    worker.onerror = (ev) => {
      const erro = new Error(`o motor do jogo parou: ${ev.message || 'erro no worker'}`)
      pendentes.forEach((p) => p.falha(erro))
      pendentes.clear()
    }
  }
  const id = proximo++
  return new Promise((ok, falha) => {
    pendentes.set(id, { ok, falha })
    worker?.postMessage({ ...msg, id } as PedidoAoMotor)
  })
}

/** Sobe o motor uma vez; os pedidos seguintes so esperam ele ficar pronto. */
export function iniciarMotor(): Promise<TemposCarga> {
  pronto ??= (async () => {
    // pede ao navegador para nao apagar o save quando faltar espaco
    // (Safari apaga dados de site nao instalado depois de dias sem uso)
    navigator.storage?.persist?.().catch(() => false)
    const base = new URL(import.meta.env.BASE_URL, document.baseURI).href
    const r = await enviar({ tipo: 'iniciar', base })
    return (r as { corpo: TemposCarga }).corpo
  })()
  pronto.catch(() => {
    pronto = null
  })
  return pronto
}

/** O mesmo contrato do fetch ao server.py: status HTTP e o corpo JSON. */
export async function pedirAoMotor(
  metodo: 'GET' | 'POST',
  caminho: string,
  corpo?: unknown,
): Promise<{ status: number; corpo: unknown }> {
  await iniciarMotor()
  const r = await enviar({ tipo: 'pedido', metodo, caminho, corpo })
  return r as { status: number; corpo: unknown }
}

/** Carreira de teste em memoria e N semanas simuladas (nao toca no save). */
export async function medirDesempenho(semanas: number): Promise<Medicao> {
  await iniciarMotor()
  const t0 = performance.now()
  const r = await enviar({ tipo: 'medir', semanas })
  if (r.tipo !== 'medicao') throw new Error('resposta inesperada do motor')
  return { ...r.medicao, parede_ms: performance.now() - t0 }
}
