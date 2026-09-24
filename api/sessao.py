# -*- coding: utf-8 -*-
"""O mundo do jogo vivo dentro do servidor.

Uma partida local, um tecnico, uma sessao: por isso o estado mora num objeto
de modulo e nao num registro de sessoes por usuario. O servidor e multi-thread
(o navegador abre varias conexoes), entao todo caminho que le ou escreve G
passa pelo mesmo cadeado - duas requisicoes avancando a semana ao mesmo tempo
jogariam a rodada duas vezes.
"""

import contextlib
import io
import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import brasfut as eng

# na web a semana 38 encerra a temporada e para: a virada so acontece quando o
# usuario clica em "Comecar o ano", depois de ver como o ano terminou
eng.VIRADA_MANUAL = True
# a rota de avancar grava depois da semana: o motor nao precisa gravar tambem
eng.SALVAR_NA_SEMANA = False


def capturar(func, *a, **kw):
    """Roda uma funcao do motor e devolve (retorno, texto impresso).

    O motor conversa por print: ele foi escrito para o terminal. Em vez de
    reescrever o motor, a API le o que ele imprimiu e devolve como log.
    """
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ret = func(*a, **kw)
    return ret, buf.getvalue()


class SemJogo(Exception):
    """Pediram uma tela antes de existir mundo carregado."""


class Sessao(object):
    def __init__(self):
        self.cadeado = threading.RLock()
        self.G = None
        self._diag = None
        self.log = []          # o que o motor imprimiu, do mais antigo ao novo
        self.pendencia = None  # decisao que trava o jogo (ex.: clube novo)
        # retrato do esquema antes da ultima troca de formacao: o Desfazer volta
        # a ele. Vale ate a proxima mexida no time, nao mais que isso.
        self.desfazer_esquema = None
        self.nova_vaga = []    # quem mudou de vaga na ultima troca de formacao
        # mesas de negociacao da semana: tentativas gastas e o que foi dito
        self.mesas = {}

    # ------------------------------------------------------------------ estado
    def exigir(self):
        if self.G is None:
            raise SemJogo("nenhum jogo carregado")
        return self.G

    @property
    def clube(self):
        G = self.exigir()
        return G["clubes"][G["clube"]]

    def diagnostico(self, recarregar=False):
        """O veredito da semana, calculado uma vez e distribuido pela tela.

        Mesma regra da janela tkinter: cinco pontos da interface discordando
        entre si e pior do que nenhum aviso.
        """
        G = self.exigir()
        if recarregar or self._diag is None:
            self._diag = eng.diagnostico_escalacao(G)
        return self._diag

    def invalidar(self):
        self._diag = None

    def esquecer_desfazer(self):
        self.desfazer_esquema = None
        self.nova_vaga = []

    def anotar(self, texto):
        if texto and texto.strip():
            self.log = (self.log + [texto.strip()])[-40:]

    # ------------------------------------------------------------------ inicio
    def tem_save(self):
        return os.path.exists(eng.SAVE)

    def carregar(self):
        G = eng.carregar()
        self._adotar(G)
        return G

    def mundo_novo(self, nome="Tecnico", opcoes=None):
        """Cria o mundo mas ainda sem clube: quem escolhe e a tela."""
        nome = " ".join(str(nome or "").split())[:40] or "Tecnico"
        G, texto = capturar(eng.criar_mundo, nome)
        eng.definir_opcoes_carreira(G, opcoes or {})
        self.anotar(texto)
        self._pendente_novo = G
        return G

    def escolher_clube(self, cid):
        """Clube do mundo novo ou, depois de uma demissao, o clube novo.

        Na demissao o id tem que ser uma das ofertas: sem isso qualquer clube
        do mundo servia, inclusive o que acabou de demitir. E a pendencia sai
        daqui - antes ela ficava, e a janela de demissao voltava a cada semana.
        """
        novo = getattr(self, "_pendente_novo", None)
        if novo is None and self.pendencia and self.pendencia.get("tipo") == "novo_clube":
            if cid not in [o["id"] for o in self.pendencia["opcoes"]]:
                raise ValueError("esse clube nao fez oferta")
            G = self.exigir()
            eng.assumir_clube(G, cid, self.pendencia.get("saida") or "demitido")
            self.pendencia = None
            G.pop("pendencia_web", None)
            self.invalidar()
            self.esquecer_desfazer()
            self.mesas = {}
            return G
        G = novo or self.exigir()
        if cid not in G["clubes"]:
            raise ValueError("clube %r nao existe" % (cid,))
        G["clube"] = cid
        if novo is not None:
            eng.comecar_no_clube(G, G["clubes"][cid])
        G["clubes"][cid]["escalacao"] = eng.auto_escalar(G, G["clubes"][cid])
        eng.definir_objetivo(G)
        self._pendente_novo = None
        self._adotar(G)
        return G

    def encerrar_carreira(self):
        """A outra saida da demissao, como no terminal: parar de vez."""
        G = self.exigir()
        eng.encerrar_passagem(G, (self.pendencia or {}).get("saida") or "encerrou a carreira")
        self.pendencia = {"tipo": "carreira_encerrada", "titulo": "Carreira encerrada",
                          "historico": list(G.get("historico", []))[-12:], "opcoes": []}
        G["pendencia_web"] = self.pendencia

    def _adotar(self, G):
        # o motor pergunta pelo terminal quando fica sem clube; "auto" cala essa
        # pergunta e a decisao volta para a tela, como pendencia
        G["auto"] = True
        eng.trocar_de_clube = self._demitido
        self.G = G
        self.pendencia = G.get("pendencia_web")
        self.invalidar()
        self.esquecer_desfazer()
        self.mesas = {}

    def _demitido(self, G):
        """Hook do motor quando o tecnico e demitido, na virada do ano.

        No tkinter isso abria um dialogo modal. Aqui vira pendencia: a proxima
        leitura da tela conta que ha uma escolha travando o jogo. As ofertas
        seguem a regra do motor (trocar_de_clube): quatro clubes das Series B,
        C e D entre os trinta de maior reputacao, nunca o que demitiu. Antes a
        web oferecia os doze maiores do mundo, com o proprio clube e os
        estrangeiros no meio.
        """
        atual = G["clube"]
        cands = [cl for cl in G["clubes"].values() if cl["divisao"] in "BCD" and cl["id"] != atual]
        cands.sort(key=lambda cl: -cl["reputacao"])
        ofertas = eng.rng.sample(cands[:30], min(4, len(cands)))
        ofertas.sort(key=lambda cl: -cl["reputacao"])
        resumo = G.get("ultimo_resumo") or {}
        self.pendencia = {
            "tipo": "novo_clube",
            "titulo": "Voce foi demitido",
            "motivo": resumo.get("diretoria") or "A diretoria encerrou o seu ciclo.",
            "de": G["clubes"][atual]["nome"],
            "saida": "demitido",
            "opcoes": [{"id": cl["id"], "nome": cl["nome"], "divisao": cl["divisao"],
                        "reputacao": cl["reputacao"], "caixa": eng.din(cl["dinheiro"]),
                        "elenco": len(cl["elenco"])} for cl in ofertas],
        }
        # vai no save: fechar o jogo aqui e reabrir nao pode devolver o clube
        G["pendencia_web"] = self.pendencia
        return None

    def pedir_demissao(self):
        """O treinador sai por vontade propria, a qualquer momento. Vira a
        mesma pendencia da demissao, mas quem oferece emprego e quem cabe na
        reputacao dele (eng.ofertas_ao_demissionario), nao a regra da demissao."""
        G = self.exigir()
        if self.pendencia:
            raise ValueError("ja existe uma decisao pendente")
        atual = G["clubes"][G["clube"]]
        ofertas = eng.ofertas_ao_demissionario(G)
        self.pendencia = {
            "tipo": "novo_clube",
            "titulo": "Voce pediu demissao",
            "motivo": "Voce entregou o cargo no %s. Estes clubes querem o seu trabalho." % atual["nome"],
            "de": atual["nome"],
            "saida": "pediu demissao",
            "opcoes": [{"id": cl["id"], "nome": cl["nome"], "divisao": cl["divisao"],
                        "reputacao": cl["reputacao"], "caixa": eng.din(cl["dinheiro"]),
                        "elenco": len(cl["elenco"])} for cl in ofertas],
        }
        G["pendencia_web"] = self.pendencia
        G["propostas_emprego"] = []
        self.invalidar()
        return self.pendencia

    # ------------------------------------------------------------------- acoes
    def salvar(self):
        eng.salvar(self.exigir())

    def avancar(self):
        """Uma semana do jogo. Devolve o que mudou, para a tela contar."""
        G = self.exigir()
        temp_antes, fase_antes = G["temporada"], G["fase"]
        ok, texto = capturar(eng.jogar_semana, G)
        self.anotar(texto)
        self.invalidar()
        self.esquecer_desfazer()
        return {
            "encerrada": ok is False,
            "log": texto.strip(),
            "jogos": eng.resultados_da_semana(G),
            "virou_o_ano": G["temporada"] != temp_antes,
            "fim_do_estadual": fase_antes == "estadual" and G["fase"] == "liga",
        }

    def definir_auto(self, ligada):
        G = self.exigir()
        if eng.escalacao_automatica(G) == bool(ligada):
            return False
        eng.definir_escalacao_automatica(G, bool(ligada))
        self.invalidar()
        return True


SESSAO = Sessao()
