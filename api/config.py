# -*- coding: utf-8 -*-
"""Preferencias que valem para qualquer carreira, fora do save.

Ficam em brasfut_config.json, ao lado do save: trocar de carreira nao apaga a
escala da interface, e o que e da carreira (dificuldade, sem demissao,
investidor) continua no save, em G["opcoes"]. Aqui so moram os padroes que a
tela de carreira nova ja traz marcados.
"""

import json
import os

import brasfut as eng

PADRAO = {
    "escala": 100,              # zoom da interface, em %
    "reduzir_animacoes": False,
    "dificuldade": "normal",    # padroes da tela de carreira nova
    "sem_demissao": False,
    "investidor": False,
}
ESCALAS = (90, 100, 110, 125)


def _caminho():
    return os.path.join(os.path.dirname(eng.SAVE), "brasfut_config.json")


def ler():
    fora = dict(PADRAO)
    try:
        with open(_caminho(), encoding="utf-8") as f:
            fora.update(_limpo(json.load(f)))
    except (OSError, ValueError):
        pass
    return fora


def gravar(novo):
    fora = ler()
    fora.update(_limpo(novo))
    with open(_caminho(), "w", encoding="utf-8") as f:
        json.dump(fora, f, indent=2)
    return fora


def _limpo(d):
    """So as chaves conhecidas, com o tipo certo: o arquivo e editavel a mao."""
    fora = {}
    if not isinstance(d, dict):
        return fora
    if d.get("escala") in ESCALAS:
        fora["escala"] = d["escala"]
    if d.get("dificuldade") in eng.DIFICULDADES:
        fora["dificuldade"] = d["dificuldade"]
    for k in ("reduzir_animacoes", "sem_demissao", "investidor"):
        if k in d:
            fora[k] = bool(d[k])
    return fora
