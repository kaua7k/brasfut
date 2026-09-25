// O mural: as notas do meu clube e, na outra aba, o resto do futebol - goleada,
// zebra, lideranca, eliminado, titulo, contratacao cara e craque machucado.

import { useState } from 'react'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import type { TelaNoticias } from '../tipos'
import { FeedMundo } from './Painel'

export function Noticias({ tela }: { tela: TelaNoticias }) {
  const [aba, setAba] = useState<'clube' | 'mundo'>('clube')
  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={tela.subtitulo} />

      <div className="alavanca mb-3" role="tablist">
        <button type="button" role="tab" aria-selected={aba === 'clube'} className={aba === 'clube' ? 'ativo' : ''} onClick={() => setAba('clube')}>
          Meu clube
        </button>
        <button type="button" role="tab" aria-selected={aba === 'mundo'} className={aba === 'mundo' ? 'ativo' : ''} onClick={() => setAba('mundo')}>
          Pelo mundo
        </button>
      </div>

      <section className="painel corte">
        {aba === 'mundo' ? (
          <FeedMundo mundo={tela.mundo} vazio="O futebol ainda nao comecou. Avance a semana." />
        ) : tela.itens.length === 0 ? (
          <div className="vazio">Nada publicado ainda. Avance a semana para comecar a historia.</div>
        ) : (
          tela.itens.map((n, i) => (
            <div className="noticia-simples" key={i}>
              <i className="bolinha mt-2" />
              <span>{n.texto}</span>
            </div>
          ))
        )}
      </section>
    </div>
  )
}
