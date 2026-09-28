# -*- coding: utf-8 -*-
"""Tela do clube: historia real ate 2025 somada ao que ele ganha no jogo."""

import os
import unittest

import apoio
import dados_clubes

eng = apoio.eng
SESSAO = apoio.SESSAO


class TestClube(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(414)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Clube"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": next(c["id"] for c in clubes if c["nome"] == "Santos")})
        cls.G = SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def sala(self, tela):
        return {t["nome"]: t for t in tela["sala"]}

    def test_dados_batem_com_os_clubes_do_jogo(self):
        nomes = {c[0] for c in eng.CLUBES_A + eng.CLUBES_B + eng.CLUBES_C + eng.CLUBES_D}
        for nome, h in dados_clubes.HISTORIA.items():
            self.assertIn(nome, nomes)
            for comp, anos in h.get("titulos", []):
                self.assertTrue(anos and all(1900 < a <= 2025 for a in anos), (nome, comp))

    def test_historia_real_do_meu_clube(self):
        tela = apoio.chamar("GET", "/api/clube/ficha")["tela"]
        self.assertTrue(tela["meu"])
        sala = self.sala(tela)
        self.assertEqual(sala["Libertadores"]["qtd"], 3)
        self.assertIn("2011", sala["Libertadores"]["anos"])
        self.assertIn("Campeonato Paulista", sala)
        self.assertNotIn("Paulista", sala)
        self.assertTrue(sala["Campeonato Paulista"]["anos"].startswith("22 ate 2025"))
        self.assertIn({"nome": "Apelido", "valor": "Peixe"}, tela["info"])

    def test_titulo_do_jogo_entra_com_o_ano(self):
        c = self.G["clubes"][self.G["clube"]]
        antes = self.sala(apoio.chamar("GET", "/api/clube/ficha")["tela"])["Copa do Brasil"]["qtd"]
        eng.dar_titulo(self.G, c, "Copa do Brasil")
        tela = apoio.chamar("GET", "/api/clube/ficha")["tela"]
        t = self.sala(tela)["Copa do Brasil"]
        self.assertEqual(t["qtd"], antes + 1)
        self.assertTrue(t["no_jogo"])
        self.assertTrue(t["anos"].endswith(str(self.G["temporada"])))
        self.assertNotIn("no jogo", t["anos"])
        self.assertIn({"nome": "Copa do Brasil", "temporada": int(self.G["temporada"])}, tela["no_jogo"])

    def test_save_antigo_sem_data(self):
        outro = next(c for c in self.G["clubes"].values() if c["nome"] == "Mirassol")
        outro["titulos"]["Copa do Brasil"] = 2          # como vinha antes do titulos_hist
        tela = apoio.chamar("POST", "/api/clube/ficha", {"id": outro["id"]})["tela"]
        self.assertFalse(tela["meu"])
        self.assertEqual(self.sala(tela)["Copa do Brasil"]["anos"], "2 titulos")

    def test_estadual_do_jogo_soma_no_real_e_data_vem_da_carreira(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        # como no save antigo: contagem sem titulos_hist, ano so na sala do treinador
        antes = self.sala(apoio.chamar("GET", "/api/clube/ficha")["tela"])["Campeonato Paulista"]["qtd"]
        c["titulos"]["Campeonato Paulista"] = c["titulos"].get("Campeonato Paulista", 0) + 1
        eng.passagem_atual(G)["titulos"].append({"nome": "Campeonato Paulista", "temporada": 2030})
        t = self.sala(apoio.chamar("GET", "/api/clube/ficha")["tela"])["Campeonato Paulista"]
        self.assertEqual(t["qtd"], antes + 1)
        self.assertEqual(t["anos"], "22 ate 2025, 2030")

    def test_clube_inexistente_e_400(self):
        with self.assertRaises(Exception):
            apoio.chamar("POST", "/api/clube/ficha", {"id": 999999})


if __name__ == "__main__":
    unittest.main()
