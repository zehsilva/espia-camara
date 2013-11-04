#!/usr/bin/python
# -*- coding: utf8 -*-

import topicdetect
import gensim
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

## dictionary=topicdetect.saveSampleCorpusPerDeputado(deplen100, 'dictionary-stemming-complete.dict','-completedic-discursos-sample10',0.1)

print 'carregando dicionario'
dictionary=topicdetect.loadDictionary('dictionary-stemming-complete.dict')

print 'carregando corpus discursos'
corpus = topicdetect.loadCorpus('-completedic-discursos-sample10')
dirmodel = '/home/msc/eliezers/Dropbox/dados_deputados/'

print 'treinando LDA'
lda = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=100, update_every=0, passes=20)
lda.save(dirmodel+'model-lda-discursos-complete-stemming-sample10-100topics.lda')

#print 'treinando HDP'
#hdp = gensim.models.hdpmodel.HdpModel(corpus=corpus, id2word=dictionary)
#hdp.save(dirmodel+'model-hdp-discursos.hdp')

