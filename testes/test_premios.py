# -*- coding: utf-8 -*-
"""Premios do ano e selecao do campeonato (Onda 2, item 6).

Melhor jogador pela media de nota (com minimo de jogos), artilheiro pelos
gols, revelacao ate 21 anos e a selecao num 4-3-3. Na virada: historico no
jogador, manchete e um pequeno ganho de valor que dura ate o ano seguinte.
Nada disso usa o rng.
"""

import os
import unittest

import apoio
from api import dto

eng = apoio.eng
SESSAO = apoio.SESSAO


def zerar_ano(G):
    for j in G["jogadores"].values():
        j["j"] = j["g"] = j["a"] = 0
        j["nota_soma"], j["nota_j"] = 0.0, 0


def jogou(j, jogos, media, gols=0):
    j["j"], j["g"] = jogos, gols
    j["nota_j"], j["nota_soma"] = jogos, round(media * jogos, 1)


class TestPremios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(606)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Premios"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def setUp(self):
        G = self.G
        zerar_ano(G)
        for j in G["jogadores"].values():
            j.pop("premios", None)
            j.pop("premio_valor", None)
        self.liga = G["ligas"]["A"]
        for t in self.liga["tabela"].values():
            t["j"] = 38
        self.meu = G["clubes"][G["clube"]]
        self.outro = G["clubes"][[c for c in self.liga["times"] if c != G["clube"]][0]]

    def pro(self, clube, pos, idade_max=99):
        return next(G_j for G_j in (self.G["jogadores"][p] for p in clube["elenco"])
                    if G_j["pos"] == pos and not eng.da_base(G_j) and G_j["idade"] <= idade_max)

    def test_melhor_exige_minimo_de_jogos(self):
        craque = self.pro(self.meu, "MEI")
        relampago = self.pro(self.outro, "MEI")
        jogou(craque, 30, 7.4)
        jogou(relampago, 12, 9.5)       # abaixo das 19 rodadas: fora da disputa
        p = eng.premios_do_ano(self.G, "A")
        self.assertEqual(p["minimo"], 19)
        self.assertEqual(p["melhor"]["id"], craque["id"])
        self.assertNotIn(relampago["id"], [g["id"] for g in p["selecao"]])

    def test_artilheiro_desempata_por_menos_jogos(self):
        a = self.pro(self.meu, "ATA")
        b = self.pro(self.outro, "ATA")
        jogou(a, 36, 6.5, gols=18)
        jogou(b, 30, 6.4, gols=18)
        p = eng.premios_do_ano(self.G, "A")
        self.assertEqual(p["artilheiro"]["id"], b["id"])
        self.assertEqual(p["artilheiro"]["gols"], 18)

    def test_revelacao_so_ate_21(self):
        velho = self.pro(self.outro, "ATA")
        velho["idade"] = 29
        jogou(velho, 30, 8.0)
        jovens = [j for c in self.liga["times"] for j in
                  (self.G["jogadores"][p] for p in self.G["clubes"][c]["elenco"])
                  if not eng.da_base(j) and j["idade"] <= 21]
        self.assertTrue(jovens, "mundo sem jogador de ate 21 anos")
        jogou(jovens[0], 25, 7.0)
        p = eng.premios_do_ano(self.G, "A")
        self.assertEqual(p["melhor"]["id"], velho["id"])
        self.assertEqual(p["revelacao"]["id"], jovens[0]["id"])

    def test_selecao_no_433(self):
        for cid in self.liga["times"]:
            for pid in self.G["clubes"][cid]["elenco"]:
                j = self.G["jogadores"][pid]
                if not eng.da_base(j):
                    jogou(j, 25, 6.0 + (pid % 30) / 10.0)
        p = eng.premios_do_ano(self.G, "A")
        pos = [g["pos"] for g in p["selecao"]]
        self.assertEqual(len(pos), 11)
        for vaga, n in eng.SELECAO_VAGAS:
            self.assertEqual(pos.count(vaga), n, vaga)
        # dentro de cada posicao, a maior media primeiro
        zag = [g["media"] for g in p["selecao"] if g["pos"] == "ZAG"]
        self.assertEqual(zag, sorted(zag, reverse=True))

    def test_liga_sem_jogo_nao_premia(self):
        p = eng.premios_do_ano(self.G, "A")
        self.assertIsNone(p)

    def test_premiar_grava_historico_valor_e_manchete_sem_rng(self):
        craque = self.pro(self.meu, "MEI")
        jogou(craque, 30, 7.8, gols=21)
        valor_antes = eng.valor_de(craque["ovr"], craque["idade"], craque["pot"])
        estado = eng.rng.getstate()
        feed_antes = len(self.G.get("feed", []))
        eng.premiar_ano(self.G)
        self.assertEqual(eng.rng.getstate(), estado, "premiar_ano usou o rng")
        nomes = [p["nome"] for p in craque["premios"]]
        liga = eng.nome_da_liga(self.G, "A")
        self.assertIn("Melhor jogador da %s" % liga, nomes)
        self.assertIn("Artilheiro da %s" % liga, nomes)
        self.assertEqual(craque["premio_valor"], eng.PREMIO_VALOR["melhor"])
        self.assertGreater(craque["valor"], valor_antes)
        # o ganho sobrevive a virada: evoluir recalcula o valor com ele
        self.assertEqual(eng.valor_jogador(craque),
                         int(valor_antes * 1.12 / 1000) * 1000)
        textos = [f["texto"] for f in self.G["feed"][feed_antes:]]
        self.assertTrue(any(craque["nome"] in t and "melhor jogador" in t for t in textos))
        # no ano seguinte, sem premio, a vitrine acaba
        zerar_ano(self.G)
        eng.premiar_ano(self.G)
        self.assertNotIn("premio_valor", craque)
        # melhor, artilheiro e a vaga de meia na selecao; nada novo no ano vazio
        self.assertEqual(len(craque["premios"]), 3)

    def test_resumo_e_ficha_mostram(self):
        craque = self.pro(self.meu, "MEI")
        jogou(craque, 30, 7.8)
        r = eng.apurar_temporada(self.G)
        self.assertEqual(r["premios_ano"]["melhor"]["id"], craque["id"])
        d = dto.resumo(r, previa=True)
        secoes = {s["titulo"]: s for s in d["secoes"]}
        titulo = "Premios da %s" % eng.nome_da_liga(self.G, "A")
        self.assertIn(titulo, secoes)
        self.assertTrue(any(craque["nome"] in i["texto"] and i["estado"] == "ok"
                            for i in secoes[titulo]["itens"]))
        eng.premiar_ano(self.G)
        ficha = apoio.chamar("POST", "/api/ficha", {"id": craque["id"]})["ficha"]
        self.assertTrue(ficha["premios"])


if __name__ == "__main__":
    unittest.main()
