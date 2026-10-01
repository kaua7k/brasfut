// A ajuda e a apresentacao da carreira nova, que ate aqui so existiam na
// janela tkinter. O texto vem da API (dto.ajuda / dto.boas_vindas): os numeros
// (janela, confianca) saem do motor e nao envelhecem quando a regra muda.

import { useEffect, useRef, useState } from 'react'
import { Escudo } from './Escudo'
import type { Ajuda as DadosAjuda, BoasVindas as DadosBoasVindas, ItemAjuda } from '../tipos'

function Lista({ itens }: { itens: ItemAjuda[] }) {
  return (
    <dl className="ajuda-lista">
      {itens.map((i) => (
        <div key={i.nome}>
          <dt>{i.nome}</dt>
          <dd>{i.texto}</dd>
        </div>
      ))}
    </dl>
  )
}

/** O foco vai para a janela ao abrir, e Esc fecha - igual ao Resumo. */
function useFoco() {
  const caixa = useRef<HTMLDivElement>(null)
  useEffect(() => {
    caixa.current?.focus({ preventScroll: true })
  }, [])
  return caixa
}

interface PropsAjuda {
  ajuda: DadosAjuda
  aoFechar: () => void
}

export function Ajuda({ ajuda, aoFechar }: PropsAjuda) {
  const [aba, setAba] = useState<'telas' | 'termos'>('telas')
  const caixa = useFoco()
  return (
    <div
      className="fundo-modal"
      role="dialog"
      aria-modal="true"
      aria-label="Ajuda"
      onKeyDown={(e) => e.key === 'Escape' && aoFechar()}
    >
      <div className="modal modal-largo dlg" ref={caixa} tabIndex={-1}>
        <header className="dlg-cab">
          <div className="dlg-textos">
            <div className="dlg-kicker">Manual do tecnico</div>
            <h2>Ajuda</h2>
            <div className="dlg-sub">O que cada tela faz e o que os termos querem dizer.</div>
          </div>
        </header>
        <div className="dlg-corpo">
        <div className="abas mb-2" role="tablist">
          {(
            [
              ['telas', 'As telas'],
              ['termos', 'Termos do jogo'],
            ] as const
          ).map(([k, rotulo]) => (
            <button
              key={k}
              type="button"
              role="tab"
              aria-selected={aba === k}
              className={aba === k ? 'bt-acao bt-mini' : 'bt-fantasma bt-mini'}
              onClick={() => setAba(k)}
            >
              {rotulo}
            </button>
          ))}
        </div>
        <Lista itens={aba === 'telas' ? ajuda.telas : ajuda.termos} />
        </div>
        <div className="modal-acoes">
          <button type="button" className="bt-acao bt-media" onClick={aoFechar}>
            Fechar
          </button>
        </div>
      </div>
    </div>
  )
}

interface PropsBoasVindas {
  dados: DadosBoasVindas
  aoVerAjuda: () => void
  aoFechar: () => void
}

export function BoasVindas({ dados, aoVerAjuda, aoFechar }: PropsBoasVindas) {
  const caixa = useFoco()
  return (
    <div
      className="fundo-modal"
      role="dialog"
      aria-modal="true"
      aria-label={`Bem-vindo ao ${dados.clube}`}
      onKeyDown={(e) => e.key === 'Escape' && aoFechar()}
    >
      <div className="modal modal-largo dlg" ref={caixa} tabIndex={-1}>
        <header className="dlg-cab">
          <Escudo nome={dados.clube} tamanho={38} />
          <div className="dlg-textos">
            <div className="dlg-kicker">Bem-vindo</div>
            <h2>Voce e o tecnico do {dados.clube}</h2>
            <div className="dlg-sub">{dados.linha}</div>
          </div>
        </header>
        <div className="dlg-corpo">

        <div className="painel-titulo mt-3 mb-2">O que a diretoria espera</div>
        <p className="mb-0 txt-atencao">{dados.objetivo}</p>
        <p className="mt-1 txt-p txt-fraco">{dados.aviso}</p>

        <div className="painel-titulo mt-3 mb-2">Os tres passos para comecar</div>
        <ol className="ajuda-lista">
          {dados.passos.map((p) => (
            <li key={p.nome}>
              <strong>{p.nome}</strong>: {p.texto}
            </li>
          ))}
        </ol>

        <div className="painel-titulo mt-3 mb-2">Sem pressa</div>
        <p className="mb-0 txt-p">{dados.sem_pressa}</p>
        </div>

        <div className="modal-acoes">
          <button type="button" className="bt-fantasma bt-media" onClick={aoVerAjuda}>
            Ver a ajuda completa
          </button>
          <button type="button" className="bt-acao bt-media" onClick={aoFechar}>
            Comecar
          </button>
        </div>
      </div>
    </div>
  )
}
