# -*- coding: utf-8 -*-
"""Confianca da diretoria semanal e a maquina demitindo treinador (Onda 2, item 5).

O numero anda toda semana com causa escrita; abaixo de 30 a diretoria avisa;
avisado, abaixo de 15 a demissao pode vir na semana seguinte, no meio do ano.
A maquina demite nos marcos (fim do turno e do ano) por regra, sem sorteio, e
a vaga aberta passa a ligar para o treinador.
"""

import os
import unittest

import apoio

eng = apoio.eng
SESSAO = apoio.SESSAO


def mundo_novo(semente, opcoes=None):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(semente)
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Diretoria", "opcoes": opcoes or {}})["clubes"]
    apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
    return SESSAO.G


def jogo(G, adv, gm, gs, em_casa=True, comp="liga"):
    """Partida de mentira do meu clube, no formato que simular devolve."""
    eu = G["clube"]
    casa, fora = (eu, adv["id"]) if em_casa else (adv["id"], eu)
    gc, gf = (gm, gs) if em_casa else (gs, gm)
    return {"casa": casa, "fora": fora, "gc": gc, "gf": gf, "pub": 30000, "comp": comp}


class TestConfianca(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        cls.G = mundo_novo(71)

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def setUp(self):
        eng.reiniciar_confianca(self.G)
        self.c = self.G["clubes"][self.G["clube"]]
        self.c["dinheiro"] = abs(self.c["dinheiro"]) + 1
        # fora do Brasileirao: so o jogo conta, a posicao nao entra
        self.fase = self.G["fase"]
        self.G["fase"] = "estadual"

    def tearDown(self):
        self.G["fase"] = self.fase

    def rivais(self):
        outros = [c for c in self.G["clubes"].values()
                  if c["divisao"] in eng.DIVISOES_BR and c["id"] != self.G["clube"]
                  and not eng.eh_classico(self.G, self.G["clube"], c["id"])]
        outros.sort(key=lambda c: eng.forca_elenco(self.G, c))
        return outros[0], outros[-1]     # o mais fraco e o mais forte

    def test_derrota_para_fraco_derruba_e_vitoria_sobre_forte_sobe(self):
        G = self.G
        fraco, forte = self.rivais()
        self.assertGreater(eng.resultado_esperado(G, self.c, fraco, True), 0.5)
        eng.atualizar_confianca(G, [jogo(G, fraco, 0, 1)])
        conf = eng.confianca(G)
        self.assertLess(conf["valor"], eng.CONFIANCA_INICIAL)
        delta, causas = conf["hist"][-1][1], conf["hist"][-1][2]
        self.assertLess(delta, 0)
        self.assertIn("derrota para o %s" % fraco["nome"], causas[0][1])
        eng.reiniciar_confianca(G)
        eng.atualizar_confianca(G, [jogo(G, forte, 2, 0, em_casa=False)])
        self.assertGreater(eng.confianca(G)["valor"], eng.CONFIANCA_INICIAL)

    def test_dificuldade_pesa_so_na_queda(self):
        G = self.G
        fraco, _ = self.rivais()
        eng.atualizar_confianca(G, [jogo(G, fraco, 0, 3)])
        normal = eng.confianca(G)["hist"][-1][1]
        eng.reiniciar_confianca(G)
        opcoes = G.get("opcoes")
        try:
            G["opcoes"] = dict(eng.opcoes_carreira(G), dificuldade="dificil")
            eng.atualizar_confianca(G, [jogo(G, fraco, 0, 3)])
            self.assertLess(eng.confianca(G)["hist"][-1][1], normal)
        finally:
            G["opcoes"] = opcoes

    def test_aviso_primeiro_demissao_so_na_semana_seguinte(self):
        G = self.G
        fraco, _ = self.rivais()
        conf = eng.confianca(G)
        conf["valor"] = 20
        eng.atualizar_confianca(G, [jogo(G, fraco, 0, 4)])
        self.assertIsNotNone(conf["aviso"])
        self.assertIsNone(SESSAO.pendencia, "demitiu na mesma semana do aviso")
        clube_antes = G["clube"]
        G["semana_abs"] = eng.semana_absoluta(G) + 1
        conf["valor"] = 10
        try:
            eng.atualizar_confianca(G, [jogo(G, fraco, 0, 4)])
            self.assertIsNotNone(SESSAO.pendencia)
            self.assertEqual(SESSAO.pendencia["tipo"], "novo_clube")
            self.assertIn("confianca", SESSAO.pendencia["motivo"])
            self.assertEqual(G["clube"], clube_antes, "o clube so troca quando eu escolher")
        finally:
            SESSAO.pendencia = None
            G.pop("pendencia_web", None)

    def test_sem_demissao_so_avisa(self):
        G = self.G
        fraco, _ = self.rivais()
        opcoes = G.get("opcoes")
        try:
            G["opcoes"] = dict(eng.opcoes_carreira(G), sem_demissao=True)
            conf = eng.confianca(G)
            conf["valor"], conf["aviso"] = 5, eng.semana_absoluta(G) - 1
            eng.atualizar_confianca(G, [jogo(G, fraco, 0, 4)])
            self.assertIsNone(SESSAO.pendencia)
        finally:
            G["opcoes"] = opcoes

    def test_voltar_acima_de_40_derruba_o_aviso(self):
        G = self.G
        _, forte = self.rivais()
        conf = eng.confianca(G)
        conf["valor"], conf["aviso"] = 35, eng.semana_absoluta(G)
        eng.atualizar_confianca(G, [jogo(G, forte, 3, 0, em_casa=False)])
        self.assertGreaterEqual(conf["valor"], eng.CONFIANCA_RECUPERA)
        self.assertIsNone(conf["aviso"])

    def test_maquina_demite_no_turno_uma_vez_e_abre_vaga(self):
        G = self.G
        liga = G["ligas"]["A"]
        guardado = (liga["rodada"], liga.get("turno_avaliado"),
                    {k: dict(v) for k, v in liga["tabela"].items()}, list(G.get("vagas_tecnico", [])))
        try:
            liga["rodada"] = len(liga["rodadas"]) // 2
            liga.pop("turno_avaliado", None)
            outros = [cid for cid in liga["times"] if cid != G["clube"]]
            gigante = max(outros, key=lambda cid: G["clubes"][cid]["reputacao"])
            for cid in liga["times"]:
                liga["tabela"][str(cid)]["p"] = 30
            liga["tabela"][str(gigante)]["p"] = -50
            demitidos = eng.ia_demite_tecnicos(G)
            self.assertIn(gigante, demitidos)
            self.assertLessEqual(len(demitidos), eng.DEMISSOES_POR_MARCO)
            self.assertIn(gigante, eng.vagas_tecnico(G))
            self.assertTrue(any(m["tipo"] == "tecnico" and G["clubes"][gigante]["nome"] in m["texto"]
                                for m in G["feed"]))
            self.assertEqual(eng.ia_demite_tecnicos(G), [], "o turno so e avaliado uma vez")
        finally:
            liga["rodada"], turno, tabela, vagas = guardado
            liga["tabela"] = tabela
            G["vagas_tecnico"] = vagas
            if turno is None:
                liga.pop("turno_avaliado", None)
            else:
                liga["turno_avaliado"] = turno

    def test_clube_novo_comeca_do_zero(self):
        G = self.G
        conf = eng.confianca(G)
        conf["valor"], conf["aviso"] = 20, eng.semana_absoluta(G)
        outro = next(c for c in G["clubes"].values() if c["divisao"] == "B")
        eng.assumir_clube(G, outro["id"], "teste")
        conf = eng.confianca(G)
        self.assertEqual((conf["valor"], conf["hist"], conf["aviso"]), (eng.CONFIANCA_INICIAL, [], None))

    def test_painel_mostra_numero_tendencia_e_causas(self):
        G = self.G
        fraco, _ = self.rivais()
        eng.atualizar_confianca(G, [jogo(G, fraco, 0, 2)])
        conf = apoio.chamar("GET", "/api/painel")["painel"]["objetivo"]["confianca"]
        self.assertEqual(conf["valor"], eng.confianca(G)["valor"])
        self.assertEqual(conf["tendencia"], eng.tendencia_confianca(G))
        self.assertTrue(conf["causas"] and conf["causas"][0]["texto"].startswith("-"))
        self.assertEqual((conf["limite_aviso"], conf["limite_demissao"]),
                         (eng.CONFIANCA_AVISO, eng.CONFIANCA_DEMISSAO))


if __name__ == "__main__":
    unittest.main()
