# -*- coding: utf-8 -*-
"""Ir para o jogo: pula semana sem jogo do meu clube e para ANTES do jogo."""

import os
import unittest

import apoio

eng = apoio.eng


class TestAteOJogo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(701)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Jogo",
                                                    "opcoes": {"sem_demissao": True}})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_com_jogo_na_semana_nao_anda_e_o_topo_mostra_o_adversario(self):
        G = self.G
        semana = G["semana"]
        cab = apoio.chamar("GET", "/api/painel")["painel"]["cabecalho"]
        self.assertIsNotNone(cab["jogo_semana"])
        self.assertTrue(cab["jogo_semana"]["adversario"])
        r = apoio.chamar("POST", "/api/avancar/ate-o-jogo", {})
        self.assertEqual(r["semanas"], 0)
        self.assertEqual(G["semana"], semana, "parou antes do jogo, sem jogar")
        self.assertEqual(r["cabecalho"]["jogo_semana"], cab["jogo_semana"])

    def test_pula_semanas_sem_jogo_e_para_na_do_jogo(self):
        G = self.G
        real = eng.jogos_da_semana
        semana = G["semana"]
        alvo = semana + 2
        # as duas proximas semanas ficam sem jogo do meu clube
        eng.jogos_da_semana = lambda G_, cid: [] if (cid == G_["clube"] and G_["semana"] < alvo) else real(G_, cid)
        try:
            r = apoio.chamar("POST", "/api/avancar/ate-o-jogo", {})
        finally:
            eng.jogos_da_semana = real
        self.assertEqual(r["semanas"], 2)
        self.assertEqual(G["semana"], alvo)
        self.assertTrue("Agora e jogo" in r["recado"] or "O jogo e nesta semana" in r["recado"], r["recado"])
        self.assertIsNotNone(r["cabecalho"]["jogo_semana"])

    def test_fora_da_temporada_recusa(self):
        G = self.G
        fase = G["fase"]
        G["fase"] = "entretemporada"
        try:
            apoio.chamar("POST", "/api/avancar/ate-o-jogo", {}, status=400)
        finally:
            G["fase"] = fase


if __name__ == "__main__":
    unittest.main()
