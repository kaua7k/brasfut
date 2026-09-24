# BRASFUT no navegador — arquitetura

Documento de trabalho da migração da janela tkinter para uma interface web.
Não é manual de jogo (esse é o `COMO-JOGAR.md`): é o mapa para quem vai
continuar migrando as telas.

## O desenho em uma frase

O motor não mudou. `brasfut.py` continua sendo o jogo inteiro e continua sem
saber que existe interface. O que entrou foi uma casca de três camadas entre
ele e o navegador.

```
brasfut.py            o jogo. Um dict G, nenhuma regra de tela.
  |
  +-- api/sessao.py   segura o G vivo no processo, salva, e é o único dono do cadeado
  +-- api/dto.py      traduz G no que UMA tela precisa. Uma função por tela.
  +-- api/mercado.py  o Mercado e as mesas de negociação (maior que o resto junto)
  +-- api/competicoes.py  estaduais, séries e copas com rodadas e chaveamento
  +-- api/avanco.py   avançar em ritmos: jogo, semana, mês, janela, temporada
  +-- api/campo.py    vaga (GOL, ZAG, LAT...) -> ponto no campo. Vale para as 6 formações.
  +-- api/rotas.py    URL -> função. Zero regra de jogo aqui dentro.
  |
server.py             http.server da stdlib. Serve a API e o web/dist.
  |
web/                  React + TypeScript (Vite). Só desenha.
```

Duas regras que sustentam o resto:

1. **A tela nunca recebe `G` cru.** O save passa de 2 MB e quase nada dele
   interessa a uma tela; pior, mandar o mundo aberto faria o React
   reimplementar regra do motor para saber o que exibir. Cada tela tem o seu
   DTO: o motor decide, o `dto.py` traduz, o React desenha.
2. **Toda ação devolve a tela já recalculada pelo servidor.** O React nunca
   tenta adivinhar sozinho o que mudou depois de avançar a semana. É o que
   mantém os vários pontos da interface dando o mesmo veredito — a mesma razão
   pela qual `diagnostico_escalacao` existe no motor.

## Como rodar

**Jogando** (não precisa de Node):

    iniciar-web.bat

Sobe o servidor Python e abre o navegador em `http://127.0.0.1:8770`.

> Não abra o `iniciar.bat` (janela tkinter) ao mesmo tempo. Os dois gravam no
> mesmo `brasfut_save.json` e um sobrescreve o outro.

**Desenvolvendo** (duas janelas):

    python server.py --sem-abrir      # API no 8770
    cd web && npm run dev             # Vite no 5173, com proxy do /api

**Publicando uma mudança de interface:**

    cd web && npm run build           # gera web/dist, que o server.py serve

O `web/dist` é versionado de propósito: quem só quer jogar não precisa ter
Node instalado.

## Decisões e o porquê

**`http.server` da stdlib, não FastAPI/Flask.** O jogo inteiro é "sem
dependências externas" — é o que deixa o `build-windows.bat` empacotar tudo num
`.exe` só e o que faz o `iniciar.bat` funcionar em qualquer Python. Custou umas
120 linhas de roteamento na mão; comprou a promessa de volta.

**Ouve só em `127.0.0.1`.** É um jogo de uma pessoa na própria máquina, não um
servidor. Não há login nem sessão por usuário, e isso é de propósito.

**Fontes hospedadas localmente** (`web/public/fontes/`, 122 KB). Space Grotesk
e Manrope vêm do design. Buscá-las no Google a cada abertura quebraria o jogo
offline.

**Uma sessão só, com cadeado.** O navegador abre várias conexões em paralelo;
sem o `threading.RLock` de `api/sessao.py`, dois pedidos de avançar semana
jogariam a rodada duas vezes.

**O aviso de time quebrado mora na tela, não na API.** `POST /api/avancar` com
diagnóstico crítico não avança: devolve o texto do aviso e espera um segundo
pedido com `confirmar: true`. A regra de deixar o usuário ver o estrago antes
de entrar em campo vem da janela tkinter e se perderia se a API simplesmente
obedecesse.

**Demissão virou pendência.** No tkinter, `eng.trocar_de_clube` abria um
diálogo modal. Aqui o hook grava uma pendência na sessão e a próxima leitura da
tela conta que há uma escolha travando o jogo. As ofertas seguem a regra do
motor (4 clubes das Séries B/C/D entre os 30 de maior reputação, nunca o que
demitiu), mais *encerrar a carreira*. A pendência vai no save
(`G["pendencia_web"]`), sai quando o clube é escolhido, e `POST /api/avancar`
recusa andar enquanto ela existir.

> Erro que passou numa leva anterior: a pendência nunca era limpa e as ofertas
> eram os 12 maiores clubes do mundo (inclusive o que demitiu). Resultado: a
> janela de demissão voltava a cada semana. O teste parou em "a janela abre" e
> não seguiu até "escolhi o clube e o jogo continua" — `testa_virada.py` agora
> faz esse caminho inteiro com a demissão forçada.

**A virada do ano espera o clique.** `eng.VIRADA_MANUAL = True` (só a web liga):
a semana 38 encerra a temporada e para — topo "Temporada N encerrada", botão
*Começar o ano N+1*, prévia do resumo pelo Painel (`GET /api/resumo`, que usa
`apurar_temporada`, só leitura). O clique aplica a virada e devolve o resumo
completo, que abre antes de tudo (antes até da janela de demissão, porque é ele
que explica a demissão). A pré-temporada continua existindo — mercado aberto,
renovar contrato vencido — e o botão dela virou *Começar o estadual*, com os
avisos do tkinter (quem sai de graça, elenco curto, base pronta). O resumo do
último ano fica no Painel durante a pré-temporada. Terminal e tkinter continuam
virando na mesma chamada.

## O que já migrou

**As 12 telas**: Painel, Elenco, Base, Treino, Escalação, Classificação,
Copas, Mercado, Finanças, Estádio, Infraestrutura e Notícias. A janela tkinter
continua funcionando e continua sendo o único lugar de alguns diálogos (ver
Pontas soltas).

**Escalação.** A troca é em dois cliques explícitos (um titular, um reserva) e
só então o botão *Trocar*; o titular também se marca clicando no disco do
campo. Trocar alguém desliga a alavanca automática, e o recado diz isso. O XI
sai do mesmo `diagnostico_escalacao` do Painel — as duas telas mostram sempre
o mesmo time. O botão da faixa do Painel e o aviso de *time quebrado* ao
avançar levam direto à Escalação.

Decisões de formação (tomadas com um agente de UX, princípios Certainty /
Fluency / Meaning / Forgiveness):

- **Mentalidade nunca remonta o XI** — só mexe nos multiplicadores.
- **Formação no Manual mantém os mesmos 11** e só reorganiza as vagas; no
  Automático a máquina remonta. Quem mudou de vaga pisca no campo e ganha o
  selo *nova vaga* na lista (texto, não só cor).
- **Toda troca de formação tem Desfazer** por 8 s no recado do topo
  (`POST /api/escalacao/desfazer`). O retrato vive em `SESSAO.desfazer_esquema`
  e morre na próxima mexida no time ou ao avançar a semana.
- **Formação personalizada**: botão *Editar formação* transforma o campo numa
  prancheta com −/+ por linha (ZAG 1–5, LAT 0–2, VOL 0–4, MEI 0–5, ATA 0–4,
  total 10), prévia ao vivo sem gravar (`POST /api/escalacao/previa`, 300 ms de
  respiro), Aplicar/Cancelar, Esc cancela com confirmação leve. Steppers e não
  arrastar: funcionam no teclado, no toque e no leitor de tela. Um slot só por
  clube (`c["formacao_custom"]`); contagem igual à de uma pronta vira a pronta.
- **"Limite do elenco"** em vez de *time quebrado* quando a formação pede uma
  posição que o elenco não tem apta (o caso real: zero laterais). O nível não
  baixa — 57% é rendimento real —, mas a faixa diz a causa, avisa que o
  automático já fez o melhor possível e oferece a melhor formação pronta que
  resolve, com ataque/defesa calculados pelo servidor, mais o atalho para o
  Mercado. A classificação mora no motor (`estrutural` no diagnóstico), então
  Painel, Escalação e aviso de avançar dizem o mesmo.
- O select agrupa por linha de defesa (Linha de 4 / 3 / 5), mostra a contagem
  de cada esquema e marca os *sem laterais*.

**Formações no motor.** Eram 6, agora são 18 distintas por contagem (o motor só
enxerga contagem por vaga, então 3-4-1-2 e 3-5-2 seriam o mesmo esquema). Dois
erros antigos corrigidos junto: o 4-5-1 somava **12** jogadores, e o 5-3-2 tinha
a contagem de um 5-4-1 (que agora existe com o próprio nome; o 5-3-2 virou
3 ZAG + 2 LAT + 3 VOL + 2 ATA). Todo lugar do motor que decidia vagas lê agora
`formacao_de(c)`, que também entende a personalizada. Clubes da máquina
continuam no 4-4-2.

**Treino.** Os seis regimes viram cartões clicáveis com evolução, físico e
lesão já julgados pelo servidor (lesão subindo é vermelho). O treino
individual para no primeiro nome que o CT não comporta e conta o porquê. O
botão *Treino individual* da Base usa a mesma rota.

**Estádio.** Preço do ingresso e obra de ampliação. A prévia da obra é só
leitura; quem cobra é o servidor, que refaz a conta e pede confirmação.

**Mercado.** Quatro abas visíveis (Comprar, Empréstimos, Agentes livres, Minha
vitrine). A vitrine junta quem está à venda, as propostas da semana (aceitar /
recusar em lote, com confirmação) e os acertos feitos com a janela fechada
(cancelar). Diálogos migrados:

- **Mesa de negociação** (`componentes/Mesa.tsx`) — compra, empréstimo e
  renovação num componente só. A cada mexida o servidor relê a proposta e
  devolve o semáforo do outro lado (`POST /api/mercado/mesa`); o envio vai
  inteiro (`POST /api/mercado/propor`) e o motor decide.
  **Mudança de regra:** as 3 tentativas por mesa agora vivem na sessão e valem
  pela semana. No tkinter o contador morava no diálogo: fechar e reabrir zerava,
  inclusive a mesa que o outro lado tinha encerrado por proposta ofensiva.
- **Taxa de empréstimo.** O motor cobra taxa quando a conta do dono passa de
  100% do salário (`taxa_emprestimo`), mas o diálogo tkinter nunca a enviava — o
  empréstimo desses jogadores era impossível pela janela. A mesa web mostra a
  taxa e a manda junto.
- **Pôr à venda / reprecificar** em lote (`DialogoVitrine.tsx`) com os
  percentuais do valor de mercado calculados no servidor e ajuste por linha.
- **Ceder por empréstimo** (`DialogoCeder.tsx`): uma linha por par
  jogador/clube, já com a melhor de cada um marcada. O percentual é relido do
  motor na hora de ceder, nunca aceito do cliente.
- **Renovar**: a mesa de renovação, uma por vez quando há vários marcados.
- A **ficha** aberta no Mercado traz *Negociar* / *Pedir emprestado* junto.

Os botões *Pôr à venda*, *Ceder empréstimo* e *Renovar* do Elenco abrem esses
mesmos diálogos, e a resposta traz de volta a tela de quem pediu (Elenco ou
Mercado).

**Competições** (item *Competições* do menu, antigo *Copas*; o hash continua
`#copas`). Cada torneio com a profundidade que tem: pontos corridos mostra a
tabela inteira, o navegador de rodadas (abre na próxima) e a faixa *Seus
jogos* com placar e V/E/D; mata-mata mostra fase por fase com ida, volta,
agregado e pênaltis, a próxima fase já sorteada e as que faltam, e numa frase
onde o seu clube está ("Vivo. Segunda fase contra Fluminense na semana 4, ida
fora"). Para isso o motor passou a guardar o que antes descartava:

- `liga["resultados"]` e `est["resultados"]`: o placar de cada rodada (antes
  só a última, em `ultimos`).
- `cp["historico"]`: existia no save mas nunca era preenchido. Agora cada fase
  jogada entra com os confrontos.
- `cp["sorteio"]`: **o sorteio da fase seguinte sai quando a anterior acaba**,
  e não mais na hora do jogo (`sortear_confrontos` / `sorteio_da_copa`). Com
  isso o Painel mostra o adversário da copa em vez de "definido no sorteio".
  Save antigo ganha o sorteio na primeira leitura; rodadas e fases jogadas
  antes da mudança aparecem como "sem registro", sem placar inventado.

**Simular.** Botão *Simular…* ao lado de *Avançar semana* (que continua sendo
uma semana só, para nunca pular meio ano por engano). Ritmos: jogo a jogo (até
o próximo jogo do seu clube), 1 semana, 1 mês, até a janela abrir/fechar e a
temporada toda, com as paradas da janela tkinter (lesão de titular, janela,
proposta, time quebrado). O navegador roda o laço uma semana por pedido
(`POST /api/avancar` com `paradas` e `leve`), então a barra anda, o relato de
cada semana aparece na hora e *Parar* vale no fim da semana. Quem diz quantas
semanas cada opção cobre e por que parar é o servidor (`api/avanco.py`).

**Correções desta leva.** Barra de ações das listas (Mercado, Elenco, Base,
Treino) presa no rodapé com `position: sticky` — antes ficava depois do último
dos 60 jogadores; `overflow: clip` no painel porque `hidden` anula o sticky.
Mesa de negociação: depois do sim o formulário sai e fica só o cartão do
negócio fechado. Com a janela fechada, quem tem acerto agendado aparece
*acertado* na lista e a mesa não reabre (antes dava para agendar o mesmo
reforço duas vezes). E um bug que derrubava a tela inteira: no Chromium novo
`scrollIntoView()` devolve uma Promise, e um `useEffect(() => ref.scrollIntoView())`
sem chaves entregava essa Promise ao React como função de limpeza. **Regra:
efeito de uma linha sempre com chaves.**

**Casca.** O endereço guarda a tela no hash (`/#elenco`): F5 não volta ao
Painel, e agora o Voltar/Avançar do navegador também troca de tela.
Marcações nas grades usam `alternarMarca` com setter funcional (dois cliques
rápidos não se apagam) e zeram quando a tela volta do servidor, para nenhuma
ação em lote apontar para quem já saiu. `[hidden]` ganhou `display:none
!important` e `.tela > *` não encolhe — era isso que cortava a lista do Elenco
sem dar scroll.

## Receita para migrar a próxima tela

Exemplo com `tela_elenco` (brasfut_app.py:1744):

1. **`api/dto.py`** — escreva `def elenco():` devolvendo só o que a tela
   desenha. Nada de regra nova: se precisar de um cálculo, ele já existe no
   motor ou deveria existir lá.
2. **`api/rotas.py`** — `@rota("GET", "/api/elenco")`. Ação que escreve no
   mundo pega `SESSAO.cadeado` e salva antes de responder.
3. **`web/src/tipos.ts`** — o espelho do DTO. É o que faz o TypeScript cobrar a
   tela inteira quando o Python mudar um campo de nome.
4. **`web/src/api.ts`** — uma linha no objeto `api`. Nenhum componente chama
   `fetch` direto.
5. **`web/src/telas/Elenco.tsx`** — use `<CabecalhoTela>` e `<Grade>`, que já
   existem, e as classes de `estilo/base.css` (`.painel`, `.cartao`,
   `.barra-acoes`...). Estilo inline só para o que é realmente pontual.
   **Cuidado com nome de classe repetido**: `.centro` já significou duas
   coisas (centralizar a tela e centralizar uma coluna), e as células herdaram
   `padding: 40px` — linhas de 133 px em vez de 35.
6. **`api/dto.py`, lista `MENU`** — troque o `False` do item para `True`.
7. **`web/src/App.tsx`** — despache a tela nova pelo estado `tela`.

As 12 telas estão de pé. Quando os diálogos que faltam (ver abaixo) também
estiverem, `iniciar.bat` passa a chamar o `server.py` e o `brasfut_app.py` sai
de cena.

## Pontas soltas conhecidas

- **Acentuação.** O motor escreve sem acento ("escalacao", "Financas") porque
  nasceu para terminal. O navegador não tem essa limitação, mas acentuar só a
  metade que eu escrevo deixaria a tela mestiça. Normalizar isso é uma
  passagem à parte, no motor.
- **Save compartilhado.** Nada impede hoje abrir a janela e o navegador ao
  mesmo tempo. Um arquivo de trava resolveria.
- **Sem testes automatizados.** O projeto não tem nenhum. A API é conferida à
  mão: leitura contra o save real, e **ação destrutiva sempre contra uma cópia**
  (aponte `eng.SAVE` para outro arquivo antes de importar a sessão).
- **Diálogos que só existem no tkinter**: a partida lance a lance
  (`Partida`), o resumo da temporada (`ResumoTemporada`), boas-vindas e ajuda.
- **Agentes de UX do plugin `bnp-frontend`** (*Design Director* e *SE: UX
  Designer*) não sobem no Claude Code: o `tools` deles usa nomes do VS Code
  Copilot (`web/fetch`, `codebase`...). A consulta de UX desta leva rodou num
  agente geral com a skill `ui-ux-pro-max`.
- **Testes**: continuam manuais, mas agora com roteiro. Os scripts usados nesta
  leva (API contra cópia do save + Edge headless via DevTools) não ficaram no
  repositório; vale trazê-los para uma pasta `testes/`.
