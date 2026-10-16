# Mapa do projeto — BRASFUT

> **Para quem (Claude Code) for trabalhar neste repo**: leia este arquivo
> primeiro. Ele existe pra evitar reler `brasfut.py` (10k linhas) e
> `brasfut_app.py` (4,5k linhas) inteiros toda vez. Abra os arquivos-fonte só
> na faixa de linha indicada abaixo para a sua tarefa. Ao terminar um
> trabalho que muda estrutura, adiciona arquivo, fecha um item do roadmap ou
> descobre algo que devia estar aqui, **edite a seção correspondente deste
> mapa** (não regenere o arquivo inteiro) — é assim que ele se paga.

Última atualização: 2026-10-16 · commit de referência: `4fd318b` (+ Copinha e convocações)

## O que é

BRASFUT é um simulador de carreira de técnico de futebol brasileiro
(campeonatos estaduais, Brasileirão, copas nacionais e continentais,
mercado de transferências, base, treino). Projeto pessoal do Kauã, em
GitHub (`kaua7k/brasfut`). Nasceu como jogo de terminal, ganhou uma janela
desktop (tkinter) e está migrando para interface web (React + TypeScript no
front, `http.server` da stdlib no back). **O motor (`brasfut.py`) é o
mesmo para as três interfaces** — não sabe que existe tela.

Doc de regras do jogo (não arquitetura): `COMO-JOGAR.md`.
Doc de arquitetura da migração web (bem mais detalhado que este mapa nessa
parte): `ARQUITETURA-WEB.md` — leia-o antes de mexer em `api/` ou `web/`.
Atas de decisão de roadmap: `docs/three-amigos/`.

## Mapa de arquivos

| Arquivo / pasta | Tamanho | O que é | Quando abrir |
|---|---|---|---|
| `brasfut.py` | 13273 linhas | O motor inteiro + a interface de terminal original (`main()`, `loop()`, `tela_*`) | Só a faixa de linha da seção que precisa (ver índice abaixo) |
| `brasfut_app.py` | 4552 linhas | Janela desktop (tkinter). Uma classe `Dialogo` por tela/ação | Só se a tarefa for na janela desktop — a maioria do trabalho novo vai para a web |
| `dados_mundo.py` | 1181 linhas | Dados estáticos: clubes, ligas, seleções, nomes | Ao adicionar/corrigir liga, clube ou país |
| `dados_clubes.py` | ~420 linhas | História real dos clubes brasileiros até 2025 (fundação, apelido, cidade, títulos com ano, soma do estadual) e `ESCUDOS` (cores, padrão e sigla do escudo genérico de ~100 clubes). Editável à mão; só aparência | Ao corrigir um título, uma cor ou incluir um clube |
| `server.py` | 156 linhas | `http.server` da stdlib; serve a API e `web/dist` | Infra do servidor, não regra de jogo |
| `api/rotas.py` | ~350 linhas | `URL -> função`. Todas as rotas HTTP registradas com `@rota(metodo, caminho)` | Para achar/adicionar um endpoint |
| `api/sessao.py` | — | Mantém o `G` vivo em memória, salva, dono do `threading.RLock`. Três slots de save (`caminho_slot`, `usar_slot`, `slots`; o slot 1 é o `brasfut_save.json`), e o motor grava um `.resumo` pequeno ao lado de cada save para o menu | Concorrência, save, trava de sessão |
| `api/dto.py` | — | Traduz `G` no formato de cada tela (uma função por tela) | Ao mudar o que uma tela recebe |
| `api/mercado.py` | — | Mesa de negociação e regras de mercado do lado da API (maior arquivo de `api/`) | Compra/venda/empréstimo/renovação na web |
| `api/competicoes.py` | — | Estaduais, séries, copas e a Copinha (`_copinha`, alvo `copinha`) — montagem e leitura pela API | Telas de Classificação/Competições |
| `api/avanco.py` | — | Avançar em ritmos (jogo/semana/mês/janela/temporada) | Botão *Avançar*/*Simular* |
| `api/campo.py` | — | Vaga (GOL, ZAG...) → ponto no campo, para as formações | Desenho do campo na Escalação |
| `api/navegador.py` | — | Modo navegador (versão do celular): `pedido(metodo, caminho, corpo_json)` para o Web Worker do Pyodide, sobre o mesmo `rotas.despachar`; `iniciar(pasta)` aponta o save para o IndexedDB; `medir(N)` = carreira de teste fora do save (`test_navegador.py`) | Versão do celular, medição de desempenho no navegador |
| `web/src/telas/*.tsx` | 16 arquivos | Uma tela por arquivo (Painel, Elenco, Escalação, Mercado, Financas, Clube, Estatísticas, etc.) | Ao mexer numa tela específica |
| `web/src/componentes/*.tsx` | 24 arquivos (`Ajuda.tsx`: ajuda e boas-vindas; `Partida.tsx`: resumo e detalhe da partida; `AoVivo.tsx`: a partida lance a lance, relógio e lances no minuto; `Intervalo.tsx`: o jogo parado aos 45', mentalidade e trocas; `DialogoRenovar.tsx`: renovação em lote; `Celulas.tsx`: selo de posição, selo de overall e barra de físico das listas; `Resumo.tsx`: resumo da temporada; `Escudo.tsx`: escudo SVG de cada clube pelo nome, com o mapa de `/api/escudos`; `Plantao.tsx`: boletim do modo caos) | Diálogos e peças reusáveis (Mesa, Grade, Campo, Ficha...) | Componente compartilhado entre telas |
| `web/src/api.ts`, `tipos.ts`, `formato.ts` | — | Cliente HTTP, tipos TS espelhando os DTOs, formatação (dinheiro, número) | Contrato front↔back |
| `web/src/motor/` (`worker.ts`, `cliente.ts`, `protocolo.ts`), `web/src/modo.ts`, `web/pages/` (`montar.mjs`, `sw.js`, `icones/`), `.github/workflows/pages.yml` | — | **Versão do celular**: motor no navegador (Pyodide num Web Worker, save no IndexedDB), PWA offline e publicação no GitHub Pages. `npm run build:pages` gera `web/dist-pages` (não versionado). Detalhes e números em `ARQUITETURA-WEB.md`, seção *Versão do celular* | Mexer no modo navegador, na PWA ou no deploy do Pages |
| `web/src/estilo/telas-celular.css`, `web/src/estreita.ts` | — | Layout até 640 px (alvo 390): menu vira gaveta, topo em três linhas, colunas `secundaria` da `<Grade>` somem, campo em pé | Ajuste de layout no celular |
| `testes/*.py` | 63 arquivos (`desempenho.py`, `balanceamento.py` e `economia.py` são harness lentos, fora da suíte; `test_copinha.py` e `test_convocacoes.py` cobrem a Copinha e as datas FIFA) | `unittest` da stdlib, sem dependência externa. `cd testes && python -m unittest -v` (~4 min, ~305 testes) | Rodar antes de qualquer PR |
| `docs/proxima-onda.md` | — | **Backlog da próxima onda**: o que espera decisão, o que espera exemplo do testador, o que está pronto para codar e como verificar | Antes de começar a próxima rodada |
| `.github/workflows/testes.yml` | — | CI (GitHub Actions): a cada push na `main` e em toda PR roda a suíte `unittest` e o `npm run build` da web; avisa se `web/dist` ficou velho | Ao mudar o que a suíte ou o build precisam |
| `ferramentas/capturas.py` | — | Capturas das 13 telas em 5 resoluções (Edge headless, cópia isolada) e comparação por pixel | Antes/depois de mexer em CSS ou tela |
| `baixar-nova-versao.bat` + `ferramentas/nova-versao.ps1` | — | Baixa a `main` já extraída em `Documents\bras2.0\<N>.0` (próximo número) e copia save, config e elencos da pasta anterior | Para atualizar a cópia local do Kauã |
| `ferramentas/importar_elencos.py` | — | Importa elencos reais (football-data.org / API-Football) | Atualização de temporada real |
| `.github/pull_request_template.md` | — | Modelo de PR (o que muda, por que, testes, docs); convenções de branch e título no `CLAUDE.md` | Ao abrir PR |

## Índice do motor (`brasfut.py`) — por seção

Não liste as 391 funções; use `grep -n "^def \|^class " brasfut.py` para
achar o nome exato, ou abra só a faixa abaixo:

| Linhas | Seção |
|---|---|
| 1–630 | Utilitários, formações (`formacao_de`), perfis das ligas de fora (`PERFIL_LIGA_EXT`), calendário das copas (`SEMANAS_*`, `COPAS_NACIONAIS`, `SUPERCOPAS_NACIONAIS`, Intercontinental/Mundial), clubes brasileiros e sul-americanos |
| 630–870 | **Ligas sul-americanas**: `LIGAS_SUL`, `VAGAS_LIB`/`VAGAS_SULA`, `CLUBES_LIGAS_SUL` (clubes novos com nome real) |
| 870–1150 | Geração de jogador/clube (`novo_jogador`, `novo_clube`), elencos reais (`aplicar_elencos_reais`), `criar_mundo` |
| 1150–1345 | Mundo embutido (`mundo_embutido`, `aplicar_mundo`), ligas de fora, `montar_ligas_sul`, `vagas_continentais_sul` |
| 1345–1700 | Copas: `montar_copas`, **Intercontinental e Mundial** (`nova_intercontinental`, `montar_mundial`), **supercopas** (`montar_supercopas`), **copas nacionais de fora** (`montar_copas_nacionais`), Champions/Europa League, grupos continentais |
| 1700–2400 | Escalação: seleção automática (`_atribuicao_hungara`), `montar_escalacao`, `diagnostico_escalacao` |
| 2400–3500 | Táticas e **estilos da máquina** (`TATICAS`, `ESTILOS`, `estilo_de`, `tatica_do_jogo`), simulação de partida (`simular` sem pausa e o gerador `partida` com o intervalo interativo, `PARTIDA_PRONTA`), posse, moral com causa (`mexer_moral`), pênaltis |
| 3230–4240 | Classificação, clássicos, **estaduais reais** (`_formato_estadual`, `montar_estaduais`), semana de estadual (joga Supercopa/Recopa) |
| 4240–4680 | Economia semanal, manchetes, mata-mata (`jogar_fase_copa`: jogo único, campo neutro, segundo plano), `avancar_semana` |
| 4680–4790 | Mercado — transferência/empréstimo básicos, IA de mercado |
| 4790–6080 | Mercado — propostas, negociação (`Proposta`/`Resposta`), salário do livre e do veterano, agendadas, contraproposta, **pré-contrato e disputa** (`pode_precontrato`, `fechar_precontrato`, `rivais_assediam`, `disputa`, `rival_leva`) |
| 5960–6420 | Evolução de jogador (potencial, declínio, leitura do olheiro `scout`), **lista de observação** (`observar`, `observados`, `avisos_observados`, `observar_mes`), treino |
| 6734–7028 | Base: categoria de base, peneira regional, promoção |
| 7029–7550 | **Copinha** (`montar_copinha`, `jogar_fase_copinha` com sorteio próprio `_rng_copinha`, `semana_copinha` no estadual, `copinha_de_janeiro` na carreira nova, `destaques_copinha`) e **convocações** (`DATAS_FIFA`, `NAC_REAL`, `fixar_nacionalidades`, `convocar`, `liberar_convocados`, `datas_fifa` no fim de `avancar_semana`; o desfalque está em `disponivel`) |
| 7551–8020 | Teto de potencial (`teto_maximo`, `revisar_potencial`), IA (livres, investimentos, rebaixamento, premiação) |
| 8021–8685 | Diretoria (**confiança semanal**, `ia_demite_tecnicos`), opções da carreira, carreira do técnico |
| 8686–9855 | **Interface de terminal original** (`tela_elenco`, `tela_mercado`, `jogar_semana` do modo texto — não confundir com `brasfut_app.py`) |
| 9856–10748 | Estatísticas do ano, crédito, prêmios do ano, relatório e resumo de temporada (`premios_do_ano`, `campanhas_do_ano`, `titulos_da_temporada`, `apurar_temporada`, `encerrar_temporada`) |
| 10749–12770 | **Capitão** (`capitao_de`, `definir_capitao`) e **Modo Caos** (`MODOS`, `EVENTOS_CAOS` com 72 eventos `ev_*` na liga do clube do jogador via `_liga`/`_gr`, bombas-relógio em `BOMBAS_CAOS`, `eventos_caos` chamado no fim de `avancar_semana`, `soltar_presos` na virada) |
| 12771–13273 | Save/load (`salvar` com o `.resumo` do menu, `carregar`, `migrar`), trava de save, `loop()` principal, `main()` |

`brasfut_app.py`: além dos helpers de UI (linhas 1–560), cada tela/diálogo
é uma classe (`class NomeDoDialogo(Dialogo)`) a partir da linha 566 — a
classe `Brasfut(tk.Tk)` (566–2994) é a janela principal; as demais
(`Negociar`, `Vitrine`, `Avancar`, `ResumoTemporada`...) são diálogos
modais. `main()` na linha 4531.

> **Começando uma rodada nova?** O backlog atualizado está em `docs/proxima-onda.md`.

## Status do roadmap (fonte: `docs/three-amigos/2026-09-24-rodada-de-melhorias.md`)

Decidido em reunião de alinhamento (Three Amigos) com base em 28 achados de
UX, 12 bugs confirmados e diagnóstico de game design.

**Onda 1 — concluída** (commits `107c079`, `95e33b3`, `26e90a8`):
bug do livre roubado pela IA, guard de posse único na API, limpeza de
`assumir_clube`, validade de proposta por semana absoluta, textos
mentirosos corrigidos, barra de forças comparando ataque×defesa certos,
memos exatos de desempenho (-23%/semana), layout estrutural sem corte,
acessibilidade básica, linguagem/números unificados.

**Onda 2 — concluída** (mergeada na `main` via PRs #1–#2; escopo, ordem e
decisões em `docs/three-amigos/2026-09-25-onda-2-decisoes.md`):
- ~~Tela da partida~~ — feito: `historico_meus` (10), notas sobrevivem ao
  save, `nota_soma`/`nota_j` somados, `componentes/Partida.tsx` no Painel e
  no fim do Simular (`test_partida.py`).
- ~~Tokens de CSS~~ — feito: azul = ação, dourado = conquista, âmbar =
  atenção; 6 degraus de fonte; inline só dinâmico (`test_tokens.py`).
- ~~Prêmios do ano~~ — feito: melhor (média de nota, mínimo metade das
  rodadas), artilheiro, revelação (até 21) e seleção 4-3-3 das quatro séries
  na virada; histórico `j["premios"]`, manchete e `premio_valor` no valor
  até o ano seguinte (`premios_do_ano`/`premiar_ano`, `test_premios.py`).
- ~~Confiança da diretoria~~ — feito: semanal com causa e tendência, aviso
  em 30, demissão em 15 depois do aviso, máquina demite nos marcos e a vaga
  alimenta as propostas (`test_confianca.py`).
- ~~Instruções condicionais pré-jogo~~ — feito: 46'/71', só a mentalidade,
  máquina sobe/desce um degrau aos 71' (`test_condicional.py`,
  `testes/balanceamento.py`).

**Onda 3 — em andamento** (os dois primeiros itens precisam de spike):
- ~~Intervalo interativo~~ — feito: `partida` é gerador que para aos 45'
  (`pausar_lado`), `simular` roda sem pausa; a API joga o 1º tempo antes da
  semana (`/api/avancar` com `intervalo`), `/api/partida/segundo-tempo` termina
  e guarda o resultado em `PARTIDA_PRONTA` (memória, nunca no save)
  (`test_intervalo.py`, `componentes/Intervalo.tsx`).
- ~~IA com identidade tática e rebalanceamento~~ — feito: `ESTILOS` por clube
  (`estilo_de`, escola do país), `tatica_do_jogo` ajusta um degrau pela força,
  `TATICAS` recalibradas (`test_estilos.py`).
- ~~Moral com causa e clássico com peso~~ — feito: `mexer_moral`/`anotar_moral`
  guardam `j["moral_hist"]` (5, só do meu clube), clássico dobra a moral de
  resultado (`test_moral.py`).
- ~~Entrosamento~~ — feito: `j["entros"]` (padrão 80, chegada 35, volta 60,
  +5 por jogo), `PESO_JOGO_ENTROS` em `rendimento`, entra na chave do memo do
  XI (`test_entrosamento.py`).
- Economia com escolhas, mercado disputado, olheiros. História do clube: feita (tela Clube, `dados_clubes.py` + `titulos_hist`).
- ~~Copinha e convocações~~ — feito: Copinha de 32 academias nas rodadas 1–5 do estadual
  (prêmio, taça do clube, vitrine aos destaques) e três datas FIFA (semanas 8, 24, 33) com
  23 por seleção sul-americana, desfalque na semana e `j["convocacoes"]` na ficha
  (`test_copinha.py`, `test_convocacoes.py`).

**Economia 2 — concluída** (PRs #12–#13, 2026-09-26/28): crédito do clube
(3 meses de receita, 2% ao mês, `tomar_credito`), IA só renova se couber na
folha, e sete espaços de patrocínio (`espacos_do_clube`, naming rights com
estádio de 20 mil+) com título pesando até x1,70. Harness `testes/economia.py`.

**Feedback do testador (Okumura) — 2026-09-26**: cartões (expulso sai de
campo, 2º amarelo = vermelho), mercado (acerto trava propostas, estadual
renova ofertas, livre sem revenda por 8 semanas), confiança do líder,
público com momento, renovação com idade, avisos no Painel, e a folha da IA
(contratação só se couber em 85% da receita — acabou com as "contratações
fantasmas" e com a Série D quebrando em 5 anos). Em aberto: ver as
`docs/proxima-onda.md` (notícia de gol e o exemplo das contratações
fantasmas, com o testador).

**Mundo — concluído** (2026-09-26): nove ligas sul-americanas (ARG 20,
URU, PAR, CHI, COL, EQU, PER, BOL, VEN) com as vagas da Libertadores e da
Sul-Americana saindo da tabela de cada país; copas nacionais de todas as
ligas de fora (jogo único, em segundo plano); Supercopa do Brasil e Recopa
numa rodada do estadual; Supercopa da UEFA e 17 supercopas nacionais na
semana 1; Copa Intercontinental todo ano (semanas 37–38) e Mundial de 32 a
cada 4 anos desde 2029 (`test_ligas_sul.py`, `test_copas_nacionais.py`,
`test_supercopas.py`, `test_mundial.py`). Semana de liga ~0,48 s.
Ponto a acompanhar: o caixa das ligas sul-americanas menores ainda cai
25–45% no primeiro ano.

**Economia — concluída** (PRs #3–#6, `docs/three-amigos/2026-09-25-economia-decisoes.md`):
extrato e informação, salário fixo pelo contrato, patrocínio como contrato e
rebalanceamento (público pela torcida, custos proporcionais, prêmio por fase
nas copas).

**Perguntas em aberto**: nenhuma. Limite de livres da IA decidido em
2026-09-25: um por clube por semana (`LIVRES_POR_CLUBE`). Cor da ação
primária decidida: azul. Histórico = 10
partidas, demissão em qualquer semana após aviso e IA também usando
instruções condicionais foram decididos em 2026-09-25.

**Pontas soltas conhecidas** (`ARQUITETURA-WEB.md`): nenhum diálogo só no
tkinter (lance a lance: `componentes/AoVivo.tsx`; ajuda e boas-vindas:
`componentes/Ajuda.tsx`, `GET /api/ajuda`); motor escreve sem acento (dívida
de quando era terminal); React não tem testes (só a API tem).

## Como rodar / testar

```
iniciar-web.bat                 # jogar (sobe server.py, abre o navegador)
cd testes && python -m unittest -v   # testes, ~2 min, sem pip/npm
python server.py --sem-abrir    # API sozinha (dev)
cd web && npm run dev           # Vite com proxy /api (dev)
cd web && npm run build         # gera web/dist (versionado)
cd web && npm run build:pages   # versao do celular em web/dist-pages (Pyodide + PWA)
cd testes && python economia.py # caixa da IA em 12 temporadas (lento)
```

O CI (`.github/workflows/testes.yml`) roda a suíte e o build em toda PR; os
harness lentos (`balanceamento.py`, `desempenho.py`) continuam só locais.

## Como manter este mapa

- Terminou uma feature/fix que fecha um item da Onda 1/2/3? Mova o item
  para "concluída" com o número do commit, igual foi feito acima.
- Mexeu numa faixa de linha grande o suficiente para mudar a seção do
  índice do motor? Ajuste a linha inicial/final daquela linha da tabela.
- Criou um arquivo novo (tela, componente, módulo em `api/`)? Uma linha na
  tabela de "Mapa de arquivos".
- Decisão nova de arquitetura ou de roadmap? Isso vai em
  `ARQUITETURA-WEB.md` ou em uma nova ata de `docs/three-amigos/` — este
  mapa só referencia, não duplica.
- Nunca regenere o arquivo inteiro relendo o projeto do zero: edite só a
  seção que mudou.
