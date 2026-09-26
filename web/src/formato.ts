// Numeros e palavras do jeito que o jogo inteiro escreve.
//
// Espelho de eng.din e eng.plural (brasfut.py): quase todo dinheiro ja chega
// formatado do servidor; aqui so o que a tela soma na hora (marcados, previa
// da obra). Os dois lados tem que dar o mesmo texto para o mesmo numero.

/** "R$ 37,6 mi", "R$ 764 mil", "R$ 3.500", "-R$ 5,4 bi". */
export function dinheiro(v: number): string {
  const sinal = v < 0 ? '-' : ''
  const a = Math.abs(v)
  if (a >= 1e9) return `${sinal}R$ ${(a / 1e9).toFixed(1).replace('.', ',')} bi`
  if (a >= 1e6) return `${sinal}R$ ${(a / 1e6).toFixed(1).replace('.', ',')} mi`
  // abaixo de cem mil o arredondamento mentiria: R$ 3.500 viraria "R$ 4 mil"
  if (a >= 1e5) return `${sinal}R$ ${Math.round(a / 1000)} mil`
  return `${sinal}R$ ${Math.round(a).toLocaleString('pt-BR')}`
}

/** "1 ano", "3 anos", "2 jogadores". Nunca "ano(s)". */
export function plural(n: number, singular: string, plural?: string): string {
  return `${n} ${n === 1 ? singular : (plural ?? `${singular}s`)}`
}

/** Itens em grupos, na ordem em que cada grupo aparece pela primeira vez
 * (para <optgroup> nos seletores de torneio). */
export function agrupar<T extends { grupo: string }>(itens: T[]): [string, T[]][] {
  const grupos = new Map<string, T[]>()
  for (const item of itens) {
    const lista = grupos.get(item.grupo)
    if (lista) lista.push(item)
    else grupos.set(item.grupo, [item])
  }
  return [...grupos.entries()]
}
