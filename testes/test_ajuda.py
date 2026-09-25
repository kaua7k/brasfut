# -*- coding: utf-8 -*-
"""Ajuda e boas-vindas na web (antes so existiam na janela tkinter).

O texto vem da API e os numeros saem do motor: se a janela ou a confianca
mudarem, a ajuda muda junto.
"""

import os
import unittest

import apoio

eng = apoio.eng


class TestAjuda(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(11)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Ajuda"})["clubes"]
        cls.cid = clubes[0]["id"]
        apoio.chamar("POST", "/api/clube", {"id": cls.cid})

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_ajuda_cobre_todas_as_telas_do_menu(self):
        r = apoio.chamar("GET", "/api/ajuda")
        from api import dto
        nomes = [t["nome"] for t in r["ajuda"]["telas"]]
        self.assertEqual(nomes, [n for _, n, _ in dto.MENU])

    def test_numeros_vem_do_motor(self):
        termos = {t["nome"]: t["texto"] for t in apoio.chamar("GET", "/api/ajuda")["ajuda"]["termos"]}
        self.assertIn("1 a 4 e 19 a 22", termos["Janela"])
        self.assertIn(str(eng.CONFIANCA_AVISO), termos["Confianca"])
        self.assertIn(str(eng.CONFIANCA_DEMISSAO), termos["Confianca"])

    def test_boas_vindas_do_clube_escolhido(self):
        bv = apoio.chamar("GET", "/api/ajuda")["boas_vindas"]
        G = apoio.SESSAO.G
        self.assertEqual(bv["clube"], G["clubes"][self.cid]["nome"])
        self.assertEqual(bv["objetivo"], G["objetivo"])
        self.assertEqual(len(bv["passos"]), 3)


if __name__ == "__main__":
    unittest.main()
