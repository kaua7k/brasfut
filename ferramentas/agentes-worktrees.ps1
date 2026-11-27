# Cria um git worktree por agente, ao lado do repo, cada um no seu branch.
# Uso: powershell -File ferramentas\agentes-worktrees.ps1 feat/assunto-motor feat/assunto-web
#   sem argumentos: motor, web, qa e design com o sufixo da data.
# Remover depois do merge: git worktree remove ..\brasfut-<nome>; git branch -d <branch>
$ErrorActionPreference = 'Stop'
$raiz = (git rev-parse --show-toplevel).Trim()
Set-Location $raiz
git fetch origin main
$branches = $args
if ($branches.Count -eq 0) {
  $d = Get-Date -Format 'MMdd'
  $branches = @("feat/motor-$d", "feat/web-$d", "test/qa-$d", "docs/design-$d")
}
foreach ($branch in $branches) {
  $nome = $branch.Substring($branch.IndexOf('/') + 1)
  $pasta = Join-Path (Split-Path $raiz -Parent) "brasfut-$nome"
  if (Test-Path $pasta) { Write-Host "ja existe: $pasta"; continue }
  git worktree add -b $branch $pasta origin/main
  Write-Host "pronto: $pasta  ($branch)"
}
git worktree list
