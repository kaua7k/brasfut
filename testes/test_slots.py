# -*- coding: utf-8 -*-
"""Tres slots de save: cada carreira no seu arquivo, o slot 1 e o save de
sempre, e o menu le um resumo pequeno em vez do save inteiro."""

import os
import unittest

import apoio

eng = apoio.eng
SESSAO = apoio.SESSAO


class TestSlots(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        cls.limpar()

    @classmethod
    def tearDownClass(cls):
        cls.limpar()
        SESSAO.usar_slot(1)
        SESSAO.slot_novo = None
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    @staticmethod
    def limpar():
        for n in (1, 2, 3):
            for arq in (SESSAO.caminho_slot(n), eng.caminho_resumo_save(SESSAO.caminho_slot(n))):
                if os.path.exists(arq):
                    os.remove(arq)

    def criar(self, slot, nome, clube_idx=0):
        clubes = apoio.chamar("POST", "/api/novo", {"nome": nome, "slot": slot})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": clubes[clube_idx]["id"]})

    def test_carreiras_em_slots_separados(self):
        self.limpar()
        self.criar(1, "Tecnico Um")
        self.criar(2, "Tecnico Dois", clube_idx=3)
        self.assertEqual(SESSAO.slot, 2)
        self.assertTrue(os.path.exists(SESSAO.caminho_slot(1)))
        self.assertTrue(os.path.exists(SESSAO.caminho_slot(2)))
        self.assertTrue(SESSAO.caminho_slot(2).endswith("brasfut_save_2.json"))
        slots = {s["slot"]: s for s in apoio.chamar("GET", "/api/estado")["slots"]}
        self.assertEqual(slots[1]["tecnico"], "Tecnico Um")
        self.assertEqual(slots[2]["tecnico"], "Tecnico Dois")
        self.assertTrue(slots[3]["vazio"])
        # voltar ao menu e abrir o slot 1 traz a outra carreira
        r = apoio.chamar("POST", "/api/menu")
        self.assertIsNone(SESSAO.G)
        self.assertEqual(r["jogo"], "tem_save")
        apoio.chamar("POST", "/api/abrir", {"slot": 1})
        self.assertEqual(SESSAO.G["tecnico"], "Tecnico Um")
        self.assertEqual(eng.SAVE, SESSAO.caminho_slot(1))

    def test_desistir_da_carreira_nova_nao_muda_o_slot(self):
        self.limpar()
        self.criar(1, "Aberto")
        apoio.chamar("POST", "/api/novo", {"nome": "Desistiu", "slot": 3})
        # sem escolher clube, quem grava continua sendo o slot 1
        self.assertEqual(SESSAO.slot, 1)
        self.assertEqual(eng.SAVE, SESSAO.caminho_slot(1))
        self.assertFalse(os.path.exists(SESSAO.caminho_slot(3)))
        SESSAO._pendente_novo = None

    def test_apagar_slot(self):
        self.limpar()
        self.criar(2, "Apagar")
        apoio.chamar("POST", "/api/menu")
        apoio.chamar("POST", "/api/slot/apagar", {"slot": 2})
        self.assertFalse(os.path.exists(SESSAO.caminho_slot(2)))
        self.assertFalse(os.path.exists(eng.caminho_resumo_save(SESSAO.caminho_slot(2))))
        # o slot aberto nao se apaga
        self.criar(3, "Aberto")
        apoio.chamar("POST", "/api/slot/apagar", {"slot": 3}, status=400)

    def test_save_antigo_sem_resumo_ganha_um(self):
        self.limpar()
        self.criar(1, "Antigo")
        resumo = eng.caminho_resumo_save(SESSAO.caminho_slot(1))
        os.remove(resumo)
        slots = {s["slot"]: s for s in apoio.chamar("GET", "/api/estado")["slots"]}
        self.assertEqual(slots[1]["tecnico"], "Antigo")
        self.assertTrue(os.path.exists(resumo))

    def test_opcoes_da_carreira_viram_padrao(self):
        self.limpar()
        apoio.chamar("POST", "/api/novo", {"nome": "Padrao", "slot": 1,
                                           "opcoes": {"dificuldade": "dificil", "sem_demissao": True}})
        cfg = apoio.chamar("GET", "/api/config")["config"]
        self.assertEqual(cfg["dificuldade"], "dificil")
        self.assertTrue(cfg["sem_demissao"])
        apoio.chamar("POST", "/api/config", {"dificuldade": "normal", "sem_demissao": False})
        SESSAO._pendente_novo = None

    def test_slot_invalido(self):
        apoio.chamar("POST", "/api/abrir", {"slot": 7}, status=400)


if __name__ == "__main__":
    unittest.main()
