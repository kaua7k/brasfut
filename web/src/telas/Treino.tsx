// Regime da semana e trabalho individual: onde se decide quem evolui.
//
// Cada regime mostra o proprio preco na cara - evolucao, fisico e lesao - com
// o sinal ja julgado pelo servidor: lesao subindo e vermelho mesmo sendo um
// numero positivo. A tela nao decide o que e bom.

import { useEffect, useState } from 'react'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import { alternarMarca, Grade, type Coluna } from '../componentes/Grade'
import type { JogadorTreino, TelaTreino } from '../tipos'

export type AcaoTreino =
  | { tipo: 'regime'; nome: string }
  | { tipo: 'foco'; ids: number[] }
  | { tipo: 'limpar' }

interface Props {
  tela: TelaTreino
  ocupado: boolean
  aoAbrirFicha: (id: number) => void
  aoAgir: (acao: AcaoTreino) => void
}

const COLUNAS: Coluna<JogadorTreino>[] = [
  {
    chave: 'foco',
    rotulo: 'Individual',
    largura: '78px',
    classe: 'centro',
    render: (j) => (j.em_foco ? <span className="tag-ok">sim</span> : '-'),
  },
  { chave: 'pos', rotulo: 'Pos', largura: '46px', classe: 'centro', render: (j) => j.pos },
  {
    chave: 'nome',
    rotulo: 'Jogador',
    largura: 'minmax(150px, 1.6fr)',
    classe: 'corta',
    render: (j) => (
      <span className={`tag-${j.tag}`}>
        {j.nome}
        {j.base && <span className="tag-fraco"> (base)</span>}
      </span>
    ),
  },
  { chave: 'idade', rotulo: 'Idade', largura: '52px', classe: 'num', render: (j) => j.idade },
  { chave: 'ovr', rotulo: 'Ovr', largura: '44px', classe: 'num', render: (j) => j.ovr },
  {
    chave: 'margem',
    rotulo: 'Margem',
    largura: '72px',
    classe: 'num',
    render: (j) => (j.margem > 0 ? `+${j.margem}` : <span className="tag-fraco">no teto</span>),
    ordem: (j) => j.margem,
  },
  {
    chave: 'evo',
    rotulo: 'Evolui por mes',
    largura: '112px',
    classe: 'num',
    render: (j) => <span className={j.evo.startsWith('-') ? 'linha-critica' : undefined}>{j.evo}</span>,
  },
]

export function Treino({ tela, ocupado, aoAbrirFicha, aoAgir }: Props) {
  const [marcados, setMarcados] = useState<Set<number>>(new Set())
  useEffect(() => {
    setMarcados(new Set())
  }, [tela])
  const ids = [...marcados]
  const marcadosJs = tela.jogadores.filter((j) => marcados.has(j.id))

  // o botao diz o que o clique VAI fazer, nao os dois caminhos
  const todosEmFoco = marcadosJs.length > 0 && marcadosJs.every((j) => j.em_foco)
  const rotuloFoco = todosEmFoco ? 'Remover do treino individual' : 'Alternar treino individual'
  const lotado = tela.em_foco >= tela.vagas

  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={tela.subtitulo} metricas={tela.metricas} />

      <div className="painel-titulo">Regime da semana</div>
      <div className="regimes" role="radiogroup" aria-label="Regime de treino">
        {tela.regimes.map((r) => (
          <button
            type="button"
            role="radio"
            aria-checked={r.ativo}
            key={r.nome}
            className={`regime${r.ativo ? ' ativo' : ''}`}
            disabled={ocupado}
            onClick={() => !r.ativo && aoAgir({ tipo: 'regime', nome: r.nome })}
          >
            <span className="regime-topo">
              <strong>{r.nome}</strong>
              {r.ativo && <span className="tag-ok regime-uso">EM USO</span>}
            </span>
            <span className="regime-desc">{r.desc}</span>
            <span className="regime-efeitos">
              {r.efeitos.map((e) => (
                <span key={e.nome} className={`tag-${e.estado}`}>
                  {e.nome} {e.texto}
                </span>
              ))}
            </span>
          </button>
        ))}
      </div>

      <div>
        <div className="painel-titulo">Trabalho individual</div>
        <div className="sub-linha">
          Quem esta na lista evolui 50% mais rapido. Cada nome custa {tela.custo_por_nome} por semana.
        </div>
      </div>
      <section className="painel painel-lista">
        <Grade
          colunas={COLUNAS}
          itens={tela.jogadores}
          idDe={(j) => j.id}
          nomeDe={(j) => j.nome}
          marcados={marcados}
          aoMarcar={(id) => setMarcados((s) => alternarMarca(s, id))}
          aoMarcarTodos={(ids) => setMarcados(new Set(ids))}
          aoAbrir={(j) => aoAbrirFicha(j.id)}
          memoria="treino"
        />
        <div className="barra-acoes barra-presa">
          <span className="resumo">
            {tela.em_foco}/{tela.vagas} vagas do CT em uso
            {lotado && ' — tire alguem para colocar outro'} · evolui = ganho de overall por mes, ja com
            regime e treino individual
          </span>
          <button
            type="button"
            className="bt-fantasma"
            disabled={ids.length === 0}
            onClick={() => aoAbrirFicha(ids[0])}
          >
            Ver ficha
          </button>
          <button
            type="button"
            className="bt-fantasma"
            disabled={ocupado || tela.em_foco === 0}
            onClick={() => aoAgir({ tipo: 'limpar' })}
          >
            Limpar a lista
          </button>
          <button
            type="button"
            className="bt-acao bt-media"
            disabled={ocupado || ids.length === 0}
            onClick={() => {
              aoAgir({ tipo: 'foco', ids })
              setMarcados(new Set())
            }}
          >
            {rotuloFoco}
          </button>
        </div>
      </section>
    </div>
  )
}
