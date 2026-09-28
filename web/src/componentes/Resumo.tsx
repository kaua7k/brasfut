// O fim do ano em uma tela: o que ganhou, onde parou em cada campeonato que
// jogou, e quanto sobrou.
//
// Abre sozinho logo depois da virada - antes ate da escolha de clube novo,
// porque ninguem entende uma demissao sem ver a temporada que a causou. Com a
// temporada encerrada e a virada ainda esperando o clique, a mesma tela mostra
// a previa: o que ja esta fechado, e o aviso do que so se decide na virada.

import { useEffect, useRef } from 'react'
import type { ResumoTemporada } from '../tipos'

interface Props {
  resumo: ResumoTemporada
  /** texto do botao que fecha: muda conforme o que vem depois */
  rotuloFechar: string
  aoFechar: () => void
}

export function Resumo({ resumo, rotuloFechar, aoFechar }: Props) {
  // o foco vai para a janela sem rolar: com autoFocus no botao de baixo ela
  // abria rolada ate o fim e o titulo (a posicao final) ficava escondido
  const caixa = useRef<HTMLDivElement>(null)
  useEffect(() => {
    caixa.current?.focus({ preventScroll: true })
  }, [])
  return (
    <div
      className="fundo-modal"
      role="dialog"
      aria-modal="true"
      aria-label={resumo.titulo}
      onKeyDown={(e) => e.key === 'Escape' && aoFechar()}
    >
      <div className="modal modal-largo modal-resumo" ref={caixa} tabIndex={-1}>
        <h2>
          {resumo.titulo}
          {resumo.previa && <span className="tag-fraco"> · previa</span>}
        </h2>
        <div className="mesa-sub">{resumo.subtitulo}</div>

        {resumo.conquistas.length > 0 ? (
          <div className="resumo-conquistas" aria-label="Conquistas do ano">
            {resumo.conquistas.map((c) => (
              <div key={c.nome} className={`resumo-conquista ${c.tipo}`}>
                <span className="icone" aria-hidden="true">
                  {c.tipo === 'titulo' ? '★' : '▲'}
                </span>
                <div>
                  <div className="tipo">{c.tipo === 'titulo' ? 'Campeao' : 'Acesso'}</div>
                  <div className="nome">{c.nome}</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="resumo-sem-titulo">Nenhum titulo nesta temporada.</div>
        )}

        <div className="resumo-vereditos">
          {resumo.vereditos.map((v) => (
            <div key={v.texto} className={`resumo-veredito ${v.estado}`}>
              {v.texto}
            </div>
          ))}
        </div>

        {resumo.campanhas.length > 0 && (
          <section className="resumo-campanhas">
            <div className="painel-titulo">Seus campeonatos</div>
            <table>
              <tbody>
                {resumo.campanhas.map((c) => (
                  <tr key={c.nome} className={c.titulo ? 'titulo' : ''}>
                    <td>
                      {c.titulo && <span aria-hidden="true">★ </span>}
                      {c.nome}
                    </td>
                    <td className={c.titulo ? '' : `tag-${c.estado}`}>{c.resultado}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}

        <div className="resumo-tiles">
          {resumo.tiles.map((t) => (
            <div className="resumo-tile" key={t.nome}>
              <div className="plano-nome">{t.nome}</div>
              <div className={`resumo-valor tag-${t.estado}`}>{t.valor}</div>
              <div className="tag-fraco resumo-sub">{t.sub}</div>
            </div>
          ))}
        </div>

        <div className="resumo-secoes">
          {resumo.secoes.map((s) => (
            <section key={s.titulo}>
              <div className="painel-titulo">{s.titulo}</div>
              <ul>
                {s.itens.map((i, k) => (
                  <li key={k} className={`tag-${i.estado}`}>
                    {i.texto}
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>

        <div className="modal-acoes">
          <span className="resumo-mesa">{resumo.nota}</span>
          <button type="button" className="bt-acao bt-media" onClick={aoFechar}>
            {rotuloFechar}
          </button>
        </div>
      </div>
    </div>
  )
}
