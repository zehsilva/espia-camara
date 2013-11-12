#!/usr/bin/python
# -*- coding: utf8 -*-
import topicdetect
import pickle as pk
import re
from gensim import corpora,models

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

dirmodel = '/home/msc/eliezers/datasets/dados_deputados/'
dictionary={}
lda={}
models_name = {'proposicoes':{'model-lda-props-nostemming-2008.lda'},
'discursos':{'model-lda-discursos-complete-stemming-sample40-100topics.lda','model-lda-discursos-complete-stemming-sample40-100topics.lda'} }

def setDirModel(name):
	dirmodel=name

def loadLdaModel(fnamemodel='model-lda-props-nostemming-2008.lda',fnamedic='dictionary-nostemming-complete.dict'):
	lda=models.ldamodel.LdaModel.load(dirmodel+fnamemodel)
	dictionary=topicdetect.loadDictionary(fnamedic)
	lda.id2word = dictionary
	dictionary.id2token={dictionary.token2id[x]:x for x in  dictionary.token2id}
	return lda

def printTopicWords(ldamodel,ntop):
	for topic in ldamodel.show_topics(ntop,formatted=False):
		for word in topic:
			print word[1],
		print
	

def tfidftopic(lda,ntop=100,max=5):
	topict = lda.show_topics(ntop,formatted=False)
	corpus=[[word[1] for word in topics] for topics in topict]
	dicio=corpora.Dictionary(corpus)
	dicio.id2token={dicio.token2id[x]:x for x in  dicio.token2id}
		
	corpusbow = [ dicio.doc2bow(doc) for doc in corpus ]
	tfidfm=models.tfidfmodel.TfidfModel(corpus=corpusbow,id2word=dicio)
	
	return [ [ (y[1],y[0]) for y in sorted( [ (x[1],dicio.id2token[x[0]]) for x in tfidfm[dicio.doc2bow(topic)] ], reverse=True )][:max] for topic in corpus ]

def tfidftopicV2(topict,topn=10):
	
	corpus=[[word[1] for word in topics] for topics in topict]
	dicio=corpora.Dictionary(corpus)
	dicio.id2token={dicio.token2id[x]:x for x in  dicio.token2id}
		
	corpusbow = [ dicio.doc2bow(doc) for doc in corpus ]
	tfidfm=models.tfidfmodel.TfidfModel(corpus=corpusbow,id2word=dicio)
	
	return [ [ (y[1],y[0]) for y in sorted( [ (x[1],dicio.id2token[x[0]]) for x in tfidfm[dicio.doc2bow(topic)] ], reverse=True )][:topn] for topic in corpus ]

def geraPrettyListV2(tftopics,original):
	tfwords = [ [ word[0] for word in topic] for topic in tftopics]
	result = [ [ (word[0],word[1]) for word in topic[1] if word[1] in topic[0]  ] for topic in zip(tfwords,original)] 
	return result

def geraPrettyListVal(lda,numtopics=300,topn=10,fn='topic-word.pkl'):
	original = lda.show_topics(numtopics,3*topn,formatted=False)
	tftopics = tfidftopic(lda,numtopics,topn)
	tfwords = [ [ word[0] for word in topic] for topic in tftopics]
	result = [ [ (word[0],word[1]) for word in topic[1] if word[1] in topic[0]  ] for topic in zip(tfwords,original)] 
	pk.dump(result,open(topicdetect.dircorpus+fn,'w'))
	return result

def  list2str(lst):
	return "\n".join( [ " ".join([word[0] for word in topic]) for topic in lst] ) 

def doc2topicdist(lda,textdoc):
	return lda[lda.id2word.doc2bow(topicdetect.convertnostemlist(textdoc))]

def processaAllProp(lda,fdist='topics-distribution-lda-prop-nostemming-2008-300topics.pk',ftuple='topics-associative-tuple-lda-prop-nostemming-2008-300topics.pk'):
	dictionary = lda.id2word
	mapaarquivos=topicdetect.loadpk('indices_inteiros_teores.pkl')
	pmeta=topicdetect.loadpk('proposicoes.pkl')
	resultdistribution = [0]*lda.num_topics
	fp=open('script-insert-prop-topic.sql','w')
	result=[]
	for nomearq in mapaarquivos:
		print '#processando arquivo '+nomearq
		props = topicdetect.loadpk(nomearq)
		#print 'number of propositions='+str(len(props))
		#print 'numer of texts='+str(len([idprop for idprop in props if isinstance(props[idprop],dict) and isinstance(props[idprop]['texto'],basestring)]))
		for idprop in props:
		#	print idprop
			if isinstance(props[idprop],dict) and isinstance(props[idprop]['texto'],basestring):
				txt = props[idprop]['texto']
				txt = re.sub(r'picscalex[0-9a-f]+\n[0-9]+\n', 'v',txt)			
				if props[idprop]['tipo_origem']=='msword':
					txt=txt.decode('iso-8859-1')
				docstem = topicdetect.convertnostemlist( txt.lower() )
				if len(docstem) > 0 :
					for topic in lda[dictionary.doc2bow( docstem )]:
						result.append( (idprop,topic[0],topic[1]) )
						print "INSERT INTO ml_proposicoes_topicos(id_proposicao,id_topico,peso) VALUES ('"+str(idprop)+"','"+str(topic[0])+"','"+str(topic[1])+"')"
						fp.write("INSERT INTO ml_proposicoes_topicos(id_proposicao,id_topico,peso) VALUES ('"+str(idprop)+"','"+str(topic[0])+"','"+str(topic[1])+"')"+"\n")
						resultdistribution[topic[0]]+=1
			props[idprop]={}
		del props
	pk.dump(result,open(topicdetect.dircorpus+ftuple,'w'))
	pk.dump(resultdistribution,open(topicdetect.dircorpus+fdist,'w'))
	fp.close()
	return resultdistribution

def processAllDiscursos(lda,fdist='topics-distribution-lda-discursos-nostemming-2010-300topics.pk',ftuple='topics-associative-tuple-lda-discursos-nostemming-2010-300topics.pk'):	
	dictionary = lda.id2word
	resultdistribution = [0]*lda.num_topics
        result=[]
	discursos = pk.load(open(topicdetect.dirdados+'discursos.pkl'))
	iddisc=0
	for discurso in discursos:
		docstem=topicdetect.convertnostemlist( discurso['inteiro_teor'] )
		if len(docstem) > 0:
			for topic in lda[dictionary.doc2bow( docstem )]:
				result.append( (iddisc,topic[0]+300,topic[1]) )
				resultdistribution[topic[0]]+=1
		iddisc+=1
	pk.dump(result,open(topicdetect.dircorpus+ftuple,'w'))
	pk.dump(resultdistribution,open(topicdetect.dircorpus+fdist,'w'))
	return resultdistribution

