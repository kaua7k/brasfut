// Antes do Painel existir, alguem precisa dizer de onde o jogo comeca.
//
// A janela tkinter faz isso com dois messagebox e um dialogo. Aqui sao dois
// estados de tela: continuar o save que existe, ou criar mundo e escolher
// clube. Sem isso o navegador so conseguiria abrir uma carreira ja comecada.

import { useState } from 'react'
import { Estrela } from '../icones'
import type { ClubeOpcao, SituacaoJogo } from '../tipos'

interface Props {
  situacao: SituacaoJogo
  clubes: ClubeOpcao[]
  erro: string | null
  ocupado: boolean
  aoAbrir: () => void
  aoCriar: () => void
  aoEscolher: (id: number) => void
}

export function Abertura({ situacao, clubes, erro, ocupado, aoAbrir, aoCriar, aoEscolher }: Props) {
  const [serie, setSerie] = useState('A')

  if (situacao === 'escolher_clube') {
    const daSerie = clubes.filter((c) => c.divisao === serie)
    return (
      <div className="centro-tela">
        <div className="modal" style={{ maxWidth: 680 }}>
          <h2>Escolha o clube que voce vai treinar</h2>
          <p>O mundo foi criado. A carreira so e salva depois desta escolha.</p>
          <div className="alavanca" style={{ marginBottom: 14 }}>
            {['A', 'B'].map((s) => (
              <button
                key={s}
                type="button"
                className={serie === s ? 'ativo' : ''}
                onClick={() => setSerie(s)}
              >
                Serie {s}
              </button>
            ))}
          </div>
          <div className="lista-clubes">
            {daSerie.map((c) => (
              <button
                type="button"
                className="clube-opcao"
                key={c.id}
                disabled={ocupado}
                onClick={() => aoEscolher(c.id)}
              >
                {c.nome}
                <span className="serie">REP {c.reputacao}</span>
              </button>
            ))}
          </div>
          {erro && <p className="erro">{erro}</p>}
        </div>
      </div>
    )
  }

  const temSave = situacao === 'tem_save'
  return (
    <div className="centro-tela">
      <div className="cartao-centro">
        <div className="escudo gg" style={{ margin: '0 auto 18px' }}>
          <Estrela tamanho={26} />
        </div>
        <h1>BRASFUT</h1>
        <p>
          {temSave
            ? 'Existe um jogo salvo nesta pasta. Continue de onde parou, ou comece uma carreira nova por cima dele.'
            : 'Nenhum jogo salvo por aqui. Vamos criar um mundo novo e escolher o seu clube.'}
        </p>
        <div className="modal-acoes">
          {temSave && (
            <button type="button" className="bt-acao" disabled={ocupado} onClick={aoAbrir}>
              {ocupado ? 'Abrindo…' : 'Continuar carreira'}
            </button>
          )}
          <button
            type="button"
            className={temSave ? 'bt-fantasma' : 'bt-acao'}
            disabled={ocupado}
            onClick={aoCriar}
          >
            {ocupado && !temSave ? 'Criando mundo…' : 'Carreira nova'}
          </button>
        </div>
        {erro && <p className="erro" style={{ marginTop: 16 }}>{erro}</p>}
      </div>
    </div>
  )
}
