# -*- coding: utf-8 -*-
"""Classicos nas manchetes e a manchete de abertura do Brasileirao."""

import contextlib
import io
import unittest

import apoio

eng = apoio.eng


def por_nome(G, nome):
    return next(c["id"] for c in G["clubes"].values() if c["nome"] == nome)


class TestClassicos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        eng.rng.seed(41)
        with contextlib.redirect_stdout(io.StringIO()):
            cls.G = eng.criar_mundo("T")
        cls.G["clube"] = por_nome(cls.G, "Mirassol")

    def jogo(self, casa, fora, gc, gf):
        return {"casa": por_nome(self.G, casa), "fora": por_nome(self.G, fora),
                "gc": gc, "gf": gf, "comp": "liga"}

    def feed_da_semana(self, jogos):
        self.G["feed"] = []
        eng.manchetes_da_semana(self.G, jogos, {})
        return [f["texto"] for f in self.G["feed"] if f["tipo"] == "resultado"]

    def test_par_e_simetrico(self):
        G = self.G
        self.assertTrue(eng.eh_classico(G, por_nome(G, "Flamengo"), por_nome(G, "Fluminense")))
        self.assertTrue(eng.eh_classico(G, por_nome(G, "Fluminense"), por_nome(G, "Flamengo")))
        self.assertTrue(eng.eh_classico(G, por_nome(G, "Santos"), por_nome(G, "Corinthians")))
        self.assertFalse(eng.eh_classico(G, por_nome(G, "Flamengo"), por_nome(G, "Santos")))

    def test_classico_sem_goleada_entra_no_corte(self):
        goleadas = [self.jogo("Palmeiras", "Juventude", 5, 0), self.jogo("Botafogo", "Mirassol", 4, 0),
                    self.jogo("Cruzeiro", "Ceara", 6, 1), self.jogo("Bahia", "Sport", 4, 0),
                    self.jogo("Fortaleza", "Vitoria", 5, 1)]
        textos = self.feed_da_semana(goleadas + [self.jogo("Gremio", "Internacional", 1, 0)])
        self.assertEqual(len(textos), eng.RESULTADOS_POR_SEMANA)
        self.assertTrue(textos[0].startswith("Gre-Nal: Gremio 1 x 0 Internacional"), textos)
        self.assertTrue(any(t.startswith("Goleada:") for t in textos[1:]))

    def test_goleada_em_classico_vira_sufixo(self):
        textos = self.feed_da_semana([self.jogo("Flamengo", "Fluminense", 4, 0)])
        self.assertEqual(textos, ["Fla-Flu: Flamengo 4 x 0 Fluminense (Serie A). Goleada."])

    def test_goleada_na_liga_de_fora_so_para_quem_treina_la(self):
        # treinando no Brasil, a liga inglesa nao disputa o feed; treinando la, a
        # goleada da minha liga vira manchete (antes nunca virava)
        G = self.G
        ing = [c for c in G["clubes"].values() if c["divisao"] == "ENG"]
        jogo = {"casa": ing[0]["id"], "fora": ing[1]["id"], "gc": 5, "gf": 0, "comp": "liga"}
        self.assertEqual(self.feed_da_semana([jogo]), [])
        meu = G["clube"]
        G["clube"] = ing[2]["id"]
        try:
            textos = self.feed_da_semana([jogo])
        finally:
            G["clube"] = meu
        self.assertEqual(len(textos), 1)
        self.assertTrue(textos[0].startswith("Goleada: %s 5 x 0 %s" % (ing[0]["nome"], ing[1]["nome"])), textos)

    def test_serie_c_so_para_quem_treina_la(self):
        G = self.G
        c = [x for x in G["clubes"].values() if x["divisao"] == "C"]
        jogo = {"casa": c[0]["id"], "fora": c[1]["id"], "gc": 6, "gf": 0, "comp": "liga"}
        self.assertEqual(self.feed_da_semana([jogo]), [])
        meu = G["clube"]
        G["clube"] = c[2]["id"]
        try:
            self.assertEqual(len(self.feed_da_semana([jogo])), 1)
        finally:
            G["clube"] = meu

    def test_classico_sem_apelido(self):
        textos = self.feed_da_semana([self.jogo("Vasco da Gama", "Botafogo", 0, 0)])
        self.assertEqual(textos, ["Classico: Vasco da Gama 0 x 0 Botafogo (Serie A)."])


class TestAberturaBrasileirao(unittest.TestCase):
    def test_uma_manchete_na_virada_do_estadual(self):
        eng.rng.seed(42)
        with contextlib.redirect_stdout(io.StringIO()):
            G = eng.criar_mundo("T")
            G["clube"] = por_nome(G, "Gremio")
            G["auto"] = True
            G["fase"] = "entretemporada"
            G["semana"] = 0
            eng.montar_estaduais(G)
            eng.iniciar_temporada(G)
            for _ in range(40):
                if G["fase"] == "liga":
                    break
                eng.jogar_semana(G)
        self.assertEqual(G["fase"], "liga")
        aberturas = [f["texto"] for f in G["feed"] if f["tipo"] == "abertura"]
        self.assertEqual(len(aberturas), 1, aberturas)
        est = eng.meu_estadual(G)
        self.assertIn(est["nome"], aberturas[0])
        self.assertIn("Gremio", aberturas[0])
        self.assertIn("Serie A", aberturas[0])

    def test_clube_sem_estadual_nao_gera_nada(self):
        eng.rng.seed(43)
        with contextlib.redirect_stdout(io.StringIO()):
            G = eng.criar_mundo("T")
        G["clube"] = next(c["id"] for c in G["clubes"].values() if c["divisao"] == "ENG")
        G["estaduais"] = {}
        self.assertIsNone(eng.manchete_abertura_brasileirao(G))


if __name__ == "__main__":
    unittest.main()
