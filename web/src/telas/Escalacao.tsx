// Quem joga e como joga.
//
// A troca e em dois cliques explicitos - um titular, um reserva - e so entao o
// botao. Clicar no reserva e ele ja entrar seria mais rapido, mas um clique
// errado no banco tiraria alguem do time sem o usuario ver quem saiu.
//
// O XI vem do mesmo diagnostico do Painel. A tela nao recalcula forca nem
// improviso: cada troca volta do servidor com os numeros refeitos.
//
// Formacao (decidido com o agente de UX): mentalidade nunca remonta o time; no
// Manual a formacao mantem os mesmos 11 e so reorganiza as vagas; no
// Automatico remonta. Toda troca de formacao pode ser desfeita por alguns
// segundos - o botao aparece no recado, la em cima.

import { useRef, useState } from 'react'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import { Campo } from '../componentes/Campo'
import { EditorFormacao } from '../componentes/EditorFormacao'
import { Grade, type Coluna } from '../componentes/Grade'
import { iconeDeEstado } from '../icones'
import type { Contagem, JogadorBanco, JogadorEmCampo, TelaEscalacao } from '../tipos'

export type AcaoEscalacao =
  | { tipo: 'auto'; ligada: boolean }
  | { tipo: 'esquema'; formacao?: string; tatica?: string; contagem?: Contagem }
  | { tipo: 'montar' }
  | { tipo: 'trocar'; titular: number; reserva: number }
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

function colunasXi(novaVaga: Set<number>): Coluna<JogadorEmCampo>[] {
  return [
    ...COLUNAS_XI.slice(0, 2),
    {
      chave: 'nome',
      rotulo: 'Jogador',
      largura: 'minmax(110px, 1fr)',
      classe: 'corta',
      render: (j) => (
        <>
          {j.nome}
          {novaVaga.has(j.id) && <span className="selo-nova-vaga">nova vaga</span>}
        </>
      ),
    },
    ...COLUNAS_XI.slice(3),
  ]
}

const COLUNAS_XI: Coluna<JogadorEmCampo>[] = [
  { chave: 'n', rotulo: '#', largura: '26px', classe: 'num', render: (j) => j.numero },
  {
    chave: 'vaga',
    rotulo: 'Vaga',
    largura: '78px',
    classe: 'centro',
    // improvisado mostra de onde veio e para onde foi: VOL > ZAG
    render: (j) => (
      <span className={j.improvisado ? `tag-${j.estado === 'critico' ? 'critico' : 'atencao'}` : undefined}>
        {j.improvisado ? `${j.pos} > ${j.vaga}` : j.vaga}
      </span>
    ),
  },
  { chave: 'nome', rotulo: 'Jogador', largura: 'minmax(110px, 1fr)', classe: 'corta', render: (j) => j.nome },
  { chave: 'ovr', rotulo: 'Ovr', largura: '40px', classe: 'num', render: (j) => j.ovr },
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
    largura: '96px',
    classe: 'corta',
    render: (j) => <span className={`tag-${j.estado}`}>{j.obs}</span>,
  },
]

const COLUNAS_BANCO: Coluna<JogadorBanco>[] = [
  { chave: 'pos', rotulo: 'Pos', largura: '46px', classe: 'centro', render: (j) => j.pos },
  {
    chave: 'nome',
    rotulo: 'Jogador',
    largura: 'minmax(110px, 1fr)',
    classe: 'corta',
    render: (j) => <span className={j.disponivel ? `tag-${j.tag}` : undefined}>{j.nome}</span>,
  },
  { chave: 'ovr', rotulo: 'Ovr', largura: '40px', classe: 'num', render: (j) => j.ovr },
  {
    chave: 'fis',
    rotulo: 'Fis',
    largura: '40px',
    classe: 'num',
    render: (j) => <span className={j.cond < 45 ? 'linha-critica' : undefined}>{j.cond}</span>,
  },
  { chave: 'sit', rotulo: 'Situacao', largura: 'minmax(90px, 0.8fr)', classe: 'corta', render: (j) => j.situacao },
]

/** Marca um so: clicar de novo no marcado desmarca. */
function unico(atual: number | null, id: number) {
  return atual === id ? null : id
}

/** Opcao do select: a contagem entre parenteses e o aviso de sem laterais. */
function rotuloOpcao(rotulo: string, c: Contagem, semLaterais: boolean) {
  const detalhe = `${c.ZAG} ZAG · ${c.LAT} LAT · ${c.VOL} VOL · ${c.MEI} MEI · ${c.ATA} ATA`
  return semLaterais && !rotulo.includes('sem laterais') ? `${rotulo} (sem laterais) — ${detalhe}` : `${rotulo} — ${detalhe}`
}

export function Escalacao({ tela, ocupado, mercadoPronto, aoAbrirFicha, aoAgir, aoIr }: Props) {
  const [sai, setSai] = useState<number | null>(null)
  const [entra, setEntra] = useState<number | null>(null)
  const [editando, setEditando] = useState(false)
  const botaoEditar = useRef<HTMLButtonElement>(null)
  const novaVaga = new Set(tela.nova_vaga)
  const saida = tela.prontidao.estrutural

  const sairDoEditor = () => {
    setEditando(false)
    // o foco volta para quem abriu o editor, e nao para o topo da pagina
    window.setTimeout(() => botaoEditar.current?.focus(), 0)
  }

  const titular = tela.titulares.find((j) => j.id === sai) ?? null
  const reserva = tela.banco.find((j) => j.id === entra) ?? null
  const podeTrocar = Boolean(titular && reserva?.disponivel) && !ocupado

  let resumo = 'marque um titular e um reserva'
  if (titular && !reserva) resumo = `sai ${titular.nome} (${titular.vaga}) — agora marque quem entra`
  if (!titular && reserva) resumo = `entra ${reserva.nome} (${reserva.pos}) — agora marque quem sai`
  if (titular && reserva) {
    resumo = reserva.disponivel
      ? `sai ${titular.nome} (${titular.vaga}), entra ${reserva.nome} (${reserva.pos})`
      : `${reserva.nome} nao tem condicao de jogar`
  }

  const trocar = () => {
    if (!titular || !reserva) return
    aoAgir({ tipo: 'trocar', titular: titular.id, reserva: reserva.id })
    setSai(null)
    setEntra(null)
  }

  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={tela.subtitulo} metricas={tela.metricas} />

      <section className={`painel faixa ${tela.prontidao.estado}`}>
        <div className="faixa-icone">{iconeDeEstado(tela.prontidao.estado)}</div>
        <div style={{ minWidth: 0 }}>
          <div className="faixa-titulo">{tela.prontidao.titulo}</div>
          <div className="faixa-detalhe">{tela.prontidao.detalhe}</div>
          {saida && !saida.alternativa && (
            <div className="faixa-detalhe">
              Nenhuma formacao pronta tira o improviso com este elenco.
            </div>
          )}
        </div>
        <div className="espaco" />
        {saida?.alternativa && (
          <button
            type="button"
            className="bt-fantasma"
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

      {/* -------------------------------------------------- comando e esquema */}
      <section className="painel barra-acoes esquema">
        <div className="alavanca" role="group" aria-label="Quem escala o time">
          <button
            type="button"
            className={tela.auto ? 'ativo' : ''}
            aria-pressed={tela.auto}
            disabled={ocupado}
            onClick={() => aoAgir({ tipo: 'auto', ligada: true })}
          >
            Automatico
          </button>
          <button
            type="button"
            className={!tela.auto ? 'ativo' : ''}
            aria-pressed={!tela.auto}
            disabled={ocupado}
            onClick={() => aoAgir({ tipo: 'auto', ligada: false })}
          >
            Manual
          </button>
        </div>
        <span className="resumo">
          {tela.auto
            ? 'a maquina monta o melhor time toda semana. Trocar alguem aqui desliga a alavanca.'
            : 'o time e seu. So repomos quem nao pode jogar, nunca reotimizamos por cima.'}
        </span>

        <label className="campo-rotulo">
          Formacao
          <select
            className="seletor seletor-formacao"
            value={tela.formacao}
            disabled={ocupado || editando}
            onChange={(e) => aoAgir({ tipo: 'esquema', formacao: e.target.value })}
          >
            {tela.personalizada && (
              <option value="Personalizada">{tela.personalizada.rotulo}</option>
            )}
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
        </label>
        <button
          type="button"
          ref={botaoEditar}
          className="bt-fantasma"
          aria-pressed={editando}
          disabled={ocupado && !editando}
          onClick={() => (editando ? sairDoEditor() : setEditando(true))}
        >
          {editando ? 'Fechar editor' : 'Editar formacao'}
        </button>
        <label className="campo-rotulo">
          Mentalidade
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
        </label>
        <button
          type="button"
          className="bt-fantasma"
          disabled={ocupado}
          title="Trocar formacao ou mentalidade tambem remonta o time"
          onClick={() => aoAgir({ tipo: 'montar' })}
        >
          Montar melhor time agora
        </button>
      </section>

      {/* ------------------------------------------------------ plano de jogo */}
      <section className="painel" style={{ padding: '14px 18px' }}>
        <div className="painel-cab" style={{ marginBottom: 10 }}>
          <span className="painel-titulo">Plano de jogo</span>
          <span className="plano-efeitos">
            {tela.plano.efeitos.map((e) => (
              <span key={e.nome}>
                {e.nome} <strong>{e.valor}</strong>
              </span>
            ))}
          </span>
          <button
            type="button"
            className="bt-fantasma bt-mini"
            disabled={ocupado || tela.plano.padrao}
            onClick={() => aoAgir({ tipo: 'plano-padrao' })}
          >
            Voltar ao padrao
          </button>
        </div>
        <div className="plano-grade">
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
        <section className="painel escalacao-campo">
          <Campo
            jogadores={tela.titulares}
            vagasAbertas={tela.vagas_abertas}
            selecionado={sai}
            novaVaga={novaVaga}
            aoClicar={(j) => setSai(unico(sai, j.id))}
          />
          <div className="legenda-campo">
            <span><i className="ponto" style={{ color: 'var(--txt)' }} /> em ordem</span>
            <span style={{ color: 'var(--atencao)' }}><i className="ponto" /> custa rendimento</span>
            <span style={{ color: 'var(--critico)' }}><i className="ponto" /> cobra caro</span>
            <span style={{ color: 'var(--acento)' }}><i className="ponto" /> marcado para sair</span>
          </div>
        </section>

        <div className="escalacao-listas">
          <div className="painel-titulo">Titulares</div>
          <section className="painel" style={{ overflow: 'hidden' }}>
            <Grade
              colunas={colunasXi(novaVaga)}
              itens={tela.titulares}
              idDe={(j) => j.id}
              nomeDe={(j) => j.nome}
              marcados={new Set(sai === null ? [] : [sai])}
              aoMarcar={(id) => setSai(unico(sai, id))}
              aoAbrir={(j) => aoAbrirFicha(j.id)}
              vazio="Ninguem escalado. Use Montar melhor time agora."
            />
          </section>

          <div className="painel-titulo">Banco e reservas</div>
          <section className="painel" style={{ overflow: 'hidden' }}>
            <Grade
              colunas={COLUNAS_BANCO}
              itens={tela.banco}
              idDe={(j) => j.id}
              nomeDe={(j) => j.nome}
              classeDe={(j) => (j.disponivel ? '' : 'linha-critica')}
              marcados={new Set(entra === null ? [] : [entra])}
              aoMarcar={(id) => setEntra(unico(entra, id))}
              aoAbrir={(j) => aoAbrirFicha(j.id)}
              vazio="Sem reservas no elenco."
            />
          </section>
        </div>
      </div>

      {/* a barra da troca fica presa embaixo: a lista do banco e longa e o
          botao nao pode sumir da vista depois de marcar alguem la no fim */}
      <div className="painel barra-acoes barra-fixa" hidden={editando}>
        <span className="resumo">{resumo}</span>
        <button
          type="button"
          className="bt-fantasma"
          disabled={sai === null && entra === null}
          onClick={() => {
            setSai(null)
            setEntra(null)
          }}
        >
          Limpar
        </button>
        <button
          type="button"
          className="bt-acao bt-media"
          disabled={!podeTrocar}
          onClick={trocar}
        >
          Trocar
        </button>
      </div>
    </div>
  )
}
