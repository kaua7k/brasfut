# -*- coding: utf-8 -*-
"""Contratacoes fantasmas e a folha da IA (feedback de 26/09/2026, item 3 e 8).

Medido em 12 temporadas: craque europeu livre (overall 89-91) caia na Serie D
pelo mercado do overall (R$ 2 a 3 mi por mes com receita de R$ 700 mil), e em
cinco anos a divisao inteira estava no vermelho. Tres portas faziam isso:
repor_elencos (sem ninguem na faixa pegava o MELHOR livre), contratar_livres_ia
(verba conferida com o salario antigo) e o livre ao acaso de mercado_ia.
Agora todas exigem que a pedida caiba na folha (cabe_na_folha).
"""

import os
import unittest

import apoio

eng = apoio.eng


class TestFolhaIA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(101)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Folha"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def craque_livre(self, pos="ATA"):
        G = self.G
        j = eng.novo_jogador(G, pos, 90, {x["nome"] for x in G["jogadores"].values()}, idade=25)
        j["clube"] = None
        G["livres"].append(j["id"])
        j.update(pos=pos, ovr=90, pot=90, idade=25)
        j["salario"] = eng.salario_de(90)
        # ele e o unico livre da posicao
        for pid in G["livres"]:
            if pid != j["id"] and G["jogadores"][pid]["pos"] == pos:
                G["jogadores"][pid]["pos"] = "GOL" if pos != "GOL" else "ZAG"
        return j

    def serie_d(self):
        return next(c for c in self.G["clubes"].values() if c["divisao"] == "D")

    def test_craque_nao_cabe_na_folha_da_serie_d(self):
        c = self.serie_d()
        self.assertFalse(eng.cabe_na_folha(self.G, c, eng.salario_de(90)))
        self.assertTrue(eng.cabe_na_folha(self.G, c, eng.salario_de(45)))

    def test_virada_nao_traz_craque_para_a_serie_d(self):
        j = self.craque_livre()
        c = self.serie_d()
        nivel = 24 + c["reputacao"] * 0.55
        self.assertFalse(eng.contratar_livre_ia(self.G, c, "ATA", nivel))
        self.assertIsNone(j["clube"])

    def test_contratacao_semanal_respeita_a_folha(self):
        G = self.G
        j = self.craque_livre("MEI")
        for _ in range(3):
            eng.contratar_livres_ia(G)
        if j["clube"] is not None:
            c = G["clubes"][j["clube"]]
            self.assertNotEqual(c["divisao"], "D")
            self.assertTrue(eng.cabe_na_folha(G, c, 0))

    def test_livre_ao_acaso_do_mercado_ia_respeita_a_folha(self):
        G = self.G
        j = self.craque_livre("LAT")
        G["livres"] = [j["id"]]
        for c in G["clubes"].values():
            if c["divisao"] == "D":
                while len(c["elenco"]) > 22:
                    c["elenco"].pop()
        for _ in range(10):
            eng.mercado_ia(G)
        if j["clube"] is not None:
            self.assertNotEqual(G["clubes"][j["clube"]]["divisao"], "D")


if __name__ == "__main__":
    unittest.main()
