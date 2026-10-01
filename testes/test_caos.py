# -*- coding: utf-8 -*-
"""Modo caos: plantoes semanais e bombas-relogio. E o capitao, que vale em
todos os modos."""

import os
import unittest

import apoio

eng = apoio.eng
SESSAO = apoio.SESSAO


def mundo(seed, modo, clube="Santos"):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(seed)
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Caos", "opcoes": {"modo": modo}})["clubes"]
    apoio.chamar("POST", "/api/clube", {"id": next(c["id"] for c in clubes if c["nome"] == clube)})
    return SESSAO.G


class TestCapitao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        cls.G = mundo(701, "classico")

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_todo_clube_tem_capitao_e_da_para_trocar(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        cap = eng.capitao_de(G, c)
        self.assertIn(cap, c["elenco"])
        outro = next(p for p in c["elenco"] if p != cap and not eng.da_base(G["jogadores"][p]))
        r = apoio.chamar("POST", "/api/capitao", {"id": outro})
        self.assertTrue(r["ficha"]["capitao"])
        self.assertEqual(eng.capitao_de(G, c), outro)
        linhas = {j["id"]: j for j in apoio.chamar("GET", "/api/elenco")["tela"]["jogadores"]}
        self.assertTrue(linhas[outro]["capitao"])
        self.assertFalse(linhas[cap]["capitao"])
        # jogador de outro clube nao
        alheio = next(p for p in G["clubes"][next(i for i in G["clubes"] if i != G["clube"])]["elenco"])
        apoio.chamar("POST", "/api/capitao", {"id": alheio}, status=400)

    def test_capitao_segura_a_moral_na_derrota(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        cap = eng.capitao_de(G, c)
        pros = [p for p in c["elenco"] if p != cap and not eng.da_base(G["jogadores"][p])]
        esc, banco = [cap] + pros[:10], pros[10]

        def derrota(capitao):
            for p in c["elenco"]:
                G["jogadores"][p]["moral"] = 65
            c["capitao"] = capitao
            eng.rng.seed(42)
            eng.aplicar_moral(G, esc, 0, 2, rival="X")
            return sum(G["jogadores"][p]["moral"] for p in esc[1:])

        # mesmo sorteio; so muda se quem usa a bracadeira esta em campo
        self.assertGreater(derrota(cap), derrota(banco))
        c["capitao"] = cap

    def test_modo_classico_nao_tem_plantao(self):
        G = self.G
        estado = eng.rng.getstate()
        self.assertEqual(eng.eventos_caos(G), [])
        self.assertEqual(eng.rng.getstate(), estado)
        r = apoio.avancar({"leve": True})
        self.assertEqual(r.get("plantao"), [])


class TestCaos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        cls.G = mundo(702, "caos")

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def clube(self, nome):
        return next(c for c in self.G["clubes"].values() if c["nome"] == nome)

    def test_todo_evento_roda_sem_quebrar(self):
        G = self.G
        G["semana"] = 30
        for ident, _peso, func in eng.EVENTOS_CAOS:
            ev = func(G)
            if ev:
                self.assertTrue(ev["titulo"] and ev["texto"], ident)
                self.assertIn(ev["gravidade"], ("leve", "grave", "tragedia"))
        # o mundo continua jogavel
        for c in G["clubes"].values():
            for p in c["elenco"] + c.get("escalacao", []):
                self.assertIn(p, G["jogadores"])

    def test_doping_turbina_e_depois_cassa_o_titulo(self):
        G = self.G
        c = self.clube("Fortaleza")
        c.pop("doping", None)
        pros = [j for j in eng._pros(G, c)]
        antes = {j["id"]: j["ovr"] for j in pros}
        eng.rng.seed(5)
        G["semana"] = 20
        # forca o alvo
        orig = eng._alvo
        eng._alvo = lambda G_, cands, meu_pode=True: c
        try:
            ev = eng.ev_doping(G)
        finally:
            eng._alvo = orig
        self.assertIsNotNone(ev)
        self.assertTrue(all(G["jogadores"][p]["ovr"] > o for p, o in antes.items()))
        tipos = [p["tipo"] for p in eng.estado_caos(G)["pendentes"] if p.get("clube") == c["id"]]
        self.assertIn("doping_fim", tipos)
        self.assertIn("doping_pego", tipos)
        eng.ev_doping_fim(G, {"clube": c["id"]})
        self.assertEqual({p: G["jogadores"][p]["ovr"] for p in antes}, antes)
        # ganhou um titulo naquele ano e foi pego depois
        temporada = c["doping"]["temporada"]
        eng.dar_titulo(G, c, "Copa do Brasil")
        c["titulos_hist"][-1]["temporada"] = temporada
        pontos = G["ligas"][c["divisao"]]["tabela"][str(c["id"])]["p"]
        ev = eng.ev_doping_pego(G, {"clube": c["id"], "temporada": temporada})
        self.assertIn("Copa do Brasil", ev["texto"])
        self.assertFalse(any(t["temporada"] == temporada for t in c["titulos_hist"]))
        self.assertEqual(G["ligas"][c["divisao"]]["tabela"][str(c["id"])]["p"], pontos - 15)

    def test_fair_play_pune_quem_recebeu_dinheiro_sujo(self):
        G = self.G
        c = self.clube("Bahia")
        caixa = c["dinheiro"]
        orig = eng._alvo
        eng._alvo = lambda G_, cands, meu_pode=True: c
        try:
            eng.ev_dinheiro_sujo(G)
        finally:
            eng._alvo = orig
        self.assertGreater(c["dinheiro"], caixa)
        bomba = next(p for p in eng.estado_caos(G)["pendentes"] if p["tipo"] == "fair_play" and p["clube"] == c["id"])
        pontos = G["ligas"][c["divisao"]]["tabela"][str(c["id"])]["p"]
        ev = eng.ev_fair_play(G, bomba)
        self.assertEqual(ev["gravidade"], "grave")
        self.assertEqual(G["ligas"][c["divisao"]]["tabela"][str(c["id"])]["p"], pontos - 12)

    def test_bomba_explode_na_semana_certa(self):
        G = self.G
        c = self.clube("Sport")
        eng.estado_caos(G)["pendentes"] = [{"tipo": "fair_play", "clube": c["id"], "valor": 10_000_000,
                                   "quando": eng.semana_absoluta(G) + 1}]
        eng.rng.seed(1)
        estado_antes = list(eng.estado_caos(G)["pendentes"])
        # semana ainda nao chegou: nada
        eng.CHANCE_CAOS, chance = 0.0, eng.CHANCE_CAOS
        try:
            eng.eventos_caos(G)
            self.assertEqual(eng.estado_caos(G)["pendentes"], estado_antes)
            G["semana_abs"] = eng.semana_absoluta(G) + 1
            plantao = eng.eventos_caos(G)
        finally:
            eng.CHANCE_CAOS = chance
        self.assertEqual([e["titulo"] for e in plantao], ["Pego no fair play financeiro"])
        self.assertEqual(eng.estado_caos(G)["pendentes"], [])

    def test_capitao_preso_sai_e_volta_depois_da_pena(self):
        G = self.G
        c = self.clube("Gremio")
        cap = eng.capitao_de(G, c)
        orig = eng._alvo
        eng._alvo = lambda G_, cands, meu_pode=True: c
        try:
            ev = eng.ev_capitao_preso(G)
        finally:
            eng._alvo = orig
        self.assertIn(G["jogadores"][cap]["nome"], ev["texto"])
        self.assertNotIn(cap, c["elenco"])
        self.assertNotIn(cap, G["livres"])
        self.assertNotEqual(eng.capitao_de(G, c), cap)
        preso = next(p for p in G["caos"]["presos"] if p["id"] == cap)
        temporada = G["temporada"]
        G["temporada"] = preso["volta"]
        eng.soltar_presos(G)
        G["temporada"] = temporada
        self.assertIn(cap, G["livres"])

    def test_aviao_deixa_so_a_base(self):
        G = self.G
        G["semana"] = 30
        G["caos"]["usados"].pop("aviao", None)
        antes = {cid: set(G["clubes"][cid]["elenco"]) for cid in G["clubes"]}
        ev = eng.ev_aviao(G)
        self.assertEqual(ev["gravidade"], "tragedia")
        c = next(cl for cl in G["clubes"].values() if cl["nome"] == ev["clube"])
        self.assertNotEqual(c["id"], G["clube"])
        velhos = {p for p in antes[c["id"]] if p not in c["elenco"]}
        self.assertTrue(velhos)
        self.assertTrue(all(p not in G["jogadores"] for p in velhos))
        self.assertGreaterEqual(len(c["elenco"]), sum(eng.ELENCO_PADRAO.values()))
        # uma vez por save: o sorteio marca o uso, e o segundo nao acontece
        G["caos"]["usados"]["aviao"] = 1
        self.assertIsNone(eng.ev_aviao(G))

    def test_remover_limpa_acertos_e_ofertas(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        pid = c["elenco"][-1]
        G["agendadas"].append({"jogador": pid, "de": c["id"], "para": c["id"], "tipo": "compra"})
        G.setdefault("ofertas", {"stamp": "", "itens": []})["itens"].append([pid, c["id"], 1000])
        eng._remover_do_mundo(G, pid)
        self.assertFalse(any(a["jogador"] == pid for a in G["agendadas"]))
        self.assertFalse(any(it[0] == pid for it in G["ofertas"]["itens"]))

    def test_avancar_devolve_o_plantao(self):
        eng.CHANCE_CAOS, chance = 1.0, eng.CHANCE_CAOS
        try:
            r = apoio.avancar({"leve": True})
        finally:
            eng.CHANCE_CAOS = chance
        self.assertTrue(r["plantao"])
        feed = [f for f in self.G["feed"] if f["tipo"] == "caos"]
        self.assertTrue(feed)


class TestCaosVariedade(unittest.TestCase):
    """Pedido de 2026-09-29: niveis de frequencia, sem repetir o mesmo evento
    em sequencia, e mais eventos e textos."""

    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(703)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Caos Nivel",
                                                    "opcoes": {"modo": "caos", "caos_nivel": "caotico"}})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": next(c["id"] for c in clubes if c["nome"] == "Santos")})
        cls.G = SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_nivel_fica_no_save_e_muda_a_chance(self):
        G = self.G
        self.assertEqual(G["opcoes"]["caos_nivel"], "caotico")
        self.assertEqual(eng.resumo_save(G)["caos_nivel"], "caotico")
        chances = {}
        for nivel in eng.NIVEIS_CAOS:
            G["opcoes"]["caos_nivel"] = nivel
            chances[nivel] = eng.chances_caos(G)
        G["opcoes"]["caos_nivel"] = "caotico"
        self.assertLess(chances["calmo"][0], chances["normal"][0])
        self.assertLess(chances["normal"][0], chances["caotico"][0])
        self.assertLess(chances["calmo"][1], chances["caotico"][1])
        self.assertEqual(chances["normal"], (eng.CHANCE_CAOS, eng.CHANCE_CAOS_DUPLO))
        self.assertTrue(all(0 < a <= 1 and 0 < b <= 1 for a, b in chances.values()))
        # nivel desconhecido (save editado a mao) cai no normal
        self.assertEqual(eng.definir_opcoes_carreira({}, {"modo": "caos", "caos_nivel": "x"})["caos_nivel"],
                         "normal")

    def test_mesmo_evento_nao_repete_na_janela(self):
        G = self.G
        est = eng.estado_caos(G)
        est["pendentes"] = []
        eng.CHANCE_CAOS, chance = 1.0, eng.CHANCE_CAOS
        vistos = []
        try:
            eng.rng.seed(11)
            for _ in range(40):
                G["semana_abs"] = eng.semana_absoluta(G) + 1
                vistos.append([(e["id"], eng.semana_absoluta(G)) for e in eng.eventos_caos(G) if "id" in e])
        finally:
            eng.CHANCE_CAOS = chance
        ultima = {}
        for semana in vistos:
            for ident, quando in semana:
                if ident in ultima:
                    self.assertGreaterEqual(quando - ultima[ident], eng.JANELA_REPETE_CAOS, ident)
                ultima[ident] = quando
        self.assertGreater(len(ultima), 15, "40 semanas no caotico deviam variar bastante")

    def test_eventos_novos_rodam(self):
        G = self.G
        novos = ("cachorro", "reality", "hacker", "vaquinha", "pacto", "enchente",
                 "portoes_fechados", "tatuagem", "vidente", "vazamento", "churrasco")
        tabela = {e[0]: e[2] for e in eng.EVENTOS_CAOS}
        self.assertEqual(len(tabela), len(eng.EVENTOS_CAOS), "id repetido na tabela")
        self.assertGreaterEqual(len(tabela), 36)
        rodaram = 0
        meu = G["clubes"][G["clube"]]
        for ident in novos:
            # vaquinha so vale para caixa negativo
            if ident == "vaquinha":
                meu["dinheiro"], caixa = -1_000_000, meu["dinheiro"]
            ev = tabela[ident](G)
            if ident == "vaquinha":
                meu["dinheiro"] += caixa + 1_000_000
            if ev:
                rodaram += 1
                self.assertTrue(ev["titulo"] and ev["texto"], ident)
                self.assertNotRegex(ev["texto"], r"%[sd(]", ident)
        self.assertGreaterEqual(rodaram, len(novos) - 1)

    def test_plantao_velho_nao_volta_no_avanco(self):
        # bug de 2026-09-29: semana sem sorteio devolvia o plantao da anterior
        G = self.G
        eng.estado_caos(G)["plantao"] = [{"titulo": "Velho", "texto": "x", "meu": True}]
        eng.CHANCE_CAOS, chance = 0.0, eng.CHANCE_CAOS
        pendentes, eng.estado_caos(G)["pendentes"] = eng.estado_caos(G)["pendentes"], []
        try:
            r = apoio.avancar({"leve": True})
        finally:
            eng.CHANCE_CAOS = chance
            eng.estado_caos(G)["pendentes"] = pendentes
        self.assertEqual(r.get("plantao"), [])

    def test_sem_de_o_nos_textos(self):
        G = self.G
        for semente in range(20):
            eng.rng.seed(semente)
            ev = eng.ev_virose(G)
            if ev:
                self.assertNotRegex(ev["texto"], r"\bde (o|a|os|as) ", ev["texto"])

    def test_texto_varia(self):
        G = self.G
        textos = set()
        for semente in range(12):
            eng.rng.seed(semente)
            ev = eng.ev_invasao(G) or eng.ev_benzedeira(G)
            if ev:
                textos.add(ev["texto"].split(G["clubes"][G["clube"]]["nome"])[0][:25])
        self.assertGreater(len(textos), 1)


NOVOS_2026_10_01 = ("escolta", "faixa_ultras", "fundo_estrangeiro", "agente", "visto", "naming",
                    "fornecedor", "var_aposta", "oferta_louca", "gramado")

NOVOS_AMIGOS = ("furia_mascote", "arqueologia", "vicio_virtual", "clausula_canina", "revelacao_divina",
                "intoxicacao_jantar", "sabotagem_textil", "abducao", "pix_misterioso", "vazio_mental",
                "var_2047", "estadio_sumiu", "arquibancada", "roupeiro", "chuva_notas", "eleicao",
                "torcida_sabe", "piloto", "jogo_infinito", "chuva_peixe", "gramado_leilao",
                "organizada_compra", "mega_sena", "capivaras", "cripto", "aula_samba")


def rodar_todos(G, sementes=range(6)):
    """Cada evento, varias sementes. Devolve [(ident, evento)] dos que dispararam."""
    G["semana"] = 30
    saida = []
    for ident, _peso, func in eng.EVENTOS_CAOS:
        for semente in sementes:
            eng.rng.seed(semente * 31 + len(ident))
            eng.estado_caos(G)["usados"].pop("aviao", None)
            eng.estado_caos(G)["usados"].pop("meteoro", None)
            # o teste libera o estadio que a rodada anterior interditou
            for c in G["clubes"].values():
                if c.get("cap_original"):
                    c["capacidade"] = c.pop("cap_original")
            # vaquinha e greve so valem para caixa negativo
            meu = G["clubes"][G["clube"]]
            caixa = meu["dinheiro"]
            if ident in ("vaquinha", "greve"):
                meu["dinheiro"] = -1_000_000
            ev = func(G)
            if ident in ("vaquinha", "greve"):
                meu["dinheiro"] = caixa
            if ev:
                saida.append((ident, ev))
    return saida


class TestCaosLigaDeFora(unittest.TestCase):
    """Pedido de 2026-10-01: os plantoes valem na liga que o jogador treina,
    nao so no Brasileirao."""

    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        cls.G = mundo(710, "caos", "Boca Juniors")

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_liga_e_a_do_clube_do_jogador(self):
        G = self.G
        meu = G["clubes"][G["clube"]]
        self.assertEqual(meu["divisao"], "ARG")
        self.assertFalse(eng._eh_br(G))
        todos = eng._liga(G)
        self.assertTrue(todos)
        self.assertTrue(all(c["divisao"] == "ARG" for c in todos))
        topo, base = eng._liga(G, "topo"), eng._liga(G, "base")
        self.assertEqual(sorted(c["id"] for c in topo + base), sorted(c["id"] for c in todos))
        self.assertGreaterEqual(min(c["reputacao"] for c in topo), max(c["reputacao"] for c in base))
        self.assertEqual(len(eng._liga(G, "nao_fundo")), len(todos))

    def test_todo_evento_cai_so_na_liga_do_jogador(self):
        G = self.G
        nomes_liga = {c["nome"] for c in G["clubes"].values() if c["divisao"] == "ARG"}
        nomes_br = {c["nome"] for c in G["clubes"].values() if c["divisao"] in eng.DIVISOES_BR}
        antes = {c["id"]: (c["dinheiro"], c["capacidade"], len(c["elenco"]), c["reputacao"])
                 for c in G["clubes"].values() if c["divisao"] in eng.DIVISOES_BR}
        disparou = rodar_todos(G)
        self.assertGreater(len({i for i, _ in disparou}), 30, "a maioria dos eventos devia rodar na Argentina")
        for ident, ev in disparou:
            self.assertTrue(ev["titulo"] and ev["texto"], ident)
            if ev["clube"]:
                self.assertIn(ev["clube"], nomes_liga, ident)
                self.assertNotIn(ev["clube"], nomes_br - nomes_liga, ident)
        # nenhum clube brasileiro foi tocado
        for cid, antes_c in antes.items():
            c = G["clubes"][cid]
            self.assertEqual((c["dinheiro"], c["capacidade"], len(c["elenco"]), c["reputacao"]), antes_c,
                             c["nome"])

    def test_eventos_novos_rodam_sem_sobra_de_formato(self):
        G = self.G
        tabela = {e[0]: e[2] for e in eng.EVENTOS_CAOS}
        self.assertEqual(len(tabela), len(eng.EVENTOS_CAOS), "id repetido na tabela")
        for ident in NOVOS_2026_10_01 + NOVOS_AMIGOS:
            self.assertIn(ident, tabela)
            peso = next(e[1] for e in eng.EVENTOS_CAOS if e[0] == ident)
            self.assertTrue(2 <= peso <= 4, ident)
        rodou = {i for i, _ in rodar_todos(G, range(10))}
        for ident in NOVOS_2026_10_01 + NOVOS_AMIGOS:
            self.assertIn(ident, rodou, ident + " nunca disparou em 10 sementes")

    def test_nenhum_texto_sobra_formato_nem_de_o(self):
        G = self.G
        for ident, ev in rodar_todos(G, range(8)):
            self.assertNotRegex(ev["texto"], r"%[sd(]", ident)
            self.assertNotIn("%%", ev["texto"], ident)
            self.assertNotRegex(ev["texto"], r"\b(de|em|por) (o|a|os|as) ", "%s: %s" % (ident, ev["texto"]))

    def test_dinheiro_acompanha_a_economia_da_liga(self):
        G = self.G
        arg = G["clubes"][G["clube"]]
        br = next(c for c in G["clubes"].values() if c["divisao"] == "A")
        ing = next(c for c in G["clubes"].values() if c["divisao"] == "ENG")
        self.assertEqual(eng._gr(G, br, 40_000_000), 40_000_000)
        self.assertEqual(eng._escala_din(G, br), 1.0)
        self.assertGreater(eng._gr(G, ing, 40_000_000), 40_000_000)
        self.assertLess(eng._gr(G, arg, 40_000_000), eng._gr(G, ing, 40_000_000))
        ven = next(c for c in G["clubes"].values() if c["divisao"] == "VEN")
        self.assertGreaterEqual(eng._escala_din(G, ven), 0.25)
        self.assertLess(eng._escala_din(G, ven), 1.0)

    def test_aviao_derruba_o_lider_da_liga_de_fora(self):
        G = self.G
        G["semana"] = 30
        eng.estado_caos(G)["usados"].pop("aviao", None)
        lider = G["clubes"][eng.classificacao(G, G["ligas"]["ARG"])[0]]
        if lider["id"] == G["clube"]:
            self.skipTest("o lider e o clube do jogador")
        ev = eng.ev_aviao(G)
        self.assertEqual(ev["clube"], lider["nome"])
        self.assertIn("Liga Profesional", ev["texto"])
        eng.estado_caos(G)["usados"]["aviao"] = 1

    def test_bombas_funcionam_em_clube_de_fora(self):
        G = self.G
        c = next(x for x in G["clubes"].values() if x["divisao"] == "ARG" and x["id"] != G["clube"])
        c.pop("doping", None)
        orig = eng._alvo
        eng._alvo = lambda G_, cands, meu_pode=True: c
        try:
            G["semana"] = 20
            ev = eng.ev_doping(G)
            self.assertIsNotNone(ev)
            temporada = c["doping"]["temporada"]
            eng.dar_titulo(G, c, "Copa Argentina")
            c["titulos_hist"][-1]["temporada"] = temporada
            pontos = G["ligas"]["ARG"]["tabela"][str(c["id"])]["p"]
            ev = eng.ev_doping_pego(G, {"clube": c["id"], "temporada": temporada})
            self.assertIn("Copa Argentina", ev["texto"])
            self.assertFalse(any(t["temporada"] == temporada for t in c["titulos_hist"]))
            self.assertEqual(G["ligas"]["ARG"]["tabela"][str(c["id"])]["p"], pontos - 15)
            # dinheiro sujo e fair play
            caixa = c["dinheiro"]
            eng.ev_dinheiro_sujo(G)
            self.assertGreater(c["dinheiro"], caixa)
            bomba = next(p for p in eng.estado_caos(G)["pendentes"] if p["tipo"] == "fair_play" and p["clube"] == c["id"])
            pontos = G["ligas"]["ARG"]["tabela"][str(c["id"])]["p"]
            ev = eng.ev_fair_play(G, bomba)
            self.assertEqual(ev["gravidade"], "grave")
            self.assertEqual(G["ligas"]["ARG"]["tabela"][str(c["id"])]["p"], pontos - 12)
        finally:
            eng._alvo = orig

    def test_semana_do_caos_so_sorteia_na_liga(self):
        G = self.G
        nomes_liga = {c["nome"] for c in G["clubes"].values() if c["divisao"] == "ARG"}
        eng.estado_caos(G)["pendentes"] = []
        eng.estado_caos(G)["recentes"] = {}
        eng.CHANCE_CAOS, chance = 1.0, eng.CHANCE_CAOS
        vistos = 0
        try:
            eng.rng.seed(21)
            for _ in range(40):
                G["semana_abs"] = eng.semana_absoluta(G) + 1
                G["semana"] = 30
                for ev in eng.eventos_caos(G):
                    vistos += 1
                    if ev["clube"]:
                        self.assertIn(ev["clube"], nomes_liga, ev["titulo"])
        finally:
            eng.CHANCE_CAOS = chance
        self.assertGreater(vistos, 20)

    def test_classico_com_clube_de_fora_nao_usa_rng(self):
        G = mundo(713, "classico", "Boca Juniors")
        estado = eng.rng.getstate()
        self.assertEqual(eng.eventos_caos(G), [])
        self.assertEqual(eng.rng.getstate(), estado)
        type(self).G = mundo(710, "caos", "Boca Juniors")


class TestCaosBrasilContinua(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        cls.G = mundo(712, "caos", "Santos")

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_carreira_brasileira_so_cai_no_brasil(self):
        G = self.G
        self.assertTrue(eng._eh_br(G))
        self.assertEqual(len(eng._liga(G)), 80)
        self.assertEqual({c["divisao"] for c in eng._liga(G, "topo")}, {"A", "B"})
        self.assertEqual({c["divisao"] for c in eng._liga(G, "base")}, {"C", "D"})
        self.assertEqual({c["divisao"] for c in eng._liga(G, "nao_fundo")}, {"A", "B", "C"})
        nomes_br = {c["nome"] for c in G["clubes"].values() if c["divisao"] in eng.DIVISOES_BR}
        nomes_fora = {c["nome"] for c in G["clubes"].values() if c["divisao"] not in eng.DIVISOES_BR} - nomes_br
        antes = {c["id"]: (c["dinheiro"], c["capacidade"], len(c["elenco"]))
                 for c in G["clubes"].values() if c["divisao"] not in eng.DIVISOES_BR}
        disparou = rodar_todos(G)
        self.assertGreater(len({i for i, _ in disparou}), 30)
        for ident, ev in disparou:
            if ev["clube"]:
                self.assertIn(ev["clube"], nomes_br, ident)
                self.assertNotIn(ev["clube"], nomes_fora, ident)
        for cid, antes_c in antes.items():
            c = G["clubes"][cid]
            self.assertEqual((c["dinheiro"], c["capacidade"], len(c["elenco"])), antes_c, c["nome"])

    def test_novos_eventos_tambem_rodam_no_brasil(self):
        rodou = {i for i, _ in rodar_todos(self.G, range(10))}
        for ident in NOVOS_2026_10_01 + NOVOS_AMIGOS:
            self.assertIn(ident, rodou, ident)

    def test_valores_no_brasil_seguem_os_de_sempre(self):
        G = self.G
        meu = G["clubes"][G["clube"]]
        self.assertEqual(eng._gr(G, meu, 40_000_000), 40_000_000)
        G["semana"] = 30
        eng.estado_caos(G)["usados"].pop("aviao", None)
        ev = eng.ev_aviao(G)
        self.assertRegex(ev["texto"], r"lider da Serie [ABCD]\b")
        self.assertRegex(ev["texto"], r"R\$ 40(,0)? mi")
        eng.estado_caos(G)["usados"]["aviao"] = 1


class TestPlantoesDosAmigos(unittest.TestCase):
    """Plantoes sugeridos pelos amigos do Kaua (2026-10-01): as mecanicas
    mais delicadas (vaga de elenco, jogador temporario, posicao, pontos)."""

    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        cls.G = mundo(720, "caos", "Santos")

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def setUp(self):
        G = self.G
        G["semana"] = 30
        for c in G["clubes"].values():
            if c.get("cap_original"):
                c["capacidade"] = c.pop("cap_original")
            c.pop("vagas_perdidas", None)
        eng.estado_caos(G)["pendentes"] = []
        # o sorteio de clube cai sempre no do jogador
        antes = eng.CHANCE_MEU_CLUBE
        eng.CHANCE_MEU_CLUBE = 1.1
        self.addCleanup(setattr, eng, "CHANCE_MEU_CLUBE", antes)

    def meu(self):
        return self.G["clubes"][self.G["clube"]]

    def test_clausula_canina_tira_uma_vaga_do_limite(self):
        G, c = self.G, self.meu()
        eng.rng.seed(1)
        self.assertEqual(eng.limite_elenco(c), eng.LIMITE_ELENCO)
        ev = eng.ev_clausula_canina(G)
        self.assertEqual(ev["clube"], c["nome"])
        self.assertEqual(eng.limite_elenco(c), eng.LIMITE_ELENCO - 1)
        self.assertTrue(all(j["moral"] == 100 for j in eng._pros(G, c)))
        # o teto vale de verdade: com o elenco no novo limite, nao cabe mais ninguem
        guardado = list(c["elenco"])
        try:
            c["elenco"] = guardado[:eng.limite_elenco(c)] + [-1000 - i for i in range(
                max(0, eng.limite_elenco(c) - len(guardado)))]
            self.assertEqual(len(c["elenco"]), eng.LIMITE_ELENCO - 1)
            self.assertTrue(eng.elenco_cheio(G, c))
            self.assertEqual(eng.vagas_elenco(G, c), 0)
            self.assertIn("%d de %d" % (len(c["elenco"]), eng.LIMITE_ELENCO - 1), eng.recado_elenco_cheio(c))
            c["elenco"].pop()
            self.assertFalse(eng.elenco_cheio(G, c))
            self.assertEqual(eng.vagas_elenco(G, c), 1)
        finally:
            c["elenco"] = guardado

    def test_clausula_canina_tem_teto_de_tres_vagas(self):
        G = self.G
        for x in eng._liga(G):
            x["vagas_perdidas"] = 3
        self.assertIsNone(eng.ev_clausula_canina(G))

    def test_roupeiro_entra_e_sai_depois_de_seis_semanas(self):
        G, c = self.G, self.meu()
        eng.rng.seed(2)
        n = len(c["elenco"])
        ev = eng.ev_roupeiro(G)
        self.assertEqual(ev["clube"], c["nome"])
        self.assertEqual(len(c["elenco"]), n + 1)
        pid = c["elenco"][-1]
        self.assertEqual(G["jogadores"][pid]["idade"], 63)
        pend = [p for p in eng.estado_caos(G)["pendentes"] if p["tipo"] == "roupeiro_sai"]
        self.assertEqual(len(pend), 1)
        self.assertEqual(pend[0]["quando"] - eng.semana_absoluta(G), 6)
        eng.BOMBAS_CAOS["roupeiro_sai"](G, pend[0])
        self.assertNotIn(pid, c["elenco"])
        self.assertNotIn(pid, G["jogadores"])
        self.assertEqual(len(c["elenco"]), n)

    def test_roupeiro_sai_pela_semana_do_caos(self):
        G, c = self.G, self.meu()
        eng.rng.seed(3)
        eng.ev_roupeiro(G)
        pid = c["elenco"][-1]
        G["semana_abs"] = eng.semana_absoluta(G) + 7
        eng.CHANCE_CAOS, chance = 0.0, eng.CHANCE_CAOS
        try:
            eng.eventos_caos(G)
        finally:
            eng.CHANCE_CAOS = chance
        self.assertNotIn(pid, G["jogadores"])
        self.assertEqual(eng.estado_caos(G)["pendentes"], [])

    def test_vicio_virtual_capitao_vira_meia_e_volta(self):
        G, c = self.G, self.meu()
        achou = None
        for semente in range(60):
            eng.rng.seed(semente)
            eng.estado_caos(G)["pendentes"] = []
            for j in eng._pros(G, c):
                j["lesao"] = 0
            cap = G["jogadores"][eng.capitao_de(G, c)]
            pos = cap["pos"]
            eng.ev_vicio_virtual(G)
            pend = [p for p in eng.estado_caos(G)["pendentes"] if p["tipo"] == "pos_volta"]
            if pend:
                achou = (cap, pos, pend[0])
                break
            if cap["pos"] != pos:
                cap["pos"] = pos
        self.assertIsNotNone(achou, "nenhuma semente deu a versao do capitao")
        cap, pos, bomba = achou
        self.assertEqual(cap["pos"], "MEI")
        self.assertGreaterEqual(cap["lesao"], 4)
        self.assertEqual(bomba["quando"] - eng.semana_absoluta(G), 4)
        eng.BOMBAS_CAOS["pos_volta"](G, bomba)
        self.assertEqual(cap["pos"], pos)

    def test_vicio_virtual_goleiro_e_capitao_ficam_fora(self):
        G, c = self.G, self.meu()
        for semente in range(60):
            eng.rng.seed(semente)
            eng.estado_caos(G)["pendentes"] = []
            for j in eng._pros(G, c):
                j["lesao"] = 0
            cap = G["jogadores"][eng.capitao_de(G, c)]
            pos = cap["pos"]
            eng.ev_vicio_virtual(G)
            if not eng.estado_caos(G)["pendentes"]:
                gol = eng._melhor_da_pos(G, c, "GOL")
                self.assertGreaterEqual(gol["lesao"], 1)
                self.assertGreaterEqual(cap["lesao"], 1)
                self.assertEqual(cap["pos"], pos)
                return
            cap["pos"] = pos
        self.fail("nenhuma semente deu a versao do goleiro")

    def test_pontos_da_tabela(self):
        G, c = self.G, self.meu()
        t = G["ligas"][c["divisao"]]["tabela"][str(c["id"])]
        base = t["p"]
        eng.rng.seed(4)
        self.assertTrue(eng.ev_var_2047(G))
        self.assertEqual(t["p"], base + 3)
        self.assertTrue(eng.ev_jogo_infinito(G))
        self.assertEqual(t["p"], base + 6)
        self.assertTrue(eng.ev_chuva_peixe(G))
        self.assertEqual(t["p"], base + 3)
        self.setUp()
        self.assertTrue(eng.ev_aula_samba(G))
        self.assertEqual(t["p"], base + 1)
        self.assertTrue(eng.ev_furia_mascote(G))
        self.assertEqual(t["p"], base - 2)

    def test_estadio_interditado_e_devolvido(self):
        G, c = self.G, self.meu()
        cap = c["capacidade"]
        self.assertTrue(eng.ev_arqueologia(G))
        self.assertEqual(c["capacidade"], 1000)
        pend = [p for p in eng.estado_caos(G)["pendentes"] if p["tipo"] == "estadio_volta"]
        self.assertEqual(pend[0]["quando"] - eng.semana_absoluta(G), 15)
        eng.BOMBAS_CAOS["estadio_volta"](G, pend[0])
        self.assertEqual(c["capacidade"], cap)

    def test_revelacao_divina_zagueiro_vira_meia(self):
        G, c = self.G, self.meu()
        zag = eng._melhor_da_pos(G, c, "ZAG", 50)
        ovr = zag["ovr"]
        self.assertTrue(eng.ev_revelacao_divina(G))
        self.assertEqual(zag["pos"], "MEI")
        self.assertEqual(zag["ovr"], ovr - 3)

    def test_abducao_sobe_o_overall(self):
        G, c = self.G, self.meu()
        ata = eng._melhor_da_pos(G, c, "ATA", 55)
        ovr = ata["ovr"]
        self.assertTrue(eng.ev_abducao(G))
        self.assertGreater(ata["ovr"], ovr)
        self.assertLessEqual(ata["ovr"], 93)
        self.assertGreaterEqual(ata["lesao"], 1)

    def test_reputacao_fica_entre_5_e_95(self):
        c = self.meu()
        c["reputacao"] = 10
        eng._rep(c, -15)
        self.assertEqual(c["reputacao"], 5)
        eng._rep(c, 500)
        self.assertEqual(c["reputacao"], 95)

    def test_organizada_derruba_confianca_e_moral(self):
        G, c = self.G, self.meu()
        conf = eng.confianca(G)
        conf["valor"] = 60
        caixa = c["dinheiro"]
        ev = eng.ev_organizada_compra(G)
        self.assertEqual(ev["clube"], c["nome"])
        self.assertEqual(conf["valor"], 52)
        self.assertGreater(c["dinheiro"], caixa)
        self.assertTrue(all(j["moral"] <= 75 for j in eng._pros(G, c)))

    def test_intoxicacao_tira_cinco_titulares_por_uma_semana(self):
        G, c = self.G, self.meu()
        for j in eng._pros(G, c):
            j["lesao"] = 0
        self.assertTrue(eng.ev_intoxicacao_jantar(G))
        self.assertEqual(sum(1 for j in eng._pros(G, c) if j["lesao"] == 1), 5)

    def test_goleiro_artilheiro_tem_variacoes_novas(self):
        G = self.G
        textos = set()
        for semente in range(120):
            eng.rng.seed(semente)
            ev = eng.ev_goleiro(G)
            if ev:
                textos.add(ev["texto"].split("goleiro")[0][:18])
        self.assertGreaterEqual(len(textos), 5)


if __name__ == "__main__":
    unittest.main()
