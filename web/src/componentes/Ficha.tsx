// A ficha do jogador.
//
// No tkinter era um bloco de texto de terminal com barras feitas de
// caractere. Aqui os mesmos julgamentos do motor vem em campos, entao a barra
// e barra de verdade e o numero fica legivel de relance.

import type { FichaJogador } from '../tipos'

interface Props {
  ficha: FichaJogador
  aoFechar: () => void
  /** Acoes que fazem sentido de onde a ficha foi aberta (ex.: Negociar, no
   *  Mercado). Sem isso o jogador fecha a ficha e tem que achar a linha de novo. */
  acoes?: { rotulo: string; principal?: boolean; aoClicar: () => void }[]
}

function estadoDaBarra(valor: number) {
  if (valor >= 65) return 'ok'
  if (valor >= 45) return 'atencao'
  return 'critico'
}

export function Ficha({ ficha, aoFechar, acoes }: Props) {
  return (
    <div
      className="fundo-modal"
      role="dialog"
      aria-modal="true"
      aria-label={`Ficha de ${ficha.nome}`}
      onClick={aoFechar}
    >
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="ficha-topo">
          <div className="ficha-ovr">{ficha.ovr}</div>
          <div className="encolhe">
            <h2>{ficha.nome}</h2>
            <div className="sub txt-fraco txt-p">
              {ficha.posicao_nome}, {ficha.idade} anos · {ficha.clube} · joga {ficha.papel}
            </div>
            {ficha.situacao && (
              <div className="txt-atencao txt-p mt-1">
                {ficha.situacao}
              </div>
            )}
          </div>
        </div>

        <div className="painel-titulo mb-2">Leitura do olheiro</div>
        <div className="txt-m mb-3">{ficha.olheiro}</div>

        <ul className="ficha-notas">
          {ficha.notas.map((n, i) => (
            <li key={i}>{n}</li>
          ))}
        </ul>

        <div className="ficha-barras">
          {ficha.barras.map((b) => (
            <div className="ficha-barra" key={b.nome}>
              <div className="topo">
                <span>{b.nome}</span>
                <strong>{b.valor}</strong>
              </div>
              <div className="barra">
                <div className={estadoDaBarra(b.valor)} style={{ width: `${b.valor}%` }} />
              </div>
            </div>
          ))}
        </div>

        <div className="painel-titulo mt-1 mb-2">Temporada</div>
        <div className="ficha-numeros">
          <div className="cx"><div className="n">{ficha.temporada.j}</div><div className="r">jogos</div></div>
          <div className="cx"><div className="n">{ficha.temporada.g}</div><div className="r">gols</div></div>
          <div className="cx"><div className="n">{ficha.temporada.a}</div><div className="r">assist.</div></div>
          <div className="cx"><div className="n">{ficha.temporada.ca}</div><div className="r">amarelos</div></div>
          <div className="cx"><div className="n">{ficha.temporada.cv}</div><div className="r">vermelhos</div></div>
        </div>

        <div className="painel-titulo mt-3 mb-2">Carreira e contrato</div>
        <div className="ficha-numeros">
          <div className="cx"><div className="n">{ficha.carreira.j}</div><div className="r">jogos</div></div>
          <div className="cx"><div className="n">{ficha.carreira.g}</div><div className="r">gols</div></div>
          <div className="cx"><div className="n">{ficha.contrato.anos}</div><div className="r">anos de contrato</div></div>
          <div className="cx"><div className="n menor">{ficha.contrato.salario}</div><div className="r">salario/mes</div></div>
          <div className="cx"><div className="n menor">{ficha.contrato.valor}</div><div className="r">valor</div></div>
        </div>

        {ficha.contrato.emprestado_aqui && (
          <p className="mt-3 mb-0 txt-atencao txt-p">
            Esta emprestado aqui: pagamos {ficha.contrato.emp_pct}% do salario e o passe nao e nosso.
          </p>
        )}

        <div className="modal-acoes mt-4">
          {acoes?.map((a) => (
            <button
              key={a.rotulo}
              type="button"
              className={a.principal ? 'bt-acao' : 'bt-fantasma'}
              onClick={a.aoClicar}
            >
              {a.rotulo}
            </button>
          ))}
          <button type="button" className={acoes?.length ? 'bt-fantasma' : 'bt-acao'} onClick={aoFechar}>
            Fechar
          </button>
        </div>
      </div>
    </div>
  )
}
