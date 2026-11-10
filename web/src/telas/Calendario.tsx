// A temporada do meu clube como calendario: cada mes do jogo (4 semanas, como
// o motor conta - SEMANAS_POR_MES) e uma faixa com um quadrado por semana.
// Jogos (com placar depois de jogados), janela abre/aberta/fecha e datas FIFA
// vem prontos do motor (dto.calendario); aqui so se desenha. Abre rolado ate a
// semana atual.

import { useEffect, useRef, type Ref } from 'react'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import type { JogoCalendario, SemanaCalendario, TelaCalendario } from '../tipos'

const SEMANAS_POR_MES = 4

const JANELA: Record<string, string> = {
  abre: 'Janela abre',
  aberta: 'Janela aberta',
  fecha: 'Janela fecha',
}

const MANDO: Record<string, string> = {
  casa: 'casa',
  fora: 'fora',
  neutro: 'neutro',
  ida_volta: 'ida e volta',
}

const RESULTADO: Record<string, string> = { v: 'vitoria', e: 'empate', d: 'derrota' }

function emMeses(semanas: SemanaCalendario[]): SemanaCalendario[][] {
  const meses: SemanaCalendario[][] = []
  for (let i = 0; i < semanas.length; i += SEMANAS_POR_MES) meses.push(semanas.slice(i, i + SEMANAS_POR_MES))
  return meses
}

function Jogo({ jogo }: { jogo: JogoCalendario }) {
  const comp = jogo.detalhe ? `${jogo.competicao} . ${jogo.detalhe}` : jogo.competicao
  return (
    <li className="cal-jogo">
      <div className="cal-comp" title={comp}>
        {jogo.competicao}
        {jogo.detalhe && <span className="cal-detalhe"> · {jogo.detalhe}</span>}
      </div>
      <div className="cal-linha-adv">
        <span className="cal-adv" title={jogo.adversario ?? undefined}>
          {jogo.adversario ?? <span className="cal-indef">a definir</span>}
        </span>
        {jogo.placar && jogo.resultado ? (
          <span className={`cal-placar cal-${jogo.resultado}`}
            aria-label={`${jogo.placar[0]} a ${jogo.placar[1]}, ${RESULTADO[jogo.resultado]}`}>
            {jogo.placar[0]} x {jogo.placar[1]}
          </span>
        ) : (
          jogo.mando && <span className="cal-mando">{MANDO[jogo.mando]}</span>
        )}
      </div>
    </li>
  )
}

function Semana({ s, refAtual }: { s: SemanaCalendario; refAtual?: Ref<HTMLLIElement> }) {
  const classe = [
    'cal-semana',
    s.atual ? 'atual' : '',
    s.passada ? 'passada' : '',
    s.janela ? `janela-${s.janela}` : '',
  ].join(' ')
  return (
    <li className={classe} ref={s.atual ? refAtual : undefined} aria-current={s.atual ? 'step' : undefined}>
      <div className="cal-cab">
        <span className="cal-rotulo">{s.rotulo}</span>
        {s.atual && <span className="cal-selo cal-selo-atual">agora</span>}
      </div>
      {(s.janela || s.fifa) && (
        <div className="cal-selos">
          {s.janela && <span className={`cal-selo cal-janela-${s.janela}`}>{JANELA[s.janela]}</span>}
          {s.fifa && <span className="cal-selo cal-fifa">Data FIFA</span>}
        </div>
      )}
      {s.jogos.length === 0 ? (
        <div className="cal-folga">Sem jogo</div>
      ) : (
        <ul className="cal-jogos">
          {s.jogos.map((j, i) => (
            <Jogo jogo={j} key={i} />
          ))}
        </ul>
      )}
    </li>
  )
}

export function Calendario({ tela }: { tela: TelaCalendario }) {
  const atual = useRef<HTMLLIElement>(null)
  useEffect(() => {
    atual.current?.scrollIntoView({ block: 'center' })
  }, [tela])

  const r = tela.resumo
  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={tela.subtitulo} />

      <section className="painel enxuto cal-resumo mb-3">
        <div>
          <div className="painel-titulo">Agora</div>
          <div className="cal-resumo-valor">{r.agora}</div>
        </div>
        <div>
          <div className="painel-titulo">Janela de transferencias</div>
          <div className={`cal-resumo-valor ${r.janela_aberta ? 'cal-aberta' : ''}`}>{r.janela}</div>
        </div>
        <div>
          <div className="painel-titulo">Proximo jogo</div>
          <div className="cal-resumo-valor">{r.proximo ?? 'Nenhum jogo pela frente nesta temporada'}</div>
        </div>
      </section>

      <div className="cal-legenda mb-3" aria-label="Legenda">
        <span><i className="cal-cor janela-abre" /> janela abre</span>
        <span><i className="cal-cor janela-aberta" /> janela aberta</span>
        <span><i className="cal-cor janela-fecha" /> janela fecha</span>
        <span><i className="cal-cor cal-cor-fifa" /> data FIFA</span>
        <span><i className="cal-cor cal-cor-atual" /> semana atual</span>
      </div>

      {tela.blocos.map((b) => (
        <section className="cal-bloco mb-3" key={b.id}>
          <div className="cal-bloco-cab">
            <h3 className="cal-bloco-titulo">{b.titulo}</h3>
            <span className="cal-bloco-sub">{b.subtitulo}</span>
          </div>
          {emMeses(b.semanas).map((mes, m) => (
            <div className="cal-mes" key={m}>
              <div className="cal-mes-titulo">
                Mes {m + 1}
                <span className="cal-mes-faixa">
                  {' · '}
                  {mes[0].rotulo.replace('Semana ', 'semanas ')}
                  {mes.length > 1 && `-${mes[mes.length - 1].numero}`}
                </span>
              </div>
              <ol className="cal-grade">
                {mes.map((s) => (
                  <Semana s={s} key={s.numero} refAtual={atual} />
                ))}
              </ol>
            </div>
          ))}
        </section>
      ))}
    </div>
  )
}
