// O mural do clube: as ultimas 25 notas do motor, da mais recente para a mais
// antiga. O Painel mostra so as ultimas; aqui fica a memoria.

import { CabecalhoTela } from '../componentes/CabecalhoTela'
import type { TelaNoticias } from '../tipos'

export function Noticias({ tela }: { tela: TelaNoticias }) {
  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={tela.subtitulo} />

      <section className="painel" style={{ overflow: 'hidden' }}>
        {tela.itens.length === 0 ? (
          <div className="vazio">Nada publicado ainda. Avance a semana para comecar a historia.</div>
        ) : (
          tela.itens.map((n, i) => (
            <div className="noticia-simples" key={i}>
              <i className="bolinha" style={{ marginTop: 7 }} />
              <span>{n.texto}</span>
            </div>
          ))
        )}
      </section>
    </div>
  )
}
