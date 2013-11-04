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

import datetime
import csv
import urllib
import zipfile
import Levenshtein as lev
import numpy as np
import os
from geral import *

ANO_ATUAL = datetime.datetime.now().year
ANO_ELEICAO = max(filter(lambda a: a < ANO_ATUAL, \
	[2010, 2006, 2002, 1998, 1994, 1990]))

DIR_DADOS = ""


def get_receitas(deputados, deputados_por_nome_tse):
	for uf in LISTA_UFS:
		with open(DIR_DADOS + "candidato/%s/ReceitasCandidatos.txt" % uf, \
			"rb") as arquivo_receitas:
			
			lista_receitas = csv.reader(arquivo_receitas, delimiter=";")
			cabecalho = True
			
			for receita in lista_receitas:
				if len(receita) <= 1:
					continue
				
				if cabecalho:
					cabecalho = False
					continue
				
				receita = map(lambda a: a.decode("utf-8"), receita)
				
				if uniformiza(receita[4]) != "DEPUTADO FEDERAL":
					continue
				
				try:
					id_deputado = deputados_por_nome_tse[uniformiza(receita[5])]
				except KeyError:
					continue
				
				deputados[id_deputado]["cpf"] = int(receita[6])
				
				try:
					dep_receitas = deputados[id_deputado]["eleicao"]["receitas"]
				except KeyError:
					deputados[id_deputado]["eleicao"]["receitas"] = []
					dep_receitas = deputados[id_deputado]["eleicao"]["receitas"]
				
				data_doacao = formata_data(receita[12])
				
				try:
					no_recibo = int(receita[8])
				except ValueError:
					no_recibo = -1
				
				try:
					no_documento = int(receita[9])
				except ValueError:
					no_documento = -1
				
				try:
					cpf_cnpj = int(receita[10])
				except ValueError:
					cpf_cnpj = -1
				
				dep_receitas.append({ \
					"recibo": no_recibo, \
					"no_documento": no_documento, \
					"cpf_cnpj": cpf_cnpj, \
					"pessoa_fisica": len(receita[10]) == 11, \
					"nome_doador": uniformiza(receita[11]), \
					"data_doacao": data_doacao, \
					"valor": float(receita[13].replace(",", ".")), \
					"tipo": uniformiza(receita[14]), \
					"fonte": uniformiza(receita[15]), \
					"especie": uniformiza(receita[16]), \
					"descricao": uniformiza(receita[17])})

def get_despesas(deputados, deputados_por_nome_tse):
	for uf in LISTA_UFS:
		with open(DIR_DADOS + "candidato/%s/DespesasCandidatos.txt" % uf, \
			"rb") as arquivo_despesas:
			
			lista_despesas = csv.reader(arquivo_despesas, delimiter=";")
			cabecalho = True
			
			for despesa in lista_despesas:
				if len(despesa) <= 1:
					continue
				
				if cabecalho:
					cabecalho = False
					continue
				
				despesa = map(lambda a: a.decode("utf-8"), despesa)
				
				if uniformiza(despesa[4]) != "DEPUTADO FEDERAL":
					continue
				
				try:
					id_deputado = deputados_por_nome_tse[uniformiza(despesa[5])]
				except KeyError:
					continue
				
				deputados[id_deputado]["cpf"] = int(despesa[6])
				
				try:
					dep_despesas = deputados[id_deputado]["eleicao"]["despesas"]
				except KeyError:
					deputados[id_deputado]["eleicao"]["despesas"] = []
					dep_despesas = deputados[id_deputado]["eleicao"]["despesas"]
				
				data_despesa = formata_data(despesa[12])
				
				try:
					no_documento = int(despesa[9])
				except ValueError:
					no_documento = -1
				
				try:
					cpf_cnpj = int(despesa[10])
				except ValueError:
					cpf_cnpj = -1
				
				dep_despesas.append({ \
					"tipo_documento": uniformiza(despesa[8]), \
					"no_documento": no_documento, \
					"cpf_cnpj": cpf_cnpj, \
					"pessoa_fisica": len(despesa[10]) == 11, \
					"nome_fornecedor": uniformiza(despesa[11]), \
					"data_despesa": data_despesa, \
					"valor": float(despesa[13].replace(",", ".")), \
					"tipo": uniformiza(despesa[14]), \
					"fonte": uniformiza(despesa[15]), \
					"especie": uniformiza(despesa[16]), \
					"descricao": uniformiza(despesa[17])})

def get_votacoes(deputados_por_seq, municipios, municipios_por_cod_tse):
	votacoes = {}
	
	for uf in LISTA_UFS:
		with open(DIR_DADOS + "votacao_candidato_munzona_%4d_%s.txt" % \
			(ANO_ELEICAO, uf), "rb") as arquivo_votacao:
			
			lista_votacao = csv.reader(arquivo_votacao, delimiter=";")
			
			for votacao in lista_votacao:
				votacao = map(lambda a: a.decode("iso-8859-1"), votacao)
				
				try:
					id_deputado = deputados_por_seq[int(votacao[12])]
				except KeyError:
					continue
				
				cod_municipio = municipios_por_cod_tse[int(votacao[7])]
				# Deselegante, mas e a unica fonte da UF do municipio!
				municipios[cod_municipio]["uf"] = uf
				
				try:
					votacoes_mun = votacoes[cod_municipio]
				except KeyError:
					votacoes[cod_municipio] = {}
					votacoes_mun = votacoes[cod_municipio]
				
				try:
					votacoes_zona = votacoes_mun[int(votacao[9])]
				except KeyError:
					votacoes_mun[int(votacao[9])] = {}
					votacoes_zona = votacoes_mun[int(votacao[9])]
				
				votacoes_zona[id_deputado] = int(votacao[28])
	
	return votacoes		

def indices_deputados(deputados):
	deputados_por_nome_completo = {}
	deputados_por_nome_completo_na = {}

	for id_deputado in deputados.keys():
		nome_deputado = uniformiza(deputados[id_deputado]["nome"])
		deputados_por_nome_completo[nome_deputado] = id_deputado
		deputados_por_nome_completo_na[normaliza(nome_deputado)] = \
			id_deputado

	return deputados_por_nome_completo, deputados_por_nome_completo_na

def get_bens_candidatos(deputados, deputados_por_seq):
	for uf in LISTA_UFS:
		with open(DIR_DADOS + "bem_candidato_%4d_%s.txt" % (ANO_ELEICAO, uf), \
			"rb") as arquivo_bens:
			
			lista_bens = csv.reader(arquivo_bens, delimiter=";")
			
			for bem in lista_bens:
				bem = map(lambda a: a.decode("iso-8859-1"), bem)
				
				try:
					id_deputado = deputados_por_seq[int(bem[5])]
				except KeyError:
					continue
				
				try:
					deputados[id_deputado]["eleicao"]["bens"].append(None)
				except KeyError:
					deputados[id_deputado]["eleicao"]["bens"] = [None]
				
				try:
					deputados[id_deputado]["eleicao"]["bens"][-1] = { \
						"cod_tipo_bem": int(bem[6]), \
						"descr_tipo_bem": bem[7], \
						"descr_bem": bem[8], \
						"valor": float(bem[9])}
				except ValueError:
					print uf, bem[5:9]
					raise

def atualiza_deputado(deputado, candidato):
	data_nascimento = datetime.datetime.strptime(candidato[25], "%d-%b-%y")
	
	if data_nascimento > datetime.datetime.now():
		data_nascimento = data_nascimento.replace( \
			year=data_nascimento.year - 100)
	
	deputado["data_nascimento"] = data_nascimento
	deputado["titulo_eleitoral"] = int(candidato[26])
	
	deputado["eleicao"] = {}
	deputado["eleicao"]["seq_candidato"] = int(candidato[11])
	deputado["eleicao"]["partido_eleito"] = candidato[17]
	deputado["eleicao"]["ocupacao_codigo"] = int(candidato[23])
	deputado["eleicao"]["ocupacao_descr"] = candidato[24].title()
	deputado["eleicao"]["grau_instrucao_codigo"] = int(candidato[30])
	deputado["eleicao"]["grau_instrucao_descr"] = candidato[31].title()

def get_candidatos(deputados, deputados_por_nome_completo, \
	deputados_por_nome_completo_na):
	
	deputados_por_seq = {}
	deputados_por_nome_tse = {}
	
	for uf in LISTA_UFS:
		with open(DIR_DADOS + "consulta_vagas_%4d_%s.txt" % (ANO_ELEICAO, uf), \
			"rb") as arquivo_vagas:
			
			lista_vagas = csv.reader(arquivo_vagas, delimiter=";")
	
			cod_deputado_federal = None

			for vaga in lista_vagas:
				if vaga[8] == "DEPUTADO FEDERAL":
					cod_deputado_federal = int(vaga[7])
					vagas_deputado_federal = int(vaga[9])
			
			if cod_deputado_federal == None:
				raise Exception("Não há vagas para deputado federal nessa " \
					"eleição para a UF %s!" % uf)
		
		deputados_identificados = []
		
		with open(DIR_DADOS + "consulta_cand_%4d_%s.txt" % (ANO_ELEICAO, uf), \
			"rb") as arquivo_candidatos:
			
			lista_candidatos = csv.reader(arquivo_candidatos, delimiter=";")
	
			candidatos = []
			nao_deputados = {}

			for candidato in lista_candidatos:
				if int(candidato[8]) != cod_deputado_federal:
					continue
		
				candidato = map(lambda a: a.decode("iso-8859-1"), candidato)
		
				if not candidato[41] in [u"ELEITO", u"SUPLENTE", u"MÉDIA"]:
					continue
				
				nome_tse = uniformiza(candidato[10])
				
				try:
					id_deputado = deputados_por_nome_completo[nome_tse]
				except KeyError:
					try:
						id_deputado = deputados_por_nome_completo_na[ \
							normaliza(nome_tse)]
					except KeyError:
						nao_deputados[uniformiza(candidato[10])] = \
							candidato
						continue
				
				deputados_identificados.append(id_deputado)
				atualiza_deputado(deputados[id_deputado], candidato)
				deputados_por_nome_tse[nome_tse] = id_deputado
				deputados_por_seq[deputados[id_deputado]["eleicao"] \
					["seq_candidato"]] = id_deputado
		
		deputados_uf = []

		for id_deputado in deputados.keys():
			if deputados[id_deputado]["uf"] == uf:
				deputados_uf.append(id_deputado)
						
		deputados_uf = set(deputados_uf)
		n_deputados_uf = len(list(deputados_uf))
		
		deputados_identificados = set(deputados_identificados)
		n_deputados_identificados = len(list(deputados_identificados))
		
		if n_deputados_identificados != vagas_deputado_federal or \
			n_deputados_uf != vagas_deputado_federal:
			
			nao_identificados = list(deputados_uf - deputados_identificados)
			
			for id_deputado in nao_identificados:
				nome_deputado = uniformiza(deputados[id_deputado]["nome"])
				candidato = None
				distancia_candidato = 11
				mesmo_partido_candidato = False
				
				for nao_deputado in nao_deputados.keys():
					try:
						distancia = lev.distance(nome_deputado, nao_deputado)
					except TypeError:
						print "<%s> <%s>" % (nome_deputado, nao_deputado)
						raise
					mesmo_partido = nao_deputados[nao_deputado][17] == \
							deputados[id_deputado]["partido"]
					
					if distancia < distancia_candidato:
						if candidato == None or (mesmo_partido and \
							not mesmo_partido_candidato):
							
							candidato = nao_deputados[nao_deputado]
							distancia_candidato = distancia
							mesmo_partido_candidato = mesmo_partido
							nome_tse = nao_deputado
						elif mesmo_partido and mesmo_partido_candidato:
							raise Exception("Deputado (%s, %s) identificado " \
								"duas vezes." % nome_deputado)
				
				if candidato == None:
					raise Exception("Deputado %s não identificado." % \
						nome_deputado)
				
				atualiza_deputado(deputados[id_deputado], candidato)
				deputados_por_nome_tse[nome_tse] = id_deputado
				deputados_por_seq[deputados[id_deputado]["eleicao"] \
					["seq_candidato"]] = id_deputado
	
	return deputados_por_seq, deputados_por_nome_tse

def obtem_arquivos():
	global DIR_DADOS
	
	fontes = ["http://agencia.tse.jus.br/estatistica/sead/odsele/" \
		"prestacao_contas/prestacao_contas_%4d.zip" % ANO_ELEICAO, \
		"http://agencia.tse.jus.br/estatistica/sead/odsele/votacao_candidato_" \
		"munzona/votacao_candidato_munzona_%4d.zip" % ANO_ELEICAO, \
		"http://agencia.tse.jus.br/estatistica/sead/odsele/consulta_vagas/" \
		"consulta_vagas_%4d.zip" % ANO_ELEICAO, \
		"http://agencia.tse.jus.br/estatistica/sead/odsele/bem_candidato/" \
		"bem_candidato_%4d.zip" % ANO_ELEICAO, \
		"http://agencia.tse.jus.br/estatistica/sead/odsele/consulta_cand/" \
		"consulta_cand_%4d.zip" % ANO_ELEICAO]
	
	dir_dados = "/tmp/tse_dados_%d/" % (np.random.random() * \
		np.iinfo(np.int32).max)
	os.makedirs(dir_dados)
	
	for fonte in fontes:
		arquivo_nome, dummy = urllib.urlretrieve(fonte)
		
		with zipfile.ZipFile(arquivo_nome, 'r') as arquivo_zip:
			arquivo_zip.extractall(path=dir_dados)
	
	DIR_DADOS = dir_dados

