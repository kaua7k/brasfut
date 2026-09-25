# BRASFUT 2.4

Gerenciador de futebol brasileiro. Séries A, B, C e D, Copa do Brasil, Libertadores,
Sul-Americana, mercado com negociação, empréstimos, estádio e categorias de base.

Quatro arquivos, todos na **mesma pasta**.

| Arquivo | Para que serve |
|---|---|
| `iniciar.bat` | **É por aqui que se joga.** Dois cliques. |
| `brasfut.py` | o motor e os 1.079 jogadores reais embutidos |
| `brasfut_app.py` | a janela, com modo visual e modo linha |
| `build-windows.bat` | gera o `BRASFUT.exe`, opcional |

## Jogar

Dois cliques no `iniciar.bat`. Ele se vira: abre o executável se existir, senão abre pelo
Python, e se não achar Python explica o que instalar (Microsoft Store, busque por
"Python", não pede admin).

## Os dois modos

O botão **Modo linha**, no canto superior direito, alterna a qualquer momento sem perder
nada — os dois mexem no mesmo jogo.

**Visual**: menu lateral, tabelas clicáveis, ficha do jogador com dois cliques, mercado
com filtros e negociação em janela.

**Linha**: console preto igual ao cmd. Comandos: `semana`, `elenco`, `escalacao`,
`troca 9 15`, `auto` (liga e desliga a escalação automática), `form 4-3-3`,
`tatica ofensivo`, `tabela B`, `copas`, `financas`, `stats`, `mercado ATA`, `noticias`,
`salvar`, `visual`, `ajuda`. No menu do terminal, Base, Treino e o resumo da temporada
também têm tela própria.

Quem quiser só terminal, sem janela: `python brasfut.py`, com `--discreto` para texto
cru sem cor e `--sim 5` para assistir cinco temporadas rodando sozinhas.

## Save

Grava sozinho ao fim de cada semana, no `brasfut_save.json` da pasta do jogo. Ao abrir,
pergunta se quer continuar. O botão **Salvar** força a gravação quando quiser.

## O que muda a sua temporada

**A alavanca da escalação.** No alto do cartão **ESCALACAO**, no Painel, e também na tela
Escalação, tem um botão de duas posições:

- **AUTO** — antes de cada jogo a máquina monta o melhor time disponível para o seu
  esquema, já contando lesão, suspensão, físico e improviso. É o padrão, inclusive em
  save antigo.
- **MANUAL** — o time é seu. O jogo só repõe quem não pode entrar em campo, nunca
  reotimiza por cima de você.

Trocar jogador na mão — pelo botão **Trocar selecionados** ou pelo `troca 9 15` — desliga
a alavanca sozinha: se você mexeu, você assumiu o time. Ser demitido e pegar outro clube
não muda a sua escolha, ela vai junto.

O time automático agora é resolvido de uma vez, e não vaga por vaga. A versão antiga era
gulosa: servia primeiro a posição mais escassa e, quando chegava na lateral, sobrava um
atacante para jogar ali. Agora as onze vagas são decididas juntas, maximizando a força do
time inteiro — o lateral reserva cobre a zaga por 80% e o atacante fica no ataque.

**Escalação.** A coluna **VAGA** mostra onde cada um está jogando de verdade: `ZAG`
quando é a posição dele, `LAT>ZAG` em amarelo quando está improvisado, com o rendimento
ao lado — lateral na zaga rende 80%, atacante na zaga rende 45%. Sem goleiro apto alguém
veste a luva e a defesa despenca. Titular machucado é substituído por outro da mesma
posição, e chega notícia avisando quem entrou no lugar de quem.

## A partida

O jogo é a partida — e ela deixou de ser um placar que aparece do nada. Agora acontece em
três períodos (0-45, 45-70, 70-90), e entre eles o time muda: as pernas cansam, o banco
entra, alguém se machuca, alguém é expulso e sai de campo de verdade.

**O meio-campo disputa.** Existe posse de bola, e ela sai da força de meio-campo dos dois
lados — quem tem VOL e MEI melhores manda no jogo — somada ao plano tático. Quem tem a
bola cria mais chances. Antes o XI virava dois números (ataque e defesa) e a formação só
mudava quantas vagas existiam de cada posição.

**Chances e conversão.** O xG de cada time continua saindo da mesma conta calibrada de
força contra força, mas agora ele é decomposto em *finalizações × conversão*. É aí que a
tática vira decisão: o mesmo xG pode virar 18 chutes de fora da área ou 8 chances dentro
dela. Daí saem as estatísticas reais do jogo — posse, finalizações, chutes no gol, defesas
do goleiro, escanteios e faltas.

**O banco existe.** Até 5 substituições, banco de 9, janelas no intervalo e aos 70
minutos, mais troca forçada por lesão. Quem entra é o reserva com melhor afinidade com a
vaga aberta, e só entra se melhorar o time naquele estado — nos últimos 20 minutos, perna
descansada compensa um pouco de qualidade. Medido: ter banco vale **+0,55 ponto por jogo**
contra jogar só com os 11.

**A tela da partida.** Avançar uma semana abre o jogo: o placar grande, as estatísticas
lado a lado em barras, o minuto a minuto (gols com assistência, cartões, lesões,
substituições) e a **nota de cada jogador** do seu time, com o melhor em campo destacado.
Nota 6,0 é jogo correto; gol vale +1,0 e assistência +0,5, e o resultado do time entra na
conta de todo mundo. Dá para reabrir clicando no placar do Painel. Na interface web, o resumo (gols e cartões com minuto, posse, chutes, melhor em campo) aparece no Painel na volta do avanço e no fim do Simular, e as bolinhas das últimas partidas trocam o jogo mostrado; "Ver detalhes" abre as notas dos dois times. No modo linha, o
relatório agora traz as estatísticas, as substituições e o melhor em campo.

## Plano de jogo

A **Tática** (Retranca a Pressão total) continua sendo a mentalidade. Em cima dela vêm
cinco botões, na tela de Escalação, e nenhum deles é só vantagem:

| Botão | Opções | O que troca |
|---|---|---|
| Pressão | Baixa / Média / Alta | posse e volume contra espaço nas costas e cartão |
| Linha | Recuada / Média / Adiantada | linha baixa entrega o campo mas fecha a área; alta comprime e concede mais |
| Ritmo | Cadenciado / Normal / Intenso | cadenciado faz menos chutes e melhores; intenso faz muitos e piores |
| Largura | Fechado / Normal / Aberto | por dentro converte melhor; aberto cruza muito e converte pouco |
| Saída | Curta / Direta | curta domina a bola e erra perto da área; direta abre mão da posse |

O cabeçalho do bloco mostra o efeito somado (posse, volume de chances, qualidade, o quanto
o time entrega e a fadiga). E há **transição**: quem espera atrás com linha recuada
castiga quem sobe a linha e pressiona alto. Calibrado para que nenhuma escolha domine —
contra um adversário igual, as opções ficam entre 1,58 e 1,88 ponto por jogo, e o que
decide é o confronto, não a opção.

### Se o jogo apertar

Ainda na Escalação, abaixo do plano: uma instrução para cada situação — **se estiver
perdendo** e **se estiver vencendo** — com o minuto (a partir do intervalo, 46', ou da
janela dos 70, 71') e a mentalidade. O jogo não pausa: a partida confere o placar nessas
duas paradas e troca a mentalidade sozinha. Vale enquanto o placar pedir; se virar, volta
a mentalidade de antes. A troca aparece no resumo da partida ("71' vira Ofensivo").

A máquina também reage, com regra fixa aos 71': perdendo, sobe um degrau (Equilibrado →
Ofensivo); vencendo, desce um (Equilibrado → Contra-ataque). Medido em 16 mil jogos: gols
por jogo de 2,75 para 2,77, empates de 24,2% para 23,4%, e quem perde aos 70 escapa da
derrota um pouco menos (11,9% → 10,7%): segurar o resultado rende mais do que ir para o
tudo ou nada.

## Simular e renovar em lote

**Simular.** Os ritmos (jogo a jogo, 1 semana, 1 mês, até a janela, temporada toda) são
cartões; as condições de parar ficam logo abaixo. O relato mostra cada semana num bloco:
resultado, placar com o mandante primeiro, seu time em destaque e a competição. No
mata-mata, o jogo que decide diz o que aconteceu: "Classificado nos pênaltis · agregado
3 x 3", "Eliminado · agregado 1 x 2", "Campeão". Lesão e proposta nova aparecem na semana
em que aconteceram, e no fim vem o resumo da última partida.

**Renovar vários.** Marque os jogadores no Elenco (ou use "Renovar os N" no Painel) e uma
janela só mostra o que cada um pede para renovar, num prazo único para todos (5 anos por
padrão; prazo longo sai um pouco mais barato por mês), e a folha antes e depois. Um clique
renova todos pelo que pediram. Quer pechinchar? Marque só aquele jogador: abre a mesa de
negociação, com três tentativas.

## A diretoria

A diretoria não espera o fim do ano para ter opinião. No cartão **Objetivo da temporada**,
no Painel, fica a **confiança da diretoria**: um número de 0 a 100, a tendência das últimas
4 semanas e, logo abaixo, por que ele mudou na última semana ("-8 derrota para o Espanyol",
"+1 dentro da meta").

- **Resultado contra o esperado.** Ganhar de quem é mais forte vale muito; perder para quem
  é mais fraco custa caro. O esperado vem do tamanho dos dois elencos e do mando de campo.
  Clássico vale o dobro, para o bem e para o mal.
- **Posição contra a meta.** No Brasileirão (da 6ª rodada em diante), a posição puxa a
  confiança aos poucos para um patamar: alto dentro da meta, baixo longe dela, mais baixo
  ainda na zona de rebaixamento. Sozinha, a tabela leva no máximo ao aviso.
- **Caixa no vermelho** também pesa.
- A **dificuldade** da carreira multiplica só as quedas.

Abaixo de **30** a diretoria avisa. Depois do aviso, se a confiança cair abaixo de **15**, a
demissão pode vir já na semana seguinte, no meio do ano. Voltar acima de 40 derruba o aviso.
No fim da temporada a avaliação de sempre continua, mas pesa a confiança: quem chega com a
diretoria do lado quase não cai, quem chega avisado cai muito mais. Clube novo começa em 60;
ano novo anda metade do caminho de volta aos 60. No modo sem demissão a diretoria só fala.

Medido em seis carreiras de 50 semanas (Séries A a D): a confiança andou entre 37 e 82 em
cinco delas; o Flamengo com meta de título caiu até 19, levou o aviso e se recuperou.
Ninguém foi demitido.

**Os outros clubes também demitem.** No fim do turno e no fim do ano, clube que despencou
seis posições abaixo do próprio tamanho e está no terço de baixo manda o treinador embora
(sai no feed do mundo). A vaga fica aberta dez semanas, e é esse clube que liga primeiro
quando você está indo bem.

## O que a varredura encontrou e o que mudou

- **Empréstimo era porta dos fundos.** A exigência passava de 100% para jogador bom, mas o
  limite de 100 transformava "impossível" em "pague o salário inteiro": 9 dos 10 melhores
  da Série A vinham de graça, e dava para montar 7 dos 11 titulares assim. Agora o excesso
  vira **taxa de empréstimo** em dinheiro, peça de time não troca por clube menor,
  intocável não sai nem por empréstimo, e o elenco comporta no máximo **4 emprestados**.
  Medido depois do conserto: 0 de 10 craques vêm só pagando salário.
- **O artilheiro era sorteado pela posição de origem, não pela vaga.** Um atacante
  improvisado na zaga continuava com peso de gol de atacante enquanto o cálculo de força
  já o tratava como zagueiro. As duas metades do motor discordavam sobre onde o jogador
  estava; agora as duas leem a vaga real.
- **O limite de elenco era menor que os elencos reais.** Com teto de 32, oito clubes
  grandes já nasciam travados — sem poder comprar, pegar emprestado nem subir um garoto da
  própria base. O teto passou para **40**, e a reposição automática também o respeita.

**O Painel.** A tela inicial responde uma pergunta só: dá para avançar a semana agora? Em
cima, a faixa de prontidão diz o veredito em uma linha — **TIME PRONTO**, **RESSALVA** ou
**TIME QUEBRADO** — com o custo em número, e leva direto para a escalação. A mesma cor
aparece na régua embaixo do botão **Avancar semana**, no rodapé, e no próprio botão, que
vira vermelho e passa a dizer **Avancar assim mesmo** quando o time está quebrado (e
pergunta antes de entrar em campo assim; nunca bloqueia — entrar quebrado é direito seu).
Abaixo vêm o XI que entra em campo com vaga e improviso de cada um, o próximo adversário
com ataque e defesa lado a lado, o objetivo da temporada com a pressão da diretoria, um
recorte da tabela em volta do seu clube, os artilheiros e os últimos acontecimentos.

**Calendário.** O ano tem três fases, e a interface diz sempre em qual você está:

1. **Pré-temporada** — mercado aberto, nada acontece até você mandar. O botão de avançar
   fica verde e diz *Começar o ano*.
2. **Estadual** — abre a temporada, como no calendário de verdade, e no formato de verdade:
   primeira fase, mata-mata e final em ida e volta. A régua do topo fica roxa e o botão diz
   *Avançar rodada*.
   - **Paulistão**: quatro grupos; cada clube enfrenta os dos *outros* grupos. Os dois
     primeiros de cada grupo fazem as quartas entre si (1º x 2º), em jogo único; semifinal
     em jogo único, rearranjada pela campanha; final em ida e volta.
   - **Carioca**: Taça Guanabara (todos contra todos), os quatro primeiros vão à semifinal
     em ida e volta, e final em ida e volta. Mineiro, Gaúcho e os estaduais com 6 clubes ou
     mais seguem o mesmo desenho; com 5 clubes a semifinal é jogo único; com 4, turno e
     returno e final direto.
   - **Copa do Nordeste**: dois grupos cruzados; quartas 1º x 4º e 2º x 3º do grupo.
   - Jogo único é na casa de quem fez a melhor campanha; na ida e volta, a volta é na casa
     dela. Empate no jogo (ou no agregado) vai para os pênaltis — sem gol fora.
   - O estadual mais longo (o Paulistão) dita a duração da fase: quem cai antes descansa
     até o Brasileirão começar.

   Cada estado com 4 clubes ou mais tem
   campeonato próprio (Paulista, Carioca, Gaúcho, Mineiro, Catarinense, Paranaense,
   Goiano, Pernambucano, Cearense); o resto se junta por região na **Copa Verde** e na
   **Copa do Nordeste**. Campeão leva título na galeria e premiação. A janela fica aberta
   durante o estadual inteiro, e a tela Classificação lista os estaduais junto com as
   quatro séries.
3. **Brasileirão** — as 38 rodadas da sua série, com as copas no meio.

**Uma semana é uma rodada.** O calendário tem 38 semanas e 38 rodadas, então "1 rodada",
"1 mês" e "3 meses" são a mesma unidade em tamanhos diferentes. O botão **Avançar em...**
abre um painel com o pulo que você quiser: 1 rodada, 1 mês (4), 3 meses (12), até a
próxima janela, até o fim do turno, ou a temporada toda — e, no estadual, até o fim dele.
A simulação roda na frente dos seus olhos com barra de progresso e o placar de cada
rodada aparecendo, e você pode parar no meio. Fim de estadual e fim de temporada param
sempre; além disso você escolhe parar se alguém do time titular se machucar, se a janela
abrir, se chegar proposta por um jogador seu, ou se o time ficar sem condição de entrar
em campo.

**Listas de jogadores: ordenar e marcar.** Em qualquer lista (Elenco, Base, Treino,
Mercado, tabelas), clique no nome da coluna para ordenar por ela: número do maior para o
menor (Ovr, idade, salário, valor, contrato), texto de A a Z e posição na ordem do campo
(GOL → ATA). O segundo clique inverte e o terceiro volta à ordem original; a seta ▼/▲
mostra qual coluna está valendo, e a escolha fica guardada para a próxima visita. Nas
listas com caixa de marcar, a caixa do cabeçalho marca ou desmarca todos. No Elenco, o
botão **Contrato acabando** marca de uma vez quem está no último ano (ou já venceu) — dá
para mandar direto para Renovar ou Pôr à venda.

**Mercado.** Quatro abas em botões visíveis: **Comprar**, **Empréstimos**, **Agentes
livres** e **Vender**. Dá para fazer proposta por qualquer jogador, esteja ele na
vitrine ou não. O `*` marca quem o clube quer vender, o `!` quem ele não quer (esse sai
por 55% a mais) e a coluna `EMP` marca quem também sai por empréstimo.

**O mercado vem atrás do que é seu.** Antes só chegava proposta por quem estava na
vitrine — quem não listasse ninguém nunca recebia nada. Agora há duas fontes: a vitrine e
a **sondagem espontânea**, em que um clube aparece atrás de um jogador que não está à
venda. O que chama sondagem é o que chamaria na vida real: render acima da média do
elenco, ser promessa jovem, estar em fim de contrato (pechincha), aparecer em campo com
gol e assistência. E quem vem atrás do seu zagueiro é o clube que está mal na zaga — o
interessado é sorteado por necessidade, não a esmo.

Junto com isso, o teto que um clube paga foi corrigido: ele vai de 80% a 132% do valor de
mercado conforme a necessidade, e o caixa acrescenta até 8%. Antes parava em 98% e ficava
*sempre* abaixo do pedido do dono, que começa em 115%: as duas pontas nunca se cruzavam e
por isso o mercado parecia morto. Quem precisa de verdade paga acima do valor de mercado.
O que impede o giro continua sendo a mesma trava: não dá para revender com lucro quem
acabou de chegar.

**Vender e contrapropor.** Na aba **Vender** cada proposta mostra o valor de mercado do
jogador, quanto o clube ofereceu e quanto isso cobre do valor (`% valor`). Marque **uma**
proposta e aparece a contraproposta: você diz quanto quer (com atalhos de +10%, +20%, valor
de mercado e o seu pedido). O comprador compara com o quanto ele acha que o jogador vale
para *ele* e com a verba dele: se couber, fecha na hora pelo seu valor; se passar um
pouco, ele sobe a oferta até um meio-termo; se você pedir muito acima, ele retira a
proposta. São duas contrapropostas por oferta por semana. No topo da aba ficam os
**contratos acabando** (último ano ou já vencido), com o que cada um pede para renovar e o
botão **Renovar**, que abre as mesas uma depois da outra. O Painel mostra o mesmo aviso.

**Verba para contratar.** O caixa não é todo seu para gastar: **3 meses de folha e
custos** ficam reservados, sem contar receita nenhuma, e o salário de quem chega entra na
reserva antes de o passe ser pago. O que sobra é a **verba**, e compra ou taxa de
empréstimo acima dela é recusada. Assim a folha está sempre paga. A verba aparece no topo,
no Mercado e na mesa de negociação; em **Finanças** está o mês inteiro (TV, bilheteria
estimada, folha, estrutura, saldo) e de onde sai a verba. A IA segue a mesma regra.

**Negociar sempre, entrar e sair só na janela.** Você pode acertar compra, venda,
empréstimo ou cessão a qualquer momento do ano. Com a janela fechada o acordo fica de pé e
o jogador troca de clube **sozinho, na semana em que a janela abrir** — a mesa de
negociação avisa quantas semanas faltam, e a aba Vender lista os acertos pendentes
com um botão para cancelar. Na abertura tudo é revalidado: se o caixa mudou, se o elenco
encheu ou se o jogador foi para outro clube antes, o acerto cai e a notícia explica por
quê.

**Limite de elenco: 32 inscritos.** A regra agora vale para *todas* as portas de entrada —
compra, agente livre, empréstimo e promoção da base. Antes só a promoção respeitava, então
dava para ter 32 jogadores, contratar mais um sem reclamação e ainda assim não poder subir
um garoto da própria academia. Quando o elenco está cheio, a mensagem diz o que fazer:
vender, emprestar ou rescindir para abrir vaga.

**A mesa de negociação** é uma tela só: passe, duração e salário ao mesmo tempo. Cada
valor tem campo, barra de arraste e atalhos (`- 10%`, `pedido`, `+ 5%`, `meu caixa`), e
embaixo de cada barra o jogo diz em tempo real como o outro lado está lendo a proposta —
verde *deve ser aceita*, amarelo *abaixo do pedido*, vermelho *ofensiva: encerra a
conversa*. Junto vêm o caixa que sobra depois do passe e a folha antes e depois do
salário. Os anos de contrato mexem no que o empresário pede: um ano custa mais, cinco
custa menos. Três tentativas por mesa.

Nos campos de dinheiro dá para escrever do jeito que se fala: `12 mi`, `12,5 mi`,
`800 mil`, `90k` ou `12000000` — todos chegam no mesmo número, e o campo formata sozinho.

**Empréstimos** nos dois sentidos. Para trazer alguém: aba **Empréstimos** (quem está
oferecido) ou o botão **Pedir emprestado** na aba Comprar, que vale para qualquer
jogador. Você negocia a fatia do salário que assume — o jogo mostra na hora quanto sai do
seu bolso e quanto fica com o dono — e pode travar uma **opção de compra** para o fim do
empréstimo, respeitando o piso do dono (85% do pedido pelo passe; antes dava para travar
o passe por qualquer trocado). Depois se exerce pelo botão **Comprar em definitivo**, no
Elenco.

Para ceder: marque os jogadores no Elenco e use **Ceder empréstimo**. Todas as propostas
de todos os marcados vêm numa tabela só, uma linha por par jogador/clube, com o quanto
cada clube assume e o quanto sobra para você — marque quantas quiser e aceite de uma vez.
Quem você cedeu aparece numa segunda tabela no Elenco, com **Chamar de volta**; antes ele
simplesmente desaparecia da tela.

**Vender vários de uma vez.** A tabela do Elenco aceita seleção múltipla (Ctrl+clique
marca vários, Shift+clique marca a faixa) e todas as ações valem para o lote: pôr à
venda, tirar da vitrine, ceder, renovar, rescindir, comprar em definitivo. Em **Pôr a
venda** a régua de percentual precifica todos de uma vez pelo valor de mercado de cada
um — 90% para saída rápida, 130% com lucro, 200% só por muito — ou você fixa um preço
igual para os marcados. O rodapé soma o pedido e a folha que sairia.

**Propostas recebidas** são sorteadas uma vez por semana e ficam guardadas no save: não
adianta fechar e reabrir a tela até sair uma oferta boa. Dá para aceitar ou recusar
várias de uma vez, com o caixa antes e depois na tela. Ninguém paga acima do que enxerga
no jogador, então pedir muito acima do valor de mercado simplesmente não atrai comprador.

**Renovação.** O pedido do empresário agora é estável dentro da janela de quatro semanas
e sai do motor, levando em conta posto no time, idade, potencial, moral e o tamanho do
seu clube — fechar e reabrir a tela não muda mais o número. O Elenco mostra quantos estão
no último ano, e a coluna Contrato marca com `!` quem sai de graça na virada se não
renovar.

**Evolução.** Potencial é oculto: você vê a leitura do olheiro ("65-69", "teto ~80"), que
erra mais quanto pior for o seu CT e mais novo o jogador. Overall muda de mês em mês, não
só na virada do ano. Minutagem é o que manda — o mesmo garoto de potencial 92 termina
oito temporadas com 89 jogando, 82 rodando e 73 encostado. Por isso ceder um jovem por
empréstimo vale a pena.

**Teto dinâmico.** O teto é uma *previsão*, não uma sentença, e a previsão se corrige com
o que aconteceu em campo. Quem rende acima do que o teto dizia ganha teto novo; quem
nunca chega perto dele tem a previsão cortada. Isso acontece em duas escalas: mês a mês,
quem bate no teto jogando muito estoura a previsão em vez de congelar; e na virada do
ano, a temporada inteira é avaliada — jogos, gols, assistências contra o esperado da
posição, e em que divisão foi. Antes, um jogador de alto nível sorteado com teto baixo
travava para sempre no dia em que o overall encostava no teto, ainda que fosse titular
absoluto. A ficha do jogador conta quando o teto foi revisado, e o resumo da temporada
lista todas as revisões do elenco.

Dois freios evitam que o mundo inteiro caminhe para 99: o **palco** limita a previsão
(arrebentar a Série D prova que ele dá conta da Série D — para o teto passar disso, tem
que render num palco maior, e a reputação do clube conta), e cada degrau lá em cima custa
mais que o anterior. O que ele **já é** nunca fica abaixo do limite: quem chegou a 76 na
Série D não tem o teto travado em 74 pela sigla da competição.

**Base.** A academia agora é um elenco de verdade, na tela **Base**: garotos de 15 a 19
anos que treinam, evoluem e aparecem com nome, overall e leitura do olheiro. Eles não
jogam e não entram no mercado enquanto não subirem — custam uma bolsa (22% do salário
profissional, que aparece na folha) e, aos 20 anos, sobem ao profissional ou são
liberados. Antes disso, subir é decisão sua, a qualquer momento, pelo botão **Subir ao
profissional**; a coluna Situação diz quem já tem nível para isso.

O nível da academia (Infraestrutura) manda em três coisas: quantas vagas ela tem (nível 1
sustenta 8 garotos, nível 10 sustenta 26), quantos nascem por temporada, e a loteria do
talento — nível 1 dá uma joia a cada 43 crias; nível 10, uma a cada 12. Academia com menos
da metade ocupada puxa uma safra maior no ano seguinte.

**Treino.** A tela **Treino** tem duas alavancas. A primeira é o **regime da semana**, e
todo regime tem preço, escrito no próprio cartão:

| Regime | O que faz |
|---|---|
| Equilibrado | ritmo normal, sem bônus e sem preço |
| Intensivo | evolução +35%, mas físico −7 por semana e lesão +45% |
| Leve | físico +7 e lesão −35%, com evolução −25% |
| Foco na base | +60% para quem tem até 21 anos; quem passou dos 26 estagna |
| Foco técnico | evolução +18% com físico um pouco abaixo |
| Foco físico | físico +11 e lesão −28%, e segura o declínio dos veteranos |

A segunda é o **trabalho individual**: quem está na lista evolui 50% mais rápido e segura
melhor o declínio. O CT limita quantos cabem (nível 1 sustenta 2 nomes, nível 10 sustenta
7) e cada um custa por semana, na conta da estrutura. Garoto de base pode entrar na lista
— e para ele o treino é a única fonte de evolução, já que não joga. A coluna **EVOLUI** da
tabela mostra, em overall por mês, o efeito do regime e do trabalho individual somados.

**Resultados na dashboard.** O Painel ganhou uma faixa de **última rodada** logo abaixo do
veredito de prontidão: o placar de cada jogo da semana em tamanho de placar, colorido por
vitória, empate ou derrota, com a competição e o mando. Ao lado, os **últimos 5**
resultados como chips V/E/D — passe o mouse em um deles e o rodapé conta qual jogo foi. E
o bloco de baixo virou **como foi a rodada**: os gols com minuto e assistência, as lesões
e os vermelhos, seguidos das notícias do clube. Antes o resultado entrava diluído em uma
linha de texto junto com notícia de mercado, e dava para terminar a semana sem saber se o
time ganhou.

**Virada de temporada.** Acabou o jeito silencioso de virar o ano. Quando a 38ª rodada
termina, abre o **resumo da temporada**: onde terminou e se cumpriu a meta, títulos seus e
de todo mundo, campanha completa, artilheiro e garçom do clube, o dinheiro do ano (caixa
no começo e no fim, receita, bilheteria, premiação, folha), cada venda e cada compra com
valor, quem mais cresceu de overall, os tetos revisados, a safra da base, quem se
aposentou, quem volta de empréstimo e — em vermelho — quem sai de graça se você não
renovar. Se você for demitido, o resumo vem **antes** da oferta de clube novo: ninguém
entende a demissão sem ver a temporada que a causou.

Depois dele o jogo entra em **pré-temporada**, e ela é inconfundível: o topo anuncia
`PRE-TEMPORADA`, o botão de avançar fica verde e passa a dizer **Iniciar temporada X**, e
o Painel mostra o que falta resolver antes da bola rolar — contratos vencidos, garotos da
base prontos para subir, elenco curto. Começar o ano virou decisão: se houver pendência, o
jogo lista e pergunta antes. O resumo fica guardado e pode ser reaberto pelo botão **Ver
resumo da temporada** (no modo linha, pela opção Resumo da temporada).

## Acessibilidade

A interface passou por revisão de Design Director, UX Designer e uma rodada de Três
Amigos. O que mudou:

**Contraste medido, não escolhido a olho.** A função `botao()` agora escolhe a cor do
texto pelo brilho do fundo, em vez de usar uma cor fixa. Antes o botão azul primário dava
3,79:1, abaixo do mínimo WCAG AA (4,5:1), e o botão verde "Começar o ano" dava **1,74:1** —
texto praticamente invisível. Hoje todo botão do jogo passa AA, e qualquer botão novo já
nasce legível sem ninguém precisar lembrar. Textos clicáveis deixaram de ser azuis
(3,74:1) e passaram a roxo (6,28:1).

**O alerta não depende só de cor.** A régua do topo dobrou de espessura e ganhou palavra:
`ATENÇÃO` e `TIME QUEBRADO` aparecem escritos ao lado, para quem não distingue as cores.

**Botão Ajuda no modo Visual.** A saudação, o objetivo e a lista de comandos só existiam no
console do Modo linha — invisíveis para quem abre o jogo normalmente. Agora há um botão
**Ajuda** fixo no topo, com três abas: o que cada uma das 12 telas faz, um glossário dos
termos do jogo (OVR, Teto, J/G, `*`, `!`, EMP, Nota, Janela) e os comandos do modo linha.

**Carreira nova se apresenta.** Ao começar do zero, uma tela de boas-vindas diz quem você
é, o que a diretoria espera e os três primeiros passos — e lembra que nada acontece até
você avançar a semana. Na escolha de clube, a coluna REP passou a ser explicada, há um
clube sugerido já marcado para quem nunca jogou, e o botão "Assumir" fica desabilitado
enquanto não há seleção, dizendo o que falta.

**Fim dos becos sem saída.** Duplo-clique num jogador do Mercado abre a ficha com os botões
**Negociar compra** e **Pedir emprestado** dentro dela. O **Resumo do ano** virou botão
permanente no topo, em vez de sumir quando o Estadual começa. O botão de treino individual
diz o que o clique vai fazer (adicionar ou remover), não os dois caminhos.

**Aviso de má fase.** Três derrotas seguidas passam a gerar uma faixa no Painel com atalho
direto para o plano de jogo — o diagnóstico antigo só olhava lesão e suspensão, então um
time inteiro e saudável perdendo todo domingo aparecia como "TIME PRONTO".

**Texto que carrega regra saiu da menor fonte.** As legendas que explicam `*`, `!` e `EMP`,
a regra da base e a do treino individual subiram de 9pt para o corpo normal. E todo aviso
de "você não marcou nada" usa o mesmo texto, ensinando as três formas de marcar.

## A interface, refeita

A tela estava poluída e parte do conteúdo não cabia. Medi antes de mexer, e os problemas
eram objetivos:

| Tela | Antes | Agora |
|---|---|---|
| Escalação | exigia 1172px, cabiam 1010 — **cortava 162px** | 929px, com folga |
| Elenco | 12 colunas, subtítulo de 127 caracteres | 8 colunas, 55 caracteres |
| Base | 10 colunas, subtítulo de 152 caracteres | 7 colunas |
| Treino | 9 colunas, subtítulo de 144 caracteres | 7 colunas |
| Barra do topo | 6 botões — Salvar e o caixa ficavam fora da tela | 2 botões, tudo visível |

**Métricas viraram chips.** Onde havia uma frase de até 162 caracteres separada por barras
verticais, agora há um título, uma linha curta de contexto e os números em blocos
separados — cada um com o valor em cima e o nome embaixo. Número é número, texto é texto.

**Tabelas mostram o essencial.** O Elenco tinha 12 colunas e cortava as últimas; agora tem
8, e o resto (teto, moral, J/G, preço na vitrine) está na ficha, a um duplo-clique. Uma
função central corta a cauda de colunas que não caberia na janela mínima, em vez de deixar
a tabela furar a tela.

**O topo carrega só a semana.** Salvar, Ajuda, Resumo do ano e Modo linha desceram para o
pé do menu lateral, que vivia com espaço vazio. No topo ficaram o clube, o caixa e o botão
de avançar.

**Menos repetição no Painel.** A tira "11/11 EM CAMPO | GOLEIRO OK | SEM IMPROVISO" dizia
exatamente o que a faixa de prontidão já anuncia logo acima, com mais destaque — saiu. O
placar também aparecia duas vezes (na faixa e no cartão de baixo); agora a faixa mostra o
resultado e o cartão mostra os lances e as notícias. Com isso o XI cabe inteiro: antes
mostrava 10 dos 11 titulares.

**Bug de exibição corrigido:** Físico e Moral apareciam como `53.9903` e `65.7588`. A
fadiga por período e o puxão de moral guardavam float no jogador, e a tabela imprimia o
número cru. Agora são inteiros na origem — 2020 dos 3525 jogadores do mundo estavam com
valor quebrado.

## Gerar o executável (opcional)

Dois cliques no `build-windows.bat`. Sai o `dist\BRASFUT.exe`, que roda em qualquer
Windows sem Python. Refaça sempre que baixar um `brasfut.py` novo. Na primeira execução o
SmartScreen avisa que o programa é desconhecido: "Mais informações", "Executar assim
mesmo".

## Trocar os elencos

Os 36 clubes das Séries A e B já vêm com 1.079 jogadores reais embutidos. Para atualizar,
ponha um `elencos.json` ao lado do jogo — ele tem prioridade e é lido ao começar carreira
nova:

```json
{
  "Goias": [
    {"nome": "Tadeu", "pos": "GOL", "idade": 32, "ovr": 74},
    {"nome": "Paulo Baya", "pos": "MEI", "idade": 26, "ovr": 72, "pot": 78}
  ]
}
```

Chave = nome do clube como está no `brasfut.py`, sem acento. `pos` aceita GOL, ZAG, LAT,
VOL, MEI e ATA. `idade`, `ovr` e `pot` são opcionais, e cada clube tem o tamanho de
elenco que você colocar.
