// A tabela do jogo, desenhada uma vez so.
//
// Elenco, Base e Classificacao usam esta mesma grade. No tkinter cada tela
// escolhia a propria largura de coluna e nada se alinhava com nada.
//
// A linha e uma div, e nao um <button>: o Chrome embrulha o conteudo de um
// botao numa caixa anonima, e com isso o display:grid da linha nao chega nas
// celulas - as colunas saem fora de lugar e a linha estica. Quem e botao de
// verdade aqui e so a caixa de marcar.
//
// A selecao e por caixa, e nao por ctrl+clique como na janela: no navegador
// ninguem descobre ctrl+clique sozinho, e a caixa ainda e alcancavel pelo Tab.
//
// Ordenar: clicar no cabecalho de uma coluna ordena a lista por ela - numero
// do maior para o menor, texto de A a Z; o segundo clique inverte e o terceiro
// volta a ordem que veio do servidor. A chave de ordem sai do que a celula
// mostra ("R$ 1.20 mi", "450 mil", "65%", "3 ano(s)"), entao toda coluna ja
// nasce ordenavel; `ordem` na coluna so e preciso quando o texto engana.

import { Children, isValidElement, useMemo, useState, type ReactNode } from 'react'
import { IconeCerto } from '../icones'

/** Marca ou desmarca um id. Use com o setter funcional -
 *  setMarcados((s) => alternarMarca(s, id)) - para dois cliques seguidos nao
 *  partirem do mesmo conjunto e um apagar o outro. */
export function alternarMarca(atual: Set<number>, id: number) {
  const novo = new Set(atual)
  if (novo.has(id)) novo.delete(id)
  else novo.add(id)
  return novo
}

export interface Coluna<T> {
  chave: string
  rotulo: string
  largura: string
  classe?: 'num' | 'centro' | 'corta'
  render: (item: T) => ReactNode
  /** Chave de ordem explicita. Sem ela, a grade le o que a celula mostra.
   *  null desliga a ordenacao desta coluna. */
  ordem?: ((item: T) => number | string | null) | null
  /** Primeiro clique: 'desc' (maior primeiro) ou 'asc'. Padrao: numero desc, texto asc. */
  primeiro?: 'asc' | 'desc'
}

interface Props<T> {
  colunas: Coluna<T>[]
  itens: T[]
  idDe: (item: T) => number
  /** Classe extra por linha: destaque do meu clube, linha em vermelho, etc. */
  classeDe?: (item: T) => string
  /** Como chamar o item na etiqueta da caixa de marcar. */
  nomeDe?: (item: T) => string
  marcados?: Set<number>
  aoMarcar?: (id: number) => void
  /** Com isto, o cabecalho ganha a caixa de marcar/desmarcar todos. Recebe o
   *  conjunto inteiro que deve ficar marcado (vazio = desmarcar). */
  aoMarcarTodos?: (ids: number[]) => void
  aoAbrir?: (item: T) => void
  /** Clicar em qualquer ponto da linha marca (a Escalacao usa: o nome e o
   *  alvo natural). A caixa continua sendo o caminho do teclado. */
  marcarAoClicar?: boolean
  vazio?: string
  /** Guarda a ordem escolhida entre visitas (por navegador). */
  memoria?: string
  /** false desliga a ordenacao na grade inteira (tabela de campeonato, etc.) */
  ordenavel?: boolean
}

type Direcao = 'asc' | 'desc'
interface Ordem {
  chave: string
  dir: Direcao
  /** a direcao do primeiro clique: o terceiro clique a reconhece e desliga */
  inicio: Direcao
}

// ------------------------------------------------------------ chave de ordem
// a mesma ordem de POS em brasfut.py
const ORDEM_POS = ['GOL', 'ZAG', 'LAT', 'VOL', 'MEI', 'ATA']

function textoDe(no: ReactNode): string {
  if (no === null || no === undefined || typeof no === 'boolean') return ''
  if (typeof no === 'string' || typeof no === 'number') return String(no)
  if (Array.isArray(no)) return no.map(textoDe).join('')
  if (isValidElement(no)) {
    const props = no.props as { children?: ReactNode }
    return Children.toArray(props.children).map(textoDe).join('')
  }
  return ''
}

/** "R$ 1.20 mi" -> 1200000; "450 mil" -> 450000; "-R$ 3 mi" -> -3000000;
 *  "65%" -> 65; "3 ano(s) !" -> 3; "Meia" -> "meia"; "-" ou vazio -> null. */
export function chaveDeOrdem(no: ReactNode): number | string | null {
  if (typeof no === 'number') return no
  const txt = textoDe(no).trim()
  if (!txt || txt === '-' || txt === 'x') return null
  // posicao vai na ordem do campo (GOL, ZAG... ATA), nao na do alfabeto
  const pos = ORDEM_POS.indexOf(txt.toUpperCase())
  if (pos >= 0) return `${pos} ${txt}`
  const dinheiro = /(-?)\s*R\$\s*(-?)([\d.,]+)\s*(mil|mi|bi)?/i.exec(txt)
  if (dinheiro) {
    const sinal = dinheiro[1] || dinheiro[2] ? -1 : 1
    const n = Number.parseFloat(dinheiro[3].replace(/\.(?=\d{3}(\D|$))/g, '').replace(',', '.'))
    const mult = { mi: 1e6, mil: 1e3, bi: 1e9 }[(dinheiro[4] ?? '').toLowerCase()] ?? 1
    if (!Number.isNaN(n)) return sinal * n * mult
  }
  // numero no comeco da celula ("65%", "3 ano(s)", "+4", "70-80"): vale ele
  const numero = /^([+-]?\d+(?:[.,]\d+)?)\s*(mil|mi)?\b/i.exec(txt)
  if (numero) {
    const n = Number.parseFloat(numero[1].replace(',', '.'))
    const mult = { mi: 1e6, mil: 1e3 }[(numero[2] ?? '').toLowerCase()] ?? 1
    return n * mult
  }
  return txt.toLocaleLowerCase('pt-BR')
}

function comparar(a: number | string | null, b: number | string | null, dir: Direcao) {
  // vazio vai sempre para o fim, qualquer que seja a direcao
  if (a === null && b === null) return 0
  if (a === null) return 1
  if (b === null) return -1
  // numero antes de texto nos dois sentidos ("+3" antes de "no teto")
  if (typeof a === 'number' && typeof b !== 'number') return -1
  if (typeof a !== 'number' && typeof b === 'number') return 1
  const r = typeof a === 'number' ? a - (b as number) : a.localeCompare(b as string, 'pt-BR')
  return dir === 'asc' ? r : -r
}

function lerMemoria(chave?: string): Ordem | null {
  if (!chave) return null
  try {
    const bruto = window.localStorage.getItem(`grade-ordem:${chave}`)
    return bruto ? (JSON.parse(bruto) as Ordem) : null
  } catch {
    return null
  }
}

function gravarMemoria(chave: string | undefined, ordem: Ordem | null) {
  if (!chave) return
  try {
    if (ordem) window.localStorage.setItem(`grade-ordem:${chave}`, JSON.stringify(ordem))
    else window.localStorage.removeItem(`grade-ordem:${chave}`)
  } catch {
    // navegador sem armazenamento: a ordem so nao sobrevive a visita
  }
}

export function Grade<T>({
  colunas,
  itens,
  idDe,
  classeDe,
  nomeDe,
  marcados,
  aoMarcar,
  aoMarcarTodos,
  aoAbrir,
  marcarAoClicar = false,
  vazio,
  memoria,
  ordenavel = true,
}: Props<T>) {
  const [ordem, setOrdem] = useState<Ordem | null>(() => lerMemoria(memoria))
  const selecionavel = Boolean(marcados && aoMarcar)
  const grid = (selecionavel ? '30px ' : '') + colunas.map((c) => c.largura).join(' ')

  const chaveDe = (c: Coluna<T>) => (c.ordem === undefined ? (i: T) => chaveDeOrdem(c.render(i)) : c.ordem)
  const colunaOrdem = ordem ? colunas.find((c) => c.chave === ordem.chave && c.ordem !== null) : undefined

  const lista = useMemo(() => {
    if (!ordenavel || !ordem || !colunaOrdem) return itens
    const chave = chaveDe(colunaOrdem)
    if (!chave) return itens
    // ordenacao estavel: empate mantem a ordem do servidor
    return itens
      .map((item, i) => ({ item, i, k: chave(item) }))
      .sort((a, b) => comparar(a.k, b.k, ordem.dir) || a.i - b.i)
      .map((x) => x.item)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [itens, ordem, colunaOrdem, ordenavel])

  const clicarCabecalho = (c: Coluna<T>) => {
    const chave = chaveDe(c)
    if (!chave) return
    let novo: Ordem | null
    if (!ordem || ordem.chave !== c.chave) {
      // o primeiro clique olha o tipo da coluna: numero comeca do maior
      const amostra = itens.map(chave).find((k) => k !== null)
      const inicio: Direcao = c.primeiro ?? (typeof amostra === 'number' ? 'desc' : 'asc')
      novo = { chave: c.chave, dir: inicio, inicio }
    } else if (ordem.dir === ordem.inicio) {
      // segundo clique inverte
      novo = { ...ordem, dir: ordem.dir === 'desc' ? 'asc' : 'desc' }
    } else {
      // terceiro volta a ordem que veio do servidor
      novo = null
    }
    setOrdem(novo)
    gravarMemoria(memoria, novo)
  }

  if (itens.length === 0) {
    return <div className="vazio">{vazio ?? 'Nada para mostrar aqui.'}</div>
  }

  const ids = lista.map(idDe)
  const todos = selecionavel && ids.length > 0 && ids.every((id) => marcados?.has(id))
  const alguns = selecionavel && !todos && ids.some((id) => marcados?.has(id))

  return (
    <div className="grade" role="table">
      <div className="grade-linha cab" style={{ gridTemplateColumns: grid }} role="row">
        {selecionavel &&
          (aoMarcarTodos ? (
            <button
              type="button"
              className={`marca-caixa${todos ? ' marcada' : alguns ? ' parcial' : ''}`}
              aria-pressed={todos ? true : alguns ? 'mixed' : false}
              aria-label={todos ? 'Desmarcar todos' : 'Marcar todos'}
              title={todos ? 'Desmarcar todos' : 'Marcar todos'}
              onClick={() => aoMarcarTodos(todos ? [] : ids)}
            >
              {todos && <IconeCerto tamanho={12} />}
              {alguns && <span className="marca-parcial" />}
            </button>
          ) : (
            <span />
          ))}
        {colunas.map((c) => {
          const pode = ordenavel && c.ordem !== null
          const ativa = ordem?.chave === c.chave && Boolean(colunaOrdem)
          const seta = ativa ? (ordem!.dir === 'desc' ? ' ▼' : ' ▲') : ''
          return (
            <span
              key={c.chave}
              className={c.classe}
              role="columnheader"
              aria-sort={ativa ? (ordem!.dir === 'desc' ? 'descending' : 'ascending') : undefined}
            >
              {pode ? (
                <button
                  type="button"
                  className={`grade-ordenar${ativa ? ' ativa' : ''}`}
                  title={`Ordenar por ${c.rotulo.toLowerCase()}`}
                  onClick={() => clicarCabecalho(c)}
                >
                  {c.rotulo}
                  {seta}
                </button>
              ) : (
                c.rotulo
              )}
            </span>
          )
        })}
      </div>

      {lista.map((item) => {
        const id = idDe(item)
        const marcada = marcados?.has(id) ?? false
        const nome = nomeDe?.(item) ?? `item ${id}`
        return (
          <div
            key={id}
            role="row"
            className={`grade-linha ${classeDe?.(item) ?? ''}${marcada ? ' marcada' : ''}${
              aoAbrir ? ' abrivel' : ''
            }`}
            style={{ gridTemplateColumns: grid }}
            title={aoAbrir ? `duplo-clique abre a ficha de ${nome}` : undefined}
            onDoubleClick={aoAbrir ? () => aoAbrir(item) : undefined}
            onClick={selecionavel && marcarAoClicar ? () => aoMarcar?.(id) : undefined}
          >
            {selecionavel && (
              <button
                type="button"
                className={`marca-caixa${marcada ? ' marcada' : ''}`}
                aria-pressed={marcada}
                aria-label={`Marcar ${nome}`}
                onClick={(e) => {
                  // com marcarAoClicar a linha tambem marca: sem isto, marcaria duas vezes
                  e.stopPropagation()
                  aoMarcar?.(id)
                }}
              >
                {marcada && <IconeCerto tamanho={12} />}
              </button>
            )}
            {colunas.map((c) => (
              <span key={c.chave} className={c.classe} role="cell">
                {c.render(item)}
              </span>
            ))}
          </div>
        )
      })}
    </div>
  )
}
