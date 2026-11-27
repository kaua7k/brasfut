# Workspace do BRASFUT no Maestri

O [Maestri](https://www.producthunt.com/products/maestri) é um canvas infinito
onde cada terminal de agente vira um nó, ao lado de notas e desenhos. Aqui fica
como montar o workspace do BRASFUT com vários agentes em paralelo sem um
pisar no outro.

> **Não use a pasta de jogar** (`Documents\bras2.0\<N>.0`): ela vem do
> `baixar-nova-versao.bat`, não é um clone do git e guarda o save de verdade.
> Os agentes trabalham num clone separado, em `C:\dev`.

## 1. Preparar o repo

Uma vez só, no PowerShell (precisa do Git for Windows e do Claude Code
instalados):

```powershell
git clone https://github.com/kaua7k/brasfut.git C:\dev\brasfut
```

A cada rodada, crie um worktree por agente (pastas irmãs
`C:\dev\brasfut-<nome>`, cada uma no seu branch saindo da `main`):

```powershell
cd C:\dev\brasfut; git pull; powershell -ExecutionPolicy Bypass -File ferramentas\agentes-worktrees.ps1
```

Sem argumentos o script cria `motor`, `web`, `qa` e `design` com a data; com
argumentos, usa os branches dados (`feat/motor-socios feat/web-socios ...`). No
Mac/Linux: `ferramentas/agentes-worktrees.sh`, com clone em `~/dev/brasfut`.

Por que worktree: o `brasfut.py` tem 13 mil linhas e todo mundo acaba tocando
nele; com uma pasta e um branch por agente cada um tem sua cópia, e o conflito
só aparece no merge, onde dá pra resolver com calma.

## 2. Montar o canvas

Crie um workspace **BRASFUT** e arrume os nós assim (esquerda para direita, o
fluxo da rodada):

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ NOTA: Rodada │   │ T1 MAESTRO   │   │ NOTA: Quadro │
│ (objetivo e  │   │ C:\dev\brasfut│   │ docs/agentes/│
│  critérios)  │   │ main, só lê  │   │ QUADRO.md    │
└──────────────┘   └──────────────┘   └──────────────┘
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ T2 MOTOR     │   │ T3 API-WEB   │   │ T4 QA        │   │ T5 DESIGN    │
│ brasfut-motor│   │ brasfut-web  │   │ brasfut-qa   │   │ brasfut-     │
│              │   │              │   │              │   │ design       │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
┌──────────────────────────────┐
│ BROWSER: http://127.0.0.1:5173│  (preview da web, servido pelo T3)
└──────────────────────────────┘
```

Em cada terminal: `cd` para o worktree e `claude`. Para outro agente (Codex
etc.) funciona igual: ele lê o `AGENTS.md` da raiz.

Atalhos estilo tmux do Maestri trocam entre terminais; o Ombro resume o que
cada um fez enquanto você estava fora.

## 3. Prompt de abertura de cada terminal

Cole como primeira mensagem. Troque `<OBJETIVO>` pelo item do
`docs/proxima-onda.md` que a rodada vai atacar.

**T1 — Maestro** (`C:\dev\brasfut`, na `main`, não edita código):

```
Você é o maestro desta rodada do BRASFUT. Leia AGENTS.md, docs/MAPA-DO-PROJETO.md
e docs/proxima-onda.md. Objetivo: <OBJETIVO>. Quebre em tarefas para quatro
agentes em paralelo (motor, api-web, qa, game-design, definidos em
.claude/agents/), cada um no seu worktree. Para cada um escreva: o que fazer,
arquivos/faixas de linha, o contrato entre motor e web e como verificar.
Não edite código. Depois acompanhe docs/agentes/QUADRO.md nos worktrees e diga
a ordem de merge.
```

**T2 — Motor** (`C:\dev\brasfut-motor`):

```
Use o subagente motor (.claude/agents/motor.md) como sua regra. Leia AGENTS.md
e a faixa certa de docs/MAPA-DO-PROJETO.md. Tarefa: <colar a parte do maestro>.
Ao terminar: suíte verde, contrato motor->web escrito em docs/agentes/QUADRO.md,
commit tipo(escopo): descricao.
```

**T3 — API e web** (`C:\dev\brasfut-web`):

```
Use o subagente api-web (.claude/agents/api-web.md) como sua regra. Leia
AGENTS.md e ARQUITETURA-WEB.md (parte da tela). Tarefa: <colar>. Enquanto o
motor não entrega o campo, trabalhe contra o contrato do QUADRO.md. Suba
`cd web && npm run dev` + `python server.py --sem-abrir` (só você usa as
portas 5173/8770). Build do web/dist só no fim, depois de rebasear na main.
```

**T4 — QA** (`C:\dev\brasfut-qa`):

```
Use o subagente qa (.claude/agents/qa.md) como sua regra. Tarefa: escreva os
testes da regra <OBJETIVO> a partir do contrato no QUADRO.md (podem falhar até
o motor entregar). Depois revise os branches dos outros com
`git fetch && git diff origin/main...<branch>` contra o checklist do qa.md.
```

**T5 — Game design** (`C:\dev\brasfut-design`):

```
Use o subagente game-design (.claude/agents/game-design.md) como sua regra.
Grave a linha de base agora: balanceamento.py, economia.py e desempenho.py com
--gravar em testes/_tmp/antes-*.json. Quando o motor tiver commit, rode de novo
no branch dele e compare. Proposta de números vai para o QUADRO.md.
```

## 4. Contexto compartilhado

| O quê | Onde | Quem lê |
|---|---|---|
| Regras do repo, comandos, git | `AGENTS.md` (+ `CLAUDE.md` no Claude Code) | todos, automático |
| Mapa por faixa de linha | `docs/MAPA-DO-PROJETO.md` | todos, antes de abrir código |
| Backlog e como verificar | `docs/proxima-onda.md` | maestro |
| Papel de cada agente | `.claude/agents/*.md` | cada terminal + subagentes do Claude Code |
| Recados entre agentes | `docs/agentes/QUADRO.md` | todos |
| Objetivo da rodada | nota no canvas | você |

O `QUADRO.md` vive em cada worktree: o recado chega aos outros pelo commit
(`git fetch` + `git show origin/<branch>:docs/agentes/QUADRO.md`), ou cole o
recado direto no terminal do outro agente pelo canvas — é o mais rápido.

## 5. Fechar a rodada

1. QA aprova cada branch; game design confirma os números.
2. Ordem de merge: motor → api-web (rebase, `npm run build`, commit de
   `web/dist`) → qa. Uma PR por branch, CI verde, merge direto (regra do
   `CLAUDE.md`).
3. O último a mergear atualiza `docs/MAPA-DO-PROJETO.md` e o
   `docs/proxima-onda.md`.
4. Limpar: `git worktree remove ../brasfut-<nome>` e apagar os branches.
5. No PC do Windows: rodar `baixar-nova-versao.bat` para levar a `main` nova.

## Sem Maestri: subagentes dentro de uma sessão só

Os mesmos papéis funcionam como subagentes do Claude Code numa sessão única
(Windows, nuvem, qualquer lugar): peça "use o agente motor para X e o agente
qa para cobrir" e o Claude Code delega. Rodam em sequência ou em paralelo
dentro da mesma pasta — bom para tarefas pequenas; para várias frentes grandes
ao mesmo tempo, prefira os worktrees.
