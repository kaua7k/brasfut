# -*- coding: utf-8 -*-
"""A coluna Situacao do Elenco virou duas: Jogo (lesao, suspensao, pendurado)
e Mercado (contrato e vitrine), que antes se misturavam."""

import os
import unittest

import apoio

eng = apoio.eng


class TestSituacao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(808)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Situacao"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": clubes[0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def linhas(self):
        return {j["id"]: j for j in apoio.chamar("GET", "/api/elenco")["tela"]["jogadores"]}

    def test_jogo_e_mercado_separados(self):
        c = self.G["clubes"][self.G["clube"]]
        a, b = [self.G["jogadores"][p] for p in c["elenco"][:2]]
        a["amar"] = {"liga": 2}
        a["listado"] = 5_000_000
        b["lesao"] = 3
        l = self.linhas()
        self.assertEqual(l[a["id"]]["jogo"], "pendurado (liga)")
        self.assertTrue(l[a["id"]]["mercado"].startswith("a venda por"))
        self.assertEqual(l[b["id"]]["jogo"], "lesionado, 3 semanas")
        a["amar"], a["listado"], b["lesao"] = {}, 0, 0


if __name__ == "__main__":
    unittest.main()
