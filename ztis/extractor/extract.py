#!/usr/bin/python2
# -*- coding: utf8 -*-
# coding=UTF8

import time, operator

from ztis.database.database import *
from ztis.database.model import *
from ztis.crawl.moneypl import *
from ztis.crawl.krs import *

from sqlalchemy.sql import select, func

sys.stdout = codecs.getwriter('utf8')(sys.stdout)


criterions = ["przychod_netto", "zysk_netto", "przeplyw_netto", \
            "przeplyw_oper", "przeplyw_inwest", "przeplyw_finans", \
            "aktywa", "zobowiazania_dlugo", "zobowiazania_krotko"]


class Extractor:
    database = Database()
    session = database.get_session()

    def maxval(self, criterion, year, top):
        
        companies = self.database.get_all(Company)
        
        max_values = {}
        
        for company in companies:
            regon = company.regon
            print regon
            finance = self.session.query(Finance).filter(Finance.regon == regon).all()
            values = []
            
            for f in finance:
                if f.date.year == year:
                    values.append(getattr(f, criterion))
            
            if len(values) > 0:
                max_values[regon] = max(values)
            
        sorted_values = sorted(max_values.iteritems(), key=operator.itemgetter(1))
        sorted_values.reverse()
        
        top = min([top, len(sorted_values)])
        
        return ((sorted_values[i][0], sorted_values[i][1]) for i in range(0, top))



    def maxdiff(self, criterion, year, top):
        
        companies = self.session.query(Company).all()
        
        max_values = {}
        
        for company in companies:
            regon = company.regon
            print regon
            finance = self.session.query(Finance).filter(Finance.regon == regon).all()
            values = []
            
            for f in finance:
                if f.date.year == year:
                    values.append(getattr(f, criterion))
            
            if len(values) > 1:
                max_values[regon] = max(values) - min(values)
            
        sorted_values = sorted(max_values.iteritems(), key=operator.itemgetter(1))
        sorted_values.reverse()
        
        top = min([top, len(sorted_values)])
        
        return ((sorted_values[i][0], sorted_values[i][1]) for i in range(0, top))
    
    
    def ids_to_companies(self, ids):
        companies = []
        
        for i in ids:
            regon = i[0]
            companies.append(self.session.query(Company).filter(Company.regon == regon).first())
        
        return companies
            


extr = Extractor()

#for val in extract_maxval(database, 'aktywa', 2001, 5):
#    print val

#for val in extr.ids_to_companies(extr.maxval('aktywa', 20069, 5)):
#    print val.www
