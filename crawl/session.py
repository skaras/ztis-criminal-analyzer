#!/usr/bin/python2
# -*- coding: utf8 -*-


import requests


from lxml.html          import fromstring, HTMLParser
from lxml.html.clean    import Cleaner


class Session(object):

    def __init__(self, encoding = None):
        # Obiekt Session, używany przy kolejnych zapytaniach. Potrzebny, żeby
        # raz ustawić nagłówki i nie przekazywać ich do każdego zapytania
        # osobno.
        self.session = requests.Session()
        self.session.headers.update({
            'Accept'            : 'text/html,application/xhtml+xml,'\
                    'application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding'   : 'gzip, deflate',
            'Accept-Language'   : 'pl,en-US;q=0.7,en;q=0.3',
            'Cache-Control'     : 'max-age=0',
            'Connection'        : 'keep-alive',
            #'Host'              : 'www.krs-online.com.pl',
            'User-Agent'        : 'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) '\
                    'Gecko/20100101 Firefox/28.0'
            #'Referer'           : 'http://www.krs-online.com.pl/muzeum-slaska-opolskiego-krs-1260077.html',
            #'Cookie'            : 'krs_fk45=h5mfc4oblmd1e1nokkpu4694e5; krs_cookie_accepted=true',
            #'DNT'               : '1',
            })
        
        self.parser = HTMLParser(encoding = encoding)
        self.cleaner = Cleaner(
                # usuwanie skryptów, styli i komentarzy
                scripts = True,
                javascript = True,
                comments = True,
                style = True,
                # head i body zostają
                page_structure = False)

    def get_session(self):
        return self.session


    def clean(self, dirty_text):
        return self.cleaner.clean_html(dirty_text)


    def get(self, address, params = {}):
        # FIXME czy na pewno takie rozłożenie słownika zadziała?
        response = self.session.get(address, **params)
        response.raise_for_status()

        return response.text

    
    def parse(self, raw_text):
        return fromstring(raw_text, parser = self.parser)


    def get_site(self, address, params = {}):
        text = self.get(address, params)
        text = self.clean(text)
        text = self.parse(text)

        return text


