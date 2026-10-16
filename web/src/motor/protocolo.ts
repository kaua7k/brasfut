// Mensagens entre a pagina e o Web Worker que roda o motor (Pyodide).
//
// A pagina manda o mesmo (metodo, caminho, corpo) que mandaria por fetch ao
// server.py; o worker devolve (status, corpo) como o HTTP devolveria. Assim o
// resto do front nao sabe se ha servidor ou nao.

export type PedidoAoMotor =
  | { id: number; tipo: 'iniciar'; base: string }
  | { id: number; tipo: 'pedido'; metodo: 'GET' | 'POST'; caminho: string; corpo?: unknown }
  | { id: number; tipo: 'medir'; semanas: number }

/** Quanto custou subir o motor, em ms, medido dentro do worker. */
export interface TemposCarga {
  /** baixar e iniciar o Pyodide (wasm + biblioteca padrao) */
  pyodide: number
  /** abrir o IndexedDB do save */
  save: number
  /** baixar os .py do jogo e gravar no sistema de arquivos virtual */
  arquivos: number
  /** importar brasfut.py e a api (compila o Python na primeira vez) */
  importar: number
  /** do worker nascer ao motor pronto */
  total: number
  /** memoria do WebAssembly depois de carregar, em MB */
  memoria_mb: number
}

export interface ResumoTempo {
  media: number
  pior: number
  melhor: number
}

/** O que `api.navegador.medir` devolve (segundos), mais a carga (ms). */
export interface Medicao {
  criar_mundo: number
  escolher_clube: number
  carregar_save: number
  tamanho_save: number
  clube: string
  divisao: string
  semana: ResumoTempo
  motor: ResumoTempo
  gravar: ResumoTempo
  semanas: { semana: number; fase: string; total: number; motor: number; gravar: number }[]
  /** gravar no IndexedDB um arquivo do tamanho do save (ms) */
  indexeddb_ms: number
  carga: TemposCarga
  memoria_mb: number
  /** tempo do lado da pagina, ida e volta da mensagem (ms) */
  parede_ms: number
}

export type RespostaDoMotor =
  | { id: number; tipo: 'resposta'; status: number; corpo: unknown }
  | { id: number; tipo: 'medicao'; medicao: Omit<Medicao, 'parede_ms'> }
  | { id: number; tipo: 'falha'; erro: string }
  | { id: 0; tipo: 'progresso'; etapa: string }
