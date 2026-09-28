// O escudo de cada clube, desenhado a partir de poucos dados.
//
// Nao sao os escudos oficiais (marca registrada): sao escudos genericos com
// as cores do clube, uma de tres formas, um padrao (liso, listras, faixas,
// faixa transversal, metade) e a sigla. As cores vem do servidor
// (dados_clubes.ESCUDOS ou uma paleta estavel pelo nome); o mapa de escudos e
// carregado uma vez e qualquer tela desenha pelo nome do clube.

import { useId, useSyncExternalStore } from 'react'
import type { DadosEscudo } from '../tipos'

let mapa = new Map<string, DadosEscudo>()
const ouvintes = new Set<() => void>()

export function guardarEscudos(lista: DadosEscudo[]) {
  mapa = new Map(lista.map((e) => [e.nome, e]))
  ouvintes.forEach((f) => f())
}

function inscrever(f: () => void) {
  ouvintes.add(f)
  return () => ouvintes.delete(f)
}

const FORMAS = [
  'M20 1.5 L38 6.5 V22 C38 35 30 43 20 46.5 C10 43 2 35 2 22 V6.5 Z',
  'M20 4 A19 19 0 1 1 19.99 4 Z',
  'M3 3 H37 V24 C37 36 29 42.5 20 46 C11 42.5 3 36 3 24 Z',
]

function Padrao({ e }: { e: DadosEscudo }) {
  switch (e.padrao) {
    case 'vertical':
      return (
        <>
          {[6, 14, 22, 30].map((x) => (
            <rect key={x} x={x} y={0} width={4} height={48} fill={e.cor2} />
          ))}
        </>
      )
    case 'horizontal':
      return (
        <>
          {[8, 20, 32].map((y) => (
            <rect key={y} x={0} y={y} width={40} height={6} fill={e.cor2} />
          ))}
        </>
      )
    case 'diagonal':
      return <polygon points="0,30 0,40 40,12 40,2" fill={e.cor2} />
    case 'metade':
      return <rect x={20} y={0} width={20} height={48} fill={e.cor2} />
    default:
      return <rect x={0} y={30} width={40} height={18} fill={e.cor2} />
  }
}

interface Props {
  /** nome do clube, como o servidor manda */
  nome: string
  tamanho?: number
  /** dados ja em maos (slot do menu): dispensa o mapa */
  dados?: DadosEscudo
}

export function Escudo({ nome, tamanho = 32, dados }: Props) {
  const atual = useSyncExternalStore(inscrever, () => mapa)
  const e = dados ?? atual.get(nome)
  const id = useId().replace(/:/g, '')
  if (!e) {
    return (
      <svg className="escudo-svg vazio" width={tamanho} height={tamanho * 1.2} viewBox="0 0 40 48" aria-hidden="true">
        <path className="contorno" d={FORMAS[0]} />
      </svg>
    )
  }
  const forma = FORMAS[e.forma % FORMAS.length]
  return (
    <svg
      className="escudo-svg"
      width={tamanho}
      height={tamanho * 1.2}
      viewBox="0 0 40 48"
      role="img"
      aria-label={`Escudo do ${e.nome}`}
    >
      <defs>
        <clipPath id={`e${id}`}>
          <path d={forma} />
        </clipPath>
      </defs>
      <g clipPath={`url(#e${id})`}>
        <rect x={0} y={0} width={40} height={48} fill={e.cor1} />
        <Padrao e={e} />
        <rect className="faixa-sigla" x={4} y={19} width={32} height={11} rx={2} />
      </g>
      <path className="contorno" d={forma} />
      <text className="sigla" x={20} y={27.5} textAnchor="middle" fontSize={e.sigla.length > 3 ? 7.5 : 9}>
        {e.sigla}
      </text>
    </svg>
  )
}
