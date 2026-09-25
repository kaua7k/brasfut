# -*- coding: utf-8 -*-
"""Harness de desempenho: quanto custa uma semana e se a saida mudou.

Nao e teste da suite (nao comeca com test_): leva alguns minutos. Serve de
gate para mexida de desempenho no motor - memo, cache, atalho - que so vale se
o jogo continuar exatamente o mesmo.

    cd testes
    python desempenho.py --gravar antes.json     # na versao de referencia
    python desempenho.py --comparar antes.json   # depois da mudanca

Campo novo que so guarda (nao sorteia, nao muda jogo) mexe no hash do mundo
sem mudar o jogo. --ignorar tira do hash chaves do mundo e do jogador, e vale
nas duas pontas (rode a referencia com o mesmo --ignorar):

    python desempenho.py --gravar antes.json --ignorar historico_meus,nota_soma,nota_j

Para cada seed, mundo novo pelo mesmo caminho da tela (/api/novo, /api/clube)
e N semanas por /api/avancar. A cada semana guarda o sha256 do mundo inteiro
(json com chaves ordenadas) e do log: a comparacao e da saida completa, nao de
um resumo - memo com chave incompleta muda um jogo e passaria num hash
agregado. Tempo medido por semana, separando semana so de liga das semanas com
fase de liga da Champions/Europa League (as mais caras).
"""

import argparse
import hashlib
import json
import os
import statistics
import sys
import time

import apoio

eng = apoio.eng

SEEDS = (11, 23, 37)
SEMANAS = 20

# o motor sozinho (jogar_semana), sem a gravacao do save nem o DTO da resposta
_MOTOR = [0.0]
_jogar_semana = eng.jogar_semana


def _cronometrado(G):
    t0 = time.perf_counter()
    try:
        return _jogar_semana(G)
    finally:
        _MOTOR[0] += time.perf_counter() - t0


eng.jogar_semana = _cronometrado


def digest(obj):
    texto = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


IGNORAR = set()


def mundo_sem_ignorados(G):
    jogadores = {str(k): {c: v for c, v in j.items() if c not in IGNORAR}
                 for k, j in G["jogadores"].items()}
    mundo = {c: v for c, v in G.items() if c not in IGNORAR}
    return dict(mundo, clubes={str(k): v for k, v in G["clubes"].items()}, jogadores=jogadores)


def rodar(seed, semanas):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(seed)
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Harness"})["clubes"]
    apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "A"][0]["id"]})
    G = apoio.SESSAO.G
    fora = []
    for _ in range(semanas):
        semana = G["semana"]
        euro = G["fase"] == "liga" and semana in eng.SEMANAS_FASE_LIGA + eng.SEMANAS_EURO
        t0, m0 = time.perf_counter(), _MOTOR[0]
        r = apoio.avancar({"leve": True})
        dt = time.perf_counter() - t0
        fora.append({"semana": semana, "euro": euro, "tempo": dt, "motor": _MOTOR[0] - m0,
                     "mundo": digest(mundo_sem_ignorados(G)),
                     "log": digest(r.get("log", "")), "jogos": digest(r.get("jogos"))})
    return fora


def resumo_tempos(corridas):
    liga = [s["tempo"] for c in corridas for s in c if not s["euro"]]
    euro = [s["tempo"] for c in corridas for s in c if s["euro"]]
    return {"liga_media": statistics.mean(liga), "liga_max": max(liga),
            "euro_media": statistics.mean(euro) if euro else 0.0,
            "euro_max": max(euro) if euro else 0.0,
            "total": sum(liga) + sum(euro),
            "motor": sum(s.get("motor", 0.0) for c in corridas for s in c)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gravar")
    ap.add_argument("--comparar")
    ap.add_argument("--semanas", type=int, default=SEMANAS)
    ap.add_argument("--ignorar", default="", help="chaves fora do hash, separadas por virgula")
    a = ap.parse_args()
    IGNORAR.update(c for c in a.ignorar.split(",") if c)
    corridas = {str(s): rodar(s, a.semanas) for s in SEEDS}
    tempos = resumo_tempos(list(corridas.values()))
    print("semana de liga: media %.3f s, pior %.3f s" % (tempos["liga_media"], tempos["liga_max"]))
    print("semana com copa europeia: media %.3f s, pior %.3f s" % (tempos["euro_media"], tempos["euro_max"]))
    print("total: %.1f s (motor %.1f s, o resto e gravar o save e montar a resposta)"
          % (tempos["total"], tempos["motor"]))
    if a.gravar:
        with open(a.gravar, "w", encoding="utf-8") as f:
            json.dump({"corridas": corridas, "tempos": tempos}, f)
    if a.comparar:
        with open(a.comparar, encoding="utf-8") as f:
            ref = json.load(f)
        diferentes = []
        for seed, semanas in corridas.items():
            for i, (x, y) in enumerate(zip(ref["corridas"][seed], semanas)):
                for campo in ("mundo", "log", "jogos"):
                    if x[campo] != y[campo]:
                        diferentes.append("seed %s, semana %d: %s mudou" % (seed, i + 1, campo))
        for rotulo, chave in (("pedido inteiro", "total"), ("motor", "motor")):
            antes = ref["tempos"].get(chave)
            if antes:
                print("%s: antes %.1f s, agora %.1f s (%+.1f%%)"
                      % (rotulo, antes, tempos[chave], 100.0 * (tempos[chave] - antes) / antes))
        if diferentes:
            print("SAIDA DIFERENTE:")
            for d in diferentes[:20]:
                print("  " + d)
            sys.exit(1)
        print("saida identica em %d seeds x %d semanas" % (len(SEEDS), a.semanas))


if __name__ == "__main__":
    main()
