# -*- coding: utf-8 -*-
"""Regras que seguram a inflacao de notas e a fila de livres."""

import io
import contextlib
import unittest

import apoio

eng = apoio.eng


class TestBalanco(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        eng.rng.seed(31)
        with contextlib.redirect_stdout(io.StringIO()):
            cls.G = eng.criar_mundo("T")
        cls.G["clube"] = next(c["id"] for c in cls.G["clubes"].values() if c["divisao"] == "A")

    def test_teto_sem_catraca(self):
        G = self.G
        for j in list(G["jogadores"].values())[:3000]:
            teto = eng.teto_maximo(G, j)
            self.assertLessEqual(teto, max(eng.TETO_REVISAO, j["ovr"]))
            if j["ovr"] >= eng.TETO_REVISAO:
                self.assertEqual(teto, j["ovr"], "folga acima da nota vira catraca")

    def test_potencial_sorteado_tem_teto(self):
        eng.rng.seed(1)
        tetos = [eng.sortear_potencial(55, 16, 1.0) for _ in range(20000)]
        self.assertLessEqual(max(tetos), 96)
        self.assertLess(sum(t >= 90 for t in tetos) / len(tetos), 0.03)

    def test_base_nao_revisa_teto(self):
        G = self.G
        j = next(G["jogadores"][p] for c in G["clubes"].values() for p in c.get("base_elenco", []))
        j["ovr_ini"] = j["ovr"] - 10     # cresceu muito no ano: antes isso dava +3 de teto
        self.assertEqual(eng.revisar_potencial(G, j), 0)

    def test_correcao_de_save_inflado(self):
        G = {"jogadores": {}, "correcao_notas": 0}
        for i in range(2000):
            G["jogadores"][i] = {"id": i, "ovr": 99 if i < 100 else 80, "pot": 99, "idade": 25,
                                 "categoria": "pro", "salario": 0, "valor": 0}
        eng.corrigir_inflacao(G)
        notas = [j["ovr"] for j in G["jogadores"].values()]
        self.assertLessEqual(max(notas), 93)
        self.assertLess(sum(n >= 88 for n in notas), 10)
        self.assertEqual(G["correcao_notas"], 2)
        self.assertEqual(eng.corrigir_inflacao(G), 0, "a correcao roda uma vez so")

    def test_ia_contrata_livre_bom(self):
        G = self.G
        j = eng.novo_jogador(G, "ATA", 84, set(), idade=26)
        j["ovr"], j["pot"] = 84, 84
        j["salario"] = eng.salario_devido(j)
        j["clube"] = None
        G["livres"].append(j["id"])
        eng.contratar_livres_ia(G)
        self.assertIsNotNone(j["clube"], "livre de 84 ficou sem clube")
        self.assertNotIn(j["id"], G["livres"])


if __name__ == "__main__":
    unittest.main()
