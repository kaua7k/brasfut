# -*- coding: utf-8 -*-
"""Copas nacionais de fora, em segundo plano (decidido em 2026-09-26).

Uma copa por liga de fora (FA Cup, Copa del Rey, Copa Argentina...), jogo
unico, com os 16 ou 8 clubes de maior reputacao da liga. O titulo conta na
sala de trofeus e sai no feed do mundo, mas nao enche as noticias do clube.
"""

import os
import unittest

import apoio

eng = apoio.eng


def mundo_novo(semente):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(semente)
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Copas"})["clubes"]
    apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
    return apoio.SESSAO.G


class TestCopasNacionais(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        cls.G = mundo_novo(31)

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_uma_copa_por_liga_de_fora(self):
        G = self.G
        for codigo, nome in eng.COPAS_NACIONAIS.items():
            with self.subTest(pais=codigo):
                cp = G["copas"][eng.chave_copa_nac(codigo)]
                self.assertEqual(cp["nome"], nome)
                # outro teste pode ter jogado a copa: o tamanho e o da primeira fase
                hist = cp["historico"]
                n = len(hist[0]["jogos"]) * 2 if hist else len(cp["vivos"])
                self.assertIn(n, (8, 16))
                self.assertEqual(cp["semanas"], eng.semanas_copa_nac(codigo, n))
                # nenhuma rodada cai em semana de copa continental
                cont = set(eng.SEMANAS_GRUPOS + eng.SEMANAS_CONT + eng.SEMANAS_SULA
                           + eng.SEMANAS_FASE_LIGA + eng.SEMANAS_EURO)
                self.assertFalse(set(cp["semanas"]) & cont, codigo)
                liga = set(G["ligas"][codigo]["times"])
                self.assertTrue(set(cp["vivos"]) <= liga)
                if not hist:
                    self.assertEqual(len(cp["sorteio"]), n // 2)
                self.assertTrue(cp["fundo"] and cp["jogo_unico"])

    def test_copa_ate_o_campeao_em_jogo_unico(self):
        G = self.G
        chave = eng.chave_copa_nac("ENG")
        cp = G["copas"][chave]
        noticias_antes = list(G["noticias"])
        n = len(cp["vivos"])
        while not cp["campeao"]:
            vivos = len(cp["vivos"])
            res = eng.jogar_fase_copa(G, chave)
            self.assertEqual(len(res), vivos // 2, "fase de ida e volta numa copa de jogo unico")
        self.assertEqual(len(cp["historico"]), {16: 4, 8: 3}[n])
        campeao = G["clubes"][cp["campeao"]]
        self.assertEqual(campeao["titulos"].get(cp["nome"]), 1)
        self.assertTrue(any(cp["nome"] in f["texto"] for f in G["feed"]))
        self.assertEqual(G["noticias"], noticias_antes, "copa de fora encheu as noticias do clube")

    def test_aparece_na_tela_de_competicoes(self):
        tela = apoio.chamar("GET", "/api/competicoes")["tela"]
        nomes = [c["nome"] for c in tela["lista"]]
        self.assertIn("Copa del Rey", nomes)
        self.assertIn("Copa Argentina", nomes)

    def test_save_antigo_ganha_a_copa_se_ainda_da_tempo(self):
        G = mundo_novo(32)
        for k in list(G["copas"]):
            if k.startswith("cn_"):
                G["copas"].pop(k)
        G["fase"], G["semana"] = "liga", 3
        eng.migrar(G)
        self.assertIn(eng.chave_copa_nac("ESP"), G["copas"])
        for k in list(G["copas"]):
            if k.startswith("cn_"):
                G["copas"].pop(k)
        G["semana"] = 20            # a primeira fase ja passou: espera a virada
        eng.migrar(G)
        self.assertNotIn(eng.chave_copa_nac("ESP"), G["copas"])


if __name__ == "__main__":
    unittest.main()
