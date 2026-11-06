# -*- coding: utf-8 -*-
"""Goleiro nao se desgasta como jogador de linha (pedido do jogador, 2026-11-06).

O desgaste da tatica caia igual em todas as posicoes; o goleiro, que joga os
90 minutos de todo jogo e quase nunca e trocado, terminava com a pior condicao
do time (55 num Real Madrid em Pressao total, com a linha entre 64 e 89)."""

import os
import unittest

import apoio

eng = apoio.eng


class TestFadigaGoleiro(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(81)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Goleiro"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": clubes[0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_goleiro_gasta_bem_menos_que_a_linha(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        c["tatica"] = "Pressao total"
        esc = [p for p in eng.auto_escalar(G, c)]
        for pid in esc:
            G["jogadores"][pid]["cond"] = 100
        efeitos = {"fadiga": 0.0}
        eng.rng.seed(82)
        for _ in range(3):                      # tres jogos seguidos, sem recuperar
            eng._fadigar(G, esc, 90, c, efeitos)
        goleiro = next(p for p in esc if G["jogadores"][p]["pos"] == "GOL")
        linha = [G["jogadores"][p]["cond"] for p in esc if p != goleiro]
        cond_gol = G["jogadores"][goleiro]["cond"]
        gasto_gol = 100 - cond_gol
        gasto_linha = 100 - sum(linha) / len(linha)
        self.assertGreater(cond_gol, max(linha), "o goleiro termina mais inteiro que qualquer um da linha")
        self.assertLess(gasto_gol, 0.5 * gasto_linha)
        self.assertGreater(gasto_gol, 0, "a mentalidade ainda pesa um pouco para ele")
        self.assertEqual(eng.FADIGA_POSICAO["GOL"], 0.35)


if __name__ == "__main__":
    unittest.main()
