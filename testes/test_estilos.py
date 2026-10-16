# -*- coding: utf-8 -*-
"""Identidade tatica da maquina: estilo por clube e mentalidade por adversario."""

import os
import unittest

import apoio

eng = apoio.eng


class TestEstilos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(503)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Estilo",
                                                    "opcoes": {"sem_demissao": True}})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_toda_maquina_tem_estilo_e_o_meu_clube_nao_muda(self):
        G = self.G
        meu = G["clubes"][G["clube"]]
        self.assertNotIn("estilo", meu)
        self.assertEqual(meu["tatica"], "Equilibrado")
        outros = [c for c in G["clubes"].values() if c["id"] != meu["id"]]
        self.assertTrue(all(c.get("estilo") in eng.ESTILOS for c in outros))
        for c in outros[:50]:
            e = eng.ESTILOS[c["estilo"]]
            self.assertEqual(c["tatica"], e["base"])
            for eixo, valor in e["plano"].items():
                self.assertEqual(c["plano"][eixo], valor)
        # todos os estilos aparecem no mundo
        self.assertEqual({c["estilo"] for c in outros}, set(eng.ESTILOS))

    def test_grande_propoe_e_pequeno_se_fecha(self):
        G = self.G
        def propoe(c):
            return c["estilo"] in ("ofensivo", "posse")
        grandes, pequenos = [], []
        for div in ["A", "B", "C", "D"] + [l[0] for l in eng.LIGAS_SUL[:4]]:
            cs = sorted((c for c in G["clubes"].values() if c["divisao"] == div and c["id"] != G["clube"]),
                        key=lambda c: c["reputacao"])
            terco = max(1, len(cs) // 3)
            pequenos += cs[:terco]
            grandes += cs[-terco:]
        taxa = lambda xs: sum(1 for c in xs if propoe(c)) / float(len(xs))
        self.assertGreater(taxa(grandes), taxa(pequenos) + 0.15)

    def test_mentalidade_do_jogo_segue_a_forca_dentro_da_faixa(self):
        G = self.G
        A = sorted((c for c in G["clubes"].values() if c["divisao"] == "A" and c["id"] != G["clube"]),
                   key=lambda c: eng._forca_crua(G, c, eng.forcas(G, c)[2]))
        fraco, forte = A[0], A[-1]
        esc_fr, esc_fo = eng.forcas(G, fraco)[2], eng.forcas(G, forte)[2]
        t_fraco = eng.tatica_do_jogo(G, fraco, esc_fr, forte, esc_fo, False)
        t_forte = eng.tatica_do_jogo(G, forte, esc_fo, fraco, esc_fr, True)
        esc = eng.ESCADA_TATICA
        lo, hi = eng.ESTILOS[fraco["estilo"]]["faixa"]
        self.assertTrue(lo <= esc.index(t_fraco) <= hi)
        self.assertLessEqual(esc.index(t_fraco), esc.index(eng.ESTILOS[fraco["estilo"]]["base"]))
        self.assertGreaterEqual(esc.index(t_forte), esc.index(eng.ESTILOS[forte["estilo"]]["base"]))

    def test_partida_devolve_a_mentalidade_de_base_e_o_painel_mostra_o_estilo(self):
        G = self.G
        a, b = [c for c in G["clubes"].values() if c["divisao"] == "B"][:2]
        antes = (a["tatica"], b["tatica"])
        eng.simular(G, a["id"], b["id"], "liga")
        self.assertEqual((a["tatica"], b["tatica"]), antes)
        proximo = apoio.chamar("GET", "/api/painel")["painel"]["proximo"]
        if proximo["tipo"] in ("jogo", "copa") and proximo.get("ataque", {}).get("dele") is not None:
            self.assertIn(proximo["estilo"]["tatica"], eng.TATICAS)

    def test_save_antigo_ganha_estilo_na_migracao(self):
        G = self.G
        c = next(x for x in G["clubes"].values() if x["id"] != G["clube"])
        c.pop("estilo")
        eng.migrar(G)
        self.assertIn(c["estilo"], eng.ESTILOS)


if __name__ == "__main__":
    unittest.main()
