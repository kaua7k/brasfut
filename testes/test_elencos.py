# -*- coding: utf-8 -*-
"""Os elencos brasileiros sao os feitos a mao (ELENCOS_EMBUTIDOS).

O importador chegou a gerar um bloco "brasil" no dados_mundo.py com o Santos
da API, e o mundo novo trocava o Santos original por ele. Nenhum dado de fora
pode mexer num clube brasileiro.
"""

import base64
import json
import os
import unittest
import zlib

import apoio

eng = apoio.eng


class TestElencosBrasileiros(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(9)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Elencos"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": clubes[0]["id"]})
        cls.G = apoio.SESSAO.G
        cls.original = json.loads(zlib.decompress(base64.b64decode(eng.ELENCOS_EMBUTIDOS)).decode("utf-8"))

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_mundo_novo_usa_o_elenco_original(self):
        G = self.G
        brasileiros = {c["nome"]: c for c in G["clubes"].values() if c["divisao"] in eng.DIVISOES_BR}
        for nome, lista in self.original.items():
            with self.subTest(clube=nome):
                c = brasileiros.get(nome)
                self.assertIsNotNone(c, "clube do arquivo original sumiu")
                no_jogo = {G["jogadores"][p]["nome"] for p in c["elenco"]}
                falta = [j["nome"] for j in lista if j["nome"] not in no_jogo]
                self.assertEqual(falta, [], "jogadores do elenco original fora do %s" % nome)

    def test_santos_e_o_original(self):
        G = self.G
        santos = next(c for c in G["clubes"].values() if c["nome"] == "Santos")
        nomes = {G["jogadores"][p]["nome"] for p in santos["elenco"]}
        self.assertIn("Neymar Jr", nomes)
        self.assertIn("Philippe Coutinho", nomes)
        # nomes completos da API nao entram
        self.assertNotIn("Benjamin Rollheiser", nomes)


if __name__ == "__main__":
    unittest.main()
