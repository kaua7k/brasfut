# Próxima onda — backlog pronto para começar

Estado em 2026-09-28, com a `main` em `600918c` (PR #13). Tudo o que foi pedido até
aqui está mergeado; esta página junta o que sobrou, separado pelo que falta para
começar. Decisões já tomadas continuam em `docs/three-amigos/`; o mapa do código é
`docs/MAPA-DO-PROJETO.md`.

## 1. Esperando uma decisão sua

| Item | O que decidir | Proposta na mesa |
|---|---|---|
| **Versão mobile** | Caminho e plataforma dos amigos (Android ou iPhone) | Motor no próprio navegador com Pyodide + PWA no GitHub Pages: sem servidor, save no celular, funciona offline. Começar por um protótipo que mede o tempo de uma semana simulada no celular; depois, passada de layout para ~390 px (Escalação, Mercado e tabelas grandes). A alternativa (servidor na internet) exige refazer `SESSAO` para vários jogadores e tem custo. |
| **Onda 3 com spike** | Se entra nesta onda | Intervalo interativo (`simular` vira máquina de estados) e IA com identidade tática + rebalanceamento (Retranca domina a Pressão; decisão D2 foi não mexer antes). |

## 2. Esperando exemplo do testador (Okumura)

| Item | O que falta |
|---|---|
| 7. Notícia de gol estranha | O texto exato ou um print. Sem isso é chute (`manchetes_da_semana`, `noticia`). |
| 3. Contratações fantasmas | Confirmar se eram craques caindo em clube pequeno na virada. Esse caso foi corrigido na PR #11 (`cabe_na_folha`); se era outra coisa, precisa do exemplo. |

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
- Capitão: pedido de escolher o capitão. Já existe desde a PR #20 (Tornar capitão, na
  ficha); talvez falte deixar isso visível, por exemplo na Escalação.
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
- Guia de estatísticas do campeonato: artilharia, assistências, cartões e notas no estilo
  Sofascore.
- Sócios: hoje o número existe e não gera receita. Decidir se entra como receita (programa
  de sócio-torcedor, que já está no item 3) ou se fica claro na tela que é futuro.

**Modo Caos (pedido depois da lista, com print de 5 plantões)**
- Mais diversidade: eventos novos e mais variações de texto em cada um (o print teve dois
  "gato descoberto" seguidos, com o mesmo texto).
- Evitar repetir o mesmo evento em sequência (ex.: não sortear de novo o mesmo tipo nas
  próximas semanas).
- Frequência em níveis, escolhida ao criar a carreira (ex.: calmo, normal, caótico).

**Fora do jogo**
- Observação sobre páginas do Santos fazendo campanha por um patch no uniforme em
  homenagem a uma mulher falecida. Só registro, sem ação no jogo.

## 3. Pronto para codar (sem decisão pendente)

- **Partida lance a lance na web** — só existe na janela tkinter (`ARQUITETURA-WEB.md`, pontas soltas).
- **Testes do React** — hoje só a API tem teste; o CI já roda `npm run build`, falta ao menos um teste de fumaça das telas.
- **Onda 3 sem spike** (`docs/three-amigos/2026-09-24-rodada-de-melhorias.md`, item 18): mercado disputado e pré-contrato, olheiros e lista de observação, Copinha e convocações. História do clube já saiu (tela Clube); falta conferir os números de `dados_clubes.py`. Economia com escolhas já andou (crédito e sete espaços de patrocínio); falta sócio-torcedor e bicho por vitória.
- **Atalho de patrocínio** — com sete espaços, a Finanças ficou longa: um botão "assinar as equilibradas de todos os espaços" resolve.

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
