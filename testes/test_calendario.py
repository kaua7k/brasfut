# -*- coding: utf-8 -*-
"""Calendario: a temporada do meu clube semana a semana - jogos (com placar
depois de jogados), janela de transferencias e datas FIFA."""

import os
import unittest

import apoio

eng = apoio.eng


def semanas(tela, bloco):
    b = next((b for b in tela["blocos"] if b["id"] == bloco), None)
    return {s["numero"]: s for s in b["semanas"]} if b else {}


class TestCalendarioLiga(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(808)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Calendario"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": clubes[0]["id"]})
        cls.G = apoio.SESSAO.G

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def tela(self):
        return apoio.chamar("GET", "/api/calendario")["tela"]

    def test_38_semanas_com_o_adversario_da_tabela(self):
        G = self.G
        meu = G["clube"]
        liga = G["ligas"][G["clubes"][meu]["divisao"]]
        sem = semanas(self.tela(), "liga")
        self.assertEqual(sorted(sem), list(range(1, eng.SEMANAS_LIGA + 1)))
        for w in range(1, eng.SEMANAS_LIGA + 1):
            casa, fora = next(p for p in liga["rodadas"][w - 1] if meu in p)
            jogo = next(j for j in sem[w]["jogos"] if j["comp"] == "liga")
            adv = fora if casa == meu else casa
            self.assertEqual(jogo["adversario_id"], adv)
            self.assertEqual(jogo["mando"], "casa" if casa == meu else "fora")

    def test_janela_e_datas_fifa(self):
        sem = semanas(self.tela(), "liga")
        self.assertEqual(sem[2]["janela"], "aberta")
        self.assertEqual(sem[4]["janela"], "fecha")
        self.assertIsNone(sem[5]["janela"])
        self.assertEqual(sem[19]["janela"], "abre")
        self.assertEqual(sem[22]["janela"], "fecha")
        for w in sem:
            self.assertEqual(sem[w]["fifa"], w in eng.DATAS_FIFA, w)

    def test_copas_vivas_entram_nas_semanas_delas(self):
        sem = semanas(self.tela(), "liga")
        for w in eng.SEMANAS_COPA:
            self.assertIn("copa", [j["comp"] for j in sem[w]["jogos"]], w)

    def test_semana_jogada_mostra_placar(self):
        G = self.G
        apoio.avancar()
        apoio.avancar()
        tela = self.tela()
        sem = semanas(tela, "liga")
        self.assertTrue(sem[1]["passada"])
        self.assertTrue(sem[3]["atual"])
        self.assertFalse(sem[3]["passada"])
        meu = G["clube"]
        liga = G["ligas"][G["clubes"][meu]["divisao"]]
        for w in (1, 2):
            casa, fora, gc, gf = next(r for r in liga["resultados"][w - 1] if meu in r[:2])
            gm, gs = (gc, gf) if casa == meu else (gf, gc)
            jogo = next(j for j in sem[w]["jogos"] if j["comp"] == "liga")
            self.assertEqual(jogo["placar"], [gm, gs])
            self.assertEqual(jogo["resultado"], "v" if gm > gs else ("e" if gm == gs else "d"))
        # o proximo jogo do resumo e o da semana atual
        self.assertIn("Semana 3", tela["resumo"]["proximo"])

    def test_copa_eliminada_some_das_semanas_futuras(self):
        G = self.G
        cp = G["copas"]["copa"]
        guardado = (list(cp["vivos"]), cp.get("sorteio"))
        cp["vivos"].remove(G["clube"])
        cp["sorteio"] = None
        try:
            sem = semanas(self.tela(), "liga")
            for w in eng.SEMANAS_COPA:
                if w >= G["semana"]:
                    self.assertNotIn("copa", [j["comp"] for j in sem[w]["jogos"]], w)
        finally:
            cp["vivos"], cp["sorteio"] = guardado

    def test_zz_copa_jogada_vem_da_copa_e_nao_do_historico_do_tecnico(self):
        G = self.G
        meu = G["clube"]
        # placar_hist e do tecnico: depois de trocar de clube ele guarda jogos de
        # outro time. Um registro falso la nao pode aparecer no calendario.
        G.setdefault("placar_hist", []).append([G["temporada"], 1, "lib", meu, 9, 9, 1])
        while G["semana"] <= 4:
            apoio.avancar()
        sem = semanas(self.tela(), "liga")
        self.assertNotIn([9, 9], [j["placar"] for j in sem[1]["jogos"]])
        lib = G["copas"]["lib"]
        g = eng.grupo_de(lib, meu)
        casa, fora, gc, gf = next(r for r in g["resultados"][0] if meu in r[:2])
        jogo = next(j for j in sem[3]["jogos"] if j["comp"] == "lib")
        self.assertEqual(jogo["placar"], [gc, gf] if casa == meu else [gf, gc])
        copa = G["copas"]["copa"]
        h = next(h for h in copa["historico"] if h["semana"] == 4)
        j = next((j for j in h["jogos"] if meu in (j["a"], j["b"])), None)
        if j:
            jogos = [x for x in sem[4]["jogos"] if x["comp"] == "copa"]
            ida = j["ida"] if j["a"] == meu else j["ida"][::-1]
            self.assertEqual(jogos[0]["placar"], ida)

    def test_resumo_da_janela(self):
        G = self.G
        guardada = G["semana"]
        try:
            G["semana"] = 10
            self.assertIn("abre na semana 19", self.tela()["resumo"]["janela"])
            G["semana"] = 20
            r = self.tela()["resumo"]
            self.assertTrue(r["janela_aberta"])
            self.assertIn("semana 22", r["janela"])
        finally:
            G["semana"] = guardada


def participa(cp, cid):
    """O clube esta (ou esteve) nesta copa no ano: vivo, esperando, num grupo ou
    num jogo ja registrado."""
    if cid in cp.get("vivos", []) or cid in cp.get("espera", []):
        return True
    if any(cid in g["times"] for g in cp.get("grupos") or []):
        return True
    return any(cid in (j["a"], j["b"]) for h in cp.get("historico") or [] for j in h.get("jogos") or [])


class TestCalendarioTrocaDeClube(unittest.TestCase):
    """Regra: o calendario so mostra jogos do clube atual. Trocou de clube no meio
    do ano, todas as semanas (passadas e futuras) passam a ser as do clube novo."""

    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(707)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Troca"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": clubes[0]["id"]})
        G = cls.G = apoio.SESSAO.G
        cls.antigo = G["clube"]
        # o antigo joga liga, Libertadores (semana 3) e Copa do Brasil (semana 4)
        while G["semana"] <= 5:
            apoio.avancar()
        cls.novo = next(c["id"] for c in clubes if c["divisao"] == "B")
        eng.assumir_clube(G, cls.novo, "proposta")

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_so_jogos_do_clube_novo(self):
        G = self.G
        novo = self.novo
        liga = G["ligas"][G["clubes"][novo]["divisao"]]
        tela = apoio.chamar("GET", "/api/calendario")["tela"]
        vistos = 0
        for b in tela["blocos"]:
            for s in b["semanas"]:
                for j in s["jogos"]:
                    vistos += 1
                    self.assertNotEqual(j["adversario_id"], novo)
                    if j["comp"] == "liga":
                        par = next(p for p in liga["rodadas"][s["numero"] - 1] if novo in p)
                        self.assertIn(j["adversario_id"], par, s["rotulo"])
                    elif j["comp"] != "estadual":
                        self.assertTrue(participa(G["copas"][j["comp"]], novo),
                                        "%s: %s e do clube antigo" % (s["rotulo"], j["competicao"]))
        self.assertGreater(vistos, 0)
        # o antigo estava na Libertadores; o novo, da Serie B, nao
        if not participa(G["copas"]["lib"], novo):
            comps = {j["comp"] for b in tela["blocos"] for s in b["semanas"] for j in s["jogos"]}
            self.assertNotIn("lib", comps)

    def test_semanas_passadas_tem_os_placares_do_clube_novo(self):
        G = self.G
        novo = self.novo
        liga = G["ligas"][G["clubes"][novo]["divisao"]]
        tela = apoio.chamar("GET", "/api/calendario")["tela"]
        sem = semanas(tela, "liga")
        for w in range(1, G["semana"]):
            casa, fora, gc, gf = next(r for r in liga["resultados"][w - 1] if novo in r[:2])
            jogo = next(j for j in sem[w]["jogos"] if j["comp"] == "liga")
            self.assertEqual(jogo["placar"], [gc, gf] if casa == novo else [gf, gc])
        self.assertIn(G["clubes"][novo]["nome"], tela["subtitulo"])


class TestCalendarioEstadual(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash_antes = apoio.hash_do_save_real()
        if os.path.exists(apoio.SAVE_TESTE):
            os.remove(apoio.SAVE_TESTE)
        eng.rng.seed(909)
        clubes = apoio.chamar("POST", "/api/novo", {"nome": "Estadual"})["clubes"]
        apoio.chamar("POST", "/api/clube", {"id": clubes[0]["id"]})
        G = cls.G = apoio.SESSAO.G
        # abre o ano pelo estadual, como a virada faz
        G["fase"], G["semana"] = "entretemporada", 0
        eng.iniciar_estaduais(G)

    @classmethod
    def tearDownClass(cls):
        assert apoio.hash_do_save_real() == cls.hash_antes, "teste mexeu no save real"

    def test_estadual_vem_antes_da_liga(self):
        tela = apoio.chamar("GET", "/api/calendario")["tela"]
        ids = [b["id"] for b in tela["blocos"]]
        self.assertEqual(ids, ["estadual", "liga"])
        est = eng.meu_estadual(self.G)
        sem = semanas(tela, "estadual")
        self.assertEqual(len(sem), eng.rodadas_estaduais(self.G))
        self.assertTrue(sem[1]["atual"])
        self.assertEqual(sem[1]["janela"], "aberta")
        meu = self.G["clube"]
        casa, fora = next(p for p in est["rodadas"][0] if meu in p)
        jogo = next(j for j in sem[1]["jogos"] if j["comp"] == "estadual")
        self.assertEqual(jogo["adversario_id"], fora if casa == meu else casa)
        # mata-mata futuro aparece sem adversario
        primeira_mata = len(est["rodadas"]) + 1
        if eng.tem_mata(est):
            jogo = next(j for j in sem[primeira_mata]["jogos"] if j["comp"] == "estadual")
            self.assertIsNone(jogo["adversario_id"])

    def test_rodada_jogada_do_estadual_tem_placar(self):
        apoio.avancar()
        sem = semanas(apoio.chamar("GET", "/api/calendario")["tela"], "estadual")
        est = eng.meu_estadual(self.G)
        meu = self.G["clube"]
        r = next((r for r in est["resultados"][0] if meu in r[:2]), None)
        jogo = next((j for j in sem[1]["jogos"] if j["comp"] == "estadual"), None)
        if r is None:
            self.assertIsNone(jogo)
            return
        casa, fora, gc, gf = r
        self.assertEqual(jogo["placar"], [gc, gf] if casa == meu else [gf, gc])
        self.assertTrue(sem[2]["atual"])


if __name__ == "__main__":
    unittest.main()


class TestFormatoDaFase(unittest.TestCase):
    """A regra de mando do mata-mata mora so em eng.formato_da_fase: a semana,
    o intervalo e o Calendario leem dali."""

    def test_final_ida_e_volta_nao_e_neutra(self):
        cp = {"vivos": [1, 2], "final_ida_volta": True}
        self.assertEqual(eng.formato_da_fase(cp), (False, False, False))

    def test_final_de_jogo_unico_e_neutra(self):
        self.assertEqual(eng.formato_da_fase({"vivos": [1, 2]}), (True, True, True))

    def test_com_clube_esperando_ainda_nao_e_final(self):
        cp = {"vivos": [1, 2], "espera": [3]}
        self.assertEqual(eng.formato_da_fase(cp)[0], False)

    def test_jogo_unico_fora_da_final_segue_a_copa(self):
        cp = {"vivos": [1, 2, 3, 4], "jogo_unico": True}
        self.assertEqual(eng.formato_da_fase(cp), (False, True, False))
