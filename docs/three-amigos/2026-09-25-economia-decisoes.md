# Economia do clube — diagnostico e decisoes

**Data**: 2026-09-25
**Base**: levantamento do motor (formulas de receita, custo, mercado), levantamento da interface web e uma temporada medida em 18 clubes (Series A-D, Inglaterra, Portugal).

## 1. Diagnostico

**Medido em uma temporada**
- Todo clube lucra: os 18 terminaram com mais caixa (Flamengo +R$ 160 mi, Porto Velho da Serie D +R$ 2,4 mi). A economia nao aperta ninguem.
- Bilheteria domina: Flamengo R$ 120 mi de ingresso contra R$ 70 mi de TV; Santa Cruz (Serie D) R$ 25 mi de ingresso contra R$ 4,7 mi de receita fixa.
- IA contra IA paga em media 1,37x o valor de mercado; comprando do usuario, so perto do valor. O mesmo jogador tem dois mercados.

**Nao existe**
- Patrocinio: "TV e patrocinio" e uma constante por serie e reputacao (`TV`, `receita_semanal`).
- Premiacao prevista; nas copas so o campeao recebe (nada por fase, nada para o vice).
- Valor do elenco; socios (gerados, sem efeito); juros ou divida.

**Errado**
- Salario de contrato apagado: `aplicar_evolucao` e `evoluir_jogadores` fazem `salario = salario_devido(j)` a cada mudanca de overall e na virada. Renovacao, contratacao, corte de rebaixamento e saneamento somem.
- Extrato do ano nao fecha: bilheteria dentro de "receita" e mostrada como parcela separada; premio do estadual some; premios de copa e de grupo, obras, infra, peneira, multas e taxas de emprestimo nao sao registrados.
- Mercado nao mostra valor de mercado na busca nem na mesa de compra.
- Estadio nao mostra publico, ocupacao, renda media nem o custo fixo de ampliar; preco inicial do ingresso abaixo do otimo.

## 2. Decisoes do usuario

| Ponto | Decisao |
|---|---|
| Patrocinio | **Contratos reais**: master e uniforme com valor, prazo e bonus por meta; 2-3 propostas na pre-temporada para escolher; valor cresce com reputacao e campanha |
| Salario | **Fixo pelo contrato**: so muda ao contratar ou renovar; quem evolui pede aumento na renovacao |
| Balanceamento | **Rebalancear com medicao**: bilheteria realista por divisao, custos que apertam quem gasta mal, premiacao por fase nas copas e para o vice; grande lucra pouco, pequeno vive no limite, gastar demais da prejuizo |
| Ordem | **Economia antes** dos premios individuais do ano (item 6 da Onda 2) |

## 3. Entregas (uma PR cada, merge na main)

1. **Informacao e extrato** (sem mudar numero do jogo): extrato por categoria que fecha com o caixa; Financas detalhada; valor de mercado na busca e na mesa; valor do elenco; publico, ocupacao e renda no Estadio; "Folha/mes" no topo.
2. **Salario fixo pelo contrato** e renovacao que parte do salario de mercado do overall atual.
3. **Patrocinio** master e de uniforme como contratos; propostas na pre-temporada; IA fecha automaticamente.
4. **Rebalanceamento** de bilheteria, custos e premiacao, calibrado junto com o patrocinio.

## 4. Guardas
- Entrega 1: harness `desempenho.py` com saida identica (so registra).
- Entregas 2 a 4: `testes/balanceamento.py` e a medicao de temporada por clube (receita, bilheteria, premio, folha, estrutura, saldo) antes e depois.
