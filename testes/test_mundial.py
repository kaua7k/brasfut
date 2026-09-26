# -*- coding: utf-8 -*-
"""Copa Intercontinental (todo ano) e Mundial de Clubes de 32 (a cada 4 anos).

Intercontinental: logo depois das finais, o campeao da Libertadores pega o
melhor da MLS no Derby das Americas e quem passa decide com o campeao da
Champions. Mundial: 8 grupos de 4 em turno unico, os dois primeiros no
mata-mata, tudo em jogo unico e campo neutro. Decidido em 2026-09-26.
"""

import os
import unittest

import apoio

eng = apoio.eng


class TestMundial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(51)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Mundial"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_anos_de_mundial(self):
        self.assertFalse(eng.ano_de_mundial(2026))
        self.assertTrue(eng.ano_de_mundial(2029))
        self.assertFalse(eng.ano_de_mundial(2031))
        self.assertTrue(eng.ano_de_mundial(2033))
        self.assertNotIn("mundial", self.G["copas"])

    def test_intercontinental_derby_e_final(self):
        G = self.G
        cp = G["copas"]["intercontinental"]
        self.assertEqual(cp["vivos"], [])
        lib = G["copas"]["lib"]["vivos"][0]
        ucl = G["copas"]["ucl"]["vivos"][0]
        G["copas"]["lib"]["campeao"] = lib
        eng.preparar_intercontinental(G)
        mls = eng._lider(G, "USA")
        self.assertEqual(sorted(cp["vivos"]), sorted([lib, mls]))
        G["copas"]["ucl"]["campeao"] = ucl
        eng.entrar_campeao_europeu(G, cp)
        derby = eng.jogar_fase_copa(G, "intercontinental")
        self.assertEqual(len(derby), 1)
        self.assertIsNone(cp["campeao"], "o vencedor do Derby nao pode ser campeao")
        self.assertIn(ucl, cp["vivos"])
        self.assertEqual(len(cp["vivos"]), 2)
        eng.jogar_fase_copa(G, "intercontinental")
        self.assertIn(cp["campeao"], (ucl, derby[0]["venc"]))
        self.assertEqual(G["clubes"][cp["campeao"]]["titulos"].get("Copa Intercontinental"), 1)

    def test_mundial_de_32(self):
        G = self.G
        cp = eng.montar_mundial(G)
        self.assertEqual(len(cp["vivos"]), 32)
        self.assertEqual(len(set(cp["vivos"])), 32)
        self.assertEqual(len(cp["grupos"]), 8)
        for g in cp["grupos"]:
            self.assertEqual(len(g["rodadas"]), 3)
            jogos = {frozenset(par) for rodada in g["rodadas"] for par in rodada}
            self.assertEqual(len(jogos), 6, "turno unico: cada par uma vez")
        blocos = [G["clubes"][i] for i in cp["vivos"]]
        self.assertEqual(sum(1 for c in blocos if c["divisao"] == "USA"), 5)
        self.assertEqual(sum(1 for c in blocos if c["divisao"] == "SAU"), 5)
        self.assertEqual(sum(1 for c in blocos if c.get("europeu")), 14)
        # grupos -> 16 no mata-mata -> campeao em jogo unico
        G["copas"]["mundial"] = cp
        for _ in range(3):
            eng.jogar_rodada_grupos(G, "mundial")
        eng.fechar_grupos(G)
        self.assertEqual(len(cp["vivos"]), 16)
        while not cp["campeao"]:
            n = len(cp["vivos"])
            self.assertEqual(len(eng.jogar_fase_copa(G, "mundial")), n // 2)
        self.assertEqual(len(cp["historico"]), 4)
        del G["copas"]["mundial"]

    def test_virada_de_ano_de_mundial_monta_os_32(self):
        G = self.G
        temporada = G["temporada"]
        G["temporada"] = eng.ANO_MUNDIAL
        try:
            eng.montar_copas(G)
            self.assertIn("mundial", G["copas"])
            self.assertIn("intercontinental", G["copas"])
            self.assertEqual(G["copas"]["mundial"]["semanas_grupos"], eng.SEMANAS_MUNDIAL_GRUPOS)
        finally:
            G["temporada"] = temporada
            eng.montar_copas(G)


if __name__ == "__main__":
    unittest.main()
