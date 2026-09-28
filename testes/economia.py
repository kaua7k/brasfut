# -*- coding: utf-8 -*-
"""Suite lenta de economia: o caixa dos clubes da IA aguenta varias temporadas?

Nao e teste da suite (nao comeca com test_): leva ~40 s por temporada. Serve de
gate para mexida em receita, custo, salario ou contratacao da IA - foi ela que
achou as "contratacoes fantasmas" (craque europeu caindo na Serie D e a divisao
inteira no vermelho em cinco anos) e mediu o patrocinio novo.

    cd testes
    python economia.py                        # 12 temporadas, seed 77
    python economia.py --anos 6 --seed 5
    python economia.py --gravar antes.json    # na versao de referencia
    python economia.py --comparar antes.json

Por temporada e por liga: caixa mediano, clubes no vermelho, e receita, folha e
estrutura semanais medianas. Usa um save proprio em testes/_tmp, entao pode
rodar ao lado da suite.
"""

import argparse
import json
import os
import statistics as st
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
os.chdir(AQUI)
import apoio  # noqa: E402

eng = apoio.eng
apoio.SAVE_TESTE = os.path.join(apoio.TMP, "economia_save.json")
eng.SAVE = apoio.SAVE_TESTE

LIGAS = ["A", "B", "C", "D", "ENG", "ESP", "POR", "USA", "ARG", "COL", "BOL"]


def foto(G):
    out = {"t": int(G["temporada"])}
    for d in LIGAS:
        cs = [c for c in G["clubes"].values() if c["divisao"] == d and c["id"] != G["clube"]]
        if not cs:
            continue
        cx = [c["dinheiro"] for c in cs]
        out[d] = {"caixa": int(st.median(cx)), "negativos": sum(1 for x in cx if x < 0), "n": len(cs),
                  "receita": int(st.median(eng.receita_semanal(G, c) for c in cs)),
                  "folha": int(st.median(eng.folha_semanal(G, c) for c in cs)),
                  "estrutura": int(st.median(eng.custo_estrutura(c) for c in cs))}
    return out


def rodar(anos, seed):
    if os.path.exists(apoio.SAVE_TESTE):
        os.remove(apoio.SAVE_TESTE)
    eng.rng.seed(seed)
    clubes = apoio.chamar("POST", "/api/novo", {"nome": "Economia", "opcoes": {"sem_demissao": True}})["clubes"]
    apoio.chamar("POST", "/api/clube", {"id": [c for c in clubes if c["divisao"] == "B"][3]["id"]})
    G = apoio.SESSAO.G
    fotos = [foto(G)]
    t0 = time.time()
    for _ in range(anos):
        for _ in range(90):
            if eng.temporada_encerrada(G):
                break
            apoio.avancar({"leve": True})
        apoio.avancar()
        apoio.SESSAO.pendencia = None
        fotos.append(foto(G))
        print("  temporada %d fechada (%.0f s)" % (G["temporada"] - 1, time.time() - t0), flush=True)
    return fotos


def tabela(fotos, titulo):
    print("\n%s: caixa mediano em mi / clubes no vermelho" % titulo)
    print("liga  " + " ".join("%9d" % f["t"] for f in fotos))
    for d in LIGAS:
        if d in fotos[0]:
            print("%-5s " % d + " ".join("%5.1f/%-3d" % (f[d]["caixa"] / 1e6, f[d]["negativos"])
                                         if d in f else "%9s" % "-" for f in fotos))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--anos", type=int, default=12)
    p.add_argument("--seed", type=int, default=77)
    p.add_argument("--gravar")
    p.add_argument("--comparar")
    a = p.parse_args()
    fotos = rodar(a.anos, a.seed)
    tabela(fotos, "agora")
    if a.gravar:
        with open(a.gravar, "w", encoding="utf-8") as f:
            json.dump(fotos, f)
        print("\ngravado em %s" % a.gravar)
    if a.comparar:
        with open(a.comparar, encoding="utf-8") as f:
            tabela(json.load(f), "antes")


if __name__ == "__main__":
    main()
