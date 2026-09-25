# -*- coding: utf-8 -*-
"""Instrucao condicional pre-jogo (Onda 2, item 4).

"Se perdendo a partir dos 71', Ofensivo": a regra e conferida nas paradas que
a partida ja tem (46' e 71'), vale enquanto o placar pedir e o clube sai do
jogo com a mentalidade com que entrou. A maquina tem regra fixa aos 71':
perdendo sobe um degrau, vencendo desce um.
"""

import os
import unittest

import apoio

eng = apoio.eng


def mundo_novo(semente):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(semente)
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Condicional"})["clubes"]
    apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
    return apoio.SESSAO.G


class TestCondicional(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        cls.G = mundo_novo(61)

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def setUp(self):
        self.c = self.G["clubes"][self.G["clube"]]
        self.c["condicionais"] = {}
        self.c["tatica"] = "Equilibrado"

    def rival(self):
        return next(c for c in self.G["clubes"].values()
                    if c["divisao"] == "A" and c["id"] != self.G["clube"])

    def test_regra_do_meu_clube_vale_do_minuto_em_diante(self):
        G, c = self.G, self.c
        ok, _ = eng.definir_condicional(G, c, "perdendo", 71, "Ofensivo")
        self.assertTrue(ok)
        self.assertEqual(eng.tatica_condicional(G, c, "Equilibrado", 0, 1, 46), "Equilibrado")
        self.assertEqual(eng.tatica_condicional(G, c, "Equilibrado", 0, 1, 71), "Ofensivo")
        # sem regra para vencendo e empate nunca troca
        self.assertEqual(eng.tatica_condicional(G, c, "Equilibrado", 2, 1, 71), "Equilibrado")
        self.assertEqual(eng.tatica_condicional(G, c, "Equilibrado", 1, 1, 71), "Equilibrado")

    def test_maquina_sobe_ou_desce_um_degrau_aos_71(self):
        G, r = self.G, self.rival()
        self.assertEqual(eng.tatica_condicional(G, r, "Equilibrado", 0, 1, 46), "Equilibrado")
        self.assertEqual(eng.tatica_condicional(G, r, "Equilibrado", 0, 1, 71), "Ofensivo")
        self.assertEqual(eng.tatica_condicional(G, r, "Equilibrado", 1, 0, 71), "Contra-ataque")
        self.assertEqual(eng.tatica_condicional(G, r, "Pressao total", 0, 2, 71), "Pressao total")
        self.assertEqual(eng.tatica_condicional(G, r, "Retranca", 3, 0, 71), "Retranca")

    def test_regra_invalida_e_recusada_e_minuto_vazio_apaga(self):
        G, c = self.G, self.c
        self.assertFalse(eng.definir_condicional(G, c, "empatando", 71, "Ofensivo")[0])
        self.assertFalse(eng.definir_condicional(G, c, "perdendo", 60, "Ofensivo")[0])
        self.assertFalse(eng.definir_condicional(G, c, "perdendo", 71, "Tudo ao ataque")[0])
        eng.definir_condicional(G, c, "vencendo", 46, "Retranca")
        self.assertEqual(eng.condicionais_de(c)["vencendo"], {"minuto": 46, "tatica": "Retranca"})
        eng.definir_condicional(G, c, "vencendo", None, None)
        self.assertIsNone(eng.condicionais_de(c)["vencendo"])
        # save antigo, lixo no campo: le como sem regra
        c["condicionais"] = {"perdendo": {"minuto": "71", "tatica": 3}}
        self.assertIsNone(eng.condicionais_de(c)["perdendo"])

    def test_partida_troca_registra_e_devolve_a_mentalidade(self):
        G, c = self.G, self.c
        eng.definir_condicional(G, c, "perdendo", 46, "Pressao total")
        eng.definir_condicional(G, c, "vencendo", 46, "Retranca")
        r = self.rival()
        tatica_rival = r["tatica"]
        visto = None
        for _ in range(40):
            res = eng.simular(G, c["id"], r["id"], "liga")
            self.assertEqual(c["tatica"], "Equilibrado")
            self.assertEqual(r["tatica"], tatica_rival)
            minhas = [x for x in res["instrucoes"] if x[1] == 0]
            if minhas:
                visto = minhas[0]
                break
        self.assertIsNotNone(visto, "em 40 jogos o placar nunca pediu a regra")
        minuto, _lado, tatica, motivo = visto
        self.assertIn(minuto, eng.MINUTOS_CONDICIONAL)
        self.assertEqual(tatica, {"perdendo": "Pressao total", "vencendo": "Retranca"}[motivo])

    def test_api_grava_e_recusa(self):
        tela = apoio.chamar("POST", "/api/escalacao/condicional",
                            {"condicao": "perdendo", "minuto": 71, "tatica": "Ofensivo"})["tela"]
        regras = {x["condicao"]: x for x in tela["condicionais"]["regras"]}
        self.assertEqual((regras["perdendo"]["minuto"], regras["perdendo"]["tatica"]), (71, "Ofensivo"))
        self.assertIsNone(regras["vencendo"]["minuto"])
        apoio.chamar("POST", "/api/escalacao/condicional",
                     {"condicao": "perdendo", "minuto": 60, "tatica": "Ofensivo"}, status=400)
        apoio.chamar("POST", "/api/escalacao/condicional",
                     {"condicao": "perdendo", "minuto": "71", "tatica": "Ofensivo"}, status=400)


if __name__ == "__main__":
    unittest.main()
