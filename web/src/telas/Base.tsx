// A academia, em tres abas: os garotos que ja estao em casa, a peneira que
// traz candidatos (regiao e posicao escolhidas pelo tecnico) e as revelacoes
// que a base ja formou. O teto de cada garoto e uma faixa que estreita com os
// meses de observacao: subir cedo e apostar.

import { porque, AGUARDE, MARQUE } from '../motivo'
import { useEffect, useState } from 'react'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import { alternarMarca, Grade, type Coluna } from '../componentes/Grade'
import { plural } from '../formato'
import { LegendaCores } from '../componentes/LegendaCores'
import type { Garoto, TelaBase } from '../tipos'

export type AcaoBase = 'subir' | 'liberar'

interface Props {
  tela: TelaBase
  ocupado: boolean
  aoAbrirFicha: (id: number) => void
  aoAgir: (acao: AcaoBase, ids: number[]) => void
  aoAlternarFoco: (ids: number[]) => void
  aoPeneira: (regiao: string | null, foco: string | null) => void
  aoCandidato: (cid: number, aceitar: boolean) => void
}

type Aba = 'garotos' | 'peneira' | 'revelados'

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
  {
    chave: 'teto',
    rotulo: 'Teto',
    largura: '96px',
    classe: 'centro',
    render: (j) => (
      <span title={`${plural(j.obs, 'mes', 'meses')} de observacao: a faixa estreita com o tempo`}>{j.teto}</span>
    ),
  },
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

export function Base(props: Props) {
  const { tela } = props
  const [aba, setAba] = useState<Aba>('garotos')
  const novos = tela.candidatos.length
  const abas: [Aba, string][] = [
    ['garotos', `Garotos (${tela.garotos.length})`],
    ['peneira', novos ? `Peneira · ${novos} para avaliar` : 'Peneira'],
    ['revelados', 'Revelacoes'],
  ]
  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={tela.subtitulo} metricas={tela.metricas} />
      <div className="alavanca mb-3" role="tablist">
        {abas.map(([id, rotulo]) => (
          <button
            key={id}
            type="button"
            role="tab"
            aria-selected={aba === id}
            className={aba === id ? 'ativo' : ''}
            onClick={() => setAba(id)}
          >
            {rotulo}
          </button>
        ))}
      </div>
      {aba === 'garotos' && <Garotos {...props} />}
      {aba === 'peneira' && <Peneira {...props} />}
      {aba === 'revelados' && <Revelados tela={tela} />}
    </div>
  )
}

// ----------------------------------------------------------------- garotos
function Garotos({ tela, ocupado, aoAbrirFicha, aoAgir, aoAlternarFoco }: Props) {
  const [marcados, setMarcados] = useState<Set<number>>(new Set())
  // a tela voltou do servidor: marcacao antiga pode apontar para quem ja subiu
  useEffect(() => {
    setMarcados(new Set())
  }, [tela])
  const ids = [...marcados]
  const nenhum = ids.length === 0
  const lotado = tela.elenco_profissional >= tela.teto_profissional

  return (
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
          'Academia vazia. A safra nova chega na virada da temporada, e a peneira traz candidatos ' +
          'durante o ano. Suba o nivel da base na Infraestrutura para ter mais vagas.'
        }
      />
      <LegendaCores />

      <div className="barra-acoes barra-presa">
        <span className="resumo">
          elenco profissional: {tela.elenco_profissional}/{tela.teto_profissional}
          {lotado && ' — sem vaga para subir ninguem agora'}
        </span>
        <button type="button" className="bt-fantasma" title={porque([[nenhum, MARQUE]])}
        disabled={nenhum} onClick={() => aoAbrirFicha(ids[0])}>
          Ver ficha
        </button>
        <button
          type="button"
          className="bt-fantasma"
          title={porque([[nenhum, MARQUE], [ocupado, AGUARDE]], 'Liga ou desliga o treino individual dos marcados')}
          disabled={nenhum || ocupado}
          onClick={() => {
            aoAlternarFoco(ids)
            setMarcados(new Set())
          }}
        >
          Treino individual
        </button>
        <button
          type="button"
          className="bt-acao medio"
          title={porque([[nenhum, MARQUE], [ocupado, AGUARDE]])}
          disabled={nenhum || ocupado}
          onClick={() => aoAgir('subir', ids)}
        >
          Subir ao profissional
        </button>
        <button
          type="button"
          className="bt-fantasma bt-perigo"
          title={porque([[nenhum, MARQUE], [ocupado, AGUARDE]])}
          disabled={nenhum || ocupado}
          onClick={() => aoAgir('liberar', ids)}
        >
          Liberar da base
        </button>
      </div>
    </section>
  )
}

// ----------------------------------------------------------------- peneira
function Peneira({ tela, ocupado, aoPeneira, aoCandidato }: Props) {
  const pen = tela.peneira
  const [regiao, setRegiao] = useState(pen.atual?.regiao ?? pen.regioes[0]?.id ?? '')
  const [foco, setFoco] = useState<string>(pen.atual?.foco ?? '')
  const estado = pen.atual
    ? `Ligada no ${pen.atual.nome}${pen.atual.foco ? ` (${pen.atual.foco})` : ''}, ${pen.atual.custo} por semana. Proxima leva em ${plural(pen.atual.proxima, 'semana')}.`
    : `Desligada. Escolha onde procurar: a cada ${pen.a_cada} semanas chegam candidatos, e cada um espera ${pen.vale} semanas pela sua resposta.`
  return (
    <>
      <section className="painel enxuto">
        <div className="painel-titulo mb-2">
          Peneira
        </div>
        <p className="tag-fraco m-0 mb-3">
          {estado}
        </p>
        <div className="regioes-peneira" role="radiogroup" aria-label="Regiao da peneira">
          {pen.regioes.map((r) => (
            <label key={r.id} className={`regiao-peneira${regiao === r.id ? ' ativa' : ''}`}>
              <input type="radio" name="regiao" checked={regiao === r.id} onChange={() => setRegiao(r.id)} />
              <strong>{r.nome}</strong>
              <span className="tag-fraco">
                talento {r.talento} · revela {r.vies}
              </span>
              <span className="tag-fraco">{r.custo} por semana</span>
            </label>
          ))}
        </div>
        <div className="linha-peneira">
          <label className="tag-fraco">
            Posicao{' '}
            <select className="campo-texto" value={foco} onChange={(e) => setFoco(e.target.value)}>
              <option value="">qualquer</option>
              {pen.posicoes.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </label>
          <div className="espaco" />
          {pen.atual && (
            <button type="button" className="bt-fantasma" title={porque([[ocupado, AGUARDE]])}
            disabled={ocupado} onClick={() => aoPeneira(null, null)}>
              Desligar
            </button>
          )}
          <button
            type="button"
            className="bt-acao medio"
            title={porque([[ocupado, AGUARDE], [!regiao, 'Escolha uma regiao']])}
            disabled={ocupado || !regiao}
            onClick={() => aoPeneira(regiao, foco || null)}
          >
            {pen.atual ? 'Mudar peneira' : 'Ligar peneira'}
          </button>
        </div>
      </section>

      <section className="painel enxuto">
        <div className="painel-titulo mb-2">
          Candidatos · {tela.vagas_livres === 1 ? '1 vaga livre' : `${tela.vagas_livres} vagas livres`} na base
        </div>
        {tela.candidatos.length === 0 ? (
          <div className="vazio justo">
            Nenhum candidato esperando. Com a peneira ligada, eles chegam a cada {pen.a_cada} semanas.
          </div>
        ) : (
          tela.candidatos.map((k) => (
            <div className="linha-proposta" key={k.cid}>
              <span>
                <strong>{k.nome}</strong>{' '}
                <span className="tag-fraco">
                  {k.pos} · {k.idade} anos · overall {k.ovr} · teto {k.faixa} · {k.regiao} · decide em {plural(k.semanas, 'semana')}
                </span>
              </span>
              <span className="modal-acoes">
                <button type="button" className="bt-fantasma" title={porque([[ocupado, AGUARDE]])}
                disabled={ocupado} onClick={() => aoCandidato(k.cid, false)}>
                  Dispensar
                </button>
                <button
                  type="button"
                  className="bt-fantasma"
                  title={porque([[ocupado, AGUARDE], [tela.vagas_livres === 0, 'A base esta cheia: libere alguem ou amplie a academia']], tela.vagas_livres === 0 ? 'Base cheia: libere alguem antes' : undefined)}
                  disabled={ocupado || tela.vagas_livres === 0}
                  onClick={() => aoCandidato(k.cid, true)}
                >
                  Trazer para a base
                </button>
              </span>
            </div>
          ))
        )}
      </section>
    </>
  )
}

// ---------------------------------------------------------------- revelados
function Revelados({ tela }: { tela: TelaBase }) {
  return (
    <section className="painel enxuto">
      <div className="painel-titulo mb-2">
        Revelacoes da academia
      </div>
      {tela.revelados.length === 0 ? (
        <div className="vazio justo">
          Ninguem subiu da base ainda. Quem subir ao profissional fica registrado aqui.
        </div>
      ) : (
        tela.revelados.map((r, i) => (
          <div key={i} className="linha-proposta">
            <span>
              <strong className={r.em_casa ? 'tag-titular' : undefined}>{r.nome}</strong>{' '}
              <span className="tag-fraco">
                {r.pos} · subiu em {r.temporada} com {r.ovr_subida}
                {r.ovr_hoje !== null && ` · hoje ${r.ovr_hoje}`} · {r.onde}
              </span>
            </span>
          </div>
        ))
      )}
    </section>
  )
}
