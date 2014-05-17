#!/usr/bin/python
# -*- coding: utf8 -*-

import logging
import pickle as pk
import nltk 
from gensim import corpora, models, similarities
import re
import random as rand
import math

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

#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

### stopwords ##
fpstop = open('/home/msc/eliezers/Dropbox/repo/datasets/stopwords-pt.txt')
stopwords={x.replace('\n','').replace('\r','').lower().decode('iso-8859-1') for x in fpstop.readlines()}
print stopwords


## portuguese stemmer (retira os radicais) ##
stemmer = nltk.stem.RSLPStemmer()

## set dir correctly ""
dirdados = '/home/msc/eliezers/datasets/dados_deputados/' # diretorios com os dados originais dos deputados etc
dircorpus = '/home/msc/eliezers/datasets/dados_deputados/' # diretorios com os dados do dicionarios, corpus, matriz de termo-documetos



def convertstemlist(discurso):
	if isinstance(discurso, basestring):
		return [ stemmer.stem( trecho.lower() ) for trecho in re.split(r'[^A-Z^a-z^\xc0-\xf4^\xf9-\xfb]+',discurso) if trecho not in stopwords and len(trecho)>1 ]
	else:
		return []

def convertnostemlist(discurso):
        if isinstance(discurso, basestring):
                return [ trecho.lower() for trecho in re.split(r'[^A-Z^a-z^\xc0-\xf4^\xf9-\xfb]+',discurso) if trecho not in stopwords and len(trecho)>1 ]
        else:
                return []

def filterdiscursoadddic(discurso,dicdep):
	iddep = discurso['id_deputado']
	if iddep in dicdep:
		listdiscursos = dicdep[iddep]
		listofstemm = convertstemlist( discurso['inteiro_teor'] )
		if len(listofstemm)>1:
			listdiscursos.append( " ".join( listofstemm ) )
		return listofstemm
	else:
		listofstemm = convertstemlist( discurso['inteiro_teor'] )
		if len(listofstemm)>1:
			dicdep[iddep]=[ " ".join( listofstemm )  ]
		return listofstemm

def filterdiscursoadddic_nostem(discurso,dicdep):
        iddep = discurso['id_deputado']
        if iddep in dicdep:
                listdiscursos = dicdep[iddep]
                listofstemm = convertnostemlist( discurso['inteiro_teor'] )
                if len(listofstemm)>1:
                        listdiscursos.append( " ".join( listofstemm ) )
                return listofstemm
        else:
                listofstemm = convertnostemlist( discurso['inteiro_teor'] )
                if len(listofstemm)>1:
                        dicdep[iddep]=[ " ".join( listofstemm )  ]
                return listofstemm


def convertsaveDiscursos():
	fpdisc = open(dirdados+'discursos.pkl')
	fpdep = open(dirdados+'discursos-deputado-inteiro-teor.pkl','w')
	discursos = pk.load(fpdisc)
	deputadodiscursos=dict()

	continua = True
	while continua:
		try:
			discurso = discursos.pop()
			filterdiscursoadddic(discurso,deputadodiscursos)
			discurso.clear()
			del discurso
		except IndexError:
			continua = False
			break
	
	pk.dump( deputadodiscursos, fpdep)
	fpdep.close()
	fpdisc.close()
	del discursos
	return deputadodiscursos

def convertsaveDiscursos_nostem(nomearq='discursos-deputado-inteiro-teor-nostem.pkl'):
        fpdisc = open(dirdados+'discursos.pkl')
        fpdep = open(dirdados+nomearq,'w')
        discursos = pk.load(fpdisc)
        deputadodiscursos=dict()

        continua = True
        while continua:
                try:
                        discurso = discursos.pop()
                        filterdiscursoadddic_nostem(discurso,deputadodiscursos)
                        discurso.clear()
                        del discurso
                except IndexError:
                        continua = False
                        break

        pk.dump( deputadodiscursos, fpdep)
        fpdep.close()
        fpdisc.close()
        del discursos
        return deputadodiscursos


def loadDiscursosDep(nomearq='discursos-deputado-inteiro-teor.pkl'):
	fp = open(dirdados+nomearq)
	discursos = pk.load(fp)
	fp.close()
	return discursos
	
def loadDeputados(fn='deputados_por_nome.pkl'):
	return pk.load( open(dirdados+fn) )

def loadpk(fn):
	return pk.load( open(dirdados+fn) )

def loadDictionary(fn='dictionary-stemmed.dict'):
	dictionary = corpora.Dictionary()
	return dictionary.load(dircorpus+fn)

def saveDictionary(dictionary,fname='dictionary-stemmed.dict'):
	#once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq == 1]
	#dictionary.filter_tokens(once_ids) # remove stop words and words that appear only once
	#dictionary.compactify() # remove gaps in id sequence after words that were removed
	dictionary.save(dircorpus+fname)


def saveCorpusPerDeputado(depdiscursos,fname,saveloaddic,fnamecorpus):
	idlist=[]
	print 'First pass: generating dictionary of terms'
	texts = ""
	d = {}
	if saveloaddic:
		for iddep in depdiscursos:
			d.update( { term.lower():1 for term in sum( [doc.split() for doc in depdiscursos[iddep]] , [] ) } )
	
	
		dictionary = corpora.Dictionary([ d.keys()  ])
		print 'saving dictionary to file: '+dircorpus+fname
        	saveDictionary(dictionary,fname)
	else:
		print 'loading dictionary for file: '+dircorpus+fname
		dictionary = loadDictionary(fname)
	
	print 'Second pass: generating corpus from each deputado'	
	corpus = []
	for iddep in depdiscursos:
		print "deputado id = "+str(iddep)
		for docbow in [ dictionary.doc2bow( docdep.lower().split() ) for docdep in depdiscursos[iddep] ]:
			corpus.append(docbow)
		#corpus = [ dictionary.doc2bow( docdep.lower().split() ) for docdep in depdiscursos[iddep] ]
		#corpora.MmCorpus.serialize(dircorpus+'corpus'+str(iddep)+'.mm', corpus) # store to disk, for later use
		idlist.append(iddep)
	corpora.MmCorpus.serialize(dircorpus+'corpus'+fnamecorpus+'mm', corpus)
	fp=open(dircorpus+fnamecorpus+'-list-iddep.pkl','w')
	pk.dump( idlist, fp)
	fp.close()

	return dictionary

def saveSampleCorpusPerDeputado(depdiscursos,fname,fnamecorpus,fraction):
        texts = ""
        print 'loading dictionary for file: '+dircorpus+fname
        dictionary = loadDictionary(fname)

        print 'generating corpus from each deputado'
        corpus = []
        idlist=[]
	for iddep in depdiscursos:
                print "deputado id = "+str(iddep)
		if( fraction*float(len(depdiscursos[iddep])) >= 1.0):
			discr = rand.sample(depdiscursos[iddep], int(math.floor(fraction*float(len(depdiscursos[iddep])))))
		else:
			discr = depdiscursos[iddep]
                
		for docbow in [ dictionary.doc2bow( docdep.lower().split() ) for docdep in discr ]:
                        corpus.append(docbow)
                #corpus = [ dictionary.doc2bow( docdep.lower().split() ) for docdep in depdiscursos[iddep] ]
                #corpora.MmCorpus.serialize(dircorpus+'corpus'+str(iddep)+'.mm', corpus) # store to disk, for later use
                idlist.append(iddep)
        corpora.MmCorpus.serialize(dircorpus+'corpus'+fnamecorpus+'.mm', corpus)
        fp=open(dircorpus+fnamecorpus+'-list-iddep.pkl','w')
        pk.dump( idlist, fp)
        fp.close()

        return dictionary

def processaCorpusProp(dicfname,fncorpus,dostemming,year):
	dictionary = loadDictionary(dicfname)
	mapaarquivos=loadpk('indices_inteiros_teores.pkl')
	pmeta=loadpk('proposicoes.pkl')
	corpus=[]
	for nomearq in mapaarquivos:
		print 'processando arquivo '+nomearq
		props = loadpk(nomearq)
		for idprop in props:
			#try:
			if props[idprop] and pmeta[idprop]['data_apresentacao'].year>=year:
				if props[idprop]['texto']:
					if len(props[idprop]['texto'])>1:
						try:
							txt = re.sub(r'picscalex[0-9a-f]+\n[0-9]+\n', '',props[idprop]['texto'])
							if props[idprop]['tipo_origem']=='msword':
								txt=txt.decode('iso-8859-1')						
							if dostemming:
								docstem = convertstemlist( txt.lower() )
							else:
								docstem = convertnostemlist( txt.lower() )
							if len(docstem) > 1 :
								corpus.append( dictionary.doc2bow( docstem ) )
						except UnicodeDecodeError:
							print '#error#'
							print 'arquivo ='+nomearq
							print 'idprop ='+str(idprop)
							print props[idprop]['tipo_origem']=='msword'
							print props[idprop]['link']
							print props[idprop]['texto']
			props[idprop]={}
			#except:
			#	print 'erro '+nomearq
		del props
	corpora.MmCorpus.serialize(dircorpus+'corpus'+fncorpus+'.mm', corpus)
	return corpus

def loadListDepIds(fname):
	fp=open(dircorpus+fname)
	idlist = pk.load(fp)
	fp.close()
	return idlist

def loadCorpus(iddep):
	corpus = corpora.MmCorpus(dircorpus+'corpus'+str(iddep)+'.mm')
	return corpus
