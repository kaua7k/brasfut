# -*- coding: utf-8 -*-
"""Historia real dos clubes brasileiros, ate a temporada 2025.

A carreira comeca em 2026: o que vem daqui e o passado do clube na vida real,
e o que o clube ganhar no jogo entra por cima (titulos_hist no save). A tela
do clube (/api/clube/ficha) junta os dois.

Arquivo editavel a mao. Chave: o nome do clube exatamente como em CLUBES_A..D
do brasfut.py. Campos, todos opcionais:
  fundacao  ano de fundacao
  apelido   como a torcida chama
  cidade    sede
  titulos   lista de (competicao, [anos]) - competicoes nacionais e
            internacionais, com o ano de cada conquista (Taca Brasil e
            Robertao contam como Brasileiro, como a CBF unificou em 2010)
  estadual  (nome do estadual, quantidade de titulos) - so a soma, sem os anos

Conferir antes de confiar: foi montado de memoria, e um erro aqui e so um
texto errado na tela, nao muda nada no jogo.
"""

HISTORIA = {
    "Flamengo": {
        "fundacao": 1895, "apelido": "Mengao", "cidade": "Rio de Janeiro",
        "titulos": [
            ("Mundial de Clubes", [1981]),
            ("Libertadores", [1981, 2019, 2022, 2025]),
            ("Recopa Sul-Americana", [2020]),
            ("Brasileirao Serie A", [1980, 1982, 1983, 1992, 2009, 2019, 2020, 2025]),
            ("Copa do Brasil", [1990, 2006, 2013, 2022, 2024]),
            ("Supercopa do Brasil", [2020, 2021, 2025]),
        ],
        "estadual": ("Carioca", 39),
    },
    "Palmeiras": {
        "fundacao": 1914, "apelido": "Verdao", "cidade": "Sao Paulo",
        "titulos": [
            ("Libertadores", [1999, 2020, 2021]),
            ("Recopa Sul-Americana", [2022]),
            ("Copa Mercosul", [1998]),
            ("Brasileirao Serie A", [1960, 1967, 1967, 1969, 1972, 1973, 1993, 1994, 2016, 2018, 2022, 2023]),
            ("Copa do Brasil", [1998, 2012, 2015, 2020]),
            ("Supercopa do Brasil", [2023]),
            ("Brasileirao Serie B", [2003, 2013]),
        ],
        "estadual": ("Paulista", 26),
    },
    "Botafogo": {
        "fundacao": 1894, "apelido": "Glorioso", "cidade": "Rio de Janeiro",
        "titulos": [
            ("Libertadores", [2024]),
            ("Copa Conmebol", [1993]),
            ("Brasileirao Serie A", [1968, 1995, 2024]),
            ("Brasileirao Serie B", [2015, 2021]),
        ],
        "estadual": ("Carioca", 21),
    },
    "Sao Paulo": {
        "fundacao": 1930, "apelido": "Tricolor", "cidade": "Sao Paulo",
        "titulos": [
            ("Mundial de Clubes", [1992, 1993, 2005]),
            ("Libertadores", [1992, 1993, 2005]),
            ("Recopa Sul-Americana", [1993, 1994]),
            ("Sul-Americana", [2012]),
            ("Brasileirao Serie A", [1977, 1986, 1991, 2006, 2007, 2008]),
            ("Copa do Brasil", [2023]),
            ("Supercopa do Brasil", [2024]),
        ],
        "estadual": ("Paulista", 22),
    },
    "Corinthians": {
        "fundacao": 1910, "apelido": "Timao", "cidade": "Sao Paulo",
        "titulos": [
            ("Mundial de Clubes", [2000, 2012]),
            ("Libertadores", [2012]),
            ("Recopa Sul-Americana", [2013]),
            ("Brasileirao Serie A", [1990, 1998, 1999, 2005, 2011, 2015, 2017]),
            ("Copa do Brasil", [1995, 2002, 2009, 2025]),
            ("Supercopa do Brasil", [1991]),
            ("Brasileirao Serie B", [2008]),
        ],
        "estadual": ("Paulista", 31),
    },
    "Atletico-MG": {
        "fundacao": 1908, "apelido": "Galo", "cidade": "Belo Horizonte",
        "titulos": [
            ("Libertadores", [2013]),
            ("Recopa Sul-Americana", [2014]),
            ("Copa Conmebol", [1992, 1997]),
            ("Brasileirao Serie A", [1937, 1971, 2021]),
            ("Copa do Brasil", [2014, 2021]),
            ("Supercopa do Brasil", [2022]),
            ("Brasileirao Serie B", [2006]),
        ],
    },
    "Internacional": {
        "fundacao": 1909, "apelido": "Colorado", "cidade": "Porto Alegre",
        "titulos": [
            ("Mundial de Clubes", [2006]),
            ("Libertadores", [2006, 2010]),
            ("Recopa Sul-Americana", [2007, 2011]),
            ("Sul-Americana", [2008]),
            ("Brasileirao Serie A", [1975, 1976, 1979]),
            ("Copa do Brasil", [1992]),
        ],
        "estadual": ("Gaucho", 46),
    },
    "Gremio": {
        "fundacao": 1903, "apelido": "Imortal Tricolor", "cidade": "Porto Alegre",
        "titulos": [
            ("Mundial de Clubes", [1983]),
            ("Libertadores", [1983, 1995, 2017]),
            ("Recopa Sul-Americana", [1996, 2018]),
            ("Brasileirao Serie A", [1981, 1996]),
            ("Copa do Brasil", [1989, 1994, 1997, 2001, 2016]),
            ("Supercopa do Brasil", [1990]),
            ("Brasileirao Serie B", [2005]),
        ],
        "estadual": ("Gaucho", 43),
    },
    "Cruzeiro": {
        "fundacao": 1921, "apelido": "Raposa", "cidade": "Belo Horizonte",
        "titulos": [
            ("Libertadores", [1976, 1997]),
            ("Supercopa Libertadores", [1991, 1992]),
            ("Recopa Sul-Americana", [1998]),
            ("Brasileirao Serie A", [1966, 2003, 2013, 2014]),
            ("Copa do Brasil", [1993, 1996, 2000, 2003, 2017, 2018]),
            ("Brasileirao Serie B", [2022]),
        ],
        "estadual": ("Mineiro", 38),
    },
    "Fluminense": {
        "fundacao": 1902, "apelido": "Tricolor das Laranjeiras", "cidade": "Rio de Janeiro",
        "titulos": [
            ("Libertadores", [2023]),
            ("Recopa Sul-Americana", [2024]),
            ("Brasileirao Serie A", [1970, 1984, 2010, 2012]),
            ("Copa do Brasil", [2007]),
            ("Brasileirao Serie C", [1999]),
        ],
        "estadual": ("Carioca", 33),
    },
    "Bahia": {
        "fundacao": 1931, "apelido": "Esquadrao de Aco", "cidade": "Salvador",
        "titulos": [
            ("Brasileirao Serie A", [1959, 1988]),
            ("Copa do Nordeste", [2001, 2002, 2017, 2021, 2025]),
        ],
    },
    "Vasco da Gama": {
        "fundacao": 1898, "apelido": "Gigante da Colina", "cidade": "Rio de Janeiro",
        "titulos": [
            ("Libertadores", [1998]),
            ("Copa Mercosul", [2000]),
            ("Brasileirao Serie A", [1974, 1989, 1997, 2000]),
            ("Copa do Brasil", [2011]),
            ("Brasileirao Serie B", [2009]),
        ],
        "estadual": ("Carioca", 24),
    },
    "Santos": {
        "fundacao": 1912, "apelido": "Peixe", "cidade": "Santos",
        "titulos": [
            ("Mundial de Clubes", [1962, 1963]),
            ("Libertadores", [1962, 1963, 2011]),
            ("Recopa Sul-Americana", [2012]),
            ("Copa Conmebol", [1998]),
            ("Brasileirao Serie A", [1961, 1962, 1963, 1964, 1965, 1968, 2002, 2004]),
            ("Copa do Brasil", [2010]),
            ("Brasileirao Serie B", [2024]),
        ],
        "estadual": ("Paulista", 22),
    },
    "Fortaleza": {
        "fundacao": 1918, "apelido": "Leao do Pici", "cidade": "Fortaleza",
        "titulos": [
            ("Copa do Nordeste", [2019, 2022, 2024]),
            ("Brasileirao Serie B", [2018]),
        ],
    },
    "Red Bull Bragantino": {
        "fundacao": 1928, "apelido": "Massa Bruta", "cidade": "Braganca Paulista",
        "titulos": [
            ("Brasileirao Serie B", [1989, 2019]),
        ],
        "estadual": ("Paulista", 1),
    },
    "Ceara": {
        "fundacao": 1914, "apelido": "Vozao", "cidade": "Fortaleza",
        "titulos": [
            ("Copa do Nordeste", [2015, 2020]),
        ],
    },
    "Sport": {
        "fundacao": 1905, "apelido": "Leao da Ilha", "cidade": "Recife",
        "titulos": [
            ("Brasileirao Serie A", [1987]),
            ("Copa do Brasil", [2008]),
            ("Brasileirao Serie B", [1990]),
        ],
    },
    "Vitoria": {
        "fundacao": 1899, "apelido": "Leao da Barra", "cidade": "Salvador",
        "titulos": [
            ("Copa do Nordeste", [1997, 1999, 2003, 2010]),
            ("Brasileirao Serie B", [2023]),
        ],
    },
    "Juventude": {
        "fundacao": 1913, "apelido": "Papo", "cidade": "Caxias do Sul",
        "titulos": [
            ("Copa do Brasil", [1999]),
            ("Brasileirao Serie B", [1994]),
        ],
        "estadual": ("Gaucho", 1),
    },
    "Mirassol": {"fundacao": 1925, "apelido": "Leao", "cidade": "Mirassol"},
    "Athletico-PR": {
        "fundacao": 1924, "apelido": "Furacao", "cidade": "Curitiba",
        "titulos": [
            ("Sul-Americana", [2018, 2021]),
            ("Brasileirao Serie A", [2001]),
            ("Copa do Brasil", [2019]),
            ("Brasileirao Serie B", [1995]),
        ],
    },
    "Coritiba": {
        "fundacao": 1909, "apelido": "Coxa", "cidade": "Curitiba",
        "titulos": [
            ("Brasileirao Serie A", [1985]),
            ("Brasileirao Serie B", [2007, 2010, 2025]),
        ],
    },
    "Goias": {
        "fundacao": 1943, "apelido": "Esmeraldino", "cidade": "Goiania",
        "titulos": [("Brasileirao Serie B", [1999, 2012])],
    },
    "America-MG": {
        "fundacao": 1912, "apelido": "Coelho", "cidade": "Belo Horizonte",
        "titulos": [("Brasileirao Serie B", [1997, 2017])],
    },
    "Atletico-GO": {"fundacao": 1937, "apelido": "Dragao", "cidade": "Goiania"},
    "Cuiaba": {"fundacao": 2001, "apelido": "Dourado", "cidade": "Cuiaba"},
    "Criciuma": {
        "fundacao": 1947, "apelido": "Tigre", "cidade": "Criciuma",
        "titulos": [("Copa do Brasil", [1991]), ("Brasileirao Serie B", [2002])],
    },
    "Chapecoense": {
        "fundacao": 1973, "apelido": "Chape", "cidade": "Chapeco",
        "titulos": [("Sul-Americana", [2016])],
    },
    "Avai": {"fundacao": 1923, "apelido": "Leao da Ilha", "cidade": "Florianopolis"},
    "Paysandu": {
        "fundacao": 1914, "apelido": "Papao", "cidade": "Belem",
        "titulos": [("Copa dos Campeoes", [2002]), ("Brasileirao Serie B", [1991, 2001])],
    },
    "Remo": {"fundacao": 1905, "apelido": "Leao Azul", "cidade": "Belem"},
    "Vila Nova": {"fundacao": 1943, "apelido": "Tigre", "cidade": "Goiania"},
    "CRB": {"fundacao": 1912, "apelido": "Galo da Praia", "cidade": "Maceio"},
    "Novorizontino": {"fundacao": 2010, "apelido": "Tigre do Vale", "cidade": "Novo Horizonte"},
    "Operario-PR": {"fundacao": 1912, "apelido": "Fantasma", "cidade": "Ponta Grossa"},
    "Amazonas": {"fundacao": 2019, "apelido": "Onca-Pintada", "cidade": "Manaus"},
    "Ferroviaria": {"fundacao": 1950, "apelido": "Locomotiva", "cidade": "Araraquara"},
    "Botafogo-SP": {"fundacao": 1918, "apelido": "Pantera", "cidade": "Ribeirao Preto"},
    "Volta Redonda": {"fundacao": 1976, "apelido": "Voltaco", "cidade": "Volta Redonda"},
    "Athletic": {"fundacao": 1909, "cidade": "Sao Joao del-Rei"},
    "Nautico": {"fundacao": 1901, "apelido": "Timbu", "cidade": "Recife"},
    "Ponte Preta": {"fundacao": 1900, "apelido": "Macaca", "cidade": "Campinas"},
    "Guarani": {
        "fundacao": 1911, "apelido": "Bugre", "cidade": "Campinas",
        "titulos": [("Brasileirao Serie A", [1978]), ("Brasileirao Serie B", [1981])],
    },
    "ABC": {"fundacao": 1915, "apelido": "Mais Querido", "cidade": "Natal"},
    "Figueirense": {"fundacao": 1921, "apelido": "Furacao do Estreito", "cidade": "Florianopolis"},
    "Londrina": {"fundacao": 1956, "apelido": "Tubarao", "cidade": "Londrina"},
    "CSA": {"fundacao": 1913, "apelido": "Azulao", "cidade": "Maceio"},
    "Sampaio Correa": {"fundacao": 1923, "apelido": "Bolivia Querida", "cidade": "Sao Luis"},
    "Ituano": {"fundacao": 1947, "apelido": "Galo de Itu", "cidade": "Itu"},
    "Botafogo-PB": {"fundacao": 1931, "apelido": "Belo", "cidade": "Joao Pessoa"},
    "Portuguesa": {"fundacao": 1920, "apelido": "Lusa", "cidade": "Sao Paulo"},
    "Santa Cruz": {"fundacao": 1914, "apelido": "Cobra Coral", "cidade": "Recife"},
    "America-RN": {"fundacao": 1915, "apelido": "Mecao", "cidade": "Natal"},
    "Joinville": {"fundacao": 1976, "apelido": "Coelho", "cidade": "Joinville"},
    "Caxias": {"fundacao": 1935, "apelido": "Grena", "cidade": "Caxias do Sul"},
    "Brasil de Pelotas": {"fundacao": 1911, "apelido": "Xavante", "cidade": "Pelotas"},
    "Treze": {"fundacao": 1925, "apelido": "Galo da Borborema", "cidade": "Campina Grande"},
    "Campinense": {"fundacao": 1915, "apelido": "Raposa", "cidade": "Campina Grande"},
}


# Cores e desenho do escudo no jogo (nao sao os escudos oficiais, que tem
# marca registrada: sao escudos genericos com as cores do clube). padrao:
# "liso", "vertical" (listras), "horizontal" (faixas), "diagonal" (faixa
# transversal) ou "metade". Clube fora desta lista ganha cores estaveis
# sorteadas pelo nome (api/dto.py, escudo_de).
ESCUDOS = {
    "Flamengo": ("#C8102E", "#111111", "horizontal", "FLA"),
    "Palmeiras": ("#006437", "#FFFFFF", "liso", "PAL"),
    "Botafogo": ("#111111", "#FFFFFF", "vertical", "BOT"),
    "Sao Paulo": ("#FFFFFF", "#E30613", "horizontal", "SPF"),
    "Corinthians": ("#FFFFFF", "#111111", "liso", "COR"),
    "Atletico-MG": ("#111111", "#FFFFFF", "vertical", "CAM"),
    "Internacional": ("#E4002B", "#FFFFFF", "liso", "INT"),
    "Gremio": ("#0D80BF", "#111111", "vertical", "GRE"),
    "Cruzeiro": ("#003DA5", "#FFFFFF", "liso", "CRU"),
    "Fluminense": ("#7A1F3D", "#00843D", "vertical", "FLU"),
    "Bahia": ("#0033A0", "#E30613", "vertical", "BAH"),
    "Vasco da Gama": ("#111111", "#FFFFFF", "diagonal", "VAS"),
    "Santos": ("#FFFFFF", "#111111", "vertical", "SAN"),
    "Fortaleza": ("#0033A0", "#E30613", "horizontal", "FOR"),
    "Red Bull Bragantino": ("#FFFFFF", "#D6001C", "liso", "RBB"),
    "Ceara": ("#111111", "#FFFFFF", "vertical", "CEA"),
    "Sport": ("#E30613", "#111111", "horizontal", "SPT"),
    "Vitoria": ("#E30613", "#111111", "horizontal", "VIT"),
    "Juventude": ("#00843D", "#FFFFFF", "liso", "JUV"),
    "Mirassol": ("#FFD100", "#00843D", "liso", "MIR"),
    "Athletico-PR": ("#C8102E", "#111111", "horizontal", "CAP"),
    "Coritiba": ("#00843D", "#FFFFFF", "liso", "CFC"),
    "Goias": ("#00843D", "#FFFFFF", "liso", "GOI"),
    "America-MG": ("#00843D", "#111111", "liso", "AME"),
    "Atletico-GO": ("#C8102E", "#111111", "horizontal", "ACG"),
    "Cuiaba": ("#FFD100", "#00843D", "liso", "CUI"),
    "Criciuma": ("#FFD100", "#111111", "vertical", "CRI"),
    "Chapecoense": ("#00843D", "#FFFFFF", "liso", "CHA"),
    "Avai": ("#0033A0", "#FFFFFF", "vertical", "AVA"),
    "Paysandu": ("#6CACE4", "#FFFFFF", "vertical", "PAY"),
    "Remo": ("#00205B", "#FFFFFF", "liso", "REM"),
    "Vila Nova": ("#C8102E", "#FFFFFF", "liso", "VIL"),
    "CRB": ("#C8102E", "#FFFFFF", "horizontal", "CRB"),
    "Novorizontino": ("#FFD100", "#111111", "liso", "NOV"),
    "Operario-PR": ("#111111", "#FFFFFF", "vertical", "OPE"),
    "Amazonas": ("#FFD100", "#111111", "liso", "AMA"),
    "Ferroviaria": ("#7A1F3D", "#FFFFFF", "liso", "FER"),
    "Botafogo-SP": ("#C8102E", "#FFFFFF", "vertical", "BFC"),
    "Volta Redonda": ("#FFD100", "#FFFFFF", "metade", "VRE"),
    "Athletic": ("#111111", "#FFFFFF", "metade", "ATH"),
    "Nautico": ("#C8102E", "#FFFFFF", "vertical", "NAU"),
    "Ponte Preta": ("#111111", "#FFFFFF", "diagonal", "PON"),
    "Guarani": ("#00843D", "#FFFFFF", "liso", "GUA"),
    "ABC": ("#111111", "#FFFFFF", "liso", "ABC"),
    "Figueirense": ("#111111", "#FFFFFF", "vertical", "FIG"),
    "Londrina": ("#6CACE4", "#FFFFFF", "liso", "LEC"),
    "CSA": ("#0033A0", "#FFFFFF", "liso", "CSA"),
    "Sampaio Correa": ("#FFD100", "#00843D", "horizontal", "SAM"),
    "Ituano": ("#C8102E", "#111111", "horizontal", "ITU"),
    "Sao Bernardo": ("#FFD100", "#111111", "liso", "SBE"),
    "Botafogo-PB": ("#111111", "#FFFFFF", "vertical", "BPB"),
    "Confianca": ("#0033A0", "#FFFFFF", "liso", "CON"),
    "Tombense": ("#C8102E", "#FFFFFF", "liso", "TOM"),
    "Ypiranga": ("#00843D", "#FFD100", "liso", "YPI"),
    "Portuguesa": ("#C8102E", "#00843D", "horizontal", "POR"),
    "Santa Cruz": ("#111111", "#C8102E", "horizontal", "SCR"),
    "America-RN": ("#C8102E", "#FFFFFF", "liso", "AMR"),
    "Joinville": ("#C8102E", "#111111", "vertical", "JEC"),
    "Caxias": ("#7A1F3D", "#FFFFFF", "liso", "CAX"),
    "Brasil de Pelotas": ("#C8102E", "#111111", "horizontal", "BRP"),
    "Treze": ("#111111", "#FFFFFF", "vertical", "TRE"),
    "Campinense": ("#C8102E", "#111111", "horizontal", "RAP"),
    # os grandes de fora
    "Real Madrid": ("#FFFFFF", "#E8B649", "liso", "RMA"),
    "Barca": ("#A50044", "#004D98", "vertical", "BAR"),
    "Atleti": ("#CB3524", "#FFFFFF", "vertical", "ATM"),
    "Man City": ("#6CABDD", "#FFFFFF", "liso", "MCI"),
    "Man United": ("#DA291C", "#111111", "liso", "MUN"),
    "Liverpool": ("#C8102E", "#FFFFFF", "liso", "LIV"),
    "Chelsea": ("#034694", "#FFFFFF", "liso", "CHE"),
    "Arsenal": ("#EF0107", "#FFFFFF", "metade", "ARS"),
    "Tottenham": ("#FFFFFF", "#132257", "liso", "TOT"),
    "Newcastle": ("#111111", "#FFFFFF", "vertical", "NEW"),
    "Bayern": ("#DC052D", "#FFFFFF", "liso", "FCB"),
    "Dortmund": ("#FDE100", "#111111", "liso", "BVB"),
    "Juventus": ("#111111", "#FFFFFF", "vertical", "JUV"),
    "Milan": ("#FB090B", "#111111", "vertical", "MIL"),
    "Inter": ("#0068A8", "#111111", "vertical", "INT"),
    "Napoli": ("#12A0D7", "#FFFFFF", "liso", "NAP"),
    "Roma": ("#8E1F2F", "#F0BC42", "liso", "ROM"),
    "PSG": ("#004170", "#DA291C", "vertical", "PSG"),
    "Marseille": ("#FFFFFF", "#2FAEE0", "liso", "OM"),
    "Porto": ("#003893", "#FFFFFF", "vertical", "FCP"),
    "SL Benfica": ("#E83030", "#FFFFFF", "liso", "SLB"),
    "Sporting CP": ("#008057", "#FFFFFF", "horizontal", "SCP"),
    "Ajax": ("#FFFFFF", "#D2122E", "vertical", "AJA"),
    "PSV": ("#ED1C24", "#FFFFFF", "vertical", "PSV"),
    "Boca Juniors": ("#003A8C", "#FDB813", "horizontal", "BOC"),
    "River Plate": ("#FFFFFF", "#E30613", "diagonal", "RIV"),
    "Racing": ("#6CACE4", "#FFFFFF", "vertical", "RAC"),
    "Independiente": ("#E30613", "#FFFFFF", "liso", "IND"),
    "Penarol": ("#FFD100", "#111111", "vertical", "PEN"),
    "Nacional": ("#FFFFFF", "#0033A0", "metade", "NAC"),
    "Colo-Colo": ("#FFFFFF", "#111111", "liso", "CCO"),
    "Olimpia": ("#FFFFFF", "#111111", "horizontal", "OLI"),
    "Al-Hilal Saudi FC": ("#0033A0", "#FFFFFF", "liso", "HIL"),
    "Al-Nassr": ("#FFD100", "#0033A0", "liso", "NAS"),
    "Inter Miami": ("#F7B5CD", "#111111", "liso", "MIA"),
}
