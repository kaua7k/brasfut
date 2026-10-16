# -*- coding: utf-8 -*-
"""Convocacoes: datas FIFA no meio do Brasileirao, 23 por selecao, desfalque
na semana da data, historico na ficha e aviso no Painel."""

import contextlib
import io
import os
import unittest

import apoio

eng = apoio.eng


def mundo_novo(semente, nome="Flamengo"):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(semente)
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Selecao",
                                                "opcoes": {"sem_demissao": True}})["clubes"]
    apoio.chamar("POST", "/api/clube", {"id": next(c["id"] for c in clubes if c["nome"] == nome)})
    return apoio.SESSAO.G


def ate_a_data_fifa(G):
    """Pula para a semana anterior a primeira data FIFA e avanca uma."""
    G["semana"] = eng.DATAS_FIFA[0] - 1
    apoio.avancar()
    assert G["semana"] == eng.DATAS_FIFA[0]


class TestConvocacoes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_nacionalidade(self):
        eng.rng.seed(601)
        with contextlib.redirect_stdout(io.StringIO()):
            G = eng.criar_mundo("T")
        por_nome = {j["nome"]: j for j in G["jogadores"].values()}
        self.assertTrue(all(j.get("nac") for j in G["jogadores"].values()))
        self.assertEqual(por_nome["Vinicius Junior"]["nac"], "BRA")      # brasileiro na Europa
        self.assertEqual(por_nome["De Arrascaeta"]["nac"], "URU")        # estrangeiro no Brasil
        fora = next(j for j in G["jogadores"].values()
                    if j["clube"] and G["clubes"][j["clube"]]["divisao"] == "ARG"
                    and j["nome"] not in eng.NAC_REAL)
        self.assertEqual(fora["nac"], "ARG")
        # depois de fixada, a nacionalidade nao muda com a transferencia
        j = por_nome["De Arrascaeta"]
        j["clube"] = next(c["id"] for c in G["clubes"].values() if c["divisao"] == "A")
        eng.fixar_nacionalidades(G)
        self.assertEqual(j["nac"], "URU")

    def test_data_fifa_desfalca_e_volta(self):
        G = mundo_novo(602)
        c = G["clubes"][G["clube"]]
        moral_antes = {p: G["jogadores"][p]["moral"] for p in c["elenco"]}
        ate_a_data_fifa(G)
        cv = eng.convocacao_atual(G)
        self.assertIsNotNone(cv)
        bra = cv["listas"]["BRA"]
        self.assertEqual(len(bra), 23)
        self.assertEqual(len(set(bra)), 23)
        js = [G["jogadores"][p] for p in bra]
        for pos, n in eng.CONVOCADOS_POR_POS:
            self.assertEqual(sum(1 for j in js if j["pos"] == pos), n, pos)
        self.assertTrue(all(j["nac"] == "BRA" and j["lesao"] == 0 and not eng.da_base(j) for j in js))
        self.assertTrue(set(cv["listas"]) <= set(eng.SELECOES))
        # o Flamengo tem gente na selecao: desfalque de verdade
        meus = [p for p in c["elenco"] if G["jogadores"][p].get("convocado")]
        self.assertTrue(meus)
        for p in meus:
            self.assertFalse(eng.disponivel(G, p))
            self.assertFalse(eng.disponivel(G, p, "copa"))
            self.assertEqual(G["jogadores"][p]["convocacoes"][-1],
                             {"temporada": G["temporada"], "semana": G["semana"],
                              "selecao": G["jogadores"][p]["convocado"]})
            self.assertGreater(G["jogadores"][p]["moral"], moral_antes[p] - 3)
        esc, _ = eng.escalacao_valida(G, c)
        self.assertEqual(len(esc), 11)
        self.assertFalse(set(esc) & set(meus))
        # Painel, Elenco e ficha contam
        painel = apoio.chamar("GET", "/api/painel")["painel"]
        self.assertIsNotNone(painel["selecao"])
        self.assertEqual(len(painel["selecao"]["nomes"]), len(meus))
        ficha = apoio.chamar("POST", "/api/ficha", {"id": meus[0]})["ficha"]
        self.assertEqual(ficha["convocacoes"]["total"], 1)
        self.assertIsNotNone(ficha["convocacoes"]["agora"])
        self.assertTrue(any("DATA FIFA" in n for n in G["noticias"]))
        self.assertTrue(any(f["tipo"] == "selecao" for f in G["feed"]))
        # passou a data: todo mundo volta, o historico fica
        apoio.avancar()
        self.assertFalse(any(j.get("convocado") for j in G["jogadores"].values()))
        self.assertIsNone(eng.convocacao_atual(G))
        self.assertTrue(all(eng.disponivel(G, p) or G["jogadores"][p]["lesao"] > 0
                            or G["jogadores"][p]["suspensao"] > 0 for p in meus))
        self.assertEqual(len(G["jogadores"][meus[0]]["convocacoes"]), 1)

    def test_lista_estavel_e_vitrine(self):
        G = mundo_novo(603)
        G["semana"] = eng.DATAS_FIFA[0]
        primeira = eng.convocar(G)
        eng.liberar_convocados(G)
        segunda = eng.convocar(G)
        self.assertEqual(primeira, segunda)            # _ruido estavel, sem rng
        j = G["jogadores"][primeira["BRA"][0]]
        self.assertGreaterEqual(float(j.get("premio_valor", 0)), eng.VITRINE_CONVOCADO)
        self.assertEqual(j["valor"], eng.valor_jogador(j))
        eng.liberar_convocados(G)
        self.assertFalse(any(x.get("convocado") for x in G["jogadores"].values()))

    def test_save_antigo_sem_nacionalidade(self):
        G = mundo_novo(604)
        for j in G["jogadores"].values():
            j.pop("nac", None)
        G.pop("convocacao", None)
        eng.migrar(G)
        self.assertIsNone(G["convocacao"])
        self.assertTrue(all(j.get("nac") for j in G["jogadores"].values()))
        self.assertIsNone(eng.convocacao_atual(G))


if __name__ == "__main__":
    unittest.main()
