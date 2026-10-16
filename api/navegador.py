# -*- coding: utf-8 -*-
"""Modo navegador: as mesmas rotas, sem servidor nenhum.

Na versao do celular (GitHub Pages) o Python roda dentro do navegador, no
Pyodide, num Web Worker. Nao existe HTTP: o front manda (metodo, caminho,
corpo) por mensagem ao worker, e o worker chama `pedido` daqui, que entra no
mesmo `rotas.despachar` que o server.py usa. Nenhuma regra nova: o que muda e
so o transporte e onde o save mora.

O save fica numa pasta do sistema de arquivos virtual do Pyodide montada sobre
o IndexedDB do navegador (IDBFS). `pedido` conta se algum arquivo dessa pasta
mudou; quando mudou, o worker sincroniza com o IndexedDB.

`medir` e o protocolo do prototipo: uma carreira de teste numa pasta
temporaria, sem tocar no save nem na carreira aberta, e o tempo de cada semana.
Roda igual fora do navegador (o teste da suite usa o Python de sempre).
"""

import gc
import json
import os
import shutil
import tempfile
import time

import brasfut as eng

from . import rotas
from .sessao import SESSAO

PASTA = None


def iniciar(pasta):
    """Aponta o save (e o brasfut_config.json, que mora ao lado) para a pasta
    persistente. Chamado uma vez, antes do primeiro pedido."""
    global PASTA
    os.makedirs(pasta, exist_ok=True)
    PASTA = pasta
    eng.SAVE = os.path.join(pasta, "brasfut_save.json")
    # a sessao guarda a base dos slots na primeira leitura: comeca do zero
    SESSAO._save_base = None
    return eng.SAVE


def _retrato():
    """mtime e tamanho de cada arquivo da pasta do save: o que mudou precisa
    ir para o IndexedDB, o resto nao."""
    if not PASTA or not os.path.isdir(PASTA):
        return {}
    fora = {}
    for nome in os.listdir(PASTA):
        try:
            st = os.stat(os.path.join(PASTA, nome))
        except OSError:
            continue
        fora[nome] = (st.st_mtime, st.st_size)
    return fora


def pedido(metodo, caminho, corpo_json=None):
    """Um pedido da tela. Devolve JSON: {status, corpo, gravou}."""
    antes = _retrato()
    corpo = None
    if corpo_json:
        try:
            corpo = json.loads(corpo_json)
        except ValueError:
            return json.dumps({"status": 400, "corpo": {"erro": "json invalido"}, "gravou": False})
    status, obj = rotas.despachar(metodo, (caminho or "").split("?")[0], corpo)
    gravou = _retrato() != antes
    return json.dumps({"status": status, "corpo": obj, "gravou": gravou}, ensure_ascii=False)


# ---------------------------------------------------------------- medicao
def _resumo(valores):
    if not valores:
        return {"media": 0.0, "pior": 0.0, "melhor": 0.0}
    return {"media": sum(valores) / len(valores), "pior": max(valores), "melhor": min(valores)}


def _chamar(metodo, caminho, corpo=None):
    status, obj = rotas.despachar(metodo, caminho, corpo)
    if status != 200:
        raise RuntimeError("%s %s -> %d: %s" % (metodo, caminho, status, obj))
    return obj


def medir(semanas=10, divisao="A"):
    """Carreira de teste do zero e `semanas` cliques de Avancar semana, cada um
    pelo mesmo caminho da tela (POST /api/avancar com o Painel de volta).

    A carreira aberta e o save do jogador ficam intactos: a sessao inteira e
    guardada antes e devolvida depois, e o save de teste vai para uma pasta
    temporaria que e apagada no fim. Devolve os tempos em segundos.
    """
    semanas = max(1, min(int(semanas), 38))
    guardada = dict(SESSAO.__dict__)
    save_antes = eng.SAVE
    hook_antes = eng.trocar_de_clube
    jogar_antes, salvar_antes = eng.jogar_semana, eng.salvar
    pasta = tempfile.mkdtemp(prefix="brasfut-medicao-")
    relogio = {"motor": 0.0, "gravar": 0.0}

    def jogar_cronometrado(G):
        t0 = time.perf_counter()
        try:
            return jogar_antes(G)
        finally:
            relogio["motor"] += time.perf_counter() - t0

    def salvar_cronometrado(G, caminho=None):
        t0 = time.perf_counter()
        try:
            return salvar_antes(G, caminho)
        finally:
            relogio["gravar"] += time.perf_counter() - t0

    fora = {"semanas": [], "divisao": divisao}
    try:
        SESSAO.__dict__.clear()
        SESSAO.__init__()
        SESSAO._save_base = os.path.join(pasta, "brasfut_save.json")
        eng.SAVE = SESSAO._save_base
        eng.jogar_semana, eng.salvar = jogar_cronometrado, salvar_cronometrado

        t0 = time.perf_counter()
        # sem demissao: a medida e de tempo, uma demissao travaria a corrida
        clubes = _chamar("POST", "/api/novo", {"nome": "Medicao", "opcoes": {"sem_demissao": True}})["clubes"]
        fora["criar_mundo"] = time.perf_counter() - t0

        escolhido = [c for c in clubes if c["divisao"] == divisao] or clubes
        t0 = time.perf_counter()
        _chamar("POST", "/api/clube", {"id": escolhido[0]["id"]})
        fora["escolher_clube"] = time.perf_counter() - t0
        fora["clube"] = escolhido[0]["nome"]
        fora["tamanho_save"] = os.path.getsize(eng.SAVE) if os.path.exists(eng.SAVE) else 0

        for _ in range(semanas):
            G = SESSAO.G
            semana, fase = G["semana"], G["fase"]
            relogio["motor"] = relogio["gravar"] = 0.0
            t0 = time.perf_counter()
            r = _chamar("POST", "/api/avancar", {})
            if "confirmar" in r:
                r = _chamar("POST", "/api/avancar", {"confirmar": True})
            total = time.perf_counter() - t0
            fora["semanas"].append({"semana": semana, "fase": fase, "total": total,
                                    "motor": relogio["motor"], "gravar": relogio["gravar"]})
            if r.get("encerrada") or SESSAO.pendencia:
                break

        t0 = time.perf_counter()
        eng.carregar(eng.SAVE)
        fora["carregar_save"] = time.perf_counter() - t0
    finally:
        eng.jogar_semana, eng.salvar = jogar_antes, salvar_antes
        SESSAO.__dict__.clear()
        SESSAO.__dict__.update(guardada)
        eng.SAVE = save_antes
        eng.trocar_de_clube = hook_antes
        shutil.rmtree(pasta, ignore_errors=True)
        gc.collect()

    fora["semana"] = _resumo([s["total"] for s in fora["semanas"]])
    fora["motor"] = _resumo([s["motor"] for s in fora["semanas"]])
    fora["gravar"] = _resumo([s["gravar"] for s in fora["semanas"]])
    return fora


def medir_json(semanas=10, divisao="A"):
    return json.dumps(medir(semanas, divisao))
