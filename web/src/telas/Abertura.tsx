// Antes do Painel existir: o menu principal do jogo.
//
// Tres portas - Iniciar, Configuracoes, Sobre. Iniciar leva a continuar o save
// que existe ou a uma carreira nova, que pede o nome do treinador e as opcoes
// que valem pelo save inteiro (dificuldade, sem demissao, investidor) antes de
// criar o mundo. So depois vem a escolha do clube, e so ela grava o save.

import { useEffect, useState } from 'react'
import { api } from '../api'
import { Estrela } from '../icones'
import type {
  ClubeOpcao,
  Config,
  OpcaoDificuldade,
  OpcoesCarreira,
  RespostaEstado,
  SituacaoJogo,
} from '../tipos'

interface Props {
  situacao: SituacaoJogo
  clubes: ClubeOpcao[]
  versao: string
  save: RespostaEstado['save']
  config: Config | null
  erro: string | null
  ocupado: boolean
  aoAbrir: () => void
  aoCriar: (nome: string, opcoes: OpcoesCarreira) => void
  aoEscolher: (id: number) => void
  aoConfig: (mudanca: Partial<Config>) => void
}

type Vista = 'menu' | 'iniciar' | 'nova' | 'config' | 'sobre'

export function Abertura(props: Props) {
  const { situacao, erro } = props
  const [vista, setVista] = useState<Vista>('menu')
  const [dificuldades, setDificuldades] = useState<OpcaoDificuldade[]>([])

  useEffect(() => {
    api.config().then((r) => setDificuldades(r.dificuldades)).catch(() => {})
  }, [])

  if (situacao === 'escolher_clube') return <EscolherClube {...props} />

  const voltar = () => setVista('menu')
  let corpo
  if (vista === 'iniciar') corpo = <Iniciar {...props} aoNova={() => setVista('nova')} aoVoltar={voltar} />
  else if (vista === 'nova')
    corpo = <NovaCarreira {...props} dificuldades={dificuldades} aoVoltar={() => setVista('iniciar')} />
  else if (vista === 'config')
    corpo = <Configuracoes {...props} dificuldades={dificuldades} aoVoltar={voltar} />
  else if (vista === 'sobre') corpo = <Sobre versao={props.versao} aoVoltar={voltar} />
  else
    corpo = (
      <nav className="menu-principal" aria-label="Menu principal">
        <button type="button" className="bt-acao" onClick={() => setVista('iniciar')}>
          Iniciar
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
    <div className="centro-tela">
      <div className="cartao-centro abertura">
        <div className="escudo gg" style={{ margin: '0 auto 18px' }}>
          <Estrela tamanho={26} />
        </div>
        <h1>BRASFUT</h1>
        {corpo}
        {erro && <p className="erro" style={{ marginTop: 16 }}>{erro}</p>}
      </div>
    </div>
  )
}

// ------------------------------------------------------------------- iniciar
function Iniciar({ situacao, save, ocupado, aoAbrir, aoNova, aoVoltar }: Props & {
  aoNova: () => void
  aoVoltar: () => void
}) {
  const temSave = situacao === 'tem_save'
  return (
    <>
      <p>
        {temSave && save
          ? `Carreira salva: ${save.tecnico}, ${save.clube}, temporada ${save.temporada}. Continue de onde parou ou comece outra por cima dela.`
          : temSave
            ? 'Existe um jogo salvo nesta pasta. Continue de onde parou, ou comece uma carreira nova por cima dele.'
            : 'Nenhum jogo salvo por aqui. Vamos criar um mundo novo e escolher o seu clube.'}
      </p>
      <div className="modal-acoes">
        <button type="button" className="bt-fantasma" onClick={aoVoltar}>
          Voltar
        </button>
        {temSave && (
          <button type="button" className="bt-acao" disabled={ocupado} onClick={aoAbrir}>
            {ocupado ? 'Abrindo…' : 'Continuar carreira'}
          </button>
        )}
        <button type="button" className={temSave ? 'bt-fantasma' : 'bt-acao'} onClick={aoNova}>
          Carreira nova
        </button>
      </div>
    </>
  )
}

// ------------------------------------------------------------ carreira nova
function NovaCarreira({ situacao, config, ocupado, dificuldades, aoCriar, aoVoltar }: Props & {
  dificuldades: OpcaoDificuldade[]
  aoVoltar: () => void
}) {
  const [nome, setNome] = useState('')
  const [opcoes, setOpcoes] = useState<OpcoesCarreira>({
    dificuldade: config?.dificuldade ?? 'normal',
    sem_demissao: config?.sem_demissao ?? false,
    investidor: config?.investidor ?? false,
  })
  const nomeLimpo = nome.trim()

  return (
    <form
      className="form-carreira"
      onSubmit={(e) => {
        e.preventDefault()
        if (nomeLimpo) aoCriar(nomeLimpo, opcoes)
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
        Estas escolhas valem pelo save inteiro.
        {situacao === 'tem_save' && ' O save atual sera substituido quando voce escolher o clube.'}
      </p>
      <div className="modal-acoes">
        <button type="button" className="bt-fantasma" onClick={aoVoltar}>
          Voltar
        </button>
        <button type="submit" className="bt-acao" disabled={ocupado || !nomeLimpo}>
          {ocupado ? 'Criando mundo…' : 'Criar mundo e escolher clube'}
        </button>
      </div>
    </form>
  )
}

// ------------------------------------------------------------ configuracoes
function Configuracoes({ config, dificuldades, aoConfig, aoVoltar }: Props & {
  dificuldades: OpcaoDificuldade[]
  aoVoltar: () => void
}) {
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

      <fieldset className="mesa-bloco">
        <legend className="painel-titulo">Padrao para carreiras novas</legend>
        {dificuldades.map((d) => (
          <label key={d.id} className="avanco-opcao">
            <input
              type="radio"
              name="dificuldade-padrao"
              checked={config.dificuldade === d.id}
              onChange={() => aoConfig({ dificuldade: d.id })}
            />
            <strong>{d.nome}</strong>
            <span className="tag-fraco">{d.desc}</span>
          </label>
        ))}
        <label className="avanco-parada">
          <input
            type="checkbox"
            checked={config.sem_demissao}
            onChange={(e) => aoConfig({ sem_demissao: e.target.checked })}
          />
          Sem demissao
        </label>
        <label className="avanco-parada">
          <input
            type="checkbox"
            checked={config.investidor}
            onChange={(e) => aoConfig({ investidor: e.target.checked })}
          />
          Investidor compra o clube
        </label>
      </fieldset>
      <p className="tag-fraco">
        Salvo na hora. A dificuldade e os modificadores de uma carreira ja comecada nao mudam: sao do save.
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
        O jogo roda inteiro na sua maquina, sem internet e sem conta. O save fica no arquivo
        brasfut_save.json, na pasta do jogo, e grava sozinho ao fim de cada semana.
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
  return (
    <div className="centro-tela">
      <div className="modal" style={{ maxWidth: 680 }}>
        <h2>Escolha o clube que voce vai treinar</h2>
        <p>O mundo foi criado. A carreira so e salva depois desta escolha.</p>
        <div className="alavanca" style={{ marginBottom: 14 }}>
          {['A', 'B', 'C', 'D'].map((s) => (
            <button
              key={s}
              type="button"
              className={serie === s ? 'ativo' : ''}
              aria-pressed={serie === s}
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
