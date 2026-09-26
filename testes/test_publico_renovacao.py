# -*- coding: utf-8 -*-
"""Publico com o momento do time e renovacao com a idade (feedback, 26/09/2026).

9. A lotacao acompanha a fase: pontos nos ultimos 5 jogos de liga e a posicao
   na tabela mexem no publico (0,80 a 1,20), sem sortear nada.
14. Na renovacao o piso sobre o salario atual cai com a idade (85% ate 30,
   75% aos 31-32, 65% aos 33-34, 55% dos 35 em diante).
"""

import os
import unittest

import apoio

eng = apoio.eng


class TestPublicoRenovacao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(91)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Publico"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def fase(self, vence):
        """Cinco rodadas de mentira: o meu clube vence (ou perde) todas."""
        G = self.G
        c = G["clubes"][G["clube"]]
        liga = G["ligas"][c["divisao"]]
        adv = [i for i in liga["times"] if i != c["id"]]
        liga["resultados"] = [[[c["id"], adv[k], 3, 0] if vence else [c["id"], adv[k], 0, 3]]
                              for k in range(5)]
        liga["rodada"] = 5
        for i in liga["times"]:
            liga["tabela"][str(i)]["p"] = 0
        liga["tabela"][str(c["id"])]["p"] = 15 if vence else -1
        return c

    def test_comeco_de_ano_e_neutro(self):
        c = self.G["clubes"][self.G["clube"]]
        self.G["ligas"][c["divisao"]]["rodada"] = 0
        self.assertEqual(eng.momento_do_clube(self.G, c)[0], 1.0)

    def test_boa_fase_enche_e_ma_fase_esvazia(self):
        G = self.G
        c = self.fase(True)
        bom, txt = eng.momento_do_clube(G, c)
        self.assertGreater(bom, 1.1)
        self.assertIn("15 pontos", txt)
        c = self.fase(False)
        ruim = eng.momento_do_clube(G, c)[0]
        self.assertLess(ruim, 0.9)
        self.assertGreaterEqual(ruim, 0.80)
        # mesmo sorteio, fases diferentes: o publico acompanha
        fora = next(x for x in G["clubes"].values() if x["divisao"] == "A" and x["id"] != c["id"])
        c["capacidade"] = 10 ** 6
        estado = eng.rng.getstate()
        pub_ruim = eng.publico_e_renda(G, c, fora, "liga")[0]
        self.fase(True)
        eng.rng.setstate(estado)
        pub_bom = eng.publico_e_renda(G, c, fora, "liga")[0]
        self.assertGreater(pub_bom, pub_ruim * 1.2)

    def test_estadio_explica_o_momento(self):
        self.fase(True)
        tela = apoio.chamar("GET", "/api/estadio")["tela"]
        self.assertIn("Momento do time", str(tela))

    def test_veterano_caro_aceita_corte_maior_na_renovacao(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        j = dict(G["jogadores"][c["elenco"][0]])
        j["salario"] = eng.salario_de(j["ovr"]) * 3
        pedidas = {}
        for idade in (27, 32, 34, 36):
            j["idade"] = idade
            pedidas[idade] = eng.salario_referencia(j)
        self.assertEqual(pedidas[27], int(j["salario"] * 0.85))
        self.assertLess(pedidas[32], pedidas[27])
        self.assertLess(pedidas[34], pedidas[32])
        self.assertLess(pedidas[36], pedidas[34])
        self.assertEqual(pedidas[36], int(j["salario"] * 0.55))


if __name__ == "__main__":
    unittest.main()
