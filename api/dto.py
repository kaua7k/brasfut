# -*- coding: utf-8 -*-
"""De G para a tela: uma funcao por tela, nenhuma regra de jogo aqui dentro.

A tela nunca recebe G cru. O save inteiro passa de 2 MB e quase nada dele
interessa ao Painel; pior, mandar o mundo aberto faria a interface reimplementar
regra do motor para saber o que exibir. Entao cada tela tem o seu DTO: o motor
decide, esta camada traduz, o React so desenha.

Migrar uma tela nova da janela tkinter = escrever a funcao dela aqui e pendurar
uma rota. Nada mais.
"""

import re

from . import campo
from .sessao import SESSAO
import brasfut as eng

LIMPA_COR = re.compile(r"\033\[[0-9;]*m")

# o menu lateral e o mesmo do tkinter (NAV em brasfut_app.py). "pronta" diz o
# que ja migrou: o React apaga o resto em vez de fingir que leva a algum lugar
MENU = [
    ("painel", "Painel", True), ("elenco", "Elenco", True), ("base", "Base", True),
    ("treino", "Treino", True), ("escalacao", "Escalacao", True),
    ("tabela", "Classificacao", True), ("copas", "Competicoes", True),
    ("mercado", "Mercado", True), ("financas", "Financas", True),
    ("estadio", "Estadio", True), ("infra", "Infraestrutura", True),
    ("noticias", "Noticias", True), ("carreira", "Carreira", True),
]


def _corta(txt, n):
    txt = (txt or "").strip()
    return txt if len(txt) <= n else txt[:n - 1] + "…"


def _iniciais(nome):
    partes = [p for p in (nome or "").split() if p]
    if not partes:
        return "?"
    if len(partes) == 1:
        return partes[0][:2].upper()
    return (partes[0][0] + partes[-1][0]).upper()


# ------------------------------------------------------------------ cabecalho
def cabecalho(G):
    c = G["clubes"][G["clube"]]
    fase = G["fase"]
    # tres momentos do ano que o botao do topo precisa distinguir: a temporada
    # acabou (a virada espera o clique), a pre-temporada (mercado aberto,
    # renovar quem venceu) e o ano em andamento
    if eng.temporada_encerrada(G):
        fase = "encerrada"
        quando = "Temporada %d encerrada . a virada acontece quando voce mandar" % G["temporada"]
        acao = "Comecar o ano %d" % (G["temporada"] + 1)
    elif G["fase"] == "entretemporada":
        quando = "Pre-temporada %d . mercado aberto, o ano comeca pelo estadual" % G["temporada"]
        acao = "Comecar o estadual"
    elif G["fase"] == "estadual":
        est = eng.meu_estadual(G)
        quando = "%s . %s . semana %d de %d" % (est["nome"] if est else "Estadual",
                                                eng.etapa_estadual(est) if est else "sem jogo",
                                                int(G.get("semana_est", 1)),
                                                eng.rodadas_estaduais(G))
        acao = "Avancar rodada"
    else:
        quando = "Temporada %d . semana %d de %d" % (G["temporada"], G["semana"],
                                                     eng.SEMANAS_LIGA)
        acao = "Avancar semana"
    return {
        "clube": c["nome"],
        "divisao": c["divisao"],
        "subtitulo": "%s . %s" % (eng.nome_da_liga(G, c["divisao"]), quando),
        "fase": fase,
        "acao": acao,
        "chips": [
            {"label": "Caixa", "valor": eng.din(c["dinheiro"]),
             "estado": "ok" if c["dinheiro"] >= 0 else "critico"},
            {"label": "Verba", "valor": eng.din(eng.verba_contratacao(G, c)),
             "estado": "ok" if eng.verba_contratacao(G, c) > 0 else "critico"},
            {"label": "Folha/mes", "valor": eng.din(eng.folha_semanal(G, c) * 4)},
            {"label": "Elenco", "valor": "%d jogadores" % len(c["elenco"])},
        ],
        "menu": [{"id": k, "nome": n, "pronta": p} for k, n, p in MENU],
    }


# -------------------------------------------------------------------- painel
def _prontidao(G, d):
    if eng.temporada_encerrada(G):
        r = eng.apurar_temporada(G)
        return {"estado": "ok" if r["objetivo_ok"] else "atencao",
                "titulo": "TEMPORADA %d ENCERRADA - %do lugar na %s"
                          % (r["temporada"], r["posicao"], eng.liga_do_resumo(r)),
                "detalhe": "Meta era top %d: %s. A virada do ano (acesso, contratos, "
                           "diretoria) acontece em Comecar o ano %d."
                           % (r["alvo"], "cumprida" if r["objetivo_ok"] else "nao cumprida",
                              G["temporada"] + 1),
                "acao": {"label": "Ver como terminou", "destino": "resumo"}}
    if G["fase"] == "entretemporada":
        r = G.get("ultimo_resumo")
        return {"estado": "ok", "titulo": "PRE-TEMPORADA %d ABERTA" % G["temporada"],
                "detalhe": "Mercado aberto. Renove quem venceu contrato antes de comecar o estadual.",
                "acao": ({"label": "Resumo de %d" % r["temporada"], "destino": "resumo"} if r else
                         {"label": "Abrir mercado", "destino": "mercado"})}
    acao = None
    if d["estado"] == "critico":
        acao = {"label": "Abrir escalacao", "destino": "escalacao"}
    elif d["estado"] == "atencao":
        acao = {"label": "Revisar escalacao", "destino": "escalacao"}
    elif d["estado"] == "neutro" and eng.mercado_aberto(G):
        acao = {"label": "Abrir mercado", "destino": "mercado"}
    return {"estado": d["estado"], "titulo": d["titulo"],
            "detalhe": _corta(d["detalhe"], 120), "acao": acao}


def _proximo(G, d):
    """O proximo jogo e o duelo que decide o placar. A partida cruza ataque de
    um com defesa do outro (xG = ataque / defesa adversaria), entao a barra
    compara "meu ataque x defesa dele" e "minha defesa x ataque dele" - ataque
    contra ataque enganava. Os dois lados com o XI da competicao do jogo
    (suspensao de copa nao vale na liga)."""
    c = G["clubes"][G["clube"]]
    jogos = eng.jogos_da_semana(G, G["clube"])
    base = {"ataque": {"meu": round(d["ataque"], 1), "dele": None},
            "defesa": {"meu": round(d["defesa"], 1), "dele": None},
            "extras": max(0, len(jogos) - 1)}

    def duelo(comp, cadv):
        at_m, de_m, _ = eng.forcas(G, c, comp)
        at, de, _ = eng.forcas(G, cadv, comp)
        base["ataque"] = {"meu": round(at_m, 1), "dele": round(de, 1)}
        base["defesa"] = {"meu": round(de_m, 1), "dele": round(at, 1)}

    if G["fase"] == "entretemporada":
        base.update(tipo="pretemporada", adversario="Pre-temporada",
                    legenda="o calendario comeca quando voce avancar", em_casa=None)
        return base
    if not jogos:
        base.update(tipo="folga", adversario="Semana livre",
                    legenda="sem jogo nesta rodada", em_casa=None)
        return base

    for comp, casa, fora in jogos:
        # liga e estadual tem mando definido; copa so depois do sorteio
        if comp in ("liga", "estadual") and casa is not None:
            adv = fora if casa == G["clube"] else casa
            cadv = G["clubes"][adv]
            if comp == "estadual":
                est = eng.meu_estadual(G)
                legenda = "%s . %s" % (_corta(est["nome"], 22) if est else "Estadual",
                                       eng.etapa_estadual(est).lower() if est else "")
            else:
                legenda = "%s . rodada %d" % (eng.nome_da_liga(G, c["divisao"]),
                                                    G["ligas"][c["divisao"]]["rodada"] + 1)
            base.update(tipo="jogo", adversario=eng.nome_clube(G, cadv["id"]), legenda=legenda,
                        em_casa=(casa == G["clube"]),
                        forte=cadv["reputacao"] > c["reputacao"])
            duelo(comp, cadv)
            return base

    # copa: o sorteio sai assim que a fase anterior acaba, entao o adversario
    # ja e conhecido - antes ele so existia no instante do jogo
    chave, casa, fora = jogos[0]
    copa = G["copas"].get(chave)
    if copa and casa is not None:
        # fase de grupos: adversario e mando ja sao da tabela do grupo
        adv = fora if casa == G["clube"] else casa
        cadv = G["clubes"][adv]
        g = eng.grupo_de(copa, G["clube"])
        base.update(tipo="copa", adversario=eng.nome_clube(G, cadv["id"]),
                    legenda="%s . %s, rodada %d" % (copa["nome"], g["nome"] if g else eng.FASE_GRUPOS,
                                                    copa["rodada_grupo"] + 1),
                    em_casa=casa == G["clube"], forte=cadv["reputacao"] > c["reputacao"])
        duelo(chave, cadv)
        return base
    if copa:
        par = next((p for p in eng.sorteio_da_copa(G, chave) if G["clube"] in p), None)
        if par:
            adv = par[1] if par[0] == G["clube"] else par[0]
            cadv = G["clubes"][adv]
            final = len(copa["vivos"]) == 2
            base.update(tipo="copa", adversario=eng.nome_clube(G, cadv["id"]),
                        legenda="%s . %s" % (copa["nome"], eng.fase_da_copa(copa)),
                        em_casa=None if final else (par[0] == G["clube"]),
                        forte=cadv["reputacao"] > c["reputacao"])
            duelo(chave, cadv)
            return base
    base.update(tipo="copa", adversario=copa["nome"] if copa else "Jogo do calendario",
                legenda="adversario definido no sorteio", em_casa=None)
    return base


def _xi(G, d):
    """O XI que entra em campo, ja com o ponto no campo e o preco do improviso."""
    jogs = G["jogadores"]
    pontos = campo.posicionar(d["vagas"])
    fora = []
    for pid, vaga in d["vagas"]:
        j = jogs[pid]
        improvisado = vaga != j["pos"]
        afin = eng.AFINIDADE[j["pos"]][vaga]
        estado, obs = "ok", ""
        if improvisado:
            estado = "critico" if afin < 0.60 else "atencao"
            obs = "rende %d%%" % int(afin * 100)
        elif j["cond"] < 45:
            estado, obs = "critico", "desgastado"
        elif j.get("amar", {}).get("liga", 0) >= 2:
            estado, obs = "atencao", "pendurado"
        p = pontos.get(pid, {"x": 50, "y": 50, "ordem": 0})
        fora.append({
            "id": pid, "nome": j["nome"], "curto": _corta(j["nome"], 14),
            "iniciais": _iniciais(j["nome"]), "pos": j["pos"], "vaga": vaga,
            "improvisado": improvisado, "afinidade": round(afin, 2),
            "ovr": j["ovr"], "cond": j["cond"], "estado": estado, "obs": obs,
            "x": p["x"], "y": p["y"], "numero": p["ordem"],
        })
    fora.sort(key=lambda x: x["numero"])
    return fora, 11 - len(fora)


def _objetivo(G):
    c = G["clubes"][G["clube"]]
    liga = G["ligas"][c["divisao"]]
    total = max(1, len(liga["times"]))
    alvo = G.get("objetivo_alvo", 16)
    comecou = liga["rodada"] > 0
    pos = eng.posicao_na_liga(G, c["id"]) if comecou else total

    if not comecou:
        estado, fala = "neutro", "aguardando a bola rolar"
    elif eng.tem_rebaixamento(c["divisao"]) and pos > total - 4:
        estado, fala = "critico", "zona de rebaixamento: risco alto de demissao"
    elif pos <= alvo:
        estado, fala = "ok", "tranquila"
    elif pos <= alvo + 2:
        estado, fala = "atencao", "cobrando resultado"
    elif G["semana"] <= 22:
        estado, fala = "atencao", "fora da meta, ainda da tempo"
    else:
        estado, fala = "critico", "risco real de demissao"

    conf = _confianca(G)
    if conf["aviso"] or conf["valor"] < 50:
        fala = conf["fala"]
    return {"texto": G["objetivo"], "pos": pos if comecou else None, "total": total,
            "alvo": alvo, "comecou": comecou, "estado": estado, "diretoria": fala,
            "confianca": conf,
            "folga": (alvo - pos) if comecou else None,
            "progresso": round(100.0 * (total - pos + 1) / total, 1) if comecou else 0,
            "marca": round(100.0 * (total - alvo + 1) / total, 1)}


def _confianca(G):
    """O numero da diretoria, a tendencia de 4 semanas e as causas da ultima."""
    conf = eng.confianca(G)
    valor = conf["valor"]
    aviso = conf["aviso"] is not None
    if aviso:
        estado, fala = "critico", "ultimato: abaixo de %d voce e demitido" % eng.CONFIANCA_DEMISSAO
    elif valor < eng.CONFIANCA_AVISO:
        estado, fala = "critico", "a paciencia acabou"
    elif valor < 50:
        estado, fala = "atencao", "cobrando resultado"
    elif valor < 75:
        estado, fala = "ok", "tranquila"
    else:
        estado, fala = "ok", "confiante no trabalho"
    ultima = conf["hist"][-1][2] if conf["hist"] else []
    return {
        "valor": valor, "estado": estado, "fala": fala, "aviso": aviso,
        "tendencia": eng.tendencia_confianca(G),
        "limite_aviso": eng.CONFIANCA_AVISO, "limite_demissao": eng.CONFIANCA_DEMISSAO,
        "causas": [{"texto": "%+d %s" % (d, txt), "estado": "ok" if d > 0 else "critico"}
                   for d, txt in ultima],
    }


def rotulo_zona(zona, div=None, estadual=False):
    """O que a faixa colorida da tabela quer dizer, em palavras: a cor sozinha
    nao chega a quem nao distingue verde de vermelho."""
    if not zona:
        return None
    if estadual:
        return "vai ao mata-mata"
    if zona == "baixa":
        return "rebaixamento"
    if div in eng.DIVISOES_BR and div != "A":
        return "acesso"
    return "G4"


def _tabela(G, quantas=6):
    c = G["clubes"][G["clube"]]
    est = eng.meu_estadual(G) if G["fase"] == "estadual" else None
    liga = est or G["ligas"][c["divisao"]]
    titulo = est["nome"] if est else "Classificacao . %s" % eng.nome_da_liga(G, c["divisao"])
    g = eng.grupo_do_clube(est, c["id"]) if est else None
    if g is not None:
        # no estadual com grupos, a briga e dentro do meu grupo
        liga = eng.subtabela(est, est["grupos"][g])
        titulo = "%s . Grupo %s" % (est["nome"], "ABCDEFGH"[g])
    if liga["rodada"] <= 0 or c["id"] not in liga["times"]:
        return {"titulo": titulo, "linhas": [],
                "vazio": "Ainda nao comecou." if liga["rodada"] <= 0
                         else "Seu clube nao esta neste torneio."}
    ordem = eng.classificacao(G, liga)
    meu = ordem.index(c["id"])
    # a janela mostra a minha vizinhanca, nao o topo: o que importa e com quem
    # eu estou brigando agora
    ini = max(0, min(meu - quantas // 2, len(ordem) - quantas))
    linhas = []
    for i in range(ini, min(len(ordem), ini + quantas)):
        cid = ordem[i]
        t = liga["tabela"][str(cid)]
        if est:
            # no estadual, a zona e a do mata-mata; nao ha rebaixamento
            zona = "alta" if i < eng.vagas_por_grupo(est) else ""
        else:
            rebaixa = eng.tem_rebaixamento(c["divisao"])
            zona = "alta" if i < 4 else ("baixa" if rebaixa and i >= len(ordem) - 4 else "")
        linhas.append({"pos": i + 1, "clube": _corta(G["clubes"][cid]["nome"], 18),
                       "j": t["j"], "sg": t["gp"] - t["gc"], "v": t.get("v", 0),
                       "pts": t["p"], "eu": cid == c["id"], "zona": zona,
                       "zona_texto": rotulo_zona(zona, c["divisao"], bool(est))})
    return {"titulo": titulo, "vazio": None, "linhas": linhas}


def _destaques(G, quantos=3):
    c = G["clubes"][G["clube"]]
    melhores = sorted([G["jogadores"][p] for p in c["elenco"]],
                      key=lambda x: (-x["g"], -x["a"], -x["ovr"]))[:quantos]
    if not melhores or melhores[0]["g"] == 0:
        # sem gol marcado, artilharia nao diz nada: o criterio vira qualidade
        melhores = sorted([G["jogadores"][p] for p in c["elenco"]],
                          key=lambda x: -x["ovr"])[:quantos]
    return [{"id": j["id"], "nome": _corta(j["nome"], 18), "iniciais": _iniciais(j["nome"]),
             "pos": j["pos"], "ovr": j["ovr"], "g": j["g"], "a": j["a"]}
            for j in melhores]


def _alerta_de_fase(G):
    """Tres tropecos seguidos e um problema, e o diagnostico nao olha para isso.

    Ele so ve lesao, suspensao e improviso: um time inteiro e saudavel perdendo
    todo domingo apareceria como TIME PRONTO.
    """
    forma = eng.forma_recente(G, 5)
    if len(forma) < 3:
        return None
    ultimos = [f[0] for f in forma[-3:]]
    if ultimos == ["D", "D", "D"]:
        return {"texto": "Tres derrotas seguidas. Reveja o plano de jogo e quem esta entrando.",
                "estado": "critico"}
    if ultimos.count("D") >= 2 and "V" not in ultimos:
        return {"texto": "Sem vencer ha tres jogos. Talvez seja hora de mexer na tatica.",
                "estado": "atencao"}
    if ultimos == ["V", "V", "V"]:
        return {"texto": "Tres vitorias seguidas. O time achou o caminho.", "estado": "ok"}
    return None


def _resultados(G):
    c = G["clubes"][G["clube"]]
    placares = []
    for r in eng.resultados_da_semana(G):
        em_casa = r["casa"] == c["id"]
        gm, gs = (r["gc"], r["gf"]) if em_casa else (r["gf"], r["gc"])
        adv = G["clubes"].get(r["fora"] if em_casa else r["casa"])
        placares.append({"eu": gm, "ele": gs, "em_casa": em_casa,
                         "adversario": _corta(adv["nome"] if adv else "-", 20),
                         "estado": "ok" if gm > gs else ("atencao" if gm == gs else "critico")})
    forma = [{"letra": l, "descricao": t} for l, t in eng.forma_recente(G, 5)]
    return {"placares": placares, "forma": forma, "alerta": _alerta_de_fase(G),
            "partidas": [partida(reg) for reg in G.get("historico_meus", [])]}


ESTATISTICAS = (("chutes", "Chutes"), ("no_gol", "No gol"), ("posse", "Posse (%)"),
                ("escanteios", "Escanteios"), ("faltas", "Faltas"), ("defesas", "Defesas"))


def partida(reg):
    """Um registro de eng.historico_meus no formato do cartao e do detalhe.

    Mandante sempre primeiro (lado 0); `eu` diz de que lado o meu clube esta.
    """
    eu = reg["eu"]
    gm, gs = (reg["gc"], reg["gf"]) if eu == 0 else (reg["gf"], reg["gc"])
    resultado = "V" if gm > gs else ("E" if gm == gs else "D")
    times = [reg["casa_nome"], reg["fora_nome"]]
    st = reg.get("stats") or {}
    notas = [[], []]
    for lado, _pid, nome, vaga, nota in reg["notas"]:
        notas[lado].append({"vaga": vaga, "nome": nome, "nota": nota})
    melhor = None
    if reg.get("melhor"):
        m = reg["melhor"]
        melhor = {"nome": m["nome"], "vaga": m["vaga"], "nota": m["nota"], "time": times[m["lado"]]}
    decisao = None
    if reg.get("agregado"):
        a, ga, gb, b = reg["agregado"]
        decisao = "Agregado: %s %d x %d %s" % (a, ga, gb, b)
    if reg.get("penaltis"):
        decisao = (decisao + " · " if decisao else "") + "nos penaltis avanca o %s" % reg["penaltis"]
    return {
        "chave": "%d-%s-%d-%d" % (reg["semana_abs"], reg["comp"], reg["casa"], reg["fora"]),
        "comp": reg["comp_nome"], "rodada": reg["rodada"],
        "resultado": resultado,
        "estado": {"V": "ok", "E": "atencao", "D": "critico"}[resultado],
        "eu": eu, "times": times, "placar": [reg["gc"], reg["gf"]],
        "gols": [{"minuto": m, "lado": l, "autor": autor, "assist": ass}
                 for m, l, autor, ass in reg["gols"]],
        "cartoes": [{"minuto": m, "lado": l, "tipo": t, "nome": n} for m, l, t, n in reg["cartoes"]],
        "instrucoes": [{"minuto": m, "lado": l, "tatica": t, "motivo": mot}
                       for m, l, t, mot in reg.get("instrucoes", [])],
        "posse": st.get("posse", [50, 50]), "chutes": st.get("chutes", [0, 0]),
        "no_gol": st.get("no_gol", [0, 0]),
        "melhor": melhor,
        "detalhes": {
            "notas": notas,
            "subs": [{"minuto": m, "lado": l, "entra": e, "sai": sai} for m, l, e, sai in reg["subs"]],
            "lesoes": [{"minuto": m, "lado": l, "nome": n} for m, l, n in reg["lesoes"]],
            "estatisticas": [{"rotulo": rot, "valores": st[k]} for k, rot in ESTATISTICAS if k in st],
            "publico": ("publico %s, renda %s" % (milhar(reg["pub"]), eng.din(reg["renda"]))
                        if reg.get("pub") else None),
            "decisao": decisao,
        },
    }


def _noticias(G, quantas=6):
    """Os lances da rodada primeiro, a noticia do clube depois.

    O motor so publica noticia em evento forte e muita semana passa sem
    nenhuma: sem os gols e as baixas, o bloco vivia vazio.
    """
    c = G["clubes"][G["clube"]]
    jogs = G["jogadores"]
    itens = []
    for r in eng.resultados_da_semana(G):
        em_casa = r["casa"] == c["id"]
        for minuto, lado, tipo, pid, ass in r.get("eventos", []):
            j = jogs.get(pid)
            if not j:
                continue
            meu = (lado == 0) == em_casa
            marca = "%d min" % minuto
            if tipo == "gol" and meu:
                extra = ""
                if ass and ass in jogs:
                    extra = " (assist. %s)" % _corta(jogs[ass]["nome"], 16)
                itens.append({"texto": "Gol de %s%s" % (j["nome"], extra),
                              "estado": "ok", "quando": marca})
            elif j["clube"] == c["id"] and tipo == "lesao":
                itens.append({"texto": "Lesao: %s, %s fora" % (j["nome"], eng.plural(j["lesao"], "semana")),
                              "estado": "critico", "quando": marca})
            elif j["clube"] == c["id"] and tipo == "vermelho":
                itens.append({"texto": "Cartao vermelho: %s" % j["nome"],
                              "estado": "critico", "quando": marca})
    for n in reversed(G["noticias"][-quantas:]):
        limpo = LIMPA_COR.sub("", n).strip().replace("\n", " ")
        itens.append({"texto": _corta(limpo, 150), "estado": "neutro",
                      "quando": "semana %d" % G["semana"]})
    return itens[:quantas]


def painel():
    G = SESSAO.exigir()
    d = SESSAO.diagnostico(recarregar=True)
    xi, vazias = _xi(G, d)
    return {
        "cabecalho": cabecalho(G),
        "prontidao": _prontidao(G, d),
        "proximo": _proximo(G, d),
        "escalacao": {"formacao": d["formacao"], "tatica": d["tatica"], "auto": d["auto"],
                      "estado": d["estado"], "jogadores": xi, "vagas_abertas": vazias},
        "objetivo": _objetivo(G),
        "tabela": _tabela(G),
        "destaques": _destaques(G),
        "resultados": _resultados(G),
        "noticias": _noticias(G),
        "contratos": _contratos_acabando(G),
        "propostas_emprego": _propostas_emprego(G),
        "patrocinio_vago": ([eng.NOME_ESPACO[e] for e in eng.espacos_vagos(G, G["clubes"][G["clube"]])]
                            or None),
        "mundo": _mundo(G, 6),
    }


def _propostas_emprego(G):
    """Clubes querendo o treinador: faixa no Painel com aceitar/recusar."""
    agora = eng.semana_absoluta(G)
    return [{"id": o["id"], "clube": o["clube"], "divisao": o["divisao"],
             "liga": eng.nome_da_liga(G, o["divisao"]), "reputacao": o["reputacao"],
             "semanas": max(0, o["vence"] - agora)}
            for o in eng.propostas_emprego(G)]


ROTULO_FEED = {"resultado": "Resultado", "tabela": "Classificacao", "copa": "Copa",
               "titulo": "Titulo", "mercado": "Mercado", "lesao": "Lesao",
               "abertura": "Brasileirao", "tecnico": "Treinador"}


def _mundo(G, quantas):
    """O feed do resto do futebol, do mais novo para o mais velho."""
    return [{"texto": f["texto"], "tipo": f["tipo"], "rotulo": ROTULO_FEED.get(f["tipo"], ""),
             "quando": ("semana %d" % f["s"]) if f["t"] == G["temporada"]
                       else "%d, semana %d" % (f["t"], f["s"])}
            for f in reversed(G.get("feed", [])[-quantas:])]


def _contratos_acabando(G):
    """Aviso do Painel: quem esta no ultimo ano (ou ja venceu) e sai de graca
    se ninguem renovar. Os ids vao para a fila de renovacao, um apos o outro."""
    c = G["clubes"][G["clube"]]
    js = [G["jogadores"][p] for p in c["elenco"]
          if not G["jogadores"][p].get("dono") and G["jogadores"][p]["contrato"] <= 1]
    if not js:
        return None
    js.sort(key=lambda j: (j["contrato"], -j["ovr"]))
    vencidos = sum(1 for j in js if j["contrato"] <= 0)
    return {"ids": [j["id"] for j in js],
            "jogadores": [{"id": j["id"], "nome": _corta(j["nome"], 22), "pos": j["pos"],
                           "ovr": j["ovr"], "vencido": j["contrato"] <= 0} for j in js[:5]],
            "extras": max(0, len(js) - 5),
            "estado": "critico" if vencidos else "atencao",
            "texto": (("1 contrato vencido: sai quando o ano comecar." if vencidos == 1 else
                       "%d contratos vencidos: saem quando o ano comecar." % vencidos) if vencidos
                      else ("1 jogador no ultimo ano de contrato: sai de graca no fim da temporada."
                            if len(js) == 1 else
                            "%d jogadores no ultimo ano de contrato: saem de graca no fim da "
                            "temporada." % len(js)))}


# ============================================================================
# DAQUI PARA BAIXO: as telas migradas depois do Painel.
#
# Todas seguem a mesma forma - devolvem o que a tela desenha e mais nada. O
# que for regra (quem pode subir da base, quanto custa a multa) continua sendo
# pergunta para o motor, nunca conta refeita aqui.
# ============================================================================

def _limpo(txt):
    return LIMPA_COR.sub("", txt or "").strip()


def _tag_ovr(ovr):
    """A mesma escada de cor do tkinter: so o extremo merece destaque."""
    if ovr >= 80:
        return "top"
    if ovr >= 70:
        return "ok"
    if ovr < 55:
        return "fraco"
    return ""


# --------------------------------------------------------------------- elenco
def _linha_elenco(G, j):
    sit = _limpo(eng.situacao(G, j))
    if not sit and j["listado"]:
        sit = "a venda por %s" % eng.din(j["listado"])
    ultimo_ano = j["contrato"] <= 1 and not j.get("dono")
    estado = "critico" if (j["lesao"] or j["suspensao"]) else ""
    return {
        "id": j["id"], "pos": j["pos"], "nome": j["nome"], "idade": j["idade"],
        "ovr": j["ovr"], "cond": j["cond"],
        "salario": eng.din(j["salario"]), "salario_num": int(j["salario"]),
        "valor": eng.din(j["valor"]), "valor_num": int(j["valor"]),
        "contrato": j["contrato"], "ultimo_ano": ultimo_ano,
        "situacao": sit, "listado": bool(j["listado"]),
        "emprestado_aqui": bool(j.get("dono")),
        "estado": estado, "tag": _tag_ovr(j["ovr"]),
    }


def elenco():
    G = SESSAO.exigir()
    c = G["clubes"][G["clube"]]
    jogs = G["jogadores"]
    ordem = sorted(c["elenco"], key=lambda p: (eng.POS.index(jogs[p]["pos"]), -jogs[p]["ovr"]))
    na_vitrine = sum(1 for p in c["elenco"] if jogs[p]["listado"])
    acabando = sum(1 for p in c["elenco"]
                   if jogs[p]["contrato"] <= 1 and not jogs[p].get("dono"))

    # quem eu cedi sai do elenco e sumiria da tela sem esta segunda lista
    cedidos = []
    for j in eng.cedidos(G, c):
        cedidos.append({
            "id": j["id"], "nome": j["nome"], "pos": j["pos"], "ovr": j["ovr"],
            "clube": G["clubes"][j["clube"]]["nome"],
            "emp_pct": j["emp_pct"],
            "custo": eng.din(j["salario"] * (100 - j["emp_pct"]) // 100),
            "opcao": eng.din(j["emp_opcao"]) if j.get("emp_opcao") else None,
            "tag": _tag_ovr(j["ovr"]),
        })

    return {
        "cabecalho": cabecalho(G),
        "titulo": "Elenco",
        "subtitulo": "Duplo clique (ou Enter) na linha abre a ficha completa do jogador.",
        "mercado_aberto": eng.mercado_aberto(G),
        "metricas": [
            {"valor": len(c["elenco"]), "nome": "jogadores"},
            {"valor": "%.1f" % eng.media_elenco(G, c), "nome": "media de overall"},
            {"valor": eng.din(sum(G["jogadores"][p]["valor"] for p in c["elenco"]
                                  if not G["jogadores"][p].get("dono"))), "nome": "valor do elenco"},
            {"valor": na_vitrine, "nome": "na vitrine",
             "estado": "atencao" if na_vitrine else None},
            {"valor": acabando, "nome": "ultimo ano",
             "estado": "critico" if acabando else None},
        ],
        "jogadores": [_linha_elenco(G, jogs[p]) for p in ordem],
        "cedidos": cedidos,
    }


# ----------------------------------------------------------------------- base
def base():
    G = SESSAO.exigir()
    c = G["clubes"][G["clube"]]
    garotos = eng.elenco_base(G, c)
    foco = eng.foco_treino(G, c)
    prontos = sum(1 for j in garotos if eng.pronto_para_subir(G, c, j))

    linhas = []
    for j in garotos:
        if j["idade"] > eng.IDADE_BASE_MAX:
            sit, estado = "aos %d sobe ou sai" % (eng.IDADE_BASE_MAX + 1), "critico"
        elif eng.pronto_para_subir(G, c, j):
            sit, estado = "pronto para subir", "ok"
        elif j["idade"] >= eng.IDADE_BASE_MAX:
            sit, estado = "ultimo ano na base", "atencao"
        else:
            sit, estado = "ainda cru", ""
        linhas.append({
            "id": j["id"], "pos": j["pos"], "nome": j["nome"], "idade": j["idade"],
            "ovr": j["ovr"], "teto": eng.scout(G, j), "em_foco": j["id"] in foco,
            "situacao": sit, "estado": estado, "tag": _tag_ovr(j["ovr"]),
            "obs": int(j.get("obs", 0)),
        })

    return {
        "cabecalho": cabecalho(G),
        "titulo": "Base",
        "subtitulo": ("Formar em casa e o jeito mais barato de melhorar o time. "
                      "Aos %d anos o garoto sobe ou e liberado." % (eng.IDADE_BASE_MAX + 1)),
        "metricas": [
            {"valor": c["base"], "nome": "nivel da academia"},
            {"valor": "%d/%d" % (len(garotos), eng.vagas_base(c)), "nome": "vagas"},
            {"valor": prontos, "nome": "prontos p/ subir", "estado": "ok" if prontos else None},
            {"valor": eng.din(eng.custo_base(G, c)), "nome": "bolsa por semana"},
        ],
        "garotos": linhas,
        "elenco_profissional": len(c["elenco"]),
        "teto_profissional": eng.LIMITE_ELENCO,
        "peneira": _peneira(G, c),
        "candidatos": [{"cid": k["cid"], "nome": k["nome"], "pos": k["pos"], "idade": k["idade"],
                        "ovr": k["ovr"], "faixa": eng.faixa_candidato(G, c, k), "regiao": k["regiao"],
                        "semanas": max(0, k["vence"] - eng.semana_absoluta(G))}
                       for k in eng.candidatos_base(G, c)],
        "vagas_livres": max(0, eng.vagas_base(c) - len(garotos)),
        "revelados": _revelados(G, c),
    }


def _peneira(G, c):
    pen = eng.peneira(c)
    regioes = [{"id": k, "nome": r["nome"], "custo": eng.din(r["custo"]),
                "vies": ", ".join(r["vies"]),
                "talento": ("alto" if r["talento"] >= 1.0 else
                            "bom" if r["talento"] >= 0.9 else "medio")}
               for k, r in eng.REGIOES_PENEIRA.items()]
    atual = None
    if pen:
        r = eng.REGIOES_PENEIRA[pen["regiao"]]
        faltam = eng.PENEIRA_A_CADA - pen.get("semanas", 0) % eng.PENEIRA_A_CADA
        atual = {"regiao": pen["regiao"], "nome": r["nome"], "foco": pen.get("foco"),
                 "custo": eng.din(r["custo"]), "proxima": faltam}
    return {"atual": atual, "regioes": regioes, "posicoes": list(eng.POS),
            "a_cada": eng.PENEIRA_A_CADA, "vale": eng.CANDIDATO_VALE}


def _revelados(G, c):
    """Quem a academia formou: como subiu e como esta hoje."""
    fora = []
    for r in reversed(c.get("revelados", [])):
        j = G["jogadores"].get(r["id"])
        if j and j.get("clube") in G["clubes"]:
            onde = G["clubes"][j["clube"]]["nome"]
        elif j:
            onde = "sem clube"
        else:
            onde = "parou de jogar"
        fora.append({"nome": r["nome"], "pos": r["pos"], "temporada": r["temporada"],
                     "ovr_subida": r["ovr"], "ovr_hoje": j["ovr"] if j else None, "onde": onde,
                     "em_casa": bool(j and j.get("clube") == c["id"])})
    return fora


# --------------------------------------------------------------------- tabela
def _torneios(G):
    """Os quatro pontos fixos e os estaduais do ano, no mesmo seletor."""
    out = [{"id": "liga:" + d, "nome": "Serie " + d} for d in "ABCD"]
    out += [{"id": "liga:" + k, "nome": l["nome"]} for k, l in eng.ligas_ext(G).items()]
    for chave, est in sorted(eng.estaduais(G).items(),
                             key=lambda kv: (-len(kv[1]["times"]), kv[1]["nome"])):
        out.append({"id": "est:" + str(chave), "nome": est["nome"]})
    return out


def _liga_por_id(G, alvo):
    if alvo and alvo.startswith("est:"):
        return eng.estaduais(G).get(alvo[4:])
    if alvo and alvo.startswith("ext:") and alvo[4:] in G["ligas"]:
        return G["ligas"][alvo[4:]]
    div = (alvo or "")[5:] if alvo and alvo.startswith("liga:") else None
    if div not in G["ligas"]:
        div = G["clubes"][G["clube"]]["divisao"]
    return G["ligas"][div]


def _chave_do_meu_estadual(G):
    """estaduais() e um dicionario; meu_estadual() devolve o valor, sem a chave.
    Quem seleciona o torneio na tela precisa da chave, entao ela vem daqui."""
    meu = G.get("clube")
    for chave, est in eng.estaduais(G).items():
        if meu in est["times"]:
            return chave
    return None


def tabela(alvo=None):
    G = SESSAO.exigir()
    meu = G["clube"]
    if alvo is None:
        chave = _chave_do_meu_estadual(G) if G["fase"] == "estadual" else None
        alvo = ("est:" + str(chave) if chave
                else "liga:" + G["clubes"][meu]["divisao"])
    liga = _liga_por_id(G, alvo)
    if liga is None:
        return {"cabecalho": cabecalho(G), "titulo": "Classificacao", "torneios": _torneios(G),
                "alvo": alvo, "legenda": None, "linhas": [], "vazio": "Torneio nao encontrado."}

    e_estadual = "campeao" in liga
    if e_estadual:
        legenda = ("%s - campeao: %s" % (liga["nome"], G["clubes"][liga["campeao"]]["nome"])
                   if liga["campeao"] else
                   "%s - %s" % (liga["nome"], eng.etapa_estadual(liga)))
    else:
        legenda = "rodada %d de %d" % (liga["rodada"], len(liga["rodadas"]))

    # estadual com grupos: uma tabela por grupo, a posicao contada dentro dele
    blocos = [(None, liga)]
    if e_estadual and liga.get("grupos"):
        blocos = [("Grupo " + "ABCDEFGH"[g], eng.subtabela(liga, ids))
                  for g, ids in enumerate(liga["grupos"])]
    vagas = eng.vagas_por_grupo(liga) if e_estadual else 0

    linhas, grupos = [], []
    if liga["rodada"] > 0 or not e_estadual:
        for nome_grupo, bloco in blocos:
            ordem = eng.classificacao(G, bloco)
            do_grupo = []
            for i, cid in enumerate(ordem, 1):
                t = liga["tabela"][str(cid)]
                if e_estadual:
                    # verde: vai ao mata-mata (ou, em save antigo, e o lider)
                    zona = "alta" if i <= vagas else ""
                else:
                    # liga de fora nao tem rebaixamento no jogo: so o verde de cima
                    rebaixa = eng.tem_rebaixamento(liga.get("div"))
                    zona = "alta" if i <= 4 else ("baixa" if rebaixa and i > len(ordem) - 4 else "")
                do_grupo.append({"pos": i, "clube": G["clubes"][cid]["nome"], "p": t["p"],
                                 "j": t["j"], "v": t["v"], "e": t["e"], "d": t["d"],
                                 "gp": t["gp"], "gc": t["gc"], "sg": t["gp"] - t["gc"],
                                 "eu": cid == meu, "zona": zona, "grupo": nome_grupo,
                                 "zona_texto": rotulo_zona(zona, liga.get("div"), e_estadual)})
            linhas.extend(do_grupo)
            if nome_grupo:
                grupos.append({"nome": nome_grupo, "linhas": do_grupo})

    return {
        "cabecalho": cabecalho(G),
        "titulo": "Classificacao",
        "subtitulo": "as quatro series e os %d estaduais do ano" % len(eng.estaduais(G)),
        "torneios": _torneios(G),
        "alvo": alvo,
        "legenda": legenda,
        "vazio": None if linhas else "Este torneio ainda nao comecou.",
        "linhas": linhas,
        "grupos": grupos or None,
    }


# ---------------------------------------------------------------------- copas
def copas():
    G = SESSAO.exigir()
    itens = []
    for chave, cp in G["copas"].items():
        if cp["campeao"]:
            itens.append({"id": chave, "nome": cp["nome"], "encerrada": True,
                          "campeao": G["clubes"][cp["campeao"]]["nome"],
                          "fase": None, "clubes": 0, "proxima": None,
                          "vivo": cp["campeao"] == G["clube"]})
            continue
        n = len(cp["vivos"]) + len(cp.get("espera", []))
        itens.append({
            "id": chave, "nome": cp["nome"], "encerrada": False, "campeao": None,
            "fase": eng.fase_da_copa(cp), "clubes": n,
            "proxima": eng.proxima_semana_copa(cp),
            "vivo": eng.vivo_na_copa(cp, G["clube"]),
        })
    return {"cabecalho": cabecalho(G), "titulo": "Copas", "copas": itens}


# ------------------------------------------------------------------- financas
# o que cada linha do extrato quer dizer, em uma frase
DICA_EXTRATO = {
    "tv": "fixo toda semana: depende da serie e da reputacao do clube",
    "patrocinio": "contratos master e de uniforme, por semana (veja Patrocinio)",
    "patrocinio_bonus": "pago na virada a quem bateu a meta do contrato",
    "bilheteria": "jogos em casa: publico vezes ingresso (veja Estadio)",
    "premio_liga": "paga na virada do ano, pela posicao final",
    "premio_estadual": "so o campeao recebe",
    "premio_copa": "passar de fase, vice e campeao das copas",
    "operacao_jogo": "parte da renda de cada jogo em casa: seguranca, staff e arbitragem",
    "premio_grupo": "cada vitoria na fase de grupos do continental",
    "vendas": "passes vendidos",
    "emprestimos": "taxas de emprestimo pagas e recebidas",
    "folha": "salarios do elenco e bolsa da base",
    "estrutura": "CT, base, medico, manutencao do estadio e operacao do clube",
    "treino": "treino individual dos jogadores marcados",
    "peneira": "peneira regional da base",
    "compras": "passes comprados",
    "rescisoes": "multas de quem foi dispensado",
    "obras": "ampliacao do estadio",
    "infra": "niveis de CT, base e medico",
}


def _extrato(G, c):
    """O ano do clube em categorias; a soma fecha com o caixa (test_extrato)."""
    st = eng.stats_ano(G)
    ex = st.get("extrato", {})
    entradas, saidas = [], []
    for chave, rotulo in eng.EXTRATO:
        v = int(ex.get(chave, 0))
        if not v and chave not in ("tv", "patrocinio", "bilheteria", "folha", "estrutura"):
            continue
        linha = {"nome": rotulo, "valor": eng.din(v), "dica": DICA_EXTRATO.get(chave, ""),
                 "estado": "ok" if v > 0 else ("critico" if v < 0 else "")}
        (entradas if v > 0 or chave in ("tv", "patrocinio", "bilheteria") else saidas).append(linha)
    resultado = int(c["dinheiro"]) - int(st["caixa_ini"])
    # save de versao anterior: o ano comecou antes do extrato existir, e o que
    # andou antes fica numa linha propria em vez de a conta nao fechar
    antes = resultado - sum(int(v) for v in ex.values())
    if antes:
        (entradas if antes > 0 else saidas).append({
            "nome": "Antes do extrato", "valor": eng.din(antes),
            "dica": "movimentos deste ano feitos numa versao anterior do jogo, sem categoria",
            "estado": "ok" if antes > 0 else "critico"})
    return {"temporada": int(G["temporada"]), "entradas": entradas, "saidas": saidas,
            "caixa_ini": eng.din(st["caixa_ini"]), "caixa": eng.din(c["dinheiro"]),
            "resultado": eng.din(resultado), "estado": "ok" if resultado >= 0 else "critico"}


def _linha_patrocinio(G, oferta):
    return {"empresa": oferta["empresa"], "perfil": oferta["perfil"],
            "semanal": eng.din(oferta["semanal"]),
            "temporadas": eng.plural(oferta["temporadas"], "temporada"),
            "meta": eng.TEXTO_META.get(oferta["meta"], oferta["meta"]),
            "bonus": eng.din(oferta["bonus"]) if oferta.get("bonus") else None,
            # o que o contrato rende num ano sem bonus (50 semanas com jogo e sem)
            "ano": eng.din(oferta["semanal"] * 50)}


def patrocinio(G, c):
    """Contratos em vigor e, nos espacos vagos, as tres propostas do ano."""
    contratos = c.get("patrocinios") or {}
    vigentes, vagos = [], []
    for espaco in eng.ESPACOS_PATROCINIO:
        k = contratos.get(espaco)
        if k:
            vigentes.append(dict(_linha_patrocinio(G, k), espaco=espaco, nome=eng.NOME_ESPACO[espaco]))
        else:
            vagos.append({"espaco": espaco, "nome": eng.NOME_ESPACO[espaco],
                          "ofertas": [dict(_linha_patrocinio(G, o), indice=i)
                                      for i, o in enumerate(eng.ofertas_patrocinio(G, c, espaco))]})
    return {"contratos": vigentes, "vagos": vagos,
            "explica": ("Contrato longo protege de um ano ruim; o fixo alto rende mais agora. "
                        "A meta paga o bonus na virada. Sem escolha, a proposta equilibrada "
                        "assina quando a bola rolar.")}


def _premiacao_em_jogo(G, c):
    """Quanto o clube ainda pode ganhar: a liga pela posicao de hoje e as copas vivas."""
    itens = []
    liga = G["ligas"].get(c["divisao"])
    if liga and liga["rodada"] > 0:
        pos = eng.posicao_na_liga(G, c["id"])
        itens.append({"nome": "%s, terminando em %do" % (eng.nome_da_liga(G, c["divisao"]), pos),
                      "valor": eng.din(eng.premio_liga(c["divisao"], pos)),
                      "dica": "campeao leva %s; cada posicao abaixo paga menos"
                              % eng.din(eng.premio_liga(c["divisao"], 1))})
    elif liga:
        itens.append({"nome": "%s, campeao" % eng.nome_da_liga(G, c["divisao"]),
                      "valor": eng.din(eng.premio_liga(c["divisao"], 1)),
                      "dica": "a liga ainda nao comecou; paga pela posicao final"})
    for chave, cp in G["copas"].items():
        if cp.get("campeao") is None and c["id"] in cp.get("vivos", []) and eng.PREMIO_COPA.get(chave):
            vivos = len(cp.get("vivos", []))
            fase = eng.premio_fase_copa(chave, vivos) if vivos > 2 else 0
            itens.append({"nome": "%s, se for campeao" % cp["nome"],
                          "valor": eng.din(eng.PREMIO_COPA[chave]),
                          "dica": ("passar desta fase paga %s; o vice leva %s"
                                   % (eng.din(fase), eng.din(eng.PREMIO_COPA[chave] * eng.FRACAO_VICE)))
                                  if fase else "o vice leva %s" % eng.din(eng.PREMIO_COPA[chave] * eng.FRACAO_VICE)})
    est = eng.meu_estadual(G)
    if est and G.get("fase") == "estadual" and not est.get("campeao"):
        itens.append({"nome": "%s, se for campeao" % est["nome"],
                      "valor": eng.din(eng.premio_estadual(est) + c["reputacao"] * 22_000),
                      "dica": "so o campeao recebe"})
    return itens


def financas():
    G = SESSAO.exigir()
    c = G["clubes"][G["clube"]]
    rec = eng.receita_semanal(G, c)
    folha = eng.folha_semanal(G, c)
    est = eng.custo_estrutura(c)
    saldo = rec - folha - est

    maiores = []
    for j in sorted([G["jogadores"][p] for p in c["elenco"]], key=lambda x: -x["salario"])[:6]:
        maiores.append({"id": j["id"], "nome": j["nome"], "pos": j["pos"],
                        "salario": eng.din(j["salario"]), "valor": eng.din(j["valor"]),
                        "obs": ("emprestado, pagamos %d%%" % j["emp_pct"]) if j.get("dono") else ""})
    jogs = [G["jogadores"][p] for p in c["elenco"]]
    proprios = [j for j in jogs if not j.get("dono")]

    return {
        "cabecalho": cabecalho(G),
        "titulo": "Financas",
        "extrato": _extrato(G, c),
        "linhas": [
            {"nome": "Cotas de TV", "valor": eng.din(eng.tv_semanal(c)), "estado": ""},
            {"nome": "Patrocinio", "valor": eng.din(rec - eng.tv_semanal(c)), "estado": ""},
            {"nome": "Folha salarial", "valor": eng.din(-folha), "estado": "critico"},
            {"nome": "Estrutura e operacao", "valor": eng.din(-est), "estado": "critico"},
            {"nome": "Saldo fixo da semana", "valor": eng.din(saldo),
             "estado": "ok" if saldo >= 0 else "critico", "destaque": True},
        ],
        "premiacao": _premiacao_em_jogo(G, c),
        "patrocinio": patrocinio(G, c),
        "mensal": _verba_mensal(G, c),
        "elenco": {"valor": eng.din(sum(j["valor"] for j in proprios)),
                   "folha_mes": eng.din(folha * 4), "jogadores": len(jogs),
                   "emprestados": len(jogs) - len(proprios)},
        "maiores": maiores,
    }


def _verba_mensal(G, c):
    """O mes do clube e, dele, o que sobra de verba para contratar."""
    orc = eng.orcamento_mensal(G, c)
    reserva = eng.reserva_custos(G, c)
    verba = eng.verba_contratacao(G, c)
    return {
        "linhas": [
            {"nome": "TV e patrocinio", "valor": eng.din(orc["tv"]), "estado": ""},
            {"nome": "Bilheteria (estimada, 2 jogos em casa)", "valor": eng.din(orc["bilheteria"]),
             "estado": ""},
            {"nome": "Folha salarial", "valor": eng.din(-orc["folha"]), "estado": "critico"},
            {"nome": "Estrutura e operacao", "valor": eng.din(-orc["estrutura"]), "estado": "critico"},
            {"nome": "Saldo do mes", "valor": eng.din(orc["saldo"]),
             "estado": "ok" if orc["saldo"] >= 0 else "critico", "destaque": True},
        ],
        "caixa": eng.din(c["dinheiro"]),
        "reserva": eng.din(reserva),
        "meses": eng.RESERVA_MESES,
        "verba": eng.din(verba),
        "estado": "ok" if verba > 0 else "critico",
        "explica": ("Do caixa, %s ficam guardados para %d meses de folha e custos - sem contar "
                    "receita nenhuma. O resto, %s, e a verba para contratar: gastando so ela, "
                    "a folha esta sempre paga. Salario de reforco entra na reserva antes do passe."
                    % (eng.din(reserva), eng.RESERVA_MESES, eng.din(verba))),
        "queima": (None if orc["saldo"] >= 0 else
                   "O caixa ja esta negativo e o mes fecha no vermelho em %s: venda alguem ou "
                   "corte folha." % eng.din(-orc["saldo"]) if c["dinheiro"] <= 0 else
                   "O mes fecha no vermelho em %s: sem vender ou cortar folha, o caixa dura "
                   "cerca de %d meses." % (eng.din(-orc["saldo"]),
                                           c["dinheiro"] // max(1, -orc["saldo"]))),
    }


# -------------------------------------------------------------- infraestrutura
ITENS_INFRA = [
    ("ct", "Centro de treinamento", "evolucao dos jogadores"),
    ("base", "Categorias de base", "qualidade das crias no fim do ano"),
    ("medico", "Departamento medico", "menos lesao e recuperacao mais rapida"),
]


def custo_infra(nivel):
    """A conta do proximo nivel. Uma funcao so, porque a tela mostra o preco e
    a rota cobra por ele - se divergissem, o usuario pagaria outro valor."""
    return int((nivel + 1) ** 2 * 900_000)


def infra():
    G = SESSAO.exigir()
    c = G["clubes"][G["clube"]]
    itens = []
    for chave, nome, desc in ITENS_INFRA:
        nivel = c[chave]
        custo = custo_infra(nivel) if nivel < 10 else None
        itens.append({"id": chave, "nome": nome, "descricao": desc, "nivel": nivel,
                      "maximo": 10, "custo": eng.din(custo) if custo else None,
                      "custo_num": custo,
                      "pode_pagar": bool(custo and custo <= c["dinheiro"])})
    return {"cabecalho": cabecalho(G), "titulo": "Infraestrutura",
            "subtitulo": "caixa %s" % eng.din(c["dinheiro"]), "itens": itens}


# ------------------------------------------------------------------- noticias
def noticias():
    G = SESSAO.exigir()
    itens = []
    for n in reversed(G["noticias"][-25:]):
        itens.append({"texto": _limpo(n).replace("\n", " ")})
    return {"cabecalho": cabecalho(G), "titulo": "Noticias",
            "subtitulo": "o seu clube e o resto do futebol",
            "itens": itens, "mundo": _mundo(G, 80)}


# ------------------------------------------------------------------ carreira
SAIDAS = {"demitido": "demitido", "pediu demissao": "pediu demissao",
          "encerrou a carreira": "encerrou a carreira"}


def carreira():
    """A sala de trofeus: o treinador, as tacas somadas e cada passagem."""
    G = SESSAO.exigir()
    passagens = eng.carreira(G)
    rep = eng.rep_tecnico(G)
    trofeus = {}
    for p in passagens:
        for t in p["titulos"]:
            item = trofeus.setdefault(t["nome"], {"nome": t["nome"], "qtd": 0, "anos": []})
            item["qtd"] += 1
            item["anos"].append("%d (%s)" % (t["temporada"], p["clube"]))
    ordem = list(eng.PESO_TITULO)
    trofeus = sorted(trofeus.values(),
                     key=lambda t: (ordem.index(t["nome"]) if t["nome"] in ordem else 99, -t["qtd"]))
    tot = {k: sum(p[k] for p in passagens) for k in ("j", "v", "e", "d", "gp", "gc")}
    anos = sorted({a for p in passagens
                   for a in range(p["de"], (p["ate"] if p["ate"] is not None else G["temporada"]) + 1)})
    op = eng.opcoes_carreira(G)
    linhas = []
    for p in reversed(passagens):
        aprov = round(100.0 * (3 * p["v"] + p["e"]) / (3 * p["j"])) if p["j"] else None
        linhas.append({
            "clube": p["clube"], "divisao": p["divisao"],
            "liga": eng.nome_da_liga(G, p["divisao"]),
            "periodo": "%d - %s" % (p["de"], p["ate"] if p["ate"] is not None else "hoje"),
            "atual": p["ate"] is None,
            "saida": p["saida"],
            "j": p["j"], "v": p["v"], "e": p["e"], "d": p["d"], "gp": p["gp"], "gc": p["gc"],
            "aproveitamento": aprov,
            "titulos": ["%s %d" % (t["nome"], t["temporada"]) for t in p["titulos"]],
            "marcos": ["%d: %s" % (m["temporada"], m["texto"]) for m in reversed(p["marcos"])],
            "parcial": bool(p.get("parcial")),
        })
    return {
        "cabecalho": cabecalho(G), "titulo": "Carreira",
        "subtitulo": "sala de trofeus e historico do treinador",
        "tecnico": {"nome": G.get("tecnico") or "Tecnico", "reputacao": rep,
                    "rotulo": _rotulo_rep(rep)},
        "totais": {"clubes": len({p["clube_id"] for p in passagens}), "temporadas": len(anos),
                   "titulos": sum(t["qtd"] for t in trofeus), **tot},
        "trofeus": trofeus,
        "passagens": linhas,
        "opcoes": {"dificuldade": eng.DIFICULDADES[op["dificuldade"]]["nome"],
                   "sem_demissao": op["sem_demissao"], "investidor": op["investidor"]},
        "propostas": _propostas_emprego(G),
        "pode_pedir_demissao": not SESSAO.pendencia,
    }


def _rotulo_rep(rep):
    if rep >= 85:
        return "lenda do futebol brasileiro"
    if rep >= 70:
        return "nome de Serie A, disputado pelos grandes"
    if rep >= 55:
        return "respeitado, com mercado na Serie A"
    if rep >= 40:
        return "em ascensao, conhecido na Serie B"
    return "desconhecido fora do proprio clube"


# --------------------------------------------------------------------- ficha
def ficha(pid):
    """A ficha do jogador, em campos e nao em texto.

    O motor tem ficha_completa(), mas ela imprime um bloco de terminal com
    barras de caractere. Aqui os mesmos julgamentos vem soltos, para a tela
    desenhar barra de verdade.
    """
    G = SESSAO.exigir()
    j = G["jogadores"].get(int(pid))
    if j is None:
        raise KeyError("jogador %s nao existe" % pid)

    papel = {"GOL": "embaixo das traves", "ZAG": "na zaga", "LAT": "na lateral",
             "VOL": "na primeira linha de meio", "MEI": "na criacao",
             "ATA": "no ataque"}[j["pos"]]
    if j["ovr"] >= 78:
        nivel = "peca de Serie A, daquelas que decidem jogo"
    elif j["ovr"] >= 70:
        nivel = "titular tranquilo em qualquer time de Serie A ou B"
    elif j["ovr"] >= 62:
        nivel = "titular de Serie B, rodagem boa"
    elif j["ovr"] >= 52:
        nivel = "nivel de Serie C, quebra galho mais acima"
    else:
        nivel = "ainda cru, coisa de Serie D ou base"
    if j["idade"] <= 21 and j["pot"] - j["ovr"] >= 8:
        fase = "garoto com espaco pra crescer bastante"
    elif j["idade"] <= 28:
        fase = "esta no auge ou chegando nele"
    elif j["idade"] <= 32:
        fase = "veterano, tende a cair de rendimento em breve"
    else:
        fase = "fim de carreira, o overall cai todo ano"

    notas = [nivel, fase]
    revisao = eng.leitura_teto(j)
    if revisao:
        notas.append(_limpo(revisao))
    if eng.da_base(j):
        notas.append("Categoria de base: nao joga e nao entra no mercado ate subir.")
    if eng.em_foco(G, j):
        notas.append("Em treino individual: evolui 50% mais rapido.")

    clube = G["clubes"].get(j["clube"])
    return {
        "id": j["id"], "nome": j["nome"], "pos": j["pos"],
        "posicao_nome": eng.NOME_POS[j["pos"]], "idade": j["idade"],
        "clube": clube["nome"] if clube else "sem clube",
        "ovr": j["ovr"], "papel": papel,
        "olheiro": _limpo(eng.rotulo_scout(G, j)),
        "notas": notas,
        "situacao": _limpo(eng.situacao(G, j)),
        "barras": [
            {"nome": "Condicao", "valor": j["cond"]},
            {"nome": "Forma", "valor": j["forma"]},
            {"nome": "Moral", "valor": j["moral"]},
        ],
        "temporada": {"j": j["j"], "g": j["g"], "a": j["a"], "ca": j["ca"], "cv": j["cv"]},
        "carreira": {"j": j["car_j"], "g": j["car_g"], "tit": j["car_tit"]},
        "contrato": {"anos": j["contrato"], "salario": eng.din(j["salario"]),
                     "valor": eng.din(j["valor"]),
                     "emprestado_aqui": bool(j.get("dono")),
                     "emp_pct": j.get("emp_pct", 100)},
    }


# ------------------------------------------------------------------ escalacao
def _linha_banco(G, j):
    apto = eng.disponivel(G, j["id"])
    return {
        "id": j["id"], "pos": j["pos"], "nome": j["nome"], "ovr": j["ovr"],
        "cond": j["cond"], "situacao": _limpo(eng.situacao(G, j)),
        "disponivel": apto, "tag": _tag_ovr(j["ovr"]),
    }


# Trocar dois titulares de vagas diferentes precisa do motor: quem decide a
# vaga de cada um e eng.atribuir_vagas, uma atribuicao otima que ignora a
# ordem do XI. Quando o motor ganhar eng.vagas_manuais(c) (e passar o mapa para
# atribuir_vagas), a troca liga sozinha, sem mexer na API nem na tela.
MOTIVO_SEM_VAGA_FIXA = ("Titulares de vagas diferentes ainda nao trocam de lugar: o motor escolhe "
                        "a vaga de cada um sozinho. Na mesma vaga, eles trocam de lado.")


def motor_fixa_vagas():
    return callable(getattr(eng, "vagas_manuais", None))


GRUPOS_FORMACAO = [("4", "Linha de 4"), ("3", "Linha de 3"), ("5", "Linha de 5")]


def _item_formacao(nome, cont):
    return {"id": nome, "rotulo": nome, "contagem": eng.normalizar_contagem(cont),
            "sem_laterais": cont.get("LAT", 0) == 0}


def formacoes_agrupadas():
    """O select agrupado pela linha de defesa, que e como o tecnico pensa."""
    grupos = []
    for prefixo, nome in GRUPOS_FORMACAO:
        itens = [_item_formacao(f, cont) for f, cont in eng.FORMACOES.items()
                 if f.startswith(prefixo)]
        if itens:
            grupos.append({"nome": nome, "itens": itens})
    return grupos


def simular_esquema(G, c, formacao, custom=None, manter=None):
    """Como o time ficaria com outra formacao, sem gravar nada.

    manter = os 11 atuais (modo manual: so as vagas mudam). Sem ele, a maquina
    monta o melhor time para o esquema. O clube e restaurado antes de voltar:
    serve a previa do editor e a sugestao da faixa.
    """
    guardado = (c.get("formacao"), c.get("formacao_custom"))
    try:
        c["formacao"] = formacao
        if custom is not None:
            c["formacao_custom"] = eng.normalizar_contagem(custom)
        form = eng.formacao_de(c)
        esc = list(manter) if manter else eng.montar_escalacao(G, c)
        ataque, defesa = eng.forcas_de(G, c, esc)
        vagas = eng.atribuir_vagas(G, esc, form)
        rotulo = eng.rotulo_formacao(c)
    finally:
        c["formacao"], c["formacao_custom"] = guardado
        if guardado[1] is None:
            c.pop("formacao_custom", None)
    jogs = G["jogadores"]
    improvisados = [(p, v) for p, v in vagas if v != jogs[p]["pos"]]
    graves = [(p, v) for p, v in improvisados if eng.AFINIDADE[jogs[p]["pos"]][v] < 0.60]
    return {"ataque": ataque, "defesa": defesa, "vagas": vagas, "rotulo": rotulo,
            "improvisados": len(improvisados), "graves": len(graves)}


def _saida_estrutural(G, c, d):
    """Quando o elenco nao tem a posicao que a formacao pede: a melhor formacao
    pronta que resolve, com os numeros ja calculados. So aparece se for melhor
    que o time de agora - sugerir pior seria pior do que nao sugerir."""
    if not d.get("estrutural"):
        return None
    vaga = (d["graves"] or d["improvisados"])[0][1]
    atual = d["ataque"] + d["defesa"]
    melhor = None
    for nome in eng.FORMACOES:
        if nome == c.get("formacao"):
            continue
        sim = simular_esquema(G, c, nome)
        soma = sim["ataque"] + sim["defesa"]
        # a saida tem que tirar o improviso, nao so trocar de lugar
        if (sim["improvisados"] < len(d["improvisados"]) and sim["graves"] == 0
                and soma > atual and (melhor is None or soma > melhor[0])):
            melhor = (soma, nome, sim)
    alternativa = None
    if melhor:
        _, nome, sim = melhor
        alternativa = {"formacao": nome, "ataque": round(sim["ataque"], 1),
                       "defesa": round(sim["defesa"], 1),
                       "sem_laterais": eng.FORMACOES[nome].get("LAT", 0) == 0}
    return {"vaga": vaga, "plural": eng.PLURAL_POS[vaga], "alternativa": alternativa,
            "mercado": eng.mercado_aberto(G)}


def escalacao():
    """O XI que entra em campo e o banco, com o plano de jogo junto.

    O XI vem do mesmo diagnostico do Painel: se a escalacao dissesse uma coisa
    e o Painel outra, o usuario nao saberia em qual acreditar.
    """
    G = SESSAO.exigir()
    c = G["clubes"][G["clube"]]
    d = SESSAO.diagnostico(recarregar=True)
    xi, vazias = _xi(G, d)
    titulares = set(d["escalacao"])
    jogs = G["jogadores"]

    resto = [p for p in c["elenco"] if p not in titulares]
    resto.sort(key=lambda p: (not eng.disponivel(G, p), eng.POS.index(jogs[p]["pos"]),
                              -eng.rendimento(jogs[p])))

    plano = eng.plano_de(c)
    ef = eng.efeitos_plano(c)
    eixos = []
    for eixo, tabela in eng.EIXOS_PLANO:
        eixos.append({"id": eixo, "nome": eixo.capitalize(), "valor": plano[eixo],
                      "opcoes": [{"id": k, "desc": v["desc"]} for k, v in tabela.items()]})

    return {
        "cabecalho": cabecalho(G),
        "titulo": "Escalacao",
        "subtitulo": "Clique em dois jogadores para trocar: titular e reserva, ou dois titulares.",
        # formacao e mentalidade ja aparecem nos proprios controles
        "metricas": [
            {"valor": "%.1f" % d["ataque"], "nome": "ataque"},
            {"valor": "%.1f" % d["defesa"], "nome": "defesa"},
        ],
        "prontidao": {"estado": d["estado"], "titulo": d["titulo"], "detalhe": d["detalhe"],
                      "estrutural": _saida_estrutural(G, c, d)},
        "auto": d["auto"],
        "formacao": c["formacao"],
        "formacao_rotulo": eng.rotulo_formacao(c),
        "contagem": eng.normalizar_contagem(eng.formacao_de(c)),
        "formacoes": formacoes_agrupadas(),
        "personalizada": ({"rotulo": "Personalizada (%s)" % eng.nome_da_contagem(c["formacao_custom"]),
                           "contagem": eng.normalizar_contagem(c["formacao_custom"])}
                          if eng.contagem_valida(c.get("formacao_custom") or {})[0] else None),
        "limites": {p: {"min": lo, "max": hi} for p, (lo, hi) in eng.LIMITES_FORMACAO.items()},
        "pode_desfazer": SESSAO.desfazer_esquema is not None,
        "troca_entre_vagas": motor_fixa_vagas(),
        "tatica": c["tatica"],
        "taticas": list(eng.TATICAS),
        "plano": {
            "eixos": eixos,
            "padrao": plano == eng.PLANO_PADRAO,
            "efeitos": [
                {"nome": "posse", "valor": "%+.0f" % (ef["posse"] * 100)},
                {"nome": "volume de chances", "valor": "x%.2f" % ef["volume"]},
                {"nome": "qualidade", "valor": "x%.2f" % ef["qualidade"]},
                {"nome": "entrega", "valor": "x%.2f" % ef["concede"]},
                {"nome": "fadiga", "valor": "%+.0f" % ef["fadiga"]},
            ],
        },
        "condicionais": {
            "minutos": list(eng.MINUTOS_CONDICIONAL),
            "regras": [{"condicao": cond, "rotulo": "Se estiver %s" % cond,
                        "minuto": r["minuto"] if r else None, "tatica": r["tatica"] if r else None}
                       for cond, r in eng.condicionais_de(c).items()],
        },
        "titulares": xi,
        "nova_vaga": SESSAO.nova_vaga,
        "vagas_abertas": vazias,
        "banco": [_linha_banco(G, jogs[p]) for p in resto],
    }


# ---------------------------------------------------------------------- treino
def _efeitos_regime(r):
    """Evolucao, fisico e lesao com o sinal ja julgado: lesao subir e ruim."""
    fora = []
    for nome, valor, bom_se_positivo, sufixo in (
            ("evolucao", round((r["evo"] - 1) * 100), True, "%"),
            ("fisico", r["cond"], True, ""),
            ("lesao", round((r["lesao"] - 1) * 100), False, "%")):
        if valor == 0:
            estado = "neutro"
        elif (valor > 0) == bom_se_positivo:
            estado = "ok"
        else:
            estado = "critico"
        fora.append({"nome": nome, "texto": "%+d%s" % (valor, sufixo), "estado": estado})
    return fora


def custo_por_nome(c):
    return 26_000 + 3_000 * int(c.get("ct", 3))


def treino():
    G = SESSAO.exigir()
    c = G["clubes"][G["clube"]]
    foco = eng.foco_treino(G, c)
    vagas = eng.vagas_treino(c)
    atual = c.get("treino") or eng.REGIME_PADRAO

    regimes = [{"nome": nome, "desc": r["desc"], "ativo": nome == atual,
                "efeitos": _efeitos_regime(r)}
               for nome, r in eng.REGIMES_TREINO.items()]

    todos = [G["jogadores"][p] for p in c["elenco"]] + eng.elenco_base(G, c)
    todos.sort(key=lambda j: (j["id"] not in foco, -(j["pot"] - j["ovr"]), j["idade"]))
    linhas = []
    for j in todos:
        taxa = eng.taxa_evolucao(G, j)
        margem = j["pot"] - j["ovr"]
        if j["id"] in foco:
            tag = "ok"
        elif taxa < 0:
            tag = "critico"
        elif margem <= 0:
            tag = "fraco"
        else:
            tag = ""
        linhas.append({
            "id": j["id"], "pos": j["pos"], "nome": j["nome"], "base": eng.da_base(j),
            "idade": j["idade"], "ovr": j["ovr"], "margem": margem,
            "evo": "%+.2f" % taxa, "em_foco": j["id"] in foco,
            "emprestado_aqui": bool(j.get("dono")), "tag": tag,
        })

    return {
        "cabecalho": cabecalho(G),
        "titulo": "Treino",
        "subtitulo": "Evoluir quem voce ja tem, sem gastar passe. Todo regime tem preco.",
        "metricas": [
            {"valor": c["ct"], "nome": "nivel do CT"},
            {"valor": "%d/%d" % (len(foco), vagas), "nome": "em treino individual",
             "estado": "atencao" if len(foco) >= vagas else None},
            {"valor": eng.din(eng.custo_treino(c)), "nome": "custo por semana"},
        ],
        "regimes": regimes,
        "custo_por_nome": eng.din(custo_por_nome(c)),
        "vagas": vagas,
        "em_foco": len(foco),
        "jogadores": linhas,
    }


# --------------------------------------------------------------------- estadio
PRECO_MIN, PRECO_MAX = 5, 300
CUSTO_LUGAR = 3500
LUGARES_MIN, LUGARES_MAX = 1000, 40000


def semanas_de_obra(lugares):
    """Mesma conta da janela tkinter e da IA: uma semana a cada 1.500 lugares."""
    return max(2, lugares // 1500)


def milhar(n):
    return f"{int(n):,}".replace(",", ".")


def estadio():
    G = SESSAO.exigir()
    c = G["clubes"][G["clube"]]
    obra = None
    if c["obra_semanas"]:
        obra = {"lugares": milhar(c["obra_lugares"]), "semanas": c["obra_semanas"]}
    return {
        "cabecalho": cabecalho(G),
        "titulo": "Estadio",
        "subtitulo": c["estadio"],
        "metricas": [
            {"valor": milhar(c["capacidade"]), "nome": "lugares"},
            {"valor": "R$ %d" % c["preco"], "nome": "ingresso"},
            {"valor": "+%s" % obra["lugares"] if obra else "nenhuma", "nome": "obra",
             "estado": "atencao" if obra else None},
        ],
        "preco": c["preco"],
        "preco_min": PRECO_MIN,
        "preco_max": PRECO_MAX,
        "obra": obra,
        "custo_lugar": CUSTO_LUGAR,
        "lugares_min": LUGARES_MIN,
        "lugares_max": LUGARES_MAX,
        "caixa": eng.din(c["dinheiro"]),
        "caixa_num": int(c["dinheiro"]),
        "rendimento": _rendimento_estadio(G, c),
    }


def _rendimento_estadio(G, c):
    """Os jogos em casa do ano: publico, ocupacao e renda, e o que pesa no preco."""
    jogos = eng.stats_ano(G).get("jogos_casa", [])
    ref = eng.preco_referencia(c)
    linhas = []
    if jogos:
        pub = sum(j[0] for j in jogos) / len(jogos)
        ocup = sum(j[0] / max(1, j[2]) for j in jogos) / len(jogos)
        renda = sum(j[1] for j in jogos)
        linhas += [
            {"nome": "Jogos em casa no ano", "valor": str(len(jogos))},
            {"nome": "Publico medio", "valor": "%s (%d%% ocupado)" % (milhar(pub), round(ocup * 100)),
             "estado": "ok" if ocup >= 0.7 else ("atencao" if ocup >= 0.4 else "critico")},
            {"nome": "Renda media por jogo", "valor": eng.din(renda / len(jogos))},
            {"nome": "Bilheteria no ano", "valor": eng.din(renda)},
        ]
    else:
        linhas.append({"nome": "Jogos em casa no ano", "valor": "nenhum ainda"})
    demanda = eng.demanda_torcida(c)
    linhas += [
        {"nome": "Torcida num jogo comum", "valor": "%s pessoas" % milhar(demanda),
         "dica": ("com ingresso de referencia; o estadio tem %s lugares%s"
                  % (milhar(c["capacidade"]),
                     " - lugar sobrando so custa manutencao" if c["capacidade"] > demanda * 1.3 else "")),
         "estado": "atencao" if c["capacidade"] > demanda * 1.3 else None},
        {"nome": "Operacao de cada jogo em casa", "valor": "%d%% da renda" % round(eng.CUSTO_JOGO_CASA * 100),
         "dica": "seguranca, staff e arbitragem saem da bilheteria"},
        {"nome": "Ingresso de referencia da sua torcida", "valor": "R$ %d" % round(ref),
         "dica": "acima disso o publico cai rapido; adversario grande e copa enchem mais"},
        {"nome": "Manutencao de cada 1.000 lugares", "valor": eng.din(1000 * eng.manutencao_por_lugar(c)) + " por semana",
         "dica": "ampliar aumenta o custo fixo; estadio cheio tambem pesa a favor em campo"},
    ]
    return linhas


def previa_esquema(cont):
    """O editor de formacao pergunta a cada clique: como fica o time assim?"""
    G = SESSAO.exigir()
    c = G["clubes"][G["clube"]]
    ok, motivo = eng.contagem_valida(cont)
    if not ok:
        return {"valida": False, "motivo": motivo}
    pronta = eng.formacao_pronta(cont)
    d = SESSAO.diagnostico()
    manter = None if eng.escalacao_automatica(G, c) else d["escalacao"]
    sim = simular_esquema(G, c, pronta or eng.FORMACAO_PERSONALIZADA,
                          None if pronta else cont, manter)
    xi, vazias = _xi(G, {"vagas": sim["vagas"]})
    return {
        "valida": True, "motivo": "",
        "rotulo": pronta or "Personalizada (%s)" % eng.nome_da_contagem(cont),
        "ataque": round(sim["ataque"], 1), "defesa": round(sim["defesa"], 1),
        "improvisados": sim["improvisados"], "graves": sim["graves"],
        "mantem_os_11": manter is not None,
        "jogadores": xi, "vagas_abertas": vazias,
    }



# ------------------------------------------------------------ resumo do ano
def resumo(r, previa=False):
    """O fim do ano em campos, do jeito que a janela tkinter mostrava.

    previa=True e o resumo antes da virada (apurar_temporada): posicao,
    campanha, titulos e dinheiro ja estao fechados; diretoria, acesso, base e
    contratos so se decidem quando o ano vira, e a tela diz isso.
    """
    cam, fin = r["campanha"], r["financas"]
    saldo = fin["caixa_fim"] - fin["caixa_ini"]
    vereditos = []
    if r["titulos"]:
        vereditos.append({"texto": "CAMPEAO: " + ", ".join(r["titulos"]), "estado": "ok"})
    if r.get("movimento"):
        tipo, de, para = r["movimento"]
        vereditos.append(
            {"texto": "ACESSO: o clube sobe da Serie %s para a Serie %s" % (de, para), "estado": "ok"}
            if tipo == "acesso" else
            {"texto": "REBAIXAMENTO: o clube cai da Serie %s para a Serie %s" % (de, para),
             "estado": "critico"})
    vereditos.append({"texto": "Objetivo cumprido" if r["objetivo_ok"] else "Objetivo nao cumprido",
                      "estado": "ok" if r["objetivo_ok"] else "atencao"})
    if not previa and r.get("diretoria"):
        vereditos.append({"texto": r["diretoria"],
                          "estado": "ok" if r["diretoria_ok"] else "critico"})

    secoes = []

    def secao(titulo, itens):
        itens = [i for i in itens if i]
        if itens:
            secoes.append({"titulo": titulo, "itens": itens})

    def item(texto, estado="neutro"):
        return {"texto": texto, "estado": estado}

    secao("Como terminou", [item("Campeao da %s: %s" % (eng.liga_do_resumo(r), r["campeao"]), "ok")]
          + [item("%s: %s" % (nome, dono)) for nome, dono in r["copas"]])
    destaques = []
    if r["artilheiro"]:
        nome, g, jj = r["artilheiro"]
        destaques.append(item("Artilheiro: %s, %s em %s" % (nome, eng.plural(g, "gol"), eng.plural(jj, "jogo")),
                              "ok"))
    if r["garcom"]:
        nome, a, jj = r["garcom"]
        destaques.append(item("Mais assistencias: %s, %d em %s" % (nome, a, eng.plural(jj, "jogo")), "ok"))
    for nome, pos, j, g, a in r.get("destaques", []):
        destaques.append(item("%s (%s): %d jogos, %d gols, %d assistencias" % (nome, pos, j, g, a)))
    secao("Seus destaques", destaques or [item("Ninguem marcou nesta temporada.")])
    if "extrato" in r:
        # o extrato do ano: uma linha por categoria, e a soma fecha com o caixa
        resultado = fin["caixa_fim"] - fin["caixa_ini"]
        linhas = [item("Caixa: %s no comeco, %s no fim (%s%s no ano)" % (
            eng.din(fin["caixa_ini"]), eng.din(fin["caixa_fim"]),
            "+" if resultado >= 0 else "-", eng.din(abs(resultado))),
            "ok" if resultado >= 0 else "critico")]
        for chave, rotulo in eng.EXTRATO:
            v = int(r["extrato"].get(chave, 0))
            if v:
                linhas.append(item("%s: %s" % (rotulo, eng.din(v)), "ok" if v > 0 else "critico"))
        antes = resultado - sum(int(v) for v in r["extrato"].values())
        if antes:
            linhas.append(item("Antes do extrato (save de versao anterior): %s" % eng.din(antes)))
        if previa:
            linhas.append(item("A premiacao da liga entra quando o ano virar."))
        secao("Dinheiro no ano", linhas)
    else:
        # resumo de save antigo, sem extrato: a bilheteria ja esta dentro da receita
        secao("Dinheiro no ano", [
            item("Caixa: %s no comeco, %s no fim" % (eng.din(fin["caixa_ini"]), eng.din(fin["caixa_fim"]))),
            item("Entrou: %s de receita (dos quais %s de bilheteria)%s" % (
                eng.din(fin["receita"]), eng.din(fin["renda_jogos"]),
                "" if previa else ", mais %s de premiacao" % eng.din(fin["premios"]))),
            item("Saiu: %s entre folha, estrutura e treino" % eng.din(fin["gasto"])),
            item("Vendas: %s em %s · Compras: %s em %s" % (
                eng.din(fin["vendido"]), eng.plural(len(r["vendas"]), "negocio"),
                eng.din(fin["comprado"]), eng.plural(len(r["compras"]), "negocio"))),
        ])
    secao("Mercado", [item("vendeu %s ao %s por %s" % (n, cl, eng.din(v)), "ok") for n, cl, v in r["vendas"]]
          + [item("comprou %s do %s por %s" % (n, cl, eng.din(v)), "atencao") for n, cl, v in r["compras"]])
    secao("Quem cresceu", [item("%s: +%d de overall, chegou a %d" % (n, d, o), "ok")
                           for n, d, o in r["evolucao"]]
          or [item("Ninguem evoluiu de forma relevante. Olhe o regime de treino.")])
    if not previa:
        secao("Teto revisado", [item("%s: %+d, agora %d" % (n, d, p), "ok" if d > 0 else "critico")
                                for n, d, p in r["tetos"]])
        secao("Base", [item("safra nova: %s (%s, %d anos, overall %d)" % tuple(x), "ok") for x in r["safra"]]
              + [item("%s completou a idade e subiu ao profissional" % n, "ok") for n in r["base_subiu"]]
              + [item("%s passou da idade sem nivel e foi liberado" % n, "atencao") for n in r["base_saiu"]]
              or [item("A academia nao formou ninguem: suba o nivel da base na Infraestrutura.")])
        mexidas = []
        if r["voltando"]:
            mexidas.append(item("voltam do emprestimo: " + ", ".join(r["voltando"])))
        if r["saindo"]:
            mexidas.append(item("fim do emprestimo, voltam aos donos: " + ", ".join(r["saindo"]), "atencao"))
        if r["aposentados"]:
            mexidas.append(item("pararam de jogar: " + ", ".join(r["aposentados"]), "atencao"))
        if r["fim_contrato"]:
            mexidas.append(item("CONTRATO VENCIDO, saem de graca se voce nao renovar na pre-temporada: "
                                + ", ".join(r["fim_contrato"]), "critico"))
        secao("Mexidas no elenco", mexidas)

    return {
        "previa": previa,
        "temporada": r["temporada"],
        "titulo": "Temporada %d encerrada" % r["temporada"],
        "subtitulo": "%s · %s · %do lugar de %d · meta era top %d" % (
            r["clube"], eng.liga_do_resumo(r), r["posicao"], r["total"], r["alvo"]),
        "vereditos": vereditos,
        "tiles": [
            {"nome": "Posicao", "valor": "%do" % r["posicao"],
             "sub": "de %d na %s" % (r["total"], eng.liga_do_resumo(r)),
             "estado": "ok" if r["objetivo_ok"] else "atencao"},
            {"nome": "Campanha", "valor": "%d pts" % cam["p"],
             "sub": "%dV %dE %dD em %d jogos" % (cam["v"], cam["e"], cam["d"], cam["j"]), "estado": "neutro"},
            {"nome": "Titulos", "valor": str(len(r["titulos"])),
             "sub": ", ".join(r["titulos"]) if r["titulos"] else "nenhum nesta temporada",
             "estado": "ok" if r["titulos"] else "neutro"},
            {"nome": "Caixa no ano", "valor": ("+" if saldo >= 0 else "") + eng.din(saldo),
             "sub": "%s no fim" % eng.din(fin["caixa_fim"]), "estado": "ok" if saldo >= 0 else "critico"},
        ],
        "secoes": secoes,
        "nota": ("Diretoria, acesso e rebaixamento, fim de contratos, base e premiacao se "
                 "decidem na virada: clique em Comecar o ano %d." % (r["temporada"] + 1)) if previa else
                "O mercado ja esta aberto e o estadual so comeca quando voce mandar.",
    }
