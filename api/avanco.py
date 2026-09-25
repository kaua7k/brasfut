# -*- coding: utf-8 -*-
"""Avancar em ritmos: jogo a jogo, semana, mes, janela e temporada.

A semana do jogo e uma rodada, entao todo ritmo e "N semanas" com uma regra de
parada. Quem roda o laco e o navegador, uma semana por pedido: assim a tela
mostra a barra andando e o Parar funciona no meio, como no painel de avanco da
janela tkinter. Aqui mora o que precisa do mundo: quantas semanas cada opcao
cobre agora, o relato de cada semana e o motivo de parar antes.

Paradas que valem sempre, qualquer que seja o ritmo: fim do estadual, fim da
temporada, carreira encerrada e demissao (a escolha do clube novo trava o jogo).
"""

import brasfut as eng

PARADAS_PADRAO = {"lesao": True, "janela": True, "proposta": False, "quebrado": True,
                  "emprego": True}


def _semanas_ate_mudar_janela(G):
    """Quantas semanas ate a janela mudar de estado (abrir ou fechar)."""
    if not eng.mercado_aberto(G):
        return eng.proxima_janela(G)
    sem = G["semana"]
    n = 0
    while sem + n in eng.JANELAS or n == 0:
        n += 1
        if n > eng.SEMANAS_LIGA:
            break
    return n


def opcoes(G):
    """(id, rotulo, semanas, nota). semanas <= 0 desliga a opcao na tela."""
    if eng.temporada_encerrada(G):
        # a virada nao se simula: ela tem resumo e pode ter demissao
        return []
    if G["fase"] == "entretemporada":
        # comecar o estadual tem os avisos proprios (contrato vencido, elenco
        # curto): fica no botao do topo, nao num pulo de simulacao
        return []
    if G["fase"] == "estadual":
        faltam = max(0, eng.rodadas_estaduais(G) - int(G.get("semana_est", 1)) + 1)
        return [
            {"id": "jogo", "rotulo": "Jogo a jogo", "semanas": faltam,
             "nota": "ate o proximo jogo do seu clube"},
            {"id": "semana", "rotulo": "1 semana", "semanas": min(1, faltam) or 1,
             "nota": "uma rodada do estadual"},
            {"id": "mes", "rotulo": "1 mes", "semanas": min(4, faltam),
             "nota": "quatro rodadas"},
            {"id": "temporada", "rotulo": "Ate o fim do estadual", "semanas": faltam,
             "nota": "%s ate o Brasileirao" % eng.plural(faltam, "rodada")},
        ]
    faltam = max(0, eng.SEMANAS_LIGA - G["semana"] + 1)
    janela = _semanas_ate_mudar_janela(G)
    aberta = eng.mercado_aberto(G)
    return [
        {"id": "jogo", "rotulo": "Jogo a jogo", "semanas": faltam,
         "nota": "ate o proximo jogo do seu clube, liga ou copa"},
        {"id": "semana", "rotulo": "1 semana", "semanas": 1,
         "nota": "uma rodada da liga e o que mais houver na semana"},
        {"id": "mes", "rotulo": "1 mes", "semanas": min(4, faltam), "nota": "quatro semanas"},
        {"id": "janela", "rotulo": "Ate a janela %s" % ("fechar" if aberta else "abrir"),
         "semanas": min(janela, faltam),
         "nota": eng.plural(janela, "semana") if janela > 0 else "sem janela pela frente"},
        {"id": "temporada", "rotulo": "Temporada toda", "semanas": faltam,
         "nota": "%s que faltam, ate a virada do ano" % eng.plural(faltam, "semana")},
    ]


def foto(G):
    """O que comparar depois da semana para saber o que mudou."""
    c = G["clubes"][G["clube"]]
    return {
        "janela": eng.mercado_aberto(G),
        "lesionados": [p for p in c["elenco"] if G["jogadores"][p]["lesao"] > 0],
        "titulares": list(c.get("escalacao", [])),
        "propostas": len(eng.propostas_recebidas(G)),
        "empregos": {o["id"] for o in eng.propostas_emprego(G)},
        "fase": G["fase"], "temporada": G["temporada"],
    }


def decisao(G, r, meu):
    """O que o jogo decidiu no mata-mata, do ponto de vista do meu clube.

    None quando o jogo nao decide nada (pontos corridos, grupo, ida). O jogo
    de volta carrega o agregado e, no empate, quem passou nos penaltis - antes
    o relato mostrava so o placar e o empate ficava sem dono.
    """
    venc = r.get("venc")
    if venc is None or r.get("perna") == "ida":
        return None
    passou = venc == meu
    cp = G["copas"].get(r.get("comp"))
    final = bool(cp and cp.get("campeao") == venc and "agregado" not in r)
    if final:
        texto = "Campeao" if passou else "Vice-campeao"
    else:
        texto = "Classificado" if passou else "Eliminado"
    if r.get("penaltis"):
        texto += " nos penaltis"
    if r.get("agregado"):
        a, ga, _b, gb = r["agregado"]
        mg, sg = (ga, gb) if a == meu else (gb, ga)
        texto += " · agregado %d x %d" % (mg, sg)
    return {"texto": texto, "estado": "ok" if passou else "critico"}


def relato(G, antes):
    """A semana que acabou: os jogos do meu clube e o que mudou no elenco.

    Mandante primeiro no placar, como no cartao da partida; `eu` diz o lado.
    """
    c = G["clubes"][G["clube"]]
    if G["fase"] == "estadual":
        titulo = "Estadual, rodada %d" % max(1, int(G.get("semana_est", 1)) - 1)
    elif G["temporada"] != antes["temporada"]:
        titulo = "Temporada %d encerrada" % antes["temporada"]
    else:
        titulo = "Semana %02d" % max(1, G["semana"] - 1)
    jogos = []
    for r in eng.resultados_da_semana(G):
        em_casa = r["casa"] == c["id"]
        gm, gs = (r["gc"], r["gf"]) if em_casa else (r["gf"], r["gc"])
        resultado = "V" if gm > gs else ("E" if gm == gs else "D")
        casa, fora = G["clubes"].get(r["casa"]), G["clubes"].get(r["fora"])
        jogos.append({
            "resultado": resultado,
            "estado": {"V": "ok", "E": "atencao", "D": "critico"}[resultado],
            "times": [casa["nome"] if casa else "-", fora["nome"] if fora else "-"],
            "placar": [r["gc"], r["gf"]], "eu": 0 if em_casa else 1,
            "comp": eng.nome_competicao(G, r.get("comp"), casa),
            "decisao": decisao(G, r, c["id"]),
        })
    avisos = []
    novas = len(eng.propostas_recebidas(G))
    if novas > antes["propostas"]:
        avisos.append({"texto": "%s por jogador seu na mesa" % eng.plural(novas, "proposta"),
                       "estado": "atencao"})
    for p in c["elenco"]:
        j = G["jogadores"][p]
        if j["lesao"] > 0 and p not in antes["lesionados"]:
            avisos.append({"texto": "Lesao: %s, %s fora" % (j["nome"], eng.plural(j["lesao"], "semana")),
                           "estado": "critico"})
    return {"titulo": titulo, "jogos": jogos, "avisos": avisos}, bool(jogos)


def motivo_de_parar(G, antes, paradas, encerrada, pendencia):
    """Por que o laco deve parar depois desta semana. "" = pode seguir."""
    if encerrada:
        return "carreira encerrada"
    if pendencia:
        return "voce precisa escolher um clube"
    if G["temporada"] != antes["temporada"] or eng.temporada_encerrada(G):
        return "a temporada acabou"
    if antes["fase"] == "estadual" and G["fase"] != "estadual":
        return "o estadual acabou"
    p = dict(PARADAS_PADRAO, **(paradas or {}))
    c = G["clubes"][G["clube"]]
    if p["janela"] and eng.mercado_aberto(G) and not antes["janela"]:
        return "a janela de transferencias abriu"
    if p["proposta"] and len(eng.propostas_recebidas(G)) > antes["propostas"]:
        return "chegou proposta por um jogador seu"
    novas = [o for o in eng.propostas_emprego(G) if o["id"] not in antes.get("empregos", set())]
    if p.get("emprego") and novas:
        return "o %s quer contratar voce" % novas[0]["clube"]
    if p["lesao"]:
        novos = [x for x in c["elenco"] if G["jogadores"][x]["lesao"] > 0
                 and x not in antes["lesionados"] and x in antes["titulares"]]
        if novos:
            return "%s se machucou" % G["jogadores"][novos[0]]["nome"]
    return ""
