# Onda 2 — escopo e decisoes

**Data**: 2026-09-25
**Base**: ata `2026-09-24-rodada-de-melhorias.md` (itens 11-15) + leitura do codigo no commit `26e90a8`
**Branch**: `melhorias/onda-2`

## 1. Estado do codigo que muda o plano
- A partida ja existe inteira em `G["ultimos_meus"]` (eventos, stats, notas, subs, xi — retorno de `simular`). A web so recebe uma linha de texto de `relato()` em `api/avanco.py`. O resumo compacto sai enriquecendo esse retorno, sem chamada extra.
- `notas` tem chave int (pid) que vira str no save; `eventos` sao tuplas que voltam como listas.
- `nota_soma` existe no jogador (`novo_jogador`) mas **nunca e somado** — hoje nao ha media de nota.
- Diretoria: so o sorteio de fim de ano em `avaliar_diretoria`. Nao ha confianca semanal nem demissao de tecnico da IA.
- `simular` ja roda em tres periodos com paradas aos 45' e 70' — ponto natural das instrucoes condicionais.
- Web: 70 hex soltos e ~110 `style={{}}` (29 no Painel).

## 2. Decisoes do usuario (2026-09-25)
| Ponto | Decisao |
|---|---|
| Tamanho do historico de partidas | **10 ultimas** do meu clube, formato compacto |
| Quando a diretoria pode demitir | **Qualquer semana apos o aviso** (aviso abaixo de 30; abaixo de 15 depois de avisado, pode demitir na semana seguinte) |
| Instrucoes condicionais | **IA tambem usa, com regra fixa** (perdendo: ofensiva; vencendo: recua). Exige suite de balanceamento, ver 4 |
| Tokens de CSS | **Antes** das telas novas — elas ja nascem nos tokens |
| "Premios do ano/selecao" | Interpretado como **selecao do campeonato** (melhor XI por posicao), nao selecao nacional |

## 3. Ordem de execucao (um commit por item)
1. **Tokens de CSS** + baseline de capturas (Edge headless, 5 resolucoes). Decidir a cor da acao primaria (amarelo so "atencao"?) no inicio deste item.
2. **Dados da partida**: normalizar chaves de `notas` (str) e `eventos`; `G["historico_meus"]` com as 10 ultimas em formato compacto; somar `nota_soma` em `simular`; migracao em `migrar`.
3. **Resumo da partida** na volta do avanco (mandante primeiro, gols/cartoes com minuto, posse, chutes, melhor em campo) + "Ver detalhes" (notas, substituicoes) + historico clicavel no Painel.
4. **Instrucoes condicionais**: ate duas regras (se perdendo / se vencendo) trocando ritmo, pressao ou linha a partir do 46' ou 71'; evento aparece no resumo. IA com regra fixa.
5. **Confianca da diretoria**: 0-100 no save; delta semanal = resultado x esperado pela forca (classico peso 2) + posicao x objetivo + caixa; tendencia = soma das ultimas 4; dificuldade multiplica os deltas. IA avalia em marcos (fim de turno/estadual/temporada), demite, gera manchete e alimenta propostas de emprego.
6. **Premios do ano**: melhor jogador (media de nota, minimo de jogos), artilheiro, revelacao (ate 21), selecao do campeonato. Na virada, com manchete, historico no jogador e pequeno ganho de valor.

## 4. Guardas
- `cd testes && python -m unittest -v` verde em todo commit; teste de regressao por item.
- Itens 2, 3, 5 e 6 **nao consomem `rng`**: harness de 3 seeds x 20 semanas continua byte-identico.
- Item 4 muda resultados de proposito (IA usa condicionais): no lugar do harness identico, rodar a suite lenta de balanceamento (5-10 temporadas) — gols 2,4-2,9 por jogo, numero de 85+ estavel, caixa sem disparar — e comparar antes/depois.
- Desempenho: semana de liga <= 0,6 s, com copa europeia <= 2,1 s.
- Save: historico compacto (~2 KB/jogo, ~20 KB no total); save antigo carrega via `migrar`.

## 5. Ainda em aberto
- Cor da acao primaria (resolver no item 1).
- Limite semanal de livres contratados pela IA (herdado da Onda 1, fora desta onda).
