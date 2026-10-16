// A mesa de negociacao: comprar, pegar emprestado ou renovar.
//
// Nao decide nada. A cada mexida pergunta ao servidor como o outro lado esta
// lendo a proposta (o semaforo embaixo de cada campo) e, no Enviar, manda o
// pacote inteiro. Tres tentativas por semana; o contador mora no servidor, e
// fechar e reabrir nao zera - era assim que a janela antiga deixava insistir
// numa mesa que o outro lado ja tinha encerrado.

import { porque } from '../motivo'
import { useEffect, useRef, useState } from 'react'
import { api, ErroDaApi } from '../api'
import type { Atalho, Leitura, Mesa as DadosMesa, PropostaMesa, TipoMesa } from '../tipos'
import { dinheiro } from '../formato'
import { CampoDinheiro } from './CampoDinheiro'
import { Escudo } from './Escudo'

interface Props {
  tipo: TipoMesa
  id: number
  /** Chamado ao sair. fechou = houve negocio, a tela de tras precisa recarregar. */
  aoFechar: (fechou: boolean, recado: string | null) => void
}

const TIPO_ROTULO: Record<TipoMesa, string> = {
  compra: 'Mesa de compra',
  emprestimo: 'Mesa de emprestimo',
  renovacao: 'Renovacao de contrato',
}

const TITULO: Record<TipoMesa, string> = {
  compra: 'Negociar',
  emprestimo: 'Emprestimo de',
  renovacao: 'Renovar',
}

function Semaforo({ leitura, antes }: { leitura?: Leitura | null; antes?: string }) {
  if (!leitura) return null
  return (
    <div className={`semaforo tag-${leitura.estado}`}>
      {antes && <span className="tag-fraco">{antes} · </span>}
      {leitura.pct !== null && `${leitura.pct}% do pedido · `}
      {leitura.texto}
    </div>
  )
}

function Atalhos({ itens, aoEscolher }: { itens?: Atalho[]; aoEscolher: (v: number) => void }) {
  if (!itens?.length) return null
  return (
    <div className="atalhos">
      {itens.map((a) => (
        <button type="button" key={a.rotulo} className="bt-fantasma bt-mini" onClick={() => aoEscolher(a.valor)}>
          {a.rotulo}
        </button>
      ))}
    </div>
  )
}

export function Mesa({ tipo, id, aoFechar }: Props) {
  const [mesa, setMesa] = useState<DadosMesa | null>(null)
  const [proposta, setProposta] = useState<PropostaMesa>({})
  const [erro, setErro] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)
  const [fechou, setFechou] = useState<string | null>(null)
  const primeiraLeitura = useRef(true)
  const caixa = useRef<HTMLDivElement>(null)

  // primeira leitura: o servidor preenche a proposta com o que o outro lado pede
  useEffect(() => {
    api
      .lerMesa(tipo, id)
      .then((r) => {
        setMesa(r.mesa)
        setProposta({
          anos: r.mesa.anos,
          valor: r.mesa.valor,
          salario: r.mesa.salario,
          pct: r.mesa.pct,
          opcao: r.mesa.opcao,
        })
      })
      .catch((e) => setErro(e instanceof ErroDaApi ? e.message : String(e)))
  }, [tipo, id])

  // releitura com respiro a cada mexida na proposta
  useEffect(() => {
    if (!mesa) return
    if (primeiraLeitura.current) {
      primeiraLeitura.current = false
      return
    }
    let vivo = true
    const t = window.setTimeout(async () => {
      try {
        const r = await api.lerMesa(tipo, id, proposta)
        if (vivo) setMesa(r.mesa)
      } catch (e) {
        if (vivo) setErro(e instanceof ErroDaApi ? e.message : String(e))
      }
    }, 250)
    return () => {
      vivo = false
      window.clearTimeout(t)
    }
  }, [proposta, tipo, id])

  useEffect(() => {
    caixa.current?.focus()
  }, [])

  const mudar = (campo: keyof PropostaMesa, v: number) => setProposta((p) => ({ ...p, [campo]: v }))

  const enviar = async () => {
    setEnviando(true)
    setErro(null)
    try {
      const r = await api.propor(tipo, id, proposta)
      setMesa(r.mesa)
      if (r.fechou) setFechou(r.recado)
    } catch (e) {
      setErro(e instanceof ErroDaApi ? e.message : String(e))
    } finally {
      setEnviando(false)
    }
  }

  const sair = () => aoFechar(Boolean(fechou), fechou)
  const botaoFechar = useRef<HTMLButtonElement>(null)
  // fechou: o foco vai para o Fechar, que e a unica coisa a fazer agora
  useEffect(() => {
    if (fechou) botaoFechar.current?.focus()
  }, [fechou])

  // negocio fechado: o formulario sai de cena. Deixar os campos e os atalhos
  // na tela depois do sim parecia que a negociacao continuava
  const concluido = fechou ?? mesa?.fechada_com ?? null
  const bloqueada = !mesa || mesa.encerrada || enviando
  const semCaixa = Boolean(mesa?.falta_caixa)

  return (
    <div
      className="fundo-modal"
      role="dialog"
      aria-modal="true"
      aria-label={mesa ? `${TITULO[tipo]} ${mesa.nome}` : 'Mesa de negociacao'}
      onKeyDown={(e) => e.key === 'Escape' && sair()}
    >
      <div className="modal modal-largo dlg" ref={caixa} tabIndex={-1}>
        {!mesa ? (
          <>
            <header className="dlg-cab">
              <div className="dlg-textos">
                <h2>{TITULO[tipo]}…</h2>
              </div>
            </header>
            <div className="dlg-corpo">
              <p>{erro ?? 'abrindo a mesa…'}</p>
            </div>
            <div className="modal-acoes">
              <button type="button" className="bt-fantasma bt-media" onClick={sair}>Fechar</button>
            </div>
          </>
        ) : (
          <>
            <header className="dlg-cab">
              {!mesa.livre && <Escudo nome={mesa.clube} tamanho={34} />}
              <div className="dlg-textos">
                <div className="dlg-kicker">{TIPO_ROTULO[tipo]}</div>
                <h2>{mesa.nome}</h2>
                <div className="dlg-sub">
                  {mesa.descricao} · {mesa.livre ? 'agente livre' : mesa.clube}
                </div>
              </div>
              {!concluido && (
                <div className="mesa-tentativas" aria-label={`tentativa ${mesa.rodada + 1} de ${mesa.tentativas}`}>
                  <span className="mesa-tent-rotulo">Tentativas</span>
                  <span className="mesa-tent-bolas">
                    {Array.from({ length: mesa.tentativas }, (_, i) => (
                      <i key={i} className={i < mesa.rodada || mesa.encerrada ? 'usada' : i === mesa.rodada ? 'atual' : 'livre'} />
                    ))}
                  </span>
                </div>
              )}
            </header>
            <div className="dlg-corpo">
            <div className="mesa-sub">
              {mesa.contexto} Seu caixa: {mesa.caixa}
              {tipo !== 'renovacao' && (
                <>
                  {' '}· verba para contratar: <strong>{mesa.verba}</strong> ({mesa.reserva} ficam reservados para{' '}
                  {mesa.reserva_meses} meses de folha e custos)
                </>
              )}
              .
            </div>
            <div className={`mesa-sub ${mesa.aberto ? 'tag-ok' : 'tag-atencao'}`}>{mesa.janela}</div>
            {mesa.acabando && (
              <div className="mesa-sub linha-critica">
                Contrato acabando: se nao renovar, ele sai de graca na virada da temporada.
              </div>
            )}

            {!concluido && (
              <div className="mesa-ficha" role="table" aria-label="Pedido contra oferta">
                <div className="mesa-ficha-linha cab" role="row">
                  <span role="columnheader">Item</span>
                  <span role="columnheader">Ele pede</span>
                  <span role="columnheader">Sua oferta</span>
                </div>
                {tipo === 'compra' && !mesa.livre && (
                  <div className="mesa-ficha-linha" role="row">
                    <span role="cell">Passe</span>
                    <span role="cell" className="pede">{mesa.pedido}</span>
                    <span role="cell" className={`oferta ${mesa.leitura_passe?.estado ?? ''}`}>{dinheiro(proposta.valor ?? 0)}</span>
                  </div>
                )}
                {tipo === 'emprestimo' && (
                  <>
                    <div className="mesa-ficha-linha" role="row">
                      <span role="cell">Fatia do salario</span>
                      <span role="cell" className="pede">{mesa.exigencia_pct}%</span>
                      <span role="cell" className={`oferta ${mesa.leitura_pct?.estado ?? ''}`}>{proposta.pct ?? 0}%</span>
                    </div>
                    <div className="mesa-ficha-linha" role="row">
                      <span role="cell">Opcao de compra</span>
                      <span role="cell" className="pede">-</span>
                      <span role="cell" className={`oferta ${mesa.leitura_opcao?.estado ?? ''}`}>{proposta.opcao ? dinheiro(proposta.opcao) : 'sem opcao'}</span>
                    </div>
                  </>
                )}
                {tipo !== 'emprestimo' && (
                  <div className="mesa-ficha-linha" role="row">
                    <span role="cell">Salario por mes</span>
                    <span role="cell" className="pede">{mesa.exigencia}</span>
                    <span role="cell" className={`oferta ${mesa.leitura_salario?.estado ?? ''}`}>{dinheiro(proposta.salario ?? 0)}</span>
                  </div>
                )}
                {tipo !== 'emprestimo' && (
                  <div className="mesa-ficha-linha" role="row">
                    <span role="cell">Contrato</span>
                    <span role="cell" className="pede">-</span>
                    <span role="cell" className="oferta">{proposta.anos ?? mesa.anos} {(proposta.anos ?? mesa.anos) === 1 ? 'ano' : 'anos'}</span>
                  </div>
                )}
              </div>
            )}

            {concluido && (
              <section className="mesa-bloco mesa-fechada" role="status">
                <div className="mesa-fechada-titulo">Negocio fechado</div>
                <div>{concluido}</div>
                <div className="tag-fraco">
                  {mesa.precontrato?.ativo
                    ? 'Ele termina a temporada onde esta e chega na virada; da para cancelar em Mercado > Vender.'
                    : mesa.aberto
                      ? 'Ele ja esta no seu elenco.'
                      : 'Fica acertado para a abertura da janela; da para cancelar em Mercado > Vender.'}
                </div>
              </section>
            )}

            {!concluido && (
            <>
            {/* ------------------------------------------------- passe */}
            {tipo === 'compra' && (
              <section className="mesa-bloco">
                <div className="painel-titulo">
                  Passe{mesa.intocavel && !proposta.precontrato ? ' — ele nao esta a venda' : ''}
                </div>
                {mesa.precontrato?.pode && (
                  <div className="segmento mesa-linha" role="group" aria-label="Tipo de contratacao">
                    <button
                      type="button"
                      className={`bt-fantasma bt-mini${!proposta.precontrato ? ' ativa' : ''}`}
                      aria-pressed={!proposta.precontrato}
                      onClick={() => setProposta((p) => ({ ...p, precontrato: false, valor: mesa.valor }))}
                    >
                      Comprar o passe
                    </button>
                    <button
                      type="button"
                      className={`bt-fantasma bt-mini${proposta.precontrato ? ' ativa' : ''}`}
                      aria-pressed={Boolean(proposta.precontrato)}
                      onClick={() => setProposta((p) => ({ ...p, precontrato: true, valor: 0 }))}
                    >
                      Pre-contrato, sem passe
                    </button>
                  </div>
                )}
                {mesa.precontrato?.porque_nao && (
                  <div className="tag-fraco mesa-linha">Ultimo ano de contrato: {mesa.precontrato.porque_nao}.</div>
                )}
                {proposta.precontrato ? (
                  <div className="tag-ok mesa-linha">
                    Pre-contrato: o contrato dele com o {mesa.clube} acaba no fim da temporada. Sem passe a pagar;
                    ele termina o ano la e chega de graca na virada. So falta acertar o salario.
                  </div>
                ) : mesa.livre ? (
                  <div className="tag-ok mesa-linha">Agente livre: nao ha passe a pagar, so acertar contrato.</div>
                ) : (
                  <>
                    <div className="mesa-linha tag-atencao">
                      O {mesa.clube} libera a partir de {mesa.pedido}.
                    </div>
                    {mesa.disputa && (
                      <div className="mesa-linha tag-critico">
                        O {mesa.disputa.clube} tambem quer e ofereceu {mesa.disputa.lance}. Abaixo disso o {mesa.clube}{' '}
                        nao fecha, e se as tentativas acabarem o {mesa.disputa.clube} leva.
                      </div>
                    )}
                    <CampoDinheiro
                      rotulo="Oferta pelo passe"
                      valor={proposta.valor ?? 0}
                      aoMudar={(v) => mudar('valor', v)}
                    />
                    <Atalhos itens={mesa.atalhos_passe} aoEscolher={(v) => mudar('valor', v)} />
                    <Semaforo leitura={mesa.leitura_passe} />
                    <div className={`mesa-linha ${semCaixa ? 'linha-critica' : 'tag-fraco'}`}>
                      {semCaixa
                        ? `Passa da sua verba: com esse salario, o maximo pelo passe e ${mesa.verba_com_salario}. O resto do caixa paga a folha.`
                        : `Caixa depois de pagar o passe: ${mesa.caixa_depois} · verba com o salario dele: ${mesa.verba_com_salario}`}
                    </div>
                  </>
                )}
              </section>
            )}

            {/* ------------------------------------------- emprestimo */}
            {tipo === 'emprestimo' && (
              <>
                <section className="mesa-bloco">
                  <div className="painel-titulo">Fatia do salario</div>
                  <div className="mesa-linha tag-atencao">
                    Salario dele: {mesa.salario_atual} por mes. O {mesa.clube} quer que voce assuma ao
                    menos {mesa.exigencia_pct}%.
                  </div>
                  <CampoDinheiro
                    rotulo="Voce banca"
                    unidade="%"
                    maximo={100}
                    valor={proposta.pct ?? 0}
                    aoMudar={(v) => mudar('pct', v)}
                  />
                  <Atalhos
                    itens={[
                      { rotulo: 'o minimo pedido', valor: mesa.exigencia_pct ?? 0 },
                      { rotulo: '50%', valor: 50 },
                      { rotulo: '100%', valor: 100 },
                    ]}
                    aoEscolher={(v) => mudar('pct', v)}
                  />
                  <Semaforo leitura={mesa.leitura_pct} antes={`pedem ${mesa.exigencia_pct}%`} />
                  <div className="mesa-linha tag-fraco">{mesa.divisao}</div>
                  {mesa.taxa && (
                    <div className={`mesa-linha ${semCaixa ? 'linha-critica' : 'tag-atencao'}`}>
                      O dono cobra {mesa.taxa} de taxa, alem do salario. Ela vai junto com a proposta.
                    </div>
                  )}
                </section>
                <section className="mesa-bloco">
                  <div className="painel-titulo">Opcao de compra</div>
                  <div className="mesa-linha tag-fraco">
                    Preco travado agora para comprar em definitivo no fim. Zero = sem opcao.
                  </div>
                  <CampoDinheiro
                    rotulo="Opcao de compra"
                    valor={proposta.opcao ?? 0}
                    aoMudar={(v) => mudar('opcao', v)}
                  />
                  <Atalhos itens={mesa.atalhos_opcao} aoEscolher={(v) => mudar('opcao', v)} />
                  <Semaforo leitura={mesa.leitura_opcao} />
                </section>
              </>
            )}

            {/* ------------------------------------ contrato (compra/renovacao) */}
            {tipo !== 'emprestimo' && (
              <section className="mesa-bloco">
                <div className="painel-titulo">{tipo === 'renovacao' ? 'Novo contrato' : 'Contrato'}</div>
                <div className="anos" role="radiogroup" aria-label="Anos de contrato">
                  <span className="plano-nome">Anos</span>
                  {[1, 2, 3, 4, 5].map((n) => (
                    <button
                      type="button"
                      role="radio"
                      aria-checked={proposta.anos === n}
                      key={n}
                      className={proposta.anos === n ? 'ativo' : ''}
                      onClick={() => mudar('anos', n)}
                    >
                      {n}
                    </button>
                  ))}
                  <span className="tag-fraco txt-p">contrato curto sai mais caro</span>
                </div>
                <CampoDinheiro
                  rotulo="Salario mensal oferecido"
                  valor={proposta.salario ?? 0}
                  aoMudar={(v) => mudar('salario', v)}
                />
                <Atalhos itens={mesa.atalhos_salario} aoEscolher={(v) => mudar('salario', v)} />
                <Semaforo leitura={mesa.leitura_salario} antes={`ele pede ${mesa.exigencia}`} />
                <div className="mesa-linha tag-fraco">{mesa.folha_depois}</div>
              </section>
            )}

            </>
            )}

            {/* ------------------------------------------------ conversa */}
            {!concluido && mesa.falas.length > 0 && (
              <ol className="mesa-falas" aria-live="polite">
                {mesa.falas.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ol>
            )}
            {erro && <div className="linha-critica mesa-linha">{erro}</div>}
            </div>

            <div className="modal-acoes">
              <span className="resumo-mesa">
                {concluido
                  ? 'negocio fechado'
                  : mesa.encerrada
                    ? 'mesa encerrada nesta semana'
                    : `tentativa ${mesa.rodada + 1} de ${mesa.tentativas}`}
              </span>
              <button type="button" ref={botaoFechar} className={concluido ? 'bt-acao bt-media' : 'bt-fantasma bt-media'} onClick={sair}>
                {concluido || mesa.encerrada ? 'Fechar' : tipo === 'renovacao' ? 'Deixar pra depois' : 'Desistir'}
              </button>
              {!concluido && !mesa.encerrada && (
                <button
                  type="button"
                  className="bt-acao bt-media"
                  title={porque([[bloqueada, 'Esta mesa ja fechou nesta semana'], [semCaixa, 'Falta verba para esta proposta']], semCaixa ? 'passa da verba para contratar' : undefined)}
                  disabled={bloqueada || semCaixa}
                  onClick={enviar}
                >
                  {tipo === 'compra'
                    ? proposta.precontrato
                      ? 'Propor pre-contrato'
                      : mesa.livre
                        ? 'Propor contrato'
                        : 'Enviar proposta'
                    : tipo === 'emprestimo'
                      ? 'Propor emprestimo'
                      : 'Propor renovacao'}
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
