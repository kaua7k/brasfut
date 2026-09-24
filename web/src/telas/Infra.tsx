// Tres areas para investir, cada uma com o que ela muda no jogo escrito junto.
//
// O preco vem calculado do servidor, e e la que ele e cobrado: a tela nunca
// manda o valor a pagar, senao daria para comprar o nivel 10 pelo preco do 1.

import { porque, AGUARDE } from '../motivo'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import type { TelaInfra } from '../tipos'

interface Props {
  tela: TelaInfra
  ocupado: boolean
  aoInvestir: (id: string) => void
}

export function Infra({ tela, ocupado, aoInvestir }: Props) {
  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={tela.subtitulo} />

      <div>
        {tela.itens.map((it) => (
          <section className="cartao" key={it.id}>
            <div className="titulo">
              {it.nome} — nivel {it.nivel} de {it.maximo}
            </div>
            <div className="desc">{it.descricao}</div>

            <div className="nivel" aria-hidden="true">
              {Array.from({ length: it.maximo }, (_, i) => (
                <i key={i} className={i < it.nivel ? 'cheio' : undefined} />
              ))}
            </div>

            {it.custo === null ? (
              <div style={{ fontSize: 12.5, fontWeight: 700, color: '#a78bfa' }}>nivel maximo</div>
            ) : (
              <button
                type="button"
                className="bt-fantasma"
                title={porque([[ocupado, AGUARDE], [!it.pode_pagar, 'Caixa insuficiente para este nivel']], it.pode_pagar ? undefined : 'caixa insuficiente')}
                disabled={ocupado || !it.pode_pagar}
                onClick={() => aoInvestir(it.id)}
              >
                Subir para o nivel {it.nivel + 1} por {it.custo}
              </button>
            )}
          </section>
        ))}
      </div>
    </div>
  )
}
