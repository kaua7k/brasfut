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

**Escalação.** A troca é em dois cliques explícitos e só então o botão
*Trocar*: titular + reserva (um sai, o outro entra) ou dois titulares
(`POST /api/escalacao/inverter`, trocam de lugar). Marca-se pelo disco do
campo ou pela linha da lista (titulares em roxo, `--titular`). Na mesma vaga
a troca é de lado no campo (a ordem do XI decide quem fica em cima); em vagas
diferentes depende do motor aceitar vaga fixada — enquanto
`eng.vagas_manuais` não existir, a API recusa com o motivo e a tela avisa
antes (`troca_entre_vagas`). A rota já grava `c["vagas_manuais"]` (lista de
`[pid, vaga]` do XI inteiro) para quando o motor ler. Trocar alguém desliga a
alavanca automática, e o recado diz isso. O disco mostra o overall. Leiaute:
campo + lista primeiro, uma barra só com alavanca, formação, *Editar
formação*, *Tática* (mentalidade e plano de jogo, recolhidos) e *Montar
melhor time*. O XI
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

**Europa e elencos reais de fora.** `ferramentas/importar_elencos.py` baixa
da football-data.org (chave em `FOOTBALL_DATA_KEY`, no `.env`, fora do git)
as 5 grandes ligas, a Libertadores e o Santos, e gera `dados_mundo.py`
(embutido em base64, como os elencos brasileiros; quem joga não precisa de
internet). A API não dá nota: o ovr sai da reputação do clube (classificação
da temporada anterior), da idade e de uma variação fixa por nome; craques têm
nota estimada em `ferramentas/notas_manuais.json`. Quem já estava no jogo
mantém a nota. Cache das respostas em `ferramentas/cache/` (fora do git);
`--baixar` busca de novo.

No motor (bloco O RESTO DO MUNDO): **as ligas de fora são jogáveis**. O
clube tem `divisao` igual ao código da liga (`ENG`, `ESP`, `GER`, `ITA`,
`FRA`, `POR`, `NED`, `USA`, `SAU`) e a liga mora em `G["ligas"]` ao lado das
séries — `ligas_ext(G)` devolve só as de fora, e `nome_da_liga(G, div)` o
nome para qualquer texto (nunca escreva "Serie %s" direto). Com isso o clube
entra na economia, no mercado (compra e vende com o Brasil), na base e nas
propostas de emprego, e o técnico pode escolhê-lo na carreira nova. Cada liga
tem `PERFIL_LIGA_EXT`: TV (calibrada para saldo semanal pouco acima de zero,
como nas séries), premiação, caixa inicial, peso no valor e teto de evolução
— injetados em `TV`/`PREMIO`/`PESO_DIVISAO`/`TETO_CREDIVEL` por
`perfil_liga`. Só é brasileiro quem `brasileiro(c)`: estadual e Copa do
Brasil ficam para as séries. Jogos das ligas de fora usam comp `"liga"` (a
suspensão bate com o diagnóstico) e o expoente europeu vem da divisão do
mandante. Sem acesso/rebaixamento lá fora: objetivo vira "fugir das últimas
posições" e a tabela não pinta zona de queda. Na virada só as séries são
remontadas; as de fora passam por `fechar_ligas_ext` (campeão e
`class_ext_anterior`). Save antigo com `G["ligas_ext"]` tem as ligas movidas
para `G["ligas"]` e os clubes viram divisão em `migrar`. Mundo novo recebe tudo (`aplicar_mundo(sul=True)`);
save antigo recebe só as ligas europeias em `migrar`, sem trocar elenco
sul-americano nem brasileiro. Competições e Classificação listam as ligas
como `ext:ENG`, `ext:ESP`... A temporada simulada ficou ~40% mais lenta e o
save de mundo novo tem ~5 MB. MLS e liga saudita vêm da API-Football
(`API_FOOTBALL_KEY`, `LIGAS_AF` no importador): o plano grátis só abre
2022–2024, então clubes e classificação são de 2024 e o elenco
(`/players/squads`) é o atual. São ~51 pedidos (limite de 100 por dia). A MLS
tem 29 clubes e joga só o turno (`nova_liga_ext`). `notas_manuais.json`
aceita `{"ovr": 80, "pos": "ATA"}` para corrigir posição genérica.

**Copas europeias e clubes novos.** Entraram Liga Portugal e Eredivisie (7
ligas), os clubes da Champions fora delas (`c["europeu"]`, sem liga, elenco
real por `/teams/{id}`) e os 15 sul-americanos da Libertadores real que o jogo
não tinha (`sul_novos`, reputação por país; entram na disputa das vagas das
copas sul-americanas pela reputação). Champions e Europa League
(`montar_copas_europeias`) usam o formato de 2024: fase de liga de 36 em
`SEMANAS_FASE_LIGA` (um "grupo" único, mesma máquina da fase de grupos, com
`cp["formato"] = "suico"`; o sorteio é simplificado: 8 rodadas do rodízio,
sem potes), 1º–8º esperando nas oitavas, 9º–24º no playoff, e o mata-mata da
Sul-Americana em `SEMANAS_EURO`. Primeiro ano: os 36 reais da Champions.
Depois: `VAGAS_CHAMPIONS` por liga pela classificação anterior
(`class_ext_anterior`), o campeão, os europeus sem liga e o resto completado
por posição intercalada entre as ligas; a Europa League pega os 36 seguintes.
Jogos de ligas e copas europeias usam `EXP_FORCA_EUROPA` (3.4): com o 2.20
brasileiro o City fazia 65 pontos e o LASK ganhava a Champions. Temporada
simulada ~15 s.

**Inflação de notas (corrigida).** O mundo caminhava para 99: em 8
temporadas simuladas o número de jogadores 90+ ia de 6 para 453. Quatro
causas: `teto_maximo` devolvia `max(limite, ovr + 2)` (quem batia no teto
ganhava 2 de folga todo mês — uma catraca com `estourar_teto`), a loteria de
`sortear_potencial` dava joia 97–99 a cada ~17 garotos de academia boa, a base
crescia como quem joga tudo (`PISO_BASE`, era 1.0) e o garoto de base ganhava
revisão de teto sem jogar. Hoje: revisão/estouro só até `TETO_REVISAO` (91),
joia rara com teto 96, base a 0.72 e sem revisão. Save antigo passa uma vez por
`corrigir_inflacao` (percentil a percentil contra `CURVA_SAUDAVEL`, só para
baixo). `test_balanco.py` segura as regras. Livres: `contratar_livres_ia`
(semanal) leva os melhores para quem os teria de titular e paga o salário — a
IA antiga pegava livre ao acaso e `limpar_livres` guardava justamente os
melhores, que ninguém contratava.

**Partida com o XI escalado.** `simular` usava `montar_escalacao` para os dois
lados: o time manual do técnico nunca entrava em campo. Agora usa
`escalacao_valida` (a máquina segue no automático), e `atribuir_vagas` aceita
as vagas fixadas pela troca entre titulares (`vagas_manuais`).

**Base: peneira, faixa que estreita, revelações.** Aba *Peneira* na Base: região
(`REGIOES_PENEIRA`: talento, posições típicas, custo semanal) e posição
opcional; a cada `PENEIRA_A_CADA` semanas chegam candidatos que esperam
`CANDIDATO_VALE` semanas (`POST /api/base/peneira`, `/api/base/candidato`). Só o
clube do jogador usa. `j["obs"]` conta os meses que o clube observa o jogador
e aperta a margem de `scout()` (EA FC / Football Manager). `c["revelados"]`
guarda quem subiu (aba *Revelações*). Pesquisa de referências (FM, EA FC,
Brasfoot, Hattrick, Top Eleven) e próximos passos possíveis: olheiro de base
contratável, dia da safra como evento, empréstimo de desenvolvimento, Copinha
sub-20, assédio a garotos, mentor.

**Casca.** O endereço guarda a tela no hash (`/#elenco`): F5 não volta ao
Painel, e agora o Voltar/Avançar do navegador também troca de tela.
Marcações nas grades usam `alternarMarca` com setter funcional (dois cliques
rápidos não se apagam) e zeram quando a tela volta do servidor, para nenhuma
ação em lote apontar para quem já saiu. `[hidden]` ganhou `display:none
!important` e `.tela > *` não encolhe — era isso que cortava a lista do Elenco
sem dar scroll.

## Rodada de melhorias (Onda 1)

Decisões em `docs/three-amigos/2026-09-24-rodada-de-melhorias.md`.

**Regras que o jogo desobedecia.**
- **Agente livre assina na hora**, com a janela aberta ou fechada, para quem
  fechar primeiro — técnico ou IA (`assina_na_hora`). Antes o acerto do técnico
  ficava agendado e a IA levava o jogador na semana seguinte. Quem tem acerto
  agendado (`presos_em_acerto`) não é contratado por ninguém; acerto com livre
  de save antigo se cumpre na próxima semana (`executar_agendadas`).
- **Guard de posse na API** (`_exigir_posse` em `api/rotas.py`): rescindir,
  tirar da vitrine, subir e liberar da base, chamar de volta e treino
  individual só aceitam jogador do meu clube; um id alheio devolve 400 com o
  nome e nada muda. Dava para rescindir jogador de rival descontando a multa
  do caixa dele.
- **Troca de clube limpa o clube antigo** (`largar_clube`, chamada por
  `assumir_clube`): vagas fixadas, treino individual, peneira e candidatos.
- **Prazo em semanas absolutas** (`G["semana_abs"]`, `semana_absoluta`):
  `G["semana"]` fica em 0 o estadual inteiro, e a proposta de 6 semanas feita
  na virada durava ~20. Proposta de emprego e candidato da peneira guardam
  `vence`; `migrar_prazos` converte save antigo.
- **Barra de forças** compara o duelo que a partida joga: meu ataque x defesa
  dele e minha defesa x ataque dele, os dois com o XI da competição do jogo.
- **Textos**: nome da liga em vez de "Serie ENG" (`liga_do_resumo`); a Série D
  não rebaixa (`tem_rebaixamento`, e a diretoria deixou de somar risco de
  queda na D); `scout` devolve "~75" (a tela já escreve "teto"); "nas
  quartas"; empréstimo de livre diz o motivo; corpo que não é objeto JSON,
  `alvo`, `contagem` e id de ficha malformados viram 400.

`testes/test_regras.py` tem um teste por critério de aceite.

**Desempenho sem mudar o jogo.** `atribuir_vagas` ganhou um memo exato
(`_MEMO_VAGAS`): a chave leva formação, vagas fixadas e, de cada titular na
ordem do XI, posição, overall, condição, forma e moral — tudo o que
`rendimento()` lê. Acerta quando o mesmo XI é medido de novo no mesmo estado
(posse, forças do primeiro tempo, diagnóstico). `montar_escalacao` e
`atribuir_vagas` calculam a linha de notas uma vez por posição, não uma vez
por vaga repetida. Um memo de `forcas_de` foi testado e saiu: a fadiga muda a
condição a cada período e ele quase nunca acertava. Ficou de fora de
propósito: tirar a semana do `esc_stamp` (muda a regra do rodízio) e gravar o
save em thread (mais lento e com risco de corromper).

`testes/desempenho.py` é o gate: 3 seeds x 20 semanas pelo mesmo caminho da
tela, sha256 do mundo inteiro, do log e dos jogos a cada semana (`--gravar`
na versão de referência, `--comparar` depois). Rode com `PYTHONHASHSEED=0` e
intercale referência e versão nova: o tempo entre execuções varia ~20% na
mesma máquina. Medido nesta leva: motor −25% (39,3 s → 29,6 s nas 60
semanas), pedido inteiro −19%, saída idêntica.

**Interface: layout, acessibilidade e linguagem.**
- *Topo*: os chips somem por classe (`chip-elenco` em 1440px, `chip-folha`
  em 1320px), nunca o Caixa nem a Verba. O `nth-of-type` contava escudo e
  título e escondia justamente o CAIXA em 1320px. O subtítulo (com a semana)
  quebra em duas linhas antes de cortar.
- *Uma rolagem por página*: o Painel tem altura natural (`.corpo` rola, as
  colunas não); acabou o cartão rolando por dentro e as Notícias vazando por
  cima do Pelo mundo. `.tela` perdeu o padding de baixo (o sticky conta a
  partir dele e a barra de ações presa ficava 24px acima do rodapé, com linhas
  passando por baixo); o respiro veio para o `::after`.
- *Grade*: largura mínima somada das colunas; abaixo dela a grade rola de lado
  dentro dela. Linha que abre ficha é focável e abre com Enter, e o texto diz
  "duplo clique (ou Enter)", que é o gesto de verdade.
- *Finanças*: `.linha-valor` em grade de duas colunas; a linha do saldo usa
  `total`, não `destaque` (que é o cartão do Painel e entortava a linha).
- *Acessibilidade*: zona da tabela com forma e texto (`componentes/Zona.tsx`,
  `zona_texto` vindo de `dto.rotulo_zona`) e legenda; legenda das cores de
  nome (`LegendaCores`); menu só de ícones com `aria-label`/`title`; todo
  botão desabilitado diz o motivo (`porque()` em `web/src/motivo.ts`); borda
  de controle `--borda-controle` (3,3:1); `prefers-reduced-motion` vale para
  tudo, não só para o disco da Escalação.
- *Linguagem*: menu "Classificacao" igual ao título; "Pos" e "Pts", nunca
  "P"; `eng.din` em pt-BR ("R$ 37,6 mi", "R$ 764 mil", "R$ 3.500" abaixo de
  cem mil) com espelho em `web/src/formato.ts`; `eng.plural`/`plural()` no
  lugar de todo "(s)"; o Mercado não repete caixa, verba e folha do topo e o
  "time pronto" não repete ataque e defesa da barra; `eng.nome_clube` põe a
  liga ao lado de nome repetido ("Athletic (La Liga)").
- `testes/test_textos.py` é o lint: zero "(s)" e zero "mi" com ponto nas
  fontes e nas telas, zero "Serie ENG", menu e título com o mesmo nome.

## Onda 2

Escopo, ordem e decisões: `docs/three-amigos/2026-09-25-onda-2-decisoes.md`.

**Tokens de CSS.** Todo valor visual mora no `:root` de
`web/src/estilo/base.css`; fora dele o CSS e o TSX só usam `var(--...)`.
- *Três cores, três sentidos*: **azul** (`--acao`, fundo com texto branco,
  5,2:1; `--acao-linha`, texto/borda/traço, 7,2:1) é você e o que você faz:
  botão principal, aba e alavanca ativas, foco, link, caixa marcada, seu
  clube na tabela, barra de progresso. **Dourado** (`--conquista`) é marca e
  conquista: escudo, troféu, título, reputação, overall da ficha. **Âmbar**
  (`--atencao`) é só atenção. O antigo `--acento` fazia os três papéis e
  saiu.
- *Fonte*: seis degraus (`--fs-mini` 11, `--fs-p` 12, `--fs-m` 13,
  `--fs-base` 14, `--fs-g` 17, `--fs-gg` 22). Eram 18 tamanhos; o menor
  rótulo subiu de 10 para 11px.
- *Inline*: `style={{}}` só para valor que vem do dado (posição no campo,
  largura de barra). O resto virou classe, e as utilitárias (`.mt-*`,
  `.mb-*`, `.txt-*`, `.painel.enxuto`...) ficam no fim do `base.css` para
  vencer a classe base de mesma especificidade.
- `testes/test_tokens.py` é o lint: zero hex, rgba ou `font-size` em px fora
  do `:root`, no máximo seis degraus de fonte, todo `var()` usado existe,
  nenhum `--acento`, nenhum inline fixo no TSX.

**Partida guardada.** `simular` devolve `notas` e `xi` com o id do jogador
como chave; o JSON vira essa chave em texto e, depois de carregar, o id não
achava mais ninguém (o melhor em campo sumia). Em memória a chave segue int:
`migrar` chama `_normalizar_partida` em `ultimos_meus`. Para guardar,
`eng.registro_partida` monta um registro só de listas e nomes (gols e
cartões com minuto, substituições, lesões, stats, `[lado, id, nome, vaga,
nota]` de quem entrou, melhor em campo) e `guardar_historico` mantém os
`HISTORICO_PARTIDAS` (10) últimos em `G["historico_meus"]`. `nota_soma` e o
novo `nota_j` somam a nota de cada jogo (`eng.media_nota`); save antigo
começa a média do zero, sem inventar nota. Nada disso usa o `rng`: o harness
com `--ignorar historico_meus,nota_soma,nota_j` dá saída idêntica.

**Resumo da partida.** `dto.partida` põe o registro no formato do cartão
(mandante primeiro, `eu` diz o lado). O Painel recebe as 10 em
`resultados.partidas` e `componentes/Partida.tsx` desenha: `ResumoPartida`
(gols e cartões com minuto, posse, chutes, melhor em campo; as bolinhas V/E/D
viram botões que trocam o jogo mostrado) e `DetalhePartida` (notas por time,
estatísticas, substituições, lesões). `/api/avancar` devolve `partidas` da
semana: o fim do Simular mostra o resumo sem outro pedido. Save sem histórico
cai na faixa antiga (`FaixaResultados`).

**Instrução condicional.** No lugar do intervalo interativo (Onda 3): "se
perdendo a partir dos 71', Ofensivo". `simular` confere a regra nas paradas
que já tinha (46' e 71') e troca só a mentalidade (`c["tatica"]`), que já pesa
em ataque, defesa, cansaço e cartão. Vale enquanto o placar pedir; o laço dos
períodos roda num `try/finally` que devolve a mentalidade original no fim,
então nada vaza para o save. As trocas saem em `r["instrucoes"]` (lista à
parte: `eventos` não ganhou tipo novo, e nenhum leitor antigo quebra) e
aparecem no cartão da partida. A máquina tem regra fixa aos 71': perdendo
sobe um degrau de `ESCADA_TATICA`, vencendo desce um (decisão do usuário em
2026-09-25). Regras em `c["condicionais"]`, validadas por
`eng.condicionais_de`; rota `POST /api/escalacao/condicional`; bloco "Se o
jogo apertar" no painel de tática da Escalação. `testes/balanceamento.py` é
a suíte lenta que mede a distribuição antes e depois.

**Capturas.** `ferramentas/capturas.py` sobe uma cópia isolada do jogo
(motor, api, `web/dist` e cópia do save) na porta 8791, abre o save e
fotografa as 13 telas (`--avancar N` joga N semanas na cópia antes) em 1280x720, 1366x768, 1440x900, 1920x1080 e
2560x1440 com o Edge headless (`--timeout` porque a Escalação tem animação
infinita e segurava o Edge). `comparar <antes> <depois>` dá a porcentagem de
pixels diferentes por captura, lendo o PNG só com `zlib`. Rode `npm run
build` antes: a captura usa `web/dist`.

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
- **`test_europa.py`** ligas europeias no mundo novo, rodadas andando,
  telas `ext:` e save antigo ganhando a Europa sem jogador duplicado.
- **`test_escalacao.py`** trocas: titular por reserva, dois titulares da
  mesma vaga trocando de lado e a recusa (ou troca) entre vagas diferentes.
- **`test_balanco.py`** teto sem catraca, joia com teto, base sem revisão,
  correção de save inflado, IA contratando livre bom.
- **`test_base.py`** peneira do começo ao fim, faixa que estreita, revelações.
- **`test_textos.py`** lint de textos: plural, dinheiro, nome de liga, menu.
- **`test_regras.py`** livre com a janela fechada, posse na API, troca de
  clube, prazo absoluto, barra de forças e os textos corrigidos.
- **`test_continentais.py`** grupos da Libertadores e da Sul-Americana até o
  playoff e as oitavas, e save antigo ganhando os clubes que faltam.
- **`test_partida.py`** histórico das 10 últimas, notas depois de salvar e
  carregar, média do ano, cartão do Painel e resumo no retorno do avanço.
- **`test_condicional.py`** regra do meu clube, regra fixa da máquina,
  validação, mentalidade devolvida no fim do jogo e a rota.
- **`test_tokens.py`** lint visual: cor e fonte só por token, escala de
  seis degraus, sem `--acento`, sem inline fixo no TSX.

Nenhum teste grava no save real: `apoio.py` intercepta `eng.salvar` e falha na hora se alguém tentar (a comparação por hash dava alarme falso com o jogo aberto).
A interface (React) ainda é conferida à mão, com `ferramentas/capturas.py`
(ver *Onda 2*): `tirar` antes e depois da mudança, `comparar` para achar as
telas que mexeram, e olhar essas.

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
