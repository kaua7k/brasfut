# -*- coding: utf-8 -*-
"""Regras de mercado do feedback do testador (26/09/2026).

4. Jogador vendido com a janela fechada (acerto agendado) nao recebe nem
   aceita outra proposta, nem do mesmo clube.
5. No estadual, com a janela aberta, as propostas se renovam toda semana (o
   carimbo semanal usava G["semana"], que fica em 0 no estadual inteiro).
6. Agente livre contratado so pode ser vendido depois de LIVRE_SEM_REVENDA
   semanas.
"""

import os
import unittest

import apoio

eng = apoio.eng


class TestMercadoRegras(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(71)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Mercado"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def setUp(self):
        self.guardado = (self.G["fase"], self.G["semana"], self.G.get("semana_abs", 0))

    def tearDown(self):
        self.G["fase"], self.G["semana"], self.G["semana_abs"] = self.guardado

    def meu(self):
        return self.G["clubes"][self.G["clube"]]

    def comprador(self):
        return next(c for c in self.G["clubes"].values()
                    if c["divisao"] == "A" and c["id"] != self.G["clube"])

    def test_acerto_com_a_janela_fechada_trava_outras_propostas(self):
        G = self.G
        G["fase"], G["semana"] = "liga", 10
        self.assertFalse(eng.mercado_aberto(G))
        j = G["jogadores"][self.meu()["elenco"][0]]
        cl = self.comprador()
        cl["dinheiro"] = 10 ** 9
        ok, _ = eng.aceitar_oferta(G, j["id"], cl["id"], 1_000_000)
        self.assertTrue(ok)
        self.assertIn(j["id"], eng.presos_em_acerto(G))
        # outra proposta, do mesmo clube ou de outro, nao passa nem aparece
        ok2, txt = eng.aceitar_oferta(G, j["id"], cl["id"], 2_000_000)
        self.assertFalse(ok2, txt)
        G["ofertas"] = {"stamp": eng._stamp_semana(G), "itens": [[j["id"], cl["id"], 3_000_000]]}
        self.assertEqual([x for x in eng.propostas_recebidas(G) if x[0]["id"] == j["id"]], [])
        j["listado"] = 5_000_000
        for _ in range(30):
            self.assertNotIn(j["id"], [it[0] for it in eng._sortear_ofertas(G)])
        G["agendadas"] = [a for a in G["agendadas"] if a["jogador"] != j["id"]]
        j["listado"] = 0

    def test_estadual_renova_as_propostas_toda_semana(self):
        G = self.G
        G["fase"], G["semana"] = "estadual", 0
        self.assertTrue(eng.mercado_aberto(G))
        a = eng._stamp_semana(G)
        G["semana_abs"] = G.get("semana_abs", 0) + 1
        self.assertNotEqual(a, eng._stamp_semana(G), "carimbo parado no estadual")
        # a vitrine gera oferta no estadual como na liga
        caro = max(self.meu()["elenco"], key=lambda p: G["jogadores"][p]["ovr"])
        j = G["jogadores"][caro]
        j["listado"] = int(j["valor"] * 0.8)
        viu = False
        for _ in range(12):
            G["semana_abs"] += 1
            if any(x[0]["id"] == caro for x in eng.propostas_recebidas(G)):
                viu = True
                break
        j["listado"] = 0
        self.assertTrue(viu, "doze semanas de estadual sem uma proposta pela vitrine")

    def test_livre_contratado_nao_revende_logo(self):
        G = self.G
        pid = G["livres"][0]
        j = G["jogadores"][pid]
        eng.transferir(G, pid, G["clube"], 0)
        self.assertEqual(eng.revenda_travada(G, j), eng.LIVRE_SEM_REVENDA)
        ok, txt = eng.por_a_venda(G, pid, 1_000_000)
        self.assertFalse(ok)
        self.assertIn("agente livre", txt)
        cl = self.comprador()
        cl["dinheiro"] = 10 ** 9
        self.assertFalse(eng.aceitar_oferta(G, pid, cl["id"], 1_000_000)[0])
        for _ in range(20):
            self.assertNotIn(pid, [it[0] for it in eng._sortear_ofertas(G)])
        G["semana_abs"] = G.get("semana_abs", 0) + eng.LIVRE_SEM_REVENDA
        self.assertEqual(eng.revenda_travada(G, j), 0)
        self.assertTrue(eng.por_a_venda(G, pid, 1_000_000)[0])
        eng.por_a_venda(G, pid, 0)

    def test_painel_avisa_a_proposta(self):
        """Item 11: a proposta aparece no Painel, sem precisar abrir o Mercado."""
        G = self.G
        j = G["jogadores"][self.meu()["elenco"][1]]
        cl = self.comprador()
        cl["dinheiro"] = 10 ** 9
        G["ofertas"] = {"stamp": eng._stamp_semana(G), "itens": [[j["id"], cl["id"], 2_000_000]]}
        painel = apoio.chamar("GET", "/api/painel")["painel"]
        aviso = painel["propostas_jogadores"]
        self.assertEqual(aviso["total"], 1)
        self.assertEqual(aviso["itens"][0]["clube"], cl["nome"])
        G["ofertas"] = {"stamp": eng._stamp_semana(G), "itens": []}
        self.assertIsNone(apoio.chamar("GET", "/api/painel")["painel"]["propostas_jogadores"])

    def test_quem_veio_com_passe_pago_nao_trava(self):
        G = self.G
        outro = self.comprador()
        pid = outro["elenco"][0]
        eng.transferir(G, pid, G["clube"], 1_000_000)
        self.assertEqual(eng.revenda_travada(G, G["jogadores"][pid]), 0)


if __name__ == "__main__":
    unittest.main()
