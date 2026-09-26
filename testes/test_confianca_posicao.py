# -*- coding: utf-8 -*-
"""Posicao x meta na confianca (print do testador, 26/09/2026): o lider, com
meta de top 16 e 83 de confianca, perdia "-1 dentro da meta". Dentro da meta a
tabela so ajuda, e o patamar sobe com a folga (75 no limite, 95 em 1o)."""

import os
import unittest

import apoio

eng = apoio.eng


class TestConfiancaPosicao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(81)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Posicao"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "B"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def na_posicao(self, pos):
        G = self.G
        c = G["clubes"][G["clube"]]
        liga = G["ligas"][c["divisao"]]
        liga["rodada"] = 10
        outros = [i for i in liga["times"] if i != c["id"]]
        ordem = outros[:pos - 1] + [c["id"]] + outros[pos - 1:]
        for k, cid in enumerate(ordem):
            t = liga["tabela"][str(cid)]
            t.update(p=100 - k, v=0, gp=0, gc=0, j=10)
        self.assertEqual(eng.posicao_na_liga(G, c["id"]), pos)

    def causas_da_semana(self, valor, pos, alvo=16):
        G = self.G
        G["fase"] = "liga"
        G["objetivo_alvo"] = alvo
        c = G["clubes"][G["clube"]]
        c["dinheiro"] = abs(c["dinheiro"]) + 1
        self.na_posicao(pos)
        eng.reiniciar_confianca(G, valor)
        eng.atualizar_confianca(G, [])
        hist = eng.confianca(G)["hist"]
        return hist[-1][2] if hist else []          # semana sem causa nao gera linha

    def test_lider_com_folga_nao_perde_ponto(self):
        causas = self.causas_da_semana(83, 1)
        self.assertFalse([c for c in causas if c[0] < 0], causas)
        self.assertTrue(any(c[0] > 0 and "dentro da meta" in c[1] for c in causas), causas)

    def test_dentro_da_meta_nunca_tira(self):
        for pos in (1, 5, 12, 16):
            causas = self.causas_da_semana(99, pos)
            self.assertFalse([c for c in causas if c[0] < 0 and "meta" in c[1]], (pos, causas))

    def test_fora_da_meta_continua_puxando_para_baixo(self):
        causas = self.causas_da_semana(80, 19, alvo=8)
        self.assertTrue(any(c[0] < 0 for c in causas), causas)


if __name__ == "__main__":
    unittest.main()
