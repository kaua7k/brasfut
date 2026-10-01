# -*- coding: utf-8 -*-
"""Trocas na Escalacao: titular por reserva e dois titulares entre si."""

import os
import unittest

import apoio

eng = apoio.eng


class TestTrocas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(7)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Escalacao"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def setUp(self):
        apoio.chamar("POST", "/api/escalacao/montar")

    def tela(self):
        return apoio.chamar("GET", "/api/escalacao")["tela"]

    def test_dois_titulares_da_mesma_vaga_trocam_de_lado(self):
        tela = self.tela()
        a, b = [j for j in tela["titulares"] if j["vaga"] == "ZAG"][:2]
        r = apoio.chamar("POST", "/api/escalacao/inverter", {"a": a["id"], "b": b["id"]})
        depois = {j["id"]: j for j in r["tela"]["titulares"]}
        self.assertEqual((depois[a["id"]]["y"], depois[b["id"]]["y"]), (b["y"], a["y"]))
        self.assertEqual(sorted(depois), sorted(j["id"] for j in tela["titulares"]))
        self.assertFalse(r["tela"]["auto"], "mexer no time desliga a alavanca")
        self.assertEqual(sorted(r["tela"]["nova_vaga"]), sorted([a["id"], b["id"]]))

    def test_capitao_aparece_no_xi_e_no_banco(self):
        tela = self.tela()
        todos = tela["titulares"] + tela["banco"]
        self.assertTrue(all("capitao" in j for j in todos))
        self.assertLessEqual(sum(1 for j in todos if j["capitao"]), 1)

    def test_titulares_de_vagas_diferentes(self):
        tela = self.tela()
        gol = [j for j in tela["titulares"] if j["vaga"] == "GOL"][0]
        zag = [j for j in tela["titulares"] if j["vaga"] == "ZAG"][0]
        corpo = {"a": gol["id"], "b": zag["id"]}
        if not tela["troca_entre_vagas"]:
            # o motor ainda escolhe a vaga sozinho: recusa com motivo, sem gravar nada
            r = apoio.chamar("POST", "/api/escalacao/inverter", corpo, status=400)
            self.assertIn("motor", r["erro"])
            self.assertEqual(self.tela()["titulares"], tela["titulares"])
            return
        r = apoio.chamar("POST", "/api/escalacao/inverter", corpo)
        vagas = {j["id"]: j["vaga"] for j in r["tela"]["titulares"]}
        self.assertEqual((vagas[gol["id"]], vagas[zag["id"]]), ("ZAG", "GOL"))

    def test_pedidos_invalidos(self):
        tela = self.tela()
        tit = tela["titulares"][0]["id"]
        res = tela["banco"][0]["id"]
        apoio.chamar("POST", "/api/escalacao/inverter", {"a": tit, "b": tit}, status=400)
        apoio.chamar("POST", "/api/escalacao/inverter", {"a": tit, "b": res}, status=400)
        apoio.chamar("POST", "/api/escalacao/inverter", {}, status=400)

    def test_titular_por_reserva_continua(self):
        tela = self.tela()
        sai = tela["titulares"][-1]
        entra = [j for j in tela["banco"] if j["disponivel"]][0]
        r = apoio.chamar("POST", "/api/escalacao/trocar", {"titular": sai["id"], "reserva": entra["id"]})
        ids = {j["id"] for j in r["tela"]["titulares"]}
        self.assertIn(entra["id"], ids)
        self.assertNotIn(sai["id"], ids)

    def test_time_manual_entra_em_campo(self):
        """O bug antigo: simular usava montar_escalacao e ignorava o XI do tecnico."""
        tela = self.tela()
        gol = [j for j in tela["titulares"] if j["vaga"] == "GOL"][0]
        reserva = [j for j in tela["banco"] if j["pos"] == "GOL" and j["disponivel"]][0]
        apoio.chamar("POST", "/api/escalacao/trocar", {"titular": gol["id"], "reserva": reserva["id"]})
        G = apoio.SESSAO.G
        meu = G["clube"]
        rival = next(c["id"] for c in G["clubes"].values() if c["divisao"] == "A" and c["id"] != meu)
        jogou = []
        original = eng.atribuir_vagas

        def espia(G_, esc, form, fixas=None):
            jogou.append(list(esc))
            return original(G_, esc, form, fixas)

        eng.atribuir_vagas = espia
        try:
            eng.simular(G, meu, rival, "liga")
        finally:
            eng.atribuir_vagas = original
        self.assertIn(reserva["id"], jogou[0], "o goleiro escalado a mao nao entrou em campo")
        self.assertNotIn(gol["id"], jogou[0])


if __name__ == "__main__":
    unittest.main()
