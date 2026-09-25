# -*- coding: utf-8 -*-
"""Rebalanceamento da economia (entrega 4): publico vem da torcida, custos
proporcionais ao porte, operacao de jogo e premio por fase nas copas."""

import os
import unittest

import apoio

eng = apoio.eng


class TestRebalanceamento(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(131)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Rebalanceamento",
                                                    "opcoes": {"sem_demissao": True}})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def clube(self, div, maior=True):
        cs = sorted((c for c in self.G["clubes"].values() if c["divisao"] == div), key=lambda c: c["reputacao"])
        return cs[-1] if maior else cs[0]

    def test_publico_vem_da_torcida_e_nao_da_capacidade(self):
        G = self.G
        casa, fora = self.clube("D"), self.clube("D", maior=False)
        casa["preco"] = int(eng.preco_referencia(casa))
        cap = casa["capacidade"]
        publicos = []
        for novo_cap in (cap, cap * 4):
            casa["capacidade"] = novo_cap
            eng.rng.seed(7)
            publicos.append(eng.publico_e_renda(G, casa, fora, "liga")[0])
        casa["capacidade"] = cap
        # quadruplicar o estadio nao quadruplica a torcida (so limita quando falta lugar)
        self.assertLessEqual(publicos[1], max(publicos[0] * 1.05, cap))
        self.assertLess(eng.demanda_torcida(self.clube("D")), eng.demanda_torcida(self.clube("A")))

    def test_ampliar_sem_torcida_so_aumenta_custo(self):
        c = self.clube("C")
        antes = eng.custo_estrutura(c)
        c["capacidade"] += 20_000
        try:
            self.assertGreater(eng.custo_estrutura(c), antes)
            self.assertLessEqual(eng.publico_esperado(c), eng.demanda_torcida(c) * 1.7)
        finally:
            c["capacidade"] -= 20_000

    def test_manutencao_da_infra_acompanha_o_porte(self):
        grande, pequeno = self.clube("A"), self.clube("D", maior=False)
        guardado = [(c["ct"], c["base"], c["medico"], c["capacidade"], list(c.get("treino_foco", [])))
                    for c in (grande, pequeno)]
        try:
            fracoes = []
            for c in (grande, pequeno):
                c["ct"] = c["base"] = c["medico"] = 3
                c["capacidade"], c["treino_foco"] = 0, []
                base = eng._receita_base(c)
                fracoes.append((eng.custo_estrutura(c) - base * eng.CUSTO_OPERACIONAL) / base)
            # mesmos niveis, mesma fracao da propria receita (antes o pequeno pagava ~3x mais)
            self.assertAlmostEqual(fracoes[0], fracoes[1], delta=0.001)
            self.assertAlmostEqual(fracoes[0], 9 * eng.CUSTO_NIVEL, delta=0.001)
        finally:
            for c, (ct, ba, me, cap, foco) in zip((grande, pequeno), guardado):
                c["ct"], c["base"], c["medico"], c["capacidade"], c["treino_foco"] = ct, ba, me, cap, foco

    def test_jogo_em_casa_desconta_a_operacao(self):
        G = self.G
        for _ in range(8):
            apoio.chamar("POST", "/api/avancar", {"leve": True, "confirmar": True})
        ex = eng.stats_ano(G)["extrato"]
        if ex.get("bilheteria"):
            self.assertAlmostEqual(-ex["operacao_jogo"], ex["bilheteria"] * eng.CUSTO_JOGO_CASA,
                                   delta=10 * len(eng.stats_ano(G)["jogos_casa"]) + 10)

    def test_copa_paga_por_fase_e_vice(self):
        self.assertEqual(eng.premio_fase_copa("copa", 16), int(78_000_000 * 0.02))
        self.assertEqual(eng.premio_fase_copa("lib", 4), int(130_000_000 * 0.07))
        self.assertEqual(eng.premio_fase_copa("copa", 2), 0)          # final paga campeao e vice
        self.assertGreater(eng.premio_fase_copa("copa", 4), eng.premio_fase_copa("copa", 32))

    def test_tela_do_estadio_compara_torcida_e_capacidade(self):
        est = apoio.chamar("GET", "/api/estadio")["tela"]
        nomes = [l["nome"] for l in est["rendimento"]]
        self.assertIn("Torcida num jogo comum", nomes)
        self.assertIn("Operacao de cada jogo em casa", nomes)


if __name__ == "__main__":
    unittest.main()
