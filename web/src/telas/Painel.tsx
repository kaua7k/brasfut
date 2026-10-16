// O Painel responde uma pergunta so: posso avancar a semana agora?
//
// Tudo se ordena por isso. O veredito vem primeiro, a prova (o XI que entra em
// campo) e o maior bloco da tela, e o resto e contexto da aposta e memoria.
// E a mesma hierarquia da janela tkinter, redesenhada.

import { porque, AGUARDE } from '../motivo'
import { useState } from 'react'
import { Campo } from '../componentes/Campo'
import { ResumoPartida } from '../componentes/Partida'
import { plural } from '../formato'
import { LegendaZonas, MarcaZona } from '../componentes/Zona'
import { EscudoRival, iconeDeEstado } from '../icones'
import { Escudo } from '../componentes/Escudo'
import type {
  AvisoContratos,
  Confianca,
  DadosPainel,
  Destaque,
  Escalacao,
  Manchete,
  Noticia,
  Objetivo,
  Prontidao,
  PropostaEmprego,
  Proximo,
  Resultados,
  Tabela,
} from '../tipos'

interface Props {
  dados: DadosPainel
  aoDefinirAuto: (ligada: boolean) => void
  mudandoAuto: boolean
  aoIr: (destino: string) => void
  /** renova esses jogadores (varios: renovacao em lote; um: a mesa) */
  aoRenovar: (ids: number[]) => void
  aoResponderProposta: (id: number, aceitar: boolean) => void
}

export function Painel({ dados, aoDefinirAuto, mudandoAuto, aoIr, aoRenovar, aoResponderProposta }: Props) {
  // o botao da faixa leva a outra tela; se ela ainda nao migrou, ele avisa
  const prontas = new Set(dados.cabecalho.menu.filter((m) => m.pronta).map((m) => m.id))
  return (
    <div className="corpo">
      <div className="coluna">
        <FaixaProntidao prontidao={dados.prontidao} prontas={prontas} aoIr={aoIr} />
        {dados.contratos && <FaixaContratos aviso={dados.contratos} aoRenovar={aoRenovar} />}
        {dados.propostas_jogadores && (
          <section className="painel faixa ok">
            <div className="faixa-icone">{iconeDeEstado('ok')}</div>
            <div className="encolhe">
              <div className="faixa-titulo">{dados.propostas_jogadores.texto}</div>
              <div className="faixa-detalhe">
                {dados.propostas_jogadores.itens
                  .map((p) => `${p.jogador} (${p.pos}): ${p.clube} oferece ${p.valor}`)
                  .join(' · ')}
                {dados.propostas_jogadores.total > dados.propostas_jogadores.itens.length &&
                  ` · e mais ${dados.propostas_jogadores.total - dados.propostas_jogadores.itens.length}`}
              </div>
            </div>
            <div className="espaco" />
            <button type="button" className="bt-fantasma" onClick={() => aoIr('mercado:vitrine')}>
              Ver propostas
            </button>
          </section>
        )}
        {dados.propostas_emprego.map((o) => (
          <FaixaProposta key={o.id} proposta={o} aoResponder={aoResponderProposta} />
        ))}
        {dados.patrocinio_vago && (
          <section className="painel faixa atencao">
            <div className="faixa-icone">{iconeDeEstado('atencao')}</div>
            <div className="encolhe">
              <div className="faixa-titulo">Patrocinio a escolher: {dados.patrocinio_vago.join(' e ')}</div>
              <div className="faixa-detalhe">
                Tres propostas por espaco. Sem escolha, a equilibrada assina quando a bola rolar.
              </div>
            </div>
            <div className="espaco" />
            <button type="button" className="bt-fantasma" onClick={() => aoIr('financas')}>
              Ver propostas
            </button>
          </section>
        )}
        {dados.selecao && (
          <section className="painel faixa atencao">
            <div className="faixa-icone">{iconeDeEstado('atencao')}</div>
            <div className="encolhe">
              <div className="faixa-titulo">{dados.selecao.titulo}</div>
              <div className="faixa-detalhe">{dados.selecao.detalhe}</div>
            </div>
            <div className="espaco" />
            <button type="button" className="bt-fantasma" onClick={() => aoIr('escalacao')}>
              Ver escalacao
            </button>
          </section>
        )}
        {dados.resultados.partidas.length > 0 ? (
          <ResumoPartida partidas={dados.resultados.partidas} alerta={dados.resultados.alerta} />
        ) : (
          <FaixaResultados resultados={dados.resultados} />
        )}
        <CardProximo proximo={dados.proximo} meuClube={dados.cabecalho.clube} />
        <CardEscalacao
          escalacao={dados.escalacao}
          aoDefinirAuto={aoDefinirAuto}
          mudandoAuto={mudandoAuto}
        />
      </div>

      <div className="coluna">
        <CardObjetivo objetivo={dados.objetivo} />
        <CardTabela tabela={dados.tabela} />
        <CardDestaques destaques={dados.destaques} />
        <CardNoticias noticias={dados.noticias} />
        <CardMundo mundo={dados.mundo} aoIr={aoIr} />
      </div>
    </div>
  )
}

// ------------------------------------------------------------------- veredito
function FaixaProntidao({
  prontidao,
  prontas,
  aoIr,
}: {
  prontidao: Prontidao
  prontas: Set<string>
  aoIr: (destino: string) => void
}) {
  const acao = prontidao.acao
  // 'resumo' nao e tela do menu: abre a janela do resumo do ano
  const migrou = acao ? prontas.has(acao.destino) || acao.destino === 'resumo' : false
  return (
    <section className={`painel faixa ${prontidao.estado}`}>
      <div className="faixa-icone">{iconeDeEstado(prontidao.estado)}</div>
      <div className="encolhe">
        <div className="faixa-titulo">{prontidao.titulo}</div>
        <div className="faixa-detalhe">{prontidao.detalhe}</div>
      </div>
      <div className="espaco" />
      {acao && (
        <button
          type="button"
          className="bt-fantasma"
          disabled={!migrou}
          title={migrou ? undefined : `${acao.label}: essa tela ainda nao migrou`}
          onClick={() => aoIr(acao.destino)}
        >
          {acao.label}
        </button>
      )}
    </section>
  )
}

// ------------------------------------------------------ contratos acabando
function FaixaContratos({
  aviso,
  aoRenovar,
}: {
  aviso: AvisoContratos
  aoRenovar: (ids: number[]) => void
}) {
  const nomes = aviso.jogadores.map((j) => `${j.nome} (${j.pos}, ${j.ovr})`).join(', ')
  return (
    <section className={`painel faixa ${aviso.estado}`}>
      <div className="faixa-icone">{iconeDeEstado(aviso.estado)}</div>
      <div className="encolhe">
        <div className="faixa-titulo">{aviso.texto}</div>
        <div className="faixa-detalhe">
          {nomes}
          {aviso.extras > 0 && ` e mais ${aviso.extras}`}
        </div>
      </div>
      <div className="espaco" />
      <button type="button" className="bt-fantasma" onClick={() => aoRenovar(aviso.ids)}>
        Renovar {aviso.ids.length > 1 ? `os ${aviso.ids.length}` : ''}
      </button>
    </section>
  )
}

// ------------------------------------------------------ proposta de emprego
function FaixaProposta({
  proposta,
  aoResponder,
}: {
  proposta: PropostaEmprego
  aoResponder: (id: number, aceitar: boolean) => void
}) {
  // aceitar troca de clube na hora: pede um segundo clique, como no Mercado
  const [certeza, setCerteza] = useState(false)
  return (
    <section className="painel faixa atencao">
      <div className="faixa-icone">{iconeDeEstado('atencao')}</div>
      <div className="encolhe">
        <div className="faixa-titulo">
          O {proposta.clube} ({proposta.liga}, REP {proposta.reputacao}) quer voce como tecnico
        </div>
        <div className="faixa-detalhe">
          {certeza
            ? 'Aceitar deixa o clube atual agora, no meio da temporada. Confirma?'
            : proposta.semanas > 1
              ? `A proposta vale por mais ${proposta.semanas} semanas.`
              : 'A proposta vence ao avancar esta semana: responda antes.'}
        </div>
      </div>
      <div className="espaco" />
      {certeza ? (
        <>
          <button type="button" className="bt-fantasma" onClick={() => setCerteza(false)}>
            Cancelar
          </button>
          <button type="button" className="bt-acao" onClick={() => aoResponder(proposta.id, true)}>
            Confirmar
          </button>
        </>
      ) : (
        <>
          <button type="button" className="bt-fantasma" onClick={() => aoResponder(proposta.id, false)}>
            Recusar
          </button>
          <button type="button" className="bt-fantasma" onClick={() => setCerteza(true)}>
            Aceitar
          </button>
        </>
      )}
    </section>
  )
}

// ---------------------------------------------------- o placar e a memoria curta
function FaixaResultados({ resultados }: { resultados: Resultados }) {
  const { placares, forma, alerta } = resultados
  if (!placares.length && !forma.length && !alerta) return null
  return (
    <section className="painel">
      <div className="resultados">
        {placares.length > 0 ? (
          placares.map((p, i) => (
            <div className="placar" key={i}>
              <span className={`placar-numero ${p.estado}`}>
                {p.eu} x {p.ele}
              </span>
              <span>
                <span className="placar-adv">{p.adversario}</span>
                <br />
                <span className="placar-onde">{p.em_casa ? 'em casa' : 'fora'}</span>
              </span>
            </div>
          ))
        ) : (
          <span className="painel-titulo">sem jogo na ultima semana</span>
        )}

        <div className="espaco" />

        <div className="a-direita">
          {/* a contagem e a real (no comeco do ano sao menos de 5) e a seta diz
              o sentido: o mais antigo a esquerda, o ultimo jogo a direita */}
          <div className="painel-titulo mb-1">
            {forma.length === 1 ? 'Ultimo jogo' : `Ultimos ${forma.length || 5}`}
            {forma.length > 1 && <span className="tag-fraco"> · antigo → recente</span>}
          </div>
          <div className="forma" aria-label={forma.map((f) => f.descricao).join(', ')}>
            {forma.length === 0 && <span className="placar-onde">sem historico ainda</span>}
            {forma.map((f, i) => (
              <span className={`forma-badge ${f.letra}`} key={i} title={f.descricao}>
                {f.letra}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* o diagnostico so olha lesao, suspensao e improviso: um time saudavel
          perdendo todo domingo passaria como TIME PRONTO sem este aviso */}
      {alerta && (
        <div className={`alerta-fase ${alerta.estado}`}>
          {iconeDeEstado(alerta.estado, 16)}
          {alerta.texto}
        </div>
      )}
    </section>
  )
}

// --------------------------------------------------------------- proximo jogo
function CardProximo({ proximo, meuClube }: { proximo: Proximo; meuClube: string }) {
  const temAdversario = proximo.tipo === 'jogo'
  return (
    <section className="painel folgado">
      <div className="painel-cab mb-3">
        <span className="painel-titulo">Proximo jogo</span>
        <span className="txt-mini negrito txt-acao">
          {proximo.legenda}
        </span>
      </div>

      <div className="confronto">
        <div className="confronto-lado">
          <Escudo nome={meuClube} tamanho={50} />
          <div className="confronto-nome">{meuClube}</div>
        </div>

        <div className="confronto-vs">
          <div className="vs">{temAdversario ? 'VS' : '—'}</div>
          <div className="onde">
            {proximo.em_casa === null
              ? proximo.tipo === 'folga' ? 'semana livre' : 'a definir'
              : proximo.em_casa ? 'em casa' : 'fora de casa'}
          </div>
        </div>

        <div className="confronto-lado">
          {temAdversario ? (
            <Escudo nome={proximo.adversario} tamanho={50} />
          ) : (
            <div className="escudo gg">
              <EscudoRival tamanho={24} />
            </div>
          )}
          <div className={`confronto-nome${proximo.forte ? ' forte' : ''}`}>
            {proximo.adversario}
          </div>
        </div>
      </div>

      {proximo.estilo && (
        <div className="txt-mini mt-3 a-centro" title={proximo.estilo.desc}>
          Estilo dele: <strong>{proximo.estilo.nome}</strong>
          <span className="tag-fraco"> · {proximo.estilo.desc} · contra voce deve vir {proximo.estilo.tatica}</span>
        </div>
      )}

      {proximo.extras > 0 && (
        <div className="txt-mini txt-atencao mt-3 a-centro">
          +{plural(proximo.extras, 'jogo')} nesta semana
        </div>
      )}

      <div className="forcas">
        {/* a partida cruza ataque com defesa: e esse duelo que a barra mostra */}
        <Forca
          nome={proximo.ataque.dele === null ? 'Ataque' : 'Seu ataque x defesa dele'}
          meu={proximo.ataque.meu}
          dele={proximo.ataque.dele}
        />
        <Forca
          nome={proximo.defesa.dele === null ? 'Defesa' : 'Sua defesa x ataque dele'}
          meu={proximo.defesa.meu}
          dele={proximo.defesa.dele}
        />
      </div>
    </section>
  )
}

function Forca({ nome, meu, dele }: { nome: string; meu: number; dele: number | null }) {
  // sem adversario definido nao ha comparacao: a barra fica cheia e neutra
  const fatia = dele === null ? 100 : (100 * meu) / Math.max(meu + dele, 0.1)
  const razao = dele === null ? 1 : meu / Math.max(dele, 0.1)
  const cor = dele === null ? '' : razao >= 1.05 ? 'ok' : razao >= 0.92 ? '' : 'critico'
  // o sinal repete o que a cor diz: quem nao ve cor continua lendo
  const sinal = dele === null ? '' : meu > dele ? '>' : meu < dele ? '<' : '='
  return (
    <div>
      <div className="forca-topo">
        <span>{nome}</span>
        <span>
          <strong>{meu.toFixed(1)}</strong> {sinal} {dele === null ? '--' : dele.toFixed(1)}
        </span>
      </div>
      <div className="barra">
        <div className={cor} style={{ width: `${fatia}%` }} />
      </div>
    </div>
  )
}

// ------------------------------------------------------------------ escalacao
function CardEscalacao({
  escalacao,
  aoDefinirAuto,
  mudandoAuto,
}: {
  escalacao: Escalacao
  aoDefinirAuto: (ligada: boolean) => void
  mudandoAuto: boolean
}) {
  const ressalvas = escalacao.jogadores.filter((j) => j.estado !== 'ok')
  return (
    <section
      className="painel folgado estica"
    >
      <div className="painel-cab mb-3">
        <span className="painel-titulo">
          Escalacao · {escalacao.formacao} · {escalacao.tatica}
        </span>
        <div className="alavanca">
          <button
            type="button"
            className={escalacao.auto ? 'ativo' : ''}
            title={porque([[mudandoAuto, AGUARDE]], 'O time se monta sozinho antes de cada jogo')}
            disabled={mudandoAuto}
            onClick={() => aoDefinirAuto(true)}
          >
            Automatico
          </button>
          <button
            type="button"
            className={!escalacao.auto ? 'ativo' : ''}
            title={porque([[mudandoAuto, AGUARDE]], 'O seu XI e soberano, so repomos quem nao pode jogar')}
            disabled={mudandoAuto}
            onClick={() => aoDefinirAuto(false)}
          >
            Manual
          </button>
        </div>
      </div>

      <Campo jogadores={escalacao.jogadores} vagasAbertas={escalacao.vagas_abertas} />

      <div className="legenda-campo">
        <span><i className="ponto txt-normal" /> em ordem</span>
        <span className="txt-atencao"><i className="ponto" /> custa rendimento</span>
        <span className="txt-critico"><i className="ponto" /> cobra caro</span>
      </div>

      {/* o campo mostra a forma; a lista mostra o preco. So aparece quem tem
          algo a explicar - quem esta em ordem nao tem, e onze linhas iguais
          roubavam do campo a altura que ele precisa para ser legivel */}
      {ressalvas.length === 0 ? (
        <div className="sem-ressalva">
          {iconeDeEstado('ok', 14)}
          Ninguem improvisado ou desgastado no XI.
        </div>
      ) : (
        <div className="xi-lista mt-3">
          {ressalvas.map((j) => (
            <div className="xi-linha" key={j.id}>
              <span className={`xi-vaga ${j.improvisado ? j.estado : ''}`}>
                {j.improvisado ? `${j.pos}>${j.vaga}` : j.vaga}
              </span>
              <span className="xi-nome" title={j.nome}>{j.nome}</span>
              <span className="xi-num">{j.ovr}</span>
              <span className={`xi-fis ${j.cond < 45 ? 'critico' : j.cond < 65 ? 'atencao' : ''}`}>
                fis {j.cond}
              </span>
              <span className={`xi-obs ${j.estado}`}>{j.obs}</span>
            </div>
          ))}
          {escalacao.vagas_abertas > 0 && (
            <div className="xi-linha">
              <span className="xi-vaga critico">---</span>
              <span className="xi-nome txt-critico">
                {plural(escalacao.vagas_abertas, 'vaga')} sem jogador apto
              </span>
              <span className="xi-num">--</span>
              <span className="xi-fis">--</span>
              <span className="xi-obs critico">contrate</span>
            </div>
          )}
        </div>
      )}
    </section>
  )
}

// ------------------------------------------------------------------- objetivo
function CardObjetivo({ objetivo }: { objetivo: Objetivo }) {
  return (
    <section className="painel enxuto">
      <div className="painel-titulo">Objetivo da temporada</div>
      <div className="txt-m seminegrito mt-1">{objetivo.texto}</div>

      <div className="objetivo-barra">
        <div className={`cheio ${objetivo.estado}`} style={{ width: `${objetivo.progresso}%` }} />
        <div className="marca" style={{ left: `${objetivo.marca}%` }} title={`meta: top ${objetivo.alvo}`} />
      </div>

      <div className="objetivo-meta">
        <span className={`objetivo-pos ${objetivo.estado}`}>
          {objetivo.comecou ? `${objetivo.pos}º de ${objetivo.total}` : 'nao comecou'}
        </span>
        <span className="diretoria">
          meta top {objetivo.alvo}
          {objetivo.folga !== null &&
            (objetivo.folga >= 0 ? ` · ${objetivo.folga} de folga` : ` · faltam ${-objetivo.folga}`)}
        </span>
      </div>
      <ConfiancaDiretoria c={objetivo.confianca} fala={objetivo.diretoria} />
    </section>
  )
}

function ConfiancaDiretoria({ c, fala }: { c: Confianca; fala: string }) {
  const seta = c.tendencia > 0 ? '▲' : c.tendencia < 0 ? '▼' : '='
  return (
    <div className="confianca">
      <div className="confianca-cab">
        <span className="painel-titulo">Confianca da diretoria</span>
        <span className={`confianca-valor ${c.estado}`}>{c.valor}</span>
        <span className={`confianca-tendencia ${c.tendencia > 0 ? 'ok' : c.tendencia < 0 ? 'critico' : ''}`}>
          {seta} {c.tendencia > 0 ? `+${c.tendencia}` : c.tendencia} em 4 semanas
        </span>
      </div>
      <div
        className="confianca-barra"
        role="meter"
        aria-label="Confianca da diretoria"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={c.valor}
      >
        <div className={`cheio ${c.estado}`} style={{ width: `${c.valor}%` }} />
        <div className="confianca-marca" style={{ left: `${c.limite_aviso}%` }} title={`aviso abaixo de ${c.limite_aviso}`} />
        <div
          className="confianca-marca critico"
          style={{ left: `${c.limite_demissao}%` }}
          title={`demissao abaixo de ${c.limite_demissao}, depois do aviso`}
        />
      </div>
      {c.causas.length > 0 && (
        <ul className="confianca-causas" aria-label="Por que mudou na ultima semana">
          {c.causas.map((x, i) => (
            <li key={i} className={`txt-${x.estado}`}>
              {x.texto}
            </li>
          ))}
        </ul>
      )}
      <div className={`diretoria${c.aviso ? ' txt-critico negrito' : ''}`}>Diretoria: {fala}</div>
    </div>
  )
}

// --------------------------------------------------------------------- tabela
function CardTabela({ tabela }: { tabela: Tabela }) {
  return (
    <section className="painel em-lista">
      <div className="painel-titulo cab-lista">{tabela.titulo}</div>
      {tabela.vazio ? (
        <div className="vazio">{tabela.vazio}</div>
      ) : (
        <>
          <div className="tablerow cab">
            <span>Pos</span>
            <span>Clube</span>
            <span className="num">J</span>
            <span className="num">SG</span>
            <span className="num">V</span>
            <span className="num">Pts</span>
          </div>
          {tabela.linhas.map((l) => (
            <div className={`tablerow ${l.zona}${l.eu ? ' eu' : ''}`} key={l.pos}>
              <span className="pos">{l.pos}</span>
              <span className="clube">
                <MarcaZona zona={l.zona} texto={l.zona_texto} />
                {l.clube}
              </span>
              <span className="num">{l.j}</span>
              <span className="num">{l.sg > 0 ? `+${l.sg}` : l.sg}</span>
              <span className="num">{l.v}</span>
              <span className="num">{l.pts}</span>
            </div>
          ))}
          <LegendaZonas linhas={tabela.linhas} />
        </>
      )}
    </section>
  )
}

// ------------------------------------------------------------------ destaques
function CardDestaques({ destaques }: { destaques: Destaque[] }) {
  return (
    <section className="painel enxuto">
      <div className="painel-titulo mb-3">Destaques do elenco</div>
      <div className="destaques">
        {destaques.map((d) => (
          <div className="destaque" key={d.id}>
            <div className="avatar">{d.iniciais}</div>
            <div className="nome" title={d.nome}>{d.nome}</div>
            <div className="linha2">{d.pos} · overall {d.ovr}</div>
            <div className="linha2">{plural(d.g, 'gol')} · {d.a} assist.</div>
          </div>
        ))}
      </div>
    </section>
  )
}

// ------------------------------------------------------------------- noticias
function CardNoticias({ noticias }: { noticias: Noticia[] }) {
  return (
    <section
      className="painel em-lista estica"
    >
      <div className="painel-cab cab-lista">
        <span className="painel-titulo">Noticias do clube</span>
      </div>
      <div className="noticias">
        {noticias.length === 0 ? (
          <div className="vazio">Nada por aqui ainda. Avance a semana para comecar a historia.</div>
        ) : (
          noticias.map((n, i) => (
            <div className={`noticia ${n.estado}`} key={i}>
              <i className="bolinha" />
              <div>
                <div className="texto">{n.texto}</div>
                <div className="quando">{n.quando}</div>
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  )
}

// ------------------------------------------------------------- pelo mundo
function CardMundo({ mundo, aoIr }: { mundo: Manchete[]; aoIr: (destino: string) => void }) {
  return (
    <section className="painel em-lista">
      <div className="painel-cab cab-lista">
        <span className="painel-titulo">Pelo mundo</span>
        <div className="espaco" />
        <button type="button" className="bt-link" onClick={() => aoIr('noticias')}>
          ver tudo
        </button>
      </div>
      <FeedMundo mundo={mundo} vazio="O futebol ainda nao comecou. Avance a semana." />
    </section>
  )
}

export function FeedMundo({ mundo, vazio }: { mundo: Manchete[]; vazio: string }) {
  if (mundo.length === 0) return <div className="vazio">{vazio}</div>
  return (
    <ul className="feed-mundo">
      {mundo.map((m, i) => (
        <li key={i} className={`manchete ${m.tipo}`}>
          <span className="manchete-rotulo">{m.rotulo}</span>
          <span className="manchete-texto">{m.texto}</span>
          <span className="quando">{m.quando}</span>
        </li>
      ))}
    </ul>
  )
}
