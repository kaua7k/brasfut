// Valor em reais digitado a mao: so digitos, com o ponto de milhar aparecendo
// enquanto se digita. "3350000" vira "3.350.000" - ninguem conta zeros.

interface Props {
  valor: number
  aoMudar: (v: number) => void
  rotulo: string
  /** "%" em vez de "R$": a mesma caixa serve a fatia do salario. */
  unidade?: 'R$' | '%'
  maximo?: number
  id?: string
}

export function CampoDinheiro({ valor, aoMudar, rotulo, unidade = 'R$', maximo, id }: Props) {
  return (
    <label className="campo-dinheiro">
      <span className="plano-nome">{rotulo}</span>
      <span className="campo-dinheiro-caixa">
        <span className="unidade" aria-hidden="true">{unidade === 'R$' ? 'R$' : ''}</span>
        <input
          id={id}
          className="seletor entrada-dinheiro"
          inputMode="numeric"
          value={valor ? valor.toLocaleString('pt-BR') : ''}
          placeholder="0"
          aria-label={`${rotulo}${unidade === '%' ? ' em porcentagem' : ' em reais'}`}
          onChange={(e) => {
            let v = Number.parseInt(e.target.value.replace(/\D/g, '') || '0', 10)
            if (maximo !== undefined) v = Math.min(v, maximo)
            aoMudar(v)
          }}
        />
        {unidade === '%' && <span className="unidade" aria-hidden="true">%</span>}
      </span>
    </label>
  )
}
