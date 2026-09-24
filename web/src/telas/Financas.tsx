// O caixa da semana em seis linhas, o mes com a verba de contratar, e depois
// quem pesa na folha.
//
// A conta que interessa e o saldo: com ele negativo, a reserva esta sendo
// queimada mesmo que o caixa ainda pareca grande. E a verba e o caixa menos a
// folha guardada - gastando so ela, o clube nunca fica sem pagar salario.

import { CabecalhoTela } from '../componentes/CabecalhoTela'
import { Grade, type Coluna } from '../componentes/Grade'
import { iconeDeEstado } from '../icones'
import type { TelaFinancas } from '../tipos'

type Maior = TelaFinancas['maiores'][number]

const COLUNAS: Coluna<Maior>[] = [
  { chave: 'nome', rotulo: 'Jogador', largura: 'minmax(150px, 2fr)', classe: 'corta', render: (j) => j.nome },
  { chave: 'pos', rotulo: 'Pos', largura: '46px', classe: 'centro', render: (j) => j.pos },
  { chave: 'sal', rotulo: 'Salario mensal', largura: '120px', classe: 'num', render: (j) => j.salario },
  { chave: 'obs', rotulo: 'Observacao', largura: 'minmax(120px, 1.4fr)', classe: 'corta', render: (j) => j.obs },
]

export function Financas({ tela }: { tela: TelaFinancas }) {
  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub="entra e sai, por semana" />

      <section className="painel" style={{ overflow: 'hidden' }}>
        {tela.linhas.map((l) => (
          <div className={`linha-valor${l.destaque ? ' total' : ''}`} key={l.nome}>
            <span className="rot">{l.nome}</span>
            <span className={`val ${l.estado}`}>{l.valor}</span>
          </div>
        ))}
      </section>

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
      <section className="painel" style={{ overflow: 'hidden' }}>
        {tela.mensal.linhas.map((l) => (
          <div className={`linha-valor${l.destaque ? ' total' : ''}`} key={l.nome}>
            <span className="rot">{l.nome}</span>
            <span className={`val ${l.estado}`}>{l.valor}</span>
          </div>
        ))}
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

      <div className="painel-titulo">Maiores salarios</div>
      <section className="painel" style={{ overflow: 'hidden' }}>
        <Grade colunas={COLUNAS} itens={tela.maiores} idDe={(j) => j.id} vazio="Elenco vazio." />
      </section>
    </div>
  )
}
