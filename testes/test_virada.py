# -*- coding: utf-8 -*-
"""A temporada inteira pela API, ate depois da demissao.

O caminho que ja quebrou: a janela de demissao abria, mas a pendencia nunca
saia e voltava a cada semana. O teste nao para em "a janela abre" - vai ate
"escolhi o clube e o jogo continua".
"""

import os
import unittest

import apoio

LIMITE_SEMANAS = 80


class TestVirada(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        apoio.eng.rng.seed(2026)
        novo = apoio.chamar("POST", "/api/novo")
        apoio.chamar("POST", "/api/clube", {"id": novo["clubes"][0]["id"]})

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_temporada_ate_o_clube_novo(self):
        G = apoio.SESSAO.G
        temporada = G["temporada"]

        # 1. joga ate a semana 38 encerrar e parar esperando o clique
        for _ in range(LIMITE_SEMANAS):
            if apoio.eng.temporada_encerrada(G):
                break
            apoio.avancar({"leve": True})
        self.assertTrue(apoio.eng.temporada_encerrada(G), "a temporada nao encerrou")
        self.assertEqual(G["temporada"], temporada, "virou o ano sem o clique")

        # 2. a previa do resumo abre antes da virada
        previa = apoio.chamar("GET", "/api/resumo")["resumo"]
        self.assertTrue(previa)

        # 3. o clique vira o ano e traz o resumo completo junto
        r = apoio.avancar()
        self.assertTrue(r["virou_o_ano"])
        self.assertIn("resumo", r)
        self.assertEqual(G["temporada"], temporada + 1)

        # 4. demissao forcada: a pendencia trava o avanco
        apoio.SESSAO.pendencia = None
        apoio.SESSAO._demitido(G)
        pend = apoio.chamar("GET", "/api/estado")["pendencia"]
        self.assertEqual(pend["tipo"], "novo_clube")
        antigo = G["clube"]
        ofertas = [o["id"] for o in pend["opcoes"]]
        self.assertNotIn(antigo, ofertas, "o clube que demitiu fez oferta")
        apoio.chamar("POST", "/api/avancar", {"confirmar": True}, status=400)
        apoio.chamar("POST", "/api/clube", {"id": antigo}, status=400)

        # 5. escolhe o clube novo: a pendencia sai e o jogo continua
        apoio.chamar("POST", "/api/clube", {"id": ofertas[0]})
        self.assertEqual(G["clube"], ofertas[0])
        self.assertIsNone(apoio.SESSAO.pendencia)
        self.assertNotIn("pendencia_web", G)
        r = apoio.avancar()
        self.assertIsNone(r["pendencia"])
        self.assertIsNone(apoio.chamar("GET", "/api/estado")["pendencia"])

        # 6. reabrir o save nao devolve a janela
        apoio.chamar("POST", "/api/abrir")
        self.assertIsNone(apoio.SESSAO.pendencia)


if __name__ == "__main__":
    unittest.main()
