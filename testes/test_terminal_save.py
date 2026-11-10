# -*- coding: utf-8 -*-
"""Terminal: save que nao abre ganha uma copia antes de o jogo novo gravar por cima."""

import contextlib
import io
import os
import unittest

import apoio

eng = apoio.eng


class TestSaveCorrompidoNoTerminal(unittest.TestCase):
    def setUp(self):
        self.save = os.path.join(apoio.TMP, "terminal_save.json")
        self.antes = {n: getattr(eng, n) for n in
                      ("SAVE", "ler", "novo_jogo", "loop", "travar_save", "preparar_terminal")}
        with open(self.save, "w", encoding="utf-8") as f:
            f.write('{"clubes": {"1": {"nome": "Sant')       # JSON cortado no meio
        self.chamadas = []
        eng.SAVE = self.save
        eng.ler = lambda _texto="": "s"
        eng.novo_jogo = lambda: self.chamadas.append("novo") or {"novo": True}
        eng.loop = lambda G: self.chamadas.append(G)
        eng.travar_save = lambda caminho=None: True
        eng.preparar_terminal = lambda _discreto=False: None

    def tearDown(self):
        for nome, valor in self.antes.items():
            setattr(eng, nome, valor)
        for sobra in (self.save, self.save + ".corrompido"):
            if os.path.exists(sobra):
                os.remove(sobra)

    def test_copia_o_save_antes_do_jogo_novo(self):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            eng.main()
        self.assertEqual(self.chamadas, ["novo", {"novo": True}])
        self.assertTrue(os.path.exists(self.save + ".corrompido"))
        with open(self.save + ".corrompido", encoding="utf-8") as f:
            self.assertIn('"Sant', f.read())
        self.assertIn(".corrompido", saida.getvalue())


if __name__ == "__main__":
    unittest.main()
