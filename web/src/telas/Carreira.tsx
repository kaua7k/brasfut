// A sala de trofeus: quem e o treinador, o que ganhou e por onde passou.
//
// Tudo vem de G["carreira"], que o motor so acrescenta: cada clube dirigido e
// uma passagem com jogos, titulos e marcos, e nada sai quando o treinador vai
// embora. Daqui tambem se pede demissao - uma acao que troca de clube, entao
// ela pede um segundo clique antes de valer.

import { porque, AGUARDE } from '../motivo'
import { useState } from 'react'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import type { PassagemCarreira, PropostaEmprego, TelaCarreira } from '../tipos'

interface Props {
  tela: TelaCarreira
  ocupado: boolean
  aoPedirDemissao: () => void
  aoResponderProposta: (id: number, aceitar: boolean) => void
}

export function Carreira({ tela, ocupado, aoPedirDemissao, aoResponderProposta }: Props) {
  const { tecnico, totais, trofeus, passagens, opcoes } = tela
  const aprov = totais.j ? Math.round((100 * (3 * totais.v + totais.e)) / (3 * totais.j)) : null
  const modificadores = [
    `Dificuldade ${opcoes.dificuldade}`,
    opcoes.sem_demissao && 'sem demissao',
    opcoes.investidor && 'com investidor',
  ].filter(Boolean)

  return (
    <div className="tela">
      <CabecalhoTela
        titulo={tela.titulo}
        sub={tela.subtitulo}
        metricas={[
          { nome: 'titulos', valor: String(totais.titulos), estado: totais.titulos ? 'ok' : null },
          { nome: 'temporadas', valor: String(totais.temporadas) },
          { nome: 'clubes', valor: String(totais.clubes) },
          { nome: 'jogos', valor: String(totais.j) },
          { nome: 'aproveitamento', valor: aprov === null ? '-' : `${aprov}%` },
        ]}
      />

      <section className="painel carreira-heroi">
        <div className="carreira-avatar" aria-hidden="true">
          {tecnico.nome.slice(0, 2).toUpperCase()}
        </div>
        <div className="encolhe">
          <div className="carreira-nome">{tecnico.nome}</div>
          <div className="carreira-rotulo">{tecnico.rotulo}</div>
          <div className="carreira-chips">
            {modificadores.map((m) => (
              <span key={String(m)} className="carreira-chip">
                {m}
              </span>
            ))}
          </div>
        </div>
        <div className="carreira-rep" aria-label={`Reputacao ${tecnico.reputacao} de 99`}>
          <div className="carreira-rep-topo">
            <span className="valor">{tecnico.reputacao}</span>
            <span className="tag-fraco">reputacao</span>
          </div>
          <div className="carreira-rep-barra">
            <span style={{ width: `${Math.min(100, (100 * tecnico.reputacao) / 99)}%` }} />
            {[40, 55, 70, 85].map((f) => (
              <i key={f} style={{ left: `${(100 * f) / 99}%` }} />
            ))}
          </div>
          <div className="tag-fraco carreira-rep-prox">
            {tecnico.proxima
              ? `faltam ${tecnico.proxima.falta} para "${tecnico.proxima.rotulo}"`
              : 'no topo da escada'}
          </div>
        </div>
      </section>

      {tela.propostas.length > 0 && (
        <section className="painel enxuto carreira-propostas">
          <div className="painel-titulo mb-2">Propostas de emprego</div>
          {tela.propostas.map((o) => (
            <LinhaProposta key={o.id} proposta={o} ocupado={ocupado} aoResponder={aoResponderProposta} />
          ))}
        </section>
      )}

      <section className="painel enxuto">
        <div className="painel-titulo mb-3">Sala de trofeus</div>
        {trofeus.length === 0 ? (
          <div className="vazio justo">
            Nenhuma taca ainda. Estadual, Copa, Serie, continental: tudo que voce ganhar fica aqui para sempre.
          </div>
        ) : (
          <ul className="clube-sala">
            {trofeus.map((t) => (
              <li key={t.nome}>
                <span className="qtd">{t.qtd}</span>
                <div>
                  <div className="nome">{t.nome}</div>
                  <div className="anos">{t.anos.join(', ')}</div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="painel enxuto">
        <div className="painel-titulo mb-3">Clubes dirigidos</div>
        <ol className="carreira-linha">
          {passagens.map((p, i) => (
            <Passagem key={i} p={p} />
          ))}
        </ol>
      </section>

      <SairDoClube pode={tela.pode_pedir_demissao} ocupado={ocupado} clube={passagens[0]?.clube} aoSair={aoPedirDemissao} />
    </div>
  )
}

function Passagem({ p }: { p: PassagemCarreira }) {
  const saidaRuim = p.saida === 'demitido'
  return (
    <li className={`carreira-passagem${p.atual ? ' atual' : ''}`}>
      <div className="carreira-passagem-cab">
        <strong>{p.clube}</strong>
        <span className="carreira-chip">{p.liga}</span>
        <span className="tag-fraco">{p.periodo}</span>
        {p.atual && <span className="carreira-chip atual">atual</span>}
        {p.saida && <span className={`carreira-chip ${saidaRuim ? 'ruim' : ''}`}>{p.saida}</span>}
      </div>
      <div className="carreira-numeros">
        <div>
          <b>{p.j}</b>
          <span>jogos</span>
        </div>
        <div>
          <b>
            <span className="tag-ok">{p.v}</span>-{p.e}-<span className="tag-critico">{p.d}</span>
          </b>
          <span>V-E-D</span>
        </div>
        <div>
          <b>
            {p.gp}:{p.gc}
          </b>
          <span>gols</span>
        </div>
        <div className="carreira-aprov">
          <b>{p.aproveitamento === null ? '-' : `${p.aproveitamento}%`}</b>
          <span>aproveitamento</span>
          <span className="carreira-aprov-barra" aria-hidden="true">
            <span style={{ width: `${p.aproveitamento ?? 0}%` }} />
          </span>
        </div>
      </div>
      {p.titulos.length > 0 && (
        <div className="carreira-selos">
          {p.titulos.map((t) => (
            <span key={t} className="carreira-selo">
              ★ {t}
            </span>
          ))}
        </div>
      )}
      {p.marcos.length > 0 && (
        <ul className="passagem-marcos">
          {p.marcos.map((m, i) => (
            <li key={i}>{m}</li>
          ))}
        </ul>
      )}
      {p.parcial && (
        <div className="tag-fraco">O registro desta passagem comeca na versao 2.5: o que veio antes nao foi guardado.</div>
      )}
    </li>
  )
}

function LinhaProposta({
  proposta,
  ocupado,
  aoResponder,
}: {
  proposta: PropostaEmprego
  ocupado: boolean
  aoResponder: (id: number, aceitar: boolean) => void
}) {
  const [certeza, setCerteza] = useState(false)
  return (
    <div className="linha-proposta">
      <span>
        <strong>{proposta.clube}</strong>{' '}
        <span className="tag-fraco">
          {proposta.liga}, REP {proposta.reputacao} ·{' '}
          {proposta.semanas > 1 ? `vale por mais ${proposta.semanas} semanas` : 'vence ao avancar esta semana'}
        </span>
      </span>
      <span className="modal-acoes">
        {certeza ? (
          <>
            <button type="button" className="bt-fantasma" onClick={() => setCerteza(false)}>
              Cancelar
            </button>
            <button type="button" className="bt-acao" title={porque([[ocupado, AGUARDE]])}
            disabled={ocupado} onClick={() => aoResponder(proposta.id, true)}>
              Confirmar troca
            </button>
          </>
        ) : (
          <>
            <button type="button" className="bt-fantasma" title={porque([[ocupado, AGUARDE]])}
            disabled={ocupado} onClick={() => aoResponder(proposta.id, false)}>
              Recusar
            </button>
            <button type="button" className="bt-fantasma" onClick={() => setCerteza(true)}>
              Aceitar
            </button>
          </>
        )}
      </span>
    </div>
  )
}

function SairDoClube({
  pode,
  ocupado,
  clube,
  aoSair,
}: {
  pode: boolean
  ocupado: boolean
  clube?: string
  aoSair: () => void
}) {
  const [certeza, setCerteza] = useState(false)
  return (
    <section className="painel faixa critico mt-1">
      <div className="encolhe">
        <div className="faixa-titulo">Pedir demissao</div>
        <div className="faixa-detalhe">
          {certeza
            ? `Voce deixa o ${clube ?? 'clube'} agora e escolhe entre os clubes que querem o seu trabalho. Nao da para voltar atras.`
            : 'Sair por vontade propria, a qualquer momento. Quem oferece emprego depende da sua reputacao.'}
        </div>
      </div>
      <div className="espaco" />
      {certeza ? (
        <>
          <button type="button" className="bt-fantasma" onClick={() => setCerteza(false)}>
            Ficar
          </button>
          <button type="button" className="bt-acao" title={porque([[ocupado, AGUARDE], [!pode, 'Nao da para pedir demissao agora']])}
          disabled={ocupado || !pode} onClick={aoSair}>
            Confirmar demissao
          </button>
        </>
      ) : (
        <button type="button" className="bt-fantasma" title={porque([[!pode, 'Nao da para pedir demissao agora']])}
        disabled={!pode} onClick={() => setCerteza(true)}>
          Pedir demissao
        </button>
      )}
    </section>
  )
}
