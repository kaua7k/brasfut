# -*- coding: utf-8 -*-
"""A partida que fica: historico das ultimas, notas que sobrevivem ao save e
media de nota do ano (Onda 2, item 2).
"""

import os
import unittest

import apoio

eng = apoio.eng


def mundo_novo(semente, divisao="A"):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(semente)
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Partida"})["clubes"]
    apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == divisao][0]["id"]})
    return apoio.SESSAO.G


def ate_jogar(G, jogos=1, limite=40):
    """Avanca ate o meu clube ter jogado `jogos` partidas guardadas."""
    for _ in range(limite):
        if len(G.get("historico_meus", [])) >= jogos:
            return
        apoio.avancar()
        G = apoio.SESSAO.G
    raise AssertionError("o clube nao jogou %d vezes em %d semanas" % (jogos, limite))


class TestPartida(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        mundo_novo(53)
        ate_jogar(apoio.SESSAO.G, jogos=3)
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_registro_tem_placar_gols_notas_e_melhor(self):
        reg = self.G["historico_meus"][-1]
        self.assertIn(self.G["clube"], (reg["casa"], reg["fora"]))
        self.assertEqual(len(reg["gols"]), reg["gc"] + reg["gf"])
        for minuto, lado, autor, _assist in reg["gols"]:
            self.assertTrue(1 <= minuto <= 92 and lado in (0, 1) and autor)
        self.assertGreaterEqual(len(reg["notas"]), 22)
        self.assertTrue(all(3.0 <= n[4] <= 10.0 for n in reg["notas"]))
        self.assertEqual(reg["melhor"]["nota"], max(n[4] for n in reg["notas"]))
        self.assertEqual(sum(reg["stats"]["posse"]), 100)
        self.assertTrue(reg["comp_nome"] and reg["rodada"])

    def test_historico_so_guarda_as_ultimas(self):
        G = self.G
        velho = list(G["historico_meus"])
        extra = [dict(G["ultimos_meus"][0])] * (eng.HISTORICO_PARTIDAS + 3)
        try:
            eng.guardar_historico(G, extra)
            self.assertEqual(len(G["historico_meus"]), eng.HISTORICO_PARTIDAS)
        finally:
            G["historico_meus"] = velho

    def test_nota_somada_e_media_do_ano(self):
        G = self.G
        reg = G["historico_meus"][-1]
        meus = [n for n in reg["notas"] if n[0] == reg["eu"]]
        for _lado, pid, _nome, _vaga, _nota in meus:
            j = G["jogadores"][pid]
            self.assertGreaterEqual(j["nota_j"], 1)
            self.assertLessEqual(j["nota_j"], j["j"])
            media = eng.media_nota(j)
            self.assertTrue(3.0 <= media <= 10.0, media)
        self.assertIsNone(eng.media_nota({"nota_soma": 0.0, "nota_j": 0}))

    def test_notas_sobrevivem_a_salvar_e_carregar(self):
        G = self.G
        eng.salvar(G, apoio.SAVE_TESTE)
        H = eng.carregar(apoio.SAVE_TESTE)
        r = H["ultimos_meus"][-1]
        lado = "casa" if r["casa"] == H["clube"] else "fora"
        xi = r["xi"][lado]
        self.assertTrue(xi)
        # o id volta a ser int e acha o jogador e a nota de novo
        for pid in xi:
            self.assertIsInstance(pid, int)
            self.assertIn(pid, H["jogadores"])
            self.assertIn(pid, r["notas"])
        self.assertEqual(H["historico_meus"], G["historico_meus"])

    def test_save_antigo_comeca_a_media_do_zero(self):
        G = self.G
        j = next(iter(G["jogadores"].values()))
        guardado = (j["nota_soma"], j["nota_j"])
        try:
            del j["nota_j"]
            j["nota_soma"] = 0.0
            eng.migrar(G)
            self.assertEqual((j["nota_soma"], j["nota_j"]), (0.0, 0))
        finally:
            j["nota_soma"], j["nota_j"] = guardado

    def test_liga_de_fora_nao_se_chama_brasileirao(self):
        G = self.G
        div = next(d for d in G["ligas"] if d not in eng.DIVISOES_BR)
        clube = next(c for c in G["clubes"].values() if c["divisao"] == div)
        nome = eng.nome_competicao(G, "liga", clube)
        self.assertNotIn("Brasileirao", nome)
        self.assertEqual(nome, eng.nome_da_liga(G, div))


if __name__ == "__main__":
    unittest.main()
