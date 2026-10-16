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

import type { CSSProperties } from 'react'
import { useTelaEstreita } from '../estreita'
import type { JogadorEmCampo } from '../tipos'

// a vaga pinta o pip do disco com a mesma cor do selo de posicao das listas
const LINHA: Record<string, string> = { GOL: 'gol', ZAG: 'def', LAT: 'lat', VOL: 'vol', MEI: 'mei', ATA: 'ata' }

// anel de condicao: mesmos cortes da barra de fisico das listas
function condicao(cond: number) {
  return cond < 45 ? 'critico' : cond < 65 ? 'atencao' : 'ok'
}

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
  const partes = [`${j.nome}${j.capitao ? ' (capitao)' : ''} (${j.pos}${j.improvisado ? ` jogando de ${j.vaga}` : ''})`,
    `overall ${j.ovr}`, `fisico ${j.cond}`]
  if (j.obs) partes.push(j.obs)
  return partes.join(', ')
}

export function Campo({ jogadores, vagasAbertas, aoClicar, marcados, novaVaga }: Props) {
  const clicavel = Boolean(aoClicar)
  // no celular o campo fica em pe: o gol do time embaixo e o ataque em cima.
  // x (de gol a gol) vira a altura e y (de lado a lado) vira a largura.
  const vertical = useTelaEstreita()
  const ponto = (x: number, y: number) => (vertical ? { left: `${y}%`, top: `${100 - x}%` } : { left: `${x}%`, top: `${y}%` })
  return (
    <div className={`campo-area${vertical ? ' vertical' : ''}`}>
      <div className="campo-linhas" />
      <div className="campo-meio" />
      <div className="campo-circulo" />
      <div className="campo-ponto" />
      <div className="campo-area-gol esq" />
      <div className="campo-area-gol dir" />
      <div className="campo-pequena esq" />
      <div className="campo-pequena dir" />

      {jogadores.map((j) => {
        const marcado = marcados?.has(j.id) ?? false
        const linha = LINHA[j.vaga] ?? ''
        const acima = vertical ? false : j.y < 50
        const classe = `jogador ${j.estado} linha-${linha}${acima ? ' acima' : ''}${marcado ? ' escolhido' : ''}${
          novaVaga?.has(j.id) ? ' nova-vaga' : ''
        }`
        const conteudo = (
          <>
            <span className={`anel ${condicao(j.cond)}`} style={{ '--cond': `${Math.max(0, Math.min(100, j.cond))}%` } as CSSProperties}>
              <span className="disco">{j.ovr}</span>
              <span className="pip-pos">{j.vaga}</span>
              {j.capitao && <span className="pip-capitao" aria-hidden="true">C</span>}
            </span>
            <span className="nome">{j.curto}</span>
          </>
        )
        // sem acao (Painel, previa do editor) o disco nao finge ser botao
        if (!clicavel) {
          return (
            <div
              key={j.id}
              className={classe}
              style={ponto(j.x, j.y)}
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
            style={ponto(j.x, j.y)}
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
          style={vertical ? { left: `${18 + i * 12}%`, top: '50%' } : { left: '50%', top: `${18 + i * 12}%` }}
          title="Sem jogador apto para esta vaga"
        >
          <span className="anel">
            <span className="disco">?</span>
          </span>
          <span className="nome">vaga aberta</span>
        </div>
      ))}
    </div>
  )
}
