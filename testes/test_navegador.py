# -*- coding: utf-8 -*-
"""Modo navegador (versao do celular): o despachante que o Web Worker chama
dentro do Pyodide. Aqui roda no Python de sempre - o que se testa e o
contrato (JSON de ida e volta, aviso de que o save mudou) e que a medicao de
desempenho nao toca na carreira aberta nem no save."""

import json
import os
import shutil
import tempfile
import unittest

import apoio
from api import navegador as nav

eng = apoio.eng
SESSAO = apoio.SESSAO


class TestNavegador(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def setUp(self):
        self.save_antes, self.base_antes, self.pasta_antes = eng.SAVE, SESSAO._save_base, nav.PASTA
        self.pasta = tempfile.mkdtemp(prefix="brasfut-nav-")

    def tearDown(self):
        eng.SAVE, SESSAO._save_base, nav.PASTA = self.save_antes, self.base_antes, self.pasta_antes
        shutil.rmtree(self.pasta, ignore_errors=True)

    def pedir(self, metodo, caminho, corpo=None):
        return json.loads(nav.pedido(metodo, caminho, None if corpo is None else json.dumps(corpo)))

    def test_iniciar_aponta_o_save_para_a_pasta(self):
        caminho = nav.iniciar(self.pasta)
        self.assertEqual(caminho, os.path.join(self.pasta, "brasfut_save.json"))
        self.assertEqual(eng.SAVE, caminho)
        self.assertEqual(SESSAO.caminho_slot(2), os.path.join(self.pasta, "brasfut_save_2.json"))

    def test_pedido_vai_pelas_mesmas_rotas(self):
        nav.iniciar(self.pasta)
        r = self.pedir("GET", "/api/estado")
        self.assertEqual(r["status"], 200)
        self.assertIn(r["corpo"]["jogo"], ("sem_save", "tem_save", "pronto"))
        self.assertFalse(r["gravou"])
        self.assertEqual(self.pedir("GET", "/api/nao-existe")["status"], 404)
        self.assertEqual(self.pedir("GET", "/api/estado?x=1")["status"], 200)
        ruim = json.loads(nav.pedido("POST", "/api/config", "{nao e json"))
        self.assertEqual(ruim["status"], 400)

    def test_gravou_avisa_quando_a_pasta_muda(self):
        nav.iniciar(self.pasta)
        r = self.pedir("POST", "/api/config", {"escala": 110})
        self.assertEqual(r["status"], 200)
        self.assertTrue(r["gravou"], "o config foi gravado: o worker precisa sincronizar")
        self.assertTrue(os.path.exists(os.path.join(self.pasta, "brasfut_config.json")))
        self.assertFalse(self.pedir("GET", "/api/config")["gravou"])

    def test_medir_nao_toca_na_carreira_aberta(self):
        G_antes, slot_antes, save_antes = SESSAO.G, SESSAO.slot, eng.SAVE
        mtime = os.path.getmtime(eng.SAVE) if os.path.exists(eng.SAVE) else None
        r = nav.medir(2)
        self.assertEqual(len(r["semanas"]), 2)
        self.assertGreater(r["criar_mundo"], 0)
        self.assertGreater(r["semana"]["media"], 0)
        self.assertGreaterEqual(r["semana"]["pior"], r["semana"]["media"])
        self.assertGreater(r["gravar"]["media"], 0, "cada semana grava o save, como na tela")
        self.assertGreater(r["tamanho_save"], 0)
        self.assertIs(SESSAO.G, G_antes)
        self.assertEqual(SESSAO.slot, slot_antes)
        self.assertEqual(eng.SAVE, save_antes)
        self.assertEqual(os.path.getmtime(eng.SAVE) if os.path.exists(eng.SAVE) else None, mtime)
        self.assertEqual(json.loads(nav.medir_json(1))["semanas"][0]["semana"], 1)


if __name__ == "__main__":
    unittest.main()
