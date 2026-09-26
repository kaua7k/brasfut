# -*- coding: utf-8 -*-
"""Supercopa do Brasil, Recopa e as supercopas de fora (decidido em 2026-09-26).

Campeao contra campeao, com os titulos do ano anterior: Supercopa do Brasil
(Brasileirao x Copa do Brasil) e Recopa (Libertadores x Sul-Americana, ida e
volta) numa rodada do estadual; Supercopa da UEFA e as nacionais de fora na
primeira semana da liga, em segundo plano. Primeiro ano nao tem supercopa.
"""

import os
import unittest

import apoio

eng = apoio.eng


class TestSupercopas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(41)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Super"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def ano_que_acabou(self):
        """Campeoes de mentira do ano anterior, com o meu clube na Supercopa."""
        G = self.G
        cp = G["copas"]
        eu = G["clube"]
        A = [c["id"] for c in G["clubes"].values() if c["divisao"] == "A" and c["id"] != eu]
        G["class_A_anterior"] = [eu] + A
        cp["copa"]["campeao"] = A[0]
        cp["lib"]["campeao"] = cp["lib"]["vivos"][0]
        cp["sul"]["campeao"] = cp["sul"]["vivos"][0]
        cp["ucl"]["campeao"] = cp["ucl"]["vivos"][0]
        cp["uel"]["campeao"] = cp["uel"]["vivos"][0]
        ant = G.setdefault("class_ext_anterior", {})
        for k in eng.SUPERCOPAS_NACIONAIS:
            ant[k] = list(G["ligas"][k]["times"])
        return A[0]

    def test_primeiro_ano_sem_supercopa(self):
        self.assertNotIn("supercopa", self.G["copas"])
        self.assertNotIn("recopa", self.G["copas"])

    def test_virada_monta_e_o_estadual_joga(self):
        G = self.G
        rival = self.ano_que_acabou()
        eng.montar_copas(G)
        cp = G["copas"]
        self.assertEqual(sorted(cp["supercopa"]["vivos"]), sorted([G["clube"], rival]))
        self.assertTrue(cp["recopa"]["final_ida_volta"])
        self.assertIn("supercopa_uefa", cp)
        for k, nome in eng.SUPERCOPAS_NACIONAIS.items():
            self.assertEqual(cp["sc_" + k]["nome"], nome)
            self.assertEqual(cp["sc_" + k]["semanas"], [eng.SEMANA_SUPERCOPAS])

        # comeca o ano pelo estadual: a Supercopa sai na rodada 2, a Recopa na 3
        eng.montar_estaduais(G)
        G["fase"] = "entretemporada"
        eng.iniciar_estaduais(G)
        visto = False
        for _ in range(6):
            if G["fase"] != "estadual":
                break
            rodada = int(G["semana_est"])
            if rodada == eng.SUPERCOPA_BR_EST:
                jogos = eng.jogos_da_semana(G, G["clube"])
                self.assertIn("supercopa", [j[0] for j in jogos], "o tecnico nao ve a Supercopa")
            meus = eng.avancar_semana(G)
            if rodada == eng.SUPERCOPA_BR_EST:
                self.assertTrue(any(r["comp"] == "supercopa" for r in meus))
                visto = True
        self.assertTrue(visto)
        self.assertIn(cp["supercopa"]["campeao"], (G["clube"], rival))
        self.assertIsNotNone(cp["recopa"]["campeao"])
        # ida e volta: dois jogos no historico da decisao
        self.assertIsNotNone(cp["recopa"]["historico"][0]["jogos"][0]["volta"])
        self.assertIsNone(cp["supercopa"]["historico"][0]["jogos"][0]["volta"])
        campeao = G["clubes"][cp["supercopa"]["campeao"]]
        self.assertGreaterEqual(campeao["titulos"].get("Supercopa do Brasil", 0), 1)

    def test_liga_ganhou_as_duas_entao_vem_o_vice(self):
        G = self.G
        eu = G["clube"]
        vice = [c["id"] for c in G["clubes"].values() if c["divisao"] == "A" and c["id"] != eu][0]
        G["class_A_anterior"] = [eu, vice]
        out = dict(eng.montar_supercopas(G, {"copa": {"campeao": eu}}))
        self.assertEqual(out["supercopa"]["vivos"], [eu, vice])


if __name__ == "__main__":
    unittest.main()
