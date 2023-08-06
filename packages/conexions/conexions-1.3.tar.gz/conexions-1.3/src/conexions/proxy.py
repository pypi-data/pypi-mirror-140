#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#+ Autor:  	Ran#
#+ Creado: 	2022/02/13 16:43:37.259437
#+ Editado:	2022/02/26 14:36:07.657868
# ------------------------------------------------------------------------------
import requests
from requests.sessions import Session
from requests.models import Response
from requests.exceptions import ConnectionError
from typing import List, Union
#import secrets
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
from halo import Halo

from .dto_proxy import ProxyDTO
from .excepcions import CambioNaPaxinaErro
# ------------------------------------------------------------------------------
class Proxy:
    # Atributos da clase -------------------------------------------------------
    __ligazon: str = 'https://sslproxies.org'
    __sesion: Session = None
    __verbose: bool = False
    __verbosalo: bool = False
    __max_cons: int = 0             # ó ser 0 implica que non ten un máximo predefinido
    # xFCR: xuntar as cant_cons nunha soa variable
    __cant_cons_totais: int = 0
    __cant_cons: int = 0
    __cant_cons_espido: int = 0
    __reintentos: int = 5
    __timeout: int = 30
    __cabeceira: dict[str, str]
    __lst_proxys: List[ProxyDTO]    # Ordeados de máis velho[0] a máis novo[len()]
    __proxy: ProxyDTO
    __spinner: Halo = Halo(text='Conectando', spinner='dots')

    __ligazons_ip: List[str] = [
            'https://ip.me',
            'https://icanhazip.com'
            ]
    # --------------------------------------------------------------------------

    def __init__(self, max_cons= 0, reintentos= 5, timeout= 30, verbose=False, verbosalo= False) -> None:
        self.__verbose = verbose
        self.__verbosalo = verbosalo
        self.__max_cons = max_cons
        self.__reintentos = reintentos
        self.__timeout = timeout
        self.__lst_proxys  = []

        self.set_cabeceira()    # Dalle valor a __cabeceira
        self.set_proxys()       # Enche a __lst_proxys
        self.set_proxy()        # Saca un proxy da lista e meteo como atributo
    # --------------------------------------------------------------------------

    # Getters

    def get_ligazon(self) -> str:
        return self.__ligazon

    def get_sesion(self) -> Session:
        """
        """

        return self.__sesion

    def get_verbose(self) -> bool:
        return self.__verbose

    def get_verbosalo(self) -> bool:
        return self.__verbosalo

    def get_max_cons(self) -> int:
        return self.__max_cons

    def get_cant_cons_totais(self) -> int:
        return self.__cant_cons_totais

    def get_cant_cons(self) -> int:
        return self.__cant_cons

    def get_cant_cons_espido(self) -> int:
        return self.__cant_cons_espido

    def get_reintentos(self) -> int:
        return self.__reintentos

    def get_timeout(self) -> int:
        return self.__timeout

    def get_cabeceira(self, set_nova: Union[bool, int] = False) -> dict[str, str]:
        try:
            return self.__cabeceira
        finally:
            if set_nova:
                self.set_cabeceira()

    def get_proxys(self) -> List[ProxyDTO]:
        return self.__lst_proxys

    def get_proxy(self) -> ProxyDTO:
        # se se alcanzou o máximo sacar novo proxy
        if (self.get_max_cons() != 0) and (self.get_cant_cons() >= self.get_max_cons()):
            self.set_proxy()
        return self.__proxy

    def __get_proxy(self) -> dict[str, str]:
        try:
            return self.get_proxy().format()
        finally:
            self.__set_cant_cons(self.get_cant_cons()+1)
            self.__set_cant_cons_totais(self.get_cant_cons_totais()+1)

    def get_ligazons_ip(self) -> List[str]:
        return self.__ligazons_ip

    def get_spinner(self) -> Halo:
        return self.__spinner

    # Getters #

    # Setters

    def __set_ligazon(self, nova_ligazon: str) -> None:
        self.__ligazon = nova_ligazon

    def set_sesion(self, reset: Union[bool, int] = False) -> None:
        """
        """

        if reset:
            self.__sesion = None
        else:
            self.__sesion = requests.Session()

    def set_verbose(self, novo_verbose: bool) -> None:
        self.__verbose = novo_verbose

    def set_verbosalo(self, novo_verbosalo: bool) -> None:
        self.__verbosalo = novo_verbosalo

    def set_reintentos(self, novo_reintentos: int) -> None:
        self.__reintentos = novo_reintentos

    def set_max_cons(self, novo_max_cons: int) -> None:
        self.__max_cons = novo_max_cons

    def __set_cant_cons_totais(self, novo_cant_cons_totais: int) -> None:
        self.__cant_cons_totais = novo_cant_cons_totais

    def __set_cant_cons(self, novo_cant_cons: int) -> None:
        self.__cant_cons = novo_cant_cons

    def __set_cant_cons_espido(self, novo_cant_cons_espido: int) -> None:
        self.__cant_cons_espido = novo_cant_cons_espido

    def set_timeout(self, novo_timeout: int) -> None:
        self.__timeout = novo_timeout

    def set_cabeceira(self) -> None:
        self.__cabeceira = {'User-Agent': UserAgent().random}

    def set_proxys(self) -> None:
        """
        Colle a páxina e saca toda a info sobre os proxys que contén.

        @entradas:
            Ningunha.

        @saidas:
            Ningunha.
        """

        while True:
            try:
                pax_web = requests.get(url= self.get_ligazon(),
                                        headers= self.get_cabeceira())
            except ConnectionError:
                pass
            except Exception:
                raise
            else:
                # se saiu todo ben sáese do bucle
                if pax_web.ok:
                    pax_web.encoding = 'utf-8'
                    break

        if self.get_verbose() and self.get_cant_cons_totais()>0: print(f'{__name__}: Enchendo a lista de proxys.')

        taboa_proxys = bs(pax_web.text, 'html.parser').find(class_='table')

        lst_nomes_cols_esperados = [
                'IP Address',
                'Port',
                'Code',
                'Country',
                'Anonymity',
                'Google',
                'Https',
                'Last Checked'
        ]
        lst_nomes_cols_obtidos = taboa_proxys.thead.find_all('th')

        if len(lst_nomes_cols_esperados) != len(lst_nomes_cols_obtidos):
            raise CambioNaPaxinaErro('Modificado o número de columnas')

        for esperado, obtido in zip(lst_nomes_cols_esperados, lst_nomes_cols_obtidos):
            if esperado != obtido.text:
                raise CambioNaPaxinaErro('Modificado o orde ou nome das columnas')

        for fila in taboa_proxys.tbody:
            novo_proxy = ProxyDTO([atributo.text for atributo in fila.find_all('td')])
            if (novo_proxy.tipo == 'elite proxy') and (novo_proxy.google == 'no') and (novo_proxy.https == 'yes'):
                # métoos desta forma na lista porque así vou sacando e eliminando dende atrás
                self.__lst_proxys.insert(0, novo_proxy)

    def set_proxy(self) -> None:
        """
        Devolve un proxy e automáticamente eliminao da lista.
        De non ter ningún proxy que devolver, escraperá a páxina
        por máis.

        @entradas:
            Ningunha.

        @saídas:
            ProxyDTO    -   Sempre
            └ O proxy a usar nas conexións.
        """

        try:
            self.__proxy = self.get_proxys().pop()
        # se a lista de proxys está baleira
        except IndexError:
            self.set_proxys()
            self.get_proxy()    # recursion
        finally:
            self.__set_cant_cons(0)

    # Setters #

    def get_ip(self, reintentos: int = None) -> str:
        """
        """

        if reintentos == None:
            reintentos = self.get_reintentos()

        try:
            return requests.get(self.get_ligazons_ip()[0]).text.rstrip()
        except ConnectionError:
            return self.get_ip(reintentos-1)

    def get_espido (self, ligazon: str, params: dict = None, bolachas: dict = None,
                stream: dict = False, timeout: int = None, reintentos: int = None) -> Response:
        """
        """

        # lazy_check_types

        #self.

        if timeout == None:
            timeout = self.get_timeout()

        if reintentos == None:
            if self.get_verbose(): print(f'*{__name__}* Chegouse á cantidade máxima de conexións.')
            reintentos = self.get_reintentos()

        if self.get_cant_cons() >= self.get_max_cons():
            self.__set_cant_cons_espido(0)
            reintentos = self.get_reintentos()

        try:
            if self.get_verbosalo(): self.get_spinner().start()
            if self.get_sesion() != None:
                return self.get_sesion().get(url= ligazon, params= params,
                                            headers= self.get_cabeceira(), cookies= bolachas,
                                            stream= stream, timeout= timeout)
            else:
                return requests.get(url= ligazon, params= params,
                                    headers= self.get_cabeceira(set_nova=True), cookies= bolachas,
                                    stream= stream, timeout= timeout)
        #except ConnectionError:
        except:
            if reintentos <= 0:
                if self.get_verbose(): print(f'*{__name__}* Chegouse á cantidade máxima de reintentos.')
                reintentos = self.get_reintentos()
            if self.get_verbose(): print(f'*{__name__}* Reintento nº {self.get_reintentos()+1-reintentos}.')

            return self.get(ligazon= ligazon, params= params, bolachas= bolachas,
                    stream=stream, timeout= timeout, reintentos= reintentos-1)
        finally:
            self.__set_cant_cons_espido(self.get_cant_cons_espido()+1)
            self.__set_cant_cons_totais(self.get_cant_cons_totais()+1)
            if self.get_verbosalo(): self.get_spinner().stop()

    def get(self, ligazon: str, params: dict = None, bolachas: dict = None,
            stream: dict = False, timeout: int = None, reintentos: int = None) -> Response:
        """
        """

        # lazy_check_types

        if timeout == None:
            timeout = self.get_timeout()

        if reintentos == None:
            reintentos = self.get_reintentos()

        if (self.get_max_cons() != 0) and (self.get_cant_cons() >= self.get_max_cons()):
            if self.get_verbose(): print(f'{__name__}: Chegouse á cantidade máxima de conexións. Collendo novo proxy ({len(self.get_proxys())} restantes)')
            self.set_proxy()
            self.__set_cant_cons(0)
            reintentos = self.get_reintentos()

        try:
            if self.get_verbosalo(): self.get_spinner().start()

            if self.get_sesion() != None:
                return self.get_sesion().get(url= ligazon, params= params, proxies= self.__get_proxy(),
                                            headers= self.get_cabeceira(), cookies= bolachas,
                                            stream= stream, timeout= timeout)
            else:
                return requests.get(url= ligazon, params= params, proxies= self.__get_proxy(),
                                        headers= self.get_cabeceira(set_nova=True), cookies= bolachas,
                                        stream= stream, timeout= timeout)
        except:
            if reintentos <= 0:
                if self.get_verbose(): print(f'{__name__}: Chegouse á cantidade máxima de reintentos. Collendo novo proxy ({len(self.get_proxys())} restantes)')
                self.set_proxy()
                reintentos = self.get_reintentos()
            if self.get_verbose(): print(f'{__name__}: Reintento nº {self.get_reintentos()+1-reintentos}.')

            return self.get(ligazon= ligazon, params= params, bolachas= bolachas,
                    stream=stream, timeout= timeout, reintentos= reintentos-1)
        finally:
            if self.get_verbosalo(): self.get_spinner().stop()

# ------------------------------------------------------------------------------
