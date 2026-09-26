// O dinheiro do clube em quatro perguntas: como foi o ano ate agora (o
// extrato, que fecha com o caixa), o que entra e sai toda semana, quanto
// ainda da para ganhar de premio, e quanto sobra para contratar.
//
// Cada linha diz de onde vem o dinheiro. A verba e o caixa menos a folha
// guardada - gastando so ela, o clube nunca fica sem pagar salario.

import { useState } from 'react'
import { CampoDinheiro } from '../componentes/CampoDinheiro'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import { Grade, type Coluna } from '../componentes/Grade'
import { iconeDeEstado } from '../icones'
import { porque, AGUARDE } from '../motivo'
import type { ContratoPatrocinio, LinhaDinheiro, TelaFinancas } from '../tipos'

type Maior = TelaFinancas['maiores'][number]

const COLUNAS: Coluna<Maior>[] = [
  { chave: 'nome', rotulo: 'Jogador', largura: 'minmax(150px, 2fr)', classe: 'corta', render: (j) => j.nome },
  { chave: 'pos', rotulo: 'Pos', largura: '46px', classe: 'centro', render: (j) => j.pos },
  { chave: 'sal', rotulo: 'Salario por mes', largura: '130px', classe: 'num', render: (j) => j.salario },
  { chave: 'val', rotulo: 'Valor', largura: '110px', classe: 'num', render: (j) => j.valor },
  { chave: 'obs', rotulo: 'Observacao', largura: 'minmax(120px, 1.4fr)', classe: 'corta', render: (j) => j.obs },
]

function Linhas({ linhas }: { linhas: LinhaDinheiro[] }) {
  return (
    <>
      {linhas.map((l) => (
        <div className={`linha-valor${l.destaque ? ' total' : ''}`} key={l.nome}>
          <span className="rot">
            {l.nome}
            {l.dica && <span className="linha-dica">{l.dica}</span>}
          </span>
          <span className={`val ${l.estado ?? ''}`}>{l.valor}</span>
        </div>
      ))}
    </>
  )
}

function CartaoPatrocinio({ k, titulo, acao }: { k: ContratoPatrocinio; titulo?: string; acao?: React.ReactNode }) {
  return (
    <div className="patrocinio-cartao">
      {titulo && <div className="painel-titulo">{titulo}</div>}
      <div className="patrocinio-empresa">{k.empresa}</div>
      <div className="patrocinio-perfil">{k.perfil}</div>
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
            {a.atrasos > 0 && ` · ${a.atrasos} parcela(s) atrasada(s): juro e multa entraram no saldo`}
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

interface Props {
  tela: TelaFinancas
  ocupado: boolean
  aoAssinarPatrocinio: (espaco: string, indice: number) => void
  aoTomarCredito: (valor: number, meses: number) => void
  aoQuitarCredito: () => void
}

export function Financas({ tela, ocupado, aoAssinarPatrocinio, aoTomarCredito, aoQuitarCredito }: Props) {
  const ex = tela.extrato
  const pat = tela.patrocinio
  const blocoPatrocinio = (
    <>
      <div className="painel-titulo">Patrocinio</div>
        <section className="painel enxuto">
          <p className="tag-fraco m-0 mb-3">{pat.explica}</p>
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
  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={`temporada ${ex.temporada}: de onde veio e para onde foi o dinheiro`} />

      {/* espaco vago: a escolha e a primeira coisa da tela */}
      {pat.vagos.length > 0 && blocoPatrocinio}

      <section className={`painel faixa ${ex.estado}`}>
        <div className="faixa-icone">{iconeDeEstado(ex.estado)}</div>
        <div>
          <div className="faixa-titulo">Resultado do ano ate agora: {ex.resultado}</div>
          <div className="faixa-detalhe">
            caixa no comeco do ano {ex.caixa_ini} · caixa agora {ex.caixa}
          </div>
        </div>
      </section>

      <BlocoCredito cr={tela.credito} ocupado={ocupado} aoTomar={aoTomarCredito} aoQuitar={aoQuitarCredito} />

      <div className="financas-colunas">
        <section className="painel corte">
          <div className="painel-titulo cab-tabela">Entrou</div>
          <Linhas linhas={ex.entradas} />
        </section>
        <section className="painel corte">
          <div className="painel-titulo cab-tabela">Saiu</div>
          <Linhas linhas={ex.saidas} />
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

      <div className="painel-titulo">O mes e a verba para contratar</div>
      <section className={`painel faixa ${tela.mensal.estado}`}>
        <div className="faixa-icone">{iconeDeEstado(tela.mensal.estado)}</div>
        <div>
          <div className="faixa-titulo">Verba para contratar: {tela.mensal.verba}</div>
          <div className="faixa-detalhe">
            caixa {tela.mensal.caixa} · reservado {tela.mensal.reserva} ({tela.mensal.meses} meses de folha e custos)
          </div>
        </div>
      </section>
      <section className="painel corte">
        <Linhas linhas={tela.mensal.linhas} />
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
