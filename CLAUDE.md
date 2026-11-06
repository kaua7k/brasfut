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

## Arquitetura em poucas linhas

Um motor só (`brasfut.py`, Python stdlib pura, sem pip) atende três
interfaces: terminal (`python brasfut.py`), janela tkinter
(`brasfut_app.py`) e web. Na web, `server.py` (`http.server`, só em
127.0.0.1:8770, porta via `BRASFUT_PORTA`) serve `web/dist` e a API
`api/` (`rotas.py` URL→função, `sessao.py` guarda o `G` em memória sob um
`RLock` e salva, `dto.py` traduz `G` para cada tela). A versão celular
(`npm run build:pages`) roda o mesmo motor no navegador via Pyodide num Web
Worker, com o save no IndexedDB — por isso o motor não pode ganhar
dependência fora da stdlib. Detalhes: `ARQUITETURA-WEB.md`.

## Comandos

- Jogar na web: `python server.py` (`--sem-abrir` para não abrir o
  navegador). Exige `web/dist` compilado.
- Front em desenvolvimento: `cd web && npm run dev` (Vite no 5173, faz proxy
  de `/api` para o `server.py` no 8770 — suba os dois).
- Build do front: `cd web && npm run build` (`tsc -b && vite build`).
  **`web/dist` é versionado**: depois de mexer em `web/src`, rode o build e
  commite `web/dist` junto (o CI avisa se ficou velho).
- Build da versão celular/GitHub Pages: `cd web && npm run build:pages`
  (gera `web/dist-pages`, ignorado pelo git).
- Um arquivo de teste: `cd testes && python -m unittest -v test_mercado_regras`;
  um caso só: `python -m unittest test_mercado_regras.Classe.test_x`.
- Harness lentos (fora da suite e do CI): `testes/balanceamento.py` (rodar
  quando a mudança altera resultado de partida, tática, força, IA) e
  `testes/desempenho.py` (quando a mudança altera tempo).
- Executável Windows: `build-windows.bat` (PyInstaller, gera `dist/BRASFUT.exe`).

Testes importam `testes/apoio.py` **antes** de `api`: ele aponta o motor para
uma cópia do save em `testes/_tmp`. O `brasfut_save.json` da raiz é o save
real do jogador — nunca escreva nele nem o apague (nem o `.lock`, a menos que
o servidor esteja comprovadamente parado).

## Git e PRs

- Um branch por tema, a partir da `main` atualizada: `tipo/assunto`
  (ex.: `feat/ligas-sul`, `fix/salario-livre`). Nao reaproveitar branch de PR
  ja mergeada.
- Titulo de commit e de PR no formato `tipo(escopo): descricao`, com `tipo`
  entre `feat`, `fix`, `perf`, `docs`, `ci`, `refactor`, `test`.
- A PR segue `.github/pull_request_template.md` e so entra com o CI verde
  (`.github/workflows/testes.yml`).
- Depois do merge, apagar o branch.
- Com o CI verde, o merge e feito direto, sem esperar confirmacao (pedido do
  Kaua em 2026-09-28). Vermelho: corrigir e esperar o verde de novo.
- A copia local do Kaua fica em `C:\Users\KauaLima\Documents\bras2.0\<N>.0`
  (11.0, 12.0...). A sessao na nuvem nao alcanca o PC dele: a cada atualizacao
  mergeada, lembrar de rodar `baixar-nova-versao.bat`, que baixa a `main` ja
  extraida na proxima pasta e leva o save junto.
