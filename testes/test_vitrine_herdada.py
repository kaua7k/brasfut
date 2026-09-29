# -*- coding: utf-8 -*-
"""O clube do treinador comeca sem as marcas que a IA tinha posto antes da
escolha (a venda, cedivel): a vitrine e decisao dele (2026-09-29)."""

import os
import unittest

import apoio

eng = apoio.eng


class TestVitrineHerdada(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(1111)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Vitrine"})["clubes"]
        G = apoio.SESSAO._pendente_novo
        # escolhe um clube que a IA marcou
        marcado = next(c for c in clubes if any(
            G["jogadores"][p]["listado"] or G["jogadores"][p]["emp_listado"]
            for p in G["clubes"][c["id"]]["elenco"]))
        apoio.chamar("POST", "/api/clube", {"id": marcado["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def limpo(self, c):
        return not any(self.G["jogadores"][p]["listado"] or self.G["jogadores"][p]["emp_listado"]
                       for p in c["elenco"])

    def test_clube_escolhido_comeca_limpo(self):
        self.assertTrue(self.limpo(self.G["clubes"][self.G["clube"]]))

    def test_trocar_de_clube_tambem_limpa(self):
        G = self.G
        novo = next(c for c in G["clubes"].values() if c["id"] != G["clube"] and c["divisao"] == "B"
                    and not self.limpo(c)) if any(not self.limpo(c) for c in G["clubes"].values()
                                                   if c["divisao"] == "B") else None
        if novo is None:
            self.skipTest("nenhum clube da B marcado neste mundo")
        eng.assumir_clube(G, novo["id"], "teste")
        self.assertTrue(self.limpo(novo))


if __name__ == "__main__":
    unittest.main()
