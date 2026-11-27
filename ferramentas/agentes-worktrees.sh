#!/usr/bin/env bash
# Cria um git worktree por agente, ao lado do repo, cada um no seu branch.
# Uso: ferramentas/agentes-worktrees.sh feat/assunto-motor feat/assunto-web ...
#   sem argumentos: motor, web, qa e design com o sufixo da data.
# Resultado: ../brasfut-<nome>/ (pasta irmã do repo), pronta para abrir num
# terminal do Maestri. Remover depois do merge:
#   git worktree remove ../brasfut-<nome> && git branch -d <branch>
set -euo pipefail
raiz="$(git rev-parse --show-toplevel)"
cd "$raiz"
git fetch origin main
if [ "$#" -eq 0 ]; then
  d="$(date +%m%d)"
  set -- "feat/motor-$d" "feat/web-$d" "test/qa-$d" "docs/design-$d"
fi
for branch in "$@"; do
  nome="${branch#*/}"
  pasta="$(dirname "$raiz")/brasfut-$nome"
  if [ -d "$pasta" ]; then echo "ja existe: $pasta"; continue; fi
  git worktree add -b "$branch" "$pasta" origin/main
  echo "pronto: $pasta  ($branch)"
done
git worktree list
