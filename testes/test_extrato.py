# -*- coding: utf-8 -*-
"""O extrato do ano fecha com o caixa: nenhum dinheiro entra ou sai sem categoria.

Temporada inteira de um clube da Serie A, com compra, venda, obra e infra no
meio: a cada semana, a soma do extrato tem que ser igual a caixa de agora
menos caixa do comeco do ano.
"""

import os
import unittest

import apoio

eng = apoio.eng


class TestExtrato(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(97)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Extrato",
                                                    "opcoes": {"sem_demissao": True}})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def conferir(self, quando):
        G = self.G
        st = eng.stats_ano(G)
        c = G["clubes"][G["clube"]]
        soma = sum(st.get("extrato", {}).values())
        self.assertEqual(soma, c["dinheiro"] - st["caixa_ini"],
                         "%s: extrato %d, caixa andou %d" % (quando, soma, c["dinheiro"] - st["caixa_ini"]))
        for cat in st.get("extrato", {}):
            self.assertIn(cat, dict(eng.EXTRATO), "categoria sem rotulo: %s" % cat)

    def test_temporada_inteira_fecha_com_o_caixa(self):
        G = self.G
        temporada = G["temporada"]
        for semana in range(70):
            apoio.chamar("POST", "/api/avancar", {"leve": True, "confirmar": True})
            if G["temporada"] != temporada:
                break
            self.conferir("semana %d" % (semana + 1))
        else:
            self.fail("a temporada nao virou em 70 semanas")
        # o ano novo abre com o extrato zerado e o caixa de agora como comeco
        self.conferir("comeco do ano novo")
        # e o resumo do ano que acabou fecha com o caixa daquele ano
        r = G.get("ultimo_resumo")
        self.assertIsNotNone(r)
        self.assertEqual(sum(r["extrato"].values()),
                         r["financas"]["caixa_fim"] - r["financas"]["caixa_ini"])
        self.assertIn("premio_liga", r["extrato"])
        secoes = {s["titulo"]: s["itens"] for s in apoio.chamar("GET", "/api/resumo")["resumo"]["secoes"]}
        self.assertTrue(any("Premiacao da liga" in i["texto"] for i in secoes["Dinheiro no ano"]))

    def test_compra_venda_obra_e_infra_entram_no_extrato(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        c["dinheiro"] = abs(c["dinheiro"]) + 900_000_000
        eng.novo_ano_stats(G)
        # obra e infra pela API, como na tela
        apoio.chamar("POST", "/api/estadio/obra", {"lugares": 1500, "confirmar": True})
        apoio.chamar("POST", "/api/infra/investir", {"id": "medico", "confirmar": True})
        # compra e venda pelo motor
        alvo = next(j for j in G["jogadores"].values()
                    if j.get("clube") not in (None, G["clube"]) and not j.get("dono"))
        eng.transferir(G, alvo["id"], G["clube"], 5_000_000)
        eng.transferir(G, alvo["id"], next(x for x in G["clubes"] if x != G["clube"]), 7_000_000)
        ex = eng.stats_ano(G)["extrato"]
        self.assertLess(ex["obras"], 0)
        self.assertLess(ex["infra"], 0)
        self.assertEqual(ex["compras"], -5_000_000)
        self.assertEqual(ex["vendas"], 7_000_000)
        self.conferir("depois dos negocios")


    def test_telas_mostram_o_que_o_dinheiro_e(self):
        fin = apoio.chamar("GET", "/api/financas")["tela"]
        nomes = [l["nome"] for l in fin["extrato"]["entradas"]]
        self.assertIn("Cotas de TV", nomes)
        self.assertIn("Patrocinio", nomes)
        self.assertIn("Bilheteria", nomes)
        self.assertTrue(all(l.get("dica") for l in fin["extrato"]["entradas"] + fin["extrato"]["saidas"]))
        self.assertTrue(fin["premiacao"])
        self.assertTrue(fin["elenco"]["valor"].startswith("R$"))
        est = apoio.chamar("GET", "/api/estadio")["tela"]
        rotulos = [l["nome"] for l in est["rendimento"]]
        self.assertIn("Ingresso de referencia da sua torcida", rotulos)
        self.assertIn("Manutencao de cada 1.000 lugares", rotulos)

    def test_premio_da_liga_previsto_e_o_mesmo_que_paga(self):
        G = self.G
        liga = G["ligas"]["A"]
        ordem = eng.classificacao(G, liga)
        antes = {cid: G["clubes"][cid]["dinheiro"] for cid in ordem}
        eng.premiacao(G)
        for pos, cid in enumerate(ordem, 1):
            self.assertEqual(G["clubes"][cid]["dinheiro"] - antes[cid], eng.premio_liga("A", pos))


if __name__ == "__main__":
    unittest.main()
