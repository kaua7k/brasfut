// Unico ponto que fala com o Python.
//
// Nenhum componente chama fetch: se a API mudar de forma, muda aqui e so aqui.
// Erro do servidor vira ErroDaApi com a mensagem que o Python escreveu - a
// tela mostra essa frase em vez de um "algo deu errado" que nao ajuda ninguem.

import type {
  ResumoTemporada,
  TelaCarreira,
  Config,
  OpcaoDificuldade,
  OpcoesCarreira,
  AbaMercado,
  Cabecalho,
  OpcaoAvanco,
  Paradas,
  Contagem,
  FiltrosMercado,
  LinhaCessao,
  LinhaPrecoVitrine,
  Mesa,
  Origem,
  PropostaMesa,
  TelaCompeticoes,
  TelaMercado,
  TipoMesa,
  DadosPainel,
  Pendencia,
  FichaJogador,
  PreviaEsquema,
  RespostaAcao,
  RespostaAvanco,
  RespostaEstado,
  TelaBase,
  TelaElenco,
  TelaEscalacao,
  TelaEstadio,
  TelaFinancas,
  TelaInfra,
  TelaNoticias,
  TelaTabela,
  TelaTreino,
} from './tipos'

export class ErroDaApi extends Error {
  status: number
  constructor(mensagem: string, status: number) {
    super(mensagem)
    this.name = 'ErroDaApi'
    this.status = status
  }
}

async function pedir<T>(caminho: string, corpo?: unknown): Promise<T> {
  let resposta: Response
  try {
    resposta = await fetch(caminho, {
      method: corpo === undefined ? 'GET' : 'POST',
      headers: corpo === undefined ? undefined : { 'Content-Type': 'application/json' },
      body: corpo === undefined ? undefined : JSON.stringify(corpo),
    })
  } catch {
    // servidor fechado no meio da partida: acontece se a janela do Python morreu
    throw new ErroDaApi('o servidor do jogo nao respondeu. Ele ainda esta aberto?', 0)
  }
  const dados = await resposta.json().catch(() => ({}))
  if (!resposta.ok) {
    throw new ErroDaApi(dados?.erro ?? `erro ${resposta.status}`, resposta.status)
  }
  return dados as T
}

/** Ação que pode pedir confirmação antes de mexer no jogo. */
type Acao<T> = (ids: number[], confirmar?: boolean) => Promise<RespostaAcao<T>>

function acao<T>(caminho: string): Acao<T> {
  return (ids, confirmar = false) => pedir<RespostaAcao<T>>(caminho, { ids, confirmar })
}

export const api = {
  // ------------------------------------------------------------------ inicio
  estado: () => pedir<RespostaEstado>('/api/estado'),
  abrir: () => pedir<RespostaEstado>('/api/abrir', {}),
  novo: (nome: string, opcoes: OpcoesCarreira) =>
    pedir<RespostaEstado>('/api/novo', { nome, opcoes }),
  config: () => pedir<{ config: Config; dificuldades: OpcaoDificuldade[] }>('/api/config'),
  gravarConfig: (mudanca: Partial<Config>) =>
    pedir<{ config: Config; dificuldades: OpcaoDificuldade[] }>('/api/config', mudanca),
  escolherClube: (id: number) => pedir<RespostaEstado>('/api/clube', { id }),
  encerrarCarreira: () => pedir<RespostaEstado>('/api/clube', { encerrar: true }),
  resumo: () => pedir<{ resumo: ResumoTemporada }>('/api/resumo'),

  // ------------------------------------------------------------------ painel
  painel: () => pedir<{ painel: DadosPainel }>('/api/painel'),
  avancar: (confirmar = false) => pedir<RespostaAvanco>('/api/avancar', { confirmar }),
  /** Um passo do avanco em ritmos: leve = sem o Painel inteiro de volta. */
  passoAvanco: (confirmar: boolean, paradas: Paradas, leve: boolean) =>
    pedir<RespostaAvanco>('/api/avancar', { confirmar, paradas, leve }),
  opcoesAvanco: () =>
    pedir<{ opcoes: OpcaoAvanco[]; paradas: Paradas; cabecalho: Cabecalho }>('/api/avanco/opcoes'),
  definirAuto: (ligada: boolean) =>
    pedir<{ mudou: boolean; painel: DadosPainel }>('/api/escalacao/auto', { ligada }),
  salvar: () => pedir<{ ok: boolean }>('/api/salvar', {}),

  // ------------------------------------------------------------------- telas
  elenco: () => pedir<{ tela: TelaElenco }>('/api/elenco'),
  base: () => pedir<{ tela: TelaBase }>('/api/base'),
  tabela: (alvo?: string) =>
    alvo === undefined
      ? pedir<{ tela: TelaTabela }>('/api/tabela')
      : pedir<{ tela: TelaTabela }>('/api/tabela', { alvo }),
  competicoes: (alvo?: string) =>
    alvo === undefined
      ? pedir<{ tela: TelaCompeticoes }>('/api/competicoes')
      : pedir<{ tela: TelaCompeticoes }>('/api/competicoes', { alvo }),
  financas: () => pedir<{ tela: TelaFinancas }>('/api/financas'),
  infra: () => pedir<{ tela: TelaInfra }>('/api/infra'),
  noticias: () => pedir<{ tela: TelaNoticias }>('/api/noticias'),
  carreira: () => pedir<{ tela: TelaCarreira }>('/api/carreira'),
  pedirDemissao: () => pedir<{ pendencia: Pendencia; cabecalho: Cabecalho }>('/api/carreira/demitir', {}),
  responderProposta: (id: number, aceitar: boolean) =>
    pedir<{ recado: string; painel: DadosPainel }>('/api/carreira/proposta', { id, aceitar }),
  ficha: (id: number) => pedir<{ ficha: FichaJogador }>('/api/ficha', { id }),

  // ------------------------------------------------------------------- acoes
  tirarDaVitrine: acao<TelaElenco>('/api/elenco/tirar-vitrine'),
  rescindir: acao<TelaElenco>('/api/elenco/rescindir'),
  exercerOpcao: acao<TelaElenco>('/api/elenco/opcao'),
  chamarDeVolta: acao<TelaElenco>('/api/elenco/chamar'),
  subirDaBase: acao<TelaBase>('/api/base/subir'),
  liberarDaBase: acao<TelaBase>('/api/base/liberar'),
  peneira: (regiao: string | null, foco: string | null) =>
    pedir<RespostaAcao<TelaBase>>('/api/base/peneira', regiao ? { regiao, foco } : { desligar: true }),
  candidato: (cid: number, aceitar: boolean) =>
    pedir<RespostaAcao<TelaBase>>('/api/base/candidato', { cid, aceitar }),
  investir: (id: string, confirmar = false) =>
    pedir<RespostaAcao<TelaInfra>>('/api/infra/investir', { id, confirmar }),

  // --------------------------------------------------------------- escalacao
  escalacao: () => pedir<{ tela: TelaEscalacao }>('/api/escalacao'),
  definirAutoNaEscalacao: (ligada: boolean) =>
    pedir<{ mudou: boolean; tela: TelaEscalacao }>('/api/escalacao/auto', {
      ligada,
      tela: 'escalacao',
    }),
  mudarEsquema: (esquema: { formacao?: string; tatica?: string; contagem?: Contagem }) =>
    pedir<RespostaAcao<TelaEscalacao>>('/api/escalacao/esquema', esquema),
  previaEsquema: (contagem: Contagem) =>
    pedir<{ previa: PreviaEsquema }>('/api/escalacao/previa', { contagem }),
  desfazerEsquema: () => pedir<RespostaAcao<TelaEscalacao>>('/api/escalacao/desfazer', {}),
  montarMelhor: () => pedir<RespostaAcao<TelaEscalacao>>('/api/escalacao/montar', {}),
  trocarTitular: (titular: number, reserva: number) =>
    pedir<RespostaAcao<TelaEscalacao>>('/api/escalacao/trocar', { titular, reserva }),
  inverterTitulares: (a: number, b: number) =>
    pedir<RespostaAcao<TelaEscalacao>>('/api/escalacao/inverter', { a, b }),
  mudarPlano: (eixo: string, valor: string) =>
    pedir<RespostaAcao<TelaEscalacao>>('/api/escalacao/plano', { eixo, valor }),
  planoPadrao: () => pedir<RespostaAcao<TelaEscalacao>>('/api/escalacao/plano', { padrao: true }),
  mudarCondicional: (condicao: string, minuto: number | null, tatica: string | null) =>
    pedir<RespostaAcao<TelaEscalacao>>('/api/escalacao/condicional', { condicao, minuto, tatica }),

  // ------------------------------------------------------------------ treino
  treino: () => pedir<{ tela: TelaTreino }>('/api/treino'),
  escolherRegime: (nome: string) =>
    pedir<RespostaAcao<TelaTreino>>('/api/treino/regime', { nome }),
  alternarFoco: (ids: number[]) => pedir<RespostaAcao<TelaTreino>>('/api/treino/foco', { ids }),
  alternarFocoNaBase: (ids: number[]) =>
    pedir<RespostaAcao<TelaBase>>('/api/treino/foco', { ids, tela: 'base' }),
  limparFoco: () => pedir<RespostaAcao<TelaTreino>>('/api/treino/limpar', {}),

  // ----------------------------------------------------------------- estadio
  estadio: () => pedir<{ tela: TelaEstadio }>('/api/estadio'),
  mudarPreco: (preco: number) => pedir<RespostaAcao<TelaEstadio>>('/api/estadio/preco', { preco }),
  contratarObra: (lugares: number, confirmar = false) =>
    pedir<RespostaAcao<TelaEstadio>>('/api/estadio/obra', { lugares, confirmar }),

  // ----------------------------------------------------------------- mercado
  mercado: (aba: AbaMercado = 'compra', filtros?: Partial<FiltrosMercado>) =>
    pedir<{ tela: TelaMercado }>('/api/mercado', { aba, filtros }),
  lerMesa: (tipo: TipoMesa, id: number, proposta?: PropostaMesa) =>
    pedir<{ mesa: Mesa }>('/api/mercado/mesa', { tipo, id, proposta }),
  propor: (tipo: TipoMesa, id: number, proposta: PropostaMesa) =>
    pedir<{ fechou: boolean; recado: string | null; mesa: Mesa }>('/api/mercado/propor', {
      tipo,
      id,
      proposta,
    }),
  linhasVitrine: (ids: number[]) =>
    pedir<{ linhas: LinhaPrecoVitrine[] }>('/api/mercado/vitrine/linhas', { ids }),
  sugerirPrecos: (ids: number[], pct: number) =>
    pedir<{ precos: { id: number; preco: number }[] }>('/api/mercado/vitrine/sugerir', { ids, pct }),
  // estas respondem com a tela de quem pediu: Elenco ou Mercado
  porAVenda: (precos: { id: number; preco: number }[], origem: Origem) =>
    pedir<RespostaAcao<unknown>>('/api/mercado/vitrine/por', { precos, ...origem }),
  tirarDaVitrineMercado: (ids: number[], origem: Origem) =>
    pedir<RespostaAcao<unknown>>('/api/mercado/vitrine/tirar', { ids, ...origem }),
  ofertasCessao: (ids: number[]) =>
    pedir<{ linhas: LinhaCessao[] }>('/api/mercado/ceder/ofertas', { ids }),
  ceder: (itens: { id: number; clube_id: number }[], origem: Origem, confirmar = false) =>
    pedir<RespostaAcao<unknown>>('/api/mercado/ceder', { itens, confirmar, ...origem }),
  aceitarPropostas: (itens: { id: number; clube_id: number }[], confirmar = false) =>
    pedir<RespostaAcao<TelaMercado>>('/api/mercado/propostas/aceitar', { itens, confirmar }),
  recusarPropostas: (itens: { id: number; clube_id: number }[]) =>
    pedir<RespostaAcao<TelaMercado>>('/api/mercado/propostas/recusar', { itens }),
  contraproposta: (id: number, clube_id: number, valor: number) =>
    pedir<RespostaAcao<TelaMercado> & { desfecho: string }>('/api/mercado/propostas/contra', {
      id,
      clube_id,
      valor,
    }),
  cancelarAgendadas: (indices: number[], origem: Origem, confirmar = false) =>
    pedir<RespostaAcao<unknown>>('/api/mercado/agendadas/cancelar', { indices, confirmar, ...origem }),
}
