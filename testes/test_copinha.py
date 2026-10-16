# -*- coding: utf-8 -*-
"""Copinha (Copa Sao Paulo de Futebol Junior): 32 academias, mata-mata no
estadual, nada no profissional, premio, taca do clube e vitrine aos destaques."""

import contextlib
import io
import os
import unittest

import apoio

eng = apoio.eng


def mundo_novo(semente, divisao="D"):
    """Carreira nova pela API: a Copinha de janeiro ja vem jogada."""
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(semente)
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Copinha",
                                                "opcoes": {"sem_demissao": True}})["clubes"]
    alvo = [c for c in clubes if c["divisao"] == divisao][-1]
    apoio.chamar("POST", "/api/clube", {"id": alvo["id"]})
    return apoio.SESSAO.G


def mundo_no_estadual(semente, nome="Gremio"):
    """Mundo pelo motor, ja na pre-temporada, com o estadual comecando."""
    eng.rng.seed(semente)
    with contextlib.redirect_stdout(io.StringIO()):
        G = eng.criar_mundo("T")
        G["clube"] = next(c["id"] for c in G["clubes"].values() if c["nome"] == nome)
        G["auto"] = True
        G["fase"] = "entretemporada"
        G["semana"] = 0
        eng.montar_estaduais(G)
        eng.iniciar_temporada(G)
    return G


def retrato(G):
    return {pid: (j["moral"], j["forma"], j["cond"], j["j"], j["g"], j["a"], j["ovr"], j["pot"])
            for pid, j in G["jogadores"].items()}


class TestCopinha(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_carreira_nova_ja_tem_a_copinha_de_janeiro(self):
        G = mundo_novo(501)
        cp = eng.copinha(G)
        self.assertIsNotNone(cp)
        self.assertEqual(len(cp["times"]), eng.COPINHA_CLUBES)
        self.assertEqual(len(set(cp["times"])), eng.COPINHA_CLUBES)
        # clube da Serie D com academia fraca: entra assim mesmo
        self.assertIn(G["clube"], cp["times"])
        self.assertTrue(all(G["clubes"][c]["divisao"] in eng.DIVISOES_BR for c in cp["times"]))
        self.assertEqual([h["fase"] for h in cp["historico"]],
                         ["Terceira fase", "Oitavas de final", "Quartas de final", "Semifinal", "FINAL"])
        self.assertIsNotNone(cp["campeao"])
        campeao = G["clubes"][cp["campeao"]]
        self.assertIn(eng.COPINHA_NOME, [t["nome"] for t in campeao["titulos_hist"]])
        self.assertTrue(any("Copinha" in n for n in G["noticias"]))
        # a taca e do sub-20: nao entra na conta do ano (diretoria, resumo)
        self.assertNotIn(eng.COPINHA_NOME, eng.titulos_da_temporada(G, cp["campeao"]))

    def test_tela_de_competicoes(self):
        G = mundo_novo(502)
        tela = apoio.chamar("POST", "/api/competicoes", {"alvo": "copinha"})["tela"]
        item = next(i for i in tela["lista"] if i["id"] == "copinha")
        self.assertTrue(item["meu"])
        self.assertTrue(item["estado"].startswith("campeao"))
        d = tela["detalhe"]
        self.assertEqual(d["tipo"], "mata-mata")
        self.assertEqual(d["titulo"], eng.COPINHA_NOME)
        self.assertEqual(d["campeao"], G["clubes"][eng.copinha(G)["campeao"]]["nome"])
        self.assertEqual(len(d["fases"]), 5)
        self.assertEqual([len(f["jogos"]) for f in d["fases"]], [16, 8, 4, 2, 1])
        self.assertTrue(any(j["meu"] for j in d["fases"][0]["jogos"]))
        self.assertIsNotNone(d["situacao"])
        self.assertTrue(d["destaques"])
        self.assertTrue(d["nota_destaques"])

    def test_nada_no_profissional_e_sem_mexer_no_rng(self):
        G = mundo_no_estadual(503)
        cp = eng.copinha(G)
        self.assertIsNotNone(cp)
        self.assertEqual(cp["fase"], 0)
        antes = retrato(G)
        estado_rng = eng.rng.getstate()
        with contextlib.redirect_stdout(io.StringIO()):
            eng.concluir_copinha(G)
        self.assertEqual(eng.rng.getstate(), estado_rng, "a Copinha nao pode consumir o rng do jogo")
        depois = retrato(G)
        destaques = {d["id"] for d in cp["destaques"]}
        self.assertTrue(destaques)
        for pid, a in antes.items():
            if pid in destaques:
                d = depois[pid]
                self.assertEqual(a[:6], d[:6])          # moral, forma, condicao, jogos, gols
                self.assertIn(d[6] - a[6], (0, 1))      # um ponto de overall, no maximo
                self.assertIn(d[7] - a[7], (0, 1, 2))   # teto revisto ate 2
                self.assertTrue(G["jogadores"][pid]["premios"])
            else:
                self.assertEqual(a, depois[pid])

    def test_uma_fase_por_rodada_do_estadual(self):
        G = mundo_no_estadual(504)
        cp = eng.copinha(G)
        with contextlib.redirect_stdout(io.StringIO()):
            for rodada in range(1, 6):
                self.assertEqual(G["semana_est"], rodada)
                eng.jogar_semana(G)
                self.assertEqual(cp["fase"], rodada)
                self.assertEqual(cp["historico"][-1]["rodada_est"], rodada)
        self.assertIsNotNone(cp["campeao"])
        self.assertEqual(G["fase"], "estadual")       # o estadual segue; a Copinha acabou
        meu = G["clube"]
        if meu in cp["times"]:
            self.assertTrue(any(n.split(": ", 1)[1].startswith(("Copinha", "COPINHA"))
                                for n in G["noticias"]))

    def test_campeao_meu_recebe_premio_no_extrato(self):
        G = mundo_no_estadual(505)
        cp = eng.copinha(G)
        meu = G["clube"]
        if meu not in cp["times"]:
            cp["times"][-1] = meu
        outro = next(c for c in cp["times"] if c != meu)
        caixa = G["clubes"][meu]["dinheiro"]
        eng.coroar_copinha(G, cp, {"a": meu, "b": outro, "ida": [2, 1], "volta": None,
                                   "penaltis": None, "venc": meu})
        self.assertEqual(G["clubes"][meu]["dinheiro"] - caixa, eng.COPINHA_PREMIO)
        self.assertEqual(eng.stats_ano(G)["extrato"]["premio_copinha"], eng.COPINHA_PREMIO)
        self.assertIn("premio_copinha", dict(eng.EXTRATO))
        from api import dto
        self.assertIn("premio_copinha", dto.DICA_EXTRATO)
        self.assertEqual(eng.campanha_copinha(G, meu), "campeao")
        self.assertTrue(any("COPINHA" in n for n in G["noticias"]))
        # a sala do treinador nao ganha a taca
        self.assertFalse(any(t["nome"] == eng.COPINHA_NOME
                             for p in eng.carreira(G) for t in p.get("titulos", [])))

    def test_save_antigo_sem_copinha(self):
        G = mundo_no_estadual(506)
        G.pop("copinha", None)
        G.pop("convocacao", None)
        eng.migrar(G)
        self.assertIsNone(G["copinha"])
        self.assertIsNone(eng.copinha(G))
        with contextlib.redirect_stdout(io.StringIO()):
            eng.jogar_semana(G)                # semana do estadual sem Copinha nao quebra
        self.assertEqual(G["semana_est"], 2)


if __name__ == "__main__":
    unittest.main()
