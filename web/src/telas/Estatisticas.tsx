// O guia do campeonato: quem faz gol, quem da passe, quem joga bem, quem apanha
// cartao, e os ataques e defesas. A nota e a do jogo (6.0 = correto), com a
// escada de cor dos sites de estatistica.

import { CabecalhoTela } from '../componentes/CabecalhoTela'
import { seloPos } from '../componentes/Celulas'
import { Escudo } from '../componentes/Escudo'
import type { RankingEstat, TelaEstatisticas } from '../tipos'

interface Props {
  tela: TelaEstatisticas
  aoAbrirFicha: (id: number) => void
  aoTrocar: (alvo: string) => void
}

function classeNota(v: number) {
  if (v >= 8) return 'nota-otima'
  if (v >= 7) return 'nota-boa'
  if (v >= 6.5) return 'nota-media'
  return 'nota-fraca'
}

function Ranking({ r, aoAbrirFicha }: { r: RankingEstat; aoAbrirFicha: (id: number) => void }) {
  const deTime = r.id === 'ataque' || r.id === 'defesa'
  return (
    <section className="painel enxuto estat-card">
      <div className="estat-cab">
        <span className="painel-titulo">{r.titulo}</span>
        {r.sub && <span className="tag-fraco">{r.sub}</span>}
      </div>
      {r.itens.length === 0 ? (
        <div className="vazio justo">Ninguem ainda.</div>
      ) : (
        <ol className="estat-lista">
          {r.itens.map((i, k) => (
            <li key={i.id} className={`${i.meu ? 'meu' : ''}${k === 0 ? ' lider' : ''}`}>
              <span className="estat-pos">{k + 1}</span>
              <Escudo nome={i.clube} tamanho={18} />
              {deTime ? (
                <span className="estat-nome">{i.nome}</span>
              ) : (
                <button type="button" className="bt-link estat-nome" onClick={() => aoAbrirFicha(i.id)}>
                  {i.nome}
                </button>
              )}
              {!deTime && seloPos(i.pos)}
              <span className="tag-fraco estat-jogos">{i.jogos} j</span>
              <span className={`estat-valor ${r.id === 'nota' ? classeNota(i.num) : ''}`}>{i.valor}</span>
            </li>
          ))}
        </ol>
      )}
    </section>
  )
}

export function Estatisticas({ tela, aoAbrirFicha, aoTrocar }: Props) {
  const grupos = [...new Set(tela.torneios.map((t) => t.grupo))]
  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={tela.subtitulo}>
        <label className="clube-seletor">
          <span className="tag-fraco">Liga</span>
          <select value={tela.alvo} onChange={(e) => aoTrocar(e.target.value)}>
            {grupos.map((g) => (
              <optgroup key={g} label={g}>
                {tela.torneios
                  .filter((t) => t.grupo === g)
                  .map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.nome}
                    </option>
                  ))}
              </optgroup>
            ))}
          </select>
        </label>
      </CabecalhoTela>
      <div className="estat-grade">
        {tela.rankings.map((r) => (
          <Ranking key={r.id} r={r} aoAbrirFicha={aoAbrirFicha} />
        ))}
      </div>
    </div>
  )
}
