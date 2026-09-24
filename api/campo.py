# -*- coding: utf-8 -*-
"""Onde cada titular fica desenhado no campo.

O motor nao guarda coordenada: ele guarda a vaga (GOL, ZAG, LAT, VOL, MEI,
ATA). Quem transforma vaga em ponto e esta tabela, e ela vale para as seis
formacoes do jogo - por isso as faixas sao calculadas, e nao onze pares de
numeros escritos a mao que so serviriam para o 4-3-3.

Eixos em porcentagem do campo: x=0 e a nossa linha de fundo, x=100 a do
adversario; y=0 e a lateral de cima.
"""

# x de cada linha e a faixa de y que ela pode ocupar
LINHAS = {
    "GOL": (7, (50, 50)),
    "ZAG": (20, (30, 70)),
    "LAT": (25, (16, 84)),
    "VOL": (41, (26, 74)),
    "MEI": (58, (22, 78)),
    "ATA": (79, (18, 82)),
}
ORDEM = ["GOL", "ZAG", "LAT", "VOL", "MEI", "ATA"]


def _espalhar(n, faixa):
    """n pontos distribuidos na faixa. Um jogador so fica no meio dela."""
    lo, hi = faixa
    if n <= 1:
        return [(lo + hi) / 2.0]
    passo = (hi - lo) / float(n - 1)
    return [lo + passo * i for i in range(n)]


def posicionar(vagas):
    """[(pid, vaga)] -> {pid: {"x","y","ordem"}}, numerado de GOL para ATA.

    O lateral e desenhado nas pontas e o zagueiro no miolo mesmo quando as
    duas linhas tem o mesmo x: e o que faz uma defesa de quatro parecer uma
    defesa de quatro.
    """
    por_vaga = {}
    for pid, vaga in vagas:
        por_vaga.setdefault(vaga, []).append(pid)

    fora = {}
    for vaga, pids in por_vaga.items():
        x, faixa = LINHAS.get(vaga, (50, (20, 80)))
        for pid, y in zip(pids, _espalhar(len(pids), faixa)):
            fora[pid] = {"x": x, "y": round(y, 1)}

    numero = 0
    for vaga in ORDEM:
        for pid in por_vaga.get(vaga, []):
            numero += 1
            fora[pid]["ordem"] = numero
    for pid in fora:
        fora[pid].setdefault("ordem", 0)
    return fora
