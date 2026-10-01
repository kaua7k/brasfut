// O boletim do modo caos: o que estourou no futebol brasileiro na semana.
//
// Abre sozinho depois do avanco quando houve plantao. O que acertou o clube do
// jogador vem primeiro e marcado; tragedia e escandalo tem cor propria.

import { useEffect, useRef } from 'react'
import type { EventoCaos } from '../tipos'
import { Escudo } from './Escudo'

interface Props {
  eventos: EventoCaos[]
  aoFechar: () => void
}

const ROTULO: Record<EventoCaos['gravidade'], string> = {
  tragedia: 'Tragedia',
  grave: 'Escandalo',
  leve: 'Plantao',
}

export function Plantao({ eventos, aoFechar }: Props) {
  const caixa = useRef<HTMLDivElement>(null)
  useEffect(() => {
    caixa.current?.focus({ preventScroll: true })
  }, [])
  const ordem = [...eventos].sort((a, b) => Number(b.meu) - Number(a.meu))
  return (
    <div
      className="fundo-modal"
      role="dialog"
      aria-modal="true"
      aria-label="Plantao BRASFUT"
      onKeyDown={(e) => e.key === 'Escape' && aoFechar()}
    >
      <div className="modal modal-largo plantao" ref={caixa} tabIndex={-1}>
        <div className="plantao-faixa">
          <span className="plantao-ao-vivo">AO VIVO</span>
          <strong>PLANTAO BRASFUT</strong>
          <span className="tag-fraco">
            {eventos.length === 1 ? '1 noticia urgente' : `${eventos.length} noticias urgentes`}
          </span>
        </div>
        <ul className="plantao-lista">
          {ordem.map((ev, i) => (
            <li key={i} className={`plantao-item ${ev.gravidade}${ev.meu ? ' meu' : ''}`}>
              <div className="plantao-cab">
                <span className="plantao-selo">{ROTULO[ev.gravidade]}</span>
                {ev.clube && (
                  <span className="plantao-clube">
                    <Escudo nome={ev.clube} tamanho={18} />
                    {ev.clube}
                  </span>
                )}
                {ev.meu && <span className="plantao-meu">seu clube</span>}
                <span className="tag-fraco plantao-quando">
                  {ev.semana ? `semana ${ev.semana} · ` : ''}
                  {ev.temporada}
                </span>
              </div>
              <div className="plantao-titulo">{ev.titulo}</div>
              <p>{ev.texto}</p>
            </li>
          ))}
        </ul>
        <div className="modal-acoes">
          <button type="button" className="bt-acao" onClick={aoFechar}>
            Voltar ao jogo
          </button>
        </div>
      </div>
    </div>
  )
}
