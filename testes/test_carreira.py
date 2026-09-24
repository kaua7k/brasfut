# -*- coding: utf-8 -*-
"""Carreira nova com nome e opcoes, sala de trofeus, propostas e demissao."""

import os
import unittest

import apoio

eng = apoio.eng


def criar(nome="Kaua Teste", **opcoes):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(99)
    novo = apoio.chamar("POST", "/api/novo", {"nome": nome, "opcoes": opcoes})
    return novo["clubes"]


def primeiro_da_serie(clubes, div):
    return [c for c in clubes if c["divisao"] == div][0]["id"]


class TestCarreiraNova(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_nome_e_opcoes_vao_para_o_save(self):
        clubes = criar("  Treinador   Novo ", dificuldade="dificil", sem_demissao=True)
        self.assertTrue(set("ABCD") <= {c["divisao"] for c in clubes})
        apoio.chamar("POST", "/api/clube", {"id": primeiro_da_serie(clubes, "C")})
        G = apoio.SESSAO.G
        self.assertEqual(G["tecnico"], "Treinador Novo")
        self.assertEqual(eng.opcoes_carreira(G),
                         {"dificuldade": "dificil", "sem_demissao": True, "investidor": False})

    def test_investidor_poe_o_aporte_da_serie(self):
        clubes = criar(investidor=True)
        cid = primeiro_da_serie(clubes, "B")
        caixa = apoio.SESSAO._pendente_novo["clubes"][cid]["dinheiro"]
        apoio.chamar("POST", "/api/clube", {"id": cid})
        c = apoio.SESSAO.G["clubes"][cid]
        self.assertEqual(c["dinheiro"] - caixa, eng.APORTE_INVESTIDOR["B"])

    def test_sem_demissao_nunca_demite(self):
        clubes = criar(sem_demissao=True)
        apoio.chamar("POST", "/api/clube", {"id": primeiro_da_serie(clubes, "A")})
        G = apoio.SESSAO.G
        G["objetivo_alvo"] = 2
        for _ in range(50):
            ok, _msg = eng.avaliar_diretoria(G, 20)
            self.assertTrue(ok)

    def test_opcao_desconhecida_vira_padrao(self):
        criar(dificuldade="impossivel", sem_demissao="sim")
        op = eng.opcoes_carreira(apoio.SESSAO._pendente_novo)
        self.assertEqual(op["dificuldade"], "normal")
        self.assertTrue(op["sem_demissao"])


class TestMobilidade(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def setUp(self):
        clubes = criar()
        apoio.chamar("POST", "/api/clube", {"id": primeiro_da_serie(clubes, "A")})
        self.G = apoio.SESSAO.G

    def test_pedir_demissao_ate_o_clube_novo(self):
        antigo = self.G["clube"]
        pend = apoio.chamar("POST", "/api/carreira/demitir")["pendencia"]
        self.assertEqual(pend["saida"], "pediu demissao")
        self.assertTrue(pend["opcoes"])
        self.assertNotIn(antigo, [o["id"] for o in pend["opcoes"]])
        apoio.chamar("POST", "/api/carreira/demitir", status=400)   # ja pendente
        apoio.chamar("POST", "/api/avancar", {"confirmar": True}, status=400)
        novo = pend["opcoes"][0]["id"]
        apoio.chamar("POST", "/api/clube", {"id": novo})
        passagens = eng.carreira(self.G)
        self.assertEqual([p["clube_id"] for p in passagens], [antigo, novo])
        self.assertEqual(passagens[0]["saida"], "pediu demissao")
        self.assertIsNone(passagens[1]["ate"])
        tela = apoio.chamar("GET", "/api/carreira")["tela"]
        self.assertEqual(tela["totais"]["clubes"], 2)
        self.assertTrue(tela["passagens"][0]["atual"])

    def test_proposta_aceita_troca_de_clube(self):
        cand = [c for c in self.G["clubes"].values()
                if c["divisao"] == "A" and c["id"] != self.G["clube"]][0]
        self.G["propostas_emprego"] = [{
            "id": cand["id"], "clube": cand["nome"], "divisao": "A",
            "reputacao": cand["reputacao"], "temporada": self.G["temporada"],
            "expira": self.G["semana"] + 2}]
        painel = apoio.chamar("GET", "/api/painel")["painel"]
        self.assertEqual([o["id"] for o in painel["propostas_emprego"]], [cand["id"]])
        apoio.chamar("POST", "/api/carreira/proposta", {"id": cand["id"], "aceitar": True})
        self.assertEqual(self.G["clube"], cand["id"])
        self.assertEqual(self.G["propostas_emprego"], [])
        self.assertTrue(eng.carreira(self.G)[0]["saida"].startswith("aceitou proposta"))
        # proposta que nao existe mais e erro de uso, nao 500
        apoio.chamar("POST", "/api/carreira/proposta", {"id": cand["id"], "aceitar": True}, status=400)

    def test_proposta_de_emprego_para_o_simular(self):
        """Proposta chegava e vencia no meio do 'Simular...' sem ninguem ver."""
        from api import avanco
        G = self.G
        antes = avanco.foto(G)
        self.assertEqual(avanco.motivo_de_parar(G, antes, None, False, None), "")
        G["tecnico_rep"] = 95
        eng.rng.seed(3)
        for _ in range(30):
            if eng.sondar_treinador(G, ano_bom=True):
                break
        self.assertTrue(eng.propostas_emprego(G), "a virada boa nao gerou proposta")
        self.assertIn("quer contratar voce", avanco.motivo_de_parar(G, antes, None, False, None))
        self.assertEqual(avanco.motivo_de_parar(G, antes, {"emprego": False}, False, None), "")
        self.assertEqual(eng.propostas_emprego(G)[0]["expira"] - G["semana"], eng.PROPOSTA_VALIDADE)

    def test_semanas_contam_jogos_e_enchem_o_feed(self):
        for _ in range(12):
            apoio.avancar({"leve": True})
        p = eng.passagem_atual(self.G)
        self.assertGreater(p["j"], 0)
        self.assertEqual(p["j"], p["v"] + p["e"] + p["d"])
        tela = apoio.chamar("GET", "/api/noticias")["tela"]
        self.assertTrue(tela["mundo"], "o feed do mundo ficou vazio")


class TestConfig(unittest.TestCase):
    def test_grava_so_o_que_conhece(self):
        r = apoio.chamar("POST", "/api/config", {"escala": 110, "dificuldade": "facil",
                                                 "lixo": 1, "reduzir_animacoes": 1})
        self.assertEqual(r["config"]["escala"], 110)
        self.assertEqual(r["config"]["dificuldade"], "facil")
        self.assertIs(r["config"]["reduzir_animacoes"], True)
        self.assertNotIn("lixo", r["config"])
        r = apoio.chamar("POST", "/api/config", {"escala": 77})
        self.assertEqual(r["config"]["escala"], 110)
        self.assertEqual(apoio.chamar("GET", "/api/estado")["config"]["escala"], 110)


if __name__ == "__main__":
    unittest.main()
