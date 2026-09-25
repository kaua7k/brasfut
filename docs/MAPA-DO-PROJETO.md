# Mapa do projeto — BRASFUT

> **Para quem (Claude Code) for trabalhar neste repo**: leia este arquivo
> primeiro. Ele existe pra evitar reler `brasfut.py` (8,5k linhas) e
> `brasfut_app.py` (4,5k linhas) inteiros toda vez. Abra os arquivos-fonte só
> na faixa de linha indicada abaixo para a sua tarefa. Ao terminar um
> trabalho que muda estrutura, adiciona arquivo, fecha um item do roadmap ou
> descobre algo que devia estar aqui, **edite a seção correspondente deste
> mapa** (não regenere o arquivo inteiro) — é assim que ele se paga.

Última atualização: 2026-09-25 · commit de referência: `26e90a8`

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
| `brasfut.py` | 8497 linhas, 391 funções/classes | O motor inteiro + a interface de terminal original (`main()`, `loop()`, `tela_*`) | Só a faixa de linha da seção que precisa (ver índice abaixo) |
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
| `web/src/componentes/*.tsx` | 14 arquivos | Diálogos e peças reusáveis (Mesa, Grade, Campo, Ficha...) | Componente compartilhado entre telas |
| `web/src/api.ts`, `tipos.ts`, `formato.ts` | — | Cliente HTTP, tipos TS espelhando os DTOs, formatação (dinheiro, número) | Contrato front↔back |
| `testes/*.py` | 14 arquivos | `unittest` da stdlib, sem dependência externa. `cd testes && python -m unittest -v` (~20s) | Rodar antes de qualquer PR |
| `ferramentas/importar_elencos.py` | — | Importa elencos reais (football-data.org / API-Football) | Atualização de temporada real |
| `.backup-pre-patch/` | — | Snapshots do motor pré-patch (histórico, não código ativo) | Raramente |

## Índice do motor (`brasfut.py`) — por seção

Não liste as 391 funções; use `grep -n "^def \|^class " brasfut.py` para
achar o nome exato, ou abra só a faixa abaixo:

| Linhas | Seção |
|---|---|
| 1–600 | Utilitários, formações (`formacao_de`, `rotulo_formacao`), helpers de texto/número |
| 600–1000 | Geração de jogador/clube (`novo_jogador`, `novo_clube`), elencos reais, `criar_mundo` |
| 1000–1500 | Ligas externas (Europa/MLS/Árabe), montagem de copas continentais |
| 1500–2000 | Escalação: seleção automática (`_atribuicao_hungara`), `montar_escalacao`, `diagnostico_escalacao` |
| 2000–2650 | Simulação de partida (`simular`), posse, força de meio, moral, pênaltis |
| 2650–3350 | Classificação, clássicos, **estaduais reais** (`_formato_estadual`, `montar_estaduais`, mata-mata) |
| 3350–3800 | Economia semanal, manchetes (`manchetes_da_semana`), `avancar_semana` |
| 3800–4000 | Mercado — transferência/empréstimo básicos, IA de mercado |
| 4000–5000 | Mercado — propostas, negociação (`Proposta`/`Resposta`), agendadas, ofertas espontâneas, contraproposta |
| 5000–5320 | Evolução de jogador (potencial, declínio, treino) |
| 5320–5630 | Base: categoria de base, peneira regional, candidatos, promoção |
| 5630–6090 | Teto de potencial, IA (contratar livres, investimentos, rebaixamento, premiação) |
| 6090–6400 | Carreira do técnico (propostas de emprego, reputação, marcos) |
| 6373–7500 | **Interface de terminal original** (`tela_elenco`, `tela_mercado`, `main()` do modo texto — não confundir com `brasfut_app.py`, que é a janela tkinter) |
| 7500–8000 | Relatório de temporada, resumo, estatísticas do ano |
| 8000–8497 | Save/load (`salvar`, `carregar`, `migrar`), trava de save, `loop()` principal, `main()` |

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

**Onda 2 — em andamento** (branch `melhorias/onda-2`; escopo, ordem e
decisões em `docs/three-amigos/2026-09-25-onda-2-decisoes.md`):
- Tela da partida: resumo compacto no retorno do avanço (placar, gols,
  cartões, posse, "Ver detalhes"); histórico curto de partidas do clube;
  normalizar chaves de `notas` no save.
- Tokens de CSS (paleta/escala únicas, fim dos hex soltos e inline styles)
  — só depois de ter baseline visual da Onda 1.
- Somar `nota_soma` e prêmios do ano/seleção.
- Confiança da diretoria semanal com causa/tendência; IA também demite
  técnico.
- Instruções condicionais pré-jogo (substitui o intervalo interativo por
  ora).

**Onda 3 — depois** (precisa de spike):
- Intervalo interativo (spike de arquitetura: `simular` viraria máquina de
  estados).
- IA com identidade tática e rebalanceamento (Retranca hoje domina
  matematicamente sobre Pressão — decisão foi **não mexer agora**).
- Moral com causa, clássico com peso, economia com escolhas, entrosamento,
  mercado disputado, olheiros, Copinha, história do clube.

**Perguntas em aberto**: limite semanal de livres contratados pela IA; cor
da ação primária (decidir no item de tokens da Onda 2). Histórico = 10
partidas, demissão em qualquer semana após aviso e IA também usando
instruções condicionais foram decididos em 2026-09-25.

**Pontas soltas conhecidas** (`ARQUITETURA-WEB.md`): partida lance a lance,
boas-vindas e ajuda só existem no tkinter; motor escreve sem acento (dívida
de quando era terminal); React não tem testes (só a API tem).

## Como rodar / testar

```
iniciar-web.bat                 # jogar (sobe server.py, abre o navegador)
cd testes && python -m unittest -v   # testes, ~20s, sem pip/npm
python server.py --sem-abrir    # API sozinha (dev)
cd web && npm run dev           # Vite com proxy /api (dev)
cd web && npm run build         # gera web/dist (versionado)
```

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
