# -*- coding: utf-8 -*-
"""Nenhuma rota responde 500, venha o que vier no corpo do pedido.

O 500 e o motor quebrando com excecao de Python; pedido torto (tipo errado,
campo faltando, id que nao existe) tem que voltar 400 com uma frase. Cobre
tambem as rotas que nenhum outro teste chamava (propostas recebidas, vitrine,
cessao, opcao de compra, esquema, plano de jogo, regime de treino, preco do
ingresso), e as telas de leitura numa carreira nova - no CI nao ha save real,
e test_telas ficava pulado.
"""

import os
import unittest

import apoio

eng = apoio.eng
rotas = apoio.rotas
SESSAO = apoio.SESSAO

# trocam de carreira, de clube ou de semana: tem teste proprio e nao entram na bateria
FORA = {"/api/novo", "/api/abrir", "/api/menu", "/api/slot/apagar", "/api/clube", "/api/avancar",
        "/api/avancar/ate-o-jogo", "/api/partida/segundo-tempo", "/api/carreira/demitir",
        "/api/carreira/proposta", "/api/salvar"}

# valores do tipo errado para os campos que as rotas leem
TORTO = {"ids": 5, "id": {}, "anos": "3a", "filtros": [1], "proposta": "x", "valor": "abc",
         "meses": None, "preco": [], "lugares": {}, "slot": "z", "aba": 5, "tipo": 7,
         "espaco": [], "indice": "0", "nivel": "x", "item": 3, "alvo": {}, "pos": 1,
         "a": "x", "b": None, "esquema": 9, "ligado": "false", "ligada": "false",
         "itens": "x", "precos": 3, "regime": [], "foco": {}, "tela": 1, "vaga": [], "jogador": {},
         "tatica": 5, "trocas": "x", "plano": "x", "regras": 7, "origem": [], "confirmar": "sim",
         "escala": "grande", "liga": 3, "div": [], "clube": "x", "pid": "x", "opcao": {}}
CORPOS = [
    {},
    TORTO,
    {"ids": [None, "a", -1, 10 ** 9, 3.5, [1]], "id": -1, "anos": -5, "valor": -1, "meses": 999,
     "preco": -3, "lugares": 10 ** 12, "indice": 99, "itens": [None, 3, {"id": "x"}, [1, 2]],
     "precos": {"x": "y"}, "filtros": {"ovr": "alto", "pos": 7, "regiao": []},
     "proposta": {"anos": [], "salario": "muito", "valor": None, "pct": {}},
     "trocas": [[1], ["a", "b"], None], "regras": [None, 4, {"quando": 3}]},
    {"id": "abc", "ids": "1,2,3", "jogador": "10", "tipo": "compra", "aba": "nao-existe"},
]


class TestRotasFumaca(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(2711)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Fumaca", "opcoes": {"sem_demissao": True}})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": clubes[0]["id"]})
        cls.G = SESSAO.G
        for _ in range(3):
            apoio.avancar({"leve": True})

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_toda_tela_de_leitura_abre(self):
        for (metodo, caminho) in sorted(rotas.ROTAS):
            if metodo != "GET":
                continue
            with self.subTest(tela=caminho):
                status, obj = rotas.despachar("GET", caminho, None)
                # o resumo so existe depois da primeira temporada encerrada
                self.assertEqual(status, 400 if caminho == "/api/resumo" else 200, obj)
                self.assertIsInstance(obj, dict)

    def test_rota_inexistente_e_404(self):
        apoio.chamar("GET", "/api/nao-existe", status=404)

    def test_corpo_que_nao_e_objeto_e_400(self):
        for corpo in ([1, 2], "texto", 7):
            status, _ = rotas.despachar("POST", "/api/mercado", corpo)
            self.assertEqual(status, 400)

    def test_pedido_torto_nunca_vira_500(self):
        quebraram = []
        for (metodo, caminho) in sorted(rotas.ROTAS):
            if metodo != "POST" or caminho in FORA:
                continue
            for n, corpo in enumerate(CORPOS):
                status, obj = rotas.despachar("POST", caminho, dict(corpo))
                if status >= 500:
                    quebraram.append("%s corpo %d: %s" % (caminho, n, obj.get("detalhe")))
        self.assertEqual(quebraram, [])
        # e o jogo segue inteiro depois da bateria
        G = SESSAO.G
        for c in G["clubes"].values():
            for p in c["elenco"]:
                self.assertIn(p, G["jogadores"])
        apoio.avancar({"leve": True})

    def test_erro_500_fala_com_o_jogador_e_guarda_o_detalhe(self):
        def quebra(_corpo):
            raise TypeError("int() argument must be a string")
        rotas.ROTAS[("POST", "/api/_teste_quebra")] = quebra
        try:
            import contextlib
            import io
            with contextlib.redirect_stderr(io.StringIO()):
                status, obj = rotas.despachar("POST", "/api/_teste_quebra", {})
        finally:
            del rotas.ROTAS[("POST", "/api/_teste_quebra")]
        self.assertEqual(status, 500)
        self.assertNotIn("TypeError", obj["erro"])
        self.assertIn("TypeError", obj["detalhe"])

    def test_encerrar_carreira_so_com_a_demissao_na_tela(self):
        self.assertIsNone(SESSAO.pendencia)
        apoio.chamar("POST", "/api/clube", {"encerrar": True}, status=400)
        self.assertIsNone(SESSAO.pendencia)
        self.assertIsInstance(apoio.chamar("GET", "/api/painel"), dict)

    def test_liga_e_desliga_so_com_booleano(self):
        apoio.chamar("POST", "/api/intervalo/preferencia", {"ligado": "false"}, status=400)
        apoio.chamar("POST", "/api/escalacao/auto", {"ligada": "false"}, status=400)
        self.assertFalse(apoio.chamar("POST", "/api/intervalo/preferencia", {"ligado": False})["ligado"])
        self.assertTrue(apoio.chamar("POST", "/api/intervalo/preferencia", {"ligado": True})["ligado"])

    def test_falha_ao_salvar_aparece_na_resposta_ate_gravar_de_novo(self):
        G = SESSAO.G
        original = eng.salvar

        def disco_cheio(_G, _caminho=None):
            raise OSError("No space left on device")
        eng.salvar = disco_cheio
        try:
            r = apoio.chamar("POST", "/api/intervalo/preferencia", {"ligado": True})
            self.assertIn("No space left", r["save_falhou"])
            # leitura tambem avisa: o problema continua la
            self.assertIn("save_falhou", apoio.chamar("GET", "/api/painel"))
            apoio.chamar("POST", "/api/salvar", status=400)
        finally:
            eng.salvar = original
        r = apoio.chamar("POST", "/api/intervalo/preferencia", {"ligado": True})
        self.assertNotIn("save_falhou", r)
        self.assertIsNone(eng.FALHA_AO_SALVAR)
        self.assertIs(G, SESSAO.G)


if __name__ == "__main__":
    unittest.main()
