# -*- coding: utf-8 -*-
"""Resumo de temporada: so os campeonatos que o clube jogou, e o que ele
ganhou em destaque (estadual e acesso tambem contam)."""

import os
import unittest

import apoio
from api import dto

eng = apoio.eng
SESSAO = apoio.SESSAO


class TestResumo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(313)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Resumo"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "B"][0]["id"]})
        cls.G = SESSAO.G
        eng.montar_estaduais(cls.G)             # o primeiro ano comeca no Brasileirao
        cls.meu = cls.G["clubes"][cls.G["clube"]]

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def meu_estadual(self):
        return next(e for e in eng.estaduais(self.G).values() if self.meu["id"] in e["times"])

    def test_dar_titulo_guarda_a_temporada(self):
        antes = len(self.meu.get("titulos_hist", []))
        eng.dar_titulo(self.G, self.meu, "Taca de Teste")
        ultimo = self.meu["titulos_hist"][antes]
        self.assertEqual(ultimo, {"nome": "Taca de Teste", "temporada": int(self.G["temporada"])})

    def test_estadual_conta_como_titulo(self):
        est = self.meu_estadual()
        antigo = est.get("campeao")
        est["campeao"] = self.meu["id"]
        try:
            self.assertIn(est["nome"], eng.titulos_da_temporada(self.G, self.meu["id"]))
            camp = {c["nome"]: c for c in eng.campanhas_do_ano(self.G, self.meu["id"])}
            self.assertEqual(camp[est["nome"]]["estado"], "titulo")
            d = dto.resumo(eng.apurar_temporada(self.G), previa=True)
            self.assertIn({"nome": est["nome"], "tipo": "titulo"}, d["conquistas"])
            linha = next(c for c in d["campanhas"] if c["nome"] == est["nome"])
            self.assertTrue(linha["titulo"])
        finally:
            est["campeao"] = antigo

    def test_so_copas_que_jogou(self):
        cid = self.meu["id"]
        nomes = {c["nome"] for c in eng.campanhas_do_ano(self.G, cid)}
        for cp in self.G["copas"].values():
            if eng.campanha_na_copa(cp, cid) is None:
                self.assertNotIn(cp["nome"], nomes)
        # uma copa europeia com campeao nao entra no resumo de um clube da Serie B
        r = eng.apurar_temporada(self.G)
        jogadas = {c["nome"] for c in r["campanhas"]}
        for nome, _ in r["copas"]:
            self.assertIn(nome, jogadas)

    def test_campanha_na_copa(self):
        cid = self.meu["id"]
        outro = next(i for i in self.G["clubes"] if i != cid)
        cp = {"campeao": None, "historico": [
            {"fase": "Oitavas", "jogos": [{"a": cid, "b": outro, "venc": cid}]},
            {"fase": "Quartas", "jogos": [{"a": cid, "b": outro, "venc": outro}]}]}
        self.assertEqual(eng.campanha_na_copa(cp, cid), ("Eliminado nas quartas", "ok"))
        cp["historico"].append({"fase": "Final", "jogos": [{"a": outro, "b": 0, "venc": outro}]})
        cp["campeao"] = outro
        self.assertEqual(eng.campanha_na_copa(cp, outro), ("Campeao", "titulo"))
        cp["historico"][-1]["jogos"][0]["b"] = cid
        self.assertEqual(eng.campanha_na_copa(cp, cid), ("Vice-campeao", "ok"))
        self.assertIsNone(eng.campanha_na_copa({"campeao": None, "historico": []}, cid))

    def test_acesso_em_destaque_e_sem_lista_do_mundo(self):
        liga = self.G["ligas"]["B"]
        for t in liga["tabela"].values():
            t["p"] = 0
        liga["tabela"][str(self.meu["id"])]["p"] = 70
        d = dto.resumo(eng.apurar_temporada(self.G), previa=True)
        tipos = [c["tipo"] for c in d["conquistas"]]
        self.assertIn("titulo", tipos)          # campeao da Serie B
        self.assertIn("acesso", tipos)
        titulos = [s["titulo"] for s in d["secoes"]]
        self.assertNotIn("Como terminou", titulos)
        liga_linha = d["campanhas"][0]
        self.assertEqual(liga_linha["nome"], "Brasileirao Serie B")
        self.assertEqual(liga_linha["resultado"], "Campeao")


if __name__ == "__main__":
    unittest.main()
