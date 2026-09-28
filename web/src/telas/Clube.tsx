// O clube por dentro: quem ele e, como esta agora e o que ja ganhou.
//
// A sala de trofeus soma dois passados: o real, ate 2025 (dados_clubes.py,
// editavel a mao), e o do jogo, que o motor grava com a temporada em cada
// titulo. O seletor do topo abre qualquer clube brasileiro, nao so o meu.

import { Escudo } from '../componentes/Escudo'
import { seloOvr, seloPos } from '../componentes/Celulas'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import type { TelaClube } from '../tipos'

interface Props {
  tela: TelaClube
  aoAbrirFicha: (id: number) => void
  aoTrocar: (id: number) => void
}

export function Clube({ tela, aoAbrirFicha, aoTrocar }: Props) {
  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={tela.subtitulo} metricas={tela.metricas}>
        <label className="clube-seletor">
          <span className="tag-fraco">Ver outro clube</span>
          <select value={tela.id} onChange={(e) => aoTrocar(Number(e.target.value))}>
            {['A', 'B', 'C', 'D'].map((d) => (
              <optgroup key={d} label={`Serie ${d}`}>
                {tela.clubes
                  .filter((c) => c.divisao === d)
                  .map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.nome}
                    </option>
                  ))}
              </optgroup>
            ))}
          </select>
        </label>
      </CabecalhoTela>

      <div className="clube-topo">
        <section className="painel enxuto">
          <div className="clube-identidade">
            <Escudo nome={tela.titulo} tamanho={64} />
            <div className="painel-titulo">Identidade</div>
          </div>
          <dl className="clube-info">
            {tela.info.map((i) => (
              <div key={i.nome}>
                <dt>{i.nome}</dt>
                <dd>{i.valor}</dd>
              </div>
            ))}
          </dl>
        </section>

        <section className="painel enxuto">
          <div className="painel-titulo mb-3">Elenco hoje</div>
          <ul className="clube-destaques">
            {tela.destaques.map((j) => (
              <li key={j.id}>
                <button type="button" className="bt-link" onClick={() => aoAbrirFicha(j.id)}>
                  {seloPos(j.pos)}
                  <span className="clube-jogador">{j.nome}</span>
                  <span className="tag-fraco">{j.idade} anos</span>
                  <span className="clube-ovr">{seloOvr(j.ovr)}</span>
                </button>
              </li>
            ))}
          </ul>
          {tela.artilheiro && (
            <div className="tag-fraco mt-2">
              Artilheiro do ano: {tela.artilheiro.nome}, {tela.artilheiro.gols} gols em {tela.artilheiro.jogos} jogos
            </div>
          )}
        </section>
      </div>

      <section className="painel enxuto">
        <div className="painel-titulo mb-3">Sala de trofeus</div>
        {tela.sala.length === 0 ? (
          <div className="vazio justo">Nenhum titulo ainda. O primeiro que vier fica aqui com o ano.</div>
        ) : (
          <ul className="clube-sala">
            {tela.sala.map((t) => (
              <li key={t.nome}>
                <span className="qtd">{t.qtd}</span>
                <div>
                  <div className="nome">{t.nome}</div>
                  <div className="anos">{t.anos}</div>
                </div>
              </li>
            ))}
          </ul>
        )}
        <div className="tag-fraco mt-2">
          {tela.tem_historia
            ? 'Historia real ate 2025 somada ao que o clube ganhou na sua carreira.'
            : 'Sem historia real cadastrada para este clube: aqui entra so o que ele ganhar no jogo.'}
        </div>
      </section>

      <section className="painel enxuto">
        <div className="painel-titulo mb-3">Conquistas no jogo</div>
        {tela.no_jogo.length === 0 ? (
          <div className="vazio justo">Nada ainda desde 2026.</div>
        ) : (
          <ol className="clube-linha-tempo">
            {tela.no_jogo.map((h, k) => (
              <li key={k}>
                <span className="ano">{h.temporada}</span>
                <span className="nome">★ {h.nome}</span>
              </li>
            ))}
          </ol>
        )}
      </section>
    </div>
  )
}
