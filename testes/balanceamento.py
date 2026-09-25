# -*- coding: utf-8 -*-
"""Suite lenta de balanceamento: o jogo continua com cara de futebol?

Nao e teste da suite (nao comeca com test_): leva minutos. Serve de gate para
mexida que muda resultado de proposito (tatica, forca, IA) - a saida muda, o
que tem que ficar no lugar e a distribuicao.

    cd testes
    python balanceamento.py                      # 3 seeds x 45 semanas
    python balanceamento.py --gravar antes.json  # na versao de referencia
    python balanceamento.py --comparar antes.json

Mundo novo por seed pelo caminho da tela e N semanas por /api/avancar. Toda
partida simulada entra na conta (todas as ligas e copas). Faixas da ata de
2026-09-24: gols por jogo entre 2,4 e 2,9.
"""

import argparse
import json
import os
import statistics

import apoio

eng = apoio.eng

SEEDS = (11, 23, 37)
SEMANAS = 45
FAIXA_GOLS = (2.4, 2.9)

_JOGOS = []
_simular = eng.simular


def _anotado(G, casa_id, fora_id, comp="liga", neutro=False):
    r = _simular(G, casa_id, fora_id, comp, neutro)
    ate70 = [0, 0]
    for minuto, lado, tipo, _pid, _extra in r["eventos"]:
        if tipo == "gol" and minuto <= 70:
            ate70[lado] += 1
    _JOGOS.append((r["gc"], r["gf"], ate70[0], ate70[1], len(r.get("instrucoes", []))))
    return r


eng.simular = _anotado


def rodar(seed, semanas):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(seed)
    # sem demissao: 45 semanas passam da virada, e tecnico demitido trava o laco
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Balanco",
                                                "opcoes": {"sem_demissao": True}})["clubes"]
    apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
    for _ in range(semanas):
        apoio.chamar("POST", "/api/avancar", {"leve": True, "confirmar": True})
    G = apoio.SESSAO.G
    return sum(1 for j in G["jogadores"].values() if j.get("clube") is not None and j["ovr"] >= 85)


def medir(jogos):
    n = len(jogos)
    gols = [a + b for a, b, *_ in jogos]
    casa = sum(1 for a, b, *_ in jogos if a > b)
    empate = sum(1 for a, b, *_ in jogos if a == b)
    # quem perdia aos 70 e nao perdeu no fim
    perdiam = [(a, b, x, y) for a, b, x, y, _ in jogos if x != y]
    viradas = sum(1 for a, b, x, y in perdiam if (x < y and a >= b) or (x > y and a <= b))
    com_troca = sum(1 for *_, t in jogos if t)
    return {"jogos": n, "gols_por_jogo": statistics.mean(gols),
            "casa": casa / n, "empate": empate / n, "fora": (n - casa - empate) / n,
            "reacao_depois_dos_70": viradas / max(1, len(perdiam)),
            "jogos_com_troca": com_troca / n}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gravar")
    ap.add_argument("--comparar")
    ap.add_argument("--semanas", type=int, default=SEMANAS)
    a = ap.parse_args()
    craques = [rodar(s, a.semanas) for s in SEEDS]
    m = medir(_JOGOS)
    m["jogadores_85_mais"] = statistics.mean(craques)
    for k, v in m.items():
        print("%-22s %s" % (k, ("%.3f" % v) if isinstance(v, float) else v))
    fora_da_faixa = not (FAIXA_GOLS[0] <= m["gols_por_jogo"] <= FAIXA_GOLS[1])
    if fora_da_faixa:
        print("GOLS FORA DA FAIXA %.1f-%.1f" % FAIXA_GOLS)
    if a.gravar:
        with open(a.gravar, "w", encoding="utf-8") as f:
            json.dump(m, f)
    if a.comparar:
        with open(a.comparar, encoding="utf-8") as f:
            ref = json.load(f)
        print("\n%-22s %10s %10s" % ("", "antes", "agora"))
        for k in m:
            if k in ref and isinstance(m[k], float):
                print("%-22s %10.3f %10.3f" % (k, ref[k], m[k]))
    if fora_da_faixa:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
