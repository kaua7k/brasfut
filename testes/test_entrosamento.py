# -*- coding: utf-8 -*-
"""Entrosamento (Onda 3): quem chega comeca baixo e ganha jogando pelo clube.

Pesa pouco no rendimento (PESO_JOGO_ENTROS), entra na chave do memo do XI e
nao usa o rng. Save antigo, sem o campo, vale o padrao.
"""

import os
import unittest

import apoio

eng = apoio.eng
SESSAO = apoio.SESSAO


class TestEntrosamento(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(77)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Entrosamento"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def outro_clube(self):
        return next(c for c in self.G["clubes"].values()
                    if c["id"] != self.G["clube"] and c["divisao"] == "A")

    def test_mundo_novo_e_save_antigo_valem_o_padrao(self):
        j = next(iter(self.G["jogadores"].values()))
        j.pop("entros", None)
        self.assertEqual(eng.entrosamento(j), eng.ENTROS_PADRAO)

    def test_quem_chega_comeca_baixo_e_ganha_jogando(self):
        G = self.G
        outro = self.outro_clube()
        pid = outro["elenco"][0]
        eng.transferir(G, pid, G["clube"], 0)
        j = G["jogadores"][pid]
        self.assertEqual(eng.entrosamento(j), eng.ENTROS_CHEGADA)
        antes = eng.rendimento(j)
        j["entros"] = 100
        self.assertGreater(eng.rendimento(j), antes)
        # a diferenca entre recem-chegado e entrosado e pequena de proposito
        self.assertLess(eng.rendimento(j) / antes, 1.05)

        # quem entra em campo ganha ENTROS_POR_JOGO, ate 100
        for p in G["clubes"][G["clube"]]["elenco"]:
            G["jogadores"][p]["entros"] = eng.ENTROS_CHEGADA
        r = eng.simular(G, G["clube"], self.outro_clube()["id"])
        jogaram = list(r["xi"]["casa"])
        self.assertTrue(jogaram)
        for p in jogaram:
            self.assertEqual(eng.entrosamento(G["jogadores"][p]),
                             eng.ENTROS_CHEGADA + eng.ENTROS_POR_JOGO)
        G["jogadores"][jogaram[0]]["entros"] = 99
        r = eng.simular(G, G["clube"], self.outro_clube()["id"])
        if jogaram[0] in r["xi"]["casa"]:
            self.assertEqual(eng.entrosamento(G["jogadores"][jogaram[0]]), 100)

    def test_emprestimo_e_volta(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        pid = c["elenco"][-1]
        j = G["jogadores"][pid]
        j["entros"] = 95
        eng.emprestar(G, pid, self.outro_clube()["id"], 100)
        self.assertEqual(eng.entrosamento(j), eng.ENTROS_CHEGADA)
        eng.devolver_emprestimo(G, pid)
        self.assertEqual(eng.entrosamento(j), eng.ENTROS_VOLTA)

    def test_memo_ve_o_entrosamento(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        esc = c["elenco"][:11]
        form = eng.formacao_de(c)
        a = eng._chave_xi(G, esc, form, None)
        G["jogadores"][esc[0]]["entros"] = 10
        self.assertNotEqual(a, eng._chave_xi(G, esc, form, None))

    def test_telas_mostram(self):
        tela = apoio.chamar("GET", "/api/escalacao")["tela"]
        self.assertIn("entrosamento", [m["nome"] for m in tela["metricas"]])
        pid = self.G["clubes"][self.G["clube"]]["elenco"][0]
        ficha = apoio.chamar("POST", "/api/ficha", {"id": pid})["ficha"]
        self.assertIn("Entrosamento", [b["nome"] for b in ficha["barras"]])


if __name__ == "__main__":
    unittest.main()
