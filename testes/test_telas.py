# -*- coding: utf-8 -*-
"""Toda tela de leitura abre contra o save real (copiado) sem erro."""

import unittest

import apoio

TELAS = ["/api/estado", "/api/painel", "/api/elenco", "/api/base", "/api/tabela",
         "/api/copas", "/api/competicoes", "/api/financas", "/api/infra",
         "/api/noticias", "/api/escalacao", "/api/treino", "/api/estadio",
         "/api/mercado", "/api/avanco/opcoes", "/api/carreira", "/api/config"]


@unittest.skipUnless(apoio.tem_save_real(), "sem brasfut_save.json na pasta do jogo")
class TestTelas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        apoio.abrir_copia_do_save()

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_todas_as_telas_abrem(self):
        for caminho in TELAS:
            with self.subTest(tela=caminho):
                self.assertIsInstance(apoio.chamar("GET", caminho), dict)

    def test_rota_inexistente_e_404(self):
        apoio.chamar("GET", "/api/nao-existe", status=404)

    def test_avancar_semana_grava_na_copia(self):
        if apoio.SESSAO.pendencia:
            self.skipTest("o save real tem uma decisao pendente (%s)" % apoio.SESSAO.pendencia["titulo"])
        semana = apoio.SESSAO.G["semana"]
        r = apoio.avancar()
        self.assertIn("cabecalho", r)
        self.assertNotEqual(apoio.SESSAO.G["semana"], semana)
        # a copia foi gravada e continua abrindo
        apoio.chamar("POST", "/api/abrir")
        apoio.chamar("GET", "/api/painel")


if __name__ == "__main__":
    unittest.main()
