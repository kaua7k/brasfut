// O jogo do meu clube, ao vivo, como no Brasfoot: o botao "Jogar" abre esta
// tela e o relogio corre. Na liga o motor joga o primeiro tempo antes da
// semana e para aos 45': o relogio vai de 0 a 45 mostrando os lances, o
// intervalo pede as decisoes (mentalidade e trocas), o servidor termina a
// partida e a semana, e o relogio segue de 46 ao apito com o resultado de
// verdade. Copa e estadual (sem intervalo no motor) correm do inicio ao fim.
//
// O que aparece e sempre o que o motor ja decidiu ate aquele minuto: o segundo
// tempo nao existe enquanto o tecnico nao decide o intervalo.

import { useEffect, useMemo, useRef, useState } from 'react'
import { Escudo } from './Escudo'
import { DetalhePartida } from './Partida'
import { DecisoesIntervalo } from './Intervalo'
import { descreve, lancesDaPartida, type Lance } from './AoVivo'
import type { Intervalo as DadosIntervalo, Lado, Partida, RespostaAvanco } from '../tipos'

export type ModoJogo =
  | { tipo: 'intervalo'; dados: DadosIntervalo }
  | { tipo: 'inteiro'; resposta: RespostaAvanco }

interface Props {
  modo: ModoJogo
  ocupado: boolean
  /** termina a partida parada no intervalo e a semana; devolve a resposta do avanco */
  aoSegundoTempo: (tatica: string, trocas: [number, number][], desligar: boolean) => Promise<RespostaAvanco | null>
  aoTerminar: (r: RespostaAvanco) => void
}

const VELOCIDADES = [
  { rotulo: '1x', ms: 450 },
  { rotulo: '2x', ms: 220 },
  { rotulo: '4x', ms: 100 },
]
const MEMORIA_VEL = 'jogo:velocidade'
const PAUSA_INTERVALO_MS = 1500

function lerVel() {
  try {
    const v = Number(window.localStorage.getItem(MEMORIA_VEL))
    return v >= 0 && v < VELOCIDADES.length ? v : 1
  } catch {
    return 1
  }
}

function gravarVel(v: number) {
  try {
    window.localStorage.setItem(MEMORIA_VEL, String(v))
  } catch {
    // sem armazenamento: a velocidade volta ao padrao no proximo jogo
  }
}

// o formato do intervalo (dto.intervalo) no formato do lance a lance
function lancesDoIntervalo(d: DadosIntervalo): Lance[] {
  return d.lances.map((l) => {
    const tipo = (['gol', 'amarelo', 'vermelho', 'lesao', 'substituicao'].includes(l.tipo)
      ? l.tipo
      : 'instrucao') as Lance['tipo']
    if (tipo === 'gol') return { minuto: l.minuto, lado: l.lado, tipo, texto: l.texto, extra: l.extra.replace(/^assist\. /, '') }
    if (tipo === 'substituicao') return { minuto: l.minuto, lado: l.lado, tipo, texto: l.texto, extra: l.extra }
    return { minuto: l.minuto, lado: l.lado, tipo, texto: l.texto, extra: '' }
  })
}

function placarAte(lances: Lance[], minuto: number): [number, number] {
  const p: [number, number] = [0, 0]
  for (const l of lances) if (l.tipo === 'gol' && l.minuto <= minuto) p[l.lado] += 1
  return p
}

export function JogoAoVivo({ modo, ocupado, aoSegundoTempo, aoTerminar }: Props) {
  // copa e estadual: as partidas do meu clube na semana, uma depois da outra
  const fila = useMemo(() => (modo.tipo === 'inteiro' ? modo.resposta.partidas ?? [] : []), [modo])
  const [indice, setIndice] = useState(0)
  const [final, setFinal] = useState<{ p: Partida; r: RespostaAvanco } | null>(
    modo.tipo === 'inteiro' && fila.length ? { p: fila[0], r: modo.resposta } : null,
  )
  const [minuto, setMinuto] = useState(0)
  const [rodando, setRodando] = useState(true)
  const [vel, setVel] = useState(lerVel)
  const [noIntervalo, setNoIntervalo] = useState(false)
  const [detalhe, setDetalhe] = useState(false)
  const pausaFeita = useRef(false)

  const p = final?.p ?? null
  const lances = useMemo(
    () => (p ? lancesDaPartida(p) : modo.tipo === 'intervalo' ? lancesDoIntervalo(modo.dados) : []),
    [p, modo],
  )
  const times: [string, string] = p ? p.times : modo.tipo === 'intervalo' ? modo.dados.times : ['', '']
  const eu: Lado = p ? p.eu : modo.tipo === 'intervalo' ? modo.dados.eu : 0
  const comp = p ? `${p.comp} · ${p.rodada}` : modo.tipo === 'intervalo' ? modo.dados.comp : ''
  const fimJogo = p ? Math.max(90, ...lances.map((l) => l.minuto)) : 90
  // sem o resultado final, o relogio so anda ate o intervalo
  const limite = p ? fimJogo : 45
  const acabou = !!p && minuto >= fimJogo
  const decidindo = !p && minuto >= 45

  useEffect(() => {
    if (!rodando || acabou || decidindo) return
    // jogo inteiro (copa): respira no intervalo e segue sozinho
    if (p && minuto === 45 && !pausaFeita.current && modo.tipo === 'inteiro') {
      pausaFeita.current = true
      setNoIntervalo(true)
      const t = window.setTimeout(() => {
        setNoIntervalo(false)
        setMinuto(46)
      }, PAUSA_INTERVALO_MS / (vel + 1))
      return () => window.clearTimeout(t)
    }
    const t = window.setTimeout(() => setMinuto((m) => Math.min(limite, m + 1)), VELOCIDADES[vel].ms)
    return () => window.clearTimeout(t)
  }, [minuto, rodando, vel, acabou, decidindo, limite, p, modo.tipo])

  const vistos = lances.filter((l) => l.minuto <= minuto)
  const placar = placarAte(lances, minuto)
  const [gm, gs] = eu === 0 ? placar : [placar[1], placar[0]]
  const estado = gm > gs ? 'ok' : gm === gs ? 'atencao' : 'critico'
  const ultimoGol = [...vistos].reverse().find((l) => l.tipo === 'gol')
  const golAgora = !!ultimoGol && minuto - ultimoGol.minuto < 3 && !acabou

  const segundoTempo = async (tatica: string, trocas: [number, number][], desligar: boolean) => {
    const r = await aoSegundoTempo(tatica, trocas, desligar)
    if (!r) return
    const meu = (r.partidas ?? []).find((x) => x.times[0] === times[0] && x.times[1] === times[1])
    if (!meu) {
      aoTerminar(r)
      return
    }
    pausaFeita.current = true
    setFinal({ p: meu, r })
    setMinuto(46)
    setRodando(true)
  }

  const pular = () => setMinuto(limite)
  const proximo = () => {
    const i = indice + 1
    if (!final || i >= fila.length) return
    setIndice(i)
    pausaFeita.current = false
    setFinal({ p: fila[i], r: final.r })
    setMinuto(0)
    setRodando(true)
  }

  if (detalhe && p) return <DetalhePartida p={p} aoFechar={() => setDetalhe(false)} />

  const fase = acabou ? 'Fim de jogo' : decidindo || noIntervalo ? 'Intervalo' : minuto === 0 ? 'Bola rolando' : minuto <= 45 ? '1o tempo' : '2o tempo'

  return (
    <div className="fundo-modal" role="dialog" aria-modal="true" aria-label={`Jogo: ${times[0]} x ${times[1]}`}>
      <div className="modal modal-largo ao-vivo jogo-ao-vivo">
        <p className="tag-fraco detalhe-sub">{comp}</p>
        <div className="detalhe-placar">
          <div className={`detalhe-time${eu === 0 ? ' eu' : ''}`}>
            <Escudo nome={times[0]} tamanho={44} />
            <h2>{times[0]}</h2>
          </div>
          <div className="ao-vivo-centro">
            <div className={`placar-numero detalhe-gols${acabou ? ` ${estado}` : ''}${golAgora ? ' gol-agora' : ''}`}>
              {placar[0]} x {placar[1]}
            </div>
            <div className="ao-vivo-relogio">{decidindo ? "45'" : `${minuto}'`}</div>
            <div className="ao-vivo-fase">{fase}</div>
          </div>
          <div className={`detalhe-time${eu === 1 ? ' eu' : ''}`}>
            <Escudo nome={times[1]} tamanho={44} />
            <h2>{times[1]}</h2>
          </div>
        </div>

        <div className="ao-vivo-barra" role="progressbar" aria-label="Tempo de jogo" aria-valuemin={0} aria-valuemax={90} aria-valuenow={minuto}>
          <div className="ao-vivo-barra-cheia" style={{ width: `${(Math.min(minuto, 90) / 90) * 100}%` }} />
          <div className="ao-vivo-barra-meio" />
        </div>

        {!acabou && !decidindo && (
          <div className="ao-vivo-controles">
            <button type="button" className="bt-fantasma" onClick={() => setRodando((r) => !r)}>
              {rodando ? 'Pausar' : 'Continuar'}
            </button>
            <div className="segmento" role="group" aria-label="Velocidade">
              {VELOCIDADES.map((v, i) => (
                <button
                  type="button"
                  key={v.rotulo}
                  className={`bt-fantasma bt-mini${i === vel ? ' ativa' : ''}`}
                  aria-pressed={i === vel}
                  onClick={() => {
                    setVel(i)
                    gravarVel(i)
                  }}
                >
                  {v.rotulo}
                </button>
              ))}
            </div>
            <button type="button" className="bt-fantasma empurra" onClick={pular}>
              {p ? 'Pular para o fim' : 'Pular para o intervalo'}
            </button>
          </div>
        )}

        {decidindo && modo.tipo === 'intervalo' && (
          <DecisoesIntervalo
            dados={modo.dados}
            ocupado={ocupado}
            aoSeguir={(tatica, trocas) => segundoTempo(tatica, trocas, false)}
            aoDesligar={() => segundoTempo(modo.dados.tatica, [], true)}
          />
        )}

        <ol className="ao-vivo-lances" aria-live="polite" aria-label="Lances">
          {acabou && p && (
            <li className="ao-vivo-lance apito">
              <span className="lance-minuto">{fimJogo}'</span>
              <span className="lance-texto">
                <strong>
                  Fim de jogo: {times[0]} {p.placar[0]} x {p.placar[1]} {times[1]}
                </strong>
                {p.detalhes.decisao && <span className="txt-atencao"> · {p.detalhes.decisao}</span>}
              </span>
            </li>
          )}
          {[...vistos].reverse().map((l, i) => {
            const d = descreve(l)
            return (
              <li key={`${l.minuto}-${l.tipo}-${i}`} className={`ao-vivo-lance ${l.tipo}${l.lado === eu ? ' meu' : ''}`}>
                <span className="lance-minuto">{l.minuto}'</span>
                <span className={`lance-marca ${l.tipo}`} aria-hidden="true" />
                <span className="lance-texto">
                  <strong>{d.titulo}</strong>
                  <span className="tag-fraco"> · {times[l.lado]}</span>
                  {d.sub && <span className="tag-fraco"> · {d.sub}</span>}
                </span>
              </li>
            )
          })}
          {vistos.length === 0 && !acabou && (
            <li className="tag-fraco">{minuto === 0 ? 'A bola vai rolar.' : 'Jogo truncado no meio de campo.'}</li>
          )}
        </ol>

        {acabou && p && (
          <>
            <table className="partida-estat mt-3">
              <tbody>
                {p.detalhes.estatisticas.map((e) => (
                  <tr key={e.rotulo}>
                    <td className="a-direita negrito">{e.valores[0]}</td>
                    <th scope="row">{e.rotulo}</th>
                    <td className="negrito">{e.valores[1]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="modal-acoes mt-4">
              <button type="button" className="bt-fantasma" onClick={() => setDetalhe(true)}>
                Ver notas
              </button>
              {indice + 1 < fila.length ? (
                <button type="button" className="bt-acao" onClick={proximo}>
                  Proximo jogo da semana
                </button>
              ) : (
                <button type="button" className="bt-acao" onClick={() => final && aoTerminar(final.r)}>
                  Continuar
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
