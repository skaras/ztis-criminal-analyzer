#!/usr/bin/env python2
# -*- coding: utf8 -*-

import sqlite3, codecs, sys, httplib, time, cPickle
from lxml import etree
from itertools import izip, cycle
#import xml.etree.ElementTree as ElementTree




def downloadAndParse():
    hc = httplib.HTTPConnection('www.sejmometr.pl')
    parser = etree.XMLParser(recover=True)
    xmlns = '{http://www.w3.org/1999/xhtml}'

    try:
        authors = cPickle.load(open('authors-dict.dat', 'rb'))
        authorID = len(authors.keys())
        print('Dict zaladowany.')
        print(authors)
    except:
        authors = {}
        authorID = 0

    with codecs.open('authors.txt', 'a', 'utf8') as sink:
        with sqlite3.connect('ustawy.db') as c:
            for row, i in izip(c.execute('SELECT id FROM ustawy WHERE id > 1246 ORDER BY id ASC'), cycle(range(100))):
                id_ = row[0]
                try:
                    hc.request('GET', '/legislacja_projekty_ustaw/' + str(id_))
                    r = hc.getresponse()

                    if r.status != 200:
                        print('Blad ustawy {}: status {}, powod: {}'.format(id_, r.status, r.reason))
                        if r.status == 301:
                            print('Przekierowanie: {}'.format(r.getheader('Location')))
                        continue

                    root = etree.fromstring(r.read(), parser=parser)

                    for spanElem in root.findall(".//{NS}p[@class='line signature']//{NS}span".format(NS=xmlns)):
                        if spanElem.text not in authors:
                            authorID += 1
                            authors[spanElem.text] = authorID
                        sink.write('{};{}\n'.format(id_, authors[spanElem.text]))

                    time.sleep(0.5)
                    if i == 99:
                        print(u'Sciagnieto setke ustaw'.format(i))
                except Exception as e:
                    print('Blad dla ustawy {}: {}'.format(id_, e.message))

    cPickle.dump(authors, open('authors-dict.dat', 'w+b'))

    #with codecs.open('authors-dict.txt', 'w', 'utf8') as authDictFile:
    #    for author, authid in authors.iteritems():
    #        authDictFile.write(u'{};{}\n'.format(authid,author))
    hc.close()


def writeAuthorsDict():
    authors = cPickle.load(open('authors-dict.dat', 'rb'))
    with codecs.open('autorzy-slownik.txt', 'w', 'utf8') as sink:
        for auth, id_ in authors.iteritems():
            sink.write(u'{};{}\n'.format(id_, auth))



if __name__ == '__main__':
    #downloadAndParse()
    writeAuthorsDict()


