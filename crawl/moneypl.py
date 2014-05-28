#!/usr/bin/python2
# -*- coding: utf8 -*-


import requests, codecs, os.path, sys

from lxml import etree
import lxml

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

############################################
############################################
############################################



class CompanySite(object):

    path_section_anchors= ".//div[@class='taby taby3 bb1']/ul/li/span/a"

    path_data_divs      = ".//div[@class='b660 box']"
    path_data_header    = "./div[@class='hd inbox']"
    path_data_table     = "./div/table[@class='tabela tlo_biel']"
    path_data_big_table = "./div/table[@class='tabela big tlo_biel']"
    path_data_big_tables= "./div/table[@class='tabela big tlo_biel ']"

    path_finances_table = ".//div[@id='val_tab_Q_t']"
    path_finances_ticker= "./body/div/div[@id='gielda']/div[@class='mpl_left']"\
            "/div[@class='b660 box']/h1[@class='hd big inbox']/em"


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

        self.details    = None
        self.employment = None
        self.board      = None
        self.finances   = None



    def extract_data_header(self, div_elem):
        header = div_elem.find( CompanySite.path_data_header )
        
        if header == None or header.text == None:
            return None

        #print(u'Analyzed header: {}'.format(lxml.etree.tostring(header)))
        h = header.text.lower().strip()
        #print(u'Returned header: {}'.format(h))
        return h


    def parse_table(self, table_elem):
        data = []
        for row in table_elem:
            row_data = []
            for cell in row:
                text = lxml.etree.tostring(cell, encoding='utf8', method='text') 
                row_data.append( text.strip() )
            data.append( row_data )
        return data


    def extract_table_content(self, table_elem):
        t_body = table_elem.find( 'tbody' )

        if t_body is not None:
            return t_body
        else:
            t_header = table_elem.find( 'thead' )
            if t_header != None:
                table_elem.remove( t_header )

            return table_elem
                        

    def extract_data_table(self, div_elem):
        table = None
        for path in [ \
                CompanySite.path_data_table,\
                CompanySite.path_data_big_table,\
                CompanySite.path_data_big_tables]:

            table = div_elem.find( path )
            if table is not None:
                break
        else:
            #print('No table was found for div element on site {}.'
            #        .format(self.address))
            return None

        table = self.extract_table_content( table )

        return self.parse_table(table)



    def parse_details_table(self, table):
        table_data = []

        for row in table:
            key = row[0].lower()
            val = row[1]
            
            for case in switch(key):
                if 'nazwa' in key:
                    table_data.append( ('nazwa', val) )
                    break
                if case('nip'):
                    table_data.append( ('nip', val.replace('-','')) )
                    break
                if case('regon'):
                    table_data.append( ('regon', val) )
                    break
                if case('prezes'):
                    table_data.append( ('prezes', val) )
                    break
                if case('ekd'):
                    table_data.append( ('ekd', val) )
                    break
                if case('www'):
                    table_data.append( ('www', val) )
                    break
                if case('krs'):
                    table_data.append( ('krs', val) )
                    break

        return table_data


    def get_details(self):
        #print(u'Site: {}'.format(self.address))
        if self.details is not None:
            return (self.details, self.employment, self.board)

        data_divisions =\
                self.site_about.findall( CompanySite.path_data_divs )

        for div in data_divisions:
            header = self.extract_data_header(div)
            table  = self.extract_data_table(div)

            if header == None or table == None:
                continue

            #print(u'Header: {}'.format(header))

            # szczegółowe informacje
            if 'szczeg' in header:
                self.details = self.parse_details_table(table)
                #print(u'Szczegóły:{}\n'.format(details))

            # dane o zatrudnieniu
            if 'zatrudnienie' in header:
                self.employment = table
                #print(u'Zatrudnienie:\n{}'.format( table ))

            # członkowie zarządu
            if 'ludzie' in header:
                self.board = table
                #print(u'Zarząd:\n{}'.format( table ))

        return (self.details, self.employment, self.board)



    def parse_finance_table(self, table):
        t_body = table.find( './tbody' )
        if t_body is not None:
            table = t_body

        indexes = [
                0,  # daty
                1,  # przychód netto
                4,  # zysk netto
                5,  # przepływ netto
                6,  # przepływ z dział. operacyjnej
                7,  # przepływ z dział. inwestycyjnej
                8,  # przepływ z dział. finansowej
                9,  # aktywa
                11, # zobowiązania długoterminowe
                12] # zobowiązania krótkoterminowe

        data = []
        for idx in indexes:
            textified_row = ( cell.text.strip() for cell in table[idx] )
            data.append( textified_row )

        return zip(*data)


    
    #def test_parse_finance_table(self):
    #    table = None
    #    with codecs.open('./cache/finance_table', 'r', 'utf8') as src:
    #        table = lxml.html.fromstring(src.read())

    #    print(u'Table: {}'.format(table))
    #    print(u'Table children: {}'.format(table.getchildren()))

    #    r = self.parse_finance_table( table )
    #    for i in r:
    #        print(i)


    def parse_finance_ticker(self, site_finances):
        ticker = site_finances.find( CompanySite.path_finances_ticker )

        if ticker is None:
            raise RuntimeError('Could not find \'ticker\' element on site {}.'
                    .format(self.address))

        return ticker.text.strip().strip('[]')



    def get_finances(self):
        if self.finances is not None:
            return self.finances
        self.finances = []

        finances_table =\
                self.site_finances.find( CompanySite.path_finances_table )

        ticker = self.parse_finance_ticker(self.site_finances)
        params = { 'ticker': ticker, 'p':'Q', 't':'t', 'o':0 }

        table_el = finances_table[1]
        next_el  = finances_table[2]
        self.finances.extend( self.parse_finance_table(table_el) )


        while 'off' not in next_el.get('class'):

            params['o'] += 4
            #print(u'Params: {}'.format(params))
            finances_table = self.session.post_to_site(
                    'http://www.money.pl/ajax/gielda/finanse/', params)

            table_el = finances_table[1]
            next_el  = finances_table[2]
            #print(u'Rotor class: {}'.format(next_el.get('class')))

            self.finances.extend( self.parse_finance_table(table_el) )

        return self.finances





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


    def get_companies(self):
        for company_address in self.get_companies_list():
            yield CompanySite(self.session, company_address)



# Przykład użycia klasy MoneyPL.
def example():
    money = MoneyPL()

    for company in money.get_companies():
        # company to obiekt CompanySite

        details, employment, board = company.get_details()

        print('Details:')
        for info in details: print(info)

        print('Employment:')
        for info in employment: print(info)
            
        print('Board:')
        for info in board: print(info)


        finances = company.get_finances()
        print(u'Finances:')
        for info in finances: print(info)

        break # inaczej pętla będzie leciała dość długo...



def main():
    money = MoneyPL()

    comps = money.get_companies_list()

    comp = CompanySite(money.session, comps[56])

    comp.get_details()
    for f in comp.get_finances():
        print(f)
    #comp.test_parse_finance_table()


if __name__ == '__main__':
    #main()
    example()

