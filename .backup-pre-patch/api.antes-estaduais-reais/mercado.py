# -*- coding: utf-8 -*-
"""O Mercado: a tela de busca, a vitrine e as mesas de negociacao.

Mora num modulo proprio porque e maior que todas as outras telas juntas. A
regra continua a mesma do dto.py: o motor decide (quanto o dono pede, se a
proposta passa), aqui so se traduz para a tela.

As mesas (comprar, pegar emprestado, renovar) tem tres tentativas, como na
janela tkinter. A diferenca: la o contador vivia no dialogo e fechar e reabrir
zerava tudo, inclusive a mesa que o outro lado tinha encerrado. Aqui ele mora
na sessao e vale pela semana - "nao adianta insistir" passa a ser verdade.
"""

from .sessao import SESSAO
from . import dto
import brasfut as eng

ABAS = [("compra", "Comprar"), ("emprestimo", "Emprestimos"),
        ("livres", "Agentes livres"), ("vitrine", "Minha vitrine")]
TENTATIVAS = 3
LIMITE_BUSCA = 60


def _limpo(txt):
    return dto.LIMPA_COR.sub("", txt or "").strip()


# ======================================================================= tela
def _filtros(f):
    """Filtros vindos da tela, ja saneados: numero vira numero ou some."""
    def inteiro(chave):
        try:
            v = int(f.get(chave) or 0)
        except (TypeError, ValueError):
            return None
        return v or None
    pos = f.get("pos") if f.get("pos") in eng.POS else None
    return {"pos": pos, "ovr": inteiro("ovr"), "idade": inteiro("idade"),
            "teto": inteiro("teto")}


def acertados(G):
    """Quem ja tem acerto agendado para vir ao meu clube na abertura da janela.

    Com a janela fechada o negocio fecha mas o jogador continua no clube dele
    ate a abertura: sem esta marca ele seguia na lista como se estivesse
    disponivel, e dava para negociar e agendar o mesmo reforco duas vezes.
    """
    return {a["jogador"]: a for _i, a in eng.minhas_agendadas(G) if a.get("para") == G["clube"]}


def _linha_busca(G, c, j, aba, pendentes=None):
    clube = G["clubes"][j["clube"]]["nome"] if j["clube"] is not None else "sem clube"
    linha = {"id": j["id"], "pos": j["pos"], "nome": j["nome"], "idade": j["idade"],
             "ovr": j["ovr"], "teto": eng.scout(G, j), "clube": clube,
             "salario": eng.din(j["salario"]), "livre": j["clube"] is None,
             "acertado": bool(pendentes and j["id"] in pendentes),
             "tag": dto._tag_ovr(j["ovr"])}
    if aba == "emprestimo":
        pct = eng.exigencia_emprestimo(G, j, c)
        linha.update(pct=pct, fatia=eng.din(j["salario"] * pct // 100))
    elif j["clube"] is None:
        linha.update(pedido="livre", marca="", emprestimo=False)
    else:
        valor, intocavel = eng.pedido_efetivo(G, j)
        # a marca e regra, nao enfeite: a legenda da tela explica cada uma
        marca = "intocavel" if intocavel else ("a_venda" if j["listado"] else "")
        linha.update(pedido=eng.din(valor), pedido_num=int(valor), marca=marca,
                     emprestimo=bool(j.get("emp_listado")))
    return linha


def _busca(G, c, aba, f):
    if aba == "livres":
        achados = [j for j in (G["jogadores"][p] for p in G["livres"])
                   if (not f["pos"] or j["pos"] == f["pos"])
                   and (not f["ovr"] or j["ovr"] >= f["ovr"])
                   and (not f["idade"] or j["idade"] <= f["idade"])]
        achados.sort(key=lambda j: -j["ovr"])
        achados = achados[:LIMITE_BUSCA]
    else:
        achados = eng.buscar(G, pos=f["pos"], ovr=f["ovr"], idade=f["idade"],
                             teto=f["teto"], so_emprestimo=(aba == "emprestimo"),
                             limite=LIMITE_BUSCA)
    pendentes = acertados(G)
    return [_linha_busca(G, c, j, aba, pendentes) for j in achados]


def _vitrine(G, c, ofertas):
    por_jogador = {}
    for j, cl, v in ofertas:
        por_jogador.setdefault(j["id"], (cl, v))
    listados = [G["jogadores"][p] for p in c["elenco"]
                if G["jogadores"][p]["listado"] and not G["jogadores"][p].get("dono")]
    linhas = []
    for j in sorted(listados, key=lambda x: -x["valor"]):
        cl, v = por_jogador.get(j["id"], (None, 0))
        linhas.append({
            "id": j["id"], "nome": j["nome"], "pos": j["pos"], "ovr": j["ovr"],
            "salario": eng.din(j["salario"]), "valor": eng.din(j["valor"]),
            "pede": eng.din(j["listado"]),
            "pct": round(100.0 * j["listado"] / max(1, j["valor"])),
            "interessado": cl["nome"] if cl else None, "oferta": eng.din(v) if v else None,
            "tag": dto._tag_ovr(j["ovr"]),
        })
    return linhas


def _ofertas(G, ofertas):
    fora = []
    for j, cl, v in ofertas:
        dif = v - j["listado"] if j["listado"] else None
        fora.append({
            "chave": "%d:%d" % (j["id"], cl["id"]), "id": j["id"], "clube_id": cl["id"],
            "nome": j["nome"], "pos": j["pos"], "ovr": j["ovr"], "clube": cl["nome"],
            "divisao": cl["divisao"], "oferta": eng.din(v), "oferta_num": int(v),
            "pede": eng.din(j["listado"]) if j["listado"] else "nao esta a venda",
            "diferenca": (("+" if dif >= 0 else "") + eng.din(dif)) if dif is not None else "-",
            "estado": "ok" if dif is None or dif >= 0 else "atencao",
            "salario_num": int(j["salario"]),
        })
    return fora


def _agendadas(G):
    fora = []
    for indice, a in eng.minhas_agendadas(G):
        j = G["jogadores"].get(a["jogador"])
        saindo = a.get("de") == G["clube"]
        outro = G["clubes"].get(a["para"] if saindo else a.get("de"))
        if a["tipo"] == eng.TIPO_EMPRESTIMO:
            tipo, valor = ("cessao" if saindo else "emprestimo"), "%d%%" % a["pct_salario"]
        else:
            tipo, valor = ("venda" if saindo else "compra"), eng.din(a["valor"])
        fora.append({"indice": indice, "jogador": j["nome"] if j else "?", "tipo": tipo,
                     "com": outro["nome"] if outro else "sem clube", "valor": valor,
                     "quando": "T%d S%d" % (a["temporada"], a["semana"])})
    return fora


def tela(aba="compra", filtros=None):
    G = SESSAO.exigir()
    c = G["clubes"][G["clube"]]
    if aba not in dict(ABAS):
        aba = "compra"
    f = _filtros(filtros or {})
    aberto = eng.mercado_aberto(G)
    ofertas = eng.propostas_recebidas(G)
    fora = {
        "cabecalho": dto.cabecalho(G),
        "titulo": "Mercado",
        "subtitulo": eng.recado_janela(G),
        "aberto": aberto,
        "metricas": [
            {"valor": "ABERTA" if aberto else "FECHADA", "nome": "janela",
             "estado": "ok" if aberto else "atencao"},
            {"valor": eng.din(c["dinheiro"]), "nome": "caixa"},
            {"valor": eng.din(eng.folha_semanal(G, c)), "nome": "folha por semana"},
            {"valor": "%d/%d" % (len(c["elenco"]), eng.LIMITE_ELENCO), "nome": "elenco"},
            {"valor": len(ofertas), "nome": "propostas", "estado": "atencao" if ofertas else None},
        ],
        "abas": [{"id": k, "nome": n, "contador": len(ofertas) if k == "vitrine" else None}
                 for k, n in ABAS],
        "aba": aba,
        "filtros": f,
        "posicoes": list(eng.POS),
        "caixa_num": int(c["dinheiro"]),
    }
    if aba == "vitrine":
        fora.update(vitrine=_vitrine(G, c, ofertas), ofertas=_ofertas(G, ofertas),
                    agendadas=_agendadas(G), jogadores=[])
    else:
        fora.update(jogadores=_busca(G, c, aba, f), vitrine=[], ofertas=[],
                    agendadas=_agendadas(G))
    return fora


# ====================================================================== mesas
def _mesa_estado(tipo, pid):
    """O contador da mesa nesta semana. Semana nova, conversa nova."""
    G = SESSAO.exigir()
    chave = "%s:%d" % (tipo, pid)
    carimbo = "%d-%d" % (G["temporada"], G["semana"])
    m = SESSAO.mesas.get(chave)
    if not m or m["carimbo"] != carimbo:
        m = {"carimbo": carimbo, "rodada": 0, "encerrada": False, "falas": [],
             "fechada_com": None}
        SESSAO.mesas[chave] = m
    return m


def _peso(G, j):
    imp = eng.importancia(G, j)
    return "reserva" if imp < 0.3 else ("titular" if imp < 0.7 else "peca central do time")


def _leitura(oferta, pedido):
    recado, estado = eng.leitura_oferta(int(oferta), int(pedido))
    return {"texto": recado, "estado": estado,
            "pct": round(100.0 * oferta / max(1, pedido)) if pedido else None}


def _inteiro(v, padrao=0):
    try:
        return max(0, int(v))
    except (TypeError, ValueError):
        return padrao


def mesa(tipo, pid, proposta=None):
    """Tudo o que a mesa desenha, com a leitura do outro lado para a proposta
    que esta na tela. A tela pergunta de novo a cada mexida (com respiro)."""
    G = SESSAO.exigir()
    c = G["clubes"][G["clube"]]
    j = G["jogadores"].get(int(pid))
    if j is None:
        raise KeyError("jogador %s nao existe" % pid)
    p = proposta or {}
    anos = int(eng.clamp(_inteiro(p.get("anos"), 3) or 3, 1, 5))
    m = _mesa_estado(tipo, j["id"])
    # quem ja e do clube nao volta a mesa de compra: a nao ser a mesa que
    # acabou de fechar o negocio, que ainda precisa mostrar o contrato
    if tipo in ("compra", "emprestimo") and j["clube"] == c["id"] and not m["fechada_com"]:
        raise ValueError("%s ja e do seu clube." % j["nome"])
    # acerto ja agendado (de qualquer semana): a mesa abre mostrando o acerto,
    # nunca o formulario - senao dava para fechar o mesmo negocio de novo
    pendente = acertados(G).get(j["id"])
    if tipo in ("compra", "emprestimo") and pendente and not m["fechada_com"]:
        m["encerrada"] = True
        m["fechada_com"] = ("%s ja esta acertado com voce (%s). Chega na abertura da janela: %s"
                            % (j["nome"], "emprestimo" if pendente["tipo"] == eng.TIPO_EMPRESTIMO
                               else "compra", eng.recado_janela(G).lower()))
    folha = eng.folha_semanal(G, c)
    base = {
        "tipo": tipo, "id": j["id"], "nome": j["nome"],
        "descricao": "%s, %d anos, overall %d, teto %s" % (
            eng.NOME_POS[j["pos"]], j["idade"], j["ovr"], eng.scout(G, j)),
        "clube": G["clubes"][j["clube"]]["nome"] if j["clube"] is not None else "sem clube",
        "janela": eng.recado_janela(G), "aberto": eng.mercado_aberto(G),
        "caixa": eng.din(c["dinheiro"]), "caixa_num": int(c["dinheiro"]),
        "salario_atual": eng.din(j["salario"]), "salario_atual_num": int(j["salario"]),
        "anos": anos, "rodada": m["rodada"], "tentativas": TENTATIVAS,
        "encerrada": m["encerrada"], "falas": list(m["falas"]),
        "fechada_com": m["fechada_com"],
    }

    if tipo == "compra":
        livre = j["clube"] is None
        pedido, intocavel = (0, False) if livre else eng.pedido_efetivo(G, j)
        exig = eng.exigencia_salarial(G, j, c, anos)
        valor = _inteiro(p.get("valor"), pedido) if "valor" in p else pedido
        salario = _inteiro(p.get("salario"), exig) if "salario" in p else exig
        base.update(
            livre=livre, intocavel=intocavel, pedido=eng.din(pedido), pedido_num=int(pedido),
            contexto=("Agente livre: nao ha passe a pagar, so acertar contrato." if livre else
                      "No clube atual ele e %s. Contrato dele: %d ano(s)." % (_peso(G, j), j["contrato"])),
            exigencia=eng.din(exig), exigencia_num=int(exig),
            valor=valor, salario=salario,
            leitura_passe=None if livre else _leitura(valor, pedido),
            leitura_salario=_leitura(salario, exig),
            caixa_depois=eng.din(c["dinheiro"] - valor), falta_caixa=valor > c["dinheiro"],
            folha_depois="Folha semanal: %s -> %s com %d ano(s) de contrato"
                         % (eng.din(folha), eng.din(folha + int(salario / 4.0)), anos),
            atalhos_passe=[] if livre else [
                {"rotulo": "- 10%", "valor": int(pedido * 0.90)},
                {"rotulo": "- 5%", "valor": int(pedido * 0.95)},
                {"rotulo": "pedido", "valor": int(pedido)},
                {"rotulo": "+ 5%", "valor": int(pedido * 1.05)},
                {"rotulo": "meu caixa", "valor": int(max(0, c["dinheiro"]))}],
            atalhos_salario=[
                {"rotulo": "- 10%", "valor": int(exig * 0.90)},
                {"rotulo": "- 5%", "valor": int(exig * 0.95)},
                {"rotulo": "o que ele pede", "valor": int(exig)},
                {"rotulo": "+ 10%", "valor": int(exig * 1.10)}])
    elif tipo == "emprestimo":
        if j["clube"] is None:
            raise ValueError("%s esta sem clube: contrate como agente livre." % j["nome"])
        exig = eng.exigencia_emprestimo(G, j, c)
        taxa = eng.taxa_emprestimo(G, j, c)
        piso = eng.piso_opcao_compra(G, j)
        mercado = eng.preco_pedido(G, j) or j["valor"]
        pct = int(eng.clamp(_inteiro(p.get("pct"), exig) if "pct" in p else exig, 0, 100))
        opcao = _inteiro(p.get("opcao"), 0)
        minha = j["salario"] * pct // 100
        if not opcao:
            leitura_opcao = {"texto": "Sem opcao: no fim da temporada ele volta ao dono.",
                             "estado": "neutro", "pct": None}
        else:
            leitura_opcao = {"texto": "O dono so trava o passe a partir de %s (valor de mercado %s)"
                                      % (eng.din(piso), eng.din(j["valor"])),
                             "estado": "ok" if opcao >= piso else "critico", "pct": None}
        base.update(
            contexto=("Ele fica com voce ate o fim da temporada e depois volta ao dono, a nao "
                      "ser que voce trave uma opcao de compra."),
            exigencia_pct=exig, pct=pct, opcao=opcao, piso=eng.din(piso), piso_num=int(piso),
            taxa=eng.din(taxa) if taxa else None, taxa_num=int(taxa),
            falta_caixa=taxa > c["dinheiro"],
            leitura_pct=_leitura(pct, exig),
            divisao="Voce paga %s por mes, o dono paga %s. Folha semanal: %s -> %s"
                    % (eng.din(minha), eng.din(j["salario"] - minha), eng.din(folha),
                       eng.din(folha + int(minha / 4.0))),
            leitura_opcao=leitura_opcao,
            atalhos_opcao=[{"rotulo": "sem opcao", "valor": 0},
                           {"rotulo": "piso do dono", "valor": int(piso)},
                           {"rotulo": "valor de mercado", "valor": int(j["valor"])},
                           {"rotulo": "pedido cheio", "valor": int(mercado)}])
    elif tipo == "renovacao":
        if j["clube"] != c["id"] or j.get("dono"):
            raise ValueError("%s nao tem contrato com voce para renovar." % j["nome"])
        exig = eng.exigencia_renovacao(G, j, anos)
        salario = _inteiro(p.get("salario"), exig) if "salario" in p else exig
        base.update(
            contexto="Contrato atual: %d ano(s) a %s por mes. Moral %d. Ele e %s."
                     % (j["contrato"], eng.din(j["salario"]), j["moral"], _peso(G, j)),
            acabando=j["contrato"] <= 1,
            exigencia=eng.din(exig), exigencia_num=int(exig), salario=salario,
            leitura_salario=_leitura(salario, exig),
            folha_depois="Folha semanal: %s -> %s | multa de rescisao ficaria %s"
                         % (eng.din(folha), eng.din(folha + int((salario - j["salario"]) / 4.0)),
                            eng.din(int(salario * 4 * anos * 0.5))),
            atalhos_salario=[
                {"rotulo": "- 10%", "valor": int(exig * 0.90)},
                {"rotulo": "- 5%", "valor": int(exig * 0.95)},
                {"rotulo": "o que ele pede", "valor": int(exig)},
                {"rotulo": "+ 10%", "valor": int(exig * 1.10)}])
    else:
        raise ValueError("mesa desconhecida")
    return base


def _insistir(m, r, recado_final, ao_esgotar=None):
    """Mais uma tentativa gasta. Encerra se o outro lado fechou ou se acabaram."""
    if r.encerrada:
        m["encerrada"] = True
        return
    m["rodada"] += 1
    if m["rodada"] >= TENTATIVAS:
        m["encerrada"] = True
        if ao_esgotar:
            recado_final = ao_esgotar()
        m["falas"].append(recado_final)


def propor(tipo, pid, p):
    """Manda a proposta que esta na tela. Devolve (fechou, recado)."""
    G = SESSAO.exigir()
    c = G["clubes"][G["clube"]]
    j = G["jogadores"].get(int(pid))
    if j is None:
        raise KeyError("jogador %s nao existe" % pid)
    m = _mesa_estado(tipo, j["id"])
    if m["encerrada"]:
        raise ValueError("Essa mesa ja fechou nesta semana. Tente de novo na proxima.")
    anos = int(eng.clamp(_inteiro(p.get("anos"), 3) or 3, 1, 5))

    if tipo == "compra":
        passe = _inteiro(p.get("valor")) if j["clube"] is not None else 0
        if passe > c["dinheiro"]:
            raise ValueError("Voce nao tem %s em caixa." % eng.din(passe))
        prop = eng.Proposta(jogador=j["id"], comprador=c["id"], valor=passe,
                            salario=_inteiro(p.get("salario")), anos=anos)
        r = eng.avaliar_clube(G, prop)
        if not r.aceita:
            m["falas"].append("PASSE: " + r.motivo)
            _insistir(m, r, "Sem acordo pelo passe de %s." % j["nome"])
            return False, None
        if j["clube"] is not None:
            m["falas"].append("PASSE: " + r.motivo)
        rj = eng.avaliar_jogador(G, prop)
        if rj.aceita:
            texto = eng.fechar_compra(G, prop)
            m["falas"].append(texto)
            m["encerrada"], m["fechada_com"] = True, texto
            return True, texto
        m["falas"].append("SALARIO: " + rj.motivo)
        _insistir(m, rj, "%s nao chegou a um acordo salarial." % j["nome"])
        return False, None

    if tipo == "emprestimo":
        taxa = eng.taxa_emprestimo(G, j, c)
        prop = eng.Proposta(jogador=j["id"], comprador=c["id"], valor=taxa,
                            pct_salario=int(eng.clamp(_inteiro(p.get("pct")), 0, 100)),
                            opcao_compra=_inteiro(p.get("opcao")), tipo=eng.TIPO_EMPRESTIMO)
        r = eng.avaliar_emprestimo(G, prop)
        m["falas"].append(r.motivo)
        if r.aceita:
            texto = eng.fechar_emprestimo(G, prop)
            m["falas"].append(texto)
            m["encerrada"], m["fechada_com"] = True, texto
            return True, texto
        _insistir(m, r, "Emprestimo de %s nao saiu." % j["nome"])
        return False, None

    if tipo == "renovacao":
        prop = eng.Proposta(jogador=j["id"], comprador=c["id"], salario=_inteiro(p.get("salario")),
                            anos=anos, tipo=eng.TIPO_RENOVACAO)
        r = eng.avaliar_renovacao(G, prop)
        if r.aceita:
            texto = eng.fechar_renovacao(G, prop)
            m["falas"].append(texto)
            m["encerrada"], m["fechada_com"] = True, texto
            return True, texto
        m["falas"].append(r.motivo)
        _insistir(m, r, "", ao_esgotar=lambda: eng.romper_renovacao(G, j))
        return False, None

    raise ValueError("mesa desconhecida")


# ============================================================= vitrine em lote
def sugerir_precos(ids, pct):
    """Preco de vitrine proporcional ao valor de cada um (o 130% da janela)."""
    G = SESSAO.exigir()
    pct = int(eng.clamp(_inteiro(pct, 130), 40, 300))
    fora = []
    for pid in ids:
        j = G["jogadores"].get(pid)
        if not j or j.get("dono"):
            continue
        fora.append({"id": j["id"], "preco": eng.preco_sugerido(G, j, pct)})
    return fora


def linhas_vitrine(ids):
    """Quem vai para a vitrine, com o preco atual (ou o sugerido de 130%)."""
    G = SESSAO.exigir()
    fora = []
    for pid in ids:
        j = G["jogadores"].get(pid)
        if not j or j.get("dono"):
            continue
        fora.append({"id": j["id"], "nome": j["nome"], "pos": j["pos"], "ovr": j["ovr"],
                     "contrato": j["contrato"], "salario": eng.din(j["salario"]),
                     "salario_num": int(j["salario"]), "valor": eng.din(j["valor"]),
                     "valor_num": int(j["valor"]),
                     "preco": int(j["listado"]) or eng.preco_sugerido(G, j, 130),
                     "tag": dto._tag_ovr(j["ovr"])})
    return fora


def ofertas_cessao(ids):
    """Toda proposta de emprestimo pelos marcados: uma linha por par jogador/clube."""
    G = SESSAO.exigir()
    fora = []
    for pid in ids:
        j = G["jogadores"].get(pid)
        if not j or j.get("dono"):
            continue
        for cl, pct in eng.ofertas_emprestimo(G, j):
            fora.append({"chave": "%d:%d" % (j["id"], cl["id"]), "id": j["id"],
                         "clube_id": cl["id"], "nome": j["nome"], "ovr": j["ovr"],
                         "salario": eng.din(j["salario"]), "clube": cl["nome"],
                         "divisao": cl["divisao"], "reputacao": cl["reputacao"], "pct": pct,
                         "sobra": eng.din(j["salario"] * (100 - pct) // 100),
                         "alivio_num": int(j["salario"] * pct // 100),
                         "tag": dto._tag_ovr(j["ovr"])})
    return fora
