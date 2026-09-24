"""API HTTP do BRASFUT: o motor de sempre, servido para a interface web.

Tres camadas, e so tres:
  sessao.py  - segura o mundo G do motor no processo e escreve o save
  dto.py     - traduz G no que uma tela precisa, uma funcao por tela
  rotas.py   - liga URL a funcao, sem nenhuma regra de jogo dentro

O motor (brasfut.py) continua sem saber que existe interface. Toda tela nova
da migracao entra por dto.py + rotas.py, nunca mexendo no motor.
"""
