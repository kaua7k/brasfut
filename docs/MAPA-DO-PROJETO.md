# Mapa do projeto — BRASFUT

> **Para quem (Claude Code) for trabalhar neste repo**: leia este arquivo
> primeiro. Ele existe pra evitar reler `brasfut.py` (9,8k linhas) e
> `brasfut_app.py` (4,5k linhas) inteiros toda vez. Abra os arquivos-fonte só
> na faixa de linha indicada abaixo para a sua tarefa. Ao terminar um
> trabalho que muda estrutura, adiciona arquivo, fecha um item do roadmap ou
> descobre algo que devia estar aqui, **edite a seção correspondente deste
> mapa** (não regenere o arquivo inteiro) — é assim que ele se paga.

Última atualização: 2026-09-26 · commit de referência: `4d2e909`

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
| `brasfut.py` | 9839 linhas | O motor inteiro + a interface de terminal original (`main()`, `loop()`, `tela_*`) | Só a faixa de linha da seção que precisa (ver índice abaixo) |
| `brasfut_app.py` | 4552 linhas | Janela desktop (tkinter). Uma classe `Dialogo` por tela/ação | Só se a tarefa for na janela desktop — a maioria do trabalho novo vai para a web |
| `dados_mundo.py` | 1181 linhas | Dados estáticos: clubes, ligas, seleções, nomes | Ao adicionar/corrigir liga, clube ou país |
| `server.py` | 156 linhas | `http.server` da stdlib; serve a API e `web/dist` | Infra do servidor, não regra de jogo |
| `api/rotas.py` | ~350 linhas | `URL -> função`. Todas as rotas HTTP registradas com `@rota(metodo, caminho)` | Para achar/adicionar um endpoint |
| `api/sessao.py` | — | Mantém o `G` vivo em memória, salva, dono do `threading.RLock` | Concorrência, save, trava de sessão |
| `api/dto.py` | — | Traduz `G` no formato de cada tela (uma função por tela) | Ao mudar o que uma tela recebe |
| `api/mercado.py` | — | Mesa de negociação e regras de mercado do lado da API (maior arquivo de `api/`) | Compra/venda/empréstimo/renovação na web |
| `api/competicoes.py` | — | Estaduais, séries, copas — montagem e leitura pela API | Telas de Classificação/Competições |
| `api/avanco.py` | — | Avançar em ritmos (jogo/semana/mês/janela/temporada) | Botão *Avançar*/*Simular* |
| `api/campo.py` | — | Vaga (GOL, ZAG...) → ponto no campo, para as formações | Desenho do campo na Escalação |
| `web/src/telas/*.tsx` | 14 arquivos | Uma tela por arquivo (Painel, Elenco, Escalação, Mercado, Financas, etc.) | Ao mexer numa tela específica |
| `web/src/componentes/*.tsx` | 19 arquivos (`Ajuda.tsx`: ajuda e boas-vindas; `Partida.tsx`: resumo e detalhe da partida; `DialogoRenovar.tsx`: renovação em lote) | Diálogos e peças reusáveis (Mesa, Grade, Campo, Ficha...) | Componente compartilhado entre telas |
| `web/src/api.ts`, `tipos.ts`, `formato.ts` | — | Cliente HTTP, tipos TS espelhando os DTOs, formatação (dinheiro, número) | Contrato front↔back |
| `testes/*.py` | 34 arquivos (`desempenho.py` e `balanceamento.py` são harness lentos, fora da suíte) | `unittest` da stdlib, sem dependência externa. `cd testes && python -m unittest -v` (~120s, 158 testes) | Rodar antes de qualquer PR |
| `.github/workflows/testes.yml` | — | CI (GitHub Actions): a cada push na `main` e em toda PR roda a suíte `unittest` e o `npm run build` da web; avisa se `web/dist` ficou velho | Ao mudar o que a suíte ou o build precisam |
| `ferramentas/capturas.py` | — | Capturas das 13 telas em 5 resoluções (Edge headless, cópia isolada) e comparação por pixel | Antes/depois de mexer em CSS ou tela |
| `ferramentas/importar_elencos.py` | — | Importa elencos reais (football-data.org / API-Football) | Atualização de temporada real |
| `.backup-pre-patch/` | — | Snapshots do motor pré-patch (histórico, não código ativo) | Raramente |

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
| 2400–3230 | Simulação de partida (`simular`), posse, moral com causa (`mexer_moral`), pênaltis |
| 3230–4240 | Classificação, clássicos, **estaduais reais** (`_formato_estadual`, `montar_estaduais`), semana de estadual (joga Supercopa/Recopa) |
| 4240–4680 | Economia semanal, manchetes, mata-mata (`jogar_fase_copa`: jogo único, campo neutro, segundo plano), `avancar_semana` |
| 4680–4790 | Mercado — transferência/empréstimo básicos, IA de mercado |
| 4790–5960 | Mercado — propostas, negociação (`Proposta`/`Resposta`), salário do livre e do veterano, agendadas, contraproposta |
| 5960–6220 | Evolução de jogador (potencial, declínio, treino) |
| 6220–6500 | Base: categoria de base, peneira regional, promoção |
| 6500–7000 | Teto de potencial, IA (livres, investimentos, rebaixamento, premiação), prêmios do ano |
| 7000–7670 | Diretoria (**confiança semanal**, `ia_demite_tecnicos`), carreira do técnico |
| 7670–8760 | **Interface de terminal original** (`tela_elenco`, `tela_mercado`, `jogar_semana` do modo texto — não confundir com `brasfut_app.py`) |
| 8760–9400 | Estatísticas do ano, relatório e resumo de temporada (`apurar_temporada`, `encerrar_temporada`) |
| 9400–9839 | Save/load (`salvar`, `carregar`, `migrar`), trava de save, `loop()` principal, `main()` |

`brasfut_app.py`: além dos helpers de UI (linhas 1–560), cada tela/diálogo
é uma classe (`class NomeDoDialogo(Dialogo)`) a partir da linha 566 — a
classe `Brasfut(tk.Tk)` (566–2994) é a janela principal; as demais
(`Negociar`, `Vitrine`, `Avancar`, `ResumoTemporada`...) são diálogos
modais. `main()` na linha 4531.

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
- Intervalo interativo (spike de arquitetura: `simular` viraria máquina de
  estados).
- IA com identidade tática e rebalanceamento (Retranca hoje domina
  matematicamente sobre Pressão — decisão foi **não mexer agora**).
- ~~Moral com causa e clássico com peso~~ — feito: `mexer_moral`/`anotar_moral`
  guardam `j["moral_hist"]` (5, só do meu clube), clássico dobra a moral de
  resultado (`test_moral.py`).
- ~~Entrosamento~~ — feito: `j["entros"]` (padrão 80, chegada 35, volta 60,
  +5 por jogo), `PESO_JOGO_ENTROS` em `rendimento`, entra na chave do memo do
  XI (`test_entrosamento.py`).
- Economia com escolhas, mercado disputado, olheiros, Copinha, história do clube.

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

**Pontas soltas conhecidas** (`ARQUITETURA-WEB.md`): partida lance a lance só
existe no tkinter (ajuda e boas-vindas migraram: `componentes/Ajuda.tsx`,
`GET /api/ajuda`); motor escreve sem acento (dívida
de quando era terminal); React não tem testes (só a API tem).

## Como rodar / testar

```
iniciar-web.bat                 # jogar (sobe server.py, abre o navegador)
cd testes && python -m unittest -v   # testes, ~2 min, sem pip/npm
python server.py --sem-abrir    # API sozinha (dev)
cd web && npm run dev           # Vite com proxy /api (dev)
cd web && npm run build         # gera web/dist (versionado)
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
