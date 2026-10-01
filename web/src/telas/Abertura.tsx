// Antes do Painel existir: o menu principal do jogo.
//
// Visual de 2026-10-01 no jeito dos apps da Apple: janela de vidro fosco
// sobre um fundo escuro com luzes suaves, icone de app, titulo grande, botoes
// em pilula, barra de navegacao com "voltar", listas agrupadas (como os
// Ajustes do iPhone), controle segmentado e chave liga/desliga.
//
// Tres portas - Jogar, Configuracoes, Sobre. Jogar mostra os tres slots de
// save: slot cheio continua (ou apaga, com um segundo clique), slot vazio
// comeca uma carreira nova. As opcoes da carreira (dificuldade, sem demissao,
// investidor) moram so no formulario da carreira nova, que ja vem marcado com
// a ultima escolha; Configuracoes fica com a interface. So a escolha do clube
// grava o save.

import { Escudo } from '../componentes/Escudo'
import { porque, AGUARDE } from '../motivo'
import { useEffect, useState, type ReactNode } from 'react'
import { api } from '../api'
import { MarcaBrasfut } from '../icones'
import type {
  ClubeOpcao,
  Config,
  ModoCarreira,
  NivelCaos,
  OpcaoDificuldade,
  OpcoesCarreira,
  SituacaoJogo,
  SlotSave,
} from '../tipos'

interface Props {
  situacao: SituacaoJogo
  clubes: ClubeOpcao[]
  versao: string
  slots: SlotSave[]
  config: Config | null
  erro: string | null
  ocupado: boolean
  aoAbrir: (slot: number) => void
  aoCriar: (nome: string, opcoes: OpcoesCarreira, slot: number) => void
  aoApagar: (slot: number) => void
  aoEscolher: (id: number) => void
  aoConfig: (mudanca: Partial<Config>) => void
}

type Vista = 'menu' | 'slots' | 'nova' | 'config' | 'sobre'

const MODOS: { id: ModoCarreira; nome: string; desc: string }[] = [
  { id: 'classico', nome: 'Classico', desc: 'O futebol como ele e: tabela, mercado, diretoria e torcida.' },
  {
    id: 'caos',
    nome: 'Caos',
    desc: 'Plantao ao vivo toda semana: doping descoberto anos depois, dinheiro sujo pego no fair play, capitao preso, xeique comprando clube da Serie D, meteorito no gramado. Nada e seguro, nem o seu clube.',
  },
]

const NIVEIS_CAOS: { id: NivelCaos; nome: string; desc: string }[] = [
  { id: 'calmo', nome: 'Calmo', desc: 'um plantao a cada tres semanas' },
  { id: 'normal', nome: 'Normal', desc: 'um plantao a cada duas semanas' },
  { id: 'caotico', nome: 'Caotico', desc: 'quase toda semana, as vezes dois' },
]

const TITULO: Record<Vista, string> = {
  menu: '',
  slots: 'Carreiras',
  nova: 'Nova carreira',
  config: 'Configuracoes',
  sobre: 'Sobre',
}

export function Abertura(props: Props) {
  const { situacao, erro } = props
  const [vista, setVista] = useState<Vista>('menu')
  const [slotNovo, setSlotNovo] = useState(1)
  const [dificuldades, setDificuldades] = useState<OpcaoDificuldade[]>([])

  useEffect(() => {
    api.config().then((r) => setDificuldades(r.dificuldades)).catch(() => {})
  }, [])

  if (situacao === 'escolher_clube') return <EscolherClube {...props} />

  let corpo
  if (vista === 'slots')
    corpo = (
      <Slots
        {...props}
        aoNova={(n) => {
          setSlotNovo(n)
          setVista('nova')
        }}
      />
    )
  else if (vista === 'nova') corpo = <NovaCarreira {...props} slot={slotNovo} dificuldades={dificuldades} />
  else if (vista === 'config') corpo = <Configuracoes {...props} />
  else if (vista === 'sobre') corpo = <Sobre versao={props.versao} />
  else
    corpo = (
      <nav className="ab-menu" aria-label="Menu principal">
        <button type="button" className="ab-bt ab-bt-primario" onClick={() => setVista('slots')}>
          Jogar
        </button>
        <button type="button" className="ab-bt ab-bt-secundario" onClick={() => setVista('config')}>
          Configuracoes
        </button>
        <button type="button" className="ab-link" onClick={() => setVista('sobre')}>
          Sobre o BRASFUT
        </button>
      </nav>
    )

  const larga = vista === 'slots' || vista === 'nova'
  return (
    <Fundo>
      <main className={`ab-janela${larga ? ' larga' : ''}${vista === 'menu' ? ' inicio' : ''}`}>
        {vista === 'menu' ? (
          <header className="ab-marca">
            <div className="ab-icone">
              <MarcaBrasfut tamanho={64} />
            </div>
            <h1 className="ab-titulo">BRASFUT</h1>
            <p className="ab-sub">O futebol brasileiro inteiro na sua mao.</p>
          </header>
        ) : (
          <BarraNav
            titulo={TITULO[vista]}
            voltar={vista === 'nova' ? 'Carreiras' : 'Inicio'}
            aoVoltar={() => setVista(vista === 'nova' ? 'slots' : 'menu')}
          />
        )}
        <div key={vista} className="ab-conteudo">
          {corpo}
        </div>
        {erro && <p className="ab-erro">{erro}</p>}
        {vista === 'menu' && <footer className="ab-rodape">versao {props.versao}</footer>}
      </main>
    </Fundo>
  )
}

// ------------------------------------------------------------ pecas comuns
function Fundo({ children }: { children: ReactNode }) {
  return (
    <div className="ab-fundo">
      <span className="ab-luz um" aria-hidden="true" />
      <span className="ab-luz dois" aria-hidden="true" />
      <span className="ab-luz tres" aria-hidden="true" />
      {children}
    </div>
  )
}

function BarraNav({ titulo, voltar, aoVoltar }: { titulo: string; voltar?: string; aoVoltar?: () => void }) {
  return (
    <div className="ab-barra">
      {aoVoltar ? (
        <button type="button" className="ab-voltar" onClick={aoVoltar}>
          <span aria-hidden="true">‹</span> {voltar}
        </button>
      ) : (
        <span />
      )}
      <h2>{titulo}</h2>
      <span />
    </div>
  )
}

/** Controle segmentado (como o do iOS): uma opcao so, a escolhida em relevo. */
function Segmento<T extends string | number>({
  opcoes,
  valor,
  aoMudar,
  rotulo,
  perigo,
}: {
  opcoes: { id: T; nome: string }[]
  valor: T
  aoMudar: (v: T) => void
  rotulo: string
  perigo?: boolean
}) {
  return (
    <div className={`ab-segmento${perigo ? ' perigo' : ''}`} role="radiogroup" aria-label={rotulo}>
      {opcoes.map((o) => (
        <button
          key={String(o.id)}
          type="button"
          role="radio"
          aria-checked={valor === o.id}
          className={valor === o.id ? 'ativo' : ''}
          onClick={() => aoMudar(o.id)}
        >
          {o.nome}
        </button>
      ))}
    </div>
  )
}

/** Linha de lista agrupada com chave liga/desliga. */
function LinhaChave({
  titulo,
  desc,
  ligado,
  aoMudar,
}: {
  titulo: string
  desc?: string
  ligado: boolean
  aoMudar: (v: boolean) => void
}) {
  return (
    <label className="ab-linha">
      <span className="ab-linha-texto">
        <span className="ab-linha-titulo">{titulo}</span>
        {desc && <span className="ab-linha-desc">{desc}</span>}
      </span>
      <input
        type="checkbox"
        role="switch"
        className="ab-chave"
        checked={ligado}
        onChange={(e) => aoMudar(e.target.checked)}
      />
    </label>
  )
}

// --------------------------------------------------------------------- slots
function Slots({ slots, ocupado, aoAbrir, aoApagar, aoNova }: Props & { aoNova: (slot: number) => void }) {
  const [apagando, setApagando] = useState<number | null>(null)
  return (
    <div className="ab-slots">
      {slots.map((s) =>
        s.vazio ? (
          <button key={s.slot} type="button" className="ab-slot vazio" onClick={() => aoNova(s.slot)}>
            <span className="ab-slot-num">Slot {s.slot}</span>
            <span className="ab-slot-mais" aria-hidden="true">+</span>
            <span className="ab-slot-clube">Carreira nova</span>
            <span className="ab-slot-meta">espaco livre</span>
          </button>
        ) : (
          <div key={s.slot} className="ab-slot">
            <div className="ab-slot-topo">
              <span className="ab-slot-num">Slot {s.slot}</span>
              {s.modo === 'caos' && (
                <span className="ab-selo caos">
                  Caos{s.caos_nivel && s.caos_nivel !== 'normal' ? ` · ${s.caos_nivel}` : ''}
                </span>
              )}
            </div>
            <div className="ab-slot-escudo">
              {s.escudo ? <Escudo nome={s.escudo.nome} dados={s.escudo} tamanho={52} /> : <MarcaBrasfut tamanho={40} />}
            </div>
            <span className="ab-slot-clube">{s.clube || 'sem clube'}</span>
            <span className="ab-slot-tecnico">{s.tecnico}</span>
            <span className="ab-slot-meta">
              {s.divisao ? `Serie ${s.divisao} · ` : ''}temporada {s.temporada}
              {s.titulos ? ` · ${s.titulos} ${s.titulos === 1 ? 'titulo' : 'titulos'}` : ''}
            </span>
            {s.salvo_em && <span className="ab-slot-meta fraco">salvo em {s.salvo_em}</span>}
            <div className="ab-slot-acoes">
              {apagando === s.slot ? (
                <>
                  <button
                    type="button"
                    className="ab-bt ab-bt-perigo pequeno"
                    onClick={() => {
                      setApagando(null)
                      aoApagar(s.slot)
                    }}
                  >
                    Apagar de vez
                  </button>
                  <button type="button" className="ab-link" onClick={() => setApagando(null)}>
                    Manter
                  </button>
                </>
              ) : (
                <>
                  <button
                    type="button"
                    className="ab-bt ab-bt-primario pequeno"
                    title={porque([[ocupado, AGUARDE]])}
                    disabled={ocupado}
                    onClick={() => aoAbrir(s.slot)}
                  >
                    {ocupado ? 'Abrindo…' : 'Continuar'}
                  </button>
                  <button type="button" className="ab-link perigo" onClick={() => setApagando(s.slot)}>
                    Apagar
                  </button>
                </>
              )}
            </div>
          </div>
        ),
      )}
    </div>
  )
}

// ------------------------------------------------------------ carreira nova
function NovaCarreira({ config, ocupado, dificuldades, slot, aoCriar }: Props & {
  slot: number
  dificuldades: OpcaoDificuldade[]
}) {
  const [nome, setNome] = useState('')
  const [opcoes, setOpcoes] = useState<OpcoesCarreira>({
    dificuldade: config?.dificuldade ?? 'normal',
    sem_demissao: config?.sem_demissao ?? false,
    investidor: config?.investidor ?? false,
    modo: config?.modo ?? 'classico',
    caos_nivel: config?.caos_nivel ?? 'normal',
  })
  const nomeLimpo = nome.trim()
  const modo = MODOS.find((m) => m.id === opcoes.modo)
  const nivel = NIVEIS_CAOS.find((n) => n.id === opcoes.caos_nivel)
  const dif = dificuldades.find((d) => d.id === opcoes.dificuldade)

  return (
    <form
      className="ab-form"
      onSubmit={(e) => {
        e.preventDefault()
        if (nomeLimpo) aoCriar(nomeLimpo, opcoes, slot)
      }}
    >
      <section className="ab-grupo">
        <h3 className="ab-grupo-titulo">Treinador</h3>
        <div className="ab-lista">
          <label className="ab-linha campo">
            <span className="ab-linha-titulo">Nome</span>
            <input
              id="nome-tecnico"
              className="ab-entrada"
              value={nome}
              maxLength={40}
              autoFocus
              autoComplete="off"
              placeholder="Como a imprensa vai te chamar"
              onChange={(e) => setNome(e.target.value)}
            />
          </label>
        </div>
      </section>

      <section className="ab-grupo">
        <h3 className="ab-grupo-titulo">Modo de jogo</h3>
        <div className="ab-lista">
          <div className="ab-linha coluna">
            <Segmento
              rotulo="Modo de jogo"
              opcoes={MODOS}
              valor={opcoes.modo}
              perigo={opcoes.modo === 'caos'}
              aoMudar={(m) => setOpcoes({ ...opcoes, modo: m })}
            />
            {modo && <p className="ab-linha-desc">{modo.desc}</p>}
          </div>
          {opcoes.modo === 'caos' && (
            <div className="ab-linha coluna">
              <span className="ab-linha-titulo">Frequencia dos plantoes</span>
              <Segmento
                rotulo="Frequencia dos plantoes"
                opcoes={NIVEIS_CAOS}
                valor={opcoes.caos_nivel}
                perigo
                aoMudar={(n) => setOpcoes({ ...opcoes, caos_nivel: n })}
              />
              {nivel && <p className="ab-linha-desc">{nivel.desc}</p>}
            </div>
          )}
        </div>
      </section>

      {dificuldades.length > 0 && (
        <section className="ab-grupo">
          <h3 className="ab-grupo-titulo">Dificuldade</h3>
          <div className="ab-lista">
            <div className="ab-linha coluna">
              <Segmento
                rotulo="Dificuldade"
                opcoes={dificuldades}
                valor={opcoes.dificuldade}
                aoMudar={(d) => setOpcoes({ ...opcoes, dificuldade: d })}
              />
              {dif && <p className="ab-linha-desc">{dif.desc}</p>}
            </div>
          </div>
        </section>
      )}

      <section className="ab-grupo">
        <h3 className="ab-grupo-titulo">Modificadores</h3>
        <div className="ab-lista">
          <LinhaChave
            titulo="Sem demissao"
            desc="A diretoria cobra, mas nunca demite."
            ligado={opcoes.sem_demissao}
            aoMudar={(v) => setOpcoes({ ...opcoes, sem_demissao: v })}
          />
          <LinhaChave
            titulo="Investidor compra o clube"
            desc="Aporte ao assumir: R$ 150 mi na Serie A, 60 mi na B, 25 mi na C, 10 mi na D."
            ligado={opcoes.investidor}
            aoMudar={(v) => setOpcoes({ ...opcoes, investidor: v })}
          />
        </div>
        <p className="ab-grupo-nota">
          Vai para o slot {slot}. As escolhas valem pelo save inteiro, e a proxima carreira nova ja vem marcada com
          elas.
        </p>
      </section>

      <button
        type="submit"
        className="ab-bt ab-bt-primario largo"
        title={porque([[ocupado, AGUARDE], [!nomeLimpo, 'Escreva o nome do treinador']])}
        disabled={ocupado || !nomeLimpo}
      >
        {ocupado ? 'Criando mundo…' : 'Criar mundo e escolher clube'}
      </button>
    </form>
  )
}

// ------------------------------------------------------------ configuracoes
function Configuracoes({ config, aoConfig }: Props) {
  if (!config) return null
  return (
    <div className="ab-form">
      <section className="ab-grupo">
        <h3 className="ab-grupo-titulo">Interface</h3>
        <div className="ab-lista">
          <div className="ab-linha">
            <span className="ab-linha-titulo">Tamanho</span>
            <Segmento
              rotulo="Tamanho da interface"
              opcoes={([90, 100, 110, 125] as const).map((e) => ({ id: e, nome: `${e}%` }))}
              valor={config.escala}
              aoMudar={(e) => aoConfig({ escala: e })}
            />
          </div>
          <LinhaChave
            titulo="Reduzir animacoes"
            desc="Janelas e transicoes aparecem sem movimento."
            ligado={config.reduzir_animacoes}
            aoMudar={(v) => aoConfig({ reduzir_animacoes: v })}
          />
        </div>
        <p className="ab-grupo-nota">
          Salvo na hora, vale para todos os slots. Dificuldade e modificadores sao escolhidos ao criar cada carreira.
        </p>
      </section>
    </div>
  )
}

// --------------------------------------------------------------------- sobre
function Sobre({ versao }: { versao: string }) {
  return (
    <div className="ab-form">
      <div className="ab-sobre-topo">
        <div className="ab-icone pequeno">
          <MarcaBrasfut tamanho={40} />
        </div>
        <div>
          <strong>BRASFUT</strong>
          <span className="ab-linha-desc">versao {versao}</span>
        </div>
      </div>
      <section className="ab-grupo">
        <div className="ab-lista">
          <p className="ab-texto">
            Gerenciador de futebol brasileiro: Series A, B, C e D, estaduais, Copa do Brasil, Libertadores e
            Sul-Americana, ligas de fora, mercado com negociacao, emprestimos, estadio e categorias de base.
          </p>
          <p className="ab-texto">
            O jogo roda inteiro na sua maquina, sem internet e sem conta. Sao tres slots de save na pasta do jogo
            (brasfut_save.json, brasfut_save_2.json e brasfut_save_3.json), gravados sozinhos ao fim de cada semana.
          </p>
        </div>
        <p className="ab-grupo-nota">
          Motor em Python, sem dependencias externas. Interface em React e TypeScript. Fontes Space Grotesk e Manrope,
          sob a SIL Open Font License.
        </p>
      </section>
    </div>
  )
}

// ----------------------------------------------------------- escolher clube
function EscolherClube({ clubes, erro, ocupado, aoEscolher }: Props) {
  const [serie, setSerie] = useState('A')
  const daSerie = clubes.filter((c) => c.divisao === serie)
  // as abas saem do que o servidor mandou: series brasileiras e ligas de fora
  const ligas: { id: string; nome: string }[] = []
  for (const c of clubes) {
    if (!ligas.some((l) => l.id === c.divisao)) ligas.push({ id: c.divisao, nome: c.liga ?? `Serie ${c.divisao}` })
  }
  return (
    <Fundo>
      <main className="ab-janela larga">
        <BarraNav titulo="Escolha seu clube" />
        <p className="ab-grupo-nota centro">O mundo foi criado. A carreira so e salva depois desta escolha.</p>
        <div className="ab-ligas" role="tablist" aria-label="Ligas">
          {ligas.map((l) => (
            <button
              key={l.id}
              type="button"
              role="tab"
              aria-selected={serie === l.id}
              className={serie === l.id ? 'ativo' : ''}
              onClick={() => setSerie(l.id)}
            >
              {l.nome}
            </button>
          ))}
        </div>
        <div className="ab-lista ab-clubes">
          {daSerie.map((c) => (
            <button
              type="button"
              className="ab-linha ab-clube"
              key={c.id}
              title={porque([[ocupado, AGUARDE]])}
              disabled={ocupado}
              onClick={() => aoEscolher(c.id)}
            >
              <Escudo nome={c.nome} tamanho={28} />
              <span className="ab-linha-titulo">{c.nome}</span>
              <span className="ab-rep" title="reputacao">
                {c.reputacao}
              </span>
              <span className="ab-chevron" aria-hidden="true">
                ›
              </span>
            </button>
          ))}
        </div>
        {erro && <p className="ab-erro">{erro}</p>}
      </main>
    </Fundo>
  )
}
