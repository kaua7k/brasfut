# -*- coding: utf-8 -*-
"""Pre-contrato (ultimo ano de contrato, chega de graca na virada) e mercado
disputado (outro clube atras do mesmo jogador)."""

import os
import unittest

import apoio

eng = apoio.eng


class TestPrecontratoEDisputa(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(401)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Pre",
                                                    "opcoes": {"sem_demissao": True}})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def meu(self):
        return self.G["clubes"][self.G["clube"]]

    def alvo_fim_de_contrato(self):
        G = self.G
        js = sorted((j for j in G["jogadores"].values()
                     if j["clube"] not in (None, G["clube"]) and not j.get("dono")
                     and not eng.da_base(j) and G["clubes"][j["clube"]]["divisao"] in "AB"
                     and j["id"] not in eng.presos_em_acerto(G)),
                    key=lambda j: j["id"])
        j = js[0]
        j["contrato"] = 1
        return j

    def test_pre_contrato_so_no_segundo_semestre_e_chega_na_virada(self):
        G = self.G
        c = self.meu()
        G["fase"], G["semana"] = "liga", 10
        j = self.alvo_fim_de_contrato()
        origem = j["clube"]
        self.assertFalse(eng.pode_precontrato(G, j, c)[0])
        G["semana"] = eng.SEMANA_PRECONTRATO
        self.assertTrue(eng.pode_precontrato(G, j, c)[0])
        j["contrato"] = 2
        self.assertFalse(eng.pode_precontrato(G, j, c)[0])
        j["contrato"] = 1

        mesa = apoio.chamar("POST", "/api/mercado/mesa", {"tipo": "compra", "id": j["id"],
                                                          "proposta": {"precontrato": True}})["mesa"]
        self.assertTrue(mesa["precontrato"]["pode"])
        self.assertTrue(mesa["precontrato"]["ativo"])
        salario = int(mesa["exigencia_num"] * 1.15)
        r = apoio.chamar("POST", "/api/mercado/propor", {
            "tipo": "compra", "id": j["id"],
            "proposta": {"precontrato": True, "salario": salario, "anos": 3}})
        self.assertTrue(r["fechou"], r)
        self.assertTrue(r["mesa"]["precontrato"]["ativo"], "a mesa fechada segue dizendo pre-contrato")
        self.assertEqual(r["mesa"]["pedido_num"], 0)
        self.assertEqual(j["clube"], origem, "pre-contrato nao muda de clube agora")
        self.assertIn(j["id"], eng.precontratados(G))
        caixa = c["dinheiro"]

        # a janela do meio do ano nao cumpre o pre-contrato
        eng.executar_agendadas(G)
        self.assertEqual(j["clube"], origem)
        # o contrato acaba e o clube dele nao renova nem libera
        j["contrato"] = 0
        eng.fim_de_contrato(G)
        self.assertEqual(j["clube"], origem)
        self.assertNotIn(j["id"], G["livres"])
        # virada: chega de graca, com o salario combinado
        G["temporada"] += 1
        G["fase"], G["semana"] = "entretemporada", 0
        eng.executar_agendadas(G)
        self.assertEqual(j["clube"], c["id"])
        self.assertEqual(j["salario"], salario)
        self.assertEqual(c["dinheiro"], caixa)
        self.assertNotIn(j["id"], eng.precontratados(G))

    def test_disputa_pede_cobrir_o_lance_e_o_rival_leva_quando_esgota(self):
        G = self.G
        c = self.meu()
        G["fase"], G["semana"] = "liga", 2
        c["dinheiro"] = 10 ** 10
        achado = None
        for j in sorted(G["jogadores"].values(), key=lambda x: -x["ovr"]):
            if j["clube"] in (None, c["id"]) or j.get("dono"):
                continue
            d = eng.disputa(G, j, c["id"])
            if d:
                achado = (j, d)
                break
        self.assertIsNotNone(achado, "nenhum jogador disputado no mundo")
        j, (rival, lance) = achado
        self.assertEqual(eng.disputa(G, j, c["id"]), (rival, lance), "disputa estavel na janela")
        self.assertIsNone(eng.disputa(G, j, rival["id"]), "so o meu clube enfrenta disputa")
        pedido, _ = eng.pedido_efetivo(G, j)
        self.assertGreater(lance, pedido)

        recusa = eng.avaliar_clube(G, eng.Proposta(jogador=j["id"], comprador=c["id"], valor=pedido))
        self.assertFalse(recusa.aceita)
        self.assertIn(rival["nome"], recusa.motivo)
        aceita = eng.avaliar_clube(G, eng.Proposta(jogador=j["id"], comprador=c["id"], valor=lance))
        self.assertTrue(aceita.aceita, aceita.motivo)

        mesa = apoio.chamar("POST", "/api/mercado/mesa", {"tipo": "compra", "id": j["id"]})["mesa"]
        self.assertEqual(mesa["disputa"]["lance_num"], lance)
        # tres tentativas abaixo do lance: o rival cobre e leva
        for _ in range(eng_tentativas()):
            apoio.chamar("POST", "/api/mercado/propor", {
                "tipo": "compra", "id": j["id"],
                "proposta": {"valor": pedido, "salario": mesa["exigencia_num"], "anos": 3}})
        self.assertEqual(j["clube"], rival["id"])
        self.assertTrue(any("levou %s" % j["nome"] in n for n in G["noticias"][-3:]))


class TestRivalAssedia(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(409)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Assedio",
                                                    "opcoes": {"sem_demissao": True}})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "B"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_rival_sonda_avisa_e_assina_se_eu_nao_renovar(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        G["fase"], G["semana"] = "liga", eng.SEMANA_PRECONTRATO
        for p in c["elenco"]:
            G["jogadores"][p]["contrato"] = 3
        j = max((G["jogadores"][p] for p in c["elenco"] if not G["jogadores"][p].get("dono")),
                key=lambda x: x["ovr"])
        j["contrato"] = 1
        base = eng.ASSEDIO_BASE
        eng.ASSEDIO_BASE = 1.0
        try:
            eng.rivais_assediam(G)
        finally:
            eng.ASSEDIO_BASE = base
        sonda = G["assedios"][str(j["id"])]
        self.assertTrue(any("procurou %s" % j["nome"] in n for n in G["noticias"][-3:]))
        linha = next(l for l in apoio.chamar("POST", "/api/mercado", {"aba": "vitrine"})["tela"]["contratos"]
                     if l["id"] == j["id"])
        self.assertIn("quer pre-contrato", linha["quando"])
        # uma semana depois ainda da tempo; na segunda ele assina
        G["semana_abs"] = eng.semana_absoluta(G) + 1
        eng.rivais_assediam(G)
        self.assertIsNone(eng.precontrato_de(G, j["id"]))
        G["semana_abs"] = eng.semana_absoluta(G) + 1
        eng.rivais_assediam(G)
        acerto = eng.precontrato_de(G, j["id"])
        self.assertEqual(acerto["para"], sonda["rival"])
        # assinou: nao renova mais, e eu nao desfaco o acerto deles
        r = eng.avaliar_renovacao(G, eng.Proposta(jogador=j["id"], comprador=c["id"],
                                                  salario=j["salario"] * 3, anos=3))
        self.assertFalse(r.aceita)
        indice = next(i for i, a in eng.minhas_agendadas(G) if a["jogador"] == j["id"])
        self.assertFalse(eng.cancelar_agendada(G, indice)[0])
        # virada: vai para o rival, de graca
        caixa = c["dinheiro"]
        j["contrato"] = 0
        eng.fim_de_contrato(G)
        G["temporada"] += 1
        G["fase"], G["semana"] = "entretemporada", 0
        eng.executar_agendadas(G)
        self.assertEqual(j["clube"], sonda["rival"])
        self.assertEqual(c["dinheiro"], caixa)

    def test_renovar_a_tempo_desfaz_a_sondagem(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        G["fase"], G["semana"] = "liga", eng.SEMANA_PRECONTRATO
        j = next(G["jogadores"][p] for p in c["elenco"]
                 if not G["jogadores"][p].get("dono") and not eng.da_base(G["jogadores"][p])
                 and eng.precontrato_de(G, p) is None)
        j["contrato"] = 1
        G.setdefault("assedios", {})[str(j["id"])] = {
            "rival": next(x["id"] for x in G["clubes"].values() if x["id"] != c["id"] and x["divisao"] == "A"),
            "desde": eng.semana_absoluta(G)}
        j["contrato"] = 3
        eng.rivais_assediam(G)
        self.assertNotIn(str(j["id"]), G["assedios"])
        self.assertIsNone(eng.precontrato_de(G, j["id"]))


def eng_tentativas():
    from api import mercado
    return mercado.TENTATIVAS


if __name__ == "__main__":
    unittest.main()
