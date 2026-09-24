// A academia.
//
// Antes de existir esta tela no jogo, a base era so um numero na
// Infraestrutura: o garoto nascia na virada do ano e caia direto no
// profissional sem ninguem ver.

import { useEffect, useState } from 'react'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import { alternarMarca, Grade, type Coluna } from '../componentes/Grade'
import type { Garoto, TelaBase } from '../tipos'

export type AcaoBase = 'subir' | 'liberar'

interface Props {
  tela: TelaBase
  ocupado: boolean
  aoAbrirFicha: (id: number) => void
  aoAgir: (acao: AcaoBase, ids: number[]) => void
  aoAlternarFoco: (ids: number[]) => void
}

const COLUNAS: Coluna<Garoto>[] = [
  { chave: 'pos', rotulo: 'Pos', largura: '46px', classe: 'centro', render: (j) => j.pos },
  {
    chave: 'nome',
    rotulo: 'Jogador',
    largura: 'minmax(140px, 1.6fr)',
    classe: 'corta',
    render: (j) => <span className={`tag-${j.tag}`}>{j.nome}</span>,
  },
  { chave: 'idade', rotulo: 'Idade', largura: '52px', classe: 'num', render: (j) => j.idade },
  { chave: 'ovr', rotulo: 'Ovr', largura: '44px', classe: 'num', render: (j) => j.ovr },
  { chave: 'teto', rotulo: 'Teto', largura: '80px', classe: 'centro', render: (j) => j.teto },
  {
    chave: 'treino',
    rotulo: 'Treino',
    largura: '64px',
    classe: 'centro',
    render: (j) => (j.em_foco ? 'sim' : '-'),
  },
  {
    chave: 'sit',
    rotulo: 'Situacao',
    largura: 'minmax(120px, 1.2fr)',
    classe: 'corta',
    render: (j) => (
      <span className={j.estado === 'ok' ? 'tag-ok' : j.estado === 'critico' ? 'linha-critica' : undefined}>
        {j.situacao}
      </span>
    ),
  },
]

export function Base({ tela, ocupado, aoAbrirFicha, aoAgir, aoAlternarFoco }: Props) {
  const [marcados, setMarcados] = useState<Set<number>>(new Set())
  // a tela voltou do servidor: marcacao antiga pode apontar para quem ja subiu
  useEffect(() => {
    setMarcados(new Set())
  }, [tela])
  const ids = [...marcados]
  const nenhum = ids.length === 0
  const lotado = tela.elenco_profissional >= tela.teto_profissional

  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={tela.subtitulo} metricas={tela.metricas} />

      <section className="painel painel-lista">
        <Grade
          colunas={COLUNAS}
          itens={tela.garotos}
          idDe={(j) => j.id}
          marcados={marcados}
          aoMarcar={(id) => setMarcados((s) => alternarMarca(s, id))}
          aoMarcarTodos={(ids) => setMarcados(new Set(ids))}
          aoAbrir={(j) => aoAbrirFicha(j.id)}
          nomeDe={(j) => j.nome}
          memoria="base"
          vazio={
            'Academia vazia. A safra nova chega na virada da temporada — suba o nivel da ' +
            'base na Infraestrutura para formar mais gente.'
          }
        />

        <div className="barra-acoes barra-presa">
          <span className="resumo">
            elenco profissional: {tela.elenco_profissional}/{tela.teto_profissional}
            {lotado && ' — sem vaga para subir ninguem agora'}
          </span>
          <button
            type="button"
            className="bt-fantasma"
            disabled={nenhum}
            onClick={() => aoAbrirFicha(ids[0])}
          >
            Ver ficha
          </button>
          <button
            type="button"
            className="bt-fantasma"
            disabled={nenhum || ocupado}
            title="Liga ou desliga o treino individual dos marcados"
            onClick={() => {
              aoAlternarFoco(ids)
              setMarcados(new Set())
            }}
          >
            Treino individual
          </button>
          <button
            type="button"
            className="bt-acao"
            style={{ height: 36, borderRadius: 'var(--raio-p)', padding: '0 16px' }}
            disabled={nenhum || ocupado}
            onClick={() => aoAgir('subir', ids)}
          >
            Subir ao profissional
          </button>
          <button
            type="button"
            className="bt-fantasma bt-perigo"
            disabled={nenhum || ocupado}
            onClick={() => aoAgir('liberar', ids)}
          >
            Liberar da base
          </button>
        </div>
      </section>
    </div>
  )
}
