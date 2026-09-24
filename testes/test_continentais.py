# -*- coding: utf-8 -*-
"""Libertadores e Sul-Americana com fase de grupos antes do mata-mata."""

import os
import unittest

import apoio

eng = apoio.eng


class TestContinentais(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(5)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_grupos_ate_o_mata_mata(self):
        G = self.G
        lib, sul = G["copas"]["lib"], G["copas"]["sul"]
        for cp in (lib, sul):
            self.assertEqual(len(cp["vivos"]), 32)
            self.assertEqual(len(cp["grupos"]), 8)
            self.assertTrue(all(len(g["times"]) == 4 for g in cp["grupos"]))
            self.assertEqual(eng.fase_da_copa(cp), eng.FASE_GRUPOS)
            self.assertEqual(eng.sorteio_da_copa(G, "lib"), [], "sorteio inventado nos grupos")
        self.assertTrue(set(lib["vivos"]).isdisjoint(sul["vivos"]))

        # a tela mostra os grupos com o meu primeiro
        d = apoio.chamar("POST", "/api/competicoes", {"alvo": "copa:lib"})["tela"]["detalhe"]
        self.assertTrue(d["em_grupos"])
        self.assertTrue(d["grupos"][0]["meu"])

        viu_jogo_de_grupo = False
        while G["semana"] <= eng.SEMANAS_GRUPOS[-1]:
            if G["semana"] in eng.SEMANAS_GRUPOS and G["fase"] == "liga":
                # a agenda do motor traz o jogo de grupo com mando; o Painel mostra
                # a liga primeiro e conta a copa como jogo extra da semana
                agenda = eng.jogos_da_semana(G, G["clube"])
                grupo = [j for j in agenda if j[0] == "lib"]
                if grupo:
                    self.assertIsNotNone(grupo[0][1])
                    proximo = apoio.chamar("GET", "/api/painel")["painel"]["proximo"]
                    self.assertGreaterEqual(proximo["extras"], 1)
                    viu_jogo_de_grupo = True
            apoio.avancar({"leve": True})
        self.assertTrue(viu_jogo_de_grupo, "a agenda nunca trouxe o jogo de grupo")

        # grupos fechados: 16 na Libertadores, playoff de 16 e 8 esperando na Sul-Americana
        self.assertFalse(eng.em_grupos(lib))
        self.assertEqual(len(lib["vivos"]), 16)
        self.assertEqual(eng.fase_da_copa(lib), "Oitavas de final")
        self.assertEqual(len(sul["vivos"]), 16)
        self.assertEqual(len(sul["espera"]), 8)
        self.assertEqual(eng.fase_da_copa(sul), "Playoffs das oitavas")
        terceiros_lib = {eng.classificacao(G, g)[2] for g in lib["grupos"]}
        self.assertTrue(terceiros_lib <= set(sul["vivos"]))
        for g in lib["grupos"]:
            self.assertTrue(all(t["j"] == 6 for t in g["tabela"].values()))
        d = apoio.chamar("POST", "/api/competicoes", {"alvo": "copa:sul"})["tela"]["detalhe"]
        self.assertFalse(d["em_grupos"])
        self.assertEqual(len(d["fases"][0]["jogos"]), 8)

        # depois do playoff, as oitavas tem 16 com os primeiros de grupo
        while G["semana"] <= eng.SEMANAS_SULA[0]:
            apoio.avancar({"leve": True})
        self.assertEqual(sul["espera"], [])
        self.assertEqual(len(sul["vivos"]), 16)
        self.assertEqual(sul["historico"][0]["fase"], "Playoffs das oitavas")


@unittest.skipUnless(apoio.tem_save_real(), "sem brasfut_save.json na pasta do jogo")
class TestSaveAntigo(unittest.TestCase):
    def test_ganha_os_clubes_que_faltam(self):
        hash_antes = apoio.hash_do_save_real()
        apoio.abrir_copia_do_save()
        G = apoio.SESSAO.G
        nomes = {c["nome"] for c in G["clubes"].values() if c["divisao"] == "EX"}
        self.assertTrue({d[0] for d in eng.CLUBES_LIB + eng.CLUBES_SUL} <= nomes)
        ids = [p for c in G["clubes"].values() for p in c["elenco"]]
        self.assertEqual(len(ids), len(set(ids)), "jogador em dois elencos")
        self.assertEqual(apoio.hash_do_save_real(), hash_antes)


if __name__ == "__main__":
    unittest.main()
