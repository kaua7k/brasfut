# -*- coding: utf-8 -*-
"""Simular: a janela de transferencias abrir SEMPRE para a simulacao, e avisa.

Era uma parada opcional (caixa "a janela de transferencias abrir"): desmarcada
- e a escolha fica guardada no navegador -, o Simular parava calado na semana
da abertura e, com o dialogo ainda aberto, o ritmo virava "Ate a janela
fechar" e um clique a mais atravessava a janela inteira sem aviso."""

import os
import unittest

import apoio

eng = apoio.eng

# o que um navegador com a preferencia antiga manda: tudo desligado
PARADAS_DESLIGADAS = {"lesao": False, "janela": False, "proposta": False,
                      "quebrado": False, "emprego": False}


class TestSimularAteAJanela(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(505)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Janela",
                                                    "opcoes": {"sem_demissao": True}})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": clubes[0]["id"]})
        cls.G = apoio.SESSAO.G
        while cls.G["semana"] < 10:
            apoio.avancar({"leve": True})

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_abertura_da_janela_para_e_avisa_mesmo_com_as_paradas_desligadas(self):
        G = self.G
        self.assertFalse(eng.mercado_aberto(G))
        o = apoio.chamar("GET", "/api/avanco/opcoes")
        self.assertNotIn("janela", o["paradas"], "a janela nao e mais parada opcional")
        op = next(x for x in o["opcoes"] if x["id"] == "janela")
        r = None
        # o laco do navegador, com folga: tem que parar sozinho na abertura
        for _ in range(op["semanas"] + 6):
            r = apoio.chamar("POST", "/api/avancar",
                             {"confirmar": True, "paradas": PARADAS_DESLIGADAS, "leve": True})
            if r.get("parar"):
                break
        self.assertEqual(G["semana"], 19)
        self.assertTrue(eng.mercado_aberto(G))
        self.assertEqual(r["parar"], "a janela de transferencias abriu")
        self.assertTrue(r["janela_abriu"])

    def test_semana_comum_nao_marca_janela(self):
        r = apoio.chamar("POST", "/api/avancar", {"confirmar": True, "leve": True})
        self.assertFalse(r.get("janela_abriu"))


if __name__ == "__main__":
    unittest.main()
