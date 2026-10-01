// O Mercado: quatro abas visiveis, e nao um filtro escondido.
//
// Na janela tkinter o emprestimo era um item de combobox que quase ninguem
// achava; la ele virou botao, aqui virou aba. Comprar, Emprestimos e Agentes
// livres sao a mesma busca com colunas diferentes; Vender (a vitrine) junta tudo o
// que sai do clube: quem esta a venda, as propostas da semana e os acertos
// feitos com a janela fechada.
//
// Negociar abre a mesa (componentes/Mesa.tsx); quem fecha negocio e o motor.

import { porque, AGUARDE } from '../motivo'
import { useEffect, useState } from 'react'
import { seloOvr, seloPos } from '../componentes/Celulas'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import { CampoDinheiro } from '../componentes/CampoDinheiro'
import { Escudo } from '../componentes/Escudo'
import { alternarMarca, chaveDeOrdem, Grade, type Coluna } from '../componentes/Grade'
import { dinheiro, plural } from '../formato'
import { LegendaCores } from '../componentes/LegendaCores'
import { iconeDeEstado } from '../icones'
import type {
  AbaMercado,
  Agendada,
  ContratoAcabando,
  Financeiro,
  FiltrosMercado,
  LinhaMercado,
  LinhaVitrine,
  OfertaRecebida,
  TelaMercado,
  TipoMesa,
} from '../tipos'

export type AcaoMercado =
  | { tipo: 'buscar'; aba: AbaMercado; filtros?: Partial<FiltrosMercado> }
  | { tipo: 'negociar'; mesa: TipoMesa; id: number }
  | { tipo: 'reprecificar'; ids: number[] }
  | { tipo: 'tirar'; ids: number[] }
  | { tipo: 'aceitar'; itens: { id: number; clube_id: number }[] }
  | { tipo: 'recusar'; itens: { id: number; clube_id: number }[] }
  | { tipo: 'contra'; id: number; clube_id: number; valor: number }
  | { tipo: 'renovar'; ids: number[] }
  | { tipo: 'cancelar'; indices: number[] }

interface Props {
  tela: TelaMercado
  ocupado: boolean
  aoAbrirFicha: (id: number) => void
  aoAgir: (acao: AcaoMercado) => void
}

const MARCA: Record<string, string> = { a_venda: ' *', intocavel: ' !' }

const BASE: Coluna<LinhaMercado>[] = [
  { chave: 'pos', rotulo: 'Pos', largura: '46px', classe: 'centro', render: (j) => seloPos(j.pos) },
  {
    chave: 'nome',
    rotulo: 'Jogador',
    largura: 'minmax(140px, 1.5fr)',
    classe: 'corta',
    render: (j) => (
      <>
        <span className={`tag-${j.tag}`}>{j.nome}</span>
        {j.acertado && <span className="selo-nova-vaga">acertado</span>}
      </>
    ),
  },
  { chave: 'idade', rotulo: 'Idade', largura: '50px', classe: 'num', render: (j) => j.idade },
  { chave: 'ovr', rotulo: 'Ovr', largura: '42px', classe: 'num', render: (j) => seloOvr(j.ovr) },
  { chave: 'teto', rotulo: 'Teto', largura: '70px', classe: 'centro', render: (j) => j.teto },
  {
    chave: 'clube',
    rotulo: 'Clube',
    largura: 'minmax(120px, 1fr)',
    render: (j) =>
      j.livre ? (
        <span className="clube-atual livre">sem clube</span>
      ) : (
        <span className="escudo-com-nome clube-atual">
          <Escudo nome={j.clube} tamanho={18} />
          <span>{j.clube}</span>
        </span>
      ),
  },
  { chave: 'sal', rotulo: 'Salario', largura: '88px', classe: 'num', render: (j) => <span className="preco-fraco">{j.salario}</span> },
]

const COLUNAS_COMPRA: Coluna<LinhaMercado>[] = [
  ...BASE,
  { chave: 'valor', rotulo: 'Valor', largura: '92px', classe: 'num', ordem: (j) => j.valor_num, render: (j) => <span className="preco-fraco">{j.valor}</span> },
  {
    chave: 'pedido',
    rotulo: 'Pedido',
    largura: '104px',
    classe: 'num',
    // agente livre ("livre") vai para o fim; o resto pelo valor pedido
    ordem: (j) => (j.pedido_num ?? null),
    render: (j) => (
      <span className={`preco-forte ${j.marca === 'intocavel' ? 'linha-critica' : j.marca === 'a_venda' ? 'tag-ok' : ''}`}>
        {j.pedido}
        {MARCA[j.marca ?? ''] ?? ''}
      </span>
    ),
  },
  { chave: 'emp', rotulo: 'Emp', largura: '44px', classe: 'centro', render: (j) => (j.emprestimo ? 'sim' : '') },
]

const COLUNAS_EMPRESTIMO: Coluna<LinhaMercado>[] = [
  ...BASE,
  { chave: 'pct', rotulo: 'Dono quer', largura: '80px', classe: 'centro', render: (j) => `${j.pct}%` },
  { chave: 'fatia', rotulo: 'Sua fatia', largura: '92px', classe: 'num', render: (j) => j.fatia },
]

const COLUNAS_VITRINE: Coluna<LinhaVitrine>[] = [
  {
    chave: 'nome',
    rotulo: 'Jogador',
    largura: 'minmax(130px, 1.4fr)',
    classe: 'corta',
    render: (j) => <span className={`tag-${j.tag}`}>{j.nome}</span>,
  },
  { chave: 'pos', rotulo: 'Pos', largura: '46px', classe: 'centro', render: (j) => seloPos(j.pos) },
  { chave: 'ovr', rotulo: 'Ovr', largura: '42px', classe: 'num', render: (j) => seloOvr(j.ovr) },
  { chave: 'sal', rotulo: 'Salario', largura: '88px', classe: 'num', render: (j) => j.salario },
  { chave: 'val', rotulo: 'Valor', largura: '92px', classe: 'num', render: (j) => j.valor },
  { chave: 'ped', rotulo: 'Voce pede', largura: '96px', classe: 'num', render: (j) => j.pede },
  { chave: 'pct', rotulo: '%', largura: '48px', classe: 'num', render: (j) => `${j.pct}%` },
  {
    chave: 'quem',
    rotulo: 'Proposta',
    largura: 'minmax(110px, 1fr)',
    classe: 'corta',
    render: (j) => (j.interessado ? <span className="tag-atencao">{j.interessado}: {j.oferta}</span> : '-'),
  },
]

const COLUNAS_OFERTAS: Coluna<OfertaRecebida & { indice: number }>[] = [
  { chave: 'nome', rotulo: 'Jogador', largura: 'minmax(120px, 1.2fr)', classe: 'corta', render: (o) => o.nome },
  { chave: 'pos', rotulo: 'Pos', largura: '46px', classe: 'centro', render: (o) => seloPos(o.pos) },
  { chave: 'ovr', rotulo: 'Ovr', largura: '42px', classe: 'num', render: (o) => seloOvr(o.ovr) },
  { chave: 'clube', rotulo: 'Interessado', largura: 'minmax(110px, 1fr)', classe: 'corta', render: (o) => `${o.clube} (${o.divisao})` },
  { chave: 'val', rotulo: 'Valor dele', largura: '96px', classe: 'num', render: (o) => o.valor },
  { chave: 'of', rotulo: 'Oferta', largura: '96px', classe: 'num', render: (o) => <strong>{o.oferta}</strong> },
  {
    chave: 'pv',
    rotulo: '% valor',
    largura: '64px',
    classe: 'num',
    render: (o) => (
      <span className={o.pct_valor >= 100 ? 'tag-ok' : o.pct_valor >= 85 ? 'tag-atencao' : 'tag-critico'}>
        {o.pct_valor}%
      </span>
    ),
  },
  { chave: 'ped', rotulo: 'Voce pede', largura: '120px', classe: 'num', render: (o) => o.pede },
  {
    chave: 'dif',
    rotulo: 'Diferenca',
    largura: '96px',
    classe: 'num',
    render: (o) => <span className={`tag-${o.estado}`}>{o.diferenca}</span>,
  },
]

const COLUNAS_AGENDADAS: Coluna<Agendada>[] = [
  { chave: 'quem', rotulo: 'Jogador', largura: 'minmax(120px, 1.2fr)', classe: 'corta', render: (a) => a.jogador },
  { chave: 'tipo', rotulo: 'Negocio', largura: '90px', classe: 'centro', render: (a) => a.tipo },
  { chave: 'com', rotulo: 'Com', largura: 'minmax(110px, 1fr)', classe: 'corta', render: (a) => a.com },
  { chave: 'valor', rotulo: 'Valor', largura: '100px', classe: 'num', render: (a) => a.valor },
  { chave: 'quando', rotulo: 'Acertado em', largura: '96px', classe: 'centro', render: (a) => a.quando },
]

const COLUNAS_CONTRATOS: Coluna<ContratoAcabando>[] = [
  {
    chave: 'nome',
    rotulo: 'Jogador',
    largura: 'minmax(130px, 1.4fr)',
    classe: 'corta',
    render: (j) => <span className={`tag-${j.tag}`}>{j.nome}</span>,
  },
  { chave: 'pos', rotulo: 'Pos', largura: '46px', classe: 'centro', render: (j) => seloPos(j.pos) },
  { chave: 'ovr', rotulo: 'Ovr', largura: '42px', classe: 'num', render: (j) => seloOvr(j.ovr) },
  { chave: 'idade', rotulo: 'Idade', largura: '50px', classe: 'num', render: (j) => j.idade },
  {
    chave: 'quando',
    rotulo: 'Contrato',
    largura: 'minmax(150px, 1.4fr)',
    classe: 'corta',
    render: (j) => <span className={`tag-${j.estado}`}>{j.quando}</span>,
  },
  { chave: 'sal', rotulo: 'Salario', largura: '88px', classe: 'num', render: (j) => j.salario },
  { chave: 'pede', rotulo: 'Pede p/ 3 anos', largura: '104px', classe: 'num', render: (j) => j.pede },
]

// o caixa nao e todo de contratar: a faixa diz quanto e, e por que
function FaixaVerba({ f }: { f: Financeiro }) {
  const lido = (t: string) => {
    const v = chaveDeOrdem(t)
    return typeof v === 'number' ? v : 0
  }
  const caixa = Math.max(1, lido(f.caixa))
  const reserva = Math.min(caixa, Math.max(0, lido(f.reserva)))
  const verba = Math.min(caixa - reserva, Math.max(0, f.verba_num))
  return (
    <section className={`painel faixa verba-faixa ${f.estado}`}>
      <div className="faixa-icone">{iconeDeEstado(f.estado)}</div>
      <div className="verba-texto">
        <div className="faixa-titulo">Verba para contratar: {f.verba}</div>
        <div className="faixa-detalhe">
          Caixa {f.caixa}; {f.reserva} reservados para {f.meses} meses de folha e custos ({f.custos_mes} por mes). Saldo do
          mes: {f.saldo_mes}. O salario de quem chega entra na reserva antes do passe.
        </div>
      </div>
      <div className="verba-medidor" role="img" aria-label={`Caixa ${f.caixa}: ${f.reserva} reservados, ${f.verba} livres`}>
        <div className="medidor-trilho">
          <i className="reserva" style={{ width: `${(reserva / caixa) * 100}%` }} />
          <i className={`verba ${f.estado}`} style={{ width: `${(verba / caixa) * 100}%` }} />
        </div>
        <div className="verba-legenda">
          <span>reservado {f.reserva}</span>
          <span>livre {f.verba}</span>
        </div>
      </div>
    </section>
  )
}

function Contraproposta({
  o,
  ocupado,
  aoEnviar,
}: {
  o: OfertaRecebida
  ocupado: boolean
  aoEnviar: (valor: number) => void
}) {
  const [valor, setValor] = useState(Math.round(Math.max(o.oferta_num * 1.1, o.pede_num || 0) / 1000) * 1000)
  useEffect(() => {
    setValor(Math.round(Math.max(o.oferta_num * 1.1, o.pede_num || 0) / 1000) * 1000)
  }, [o.chave, o.oferta_num, o.pede_num])
  const acima = Math.round((valor / Math.max(1, o.oferta_num) - 1) * 100)
  const risco = acima <= 0 ? 'ok' : acima <= 15 ? 'ok' : acima <= 35 ? 'atencao' : 'critico'
  const atalhos = [
    { rotulo: '+10% da oferta', valor: o.oferta_num * 1.1 },
    { rotulo: '+20% da oferta', valor: o.oferta_num * 1.2 },
    { rotulo: 'valor de mercado', valor: o.valor_num },
    ...(o.pede_num ? [{ rotulo: 'seu pedido', valor: o.pede_num }] : []),
  ]
  return (
    <div className="contraproposta">
      <div className="painel-titulo">
        Contraproposta por {o.nome} · {o.clube}
      </div>
      <div className="contra-numeros">
        <span>
          Valor de mercado <strong>{o.valor}</strong>
        </span>
        <span>
          Oferta <strong>{o.oferta}</strong> ({o.pct_valor}% do valor)
        </span>
        <span>
          Voce pede <strong>{o.pede}</strong>
        </span>
      </div>
      <div className="contra-linha">
        <CampoDinheiro rotulo="Voce quer" valor={valor} aoMudar={setValor} />
        <div className="contra-atalhos">
          {atalhos.map((a) => (
            <button
              key={a.rotulo}
              type="button"
              className="bt-fantasma bt-mini"
              onClick={() => setValor(Math.round(a.valor / 1000) * 1000)}
            >
              {a.rotulo}
            </button>
          ))}
        </div>
        <span className={`tag-${risco}`}>
          {acima <= 0 ? 'igual ou abaixo da oferta: e aceitar' : `+${acima}% sobre a oferta`}
        </span>
        <button
          type="button"
          className="bt-acao bt-media"
          title={porque([[ocupado, AGUARDE], [!valor, 'Diga quanto voce quer'], [o.contras <= 0, 'Sem contraproposta restante nesta semana']])}
          disabled={ocupado || !valor || o.contras <= 0}
          onClick={() => aoEnviar(valor)}
        >
          Enviar contraproposta
        </button>
      </div>
      <p className="contra-dica">
        Como funciona: o {o.clube} compara o seu valor com o quanto ele acha que {o.nome} vale para ele e com a verba
        dele. Se couber, a venda fecha na hora pelo seu valor. Se passar um pouco, ele sobe a oferta ate um meio-termo.
        Se voce pedir muito acima, ele retira a proposta.{' '}
        {o.contras > 0
          ? `${o.contras === 1 ? 'Resta 1 contraproposta' : `Restam ${o.contras} contrapropostas`} nesta oferta nesta semana.`
          : 'Ele ja deu a ultima palavra nesta semana: aceite ou recuse.'}
      </p>
    </div>
  )
}

export function Mercado({ tela, ocupado, aoAbrirFicha, aoAgir }: Props) {
  const [marcado, setMarcado] = useState<number | null>(null)
  const [vitrine, setVitrine] = useState<Set<number>>(new Set())
  const [ofertas, setOfertas] = useState<Set<number>>(new Set())
  const [agendadas, setAgendadas] = useState<Set<number>>(new Set())
  const [contratos, setContratos] = useState<Set<number>>(new Set())
  const [pos, setPos] = useState(tela.filtros.pos ?? '')
  const [ovr, setOvr] = useState(tela.filtros.ovr ? String(tela.filtros.ovr) : '')
  const [idade, setIdade] = useState(tela.filtros.idade ? String(tela.filtros.idade) : '')
  const [teto, setTeto] = useState(tela.filtros.teto ?? 0)
  const [idadeMin, setIdadeMin] = useState(tela.filtros.idade_min ? String(tela.filtros.idade_min) : '')
  const [potMin, setPotMin] = useState(tela.filtros.pot_min ? String(tela.filtros.pot_min) : '')
  const [regiao, setRegiao] = useState(tela.filtros.regiao ?? '')
  const [soVenda, setSoVenda] = useState(tela.filtros.so_venda ?? false)

  // a tela voltou do servidor (outra aba, negocio fechado): marcacoes antigas
  // podem apontar para quem ja saiu
  useEffect(() => {
    setMarcado(null)
    setVitrine(new Set())
    setOfertas(new Set())
    setAgendadas(new Set())
    setContratos(new Set())
  }, [tela])

  const filtros = (): Partial<FiltrosMercado> => ({
    pos: pos || null,
    ovr: ovr ? Number(ovr) : null,
    idade: idade ? Number(idade) : null,
    teto: teto || null,
    idade_min: idadeMin ? Number(idadeMin) : null,
    pot_min: potMin ? Number(potMin) : null,
    regiao: regiao || null,
    so_venda: soVenda,
  })
  const limpar = () => {
    setPos('')
    setOvr('')
    setIdade('')
    setTeto(0)
    setIdadeMin('')
    setPotMin('')
    setRegiao('')
    setSoVenda(false)
    aoAgir({ tipo: 'buscar', aba, filtros: {} })
  }

  const aba = tela.aba
  const alvo = tela.jogadores.find((j) => j.id === marcado) ?? null
  const ofertasIdx = tela.ofertas.map((o, i) => ({ ...o, indice: i }))
  const itensOfertas = ofertasIdx
    .filter((o) => ofertas.has(o.indice))
    .map((o) => ({ id: o.id, clube_id: o.clube_id }))
  const entra = ofertasIdx.filter((o) => ofertas.has(o.indice)).reduce((s, o) => s + o.oferta_num, 0)
  // contraproposta e uma conversa com UM clube: aparece com uma oferta marcada
  const umaOferta = ofertas.size === 1 ? ofertasIdx.find((o) => ofertas.has(o.indice)) ?? null : null

  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={tela.subtitulo} metricas={tela.metricas} />

      <div className="abas" role="tablist" aria-label="Areas do mercado">
        {tela.abas.map((a) => (
          <button
            key={a.id}
            type="button"
            role="tab"
            aria-selected={a.id === aba}
            className={`aba${a.id === aba ? ' ativa' : ''}`}
            title={porque([[ocupado, AGUARDE]])}
            disabled={ocupado}
            onClick={() => a.id !== aba && aoAgir({ tipo: 'buscar', aba: a.id, filtros: filtros() })}
          >
            {a.nome}
            {a.contador ? <span className="contador">{a.contador}</span> : null}
          </button>
        ))}
        {!tela.aberto && (
          <span className="aviso-janela">janela fechada: da para acertar agora, o jogador troca de clube na abertura</span>
        )}
      </div>

      <FaixaVerba f={tela.financeiro} />

      {aba !== 'vitrine' ? (
        <>
          <form
            className="painel barra-acoes filtros filtros-c"
            onSubmit={(e) => {
              e.preventDefault()
              aoAgir({ tipo: 'buscar', aba, filtros: filtros() })
            }}
          >
            <label className="campo-rotulo">
              Posicao
              <select className="seletor" value={pos} onChange={(e) => setPos(e.target.value)}>
                <option value="">Todas</option>
                {tela.posicoes.map((p) => (
                  <option key={p}>{p}</option>
                ))}
              </select>
            </label>
            <label className="campo-rotulo">
              Ovr min
              <input
                className="seletor entrada entrada-curta"
                inputMode="numeric"
                value={ovr}
                onChange={(e) => setOvr(e.target.value.replace(/\D/g, '').slice(0, 2))}
              />
            </label>
            <label className="campo-rotulo">
              Idade min
              <input
                className="seletor entrada entrada-curta"
                inputMode="numeric"
                value={idadeMin}
                onChange={(e) => setIdadeMin(e.target.value.replace(/\D/g, '').slice(0, 2))}
              />
            </label>
            <label className="campo-rotulo">
              Idade max
              <input
                className="seletor entrada entrada-curta"
                inputMode="numeric"
                value={idade}
                onChange={(e) => setIdade(e.target.value.replace(/\D/g, '').slice(0, 2))}
              />
            </label>
            <label className="campo-rotulo" title="Pelo que o seu olheiro enxerga: o potencial real e escondido">
              Teto min
              <input
                className="seletor entrada entrada-curta"
                inputMode="numeric"
                value={potMin}
                onChange={(e) => setPotMin(e.target.value.replace(/\D/g, '').slice(0, 2))}
              />
            </label>
            {aba !== 'livres' && (
              <label className="campo-rotulo">
                Regiao
                <select className="seletor" value={regiao} onChange={(e) => setRegiao(e.target.value)}>
                  <option value="">Todas</option>
                  {tela.regioes.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.nome}
                    </option>
                  ))}
                </select>
              </label>
            )}
            {aba !== 'livres' && <CampoDinheiro rotulo="Pedido ate" valor={teto} aoMudar={setTeto} />}
            {aba === 'compra' && (
              <label className="avanco-parada filtro-marca">
                <input type="checkbox" checked={soVenda} onChange={(e) => setSoVenda(e.target.checked)} />
                So a venda
              </label>
            )}
            <div className="filtros-botoes">
              <button type="button" className="bt-fantasma bt-media" disabled={ocupado} onClick={limpar}>
                Limpar
              </button>
              <button type="submit" className="bt-acao bt-media" title={porque([[ocupado, AGUARDE]])} disabled={ocupado}>
                Buscar
              </button>
            </div>
          </form>

          <section className="painel painel-lista">
            <Grade
              colunas={aba === 'emprestimo' ? COLUNAS_EMPRESTIMO : COLUNAS_COMPRA}
              itens={tela.jogadores}
              idDe={(j) => j.id}
              nomeDe={(j) => j.nome}
              marcados={new Set(marcado === null ? [] : [marcado])}
              aoMarcar={(id) => setMarcado(marcado === id ? null : id)}
              memoria={`mercado-${aba}`}
              aoAbrir={(j) => aoAbrirFicha(j.id)}
              vazio="Ninguem com esse perfil agora. Afrouxe os filtros."
            />
            <LegendaCores />
            <div className="barra-acoes barra-presa">
              <span className="resumo">
                {/* com alguem marcado, a barra diz quem e: ela fica presa no rodape
                    e a linha marcada pode estar la em cima, fora da vista */}
                {alvo?.acertado ? (
                  <strong className="tag-atencao">
                    {alvo.nome} ja esta acertado com voce: chega na abertura da janela.
                  </strong>
                ) : alvo ? (
                  <strong className="tag-ok">
                    {alvo.nome} · {alvo.pos} · {alvo.ovr} ·{' '}
                    {aba === 'emprestimo' ? `dono quer ${alvo.pct}%` : alvo.livre ? 'agente livre' : `pede ${alvo.pedido}`}
                  </strong>
                ) : aba === 'emprestimo' ? (
                  'marque um jogador · aqui aparece so quem foi oferecido; para pedir qualquer outro, use Pedir emprestado na aba Comprar'
                ) : (
                  'marque um jogador · * o clube quer vender · ! nao quer vender (pede mais caro) · Emp: tambem sai por emprestimo'
                )}
              </span>
              <button type="button" className="bt-fantasma" title={porque([[!alvo, 'Marque um jogador na lista']])}
              disabled={!alvo} onClick={() => alvo && aoAbrirFicha(alvo.id)}>
                Ver ficha
              </button>
              {aba === 'compra' && (
                <button
                  type="button"
                  className="bt-fantasma"
                  title={porque([[!alvo, 'Marque um jogador na lista'], [Boolean(alvo?.acertado), 'Ja acertado com voce: ele chega na abertura da janela'], [ocupado, AGUARDE]])}
                  disabled={!alvo || alvo.acertado || ocupado}
                  onClick={() => alvo && aoAgir({ tipo: 'negociar', mesa: 'emprestimo', id: alvo.id })}
                >
                  Pedir emprestado
                </button>
              )}
              <button
                type="button"
                className="bt-acao bt-media"
                title={porque([[!alvo, 'Marque um jogador na lista'], [Boolean(alvo?.acertado), 'Ja acertado com voce: ele chega na abertura da janela'], [ocupado, AGUARDE]])}
                disabled={!alvo || alvo.acertado || ocupado}
                onClick={() =>
                  alvo && aoAgir({ tipo: 'negociar', mesa: aba === 'emprestimo' ? 'emprestimo' : 'compra', id: alvo.id })
                }
              >
                {aba === 'emprestimo' ? 'Pegar emprestado' : aba === 'livres' ? 'Negociar contrato' : 'Negociar compra'}
              </button>
            </div>
          </section>
        </>
      ) : (
        <>
          {tela.contratos.length > 0 && (
            <>
              <div className="painel-titulo tag-atencao">Contratos acabando: renove ou venda antes que saiam de graca</div>
              <section className="painel painel-lista">
                <Grade
                  colunas={COLUNAS_CONTRATOS}
                  itens={tela.contratos}
                  idDe={(j) => j.id}
                  nomeDe={(j) => j.nome}
                  marcados={contratos}
                  aoMarcar={(id) => setContratos((s) => alternarMarca(s, id))}
                  aoMarcarTodos={(ids) => setContratos(new Set(ids))}
                  memoria="mercado-contratos"
                  aoAbrir={(j) => aoAbrirFicha(j.id)}
                />
                <div className="barra-acoes barra-presa">
                  <span className="resumo">
                    {contratos.size
                      ? `${plural(contratos.size, 'marcado')}: as mesas abrem uma depois da outra`
                      : 'sem marcar ninguem, renova todos da lista, um por vez'}
                  </span>
                  <button
                    type="button"
                    className="bt-acao bt-media"
                    title={porque([[ocupado, AGUARDE]])}
                    disabled={ocupado}
                    onClick={() =>
                      aoAgir({
                        tipo: 'renovar',
                        ids: contratos.size ? tela.contratos.filter((j) => contratos.has(j.id)).map((j) => j.id) : tela.contratos.map((j) => j.id),
                      })
                    }
                  >
                    Renovar
                  </button>
                </div>
              </section>
            </>
          )}

          <div className="painel-titulo">Na vitrine</div>
          <section className="painel painel-lista">
            <Grade
              colunas={COLUNAS_VITRINE}
              itens={tela.vitrine}
              idDe={(j) => j.id}
              nomeDe={(j) => j.nome}
              marcados={vitrine}
              aoMarcar={(id) => setVitrine((s) => alternarMarca(s, id))}
              aoMarcarTodos={(ids) => setVitrine(new Set(ids))}
              memoria="mercado-vitrine"
              aoAbrir={(j) => aoAbrirFicha(j.id)}
              vazio="Ninguem na vitrine. Marque jogadores no Elenco e use Por a venda - da para precificar varios de uma vez."
            />
            {tela.vitrine.length > 0 && (
              <div className="barra-acoes barra-presa">
                <span className="resumo">
                  {vitrine.size ? plural(vitrine.size, 'marcado') : 'sem marcar ninguem, a acao vale para todos da vitrine'}
                </span>
                <button
                  type="button"
                  className="bt-fantasma"
                  title={porque([[ocupado, AGUARDE]])}
                  disabled={ocupado}
                  onClick={() => aoAgir({ tipo: 'reprecificar', ids: vitrine.size ? [...vitrine] : tela.vitrine.map((j) => j.id) })}
                >
                  Reprecificar
                </button>
                <button
                  type="button"
                  className="bt-fantasma"
                  title={porque([[ocupado, AGUARDE]])}
                  disabled={ocupado}
                  onClick={() => aoAgir({ tipo: 'tirar', ids: vitrine.size ? [...vitrine] : tela.vitrine.map((j) => j.id) })}
                >
                  Tirar da vitrine
                </button>
              </div>
            )}
          </section>

          <div className="painel-titulo">Propostas desta semana</div>
          <section className="painel painel-lista">
            <Grade
              colunas={COLUNAS_OFERTAS}
              itens={ofertasIdx}
              idDe={(o) => o.indice}
              nomeDe={(o) => `${o.nome}, oferta do ${o.clube}`}
              marcados={ofertas}
              aoMarcar={(i) => setOfertas((s) => alternarMarca(s, i))}
              aoMarcarTodos={(ids) => setOfertas(new Set(ids))}
              memoria="mercado-ofertas"
              aoAbrir={(o) => aoAbrirFicha(o.id)}
              vazio="Nenhuma proposta nesta semana. Ponha alguem na vitrine, ou baixe o preco: pedir muito acima do valor afasta comprador."
            />
            {umaOferta && (
              <Contraproposta
                o={umaOferta}
                ocupado={ocupado}
                aoEnviar={(valor) => aoAgir({ tipo: 'contra', id: umaOferta.id, clube_id: umaOferta.clube_id, valor })}
              />
            )}
            {tela.ofertas.length > 0 && (
              <div className="barra-acoes barra-presa">
                <span className="resumo">
                  {!umaOferta && 'marque UMA proposta para fazer contraproposta · '}
                  as mesmas ate a semana virar: nao adianta sair e voltar
                  {itensOfertas.length > 0 &&
                    ` · ${plural(itensOfertas.length, 'marcada')}, entram ${dinheiro(entra)}`}
                </span>
                <button
                  type="button"
                  className="bt-fantasma"
                  title={porque([[ocupado, AGUARDE], [!itensOfertas.length, 'Marque pelo menos uma proposta']])}
                  disabled={ocupado || !itensOfertas.length}
                  onClick={() => aoAgir({ tipo: 'recusar', itens: itensOfertas })}
                >
                  Recusar marcadas
                </button>
                <button
                  type="button"
                  className="bt-acao bt-media"
                  title={porque([[ocupado, AGUARDE], [!itensOfertas.length, 'Marque pelo menos uma proposta']])}
                  disabled={ocupado || !itensOfertas.length}
                  onClick={() => aoAgir({ tipo: 'aceitar', itens: itensOfertas })}
                >
                  Aceitar marcadas
                </button>
              </div>
            )}
          </section>
        </>
      )}

      {tela.agendadas.length > 0 && (
        <>
          <div className="painel-titulo tag-atencao">Acertado para a proxima janela</div>
          <section className="painel painel-lista">
            <Grade
              colunas={COLUNAS_AGENDADAS}
              itens={tela.agendadas}
              idDe={(a) => a.indice}
              nomeDe={(a) => a.jogador}
              marcados={agendadas}
              aoMarcar={(i) => setAgendadas((s) => alternarMarca(s, i))}
              aoMarcarTodos={(ids) => setAgendadas(new Set(ids))}
            />
            <div className="barra-acoes barra-presa">
              <span className="resumo">entram sozinhos assim que a janela abrir, revalidando caixa e elenco</span>
              <button
                type="button"
                className="bt-fantasma bt-perigo"
                title={porque([[ocupado, AGUARDE], [agendadas.size === 0, 'Marque o acerto que voce quer desfazer']])}
                disabled={ocupado || agendadas.size === 0}
                onClick={() => aoAgir({ tipo: 'cancelar', indices: [...agendadas] })}
              >
                Cancelar acerto
              </button>
            </div>
          </section>
        </>
      )}
    </div>
  )
}
