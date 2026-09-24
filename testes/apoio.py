# -*- coding: utf-8 -*-
"""Chao comum dos testes: o motor apontado para uma copia do save.

Importe este modulo ANTES de `api`: a sessao le eng.SAVE, e o save de verdade
nunca pode ser tocado por teste. A API e chamada pelo mesmo `despachar` que o
server.py usa, sem HTTP no meio - o que se testa e a rota, nao a stdlib.
"""

import os
import shutil
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(RAIZ, "testes", "_tmp")
sys.path.insert(0, RAIZ)

import brasfut as eng  # noqa: E402

SAVE_REAL = eng.SAVE
SAVE_TESTE = os.path.join(TMP, "brasfut_save.json")
os.makedirs(TMP, exist_ok=True)
eng.SAVE = SAVE_TESTE

from api import rotas  # noqa: E402
from api.sessao import SESSAO  # noqa: E402


# Protecao do save real: qualquer tentativa de gravar nele, vinda de teste,
# falha na hora. (Comparar o hash do arquivo dava alarme falso com o jogo
# aberto, que grava a cada clique enquanto os testes rodam.)
_salvar_original = eng.salvar
TENTATIVAS_NO_REAL = []


def _salvar_protegido(G, caminho=None):
    alvo = os.path.abspath(caminho or eng.SAVE)
    if os.path.normcase(alvo) == os.path.normcase(os.path.abspath(SAVE_REAL)):
        TENTATIVAS_NO_REAL.append(alvo)
        raise AssertionError("teste tentou gravar no save real: %s" % alvo)
    return _salvar_original(G, caminho)


eng.salvar = _salvar_protegido


def hash_do_save_real():
    """Quantas vezes algum teste tentou gravar no save real (tem que ser zero).
    O nome ficou pelos testes antigos, que comparam o valor antes e depois."""
    return len(TENTATIVAS_NO_REAL)


def tem_save_real():
    return os.path.exists(SAVE_REAL)


def abrir_copia_do_save():
    """Copia o save real para _tmp e abre por /api/abrir."""
    shutil.copyfile(SAVE_REAL, SAVE_TESTE)
    return chamar("POST", "/api/abrir")


def chamar(metodo, caminho, corpo=None, status=200):
    """Chama a rota e confere o status; devolve o objeto da resposta."""
    obtido, obj = rotas.despachar(metodo, caminho, corpo)
    if obtido != status:
        raise AssertionError("%s %s -> %d (esperava %d): %s"
                             % (metodo, caminho, obtido, status, obj))
    return obj


def avancar(corpo=None):
    """Avanca uma semana confirmando qualquer aviso (time quebrado, estadual)."""
    r = chamar("POST", "/api/avancar", corpo)
    if "confirmar" in r:
        r = chamar("POST", "/api/avancar", dict(corpo or {}, confirmar=True))
    return r
