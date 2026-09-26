# -*- coding: utf-8 -*-
"""Ligas sul-americanas (decidido em 2026-09-26).

Nove ligas (ARG, URU, PAR, CHI, COL, EQU, PER, BOL, VEN) com os sul-americanos
que ja existiam mais clubes reais com elenco gerado. As 24 vagas de fora da
Libertadores e da Sul-Americana saem da classificacao de cada liga. Save
antigo ganha as ligas ao abrir.
"""

import os
import unittest
from collections import Counter

import apoio

eng = apoio.eng


def mundo_novo(semente):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(semente)
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Sul"})["clubes"]
    apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
    return apoio.SESSAO.G


class TestLigasSul(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        cls.G = mundo_novo(21)

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_nove_ligas_com_o_tamanho_certo(self):
        G = self.G
        self.assertEqual(eng.ligas_sul(G), eng.CODIGOS_SUL)
        for codigo, _, n in eng.LIGAS_SUL:
            liga = G["ligas"][codigo]
            with self.subTest(liga=codigo):
                self.assertEqual(len(liga["times"]), n)
                for cid in liga["times"]:
                    c = G["clubes"][cid]
                    self.assertEqual((c["divisao"], c["liga_ext"], c["uf"]), (codigo, codigo, codigo))
                # cabe nas 38 semanas
                self.assertLessEqual(len(liga["rodadas"]), eng.SEMANAS_LIGA)

    def test_nenhum_sul_americano_fora_de_liga(self):
        soltos = [c["nome"] for c in self.G["clubes"].values()
                  if c["divisao"] == "EX" and not c.get("europeu")]
        self.assertEqual(soltos, [])

    def test_grandes_estao_na_liga_do_pais(self):
        G = self.G
        por_nome = {c["nome"]: c for c in G["clubes"].values()}
        for nome, pais in (("Boca Juniors", "ARG"), ("River Plate", "ARG"), ("Penarol", "URU"),
                           ("Olimpia", "PAR"), ("Colo-Colo", "CHI"), ("Atletico Nacional", "COL"),
                           ("LDU Quito", "EQU"), ("Alianza Lima", "PER"), ("Bolivar", "BOL"),
                           ("Caracas FC", "VEN")):
            self.assertEqual(por_nome[nome]["divisao"], pais, nome)

    def test_vagas_continentais_por_pais(self):
        G = self.G
        lib, sula = G["copas"]["lib"]["vivos"], G["copas"]["sul"]["vivos"]
        self.assertEqual(len(lib), 32)
        self.assertEqual(len(sula), 32)
        self.assertFalse(set(lib) & set(sula))
        paises_lib = Counter(eng.pais(G["clubes"][i]) for i in lib)
        paises_sula = Counter(eng.pais(G["clubes"][i]) for i in sula)
        for k, n in eng.VAGAS_LIB.items():
            self.assertEqual(paises_lib[k], n, k)
        for k, n in eng.VAGAS_SULA.items():
            self.assertEqual(paises_sula[k], n, k)

    def test_vaga_segue_a_classificacao_do_ano_anterior(self):
        G = self.G
        arg = G["ligas"]["ARG"]["times"]
        # o ultimo do ano passado vira o campeao: tem de ir para a Libertadores
        ordem = list(reversed(eng.classificacao(G, G["ligas"]["ARG"])))
        G.setdefault("class_ext_anterior", {})["ARG"] = ordem
        lib, _ = eng.vagas_continentais_sul(G)
        self.assertIn(ordem[0], lib)
        self.assertEqual(len([i for i in lib if i in arg]), eng.VAGAS_LIB["ARG"])
        G["class_ext_anterior"].pop("ARG")

    def test_ligas_jogam_e_aparecem_na_classificacao(self):
        apoio.avancar({"leve": True})
        G = self.G
        for k in eng.CODIGOS_SUL:
            self.assertGreaterEqual(G["ligas"][k]["rodada"], 0)
        tela = apoio.chamar("GET", "/api/tabela")["tela"]
        ids = str(tela)
        self.assertIn("Liga Profesional Argentina", ids)

    def test_save_antigo_ganha_as_ligas(self):
        G = mundo_novo(22)
        # simula um save de antes: sul-americanos soltos em "EX", sem as ligas
        for k in eng.CODIGOS_SUL:
            for cid in G["ligas"].pop(k)["times"]:
                c = G["clubes"][cid]
                c["divisao"] = "EX"
                c.pop("liga_ext", None)
        eng.migrar(G)
        self.assertEqual(eng.ligas_sul(G), eng.CODIGOS_SUL)
        for codigo, _, n in eng.LIGAS_SUL:
            self.assertEqual(len(G["ligas"][codigo]["times"]), n)
        # os clubes que ja existiam foram reaproveitados, nao duplicados
        nomes = Counter(c["nome"] for c in G["clubes"].values() if c["divisao"] in eng.CODIGOS_SUL)
        self.assertEqual([n for n, k in nomes.items() if k > 1], [])


if __name__ == "__main__":
    unittest.main()
