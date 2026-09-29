#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BRASFUT 1.0 - gerenciador de futebol brasileiro, 100% em texto.
Sem dependencias externas. Rodar: python3 brasfut.py
"""

import base64, dataclasses, json, os, random, re, sys, time, zlib
from typing import Any, Dict, List, Optional, Tuple
from math import exp

VERSAO = "2.5"


def pasta_base():
    """Pasta onde ficam save e elencos: ao lado do .exe, ou ao lado do .py."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


SAVE = os.path.join(pasta_base(), "brasfut_save.json")
ARQ_ELENCOS = os.path.join(pasta_base(), "elencos.json")

ELENCOS_EMBUTIDOS = (
    "eNrVfcty48iS5b6/Alab3nSZUXyrd9QzUxKVupJMOZVjswiCkWRUghGqAMBKsq0/Zr5lfqwjAFJZJgTgDxIym8VNu5X3FoJ4hMdx"
    "9+Pn/Ne/RdFvV4lYSb0wv/1n9L/dP0fRfxV/uv9Fm5V0f/vbo0lT9dt/7P/61aT+b6+/3P36OzUXc///7Z28/ZVZW/cX427xz//9"
    "H+FLX2zMwkSTZC1T3ALd7rsFBoN//HuZ+4vhuHHFiZ5b+TdyscH7xZqv/SKsTETl2neT58CT6r279qjfeO3LlbSp0dGj2YgEt0R3"
    "9H6JYfOj2djMrXCXxyJFrnD6foVR8wqJ/Bk9CfcKDPIpDWi3cCdN9MVmalu5/LfJdeDynfeXPwUv/yCtVFZwF2j+gi6EVolBXntA"
    "e/gvKhPIS3eH7y89aLz0jREmelFxZixugZP3H05/TNvGl1bFP6KHPFmI6pIvwdDUpT2uG2MXSi8N8up92ou+XEub+d02sSL/E7lI"
    "933MGHbfPbVRc7h9Enk1dkwvPyMCObDxLqS7EyvSWMhMIJd4/0LGA2iJRETnNt/irl8NTqfgC5fRuShvA/mcumNigPLBNXoQf+Xo"
    "51S5j3GveQnj7kAjr92pnHDvv6jmY+lBhmL55HmCuY/mj/XM5tpEn6S2yj0t3BrVmNgHXofa1m3B8AIdWmR8EqtcJtGd0tinNKQF"
    "kmujtyJxx1IiAh9UeAniwTHR2dLoTfQiEqljhV2lEqx67z+tHnSo/JUrHV258zYLIJLwqpUPuhIiO+Wq7s//4/+n3x5EsvInelqP"
    "gF1QSEwaTdXCvUwkdiSCr6mwsXTv8c6sZgIJtt9vqGEfsaHO3MGjtMgM8j7eB7hhp3GR26VMHJzXSABJ3K+TRZ66Xx9dK7FBrlA5"
    "9k/efxDAsSC/Z/Kj1tp98g8+4lm5RS47ph101+4ZirWJrt0/Y4Hy+808Pmn+mnOLxrHVc3qM+Iyv8niZIhcYET8yl6W4HEXa6EzY"
    "mdlisT4RMp1JLecyyxTyLiqRbUSLp5crlSjhHp0LNW4PBV79Cy6QDaBAlpj6qP2CKhuAx7ZHUZdroRcyUWng4EMu04NrBR6u1aR8"
    "YVjboZ2uU+H2SqwMErARz+4r93xeHTb3n3NqkKiwWptofuUTmy1zy0WcQxrivBP4G+megHumC+XMxkaPBg1AKyuOO+9WHDdHt6tE"
    "xB4FvAb2Jw7NAaH5weWAwbwWCUebz5ZHsXKb/8mkWJRIjC43yyJnVmg8WHc2vsG/M5OJ76ap/nktZlY5EH8msmCsweEm4Ev76sKm"
    "DH3YYej3fhcB5ZJz63750kV/92UFajThO6js1Pef8hCCtJmvlxmNxk+VuFMB72NouwY/bWR59AQuXj47dCtTbokXPDljbG23NyJ+"
    "ALkSM6HNB72I8kSIzpciVNkP45sB7XVcSWuFlalqBwTeCuW+XaEzl/Riy6bVo78DBTO3Iz9Jqz3c3HJxYF2GW3tn8xy51AlYHWoO"
    "avvIeVNkbYZ7gz3aDZbocGr0NhBOw0v2aZl0WaantQKqt9Wn3dYkSQJlvTDQHdAOn+J48KfDVM6VRqLpykMb9Tm9jRdU5w0IBruE"
    "YCV0qEATXqJSPWlGNvfy78wgn38FNQHR+Vbk7uE/m0TOsQ+oA/VBgSfmtoeDtsiso9KuGXaohQ07d3fo8mkrsYlU5RaHxEPom9rI"
    "eNlOynM5l+5rxmdUlQ9iCKBBt9ljGV2ItWK+IuqxcGFWSi9M6nNF66+Je0k98MvooJCCOykC2AeJ6Zsf5rPyRbWlcWmJBwzcTgJw"
    "ludauVTxySEGg12CWI5weHop83RXv0m5ZfjKGT7EVP+Z6W+16D+AwImyuLWqX3wlP2kOSp/yRU7IhE/AiPu+s/AkPITMkyZujfgu"
    "sC2FCuYHaj+7rsW5C/Ma3bY4pR28Rec/3AREJpVdIn8ntzJx0PwszwSXpNKFW5rRnVphr98BQ2AzMPoqHfpPknZ4QyUyKsoyyAW6"
    "tKPqs1i4t+HO9zxeKuYbAd55uUk8PjKKy40BSv525sEXttLfp4GFt6P1InehW3LbCRC3Y4ZPsYhb4vPCHW2+lJzOpM3MB3F8Pqci"
    "5uZWHdpSX1JjFTc/7Z++X6w5Lt+r2CQi5T7FEW21BzFLfM9HsdM6uHFdoEaXHSnDzI8A5HMhVj47PTMzBw+SRLSTRLaZ4fnkVybb"
    "INxAErA6wGGfJxvupfuoekqOboH1K00QxInrC3r4NhuM/qB858+lO7S03DDXq+76U+gpKoFlAVVP+SEAw7RLDtwWOXeJo7QKuUqX"
    "1nmvfUPINO0E7rZGTypZCyahDFrAZrnl/vbmLfIsM8nNWvq0Nv7jRvjuutCxSmPDXXRMK6XsKSM+vRVacDOmIa187LZMLI6VDALh"
    "oGQvuxvk8gBP3iV/Lu1Suui5NRDLXArqyxL5VnBZZaeY9v+d8QMeuBUOrfnfikCvvJ1ZjrIgsiW0/Ia8isuZCrRMkE3F5qd15Tsk"
    "W5fPTvRCBSM3LkkDvm7/nXFzsyHi7J6qRGjs0Aix2bJvIhXEhVD//TgZYHH6uDxZJEvDTQN7qCBaS2nGUe/4FZlwOtMFy+w9zPAH"
    "fvbj/dnaJ277xwJLS2abB7ibMys9SVbN0ZnACVRgBdDv+bKgfiA7e8QW837iKnhq40hywNsoKPS7T/tovavmoPlo5la5g/NaWGwH"
    "i8qR3Ud+EvWP2pgoY46fOHFJLTYvHNC+5xuZptLPHyyEnXN7YSeMxjRulgVImi6UrKnRt5MUFm+ES2Ts0zqw17mKJiuHElfIm6vE"
    "zSEtA/0jt27FJFzCQ3ILmx/fVK5elyqNLuSr2DBz0HGXRfFCJriYQsRjaEoOmYE2//hv4oewSkR3YrYRc2YpYDgGP6t7uRDs1HBE"
    "6w/eis0PLDm2C3ZKujAp61ymwjIXrCYz73t2kyyRmYrN79Pr+rTNT2/iuZpD2qmwx7sXMvkeiA3XqKLtEDpBfRTgZoR9Wtwpd9W5"
    "mVlxNOYpUGEXHu/IhJmQAIH7UeqCSDtX3PkcoGJvZazE3HCvDhRVNkLH7D5RH0GXDyabyCTtBJy/J/XQOjSw9FjQsKyDTCaZs4ml"
    "3WON4VdP/D6Ngf0g0lhpxV2tR1vts54r9p1VaADAyEmyr4Jik44xrWd7ZeUcmTCRad6bGJ1cEkvct3KtfBPAZWOaTbWEp+PSYjwO"
    "ef0uSEACqOvKZTC4tRAtZ9xo5FMs7Ctbx6ADzP1Zjc/FiDWmolPvBztTZBYzop59Lp5I7KxXn1ZLfDar3bTdljnfVa1dDTBV/+CJ"
    "FV4Rrpb1gT5tmio/usDNMJqxw0UeqFSH8woi6jnPZahIgZwa68HRfKr0nK0tMKS99+el2tGWZuhJsj65IS9IjFM4v68kK5915oNJ"
    "rIwWSX268iTtwiVOjyZeSiTopzagS5ao4mYrY7AKZKJLdwxYbspCZBkWMXomFVfFAKoxC09nmSxyZS17Nq6SO49wvSyxVILZzAKe"
    "mudAo3tx1TrzEKpreGrDqphfV68COdpTLQENwY7pz+jZWIseXCN2GPb5/VTaOJTlhW+DSJncHWy7tT6oE1SOsdzINE+5K3bI89lt"
    "aZrtjggCcY74Hey7GC+e0bawbFIbRkUpjAiRC3SA23BnD3psiVj/f1TxMoSVcUoVEJXco44HkXkpOW7z5fQQCSvcqBCIMxI5w/Ys"
    "KqxFkKma+Lm6RDnUip51IkpkTVxY/8ntuXSpM5Qeemu8ZtmQlhzfmJKEZ2dGS/QiI6osSUG19W1dH97ZjKX+8Rot1DTSNw02XKxP"
    "PJX2wOc810txoPDrG/K+tnKlGuZ6vkov8IhuEYx5LYJr/y1jiV3EEcRfMEU79I28kZP330GfrBlRsMl9qiLaUUJo4Mcgx4c6CP2j"
    "dkaTzktRghoeFLI90EHkWm6hzDBFz2p7bLWxQGu5cn9wewYAABLJLJeaTRvrAYO6CxfooztpfE3PcFsGOOJY3eAnUtNgjOjSkRKG"
    "gyd8dmPOXDWKPpXi61ZLhQ4oriEB/RCjClGIxqWCy+c6AUbJ5op5ZQBql4rK98a9/gV7VAgYsPFbRCvuxYEwYs1aafefmDsFA7TM"
    "PYRPVuy5eGqFMjRRgAP1YN65wBbwD6Yc+UpXtvzb/cEW8B1iZpxflFaxylsavH+TR3lwUVhz4TYA6lf5NueCbUCawKyFlodJLEBy"
    "7FqsjA1Vs3B3MMSxMe99P3slNZq/1j1QMH3fJ5BJZsWKO+JTHdkEKbUu6Z7neESBYAqM3s+n2HwrlTVNqsdpqgxTixioRnsmx8SK"
    "EE0N2TJo/ua/OMCkzAfRja4KEMhMV8B0wkWeIsCxAT+gPuBQkRIrZtEe4rjukshH8yffU6QDFp2jqQs+WFm+g4tIxcxO7DUofHmv"
    "HaeRIkvdaYJz69td3MjoR9bry1HiAognM8Htr2C0wMJzpEgCD66gVFvXRRKQME4Rj+6frGEiZuCY+SZrvH7C3JoxOLUxxswi+q2q"
    "uGv2ibWFa4LqcdWfovMRIyKnwHDQDnsejZ6CGOY6NynanOTwcVEXSAvrFS4NY4ybHpRxO+4YBVh7cvlHmhFoPUQpp6+iTsD7KAlO"
    "2acqG5I5lq/CKIyWOmxs5bJTGuPhVuqNdyUyG8M0D6keb0NAQUSl0pbnm7USnW2dHKh06DaRO4cid8N/qmP7pNSKVqWJ5KrC1QaJ"
    "t+zkKslXSkudyvr8xOEwLMTvD2hRoySyX+ZztC9hJaPtgX0Ob/fyoDKR5AtsX6p3YK19Z0f0v1xyhE5YhtT5owU7UwHnLpBkqQq3"
    "EaT9qmQp7cqbmAnN1pU7xdQSwsA0iHz7J7Sv9vOi4AK2A6sLZvGjmAVZoEdRMLuycpOhWVdD2s+fquCUavjaxJ7ZjVyt2L8baIje"
    "5F7t8ErNvfra0STDxihk+yj5Sw5pS36SNs4TPkcJVNb3jjdJwu49NEfzexM01Ho5hjFETSUL6XEJlWd0ari0JDB9XZpoEuNTieqP"
    "PwW4PCo9wNKmc8RuD0J8uQvosyQ/cFiqTywkuQx49f/+r+ckobXHxsTuiLvyLITEjmL48mQymcy5FpOQ2nAxLvXkyd7t6II9ibWw"
    "eO/HU6rq21J70K/lfMPMnodQey3NFH7so46K88tspyCfNziNh7mkOA8c4GU7kDf3ZMywBP01ytUXaATciTwTts6+CUc1G4LmFoWJ"
    "200+47L4gef0aFZC15gD4hhA1F73B0gI+3FOFd2p19fQ3Hs7fYJbofN25qy9LcC8VTXhHQ+P4ulNJWwUS/hysETLFhOp6Y3SRO2Y"
    "63yT0VsyyaU1DWhLFqTAnWellVxTR8ACOJZrvDcJcSL+Rno5BXwngnoIXwYJ/kcB5/sZjnuZhvYJkq8DbEUVL2VS51KNtD7vwW70"
    "RkePalZQAnCQekQVcfZBq47D2I6eU7E3nnKRprnmCgtTZ8hLIt1Dnixa8uMuO/Y6ujGp5M76AmSkuVxhbTioJ4v/1gQa0Vf4YOBM"
    "j/zTRC8yUVsuReiUVnsvXQ5psxgHI6Zb9UNGXxK1luiOE7E5XEihFNrxzOnlAXEU/yJkgYFcqkOXqI2uct+OWiGXHEGalRDxQfpB"
    "P4J4dgcb+d5yqxeROjw1F9G1WDXkWP6X3Ag7x0pLVff3KULp3j3eLd5jnqo5m6/EW7dy2w6tqKRfPKjMsK3sIW2ePGmYDQz3NTpU"
    "zYaPdf30A5VPLrirtRLcpAEjXBYVElxczhKxjby3UcolWnyYOuDhBVrL5hB6cIC6xLMDkZH/A1lJJnbQ9tPS3sooZS4BdVmEstwy"
    "OCzVUZoTmpQrakQ8gu494cLnvnjmEHlK1GWDaU0dByfXgwH07bDhr0Sc67lnIiVqrlod1g1TU9uRnZkWxeDok9Iulliz5WI3FJ2n"
    "pjyEez/gXIevOlvue+kC2Qea6NQlpgfnicjnPiV8rWkH0qYh/uH0V9g+whbyVmzRlHeq0rN5sxtkArsuMBlqFlKjCTF1I9RN9ILa"
    "MZ6jQDqHGN1bV0wKCXDxSwe+Z8K2U72+K5IxiZakofaBd7RsaVWaqlVL9A6e/QGCO9aBt8XEwUXFt1wjjrXu/Aqvjd6KhTiaK8II"
    "cZ+J1LGwH8QT2ReiJlaYdmBlcVNP8XKl5hmXzN/BEayLcopox4XhH1oKiq/L2UUYKXMlWpqPloelSnzrzOGxPCN42BGtBJ+XIuyR"
    "dpQB3qCjK/Lx4F7vmdGZXL2aD6LOT335IwkJNbQzG7Ajjz54+Ur1QcX0e7lZCRvdWGahezwEIEGSLAvSdjspxtuXUaMJgEyWoJvA"
    "2nNT5wIua0RsaJZodZ+vcc895V4byuhnhRGiaac4fkZi9w+pKgn4/KdalyZrYpSIO7oLFSLa8W/ydQPv9qlFsFiEFEcd0AIJ1agc"
    "r73+lgQ+ynl0lidFlrfwFT3dNFydSIXWh6KqAO8nVLnKUDggH6QHt6PHulMWjc7Fq/opZmyGfvPOeymmrEI08aP4RkwW7sF5vqH7"
    "Nv59onVLCk67wt+n3GZ4E4k+dchjuypqZ3U9mKNw9ncSCNGuusLk7kPmVepnfd0BeRsdrHzTX7lsSb5pz9mvj6tHIbz4masQ/j/K"
    "QHKd+NRR2gePYqUs+rEQh54erPgp52jR/SGnF1mHIcNLEJ1VbpZGR/4PrrL/KWLcrQjhvgT6QQnLvfAzCE/4h3Zoff9JpEvRjvz+"
    "g8oy0Y6e6C5kmHbUh8rYilcSPfSlT03qoiyfFoOAkfcSLUBU+aKIbt+TbLnBz30f7EnoIw2WKts7UFvpvpQfqWkZI5nmHarnYnkU"
    "38u15LZ6qQXo/fYiySocykP+NdHqZxHSY5GO9rvjF+nID0o3jXSUZ9fExkL/ic1HiID3SulMJiuh25m4KGwzn0IKokdpfF26H54X"
    "rUGVYclM1LkUh33YNCYoMxOrsDAFLpcZDuHG17nbPQqdyQxY0nIED/kRdYRqlWdCY/tAvS6Rp6ni2GFmxcyOUM4rz8Ju0YSuQ4+F"
    "y3nOnaQegKmLn5x6MvkWm3oPaVb1X0VQzvblGO33f5SSRbJEz0oQ1bHLCTxmhwp4OperXajbjWNvmXPBEBWtdBErzI4yhe4mdYg7"
    "I2S0hSNuAQGj4HY/ibW0ynBXgBiNhVzMtdGxSNbYrLX6hPoAg3wmdfQ5XYWMWLndojHozJqZ6FZsttiODrWzUFC40P7TRLGHL+ma"
    "MBpxSivbhsegkISnIVxv5jK2QBpjgS+8UYs5mmPECUIKvZancpT7KnHH9gCLDeC4I8xuVOFkn62wiBvcBBbgpIZ1DthvqcpUWe9i"
    "0+CT547vDGsx1xuTB5N+RtO8OLuZvuFQW0Z6Fb3Vhsn+A9KU56U7VrcySbi/fjAEjUWDsQ8nSgUWoQo7NK/Vh1ygR4uAu6mXM/8K"
    "2EsM4NJTzUA2kmWI2dbFVBm6GUyFTXvK2FTES7T5HZUuWfhVMSc1II9rT1OlNXJGtLdwmGUftTjlS5nR1OSWy3wD3XZSGU3w/nBE"
    "4LGv552LrZdgytjeGEN46331hHG9yNDe3YcWK707ivLQx+sYcJ8fQOlaik3CFsiFyPZLFTswHhg0xJnrARvlQmqV4NV9ifhsN/VV"
    "p8KP08iCtvq+MexbFirjqgQBr+FeLnI5E0yyErAzHKxJ8e0JYp566YlQ3k1PmZjrlw28gl1xngDDT2mndjmLU8NgOMotfJNRORWJ"
    "Rfs9cgZmZRg6ha/fpf3+NwramYhD+j9Ij40hRM+aZMtEZi4k/f7wWJ8DTDdxqF5xjYvwfWq/OPhZINMBpIhj0EqvHZrWNExdRPYw"
    "IFyUeomSM6n92CG6U9IhgmzfcNgp1ZP8uanVsRJsX/rAvw58b8gct3mNT97xR7AbJx1I0YCbIgBTAGbmHU+uPLFMWYl2yO5S+zLF"
    "Af8sLXqSfED7lna0HZnIreI2T4h6N1d+TiN4mCFJZh0eUwTZe+gDFasMr9TUIyoZXnptgkcVB9EcsvE/ZEyeeZsl5Hpgzx9SsVZ5"
    "QhifIZ4nJZD5Jl6Dc7NIlhg0N5cn7fQi/OyqiYgWfof6TZJyh4Pffqll+uIlgdBIk/gJ7JaQiVeaaadqXUj2EQlpp3RF7ZWwLbUr"
    "fJi5da8dazdStS8GFPwz94bL0jhaP6BHDPOfUyFiJl2PGiQdjDioCdIFG4Ka2TWi+xhvisYtPtOD7TUrIk/nxqpMzRoIV2XzymGP"
    "kJ7idStiJh6Tp6lirjYgSsXviRB3MuQqimvWDCBnrBjrPk5MdstTdBpydUM2CQARCBFvfH1a6KXgGpyD4z9vZhnez4dtE85BUxTf"
    "9s7ByayKDdaUfEzkRux0Q6cmwSc4Y9p72jlHXtmirMLu5/TAtiY3PwOsV72gFLcLwvm2Jg4ZuityhYI7xCgmC1depmnoAPp0w901"
    "ZDME0LSXM1EqJoS1pZCLDNrvfWC8KO9zjWaCH/rOb0yaSxfD/IACWveL2lTY1TXmfiGs5m0VIA4gGaUN3nrjhHiEeTnoui4obm6H"
    "uv936nWTrfj+QUy1ZxUCTMi1iDIt9+4ccymbb6TItvoob43YOoEQJJzvgRqxIjOhouxREh+iNjHxRNsf+kSfxWroBIy6csuVgxjC"
    "o1yFwphKM6629QCqMrnEX3BnxQZEUYC9x65WaAGQQ4tChSL5rjfDvcsekRXrexoTF2/YC5KRc9l6ulBYZcXDmb/KIR47565WF1F/"
    "5d1L8Spj02xIudP9InX1iDXyUNclfGFiO2efVX+VVmM5kNVzt0/9MmdSp9wGG0YE88EhYRkbbksS1BFHa0UcClH8BDV+SIka2Uvm"
    "a+RwnWWK/0EJb7k1npcbabGWNT0qo3pnWUPSciCfT/6rcrtQB0v7yJwaRVY9FzITaGucSoUL8BUX6DGryhMasTSjcN8p8PgvzEq0"
    "kw1+UgWzU1qVCdMO2e4Pn2OU3ALmiNgQMlAVOvb4MpRb4HQuBmNEES6oMfuCEi5Cba+ycsWdfQKql8rXXRyOneRejofrdTOEUN5K"
    "JdhrE4vTRX5cZvncZukJwqhnorNgaQTZKyV2L3fng7uttfCKfGxVdEhmOBOJ+aCG0FSE+anI1UbU1XS8bCkrK/mF3OyhT/sU/vDb"
    "M/4RnfmihZLcSTug4lPYKtd16JGpH/EbP74HTCVNeZSrBs25ven8o9ALLMeR2nX4Y6fjvcR2H6tVlA57DKYdVmO9tx5OvgKYfNpn"
    "y/XLIHUI4ASilGDiSjVA7e+/+ckQsW7zLNIUbWtDhd+3icjTdnpa7h0kCbqn2KUd299k9Dk8PoyUggC8hIS3tt2iqYxEZOmDo2ea"
    "+3+bN1cFZDzu8XyVRU+J27EC91eCHg0iPpyp0djRJiogehBaLJTJFNa1hwgdbsQ8rA+DU8YDU2WfKZ/lEs16JO7YOk7qUcDolZUu"
    "20y5TS5isa3Ucvm004fctvNCHlQcG+ZEFnBOFunzg/oh4mXObf90oYP+u0s+Nda4k1plexaJEmihBGKMuBaJFFin+UpwA3fxn+zU"
    "YojSeA1SopArDMD5qBreN64pCVz/wazlnCs3OIDaqtnmg5o2Ba4OuzDjhlGAW3l22ekKPYbYO7Dn5ZAQ10Jqfx9vSdWVsZnbXNsG"
    "0mXx8Oq+MlxeBTgJfJKJH3+ikB4HVIK/1Bor0Uccm39WoaCKZDyO2+/zACVta1J/LsR5yhaJawanX+WaoqJHHNI99xY3Zi1WXOYk"
    "0ZH+TOo/xUrp6DZPY7lWMbNPAhlI7MoZbjn3+HSecfsxoL1LMXk4WauE7WraOUQDMnwXfapUwo62y/XdInMqU2rGdcKdcE1TmWVs"
    "uiOGIxJWdn7BDeoCRsDeT0dyFdUxHEe//1/RMgxE89Q/ZMHTLB0BkMh/TN0e/18JB57y0xgkOxM+EfEmXYdv9LzQ8/FvxuNHtOlO"
    "j2o3Kzc1h2T48oMPFfYbAZamYuWVO6WypiVdwkPclMACeCI0ZUqLGAE98jQUoerqDYze87WksA14vY4uhgPS0CCYVN57imntg4K7"
    "V/7ICDWSkC2WLqYZ61WjUy7fCKW67LZEaDIFCalRrGfuDBQoeKnQDQiqijCtS8DzWInuhIvUc66fPZTOHEflDVIHkmyy2hDHJAs2"
    "GZFKCkMMXxWPjYnJ/JvpwJOZWZFwAfgpWFHO8XZA1cuPcI3RmrYQEiFjdFim+UIrrqkpxrwHbz5KPTzvTO6OT3TRnRjodrMKBDh5"
    "qP57LX/zKLJu5XR0UGgCNwczwlyfJh1MBpNByT5kBwTIRT21z53KG67V0PCITYou8bkcKhsBqvnE3Oo1VcbnH+4tofFHJD1pAJm3"
    "PL0am9WD5LoZvOuj+G6L4AbBaRVDai9irbjcIKKX6YRiGNkjOlYUYrNe/jBvSbX4aNSjIaQbs8EXtw+VTT3KqMGYb0uD1A6DpJBW"
    "plB5kVus0HB1lyD0pCki7sRRpUept2wdMkCcdek7GqpQ9FpLvnbxCHGW1/HEcXx30N/Ig8NbNEDvkKVBwx3dF5TlcdV0rH9UqFuN"
    "h835xqeNsdgac3VLjwBVA7tQpl79/CiV2SbTB1ylHP6e8Apwh8OUkEIHsshMZHyWXjVFn1e5bEcJ5og2ppZdOsVuuTASsGIzK1Kh"
    "uUu7/IW06kdtcQcJsweoMfZJ5l+E4fps9kA66IO0BLI88S4OskeBBCy+E2rlaN2/N9h+k6+lzvJ5wyTyTYHmFBO6g0lc0Q+/zm0e"
    "S7EQXBCPKsJ51xY9x65BJvz57Z6n8RIrwUud157MQtPUSOBLrJzs+RCffObILtxDNi0Lkk9Lj/ZCGu01kLlIHypN/5A2mgQnYJDJ"
    "AVCX/js8AHskTWG+WjFOkuwpQBNC5huQG3fGtotq/mrO1atV+FHpQ2FPARKevhu7FdyaNMpM6FqFxWiQesgDTv0FmXYApHmpfhp+"
    "ygR8RlIjBXz7xB1wE1avR6YXmNRoV6FET9US0f+lVqadsrl3f/AMyLmIBVf7GWdv+iItemSW2vpUCcUmY0Tt2u5b2jPVjnDxbnR9"
    "w/VwRPlORbQhBaJM2GVpFh35PsCiJZGwM3fOhGzqkPrO79nf18ZrEdQi7Wd3nZyJToFC5k6Vrl4uDKko1HwQXG7lXzm6zA8PxYN0"
    "SuXjYBJUwcBNi1LtPCFhmKOY54ULqUjMDQbfbZ1uCBKxYqqQj2oWpKcdxTevjo2DZIL02y+WQ+JCBymqQqYzmsCiGFMVp8XGnRrt"
    "SNqU85fnIs0sFu4dSjf9ZcMXPQq0fkvLpA1qC/9aLiSXxNxvlQ7SRzamz3xqYpX4IJLxRKcyWZmCk4jlPjA1uSdBS3TkAOgAYCgU"
    "xlLniVxJnUku/gEwVpooB7AsukhOLp3KOaGCfXA/NyhVhpyBJFs4oJciKst+coDX+kqmVezCcB8yh5g4dK1i8fv0uoHUUQr1civD"
    "QwQ5+cxtIzVn61T2EdTSFVOKBRKBkwrvrtw9EJYGpfORJhMgYJxvcJc+eR9c+kQCjGdCsx3mTlDJYo2e6lGovruZXQoPosdimD6Z"
    "VHB1XyBoqg26lk30lN958X1Js3gpF4KrLIMaNzgr2xfpBzlfu+3Hnecb4KjXl4nahiopL8eIg+5pWcmfeWx+I1/cEaEM1xWBqPe2"
    "LzxdmJXD9YZN/O1ioNdkJUJ0+Hb4ETfGLrw5r+DWlLso6YwHisDOKS0G/wL8D8LKueTOZw0hdsfWszumPpFUQiuuk/EIhfAflMYP"
    "4lEd7HazL8g7OKXKEXl+ds1gCrLACWla+75Q9E1t0YOcFTl1WKdwku2smK+/1EPVl0TM1UpZbt0TQ3WvZeojB+lAtfZo6naNslg9"
    "+KqqCsQoqxnOOIrA+WRe9FV3073symkP0B63idxwu/1AV0nODlDVOGE5OIWBF7GJcSCJAFvFoXleEb8eX9b06mw1SOUo2PEQUsEJ"
    "sHd9tu6DbSITwZ1wGzA1OZAYsddmHx7KlWsiJ9ILGqNBXZhzp9xCKWaQ2quUcJvx/ba5vj1Y1YfA9h1SQ6cPbxuXuDrgl3LXADtz"
    "1qAb2iPq5jqOJRV8xD+bWOjgAXmUhvatWKpU2uhOarSFDzFS7HOwCd57ic5bPc+VaHKu3fMXz4XVWEBGHJYtLdnD2vnXx+i2eXF+"
    "JNIjKmt6aiRXuRnAGjag0IWESF22VjdSeoxYTCgYvZerV2llbrn1NsQ3dCbSlK1rMET0VL3BN7aZTY5ZuUqF+SAdsHORyBkWJRxK"
    "9XiQWG8V6nHeRMJ4wflcj6nVo2LzhPZOO531qfjJPeYh5SYddsI4SmUv7MIVvvTh4UWlZUviO34yhThofpQRHhCbyjwlgCJiSn9j"
    "tEO/xYzs95a0mne6HTWVvKMwjY+koQJ065MQ9w7Z3h6BHeG1UPWAq5i2ODNLJGKhVnVrugjITjPC3a8dg5FJkuCn1akpeUNQx6ks"
    "AxnVjfz+naIke2iLwwffBlp7OyDvUW40weiCGH/L4Bj9K/d570pwPf76KH/zdgZiLky+wLMtB9yW0OSvXKGnbg6GQ972jDDNThcN"
    "KYZuHqTGCr1S8/ivHtJbtOQXtdZ94X+9EgvJ9CCB6qEeANcW/ZDefD2uUj9SerULEtdc+l+WIZhTLADNa4OGoujDvKHwdI51wiCL"
    "irmLX4uVSLAIsd+hYquiHf+itjJvZ9TkUaGN3MlljUIlwODt9g6NfZ9TgbbSZuhAnVs/GLFqKM3t8h7upDegZ6aCra6jSJkW+GRq"
    "rEmxzgZdKIsGpU2PMYUNKoRSzKA7dO2FqdDig/SazmUqLHec/ATR4wkTusMwjjyOXeitFBMQ2MFsait4x1pBXpzYxfNslQJYydec"
    "C6ehn78K2QW3AxJ3g2VRieHbYd49+b7whjv5DT0sn9i007ANtiaQ0PkE8YqjL1mIMnQUdaY6o9ZjDbVEd2bWUh/1kzpAJYlYwT1Y"
    "XAigthVko0NU8oHiyNLXDUVEshsmrlE3iIi8gS67vYjs00KzMFhR2YPdqwu7QO4Y1Ml7hPl41tT33atQzhS6qEdk2uwHFWUm+B5X"
    "XcYkBHKKekQDmQ5chjznkJw54AyieVERT6FbuVbsSwMVio2O0T/7UEG6Myu9BzF3IBslpGjWIuOCsi4E8XXBHZ9LtylWr+jxGmI5"
    "uqgXkQZ4qgRYQIPeRdtwbopEmMSdt6shESaeqS//3G7SzLwupeV2slGWtv7VhzWtj1YuFIZ7Bx1EqZZAraNW5+uovcgqJzC2kWZy"
    "XVBIwrxYXCFygHEtuxVJspEJtyJJrXyoHwLdyyRSVnYdDffQFgvFhiUInY2HpUshN6+Si6AR+nbeST0T+YHYCjGwk3EddYcIZsq9"
    "RF/+YCgq5myuxfuO+L1ZG6u23lDdAcEGQ1c7Z8tnDuCt2c78criUdn2MHH8aFkdDjpnAFRWsSia14e6zMX9QsCuxPH94JBI/QQ34"
    "nVkTWAJZwARF2l2YKMafg1q7SBSI0nbjkhm74As2Hixb9iAIRIvb/EDDyw7oW400RlNC/5WrlriM0oVvkcyxlyeyD7x/GdrXiggr"
    "SVJJ1Df9y1bgi83Uth0pRS/7oHyxY+1LdWy9RlRF9kmtREsA88ZFJoWGlocWNotilFcN/Ci9eR9VBFsfHBIamvFdTHHlTV+ElLFo"
    "h91ZNil2eg34UieRSvEs1geIDFHZFOUH5qMvvtE+InJDZKK4hITB+5b9l1dpXfwwvz881oPYy0RhkSY1V3oRC421OK1yQziVZ9wQ"
    "Tcvj0rzDCTml00GNaHnmTEwwHx3Q4vptIvK0HaEaP2v5uuTq+JzAbvPnudR5O9evsyEIo8Ah7ZnXFE6Ocm1vnimjC6EzwZ0mAlY4"
    "X/oB/rR2lhzZYgaEiBxWmqNNQHvEiFMQugpHkOhbnuQhTwtkabeDKB4XEtcBfxkcg2AwQoWJM5PGS5VgBRqpFdK9mG504f7Lllso"
    "BZ6WsELNuFZMA7B/ozUbTfZpImnnQpm6PYhUtum1ZwkKaIB4p4zoX57prbG6mNTZ1revaeoVoLJMHQiT6gfc/naIlVl4BS7+SSVz"
    "WejL04yLKjsPSryW5u/o2Vgr2YTQPkQIfVGJiO7NuoER6tCsl+C9kyqT7Sg9Xggv149mnZKVrfYj75lKxEe17cUGbQdEJbcfwSwU"
    "NVRSN5mMI4dSe0rPQfYUUtsQO6RoUqyIDBW2THYTH9GNTPO0HWi6ExzzfXxh0Q/rhJi8Kv95Bd2IkWPjxBmv/V1NHQjQS8EWOuwh"
    "bmsqrcrQS3QZnLAd8FPBY+EoPfH74lvmTooPyBz3v4o8Oo3qavtImXSo64seBSK+lYs8oPR8lMLoZcj1FqcvSfXSKOnt4aYfkhnb"
    "wSizhsVxj+KVeOHwmMg8muFeH6gLiLqZO2RNr4vIrr2eBrfUCnQA12EZOFrzu+7tbjzxP+RxgGMJALW2vXzzISuM3gHTM5OJ72Zh"
    "fn96aO7do1V4iB32Mm2MbhP1+sr3zCGCoF+cDhd4CaW/ITXfLolh7h437TA0fV5hmT8ewQMU+oNQ6Rt0vJMrPnWyC06Ii1i2gxm9"
    "5BOeM0ms29T0znDN+AFOLPqzNnHYfhhZqu7gxlPxpAhq2XTf6X8SiUzbKZruJSyn3jQ7aad0ujMpmxorsLdRibkDeKLSRBPtDkK0"
    "KDmxL7QDOtdi3ZJW961MQrx35LVRIMG/Az/+xlWbbH7Pf+RWcUWWerRq6cRmy9zXMtQP2U5N89NmgdXP7nEFWKJ7ueKqpXeQcOBf"
    "uVc/2jKHmRDbTpn6BBwHoIGN9ylfsHviYyAwuQP0iDXSMcc79sDF/qGXviwE0+tB713RwjKh/Y9krQIcvkTkMXs4q4PiOV75srnk"
    "zukTjWu+hfgxSPudE8wYo2aSQoHvuhmaIIediF/3hXI5V3QmMhWqlOKUpagY+8F3L92NPonVq1CmHVvHJzV32anlIniMieCZTORW"
    "Ma3JB6dEkSSflNQ0h5D4e0yvbiEHuUZH1Kwa0S5+5dMGf5p9TtXcWLanevPG/8Mj4Zphtxeem+4IQyj4kqj1AZVl4JUX+prRnQp2"
    "fV5aic2ldDdBOp3omnFjMvFBQ1GTNFUp9y4AqkfZ9ZnJrUg/iMiwO3zu5cLmcay4z3BApU/UzXAcpcha8llN9OyyP3xXnVhs/epO"
    "M5/BRpNXb3bUDsHhQv10K7xItDTtoYf0H576pbmK8cS8sNQTjcLSn8j7I355IUlkHLt5MPwF4f/tv/8HP0u5zA=="
)

rng = random.Random()

# ----------------------------------------------------------------------------
# CONSTANTES DE JOGO
# ----------------------------------------------------------------------------

POS = ["GOL", "ZAG", "LAT", "VOL", "MEI", "ATA"]
PLURAL_POS = {"GOL": "goleiros", "ZAG": "zagueiros", "LAT": "laterais",
              "VOL": "volantes", "MEI": "meias", "ATA": "atacantes"}

# O motor so enxerga a contagem por vaga, entao dois esquemas com a mesma
# contagem sao o mesmo esquema - por isso nao ha 3-4-1-2 ao lado do 3-5-2,
# nem 3-6-1 ao lado do 5-4-1.
# Na linha de 3 e de 5, os LAT sao os alas. Os esquemas "sem laterais" existem
# para o elenco que nao tem lateral nenhum: antes, todo esquema pedia dois, e
# ate a escalacao automatica era obrigada a improvisar.
#
# Corrigidos junto com a expansao: o 4-5-1 somava 12 jogadores, e o 5-3-2
# tinha a contagem de um 5-4-1 (que agora existe com o proprio nome).
FORMACOES = {
    # linha de 4
    "4-4-2":             {"GOL": 1, "ZAG": 2, "LAT": 2, "VOL": 2, "MEI": 2, "ATA": 2},
    "4-4-2 losango":     {"GOL": 1, "ZAG": 2, "LAT": 2, "VOL": 1, "MEI": 3, "ATA": 2},
    "4-3-1-2":           {"GOL": 1, "ZAG": 2, "LAT": 2, "VOL": 3, "MEI": 1, "ATA": 2},
    "4-3-3":             {"GOL": 1, "ZAG": 2, "LAT": 2, "VOL": 2, "MEI": 1, "ATA": 3},
    "4-3-3 ofensivo":    {"GOL": 1, "ZAG": 2, "LAT": 2, "VOL": 1, "MEI": 2, "ATA": 3},
    "4-3-3 defensivo":   {"GOL": 1, "ZAG": 2, "LAT": 2, "VOL": 3, "MEI": 0, "ATA": 3},
    "4-2-3-1":           {"GOL": 1, "ZAG": 2, "LAT": 2, "VOL": 2, "MEI": 3, "ATA": 1},
    "4-5-1":             {"GOL": 1, "ZAG": 2, "LAT": 2, "VOL": 1, "MEI": 4, "ATA": 1},
    "4-2-4":             {"GOL": 1, "ZAG": 2, "LAT": 2, "VOL": 2, "MEI": 0, "ATA": 4},
    "4-6-0":             {"GOL": 1, "ZAG": 2, "LAT": 2, "VOL": 2, "MEI": 4, "ATA": 0},
    "4-4-2 sem laterais": {"GOL": 1, "ZAG": 4, "LAT": 0, "VOL": 2, "MEI": 2, "ATA": 2},
    "4-3-3 sem laterais": {"GOL": 1, "ZAG": 4, "LAT": 0, "VOL": 2, "MEI": 1, "ATA": 3},
    # linha de 3
    "3-5-2":             {"GOL": 1, "ZAG": 3, "LAT": 2, "VOL": 2, "MEI": 1, "ATA": 2},
    "3-4-3":             {"GOL": 1, "ZAG": 3, "LAT": 2, "VOL": 2, "MEI": 0, "ATA": 3},
    "3-4-3 sem laterais": {"GOL": 1, "ZAG": 3, "LAT": 0, "VOL": 2, "MEI": 2, "ATA": 3},
    "3-5-2 sem laterais": {"GOL": 1, "ZAG": 3, "LAT": 0, "VOL": 3, "MEI": 2, "ATA": 2},
    # linha de 5
    "5-3-2":             {"GOL": 1, "ZAG": 3, "LAT": 2, "VOL": 3, "MEI": 0, "ATA": 2},
    "5-4-1":             {"GOL": 1, "ZAG": 3, "LAT": 2, "VOL": 2, "MEI": 2, "ATA": 1},
}

# A formacao montada a mao pelo usuario. Uma so por clube: fica guardada em
# c["formacao_custom"] e vale quando c["formacao"] tem este nome.
FORMACAO_PERSONALIZADA = "Personalizada"
# quantos de cada vaga o editor aceita. Mais de dois laterais nao tem onde
# desenhar nem como render: seriam laterais jogando de lateral um do outro.
LIMITES_FORMACAO = {"ZAG": (1, 5), "LAT": (0, 2), "VOL": (0, 4), "MEI": (0, 5), "ATA": (0, 4)}
JOGADORES_DE_LINHA = 10


def contagem_valida(cont: Dict[str, int]) -> Tuple[bool, str]:
    """A contagem cabe no editor? Devolve o motivo quando nao cabe."""
    total = 0
    for pos, (lo, hi) in LIMITES_FORMACAO.items():
        try:
            q = int(cont.get(pos, 0))
        except (TypeError, ValueError):
            return False, "Quantidade invalida para %s." % pos
        if q < lo or q > hi:
            return False, "%s vai de %d a %d." % (pos, lo, hi)
        total += q
    if total != JOGADORES_DE_LINHA:
        return False, "A formacao precisa de %d jogadores de linha, e tem %d." % (
            JOGADORES_DE_LINHA, total)
    return True, ""


def normalizar_contagem(cont: Dict[str, int]) -> Dict[str, int]:
    fora = {"GOL": 1}
    for pos in LIMITES_FORMACAO:
        fora[pos] = int(cont.get(pos, 0))
    return fora


def nome_da_contagem(cont: Dict[str, int]) -> str:
    """3-4-3 a partir da contagem: defesa, meio e ataque, como se fala."""
    return "%d-%d-%d" % (cont.get("ZAG", 0) + cont.get("LAT", 0),
                         cont.get("VOL", 0) + cont.get("MEI", 0), cont.get("ATA", 0))


def formacao_pronta(cont: Dict[str, int]) -> Optional[str]:
    """O nome do esquema pronto com esta contagem, se existir um."""
    alvo = normalizar_contagem(cont)
    for nome, form in FORMACOES.items():
        if all(form.get(p, 0) == alvo[p] for p in POS):
            return nome
    return None


def formacao_de(c: "Clube") -> Dict[str, int]:
    """A contagem por vaga que o clube usa. Unico lugar que le c["formacao"]
    para decidir vagas: a personalizada entra aqui e o resto do motor nem
    percebe a diferenca."""
    if c.get("formacao") == FORMACAO_PERSONALIZADA:
        cont = c.get("formacao_custom") or {}
        if contagem_valida(cont)[0]:
            return normalizar_contagem(cont)
    return FORMACOES.get(c.get("formacao"), FORMACOES["4-4-2"])


def rotulo_formacao(c: "Clube") -> str:
    """Como a formacao aparece para o usuario: a personalizada diz a contagem."""
    if c.get("formacao") == FORMACAO_PERSONALIZADA:
        return "Personalizada (%s)" % nome_da_contagem(formacao_de(c))
    return c.get("formacao") or "4-4-2"

# tatica -> (multiplicador de ataque, multiplicador de defesa)
# Multiplicadores de defesa resolvidos numericamente para que as cinco taticas
# rendam o MESMO contra um adversario equivalente (1.583 pt/jogo). Produto 1.00
# nao serve: no xG ataque e defesa entram simetricos, mas pontos nao sao lineares
# em xG, entao ataque paga mais. Antes disso, Ofensivo ganhava de todas as cinco.
# O que diferencia agora e o matchup e a variancia: Retranca dobra os pontos do
# azarao (1.02 contra 0.51 da Pressao) e Pressao rende mais ao favorito.
# Calibrado para EXP_FORCA = 2.20 -- refazer a conta se o expoente mudar.
TATICAS = {
    "Retranca":        (0.78, 1.417),
    "Contra-ataque":   (0.90, 1.147),
    "Equilibrado":     (1.00, 1.000),
    "Ofensivo":        (1.14, 0.854),
    "Pressao total":   (1.34, 0.710),
}

# desgaste e propensao a cartao por tatica: (fadiga_min, fadiga_max, mult_cartao)
CUSTO_TATICA = {
    "Retranca":        (6, 15, 0.85),
    "Contra-ataque":   (8, 17, 0.95),
    "Equilibrado":     (9, 20, 1.00),
    "Ofensivo":        (11, 22, 1.15),
    "Pressao total":   (13, 26, 1.40),
}

# zagueiro e volante levam mais cartao que atacante; goleiro quase nunca
# Lesao em jogo: chance por jogador a cada 90 minutos, antes de medico, regime
# de treino e fisico. Era 0.026 com lesoes de ate 13 semanas; jogador reclamou
# de departamento medico cheio, e com Copa e continental na mesma semana o
# elenco de quem vai bem joga o dobro. Agora 0.015, e a lesao longa ficou rara.
RISCO_LESAO_JOGO = 0.015
SEMANAS_LESAO = [1, 1, 1, 1, 2, 2, 3, 4, 6, 9]   # sorteio; +1 semana na hora
RISCO_CARTAO = {"GOL": 0.25, "ZAG": 1.25, "LAT": 1.10, "VOL": 1.45, "MEI": 0.95, "ATA": 0.80}
ATT_W = {"GOL": 0.00, "ZAG": 0.06, "LAT": 0.22, "VOL": 0.28, "MEI": 0.85, "ATA": 1.00}
DEF_W = {"GOL": 1.10, "ZAG": 1.00, "LAT": 0.72, "VOL": 0.68, "MEI": 0.22, "ATA": 0.05}
GOL_W = {"GOL": 0.0, "ZAG": 6, "LAT": 5, "VOL": 8, "MEI": 26, "ATA": 55}
ASS_W = {"GOL": 0.0, "ZAG": 4, "LAT": 16, "VOL": 10, "MEI": 40, "ATA": 30}

ELENCO_PADRAO = {"GOL": 3, "ZAG": 5, "LAT": 4, "VOL": 4, "MEI": 5, "ATA": 5}

# receita semanal de TV/patrocinio por divisao: (base, por ponto de reputacao)
TV = {"A": (320_000, 11_500), "B": (170_000, 4_500),
      "C": (120_000, 2_500), "D": (105_000, 1_800), "EX": (0, 0)}

DIVISOES_BR = ("A", "B", "C", "D")


def tem_rebaixamento(div: str) -> bool:
    """Quem cai: as quatro ultimas das Series A, B e C. A D e o fundo do
    sistema e as ligas de fora nao tem acesso nem queda."""
    return div in ("A", "B", "C")

# As ligas de fora sao divisoes como as series: clube com divisao "ENG" joga,
# compra, vende e pode ser treinado. Cada liga tem o seu dinheiro: TV semanal
# (base, por ponto de reputacao; calibrada para saldo semanal pouco acima de
# zero, como nas series), premiacao do campeao, multiplicador do caixa
# inicial, peso no valor de mercado e teto de evolucao dos jogadores.
PERFIL_LIGA_EXT = {
    "ENG": {"tv": (1_750_000, 52_000), "premio": 260_000_000, "caixa": 3.0, "peso": 1.10, "teto": 97},
    "ESP": {"tv": (1_250_000, 47_000), "premio": 180_000_000, "caixa": 2.4, "peso": 1.06, "teto": 97},
    "GER": {"tv": (1_250_000, 47_000), "premio": 170_000_000, "caixa": 2.2, "peso": 1.05, "teto": 96},
    "ITA": {"tv": (1_230_000, 47_000), "premio": 160_000_000, "caixa": 2.0, "peso": 1.04, "teto": 96},
    "FRA": {"tv": (1_000_000, 39_000), "premio": 130_000_000, "caixa": 1.8, "peso": 1.02, "teto": 95},
    "POR": {"tv": (690_000, 35_000), "premio": 50_000_000, "caixa": 1.2, "peso": 0.96, "teto": 92},
    "NED": {"tv": (600_000, 30_000), "premio": 50_000_000, "caixa": 1.2, "peso": 0.95, "teto": 92},
    "USA": {"tv": (830_000, 28_000), "premio": 40_000_000, "caixa": 1.4, "peso": 0.90, "teto": 88},
    "SAU": {"tv": (700_000, 28_000), "premio": 60_000_000, "caixa": 2.5, "peso": 0.88, "teto": 88},
    # America do Sul: bem abaixo da Europa, a Argentina um degrau acima dos vizinhos
    "ARG": {"tv": (300_000, 7_800), "premio": 12_000_000, "caixa": 0.45, "peso": 0.90, "teto": 90},
    "URU": {"tv": (190_000, 5_200), "premio": 4_000_000, "caixa": 0.25, "peso": 0.84, "teto": 86},
    "PAR": {"tv": (200_000, 4_800), "premio": 4_000_000, "caixa": 0.25, "peso": 0.83, "teto": 85},
    "CHI": {"tv": (175_000, 5_000), "premio": 4_500_000, "caixa": 0.28, "peso": 0.84, "teto": 86},
    "COL": {"tv": (230_000, 5_600), "premio": 5_000_000, "caixa": 0.30, "peso": 0.85, "teto": 87},
    "EQU": {"tv": (240_000, 5_300), "premio": 4_500_000, "caixa": 0.28, "peso": 0.84, "teto": 86},
    "PER": {"tv": (155_000, 4_600), "premio": 2_500_000, "caixa": 0.20, "peso": 0.78, "teto": 83},
    "BOL": {"tv": (130_000, 4_400), "premio": 2_000_000, "caixa": 0.18, "peso": 0.76, "teto": 82},
    "VEN": {"tv": (125_000, 4_000), "premio": 2_000_000, "caixa": 0.18, "peso": 0.76, "teto": 82},
}
PERFIL_PADRAO = {"tv": (600_000, 20_000), "premio": 30_000_000, "caixa": 1.0, "peso": 0.9, "teto": 88}


def perfil_liga(div):
    return PERFIL_LIGA_EXT.get(div, PERFIL_PADRAO)


# Quanto a folha de cada liga de fora encolheu com o salario achatado acima de
# 75 (2026-09-28), medido no mundo novo. A receita (e com ela a estrutura, que
# e proporcional) encolhe junto: a margem fica como era. Sem isto o caixa
# mediano da Premier League ia de R$ 180 mi para R$ 3,5 bi em oito anos.
ESCALA_EXT = {"ENG": 0.70, "ESP": 0.70, "GER": 0.76, "ITA": 0.78, "FRA": 0.82, "POR": 0.92,
              "NED": 0.96, "SAU": 0.96, "USA": 0.98, "ARG": 0.97, "URU": 0.95}


def brasileiro(c):
    """Clube das series brasileiras (joga estadual e Copa do Brasil)."""
    return c["divisao"] in DIVISOES_BR


def de_liga_ext(c):
    return c["divisao"] not in DIVISOES_BR and c["divisao"] != "EX"

# premiacao por posicao final (1o lugar), decai conforme a colocacao
PREMIO = {"A": 32_000_000, "B": 6_000_000, "C": 1_800_000, "D": 600_000}

COMPETICOES = ("liga", "copa", "lib", "sul", "estadual", "ext")

# Quanto a diferenca de forca entre dois times se traduz em xG. Com 1.55 os
# elencos (que variam so ~4% entre si na mesma serie) ficavam indistinguiveis e
# o campeonato virava sorteio; 2.20 separa o suficiente sem inflar goleada.
EXP_FORCA = 2.20
# Na Europa a distancia entre grande e pequeno e maior que aqui: com 2.20 o
# City fazia 65 pontos e o LASK ganhava a Champions. So vale para ligas e copas
# europeias; o equilibrio brasileiro fica como estava.
EXP_FORCA_EUROPA = 3.4
COMPS_EUROPA = ("ext", "ucl", "uel")
SEMANAS_LIGA = 38
SEMANAS_COPA = [4, 9, 14, 19, 25, 31]        # Copa do Brasil: 6 fases (64 times)
# Libertadores e Sul-Americana: fase de grupos (8 grupos de 4, ida e volta) e
# depois mata-mata. Na Sul-Americana o 2o do grupo joga um playoff contra o 3o
# da Libertadores; o 1o espera nas oitavas. Final em jogo unico, como antes.
SEMANAS_GRUPOS = [3, 6, 8, 11, 13, 16]       # as 6 rodadas dos grupos
SEMANAS_CONT = [22, 27, 32, 36]              # Libertadores: oitavas ... final
SEMANAS_SULA = [21, 23, 28, 33, 35]          # Sul-Americana: playoff, oitavas ... final
FASES_LIB = ["Oitavas de final", "Quartas de final", "Semifinal", "FINAL"]
FASES_SULA = ["Playoffs das oitavas"] + FASES_LIB
FASE_GRUPOS = "Fase de grupos"
# Champions e Europa League: fase de liga de 36 (8 jogos cada), 1o a 8o direto
# nas oitavas, 9o a 24o no playoff; oitavas, quartas e semi em ida e volta
SEMANAS_FASE_LIGA = [5, 7, 10, 12, 15, 17, 20, 23]
SEMANAS_EURO = [26, 29, 32, 35, 37]
FASE_LIGA = "Fase de liga"
# Copas nacionais de fora: em segundo plano, jogo unico, com os clubes da liga
# (os 16 ou 8 de maior reputacao). Semanas livres das copas continentais.
COPAS_NACIONAIS = {
    "ENG": "FA Cup", "ESP": "Copa del Rey", "GER": "DFB-Pokal", "ITA": "Coppa Italia",
    "FRA": "Coupe de France", "POR": "Taca de Portugal", "NED": "KNVB Beker",
    "USA": "US Open Cup", "SAU": "King's Cup", "ARG": "Copa Argentina", "URU": "Copa AUF Uruguay",
    "PAR": "Copa Paraguay", "CHI": "Copa Chile", "COL": "Copa Colombia", "EQU": "Copa Ecuador",
    "PER": "Copa Bicentenario", "BOL": "Copa Bolivia", "VEN": "Copa Venezuela",
}
# calendario por pais, em grupos, para as estreias nao cairem todas na mesma
# semana (80 jogos a mais numa semana so passava do limite de tempo)
_CN16 = {"A": [9, 18, 25, 34], "B": [2, 19, 30, 38], "C": [4, 14, 24, 31]}
_CN8 = {"A": [1, 18, 30], "B": [14, 25, 34]}
# Supercopas: campeao contra campeao, com os titulos do ano anterior. A do
# Brasil e a Recopa caem no estadual (rodada do estadual, semana_est); a da
# UEFA e as nacionais de fora, na primeira semana da liga.
SUPERCOPA_BR_EST = 2          # rodada do estadual da Supercopa do Brasil
RECOPA_EST = 3                # e da Recopa (ida e volta na mesma semana)
SEMANA_SUPERCOPAS = 1
SUPERCOPAS_NACIONAIS = {
    "ENG": "Community Shield", "ESP": "Supercopa da Espanha", "GER": "DFL-Supercup",
    "ITA": "Supercoppa Italiana", "FRA": "Trophee des Champions", "POR": "Supertaca Candido de Oliveira",
    "NED": "Johan Cruijff Schaal", "SAU": "Supercopa Saudita", "ARG": "Supercopa Argentina",
    "URU": "Supercopa Uruguaya", "PAR": "Supercopa Paraguay", "CHI": "Supercopa de Chile",
    "COL": "Superliga Colombiana", "EQU": "Supercopa do Equador", "PER": "Supercopa Peruana",
    "BOL": "Supercopa Boliviana", "VEN": "Supercopa Venezuelana",
}
# Copa Intercontinental, todo ano, logo depois das finais: o campeao da
# Libertadores pega o melhor da MLS (Derby das Americas) e quem passa decide com
# o campeao da Champions. Campo neutro, jogo unico.
SEMANAS_INTERCONTINENTAL = [37, 38]
FASES_INTERCONTINENTAL = ["Derby das Americas", "FINAL"]
# Mundial de Clubes de 32, a cada 4 anos (o de 2025 ja foi): 8 grupos de 4 em
# turno unico e mata-mata em jogo unico, tudo em campo neutro, nas semanas
# livres das copas continentais.
ANO_MUNDIAL = 2029
SEMANAS_MUNDIAL_GRUPOS = [18, 19, 24]
SEMANAS_MUNDIAL = [25, 30, 31, 34]
VAGAS_MUNDIAL = (("europeu", 14), ("conmebol", 8), ("USA", 5), ("SAU", 5))
SEMANAS_COPA_NAC = {
    16: {"ENG": _CN16["A"], "ESP": _CN16["A"], "GER": _CN16["A"], "ITA": _CN16["A"],
         "FRA": _CN16["B"], "POR": _CN16["B"], "NED": _CN16["B"],
         "USA": _CN16["C"], "SAU": _CN16["C"], "ARG": _CN16["C"]},
    8: {"URU": _CN8["A"], "PAR": _CN8["A"], "CHI": _CN8["A"], "COL": _CN8["A"],
        "EQU": _CN8["B"], "PER": _CN8["B"], "BOL": _CN8["B"], "VEN": _CN8["B"]},
}


def semanas_copa_nac(codigo: str, n: int) -> List[int]:
    return list(SEMANAS_COPA_NAC[n].get(codigo) or (_CN16["A"] if n == 16 else _CN8["B"]))
# ordem de forca das ligas: desempata vaga e completa as copas
ORDEM_LIGAS_EXT = ["ENG", "ESP", "GER", "ITA", "FRA", "POR", "NED"]
VAGAS_CHAMPIONS = {"ENG": 4, "ESP": 4, "GER": 4, "ITA": 4, "FRA": 3, "POR": 2, "NED": 2}
# o que cada vitoria na fase de grupos paga a um clube brasileiro
PREMIO_VITORIA_GRUPO = {"lib": 1_800_000, "sul": 900_000, "ucl": 12_000_000, "uel": 4_000_000,
                        "mundial": 6_000_000}
JANELAS = list(range(1, 5)) + list(range(19, 23))   # semanas com mercado aberto

# ----------------------------------------------------------------------------
# BANCO DE CLUBES  (nome, UF, estadio, capacidade, reputacao)
# ----------------------------------------------------------------------------

CLUBES_A = [
    ("Flamengo", "RJ", "Maracana", 78838, 92),
    ("Palmeiras", "SP", "Allianz Parque", 43713, 91),
    ("Botafogo", "RJ", "Nilton Santos", 44661, 86),
    ("Sao Paulo", "SP", "Morumbi", 66795, 85),
    ("Corinthians", "SP", "Neo Quimica Arena", 49205, 85),
    ("Atletico-MG", "MG", "Arena MRV", 46000, 83),
    ("Internacional", "RS", "Beira-Rio", 50128, 82),
    ("Gremio", "RS", "Arena do Gremio", 55225, 82),
    ("Cruzeiro", "MG", "Mineirao", 61846, 82),
    ("Fluminense", "RJ", "Maracana", 78838, 81),
    ("Bahia", "BA", "Arena Fonte Nova", 47907, 79),
    ("Vasco da Gama", "RJ", "Sao Januario", 21880, 78),
    ("Santos", "SP", "Vila Belmiro", 16068, 77),
    ("Fortaleza", "CE", "Castelao", 63903, 76),
    ("Red Bull Bragantino", "SP", "Nabi Abi Chedid", 17724, 72),
    ("Ceara", "CE", "Castelao", 63903, 70),
    ("Sport", "PE", "Ilha do Retiro", 26418, 69),
    ("Vitoria", "BA", "Barradao", 30618, 67),
    ("Juventude", "RS", "Alfredo Jaconi", 19924, 63),
    ("Mirassol", "SP", "Campos Maia", 15000, 61),
]

CLUBES_B = [
    ("Athletico-PR", "PR", "Ligga Arena", 42372, 72),
    ("Coritiba", "PR", "Couto Pereira", 40502, 66),
    ("Goias", "GO", "Serrinha", 14525, 62),
    ("America-MG", "MG", "Independencia", 23018, 61),
    ("Atletico-GO", "GO", "Antonio Accioly", 12500, 60),
    ("Cuiaba", "MT", "Arena Pantanal", 44097, 58),
    ("Criciuma", "SC", "Heriberto Hulse", 19300, 56),
    ("Chapecoense", "SC", "Arena Conda", 22600, 55),
    ("Avai", "SC", "Ressacada", 17800, 54),
    ("Paysandu", "PA", "Curuzu", 16200, 54),
    ("Remo", "PA", "Baenao", 13000, 53),
    ("Vila Nova", "GO", "OBA", 14525, 52),
    ("CRB", "AL", "Rei Pele", 17126, 52),
    ("Novorizontino", "SP", "Jorge Ismael de Biasi", 17000, 51),
    ("Operario-PR", "PR", "Germano Kruger", 10632, 48),
    ("Amazonas", "AM", "Arena da Amazonia", 44300, 47),
    ("Ferroviaria", "SP", "Fonte Luminosa", 18000, 46),
    ("Botafogo-SP", "SP", "Santa Cruz", 30000, 46),
    ("Volta Redonda", "RJ", "Raulino de Oliveira", 17000, 44),
    ("Athletic", "MG", "Joaquim Portugal", 3000, 43),
]

CLUBES_C = [
    ("Nautico", "PE", "Aflitos", 22500, 48),
    ("Ponte Preta", "SP", "Moises Lucarelli", 17728, 47),
    ("Guarani", "SP", "Brinco de Ouro", 29498, 46),
    ("ABC", "RN", "Frasqueirao", 18000, 44),
    ("Figueirense", "SC", "Orlando Scarpelli", 19584, 43),
    ("Londrina", "PR", "Cafe", 30000, 42),
    ("CSA", "AL", "Rei Pele", 17126, 42),
    ("Sampaio Correa", "MA", "Castelao-MA", 40000, 41),
    ("Ituano", "SP", "Novelli Junior", 18560, 40),
    ("Sao Bernardo", "SP", "1o de Maio", 15000, 39),
    ("Botafogo-PB", "PB", "Almeidao", 30000, 39),
    ("Brusque", "SC", "Augusto Bauer", 5000, 38),
    ("Confianca", "SE", "Batistao", 15300, 37),
    ("Tombense", "MG", "Almeidao-MG", 5000, 36),
    ("Ypiranga", "RS", "Colosso da Lagoa", 5000, 36),
    ("Maringa", "PR", "Willie Davids", 12000, 35),
    ("Floresta", "CE", "Domingao", 12000, 34),
    ("Retro", "PE", "Arena de Pernambuco", 44300, 34),
    ("Itabaiana", "SE", "Mendoncao", 8000, 33),
    ("Anapolis", "GO", "Jonas Duarte", 15000, 32),
]

CLUBES_D = [
    ("Portuguesa", "SP", "Caninde", 21000, 38),
    ("Santa Cruz", "PE", "Arruda", 60044, 40),
    ("America-RN", "RN", "Arena das Dunas", 31375, 36),
    ("Joinville", "SC", "Arena Joinville", 22400, 33),
    ("Caxias", "RS", "Centenario", 22132, 33),
    ("Brasil de Pelotas", "RS", "Bento Freitas", 12000, 31),
    ("Sao Jose-RS", "RS", "Passo Dareia", 10000, 30),
    ("Ferroviario", "CE", "Presidente Vargas", 20000, 31),
    ("Treze", "PB", "Amigao", 18000, 30),
    ("Campinense", "PB", "Amigao", 18000, 30),
    ("Cascavel", "PR", "Olimpico Regional", 20000, 29),
    ("Nova Iguacu", "RJ", "Laranjao", 3000, 29),
    ("Boavista", "RJ", "Elcyr Resende", 5000, 28),
    ("Marcilio Dias", "SC", "Hercilio Luz", 6000, 27),
    ("Aguia de Maraba", "PA", "Zinho Oliveira", 9000, 27),
    ("Sergipe", "SE", "Batistao", 15300, 26),
    ("Central", "PE", "Lacerdao", 20000, 26),
    ("Altos", "PI", "Felipe Zovaro", 4000, 25),
    ("Aparecidense", "GO", "Anibal Batista", 3000, 24),
    ("Porto Velho", "RO", "Aluizao", 20000, 23),
]

CLUBES_LIB = [
    ("River Plate", "ARG", "Monumental", 83214, 88),
    ("Boca Juniors", "ARG", "Bombonera", 54000, 87),
    ("Racing", "ARG", "Cilindro", 55000, 80),
    ("Independiente", "ARG", "Libertadores de America", 48069, 76),
    ("Velez Sarsfield", "ARG", "Jose Amalfitani", 49540, 76),
    ("Estudiantes", "ARG", "Uno", 30018, 74),
    ("Talleres", "ARG", "Mario Kempes", 57000, 73),
    ("San Lorenzo", "ARG", "Pedro Bidegain", 47964, 72),
    ("Nacional", "URU", "Gran Parque Central", 34000, 78),
    ("Penarol", "URU", "Campeon del Siglo", 40005, 78),
    ("Colo-Colo", "CHI", "Monumental David Arellano", 47347, 77),
    ("Universidad de Chile", "CHI", "Nacional de Chile", 48665, 74),
    ("Universidad Catolica", "CHI", "San Carlos de Apoquindo", 20000, 72),
    ("Olimpia", "PAR", "Defensores del Chaco", 42354, 76),
    ("Cerro Porteno", "PAR", "La Nueva Olla", 45000, 75),
    ("Libertad", "PAR", "La Huerta", 12000, 72),
    ("Atletico Nacional", "COL", "Atanasio Girardot", 40043, 78),
    ("Millonarios", "COL", "El Campin", 36343, 73),
    ("Junior", "COL", "Metropolitano", 46692, 72),
    ("Independiente del Valle", "EQU", "Banco Guayaquil", 12000, 77),
    ("LDU Quito", "EQU", "Rodrigo Paz", 41575, 76),
    ("Barcelona SC", "EQU", "Monumental Banco Pichincha", 57267, 74),
    ("Alianza Lima", "PER", "Matute", 35000, 70),
    ("Bolivar", "BOL", "Hernando Siles", 41143, 70),
]

CLUBES_SUL = [
    ("Lanus", "ARG", "La Fortaleza", 47027, 69),
    ("Defensa y Justicia", "ARG", "Norberto Tomaghello", 18000, 67),
    ("Huracan", "ARG", "Tomas Duco", 48314, 66),
    ("Danubio", "URU", "Jardines del Hipodromo", 18000, 62),
    ("Deportivo Cali", "COL", "Palmaseca", 52000, 66),
    ("Always Ready", "BOL", "Municipal de El Alto", 25000, 61),
    ("Sporting Cristal", "PER", "Alberto Gallardo", 18000, 67),
    ("The Strongest", "BOL", "Hernando Siles", 41143, 63),
    # a Sul-Americana tem 32 clubes na fase de grupos: 24 de fora e 8 daqui
    ("Argentinos Juniors", "ARG", "Diego Armando Maradona", 26000, 68),
    ("Belgrano", "ARG", "Gigante de Alberdi", 38000, 66),
    ("Newell's Old Boys", "ARG", "Marcelo Bielsa", 42000, 67),
    ("Rosario Central", "ARG", "Gigante de Arroyito", 41654, 68),
    ("Defensor Sporting", "URU", "Luis Franzini", 18000, 60),
    ("Liverpool Montevideo", "URU", "Belvedere", 10000, 58),
    ("Coquimbo Unido", "CHI", "Francisco Sanchez Rumoroso", 18750, 58),
    ("Audax Italiano", "CHI", "Bicentenario La Florida", 12000, 57),
    ("America de Cali", "COL", "Pascual Guerrero", 38000, 65),
    ("Once Caldas", "COL", "Palogrande", 28000, 63),
    ("Club Guarani", "PAR", "Rogelio Livieres", 6000, 58),
    ("Nacional Asuncion", "PAR", "Arsenio Erico", 4000, 57),
    ("Aucas", "EQU", "Gonzalo Pozo Ripalda", 18800, 59),
    ("El Nacional", "EQU", "Olimpico Atahualpa", 35000, 58),
    ("Melgar", "PER", "Monumental UNSA", 60000, 61),
    ("Cienciano", "PER", "Inca Garcilaso", 45000, 60),
]

# ----------------------------------------------------------------------------
# LIGAS SUL-AMERICANAS
#
# Os clubes de CLUBES_LIB, CLUBES_SUL e os sul-americanos do dados_mundo.py
# entram na liga do pais; os que faltam para fechar a liga vem daqui, com nome
# real e elenco gerado pela reputacao. As vagas da Libertadores e da
# Sul-Americana saem da classificacao de cada liga no ano anterior.
# ----------------------------------------------------------------------------

# codigo (= pais), nome da liga, numero de clubes
LIGAS_SUL = [
    ("ARG", "Liga Profesional Argentina", 20),
    ("URU", "Campeonato Uruguaio", 10),
    ("PAR", "Campeonato Paraguaio", 10),
    ("CHI", "Campeonato Chileno", 12),
    ("COL", "Liga Colombiana", 12),
    ("EQU", "LigaPro Equatoriana", 10),
    ("PER", "Liga 1 Peruana", 10),
    ("BOL", "Campeonato Boliviano", 10),
    ("VEN", "Liga Venezuelana", 10),
]
CODIGOS_SUL = [k for k, _, _ in LIGAS_SUL]
# 24 vagas de fora em cada copa (as outras 8 sao brasileiras)
VAGAS_LIB = {"ARG": 5, "URU": 3, "PAR": 3, "CHI": 3, "COL": 3, "EQU": 3, "PER": 2, "BOL": 1, "VEN": 1}
VAGAS_SULA = {"ARG": 4, "URU": 3, "PAR": 3, "CHI": 3, "COL": 3, "EQU": 3, "PER": 2, "BOL": 2, "VEN": 1}

# na ordem em que entram, ate a liga fechar o numero de clubes
CLUBES_LIGAS_SUL = {
    "ARG": [("Godoy Cruz", "ARG", "Malvinas Argentinas", 42000, 64),
            ("Gimnasia La Plata", "ARG", "Juan Carmelo Zerillo", 24544, 63),
            ("Banfield", "ARG", "Florencio Sola", 34901, 62),
            ("Union de Santa Fe", "ARG", "15 de Abril", 22852, 62),
            ("Tigre", "ARG", "Jose Dellagiovanna", 26282, 61)],
    "URU": [("Montevideo Wanderers", "URU", "Parque Alfredo Viera", 7420, 57),
            ("Cerro Largo", "URU", "Antonio Ubilla", 9000, 54),
            ("Plaza Colonia", "URU", "Profesor Alberto Suppici", 12000, 53),
            ("Racing Montevideo", "URU", "Parque Roberto", 8500, 53),
            ("Progreso", "URU", "Parque Abraham Paladino", 8000, 52),
            ("Fenix", "URU", "Parque Capurro", 5500, 52)],
    "PAR": [("Sportivo Luqueno", "PAR", "Feliciano Caceres", 24000, 55),
            ("Sportivo Trinidense", "PAR", "Martin Torres", 3000, 52),
            ("Tacuary", "PAR", "Roberto Bettega", 3000, 51),
            ("Sportivo Ameliano", "PAR", "Jose Tomas Silva", 3000, 51),
            ("General Caballero", "PAR", "Ka'arendy", 8000, 51),
            ("Sportivo San Lorenzo", "PAR", "Gunther Vogel", 5000, 50)],
    "CHI": [("Palestino", "CHI", "Municipal de La Cisterna", 12000, 58),
            ("Everton de Vina", "CHI", "Sausalito", 22360, 57),
            ("Union Espanola", "CHI", "Santa Laura", 19887, 57),
            ("Cobresal", "CHI", "El Cobre", 12000, 55),
            ("Nublense", "CHI", "Nelson Oyarzun", 12000, 55),
            ("Union La Calera", "CHI", "Nicolas Chahuan", 9200, 55),
            ("Deportes Iquique", "CHI", "Tierra de Campeones", 13171, 54)],
    "COL": [("Independiente Medellin", "COL", "Atanasio Girardot", 40043, 64),
            ("Atletico Bucaramanga", "COL", "Alfonso Lopez", 25000, 61),
            ("Deportivo Pereira", "COL", "Hernan Ramirez Villegas", 30297, 59),
            ("Envigado", "COL", "Polideportivo Sur", 11000, 55),
            ("Deportivo Pasto", "COL", "Departamental Libertad", 20665, 55),
            ("Alianza FC", "COL", "Armando Maestre", 11000, 54)],
    "EQU": [("Emelec", "EQU", "George Capwell", 40020, 66),
            ("Catolica del Ecuador", "EQU", "Olimpico Atahualpa", 35258, 58),
            ("Delfin", "EQU", "Jocay", 17000, 58),
            ("Orense", "EQU", "9 de Mayo", 16500, 56),
            ("Deportivo Cuenca", "EQU", "Alejandro Serrano Aguilar", 16500, 56),
            ("Mushuc Runa", "EQU", "Mushuc Runa", 8200, 54),
            ("Tecnico Universitario", "EQU", "Bellavista", 16467, 53)],
    "PER": [("Sport Huancayo", "PER", "Huancayo", 20000, 55),
            ("Deportivo Garcilaso", "PER", "Garcilaso", 45000, 54),
            ("ADT", "PER", "Union Tarma", 9000, 53),
            ("Alianza Atletico", "PER", "Campeones del 36", 8000, 52),
            ("Atletico Grau", "PER", "Miguel Grau", 25000, 52),
            ("Comerciantes Unidos", "PER", "Juan Maldonado Gamarra", 5000, 51),
            ("UTC", "PER", "Heroes de San Ramon", 18000, 51)],
    "BOL": [("Blooming", "BOL", "Ramon Tahuichi Aguilera", 38000, 57),
            ("Oriente Petrolero", "BOL", "Ramon Tahuichi Aguilera", 38000, 57),
            ("Jorge Wilstermann", "BOL", "Felix Capriles", 32000, 57),
            ("San Antonio Bulo Bulo", "BOL", "Carlos Villegas", 6000, 53),
            ("Aurora", "BOL", "Felix Capriles", 32000, 52),
            ("Real Tomayapo", "BOL", "IV Centenario", 15000, 51),
            ("Guabira", "BOL", "Gilberto Parada", 13000, 51),
            ("Universitario de Vinto", "BOL", "Municipal de Vinto", 5000, 50)],
    "VEN": [("Caracas FC", "VEN", "Olimpico de la UCV", 23940, 58),
            ("Monagas", "VEN", "Monumental de Maturin", 51796, 55),
            ("Estudiantes de Merida", "VEN", "Metropolitano de Merida", 42200, 54),
            ("Zamora", "VEN", "Agustin Tovar", 29800, 53),
            ("Metropolitanos", "VEN", "Olimpico de la UCV", 23940, 53),
            ("Portuguesa FC", "VEN", "Jose Antonio Paez", 18000, 52),
            ("Rayo Zuliano", "VEN", "Pachencho Romero", 40800, 51),
            ("Academia Puerto Cabello", "VEN", "Complejo Socialista", 7500, 51)],
}


# ----------------------------------------------------------------------------
# GERADOR DE NOMES
# ----------------------------------------------------------------------------

PRIMEIROS = """Gabriel Lucas Matheus Pedro Rafael Bruno Vinicius Thiago Felipe Rodrigo
Guilherme Eduardo Leonardo Andre Marcelo Caio Diego Igor Renato Everton Wesley
Douglas Fernando Ricardo Alisson Danilo Emerson Fabricio Geraldo Hugo Ian Jean
Kaique Luan Murilo Nathan Otavio Patrick Quesley Raul Samuel Tales Ubiratan Victor
Walace Yuri Zeca Adriano Alan Alex Arthur Breno Cleiton Cristian Denilson Deyverson
Edinho Elias Fabio Gilberto Helio Italo Jadson Joao Juninho Kevin Lincoln Lucca
Maicon Michel Nicolas Osvaldo Paulinho Reinaldo Robson Ruan Sandro Sidney Tiago
Uilson Valter Wanderson Washington Wellington Willian Yan Anderson Bernardo Carlos
Cesar Daniel David Erick Evandro Fabinho Gustavo Henrique Jonas Jorge Julio Kaio
Leandro Lucio Marcos Mateus Nilton Pablo Renan Ronaldo Sergio Vitor""".split()

SOBRENOMES = """Silva Santos Oliveira Souza Lima Pereira Ferreira Alves Rodrigues Costa
Gomes Martins Araujo Ribeiro Carvalho Barbosa Rocha Dias Nascimento Moreira Cardoso
Teixeira Correia Cunha Pinto Moraes Freitas Campos Monteiro Machado Miranda Andrade
Nogueira Vieira Ramos Azevedo Batista Duarte Fonseca Guimaraes Lopes Macedo Nunes
Pacheco Queiroz Rezende Sampaio Tavares Vasconcelos Xavier Bastos Camargo Sales
Fagundes Galvao Marques Mendes Peixoto Salgado Bezerra Caldeira Furtado Assuncao
Braga Dantas Estevao Faria Godoy Leal Maia Neves Prado Reis Sa Torres Valente""".split()

APELIDOS = """Tiquinho Nenem Careca Zinho Pituca Caju Serginho Dedeco Bolinha Piriquito
Lelo Baiano Gaucho Mineiro Paulinho Cebola Pantera Formiga Gaguinho Nego Tito Bambam
Fumaca Chulapa Jacare Tatu Rasta Piolho Ronaldinho Careta Vava Zico Kiko Pitbull
Furacao Trovao Pelezinho Kaka Dudu Yaya Lolo Bibi Kadu Cacau Chocolate Foguinho""".split()


# ----------------------------------------------------------------------------
# UTILITARIOS
# ----------------------------------------------------------------------------

def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def din(v):
    """Formata dinheiro em reais de forma curta, em pt-BR: "R$ 37,6 mi",
    "R$ 764 mil", "-R$ 5,4 bi". Formatador unico: tela, noticia e terminal
    escrevem dinheiro por aqui (a web tem o espelho em web/src/formato.ts)."""
    v = float(v)
    s = "-" if v < 0 else ""
    v = abs(v)
    if v >= 1_000_000_000:
        return "%sR$ %s bi" % (s, ("%.1f" % (v / 1_000_000_000)).replace(".", ","))
    if v >= 1_000_000:
        return "%sR$ %s mi" % (s, ("%.1f" % (v / 1_000_000)).replace(".", ","))
    if v >= 100_000:
        return "%sR$ %.0f mil" % (s, v / 1_000)
    # abaixo de cem mil o arredondamento mentiria: R$ 3.500 viraria "R$ 4 mil"
    return "%sR$ %s" % (s, "{:,.0f}".format(v).replace(",", "."))


def plural(n, singular, plural_=None):
    """"1 ano", "3 anos", "2 jogadores". Nunca "ano(s)"."""
    return "%d %s" % (n, singular if n == 1 else (plural_ or singular + "s"))


def poisson(lmbda):
    lmbda = max(0.05, min(6.0, lmbda))
    L = exp(-lmbda)
    k, p = 0, 1.0
    while True:
        p *= rng.random()
        if p <= L:
            return k
        k += 1
        if k > 12:
            return k


def linha(c="-", n=78):
    return c * n


def pausa(G):
    if G.get("auto"):
        return
    try:
        input("\n[enter] ")
    except EOFError:
        G["auto"] = True


def ler(txt, G=None):
    try:
        return input(txt).strip()
    except EOFError:
        if G is not None:
            G["auto"] = True
        return ""


def ler_int(txt, G=None, minimo=None, maximo=None):
    s = ler(txt, G)
    try:
        v = int(s.replace(".", "").replace(",", ""))
    except ValueError:
        return None
    if minimo is not None and v < minimo:
        return None
    if maximo is not None and v > maximo:
        return None
    return v


def gerar_nome(usados):
    for _ in range(80):
        r = rng.random()
        if r < 0.20:
            n = rng.choice(APELIDOS)
        elif r < 0.40:
            n = rng.choice(PRIMEIROS)
        else:
            n = "%s %s" % (rng.choice(PRIMEIROS), rng.choice(SOBRENOMES))
        if n not in usados:
            usados.add(n)
            return n
    n = "%s %s %s" % (rng.choice(PRIMEIROS), rng.choice(SOBRENOMES), rng.choice(SOBRENOMES))
    usados.add(n)
    return n


def _curva_mercado(ovr):
    """A curva antiga, que dobra a cada ~5 de overall. Segue valendo para o
    valor do passe (valor_de): o que ficou mais barato foi o salario."""
    return max(8_000, 1500 * (1.16 ** (ovr - 40)))


SALARIO_JOELHO = 75       # ate este overall o salario segue a curva de mercado
SALARIO_CRESCE = 1.068    # acima dele, cada ponto a mais custa 6,8% (antes 16%)


def salario_de(ovr):
    """Salario mensal de mercado pelo overall. Achatado acima de 75 (decidido
    em 2026-09-28): 80 = ~R$ 375 mil, 85 = ~R$ 520 mil, 90 = ~R$ 720 mil. Antes
    90 pedia R$ 2,5 mi e um craque livre levava ate 46% da folha do Santos."""
    if ovr <= SALARIO_JOELHO:
        return int(_curva_mercado(ovr))
    return int(_curva_mercado(SALARIO_JOELHO) * SALARIO_CRESCE ** (ovr - SALARIO_JOELHO))


def fator_idade(idade):
    if idade <= 20:
        return 1.45
    if idade <= 23:
        return 1.35
    if idade <= 26:
        return 1.20
    if idade <= 29:
        return 1.00
    if idade <= 31:
        return 0.72
    if idade <= 33:
        return 0.48
    return 0.25


def valor_de(ovr, idade, pot):
    base = _curva_mercado(ovr) * 30.0
    base *= fator_idade(idade)
    base *= 1.0 + max(0, pot - ovr) * 0.035
    return int(base / 1000) * 1000


def valor_jogador(j) -> int:
    """valor_de mais a vitrine do ultimo premio do ano (premio_valor, que
    dura ate a proxima virada)."""
    v = valor_de(j["ovr"], j["idade"], j["pot"])
    bonus = float(j.get("premio_valor", 0.0))
    return int(v * (1.0 + bonus) / 1000) * 1000 if bonus else v


# ----------------------------------------------------------------------------
# CRIACAO DO MUNDO
# ----------------------------------------------------------------------------

def novo_jogador(G, pos, nivel, usados, idade=None):
    G["seq"] += 1
    pid = G["seq"]
    if idade is None:
        idade = rng.choices(
            [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
            weights=[2, 4, 6, 8, 9, 10, 10, 10, 9, 9, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1])[0]
    ovr = int(round(rng.gauss(nivel, 4.5)))
    if rng.random() < 0.06:
        ovr += rng.randint(4, 9)
    if idade <= 20:
        ovr -= rng.randint(3, 9)
    elif idade >= 33:
        ovr -= rng.randint(0, 4)
    ovr = clamp(ovr, 28, 93)
    teto = sortear_potencial(ovr, idade, clamp((nivel - 40) / 45.0, 0.0, 1.0))
    j = {
        "id": pid, "nome": gerar_nome(usados), "pos": pos, "idade": idade,
        "ovr": ovr, "pot": teto, "cond": rng.randint(88, 100),
        "forma": rng.randint(45, 70), "moral": rng.randint(55, 80),
        "lesao": 0, "amarelos": 0, "suspensao": 0,
        "amar": {k: 0 for k in COMPETICOES}, "susp": {k: 0 for k in COMPETICOES},
        "contrato": rng.randint(1, 4), "salario": salario_de(ovr),
        "valor": valor_de(ovr, idade, teto), "clube": None, "listado": 0,
        "dono": None, "emp_pct": 100, "emp_listado": 0, "emp_opcao": 0,
        "pago": 0, "desde": 0, "ovr_frac": 0.0, "j_mes": 0,
        "j": 0, "g": 0, "a": 0, "ca": 0, "cv": 0, "nota_soma": 0.0, "nota_j": 0,
        "car_j": 0, "car_g": 0, "car_tit": 0,
        "categoria": "pro", "g_mes": 0, "a_mes": 0, "ovr_ini": ovr, "pot_rev": 0,
    }
    G["jogadores"][pid] = j
    return j


def novo_clube(G, dados, divisao, usados):
    nome, uf, estadio, cap, rep = dados
    G["seq_c"] += 1
    cid = G["seq_c"]
    mult = {"A": 1.0, "B": 0.40, "C": 0.16, "D": 0.07, "EX": 1.0}.get(divisao) or perfil_liga(divisao)["caixa"]
    c = {
        "id": cid, "nome": nome, "uf": uf, "estadio": estadio, "capacidade": cap,
        "reputacao": rep, "divisao": divisao,
        "dinheiro": int(rep * rep * 3800 * mult) + rng.randint(500_000, 3_000_000),
        "preco": int(clamp(rep * 0.9, 12, 95)),
        "ct": clamp(int(rep / 12), 1, 8), "base": clamp(int(rep / 13), 1, 8),
        "medico": clamp(int(rep / 13), 1, 8),
        "obra_lugares": 0, "obra_semanas": 0,
        "formacao": "4-4-2", "tatica": "Equilibrado", "auto_esc": True,
        "elenco": [], "escalacao": [], "emprestados": [], "esc_stamp": "", "titulos": {},
        "base_elenco": [], "treino": REGIME_PADRAO, "treino_foco": [],
        "plano": dict(PLANO_PADRAO),
        "socios": int(cap * rng.uniform(0.15, 0.55)),
    }
    nivel = 26 + rep * 0.58
    for pos, qtd in ELENCO_PADRAO.items():
        for _ in range(qtd):
            j = novo_jogador(G, pos, nivel + rng.uniform(-2, 2), usados)
            j["clube"] = cid
            c["elenco"].append(j["id"])
    G["clubes"][cid] = c
    return c


def trocar_elenco(G, c, lista, usados):
    """Poe no clube os jogadores da lista ({nome, pos, idade, ovr, pot}) no lugar
    dos gerados. Devolve quantos reservas precisou gerar para fechar posicao."""
    for pid in list(c["elenco"]):
        G["jogadores"].pop(pid, None)
    c["elenco"] = []
    nivel = 26 + c["reputacao"] * 0.58
    for item in lista:
        pos = str(item.get("pos", "MEI")).upper()
        if pos not in POS:
            pos = "MEI"
        j = novo_jogador(G, pos, nivel, usados, idade=item.get("idade"))
        if item.get("nome"):
            j["nome"] = str(item["nome"])
        if item.get("ovr"):
            j["ovr"] = clamp(int(item["ovr"]), 20, 95)
            j["pot"] = clamp(int(item.get("pot", j["ovr"] + 4)), j["ovr"], 95)
            j["salario"] = salario_de(j["ovr"])
            j["valor"] = valor_jogador(j)
        j["clube"] = c["id"]
        c["elenco"].append(j["id"])
    return completar_minimo(G, c, usados, nivel)


def aplicar_elencos_reais(G, usados):
    """Se existir elencos.json na pasta, usa aqueles jogadores no lugar dos gerados.

    Formato:
    {"Flamengo": [{"nome": "Fulano", "pos": "ATA", "idade": 27, "ovr": 84}, ...], ...}
    Clubes que nao estiverem no arquivo continuam com elenco gerado.
    """
    dados, origem = None, ""
    if os.path.exists(ARQ_ELENCOS):
        try:
            with open(ARQ_ELENCOS, encoding="utf-8") as f:
                dados = json.load(f)
            origem = "elencos.json da pasta"
        except Exception as e:
            print("Nao consegui ler %s (%s). Vou usar os elencos embutidos." %
                  (ARQ_ELENCOS, e))
            dados = None
    if dados is None:
        try:
            dados = json.loads(zlib.decompress(base64.b64decode(ELENCOS_EMBUTIDOS)).decode("utf-8"))
            origem = "elencos embutidos no programa"
        except Exception:
            return
    if not isinstance(dados, dict):
        return
    por_nome = {c["nome"].lower(): c for c in G["clubes"].values()}
    importados = set()
    trocados = completados = 0
    for nome_clube, lista in dados.items():
        c = por_nome.get(str(nome_clube).lower())
        if not c or not isinstance(lista, list) or not lista:
            continue
        completados += trocar_elenco(G, c, lista, usados)
        importados.add(c["id"])
        trocados += 1
    if trocados:
        print("Elencos reais de %s carregados (%s)." % (plural(trocados, "clube"), origem))
    if completados:
        print("%s de reserva gerados para fechar buracos de posicao." % plural(completados, "jogador", "jogadores"))
    if trocados >= 5:
        ajustados = recalibrar_gerados(G, importados)
        if ajustados:
            print("%s sem elenco no arquivo nivelados pela curva do seu arquivo."
                  % plural(ajustados, "clube"))


def recalibrar_gerados(G, importados):
    """Deixa os clubes gerados na mesma escala de forca dos elencos importados.

    Ajusta uma reta media_do_elenco x reputacao com os clubes que vieram do arquivo e
    desloca o overall dos demais para caberem nessa mesma curva.
    """
    pontos = [(G["clubes"][i]["reputacao"], media_elenco(G, G["clubes"][i])) for i in importados]
    pontos = [p for p in pontos if p[1] > 0]
    if len(pontos) < 5:
        return 0
    n = len(pontos)
    mx = sum(p[0] for p in pontos) / n
    my = sum(p[1] for p in pontos) / n
    var = sum((p[0] - mx) ** 2 for p in pontos)
    if var <= 0:
        return 0
    inc = sum((p[0] - mx) * (p[1] - my) for p in pontos) / var
    base = my - inc * mx
    ajustados = 0
    for c in G["clubes"].values():
        if c["id"] in importados or not c["elenco"]:
            continue
        alvo = base + inc * c["reputacao"]
        delta = int(round(clamp(alvo - media_elenco(G, c), -5, 5)))
        if delta == 0:
            continue
        for p in c["elenco"]:
            j = G["jogadores"][p]
            j["ovr"] = int(clamp(j["ovr"] + delta, 20, 95))
            j["pot"] = int(clamp(max(j["pot"] + delta, j["ovr"]), j["ovr"], 95))
            j["salario"] = salario_de(j["ovr"])
            j["valor"] = valor_jogador(j)
        ajustados += 1
    return ajustados


def completar_minimo(G, c, usados, nivel):
    """Rede de seguranca: garante 1 goleiro, 1 de cada posicao e 14 jogadores no total.

    Nao mexe no tamanho do elenco importado alem disso - se o clube tem 23 ou 37
    jogadores no arquivo, e com 23 ou 37 que ele joga.
    """
    criados = 0
    for pos in POS:
        if conta_posicao(G, c, pos) == 0:
            j = novo_jogador(G, pos, nivel - 10, usados)
            j["clube"] = c["id"]
            c["elenco"].append(j["id"])
            criados += 1
    while len(c["elenco"]) < 14:
        faltante = min(POS, key=lambda p: conta_posicao(G, c, p) / max(1, ELENCO_PADRAO[p]))
        j = novo_jogador(G, faltante, nivel - 10, usados)
        j["clube"] = c["id"]
        c["elenco"].append(j["id"])
        criados += 1
    return criados


def gerar_rodadas(times):
    t = list(times)
    rng.shuffle(t)
    n = len(t)
    fixo, resto = t[0], t[1:]
    turno = []
    for r in range(n - 1):
        arr = [fixo] + resto
        rodada = []
        for i in range(n // 2):
            a, b = arr[i], arr[n - 1 - i]
            if (r + i) % 2 == 0:
                rodada.append([a, b])
            else:
                rodada.append([b, a])
        turno.append(rodada)
        resto = [resto[-1]] + resto[:-1]
    volta = [[[b, a] for a, b in rd] for rd in turno]
    return turno + volta


def nova_tabela(times):
    return {str(t): {"p": 0, "j": 0, "v": 0, "e": 0, "d": 0, "gp": 0, "gc": 0} for t in times}


def nova_liga(G, div):
    times = [c["id"] for c in G["clubes"].values() if c["divisao"] == div]
    return {"div": div, "times": times, "rodadas": gerar_rodadas(times),
            "tabela": nova_tabela(times), "rodada": 0}


def criar_mundo(nome_tecnico):
    G = {"versao": VERSAO, "econ_estrelas": True, "cedivel_limpo": True, "temporada": 2026, "semana": 1, "seq": 0, "seq_c": 0,
         "clubes": {}, "jogadores": {}, "livres": [], "noticias": [], "historico": [],
         "tecnico": nome_tecnico, "clube": None, "auto": False, "fase": "liga",
         "objetivo": "", "log_semana": [], "artilharia_temp": {},
         "placar_hist": [], "temporada_stats": {}, "ultimos_meus": [], "historico_meus": [],
         "agendadas": [], "emp_ofertas": {"stamp": "", "itens": []},
         "estaduais": {}, "semana_est": 0}
    usados = set()
    for dados in CLUBES_A:
        novo_clube(G, dados, "A", usados)
    for dados in CLUBES_B:
        novo_clube(G, dados, "B", usados)
    for dados in CLUBES_C:
        novo_clube(G, dados, "C", usados)
    for dados in CLUBES_D:
        novo_clube(G, dados, "D", usados)
    for dados in CLUBES_LIB + CLUBES_SUL:
        novo_clube(G, dados, "EX", usados)
    G["ligas"] = {d: nova_liga(G, d) for d in "ABCD"}
    # agentes livres
    for _ in range(45):
        pos = rng.choice(POS)
        j = novo_jogador(G, pos, rng.uniform(38, 62), usados)
        G["livres"].append(j["id"])
    aplicar_elencos_reais(G, usados)
    # depois dos elencos brasileiros: a recalibracao deles nao pode mexer na Europa
    aplicar_mundo(G, usados, sul=True)
    montar_ligas_sul(G, usados)
    for c in G["clubes"].values():
        if c["divisao"] == "EX":
            continue
        for _ in range(rng.randint(0, 2)):
            p = rng.choice(c["elenco"])
            G["jogadores"][p]["listado"] = preco_pedido(G, G["jogadores"][p])
        cedivel = [p for p in c["elenco"] if emprestavel(G, G["jogadores"][p])]
        for p in rng.sample(cedivel, min(len(cedivel), rng.randint(0, 3))):
            G["jogadores"][p]["emp_listado"] = 1
        # academia povoada desde o primeiro dia: sem isto a tela de base
        # abriria vazia e so encheria na virada do primeiro ano
        for _ in range(rng.randint(4, 7)):
            if len(c["base_elenco"]) < vagas_base(c):
                gerar_cria(G, c, usados, idade=rng.randint(IDADE_BASE_MIN, IDADE_BASE_MAX - 1))
    montar_copas(G, primeira=True)
    return G


# ----------------------------------------------------------------------------
# O RESTO DO MUNDO: LIGAS EUROPEIAS E ELENCOS REAIS DE FORA
#
# dados_mundo.py e gerado por ferramentas/importar_elencos.py (football-data.org)
# e embutido como os elencos brasileiros. Os clubes europeus sao "EX" - fora da
# economia, do mercado e dos torneios brasileiros, como os sul-americanos - e
# levam c["liga_ext"]. Cada liga joga uma rodada por semana em G["ligas_ext"],
# sem acesso nem rebaixamento. Sem o arquivo, o jogo segue sem a Europa.
# ----------------------------------------------------------------------------

_MUNDO = []


def mundo_embutido():
    if not _MUNDO:
        try:
            import dados_mundo
            texto = "".join(dados_mundo.MUNDO_EMBUTIDO)
            _MUNDO.append(json.loads(zlib.decompress(base64.b64decode(texto)).decode("utf-8")))
        except Exception:
            _MUNDO.append(None)
    return _MUNDO[0]


def ligas_ext(G):
    """As ligas de fora: tudo em G["ligas"] que nao e serie brasileira."""
    return {k: v for k, v in G["ligas"].items() if k not in DIVISOES_BR}


def nome_da_liga(G, div):
    if div in DIVISOES_BR:
        return "Serie %s" % div
    liga = G.get("ligas", {}).get(div)
    return liga.get("nome", div) if liga else div


_REPETIDOS = {"n": -1, "nomes": set()}


def nome_clube(G, cid):
    """Nome do clube para lista e noticia. Nome repetido no mundo (o Athletic
    mineiro e o de Bilbao) ganha a liga ao lado: "Athletic (La Liga)"."""
    c = G["clubes"].get(cid) if cid is not None else None
    if not c:
        return "sem clube"
    if _REPETIDOS["n"] != len(G["clubes"]):
        vistos, repetidos = set(), set()
        for x in G["clubes"].values():
            (repetidos if x["nome"] in vistos else vistos).add(x["nome"])
        _REPETIDOS.update(n=len(G["clubes"]), nomes=repetidos)
    if c["nome"] in _REPETIDOS["nomes"]:
        return "%s (%s)" % (c["nome"], nome_da_liga(G, c["divisao"]) if c["divisao"] != "EX" else "exterior")
    return c["nome"]


def nova_liga_ext(codigo, nome, ids):
    # liga grande (a MLS tem 29) ou impar nao cabe em ida e volta nas 38 semanas:
    # joga so o turno
    if len(ids) > 20 or len(ids) % 2:
        rodadas = _turno_completo(ids)
    else:
        rodadas = gerar_rodadas(ids)
    return {"div": codigo, "nome": nome, "times": list(ids), "rodadas": rodadas,
            "tabela": nova_tabela(ids), "rodada": 0, "resultados": []}


def aplicar_mundo(G, usados, sul=False):
    """Cria as ligas europeias que faltam. Com sul=True (so em mundo novo), poe
    tambem os elencos reais dos sul-americanos: em save ja comecado eles nao
    mudam, para nao virar o elenco de ninguem.

    Os brasileiros vem so de ELENCOS_EMBUTIDOS (feitos a mao). O bloco "brasil"
    que o importador chegou a gerar (o Santos da API por cima do original) e
    ignorado de proposito."""
    m = mundo_embutido()
    if not m:
        return
    ligas = G["ligas"]
    for liga in m.get("ligas", []):
        if liga["codigo"] in ligas:
            continue
        ids = []
        for d in liga["clubes"]:
            c = novo_clube(G, (d["nome"], d["pais"], d["estadio"], d["capacidade"], d["reputacao"]),
                           liga["codigo"], usados)
            c["liga_ext"] = liga["codigo"]
            trocar_elenco(G, c, d["elenco"], usados)
            ids.append(c["id"])
        ligas[liga["codigo"]] = nova_liga_ext(liga["codigo"], liga["nome"], ids)
    ja = {c["nome"] for c in G["clubes"].values() if c["divisao"] == "EX"}
    for bloco, europeu in (("outros_europeus", True), ("sul_novos", False)):
        for d in m.get(bloco) or []:
            if d["nome"] in ja:
                continue
            c = novo_clube(G, (d["nome"], d["pais"], d["estadio"], d["capacidade"], d["reputacao"]),
                           "EX", usados)
            c["europeu"] = europeu
            if d["elenco"]:
                trocar_elenco(G, c, d["elenco"], usados)
    for c in G["clubes"].values():
        if c.get("liga_ext") in ORDEM_LIGAS_EXT:
            c["europeu"] = True
    if not sul:
        return
    por_nome = {c["nome"]: c for c in G["clubes"].values() if not c.get("europeu")}
    for nome, lista in (m.get("sul") or {}).items():
        if nome in por_nome and lista and por_nome[nome]["divisao"] not in DIVISOES_BR:
            trocar_elenco(G, por_nome[nome], lista, usados)


def montar_ligas_sul(G, usados):
    """Poe os sul-americanos "EX" na liga do pais e completa cada liga com os
    clubes de CLUBES_LIGAS_SUL. Liga que ja existe no save nao muda. Devolve
    os codigos criados."""
    criadas = []
    for codigo, nome, n in LIGAS_SUL:
        if codigo in G["ligas"]:
            continue
        do_pais = sorted((c for c in G["clubes"].values()
                          if c["divisao"] == "EX" and c["uf"] == codigo and not c.get("europeu")),
                         key=lambda c: -c["reputacao"])
        nomes = {c["nome"] for c in do_pais}
        for dados in CLUBES_LIGAS_SUL.get(codigo, []):
            if len(do_pais) >= n:
                break
            if dados[0] in nomes:
                continue
            do_pais.append(novo_clube(G, dados, codigo, usados))
        if len(do_pais) < 4:
            continue
        ids = []
        for c in do_pais:
            if c["divisao"] == "EX":
                # veio de fora das ligas: caixa na escala do pais
                c["dinheiro"] = int(c["reputacao"] ** 2 * 3800 * perfil_liga(codigo)["caixa"]) \
                    + rng.randint(200_000, 1_200_000)
            c["divisao"] = codigo
            c["liga_ext"] = codigo
            ids.append(c["id"])
        G["ligas"][codigo] = nova_liga_ext(codigo, nome, ids)
        criadas.append(codigo)
    return criadas


def ligas_sul(G):
    return [k for k in CODIGOS_SUL if k in G["ligas"]]


def vagas_continentais_sul(G):
    """As 24 vagas de fora da Libertadores e da Sul-Americana, pela liga de
    cada pais (classificacao do ano anterior; no primeiro ano, reputacao)."""
    lib, sula = [], []
    for k in ligas_sul(G):
        ordem = _ordem_liga_ext(G, k)
        a, b = VAGAS_LIB.get(k, 0), VAGAS_SULA.get(k, 0)
        lib += ordem[:a]
        sula += ordem[a:a + b]
    return lib, sula


def falta_mundo(G):
    """O save ainda nao tem tudo o que o dados_mundo.py traz?"""
    m = mundo_embutido()
    if not m:
        return False
    if set(l["codigo"] for l in m.get("ligas", [])) - set(G["ligas"]):
        return True
    nomes = {c["nome"] for c in G["clubes"].values()}
    return any(d["nome"] not in nomes for b in ("outros_europeus", "sul_novos") for d in m.get(b) or [])


def jogar_rodada_ext(G, liga):
    if liga["rodada"] >= len(liga["rodadas"]):
        return []
    res, placares = [], []
    for casa, fora in liga["rodadas"][liga["rodada"]]:
        r = simular(G, casa, fora, "liga")
        registrar(liga, casa, fora, r["gc"], r["gf"])
        placares.append([casa, fora, r["gc"], r["gf"]])
        res.append(r)
    liga["resultados"].append(placares)
    liga["ultimos"] = placares
    liga["rodada"] += 1
    return res


def fechar_ligas_ext(G):
    """Virada: campeao de quem jogou tudo, e as ligas recomecam com os mesmos clubes."""
    anterior = G.setdefault("class_ext_anterior", {})
    for codigo, liga in list(ligas_ext(G).items()):
        if liga["rodada"] >= len(liga["rodadas"]) and liga["times"]:
            ordem = classificacao(G, liga)
            dar_titulo(G, G["clubes"][ordem[0]], liga["nome"])
            anterior[codigo] = ordem
        vivos = [i for i in liga["times"] if i in G["clubes"]]
        G["ligas"][codigo] = nova_liga_ext(codigo, liga["nome"], vivos)


# ----------------------------------------------------------------------------
# COPAS
# ----------------------------------------------------------------------------

def montar_copas(G, primeira=False):
    A = [c["id"] for c in G["clubes"].values() if c["divisao"] == "A"]
    B = [c["id"] for c in G["clubes"].values() if c["divisao"] == "B"]
    C = [c["id"] for c in G["clubes"].values() if c["divisao"] == "C"]
    D = [c["id"] for c in G["clubes"].values() if c["divisao"] == "D"]
    D.sort(key=lambda i: -G["clubes"][i]["reputacao"])
    copa = A + B + C + D[:4]

    if primeira:
        ordem = sorted(A, key=lambda i: -G["clubes"][i]["reputacao"])
    else:
        ordem = G.get("class_A_anterior") or sorted(A, key=lambda i: -G["clubes"][i]["reputacao"])
        ordem = [i for i in ordem if G["clubes"][i]["divisao"] == "A"]
        faltam = [i for i in A if i not in ordem]
        ordem = ordem + faltam

    campeao_ucl = (G.get("copas") or {}).get("ucl", {}).get("campeao")
    supercopas = [] if primeira else montar_supercopas(G, G.get("copas") or {})
    ex = sorted((c["id"] for c in G["clubes"].values()
                 if c["divisao"] == "EX" and not c.get("liga_ext") and not c.get("europeu")),
                key=lambda i: -G["clubes"][i]["reputacao"])
    if ligas_sul(G):
        # as vagas saem das ligas do continente; sobra de "EX" (save antigo) completa
        ex_lib, ex_sul = vagas_continentais_sul(G)
        resto = [i for i in ex if i not in ex_lib and i not in ex_sul]
        ex_lib += resto[:max(0, 24 - len(ex_lib))]
        resto = [i for i in resto if i not in ex_lib]
        ex_sul += resto[:max(0, 24 - len(ex_sul))]
    else:
        ex_lib, ex_sul = ex[:24], ex[24:48]
    br_lib, br_sul = ordem[:8], ordem[8:16]
    # mundo sem estrangeiros bastantes: a Sul-Americana completa com brasileiros,
    # seguindo a Serie A e depois a Serie B por reputacao
    if len(ex_sul) < 24:
        usados = set(br_lib + br_sul)
        extras = [i for i in ordem[16:] + sorted(B, key=lambda i: -G["clubes"][i]["reputacao"])
                  if i not in usados]
        br_sul = br_sul + extras[:24 - len(ex_sul)]

    G["copas"] = {
        "copa": {"nome": "Copa do Brasil", "vivos": copa[:], "fase": 0,
                 "semanas": SEMANAS_COPA, "campeao": None, "historico": []},
        "lib": nova_copa_continental(G, "Libertadores", br_lib + ex_lib, SEMANAS_CONT, FASES_LIB),
        "sul": nova_copa_continental(G, "Sul-Americana", br_sul + ex_sul, SEMANAS_SULA, FASES_SULA),
    }
    rng.shuffle(G["copas"]["copa"]["vivos"])
    G["copas"]["copa"]["sorteio"] = sortear_confrontos(G, G["copas"]["copa"]["vivos"])
    montar_copas_europeias(G, primeira, campeao_ucl)
    montar_copas_nacionais(G)
    for chave, cp in supercopas:
        G["copas"][chave] = cp
    # depois da Champions no dicionario: na semana 37 a final dela ja saiu
    G["copas"]["intercontinental"] = nova_intercontinental()
    if ano_de_mundial(int(G["temporada"])) and not primeira:
        mundial = montar_mundial(G)
        if mundial:
            G["copas"]["mundial"] = mundial


def nova_intercontinental():
    return {"nome": "Copa Intercontinental", "vivos": [], "fase": 0,
            "semanas": list(SEMANAS_INTERCONTINENTAL), "fases": list(FASES_INTERCONTINENTAL),
            "campeao": None, "historico": [], "sorteio": [], "espera": [],
            "jogo_unico": True, "neutro": True, "intercontinental": True}


def _lider(G, codigo):
    liga = G["ligas"].get(codigo)
    return classificacao(G, liga)[0] if liga and liga["times"] else None


def preparar_intercontinental(G):
    """Assim que a Libertadores tem campeao, o Derby das Americas ganha os dois
    lados (o melhor da MLS agora; sem MLS, o da Arabia)."""
    cp = G["copas"].get("intercontinental")
    if not cp or cp["vivos"] or cp["campeao"] or cp["fase"]:
        return
    lib = (G["copas"].get("lib") or {}).get("campeao")
    if lib is None:
        return
    rival = _lider(G, "USA") or _lider(G, "SAU")
    if rival is None or rival == lib:
        return
    cp["vivos"] = [lib, rival]
    cp["sorteio"] = [[rival, lib]]


def entrar_campeao_europeu(G, cp):
    """Na hora do Derby: o campeao da Champions (final na mesma semana, antes
    no calendario) espera na final."""
    ucl = (G["copas"].get("ucl") or {}).get("campeao")
    if cp["fase"] == 0 and ucl is not None and ucl not in cp["vivos"] and not cp["espera"]:
        cp["espera"] = [ucl]


def ano_de_mundial(temporada: int) -> bool:
    return temporada >= ANO_MUNDIAL and (temporada - ANO_MUNDIAL) % 4 == 0


def montar_mundial(G):
    """Os 32: campeoes da Champions e da Libertadores do ano que acabou, e o
    resto por reputacao em cada bloco (Europa, America do Sul com os
    brasileiros, MLS e Arabia). Bloco que nao fecha e completado pela Europa."""
    anteriores = G.get("copas") or {}
    clubes = G["clubes"].values()
    blocos = {
        "europeu": [c for c in clubes if c.get("europeu")],
        "conmebol": [c for c in clubes if c["divisao"] in DIVISOES_BR or c["divisao"] in CODIGOS_SUL],
        "USA": [c for c in clubes if c["divisao"] == "USA"],
        "SAU": [c for c in clubes if c["divisao"] == "SAU"],
    }
    campeoes = {"europeu": (anteriores.get("ucl") or {}).get("campeao"),
                "conmebol": (anteriores.get("lib") or {}).get("campeao")}
    times, falta = [], 0
    for bloco, n in VAGAS_MUNDIAL:
        ordem = sorted((c["id"] for c in blocos[bloco]), key=lambda i: -G["clubes"][i]["reputacao"])
        primeiro = campeoes.get(bloco)
        if primeiro in G["clubes"]:
            ordem = [primeiro] + [i for i in ordem if i != primeiro]
        escolhidos = ordem[:n]
        falta += n - len(escolhidos)
        times += escolhidos
    if falta:
        resto = sorted((c["id"] for c in blocos["europeu"] if c["id"] not in times),
                       key=lambda i: -G["clubes"][i]["reputacao"])
        times += resto[:falta]
    if len(times) < 32:
        return None
    grupos = sortear_grupos_continentais(G, times)
    for g in grupos:
        a, b, c, d = g["times"]
        g["rodadas"] = [[[a, b], [c, d]], [[a, c], [d, b]], [[d, a], [b, c]]]
    return {"nome": "Mundial de Clubes", "vivos": list(times), "fase": 0,
            "semanas": list(SEMANAS_MUNDIAL), "fases": list(FASES_LIB), "campeao": None,
            "historico": [], "sorteio": [], "espera": [], "grupos": grupos,
            "semanas_grupos": list(SEMANAS_MUNDIAL_GRUPOS), "rodada_grupo": 0,
            "formato": "grupos_top2", "jogo_unico": True, "neutro": True}


def _decisao(nome, a, b, **extra):
    """Uma supercopa: dois clubes, uma fase so."""
    cp = {"nome": nome, "vivos": [a, b], "fase": 0, "semanas": [], "campeao": None,
          "historico": [], "sorteio": [[a, b]], "supercopa": True}
    cp.update(extra)
    return cp


def _campeao_liga(G, codigo):
    if codigo == "A":
        ordem = G.get("class_A_anterior") or []
    else:
        ordem = G.get("class_ext_anterior", {}).get(codigo) or []
    return [i for i in ordem if i in G["clubes"]]


def montar_supercopas(G, anteriores):
    """As supercopas do ano que comeca, com os campeoes do ano que acabou.
    Quando o mesmo clube ganhou as duas coisas, o outro lado e o vice da liga."""
    out = []

    def par(liga_ordem, copa):
        if not liga_ordem:
            return None
        a = liga_ordem[0]
        b = (anteriores.get(copa) or {}).get("campeao")
        if b is None or b == a or b not in G["clubes"]:
            b = liga_ordem[1] if len(liga_ordem) > 1 else None
        return (a, b) if b is not None else None

    ab = par(_campeao_liga(G, "A"), "copa")
    if ab:
        out.append(("supercopa", _decisao("Supercopa do Brasil", *ab, semanas_est=[SUPERCOPA_BR_EST])))
    lib = (anteriores.get("lib") or {}).get("campeao")
    sula = (anteriores.get("sul") or {}).get("campeao")
    if lib in G["clubes"] and sula in G["clubes"] and lib != sula:
        out.append(("recopa", _decisao("Recopa Sul-Americana", lib, sula, semanas_est=[RECOPA_EST],
                                       final_ida_volta=True)))
    ucl = (anteriores.get("ucl") or {}).get("campeao")
    uel = (anteriores.get("uel") or {}).get("campeao")
    if ucl in G["clubes"] and uel in G["clubes"] and ucl != uel:
        out.append(("supercopa_uefa", _decisao("Supercopa da UEFA", ucl, uel,
                                               semanas=[SEMANA_SUPERCOPAS], fundo=True)))
    for codigo, nome in SUPERCOPAS_NACIONAIS.items():
        ab = par(_campeao_liga(G, codigo), chave_copa_nac(codigo))
        if ab:
            out.append(("sc_" + codigo, _decisao(nome, *ab, semanas=[SEMANA_SUPERCOPAS],
                                                 fundo=True, pais=codigo)))
    return out


def copa_do_estadual_na_semana(cp, semana_est):
    """Copa que se joga numa rodada do estadual (Supercopa, Recopa)."""
    se = cp.get("semanas_est") or []
    return not cp["campeao"] and cp["fase"] < len(se) and se[cp["fase"]] == semana_est


def chave_copa_nac(codigo: str) -> str:
    return "cn_" + codigo


def montar_copas_nacionais(G, so_faltam=False):
    """Uma copa por liga de fora que tem nome em COPAS_NACIONAIS. Com
    so_faltam (save antigo), cria so as que nao existem e so se a primeira
    fase ainda nao passou."""
    for codigo, nome in COPAS_NACIONAIS.items():
        chave = chave_copa_nac(codigo)
        liga = G["ligas"].get(codigo)
        if not liga or (so_faltam and chave in G["copas"]):
            continue
        times = sorted((i for i in liga["times"] if i in G["clubes"]),
                       key=lambda i: -G["clubes"][i]["reputacao"])
        n = 16 if len(times) >= 16 else 8
        if len(times) < n:
            continue
        semanas = semanas_copa_nac(codigo, n)
        if so_faltam and G.get("fase") == "liga" and G["semana"] >= semanas[0]:
            continue
        vivos = times[:n]
        rng.shuffle(vivos)
        G["copas"][chave] = {"nome": nome, "vivos": vivos, "fase": 0, "semanas": list(semanas),
                             "campeao": None, "historico": [], "jogo_unico": True, "fundo": True,
                             "pais": codigo, "sorteio": sortear_confrontos(G, vivos)}


# ----------------------------------------------------------------------------
# COPAS EUROPEIAS
#
# Champions e Europa League no formato de 2024: fase de liga com os 36 numa
# tabela so, 8 jogos cada. Ela e um "grupo" unico em cp["grupos"], entao usa a
# mesma maquina da fase de grupos; o mata-mata e o da Sul-Americana (playoff do
# 9o ao 24o, com os 8 primeiros esperando em cp["espera"]). O sorteio da fase
# de liga e simplificado: 8 rodadas do rodizio, sem potes.
# ----------------------------------------------------------------------------

def _ordem_liga_ext(G, codigo):
    liga = G["ligas"][codigo]
    ordem = [i for i in G.get("class_ext_anterior", {}).get(codigo, []) if i in liga["times"]]
    resto = sorted((i for i in liga["times"] if i not in ordem), key=lambda i: -G["clubes"][i]["reputacao"])
    return ordem + resto


def _intercalado(G, excluir):
    """Clubes das ligas por posicao: 1os de todas, depois 2os... na ordem de forca."""
    ordens = [_ordem_liga_ext(G, k) for k in ORDEM_LIGAS_EXT if k in G["ligas"]]
    fora = []
    for pos in range(max((len(o) for o in ordens), default=0)):
        for o in ordens:
            if pos < len(o) and o[pos] not in excluir and o[pos] not in fora:
                fora.append(o[pos])
    return fora


def montar_copas_europeias(G, primeira, campeao_ucl):
    if not any(k in G["ligas"] for k in ORDEM_LIGAS_EXT):
        return
    outros = sorted((c["id"] for c in G["clubes"].values()
                     if c.get("europeu") and not c.get("liga_ext")),
                    key=lambda i: -G["clubes"][i]["reputacao"])
    m = mundo_embutido() or {}
    por_nome = {c["nome"]: c["id"] for c in G["clubes"].values() if c.get("europeu")}
    reais = [por_nome[n] for n in m.get("champions", []) if n in por_nome]
    if primeira and len(reais) >= 32:
        ucl = reais[:36]
    else:
        ucl = []
        for k in ORDEM_LIGAS_EXT:
            if k in G["ligas"]:
                ucl += _ordem_liga_ext(G, k)[:VAGAS_CHAMPIONS.get(k, 1)]
        if campeao_ucl in G["clubes"] and campeao_ucl not in ucl:
            ucl.append(campeao_ucl)
        ucl += [i for i in outros if i not in ucl][:36 - len(ucl)]
    ucl += _intercalado(G, set(ucl))[:36 - len(ucl)]
    uel = _intercalado(G, set(ucl))[:36]
    G["copas"]["ucl"] = nova_copa_suica(G, "Champions League", ucl)
    if len(uel) >= 24:
        G["copas"]["uel"] = nova_copa_suica(G, "Europa League", uel)


def nova_copa_suica(G, nome, times):
    ids = list(times)
    rodadas = gerar_rodadas(ids)[:len(SEMANAS_FASE_LIGA)]
    liga = {"nome": FASE_LIGA, "times": ids, "tabela": nova_tabela(ids), "rodadas": rodadas,
            "rodada": 0, "resultados": []}
    return {"nome": nome, "vivos": ids, "fase": 0, "semanas": list(SEMANAS_EURO),
            "fases": list(FASES_SULA), "campeao": None, "historico": [], "sorteio": [],
            "espera": [], "grupos": [liga], "semanas_grupos": list(SEMANAS_FASE_LIGA),
            "rodada_grupo": 0, "formato": "suico"}


# ----------------------------------------------------------------------------
# FASE DE GRUPOS DAS COPAS CONTINENTAIS
#
# Cada grupo e uma mini-liga (times, tabela, rodadas, rodada) e por isso usa
# registrar e classificacao das series. Durante os grupos todos os 32 estao em
# cp["vivos"]; quando os grupos acabam, vivos vira quem segue no mata-mata e o
# resto da copa (fase, semanas, sorteio, historico) funciona como sempre.
# Na Sul-Americana, os primeiros de grupo esperam o playoff em cp["espera"].
# ----------------------------------------------------------------------------

def nova_copa_continental(G, nome, times, semanas, fases):
    return {"nome": nome, "vivos": list(times), "fase": 0, "semanas": list(semanas),
            "fases": list(fases), "campeao": None, "historico": [], "sorteio": [],
            "espera": [], "grupos": sortear_grupos_continentais(G, times),
            "semanas_grupos": list(SEMANAS_GRUPOS), "rodada_grupo": 0}


def pais(c):
    return "BRA" if brasileiro(c) else c["uf"]


def sortear_grupos_continentais(G, times):
    """Quatro potes por reputacao, um clube de cada pote por grupo. Clubes do
    mesmo pais se evitam quando da: sorteia de novo e fica com o que tiver
    menos encontros de compatriotas."""
    ordem = sorted(times, key=lambda i: -G["clubes"][i]["reputacao"])
    n = max(1, len(ordem) // 4)
    potes = [ordem[k * n:(k + 1) * n] for k in range(4)]
    melhor, pior = None, None
    for _ in range(200):
        grupos = [[] for _ in range(n)]
        for pote in potes:
            embaralhado = pote[:]
            rng.shuffle(embaralhado)
            for g, cid in zip(grupos, embaralhado):
                g.append(cid)
        choques = sum(len(g) - len({pais(G["clubes"][i]) for i in g}) for g in grupos)
        if pior is None or choques < pior:
            melhor, pior = grupos, choques
        if choques == 0:
            break
    fora = []
    for k, ids in enumerate(melhor):
        a, b, c, d = ids
        rodadas = [[[a, b], [c, d]], [[d, a], [b, c]], [[a, c], [d, b]],
                   [[b, a], [d, c]], [[a, d], [c, b]], [[c, a], [b, d]]]
        fora.append({"nome": "Grupo " + "ABCDEFGH"[k % 8], "times": list(ids),
                     "tabela": nova_tabela(ids), "rodadas": rodadas, "rodada": 0,
                     "resultados": []})
    return fora


def em_grupos(cp):
    return bool(cp.get("grupos")) and cp.get("rodada_grupo", 0) < len(cp.get("semanas_grupos", []))


def vivo_na_copa(cp, cid):
    """Segue na copa: jogando agora ou esperando o playoff acabar."""
    return not cp.get("campeao") and (cid in cp["vivos"] or cid in cp.get("espera", []))


def fase_da_copa(cp):
    if cp.get("campeao"):
        return "Encerrada"
    if em_grupos(cp):
        return FASE_LIGA if cp.get("formato") == "suico" else FASE_GRUPOS
    fases = cp.get("fases")
    if fases and cp["fase"] < len(fases):
        return fases[cp["fase"]]
    return nome_fase(len(cp["vivos"]))


def proxima_semana_copa(cp):
    if cp.get("campeao"):
        return None
    if em_grupos(cp):
        return cp["semanas_grupos"][cp["rodada_grupo"]]
    return cp["semanas"][cp["fase"]] if cp["fase"] < len(cp["semanas"]) else None


def grupo_de(cp, cid):
    for g in cp.get("grupos") or []:
        if cid in g["times"]:
            return g
    return None


def jogo_de_grupo(cp, cid):
    """(casa, fora) do clube na proxima rodada de grupos, ou None."""
    if not em_grupos(cp):
        return None
    g = grupo_de(cp, cid)
    if not g or g["rodada"] >= len(g["rodadas"]):
        return None
    return next(((a, b) for a, b in g["rodadas"][g["rodada"]] if cid in (a, b)), None)


def jogar_rodada_grupos(G, chave):
    cp = G["copas"][chave]
    res = []
    for g in cp["grupos"]:
        if g["rodada"] >= len(g["rodadas"]):
            continue
        placares = []
        for casa, fora in g["rodadas"][g["rodada"]]:
            r = simular(G, casa, fora, chave, neutro=bool(cp.get("neutro")))
            registrar(g, casa, fora, r["gc"], r["gf"])
            placares.append([casa, fora, r["gc"], r["gf"]])
            res.append(r)
            if r["gc"] != r["gf"]:
                venc = G["clubes"][casa if r["gc"] > r["gf"] else fora]
                if venc["divisao"] != "EX":
                    lancar(G, venc, PREMIO_VITORIA_GRUPO.get(chave, 0), "premio_grupo")
        g["resultados"].append(placares)
        g["rodada"] += 1
    cp["rodada_grupo"] += 1
    return res


def cruzar(G, cabecas, outros):
    """Confrontos cabeca de chave x outro. O cabeca (melhor campanha) decide em
    casa: na lista de pares ele vai em segundo, porque o primeiro manda a ida."""
    c, o = list(cabecas), list(outros)
    rng.shuffle(c)
    rng.shuffle(o)
    return [[b, a] for a, b in zip(c, o)]


def fechar_grupos(G):
    """Grupos que acabaram viram mata-mata. A Libertadores fecha antes, porque
    os terceiros dela vao para o playoff da Sul-Americana."""
    meu = G.get("clube")
    for chave, cp in G["copas"].items():
        if cp.get("formato") != "suico" or cp.get("grupos_fechados") or em_grupos(cp):
            continue
        ordem = classificacao(G, cp["grupos"][0])
        cp["grupos_fechados"] = True
        cp["espera"] = ordem[:8]
        cp["vivos"] = ordem[8:24]
        cp["sorteio"] = cruzar(G, ordem[8:16], ordem[16:24])
        manchete(G, "copa", "%s: %s termina a fase de liga em primeiro." %
                 (cp["nome"], G["clubes"][ordem[0]]["nome"]))
    for chave, cp in G["copas"].items():
        if cp.get("formato") != "grupos_top2" or cp.get("grupos_fechados") or em_grupos(cp):
            continue
        ordens = [classificacao(G, g) for g in cp["grupos"]]
        primeiros, segundos = [o[0] for o in ordens], [o[1] for o in ordens]
        cp["grupos_fechados"] = True
        cp["vivos"] = primeiros + segundos
        cp["sorteio"] = cruzar(G, primeiros, segundos)
        if meu in cp["vivos"]:
            noticia(G, "%s: classificado para o mata-mata." % cp["nome"])
    for chave in ("lib", "sul"):
        cp = G["copas"].get(chave)
        if not cp or not cp.get("grupos") or cp.get("grupos_fechados") or em_grupos(cp):
            continue
        lib = G["copas"].get("lib")
        if chave == "sul" and lib and lib.get("grupos") and not lib.get("grupos_fechados"):
            continue
        ordens = [classificacao(G, g) for g in cp["grupos"]]
        primeiros = [o[0] for o in ordens]
        segundos = [o[1] for o in ordens]
        terceiros = [o[2] for o in ordens]
        cp["grupos_fechados"] = True
        if chave == "lib":
            cp["vivos"] = primeiros + segundos
            cp["sorteio"] = cruzar(G, primeiros, segundos)
            sul = G["copas"].get("sul")
            if sul and sul.get("grupos"):
                sul["terceiros_lib"] = terceiros
                if meu in terceiros:
                    noticia(G, "Terceiro no grupo da Libertadores: o time cai para o playoff "
                               "da Sul-Americana.")
        else:
            vindos = cp.pop("terceiros_lib", None)
            if vindos:
                cp["vivos"] = segundos + vindos
                # o terceiro da Libertadores decide em casa
                cp["sorteio"] = cruzar(G, vindos, segundos)
                cp["espera"] = primeiros
            else:
                # sem Libertadores de grupos para cruzar: oitavas direto
                cp["fases"] = cp["fases"][1:]
                cp["semanas"] = cp["semanas"][1:]
                cp["vivos"] = primeiros + segundos
                cp["sorteio"] = cruzar(G, primeiros, segundos)
        if meu in [i for o in ordens for i in o]:
            if meu in cp["vivos"] or meu in cp.get("espera", []):
                noticia(G, "%s: classificado para o mata-mata." % cp["nome"])
            elif not (chave == "lib" and meu in terceiros):
                noticia(G, "%s: eliminado na fase de grupos." % cp["nome"])
        for o in ordens:
            for cid in o[2 if chave == "lib" else 1:]:
                cl = G["clubes"][cid]
                if cl["reputacao"] >= GRANDE_REP and cl["divisao"] != "EX":
                    manchete(G, "copa", "%s cai na fase de grupos da %s." % (cl["nome"], cp["nome"]))


def sortear_confrontos(G, vivos):
    """Os pares da proxima fase. Manda o primeiro jogo quem tem menor
    reputacao (fator zebra), como sempre foi.

    O sorteio agora sai logo que a fase anterior acaba, e nao na hora do jogo:
    assim o tecnico sabe quem vem pela frente na copa, e a tela pode mostrar o
    chaveamento. Antes o adversario so existia no instante da partida.
    """
    vivos = list(vivos)
    rng.shuffle(vivos)
    pares = []
    for i in range(0, len(vivos) - 1, 2):
        a, b = vivos[i], vivos[i + 1]
        if G["clubes"][a]["reputacao"] > G["clubes"][b]["reputacao"]:
            a, b = b, a
        pares.append([a, b])
    return pares


def sorteio_da_copa(G, chave):
    """Os confrontos ja sorteados da fase que vem. Save antigo, que nao tinha
    sorteio guardado, ganha um na primeira vez que alguem pergunta."""
    cp = G["copas"][chave]
    if cp.get("campeao") or len(cp["vivos"]) < 2 or em_grupos(cp):
        return []
    pares = cp.get("sorteio") or []
    nos_pares = sorted(x for par in pares for x in par)
    if nos_pares != sorted(cp["vivos"]):
        cp["sorteio"] = pares = sortear_confrontos(G, cp["vivos"])
    return pares


def nome_fase(n):
    return {2: "FINAL", 4: "Semifinal", 8: "Quartas de final", 16: "Oitavas de final",
            32: "Terceira fase", 64: "Segunda fase", 128: "Primeira fase"}.get(n, "Fase de %d" % n)


# ----------------------------------------------------------------------------
# FORCA DO TIME / ESCALACAO
# ----------------------------------------------------------------------------

Jogador = Dict[str, Any]
Clube = Dict[str, Any]
Mundo = Dict[str, Any]

# Quanto um jogador rende ao ser escalado fora da posicao natural.
# 0.0 = nao entra nessa vaga de jeito nenhum.
AFINIDADE: Dict[str, Dict[str, float]] = {
    #        GOL   ZAG   LAT   VOL   MEI   ATA
    "GOL": {"GOL": 1.00, "ZAG": 0.45, "LAT": 0.35, "VOL": 0.30, "MEI": 0.25, "ATA": 0.25},
    "ZAG": {"GOL": 0.35, "ZAG": 1.00, "LAT": 0.80, "VOL": 0.78, "MEI": 0.55, "ATA": 0.45},
    "LAT": {"GOL": 0.30, "ZAG": 0.80, "LAT": 1.00, "VOL": 0.80, "MEI": 0.72, "ATA": 0.60},
    "VOL": {"GOL": 0.30, "ZAG": 0.78, "LAT": 0.78, "VOL": 1.00, "MEI": 0.85, "ATA": 0.60},
    "MEI": {"GOL": 0.25, "ZAG": 0.55, "LAT": 0.72, "VOL": 0.85, "MEI": 1.00, "ATA": 0.85},
    "ATA": {"GOL": 0.25, "ZAG": 0.45, "LAT": 0.58, "VOL": 0.60, "MEI": 0.85, "ATA": 1.00},
}

# Pesos de ESCOLHA (quem entra) - dominados pelo OVR de proposito.
PESO_ESCOLHA_COND = 0.16
PESO_ESCOLHA_FORMA = 0.10
PESO_ESCOLHA_MORAL = 0.06
# Pesos de DESEMPENHO (quanto rende em campo) - condicao pesa bem mais aqui.
PESO_JOGO_COND = 0.28
PESO_JOGO_FORMA = 0.10
PESO_JOGO_MORAL = 0.05
# Entrosamento (0-100): o quanto o jogador conhece o time. Quem chega comeca
# baixo e ganha a cada jogo pelo clube; quem ja estava no mundo novo comeca
# em ENTROS_PADRAO (sem campo no save, vale o padrao: save antigo carrega igual).
PESO_JOGO_ENTROS = 0.06
ENTROS_PADRAO = 80
ENTROS_CHEGADA = 35       # contratado ou emprestado: time novo, esquema novo
ENTROS_VOLTA = 60         # voltou de emprestimo ou subiu da base: ja conhecia a casa
ENTROS_POR_JOGO = 5


def entrosamento(j: Jogador) -> int:
    return int(j.get("entros", ENTROS_PADRAO))


def sincronizar_suspensao(j: Jogador) -> None:
    """Mantem j["suspensao"] como o total de jogos de gancho, so para exibicao.

    A regra de verdade e j["susp"][competicao]; este campo agregado existe para
    as telas antigas que so perguntam "esta suspenso?".
    """
    j["suspensao"] = sum(j.get("susp", {}).values())


def cumprir_suspensao(G: Mundo, c: Clube, comp: str) -> None:
    """Desconta um jogo de gancho de quem ficou de fora DESTA partida."""
    for pid in c["elenco"]:
        j = G["jogadores"].get(pid)
        if j and j.get("susp", {}).get(comp, 0) > 0:
            j["susp"][comp] -= 1
            sincronizar_suspensao(j)


def disponivel(G: Mundo, pid: int, comp: str = "liga") -> bool:
    j = G["jogadores"].get(pid)
    if j is None:
        return False
    return j["lesao"] <= 0 and j.get("susp", {}).get(comp, 0) <= 0


def rendimento(j: Jogador, afinidade: float = 1.0) -> float:
    """Quanto o jogador rende EM CAMPO, ja descontada a posicao improvisada."""
    base = j["ovr"] * afinidade
    base *= (1.0 - PESO_JOGO_COND) + PESO_JOGO_COND * (j["cond"] / 100.0)
    base *= (1.0 - PESO_JOGO_FORMA) + PESO_JOGO_FORMA * (j["forma"] / 100.0)
    base *= (1.0 - PESO_JOGO_MORAL) + PESO_JOGO_MORAL * (j["moral"] / 100.0)
    base *= (1.0 - PESO_JOGO_ENTROS) + PESO_JOGO_ENTROS * (j.get("entros", ENTROS_PADRAO) / 100.0)
    return base


def nota_escalacao(j: Jogador, pos_alvo: str) -> float:
    """Criterio de ESCOLHA do titular. OVR manda; fisico e desempate, nao sentenca.

    Diferente de rendimento() de proposito: um reserva descansado nao pode passar
    na frente de um titular claramente melhor so por estar com 100 de condicao.
    """
    afin = AFINIDADE[j["pos"]][pos_alvo]
    if afin <= 0.0:
        return -1.0
    nota = j["ovr"] * afin
    nota *= (1.0 - PESO_ESCOLHA_COND) + PESO_ESCOLHA_COND * (j["cond"] / 100.0)
    nota *= (1.0 - PESO_ESCOLHA_FORMA) + PESO_ESCOLHA_FORMA * (j["forma"] / 100.0)
    nota *= (1.0 - PESO_ESCOLHA_MORAL) + PESO_ESCOLHA_MORAL * (j["moral"] / 100.0)
    # degraus de fadiga: o tecnico poupa quem esta acabado, nao quem esta em 80%
    if j["cond"] < 45:
        nota *= 0.72
    elif j["cond"] < 65:
        nota *= 0.90
    return nota


def _vagas_do_esquema(form: Dict[str, int]) -> List[str]:
    """Lista plana de 11 vagas a partir do mapa posicao -> quantidade."""
    vagas: List[str] = []
    for pos in POS:
        vagas.extend([pos] * form.get(pos, 0))
    return vagas


def _vagas(formacao: str) -> List[str]:
    """Lista plana de 11 vagas a partir do nome do esquema. GOL sempre primeiro."""
    return _vagas_do_esquema(FORMACOES.get(formacao, FORMACOES["4-4-2"]))


def _selecionar(G: Mundo, c: Clube, demanda: Dict[str, int],
                usados: Optional[set] = None, comp: str = "liga") -> List[int]:
    """Escolhe jogadores para um conjunto de vagas, naturais primeiro.

    demanda = quantas vagas de cada posicao ainda precisam ser preenchidas.
    usados  = quem ja esta escalado e nao pode ser reaproveitado.
    Complexidade O(n log n) por chamada, com um balde ordenado por posicao.
    """
    usados = set(usados or ())
    aptos: List[int] = [p for p in c["elenco"] if disponivel(G, p, comp) and p not in usados]
    if not aptos:
        return []

    baldes: Dict[str, List[int]] = {p: [] for p in POS}
    for pid in aptos:
        baldes[G["jogadores"][pid]["pos"]].append(pid)
    for pos, lista in baldes.items():
        lista.sort(key=lambda p: -nota_escalacao(G["jogadores"][p], pos))

    pedidas = {p: q for p, q in demanda.items() if q > 0}
    if not pedidas:
        return []
    # escassez primeiro: quem tem menos natural por vaga e servido antes
    ordem_pos = sorted(pedidas, key=lambda p: (len(baldes[p]) / float(pedidas[p]), POS.index(p)))

    escolhidos: List[int] = []
    abertas: List[str] = []
    for pos in ordem_pos:
        naturais = [p for p in baldes[pos] if p not in usados]
        pega = naturais[:pedidas[pos]]
        escolhidos.extend(pega)
        usados.update(pega)
        abertas.extend([pos] * (pedidas[pos] - len(pega)))

    if abertas:
        abertas.sort(key=lambda p: POS.index(p))   # vaga mais exigente primeiro
        for pos in abertas:
            melhor: Optional[int] = None
            melhor_nota = 0.0
            for pid in aptos:
                if pid in usados:
                    continue
                nota = nota_escalacao(G["jogadores"][pid], pos)
                if nota > melhor_nota:
                    melhor, melhor_nota = pid, nota
            if melhor is not None:
                escolhidos.append(melhor)
                usados.add(melhor)
    return escolhidos


def _peso_vagas(form: Dict[str, int]) -> Dict[str, float]:
    """Quanto cada vaga do esquema pesa na forca final calculada por forcas().

    E a mesma conta de forcas(): ataque e a media ponderada por ATT_W e defesa
    a media ponderada por DEF_W. Somando as duas ja normalizadas, cada vaga
    ganha um valor unico, e maximizar essa soma e literalmente montar o melhor
    time para o esquema escolhido.
    """
    peso_at = sum(ATT_W[p] * q for p, q in form.items()) or 1.0
    peso_de = sum(DEF_W[p] * q for p, q in form.items()) or 1.0
    return {p: ATT_W[p] / peso_at + DEF_W[p] / peso_de for p in POS}


def _atribuicao_hungara(custo: List[List[float]]) -> List[int]:
    """Atribuicao de custo minimo (hungaro / Jonker-Volgenant), O(n^2 m).

    custo[i][j] e o custo de por o candidato j na vaga i, com n vagas e m
    candidatos, n <= m. Devolve, para cada vaga, o indice do candidato que
    ficou com ela. Aqui n e sempre 11, entao roda em fracao de milissegundo.
    """
    n = len(custo)
    if n == 0:
        return []
    m = len(custo[0])
    assert n <= m, "o hungaro precisa de pelo menos uma coluna por linha"
    INF = float("inf")
    u = [0.0] * (n + 1)
    v = [0.0] * (m + 1)
    dono = [0] * (m + 1)
    caminho = [0] * (m + 1)
    for i in range(1, n + 1):
        dono[0] = i
        col = 0
        menor = [INF] * (m + 1)
        visto = [False] * (m + 1)
        while True:
            visto[col] = True
            linha = dono[col]
            base = custo[linha - 1]
            u_linha = u[linha]      # nao muda dentro do laco; mesma conta, na mesma ordem
            delta = INF
            prox = 0
            for j in range(1, m + 1):
                if visto[j]:
                    continue
                atual = base[j - 1] - u_linha - v[j]
                if atual < menor[j]:
                    menor[j] = atual
                    caminho[j] = col
                if menor[j] < delta:
                    delta = menor[j]
                    prox = j
            for j in range(m + 1):
                if visto[j]:
                    u[dono[j]] += delta
                    v[j] -= delta
                else:
                    menor[j] -= delta
            col = prox
            if dono[col] == 0:
                break
        while col:
            anterior = caminho[col]
            dono[col] = dono[anterior]
            col = anterior
    escolha = [-1] * n
    for j in range(1, m + 1):
        if dono[j]:
            escolha[dono[j] - 1] = j - 1
    return escolha


def _resolver_vagas(valores: List[List[float]], candidatos: int) -> List[int]:
    """Recebe valores (quanto maior melhor) e devolve o candidato de cada vaga.

    Quando ha menos candidatos que vagas, completa com colunas fantasma de
    valor zero: a vaga que sobra vazia e a que menos pesa no time, nao a que
    calhou de ficar por ultimo na lista.
    """
    if not valores or candidatos == 0:
        return []
    vagas = len(valores)
    custo = [[-x for x in linha] for linha in valores]
    if candidatos < vagas:
        for linha in custo:
            linha.extend([0.0] * (vagas - candidatos))
    return _atribuicao_hungara(custo)


def montar_escalacao(G: Mundo, c: Clube, comp: str = "liga",
                     ignorar_baixas: bool = False) -> List[int]:
    """O melhor XI possivel para o esquema, resolvido como atribuicao otima.

    A versao gulosa escolhia vaga a vaga e desperdicava versatilidade: servia
    primeiro a posicao mais escassa e, quando chegava na lateral, o unico que
    sobrava era um atacante. Resolvendo as 11 vagas de uma vez o time inteiro
    e maximizado, com cada vaga valendo o que ela pesa em forcas().

    ignorar_baixas monta o time como se ninguem estivesse fora: serve para o
    painel dizer QUEM caiu, comparando o time sonhado com o time possivel.
    """
    form = formacao_de(c)
    aptos = [p for p in c["elenco"] if ignorar_baixas or disponivel(G, p, comp)]
    if not aptos:
        return []
    vagas = _vagas_do_esquema(form)
    peso = _peso_vagas(form)
    # as vagas repetem (4 ZAG/LAT, 3 MEI...): a linha de notas de cada posicao
    # e a mesma, entao sai uma vez so. _resolver_vagas copia antes de mexer.
    linhas: Dict[str, List[float]] = {}
    for vaga in vagas:
        if vaga not in linhas:
            linhas[vaga] = [nota_escalacao(G["jogadores"][pid], vaga) * peso[vaga] for pid in aptos]
    valores = [linhas[vaga] for vaga in vagas]
    esc = [aptos[k] for k in _resolver_vagas(valores, len(aptos)) if 0 <= k < len(aptos)]
    esc.sort(key=lambda p: POS.index(G["jogadores"][p]["pos"]))
    return esc[:11]


def reparar_escalacao(G: Mundo, c: Clube, esc: List[int],
                      form: Dict[str, int], comp: str = "liga") -> List[int]:
    """Repoe as baixas de uma escalacao manual RESPEITANDO a vaga que vagou.

    Sem isto, ao perder um volante o time entrava com mais um atacante, porque a
    reposicao pegava o melhor disponivel em vez do melhor para aquela vaga.
    """
    faltam = 11 - len(esc)
    if faltam <= 0:
        return esc[:11]
    contagem: Dict[str, int] = {}
    for pid in esc:
        pos = G["jogadores"][pid]["pos"]
        contagem[pos] = contagem.get(pos, 0) + 1
    demanda = {p: max(0, form.get(p, 0) - contagem.get(p, 0)) for p in POS}

    novos = _selecionar(G, c, demanda, set(esc), comp)[:faltam]
    esc = esc + novos
    if len(esc) < 11:
        # o usuario empilhou posicoes: completa com o melhor disponivel de qualquer setor
        resto = [p for p in c["elenco"] if disponivel(G, p, comp) and p not in esc]
        resto.sort(key=lambda p: -nota_escalacao(G["jogadores"][p], G["jogadores"][p]["pos"]))
        esc.extend(resto[:11 - len(esc)])
    return esc[:11]


# compatibilidade com o codigo antigo que chama auto_escalar
def auto_escalar(G: Mundo, c: Clube, comp: str = "liga") -> List[int]:
    return montar_escalacao(G, c, comp)


def escalacao_automatica(G: Mundo, c: Optional[Clube] = None) -> bool:
    """A alavanca esta ligada para este clube?

    Clube da maquina nao tem alavanca: ele sempre escala sozinho. A alavanca so
    existe para o clube do usuario, e por isso ela mora no clube e vai no save.
    """
    c = c or G["clubes"][G["clube"]]
    if c["id"] != G.get("clube"):
        return True
    return bool(c.get("auto_esc", True))


def definir_escalacao_automatica(G: Mundo, ligada: bool, c: Optional[Clube] = None) -> bool:
    """Liga ou desliga a alavanca e ja deixa a escalacao coerente com ela.

    Ao ligar, monta o melhor time na hora, para o usuario ver o efeito antes de
    avancar a semana. Ao desligar, congela o XI atual como ponto de partida da
    escalacao manual, em vez de devolver uma lista vazia.
    """
    c = c or G["clubes"][G["clube"]]
    c["auto_esc"] = bool(ligada)
    c["esc_stamp"] = ""
    if ligada:
        c.pop("vagas_manuais", None)
        c["escalacao"] = montar_escalacao(G, c)
    elif not c.get("escalacao"):
        c["escalacao"] = montar_escalacao(G, c)
    return c["auto_esc"]


def herdar_preferencias(G: Mundo, antigo: Clube) -> None:
    """O tecnico troca de clube, mas nao troca de jeito de trabalhar.

    Sem isto, ser demitido religava a escalacao automatica no clube novo sem
    ninguem pedir, porque todo clube nasce com a alavanca ligada.
    """
    novo = G["clubes"][G["clube"]]
    if novo["id"] == antigo["id"]:
        return
    novo["auto_esc"] = bool(antigo.get("auto_esc", True))
    novo["esc_stamp"] = ""


def _assinatura(G: Mundo, c: Clube, comp: str = "liga") -> str:
    """Muda quando algo que invalida a escalacao muda: semana, elenco ou baixas."""
    baixas = sum(1 for p in c["elenco"] if not disponivel(G, p, comp))
    return "%d-%d-%d-%d-%s-%s-%s-%s" % (G["temporada"], G["semana"], len(c["elenco"]),
                                        baixas, nome_da_contagem(formacao_de(c)) + str(
                                            formacao_de(c).get("LAT", 0)), c["tatica"], comp,
                                        "A" if escalacao_automatica(G, c) else "M")


def escalacao_valida(G: Mundo, c: Clube, comp: str = "liga") -> Tuple[List[int], Dict[str, int]]:
    """Devolve o XI que entra em campo, com cache por assinatura.

    O time do usuario e soberano: se ele escalou, so repomos quem nao pode jogar,
    nunca reotimizamos por cima da escolha dele.
    """
    form = formacao_de(c)
    assinatura = _assinatura(G, c, comp)
    cache = c.get("escalacao") or []
    # so a liga grava o XI no clube: assim um gancho de copa nao reescreve a
    # escalacao que o usuario montou para o campeonato.
    guardar = (comp == "liga")
    if guardar and c.get("esc_stamp") == assinatura and len(cache) == 11:
        if all(p in c["elenco"] and disponivel(G, p, comp) for p in cache):
            return cache, form

    # com a alavanca ligada o clube do usuario passa pelo mesmo caminho da
    # maquina: time novo a cada semana, sempre o melhor disponivel
    manual = not escalacao_automatica(G, c)
    if manual:
        esc = [p for p in cache if p in c["elenco"] and disponivel(G, p, comp)]
        esc = list(dict.fromkeys(esc))[:11]
        baixas = [p for p in cache if p not in esc]
        esc = reparar_escalacao(G, c, esc, form, comp)
        for i, p in enumerate(esc):
            if p in cache or i >= len(esc):
                continue
            fora = baixas.pop(0) if baixas else None
            if fora is not None and fora in G["jogadores"]:
                noticia(G, "%s entrou no time no lugar de %s."
                        % (G["jogadores"][p]["nome"], G["jogadores"][fora]["nome"]))
    else:
        esc = montar_escalacao(G, c, comp)

    if guardar:
        c["escalacao"] = esc
        c["esc_stamp"] = assinatura
    return esc, form


def vagas_manuais(c: Optional[Clube]) -> Dict[int, str]:
    """Vagas que o tecnico fixou trocando dois titulares de lugar (api/rotas.py
    grava em c["vagas_manuais"] como [[pid, vaga], ...]). Vazio = tudo otimo."""
    if not c:
        return {}
    return {int(p): v for p, v in (c.get("vagas_manuais") or [])}


# Memo exato do laco de simulacao. atribuir_vagas e funcao pura de (formacao,
# vagas fixadas e, de cada titular na ordem do XI: posicao, overall, condicao,
# forma, moral e entrosamento) - rendimento() nao le mais nada. A chave leva tudo isso, entao
# o memo nunca devolve conta velha: jogador que cansou no intervalo ou mudou de
# moral e outra chave. Acerta quando o mesmo XI e medido de novo no mesmo
# estado (posse, forcas do primeiro tempo, diagnostico, painel). Vive fora do
# save e se esvazia inteiro quando enche; esvaziar nunca muda resultado.
_MEMO_VAGAS: Dict[Any, List[Tuple[int, str]]] = {}
MEMO_MAX = 20_000


def _chave_xi(G: Mundo, esc: List[int], form: Dict[str, int],
              fixas: Optional[Dict[int, str]]) -> Any:
    js = G["jogadores"]
    jogadores = tuple((pid, js[pid]["pos"], js[pid]["ovr"], js[pid]["cond"],
                       js[pid]["forma"], js[pid]["moral"], js[pid].get("entros", ENTROS_PADRAO))
                      for pid in esc)
    return (tuple(sorted(form.items())), tuple(sorted((fixas or {}).items())), jogadores)


def atribuir_vagas(G: Mundo, esc: List[int], form: Dict[str, int],
                   fixas: Optional[Dict[int, str]] = None) -> List[Tuple[int, str]]:
    """Diz em que vaga do esquema cada titular esta jogando (com memo exato;
    a conta mora em _atribuir_vagas)."""
    if not esc:
        return []
    chave = _chave_xi(G, esc, form, fixas)
    feito = _MEMO_VAGAS.get(chave)
    if feito is None:
        if len(_MEMO_VAGAS) >= MEMO_MAX:
            _MEMO_VAGAS.clear()
        feito = _MEMO_VAGAS[chave] = _atribuir_vagas(G, esc, form, fixas)
    return list(feito)


def _atribuir_vagas(G: Mundo, esc: List[int], form: Dict[str, int],
                    fixas: Optional[Dict[int, str]] = None) -> List[Tuple[int, str]]:
    """Diz em que vaga do esquema cada titular esta jogando.

    Fonte unica: forcas() calcula a penalidade a partir daqui e a interface
    mostra exatamente a mesma atribuicao. Antes o motor sabia que o volante
    estava improvisado na zaga e a tela nao contava para o usuario.

    A distribuicao e otima, nao gulosa: dados esses 11 jogadores, e o arranjo
    de vagas que mais rende. Com o guloso, trocar um titular podia piorar de
    tabela dois outros, e o usuario nao entendia por que a forca tinha caido.
    """
    if not esc:
        return []
    vagas = _vagas_do_esquema(form)
    peso = _peso_vagas(form)
    saida: List[Tuple[int, str]] = []
    # primeiro quem o tecnico fixou, se a vaga ainda existe no esquema; o resto
    # passa pela atribuicao otima de sempre
    livres = list(vagas)
    soltos = []
    for pid in esc:
        vaga = (fixas or {}).get(pid)
        if vaga in livres:
            livres.remove(vaga)
            saida.append((pid, vaga))
        else:
            soltos.append(pid)
    if soltos:
        linhas: Dict[str, List[float]] = {}
        for vaga in livres:
            if vaga not in linhas:
                linhas[vaga] = [rendimento(G["jogadores"][pid],
                                           AFINIDADE[G["jogadores"][pid]["pos"]][vaga]) * peso[vaga]
                                for pid in soltos]
        valores = [linhas[vaga] for vaga in livres]
        for i, k in enumerate(_resolver_vagas(valores, len(soltos))):
            if 0 <= k < len(soltos):
                saida.append((soltos[k], livres[i]))
    ordem_esc = {p: i for i, p in enumerate(esc)}
    saida.sort(key=lambda t: ordem_esc[t[0]])
    return saida


def forcas_de(G: Mundo, c: Clube, esc: List[int]) -> Tuple[float, float]:
    """Ataque e defesa de um XI qualquer, ja com improviso e tatica aplicados.

    Separado de forcas() para o painel poder medir o time escalado contra o
    time que a maquina montaria, sem encostar na escalacao guardada no clube.
    """
    form = formacao_de(c)
    if not esc:
        return 30.0, 30.0

    ataque = defesa = 0.0
    peso_at = peso_de = 0.0
    tem_goleiro = False
    for pid, vaga in atribuir_vagas(G, esc, form, vagas_manuais(c)):
        j = G["jogadores"][pid]
        natural = j["pos"]
        if vaga == "GOL":
            tem_goleiro = True
        r = rendimento(j, AFINIDADE[natural][vaga])
        ataque += r * ATT_W[vaga]
        peso_at += ATT_W[vaga]
        defesa += r * DEF_W[vaga]
        peso_de += DEF_W[vaga]

    if peso_at <= 0 or peso_de <= 0:
        return 30.0, 30.0
    ataque /= peso_at
    defesa /= peso_de
    if not tem_goleiro:
        defesa *= 0.62          # sem ninguem no gol o buraco e bem maior que 20%
    if len(esc) < 11:
        fator = 0.74 + 0.024 * len(esc)
        ataque *= fator
        defesa *= fator
    mult_at, mult_de = TATICAS.get(c["tatica"], (1.0, 1.0))
    return ataque * mult_at, defesa * mult_de


def forcas(G: Mundo, c: Clube, comp: str = "liga") -> Tuple[float, float, List[int]]:
    """Ataque e defesa do time que realmente entra em campo nesta semana."""
    esc, _ = escalacao_valida(G, c, comp)
    at, de = forcas_de(G, c, esc)
    return at, de, esc


def diagnostico_escalacao(G: Mundo, c: Optional[Clube] = None,
                          comp: str = "liga") -> Dict[str, object]:
    """Radiografia do XI que entra em campo, com veredito pronto para a tela.

    Fonte unica do aviso. O painel, a regua do topo, o botao de avancar, o
    rodape e o console leem daqui: cinco pontos da interface discordando e
    pior do que nenhum aviso. Devolve os numeros crus e tambem a frase.

    Os degraus, na ordem em que sao testados:
      critico  - o time esta quebrado e o jogo vai cobrar caro
      atencao  - da para jogar, mas custa rendimento
      ok       - nada te impede de avancar
      neutro   - nao ha jogo nesta semana, nao ha time certo nem errado
    """
    c = c or G["clubes"][G["clube"]]
    jogs = G["jogadores"]
    auto = escalacao_automatica(G, c)

    esc, form = escalacao_valida(G, c, comp)
    vagas = atribuir_vagas(G, esc, form, vagas_manuais(c))
    improvisados = [(pid, vaga) for pid, vaga in vagas if vaga != jogs[pid]["pos"]]
    afin_min = min([AFINIDADE[jogs[pid]["pos"]][vaga] for pid, vaga in improvisados],
                   default=1.0)
    graves = [(pid, vaga) for pid, vaga in improvisados
              if AFINIDADE[jogs[pid]["pos"]][vaga] < 0.60]
    tem_goleiro = any(vaga == "GOL" for _, vaga in vagas)

    desfalques = [p for p in c["elenco"] if not disponivel(G, p, comp)]
    lesionados = [p for p in desfalques if jogs[p]["lesao"] > 0]
    suspensos = [p for p in desfalques if jogs[p].get("susp", {}).get(comp, 0) > 0]
    aptos = len(c["elenco"]) - len(desfalques)
    # quem seria titular se estivesse inteiro, mas nao esta: esses sim "cairam"
    caidos = [p for p in montar_escalacao(G, c, comp, ignorar_baixas=True)
              if not disponivel(G, p, comp)]
    desgastados = [pid for pid, _ in vagas if jogs[pid]["cond"] < 45]
    pendurados = [pid for pid, _ in vagas
                  if jogs[pid].get("amar", {}).get(comp, 0) >= 2]

    # improviso estrutural: a vaga pede mais naturais do que o elenco tem aptos.
    # Ai nem a maquina resolve trocando nomes - so outra formacao ou o mercado.
    naturais_aptos: Dict[str, int] = {}
    for p in c["elenco"]:
        if disponivel(G, p, comp):
            naturais_aptos[jogs[p]["pos"]] = naturais_aptos.get(jogs[p]["pos"], 0) + 1
    faltam_no_elenco = [v for v in POS if form.get(v, 0) > naturais_aptos.get(v, 0)]
    estrutural = bool(graves) and all(v in faltam_no_elenco for _, v in graves)
    # o mesmo para o improviso leve: zagueiro de lateral a 80% porque nao ha lateral
    estrutural_leve = (not graves and bool(improvisados)
                       and all(v in faltam_no_elenco for _, v in improvisados))

    ataque, defesa = forcas_de(G, c, esc)
    ideal = montar_escalacao(G, c, comp)
    at_ideal, de_ideal = forcas_de(G, c, ideal)
    sobra = (at_ideal + de_ideal) - (ataque + defesa)
    tem_jogo = bool(jogos_da_semana(G, c["id"])) and G["fase"] != "entretemporada"

    def nome(pid):
        return jogs[pid]["nome"]

    causas: List[str] = []
    if not tem_goleiro:
        causas.append("ninguem no gol")
    if len(esc) < 11:
        causas.append("so %d em campo" % len(esc))
    for pid, vaga in graves:
        causas.append("%s de %s rende %d%%"
                      % (nome(pid), vaga, int(AFINIDADE[jogs[pid]["pos"]][vaga] * 100)))
    if caidos:
        causas.append("%s fora" % plural(len(caidos), "titular", "titulares"))
    leves = [t for t in improvisados if t not in graves]
    if leves:
        causas.append(plural(len(leves), "improvisado"))
    if desgastados:
        causas.append("%d no limite fisico" % len(desgastados))

    # ---- os degraus, na ordem: o primeiro que bate define o titulo do aviso
    estado, titulo_aviso, detalhe = "ok", "", ""
    if not tem_jogo:
        estado = "neutro"
        titulo_aviso = "SEM JOGO NA SEMANA"
        detalhe = ("Pre-temporada. Use o mercado antes que a liga comece."
                   if G["fase"] == "entretemporada"
                   else "Semana livre. O elenco descansa e recupera condicao.")
    elif len(esc) < 11:
        estado = "critico"
        titulo_aviso = "TIME QUEBRADO - so %d jogadores em campo" % len(esc)
        detalhe = ("Faltam %d. Com esse buraco o time inteiro rende %d%%."
                   % (11 - len(esc), int((0.74 + 0.024 * len(esc)) * 100)))
    elif not tem_goleiro:
        estado = "critico"
        titulo_aviso = "TIME QUEBRADO - ninguem no gol"
        detalhe = "A defesa cai 38% se a semana avancar assim."
    elif graves and estrutural:
        # o time esta quebrado do mesmo jeito, mas a culpa e do elenco, nao da
        # escalacao: dizer isso evita o usuario achar que o automatico falhou
        estado = "critico"
        pid, vaga = graves[0]
        tem = naturais_aptos.get(vaga, 0)
        titulo_aviso = ("LIMITE DO ELENCO - %s: %s joga de %s e rende %d%%"
                        % ("voce nao tem %s aptos" % PLURAL_POS[vaga] if tem == 0
                           else "so %d %s %s" % (tem, NOME_POS[vaga].lower(), "apto" if tem == 1 else "aptos"),
                           nome(pid), vaga, int(AFINIDADE[jogs[pid]["pos"]][vaga] * 100)))
        detalhe = ("A formacao pede %d %s e o elenco tem %d. %sTroque a formacao ou contrate."
                   % (form.get(vaga, 0), PLURAL_POS[vaga], tem,
                      "O automatico ja escalou o melhor possivel. " if auto else ""))
    elif graves:
        estado = "critico"
        pid, vaga = graves[0]
        titulo_aviso = ("TIME QUEBRADO - %s joga de %s e rende so %d%%"
                        % (nome(pid), vaga, int(AFINIDADE[jogs[pid]["pos"]][vaga] * 100)))
        detalhe = "Fora de posicao abaixo de 60% custa mais que jogar com dez."
    elif improvisados:
        estado = "atencao"
        medio = sum(AFINIDADE[jogs[p]["pos"]][v] for p, v in improvisados) / len(improvisados)
        if estrutural_leve:
            vaga = improvisados[0][1]
            tem = naturais_aptos.get(vaga, 0)
            titulo_aviso = ("LIMITE DO ELENCO - %s: %s em campo"
                            % ("voce nao tem %s aptos" % PLURAL_POS[vaga] if tem == 0
                               else "so %d %s %s" % (tem, NOME_POS[vaga].lower(), "apto" if tem == 1 else "aptos"),
                               plural(len(improvisados), "improvisado")))
            detalhe = ("A formacao pede %d %s e o elenco tem %d. Rendimento medio do improviso: "
                       "%d%%. %sTroque a formacao ou contrate."
                       % (form.get(vaga, 0), PLURAL_POS[vaga], tem, int(medio * 100),
                          "O automatico ja escalou o melhor possivel. " if auto else ""))
        else:
            titulo_aviso = "ESCALACAO COM RESSALVA - %s em campo" % plural(len(improvisados), "improvisado")
            detalhe = ("Rendimento medio do improviso: %d%%. Da para jogar, mas voce perde forca."
                       % int(medio * 100))
    elif len(desgastados) >= 3:
        estado = "atencao"
        titulo_aviso = ("ESCALACAO COM RESSALVA - %s no limite fisico"
                        % plural(len(desgastados), "titular", "titulares"))
        detalhe = "Abaixo de 45 de fisico o jogador rende menos e machuca mais."
    elif aptos < 14:
        estado = "atencao"
        titulo_aviso = "ELENCO CURTO - so %d jogadores aptos" % aptos
        detalhe = "Sem banco de verdade, a proxima lesao vira time incompleto."
    # pendurado nao vira mais faixa de alerta (pedido do testador, 26/09/2026):
    # a marca discreta fica no jogador, em diagnostico["pendurados"] e na Escalacao
    elif caidos:
        estado = "atencao"
        titulo_aviso = "ESCALACAO REFEITA - %s fora" % plural(len(caidos), "titular", "titulares")
        detalhe = (("A maquina ja repos: %s de fora, alguem assumiu a vaga."
                    if auto else
                    "Repusemos sem te perguntar: %s de fora. Confira quem entrou.")
                   % ", ".join(nome(p) for p in caidos[:3]))
    else:
        estado = "ok"
        titulo_aviso = "TIME PRONTO PARA A SEMANA"
        # ataque e defesa ficam na barra do proximo jogo e no campo da
        # Escalacao; repetir aqui era o mesmo numero duas vezes na tela
        detalhe = "11 em campo, goleiro no gol, nenhum improvisado."

    return {
        "auto": auto,
        "estado": estado,
        "titulo": titulo_aviso,
        "detalhe": detalhe,
        "causas": causas,
        "tem_jogo": tem_jogo,
        "escalacao": esc,
        "vagas": vagas,
        "formacao": rotulo_formacao(c),
        "tatica": c["tatica"],
        "estrutural": estrutural or estrutural_leve,
        "faltam_no_elenco": faltam_no_elenco,
        "improvisados": improvisados,
        "graves": graves,
        "afinidade_minima": afin_min,
        "tem_goleiro": tem_goleiro,
        "completo": len(esc) >= 11,
        "aptos": aptos,
        "desfalques": desfalques,
        "lesionados": lesionados,
        "suspensos": suspensos,
        "caidos": caidos,
        "desgastados": desgastados,
        "pendurados": pendurados,
        "ataque": ataque,
        "defesa": defesa,
        "ataque_ideal": at_ideal,
        "defesa_ideal": de_ideal,
        "sobra": sobra,
    }



# ----------------------------------------------------------------------------
# MOTOR DE PARTIDA
# ----------------------------------------------------------------------------

def sorteia_autor(G, esc, pesos, vagas=None):
    """Quem finaliza (ou da o passe). Pesa pela VAGA em que o jogador esta.

    Usava j["pos"], a posicao de origem: um atacante improvisado na zaga
    continuava com peso de gol de atacante, enquanto forcas_de ja o tratava
    como zagueiro rendendo 45%. As duas metades do motor discordavam sobre
    onde o jogador estava em campo.
    """
    cand, w = [], []
    for pid in esc:
        j = G["jogadores"].get(pid)
        if not j:
            continue
        vaga = (vagas or {}).get(pid, j["pos"])
        peso = pesos[vaga] * (0.55 + j["ovr"] / 100.0)
        if peso > 0:
            cand.append(pid)
            w.append(peso)
    if not cand:
        return None
    return rng.choices(cand, weights=w)[0]


def preco_referencia(c: Clube) -> float:
    """O ingresso que a torcida deste tamanho paga sem esvaziar o estadio."""
    return clamp(c["reputacao"] * 0.9, 12, 95)


def manutencao_por_lugar(c: Clube) -> float:
    """Quanto cada lugar do estadio custa por semana (entra em custo_estrutura)."""
    return 0.2 + 0.015 * c["reputacao"]


# Torcida que vai ao estadio num jogo comum, com ingresso de referencia:
# constante da divisao x (reputacao/50)^2. Antes o publico era uma fracao da
# CAPACIDADE, e estadio grande enchia sozinho (Serie D com 8,6 mil por jogo,
# ampliar sempre compensava). Agora o estadio so limita: lugar sobrando e
# manutencao. Medias por divisao perto de A 27 mil, B 11 mil, C 5 mil, D 2,5 mil.
DEMANDA_DIVISAO = {"A": 12_000, "B": 9_000, "C": 7_000, "D": 6_000,
                   "ENG": 15_000, "ESP": 12_000, "GER": 16_000, "ITA": 11_000,
                   "FRA": 10_000, "POR": 7_000, "NED": 8_000, "USA": 8_000, "SAU": 5_000}
DEMANDA_PADRAO = 8_000


def demanda_torcida(c: Clube) -> float:
    k = DEMANDA_DIVISAO.get(c["divisao"], DEMANDA_PADRAO)
    return k * (c["reputacao"] / 50.0) ** 2


def publico_esperado(c: Clube) -> int:
    """Publico de um jogo comum com o ingresso atual (sem sorteio)."""
    elast = clamp(1.35 - 0.55 * (c["preco"] / max(8.0, preco_referencia(c))), 0.15, 1.35) / 0.80
    return int(min(c["capacidade"] * 0.99, demanda_torcida(c) * elast))


MOMENTO_JOGOS = 5            # ultimos jogos de liga que contam para o publico


def momento_do_clube(G: Mundo, c: Clube) -> Tuple[float, str]:
    """Quanto a fase do time mexe no publico: pontos nos ultimos 5 jogos de liga
    (7 e o normal) e a posicao na tabela. De 0,80 a 1,20; 1,0 no comeco do ano.
    Nao sorteia nada."""
    liga = G["ligas"].get(c["divisao"])
    if not liga or liga.get("rodada", 0) < 3:
        return 1.0, ""
    pts, jogos = 0, 0
    for rodada in reversed(liga.get("resultados") or []):
        for casa_id, fora_id, gc, gf in rodada:
            if c["id"] in (casa_id, fora_id):
                pro, contra = (gc, gf) if casa_id == c["id"] else (gf, gc)
                pts += 3 if pro > contra else (1 if pro == contra else 0)
                jogos += 1
        if jogos >= MOMENTO_JOGOS:
            break
    if not jogos:
        return 1.0, ""
    ritmo = pts * MOMENTO_JOGOS / float(jogos)        # pontos numa janela de 5
    ordem = classificacao(G, liga)
    frac = ordem.index(c["id"]) / float(max(1, len(ordem) - 1)) if c["id"] in ordem else 0.5
    fator = clamp(1.0 + 0.025 * (ritmo - 7) + 0.10 * (0.5 - frac), 0.80, 1.20)
    return fator, "%d pontos nos ultimos %s, %do na tabela" % (
        pts, plural(jogos, "jogo"), ordem.index(c["id"]) + 1 if c["id"] in ordem else 0)


def publico_e_renda(G, casa, fora, comp):
    cap = casa["capacidade"]
    rel = fora["reputacao"] / max(30.0, casa["reputacao"])
    # adversario grande e copa enchem mais; 1,0 = jogo comum contra um igual
    jogo = 0.30 + 0.22 * min(1.6, rel)
    if comp != "liga":
        jogo += 0.06
    jogo /= 0.52
    preco_ref = preco_referencia(casa)
    elast = clamp(1.35 - 0.55 * (casa["preco"] / max(8.0, preco_ref)), 0.15, 1.35) / 0.80
    momento = momento_do_clube(G, casa)[0]      # time em boa fase enche o estadio
    pub = int(min(cap * 0.99, demanda_torcida(casa) * jogo * elast * momento * rng.uniform(0.82, 1.18)))
    pub = max(pub, int(cap * 0.02))
    renda = int(pub * casa["preco"])
    return pub, renda


# ----------------------------------------------------------------------------
# PLANO TATICO
#
# A mentalidade (TATICAS) continua sendo o eixo, porque e ela que esta
# calibrada. O plano acrescenta cinco botoes que mexem em COMO o time chega la:
# onde pressiona, onde fica a linha, em que ritmo joga, por onde ataca e como
# sai jogando. Nenhum deles e so vantagem.
#
# Os efeitos entram em tres lugares: posse (quem manda no meio), volume (quantas
# chances saem) e qualidade (o quanto cada chance vale). Trocar volume por
# qualidade e a decisao tatica de verdade: o mesmo xG pode virar 18 chutes de
# fora da area ou 8 chances dentro dela.
# ----------------------------------------------------------------------------

PRESSAO = {
    "Baixa":  dict(posse=-0.05, volume=0.94, qualidade=1.02, concede=0.90, expoe=-0.30,
                   fadiga=-2, cartao=0.85,
                   desc="espera no campo dele, cede a bola e fecha o espaco"),
    "Media":  dict(posse=0.00, volume=1.00, qualidade=1.00, concede=1.00, expoe=0.00,
                   fadiga=0, cartao=1.00, desc="marca a partir do meio, sem exagero"),
    "Alta":   dict(posse=+0.07, volume=1.10, qualidade=0.98, concede=1.14, expoe=+0.35,
                   fadiga=+5, cartao=1.25,
                   desc="sufoca a saida do adversario e paga em espaco atras"),
}
LINHA = {
    "Recuada":   dict(posse=-0.04, concede=0.86, contra=+0.30, fadiga=-1,
                      desc="linha baixa: dificil furar, mas entrega o campo"),
    "Media":     dict(posse=0.00, concede=1.00, contra=0.00, fadiga=0,
                      desc="linha no meio, sem risco extra"),
    "Adiantada": dict(posse=+0.05, concede=1.16, contra=-0.15, fadiga=+3,
                      desc="linha alta comprime o jogo e vive do impedimento"),
}
RITMO = {
    "Cadenciado": dict(posse=+0.05, volume=0.86, qualidade=1.12, fadiga=-4, cartao=0.92,
                       desc="segura a bola, arrisca menos e chega melhor"),
    "Normal":     dict(posse=0.00, volume=1.00, qualidade=1.00, fadiga=0, cartao=1.00,
                       desc="sem instrucao especial de ritmo"),
    "Intenso":    dict(posse=+0.01, volume=1.18, qualidade=0.90, fadiga=+6, cartao=1.12,
                       desc="verticaliza sempre: muito chute, chance pior, elenco moido"),
}
LARGURA = {
    "Fechado": dict(posse=+0.04, volume=0.93, qualidade=1.08,
                    desc="joga por dentro, com menos volume e melhor finalizacao"),
    "Normal":  dict(posse=0.00, volume=1.00, qualidade=1.00, desc="sem preferencia de lado"),
    "Aberto":  dict(posse=-0.02, volume=1.12, qualidade=0.93,
                    desc="abre nas pontas: cruza muito, converte pouco"),
}
SAIDA = {
    "Curta":  dict(posse=+0.06, volume=1.00, qualidade=1.02, expoe=+0.10,
                   desc="sai jogando de tras: domina a bola e erra perto da area"),
    "Direta": dict(posse=-0.07, volume=1.07, qualidade=0.95, expoe=-0.10,
                   desc="lanca na frente: menos posse, mais disputa"),
}

PLANO_PADRAO = {"pressao": "Media", "linha": "Media", "ritmo": "Normal",
                "largura": "Normal", "saida": "Curta"}

EIXOS_PLANO = (("pressao", PRESSAO), ("linha", LINHA), ("ritmo", RITMO),
               ("largura", LARGURA), ("saida", SAIDA))

# peso de cada vaga na disputa do meio-campo
MEIO_W = {"GOL": 0.00, "ZAG": 0.18, "LAT": 0.45, "VOL": 1.00, "MEI": 1.00, "ATA": 0.28}

CHANCES_BASE = 11.5        # chances por jogo de um time medio, antes do plano
MAX_SUBS = 5
BANCO_MAX = 9


def plano_de(c: Optional[Clube]) -> Dict[str, str]:
    """O plano do clube, completado com o padrao. Save antigo entra neutro."""
    plano = dict(PLANO_PADRAO)
    if c:
        guardado = c.get("plano") or {}
        for eixo, tabela in EIXOS_PLANO:
            if guardado.get(eixo) in tabela:
                plano[eixo] = guardado[eixo]
    return plano


def definir_plano(G: Mundo, c: Clube, eixo: str, valor: str) -> Tuple[bool, str]:
    tabela = dict(EIXOS_PLANO).get(eixo)
    if not tabela or valor not in tabela:
        return False, "Instrucao desconhecida."
    plano = dict(plano_de(c))
    plano[eixo] = valor
    c["plano"] = plano
    c["esc_stamp"] = ""
    return True, "%s: %s - %s" % (eixo.capitalize(), valor, tabela[valor]["desc"])


# Instrucao condicional pre-jogo: "se perdendo a partir do 71', Ofensivo". A
# partida ja para no intervalo (46') e na janela dos 70 (71'); e ali que a
# regra e conferida. Vale enquanto a condicao durar: virou o placar, volta a
# mentalidade de antes. Troca so a mentalidade (c["tatica"]), que ja pesa no
# ataque, na defesa, no cansaco e no cartao - custo O(1), sem pausar o jogo.
ESCADA_TATICA = ["Retranca", "Contra-ataque", "Equilibrado", "Ofensivo", "Pressao total"]
MINUTOS_CONDICIONAL = (46, 71)
CONDICOES = ("perdendo", "vencendo")


def condicionais_de(c: Optional[Clube]) -> Dict[str, Optional[Dict[str, Any]]]:
    """As regras do clube, so as validas. Save antigo nao tem nenhuma."""
    out: Dict[str, Optional[Dict[str, Any]]] = {k: None for k in CONDICOES}
    guardado = (c or {}).get("condicionais") or {}
    for cond in CONDICOES:
        r = guardado.get(cond)
        if (isinstance(r, dict) and r.get("minuto") in MINUTOS_CONDICIONAL
                and r.get("tatica") in TATICAS):
            out[cond] = {"minuto": r["minuto"], "tatica": r["tatica"]}
    return out


def definir_condicional(G: Mundo, c: Clube, condicao: str, minuto: Optional[int],
                        tatica: Optional[str]) -> Tuple[bool, str]:
    """minuto vazio (ou 0) apaga a regra daquela condicao."""
    if condicao not in CONDICOES:
        return False, "Condicao desconhecida."
    regras = {k: v for k, v in condicionais_de(c).items() if v}
    if not minuto:
        regras.pop(condicao, None)
        c["condicionais"] = regras
        return True, "Sem instrucao se estiver %s." % condicao
    if minuto not in MINUTOS_CONDICIONAL:
        return False, "A instrucao so vale no intervalo (46') ou aos 71'."
    if tatica not in TATICAS:
        return False, "Mentalidade desconhecida."
    regras[condicao] = {"minuto": int(minuto), "tatica": tatica}
    c["condicionais"] = regras
    return True, "Se estiver %s a partir dos %d': %s." % (condicao, minuto, tatica)


def tatica_condicional(G: Mundo, c: Clube, original: str, pro: int, contra: int,
                       minuto: int) -> str:
    """A mentalidade que o clube usa a partir deste minuto, pelo placar.

    O meu clube segue as regras que eu deixei. A maquina tem regra fixa na
    janela dos 70: perdendo sobe um degrau na escada, vencendo desce um.
    """
    if pro == contra:
        return original
    condicao = "perdendo" if pro < contra else "vencendo"
    if c["id"] == G.get("clube"):
        regra = condicionais_de(c)[condicao]
        if regra and regra["minuto"] <= minuto:
            return regra["tatica"]
        return original
    if minuto < MINUTOS_CONDICIONAL[-1] or original not in ESCADA_TATICA:
        return original
    i = ESCADA_TATICA.index(original) + (1 if condicao == "perdendo" else -1)
    return ESCADA_TATICA[max(0, min(len(ESCADA_TATICA) - 1, i))]


def _efeitos(plano: Dict[str, str]) -> Dict[str, float]:
    """Soma os cinco botoes nos numeros que a partida sabe usar."""
    out = {"posse": 0.0, "volume": 1.0, "qualidade": 1.0, "concede": 1.0,
           "contra": 0.0, "expoe": 0.0, "fadiga": 0.0, "cartao": 1.0}
    for eixo, tabela in EIXOS_PLANO:
        e = tabela[plano[eixo]]
        out["posse"] += e.get("posse", 0.0)
        out["volume"] *= e.get("volume", 1.0)
        out["qualidade"] *= e.get("qualidade", 1.0)
        out["concede"] *= e.get("concede", 1.0)
        out["contra"] += e.get("contra", 0.0)
        out["expoe"] += e.get("expoe", 0.0)
        out["fadiga"] += e.get("fadiga", 0.0)
        out["cartao"] *= e.get("cartao", 1.0)
    return out


def efeitos_plano(c: Optional[Clube]) -> Dict[str, float]:
    """Versao publica, para a interface mostrar o que o plano esta fazendo."""
    return _efeitos(plano_de(c))


def forca_meio(G: Mundo, c: Clube, esc: List[int]) -> float:
    """Quanto este XI pesa na disputa do meio-campo."""
    form = formacao_de(c)
    total = peso = 0.0
    for pid, vaga in atribuir_vagas(G, esc, form, vagas_manuais(c)):
        j = G["jogadores"].get(pid)
        if not j:
            continue
        w = MEIO_W[vaga]
        if w <= 0:
            continue
        total += rendimento(j, AFINIDADE[j["pos"]][vaga]) * w
        peso += w
    return (total / peso) if peso > 0 else 30.0


def posse_de(G: Mundo, casa: Clube, fora: Clube, esc_c: List[int],
             esc_f: List[int]) -> float:
    """Fatia de bola do mandante, de 0 a 1.

    Sai da forca de meio-campo dos dois lados - quem tem mais VOL/MEI bom manda
    no jogo - e do plano tatico. Antes o meio-campo nao disputava nada: o XI
    virava dois numeros (ataque, defesa) e a formacao so mudava quantas vagas
    existiam de cada posicao.
    """
    mc = forca_meio(G, casa, esc_c)
    mf = forca_meio(G, fora, esc_f)
    base = mc / max(1.0, mc + mf)
    base += _efeitos(plano_de(casa))["posse"] - _efeitos(plano_de(fora))["posse"]
    return clamp(base + 0.015, 0.28, 0.72)       # leve vantagem de mando


def _nota_base(j: Jogador, vaga: str) -> float:
    return 6.0 + (rendimento(j, AFINIDADE[j["pos"]][vaga]) - 62.0) / 42.0


def banco_disponivel(G: Mundo, c: Clube, esc: List[int], comp: str = "liga") -> List[int]:
    """Os reservas que podem entrar, do mais pronto para o menos."""
    fora = [p for p in c["elenco"] if p not in esc and disponivel(G, p, comp)
            and not da_base(G["jogadores"][p])]
    fora.sort(key=lambda p: -nota_escalacao(G["jogadores"][p], G["jogadores"][p]["pos"]))
    return fora[:BANCO_MAX]


def _trocar(G, dono, esc, banco, vagas, jogaram, minuto, lado, eventos, subs,
            forcado=None, usadas=0, limite_cond=62):
    """Uma substituicao. Devolve 1 se trocou, 0 se nao deu.

    Quem sai e o mais acabado (ou o lesionado); quem entra e o reserva com
    melhor afinidade com a vaga aberta. So troca se o reserva render mais que
    o titular naquele estado - senao o banco pioraria o time.
    """
    if usadas >= MAX_SUBS or not banco:
        return 0
    if forcado is not None and forcado in esc:
        sai = forcado
    else:
        candidatos = [p for p in esc if G["jogadores"][p]["cond"] < limite_cond
                      and vagas.get(p) != "GOL"]
        if not candidatos:
            return 0
        sai = min(candidatos, key=lambda p: G["jogadores"][p]["cond"])
    vaga = vagas.get(sai, G["jogadores"][sai]["pos"])
    entra = max(banco, key=lambda p: nota_escalacao(G["jogadores"][p], vaga))
    jsai, jentra = G["jogadores"][sai], G["jogadores"][entra]
    if forcado is None:
        # nos ultimos 20 minutos, perna descansada compensa um pouco de
        # qualidade: e por isso que se troca no fim do jogo mesmo quando o
        # reserva e nominalmente pior.
        margem = 0.97 if minuto >= 66 else 1.00
        if rendimento(jentra, AFINIDADE[jentra["pos"]][vaga]) <= \
                rendimento(jsai, AFINIDADE[jsai["pos"]][vaga]) * margem:
            return 0
    esc[esc.index(sai)] = entra
    banco.remove(entra)
    vagas.pop(sai, None)
    vagas[entra] = vaga
    jogaram[entra] = vaga
    eventos.append((minuto, lado, "substituicao", entra, sai))
    subs.append([minuto, lado, sai, entra])
    return 1


def _fadigar(G, esc, minutos, dono, efeitos):
    fad_min, fad_max, _ = CUSTO_TATICA.get(dono["tatica"], (9, 20, 1.0))
    for pid in esc:
        j = G["jogadores"][pid]
        gasto = (rng.uniform(fad_min, fad_max) + efeitos["fadiga"]) * (minutos / 90.0)
        # inteiro: condicao e um numero que o jogador LE na tabela, e 53.9903
        # nao e leitura, e vazamento de conta interna
        j["cond"] = int(round(clamp(j["cond"] - gasto, 5, 100)))


def simular(G, casa_id, fora_id, comp="liga", neutro=False):
    """Uma partida de 90 minutos, em tres periodos, com banco e plano tatico.

    O xG total continua saindo da mesma conta calibrada (forca contra forca,
    EXP_FORCA), mas agora ele e DECOMPOSTO em chances x conversao: o plano
    decide se o time faz muitos chutes ruins ou poucas chances boas, e a
    substituicao muda o time no meio do caminho. A media de gols continua a
    mesma de antes; o que passou a existir e a partida entre o apito inicial e
    o placar final.
    """
    casa, fora = G["clubes"][casa_id], G["clubes"][fora_id]
    cumprir_suspensao(G, casa, comp)
    cumprir_suspensao(G, fora, comp)
    # o XI escalado: o do tecnico (manual ou automatico) e o da maquina. Antes
    # era sempre montar_escalacao, e o time manual nunca entrava em campo
    esc_c = list(escalacao_valida(G, casa, comp)[0])
    esc_f = list(escalacao_valida(G, fora, comp)[0])
    banco_c = banco_disponivel(G, casa, esc_c, comp)
    banco_f = banco_disponivel(G, fora, esc_f, comp)
    form_c = formacao_de(casa)
    form_f = formacao_de(fora)
    vagas_c = dict(atribuir_vagas(G, esc_c, form_c, vagas_manuais(casa)))
    vagas_f = dict(atribuir_vagas(G, esc_f, form_f, vagas_manuais(fora)))
    jogaram_c, jogaram_f = dict(vagas_c), dict(vagas_f)
    ef_c, ef_f = _efeitos(plano_de(casa)), _efeitos(plano_de(fora))

    pub, renda = (0, 0)
    fator_casa = 1.0
    if not neutro:
        pub, renda = publico_e_renda(G, casa, fora, comp)
        fator_casa = 1.10 + 0.10 * (pub / max(1, casa["capacidade"]))
        lancar(G, casa, renda, "bilheteria")
        lancar(G, casa, -int(renda * CUSTO_JOGO_CASA), "operacao_jogo")

    posse = posse_de(G, casa, fora, esc_c, esc_f)
    eventos, subs = [], []
    stats = {"posse": [int(round(posse * 100)), 100 - int(round(posse * 100))],
             "chutes": [0, 0], "no_gol": [0, 0], "escanteios": [0, 0],
             "faltas": [0, 0], "defesas": [0, 0]}
    notas = {}
    for jogaram in (jogaram_c, jogaram_f):
        for pid, vaga in jogaram.items():
            notas[pid] = _nota_base(G["jogadores"][pid], vaga)
    gc = gf = 0
    usadas_c = usadas_f = 0

    # tres periodos: e o que da sentido ao banco. O time que termina o jogo nao
    # e o mesmo que comecou, nem em pernas nem em nomes.
    europeu = comp in COMPS_EUROPA or (comp == "liga" and G["clubes"][casa_id]["divisao"] not in DIVISOES_BR)
    expoente = EXP_FORCA_EUROPA if europeu else EXP_FORCA
    # a mentalidade pode mudar no meio (instrucao condicional); o clube sai do
    # jogo com a que entrou, ate se a partida estourar no meio
    originais = (casa["tatica"], fora["tatica"])
    instrucoes = []
    amarelados: set = set()          # amarelo neste jogo: o segundo e vermelho
    expulsos: List[Tuple[int, int, int, int]] = []
    try:
        for ini, fim, minutos in ((1, 45, 45), (46, 70, 25), (71, 92, 20)):
            if ini > 1:
                for lado, clube, antes in ((0, casa, originais[0]), (1, fora, originais[1])):
                    pro, contra = (gc, gf) if lado == 0 else (gf, gc)
                    nova = tatica_condicional(G, clube, antes, pro, contra, ini)
                    if nova != clube["tatica"]:
                        clube["tatica"] = nova
                        motivo = ("perdendo" if pro < contra else
                                  "vencendo" if pro > contra else "empatado")
                        instrucoes.append([ini, lado, nova, motivo])
            at_c, de_c = forcas_de(G, casa, esc_c)
            at_f, de_f = forcas_de(G, fora, esc_f)
            xg_c = 1.22 * ((at_c / max(25.0, de_f)) ** expoente) * fator_casa
            xg_f = 1.10 * ((at_f / max(25.0, de_c)) ** expoente)
            # concede > 1 quer dizer "este time entrega mais chance": ele MULTIPLICA
            # o xG de quem esta atacando. Dividir fazia linha alta defender melhor.
            xg_c *= ef_c["qualidade"] * ef_c["volume"] * ef_f["concede"]
            xg_f *= ef_f["qualidade"] * ef_f["volume"] * ef_c["concede"]
            # transicao: quem espera atras castiga quem sobe demais a linha
            xg_c *= 1.0 + ef_c["contra"] * max(0.0, ef_f["expoe"])
            xg_f *= 1.0 + ef_f["contra"] * max(0.0, ef_c["expoe"])
            xg_c *= rng.uniform(0.82, 1.20) * (minutos / 90.0)
            xg_f *= rng.uniform(0.82, 1.20) * (minutos / 90.0)

            for lado, xg, esc, adv_vagas, ef in ((0, xg_c, esc_c, vagas_f, ef_c),
                                                 (1, xg_f, esc_f, vagas_c, ef_f)):
                if not esc:
                    continue
                fatia = posse if lado == 0 else (1.0 - posse)
                chances = CHANCES_BASE * (0.55 + 0.9 * fatia) * ef["volume"] * (minutos / 90.0)
                chances = max(1, int(round(chances * rng.uniform(0.8, 1.2))))
                conversao = clamp(xg / chances, 0.005, 0.60)
                vagas = vagas_c if lado == 0 else vagas_f
                for _ in range(chances):
                    stats["chutes"][lado] += 1
                    minuto = rng.randint(ini, fim)
                    sorte = rng.random()
                    if sorte < conversao:
                        stats["no_gol"][lado] += 1
                        autor = sorteia_autor(G, esc, GOL_W, vagas)
                        assist = sorteia_autor(G, esc, ASS_W, vagas)
                        if assist == autor:
                            assist = None
                        if autor:
                            ja = G["jogadores"][autor]
                            ja["g"] += 1
                            ja["car_g"] += 1
                            ja["g_mes"] = ja.get("g_mes", 0) + 1
                            notas[autor] = notas.get(autor, 6.0) + 1.0
                        if assist:
                            js = G["jogadores"][assist]
                            js["a"] += 1
                            js["a_mes"] = js.get("a_mes", 0) + 1
                            notas[assist] = notas.get(assist, 6.0) + 0.5
                        eventos.append((minuto, lado, "gol", autor, assist))
                        if lado == 0:
                            gc += 1
                        else:
                            gf += 1
                    elif sorte < conversao + 0.30:
                        stats["no_gol"][lado] += 1
                        stats["defesas"][1 - lado] += 1
                        goleiro = next((p for p, v in adv_vagas.items() if v == "GOL"), None)
                        if goleiro:
                            notas[goleiro] = notas.get(goleiro, 6.0) + 0.10
                    elif sorte < conversao + 0.55:
                        stats["escanteios"][lado] += 1

            # cartoes, faltas e lesoes do periodo
            for lado, esc, dono, ef in ((0, esc_c, casa, ef_c), (1, esc_f, fora, ef_f)):
                vagas = vagas_c if lado == 0 else vagas_f
                jogaram = jogaram_c if lado == 0 else jogaram_f
                banco = banco_c if lado == 0 else banco_f
                _, _, mult_cartao = CUSTO_TATICA.get(dono["tatica"], (9, 20, 1.0))
                mult_cartao *= ef["cartao"]
                for pid in list(esc):
                    j = G["jogadores"][pid]
                    peso = RISCO_CARTAO[vagas.get(pid, j["pos"])] * mult_cartao * (minutos / 90.0)
                    if rng.random() < 0.55 * peso:
                        stats["faltas"][lado] += 1
                    if rng.random() < 0.214 * peso:
                        j["ca"] += 1
                        notas[pid] = notas.get(pid, 6.0) - 0.25
                        minuto_cartao = rng.randint(ini, fim)
                        eventos.append((minuto_cartao, lado, "amarelo", pid, None))
                        if pid in amarelados:
                            # segundo amarelo no jogo: vermelho. Ele nao entra no
                            # acumulado da competicao; a expulsao suspende um jogo
                            j["cv"] += 1
                            j["susp"][comp] = j["susp"].get(comp, 0) + 1
                            sincronizar_suspensao(j)
                            notas[pid] = notas.get(pid, 6.0) - 1.0
                            eventos.append((minuto_cartao, lado, "vermelho", pid, None))
                            expulsos.append((pid, len(eventos) - 1, ini, fim))
                            esc.remove(pid)
                            continue
                        amarelados.add(pid)
                        j["amar"][comp] = j["amar"].get(comp, 0) + 1
                        if j["amar"][comp] >= 3:
                            j["amar"][comp] = 0
                            j["susp"][comp] = j["susp"].get(comp, 0) + 1
                            sincronizar_suspensao(j)
                    if rng.random() < 0.013 * peso:
                        j["cv"] += 1
                        j["susp"][comp] = j["susp"].get(comp, 0) + 1 + rng.randint(0, 2)
                        sincronizar_suspensao(j)
                        notas[pid] = notas.get(pid, 6.0) - 1.5
                        eventos.append((rng.randint(ini, fim), lado, "vermelho", pid, None))
                        expulsos.append((pid, len(eventos) - 1, ini, fim))
                        esc.remove(pid)              # expulso sai de campo de verdade
                        continue
                    risco = RISCO_LESAO_JOGO * (1.0 - 0.05 * dono["medico"]) * (minutos / 90.0)
                    risco *= risco_lesao_treino(G, dono)
                    risco *= 1.0 + 1.6 * max(0.0, (55 - j["cond"]) / 55.0)
                    if rng.random() < risco:
                        j["lesao"] = rng.choice(SEMANAS_LESAO) + 1
                        if j["ovr"] >= CRAQUE_OVR and j["lesao"] >= LESAO_MANCHETE:
                            manchete(G, "lesao", "%s, do %s, se machuca e fica %d semanas fora." % (
                                j["nome"], dono["nome"], j["lesao"]))
                        eventos.append((rng.randint(ini, fim), lado, "lesao", pid, None))
                        usou = _trocar(G, dono, esc, banco, vagas, jogaram,
                                       rng.randint(ini, fim), lado, eventos, subs,
                                       forcado=pid,
                                       usadas=usadas_c if lado == 0 else usadas_f)
                        if lado == 0:
                            usadas_c += usou
                        else:
                            usadas_f += usou

            # o periodo sorteia os gols antes dos cartoes, cada evento com minuto
            # proprio: o expulso nao pode aparecer depois da expulsao. O cartao
            # vai para depois do ultimo lance dele no periodo (sem mexer no rng)
            for pid, k, p_ini, p_fim in expulsos:
                m = eventos[k][0]
                # o segundo amarelo, colado no vermelho, anda junto com ele
                par = k - 1 if (k > 0 and eventos[k - 1][2] == "amarelo"
                                and eventos[k - 1][3] == pid and eventos[k - 1][0] == m) else None
                ultimo = max((e[0] for i, e in enumerate(eventos)
                              if i not in (k, par) and p_ini <= e[0] <= p_fim
                              and pid in (e[3], e[4])), default=None)
                if ultimo is not None and ultimo >= m:
                    novo = min(p_fim, ultimo + 1)
                    eventos[k] = (novo,) + tuple(eventos[k][1:])
                    if par is not None:
                        eventos[par] = (novo,) + tuple(eventos[par][1:])
            expulsos.clear()

            _fadigar(G, esc_c, minutos, casa, ef_c)
            _fadigar(G, esc_f, minutos, fora, ef_f)

            if fim < 90:
                # janela de substituicao. O limite sobe a cada parada: no intervalo
                # so sai quem ja esta ruim, no fim do jogo troca-se perna cansada.
                limite = 70 if fim <= 45 else 84
                for _ in range(3):
                    usadas_c += _trocar(G, casa, esc_c, banco_c, vagas_c, jogaram_c,
                                        fim + 1, 0, eventos, subs, usadas=usadas_c,
                                        limite_cond=limite)
                    usadas_f += _trocar(G, fora, esc_f, banco_f, vagas_f, jogaram_f,
                                        fim + 1, 1, eventos, subs, usadas=usadas_f,
                                        limite_cond=limite)
    finally:
        casa["tatica"], fora["tatica"] = originais

    # partida disputada conta para todo mundo que entrou em campo, titular ou nao
    for jogaram in (jogaram_c, jogaram_f):
        for pid in jogaram:
            j = G["jogadores"].get(pid)
            if not j:
                continue
            j["j"] += 1
            j["car_j"] += 1
            j["j_mes"] = j.get("j_mes", 0) + 1
            if entrosamento(j) < 100:
                j["entros"] = min(100, entrosamento(j) + ENTROS_POR_JOGO)

    for lado, jogaram in ((0, jogaram_c), (1, jogaram_f)):
        pro, contra = (gc, gf) if lado == 0 else (gf, gc)
        bonus = 0.5 if pro > contra else (0.0 if pro == contra else -0.4)
        for pid, vaga in jogaram.items():
            nota = notas.get(pid, 6.0) + bonus
            if vaga in ("GOL", "ZAG", "LAT") and contra == 0:
                nota += 0.5
            elif vaga in ("GOL", "ZAG") and contra >= 3:
                nota -= 0.5
            notas[pid] = round(clamp(nota, 3.0, 10.0), 1)
            j = G["jogadores"].get(pid)
            if j:
                # media do ano = nota_soma / nota_j (nota_j e separado de j["j"]:
                # save antigo tem jogos sem nota, e a media nao pode inventa-las)
                j["nota_soma"] = round(j.get("nota_soma", 0.0) + notas[pid], 1)
                j["nota_j"] = j.get("nota_j", 0) + 1

    classico = eh_classico(G, casa_id, fora_id)
    aplicar_moral(G, list(jogaram_c), gc, gf, fora["nome"], classico)
    aplicar_moral(G, list(jogaram_f), gf, gc, casa["nome"], classico)
    eventos.sort(key=lambda e: e[0])
    return {"casa": casa_id, "fora": fora_id, "gc": gc, "gf": gf,
            "pub": pub, "renda": renda, "eventos": eventos, "comp": comp,
            "stats": stats, "notas": notas, "subs": subs, "instrucoes": instrucoes,
            "xi": {"casa": jogaram_c, "fora": jogaram_f}}


MORAL_HIST = 5          # causas de moral guardadas por jogador (so do meu clube)
PESO_CLASSICO_MORAL = 2  # vitoria ou derrota em classico mexe o dobro na moral


def anotar_moral(G: Mundo, j: Jogador, delta: int, causa: str) -> None:
    """Guarda a causa da mudanca de moral, para a ficha explicar o numero.
    So para quem esta no meu clube: o resto do mundo nao aparece em lugar
    nenhum e encheria o save."""
    if not delta or j.get("clube") != G.get("clube"):
        return
    hist = j.setdefault("moral_hist", [])
    hist.append([semana_absoluta(G), int(delta), causa])
    del hist[:-MORAL_HIST]


def mexer_moral(G: Mundo, j: Jogador, delta: int, causa: str) -> None:
    antes = j["moral"]
    j["moral"] = clamp(j["moral"] + delta, 5, 100)
    anotar_moral(G, j, j["moral"] - antes, causa)


def aplicar_moral(G, esc, pro, contra, rival=None, classico=False):
    if pro > contra:
        dm, df, fato = 3, 3, "vitoria"
    elif pro == contra:
        dm, df, fato = 1, 1, "empate"
    else:
        dm, df, fato = -3, -3, "derrota"
    if classico and pro != contra:
        dm *= PESO_CLASSICO_MORAL
    causa = "%s %s%s" % (fato, "no classico contra o " if classico else
                         {"vitoria": "sobre o ", "empate": "com o ", "derrota": "para o "}[fato],
                         rival or "adversario")
    causa += " (%d x %d)" % (pro, contra)
    # o capitao em campo segura um ponto da queda na derrota
    if pro < contra and esc and esc[0] in G["jogadores"]:
        clube = G["clubes"].get(G["jogadores"][esc[0]]["clube"])
        if clube and capitao_de(G, clube) in esc:
            dm += 1
    for pid in esc:
        j = G["jogadores"][pid]
        antes = j["moral"]
        m = j["moral"] + dm + rng.randint(-2, 2)
        f = j["forma"] + df + rng.randint(-6, 6)
        # puxao de volta para a media: sem isto, moral vira espiral divergente e
        # o campeonato passa a separar times por historico em vez de por elenco.
        j["moral"] = int(round(clamp(m + 0.12 * (65 - m), 5, 100)))
        j["forma"] = int(round(clamp(f + 0.12 * (65 - f), 5, 100)))
        anotar_moral(G, j, j["moral"] - antes, causa)


def penaltis(G: Mundo, a: int, b: int, comp: str = "liga") -> int:
    at_a, de_a, _ = forcas(G, G["clubes"][a], comp)
    at_b, de_b, _ = forcas(G, G["clubes"][b], comp)
    fa, fb = at_a + de_a, at_b + de_b
    p = fa / (fa + fb)
    return a if rng.random() < p * 0.92 + 0.04 else b


# ----------------------------------------------------------------------------
# TABELA E CLASSIFICACAO
# ----------------------------------------------------------------------------

def registrar(liga, casa, fora, gc, gf):
    t = liga["tabela"]
    a, b = t[str(casa)], t[str(fora)]
    a["j"] += 1; b["j"] += 1
    a["gp"] += gc; a["gc"] += gf
    b["gp"] += gf; b["gc"] += gc
    if gc > gf:
        a["p"] += 3; a["v"] += 1; b["d"] += 1
    elif gc < gf:
        b["p"] += 3; b["v"] += 1; a["d"] += 1
    else:
        a["p"] += 1; b["p"] += 1; a["e"] += 1; b["e"] += 1


def classificacao(G, liga):
    ids = liga["times"]
    def chave(i):
        t = liga["tabela"][str(i)]
        return (-t["p"], -t["v"], -(t["gp"] - t["gc"]), -t["gp"], G["clubes"][i]["nome"])
    return sorted(ids, key=chave)


def posicao_na_liga(G, cid):
    c = G["clubes"][cid]
    if c["divisao"] not in G["ligas"]:
        return 0
    return classificacao(G, G["ligas"][c["divisao"]]).index(cid) + 1


# ----------------------------------------------------------------------------
# ESTADUAIS
#
# Abrem o ano, como no calendario de verdade: primeiro o estadual, depois o
# Brasileirao. Eles vivem na fase "estadual", com contador proprio
# (semana_est), para nao baguncar o calendario da liga nem as janelas de
# mercado, que andam por G["semana"].
#
# Formato: o da vida real. Uma primeira fase (tabela unica ou grupos) e depois
# mata-mata ate a final em ida e volta. O Paulistao tem quatro grupos em que
# cada clube enfrenta os dos OUTROS grupos, e as quartas saem de dentro do
# grupo (1o x 2o); o Carioca tem a Taca Guanabara e semifinal; a Copa do
# Nordeste tem dois grupos cruzados e quartas 1o x 4o, 2o x 3o. Mata-mata:
# jogo unico na casa de quem fez a melhor campanha; ida e volta com a volta na
# casa dela. Empate (ou agregado igual) vai para os penaltis - sem gol fora.
#
# Estado com poucos clubes joga um torneio regional, que e o que o futebol
# brasileiro faz de fato (Copa Verde, Copa do Nordeste).
# ----------------------------------------------------------------------------

MIN_ESTADUAL = 4          # abaixo disso o estado nao sustenta campeonato proprio

# Premio do campeao por porte do torneio, pela mesma chave de FORMATOS_ESTADUAL.
# Paulistao muito acima, RJ/MG/RS num segundo patamar e os regionais (Copa do
# Nordeste, Copa Verde) no piso. Somado a reputacao do campeao, como antes.
PREMIO_ESTADUAL = {
    "uf-SP": 2_600_000,
    "uf-RJ": 1_500_000,
    "uf-MG": 1_500_000,
    "uf-RS": 1_500_000,
    "reg-Nordeste": 450_000,
    "reg-Verde": 450_000,
}
# chave fora do dicionario: o estadual generico de _formato_estadual, pelo
# tamanho (n >= 6, n == 5, menor), e qualquer outro regional no piso
PREMIO_ESTADUAL_GENERICO = ((6, 1_000_000), (5, 800_000), (0, 600_000))
PREMIO_REGIONAL = 450_000


def premio_estadual(est: Dict[str, Any]) -> int:
    """Base do premio do campeao deste estadual (sem a parte da reputacao)."""
    chave = est.get("chave", "")
    if chave in PREMIO_ESTADUAL:
        return PREMIO_ESTADUAL[chave]
    if chave.startswith("reg-"):
        return PREMIO_REGIONAL
    n = len(est.get("times", []))
    return next(v for minimo, v in PREMIO_ESTADUAL_GENERICO if n >= minimo)

UF_NOME = {
    "AC": "Acreano", "AL": "Alagoano", "AM": "Amazonense", "AP": "Amapaense",
    "BA": "Baiano", "CE": "Cearense", "DF": "Brasiliense", "ES": "Capixaba",
    "GO": "Goiano", "MA": "Maranhense", "MG": "Mineiro", "MS": "Sul-Mato-Grossense",
    "MT": "Mato-Grossense", "PA": "Paraense", "PB": "Paraibano", "PE": "Pernambucano",
    "PI": "Piauiense", "PR": "Paranaense", "RJ": "Carioca", "RN": "Potiguar",
    "RO": "Rondoniense", "RR": "Roraimense", "RS": "Gaucho", "SC": "Catarinense",
    "SE": "Sergipano", "SP": "Paulista", "TO": "Tocantinense",
}

REGIAO_UF = {
    "AC": "Verde", "AM": "Verde", "AP": "Verde", "PA": "Verde", "RO": "Verde",
    "RR": "Verde", "TO": "Verde", "MT": "Verde", "MS": "Verde", "DF": "Verde", "GO": "Verde",
    "MA": "Nordeste", "PI": "Nordeste", "CE": "Nordeste", "RN": "Nordeste",
    "PB": "Nordeste", "PE": "Nordeste", "AL": "Nordeste", "SE": "Nordeste", "BA": "Nordeste",
    "MG": "Regional", "ES": "Regional", "RJ": "Regional", "SP": "Regional",
    "PR": "Regional", "SC": "Regional", "RS": "Regional",
}

NOME_REGIONAL = {"Verde": "Copa Verde", "Nordeste": "Copa do Nordeste",
                 "Regional": "Copa Regional"}

# Classicos do futebol brasileiro, pelo "nome" do clube no jogo (os reais, sem
# acento). A relacao e simetrica: basta listar de um lado, CLASSICOS completa.
CLASSICOS_POR_NOME = {
    # Rio
    "Flamengo": ["Fluminense", "Vasco da Gama", "Botafogo"],
    "Fluminense": ["Vasco da Gama", "Botafogo"],
    "Vasco da Gama": ["Botafogo"],
    # Sao Paulo: o quadrangular dos grandes, mais os de Campinas
    "Corinthians": ["Palmeiras", "Sao Paulo", "Santos"],
    "Palmeiras": ["Sao Paulo", "Santos"],
    "Sao Paulo": ["Santos"],
    "Ponte Preta": ["Guarani"],
    # Minas, Rio Grande do Sul, Parana, Santa Catarina
    "Atletico-MG": ["Cruzeiro", "America-MG"],
    "Cruzeiro": ["America-MG"],
    "Gremio": ["Internacional"],
    "Juventude": ["Caxias"],
    "Athletico-PR": ["Coritiba"],
    "Avai": ["Figueirense"],
    # Nordeste
    "Bahia": ["Vitoria"],
    "Sport": ["Nautico", "Santa Cruz"],
    "Nautico": ["Santa Cruz"],
    "Fortaleza": ["Ceara"],
    "CRB": ["CSA"],
    "ABC": ["America-RN"],
    "Treze": ["Campinense", "Botafogo-PB"],
    "Campinense": ["Botafogo-PB"],
    # Norte e Centro-Oeste
    "Paysandu": ["Remo"],
    "Goias": ["Vila Nova", "Atletico-GO"],
    "Vila Nova": ["Atletico-GO"],
}
CLASSICOS = {frozenset((a, b)) for a, rivais in CLASSICOS_POR_NOME.items() for b in rivais}

# o apelido, quando o classico tem um
NOME_CLASSICO = {
    frozenset(("Flamengo", "Fluminense")): "Fla-Flu",
    frozenset(("Flamengo", "Vasco da Gama")): "Classico dos Milhoes",
    frozenset(("Botafogo", "Fluminense")): "Classico Vovo",
    frozenset(("Corinthians", "Palmeiras")): "Derby Paulista",
    frozenset(("Palmeiras", "Sao Paulo")): "Choque-Rei",
    frozenset(("Corinthians", "Sao Paulo")): "Majestoso",
    frozenset(("Santos", "Sao Paulo")): "San-Sao",
    frozenset(("Corinthians", "Santos")): "Classico Alvinegro",
    frozenset(("Palmeiras", "Santos")): "Classico da Saudade",
    frozenset(("Guarani", "Ponte Preta")): "Derby Campineiro",
    frozenset(("Gremio", "Internacional")): "Gre-Nal",
    frozenset(("Caxias", "Juventude")): "Ca-Ju",
    frozenset(("Atletico-MG", "Cruzeiro")): "Classico Mineiro",
    frozenset(("Athletico-PR", "Coritiba")): "Atletiba",
    frozenset(("Bahia", "Vitoria")): "Ba-Vi",
    frozenset(("Nautico", "Sport")): "Classico dos Classicos",
    frozenset(("Santa Cruz", "Sport")): "Classico das Multidoes",
    frozenset(("Ceara", "Fortaleza")): "Classico-Rei",
    frozenset(("Paysandu", "Remo")): "Re-Pa",
}


def eh_classico(G: Mundo, casa_id: int, fora_id: int) -> bool:
    casa, fora = G["clubes"].get(casa_id), G["clubes"].get(fora_id)
    return bool(casa and fora and frozenset((casa["nome"], fora["nome"])) in CLASSICOS)


def nome_classico(G: Mundo, casa_id: int, fora_id: int) -> str:
    par = frozenset((G["clubes"][casa_id]["nome"], G["clubes"][fora_id]["nome"]))
    return NOME_CLASSICO.get(par, "Classico")

# fases do mata-mata: (nome, ida e volta?)
_QUARTAS = ("Quartas de final", False)
_SEMI_UNICA = ("Semifinal", False)
_SEMI_IV = ("Semifinal", True)
_FINAL_IV = ("Final", True)

# fase1: "turno" (todos contra todos, uma vez), "returno" (ida e volta) ou
# "cruzado" (grupos; cada clube enfrenta os dos outros grupos).
# no_grupo: o primeiro mata-mata cruza dentro do grupo (1o x ultimo classificado).
# Passam da primeira fase 2 ** len(mata) clubes, divididos pelos grupos.
FORMATOS_ESTADUAL = {
    "uf-SP": {"fase1": "cruzado", "grupos": 4, "nome1": "Fase de grupos",
              "mata": [_QUARTAS, _SEMI_UNICA, _FINAL_IV], "no_grupo": True},
    "uf-RJ": {"fase1": "turno", "grupos": 1, "nome1": "Taca Guanabara",
              "mata": [_SEMI_IV, _FINAL_IV]},
    "uf-MG": {"fase1": "turno", "grupos": 1, "nome1": "Primeira fase",
              "mata": [_SEMI_IV, _FINAL_IV]},
    "uf-RS": {"fase1": "turno", "grupos": 1, "nome1": "Primeira fase",
              "mata": [_SEMI_IV, _FINAL_IV]},
    "reg-Nordeste": {"fase1": "cruzado", "grupos": 2, "nome1": "Fase de grupos",
                     "mata": [_QUARTAS, _SEMI_UNICA, _FINAL_IV], "no_grupo": True},
}


def _formato_estadual(chave: str, n: int) -> Dict[str, Any]:
    """O formato do torneio, se o numero de clubes aguentar; senao, o de um
    estadual pequeno de verdade (turno e mata-mata curto)."""
    fmt = FORMATOS_ESTADUAL.get(chave)
    if fmt:
        vagas = 2 ** len(fmt["mata"])
        g = fmt["grupos"]
        por = vagas // g
        # cada grupo precisa de mais clubes do que vagas, senao a fase e enfeite
        if vagas % g == 0 and n >= g * (por + 1) and n > vagas:
            return dict(fmt)
    if n >= 6:
        return {"fase1": "turno", "grupos": 1, "nome1": "Primeira fase",
                "mata": [_SEMI_IV, _FINAL_IV]}
    if n == 5:
        return {"fase1": "turno", "grupos": 1, "nome1": "Primeira fase",
                "mata": [_SEMI_UNICA, _FINAL_IV]}
    return {"fase1": "returno", "grupos": 1, "nome1": "Primeira fase", "mata": [_FINAL_IV]}


def _grupos_estaduais(G: Mundo) -> List[Tuple[str, str, List[int]]]:
    """Monta os torneios do ano: (chave, nome, ids dos clubes).

    Estado com MIN_ESTADUAL clubes ou mais joga o proprio campeonato. O resto
    se junta por regiao. Grupo que ainda assim nao fecha quatro clubes fica de
    fora do ano - e melhor descansar do que jogar um torneio de dois.
    """
    por_uf: Dict[str, List[int]] = {}
    for c in G["clubes"].values():
        if not brasileiro(c):
            continue
        por_uf.setdefault(c["uf"], []).append(c["id"])
    grupos, sobras = [], {}
    for uf, ids in sorted(por_uf.items()):
        if len(ids) >= MIN_ESTADUAL:
            grupos.append(("uf-" + uf, "Campeonato " + UF_NOME.get(uf, uf), ids))
        else:
            sobras.setdefault(REGIAO_UF.get(uf, "Regional"), []).extend(ids)
    for regiao, ids in sorted(sobras.items()):
        if len(ids) >= MIN_ESTADUAL:
            grupos.append(("reg-" + regiao, NOME_REGIONAL[regiao], ids))
    return grupos


def _turno_completo(ids: List[int]) -> List[List[List[int]]]:
    """Todos contra todos uma vez. gerar_rodadas pressupoe numero par de
    clubes; com impar entra um fantasma e quem o enfrenta folga na rodada."""
    t = list(ids)
    if len(t) % 2:
        t.append(None)
    turno = gerar_rodadas(t)[:len(t) - 1]
    return [[j for j in rd if None not in j] for rd in turno]


def _encaixar_rodadas(pares: List[Tuple[int, int]]) -> List[List[List[int]]]:
    """Distribui jogos avulsos em rodadas: ninguem joga duas vezes na mesma
    rodada e, quanto menos rodadas, melhor. Guloso, varias tentativas, dando
    preferencia a quem ainda tem mais jogo pela frente."""
    melhor = None
    for _ in range(120):
        resto = list(pares)
        rng.shuffle(resto)
        rodadas = []
        while resto:
            falta: Dict[int, int] = {}
            for a, b in resto:
                falta[a] = falta.get(a, 0) + 1
                falta[b] = falta.get(b, 0) + 1
            resto.sort(key=lambda p: -(falta[p[0]] + falta[p[1]]))
            usados, rodada, sobra = set(), [], []
            for a, b in resto:
                if a in usados or b in usados:
                    sobra.append((a, b))
                    continue
                usados.update((a, b))
                rodada.append([a, b])
            rodadas.append(rodada)
            resto = sobra
            if melhor is not None and len(rodadas) >= len(melhor):
                break
        else:
            if melhor is None or len(rodadas) < len(melhor):
                melhor = rodadas
    # mando alternado: joga em casa quem tem menos jogos em casa ate ali
    em_casa: Dict[int, int] = {}
    for rodada in melhor or []:
        for jogo in rodada:
            if em_casa.get(jogo[0], 0) > em_casa.get(jogo[1], 0):
                jogo[0], jogo[1] = jogo[1], jogo[0]
            em_casa[jogo[0]] = em_casa.get(jogo[0], 0) + 1
    return melhor or []


def _sortear_grupos(G: Mundo, ids: List[int], n_grupos: int) -> List[List[int]]:
    """Potes por reputacao, um clube de cada pote em cada grupo."""
    ordem = sorted(ids, key=lambda i: -G["clubes"][i]["reputacao"])
    grupos: List[List[int]] = [[] for _ in range(n_grupos)]
    for k in range(0, len(ordem), n_grupos):
        pote = ordem[k:k + n_grupos]
        rng.shuffle(pote)
        alvos = sorted(range(n_grupos), key=lambda g: (len(grupos[g]), rng.random()))
        for cid, g in zip(pote, alvos):
            grupos[g].append(cid)
    return grupos


def montar_estaduais(G: Mundo) -> None:
    """Sorteia a tabela do ano. Chamado na virada da temporada."""
    G["estaduais"] = {}
    for chave, nome, ids in _grupos_estaduais(G):
        ids = sorted(ids, key=lambda i: -G["clubes"][i]["reputacao"])
        fmt = _formato_estadual(chave, len(ids))
        grupos = None
        if fmt["fase1"] == "cruzado":
            grupos = _sortear_grupos(G, ids, fmt["grupos"])
            grupo_de = {cid: g for g, grp in enumerate(grupos) for cid in grp}
            pares = [(a, b) for i, a in enumerate(ids) for b in ids[i + 1:]
                     if grupo_de[a] != grupo_de[b]]
            rodadas = _encaixar_rodadas(pares)
        elif fmt["fase1"] == "returno":
            turno = _turno_completo(ids)
            rodadas = turno + [[[b, a] for a, b in rd] for rd in turno]
        else:
            rodadas = _turno_completo(ids)
        G["estaduais"][chave] = {
            "chave": chave, "nome": nome, "times": ids, "rodadas": rodadas,
            "tabela": nova_tabela(ids), "rodada": 0, "campeao": None, "ultimos": [],
            "formato": fmt, "nome1": fmt["nome1"], "grupos": grupos,
            "mata": [{"nome": n, "ida_volta": iv, "jogos": []} for n, iv in fmt["mata"]],
            "mata_fase": 0, "perna": 0, "premiado": False,
        }


def estaduais(G: Mundo) -> Dict[str, Dict[str, Any]]:
    return G.setdefault("estaduais", {})


def meu_estadual(G: Mundo) -> Optional[Dict[str, Any]]:
    """O torneio do meu clube neste ano, se ele estiver em algum."""
    for est in estaduais(G).values():
        if G.get("clube") in est["times"]:
            return est
    return None


def tem_mata(est: Dict[str, Any]) -> bool:
    """Save de antes do mata-mata guarda estadual so de pontos corridos."""
    return bool(est.get("mata"))


def semanas_estadual(est: Dict[str, Any]) -> int:
    """Quantas semanas o torneio ocupa: primeira fase mais cada perna do mata-mata."""
    return len(est["rodadas"]) + sum(2 if f["ida_volta"] else 1 for f in est.get("mata") or [])


def semana_da_fase(est: Dict[str, Any], k: int) -> int:
    """Semana do estadual (1..) em que a fase k do mata-mata comeca."""
    return len(est["rodadas"]) + 1 + sum(2 if f["ida_volta"] else 1 for f in est["mata"][:k])


def rodadas_estaduais(G: Mundo) -> int:
    """Quantas semanas o torneio mais longo tem."""
    return max([semanas_estadual(e) for e in estaduais(G).values()] or [0])


def estadual_terminado(est: Dict[str, Any]) -> bool:
    if tem_mata(est):
        return bool(est.get("campeao"))
    return est["rodada"] >= len(est["rodadas"])


def estadual_em_andamento(G: Mundo) -> bool:
    return any(not estadual_terminado(e) for e in estaduais(G).values())


def subtabela(est: Dict[str, Any], ids: List[int]) -> Dict[str, Any]:
    """Um grupo do estadual com cara de liga, para classificacao() e as telas."""
    return {"times": list(ids), "tabela": est["tabela"], "rodada": est["rodada"],
            "rodadas": est["rodadas"]}


def grupo_do_clube(est: Dict[str, Any], cid: int) -> Optional[int]:
    for g, ids in enumerate(est.get("grupos") or []):
        if cid in ids:
            return g
    return None


def vagas_por_grupo(est: Dict[str, Any]) -> int:
    """Quantos de cada grupo (ou da tabela unica) vao ao mata-mata."""
    if not tem_mata(est):
        return 1
    return 2 ** len(est["mata"]) // max(1, len(est.get("grupos") or [0]))


def etapa_estadual(est: Dict[str, Any]) -> str:
    """Em que pe o torneio esta, numa expressao curta."""
    if estadual_terminado(est):
        return "encerrado"
    if est["rodada"] < len(est["rodadas"]):
        return "%s, rodada %d de %d" % (est.get("nome1") or "Primeira fase",
                                         est["rodada"] + 1, len(est["rodadas"]))
    f = est["mata"][est["mata_fase"]]
    if not f["ida_volta"]:
        return "%s, jogo unico" % f["nome"]
    return "%s, %s" % (f["nome"], "volta" if est.get("perna") else "ida")


def _cruzar(G: Mundo, est: Dict[str, Any], blocos: List[List[int]]) -> List[Dict[str, Any]]:
    """Confrontos do mata-mata: em cada bloco (ja em ordem de campanha) o
    melhor pega o pior. Jogo unico e na casa de quem fez a melhor campanha;
    ida e volta, a volta e na casa dela."""
    ida_volta = est["mata"][est["mata_fase"]]["ida_volta"]
    jogos = []
    for bloco in blocos:
        for i in range(len(bloco) // 2):
            melhor, pior = bloco[i], bloco[-1 - i]
            a, b = (pior, melhor) if ida_volta else (melhor, pior)
            jogos.append({"a": a, "b": b, "ida": None, "volta": None,
                          "penaltis": None, "venc": None})
    return jogos


def _abrir_mata(G: Mundo, est: Dict[str, Any]) -> None:
    """Fim da primeira fase: os classificados e os primeiros confrontos."""
    campanha = classificacao(G, est)
    grupos = est.get("grupos")
    por = vagas_por_grupo(est)
    if grupos:
        blocos = [classificacao(G, subtabela(est, g))[:por] for g in grupos]
        if not est["formato"].get("no_grupo"):
            todos = [cid for b in blocos for cid in b]
            blocos = [sorted(todos, key=campanha.index)]
    else:
        blocos = [campanha[:por]]
    est["mata_fase"] = 0
    est["perna"] = 0
    est["mata"][0]["jogos"] = _cruzar(G, est, blocos)


def _decidir(G: Mundo, jogo: Dict[str, Any], r: Dict[str, Any], ga: int, gb: int) -> None:
    a, b = jogo["a"], jogo["b"]
    if ga > gb:
        venc = a
    elif gb > ga:
        venc = b
    else:
        venc = penaltis(G, a, b, "estadual")
        r["penaltis"] = venc
        jogo["penaltis"] = venc
    jogo["venc"] = venc
    r["venc"] = venc


def _jogar_perna_mata(G: Mundo, est: Dict[str, Any]) -> List[Dict[str, Any]]:
    fase = est["mata"][est["mata_fase"]]
    volta = bool(est.get("perna"))
    res = []
    est["ultimos"] = []
    for j in fase["jogos"]:
        if not volta:
            r = simular(G, j["a"], j["b"], "estadual")
            j["ida"] = [r["gc"], r["gf"]]
            est["ultimos"].append([j["a"], j["b"], r["gc"], r["gf"]])
            if not fase["ida_volta"]:
                _decidir(G, j, r, r["gc"], r["gf"])
        else:
            r = simular(G, j["b"], j["a"], "estadual")
            # guardado do ponto de vista de a, como nas copas
            j["volta"] = [r["gf"], r["gc"]]
            est["ultimos"].append([j["b"], j["a"], r["gc"], r["gf"]])
            ga, gb = j["ida"][0] + j["volta"][0], j["ida"][1] + j["volta"][1]
            r["agregado"] = [j["a"], ga, j["b"], gb]
            _decidir(G, j, r, ga, gb)
        res.append(r)
    if fase["ida_volta"] and not volta:
        est["perna"] = 1
        return res
    est["perna"] = 0
    vencedores = [j["venc"] for j in fase["jogos"]]
    est["mata_fase"] += 1
    if est["mata_fase"] >= len(est["mata"]):
        est["campeao"] = vencedores[0]
        return res
    # as fases seguintes cruzam por campanha na primeira fase, como no Paulistao
    campanha = classificacao(G, est)
    est["mata"][est["mata_fase"]]["jogos"] = _cruzar(
        G, est, [sorted(vencedores, key=campanha.index)])
    return res


def jogar_rodada_estadual(G: Mundo, chave: str) -> List[Dict[str, Any]]:
    """A semana do torneio: uma rodada da primeira fase ou uma perna do mata-mata."""
    est = estaduais(G)[chave]
    if estadual_terminado(est):
        return []
    if est["rodada"] >= len(est["rodadas"]):
        return _jogar_perna_mata(G, est)
    res = []
    est["ultimos"] = []
    for casa, fora in est["rodadas"][est["rodada"]]:
        r = simular(G, casa, fora, "estadual")
        registrar(est, casa, fora, r["gc"], r["gf"])
        est["ultimos"].append([casa, fora, r["gc"], r["gf"]])
        res.append(r)
    est.setdefault("resultados", []).append(list(est["ultimos"]))
    est["rodada"] += 1
    if est["rodada"] >= len(est["rodadas"]) and tem_mata(est):
        _abrir_mata(G, est)
    return res


def jogos_estaduais_da_semana(G: Mundo, cid: int) -> List[Tuple[str, int, int]]:
    """(comp, casa, fora) do clube na semana estadual que vem."""
    out = []
    for est in estaduais(G).values():
        if cid not in est["times"] or estadual_terminado(est):
            continue
        if est["rodada"] < len(est["rodadas"]):
            for casa, fora in est["rodadas"][est["rodada"]]:
                if cid in (casa, fora):
                    out.append(("estadual", casa, fora))
            continue
        for j in est["mata"][est["mata_fase"]]["jogos"]:
            if cid in (j["a"], j["b"]):
                out.append(("estadual", j["b"], j["a"]) if est.get("perna")
                           else ("estadual", j["a"], j["b"]))
    return out


def campanha_estadual(G: Mundo, est: Dict[str, Any], cid: int) -> str:
    """Onde o clube parou (ou esta) no torneio, numa frase curta."""
    if cid not in est["times"]:
        return "fora do torneio"
    if est.get("campeao") == cid:
        return "campeao"
    for k, f in enumerate(est.get("mata") or []):
        for j in f["jogos"]:
            if cid not in (j["a"], j["b"]):
                continue
            if j["venc"] is None:
                return "vivo: %s" % f["nome"].lower()
            if j["venc"] != cid:
                if k == len(est["mata"]) - 1:
                    return "vice-campeao"
                return "eliminado " + _na_fase(f["nome"].lower())
    g = grupo_do_clube(est, cid)
    liga = subtabela(est, est["grupos"][g]) if g is not None else est
    pos = classificacao(G, liga).index(cid) + 1
    onde = " do grupo %s" % "ABCDEFGH"[g] if g is not None else ""
    if est["rodada"] >= len(est["rodadas"]):
        if tem_mata(est):
            return "%do%s, fora do mata-mata" % (pos, onde)
        return "%do lugar" % pos
    return "%do%s" % (pos, onde)


def iniciar_estaduais(G: Mundo) -> List[str]:
    """Abre o ano: contratos vencidos caem e a pre-temporada vira estadual."""
    c = G["clubes"][G["clube"]]
    recados = []
    for pid in [p for p in c["elenco"] if G["jogadores"][p]["contrato"] <= 0
                and not G["jogadores"][p].get("dono")]:
        j = G["jogadores"][pid]
        c["elenco"].remove(pid)
        if pid in c.get("escalacao", []):
            c["escalacao"].remove(pid)
        j["clube"] = None
        j["listado"] = 0
        j["emp_listado"] = 0
        G["livres"].append(pid)
        recados.append("Contrato encerrado: %s deixou o clube." % j["nome"])
    if not estaduais(G):
        montar_estaduais(G)
    G["fase"] = "estadual"
    G["semana_est"] = 1
    c["escalacao"] = auto_escalar(G, c)
    meu = meu_estadual(G)
    if meu and tem_mata(meu):
        recados.append("%s comeca: %s com %d rodadas, depois %s. Sao %d semanas antes do "
                       "Brasileirao." % (meu["nome"], (meu.get("nome1") or "primeira fase").lower(),
                                         len(meu["rodadas"]),
                                         ", ".join(f["nome"].lower() for f in meu["mata"]),
                                         semanas_estadual(meu)))
    else:
        recados.append("%s comeca: %d rodadas antes do Brasileirao."
                       % (meu["nome"] if meu else "A pre-temporada",
                          len(meu["rodadas"]) if meu else 0))
    salvar_auto(G)
    return recados


def _na_fase(fase: str) -> str:
    """"na semifinal", "nas quartas de final", "na Taca Guanabara"."""
    plural = fase.lower().split()[0] in ("quartas", "oitavas", "semifinais")
    return ("nas %s" if plural else "na %s") % fase


def manchete_abertura_brasileirao(G: Mundo) -> Optional[str]:
    """Evento unico da virada estadual -> liga: como o MEU clube saiu do
    estadual, contado como pano de fundo da estreia no Brasileirao. So o meu
    clube, para nao encher o feed; clube sem estadual (de fora) nao gera nada."""
    est = meu_estadual(G)
    cid = G.get("clube")
    if not est or cid is None:
        return None
    c = G["clubes"][cid]
    liga = nome_da_liga(G, c["divisao"])
    campanha = campanha_estadual(G, est, cid)
    if campanha == "campeao":
        texto = "Depois do titulo do %s, %s estreia na %s com favoritismo." % (est["nome"], c["nome"], liga)
    elif campanha == "vice-campeao":
        texto = "Vice do %s, %s chega a %s querendo dar o troco." % (est["nome"], c["nome"], liga)
    elif campanha.startswith("eliminado "):
        texto = "Eliminado %s do %s, %s busca a volta por cima na %s." % (
            campanha[len("eliminado "):], est["nome"], c["nome"], liga)
    elif campanha.endswith("fora do mata-mata"):
        fase = est.get("nome1") or "Primeira fase"
        # "Taca Guanabara" e nome proprio; "Primeira fase" e "Fase de grupos" nao
        if fase.split()[0] in ("Primeira", "Fase"):
            fase = fase[0].lower() + fase[1:]
        texto = "Eliminado ainda %s do %s, %s tenta reacao na %s." % (
            _na_fase(fase), est["nome"], c["nome"], liga)
    else:
        # estadual so de pontos corridos (save antigo): conta a colocacao
        texto = "%s termina o %s em %s e vira a chave para a %s." % (
            c["nome"], est["nome"], campanha, liga)
    manchete(G, "abertura", texto)
    return texto


def encerrar_estaduais(G: Mundo) -> List[str]:
    """Coroa os campeoes, paga o premio e entrega o ano ao Brasileirao."""
    recados = []
    for est in estaduais(G).values():
        if est.get("premiado") or not est["times"]:
            continue
        if not est.get("campeao"):
            # save antigo, so de pontos corridos: o lider e o campeao
            est["campeao"] = classificacao(G, est)[0]
        campeao = est["campeao"]
        est["premiado"] = True
        cl = G["clubes"][campeao]
        dar_titulo(G, cl, est["nome"])
        premio = int(premio_estadual(est) + cl["reputacao"] * 22_000)
        lancar(G, cl, premio, "premio_estadual")
        if campeao == G.get("clube"):
            st = stats_ano(G)
            st["premios"] = int(st.get("premios", 0)) + premio
            recados.append("CAMPEAO: voce venceu o %s e levou %s."
                           % (est["nome"], din(premio)))
        elif G.get("clube") in est["times"]:
            recados.append("%s: %s campeao. Sua campanha: %s."
                           % (est["nome"], cl["nome"], campanha_estadual(G, est, G["clube"])))
    G["fase"] = "liga"
    G["semana"] = 1
    G["semana_est"] = 0
    manchete_abertura_brasileirao(G)
    for cl in G["clubes"].values():
        cl["esc_stamp"] = ""
    c = G["clubes"][G["clube"]]
    c["escalacao"] = auto_escalar(G, c)
    recados.append("%s comecando. Objetivo: %s."
                   % (("Brasileirao " if brasileiro(c) else "") + nome_da_liga(G, c["divisao"]),
                      G["objetivo"]))
    salvar_auto(G)
    return recados


def _semana_estadual(G: Mundo) -> List[Dict[str, Any]]:
    """Uma rodada de estadual em todos os torneios de uma vez."""
    meus = []
    for chave in list(estaduais(G)):
        for r in jogar_rodada_estadual(G, chave):
            if G["clube"] in (r["casa"], r["fora"]):
                meus.append(r)
    rodada = int(G.get("semana_est", 1))
    for chave, cp in list(G["copas"].items()):
        if copa_do_estadual_na_semana(cp, rodada):
            for r in jogar_fase_copa(G, chave):
                if G["clube"] in (r["casa"], r["fora"]):
                    meus.append(r)
    G["ultimos_meus"] = [dict(r) for r in meus]
    guardar_historico(G, meus)
    for r in meus:
        registrar_placar(G, r)
    economia_semanal(G)
    atualizar_confianca(G, meus)
    recuperacao(G)
    mercado_ia(G)
    carimbar_livres(G)
    contratar_livres_ia(G)
    rodar_peneira(G)
    G["semana_est"] = int(G.get("semana_est", 1)) + 1
    for recado in executar_agendadas(G):
        noticia(G, recado)
    if G["semana_est"] % SEMANAS_POR_MES == 0:
        pagar_parcela_credito(G)
        for pid, delta in progresso_mensal(G):
            j = G["jogadores"][pid]
            if delta > 0:
                noticia(G, "%s evoluiu para %d de overall." % (j["nome"], j["ovr"]))
    if not estadual_em_andamento(G):
        for recado in encerrar_estaduais(G):
            noticia(G, recado)
    return meus


# ----------------------------------------------------------------------------
# SEMANA
# ----------------------------------------------------------------------------

def jogos_da_semana(G, cid):
    """Lista de (comp, casa, fora) do clube na semana atual."""
    if G.get("fase") == "estadual":
        out = jogos_estaduais_da_semana(G, cid)
        rodada = int(G.get("semana_est", 1))
        for k, cp in G["copas"].items():
            if cid in cp["vivos"] and copa_do_estadual_na_semana(cp, rodada):
                out.append((k, None, None))
        return out
    out = []
    sem = G["semana"]
    c = G["clubes"][cid]
    if sem <= SEMANAS_LIGA and c["divisao"] in G["ligas"]:
        liga = G["ligas"][c["divisao"]]
        if liga["rodada"] < len(liga["rodadas"]):
            for casa, fora in liga["rodadas"][liga["rodada"]]:
                if cid in (casa, fora):
                    out.append(("liga", casa, fora))
    for k, cp in G["copas"].items():
        if cp["campeao"] or cid not in cp["vivos"]:
            continue
        if em_grupos(cp):
            jogo = jogo_de_grupo(cp, cid)
            if jogo and cp["semanas_grupos"][cp["rodada_grupo"]] == sem:
                out.append((k, jogo[0], jogo[1]))
            continue
        if cp["fase"] < len(cp["semanas"]) and cp["semanas"][cp["fase"]] == sem:
            out.append((k, None, None))
        elif cp.get("semanas_est") and cp["fase"] < len(cp["semanas_est"]):
            out.append((k, None, None))
    return out


def _receita_base(c):
    """A receita fixa que o clube tinha antes de o patrocinio existir: a regua
    de TV e patrocinio juntos, por serie e reputacao."""
    base, por_rep = TV.get(c["divisao"]) or perfil_liga(c["divisao"])["tv"]
    return int((base + por_rep * c["reputacao"]) * ESCALA_EXT.get(c["divisao"], 1.0))


# a regua antiga dividida: 60% vira cota de TV, 40% patrocinio (master 28%,
# uniforme 12%). A calibragem de quanto cada um vale e da entrega 4.
FATIA_TV = 0.60
# fatia da receita-base por espaco (decidido em 2026-09-26: ~2,5x o total de
# antes, quando so havia master 0,28 e uniforme 0,12)
FATIA_PATROCINIO = {"master": 0.40, "uniforme": 0.18, "costas": 0.14, "naming": 0.16,
                    "manga": 0.07, "calcao": 0.06, "treino": 0.04}
NAMING_CAPACIDADE = 20_000     # naming rights so para estadio deste tamanho


def tv_semanal(c):
    return int(_receita_base(c) * FATIA_TV)


def receita_semanal(G, c):
    """Receita fixa da semana: cota de TV mais os patrocinios."""
    return tv_semanal(c) + patrocinio_semanal(G, c)


# ----------------------------------------------------------------------------
# PATROCINIO
#
# Master e uniforme sao contratos do meu clube: empresa, valor por semana,
# temporadas restantes e um bonus por meta, pago na virada. Na pre-temporada,
# espaco vazio recebe tres propostas (fixo alto e curto, equilibrado, aposta
# com bonus grande e longo); sem escolha, a equilibrada assina quando a bola
# rola. A maquina recebe o valor base, sem contrato guardado. Tudo sem
# sorteio: empresa e variacao saem de _ruido, estaveis por clube e ano.
# ----------------------------------------------------------------------------

ESPACOS_PATROCINIO = ("master", "uniforme", "costas", "naming", "manga", "calcao", "treino")
NOME_ESPACO = {"master": "Patrocinio master", "uniforme": "Fornecedor de uniforme",
               "costas": "Costas da camisa", "naming": "Naming rights do estadio",
               "manga": "Manga", "calcao": "Calcao", "treino": "Patrocinio de treino"}
# naming rights e contrato longo: as temporadas do perfil valem o dobro
ANOS_ESPACO = {"naming": 2}


def espacos_do_clube(c) -> Tuple[str, ...]:
    """Os espacos que este clube tem para vender: naming so com estadio grande."""
    return tuple(e for e in ESPACOS_PATROCINIO
                 if e != "naming" or c.get("capacidade", 0) >= NAMING_CAPACIDADE)
EMPRESAS = {
    "master": ["Banco Horizonte", "Viva Telecom", "Construtora Atlas", "Seguros Farol",
               "Rede Mercadao", "Aurora Energia", "Grupo Ventura", "Credito Popular",
               "Transportes Rota Sul", "Farmacias Bem Estar"],
    "uniforme": ["Kappo Sport", "Trama Esportes", "Vento Norte", "Arena Wear",
                 "Pulso Athletic", "Garra Sports", "Linha Fina", "Onda Esportiva"],
    "costas": ["Supermercados Boa Praca", "Viacao Estrela", "Clinica Vital", "Ceramica Solar",
               "Tintas Arco-Iris", "Motos Trilha"],
    "naming": ["Banco Horizonte", "Viva Telecom", "Aurora Energia", "Grupo Ventura",
               "Seguradora Porto Firme", "Petro Litoral"],
    "manga": ["Oticas Visao", "Auto Pecas Motor", "Cafe Serrano", "Moveis Lar Doce",
              "Escola Futuro", "Agua Cristal"],
    "calcao": ["Academia Forte", "Pizzaria Bella", "Imobiliaria Chave", "Pneus Rodovia",
               "Laticinios Campo Verde"],
    "treino": ["Suplementos Pro", "Isotonico Rapido", "Plano Saude Mais", "Tenis Pista",
               "App Delivery Ja"],
}
# (rotulo, fator do fixo, temporadas, meta do bonus, bonus em semanas de fixo)
PERFIS_PATROCINIO = (
    ("fixo alto", 1.06, 1, "objetivo", 4),
    ("equilibrado", 0.96, 2, "objetivo", 10),
    ("aposta", 0.82, 3, "titulo", 26),
)
TEXTO_META = {"objetivo": "cumprir o objetivo da temporada",
              "titulo": "ser campeao da liga",
              "acesso": "subir de divisao"}


def fator_campanha(G, c):
    """O ano que passou pesa no quanto as empresas oferecem: quem ganha tudo
    vale bem mais (1 titulo 1,35; 2 titulos 1,50; 3 ou mais 1,70)."""
    r = G.get("ultimo_resumo") or {}
    if c["id"] != G.get("clube") or not r:
        return 1.0
    n = len(r.get("titulos") or [])
    if n >= 3:
        return 1.70
    if n == 2:
        return 1.50
    if n == 1:
        return 1.35
    return 1.12 if r.get("objetivo_ok") else 0.92


def fator_marca(c):
    """Quanto a marca do clube vale para as empresas, pela reputacao: ~+50% na
    media, puxado para os grandes (rep 40 = 1,15; 70 = 1,53; 92 = 1,84).
    Decidido em 2026-09-28, so para o futebol brasileiro: fora, a receita ja
    era calibrada pela liga (e com isto o caixa europeu explodia)."""
    if not brasileiro(c):
        return 1.0
    return max(1.15, 0.55 + 0.0140 * c["reputacao"])


def patrocinio_base(G, c, espaco):
    """O valor semanal de referencia deste espaco para este clube hoje."""
    return int(_receita_base(c) * FATIA_PATROCINIO[espaco] * fator_marca(c) * fator_campanha(G, c))


def patrocinio_semanal(G, c):
    if c["id"] != G.get("clube"):
        return sum(int(_receita_base(c) * FATIA_PATROCINIO[e] * fator_marca(c)) for e in espacos_do_clube(c))
    contratos = c.get("patrocinios") or {}
    return sum(int(contratos[e]["semanal"]) for e in espacos_do_clube(c) if contratos.get(e))


def _meta_do_perfil(c, meta):
    # titulo da liga na Serie B pra baixo vira acesso: e o que o clube persegue
    if meta == "titulo" and c["divisao"] in "BCD":
        return "acesso"
    return meta


def ofertas_patrocinio(G, c, espaco):
    """As tres propostas deste espaco neste ano (estaveis: reabrir mostra as mesmas)."""
    base = patrocinio_base(G, c, espaco)
    nomes = EMPRESAS[espaco]
    fora = []
    for i, (rotulo, fator, anos, meta, semanas_bonus) in enumerate(PERFIS_PATROCINIO):
        chave = "patro-%d-%s-%d-%d" % (c["id"], espaco, int(G["temporada"]), i)
        semanal = int(base * fator * _ruido(chave, 0.94, 1.07) / 100) * 100
        empresa = nomes[int(_ruido(chave + "-nome", 0, len(nomes) - 0.001))]
        meta = _meta_do_perfil(c, meta)
        fora.append({"perfil": rotulo, "empresa": empresa, "semanal": semanal,
                     "temporadas": anos * ANOS_ESPACO.get(espaco, 1),
                     "meta": meta, "bonus": int(semanal * semanas_bonus / 1000) * 1000})
    return fora


def assinar_patrocinio(G, c, espaco, oferta, automatico=False):
    c.setdefault("patrocinios", {})[espaco] = dict(oferta)
    noticia(G, "%s: %s assina por %s, %s por semana%s." % (
        NOME_ESPACO[espaco], oferta["empresa"], plural(oferta["temporadas"], "temporada"),
        din(oferta["semanal"]), " (assinado sem escolha sua)" if automatico else ""))


def espacos_vagos(G, c):
    contratos = c.get("patrocinios") or {}
    return [e for e in espacos_do_clube(c) if not contratos.get(e)]


def assinar_vagos_automatico(G):
    """A bola vai rolar e o espaco segue vazio: fecha a proposta equilibrada."""
    c = G["clubes"].get(G.get("clube"))
    if not c:
        return
    for espaco in espacos_vagos(G, c):
        assinar_patrocinio(G, c, espaco, ofertas_patrocinio(G, c, espaco)[1], automatico=True)


def herdar_patrocinios(G, c):
    """Clube novo (ou save de antes do patrocinio): os contratos que ja estavam
    la, pelo valor base, ate o fim desta temporada."""
    c["patrocinios"] = {}
    for espaco in espacos_do_clube(c):
        c["patrocinios"][espaco] = {
            "perfil": "herdado", "empresa": EMPRESAS[espaco][c["id"] % len(EMPRESAS[espaco])],
            "semanal": patrocinio_base(G, c, espaco), "temporadas": 1, "meta": "objetivo", "bonus": 0}


def meta_cumprida(G, c, meta, resumo):
    if meta == "objetivo":
        return bool(resumo.get("objetivo_ok"))
    if meta == "titulo":
        return int(resumo.get("posicao") or 99) == 1
    if meta == "acesso":
        mov = resumo.get("movimento")
        return bool(mov and mov[0] == "acesso")
    return False


def fechar_ano_patrocinio(G, c, resumo):
    """Virada: paga o bonus de quem bateu a meta e desconta um ano de contrato."""
    pagos = []
    contratos = c.get("patrocinios") or {}
    for espaco in espacos_do_clube(c):
        k = contratos.get(espaco)
        if not k:
            continue
        if k.get("bonus") and meta_cumprida(G, c, k["meta"], resumo):
            lancar(G, c, int(k["bonus"]), "patrocinio_bonus")
            pagos.append([k["empresa"], int(k["bonus"]), TEXTO_META[k["meta"]]])
        k["temporadas"] = int(k["temporadas"]) - 1
        if k["temporadas"] <= 0:
            contratos[espaco] = None
    resumo["patrocinio_bonus"] = pagos
    return pagos


def folha_semanal(G, c):
    """Quem esta emprestado aqui custa so a fatia combinada; quem eu cedi, o resto."""
    total = 0.0
    for p in c["elenco"]:
        j = G["jogadores"][p]
        total += j["salario"] * (j["emp_pct"] / 100.0 if j["dono"] else 1.0)
    for p in c.get("emprestados", []):
        j = G["jogadores"].get(p)
        if j and j["dono"] == c["id"]:
            total += j["salario"] * (1.0 - j["emp_pct"] / 100.0)
    # a bolsa da base e folha como qualquer outra, e tem que aparecer como tal
    return int(total / 4.0) + custo_base(G, c)


# Custos calibrados em 2026-09-25 (economia, entrega 4) com a temporada
# inteira de todos os clubes brasileiros medida por divisao.
# - cada nivel de CT, base e medico custa uma fracao da receita fixa: antes era
#   quase fixo por nivel e comia 16% da receita de um grande e 45% da de um
#   clube da Serie D (custo regressivo que esmagava o pequeno);
# - operacional (comissao, viagens, impostos) sobe de 45% para 60%;
# - cada jogo em casa custa 45% da renda (seguranca, staff, arbitragem).
CUSTO_NIVEL = 0.011
CUSTO_OPERACIONAL = 0.40       # era 0,60: comia quase a cota de TV inteira (2026-09-28)
CUSTO_OPERACIONAL_EXT = 0.60   # fora do Brasil segue o de antes (a margem de la ja fechava)
CUSTO_JOGO_CASA = 0.45


def custo_estrutura(c):
    """Estrutura, comissao, viagens, impostos e manutencao."""
    base = _receita_base(c)
    fixo = (c["ct"] + c["base"] + c["medico"]) * base * CUSTO_NIVEL
    fixo += c["capacidade"] * manutencao_por_lugar(c)
    operacional = base * (CUSTO_OPERACIONAL if brasileiro(c) else CUSTO_OPERACIONAL_EXT)
    return int(fixo + operacional) + custo_treino(c)


# ----------------------------------------------------------------------------
# VERBA
#
# O caixa nao e todo dinheiro de contratar. Uma parte ja tem dono: a folha e a
# estrutura dos proximos meses, que saem toda semana haja receita ou nao. A
# verba de contratacao e o caixa MENOS essa reserva - e o salario de quem
# chega entra na reserva antes de o passe ser pago. Assim nenhuma compra deixa
# o clube sem dinheiro para a folha. Vale para voce e para a IA.
# ----------------------------------------------------------------------------

RESERVA_MESES = 3


def bilheteria_mensal_estimada(c: Clube) -> int:
    """Mesma estimativa que sob_pressao usa: dois jogos em casa por mes, em media."""
    return int(publico_esperado(c) * c["preco"] * 2)       # dois jogos em casa por mes


def orcamento_mensal(G: Mundo, c: Clube) -> Dict[str, int]:
    """O mes do clube: o que entra, o que sai e o saldo."""
    tv = receita_semanal(G, c) * 4
    bilheteria = bilheteria_mensal_estimada(c)
    folha = folha_semanal(G, c) * 4
    estrutura = custo_estrutura(c) * 4
    socios = socios_mensal(c) // 4 * 4
    return {"tv": int(tv), "bilheteria": bilheteria, "socios": socios, "folha": int(folha),
            "estrutura": int(estrutura), "custos": int(folha + estrutura),
            "saldo": int(tv + bilheteria + socios - folha - estrutura)}


def reserva_custos(G: Mundo, c: Clube, salario_novo: int = 0) -> int:
    """O que fica guardado: RESERVA_MESES meses de folha e estrutura, sem
    descontar receita nenhuma (TV atrasa, bilheteria oscila; custo nao).
    salario_novo e o salario MENSAL de quem esta para chegar."""
    custo_mes = (folha_semanal(G, c) + custo_estrutura(c)) * 4 + max(0, int(salario_novo))
    return int(custo_mes * RESERVA_MESES)


TETO_FOLHA_RECEITA = 0.85   # folha que um clube da IA aceita, em fracao da receita do mes
TETO_UM_SALARIO = 0.25      # e um contrato sozinho, no maximo (craque nao cai na Serie D)


def cabe_na_folha(G: Mundo, c: Clube, salario_mes: int) -> bool:
    """Este salario cabe na folha do clube? A mesma conta de sob_pressao: sem
    ela, craque europeu livre caia na Serie D pelo mercado do overall (R$ 2 a 3
    mi por mes com receita de R$ 700 mil) e a divisao inteira quebrava."""
    receita_mes = receita_semanal(G, c) * 4 + bilheteria_mensal_estimada(c)
    if int(salario_mes) > receita_mes * TETO_UM_SALARIO:
        return False
    return folha_semanal(G, c) * 4 + max(0, int(salario_mes)) <= receita_mes * TETO_FOLHA_RECEITA


def verba_contratacao(G: Mundo, c: Clube, salario_novo: int = 0) -> int:
    """Quanto pode ir para passe ou taxa sem ameacar a folha."""
    return max(0, int(c["dinheiro"] - reserva_custos(G, c, salario_novo)))


def sob_pressao(G, c):
    """Folha comprometendo a receita e o gatilho preventivo de corte.

    Sem isto a folha cresce junto com o OVR do mundo (salario e exponencial) e
    a liga inteira quebra depois de uma decada. O clube reage antes de furar o
    caixa, como um clube de verdade faria.
    """
    receita_mes = receita_semanal(G, c) * 4 + bilheteria_mensal_estimada(c)
    return folha_semanal(G, c) * 4 > receita_mes * 0.82


def saneamento_ia(G):
    """Clubes da IA no vermelho, ou com folha alta demais, cortam custo."""
    for c in G["clubes"].values():
        if c["divisao"] == "EX" or c["id"] == G["clube"]:
            continue
        aperto = sob_pressao(G, c)
        if c["dinheiro"] > -500_000 and not aperto:
            continue
        if aperto and c["dinheiro"] > 0:
            # ainda da para respirar: poe o salario mais alto na vitrine
            proprios_ok = [p for p in c["elenco"] if not G["jogadores"][p].get("dono")]
            if proprios_ok and rng.random() < 0.5:
                caro = max(proprios_ok, key=lambda p: G["jogadores"][p]["salario"])
                if not G["jogadores"][caro]["listado"]:
                    G["jogadores"][caro]["listado"] = preco_pedido(G, G["jogadores"][caro])
            continue
        # vende o melhor ativo para quem tem caixa
        proprios = [p for p in c["elenco"] if not G["jogadores"][p].get("dono")]
        if rng.random() < 0.45 and len(proprios) > 16:
            pid = max(proprios, key=lambda p: G["jogadores"][p]["valor"])
            preco = int(G["jogadores"][pid]["valor"] * 0.70)
            ricos = [cl for cl in G["clubes"].values()
                     if cl["divisao"] != "EX" and cl["id"] not in (c["id"], G["clube"])
                     and cl["dinheiro"] > preco * 2 and len(cl["elenco"]) < 28
                     and verba_contratacao(G, cl, G["jogadores"][pid]["salario"]) >= preco]
            if ricos and preco > 0:
                transferir(G, pid, rng.choice(ricos)["id"], preco)
                continue
        if len(proprios) <= 18 or rng.random() > 0.5:
            continue
        pid = max(proprios, key=lambda p: G["jogadores"][p]["salario"])
        j = G["jogadores"][pid]
        c["elenco"].remove(pid)
        if pid in c.get("escalacao", []):
            c["escalacao"].remove(pid)
        j["clube"] = None
        j["listado"] = 0
        j["salario"] = int(j["salario"] * 0.85)
        G["livres"].append(pid)


# Socios: o numero vem do sorteio do clube (15% a 55% da capacidade) e agora
# paga mensalidade, por divisao (decidido em 2026-09-29). Soma perto de 6% da
# receita do mes em todas as series. So no Brasil: a economia de fora ja fecha.
MENSALIDADE_SOCIO = {"A": 50, "B": 30, "C": 20, "D": 12}


def socios_mensal(c) -> int:
    """O que os socios pagam por mes ao clube."""
    if not brasileiro(c):
        return 0
    return int(c.get("socios", 0)) * MENSALIDADE_SOCIO.get(c["divisao"], 0)


def economia_semanal(G):
    for c in G["clubes"].values():
        if c["divisao"] == "EX":
            continue
        rec, folha, est = receita_semanal(G, c), folha_semanal(G, c), custo_estrutura(c)
        socios = socios_mensal(c) // 4
        if c["id"] == G.get("clube"):
            st = stats_ano(G)
            st["receita"] = int(st.get("receita", 0)) + int(rec + socios)
            st["gasto"] = int(st.get("gasto", 0)) + int(folha + est)
        treino = custo_treino(c)
        tv = tv_semanal(c)
        lancar(G, c, tv, "tv")
        if rec - tv:
            lancar(G, c, rec - tv, "patrocinio")
        if socios:
            lancar(G, c, socios, "socios")
        lancar(G, c, -folha, "folha")
        lancar(G, c, -(est - treino), "estrutura")
        if treino:
            lancar(G, c, -treino, "treino")
        if c["obra_semanas"] > 0:
            c["obra_semanas"] -= 1
            if c["obra_semanas"] == 0:
                c["capacidade"] += c["obra_lugares"]
                if c["id"] == G["clube"]:
                    noticia(G, "Obra concluida: %s passa a ter %s lugares." %
                            (c["estadio"], f"{c['capacidade']:,}".replace(",", ".")))
                c["obra_lugares"] = 0


def recuperacao(G):
    for j in G["jogadores"].values():
        c = G["clubes"].get(j["clube"]) if j["clube"] else None
        ct = c["ct"] if c else 3
        med = c["medico"] if c else 3
        j["cond"] = int(round(clamp(j["cond"] + 10 + ct + regime_de(c)["cond"], 5, 100)))
        if j["lesao"] > 0:
            j["lesao"] -= 1 if rng.random() > med * 0.05 else 2
            j["lesao"] = max(0, j["lesao"])
        j["forma"] = clamp(j["forma"] + rng.randint(-2, 2), 5, 100)


# o terminal e a janela gravam ao fim de cada semana; a web grava uma vez so,
# na rota de avancar, e desliga isto (api/sessao.py)
SALVAR_NA_SEMANA = True


def salvar_auto(G, forcar=False):
    if not SALVAR_NA_SEMANA and not forcar:
        return False
    try:
        salvar(G)
        return True
    except Exception:
        return False


def noticia(G, txt):
    G["noticias"].append("S%02d: %s" % (G["semana"], txt))
    G["noticias"] = G["noticias"][-40:]


# ----------------------------------------------------------------------------
# PELO MUNDO
#
# As noticias acima sao do meu clube. O feed e o resto do futebol: goleada,
# zebra, troca de lideranca, grande eliminado, titulo, contratacao cara e
# craque machucado, de qualquer clube. So registra o que o motor ja decidiu -
# nenhuma manchete inventa fato.
# ----------------------------------------------------------------------------

LIMITE_FEED = 300
RESULTADOS_POR_SEMANA = 4    # o resto da rodada fica so na tabela
PESO_CLASSICO = 1000         # acima de qualquer goleada ou zebra no corte da semana
GOLEADA = 4                  # diferenca de gols que vira manchete
ZEBRA_REP = 20               # vencedor com tanto menos de reputacao que o perdedor
GRANDE_REP = 72              # clube cuja eliminacao e noticia
NEGOCIO_MANCHETE = 8_000_000
CRAQUE_OVR = 78
LESAO_MANCHETE = 4           # semanas
NOME_COMP = {"liga": None, "copa": "Copa do Brasil", "lib": "Libertadores",
             "sul": "Sul-Americana", "estadual": None}


def manchete(G: Mundo, tipo: str, texto: str) -> None:
    feed = G.setdefault("feed", [])
    feed.append({"t": int(G.get("temporada", 0)), "s": int(G.get("semana", 0)),
                 "tipo": tipo, "texto": texto})
    del feed[:-LIMITE_FEED]


def _onde(G: Mundo, r: Dict[str, Any]) -> str:
    comp = NOME_COMP.get(r.get("comp"))
    if comp:
        return comp
    cp = G.get("copas", {}).get(r.get("comp"))
    if cp:
        return cp["nome"]           # copas nacionais de fora, supercopas, Mundial
    div = G["clubes"][r["casa"]]["divisao"]
    return nome_da_liga(G, div)


def manchetes_da_semana(G: Mundo, jogos: List[Dict[str, Any]],
                        lideres_antes: Dict[str, Optional[int]]) -> None:
    candidatas = []   # (peso, texto): so as maiores da semana viram manchete
    for r in jogos:
        casa, fora = G["clubes"][r["casa"]], G["clubes"][r["fora"]]
        # Serie D e continental entre estrangeiros enchem o feed sem interessar
        if r.get("comp") == "liga" and casa["divisao"] not in "AB":
            continue
        if casa["divisao"] == "EX" and fora["divisao"] == "EX":
            continue
        placar = "%s %d x %d %s" % (casa["nome"], r["gc"], r["gf"], fora["nome"])
        saldo = abs(r["gc"] - r["gf"])
        peso, marca = 0, None
        if saldo >= GOLEADA:
            peso, marca = saldo * 10, "Goleada"
        elif saldo:
            venc, perd = (casa, fora) if r["gc"] > r["gf"] else (fora, casa)
            dif = perd["reputacao"] - venc["reputacao"]
            if dif >= ZEBRA_REP:
                peso, marca = dif, "Zebra"
        if eh_classico(G, r["casa"], r["fora"]):
            # classico entra quase sempre no corte, mesmo sem goleada; a
            # goleada ou zebra, se houver, vai junto no fim do texto
            texto = "%s: %s (%s)." % (nome_classico(G, r["casa"], r["fora"]), placar, _onde(G, r))
            if marca:
                texto += " %s." % marca
            candidatas.append((PESO_CLASSICO + peso, texto))
        elif marca:
            candidatas.append((peso, "%s: %s (%s)." % (marca, placar, _onde(G, r))))
    candidatas.sort(key=lambda x: -x[0])
    for _peso, texto in candidatas[:RESULTADOS_POR_SEMANA]:
        manchete(G, "resultado", texto)
    for div, liga, nome, minimo in _ligas_de_manchete(G):
        if liga["rodada"] < minimo:
            continue
        lider = classificacao(G, liga)[0]
        if lideres_antes.get(div) is not None and lider != lideres_antes[div]:
            t = liga["tabela"].get(str(lider)) or {}
            manchete(G, "tabela", "%s assume a lideranca da %s, com %d pontos." %
                     (G["clubes"][lider]["nome"], nome, t.get("p", 0)))


def _ligas_de_manchete(G):
    fora = [(d, G["ligas"][d], "Serie %s" % d, 3) for d in "AB"]
    fora += [(k, l, l["nome"], 10) for k, l in ligas_ext(G).items()]
    return fora


def lideres(G: Mundo) -> Dict[str, Optional[int]]:
    fora = {}
    for div, liga, _nome, _minimo in _ligas_de_manchete(G):
        fora[div] = classificacao(G, liga)[0] if liga["rodada"] >= 2 else None
    return fora


def jogar_rodada_liga(G, div):
    liga = G["ligas"][div]
    if liga["rodada"] >= len(liga["rodadas"]):
        return []
    res = []
    liga["ultimos"] = []
    for casa, fora in liga["rodadas"][liga["rodada"]]:
        r = simular(G, casa, fora, "liga")
        registrar(liga, casa, fora, r["gc"], r["gf"])
        liga["ultimos"].append([casa, fora, r["gc"], r["gf"]])
        res.append(r)
    # rodada a rodada, para a tela navegar pelos resultados de qualquer rodada
    liga.setdefault("resultados", []).append(list(liga["ultimos"]))
    liga["rodada"] += 1
    return res


def jogar_fase_copa(G, chave):
    cp = G["copas"][chave]
    vivos = cp["vivos"][:]
    if len(vivos) < 2:
        return []
    pares = [tuple(par) for par in sorteio_da_copa(G, chave)]
    # a Recopa decide em ida e volta: a "final" dela nao e jogo unico
    # com clube esperando (o campeao europeu na Intercontinental) ainda nao e a final
    final = len(vivos) == 2 and not cp.get("final_ida_volta") and not cp.get("espera")
    res, prox = [], []
    # o que a fase deixou: vai para o historico, que a tela de competicoes le
    registro = {"fase": fase_da_copa(cp), "semana": int(G["semana"]),
                "temporada": int(G["temporada"]), "jogos": []}
    unico = final or cp.get("jogo_unico")
    fundo = cp.get("fundo")
    for a, b in pares:
        if unico:
            r = simular(G, a, b, chave, neutro=final or bool(cp.get("neutro")))
            if r["gc"] > r["gf"]:
                venc = a
            elif r["gf"] > r["gc"]:
                venc = b
            else:
                venc = penaltis(G, a, b, chave)
                r["penaltis"] = venc
            r["venc"] = venc
            res.append(r)
            registro["jogos"].append({"a": a, "b": b, "ida": [r["gc"], r["gf"]], "volta": None,
                                      "penaltis": r.get("penaltis"), "venc": venc})
        else:
            r1 = simular(G, a, b, chave)
            r2 = simular(G, b, a, chave)
            ga = r1["gc"] + r2["gf"]
            gb = r1["gf"] + r2["gc"]
            if ga > gb:
                venc = a
            elif gb > ga:
                venc = b
            else:
                venc = penaltis(G, a, b, chave)
                r2["penaltis"] = venc
            r2["agregado"] = [a, ga, b, gb]
            r1["venc"] = r2["venc"] = venc
            r1["perna"] = "ida"
            res.extend([r1, r2])
            # a volta e r2 com os lados trocados: guardado do ponto de vista de a
            registro["jogos"].append({"a": a, "b": b, "ida": [r1["gc"], r1["gf"]],
                                      "volta": [r2["gf"], r2["gc"]],
                                      "penaltis": r2.get("penaltis"), "venc": venc})
        prox.append(venc)
        perd = G["clubes"][b if venc == a else a]
        # premio por fase: quem passa ganha uma fatia; na final, o vice leva 40%
        if final:
            if perd["divisao"] != "EX":
                lancar(G, perd, int(PREMIO_COPA.get(chave, 0) * FRACAO_VICE), "premio_copa")
        elif G["clubes"][venc]["divisao"] != "EX":
            lancar(G, G["clubes"][venc], premio_fase_copa(chave, len(vivos)), "premio_copa")
        if perd["reputacao"] >= GRANDE_REP and perd["divisao"] != "EX" and not final and not fundo:
            manchete(G, "copa", "%s elimina %s na %s (%s)." % (
                G["clubes"][venc]["nome"], perd["nome"], cp["nome"], registro["fase"].lower()))
    cp.setdefault("historico", []).append(registro)
    cp["vivos"] = prox
    cp["fase"] += 1
    if cp.get("espera"):
        # playoff jogado: os primeiros de grupo entram nas oitavas como cabecas
        cp["sorteio"] = cruzar(G, cp["espera"], prox)
        cp["vivos"] = prox + cp["espera"]
        cp["espera"] = []
    else:
        cp["sorteio"] = sortear_confrontos(G, prox) if len(prox) >= 2 else []
    if len(cp["vivos"]) == 1:
        cp["campeao"] = cp["vivos"][0]
        c = G["clubes"][cp["campeao"]]
        dar_titulo(G, c, cp["nome"])
        premio = PREMIO_COPA.get(chave, 0)
        if c["divisao"] != "EX":
            lancar(G, c, premio, "premio_copa")
            c["reputacao"] = clamp(c["reputacao"] + 2, 10, 99)
        if not fundo:
            noticia(G, "%s: %s e campeao." % (cp["nome"], c["nome"]))
    return res


def semana_absoluta(G: Mundo) -> int:
    """Semanas jogadas desde o comeco do save, estadual incluido.

    G["semana"] fica em 0 durante todo o estadual e volta a 1 no Brasileirao:
    prazo contado nela durava o estadual inteiro de graca (a proposta de 6
    semanas feita na virada valia ~20). Prazo se conta aqui."""
    return int(G.get("semana_abs", 0))


def avancar_semana(G):
    G["log_semana"] = []
    assinar_vagos_automatico(G)
    G["semana_abs"] = semana_absoluta(G) + 1
    if G.get("fase") == "estadual":
        return _semana_estadual(G)
    sem = G["semana"]
    meus, todos = [], []
    antes = lideres(G)
    if sem <= SEMANAS_LIGA:
        for div in list(G["ligas"]):
            for r in jogar_rodada_liga(G, div):
                todos.append(r)
                if G["clube"] in (r["casa"], r["fora"]):
                    meus.append(r)
    for chave, cp in G["copas"].items():
        if cp["campeao"]:
            continue
        if em_grupos(cp):
            jogar = jogar_rodada_grupos if cp["semanas_grupos"][cp["rodada_grupo"]] == sem else None
        elif cp["fase"] < len(cp["semanas"]) and cp["semanas"][cp["fase"]] == sem:
            jogar = jogar_fase_copa
        elif cp.get("semanas_est") and cp["fase"] < len(cp["semanas_est"]):
            jogar = jogar_fase_copa         # o estadual acabou antes dela: joga agora
        else:
            jogar = None
        if jogar and cp.get("intercontinental"):
            entrar_campeao_europeu(G, cp)
        if jogar:
            for r in jogar(G, chave):
                todos.append(r)
                if G["clube"] in (r["casa"], r["fora"]):
                    meus.append(r)
    fechar_grupos(G)
    preparar_intercontinental(G)
    ia_demite_tecnicos(G)
    manchetes_da_semana(G, todos, antes)
    G["ultimos_meus"] = [dict(r) for r in meus]
    guardar_historico(G, meus)
    for r in meus:
        registrar_placar(G, r)
    economia_semanal(G)
    atualizar_confianca(G, meus)
    recuperacao(G)
    mercado_ia(G)
    carimbar_livres(G)
    contratar_livres_ia(G)
    rodar_peneira(G)
    saneamento_ia(G)
    if G["semana"] % SEMANAS_POR_MES == 0:
        pagar_parcela_credito(G)
        sondar_treinador(G)
        for pid, delta in progresso_mensal(G):
            j = G["jogadores"][pid]
            if delta > 0:
                noticia(G, "%s evoluiu para %d de overall." % (j["nome"], j["ovr"]))
            elif j["idade"] >= 32:
                noticia(G, "%s caiu para %d de overall." % (j["nome"], j["ovr"]))
    if modo_caos(G):
        eventos_caos(G)
    G["semana"] += 1
    # so agora a semana e a nova: se ela for de janela, o que estava acertado
    # entra hoje, e nao daqui a mais uma semana
    for recado in executar_agendadas(G):
        noticia(G, recado)
    return meus


# ----------------------------------------------------------------------------
# MERCADO
# ----------------------------------------------------------------------------

def mercado_aberto(G):
    """Janela: as semanas de JANELAS, mais a pre-temporada inteira (o estadual
    faz parte dela). Negociar pode sempre; entrar e sair, so aqui."""
    return G["semana"] in JANELAS or G["fase"] in ("entretemporada", "estadual")


def conta_posicao(G, c, pos):
    return sum(1 for p in c["elenco"] if G["jogadores"][p]["pos"] == pos)


# preco_pedido vive agora no bloco NEGOCIACAO


def transferir(G, pid, destino_id, valor):
    j = G["jogadores"][pid]
    if j.get("dono"):
        devolver_emprestimo(G, pid)
    origem = G["clubes"].get(j["clube"]) if j["clube"] else None
    destino = G["clubes"][destino_id]
    registrar_negocio(G, j, origem["id"] if origem else None, destino_id, valor)
    if origem is None:
        # agente livre: sem passe pago, nao pode virar lucro na semana seguinte
        j["livre_trava_ate"] = semana_absoluta(G) + LIVRE_SEM_REVENDA
    else:
        j.pop("livre_trava_ate", None)
    if da_base(j):
        # ninguem sai da academia direto para outro clube: se foi negociado,
        # e porque virou profissional
        if origem:
            origem["base_elenco"] = [p for p in origem.get("base_elenco", []) if p != pid]
        j["categoria"] = "pro"
    # contrato novo: salario de mercado do overall de hoje. A mesa do usuario
    # (fechar_compra) grava o negociado logo depois
    j["salario"] = salario_de(j["ovr"])
    if origem:
        if pid in origem["elenco"]:
            origem["elenco"].remove(pid)
        if pid in origem.get("escalacao", []):
            origem["escalacao"].remove(pid)
        lancar(G, origem, valor, "vendas")
    elif pid in G["livres"]:
        G["livres"].remove(pid)
    lancar(G, destino, -valor, "compras")
    destino["elenco"].append(pid)
    j["clube"] = destino_id
    j["obs"] = 0
    j["pago"] = int(valor)
    j["desde"] = G["temporada"] * 100 + G["semana"]
    j["listado"] = 0
    j["emp_listado"] = 0
    j["dono"] = None
    j["emp_pct"] = 100
    j["emp_opcao"] = 0
    j.pop("livre_desde", None)
    j["entros"] = ENTROS_CHEGADA
    mexer_moral(G, j, 8, "chegou ao clube")


def emprestar(G, pid, destino_id, pct):
    """Cede o jogador ate o fim da temporada. pct = fatia do salario paga pelo destino."""
    j = G["jogadores"][pid]
    origem = G["clubes"][j["clube"]]
    destino = G["clubes"][destino_id]
    origem["elenco"].remove(pid)
    if pid in origem.get("escalacao", []):
        origem["escalacao"].remove(pid)
    origem.setdefault("emprestados", []).append(pid)
    destino["elenco"].append(pid)
    j["clube"] = destino_id
    j["dono"] = origem["id"]
    j["emp_pct"] = int(clamp(pct, 0, 100))
    j["listado"] = 0
    j["emp_listado"] = 0
    j["entros"] = ENTROS_CHEGADA
    mexer_moral(G, j, 6, "chegou por emprestimo")


def devolver_emprestimo(G, pid):
    j = G["jogadores"].get(pid)
    if not j or not j.get("dono"):
        return
    atual = G["clubes"].get(j["clube"])
    dono = G["clubes"].get(j["dono"])
    if atual and pid in atual["elenco"]:
        atual["elenco"].remove(pid)
    if atual and pid in atual.get("escalacao", []):
        atual["escalacao"].remove(pid)
    if dono:
        if pid in dono.get("emprestados", []):
            dono["emprestados"].remove(pid)
        dono["elenco"].append(pid)
        j["clube"] = dono["id"]
        j["entros"] = ENTROS_VOLTA
    j["dono"] = None
    j["emp_pct"] = 100
    j["emp_opcao"] = 0


def devolver_todos(G):
    for pid in [p for p, j in G["jogadores"].items() if j.get("dono")]:
        devolver_emprestimo(G, pid)


def emprestavel(G, j):
    """Jogador que faz sentido ser cedido: jovem ou reserva, sem ser peca central."""
    if j.get("dono") or j["clube"] is None:
        return False
    c = G["clubes"][j["clube"]]
    titulares = sorted(c["elenco"], key=lambda p: -G["jogadores"][p]["ovr"])[:13]
    return j["id"] not in titulares or j["idade"] <= 21


def mercado_ia(G):
    """Clubes controlados pelo computador movimentam o mercado."""
    if not mercado_aberto(G):
        return
    clubes = [c for c in G["clubes"].values()
              if c["divisao"] != "EX" and c["id"] != G["clube"]]
    rng.shuffle(clubes)
    presos = presos_em_acerto(G)
    for c in clubes[:14]:
        if rng.random() > 0.35:
            continue
        # vende excedente
        for pos, minimo in ELENCO_PADRAO.items():
            if conta_posicao(G, c, pos) > minimo + 1 and rng.random() < 0.5:
                cand = [p for p in c["elenco"]
                        if G["jogadores"][p]["pos"] == pos and not G["jogadores"][p].get("dono")]
                cand.sort(key=lambda p: rendimento(G["jogadores"][p]))
                if cand:
                    G["jogadores"][cand[0]]["listado"] = preco_pedido(G, G["jogadores"][cand[0]])
        if rng.random() < 0.45 and len(c["elenco"]) > 20:
            p = rng.choice(c["elenco"])
            if not G["jogadores"][p].get("dono"):
                G["jogadores"][p]["listado"] = preco_pedido(G, G["jogadores"][p])
        if rng.random() < 0.40 and len(c["elenco"]) > 22:
            cand = [p for p in c["elenco"] if emprestavel(G, G["jogadores"][p])]
            if cand:
                G["jogadores"][rng.choice(cand)]["emp_listado"] = 1
        # compra reforco
        caixa = min(c["dinheiro"] * 0.55, verba_contratacao(G, c))
        alvos = [j for j in G["jogadores"].values()
                 if j["listado"] and j["clube"] not in (None, c["id"], G["clube"])
                 and j["id"] not in presos and j["listado"] <= caixa and j["ovr"] > media_elenco(G, c) - 2
                 and j["listado"] <= verba_contratacao(G, c, j["salario"])
                 and cabe_na_folha(G, c, j["salario"])]
        if alvos and len(c["elenco"]) < 28 and rng.random() < 0.85:
            alvo = rng.choice(alvos)
            vendedor = G["clubes"][alvo["clube"]]
            if conta_posicao(G, vendedor, alvo["pos"]) > ELENCO_PADRAO[alvo["pos"]] - 1:
                transferir(G, alvo["id"], c["id"], alvo["listado"])
        # contrata livre
        soltos = [p for p in G["livres"] if p not in presos]
        if len(c["elenco"]) < 24 and soltos and rng.random() < 0.4:
            pid = rng.choice(soltos)
            j = G["jogadores"][pid]
            pedida = exigencia_salarial(G, j, c)
            if cabe_na_folha(G, c, pedida):
                j["salario"] = pedida
                transferir(G, pid, c["id"], 0)
                j["contrato"] = rng.randint(1, 3)


def media_elenco(G, c):
    if not c["elenco"]:
        return 40
    return sum(G["jogadores"][p]["ovr"] for p in c["elenco"]) / len(c["elenco"])


def lista_mercado(G, pos_filtro=None, max_valor=None, limite=40):
    out = []
    for j in G["jogadores"].values():
        if not j["listado"] or j["clube"] == G["clube"] or j.get("dono") or da_base(j):
            continue
        if j["clube"] is not None and G["clubes"][j["clube"]]["divisao"] == "EX":
            continue
        if pos_filtro and j["pos"] != pos_filtro:
            continue
        if max_valor and j["listado"] > max_valor:
            continue
        out.append(j)
    out.sort(key=lambda j: -j["ovr"])
    return out[:limite]


# ----------------------------------------------------------------------------
# NEGOCIACAO
#
# Camada de servico. As entidades (jogador, clube) continuam sendo dicts, porque
# sao o formato do save. Proposta e Resposta sao objetos de valor transitorios:
# nascem na negociacao, morrem nela, nunca vao para o JSON.
#
# Regra da casa: nenhuma decisao de negocio pode ficar na interface. CLI, janela
# e IA chamam avaliar_clube / avaliar_jogador / avaliar_emprestimo e obedecem.
# ----------------------------------------------------------------------------

TIPO_COMPRA = "compra"
TIPO_EMPRESTIMO = "emprestimo"

# Teto de inscritos no profissional. Vale para TODAS as portas de entrada:
# compra, agente livre, emprestimo e promocao da base. Antes so a promocao
# respeitava, entao dava para ter 32 jogadores, contratar mais um sem reclamacao
# e ainda assim nao poder subir um garoto da propria academia.
# 40 e folga, nao permissividade: os elencos reais embutidos chegam a 38, e
# com o teto em 32 oito clubes grandes JA nasciam travados - sem poder comprar,
# pegar emprestado nem subir um garoto da propria base ate venderem alguem.
LIMITE_ELENCO = 40


def elenco_cheio(G: "Mundo", c: "Clube") -> bool:
    return len(c["elenco"]) >= LIMITE_ELENCO


def vagas_elenco(G: "Mundo", c: "Clube") -> int:
    return max(0, LIMITE_ELENCO - len(c["elenco"]))


def recado_elenco_cheio(c: "Clube") -> str:
    return ("Elenco cheio: %d de %d inscritos. Venda, empreste ou rescinda alguem "
            "para abrir vaga." % (len(c["elenco"]), LIMITE_ELENCO))


@dataclasses.dataclass(frozen=True)
class Proposta:
    jogador: int
    comprador: int
    valor: int = 0            # passe oferecido
    salario: int = 0          # salario mensal oferecido ao jogador
    anos: int = 3
    pct_salario: int = 100    # emprestimo: fatia que o clube de destino banca
    opcao_compra: int = 0     # emprestimo: preco fixado para compra futura
    tipo: str = TIPO_COMPRA


@dataclasses.dataclass(frozen=True)
class Resposta:
    aceita: bool
    motivo: str
    pedido: int = 0           # quanto eles querem: passe, salario ou percentual
    encerrada: bool = False   # True = mesa fechada, nao adianta insistir


def _ruido(chave: str, lo: float, hi: float) -> float:
    """Variacao estavel: mesma chave devolve sempre o mesmo numero.

    Usa crc32 em vez de hash() porque hash() de string muda a cada processo,
    o que faria o preco mudar toda vez que o jogo reabre.
    """
    h = zlib.crc32(chave.encode("utf-8")) & 0xFFFFFFFF
    return lo + (hi - lo) * (h / float(0xFFFFFFFF))


def _janela(G: Mundo) -> str:
    """O mercado remarca precos a cada 4 semanas, nao a cada clique."""
    return "%d-%d" % (G["temporada"], G["semana"] // 4)


def importancia(G: Mundo, j: Jogador) -> float:
    """O quanto o clube atual depende dele. 0 = descartavel, 1 = intocavel."""
    if j["clube"] is None:
        return 0.0
    c = G["clubes"][j["clube"]]
    mesma = sorted([p for p in c["elenco"] if G["jogadores"][p]["pos"] == j["pos"]],
                   key=lambda p: -G["jogadores"][p]["ovr"])
    rank = mesma.index(j["id"]) if j["id"] in mesma else len(mesma)
    posto = {0: 1.0, 1: 0.55}.get(rank, 0.15)
    acima = clamp((j["ovr"] - media_elenco(G, c)) / 12.0, 0.0, 1.0)
    joia = 0.35 if (j["idade"] <= 23 and j["pot"] - j["ovr"] >= 8) else 0.0
    escassez = 0.25 if len(mesma) <= ELENCO_PADRAO[j["pos"]] - 1 else 0.0
    return clamp(0.30 * posto + 0.40 * acima + joia + escassez, 0.0, 1.0)


def _fator_contrato(j: Jogador) -> float:
    """Contrato curto derruba o preco para as DUAS pontas.

    Usar o mesmo fator na venda e na compra e o que impede arbitragem com
    jogadores em fim de contrato.
    """
    if j["contrato"] <= 1:
        return 0.72
    if j["contrato"] >= 4:
        return 1.12
    return 1.0


def preco_pedido(G: Mundo, j: Jogador) -> int:
    """Quanto o dono quer pelo passe. Estavel dentro da janela de 4 semanas.

    Assinatura mantida de proposito: os chamadores antigos passam o dict do
    jogador e continuam funcionando.
    """
    if j["listado"]:
        return int(j["listado"])
    if j["clube"] is None:
        return 0
    premio = (1.15 + 0.95 * importancia(G, j)) * _fator_contrato(j)
    premio *= _ruido("passe-%d-%s" % (j["id"], _janela(G)), 0.94, 1.09)
    return int(j["valor"] * premio / 1000.0) * 1000


def pedido_efetivo(G: Mundo, j: Jogador) -> Tuple[int, bool]:
    """Preco real de balcao e se o clube considera o jogador inegociavel.

    Fonte unica de verdade: a tela mostra este numero e avaliar_clube cobra
    exatamente ele. Antes a tela mostrava um valor e a mesa cobrava outro.
    """
    pedido = preco_pedido(G, j)
    if j["clube"] is None or j["listado"]:
        return pedido, False
    dono = G["clubes"][j["clube"]]
    sobra = sum(1 for p in dono["elenco"] if G["jogadores"][p]["pos"] == j["pos"])
    intocavel = importancia(G, j) >= 0.80 or sobra <= ELENCO_PADRAO[j["pos"]] - 1
    if intocavel:
        pedido = int(pedido * 1.55)
    return pedido, intocavel


def fator_idade_salario(idade: int) -> float:
    """O mercado paga menos pelo veterano: o mesmo overall aos 35 vale um
    contrato bem menor que aos 27 (decidido em 2026-09-25)."""
    if idade >= 35:
        return 0.55
    if idade >= 33:
        return 0.70
    if idade >= 31:
        return 0.85
    return 1.0


LIVRE_DESCONTO_INI = 0.15    # livre recem-saido ja pede 15% abaixo do mercado
LIVRE_DESCONTO_MAX = 0.40    # e encalhado chega a 40% abaixo
LIVRE_SEMANAS_MAX = 10       # semanas sem clube ate o desconto maximo
LIVRE_TETO_DEGRAU = 1.30     # livre desce de patamar cobrando no maximo 30% a mais


def semanas_sem_clube(G: Mundo, j: Jogador) -> int:
    """Ha quanto tempo o livre esta parado. O carimbo e posto toda semana em
    carimbar_livres; sem carimbo ainda (acabou de sair), conta zero."""
    if j["clube"] is not None:
        return 0
    return max(0, semana_absoluta(G) - int(j.get("livre_desde", semana_absoluta(G))))


def desconto_livre(G: Mundo, j: Jogador) -> float:
    frac = min(1.0, semanas_sem_clube(G, j) / float(LIVRE_SEMANAS_MAX))
    return LIVRE_DESCONTO_INI + (LIVRE_DESCONTO_MAX - LIVRE_DESCONTO_INI) * frac


def carimbar_livres(G: Mundo) -> None:
    """Marca a semana em que cada livre ficou sem clube (uma vez)."""
    agora = semana_absoluta(G)
    for pid in G["livres"]:
        j = G["jogadores"].get(pid)
        if j is not None and "livre_desde" not in j:
            j["livre_desde"] = agora


def salario_referencia(j: Jogador) -> int:
    """De onde parte o que o jogador pede: o mercado do overall e da idade de
    hoje. Quem tem clube nunca pede menos que 85% do que ja ganha (quem evoluiu
    com contrato barato pede aumento; o veterano em queda aceita corte de ate
    15%). O livre nao tem contrato a defender: parte so do mercado."""
    mercado = int(salario_de(j["ovr"]) * fator_idade_salario(j["idade"]))
    if j["clube"] is None:
        return mercado
    return max(mercado, int(j["salario"] * piso_salario_atual(j["idade"])))


def piso_salario_atual(idade: int) -> float:
    """Quanto do salario atual quem tem clube defende numa renovacao ou
    transferencia. O veterano acima do mercado aceita corte maior: sem isto o
    piso de 85% apagava a idade da conta."""
    if idade >= 35:
        return 0.55
    if idade >= 33:
        return 0.65
    if idade >= 31:
        return 0.75
    return 0.85


def exigencia_salarial(G: Mundo, j: Jogador, destino: Clube, anos: int = 3) -> int:
    """Quanto o jogador quer por mes para assinar com este clube."""
    base = salario_referencia(j) * 1.12
    livre = j["clube"] is None
    if livre:
        base *= 1.0 - desconto_livre(G, j)
    rep_origem = G["clubes"][j["clube"]]["reputacao"] if j["clube"] else 42
    gap = destino["reputacao"] - rep_origem
    if gap < -8:
        # quanto mais fundo o degrau, mais caro. Curva continua, sem salto.
        # O livre nao tem clube para comparar: desce cobrando pouco a mais.
        base *= min(LIVRE_TETO_DEGRAU if livre else 2.60, 1.0 + (-gap - 8) * 0.032)
    elif gap > 8:
        base *= 1.0 - min(0.16, (gap - 8) * 0.007)
    if j["idade"] <= 23 and j["pot"] - j["ovr"] >= 8:
        melhores = sum(1 for p in destino["elenco"]
                       if G["jogadores"][p]["pos"] == j["pos"]
                       and G["jogadores"][p]["ovr"] > j["ovr"])
        if melhores >= 2:
            base *= 1.25        # promessa nao quer banco
    if anos <= 1:
        base *= 1.10
    elif anos >= 4:
        base *= 0.96
    base *= _ruido("sal-%d-%d-%s" % (j["id"], destino["id"], _janela(G)), 0.96, 1.08)
    return int(base / 100.0) * 100


def avaliar_clube(G: Mundo, prop: Proposta) -> Resposta:
    """O clube dono aceita vender o passe por esse valor?"""
    j = G["jogadores"][prop.jogador]
    comprador = G["clubes"][prop.comprador]
    if j["clube"] == prop.comprador:
        return Resposta(False, "O jogador ja e seu.", 0, True)
    if elenco_cheio(G, comprador):
        return Resposta(False, recado_elenco_cheio(comprador), 0, True)
    if j["clube"] is None:
        return Resposta(True, "Agente livre, nao ha passe a pagar.", 0)
    if j.get("dono"):
        return Resposta(False, "Ele esta emprestado, o passe nao pertence a este clube.", 0, True)
    if prop.valor > comprador["dinheiro"]:
        return Resposta(False, "Voce nao tem esse dinheiro em caixa.", 0)

    dono = G["clubes"][j["clube"]]
    pedido, intocavel = pedido_efetivo(G, j)
    if intocavel:
        recado = "%s nao pretende vende-lo. So sai por algo perto de %s." % (dono["nome"], din(pedido))
    else:
        recado = "%s libera a partir de algo perto de %s." % (dono["nome"], din(pedido))

    if prop.valor >= int(pedido * 0.97):
        return Resposta(True, "Proposta aceita pelo %s." % dono["nome"], pedido)
    if prop.valor < pedido * 0.50:
        return Resposta(False, "Proposta considerada ofensiva. O %s encerrou a conversa." % dono["nome"],
                        pedido, True)
    return Resposta(False, recado, pedido)


# Limite de aceite escondido (decidido em 2026-09-29): o pedido que o
# empresario diz e referencia, nao corte seco. Cada jogador tem, por janela, um
# limite entre 7% abaixo e 7% acima dele - 5% abaixo as vezes fecha, 100% as
# vezes nao. O livre e mais flexivel, e mais ainda quanto mais tempo parado.
LIMITE_ACEITE = (0.93, 1.07)
LIMITE_ACEITE_LIVRE = (0.86, 1.03)


def limite_de_aceite(G: Mundo, j: Jogador, destino: Clube, exig: int, tipo: str = "contrato") -> int:
    """O menor salario que ele aceita de verdade. Estavel na janela: repetir a
    mesma oferta nao vira sorteio."""
    lo, hi = LIMITE_ACEITE_LIVRE if j["clube"] is None else LIMITE_ACEITE
    if j["clube"] is None:
        # parado ha semanas, baixa ainda mais a guarda (ate 4 pontos)
        lo -= 0.04 * min(1.0, semanas_sem_clube(G, j) / float(LIVRE_SEMANAS_MAX))
    fator = _ruido("aceite-%s-%d-%d-%s" % (tipo, j["id"], destino["id"], _janela(G)), lo, hi)
    return int(exig * fator / 100.0) * 100


def avaliar_jogador(G: Mundo, prop: Proposta) -> Resposta:
    """O jogador aceita o salario, a duracao e o tamanho do clube?"""
    j = G["jogadores"][prop.jogador]
    destino = G["clubes"][prop.comprador]
    exig = exigencia_salarial(G, j, destino, prop.anos)
    if prop.salario >= limite_de_aceite(G, j, destino, exig):
        return Resposta(True, "Acertado: %s por mes, %s." % (din(prop.salario), plural(prop.anos, "ano")), exig)
    if prop.salario < exig * 0.60:
        return Resposta(False, "Ele nem levou a proposta ao empresario.", exig, True)
    rep_origem = G["clubes"][j["clube"]]["reputacao"] if j["clube"] else 42
    if destino["reputacao"] <= rep_origem - 25:
        motivo = "Vem de um patamar bem maior. Abaixo de %s nem senta na mesa." % din(exig)
    else:
        motivo = "O empresario avisa que abaixo de %s nao ha conversa." % din(exig)
    return Resposta(False, motivo, exig)


MAX_EMPRESTADOS = 4      # quantos emprestados cabem no elenco ao mesmo tempo


def _exigencia_bruta(G: Mundo, j: Jogador, destino: Clube) -> float:
    """A conta crua, que PODE passar de 100. E o excesso que vira dinheiro."""
    dono = G["clubes"][j["clube"]]
    base = 45.0 + (j["ovr"] - 58) * 2.2
    base -= (destino["reputacao"] - dono["reputacao"]) * 0.4
    base += importancia(G, j) * 25.0
    base *= _ruido("emp-%d-%d-%s" % (j["id"], destino["id"], _janela(G)), 0.95, 1.06)
    return base


def exigencia_emprestimo(G: Mundo, j: Jogador, destino: Clube) -> int:
    """Percentual do salario que o dono quer que o destino assuma."""
    return int(clamp(_exigencia_bruta(G, j, destino), 15, 100))


def taxa_emprestimo(G: Mundo, j: Jogador, destino: Clube) -> int:
    """Dinheiro que o dono cobra ALEM do salario para ceder o jogador.

    Enquanto a conta cabe em 100% do salario, nao ha taxa. O que passa disso
    e o preco de tirar um jogador que o dono nao queria ceder - antes esse
    excesso simplesmente evaporava no clamp, e craque saia de graca.
    """
    bruta = _exigencia_bruta(G, j, destino)
    if bruta <= 100.0:
        return 0
    return int(preco_pedido(G, j) * (bruta - 100.0) * 0.006 / 1000.0) * 1000


def emprestados_no_elenco(G: Mundo, c: Clube) -> int:
    return sum(1 for p in c["elenco"] if G["jogadores"].get(p, {}).get("dono"))


def piso_opcao_compra(G: Mundo, j: Jogador) -> int:
    """Menor preco pelo qual o dono aceita travar o passe para o fim do emprestimo.

    Sem esse piso dava para pegar emprestado com opcao de R$ 1 e comprar o
    jogador por nada na temporada seguinte: o emprestimo virava compra de graca.
    """
    return int(preco_pedido(G, j) * 0.85 / 1000.0) * 1000


def avaliar_emprestimo(G: Mundo, prop: Proposta) -> Resposta:
    """O dono cede por emprestimo nesses termos?"""
    j = G["jogadores"][prop.jogador]
    if j["clube"] is None or j.get("dono"):
        return Resposta(False, "Este jogador nao esta disponivel para emprestimo.", 0, True)
    destino = G["clubes"][prop.comprador]
    if elenco_cheio(G, destino):
        return Resposta(False, recado_elenco_cheio(destino), 0, True)
    if emprestados_no_elenco(G, destino) >= MAX_EMPRESTADOS:
        return Resposta(False, "Voce ja tem %d emprestados no elenco, o maximo permitido. "
                        "Devolva ou compre um antes de pegar outro." % MAX_EMPRESTADOS,
                        0, True)
    dono = G["clubes"][j["clube"]]
    imp = importancia(G, j)
    # peca de time nao vai jogar em clube menor por emprestimo: isso era o
    # buraco que deixava craque de Serie A cair em qualquer elenco
    if imp >= 0.55 and destino["reputacao"] < dono["reputacao"] - 8:
        return Resposta(False, "%s e peca do %s e nao troca por um clube menor."
                        % (j["nome"], dono["nome"]), 100, True)
    if imp >= 0.80:
        return Resposta(False, "%s e intocavel no %s. Nao sai nem por emprestimo."
                        % (j["nome"], dono["nome"]), 100, True)
    exig = exigencia_emprestimo(G, j, destino)
    taxa = taxa_emprestimo(G, j, destino)
    piso = piso_opcao_compra(G, j)
    if prop.opcao_compra and prop.opcao_compra < piso:
        return Resposta(False, "O %s so trava o passe de %s a partir de %s."
                        % (dono["nome"], j["nome"], din(piso)), exig)
    if taxa and prop.valor < taxa:
        return Resposta(False, "O %s so empresta %s mediante taxa de %s, alem do salario."
                        % (dono["nome"], j["nome"], din(taxa)), exig)
    if taxa and prop.valor > destino["dinheiro"]:
        return Resposta(False, "Voce nao tem %s em caixa para a taxa." % din(prop.valor), exig)
    if prop.pct_salario >= exig:
        extra = (" mais %s de taxa" % din(taxa)) if taxa else ""
        return Resposta(True, "Emprestimo acertado: voce banca %d%% do salario%s."
                        % (prop.pct_salario, extra), exig)
    return Resposta(False, "O %s quer que voce assuma pelo menos %d%%." % (dono["nome"], exig), exig)


def fechar_compra(G: Mundo, prop: Proposta) -> str:
    """Executa a transferencia ja aprovada pelas duas pontas.

    Com a janela fechada o acordo vale, mas fica agendado: o jogador troca de
    clube na abertura. Negociar pode sempre; entrar e sair, so na janela.
    Agente livre e a excecao: ja saiu do clube, entao assina na hora com quem
    fechar primeiro, janela aberta ou fechada (vale para a IA tambem).
    """
    j = G["jogadores"][prop.jogador]
    if not assina_na_hora(G, j):
        return agendar(G, prop, "Contratacao acertada")
    comprador = G["clubes"][prop.comprador]
    nome_antigo = nome_clube(G, j["clube"])
    transferir(G, prop.jogador, prop.comprador, prop.valor)
    j["salario"] = prop.salario
    j["contrato"] = int(clamp(prop.anos, 1, 5))
    noticia(G, "%s contratou %s (%s) do %s por %s."
            % (comprador["nome"], j["nome"], j["pos"], nome_antigo, din(prop.valor)))
    return ("CONTRATADO: %s assina por %s. Passe %s, salario %s por mes."
            % (j["nome"], plural(j["contrato"], "ano"), din(prop.valor), din(prop.salario)))


def fechar_emprestimo(G: Mundo, prop: Proposta) -> str:
    if not mercado_aberto(G):
        return agendar(G, prop, "Emprestimo acertado")
    j = G["jogadores"][prop.jogador]
    destino = G["clubes"][prop.comprador]
    dono = G["clubes"][j["clube"]]
    taxa = int(prop.valor or 0)
    if taxa:
        lancar(G, destino, -taxa, "emprestimos")
        lancar(G, dono, taxa, "emprestimos")
    emprestar(G, prop.jogador, prop.comprador, prop.pct_salario)
    j["emp_opcao"] = int(prop.opcao_compra)
    noticia(G, "%s pegou %s emprestado do %s." % (destino["nome"], j["nome"], dono["nome"]))
    extra = ""
    if taxa:
        extra += " Taxa de emprestimo: %s." % din(taxa)
    if prop.opcao_compra:
        extra += " Opcao de compra fixada em %s." % din(prop.opcao_compra)
    return ("%s chega por emprestimo ate o fim da temporada. Voce paga %d%% do salario (%s por mes).%s"
            % (j["nome"], prop.pct_salario, din(j["salario"] * prop.pct_salario // 100), extra))


def opcao_disponivel(G: Mundo, j: Jogador, clube_id: int) -> int:
    """Valor da opcao de compra de um emprestado, 0 se nao houver."""
    if not j.get("dono") or j["clube"] != clube_id:
        return 0
    return int(j.get("emp_opcao") or 0)


def exercer_opcao(G: Mundo, pid: int, clube_id: int) -> str:
    j = G["jogadores"][pid]
    preco = opcao_disponivel(G, j, clube_id)
    c = G["clubes"][clube_id]
    if preco <= 0:
        return "Nao ha opcao de compra combinada para %s." % j["nome"]
    if preco > c["dinheiro"]:
        return "Caixa insuficiente: a opcao custa %s." % din(preco)
    dono = G["clubes"][j["dono"]]
    devolver_emprestimo(G, pid)
    transferir(G, pid, clube_id, preco)
    j["emp_opcao"] = 0
    noticia(G, "%s comprou %s em definitivo por %s." % (c["nome"], j["nome"], din(preco)))
    return "%s comprado em definitivo ao %s por %s." % (j["nome"], dono["nome"], din(preco))


def necessidade(G: Mundo, j: Jogador, comprador: Clube) -> float:
    """O quanto ESTE comprador precisa deste jogador. 0 = nao muda nada."""
    na_posicao = [G["jogadores"][p]["ovr"] for p in comprador["elenco"]
                  if G["jogadores"][p]["pos"] == j["pos"]]
    if not na_posicao:
        return 1.0
    melhor = max(na_posicao)
    falta = clamp((j["ovr"] - melhor) / 10.0, 0.0, 1.0)
    magro = 0.35 if len(na_posicao) < ELENCO_PADRAO[j["pos"]] else 0.0
    return clamp(falta + magro, 0.0, 1.0)


def semanas_no_clube(G: Mundo, j: Jogador) -> int:
    """Ha quanto tempo ele esta ali. 999 se veio da base ou do mundo inicial."""
    if not j.get("desde"):
        return 999
    return (G["temporada"] * 100 + G["semana"]) - int(j["desde"])


def valor_para_comprador(G: Mundo, j: Jogador, comprador: Clube) -> int:
    """Teto que ESTE clube paga por este jogador.

    NAO usa importancia(): essa e a visao do dono, e reaproveita-la aqui abriria
    arbitragem (comprar de quem nao precisa e revender a quem precisa).

    A faixa vai de 0.80 a 1.32 do valor de mercado conforme a necessidade, e o
    caixa ainda acrescenta ate 8%. Antes o teto parava em 0.98 e ficava SEMPRE
    abaixo do pedido do dono, que comeca em 1.15: as duas pontas nunca se
    cruzavam e o mercado morria - ninguem comprava de voce, e as sondagens
    nasciam mortas. Quem precisa de verdade paga acima do valor de mercado,
    que e como o futebol funciona.

    O que impede o giro continua sendo a trava de baixo, nao o teto: nao da
    para revender com lucro quem acabou de chegar.
    """
    base = j["valor"] * _fator_contrato(j) * (0.80 + 0.52 * necessidade(G, j, comprador))
    folga = clamp(comprador["dinheiro"] / max(1.0, base), 0.0, 3.0)
    base *= 0.92 + 0.16 * min(1.0, folga)
    if j["idade"] >= 31:
        base *= 0.85
    base *= _ruido("oferta-%d-%d-%s" % (j["id"], comprador["id"], _janela(G)), 0.92, 1.04)
    # trava anti-giro: ninguem paga premio por quem acabou de chegar. Renovar
    # contrato para revender caro deixa de ser lucro instantaneo.
    if j.get("pago") and semanas_no_clube(G, j) < 16:
        base = min(base, j["pago"] * 0.92)   # revenda imediata sempre sai no prejuizo
    return int(base / 1000.0) * 1000


# compatibilidade: assinaturas antigas continuam de pe, agora so delegam
def aceita_proposta(G: Mundo, j: Jogador, oferta: int) -> Tuple[bool, int]:
    r = avaliar_clube(G, Proposta(jogador=j["id"], comprador=G["clube"], valor=oferta))
    return r.aceita, r.pedido


def aceita_contrato(G: Mundo, j: Jogador, salario_oferta: int, clube_destino: Clube) -> Tuple[bool, int]:
    r = avaliar_jogador(G, Proposta(jogador=j["id"], comprador=clube_destino["id"],
                                    salario=salario_oferta))
    return r.aceita, r.pedido


# ----------------------------------------------------------------------------
# RENOVACAO, VITRINE, RESCISAO E PROPOSTAS RECEBIDAS
#
# Mesmo contrato da mesa de compra: a interface pergunta, o motor responde.
#
# Duas regras que faltavam e davam para explorar:
#   1. o pedido do empresario e ESTAVEL dentro da janela de 4 semanas, o que
#      acaba com o truque de fechar e reabrir a tela ate sair numero baixo;
#   2. as propostas recebidas sao sorteadas UMA vez por semana e guardadas no
#      save, em vez de nascerem a cada abertura da tela.
# ----------------------------------------------------------------------------

TIPO_RENOVACAO = "renovacao"


def exigencia_renovacao(G: Mundo, j: Jogador, anos: int = 3) -> int:
    """Salario mensal que o jogador quer para renovar com o clube dele.

    Quem e peca do time cobra pelo posto; promessa cobra pelo futuro; veterano
    aceita menos. Estavel dentro da janela: a mesma tela reaberta pede o mesmo.
    """
    c = G["clubes"][j["clube"]]
    base = salario_referencia(j) * 1.12
    base *= 1.0 + 0.45 * importancia(G, j)
    if j["idade"] <= 23 and j["pot"] - j["ovr"] >= 8:
        base *= 1.18
    elif j["idade"] >= 33:
        base *= 0.88
    if j["ovr"] > media_elenco(G, c) + 6:
        base *= 1.10
    if j["moral"] < 45:
        base *= 1.12
    elif j["moral"] >= 80:
        base *= 0.95
    if anos <= 1:
        base *= 1.10
    elif anos >= 4:
        base *= 0.96
    base *= _ruido("renov-%d-%s" % (j["id"], _janela(G)), 0.97, 1.06)
    return int(base / 100.0) * 100


def avaliar_renovacao(G: Mundo, prop: Proposta) -> Resposta:
    """O jogador aceita renovar nesses termos?"""
    j = G["jogadores"][prop.jogador]
    if j.get("dono"):
        return Resposta(False, "%s esta emprestado: o contrato e do dono do passe." % j["nome"],
                        0, True)
    if j["clube"] != prop.comprador:
        return Resposta(False, "Ele nao e do seu clube.", 0, True)
    exig = exigencia_renovacao(G, j, prop.anos)
    if prop.salario >= limite_de_aceite(G, j, G["clubes"][j["clube"]], exig, "renovacao"):
        return Resposta(True, "Acertado: %s por mes, %s." % (din(prop.salario), plural(prop.anos, "ano")),
                        exig)
    if prop.salario < exig * 0.72:
        return Resposta(False, "O empresario devolveu a proposta sem levar ao jogador.", exig, True)
    return Resposta(False, "O empresario insiste em algo perto de %s por mes." % din(exig), exig)


def fechar_renovacao(G: Mundo, prop: Proposta) -> str:
    """Grava a renovacao ja aceita pelas duas pontas."""
    j = G["jogadores"][prop.jogador]
    j["salario"] = int(prop.salario)
    j["contrato"] = int(clamp(prop.anos, 1, 5))
    mexer_moral(G, j, 12, "renovou o contrato")
    noticia(G, "%s renovou com o %s por %s."
            % (j["nome"], G["clubes"][j["clube"]]["nome"], plural(j["contrato"], "ano")))
    return "%s renovou por %s, %s por mes." % (j["nome"], plural(j["contrato"], "ano"), din(prop.salario))


def romper_renovacao(G: Mundo, j: Jogador) -> str:
    """Conversa esgotada: ele fecha a porta e a moral cai."""
    mexer_moral(G, j, -8, "a renovacao nao saiu")
    return "%s recusou renovar e vai ouvir o mercado." % j["nome"]


def preco_sugerido(G: Mundo, j: Jogador, pct: int = 130) -> int:
    """Preco de vitrine a partir do valor de mercado, arredondado em milhares."""
    return int(max(1000.0, j["valor"] * pct / 100.0) / 1000.0) * 1000


LIVRE_SEM_REVENDA = 8        # semanas: livre contratado nao volta ao mercado antes disso


def revenda_travada(G: Mundo, j: Jogador) -> int:
    """Semanas que faltam para poder vender quem chegou como agente livre."""
    return max(0, int(j.get("livre_trava_ate", 0)) - semana_absoluta(G))


def recado_revenda(G: Mundo, j: Jogador) -> str:
    return ("%s chegou como agente livre: so pode ser vendido daqui a %s."
            % (j["nome"], plural(revenda_travada(G, j), "semana")))


def por_a_venda(G: Mundo, pid: int, preco: int) -> Tuple[bool, str]:
    """Coloca (ou reprecifica) o jogador na vitrine."""
    j = G["jogadores"][pid]
    if j.get("dono"):
        return False, "%s esta emprestado, o passe nao e seu." % j["nome"]
    if int(preco) > 0 and revenda_travada(G, j):
        return False, recado_revenda(G, j)
    j["listado"] = max(0, int(preco))
    if not j["listado"]:
        return True, "%s saiu da vitrine." % j["nome"]
    return True, "%s esta na vitrine por %s." % (j["nome"], din(j["listado"]))


def tirar_da_vitrine(G: Mundo, pid: int) -> Tuple[bool, str]:
    j = G["jogadores"][pid]
    j["listado"] = 0
    j["emp_listado"] = 0
    _descartar_oferta(G, pid)
    return True, "%s saiu da vitrine." % j["nome"]


def multa_rescisao(G: Mundo, j: Jogador) -> int:
    """Metade do que ainda seria pago em salario ate o fim do contrato."""
    return int(j["salario"] * 4 * max(1, j["contrato"]) * 0.5)


def rescindir_contrato(G: Mundo, pid: int) -> Tuple[bool, str]:
    """Dispensa o jogador pagando multa. Devolve (feito, recado)."""
    j = G["jogadores"][pid]
    if j.get("dono"):
        return False, "%s esta emprestado: devolva ao dono antes de rescindir." % j["nome"]
    if j["clube"] is None:
        return False, "%s nao tem contrato com ninguem." % j["nome"]
    c = G["clubes"][j["clube"]]
    multa = multa_rescisao(G, j)
    if multa > c["dinheiro"]:
        return False, "Caixa insuficiente: a multa de %s custa %s." % (j["nome"], din(multa))
    lancar(G, c, -multa, "rescisoes")
    if pid in c["elenco"]:
        c["elenco"].remove(pid)
    if pid in c.get("escalacao", []):
        c["escalacao"].remove(pid)
    j["clube"] = None
    j["listado"] = 0
    j["emp_listado"] = 0
    G["livres"].append(pid)
    _descartar_oferta(G, pid)
    noticia(G, "%s dispensou %s." % (c["nome"], j["nome"]))
    return True, ("%s foi dispensado. Multa de %s, a folha alivia %s por mes."
                  % (j["nome"], din(multa), din(j["salario"])))


def cedidos(G: Mundo, c: Clube) -> List[Jogador]:
    """Quem eu cedi por emprestimo e esta jogando em outro clube."""
    out = []
    for pid in c.get("emprestados", []):
        j = G["jogadores"].get(pid)
        if j and j.get("dono") == c["id"]:
            out.append(j)
    return out


def ofertas_emprestimo(G: Mundo, j: Jogador, limite: int = 6) -> List[Tuple[Clube, int]]:
    """Clubes dispostos a levar o jogador, com a fatia do salario que assumem.

    Estavel dentro da janela de 4 semanas: reabrir a tela nao re-sorteia.
    """
    if j["clube"] is None or j.get("dono"):
        return []
    c = G["clubes"][j["clube"]]
    interessados = [cl for cl in G["clubes"].values()
                    if cl["divisao"] != "EX" and cl["id"] != c["id"]
                    and cl["reputacao"] <= c["reputacao"] + 6
                    and conta_posicao(G, cl, j["pos"]) <= ELENCO_PADRAO[j["pos"]] + 1]
    interessados.sort(key=lambda cl: -cl["reputacao"])
    out = []
    for cl in interessados[:limite]:
        cap = clamp(cl["dinheiro"] / max(1, j["salario"] * 12) * 30, 15, 95)
        fator = _ruido("cede-%d-%d-%s" % (j["id"], cl["id"], _janela(G)), 0.70, 1.20)
        out.append((cl, int(clamp(cap * fator, 10, 100))))
    return out


def ceder_por_emprestimo(G: Mundo, pid: int, destino_id: int, pct: int) -> Tuple[bool, str]:
    """Executa a cessao por emprestimo ja combinada."""
    j = G["jogadores"][pid]
    if j.get("dono"):
        return False, "%s ja esta emprestado." % j["nome"]
    if j["contrato"] <= 0:
        return False, "Contrato de %s acabando: renove antes de emprestar." % j["nome"]
    if not mercado_aberto(G):
        return True, agendar(G, Proposta(jogador=pid, comprador=destino_id,
                                         pct_salario=int(pct), tipo=TIPO_EMPRESTIMO),
                             "Cessao acertada")
    origem = G["clubes"][j["clube"]]
    destino = G["clubes"][destino_id]
    emprestar(G, pid, destino_id, pct)
    j["emp_listado"] = 0
    noticia(G, "%s cedeu %s ao %s por emprestimo." % (origem["nome"], j["nome"], destino["nome"]))
    return True, ("%s cedido ao %s ate o fim da temporada. Eles pagam %d%% do salario (%s por mes)."
                  % (j["nome"], destino["nome"], pct, din(j["salario"] * pct // 100)))


def _stamp_semana(G: Mundo) -> str:
    """Uma chave por semana jogada. Era temporada-semana, mas G["semana"] fica
    em 0 no estadual inteiro: as propostas nunca se renovavam ali."""
    return "%d-a%d" % (G["temporada"], semana_absoluta(G))


# ----------------------------------------------------------------------------
# JANELA E TRANSFERENCIAS AGENDADAS
#
# Negociar pode a qualquer momento; ENTRAR e SAIR, so com a janela aberta.
# Fora da janela o acordo e fechado e fica guardado em G["agendadas"], e a
# troca acontece sozinha na primeira semana de janela - revalidando tudo, que
# em quatro meses o caixa muda, o elenco enche e o jogador pode ter sido
# vendido para outro.
# ----------------------------------------------------------------------------

def proxima_janela(G: Mundo) -> int:
    """Em quantas semanas a janela abre. 0 se ja esta aberta."""
    if mercado_aberto(G):
        return 0
    futuras = [s for s in JANELAS if s > G["semana"]]
    if futuras:
        return futuras[0] - G["semana"]
    # nao abre mais neste ano: abre na virada, junto com a pre-temporada
    return max(1, SEMANAS_LIGA + 1 - G["semana"])


def assina_na_hora(G: Mundo, j: Jogador) -> bool:
    """A contratacao se cumpre agora? Com a janela aberta, sempre; fechada, so
    agente livre - ele nao tem clube de onde sair."""
    return mercado_aberto(G) or j["clube"] is None


def presos_em_acerto(G: Mundo) -> set:
    """Quem ja tem acerto fechado com algum clube. Ninguem mais assina com eles,
    nem a IA pegando agente livre."""
    return {a["jogador"] for a in agendadas(G)}


def recado_janela(G: Mundo) -> str:
    faltam = proxima_janela(G)
    if not faltam:
        return "Janela aberta: o negocio se cumpre na hora."
    return ("Janela fechada: da para acertar agora, mas ele so troca de clube na "
            "abertura, em %s." % plural(faltam, "semana"))


def agendadas(G: Mundo) -> List[Dict[str, Any]]:
    lista = G.setdefault("agendadas", [])
    return lista


def agendar(G: Mundo, prop: Proposta, rotulo: str) -> str:
    """Guarda o acordo fechado fora da janela."""
    j = G["jogadores"][prop.jogador]
    origem = j["clube"]
    agendadas(G).append({
        "jogador": int(prop.jogador), "de": int(origem) if origem else None,
        "para": int(prop.comprador), "valor": int(prop.valor),
        "salario": int(prop.salario), "anos": int(prop.anos),
        "pct_salario": int(prop.pct_salario), "opcao_compra": int(prop.opcao_compra),
        "tipo": prop.tipo, "temporada": int(G["temporada"]), "semana": int(G["semana"]),
    })
    return "%s: %s. %s" % (rotulo, j["nome"], recado_janela(G))


def minhas_agendadas(G: Mundo) -> List[Tuple[int, Dict[str, Any]]]:
    """As que envolvem o meu clube, com o indice para poder cancelar."""
    meu = G.get("clube")
    return [(i, a) for i, a in enumerate(agendadas(G))
            if meu in (a.get("de"), a.get("para"))]


def cancelar_agendada(G: Mundo, indice: int) -> Tuple[bool, str]:
    lista = agendadas(G)
    if not (0 <= indice < len(lista)):
        return False, "Este acerto nao existe mais."
    a = lista.pop(indice)
    j = G["jogadores"].get(a["jogador"])
    return True, "Acerto por %s cancelado." % (j["nome"] if j else "jogador")


def _validar_agendada(G: Mundo, a: Dict[str, Any]) -> Optional[str]:
    """Devolve o motivo da queda, ou None se o acordo ainda vale."""
    j = G["jogadores"].get(a["jogador"])
    destino = G["clubes"].get(a["para"])
    if not j or not destino:
        return "jogador ou clube nao existe mais"
    if a.get("de") is not None and j["clube"] != a["de"]:
        return "ele mudou de clube antes da janela abrir"
    if a.get("de") is None and j["clube"] is not None:
        return "ele assinou com outro clube antes"
    if elenco_cheio(G, destino):
        return "o elenco do %s ja esta cheio" % destino["nome"]
    if a["tipo"] == TIPO_EMPRESTIMO:
        if j.get("dono"):
            return "ele ja esta emprestado a outro clube"
        return None
    if a["valor"] > destino["dinheiro"]:
        return "o %s nao tem mais %s em caixa" % (destino["nome"], din(a["valor"]))
    return None


def executar_agendadas(G: Mundo) -> List[str]:
    """Cumpre, na abertura da janela, tudo o que foi acertado antes. Com a
    janela fechada so cumpre acerto com agente livre (save de antes da regra
    que faz livre assinar na hora)."""
    if not agendadas(G):
        return []
    aberto = mercado_aberto(G)
    pendentes, fica = [], []
    for a in agendadas(G):
        livre = a.get("de") is None and a["tipo"] != TIPO_EMPRESTIMO
        (pendentes if aberto or livre else fica).append(a)
    if not pendentes:
        return []
    recados = []
    G["agendadas"] = fica
    prefixo = "Janela aberta: " if aberto else ""
    for a in pendentes:
        queda = _validar_agendada(G, a)
        j = G["jogadores"].get(a["jogador"])
        nome = j["nome"] if j else "jogador"
        if queda:
            recados.append("Acerto por %s caiu: %s." % (nome, queda))
            if G.get("clube") in (a.get("de"), a.get("para")):
                noticia(G, "O acerto por %s nao se cumpriu: %s." % (nome, queda))
            continue
        if a["tipo"] == TIPO_EMPRESTIMO:
            prop = Proposta(jogador=a["jogador"], comprador=a["para"],
                            pct_salario=a["pct_salario"], opcao_compra=a["opcao_compra"],
                            tipo=TIPO_EMPRESTIMO)
            recados.append(prefixo + fechar_emprestimo(G, prop))
        else:
            prop = Proposta(jogador=a["jogador"], comprador=a["para"], valor=a["valor"],
                            salario=a["salario"] or j["salario"], anos=a["anos"] or 3)
            recados.append(prefixo + fechar_compra(G, prop))
    return recados


# ----------------------------------------------------------------------------
# SONDAGENS: O MERCADO VEM ATRAS DO QUE E SEU
#
# Antes so chegava proposta por quem estava na vitrine. Quem nao listasse
# ninguem nunca recebia nada, e o mercado parecia morto. Agora ha duas fontes:
# a vitrine (voce ofereceu) e a sondagem espontanea (eles vieram atras).
# ----------------------------------------------------------------------------

# quanto do pedido uma sondagem espontanea costuma cobrir
SONDAGEM_MIN, SONDAGEM_MAX = 0.82, 1.12


NIVEL_COMPRADOR = 3      # o jogador tem que chegar a 3 pontos da media do elenco de quem compra


def serve_para(G: Mundo, j: Jogador, cl: Clube) -> bool:
    """Ele entra no elenco deste clube? Sem isto Leverkusen e Ajax mandavam
    proposta por jogador de 50 de overall da Serie D (2026-09-29). Promessa
    jovem vale pelo teto, nao pelo overall de hoje."""
    media = media_elenco(G, cl)
    if j["ovr"] >= media - NIVEL_COMPRADOR:
        return True
    return j["idade"] <= 21 and j["pot"] >= media + 2


def _compradores_possiveis(G: Mundo, j: Jogador, preco: int) -> List[Clube]:
    meu = G.get("clube")
    return [cl for cl in G["clubes"].values()
            if cl["divisao"] != "EX" and cl["id"] != meu
            and not elenco_cheio(G, cl)
            and verba_contratacao(G, cl, j["salario"]) >= preco
            and cl["reputacao"] > j["ovr"] - 26
            and serve_para(G, j, cl)]


def _comprador_interessado(G: Mundo, j: Jogador, candidatos: List[Clube]) -> Optional[Clube]:
    """Sorteia quem vem atras, pesado pela necessidade.

    Sortear a esmo entre 50 clubes quase sempre caia em alguem que nao precisa
    do jogador - e quem nao precisa nao paga nada que preste. Quem vem atras do
    seu zagueiro e o clube que esta mal na zaga.
    """
    if not candidatos:
        return None
    pesos = [0.12 + necessidade(G, j, cl) for cl in candidatos]
    if sum(pesos) <= 0:
        return None
    return rng.choices(candidatos, weights=pesos)[0]


def _chance_sondagem(G: Mundo, j: Jogador, c: Clube) -> float:
    """O quanto o mercado se interessa por um jogador que NAO esta a venda."""
    if j.get("dono") or da_base(j) or j["listado"]:
        return 0.0
    base = 0.012
    acima = j["ovr"] - media_elenco(G, c)
    if acima > 0:
        base += min(0.055, acima * 0.011)          # destaque chama atencao
    if j["idade"] <= 23 and j["pot"] - j["ovr"] >= 6:
        base += 0.030                              # promessa e o que mais some
    if j["contrato"] <= 1:
        base += 0.045                              # fim de contrato e pechincha
    if j.get("j", 0) >= 8 and j.get("g", 0) + j.get("a", 0) >= 4:
        base += 0.030                              # quem aparece em campo aparece no mercado
    if j["idade"] >= 32:
        base *= 0.45
    if importancia(G, j) >= 0.8:
        base *= 1.35                               # justamente o que voce nao quer vender
    return clamp(base, 0.0, 0.22)


def _sortear_ofertas(G: Mundo) -> List[List[int]]:
    """As propostas da semana pelos meus jogadores, das duas fontes."""
    c = G["clubes"][G["clube"]]
    itens: List[List[int]] = []
    ja = set()
    presos = presos_em_acerto(G)
    for pid in list(c["elenco"]):
        j = G["jogadores"][pid]
        # acertado com alguem (janela fechada) ou livre recem-chegado: ninguem oferta
        if j.get("dono") or da_base(j) or pid in presos or revenda_travada(G, j):
            continue
        if j["listado"]:
            # vitrine: o preco e seu, e quem cobre o pedido aparece rapido
            preco = int(j["listado"])
            compradores = _compradores_possiveis(G, j, preco)
            for _ in range(3):             # tres clubes olham, o melhor aparece
                cl = _comprador_interessado(G, j, compradores)
                if cl is None:
                    break
                teto = valor_para_comprador(G, j, cl)
                if preco > teto * 1.15:
                    continue               # pediu acima do que este enxerga
                if rng.random() < 0.72:
                    itens.append([pid, cl["id"], int(min(preco, max(teto, preco * 0.82)))])
                    ja.add(pid)
                    break
        else:
            if rng.random() >= _chance_sondagem(G, j, c):
                continue
            pedido = preco_pedido(G, j)
            compradores = _compradores_possiveis(G, j, pedido)
            if not compradores:
                continue
            cl = _comprador_interessado(G, j, compradores)
            if cl is None:
                continue
            teto = valor_para_comprador(G, j, cl)
            oferta = int(pedido * rng.uniform(SONDAGEM_MIN, SONDAGEM_MAX))
            oferta = int(min(oferta, teto * 1.12))
            if oferta < pedido * 0.45:
                continue                   # sondagem ofensiva nem chega na mesa
            itens.append([pid, cl["id"], oferta])
            ja.add(pid)
    return itens


def sondagens_por_emprestimo(G: Mundo) -> List[Tuple[Jogador, Clube, int]]:
    """Clubes que querem levar por emprestimo quem esta encostado em voce."""
    c = G["clubes"][G["clube"]]
    caixa = G.setdefault("emp_ofertas", {"stamp": "", "itens": []})
    if caixa.get("stamp") != _stamp_semana(G):
        caixa["stamp"] = _stamp_semana(G)
        itens = []
        for pid in list(c["elenco"]):
            j = G["jogadores"][pid]
            if j.get("dono") or da_base(j) or not emprestavel(G, j) or j["contrato"] <= 0:
                continue
            if rng.random() > 0.16:
                continue
            ofertas = ofertas_emprestimo(G, j, limite=3)
            if ofertas:
                cl, pct = max(ofertas, key=lambda t: t[1])
                itens.append([pid, cl["id"], int(pct)])
        caixa["itens"] = itens
    saida = []
    for pid, cid, pct in list(caixa["itens"]):
        j = G["jogadores"].get(pid)
        cl = G["clubes"].get(cid)
        if not j or not cl or j["clube"] != G["clube"] or j.get("dono"):
            continue
        saida.append((j, cl, int(pct)))
    return saida


def propostas_recebidas(G: Mundo) -> List[Tuple[Jogador, Clube, int]]:
    """Ofertas da semana pelos jogadores que voce colocou na vitrine."""
    caixa = G.setdefault("ofertas", {"stamp": "", "itens": []})
    if caixa.get("stamp") != _stamp_semana(G):
        caixa["stamp"] = _stamp_semana(G)
        caixa["itens"] = _sortear_ofertas(G)
        caixa["contras"] = {}
    saida = []
    presos = presos_em_acerto(G)
    for pid, cid, valor in list(caixa["itens"]):
        j = G["jogadores"].get(pid)
        cl = G["clubes"].get(cid)
        if pid in presos:
            continue                    # vendido com a janela fechada: acabou a conversa
        # descarta o que envelheceu: jogador que saiu, clube que gastou o caixa.
        # NAO exige mais estar na vitrine: sondagem espontanea nasce justamente
        # de quem nao esta a venda, e essa condicao apagava todas elas.
        if not j or not cl or j["clube"] != G["clube"] or j.get("dono"):
            continue
        # o comprador tambem guarda a folha: so oferta o que cabe na verba dele
        if verba_contratacao(G, cl, j["salario"]) < valor:
            continue
        saida.append((j, cl, int(valor)))
    saida.sort(key=lambda t: -t[2])
    return saida


def _descartar_oferta(G: Mundo, pid: int) -> None:
    caixa = G.get("ofertas")
    if isinstance(caixa, dict) and caixa.get("itens"):
        caixa["itens"] = [it for it in caixa["itens"] if it[0] != pid]


def aceitar_oferta(G: Mundo, pid: int, cid: int, valor: int) -> Tuple[bool, str]:
    """Vende o jogador para quem ofereceu, revalidando a proposta."""
    j = G["jogadores"].get(pid)
    cl = G["clubes"].get(cid)
    if not j or not cl or j["clube"] != G["clube"] or j.get("dono"):
        return False, "Esta proposta nao vale mais."
    if pid in presos_em_acerto(G):
        _descartar_oferta(G, pid)
        return False, "%s ja tem acerto fechado: sai na abertura da janela." % j["nome"]
    if revenda_travada(G, j):
        return False, recado_revenda(G, j)
    if cl["dinheiro"] < valor:
        return False, "O %s nao tem mais esse dinheiro em caixa." % cl["nome"]
    if not mercado_aberto(G):
        _descartar_oferta(G, pid)
        return True, agendar(G, Proposta(jogador=pid, comprador=cid, valor=int(valor),
                                         salario=j["salario"], anos=max(1, j["contrato"])),
                             "Venda acertada")
    vendedor = G["clubes"][G["clube"]]["nome"]
    transferir(G, pid, cid, valor)
    noticia(G, "%s vendeu %s ao %s por %s." % (vendedor, j["nome"], cl["nome"], din(valor)))
    _descartar_oferta(G, pid)
    return True, "VENDIDO: %s para o %s por %s." % (j["nome"], cl["nome"], din(valor))


def recusar_oferta(G: Mundo, pid: int) -> Tuple[bool, str]:
    j = G["jogadores"].get(pid)
    _descartar_oferta(G, pid)
    return True, "Proposta por %s recusada." % (j["nome"] if j else "jogador")


# ----------------------------------------------------------------------------
# CONTRAPROPOSTA
#
# A oferta que chega nao e a ultima palavra. Voce pede um valor; o comprador
# compara com o que ele acha que o jogador vale para ELE (valor_para_comprador)
# e com a verba dele. Cabe: fecha no seu valor. Passa um pouco: ele sobe a
# oferta ate um meio-termo. Passa muito: ele retira a proposta. Duas
# contrapropostas por oferta por semana - depois a oferta fica como esta.
# ----------------------------------------------------------------------------

CONTRAS_POR_OFERTA = 2


def _mudar_oferta(G: Mundo, pid: int, cid: int, valor: Optional[int]) -> None:
    """Troca o valor de UMA oferta (pid, cid) ou, com valor None, a retira."""
    caixa = G.get("ofertas") or {}
    itens = []
    for it in caixa.get("itens", []):
        if it[0] == pid and it[1] == cid:
            if valor is None:
                continue
            it = [pid, cid, int(valor)]
        itens.append(it)
    caixa["itens"] = itens


def contrapropostas_restantes(G: Mundo, pid: int, cid: int) -> int:
    contras = (G.get("ofertas") or {}).get("contras") or {}
    return max(0, CONTRAS_POR_OFERTA - int(contras.get("%d:%d" % (pid, cid), 0)))


def contraproposta(G: Mundo, pid: int, cid: int, pedido: int) -> Tuple[str, str]:
    """Voce pede um valor pela oferta (pid, cid). Devolve (desfecho, recado),
    com desfecho em vendido / subiu / mantem / desistiu / invalida."""
    vivas = {(j["id"], cl["id"]): (j, cl, v) for j, cl, v in propostas_recebidas(G)}
    if (pid, cid) not in vivas:
        return "invalida", "Esta proposta nao vale mais."
    j, cl, oferta = vivas[(pid, cid)]
    pedido = int(pedido)
    if pedido <= oferta:
        ok, txt = aceitar_oferta(G, pid, cid, oferta)
        return ("vendido" if ok else "invalida"), txt
    if contrapropostas_restantes(G, pid, cid) <= 0:
        return "mantem", ("O %s ja deu a ultima palavra nesta semana: a oferta de %s por %s "
                          "esta de pe." % (cl["nome"], din(oferta), j["nome"]))
    contras = G["ofertas"].setdefault("contras", {})
    chave = "%d:%d" % (pid, cid)
    contras[chave] = int(contras.get(chave, 0)) + 1
    ultima = contrapropostas_restantes(G, pid, cid) <= 0
    # o maximo que ESTE clube paga: o que ele ve no jogador, com folga, e a verba dele
    limite = int(min(valor_para_comprador(G, j, cl) * 1.10,
                     verba_contratacao(G, cl, j["salario"])))
    limite = max(limite, oferta)
    if pedido <= limite:
        ok, txt = aceitar_oferta(G, pid, cid, pedido)
        if not ok:
            return "invalida", txt
        return "vendido", "O %s aceitou a contraproposta. %s" % (cl["nome"], txt)
    if pedido > limite * 1.5 or (ultima and pedido > limite * 1.25):
        _mudar_oferta(G, pid, cid, None)
        return "desistiu", ("O %s achou %s fora da realidade por %s e retirou a proposta."
                            % (cl["nome"], din(pedido), j["nome"]))
    if limite > oferta:
        nova = int(oferta + (limite - oferta) * rng.uniform(0.5, 0.9))
        nova = max(oferta + 1, min(nova, limite))
        _mudar_oferta(G, pid, cid, nova)
        return "subiu", ("O %s nao chega a %s, mas subiu a proposta por %s de %s para %s.%s"
                         % (cl["nome"], din(pedido), j["nome"], din(oferta), din(nova),
                            " E a ultima palavra dele nesta semana." if ultima else ""))
    return "mantem", ("O %s nao sobe: a oferta por %s continua %s."
                      % (cl["nome"], j["nome"], din(oferta)))


def leitura_oferta(oferta: int, pedido: int) -> Tuple[str, str]:
    """Semaforo para a interface: (recado, estado em ok/atencao/critico)."""
    if pedido <= 0:
        return "sem custo de passe", "ok"
    razao = oferta / float(pedido)
    if razao >= 0.97:
        return "deve ser aceita", "ok"
    if razao >= 0.85:
        return "perto do pedido, pode virar", "atencao"
    if razao >= 0.60:
        return "abaixo do pedido", "atencao"
    return "ofensiva: encerra a conversa", "critico"


# ----------------------------------------------------------------------------
# POTENCIAL E DESENVOLVIMENTO
#
# pot e atributo OCULTO: o motor usa o numero, a interface so mostra a leitura
# do olheiro (scout), que erra mais quanto pior for o CT e quanto mais novo o
# jogador. O numero cru nunca vai para a tela.
#
# O crescimento e mensal (a cada 4 semanas) e acumulado em ovr_frac, para que
# a temporada tenha progressao visivel em vez de um salto no fim do ano.
# ----------------------------------------------------------------------------

POT_MAX = 99
SEMANAS_POR_MES = 4

# Ritmo de evolucao. PISO_TREINO e quanto um jogador evolui SEM jogar: garoto
# de base treina e cresce quase como quem joga; jogador feito precisa de jogo.
EVOLUCAO_BASE = 0.80
PISO_BASE = 0.72
PISO_TREINO = ((21, 0.60), (25, 0.40), (99, 0.30))

# faixa de potencial por sorteio de talento: (peso, minimo, maximo)
FAIXAS_TALENTO: List[Tuple[float, int, int]] = [
    (0.0025, 88, 96),       # joia rara
    (0.055, 78, 88),        # promessa forte
    (0.220, 67, 77),        # bom aproveitamento
    (0.719, 50, 66),        # elenco comum
]


def sortear_potencial(ovr: int, idade: int, qualidade: float) -> int:
    """Teto de carreira. qualidade (0 a 1) vem da base do clube ou da reputacao.

    O sorteio e por faixa, nao por soma linear: joia tem que ser raridade,
    nao consequencia de ter CT nivel 10.
    """
    peso_extra = clamp(qualidade, 0.0, 1.0)
    # academia boa nao garante joia, muda a loteria: no nivel 1 a chance e
    # residual, no nivel 10 fica em torno de uma cria excepcional a cada 8.
    # (era 14/4 com deslocamento de 8: academia 10 dava joia 97-99 a cada 17
    # garotos e, com 260 clubes com base, o mundo enchia de 99)
    escala = (5.0, 2.5, 0.6, -0.50)
    pesos = []
    for i, (peso, _lo, _hi) in enumerate(FAIXAS_TALENTO):
        pesos.append(max(0.0005, peso * (1.0 + peso_extra * escala[i])))
    faixa = rng.choices(FAIXAS_TALENTO, weights=pesos)[0]
    # alem de mudar a loteria, a qualidade do clube desloca a faixa inteira:
    # a cria comum de um grande nasce com teto maior que a cria comum de um
    # pequeno. E isso que define o nivel de equilibrio de cada divisao.
    # o deslocamento sobe so o piso da faixa: nunca passa do teto dela
    desloca = int(round(peso_extra * 5))
    teto = rng.randint(min(faixa[1] + desloca, faixa[2]), faixa[2])
    # quem ja e velho nao tem para onde crescer
    if idade >= 28:
        teto = min(teto, ovr + rng.randint(0, 2))
    elif idade >= 24:
        teto = min(teto, ovr + rng.randint(2, 8))
    return int(clamp(max(teto, ovr), ovr, POT_MAX))


def fator_idade_evolucao(idade: int) -> float:
    """Velocidade de aprendizado. Pico ate 19, some aos 29."""
    if idade <= 19:
        return 1.00
    if idade <= 22:
        return 0.92
    if idade <= 25:
        return 0.70
    if idade <= 28:
        return 0.38
    if idade <= 30:
        return 0.15
    return 0.0


def declinio_mensal(idade: int) -> float:
    """Perda de OVR por mes na descida da carreira."""
    if idade <= 29:
        return 0.0
    if idade <= 31:
        return 0.07
    if idade <= 33:
        return 0.17
    if idade <= 35:
        return 0.30
    return 0.48


def taxa_evolucao(G: Mundo, j: Jogador) -> float:
    """Pontos de OVR por mes. Positivo cresce, negativo encolhe.

    Pesa, nesta ordem: distancia ate o teto, idade, minutagem no periodo,
    qualidade do CT e talento bruto. Sem minutagem o jovem ainda evolui, mas
    a um terco da velocidade de quem esta jogando.
    """
    clube = G["clubes"].get(j["clube"]) if j["clube"] else None
    ct = clube["ct"] if clube else 2
    idade = j["idade"]

    queda = declinio_mensal(idade)
    if queda > 0.0:
        med = clube["medico"] if clube else 3
        queda *= 1.18 - 0.03 * med          # departamento medico segura a queda
        queda *= freio_declinio(G, j)       # e o treino segura mais um pouco
        desgaste = 1.0 + clamp(j.get("j_mes", 0) / 6.0, 0.0, 0.5)
        return -queda * desgaste

    gap = j["pot"] - j["ovr"]
    if gap <= 0:
        return 0.0
    fator_idade = fator_idade_evolucao(idade)
    if fator_idade <= 0.0:
        return 0.0
    perto_do_teto = clamp(gap / 25.0, 0.0, 1.0)
    minutagem = clamp(j.get("j_mes", 0) / 4.0, 0.0, 1.2)
    talento = 0.70 + 0.30 * clamp((j["pot"] - 60) / 39.0, 0.0, 1.0)
    estrutura = 0.80 + 0.05 * ct
    fisico = 0.55 if j["lesao"] > 0 else 1.0

    piso = next(v for lim, v in PISO_TREINO if idade <= lim)
    if da_base(j):
        # garoto de base nao tem jogo: o treino e a unica fonte dele (era 1.0,
        # o ritmo de quem joga tudo; com foco na base passava de 20 por ano)
        minutagem, piso = 0.0, PISO_BASE
    ganho = EVOLUCAO_BASE * fator_idade * (piso + (1.0 - piso) * minutagem)
    ganho *= 0.40 + 0.60 * perto_do_teto
    ganho *= estrutura * talento * fisico
    ganho *= multiplicador_treino(G, j)
    return ganho


def aplicar_evolucao(G: Mundo, j: Jogador, meses: float = 1.0) -> int:
    """Acumula a fracao e converte em pontos inteiros. Devolve a variacao."""
    j["ovr_frac"] = float(j.get("ovr_frac", 0.0)) + taxa_evolucao(G, j) * meses
    mudou = 0
    while j["ovr_frac"] >= 1.0 and j["ovr"] < j["pot"]:
        j["ovr"] += 1
        j["ovr_frac"] -= 1.0
        mudou += 1
    while j["ovr_frac"] <= -1.0 and j["ovr"] > 20:
        j["ovr"] -= 1
        j["ovr_frac"] += 1.0
        mudou -= 1
    if j["ovr"] >= j["pot"]:
        j["ovr_frac"] = min(j["ovr_frac"], 0.0)
    if mudou:
        # salario de profissional e o do contrato: so muda ao contratar ou
        # renovar (decisao de 2026-09-25). Antes voltava a tabela a cada ponto
        # de overall e a renovacao durava ate o proximo treino.
        if da_base(j):
            j["salario"] = salario_devido(j)
        j["valor"] = valor_jogador(j)
    return mudou


def progresso_mensal(G: Mundo) -> List[Tuple[int, int]]:
    """Roda a cada 4 semanas. Devolve [(id do jogador, variacao)] do seu clube."""
    meu = G.get("clube")
    noticias: List[Tuple[int, int]] = []
    for j in G["jogadores"].values():
        # o teto e revisto ANTES de aplicar a evolucao: quem estourou a
        # previsao no mes ja cresce dentro do teto novo, sem esperar o ano
        estourou = estourar_teto(G, j)
        mudou = aplicar_evolucao(G, j)
        if j["clube"] is not None:
            j["obs"] = int(j.get("obs", 0)) + 1
        if (mudou or estourou) and (j["clube"] == meu or j.get("dono") == meu):
            noticias.append((j["id"], mudou))
        j["j_mes"] = 0
        j["g_mes"] = 0
        j["a_mes"] = 0
    return noticias


def scout(G: Mundo, j: Jogador, clube_id: Optional[int] = None) -> str:
    """Leitura do olheiro. Erra de proposito: pot e oculto.

    A margem encolhe com o nivel do CT, com a idade e com o tempo de casa.
    Mesma chave devolve sempre a mesma leitura, entao nao adianta reabrir a tela.
    """
    observador = G["clubes"].get(clube_id if clube_id is not None else G.get("clube"))
    olho = (observador["ct"] + observador["base"]) / 2.0 if observador else 3.0
    proprio = bool(observador and j["clube"] == observador["id"])
    margem = 14.0 - olho * 0.9
    if proprio:
        margem *= 0.55
        # cada mes de observacao aperta a leitura (EA FC, Football Manager):
        # o garoto de "72-88" vira "79-84" depois de um ano em casa
        margem /= 1.0 + 0.12 * int(j.get("obs", 0))
    if j["idade"] >= 26:
        margem *= 0.45                      # jogador feito nao tem misterio
    margem = max(2.0, margem)

    desvio = (_ruido("scout-%d-%d" % (j["id"], observador["id"] if observador else 0), -1.0, 1.0)) * margem
    visto = clamp(j["pot"] + desvio, j["ovr"], POT_MAX)
    lo = int(clamp(visto - margem * 0.6, j["ovr"], POT_MAX))
    hi = int(clamp(visto + margem * 0.6, lo + 1, POT_MAX))
    if hi - lo <= 3:
        # so o numero: quem mostra ja escreve "teto" antes (dava "teto teto ~75")
        return "~%d" % int((lo + hi) / 2)
    return "%d-%d" % (lo, hi)


def rotulo_scout(G: Mundo, j: Jogador, clube_id: Optional[int] = None) -> str:
    """Versao em palavras, para a ficha."""
    faixa = scout(G, j, clube_id)
    numeros = [int(n) for n in re.findall(r"\d+", faixa)]
    centro = sum(numeros) / len(numeros)
    folga = centro - j["ovr"]
    if j["idade"] >= 30:
        return "ja deu o que tinha que dar"
    if folga < 3:
        return "chegou no limite dele"
    if centro >= 86:
        return "pode virar craque de verdade"
    if centro >= 76:
        return "promessa forte, titular de time grande"
    if centro >= 66:
        return "deve virar titular de Serie A ou B"
    if folga >= 10:
        return "cru, mas tem margem para crescer"
    return "jogador de elenco"


# ----------------------------------------------------------------------------
# TREINO
#
# O clube escolhe um regime por semana e, dentro dele, aponta alguns nomes para
# trabalho individual. Todo regime tem preco: quem evolui rapido chega cansado
# e se machuca mais; quem poupa o elenco nao desenvolve ninguem.
#
# Os numeros entram em tres lugares, e so neles: taxa_evolucao (quanto cresce),
# recuperacao (quanto de fisico volta na semana) e o sorteio de lesao em
# simular. Regra da casa mantida: a interface escolhe, o motor resolve.
# ----------------------------------------------------------------------------

REGIME_PADRAO = "Equilibrado"

REGIMES_TREINO: Dict[str, Dict[str, Any]] = {
    "Equilibrado": dict(evo=1.00, jovem=1.00, veterano=1.00, cond=0, lesao=1.00,
                        desc="ritmo normal, sem bonus e sem preco"),
    "Intensivo": dict(evo=1.35, jovem=1.10, veterano=0.95, cond=-7, lesao=1.45,
                      desc="desenvolve rapido, mas o time chega cansado e machuca mais"),
    "Leve": dict(evo=0.75, jovem=0.95, veterano=1.10, cond=+7, lesao=0.65,
                 desc="poupa o elenco: pouca evolucao, mais fisico e menos lesao"),
    "Foco na base": dict(evo=0.95, jovem=1.60, veterano=0.78, cond=-2, lesao=1.05,
                         desc="o CT trabalha para os moleques; quem passou dos 26 estagna"),
    "Foco tecnico": dict(evo=1.18, jovem=1.12, veterano=1.02, cond=-3, lesao=1.10,
                         desc="bola no pe: evolucao acima da media, fisico um pouco abaixo"),
    "Foco fisico": dict(evo=0.88, jovem=0.92, veterano=1.28, cond=+11, lesao=0.72,
                        desc="ninguem evolui muito, mas o elenco inteiro chega no fim do ano"),
}

IDADE_JOVEM = 21          # ate aqui o jovem do regime
IDADE_VETERANO = 27       # daqui em diante o veterano do regime


def regime_de(c: Optional[Clube]) -> Dict[str, Any]:
    """O regime do clube, com o padrao valendo para save antigo e clube da IA."""
    if not c:
        return REGIMES_TREINO[REGIME_PADRAO]
    return REGIMES_TREINO.get(c.get("treino") or REGIME_PADRAO,
                              REGIMES_TREINO[REGIME_PADRAO])


def definir_regime(G: Mundo, c: Clube, nome: str) -> Tuple[bool, str]:
    if nome not in REGIMES_TREINO:
        return False, "Regime de treino desconhecido."
    c["treino"] = nome
    return True, "Treino da semana: %s - %s." % (nome, REGIMES_TREINO[nome]["desc"])


def vagas_treino(c: Clube) -> int:
    """Quantos nomes o CT sustenta em trabalho individual. Nivel 1 da 2, nivel 10 da 7."""
    return 2 + int(c.get("ct", 3)) // 2


def foco_treino(G: Mundo, c: Clube) -> List[int]:
    """Lista limpa dos que estao em treino individual: quem saiu do clube cai fora."""
    dentro = set(c["elenco"]) | set(c.get("base_elenco", []))
    atual = [p for p in c.get("treino_foco", []) if p in dentro]
    if atual != c.get("treino_foco", []):
        c["treino_foco"] = atual
    return atual


def custo_treino(c: Clube) -> int:
    """Custo semanal do trabalho individual. Entra em custo_estrutura."""
    quantos = len(c.get("treino_foco") or [])
    return quantos * (26_000 + 3_000 * int(c.get("ct", 3)))


def alternar_foco(G: Mundo, c: Clube, pid: int) -> Tuple[bool, str]:
    """Liga ou desliga o trabalho individual de um jogador."""
    j = G["jogadores"].get(pid)
    if not j:
        return False, "Jogador nao encontrado."
    foco = foco_treino(G, c)
    if pid in foco:
        foco.remove(pid)
        c["treino_foco"] = foco
        return True, "%s saiu do treino individual." % j["nome"]
    if j.get("dono"):
        return False, "%s esta emprestado: o dono manda no desenvolvimento dele." % j["nome"]
    if len(foco) >= vagas_treino(c):
        return False, ("O CT nivel %d sustenta %s em treino individual. "
                       "Tire alguem antes, ou melhore o CT."
                       % (c.get("ct", 3), plural(vagas_treino(c), "nome")))
    foco.append(pid)
    c["treino_foco"] = foco
    return True, ("%s entrou no treino individual: evolui 50%% mais rapido, e custa %s por semana."
                  % (j["nome"], din(26_000 + 3_000 * int(c.get("ct", 3)))))


def em_foco(G: Mundo, j: Jogador) -> bool:
    c = G["clubes"].get(j["clube"]) if j["clube"] else None
    return bool(c and j["id"] in (c.get("treino_foco") or []))


def multiplicador_treino(G: Mundo, j: Jogador) -> float:
    """Quanto o treino acelera (ou freia) a evolucao deste jogador."""
    c = G["clubes"].get(j["clube"]) if j["clube"] else None
    reg = regime_de(c)
    m = float(reg["evo"])
    if j["idade"] <= IDADE_JOVEM:
        m *= float(reg["jovem"])
    elif j["idade"] >= IDADE_VETERANO:
        m *= float(reg["veterano"])
    if em_foco(G, j):
        m *= 1.50
    return m


def freio_declinio(G: Mundo, j: Jogador) -> float:
    """Quanto o treino segura a queda de quem ja passou do pico."""
    c = G["clubes"].get(j["clube"]) if j["clube"] else None
    freio = 1.0 / max(0.5, float(regime_de(c)["veterano"]))
    if em_foco(G, j):
        freio *= 0.78
    return freio


def risco_lesao_treino(G: Mundo, c: Optional[Clube]) -> float:
    return float(regime_de(c)["lesao"])


# ----------------------------------------------------------------------------
# CATEGORIAS DE BASE
#
# Antes a base era um numero no clube: no fim do ano cuspia jogador direto no
# profissional e pronto. Agora existe elenco de base de verdade - garotos de
# 15 a 19 anos que treinam, evoluem, aparecem na tela e sobem quando VOCE
# manda. Eles nao entram em campo nem no mercado enquanto forem da base.
#
# Marca no jogador: categoria = "base" ou "pro". Tudo que varre o mundo
# (mercado, escalacao, fim de contrato) tem que respeitar isso.
# ----------------------------------------------------------------------------

BOLSA_BASE = 0.22        # fatia do salario profissional que o garoto custa
IDADE_BASE_MIN = 15
IDADE_BASE_MAX = 19      # aos 20 ele sobe ou e liberado


def da_base(j: Jogador) -> bool:
    return j.get("categoria") == "base"


def salario_devido(j: Jogador) -> int:
    """Quanto o jogador custa hoje. Garoto de base recebe bolsa, nao salario."""
    base = salario_de(j["ovr"])
    return max(1, int(base * BOLSA_BASE)) if da_base(j) else base


def vagas_base(c: Clube) -> int:
    """Tamanho da academia. Nivel 1 sustenta 8 garotos, nivel 10 sustenta 26."""
    return 6 + int(c.get("base", 1)) * 2


def elenco_base(G: Mundo, c: Clube) -> List[Jogador]:
    """Os garotos do clube, do mais promissor para o menos."""
    out = []
    for pid in list(c.get("base_elenco", [])):
        j = G["jogadores"].get(pid)
        if j and da_base(j) and j["clube"] == c["id"]:
            out.append(j)
        else:
            c["base_elenco"] = [p for p in c["base_elenco"] if p != pid]
    out.sort(key=lambda j: (-j["pot"], -j["ovr"], j["idade"]))
    return out


def custo_base(G: Mundo, c: Clube) -> int:
    """Bolsa semanal de toda a base. Entra na folha, porque e folha."""
    total = sum(salario_devido(j) for j in elenco_base(G, c))
    return int(total / 4.0)


def gerar_cria(G: Mundo, c: Clube, usados: set, idade: Optional[int] = None) -> Jogador:
    """Nasce um garoto na academia do clube."""
    nivel = 26 + c["base"] * 2.0 + c["reputacao"] * 0.16
    if idade is None:
        idade = rng.randint(IDADE_BASE_MIN, 17)
    j = novo_jogador(G, rng.choice(POS), nivel, usados, idade=idade)
    qualidade = clamp(c["base"] / 10.0 * 0.75 + c["reputacao"] / 100.0 * 0.25, 0.0, 1.0)
    j["pot"] = sortear_potencial(j["ovr"], j["idade"], qualidade)
    j["categoria"] = "base"
    j["clube"] = c["id"]
    j["contrato"] = 3
    j["salario"] = salario_devido(j)
    j["valor"] = valor_jogador(j)
    j["ovr_ini"] = j["ovr"]
    c.setdefault("base_elenco", []).append(j["id"])
    return j


def base_gera(G, c, usados):
    """Safra anual da academia. Devolve os garotos que entraram na base.

    Assinatura mantida: quem chamava isso no fim de temporada continua
    chamando. O que mudou e o destino - antes ia direto ao profissional.
    """
    qtd = 1 + (1 if c["base"] >= 4 else 0) + (1 if c["base"] >= 8 else 0)
    if c["base"] >= 6 and rng.random() < 0.45:
        qtd += 1
    # academia meio vazia puxa uma safra maior: sem isto, clube que promove
    # muito ficava com dois garotos na base e a tela vivia deserta
    ocupacao = len(c.get("base_elenco", [])) / float(max(1, vagas_base(c)))
    if ocupacao < 0.55:
        qtd += 2
    livres = vagas_base(c) - len(c.get("base_elenco", []))
    novos = []
    for _ in range(max(0, min(qtd, livres))):
        novos.append(gerar_cria(G, c, usados))
    return novos


def pronto_para_subir(G: Mundo, c: Clube, j: Jogador) -> bool:
    """Se ele ja tem nivel de profissional. Serve ao aviso e a IA."""
    if j["idade"] >= 18:
        return j["ovr"] >= media_elenco(G, c) - 8
    return j["ovr"] >= media_elenco(G, c) - 4


def promover_da_base(G: Mundo, pid: int, anos: int = 3) -> Tuple[bool, str]:
    """Sobe o garoto ao profissional, com contrato e salario de gente grande."""
    j = G["jogadores"].get(pid)
    if not j or not da_base(j):
        return False, "Este jogador nao esta na base."
    c = G["clubes"][j["clube"]]
    if elenco_cheio(G, c):
        return False, "%s nao sobe agora. %s" % (j["nome"], recado_elenco_cheio(c))
    c["base_elenco"] = [p for p in c.get("base_elenco", []) if p != pid]
    c["elenco"].append(pid)
    j["categoria"] = "pro"
    j["contrato"] = int(clamp(anos, 1, 5))
    j["salario"] = salario_devido(j)
    j["desde"] = G["temporada"] * 100 + G["semana"]
    j["entros"] = ENTROS_VOLTA
    mexer_moral(G, j, 14, "subiu da base ao profissional")
    c.setdefault("revelados", []).append({"id": pid, "nome": j["nome"], "pos": j["pos"],
                                         "temporada": int(G["temporada"]), "ovr": int(j["ovr"])})
    del c["revelados"][:-30]
    if c["id"] == G.get("clube"):
        noticia(G, "%s (%d anos, %s) subiu da base ao profissional."
                % (j["nome"], j["idade"], j["pos"]))
    return True, ("%s subiu ao profissional: %s de contrato, %s por mes."
                  % (j["nome"], plural(j["contrato"], "ano"), din(j["salario"])))


def dispensar_da_base(G: Mundo, pid: int) -> Tuple[bool, str]:
    """Libera o garoto. Sem multa: contrato de base nao tem rescisao."""
    j = G["jogadores"].get(pid)
    if not j or not da_base(j):
        return False, "Este jogador nao esta na base."
    c = G["clubes"][j["clube"]]
    c["base_elenco"] = [p for p in c.get("base_elenco", []) if p != pid]
    nome = j["nome"]
    del G["jogadores"][pid]
    return True, "%s foi liberado da base." % nome


# ----------------------------------------------------------------------------
# PENEIRA
#
# Brasfoot tem peneira, Hattrick chama o olheiro por regiao, EA FC manda
# olheiro para um pais: aqui o tecnico escolhe onde procurar e, se quiser, que
# posicao. A cada 4 semanas chegam candidatos; cada um espera 4 semanas por um
# sim (entra na base, se houver vaga) ou um nao. A peneira custa por semana
# enquanto estiver ligada. So o clube do jogador usa: a IA segue com a safra.
# ----------------------------------------------------------------------------

# talento: multiplica a qualidade do sorteio de potencial; vies: posicoes que a
# regiao revela mais; custo: por semana
REGIOES_PENEIRA = {
    "sp": {"nome": "Sao Paulo", "talento": 1.00, "vies": ["MEI", "ATA"], "custo": 90_000},
    "rj": {"nome": "Rio de Janeiro", "talento": 0.95, "vies": ["ATA", "LAT"], "custo": 80_000},
    "sul": {"nome": "Sul", "talento": 0.92, "vies": ["ZAG", "GOL", "VOL"], "custo": 70_000},
    "ne": {"nome": "Nordeste", "talento": 0.88, "vies": ["ATA", "MEI"], "custo": 50_000},
    "nco": {"nome": "Norte e Centro-Oeste", "talento": 0.80, "vies": ["LAT", "VOL"], "custo": 35_000},
    "sula": {"nome": "America do Sul", "talento": 1.05, "vies": ["VOL", "ZAG", "ATA"], "custo": 140_000},
}
PENEIRA_A_CADA = 4          # semanas entre levas de candidatos
CANDIDATO_VALE = 4          # semanas que um candidato espera resposta


def peneira(c: Clube) -> Optional[Dict[str, Any]]:
    return c.get("peneira") or None


def ligar_peneira(G: Mundo, c: Clube, regiao: str, foco: Optional[str] = None) -> Tuple[bool, str]:
    if regiao not in REGIOES_PENEIRA:
        return False, "Regiao de peneira desconhecida."
    if foco and foco not in POS:
        return False, "Posicao desconhecida."
    r = REGIOES_PENEIRA[regiao]
    c["peneira"] = {"regiao": regiao, "foco": foco or None, "semanas": 0}
    return True, "Peneira ligada no %s%s: %s por semana, candidatos a cada %d semanas." % (
        r["nome"], " (%s)" % foco if foco else "", din(r["custo"]), PENEIRA_A_CADA)


def desligar_peneira(G: Mundo, c: Clube) -> Tuple[bool, str]:
    if not c.get("peneira"):
        return False, "Nao ha peneira ligada."
    c["peneira"] = None
    return True, "Peneira desligada."


def candidatos_base(G: Mundo, c: Clube) -> List[Dict[str, Any]]:
    """Os candidatos ainda de pe (os vencidos saem aqui)."""
    agora = semana_absoluta(G)
    vivos = [k for k in c.get("base_candidatos", []) if k.get("vence", 0) > agora]
    c["base_candidatos"] = vivos
    return vivos


def _novo_candidato(G: Mundo, c: Clube, regiao: str, foco: Optional[str]) -> Dict[str, Any]:
    r = REGIOES_PENEIRA[regiao]
    if foco:
        pos = foco
    elif rng.random() < 0.55:
        pos = rng.choice(r["vies"])
    else:
        pos = rng.choice(POS)
    idade = rng.randint(IDADE_BASE_MIN, 17)
    nivel = 26 + c["base"] * 2.0 + c["reputacao"] * 0.16
    ovr = int(clamp(nivel + rng.uniform(-4, 4) - (18 - idade) * 2, 25, 70))
    qualidade = clamp((c["base"] / 10.0 * 0.6 + c["reputacao"] / 100.0 * 0.4) * r["talento"], 0.0, 1.0)
    G["seq_cand"] = int(G.get("seq_cand", 0)) + 1
    return {"cid": G["seq_cand"], "nome": gerar_nome({j["nome"] for j in G["jogadores"].values()}), "pos": pos, "idade": idade,
            "ovr": ovr, "pot": sortear_potencial(ovr, idade, qualidade),
            "regiao": r["nome"], "temporada": int(G["temporada"]),
            "vence": semana_absoluta(G) + CANDIDATO_VALE}


def rodar_peneira(G: Mundo) -> List[Dict[str, Any]]:
    """Semanal: cobra a peneira do meu clube e, a cada 4 semanas, traz candidatos."""
    c = G["clubes"].get(G.get("clube"))
    pen = peneira(c) if c else None
    if not pen:
        return []
    r = REGIOES_PENEIRA[pen["regiao"]]
    lancar(G, c, -r["custo"], "peneira")
    pen["semanas"] = int(pen.get("semanas", 0)) + 1
    if pen["semanas"] % PENEIRA_A_CADA:
        return []
    novos = [_novo_candidato(G, c, pen["regiao"], pen.get("foco"))
             for _ in range(1 + (1 if rng.random() < 0.45 + 0.03 * c["base"] else 0))]
    c.setdefault("base_candidatos", []).extend(novos)
    noticia(G, "Peneira no %s: %s para avaliar na tela da Base." % (r["nome"], plural(len(novos), "garoto")))
    return novos


def aceitar_candidato(G: Mundo, c: Clube, cid: int) -> Tuple[bool, str]:
    k = next((k for k in candidatos_base(G, c) if k["cid"] == cid), None)
    if not k:
        return False, "Esse candidato nao esta mais esperando."
    if len(c.get("base_elenco", [])) >= vagas_base(c):
        return False, "A base esta cheia (%d vagas): libere alguem ou amplie a academia." % vagas_base(c)
    usados = {j["nome"] for j in G["jogadores"].values()}
    j = novo_jogador(G, k["pos"], k["ovr"], usados, idade=k["idade"])
    j["nome"] = k["nome"] if k["nome"] not in usados else j["nome"]
    j["ovr"], j["pot"] = k["ovr"], max(k["ovr"], k["pot"])
    j["categoria"] = "base"
    j["clube"] = c["id"]
    j["contrato"] = 3
    j["salario"] = salario_devido(j)
    j["valor"] = valor_jogador(j)
    j["ovr_ini"] = j["ovr"]
    c.setdefault("base_elenco", []).append(j["id"])
    c["base_candidatos"] = [x for x in c["base_candidatos"] if x["cid"] != cid]
    return True, "%s (%d anos, %s) entrou na base." % (j["nome"], j["idade"], j["pos"])


def recusar_candidato(G: Mundo, c: Clube, cid: int) -> Tuple[bool, str]:
    antes = len(c.get("base_candidatos", []))
    c["base_candidatos"] = [x for x in c.get("base_candidatos", []) if x["cid"] != cid]
    if len(c["base_candidatos"]) == antes:
        return False, "Esse candidato nao esta mais esperando."
    return True, "Candidato dispensado."


def faixa_candidato(G: Mundo, c: Clube, k: Dict[str, Any]) -> str:
    """Leitura do candidato: larga, porque ele so foi visto na peneira."""
    olho = (c["ct"] + c["base"]) / 2.0
    margem = max(4.0, 14.0 - olho * 0.9)
    desvio = _ruido("cand-%d" % k["cid"], -1.0, 1.0) * margem
    visto = clamp(k["pot"] + desvio, k["ovr"], POT_MAX)
    lo = int(clamp(visto - margem * 0.6, k["ovr"], POT_MAX))
    hi = int(clamp(visto + margem * 0.6, lo + 1, POT_MAX))
    return "%d-%d" % (lo, hi)


def promover_base_ia(G: Mundo, c: Clube) -> None:
    """Clube da IA resolve a base dele sozinho, com o mesmo critorio de nivel."""
    for j in elenco_base(G, c):
        if len(c["elenco"]) >= LIMITE_ELENCO - 2:
            return
        if j["idade"] >= 18 and pronto_para_subir(G, c, j):
            promover_da_base(G, j["id"], anos=rng.randint(2, 4))


def resolver_base(G: Mundo, c: Clube) -> Tuple[List[str], List[str]]:
    """Virada de ano: quem passou da idade de base sobe ou sai.

    Devolve (subiram, sairam) em nomes, para o resumo da temporada.
    """
    subiram, sairam = [], []
    for j in elenco_base(G, c):
        if j["idade"] <= IDADE_BASE_MAX:
            continue
        if pronto_para_subir(G, c, j) and not elenco_cheio(G, c):
            ok, _ = promover_da_base(G, j["id"], anos=rng.randint(2, 4))
            if ok:
                subiram.append(j["nome"])
                continue
        nome = j["nome"]
        if dispensar_da_base(G, j["id"])[0]:
            sairam.append(nome)
    return subiram, sairam


# ----------------------------------------------------------------------------
# POTENCIAL DINAMICO
#
# O teto deixou de ser sentenca. Ele nasce como PREVISAO e a previsao se
# corrige com o que aconteceu em campo: quem rende acima do que o teto dizia
# ganha teto novo, quem nunca chega perto dele tem a previsao cortada.
#
# Sem isso um jogador de alto nivel sorteado com teto baixo congelava para
# sempre no dia em que o overall encostava no teto, ainda que fosse titular
# absoluto e convocado.
#
# Duas escalas:
#   estourar_teto()    - mensal, curto, so para quem bateu no teto jogando;
#   revisar_potencial() - anual, olha a temporada inteira do jogador.
# ----------------------------------------------------------------------------

# producao esperada por jogo de um titular medio da posicao
G_ESPERADO = {"GOL": 0.00, "ZAG": 0.045, "LAT": 0.035, "VOL": 0.055, "MEI": 0.16, "ATA": 0.36}
A_ESPERADO = {"GOL": 0.00, "ZAG": 0.025, "LAT": 0.110, "VOL": 0.070, "MEI": 0.23, "ATA": 0.16}
# o quanto gol e assistencia contam na nota da posicao: goleiro se mede por
# presenca, atacante por numero.
PESO_PRODUCAO = {"GOL": 0.10, "ZAG": 0.22, "LAT": 0.35, "VOL": 0.42, "MEI": 0.60, "ATA": 0.72}
PESO_DIVISAO = {"A": 1.00, "B": 0.84, "C": 0.68, "D": 0.54, "EX": 0.92}
PESO_DIVISAO.update({k: v["peso"] for k, v in PERFIL_LIGA_EXT.items()})


def desempenho_temporada(G: Mundo, j: Jogador) -> float:
    """Nota de 0 a 1 do ano do jogador: quanto jogou, em que nivel e o que produziu."""
    if da_base(j):
        # garoto de base nao tem jogo: o sinal dele e o quanto cresceu no ano
        return clamp((j["ovr"] - int(j.get("ovr_ini", j["ovr"]))) / 6.0, 0.0, 1.0)
    jogos = int(j.get("j", 0))
    if jogos <= 0:
        return 0.0
    clube = G["clubes"].get(j["clube"]) if j["clube"] else None
    divisao = PESO_DIVISAO.get(clube["divisao"], 0.7) if clube else 0.6
    uso = clamp(jogos / 30.0, 0.0, 1.0)
    esperado = ((G_ESPERADO[j["pos"]] + 0.6 * A_ESPERADO[j["pos"]])
                * clamp(j["ovr"] / 70.0, 0.55, 1.65))
    produziu = (j.get("g", 0) + 0.6 * j.get("a", 0)) / float(jogos)
    prod = clamp(produziu / esperado, 0.0, 2.0) / 2.0 if esperado > 0.01 else uso
    peso = PESO_PRODUCAO[j["pos"]]
    nota = (1.0 - peso) * uso + peso * prod
    return clamp(nota * (0.70 + 0.30 * divisao), 0.0, 1.0)


# Ate onde a revisao consegue levar o teto em cada palco. Arrebentar a Serie D
# prova que o jogador da conta da Serie D; para o teto passar disso ele precisa
# render num palco maior. Sem esse limite o mundo inteiro caminhava para 99.
TETO_CREDIVEL = {"A": 97, "B": 88, "C": 80, "D": 74, "EX": 94}
# nenhuma revisao ou estouro leva o teto alem disto: 92+ so nasce, nao se fabrica
TETO_REVISAO = 91
TETO_CREDIVEL.update({k: v["teto"] for k, v in PERFIL_LIGA_EXT.items()})


def teto_maximo(G: Mundo, j: Jogador) -> int:
    """Teto maximo que a revisao pode alcancar para este jogador, hoje.

    Tres coisas o definem, e a maior delas vence:
      a divisao onde ele joga, porque o palco e que da a prova;
      a reputacao do clube, porque grande caido de divisao ainda e vitrine;
      o que ele JA e, porque o campo nao mente - quem chegou a 76 na Serie D
      nao pode ter o teto travado em 74 so pela sigla da competicao.
    """
    c = G["clubes"].get(j["clube"]) if j["clube"] else None
    if not c:
        return int(min(TETO_REVISAO, max(TETO_CREDIVEL["D"], j["ovr"])))
    limite = max(TETO_CREDIVEL.get(c["divisao"], 74),
                 int(clamp(58 + c["reputacao"] * 0.42, 58, 97)))
    # quem ja passou do limite fica onde esta (o campo nao mente), mas nao
    # ganha folga: o "+2" antigo era uma catraca - bateu no teto, o teto subia,
    # e o mundo caminhava para 99 mes a mes
    return int(min(TETO_REVISAO, max(limite, j["ovr"])))


def chance_subida(pot: int) -> float:
    """Rendimento decrescente: cada degrau la em cima custa muito mais.

    Subir de 65 para 66 e barato porque previsao errada e comum nessa faixa.
    Subir de 92 para 93 tem que ser raro, senao o teto perde o sentido.
    """
    if pot < 70:
        return 1.00
    if pot < 78:
        return 0.80
    if pot < 85:
        return 0.52
    if pot < 88:
        return 0.22
    if pot < 91:
        return 0.08
    return 0.03


def estourar_teto(G: Mundo, j: Jogador) -> int:
    """Mensal: quem bateu no teto e continua rendendo ganha um degrau.

    E o remedio direto do jogador de alto nivel com teto baixo: em vez de
    congelar no mes em que ovr encosta em pot, ele segue subindo devagar.
    """
    if da_base(j) or j["ovr"] < j["pot"] or j["pot"] >= POT_MAX:
        return 0
    if j["idade"] > 27 or int(j.get("j_mes", 0)) < 3:
        return 0
    c = G["clubes"].get(j["clube"]) if j["clube"] else None
    if not c or j["pot"] >= teto_maximo(G, j):
        return 0
    chance = 0.045 + 0.008 * c.get("ct", 3)
    if j["idade"] <= 21:
        chance += 0.05
    if int(j.get("g_mes", 0)) + int(j.get("a_mes", 0)) >= 2:
        chance += 0.05
    if em_foco(G, j):
        chance += 0.04
    if rng.random() >= chance * chance_subida(j["pot"]):
        return 0
    j["pot"] = int(min(POT_MAX, j["pot"] + 1))
    j["pot_rev"] = int(j.get("pot_rev", 0)) + 1
    j["valor"] = valor_jogador(j)
    return 1


def revisar_potencial(G: Mundo, j: Jogador) -> int:
    """Corrige o teto com base na temporada inteira. Devolve a variacao."""
    if da_base(j):
        return 0                # sem jogo nao ha prova: a base nao se revisa
    nota = desempenho_temporada(G, j)
    gap = j["pot"] - j["ovr"]
    idade = j["idade"]
    delta = 0
    if idade <= 26 and nota >= 0.62 and gap <= 4:
        # rendeu e ja nao tem para onde crescer: a previsao estava curta
        delta = 1 + (1 if nota >= 0.78 else 0) + (1 if nota >= 0.90 and idade <= 22 else 0)
    elif idade <= 23 and nota >= 0.75 and gap <= 9:
        delta = 1
    elif gap >= 10 and idade >= 24 and nota <= 0.33:
        delta = -2 if idade >= 26 else -1
    elif gap >= 6 and idade >= 28:
        delta = -2
    if delta > 0:
        folga = teto_maximo(G, j) - j["pot"]
        if folga <= 0 or rng.random() > chance_subida(j["pot"]):
            return 0
        delta = min(delta, folga)
    if not delta:
        return 0
    novo = int(clamp(j["pot"] + delta, max(j["ovr"], 30), POT_MAX))
    delta = novo - j["pot"]
    if not delta:
        return 0
    j["pot"] = novo
    j["pot_rev"] = int(j.get("pot_rev", 0)) + delta
    j["valor"] = valor_jogador(j)
    return delta


def revisar_potenciais(G: Mundo) -> List[Tuple[int, int]]:
    """Fim de temporada: revisa o mundo. Devolve [(id, variacao)] do meu clube."""
    meu = G.get("clube")
    mudancas: List[Tuple[int, int]] = []
    for j in list(G["jogadores"].values()):
        d = revisar_potencial(G, j)
        if d and (j["clube"] == meu or j.get("dono") == meu):
            mudancas.append((j["id"], d))
    mudancas.sort(key=lambda t: -abs(t[1]))
    return mudancas


def leitura_teto(j: Jogador) -> str:
    """Como a ficha conta que o teto foi revisado."""
    rev = int(j.get("pot_rev", 0))
    if rev >= 3:
        return "estourou a previsao: teto revisado %d pontos para cima" % rev
    if rev > 0:
        return "rendeu acima do previsto: teto subiu %s" % plural(rev, "ponto")
    if rev <= -3:
        return "a previsao nao se cumpriu: teto cortado %d pontos" % -rev
    if rev < 0:
        return "teto cortado %s pelo que rendeu" % plural(-rev, "ponto")
    return ""


# ----------------------------------------------------------------------------
# DESENVOLVIMENTO, FIM DE TEMPORADA
# ----------------------------------------------------------------------------

def evoluir_jogadores(G: Mundo) -> None:
    """Virada de ano: envelhece, liquida o residuo do ano e aposenta.

    O grosso do crescimento ja aconteceu mes a mes em progresso_mensal(). Aqui
    fica so o que sobra: a ferias/pre-temporada de quem nao jogou e o efeito de
    ficar um ano mais velho.
    """
    aposentados: List[int] = []
    for j in list(G["jogadores"].values()):
        j["idade"] += 1
        aplicar_evolucao(G, j, meses=1.5)      # janela sem jogos, ritmo reduzido
        if da_base(j):
            j["salario"] = salario_devido(j)      # bolsa; o profissional tem contrato
        j["valor"] = valor_jogador(j)
        j["j"] = j["g"] = j["a"] = j["ca"] = j["cv"] = 0
        j["nota_soma"], j["nota_j"] = 0.0, 0
        j["j_mes"] = 0
        j["amarelos"] = 0
        # ferias e pre-temporada: sem isto o elenco comecava o ano novo exatamente
        # como terminou o anterior (condicao 24, moral 12, lesao pela metade) e a
        # espiral de moral atravessava temporadas.
        j["cond"] = 100
        j["forma"] = clamp(60 + rng.randint(0, 12), 5, 100)
        antes = j["moral"]
        j["moral"] = clamp(int(j["moral"] + 0.6 * (65 - j["moral"])), 5, 100)
        anotar_moral(G, j, j["moral"] - antes, "ferias e pre-temporada")
        j["lesao"] = 0
        j["amar"] = {k: 0 for k in COMPETICOES}
        j["susp"] = {k: 0 for k in COMPETICOES}
        j["suspensao"] = 0
        j["contrato"] -= 1
        if j["idade"] >= 33:
            # quanto mais velho e mais caido de rendimento, maior a chance de parar
            chance = (j["idade"] - 32) * 0.16 + clamp((60 - j["ovr"]) / 40.0, 0.0, 0.45)
            if j["idade"] >= 40 or rng.random() < chance:
                aposentados.append(j["id"])
    for pid in aposentados:
        j = G["jogadores"][pid]
        c = G["clubes"].get(j["clube"]) if j["clube"] else None
        if c and pid in c["elenco"]:
            c["elenco"].remove(pid)
            if pid in c.get("escalacao", []):
                c["escalacao"].remove(pid)
        if pid in G["livres"]:
            G["livres"].remove(pid)
        del G["jogadores"][pid]


def fim_de_contrato(G):
    """Contratos zerados: jogador vira agente livre (exceto do clube do usuario,
    que decide na renovacao)."""
    for j in list(G["jogadores"].values()):
        if j["contrato"] > 0 or j["clube"] is None or da_base(j):
            continue                    # contrato de base se resolve em resolver_base
        c = G["clubes"][j["clube"]]
        if c["id"] == G["clube"]:
            continue
        if c["divisao"] == "EX":
            j["contrato"] = rng.randint(1, 3)
            j["salario"] = salario_de(j["ovr"])
            continue
        novo = salario_de(j["ovr"])
        # renova so se o aumento cabe na folha: sem isto quem evoluiu era
        # renovado mais caro todo ano e a folha das ligas de fora passava da receita
        if rng.random() < 0.88 and (novo <= j["salario"] or cabe_na_folha(G, c, novo - j["salario"])):
            j["contrato"] = rng.randint(1, 4)
            j["salario"] = novo                    # renovou: salario de mercado
        else:
            c["elenco"].remove(j["id"])
            if j["id"] in c.get("escalacao", []):
                c["escalacao"].remove(j["id"])
            j["clube"] = None
            j["listado"] = 0
            j["emp_listado"] = 0
            G["livres"].append(j["id"])


LIVRES_POR_SEMANA = 10
# cada clube da IA assina no maximo um livre por semana: sem isto o clube
# rico do topo da fila levava os melhores livres todos de uma vez
LIVRES_POR_CLUBE = 1


def contratar_livres_ia(G):
    """Semanal: os melhores agentes livres vao para clubes onde seriam titulares
    e que pagam o salario. Antes a IA pegava livre ao acaso, so com elenco
    abaixo de 24, e a limpeza de fim de ano guardava justamente os melhores:
    a fila de craques sem clube so crescia."""
    presos = presos_em_acerto(G)
    livres = sorted((G["jogadores"][p] for p in G["livres"]
                     if p in G["jogadores"] and p not in presos),
                    key=lambda j: -j["ovr"])
    agora = semana_absoluta(G)

    def pode(c):
        feito = c.get("livres_sem") or [None, 0]
        return len(c["elenco"]) < 30 and not (feito[0] == agora and feito[1] >= LIVRES_POR_CLUBE)

    clubes = [c for c in G["clubes"].values()
              if c["divisao"] != "EX" and c["id"] != G.get("clube") and pode(c)]
    feitos = 0
    for j in livres[:40]:
        if feitos >= LIVRES_POR_SEMANA:
            break
        cands = []
        for c in clubes:
            titulares = sorted((G["jogadores"][p]["ovr"] for p in c["elenco"]
                                if G["jogadores"][p]["pos"] == j["pos"]), reverse=True)
            vagas = max(1, ELENCO_PADRAO[j["pos"]] // 2)
            pior_titular = titulares[vagas - 1] if len(titulares) >= vagas else 0
            if j["ovr"] <= pior_titular:
                continue
            pedida = exigencia_salarial(G, j, c)
            if verba_contratacao(G, c, pedida) <= 0 or not cabe_na_folha(G, c, pedida):
                continue
            cands.append(c)
        if not cands:
            continue
        cands.sort(key=lambda c: -c["reputacao"])
        c = cands[0] if rng.random() < 0.6 else rng.choice(cands[:5])
        j["salario"] = exigencia_salarial(G, j, c)
        transferir(G, j["id"], c["id"], 0)
        j["contrato"] = rng.randint(1, 3)
        feito = c.get("livres_sem") or [None, 0]
        c["livres_sem"] = [agora, (feito[1] if feito[0] == agora else 0) + 1]
        clubes = [x for x in clubes if pode(x)]
        feitos += 1
        if j["ovr"] >= 78:
            manchete(G, "mercado", "%s, sem clube, assina com o %s." % (j["nome"], c["nome"]))
    return feitos


def contratar_livre_ia(G, c, pos, nivel_alvo):
    """Clube da IA busca um agente livre da posicao; devolve True se contratou."""
    presos = presos_em_acerto(G)
    cands = [G["jogadores"][p] for p in G["livres"]
             if G["jogadores"][p]["pos"] == pos and p not in presos]
    if not cands:
        return False
    cands.sort(key=lambda j: -j["ovr"])
    # so quem e do nivel do clube e cabe na folha. Antes, sem ninguem na faixa,
    # ia o MELHOR livre do mundo: as "contratacoes fantasmas" da virada
    alvo = next((j for j in cands if j["ovr"] <= nivel_alvo + 6
                 and cabe_na_folha(G, c, exigencia_salarial(G, j, c))), None)
    if alvo is None:
        return False                  # repor_elencos gera um jogador do nivel
    alvo["salario"] = exigencia_salarial(G, alvo, c)
    transferir(G, alvo["id"], c["id"], 0)
    alvo["contrato"] = rng.randint(1, 3)
    return True


def limpar_livres(G, teto=90):
    """Agentes livres encalhados se aposentam."""
    if len(G["livres"]) <= teto:
        return
    ordem = sorted(G["livres"], key=lambda p: (G["jogadores"][p]["ovr"] - G["jogadores"][p]["idade"] * 0.8))
    for pid in ordem[:len(G["livres"]) - teto]:
        G["livres"].remove(pid)
        G["jogadores"].pop(pid, None)


def repor_elencos(G, usados):
    for c in G["clubes"].values():
        if c["divisao"] == "EX":
            for pos, minimo in ELENCO_PADRAO.items():
                while conta_posicao(G, c, pos) < minimo:
                    j = novo_jogador(G, pos, 26 + c["reputacao"] * 0.58, usados)
                    j["clube"] = c["id"]
                    c["elenco"].append(j["id"])
            continue
        nivel = 24 + c["reputacao"] * 0.55
        for pos, minimo in ELENCO_PADRAO.items():
            while conta_posicao(G, c, pos) < minimo - 1 and not elenco_cheio(G, c):
                if contratar_livre_ia(G, c, pos, nivel):
                    continue
                j = novo_jogador(G, pos, nivel, usados)
                j["clube"] = c["id"]
                j["contrato"] = rng.randint(1, 3)
                c["elenco"].append(j["id"])
    limpar_livres(G)
    while len(G["livres"]) < 25:
        j = novo_jogador(G, rng.choice(POS), rng.uniform(36, 60), usados)
        G["livres"].append(j["id"])


def investimentos_ia(G):
    """Clubes da IA reinvestem o caixa em estrutura e estadio."""
    for c in G["clubes"].values():
        if c["divisao"] == "EX" or c["id"] == G["clube"]:
            continue
        for _ in range(3):
            if c["dinheiro"] < 25_000_000:
                break
            k = rng.choice(["ct", "base", "medico"])
            if c[k] >= 10:
                continue
            custo = int((c[k] + 1) ** 2 * 900_000)
            if custo < c["dinheiro"] * 0.35:
                lancar(G, c, -custo, "infra")
                c[k] += 1
        if c["dinheiro"] > 90_000_000 and c["obra_semanas"] == 0 and rng.random() < 0.5:
            lugares = min(15000, int(c["dinheiro"] * 0.30 / 3500))
            if lugares >= 1000:
                lancar(G, c, -lugares * 3500, "obras")
                c["obra_lugares"] = lugares
                c["obra_semanas"] = max(2, lugares // 1500)
        # sobra vira reforco pontual
        if c["dinheiro"] > 40_000_000 and len(c["elenco"]) < 28:
            alvos = [j for j in G["jogadores"].values()
                     if j["listado"] and j["clube"] not in (None, c["id"], G["clube"])
                     and j["listado"] < c["dinheiro"] * 0.4
                     and j["listado"] <= verba_contratacao(G, c, j["salario"])
                     and cabe_na_folha(G, c, j["salario"])]
            if alvos:
                alvo = max(alvos, key=lambda j: j["ovr"])
                transferir(G, alvo["id"], c["id"], alvo["listado"])


def premio_liga(div: str, posicao: int) -> int:
    """O que a liga paga a quem termina nesta posicao (1 = campeao)."""
    total = PREMIO.get(div) or int(perfil_liga(div)["premio"] * ESCALA_EXT.get(div, 1.0))
    return int(total * (0.55 ** ((posicao - 1) * 0.30)))


PREMIO_COPA = {"copa": 78_000_000, "lib": 130_000_000, "sul": 30_000_000,
               "ucl": 350_000_000, "uel": 90_000_000,
               "supercopa": 10_000_000, "recopa": 9_000_000,
               "intercontinental": 25_000_000, "mundial": 180_000_000}
# passar de fase paga uma fracao do premio do campeao (pelo numero de clubes
# vivos na rodada); o vice leva 40%. Antes so o campeao recebia.
FRACAO_FASE = ((32, 0.01), (16, 0.02), (8, 0.04), (4, 0.07))
FRACAO_VICE = 0.40


def premio_fase_copa(chave: str, vivos: int) -> int:
    """O que ganha quem passa de uma rodada com `vivos` clubes (final fora)."""
    total = PREMIO_COPA.get(chave, 0)
    frac = next((f for minimo, f in FRACAO_FASE if vivos >= minimo), 0.0)
    return int(total * frac)


def premiacao(G):
    for div, liga in G["ligas"].items():
        if liga["rodada"] < len(liga["rodadas"]) and div not in DIVISOES_BR:
            continue                     # liga de fora que nao terminou nao paga
        for i, cid in enumerate(classificacao(G, liga)):
            lancar(G, G["clubes"][cid], premio_liga(div, i + 1), "premio_liga")


def acesso_rebaixamento(G):
    movs = []
    ordem = {d: classificacao(G, G["ligas"][d]) for d in "ABCD"}
    G["class_A_anterior"] = ordem["A"][:]
    for sup, inf in (("A", "B"), ("B", "C"), ("C", "D")):
        caem = ordem[sup][-4:]
        sobem = ordem[inf][:4]
        for cid in caem:
            cl = G["clubes"][cid]
            cl["divisao"] = inf
            cl["reputacao"] = clamp(cl["reputacao"] - 4, 12, 99)
            for p in cl["elenco"]:
                G["jogadores"][p]["salario"] = int(G["jogadores"][p]["salario"] * 0.72)
            movs.append((cid, sup, inf))
        for cid in sobem:
            cl = G["clubes"][cid]
            cl["divisao"] = sup
            cl["reputacao"] = clamp(cl["reputacao"] + 4, 12, 99)
            for p in cl["elenco"]:
                G["jogadores"][p]["salario"] = int(G["jogadores"][p]["salario"] * 1.18)
            movs.append((cid, inf, sup))
    for d in "ABCD":
        for i, cid in enumerate(ordem[d]):
            c = G["clubes"][cid]
            if i < 4:
                c["reputacao"] = clamp(c["reputacao"] + 1, 12, 99)
            elif i > 14:
                c["reputacao"] = clamp(c["reputacao"] - 1, 12, 99)
    return movs


# ----------------------------------------------------------------------------
# DIRETORIA / OBJETIVOS
# ----------------------------------------------------------------------------

def definir_objetivo(G):
    c = G["clubes"][G["clube"]]
    div = c["divisao"]
    liga = G["ligas"][div]
    ordem = sorted(liga["times"], key=lambda i: -G["clubes"][i]["reputacao"])
    rank = ordem.index(c["id"]) + 1
    n = len(ordem)
    meio = max(6, round(n * 0.6))
    if rank <= 3:
        alvo, txt = 2, "brigar pelo titulo (terminar entre os 2 primeiros)"
    elif rank <= 6:
        alvo, txt = 6, "terminar entre os 6 primeiros"
    elif rank <= meio:
        alvo, txt = meio, "terminar entre os %d primeiros" % meio
    elif div in DIVISOES_BR:
        alvo, txt = 16, "evitar o rebaixamento (nao terminar nos 4 ultimos)"
    else:
        alvo, txt = n - 4, "fugir das ultimas posicoes (nao terminar nos 4 ultimos)"
    if div == "D":
        txt += " e brigar pelo acesso"
    G["objetivo"] = txt
    G["objetivo_alvo"] = alvo
    return alvo, txt


def avaliar_diretoria(G, posicao_final):
    alvo = G.get("objetivo_alvo", 16)
    if posicao_final <= alvo:
        return True, "A diretoria aprovou a temporada."
    if opcoes_carreira(G)["sem_demissao"]:
        return True, "A diretoria cobrou resultados, mas o seu cargo e intocavel (modo sem demissao)."
    margem = posicao_final - alvo
    risco = (0.25 + margem * 0.14) * dificuldade(G)["diretoria"]
    # a confianca do ano pesa: quem chegou com a diretoria do lado quase nao cai
    # (60 da x0,25), quem ja estava avisado cai muito mais (10 da x1,5)
    risco *= clamp((70 - confianca(G)["valor"]) / 40.0, 0.25, 1.5)
    if tem_rebaixamento(G["clubes"][G["clube"]]["divisao"]) and posicao_final > 16:
        risco += 0.30 * dificuldade(G)["diretoria"]
    if rng.random() < risco:
        return False, "A diretoria decidiu encerrar seu ciclo no %s." % G["clubes"][G["clube"]]["nome"]
    return True, "A diretoria cobrou resultados, mas manteve voce no cargo."


# ----------------------------------------------------------------------------
# CONFIANCA DA DIRETORIA
#
# Um numero de 0 a 100 que anda toda semana e diz por que andou. Resultado
# contra o esperado pela forca dos elencos (classico vale o dobro), posicao
# contra a meta e caixa no vermelho. Abaixo de CONFIANCA_AVISO a diretoria
# avisa; avisado, abaixo de CONFIANCA_DEMISSAO a demissao pode vir na semana
# seguinte, no meio do ano (decisao do usuario em 2026-09-25). A dificuldade
# multiplica so as quedas. Nada aqui sorteia: e conta sobre o que ja aconteceu.
# ----------------------------------------------------------------------------

CONFIANCA_INICIAL = 60
CONFIANCA_AVISO = 30
CONFIANCA_DEMISSAO = 15
CONFIANCA_RECUPERA = 40     # voltou acima disto, o aviso cai
CONFIANCA_HIST = 12         # semanas guardadas (a tendencia usa as 4 ultimas)
PATAMAR_CONFIANCA = {"meta": 75, "perto": 55, "longe": 35, "rebaixamento": 22}
PATAMAR_TOPO = 95            # patamar do 1o colocado, com a meta cumprida com folga


def confianca(G: Mundo) -> Dict[str, Any]:
    return G.setdefault("confianca", {"valor": CONFIANCA_INICIAL, "hist": [], "aviso": None})


def reiniciar_confianca(G: Mundo, valor: int = CONFIANCA_INICIAL) -> None:
    G["confianca"] = {"valor": int(valor), "hist": [], "aviso": None}


def tendencia_confianca(G: Mundo, semanas: int = 4) -> int:
    return sum(h[1] for h in confianca(G)["hist"][-semanas:])


def forca_elenco(G: Mundo, c: Clube) -> float:
    """Media de overall dos 11 melhores: o tamanho do time, sem cansaco do dia."""
    ovrs = sorted((G["jogadores"][p]["ovr"] for p in c["elenco"] if p in G["jogadores"]), reverse=True)
    top = ovrs[:11]
    return sum(top) / len(top) if top else 40.0


# curva medida no proprio motor (9 mil jogos, forca_elenco do mandante menos a
# do visitante contra os pontos do mandante): escala 24 e casa valendo 4 de
# overall. Com a curva mais inclinada o favorito "devia" ganhar mais do que o
# motor deixa e a confianca escorria ate de quem jogava o esperado.
ESCALA_ESPERADO = 24.0
CASA_ESPERADO = 4.0


def resultado_esperado(G: Mundo, meu: Clube, adv: Clube, em_casa: Optional[bool]) -> float:
    """0 a 1: quanto o meu time devia tirar do jogo (vitoria 1, empate 0,5)."""
    diff = forca_elenco(G, meu) - forca_elenco(G, adv)
    if em_casa is not None:
        diff += CASA_ESPERADO if em_casa else -CASA_ESPERADO
    return clamp(1.0 / (1.0 + 10 ** (-diff / ESCALA_ESPERADO)), 0.1, 0.9)


def atualizar_confianca(G: Mundo, meus: List[Dict[str, Any]]) -> None:
    """A semana da diretoria: soma as causas, avisa e, se for o caso, demite."""
    conf = confianca(G)
    c = G["clubes"][G["clube"]]
    causas: List[List[Any]] = []
    for r in meus:
        em_casa = r["casa"] == c["id"]
        adv = G["clubes"].get(r["fora"] if em_casa else r["casa"])
        if not adv:
            continue
        gm, gs = (r["gc"], r["gf"]) if em_casa else (r["gf"], r["gc"])
        pontos = 1.0 if gm > gs else (0.5 if gm == gs else 0.0)
        neutro = r.get("pub", 0) == 0 and r.get("comp") not in ("liga", "estadual")
        esperado = resultado_esperado(G, c, adv, None if neutro else em_casa)
        classico = eh_classico(G, r["casa"], r["fora"])
        delta = int(round((pontos - esperado) * 8 * (2 if classico else 1)))
        if delta:
            quem = "vitoria sobre" if gm > gs else ("empate com" if gm == gs else "derrota para")
            causas.append([delta, "%s o %s%s" % (quem, adv["nome"], " no classico" if classico else "")])
    # a posicao nao soma sem fim: puxa a confianca para um patamar (12% da
    # distancia por semana). Sozinha ela leva no maximo ao aviso; demissao
    # pede resultado abaixo do esperado em cima
    liga = G["ligas"].get(c["divisao"])
    if G.get("fase") == "liga" and liga and liga["rodada"] >= 6:
        pos = posicao_na_liga(G, c["id"])
        total = len(liga["times"])
        alvo = int(G.get("objetivo_alvo", 16))
        if tem_rebaixamento(c["divisao"]) and pos > total - 4:
            patamar, txt = PATAMAR_CONFIANCA["rebaixamento"], "zona de rebaixamento (%do)" % pos
        elif pos <= alvo:
            # quanto mais folga sobre a meta, mais alto o patamar: 75 no limite,
            # ate PATAMAR_TOPO em 1o. Antes era 75 para todos, e o lider com 83
            # de confianca perdia ponto "dentro da meta"
            folga = (alvo - pos) / float(max(1, alvo - 1))
            patamar = PATAMAR_CONFIANCA["meta"] + (PATAMAR_TOPO - PATAMAR_CONFIANCA["meta"]) * folga
            txt = "dentro da meta (%do)" % pos
        elif pos <= alvo + 3:
            patamar, txt = PATAMAR_CONFIANCA["perto"], "perto da meta (%do, meta top %d)" % (pos, alvo)
        else:
            patamar, txt = PATAMAR_CONFIANCA["longe"], "abaixo da meta (%do, meta top %d)" % (pos, alvo)
        puxao = int(round((patamar - conf["valor"]) * 0.12))
        if pos <= alvo and not (tem_rebaixamento(c["divisao"]) and pos > total - 4):
            puxao = max(0, puxao)       # dentro da meta a tabela so ajuda; quem tira e o resultado
        if puxao:
            causas.append([puxao, txt])
    if c["dinheiro"] < 0:
        causas.append([-1, "caixa no vermelho"])
    cr = credito(G)
    if cr and cr.get("ultimo_atraso") is not None and cr["ultimo_atraso"] >= semana_absoluta(G) - 1:
        causas.append([CREDITO_CONFIANCA_ATRASO, "parcela do credito atrasada"])
    mult = dificuldade(G)["diretoria"]
    for x in causas:
        if x[0] < 0:
            x[0] = int(round(x[0] * mult)) or -1
    total_semana = sum(x[0] for x in causas)
    conf["valor"] = int(clamp(conf["valor"] + total_semana, 0, 100))
    if causas:
        conf["hist"].append([semana_absoluta(G), total_semana, causas])
        del conf["hist"][:-CONFIANCA_HIST]
    agora = semana_absoluta(G)
    if conf["aviso"] is None and conf["valor"] < CONFIANCA_AVISO:
        conf["aviso"] = agora
        noticia(G, "A diretoria perdeu a paciencia: se a confianca cair abaixo de %d, voce esta fora."
                % CONFIANCA_DEMISSAO)
    elif conf["aviso"] is not None and conf["valor"] >= CONFIANCA_RECUPERA:
        conf["aviso"] = None
        noticia(G, "A diretoria voltou a confiar no trabalho.")
    elif (conf["aviso"] is not None and conf["aviso"] < agora
          and conf["valor"] < CONFIANCA_DEMISSAO and not opcoes_carreira(G)["sem_demissao"]):
        G["motivo_demissao"] = ("Depois do aviso, a confianca da diretoria caiu para %d. "
                                "O %s encerrou o seu ciclo no meio da temporada." % (conf["valor"], c["nome"]))
        noticia(G, "Demitido: o %s perdeu a confianca no treinador." % c["nome"])
        trocar_de_clube(G)


# a maquina demite tambem, nos marcos: fim do turno e fim da temporada. Sem
# sorteio: clube que despencou 6 posicoes abaixo do tamanho (ordem de
# reputacao na liga) e esta no terco de baixo manda o treinador embora. A vaga
# fica aberta VAGA_TECNICO_SEMANAS e e ela que liga para o treinador que vai bem.
VAGA_TECNICO_SEMANAS = 10
DEMISSOES_POR_MARCO = 2


def ia_demite_tecnicos(G: Mundo, fim_de_ano: bool = False) -> List[int]:
    demitiu = []
    for liga in G["ligas"].values():
        rodadas = len(liga.get("rodadas") or [])
        if not rodadas or not liga["times"]:
            continue
        if fim_de_ano:
            if liga["rodada"] < rodadas:
                continue
        elif liga["rodada"] != rodadas // 2 or liga.get("turno_avaliado") == G["temporada"]:
            continue
        liga["turno_avaliado"] = G["temporada"]
        ordem = classificacao(G, liga)
        tamanho = sorted(ordem, key=lambda cid: -G["clubes"][cid]["reputacao"])
        total = len(ordem)
        caidos = []
        for pos, cid in enumerate(ordem, 1):
            if cid == G.get("clube"):
                continue
            queda = pos - (tamanho.index(cid) + 1)
            if queda >= 6 and pos > round(total * 0.6):
                caidos.append((-queda, pos, cid))
        for _q, pos, cid in sorted(caidos)[:DEMISSOES_POR_MARCO]:
            cl = G["clubes"][cid]
            manchete(G, "tecnico", "%s demite o treinador depois de %s em %do." % (
                cl["nome"], "fechar o ano" if fim_de_ano else "fechar o turno", pos))
            G.setdefault("vagas_tecnico", []).append(
                {"id": cid, "vence": semana_absoluta(G) + VAGA_TECNICO_SEMANAS})
            demitiu.append(cid)
    return demitiu


def vagas_tecnico(G: Mundo) -> List[int]:
    """Clubes com o cargo vago (as vencidas e a do meu clube saem aqui)."""
    agora = semana_absoluta(G)
    vivas = [v for v in G.get("vagas_tecnico", [])
             if v["vence"] > agora and v["id"] in G["clubes"] and v["id"] != G.get("clube")]
    G["vagas_tecnico"] = vivas
    return [v["id"] for v in vivas]


# ----------------------------------------------------------------------------
# OPCOES DA CARREIRA
#
# Escolhidas uma vez, na criacao do save, e guardadas em G["opcoes"]. Save
# antigo nao tem a chave e joga com o padrao, que e o jogo de sempre.
# ----------------------------------------------------------------------------

DIFICULDADES = {
    # diretoria: multiplica o risco de demissao; caixa: o caixa do primeiro clube
    "facil": {"nome": "Facil", "diretoria": 0.5, "caixa": 1.4,
              "desc": "diretoria paciente e 40% a mais de caixa no primeiro clube"},
    "normal": {"nome": "Normal", "diretoria": 1.0, "caixa": 1.0,
               "desc": "o jogo de sempre"},
    "dificil": {"nome": "Dificil", "diretoria": 1.5, "caixa": 0.75,
                "desc": "diretoria impaciente e 25% a menos de caixa no primeiro clube"},
}

OPCOES_PADRAO = {"dificuldade": "normal", "sem_demissao": False, "investidor": False, "modo": "classico"}

# o investidor compra o clube e poe dinheiro de uma vez, conforme a serie
APORTE_INVESTIDOR = {"A": 150_000_000, "B": 60_000_000, "C": 25_000_000, "D": 10_000_000}


def opcoes_carreira(G: Mundo) -> Dict[str, Any]:
    fora = dict(OPCOES_PADRAO)
    fora.update(G.get("opcoes") or {})
    if fora["dificuldade"] not in DIFICULDADES:
        fora["dificuldade"] = "normal"
    return fora


def dificuldade(G: Mundo) -> Dict[str, Any]:
    return DIFICULDADES[opcoes_carreira(G)["dificuldade"]]


def definir_opcoes_carreira(G: Mundo, opcoes: Dict[str, Any]) -> Dict[str, Any]:
    """Grava so as chaves conhecidas, com o tipo certo."""
    limpo = dict(OPCOES_PADRAO)
    if opcoes.get("dificuldade") in DIFICULDADES:
        limpo["dificuldade"] = opcoes["dificuldade"]
    limpo["sem_demissao"] = bool(opcoes.get("sem_demissao"))
    limpo["investidor"] = bool(opcoes.get("investidor"))
    if opcoes.get("modo") in MODOS:
        limpo["modo"] = opcoes["modo"]
    G["opcoes"] = limpo
    return limpo


def limpar_vitrine_herdada(G: Mundo, c: Clube, a_venda: bool = True) -> None:
    """O mundo e sorteado antes da escolha do clube: a IA ja tinha posto
    jogadores a venda e marcado cediveis (a marca que alimenta a aba de
    emprestimos dela). No clube do treinador isso vira ruido - a vitrine e
    decisao dele, e ceder e pelo botao Ceder. Limpa ao assumir."""
    for p in c["elenco"]:
        j = G["jogadores"][p]
        j["emp_listado"] = 0
        if a_venda:
            j["listado"] = 0


def comecar_no_clube(G: Mundo, c: Clube) -> List[str]:
    """O primeiro clube da carreira recebe o que as opcoes prometem: caixa da
    dificuldade e, com investidor, o aporte. Devolve as noticias do dia."""
    limpar_vitrine_herdada(G, c)
    op = opcoes_carreira(G)
    recados = []
    mult = DIFICULDADES[op["dificuldade"]]["caixa"]
    if mult != 1.0:
        c["dinheiro"] = int(c["dinheiro"] * mult)
    if op["investidor"]:
        aporte = APORTE_INVESTIDOR.get(c["divisao"]) or int(APORTE_INVESTIDOR["A"] * perfil_liga(c["divisao"])["caixa"])
        c["dinheiro"] += aporte
        c["reputacao"] = clamp(c["reputacao"] + 2, 10, 99)
        recados.append("Investidor compra o %s e injeta %s no caixa." % (c["nome"], din(aporte)))
    G["tecnico_rep"] = REP_TECNICO_INICIAL
    G["carreira"] = [_passagem(G, c["id"])]
    novo_ano_stats(G)   # o caixa do comeco ja com dificuldade e aporte
    G["propostas_emprego"] = []
    for r in recados:
        noticia(G, r)
    return recados


# ----------------------------------------------------------------------------
# CARREIRA DO TREINADOR
#
# O treinador tem reputacao propria (G["tecnico_rep"], 1 a 99), separada da do
# clube: sobe com meta cumprida e titulo, cai com fracasso. E ela que decide
# quem liga oferecendo emprego e quem aceita um treinador que pediu demissao.
# Cada clube dirigido vira uma passagem em G["carreira"], com jogos, titulos e
# marcos - a sala de trofeus le daqui e nunca apaga nada.
# ----------------------------------------------------------------------------

REP_TECNICO_INICIAL = 35
PROPOSTA_VALIDADE = 6        # semanas que uma proposta de emprego fica de pe
MAX_PROPOSTAS = 3
# quanto cada titulo pesa na reputacao do treinador
PESO_TITULO = {"Brasileirao Serie A": 12, "Libertadores": 12, "Copa do Brasil": 8,
               "Sul-Americana": 6, "Brasileirao Serie B": 6, "Brasileirao Serie C": 4,
               "Brasileirao Serie D": 3}
PESO_TITULO_OUTROS = 3       # estaduais e regionais


def _passagem(G: Mundo, cid: int, parcial: bool = False) -> Dict[str, Any]:
    c = G["clubes"][cid]
    return {"clube_id": cid, "clube": c["nome"], "divisao": c["divisao"],
            "de": int(G["temporada"]), "ate": None, "saida": None,
            "j": 0, "v": 0, "e": 0, "d": 0, "gp": 0, "gc": 0,
            "titulos": [], "marcos": [],
            # save de antes da sala de trofeus: o registro comeca no meio
            "parcial": parcial}


def carreira(G: Mundo) -> List[Dict[str, Any]]:
    """As passagens do treinador, da primeira a atual. Save antigo ganha a
    passagem atual aberta na primeira leitura."""
    lst = G.setdefault("carreira", [])
    if not lst and G.get("clube") in G.get("clubes", {}):
        lst.append(_passagem(G, G["clube"], parcial=True))
    return lst


def passagem_atual(G: Mundo) -> Optional[Dict[str, Any]]:
    lst = carreira(G)
    if lst and lst[-1]["ate"] is None and lst[-1]["clube_id"] == G.get("clube"):
        return lst[-1]
    return None


def rep_tecnico(G: Mundo) -> int:
    if "tecnico_rep" not in G:
        # save antigo: quem ja tem estrada comeca mais conhecido
        G["tecnico_rep"] = int(min(70, REP_TECNICO_INICIAL + 3 * len(G.get("historico", []))))
    return int(G["tecnico_rep"])


def mexer_rep_tecnico(G: Mundo, delta: float) -> None:
    G["tecnico_rep"] = int(round(clamp(rep_tecnico(G) + delta, 1, 99)))


def contar_jogo_na_carreira(G: Mundo, gm: int, gs: int) -> None:
    p = passagem_atual(G)
    if not p:
        return
    p["j"] += 1
    p["gp"] += int(gm)
    p["gc"] += int(gs)
    p["v" if gm > gs else ("e" if gm == gs else "d")] += 1


def dar_titulo(G: Mundo, cl: Clube, nome: str) -> None:
    """Conta a taca para o clube e, se for o meu, para a sala de trofeus."""
    cl["titulos"][nome] = cl["titulos"].get(nome, 0) + 1
    cl.setdefault("titulos_hist", []).append({"nome": nome, "temporada": int(G["temporada"])})
    manchete(G, "titulo", "%s e campeao: %s %d." % (cl["nome"], nome, int(G["temporada"])))
    if cl["id"] != G.get("clube"):
        return
    p = passagem_atual(G)
    if p is not None:
        p["titulos"].append({"nome": nome, "temporada": int(G["temporada"])})
    mexer_rep_tecnico(G, PESO_TITULO.get(nome, PESO_TITULO_OUTROS))


def marco(G: Mundo, texto: str) -> None:
    p = passagem_atual(G)
    if p is not None:
        p["marcos"].append({"temporada": int(G["temporada"]), "texto": texto})


def _fechar_passagem(G: Mundo, saida: str) -> None:
    p = passagem_atual(G)
    if p is None:
        return
    # na pre-temporada o ano novo ainda nao teve jogo: a passagem acabou no anterior
    ate = int(G["temporada"]) - (1 if G.get("fase") == "entretemporada" else 0)
    p["ate"] = max(int(p["de"]), ate)
    p["saida"] = saida


def assumir_clube(G: Mundo, cid: int, saida: str) -> None:
    """Troca de clube no meio da carreira: fecha a passagem atual com o motivo
    da saida e abre a nova. Serve a demissao, ao pedido de demissao e a
    proposta aceita - e o unico lugar que muda G["clube"] depois do inicio."""
    antigo = G["clubes"][G["clube"]]
    _fechar_passagem(G, saida)
    largar_clube(antigo)
    limpar_vitrine_herdada(G, G["clubes"][cid])
    G["clube"] = cid
    herdar_preferencias(G, antigo)
    definir_objetivo(G)
    reiniciar_confianca(G)
    herdar_patrocinios(G, G["clubes"][cid])
    novo_ano_stats(G)   # o extrato e do clube de agora: misturar dois caixas nao fecha
    G["propostas_emprego"] = []
    carreira(G).append(_passagem(G, cid))
    noticia(G, "%s deixa o %s (%s) e assume o %s." %
            (G.get("tecnico") or "O tecnico", antigo["nome"], saida, G["clubes"][cid]["nome"]))


def largar_clube(c: Clube) -> None:
    """O que era decisao do tecnico sai junto com ele. Sem isto a maquina
    herdava as vagas fixadas na Escalacao (atribuir_vagas le de qualquer
    clube), o CT seguia cobrando o treino individual e a peneira paga seguia
    ligada num clube que nao e mais dele."""
    c.pop("vagas_manuais", None)
    c["treino_foco"] = []
    c["peneira"] = None
    c["base_candidatos"] = []
    c["esc_stamp"] = ""
    c.pop("patrocinios", None)      # contrato de patrocinio e do tecnico que negociou


def encerrar_passagem(G: Mundo, saida: str) -> None:
    """Fim de carreira: a ultima passagem fecha sem clube novo."""
    _fechar_passagem(G, saida)


def clubes_interessados(G: Mundo, n: int, teto: int) -> List[Clube]:
    """Clubes que aceitariam este treinador: reputacao ate o teto. Sorteio
    entre os mais fortes que cabem, para nao ser sempre a mesma lista."""
    cands = [cl for cl in G["clubes"].values()
             if cl["divisao"] != "EX" and cl["id"] != G.get("clube") and cl["reputacao"] <= teto]
    cands.sort(key=lambda cl: -cl["reputacao"])
    escolha = rng.sample(cands[:max(12, n)], min(n, len(cands)))
    escolha.sort(key=lambda cl: -cl["reputacao"])
    return escolha


def propostas_emprego(G: Mundo) -> List[Dict[str, Any]]:
    """As propostas ainda de pe (as vencidas saem aqui)."""
    agora = semana_absoluta(G)
    vivas = [o for o in G.get("propostas_emprego", [])
             if o.get("vence", 0) > agora
             and o["id"] in G["clubes"] and o["id"] != G.get("clube")]
    G["propostas_emprego"] = vivas
    return vivas


def sondar_treinador(G: Mundo, ano_bom: Optional[bool] = None) -> Optional[Dict[str, Any]]:
    """Uma vez por mes, no Brasileirao: quem esta indo bem atrai proposta.

    A chance sobe com o time em cima da meta e com a reputacao do treinador.
    Quem liga e clube pelo menos do tamanho do atual (menos uma folga) que cabe
    na reputacao dele - ninguem da Serie A liga para um desconhecido.

    ano_bom (so na virada): a temporada que acabou julga, e nao a tabela atual,
    que acabou de zerar. E quando o mercado de treinadores mais mexe.
    """
    if ano_bom is None and (G.get("fase") != "liga" or G["semana"] > SEMANAS_LIGA - 4):
        return None
    vivas = propostas_emprego(G)
    if len(vivas) >= MAX_PROPOSTAS:
        return None
    c = G["clubes"][G["clube"]]
    rep = rep_tecnico(G)
    if ano_bom is None:
        ordem = classificacao(G, G["ligas"][c["divisao"]])
        pos = ordem.index(c["id"]) + 1 if c["id"] in ordem else 99
        alvo = G.get("objetivo_alvo", 16)
        # time afundando abaixo da meta nao atrai ninguem, por mais nome que o tecnico tenha
        if pos > alvo + 6:
            return None
        chance = 0.05 + (0.20 if pos <= alvo else 0.0) + max(0, rep - 40) / 250.0
    else:
        chance = (0.45 if ano_bom else 0.08) + max(0, rep - 40) / 250.0
    if rng.random() >= chance:
        return None
    ja = {o["id"] for o in vivas}
    # dirigir um clube prova o nivel: quem esta bem num grande atrai grande
    teto = max(rep + 8, c["reputacao"] + 6)
    cands = [cl for cl in clubes_interessados(G, 6, teto)
             if cl["id"] not in ja and cl["reputacao"] >= c["reputacao"] - 3]
    if not cands:
        return None
    cl = cands[0] if rng.random() < 0.5 else rng.choice(cands)
    # clube que acabou de demitir o treinador liga antes (mesmo sorteio de
    # antes: a vaga so muda quem, nunca se)
    vagas = set(vagas_tecnico(G))
    com_vaga = [x for x in cands if x["id"] in vagas]
    if com_vaga:
        cl = com_vaga[0]
    oferta = {"id": cl["id"], "clube": cl["nome"], "divisao": cl["divisao"],
              "reputacao": cl["reputacao"], "temporada": int(G["temporada"]),
              "vence": semana_absoluta(G) + PROPOSTA_VALIDADE}
    G.setdefault("propostas_emprego", []).append(oferta)
    noticia(G, "O %s quer contratar %s. A proposta vale por %d semanas." %
            (cl["nome"], G.get("tecnico") or "voce", PROPOSTA_VALIDADE))
    return oferta


def aceitar_proposta_emprego(G: Mundo, cid: int) -> Tuple[bool, str]:
    if cid not in [o["id"] for o in propostas_emprego(G)]:
        return False, "Essa proposta nao existe mais."
    antigo = G["clubes"][G["clube"]]["nome"]
    assumir_clube(G, cid, "aceitou proposta do %s" % G["clubes"][cid]["nome"])
    return True, "Voce deixou o %s e assumiu o %s. Objetivo: %s." % (
        antigo, G["clubes"][cid]["nome"], G["objetivo"])


def recusar_proposta_emprego(G: Mundo, cid: int) -> Tuple[bool, str]:
    antes = len(G.get("propostas_emprego", []))
    G["propostas_emprego"] = [o for o in G.get("propostas_emprego", []) if o["id"] != cid]
    if len(G["propostas_emprego"]) == antes:
        return False, "Essa proposta nao existe mais."
    return True, "Proposta do %s recusada." % G["clubes"][cid]["nome"]


def ofertas_ao_demissionario(G: Mundo, n: int = 4) -> List[Clube]:
    """Quem pede demissao desce um degrau: cabe no teto a reputacao dele ou a
    do clube que deixou, menos um pouco."""
    atual = G["clubes"][G["clube"]]["reputacao"]
    return clubes_interessados(G, n, max(rep_tecnico(G) + 8, atual - 4))



# ----------------------------------------------------------------------------
# IDENTIDADE VISUAL (tudo em texto, sem enfeite que atrapalhe)
# ----------------------------------------------------------------------------

LARG = 80

CORES = {
    "reset": "\033[0m", "neg": "\033[1m", "fraco": "\033[2m",
    "tit": "\033[1;36m", "ok": "\033[32m", "ruim": "\033[31m",
    "av": "\033[33m", "des": "\033[35m", "azul": "\033[34m",
}

TRACOS = {"h": "─", "v": "│", "ne": "╮", "no": "╭", "se": "╯", "so": "╰",
          "dh": "═", "pt": "·", "seta": "›"}
TRACOS_ASCII = {"h": "-", "v": "|", "ne": "+", "no": "+", "se": "+", "so": "+",
                "dh": "=", "pt": "-", "seta": ">"}

ESTILO = {"cor": True, "uni": True}


def preparar_terminal(discreto=False):
    if os.name == "nt":
        os.system("")
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if discreto:
        ESTILO["cor"] = False
        ESTILO["uni"] = False
        return
    ESTILO["cor"] = sys.stdout.isatty() or os.environ.get("FORCE_COLOR")
    try:
        "─╭╯".encode(sys.stdout.encoding or "utf-8")
    except Exception:
        ESTILO["uni"] = False


def tr(k):
    return (TRACOS if ESTILO["uni"] else TRACOS_ASCII)[k]


def cor(txt, nome):
    if not ESTILO["cor"] or not nome:
        return txt
    return CORES.get(nome, "") + txt + CORES["reset"]


def visivel(txt):
    return len(re.sub(r"\033\[[0-9;]*m", "", txt))


def pad(txt, larg, alin="<"):
    falta = max(0, larg - visivel(txt))
    if alin == ">":
        return " " * falta + txt
    if alin == "^":
        e = falta // 2
        return " " * e + txt + " " * (falta - e)
    return txt + " " * falta


def regra(c=None, larg=LARG):
    print(cor((c or tr("h")) * larg, "fraco"))


def titulo(txt, sub=""):
    print()
    print(cor(txt.upper(), "tit") + (cor("  " + tr("pt") + "  " + sub, "fraco") if sub else ""))
    print(cor(tr("h") * LARG, "fraco"))


def caixa(linhas, cor_borda="fraco"):
    print(cor(tr("no") + tr("h") * (LARG - 2) + tr("ne"), cor_borda))
    for l in linhas:
        print(cor(tr("v"), cor_borda) + pad(" " + l, LARG - 2) + cor(tr("v"), cor_borda))
    print(cor(tr("so") + tr("h") * (LARG - 2) + tr("se"), cor_borda))


def tabela(cols, linhas):
    """cols = [(titulo, largura, alinhamento)], linhas = lista de tuplas de texto."""
    cab = " ".join(pad(c[0], c[1], c[2]) for c in cols)
    print(cor(cab, "fraco"))
    print(cor(tr("h") * min(LARG, visivel(cab)), "fraco"))
    for ln in linhas:
        print(" ".join(pad(str(v), cols[i][1], cols[i][2]) for i, v in enumerate(ln)))


def menu(itens, largura_col=38):
    """itens = [(tecla, texto)] distribuidos em duas colunas."""
    metade = (len(itens) + 1) // 2
    esq, dir_ = itens[:metade], itens[metade:]
    linhas = []
    for i in range(metade):
        a = "%s %s" % (cor(pad(esq[i][0], 2, ">"), "neg"), esq[i][1])
        b = ""
        if i < len(dir_):
            b = "%s %s" % (cor(pad(dir_[i][0], 2, ">"), "neg"), dir_[i][1])
        linhas.append(pad(a, largura_col) + b)
    caixa(linhas)


def cor_ovr(v):
    if v >= 80:
        return "des"
    if v >= 72:
        return "ok"
    if v >= 62:
        return "neg"
    if v >= 52:
        return ""
    return "fraco"


def barra(valor, larg=10):
    cheio = int(round(clamp(valor, 0, 100) / 100.0 * larg))
    return "#" * cheio + "." * (larg - cheio)



# ----------------------------------------------------------------------------
# FICHAS E LISTAS
# ----------------------------------------------------------------------------

NOME_POS = {"GOL": "Goleiro", "ZAG": "Zagueiro", "LAT": "Lateral",
            "VOL": "Volante", "MEI": "Meia", "ATA": "Atacante"}


def situacao(G, j):
    if j["lesao"] > 0:
        return cor("lesao %ds" % j["lesao"], "ruim")
    if j["suspensao"] > 0:
        gan = [k for k in COMPETICOES if j.get("susp", {}).get(k, 0) > 0]
        return cor("gancho %s" % "/".join(gan), "ruim")
    if any(v == 2 for v in j.get("amar", {}).values()):
        pend = [k for k, v in j["amar"].items() if v == 2]
        return cor("pendurado %s" % "/".join(pend), "av")
    if j["contrato"] <= 0:
        return cor("sem contrato", "av")
    if j.get("dono"):
        return cor("emprestado", "azul")
    if j["listado"]:
        return cor("a venda", "av")
    if j.get("emp_listado"):
        return cor("cedivel", "fraco")
    return ""


def linha_jogador(G, j, i=None):
    return (
        str(i) if i is not None else "",
        j["pos"],
        j["nome"][:16],
        j["idade"],
        cor(str(j["ovr"]), cor_ovr(j["ovr"])),
        scout(G, j),
        j["cond"],
        j["forma"],
        j["moral"],
        "%d/%d" % (j["j"], j["g"]),
        din(j["salario"]),
        j["contrato"],
        situacao(G, j),
    )


COLS_ELENCO = [("#", 3, ">"), ("POS", 3, "<"), ("JOGADOR", 16, "<"), ("IDA", 3, ">"),
               ("OVR", 3, ">"), ("TETO", 7, "<"), ("FIS", 3, ">"), ("FOR", 3, ">"),
               ("MOR", 3, ">"), ("J/G", 5, ">"), ("SALARIO", 9, ">"),
               ("CT", 2, ">"), ("SIT", 8, "<")]


def ficha(G, j, mostrar_clube=True):
    dono = G["clubes"][j["clube"]]["nome"] if j["clube"] else "sem clube"
    l = []
    l.append("%s %s %s, %d anos" % (cor(j["nome"], "neg"), tr("pt"),
                                    NOME_POS[j["pos"]], j["idade"]))
    if mostrar_clube:
        l.append("Clube: %s" % dono)
    l.append("Overall %s   Teto estimado %s   %s" %
             (cor(str(j["ovr"]), cor_ovr(j["ovr"])), cor(scout(G, j), "av"), barra(j["ovr"])))
    l.append("Condicao %3d  Forma %3d  Moral %3d" % (j["cond"], j["forma"], j["moral"]))
    l.append("Salario %s/mes   Valor de mercado %s   Contrato %s" %
             (din(j["salario"]), din(j["valor"]), plural(j["contrato"], "ano")))
    if j["listado"]:
        l.append("Pedido do clube: %s" % din(j["listado"]))
    if j.get("emp_listado"):
        l.append("Disponivel para emprestimo")
    caixa(l)


def escolher_do_elenco(G, texto="Numero do jogador (0 cancela): ", filtro=None):
    c = G["clubes"][G["clube"]]
    elenco = [p for p in c["elenco"] if (filtro is None or filtro(G["jogadores"][p]))]
    elenco.sort(key=lambda p: (POS.index(G["jogadores"][p]["pos"]), -G["jogadores"][p]["ovr"]))
    if not elenco:
        print("Nenhum jogador se encaixa aqui.")
        return None
    tabela(COLS_ELENCO, [linha_jogador(G, G["jogadores"][p], i)
                         for i, p in enumerate(elenco, 1)])
    k = ler_int(texto, G, 0, len(elenco))
    if not k:
        return None
    return G["jogadores"][elenco[k - 1]]


# ----------------------------------------------------------------------------
# PAINEL
# ----------------------------------------------------------------------------

def cabecalho(G):
    c = G["clubes"][G["clube"]]
    p = tr("pt")
    l1 = "%s %s %s %s Serie %s" % (cor(c["nome"].upper(), "neg"), p, c["estadio"], p, c["divisao"])
    dir1 = "Temporada %d" % G["temporada"]
    if G["fase"] == "entretemporada":
        dir1 += " %s pre-temporada" % p
    else:
        dir1 += " %s semana %02d/%d" % (p, G["semana"], SEMANAS_LIGA)
    esp1 = LARG - 4 - visivel(dir1)
    if visivel(l1) > esp1:
        l1 = "%s %s Serie %s" % (cor(c["nome"].upper(), "neg"), p, c["divisao"])
    linhas = [pad(l1, esp1) + cor(dir1, "fraco")]

    liga = G["ligas"][c["divisao"]]
    if G["fase"] != "entretemporada" and liga["rodada"] > 0:
        pos = posicao_na_liga(G, c["id"])
        t = liga["tabela"][str(c["id"])]
        esq = "%do lugar %s %d pts em %d jogos" % (pos, p, t["p"], t["j"])
    else:
        curto = {2: "brigar pelo titulo", 6: "terminar no G6", 12: "ficar no top 12"}
        esq = "Meta: %s" % curto.get(G.get("objetivo_alvo", 16), "fugir do rebaixamento")
    caixa_cor = "ok" if c["dinheiro"] >= 0 else "ruim"
    dir2 = "caixa %s %s folha %s" % (cor(din(c["dinheiro"]), caixa_cor), p,
                                     din(folha_semanal(G, c) * 4))
    esp2 = LARG - 4 - visivel(dir2)
    if visivel(esq) > esp2:
        esq = esq[:max(0, esp2 - 1)] + tr("pt")
    linhas.append(pad(esq, esp2) + dir2)
    caixa(linhas, "fraco")

    n = len(c["elenco"])
    aptos = sum(1 for x in c["elenco"] if disponivel(G, x))
    if n < 18 or aptos < 13:
        print(cor("  Elenco curto: %d jogadores, %d aptos. Va ao mercado." % (n, aptos), "av"))
    if c["dinheiro"] < 0:
        print(cor("  Caixa negativo. Corte folha, ceda jogadores ou venda alguem.", "ruim"))


# ----------------------------------------------------------------------------
# ELENCO
# ----------------------------------------------------------------------------

def tela_elenco(G, cid=None, detalhar=True):
    c = G["clubes"][cid or G["clube"]]
    ordem = sorted(c["elenco"],
                   key=lambda p: (POS.index(G["jogadores"][p]["pos"]), -G["jogadores"][p]["ovr"]))
    med = media_elenco(G, c)
    idade = sum(G["jogadores"][p]["idade"] for p in c["elenco"]) / max(1, len(c["elenco"]))
    titulo("elenco " + c["nome"], "%d jogadores %s media %.1f %s idade media %.1f" %
           (len(c["elenco"]), tr("pt"), med, tr("pt"), idade))
    linhas = []
    atual = None
    for i, pid in enumerate(ordem, 1):
        j = G["jogadores"][pid]
        if j["pos"] != atual:
            atual = j["pos"]
        linhas.append(linha_jogador(G, j, i))
    tabela(COLS_ELENCO, linhas)
    cedidos = [p for p in c.get("emprestados", []) if p in G["jogadores"]]
    if cedidos:
        print(cor("\nCedidos por emprestimo:", "fraco"))
        for p in cedidos:
            j = G["jogadores"][p]
            print("  %-20s %s em %s, pagamos %d%% do salario" %
                  (j["nome"], j["pos"], G["clubes"][j["clube"]]["nome"], 100 - j["emp_pct"]))
    print(cor("FIS condicao fisica %s FOR forma %s MOR moral %s J/G jogos e gols %s CT anos de contrato"
              % (tr("pt"), tr("pt"), tr("pt"), tr("pt")), "fraco"))
    if detalhar and not G.get("auto"):
        while True:
            k = ler_int("Ver a ficha de quem? (numero, 0 volta): ", G, 0, len(ordem))
            if not k:
                return ordem
            ficha_completa(G, G["jogadores"][ordem[k - 1]])
    return ordem


def ficha_completa(G, j):
    papel = {"GOL": "embaixo das traves", "ZAG": "na zaga", "LAT": "na lateral",
             "VOL": "na primeira linha de meio", "MEI": "na criacao",
             "ATA": "no ataque"}[j["pos"]]
    if j["ovr"] >= 78:
        nivel = "peca de Serie A, daquelas que decidem jogo"
    elif j["ovr"] >= 70:
        nivel = "titular tranquilo em qualquer time de Serie A ou B"
    elif j["ovr"] >= 62:
        nivel = "titular de Serie B, rodagem boa"
    elif j["ovr"] >= 52:
        nivel = "nivel de Serie C, quebra galho mais acima"
    else:
        nivel = "ainda cru, coisa de Serie D ou base"
    if j["idade"] <= 21 and j["pot"] - j["ovr"] >= 8:
        fase = "garoto com espaco pra crescer bastante"
    elif j["idade"] <= 28:
        fase = "esta no auge ou chegando nele"
    elif j["idade"] <= 32:
        fase = "veterano, tende a cair de rendimento em breve"
    else:
        fase = "fim de carreira, o overall cai todo ano"
    ficha(G, j)
    linhas = ["%s, joga %s" % (nivel, papel),
              "Leitura do olheiro: %s" % rotulo_scout(G, j),
              fase]
    revisao = leitura_teto(j)
    if revisao:
        linhas.append(revisao)
    if da_base(j):
        linhas.append("Categoria de base: nao joga e nao entra no mercado ate subir.")
    if em_foco(G, j):
        linhas.append("Em treino individual: evolui 50% mais rapido.")
    caixa(linhas + [
           "Temporada: %s, %s, %s, %s" %
           (plural(j["j"], "jogo"), plural(j["g"], "gol"), plural(j["a"], "assistencia"),
            plural(j["ca"], "amarelo")),
           "Carreira no jogo: %s e %s" % (plural(j["car_j"], "jogo"), plural(j["car_g"], "gol")),
           "Condicao %s %d   Forma %s %d   Moral %s %d" %
           (barra(j["cond"], 8), j["cond"], barra(j["forma"], 8), j["forma"],
            barra(j["moral"], 8), j["moral"])])


# ----------------------------------------------------------------------------
# ESCALACAO
# ----------------------------------------------------------------------------

def setor(pos):
    return {"GOL": "GOL", "ZAG": "DEF", "LAT": "DEF", "VOL": "MEI", "MEI": "MEI", "ATA": "ATA"}[pos]


def tela_escalacao(G):
    c = G["clubes"][G["clube"]]
    if not c.get("escalacao"):
        c["escalacao"] = auto_escalar(G, c)
    while True:
        esc, form = escalacao_valida(G, c)
        c["escalacao"] = esc
        at, de, _ = forcas(G, c)
        resto = [p for p in c["elenco"] if p not in esc]
        resto.sort(key=lambda p: (not disponivel(G, p),
                                  POS.index(G["jogadores"][p]["pos"]),
                                  -rendimento(G["jogadores"][p])))
        auto = escalacao_automatica(G, c)
        titulo("escalacao", "%s %s %s" % (c["formacao"], tr("pt"), c["tatica"]))
        caixa(["Forca de ataque %s   Forca de defesa %s   %s" %
               (cor("%.1f" % at, "ok"), cor("%.1f" % de, "azul"),
                "elenco apto: %d" % sum(1 for p in c["elenco"] if disponivel(G, p))),
               "Escalacao %s" % (cor("AUTOMATICA - a maquina monta o melhor time toda semana", "ok")
                                 if auto else
                                 cor("MANUAL - o time so muda quando voce mexe", "av"))])
        linhas = []
        for i, (pid, vaga) in enumerate(atribuir_vagas(G, esc, form, vagas_manuais(c)), 1):
            j = G["jogadores"][pid]
            if vaga == j["pos"]:
                marca = j["pos"]
                obs = situacao(G, j)
            else:
                marca = cor("%s>%s" % (j["pos"], vaga), "av")
                obs = cor("improvisado (%d%%)" % int(AFINIDADE[j["pos"]][vaga] * 100), "av")
            linhas.append((i, marca, j["nome"][:20], j["idade"],
                           cor(str(j["ovr"]), cor_ovr(j["ovr"])), j["cond"], j["forma"],
                           j["moral"], barra(j["cond"], 8), obs))
        cols = [("#", 3, ">"), ("VAGA", 8, "<"), ("TITULAR", 20, "<"), ("IDA", 3, ">"),
                ("OVR", 3, ">"), ("FIS", 3, ">"), ("FOR", 3, ">"), ("MOR", 3, ">"),
                ("CONDICAO", 8, "<"), ("SITUACAO", 16, "<")]
        tabela(cols, linhas)
        print(cor("\nBANCO E RESERVAS", "fraco"))
        cols_banco = [("#", 3, ">"), ("POS", 8, "<"), ("RESERVA", 20, "<"), ("IDA", 3, ">"),
                      ("OVR", 3, ">"), ("FIS", 3, ">"), ("FOR", 3, ">"), ("MOR", 3, ">"),
                      ("CONDICAO", 8, "<"), ("SITUACAO", 16, "<")]
        linhas = []
        for i, pid in enumerate(resto, 12):
            j = G["jogadores"][pid]
            linhas.append((i, j["pos"], j["nome"][:20], j["idade"],
                           cor(str(j["ovr"]), cor_ovr(j["ovr"])), j["cond"], j["forma"],
                           j["moral"], barra(j["cond"], 8), situacao(G, j)))
        tabela(cols_banco, linhas)
        print()
        caixa(["%s digite dois numeros para trocar (ex: 9 15)" % tr("seta"),
               "%s [a] %s   [f] formacao   [t] tatica   [enter] voltar"
               % (tr("seta"), "voltar para manual" if auto else "ligar escalacao automatica")])
        cmd = ler("> ", G).strip().lower()
        if cmd in ("", "0", "v"):
            return
        if cmd == "a":
            ligada = definir_escalacao_automatica(G, not auto)
            print(cor("Escalacao automatica LIGADA. A maquina monta o time toda semana."
                      if ligada else
                      "Escalacao automatica DESLIGADA. O time agora e seu.", "ok"))
            continue
        if cmd == "f":
            ops = list(FORMACOES)
            for i, f in enumerate(ops, 1):
                d = FORMACOES[f]
                print("%2d %-9s %s" % (i, f, " ".join("%s%d" % (k, v) for k, v in d.items())))
            k = ler_int("Formacao: ", G, 1, len(ops))
            if k:
                c["formacao"] = ops[k - 1]
                c["escalacao"] = auto_escalar(G, c)
                c["esc_stamp"] = ""
            continue
        if cmd == "t":
            ops = list(TATICAS)
            for i, t in enumerate(ops, 1):
                ma, md = TATICAS[t]
                print("%2d %-16s ataque x%.2f  defesa x%.2f" % (i, t, ma, md))
            k = ler_int("Tatica: ", G, 1, len(ops))
            if k:
                c["tatica"] = ops[k - 1]
            continue
        partes = cmd.replace(",", " ").split()
        if len(partes) == 2 and all(p.isdigit() for p in partes):
            a, b = int(partes[0]), int(partes[1])
            todos = esc + resto
            if not (1 <= a <= len(todos) and 1 <= b <= len(todos)):
                print(cor("Numero fora da lista.", "av"))
                continue
            pa, pb = todos[a - 1], todos[b - 1]
            for p in (pa, pb):
                if not disponivel(G, p):
                    print(cor("%s nao tem condicao de jogar." % G["jogadores"][p]["nome"], "av"))
                    break
            else:
                nova = esc[:]
                if pa in nova and pb in nova:
                    i1, i2 = nova.index(pa), nova.index(pb)
                    nova[i1], nova[i2] = nova[i2], nova[i1]
                elif pa in nova:
                    nova[nova.index(pa)] = pb
                elif pb in nova:
                    nova[nova.index(pb)] = pa
                else:
                    print(cor("Escolha pelo menos um titular.", "av"))
                    continue
                if auto:
                    definir_escalacao_automatica(G, False)
                    print(cor("Voce mexeu no time: a escalacao automatica foi desligada.", "av"))
                c["escalacao"] = nova
                c["esc_stamp"] = ""
            continue
        print(cor("Nao entendi. Use dois numeros, ou a/f/t.", "av"))


# ----------------------------------------------------------------------------
# TABELA, COPAS, ESTATISTICAS
# ----------------------------------------------------------------------------

def tela_tabela(G, div=None):
    div = div or G["clubes"][G["clube"]]["divisao"]
    liga = G["ligas"][div]
    ordem = classificacao(G, liga)
    titulo("classificacao serie " + div, "rodada %d de %d" % (liga["rodada"], len(liga["rodadas"])))
    linhas = []
    for i, cid in enumerate(ordem, 1):
        t = liga["tabela"][str(cid)]
        if i <= 4:
            marca = cor(tr("seta"), "ok")
        elif i > len(ordem) - 4:
            marca = cor("x", "ruim")
        else:
            marca = " "
        nome = G["clubes"][cid]["nome"][:22]
        if cid == G["clube"]:
            nome = cor(nome, "neg")
        linhas.append((marca, i, nome, t["p"], t["j"], t["v"], t["e"], t["d"],
                       t["gp"], t["gc"], t["gp"] - t["gc"]))
    tabela([("", 1, "<"), ("", 2, ">"), ("CLUBE", 22, "<"), ("P", 3, ">"), ("J", 3, ">"),
            ("V", 3, ">"), ("E", 3, ">"), ("D", 3, ">"), ("GP", 3, ">"), ("GC", 3, ">"),
            ("SG", 4, ">")], linhas)
    print(cor("%s acesso ou titulo   x rebaixamento" % tr("seta"), "fraco"))


def tela_copas(G):
    titulo("copas")
    for chave, cp in G["copas"].items():
        if cp["campeao"]:
            print("%-16s campeao: %s" % (cp["nome"], cor(G["clubes"][cp["campeao"]]["nome"], "des")))
            continue
        n = len(cp["vivos"]) + len(cp.get("espera", []))
        vivo = cor(" [seu clube segue vivo]", "ok") if vivo_na_copa(cp, G["clube"]) else ""
        prox = proxima_semana_copa(cp)
        print("%-16s %s, %d clubes%s%s" % (cp["nome"], fase_da_copa(cp), n, vivo,
                                           cor("  proxima fase na semana %d" % prox, "fraco") if prox else ""))


def tela_base(G):
    """A academia no modo linha: quem tem, quem esta pronto, quem sobe."""
    c = G["clubes"][G["clube"]]
    garotos = elenco_base(G, c)
    titulo("categorias de base",
           "academia nivel %d %s %d de %d vagas %s bolsa %s por semana"
           % (c["base"], tr("pt"), len(garotos), vagas_base(c), tr("pt"),
              din(custo_base(G, c))))
    if not garotos:
        print(cor("Academia vazia. A safra nova chega na virada da temporada.", "av"))
        print(cor("Suba o nivel da base na Infraestrutura para formar mais gente.", "fraco"))
        return
    foco = foco_treino(G, c)
    tabela([("#", 3, ">"), ("POS", 3, "<"), ("JOGADOR", 20, "<"), ("IDA", 3, ">"),
            ("OVR", 3, ">"), ("TETO", 7, "<"), ("BOLSA", 10, ">"), ("SITUACAO", 22, "<")],
           [(i, j["pos"], j["nome"][:20], j["idade"], cor(str(j["ovr"]), cor_ovr(j["ovr"])),
             scout(G, j), din(j["salario"]),
             ("em treino individual" if j["id"] in foco else "") or
             ("aos 20 sobe ou sai" if j["idade"] >= IDADE_BASE_MAX else
              ("pronto para subir" if pronto_para_subir(G, c, j) else "ainda cru")))
            for i, j in enumerate(garotos, 1)])
    print(cor("Garoto de base nao joga e nao entra no mercado enquanto nao subir.", "fraco"))
    op = ler("(s)ubir, (l)iberar, (t)reino individual, (f)icha, enter volta: ", G).lower()
    if not op or op[0] not in "sltf":
        return
    k = ler_int("Numero do garoto (0 cancela): ", G, 0, len(garotos))
    if not k:
        return
    j = garotos[k - 1]
    if op[0] == "f":
        ficha_completa(G, j)
    elif op[0] == "s":
        print(cor(promover_da_base(G, j["id"])[1], "ok"))
    elif op[0] == "l":
        if ler("Liberar %s de vez? (s/n) " % j["nome"], G).lower().startswith("s"):
            print(cor(dispensar_da_base(G, j["id"])[1], "av"))
    else:
        print(cor(alternar_foco(G, c, j["id"])[1], "ok"))


def tela_treino(G):
    """Regime da semana e trabalho individual."""
    c = G["clubes"][G["clube"]]
    foco = foco_treino(G, c)
    titulo("treino", "regime atual: %s %s CT nivel %d %s %d de %d em trabalho individual"
           % (c["treino"], tr("pt"), c["ct"], tr("pt"), len(foco), vagas_treino(c)))
    nomes = list(REGIMES_TREINO)
    tabela([("#", 3, ">"), ("REGIME", 14, "<"), ("EVOLUCAO", 9, ">"), ("JOVEM", 7, ">"),
            ("VETERANO", 9, ">"), ("FISICO", 7, ">"), ("LESAO", 7, ">"), ("", 40, "<")],
           [(i, nome + (" *" if nome == c["treino"] else ""),
             "%+d%%" % round((r["evo"] - 1) * 100), "%+d%%" % round((r["jovem"] - 1) * 100),
             "%+d%%" % round((r["veterano"] - 1) * 100), "%+d" % r["cond"],
             "%+d%%" % round((r["lesao"] - 1) * 100), r["desc"][:40])
            for i, (nome, r) in enumerate(((n, REGIMES_TREINO[n]) for n in nomes), 1)])
    if foco:
        print(cor("\nEm trabalho individual (%s por semana):" % din(custo_treino(c)), "fraco"))
        for pid in foco:
            j = G["jogadores"].get(pid)
            if j:
                print("   %-22s %s %2d anos  ovr %2d  teto %s  %s"
                      % (j["nome"], j["pos"], j["idade"], j["ovr"], scout(G, j),
                         "base" if da_base(j) else ""))
    op = ler("\n(r)egime, (t)reino individual, enter volta: ", G).lower()
    if not op:
        return
    if op[0] == "r":
        k = ler_int("Numero do regime (0 cancela): ", G, 0, len(nomes))
        if k:
            print(cor(definir_regime(G, c, nomes[k - 1])[1], "ok"))
        return
    if op[0] != "t":
        return
    candidatos = [G["jogadores"][p] for p in c["elenco"]] + elenco_base(G, c)
    for i, j in enumerate(candidatos, 1):
        marca = " *" if j["id"] in foco else ""
        print("  %2d. %-22s %s %2d anos  ovr %2d  %s%s"
              % (i, j["nome"], j["pos"], j["idade"], j["ovr"],
                 "base" if da_base(j) else "profissional", marca))
    k = ler_int("Ligar/desligar qual? (0 cancela): ", G, 0, len(candidatos))
    if k:
        feito, recado = alternar_foco(G, c, candidatos[k - 1]["id"])
        print(cor(recado, "ok" if feito else "av"))


def tela_tatica(G):
    """Plano de jogo no modo linha: os mesmos cinco botoes da janela."""
    c = G["clubes"][G["clube"]]
    plano = plano_de(c)
    ef = efeitos_plano(c)
    titulo("plano de jogo",
           "%s %s %s %s formacao %s" % (c["tatica"], tr("pt"), c["formacao"],
                                        tr("pt"), c["formacao"]))
    print(cor("   posse %+.0f  volume x%.2f  qualidade x%.2f  entrega x%.2f  fadiga %+.0f"
              % (ef["posse"] * 100, ef["volume"], ef["qualidade"], ef["concede"],
                 ef["fadiga"]), "fraco"))
    eixos = list(EIXOS_PLANO)
    for i, (eixo, tabela) in enumerate(eixos, 1):
        atual = plano[eixo]
        print("  %d. %-9s %-12s %s" % (i, eixo, atual, tabela[atual]["desc"]))
    k = ler_int("Mudar qual? (0 volta): ", G, 0, len(eixos))
    if not k:
        return
    eixo, tabela = eixos[k - 1]
    opcoes = list(tabela)
    for i, valor in enumerate(opcoes, 1):
        print("     %d. %-12s %s" % (i, valor, tabela[valor]["desc"]))
    e = ler_int("Escolha: ", G, 1, len(opcoes))
    if e:
        print(cor(definir_plano(G, c, eixo, opcoes[e - 1])[1], "ok"))


def tela_estatisticas(G):
    div = G["clubes"][G["clube"]]["divisao"]
    liga = G["ligas"][div]
    art = []
    for cid in liga["times"]:
        for p in G["clubes"][cid]["elenco"]:
            j = G["jogadores"][p]
            if j["g"] or j["a"]:
                art.append((j["g"], j["a"], j["nome"], G["clubes"][cid]["nome"], cid))
    art.sort(key=lambda x: (-x[0], -x[1]))
    titulo("artilharia serie " + div)
    tabela([("#", 3, ">"), ("JOGADOR", 22, "<"), ("CLUBE", 22, "<"), ("GOLS", 5, ">"), ("ASS", 4, ">")],
           [(i, cor(n, "neg") if cid == G["clube"] else n, cl[:22], g, a)
            for i, (g, a, n, cl, cid) in enumerate(art[:20], 1)])
    c = G["clubes"][G["clube"]]
    meus = sorted([G["jogadores"][p] for p in c["elenco"]], key=lambda j: (-j["g"], -j["a"]))[:5]
    print(cor("\nDESTAQUES DO ELENCO", "fraco"))
    for j in meus:
        print("  %-20s %s, %s, %s" % (j["nome"], plural(j["j"], "jogo"), plural(j["g"], "gol"),
                                     plural(j["a"], "assistencia")))
    if c["titulos"]:
        print(cor("\nTitulos: ", "fraco") + ", ".join("%s x%d" % (k, v) for k, v in c["titulos"].items()))


# ----------------------------------------------------------------------------
# FINANCAS, ESTADIO, INFRA
# ----------------------------------------------------------------------------

def tela_financas(G):
    c = G["clubes"][G["clube"]]
    rec, folha, est = receita_semanal(G, c), folha_semanal(G, c), custo_estrutura(c)
    saldo = rec - folha - est
    titulo("financas", c["nome"])
    caixa([
        "Caixa atual                %s" % cor(din(c["dinheiro"]), "ok" if c["dinheiro"] >= 0 else "ruim"),
        "TV e patrocinio            %s por semana" % din(rec),
        "Folha salarial             %s por semana" % cor(din(-folha), "ruim"),
        "Estrutura e operacao       %s por semana" % cor(din(-est), "ruim"),
        "Saldo semanal              %s  (sem contar bilheteria)" %
        cor(din(saldo), "ok" if saldo >= 0 else "ruim"),
    ])
    print("Folha mensal: %s   Preco do ingresso: R$ %d   Capacidade: %s lugares" %
          (din(folha * 4), c["preco"], f"{c['capacidade']:,}".replace(",", ".")))
    if c["obra_semanas"]:
        print(cor("Obra em andamento: +%s lugares, faltam %d semanas." %
                  (f"{c['obra_lugares']:,}".replace(",", "."), c["obra_semanas"]), "av"))
    caros = sorted([G["jogadores"][p] for p in c["elenco"]], key=lambda j: -j["salario"])[:5]
    print(cor("\nMAIORES SALARIOS", "fraco"))
    for j in caros:
        parte = "" if not j.get("dono") else " (emprestado, pagamos %d%%)" % j["emp_pct"]
        print("  %-20s %-4s %s/mes%s" % (j["nome"], j["pos"], din(j["salario"]), parte))


def tela_estadio(G):
    c = G["clubes"][G["clube"]]
    while True:
        titulo("estadio", c["estadio"])
        caixa(["Capacidade %s lugares   Socios %s" %
               (f"{c['capacidade']:,}".replace(",", "."), f"{c['socios']:,}".replace(",", ".")),
               "Preco do ingresso R$ %d   Caixa %s" % (c["preco"], din(c["dinheiro"])),
               "Obra: %s" % ("+%d lugares, faltam %d semanas" % (c["obra_lugares"], c["obra_semanas"])
                             if c["obra_semanas"] else "nenhuma")])
        menu([("1", "Mudar preco do ingresso"), ("2", "Ampliar o estadio"), ("0", "Voltar")])
        op = ler("> ", G)
        if op == "1":
            v = ler_int("Novo preco (R$ 5 a 300): ", G, 5, 300)
            if v:
                c["preco"] = v
                print(cor("Preco atualizado. Caro afasta publico, barato enche o estadio.", "fraco"))
        elif op == "2":
            if c["obra_semanas"]:
                print(cor("Ja existe obra em andamento.", "av"))
                continue
            print("Custo R$ 3.500 por lugar. Prazo de 1 semana a cada 1.500 lugares.")
            v = ler_int("Lugares a adicionar (1000 a 40000): ", G, 1000, 40000)
            if not v:
                continue
            custo = v * 3500
            if custo > c["dinheiro"]:
                print(cor("Caixa insuficiente. Custaria %s." % din(custo), "ruim"))
                continue
            lancar(G, c, -custo, "obras")
            c["obra_lugares"] = v
            c["obra_semanas"] = max(2, v // 1500)
            print(cor("Obra contratada: %s, pronta em %d semanas." % (din(custo), c["obra_semanas"]), "ok"))
        else:
            return


def tela_infra(G):
    c = G["clubes"][G["clube"]]
    while True:
        titulo("infraestrutura")
        caixa(["Centro de treinamento  %s  nivel %d   evolucao dos jogadores" % (barra(c["ct"] * 10), c["ct"]),
               "Categorias de base     %s  nivel %d   crias no fim do ano" % (barra(c["base"] * 10), c["base"]),
               "Departamento medico    %s  nivel %d   menos lesao, recuperacao rapida" % (barra(c["medico"] * 10), c["medico"]),
               "Caixa %s" % din(c["dinheiro"])])
        menu([("1", "Investir no CT"), ("2", "Investir na base"),
              ("3", "Investir no medico"), ("0", "Voltar")])
        op = ler("> ", G)
        mapa = {"1": "ct", "2": "base", "3": "medico"}
        if op not in mapa:
            return
        k = mapa[op]
        if c[k] >= 10:
            print(cor("Ja esta no nivel maximo.", "av"))
            continue
        custo = int((c[k] + 1) ** 2 * 900_000)
        print("Subir para o nivel %d custa %s." % (c[k] + 1, din(custo)))
        if ler("Confirmar? (s/n) ", G).lower().startswith("s"):
            if custo > c["dinheiro"]:
                print(cor("Caixa insuficiente.", "ruim"))
            else:
                lancar(G, c, -custo, "infra")
                c[k] += 1
                print(cor("Investimento feito.", "ok"))



# ----------------------------------------------------------------------------
# MERCADO
# ----------------------------------------------------------------------------

COLS_MERCADO = [("#", 3, ">"), ("POS", 3, "<"), ("JOGADOR", 16, "<"), ("IDA", 3, ">"),
                ("OVR", 3, ">"), ("TETO", 7, "<"), ("CLUBE", 16, "<"),
                ("SALARIO", 9, ">"), ("PEDIDO", 10, ">")]


def linha_mercado(G, j, i):
    clube = G["clubes"][j["clube"]]["nome"][:16] if j["clube"] else "sem clube"
    if j["clube"] is None:
        pedido = cor("livre", "ok")
    elif j["listado"]:
        pedido = cor(din(j["listado"]), "av")     # na vitrine, quer sair
    else:
        valor, intocavel = pedido_efetivo(G, j)
        pedido = cor(din(valor), "ruim") if intocavel else din(valor)
    return (i, j["pos"], j["nome"][:16], j["idade"], cor(str(j["ovr"]), cor_ovr(j["ovr"])),
            scout(G, j), clube, din(j["salario"]), pedido)


def tela_mercado(G):
    c = G["clubes"][G["clube"]]
    while True:
        aberto = mercado_aberto(G)
        pendentes = len([p for p in c["elenco"] if G["jogadores"][p]["listado"]])
        titulo("mercado", "janela %s" % (cor("aberta", "ok") if aberto else cor("fechada", "ruim")))
        caixa(["Caixa %s   Elenco %d jogadores   Folha %s/mes" %
               (cor(din(c["dinheiro"]), "ok" if c["dinheiro"] >= 0 else "ruim"),
                len(c["elenco"]), din(folha_semanal(G, c) * 4)),
               "Janelas: semanas 1 a 4, 19 a 22 e a pre-temporada inteira",
               "Na vitrine: %s seus" % plural(pendentes, "jogador", "jogadores")])
        menu([("1", "Procurar jogador para comprar"),
              ("2", "Agentes livres"),
              ("3", "Buscar jogador por emprestimo"),
              ("4", "Ceder jogador por emprestimo"),
              ("5", "Colocar jogador meu a venda"),
              ("6", "Propostas recebidas"),
              ("7", "Renovar contrato"),
              ("8", "Rescindir contrato"),
              ("9", "Comprar emprestado em definitivo"),
              ("0", "Voltar")])
        op = ler("> ", G)
        if op == "1":
            procurar(G, aberto)
        elif op == "2":
            agentes_livres(G, aberto)
        elif op == "3":
            buscar_emprestimo(G, aberto)
        elif op == "4":
            ceder_emprestimo(G, aberto)
        elif op == "5":
            vitrine(G)
        elif op == "6":
            propostas(G, aberto)
        elif op == "7":
            renovar(G)
        elif op == "8":
            rescindir(G)
        elif op == "9":
            comprar_emprestado(G, aberto)
        else:
            return


def filtros(G):
    print(cor("Deixe em branco para ignorar o filtro.", "fraco"))
    pos = ler("Posicao (GOL/ZAG/LAT/VOL/MEI/ATA): ", G).upper()
    pos = pos if pos in POS else None
    ovr = ler_int("Overall minimo: ", G, 0, 99)
    idade = ler_int("Idade maxima: ", G, 15, 45)
    teto = ler_int("Valor maximo em reais: ", G, 0)
    return pos, ovr, idade, teto


def buscar(G, pos=None, ovr=None, idade=None, teto=None, so_livres=False,
           so_emprestimo=False, limite=25, so_listados=False):
    out = []
    for j in G["jogadores"].values():
        if j["clube"] == G["clube"] or j.get("dono") or da_base(j):
            continue
        if j["clube"] is not None and G["clubes"][j["clube"]]["divisao"] == "EX":
            continue
        if so_livres and j["clube"] is not None:
            continue
        # emprestimo exige dono do outro lado da mesa: agente livre se contrata
        if so_emprestimo and (not j.get("emp_listado") or j["clube"] is None):
            continue
        if so_listados and not j["listado"]:
            continue
        if pos and j["pos"] != pos:
            continue
        if ovr and j["ovr"] < ovr:
            continue
        if idade and j["idade"] > idade:
            continue
        if teto and pedido_efetivo(G, j)[0] > teto:
            continue
        out.append(j)
    out.sort(key=lambda j: (-j["ovr"], j["idade"]))
    return out[:limite]


def procurar(G, aberto):
    pos, ovr, idade, teto = filtros(G)
    lst = buscar(G, pos, ovr, idade, teto)
    if not lst:
        print(cor("Ninguem com esse perfil agora. Afrouxe os filtros.", "av"))
        return
    titulo("jogadores no radar",
           "%d encontrados %s em amarelo, quem o clube quer vender" % (len(lst), tr("pt")))
    tabela(COLS_MERCADO, [linha_mercado(G, j, i) for i, j in enumerate(lst, 1)])
    if not aberto:
        print(cor("Janela fechada: da para observar, mas nao contratar.", "av"))
        return
    k = ler_int("Numero do alvo (0 cancela): ", G, 0, len(lst))
    if not k:
        return
    negociar_compra(G, lst[k - 1])


def negociar_compra(G: Mundo, j: Jogador) -> None:
    """Conduz a mesa. Toda decisao vem de avaliar_clube/avaliar_jogador."""
    c = G["clubes"][G["clube"]]
    ficha(G, j)
    livre = j["clube"] is None
    valor = 0
    if not livre:
        alvo_preco, intocavel = pedido_efetivo(G, j)
        print("%s pede %s pelo passe.%s" %
              (G["clubes"][j["clube"]]["nome"], cor(din(alvo_preco), "neg"),
               cor("  Ele nao esta a venda.", "ruim") if intocavel else ""))
        for _ in range(3):
            oferta = ler_int("Sua oferta pelo passe (0 desiste): ", G, 0)
            if not oferta:
                return
            r = avaliar_clube(G, Proposta(jogador=j["id"], comprador=c["id"], valor=oferta))
            print(cor(r.motivo, "ok" if r.aceita else ("ruim" if r.encerrada else "av")))
            if r.aceita:
                valor = oferta
                break
            if r.encerrada:
                return
        else:
            print(cor("Sem acordo pelo passe.", "ruim"))
            return

    anos = ler_int("Anos de contrato (1 a 5): ", G, 1, 5) or 3
    print("\nAgora o acerto com o jogador. Hoje ele ganha %s por mes." % din(j["salario"]))
    for _ in range(3):
        sal = ler_int("Salario mensal oferecido (0 desiste): ", G, 0)
        if not sal:
            return
        prop = Proposta(jogador=j["id"], comprador=c["id"], valor=valor, salario=sal, anos=anos)
        r = avaliar_jogador(G, prop)
        print(cor(r.motivo, "ok" if r.aceita else ("ruim" if r.encerrada else "av")))
        if r.aceita:
            print(cor("\n" + fechar_compra(G, prop), "ok"))
            return
        if r.encerrada:
            return
    print(cor("Sem acordo salarial.", "ruim"))


def agentes_livres(G, aberto):
    c = G["clubes"][G["clube"]]
    pos = ler("Filtrar posicao (enter para todas): ", G).upper()
    pos = pos if pos in POS else None
    lst = [G["jogadores"][p] for p in G["livres"]]
    if pos:
        lst = [j for j in lst if j["pos"] == pos]
    lst.sort(key=lambda j: -j["ovr"])
    lst = lst[:25]
    if not lst:
        print(cor("Sem agentes livres nesse perfil.", "av"))
        return
    titulo("agentes livres", "sem custo de passe")
    tabela(COLS_MERCADO, [linha_mercado(G, j, i) for i, j in enumerate(lst, 1)])
    if not aberto:
        return
    k = ler_int("Numero do alvo (0 cancela): ", G, 0, len(lst))
    if not k:
        return
    j = lst[k - 1]
    ficha(G, j)
    anos = ler_int("Anos de contrato (1 a 5): ", G, 1, 5) or 2
    for _ in range(3):
        sal = ler_int("Salario mensal oferecido (0 desiste): ", G, 0)
        if not sal:
            return
        prop = Proposta(jogador=j["id"], comprador=c["id"], salario=sal, anos=anos)
        r = avaliar_jogador(G, prop)
        print(cor(r.motivo, "ok" if r.aceita else ("ruim" if r.encerrada else "av")))
        if r.aceita:
            print(cor(fechar_compra(G, prop), "ok"))
            return
        if r.encerrada:
            return


# ----------------------------------------------------------------------------
# EMPRESTIMOS
# ----------------------------------------------------------------------------

def buscar_emprestimo(G, aberto):
    c = G["clubes"][G["clube"]]
    pos = ler("Filtrar posicao (enter para todas): ", G).upper()
    pos = pos if pos in POS else None
    lst = buscar(G, pos=pos, so_emprestimo=True, limite=25)
    if not lst:
        print(cor("Nenhum clube oferecendo jogador por emprestimo agora.", "av"))
        return
    titulo("disponiveis por emprestimo", "voce paga uma fatia do salario ate o fim da temporada")
    tabela([("#", 3, ">"), ("POS", 3, "<"), ("JOGADOR", 18, "<"), ("IDA", 3, ">"),
            ("OVR", 3, ">"), ("TETO", 7, "<"), ("CLUBE", 20, "<"), ("SALARIO", 11, ">")],
           [(i, j["pos"], j["nome"][:18], j["idade"], cor(str(j["ovr"]), cor_ovr(j["ovr"])),
             scout(G, j), G["clubes"][j["clube"]]["nome"][:20], din(j["salario"]))
            for i, j in enumerate(lst, 1)])
    if not aberto:
        print(cor("Janela fechada.", "av"))
        return
    k = ler_int("Numero do alvo (0 cancela): ", G, 0, len(lst))
    if not k:
        return
    j = lst[k - 1]
    dono = G["clubes"][j["clube"]]
    ficha(G, j)
    print("O %s quer dividir o salario de %s por mes." % (dono["nome"], din(j["salario"])))
    opcao = ler_int("Opcao de compra ao fim do emprestimo, em reais (0 = sem opcao): ", G, 0) or 0
    for _ in range(3):
        pct = ler_int("Qual percentual do salario voce banca? (0 desiste): ", G, 0, 100)
        if not pct:
            return
        prop = Proposta(jogador=j["id"], comprador=c["id"], pct_salario=pct,
                        opcao_compra=opcao, tipo=TIPO_EMPRESTIMO)
        r = avaliar_emprestimo(G, prop)
        print(cor(r.motivo, "ok" if r.aceita else ("ruim" if r.encerrada else "av")))
        if r.aceita:
            print(cor(fechar_emprestimo(G, prop), "ok"))
            return
        if r.encerrada:
            return
    print(cor("Sem acordo. O emprestimo nao saiu.", "ruim"))


def ceder_emprestimo(G, aberto):
    c = G["clubes"][G["clube"]]
    if not aberto:
        print(cor("Janela fechada.", "av"))
        return
    print(cor("Ceder um jovem ou reserva alivia a folha e ele volta melhor no fim do ano.", "fraco"))
    j = escolher_do_elenco(G, "Quem voce quer ceder? (0 cancela): ",
                           filtro=lambda x: not x.get("dono"))
    if not j:
        return
    if j["contrato"] <= 0:
        print(cor("Contrato acabando. Renove antes de emprestar.", "av"))
        return
    ofertas = ofertas_emprestimo(G, j)
    if not ofertas:
        print(cor("Nenhum clube demonstrou interesse neste jogador.", "av"))
        return
    titulo("propostas de emprestimo", j["nome"])
    tabela([("#", 3, ">"), ("CLUBE", 24, "<"), ("SERIE", 5, "<"), ("REP", 3, ">"),
            ("ASSUME", 7, ">"), ("SOBRA PRA VOCE", 15, ">")],
           [(i, cl["nome"][:24], cl["divisao"], cl["reputacao"], "%d%%" % pct,
             din(j["salario"] * (100 - pct) // 100))
            for i, (cl, pct) in enumerate(ofertas, 1)])
    k = ler_int("Aceitar qual? (0 nenhuma): ", G, 0, len(ofertas))
    if not k:
        return
    cl, pct = ofertas[k - 1]
    feito, recado = ceder_por_emprestimo(G, j["id"], cl["id"], pct)
    print(cor(recado, "ok" if feito else "ruim"))


# ----------------------------------------------------------------------------
# VENDER, PROPOSTAS, CONTRATOS
# ----------------------------------------------------------------------------

def comprar_emprestado(G: Mundo, aberto: bool) -> None:
    c = G["clubes"][G["clube"]]
    emprestados = [G["jogadores"][p] for p in c["elenco"]
                   if opcao_disponivel(G, G["jogadores"][p], c["id"]) > 0]
    if not emprestados:
        print(cor("Nenhum emprestado seu tem opcao de compra combinada.", "av"))
        return
    if not aberto:
        print(cor("Janela fechada.", "av"))
        return
    for i, j in enumerate(emprestados, 1):
        print("%d. %-22s %s  opcao de compra %s" %
              (i, j["nome"], j["pos"], din(j["emp_opcao"])))
    k = ler_int("Comprar qual? (0 cancela): ", G, 0, len(emprestados))
    if not k:
        return
    print(cor(exercer_opcao(G, emprestados[k - 1]["id"], c["id"]), "ok"))


def vitrine(G):
    j = escolher_do_elenco(G, "Numero do jogador (0 cancela): ",
                           filtro=lambda x: not x.get("dono"))
    if not j:
        return
    if j["listado"]:
        j["listado"] = 0
        print(cor("%s saiu da vitrine." % j["nome"], "ok"))
        return
    ficha(G, j)
    print("Valor de mercado estimado: %s" % cor(din(j["valor"]), "neg"))
    print(cor("Pedir muito acima do valor afasta proposta. Abaixo, elas chegam rapido.", "fraco"))
    v = ler_int("Preco pedido (0 cancela): ", G, 0)
    if not v:
        return
    j["listado"] = v
    print(cor("%s esta na vitrine por %s." % (j["nome"], din(v)), "ok"))


def propostas(G, aberto):
    c = G["clubes"][G["clube"]]
    alvos = [G["jogadores"][p] for p in c["elenco"]
             if G["jogadores"][p]["listado"] and not G["jogadores"][p].get("dono")]
    if not alvos:
        print(cor("Nenhum jogador seu esta na vitrine. Use a opcao 5 primeiro.", "av"))
        return
    ofertas = propostas_recebidas(G)
    if not ofertas:
        print(cor("Nenhuma proposta chegou nesta semana. Talvez o preco esteja alto.", "av"))
        return
    titulo("propostas recebidas", "as mesmas ate a semana virar")
    tabela([("#", 3, ">"), ("JOGADOR", 20, "<"), ("POS", 3, "<"), ("OVR", 3, ">"),
            ("INTERESSADO", 20, "<"), ("OFERTA", 11, ">"), ("VOCE PEDE", 11, ">")],
           [(i, j["nome"][:20], j["pos"], j["ovr"], cl["nome"][:20], din(v), din(j["listado"]))
            for i, (j, cl, v) in enumerate(ofertas, 1)])
    if not aberto:
        print(cor("Janela fechada: as propostas caem se voce nao puder negociar agora.", "av"))
        return
    k = ler_int("Aceitar qual? (0 nenhuma): ", G, 0, len(ofertas))
    if not k:
        return
    j, cl, v = ofertas[k - 1]
    feito, recado = aceitar_oferta(G, j["id"], cl["id"], v)
    print(cor(recado, "ok" if feito else "ruim"))


def renovar(G):
    j = escolher_do_elenco(G, "Quem voce quer renovar? (0 cancela): ",
                           filtro=lambda x: not x.get("dono"))
    if not j:
        return
    ficha(G, j)
    anos = ler_int("Anos de contrato (1 a 5): ", G, 1, 5) or 3
    pedido = exigencia_renovacao(G, j, anos)
    print("Ele pede algo perto de %s por mes por %s." % (cor(din(pedido), "neg"), plural(anos, "ano")))
    for _ in range(3):
        sal = ler_int("Salario oferecido (0 desiste): ", G, 0)
        if not sal:
            return
        prop = Proposta(jogador=j["id"], comprador=G["clube"], salario=sal, anos=anos,
                        tipo=TIPO_RENOVACAO)
        r = avaliar_renovacao(G, prop)
        if r.aceita:
            print(cor(fechar_renovacao(G, prop), "ok"))
            return
        print(cor(r.motivo, "ruim" if r.encerrada else "av"))
        if r.encerrada:
            return
    print(cor(romper_renovacao(G, j), "ruim"))


def rescindir(G):
    j = escolher_do_elenco(G, "Quem voce quer dispensar? (0 cancela): ",
                           filtro=lambda x: not x.get("dono"))
    if not j:
        return
    multa = multa_rescisao(G, j)
    print("Rescindir custa %s de multa e libera %s por mes."
          % (cor(din(multa), "ruim"), din(j["salario"])))
    if not ler("Confirmar? (s/n) ", G).lower().startswith("s"):
        return
    feito, recado = rescindir_contrato(G, j["id"])
    print(cor(recado, "ok" if feito else "ruim"))



# ----------------------------------------------------------------------------
# JOGOS
# ----------------------------------------------------------------------------

def proximo_jogo(G):
    js = jogos_da_semana(G, G["clube"])
    if not js:
        return "semana livre, sem jogo"
    partes = []
    for comp, casa, fora in js:
        if comp == "liga":
            adv = fora if casa == G["clube"] else casa
            ond = "em casa" if casa == G["clube"] else "fora"
            partes.append("%s (%s)" % (G["clubes"][adv]["nome"], ond))
        else:
            cp = G["copas"][comp]
            partes.append("%s %s %s" % (cp["nome"], tr("pt"), fase_da_copa(cp)))
    return (" %s " % tr("pt")).join(partes)


def nome_competicao(G, comp, casa=None):
    """Como a competicao se chama na tela. Unico lugar que sabe disso.

    Precisa aguentar chave que nao e copa: o estadual entrou no calendario e
    tres pontos do codigo quebravam por assumir liga-ou-copa.
    """
    if comp == "liga":
        div = casa["divisao"] if casa else G["clubes"][G["clube"]]["divisao"]
        if div in DIVISOES_BR:
            return "Brasileirao Serie " + div
        return nome_da_liga(G, div)
    if comp == "estadual":
        for est in G.get("estaduais", {}).values():
            if casa is None or casa["id"] in est["times"]:
                return est["nome"]
        return "Estadual"
    cp = G.get("copas", {}).get(comp)
    return cp["nome"] if cp else str(comp)


def relatorio(G, r):
    casa, fora = G["clubes"][r["casa"]], G["clubes"][r["fora"]]
    comp = nome_competicao(G, r["comp"], casa)
    meu_casa = r["casa"] == G["clube"]
    gm, gs = (r["gc"], r["gf"]) if meu_casa else (r["gf"], r["gc"])
    cr = "ok" if gm > gs else ("av" if gm == gs else "ruim")
    placar = "%s  %d %s %d  %s" % (pad(casa["nome"][:24], 24, ">"), r["gc"], "x", r["gf"],
                                   pad(fora["nome"][:24], 24, "<"))
    linhas = [cor(comp, "fraco"), cor(placar, cr)]
    if r["pub"]:
        ocup = r["pub"] / max(1, casa["capacidade"]) * 100
        linhas.append(cor("Publico %s (%.0f%% do estadio)  Renda %s" %
                          (f"{r['pub']:,}".replace(",", "."), ocup, din(r["renda"])), "fraco"))
    caixa(linhas, cr)
    for minuto, lado, tipo, pid, ass in r["eventos"]:
        if tipo != "gol" or pid not in G["jogadores"]:
            continue
        quem = casa["nome"] if lado == 0 else fora["nome"]
        extra = ""
        if ass and ass in G["jogadores"]:
            extra = cor("  assistencia de %s" % G["jogadores"][ass]["nome"], "fraco")
        print("   %2d'  %-22s %s%s" % (minuto, G["jogadores"][pid]["nome"][:22],
                                       cor(quem[:20], "fraco"), extra))
    st = r.get("stats")
    if st:
        print(cor("   posse %d%% x %d%%   finalizacoes %d x %d (%d x %d no gol)   "
                  "escanteios %d x %d"
                  % (st["posse"][0], st["posse"][1], st["chutes"][0], st["chutes"][1],
                     st["no_gol"][0], st["no_gol"][1],
                     st["escanteios"][0], st["escanteios"][1]), "fraco"))
    for minuto, lado, tipo, pid, extra in r["eventos"]:
        if tipo != "substituicao" or pid not in G["jogadores"]:
            continue
        clube = casa if lado == 0 else fora
        if clube["id"] != G["clube"]:
            continue
        sai = G["jogadores"].get(extra)
        print(cor("   %2d'  entra %s, sai %s"
                  % (minuto, G["jogadores"][pid]["nome"],
                     sai["nome"] if sai else "?"), "fraco"))
    notas = r.get("notas") or {}
    xi = (r.get("xi") or {}).get("casa" if meu_casa else "fora") or {}
    meus = [(notas.get(p, 6.0), p, v) for p, v in xi.items() if p in G["jogadores"]]
    if meus:
        meus.sort(reverse=True)
        nota, pid, vaga = meus[0]
        print(cor("   melhor em campo: %s (%s) nota %.1f"
                  % (G["jogadores"][pid]["nome"], vaga, nota), "neg"))
        piores = [m for m in meus if m[0] < 5.5]
        if piores:
            print(cor("   abaixo da media: %s"
                      % ", ".join("%s %.1f" % (G["jogadores"][p]["nome"], n)
                                  for n, p, _v in piores[:3]), "av"))
    if "agregado" in r:
        a, ga, b, gb = r["agregado"]
        print(cor("   agregado: %s %d x %d %s" % (G["clubes"][a]["nome"], ga, gb, G["clubes"][b]["nome"]), "neg"))
    if "penaltis" in r:
        print(cor("   nos penaltis avanca o %s" % G["clubes"][r["penaltis"]]["nome"], "neg"))
    for _, _, tipo, pid, _ in r["eventos"]:
        if pid not in G["jogadores"] or G["jogadores"][pid]["clube"] != G["clube"]:
            continue
        j = G["jogadores"][pid]
        if tipo == "lesao":
            print(cor("   lesao: %s fica fora por %s" % (j["nome"], plural(j["lesao"], "semana")), "ruim"))
        elif tipo == "vermelho":
            print(cor("   cartao vermelho: %s" % j["nome"], "ruim"))
        elif tipo == "amarelo":
            amar = j.get("amar", {}).get(r["comp"], 0)
            if amar == 0 and j["suspensao"] > 0:
                print(cor("   %s pegou o terceiro amarelo e desfalca o time" % j["nome"], "av"))
            elif amar == 2:
                print(cor("   %s esta pendurado (2 amarelos)" % j["nome"], "av"))


def outros_resultados(G):
    div = G["clubes"][G["clube"]]["divisao"]
    liga = G["ligas"][div]
    if liga["rodada"] <= 0:
        return
    print(cor("\nOutros jogos da rodada %d" % liga["rodada"], "fraco"))
    for casa, fora, gc, gf in liga.get("ultimos", []):
        if G["clube"] in (casa, fora):
            continue
        print("   %s %s %d x %d %s %s" % (pad(G["clubes"][casa]["nome"][:22], 22, ">"),
                                          "", gc, gf, "", G["clubes"][fora]["nome"][:22]))


# Quem liga isto e a interface web: a semana 38 encerra a temporada e PARA, e a
# virada (acesso, contratos, idade, ano novo) so acontece no proximo pedido -
# o clique em "Comecar o ano". Terminal e janela tkinter seguem virando na
# mesma chamada, como sempre.
VIRADA_MANUAL = False


def temporada_encerrada(G) -> bool:
    """Todas as rodadas jogadas, virada ainda nao aplicada."""
    return G.get("fase") == "liga" and G["semana"] > SEMANAS_LIGA


def jogar_semana(G):
    # pre-temporada nao tem semana para jogar: avancar dali significa abrir o
    # ano. Sem esta guarda, quem chamasse jogar_semana na entretemporada
    # rodava uma rodada de liga com o calendario ainda zerado.
    if G.get("fase") == "entretemporada":
        iniciar_temporada(G)
        return True
    if G.get("fase") == "estadual":
        est = meu_estadual(G)
        titulo("estadual %s rodada %d" % (tr("pt"), int(G.get("semana_est", 1))),
               est["nome"] if est else "sem estadual neste ano")
        meus = avancar_semana(G)
        for r in meus:
            relatorio(G, r)
        if not meus:
            print(cor("Sem jogo nesta rodada do estadual.", "fraco"))
        if G["fase"] == "liga":
            print(cor("\nEstadual encerrado. O Brasileirao comeca agora.", "neg"))
        salvar_auto(G)
        return True
    if G["semana"] > SEMANAS_LIGA:
        return fim_temporada(G)
    titulo("semana %02d" % G["semana"], proximo_jogo(G))
    meus = avancar_semana(G)
    if not meus:
        print(cor("Sem jogo nesta semana. O elenco descansou e recuperou condicao.", "fraco"))
    for r in meus:
        relatorio(G, r)
    if any(r["comp"] == "liga" for r in meus):
        outros_resultados(G)
    if salvar_auto(G):
        print(cor("\n  progresso salvo automaticamente em %s" % os.path.basename(SAVE), "fraco"))
    else:
        print(cor("\n  nao consegui salvar sozinho. Use a opcao Salvar do menu.", "av"))
    if G["semana"] > SEMANAS_LIGA and not VIRADA_MANUAL:
        pausa(G)
        return fim_temporada(G)
    return True


# ----------------------------------------------------------------------------
# HISTORICO DA TEMPORADA
#
# O jogo sabia o placar da semana e esquecia. Agora guarda: cada resultado do
# meu clube entra em placar_hist e o dinheiro do ano em temporada_stats. E
# disso que saem a tira de forma no painel e o resumo do fim do ano - sem
# registro nao ha o que resumir.
#
# Tudo aqui e JSON puro, porque vai para o save junto com o resto.
# ----------------------------------------------------------------------------

LIMITE_PLACARES = 90


def novo_ano_stats(G: Mundo) -> Dict[str, Any]:
    """Zera o caderno do ano. Chamado ao virar a temporada."""
    c = G["clubes"].get(G.get("clube")) if G.get("clube") else None
    G["temporada_stats"] = {
        "temporada": int(G.get("temporada", 0)),
        "caixa_ini": int(c["dinheiro"]) if c else 0,
        "receita": 0, "gasto": 0, "premios": 0, "renda_jogos": 0,
        "vendas": [], "compras": [], "extrato": {}, "jogos_casa": [],
    }
    return G["temporada_stats"]


# O extrato do ano: toda entrada e saida de dinheiro do meu clube, por
# categoria. Soma das categorias = caixa no fim - caixa no comeco (o teste
# test_extrato confere numa temporada inteira). Ordem = ordem da tela.
EXTRATO = (
    ("tv", "Cotas de TV"), ("patrocinio", "Patrocinio"),
    ("patrocinio_bonus", "Bonus de patrocinio"), ("bilheteria", "Bilheteria"),
    ("socios", "Socios"),
    ("premio_liga", "Premiacao da liga"), ("premio_estadual", "Premio do estadual"),
    ("premio_copa", "Premio de copa"), ("premio_grupo", "Vitorias na fase de grupos"),
    ("vendas", "Venda de jogadores"), ("emprestimos", "Taxas de emprestimo"),
    ("folha", "Folha salarial"), ("estrutura", "Estrutura e operacao"),
    ("operacao_jogo", "Operacao dos jogos em casa"),
    ("treino", "Treino individual"), ("peneira", "Peneira da base"),
    ("compras", "Compra de jogadores"), ("rescisoes", "Rescisoes"),
    ("obras", "Obras no estadio"), ("infra", "Infraestrutura"),
    ("credito", "Credito tomado"), ("credito_parcela", "Parcelas do credito"),
    ("imprevistos", "Imprevistos (modo caos)"),
)


# ----------------------------------------------------------------------------
# CREDITO DO CLUBE
#
# Emprestimo financeiro (nao o de jogador): o banco empresta ate 3 meses de
# receita, a 2% ao mes, em parcelas fixas (tabela Price). Uma operacao por vez.
# A parcela sai na virada do mes; sem caixa para ela, atrasa: o juro do mes
# entra no saldo, a parcela ganha 2% de multa, o prazo anda um mes e a
# diretoria cobra na confianca. So o clube do jogador toma credito.
# ----------------------------------------------------------------------------

CREDITO_JUROS = 0.02
CREDITO_MESES_RECEITA = 3
CREDITO_PRAZOS = (6, 12, 24)
CREDITO_MINIMO = 100_000
CREDITO_MULTA = 0.02
CREDITO_CONFIANCA_ATRASO = -4


def receita_mensal(G: Mundo, c: Clube) -> int:
    return int(receita_semanal(G, c) * 4 + bilheteria_mensal_estimada(c))


def credito(G: Mundo) -> Optional[Dict[str, Any]]:
    return G.get("credito") or None


def limite_credito(G: Mundo) -> int:
    c = G["clubes"][G["clube"]]
    if credito(G):
        return 0                       # uma operacao por vez
    return max(0, int(receita_mensal(G, c) * CREDITO_MESES_RECEITA / 1000) * 1000)


def parcela_credito(valor: int, meses: int, juros: float = CREDITO_JUROS) -> int:
    """Parcela fixa da tabela Price."""
    if meses <= 0:
        return int(valor)
    return int(round(valor * juros / (1 - (1 + juros) ** -meses)))


def tomar_credito(G: Mundo, valor: int, meses: int) -> Tuple[bool, str]:
    c = G["clubes"][G["clube"]]
    valor, meses = int(valor), int(meses)
    if credito(G):
        return False, "Ja existe um credito em aberto: quite antes de tomar outro."
    if meses not in CREDITO_PRAZOS:
        return False, "Prazo invalido: %s meses." % " / ".join(str(m) for m in CREDITO_PRAZOS)
    limite = limite_credito(G)
    if valor < CREDITO_MINIMO:
        return False, "O banco nao opera abaixo de %s." % din(CREDITO_MINIMO)
    if valor > limite:
        return False, "O limite do clube e %s (3 meses de receita)." % din(limite)
    parcela = parcela_credito(valor, meses)
    G["credito"] = {"valor": valor, "saldo": valor, "parcela": parcela, "meses": meses,
                    "restantes": meses, "atrasos": 0, "ultimo_atraso": None,
                    "desde": [int(G["temporada"]), semana_absoluta(G)]}
    lancar(G, c, valor, "credito")
    noticia(G, "Credito de %s tomado em %d parcelas de %s." % (din(valor), meses, din(parcela)))
    return True, ("Credito liberado: %s no caixa, %d parcelas de %s por mes (total %s)."
                  % (din(valor), meses, din(parcela), din(parcela * meses)))


def quitar_credito(G: Mundo) -> Tuple[bool, str]:
    cr = credito(G)
    if not cr:
        return False, "Nao ha credito em aberto."
    c = G["clubes"][G["clube"]]
    saldo = int(cr["saldo"])
    if c["dinheiro"] < saldo:
        return False, "Quitar custa %s e o caixa tem %s." % (din(saldo), din(c["dinheiro"]))
    lancar(G, c, -saldo, "credito_parcela")
    G["credito"] = None
    noticia(G, "Credito quitado antes do prazo (%s)." % din(saldo))
    return True, "Credito quitado: %s pagos, sem mais parcelas." % din(saldo)


def pagar_parcela_credito(G: Mundo) -> None:
    """Virada do mes: a parcela sai do caixa, ou atrasa."""
    cr = credito(G)
    if not cr:
        return
    c = G["clubes"][G["clube"]]
    juros = int(cr["saldo"] * CREDITO_JUROS)
    parcela = min(int(cr["parcela"]), int(cr["saldo"]) + juros)
    if c["dinheiro"] >= parcela:
        lancar(G, c, -parcela, "credito_parcela")
        cr["saldo"] = max(0, int(cr["saldo"]) + juros - parcela)
        cr["restantes"] = max(0, int(cr["restantes"]) - 1)
        if cr["restantes"] <= 0 or cr["saldo"] <= 0:
            G["credito"] = None
            noticia(G, "Ultima parcela do credito paga: divida zerada.")
        return
    # sem caixa: atrasa. O juro capitaliza, a multa entra e o prazo anda
    cr["saldo"] = int(cr["saldo"]) + juros + int(cr["parcela"] * CREDITO_MULTA)
    cr["atrasos"] = int(cr.get("atrasos", 0)) + 1
    cr["ultimo_atraso"] = semana_absoluta(G)
    cr["parcela"] = parcela_credito(cr["saldo"], max(1, int(cr["restantes"])))
    noticia(G, "Parcela do credito ATRASADA: sem caixa para %s. Saldo devedor agora %s."
            % (din(parcela), din(cr["saldo"])))


def lancar(G: Mundo, c: Clube, valor: int, categoria: str) -> None:
    """Todo dinheiro que entra ou sai de um clube passa aqui; o do meu clube
    fica no extrato do ano. O caderno e aberto ANTES de mexer no caixa: aberto
    depois, o caixa do comeco ja teria o lancamento e ele contaria duas vezes."""
    if c["id"] == G.get("clube"):
        ex = stats_ano(G).setdefault("extrato", {})
        ex[categoria] = int(ex.get(categoria, 0)) + int(valor)
    c["dinheiro"] += int(valor)


def stats_ano(G: Mundo) -> Dict[str, Any]:
    st = G.get("temporada_stats")
    if not isinstance(st, dict) or st.get("temporada") != int(G.get("temporada", 0)):
        st = novo_ano_stats(G)
    return st


def registrar_negocio(G: Mundo, j: Jogador, origem_id: Optional[int],
                      destino_id: int, valor: int) -> None:
    """Anota compra e venda do meu clube. Chamado de dentro de transferir()."""
    meu = G.get("clube")
    if meu is None or origem_id == destino_id:
        return
    if valor >= NEGOCIO_MANCHETE:
        de = " do %s" % G["clubes"][origem_id]["nome"] if origem_id else ""
        manchete(G, "mercado", "%s contrata %s%s por %s." % (
            G["clubes"][destino_id]["nome"], j["nome"], de, din(valor)))
    st = stats_ano(G)
    if origem_id == meu:
        st["vendas"].append([j["nome"], G["clubes"][destino_id]["nome"], int(valor)])
    elif destino_id == meu:
        nome_origem = G["clubes"][origem_id]["nome"] if origem_id else "sem clube"
        st["compras"].append([j["nome"], nome_origem, int(valor)])


def registrar_placar(G: Mundo, r: Dict[str, Any]) -> None:
    """Guarda um resultado do meu clube: placar, competicao e renda."""
    meu = G.get("clube")
    if meu not in (r["casa"], r["fora"]):
        return
    em_casa = r["casa"] == meu
    gm, gs = (r["gc"], r["gf"]) if em_casa else (r["gf"], r["gc"])
    adv = r["fora"] if em_casa else r["casa"]
    contar_jogo_na_carreira(G, gm, gs)
    hist = G.setdefault("placar_hist", [])
    hist.append([int(G.get("temporada", 0)), int(G.get("semana", 0)), r["comp"],
                 int(adv), int(gm), int(gs), 1 if em_casa else 0])
    del hist[:-LIMITE_PLACARES]
    if em_casa and r.get("renda"):
        st = stats_ano(G)
        st["renda_jogos"] = int(st.get("renda_jogos", 0)) + int(r["renda"])
        st["receita"] = int(st.get("receita", 0)) + int(r["renda"])
        # publico, renda, capacidade e preco de cada jogo em casa: a tela do
        # estadio tira media, ocupacao e o quanto o ingresso esta rendendo
        c = G["clubes"][meu]
        st.setdefault("jogos_casa", []).append(
            [int(r.get("pub", 0)), int(r["renda"]), int(c["capacidade"]), int(c["preco"])])


def placares_da_temporada(G: Mundo, temporada: Optional[int] = None) -> List[List[Any]]:
    alvo = int(temporada if temporada is not None else G.get("temporada", 0))
    return [p for p in G.get("placar_hist", []) if int(p[0]) == alvo]


def forma_recente(G: Mundo, quantos: int = 5) -> List[Tuple[str, str]]:
    """Ultimos resultados como [(V|E|D, texto)], do mais antigo ao mais novo."""
    out = []
    for temp, _sem, comp, adv, gm, gs, casa in G.get("placar_hist", [])[-quantos:]:
        letra = "V" if gm > gs else ("E" if gm == gs else "D")
        nome = G["clubes"][adv]["nome"] if adv in G["clubes"] else "adversario"
        onde = "em casa" if casa else "fora"
        rotulo = "%s %d x %d %s (%s)" % ("casa" if casa else "fora", gm, gs, nome, onde)
        out.append((letra, rotulo))
    return out


def resultados_da_semana(G: Mundo) -> List[Dict[str, Any]]:
    """O que o meu clube jogou na ultima semana processada."""
    return list(G.get("ultimos_meus") or [])


HISTORICO_PARTIDAS = 10     # ultimas partidas do meu clube guardadas no save


def media_nota(j: Jogador) -> Optional[float]:
    """Media de nota no ano; None enquanto nao ha jogo com nota."""
    n = int(j.get("nota_j", 0))
    if n <= 0:
        return None
    return round(j.get("nota_soma", 0.0) / n, 2)


def registro_partida(G: Mundo, r: Dict[str, Any]) -> Dict[str, Any]:
    """A partida em formato de guardar: so listas e nomes, nada de dict com id.

    O retorno de simular tem notas e xi com o id do jogador como chave; o JSON
    transforma essa chave em texto e o id deixa de achar o jogador. Aqui cada
    jogador ja vai com o nome, entao o registro sobrevive ao save, a venda e a
    aposentadoria de quem jogou.
    """
    casa, fora = G["clubes"][r["casa"]], G["clubes"][r["fora"]]

    def nome(pid):
        j = G["jogadores"].get(pid) if pid is not None else None
        return j["nome"] if j else ""

    gols, cartoes, subs, lesoes = [], [], [], []
    for minuto, lado, tipo, pid, extra in r.get("eventos", []):
        if tipo == "gol":
            gols.append([minuto, lado, nome(pid), nome(extra)])
        elif tipo in ("amarelo", "vermelho"):
            ant = cartoes[-1] if cartoes else None
            # o segundo amarelo vem colado no vermelho (mesmo minuto, mesmo
            # jogador): vira um cartao so, "segundo_amarelo", para a tela nao
            # mostrar amarelo e vermelho como se fossem lances diferentes
            if (tipo == "vermelho" and ant and ant[2] == "amarelo" and ant[0] == minuto
                    and ant[1] == lado and ant[3] == nome(pid)):
                ant[2] = "segundo_amarelo"
                continue
            cartoes.append([minuto, lado, tipo, nome(pid)])
        elif tipo == "substituicao":
            subs.append([minuto, lado, nome(pid), nome(extra)])
        elif tipo == "lesao":
            lesoes.append([minuto, lado, nome(pid)])
    notas = r.get("notas") or {}
    linhas = []
    for lado, chave in ((0, "casa"), (1, "fora")):
        for pid, vaga in ((r.get("xi") or {}).get(chave) or {}).items():
            linhas.append([lado, pid, nome(pid), vaga, notas.get(pid, 6.0)])
    melhor = max(linhas, key=lambda x: x[4]) if linhas else None
    if G.get("fase") == "estadual":
        rodada = "Estadual, rodada %d" % max(1, int(G.get("semana_est", 1)))
    else:
        rodada = "Semana %02d" % max(1, int(G.get("semana", 1)))
    reg = {
        "temporada": G["temporada"], "semana_abs": semana_absoluta(G), "rodada": rodada,
        "comp": r.get("comp"), "comp_nome": nome_competicao(G, r.get("comp"), casa),
        "casa": casa["id"], "fora": fora["id"], "casa_nome": casa["nome"], "fora_nome": fora["nome"],
        "eu": 0 if casa["id"] == G["clube"] else 1,
        "gc": r["gc"], "gf": r["gf"], "pub": r.get("pub", 0), "renda": r.get("renda", 0),
        "stats": {k: list(v) for k, v in (r.get("stats") or {}).items()},
        "gols": gols, "cartoes": cartoes, "subs": subs, "lesoes": lesoes,
        # [minuto, lado, mentalidade nova, motivo]: a instrucao condicional em campo
        "instrucoes": [list(x) for x in r.get("instrucoes", [])],
        # notas: [lado, id, nome, vaga, nota] por jogador que entrou em campo
        "notas": linhas,
        "melhor": dict(zip(("lado", "id", "nome", "vaga", "nota"), melhor)) if melhor else None,
    }
    if "agregado" in r:
        a, ga, b, gb = r["agregado"]
        reg["agregado"] = [G["clubes"][a]["nome"], ga, gb, G["clubes"][b]["nome"]]
    if "penaltis" in r:
        reg["penaltis"] = G["clubes"][r["penaltis"]]["nome"]
    return reg


def guardar_historico(G: Mundo, meus: List[Dict[str, Any]]) -> None:
    """Empilha as partidas da semana; fica so com as HISTORICO_PARTIDAS ultimas."""
    if not meus:
        return
    hist = G.setdefault("historico_meus", [])
    hist.extend(registro_partida(G, r) for r in meus)
    del hist[:-HISTORICO_PARTIDAS]


def _normalizar_partida(r: Dict[str, Any]) -> None:
    """Partida crua que passou pelo JSON: id volta a ser int nas chaves."""
    if isinstance(r.get("notas"), dict):
        r["notas"] = {int(k): v for k, v in r["notas"].items()}
    xi = r.get("xi")
    if isinstance(xi, dict):
        for lado in ("casa", "fora"):
            if isinstance(xi.get(lado), dict):
                xi[lado] = {int(k): v for k, v in xi[lado].items()}


# ----------------------------------------------------------------------------
# RESUMO DA TEMPORADA
#
# fim_temporada virou tres coisas, porque a janela precisa das duas primeiras
# separadas do print:
#   apurar_temporada   - le o ano que acabou e devolve o resumo (nao muda nada)
#   encerrar_temporada - aplica a virada e completa o resumo com o que mudou
#   fim_temporada      - o fluxo do terminal: apura, encerra e imprime
# ----------------------------------------------------------------------------

# a selecao do campeonato sai num 4-3-3: goleiro, dois zagueiros, dois
# laterais, um volante, dois meias e tres atacantes
SELECAO_VAGAS = (("GOL", 1), ("ZAG", 2), ("LAT", 2), ("VOL", 1), ("MEI", 2), ("ATA", 3))
REVELACAO_IDADE = 21
# ganho de valor de mercado de quem foi premiado, ate a proxima virada
PREMIO_VALOR = {"melhor": 0.12, "artilheiro": 0.08, "revelacao": 0.10, "selecao": 0.04}


def premios_do_ano(G: Mundo, div: str) -> Optional[Dict[str, Any]]:
    """Melhor jogador, artilheiro, revelacao e selecao de uma divisao.

    Conta quem esta no elenco dos clubes da divisao, com os numeros do ano
    inteiro (liga, estadual e copas). Para melhor, revelacao e selecao vale a
    media de nota, e so entra quem jogou metade das rodadas da liga. Nao muda
    nada no mundo e nao usa o rng: quem aplica e premiar_ano.
    """
    liga = G["ligas"].get(div)
    if not liga or not liga.get("times"):
        return None
    rodadas = max((int(t.get("j", 0)) for t in liga["tabela"].values()), default=0)
    minimo = max(5, (rodadas + 1) // 2)
    todos = []
    for cid in liga["times"]:
        cl = G["clubes"][cid]
        for pid in cl["elenco"]:
            j = G["jogadores"].get(pid)
            if j and not da_base(j) and j.get("j", 0) > 0:
                todos.append((j, cl))
    if not todos:
        return None

    def media(j):
        return media_nota(j) or 0.0

    def melhor_media(j_cl):
        j = j_cl[0]
        return (-media(j), -int(j.get("nota_j", 0)), -j["ovr"], j["id"])

    aptos = sorted((x for x in todos if int(x[0].get("nota_j", 0)) >= minimo), key=melhor_media)

    def linha(j, cl, premio):
        return {"id": j["id"], "nome": j["nome"], "pos": j["pos"], "idade": j["idade"],
                "clube": cl["nome"], "clube_id": cl["id"], "media": media(j),
                "jogos": int(j["j"]), "gols": int(j["g"]), "premio": premio}

    out: Dict[str, Any] = {"divisao": div, "liga": nome_da_liga(G, div), "minimo": minimo,
                           "melhor": None, "artilheiro": None, "revelacao": None, "selecao": []}
    if aptos:
        out["melhor"] = linha(*aptos[0], "melhor")
    art = min(todos, key=lambda x: (-x[0]["g"], x[0]["j"], -media(x[0]), x[0]["id"]))
    if art[0]["g"] > 0:
        out["artilheiro"] = linha(*art, "artilheiro")
    jovens = [x for x in aptos if x[0]["idade"] <= REVELACAO_IDADE]
    if jovens:
        out["revelacao"] = linha(*jovens[0], "revelacao")
    for pos, n in SELECAO_VAGAS:
        da_pos = [x for x in aptos if x[0]["pos"] == pos][:n]
        out["selecao"] += [linha(j, cl, "selecao") for j, cl in da_pos]
    return out


def _rotulo_premio(premio: str, liga: str) -> str:
    return {"melhor": "Melhor jogador da %s", "artilheiro": "Artilheiro da %s",
            "revelacao": "Revelacao da %s", "selecao": "Selecao da %s"}[premio] % liga


def premiar_ano(G: Mundo) -> List[Dict[str, Any]]:
    """Aplica os premios das quatro series (e da liga do meu clube, se for de
    fora): historico no jogador, vitrine no valor e manchete. Tem de rodar
    antes de evoluir_jogadores, que zera os numeros do ano."""
    for j in G["jogadores"].values():
        j.pop("premio_valor", None)
    divs = list(DIVISOES_BR)
    meu = G["clubes"][G["clube"]]["divisao"]
    if meu not in divs:
        divs.append(meu)
    todos = []
    for d in divs:
        p = premios_do_ano(G, d)
        if not p:
            continue
        todos.append(p)
        ganhos = [p[k] for k in ("melhor", "artilheiro", "revelacao") if p[k]] + p["selecao"]
        for g in ganhos:
            j = G["jogadores"][g["id"]]
            j.setdefault("premios", []).append(
                {"temporada": int(G["temporada"]), "nome": _rotulo_premio(g["premio"], p["liga"])})
            j["premio_valor"] = max(float(j.get("premio_valor", 0.0)), PREMIO_VALOR[g["premio"]])
            j["valor"] = valor_jogador(j)
        if d == "A" or d == meu:
            m = p["melhor"]
            if m:
                manchete(G, "premio", "%s, do %s, e o melhor jogador da %s %d (media %.2f)."
                         % (m["nome"], m["clube"], p["liga"], int(G["temporada"]), m["media"]))
            a = p["artilheiro"]
            if a:
                manchete(G, "premio", "%s, do %s, e o artilheiro da %s %d com %s."
                         % (a["nome"], a["clube"], p["liga"], int(G["temporada"]), plural(a["gols"], "gol")))
        if d == meu:
            nossos = [g for g in ganhos if g["clube_id"] == G["clube"]]
            for g in nossos:
                if g["premio"] != "selecao":
                    noticia(G, "%s: %s." % (_rotulo_premio(g["premio"], p["liga"]), g["nome"]))
            na_selecao = [g["nome"] for g in p["selecao"] if g["clube_id"] == G["clube"]]
            if na_selecao:
                noticia(G, "Na selecao da %s: %s." % (p["liga"], ", ".join(na_selecao)))
    return todos


def campanha_na_copa(cp: Dict[str, Any], cid: int) -> Optional[Tuple[str, str]]:
    """(resultado, estado) do clube numa copa, ou None se ele nao jogou.
    estado: "titulo", "ok" (foi longe), "neutro" ou "critico" (caiu cedo)."""
    if cp.get("campeao") == cid:
        return "Campeao", "titulo"
    hist = cp.get("historico") or []
    ultimo = None
    for k, h in enumerate(hist):
        for j in h["jogos"]:
            if cid in (j["a"], j["b"]):
                ultimo = (k, h, j)
    if ultimo:
        k, h, j = ultimo
        if j.get("venc") == cid:
            # passou da ultima fase que o historico tem: segue vivo
            return "Em andamento", "neutro"
        final = cp.get("campeao") is not None and k == len(hist) - 1
        if final or str(h["fase"]).upper() == "FINAL":
            return "Vice-campeao", "ok"
        fase = str(h["fase"])
        estado = "ok" if fase.lower().startswith(("semi", "quartas")) else "critico"
        return "Eliminado %s" % _na_fase(fase.lower()), estado
    if grupo_de(cp, cid) is not None:
        nome = FASE_LIGA if cp.get("formato") == "suico" else FASE_GRUPOS
        if cp.get("grupos_fechados"):
            return "Eliminado na %s" % nome.lower(), "critico"
        return "Em andamento", "neutro"
    if cid in cp.get("vivos", []) or cid in cp.get("espera", []):
        return "Em andamento", "neutro"
    return None


def campanhas_do_ano(G: Mundo, cid: int) -> List[Dict[str, Any]]:
    """Os campeonatos que o clube jogou no ano, com o resultado de cada um:
    liga, estadual e as copas em que ele entrou (nao o mundo inteiro)."""
    c = G["clubes"][cid]
    out = []
    liga = G["ligas"].get(c["divisao"])
    if liga:
        ordem = classificacao(G, liga)
        pos = ordem.index(cid) + 1 if cid in ordem else 0
        nome = "Brasileirao Serie %s" % c["divisao"] if c["divisao"] in DIVISOES_BR else liga["nome"]
        total = len(ordem)
        if pos == 1:
            res, est = "Campeao", "titulo"
        elif c["divisao"] in DIVISOES_BR and c["divisao"] != "A" and pos <= 4:
            res, est = "%do lugar, acesso" % pos, "ok"
        elif tem_rebaixamento(c["divisao"]) and pos > total - 4:
            res, est = "%do lugar, rebaixado" % pos, "critico"
        else:
            res, est = "%do de %d" % (pos, total), "neutro"
        sobe = c["divisao"] in DIVISOES_BR and c["divisao"] != "A" and 0 < pos <= 4
        out.append({"nome": nome, "resultado": res, "estado": est, "tipo": "liga", "acesso": sobe})
    for est_ in estaduais(G).values():
        if cid in est_["times"]:
            txt = campanha_estadual(G, est_, cid)
            estado = ("titulo" if txt == "campeao" else "ok" if txt == "vice-campeao"
                      else "critico" if txt.startswith("eliminado") or "fora do mata" in txt else "neutro")
            out.append({"nome": est_["nome"], "resultado": txt[:1].upper() + txt[1:], "estado": estado,
                        "tipo": "estadual"})
    for chave, cp in (G.get("copas") or {}).items():
        r = campanha_na_copa(cp, cid)
        if r:
            out.append({"nome": cp["nome"], "resultado": r[0], "estado": r[1], "tipo": "copa"})
    return out


def titulos_da_temporada(G: Mundo, cid: int) -> List[str]:
    """Titulos do clube no ano: o que a sala de trofeus ja registrou (estadual,
    copas, supercopas) mais a liga, que so e entregue na virada."""
    temporada = int(G["temporada"])
    nomes = [t["nome"] for t in (G["clubes"][cid].get("titulos_hist") or []) if t["temporada"] == temporada]
    p = passagem_atual(G) if cid == G.get("clube") else None
    for t in (p or {}).get("titulos", []):          # save de antes do titulos_hist
        if t["temporada"] == temporada and t["nome"] not in nomes:
            nomes.append(t["nome"])
    for camp in campanhas_do_ano(G, cid):
        if camp["estado"] == "titulo" and camp["nome"] not in nomes:
            nomes.append(camp["nome"])
    return nomes


def apurar_temporada(G: Mundo) -> Dict[str, Any]:
    """Fecha a conta do ano que acabou. Nao muda nada no mundo."""
    c = G["clubes"][G["clube"]]
    div = c["divisao"]
    liga = G["ligas"][div]
    ordem = classificacao(G, liga)
    pos = (ordem.index(c["id"]) + 1) if c["id"] in ordem else 0
    t = dict(liga["tabela"].get(str(c["id"])) or {})
    alvo = int(G.get("objetivo_alvo", 16))

    # titulos: estadual, copas e liga (antes o estadual nunca entrava)
    titulos_meus = titulos_da_temporada(G, c["id"])
    campanhas = campanhas_do_ano(G, c["id"])
    # so as copas que o clube jogou; antes vinham as ~30 do mundo inteiro
    jogadas = {x["nome"] for x in campanhas if x["tipo"] == "copa"}
    copas = [[cp["nome"], G["clubes"][cp["campeao"]]["nome"]] for cp in G["copas"].values()
             if cp["campeao"] and cp["nome"] in jogadas]

    meus = [G["jogadores"][p] for p in c["elenco"] if p in G["jogadores"]]
    meus += [G["jogadores"][p] for p in c.get("emprestados", []) if p in G["jogadores"]]
    jogaram = [j for j in meus if j.get("j", 0) > 0]
    art = max(jogaram, key=lambda j: (j["g"], j["a"]), default=None)
    gar = max(jogaram, key=lambda j: (j["a"], j["g"]), default=None)
    destaques = sorted(jogaram, key=lambda j: (-(j["g"] + j["a"]), -j["j"]))[:6]
    cresceram = sorted(meus, key=lambda j: -(j["ovr"] - int(j.get("ovr_ini", j["ovr"]))))[:6]

    st = stats_ano(G)
    caixa_ini = int(st.get("caixa_ini", c["dinheiro"]))
    vendido = sum(v[2] for v in st.get("vendas", []))
    comprado = sum(v[2] for v in st.get("compras", []))
    return {
        "temporada": int(G["temporada"]), "clube": c["nome"], "divisao": div,
        "liga": nome_da_liga(G, div), "posicao": pos, "total": len(ordem), "objetivo": G.get("objetivo", ""),
        "alvo": alvo, "objetivo_ok": bool(pos and pos <= alvo),
        "campeao": G["clubes"][ordem[0]]["nome"] if ordem else "",
        "copas": copas, "titulos": titulos_meus, "campanhas": campanhas,
        "campanha": {"j": t.get("j", 0), "v": t.get("v", 0), "e": t.get("e", 0),
                     "d": t.get("d", 0), "gp": t.get("gp", 0), "gc": t.get("gc", 0),
                     "p": t.get("p", 0)},
        "artilheiro": [art["nome"], art["g"], art["j"]] if art and art["g"] else None,
        "garcom": [gar["nome"], gar["a"], gar["j"]] if gar and gar["a"] else None,
        "destaques": [[j["nome"], j["pos"], j["j"], j["g"], j["a"]] for j in destaques],
        "evolucao": [[j["nome"], j["ovr"] - int(j.get("ovr_ini", j["ovr"])), j["ovr"]]
                     for j in cresceram if j["ovr"] - int(j.get("ovr_ini", j["ovr"])) > 0],
        "financas": {"caixa_ini": caixa_ini, "caixa_fim": int(c["dinheiro"]),
                     "receita": int(st.get("receita", 0)), "gasto": int(st.get("gasto", 0)),
                     "premios": 0, "renda_jogos": int(st.get("renda_jogos", 0)),
                     "vendido": int(vendido), "comprado": int(comprado)},
        "vendas": [list(v) for v in st.get("vendas", [])],
        "compras": [list(v) for v in st.get("compras", [])],
        "premios_ano": premios_do_ano(G, div),
        # o extrato por categoria (a virada completa com a premiacao da liga)
        "extrato": dict(st.get("extrato", {})),
        # completados por encerrar_temporada
        "diretoria": "", "diretoria_ok": True, "movimento": None,
        "tetos": [], "safra": [], "base_subiu": [], "base_saiu": [],
        "voltando": [], "saindo": [], "aposentados": [], "fim_contrato": [],
    }


def encerrar_temporada(G: Mundo, resumo: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Aplica a virada de ano e completa o resumo. Devolve (continua, resumo).

    continua=False significa demitido: quem chamou decide como oferecer outro
    clube (o terminal usa trocar_de_clube; a janela troca a funcao por um
    dialogo antes de chegar aqui).
    """
    c = G["clubes"][G["clube"]]
    div_antes = c["divisao"]
    pos_final = resumo["posicao"]
    campeao = classificacao(G, G["ligas"][div_antes])[0]

    for d in "ABCD":
        cid = classificacao(G, G["ligas"][d])[0]
        cl = G["clubes"][cid]
        chave = "Brasileirao Serie " + d
        dar_titulo(G, cl, chave)
    fechar_ligas_ext(G)
    if modo_caos(G):
        soltar_presos(G)
    G["historico"].append("%d %s %s: campeao %s %s %s terminou em %do" %
                          (G["temporada"], tr("pt"), nome_da_liga(G, div_antes), G["clubes"][campeao]["nome"],
                           tr("pt"), c["nome"], pos_final))

    caixa_antes = c["dinheiro"]
    premiacao(G)
    resumo["financas"]["premios"] = int(c["dinheiro"] - caixa_antes)
    resumo["financas"]["caixa_fim"] = int(c["dinheiro"])
    resumo["extrato"] = dict(stats_ano(G).get("extrato", {}))
    investimentos_ia(G)
    ia_demite_tecnicos(G, fim_de_ano=True)

    ok, msg = avaliar_diretoria(G, pos_final)
    resumo["diretoria"], resumo["diretoria_ok"] = msg, bool(ok)

    for cid, de, para in acesso_rebaixamento(G):
        if cid == G["clube"]:
            subiu = "ABCD".index(para) < "ABCD".index(de)
            resumo["movimento"] = ["acesso" if subiu else "rebaixamento", de, para]

    # a sala de trofeus guarda a temporada; a reputacao do treinador anda
    marco(G, "%do lugar na %s, meta %s" % (
        pos_final, nome_da_liga(G, div_antes), "cumprida" if resumo["objetivo_ok"] else "nao cumprida"))
    mexer_rep_tecnico(G, 6 if resumo["objetivo_ok"] else -5)
    fechar_ano_patrocinio(G, c, resumo)
    if resumo["movimento"]:
        tipo, de, para = resumo["movimento"]
        marco(G, ("Acesso da Serie %s para a %s" if tipo == "acesso"
                  else "Rebaixamento da Serie %s para a %s") % (de, para))
        mexer_rep_tecnico(G, 5 if tipo == "acesso" else -6)

    # antes de devolver os emprestados: o premio e de quem jogou por aqui
    premios = premiar_ano(G)
    resumo["premios_ano"] = next((p for p in premios if p["divisao"] == div_antes), None)

    resumo["voltando"] = [G["jogadores"][p]["nome"] for p in c.get("emprestados", [])
                          if p in G["jogadores"]]
    resumo["saindo"] = [G["jogadores"][p]["nome"] for p in c["elenco"]
                        if G["jogadores"][p].get("dono")]
    devolver_todos(G)

    # o teto se corrige ANTES de evoluir_jogadores, que e quem zera as
    # estatisticas do ano em que a revisao se baseia
    for pid, d in revisar_potenciais(G):
        j = G["jogadores"].get(pid)
        if j:
            resumo["tetos"].append([j["nome"], int(d), int(j["pot"])])

    antes_do_ano = {p: G["jogadores"][p]["nome"] for p in c["elenco"] if p in G["jogadores"]}
    usados = set(j["nome"] for j in G["jogadores"].values())
    evoluir_jogadores(G)
    resumo["aposentados"] = [n for p, n in antes_do_ano.items() if p not in G["jogadores"]]
    fim_de_contrato(G)

    for cl in G["clubes"].values():
        if cl["divisao"] == "EX":
            continue
        novos = base_gera(G, cl, usados)
        subiram, sairam = resolver_base(G, cl)
        if cl["id"] != G["clube"]:
            promover_base_ia(G, cl)
            continue
        resumo["safra"] = [[j["nome"], j["pos"], j["idade"], j["ovr"]] for j in novos]
        resumo["base_subiu"], resumo["base_saiu"] = subiram, sairam
    repor_elencos(G, usados)

    resumo["fim_contrato"] = [G["jogadores"][p]["nome"] for p in c["elenco"]
                              if p in G["jogadores"] and G["jogadores"][p]["contrato"] <= 0
                              and not G["jogadores"][p].get("dono")]

    G["temporada"] += 1
    G["semana"] = 0
    G["fase"] = "entretemporada"
    for d in DIVISOES_BR:
        G["ligas"][d] = nova_liga(G, d)
    montar_copas(G)
    montar_estaduais(G)
    for cl in G["clubes"].values():
        cl["escalacao"] = []
        cl["esc_stamp"] = ""
    for j in G["jogadores"].values():
        j["ovr_ini"] = j["ovr"]
    definir_objetivo(G)
    # ano novo, meta nova: a confianca anda metade do caminho de volta aos 60
    anterior = confianca(G)["valor"]
    reiniciar_confianca(G, round(CONFIANCA_INICIAL + (anterior - CONFIANCA_INICIAL) / 2))
    novo_ano_stats(G)
    # a pre-temporada ja e janela aberta: o que ficou acertado entra agora
    for recado in executar_agendadas(G):
        noticia(G, recado)
    G["ultimo_resumo"] = resumo
    # a virada e a hora do mercado de treinadores: quem foi bem recebe sondagem
    if ok:
        ano_bom = bool(resumo["objetivo_ok"] or resumo["titulos"])
        for _ in range(2):
            sondar_treinador(G, ano_bom=ano_bom)
    return bool(ok), resumo


def liga_do_resumo(r: Dict[str, Any]) -> str:
    """Nome da liga do resumo. Resumo gravado antes do campo "liga" so tem a
    divisao, e "Serie ENG" nao existe."""
    if r.get("liga"):
        return r["liga"]
    div = r.get("divisao", "")
    return "Serie %s" % div if div in DIVISOES_BR else div


def texto_resumo(G: Mundo, r: Dict[str, Any]) -> List[str]:
    """O resumo em linhas de texto. Serve ao terminal e ao log da janela."""
    cam = r["campanha"]
    fin = r["financas"]
    saldo = fin["caixa_fim"] - fin["caixa_ini"]
    linhas = [
        "TEMPORADA %d - %s, %s" % (r["temporada"], r["clube"], liga_do_resumo(r)),
        "Posicao final: %do de %d   (meta era top %d: %s)"
        % (r["posicao"], r["total"], r["alvo"], "cumprida" if r["objetivo_ok"] else "nao cumprida"),
        "Campanha: %d jogos, %dV %dE %dD, %d gols pro e %d contra, %d pontos"
        % (cam["j"], cam["v"], cam["e"], cam["d"], cam["gp"], cam["gc"], cam["p"]),
        "Campeao da %s: %s" % (liga_do_resumo(r), r["campeao"]),
    ]
    for nome, dono in r["copas"]:
        linhas.append("%s: %s" % (nome, dono))
    if r["titulos"]:
        linhas.append("SEUS TITULOS: " + ", ".join(r["titulos"]))
    else:
        linhas.append("Sem titulos nesta temporada.")
    if r["artilheiro"]:
        nome, g, jj = r["artilheiro"]
        linhas.append("Artilheiro do clube: %s, %s em %s" % (nome, plural(g, "gol"), plural(jj, "jogo")))
    if r["garcom"]:
        nome, a, jj = r["garcom"]
        linhas.append("Mais assistencias: %s, %d em %s" % (nome, a, plural(jj, "jogo")))
    pr = r.get("premios_ano")
    if pr:
        for chave, rotulo in (("melhor", "Melhor da liga"), ("artilheiro", "Artilheiro da liga"),
                              ("revelacao", "Revelacao")):
            g = pr.get(chave)
            if g:
                linhas.append("%s: %s (%s)" % (rotulo, g["nome"], g["clube"]))
        nossos = [g["nome"] for g in pr.get("selecao", []) if g["clube"] == r["clube"]]
        if nossos:
            linhas.append("Na selecao do campeonato: " + ", ".join(nossos))
    linhas.append("Caixa: %s -> %s   (%s no ano)"
                  % (din(fin["caixa_ini"]), din(fin["caixa_fim"]),
                     ("+" if saldo >= 0 else "") + din(saldo)))
    linhas.append("Vendas %s em %s   Compras %s em %s   Premiacao %s"
                  % (din(fin["vendido"]), plural(len(r["vendas"]), "negocio"), din(fin["comprado"]),
                     plural(len(r["compras"]), "negocio"), din(fin["premios"])))
    if r["evolucao"]:
        linhas.append("Quem mais cresceu: "
                      + ", ".join("%s +%d (%d)" % tuple(e) for e in r["evolucao"][:4]))
    if r["tetos"]:
        linhas.append("Teto revisado: "
                      + ", ".join("%s %s%d (agora %d)" % (t[0], "+" if t[1] > 0 else "", t[1], t[2])
                                  for t in r["tetos"][:4]))
    if r["safra"]:
        linhas.append("Safra da base: "
                      + ", ".join("%s (%s, %d anos, %d)" % tuple(s) for s in r["safra"]))
    if r["base_subiu"]:
        linhas.append("Subiram ao profissional: " + ", ".join(r["base_subiu"]))
    if r["base_saiu"]:
        linhas.append("Liberados da base: " + ", ".join(r["base_saiu"]))
    if r["aposentados"]:
        linhas.append("Pararam de jogar: " + ", ".join(r["aposentados"]))
    if r["voltando"]:
        linhas.append("Voltam de emprestimo: " + ", ".join(r["voltando"]))
    if r["saindo"]:
        linhas.append("Fim do emprestimo, voltam aos donos: " + ", ".join(r["saindo"]))
    if r["movimento"]:
        tipo, de, para = r["movimento"]
        linhas.append(("ACESSO: seu clube sobe da Serie %s para a Serie %s" % (de, para))
                      if tipo == "acesso" else
                      ("REBAIXAMENTO: seu clube cai da Serie %s para a Serie %s" % (de, para)))
    if r["fim_contrato"]:
        linhas.append("ATENCAO, contrato vencido (saem se voce nao renovar): "
                      + ", ".join(r["fim_contrato"]))
    linhas.append("Diretoria: " + r["diretoria"])
    return linhas


# ----------------------------------------------------------------------------
# FIM DE TEMPORADA
# ----------------------------------------------------------------------------

def fim_temporada(G):
    """Fluxo do terminal. A janela usa apurar/encerrar direto, para poder
    mostrar o resumo em tela antes de deixar o jogador seguir."""
    div_antes = G["clubes"][G["clube"]]["divisao"]
    resumo = apurar_temporada(G)
    titulo("fim da temporada %d" % resumo["temporada"])
    tela_tabela(G, div_antes)
    ok, resumo = encerrar_temporada(G, resumo)
    caixa(texto_resumo(G, resumo), "ok" if resumo["objetivo_ok"] else "av")
    print(cor("\nTemporada %d comeca quando voce mandar. Mercado aberto." % G["temporada"],
              "neg"))
    if not ok:
        return trocar_de_clube(G)
    return True


def trocar_de_clube(G):
    titulo("sem clube")
    cands = [cl for cl in G["clubes"].values()
             if cl["divisao"] in "BCD" and cl["id"] != G["clube"]]
    cands.sort(key=lambda cl: -cl["reputacao"])
    ofertas = rng.sample(cands[:30], min(4, len(cands)))
    tabela([("#", 3, ">"), ("CLUBE", 24, "<"), ("SERIE", 5, "<"), ("REP", 3, ">"),
            ("CAIXA", 12, ">"), ("ELENCO", 6, ">")],
           [(i, cl["nome"][:24], cl["divisao"], cl["reputacao"], din(cl["dinheiro"]), len(cl["elenco"]))
            for i, cl in enumerate(ofertas, 1)])
    print("  0  encerrar a carreira")
    k = ler_int("Escolha: ", G, 0, len(ofertas))
    if k is None and G["auto"]:
        k = 1
    if not k:
        encerrar_passagem(G, "encerrou a carreira")
        titulo("carreira encerrada")
        for h in G["historico"]:
            print("  " + h)
        return False
    assumir_clube(G, ofertas[k - 1]["id"], "demitido")
    print(cor("Novo clube: %s. Objetivo: %s." % (ofertas[k - 1]["nome"], G["objetivo"]), "ok"))
    return True


def iniciar_temporada(G):
    """Abre o ano pelo estadual. O Brasileirao comeca quando ele terminar."""
    for recado in iniciar_estaduais(G):
        print(cor(recado, "av" if "Contrato encerrado" in recado else "ok"))
    meu = meu_estadual(G)
    if meu:
        print(cor("\nTemporada %d comecando pelo %s. Objetivo no Brasileirao: %s."
                  % (G["temporada"], meu["nome"], G["objetivo"]), "neg"))
    else:
        print(cor("\nSeu estado nao tem clubes suficientes para um estadual: o elenco "
                  "descansa ate o Brasileirao.", "av"))


# ----------------------------------------------------------------------------
# SAVE / LOAD
# ----------------------------------------------------------------------------

# Fracao de profissionais com ovr >= t num mundo novo (medida em 2026-09).
# E a curva saudavel: a correcao de save inflado casa percentil com percentil.
CURVA_SAUDAVEL = {93: 0.00005, 92: 0.0001, 91: 0.00021, 90: 0.0003, 89: 0.00063, 88: 0.00115,
                  87: 0.00273, 86: 0.00524, 85: 0.00839, 84: 0.01227, 83: 0.01803, 82: 0.02506,
                  81: 0.03334, 80: 0.04445, 79: 0.05924, 78: 0.07591, 77: 0.09646, 76: 0.12288,
                  75: 0.14846, 74: 0.18096, 73: 0.21556, 72: 0.25645, 71: 0.29367, 70: 0.34148,
                  69: 0.37849, 68: 0.42787, 67: 0.47033, 66: 0.51961, 65: 0.55546, 64: 0.60128,
                  63: 0.63672, 62: 0.6796, 61: 0.71346, 60: 0.74596, 59: 0.77155, 58: 0.80478,
                  57: 0.82544, 56: 0.84431, 55: 0.86297, 54: 0.88237, 53: 0.89799, 52: 0.9135,
                  51: 0.92514, 50: 0.93678}


def corrigir_inflacao(G):
    """Uma vez por save: o motor antigo inflava o mundo inteiro (em 2035 havia
    5.670 profissionais com 70+ contra 3.257 num mundo novo, e dezenas de 99).
    Cada profissional recebe a nota do mesmo percentil na curva saudavel - so
    para baixo - e o teto desce junto, mantendo a folga que ele tinha."""
    if G.get("correcao_notas", 0) >= 2:
        return 0
    pros = sorted((j for j in G["jogadores"].values() if not da_base(j)), key=lambda j: -j["ovr"])
    n = max(1, len(pros))
    faixas = sorted(CURVA_SAUDAVEL.items(), key=lambda kv: -kv[0])
    mexidos = 0
    for r, j in enumerate(pros):
        frac = (r + 1) / n
        alvo = next((t for t, f in faixas if frac <= f), None)
        if alvo is None or alvo >= j["ovr"]:
            continue
        folga = max(0, j["pot"] - j["ovr"])
        j["ovr"] = alvo
        j["pot"] = int(min(TETO_REVISAO + 3, alvo + folga))
        j["salario"] = salario_devido(j)
        j["valor"] = valor_jogador(j)
        mexidos += 1
    for j in G["jogadores"].values():
        if da_base(j) and j["pot"] > 88:
            j["pot"] = int(round(88 + (j["pot"] - 88) * 0.45))
    G["correcao_notas"] = 2
    return mexidos


# ----------------------------------------------------------------------------
# CAPITAO
#
# Todo clube tem um capitao: o escolhido do treinador ou, sem escolha, o mais
# experiente entre os melhores. Na derrota ele segura a moral de quem jogou
# com ele (aplicar_moral). No modo caos ele tambem e alvo de escandalo.
# ----------------------------------------------------------------------------

def capitao_de(G: Mundo, c: Clube) -> Optional[int]:
    """O capitao do clube; sem um valido, escolhe o de sempre (sem rng)."""
    pid = c.get("capitao")
    if pid in c["elenco"] and pid in G["jogadores"] and not G["jogadores"][pid].get("dono"):
        return pid
    cands = [G["jogadores"][p] for p in c["elenco"]
             if p in G["jogadores"] and not G["jogadores"][p].get("dono")
             and not da_base(G["jogadores"][p])]
    if not cands:
        c["capitao"] = None
        return None
    melhor = max(cands, key=lambda j: (j["ovr"] + 0.8 * min(j["idade"], 33), -j["id"]))
    c["capitao"] = melhor["id"]
    return melhor["id"]


def definir_capitao(G: Mundo, pid: int) -> Tuple[bool, str]:
    """O treinador escolhe a braçadeira."""
    j = G["jogadores"].get(pid)
    c = G["clubes"][G["clube"]]
    if j is None or pid not in c["elenco"]:
        return False, "So um jogador do seu elenco pode ser capitao."
    if j.get("dono"):
        return False, "%s esta emprestado: a bracadeira fica com quem e do clube." % j["nome"]
    if da_base(j):
        return False, "Garoto da base nao usa a bracadeira do profissional."
    antigo = c.get("capitao")
    c["capitao"] = pid
    mexer_moral(G, j, 6, "virou o capitao do time")
    if antigo and antigo != pid and antigo in G["jogadores"]:
        mexer_moral(G, G["jogadores"][antigo], -4, "perdeu a bracadeira")
    noticia(G, "%s e o novo capitao do %s." % (j["nome"], c["nome"]))
    return True, "%s agora e o capitao." % j["nome"]


# ----------------------------------------------------------------------------
# MODO CAOS
#
# Carreira alternativa (G["opcoes"]["modo"] == "caos"): toda semana de liga
# pode estourar um plantao no futebol brasileiro - do escandalo que mexe na
# tabela ao absurdo que so vira manchete. Alguns eventos plantam uma
# bomba-relogio (doping, dinheiro ilegal) que so explode temporadas depois,
# com titulo cassado e pontos perdidos. Nada disto roda no modo classico, e o
# rng so e usado aqui dentro do modo caos: a carreira classica nao muda.
# ----------------------------------------------------------------------------

MODOS = {
    "classico": {"nome": "Classico", "desc": "O futebol como ele e: tabela, mercado e diretoria."},
    "caos": {"nome": "Caos", "desc": "Plantoes ao vivo toda semana: tragedias, doping, dinheiro "
                                     "sujo, capitao preso, meteorito no gramado. Nada e seguro."},
}
CHANCE_CAOS = 0.55           # chance de ao menos um plantao por semana de liga
CHANCE_CAOS_DUPLO = 0.18     # e de um segundo na mesma semana
CHANCE_MEU_CLUBE = 0.28      # parte dos eventos que mira o clube do jogador
LIMITE_HISTORIA_CAOS = 80


def modo_caos(G: Mundo) -> bool:
    return (G.get("opcoes") or {}).get("modo") == "caos"


def estado_caos(G: Mundo) -> Dict[str, Any]:
    return G.setdefault("caos", {"pendentes": [], "plantao": [], "historia": [], "usados": {},
                                 "presos": []})


def _br(G: Mundo, divs: str = "ABCD") -> List[Clube]:
    return [c for c in G["clubes"].values() if c["divisao"] in DIVISOES_BR and c["divisao"] in divs]


def _pos_liga(G: Mundo, c: Clube) -> int:
    return posicao_na_liga(G, c["id"])


def _pros(G: Mundo, c: Clube) -> List[Jogador]:
    return [G["jogadores"][p] for p in c["elenco"]
            if p in G["jogadores"] and not da_base(G["jogadores"][p])]


def _nomes_usados(G: Mundo) -> set:
    return {j["nome"] for j in G["jogadores"].values()}


def _remover_do_mundo(G: Mundo, pid: int) -> None:
    """Tira o jogador do jogo de vez (como a aposentadoria faz)."""
    j = G["jogadores"].get(pid)
    if j is None:
        return
    for c in G["clubes"].values():
        for lista in ("elenco", "escalacao", "emprestados", "base_elenco"):
            if pid in c.get(lista, []):
                c[lista].remove(pid)
        if c.get("capitao") == pid:
            c["capitao"] = None
    if pid in G["livres"]:
        G["livres"].remove(pid)
    _esquecer_jogador(G, pid)
    del G["jogadores"][pid]


def _esquecer_jogador(G: Mundo, pid: int) -> None:
    """Propostas, emprestimos oferecidos e acertos que citam quem saiu do jogo
    no meio do ano (a aposentadoria so acontece na virada, quando isso ja esta vazio)."""
    _descartar_oferta(G, pid)
    emp = G.get("emp_ofertas")
    if isinstance(emp, dict) and emp.get("itens"):
        emp["itens"] = [it for it in emp["itens"] if (it[0] if isinstance(it, (list, tuple)) else it.get("id")) != pid]
    G["agendadas"] = [a for a in G.get("agendadas", []) if a.get("jogador") != pid]


def _soltar(G: Mundo, pid: int) -> None:
    """Tira do clube sem apagar do mundo (e sem virar livre)."""
    j = G["jogadores"][pid]
    for c in G["clubes"].values():
        for lista in ("elenco", "escalacao", "emprestados", "base_elenco"):
            if pid in c.get(lista, []):
                c[lista].remove(pid)
        if c.get("capitao") == pid:
            c["capitao"] = None
    if pid in G["livres"]:
        G["livres"].remove(pid)
    _esquecer_jogador(G, pid)
    j["clube"], j["dono"], j["listado"], j["emp_listado"] = None, None, 0, 0


def _completar_elenco(G: Mundo, c: Clube, nivel: float) -> None:
    usados = _nomes_usados(G)
    for pos, minimo in ELENCO_PADRAO.items():
        while conta_posicao(G, c, pos) < minimo:
            j = novo_jogador(G, pos, nivel + rng.uniform(-3, 3), usados)
            j["clube"] = c["id"]
            j["contrato"] = rng.randint(1, 3)
            c["elenco"].append(j["id"])
    c["escalacao"] = auto_escalar(G, c)


def _cassar_titulos(G: Mundo, c: Clube, temporada: int) -> List[str]:
    """Tira do clube (e da sala de trofeus do treinador, se for o meu) o que
    ele ganhou naquela temporada."""
    tirados = [t["nome"] for t in c.get("titulos_hist") or [] if t["temporada"] == temporada]
    c["titulos_hist"] = [t for t in c.get("titulos_hist") or [] if t["temporada"] != temporada]
    for nome in tirados:
        if c["titulos"].get(nome):
            c["titulos"][nome] -= 1
            if c["titulos"][nome] <= 0:
                del c["titulos"][nome]
    for p in carreira(G):
        if p.get("clube_id") == c["id"]:
            p["titulos"] = [t for t in p["titulos"] if int(t["temporada"]) != temporada]
    return tirados


def _tirar_pontos(G: Mundo, c: Clube, pontos: int) -> bool:
    liga = G["ligas"].get(c["divisao"])
    t = liga and liga["tabela"].get(str(c["id"]))
    if not t:
        return False
    t["p"] = int(t["p"]) - pontos
    return True


def _agendar(G: Mundo, semanas: int, tipo: str, **dados: Any) -> None:
    estado_caos(G)["pendentes"].append(dict(dados, tipo=tipo, quando=semana_absoluta(G) + semanas))


def _evento(G: Mundo, c: Optional[Clube], titulo: str, texto: str, gravidade: str = "leve") -> Dict[str, Any]:
    return {"titulo": titulo, "texto": texto, "gravidade": gravidade,
            "clube": c["nome"] if c else "", "meu": bool(c and c["id"] == G.get("clube")),
            "temporada": int(G["temporada"]), "semana": int(G.get("semana", 0))}


def _alvo(G: Mundo, candidatos: List[Clube], meu_pode: bool = True) -> Optional[Clube]:
    """Um clube dos candidatos; as vezes, de proposito, o do jogador."""
    meu = G["clubes"].get(G.get("clube"))
    if meu_pode and meu in candidatos and rng.random() < CHANCE_MEU_CLUBE:
        return meu
    outros = [c for c in candidatos if meu_pode or c["id"] != G.get("clube")]
    return rng.choice(outros) if outros else None


# ------------------------------------------------------------------ eventos
def ev_aviao(G):
    if G["semana"] < 26 or estado_caos(G)["usados"].get("aviao"):
        return None
    lideres_ = [G["clubes"][cid] for d in DIVISOES_BR
                for cid in classificacao(G, G["ligas"][d])[:1] if cid != G.get("clube")]
    if not lideres_:
        return None
    c = rng.choice(lideres_)
    for j in _pros(G, c):
        _remover_do_mundo(G, j["id"])
    subiram = []
    for pid in list(c.get("base_elenco", [])):
        j = G["jogadores"][pid]
        c["base_elenco"].remove(pid)
        j["categoria"] = "pro"
        c["elenco"].append(pid)
        subiram.append(j["nome"])
    _completar_elenco(G, c, 30 + c["reputacao"] * 0.3)
    lancar(G, c, 40_000_000, "imprevistos")
    for j in _pros(G, c):
        mexer_moral(G, j, 20, "luto e reconstrucao")
    return _evento(G, c, "Tragedia no ar",
                   "O aviao do %s, lider da Serie %s, caiu a caminho da rodada %d. O elenco "
                   "profissional nao sobreviveu. So restam os garotos da base (%d subiram as "
                   "pressas) e reforcos de emergencia. O seguro paga R$ 40 mi." %
                   (c["nome"], c["divisao"], G["semana"], len(subiram)), "tragedia")


def ev_doping(G):
    cands = [c for c in _br(G, "AB") if 3 <= _pos_liga(G, c) <= 8 and not c.get("doping")]
    c = _alvo(G, cands, meu_pode=False)
    if not c:
        return None
    boost = {}
    for j in _pros(G, c):
        ganho = rng.randint(5, 8)
        j["ovr"] = min(99, j["ovr"] + ganho)
        boost[str(j["id"])] = ganho
    c["doping"] = {"temporada": int(G["temporada"]), "boost": boost}
    fim = max(1, SEMANAS_LIGA - int(G["semana"]) + 1)
    _agendar(G, fim, "doping_fim", clube=c["id"])
    _agendar(G, fim + rng.randint(2, 3) * (SEMANAS_LIGA + 12), "doping_pego", clube=c["id"],
             temporada=int(G["temporada"]))
    return _evento(G, c, "Arrancada suspeita",
                   "O %s vive uma fase inexplicavel: o elenco inteiro parece outro, mais forte e "
                   "mais rapido. A comissao tecnica fala em 'metodologia nova'. Ninguem pergunta muito." % c["nome"])


def ev_doping_fim(G, p):
    c = G["clubes"].get(p["clube"])
    if not c or not c.get("doping"):
        return None
    for pid, ganho in c["doping"].get("boost", {}).items():
        j = G["jogadores"].get(int(pid))
        if j:
            j["ovr"] = max(20, j["ovr"] - int(ganho))
    c["doping"]["boost"] = {}
    return None


def ev_doping_pego(G, p):
    c = G["clubes"].get(p["clube"])
    if not c:
        return None
    temporada = int(p["temporada"])
    tirados = _cassar_titulos(G, c, temporada)
    multa = int(max(5_000_000, abs(c["dinheiro"]) * 0.25))
    lancar(G, c, -multa, "imprevistos")
    c["reputacao"] = max(5, c["reputacao"] - 8)
    _tirar_pontos(G, c, 15)
    c.pop("doping", None)
    return _evento(G, c, "Escandalo de doping",
                   "Exames guardados de %d confirmam: o %s usou anabolizantes. Perde %s, leva "
                   "multa de %s, perde 15 pontos na tabela atual e 8 de reputacao." %
                   (temporada, c["nome"], ", ".join(tirados) if tirados else "o que conquistou naquele ano",
                    din(multa)), "grave")


def ev_dinheiro_sujo(G):
    cands = [c for c in _br(G, "ABC") if not c.get("dinheiro_sujo")]
    c = _alvo(G, cands, meu_pode=False)
    if not c:
        return None
    valor = int(c["reputacao"] * rng.uniform(1.2, 2.2) * 1_000_000)
    lancar(G, c, valor, "imprevistos")
    c["dinheiro_sujo"] = int(G["temporada"])
    _agendar(G, rng.randint(1, 3) * (SEMANAS_LIGA + 12) + rng.randint(-6, 6), "fair_play", clube=c["id"],
             valor=valor)
    return _evento(G, c, "Investidor misterioso",
                   "Um fundo sem sede conhecida injeta %s no %s. A diretoria nao explica de onde veio: "
                   "'o importante e reforcar o time'." % (din(valor), c["nome"]))


def ev_fair_play(G, p):
    c = G["clubes"].get(p["clube"])
    if not c:
        return None
    multa = int(p.get("valor", 0) * 0.6)
    lancar(G, c, -multa, "imprevistos")
    _tirar_pontos(G, c, 12)
    c["reputacao"] = max(5, c["reputacao"] - 5)
    c.pop("dinheiro_sujo", None)
    return _evento(G, c, "Pego no fair play financeiro",
                   "A investigacao chegou ao fundo que bancou o %s: dinheiro sem origem. Punicao: "
                   "12 pontos a menos, multa de %s e 5 de reputacao." % (c["nome"], din(multa)), "grave")


def ev_capitao_preso(G):
    cands = [c for c in _br(G) if capitao_de(G, c)]
    c = _alvo(G, cands)
    if not c:
        return None
    pid = capitao_de(G, c)
    j = G["jogadores"][pid]
    anos = rng.randint(1, 3)
    _soltar(G, pid)
    estado_caos(G)["presos"].append({"id": pid, "volta": int(G["temporada"]) + anos})
    capitao_de(G, c)
    for o in _pros(G, c):
        mexer_moral(G, o, -8, "o capitao foi preso")
    crime = rng.choice(["traficava na encolha, usando o onibus do clube",
                        "comandava um esquema de rifas falsas com a camisa do time",
                        "vendia ingressos do proprio jogo a preco de final de Copa",
                        "lavava dinheiro de bicheiro numa rede de pastelarias"])
    return _evento(G, c, "Capitao preso",
                   "A policia prendeu %s, capitao do %s, no CT: ele %s. Pegou %s e o contrato foi "
                   "rompido. A bracadeira passa adiante." % (j["nome"], c["nome"], crime, plural(anos, "ano")),
                   "grave")


def soltar_presos(G: Mundo) -> None:
    """Virada do ano no modo caos: quem cumpriu a pena volta como livre."""
    est = estado_caos(G)
    ficam = []
    for p in est["presos"]:
        j = G["jogadores"].get(p["id"])
        if not j:
            continue
        if int(G["temporada"]) >= int(p["volta"]):
            j["ovr"] = max(30, j["ovr"] - 8)
            G["livres"].append(j["id"])
            manchete(G, "caos", "%s cumpriu a pena e procura clube." % j["nome"])
        else:
            ficam.append(p)
    est["presos"] = ficam


def ev_presidente_foge(G):
    cands = [c for c in _br(G) if c["dinheiro"] > 3_000_000]
    c = _alvo(G, cands)
    if not c:
        return None
    levou = int(c["dinheiro"] * rng.uniform(0.6, 0.95))
    lancar(G, c, -levou, "imprevistos")
    destino = rng.choice(["Dubai", "Miami", "um resort no Caribe", "Andorra", "um iate sem bandeira"])
    return _evento(G, c, "Presidente sumiu",
                   "O presidente do %s nao aparece ha tres dias. Nem o caixa: %s sumiram junto. A "
                   "ultima foto dele foi postada de %s." % (c["nome"], din(levou), destino), "grave")


def ev_abandona(G):
    cands = [j for c in _br(G) for j in _pros(G, c) if j["ovr"] >= 68 and j["idade"] <= 30]
    if not cands:
        return None
    meus = [j for j in cands if j["clube"] == G.get("clube")]
    j = rng.choice(meus) if meus and rng.random() < CHANCE_MEU_CLUBE else rng.choice(cands)
    c = G["clubes"][j["clube"]]
    motivo = rng.choice(["ganhou sozinho na Mega-Sena da Virada e comprou uma fazenda de bufalos",
                         "largou tudo para virar cantor de sertanejo universitario",
                         "virou influenciador de cripto e diz que 'futebol e coisa do passado'",
                         "entrou para um mosteiro no Tibete e fez voto de silencio",
                         "decidiu ser astronauta e se inscreveu num programa privado"])
    _remover_do_mundo(G, j["id"])
    return _evento(G, c, "Pendurou as chuteiras",
                   "%s (%d anos, %d de overall), do %s, %s. Nao volta mais." %
                   (j["nome"], j["idade"], j["ovr"], c["nome"], motivo))


def ev_gato(G):
    cands = [j for c in _br(G) for j in _pros(G, c) if j["idade"] <= 21 and j["pot"] - j["ovr"] >= 8]
    if not cands:
        return None
    j = rng.choice(cands)
    c = G["clubes"][j["clube"]]
    real = j["idade"] + rng.randint(9, 13)
    antes = j["idade"]
    j["idade"], j["pot"] = real, j["ovr"]
    j["valor"] = valor_jogador(j)
    mexer_moral(G, j, -30, "a idade verdadeira veio a tona")
    return _evento(G, c, "Gato descoberto",
                   "A promessa %s, do %s, nao tinha %d anos: a certidao verdadeira diz %d. O potencial "
                   "evaporou e o valor despencou." % (j["nome"], c["nome"], antes, real))


def ev_virose(G):
    c = _alvo(G, _br(G))
    if not c:
        return None
    alvos = rng.sample(_pros(G, c), min(len(_pros(G, c)), rng.randint(6, 9)))
    for j in alvos:
        j["lesao"] = max(j["lesao"], rng.randint(1, 3))
    prato = rng.choice(["uma feijoada estragada", "o sushi do rodizio da concentracao",
                        "o bolo de aniversario do roupeiro", "a agua do bebedouro novo"])
    return _evento(G, c, "Surto no elenco",
                   "%d jogadores do %s foram parar no hospital depois de %s. Ficam de 1 a 3 semanas fora." %
                   (len(alvos), c["nome"], prato))


def ev_invasao(G):
    cands = [c for c in _br(G) if _pos_liga(G, c) > len(G["ligas"][c["divisao"]]["times"]) // 2]
    c = _alvo(G, cands)
    if not c:
        return None
    for j in _pros(G, c):
        mexer_moral(G, j, -15, "a torcida invadiu o CT")
    return _evento(G, c, "Invasao no CT",
                   "Torcedores do %s pularam o muro do CT, soltaram rojoes no vestiario e picharam o "
                   "onibus. O elenco esta abalado." % c["nome"])


def ev_xeique(G):
    cands = [c for c in _br(G, "CD")]
    c = _alvo(G, cands)
    if not c:
        return None
    valor = rng.randint(120, 220) * 1_000_000
    lancar(G, c, valor, "imprevistos")
    c["reputacao"] = min(95, c["reputacao"] + 8)
    return _evento(G, c, "Xeique compra o clube",
                   "Um xeique que viu um video do %s no TikTok comprou o clube e depositou %s. Promete "
                   "Libertadores em tres anos." % (c["nome"], din(valor)))


def ev_heranca(G):
    c = _alvo(G, _br(G))
    if not c:
        return None
    valor = rng.randint(15, 60) * 1_000_000
    lancar(G, c, valor, "imprevistos")
    return _evento(G, c, "Heranca de torcedor",
                   "Um torcedor fanatico do %s morreu aos 104 anos e deixou tudo para o clube: %s e "
                   "uma colecao de 3 mil flamulas." % (c["nome"], din(valor)))


def _interditar(G, c, fracao, semanas):
    if c.get("cap_original"):
        return False
    c["cap_original"] = c["capacidade"]
    c["capacidade"] = max(1000, int(c["capacidade"] * fracao))
    _agendar(G, semanas, "estadio_volta", clube=c["id"])
    return True


def ev_estadio_volta(G, p):
    c = G["clubes"].get(p["clube"])
    if c and c.get("cap_original"):
        c["capacidade"] = c.pop("cap_original")
    return None


def ev_interdicao(G):
    c = _alvo(G, [c for c in _br(G) if not c.get("cap_original")])
    if not c or not _interditar(G, c, 0.3, 6):
        return None
    return _evento(G, c, "Estadio interditado",
                   "Um laudo apontou rachaduras na arquibancada do %s. Por 6 semanas, so 30%% da "
                   "capacidade pode entrar." % c["nome"])


def ev_meteoro(G):
    if estado_caos(G)["usados"].get("meteoro", 0) >= 2:
        return None
    c = _alvo(G, [c for c in _br(G) if not c.get("cap_original")])
    if not c or not _interditar(G, c, 0.55, 10):
        return None
    c["reputacao"] = min(95, c["reputacao"] + 3)
    return _evento(G, c, "Meteorito no gramado",
                   "Um meteorito do tamanho de uma geladeira caiu no meio-campo do %s durante a "
                   "madrugada. Ninguem se feriu, a cratera virou ponto turistico e metade do estadio "
                   "fica fechada por 10 semanas." % c["nome"], "grave")


def ev_manipulacao(G):
    c = _alvo(G, _br(G))
    if not c:
        return None
    resto = max(2, SEMANAS_LIGA - int(G["semana"]) + 1)
    alvos = rng.sample(_pros(G, c), min(len(_pros(G, c)), rng.randint(2, 4)))
    for j in alvos:
        j["lesao"] = max(j["lesao"], resto)
    return _evento(G, c, "Esquema de apostas",
                   "A policia descobriu que %s, do %s, forcavam cartoes para apostadores. Afastados ate "
                   "o fim da temporada." % (", ".join(j["nome"] for j in alvos), c["nome"]), "grave")


def ev_prodigio(G):
    meu = G["clubes"].get(G.get("clube"))
    cands = _br(G, "CD")
    c = meu if meu and rng.random() < 0.2 else (rng.choice(cands) if cands else None)
    if not c:
        return None
    j = gerar_cria(G, c, _nomes_usados(G), idade=15)
    j["pot"] = rng.randint(92, 97)
    j["ovr"] = max(j["ovr"], 55)
    j["valor"] = valor_jogador(j)
    return _evento(G, c, "Joia descoberta",
                   "Um olheiro filmou %s, 15 anos, dando caneta em tres zagueiros num campo de terra. Ja "
                   "esta na base do %s. Dizem que e o novo Pele." % (j["nome"], c["nome"]))


def ev_lenda(G):
    j = novo_jogador(G, rng.choice(["MEI", "ATA"]), rng.uniform(74, 80), _nomes_usados(G), idade=41)
    j["nome"] = j["nome"].split()[0] + " o Eterno"
    j["pot"] = j["ovr"]
    j["valor"] = valor_jogador(j)
    G["livres"].append(j["id"])
    return _evento(G, None, "A lenda voltou",
                   "Aos 41 anos, %s desistiu da aposentadoria depois de um sonho. Esta livre no mercado, "
                   "com %d de overall e muita historia pra contar." % (j["nome"], j["ovr"]))


def ev_greve(G):
    cands = [c for c in _br(G) if c["dinheiro"] < 0]
    c = _alvo(G, cands)
    if not c:
        return None
    for j in _pros(G, c):
        mexer_moral(G, j, -25, "salario atrasado")
    return _evento(G, c, "Greve no elenco",
                   "Com o salario atrasado, os jogadores do %s cruzaram os bracos no treino e deram "
                   "entrevista coletiva de oculos escuros." % c["nome"])


def ev_benzedeira(G):
    c = _alvo(G, _br(G))
    if not c:
        return None
    for j in _pros(G, c):
        mexer_moral(G, j, 20, "o trabalho da benzedeira")
    return _evento(G, c, "Trabalho espiritual",
                   "A diretoria do %s trouxe uma benzedeira de Minas, enterrou um sapo atras do gol e "
                   "jura que a zica acabou. O elenco acredita." % c["nome"])


def ev_racha(G):
    c = _alvo(G, _br(G))
    top = sorted(_pros(G, c), key=lambda j: -j["ovr"])[:2] if c else []
    if len(top) < 2:
        return None
    for j in top:
        mexer_moral(G, j, -30, "briga no vestiario")
    motivo = rng.choice(["a vaga no estacionamento", "quem bate o penalti",
                         "uma dancinha de comemoracao", "a playlist do vestiario"])
    return _evento(G, c, "Racha no vestiario",
                   "%s e %s, do %s, sairam no soco por causa de %s. Nenhum dos dois fala com o outro." %
                   (top[0]["nome"], top[1]["nome"], c["nome"], motivo))


def ev_patrocinador(G):
    c = _alvo(G, _br(G, "AB"))
    if not c:
        return None
    if c["id"] == G.get("clube"):
        k = (c.get("patrocinios") or {}).get("master")
        if not k:
            return None
        empresa = k["empresa"]
        c["patrocinios"]["master"] = None
        texto = ("%s, patrocinadora master do %s, faliu da noite para o dia. O espaco na camisa "
                 "esta vago: ha propostas novas em Financas." % (empresa, c["nome"]))
    else:
        perda = int(patrocinio_semanal(G, c) * 6)
        lancar(G, c, -perda, "imprevistos")
        texto = "A casa de apostas que patrocinava o %s faliu e deixou um rombo de %s." % (c["nome"], din(perda))
    return _evento(G, c, "Patrocinador quebrou", texto)


def ev_pastor(G):
    cands = [c for c in _br(G) if capitao_de(G, c)]
    c = _alvo(G, cands)
    if not c:
        return None
    j = G["jogadores"][capitao_de(G, c)]
    _remover_do_mundo(G, j["id"])
    capitao_de(G, c)
    return _evento(G, c, "Chamado divino",
                   "%s, capitao do %s, anunciou no Instagram que recebeu um chamado e largou o futebol "
                   "para abrir uma igreja no bairro onde nasceu." % (j["nome"], c["nome"]))


def ev_sumiu(G):
    cands = [j for c in _br(G) for j in _pros(G, c) if j["ovr"] >= 65]
    if not cands:
        return None
    meus = [j for j in cands if j["clube"] == G.get("clube")]
    j = rng.choice(meus) if meus and rng.random() < CHANCE_MEU_CLUBE else rng.choice(cands)
    c = G["clubes"][j["clube"]]
    j["lesao"] = max(j["lesao"], 4)
    mexer_moral(G, j, -10, "sumiu depois da festa")
    lugar = rng.choice(["Ibiza", "um baile funk em Parada de Lucas", "Las Vegas", "um cruzeiro de pagode"])
    return _evento(G, c, "Desaparecido",
                   "%s, do %s, foi visto pela ultima vez em %s. Reapareceu 4 dias depois dizendo que "
                   "'perdeu o celular'. Fica 4 semanas fora." % (j["nome"], c["nome"], lugar))


def ev_goleiro(G):
    cands = [j for c in _br(G) for j in _pros(G, c) if j["pos"] == "GOL" and j["ovr"] >= 55]
    if not cands:
        return None
    j = rng.choice(cands)
    c = G["clubes"][j["clube"]]
    j["pos"] = "ATA"
    return _evento(G, c, "Goleiro artilheiro",
                   "Depois de fazer tres gols de falta no treino, %s, goleiro do %s, exigiu jogar de "
                   "centroavante. A diretoria cedeu." % (j["nome"], c["nome"]))


def ev_nepotismo(G):
    c = G["clubes"].get(G.get("clube"))
    if not c or c["divisao"] not in DIVISOES_BR or elenco_cheio(G, c):
        return None
    j = novo_jogador(G, "ATA", 34, _nomes_usados(G), idade=19)
    j["nome"] = j["nome"].split()[0] + " Junior"
    j["clube"] = c["id"]
    j["contrato"] = 3
    j["salario"] = 250_000
    c["elenco"].append(j["id"])
    return _evento(G, c, "Filho do presidente",
                   "O presidente contratou o proprio filho, %s (%d de overall), por R$ 250 mil por mes e "
                   "tres anos de contrato. 'Ele tem muito potencial', garantiu." % (j["nome"], j["ovr"]))


def ev_ovni(G):
    c = _alvo(G, _br(G))
    if not c:
        return None
    c["reputacao"] = min(95, c["reputacao"] + 1)
    return _evento(G, c, "Luzes no ceu",
                   "Um objeto luminoso parou 20 minutos sobre o estadio do %s. O jogo foi paralisado, a "
                   "torcida filmou tudo e o clube ja vende a camisa 'eu vi'." % c["nome"])


EVENTOS_CAOS = (
    # (id, peso, funcao)
    ("aviao", 1, ev_aviao), ("doping", 4, ev_doping), ("dinheiro_sujo", 4, ev_dinheiro_sujo),
    ("capitao_preso", 4, ev_capitao_preso), ("presidente_foge", 3, ev_presidente_foge),
    ("abandona", 5, ev_abandona), ("gato", 4, ev_gato), ("virose", 5, ev_virose),
    ("invasao", 4, ev_invasao), ("xeique", 2, ev_xeique), ("heranca", 4, ev_heranca),
    ("interdicao", 3, ev_interdicao), ("meteoro", 1, ev_meteoro), ("manipulacao", 3, ev_manipulacao),
    ("prodigio", 3, ev_prodigio), ("lenda", 2, ev_lenda), ("greve", 3, ev_greve),
    ("benzedeira", 3, ev_benzedeira), ("racha", 4, ev_racha), ("patrocinador", 3, ev_patrocinador),
    ("pastor", 2, ev_pastor), ("sumiu", 4, ev_sumiu), ("goleiro", 2, ev_goleiro),
    ("nepotismo", 2, ev_nepotismo), ("ovni", 2, ev_ovni),
)
BOMBAS_CAOS = {"doping_fim": ev_doping_fim, "doping_pego": ev_doping_pego,
               "fair_play": ev_fair_play, "estadio_volta": ev_estadio_volta}


def _registrar(G: Mundo, ev: Dict[str, Any]) -> None:
    est = estado_caos(G)
    est["plantao"].append(ev)
    est["historia"] = (est["historia"] + [ev])[-LIMITE_HISTORIA_CAOS:]
    manchete(G, "caos", "%s: %s" % (ev["titulo"], ev["texto"]))
    if ev["meu"]:
        noticia(G, "PLANTAO: %s" % ev["texto"])


def eventos_caos(G: Mundo) -> List[Dict[str, Any]]:
    """A semana do modo caos: bombas-relogio vencidas e os plantoes sorteados."""
    est = estado_caos(G)
    est["plantao"] = []
    if not modo_caos(G):
        return []
    agora = semana_absoluta(G)
    ficam = []
    for p in est["pendentes"]:
        if int(p["quando"]) <= agora and p["tipo"] in BOMBAS_CAOS:
            ev = BOMBAS_CAOS[p["tipo"]](G, p)
            if ev:
                _registrar(G, ev)
        else:
            ficam.append(p)
    est["pendentes"] = ficam
    sorteios = 0
    if rng.random() < CHANCE_CAOS:
        sorteios = 2 if rng.random() < CHANCE_CAOS_DUPLO else 1
    for _ in range(sorteios):
        for _tentativa in range(4):
            ident, _peso, func = rng.choices(EVENTOS_CAOS, weights=[e[1] for e in EVENTOS_CAOS])[0]
            ev = func(G)
            if ev:
                est["usados"][ident] = int(est["usados"].get(ident, 0)) + 1
                ev["id"] = ident
                _registrar(G, ev)
                break
    return est["plantao"]


def migrar_prazos(G):
    """Save de antes do contador absoluto: o contador nasce de temporada e
    semana (so precisa crescer daqui para a frente), e proposta e candidato
    ganham o prazo absoluto com o que ainda lhes restava na conta antiga."""
    if "semana_abs" not in G:
        G["semana_abs"] = (max(0, int(G.get("temporada", 2026)) - 2026) * 60
                           + int(G.get("semana_est", 0)) + int(G.get("semana", 0)))
    agora = semana_absoluta(G)

    def converter(item, teto):
        if "vence" in item:
            return
        resta = 0
        if item.get("temporada") == G.get("temporada"):
            resta = int(item.get("expira", 0)) - int(G.get("semana", 0)) + 1
        item["vence"] = agora + int(clamp(resta, 0, teto))
        item.pop("expira", None)

    for o in G.get("propostas_emprego") or []:
        converter(o, PROPOSTA_VALIDADE)
    for c in G.get("clubes", {}).values():
        for k in c.get("base_candidatos") or []:
            converter(k, CANDIDATO_VALE)


def migrar_economia_estrelas(G):
    """Save de antes da curva achatada e do patrocinio novo (2026-09-28), uma
    vez: salario de quem passa de 75 cai na mesma proporcao da curva nova, e
    contrato de patrocinio abaixo do valor novo sobe para a proposta
    equilibrada de hoje (quem ja ganha mais fica como esta)."""
    if G.get("econ_estrelas"):
        return
    G["econ_estrelas"] = True
    for j in G["jogadores"].values():
        if j["ovr"] > SALARIO_JOELHO and j.get("salario"):
            fator = salario_de(j["ovr"]) / _curva_mercado(j["ovr"])
            j["salario"] = int(j["salario"] * fator)
    c = G["clubes"].get(G.get("clube"))
    if c:
        for espaco, k in (c.get("patrocinios") or {}).items():
            if k and espaco in FATIA_PATROCINIO:
                k["semanal"] = max(int(k["semanal"]), int(patrocinio_base(G, c, espaco) * 0.96 / 100) * 100)


def migrar(G):
    ja = {c["nome"] for c in G["clubes"].values() if c["divisao"] == "EX"}
    faltam = [d for d in CLUBES_LIB + CLUBES_SUL if d[0] not in ja]
    if faltam:
        usados = {j["nome"] for j in G["jogadores"].values()}
        G["seq_c"] = max([G.get("seq_c", 0)] + list(G["clubes"]))
        G["seq"] = max([G.get("seq", 0)] + list(G["jogadores"]))
        for dados in faltam:
            novo_clube(G, dados, "EX", usados)
    if G.get("ligas_ext"):
        for codigo, liga in G.pop("ligas_ext").items():
            G["ligas"][codigo] = liga
            for cid in liga["times"]:
                c = G["clubes"].get(cid)
                if c and c["divisao"] == "EX":
                    c["divisao"] = codigo
                    c["dinheiro"] = int(c["reputacao"] ** 2 * 3800 * perfil_liga(codigo)["caixa"])
                    c["europeu"] = codigo in ORDEM_LIGAS_EXT
    if G.get("clube") is not None and G.get("temporada", 2026) > 2027:
        corrigir_inflacao(G)
    else:
        G.setdefault("correcao_notas", 2)
    if falta_mundo(G):
        G["seq_c"] = max([G.get("seq_c", 0)] + list(G["clubes"]))
        G["seq"] = max([G.get("seq", 0)] + list(G["jogadores"]))
        aplicar_mundo(G, {j["nome"] for j in G["jogadores"].values()})
    if any(k not in G["ligas"] for k in CODIGOS_SUL):
        G["seq_c"] = max([G.get("seq_c", 0)] + list(G["clubes"]))
        G["seq"] = max([G.get("seq", 0)] + list(G["jogadores"]))
        montar_ligas_sul(G, {j["nome"] for j in G["jogadores"].values()})
    if G.get("copas") and any(chave_copa_nac(k) not in G["copas"] for k in COPAS_NACIONAIS if k in G["ligas"]):
        montar_copas_nacionais(G, so_faltam=True)
    if G.get("copas") and "intercontinental" not in G["copas"] and \
            not (G.get("fase") == "liga" and G.get("semana", 0) >= SEMANAS_INTERCONTINENTAL[0]):
        G["copas"]["intercontinental"] = nova_intercontinental()
    for j in G["jogadores"].values():
        j.setdefault("dono", None)
        j.setdefault("emp_pct", 100)
        j.setdefault("emp_listado", 0)
        j.setdefault("emp_opcao", 0)
        j.setdefault("pago", 0)
        j.setdefault("desde", 0)
        j.setdefault("ovr_frac", 0.0)
        j.setdefault("j_mes", 0)
        # suspensao virou por competicao e contada em JOGOS, nao em semanas
        if not isinstance(j.get("amar"), dict):
            j["amar"] = {k: 0 for k in COMPETICOES}
            j["amar"]["liga"] = int(j.get("amarelos", 0) or 0)
        if not isinstance(j.get("susp"), dict):
            j["susp"] = {k: 0 for k in COMPETICOES}
            j["susp"]["liga"] = int(j.get("suspensao", 0) or 0)
        for k in COMPETICOES:
            j["amar"].setdefault(k, 0)
            j["susp"].setdefault(k, 0)
        sincronizar_suspensao(j)
    for c in G["clubes"].values():
        c.setdefault("emprestados", [])
        c.setdefault("esc_stamp", "")
        # alavanca da escalacao automatica: save antigo entra com ela ligada,
        # que e o que resolve a escalacao velha apodrecendo depois do mercado
        c.setdefault("auto_esc", True)
    for j in G["jogadores"].values():
        if j["clube"] is None:
            j["emp_listado"] = 0
        j.setdefault("categoria", "pro")
        j.setdefault("g_mes", 0)
        j.setdefault("a_mes", 0)
        j.setdefault("pot_rev", 0)
        j.setdefault("ovr_ini", j["ovr"])
        # save gravado antes deste conserto tem float guardado
        for chave in ("cond", "forma", "moral"):
            if isinstance(j.get(chave), float):
                j[chave] = int(round(j[chave]))
    for c in G["clubes"].values():
        c.setdefault("base_elenco", [])
        c.setdefault("treino", REGIME_PADRAO)
        c.setdefault("treino_foco", [])
        c["plano"] = plano_de(c)
        if c["treino"] not in REGIMES_TREINO:
            c["treino"] = REGIME_PADRAO
    G.setdefault("auto", False)
    G.setdefault("ofertas", {"stamp": "", "itens": []})
    G.setdefault("placar_hist", [])
    G.setdefault("ultimos_meus", [])
    for r in G["ultimos_meus"]:
        _normalizar_partida(r)
    G.setdefault("historico_meus", [])
    meu = G["clubes"].get(G.get("clube")) if G.get("clube") is not None else None
    if meu is not None and "patrocinios" not in meu:
        herdar_patrocinios(G, meu)
    for j in G["jogadores"].values():
        if "nota_j" not in j:
            # save antigo nunca somou nota: comeca a media do zero, sem inventar
            j["nota_soma"], j["nota_j"] = 0.0, 0
    G.setdefault("agendadas", [])
    G.setdefault("semana_est", 0)
    migrar_prazos(G)
    migrar_economia_estrelas(G)
    # save antigo: a marca de cedivel herdada da IA nao faz nada no meu clube
    # (a venda fica: pode ter sido escolha do treinador)
    if G.get("clube") in G.get("clubes", {}) and not G.get("cedivel_limpo"):
        limpar_vitrine_herdada(G, G["clubes"][G["clube"]], a_venda=False)
        G["cedivel_limpo"] = True
    if not isinstance(G.get("emp_ofertas"), dict):
        G["emp_ofertas"] = {"stamp": "", "itens": []}
    if not isinstance(G.get("estaduais"), dict):
        G["estaduais"] = {}
    # save que ja estava em entretemporada entra no ano novo com estadual
    if not G["estaduais"] and G.get("fase") == "entretemporada" and G.get("clube"):
        montar_estaduais(G)
    # estadual sorteado no formato antigo (so pontos corridos) e ainda nao
    # comecado: sorteia de novo, com grupos e mata-mata. Nada jogado se perde.
    elif (G.get("fase") == "entretemporada" and G.get("clube")
          and any("formato" not in e for e in G["estaduais"].values())
          and all(e.get("rodada", 0) == 0 for e in G["estaduais"].values())):
        montar_estaduais(G)
    if not isinstance(G.get("temporada_stats"), dict):
        G["temporada_stats"] = {}
    # save antigo nao tem academia nenhuma: povoa uma vez, senao a tela de base
    # abre vazia e o jogador espera um ano inteiro para ver um garoto
    if G.get("clube") is not None and not any(c.get("base_elenco")
                                              for c in G["clubes"].values()):
        usados = set(j["nome"] for j in G["jogadores"].values())
        for c in G["clubes"].values():
            if c["divisao"] == "EX":
                continue
            for _ in range(rng.randint(4, 7)):
                if len(c["base_elenco"]) < vagas_base(c):
                    gerar_cria(G, c, usados,
                               idade=rng.randint(IDADE_BASE_MIN, IDADE_BASE_MAX - 1))
    return G


def salvar(G, caminho=None):
    # SAVE resolvido na chamada, nao no import: como padrao de argumento ele
    # congelava o caminho e quem trocasse SAVE gravava no arquivo errado
    caminho = caminho or SAVE
    d = dict(G)
    d["clubes"] = {str(k): v for k, v in G["clubes"].items()}
    d["jogadores"] = {str(k): v for k, v in G["jogadores"].items()}
    # json.dumps usa o codificador em C e escreve de uma vez; json.dump(d, f)
    # caia no codificador em Python e fazia milhoes de escritas pequenas - com
    # o save de 8 MB, cada clique que grava custava 600 ms. Grava num .tmp e
    # troca: fechar o jogo no meio nunca deixa um save pela metade.
    texto = json.dumps(d, separators=(",", ":"))
    tmp = caminho + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(texto)
    os.replace(tmp, caminho)
    try:
        with open(caminho_resumo_save(caminho), "w", encoding="utf-8") as f:
            json.dump(resumo_save(G), f)
    except OSError:
        pass           # o resumo e so para o menu: sem ele o save continua valendo
    return caminho


def caminho_resumo_save(caminho):
    return caminho + ".resumo"


def resumo_save(G):
    """O que o menu mostra de um save sem abrir os 8 MB dele."""
    c = G["clubes"].get(G.get("clube")) if G.get("clube") is not None else None
    return {"tecnico": G.get("tecnico") or "Tecnico", "clube": c["nome"] if c else "",
            "divisao": c["divisao"] if c else "", "temporada": G.get("temporada"),
            "semana": G.get("semana"), "modo": (G.get("opcoes") or {}).get("modo", "classico"),
            "titulos": len([t for p in G.get("carreira") or [] for t in p.get("titulos", [])]),
            "salvo_em": time.strftime("%d/%m/%Y %H:%M")}


def ler_resumo_save(caminho):
    """O resumo gravado ao lado do save; sem ele (save antigo), abre o save uma
    vez e grava o resumo para as proximas."""
    try:
        with open(caminho_resumo_save(caminho), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        pass
    try:
        meta = resumo_save(carregar(caminho))
        meta["salvo_em"] = time.strftime("%d/%m/%Y %H:%M", time.localtime(os.path.getmtime(caminho)))
        with open(caminho_resumo_save(caminho), "w", encoding="utf-8") as f:
            json.dump(meta, f)
        return meta
    except Exception:
        return None


def carregar(caminho=None):
    caminho = caminho or SAVE
    with open(caminho, encoding="utf-8") as f:
        d = json.load(f)
    d["clubes"] = {int(k): v for k, v in d["clubes"].items()}
    d["jogadores"] = {int(k): v for k, v in d["jogadores"].items()}
    return migrar(d)


# Janela, navegador e terminal gravam no mesmo save; abertos juntos, um
# sobrescreve o outro. A trava e um lock do sistema operacional num arquivo ao
# lado do save, segurado enquanto o processo vive: morreu, o SO solta sozinho,
# sem trava velha para apagar na mao.
_TRAVA = None


def travar_save(caminho=None):
    """Tenta ser o unico processo mexendo no save. True se conseguiu (ou ja
    tinha), False se outro BRASFUT esta aberto na mesma pasta."""
    global _TRAVA
    if _TRAVA is not None:
        return True
    f = open((caminho or SAVE) + ".lock", "a+")
    try:
        f.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        return False
    _TRAVA = f
    return True


AVISO_TRAVA = ("Ja existe um BRASFUT aberto nesta pasta (janela, navegador ou terminal). "
               "Feche o outro antes: os dois gravariam no mesmo save e um apagaria o outro.")


# ----------------------------------------------------------------------------
# NOVO JOGO
# ----------------------------------------------------------------------------

def escolher_clube(G):
    while True:
        titulo("escolha do clube")
        menu([("1", "Serie A"), ("2", "Serie B"), ("3", "Serie C"), ("4", "Serie D")])
        op = ler("> ", G)
        div = {"1": "A", "2": "B", "3": "C", "4": "D"}.get(op)
        if not div:
            if G["auto"]:
                return [c["id"] for c in G["clubes"].values() if c["divisao"] == "B"][0]
            continue
        times = sorted([c for c in G["clubes"].values() if c["divisao"] == div],
                       key=lambda c: -c["reputacao"])
        titulo("serie " + div)
        tabela([("#", 3, ">"), ("CLUBE", 20, "<"), ("UF", 2, "<"), ("ESTADIO", 20, "<"),
                ("CAPAC.", 7, ">"), ("REP", 3, ">"), ("CAIXA", 11, ">"), ("ELENCO", 6, ">")],
               [(i, c["nome"][:20], c["uf"], c["estadio"][:20],
                 f"{c['capacidade']:,}".replace(",", "."), c["reputacao"],
                 din(c["dinheiro"]), len(c["elenco"]))
                for i, c in enumerate(times, 1)])
        k = ler_int("Numero do clube (0 volta): ", G, 0, len(times))
        if k:
            return times[k - 1]["id"]
        if G["auto"]:
            return times[-1]["id"]


def novo_jogo():
    caixa([cor("BRASFUT %s" % VERSAO, "neg"),
           "Gerenciador de futebol brasileiro. Series A, B, C e D, Copa do Brasil,",
           "Libertadores, Sul-Americana, mercado, emprestimos e estadio.",
           cor("Tudo em texto, nada de imagem.", "fraco")])
    nome = ler("Nome do tecnico: ") or "Tecnico"
    semente = ler("Semente do mundo (enter para aleatorio): ")
    if semente:
        rng.seed(semente)
    G = criar_mundo(nome)
    G["clube"] = escolher_clube(G)
    c = G["clubes"][G["clube"]]
    c["escalacao"] = auto_escalar(G, c)
    definir_objetivo(G)
    titulo("bem-vindo ao " + c["nome"])
    caixa(["Estadio %s, %s lugares" % (c["estadio"], f"{c['capacidade']:,}".replace(",", ".")),
           "Elenco de %d jogadores, media %.1f" % (len(c["elenco"]), media_elenco(G, c)),
           "Caixa %s, folha %s por mes" % (din(c["dinheiro"]), din(folha_semanal(G, c) * 4)),
           cor("Objetivo da diretoria: %s" % G["objetivo"], "av")])
    return G


# ----------------------------------------------------------------------------
# LOOP PRINCIPAL
# ----------------------------------------------------------------------------

MENU_JOGO = [("1", "Avancar semana"), ("2", "Elenco"), ("3", "Escalacao e tatica"),
             ("4", "Classificacao"), ("5", "Copas"), ("6", "Mercado"),
             ("7", "Financas"), ("8", "Estadio"), ("9", "Infraestrutura"),
             ("10", "Estatisticas"), ("11", "Noticias"), ("12", "Base"),
             ("13", "Treino"), ("14", "Plano de jogo"), ("15", "Salvar"),
             ("0", "Sair")]

MENU_PRE = [("1", "Iniciar a temporada"), ("2", "Elenco"), ("3", "Escalacao e tatica"),
            ("4", "Mercado"), ("5", "Infraestrutura"), ("6", "Financas"),
            ("7", "Historico"), ("8", "Base"), ("9", "Treino"), ("10", "Resumo da temporada"),
            ("11", "Salvar"), ("0", "Sair")]


def loop(G):
    while True:
        cabecalho(G)
        pre = G["fase"] == "entretemporada"
        if not pre:
            print(cor("  Proximo: %s" % proximo_jogo(G), "fraco"))
        menu(MENU_PRE if pre else MENU_JOGO)
        op = ler("> ", G).strip()
        if G["auto"] and op == "":
            return
        if pre:
            if op == "1":
                iniciar_temporada(G)
            elif op == "2":
                tela_elenco(G)
            elif op == "3":
                tela_escalacao(G)
            elif op == "4":
                tela_mercado(G)
            elif op == "5":
                tela_infra(G)
            elif op == "6":
                tela_financas(G)
            elif op == "7":
                titulo("historico")
                for h in G["historico"]:
                    print("  " + h)
            elif op == "8":
                tela_base(G)
            elif op == "9":
                tela_treino(G)
            elif op == "10":
                r = G.get("ultimo_resumo")
                if not r:
                    print(cor("Nenhuma temporada encerrada ainda.", "av"))
                else:
                    titulo("resumo da temporada %d" % r["temporada"])
                    caixa(texto_resumo(G, r), "ok" if r["objetivo_ok"] else "av")
            elif op == "11":
                print(cor("Salvo em %s" % salvar(G), "ok"))
            elif op == "0":
                return
            continue
        if op == "1":
            if not jogar_semana(G):
                return
        elif op == "2":
            tela_elenco(G)
        elif op == "3":
            tela_escalacao(G)
        elif op == "4":
            tela_tabela(G)
            d = ler("Ver outra serie? (A/B/C/D ou enter): ", G).upper()
            if d in ("A", "B", "C", "D"):
                tela_tabela(G, d)
        elif op == "5":
            tela_copas(G)
        elif op == "6":
            tela_mercado(G)
        elif op == "7":
            tela_financas(G)
        elif op == "8":
            tela_estadio(G)
        elif op == "9":
            tela_infra(G)
        elif op == "10":
            tela_estatisticas(G)
        elif op == "11":
            titulo("noticias")
            for n in G["noticias"][-15:]:
                print("  " + n)
        elif op == "12":
            tela_base(G)
        elif op == "13":
            tela_treino(G)
        elif op == "14":
            tela_tatica(G)
        elif op == "15":
            print(cor("Salvo em %s" % salvar(G), "ok"))
        elif op == "0":
            if ler("Salvar antes de sair? (s/n) ", G).lower().startswith("s"):
                salvar(G)
                print(cor("Salvo em %s" % SAVE, "ok"))
            return


def simulacao(temporadas, semente="teste"):
    rng.seed(semente)
    G = criar_mundo("Auto")
    G["auto"] = True
    G["clube"] = sorted([c["id"] for c in G["clubes"].values() if c["divisao"] == "B"],
                        key=lambda i: -G["clubes"][i]["reputacao"])[3]
    G["clubes"][G["clube"]]["escalacao"] = auto_escalar(G, G["clubes"][G["clube"]])
    definir_objetivo(G)
    print("Clube: %s" % G["clubes"][G["clube"]]["nome"])
    for _ in range(temporadas):
        while 0 < G["semana"] <= SEMANAS_LIGA:
            avancar_semana(G)
        c = G["clubes"][G["clube"]]
        camp = {d: G["clubes"][classificacao(G, G["ligas"][d])[0]]["nome"] for d in "ABCD"}
        print("T%d | A:%s B:%s C:%s D:%s | %s %s %do, caixa %s, elenco %d, media %.1f" %
              (G["temporada"], camp["A"], camp["B"], camp["C"], camp["D"], c["nome"],
               c["divisao"], posicao_na_liga(G, c["id"]), din(c["dinheiro"]),
               len(c["elenco"]), media_elenco(G, c)))
        if not fim_temporada(G):
            return
        iniciar_temporada(G)
    salvar(G, "teste_save.json")
    G2 = carregar("teste_save.json")
    print("Save/load ok: temporada %d, %d clubes, %d jogadores." %
          (G2["temporada"], len(G2["clubes"]), len(G2["jogadores"])))


def main():
    preparar_terminal("--discreto" in sys.argv)
    if getattr(sys, "frozen", False):
        try:
            os.system("title BRASFUT %s" % VERSAO if os.name == "nt" else "")
        except Exception:
            pass
    if "--sim" in sys.argv:
        i = sys.argv.index("--sim")
        simulacao(int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 3)
        return
    if not travar_save():
        print(cor(AVISO_TRAVA, "ruim"))
        return
    G = None
    if os.path.exists(SAVE):
        if ler("Existe um jogo salvo em %s. Carregar? (s/n) " % SAVE).lower().startswith("s"):
            try:
                G = carregar()
                print(cor("Carregado: %s, temporada %d." %
                          (G["clubes"][G["clube"]]["nome"], G["temporada"]), "ok"))
            except Exception as e:
                print(cor("Falha ao carregar (%s). Comecando um jogo novo." % e, "ruim"))
                G = None
    if G is None:
        G = novo_jogo()
    try:
        loop(G)
    except KeyboardInterrupt:
        print("\nSaindo.")
    finally:
        if getattr(sys, "frozen", False):
            try:
                input("\nAte a proxima. Aperte enter para fechar. ")
            except EOFError:
                pass


if __name__ == "__main__":
    main()
