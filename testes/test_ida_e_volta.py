# -*- coding: utf-8 -*-
"""Salvar, reabrir e continuar: o mundo reaberto e o mesmo que estava na memoria.

Duas garantias, em carreira classica e no modo caos:
- o save reaberto e identico ao mundo vivo (nenhuma migracao mexe num mundo
  saudavel, nenhuma chave se perde no JSON);
- jogar as mesmas semanas, com a mesma semente, no mundo vivo e no reaberto da
  o mesmo resultado.

Foi este teste que achou os 48 clubes-fantasma: ate 2026-11-10 todo save
reaberto ganhava de novo os sul-americanos de CLUBES_LIB/CLUBES_SUL como "EX".
"""

import json
import os
import shutil
import unittest

import apoio

eng = apoio.eng
SESSAO = apoio.SESSAO
COPIA = os.path.join(apoio.TMP, "ida_e_volta.json")


def canonico(G):
    d = dict(G)
    d["clubes"] = {str(k): v for k, v in G["clubes"].items()}
    d["jogadores"] = {str(k): v for k, v in G["jogadores"].items()}
    return json.loads(json.dumps(d, sort_keys=True))


def diferencas(a, b, onde="", achadas=None, limite=12):
    """Os primeiros caminhos em que dois mundos diferem (para a mensagem do teste)."""
    achadas = [] if achadas is None else achadas
    if len(achadas) >= limite:
        return achadas
    if type(a) is not type(b):
        achadas.append("%s: %s x %s" % (onde, type(a).__name__, type(b).__name__))
    elif isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                achadas.append("%s/%s: so de um lado" % (onde, k))
            else:
                diferencas(a[k], b[k], "%s/%s" % (onde, k), achadas, limite)
    elif isinstance(a, list):
        if len(a) != len(b):
            achadas.append("%s: %d x %d itens" % (onde, len(a), len(b)))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                diferencas(x, y, "%s[%d]" % (onde, i), achadas, limite)
    elif a != b:
        achadas.append("%s: %r x %r" % (onde, a, b))
    return achadas


def mundo(semente, opcoes=None):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(semente)
    opcoes = dict(opcoes or {}, sem_demissao=True)
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Ida e Volta", "opcoes": opcoes})["clubes"]
    apoio.chamar("POST", "/api/clube", {"id": clubes[0]["id"]})
    return SESSAO.G


def reabrir():
    """O caminho de verdade: o save vai para o lugar dele e a API o abre."""
    shutil.copyfile(COPIA, apoio.SAVE_TESTE)
    apoio.chamar("POST", "/api/abrir")
    return SESSAO.G


class Base(object):
    SEMENTE = 0
    OPCOES = None
    SEMANAS = 0

    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        cls.G = mundo(cls.SEMENTE, cls.OPCOES)
        for _ in range(cls.SEMANAS):
            apoio.avancar({"leve": True})

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(COPIA):
            os.remove(COPIA)
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def conferir_ida_e_volta(self):
        """Salva, reabre, compara; depois joga 2 semanas dos dois lados e compara de novo."""
        G = SESSAO.G
        # quem nasceu depois da ultima convocacao ganha nacionalidade ao reabrir
        # (regra do motor): fixa antes, para comparar o resto
        eng.fixar_nacionalidades(G)
        eng.salvar(G, COPIA)
        vivo = canonico(G)
        aberto = canonico(eng.carregar(COPIA))
        self.assertEqual(diferencas(vivo, aberto), [], "o save reaberto nao e o mundo que foi salvo")

        eng.rng.seed(4321)
        for _ in range(2):
            apoio.avancar({"leve": True})
        depois_vivo = canonico(SESSAO.G)
        reabrir()
        eng.rng.seed(4321)
        for _ in range(2):
            apoio.avancar({"leve": True})
        self.assertEqual(diferencas(depois_vivo, canonico(SESSAO.G)), [],
                         "as mesmas semanas deram resultado diferente no save reaberto")


class TestIdaEVoltaClassico(Base, unittest.TestCase):
    SEMENTE = 2611
    SEMANAS = 0

    def test_1_mundo_novo_reaberto_nao_ganha_clube_nem_jogador(self):
        G = self.G
        clubes, jogadores = len(G["clubes"]), len(G["jogadores"])
        eng.salvar(G, COPIA)
        aberto = eng.carregar(COPIA)
        self.assertEqual((len(aberto["clubes"]), len(aberto["jogadores"])), (clubes, jogadores))
        nomes = [c["nome"] for c in aberto["clubes"].values() if c["divisao"] not in eng.DIVISOES_BR]
        self.assertEqual(len(nomes), len(set(nomes)), "clube de fora duplicado")
        # e nenhuma chave nasce so ao reabrir
        self.assertEqual(sorted(set(aberto) - set(G)), [])

    def test_2_no_comeco_da_liga(self):
        # a primeira temporada comeca direto na liga (o estadual vem no segundo ano)
        for _ in range(4):
            apoio.avancar({"leve": True})
        self.assertEqual(SESSAO.G["fase"], "liga")
        self.conferir_ida_e_volta()

    def test_3_depois_da_data_fifa_na_virada_e_no_estadual(self):
        G = SESSAO.G
        while G["semana"] < 9:                 # passa da primeira data FIFA
            apoio.avancar({"leve": True})
        self.conferir_ida_e_volta()
        G = SESSAO.G
        ano = G["temporada"]
        for _ in range(60):
            if G["temporada"] != ano:
                break
            apoio.avancar({"leve": True})
        self.assertEqual(G["temporada"], ano + 1, "a temporada nao virou")
        self.conferir_ida_e_volta()
        G = SESSAO.G
        for _ in range(6):
            if G["fase"] == "estadual" and int(G.get("semana_est") or 0) >= 3:
                break
            apoio.avancar({"leve": True})
        self.assertEqual(G["fase"], "estadual")
        self.conferir_ida_e_volta()


class TestIdaEVoltaCaos(Base, unittest.TestCase):
    SEMENTE = 2612
    OPCOES = {"modo": "caos", "caos_nivel": "caotico"}
    SEMANAS = 22

    def test_caos_com_bombas_e_plantoes(self):
        est = eng.estado_caos(SESSAO.G)
        self.assertTrue(est["historia"], "22 semanas no caotico sem nenhum plantao")
        self.conferir_ida_e_volta()


class TestClubesFantasma(Base, unittest.TestCase):
    """Save que ja reabriu com o bug antigo: os duplicados saem, o resto fica."""
    SEMENTE = 2613

    def fantasmas(self, G):
        usados = {j["nome"] for j in G["jogadores"].values()}
        G["seq_c"] = max(G["clubes"])
        G["seq"] = max(G["jogadores"])
        return [eng.novo_clube(G, dados, "EX", usados) for dados in eng.CLUBES_LIB + eng.CLUBES_SUL]

    def test_duplicados_saem_e_o_jogo_segue(self):
        G = self.G
        clubes, jogadores = len(G["clubes"]), len(G["jogadores"])
        novos = self.fantasmas(G)
        self.assertEqual(len(G["clubes"]), clubes + 48)
        # um fantasma convocado pela selecao: a lista perde o nome dele
        convocado = novos[0]["elenco"][0]
        G["convocacao"] = {"temporada": G["temporada"], "semana": 8, "liberada": True,
                           "listas": {"ARG": [convocado]}}
        eng.salvar(G, COPIA)
        G = reabrir()
        self.assertEqual((len(G["clubes"]), len(G["jogadores"])), (clubes, jogadores))
        self.assertEqual(G["convocacao"]["listas"]["ARG"], [])
        for c in G["clubes"].values():
            for p in c["elenco"]:
                self.assertIn(p, G["jogadores"])
        for _ in range(3):
            apoio.avancar({"leve": True})

    def test_quem_esta_numa_copa_ou_tem_titulo_fica(self):
        G = SESSAO.G
        clubes = len(G["clubes"])
        novos = self.fantasmas(G)
        na_copa, com_titulo = novos[0], novos[1]
        G["copas"]["lib"]["vivos"].append(na_copa["id"])
        com_titulo["titulos"] = {"Libertadores": 1}
        self.assertEqual(eng.remover_clubes_fantasma(G), 46)
        self.assertEqual(len(G["clubes"]), clubes + 2)
        self.assertIn(na_copa["id"], G["clubes"])
        self.assertIn(com_titulo["id"], G["clubes"])
        # devolve o mundo ao que era
        G["copas"]["lib"]["vivos"].remove(na_copa["id"])
        com_titulo["titulos"] = {}
        self.assertEqual(eng.remover_clubes_fantasma(G), 2)
        self.assertEqual(len(G["clubes"]), clubes)

    def test_europeu_e_estrangeiro_sem_gemeo_nao_sao_fantasma(self):
        G = SESSAO.G
        antes = len(G["clubes"])
        usados = {j["nome"] for j in G["jogadores"].values()}
        G["seq_c"] = max(G["clubes"])
        G["seq"] = max(G["jogadores"])
        sozinho = eng.novo_clube(G, ("Clube Sem Gemeo", "ARG", "Estadio", 10000, 60), "EX", usados)
        self.assertEqual(eng.remover_clubes_fantasma(G), 0)
        self.assertEqual(len(G["clubes"]), antes + 1)
        for p in list(sozinho["elenco"]):
            del G["jogadores"][p]
        del G["clubes"][sozinho["id"]]


if __name__ == "__main__":
    unittest.main()
