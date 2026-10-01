// Vitrine em lote: precifica e lista varios jogadores de uma vez.
//
// O jeito rapido sao os botoes de percentual: cada um recebe o preco
// proporcional ao SEU valor de mercado (calculado no servidor), e nao um preco
// igual para todos. Da para ajustar linha a linha antes de confirmar. Pôr na
// vitrine nao cobra nada e se desfaz com um clique, por isso nao ha pergunta
// de confirmacao no fim.

import { porque, AGUARDE } from '../motivo'
import { useEffect, useState } from 'react'
import { api, ErroDaApi } from '../api'
import { dinheiro as reais, plural } from '../formato'
import type { LinhaPrecoVitrine } from '../tipos'
import { CampoDinheiro } from './CampoDinheiro'

interface Props {
  ids: number[]
  ocupado: boolean
  aoConfirmar: (precos: { id: number; preco: number }[]) => void
  aoFechar: () => void
}

const PERCENTUAIS = [
  { pct: 90, rotulo: 'saida rapida 90%' },
  { pct: 100, rotulo: 'mercado 100%' },
  { pct: 130, rotulo: 'com lucro 130%' },
  { pct: 200, rotulo: 'so por muito 200%' },
]

export function DialogoVitrine({ ids, ocupado, aoConfirmar, aoFechar }: Props) {
  const [linhas, setLinhas] = useState<LinhaPrecoVitrine[]>([])
  const [precos, setPrecos] = useState<Record<number, number>>({})
  const [fixo, setFixo] = useState(0)
  const [erro, setErro] = useState<string | null>(null)

  useEffect(() => {
    api
      .linhasVitrine(ids)
      .then((r) => {
        setLinhas(r.linhas)
        setPrecos(Object.fromEntries(r.linhas.map((l) => [l.id, l.preco])))
      })
      .catch((e) => setErro(e instanceof ErroDaApi ? e.message : String(e)))
  }, [ids])

  const aplicarPct = async (pct: number) => {
    try {
      const r = await api.sugerirPrecos(linhas.map((l) => l.id), pct)
      setPrecos((p) => ({ ...p, ...Object.fromEntries(r.precos.map((x) => [x.id, x.preco])) }))
    } catch (e) {
      setErro(e instanceof ErroDaApi ? e.message : String(e))
    }
  }

  const total = linhas.reduce((s, l) => s + (precos[l.id] ?? 0), 0)
  const folha = linhas.reduce((s, l) => s + l.salario_num, 0)
  const invalidos = linhas.filter((l) => (precos[l.id] ?? 0) < 1000)

  return (
    <div
      className="fundo-modal"
      role="dialog"
      aria-modal="true"
      aria-label="Por a venda"
      onKeyDown={(e) => e.key === 'Escape' && aoFechar()}
    >
      <div className="modal modal-largo dlg">
        <header className="dlg-cab">
          <div className="dlg-textos">
            <div className="dlg-kicker">Vitrine em lote</div>
            <h2>Por a venda</h2>
            <div className="dlg-sub">
              Pedir muito acima do valor afasta proposta; abaixo, elas chegam rapido.
            </div>
          </div>
          <div className="dlg-selo">{plural(linhas.length, 'jogador', 'jogadores')}</div>
        </header>
        <div className="dlg-corpo">

        <div className="painel-titulo">Preco como percentual do valor de mercado</div>
        <div className="atalhos mt-2 mb-3">
          {PERCENTUAIS.map((p) => (
            <button key={p.pct} type="button" className="bt-fantasma bt-mini" onClick={() => aplicarPct(p.pct)}>
              {p.rotulo}
            </button>
          ))}
        </div>

        <div className="vitrine-linhas" role="table">
          <div className="vitrine-linha cab" role="row">
            <span role="columnheader">Jogador</span>
            <span role="columnheader">Valor</span>
            <span role="columnheader">Voce pede</span>
            <span role="columnheader" className="num">%</span>
          </div>
          {linhas.map((l) => {
            const preco = precos[l.id] ?? 0
            return (
              <div className="vitrine-linha" role="row" key={l.id}>
                <span role="cell" className="corta">
                  <span className={`tag-${l.tag}`}>{l.nome}</span>{' '}
                  <span className="tag-fraco">
                    {l.pos} · {l.ovr} · {plural(l.contrato, 'ano')}
                  </span>
                </span>
                <span role="cell" className="tag-fraco">{l.valor}</span>
                <span role="cell">
                  <CampoDinheiro
                    rotulo={`Preco de ${l.nome}`}
                    valor={preco}
                    aoMudar={(v) => setPrecos((p) => ({ ...p, [l.id]: v }))}
                  />
                </span>
                <span role="cell" className="num">{Math.round((100 * preco) / Math.max(1, l.valor_num))}%</span>
              </div>
            )
          })}
        </div>

        <div className="linha-form">
          <CampoDinheiro rotulo="Preco fixo para todos" valor={fixo} aoMudar={setFixo} />
          <button
            type="button"
            className="bt-fantasma"
            title={porque([[fixo < 1000, 'O preco minimo de vitrine e R$ 1.000']])}
            disabled={fixo < 1000}
            onClick={() => setPrecos(Object.fromEntries(linhas.map((l) => [l.id, fixo])))}
          >
            Aplicar a todos
          </button>
        </div>

        <div className="totais">
          <div className="total-cel principal">
            <span>Pedido somado</span>
            <b>{reais(total)}</b>
            <small>se todos forem vendidos</small>
          </div>
          <div className="total-cel">
            <span>Folha que sairia</span>
            <b>{reais(folha)}</b>
            <small>por mes</small>
          </div>
        </div>
        {invalidos.length > 0 && (
          <div className="mesa-linha linha-critica">O preco minimo de vitrine e R$ 1 mil.</div>
        )}
        {erro && <div className="mesa-linha linha-critica">{erro}</div>}
        </div>

        <div className="modal-acoes">
          <button type="button" className="bt-fantasma bt-media" onClick={aoFechar}>
            Cancelar
          </button>
          <button
            type="button"
            className="bt-acao bt-media"
            title={porque([[ocupado, AGUARDE], [!linhas.length, 'Ninguem para por na vitrine'], [invalidos.length > 0, 'Algum preco esta abaixo de R$ 1.000']])}
            disabled={ocupado || !linhas.length || invalidos.length > 0}
            onClick={() => aoConfirmar(linhas.map((l) => ({ id: l.id, preco: precos[l.id] })))}
          >
            Por na vitrine
          </button>
        </div>
      </div>
    </div>
  )
}
