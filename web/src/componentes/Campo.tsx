// O campo com o XI desenhado.
//
// As coordenadas vem prontas do Python (api/campo.py): quem sabe que um
// lateral joga na ponta e o jogo, nao a tela. Aqui so se pinta.
//
// A borda do disco e o que carrega o problema - amarelo para quem esta
// improvisado ou pendurado, vermelho para improviso grave e desgaste. Quem nao
// enxerga a diferenca de cor le a mesma coisa na lista ao lado, que repete o
// motivo por escrito: no resto do jogo a cor nunca e a unica voz.

import type { JogadorEmCampo } from '../tipos'

interface Props {
  jogadores: JogadorEmCampo[]
  vagasAbertas: number
  aoClicar?: (jogador: JogadorEmCampo) => void
  /** Titular marcado para sair: a Escalacao usa, o Painel nao. */
  selecionado?: number | null
  /** Quem mudou de vaga na ultima troca de formacao: pisca uma vez. */
  novaVaga?: Set<number>
}

function descrever(j: JogadorEmCampo) {
  const partes = [`${j.nome} (${j.pos}${j.improvisado ? ` jogando de ${j.vaga}` : ''})`,
    `overall ${j.ovr}`, `fisico ${j.cond}`]
  if (j.obs) partes.push(j.obs)
  if (j.improvisado) partes.push(`vaga ${j.vaga}`)
  return partes.join(', ')
}

export function Campo({ jogadores, vagasAbertas, aoClicar, selecionado, novaVaga }: Props) {
  return (
    <div className="campo-area">
      <div className="campo-linhas" />
      <div className="campo-meio" />
      <div className="campo-circulo" />
      <div className="campo-area-gol esq" />
      <div className="campo-area-gol dir" />

      {jogadores.map((j) => (
        <button
          key={j.id}
          type="button"
          className={`jogador ${j.estado}${j.y < 50 ? ' acima' : ''}${
            selecionado === j.id ? ' escolhido' : ''
          }${novaVaga?.has(j.id) ? ' nova-vaga' : ''}`}
          style={{ left: `${j.x}%`, top: `${j.y}%` }}
          title={descrever(j)}
          aria-label={descrever(j)}
          aria-pressed={selecionado === undefined ? undefined : selecionado === j.id}
          onClick={() => aoClicar?.(j)}
        >
          <span className="disco">{j.numero}</span>
          <span className="nome">{j.curto}</span>
        </button>
      ))}

      {/* vaga sem ninguem apto: o campo tem que mostrar o buraco, nao escondê-lo */}
      {Array.from({ length: Math.max(0, vagasAbertas) }, (_, i) => (
        <div
          key={`vazia-${i}`}
          className="jogador vazia"
          style={{ left: '50%', top: `${18 + i * 12}%` }}
          title="Sem jogador apto para esta vaga"
        >
          <span className="disco">?</span>
          <span className="nome">vaga aberta</span>
        </div>
      ))}
    </div>
  )
}
