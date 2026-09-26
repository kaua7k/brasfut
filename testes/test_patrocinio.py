# -*- coding: utf-8 -*-
"""Patrocinio master e de uniforme como contratos (economia, entrega 3)."""

import os
import unittest

import apoio

eng = apoio.eng


def mundo_novo(semente, divisao="A"):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(semente)
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Patrocinio",
                                                "opcoes": {"sem_demissao": True}})["clubes"]
    apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == divisao][0]["id"]})
    return apoio.SESSAO.G


class TestPatrocinio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_carreira_nova_tem_tres_propostas_estaveis_por_espaco(self):
        G = mundo_novo(111)
        c = G["clubes"][G["clube"]]
        self.assertEqual(eng.espacos_vagos(G, c), list(eng.espacos_do_clube(c)))
        # naming rights so com estadio grande
        self.assertEqual("naming" in eng.espacos_do_clube(c), c["capacidade"] >= eng.NAMING_CAPACIDADE)
        ofertas = eng.ofertas_patrocinio(G, c, "master")
        self.assertEqual([o["perfil"] for o in ofertas], ["fixo alto", "equilibrado", "aposta"])
        self.assertEqual(ofertas, eng.ofertas_patrocinio(G, c, "master"))
        self.assertGreater(ofertas[0]["semanal"], ofertas[2]["semanal"])
        self.assertGreater(ofertas[2]["bonus"], ofertas[0]["bonus"])
        self.assertEqual(ofertas[2]["meta"], "titulo")
        painel = apoio.chamar("GET", "/api/painel")["painel"]
        self.assertEqual(len(painel["patrocinio_vago"]), len(eng.espacos_do_clube(c)))

    def test_serie_b_aposta_no_acesso(self):
        G = mundo_novo(113, divisao="B")
        c = G["clubes"][G["clube"]]
        self.assertEqual(eng.ofertas_patrocinio(G, c, "master")[2]["meta"], "acesso")

    def test_assinar_pela_api_e_o_resto_assina_sozinho_quando_a_bola_rola(self):
        G = mundo_novo(117)
        c = G["clubes"][G["clube"]]
        escolhida = eng.ofertas_patrocinio(G, c, "master")[0]
        r = apoio.chamar("POST", "/api/patrocinio/assinar", {"espaco": "master", "indice": 0})
        self.assertIn(escolhida["empresa"], r["recado"])
        self.assertEqual(c["patrocinios"]["master"]["semanal"], escolhida["semanal"])
        apoio.chamar("POST", "/api/patrocinio/assinar", {"espaco": "master", "indice": 1}, status=400)
        resto = [e for e in eng.espacos_do_clube(c) if e != "master"]
        equilibradas = {e: eng.ofertas_patrocinio(G, c, e)[1] for e in resto}
        apoio.chamar("POST", "/api/avancar", {"leve": True, "confirmar": True})
        for e, o in equilibradas.items():
            self.assertEqual(c["patrocinios"][e]["empresa"], o["empresa"], e)
        # a semana entrou no extrato em duas linhas: TV e patrocinio
        ex = eng.stats_ano(G)["extrato"]
        self.assertEqual(ex["patrocinio"], escolhida["semanal"] + sum(o["semanal"] for o in equilibradas.values()))
        self.assertEqual(ex["tv"], eng.tv_semanal(c))

    def test_virada_paga_bonus_da_meta_e_vence_contrato(self):
        G = mundo_novo(119)
        c = G["clubes"][G["clube"]]
        eng.assinar_patrocinio(G, c, "master", {"perfil": "fixo alto", "empresa": "X", "semanal": 1000,
                                                "temporadas": 1, "meta": "objetivo", "bonus": 50_000})
        eng.assinar_patrocinio(G, c, "uniforme", {"perfil": "aposta", "empresa": "Y", "semanal": 1000,
                                                  "temporadas": 3, "meta": "titulo", "bonus": 90_000})
        caixa = c["dinheiro"]
        pagos = eng.fechar_ano_patrocinio(G, c, {"objetivo_ok": True, "posicao": 5})
        self.assertEqual(c["dinheiro"] - caixa, 50_000)
        self.assertEqual([p[0] for p in pagos], ["X"])
        self.assertIsNone(c["patrocinios"]["master"])
        self.assertEqual(c["patrocinios"]["uniforme"]["temporadas"], 2)
        self.assertEqual(eng.espacos_vagos(G, c)[0], "master")
        self.assertNotIn("uniforme", eng.espacos_vagos(G, c))

    def test_troca_de_clube_herda_contratos_e_maquina_recebe_base(self):
        G = mundo_novo(123)
        antigo = G["clubes"][G["clube"]]
        apoio.chamar("POST", "/api/avancar", {"leve": True, "confirmar": True})
        novo = next(c for c in G["clubes"].values() if c["divisao"] == "B")
        eng.assumir_clube(G, novo["id"], "teste")
        self.assertNotIn("patrocinios", antigo)
        self.assertEqual(eng.espacos_vagos(G, novo), [])
        self.assertEqual(novo["patrocinios"]["master"]["perfil"], "herdado")
        # a maquina recebe a TV e a soma das fatias de patrocinio dos espacos dela
        esperado = eng.tv_semanal(antigo) + sum(int(eng._receita_base(antigo) * eng.FATIA_PATROCINIO[e])
                                                 for e in eng.espacos_do_clube(antigo))
        self.assertAlmostEqual(eng.receita_semanal(G, antigo), esperado, delta=esperado * 0.01)

    def test_save_antigo_ganha_contratos_herdados(self):
        G = mundo_novo(127)
        c = G["clubes"][G["clube"]]
        c.pop("patrocinios", None)
        eng.migrar(G)
        self.assertEqual(sorted(k for k, v in c["patrocinios"].items() if v), sorted(eng.espacos_do_clube(c)))


if __name__ == "__main__":
    unittest.main()
