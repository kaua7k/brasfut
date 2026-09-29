# -*- coding: utf-8 -*-
"""Guia de estatisticas do campeonato."""

import os
import unittest

import apoio

eng = apoio.eng


class TestEstatisticas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(1212)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Estat"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": clubes[0]["id"]})
        cls.G = apoio.SESSAO.G
        for _ in range(4):
            apoio.avancar({"leve": True})

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_rankings_ordenados_e_da_liga(self):
        t = apoio.chamar("GET", "/api/estatisticas")["tela"]
        rk = {r["id"]: r for r in t["rankings"]}
        for chave in ("gols", "assist", "participa", "nota", "amarelos", "ataque", "defesa"):
            self.assertIn(chave, rk)
        gols = [i["num"] for i in rk["gols"]["itens"]]
        self.assertTrue(gols and gols == sorted(gols, reverse=True))
        defesa = [i["num"] for i in rk["defesa"]["itens"]]
        self.assertEqual(defesa, sorted(defesa))
        liga = self.G["ligas"][self.G["clubes"][self.G["clube"]]["divisao"]]
        for i in rk["gols"]["itens"]:
            self.assertIn(self.G["jogadores"][i["id"]]["clube"], liga["times"])

    def test_outra_liga(self):
        t = apoio.chamar("POST", "/api/estatisticas", {"alvo": "liga:ENG"})["tela"]
        self.assertEqual(t["alvo"], "liga:ENG")
        ids = [i["id"] for i in t["rankings"][0]["itens"]]
        self.assertTrue(all(self.G["clubes"][self.G["jogadores"][p]["clube"]]["divisao"] == "ENG" for p in ids))


if __name__ == "__main__":
    unittest.main()
