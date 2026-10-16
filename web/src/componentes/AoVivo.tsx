// A partida lance a lance: o relogio corre de 0 a 90 e o placar, os cartoes,
// as trocas e as mudancas de mentalidade aparecem no minuto em que o motor os
// registrou. O jogo ja foi simulado inteiro; aqui so se assiste de novo, na
// ordem. Estatisticas (posse, chutes) so aparecem no apito final: o motor
// guarda o total, nao o minuto a minuto, e inventar a curva seria mentir.
//
// Tudo vem no mesmo objeto Partida do resumo, sem outra chamada a API.

import { useEffect, useMemo, useRef, useState } from 'react'
import { Escudo } from './Escudo'
import { DetalhePartida } from './Partida'
import type { Lado, Partida } from '../tipos'

type TipoLance = 'gol' | 'amarelo' | 'vermelho' | 'segundo_amarelo' | 'substituicao' | 'lesao' | 'instrucao'

interface Lance {
  minuto: number
  lado: Lado
  tipo: TipoLance
  texto: string
  extra: string
}

// milissegundos por minuto de jogo em cada velocidade (1x: ~36 s por partida)
const VELOCIDADES = [
  { rotulo: '1x', ms: 400 },
  { rotulo: '2x', ms: 200 },
  { rotulo: '4x', ms: 100 },
]
// o intervalo segura o relogio um pouco antes do segundo tempo
const PAUSA_INTERVALO_MS = 2500

// mesma ordem dentro do minuto: o gol antes do cartao que veio da comemoracao
const ORDEM: Record<TipoLance, number> = {
  gol: 0, amarelo: 1, segundo_amarelo: 2, vermelho: 3, lesao: 4, substituicao: 5, instrucao: 6,
}

export function lancesDaPartida(p: Partida): Lance[] {
  return [
    ...p.gols.map((g) => ({ minuto: g.minuto, lado: g.lado, tipo: 'gol' as const, texto: g.autor, extra: g.assist })),
    ...p.cartoes.map((c) => ({ minuto: c.minuto, lado: c.lado, tipo: c.tipo, texto: c.nome, extra: '' })),
    ...p.detalhes.subs.map((s) => ({
      minuto: s.minuto, lado: s.lado, tipo: 'substituicao' as const, texto: `entra ${s.entra}`, extra: `sai ${s.sai}`,
    })),
    ...p.detalhes.lesoes.map((l) => ({ minuto: l.minuto, lado: l.lado, tipo: 'lesao' as const, texto: l.nome, extra: '' })),
    ...p.instrucoes.map((x) => ({
      minuto: x.minuto, lado: x.lado, tipo: 'instrucao' as const, texto: `passa a jogar ${x.tatica}`, extra: x.motivo,
    })),
  ].sort((a, b) => a.minuto - b.minuto || ORDEM[a.tipo] - ORDEM[b.tipo])
}

function descreve(l: Lance) {
  switch (l.tipo) {
    case 'gol':
      return { titulo: `GOL! ${l.texto}`, sub: l.extra ? `assistencia de ${l.extra}` : '' }
    case 'amarelo':
      return { titulo: `Amarelo para ${l.texto}`, sub: '' }
    case 'segundo_amarelo':
      return { titulo: `Segundo amarelo: ${l.texto} expulso`, sub: '' }
    case 'vermelho':
      return { titulo: `Vermelho direto para ${l.texto}`, sub: '' }
    case 'lesao':
      return { titulo: `${l.texto} se machucou`, sub: '' }
    case 'substituicao':
      return { titulo: l.texto, sub: l.extra }
    case 'instrucao':
      return { titulo: l.texto, sub: l.extra }
  }
}

function fase(minuto: number, fim: number, noIntervalo: boolean) {
  if (minuto >= fim) return 'Fim de jogo'
  if (noIntervalo) return 'Intervalo'
  if (minuto === 0) return 'Antes do apito'
  return minuto <= 45 ? '1o tempo' : '2o tempo'
}

export function AoVivo({ p, aoFechar }: { p: Partida; aoFechar: () => void }) {
  const lances = useMemo(() => lancesDaPartida(p), [p])
  const fim = Math.max(90, ...lances.map((l) => l.minuto))
  const [minuto, setMinuto] = useState(0)
  const [rodando, setRodando] = useState(true)
  const [vel, setVel] = useState(0)
  const [noIntervalo, setNoIntervalo] = useState(false)
  const [detalhe, setDetalhe] = useState(false)
  const intervaloFeito = useRef(false)

  const acabou = minuto >= fim

  useEffect(() => {
    if (!rodando || acabou) return
    if (minuto === 45 && !intervaloFeito.current) {
      intervaloFeito.current = true
      setNoIntervalo(true)
      const t = window.setTimeout(() => {
        setNoIntervalo(false)
        setMinuto(46)
      }, PAUSA_INTERVALO_MS / (vel + 1))
      return () => window.clearTimeout(t)
    }
    const t = window.setTimeout(() => setMinuto((m) => Math.min(fim, m + 1)), VELOCIDADES[vel].ms)
    return () => window.clearTimeout(t)
  }, [minuto, rodando, vel, acabou, fim])

  const vistos = lances.filter((l) => l.minuto <= minuto)
  const placar: [number, number] = [0, 0]
  for (const l of vistos) if (l.tipo === 'gol') placar[l.lado] += 1
  const meioTempo: [number, number] = [0, 0]
  for (const l of lances) if (l.tipo === 'gol' && l.minuto <= 45) meioTempo[l.lado] += 1
  const ultimoGol = [...vistos].reverse().find((l) => l.tipo === 'gol')
  const golAgora = !!ultimoGol && minuto - ultimoGol.minuto < 3 && !acabou

  const pular = () => {
    intervaloFeito.current = true
    setNoIntervalo(false)
    setMinuto(fim)
  }
  const pausarOuSeguir = () => {
    if (noIntervalo) {
      setNoIntervalo(false)
      setMinuto(46)
      setRodando(true)
      return
    }
    setRodando((r) => !r)
  }

  if (detalhe) return <DetalhePartida p={p} aoFechar={() => setDetalhe(false)} />

  const intervalo = (
    <li key="intervalo" className="ao-vivo-lance apito">
      <span className="lance-minuto">45'</span>
      <span className="lance-texto tag-fraco">
        Intervalo: {p.times[0]} {meioTempo[0]} x {meioTempo[1]} {p.times[1]}
      </span>
    </li>
  )

  return (
    <div
      className="fundo-modal"
      role="dialog"
      aria-modal="true"
      aria-label={`Ao vivo: ${p.times[0]} x ${p.times[1]}`}
      onClick={aoFechar}
      onKeyDown={(e) => {
        e.stopPropagation()
        if (e.key === 'Escape') aoFechar()
        if (e.key === ' ' && e.target === e.currentTarget) {
          e.preventDefault()
          pausarOuSeguir()
        }
      }}
    >
      <div className="modal modal-largo ao-vivo" onClick={(e) => e.stopPropagation()}>
        <p className="tag-fraco detalhe-sub">
          {p.comp} · {p.rodada}
          {p.detalhes.publico && ` · ${p.detalhes.publico}`}
        </p>
        <div className="detalhe-placar">
          <div className={`detalhe-time${p.eu === 0 ? ' eu' : ''}`}>
            <Escudo nome={p.times[0]} tamanho={48} />
            <h2>{p.times[0]}</h2>
          </div>
          <div className="ao-vivo-centro">
            <div className={`placar-numero detalhe-gols${acabou ? ` ${p.estado}` : ''}${golAgora ? ' gol-agora' : ''}`}>
              {placar[0]} x {placar[1]}
            </div>
            <div className="ao-vivo-relogio" aria-live="off">
              {minuto}'
            </div>
            <div className="ao-vivo-fase">{fase(minuto, fim, noIntervalo)}</div>
          </div>
          <div className={`detalhe-time${p.eu === 1 ? ' eu' : ''}`}>
            <Escudo nome={p.times[1]} tamanho={48} />
            <h2>{p.times[1]}</h2>
          </div>
        </div>

        <div
          className="ao-vivo-barra"
          role="progressbar"
          aria-label="Tempo de jogo"
          aria-valuemin={0}
          aria-valuemax={fim}
          aria-valuenow={minuto}
        >
          <div className="ao-vivo-barra-cheia" style={{ width: `${(minuto / fim) * 100}%` }} />
          <div className="ao-vivo-barra-meio" />
        </div>

        {!acabou && (
          <div className="ao-vivo-controles">
            <button type="button" className="bt-acao" onClick={pausarOuSeguir}>
              {noIntervalo ? 'Comecar o 2o tempo' : rodando ? 'Pausar' : 'Continuar'}
            </button>
            <div className="ao-vivo-velocidade" role="group" aria-label="Velocidade">
              {VELOCIDADES.map((v, i) => (
                <button
                  type="button"
                  key={v.rotulo}
                  className={`bt-fantasma bt-mini${i === vel ? ' ativa' : ''}`}
                  aria-pressed={i === vel}
                  onClick={() => setVel(i)}
                >
                  {v.rotulo}
                </button>
              ))}
            </div>
            <button type="button" className="bt-fantasma empurra" onClick={pular}>
              Pular para o fim
            </button>
          </div>
        )}

        <ol className="ao-vivo-lances" aria-live="polite" aria-label="Lances">
          {acabou && (
            <li className="ao-vivo-lance apito">
              <span className="lance-minuto">{fim}'</span>
              <span className="lance-texto">
                <strong>
                  Fim de jogo: {p.times[0]} {p.placar[0]} x {p.placar[1]} {p.times[1]}
                </strong>
                {p.detalhes.decisao && <span className="txt-atencao"> · {p.detalhes.decisao}</span>}
              </span>
            </li>
          )}
          {[...vistos].reverse().flatMap((l, i, lista) => {
            const d = descreve(l)
            const item = (
              <li key={`${l.minuto}-${l.tipo}-${i}`} className={`ao-vivo-lance ${l.tipo}${l.lado === p.eu ? ' meu' : ''}`}>
                <span className="lance-minuto">{l.minuto}'</span>
                <span className={`lance-marca ${l.tipo}`} aria-hidden="true" />
                <span className="lance-texto">
                  <strong>{d.titulo}</strong>
                  <span className="tag-fraco"> · {p.times[l.lado]}</span>
                  {d.sub && <span className="tag-fraco"> · {d.sub}</span>}
                </span>
              </li>
            )
            // o intervalo entra entre o ultimo lance do 2o tempo e o primeiro do 1o
            const anterior = i > 0 ? lista[i - 1].minuto : Infinity
            if (minuto >= 46 && l.minuto <= 45 && anterior > 45) return [intervalo, item]
            return [item]
          })}
          {minuto >= 46 && !vistos.some((l) => l.minuto <= 45) && intervalo}
          {vistos.length === 0 && minuto < 46 && !acabou && (
            <li className="tag-fraco">{minuto === 0 ? 'A bola vai rolar.' : 'Jogo truncado no meio de campo.'}</li>
          )}
        </ol>

        {acabou && (
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
        )}

        <div className="modal-acoes mt-4">
          {acabou && (
            <button type="button" className="bt-fantasma" onClick={() => setDetalhe(true)}>
              Ver notas
            </button>
          )}
          <button type="button" className={acabou ? 'bt-acao' : 'bt-fantasma'} onClick={aoFechar}>
            Fechar
          </button>
        </div>
      </div>
    </div>
  )
}
