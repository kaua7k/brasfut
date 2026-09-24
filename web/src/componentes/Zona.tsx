// A zona da tabela (G4, acesso, rebaixamento, mata-mata) com forma e texto,
// nao so com cor: ~8% dos homens nao separam o verde do vermelho, e a linha do
// meu clube pintava a faixa de dourado e escondia a zona de vez.

const FORMA: Record<string, string> = { alta: '▲', baixa: '▼', media: '◆' }

interface ComZona {
  zona: string
  zona_texto?: string | null
}

export function MarcaZona({ zona, texto }: { zona: string; texto?: string | null }) {
  if (!zona) return <i className="marca-zona" aria-hidden="true" />
  return (
    <i className={`marca-zona ${zona}`} title={texto ?? undefined} role="img" aria-label={texto ?? zona}>
      {FORMA[zona]}
    </i>
  )
}

/** "▲ G4 · ▼ rebaixamento", com as zonas que aparecem nestas linhas. */
export function LegendaZonas({ linhas }: { linhas: ComZona[] }) {
  const vistas = new Map<string, string>()
  for (const l of linhas) {
    if (l.zona && l.zona_texto && !vistas.has(l.zona)) vistas.set(l.zona, l.zona_texto)
  }
  if (vistas.size === 0) return null
  return (
    <div className="legenda-zonas">
      {[...vistas].map(([zona, texto]) => (
        <span key={zona}>
          <MarcaZona zona={zona} texto={texto} /> {texto}
        </span>
      ))}
    </div>
  )
}
