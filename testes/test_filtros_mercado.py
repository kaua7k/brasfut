# -*- coding: utf-8 -*-
"""Filtros novos do mercado: idade minima, teto (pelo olheiro), regiao e so a venda."""

import os
import unittest

import apoio
from api import mercado

eng = apoio.eng


class TestFiltrosMercado(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(1010)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Filtros"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": clubes[0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def busca(self, **f):
        tela = apoio.chamar("POST", "/api/mercado", {"aba": "compra", "filtros": f})["tela"]
        return [self.G["jogadores"][l["id"]] for l in tela["jogadores"]]

    def test_regiao(self):
        for reg in ("br", "sul", "europa"):
            achados = self.busca(regiao=reg)
            self.assertTrue(achados, reg)
            self.assertTrue(all(mercado.regiao_de(self.G, j) == reg for j in achados), reg)

    def test_idade_min_e_teto(self):
        achados = self.busca(idade_min=30)
        self.assertTrue(achados and all(j["idade"] >= 30 for j in achados))
        achados = self.busca(pot_min=85)
        self.assertTrue(achados and all(mercado.teto_visto(self.G, j) >= 85 for j in achados))

    def test_so_venda(self):
        alguem = next(j for j in self.G["jogadores"].values()
                      if j["clube"] not in (None, self.G["clube"]) and not j.get("dono")
                      and self.G["clubes"][j["clube"]]["divisao"] != "EX")
        alguem["listado"] = 1_000_000
        achados = self.busca(so_venda=True)
        self.assertTrue(achados and all(j["listado"] for j in achados))
        alguem["listado"] = 0

    def test_filtro_invalido_e_ignorado(self):
        self.assertTrue(self.busca(regiao="lua", idade_min="x"))


if __name__ == "__main__":
    unittest.main()
