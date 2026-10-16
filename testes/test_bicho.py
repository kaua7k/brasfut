# -*- coding: utf-8 -*-
"""Bicho por vitoria: custo no caixa e moral extra para quem jogou."""

import os
import unittest

import apoio

eng = apoio.eng


def mundo_novo(semente):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(semente)
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Bicho",
                                                "opcoes": {"sem_demissao": True}})["clubes"]
    apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
    return apoio.SESSAO.G


class TestBicho(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_padrao_sem_bicho_e_api_muda_o_nivel(self):
        G = mundo_novo(201)
        self.assertEqual(eng.bicho_nivel(G), "nenhum")
        tela = apoio.chamar("GET", "/api/financas")["tela"]
        self.assertEqual(tela["bicho"]["nivel"], "nenhum")
        self.assertEqual([n["id"] for n in tela["bicho"]["niveis"]], [b[0] for b in eng.BICHO])
        r = apoio.chamar("POST", "/api/bicho", {"nivel": "alto"})
        self.assertEqual(G["bicho"], "alto")
        self.assertEqual(r["tela"]["bicho"]["nivel"], "alto")
        apoio.chamar("POST", "/api/bicho", {"nivel": "absurdo"}, status=400)

    def test_vitoria_paga_o_bicho_e_anima_quem_jogou(self):
        G = mundo_novo(203)
        c = G["clubes"][G["clube"]]
        G["bicho"] = "dobrado"
        custo = eng.custo_bicho(G, c)
        self.assertGreater(custo, 0)
        esc = list(c["elenco"][:11])
        for pid in esc:
            G["jogadores"][pid]["moral"] = 50
        caixa = c["dinheiro"]
        eng.pagar_bicho(G, c, esc)
        self.assertEqual(c["dinheiro"], caixa - custo)
        self.assertEqual(eng.stats_ano(G)["extrato"]["bicho"], -custo)
        for pid in esc:
            self.assertEqual(G["jogadores"][pid]["moral"], 54)
        # maquina nao paga, e sem bicho nada muda
        outro = next(x for x in G["clubes"].values() if x["id"] != c["id"])
        caixa_outro = outro["dinheiro"]
        eng.pagar_bicho(G, outro, list(outro["elenco"][:11]))
        self.assertEqual(outro["dinheiro"], caixa_outro)
        G["bicho"] = "nenhum"
        eng.pagar_bicho(G, c, esc)
        self.assertEqual(c["dinheiro"], caixa - custo)


class TestCapitaoNaEscalacao(unittest.TestCase):
    def test_escolhe_a_bracadeira_pela_escalacao(self):
        G = mundo_novo(207)
        c = G["clubes"][G["clube"]]
        tela = apoio.chamar("GET", "/api/escalacao")["tela"]
        cap = tela["capitao"]
        self.assertEqual(cap["id"], eng.capitao_de(G, c))
        xi = {j["id"] for j in tela["titulares"]}
        titulares = [o for o in cap["opcoes"] if o["titular"]]
        self.assertTrue(titulares)
        self.assertEqual(cap["opcoes"][:len(titulares)], titulares)
        self.assertTrue({o["id"] for o in titulares} <= xi)
        novo = next(o["id"] for o in cap["opcoes"] if o["id"] != cap["id"])
        r = apoio.chamar("POST", "/api/escalacao/capitao", {"id": novo})
        self.assertEqual(c["capitao"], novo)
        self.assertEqual(r["tela"]["capitao"]["id"], novo)
        apoio.chamar("POST", "/api/escalacao/capitao", {"id": -1}, status=400)


if __name__ == "__main__":
    unittest.main()
