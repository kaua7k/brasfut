// Tres areas para investir, cada uma com o que ela muda no jogo escrito junto.
//
// O preco vem calculado do servidor, e e la que ele e cobrado: a tela nunca
// manda o valor a pagar, senao daria para comprar o nivel 10 pelo preco do 1.

import { porque, AGUARDE } from '../motivo'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import { chaveDeOrdem } from '../componentes/Grade'
import type { TelaInfra } from '../tipos'

interface Props {
  tela: TelaInfra
  ocupado: boolean
  aoInvestir: (id: string) => void
}

export function Infra({ tela, ocupado, aoInvestir }: Props) {
  // o caixa so vem escrito no subtitulo ("caixa R$ 30,4 mi"): a barra de quanto
  // dele cobre o proximo nivel e so leitura, quem cobra e o servidor
  const lido = chaveDeOrdem(tela.subtitulo.replace(/^caixa\s*/i, ''))
  const caixa = typeof lido === 'number' ? lido : 0
  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={tela.subtitulo} />

      <div className="infra-grade">
        {tela.itens.map((it) => {
          const preco = it.custo_num ?? 0
          const cobre = preco > 0 && caixa > 0 ? Math.min(100, Math.round((caixa / preco) * 100)) : 0
          return (
            <section className={`infra-cartao${it.custo === null ? ' maximo' : ''}`} key={it.id}>
              <div className="infra-topo">
                <div className="infra-textos">
                  <div className="infra-nome">{it.nome}</div>
                  <div className="infra-desc">{it.descricao}</div>
                </div>
                <div className="infra-nivel-num" aria-label={`nivel ${it.nivel} de ${it.maximo}`}>
                  <b>{it.nivel}</b>
                  <span>/{it.maximo}</span>
                </div>
              </div>

              <div className="nivel infra-medidor" aria-hidden="true">
                {Array.from({ length: it.maximo }, (_, i) => (
                  <i key={i} className={i < it.nivel ? 'cheio' : i === it.nivel && it.custo !== null ? 'proximo' : undefined} />
                ))}
              </div>

              {it.custo === null ? (
                <div className="infra-maximo">Nivel maximo: nada mais a investir aqui</div>
              ) : (
                <div className="infra-rodape">
                  <div className="infra-custo">
                    <span className="infra-custo-rotulo">Nivel {it.nivel + 1}</span>
                    <strong className={it.pode_pagar ? '' : 'falta'}>{it.custo}</strong>
                    {!it.pode_pagar && cobre > 0 && (
                      <span className="infra-cobre">
                        <i style={{ width: `${cobre}%` }} />
                      </span>
                    )}
                    <span className="infra-custo-nota">
                      {it.pode_pagar ? 'cabe no caixa' : `o caixa cobre ${cobre}%`}
                    </span>
                  </div>
                  <button
                    type="button"
                    className={it.pode_pagar ? 'bt-acao bt-media' : 'bt-fantasma'}
                    title={porque([[ocupado, AGUARDE], [!it.pode_pagar, 'Caixa insuficiente para este nivel']], it.pode_pagar ? undefined : 'caixa insuficiente')}
                    disabled={ocupado || !it.pode_pagar}
                    onClick={() => aoInvestir(it.id)}
                  >
                    Subir de nivel
                  </button>
                </div>
              )}
            </section>
          )
        })}
      </div>
    </div>
  )
}
