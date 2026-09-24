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

> Um BRASFUT por pasta. Janela, navegador e terminal gravam no mesmo
> `brasfut_save.json`; o segundo a abrir recusa com um aviso (ver *Trava do
> save*).

**Testando** (sem Node, sem pip):

    cd testes && python -m unittest -v

Uns 20 s. Ver *Testes* abaixo.

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

**Mercado.** Quatro abas visíveis (Comprar, Empréstimos, Agentes livres, Vender —
antes *Minha vitrine*). A aba Vender junta quem está à venda, as propostas da semana (aceitar /
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

**Estaduais reais.** Acabou o turno único de 7 rodadas (`RODADAS_ESTADUAL`
saiu). Cada estadual tem o formato da vida real, em `FORMATOS_ESTADUAL`
(brasfut.py): primeira fase (`turno`, `returno` ou `cruzado` — grupos em que
cada clube enfrenta os dos outros grupos) e mata-mata até a final em ida e
volta. Paulistão com 4 grupos cruzados e quartas dentro do grupo; Carioca com
Taça Guanabara e semifinal; Copa do Nordeste com 2 grupos cruzados. Mata-mata
de jogo único é na casa de quem fez melhor campanha; empate vai para os
pênaltis, sem gol fora. Estado com poucos clubes cai num formato menor
(`_formato_estadual`). Na tela, a Competições mostra os grupos, a primeira
fase como pontos corridos e o mata-mata por cima (`_estadual` em
`api/competicoes.py`), com a frase da campanha (`campanha_estadual`). Quem
pergunta se o estadual acabou usa `estadual_terminado(est)`, não mais
`est["campeao"]`.

**Verba para contratar e contraproposta.** O caixa deixou de ser o limite de
compra. Do caixa sai uma reserva de `RESERVA_MESES` (3) meses de folha e
custos, sem contar receita (`reserva_custos`); o que sobra é a verba
(`verba_contratacao`). O salário do reforço entra na reserva antes do passe,
então a mesa de negociação recusa pela verba *com* o salário proposto. Painel,
Finanças (bloco `mensal`: receitas, folha, estrutura, saldo e quanto tempo o
caixa aguenta no vermelho) e Mercado mostram a mesma verba. O Painel ganhou o
aviso de **contratos acabando** (último ano ou vencido), com os ids indo para
a fila de renovação. A aba *Minha vitrine* virou **Vender**, e com uma única
proposta marcada dá para mandar **contraproposta** (`POST
/api/mercado/propostas/contra`, `eng.contraproposta`): um número limitado por
oferta por semana (`contrapropostas_restantes`), depois a oferta fica como
está.

**Ordenar listas.** Clicar no cabeçalho de uma coluna da `<Grade>` ordena:
número do maior para o menor, texto de A a Z; o segundo clique inverte e o
terceiro volta à ordem do servidor. A chave sai do texto da célula
(`chaveDeOrdem`: "R$ 1.20 mi", "450 mil", "65%", "3 ano(s)"; posição na ordem
do campo, GOL→ATA), então toda coluna já nasce ordenável. Na coluna, `ordem`
só é preciso quando o texto engana (`null` desliga); `ordenavel={false}`
desliga a grade inteira (tabela de campeonato), `memoria` guarda a escolha no
navegador e `aoMarcarTodos` põe a caixa de marcar todos no cabeçalho. Vale
para Mercado, Elenco, Base e Treino.

## Versão 2.5: carreira e mundo

**Menu principal** (`telas/Abertura.tsx`): Iniciar, Configurações e Sobre.
Iniciar leva a *Continuar* (o menu já diz treinador, clube e temporada do
save, lidos por `GET /api/estado` sem adotar o mundo) ou a *Carreira nova*,
que pede o nome do treinador e as opções da carreira antes de criar o mundo.
A escolha de clube mostra as quatro séries.

**Opções da carreira** ficam no save, em `G["opcoes"]` (`opcoes_carreira`,
`definir_opcoes_carreira` no motor): `dificuldade` (`DIFICULDADES`: risco de
demissão e caixa do primeiro clube), `sem_demissao` (`avaliar_diretoria`
nunca demite) e `investidor` (`APORTE_INVESTIDOR` por série, aplicado em
`comecar_no_clube`). Save antigo joga com `OPCOES_PADRAO`, que é o jogo de
sempre. **Configurações** globais (escala da interface, reduzir animações e os
padrões da carreira nova) moram fora do save, em `brasfut_config.json`
(`api/config.py`, `GET/POST /api/config`); só chaves conhecidas são gravadas.

**Carreira do treinador** (bloco CARREIRA DO TREINADOR em brasfut.py):
- `G["tecnico_rep"]` (1–99) anda com meta cumprida (+6) ou não (−5),
  acesso/rebaixamento e títulos (`PESO_TITULO`). Save antigo começa em
  35 + 3 por temporada de histórico, até 70.
- `G["carreira"]`: uma passagem por clube com jogos, V/E/D, gols, títulos e
  marcos. **Toda troca de clube passa por `assumir_clube`**, que fecha a
  passagem com o motivo da saída; título de qualquer clube passa por
  `dar_titulo`, e jogo do meu clube por `contar_jogo_na_carreira` (dentro de
  `registrar_placar`). Não troque `G["clube"]` na mão.
- **Propostas de emprego**: `sondar_treinador` roda uma vez por mês no
  Brasileirão. Chance maior com o time em cima da meta e reputação alta;
  time afundando (6+ posições abaixo da meta) não atrai ninguém. Quem liga
  cabe em `max(rep + 8, rep do clube atual + 6)`. Valem 4 semanas, até 3 de
  uma vez; `POST /api/carreira/proposta` aceita ou recusa.
- **Pedir demissão** (`POST /api/carreira/demitir`) vira a mesma pendência
  da demissão, com `saida: "pediu demissao"` e ofertas de
  `ofertas_ao_demissionario`. A demissão pela diretoria segue a regra antiga.
- Tela **Carreira** (`telas/Carreira.tsx`, `GET /api/carreira`): reputação,
  sala de troféus somada, cada passagem e o botão de pedir demissão (com
  segundo clique).

**Pelo mundo** (`G["feed"]`, bloco PELO MUNDO): `manchete()` registra goleada
(4+ gols), zebra (20+ de reputação), troca de líder das Séries A e B, grande
brasileiro eliminado, título de qualquer clube, contratação de R$ 8 mi ou
mais e lesão de 4+ semanas de craque (78+). No máximo 4 manchetes de
resultado por semana (as maiores). Nenhuma manchete inventa fato: tudo sai de
algo que o motor decidiu. Aparece no Painel (*Pelo mundo*) e na aba de
Notícias.

**Lesões**: `RISCO_LESAO_JOGO` 0.026 → 0.015 e `SEMANAS_LESAO` com lesão
longa rara. Média de lesionados por clube da Série A caiu de 0,81 para 0,29.

**Libertadores e Sul-Americana com fase de grupos** (bloco FASE DE GRUPOS):
32 clubes em cada (8 brasileiros + 24 estrangeiros; mundo sem estrangeiros
bastantes completa a Sul-Americana com brasileiros), 8 grupos de 4 sorteados
por potes de reputação evitando compatriotas, 6 rodadas em `SEMANAS_GRUPOS`.
Cada grupo é uma mini-liga (`registrar`/`classificacao` das séries). Durante
os grupos os 32 estão em `cp["vivos"]` e `sorteio_da_copa` devolve vazio;
`fechar_grupos` (fim da semana 16) transforma o resultado no mata-mata de
sempre: Libertadores com 1º e 2º nas oitavas e o 3º no playoff da
Sul-Americana; Sul-Americana com 2º x 3º da Libertadores no playoff e o 1º
esperando em `cp["espera"]` até entrar nas oitavas. Quem pergunta pelo estado
da copa usa `fase_da_copa`, `vivo_na_copa`, `proxima_semana_copa` e
`jogo_de_grupo` — `nome_fase(len(vivos))` erra durante os grupos e o
playoff. Vitória de brasileiro nos grupos paga `PREMIO_VITORIA_GRUPO`. Save
antigo termina a temporada corrente no formato velho, ganha os 16 clubes
estrangeiros novos em `migrar` e pega os grupos na virada.

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

8. **`testes/test_telas.py`** — ponha a rota nova na lista `TELAS`.

As 12 telas estão de pé. Quando os diálogos que faltam (ver abaixo) também
estiverem, `iniciar.bat` passa a chamar o `server.py` e o `brasfut_app.py` sai
de cena.

## Trava do save

`eng.travar_save()` (brasfut.py, logo depois de `carregar`) pega um lock do
sistema operacional em `brasfut_save.json.lock` — `msvcrt.locking` no Windows,
`flock` no resto — e segura enquanto o processo vive. Os três pontos de
entrada chamam antes de tudo: `server.py`, `brasfut_app.py` e o `main` do
terminal. Quem chega em segundo mostra `eng.AVISO_TRAVA` e sai (o servidor com
código 1, para o `iniciar-web.bat` pausar com a mensagem na tela). Como o lock
é do SO, processo morto ou fechado à força solta sozinho: não existe trava
velha para apagar na mão. `--sim` não trava, porque não grava no save.

## Testes

`testes/`, só com `unittest` da stdlib — a mesma promessa de zero dependência.

    cd testes && python -m unittest -v

- **`apoio.py`** aponta `eng.SAVE` para `testes/_tmp/` **antes** de importar
  `api`, e chama as rotas pelo `rotas.despachar` que o `server.py` usa, sem
  HTTP. `chamar(metodo, caminho, corpo, status)` já confere o status.
- **`test_telas.py`** abre todas as telas de leitura contra uma cópia do save
  real e avança uma semana. Pula se não houver `brasfut_save.json`.
- **`test_virada.py`** mundo novo, temporada inteira até a semana 38 parar,
  prévia do resumo, clique da virada e demissão forçada até o clube novo
  jogar a semana seguinte. É o caminho que já quebrou (ver *Demissão virou
  pendência*).
- **`test_trava.py`** dois processos no mesmo save: o segundo é recusado e,
  quando o primeiro sai, o lock é liberado.
- **`test_carreira.py`** nome e opções da carreira nova, aporte do
  investidor, sem demissão, pedir demissão até o clube novo, proposta aceita,
  jogos contados na passagem, feed do mundo e `/api/config`.
- **`test_continentais.py`** grupos da Libertadores e da Sul-Americana até o
  playoff e as oitavas, e save antigo ganhando os clubes que faltam.

Todo teste que mexe no save confere no fim que o hash do save real não mudou.
A interface (React) ainda é conferida à mão. Roteiro que funciona: copiar
`api/`, `brasfut.py`, `server.py`, `web/dist` e uma cópia do save para uma pasta
temporária, subir com `BRASFUT_PORTA=8791 python server.py --sem-abrir`,
preparar o estado por `curl` na API e fotografar com
`msedge --headless=new --user-data-dir=<pasta nova> --screenshot=... URL/#tela`
(o arquivo aparece alguns segundos depois de o processo sair).

## Pontas soltas conhecidas

- **Diálogos que só existem no tkinter**: a partida lance a lance
  (`Partida`, brasfut_app.py), as boas-vindas (`Boas_vindas`) e a ajuda
  (`Ajuda` — o botão já está no menu lateral, desativado). O resumo da
  temporada já migrou (`componentes/Resumo.tsx`).
- **Acentuação.** O motor escreve sem acento ("escalacao", "Financas") porque
  nasceu para terminal. O navegador não tem essa limitação, mas acentuar só a
  metade que eu escrevo deixaria a tela mestiça. Normalizar isso é uma
  passagem à parte, no motor.
- **Testes de interface.** A API tem testes; o React não.
- **Agentes de UX do plugin `bnp-frontend`** (*Design Director* e *SE: UX
  Designer*) não sobem no Claude Code: o `tools` deles usa nomes do VS Code
  Copilot (`web/fetch`, `codebase`...). A consulta de UX desta leva rodou num
  agente geral com a skill `ui-ux-pro-max`.

## Histórico

O projeto está em git desde 2026-09-24. O primeiro commit guarda a pasta
`.backup-pre-patch` (versões 2.0–2.4 do motor e o antes de cada leva); ela
saiu no commit seguinte. Para ver uma versão antiga:
`git show <primeiro-commit>:.backup-pre-patch/brasfut.py.v2.3`.
