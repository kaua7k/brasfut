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
import re
import brasfut as eng

ABAS = [("compra", "Comprar"), ("emprestimo", "Emprestimos"),
        ("livres", "Agentes livres"), ("vitrine", "Vender")]
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
    regiao = f.get("regiao") if f.get("regiao") in REGIOES else None
    return {"pos": pos, "ovr": inteiro("ovr"), "idade": inteiro("idade"),
            "teto": inteiro("teto"), "idade_min": inteiro("idade_min"),
            "pot_min": inteiro("pot_min"), "regiao": regiao, "so_venda": bool(f.get("so_venda"))}


# regioes do filtro do mercado: a liga de onde o jogador viria
REGIOES = {"br": "Brasil", "sul": "America do Sul", "europa": "Europa", "outros": "Outras ligas"}
EUROPA = ("ENG", "ESP", "GER", "ITA", "FRA", "POR", "NED")


def regiao_de(G, j):
    if j["clube"] is None:
        return None
    div = G["clubes"][j["clube"]]["divisao"]
    if div in eng.DIVISOES_BR:
        return "br"
    if div in eng.CODIGOS_SUL:
        return "sul"
    return "europa" if div in EUROPA else "outros"


def teto_visto(G, j):
    """O teto que o MEU olheiro enxerga (o meio da faixa): o filtro nao pode
    revelar o potencial escondido."""
    nums = [int(n) for n in re.findall(r"\d+", eng.scout(G, j))]
    return sum(nums) // len(nums) if nums else j["ovr"]


def _passa(G, j, f):
    if f["idade_min"] and j["idade"] < f["idade_min"]:
        return False
    if f["regiao"] and regiao_de(G, j) != f["regiao"]:
        return False
    if f["so_venda"] and not j["listado"]:
        return False
    if f["pot_min"] and teto_visto(G, j) < f["pot_min"]:
        return False
    return True


def acertados(G):
    """Quem ja tem acerto agendado para vir ao meu clube na abertura da janela.

    Com a janela fechada o negocio fecha mas o jogador continua no clube dele
    ate a abertura: sem esta marca ele seguia na lista como se estivesse
    disponivel, e dava para negociar e agendar o mesmo reforco duas vezes.
    """
    return {a["jogador"]: a for _i, a in eng.minhas_agendadas(G) if a.get("para") == G["clube"]}


def _porque_do_pedido(G, j, intocavel):
    """O que empurra o pedido acima do valor, em palavras (a conta e preco_pedido)."""
    motivos = []
    if intocavel:
        motivos.append("o clube nao quer vender")
    imp = eng.importancia(G, j)
    if imp >= 0.6:
        motivos.append("ele e peca central do time")
    elif imp >= 0.3:
        motivos.append("ele e titular")
    if j["contrato"] >= 4:
        motivos.append("contrato longo")
    elif j["contrato"] <= 1:
        motivos.append("ultimo ano de contrato baixa o preco")
    return (": " + ", ".join(motivos)) if motivos else ""


def _linha_busca(G, c, j, aba, pendentes=None):
    clube = eng.nome_clube(G, j["clube"])
    linha = {"id": j["id"], "pos": j["pos"], "nome": j["nome"], "idade": j["idade"],
             "ovr": j["ovr"], "teto": eng.scout(G, j), "clube": clube,
             "salario": eng.din(j["salario"]), "livre": j["clube"] is None,
             "valor": eng.din(j["valor"]), "valor_num": int(j["valor"]),
             "acertado": bool(pendentes and j["id"] in pendentes),
             "tag": dto._tag_ovr(j["ovr"])}
    if aba == "emprestimo":
        pct = eng.exigencia_emprestimo(G, j, c)
        linha.update(pct=pct, fatia=eng.din(j["salario"] * pct // 100))
    elif j["clube"] is None:
        # o livre nao tem salario em vigor: a coluna mostra o que ele pede aqui
        linha.update(pedido="livre", marca="", emprestimo=False,
                     salario=eng.din(eng.exigencia_salarial(G, j, c)))
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
                   and (not f["idade"] or j["idade"] <= f["idade"])
                   and _passa(G, j, dict(f, regiao=None, so_venda=False))]
        achados.sort(key=lambda j: -j["ovr"])
        achados = achados[:LIMITE_BUSCA]
    else:
        # os filtros extras cortam antes do limite: senao sobravam 3 dos 25
        achados = eng.buscar(G, pos=f["pos"], ovr=f["ovr"], idade=f["idade"],
                             teto=f["teto"], so_emprestimo=(aba == "emprestimo"),
                             limite=10 ** 6)
        achados = [j for j in achados if _passa(G, j, f)][:LIMITE_BUSCA]
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
            "interessado": eng.nome_clube(G, cl["id"]) if cl else None, "oferta": eng.din(v) if v else None,
            "tag": dto._tag_ovr(j["ovr"]),
        })
    return linhas


def _ofertas(G, ofertas):
    fora = []
    for j, cl, v in ofertas:
        dif = v - j["listado"] if j["listado"] else None
        pct_valor = round(100.0 * v / max(1, j["valor"]))
        fora.append({
            "valor": eng.din(j["valor"]), "valor_num": int(j["valor"]),
            "pede_num": int(j["listado"]), "pct_valor": pct_valor,
            "contras": eng.contrapropostas_restantes(G, j["id"], cl["id"]),
            "contrato": j["contrato"],
            "chave": "%d:%d" % (j["id"], cl["id"]), "id": j["id"], "clube_id": cl["id"],
            "nome": j["nome"], "pos": j["pos"], "ovr": j["ovr"], "clube": eng.nome_clube(G, cl["id"]),
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
                     "com": eng.nome_clube(G, outro["id"]) if outro else "sem clube", "valor": valor,
                     "quando": "T%d S%d" % (a["temporada"], a["semana"])})
    return fora


def financeiro(G, c):
    """Caixa, o que dele fica reservado para a folha e o que sobra para contratar."""
    orc = eng.orcamento_mensal(G, c)
    reserva = eng.reserva_custos(G, c)
    verba = eng.verba_contratacao(G, c)
    return {"caixa": eng.din(c["dinheiro"]), "reserva": eng.din(reserva),
            "verba": eng.din(verba), "verba_num": verba,
            "meses": eng.RESERVA_MESES, "custos_mes": eng.din(orc["custos"]),
            "saldo_mes": eng.din(orc["saldo"]), "saldo_mes_num": orc["saldo"],
            "estado": "ok" if verba > 0 else "critico"}


def contratos_acabando(G, c):
    """Meus jogadores no ultimo ano de contrato (ou ja vencido), com o que pedem
    para renovar por tres anos. Emprestado aqui nao entra: o contrato e do dono."""
    linhas = []
    for p in c["elenco"]:
        j = G["jogadores"][p]
        if j.get("dono") or j["contrato"] > 1:
            continue
        linhas.append({
            "id": j["id"], "nome": j["nome"], "pos": j["pos"], "ovr": j["ovr"],
            "idade": j["idade"], "contrato": j["contrato"], "tag": dto._tag_ovr(j["ovr"]),
            "salario": eng.din(j["salario"]),
            "pede": eng.din(eng.exigencia_renovacao(G, j, 3)),
            "valor": eng.din(j["valor"]),
            "estado": "critico" if j["contrato"] <= 0 else "atencao",
            "quando": ("venceu: sai quando o ano comecar" if j["contrato"] <= 0
                       else "ultimo ano: sai de graca no fim da temporada"),
        })
    linhas.sort(key=lambda l: (l["contrato"], -l["ovr"]))
    return linhas


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
        # cada dado uma vez: caixa, verba e folha moram nos chips do topo (caixa e
        # verba nunca somem) e a faixa da verba, logo abaixo, explica a conta
        "metricas": [
            {"valor": "ABERTA" if aberto else "FECHADA", "nome": "janela",
             "estado": "ok" if aberto else "atencao"},
            {"valor": "%d/%d" % (len(c["elenco"]), eng.LIMITE_ELENCO), "nome": "elenco"},
            {"valor": len(ofertas), "nome": "propostas", "estado": "atencao" if ofertas else None},
        ],
        "abas": [{"id": k, "nome": n, "contador": len(ofertas) if k == "vitrine" else None}
                 for k, n in ABAS],
        "aba": aba,
        "filtros": f,
        "regioes": [{"id": k, "nome": n} for k, n in REGIOES.items()],
        "posicoes": list(eng.POS),
        "caixa_num": int(c["dinheiro"]),
        "financeiro": financeiro(G, c),
        "contratos": contratos_acabando(G, c),
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
    fin = financeiro(G, c)
    # agente livre assina na hora, com a janela aberta ou fechada; depois de
    # assinar ele ja e do clube e a mesa ainda precisa dizer "ja esta no elenco"
    na_hora = eng.mercado_aberto(G) or (tipo == "compra" and j["clube"] in (None, c["id"]))
    base = {
        "verba": fin["verba"], "verba_num": fin["verba_num"], "reserva": fin["reserva"],
        "reserva_meses": fin["meses"],
        "tipo": tipo, "id": j["id"], "nome": j["nome"],
        "descricao": "%s, %d anos, overall %d, teto %s" % (
            eng.NOME_POS[j["pos"]], j["idade"], j["ovr"], eng.scout(G, j)),
        "clube": eng.nome_clube(G, j["clube"]),
        "janela": (eng.recado_janela(G) if eng.mercado_aberto(G) or not na_hora
                   else "Agente livre: assina na hora, com a janela aberta ou fechada."),
        "aberto": na_hora,
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
                      "No clube atual ele e %s. Contrato dele: %s. Valor de mercado %s: o pedido e %d%% "
                      "disso%s." % (_peso(G, j), eng.plural(j["contrato"], "ano"), eng.din(j["valor"]),
                                    round(100.0 * pedido / max(1, j["valor"])), _porque_do_pedido(G, j, intocavel))),
            exigencia=eng.din(exig), exigencia_num=int(exig),
            valor=valor, salario=salario,
            leitura_passe=None if livre else _leitura(valor, pedido),
            leitura_salario=_leitura(salario, exig),
            caixa_depois=eng.din(c["dinheiro"] - valor),
            # a verba conta o salario proposto: ele entra na reserva de folha
            verba_com_salario=eng.din(eng.verba_contratacao(G, c, salario)),
            falta_caixa=valor > eng.verba_contratacao(G, c, salario),
            folha_depois="Folha semanal: %s -> %s com %s de contrato"
                         % (eng.din(folha), eng.din(folha + int(salario / 4.0)), eng.plural(anos, "ano")),
            atalhos_passe=[] if livre else [
                {"rotulo": "- 10%", "valor": int(pedido * 0.90)},
                {"rotulo": "- 5%", "valor": int(pedido * 0.95)},
                {"rotulo": "pedido", "valor": int(pedido)},
                {"rotulo": "+ 5%", "valor": int(pedido * 1.05)},
                {"rotulo": "minha verba", "valor": int(eng.verba_contratacao(G, c, exig))}],
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
            falta_caixa=taxa > eng.verba_contratacao(G, c, minha),
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
            contexto="Contrato atual: %s a %s por mes; o mercado paga %s para o overall dele. Moral %d. Ele e %s."
                     % (eng.plural(j["contrato"], "ano"), eng.din(j["salario"]),
                        eng.din(eng.salario_de(j["ovr"])), j["moral"], _peso(G, j)),
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
        verba = eng.verba_contratacao(G, c, _inteiro(p.get("salario")))
        if passe > verba:
            raise ValueError(
                "Sua verba para contratar e %s: do caixa de %s, %s ficam reservados para "
                "%d meses de folha e custos (ja contando o salario dele). Venda alguem ou "
                "baixe a proposta." % (eng.din(verba), eng.din(c["dinheiro"]),
                                      eng.din(eng.reserva_custos(G, c, _inteiro(p.get("salario")))),
                                      eng.RESERVA_MESES))
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
        if j["clube"] is None:
            raise ValueError("%s esta sem clube: contrate como agente livre." % j["nome"])
        if j["clube"] == c["id"]:
            raise ValueError("%s ja e do seu clube." % j["nome"])
        taxa = eng.taxa_emprestimo(G, j, c)
        fatia = j["salario"] * int(eng.clamp(_inteiro(p.get("pct")), 0, 100)) // 100
        if taxa > eng.verba_contratacao(G, c, fatia):
            raise ValueError("A taxa de %s passa da sua verba para contratar (%s): o resto "
                             "do caixa esta reservado para a folha."
                             % (eng.din(taxa), eng.din(eng.verba_contratacao(G, c, fatia))))
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


ANOS_RENOVACAO_LOTE = 5     # o padrao da renovacao em lote: o prazo mais longo sai mais barato


def _motivo_sem_renovacao(G, c, j):
    if j["clube"] != c["id"]:
        return "nao e do seu clube"
    if j.get("dono"):
        return "emprestado: o contrato e do dono do passe"
    return None


def linhas_renovacao(ids, anos):
    """Renovar varios de uma vez: o que cada um pede nesse prazo e a folha.

    Uma mesa por jogador (tres tentativas, contraproposta) fica para quem quer
    pechinchar um nome. Aqui cada um renova pelo que pediu - pagar o pedido e
    aceito sempre -, com um prazo so para todos.
    """
    G = SESSAO.exigir()
    c = G["clubes"][G["clube"]]
    anos = int(eng.clamp(int(anos or ANOS_RENOVACAO_LOTE), 1, 5))
    linhas, soma = [], 0
    for pid in ids:
        j = G["jogadores"].get(pid)
        if not j:
            continue
        motivo = _motivo_sem_renovacao(G, c, j)
        pede = 0 if motivo else eng.pedido_renovacao_lote(G, j, anos)
        if not motivo:
            soma += pede - j["salario"]
        linhas.append({"id": j["id"], "nome": j["nome"], "pos": j["pos"], "ovr": j["ovr"],
                       "idade": j["idade"], "contrato": j["contrato"], "tag": dto._tag_ovr(j["ovr"]),
                       "salario": eng.din(j["salario"]), "pede": eng.din(pede) if pede else "-",
                       "diferenca": ("%s%s" % ("+" if pede >= j["salario"] else "-",
                                               eng.din(abs(pede - j["salario"])))) if pede else "-",
                       "motivo": motivo})
    folha = eng.folha_semanal(G, c)
    return {"anos": anos, "linhas": linhas,
            "folha_mes": eng.din(folha * 4), "folha_mes_depois": eng.din(folha * 4 + soma),
            "diferenca_mes": "%s%s" % ("+" if soma >= 0 else "-", eng.din(abs(soma)))}


def renovar_lote(ids, anos):
    """Fecha a renovacao de todos os validos pelo que pediram, no mesmo prazo."""
    G = SESSAO.exigir()
    c = G["clubes"][G["clube"]]
    anos = int(eng.clamp(int(anos or ANOS_RENOVACAO_LOTE), 1, 5))
    feitos, pulados = [], []
    for pid in ids:
        j = G["jogadores"].get(pid)
        if not j:
            continue
        motivo = _motivo_sem_renovacao(G, c, j)
        if motivo:
            pulados.append("%s (%s)" % (j["nome"], motivo))
            continue
        prop = eng.Proposta(jogador=j["id"], comprador=c["id"], anos=anos, tipo=eng.TIPO_RENOVACAO,
                            salario=eng.pedido_renovacao_lote(G, j, anos))
        if eng.avaliar_renovacao(G, prop).aceita:
            eng.fechar_renovacao(G, prop)
            feitos.append(j["nome"])
        else:
            pulados.append("%s (recusou)" % j["nome"])
    return feitos, pulados, anos


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
                         "salario": eng.din(j["salario"]), "clube": eng.nome_clube(G, cl["id"]),
                         "divisao": cl["divisao"], "reputacao": cl["reputacao"], "pct": pct,
                         "sobra": eng.din(j["salario"] * (100 - pct) // 100),
                         "alivio_num": int(j["salario"] * pct // 100),
                         "tag": dto._tag_ovr(j["ovr"])})
    return fora
