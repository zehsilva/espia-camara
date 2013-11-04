#!/usr/bin/python
# -*- coding: utf8 -*-

import topicdetect

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

#print '> salvando discursos por nome de deputado, sem aplicar stemming, mas aplicando stopwords e outros pre-processamentos'
#depdoc = topicdetect.convertsaveDiscursos_nostem()

print '>carregando discursos ja salvos (sem stemming)'
depdoc = topicdetect.loadDiscursosDep('discursos-deputado-inteiro-teor-nostem.pkl')

#print '> salvando discursos por nome de deputado, aplicando stemming, stopwords e outros pre-processamentos'
#depdoc = topicdetect.convertsaveDiscursos()


#print '>carregando discursos ja salvos'
#depdoc = topicdetect.loadDiscursosDep()


print '>selecionando deputados com mais de 10 discursos'
deplen100 = {iddep:depdoc[iddep] for iddep in depdoc if len(depdoc[iddep])>10}
del depdoc


#print '>salvando bag-of-words matrix (mm) de deputados com mais de 10 discursos e dicionario de termos'
#dictionary=topicdetect.saveCorpusPerDeputado(deplen100, 'dictionary-stemming-complete.dict',False,'-completedic-discursos-m10')

print '>salvando amostra (30%) bag-of-words matrix (mm) de deputados com mais de 10 discursos e dicionario de termos sem stemming'
dictionary=topicdetect.saveSampleCorpusPerDeputado(deplen100, 'dictionary-nostemming-complete.dict','-completedic-discursos-sample30-nostem',0.3)


#print '>selecionando deputados com mandato atual e mais de 100 discursos'
#deputadostitulares = topicdetect.loadDeputados('deputados_titulares.pkl')
#depdiscursoslen = {iddep:depdoc[iddep] for iddep in depdoc if iddep in deputadostitulares and len(depdoc[iddep])>100}
#del depdoc

#print '>salvando bag-of-words matrix (mm) de deputados titulares com mais de 100 discursos e dicionario de termos'
#dictionary=topicdetect.saveCorpusPerDeputado(depdiscursoslen, 'dictionary-stemmed-titulares-disclen100.dict')


