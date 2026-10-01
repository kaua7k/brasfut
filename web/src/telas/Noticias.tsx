// O mural: as notas do meu clube e, na outra aba, o resto do futebol - goleada,
// zebra, lideranca, eliminado, titulo, contratacao cara e craque machucado.

import { useState } from 'react'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import type { TelaNoticias } from '../tipos'
import { FeedMundo } from './Painel'

// O texto vem pronto do motor ("S01: Camisa: X assina..."): a temporada vira
// carimbo e uma palavra-chave decide a cor do rotulo.
function leitura(texto: string): { temp: string | null; corpo: string; tipo: string; rotulo: string } {
  const m = /^S(\d+):\s*(.*)$/s.exec(texto)
  const corpo = m ? m[2] : texto
  const t = corpo.toLowerCase()
  let tipo = 'geral'
  let rotulo = 'Clube'
  if (/assina|patrocin|naming|camisa|manga|calcao|uniforme|R\$/i.test(corpo)) [tipo, rotulo] = ['grana', 'Negocio']
  else if (/lesao|lesionad|machuc/.test(t)) [tipo, rotulo] = ['mal', 'Lesao']
  else if (/titulo|campea|taca|acesso/.test(t)) [tipo, rotulo] = ['ouro', 'Conquista']
  else if (/contrat|reforco|vendid|comprad|transfer|renov/.test(t)) [tipo, rotulo] = ['bom', 'Mercado']
  return { temp: m ? `S${m[1]}` : null, corpo, tipo, rotulo }
}

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
          tela.itens.map((n, i) => {
            const l = leitura(n.texto)
            return (
              <div className={`noticia-simples not-${l.tipo}`} key={i}>
                <span className="not-rotulo">{l.rotulo}</span>
                <span className="not-texto">{l.corpo}</span>
                {l.temp && <span className="not-temp">{l.temp}</span>}
              </div>
            )
          })
        )}
      </section>
    </div>
  )
}
