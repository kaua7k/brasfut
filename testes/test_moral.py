# -*- coding: utf-8 -*-
"""Moral com causa e classico com peso (Onda 3).

Toda mudanca de moral do meu elenco guarda a causa, e a ficha mostra as
ultimas. Vitoria ou derrota em classico mexe o dobro na moral. O rng e
consumido igual com ou sem classico.
"""

import os
import unittest

import apoio

eng = apoio.eng
SESSAO = apoio.SESSAO


class TestMoral(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(313)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Moral"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def meus(self, n=5):
        c = self.G["clubes"][self.G["clube"]]
        return [p for p in c["elenco"] if not self.G["jogadores"][p].get("dono")][:n]

    def moral_depois(self, pro, contra, classico, semente=5):
        for p in self.meus():
            self.G["jogadores"][p]["moral"] = 60
            self.G["jogadores"][p].pop("moral_hist", None)
        eng.rng.seed(semente)
        eng.aplicar_moral(self.G, self.meus(), pro, contra, "Rival", classico)
        estado = eng.rng.getstate()
        return [self.G["jogadores"][p]["moral"] for p in self.meus()], estado

    def test_classico_pesa_o_dobro(self):
        normal, rng_n = self.moral_depois(2, 0, False)
        classico, rng_c = self.moral_depois(2, 0, True)
        self.assertEqual(rng_n, rng_c, "classico mudou o consumo do rng")
        for a, b in zip(normal, classico):
            self.assertGreater(b, a)
        normal, _ = self.moral_depois(0, 2, False)
        classico, _ = self.moral_depois(0, 2, True)
        for a, b in zip(normal, classico):
            self.assertLess(b, a)
        # empate em classico nao pesa mais
        self.assertEqual(self.moral_depois(1, 1, False)[0], self.moral_depois(1, 1, True)[0])

    def test_causa_anotada_so_no_meu_clube(self):
        self.moral_depois(0, 3, True)
        j = self.G["jogadores"][self.meus()[0]]
        sem, delta, causa = j["moral_hist"][-1]
        self.assertLess(delta, 0)
        self.assertIn("classico contra o Rival", causa)
        self.assertIn("0 x 3", causa)
        outro = next(c for c in self.G["clubes"].values()
                     if c["id"] != self.G["clube"] and c["divisao"] == "A")
        pid = outro["elenco"][0]
        eng.aplicar_moral(self.G, [pid], 3, 0, "Nos", False)
        self.assertNotIn("moral_hist", self.G["jogadores"][pid])

    def test_historico_curto(self):
        j = self.G["jogadores"][self.meus()[0]]
        j["moral"] = 50
        j.pop("moral_hist", None)
        for i in range(eng.MORAL_HIST + 3):
            eng.mexer_moral(self.G, j, 1, "causa %d" % i)
        self.assertEqual(len(j["moral_hist"]), eng.MORAL_HIST)
        self.assertEqual(j["moral_hist"][-1][2], "causa %d" % (eng.MORAL_HIST + 2))
        # teto: moral no maximo nao anota causa de +0
        j["moral"] = 100
        n = len(j["moral_hist"])
        eng.mexer_moral(self.G, j, 5, "nada muda")
        self.assertEqual(len(j["moral_hist"]), n)

    def test_ficha_explica_a_moral(self):
        pid = self.meus()[0]
        self.moral_depois(3, 1, True)
        ficha = apoio.chamar("POST", "/api/ficha", {"id": pid})["ficha"]
        self.assertTrue(ficha["moral_causas"])
        self.assertIn("classico", ficha["moral_causas"][0]["texto"])
        self.assertEqual(ficha["moral_causas"][0]["estado"], "ok")


if __name__ == "__main__":
    unittest.main()
