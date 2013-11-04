#!/usr/bin/python
# -*- coding: utf8 -*-

import topicdetect
import gensim
import pickle as pk

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

def print_topics_hdp(ldamodel, topics=20, topn=20):
	if not ldamodel.m_status_up_to_date:
		ldamodel.update_expectations()
	betas = ldamodel.m_lambda + ldamodel.m_eta
	hdp_formatter = gensim.models.ldamodel.HdpTopicFormatter(ldamodel.id2word, betas)
	hdp_formatter.show_topics(topics, topn, formatted=False)

print 'carregando dicionario'
dictionary=topicdetect.loadDictionary('dictionary-stemmed-disclen100.dict')

print 'carregando ids de deputados com mais de 100 discursos'
iddeplist = topicdetect.loadListDepIds('listiddepsavedcorpus.pkl')
deptitulares = topicdetect.loadDeputados('deputados_titulares.pkl')
topics={}
#topics2={}

print 'carregando corpus iddep'
corpus = topicdetect.loadCorpus('-total')

dirmodel = '/home/msc/eliezers/Dropbox/dados_deputados/'
print 'carregando LDA'
lda = gensim.models.ldamodel.LdaModel().load(dirmodel+'model-lda-discursos.lda')

#print 'carregando HDP'
#hdp = gensim.models.hdpmodel.HdpModel().load(dirmodel+'model-lda-discursos.lda')

discursos=topicdetect.loadDiscursosDep()

for iddep in [x for x in iddeplist if x in deptitulares]:
	topics[iddep] = [ lda[corpus.doc2bow(discurso)] for discurso in discursos[iddep] if len(discurso)>1 ]
	#topics2[iddep] = [ hdp[corpus.doc2bow(discurso)] for discurso in discursos[iddep] if len(discurso)>1 ]
		
pk.dump(topics,open('/home/msc/eliezers/Dropbox/repo/datasets/dados-hackathon/topics-lda-deputados-titulares.pkl','w'))
#pk.dump(topics2,open('/home/msc/eliezers/Dropbox/repo/datasets/dados-hackathon/topics-hdp-deputados-titulares.pkl','w'))
