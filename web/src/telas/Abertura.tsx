// Antes do Painel existir: o menu principal do jogo.
//
// Tres portas - Jogar, Configuracoes, Sobre. Jogar mostra os tres slots de
// save: slot cheio continua (ou apaga, com um segundo clique), slot vazio
// comeca uma carreira nova. As opcoes da carreira (dificuldade, sem demissao,
// investidor) moram so no formulario da carreira nova, que ja vem marcado com
// a ultima escolha; Configuracoes fica com a interface. So a escolha do clube
// grava o save.

import { Escudo } from '../componentes/Escudo'
import { porque, AGUARDE } from '../motivo'
import { useEffect, useState } from 'react'
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

export function Abertura(props: Props) {
  const { situacao, erro } = props
  const [vista, setVista] = useState<Vista>('menu')
  const [slotNovo, setSlotNovo] = useState(1)
  const [dificuldades, setDificuldades] = useState<OpcaoDificuldade[]>([])

  useEffect(() => {
    api.config().then((r) => setDificuldades(r.dificuldades)).catch(() => {})
  }, [])

  if (situacao === 'escolher_clube') return <EscolherClube {...props} />

  const voltar = () => setVista('menu')
  let corpo
  if (vista === 'slots')
    corpo = (
      <Slots
        {...props}
        aoNova={(n) => {
          setSlotNovo(n)
          setVista('nova')
        }}
        aoVoltar={voltar}
      />
    )
  else if (vista === 'nova')
    corpo = <NovaCarreira {...props} slot={slotNovo} dificuldades={dificuldades} aoVoltar={() => setVista('slots')} />
  else if (vista === 'config') corpo = <Configuracoes {...props} aoVoltar={voltar} />
  else if (vista === 'sobre') corpo = <Sobre versao={props.versao} aoVoltar={voltar} />
  else
    corpo = (
      <nav className="menu-principal" aria-label="Menu principal">
        <button type="button" className="bt-acao" onClick={() => setVista('slots')}>
          Jogar
        </button>
        <button type="button" className="bt-fantasma" onClick={() => setVista('config')}>
          Configuracoes
        </button>
        <button type="button" className="bt-fantasma" onClick={() => setVista('sobre')}>
          Sobre
        </button>
      </nav>
    )

  return (
    <div className="abertura-fundo">
      <div className={`abertura-cartao${vista === 'slots' || vista === 'nova' ? ' largo' : ''}`}>
        <header className="abertura-marca">
          <MarcaBrasfut tamanho={vista === 'menu' ? 84 : 52} />
          <div>
            <h1>BRASFUT</h1>
            {vista === 'menu' && <div className="abertura-lema">o futebol brasileiro inteiro na sua mao</div>}
          </div>
        </header>
        {corpo}
        {erro && <p className="erro mt-4">{erro}</p>}
        <div className="abertura-versao">versao {props.versao}</div>
      </div>
    </div>
  )
}

// --------------------------------------------------------------------- slots
function Slots({ slots, ocupado, aoAbrir, aoApagar, aoNova, aoVoltar }: Props & {
  aoNova: (slot: number) => void
  aoVoltar: () => void
}) {
  const [apagando, setApagando] = useState<number | null>(null)
  return (
    <>
      <div className="slots">
        {slots.map((s) =>
          s.vazio ? (
            <button key={s.slot} type="button" className="slot vazio" onClick={() => aoNova(s.slot)}>
              <span className="slot-num">Slot {s.slot}</span>
              <span className="slot-mais" aria-hidden="true">+</span>
              <span className="slot-clube">Carreira nova</span>
              <span className="tag-fraco">vazio</span>
            </button>
          ) : (
            <div key={s.slot} className="slot">
              <span className="slot-num">
                Slot {s.slot}
                {s.modo === 'caos' && (
                  <span className="slot-modo">
                    modo caos{s.caos_nivel && s.caos_nivel !== 'normal' ? ` · ${s.caos_nivel}` : ''}
                  </span>
                )}
              </span>
              <span className="slot-clube escudo-com-nome">
                {s.escudo && <Escudo nome={s.escudo.nome} dados={s.escudo} tamanho={30} />}
                <span>{s.clube || 'sem clube'}</span>
              </span>
              <span className="slot-tecnico">{s.tecnico}</span>
              <span className="tag-fraco">
                {s.divisao ? `Serie ${s.divisao} · ` : ''}temporada {s.temporada}
                {s.titulos ? ` · ${s.titulos} ${s.titulos === 1 ? 'titulo' : 'titulos'}` : ''}
              </span>
              {s.salvo_em && <span className="tag-fraco slot-data">salvo em {s.salvo_em}</span>}
              {apagando === s.slot ? (
                <div className="slot-acoes">
                  <button type="button" className="bt-fantasma" onClick={() => setApagando(null)}>
                    Manter
                  </button>
                  <button
                    type="button"
                    className="bt-acao bt-perigo"
                    onClick={() => {
                      setApagando(null)
                      aoApagar(s.slot)
                    }}
                  >
                    Apagar de vez
                  </button>
                </div>
              ) : (
                <div className="slot-acoes">
                  <button type="button" className="bt-fantasma" onClick={() => setApagando(s.slot)}>
                    Apagar
                  </button>
                  <button type="button" className="bt-acao" title={porque([[ocupado, AGUARDE]])}
                  disabled={ocupado} onClick={() => aoAbrir(s.slot)}>
                    {ocupado ? 'Abrindo…' : 'Continuar'}
                  </button>
                </div>
              )}
            </div>
          ),
        )}
      </div>
      <div className="modal-acoes">
        <button type="button" className="bt-fantasma" onClick={aoVoltar}>
          Voltar
        </button>
      </div>
    </>
  )
}

// ------------------------------------------------------------ carreira nova
function NovaCarreira({ config, ocupado, dificuldades, slot, aoCriar, aoVoltar }: Props & {
  slot: number
  dificuldades: OpcaoDificuldade[]
  aoVoltar: () => void
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

  return (
    <form
      className="form-carreira"
      onSubmit={(e) => {
        e.preventDefault()
        if (nomeLimpo) aoCriar(nomeLimpo, opcoes, slot)
      }}
    >
      <label className="campo-rotulo" htmlFor="nome-tecnico">
        Nome do treinador
      </label>
      <input
        id="nome-tecnico"
        className="campo-texto"
        value={nome}
        maxLength={40}
        autoFocus
        autoComplete="off"
        placeholder="Como a imprensa vai te chamar"
        onChange={(e) => setNome(e.target.value)}
      />

      <fieldset className="mesa-bloco">
        <legend className="painel-titulo">Modo de jogo</legend>
        <div className="modos">
          {MODOS.map((m) => (
            <label key={m.id} className={`modo-opcao ${m.id}${opcoes.modo === m.id ? ' ativo' : ''}`}>
              <input
                type="radio"
                name="modo"
                checked={opcoes.modo === m.id}
                onChange={() => setOpcoes({ ...opcoes, modo: m.id })}
              />
              <strong>{m.nome}</strong>
              <span>{m.desc}</span>
            </label>
          ))}
        </div>
        {opcoes.modo === 'caos' && (
          <div className="niveis-caos" role="radiogroup" aria-label="Frequencia dos plantoes">
            <span className="tag-fraco">Frequencia dos plantoes</span>
            {NIVEIS_CAOS.map((n) => (
              <label key={n.id} className={`nivel-caos${opcoes.caos_nivel === n.id ? ' ativo' : ''}`}>
                <input
                  type="radio"
                  name="caos_nivel"
                  checked={opcoes.caos_nivel === n.id}
                  onChange={() => setOpcoes({ ...opcoes, caos_nivel: n.id })}
                />
                <strong>{n.nome}</strong>
                <span>{n.desc}</span>
              </label>
            ))}
          </div>
        )}
      </fieldset>

      <fieldset className="mesa-bloco">
        <legend className="painel-titulo">Dificuldade</legend>
        {dificuldades.map((d) => (
          <label key={d.id} className="avanco-opcao">
            <input
              type="radio"
              name="dificuldade"
              checked={opcoes.dificuldade === d.id}
              onChange={() => setOpcoes({ ...opcoes, dificuldade: d.id })}
            />
            <strong>{d.nome}</strong>
            <span className="tag-fraco">{d.desc}</span>
          </label>
        ))}
      </fieldset>

      <fieldset className="mesa-bloco">
        <legend className="painel-titulo">Modificadores de carreira</legend>
        <label className="avanco-parada">
          <input
            type="checkbox"
            checked={opcoes.sem_demissao}
            onChange={(e) => setOpcoes({ ...opcoes, sem_demissao: e.target.checked })}
          />
          <span>
            <strong>Sem demissao</strong>
            <span className="tag-fraco"> a diretoria cobra, mas nunca demite</span>
          </span>
        </label>
        <label className="avanco-parada">
          <input
            type="checkbox"
            checked={opcoes.investidor}
            onChange={(e) => setOpcoes({ ...opcoes, investidor: e.target.checked })}
          />
          <span>
            <strong>Investidor compra o clube</strong>
            <span className="tag-fraco"> aporte no caixa ao assumir: R$ 150 mi na Serie A, 60 mi na B, 25 mi na C, 10 mi na D</span>
          </span>
        </label>
      </fieldset>

      <p className="tag-fraco">
        Vai para o slot {slot}. Estas escolhas valem pelo save inteiro, e a proxima carreira nova ja vem marcada
        com elas.
      </p>
      <div className="modal-acoes">
        <button type="button" className="bt-fantasma" onClick={aoVoltar}>
          Voltar
        </button>
        <button type="submit" className="bt-acao" title={porque([[ocupado, AGUARDE], [!nomeLimpo, 'Escreva o nome do treinador']])}
        disabled={ocupado || !nomeLimpo}>
          {ocupado ? 'Criando mundo…' : 'Criar mundo e escolher clube'}
        </button>
      </div>
    </form>
  )
}

// ------------------------------------------------------------ configuracoes
function Configuracoes({ config, aoConfig, aoVoltar }: Props & { aoVoltar: () => void }) {
  if (!config) return null
  return (
    <div className="form-carreira">
      <fieldset className="mesa-bloco">
        <legend className="painel-titulo">Interface</legend>
        <div className="linha-config">
          <span>Tamanho da interface</span>
          <div className="alavanca">
            {([90, 100, 110, 125] as const).map((e) => (
              <button
                key={e}
                type="button"
                className={config.escala === e ? 'ativo' : ''}
                aria-pressed={config.escala === e}
                onClick={() => aoConfig({ escala: e })}
              >
                {e}%
              </button>
            ))}
          </div>
        </div>
        <label className="avanco-parada">
          <input
            type="checkbox"
            checked={config.reduzir_animacoes}
            onChange={(e) => aoConfig({ reduzir_animacoes: e.target.checked })}
          />
          Reduzir animacoes
        </label>
      </fieldset>
      <p className="tag-fraco">
        Salvo na hora, vale para todos os slots. Dificuldade e modificadores sao escolhidos ao criar cada carreira.
      </p>
      <div className="modal-acoes">
        <button type="button" className="bt-acao" onClick={aoVoltar}>
          Voltar
        </button>
      </div>
    </div>
  )
}

// --------------------------------------------------------------------- sobre
function Sobre({ versao, aoVoltar }: { versao: string; aoVoltar: () => void }) {
  return (
    <div className="sobre">
      <p>
        <strong>Versao {versao}</strong>
        <br />
        Gerenciador de futebol brasileiro: Series A, B, C e D, estaduais, Copa do Brasil, Libertadores e
        Sul-Americana, mercado com negociacao, emprestimos, estadio e categorias de base.
      </p>
      <p>
        O jogo roda inteiro na sua maquina, sem internet e sem conta. Sao tres slots de save na pasta do
        jogo (brasfut_save.json, brasfut_save_2.json e brasfut_save_3.json), gravados sozinhos ao fim de cada
        semana.
      </p>
      <p className="tag-fraco">
        Motor em Python, sem dependencias externas. Interface em React e TypeScript. Fontes Space Grotesk e
        Manrope, sob a SIL Open Font License.
      </p>
      <div className="modal-acoes">
        <button type="button" className="bt-acao" onClick={aoVoltar}>
          Voltar
        </button>
      </div>
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
    <div className="centro-tela">
      <div className="modal largo">
        <h2>Escolha o clube que voce vai treinar</h2>
        <p>O mundo foi criado. A carreira so e salva depois desta escolha.</p>
        <div className="alavanca abas-ligas mb-3">
          {ligas.map((l) => (
            <button
              key={l.id}
              type="button"
              className={serie === l.id ? 'ativo' : ''}
              aria-pressed={serie === l.id}
              onClick={() => setSerie(l.id)}
            >
              {l.nome}
            </button>
          ))}
        </div>
        <div className="lista-clubes">
          {daSerie.map((c) => (
            <button
              type="button"
              className="clube-opcao"
              key={c.id}
              title={porque([[ocupado, AGUARDE]])}
              disabled={ocupado}
              onClick={() => aoEscolher(c.id)}
            >
              <span className="escudo-com-nome">
                <Escudo nome={c.nome} tamanho={22} />
                <span>{c.nome}</span>
              </span>
              <span className="serie">REP {c.reputacao}</span>
            </button>
          ))}
        </div>
        {erro && <p className="erro">{erro}</p>}
      </div>
    </div>
  )
}
