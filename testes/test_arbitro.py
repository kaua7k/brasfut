# -*- coding: utf-8 -*-
"""Cartoes com cara de futebol (pedido do jogador, 2026-11-06).

Antes: ~5,4 amarelos e ~0,64 vermelho por jogo, e quase todo jogo entre 3 e 8
cartoes - cada jogador sorteado por conta propria, com a mesma regua em toda
partida. Agora cada partida tem um rigor do arbitro (media 1, teto
RIGOR_ARBITRO_MAX) que vale para os dois times: a media cai para ~4 e a
distribuicao abre - tem jogo sem cartao e jogo que chove cartao."""

import os
import unittest

import apoio

eng = apoio.eng

JOGOS = 400


class TestArbitro(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(71)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Arbitro"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": clubes[0]["id"]})
        G = cls.G = apoio.SESSAO.G
        a = [c["id"] for c in G["clubes"].values() if c["divisao"] in ("A", "B")]
        eng.rng.seed(72)
        cls.amarelos, cls.vermelhos, cls.rigores = [], [], []
        for k in range(JOGOS):
            casa, fora = a[k % len(a)], a[(k * 7 + 3) % len(a)]
            if casa == fora:
                fora = a[(k + 1) % len(a)]
            # elenco inteiro e descansado a cada jogo: mede o arbitro, nao o desgaste
            for cid in (casa, fora):
                for pid in G["clubes"][cid]["elenco"]:
                    j = G["jogadores"][pid]
                    j["cond"], j["lesao"], j["susp"] = 100, 0, {}
                    eng.sincronizar_suspensao(j)
            r = eng.simular(G, casa, fora, "liga")
            cls.amarelos.append(sum(1 for e in r["eventos"] if e[2] == "amarelo"))
            cls.vermelhos.append(sum(1 for e in r["eventos"] if e[2] == "vermelho"))
            cls.rigores.append(r["rigor"])

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_media_de_amarelos_e_vermelhos(self):
        media_am = sum(self.amarelos) / JOGOS
        media_vm = sum(self.vermelhos) / JOGOS
        self.assertGreaterEqual(media_am, 3.3, media_am)
        self.assertLessEqual(media_am, 4.7, media_am)
        self.assertGreaterEqual(media_vm, 0.12, media_vm)
        self.assertLessEqual(media_vm, 0.5, media_vm)

    def test_distribuicao_aberta(self):
        def fatia(f):
            return sum(1 for x in self.amarelos if f(x)) / JOGOS
        self.assertGreaterEqual(fatia(lambda x: x == 0), 0.02, "jogo sem cartao tem que existir")
        self.assertGreaterEqual(fatia(lambda x: x <= 2), 0.20, "jogo tranquilo (0 a 2) e comum")
        self.assertGreaterEqual(fatia(lambda x: x >= 6), 0.08, "jogo pegado (6+) ainda acontece")

    def test_rigor_por_partida(self):
        self.assertLessEqual(max(self.rigores), eng.RIGOR_ARBITRO_MAX)
        self.assertLess(min(self.rigores), 0.6, "tem arbitro que deixa o jogo correr")
        media = sum(self.rigores) / JOGOS
        self.assertGreater(media, 0.8)
        self.assertLess(media, 1.1)


if __name__ == "__main__":
    unittest.main()
