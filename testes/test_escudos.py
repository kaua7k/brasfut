# -*- coding: utf-8 -*-
"""Escudos: dado estavel por clube, cores reais onde ha cadastro."""

import re
import unittest

import apoio
import dados_clubes
from api import dto

eng = apoio.eng
HEX = re.compile(r"^#[0-9A-F]{6}$")


class TestEscudos(unittest.TestCase):
    def test_cadastro_bate_com_os_clubes_e_e_valido(self):
        nomes = {c[0] for c in eng.CLUBES_A + eng.CLUBES_B + eng.CLUBES_C + eng.CLUBES_D}
        for nome, (c1, c2, padrao, sigla) in dados_clubes.ESCUDOS.items():
            self.assertTrue(HEX.match(c1) and HEX.match(c2), nome)
            self.assertIn(padrao, dto.PADROES_ESCUDO, nome)
            self.assertTrue(1 <= len(sigla) <= 4, nome)
        brasileiros = [n for n in dados_clubes.ESCUDOS if n in nomes]
        self.assertGreater(len(brasileiros), 50)

    def test_mesmo_nome_mesmo_escudo(self):
        self.assertEqual(dto.escudo_de("Clube Inventado FC"), dto.escudo_de("Clube Inventado FC"))
        self.assertEqual(dto.escudo_de("Santos")["cor1"], "#FFFFFF")
        e = dto.escudo_de("Clube Inventado FC")
        self.assertIn(e["padrao"], dto.PADROES_ESCUDO)
        self.assertEqual(e["sigla"], "CIF")

    def test_rota_sem_mundo_e_com_mundo(self):
        sem = apoio.chamar("GET", "/api/escudos")["escudos"]
        self.assertTrue(any(e["nome"] == "Flamengo" for e in sem))
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Escudos"})["clubes"]
        com = {e["nome"] for e in apoio.chamar("GET", "/api/escudos")["escudos"]}
        self.assertTrue(all(c["nome"] in com for c in clubes))
        apoio.SESSAO._pendente_novo = None


if __name__ == "__main__":
    unittest.main()
