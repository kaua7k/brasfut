# -*- coding: utf-8 -*-
"""URL -> funcao. Nenhuma regra de jogo mora aqui.

Toda rota que escreve no mundo pega o cadeado da sessao e salva antes de
responder: a interface web pode ser fechada no meio de qualquer acao, e um
jogo perdido por causa disso seria culpa da arquitetura, nao do usuario.
"""

import json
import traceback

from . import avanco, competicoes, config, dto, mercado
from .sessao import SESSAO, SemJogo
import brasfut as eng

ROTAS = {}


def rota(metodo, caminho):
    def registra(func):
        ROTAS[(metodo, caminho)] = func
        return func
    return registra


class ErroDeUso(Exception):
    """Pedido malformado: culpa do cliente, responde 400."""


# ------------------------------------------------------------------- leitura
@rota("GET", "/api/estado")
def estado(_corpo):
    """A primeira pergunta do cliente: da para jogar, e de onde comeco?"""
    base = {"versao": eng.VERSAO, "config": config.ler()}
    if SESSAO.G is None:
        if SESSAO.tem_save():
            return dict(base, jogo="tem_save", save=_sobre_o_save())
        return dict(base, jogo="sem_save")
    return dict(base, jogo="pronto", cabecalho=dto.cabecalho(SESSAO.exigir()),
                pendencia=SESSAO.pendencia)


def _sobre_o_save():
    """Quem esta no save, para o menu dizer o que 'Continuar' abre. Le o
    arquivo sem adotar o mundo: abrir continua sendo decisao do usuario."""
    try:
        G = eng.carregar()
    except Exception:
        return None
    c = G["clubes"].get(G.get("clube"))
    return {"tecnico": G.get("tecnico") or "Tecnico", "clube": c["nome"] if c else "",
            "temporada": G.get("temporada"), "semana": G.get("semana")}


@rota("GET", "/api/config")
def ver_config(_corpo):
    return {"config": config.ler(), "dificuldades": _dificuldades()}


@rota("POST", "/api/config")
def gravar_config(corpo):
    return {"config": config.gravar(corpo or {}), "dificuldades": _dificuldades()}


def _dificuldades():
    return [{"id": k, "nome": d["nome"], "desc": d["desc"]} for k, d in eng.DIFICULDADES.items()]


@rota("GET", "/api/painel")
def painel(_corpo):
    with SESSAO.cadeado:
        return {"painel": dto.painel(), "pendencia": SESSAO.pendencia}


# -------------------------------------------------------------------- inicio
@rota("POST", "/api/abrir")
def abrir(_corpo):
    """Continua o jogo salvo."""
    with SESSAO.cadeado:
        SESSAO.carregar()
        return {"jogo": "pronto", "cabecalho": dto.cabecalho(SESSAO.exigir()),
                "pendencia": SESSAO.pendencia}


@rota("POST", "/api/novo")
def novo(corpo):
    """Cria o mundo e devolve os clubes para escolher. Nada e salvo ainda.
    Leva o nome do tecnico e as opcoes da carreira (dificuldade, sem demissao,
    investidor), que valem pelo save inteiro."""
    with SESSAO.cadeado:
        G = SESSAO.mundo_novo(corpo.get("nome"), corpo.get("opcoes"))
        ordem = list(eng.DIVISOES_BR) + list(eng.ligas_ext(G))
        clubes = [{"id": cid, "nome": c["nome"], "divisao": c["divisao"],
                   "liga": eng.nome_da_liga(G, c["divisao"]), "reputacao": c["reputacao"]}
                  for cid, c in G["clubes"].items() if c["divisao"] in G["ligas"]]
        clubes.sort(key=lambda x: (ordem.index(x["divisao"]), -x["reputacao"]))
        return {"jogo": "escolher_clube", "clubes": clubes}


@rota("POST", "/api/clube")
def escolher_clube(corpo):
    if corpo.get("encerrar"):
        with SESSAO.cadeado:
            SESSAO.encerrar_carreira()
            SESSAO.salvar()
            return {"jogo": "pronto", "pendencia": SESSAO.pendencia,
                    "cabecalho": dto.cabecalho(SESSAO.exigir())}
    cid = corpo.get("id")
    if cid is None:
        raise ErroDeUso("falta o id do clube")
    with SESSAO.cadeado:
        try:
            SESSAO.escolher_clube(cid)
        except ValueError as e:
            raise ErroDeUso(str(e))
        SESSAO.salvar()
        return {"jogo": "pronto", "cabecalho": dto.cabecalho(SESSAO.exigir()),
                "pendencia": SESSAO.pendencia}


@rota("GET", "/api/resumo")
def ver_resumo(_corpo):
    """O resumo do ano: o ultimo que virou, ou a previa se a temporada acabou
    e a virada ainda espera o clique."""
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        if eng.temporada_encerrada(G):
            return {"resumo": dto.resumo(eng.apurar_temporada(G), previa=True)}
        r = G.get("ultimo_resumo")
        if not r:
            raise ErroDeUso("Nenhuma temporada encerrada ainda.")
        return {"resumo": dto.resumo(r)}


# --------------------------------------------------------------------- acoes
@rota("POST", "/api/avancar")
def avancar(corpo):
    """Joga a semana. O aviso de time quebrado e decidido na tela, nao aqui.

    Quando o diagnostico esta critico a primeira chamada nao avanca: devolve o
    aviso e espera um segundo pedido com confirmar=true. A regra de deixar o
    usuario ver o estrago antes vem da janela tkinter e se perde se a API
    simplesmente obedecer.
    """
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        # demissao ou fim de carreira travam o jogo: sem isto a semana andava
        # por baixo da janela de escolha e ela voltava a cada avanco
        if SESSAO.pendencia:
            raise ErroDeUso("Resolva a pendencia antes de seguir: %s." % SESSAO.pendencia["titulo"].lower())
        if G["fase"] == "entretemporada" and not corpo.get("confirmar"):
            aviso = _avisos_do_estadual(G)
            if aviso:
                return {"confirmar": aviso}
        d = SESSAO.diagnostico(recarregar=True)
        if (d and d["estado"] == "critico" and G["fase"] != "entretemporada"
                and not corpo.get("confirmar")):
            return {"confirmar": {
                "titulo": "Time quebrado",
                "texto": ("%s\n\nAvancar a semana agora entra em campo com esse time.\n"
                          "Ataque %.1f, defesa %.1f - com o problema ja descontado."
                          % (d["titulo"], d["ataque"], d["defesa"])),
                "destino": "escalacao"}}
        antes = avanco.foto(G)
        virada = eng.temporada_encerrada(G)
        fora = SESSAO.avancar()
        eng.salvar_auto(G)
        # a virada acabou de acontecer: o resumo vem junto, para a tela abrir
        # antes de qualquer outra coisa (inclusive da escolha de clube novo)
        if virada and G.get("ultimo_resumo"):
            fora["resumo"] = dto.resumo(G["ultimo_resumo"])
        # o relato e o motivo de parar servem o avanco em ritmos (jogo, mes,
        # janela, temporada): o navegador roda o laco semana a semana e para
        # quando o servidor disser por que
        fora["linhas"], fora["jogou"] = avanco.relato(G, antes)
        fora["parar"] = avanco.motivo_de_parar(G, antes, corpo.get("paradas"),
                                              fora["encerrada"], SESSAO.pendencia)
        fora["opcoes"] = avanco.opcoes(G)
        # no meio do laco o Painel inteiro a cada semana e desperdicio: so no fim
        if not corpo.get("leve"):
            fora["painel"] = dto.painel()
        fora["cabecalho"] = dto.cabecalho(G)
        fora["pendencia"] = SESSAO.pendencia
        return fora


def _avisos_do_estadual(G):
    """O que o tkinter perguntava antes de abrir o ano: comecar e decisao."""
    c = G["clubes"][G["clube"]]
    avisos = []
    vencidos = [G["jogadores"][p]["nome"] for p in c["elenco"]
                if G["jogadores"][p]["contrato"] <= 0 and not G["jogadores"][p].get("dono")]
    if vencidos:
        avisos.append("Saem de graca agora, por fim de contrato:\n  %s" % ", ".join(vencidos))
    if len(c["elenco"]) < 18:
        avisos.append("Elenco com %d jogadores: pouco para a temporada inteira." % len(c["elenco"]))
    prontos = [j["nome"] for j in eng.elenco_base(G, c) if eng.pronto_para_subir(G, c, j)]
    if prontos:
        avisos.append("Pronto(s) para subir da base: %s" % ", ".join(prontos))
    if not avisos:
        return None
    return {"titulo": "Comecar o estadual %d" % G["temporada"],
            "texto": "%s\n\nComecar assim mesmo?" % "\n\n".join(avisos),
            "destino": "elenco"}


@rota("GET", "/api/avanco/opcoes")
def opcoes_de_avanco(_corpo):
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        return {"opcoes": avanco.opcoes(G), "paradas": avanco.PARADAS_PADRAO,
                "cabecalho": dto.cabecalho(G)}


@rota("POST", "/api/escalacao/auto")
def escalacao_auto(corpo):
    if "ligada" not in corpo:
        raise ErroDeUso("falta o campo ligada")
    with SESSAO.cadeado:
        mudou = SESSAO.definir_auto(corpo["ligada"])
        if mudou:
            SESSAO.esquecer_desfazer()
            eng.salvar_auto(SESSAO.exigir())
        # a alavanca mora no Painel e na Escalacao: devolve a tela de quem pediu
        if corpo.get("tela") == "escalacao":
            return {"mudou": mudou, "tela": dto.escalacao()}
        return {"mudou": mudou, "painel": dto.painel()}


@rota("POST", "/api/salvar")
def salvar(_corpo):
    with SESSAO.cadeado:
        SESSAO.salvar()
        return {"ok": True}


# ---------------------------------------------------------------- outras telas
@rota("GET", "/api/elenco")
def ver_elenco(_corpo):
    with SESSAO.cadeado:
        return {"tela": dto.elenco()}


@rota("GET", "/api/base")
def ver_base(_corpo):
    with SESSAO.cadeado:
        return {"tela": dto.base()}


@rota("GET", "/api/tabela")
def ver_tabela(corpo):
    with SESSAO.cadeado:
        return {"tela": dto.tabela((corpo or {}).get("alvo"))}


@rota("POST", "/api/tabela")
def ver_tabela_alvo(corpo):
    with SESSAO.cadeado:
        return {"tela": dto.tabela(corpo.get("alvo"))}


@rota("GET", "/api/copas")
def ver_copas(_corpo):
    with SESSAO.cadeado:
        return {"tela": dto.copas()}


@rota("GET", "/api/competicoes")
def ver_competicoes(_corpo):
    with SESSAO.cadeado:
        return {"tela": competicoes.tela()}


@rota("POST", "/api/competicoes")
def ver_competicao(corpo):
    with SESSAO.cadeado:
        return {"tela": competicoes.tela(corpo.get("alvo"))}


@rota("GET", "/api/financas")
def ver_financas(_corpo):
    with SESSAO.cadeado:
        return {"tela": dto.financas()}


@rota("GET", "/api/infra")
def ver_infra(_corpo):
    with SESSAO.cadeado:
        return {"tela": dto.infra()}


@rota("GET", "/api/carreira")
def ver_carreira(_corpo):
    with SESSAO.cadeado:
        return {"tela": dto.carreira()}


@rota("POST", "/api/carreira/demitir")
def pedir_demissao(_corpo):
    """Sai do clube por vontade propria. Vira pendencia com os clubes que
    querem o treinador; o jogo nao anda ate ele escolher."""
    with SESSAO.cadeado:
        try:
            SESSAO.pedir_demissao()
        except ValueError as e:
            raise ErroDeUso(str(e))
        SESSAO.salvar()
        return {"pendencia": SESSAO.pendencia, "cabecalho": dto.cabecalho(SESSAO.exigir())}


@rota("POST", "/api/carreira/proposta")
def responder_proposta(corpo):
    """Aceita ou recusa um clube que quer o treinador."""
    cid = corpo.get("id")
    if not isinstance(cid, int):
        raise ErroDeUso("falta o id do clube")
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        if corpo.get("aceitar"):
            ok, recado = eng.aceitar_proposta_emprego(G, cid)
            if ok:
                SESSAO.invalidar()
                SESSAO.esquecer_desfazer()
                SESSAO.mesas = {}
        else:
            ok, recado = eng.recusar_proposta_emprego(G, cid)
        if not ok:
            raise ErroDeUso(recado)
        SESSAO.salvar()
        return {"recado": recado, "painel": dto.painel()}


@rota("GET", "/api/noticias")
def ver_noticias(_corpo):
    with SESSAO.cadeado:
        return {"tela": dto.noticias()}


@rota("POST", "/api/ficha")
def ver_ficha(corpo):
    if "id" not in corpo:
        raise ErroDeUso("falta o id do jogador")
    with SESSAO.cadeado:
        try:
            return {"ficha": dto.ficha(corpo["id"])}
        except KeyError as e:
            raise ErroDeUso(str(e))


# ------------------------------------------------------------ acoes do elenco
def _ids(corpo, campo="ids"):
    ids = corpo.get(campo) or []
    if not isinstance(ids, list) or not ids:
        raise ErroDeUso("selecione pelo menos um jogador")
    try:
        return [int(i) for i in ids]
    except (TypeError, ValueError):
        raise ErroDeUso("id de jogador invalido")


def _meus(G, ids):
    """Só o que é meu de verdade. Quem está emprestado aqui tem passe alheio,
    e o motor recusaria a operação de qualquer jeito - melhor dizer antes."""
    jogs = []
    alheios = []
    for pid in ids:
        j = G["jogadores"].get(pid)
        if j is None:
            raise ErroDeUso("jogador %d nao existe" % pid)
        (alheios if j.get("dono") else jogs).append(j)
    return jogs, alheios


@rota("POST", "/api/elenco/tirar-vitrine")
def tirar_vitrine(corpo):
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        proprios, alheios = _meus(G, _ids(corpo))
        if not proprios:
            raise ErroDeUso("%s esta emprestado aqui: o passe nao e seu."
                            % ", ".join(j["nome"] for j in alheios))
        recados = [eng.tirar_da_vitrine(G, j["id"])[1] for j in proprios]
        eng.salvar_auto(G)
        return {"recado": " ".join(r for r in recados if r), "tela": dto.elenco()}


@rota("POST", "/api/elenco/rescindir")
def rescindir(corpo):
    """Dispensar custa multa. A conta vem antes da decisao, nunca depois."""
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        proprios, alheios = _meus(G, _ids(corpo))
        if not proprios:
            raise ErroDeUso("%s esta emprestado aqui: o passe nao e seu."
                            % ", ".join(j["nome"] for j in alheios))
        if not corpo.get("confirmar"):
            multa = sum(eng.multa_rescisao(G, j) for j in proprios)
            folha = sum(j["salario"] for j in proprios)
            return {"confirmar": {
                "titulo": "Rescindir contrato",
                "texto": ("Dispensar %s\n\ncusta %s de multa e alivia %s por mes."
                          % (", ".join(j["nome"] for j in proprios),
                             eng.din(multa), eng.din(folha))),
                "perigo": True}}
        recados = [eng.rescindir_contrato(G, j["id"])[1] for j in proprios]
        eng.salvar_auto(G)
        SESSAO.invalidar()
        return {"recado": " ".join(r for r in recados if r), "tela": dto.elenco()}


@rota("POST", "/api/elenco/opcao")
def exercer_opcao(corpo):
    """Compra em definitivo quem esta emprestado aqui com opcao combinada."""
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        ids = _ids(corpo)
        com = []
        for pid in ids:
            j = G["jogadores"].get(pid)
            if j is None:
                raise ErroDeUso("jogador %d nao existe" % pid)
            preco = eng.opcao_disponivel(G, j, G["clube"])
            if preco > 0:
                com.append((j, preco))
        if not com:
            raise ErroDeUso("Nenhum dos marcados tem opcao de compra combinada.")
        if not corpo.get("confirmar"):
            total = sum(p for _, p in com)
            detalhe = "\n".join("  %s por %s" % (j["nome"], eng.din(p)) for j, p in com)
            return {"confirmar": {
                "titulo": "Opcao de compra",
                "texto": ("Comprar em definitivo:\n%s\n\nTotal: %s\nCaixa: %s"
                          % (detalhe, eng.din(total),
                             eng.din(G["clubes"][G["clube"]]["dinheiro"])))}}
        recados = [eng.exercer_opcao(G, j["id"], G["clube"]) for j, _ in com]
        eng.salvar_auto(G)
        SESSAO.invalidar()
        return {"recado": " ".join(str(r) for r in recados if r), "tela": dto.elenco()}


@rota("POST", "/api/elenco/chamar")
def chamar_de_volta(corpo):
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        if not eng.mercado_aberto(G):
            raise ErroDeUso("Emprestimo so se interrompe com a janela aberta.")
        ids = _ids(corpo)
        js = [G["jogadores"][p] for p in ids if p in G["jogadores"]]
        if not js:
            raise ErroDeUso("selecione quem voce quer de volta")
        if not corpo.get("confirmar"):
            folha = sum(j["salario"] * (j["emp_pct"] / 100.0) for j in js)
            return {"confirmar": {
                "titulo": "Chamar de volta",
                "texto": ("Interromper o emprestimo de %s?\n\n"
                          "A folha deles volta inteira pra voce: %s por mes a mais."
                          % (", ".join(j["nome"] for j in js), eng.din(folha)))}}
        for j in js:
            eng.devolver_emprestimo(G, j["id"])
        eng.salvar_auto(G)
        SESSAO.invalidar()
        return {"recado": "%d jogador(es) de volta ao elenco." % len(js),
                "tela": dto.elenco()}


# -------------------------------------------------------------- acoes da base
@rota("POST", "/api/base/subir")
def subir_da_base(corpo):
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        ids = _ids(corpo)
        js = [G["jogadores"][p] for p in ids if p in G["jogadores"]]
        if not js:
            raise ErroDeUso("selecione um ou mais garotos da base")
        if not corpo.get("confirmar"):
            nomes = "\n".join("  %s, %s, %d anos, overall %d (teto %s)"
                              % (j["nome"], j["pos"], j["idade"], j["ovr"], eng.scout(G, j))
                              for j in js)
            return {"confirmar": {
                "titulo": "Subir ao profissional",
                "texto": ("Subir ao elenco profissional:\n%s\n\n"
                          "Eles passam a receber salario cheio e podem jogar." % nomes)}}
        recados = []
        for j in js:
            feito, recado = eng.promover_da_base(G, j["id"])
            recados.append(recado)
            if not feito:
                break  # elenco cheio: parar e contar, em vez de tentar o resto
        eng.salvar_auto(G)
        SESSAO.invalidar()
        return {"recado": " ".join(r for r in recados if r), "tela": dto.base()}


@rota("POST", "/api/base/liberar")
def liberar_da_base(corpo):
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        ids = _ids(corpo)
        js = [G["jogadores"][p] for p in ids if p in G["jogadores"]]
        if not js:
            raise ErroDeUso("selecione um ou mais garotos da base")
        if not corpo.get("confirmar"):
            return {"confirmar": {
                "titulo": "Liberar da base",
                "texto": ("Liberar de vez:\n\n%s\n\nNao tem multa, e nao tem volta."
                          % ", ".join(j["nome"] for j in js)),
                "perigo": True}}
        recados = [eng.dispensar_da_base(G, j["id"])[1] for j in js]
        eng.salvar_auto(G)
        return {"recado": " ".join(r for r in recados if r), "tela": dto.base()}


# ------------------------------------------------------ acao da infraestrutura
@rota("POST", "/api/infra/investir")
def investir(corpo):
    """Sobe um nivel. O preco e calculado aqui pelo nivel atual, e nao aceito
    do cliente: senao daria para comprar nivel 10 pelo preco do 1."""
    chave = corpo.get("id")
    if chave not in [k for k, _, _ in dto.ITENS_INFRA]:
        raise ErroDeUso("area invalida")
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        c = G["clubes"][G["clube"]]
        if c[chave] >= 10:
            raise ErroDeUso("essa area ja esta no nivel maximo")
        custo = dto.custo_infra(c[chave])
        if custo > c["dinheiro"]:
            raise ErroDeUso("Caixa insuficiente: faltam %s."
                            % eng.din(custo - c["dinheiro"]))
        if not corpo.get("confirmar"):
            return {"confirmar": {
                "titulo": "Investir na estrutura",
                "texto": ("Subir %s para o nivel %d custa %s.\n\nCaixa depois: %s."
                          % (chave.upper(), c[chave] + 1, eng.din(custo),
                             eng.din(c["dinheiro"] - custo)))}}
        c["dinheiro"] -= custo
        c[chave] += 1
        eng.salvar_auto(G)
        return {"recado": "%s agora esta no nivel %d." % (chave.upper(), c[chave]),
                "tela": dto.infra()}


# ------------------------------------------------------------------ escalacao
@rota("GET", "/api/escalacao")
def ver_escalacao(_corpo):
    with SESSAO.cadeado:
        return {"tela": dto.escalacao()}


def _remontar(G, c):
    """O melhor XI para o esquema atual. Mesmo caminho do botao da janela."""
    c["escalacao"] = eng.auto_escalar(G, c)
    c["esc_stamp"] = ""
    SESSAO.invalidar()
    eng.salvar_auto(G)


def _vagas_por_id(G):
    d = SESSAO.diagnostico(recarregar=True)
    return dict(d["vagas"])


@rota("POST", "/api/escalacao/esquema")
def mudar_esquema(corpo):
    """Formacao (pronta ou personalizada) e mentalidade.

    Mentalidade so mexe nos multiplicadores: o XI fica. Formacao no Manual
    mantem os mesmos 11 e so reorganiza as vagas - o time e do usuario; no
    Automatico a maquina remonta. Nos dois casos da para desfazer.
    """
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        c = G["clubes"][G["clube"]]

        if "tatica" in corpo and not ("formacao" in corpo or "contagem" in corpo):
            if corpo["tatica"] not in eng.TATICAS:
                raise ErroDeUso("tatica desconhecida")
            c["tatica"] = corpo["tatica"]
            c["esc_stamp"] = ""
            SESSAO.invalidar()
            eng.salvar_auto(G)
            return {"recado": "Mentalidade: %s. Escalacao mantida." % c["tatica"],
                    "tela": dto.escalacao()}

        custom = None
        if "contagem" in corpo:
            cont = corpo["contagem"] or {}
            ok, motivo = eng.contagem_valida(cont)
            if not ok:
                raise ErroDeUso(motivo)
            formacao = eng.formacao_pronta(cont)
            if formacao is None:
                formacao, custom = eng.FORMACAO_PERSONALIZADA, eng.normalizar_contagem(cont)
        else:
            formacao = corpo.get("formacao")
            if formacao == eng.FORMACAO_PERSONALIZADA:
                if not eng.contagem_valida(c.get("formacao_custom") or {})[0]:
                    raise ErroDeUso("Ainda nao ha formacao personalizada. Use Editar formacao.")
            elif formacao not in eng.FORMACOES:
                raise ErroDeUso("formacao desconhecida")
        if "tatica" in corpo:
            if corpo["tatica"] not in eng.TATICAS:
                raise ErroDeUso("tatica desconhecida")
            c["tatica"] = corpo["tatica"]

        antes = _vagas_por_id(G)
        SESSAO.desfazer_esquema = {
            "formacao": c["formacao"], "formacao_custom": c.get("formacao_custom"),
            "escalacao": list(SESSAO.diagnostico()["escalacao"]),
        }
        c["formacao"] = formacao
        if custom is not None:
            c["formacao_custom"] = custom   # um slot so: o Aplicar sobrescreve
        c["esc_stamp"] = ""
        auto = eng.escalacao_automatica(G, c)
        if auto:
            c["escalacao"] = eng.auto_escalar(G, c)
        else:
            c["escalacao"] = list(SESSAO.desfazer_esquema["escalacao"])
        SESSAO.invalidar()
        depois = _vagas_por_id(G)
        SESSAO.nova_vaga = [p for p, v in depois.items() if p in antes and antes[p] != v]
        eng.salvar_auto(G)

        rotulo = eng.rotulo_formacao(c)
        if auto:
            recado = "Time remontado para %s." % rotulo
        else:
            recado = "Formacao %s aplicada. Mesmos 11, vagas reorganizadas." % rotulo
        return {"recado": recado, "desfazer": True, "tela": dto.escalacao()}


@rota("POST", "/api/escalacao/previa")
def previa_esquema(corpo):
    with SESSAO.cadeado:
        return {"previa": dto.previa_esquema(corpo.get("contagem") or {})}


@rota("POST", "/api/escalacao/desfazer")
def desfazer_esquema(_corpo):
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        c = G["clubes"][G["clube"]]
        foto = SESSAO.desfazer_esquema
        if foto is None:
            raise ErroDeUso("Nada para desfazer.")
        c["formacao"] = foto["formacao"]
        if foto["formacao_custom"] is None:
            c.pop("formacao_custom", None)
        else:
            c["formacao_custom"] = foto["formacao_custom"]
        c["escalacao"] = foto["escalacao"]
        c["esc_stamp"] = ""
        SESSAO.invalidar()
        SESSAO.esquecer_desfazer()
        eng.salvar_auto(G)
        return {"recado": "Voltou para %s." % eng.rotulo_formacao(c), "tela": dto.escalacao()}


@rota("POST", "/api/escalacao/montar")
def montar_melhor(_corpo):
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        SESSAO.esquecer_desfazer()
        _remontar(G, G["clubes"][G["clube"]])
        return {"recado": "Melhor time disponivel montado.", "tela": dto.escalacao()}


@rota("POST", "/api/escalacao/trocar")
def trocar_titular(corpo):
    """Um sai, outro entra. Mexer no time e assumir o comando: a alavanca cede.

    A alternativa seria a maquina desfazer a troca na semana seguinte sem
    avisar - exatamente a reclamacao que a alavanca veio resolver.
    """
    try:
        sai, entra = int(corpo.get("titular")), int(corpo.get("reserva"))
    except (TypeError, ValueError):
        raise ErroDeUso("marque um titular e um reserva")
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        c = G["clubes"][G["clube"]]
        esc, _ = eng.escalacao_valida(G, c)
        if sai not in esc:
            raise ErroDeUso("esse jogador nao esta entre os titulares")
        if entra not in c["elenco"] or entra in esc:
            raise ErroDeUso("esse jogador nao esta no banco")
        if not eng.disponivel(G, entra):
            raise ErroDeUso("%s nao tem condicao de jogar." % G["jogadores"][entra]["nome"])
        SESSAO.esquecer_desfazer()
        desligou = eng.escalacao_automatica(G, c)
        if desligou:
            eng.definir_escalacao_automatica(G, False)
        nova = esc[:]
        nova[nova.index(sai)] = entra
        c["escalacao"] = nova
        c["esc_stamp"] = ""
        SESSAO.invalidar()
        eng.salvar_auto(G)
        recado = "Sai %s, entra %s." % (G["jogadores"][sai]["nome"], G["jogadores"][entra]["nome"])
        if desligou:
            recado += " Voce mexeu no time: a escalacao automatica foi desligada."
        return {"recado": recado, "tela": dto.escalacao()}


@rota("POST", "/api/escalacao/plano")
def mudar_plano(corpo):
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        c = G["clubes"][G["clube"]]
        if corpo.get("padrao"):
            c["plano"] = dict(eng.PLANO_PADRAO)
            c["esc_stamp"] = ""
            feito, recado = True, "Plano de jogo neutro."
        else:
            feito, recado = eng.definir_plano(G, c, corpo.get("eixo"), corpo.get("valor"))
        if not feito:
            raise ErroDeUso(recado)
        SESSAO.invalidar()
        eng.salvar_auto(G)
        return {"recado": recado, "tela": dto.escalacao()}


# ---------------------------------------------------------------------- treino
@rota("GET", "/api/treino")
def ver_treino(_corpo):
    with SESSAO.cadeado:
        return {"tela": dto.treino()}


@rota("POST", "/api/treino/regime")
def escolher_regime(corpo):
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        feito, recado = eng.definir_regime(G, G["clubes"][G["clube"]], corpo.get("nome"))
        if not feito:
            raise ErroDeUso(recado)
        eng.salvar_auto(G)
        return {"recado": recado, "tela": dto.treino()}


@rota("POST", "/api/treino/foco")
def alternar_foco(corpo):
    """Liga ou desliga o treino individual de cada marcado.

    Serve a tela de Treino e a de Base: devolve a tela de quem pediu. Para no
    primeiro que o motor recusar (CT sem vaga) e conta o porque, em vez de
    seguir tentando o resto e esconder o motivo no meio.
    """
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        c = G["clubes"][G["clube"]]
        recados = []
        recusa = None
        for pid in _ids(corpo):
            feito, recado = eng.alternar_foco(G, c, pid)
            if not feito:
                recusa = recado
                break
            recados.append(recado)
        if recusa and not recados:
            raise ErroDeUso(recusa)
        eng.salvar_auto(G)
        tela = dto.base() if corpo.get("tela") == "base" else dto.treino()
        return {"recado": " ".join(recados + ([recusa] if recusa else [])), "tela": tela}


@rota("POST", "/api/treino/limpar")
def limpar_foco(_corpo):
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        G["clubes"][G["clube"]]["treino_foco"] = []
        eng.salvar_auto(G)
        return {"recado": "Treino individual esvaziado.", "tela": dto.treino()}


# --------------------------------------------------------------------- estadio
@rota("GET", "/api/estadio")
def ver_estadio(_corpo):
    with SESSAO.cadeado:
        return {"tela": dto.estadio()}


def _inteiro(corpo, campo, nome):
    try:
        return int(corpo.get(campo))
    except (TypeError, ValueError):
        raise ErroDeUso("%s precisa ser um numero inteiro" % nome)


@rota("POST", "/api/estadio/preco")
def mudar_preco(corpo):
    preco = _inteiro(corpo, "preco", "o preco")
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        c = G["clubes"][G["clube"]]
        c["preco"] = int(eng.clamp(preco, dto.PRECO_MIN, dto.PRECO_MAX))
        eng.salvar_auto(G)
        return {"recado": "Ingresso a R$ %d. Caro afasta publico, barato enche o estadio."
                          % c["preco"], "tela": dto.estadio()}


@rota("POST", "/api/estadio/obra")
def contratar_obra(corpo):
    """O custo e o prazo sao calculados aqui, nunca aceitos do cliente."""
    lugares = _inteiro(corpo, "lugares", "a quantidade de lugares")
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        c = G["clubes"][G["clube"]]
        if c["obra_semanas"]:
            raise ErroDeUso("Ja existe uma obra em andamento.")
        lugares = int(eng.clamp(lugares, dto.LUGARES_MIN, dto.LUGARES_MAX))
        custo = lugares * dto.CUSTO_LUGAR
        semanas = dto.semanas_de_obra(lugares)
        if custo > c["dinheiro"]:
            raise ErroDeUso("Caixa insuficiente: a obra custaria %s e faltam %s."
                            % (eng.din(custo), eng.din(custo - c["dinheiro"])))
        if not corpo.get("confirmar"):
            return {"confirmar": {
                "titulo": "Ampliar o estadio",
                "texto": ("Ampliar em %s lugares custa %s e fica pronto em %d semanas.\n\n"
                          "Caixa depois: %s." % (dto.milhar(lugares), eng.din(custo), semanas,
                                                  eng.din(c["dinheiro"] - custo)))}}
        c["dinheiro"] -= custo
        c["obra_lugares"] = lugares
        c["obra_semanas"] = semanas
        texto = ("Obra contratada: +%s lugares por %s, pronta em %d semanas."
                 % (dto.milhar(lugares), eng.din(custo), semanas))
        SESSAO.anotar(texto)
        eng.salvar_auto(G)
        return {"recado": texto, "tela": dto.estadio()}


# --------------------------------------------------------------------- mercado
def _tela_de_volta(corpo, aba="vitrine"):
    """A acao pode ter vindo do Elenco ou do Mercado: devolve a tela de quem pediu."""
    if corpo.get("tela") == "elenco":
        return dto.elenco()
    return mercado.tela(corpo.get("aba") or aba, corpo.get("filtros"))


def _pares(corpo):
    """[{id, clube_id}] -> [(pid, cid)], sem repetir jogador."""
    fora, vistos = [], set()
    for it in corpo.get("itens") or []:
        try:
            pid, cid = int(it["id"]), int(it["clube_id"])
        except (KeyError, TypeError, ValueError):
            raise ErroDeUso("item invalido")
        if pid not in vistos:
            vistos.add(pid)
            fora.append((pid, cid))
    if not fora:
        raise ErroDeUso("marque pelo menos uma proposta")
    return fora


@rota("POST", "/api/mercado")
def ver_mercado(corpo):
    with SESSAO.cadeado:
        return {"tela": mercado.tela(corpo.get("aba") or "compra", corpo.get("filtros"))}


@rota("GET", "/api/mercado")
def ver_mercado_padrao(_corpo):
    with SESSAO.cadeado:
        return {"tela": mercado.tela("compra")}


@rota("POST", "/api/mercado/mesa")
def ler_mesa(corpo):
    with SESSAO.cadeado:
        try:
            return {"mesa": mercado.mesa(corpo.get("tipo"), int(corpo.get("id")),
                                         corpo.get("proposta"))}
        except (KeyError, ValueError, TypeError) as e:
            raise ErroDeUso(str(e).strip("'"))


@rota("POST", "/api/mercado/propor")
def propor(corpo):
    """A proposta vai inteira; quem decide se passa e o motor."""
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        tipo, pid = corpo.get("tipo"), corpo.get("id")
        try:
            fechou, texto = mercado.propor(tipo, int(pid), corpo.get("proposta") or {})
            leitura = mercado.mesa(tipo, int(pid), corpo.get("proposta"))
        except (KeyError, ValueError, TypeError) as e:
            raise ErroDeUso(str(e).strip("'"))
        if fechou:
            SESSAO.invalidar()
            SESSAO.anotar(texto)
        eng.salvar_auto(G)
        return {"fechou": fechou, "recado": texto, "mesa": leitura}


@rota("POST", "/api/mercado/vitrine/linhas")
def linhas_vitrine(corpo):
    with SESSAO.cadeado:
        return {"linhas": mercado.linhas_vitrine(_ids(corpo))}


@rota("POST", "/api/mercado/vitrine/sugerir")
def sugerir_precos(corpo):
    with SESSAO.cadeado:
        return {"precos": mercado.sugerir_precos(_ids(corpo), corpo.get("pct"))}


@rota("POST", "/api/mercado/vitrine/por")
def por_a_venda(corpo):
    precos = corpo.get("precos") or []
    if not precos:
        raise ErroDeUso("ninguem para por na vitrine")
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        meus = set(G["clubes"][G["clube"]]["elenco"])
        recados = []
        for it in precos:
            try:
                pid, preco = int(it["id"]), int(it["preco"])
            except (KeyError, TypeError, ValueError):
                raise ErroDeUso("preco invalido")
            if pid not in meus:
                raise ErroDeUso("jogador %d nao e do seu elenco" % pid)
            if preco < 1000:
                raise ErroDeUso("o preco minimo de vitrine e R$ 1 mil")
            recados.append(eng.por_a_venda(G, pid, preco)[1])
        eng.salvar_auto(G)
        return {"recado": " ".join(recados), "tela": _tela_de_volta(corpo)}


@rota("POST", "/api/mercado/vitrine/tirar")
def tirar_vitrine_mercado(corpo):
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        meus = set(G["clubes"][G["clube"]]["elenco"])
        recados = [eng.tirar_da_vitrine(G, pid)[1] for pid in _ids(corpo) if pid in meus]
        eng.salvar_auto(G)
        return {"recado": " ".join(recados), "tela": _tela_de_volta(corpo)}


@rota("POST", "/api/mercado/ceder/ofertas")
def ofertas_cessao(corpo):
    with SESSAO.cadeado:
        return {"linhas": mercado.ofertas_cessao(_ids(corpo))}


@rota("POST", "/api/mercado/ceder")
def ceder(corpo):
    """A fatia vem da oferta do clube, nunca do cliente: reler aqui garante que
    o percentual cobrado e o que estava na tabela."""
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        escolhas = []
        for pid, cid in _pares(corpo):
            j = G["jogadores"].get(pid)
            if not j or j["clube"] != G["clube"] or j.get("dono"):
                raise ErroDeUso("jogador %d nao pode ser cedido" % pid)
            pct = dict((cl["id"], pct) for cl, pct in eng.ofertas_emprestimo(G, j)).get(cid)
            if pct is None:
                raise ErroDeUso("o clube nao tem mais interesse em %s" % j["nome"])
            escolhas.append((j, G["clubes"][cid], pct))
        if not corpo.get("confirmar"):
            alivio = sum(j["salario"] * pct // 100 for j, _cl, pct in escolhas)
            linhas = "\n".join("  %s para o %s (eles pagam %d%%)" % (j["nome"], cl["nome"], pct)
                               for j, cl, pct in escolhas)
            return {"confirmar": {
                "titulo": "Ceder por emprestimo",
                "texto": ("%s\n\nA folha alivia %s por mes. Eles voltam no fim da temporada.\n%s"
                          % (linhas, eng.din(alivio), eng.recado_janela(G)))}}
        recados = [eng.ceder_por_emprestimo(G, j["id"], cl["id"], pct)[1]
                   for j, cl, pct in escolhas]
        SESSAO.invalidar()
        eng.salvar_auto(G)
        return {"recado": " ".join(recados), "tela": _tela_de_volta(corpo)}


def _ofertas_marcadas(G, corpo):
    """As propostas marcadas, relidas do motor: o valor vem de la."""
    vivas = {(j["id"], cl["id"]): (j, cl, v) for j, cl, v in eng.propostas_recebidas(G)}
    fora = []
    for par in _pares(corpo):
        if par not in vivas:
            raise ErroDeUso("uma das propostas nao vale mais; a lista foi atualizada")
        fora.append(vivas[par])
    return fora


@rota("POST", "/api/mercado/propostas/aceitar")
def aceitar_propostas(corpo):
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        marcadas = _ofertas_marcadas(G, corpo)
        if not corpo.get("confirmar"):
            caixa = G["clubes"][G["clube"]]["dinheiro"]
            entra = sum(v for _j, _cl, v in marcadas)
            linhas = "\n".join("  %s para o %s por %s" % (j["nome"], cl["nome"], eng.din(v))
                               for j, cl, v in marcadas)
            return {"confirmar": {
                "titulo": "Vender",
                "texto": ("%s\n\nEntram %s no caixa (%s -> %s).\n%s"
                          % (linhas, eng.din(entra), eng.din(caixa), eng.din(caixa + entra),
                             eng.recado_janela(G))),
                "perigo": True}}
        recados = [eng.aceitar_oferta(G, j["id"], cl["id"], v)[1] for j, cl, v in marcadas]
        SESSAO.invalidar()
        eng.salvar_auto(G)
        return {"recado": " ".join(recados), "tela": mercado.tela("vitrine")}


@rota("POST", "/api/mercado/propostas/recusar")
def recusar_propostas(corpo):
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        recados = [eng.recusar_oferta(G, j["id"])[1] for j, _cl, _v in _ofertas_marcadas(G, corpo)]
        eng.salvar_auto(G)
        return {"recado": " ".join(recados), "tela": mercado.tela("vitrine")}


@rota("POST", "/api/mercado/propostas/contra")
def contraproposta(corpo):
    """Pede outro valor por UMA oferta. O comprador responde na hora: fecha,
    sobe, mantem ou desiste - quem decide e o motor."""
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        try:
            pid, cid = int(corpo["id"]), int(corpo["clube_id"])
            valor = int(corpo["valor"])
        except (KeyError, TypeError, ValueError):
            raise ErroDeUso("contraproposta invalida")
        if valor <= 0:
            raise ErroDeUso("diga quanto voce quer pelo jogador")
        desfecho, recado = eng.contraproposta(G, pid, cid, valor)
        if desfecho == "vendido":
            SESSAO.invalidar()
        eng.salvar_auto(G)
        return {"recado": recado, "desfecho": desfecho, "tela": mercado.tela("vitrine")}


@rota("POST", "/api/mercado/agendadas/cancelar")
def cancelar_agendadas(corpo):
    try:
        indices = sorted({int(i) for i in corpo.get("indices") or []}, reverse=True)
    except (TypeError, ValueError):
        raise ErroDeUso("acerto invalido")
    if not indices:
        raise ErroDeUso("marque o acerto que voce quer desfazer")
    with SESSAO.cadeado:
        G = SESSAO.exigir()
        meus = dict(eng.minhas_agendadas(G))
        if any(i not in meus for i in indices):
            raise ErroDeUso("um dos acertos nao existe mais; a lista foi atualizada")
        if not corpo.get("confirmar"):
            nomes = ", ".join(G["jogadores"].get(meus[i]["jogador"], {}).get("nome", "?")
                              for i in indices)
            return {"confirmar": {"titulo": "Cancelar acerto",
                                  "texto": "Desfazer o acerto por %s?\n\nO negocio volta a "
                                           "estaca zero." % nomes, "perigo": True}}
        # do maior para o menor: tirar um da lista nao desloca os que faltam
        recados = [eng.cancelar_agendada(G, i)[1] for i in indices]
        eng.salvar_auto(G)
        return {"recado": " ".join(recados), "tela": _tela_de_volta(corpo)}


# ---------------------------------------------------------------- despachante
def despachar(metodo, caminho, corpo):
    """(status, objeto). Erro do motor nunca derruba o servidor: vira 500 com
    o traceback no console, do mesmo jeito que a janela mostrava a excecao."""
    func = ROTAS.get((metodo, caminho))
    if func is None:
        return 404, {"erro": "rota inexistente", "caminho": caminho}
    try:
        return 200, func(corpo or {})
    except SemJogo as e:
        return 409, {"erro": str(e), "jogo": "sem_save" if not SESSAO.tem_save() else "tem_save"}
    except ErroDeUso as e:
        return 400, {"erro": str(e)}
    except Exception as e:
        traceback.print_exc()
        return 500, {"erro": "%s: %s" % (type(e).__name__, e)}


def json_bytes(obj):
    return json.dumps(obj, ensure_ascii=False).encode("utf-8")
