#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baixa elencos reais da football-data.org e gera dados_mundo.py.

Nao roda dentro do jogo: e ferramenta de quem mantem o jogo. O jogo so le o
dados_mundo.py gerado (embutido, como os elencos brasileiros), entao quem joga
nao precisa de internet nem de chave.

    python ferramentas/importar_elencos.py           usa o cache se existir
    python ferramentas/importar_elencos.py --baixar  busca tudo de novo

A chave vem de FOOTBALL_DATA_KEY (ambiente ou .env na pasta do jogo). O plano
gratis aceita 10 pedidos por minuto; o script espera entre um e outro.

O que a API da e nome, posicao, nascimento e clube. Nota ela nao da: o ovr sai
da reputacao do clube (pela classificacao da temporada anterior), da idade e
de uma variacao fixa por jogador. Craque que precisa de nota propria vai em
ferramentas/notas_manuais.json ({"Nome do Jogador": 91}).
"""

import base64
import datetime
import difflib
import hashlib
import json
import os
import sys
import time
import unicodedata
import urllib.request
import zlib

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
CACHE = os.path.join(AQUI, "cache")
SAIDA = os.path.join(RAIZ, "dados_mundo.py")
NOTAS = os.path.join(AQUI, "notas_manuais.json")
API = "https://api.football-data.org/v4"
TEMPORADA_ANTERIOR = 2025
HOJE = datetime.date(2026, 9, 24)

sys.path.insert(0, RAIZ)
import brasfut as eng  # noqa: E402

# codigo no jogo, codigo na API, nome, pais, reputacao do campeao e do lanterna
LIGAS = [
    ("ENG", "PL", "Premier League", "ENG", 97, 80),
    ("ESP", "PD", "La Liga", "ESP", 97, 76),
    ("GER", "BL1", "Bundesliga", "GER", 95, 76),
    ("ITA", "SA", "Serie A Italiana", "ITA", 94, 75),
    ("FRA", "FL1", "Ligue 1", "FRA", 93, 72),
]

# Brasil: so estes clubes sao sincronizados; o resto do embutido nao muda
BRASIL_SINCRONIZAR = ["Santos"]

POS_EXATA = {
    "Goalkeeper": "GOL", "Centre-Back": "ZAG", "Left-Back": "LAT", "Right-Back": "LAT",
    "Defensive Midfield": "VOL", "Central Midfield": "VOL", "Attacking Midfield": "MEI",
    "Left Midfield": "MEI", "Right Midfield": "MEI", "Left Winger": "ATA",
    "Right Winger": "ATA", "Centre-Forward": "ATA", "Offence": "ATA",
}


# ------------------------------------------------------------------ rede
def chave():
    k = os.environ.get("FOOTBALL_DATA_KEY")
    env = os.path.join(RAIZ, ".env")
    if not k and os.path.exists(env):
        for linha in open(env, encoding="utf-8"):
            if linha.startswith("FOOTBALL_DATA_KEY="):
                k = linha.split("=", 1)[1].strip()
    if not k:
        sys.exit("Falta FOOTBALL_DATA_KEY (ambiente ou .env na pasta do jogo).")
    return k


_ultimo = [0.0]


def pedir(caminho, baixar):
    arq = os.path.join(CACHE, caminho.strip("/").replace("/", "_").replace("?", "_") + ".json")
    if os.path.exists(arq) and not baixar:
        return json.load(open(arq, encoding="utf-8"))
    espera = 6.5 - (time.time() - _ultimo[0])
    if espera > 0:
        time.sleep(espera)
    req = urllib.request.Request(API + caminho, headers={"X-Auth-Token": chave()})
    with urllib.request.urlopen(req, timeout=30) as r:
        dados = json.load(r)
    _ultimo[0] = time.time()
    os.makedirs(CACHE, exist_ok=True)
    json.dump(dados, open(arq, "w", encoding="utf-8"))
    print("  baixado %s" % caminho)
    return dados


# ------------------------------------------------------------- conversao
def sem_acento(txt):
    txt = unicodedata.normalize("NFKD", txt or "")
    return "".join(ch for ch in txt if not unicodedata.combining(ch)).strip()


def chave_nome(txt):
    return " ".join(sem_acento(txt).lower().replace("-", " ").replace(".", " ").split())


# prefixos que a API poe e o jogo nao ("CA River Plate", "Club Bolivar")
PREFIXOS = {"ca", "cs", "cd", "club", "fc", "sc", "cf", "ac", "de", "football", "futbol"}
# nomes que nem sem prefixo batem
APELIDOS = {"cristal": "Sporting Cristal", "liverpool": "Liverpool Montevideo",
            "universidad catolica": "Universidad Catolica", "nacional": "Nacional"}


def chave_clube(txt):
    return " ".join(t for t in chave_nome(txt).split() if t not in PREFIXOS)


def idade(nasc):
    if not nasc:
        return None
    d = datetime.date.fromisoformat(nasc[:10])
    return HOJE.year - d.year - ((HOJE.month, HOJE.day) < (d.month, d.day))


def variacao(nome):
    """-5 a +5, sempre a mesma para o mesmo nome: o elenco tem destaque e
    reserva sem sorteio a cada importacao."""
    h = int(hashlib.md5(nome.encode("utf-8")).hexdigest()[:8], 16)
    return (h % 11) - 5


AJUSTE_IDADE = {17: -14, 18: -11, 19: -9, 20: -7, 21: -5, 22: -3, 23: -2, 31: -1,
                32: -2, 33: -3, 34: -4, 35: -6, 36: -8}


def nota(nome, anos, reputacao, manuais):
    if nome in manuais:
        ovr = int(manuais[nome])
    else:
        nivel = 26 + reputacao * 0.58
        ovr = round(nivel + AJUSTE_IDADE.get(anos, -10 if anos and anos > 36 else 0) + variacao(nome))
    ovr = max(40, min(95, ovr))
    folga = {17: 16, 18: 14, 19: 12, 20: 10, 21: 8, 22: 6, 23: 4, 24: 2}.get(anos, 0)
    return ovr, min(95, ovr + folga)


def converter_elenco(squad, reputacao, manuais, notas_antigas=None):
    """Lista da API -> lista do jogo. Posicao generica (Defence, Midfield) vira
    ZAG/LAT e VOL/MEI conforme o que falta para o elenco padrao."""
    fora = []
    gen = {"Defence": [], "Midfield": []}
    for p in squad:
        anos = idade(p.get("dateOfBirth"))
        if anos is None or anos < 16 or anos > 42:
            continue                      # cadastro quebrado (a API tem nascido em 2016)
        nome = sem_acento(p["name"])
        pos = POS_EXATA.get(p.get("position") or "")
        item = {"nome": nome, "idade": anos, "pos": pos}
        if pos is None:
            grupo = "Defence" if p.get("position") == "Defence" else "Midfield"
            gen[grupo].append(item)
        fora.append(item)
    conta = lambda pos: sum(1 for i in fora if i["pos"] == pos)
    for grupo, (a, b) in (("Defence", ("ZAG", "LAT")), ("Midfield", ("VOL", "MEI"))):
        for item in gen[grupo]:
            falta_a = eng.ELENCO_PADRAO[a] - conta(a)
            falta_b = eng.ELENCO_PADRAO[b] - conta(b)
            item["pos"] = a if falta_a >= falta_b else b
    antigas = {chave_nome(j["nome"]): j for j in (notas_antigas or [])}

    def achar_antigo(nome):
        k = chave_nome(nome)
        if k in antigas:
            return antigas[k]
        # "Neymar" x "Neymar Jr", "Rollheiser" x "Benjamin Rollheiser": um nome
        # contem o outro, e so vale se houver um candidato
        tk = set(k.split())
        pares = [v for kk, v in antigas.items() if tk <= set(kk.split()) or set(kk.split()) <= tk]
        return pares[0] if len(pares) == 1 else None

    for item in fora:
        velho = achar_antigo(item["nome"])
        if velho:
            # quem ja estava no jogo mantem a nota que tinha
            item["ovr"] = velho["ovr"]
            item["pot"] = velho.get("pot", max(velho["ovr"], item["ovr"] if "ovr" in item else 0))
            item["pos"] = velho.get("pos", item["pos"])
        else:
            item["ovr"], item["pot"] = nota(item["nome"], item["idade"], reputacao, manuais)
    return fora


def nome_clube(t):
    nome = t.get("shortName") or t["name"]
    return sem_acento(nome)


def capacidade(reputacao):
    return int(max(12000, min(85000, 20000 + (reputacao - 70) * 2400)))


# --------------------------------------------------------------- execucao
def main():
    baixar = "--baixar" in sys.argv
    manuais = json.load(open(NOTAS, encoding="utf-8")) if os.path.exists(NOTAS) else {}
    manuais = {k: v for k, v in manuais.items() if not k.startswith("_")}
    mundo = {"gerado": HOJE.isoformat(), "ligas": [], "sul": {}, "brasil": {}}

    for cod, api, nome_liga, pais, topo, fundo in LIGAS:
        times = pedir("/competitions/%s/teams" % api, baixar)["teams"]
        tabela = pedir("/competitions/%s/standings?season=%d" % (api, TEMPORADA_ANTERIOR), baixar)
        ordem = [linha["team"]["id"] for linha in tabela["standings"][0]["table"]]
        n = len(ordem)
        clubes = []
        for t in times:
            pos = ordem.index(t["id"]) if t["id"] in ordem else n + 1   # promovido
            rep = round(topo - (topo - fundo) * min(pos, n - 1) / max(1, n - 1))
            if t["id"] not in ordem:
                rep = fundo - 1
            elenco = converter_elenco(t.get("squad") or [], rep, manuais)
            clubes.append({"nome": nome_clube(t), "pais": pais,
                           "estadio": sem_acento(t.get("venue") or "Estadio %s" % nome_clube(t)),
                           "capacidade": capacidade(rep), "reputacao": rep, "elenco": elenco})
        mundo["ligas"].append({"codigo": cod, "nome": nome_liga, "clubes": clubes})
        print("%-18s %d clubes, %d jogadores" % (nome_liga, len(clubes), sum(len(c["elenco"]) for c in clubes)))

    # America do Sul: so clubes que ja existem no jogo, casados pelo nome
    ex = {chave_clube(d[0]): d for d in eng.CLUBES_LIB + eng.CLUBES_SUL}
    por_nome = {d[0]: d for d in eng.CLUBES_LIB + eng.CLUBES_SUL}
    brasileiros = {chave_clube(d[0]) for d in eng.CLUBES_A + eng.CLUBES_B + eng.CLUBES_C + eng.CLUBES_D}
    for t in pedir("/competitions/CLI/teams", baixar)["teams"]:
        candidatos = [chave_clube(t["name"]), chave_clube(t.get("shortName") or "")]
        achado = None
        for c in candidatos:
            if c in ex:
                achado = ex[c]
                break
            if c in APELIDOS and APELIDOS[c] in por_nome and t["area"]["name"] != "Brazil":
                achado = por_nome[APELIDOS[c]]
                break
        if not achado:
            perto = difflib.get_close_matches(candidatos[-1] or candidatos[0], list(ex), n=1, cutoff=0.8)
            achado = ex[perto[0]] if perto else None
        if not achado:
            if not any(c in brasileiros for c in candidatos):
                print("  sem par no jogo: %s" % t["name"])
            continue
        mundo["sul"][achado[0]] = converter_elenco(t.get("squad") or [], achado[4], manuais)
    print("America do Sul: %d clubes do jogo com elenco real" % len(mundo["sul"]))

    # Brasil: so os clubes pedidos, mantendo a nota de quem ja estava
    embutido = json.loads(zlib.decompress(base64.b64decode(eng.ELENCOS_EMBUTIDOS)).decode("utf-8"))
    reps = {d[0]: d[4] for d in eng.CLUBES_A + eng.CLUBES_B + eng.CLUBES_C + eng.CLUBES_D}
    for t in pedir("/competitions/BSA/teams", baixar)["teams"]:
        nome = nome_clube(t)
        alvo = next((b for b in BRASIL_SINCRONIZAR if chave_nome(b) == chave_nome(nome)), None)
        if alvo:
            mundo["brasil"][alvo] = converter_elenco(t["squad"], reps[alvo], manuais, embutido.get(alvo))
            print("%s: %d jogadores (antes %d)" % (alvo, len(mundo["brasil"][alvo]), len(embutido.get(alvo, []))))

    bruto = json.dumps(mundo, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    texto = base64.b64encode(zlib.compress(bruto, 9)).decode("ascii")
    linhas = [texto[i:i + 100] for i in range(0, len(texto), 100)]
    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write('# -*- coding: utf-8 -*-\n"""Gerado por ferramentas/importar_elencos.py em %s. Nao edite a mao:\n'
                'mude o script (ou notas_manuais.json) e gere de novo. Fonte: football-data.org."""\n\n'
                "MUNDO_EMBUTIDO = (\n" % HOJE.isoformat())
        for linha in linhas:
            f.write('    "%s"\n' % linha)
        f.write(")\n")
    print("gerado %s (%d KB)" % (os.path.relpath(SAIDA, RAIZ), os.path.getsize(SAIDA) // 1024))


if __name__ == "__main__":
    main()
