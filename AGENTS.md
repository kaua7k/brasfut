# BRASFUT — contexto para qualquer agente

Este arquivo é o **pacote de contexto único** do projeto. Vale para qualquer
agente de código (Claude Code, Codex, Gemini, Cursor...) aberto num terminal
deste repo, inclusive vários ao mesmo tempo num workspace do Maestri
(`docs/MAESTRI-WORKSPACE.md`). O Claude Code também lê o `CLAUDE.md`; as regras
são as mesmas.

## O jogo em um parágrafo

BRASFUT é um simulador de carreira de técnico de futebol brasileiro: Séries
A–D, estaduais reais, Copa do Brasil, Libertadores, Sul-Americana, nove ligas
sul-americanas, ligas europeias, copas nacionais e continentais, Mundial,
mercado com negociação (proposta, contraproposta, pré-contrato, empréstimo),
economia (patrocínio, sócios, crédito, bicho), base e Copinha, convocações,
diretoria com confiança semanal, partida com intervalo interativo e Modo Caos.
Projeto pessoal do Kauã (`kaua7k/brasfut`). Regras de jogo: `COMO-JOGAR.md`.

## Arquitetura em poucas linhas

- **Um motor só**: `brasfut.py` (~13,7 mil linhas, Python **stdlib pura, sem
  pip**). Não sabe que existe tela. Atende três interfaces:
  - terminal: `python brasfut.py`
  - janela tkinter: `brasfut_app.py` (~4,5 mil linhas; pouco trabalho novo vai pra lá)
  - web: `server.py` (`http.server`, 127.0.0.1:8770, porta em `BRASFUT_PORTA`)
    serve `web/dist` e a API em `api/` — `rotas.py` (URL→função), `sessao.py`
    (`G` em memória sob `RLock`, save, slots), `dto.py` (`G` → formato de cada
    tela), `mercado.py`, `competicoes.py`, `avanco.py`, `navegador.py`.
- **Front**: React + TypeScript + Vite em `web/src` (`telas/`, `componentes/`,
  `api.ts`, `tipos.ts`). **`web/dist` é versionado**: mexeu em `web/src`, rode
  `cd web && npm run build` e commite `web/dist` junto.
- **Celular**: `npm run build:pages` roda o mesmo motor no navegador (Pyodide
  num Web Worker, save no IndexedDB). Por isso o motor **nunca** ganha
  dependência fora da stdlib.
- Dados estáticos: `dados_mundo.py` (clubes, ligas, nomes), `dados_clubes.py`
  (história e escudos).

## Por onde começar (ordem de leitura)

1. `docs/MAPA-DO-PROJETO.md` — mapa de arquivos e **índice do motor por faixa
   de linha**. Abra só a faixa que interessa; nunca leia `brasfut.py` inteiro.
   Nome exato de função: `grep -n "^def \|^class " brasfut.py`.
2. `docs/proxima-onda.md` — backlog: o que está pronto para codar, o que
   espera decisão, como verificar.
3. `ARQUITETURA-WEB.md` — referência completa de `api/` e `web/`.
4. `docs/three-amigos/` — decisões de roadmap já tomadas (não reabrir).

## Regras que não se quebram

- `brasfut_save.json` (e `brasfut_save_*.json`, `.lock`) na raiz é o **save
  real do jogador**: nunca escrever nem apagar.
- Testes importam `testes/apoio.py` **antes** de `api` (aponta o save para
  `testes/_tmp`).
- Motor sem dependência externa. Front pode usar npm.
- Tempo da semana de liga: média ~0,48 s, limite 0,6 s. Competição ou regra
  nova que pesa no tempo precisa medir (`testes/desempenho.py`).
- Save antigo precisa continuar abrindo: campo novo em `G` ganha migração em
  `migrar` (fim do `brasfut.py`).
- Textos do jogo em português do Brasil. O motor escreve sem acento (dívida
  antiga); o front tem acento.

## Comandos

```
cd testes && python -m unittest -v          # suíte inteira (~3-4 min), obrigatória antes de pronto
cd testes && python -m unittest -v test_mercado_regras   # um arquivo
python testes/balanceamento.py --gravar antes.json       # mexeu em partida/tática/força/IA
python testes/desempenho.py --gravar antes.json          # mexeu em tempo
python testes/economia.py --gravar antes.json            # mexeu em dinheiro
cd web && npm run build                     # tsc -b && vite build -> web/dist (commitar)
python server.py --sem-abrir                # API + web/dist
cd web && npm run dev                       # Vite 5173 com proxy /api -> 8770
```

## Git

- Um branch por tema a partir da `main` atualizada: `tipo/assunto`
  (`feat/ligas-sul`, `fix/salario-livre`).
- Commit e PR: `tipo(escopo): descricao`, tipo em `feat`, `fix`, `perf`,
  `docs`, `ci`, `refactor`, `test`.
- PR segue `.github/pull_request_template.md` e só entra com o CI verde.
- Terminou algo estrutural (arquivo novo, item do roadmap, seção do motor que
  mudou de lugar)? Atualize **só a seção que mudou** de
  `docs/MAPA-DO-PROJETO.md`.

## Trabalhando em paralelo (vários agentes)

Quando há mais de um agente ao mesmo tempo:

- **Cada agente no seu git worktree e no seu branch.** Dois agentes na mesma
  pasta se atropelam no `brasfut.py`. Script: `ferramentas/agentes-worktrees.sh`
  (macOS/Linux) ou `ferramentas/agentes-worktrees.ps1` (Windows).
- **Dono por área** (ver `.claude/agents/`): motor (`brasfut.py`,
  `dados_*.py`), api+web (`api/`, `web/`), QA (`testes/`), game design
  (harness de balanceamento/economia, sem editar código de produção).
  Precisou mexer fora da sua área? Escreva no `docs/agentes/QUADRO.md` em vez
  de editar.
- `web/dist` só é regenerado por quem mexeu em `web/src`, no fim, depois de
  rebasear na `main` (é o arquivo que mais dá conflito).
- `docs/MAPA-DO-PROJETO.md` é editado por um agente só por vez — de
  preferência o último a mergear.
- Servidor: só um agente sobe o `npm run dev` (o proxy do Vite aponta fixo
  para o 8770). Os outros usam `BRASFUT_PORTA=8771 python server.py --sem-abrir`
  com `web/dist` se precisarem da API.
