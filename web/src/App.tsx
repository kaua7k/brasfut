// A casca do jogo: menu, topo e a tela da vez.
//
// O estado do mundo mora no Python. Aqui so se guarda o retrato mais recente
// dele - toda acao devolve a tela ja recalculada pelo servidor, entao a tela
// nunca tenta adivinhar sozinha o que mudou. Foi assim que a janela tkinter
// manteve cinco pontos da interface dando o mesmo veredito.

import { porque, AGUARDE } from './motivo'
import { useCallback, useEffect, useRef, useState } from 'react'
import { api, ErroDaApi } from './api'
import { MODO_NAVEGADOR } from './modo'
import { BarraTopo } from './componentes/BarraTopo'
import { DialogoAvanco } from './componentes/DialogoAvanco'
import { DialogoCeder } from './componentes/DialogoCeder'
import { DialogoVitrine } from './componentes/DialogoVitrine'
import { DialogoRenovar } from './componentes/DialogoRenovar'
import { Ficha } from './componentes/Ficha'
import { JanelaPendencia } from './componentes/JanelaPendencia'
import { Mesa } from './componentes/Mesa'
import { Resumo } from './componentes/Resumo'
import { Ajuda, BoasVindas } from './componentes/Ajuda'
import { MenuLateral } from './componentes/MenuLateral'
import { Abertura } from './telas/Abertura'
import { Base, type AcaoBase } from './telas/Base'
import { Classificacao } from './telas/Classificacao'
import { Competicoes } from './telas/Competicoes'
import { Elenco, type AcaoElenco } from './telas/Elenco'
import { Escalacao, type AcaoEscalacao } from './telas/Escalacao'
import { Estadio, type AcaoEstadio } from './telas/Estadio'
import { Financas } from './telas/Financas'
import { Infra } from './telas/Infra'
import { Mercado, type AcaoMercado } from './telas/Mercado'
import { Noticias } from './telas/Noticias'
import { Carreira } from './telas/Carreira'
import { Clube } from './telas/Clube'
import { Estatisticas } from './telas/Estatisticas'
import { Plantao } from './componentes/Plantao'
import { guardarEscudos } from './componentes/Escudo'
import { Painel } from './telas/Painel'
import { Treino, type AcaoTreino } from './telas/Treino'
import type {
  AbaMercado,
  Ajuda as DadosAjuda,
  BoasVindas as DadosBoasVindas,
  Cabecalho,
  ClubeOpcao,
  Config,
  OpcoesCarreira,
  SlotSave,
  EventoCaos,
  Confirmar,
  DadosPainel,
  FichaJogador,
  Origem,
  Pendencia,
  RespostaAcao,
  ResumoTemporada,
  SituacaoJogo,
  TelaBase,
  TelaCarreira,
  TelaClube,
  TelaEstatisticas,
  TelaCompeticoes,
  TelaElenco,
  TelaEscalacao,
  TelaEstadio,
  TelaFinancas,
  TelaInfra,
  TelaMercado,
  TelaNoticias,
  TelaTabela,
  TelaTreino,
  TipoMesa,
} from './tipos'

/** O conteudo da area principal. Cada tela traz o seu proprio cabecalho. */
type Conteudo =
  | { tipo: 'painel'; dados: DadosPainel }
  | { tipo: 'elenco'; dados: TelaElenco }
  | { tipo: 'base'; dados: TelaBase }
  | { tipo: 'tabela'; dados: TelaTabela }
  | { tipo: 'copas'; dados: TelaCompeticoes }
  | { tipo: 'financas'; dados: TelaFinancas }
  | { tipo: 'infra'; dados: TelaInfra }
  | { tipo: 'noticias'; dados: TelaNoticias }
  | { tipo: 'carreira'; dados: TelaCarreira }
  | { tipo: 'clube'; dados: TelaClube }
  | { tipo: 'estatisticas'; dados: TelaEstatisticas }
  | { tipo: 'escalacao'; dados: TelaEscalacao }
  | { tipo: 'treino'; dados: TelaTreino }
  | { tipo: 'estadio'; dados: TelaEstadio }
  | { tipo: 'mercado'; dados: TelaMercado }

/** Confirmacao pendente: o texto que o servidor mandou e o que fazer no sim. */
interface Pergunta {
  confirmar: Confirmar
  aoConfirmar: () => Promise<void>
  /** Tela onde se conserta o problema, quando existe uma. */
  destino?: string
}

export function App() {
  const [situacao, setSituacao] = useState<SituacaoJogo | null>(null)
  const [clubes, setClubes] = useState<ClubeOpcao[]>([])
  const [versao, setVersao] = useState('')
  const [slots, setSlots] = useState<SlotSave[]>([])
  const [plantao, setPlantao] = useState<EventoCaos[]>([])
  const [config, setConfig] = useState<Config | null>(null)
  // modo navegador: a primeira abertura espera o Python subir no aparelho
  const [etapaMotor, setEtapaMotor] = useState('')
  // celular: o menu lateral vira gaveta, aberta pelo botao do topo
  const [menuAberto, setMenuAberto] = useState(false)
  const fecharMenu = useCallback(() => setMenuAberto(false), [])

  useEffect(() => {
    if (!MODO_NAVEGADOR) return
    let parar = () => {}
    import('./motor/cliente').then((m) => {
      parar = m.aoProgresso(setEtapaMotor)
    })
    return () => parar()
  }, [])

  // escala e animacoes valem para o jogo inteiro, nao so para o menu
  useEffect(() => {
    if (!config) return
    document.documentElement.style.setProperty('zoom', `${config.escala}%`)
    document.documentElement.classList.toggle('sem-animacao', config.reduzir_animacoes)
  }, [config])
  const [conteudo, setConteudo] = useState<Conteudo | null>(null)
  const [erro, setErro] = useState<string | null>(null)
  const [recado, setRecado] = useState<string | null>(null)
  const [ocupado, setOcupado] = useState(false)
  const [mudandoAuto, setMudandoAuto] = useState(false)
  const [salvando, setSalvando] = useState(false)
  const [pergunta, setPergunta] = useState<Pergunta | null>(null)
  const [pendencia, setPendencia] = useState<Pendencia | null>(null)
  const [ficha, setFicha] = useState<FichaJogador | null>(null)
  // dialogos do mercado: mesa de negociacao, vitrine e renovacao em lote, cessao.
  const [mesa, setMesa] = useState<{ tipo: TipoMesa; id: number } | null>(null)
  const [dialogoVitrine, setDialogoVitrine] = useState<number[] | null>(null)
  const [dialogoRenovar, setDialogoRenovar] = useState<number[] | null>(null)
  const [dialogoCeder, setDialogoCeder] = useState<number[] | null>(null)
  const [simulando, setSimulando] = useState(false)
  // o resumo do ano: abre sozinho na virada e pelo Painel na pre-temporada.
  // Enquanto ele esta aberto a janela de demissao espera - o resumo explica
  // a demissao, entao vem antes dela
  const [resumo, setResumo] = useState<ResumoTemporada | null>(null)
  // ajuda pelo menu; boas-vindas so na carreira nova, logo depois de escolher o clube
  const [ajuda, setAjuda] = useState<DadosAjuda | null>(null)
  const [boasVindas, setBoasVindas] = useState<DadosBoasVindas | null>(null)
  // o Desfazer oferecido junto do recado: vale alguns segundos e some
  const [desfazer, setDesfazer] = useState<(() => void) | null>(null)

  useEffect(() => {
    if (!desfazer) return
    const t = window.setTimeout(() => setDesfazer(null), 8000)
    return () => window.clearTimeout(t)
  }, [desfazer])

  const comErro = useCallback(async (acao: () => Promise<void>) => {
    setErro(null)
    try {
      await acao()
    } catch (e) {
      setErro(e instanceof ErroDaApi ? e.message : String(e))
    }
  }, [])

  /** Busca uma tela pelo id do menu e a coloca na area principal. */
  const irPara = useCallback(
    (id: string, alvo?: string) =>
      comErro(async () => {
        setOcupado(true)
        setRecado(null)
        try {
          switch (id) {
            case 'painel':
              setConteudo({ tipo: 'painel', dados: (await api.painel()).painel })
              break
            case 'elenco':
              setConteudo({ tipo: 'elenco', dados: (await api.elenco()).tela })
              break
            case 'base':
              setConteudo({ tipo: 'base', dados: (await api.base()).tela })
              break
            case 'tabela':
              setConteudo({ tipo: 'tabela', dados: (await api.tabela(alvo)).tela })
              break
            case 'copas':
              // o item do menu continua 'copas' (hash antigo segue valendo), mas
              // a tela agora e Competicoes: estaduais, series e copas juntos
              setConteudo({ tipo: 'copas', dados: (await api.competicoes(alvo)).tela })
              break
            case 'financas':
              setConteudo({ tipo: 'financas', dados: (await api.financas()).tela })
              break
            case 'infra':
              setConteudo({ tipo: 'infra', dados: (await api.infra()).tela })
              break
            case 'noticias':
              setConteudo({ tipo: 'noticias', dados: (await api.noticias()).tela })
              break
            case 'estatisticas':
              setConteudo({ tipo: 'estatisticas', dados: (await api.estatisticas(alvo)).tela })
              break
            case 'clube':
              setConteudo({ tipo: 'clube', dados: (await api.clube(alvo ? Number(alvo) : undefined)).tela })
              break
            case 'carreira':
              setConteudo({ tipo: 'carreira', dados: (await api.carreira()).tela })
              break
            case 'escalacao':
              setConteudo({ tipo: 'escalacao', dados: (await api.escalacao()).tela })
              break
            case 'treino':
              setConteudo({ tipo: 'treino', dados: (await api.treino()).tela })
              break
            case 'estadio':
              setConteudo({ tipo: 'estadio', dados: (await api.estadio()).tela })
              break
            case 'mercado':
              setConteudo({ tipo: 'mercado', dados: (await api.mercado((alvo as AbaMercado) || 'compra')).tela })
              break
            default:
              // tela ainda nao migrada: o menu ja impede o clique, isto e a rede
              setRecado('Essa tela ainda nao migrou. Use o jogo na janela antiga.')
          }
          setSituacao('pronto')
          if (window.location.hash.slice(1) !== id) window.location.hash = id
        } finally {
          setOcupado(false)
        }
      }),
    [comErro],
  )

  // os escudos do mundo aberto: uma leitura por mundo, qualquer tela desenha pelo nome
  useEffect(() => {
    if (situacao === 'pronto' || situacao === 'escolher_clube')
      api.escudos().then((r) => guardarEscudos(r.escudos)).catch(() => {})
  }, [situacao])

  useEffect(() => {
    comErro(async () => {
      const r = await api.estado()
      setSituacao(r.jogo)
      setVersao(r.versao ?? '')
      setSlots(r.slots ?? [])
      if (r.config) setConfig(r.config)
      // a pendencia (demissao) vai no save: reabrir o jogo tem que mostra-la
      if (r.pendencia) setPendencia(r.pendencia)
      // o hash manda na primeira tela: F5 nao joga o usuario de volta no Painel
      const inicial = window.location.hash.slice(1) || 'painel'
      if (r.jogo === 'pronto') await irPara(inicial)
    })
  }, [comErro, irPara])

  // Voltar/Avancar do navegador e hash digitado a mao trocam de tela. O ref
  // evita recarregar a tela que o proprio irPara acabou de marcar no hash.
  const telaAtual = useRef<string | null>(null)
  useEffect(() => {
    telaAtual.current = conteudo?.tipo ?? null
  }, [conteudo])
  useEffect(() => {
    const aoMudarHash = () => {
      const id = window.location.hash.slice(1)
      if (id && id !== telaAtual.current && situacao === 'pronto') irPara(id)
    }
    window.addEventListener('hashchange', aoMudarHash)
    return () => window.removeEventListener('hashchange', aoMudarHash)
  }, [irPara, situacao])

  // ------------------------------------------------------------------ abertura
  const abrir = (slot: number) =>
    comErro(async () => {
      setOcupado(true)
      try {
        const r = await api.abrir(slot)
        if (r.pendencia) setPendencia(r.pendencia)
      } finally {
        setOcupado(false)
      }
      await irPara('painel')
    })

  const apagarSlot = (slot: number) =>
    comErro(async () => {
      setSlots((await api.apagarSlot(slot)).slots)
    })

  // salva e fecha a carreira: o menu principal volta com os slots
  const voltarAoMenu = () =>
    comErro(async () => {
      setOcupado(true)
      try {
        const r = await api.menu()
        setSlots(r.slots ?? [])
        setConteudo(null)
        setPendencia(null)
        setSituacao(r.jogo)
        window.location.hash = ''
      } finally {
        setOcupado(false)
      }
    })

  const criar = (nome: string, opcoes: OpcoesCarreira, slot: number) =>
    comErro(async () => {
      setOcupado(true)
      try {
        const r = await api.novo(nome, opcoes, slot)
        setClubes(r.clubes ?? [])
        setSituacao('escolher_clube')
      } finally {
        setOcupado(false)
      }
    })

  // ----------------------------------------------------------------- carreira
  const pedirDemissao = () =>
    comErro(async () => {
      setOcupado(true)
      try {
        const r = await api.pedirDemissao()
        setPendencia(r.pendencia)
      } finally {
        setOcupado(false)
      }
    })

  const responderProposta = (id: number, aceitar: boolean) =>
    comErro(async () => {
      setOcupado(true)
      try {
        const r = await api.responderProposta(id, aceitar)
        setRecado(r.recado)
        setConteudo({ tipo: 'painel', dados: r.painel })
        if (window.location.hash.slice(1) !== 'painel') window.location.hash = 'painel'
      } finally {
        setOcupado(false)
      }
    })

  const gravarConfig = (mudanca: Partial<Config>) =>
    comErro(async () => {
      setConfig((await api.gravarConfig(mudanca)).config)
    })

  const escolherClube = (id: number) =>
    comErro(async () => {
      setOcupado(true)
      try {
        await api.escolherClube(id)
      } finally {
        setOcupado(false)
      }
      await irPara('painel')
      const r = await api.ajuda()
      setBoasVindas(r.boas_vindas)
    })

  const abrirAjuda = () =>
    comErro(async () => {
      setAjuda((await api.ajuda()).ajuda)
    })

  // --------------------------------------------------------------------- acoes
  const avancar = (confirmar = false) =>
    comErro(async () => {
      setOcupado(true)
      setRecado(null)
      try {
        const r = await api.avancar(confirmar)
        if (r.confirmar) {
          // time quebrado: a decisao de entrar em campo assim e do usuario, e
          // ele precisa ver o estrago antes de tomar
          setPergunta({
            confirmar: { titulo: r.confirmar.titulo, texto: r.confirmar.texto, perigo: true },
            aoConfirmar: () => avancar(true),
            destino: r.confirmar.destino,
          })
          return
        }
        setPergunta(null)
        if (r.plantao?.length) setPlantao(r.plantao)
        if (r.painel) setConteudo({ tipo: 'painel', dados: r.painel })
        if (r.resumo) setResumo(r.resumo)
        if (r.pendencia) setPendencia(r.pendencia)
        if (r.encerrada) setRecado('Carreira encerrada.')
        else if (r.resumo) setRecado(`Ano novo: pre-temporada ${r.resumo.temporada + 1}, mercado aberto.`)
        else if (r.painel?.cabecalho.fase === 'encerrada')
          setRecado(`A temporada acabou. ${r.painel.cabecalho.acao} vira o ano e mostra o resumo.`)
        else if (r.fim_do_estadual) setRecado('O estadual acabou. Comeca a Serie A.')
        else setRecado('Semana processada e salva.')
      } finally {
        setOcupado(false)
      }
    })

  /**
   * Executa uma ação de tela. Se o servidor pedir confirmação, guarda a
   * pergunta e repete a mesma chamada com `confirmar` no sim — assim a conta
   * mostrada e a conta cobrada são sempre a mesma.
   */
  function despachar<T>(
    chamar: (confirmar: boolean) => Promise<RespostaAcao<T>>,
    aplicar: (dados: T) => void,
    aoDesfazer?: () => void,
  ) {
    const executar = (confirmar: boolean) =>
      comErro(async () => {
        setOcupado(true)
        setRecado(null)
        setDesfazer(null)
        try {
          const r = await chamar(confirmar)
          if (r.confirmar) {
            setPergunta({ confirmar: r.confirmar, aoConfirmar: () => executar(true) })
            return
          }
          setPergunta(null)
          if (r.tela) aplicar(r.tela)
          if (r.recado) setRecado(r.recado)
          if (r.desfazer && aoDesfazer) setDesfazer(() => aoDesfazer)
        } finally {
          setOcupado(false)
        }
      })
    return executar(false)
  }

  const agirElenco = (acao: AcaoElenco, ids: number[]) => {
    if (acao === 'vender') return setDialogoVitrine(ids)
    if (acao === 'ceder') return setDialogoCeder(ids)
    if (acao === 'renovar') {
      // um jogador: a mesa, para negociar; varios: a renovacao em lote
      if (ids.length > 1) return setDialogoRenovar(ids)
      return setMesa({ tipo: 'renovacao', id: ids[0] })
    }
    const rota = {
      tirar: api.tirarDaVitrine,
      rescindir: api.rescindir,
      opcao: api.exercerOpcao,
      chamar: api.chamarDeVolta,
    }[acao]
    despachar<TelaElenco>(
      (c) => rota(ids, c),
      (dados) => setConteudo({ tipo: 'elenco', dados }),
    )
  }

  const agirBase = (acao: AcaoBase, ids: number[]) => {
    const rota = acao === 'subir' ? api.subirDaBase : api.liberarDaBase
    despachar<TelaBase>(
      (c) => rota(ids, c),
      (dados) => setConteudo({ tipo: 'base', dados }),
    )
  }

  const investir = (id: string) =>
    despachar<TelaInfra>(
      (c) => api.investir(id, c),
      (dados) => setConteudo({ tipo: 'infra', dados }),
    )

  const agirEscalacao = (acao: AcaoEscalacao) => {
    const aplicar = (dados: TelaEscalacao) => setConteudo({ tipo: 'escalacao', dados })
    if (acao.tipo === 'auto') {
      comErro(async () => {
        setMudandoAuto(true)
        setRecado(null)
        try {
          const r = await api.definirAutoNaEscalacao(acao.ligada)
          aplicar(r.tela)
          if (r.mudou) {
            setRecado(acao.ligada
              ? 'Escalacao automatica ligada - o XI foi remontado.'
              : 'Escalacao manual ligada - voce responde pelo XI.')
          }
        } finally {
          setMudandoAuto(false)
        }
      })
      return
    }
    const chamar = () => {
      switch (acao.tipo) {
        case 'esquema':
          return api.mudarEsquema({
            formacao: acao.formacao,
            tatica: acao.tatica,
            contagem: acao.contagem,
          })
        case 'trocar':
          return api.trocarTitular(acao.titular, acao.reserva)
        case 'inverter':
          return api.inverterTitulares(acao.a, acao.b)
        case 'plano':
          return api.mudarPlano(acao.eixo, acao.valor)
        case 'plano-padrao':
          return api.planoPadrao()
        case 'condicional':
          return api.mudarCondicional(acao.condicao, acao.minuto, acao.tatica)
        case 'montar':
          return api.montarMelhor()
        case 'capitao':
          return api.capitaoNaEscalacao(acao.id)
      }
    }
    despachar<TelaEscalacao>(chamar, aplicar, () =>
      despachar<TelaEscalacao>(() => api.desfazerEsquema(), aplicar),
    )
  }

  const agirTreino = (acao: AcaoTreino) => {
    const aplicar = (dados: TelaTreino) => setConteudo({ tipo: 'treino', dados })
    if (acao.tipo === 'regime') despachar<TelaTreino>(() => api.escolherRegime(acao.nome), aplicar)
    else if (acao.tipo === 'foco') despachar<TelaTreino>(() => api.alternarFoco(acao.ids), aplicar)
    else despachar<TelaTreino>(() => api.limparFoco(), aplicar)
  }

  const peneiraNaBase = (regiao: string | null, foco: string | null) =>
    despachar<TelaBase>(
      () => api.peneira(regiao, foco),
      (dados) => setConteudo({ tipo: 'base', dados }),
    )

  const candidatoNaBase = (cid: number, aceitar: boolean) =>
    despachar<TelaBase>(
      () => api.candidato(cid, aceitar),
      (dados) => setConteudo({ tipo: 'base', dados }),
    )

  const focoNaBase = (ids: number[]) =>
    despachar<TelaBase>(
      () => api.alternarFocoNaBase(ids),
      (dados) => setConteudo({ tipo: 'base', dados }),
    )

  const agirEstadio = (acao: AcaoEstadio) => {
    const aplicar = (dados: TelaEstadio) => setConteudo({ tipo: 'estadio', dados })
    if (acao.tipo === 'preco') despachar<TelaEstadio>(() => api.mudarPreco(acao.preco), aplicar)
    else despachar<TelaEstadio>((c) => api.contratarObra(acao.lugares, c), aplicar)
  }

  /** De onde veio a acao em lote do mercado, para a resposta trazer a mesma tela. */
  const origem = (): Origem =>
    conteudo?.tipo === 'mercado'
      ? { tela: 'mercado', aba: conteudo.dados.aba, filtros: conteudo.dados.filtros }
      : { tela: 'elenco' }

  /** Aplica a tela que voltou de uma acao do mercado: Elenco ou Mercado. */
  const aplicarVolta = (dados: unknown) => {
    const d = dados as TelaElenco | TelaMercado
    if ('aba' in d) setConteudo({ tipo: 'mercado', dados: d })
    else setConteudo({ tipo: 'elenco', dados: d })
  }

  const recarregarAtual = async () => {
    if (conteudo?.tipo === 'mercado') {
      return comErro(async () => {
        const r = await api.mercado(conteudo.dados.aba, conteudo.dados.filtros)
        setConteudo({ tipo: 'mercado', dados: r.tela })
      })
    }
    if (conteudo) await irPara(conteudo.tipo)
  }

  const agirMercado = (acao: AcaoMercado) => {
    const aplicar = (dados: TelaMercado) => setConteudo({ tipo: 'mercado', dados })
    switch (acao.tipo) {
      case 'buscar':
        return comErro(async () => {
          setOcupado(true)
          try {
            aplicar((await api.mercado(acao.aba, acao.filtros)).tela)
          } finally {
            setOcupado(false)
          }
        })
      case 'negociar':
        return setMesa({ tipo: acao.mesa, id: acao.id })
      case 'reprecificar':
        return setDialogoVitrine(acao.ids)
      case 'tirar':
        return despachar<unknown>(() => api.tirarDaVitrineMercado(acao.ids, origem()), aplicarVolta)
      case 'aceitar':
        return despachar<TelaMercado>((c) => api.aceitarPropostas(acao.itens, c), aplicar)
      case 'recusar':
        return despachar<TelaMercado>(() => api.recusarPropostas(acao.itens), aplicar)
      case 'contra':
        return despachar<TelaMercado>(() => api.contraproposta(acao.id, acao.clube_id, acao.valor), aplicar)
      case 'renovar':
        // o mesmo caminho do Elenco: varios vao para a renovacao em lote
        return agirElenco('renovar', acao.ids)
      case 'cancelar':
        return despachar<unknown>((c) => api.cancelarAgendadas(acao.indices, origem(), c), aplicarVolta)
      case 'observar':
        return comErro(async () => {
          setOcupado(true)
          try {
            const r = await api.observar(acao.id, acao.observar)
            if (conteudo?.tipo === 'mercado') {
              aplicar((await api.mercado(conteudo.dados.aba, conteudo.dados.filtros)).tela)
            }
            setRecado(r.recado)
          } finally {
            setOcupado(false)
          }
        })
    }
  }

  const fecharMesa = async (fechou: boolean, texto: string | null) => {
    setMesa(null)
    // o negocio mexeu em caixa, elenco e folha - e uma renovacao rompida mexe
    // na moral: a tela de tras se refaz. O recado vem depois, senao a recarga
    // (que limpa o recado da tela anterior) apagaria a noticia do negocio
    if (fechou || conteudo?.tipo === 'elenco') await recarregarAtual()
    if (texto) setRecado(texto)
  }

  const definirAuto = (ligada: boolean) =>
    comErro(async () => {
      setMudandoAuto(true)
      try {
        const r = await api.definirAuto(ligada)
        setConteudo({ tipo: 'painel', dados: r.painel })
        if (r.mudou) {
          setRecado(ligada
            ? 'Escalacao automatica ligada - o XI foi remontado.'
            : 'Escalacao manual ligada - voce responde pelo XI.')
        }
      } finally {
        setMudandoAuto(false)
      }
    })

  const salvar = () =>
    comErro(async () => {
      setSalvando(true)
      try {
        await api.salvar()
        setRecado('Jogo salvo.')
      } finally {
        setSalvando(false)
      }
    })

  const abrirFicha = (id: number) =>
    comErro(async () => {
      setFicha((await api.ficha(id)).ficha)
    })

  const observarDaFicha = (id: number, observar: boolean) =>
    comErro(async () => {
      const r = await api.observar(id, observar)
      setFicha(r.ficha)
      setRecado(r.recado)
      if (conteudo?.tipo === 'mercado') {
        setConteudo({ tipo: 'mercado', dados: (await api.mercado(conteudo.dados.aba, conteudo.dados.filtros)).tela })
      }
    })

  const tornarCapitao = (id: number) =>
    comErro(async () => {
      const r = await api.capitao(id)
      setFicha(r.ficha)
      setRecado(r.recado)
      if (conteudo?.tipo === 'elenco') irPara('elenco')
    })

  // --------------------------------------------------------------------- telas
  if (situacao === null) {
    return (
      <div className="centro-tela">
        <span className="carregando" role="status">
          {etapaMotor ? `abrindo o jogo: ${etapaMotor}…` : 'abrindo o jogo…'}
        </span>
        {MODO_NAVEGADOR && erro && <span className="erro">{erro}</span>}
      </div>
    )
  }

  if (situacao !== 'pronto' || !conteudo) {
    return (
      <Abertura
        situacao={situacao}
        clubes={clubes}
        versao={versao}
        slots={slots}
        config={config}
        erro={erro}
        ocupado={ocupado}
        aoAbrir={abrir}
        aoCriar={criar}
        aoApagar={apagarSlot}
        aoEscolher={escolherClube}
        aoConfig={gravarConfig}
      />
    )
  }

  const cabecalho: Cabecalho = conteudo.dados.cabecalho

  return (
    <div className="app">
      <MenuLateral
        clube={cabecalho.clube}
        itens={cabecalho.menu}
        atual={conteudo.tipo}
        aoTrocar={(id) => irPara(id)}
        aoSalvar={salvar}
        aoMenu={voltarAoMenu}
        salvando={salvando}
        aoAjuda={abrirAjuda}
        aberto={menuAberto}
        aoFechar={fecharMenu}
      />

      <div className="conteudo">
        <BarraTopo
          cabecalho={cabecalho}
          aoAvancar={() => avancar(false)}
          aoSimular={() => setSimulando(true)}
          avancando={ocupado}
          aoAbrirMenu={() => setMenuAberto(true)}
          menuAberto={menuAberto}
        />

        {(erro || recado) && (
          <div role="status" className={erro ? 'recado-app erro' : 'recado-app'}>
            {erro ?? recado}
            {!erro && desfazer && (
              <button type="button" className="bt-fantasma bt-mini bt-desfazer" onClick={desfazer}>
                Desfazer
              </button>
            )}
          </div>
        )}

        {conteudo.tipo === 'painel' && (
          <Painel
            dados={conteudo.dados}
            aoResponderProposta={responderProposta}
            aoDefinirAuto={definirAuto}
            mudandoAuto={mudandoAuto}
            aoIr={(destino) =>
              destino === 'resumo'
                ? comErro(async () => setResumo((await api.resumo()).resumo))
                : irPara(...(destino.split(':') as [string, string?]))
            }
            aoRenovar={(ids) => agirElenco('renovar', ids)}
          />
        )}
        {conteudo.tipo === 'elenco' && (
          <Elenco
            tela={conteudo.dados}
            ocupado={ocupado}
            aoAbrirFicha={abrirFicha}
            aoAgir={agirElenco}
          />
        )}
        {conteudo.tipo === 'base' && (
          <Base
            tela={conteudo.dados}
            ocupado={ocupado}
            aoAbrirFicha={abrirFicha}
            aoAgir={agirBase}
            aoAlternarFoco={focoNaBase}
            aoPeneira={peneiraNaBase}
            aoCandidato={candidatoNaBase}
          />
        )}
        {conteudo.tipo === 'tabela' && (
          <Classificacao
            tela={conteudo.dados}
            ocupado={ocupado}
            aoTrocarTorneio={(alvo) => irPara('tabela', alvo)}
          />
        )}
        {conteudo.tipo === 'copas' && (
          <Competicoes tela={conteudo.dados} ocupado={ocupado} aoTrocar={(alvo) => irPara('copas', alvo)} />
        )}
        {conteudo.tipo === 'financas' && (
          <Financas
            tela={conteudo.dados}
            ocupado={ocupado}
            aoAssinarPatrocinio={(espaco, indice) =>
              comErro(async () => {
                setOcupado(true)
                try {
                  const r = await api.assinarPatrocinio(espaco, indice)
                  setConteudo({ tipo: 'financas', dados: r.tela })
                  setRecado(r.recado)
                } finally {
                  setOcupado(false)
                }
              })
            }
            aoAssinarEquilibradas={() =>
              comErro(async () => {
                setOcupado(true)
                try {
                  const r = await api.assinarEquilibradas()
                  setConteudo({ tipo: 'financas', dados: r.tela })
                  setRecado(r.recado)
                } finally {
                  setOcupado(false)
                }
              })
            }
            aoMudarBicho={(nivel) =>
              comErro(async () => {
                setOcupado(true)
                try {
                  const r = await api.definirBicho(nivel)
                  setConteudo({ tipo: 'financas', dados: r.tela })
                  setRecado(r.recado)
                } finally {
                  setOcupado(false)
                }
              })
            }
            aoTomarCredito={(valor, meses) =>
              comErro(async () => {
                setOcupado(true)
                try {
                  const r = await api.tomarCredito(valor, meses)
                  setConteudo({ tipo: 'financas', dados: r.tela })
                  setRecado(r.recado)
                } finally {
                  setOcupado(false)
                }
              })
            }
            aoQuitarCredito={() =>
              comErro(async () => {
                setOcupado(true)
                try {
                  const r = await api.quitarCredito()
                  setConteudo({ tipo: 'financas', dados: r.tela })
                  setRecado(r.recado)
                } finally {
                  setOcupado(false)
                }
              })
            }
          />
        )}
        {conteudo.tipo === 'infra' && (
          <Infra tela={conteudo.dados} ocupado={ocupado} aoInvestir={investir} />
        )}
        {conteudo.tipo === 'noticias' && <Noticias tela={conteudo.dados} />}
        {conteudo.tipo === 'estatisticas' && (
          <Estatisticas tela={conteudo.dados} aoAbrirFicha={abrirFicha}
          aoTrocar={(alvo) => irPara('estatisticas', alvo)} />
        )}
        {conteudo.tipo === 'clube' && (
          <Clube tela={conteudo.dados} aoAbrirFicha={abrirFicha} aoTrocar={(id) => irPara('clube', String(id))} />
        )}
        {conteudo.tipo === 'carreira' && (
          <Carreira
            tela={conteudo.dados}
            ocupado={ocupado}
            aoPedirDemissao={pedirDemissao}
            aoResponderProposta={responderProposta}
          />
        )}
        {conteudo.tipo === 'escalacao' && (
          <Escalacao
            tela={conteudo.dados}
            ocupado={ocupado || mudandoAuto}
            mercadoPronto={cabecalho.menu.some((m) => m.id === 'mercado' && m.pronta)}
            aoAbrirFicha={abrirFicha}
            aoAgir={agirEscalacao}
            aoIr={(destino) => irPara(destino)}
          />
        )}
        {conteudo.tipo === 'treino' && (
          <Treino tela={conteudo.dados} ocupado={ocupado} aoAbrirFicha={abrirFicha} aoAgir={agirTreino} />
        )}
        {conteudo.tipo === 'mercado' && (
          <Mercado tela={conteudo.dados} ocupado={ocupado} aoAbrirFicha={abrirFicha} aoAgir={agirMercado} />
        )}
        {conteudo.tipo === 'estadio' && (
          <Estadio tela={conteudo.dados} ocupado={ocupado} aoAgir={agirEstadio} />
        )}
      </div>

      {ficha && (
        <Ficha
          ficha={ficha}
          aoFechar={() => setFicha(null)}
          acoes={[
            ...(ficha.pode_observar
              ? [{ rotulo: ficha.observado ? 'Parar de observar' : 'Observar',
                   aoClicar: () => observarDaFicha(ficha.id, !ficha.observado) }]
              : []),
            ...((conteudo.tipo !== 'mercado' || conteudo.dados.aba === 'vitrine'
              ? ficha.pode_capitao
                ? [{ rotulo: 'Tornar capitao', aoClicar: () => tornarCapitao(ficha.id) }]
                : undefined
              : conteudo.dados.aba === 'emprestimo'
                ? [{ rotulo: 'Pegar emprestado', principal: true,
                     aoClicar: () => { setFicha(null); setMesa({ tipo: 'emprestimo', id: ficha.id }) } }]
                : [
                    ...(ficha.clube !== 'sem clube'
                      ? [{ rotulo: 'Pedir emprestado',
                           aoClicar: () => { setFicha(null); setMesa({ tipo: 'emprestimo', id: ficha.id }) } }]
                      : []),
                    { rotulo: ficha.clube === 'sem clube' ? 'Negociar contrato' : 'Negociar compra',
                      principal: true,
                      aoClicar: () => { setFicha(null); setMesa({ tipo: 'compra', id: ficha.id }) } },
                  ]) ?? []),
          ]}
        />
      )}

      {simulando && (
        <DialogoAvanco
          aoAbrirEscalacao={() => {
            setSimulando(false)
            irPara('escalacao')
          }}
          aoFechar={(houve, p, eventos) => {
            setSimulando(false)
            if (p) setPendencia(p)
            if (eventos?.length) setPlantao(eventos)
            // o mundo andou: a tela de tras (e o topo) se refazem
            if (houve && conteudo) {
              if (conteudo.tipo === 'mercado') recarregarAtual()
              else irPara(conteudo.tipo)
            }
          }}
        />
      )}

      {mesa && <Mesa key={`${mesa.tipo}-${mesa.id}`} tipo={mesa.tipo} id={mesa.id} aoFechar={fecharMesa} />}

      {dialogoVitrine && (
        <DialogoVitrine
          ids={dialogoVitrine}
          ocupado={ocupado}
          aoFechar={() => setDialogoVitrine(null)}
          aoConfirmar={(precos) => {
            setDialogoVitrine(null)
            despachar<unknown>(() => api.porAVenda(precos, origem()), aplicarVolta)
          }}
        />
      )}

      {dialogoRenovar && (
        <DialogoRenovar
          ids={dialogoRenovar}
          ocupado={ocupado}
          aoFechar={() => setDialogoRenovar(null)}
          aoConfirmar={(anos) => {
            const ids = dialogoRenovar
            setDialogoRenovar(null)
            comErro(async () => {
              setOcupado(true)
              try {
                const r = await api.renovarLote(ids, anos)
                await recarregarAtual()
                setRecado(r.recado)
              } finally {
                setOcupado(false)
              }
            })
          }}
        />
      )}

      {dialogoCeder && (
        <DialogoCeder
          ids={dialogoCeder}
          ocupado={ocupado}
          aoFechar={() => setDialogoCeder(null)}
          aoConfirmar={(itens) => {
            setDialogoCeder(null)
            despachar<unknown>((c) => api.ceder(itens, origem(), c), aplicarVolta)
          }}
        />
      )}

      {pergunta && (
        <div
          className="fundo-modal"
          role="dialog"
          aria-modal="true"
          aria-label={pergunta.confirmar.titulo}
        >
          <div className="modal">
            <h2>{pergunta.confirmar.titulo}</h2>
            <p>{pergunta.confirmar.texto}</p>
            <div className="modal-acoes">
              <button type="button" className="bt-fantasma" onClick={() => setPergunta(null)}>
                Cancelar
              </button>
              {pergunta.destino && pergunta.destino !== conteudo.tipo && (
                <button
                  type="button"
                  className="bt-fantasma"
                  onClick={() => {
                    const destino = pergunta.destino as string
                    setPergunta(null)
                    irPara(destino)
                  }}
                >
                  Abrir {pergunta.destino}
                </button>
              )}
              <button
                type="button"
                className={`bt-acao${pergunta.confirmar.perigo ? ' bt-perigo' : ''}`}
                title={porque([[ocupado, AGUARDE]])}
                disabled={ocupado}
                onClick={() => pergunta.aoConfirmar()}
              >
                Confirmar
              </button>
            </div>
          </div>
        </div>
      )}

      {resumo && (
        <Resumo
          resumo={resumo}
          rotuloFechar={
            pendencia ? 'Continuar' : resumo.previa ? 'Fechar' : `Comecar a pre-temporada ${resumo.temporada + 1}`
          }
          aoFechar={() => setResumo(null)}
        />
      )}

      {plantao.length > 0 && !resumo && <Plantao eventos={plantao} aoFechar={() => setPlantao([])} />}

      {boasVindas && (
        <BoasVindas
          dados={boasVindas}
          aoFechar={() => setBoasVindas(null)}
          aoVerAjuda={() => {
            setBoasVindas(null)
            abrirAjuda()
          }}
        />
      )}

      {ajuda && <Ajuda ajuda={ajuda} aoFechar={() => setAjuda(null)} />}

      {pendencia && !resumo && (
        <JanelaPendencia
          pendencia={pendencia}
          ocupado={ocupado}
          aoEscolher={(id) =>
            comErro(async () => {
              const r = await api.escolherClube(id)
              setPendencia(r.pendencia ?? null)
              await irPara('painel')
              setRecado('Carreira segue: bem-vindo ao clube novo.')
            })
          }
          aoEncerrar={() =>
            comErro(async () => {
              const r = await api.encerrarCarreira()
              setPendencia(r.pendencia ?? null)
            })
          }
          aoNovaCarreira={() => {
            // volta ao menu: carreira nova passa pelo nome e pelas opcoes
            setPendencia(null)
            setSituacao('tem_save')
          }}
        />
      )}
    </div>
  )
}
