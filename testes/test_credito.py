# -*- coding: utf-8 -*-
"""Credito do clube (item 10 do feedback, decidido em 2026-09-26).

Ate 3 meses de receita, 2% ao mes, parcelas fixas (Price) que saem na virada do
mes. Sem caixa, a parcela atrasa: juro e multa entram no saldo e a diretoria
cobra na confianca. Uma operacao por vez; da para quitar antes.
"""

import os
import unittest

import apoio

eng = apoio.eng


class TestCredito(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(111)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Credito"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "B"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def setUp(self):
        self.G["credito"] = None
        self.c = self.G["clubes"][self.G["clube"]]

    def test_limite_e_tres_meses_de_receita(self):
        lim = eng.limite_credito(self.G)
        self.assertAlmostEqual(lim, eng.receita_mensal(self.G, self.c) * 3, delta=1000)

    def test_tomar_pagar_ate_zerar(self):
        G, c = self.G, self.c
        caixa = c["dinheiro"]
        no_extrato = eng.stats_ano(G)["extrato"].get("credito", 0)
        ok, txt = eng.tomar_credito(G, 1_000_000, 6)
        self.assertTrue(ok, txt)
        self.assertEqual(c["dinheiro"], caixa + 1_000_000)
        self.assertEqual(eng.stats_ano(G)["extrato"].get("credito") - no_extrato, 1_000_000)
        self.assertEqual(eng.limite_credito(G), 0, "segunda operacao com uma em aberto")
        self.assertFalse(eng.tomar_credito(G, 200_000, 6)[0])
        parcela = G["credito"]["parcela"]
        self.assertEqual(parcela, eng.parcela_credito(1_000_000, 6))
        c["dinheiro"] = 10 ** 9
        pago = 0
        for _ in range(6):
            antes = c["dinheiro"]
            eng.pagar_parcela_credito(G)
            pago += antes - c["dinheiro"]
        self.assertIsNone(eng.credito(G), "seis parcelas e a divida nao zerou")
        # tabela Price: seis parcelas iguais (a ultima pode sobrar um troco)
        self.assertAlmostEqual(pago, parcela * 6, delta=10)

    def test_regras_de_entrada(self):
        G = self.G
        self.assertFalse(eng.tomar_credito(G, 50_000, 6)[0], "abaixo do minimo")
        self.assertFalse(eng.tomar_credito(G, eng.limite_credito(G) + 1_000_000, 6)[0], "acima do limite")
        self.assertFalse(eng.tomar_credito(G, 500_000, 7)[0], "prazo fora da tabela")

    def test_atraso_capitaliza_e_diretoria_cobra(self):
        G, c = self.G, self.c
        eng.tomar_credito(G, 1_000_000, 12)
        saldo = G["credito"]["saldo"]
        c["dinheiro"] = 0
        eng.pagar_parcela_credito(G)
        cr = G["credito"]
        self.assertEqual(cr["atrasos"], 1)
        self.assertGreater(cr["saldo"], saldo)
        self.assertEqual(cr["restantes"], 12, "parcela atrasada nao conta como paga")
        # na semana seguinte a confianca registra o atraso
        G["semana_abs"] = eng.semana_absoluta(G) + 1
        eng.reiniciar_confianca(G, 60)
        eng.atualizar_confianca(G, [])
        causas = eng.confianca(G)["hist"][-1][2]
        self.assertTrue(any(x[1] == "parcela do credito atrasada" and x[0] < 0 for x in causas), causas)

    def test_quitar_antes(self):
        G, c = self.G, self.c
        eng.tomar_credito(G, 800_000, 24)
        c["dinheiro"] = 10 ** 8
        saldo = G["credito"]["saldo"]
        ok, _ = eng.quitar_credito(G)
        self.assertTrue(ok)
        self.assertEqual(c["dinheiro"], 10 ** 8 - saldo)
        self.assertIsNone(eng.credito(G))

    def test_api_e_tela(self):
        G = self.G
        self.c["dinheiro"] = 5_000_000
        tela = apoio.chamar("GET", "/api/financas")["tela"]
        self.assertIsNone(tela["credito"]["ativo"])
        self.assertEqual([p["meses"] for p in tela["credito"]["prazos"]], list(eng.CREDITO_PRAZOS))
        r = apoio.chamar("POST", "/api/credito", {"acao": "tomar", "valor": 300_000, "meses": 12})
        self.assertIsNotNone(r["tela"]["credito"]["ativo"])
        apoio.chamar("POST", "/api/credito", {"acao": "tomar", "valor": 300_000, "meses": 12}, status=400)
        r = apoio.chamar("POST", "/api/credito", {"acao": "quitar"})
        self.assertIsNone(r["tela"]["credito"]["ativo"])


if __name__ == "__main__":
    unittest.main()
