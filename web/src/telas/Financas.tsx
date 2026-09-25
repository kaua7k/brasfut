// O dinheiro do clube em quatro perguntas: como foi o ano ate agora (o
// extrato, que fecha com o caixa), o que entra e sai toda semana, quanto
// ainda da para ganhar de premio, e quanto sobra para contratar.
//
// Cada linha diz de onde vem o dinheiro. A verba e o caixa menos a folha
// guardada - gastando so ela, o clube nunca fica sem pagar salario.

import { CabecalhoTela } from '../componentes/CabecalhoTela'
import { Grade, type Coluna } from '../componentes/Grade'
import { iconeDeEstado } from '../icones'
import type { LinhaDinheiro, TelaFinancas } from '../tipos'

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

export function Financas({ tela }: { tela: TelaFinancas }) {
  const ex = tela.extrato
  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={`temporada ${ex.temporada}: de onde veio e para onde foi o dinheiro`} />

      <section className={`painel faixa ${ex.estado}`}>
        <div className="faixa-icone">{iconeDeEstado(ex.estado)}</div>
        <div>
          <div className="faixa-titulo">Resultado do ano ate agora: {ex.resultado}</div>
          <div className="faixa-detalhe">
            caixa no comeco do ano {ex.caixa_ini} · caixa agora {ex.caixa}
          </div>
        </div>
      </section>

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
