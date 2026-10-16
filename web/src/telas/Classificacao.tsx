// As quatro series e os estaduais do ano, no mesmo seletor.
//
// A tabela completa mora aqui; o Painel mostra so a minha vizinhanca, que e o
// que importa de relance. Aqui e o lugar de olhar o torneio inteiro.

import { Escudo } from '../componentes/Escudo'
import { agrupar } from '../formato'
import { CabecalhoTela } from '../componentes/CabecalhoTela'
import { Grade, type Coluna } from '../componentes/Grade'
import { LegendaZonas, MarcaZona } from '../componentes/Zona'
import type { LinhaClassificacao, TelaTabela } from '../tipos'

interface Props {
  tela: TelaTabela
  aoTrocarTorneio: (alvo: string) => void
  ocupado: boolean
}

const COLUNAS: Coluna<LinhaClassificacao>[] = [
  { chave: 'pos', rotulo: 'Pos', largura: '40px', classe: 'num', render: (l) => <span className={`pos-selo${l.zona ? ` ${l.zona}` : ''}`}>{l.pos}</span> },
  {
    chave: 'clube',
    rotulo: 'Clube',
    largura: 'minmax(150px, 2fr)',
    classe: 'corta',
    render: (l) => (
      <span className="linha-flex">
        <MarcaZona zona={l.zona} texto={l.zona_texto} />
        <Escudo nome={l.clube} tamanho={16} />
        {l.clube}
      </span>
    ),
  },
  { chave: 'p', rotulo: 'Pts', largura: '42px', classe: 'num', render: (l) => <strong className="pts">{l.p}</strong> },
  { chave: 'j', rotulo: 'J', largura: '38px', classe: 'num', render: (l) => l.j },
  { chave: 'v', secundaria: true, rotulo: 'V', largura: '38px', classe: 'num', render: (l) => l.v },
  { chave: 'e', secundaria: true, rotulo: 'E', largura: '38px', classe: 'num', render: (l) => l.e },
  { chave: 'd', secundaria: true, rotulo: 'D', largura: '38px', classe: 'num', render: (l) => l.d },
  { chave: 'gp', secundaria: true, rotulo: 'GP', largura: '42px', classe: 'num', render: (l) => l.gp },
  { chave: 'gc', secundaria: true, rotulo: 'GC', largura: '42px', classe: 'num', render: (l) => l.gc },
  {
    chave: 'sg',
    rotulo: 'SG',
    largura: '46px',
    classe: 'num',
    render: (l) => <span className={l.sg > 0 ? 'sg-pos' : l.sg < 0 ? 'sg-neg' : ''}>{l.sg > 0 ? `+${l.sg}` : l.sg}</span>,
  },
  {
    chave: 'ap',
    secundaria: true,
    rotulo: 'Ap%',
    largura: '58px',
    classe: 'num',
    render: (l) => <span className="ap-pct">{l.j > 0 ? Math.round((100 * l.p) / (3 * l.j)) : 0}%</span>,
  },
]

export function Classificacao({ tela, aoTrocarTorneio, ocupado }: Props) {
  return (
    <div className="tela">
      <CabecalhoTela titulo={tela.titulo} sub={tela.subtitulo}>
        <div className="linha-flex larga mt-3">
          <label htmlFor="torneio" className="painel-titulo">Torneio</label>
          <select
            id="torneio"
            className="seletor"
            value={tela.alvo}
            disabled={ocupado}
            onChange={(e) => aoTrocarTorneio(e.target.value)}
          >
            {agrupar(tela.torneios).map(([grupo, itens]) => (
              <optgroup key={grupo} label={grupo}>
                {itens.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.nome}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
          {tela.legenda && <span className="sub txt-fraco">{tela.legenda}</span>}
        </div>
      </CabecalhoTela>

      {tela.grupos ? (
        // estadual com grupos: uma tabela por grupo, verde = vai ao mata-mata
        <div className="competicao-tabelas">
          {tela.grupos.map((g) => (
            <section className="painel corte" key={g.nome}>
              <div className="painel-titulo cab-tabela">{g.nome}</div>
              <Grade
                colunas={COLUNAS}
                itens={g.linhas}
                idDe={(l) => l.pos}
                classeDe={(l) => `${l.zona}${l.eu ? ' eu' : ''}`}
              />
              <LegendaZonas linhas={g.linhas} />
            </section>
          ))}
        </div>
      ) : (
        <section className="painel corte">
          <Grade
            colunas={COLUNAS}
            itens={tela.linhas}
            idDe={(l) => l.pos}
            classeDe={(l) => `${l.zona}${l.eu ? ' eu' : ''}`}
            vazio={tela.vazio ?? 'Este torneio ainda nao comecou.'}
          />
          <LegendaZonas linhas={tela.linhas} />
        </section>
      )}
    </div>
  )
}
