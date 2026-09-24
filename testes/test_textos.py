# -*- coding: utf-8 -*-
"""Lint de textos: o que a tela escreve segue um jeito so.

Zero "(s)", zero dinheiro com ponto decimal ("R$ 13.07 mi"), zero "Serie ENG",
e o menu e o titulo da tela usam o mesmo nome. Roda nas fontes (o texto que
ainda nem apareceu) e nas telas de um mundo novo (o texto montado na hora).
"""

import glob
import json
import os
import re
import unittest

import apoio
from test_telas import TELAS

eng = apoio.eng

# "(s)ubir" e o atalho do terminal; "tuple(s) for" e "(s) =>" sao codigo
PLURAL_AMBIGUO = re.compile(r"\w\((?:s|es)\)(?!ubir)(?!\s*(?:for|=>|\)|,))")
DINHEIRO_COM_PONTO = re.compile(r"R\$ ?-?\d+\.\d+ (?:mi|bi)")
SERIE_DE_FORA = re.compile(r"Serie (?:%s)\b" % "|".join(eng.ORDEM_LIGAS_EXT + ["EX", "USA", "SAU"]))


def fontes():
    raiz = apoio.RAIZ
    arquivos = [os.path.join(raiz, "brasfut.py")] + glob.glob(os.path.join(raiz, "api", "*.py"))
    arquivos += glob.glob(os.path.join(raiz, "web", "src", "**", "*.ts*"), recursive=True)
    for caminho in arquivos:
        with open(caminho, encoding="utf-8") as f:
            for n, linha in enumerate(f, 1):
                codigo = linha.split("#")[0] if caminho.endswith(".py") else linha.split("//")[0]
                yield os.path.relpath(caminho, raiz), n, codigo


class TestTextos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(5)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Textos"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        for _ in range(3):
            apoio.avancar({"leve": True})
        cls.telas = {caminho: json.dumps(apoio.chamar("GET", caminho), ensure_ascii=False)
                     for caminho in TELAS}

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_fontes_sem_plural_ambiguo(self):
        achados = ["%s:%d" % (a, n) for a, n, c in fontes()
                   if PLURAL_AMBIGUO.search(c) and "Nunca" not in c]
        self.assertEqual(achados, [])

    def test_fontes_sem_dinheiro_com_ponto(self):
        achados = ["%s:%d" % (a, n) for a, n, c in fontes() if "toFixed(2)} mi" in c or '%.2f mi' in c]
        self.assertEqual(achados, [])

    def test_telas(self):
        for caminho, texto in self.telas.items():
            with self.subTest(tela=caminho):
                self.assertIsNone(PLURAL_AMBIGUO.search(texto))
                self.assertIsNone(DINHEIRO_COM_PONTO.search(texto))
                self.assertIsNone(SERIE_DE_FORA.search(texto))

    def test_dinheiro_pt_br(self):
        self.assertEqual(eng.din(37_600_000), "R$ 37,6 mi")
        self.assertEqual(eng.din(-5_400_000_000), "-R$ 5,4 bi")
        self.assertEqual(eng.din(764_000), "R$ 764 mil")
        self.assertEqual(eng.din(3_500), "R$ 3.500")

    def test_menu_e_titulo_com_o_mesmo_nome(self):
        menu = {m["id"]: m["nome"] for m in apoio.chamar("GET", "/api/estado")["cabecalho"]["menu"]}
        for id_, rota in (("tabela", "/api/tabela"), ("financas", "/api/financas"),
                          ("elenco", "/api/elenco"), ("mercado", "/api/mercado")):
            with self.subTest(tela=id_):
                self.assertEqual(apoio.chamar("GET", rota)["tela"]["titulo"], menu[id_])


if __name__ == "__main__":
    unittest.main()
