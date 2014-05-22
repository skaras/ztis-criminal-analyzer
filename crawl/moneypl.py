#!/usr/bin/python2
# -*- coding: utf8 -*-


import requests, codecs, os.path

from lxml import etree
import lxml

from session    import Session


class MoneyPL(object):

    def __init__(self):
        self.session = Session(encoding = 'iso-8859-2')




    def cache_exists(self, cache_file):
        return os.path.isfile(cache_file)


    def cache_read(self, cache_file):
        with codecs.open(cache_file, 'r', 'utf8') as src:
            return [line.strip() for line in src.readlines()]


    def cache_write(self, cache_file, lines):
        with codecs.open(cache_file, 'w', 'utf8') as sink:
            for line in lines:
                sink.write('{}\n'.format(line))




    def get_sectors_list(self):
        cache_file = './cache/sectors_list'
        if self.cache_exists(cache_file):
            return self.cache_read(cache_file)

        sectors_site    = 'http://www.money.pl/gielda/spolki_gpw/'
        sectors_anchors = ".//li[@class='zwin']/a"
        result = []

        sectors_site    = self.session.get_site(sectors_site)
        sectors_anchors = sectors_site.findall(sectors_anchors)

        for anchor in sectors_anchors:
            result.append( anchor.get('href') )

        self.cache_write(cache_file, result)
        return result

        
    def get_companies_list(self):
        cache_file = './cache/companies_list'
        if self.cache_exists(cache_file):
            return self.cache_read(cache_file)

        companies_anchors_path = ".//div[@class='box lista_for']/ul/li/ul/li/a"
        result = []

        for sector_site in self.get_sectors_list():
            #print(u'Ściągam: {}'.format(sector_site))
            sector_site         = self.session.get_site(sector_site)
            companies_anchors   = sector_site.findall(companies_anchors_path)

            for anchor in companies_anchors:
                result.append( anchor.get('href') )

        self.cache_write(cache_file, result)
        return result




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

    def parse_entity_site(self, address):
        # Tak to wygląda testowo:
        site = None
        with codecs.open('./moneypl_entity_site', 'r', 'iso-8859-2') as src:
            site = self.session.clean(src.read())
            site = self.session.parse(site)

        # Tak to powinno wyglądać:
        #site = self.session.get_site(address)

        print('Site: |{}|'.format(site))
        elem = site.findall(".//div[@id='notowania_d']")
        print('Elem: |{}|'.format(lxml.etree.tostring(elem[0])))


# Przykład użycia klasy MoneyPL.
def example():
    pass



def main():
    money = MoneyPL()

    #money.parse_entity_site('whatever')
    money.get_companies_list()


if __name__ == '__main__':
    main()

