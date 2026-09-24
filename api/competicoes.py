# -*- coding: utf-8 -*-
"""Competicoes: cada torneio do ano com a profundidade que ele tem.

Pontos corridos (as quatro series e a primeira fase dos estaduais): tabela
inteira, todas as rodadas com placar ou a jogar, e os meus jogos em destaque.
O estadual leva ainda os grupos, quando tem, e o mata-mata ate a final. Mata-mata (Copa do
Brasil, Libertadores, Sul-Americana): as fases ja jogadas com ida, volta e
penaltis, o sorteio da proxima e as que ainda vem, e onde o meu clube esta.

O motor so passou a guardar resultado por rodada e fase depois desta tela
existir. Save antigo mostra a tabela e o que vier dali para a frente - as
rodadas anteriores aparecem como "sem registro", e nao inventadas.
"""

from .sessao import SESSAO
from . import dto
import brasfut as eng


def _nome(G, cid):
    c = G["clubes"].get(cid)
    return c["nome"] if c else "?"


# ================================================================== lista
def _lista(G):
    """Todos os torneios do ano, os do meu clube primeiro."""
    meu = G["clube"]
    c = G["clubes"][meu]
    itens = []
    for chave, cp in G["copas"].items():
        participa = meu in cp["vivos"] or any(
            meu in (j["a"], j["b"]) for h in cp.get("historico", []) for j in h["jogos"])
        if cp["campeao"]:
            estado = "campeao: %s" % _nome(G, cp["campeao"])
        else:
            estado = eng.nome_fase(len(cp["vivos"]))
        itens.append({"id": "copa:" + chave, "nome": cp["nome"], "tipo": "mata-mata",
                      "meu": participa, "estado": estado,
                      "vivo": meu in cp["vivos"] and not cp["campeao"]})
    for d in "ABCD":
        liga = G["ligas"][d]
        itens.append({"id": "liga:" + d, "nome": "Serie " + d, "tipo": "pontos",
                      "meu": c["divisao"] == d,
                      "estado": "rodada %d de %d" % (liga["rodada"], len(liga["rodadas"])),
                      "vivo": c["divisao"] == d})
    for chave, est in sorted(eng.estaduais(G).items(),
                             key=lambda kv: (meu not in kv[1]["times"], kv[1]["nome"])):
        campanha = eng.campanha_estadual(G, est, meu)
        caiu = campanha.startswith("eliminado") or campanha.endswith("mata-mata")
        itens.append({"id": "est:" + chave, "nome": est["nome"], "tipo": "pontos",
                      "meu": meu in est["times"],
                      "estado": ("campeao: %s" % _nome(G, est["campeao"])
                                 if eng.estadual_terminado(est) and est.get("campeao")
                                 else eng.etapa_estadual(est).lower()),
                      "vivo": meu in est["times"] and not eng.estadual_terminado(est)
                              and not caiu})
    itens.sort(key=lambda x: (not x["meu"],))
    return itens


def _padrao(G):
    meu = G["clube"]
    if G["fase"] in ("estadual", "entretemporada"):
        for chave, est in eng.estaduais(G).items():
            if meu in est["times"]:
                return "est:" + chave
    return "liga:" + G["clubes"][meu]["divisao"]


# ========================================================= pontos corridos
def _pontos(G, liga, alvo, titulo):
    meu = G["clube"]
    resultados = liga.get("resultados") or []
    jogadas = liga["rodada"]
    # quantas rodadas o motor jogou antes de comecar a guardar resultado
    sem_registro = max(0, jogadas - len(resultados))
    rodadas = []
    for i, jogos in enumerate(liga["rodadas"]):
        placares = {}
        if i < jogadas and i >= sem_registro:
            for casa, fora, gc, gf in resultados[i - sem_registro]:
                placares[(casa, fora)] = (gc, gf)
        elif i == jogadas - 1 and liga.get("ultimos"):
            for casa, fora, gc, gf in liga["ultimos"]:
                placares[(casa, fora)] = (gc, gf)
        linha = []
        for casa, fora in jogos:
            p = placares.get((casa, fora))
            linha.append({"casa": _nome(G, casa), "fora": _nome(G, fora),
                          "gc": p[0] if p else None, "gf": p[1] if p else None,
                          "meu": meu in (casa, fora),
                          "resultado": (None if not p or meu not in (casa, fora) else
                                        _resultado(p[0], p[1], casa == meu))})
        rodadas.append({"numero": i + 1, "jogada": i < jogadas,
                        "registrada": i >= sem_registro or i == jogadas - 1 or i >= jogadas,
                        "jogos": linha})

    tabela = dto.tabela(alvo)
    meus = [dict(j, rodada=r["numero"]) for r in rodadas for j in r["jogos"] if j["meu"]]
    return {
        "tipo": "pontos", "titulo": titulo, "id": alvo,
        "legenda": tabela["legenda"], "linhas": tabela["linhas"], "vazio": tabela["vazio"],
        "rodadas": rodadas, "rodada_atual": min(jogadas, len(rodadas) - 1) if rodadas else 0,
        "jogadas": jogadas, "meus_jogos": meus,
        "aviso": ("As %d primeira(s) rodada(s) foram jogadas antes de o jogo guardar "
                  "resultado por rodada: aparecem sem placar." % sem_registro) if sem_registro > 1 else None,
    }


def _resultado(gc, gf, em_casa):
    gm, gs = (gc, gf) if em_casa else (gf, gc)
    return "V" if gm > gs else ("E" if gm == gs else "D")


# =============================================================== mata-mata
def _jogo_copa(G, j, meu):
    a, b = j["a"], j["b"]
    agregado = None
    if j.get("volta"):
        agregado = [j["ida"][0] + j["volta"][0], j["ida"][1] + j["volta"][1]]
    return {"a": _nome(G, a), "b": _nome(G, b), "ida": j["ida"], "volta": j.get("volta"),
            "agregado": agregado,
            "penaltis": _nome(G, j["penaltis"]) if j.get("penaltis") else None,
            "vencedor": _nome(G, j["venc"]) if j.get("venc") else None,
            "venceu_a": j["venc"] == a if j.get("venc") else None,
            "meu": meu in (a, b), "passei": j["venc"] == meu if j.get("venc") else None}


def _copa(G, chave, alvo):
    cp = G["copas"][chave]
    meu = G["clube"]
    fases = []
    for h in cp.get("historico", []):
        fases.append({"nome": h["fase"], "semana": h["semana"], "estado": "jogada",
                      "jogos": [_jogo_copa(G, j, meu) for j in h["jogos"]]})
    jogadas_sem_registro = cp["fase"] - len(fases)
    sorteio = eng.sorteio_da_copa(G, chave)
    if not cp["campeao"] and cp["fase"] < len(cp["semanas"]):
        fases.append({"nome": eng.nome_fase(len(cp["vivos"])), "semana": cp["semanas"][cp["fase"]],
                      "estado": "sorteada",
                      "jogos": [{"a": _nome(G, a), "b": _nome(G, b), "ida": None, "volta": None,
                                 "agregado": None, "penaltis": None, "vencedor": None,
                                 "venceu_a": None, "meu": meu in (a, b), "passei": None}
                                for a, b in sorteio]})
        n = len(cp["vivos"]) // 2
        for sem in cp["semanas"][cp["fase"] + 1:]:
            if n < 2:
                break
            fases.append({"nome": eng.nome_fase(n), "semana": sem, "estado": "futura", "jogos": []})
            n //= 2

    # onde o meu clube esta nesta copa, numa frase
    situacao = None
    if cp["campeao"] == meu:
        situacao = {"estado": "ok", "texto": "Campeao! O titulo e seu."}
    elif meu in cp["vivos"] and not cp["campeao"]:
        par = next((p for p in sorteio if meu in p), None)
        if par:
            adv = par[1] if par[0] == meu else par[0]
            final = len(cp["vivos"]) == 2
            situacao = {"estado": "ok", "texto": "Vivo. %s contra %s na semana %d%s." % (
                eng.nome_fase(len(cp["vivos"])), _nome(G, adv), cp["semanas"][cp["fase"]],
                " (jogo unico, campo neutro)" if final else
                (", ida em casa" if par[0] == meu else ", ida fora"))}
    else:
        for f in fases:
            for j in f["jogos"]:
                if j["meu"] and j["vencedor"] and not j["passei"]:
                    situacao = {"estado": "critico",
                                "texto": "Eliminado na %s por %s." % (f["nome"].lower(), j["vencedor"])}
        if situacao is None and not any(j["meu"] for f in fases for j in f["jogos"]):
            situacao = {"estado": "neutro", "texto": "Seu clube nao disputa esta copa neste ano."}
    return {
        "tipo": "mata-mata", "titulo": cp["nome"], "id": alvo,
        "campeao": _nome(G, cp["campeao"]) if cp["campeao"] else None,
        "situacao": situacao, "fases": fases,
        "aviso": ("%d fase(s) foram jogadas antes de o jogo guardar o chaveamento."
                  % jogadas_sem_registro) if jogadas_sem_registro > 0 else None,
    }


# ================================================================ estadual
def _estadual(G, est, alvo):
    """Primeira fase como pontos corridos (grupos, se houver) e, por cima, o
    mata-mata: fases jogadas, a que esta em curso e as que ainda vem."""
    meu = G["clube"]
    detalhe = _pontos(G, est, alvo, est["nome"])
    tabela = dto.tabela(alvo)
    detalhe["grupos"] = tabela.get("grupos")
    detalhe["fase1"] = est.get("nome1") or "Primeira fase"
    detalhe["mata"] = None
    detalhe["situacao"] = None
    if not eng.tem_mata(est):
        return detalhe

    fases = []
    for k, f in enumerate(est["mata"]):
        if k < est["mata_fase"] or eng.estadual_terminado(est):
            estado = "jogada"
        elif f["jogos"]:
            estado = "sorteada"
        else:
            estado = "futura"
        nota = None
        if estado == "sorteada":
            nota = eng.etapa_estadual(est).split(", ", 1)[-1] if k == est["mata_fase"] else None
        elif estado == "futura":
            nota = ("classificados: %d por grupo" % eng.vagas_por_grupo(est)
                    if k == 0 and est.get("grupos") else
                    "os %d primeiros" % eng.vagas_por_grupo(est) if k == 0 else "a definir")
        fases.append({"nome": f["nome"] + (" (ida e volta)" if f["ida_volta"] else " (jogo unico)"),
                      "semana": eng.semana_da_fase(est, k), "estado": estado, "nota": nota,
                      "jogos": [_jogo_copa(G, j, meu) for j in f["jogos"]]})
    detalhe["mata"] = fases

    if meu in est["times"]:
        campanha = eng.campanha_estadual(G, est, meu)
        if campanha == "campeao":
            situacao = {"estado": "ok", "texto": "Campeao! O titulo e seu."}
        elif campanha.startswith("vivo"):
            situacao = {"estado": "ok", "texto": "Vivo no mata-mata: %s." % campanha[6:]}
        elif campanha == "vice-campeao" or campanha.startswith("eliminado")                 or campanha.endswith("mata-mata"):
            situacao = {"estado": "critico", "texto": "Campanha encerrada: %s." % campanha}
        else:
            situacao = {"estado": "neutro",
                        "texto": "%s: voce esta em %s. Passam %d%s ao mata-mata." % (
                            detalhe["fase1"], campanha, eng.vagas_por_grupo(est),
                            " por grupo" if est.get("grupos") else "")}
        detalhe["situacao"] = situacao
    return detalhe


# ==================================================================== tela
def tela(alvo=None):
    G = SESSAO.exigir()
    alvo = alvo or _padrao(G)
    if alvo.startswith("copa:") and alvo[5:] in G["copas"]:
        detalhe = _copa(G, alvo[5:], alvo)
    elif alvo.startswith("est:") and alvo[4:] in eng.estaduais(G):
        detalhe = _estadual(G, eng.estaduais(G)[alvo[4:]], alvo)
    else:
        d = alvo[5:] if alvo.startswith("liga:") and alvo[5:] in G["ligas"] else \
            G["clubes"][G["clube"]]["divisao"]
        alvo = "liga:" + d
        detalhe = _pontos(G, G["ligas"][d], alvo, "Serie " + d)
    return {"cabecalho": dto.cabecalho(G), "titulo": "Competicoes",
            "subtitulo": "Temporada %d · tudo o que o seu clube disputa, e o resto do pais"
                         % G["temporada"],
            "lista": _lista(G), "alvo": alvo, "detalhe": detalhe}
