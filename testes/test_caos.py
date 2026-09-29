# -*- coding: utf-8 -*-
"""Modo caos: plantoes semanais e bombas-relogio. E o capitao, que vale em
todos os modos."""

import os
import unittest

import apoio

eng = apoio.eng
SESSAO = apoio.SESSAO


def mundo(seed, modo):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(seed)
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Caos", "opcoes": {"modo": modo}})["clubes"]
    apoio.chamar("POST", "/api/clube", {"id": next(c["id"] for c in clubes if c["nome"] == "Santos")})
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
        tipos = [p["tipo"] for p in G["caos"]["pendentes"] if p.get("clube") == c["id"]]
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
        bomba = next(p for p in G["caos"]["pendentes"] if p["tipo"] == "fair_play" and p["clube"] == c["id"])
        pontos = G["ligas"][c["divisao"]]["tabela"][str(c["id"])]["p"]
        ev = eng.ev_fair_play(G, bomba)
        self.assertEqual(ev["gravidade"], "grave")
        self.assertEqual(G["ligas"][c["divisao"]]["tabela"][str(c["id"])]["p"], pontos - 12)

    def test_bomba_explode_na_semana_certa(self):
        G = self.G
        c = self.clube("Sport")
        G["caos"]["pendentes"] = [{"tipo": "fair_play", "clube": c["id"], "valor": 10_000_000,
                                   "quando": eng.semana_absoluta(G) + 1}]
        eng.rng.seed(1)
        estado_antes = list(G["caos"]["pendentes"])
        # semana ainda nao chegou: nada
        eng.CHANCE_CAOS, chance = 0.0, eng.CHANCE_CAOS
        try:
            eng.eventos_caos(G)
            self.assertEqual(G["caos"]["pendentes"], estado_antes)
            G["semana_abs"] = eng.semana_absoluta(G) + 1
            plantao = eng.eventos_caos(G)
        finally:
            eng.CHANCE_CAOS = chance
        self.assertEqual([e["titulo"] for e in plantao], ["Pego no fair play financeiro"])
        self.assertEqual(G["caos"]["pendentes"], [])

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
        pendentes, G["caos"]["pendentes"] = G["caos"]["pendentes"], []
        try:
            r = apoio.avancar({"leve": True})
        finally:
            eng.CHANCE_CAOS = chance
            G["caos"]["pendentes"] = pendentes
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


if __name__ == "__main__":
    unittest.main()
