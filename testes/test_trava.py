# -*- coding: utf-8 -*-
"""Dois BRASFUT na mesma pasta: o segundo nao abre."""

import os
import subprocess
import sys
import unittest

import apoio

TENTA = "import sys; sys.path.insert(0, %r); import brasfut; print(brasfut.travar_save(%r))"


def outro_processo_trava(caminho):
    r = subprocess.run([sys.executable, "-c", TENTA % (apoio.RAIZ, caminho)],
                       capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


class TestTrava(unittest.TestCase):
    def test_segundo_processo_e_recusado_e_liberado_depois(self):
        caminho = os.path.join(apoio.TMP, "trava.json")
        # quem segura e um processo filho, para nao prender a trava neste
        dono = subprocess.Popen(
            [sys.executable, "-c", TENTA % (apoio.RAIZ, caminho)
             + "; sys.stdout.flush(); sys.stdin.read()"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        try:
            self.assertEqual(dono.stdout.readline().strip(), "True")
            self.assertEqual(outro_processo_trava(caminho), "False")
        finally:
            dono.stdin.close()
            dono.wait(timeout=60)
            dono.stdout.close()
        # o dono saiu: o sistema soltou a trava sem ninguem apagar arquivo
        self.assertEqual(outro_processo_trava(caminho), "True")


if __name__ == "__main__":
    unittest.main()
