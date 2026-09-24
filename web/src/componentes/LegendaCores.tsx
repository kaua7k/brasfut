// O que a cor do nome do jogador quer dizer (a escada de _tag_ovr, api/dto.py).
// Sem legenda a cor era enigma para quem via e invisivel para quem nao via.

export function LegendaCores({ critico }: { critico?: string }) {
  return (
    <div className="legenda-cores">
      <span>Cor do nome pelo overall:</span>
      <span className="tag-top">roxo 80+</span>
      <span className="tag-ok">verde 70 a 79</span>
      <span>branco 55 a 69</span>
      <span className="tag-fraco">cinza abaixo de 55</span>
      {critico && <span className="linha-critica">linha vermelha: {critico}</span>}
    </div>
  )
}
