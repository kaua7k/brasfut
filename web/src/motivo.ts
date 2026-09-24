// Botao desabilitado diz por que. Sem isto o jogador via "Por a venda" apagado
// e nao sabia se era regra do jogo, falta de dinheiro ou so marcar alguem.

/** O title do botao: o primeiro motivo que vale, ou a dica de sempre. */
export function porque(casos: [boolean, string][], dica?: string): string | undefined {
  const achado = casos.find(([vale]) => vale)
  return achado ? achado[1] : dica
}

export const AGUARDE = 'Aguarde: o jogo ainda esta respondendo ao ultimo pedido'
export const MARQUE = 'Marque pelo menos um jogador na lista'
