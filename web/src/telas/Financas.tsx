// O dinheiro do clube em quatro perguntas: como foi o ano ate agora (o
// extrato, que fecha com o caixa), o que entra e sai toda semana, quanto
// ainda da para ganhar de premio, e quanto sobra para contratar.
//
// Cada linha diz de onde vem o dinheiro. A verba e o caixa menos a folha
// guardada - gastando so ela, o clube nunca fica sem pagar salario.

import { useState } from 'react'
import { CampoDinheiro } from '../componentes/CampoDinheiro'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import { chaveDeOrdem, Grade, type Coluna } from '../componentes/Grade'
import { dinheiro } from '../formato'
import { iconeDeEstado } from '../icones'
import { porque, AGUARDE } from '../motivo'
import type { ContratoPatrocinio, LinhaDinheiro, Metrica, TelaFinancas } from '../tipos'

type Maior = TelaFinancas['maiores'][number]

const COLUNAS: Coluna<Maior>[] = [
  { chave: 'nome', rotulo: 'Jogador', largura: 'minmax(150px, 2fr)', classe: 'corta', render: (j) => j.nome },
  { chave: 'pos', rotulo: 'Pos', largura: '46px', classe: 'centro', render: (j) => j.pos },
  { chave: 'sal', rotulo: 'Salario por mes', largura: '130px', classe: 'num', render: (j) => j.salario },
  { chave: 'val', rotulo: 'Valor', largura: '110px', classe: 'num', render: (j) => j.valor },
  { chave: 'obs', rotulo: 'Observacao', largura: 'minmax(120px, 1.4fr)', classe: 'corta', render: (j) => j.obs },
]

/** O valor numerico de um texto de dinheiro do servidor ("-R$ 1,1 mi" -> -1100000). */
function numero(texto: string): number {
  const v = chaveDeOrdem(texto)
  return typeof v === 'number' ? v : 0
}

function Linhas({ linhas, total }: { linhas: LinhaDinheiro[]; total?: { rotulo: string; valor: number; estado?: string } }) {
  // cada linha ganha uma barrinha com a fatia dela no grupo (so quando ha o que dividir)
  const soma = linhas.reduce((s, l) => s + Math.abs(numero(l.valor)), 0)
  return (
    <>
      {linhas.map((l) => {
        const parte = soma > 0 ? Math.abs(numero(l.valor)) / soma : 0
        return (
          <div className={`linha-valor${l.destaque ? ' total' : ''}`} key={l.nome}>
            <span className="rot">
              {l.nome}
              {l.dica && <span className="linha-dica">{l.dica}</span>}
            </span>
            <span className={`val ${l.estado ?? ''}`}>{l.valor}</span>
            {parte > 0 && !l.destaque && (
              <span className="linha-fatia" aria-hidden="true">
                <i style={{ width: `${Math.round(parte * 100)}%` }} />
              </span>
            )}
          </div>
        )
      })}
      {total && (
        <div className="linha-valor subtotal">
          <span className="rot">{total.rotulo}</span>
          <span className={`val ${total.estado ?? ''}`}>{dinheiro(total.valor)}</span>
        </div>
      )}
    </>
  )
}

const somaDe = (linhas: LinhaDinheiro[]) => linhas.reduce((s, l) => s + Math.abs(numero(l.valor)), 0)

/** Uma barra de entrada ou de saida: segmentos proporcionais ao maior dos dois lados. */
function BarraFluxo({ rotulo, tom, itens, maximo }: {
  rotulo: string
  tom: 'ok' | 'critico'
  itens: { nome: string; valor: string; v: number }[]
  maximo: number
}) {
  const total = itens.reduce((s, i) => s + i.v, 0)
  return (
    <div className={`fluxo-barra ${tom}`}>
      <div className="fluxo-cab">
        <span className="fluxo-rotulo">{rotulo}</span>
        <span className="fluxo-total">{dinheiro(total)}</span>
      </div>
      <div className="fluxo-trilho" role="img" aria-label={`${rotulo}: ${dinheiro(total)}`}>
        {itens.map((i) => (
          <i key={i.nome} title={`${i.nome}: ${i.valor}`} style={{ width: `${(i.v / maximo) * 100}%` }} />
        ))}
      </div>
      <ul className="fluxo-legenda">
        {itens.map((i) => (
          <li key={i.nome}>
            <i aria-hidden="true" />
            <span>{i.nome}</span>
            <b>{i.valor.replace(/^-/, '')}</b>
          </li>
        ))}
      </ul>
    </div>
  )
}

/** O mes em duas barras: o que entra contra o que sai, com o saldo no fim. */
function Fluxo({ linhas }: { linhas: LinhaDinheiro[] }) {
  const itens = linhas.filter((l) => !l.destaque).map((l) => ({ nome: l.nome, valor: l.valor, v: numero(l.valor) }))
  const entra = itens.filter((i) => i.v > 0)
  const sai = itens.filter((i) => i.v < 0).map((i) => ({ ...i, v: -i.v }))
  const maximo = Math.max(1, entra.reduce((s, i) => s + i.v, 0), sai.reduce((s, i) => s + i.v, 0))
  const saldo = linhas.find((l) => l.destaque)
  return (
    <div className="fluxo">
      <BarraFluxo rotulo="Entra" tom="ok" itens={entra} maximo={maximo} />
      <BarraFluxo rotulo="Sai" tom="critico" itens={sai} maximo={maximo} />
      {saldo && (
        <div className="fluxo-saldo">
          <span>{saldo.nome}</span>
          <strong className={saldo.estado ?? ''}>{saldo.valor}</strong>
        </div>
      )}
    </div>
  )
}

/** O caixa dividido: o que fica guardado para a folha e o que sobra para contratar. */
function MedidorVerba({ m }: { m: TelaFinancas['mensal'] }) {
  const caixa = Math.max(1, numero(m.caixa))
  const reserva = Math.min(caixa, Math.max(0, numero(m.reserva)))
  const verba = Math.min(caixa - reserva, Math.max(0, numero(m.verba)))
  return (
    <div className="medidor-verba">
      <div className="medidor-cab">
        <span>Caixa {m.caixa}</span>
        <strong className={m.estado}>Verba para contratar {m.verba}</strong>
      </div>
      <div className="medidor-trilho" role="img" aria-label={`Caixa ${m.caixa}, reservado ${m.reserva}, verba ${m.verba}`}>
        <i className="reserva" style={{ width: `${(reserva / caixa) * 100}%` }} />
        <i className={`verba ${m.estado}`} style={{ width: `${(verba / caixa) * 100}%` }} />
      </div>
      <ul className="fluxo-legenda">
        <li className="reserva">
          <i aria-hidden="true" />
          <span>Reservado ({m.meses} meses de folha e custos)</span>
          <b>{m.reserva}</b>
        </li>
        <li className={`verba ${m.estado}`}>
          <i aria-hidden="true" />
          <span>Livre para contratar</span>
          <b>{m.verba}</b>
        </li>
      </ul>
    </div>
  )
}

function CartaoPatrocinio({ k, titulo, acao }: { k: ContratoPatrocinio; titulo?: string; acao?: React.ReactNode }) {
  return (
    <div className={`patrocinio-cartao${acao ? '' : ' assinado'}`}>
      {titulo && <div className="painel-titulo">{titulo}</div>}
      <div className="patrocinio-topo">
        <div className="patrocinio-empresa">{k.empresa}</div>
        <div className="patrocinio-perfil">{k.perfil}</div>
      </div>
      <div className="patrocinio-valor">
        {k.semanal} <span className="tag-fraco">por semana · {k.temporadas}</span>
      </div>
      <div className="tag-fraco">cerca de {k.ano} no ano</div>
      {k.bonus ? (
        <div className="patrocinio-bonus">
          + bonus de {k.bonus} pela meta: {k.meta}
        </div>
      ) : (
        <div className="tag-fraco">sem bonus</div>
      )}
      {acao}
    </div>
  )
}

// parcela da tabela Price, igual a do motor (eng.parcela_credito), so para a previa
function parcelaPrice(valor: number, meses: number, juros: number): number {
  return Math.round((valor * juros) / (1 - (1 + juros) ** -meses))
}

function BlocoCredito({ cr, ocupado, aoTomar, aoQuitar }: {
  cr: TelaFinancas['credito']
  ocupado: boolean
  aoTomar: (valor: number, meses: number) => void
  aoQuitar: () => void
}) {
  const [valor, setValor] = useState(0)
  const [meses, setMeses] = useState(cr.prazos[1]?.meses ?? 12)
  if (cr.ativo) {
    const a = cr.ativo
    return (
      <section className={`painel faixa ${a.atrasos ? 'critico' : 'atencao'}`}>
        <div className="faixa-icone">{iconeDeEstado(a.atrasos ? 'critico' : 'atencao')}</div>
        <div className="encolhe">
          <div className="faixa-titulo">
            Credito em aberto: {a.restantes} de {a.meses} parcelas de {a.parcela}
          </div>
          <div className="faixa-detalhe">
            tomou {a.valor} a {cr.juros} · saldo devedor {a.saldo}
            {a.atrasos > 0 &&
              ` · ${a.atrasos} ${a.atrasos === 1 ? 'parcela atrasada' : 'parcelas atrasadas'}: juro e multa entraram no saldo`}
          </div>
        </div>
        <div className="espaco" />
        <button type="button" className="bt-fantasma" disabled={ocupado} onClick={aoQuitar}>
          Quitar ({a.quitar})
        </button>
      </section>
    )
  }
  const juros = parseFloat(cr.juros) / 100
  const cabe = valor >= (cr.minimo_num ?? 0) && valor <= cr.limite_num
  return (
    <section className="painel enxuto">
      <div className="painel-titulo">Credito do clube</div>
      <p className="tag-fraco m-0 mb-3">
        O banco empresta ate {cr.limite} (3 meses de receita) a {cr.juros}, em parcelas fixas que saem
        na virada do mes. Sem caixa para a parcela, ela atrasa: juro e multa vao para o saldo e a
        diretoria cobra.
      </p>
      <div className="linha-flex larga">
        <CampoDinheiro rotulo="Valor" valor={valor} aoMudar={setValor} maximo={cr.limite_num} />
        <label className="campo-rotulo">
          Prazo
          <select className="seletor" value={meses} onChange={(e) => setMeses(Number(e.target.value))}>
            {cr.prazos.map((p) => (
              <option key={p.meses} value={p.meses}>
                {p.meses} meses
              </option>
            ))}
          </select>
        </label>
        <span className="tag-fraco">
          {valor > 0 ? `parcela de R$ ${parcelaPrice(valor, meses, juros).toLocaleString('pt-BR')} por mes` : ''}
        </span>
        <div className="espaco" />
        <button type="button" className="bt-acao" disabled={ocupado || !cabe} onClick={() => aoTomar(valor, meses)}>
          Tomar credito
        </button>
      </div>
    </section>
  )
}

function BlocoBicho({ b, ocupado, aoMudar }: { b: TelaFinancas['bicho']; ocupado: boolean; aoMudar: (nivel: string) => void }) {
  const atual = b.niveis.find((n) => n.id === b.nivel)
  return (
    <section className="painel enxuto">
      <div className="painel-titulo">Bicho por vitoria</div>
      <p className="tag-fraco m-0 mb-3">
        O premio que voce promete ao elenco. Sai do caixa a cada vitoria (uma fatia da folha semanal) e
        da moral extra a quem entrou em campo.
      </p>
      <div className="linha-flex larga">
        <label className="campo-rotulo">
          Nivel
          <select
            className="seletor"
            value={b.nivel}
            disabled={ocupado}
            onChange={(e) => aoMudar(e.target.value)}
          >
            {b.niveis.map((n) => (
              <option key={n.id} value={n.id}>
                {n.id === 'nenhum' ? n.rotulo : `${n.rotulo}: ${n.custo} por vitoria, +${n.moral} de moral`}
              </option>
            ))}
          </select>
        </label>
        <span className="tag-fraco">
          {atual && atual.id !== 'nenhum'
            ? `cada vitoria custa ${atual.custo} e da +${atual.moral} de moral a quem jogou`
            : 'vitoria vale so a moral do resultado'}
        </span>
      </div>
    </section>
  )
}

interface Props {
  tela: TelaFinancas
  ocupado: boolean
  aoAssinarPatrocinio: (espaco: string, indice: number) => void
  aoAssinarEquilibradas: () => void
  aoMudarBicho: (nivel: string) => void
  aoTomarCredito: (valor: number, meses: number) => void
  aoQuitarCredito: () => void
}

export function Financas({ tela, ocupado, aoAssinarPatrocinio, aoAssinarEquilibradas, aoMudarBicho, aoTomarCredito, aoQuitarCredito }: Props) {
  const ex = tela.extrato
  const pat = tela.patrocinio
  const blocoPatrocinio = (
    <>
      <div className="painel-titulo">Patrocinio</div>
        <section className="painel enxuto">
          <p className="tag-fraco m-0 mb-3">{pat.explica}</p>
          {pat.vagos.length > 1 && (
            <div className="linha-flex larga mb-3">
              <span className="tag-fraco">
                {pat.vagos.length} espacos vagos. Sem tempo para escolher um por um?
              </span>
              <div className="espaco" />
              <button
                type="button"
                className="bt-acao"
                title={porque([[ocupado, AGUARDE]])}
                disabled={ocupado}
                onClick={aoAssinarEquilibradas}
              >
                Assinar as equilibradas de todos
              </button>
            </div>
          )}
          {pat.contratos.length > 0 && (
            <div className="patrocinio-grade">
              {pat.contratos.map((k) => (
                <CartaoPatrocinio key={k.espaco} k={k} titulo={k.nome} />
              ))}
            </div>
          )}
          {pat.vagos.map((v) => (
            <div key={v.espaco} className="mt-3">
              <div className="painel-titulo mb-2">{v.nome}: escolha uma proposta</div>
              <div className="patrocinio-grade">
                {v.ofertas.map((o) => (
                  <CartaoPatrocinio
                    key={o.indice}
                    k={o}
                    acao={
                      <button
                        type="button"
                        className="bt-acao medio mt-2"
                        title={porque([[ocupado, AGUARDE]])}
                        disabled={ocupado}
                        onClick={() => aoAssinarPatrocinio(v.espaco, o.indice)}
                      >
                        Assinar
                      </button>
                    }
                  />
                ))}
              </div>
            </div>
          ))}
        </section>
    </>
  )
  const metricas = [
    { nome: 'Caixa', valor: ex.caixa, estado: undefined },
    { nome: 'Verba p/ contratar', valor: tela.mensal.verba, estado: tela.mensal.estado },
    { nome: 'Saldo do mes', valor: tela.mensal.linhas.find((l) => l.destaque)?.valor ?? '-', estado: tela.mensal.linhas.find((l) => l.destaque)?.estado },
    { nome: 'Resultado do ano', valor: ex.resultado, estado: ex.estado },
  ] as Metrica[]
  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={`temporada ${ex.temporada}: de onde veio e para onde foi o dinheiro`} metricas={metricas} />

      {/* espaco vago: a escolha e a primeira coisa da tela */}
      {pat.vagos.length > 0 && blocoPatrocinio}

      <BlocoCredito cr={tela.credito} ocupado={ocupado} aoTomar={aoTomarCredito} aoQuitar={aoQuitarCredito} />

      <BlocoBicho b={tela.bicho} ocupado={ocupado} aoMudar={aoMudarBicho} />

      <div className="painel-titulo">O mes e a verba para contratar</div>
      <div className="financas-resumo">
        <section className="painel enxuto">
          <div className="painel-titulo mb-2">Mes tipico: entra contra sai</div>
          <Fluxo linhas={tela.mensal.linhas} />
        </section>
        <section className="painel enxuto">
          <div className="painel-titulo mb-2">Caixa e verba</div>
          <MedidorVerba m={tela.mensal} />
          <p className="verba-explica">
            {tela.mensal.explica}
            {tela.mensal.queima && (
              <>
                {' '}
                <span className="tag-critico">{tela.mensal.queima}</span>
              </>
            )}
          </p>
        </section>
      </div>

      <div className="painel-titulo">
        Extrato da temporada: caixa {ex.caixa_ini} no comeco, {ex.caixa} agora
      </div>
      <div className="financas-colunas">
        <section className="painel corte">
          <div className="painel-titulo cab-tabela">Entrou</div>
          <Linhas linhas={ex.entradas} total={{ rotulo: 'Total que entrou', valor: somaDe(ex.entradas), estado: 'ok' }} />
        </section>
        <section className="painel corte">
          <div className="painel-titulo cab-tabela">Saiu</div>
          <Linhas linhas={ex.saidas} total={{ rotulo: 'Total que saiu', valor: -somaDe(ex.saidas), estado: somaDe(ex.saidas) > 0 ? 'critico' : undefined }} />
        </section>
      </div>

      <div className="financas-colunas">
        <section className="painel corte">
          <div className="painel-titulo cab-tabela">Toda semana (sem bilheteria e premio)</div>
          <Linhas linhas={tela.linhas} />
        </section>
        <section className="painel corte">
          <div className="painel-titulo cab-tabela">Premiacao em jogo</div>
          {tela.premiacao.length ? (
            <Linhas linhas={tela.premiacao} />
          ) : (
            <p className="verba-explica">Nenhuma premiacao em disputa agora.</p>
          )}
        </section>
      </div>

      {pat.vagos.length === 0 && blocoPatrocinio}

      <div className="painel-titulo">
        Elenco: {tela.elenco.jogadores} jogadores · valor de mercado {tela.elenco.valor} · folha {tela.elenco.folha_mes} por mes
        {tela.elenco.emprestados > 0 && ` · ${tela.elenco.emprestados} emprestados aqui (valor nao conta)`}
      </div>
      <section className="painel corte">
        <Grade colunas={COLUNAS} itens={tela.maiores} idDe={(j) => j.id} vazio="Elenco vazio." />
      </section>
    </div>
  )
}
