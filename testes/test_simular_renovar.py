# -*- coding: utf-8 -*-
"""Relato do Simular por semana (com quem passou no mata-mata) e renovacao em lote."""

import os
import unittest

import apoio
from api import avanco

eng = apoio.eng


def mundo_novo(semente):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(semente)
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Simular"})["clubes"]
    apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
    return apoio.SESSAO.G


class TestSimularERenovar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        cls.G = mundo_novo(83)

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def meu_e_outro(self):
        G = self.G
        outro = next(c for c in G["clubes"].values() if c["id"] != G["clube"] and c["divisao"] == "A")
        return G["clube"], outro["id"]

    # --------------------------------------------------------------- relato
    def test_decisao_diz_quem_passou_nos_penaltis(self):
        eu, ele = self.meu_e_outro()
        volta = {"casa": ele, "fora": eu, "gc": 1, "gf": 1, "comp": "copa",
                 "agregado": [eu, 3, ele, 3], "penaltis": eu, "venc": eu}
        d = avanco.decisao(self.G, volta, eu)
        self.assertEqual(d["estado"], "ok")
        self.assertEqual(d["texto"], "Classificado nos penaltis · agregado 3 x 3")
        volta.update(penaltis=ele, venc=ele)
        d = avanco.decisao(self.G, volta, eu)
        self.assertEqual((d["estado"], d["texto"]), ("critico", "Eliminado nos penaltis · agregado 3 x 3"))

    def test_agregado_e_contado_do_meu_lado(self):
        eu, ele = self.meu_e_outro()
        volta = {"casa": eu, "fora": ele, "gc": 0, "gf": 2, "comp": "copa",
                 "agregado": [ele, 1, eu, 4], "venc": eu}
        self.assertEqual(avanco.decisao(self.G, volta, eu)["texto"], "Classificado · agregado 4 x 1")

    def test_ida_e_pontos_corridos_nao_decidem(self):
        eu, ele = self.meu_e_outro()
        ida = {"casa": eu, "fora": ele, "gc": 2, "gf": 0, "comp": "copa", "venc": eu, "perna": "ida"}
        self.assertIsNone(avanco.decisao(self.G, ida, eu))
        liga = {"casa": eu, "fora": ele, "gc": 2, "gf": 0, "comp": "liga"}
        self.assertIsNone(avanco.decisao(self.G, liga, eu))

    def test_avanco_devolve_a_semana_estruturada(self):
        for _ in range(12):
            r = apoio.avancar({"leve": True})
            if r["jogou"]:
                break
        sem = r["semana"]
        self.assertTrue(sem["titulo"])
        self.assertTrue(sem["jogos"])
        j = sem["jogos"][0]
        self.assertIn(j["resultado"], ("V", "E", "D"))
        self.assertEqual(len(j["times"]), 2)
        self.assertIn(self.G["clubes"][self.G["clube"]]["nome"], j["times"][j["eu"]])
        self.assertTrue(j["comp"])

    # ------------------------------------------------------------ renovacao
    def test_previa_do_lote_em_cinco_anos_e_quem_fica_de_fora(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        ids = [p for p in c["elenco"] if not G["jogadores"][p].get("dono")][:4]
        emprestado = next(j for j in G["jogadores"].values()
                          if j.get("clube") not in (None, G["clube"]))
        previa = apoio.chamar("POST", "/api/mercado/renovar-lote/linhas",
                              {"ids": ids + [emprestado["id"]]})
        self.assertEqual(previa["anos"], 5)
        linhas = {l["id"]: l for l in previa["linhas"]}
        for pid in ids:
            self.assertIsNone(linhas[pid]["motivo"])
            self.assertEqual(linhas[pid]["pede"],
                             eng.din(eng.exigencia_renovacao(G, G["jogadores"][pid], 5)))
        self.assertIsNotNone(linhas[emprestado["id"]]["motivo"])

    def test_lote_renova_todos_de_uma_vez_pelo_pedido(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        ids = [p for p in c["elenco"] if not G["jogadores"][p].get("dono")][4:10]
        pedidos = {p: eng.exigencia_renovacao(G, G["jogadores"][p], 3) for p in ids}
        # o pedido e referencia: quem, por dentro, quer mais que ele fica de fora
        # do lote (vai para a mesa); quem aceita renova exatamente pelo pedido
        aceitam = [p for p in ids if eng.limite_de_aceite(G, G["jogadores"][p], c, pedidos[p],
                                                          "renovacao") <= pedidos[p]]
        self.assertTrue(aceitam)
        r = apoio.chamar("POST", "/api/mercado/renovar-lote", {"ids": ids, "anos": 3})
        self.assertEqual(sorted(r["feitos"]), sorted(G["jogadores"][p]["nome"] for p in aceitam))
        for p in aceitam:
            j = G["jogadores"][p]
            self.assertEqual((j["contrato"], j["salario"]), (3, pedidos[p]))

    def test_lote_sem_ninguem_valido_e_recusado(self):
        G = self.G
        de_fora = next(j for j in G["jogadores"].values() if j.get("clube") not in (None, G["clube"]))
        apoio.chamar("POST", "/api/mercado/renovar-lote", {"ids": [de_fora["id"]]}, status=400)
        apoio.chamar("POST", "/api/mercado/renovar-lote", {"ids": []}, status=400)


if __name__ == "__main__":
    unittest.main()
