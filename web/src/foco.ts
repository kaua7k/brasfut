// Foco inicial de um dialogo.
//
// O Esc de cada dialogo mora no onKeyDown da caixa dele, e tecla so chega em
// quem tem o foco: sem isto o foco ficava no botao da tela de tras e o Esc so
// funcionava depois de um clique dentro do dialogo. Quem ja tem um campo com
// autoFocus fica como esta.

import { useEffect, useRef } from 'react'

export function useFocoInicial<T extends HTMLElement = HTMLDivElement>() {
  const caixa = useRef<T>(null)
  useEffect(() => {
    const el = caixa.current
    if (el && !el.contains(document.activeElement)) el.focus({ preventScroll: true })
  }, [])
  return caixa
}
