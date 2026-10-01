// Ingresso e obra.
//
// A conta da obra aparece enquanto se digita, mas e so leitura: quem cobra e
// o servidor, que refaz o calculo e pede confirmacao com o numero dele. Os
// limites tambem vem de la - a tela nao sabe sozinha que o ingresso vai de
// R$ 5 a R$ 300.

import { porque, AGUARDE } from '../motivo'
import { useEffect, useState } from 'react'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import { dinheiro as reais, plural } from '../formato'
import type { TelaEstadio } from '../tipos'

export type AcaoEstadio = { tipo: 'preco'; preco: number } | { tipo: 'obra'; lugares: number }

interface Props {
  tela: TelaEstadio
  ocupado: boolean
  aoAgir: (acao: AcaoEstadio) => void
}

/** "34.679 pessoas" -> 34679 (o ponto e de milhar, nao decimal). */
function inteiroDe(texto: string): number {
  const m = /^[\d.]+/.exec(texto.trim())
  return m ? Number.parseInt(m[0].replace(/\./g, ''), 10) || 0 : 0
}

export function Estadio({ tela, ocupado, aoAgir }: Props) {
  const [preco, setPreco] = useState(String(tela.preco))
  const [lugares, setLugares] = useState('')

  // a tela voltou do servidor com o preco valendo: o campo segue ele
  useEffect(() => {
    setPreco(String(tela.preco))
  }, [tela.preco])

  const precoNum = Number.parseInt(preco, 10)
  const precoValido = Number.isFinite(precoNum) && precoNum >= tela.preco_min && precoNum <= tela.preco_max

  const lugaresNum = Number.parseInt(lugares, 10)
  const lugaresValido =
    Number.isFinite(lugaresNum) && lugaresNum >= tela.lugares_min && lugaresNum <= tela.lugares_max
  const custo = lugaresValido ? lugaresNum * tela.custo_lugar : 0
  const semanas = lugaresValido ? Math.max(2, Math.floor(lugaresNum / 1500)) : 0
  const cabe = custo <= tela.caixa_num

  let previa = `entre ${tela.lugares_min.toLocaleString('pt-BR')} e ${tela.lugares_max.toLocaleString('pt-BR')} lugares`
  if (lugaresValido) {
    previa = `${reais(custo)} · pronta em ${semanas} semanas`
    if (!cabe) previa += ` · faltam ${reais(custo - tela.caixa_num)} no caixa`
  }

  const lugaresTotal = inteiroDe(String(tela.metricas.find((m) => m.nome === 'lugares')?.valor ?? ''))
  const torcida = inteiroDe(tela.rendimento.find((l) => l.nome.startsWith('Torcida'))?.valor ?? '')
  const ocupacao = lugaresTotal > 0 && torcida > 0 ? Math.min(100, Math.round((torcida / lugaresTotal) * 100)) : 0
  // o preco no controle deslizante acompanha o campo de texto
  const posicao = Number.isFinite(precoNum) ? Math.min(tela.preco_max, Math.max(tela.preco_min, precoNum)) : tela.preco

  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={tela.subtitulo} metricas={tela.metricas} />

      {ocupacao > 0 && (
        <section className="painel estadio-lotacao" aria-label="Lotacao tipica">
          <div className="estadio-lotacao-cab">
            <span className="painel-titulo">Lotacao de um jogo comum</span>
            <strong className={ocupacao >= 85 ? 'ok' : ocupacao >= 60 ? 'atencao' : 'critico'}>{ocupacao}%</strong>
          </div>
          <div className="estadio-arquibancada" role="img" aria-label={`${torcida.toLocaleString('pt-BR')} de ${lugaresTotal.toLocaleString('pt-BR')} lugares`}>
            <i style={{ width: `${ocupacao}%` }} />
          </div>
          <div className="estadio-lotacao-nota">
            {torcida.toLocaleString('pt-BR')} pessoas em {lugaresTotal.toLocaleString('pt-BR')} lugares
            {ocupacao < 60 ? ': lugar sobrando so custa manutencao' : ocupacao >= 95 ? ': casa cheia, da para subir o ingresso ou ampliar' : ''}
          </div>
        </section>
      )}

      <div className="estadio-grade">
      <section className="painel corte financas-colunas-unica" aria-label="Como o estadio esta rendendo">
        <div className="painel-titulo cab-tabela">Como o estadio esta rendendo</div>
        {tela.rendimento.map((l) => (
          <div className="linha-valor" key={l.nome}>
            <span className="rot">
              {l.nome}
              {l.dica && <span className="linha-dica">{l.dica}</span>}
            </span>
            <span className={`val ${l.estado ?? ''}`}>{l.valor}</span>
          </div>
        ))}
      </section>

      <div className="estadio-acoes">
      <section className="cartao">
        <div className="titulo">Preco do ingresso</div>
        <div className="desc">
          Caro afasta publico, barato enche o estadio. Vale de R$ {tela.preco_min} a R$ {tela.preco_max}.
        </div>
        <form
          className="linha-form"
          onSubmit={(e) => {
            e.preventDefault()
            if (precoValido) aoAgir({ tipo: 'preco', preco: precoNum })
          }}
        >
          <label className="campo-rotulo">
            Novo preco (R$)
            <input
              className="seletor entrada"
              inputMode="numeric"
              value={preco}
              onChange={(e) => setPreco(e.target.value.replace(/\D/g, ''))}
              aria-invalid={!precoValido}
            />
          </label>
          <input
            type="range"
            className="estadio-deslizante"
            aria-label="Preco do ingresso"
            min={tela.preco_min}
            max={tela.preco_max}
            value={posicao}
            onChange={(e) => setPreco(e.target.value)}
          />
          <button
            type="submit"
            className="bt-acao bt-media"
            title={porque([[ocupado, AGUARDE], [!precoValido, 'Preco fora da faixa permitida'], [precoNum === tela.preco, 'Esse ja e o preco atual']])}
            disabled={ocupado || !precoValido || precoNum === tela.preco}
          >
            Aplicar preco
          </button>
          {!precoValido && preco !== '' && (
            <span className="linha-critica txt-p">
              fora do limite de R$ {tela.preco_min} a R$ {tela.preco_max}
            </span>
          )}
        </form>
      </section>

      <section className="cartao">
        <div className="titulo">Ampliar o estadio</div>
        <div className="desc">
          {reais(tela.custo_lugar)} por lugar, uma semana de obra a cada 1.500 lugares. Caixa: {tela.caixa}.
        </div>
        {tela.obra ? (
          <div className="aviso-obra">
            Obra em andamento: +{tela.obra.lugares} lugares, faltam {plural(tela.obra.semanas, 'semana')}. Uma obra
            por vez.
          </div>
        ) : (
          <form
            className="linha-form"
            onSubmit={(e) => {
              e.preventDefault()
              if (lugaresValido && cabe) aoAgir({ tipo: 'obra', lugares: lugaresNum })
            }}
          >
            <label className="campo-rotulo">
              Lugares a mais
              <input
                className="seletor entrada"
                inputMode="numeric"
                placeholder="ex.: 3000"
                value={lugares}
                onChange={(e) => setLugares(e.target.value.replace(/\D/g, ''))}
              />
            </label>
            <button
              type="submit"
              className="bt-acao bt-media"
              title={porque([[ocupado, AGUARDE], [!lugaresValido, 'Quantidade de lugares fora da faixa'], [!cabe, 'Caixa insuficiente para a obra']])}
              disabled={ocupado || !lugaresValido || !cabe}
            >
              Contratar obra
            </button>
            <span className={`${lugaresValido && !cabe ? 'linha-critica' : 'tag-fraco'} txt-p`}>
              {previa}
            </span>
          </form>
        )}
      </section>
      </div>
      </div>
    </div>
  )
}
