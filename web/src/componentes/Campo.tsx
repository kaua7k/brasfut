// O campo com o XI desenhado.
//
// As coordenadas vem prontas do Python (api/campo.py): quem sabe que um
// lateral joga na ponta e o jogo, nao a tela. Aqui so se pinta.
//
// O disco mostra o overall: e o numero que o tecnico procura ao bater o olho
// no time. A borda do disco e o que carrega o problema - amarelo para quem
// esta improvisado ou pendurado, vermelho para improviso grave e desgaste.
// Quem nao enxerga a diferenca de cor le a mesma coisa na lista ao lado, que
// repete o motivo por escrito: no resto do jogo a cor nunca e a unica voz.

import type { JogadorEmCampo } from '../tipos'

interface Props {
  jogadores: JogadorEmCampo[]
  vagasAbertas: number
  aoClicar?: (jogador: JogadorEmCampo) => void
  /** Titulares marcados para a troca: a Escalacao usa, o Painel nao. */
  marcados?: Set<number>
  /** Quem mudou de vaga na ultima troca de formacao: pisca uma vez. */
  novaVaga?: Set<number>
}

function descrever(j: JogadorEmCampo) {
  const partes = [`${j.nome} (${j.pos}${j.improvisado ? ` jogando de ${j.vaga}` : ''})`,
    `overall ${j.ovr}`, `fisico ${j.cond}`]
  if (j.obs) partes.push(j.obs)
  return partes.join(', ')
}

export function Campo({ jogadores, vagasAbertas, aoClicar, marcados, novaVaga }: Props) {
  const clicavel = Boolean(aoClicar)
  return (
    <div className="campo-area">
      <div className="campo-linhas" />
      <div className="campo-meio" />
      <div className="campo-circulo" />
      <div className="campo-area-gol esq" />
      <div className="campo-area-gol dir" />

      {jogadores.map((j) => {
        const marcado = marcados?.has(j.id) ?? false
        const classe = `jogador ${j.estado}${j.y < 50 ? ' acima' : ''}${marcado ? ' escolhido' : ''}${
          novaVaga?.has(j.id) ? ' nova-vaga' : ''
        }`
        const conteudo = (
          <>
            <span className="disco">{j.ovr}</span>
            <span className="nome">{j.curto}</span>
          </>
        )
        // sem acao (Painel, previa do editor) o disco nao finge ser botao
        if (!clicavel) {
          return (
            <div
              key={j.id}
              className={classe}
              style={{ left: `${j.x}%`, top: `${j.y}%` }}
              title={descrever(j)}
              role="img"
              aria-label={descrever(j)}
            >
              {conteudo}
            </div>
          )
        }
        return (
          <button
            key={j.id}
            type="button"
            className={classe}
            style={{ left: `${j.x}%`, top: `${j.y}%` }}
            title={descrever(j)}
            aria-label={descrever(j)}
            aria-pressed={marcado}
            onClick={() => aoClicar?.(j)}
          >
            {conteudo}
          </button>
        )
      })}

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
