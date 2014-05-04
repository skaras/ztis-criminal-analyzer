#!/usr/bin/python2
# -*- coding: utf8 -*-


import requests, codecs

from lxml import etree



class MoneyPL(object):

    def __init__(self):
        # Obiekt Session, używany przy kolejnych zapytaniach. Potrzebny, żeby
        # raz ustawić nagłówki i nie przekazywać ich do każdego zapytania
        # osobno.
        self.session = requests.Session()
        self.session.headers.update({
            'Accept'            : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding'   : 'gzip, deflate',
            'Accept-Language'   : 'pl,en-US;q=0.7,en;q=0.3',
            'Cache-Control'     : 'max-age=0',
            'Connection'        : 'keep-alive',
            #'Cookie'            : 'krs_fk45=h5mfc4oblmd1e1nokkpu4694e5; krs_cookie_accepted=true',
            #'DNT'               : '1',
            'Host'              : 'www.krs-online.com.pl',
            #'Referer'           : 'http://www.krs-online.com.pl/muzeum-slaska-opolskiego-krs-1260077.html',
            'User-Agent'        : 'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'
            })

        # Obiekt parsera, różny od domyślnego tylko w tym, że nie przewraca się
        # na błędach. Przestrzeń nazw dla XML'i przechowujących strony HTTP.
        self.parser = etree.XMLParser(recover=True, encoding = 'iso-8859-2')
        self.xml_ns = {'ns': 'http://www.w3.org/1999/xhtml'}



    ## Parsuje stronę wyników wyszukiwania KRS'u. Dostaje surowy tekst HTML,
    ## zwraca linki do podstron, które są rezultatem wyszukania.
    #def _parseSearchResults(self, text):
    #    document = etree.fromstring(text, parser = self.parser)

    #    links = document.findall(".//ns:div[@id='main']/ns:p/ns:a",\
    #            namespaces = self.xml_ns)

    #    result = []
    #    for link in links:
    #        result.append('http://www.krs-online.com.pl/{}'.format(link.get('href')))
    #    return result



    ## Szukanie stron z informacjami o podmiotach wg NIP'u. Zwraca listę linków
    ## z wynikami wyszukania.
    #def searchTaxID(self, nip):
    #    r = self.session.get('http://www.krs-online.com.pl/',
    #        params = {'p': 6, 'look': nip})
    #    r.raise_for_status()

    #    return self._parseSearchResults(r.text)



    # Parsuje jedną tabelę ze strony podmiotu. Dostaje obiekt '_Element'
    # odpowiadający tabeli, zwraca słownik znalezionych danych (jeśli tabela
    # miała dwie kolumny). Tu znajdują się też rozpoznania, czy tabela w ogóle
    # zawiera interesujące dane.
    # TODO usuwanie niealfanumerycznych znaków z kluczy??
    def _parseTable(self, table_elem):
        data = {}

        for row in table_elem:
            cells = row.getchildren()
            print('Children: {}'.format([c.text for c in cells]))
            if len(cells) == 2:
                key = cells[0].text
                val = cells[1].text
                if key and val:
                    key = key.lower().strip() #TODO zestaw znaków do usunięcia
                    data[key] = val
        return data


    # Parsuje stronę podmiotu. Dostaje surowy tekst HTML, zwraca słownik
    # znalezionych w tabelach danych.
    def _parseEntitySite(self, text):
        document = etree.fromstring(text, parser = self.parser)
        print(document)
        print(document.getchildren())

        #tables = document.findall("./ns:html/ns:body/ns:div/ns:div[@id='gielda',@class='col2']/ns:div[@class='mpl_left']/ns:div[@class='660 box']/ns:div[@class='corner box sesja_big']/ns:div[@class='corner box sesja_big']/ns:div[@id='notowania_d']/ns:div[@class='wartosci']/ns:table[@class='tabela']", namespaces = self.xml_ns)
        tables = document.findall(".//ns:body", namespaces = self.xml_ns)

        print('Tabales: {}'.format(tables))
        result = {}
        for table in tables:
            result.update(self._parseTable(table))
        return result



    # Wyciąga informacje ze strony jednego podmiotu. Dostaje adres strony,
    # zwraca słownik danych.
    def extractEntityData(self, address):
        r = self.session.get(address)
        r.raise_for_status()

        #document = etree.fromstring(r.text, parser = self.parser)
        return self._parseEntitySite(r.text)



# Przykład użycia klasy MoneyPL.
def example():
    pass



def main():
    money = MoneyPL()

    # Testowe parsowanie tekstu strony z pliku.
    #with codecs.open('site', 'r', 'utf8') as src:
    #    return krs._parseSearchResults(srd.read())


    # Testowe wyciąganie danych ze strony w pliku.
    with codecs.open('./moneypl_entity_site', 'r', 'iso-8859-2') as src:
        tabs = money._parseEntitySite(src.read())

        for k,v in tabs.iteritems():
            print(u'{} -> {}'.format(k,v))


if __name__ == '__main__':
    main()

