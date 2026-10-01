// O que trava o jogo: clube novo depois da demissao, ou o fim da carreira.
//
// As ofertas vem do servidor com a mesma regra do motor (quatro clubes das
// Series B, C e D, nunca o que demitiu). Encerrar a carreira pede um segundo
// clique ali mesmo - e irreversivel, nao pode estar a um clique errado.

import { porque, AGUARDE } from '../motivo'
import { useState } from 'react'
import type { Pendencia } from '../tipos'

interface Props {
  pendencia: Pendencia
  ocupado: boolean
  aoEscolher: (id: number) => void
  aoEncerrar: () => void
  aoNovaCarreira: () => void
}

export function JanelaPendencia({ pendencia, ocupado, aoEscolher, aoEncerrar, aoNovaCarreira }: Props) {
  const [confirmarFim, setConfirmarFim] = useState(false)

  if (pendencia.tipo === 'carreira_encerrada') {
    return (
      <div className="fundo-modal" role="dialog" aria-modal="true" aria-label={pendencia.titulo}>
        <div className="modal dlg">
          <header className="dlg-cab">
            <div className="dlg-textos">
              <div className="dlg-kicker">Fim de jogo</div>
              <h2>{pendencia.titulo}</h2>
              <div className="dlg-sub">A historia que ficou:</div>
            </div>
          </header>
          <div className="dlg-corpo">
            <ul className="ficha-notas">
              {(pendencia.historico ?? []).map((h, i) => (
                <li key={i}>{h}</li>
              ))}
            </ul>
          </div>
          <div className="modal-acoes">
            <button type="button" className="bt-acao bt-media" title={porque([[ocupado, AGUARDE]])}
            disabled={ocupado} onClick={aoNovaCarreira}>
              Comecar nova carreira
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fundo-modal" role="dialog" aria-modal="true" aria-label={pendencia.titulo}>
      <div className="modal modal-largo dlg">
        <header className="dlg-cab">
          <div className="dlg-textos">
            <div className="dlg-kicker">Voce foi demitido</div>
            <h2>{pendencia.titulo}</h2>
            <div className="dlg-sub">
              {pendencia.opcoes.length
                ? `Estes clubes querem voce${pendencia.de ? ` depois do ${pendencia.de}` : ''}. Escolha um para continuar a carreira.`
                : 'Nenhum clube fez oferta.'}
            </div>
          </div>
        </header>
        <div className="dlg-corpo">
        {pendencia.motivo && <p className="linha-critica">{pendencia.motivo}</p>}
        <div className="lista-clubes">
          {pendencia.opcoes.map((c) => (
            <button
              type="button"
              className="clube-opcao clube-oferta"
              key={c.id}
              title={porque([[ocupado, AGUARDE]])}
              disabled={ocupado}
              onClick={() => aoEscolher(c.id)}
            >
              <span className="clube-oferta-nome">
                {c.nome}
                <span className="serie">SERIE {c.divisao}</span>
              </span>
              {c.reputacao !== undefined && (
                <span className="tag-fraco clube-oferta-info">
                  reputacao {c.reputacao} · caixa {c.caixa} · {c.elenco} jogadores
                </span>
              )}
            </button>
          ))}
        </div>
        </div>
        <div className="modal-acoes">
          {confirmarFim ? (
            <>
              <span className="aviso">Encerrar a carreira de vez? O jogo termina aqui.</span>
              <button type="button" className="bt-fantasma" onClick={() => setConfirmarFim(false)}>
                Voltar
              </button>
              <button type="button" className="bt-fantasma bt-perigo" title={porque([[ocupado, AGUARDE]])}
              disabled={ocupado} onClick={aoEncerrar}>
                Encerrar carreira
              </button>
            </>
          ) : (
            <button type="button" className="bt-fantasma bt-perigo" onClick={() => setConfirmarFim(true)}>
              Encerrar a carreira
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
