// Tela de celular (ate 640 px de largura, em pe). O CSS tem o mesmo corte em
// @media (max-width: 640px); aqui e para o que o CSS nao alcanca, como as
// colunas da <Grade>, que vao no style da linha.

import { useSyncExternalStore } from 'react'

export const CONSULTA_ESTREITA = '(max-width: 640px)'

function assinar(aviso: () => void) {
  const m = window.matchMedia(CONSULTA_ESTREITA)
  m.addEventListener('change', aviso)
  return () => m.removeEventListener('change', aviso)
}

export function useTelaEstreita(): boolean {
  return useSyncExternalStore(
    assinar,
    () => window.matchMedia(CONSULTA_ESTREITA).matches,
    () => false,
  )
}
