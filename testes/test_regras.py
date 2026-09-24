# -*- coding: utf-8 -*-
"""Regras que o jogo desobedecia (rodada de melhorias de 2026-09-24).

Um teste por criterio de aceite da Onda 1: livre roubado, posse na API, troca
de clube, prazo absoluto, barra de forcas e os textos que mentiam.
"""

import os
import unittest

import apoio

eng = apoio.eng


def mundo_novo(semente, divisao="A"):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(semente)
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Regras"})["clubes"]
    apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == divisao][0]["id"]})
    return apoio.SESSAO.G


def rival(G, div="A"):
    return [c for c in G["clubes"].values() if c["divisao"] == div and c["id"] != G["clube"]][0]


class TestRegras(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        cls.G = mundo_novo(41)

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def setUp(self):
        self.c = self.G["clubes"][self.G["clube"]]

    # ------------------------------------------------------------------ livres
    def fechar_janela(self):
        G = self.G
        guardado = (G["fase"], G["semana"])
        G["fase"], G["semana"] = "liga", 10
        self.assertFalse(eng.mercado_aberto(G))
        return guardado

    def test_livre_assina_na_hora_com_a_janela_fechada(self):
        G = self.G
        guardado = self.fechar_janela()
        try:
            pid = max(G["livres"], key=lambda p: G["jogadores"][p]["ovr"])
            mesa = apoio.chamar("POST", "/api/mercado/mesa", {"tipo": "compra", "id": pid})["mesa"]
            self.assertTrue(mesa["aberto"])
            self.assertIn("assina na hora", mesa["janela"])
            r = apoio.chamar("POST", "/api/mercado/propor", {
                "tipo": "compra", "id": pid,
                "proposta": {"valor": 0, "salario": mesa["exigencia_num"], "anos": 2}})
            self.assertTrue(r["fechou"], r)
            self.assertEqual(G["jogadores"][pid]["clube"], G["clube"])
            self.assertIn(pid, self.c["elenco"])
            self.assertNotIn(pid, G["livres"])
            self.assertFalse([a for a in eng.agendadas(G) if a["jogador"] == pid])
        finally:
            G["fase"], G["semana"] = guardado

    def test_ia_nao_leva_livre_acertado_com_outro_clube(self):
        """Save de antes da regra: o acerto com livre ficava agendado e a IA
        levava o jogador antes da janela abrir."""
        G = self.G
        guardado = self.fechar_janela()
        try:
            pid = max(G["livres"], key=lambda p: G["jogadores"][p]["ovr"])
            G["agendadas"].append({"jogador": pid, "de": None, "para": G["clube"], "valor": 0,
                                   "salario": G["jogadores"][pid]["salario"], "anos": 2,
                                   "pct_salario": 100, "opcao_compra": 0, "tipo": eng.TIPO_COMPRA,
                                   "temporada": G["temporada"], "semana": G["semana"]})
            eng.contratar_livres_ia(G)
            eng.mercado_ia(G)
            self.assertIsNone(G["jogadores"][pid]["clube"], "a IA levou o livre acertado")
            recados = eng.executar_agendadas(G)
            self.assertEqual(G["jogadores"][pid]["clube"], G["clube"], recados)
            self.assertFalse(eng.agendadas(G))
        finally:
            G["fase"], G["semana"] = guardado

    def test_emprestimo_de_livre_diz_o_motivo(self):
        pid = self.G["livres"][0]
        r = apoio.chamar("POST", "/api/mercado/propor",
                         {"tipo": "emprestimo", "id": pid, "proposta": {"pct": 50}}, status=400)
        self.assertIn("sem clube", r["erro"])

    # ------------------------------------------------------------------- posse
    def test_nao_mexe_em_jogador_de_outro_clube(self):
        G = self.G
        outro = rival(G)
        alvo = outro["elenco"][0]
        caixa, elenco = outro["dinheiro"], list(outro["elenco"])
        for caminho in ("/api/elenco/rescindir", "/api/elenco/tirar-vitrine", "/api/base/subir",
                        "/api/base/liberar", "/api/elenco/chamar", "/api/treino/foco"):
            r = apoio.chamar("POST", caminho, {"ids": [alvo], "confirmar": True}, status=400)
            self.assertIn(G["jogadores"][alvo]["nome"], r["erro"], caminho)
        self.assertEqual(outro["dinheiro"], caixa)
        self.assertEqual(outro["elenco"], elenco)
        self.assertEqual(G["jogadores"][alvo]["clube"], outro["id"])
        self.assertNotIn(alvo, self.c.get("treino_foco", []))

    def test_garoto_da_base_de_outro_clube(self):
        outro = [c for c in self.G["clubes"].values()
                 if c.get("base_elenco") and c["id"] != self.G["clube"]][0]
        garoto = outro["base_elenco"][0]
        apoio.chamar("POST", "/api/base/liberar", {"ids": [garoto], "confirmar": True}, status=400)
        apoio.chamar("POST", "/api/base/subir", {"ids": [garoto], "confirmar": True}, status=400)
        self.assertIn(garoto, outro["base_elenco"])
        self.assertIn(garoto, self.G["jogadores"])

    def test_meu_jogador_continua_funcionando(self):
        meu = self.c["elenco"][-1]
        r = apoio.chamar("POST", "/api/elenco/rescindir", {"ids": [meu]})
        self.assertIn("confirmar", r)
        r = apoio.chamar("POST", "/api/treino/foco", {"ids": [meu]})
        self.assertIn("treino individual", r["recado"])
        apoio.chamar("POST", "/api/treino/foco", {"ids": [meu]})

    # ---------------------------------------------------------- troca de clube
    def test_clube_antigo_fica_sem_as_decisoes_do_tecnico(self):
        G = mundo_novo(43)
        antigo = G["clubes"][G["clube"]]
        esc = eng.escalacao_valida(G, antigo)[0]
        antigo["vagas_manuais"] = [[p, "ATA"] for p in esc]
        antigo["treino_foco"] = esc[:2]
        eng.ligar_peneira(G, antigo, "ne")
        antigo["base_candidatos"] = [{"cid": 1, "vence": eng.semana_absoluta(G) + 3}]
        novo = rival(G)
        G["propostas_emprego"] = [{"id": novo["id"], "clube": novo["nome"], "divisao": "A",
                                   "reputacao": novo["reputacao"], "temporada": G["temporada"],
                                   "vence": eng.semana_absoluta(G) + 3}]
        apoio.chamar("POST", "/api/carreira/proposta", {"id": novo["id"], "aceitar": True})
        self.assertEqual(G["clube"], novo["id"])
        self.assertNotIn("vagas_manuais", antigo)
        self.assertEqual(antigo["treino_foco"], [])
        self.assertIsNone(antigo["peneira"])
        self.assertEqual(antigo["base_candidatos"], [])
        # a maquina volta a escolher as vagas sozinha
        self.assertEqual(eng.vagas_manuais(antigo), {})
        type(self).G = mundo_novo(41)

    # ------------------------------------------------------------------ prazos
    def test_proposta_do_estadual_vence_em_seis_semanas(self):
        G = mundo_novo(47)
        # o primeiro ano nasce no Brasileirao: abre o estadual como a virada abre
        G["fase"], G["semana"] = "entretemporada", 0
        eng.iniciar_estaduais(G)
        apoio.avancar({"leve": True})
        self.assertEqual(G["fase"], "estadual")
        G["tecnico_rep"] = 95
        eng.rng.seed(5)
        for _ in range(40):
            if eng.sondar_treinador(G, ano_bom=True):
                break
        self.assertTrue(eng.propostas_emprego(G))
        for semana in range(1, eng.PROPOSTA_VALIDADE + 1):
            apoio.avancar({"leve": True})
            self.assertEqual(G["fase"], "estadual", "o estadual acabou antes do prazo")
            vivas = eng.propostas_emprego(G)
            if semana < eng.PROPOSTA_VALIDADE:
                self.assertTrue(vivas, "venceu cedo, na semana %d" % semana)
        self.assertFalse(eng.propostas_emprego(G), "a proposta sobreviveu ao prazo")
        type(self).G = mundo_novo(41)

    def test_save_antigo_ganha_prazo_absoluto(self):
        G = {"temporada": 2027, "semana": 0, "semana_est": 9, "clubes": {
            1: {"base_candidatos": [{"cid": 1, "temporada": 2027, "expira": 4}]}},
             "propostas_emprego": [{"id": 1, "temporada": 2027, "expira": 6},
                                   {"id": 2, "temporada": 2026, "expira": 30}]}
        eng.migrar_prazos(G)
        agora = eng.semana_absoluta(G)
        self.assertEqual(agora, 60 + 9)
        prazos = [o["vence"] - agora for o in G["propostas_emprego"]]
        self.assertEqual(prazos, [eng.PROPOSTA_VALIDADE, 0])
        self.assertLessEqual(G["clubes"][1]["base_candidatos"][0]["vence"] - agora, eng.CANDIDATO_VALE)
        self.assertNotIn("expira", G["propostas_emprego"][0])

    # ------------------------------------------------------------------ forcas
    def test_barra_compara_ataque_com_defesa(self):
        G = self.G
        for _ in range(8):
            proximo = apoio.chamar("GET", "/api/painel")["painel"]["proximo"]
            if proximo["tipo"] in ("jogo", "copa") and proximo["ataque"]["dele"] is not None:
                break
            apoio.avancar({"leve": True})
        self.assertIsNotNone(proximo["ataque"]["dele"], "nenhum jogo com adversario em 8 semanas")
        adv = [c for c in G["clubes"].values() if eng.nome_clube(G, c["id"]) == proximo["adversario"]][0]
        comp = [k for k, casa, fora in eng.jogos_da_semana(G, G["clube"])
                if adv["id"] in (casa, fora) or casa is None][0]
        at, de, _ = eng.forcas(G, adv, comp)
        meu_at, meu_de, _ = eng.forcas(G, self.c, comp)
        self.assertEqual(proximo["ataque"], {"meu": round(meu_at, 1), "dele": round(de, 1)})
        self.assertEqual(proximo["defesa"], {"meu": round(meu_de, 1), "dele": round(at, 1)})

    # ------------------------------------------------------------------ textos
    def test_textos_que_mentiam(self):
        G = self.G
        self.assertFalse(eng.tem_rebaixamento("D"))
        self.assertTrue(eng.tem_rebaixamento("C"))
        self.assertFalse(eng.tem_rebaixamento("ENG"))
        for j in list(G["jogadores"].values())[:400]:
            self.assertNotIn("teto", eng.scout(G, j))
        self.assertEqual(eng.liga_do_resumo({"divisao": "ENG", "liga": "Premier League"}),
                         "Premier League")
        self.assertEqual(eng.liga_do_resumo({"divisao": "B"}), "Serie B")
        self.assertEqual(eng._na_fase("quartas de final"), "nas quartas de final")
        painel = apoio.chamar("GET", "/api/painel")["painel"]
        self.assertNotIn("demite na hora", str(painel))

    def test_resumo_de_liga_de_fora_nao_diz_serie(self):
        r = eng.apurar_temporada(self.G)
        r.update(divisao="ENG", liga="Premier League")
        textos = " ".join(eng.texto_resumo(self.G, r))
        from api import dto
        textos += str(dto.resumo(r))
        self.assertNotIn("Serie ENG", textos)
        self.assertIn("Premier League", textos)

    def test_entrada_malformada_e_400(self):
        for caminho, corpo in (("/api/ficha", {"id": "abc"}), ("/api/tabela", {"alvo": 5}),
                               ("/api/competicoes", {"alvo": ["x"]}),
                               ("/api/escalacao/previa", {"contagem": "x"}),
                               ("/api/mercado", [1, 2])):
            st, obj = apoio.rotas.despachar("POST", caminho, corpo)
            self.assertEqual(st, 400, (caminho, obj))


if __name__ == "__main__":
    unittest.main()
