// A sala de trofeus: quem e o treinador, o que ganhou e por onde passou.
//
// Tudo vem de G["carreira"], que o motor so acrescenta: cada clube dirigido e
// uma passagem com jogos, titulos e marcos, e nada sai quando o treinador vai
// embora. Daqui tambem se pede demissao - uma acao que troca de clube, entao
// ela pede um segundo clique antes de valer.

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

      <section className="painel carreira-tecnico">
        <div>
          <div className="carreira-nome">{tecnico.nome}</div>
          <div className="tag-fraco">
            {tecnico.rotulo} · {modificadores.join(' · ')}
          </div>
        </div>
        <div className="carreira-rep" aria-label={`Reputacao ${tecnico.reputacao} de 99`}>
          <span className="valor">{tecnico.reputacao}</span>
          <span className="tag-fraco">reputacao</span>
          <progress max={99} value={tecnico.reputacao} />
        </div>
      </section>

      {tela.propostas.length > 0 && (
        <section className="painel" style={{ padding: '14px 18px' }}>
          <div className="painel-titulo" style={{ marginBottom: 8 }}>
            Propostas de emprego
          </div>
          {tela.propostas.map((o) => (
            <LinhaProposta key={o.id} proposta={o} ocupado={ocupado} aoResponder={aoResponderProposta} />
          ))}
        </section>
      )}

      <section className="painel" style={{ padding: '14px 18px' }}>
        <div className="painel-titulo" style={{ marginBottom: 10 }}>
          Sala de trofeus
        </div>
        {trofeus.length === 0 ? (
          <div className="vazio" style={{ padding: 0 }}>
            Nenhuma taca ainda. Estadual, Copa, Serie, continental: tudo que voce ganhar fica aqui para sempre.
          </div>
        ) : (
          <ul className="trofeus">
            {trofeus.map((t) => (
              <li key={t.nome} className="trofeu">
                <span className="trofeu-qtd">{t.qtd}x</span>
                <span className="trofeu-nome">{t.nome}</span>
                <span className="tag-fraco">{t.anos.join(', ')}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="painel" style={{ padding: '14px 18px' }}>
        <div className="painel-titulo" style={{ marginBottom: 10 }}>
          Clubes dirigidos
        </div>
        {passagens.map((p, i) => (
          <Passagem key={i} p={p} />
        ))}
      </section>

      <SairDoClube pode={tela.pode_pedir_demissao} ocupado={ocupado} clube={passagens[0]?.clube} aoSair={aoPedirDemissao} />
    </div>
  )
}

function Passagem({ p }: { p: PassagemCarreira }) {
  return (
    <div className={`passagem${p.atual ? ' atual' : ''}`}>
      <div className="passagem-cab">
        <strong>{p.clube}</strong>
        <span className="tag-fraco">
          {p.liga} · {p.periodo}
          {p.saida && ` · saiu: ${p.saida}`}
        </span>
      </div>
      <div className="passagem-numeros">
        {p.j} jogos · {p.v}V {p.e}E {p.d}D · {p.gp} gols pro, {p.gc} contra
        {p.aproveitamento !== null && ` · ${p.aproveitamento}% de aproveitamento`}
      </div>
      {p.titulos.length > 0 && <div className="passagem-titulos">{p.titulos.join(' · ')}</div>}
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
    </div>
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
            <button type="button" className="bt-acao" disabled={ocupado} onClick={() => aoResponder(proposta.id, true)}>
              Confirmar troca
            </button>
          </>
        ) : (
          <>
            <button type="button" className="bt-fantasma" disabled={ocupado} onClick={() => aoResponder(proposta.id, false)}>
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
    <section className="painel faixa critico" style={{ marginTop: 4 }}>
      <div style={{ minWidth: 0 }}>
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
          <button type="button" className="bt-acao" disabled={ocupado || !pode} onClick={aoSair}>
            Confirmar demissao
          </button>
        </>
      ) : (
        <button type="button" className="bt-fantasma" disabled={!pode} onClick={() => setCerteza(true)}>
          Pedir demissao
        </button>
      )}
    </section>
  )
}
