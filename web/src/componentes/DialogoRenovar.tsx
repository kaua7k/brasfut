// Renovar varios de uma vez: um prazo para todos e cada um pelo que pede.
//
// Antes, marcar dez jogadores abria dez mesas de negociacao seguidas. A mesa
// continua existindo para quem quer pechinchar um nome (um jogador marcado
// abre a mesa); aqui o jogo mostra o pedido de cada um no prazo escolhido e o
// peso na folha, e um clique fecha todos. Pagar o que o jogador pede e sempre
// aceito. O prazo mais longo sai um pouco mais barato por mes.

import { porque, AGUARDE } from '../motivo'
import { useEffect, useState } from 'react'
import { api, ErroDaApi } from '../api'
import { plural } from '../formato'
import type { PreviaRenovacao } from '../tipos'

interface Props {
  ids: number[]
  ocupado: boolean
  aoConfirmar: (anos: number) => void
  aoFechar: () => void
}

const PRAZOS = [1, 2, 3, 4, 5]

export function DialogoRenovar({ ids, ocupado, aoConfirmar, aoFechar }: Props) {
  const [anos, setAnos] = useState(5)
  const [previa, setPrevia] = useState<PreviaRenovacao | null>(null)
  const [erro, setErro] = useState<string | null>(null)

  useEffect(() => {
    api
      .linhasRenovacao(ids, anos)
      .then(setPrevia)
      .catch((e) => setErro(e instanceof ErroDaApi ? e.message : String(e)))
  }, [ids, anos])

  const validos = previa ? previa.linhas.filter((l) => !l.motivo) : []

  return (
    <div
      className="fundo-modal"
      role="dialog"
      aria-modal="true"
      aria-label="Renovar contratos"
      onKeyDown={(e) => e.key === 'Escape' && aoFechar()}
    >
      <div className="modal modal-largo">
        <h2>Renovar contratos</h2>
        <p className="tag-fraco m-0">
          Cada um renova pelo salario que pede, todos no mesmo prazo. Para negociar um jogador so, marque apenas ele.
        </p>

        <fieldset className="simular-bloco">
          <legend className="painel-titulo">Prazo para todos</legend>
          <div className="alavanca" role="radiogroup" aria-label="Prazo do contrato">
            {PRAZOS.map((n) => (
              <button
                key={n}
                type="button"
                role="radio"
                aria-checked={anos === n}
                className={anos === n ? 'ativo' : ''}
                onClick={() => setAnos(n)}
              >
                {plural(n, 'ano')}
              </button>
            ))}
          </div>
        </fieldset>

        {previa && (
          <div className="renovar-linhas mt-3" role="table" aria-label="Pedido de cada jogador">
            <div className="renovar-linha cab" role="row">
              <span role="columnheader">Jogador</span>
              <span role="columnheader" className="num">Ganha hoje</span>
              <span role="columnheader" className="num">Pede</span>
              <span role="columnheader" className="num">Diferenca</span>
            </div>
            {previa.linhas.map((l) => (
              <div className={`renovar-linha${l.motivo ? ' fora' : ''}`} role="row" key={l.id}>
                <span role="cell" className="corta">
                  <span className={`tag-${l.tag}`}>{l.nome}</span>{' '}
                  <span className="tag-fraco">
                    {l.pos} · {l.ovr} · {l.idade} anos · {l.contrato <= 0 ? 'contrato vencido' : `${plural(l.contrato, 'ano')} de contrato`}
                  </span>
                  {l.motivo && <span className="txt-critico"> · {l.motivo}</span>}
                </span>
                <span role="cell" className="num tag-fraco">{l.salario}</span>
                <span role="cell" className="num negrito">{l.pede}</span>
                <span role="cell" className={`num ${l.diferenca.startsWith('+') ? 'txt-atencao' : 'txt-ok'}`}>
                  {l.diferenca}
                </span>
              </div>
            ))}
          </div>
        )}

        {previa && (
          <div className="mesa-linha tag-fraco mt-3">
            Folha por mes: {previa.folha_mes} → <strong className="txt-normal">{previa.folha_mes_depois}</strong> (
            {previa.diferenca_mes})
          </div>
        )}
        {erro && <div className="mesa-linha linha-critica">{erro}</div>}

        <div className="modal-acoes">
          <button type="button" className="bt-fantasma" onClick={aoFechar}>
            Cancelar
          </button>
          <button
            type="button"
            className="bt-acao bt-media"
            title={porque([[ocupado, AGUARDE], [!validos.length, 'Ninguem desta lista pode renovar com voce']])}
            disabled={ocupado || !validos.length}
            onClick={() => aoConfirmar(anos)}
          >
            Renovar {validos.length > 1 ? `os ${validos.length}` : ''} por {plural(anos, 'ano')}
          </button>
        </div>
      </div>
    </div>
  )
}
