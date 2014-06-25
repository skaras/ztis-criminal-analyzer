#!/usr/bin/python2
# -*- coding: utf8 -*-
# coding=UTF8

from ztis.database.database import *
from ztis.database.model import *
from ztis.crawl.moneypl import *
from ztis.crawl.krs import *

from sqlalchemy.sql import select, func

sys.stdout = codecs.getwriter('utf8')(sys.stdout)


def import_all(database):
    #database.destroy()
    #database.create()
    #database.clear()
    
    sess = database.get_session()
    
    cnt = sess.query(Company.regon).count()
    print "Got " + str(cnt) + " objects"
    
    money = MoneyPL()
    krs = KRS()
    
    i = 0
    
    for company in money.get_companies():
        
        if i < cnt:
            i += 1
            continue
        
        krs_data = None
        
        details, employment, board = company.get_details()
        
        
        company_data = dict((x.lower(), y) for x, y in details)
        
        krs_id = company_data.get('krs', 0)
        regon_id = company_data.get('regon', 0)
        
        print krs_id
        
        if krs_id > 0:
            krs_details = krs.search_for(krs_id)
        
        krs_data = dict((x.lower(), y) for x, y in krs_details)
        
        all_data = dict(company_data.items() + krs_data.items())
        
        company_obj = Company.create(all_data)
        database.save(company_obj)
        
        for info in employment:
            employment_obj = Employment.create(regon_id, info)
            database.save(employment_obj)
        
        for info in board:
            board_obj = Board.create(regon_id, info)
            database.save(board_obj)
        
        finances = company.get_finances()
        for info in finances:
            finance_obj = Finance.create(regon_id, info)
            database.save(finance_obj)
            
        

database = Database()

import_all(database)
