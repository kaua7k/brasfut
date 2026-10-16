// O motor do jogo dentro do navegador: Pyodide num Web Worker.
//
// So existe no build do GitHub Pages (modo navegador). O worker baixa o
// Pyodide (servido junto do app, em pyodide/, para funcionar offline), grava
// os .py do jogo no sistema de arquivos virtual, monta a pasta do save sobre o
// IndexedDB e responde cada pedido da pagina chamando api/navegador.py, que
// entra no mesmo despachante de rotas do server.py.
//
// Python roda sincrono aqui dentro: um pedido por vez, na ordem em que
// chegaram - o mesmo efeito do cadeado da sessao no servidor.

/// <reference lib="webworker" />

import type { PyodideAPI, loadPyodide as CarregarPyodide } from 'pyodide'
import type { PedidoAoMotor, RespostaDoMotor, TemposCarga } from './protocolo'

declare const self: DedicatedWorkerGlobalScope

const PASTA_CODIGO = '/brasfut/codigo'
const PASTA_SAVE = '/brasfut/save'

interface Motor {
  py: PyodideAPI
  pedido: (metodo: string, caminho: string, corpo: string | null) => string
  medir: (semanas: number) => string
  carga: TemposCarga
}

const nasceu = performance.now()
let motor: Promise<Motor> | null = null
let fila: Promise<void> = Promise.resolve()

function responder(r: RespostaDoMotor) {
  self.postMessage(r)
}

function progresso(etapa: string) {
  responder({ id: 0, tipo: 'progresso', etapa })
}

function memoriaMb(py: PyodideAPI): number {
  // o HEAP do Emscripten nao e API publica; serve so de numero para a medicao
  const heap = (py as unknown as { _module?: { HEAP8?: Int8Array } })._module?.HEAP8
  return heap ? Math.round(heap.length / 1048576) : 0
}

function syncfs(py: PyodideAPI, carregar: boolean): Promise<void> {
  return new Promise((ok, falha) => py.FS.syncfs(carregar, (e: unknown) => (e ? falha(e) : ok())))
}

/** Grava o save no IndexedDB. Uma sincronizacao por vez, em fila. */
function persistir(py: PyodideAPI): Promise<void> {
  fila = fila.then(() => syncfs(py, false)).catch((e) => console.error('BRASFUT: falha ao gravar o save', e))
  return fila
}

async function subir(base: string): Promise<Motor> {
  const t0 = performance.now()
  progresso('baixando o Python (Pyodide)')
  const { loadPyodide } = (await import(/* @vite-ignore */ `${base}pyodide/pyodide.mjs`)) as {
    loadPyodide: typeof CarregarPyodide
  }
  // o motor fala por print (era terminal); a API ja captura o que interessa
  const py = await loadPyodide({ indexURL: `${base}pyodide/`, stdout: () => {}, stderr: (texto: string) => console.warn(texto) })
  const t1 = performance.now()

  progresso('abrindo o save do aparelho')
  py.FS.mkdirTree(PASTA_SAVE)
  // os tipos do Emscripten nao trazem FS.filesystems, mas o Pyodide documenta o IDBFS ali
  const sistemas = (py.FS as unknown as { filesystems: Record<string, Emscripten.FileSystemType> }).filesystems
  py.FS.mount(sistemas.IDBFS, {}, PASTA_SAVE)
  await syncfs(py, true)
  const t2 = performance.now()

  progresso('baixando o motor do jogo')
  const lista = (await (await fetch(`${base}motor/arquivos.json`)).json()) as { versao: string; arquivos: string[] }
  await Promise.all(
    lista.arquivos.map(async (arq) => {
      const r = await fetch(`${base}motor/py/${arq}?v=${lista.versao}`)
      if (!r.ok) throw new Error(`faltou ${arq} (${r.status})`)
      const destino = `${PASTA_CODIGO}/${arq}`
      py.FS.mkdirTree(destino.slice(0, destino.lastIndexOf('/')))
      py.FS.writeFile(destino, new Uint8Array(await r.arrayBuffer()))
    }),
  )
  const t3 = performance.now()

  progresso('preparando o mundo')
  py.runPython(`
import sys
sys.path.insert(0, ${JSON.stringify(PASTA_CODIGO)})
sys.dont_write_bytecode = True
from api import navegador as _nav
_nav.iniciar(${JSON.stringify(PASTA_SAVE)})
`)
  const nav = py.pyimport('api.navegador') as unknown as {
    pedido: Motor['pedido']
    medir_json: Motor['medir']
  }
  const t4 = performance.now()
  const carga: TemposCarga = {
    pyodide: t1 - t0,
    save: t2 - t1,
    arquivos: t3 - t2,
    importar: t4 - t3,
    total: t4 - nasceu,
    memoria_mb: memoriaMb(py),
  }
  return { py, pedido: nav.pedido, medir: nav.medir_json, carga }
}

/** Quanto custa gravar um save do tamanho medido no IndexedDB (ms). */
async function medirIndexedDb(py: PyodideAPI, bytes: number): Promise<number> {
  const arq = `${PASTA_SAVE}/.medicao.tmp`
  py.FS.writeFile(arq, new Uint8Array(Math.max(1, bytes)).fill(32))
  const t0 = performance.now()
  await persistir(py)
  const dt = performance.now() - t0
  py.FS.unlink(arq)
  await persistir(py)
  return dt
}

self.onmessage = async (ev: MessageEvent<PedidoAoMotor>) => {
  const msg = ev.data
  try {
    if (msg.tipo === 'iniciar') {
      motor ??= subir(msg.base)
      const m = await motor
      responder({ id: msg.id, tipo: 'resposta', status: 200, corpo: m.carga })
      return
    }
    if (!motor) throw new Error('motor nao iniciado')
    const m = await motor
    if (msg.tipo === 'pedido') {
      const corpo = msg.corpo === undefined ? null : JSON.stringify(msg.corpo)
      const r = JSON.parse(m.pedido(msg.metodo, msg.caminho, corpo)) as {
        status: number
        corpo: unknown
        gravou: boolean
      }
      responder({ id: msg.id, tipo: 'resposta', status: r.status, corpo: r.corpo })
      if (r.gravou) void persistir(m.py)
      return
    }
    if (msg.tipo === 'medir') {
      const med = JSON.parse(m.medir(msg.semanas))
      const indexeddb_ms = await medirIndexedDb(m.py, med.tamanho_save)
      responder({
        id: msg.id,
        tipo: 'medicao',
        medicao: { ...med, indexeddb_ms, carga: m.carga, memoria_mb: memoriaMb(m.py) },
      })
    }
  } catch (e) {
    responder({ id: msg.id, tipo: 'falha', erro: e instanceof Error ? e.message : String(e) })
  }
}
