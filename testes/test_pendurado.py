# -*- coding: utf-8 -*-
"""Aviso de pendurado menos intrusivo (item 13, 26/09/2026): tres ou mais
pendurados no XI nao viram mais faixa "ESCALACAO COM RESSALVA"; o jogador so
leva a marca "pendurado", sem cor de alerta."""

import os
import unittest

import apoio

eng = apoio.eng


class TestPendurado(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(121)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Pendurado"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_pendurados_nao_viram_alerta(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        for pid in c["elenco"]:
            j = G["jogadores"][pid]
            j["cond"], j["lesao"] = 100, 0
            j["amar"]["liga"] = 2
        d = eng.diagnostico_escalacao(G, c)
        self.assertGreaterEqual(len(d["pendurados"]), 3)
        self.assertNotIn("pendurado", (d.get("titulo") or "").lower())
        painel = apoio.chamar("GET", "/api/painel")["painel"]
        xi = painel["escalacao"]["jogadores"]
        marcados = [j for j in xi if j["obs"] == "pendurado"]
        self.assertTrue(marcados, "a marca discreta sumiu")
        self.assertTrue(all(j["estado"] == "ok" for j in marcados))
        for pid in c["elenco"]:
            G["jogadores"][pid]["amar"]["liga"] = 0


if __name__ == "__main__":
    unittest.main()
