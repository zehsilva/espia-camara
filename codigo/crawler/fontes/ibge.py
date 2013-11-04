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

import csv
import urllib
from geral import *

def get_municipios():
	municipios = {}
	municipios_por_cod_tse = {}
	
	with open('equivalencia_tse_ibge.csv', 'rb') as arquivo_equivalencia:
		lista_municipios = csv.reader(arquivo_equivalencia, delimiter=';')
		i = 0
		
		for municipio in lista_municipios:
			cod_ibge = int(municipio[0])
			cod_tse = int(municipio[1])
			
			#print "[%4d] Baixando informações sobre o município "\
			#	"(IBGE: %s, TSE: %s)" % (i, cod_ibge, cod_tse)
			
			i += 1
			arquivo_nome, dummy = urllib.urlretrieve( \
				"http://cidades.ibge.gov.br/xtras/csv.php?lang=&idtema=16&" \
				"codmun=%s" % cod_ibge)
			
			with open(arquivo_nome, "r") as arquivo_municipio:
				dados_municipio = csv.reader(arquivo_municipio, delimiter=';')
				
				cabecalho = True
				municipios[cod_ibge] = {}
				municipios[cod_ibge]["cod_tse"] = cod_tse
				municipios_por_cod_tse[cod_tse] = cod_ibge
				conta = 0
				
				for dado in dados_municipio:
					dado = map(lambda a: a.decode("iso-8859-1"), dado)
					conta += 1
					
					if cabecalho:
						if conta == 1:
							if normaliza(dado[1]) == "CODIGO:":
								raise Exception("Problema na leitura do " \
									"município (%s, %s)" % (cod_ibge, cod_tse))
							
							municipios[cod_ibge]["nome"] = dado[0].title()
						
						if conta == 3 and len(dado) == 1 and \
							normaliza(dado[0]) == normaliza( \
							"Síntese das Informações"):
							
							cabecalho = False
						
						continue
					
					try:
						descricao = normaliza(dado[0])
						
						try:
							valor = float(dado[1].replace(".", ""). \
								replace(",", "."))
						except ValueError:
							if dado[1] == "-" or normaliza(dado[1]) == \
								normaliza("N&atilde"):
								
								valor = 0
							else:
								raise
						
						unidades = normaliza(dado[2])
						
						municipios[cod_ibge][descricao] = [valor, unidades]
					except IndexError:
						break
			
			municipios_por_cod_tse[cod_tse] = cod_ibge
	
	return municipios, municipios_por_cod_tse

