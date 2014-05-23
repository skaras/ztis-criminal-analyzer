#!/usr/bin/python2
# -*- coding: utf8 -*-


import requests, codecs, os.path, sys

from lxml import etree
import lxml

from session    import Session

sys.stdout = codecs.getwriter('utf8')(sys.stdout)

class Employment(object):
    def __init__(self, year, employment):
        self.year       = year
        self.employment = employment


class BoardMember(object):
    def __init__(self, name, function, year):
        self.name       = name,
        self.function   = function,
        self.year       = year


class Details(object):
    def __init__(self, 
            name        = None, 
            address     = None, 
            nip         = None,
            regon       = None,
            krs         = None,
            employment  = None,
            board       = None):

        self.name       = name
        self.address    = address
        self.nip        = nip
        self.regon      = regon
        self.krs        = krs
        self.employment = employment
        self.board      = board



class CompanySite(object):

    path_section_anchors = ".//div[@class='taby taby3 bb1']/ul/li/span/a"

    path_data_divisions  = ".//div[@class='b660 box']"
    path_data_div_header = "./div[@class='hd inbox']"
    path_data_div_table  = "./div/table[@class='tabela tlo_biel']"
    path_data_div_btable = "./div/table[@class='tabela big tlo_biel']"


    def __init__(self, session, address):
        self.session = session
        self.address = address

        self.site_info      = None
        self.site_about     = None
        self.site_finances  = None

        self.site_info =\
                self.session.get_site(self.address)

        section_anchors =\
                self.site_info.findall( CompanySite.path_section_anchors )

        for anchor in section_anchors:
            text = anchor.text.strip().lower()
            href = anchor.get('href')

            if text == 'o firmie':
                self.site_about = self.session.get_site( href )

            if text == 'finanse':
                self.site_finances = self.session.get_site( href )

        for site in [self.site_info, self.site_about, self.site_finances]:
            if site == None:
                raise RuntimeError('One of the subsites was not found on {}.'
                        .format(self.address))

        self.details = None
        self.finances = None



    def parse_table(self, table_elem):
        data = []
        for row in table_elem:
            row_data = []
            for cell in row:
                text = lxml.etree.tostring(cell, encoding='utf8', method='text') 
                row_data.append( text.strip() )
            data.append( row_data )
        return data


    def extract_data_div_header(self, div_elem):
        header = div_elem.find( CompanySite.path_data_div_header )
        
        if header == None or header.text == None:
            return None
        
        print(u'Analyzed header: {}'.format(lxml.etree.tostring(header)))
        h = header.text.lower().strip()
        print(u'Returned header: {}'.format(h))
        return h


    def extract_data_div_table(self, div_elem):
        table = div_elem.find( CompanySite.path_data_div_table )
        if table == None:
            table = div_elem.find( CompanySite.path_data_div_btable )

        # TODO tabela mała czasem ma thead, czasem nie, tbody - nigdy
        # table big ma thead i tbody, chyba zawsze...

        if table == None: return None

        return self.parse_table(table)


    def get_details(self):
        if self.details != None:
            return self.details

        self.details = Details()

        data_divisions =\
                self.site_about.findall( CompanySite.path_data_divisions )

        for div in data_divisions:
            header = self.extract_data_div_header(div)
            table  = self.extract_data_div_table(div)

            if header == None or table == None:
                continue

            print(u'Header: {}'.format(header))

            # szczegółowe informacje
            if 'szczeg' in header:
                print(u'Szczegóły:{}\n'.format(table))

            # dane o zatrudnieniu
            if 'zatrudnienie' in header:
                print(u'Zatrudnienie:\n{}'.format( table ))

            # członkowie zarządu
            if 'ludzie' in header:
                print(u'Zarząd:\n{}'.format( table ))








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




    ## Parsuje jedną tabelę ze strony podmiotu. Dostaje obiekt '_Element'
    ## odpowiadający tabeli, zwraca słownik znalezionych danych (jeśli tabela
    ## miała dwie kolumny). Tu znajdują się też rozpoznania, czy tabela w ogóle
    ## zawiera interesujące dane.
    ## TODO usuwanie niealfanumerycznych znaków z kluczy??
    #def _parseTable(self, table_elem):
    #    data = {}

    #    for row in table_elem:
    #        cells = row.getchildren()
    #        print('Children: {}'.format([c.text for c in cells]))
    #        if len(cells) == 2:
    #            key = cells[0].text
    #            val = cells[1].text
    #            if key and val:
    #                key = key.lower().strip() #TODO zestaw znaków do usunięcia
    #                data[key] = val
    #    return data


    ## Parsuje stronę podmiotu. Dostaje surowy tekst HTML, zwraca słownik
    ## znalezionych w tabelach danych.
    #def _parseEntitySite(self, text):
    #    document = etree.fromstring(text, parser = self.parser)
    #    print(document)
    #    print(document.getchildren())

    #    #tables = document.findall("./ns:html/ns:body/ns:div/ns:div[@id='gielda',@class='col2']/ns:div[@class='mpl_left']/ns:div[@class='660 box']/ns:div[@class='corner box sesja_big']/ns:div[@class='corner box sesja_big']/ns:div[@id='notowania_d']/ns:div[@class='wartosci']/ns:table[@class='tabela']", namespaces = self.xml_ns)
    #    tables = document.findall(".//ns:body", namespaces = self.xml_ns)

    #    print('Tabales: {}'.format(tables))
    #    result = {}
    #    for table in tables:
    #        result.update(self._parseTable(table))
    #    return result

    #def parse_entity_site(self, address):
    #    # Tak to wygląda testowo:
    #    site = None
    #    with codecs.open('./moneypl_entity_site', 'r', 'iso-8859-2') as src:
    #        site = self.session.clean(src.read())
    #        site = self.session.parse(site)

    #    # Tak to powinno wyglądać:
    #    #site = self.session.get_site(address)

    #    print('Site: |{}|'.format(site))
    #    elem = site.findall(".//div[@id='notowania_d']")
    #    print('Elem: |{}|'.format(lxml.etree.tostring(elem[0])))


# Przykład użycia klasy MoneyPL.
def example():
    pass



def main():
    money = MoneyPL()

    comps = money.get_companies_list()

    comp = CompanySite(money.session, comps[26])

    #print('Info children:')
    #print(comp.site_info.getchildren())
    #print('About children:')
    #print(comp.site_about.getchildren())
    comp.get_details()


if __name__ == '__main__':
    main()

