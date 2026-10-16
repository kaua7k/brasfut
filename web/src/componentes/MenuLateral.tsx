// O menu lateral: as mesmas doze telas da janela tkinter, na mesma ordem.
//
// Item de tela que ainda nao migrou fica desabilitado de verdade (<button
// disabled>), e nao apenas apagado: o teclado tem que pular por cima dele,
// senao o Tab leva a um lugar que nao existe.

import { Fragment, useEffect } from 'react'
import { porque, AGUARDE } from '../motivo'
import { ICONES_MENU, IconeAjuda, IconeMenu, IconeSalvar } from '../icones'
import { Escudo } from './Escudo'
import type { ItemMenu } from '../tipos'

interface Props {
  clube: string
  itens: ItemMenu[]
  atual: string
  aoTrocar: (id: string) => void
  aoSalvar: () => void
  /** salva e volta ao menu principal (trocar de slot) */
  aoMenu: () => void
  salvando: boolean
  aoAjuda: () => void
  /** Celular: o menu e uma gaveta por cima da tela. Aberta ou fechada. */
  aberto?: boolean
  aoFechar?: () => void
}

// Titulo do grupo que abre antes de cada item (a ordem do menu e a do jogo).
const GRUPO_ANTES: Record<string, string> = {
  painel: 'Jogo',
  tabela: 'Torneios',
  mercado: 'Clube',
  noticias: 'Imprensa',
  clube: 'Historia',
}

export function MenuLateral({
  clube,
  itens,
  atual,
  aoTrocar,
  aoSalvar,
  aoMenu,
  salvando,
  aoAjuda,
  aberto = false,
  aoFechar,
}: Props) {
  // gaveta aberta: Esc fecha, como qualquer janela por cima
  useEffect(() => {
    if (!aberto || !aoFechar) return
    const tecla = (e: KeyboardEvent) => {
      if (e.key === 'Escape') aoFechar()
    }
    window.addEventListener('keydown', tecla)
    return () => window.removeEventListener('keydown', tecla)
  }, [aberto, aoFechar])

  // escolher uma tela (ou salvar, ajuda, menu) fecha a gaveta
  const fechando = (acao: () => void) => () => {
    aoFechar?.()
    acao()
  }

  return (
    <>
    {aberto && aoFechar && (
      <button type="button" className="veu-gaveta" aria-label="Fechar o menu" tabIndex={-1} onClick={aoFechar} />
    )}
    <nav id="menu-lateral" className={`lateral${aberto ? ' aberta' : ''}`} aria-label="Telas do jogo">
      <div className="marca">
        <Escudo nome={clube} tamanho={34} />
        <div>
          <div className="marca-nome">{clube}</div>
          <div className="marca-sub">Modo Carreira</div>
        </div>
      </div>

      <div className="navlista">
        {itens.map((item) => {
          const Icone = ICONES_MENU[item.id] ?? ICONES_MENU.painel
          const ativo = item.id === atual
          return (
            <Fragment key={item.id}>
            {GRUPO_ANTES[item.id] && (
              <div className="nav-grupo" aria-hidden="true">
                <span>{GRUPO_ANTES[item.id]}</span>
              </div>
            )}
            <button
              type="button"
              className={`navitem${ativo ? ' ativo' : ''}`}
              disabled={!item.pronta}
              aria-current={ativo ? 'page' : undefined}
              // em tela estreita o menu vira so icones: o nome continua no
              // leitor de tela (aria-label) e no mouse (title)
              aria-label={item.nome}
              title={item.pronta ? item.nome : `${item.nome}: ainda so na janela do jogo`}
              onClick={fechando(() => aoTrocar(item.id))}
            >
              <Icone />
              <span className="rotulo-nav">{item.nome}</span>
            </button>
            </Fragment>
          )
        })}
      </div>

      <div className="navrodape">
        <button
          type="button"
          className="navitem"
          onClick={fechando(aoSalvar)}
          aria-label="Salvar"
          title={porque([[salvando, AGUARDE]], 'Salvar')}
          disabled={salvando}
        >
          <IconeSalvar />
          <span className="rotulo-nav">{salvando ? 'Salvando…' : 'Salvar'}</span>
        </button>
        <button type="button" className="navitem" onClick={fechando(aoAjuda)} aria-label="Ajuda" title="Ajuda">
          <IconeAjuda />
          <span className="rotulo-nav">Ajuda</span>
        </button>
        <button type="button" className="navitem" onClick={fechando(aoMenu)} aria-label="Menu principal"
        title="Salva e volta ao menu principal (trocar de slot)" disabled={salvando}>
          <IconeMenu />
          <span className="rotulo-nav">Menu principal</span>
        </button>
      </div>
    </nav>
    </>
  )
}
