# -*- coding: utf-8 -*-
"""Lista de observacao do olheiro: vagas, leitura que aperta e avisos."""

import os
import re
import unittest

import apoio

eng = apoio.eng


def mundo_novo(semente):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(semente)
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Olheiro",
                                                "opcoes": {"sem_demissao": True}})["clubes"]
    apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "B"][0]["id"]})
    return apoio.SESSAO.G


def de_fora(G, n, idade_max=99):
    meu = G["clube"]
    js = [j for j in G["jogadores"].values()
          if j["clube"] not in (None, meu) and j["idade"] <= idade_max and not eng.da_base(j)]
    js.sort(key=lambda j: j["id"])
    return js[:n]


def largura(faixa):
    nums = [int(x) for x in re.findall(r"\d+", faixa)]
    return nums[-1] - nums[0] if len(nums) == 2 else 0


class TestObservacao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_vagas_pela_api_e_aba_do_mercado(self):
        G = mundo_novo(301)
        c = G["clubes"][G["clube"]]
        vagas = eng.vagas_observacao(c)
        alvos = de_fora(G, vagas + 1)
        for j in alvos[:vagas]:
            r = apoio.chamar("POST", "/api/observar", {"id": j["id"]})
            self.assertTrue(r["ficha"]["observado"])
        r = apoio.chamar("POST", "/api/observar", {"id": alvos[vagas]["id"]}, status=400)
        apoio.chamar("POST", "/api/observar", {"id": alvos[0]["id"]}, status=400)
        meu = G["jogadores"][c["elenco"][0]]
        apoio.chamar("POST", "/api/observar", {"id": meu["id"]}, status=400)
        tela = apoio.chamar("POST", "/api/mercado", {"aba": "observados"})["tela"]
        self.assertEqual({l["id"] for l in tela["jogadores"]}, {j["id"] for j in alvos[:vagas]})
        self.assertEqual(tela["observacao"], {"usadas": vagas, "vagas": vagas})
        self.assertTrue(all(l["observado"] for l in tela["jogadores"]))
        r = apoio.chamar("POST", "/api/observar", {"id": alvos[0]["id"], "observar": False})
        self.assertFalse(r["ficha"]["observado"])
        self.assertEqual(len(eng.observados(G)), vagas - 1)

    def test_leitura_aperta_com_os_meses(self):
        G = mundo_novo(303)
        garotos = [j for j in de_fora(G, 400, idade_max=19) if largura(eng.scout(G, j)) >= 8]
        self.assertTrue(garotos)
        j = garotos[0]
        antes = largura(eng.scout(G, j))
        eng.observar(G, j["id"])
        for _ in range(6):
            eng.observar_mes(G)
        self.assertLess(largura(eng.scout(G, j)), antes)

    def test_olheiro_avisa_venda_livre_e_troca_de_clube(self):
        G = mundo_novo(307)
        a, b, c = de_fora(G, 3)
        for j in (a, b, c):
            eng.observar(G, j["id"])
        a["listado"] = max(1, a["valor"])
        G["clubes"][b["clube"]]["elenco"].remove(b["id"])
        b["clube"] = None
        G["livres"].append(b["id"])
        outro = next(x for x in G["clubes"].values() if x["id"] not in (G["clube"], c["clube"]))
        G["clubes"][c["clube"]]["elenco"].remove(c["id"])
        c["clube"] = outro["id"]
        outro["elenco"].append(c["id"])
        eng.avisos_observados(G)
        log = " | ".join(G["noticias"][-3:])
        self.assertIn("%s foi colocado a venda" % a["nome"], log)
        self.assertIn("%s ficou sem clube" % b["nome"], log)
        self.assertIn("%s foi para o %s" % (c["nome"], outro["nome"]), log)
        # a segunda semana sem mudanca nao repete o aviso
        antes = list(G["noticias"])
        eng.avisos_observados(G)
        self.assertEqual(G["noticias"], antes)

    def test_quem_chega_ao_meu_clube_sai_da_lista(self):
        G = mundo_novo(311)
        j = de_fora(G, 1)[0]
        eng.observar(G, j["id"])
        meu = G["clubes"][G["clube"]]
        G["clubes"][j["clube"]]["elenco"].remove(j["id"])
        j["clube"] = meu["id"]
        meu["elenco"].append(j["id"])
        self.assertNotIn(str(j["id"]), eng.observados(G))


if __name__ == "__main__":
    unittest.main()
