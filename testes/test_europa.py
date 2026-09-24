# -*- coding: utf-8 -*-
"""Ligas europeias simuladas e elencos reais de fora (dados_mundo.py)."""

import os
import unittest

import apoio

eng = apoio.eng


@unittest.skipUnless(eng.mundo_embutido(), "sem dados_mundo.py")
class TestEuropa(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(8)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_mundo_novo_tem_as_ligas_e_elencos_reais(self):
        G = self.G
        self.assertEqual(set(G["ligas_ext"]), {"ENG", "ESP", "GER", "ITA", "FRA"})
        nomes = {G["jogadores"][p]["nome"] for c in G["clubes"].values() if c.get("liga_ext")
                 for p in c["elenco"]}
        self.assertIn("Erling Haaland", nomes)
        santos = next(c for c in G["clubes"].values() if c["nome"] == "Santos")
        self.assertIn("Neymar", {G["jogadores"][p]["nome"] for p in santos["elenco"]})
        # europeu nao entra nas copas sul-americanas nem no mercado
        for k in ("lib", "sul"):
            self.assertFalse(any(G["clubes"][i].get("liga_ext") for i in G["copas"][k]["vivos"]))

    def test_rodadas_andam_e_a_tela_mostra(self):
        for _ in range(3):
            apoio.avancar({"leve": True})
        liga = self.G["ligas_ext"]["ENG"]
        self.assertGreater(liga["rodada"], 0)
        tela = apoio.chamar("POST", "/api/competicoes", {"alvo": "ext:ENG"})["tela"]
        self.assertEqual(tela["detalhe"]["titulo"], "Premier League")
        self.assertEqual(len(tela["detalhe"]["linhas"]), 20)
        self.assertIn("ext:ENG", [i["id"] for i in tela["lista"]])
        self.assertEqual(apoio.chamar("POST", "/api/tabela", {"alvo": "ext:ESP"})["tela"]["alvo"], "ext:ESP")


@unittest.skipUnless(apoio.tem_save_real() and eng.mundo_embutido(), "sem save real ou dados_mundo.py")
class TestSaveAntigoGanhaEuropa(unittest.TestCase):
    def test_europa_entra_sem_mexer_no_brasil(self):
        hash_antes = apoio.hash_do_save_real()
        apoio.abrir_copia_do_save()
        G = apoio.SESSAO.G
        self.assertEqual(len(G["ligas_ext"]), 5)
        ids = [p for c in G["clubes"].values() for p in c["elenco"]]
        self.assertEqual(len(ids), len(set(ids)), "jogador em dois elencos")
        self.assertEqual(apoio.hash_do_save_real(), hash_antes)
