// O quadro de formacao: o campo vira prancheta com um -/+ por linha.
//
// Steppers e nao arrastar: funcionam no teclado, no toque e no leitor de
// tela, e o total 10/10 fica sempre a vista. A cada clique o servidor devolve
// a previa (onde cada um fica e a forca prevista) sem gravar nada; so o
// Aplicar mexe no jogo. Cancelar descarta, e por isso nao precisa de desfazer
// aqui dentro.

import { useEffect, useRef, useState } from 'react'
import { api, ErroDaApi } from '../api'
import type { Contagem, PreviaEsquema } from '../tipos'
import { Campo } from './Campo'

interface Props {
  inicial: Contagem
  limites: Record<string, { min: number; max: number }>
  ocupado: boolean
  aoAplicar: (contagem: Contagem) => void
  aoSair: () => void
}

// da nossa area para a do adversario, na mesma ordem em que o campo desenha
const LINHAS: { id: keyof Contagem; nome: string; plural: string }[] = [
  { id: 'ZAG', nome: 'zagueiro', plural: 'Zagueiros' },
  { id: 'LAT', nome: 'lateral', plural: 'Laterais' },
  { id: 'VOL', nome: 'volante', plural: 'Volantes' },
  { id: 'MEI', nome: 'meia', plural: 'Meias' },
  { id: 'ATA', nome: 'atacante', plural: 'Atacantes' },
]

const LINHA_TOTAL = 10

function igual(a: Contagem, b: Contagem) {
  return LINHAS.every((l) => a[l.id] === b[l.id])
}

export function EditorFormacao({ inicial, limites, ocupado, aoAplicar, aoSair }: Props) {
  const [cont, setCont] = useState<Contagem>(inicial)
  const [previa, setPrevia] = useState<PreviaEsquema | null>(null)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [confirmarSaida, setConfirmarSaida] = useState(false)
  const primeiro = useRef<HTMLButtonElement>(null)

  const total = LINHAS.reduce((s, l) => s + cont[l.id], 0)
  const mudou = !igual(cont, inicial)
  const falta = LINHA_TOTAL - total

  // o foco entra na primeira linha: quem abriu pelo teclado ja pode mexer
  useEffect(() => {
    primeiro.current?.focus()
  }, [])

  // previa com respiro: clicar tres vezes seguidas faz uma pergunta, nao tres
  useEffect(() => {
    if (total !== LINHA_TOTAL) {
      setPrevia(null)
      return
    }
    let vivo = true
    setCarregando(true)
    const t = window.setTimeout(async () => {
      try {
        const r = await api.previaEsquema(cont)
        if (vivo) {
          setPrevia(r.previa)
          setErro(null)
        }
      } catch (e) {
        if (vivo) setErro(e instanceof ErroDaApi ? e.message : String(e))
      } finally {
        if (vivo) setCarregando(false)
      }
    }, 300)
    return () => {
      vivo = false
      window.clearTimeout(t)
    }
  }, [cont, total])

  const sair = () => {
    if (mudou && !confirmarSaida) {
      setConfirmarSaida(true)
      return
    }
    aoSair()
  }

  const mexer = (id: keyof Contagem, delta: number) => {
    setConfirmarSaida(false)
    // funcional: dois cliques rapidos nao podem partir do mesmo numero
    setCont((atual) => ({ ...atual, [id]: atual[id] + delta }))
  }

  let ajuda = ''
  if (falta > 0) ajuda = `Faltam ${falta}`
  if (falta < 0) ajuda = `Sobram ${-falta}`

  return (
    <div
      className="editor-formacao"
      onKeyDown={(e) => {
        if (e.key === 'Escape') {
          e.stopPropagation()
          sair()
        }
      }}
    >
      <div className="editor-campo" aria-hidden={carregando}>
        {previa?.jogadores ? (
          <Campo jogadores={previa.jogadores} vagasAbertas={previa.vagas_abertas ?? 0} />
        ) : (
          <div className="campo-area editor-vazio">
            <span>{total === LINHA_TOTAL ? 'calculando…' : `${ajuda} jogador(es) de linha`}</span>
          </div>
        )}
      </div>

      <div className="editor-linhas">
        <div className="editor-linha fixa">
          <span className="plano-nome">Goleiro</span>
          <span className="editor-num">1</span>
          <span className="editor-lim">fixo</span>
        </div>
        {LINHAS.map((l, i) => {
          const lim = limites[l.id] ?? { min: 0, max: 5 }
          const noMin = cont[l.id] <= lim.min
          const noMax = cont[l.id] >= lim.max
          return (
            <fieldset className="editor-linha" key={l.id}>
              <legend className="plano-nome">{l.plural}</legend>
              <div className="stepper">
                <button
                  type="button"
                  ref={i === 0 ? primeiro : undefined}
                  disabled={noMin}
                  title={noMin ? `Minimo ${lim.min} ${lim.min === 1 ? l.nome : l.plural.toLowerCase()}` : undefined}
                  aria-label={`Remover ${l.nome}, atual ${cont[l.id]}`}
                  onClick={() => mexer(l.id, -1)}
                >
                  −
                </button>
                <span className="editor-num" aria-hidden="true">{cont[l.id]}</span>
                <button
                  type="button"
                  disabled={noMax}
                  title={noMax ? `Maximo ${lim.max} ${l.plural.toLowerCase()}` : undefined}
                  aria-label={`Adicionar ${l.nome}, atual ${cont[l.id]}`}
                  onClick={() => mexer(l.id, +1)}
                >
                  +
                </button>
              </div>
              <span className="editor-lim">
                {lim.min}–{lim.max}
              </span>
            </fieldset>
          )
        })}
      </div>

      <div className="barra-acoes editor-rodape">
        <span className="resumo" aria-live="polite">
          <strong className={falta === 0 ? 'tag-ok' : 'tag-atencao'}>
            {total}/{LINHA_TOTAL} jogadores de linha
          </strong>
          {ajuda && <> · {ajuda}</>}
          {falta === 0 && previa?.valida && (
            <span className={carregando ? 'carregando-num' : undefined}>
              {' '}
              · {previa.rotulo} · Forca prevista: ataque {previa.ataque} / defesa {previa.defesa}
              {previa.improvisados ? ` · ${previa.improvisados} improvisado(s)` : ' · ninguem improvisado'}
              {previa.mantem_os_11 ? ' · mesmos 11, so as vagas mudam' : ' · o automatico remonta o time'}
            </span>
          )}
          {erro && <span className="linha-critica"> · {erro}</span>}
        </span>

        {confirmarSaida ? (
          <>
            <span className="aviso">Descartar alteracoes na formacao?</span>
            <button type="button" className="bt-fantasma bt-perigo" onClick={aoSair}>
              Descartar
            </button>
            <button type="button" className="bt-fantasma" onClick={() => setConfirmarSaida(false)}>
              Continuar editando
            </button>
          </>
        ) : (
          <>
            <button type="button" className="bt-fantasma" onClick={sair}>
              Cancelar
            </button>
            <button
              type="button"
              className="bt-acao bt-media"
              disabled={ocupado || falta !== 0 || !mudou}
              title={falta !== 0 ? ajuda : !mudou ? 'Nada mudou' : undefined}
              onClick={() => aoAplicar(cont)}
            >
              Aplicar
            </button>
          </>
        )}
      </div>
    </div>
  )
}
