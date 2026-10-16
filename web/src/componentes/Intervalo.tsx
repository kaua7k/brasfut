// O intervalo do meu jogo de liga: o primeiro tempo ja foi jogado e o segundo
// espera a decisao do tecnico. Da para trocar a mentalidade e fazer
// substituicoes (titular que sai x reserva que entra, ate o limite do jogo).
// O resto da semana so roda depois do "Comecar o 2o tempo".

import { useState } from 'react'
import { barraFisico, seloOvr, seloPos } from './Celulas'
import { Escudo } from './Escudo'
import type { Intervalo as DadosIntervalo } from '../tipos'

interface Props {
  dados: DadosIntervalo
  ocupado: boolean
  aoSeguir: (tatica: string, trocas: [number, number][]) => void
  aoDesligar: () => void
}

export function Intervalo({ dados, ocupado, aoSeguir, aoDesligar }: Props) {
  const [tatica, setTatica] = useState(dados.tatica)
  const [trocas, setTrocas] = useState<[number, number][]>([])
  const [sai, setSai] = useState<number | null>(null)

  const saindo = new Set(trocas.map((t) => t[0]))
  const entrando = new Set(trocas.map((t) => t[1]))
  const restam = dados.trocas_restantes - trocas.length
  const nome = (id: number) =>
    dados.titulares.find((j) => j.id === id)?.nome ?? dados.banco.find((j) => j.id === id)?.nome ?? '?'
  const meu = dados.eu
  const [gm, gs] = meu === 0 ? dados.placar : [dados.placar[1], dados.placar[0]]
  const estado = gm > gs ? 'ok' : gm === gs ? 'atencao' : 'critico'

  return (
    <div className="fundo-modal" role="dialog" aria-modal="true" aria-label="Intervalo">
      <div className="modal modal-largo intervalo">
        <p className="tag-fraco detalhe-sub">{dados.comp} · intervalo</p>
        <div className="detalhe-placar">
          <div className={`detalhe-time${meu === 0 ? ' eu' : ''}`}>
            <Escudo nome={dados.times[0]} tamanho={44} />
            <h2>{dados.times[0]}</h2>
          </div>
          <div className="ao-vivo-centro">
            <div className={`placar-numero detalhe-gols ${estado}`}>
              {dados.placar[0]} x {dados.placar[1]}
            </div>
            <div className="ao-vivo-fase">fim do 1o tempo</div>
          </div>
          <div className={`detalhe-time${meu === 1 ? ' eu' : ''}`}>
            <Escudo nome={dados.times[1]} tamanho={44} />
            <h2>{dados.times[1]}</h2>
          </div>
        </div>
        <p className="tag-fraco a-centro m-0">
          Posse {dados.posse[0]}% x {dados.posse[1]}% · chutes {dados.chutes[0]} x {dados.chutes[1]} (
          {dados.no_gol[0]} x {dados.no_gol[1]} no gol)
        </p>

        {dados.lances.length > 0 && (
          <ul className="partida-lista mt-3" aria-label="Lances do primeiro tempo">
            {dados.lances.map((l, i) => (
              <li key={i}>
                <span className="lance-minuto">{l.minuto}'</span>
                <span className={`lance-marca ${l.tipo}`} aria-hidden="true" />
                <span className="lance-texto">
                  {l.tipo === 'gol' ? <strong>GOL! {l.texto}</strong> : l.texto}
                  <span className="tag-fraco"> · {dados.times[l.lado]}</span>
                  {l.extra && <span className="tag-fraco"> · {l.extra}</span>}
                </span>
              </li>
            ))}
          </ul>
        )}

        <section className="mesa-bloco mt-3">
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
              ? 'Clique em quem sai e depois em quem entra. Fisico e nota sao do primeiro tempo.'
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
            Nao parar mais no intervalo
          </button>
          <button
            type="button"
            className="bt-acao"
            disabled={ocupado}
            onClick={() => aoSeguir(tatica, trocas)}
          >
            Comecar o 2o tempo
          </button>
        </div>
      </div>
    </div>
  )
}
