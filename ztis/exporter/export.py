#!/usr/bin/python2
# -*- coding: utf8 -*-
# coding=UTF8

import time, operator
import codecs

from ztis.database.database import *
from ztis.database.model import *
from ztis.crawl.moneypl import *
from ztis.crawl.krs import *

from sqlalchemy.sql import select, func

sys.stdout = codecs.getwriter('utf8')(sys.stdout)

def make_obj(ident):
    return u"PT_OBJECT" + str(ident)

def make_prop(ident):
    return u"PT_PROPERTY" + str(ident)


class Exporter:
    database = Database()
    session = database.get_session()
    
    intro = u"<?xml version='1.0' encoding='UTF-8'?><palantir xmlns=\"http://www.palantirtech.com/pg/schema/import/\"><graph>\n\n"
    outro = u"</graph></palantir>"
    
    objects_start = u"<objectSet>"
    objects_end = u"</objectSet>"
    
    company_start = u"<object id='{}' type='com.palantir.object.business' baseType='com.palantir.object.entity'>\n" # PT_OBJECT1
    company_end = u"</object>\n\n"
    
    properties_start = u"<propertySet>\n"
    properties_end= u"</propertySet>\n\n"
    
    company_name = \
            u"""<property id='{}' type='com.palantir.property.OrganizationName' linkType='com.palantir.link.Simple' role='com.palantir.role.none' keywordDisabled='false' >
               <propertyValue>
                  <propertyData>{}</propertyData>
               </propertyValue>
            </property>\n\n""" # PT_PROPERTY4, name
    
    company_address = \
            u"""\n<property id='{}' type='com.palantir.property.Address' linkType='com.palantir.link.Simple' role='com.palantir.role.none' keywordDisabled='false'>
               <gisData >
                  <point latitude='{}' longitude='{}' >
                  </point>
               </gisData>

               <propertyValue>
                  <propertyComponent type='ADDRESS1' >
                     <propertyData>{}</propertyData>
                  </propertyComponent>
                  <propertyComponent type='CITY' >
                     <propertyData>{}</propertyData>
                  </propertyComponent>
                  <propertyComponent type='ZIP' >
                     <propertyData>{}</propertyData>
                  </propertyComponent>
               </propertyValue>

            </property>\n\n""" # PT_PROPERTY3, lat, long, street + number, city, zipcode
    
    company_url = \
            u"""<property id='{}' type='com.palantir.property.URL' linkType='com.palantir.link.Simple' role='com.palantir.role.none' keywordDisabled='false' >
               <propertyValue>
                  <propertyData>{}</propertyData>
               </propertyValue>
            </property>\n\n""" # PT_PROPERTY8, url
    
    def export(self, companies, filepath):
        pfile = codecs.open(filepath, "w", "utf-8")
        pfile.write(self.intro)
        pfile.write(self.objects_start)
        
        prop_id = 1
        
        for i in range(len(companies)):
            pfile.write(self.company_start.format(make_obj(i+1)))
            pfile.write(self.properties_start)
            
            # company name
            pfile.write(self.company_name.format(make_prop(prop_id), companies[i].name))
            prop_id += 1
            
            # address and gis data
            pfile.write(self.company_address.format(make_prop(prop_id), \
                companies[i].lat, companies[i].lng, companies[i].address, \
                companies[i].city, companies[i].zip_code))
            prop_id += 1
            
            # www
            pfile.write(self.company_url.format(make_prop(prop_id), companies[i].www))
            prop_id += 1
            
            pfile.write(self.properties_end)
            pfile.write(self.company_end)
        
        pfile.write(self.objects_end)
        
        # links
        
        pfile.write(self.outro)
        pfile.close()


