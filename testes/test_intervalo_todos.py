# -*- coding: utf-8 -*-
"""Intervalo em todo jogo meu: liga, copa (grupo e mata-mata) e estadual.

Semana com mais de um jogo meu (liga e copa, ida e volta) abre um intervalo
depois do outro, e a semana usa exatamente os resultados jogados ao vivo."""

import os
import unittest

import apoio

eng = apoio.eng


def jogar_semana_toda(test):
    """'Jogar' e segue cada intervalo sem mexer. Devolve as competicoes que
    pararam, os placares finais vistos na tela e a resposta final."""
    G = test.G
    r = apoio.chamar("POST", "/api/avancar", {"confirmar": True, "intervalo": True})
    paradas, placares = [], []
    while "intervalo" in r:
        paradas.append(r["intervalo"]["comp"])
        r = apoio.chamar("POST", "/api/partida/segundo-tempo", {})
        if "partida" in r:
            placares.append((r["partida"]["times"], r["partida"]["placar"]))
    return paradas, placares, r


class TestIntervaloLigaECopa(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(404)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Intervalo Todos",
                                                    "opcoes": {"sem_demissao": True}})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": clubes[0]["id"]})   # Flamengo: liga, Libertadores, Copa do Brasil
        cls.G = apoio.SESSAO.G
        cls.G["intervalo_interativo"] = True
        while cls.G["semana"] < 3:
            apoio.avancar({"leve": True})

    @classmethod
    def tearDownClass(cls):
        apoio.SESSAO.intervalo = None
        apoio.SESSAO.fila_ao_vivo = []
        eng.PARTIDA_PRONTA.clear()
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_a_semana_de_liga_e_libertadores_para_nos_dois(self):
        G = self.G
        self.assertEqual(G["semana"], 3)
        fila = eng.meus_jogos_ao_vivo(G)
        self.assertEqual([j["comp"] for j in fila], ["liga", "lib"])
        paradas, placares, r = jogar_semana_toda(self)
        self.assertEqual(len(paradas), 2)
        self.assertIn("Libertadores", paradas[1])
        self.assertEqual(G["semana"], 4, "a semana andou depois do ultimo intervalo")
        self.assertEqual(eng.PARTIDA_PRONTA, {}, "a semana usou os jogos prontos")
        # o placar visto ao fim do 1o jogo e o que ficou no historico
        hist = eng.historico_do_clube(G)[-2:]
        times, placar = placares[0]
        self.assertEqual([hist[0]["casa_nome"], hist[0]["fora_nome"]], times)
        self.assertEqual([hist[0]["gc"], hist[0]["gf"]], placar)
        self.assertEqual(hist[1]["comp"], "lib")

    def test_b_semana_de_copa_do_brasil_para_em_todo_jogo_meu(self):
        G = self.G
        self.assertEqual(G["semana"], 4)
        fila = eng.meus_jogos_ao_vivo(G)
        self.assertIn("copa", [j["comp"] for j in fila])
        antes = len(G["historico_meus"])
        paradas, _placares, _r = jogar_semana_toda(self)
        self.assertEqual(len(paradas), len(fila))
        self.assertEqual(len(G["historico_meus"]) - antes, len(fila), "nenhum jogo meu passou direto")
        self.assertEqual(eng.PARTIDA_PRONTA, {})

    def test_c_desligado_nao_para(self):
        G = self.G
        G["intervalo_interativo"] = False
        try:
            r = apoio.chamar("POST", "/api/avancar", {"confirmar": True, "intervalo": True})
            self.assertNotIn("intervalo", r)
        finally:
            G["intervalo_interativo"] = True


class TestIntervaloEstadual(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(303)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Intervalo Estadual",
                                                    "opcoes": {"sem_demissao": True}})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": clubes[0]["id"]})
        G = cls.G = apoio.SESSAO.G
        G["intervalo_interativo"] = True
        G["fase"], G["semana"] = "entretemporada", 0
        eng.iniciar_estaduais(G)

    @classmethod
    def tearDownClass(cls):
        apoio.SESSAO.intervalo = None
        apoio.SESSAO.fila_ao_vivo = []
        eng.PARTIDA_PRONTA.clear()
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_rodada_do_estadual_para_no_intervalo(self):
        G = self.G
        # o clube pode folgar na rodada (estadual de numero impar): ate a primeira com jogo
        for _ in range(4):
            if eng.meus_jogos_ao_vivo(G):
                break
            apoio.avancar({"leve": True})
        self.assertEqual(G["fase"], "estadual")
        fila = eng.meus_jogos_ao_vivo(G)
        self.assertTrue(fila)
        self.assertEqual(fila[0]["comp"], "estadual")
        est = eng.meu_estadual(G)
        antes = len(G["historico_meus"])
        paradas, _p, _r = jogar_semana_toda(self)
        self.assertEqual(len(paradas), len(fila))
        self.assertIn(est["nome"], paradas[0])
        self.assertEqual(len(G["historico_meus"]) - antes, len(fila))
        self.assertEqual(eng.PARTIDA_PRONTA, {})


if __name__ == "__main__":
    unittest.main()
