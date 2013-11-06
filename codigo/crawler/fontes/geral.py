#!/usr/bin/python
# -*- coding: utf-8 -*-

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

import unicodedata
import datetime

LISTA_UFS = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", \
	"MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", \
	"SC", "SP", "SE", "TO"]

def remove_acentos(texto):
	if isinstance(texto, unicode):
		u_texto = texto
	else:
		u_texto = texto.decode("utf-8")
	
	return unicodedata.normalize('NFKD', u_texto).encode('ascii', 'ignore'). \
		decode("utf-8")

def normaliza(texto):
	return remove_acentos(texto).upper().strip().replace("`", "'")

def uniformiza(texto):
	if isinstance(texto, unicode):
		u_texto = texto
	else:
		u_texto = texto.decode("utf-8")
	
	return u_texto.upper().strip().replace("`", "'")

def certifica_lista(lista, indice):
	try:
		if isinstance(lista[indice], list):
			return lista[indice]
	except (TypeError, KeyError, AttributeError):
		return []
	
	return [lista[indice]]

def formata_data(str_data):
	try:
		return datetime.datetime.strptime(str_data, "%d/%m/%Y %H:%M:%S")
	except ValueError:
		try:
			return datetime.datetime.strptime(str_data, "%d/%m/%Y")
		except ValueError:
			return None

