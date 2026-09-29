// O contrato com a API, escrito uma vez so.
//
// Estes tipos sao o espelho de api/dto.py. Quando uma tela nova for migrada,
// o DTO dela entra aqui junto - e o TypeScript passa a cobrar a tela inteira
// se o Python mudar um campo de nome.

export type Estado = 'ok' | 'atencao' | 'critico' | 'neutro'

export interface ItemMenu {
  id: string
  nome: string
  pronta: boolean
}

export interface ChipTopo {
  label: string
  valor: string
  estado?: Estado
}

export interface Cabecalho {
  clube: string
  divisao: string
  subtitulo: string
  fase: string
  acao: string
  chips: ChipTopo[]
  menu: ItemMenu[]
}

export interface Prontidao {
  estado: Estado
  titulo: string
  detalhe: string
  acao: { label: string; destino: string } | null
}

export interface Forca {
  meu: number
  dele: number | null
}

export interface Proximo {
  tipo: 'jogo' | 'copa' | 'folga' | 'pretemporada'
  adversario: string
  legenda: string
  em_casa: boolean | null
  forte?: boolean
  extras: number
  /** meu ataque x defesa do adversario (dele = defesa dele) */
  ataque: Forca
  /** minha defesa x ataque do adversario (dele = ataque dele) */
  defesa: Forca
}

export interface JogadorEmCampo {
  id: number
  nome: string
  curto: string
  iniciais: string
  pos: string
  vaga: string
  improvisado: boolean
  afinidade: number
  ovr: number
  cond: number
  estado: Estado
  obs: string
  x: number
  y: number
  numero: number
}

export interface Escalacao {
  formacao: string
  tatica: string
  auto: boolean
  estado: Estado
  jogadores: JogadorEmCampo[]
  vagas_abertas: number
}

export interface Objetivo {
  texto: string
  pos: number | null
  total: number
  alvo: number
  comecou: boolean
  estado: Estado
  diretoria: string
  folga: number | null
  progresso: number
  marca: number
  confianca: Confianca
}

export interface Confianca {
  valor: number
  estado: Estado
  fala: string
  aviso: boolean
  /** soma das ultimas 4 semanas */
  tendencia: number
  limite_aviso: number
  limite_demissao: number
  causas: { texto: string; estado: Estado }[]
}

export interface LinhaTabela {
  pos: number
  clube: string
  j: number
  sg: number
  v: number
  pts: number
  eu: boolean
  zona: 'alta' | 'baixa' | ''
  /** a zona em palavras: "G4", "acesso", "rebaixamento", "vai ao mata-mata" */
  zona_texto?: string | null
}

export interface Tabela {
  titulo: string
  vazio: string | null
  linhas: LinhaTabela[]
}

export interface Destaque {
  id: number
  nome: string
  iniciais: string
  pos: string
  ovr: number
  g: number
  a: number
}

export interface Placar {
  eu: number
  ele: number
  em_casa: boolean
  adversario: string
  estado: Estado
}

export interface Resultados {
  placares: Placar[]
  forma: { letra: 'V' | 'E' | 'D'; descricao: string }[]
  alerta: { texto: string; estado: Estado } | null
  /** as ultimas partidas guardadas (dto.partida), da mais antiga a mais nova */
  partidas: Partida[]
}

/** lado 0 e o mandante, 1 o visitante */
export type Lado = 0 | 1

export interface LinhaNota {
  vaga: string
  nome: string
  nota: number
}

export interface Partida {
  chave: string
  comp: string
  rodada: string
  resultado: 'V' | 'E' | 'D'
  estado: Estado
  eu: Lado
  times: [string, string]
  placar: [number, number]
  gols: { minuto: number; lado: Lado; autor: string; assist: string }[]
  cartoes: { minuto: number; lado: Lado; tipo: 'amarelo' | 'vermelho' | 'segundo_amarelo'; nome: string }[]
  /** trocas de mentalidade em campo (instrucao condicional ou a regra da maquina) */
  instrucoes: { minuto: number; lado: Lado; tatica: string; motivo: string }[]
  posse: [number, number]
  chutes: [number, number]
  no_gol: [number, number]
  melhor: { nome: string; vaga: string; nota: number; time: string } | null
  detalhes: {
    notas: [LinhaNota[], LinhaNota[]]
    subs: { minuto: number; lado: Lado; entra: string; sai: string }[]
    lesoes: { minuto: number; lado: Lado; nome: string }[]
    estatisticas: { rotulo: string; valores: [number, number] }[]
    publico: string | null
    decisao: string | null
  }
}

export interface Noticia {
  texto: string
  estado: Estado
  quando: string
}

export interface DadosPainel {
  cabecalho: Cabecalho
  prontidao: Prontidao
  proximo: Proximo
  escalacao: Escalacao
  objetivo: Objetivo
  tabela: Tabela
  destaques: Destaque[]
  resultados: Resultados
  noticias: Noticia[]
  /** quem esta no ultimo ano (ou venceu): atalho para a fila de renovacao */
  contratos: AvisoContratos | null
  /** propostas da semana pelos meus jogadores (dto._propostas_jogadores) */
  propostas_jogadores: AvisoPropostas | null
  /** clubes querendo o treinador */
  propostas_emprego: PropostaEmprego[]
  /** espacos de patrocinio sem contrato (pre-temporada): atalho para Financas */
  patrocinio_vago: string[] | null
  /** o resto do futebol: as ultimas manchetes */
  mundo: Manchete[]
}

export interface PropostaEmprego {
  id: number
  clube: string
  divisao: string
  liga: string
  reputacao: number
  semanas: number
}

export interface Manchete {
  texto: string
  tipo: 'resultado' | 'tabela' | 'copa' | 'titulo' | 'mercado' | 'lesao' | string
  rotulo: string
  quando: string
}

export interface PassagemCarreira {
  clube: string
  divisao: string
  liga: string
  periodo: string
  atual: boolean
  saida: string | null
  j: number
  v: number
  e: number
  d: number
  gp: number
  gc: number
  aproveitamento: number | null
  titulos: string[]
  marcos: string[]
  /** save de antes da sala de trofeus: o registro comeca no meio */
  parcial: boolean
}

export interface TelaClube {
  cabecalho: Cabecalho
  titulo: string
  subtitulo: string
  id: number
  /** o clube do treinador (os outros aparecem pelo seletor) */
  meu: boolean
  info: { nome: string; valor: string }[]
  metricas: Metrica[]
  destaques: { id: number; nome: string; pos: string; ovr: number; idade: number }[]
  artilheiro: { nome: string; gols: number; jogos: number } | null
  /** real ate 2025 e do jogo somados; anos ja vem em texto */
  sala: { nome: string; qtd: number; anos: string; no_jogo: boolean }[]
  no_jogo: { nome: string; temporada: number }[]
  tem_historia: boolean
  clubes: { id: number; nome: string; divisao: string }[]
}

export interface TelaCarreira {
  cabecalho: Cabecalho
  titulo: string
  subtitulo: string
  tecnico: {
    nome: string
    reputacao: number
    rotulo: string
    /** a proxima faixa de reputacao; null no topo */
    proxima: { rotulo: string; falta: number; em: number } | null
  }
  totais: {
    clubes: number
    temporadas: number
    titulos: number
    j: number
    v: number
    e: number
    d: number
    gp: number
    gc: number
  }
  trofeus: { nome: string; qtd: number; anos: string[] }[]
  passagens: PassagemCarreira[]
  opcoes: { dificuldade: string; sem_demissao: boolean; investidor: boolean }
  propostas: PropostaEmprego[]
  pode_pedir_demissao: boolean
}

export interface AvisoContratos {
  ids: number[]
  jogadores: { id: number; nome: string; pos: string; ovr: number; vencido: boolean }[]
  extras: number
  estado: Estado
  texto: string
}

/** Decisao que trava o jogo: clube novo depois de demissao, ou fim de carreira. */
export interface Pendencia {
  tipo: 'novo_clube' | 'carreira_encerrada' | string
  titulo: string
  motivo?: string
  de?: string
  opcoes: {
    id: number
    nome: string
    divisao: string
    reputacao?: number
    caixa?: string
    elenco?: number
  }[]
  historico?: string[]
}

export interface ResumoTemporada {
  previa: boolean
  temporada: number
  titulo: string
  subtitulo: string
  /** o que foi ganho no ano: titulos e acesso, em destaque no topo */
  conquistas: { nome: string; tipo: 'titulo' | 'acesso' }[]
  /** so os campeonatos que o clube jogou, com onde parou em cada um */
  campanhas: { nome: string; resultado: string; estado: Estado; titulo: boolean }[]
  vereditos: { texto: string; estado: Estado }[]
  tiles: { nome: string; valor: string; sub: string; estado: Estado }[]
  secoes: { titulo: string; itens: { texto: string; estado: Estado }[] }[]
  nota: string
}

export interface Confirmacao {
  titulo: string
  texto: string
  destino: string
}

export interface OpcaoAvanco {
  id: 'jogo' | 'semana' | 'mes' | 'janela' | 'temporada'
  rotulo: string
  semanas: number
  nota: string
}

export type Paradas = Record<'lesao' | 'janela' | 'proposta' | 'quebrado' | 'emprego', boolean>

export interface LinhaRelato {
  texto: string
  estado: Estado
}

/** Um jogo do meu clube no relato do Simular (mandante primeiro) */
export interface JogoRelato {
  resultado: 'V' | 'E' | 'D'
  estado: Estado
  times: [string, string]
  placar: [number, number]
  eu: 0 | 1
  comp: string
  /** mata-mata que se decidiu nesta semana: classificado, eliminado, campeao... */
  decisao: LinhaRelato | null
}

export interface RelatoSemana {
  titulo: string
  jogos: JogoRelato[]
  avisos: LinhaRelato[]
}

export interface RespostaAvanco {
  encerrada?: boolean
  log?: string
  virou_o_ano?: boolean
  fim_do_estadual?: boolean
  painel?: DadosPainel
  pendencia?: Pendencia | null
  confirmar?: Confirmacao
  // avanco em ritmos
  semana?: RelatoSemana
  jogou?: boolean
  /** as partidas desta semana (dto.partida), para o resumo no fim do Simular */
  partidas?: Partida[]
  parar?: string
  opcoes?: OpcaoAvanco[]
  cabecalho?: Cabecalho
  /** veio na virada do ano: a tela abre o resumo antes de qualquer outra coisa */
  resumo?: ResumoTemporada
  /** modo caos: os plantoes da semana */
  plantao?: EventoCaos[]
}

export interface EventoCaos {
  id?: string
  titulo: string
  texto: string
  gravidade: 'leve' | 'grave' | 'tragedia'
  clube: string
  meu: boolean
  temporada: number
  semana: number
}

export interface ClubeOpcao {
  id: number
  nome: string
  divisao: string
  /** "Serie A", "Premier League"... */
  liga?: string
  reputacao: number
}

export type SituacaoJogo = 'pronto' | 'tem_save' | 'sem_save' | 'escolher_clube'

export interface RespostaEstado {
  jogo: SituacaoJogo
  cabecalho?: Cabecalho
  clubes?: ClubeOpcao[]
  pendencia?: Pendencia | null
  versao?: string
  config?: Config
  /** quem esta no save, para o menu dizer o que Continuar abre */
  save?: { tecnico: string; clube: string; temporada: number; semana: number } | null
  /** os tres slots de save, com o resumo de cada um */
  slots?: SlotSave[]
  slot?: number
}

/** O escudo de um clube (api/dto.py, escudo_de): so dado, o Escudo desenha. */
export interface DadosEscudo {
  nome: string
  sigla: string
  cor1: string
  cor2: string
  padrao: 'liso' | 'vertical' | 'horizontal' | 'diagonal' | 'metade'
  forma: number
}

export interface SlotSave {
  escudo?: DadosEscudo
  slot: number
  vazio: boolean
  tecnico?: string
  clube?: string
  divisao?: string
  temporada?: number
  semana?: number
  modo?: string
  titulos?: number
  salvo_em?: string
}

export type Dificuldade = 'facil' | 'normal' | 'dificil'

/** Preferencias fora do save (brasfut_config.json). */
export interface Config {
  escala: 90 | 100 | 110 | 125
  reduzir_animacoes: boolean
  /** padroes que a tela de carreira nova ja traz marcados */
  dificuldade: Dificuldade
  sem_demissao: boolean
  investidor: boolean
  modo: ModoCarreira
}

export interface OpcaoDificuldade {
  id: Dificuldade
  nome: string
  desc: string
}

/** O que vale pelo save inteiro, escolhido na carreira nova. */
export type ModoCarreira = 'classico' | 'caos'

export interface OpcoesCarreira {
  dificuldade: Dificuldade
  sem_demissao: boolean
  investidor: boolean
  modo: ModoCarreira
}

// ============================================================================
// Telas migradas depois do Painel.
//
// Todas carregam o mesmo `cabecalho`, porque o topo e o menu são os mesmos em
// qualquer tela — é o App que decide o que desenhar embaixo.
// ============================================================================

export interface Metrica {
  valor: string | number
  nome: string
  estado?: Estado | null
}

export interface Confirmar {
  titulo: string
  texto: string
  perigo?: boolean
}

/** Toda ação devolve o recado e a tela já recalculada, ou pede confirmação. */
export interface RespostaAcao<T> {
  recado?: string
  /** A acao pode ser desfeita: a tela oferece o botao por alguns segundos. */
  desfazer?: boolean
  tela?: T
  confirmar?: Confirmar
}

export interface JogadorElenco {
  /** lesao, suspensao, pendurado */
  jogo: string
  /** contrato e vitrine: sem contrato, a venda, emprestado */
  mercado: string
  id: number
  pos: string
  nome: string
  capitao: boolean
  idade: number
  ovr: number
  cond: number
  salario: string
  salario_num: number
  valor: string
  valor_num: number
  contrato: number
  ultimo_ano: boolean
  situacao: string
  listado: boolean
  emprestado_aqui: boolean
  estado: string
  tag: string
}

export interface Cedido {
  id: number
  nome: string
  pos: string
  ovr: number
  clube: string
  emp_pct: number
  custo: string
  opcao: string | null
  tag: string
}

export interface TelaElenco {
  cabecalho: Cabecalho
  titulo: string
  subtitulo: string
  mercado_aberto: boolean
  metricas: Metrica[]
  jogadores: JogadorElenco[]
  cedidos: Cedido[]
}

export interface Garoto {
  id: number
  pos: string
  nome: string
  idade: number
  ovr: number
  teto: string
  em_foco: boolean
  situacao: string
  estado: string
  tag: string
  /** meses que o clube ja observa o garoto: a faixa do teto estreita com isso */
  obs: number
}

export interface TelaBase {
  cabecalho: Cabecalho
  titulo: string
  subtitulo: string
  metricas: Metrica[]
  garotos: Garoto[]
  elenco_profissional: number
  teto_profissional: number
  peneira: {
    atual: { regiao: string; nome: string; foco: string | null; custo: string; proxima: number } | null
    regioes: { id: string; nome: string; custo: string; vies: string; talento: string }[]
    posicoes: string[]
    a_cada: number
    vale: number
  }
  candidatos: {
    cid: number
    nome: string
    pos: string
    idade: number
    ovr: number
    faixa: string
    regiao: string
    semanas: number
  }[]
  vagas_livres: number
  revelados: {
    nome: string
    pos: string
    temporada: number
    ovr_subida: number
    ovr_hoje: number | null
    onde: string
    em_casa: boolean
  }[]
}

export interface LinhaClassificacao {
  pos: number
  clube: string
  p: number
  j: number
  v: number
  e: number
  d: number
  gp: number
  gc: number
  sg: number
  eu: boolean
  zona: 'alta' | 'baixa' | 'media' | ''
  zona_texto?: string | null
  /** so no estadual com grupos: "Grupo A"... (a posicao conta dentro dele) */
  grupo?: string | null
}

export interface GrupoTabela {
  nome: string
  linhas: LinhaClassificacao[]
}

export interface TelaTabela {
  cabecalho: Cabecalho
  titulo: string
  subtitulo?: string
  torneios: { id: string; nome: string; grupo: string }[]
  alvo: string
  legenda: string | null
  vazio: string | null
  linhas: LinhaClassificacao[]
  grupos?: GrupoTabela[] | null
}

export interface CopaItem {
  id: string
  nome: string
  encerrada: boolean
  campeao: string | null
  fase: string | null
  clubes: number
  proxima: number | null
  vivo: boolean
}

export interface TelaCopas {
  cabecalho: Cabecalho
  titulo: string
  copas: CopaItem[]
}

export interface LinhaDinheiro {
  nome: string
  valor: string
  estado?: string
  /** uma frase: de onde vem esse dinheiro */
  dica?: string
  destaque?: boolean
}

export interface ContratoPatrocinio {
  empresa: string
  perfil: string
  semanal: string
  temporadas: string
  meta: string
  bonus: string | null
  ano: string
}

export interface Patrocinio {
  contratos: (ContratoPatrocinio & { espaco: string; nome: string })[]
  vagos: { espaco: string; nome: string; ofertas: (ContratoPatrocinio & { indice: number })[] }[]
  explica: string
}

export interface TelaFinancas {
  cabecalho: Cabecalho
  titulo: string
  /** credito do clube (emprestimo financeiro): o que esta aberto, ou o limite */
  credito: CreditoClube
  /** o ano ate agora, por categoria; a soma fecha com o caixa */
  extrato: {
    temporada: number
    entradas: LinhaDinheiro[]
    saidas: LinhaDinheiro[]
    caixa_ini: string
    caixa: string
    resultado: string
    estado: Estado
  }
  /** o que entra e sai toda semana, sem bilheteria nem premio */
  linhas: LinhaDinheiro[]
  premiacao: LinhaDinheiro[]
  patrocinio: Patrocinio
  mensal: VerbaMensal
  elenco: { valor: string; folha_mes: string; jogadores: number; emprestados: number }
  maiores: { id: number; nome: string; pos: string; salario: string; valor: string; obs: string }[]
}

export interface VerbaMensal {
  linhas: { nome: string; valor: string; estado: string; destaque?: boolean }[]
  caixa: string
  reserva: string
  meses: number
  verba: string
  estado: Estado
  explica: string
  queima: string | null
}

export interface ItemInfra {
  id: string
  nome: string
  descricao: string
  nivel: number
  maximo: number
  custo: string | null
  custo_num: number | null
  pode_pagar: boolean
}

export interface TelaInfra {
  cabecalho: Cabecalho
  titulo: string
  subtitulo: string
  itens: ItemInfra[]
}

export interface TelaNoticias {
  cabecalho: Cabecalho
  titulo: string
  subtitulo: string
  itens: { texto: string }[]
  mundo: Manchete[]
}

export interface FichaJogador {
  id: number
  nome: string
  /** usa a bracadeira no clube dele */
  capitao: boolean
  /** e do meu elenco e pode receber a bracadeira */
  pode_capitao: boolean
  pos: string
  posicao_nome: string
  idade: number
  clube: string
  ovr: number
  papel: string
  olheiro: string
  notas: string[]
  situacao: string
  barras: { nome: string; valor: number }[]
  temporada: { j: number; g: number; a: number; ca: number; cv: number }
  carreira: { j: number; g: number; tit: number }
  /** premios do ano que o jogador ganhou, do mais novo para o mais velho */
  premios: string[]
  /** as ultimas causas da moral, da mais nova para a mais velha */
  moral_causas: { texto: string; estado: string; quando: string }[]
  contrato: {
    anos: number
    salario: string
    valor: string
    emprestado_aqui: boolean
    emp_pct: number
  }
}

export interface JogadorBanco {
  id: number
  pos: string
  nome: string
  ovr: number
  cond: number
  situacao: string
  disponivel: boolean
  tag: string
}

export interface EixoPlano {
  id: string
  nome: string
  valor: string
  opcoes: { id: string; desc: string }[]
}

/** Quantos de cada vaga. GOL e sempre 1; os outros somam 10. */
export type Contagem = Record<'GOL' | 'ZAG' | 'LAT' | 'VOL' | 'MEI' | 'ATA', number>

export interface OpcaoFormacao {
  id: string
  rotulo: string
  contagem: Contagem
  sem_laterais: boolean
}

/** O elenco nao tem a posicao que a formacao pede: a saida ja calculada. */
export interface SaidaEstrutural {
  vaga: string
  plural: string
  alternativa: { formacao: string; ataque: number; defesa: number; sem_laterais: boolean } | null
  mercado: boolean
}

export interface PreviaEsquema {
  valida: boolean
  motivo: string
  rotulo?: string
  ataque?: number
  defesa?: number
  improvisados?: number
  graves?: number
  mantem_os_11?: boolean
  jogadores?: JogadorEmCampo[]
  vagas_abertas?: number
}

export interface TelaEscalacao {
  cabecalho: Cabecalho
  titulo: string
  subtitulo: string
  metricas: Metrica[]
  prontidao: { estado: Estado; titulo: string; detalhe: string; estrutural: SaidaEstrutural | null }
  auto: boolean
  formacao: string
  formacao_rotulo: string
  contagem: Contagem
  formacoes: { nome: string; itens: OpcaoFormacao[] }[]
  personalizada: { rotulo: string; contagem: Contagem } | null
  limites: Record<string, { min: number; max: number }>
  pode_desfazer: boolean
  /** O motor aceita vaga fixada? Sem isso, so titulares da mesma vaga trocam de lugar. */
  troca_entre_vagas: boolean
  nova_vaga: number[]
  tatica: string
  taticas: string[]
  plano: {
    eixos: EixoPlano[]
    padrao: boolean
    efeitos: { nome: string; valor: string }[]
  }
  condicionais: {
    minutos: number[]
    regras: RegraCondicional[]
  }
  titulares: JogadorEmCampo[]
  vagas_abertas: number
  banco: JogadorBanco[]
}

export interface RegraCondicional {
  condicao: 'perdendo' | 'vencendo'
  rotulo: string
  /** null = sem instrucao para essa condicao */
  minuto: number | null
  tatica: string | null
}

export interface Regime {
  nome: string
  desc: string
  ativo: boolean
  efeitos: { nome: string; texto: string; estado: Estado }[]
}

export interface JogadorTreino {
  id: number
  pos: string
  nome: string
  base: boolean
  idade: number
  ovr: number
  margem: number
  evo: string
  em_foco: boolean
  emprestado_aqui: boolean
  tag: string
}

export interface TelaTreino {
  cabecalho: Cabecalho
  titulo: string
  subtitulo: string
  metricas: Metrica[]
  regimes: Regime[]
  custo_por_nome: string
  vagas: number
  em_foco: number
  jogadores: JogadorTreino[]
}

export interface TelaEstadio {
  cabecalho: Cabecalho
  titulo: string
  subtitulo: string
  metricas: Metrica[]
  preco: number
  preco_min: number
  preco_max: number
  obra: { lugares: string; semanas: number } | null
  custo_lugar: number
  lugares_min: number
  lugares_max: number
  caixa: string
  caixa_num: number
  /** os jogos em casa do ano e o que pesa no preco e na obra */
  rendimento: LinhaDinheiro[]
}

// ============================================================================
// Mercado
// ============================================================================

export type AbaMercado = 'compra' | 'emprestimo' | 'livres' | 'vitrine'

export interface FiltrosMercado {
  pos: string | null
  ovr: number | null
  idade: number | null
  teto: number | null
  idade_min: number | null
  /** teto minimo, pelo que o olheiro enxerga */
  pot_min: number | null
  regiao: string | null
  so_venda: boolean
}

export interface LinhaMercado {
  id: number
  pos: string
  nome: string
  idade: number
  ovr: number
  teto: string
  clube: string
  salario: string
  livre: boolean
  /** ja acertado comigo, esperando a janela abrir */
  acertado: boolean
  tag: string
  // compra
  pedido?: string
  pedido_num?: number
  valor: string
  valor_num: number
  marca?: '' | 'a_venda' | 'intocavel'
  emprestimo?: boolean
  // emprestimo
  pct?: number
  fatia?: string
}

export interface LinhaVitrine {
  id: number
  nome: string
  pos: string
  ovr: number
  salario: string
  valor: string
  pede: string
  pct: number
  interessado: string | null
  oferta: string | null
  tag: string
}

export interface OfertaRecebida {
  chave: string
  id: number
  clube_id: number
  nome: string
  pos: string
  ovr: number
  clube: string
  divisao: string
  oferta: string
  oferta_num: number
  pede: string
  pede_num: number
  diferenca: string
  estado: Estado
  salario_num: number
  /** valor de mercado do jogador e quanto a oferta cobre dele */
  valor: string
  valor_num: number
  pct_valor: number
  /** contrapropostas que ainda cabem nesta oferta, nesta semana */
  contras: number
  contrato: number
}

export interface Financeiro {
  caixa: string
  reserva: string
  verba: string
  verba_num: number
  meses: number
  custos_mes: string
  saldo_mes: string
  saldo_mes_num: number
  estado: Estado
}

export interface ContratoAcabando {
  id: number
  nome: string
  pos: string
  ovr: number
  idade: number
  contrato: number
  tag: string
  salario: string
  pede: string
  valor: string
  estado: Estado
  quando: string
}

export interface Agendada {
  indice: number
  jogador: string
  tipo: string
  com: string
  valor: string
  quando: string
}

export interface TelaMercado {
  cabecalho: Cabecalho
  titulo: string
  subtitulo: string
  aberto: boolean
  metricas: Metrica[]
  abas: { id: AbaMercado; nome: string; contador: number | null }[]
  aba: AbaMercado
  filtros: FiltrosMercado
  regioes: { id: string; nome: string }[]
  posicoes: string[]
  caixa_num: number
  jogadores: LinhaMercado[]
  vitrine: LinhaVitrine[]
  ofertas: OfertaRecebida[]
  agendadas: Agendada[]
  financeiro: Financeiro
  contratos: ContratoAcabando[]
}

export type TipoMesa = 'compra' | 'emprestimo' | 'renovacao'

export interface Leitura {
  texto: string
  estado: Estado
  pct: number | null
}

export interface Atalho {
  rotulo: string
  valor: number
}

/** A proposta que esta na tela, do jeito que vai para o servidor. */
export interface PropostaMesa {
  anos?: number
  valor?: number
  salario?: number
  pct?: number
  opcao?: number
}

export interface Mesa {
  tipo: TipoMesa
  id: number
  nome: string
  descricao: string
  clube: string
  janela: string
  aberto: boolean
  caixa: string
  caixa_num: number
  /** verba de contratacao: o caixa menos a reserva de folha e custos */
  verba: string
  verba_num: number
  reserva: string
  reserva_meses: number
  salario_atual: string
  anos: number
  rodada: number
  tentativas: number
  encerrada: boolean
  falas: string[]
  fechada_com: string | null
  contexto: string
  // compra e renovacao
  exigencia?: string
  exigencia_num?: number
  salario?: number
  leitura_salario?: Leitura
  folha_depois?: string
  atalhos_salario?: Atalho[]
  // compra
  livre?: boolean
  intocavel?: boolean
  pedido?: string
  pedido_num?: number
  valor?: number
  leitura_passe?: Leitura | null
  caixa_depois?: string
  verba_com_salario?: string
  falta_caixa?: boolean
  atalhos_passe?: Atalho[]
  // emprestimo
  exigencia_pct?: number
  pct?: number
  opcao?: number
  piso?: string
  taxa?: string | null
  taxa_num?: number
  leitura_pct?: Leitura
  divisao?: string
  leitura_opcao?: Leitura
  atalhos_opcao?: Atalho[]
  // renovacao
  acabando?: boolean
}

export interface LinhaRenovacao {
  id: number
  nome: string
  pos: string
  ovr: number
  idade: number
  contrato: number
  tag: string
  salario: string
  pede: string
  /** "+R$ 120 mil" ou "-R$ 20 mil" em relacao ao salario de hoje */
  diferenca: string
  /** por que nao da para renovar (emprestado, de outro clube); null = pode */
  motivo: string | null
}

export interface PreviaRenovacao {
  anos: number
  linhas: LinhaRenovacao[]
  folha_mes: string
  folha_mes_depois: string
  diferenca_mes: string
}

export interface LinhaPrecoVitrine {
  id: number
  nome: string
  pos: string
  ovr: number
  contrato: number
  salario: string
  salario_num: number
  valor: string
  valor_num: number
  preco: number
  tag: string
}

export interface LinhaCessao {
  chave: string
  id: number
  clube_id: number
  nome: string
  ovr: number
  salario: string
  clube: string
  divisao: string
  reputacao: number
  pct: number
  sobra: string
  alivio_num: number
  tag: string
}

/** De onde veio a acao em lote: a resposta traz a tela de quem pediu. */
export type Origem = { tela: 'elenco' } | { tela: 'mercado'; aba: AbaMercado; filtros?: FiltrosMercado }

// ============================================================================
// Competicoes
// ============================================================================

export interface ItemCompeticao {
  id: string
  nome: string
  tipo: 'pontos' | 'mata-mata'
  meu: boolean
  estado: string
  vivo: boolean
  /** regiao no seletor: Brasil, Estaduais, America do Sul, Europa, Mundial... */
  grupo: string
}

export interface JogoRodada {
  casa: string
  fora: string
  gc: number | null
  gf: number | null
  meu: boolean
  resultado: 'V' | 'E' | 'D' | null
}

export interface Rodada {
  numero: number
  jogada: boolean
  registrada: boolean
  jogos: JogoRodada[]
}

export interface DetalhePontos {
  tipo: 'pontos'
  titulo: string
  id: string
  legenda: string | null
  linhas: LinhaClassificacao[]
  vazio: string | null
  rodadas: Rodada[]
  rodada_atual: number
  jogadas: number
  meus_jogos: (JogoRodada & { rodada: number })[]
  aviso: string | null
  /** so nos estaduais: nome da primeira fase, grupos e o mata-mata */
  fase1?: string
  grupos?: GrupoTabela[] | null
  mata?: FaseCopa[] | null
  situacao?: { estado: Estado; texto: string } | null
}

export interface JogoCopa {
  a: string
  b: string
  ida: [number, number] | null
  volta: [number, number] | null
  agregado: [number, number] | null
  penaltis: string | null
  vencedor: string | null
  venceu_a: boolean | null
  meu: boolean
  passei: boolean | null
}

export interface FaseCopa {
  nome: string
  /** null na Supercopa e na Recopa, que caem numa rodada do estadual (vem na nota) */
  semana: number | null
  estado: 'jogada' | 'sorteada' | 'futura'
  /** troca o rotulo padrao da fase (estadual: "ida", "a definir"...) */
  nota?: string | null
  jogos: JogoCopa[]
}

export interface DetalheCopa {
  tipo: 'mata-mata'
  titulo: string
  id: string
  campeao: string | null
  situacao: { estado: Estado; texto: string } | null
  fases: FaseCopa[]
  aviso: string | null
  /** Libertadores e Sul-Americana: a fase de grupos, o meu grupo primeiro */
  grupos?: GrupoCopa[] | null
  em_grupos?: boolean
  titulo_grupos?: string
  nota_grupos?: string | null
}

export interface GrupoCopa {
  nome: string
  meu: boolean
  linhas: LinhaClassificacao[]
  jogos: {
    rodada: number
    semana: number
    casa: string
    fora: string
    gc: number | null
    gf: number | null
    meu: boolean
    resultado: 'V' | 'E' | 'D' | null
  }[]
}

export interface TelaCompeticoes {
  cabecalho: Cabecalho
  titulo: string
  subtitulo: string
  lista: ItemCompeticao[]
  alvo: string
  detalhe: DetalhePontos | DetalheCopa
}

/** Um item de texto da ajuda: o nome de uma tela ou de um termo e a explicacao. */
export interface ItemAjuda {
  nome: string
  texto: string
}

/** GET /api/ajuda: o que cada tela faz e o que os termos querem dizer. */
export interface Ajuda {
  telas: ItemAjuda[]
  termos: ItemAjuda[]
}

/** A apresentacao da carreira nova (dto.boas_vindas). */
export interface BoasVindas {
  clube: string
  linha: string
  objetivo: string
  aviso: string
  passos: ItemAjuda[]
  sem_pressa: string
}

/** Faixa do Painel: alguem quer comprar um dos seus jogadores. */
export interface AvisoPropostas {
  total: number
  itens: { jogador: string; pos: string; clube: string; valor: string }[]
  texto: string
}

export interface CreditoClube {
  ativo: {
    valor: string
    saldo: string
    parcela: string
    restantes: number
    meses: number
    atrasos: number
    quitar: string
  } | null
  limite: string | null
  limite_num: number
  minimo_num?: number
  juros: string
  prazos: { meses: number; parcela_do_limite: string }[]
}
