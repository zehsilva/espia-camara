#!/usr/bin/python
# -*- coding: utf8 -*-

import pickle as pk
from gensim import corpora
import topicdetect as td
import re
import logging

"""
Copyright 2013 de Alan Godoy Souza Mello, Eliezer de Souza da Silva e Saullo
Haniell Galvão de Oliveira
Este arquivo é parte do programa EspiaCâmara. O EspiaCâmara é um software livre;
você pode redistribuí-lo e/ou modificá-lo dentro dos termos da GNU General
Public License como publicada pela Fundação do Software Livre (FSF); na versão 3
da Licença. Este programa é distribuído na esperança que possa ser útil, mas SEM
NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer MERCADO ou
APLICAÇÃO EM PARTICULAR. Veja a licença para maiores detalhes. Você deve ter
recebido uma cópia da [GNU General Public License OU GNU Affero General Public
License], sob o título "LICENCA.txt", junto com este programa, se não, acesse
http://www.gnu.org/licenses/
"""

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

dicio=pk.load(open('pt-unicode.dic'))
print len(dicio)
dicnovo={td.convertnostemlist( x.lower() )[0]:1 for x in dicio if len(td.convertnostemlist( x.lower() ))>0 }
print len(dicnovo)
mapstem={}
for termo in dicnovo:
	stem=td.stemmer.stem(termo)
	if(len(stem)>1):
		if stem not in mapstem:
			mapstem[stem]=set()
		mapstem[stem].update(termo)
print len(mapstem)
dictionary = corpora.Dictionary([ sorted(dicnovo) ])
td.saveDictionary(dictionary,'dictionary-nostemming-complete.dict')

dictionary = corpora.Dictionary([ mapstem.keys() ])
td.saveDictionary(dictionary,'dictionary-stemming-complete.dict')

pk.dump(mapstem,open(td.dircorpus+'map-stem-setword.map','w'))
