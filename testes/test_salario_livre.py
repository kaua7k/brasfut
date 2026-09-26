# -*- coding: utf-8 -*-
"""Salario do agente livre e do veterano (decidido em 2026-09-25).

O livre nao defende contrato: parte do mercado do overall e da idade, da um
desconto que cresce com o tempo parado (15% -> 40% em 10 semanas) e desce de
patamar cobrando no maximo 30% a mais. O mercado paga menos pelo veterano.
A lista do Mercado mostra o que o livre pede, nao o contrato antigo.
"""

import os
import unittest

import apoio

eng = apoio.eng
SESSAO = apoio.SESSAO


class TestSalarioLivre(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(404)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Salario"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def livre(self, ovr=72, idade=27, salario=None):
        j = self.G["jogadores"][self.G["livres"][0]]
        j.update(ovr=ovr, idade=idade, pot=ovr)
        j["salario"] = salario if salario is not None else eng.salario_de(ovr)
        j.pop("livre_desde", None)
        return j

    def meu(self):
        return self.G["clubes"][self.G["clube"]]

    def test_idade_derruba_o_mercado(self):
        self.assertEqual(eng.fator_idade_salario(27), 1.0)
        self.assertEqual(eng.fator_idade_salario(31), 0.85)
        self.assertEqual(eng.fator_idade_salario(34), 0.70)
        self.assertEqual(eng.fator_idade_salario(36), 0.55)
        novo = self.livre(idade=27)
        pede_novo = eng.exigencia_salarial(self.G, novo, self.meu())
        velho = self.livre(idade=36)
        pede_velho = eng.exigencia_salarial(self.G, velho, self.meu())
        self.assertLess(pede_velho, pede_novo * 0.62)

    def test_livre_nao_usa_o_contrato_antigo(self):
        """O caso do veterano de 36 que pedia mais que o mercado do overall."""
        j = self.livre(ovr=71, idade=36, salario=233_000)
        pede = eng.exigencia_salarial(self.G, j, self.meu())
        self.assertLess(pede, eng.salario_de(71) * 0.55)

    def test_desconto_cresce_com_o_tempo_parado(self):
        j = self.livre()
        self.assertAlmostEqual(eng.desconto_livre(self.G, j), eng.LIVRE_DESCONTO_INI)
        agora = eng.semana_absoluta(self.G)
        j["livre_desde"] = agora - 5
        meio = eng.desconto_livre(self.G, j)
        self.assertGreater(meio, eng.LIVRE_DESCONTO_INI)
        j["livre_desde"] = agora - 30
        self.assertAlmostEqual(eng.desconto_livre(self.G, j), eng.LIVRE_DESCONTO_MAX)
        pede_encalhado = eng.exigencia_salarial(self.G, j, self.meu())
        j["livre_desde"] = agora
        self.assertLess(pede_encalhado, eng.exigencia_salarial(self.G, j, self.meu()))

    def test_clube_pequeno_paga_no_maximo_30_por_cento_a_mais(self):
        j = self.livre()
        pequeno = min((c for c in self.G["clubes"].values() if c["divisao"] in eng.DIVISOES_BR),
                      key=lambda c: c["reputacao"])
        grande = self.meu()
        base = eng.salario_referencia(j) * 1.12 * (1 - eng.desconto_livre(self.G, j))
        self.assertLessEqual(eng.exigencia_salarial(self.G, j, pequeno), base * 1.30 * 1.08 + 100)
        self.assertLess(eng.exigencia_salarial(self.G, j, grande), base * 1.08 + 100)

    def test_quem_tem_clube_mantem_o_piso_do_salario_atual(self):
        c = self.meu()
        j = self.G["jogadores"][c["elenco"][0]]
        j["salario"] = eng.salario_de(j["ovr"]) * 3
        self.assertEqual(eng.salario_referencia(j), int(j["salario"] * eng.piso_salario_atual(j["idade"])))

    def test_carimbo_e_ia_pagando_a_pedida(self):
        G = self.G
        eng.carimbar_livres(G)
        for pid in G["livres"]:
            self.assertIn("livre_desde", G["jogadores"][pid])
        j = self.livre(ovr=60, idade=35, salario=500_000)
        c = next(x for x in G["clubes"].values() if x["divisao"] == "D")
        eng.contratar_livre_ia(G, c, j["pos"], 90)
        if j["clube"] == c["id"]:
            self.assertLess(j["salario"], 500_000)
            self.assertNotIn("livre_desde", j)

    def test_mercado_mostra_a_pedida_do_livre(self):
        from api import mercado
        G = self.G
        j = self.livre(ovr=70, idade=34, salario=900_000)
        linha = mercado._linha_busca(G, self.meu(), j, "compra")
        self.assertEqual(linha["salario"], eng.din(eng.exigencia_salarial(G, j, self.meu())))


if __name__ == "__main__":
    unittest.main()
