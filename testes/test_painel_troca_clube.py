# -*- coding: utf-8 -*-
"""Trocou de clube: o bloco de resultados do Painel (ultima partida, placar da
semana, ultimos 5 e o alerta de fase) passa a ser do clube novo.

Os historicos que alimentam esse bloco (historico_meus, ultimos_meus,
placar_hist) sao do tecnico, nao do clube: sem filtro, o Painel do clube novo
mostrava o jogo e a forma do antigo."""

import os
import unittest

import apoio

eng = apoio.eng


class TestPainelTrocaDeClube(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(606)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "PainelTroca"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": clubes[0]["id"]})
        G = cls.G = apoio.SESSAO.G
        cls.antigo = G["clube"]
        for _ in range(3):
            apoio.avancar()
        # um clube da Serie B: nao cruzou com o antigo nessas semanas
        cls.novo = next(c["id"] for c in clubes if c["divisao"] == "B")
        eng.assumir_clube(G, cls.novo, "proposta")

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def resultados(self):
        return apoio.chamar("GET", "/api/painel")["painel"]["resultados"]

    def test_logo_depois_da_troca_nada_do_clube_antigo(self):
        r = self.resultados()
        nome_antigo = self.G["clubes"][self.antigo]["nome"]
        for p in r["partidas"]:
            self.assertNotIn(nome_antigo, p["times"])
        self.assertEqual(r["partidas"], [])
        self.assertEqual(r["placares"], [])
        self.assertEqual(r["forma"], [])
        self.assertIsNone(r["alerta"])

    def test_zz_depois_de_jogar_so_aparece_o_clube_novo(self):
        apoio.avancar()
        G = self.G
        r = self.resultados()
        novo = G["clubes"][self.novo]["nome"]
        self.assertTrue(r["partidas"])
        for reg in eng.historico_do_clube(G):
            self.assertIn(self.novo, (reg["casa"], reg["fora"]))
        self.assertLessEqual(len(r["forma"]), len(eng.historico_do_clube(G)))
        self.assertTrue(r["forma"])
        for p in r["placares"]:
            self.assertNotEqual(p["adversario"], novo)
        for jogo in eng.resultados_da_semana(G):
            self.assertIn(self.novo, (jogo["casa"], jogo["fora"]))


if __name__ == "__main__":
    unittest.main()
