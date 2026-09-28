# BRASFUT — instruções para o Claude Code neste repo

Antes de explorar o código (ler `brasfut.py`, `brasfut_app.py` inteiros,
ou varrer `web/src`), **leia `docs/MAPA-DO-PROJETO.md`**. Ele tem a
arquitetura, o índice de seções do motor por faixa de linha, o mapa de
arquivos e o status do roadmap (Onda 1/2/3). Isso evita reler os dois
arquivos gigantes do motor (juntos, ~13 mil linhas) a cada tarefa —
abra só a faixa de linha que o mapa indica para o que você precisa, e
use `grep -n "^def \|^class " brasfut.py` quando precisar do número
exato de uma função específica.

Começando uma rodada nova de melhorias, o backlog (o que espera decisão, o
que está pronto para codar, como verificar) está em `docs/proxima-onda.md`.

Para o que envolve a migração web, `ARQUITETURA-WEB.md` é a referência
completa (o mapa só aponta pra lá, não duplica). Para regra de jogo,
`COMO-JOGAR.md`. Para decisões de roadmap já tomadas, `docs/three-amigos/`.

**Depois de terminar um trabalho** que muda estrutura de arquivos, fecha
um item do roadmap, ou desloca uma seção grande dentro de `brasfut.py`,
atualize a seção correspondente de `docs/MAPA-DO-PROJETO.md` — só a parte
que mudou, sem reler o projeto inteiro para regenerar o mapa do zero. Se
nada estrutural mudou (um bugfix pontual, um ajuste de texto), não precisa
tocar no mapa.

Rodar os testes antes de considerar algo pronto:
`cd testes && python -m unittest -v` (unittest da stdlib, sem pip, ~2 min).

## Git e PRs

- Um branch por tema, a partir da `main` atualizada: `tipo/assunto`
  (ex.: `feat/ligas-sul`, `fix/salario-livre`). Nao reaproveitar branch de PR
  ja mergeada.
- Titulo de commit e de PR no formato `tipo(escopo): descricao`, com `tipo`
  entre `feat`, `fix`, `perf`, `docs`, `ci`, `refactor`, `test`.
- A PR segue `.github/pull_request_template.md` e so entra com o CI verde
  (`.github/workflows/testes.yml`).
- Depois do merge, apagar o branch.
