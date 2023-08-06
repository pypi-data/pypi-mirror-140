#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#+ Autor:  	Ran#
#+ Creado: 	2022/02/13 15:30:39.408208
#+ Editado:	2022/02/15 22:06:52.179490
# ------------------------------------------------------------------------------
from dataclasses import dataclass
from typing import List
# ------------------------------------------------------------------------------
@dataclass
class ProxyDTO:
    ip: str
    porto: str
    codigo_estado: str
    nome_estado: str
    tipo: str
    google: str
    https: str
    dende: str

    def __init__(self, lst_contidos: List) -> None:
        self.ip = lst_contidos[0]
        self.porto = lst_contidos[1]
        self.codigo_estado = lst_contidos[2]
        self.nome_estado = lst_contidos[3]
        self.tipo = lst_contidos[4]
        self.google = lst_contidos[5]
        self.https = lst_contidos[6]
        self.dende = lst_contidos[7]

    def format(self) -> dict[str, str]:
        return {'http': 'http://'+self.ip+':'+self.porto,
                'https': 'http://'+self.ip+':'+self.porto}
# ------------------------------------------------------------------------------
