#!/usr/bin/python2
# -*- coding: utf8 -*-
# coding=UTF8

import requests, codecs, sys, re
import pygeocoder

from session    import Session



sys.stdout = codecs.getwriter('utf8')(sys.stdout)



# http://code.activestate.com/recipes/410692/
# This class provides the functionality we want. You only need to look at
# this if you want to know how this works. It only needs to be defined
# once, no need to muck around with its internals.
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False




class KRS(object):

    path_search_result = "./body/div[@id='all']/div[@id='main']/p/a"
    path_data_table    = "./body/div[@id='all']/div[@id='main']/"\
        "table[@class='tab1']"



    def __init__(self):
        self.session = Session()
        self.stripper = re.compile(r'[\W+_]', re.UNICODE)
        self.geocoder = pygeocoder.Geocoder()



    def strip_string(self, text):
        if not text:
            return ''

        return self.stripper.sub('', text.lower())

    

    def _geocode_address(self, data):
        lat, lng = None, None
        street, zip_code, city = None, None, None

        for pair in data:
            for case in switch(pair[0]):
                if case('ulica'):
                    street = pair[1]
                    break
                if case('kodpocztowy'):
                    zip_code = pair[1]
                    break
                if case(u'miejscowość'):
                    city = pair[1]
                    break

        # ulica, kod pocztowy miejscowość, Poland
        address = u'{}, {} {}, Poland'.format(street, zip_code, city)

        try:
            results = self.geocoder.geocode( address )

            if len(results) > 0:
                lat, lng = results[0].coordinates

                if len(results) > 1:
                    print('Gecoding address {} gave more than on result, first '
                            'one will be chosen.'.format(address))
        except Exception as e:
            print(u'Exception while geocoding: {}'.format(e.message))

        if lat == 0 and lng == 0:
            print('Could not geocode address {}!'.format(address))

        data.append( (u'szer', lat) )
        data.append( (u'dlug', lng) )



    #def _accept_table(self, table):
    #    pass

    # Parsuje jedną tabelę ze strony podmiotu. Dostaje obiekt '_Element'
    # odpowiadający tabeli, zwraca listę znalezionych danych (jeśli tabela
    # miała dwie kolumny). Tu znajdują się też rozpoznania, czy tabela w ogóle
    # zawiera interesujące dane.
    # UPDATE: na razie 'akceptowalna' tabelka to taka, która ma 2 kolumny. Nie
    # jest to nazbyt zmyślne, więc jeśli trzeba będzie czegoś więcej, tu będzie
    # rozpoznawanie rodzaju table. Odrzucanie -> return None.
    def _parse_table(self, table_elem):

        # Tak może wyglądać sprawdzanie poprawności tabeli:
        #if not self._accept_table( table_elem ):
        #    return None

        data = []

        for row in table_elem:
            cells = row.getchildren()
            #print('Children: {}'.format([c.text for c in cells]))
            if len(cells) == 2:
                key = cells[0].text
                val = cells[1].text
                if key and val:
                    key = self.strip_string(key)

                    if u'nazwisko' in key and u'imię' in key:
                        return []

                    data.append( (key,val) )
        return data



    # Wyciąga informacje ze strony jednego podmiotu KRS. Dostaje adres strony,
    # zwraca listę wierszy z danymi.
    def get_entity(self, address):

        entity_site = self.session.get_site(address)
        data_tables = entity_site.findall( KRS.path_data_table )

        result = []
        for table in data_tables:
            parse_result = self._parse_table( table )
            if parse_result is not None:
                result.extend( parse_result )

        self._geocode_address( result )

        return result


    # Parsuje stronę wyników wyszukiwania KRS'u. Dostaje stronę w ElementTree,
    # zwraca linki do podstron, które są rezultatem wyszukania.
    def _parse_search_results(self, results_site):
        links = results_site.findall( KRS.path_search_result )

        get_addr = lambda link:\
            'http://www.krs-online.com.pl/{}'.format(link.get('href'))

        return map(get_addr,  links)



    def search_for(self, look_for):
        search_results = self.session.get_site('http://www.krs-online.com.pl/',
            params = {'p': 6, 'look': look_for})

        search_results = self._parse_search_results( search_results )

        if len(search_results) == 0:
            raise RuntimeError('Nothing found when searching in KRS for {}'
                    .format(look_for))
        elif len(search_results) > 1:
            print('Warning: searching in KRS for id {} returned more than one '
                    'result!. First result will be used.'.format(look_for))

        entity = self.get_entity( search_results[0] )
        return entity



    # Szukanie stron z informacjami o podmiotach wg NIP'u. Zwraca listę linków
    # z wynikami wyszukania.
    # TODO Czy te w ogóle będą potrzebne???
    def get_tax_id(self, nip):
        pass

    def get_registry_id(self, reg_id):
        pass





# Przykład użycia klasy KRS.
def example():
    krs = KRS()


    #id_num = '0000018602' # numer spółki Żywiec
    id_num = 6290011681   # NIP spółki ERG SA


    # Szukanie po NIP'ie (może też być numer KRS, jest w danych z money.pl)
    entity_data = krs.search_for(id_num)
    

    # Jeżeli wyszukiwanie zwróci więcej niż jeden wynik, wypisze się ostrzeżenie
    # i sparsowany zostanie pierwszy z nich.
    # Jeżeli nic się nie znajdzie, poleci RuntimeError.

    # Funkcje spóbuje też geo-zlokalizować adres wyciągnięty z danych, jeśli
    # coś się nie uda - wypisze ostrzeżenie (wraz z adresem), jeśli wszystko
    # poszło bez problemów, w danych będą krotki ('szer', X), ('dlug', Y).


    # Zrób sobie coś z danymi.
    print('Dane podmiotu o numerze {}:'.format(id_num))
    for element in entity_data:
        print(element)



def main():
    krs = KRS()

    # Testowe parsowanie tekstu strony z pliku.
    #with codecs.open('site', 'r', 'utf8') as src:
    #    return krs._parse_search_results(srd.read())


    # Testowe wyciąganie danych ze strony w pliku.
    with codecs.open('./cache/krs_entity_site', 'r', 'utf8') as src:
        tabs = krs._parseEntitySite(src.read())

        for k,v in tabs.iteritems():
            print(u'{} -> {}'.format(k,v))


if __name__ == '__main__':
    #main()
    example()

