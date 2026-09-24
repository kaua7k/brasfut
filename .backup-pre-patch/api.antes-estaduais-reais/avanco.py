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

PARADAS_PADRAO = {"lesao": True, "janela": True, "proposta": False, "quebrado": True}


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
             "nota": "%d rodada(s) ate o Brasileirao" % faltam},
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
         "nota": ("%d semana(s)" % janela) if janela > 0 else "sem janela pela frente"},
        {"id": "temporada", "rotulo": "Temporada toda", "semanas": faltam,
         "nota": "as %d semana(s) que faltam, ate a virada do ano" % faltam},
    ]


def foto(G):
    """O que comparar depois da semana para saber o que mudou."""
    c = G["clubes"][G["clube"]]
    return {
        "janela": eng.mercado_aberto(G),
        "lesionados": [p for p in c["elenco"] if G["jogadores"][p]["lesao"] > 0],
        "titulares": list(c.get("escalacao", [])),
        "propostas": len(eng.propostas_recebidas(G)),
        "fase": G["fase"], "temporada": G["temporada"],
    }


def relato(G, antes):
    """Uma linha por jogo do meu clube, mais lesao e proposta nova."""
    c = G["clubes"][G["clube"]]
    if G["fase"] == "estadual":
        cabeca = "Estadual, rodada %d" % max(1, int(G.get("semana_est", 1)) - 1)
    elif G["temporada"] != antes["temporada"]:
        cabeca = "Temporada %d encerrada" % antes["temporada"]
    else:
        cabeca = "Semana %02d" % max(1, G["semana"] - 1)
    linhas = []
    jogos = eng.resultados_da_semana(G)
    if not jogos:
        linhas.append({"texto": "%s · sem jogo" % cabeca, "estado": "neutro"})
    for r in jogos:
        em_casa = r["casa"] == c["id"]
        gm, gs = (r["gc"], r["gf"]) if em_casa else (r["gf"], r["gc"])
        adv = G["clubes"].get(r["fora"] if em_casa else r["casa"])
        comp = G["copas"][r["comp"]]["nome"] if r.get("comp") in G["copas"] else ""
        linhas.append({"texto": "%s · %d x %d %s (%s)%s" % (
            cabeca, gm, gs, adv["nome"] if adv else "-", "casa" if em_casa else "fora",
            " · " + comp if comp else ""),
            "estado": "ok" if gm > gs else ("atencao" if gm == gs else "critico")})
    novas = len(eng.propostas_recebidas(G))
    if novas > antes["propostas"]:
        linhas.append({"texto": "   %d proposta(s) na mesa" % novas, "estado": "atencao"})
    for p in c["elenco"]:
        j = G["jogadores"][p]
        if j["lesao"] > 0 and p not in antes["lesionados"]:
            linhas.append({"texto": "   lesao: %s, %d semana(s) fora" % (j["nome"], j["lesao"]),
                           "estado": "critico"})
    return linhas, bool(jogos)


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
    if p["lesao"]:
        novos = [x for x in c["elenco"] if G["jogadores"][x]["lesao"] > 0
                 and x not in antes["lesionados"] and x in antes["titulares"]]
        if novos:
            return "%s se machucou" % G["jogadores"][novos[0]]["nome"]
    return ""
