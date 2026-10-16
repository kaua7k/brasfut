// O elenco profissional, com as acoes em lote.
//
// A tela guarda so o que esta marcado; quem busca e quem manda agir e o App.
// Por a venda, ceder e renovar abrem os dialogos do Mercado (vitrine em lote,
// cessao e a mesa de renovacao); o resto e acao direta com confirmacao.

import { porque, AGUARDE, MARQUE } from '../motivo'
import { useEffect, useMemo, useState } from 'react'
import { barraFisico, seloCapitao, seloOvr, seloPos } from '../componentes/Celulas'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import { alternarMarca, Grade, type Coluna } from '../componentes/Grade'
import { dinheiro, plural } from '../formato'
import { LegendaCores } from '../componentes/LegendaCores'
import type { Cedido, JogadorElenco, TelaElenco } from '../tipos'

export type AcaoElenco = 'tirar' | 'rescindir' | 'opcao' | 'chamar' | 'vender' | 'ceder' | 'renovar'

interface Props {
  tela: TelaElenco
  ocupado: boolean
  aoAbrirFicha: (id: number) => void
  aoAgir: (acao: AcaoElenco, ids: number[]) => void
}

const COLUNAS: Coluna<JogadorElenco>[] = [
  { chave: 'pos', rotulo: 'Pos', largura: '46px', classe: 'centro', render: (j) => seloPos(j.pos) },
  {
    chave: 'nome',
    rotulo: 'Jogador',
    largura: 'minmax(140px, 1.6fr)',
    classe: 'corta',
    render: (j) => (
      <>
        <span className={`tag-${j.tag}`}>{j.nome}</span>
        {j.capitao && seloCapitao()}
      </>
    ),
  },
  { chave: 'idade', secundaria: true, rotulo: 'Idade', largura: '52px', classe: 'num', render: (j) => j.idade },
  { chave: 'ovr', rotulo: 'Ovr', largura: '44px', classe: 'num', render: (j) => seloOvr(j.ovr) },
  {
    chave: 'fis',
    rotulo: 'Fisico',
    largura: '72px',
    classe: 'num',
    render: (j) => barraFisico(j.cond),
  },
  { chave: 'sal', secundaria: true, rotulo: 'Salario', largura: '92px', classe: 'num', render: (j) => j.salario, ordem: (j) => j.salario_num },
  { chave: 'val', secundaria: true, rotulo: 'Valor', largura: '92px', classe: 'num', render: (j) => j.valor, ordem: (j) => j.valor_num },
  {
    chave: 'ct',
    secundaria: true,
    rotulo: 'Contrato',
    largura: '84px',
    classe: 'centro',
    // o ! avisa o ultimo ano: sem renovar ele sai de graca
    render: (j) => (
      <span className={j.ultimo_ano ? 'chip-ultimo-ano' : undefined}>
        {plural(j.contrato, 'ano')}{j.ultimo_ano ? ' !' : ''}
      </span>
    ),
  },
  {
    chave: 'jogo',
    secundaria: true,
    rotulo: 'Jogo',
    largura: 'minmax(110px, 1fr)',
    classe: 'corta',
    render: (j) => <span className={j.jogo.startsWith('pendurado') ? 'tag-atencao' : 'tag-critico'}>{j.jogo}</span>,
  },
  {
    chave: 'mercado',
    secundaria: true,
    rotulo: 'Mercado',
    largura: 'minmax(110px, 1fr)',
    classe: 'corta',
    render: (j) => j.mercado,
  },
]

const COLUNAS_CEDIDOS: Coluna<Cedido>[] = [
  {
    chave: 'nome',
    rotulo: 'Jogador',
    largura: 'minmax(130px, 1.4fr)',
    classe: 'corta',
    render: (j) => <span className={`tag-${j.tag}`}>{j.nome}</span>,
  },
  { chave: 'pos', rotulo: 'Pos', largura: '46px', classe: 'centro', render: (j) => seloPos(j.pos) },
  { chave: 'ovr', rotulo: 'Ovr', largura: '44px', classe: 'num', render: (j) => seloOvr(j.ovr) },
  { chave: 'clube', rotulo: 'Esta no', largura: 'minmax(110px, 1.2fr)', classe: 'corta', render: (j) => j.clube },
  { chave: 'pct', rotulo: 'Eles pagam', largura: '86px', classe: 'centro', render: (j) => `${j.emp_pct}%` },
  { chave: 'custo', rotulo: 'Custa a voce', largura: '96px', classe: 'num', render: (j) => j.custo },
  { chave: 'op', rotulo: 'Opcao', largura: '92px', classe: 'num', render: (j) => j.opcao ?? '-' },
]

export function Elenco({ tela, ocupado, aoAbrirFicha, aoAgir }: Props) {
  const [marcados, setMarcados] = useState<Set<number>>(new Set())
  const [marcadosCedidos, setMarcadosCedidos] = useState<Set<number>>(new Set())

  // a tela voltou do servidor (vendeu, rescindiu, cedeu): marcacao antiga
  // apontaria para quem ja saiu do elenco
  useEffect(() => {
    setMarcados(new Set())
    setMarcadosCedidos(new Set())
  }, [tela])

  // contar o que esta marcado: acao em lote sem isso e um tiro no escuro
  const resumo = useMemo(() => {
    const js = tela.jogadores.filter((j) => marcados.has(j.id))
    if (js.length === 0) return 'nenhum jogador marcado'
    const folha = js.reduce((s, j) => s + j.salario_num, 0)
    const valor = js.reduce((s, j) => s + j.valor_num, 0)
    return `${plural(js.length, 'marcado')} · folha ${dinheiro(folha)} por mes · valor somado ${dinheiro(valor)}`
  }, [tela.jogadores, marcados])

  const ids = [...marcados]
  const nenhum = ids.length === 0
  // emprestado aqui nao conta: o contrato dele e com o dono
  const acabando = tela.jogadores.filter((j) => j.contrato <= 1 && !j.emprestado_aqui).map((j) => j.id)

  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={tela.subtitulo} metricas={tela.metricas} />

      <section className="painel painel-lista">
        <Grade
          colunas={COLUNAS}
          itens={tela.jogadores}
          idDe={(j) => j.id}
          classeDe={(j) => (j.estado === 'critico' ? 'linha-critica' : '')}
          marcados={marcados}
          aoMarcar={(id) => setMarcados((s) => alternarMarca(s, id))}
          aoMarcarTodos={(ids) => setMarcados(new Set(ids))}
          aoAbrir={(j) => aoAbrirFicha(j.id)}
          nomeDe={(j) => j.nome}
          memoria="elenco"
          vazio="Elenco vazio. Contrate no Mercado."
        />
        <LegendaCores critico="machucado ou suspenso" />

        <div className="barra-acoes barra-presa">
          <span className="resumo">{resumo}</span>

          <button
            type="button"
            className="bt-fantasma"
            title={porque([[acabando.length === 0, 'Ninguem no ultimo ano de contrato']], 'Marca quem esta no ultimo ano de contrato (ou ja venceu) e nao e emprestado')}
            disabled={acabando.length === 0}
            onClick={() => setMarcados(new Set(acabando))}
          >
            Contrato acabando ({acabando.length})
          </button>

          <button
            type="button"
            className="bt-fantasma"
            title={porque([[nenhum, MARQUE]])}
            disabled={nenhum}
            onClick={() => aoAbrirFicha(ids[0])}
          >
            Ver ficha
          </button>
          <button
            type="button"
            className="bt-fantasma"
            title={porque([[nenhum, MARQUE], [ocupado, AGUARDE]])}
            disabled={nenhum || ocupado}
            onClick={() => aoAgir('vender', ids)}
          >
            Por a venda
          </button>
          <button
            type="button"
            className="bt-fantasma"
            title={porque([[nenhum, MARQUE], [ocupado, AGUARDE]])}
            disabled={nenhum || ocupado}
            onClick={() => aoAgir('tirar', ids)}
          >
            Tirar da vitrine
          </button>
          <button
            type="button"
            className="bt-fantasma"
            title={porque([[nenhum, MARQUE], [ocupado, AGUARDE]])}
            disabled={nenhum || ocupado}
            onClick={() => aoAgir('ceder', ids)}
          >
            Ceder emprestimo
          </button>
          <button
            type="button"
            className="bt-fantasma"
            title={porque([[nenhum, MARQUE], [ocupado, AGUARDE]], 'Um marcado abre a mesa para negociar; varios renovam em lote, com um prazo para todos')}
            disabled={nenhum || ocupado}
            onClick={() => aoAgir('renovar', ids)}
          >
            Renovar
          </button>
          <button
            type="button"
            className="bt-fantasma"
            title={porque([[nenhum, MARQUE], [ocupado, AGUARDE]])}
            disabled={nenhum || ocupado}
            onClick={() => aoAgir('opcao', ids)}
          >
            Comprar em definitivo
          </button>
          <button
            type="button"
            className="bt-fantasma bt-perigo"
            title={porque([[nenhum, MARQUE], [ocupado, AGUARDE]])}
            disabled={nenhum || ocupado}
            onClick={() => aoAgir('rescindir', ids)}
          >
            Rescindir
          </button>
        </div>

        {!tela.mercado_aberto && (
          <div className="barra-acoes colada">
            <span className="aviso">
              Janela fechada: da para renovar e rescindir, nao para vender ou emprestar.
            </span>
          </div>
        )}
      </section>

      {/* quem eu cedi sai do elenco e sem esta tabela simplesmente sumiria */}
      {tela.cedidos.length > 0 && (
        <>
          <div className="painel-titulo">Cedidos por emprestimo</div>
          <section className="painel painel-lista">
            <Grade
              colunas={COLUNAS_CEDIDOS}
              itens={tela.cedidos}
              idDe={(j) => j.id}
              marcados={marcadosCedidos}
              aoMarcar={(id) => setMarcadosCedidos((s) => alternarMarca(s, id))}
              aoMarcarTodos={(ids) => setMarcadosCedidos(new Set(ids))}
              memoria="cedidos"
              aoAbrir={(j) => aoAbrirFicha(j.id)}
              nomeDe={(j) => j.nome}
            />
            <div className="barra-acoes barra-presa">
              <span className="resumo">
                {tela.mercado_aberto
                  ? 'ele volta ao seu elenco e a folha inteira volta pra voce'
                  : 'emprestimo so se interrompe com a janela aberta'}
              </span>
              <button
                type="button"
                className="bt-fantasma"
                title={porque([[marcadosCedidos.size === 0, 'Marque quem voce quer de volta'], [ocupado, AGUARDE], [!tela.mercado_aberto, 'So com a janela aberta']])}
                disabled={marcadosCedidos.size === 0 || ocupado || !tela.mercado_aberto}
                onClick={() => aoAgir('chamar', [...marcadosCedidos])}
              >
                Chamar de volta
              </button>
            </div>
          </section>
        </>
      )}
    </div>
  )
}
