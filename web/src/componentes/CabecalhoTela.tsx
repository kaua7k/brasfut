// Titulo, uma linha curta de contexto e as metricas como chips.
//
// A mesma regra da janela: numero e numero (chip), texto e texto (uma linha
// so). Antes tudo isso era uma frase unica de ate 162 caracteres separada por
// barras verticais, e o olho nao achava onde comecava cada informacao.

import type { ReactNode } from 'react'
import type { Metrica } from '../tipos'

interface Props {
  titulo: string
  sub?: string
  metricas?: Metrica[]
  children?: ReactNode
}

export function CabecalhoTela({ titulo, sub, metricas, children }: Props) {
  return (
    <div className="cabecalho-tela">
      <h2>{titulo}</h2>
      {sub && <div className="sub">{sub}</div>}
      {metricas && metricas.length > 0 && (
        <div className="metricas">
          {metricas.map((m) => (
            <div className="metrica" key={m.nome}>
              <div className={`valor ${m.estado ?? ''}`}>{m.valor}</div>
              <div className="nome">{m.nome}</div>
            </div>
          ))}
        </div>
      )}
      {children}
    </div>
  )
}
