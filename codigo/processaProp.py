#!/usr/bin/python
# -*- coding: utf8 -*-

import topicdetect as tp

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

print 'carregando dicionario'

tp.processaCorpusProp('dictionary-stemming-complete.dict','-prop-stemming-2010',False,2010)