# Three Amigos Meeting — Rodada de melhorias do BRASFUT

**Data**: 2026-09-24
**Fonte**: pedido do usuario (texto livre) + tres auditorias (UX/UI visual, funcional/bugs, game design)
**Participantes**: business-analyst, product-manager, qa-strategist (plugins bnp); principal software engineer, UX designer e design director (agentes gerais no papel — os agentes de plugin nao sobem no Claude Code)

## 1. Resumo da tarefa
Decidir e priorizar melhorias de jogabilidade, interface, mecanicas e bugs do BRASFUT sem deixar o jogo perceptivelmente mais lento. Insumo: 28 achados visuais, 12 bugs confirmados + suspeitas + perfil de desempenho, e diagnostico de game design com simulacoes.

## 2. Consenso

### 2.1 O que fazer
**Onda 1 — agora (custo de desempenho ~zero ou negativo)**
1. Bug do livre acertado roubado pela IA (ver decisao D1).
2. Posse: guard unico na API (`j["clube"] == G["clube"]`, `pid in base_elenco`, `dono == meu`) em rescindir, base/subir, base/liberar, elenco/chamar, treino/foco — erro 400 visivel, sem mudar estado. Hoje da para rescindir jogador de rival descontando a multa do caixa dele.
3. `assumir_clube` limpa `vagas_manuais`, foco de treino, peneira e candidatos do clube que o tecnico deixa (a IA herdava as vagas fixadas).
4. Validade de proposta de emprego e de candidato da peneira por contador absoluto de semanas (hoje `semana` fica 0 no estadual e elas duram ~20 semanas).
5. Textos mentirosos: "Serie ENG/USA" no resumo e na abertura; "rebaixamento demite" na Serie D; "teto teto ~75"; erro "None" no emprestimo de livre; "na quartas" em `campanha_estadual`; entrada malformada vira 400, nao 500.
6. Barra de forcas do proximo jogo: comparar "seu ataque x defesa dele" e "sua defesa x ataque dele" (hoje compara ataque com ataque e engana); forca do rival com a competicao certa.
7. Desempenho: dois memos exatos (atribuir_vagas/forcas_de com chave que inclui cond/forma/moral; linha de vagas repetidas no montar_escalacao) — medido -23% por semana com saida identica.
8. Layout estrutural (ver D3): topo sem esconder CAIXA (trocar `nth-of-type` por classe por chip), Painel sem altura fixa (uma rolagem por pagina, fim do scroll duplo e da sobreposicao), barra de acoes presa sem vazar linhas, grade do Elenco com scroll horizontal proprio, Financas alinhada.
9. Acessibilidade basica (custo zero): V/E/D e zonas da tabela com letra/rotulo, nao so cor; legenda para as cores de nome de jogador; aria-label/title no menu so de icones; foco de teclado na linha do Elenco e instrucao igual ao gesto; botao desabilitado diz o motivo; contraste de borda de controle 3:1; reduced-motion completo.
10. Linguagem e numeros: glossario unico (Classificacao no menu e no titulo; "Pos" e "Pts", nunca "P"); formatador unico de dinheiro pt-BR ("R$ 37,6 mi"); "(s)" trocado por plural certo; Mercado e Painel mostram cada dado uma vez; "Athletic" com o pais/liga ao lado.

**Onda 2 — proximo**
11. Tela da partida: resumo compacto na volta do avanco (placar mandante primeiro, gols e cartoes com minuto, posse, chutes, melhor em campo), sem clique extra obrigatorio; "Ver detalhes" com notas e substituicoes. Guardar historico curto das partidas do meu clube e normalizar as chaves de `notas` (int vira str no save).
12. Tokens de CSS: escala de no maximo 6 tamanhos de fonte, cores por token, fim dos hex soltos e dos ~110 estilos inline — depois da Onda 1 e com baseline visual.
13. Somar `nota_soma` (media de nota) e premios do ano/selecao.
14. Confianca da diretoria semanal com causa e tendencia ("-3: derrota no classico"), aviso antes de demitir; a IA tambem demite tecnico (e alimenta as propostas).
15. Instrucoes condicionais pre-jogo ("se perdendo aos 60', ofensivo") no lugar do intervalo interativo: a decisao pesa, custo O(1), sem pausar o jogo.

**Onda 3 — depois**
16. Spike de arquitetura do intervalo interativo (G: simular vira maquina de estados, save no meio do jogo).
17. IA com identidade tatica e rebalanceamento das taticas (Retranca domina por construcao: produto at x de 1,105 contra 0,951 da Pressao) — rebaixado pela decisao D2.
18. Moral com causa, classico com peso, economia com escolhas (socio, patrocinio, bicho, emprestimo), entrosamento, mercado disputado/pre-contrato, olheiros e lista de observacao, Copinha e convocacoes, historia do clube.

### 2.2 Por que
O que mais corroi o jogo hoje e desconfianca: o sistema desobedece as proprias regras (livre roubado, posse, janela assimetrica) e a interface diz coisas falsas ou ambiguas (Serie USA, "P", barra de forcas, rebaixamento na D). Isso vem antes de qualquer mecanica nova, porque mecanica nova sobre leitura ambigua empilha incerteza. Depois, o maior ganho de valor por custo e mostrar a partida, que o motor ja calcula e a web esconde.

### 2.3 Como
- Motor e API: guard de posse na camada de rotas; regra da janela unica; contador absoluto de semanas no save (migracao simples); limpeza em `assumir_clube`.
- Desempenho: memos exatos validados por harness de hash/saida com seed fixa; nada que mude a regra do rodizio (a semana continua no `esc_stamp`; salvar em thread foi descartado — 79 ms medidos e risco de corromper o save).
- Interface: correcoes estruturais de layout antes de tokens; baseline de capturas (Edge headless) recriada depois dos fixes.
- Commits separados: bugs, desempenho e interface em PRs/commits distintos, cada um com seu gate.

### 2.4 Como garantir
- Testes de regressao para cada bug (API in-process, save protegido).
- Harness de desempenho: saida byte-identica em 3 seeds x 20 semanas para os memos; semana de liga <= 0,6 s e com copa europeia <= 2,1 s.
- Capturas em 1280x720, 1366x768, 1440x900, 1920x1080 e 2560x1440 sem corte, sem scroll horizontal e sem sobreposicao nas telas principais.
- Lint de textos: zero "Serie ENG", zero "mi" com ponto, zero "(s)", termo unico por conceito.
- Suite lenta de balanceamento (5-10 temporadas): numero de 85+ estavel, gols 2,4-2,9, caixa sem disparar.

## 3. Criterios de aceite
- **Livre**: Dado um agente livre, Quando eu ou a IA oferecemos contrato em qualquer semana, Entao a assinatura vale na hora para quem fechou primeiro, e ninguem assina com quem ja esta acertado com outro clube.
- **Posse**: Dado um jogador de outro clube, Quando chamo rescindir, subir, liberar, chamar ou foco, Entao a API devolve erro de uso, o caixa e o jogador nao mudam, e a tela mostra o motivo.
- **Troca de clube**: Dado que aceito proposta ou sou demitido, Quando assumo o clube novo, Entao o clube antigo fica sem vagas fixadas, foco de treino e peneira meus.
- **Validade**: Dada uma proposta criada no estadual, Quando passam 6 semanas de jogo, Entao ela vence.
- **Forcas**: Dado o proximo jogo, Quando vejo a barra, Entao ela compara meu ataque com a defesa dele (e vice-versa) e a cor bate com a vantagem esperada.
- **Memos**: Dada a seed fixa, Quando comparo antes e depois em 3 seeds x 20 semanas, Entao toda a saida e identica e a semana cai >= 15%.
- **Layout**: Dadas as telas de 1280x720 a 2560x1440, Quando abro Painel, Elenco, Mercado, Escalacao e Financas, Entao CAIXA, nome do clube, semana e "Avancar semana" aparecem inteiros, ha uma rolagem por pagina e nada se sobrepoe.
- **Acessibilidade**: Dado o jogo em escala de cinza ou so no teclado, Quando jogo uma semana, Entao entendo V/E/D e zonas e alcanco todas as acoes; todo desabilitado diz o motivo.
- **Linguagem**: Dado qualquer valor em dinheiro, Quando aparece em qualquer tela, Entao segue "R$ 37,6 mi"; o menu e o titulo da tela usam o mesmo nome.
- **Partida (Onda 2)**: Dada uma semana com jogo, Quando o avanco termina, Entao vejo o resumo da partida sem chamada extra de API e sem clique a mais, e as notas sobrevivem a salvar e carregar.

## 4. Riscos
| Risco | Tipo | Severidade | Mitigacao |
|------|------|----------|------------|
| Memo com chave incompleta muda resultado sem mudar o hash agregado | Tecnico | Alta | Comparar saida completa em 3 seeds x 20 semanas, nao so hash |
| Livres a qualquer momento esvaziam a janela e mudam o mercado da IA | Balanceamento | Media | IA com limite semanal de contratacoes de livres e prioridade para quem precisa; medir livres disponiveis por semana |
| Correcoes de CSS regridem outras telas | Visual | Media | Baseline de capturas antes/depois; commits pequenos |
| Guard de posse bloqueia o dono certo (emprestados, base) | Funcional | Media | Testes cobrindo emprestado para mim, emprestado por mim e base |
| Contador absoluto de semanas quebra save antigo | Dados | Baixa | Migracao em `migrar` com valor derivado de temporada/semana |
| Tela da partida aumenta o save | Desempenho | Baixa | Historico curto (ultimas N partidas do meu clube) |

## 5. Perguntas em aberto
- Tamanho do historico de partidas guardado (sugestao: 10 ultimas).
- Limite semanal de livres contratados pela IA com a regra nova.
- Cor da acao primaria (o amarelo passa a significar so "atencao"?) — proposta do Design Director, a confirmar na Onda 2.

## 6. Divergencias resolvidas
| Ponto | Posicoes | Decisao |
|------|------|------|
| D1 Livre fora da janela | Eng: regra unica, aberta ou fechada; Negocio: documentar | **Usuario: qualquer um assina a qualquer momento, IA e jogador** (livre ja saiu do clube, como na vida real) |
| D2 Automatico vencendo sozinho | Produto/Design: defeito, rebalancear antes da IA tatica; UX: e balanco | **Usuario: e conforto, fica como esta** — IA tatica e rebalanceamento vao para a Onda 3 |
| D3 Largura minima | UX: 1000 + 800 degradado; Design: 1000 ou 800 | **Usuario: funcional em notebook, monitor e telas grandes** (1280x720 ate 2560x1440) |
| D4 Acentos | Design: so texto exibido; Eng: so TSX agora | **Usuario: sem acentos** — item retirado; numeros pt-BR continuam |
| Tela da partida por padrao | UX/Produto/Design | Resumo compacto sem clique extra + "Ver detalhes" |
| Intervalo interativo | Negocio/UX (P1) x Eng/Design (G, depois) | Depois, com spike; agora instrucoes condicionais pre-jogo |
| Tokens CSS antes do layout | Produto x Eng/UX | Layout estrutural primeiro, tokens na Onda 2 |
| A11y basica | Produto (proximo) x QA/Design/UX (agora) | Agora — custo zero, daltonismo ~8% |
| Tirar semana do esc_stamp / salvar em thread | Auditoria x Eng | Descartados (mudam regra / mais lentos) |
| Posse ALTA ou MEDIA | QA x Negocio/Produto | ALTA — integridade, rescisao desconta caixa do rival |
| "Ultimos 5" x "tres vitorias" | Design/UX suspeitavam de bug | Nao e bug (ordem antiga->recente); falta seta e contagem real |

## 7. Dependencias
- Memos de desempenho antes de qualquer mecanica nova que rode no loop de simulacao.
- Baseline visual so depois das correcoes de layout.
- Tela da partida depende de guardar historico e normalizar as chaves de `notas`.
- Premios dependem de `nota_soma` somada (com migracao de save).

## 8. Proximos passos
1. Implementar a Onda 1 em tres commits: (a) bugs e regras (livres, posse, troca de clube, validade, textos, forcas), (b) desempenho (memos com harness), (c) interface (layout, acessibilidade, linguagem e numeros).
2. Rodar as guardas (testes, harness de desempenho, capturas em 5 resolucoes) e medir livres por semana com a regra nova.
3. Iniciar a Onda 2 pela tela da partida.

## 9. Veredito
**Sim, pronto para desenvolvimento a Onda 1.** Escopo, regras e criterios estao definidos e as quatro divergencias foram decididas pelo usuario. A Onda 2 esta clara o suficiente para comecar depois; a Onda 3 precisa de spike (intervalo) e de nova rodada de balanceamento.
