# -*- coding: utf-8 -*-
"""O pedido do jogador e referencia, nao corte seco (2026-09-29): 5% abaixo
as vezes fecha, 100% as vezes nao, e o livre cede mais."""

import os
import unittest

import apoio

eng = apoio.eng


class TestAceite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(909)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Aceite"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": clubes[0]["id"]})
        cls.G = apoio.SESSAO.G
        cls.meu = cls.G["clubes"][cls.G["clube"]]

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def responde(self, j, fator):
        exig = eng.exigencia_salarial(self.G, j, self.meu, 3)
        prop = eng.Proposta(jogador=j["id"], comprador=self.meu["id"], salario=int(exig * fator), anos=3)
        return eng.avaliar_jogador(self.G, prop).aceita

    def alvos(self, livre):
        if livre:
            return [self.G["jogadores"][p] for p in self.G["livres"]][:60]
        return [j for j in self.G["jogadores"].values()
                if j["clube"] not in (None, self.meu["id"]) and not j.get("dono")][:300]

    def test_nem_corte_seco_nem_garantia(self):
        js = self.alvos(False)
        abaixo = sum(self.responde(j, 0.95) for j in js)
        cheio = sum(self.responde(j, 1.00) for j in js)
        self.assertGreater(abaixo, 0, "5% abaixo nunca fecha")
        self.assertLess(abaixo, len(js) * 0.5)
        self.assertLess(cheio, len(js), "100% sempre fecha")
        self.assertGreater(cheio, len(js) * 0.35)
        self.assertTrue(all(self.responde(j, 1.08) for j in js), "8% acima deveria fechar sempre")
        self.assertFalse(any(self.responde(j, 0.92) for j in js))

    def test_mesma_oferta_mesma_resposta(self):
        j = self.alvos(False)[0]
        self.assertEqual({self.responde(j, 0.97) for _ in range(5)}, {self.responde(j, 0.97)})

    def test_livre_cede_mais(self):
        def taxa(js, fator):
            return sum(self.responde(j, fator) for j in js) / float(len(js))
        self.assertGreater(taxa(self.alvos(True), 0.95), taxa(self.alvos(False), 0.95))


if __name__ == "__main__":
    unittest.main()
