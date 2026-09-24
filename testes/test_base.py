# -*- coding: utf-8 -*-
"""Base: peneira regional, candidatos, faixa que estreita e revelacoes."""

import os
import unittest

import apoio

eng = apoio.eng


class TestPeneira(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(17)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Base"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = apoio.SESSAO.G
        cls.c = cls.G["clubes"][cls.G["clube"]]

    def test_peneira_do_comeco_ao_fim(self):
        c = self.c
        apoio.chamar("POST", "/api/base/peneira", {"regiao": "marte"}, status=400)
        r = apoio.chamar("POST", "/api/base/peneira", {"regiao": "ne", "foco": "ATA"})
        self.assertEqual(r["tela"]["peneira"]["atual"]["regiao"], "ne")
        for _ in range(eng.PENEIRA_A_CADA):
            apoio.avancar({"leve": True})
        tela = apoio.chamar("GET", "/api/base")["tela"]
        self.assertTrue(tela["candidatos"], "a peneira nao trouxe ninguem")
        self.assertTrue(all(k["pos"] == "ATA" for k in tela["candidatos"]))

        # base cheia recusa; com vaga, entra
        while len(c["base_elenco"]) < eng.vagas_base(c):
            eng.gerar_cria(self.G, c, set())
        k = tela["candidatos"][0]
        apoio.chamar("POST", "/api/base/candidato", {"cid": k["cid"], "aceitar": True}, status=400)
        c["base_elenco"].pop()
        r = apoio.chamar("POST", "/api/base/candidato", {"cid": k["cid"], "aceitar": True})
        self.assertIn(k["nome"].split()[0], r["recado"])
        self.assertNotIn(k["cid"], [x["cid"] for x in r["tela"]["candidatos"]])
        for resto in r["tela"]["candidatos"]:
            apoio.chamar("POST", "/api/base/candidato", {"cid": resto["cid"], "aceitar": False})
        apoio.chamar("POST", "/api/base/candidato", {"cid": k["cid"], "aceitar": False}, status=400)

        r = apoio.chamar("POST", "/api/base/peneira", {"desligar": True})
        self.assertIsNone(r["tela"]["peneira"]["atual"])

    def test_faixa_estreita_com_observacao(self):
        c = self.c
        j = eng.gerar_cria(self.G, c, set(), idade=15)
        j["obs"] = 0
        largura = lambda: (lambda n: n[-1] - n[0])([int(x) for x in eng.scout(self.G, j).replace("teto ~", "").split("-")])
        antes = largura()
        j["obs"] = 18
        self.assertLessEqual(largura(), antes)

    def test_revelacao_fica_registrada(self):
        c = self.c
        j = eng.gerar_cria(self.G, c, set(), idade=18)
        while len(c["elenco"]) >= eng.LIMITE_ELENCO:
            c["elenco"].pop()
        ok, _ = eng.promover_da_base(self.G, j["id"])
        self.assertTrue(ok)
        rev = apoio.chamar("GET", "/api/base")["tela"]["revelados"]
        self.assertEqual(rev[0]["nome"], j["nome"])
        self.assertTrue(rev[0]["em_casa"])


if __name__ == "__main__":
    unittest.main()
