# -*- coding: utf-8 -*-
"""Cartoes (feedback do testador, 26/09/2026).

1. Expulso sai de campo de verdade: nenhum lance dele depois do vermelho. O
   bug era de ordem: o periodo sorteava os gols antes dos cartoes, cada evento
   com minuto proprio, e o vermelho podia cair antes de um gol do mesmo jogador.
2. Segundo amarelo na mesma partida vira vermelho, e esse segundo amarelo nao
   entra no acumulado da competicao.
"""

import os
import unittest
from collections import defaultdict

import apoio

eng = apoio.eng


class TestCartoes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(61)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Cartoes"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = apoio.SESSAO.G
        a = [c for c in cls.G["clubes"].values() if c["divisao"] == "A"]
        cls.pares = [(a[i]["id"], a[(i + 1) % len(a)]["id"]) for i in range(len(a))]
        # jogos em serie, com os clubes em tatica de muito cartao, para ter casos
        cls.jogos = []
        eng.rng.seed(62)
        for c in a:
            c["tatica"] = "Pressao total"
        for rodada in range(15):
            for casa, fora in cls.pares:
                for pid in list(cls.G["clubes"][casa]["elenco"]) + list(cls.G["clubes"][fora]["elenco"]):
                    j = cls.G["jogadores"][pid]
                    j["susp"] = {k: 0 for k in eng.COMPETICOES}
                    j["suspensao"] = j["lesao"] = 0
                    j["cond"] = 100
                cls.jogos.append(eng.simular(cls.G, casa, fora, "copa"))

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_expulso_nao_aparece_depois_do_vermelho(self):
        vermelhos = 0
        for r in self.jogos:
            evs = r["eventos"]           # ja ordenados por minuto
            for i, (m, lado, tipo, pid, extra) in enumerate(evs):
                if tipo != "vermelho":
                    continue
                vermelhos += 1
                depois = [e for e in evs[i + 1:] if pid in (e[3], e[4])]
                self.assertEqual(depois, [], "expulso aos %d' seguiu em campo: %s" % (m, depois))
        self.assertGreater(vermelhos, 5, "poucos vermelhos para o teste valer")

    def test_segundo_amarelo_vira_vermelho(self):
        casos = 0
        for r in self.jogos:
            amarelos = defaultdict(list)
            vermelho = {}
            for m, lado, tipo, pid, extra in r["eventos"]:
                if tipo == "amarelo":
                    amarelos[pid].append(m)
                elif tipo == "vermelho":
                    vermelho[pid] = m
            for pid, ms in amarelos.items():
                self.assertLessEqual(len(ms), 2, "tres amarelos no mesmo jogo")
                if len(ms) == 2:
                    casos += 1
                    self.assertIn(pid, vermelho, "dois amarelos e seguiu em campo")
                    self.assertEqual(vermelho[pid], ms[1])
        self.assertGreater(casos, 0, "nenhum segundo amarelo nos jogos do teste")

    def test_registro_mostra_segundo_amarelo_como_um_cartao(self):
        casos = 0
        for r in self.jogos:
            reg = eng.registro_partida(self.G, r)
            pares = [c for c in reg["cartoes"] if c[2] == "segundo_amarelo"]
            casos += len(pares)
            for m, lado, tipo, nome in pares:
                # nem o amarelo nem o vermelho do mesmo lance ficam soltos
                self.assertFalse([c for c in reg["cartoes"] if c[3] == nome and c[0] == m
                                  and c[2] in ("amarelo", "vermelho")])
        self.assertGreater(casos, 0, "nenhum segundo amarelo nos jogos do teste")

    def test_segundo_amarelo_nao_conta_no_acumulado(self):
        G = self.G
        casa, fora = self.pares[0]
        for _ in range(200):
            for pid in G["clubes"][casa]["elenco"] + G["clubes"][fora]["elenco"]:
                j = G["jogadores"][pid]
                j["amar"] = {k: 0 for k in eng.COMPETICOES}
                j["susp"] = {k: 0 for k in eng.COMPETICOES}
                j["suspensao"] = j["lesao"] = 0
            r = eng.simular(G, casa, fora, "sul")
            dois = [pid for pid in set(e[3] for e in r["eventos"] if e[2] == "amarelo")
                    if sum(1 for e in r["eventos"] if e[2] == "amarelo" and e[3] == pid) == 2]
            if dois:
                j = G["jogadores"][dois[0]]
                self.assertEqual(j["amar"]["sul"], 1, "o segundo amarelo entrou no acumulado")
                self.assertGreaterEqual(j["susp"]["sul"], 1, "expulso sem suspensao")
                return
        self.skipTest("nenhum segundo amarelo em 200 jogos")


if __name__ == "__main__":
    unittest.main()
