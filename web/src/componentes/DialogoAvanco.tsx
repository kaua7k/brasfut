// Simular: o tamanho do pulo e as condicoes de parar antes.
//
// Jogo a jogo, 1 semana, 1 mes, ate a janela e a temporada toda. O navegador
// roda o laco uma semana por pedido - a barra anda, o relato de cada semana
// aparece na hora e o Parar vale no fim da semana em curso. Quem diz quantas
// semanas cada opcao cobre, e por que parar, e o servidor.
//
// A ultima escolha e as paradas ficam guardadas no navegador: quem simula mes
// a mes nao quer remarcar tudo toda vez.

import { useEffect, useRef, useState } from 'react'
import { api, ErroDaApi } from '../api'
import type { LinhaRelato, OpcaoAvanco, Paradas, Pendencia } from '../tipos'

interface Props {
  /** houve = pelo menos uma semana andou; a tela de tras precisa se refazer. */
  aoFechar: (houve: boolean, pendencia: Pendencia | null) => void
  aoAbrirEscalacao: () => void
}

const TEXTO_PARADA: Record<keyof Paradas, string> = {
  lesao: 'alguem do time titular se machucar',
  janela: 'a janela de transferencias abrir',
  proposta: 'chegar proposta por um jogador seu',
  quebrado: 'o time ficar sem condicao de entrar em campo',
  emprego: 'outro clube quiser contratar voce',
}

function lembrar<T>(chave: string, padrao: T): T {
  try {
    const v = localStorage.getItem(chave)
    return v ? (JSON.parse(v) as T) : padrao
  } catch {
    return padrao
  }
}

function guardar(chave: string, valor: unknown) {
  try {
    localStorage.setItem(chave, JSON.stringify(valor))
  } catch {
    // navegador sem armazenamento: so nao lembra da proxima vez
  }
}

export function DialogoAvanco({ aoFechar, aoAbrirEscalacao }: Props) {
  const [opcoes, setOpcoes] = useState<OpcaoAvanco[]>([])
  const [escolha, setEscolha] = useState<string>(() => lembrar('brasfut.avanco.escolha', 'semana'))
  const [paradas, setParadas] = useState<Paradas | null>(null)
  const [rodando, setRodando] = useState(false)
  const [feitas, setFeitas] = useState(0)
  const [total, setTotal] = useState(0)
  const [linhas, setLinhas] = useState<LinhaRelato[]>([])
  const [motivo, setMotivo] = useState<string | null>(null)
  const [quebrado, setQuebrado] = useState<string | null>(null)
  const [erro, setErro] = useState<string | null>(null)
  const pedirParada = useRef(false)
  const houve = useRef(false)
  const pendencia = useRef<Pendencia | null>(null)
  const fimDoLog = useRef<HTMLDivElement>(null)

  useEffect(() => {
    api
      .opcoesAvanco()
      .then((r) => {
        setOpcoes(r.opcoes)
        // preferencia antiga salva no navegador nao tem as paradas novas: o servidor completa
        setParadas({ ...r.paradas, ...lembrar('brasfut.avanco.paradas', r.paradas) })
        // a escolha guardada pode nao existir nesta fase (pre-temporada so tem uma)
        if (!r.opcoes.some((o) => o.id === escolha && o.semanas > 0)) setEscolha(r.opcoes[0]?.id ?? 'semana')
      })
      .catch((e) => setErro(e instanceof ErroDaApi ? e.message : String(e)))
    // so na abertura: a escolha guardada entra como ponto de partida
  }, [])

  // chaves de proposito: no Chromium novo scrollIntoView devolve uma Promise,
  // e efeito que devolve algo que nao e funcao derruba a tela inteira
  useEffect(() => {
    fimDoLog.current?.scrollIntoView({ block: 'nearest' })
  }, [linhas])

  const opcao = opcoes.find((o) => o.id === escolha)

  const rodar = async (confirmarQuebrado = false) => {
    if (!opcao || !paradas || opcao.semanas <= 0) return
    guardar('brasfut.avanco.escolha', escolha)
    guardar('brasfut.avanco.paradas', paradas)
    setRodando(true)
    setMotivo(null)
    setQuebrado(null)
    setErro(null)
    pedirParada.current = false
    setTotal(opcao.semanas)
    setFeitas(0)
    let confirmar = confirmarQuebrado
    let fim = ''
    try {
      for (let i = 0; i < opcao.semanas; i++) {
        if (pedirParada.current) {
          fim = 'voce mandou parar'
          break
        }
        const r = await api.passoAvanco(confirmar, paradas, true)
        if (r.confirmar) {
          // time quebrado antes de entrar em campo
          // "jogar assim mesmo" vale para o pulo inteiro, nao so a primeira semana
          if (paradas.quebrado && !confirmarQuebrado) {
            setQuebrado(r.confirmar.texto)
            fim = 'o time nao tem condicao de entrar em campo'
            break
          }
          confirmar = true
          i -= 1
          continue
        }
        confirmar = false
        houve.current = true
        setFeitas(i + 1)
        setLinhas((l) => [...l, ...(r.linhas ?? [])])
        if (r.opcoes) setOpcoes(r.opcoes)
        if (r.pendencia) pendencia.current = r.pendencia
        if (r.parar) {
          fim = r.parar
          break
        }
        if (escolha === 'jogo' && r.jogou) {
          fim = 'seu clube jogou'
          break
        }
      }
    } catch (e) {
      setErro(e instanceof ErroDaApi ? e.message : String(e))
    } finally {
      setRodando(false)
      setMotivo(fim || null)
      if (pendencia.current) aoFechar(true, pendencia.current)
    }
  }

  const fechar = () => !rodando && aoFechar(houve.current, pendencia.current)

  return (
    <div
      className="fundo-modal"
      role="dialog"
      aria-modal="true"
      aria-label="Simular"
      onKeyDown={(e) => e.key === 'Escape' && fechar()}
    >
      <div className="modal modal-largo">
        <h2>Simular</h2>
        <p>Escolha o tamanho do pulo. Fim do estadual e fim da temporada param sempre.</p>

        {opcoes.length === 0 && !erro && (
          <div className="mesa-bloco tag-atencao">
            Nada para simular agora: a virada do ano e o comeco do estadual tem aviso e resumo
            proprios. Feche e use o botao do topo.
          </div>
        )}

        <fieldset className="mesa-bloco avanco-opcoes" disabled={rodando} hidden={opcoes.length === 0}>
          <legend className="painel-titulo">Quanto avancar</legend>
          {opcoes.map((o) => (
            <label key={o.id} className={`avanco-opcao${o.semanas <= 0 ? ' desligada' : ''}`}>
              <input
                type="radio"
                name="ritmo"
                value={o.id}
                checked={escolha === o.id}
                disabled={o.semanas <= 0}
                onChange={() => setEscolha(o.id)}
              />
              <strong>{o.rotulo}</strong>
              <span className="tag-fraco">{o.nota}</span>
            </label>
          ))}
        </fieldset>

        {paradas && (
          <fieldset className="mesa-bloco" disabled={rodando}>
            <legend className="painel-titulo">Parar antes se</legend>
            {(Object.keys(TEXTO_PARADA) as (keyof Paradas)[]).map((k) => (
              <label key={k} className="avanco-parada">
                <input
                  type="checkbox"
                  checked={paradas[k]}
                  onChange={(e) => setParadas({ ...paradas, [k]: e.target.checked })}
                />
                {TEXTO_PARADA[k]}
              </label>
            ))}
          </fieldset>
        )}

        {(rodando || feitas > 0) && (
          <div className="avanco-progresso">
            <progress max={total || 1} value={feitas} aria-label="Semanas simuladas" />
            <span className="tag-fraco">
              {rodando ? `${feitas} de ${total}` : `${feitas} semana(s) simulada(s)`}
              {motivo && ` · parou: ${motivo}`}
            </span>
          </div>
        )}

        {quebrado && (
          <div className="mesa-bloco avanco-quebrado">
            <div className="linha-critica" style={{ whiteSpace: 'pre-line' }}>{quebrado}</div>
            <div className="modal-acoes" style={{ justifyContent: 'flex-start' }}>
              <button type="button" className="bt-fantasma" onClick={aoAbrirEscalacao}>
                Abrir escalacao
              </button>
              <button type="button" className="bt-fantasma bt-perigo" onClick={() => rodar(true)}>
                Jogar assim mesmo
              </button>
            </div>
          </div>
        )}

        {linhas.length > 0 && (
          <div className="avanco-log" aria-live="polite">
            {linhas.map((l, i) => (
              <div key={i} className={`tag-${l.estado}`}>{l.texto}</div>
            ))}
            <div ref={fimDoLog} />
          </div>
        )}
        {erro && <div className="mesa-linha linha-critica">{erro}</div>}

        <div className="modal-acoes">
          <button type="button" className="bt-fantasma" disabled={rodando} onClick={fechar}>
            Fechar
          </button>
          {rodando ? (
            <button type="button" className="bt-fantasma bt-perigo" onClick={() => (pedirParada.current = true)}>
              Parar
            </button>
          ) : (
            <button
              type="button"
              className="bt-acao bt-media"
              disabled={!opcao || opcao.semanas <= 0}
              onClick={() => rodar(false)}
            >
              {feitas > 0 ? 'Simular mais' : 'Simular'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
