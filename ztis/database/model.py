#!/usr/bin/python2
# -*- coding: utf8 -*-
# coding=UTF8

import datetime
from dateutil import parser

from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Text, DateTime, UnicodeText


def to_utf8(string):
    if isinstance(string, unicode):
        return string
    else:
        return string.decode('utf8')


def to_int(string):
    string = string.replace(' ', '')
    if string == '-':
        return 0
    else:
        try:
            return int(string)
        except:
            return 0


Base = declarative_base()

class Company(Base):
    __tablename__ = 'Company'

    regon = Column(Integer, primary_key=True)
    nip = Column(Integer)
    krs = Column(Integer)
    
    name = Column(UnicodeText)
    ekd = Column(UnicodeText)
    chairman = Column(UnicodeText)
    
    www = Column(UnicodeText)
    address = Column(UnicodeText)
    
    lat = Column(String)
    lng = Column(String)
    
    zip_code = Column(UnicodeText)
    city = Column(UnicodeText)
    street = Column(UnicodeText)
    

    def __init__(self, regon, nip, krs, name, ekd, chairman, www, address, lat, lng, zip_code, city, street):
        self.regon = regon
        self.nip = nip
        self.krs = krs
        
        self.name = name
        self.ekd = ekd
        self.chairman = chairman
        
        self.www = www
        self.address = address
        
        self.lat = lat
        self.lng = lng
        
        self.zip_code = zip_code
        self.city = city
        self.street = street
        
    
    def __repr__(self):
        return str(str(self.regon) + " " + self.name)
    
    
    @staticmethod
    def create(data):
        
        #try:
        regon = int(data.get('regon'))
        nip = int(data.get('nip'))
        krs = int(data.get('krs'))
        
        print repr(data.get('nazwa', u''))
        name = to_utf8(data.get('nazwa', u''))
        ekd = to_utf8(data.get('ekd', u''))
        chairman = to_utf8(data.get('prezes', u''))
        
        www = to_utf8(data.get('www', u''))
        print repr(data.get('adres', u''))
        address = to_utf8(data.get('adres', u''))
        
        lat = str(data.get('szer', ''))
        lng = str(data.get('dlug', ''))
        
        zip_code = to_utf8(data.get('kodpocztowy', u''))
        city = to_utf8(data.get(u'miejscowość', u''))
        street = to_utf8(data.get('ulica', u''))
        
        #for k in data.keys():
        #    print k, " -> ", data.get(k)
        
        return Company(regon, nip, krs, name, ekd, chairman, www, address, lat, lng, zip_code, city, street)
        #except:
        #    return None
    
    
    def __eq__(self, other):
        return self.regon == other.regon
    
    
    def __hash__(self):
        return hash(('regon', regon))




class Board(Base):
    __tablename__ = 'Board'

    regon = Column(Integer, primary_key=True)
    name = Column(UnicodeText, primary_key=True)
    
    position = Column(UnicodeText)
    date = Column(DateTime)
    

    def __init__(self, regon, name, position, date):
        self.regon = regon
        self.name = name
        self.position = position
        self.date = date
        
    
    def __repr__(self):
        return str(self.regon + " " + self.name)
    
    
    @staticmethod
    def create(regon, data):
        
        name = to_utf8(data[0])
        position = to_utf8(data[1])
        date = parser.parse(data[2])
        
        return Board(regon, name, position, date)
    
    
    def __eq__(self, other):
        return self.regon == other.regon
    
    
    def __hash__(self):
        return hash(('regon', regon, 'name', name))



class Employment(Base):
    __tablename__ = 'Employment'

    regon = Column(Integer, primary_key=True)    
    year = Column(Integer, primary_key=True)
    people_count = Column(Integer)
    
    def __init__(self, regon, year, people_count):
        self.regon = regon
        self.year = year
        self.people_count = people_count
    
    def __repr__(self):
        return str(str(self.regon) + " " + str(self.year))
    
    
    @staticmethod
    def create(regon, data):
        
        try:
            regon = to_int(regon)
            year = to_int(data[0])
            people_count = to_int(data[1])
            
            return Employment(regon, year, people_count)
        except:
            return None
    
    def __eq__(self, other):
        return self.regon == other.regon and self.year == other.year
    
    
    def __hash__(self):
        return hash(('regon', regon, 'year', year))



class Finance(Base):
    __tablename__ = 'Finance'

    regon = Column(Integer, primary_key=True)    
    date = Column(DateTime, primary_key=True)
    
    przychod_netto = Column(Integer)
    zysk_netto = Column(Integer)
    
    przeplyw_netto = Column(Integer)
    przeplyw_oper = Column(Integer)
    przeplyw_inwest = Column(Integer)
    przeplyw_finans = Column(Integer)
    
    aktywa = Column(Integer)
    zobowiazania_dlugo = Column(Integer)
    zobowiazania_krotko = Column(Integer)
    
    
    def __init__(self, regon, date, przychod_netto, zysk_netto, przeplyw_netto, \
        przeplyw_oper, przeplyw_inwest, przeplyw_finans, aktywa, \
        zobowiazania_dlugo, zobowiazania_krotko):
        self.regon = regon
        self.date = date
        
        self.przychod_netto = przychod_netto
        self.zysk_netto = zysk_netto
        
        self.przeplyw_netto = przeplyw_netto
        self.przeplyw_oper = przeplyw_oper
        self.przeplyw_inwest = przeplyw_inwest
        self.przeplyw_finans = przeplyw_finans
        
        self.aktywa = aktywa
        self.zobowiazania_dlugo = zobowiazania_dlugo
        self.zobowiazania_krotko = zobowiazania_krotko
    
    
    def __repr__(self):
        return str(str(self.regon) + " " + str(self.date))
    
    
    @staticmethod
    def create(regon, data):
        
        regonid = przychod_netto = zysk_netto = przeplyw_netto = przeplyw_oper \
            = przeplyw_inwest = przeplyw_finans = aktywa = zobowiazania_dlugo \
            = zobowiazania_krotko = 0
        
        try:
            regonid = int(regon)
            date = parser.parse(data[0])
            przychod_netto = to_int(data[1])
            zysk_netto = to_int(data[2])
            
            przeplyw_netto = to_int(data[3])
            przeplyw_oper = to_int(data[4])
            przeplyw_inwest = to_int(data[5])
            przeplyw_finans = to_int(data[6])
            
            aktywa = to_int(data[7])
            zobowiazania_dlugo = to_int(data[8])
            zobowiazania_krotko = to_int(data[9])
            
            return Finance(regonid, date, przychod_netto, zysk_netto, przeplyw_netto, \
                przeplyw_oper, przeplyw_inwest, przeplyw_finans, aktywa, \
                zobowiazania_dlugo, zobowiazania_krotko)
        except:
            return None
    
    
    def __eq__(self, other):
        return self.regon == other.regon
    
    
    def __hash__(self):
        return hash(('regon', regon, 'date', date))

