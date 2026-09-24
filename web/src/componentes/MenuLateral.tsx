// O menu lateral: as mesmas doze telas da janela tkinter, na mesma ordem.
//
// Item de tela que ainda nao migrou fica desabilitado de verdade (<button
// disabled>), e nao apenas apagado: o teclado tem que pular por cima dele,
// senao o Tab leva a um lugar que nao existe.

import { porque, AGUARDE } from '../motivo'
import { ICONES_MENU, Estrela, IconeAjuda, IconeSalvar } from '../icones'
import type { ItemMenu } from '../tipos'

interface Props {
  clube: string
  itens: ItemMenu[]
  atual: string
  aoTrocar: (id: string) => void
  aoSalvar: () => void
  salvando: boolean
}

export function MenuLateral({ clube, itens, atual, aoTrocar, aoSalvar, salvando }: Props) {
  return (
    <nav className="lateral" aria-label="Telas do jogo">
      <div className="marca">
        <div className="escudo"><Estrela /></div>
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
            <button
              key={item.id}
              type="button"
              className={`navitem${ativo ? ' ativo' : ''}`}
              disabled={!item.pronta}
              aria-current={ativo ? 'page' : undefined}
              // em tela estreita o menu vira so icones: o nome continua no
              // leitor de tela (aria-label) e no mouse (title)
              aria-label={item.nome}
              title={item.pronta ? item.nome : `${item.nome}: ainda so na janela do jogo`}
              onClick={() => aoTrocar(item.id)}
            >
              <Icone />
              <span className="rotulo-nav">{item.nome}</span>
            </button>
          )
        })}
      </div>

      <div className="navrodape">
        <button
          type="button"
          className="navitem"
          onClick={aoSalvar}
          aria-label="Salvar"
          title={porque([[salvando, AGUARDE]], 'Salvar')}
          disabled={salvando}
        >
          <IconeSalvar />
          <span className="rotulo-nav">{salvando ? 'Salvando…' : 'Salvar'}</span>
        </button>
        <button type="button" className="navitem" disabled aria-label="Ajuda" title="Ajuda: ainda so na janela do jogo">
          <IconeAjuda />
          <span className="rotulo-nav">Ajuda</span>
        </button>
      </div>
    </nav>
  )
}
