// A partida que o motor ja calculava e a web escondia.
//
// ResumoPartida e o cartao compacto que aparece na volta do avanco (Painel e
// fim do Simular): mandante primeiro, gols e cartoes com minuto, posse,
// chutes e melhor em campo. As bolinhas V/E/D das ultimas partidas trocam o
// jogo mostrado. "Ver detalhes" abre DetalhePartida com notas, substituicoes
// e o resto das estatisticas - tudo ja veio no mesmo pedido, sem outra
// chamada a API.

import { useState } from 'react'
import { iconeDeEstado } from '../icones'
import type { Estado, Lado, LinhaNota, Partida } from '../tipos'

interface PropsResumo {
  partidas: Partida[]
  /** quantas bolinhas de historico mostrar (0 esconde) */
  historico?: number
  alerta?: { texto: string; estado: Estado } | null
}

const LETRA: Record<Partida['resultado'], string> = { V: 'vitoria', E: 'empate', D: 'derrota' }

export function ResumoPartida({ partidas, historico = 5, alerta }: PropsResumo) {
  const [escolhida, setEscolhida] = useState<string | null>(null)
  const [detalhe, setDetalhe] = useState(false)
  if (!partidas.length) return null
  const p = partidas.find((x) => x.chave === escolhida) ?? partidas[partidas.length - 1]
  const recentes = historico > 0 ? partidas.slice(-historico) : []

  return (
    <section className="painel partida" aria-label="Ultima partida">
      <div className="partida-topo">
        <span className="painel-titulo">
          {p.comp} · {p.rodada}
        </span>
        {recentes.length > 1 && (
          <div className="partida-historico">
            <span className="painel-titulo">
              Ultimos {recentes.length}
              <span className="tag-fraco"> · antigo → recente</span>
            </span>
            <div className="forma" role="group" aria-label="Escolher partida">
              {recentes.map((x) => (
                <button
                  type="button"
                  key={x.chave}
                  className={`forma-badge ${x.resultado}${x.chave === p.chave ? ' ativa' : ''}`}
                  aria-pressed={x.chave === p.chave}
                  title={`${x.times[0]} ${x.placar[0]} x ${x.placar[1]} ${x.times[1]} · ${x.comp}`}
                  aria-label={`${LETRA[x.resultado]}: ${x.times[0]} ${x.placar[0]} x ${x.placar[1]} ${x.times[1]}`}
                  onClick={() => setEscolhida(x.chave)}
                >
                  {x.resultado}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="partida-placar">
        <span className={`partida-time${p.eu === 0 ? ' eu' : ''}`}>{p.times[0]}</span>
        <span className={`placar-numero ${p.estado}`}>
          {p.placar[0]} x {p.placar[1]}
        </span>
        <span className={`partida-time${p.eu === 1 ? ' eu' : ''}`}>{p.times[1]}</span>
      </div>
      {p.detalhes.decisao && <div className="partida-decisao">{p.detalhes.decisao}</div>}

      <div className="partida-lances">
        <Lances p={p} lado={0} />
        <Lances p={p} lado={1} />
      </div>

      <div className="partida-numeros">
        <span>
          Posse <strong>{p.posse[0]}%</strong> x <strong>{p.posse[1]}%</strong>
        </span>
        <span>
          Chutes <strong>{p.chutes[0]}</strong> x <strong>{p.chutes[1]}</strong>
          <span className="tag-fraco">
            {' '}
            ({p.no_gol[0]} x {p.no_gol[1]} no gol)
          </span>
        </span>
        {p.melhor && (
          <span>
            Melhor em campo: <strong>{p.melhor.nome}</strong>
            <span className="tag-fraco">
              {' '}
              ({p.melhor.vaga}, {p.melhor.time})
            </span>{' '}
            <strong className={classeDaNota(p.melhor.nota)}>{p.melhor.nota.toFixed(1)}</strong>
          </span>
        )}
        <button type="button" className="bt-fantasma empurra" onClick={() => setDetalhe(true)}>
          Ver detalhes
        </button>
      </div>

      {alerta && (
        <div className={`alerta-fase ${alerta.estado}`}>
          {iconeDeEstado(alerta.estado, 16)}
          {alerta.texto}
        </div>
      )}

      {detalhe && <DetalhePartida p={p} aoFechar={() => setDetalhe(false)} />}
    </section>
  )
}

function Lances({ p, lado }: { p: Partida; lado: Lado }) {
  const itens = [
    ...p.gols
      .filter((g) => g.lado === lado)
      .map((g) => ({ minuto: g.minuto, tipo: 'gol' as const, texto: g.autor, extra: g.assist })),
    ...p.cartoes
      .filter((c) => c.lado === lado)
      .map((c) => ({ minuto: c.minuto, tipo: c.tipo, texto: c.nome, extra: '' })),
    ...p.instrucoes
      .filter((x) => x.lado === lado)
      .map((x) => ({ minuto: x.minuto, tipo: 'instrucao' as const, texto: `vira ${x.tatica}`, extra: x.motivo })),
  ].sort((a, b) => a.minuto - b.minuto)
  return (
    <ul className={`partida-lista${lado === 1 ? ' fora' : ''}`} aria-label={`Lances do ${p.times[lado]}`}>
      {itens.length === 0 && <li className="tag-fraco">sem gol nem cartao</li>}
      {itens.map((l, i) => (
        <li key={i}>
          <span className="lance-minuto">{l.minuto}'</span>
          <span className={`lance-marca ${l.tipo}`} aria-hidden="true" />
          <span className="lance-texto">
            {l.texto}
            {l.tipo === 'instrucao' ? (
              <span className="tag-fraco"> · {l.extra}</span>
            ) : (
              <>
                <span className="so-leitor"> ({l.tipo === 'gol' ? 'gol' : `cartao ${l.tipo}`})</span>
                {l.extra && <span className="tag-fraco"> · assist. {l.extra}</span>}
              </>
            )}
          </span>
        </li>
      ))}
    </ul>
  )
}

function classeDaNota(nota: number) {
  if (nota >= 7) return 'txt-ok'
  if (nota < 5.5) return 'txt-critico'
  return ''
}

function TabelaNotas({ titulo, linhas }: { titulo: string; linhas: LinhaNota[] }) {
  return (
    <table className="partida-notas">
      <caption className="painel-titulo">{titulo}</caption>
      <thead>
        <tr>
          <th scope="col">Vaga</th>
          <th scope="col">Jogador</th>
          <th scope="col" className="a-direita">
            Nota
          </th>
        </tr>
      </thead>
      <tbody>
        {linhas.map((l, i) => (
          <tr key={i}>
            <td>{l.vaga}</td>
            <td>{l.nome}</td>
            <td className={`a-direita negrito ${classeDaNota(l.nota)}`}>{l.nota.toFixed(1)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export function DetalhePartida({ p, aoFechar }: { p: Partida; aoFechar: () => void }) {
  const d = p.detalhes
  return (
    <div
      className="fundo-modal"
      role="dialog"
      aria-modal="true"
      aria-label={`${p.times[0]} ${p.placar[0]} x ${p.placar[1]} ${p.times[1]}`}
      onClick={aoFechar}
      onKeyDown={(e) => {
        // dentro do Simular: o Esc fecha so o detalhe, nao o dialogo de tras
        e.stopPropagation()
        if (e.key === 'Escape') aoFechar()
      }}
    >
      <div className="modal modal-largo" onClick={(e) => e.stopPropagation()}>
        <h2>
          {p.times[0]} {p.placar[0]} x {p.placar[1]} {p.times[1]}
        </h2>
        <p className="tag-fraco m-0 mb-3">
          {p.comp} · {p.rodada}
          {d.publico && ` · ${d.publico}`}
        </p>
        {d.decisao && <p className="txt-atencao mt-1 mb-3">{d.decisao}</p>}

        <div className="partida-detalhe">
          <TabelaNotas titulo={p.times[0]} linhas={d.notas[0]} />
          <TabelaNotas titulo={p.times[1]} linhas={d.notas[1]} />
        </div>

        <div className="partida-detalhe mt-3">
          <section>
            <h3 className="painel-titulo mb-2">Estatisticas</h3>
            <table className="partida-estat">
              <tbody>
                {d.estatisticas.map((e) => (
                  <tr key={e.rotulo}>
                    <td className="a-direita negrito">{e.valores[0]}</td>
                    <th scope="row">{e.rotulo}</th>
                    <td className="negrito">{e.valores[1]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
          <section>
            <h3 className="painel-titulo mb-2">Substituicoes</h3>
            {d.subs.length === 0 && <p className="tag-fraco m-0">ninguem saiu</p>}
            <ul className="partida-lista">
              {d.subs.map((s, i) => (
                <li key={i}>
                  <span className="lance-minuto">{s.minuto}'</span>
                  <span className="lance-texto">
                    entra {s.entra}, sai {s.sai}
                    <span className="tag-fraco"> · {p.times[s.lado]}</span>
                  </span>
                </li>
              ))}
            </ul>
            {d.lesoes.length > 0 && (
              <>
                <h3 className="painel-titulo mt-3 mb-2">Lesoes</h3>
                <ul className="partida-lista">
                  {d.lesoes.map((l, i) => (
                    <li key={i} className="txt-critico">
                      <span className="lance-minuto">{l.minuto}'</span>
                      <span className="lance-texto">
                        {l.nome}
                        <span className="tag-fraco"> · {p.times[l.lado]}</span>
                      </span>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </section>
        </div>

        <div className="modal-acoes mt-4">
          <button type="button" className="bt-acao" onClick={aoFechar}>
            Fechar
          </button>
        </div>
      </div>
    </div>
  )
}
