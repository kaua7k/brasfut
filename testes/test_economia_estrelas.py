# -*- coding: utf-8 -*-
"""Salario de estrela achatado, patrocinio pela marca e migracao do save
antigo (decidido em 2026-09-28)."""

import os
import unittest

import apoio

eng = apoio.eng
SESSAO = apoio.SESSAO


class TestEconomiaEstrelas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(515)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Estrelas"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": next(c["id"] for c in clubes if c["nome"] == "Santos")})
        cls.G = SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_curva_achatada_so_acima_de_75(self):
        for ovr in (50, 60, 70, 75):
            self.assertEqual(eng.salario_de(ovr), int(eng._curva_mercado(ovr)))
        self.assertLess(eng.salario_de(90), 800_000)
        self.assertLess(eng.salario_de(85), 560_000)
        self.assertLess(eng.salario_de(80), 400_000)
        self.assertGreater(eng.salario_de(90), eng.salario_de(85))

    def test_valor_do_passe_nao_mudou(self):
        self.assertEqual(eng.valor_de(90, 27, 92), int(eng._curva_mercado(90) * 30 * 1.0 * (1 + 2 * 0.035) / 1000) * 1000)

    def test_marca_puxa_para_os_grandes(self):
        grande = next(c for c in self.G["clubes"].values() if c["nome"] == "Flamengo")
        pequeno = next(c for c in self.G["clubes"].values() if c["nome"] == "Portuguesa")
        self.assertGreater(eng.fator_marca(grande), 1.7)
        self.assertEqual(eng.fator_marca(pequeno), 1.15)

    def test_um_contrato_nao_passa_de_um_quarto_da_receita(self):
        c = next(c for c in self.G["clubes"].values() if c["divisao"] == "D")
        receita = eng.receita_semanal(self.G, c) * 4 + eng.bilheteria_mensal_estimada(c)
        self.assertFalse(eng.cabe_na_folha(self.G, c, int(receita * eng.TETO_UM_SALARIO) + 1000))

    def test_carreira_nova_nao_migra(self):
        self.assertTrue(self.G.get("econ_estrelas"))
        j = next(j for j in self.G["jogadores"].values() if j["ovr"] >= 85 and j["clube"])
        antes = j["salario"]
        eng.migrar(self.G)
        self.assertEqual(j["salario"], antes)

    def test_save_antigo_migra_uma_vez(self):
        G = self.G
        j = next(j for j in G["jogadores"].values() if j["ovr"] >= 85 and j["clube"])
        medio = next(j for j in G["jogadores"].values() if j["ovr"] <= 70 and j["clube"])
        c = G["clubes"][G["clube"]]
        eng.herdar_patrocinios(G, c)
        master = c["patrocinios"]["master"]
        certo = master["semanal"]
        # como estava antes: salario pela curva velha e patrocinio antigo
        j["salario"] = int(eng._curva_mercado(j["ovr"]))
        medio_antes = medio["salario"]
        master["semanal"] = 200_000
        G.pop("econ_estrelas")
        eng.migrar(G)
        self.assertAlmostEqual(j["salario"], eng.salario_de(j["ovr"]), delta=10)
        self.assertEqual(medio["salario"], medio_antes)
        self.assertGreaterEqual(master["semanal"], int(certo * 0.95))
        # segunda carga nao corta de novo
        cortado = j["salario"]
        eng.migrar(G)
        self.assertEqual(j["salario"], cortado)

    def test_financas_mostram_bilheteria_no_saldo(self):
        linhas = {l["nome"]: l for l in apoio.chamar("GET", "/api/financas")["tela"]["linhas"]}
        self.assertIn("Bilheteria (media por semana)", linhas)
        self.assertIn("Saldo medio da semana", linhas)


if __name__ == "__main__":
    unittest.main()
