#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import csv
import pickle
import os
import numpy as np
import zipfile

dir_dados = "/tmp/cruza_dados_%d/" % (np.random.random() * \
	np.iinfo(np.int32).max)
os.makedirs(dir_dados)

arq_nome = dir_dados + "tabela_municipios.csv"

if not os.path.isfile(arq_nome):
	arquivo_nome, dummy = urllib.urlretrieve("http://www.interlegis.leg.br/" \
		"processo_legislativo/censo/relatorios/1-cadastro-da-cm.csv/download", \
		filename=arq_nome)
else:
	arquivo_nome = arq_nome

municipios_por_cod_tse = {}
municipios = {}

with open(arquivo_nome, "rb") as arquivo_municipios:
	lista_municipios = csv.reader(arquivo_municipios, delimiter=",")
	cabecalho = True
	
	for municipio in lista_municipios:
		if cabecalho:
			cabecalho = False
			continue
		
		municipio = map(lambda a: a.decode("utf-8"), municipio)
		
		cod_tse = int(municipio[0])
		cod_ibge = int(municipio[1])
		
		municipios_por_cod_tse[cod_tse] = cod_ibge

LISTA_UFS = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", \
	"MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", \
	"SC", "SP", "SE", "TO"]

sem_equivalencia = {}
visitados = {}

with open('equivalencia_tse_ibge.csv', 'wb') as arquivo_equivalencia:
	equivalencia_saida = csv.writer(arquivo_equivalencia, delimiter=';')
	
	fonte = "http://agencia.tse.jus.br/estatistica/sead/odsele/votacao_" \
		"candidato_munzona/votacao_candidato_munzona_2010.zip"
	
	arquivo_nome, dummy = urllib.urlretrieve(fonte)
	
	with zipfile.ZipFile(arquivo_nome, 'r') as arquivo_zip:
		arquivo_zip.extractall(path=dir_dados)
	
	for uf in LISTA_UFS:
		with open(dir_dados + "votacao_candidato_munzona_2010_%s.txt" % uf, \
			"rb") as arquivo_municipios:
			
			lista_municipios = csv.reader(arquivo_municipios, delimiter=";")
			
			for municipio in lista_municipios:
				municipio = map(lambda a: a.decode("iso-8859-1"), municipio)
		
				cod_tse = int(municipio[7])
			
				try:
					cod_ibge = municipios_por_cod_tse[cod_tse]
					
					try:
						dummy = visitados[cod_ibge]
					except KeyError:
						equivalencia_saida.writerow([cod_ibge, cod_tse])
						visitados[cod_ibge] = True
				except KeyError:
					sem_equivalencia[cod_tse] = [municipio[8], municipio[6]]

print sem_equivalencia

