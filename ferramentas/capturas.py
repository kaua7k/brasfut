"""Capturas das telas web em varias resolucoes, e a comparacao entre duas levas.

Sobe uma copia isolada do jogo (motor, api, web/dist e uma copia do save) numa
pasta temporaria e numa porta propria, e fotografa cada tela com o Edge
headless. Nada toca o save de verdade nem o servidor que estiver aberto.

    python ferramentas/capturas.py tirar  <pasta>            # 13 telas x 5 resolucoes
    python ferramentas/capturas.py tirar  <pasta> --telas painel,elenco --res 1280x720
    python ferramentas/capturas.py tirar  <pasta> --avancar 6  # joga 6 semanas na copia antes
    python ferramentas/capturas.py comparar <antes> <depois>  # % de pixels diferentes

So stdlib: o PNG do Edge e lido com zlib (8 bits, RGB/RGBA, sem entrelacamento).
"""

import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request
import zlib

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TELAS = ["painel", "elenco", "base", "treino", "escalacao", "tabela", "copas",
         "mercado", "financas", "estadio", "infra", "noticias", "carreira"]
RESOLUCOES = ["1280x720", "1366x768", "1440x900", "1920x1080", "2560x1440"]
PORTA = 8791
EDGE = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]


def _edge():
    for caminho in EDGE:
        if os.path.exists(caminho):
            return caminho
    sys.exit("Edge nao encontrado em %s" % " nem ".join(EDGE))


def _copia_isolada():
    pasta = tempfile.mkdtemp(prefix="brasfut-cap-")
    for nome in ("brasfut.py", "dados_mundo.py", "server.py", "brasfut_save.json"):
        origem = os.path.join(RAIZ, nome)
        if os.path.exists(origem):
            shutil.copy2(origem, pasta)
    shutil.copytree(os.path.join(RAIZ, "api"), os.path.join(pasta, "api"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(os.path.join(RAIZ, "web", "dist"), os.path.join(pasta, "web", "dist"))
    return pasta


def _esperar_servidor(url, limite=30.0):
    fim = time.time() + limite
    while time.time() < fim:
        try:
            urllib.request.urlopen(url + "api/estado", timeout=2).read()
            return
        except Exception:
            time.sleep(0.3)
    sys.exit("o servidor da copia nao subiu em %.0fs" % limite)


def _post(url, caminho, corpo):
    pedido = urllib.request.Request(url + caminho, data=json.dumps(corpo).encode("utf-8"),
                                    method="POST", headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(pedido, timeout=300).read() or b"{}")


def tirar(destino, telas, resolucoes, avancar=0):
    os.makedirs(destino, exist_ok=True)
    edge = _edge()
    pasta = _copia_isolada()
    env = dict(os.environ, BRASFUT_PORTA=str(PORTA))
    servidor = subprocess.Popen([sys.executable, "server.py", "--sem-abrir"], cwd=pasta, env=env,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = "http://127.0.0.1:%d/" % PORTA
    try:
        _esperar_servidor(url)
        # sem isto toda captura para no menu principal: abrir e decisao do usuario
        _post(url, "api/abrir", {})
        # a copia joga semanas antes da foto (cartao da partida, historico...);
        # confirmar pula aviso de virada e de time quebrado
        for _ in range(avancar):
            r = _post(url, "api/avancar", {"confirmar": True, "leve": True})
            if r.get("pendencia"):
                break
        for res in resolucoes:
            w, h = res.split("x")
            for tela in telas:
                arquivo = os.path.abspath(os.path.join(destino, "%s-%s.png" % (tela, res)))
                perfil = tempfile.mkdtemp(prefix="brasfut-edge-")
                # --timeout corta a espera quando a pagina nunca fica ociosa (a
                # Escalacao tem animacao infinita e segurava o Edge para sempre)
                try:
                    subprocess.run([edge, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                                    "--user-data-dir=" + perfil, "--window-size=%s,%s" % (w, h),
                                    "--virtual-time-budget=6000", "--timeout=8000",
                                    "--screenshot=" + arquivo, url + "#" + tela],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
                except subprocess.TimeoutExpired:
                    pass
                # o Edge escreve o arquivo um pouco depois de sair
                for _ in range(50):
                    if os.path.exists(arquivo):
                        break
                    time.sleep(0.1)
                shutil.rmtree(perfil, ignore_errors=True)
                print("%-10s %-9s %s" % (tela, res, "ok" if os.path.exists(arquivo) else "FALHOU"))
    finally:
        servidor.terminate()
        servidor.wait(timeout=10)
        shutil.rmtree(pasta, ignore_errors=True)


def ler_png(caminho):
    """(largura, altura, bytes por pixel, linhas desfiltradas)."""
    with open(caminho, "rb") as f:
        dados = f.read()
    if dados[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("nao e PNG: %s" % caminho)
    pos, idat = 8, []
    largura = altura = bpp = 0
    while pos < len(dados):
        n, tipo = struct.unpack(">I4s", dados[pos:pos + 8])
        corpo = dados[pos + 8:pos + 8 + n]
        if tipo == b"IHDR":
            largura, altura, prof, cor, _, _, entrelacado = struct.unpack(">IIBBBBB", corpo)
            if prof != 8 or cor not in (2, 6) or entrelacado:
                raise ValueError("PNG fora do formato do Edge: %s" % caminho)
            bpp = 3 if cor == 2 else 4
        elif tipo == b"IDAT":
            idat.append(corpo)
        pos += 12 + n
    cru = zlib.decompress(b"".join(idat))
    passo = largura * bpp
    linhas, anterior = [], bytearray(passo)
    for y in range(altura):
        ini = y * (passo + 1)
        filtro, linha = cru[ini], bytearray(cru[ini + 1:ini + 1 + passo])
        for x in range(passo):
            a = linha[x - bpp] if x >= bpp else 0
            b = anterior[x]
            c = anterior[x - bpp] if x >= bpp else 0
            if filtro == 1:
                linha[x] = (linha[x] + a) & 255
            elif filtro == 2:
                linha[x] = (linha[x] + b) & 255
            elif filtro == 3:
                linha[x] = (linha[x] + (a + b) // 2) & 255
            elif filtro == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                linha[x] = (linha[x] + pred) & 255
        linhas.append(bytes(linha))
        anterior = linha
    return largura, altura, bpp, linhas


def diferenca(a, b):
    """Fracao de pixels diferentes (1.0 se o tamanho mudou)."""
    la, aa, bpa, pa = ler_png(a)
    lb, ab, bpb, pb = ler_png(b)
    if (la, aa) != (lb, ab):
        return 1.0
    diferentes = 0
    for ya, yb in zip(pa, pb):
        if ya == yb:
            continue
        for x in range(la):
            if ya[x * bpa:x * bpa + 3] != yb[x * bpb:x * bpb + 3]:
                diferentes += 1
    return diferentes / float(la * aa)


def comparar(antes, depois):
    nomes = sorted(n for n in os.listdir(antes) if n.endswith(".png"))
    for nome in nomes:
        outro = os.path.join(depois, nome)
        if not os.path.exists(outro):
            print("%-28s sem par" % nome)
            continue
        d = diferenca(os.path.join(antes, nome), outro)
        print("%-28s %6.2f%%" % (nome, d * 100))


def main(args):
    if len(args) >= 2 and args[0] == "tirar":
        telas, res = TELAS, RESOLUCOES
        if "--telas" in args:
            telas = args[args.index("--telas") + 1].split(",")
        if "--res" in args:
            res = args[args.index("--res") + 1].split(",")
        avancar = int(args[args.index("--avancar") + 1]) if "--avancar" in args else 0
        tirar(args[1], telas, res, avancar)
    elif len(args) == 3 and args[0] == "comparar":
        comparar(args[1], args[2])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
