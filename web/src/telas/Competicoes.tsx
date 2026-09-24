// Competicoes: cada torneio com a profundidade que ele tem.
//
// Pontos corridos mostra a tabela inteira ao lado das rodadas, com o
// navegador de rodada abrindo na que vem - e os meus jogos numa faixa propria.
// Mata-mata mostra fase por fase: ida, volta, agregado e penaltis nas jogadas,
// os confrontos ja sorteados da proxima e o que ainda falta.
//
// O seletor separa os torneios do meu clube dos outros: sao ate trinta
// estaduais no ano, e botao para cada um afogaria os quatro que importam.

import { useEffect, useState } from 'react'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import { Grade, type Coluna } from '../componentes/Grade'
import { iconeDeEstado } from '../icones'
import type {
  DetalheCopa,
  DetalhePontos,
  FaseCopa,
  JogoCopa,
  LinhaClassificacao,
  TelaCompeticoes,
} from '../tipos'

interface Props {
  tela: TelaCompeticoes
  ocupado: boolean
  aoTrocar: (alvo: string) => void
}

const COLUNAS: Coluna<LinhaClassificacao>[] = [
  {
    chave: 'pos',
    rotulo: '#',
    largura: '44px',
    classe: 'num',
    render: (l) => (
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
        <i className="marcador-zona" />
        {l.pos}
      </span>
    ),
  },
  { chave: 'clube', rotulo: 'Clube', largura: 'minmax(110px, 1fr)', classe: 'corta', render: (l) => l.clube },
  { chave: 'p', rotulo: 'P', largura: '34px', classe: 'num', render: (l) => <strong>{l.p}</strong> },
  { chave: 'j', rotulo: 'J', largura: '30px', classe: 'num', render: (l) => l.j },
  { chave: 'v', rotulo: 'V', largura: '30px', classe: 'num', render: (l) => l.v },
  { chave: 'e', rotulo: 'E', largura: '30px', classe: 'num', render: (l) => l.e },
  { chave: 'd', rotulo: 'D', largura: '30px', classe: 'num', render: (l) => l.d },
  { chave: 'sg', rotulo: 'SG', largura: '38px', classe: 'num', render: (l) => (l.sg > 0 ? `+${l.sg}` : l.sg) },
]

function placar(gc: number | null, gf: number | null) {
  return gc === null || gf === null ? 'x' : `${gc} x ${gf}`
}

// ------------------------------------------------------------ pontos corridos
function Pontos({ d }: { d: DetalhePontos }) {
  const [rodada, setRodada] = useState(d.rodada_atual)
  useEffect(() => {
    setRodada(d.rodada_atual)
  }, [d.id, d.rodada_atual])
  const r = d.rodadas[rodada]
  // estadual: com o mata-mata em curso, as fases vem antes da primeira fase;
  // antes disso, o chaveamento a definir fica embaixo das tabelas
  const emMata = d.mata?.some((f) => f.estado !== 'futura') ?? false
  const fasesMata = d.mata && (
    <>
      {[...d.mata].reverse().map((f) => (
        <Fase f={f} key={`${d.id}-${f.nome}`} />
      ))}
    </>
  )

  return (
    <>
      {d.situacao && <Situacao s={d.situacao} campeao={null} />}

      {d.meus_jogos.length > 0 && (
        <section className="painel meus-jogos" aria-label="Seus jogos">
          <div className="painel-titulo">Seus jogos</div>
          <div className="meus-jogos-faixa">
            {d.meus_jogos.map((j) => (
              <button
                type="button"
                key={j.rodada}
                className={`jogo-chip ${j.resultado ?? 'aberto'}${j.rodada - 1 === rodada ? ' ativo' : ''}`}
                title={`Rodada ${j.rodada}: ${j.casa} ${placar(j.gc, j.gf)} ${j.fora}`}
                onClick={() => setRodada(j.rodada - 1)}
              >
                <span className="jc-rodada">R{j.rodada}</span>
                <span className="jc-placar">{j.resultado ? `${j.gc}-${j.gf}` : 'a jogar'}</span>
              </button>
            ))}
          </div>
        </section>
      )}

      {emMata && fasesMata}

      <div className="competicao-corpo">
        <div className="competicao-tabelas">
          {d.grupos ? (
            d.grupos.map((g, i) => (
              <section className="painel painel-lista" key={g.nome}>
                <div className="painel-cab" style={{ padding: '12px 16px 4px' }}>
                  <span className="painel-titulo">
                    {d.fase1} · {g.nome}
                  </span>
                  {i === 0 && <span className="tag-fraco" style={{ fontSize: 12 }}>{d.legenda}</span>}
                </div>
                <Grade
                  colunas={COLUNAS}
                  itens={g.linhas}
                  idDe={(l) => l.pos}
                  classeDe={(l) => `${l.zona}${l.eu ? ' eu' : ''}`}
                />
              </section>
            ))
          ) : (
            <section className="painel painel-lista">
              <div className="painel-cab" style={{ padding: '12px 16px 4px' }}>
                <span className="painel-titulo">{d.fase1 ?? 'Classificacao'}</span>
                <span className="tag-fraco" style={{ fontSize: 12 }}>{d.legenda}</span>
              </div>
              <Grade
                colunas={COLUNAS}
                itens={d.linhas}
                idDe={(l) => l.pos}
                classeDe={(l) => `${l.zona}${l.eu ? ' eu' : ''}`}
                vazio={d.vazio ?? undefined}
              />
            </section>
          )}
        </div>

        <section className="painel painel-lista" aria-label="Rodadas">
          <div className="navegador-rodada">
            <button
              type="button"
              className="bt-fantasma bt-mini"
              disabled={rodada <= 0}
              aria-label="Rodada anterior"
              onClick={() => setRodada(rodada - 1)}
            >
              ◀
            </button>
            <span className="painel-titulo" aria-live="polite">
              {d.fase1 && `${d.fase1} · `}Rodada {r?.numero ?? '-'} de {d.rodadas.length}
              {r && !r.jogada && ' · a jogar'}
              {r && r.jogada && !r.registrada && ' · sem registro'}
            </span>
            <button
              type="button"
              className="bt-fantasma bt-mini"
              disabled={rodada >= d.rodadas.length - 1}
              aria-label="Proxima rodada"
              onClick={() => setRodada(rodada + 1)}
            >
              ▶
            </button>
          </div>
          {r?.jogos.map((j, i) => (
            <div className={`jogo-linha${j.meu ? ' meu' : ''}`} key={i}>
              <span className="jl-casa corta">{j.casa}</span>
              <span className={`jl-placar${j.resultado ? ` res-${j.resultado}` : ''}`}>{placar(j.gc, j.gf)}</span>
              <span className="jl-fora corta">{j.fora}</span>
            </div>
          ))}
          {d.aviso && <div className="vazio">{d.aviso}</div>}
        </section>
      </div>

      {!emMata && fasesMata}
    </>
  )
}

// ------------------------------------------------------------------ mata-mata
function LinhaCopa({ j }: { j: JogoCopa }) {
  const jogado = j.ida !== null
  return (
    <div className={`copa-jogo${j.meu ? ' meu' : ''}`}>
      <span className={`cj-time corta${j.vencedor && j.venceu_a ? ' venceu' : ''}`}>{j.a}</span>
      <span className="cj-placar">
        {!jogado ? (
          'x'
        ) : (
          <>
            {j.ida![0]} x {j.ida![1]}
            {j.volta && (
              <span className="tag-fraco">
                {' '}· volta {j.volta[0]} x {j.volta[1]} · agregado {j.agregado![0]} x {j.agregado![1]}
              </span>
            )}
            {j.penaltis && <span className="tag-atencao"> · penaltis: {j.penaltis}</span>}
          </>
        )}
      </span>
      <span className={`cj-time dir corta${j.vencedor && !j.venceu_a ? ' venceu' : ''}`}>{j.b}</span>
    </div>
  )
}

function Fase({ f }: { f: FaseCopa }) {
  // a fase com o meu jogo abre aberta; as outras mostram so o meu confronto
  const [aberta, setAberta] = useState(f.estado === 'sorteada' || f.jogos.length <= 4)
  const meus = f.jogos.filter((j) => j.meu)
  const visiveis = aberta ? f.jogos : meus
  return (
    <section className={`painel copa-fase ${f.estado}`}>
      <div className="painel-cab" style={{ padding: '12px 16px 6px' }}>
        <span className="painel-titulo">
          {f.nome} · semana {f.semana}
          {f.nota
            ? ` · ${f.nota}`
            : (f.estado === 'sorteada' && ' · proxima fase, ja sorteada') || (f.estado === 'futura' && ' · a sortear')}
        </span>
        {f.jogos.length > 4 && (
          <button type="button" className="bt-fantasma bt-mini" aria-expanded={aberta} onClick={() => setAberta(!aberta)}>
            {aberta ? 'So o meu jogo' : `Ver os ${f.jogos.length} confrontos`}
          </button>
        )}
      </div>
      {visiveis.map((j, i) => (
        <LinhaCopa j={j} key={i} />
      ))}
      {f.estado !== 'futura' && !aberta && meus.length === 0 && (
        <div className="vazio">Seu clube nao jogou esta fase.</div>
      )}
    </section>
  )
}

function Situacao({ s, campeao }: { s: NonNullable<DetalheCopa['situacao']>; campeao: string | null }) {
  return (
    <section className={`painel faixa ${s.estado}`}>
      <div className="faixa-icone">{iconeDeEstado(s.estado)}</div>
      <div className="faixa-titulo">{s.texto}</div>
      {campeao && (
        <>
          <div className="espaco" />
          <span className="tag-top" style={{ fontWeight: 700 }}>Campeao: {campeao}</span>
        </>
      )}
    </section>
  )
}

function Copa({ d }: { d: DetalheCopa }) {
  return (
    <>
      {d.situacao && <Situacao s={d.situacao} campeao={d.campeao} />}
      {d.aviso && <div className="vazio">{d.aviso}</div>}
      {/* a fase mais recente primeiro: e ela que interessa agora */}
      {[...d.fases].reverse().map((f) => (
        <Fase f={f} key={`${d.id}-${f.nome}`} />
      ))}
    </>
  )
}

// ======================================================================= tela
export function Competicoes({ tela, ocupado, aoTrocar }: Props) {
  const meus = tela.lista.filter((c) => c.meu)
  const outros = tela.lista.filter((c) => !c.meu)
  const alvoEOutro = outros.some((c) => c.id === tela.alvo)

  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={tela.subtitulo} />

      <div className="abas" role="tablist" aria-label="Seus torneios">
        {meus.map((c) => (
          <button
            key={c.id}
            type="button"
            role="tab"
            aria-selected={c.id === tela.alvo}
            className={`aba aba-comp${c.id === tela.alvo ? ' ativa' : ''}`}
            disabled={ocupado}
            onClick={() => c.id !== tela.alvo && aoTrocar(c.id)}
          >
            <span>{c.nome}</span>
            <span className={`aba-estado${c.vivo ? '' : ' fora'}`}>{c.estado}</span>
          </button>
        ))}
        <label className="campo-rotulo" style={{ marginLeft: 'auto' }}>
          Outros torneios
          <select
            className="seletor"
            value={alvoEOutro ? tela.alvo : ''}
            disabled={ocupado}
            onChange={(e) => e.target.value && aoTrocar(e.target.value)}
          >
            <option value="">escolha…</option>
            {outros.map((c) => (
              <option key={c.id} value={c.id}>
                {c.nome} · {c.estado}
              </option>
            ))}
          </select>
        </label>
      </div>

      {tela.detalhe.tipo === 'pontos' ? <Pontos d={tela.detalhe} /> : <Copa d={tela.detalhe} />}
    </div>
  )
}
