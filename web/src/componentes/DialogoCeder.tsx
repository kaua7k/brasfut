// Ceder por emprestimo: toda proposta dos marcados numa tabela so.
//
// Uma linha por par jogador/clube. Ja abre com a melhor de cada um marcada (a
// que assume a maior fatia do salario), e marcar outra do mesmo jogador troca
// a escolha - um jogador nao vai para dois clubes. A confirmacao com a conta
// vem do servidor, como em toda acao que mexe no elenco.

import { porque, AGUARDE } from '../motivo'
import { useEffect, useState } from 'react'
import { api, ErroDaApi } from '../api'
import { dinheiro as reais, plural } from '../formato'
import type { LinhaCessao } from '../tipos'
import { Grade, type Coluna } from './Grade'

interface Props {
  ids: number[]
  ocupado: boolean
  aoConfirmar: (itens: { id: number; clube_id: number }[]) => void
  aoFechar: () => void
}

const COLUNAS: Coluna<LinhaCessao>[] = [
  {
    chave: 'nome',
    rotulo: 'Jogador',
    largura: 'minmax(120px, 1.2fr)',
    classe: 'corta',
    render: (l) => <span className={`tag-${l.tag}`}>{l.nome}</span>,
  },
  { chave: 'ovr', rotulo: 'Ovr', largura: '40px', classe: 'num', render: (l) => l.ovr },
  { chave: 'clube', rotulo: 'Interessado', largura: 'minmax(110px, 1fr)', classe: 'corta', render: (l) => l.clube },
  { chave: 'div', rotulo: 'Serie', largura: '48px', classe: 'centro', render: (l) => l.divisao },
  { chave: 'rep', rotulo: 'Rep', largura: '40px', classe: 'num', render: (l) => l.reputacao },
  { chave: 'pct', rotulo: 'Assume', largura: '64px', classe: 'centro', render: (l) => `${l.pct}%` },
  { chave: 'sobra', rotulo: 'Sobra pra voce', largura: '104px', classe: 'num', render: (l) => l.sobra },
]

export function DialogoCeder({ ids, ocupado, aoConfirmar, aoFechar }: Props) {
  const [linhas, setLinhas] = useState<LinhaCessao[] | null>(null)
  // a escolha e por jogador: id -> indice da linha escolhida
  const [escolha, setEscolha] = useState<Record<number, number>>({})
  const [erro, setErro] = useState<string | null>(null)

  useEffect(() => {
    api
      .ofertasCessao(ids)
      .then((r) => {
        setLinhas(r.linhas)
        const melhor: Record<number, number> = {}
        r.linhas.forEach((l, i) => {
          const atual = melhor[l.id]
          if (atual === undefined || l.pct > r.linhas[atual].pct) melhor[l.id] = i
        })
        setEscolha(melhor)
      })
      .catch((e) => setErro(e instanceof ErroDaApi ? e.message : String(e)))
  }, [ids])

  const indices = new Set(Object.values(escolha))
  const escolhidas = (linhas ?? []).filter((_, i) => indices.has(i))
  const alivio = escolhidas.reduce((s, l) => s + l.alivio_num, 0)

  const alternar = (i: number) => {
    if (!linhas) return
    const l = linhas[i]
    setEscolha((e) => {
      const nova = { ...e }
      if (nova[l.id] === i) delete nova[l.id]
      else nova[l.id] = i
      return nova
    })
  }

  return (
    <div
      className="fundo-modal"
      role="dialog"
      aria-modal="true"
      aria-label="Ceder por emprestimo"
      onKeyDown={(e) => e.key === 'Escape' && aoFechar()}
    >
      <div className="modal modal-largo">
        <h2>Ceder por emprestimo</h2>
        <p>
          Ele volta no fim da temporada, joga o ano inteiro e costuma voltar melhor. Quem recebe assume a
          fatia do salario da coluna Assume.
        </p>
        {linhas === null && !erro && <p>procurando interessados…</p>}
        {linhas !== null && linhas.length === 0 && (
          <p className="tag-atencao">
            Nenhum clube demonstrou interesse nesses jogadores. Clubes so pegam emprestado quem cabe no
            elenco deles e de reputacao parecida com a sua.
          </p>
        )}
        {linhas !== null && linhas.length > 0 && (
          <section className="painel" style={{ overflow: 'hidden' }}>
            <Grade
              colunas={COLUNAS}
              itens={linhas.map((l, i) => ({ ...l, indice: i }))}
              idDe={(l) => (l as LinhaCessao & { indice: number }).indice}
              nomeDe={(l) => `${l.nome} para o ${l.clube}`}
              marcados={indices}
              aoMarcar={alternar}
            />
          </section>
        )}
        <div className="mesa-linha tag-fraco" style={{ marginTop: 10 }}>
          {plural(escolhidas.length, 'jogador', 'jogadores')} {escolhidas.length === 1 ? 'sairia' : 'sairiam'}, aliviando {reais(alivio)} por mes na folha · marcar
          outra linha do mesmo jogador troca o clube escolhido
        </div>
        {erro && <div className="mesa-linha linha-critica">{erro}</div>}
        <div className="modal-acoes">
          <button type="button" className="bt-fantasma" onClick={aoFechar}>
            Fechar
          </button>
          <button
            type="button"
            className="bt-acao bt-media"
            title={porque([[ocupado, AGUARDE], [escolhidas.length === 0, 'Marque pelo menos uma oferta']])}
            disabled={ocupado || escolhidas.length === 0}
            onClick={() => aoConfirmar(escolhidas.map((l) => ({ id: l.id, clube_id: l.clube_id })))}
          >
            Ceder marcados
          </button>
        </div>
      </div>
    </div>
  )
}
