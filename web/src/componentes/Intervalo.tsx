// As decisoes do intervalo do meu jogo de liga: mentalidade do segundo tempo
// e substituicoes (titular que sai x reserva que entra, ate o limite do jogo).
// Mora dentro da partida ao vivo (JogoAoVivo.tsx): o primeiro tempo correu no
// relogio, o placar ja esta na tela, e aqui so o que o tecnico pode mexer.

import { useState } from 'react'
import { barraFisico, seloOvr, seloPos } from './Celulas'
import type { Intervalo as DadosIntervalo } from '../tipos'

interface Props {
  dados: DadosIntervalo
  ocupado: boolean
  aoSeguir: (tatica: string, trocas: [number, number][]) => void
  aoDesligar: () => void
}

export function DecisoesIntervalo({ dados, ocupado, aoSeguir, aoDesligar }: Props) {
  const [tatica, setTatica] = useState(dados.tatica)
  const [trocas, setTrocas] = useState<[number, number][]>([])
  const [sai, setSai] = useState<number | null>(null)

  const saindo = new Set(trocas.map((t) => t[0]))
  const entrando = new Set(trocas.map((t) => t[1]))
  const restam = dados.trocas_restantes - trocas.length
  const nome = (id: number) =>
    dados.titulares.find((j) => j.id === id)?.nome ?? dados.banco.find((j) => j.id === id)?.nome ?? '?'

  return (
    <div className="intervalo-decisoes">
      <section className="mesa-bloco">
        <div className="painel-titulo mb-2">Mentalidade no 2o tempo</div>
        <div className="segmento" role="group" aria-label="Mentalidade">
          {dados.taticas.map((t) => (
            <button
              type="button"
              key={t}
              className={`bt-fantasma bt-mini${t === tatica ? ' ativa' : ''}`}
              aria-pressed={t === tatica}
              onClick={() => setTatica(t)}
            >
              {t}
            </button>
          ))}
        </div>
      </section>

      <section className="mesa-bloco mt-3">
        <div className="painel-titulo mb-2">
          Substituicoes · {restam > 0 ? `pode trocar mais ${restam}` : 'sem trocas'}
        </div>
        <p className="tag-fraco m-0 mb-2">
          {sai === null
            ? 'Toque em quem sai e depois em quem entra. Fisico e nota sao do primeiro tempo.'
            : `Sai ${nome(sai)}: agora escolha quem entra.`}
        </p>
        <div className="intervalo-listas">
          <ul className="intervalo-lista" aria-label="Em campo">
            {dados.titulares.map((j) => {
              const marcado = sai === j.id
              const fora = saindo.has(j.id)
              return (
                <li key={j.id}>
                  <button
                    type="button"
                    className={`intervalo-jogador${marcado ? ' marcado' : ''}${fora ? ' saiu' : ''}`}
                    disabled={fora || (restam <= 0 && !marcado)}
                    aria-pressed={marcado}
                    onClick={() => setSai(marcado ? null : j.id)}
                  >
                    {seloPos(j.vaga)}
                    <span className="intervalo-nome">
                      {j.nome}
                      {j.amarelo && <span className="lance-marca amarelo" aria-label="amarelo" />}
                      {j.lesionado && <span className="tag-critico"> lesionado</span>}
                    </span>
                    <span className="intervalo-nota">{j.nota.toFixed(1)}</span>
                    {barraFisico(j.cond)}
                  </button>
                </li>
              )
            })}
          </ul>
          <ul className="intervalo-lista" aria-label="No banco">
            {dados.banco.map((j) => {
              const usado = entrando.has(j.id)
              return (
                <li key={j.id}>
                  <button
                    type="button"
                    className={`intervalo-jogador${usado ? ' saiu' : ''}`}
                    disabled={usado || sai === null}
                    onClick={() => {
                      if (sai === null) return
                      setTrocas((t) => [...t, [sai, j.id]])
                      setSai(null)
                    }}
                  >
                    {seloPos(j.pos)}
                    <span className="intervalo-nome">{j.nome}</span>
                    {seloOvr(j.ovr)}
                    {barraFisico(j.cond)}
                  </button>
                </li>
              )
            })}
          </ul>
        </div>
        {trocas.length > 0 && (
          <ul className="partida-lista mt-2">
            {trocas.map(([quemSai, quemEntra], i) => (
              <li key={i}>
                <span className="lance-texto">
                  entra <strong>{nome(quemEntra)}</strong>, sai {nome(quemSai)}
                </span>
                <button
                  type="button"
                  className="bt-fantasma bt-mini"
                  onClick={() => setTrocas((t) => t.filter((_, k) => k !== i))}
                >
                  Desfazer
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <div className="modal-acoes mt-4">
        <button type="button" className="bt-fantasma" disabled={ocupado} onClick={aoDesligar}>
          Nao parar no intervalo
        </button>
        <button type="button" className="bt-acao" disabled={ocupado} onClick={() => aoSeguir(tatica, trocas)}>
          {ocupado ? 'Jogando…' : 'Comecar o 2o tempo'}
        </button>
      </div>
    </div>
  )
}
