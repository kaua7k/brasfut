// A pergunta antes de uma acao que custa caro ou nao tem volta (vender,
// rescindir, obra, entrar em campo com o time quebrado).
//
// Esc cancela. O foco comeca no Cancelar quando a acao e perigosa (Enter por
// reflexo nao confirma) e no Confirmar quando nao e.

import { useEffect, useRef } from 'react'
import { porque, AGUARDE } from '../motivo'
import type { Confirmar } from '../tipos'

interface Props {
  confirmar: Confirmar
  /** nome da tela onde se conserta o problema (ex.: "Escalacao"), quando existe uma */
  destino?: string
  ocupado: boolean
  aoCancelar: () => void
  aoConfirmar: () => void
  aoAbrirDestino?: () => void
}

export function Confirmacao({ confirmar, destino, ocupado, aoCancelar, aoConfirmar, aoAbrirDestino }: Props) {
  const cancelar = useRef<HTMLButtonElement>(null)
  const sim = useRef<HTMLButtonElement>(null)
  useEffect(() => {
    ;(confirmar.perigo ? cancelar : sim).current?.focus({ preventScroll: true })
  }, [confirmar.perigo])
  return (
    <div
      className="fundo-modal"
      role="alertdialog"
      aria-modal="true"
      aria-label={confirmar.titulo}
      onKeyDown={(e) => e.key === 'Escape' && aoCancelar()}
    >
      <div className="modal">
        <h2>{confirmar.titulo}</h2>
        <p>{confirmar.texto}</p>
        <div className="modal-acoes">
          <button type="button" className="bt-fantasma" ref={cancelar} onClick={aoCancelar}>
            Cancelar
          </button>
          {destino && aoAbrirDestino && (
            <button type="button" className="bt-fantasma" onClick={aoAbrirDestino}>
              Abrir {destino}
            </button>
          )}
          <button
            type="button"
            ref={sim}
            className={`bt-acao${confirmar.perigo ? ' bt-perigo' : ''}`}
            title={porque([[ocupado, AGUARDE]])}
            disabled={ocupado}
            onClick={aoConfirmar}
          >
            Confirmar
          </button>
        </div>
      </div>
    </div>
  )
}
