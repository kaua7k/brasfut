# -*- coding: utf-8 -*-
"""Salario de profissional e o do contrato (economia, entrega 2).

So muda ao contratar ou renovar. Evoluir ou envelhecer nao reescreve o
salario (antes ele voltava a tabela a cada ponto de overall, e a renovacao
durava ate o proximo treino). Bolsa de base segue a tabela. O pedido de quem
evoluiu com contrato barato parte do mercado.
"""

import os
import unittest

import apoio

eng = apoio.eng


class TestSalarioContrato(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(103)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Salario"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def profissional(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        return next(G["jogadores"][p] for p in c["elenco"]
                    if not G["jogadores"][p].get("dono") and not eng.da_base(G["jogadores"][p]))

    def test_evoluir_nao_apaga_a_renovacao(self):
        G, j = self.G, self.profissional()
        prop = eng.Proposta(jogador=j["id"], comprador=j["clube"], anos=3, tipo=eng.TIPO_RENOVACAO,
                            salario=eng.exigencia_renovacao(G, j, 3) + 50_000)
        eng.fechar_renovacao(G, prop)
        acertado = j["salario"]
        j["ovr_frac"] = 2.5                 # dois pontos de overall na proxima evolucao
        ovr = j["ovr"]
        eng.aplicar_evolucao(G, j, meses=0.0)
        self.assertGreater(j["ovr"], ovr)
        self.assertEqual(j["salario"], acertado)

    def test_virada_nao_apaga_salario_e_bolsa_segue_a_tabela(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        pro = self.profissional()
        pro["salario"] = 123_400
        base = next((G["jogadores"][p] for p in c.get("base_elenco", [])), None)
        eng.evoluir_jogadores(G)
        if pro["id"] in G["jogadores"]:
            self.assertEqual(pro["salario"], 123_400)
        if base is not None and base["id"] in G["jogadores"] and eng.da_base(base):
            self.assertEqual(base["salario"], eng.salario_devido(base))

    def test_quem_evoluiu_barato_pede_o_mercado(self):
        j = dict(self.profissional())
        j["salario"] = 10_000
        self.assertEqual(eng.salario_referencia(j), eng.salario_de(j["ovr"]))
        j["salario"] = eng.salario_de(j["ovr"]) * 3        # veterano caro: aceita no maximo 15% de corte
        self.assertEqual(eng.salario_referencia(j), int(j["salario"] * 0.85))

    def test_contrato_novo_parte_do_mercado_e_a_mesa_grava_o_negociado(self):
        G = self.G
        alvo = next(j for j in G["jogadores"].values()
                    if j.get("clube") not in (None, G["clube"]) and not j.get("dono")
                    and not eng.da_base(j))
        outro = next(cid for cid, c in G["clubes"].items()
                     if cid not in (G["clube"], alvo["clube"]) and c["divisao"] == "A")
        alvo["salario"] = 1
        eng.transferir(G, alvo["id"], outro, 0)
        self.assertEqual(alvo["salario"], eng.salario_de(alvo["ovr"]))
        G["clubes"][G["clube"]]["dinheiro"] += 10 ** 9
        prop = eng.Proposta(jogador=alvo["id"], comprador=G["clube"], valor=1_000_000,
                            salario=777_000, anos=2, tipo=eng.TIPO_COMPRA)
        antes = G["fase"], G["semana"]
        G["fase"], G["semana"] = "entretemporada", 0      # janela aberta: assina na hora
        try:
            eng.fechar_compra(G, prop)
        finally:
            G["fase"], G["semana"] = antes
        self.assertEqual(alvo["salario"], 777_000)

    def test_maquina_renovando_vai_para_o_mercado(self):
        G = self.G
        meus = set(G["clubes"][G["clube"]]["elenco"])
        cands = [j for j in G["jogadores"].values()
                 if j.get("clube") and j["id"] not in meus and not eng.da_base(j)][:60]
        for j in cands:
            j["contrato"], j["salario"] = 0, 1
        eng.fim_de_contrato(G)
        renovados = [j for j in cands if j["contrato"] > 0]
        self.assertTrue(renovados)
        for j in renovados:
            self.assertEqual(j["salario"], eng.salario_de(j["ovr"]))


if __name__ == "__main__":
    unittest.main()
