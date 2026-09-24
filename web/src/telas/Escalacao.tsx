// Quem joga e como joga.
//
// O objeto principal e o campo com o XI; a lista ao lado repete os mesmos 11
// (em roxo) e o banco logo abaixo. O resto - formacao, tatica, plano de jogo -
// fica numa barra so, e o que e ajuste fino (mentalidade e os cinco eixos do
// plano) abre sob demanda: antes eram quatro faixas de controles empilhadas
// antes do campo aparecer.
//
// A troca e em dois cliques explicitos e so entao o botao. Titular + reserva:
// um sai, o outro entra. Dois titulares: trocam de lugar. Clicar e ja trocar
// seria mais rapido, mas um clique errado no banco tiraria alguem do time sem
// o usuario ver quem saiu.
//
// O XI vem do mesmo diagnostico do Painel. A tela nao recalcula forca nem
// improviso: cada troca volta do servidor com os numeros refeitos.
//
// Formacao (decidido com o agente de UX): mentalidade nunca remonta o time; no
// Manual a formacao mantem os mesmos 11 e so reorganiza as vagas; no
// Automatico remonta. Toda troca de formacao pode ser desfeita por alguns
// segundos - o botao aparece no recado, la em cima.

import { porque, AGUARDE } from '../motivo'
import { useRef, useState } from 'react'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import { Campo } from '../componentes/Campo'
import { EditorFormacao } from '../componentes/EditorFormacao'
import { Grade, type Coluna } from '../componentes/Grade'
import { iconeDeEstado, IconeSeta } from '../icones'
import type { Contagem, JogadorBanco, JogadorEmCampo, TelaEscalacao } from '../tipos'

export type AcaoEscalacao =
  | { tipo: 'auto'; ligada: boolean }
  | { tipo: 'esquema'; formacao?: string; tatica?: string; contagem?: Contagem }
  | { tipo: 'montar' }
  | { tipo: 'trocar'; titular: number; reserva: number }
  | { tipo: 'inverter'; a: number; b: number }
  | { tipo: 'plano'; eixo: string; valor: string }
  | { tipo: 'plano-padrao' }

interface Props {
  tela: TelaEscalacao
  ocupado: boolean
  /** O Mercado ja migrou? O atalho da faixa depende disso. */
  mercadoPronto: boolean
  aoAbrirFicha: (id: number) => void
  aoAgir: (acao: AcaoEscalacao) => void
  aoIr: (destino: string) => void
}

const MEMORIA_TATICA = 'escalacao:tatica-aberta'

function lerTaticaAberta() {
  try {
    return window.localStorage.getItem(MEMORIA_TATICA) === '1'
  } catch {
    return false
  }
}

function gravarTaticaAberta(aberta: boolean) {
  try {
    window.localStorage.setItem(MEMORIA_TATICA, aberta ? '1' : '0')
  } catch {
    // sem armazenamento: o painel so volta fechado na proxima visita
  }
}

function colunasXi(novaVaga: Set<number>): Coluna<JogadorEmCampo>[] {
  return [
    {
      chave: 'vaga',
      rotulo: 'Vaga',
      largura: '72px',
      classe: 'centro',
      // improvisado mostra de onde veio e para onde foi: VOL > ZAG
      render: (j) => (
        <span className={j.improvisado ? `tag-${j.estado === 'critico' ? 'critico' : 'atencao'}` : undefined}>
          {j.improvisado ? `${j.pos} > ${j.vaga}` : j.vaga}
        </span>
      ),
    },
    {
      chave: 'nome',
      rotulo: 'Jogador',
      largura: 'minmax(110px, 1fr)',
      classe: 'corta',
      render: (j) => (
        <>
          <span className="nome-titular">{j.nome}</span>
          {novaVaga.has(j.id) && <span className="selo-nova-vaga">nova vaga</span>}
        </>
      ),
    },
    { chave: 'ovr', rotulo: 'Ovr', largura: '40px', classe: 'num', render: (j) => <strong>{j.ovr}</strong> },
    {
      chave: 'fis',
      rotulo: 'Fis',
      largura: '40px',
      classe: 'num',
      render: (j) => <span className={j.cond < 45 ? 'linha-critica' : undefined}>{j.cond}</span>,
    },
    {
      chave: 'obs',
      rotulo: 'Situacao',
      largura: '92px',
      classe: 'corta',
      render: (j) => <span className={`tag-${j.estado}`}>{j.obs}</span>,
      ordem: (j) => j.obs || null,
    },
  ]
}

const COLUNAS_BANCO: Coluna<JogadorBanco>[] = [
  { chave: 'pos', rotulo: 'Pos', largura: '72px', classe: 'centro', render: (j) => j.pos },
  { chave: 'nome', rotulo: 'Jogador', largura: 'minmax(110px, 1fr)', classe: 'corta', render: (j) => j.nome },
  { chave: 'ovr', rotulo: 'Ovr', largura: '40px', classe: 'num', render: (j) => j.ovr },
  {
    chave: 'fis',
    rotulo: 'Fis',
    largura: '40px',
    classe: 'num',
    render: (j) => <span className={j.cond < 45 ? 'linha-critica' : undefined}>{j.cond}</span>,
  },
  { chave: 'sit', rotulo: 'Situacao', largura: '92px', classe: 'corta', render: (j) => j.situacao },
]

/** Opcao do select: a contagem entre parenteses e o aviso de sem laterais. */
function rotuloOpcao(rotulo: string, c: Contagem, semLaterais: boolean) {
  const detalhe = `${c.ZAG} ZAG · ${c.LAT} LAT · ${c.VOL} VOL · ${c.MEI} MEI · ${c.ATA} ATA`
  return semLaterais && !rotulo.includes('sem laterais') ? `${rotulo} (sem laterais) — ${detalhe}` : `${rotulo} — ${detalhe}`
}

/** Marca ate dois. Clicar no marcado desmarca; dois reservas nao trocam entre
 *  si, entao o reserva novo toma o lugar do antigo; com dois marcados, o
 *  terceiro clique empurra o mais antigo para fora. */
function marcar(atual: number[], id: number, ehTitular: (id: number) => boolean) {
  if (atual.includes(id)) return atual.filter((x) => x !== id)
  let novo = [...atual, id]
  if (!ehTitular(id)) novo = novo.filter((x) => x === id || ehTitular(x))
  return novo.slice(-2)
}

interface Troca {
  resumo: string
  acao: AcaoEscalacao | null
}

export function Escalacao({ tela, ocupado, mercadoPronto, aoAbrirFicha, aoAgir, aoIr }: Props) {
  const [marcados, setMarcados] = useState<number[]>([])
  const [editando, setEditando] = useState(false)
  const [taticaAberta, setTaticaAberta] = useState(lerTaticaAberta)
  const botaoEditar = useRef<HTMLButtonElement>(null)
  const novaVaga = new Set(tela.nova_vaga)
  const saida = tela.prontidao.estrutural

  const porTitular = new Map(tela.titulares.map((j) => [j.id, j]))
  const porReserva = new Map(tela.banco.map((j) => [j.id, j]))
  const ehTitular = (id: number) => porTitular.has(id)
  // quem saiu do elenco ou do time depois da ultima resposta nao conta mais
  const validos = marcados.filter((id) => porTitular.has(id) || porReserva.has(id))
  const conjunto = new Set(validos)
  const alternar = (id: number) => setMarcados((atual) => marcar(atual, id, ehTitular))

  const sairDoEditor = () => {
    setEditando(false)
    // o foco volta para quem abriu o editor, e nao para o topo da pagina
    window.setTimeout(() => botaoEditar.current?.focus(), 0)
  }

  const abrirTatica = () => {
    setTaticaAberta((antes) => {
      gravarTaticaAberta(!antes)
      return !antes
    })
  }

  const troca = descreverTroca()
  function descreverTroca(): Troca {
    const tits = validos.map((id) => porTitular.get(id)).filter((j): j is JogadorEmCampo => Boolean(j))
    const res = validos.map((id) => porReserva.get(id)).filter((j): j is JogadorBanco => Boolean(j))
    if (tits.length === 2) {
      const [a, b] = tits
      if (a.vaga === b.vaga) {
        return { resumo: `${a.nome} e ${b.nome} trocam de lado (${a.vaga})`, acao: { tipo: 'inverter', a: a.id, b: b.id } }
      }
      if (!tela.troca_entre_vagas) {
        return {
          resumo: `${a.vaga} e ${b.vaga} sao vagas diferentes: o motor ainda escolhe sozinho a vaga de cada titular`,
          acao: null,
        }
      }
      return {
        resumo: `${a.nome} vai para ${b.vaga}, ${b.nome} para ${a.vaga}`,
        acao: { tipo: 'inverter', a: a.id, b: b.id },
      }
    }
    if (tits.length === 1 && res.length === 1) {
      const [t] = tits
      const [r] = res
      if (!r.disponivel) return { resumo: `${r.nome} nao tem condicao de jogar`, acao: null }
      return {
        resumo: `sai ${t.nome} (${t.vaga}), entra ${r.nome} (${r.pos})`,
        acao: { tipo: 'trocar', titular: t.id, reserva: r.id },
      }
    }
    if (tits.length === 1) {
      return { resumo: `${tits[0].nome} (${tits[0].vaga}): agora um reserva para entrar, ou outro titular para trocar de lugar`, acao: null }
    }
    if (res.length === 1) return { resumo: `entra ${res[0].nome} (${res[0].pos}): agora marque quem sai`, acao: null }
    return {
      resumo: tela.auto
        ? 'Automatico: a maquina escala o melhor time toda semana. Trocar alguem passa o time para o Manual.'
        : 'Manual: o time e seu. So repomos quem nao pode jogar, nunca reotimizamos por cima.',
      acao: null,
    }
  }

  const trocar = () => {
    if (!troca.acao) return
    aoAgir(troca.acao)
    setMarcados([])
  }

  return (
    <div className="tela">
      {/* ataque e defesa moram em cima do campo, junto do time que os produz */}
      <CabecalhoTela titulo={tela.titulo} sub={tela.subtitulo} />

      <section
        className={`painel faixa ${tela.prontidao.estado}${saida ? '' : ' compacta'}`}
        aria-live="polite"
      >
        <div className="faixa-icone">{iconeDeEstado(tela.prontidao.estado)}</div>
        <div style={{ minWidth: 0 }}>
          <div className="faixa-titulo">{tela.prontidao.titulo}</div>
          <div className="faixa-detalhe">{tela.prontidao.detalhe}</div>
          {saida && !saida.alternativa && (
            <div className="faixa-detalhe">Nenhuma formacao pronta tira o improviso com este elenco.</div>
          )}
        </div>
        <div className="espaco" />
        {saida?.alternativa && (
          <button
            type="button"
            className="bt-fantasma"
            title={porque([[ocupado, AGUARDE]])}
            disabled={ocupado}
            onClick={() => aoAgir({ tipo: 'esquema', formacao: saida.alternativa!.formacao })}
          >
            Usar {saida.alternativa.formacao}: ataque {saida.alternativa.ataque} / defesa{' '}
            {saida.alternativa.defesa}
          </button>
        )}
        {saida && (
          <button
            type="button"
            className="bt-fantasma"
            disabled={!mercadoPronto || !saida.mercado}
            title={
              !mercadoPronto
                ? 'o Mercado ainda nao migrou'
                : !saida.mercado
                  ? 'janela de transferencias fechada'
                  : undefined
            }
            onClick={() => aoIr('mercado')}
          >
            Ver {saida.plural} no Mercado
          </button>
        )}
      </section>

      {/* ------------------------------------------ comando, esquema e tatica */}
      <section className="painel comando">
        <div className="comando-linha">
          <div className="alavanca" role="group" aria-label="Quem escala o time">
            <button
              type="button"
              className={tela.auto ? 'ativo' : ''}
              aria-pressed={tela.auto}
              title={porque([[ocupado, AGUARDE]], 'A maquina monta o melhor time toda semana')}
              disabled={ocupado}
              onClick={() => aoAgir({ tipo: 'auto', ligada: true })}
            >
              Automatico
            </button>
            <button
              type="button"
              className={!tela.auto ? 'ativo' : ''}
              aria-pressed={!tela.auto}
              title={porque([[ocupado, AGUARDE]], 'O time e seu: so repomos quem nao pode jogar')}
              disabled={ocupado}
              onClick={() => aoAgir({ tipo: 'auto', ligada: false })}
            >
              Manual
            </button>
          </div>

          <span className="comando-divisor" aria-hidden="true" />

          {/* sem rotulo visivel: a opcao ja comeca pelo nome do esquema (4-4-2) */}
          <select
            className="seletor seletor-formacao"
            aria-label="Formacao"
            value={tela.formacao}
            disabled={ocupado || editando}
            onChange={(e) => aoAgir({ tipo: 'esquema', formacao: e.target.value })}
          >
            {tela.personalizada && <option value="Personalizada">{tela.personalizada.rotulo}</option>}
            {tela.formacoes.map((g) => (
              <optgroup key={g.nome} label={g.nome}>
                {g.itens.map((f) => (
                  <option key={f.id} value={f.id}>
                    {rotuloOpcao(f.rotulo, f.contagem, f.sem_laterais)}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
          <button
            type="button"
            ref={botaoEditar}
            className="bt-fantasma"
            aria-pressed={editando}
            title={porque([[ocupado && !editando, AGUARDE]])}
            disabled={ocupado && !editando}
            onClick={() => (editando ? sairDoEditor() : setEditando(true))}
          >
            {editando ? 'Fechar editor' : 'Editar formacao'}
          </button>

          <button
            type="button"
            className={`bt-fantasma bt-abrir${taticaAberta ? ' aberto' : ''}`}
            aria-expanded={taticaAberta}
            aria-controls="escalacao-tatica"
            onClick={abrirTatica}
          >
            <span>
              Tatica: <strong>{tela.tatica}</strong>
              {!tela.plano.padrao && ' · plano ajustado'}
            </span>
            <IconeSeta tamanho={14} />
          </button>

          <span className="espaco" />
          <button
            type="button"
            className="bt-fantasma"
            title={porque([[ocupado, AGUARDE]], 'Monta o melhor XI disponivel para a formacao atual')}
            disabled={ocupado}
            onClick={() => aoAgir({ tipo: 'montar' })}
          >
            Montar melhor time
          </button>
        </div>

        <div id="escalacao-tatica" className="comando-tatica" hidden={!taticaAberta}>
          <div className="tatica-cab">
            <span className="painel-titulo">Plano de jogo</span>
            <div className="plano-efeitos" aria-label="Efeito do plano de jogo">
              {tela.plano.efeitos.map((e) => (
                <span key={e.nome}>
                  {e.nome} <strong>{e.valor}</strong>
                </span>
              ))}
            </div>
            <button
              type="button"
              className="bt-fantasma bt-mini"
              title={porque([[ocupado, AGUARDE], [tela.plano.padrao, 'O plano ja esta neutro']])}
              disabled={ocupado || tela.plano.padrao}
              onClick={() => aoAgir({ tipo: 'plano-padrao' })}
            >
              Voltar ao padrao
            </button>
          </div>
          <div className="plano-grade" role="group" aria-label="Plano de jogo">
            <label className="plano-eixo">
              <span className="plano-nome">Mentalidade</span>
              <select
                className="seletor"
                value={tela.tatica}
                disabled={ocupado}
                onChange={(e) => aoAgir({ tipo: 'esquema', tatica: e.target.value })}
              >
                {tela.taticas.map((t) => (
                  <option key={t}>{t}</option>
                ))}
              </select>
              <span className="plano-desc">pesa no ataque e na defesa; nunca remonta o time</span>
            </label>
            {tela.plano.eixos.map((eixo) => {
              const atual = eixo.opcoes.find((o) => o.id === eixo.valor)
              return (
                <label className="plano-eixo" key={eixo.id}>
                  <span className="plano-nome">{eixo.nome}</span>
                  <select
                    className="seletor"
                    value={eixo.valor}
                    disabled={ocupado}
                    onChange={(e) => aoAgir({ tipo: 'plano', eixo: eixo.id, valor: e.target.value })}
                  >
                    {eixo.opcoes.map((o) => (
                      <option key={o.id} value={o.id}>
                        {o.id}
                      </option>
                    ))}
                  </select>
                  <span className="plano-desc">{atual?.desc}</span>
                </label>
              )
            })}
          </div>
        </div>
      </section>

      {editando && (
        <section className="painel" style={{ padding: 14 }} aria-label="Editar formacao">
          <EditorFormacao
            inicial={tela.contagem}
            limites={tela.limites}
            ocupado={ocupado}
            aoSair={sairDoEditor}
            aoAplicar={(contagem) => {
              aoAgir({ tipo: 'esquema', contagem })
              sairDoEditor()
            }}
          />
        </section>
      )}

      {/* ------------------------------------------------------- quem joga */}
      <div className="escalacao-corpo" hidden={editando}>
        <section className="painel escalacao-campo" aria-label="Campo">
          <div className="campo-cab">
            <h3 className="painel-titulo">Em campo</h3>
            <span className="espaco" />
            {tela.metricas.map((m) => (
              <span className="campo-forca" key={m.nome}>
                {m.nome} <strong className={m.estado ?? undefined}>{m.valor}</strong>
              </span>
            ))}
          </div>
          <Campo
            jogadores={tela.titulares}
            vagasAbertas={tela.vagas_abertas}
            marcados={conjunto}
            novaVaga={novaVaga}
            aoClicar={(j) => alternar(j.id)}
          />
          <div className="legenda-campo">
            <span>
              <i className="disco-mini">77</i> overall
            </span>
            <span style={{ color: 'var(--atencao)' }}>
              <i className="ponto" /> custa rendimento
            </span>
            <span style={{ color: 'var(--critico)' }}>
              <i className="ponto" /> cobra caro
            </span>
            <span style={{ color: 'var(--acento)' }}>
              <i className="ponto cheio" /> marcado
            </span>
          </div>
        </section>

        <section className="painel escalacao-listas">
          <h3 className="lista-cab">
            <span className="painel-titulo titular">Titulares</span>
            <span className="lista-conta">{tela.titulares.length}</span>
          </h3>
          <Grade
            colunas={colunasXi(novaVaga)}
            itens={tela.titulares}
            idDe={(j) => j.id}
            nomeDe={(j) => `${j.nome}, titular`}
            classeDe={() => 'titular'}
            marcados={conjunto}
            aoMarcar={alternar}
            marcarAoClicar
            aoAbrir={(j) => aoAbrirFicha(j.id)}
            vazio="Ninguem escalado. Use Montar melhor time."
          />

          <h3 className="lista-cab">
            <span className="painel-titulo">Reservas</span>
            <span className="lista-conta">{tela.banco.length}</span>
          </h3>
          <Grade
            colunas={COLUNAS_BANCO}
            itens={tela.banco}
            idDe={(j) => j.id}
            nomeDe={(j) => `${j.nome}, reserva`}
            classeDe={(j) => (j.disponivel ? '' : 'linha-critica')}
            marcados={conjunto}
            aoMarcar={alternar}
            marcarAoClicar
            aoAbrir={(j) => aoAbrirFicha(j.id)}
            vazio="Sem reservas no elenco."
          />
        </section>
      </div>

      {/* a barra da troca fica presa embaixo: a lista do banco e longa e o
          botao nao pode sumir da vista depois de marcar alguem la no fim */}
      <div className="painel barra-acoes barra-fixa" hidden={editando}>
        <span className="resumo" aria-live="polite">
          {troca.resumo}
        </span>
        <button
          type="button"
          className="bt-fantasma"
          title={porque([[validos.length === 0, 'Nada marcado para limpar']])}
          disabled={validos.length === 0}
          onClick={() => setMarcados([])}
        >
          Limpar
        </button>
        <button type="button" className="bt-acao bt-media" title={porque([[!troca.acao, 'Marque dois jogadores para trocar'], [ocupado, AGUARDE]])}
        disabled={!troca.acao || ocupado} onClick={trocar}>
          Trocar
        </button>
      </div>
    </div>
  )
}
