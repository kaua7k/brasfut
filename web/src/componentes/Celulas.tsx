// As celulas de jogador que toda lista repete: posicao, overall e fisico.
//
// Sao funcoes que devolvem <span> com o numero como texto, e nao componentes:
// a Grade ordena lendo o texto da celula (textoDe), e um componente proprio
// esconderia o valor dentro das props.

// a linha do campo pela posicao principal ("ZAG/LAT" conta como ZAG)
// zagueiro e lateral, volante e meia: mesma familia de cor, tons diferentes
const LINHA: Record<string, string> = { GOL: 'gol', ZAG: 'def', LAT: 'lat', VOL: 'vol', MEI: 'mei', ATA: 'ata' }

/** "ATA" num selo com a cor da linha do campo. */
export function seloPos(pos: string) {
  return <span className={`selo-pos ${LINHA[pos.split('/')[0].trim().toUpperCase()] ?? ''}`}>{pos}</span>
}

/** O overall num selo com as faixas da cor do nome (dto._tag_ovr e a LegendaCores):
 *  roxo 80+, verde 70 a 79, branco 55 a 69, cinza abaixo de 55. */
export function seloOvr(ovr: number) {
  const faixa = ovr >= 80 ? 'elite' : ovr >= 70 ? 'bom' : ovr >= 55 ? 'medio' : 'fraco'
  return <span className={`selo-ovr ${faixa}`}>{ovr}</span>
}

/** A bracadeira: um "C" dourado ao lado do nome do capitao. */
export function seloCapitao() {
  return <span className="selo-capitao" title="Capitao" aria-label="Capitao">C</span>
}

/** Meio da faixa do olheiro: "74-80" vira 77, "~75" vira 75, outra coisa vira null. */
export function meioDoTeto(teto: string): number | null {
  const n = teto.match(/\d+/g)?.map(Number) ?? []
  if (n.length === 0) return null
  return n.length === 1 ? n[0] : (n[0] + n[1]) / 2
}

/** Potencial em cinco estrelas a partir do teto estimado (55 ou menos = 1, 90+ = 5). */
export function estrelasDoTeto(teto: string) {
  const meio = meioDoTeto(teto)
  if (meio === null) return null
  const cheias = Math.max(1, Math.min(5, Math.round((meio - 55) / 8) + 1))
  return (
    <span className="estrelas" title={`potencial estimado ${teto}`} aria-label={`${cheias} de 5 estrelas`}>
      <span className="estrelas-cheias">{'★'.repeat(cheias)}</span>
      <span className="estrelas-vazias">{'★'.repeat(5 - cheias)}</span>
    </span>
  )
}

/** Condicao fisica: barrinha e o numero. Abaixo de 45 critico, de 65 atencao. */
export function barraFisico(cond: number) {
  const estado = cond < 45 ? 'critico' : cond < 65 ? 'atencao' : 'ok'
  return (
    <span className={`fisico ${estado}`}>
      <span className="fisico-barra" aria-hidden="true">
        <span style={{ width: `${Math.max(0, Math.min(100, cond))}%` }} />
      </span>
      {cond}
    </span>
  )
}
