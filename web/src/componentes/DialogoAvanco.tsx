// Simular: o tamanho do pulo e as condicoes de parar antes.
//
// Jogo a jogo, 1 semana, 1 mes, ate a janela e a temporada toda. O navegador
// roda o laco uma semana por pedido - a barra anda, o relato de cada semana
// aparece na hora e o Parar vale no fim da semana em curso. Quem diz quantas
// semanas cada opcao cobre, e por que parar, e o servidor.
//
// A ultima escolha e as paradas ficam guardadas no navegador: quem simula mes
// a mes nao quer remarcar tudo toda vez.

import { porque } from '../motivo'
import { useEffect, useRef, useState } from 'react'
import { api, ErroDaApi } from '../api'
import { plural } from '../formato'
import { iconeDeEstado } from '../icones'
import type { OpcaoAvanco, Paradas, Partida, Pendencia, RelatoSemana } from '../tipos'
import { ResumoPartida } from './Partida'

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
  const [semanas, setSemanas] = useState<RelatoSemana[]>([])
  const [partidas, setPartidas] = useState<Partida[]>([])
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
  }, [semanas])

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
    setPartidas([])
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
        if (r.semana) setSemanas((l) => [...l, r.semana!])
        if (r.partidas?.length) setPartidas((p) => [...p, ...r.partidas!].slice(-5))
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
      <div className="modal modal-largo simular">
        <h2>Simular</h2>
        <p className="tag-fraco m-0">
          Escolha o tamanho do pulo. Fim do estadual e fim da temporada param sempre.
        </p>

        {opcoes.length === 0 && !erro && (
          <div className="mesa-bloco tag-atencao">
            Nada para simular agora: a virada do ano e o comeco do estadual tem aviso e resumo
            proprios. Feche e use o botao do topo.
          </div>
        )}

        <fieldset className="simular-bloco" disabled={rodando} hidden={opcoes.length === 0}>
          <legend className="painel-titulo">Quanto avancar</legend>
          <div className="ritmos">
            {opcoes.map((o) => (
              <label
                key={o.id}
                className={`ritmo${escolha === o.id ? ' ativo' : ''}${o.semanas <= 0 ? ' desligada' : ''}`}
              >
                <input
                  type="radio"
                  className="so-leitor"
                  name="ritmo"
                  value={o.id}
                  checked={escolha === o.id}
                  disabled={o.semanas <= 0}
                  onChange={() => setEscolha(o.id)}
                />
                <span className="ritmo-nome">{o.rotulo}</span>
                <span className="ritmo-nota">{o.semanas > 0 ? o.nota : 'nada para simular agora'}</span>
              </label>
            ))}
          </div>
        </fieldset>

        {paradas && (
          <fieldset className="simular-bloco" disabled={rodando}>
            <legend className="painel-titulo">Parar antes se</legend>
            <div className="paradas">
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
            </div>
          </fieldset>
        )}

        {(rodando || feitas > 0) && (
          <div className="avanco-progresso">
            <progress max={total || 1} value={feitas} aria-label="Semanas simuladas" />
            <span className="tag-fraco">
              {rodando ? `semana ${feitas} de ${total}` : `${plural(feitas, 'semana')} simulada${feitas === 1 ? '' : 's'}`}
            </span>
          </div>
        )}

        {quebrado && (
          <div className="mesa-bloco avanco-quebrado">
            <div className="linha-critica pre-linha">{quebrado}</div>
            <div className="modal-acoes a-esquerda">
              <button type="button" className="bt-fantasma" onClick={aoAbrirEscalacao}>
                Abrir escalacao
              </button>
              <button type="button" className="bt-fantasma bt-perigo" onClick={() => rodar(true)}>
                Jogar assim mesmo
              </button>
            </div>
          </div>
        )}

        {semanas.length > 0 && (
          <div className="relato" aria-live="polite">
            {semanas.map((sem, i) => (
              <section className="relato-semana" key={i} aria-label={sem.titulo}>
                <h3 className="relato-titulo">{sem.titulo}</h3>
                {sem.jogos.length === 0 && <div className="relato-vazio">sem jogo · o elenco descansou</div>}
                {sem.jogos.map((j, k) => (
                  <div className="relato-jogo" key={k}>
                    <span
                      className={`forma-badge ${j.resultado}`}
                      aria-label={{ V: 'vitoria', E: 'empate', D: 'derrota' }[j.resultado]}
                    >
                      {j.resultado}
                    </span>
                    <span className={`relato-time${j.eu === 0 ? ' eu' : ''}`}>{j.times[0]}</span>
                    <span className={`relato-placar ${j.estado}`}>
                      {j.placar[0]} x {j.placar[1]}
                    </span>
                    <span className={`relato-time fora${j.eu === 1 ? ' eu' : ''}`}>{j.times[1]}</span>
                    <span className="relato-comp">{j.comp}</span>
                    {j.decisao && (
                      <span className={`relato-decisao ${j.decisao.estado}`}>
                        {iconeDeEstado(j.decisao.estado, 14)}
                        {j.decisao.texto}
                      </span>
                    )}
                  </div>
                ))}
                {sem.avisos.map((a, k) => (
                  <div className={`relato-aviso ${a.estado}`} key={k}>
                    {iconeDeEstado(a.estado, 14)}
                    {a.texto}
                  </div>
                ))}
              </section>
            ))}
            {motivo && !rodando && <div className="relato-fim">Parou: {motivo}</div>}
            <div ref={fimDoLog} />
          </div>
        )}
        {erro && <div className="mesa-linha linha-critica">{erro}</div>}

        {/* terminou com jogo: o resumo da ultima partida, sem clique a mais */}
        {!rodando && partidas.length > 0 && <ResumoPartida key={partidas[partidas.length - 1].chave} partidas={partidas} />}

        <div className="modal-acoes">
          <button type="button" className="bt-fantasma" title={porque([[rodando, 'Espere a simulacao parar']])}
          disabled={rodando} onClick={fechar}>
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
              title={porque([[!opcao, 'Escolha um ritmo'], [!opcao || opcao.semanas <= 0, 'Nao ha semanas para simular nesse ritmo']])}
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
