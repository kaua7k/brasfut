# -*- coding: utf-8 -*-
"""Socios pagam mensalidade: por divisao, so no Brasil, com linha no extrato."""

import os
import unittest

import apoio

eng = apoio.eng


class TestSocios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(29)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Socios"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "B"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_mensalidade_por_divisao(self):
        for c in self.G["clubes"].values():
            if c["divisao"] in eng.MENSALIDADE_SOCIO:
                self.assertEqual(eng.socios_mensal(c), c["socios"] * eng.MENSALIDADE_SOCIO[c["divisao"]])
            else:
                self.assertEqual(eng.socios_mensal(c), 0, c["nome"])

    def test_peso_na_receita(self):
        # perto de 6% da receita do mes em cada serie: nem enfeite, nem fortuna
        for div in "ABCD":
            cls = [c for c in self.G["clubes"].values() if c["divisao"] == div]
            socios = sum(eng.socios_mensal(c) for c in cls)
            receita = sum(eng.receita_mensal(self.G, c) for c in cls)
            self.assertTrue(0.02 < socios / receita < 0.12, "%s: %.3f" % (div, socios / receita))

    def test_semana_lanca_no_extrato(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        antes = int(eng.stats_ano(G).get("extrato", {}).get("socios", 0))
        eng.economia_semanal(G)
        depois = int(eng.stats_ano(G).get("extrato", {}).get("socios", 0))
        self.assertEqual(depois - antes, eng.socios_mensal(c) // 4)
        self.assertGreater(depois, antes)

    def test_financas_mostra(self):
        fin = apoio.chamar("GET", "/api/financas")
        texto = repr(fin)
        self.assertIn("Socios", texto)
        orc = eng.orcamento_mensal(self.G, self.G["clubes"][self.G["clube"]])
        self.assertEqual(orc["saldo"], orc["tv"] + orc["bilheteria"] + orc["socios"]
                         - orc["folha"] - orc["estrutura"])


if __name__ == "__main__":
    unittest.main()
