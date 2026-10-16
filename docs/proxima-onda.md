# Próxima onda — backlog pronto para começar

Estado em 2026-10-16 (decisões da seção 1); antes disso, 2026-09-28 com a `main` em `600918c` (PR #13). Tudo o que foi pedido até
aqui está mergeado; esta página junta o que sobrou, separado pelo que falta para
começar. Decisões já tomadas continuam em `docs/three-amigos/`; o mapa do código é
`docs/MAPA-DO-PROJETO.md`.

## 1. Decisões de 2026-10-16

- **Versão mobile**: para Android e iPhone. Caminho: motor no navegador (Pyodide) + PWA
  no GitHub Pages, começando pelo protótipo que mede uma semana simulada no celular.
- **Onda 3 com spike**: entram os dois (intervalo interativo e IA com identidade tática +
  rebalanceamento).
- **Ordem combinada**: atalhos e bicho → partida lance a lance na web → mercado disputado e
  olheiros → Copinha e convocações → os dois spikes → protótipo mobile.
- **Exemplos do Okumura** (notícia de gol estranha, contratações fantasmas): descartados.

### Protótipo mobile — feito (2026-10-16)

Motor no navegador com Pyodide 0.29.5 num Web Worker, save no IndexedDB, PWA offline e
workflow do GitHub Pages (`npm run build:pages`, `.github/workflows/pages.yml`); layout de
390 px (menu-gaveta, topo em três linhas, colunas secundárias somem, campo em pé).
Detalhes em `ARQUITETURA-WEB.md`, seção *Versão do celular*. Testado com Playwright:
carreira nova, semana, recarregar (o save volta) e abrir offline.

Medido (*Menu principal > Medir desempenho*, clique de Avançar inteiro, Série A):

| | PC nativo | PC no navegador | celular bom (CPU 2x) | celular médio (4x) |
|---|---|---|---|---|
| Abrir (Pyodide + motor) | – | 2,5 s | 5,2 s | 11,3 s |
| Criar o mundo | 1,0 s | 2,4 s | 4,6 s | 9,4 s |
| Semana, média / pior | 0,63 / 0,72 s | 1,12 / 1,46 s | 2,50 / 3,26 s | 5,16 / 6,10 s |

O que falta para virar produto, em ordem de impacto:
- **Gravar menos**: cada clique regrava o save de 8 MB em JSON (0,9 s de 5,2 s no 4x).
  Gravar a cada N semanas ou só no Salvar/fechar a aba (`visibilitychange`), ou gravar
  compactado (zlib já está na stdlib).
- **Motor mais leve no wasm**: o motor sozinho é ~1,8x o nativo; o `desempenho.py` aponta
  as semanas de Champions/Europa como as mais caras. Ligas de fora em segundo plano mais
  simples no celular seria a alavanca grande.
- **Abrir mais rápido**: importar os `.py` a frio custa 1,8 s no 4x; mandar `.pyc`
  pré-compilado (mesma versão do Pyodide) ou um snapshot do Pyodide.
- **Medir num aparelho de verdade**: o 2x/4x é emulação (freio no Chromium inteiro, porque o
  throttling do DevTools não pega Web Worker). Abrir o Pages num Android intermediário e
  num iPhone e rodar *Medir desempenho*.
- **iPhone**: testar no Safari de verdade (worker em módulo, IDBFS, memória: 86 MB de wasm
  depois da medição) e a política de 7 dias sem uso para site não instalado.
- **Layout**: passada mínima feita em Painel, Escalação, Mercado, Classificação, Elenco e
  Finanças. Faltam Competições (mata-mata), Base, Treino, Estádio, a Mesa de negociação e o
  editor de formação; abrir a ficha é duplo clique (no toque, dois toques).
- **Save entre aparelhos**: exportar/importar o save (arquivo) para levar do PC ao celular.
- **Pages ligado**: no GitHub, *Settings > Pages > Source = GitHub Actions* uma vez.

## 2b. Lista de 2026-09-29 (anotada, nada feito ainda)

Veio com dois prints: a coluna Situação do Elenco (mistura "a venda" com "pendurado liga"
e "gancho liga") e a lista de cartões de uma partida (dois amarelos do mesmo jogador
aparecem como amarelo, amarelo e vermelho, sem dizer que o vermelho veio do segundo
amarelo).

**Interface e navegação**
- ~~Selo de posição: separar ZAG/LAT e VOL/MEI~~ feito (lateral azul claro, volante
  verde-água).
- ~~Coluna Situação~~ feito: no Elenco virou **Jogo** (lesão, suspenso, pendurado) e
  **Mercado** (sem contrato, à venda, emprestado, disponível para empréstimo).
- ~~Mercado: filtro melhor~~ feito: idade mínima, teto mínimo (pelo olheiro, sem revelar o
  potencial), região (Brasil, América do Sul, Europa, outras), só à venda e Limpar.

**Mecânicas**
- ~~Capitão~~ feito: além da ficha (PR #20), escolhido direto na Escalação, abaixo dos
  titulares.
- ~~"Cedível"~~ resolvido: é a marca da IA para quem ela aceita emprestar (alimenta a aba
  Empréstimos). O mundo é sorteado antes da escolha do clube, então o elenco do treinador
  herdava "cedível" e até "à venda" que ele nunca pôs. Agora assumir um clube limpa essas
  marcas (`limpar_vitrine_herdada`); save antigo perde só o "cedível", uma vez.
- ~~Cartões: dois amarelos x vermelho direto~~ feito na lista de lances: o segundo amarelo
  vira um cartão só (metade amarelo, metade vermelho, "2o amarelo, expulso") e o vermelho
  direto diz "vermelho direto". A suspensão já era diferente (1 jogo x 1 a 3).

**Negociações e contratos**
- ~~Oferta 5% abaixo x 100%~~ feito: limite de aceite escondido entre 7% abaixo e 7% acima
  do pedido, fixo na janela (`limite_de_aceite`); vale para contratação e renovação, e a
  renovação em lote deixa de fora quem quer mais que o pedido.
- ~~Flexibilidade com agente livre~~ feito junto: o livre aceita de 14% abaixo a 3% acima,
  e até 4 pontos a menos quanto mais tempo parado.
- ~~Propostas irreais por jogador de divisão baixa~~ feito: medido num clube da Série D,
  quem sondava eram Leverkusen, Ajax, Atalanta e Benfica por jogadores de 46 a 54 de
  overall. Agora o comprador precisa querer o jogador no elenco (`serve_para`: até 3
  pontos abaixo da média dele, ou promessa com teto acima dela); as propostas passam a vir
  da C, da D e de sul-americanos menores.

**Funcionalidades novas**
- ~~Guia de estatísticas~~ feito: tela Estatísticas (menu), liga por liga: artilharia,
  assistências, participação em gols, nota média (mínimo de metade das rodadas, com cor),
  amarelos, vermelhos, melhor ataque e melhor defesa. Os números são do ano em todas as
  competições (o jogo guarda o total por jogador, não por competição).
- ~~Sócios~~ feito: o número passa a pagar mensalidade por série (R$ 50 na A, 30 na B, 20
  na C, 12 na D), perto de 6% da receita do mês; linha própria no extrato e no mês de
  Finanças. Fica para depois: o número de sócios reagir a resultado e preço.

**Modo Caos (pedido depois da lista, com print de 5 plantões)**
- ~~Mais diversidade~~ feito: 11 eventos novos (36 no total: cachorro mascote, reality,
  hacker, vaquinha, veterano que rejuvenesce, enchente, portões fechados, tatuagem do rival,
  vidente, folha vazada, churrasco) e duas a quatro variações de texto na maioria.
- ~~Evitar repetir~~ feito: o mesmo tipo não é sorteado de novo por 10 semanas.
- ~~Plantões na liga do jogador~~ feito (2026-10-01): treinando fora do Brasil, os eventos caem
  nos clubes da liga do país (topo/base por reputação, dinheiro ajustado à economia da liga),
  10 eventos novos com sabor internacional (45 no total) e 3 a 4 textos em quase todos.
- ~~Frequência em níveis~~ feito: calmo, normal ou caótico, escolhido na carreira nova
  (aparece no slot do save).

**Fora do jogo**
- Observação sobre páginas do Santos fazendo campanha por um patch no uniforme em
  homenagem a uma mulher falecida. Só registro, sem ação no jogo.

## 3. Pronto para codar (sem decisão pendente)

- ~~**Partida lance a lance na web**~~ — feito: "Ver lance a lance" no cartão da partida abre `componentes/AoVivo.tsx` (relógio, placar, lances no minuto, intervalo, 1x/2x/4x, estatísticas no apito).
- **Testes do React** — hoje só a API tem teste; o CI já roda `npm run build`, falta ao menos um teste de fumaça das telas.
- **Onda 3 sem spike** (`docs/three-amigos/2026-09-24-rodada-de-melhorias.md`, item 18): ~~mercado disputado e pré-contrato~~ (feito: pré-contrato a partir da semana 19 nos dois sentidos, rival que cobre o lance), ~~olheiros e lista de observação~~ (feito: aba Observados no Mercado, leitura que aperta por mês, avisos do olheiro), Copinha e convocações. História do clube já saiu (tela Clube); falta conferir os números de `dados_clubes.py`. Economia com escolhas já andou (crédito, sete espaços de patrocínio, sócios e bicho por vitória: nenhum, normal, alto ou dobrado nas Finanças).
- ~~**Atalho de patrocínio**~~ — feito: "Assinar as equilibradas de todos" nas Finanças (`assinar_equilibradas`).

## 4. Pontos para acompanhar numa carreira longa

- **Economia de 2026-09-28** (salário achatado acima de 75, marca no patrocínio brasileiro,
  operacional 40%): em 8 temporadas a Série A dobra o caixa mediano e a Europa fica perto do
  de antes. Ver se o clube do jogador não fica rico demais cedo e se a IA brasileira não
  passa a pagar mais que a europeia.
- **Mundo mais rico depois do patrocínio novo** (PR #13): em 12 temporadas ninguém quebra, mas os caixas sobem e depois descem devagar pela folha. Ver se a IA não passa a comprar demais.
- **Tempo da semana**: ~0,48 s de média na semana de liga (limite 0,6 s); o pior caso já passou de 0,6 s uma vez. Qualquer competição nova precisa medir.
- **Save antigo**: cada onda adicionou migração em `migrar`; carreira nova é sempre a referência dos testes.

## 5. Como verificar uma mudança (antes de abrir a PR)

```
cd testes && python -m unittest            # suite, ~3 min (o CI roda o mesmo)
python balanceamento.py --gravar antes.json  # na main, e depois --comparar: partidas
python desempenho.py --gravar antes.json     # idem: tempo por semana (roda sem demissao)
python economia.py --gravar antes.json       # idem: caixa dos clubes em 12 temporadas
cd web && npm run build                      # e commitar web/dist
```

Convenções de branch, título e PR estão no `CLAUDE.md` (seção "Git e PRs").
