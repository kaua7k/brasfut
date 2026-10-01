# -*- coding: utf-8 -*-
"""Lint visual: todo valor de cor e de fonte da web mora nos tokens.

Fora do bloco :root de base.css nao existe hex, rgba nem font-size em px; a
escala de fonte tem no maximo seis degraus; o TSX nao carrega style={{}} com
valor fixo (inline so para o que vem do dado, como posicao e largura); e o
amarelo antigo (--acento) nao volta: acao e azul, conquista e dourado, atencao
e ambar.
"""

import glob
import os
import re
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = os.path.join(RAIZ, "web", "src", "estilo", "base.css")
TSX = glob.glob(os.path.join(RAIZ, "web", "src", "**", "*.tsx"), recursive=True)

COR_SOLTA = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\(")
FONTE_SOLTA = re.compile(r"font-size:\s*[0-9.]+(px|rem|em)")
ESTILO = re.compile(r"style=\{\{(.*?)\}\}", re.S)


# os refinos por grupo de telas seguem as mesmas regras de base.css
EXTRAS = sorted(glob.glob(os.path.join(RAIZ, "web", "src", "estilo", "telas-*.css")))


def _css():
    with open(CSS, encoding="utf-8") as f:
        s = f.read()
    ini = s.index(":root {")
    fim = s.index("\n}", ini) + 2
    corpo = s[fim:]
    for caminho in EXTRAS:
        with open(caminho, encoding="utf-8") as f:
            corpo += "\n" + f.read()
    return s[ini:fim], corpo


def _sem_comentario(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


class TestTokens(unittest.TestCase):
    def test_css_sem_cor_nem_fonte_fora_dos_tokens(self):
        _, corpo = _css()
        achados = []
        for n, linha in enumerate(_sem_comentario(corpo).split("\n")):
            if COR_SOLTA.search(linha) or FONTE_SOLTA.search(linha):
                achados.append(linha.strip())
        self.assertEqual(achados, [], "valor solto fora do :root")

    def test_escala_de_fonte_tem_no_maximo_seis_degraus(self):
        raiz, corpo = _css()
        degraus = set(re.findall(r"--(fs-[\w-]+):", raiz))
        self.assertLessEqual(len(degraus), 6, sorted(degraus))
        usados = set(re.findall(r"var\(--(fs-[\w-]+)\)", corpo))
        self.assertEqual(usados - degraus, set(), "degrau usado sem existir")

    def test_todo_token_usado_existe(self):
        raiz, corpo = _css()
        definidos = set(re.findall(r"--([\w-]+):", raiz))
        usados = set(re.findall(r"var\(--([\w-]+)\)", corpo))
        for caminho in TSX:
            with open(caminho, encoding="utf-8") as f:
                usados |= set(re.findall(r"var\(--([\w-]+)\)", f.read()))
        self.assertEqual(usados - definidos, set())

    def test_amarelo_antigo_nao_volta(self):
        with open(CSS, encoding="utf-8") as f:
            self.assertNotIn("--acento", f.read())
        for caminho in TSX:
            with open(caminho, encoding="utf-8") as f:
                self.assertNotIn("--acento", f.read(), caminho)

    def test_tsx_sem_estilo_inline_fixo(self):
        achados = []
        for caminho in TSX:
            with open(caminho, encoding="utf-8") as f:
                s = f.read()
            for m in ESTILO.finditer(s):
                # inline e para valor que vem do dado: posicao, largura
                if "${" not in m.group(1):
                    achados.append("%s: %s" % (os.path.basename(caminho), m.group(1).strip()))
            if COR_SOLTA.search(s):
                achados.append("%s: cor solta no TSX" % os.path.basename(caminho))
        self.assertEqual(achados, [])


if __name__ == "__main__":
    unittest.main()
