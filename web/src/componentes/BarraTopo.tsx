// A barra do topo carrega SO a acao da semana.
//
// A mesma regra da janela tkinter: com Salvar, Ajuda e Resumo aqui em cima a
// barra estourava e o caixa saia da tela. Salvar desceu para o pe do menu.

import { porque, AGUARDE } from '../motivo'
import { IconeGaveta, IconeSeta } from '../icones'
import { Escudo } from './Escudo'
import type { Cabecalho } from '../tipos'

interface Props {
  cabecalho: Cabecalho
  aoAvancar: () => void
  /** o jogo da semana ao vivo (liga para no intervalo) */
  aoJogar: () => void
  /** pula as semanas sem jogo e para antes do proximo */
  aoIrParaOJogo: () => void
  /** Abre o painel de ritmos: jogo a jogo, mes, janela, temporada. */
  aoSimular: () => void
  avancando: boolean
  /** Celular: o menu vira gaveta e este botao a abre (some na tela larga). */
  aoAbrirMenu?: () => void
  menuAberto?: boolean
}

export function BarraTopo({ cabecalho, aoAvancar, aoJogar, aoIrParaOJogo, aoSimular, avancando, aoAbrirMenu, menuAberto }: Props) {
  // durante a temporada o botao principal e o do jogo, como no Brasfoot: com
  // jogo na semana ele e "Jogar" (ao vivo); sem, "Ir para o jogo" pula ate ele.
  // Avancar semana fica ao lado, para quem quer andar rapido sem assistir.
  const emTemporada = cabecalho.fase === 'liga' || cabecalho.fase === 'estadual'
  const jogo = cabecalho.jogo_semana
  return (
    <header className="topo">
      {aoAbrirMenu && (
        <button
          type="button"
          className="bt-gaveta"
          aria-label="Abrir o menu"
          aria-controls="menu-lateral"
          aria-expanded={Boolean(menuAberto)}
          onClick={aoAbrirMenu}
        >
          <IconeGaveta />
        </button>
      )}
      <Escudo nome={cabecalho.clube} tamanho={40} />
      {/* o nome e o subtitulo cedem espaco (com reticencias) antes dos chips e
          do botao: o botao da acao nunca pode sair da tela */}
      <div className="topo-titulo">
        <h1>{cabecalho.clube}</h1>
        <div className="topo-sub">{cabecalho.subtitulo}</div>
      </div>

      <div className="espaco" />

      {cabecalho.chips.map((chip) => (
        <div className={`chip chip-${chip.label.split("/")[0].toLowerCase()}`} key={chip.label}>
          <span className="rotulo">{chip.label}</span>
          <span className={`valor${chip.estado === 'critico' ? ' critico' : ''}`}>{chip.valor}</span>
        </div>
      ))}

      <div className="topo-acoes">
        <button
          type="button"
          className="bt-fantasma bt-simular"
          onClick={aoSimular}
          title={porque([[avancando, AGUARDE]], 'Jogo a jogo, 1 mes, ate a janela ou a temporada toda')}
          disabled={avancando}
        >
          Simular…
        </button>
        {emTemporada && (
          <button
            type="button"
            className="bt-fantasma bt-semana"
            onClick={aoAvancar}
            title={porque([[avancando, AGUARDE]], 'Joga a semana sem assistir: o resultado vem no Painel')}
            disabled={avancando}
          >
            {cabecalho.acao}
          </button>
        )}
        {emTemporada ? (
          <button
            type="button"
            className="bt-acao bt-jogo"
            onClick={jogo ? aoJogar : aoIrParaOJogo}
            title={porque([[avancando, AGUARDE]],
              jogo ? 'Assistir ao jogo ao vivo e mexer no intervalo' : 'Pula as semanas sem jogo do seu time e para antes dele')}
            disabled={avancando}
          >
            <span className="bt-jogo-textos">
              <span>{avancando ? 'Processando…' : jogo ? 'Jogar' : 'Ir para o jogo'}</span>
              {jogo && !avancando && (
                <span className="bt-jogo-sub">
                  {jogo.adversario ? `${jogo.em_casa === false ? 'em ' : 'x '}${jogo.adversario}` : jogo.competicao}
                </span>
              )}
            </span>
            <IconeSeta />
          </button>
        ) : (
          <button type="button" className="bt-acao" onClick={aoAvancar} title={porque([[avancando, AGUARDE]])}
          disabled={avancando}>
            {avancando ? 'Processando…' : cabecalho.acao}
            <IconeSeta />
          </button>
        )}
      </div>
    </header>
  )
}
