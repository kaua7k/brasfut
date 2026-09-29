# -*- coding: utf-8 -*-
"""Quem manda proposta por jogador seu tem que querer ele no elenco: clube
grande nao sonda reserva de Serie D (2026-09-29)."""

import os
import unittest

import apoio

eng = apoio.eng


class TestCompradores(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(4)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Compradores"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "D"][2]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_quem_compra_tem_elenco_do_nivel_dele(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        for pid in c["elenco"]:
            j = G["jogadores"][pid]
            for cl in eng._compradores_possiveis(G, j, 1):
                self.assertTrue(j["ovr"] >= eng.media_elenco(G, cl) - eng.NIVEL_COMPRADOR
                                or (j["idade"] <= 21 and j["pot"] >= eng.media_elenco(G, cl) + 2),
                                (j["nome"], cl["nome"]))

    def test_gigante_nao_sonda_jogador_fraco(self):
        G = self.G
        real = next(cl for cl in G["clubes"].values() if cl["nome"] == "Real Madrid")
        fraco = min((G["jogadores"][p] for p in G["clubes"][G["clube"]]["elenco"]), key=lambda j: j["ovr"])
        self.assertFalse(eng.serve_para(G, fraco, real))

    def test_promessa_vale_pelo_teto(self):
        G = self.G
        cl = next(c for c in G["clubes"].values() if c["divisao"] == "A")
        j = dict(G["jogadores"][G["clubes"][G["clube"]]["elenco"][0]])
        j.update(ovr=int(eng.media_elenco(G, cl)) - 15, idade=19, pot=int(eng.media_elenco(G, cl)) + 5)
        self.assertTrue(eng.serve_para(G, j, cl))


if __name__ == "__main__":
    unittest.main()
