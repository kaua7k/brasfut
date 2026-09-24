// A barra do topo carrega SO a acao da semana.
//
// A mesma regra da janela tkinter: com Salvar, Ajuda e Resumo aqui em cima a
// barra estourava e o caixa saia da tela. Salvar desceu para o pe do menu.

import { Estrela, IconeSeta } from '../icones'
import type { Cabecalho } from '../tipos'

interface Props {
  cabecalho: Cabecalho
  aoAvancar: () => void
  /** Abre o painel de ritmos: jogo a jogo, mes, janela, temporada. */
  aoSimular: () => void
  avancando: boolean
}

export function BarraTopo({ cabecalho, aoAvancar, aoSimular, avancando }: Props) {
  return (
    <header className="topo">
      <div className="escudo g"><Estrela tamanho={24} /></div>
      {/* o nome e o subtitulo cedem espaco (com reticencias) antes dos chips e
          do botao: o botao da acao nunca pode sair da tela */}
      <div className="topo-titulo">
        <h1>{cabecalho.clube}</h1>
        <div className="topo-sub">{cabecalho.subtitulo}</div>
      </div>

      <div className="espaco" />

      {cabecalho.chips.map((chip) => (
        <div className="chip" key={chip.label}>
          <span className="rotulo">{chip.label}</span>
          <span className={`valor${chip.estado === 'critico' ? ' critico' : ''}`}>{chip.valor}</span>
        </div>
      ))}

      {/* o clique de sempre continua sendo uma semana; os outros ritmos moram
          no Simular, para o botao principal nunca pular meio ano por engano */}
      <button
        type="button"
        className="bt-fantasma bt-simular"
        onClick={aoSimular}
        disabled={avancando}
        title="Jogo a jogo, 1 mes, ate a janela ou a temporada toda"
      >
        Simular…
      </button>
      <button type="button" className="bt-acao" onClick={aoAvancar} disabled={avancando}>
        {avancando ? 'Processando…' : cabecalho.acao}
        <IconeSeta />
      </button>
    </header>
  )
}
