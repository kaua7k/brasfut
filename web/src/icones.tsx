// Os icones do design, inline.
//
// Sao os mesmos tracados do mockup: stroke de 2, sem preenchimento, herdando
// currentColor. Inline e nao arquivo porque um icone que muda de cor junto com
// o texto do menu precisa herdar a cor, e <img> nao herda.

import type { ReactElement } from 'react'

type Props = { tamanho?: number }

const base = (t: number) => ({
  width: t,
  height: t,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 2,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
  'aria-hidden': true,
})

export function IconePainel({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)}>
      <rect x="3" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="3" width="7" height="7" rx="1.5" />
      <rect x="3" y="14" width="7" height="7" rx="1.5" />
      <rect x="14" y="14" width="7" height="7" rx="1.5" />
    </svg>
  )
}

export function IconeElenco({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)}>
      <circle cx="9" cy="7" r="3.2" />
      <path d="M3 20c1-4 4-6 6-6s5 2 6 6" />
      <circle cx="18" cy="8" r="2.4" />
      <path d="M15.5 13.5c1.7.3 3.6 1.8 4.5 5" />
    </svg>
  )
}

export function IconeBase({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)}>
      <path d="M4 20V10l8-6 8 6v10" />
      <path d="M9 20v-6h6v6" />
    </svg>
  )
}

export function IconeTreino({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)}>
      <path d="M12 3v5.5M12 15.5V21M4.2 7l4.8 2.7M15 14.3l4.8 2.7M4.2 17l4.8-2.7M15 9.7l4.8-2.7" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  )
}

export function IconeEscalacao({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)}>
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <path d="M3 9h18M9 4v16" />
    </svg>
  )
}

export function IconeTabela({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)}>
      <path d="M4 6h16M4 12h16M4 18h10" />
    </svg>
  )
}

export function IconeCopas({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)}>
      <path d="M12 3l2.2 4.6 5 .7-3.7 3.6.9 5-4.4-2.4L7.6 17l.9-5-3.7-3.6 5-.7z" />
    </svg>
  )
}

export function IconeMercado({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)}>
      <path d="M3 7l9-4 9 4-9 4z" />
      <path d="M6 9.5v5.4c2 2.4 10 2.4 12 0V9.5" />
    </svg>
  )
}

export function IconeFinancas({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)}>
      <rect x="3" y="6" width="18" height="13" rx="2" />
      <path d="M3 10h18M8 6V4h8v2" />
    </svg>
  )
}

export function IconeEstadio({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)}>
      <path d="M4 21V9l8-6 8 6v12" />
      <path d="M9 21v-7h6v7" />
    </svg>
  )
}

export function IconeInfra({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)}>
      <path d="M4 21V8l5-4 5 4v13M14 21v-6l6-4v10z" />
    </svg>
  )
}

export function IconeNoticias({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)}>
      <path d="M5 4h14v13l-4 3v-3H5z" />
    </svg>
  )
}

export function IconeAjuda({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 8v4l3 2" />
    </svg>
  )
}

export function IconeSalvar({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)}>
      <path d="M5 4h11l3 3v13H5z" />
      <path d="M8 4v6h8V4M8 21v-6h8v6" />
    </svg>
  )
}

export function IconeSeta({ tamanho = 16 }: Props) {
  return (
    <svg {...base(tamanho)} strokeWidth={2.4} stroke="currentColor">
      <path d="M9 6l6 6-6 6" />
    </svg>
  )
}

export function IconeCerto({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)} strokeWidth={3}>
      <path d="M4 12l5 5L20 6" />
    </svg>
  )
}

export function IconeAviso({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)} strokeWidth={2.4}>
      <path d="M12 4v9" />
      <circle cx="12" cy="18" r="0.6" fill="currentColor" />
    </svg>
  )
}

export function IconeErro({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)} strokeWidth={2.6}>
      <path d="M6 6l12 12M18 6L6 18" />
    </svg>
  )
}

export function IconeRelogio({ tamanho = 18 }: Props) {
  return (
    <svg {...base(tamanho)}>
      <circle cx="12" cy="12" r="8" />
      <path d="M12 8v4l2.5 1.5" />
    </svg>
  )
}

/** O escudo do clube: estrela cheia, do jeito que o design desenha. */
export function Estrela({ tamanho = 20 }: Props) {
  return (
    <svg width={tamanho} height={tamanho} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 2l2.4 7.2H22l-6 4.6 2.3 7.2L12 16.4 5.7 21l2.3-7.2-6-4.6h7.6z" fill="currentColor" />
    </svg>
  )
}

/** O escudo do adversario, para separar os dois lados do confronto. */
export function EscudoRival({ tamanho = 24 }: Props) {
  return (
    <svg {...base(tamanho)}>
      <path d="M12 3l7 4v6c0 4.5-3 7-7 8-4-1-7-3.5-7-8V7z" />
    </svg>
  )
}

export const ICONES_MENU: Record<string, (p: Props) => ReactElement> = {
  painel: IconePainel,
  elenco: IconeElenco,
  base: IconeBase,
  treino: IconeTreino,
  escalacao: IconeEscalacao,
  tabela: IconeTabela,
  copas: IconeCopas,
  mercado: IconeMercado,
  financas: IconeFinancas,
  estadio: IconeEstadio,
  infra: IconeInfra,
  noticias: IconeNoticias,
}

export function iconeDeEstado(estado: string, tamanho = 18) {
  if (estado === 'ok') return <IconeCerto tamanho={tamanho} />
  if (estado === 'atencao') return <IconeAviso tamanho={tamanho} />
  if (estado === 'critico') return <IconeErro tamanho={tamanho} />
  return <IconeRelogio tamanho={tamanho} />
}
