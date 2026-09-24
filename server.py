#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BRASFUT no navegador: o motor de sempre servido por HTTP.

Roda com a biblioteca padrao do Python, sem pip install nenhum - a mesma
promessa do resto do jogo, e o que deixa o build-windows.bat continuar
empacotando tudo num .exe so.

Ouve apenas em 127.0.0.1: e um jogo de uma pessoa na propria maquina, nao um
servidor. Nao ha login nem sessao por usuario de proposito.

    python server.py            abre o navegador sozinho
    python server.py --sem-abrir    so sobe o servidor
"""

import os
import posixpath
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from api import rotas
import brasfut as eng

WEB = os.path.join(BASE, "web", "dist")
PORTA = int(os.environ.get("BRASFUT_PORTA", "8770"))

TIPOS = {
    ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
    ".ico": "image/x-icon", ".woff2": "font/woff2", ".woff": "font/woff",
    ".ttf": "font/ttf", ".map": "application/json",
}

SEM_BUILD = """<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<title>BRASFUT - falta compilar a interface</title>
<body style="background:#0b0c0e;color:#f2f2f0;font:16px/1.6 system-ui;padding:60px">
<h1 style="font-size:22px">A interface ainda nao foi compilada</h1>
<p>O servidor esta no ar, mas nao existe <code>web/dist</code>.</p>
<pre style="background:#141518;border:1px solid #232428;border-radius:12px;padding:16px">cd web
npm install
npm run build</pre>
<p style="color:#87888d">Depois disso, recarregue esta pagina.</p>
</body></html>"""


class Manipulador(BaseHTTPRequestHandler):
    server_version = "BRASFUT"

    # o log padrao escreve uma linha por arquivo servido e afoga o console
    def log_message(self, formato, *args):
        if self.path.startswith("/api/"):
            sys.stderr.write("  %s %s\n" % (self.command, self.path))

    # ------------------------------------------------------------------ envio
    def _responde(self, status, corpo, tipo="application/json; charset=utf-8"):
        if isinstance(corpo, str):
            corpo = corpo.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        # o estado muda a cada semana: cache aqui mostraria a rodada passada
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(corpo)
        except (BrokenPipeError, ConnectionAbortedError):
            pass  # aba fechada no meio da resposta

    def _api(self, metodo):
        tamanho = int(self.headers.get("Content-Length") or 0)
        corpo = None
        if tamanho:
            import json
            try:
                corpo = json.loads(self.rfile.read(tamanho).decode("utf-8"))
            except ValueError:
                return self._responde(400, rotas.json_bytes({"erro": "json invalido"}))
        status, obj = rotas.despachar(metodo, self.path.split("?")[0], corpo)
        self._responde(status, rotas.json_bytes(obj))

    # ---------------------------------------------------------------- estatico
    def _arquivo(self):
        caminho = self.path.split("?")[0]
        rel = posixpath.normpath(caminho).lstrip("/")
        alvo = os.path.join(WEB, *rel.split("/")) if rel else os.path.join(WEB, "index.html")
        # o React cuida das rotas: o que nao for arquivo cai no index
        if not os.path.isfile(alvo):
            alvo = os.path.join(WEB, "index.html")
        if not os.path.isfile(alvo):
            return self._responde(200, SEM_BUILD, "text/html; charset=utf-8")
        # ninguem le fora de web/dist, mesmo com ../ na URL
        if not os.path.abspath(alvo).startswith(os.path.abspath(WEB)):
            return self._responde(403, b"")
        with open(alvo, "rb") as f:
            dados = f.read()
        tipo = TIPOS.get(os.path.splitext(alvo)[1].lower(), "application/octet-stream")
        self._responde(200, dados, tipo)

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self._api("GET")
        self._arquivo()

    def do_POST(self):
        if self.path.startswith("/api/"):
            return self._api("POST")
        self._responde(404, rotas.json_bytes({"erro": "rota inexistente"}))


def _ja_no_ar(url):
    """Tem um servidor do BRASFUT respondendo nesta porta?"""
    import json
    import urllib.request
    try:
        with urllib.request.urlopen(url + "api/estado", timeout=2) as r:
            return "jogo" in json.load(r)
    except Exception:
        return False


def main():
    if not eng.travar_save():
        # o jogo ja esta rodando no navegador (fechar a aba nao fecha o servidor):
        # abre a mesma pagina em vez de recusar
        url = "http://127.0.0.1:%d/" % PORTA
        if _ja_no_ar(url):
            print("O BRASFUT ja esta aberto: abrindo o navegador nele (%s)." % url)
            webbrowser.open(url)
            return
        # sai com erro: o iniciar-web.bat pausa e a mensagem fica na tela
        print(eng.AVISO_TRAVA)
        sys.exit(1)
    servidor =ThreadingHTTPServer(("127.0.0.1", PORTA), Manipulador)
    url = "http://127.0.0.1:%d/" % PORTA
    print("BRASFUT %s no ar em %s" % (eng.VERSAO, url))
    print("save: %s" % eng.SAVE)
    if not os.path.isdir(WEB):
        print("aviso: web/dist nao existe - rode 'npm install && npm run build' em web/")
    print("feche esta janela para encerrar o jogo.")
    if "--sem-abrir" not in sys.argv:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nencerrando.")
        servidor.shutdown()


if __name__ == "__main__":
    main()
