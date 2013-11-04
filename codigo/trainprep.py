#!/usr/bin/python
# -*- coding: utf8 -*-

import topicdetect
import gensim
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
# processaCorpusProp('dictionary-nostemming-complete.dict','-prop-nostemming-2008',False)

print 'carregando dicionario'
dictionary=topicdetect.loadDictionary('dictionary-nostemming-complete.dict')
print 'carregando corpus props'
corpus = topicdetect.loadCorpus('-prop-nostemming-2008')
dirmodel = '/home/msc/eliezers/Dropbox/dados_deputados/'
print 'treinando LDA'
lda = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=300, update_every=0, passes=10)
lda.save(dirmodel+'model-lda-props-nostemming-2008-300topics.lda')
#print 'treinando HDP'
#hdp = gensim.models.hdpmodel.HdpModel(corpus=corpus, id2word=dictionary)
#hdp.save(dirmodel+'model-hdp-props.hdp')

