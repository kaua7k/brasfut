# -*- coding: utf-8 -*-
"""Intervalo interativo: o meu jogo de liga para aos 45', o tecnico mexe e a
semana usa o resultado dessa partida (sem jogar de novo)."""

import os
import unittest

import apoio

eng = apoio.eng


def ate_semana_de_liga(G):
    for _ in range(40):
        if eng.meu_jogo_de_liga(G):
            return True
        apoio.chamar("POST", "/api/avancar", {"leve": True, "confirmar": True})
    return False


class TestIntervalo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(601)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Teste Intervalo",
                                                    "opcoes": {"sem_demissao": True}})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
        cls.G = apoio.SESSAO.G
        assert ate_semana_de_liga(cls.G)

    @classmethod
    def tearDownClass(cls):
        apoio.SESSAO.intervalo = None
        eng.PARTIDA_PRONTA.clear()
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_para_no_intervalo_e_o_segundo_tempo_usa_as_decisoes(self):
        G = self.G
        c = G["clubes"][G["clube"]]
        self.assertTrue(ate_semana_de_liga(G))
        casa, fora = eng.meu_jogo_de_liga(G)
        r = apoio.chamar("POST", "/api/avancar", {"confirmar": True, "intervalo": True})
        it = r["intervalo"]
        self.assertEqual(it["times"], [G["clubes"][casa]["nome"], G["clubes"][fora]["nome"]])
        self.assertTrue(all(l["minuto"] <= 46 for l in it["lances"]))
        self.assertEqual(len(it["titulares"]), len(apoio.SESSAO.intervalo["foto"]["esc"]))
        self.assertTrue(it["banco"])
        semana = G["semana"]
        sai = it["titulares"][-1]["id"]
        entra = it["banco"][0]["id"]
        r2 = apoio.chamar("POST", "/api/partida/segundo-tempo",
                          {"tatica": "Retranca", "trocas": [[sai, entra]]})
        self.assertEqual(G["semana"], semana + 1, "a semana andou")
        self.assertIsNone(apoio.SESSAO.intervalo)
        self.assertEqual(eng.PARTIDA_PRONTA, {}, "o jogo pronto foi usado pela semana")
        ultimo = G["historico_meus"][-1]
        self.assertIn([46, 0 if casa == c["id"] else 1, "Retranca", "intervalo"],
                      [list(x) for x in ultimo.get("instrucoes", [])])
        nomes = [s for s in ultimo["subs"] if s[0] == 46]
        self.assertTrue(nomes, "a troca do intervalo entrou no registro")
        self.assertEqual(c["tatica"], "Equilibrado", "o clube volta com a mentalidade de antes")
        self.assertTrue(r2["partidas"])

    def test_sem_decisao_e_preferencia_desligada(self):
        G = self.G
        self.assertTrue(ate_semana_de_liga(G))
        r = apoio.chamar("POST", "/api/avancar", {"confirmar": True, "intervalo": True})
        self.assertIn("intervalo", r)
        semana = G["semana"]
        # a tela fechou: o proximo avancar termina o jogo como estava e segue
        apoio.chamar("POST", "/api/avancar", {"confirmar": True, "intervalo": True})
        self.assertEqual(G["semana"], semana + 1)
        self.assertTrue(ate_semana_de_liga(G))
        apoio.chamar("POST", "/api/intervalo/preferencia", {"ligado": False})
        r = apoio.chamar("POST", "/api/avancar", {"confirmar": True, "intervalo": True})
        self.assertNotIn("intervalo", r)
        apoio.chamar("POST", "/api/intervalo/preferencia", {"ligado": True})
        apoio.chamar("POST", "/api/partida/segundo-tempo", {}, status=400)

    def test_partida_sem_pausa_e_igual_ao_simular(self):
        G = self.G
        a, b = [x["id"] for x in G["clubes"].values() if x["divisao"] == "C"][:2]
        g = eng.partida(G, a, b, "liga", False, pausar_lado=0)
        foto = next(g)
        self.assertEqual(len(foto["placar"]), 2)
        with self.assertRaises(StopIteration):
            g.send({})


if __name__ == "__main__":
    unittest.main()
