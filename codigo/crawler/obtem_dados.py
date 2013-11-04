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

import fontes.camara.cotas_parlamentares as dados_cotas_parlamentares
import fontes.camara.deputados as dados_deputados
import fontes.camara.orgaos as dados_orgaos
import fontes.camara.proposicoes as dados_proposicoes
import fontes.camara.sessoes as dados_sessoes
import fontes.ibge as dados_ibge
import fontes.tse as dados_tse
import inspect
import datetime
import cPickle as pickle
import logging
import argparse
import threading
import math
import os
import shutil
import suds
import collections
import multiprocessing
import itertools
import random

PERIODO_SESSOES_PADRAO = 20
PERIODO_VOTACOES_PADRAO = 20
PERIODO_PROPOSICOES_PADRAO = 20
PERIODO_DISCURSOS_PADRAO = 20
LOTE_REQUISICOES_PADRAO = 5000

NUM_THREADS_PADRAO = 32
NUM_REQUISICOES_PADRAO = 32

MAX_SEGUNDOS_DELAY = .5

ignora_erro_mensagem = [ \
	"[Microsoft][ODBC SQL Server Driver]Timeout expired - Microsoft OLE DB " \
	"Provider for ODBC Drivers -    at ADODB.RecordsetClass.Open(Object " \
	"Source, Object ActiveConnection, CursorTypeEnum CursorType, " \
	"LockTypeEnum LockType, Int32 Options)"]

def t_map(func, dados, num_requisicoes=None):
	def task_wrapper(i):
		# Tentando mais umas vezes os que tiveram problemas (importante caso
		# esteja obtendo dados da internet.
		for j in range(n_tentativas):
			try:
				resultados[i] = func(dados[i], semaforo, \
					segundos_espera=random.random() * MAX_SEGUNDOS_DELAY)
				return
			except Exception as e:
				if isinstance(e, suds.WebFault) and len(filter(lambda a: e. \
					fault.faultstring.startswith(a), ignora_erro_mensagem)) > 0:
					
					resultados[i] = None
					return
				
				excecoes[i] = e
	
	if num_requisicoes == None:
		global num_threads
		semaforo = None
		n_threads = num_threads
	else:
		semaforo = threading.Semaphore(num_requisicoes)
		n_threads = len(dados)
	
	n_tentativas = int(math.ceil(math.log10(len(dados)))) + 1
	sem_resultados = range(len(dados))
	resultados = [False] * len(dados)
	excecoes = [None] * len(dados)
	
	n_elems = len(sem_resultados)
	n_slices = int(math.ceil(float(n_elems) / n_threads))
	
	for j in range(n_slices):
		threads = [threading.Thread(target=task_wrapper, args=(k,)) for k in \
			sem_resultados[j * n_threads:(j + 1) * n_threads]]
		
		for thread in threads:
			thread.start()
		
		for thread in threads:
			thread.join()
			
	sem_resultados = filter(lambda a: resultados[a] == False, \
		sem_resultados)
	
	if len(sem_resultados) == 0:
		return resultados

	raise Exception("Problemas na excecução das threads (dados " \
		"com problemas: %s)" % map(lambda a: (dados[a], excecoes[a]), \
		sem_resultados))

def c_map(func, dados, num_requisicoes=None):
	global num_threads
	
	n_tentativas = math.ceil(math.log10(len(dados)))
	
	def task_wrapper():
		while True:
			dados_lock.acquire()
			
			try:
				i = fila_dados.popleft()
			except IndexError:
				dados_lock.release()
				return
			
			dados_lock.release()
			
			tentativas[i] += 1
			
			try:
				resultados[i] = func(dados[i], semaforo=semaforo)
			except Exception as e:
				if (isinstance(e, suds.WebFault) and len(filter(lambda a: \
					e.fault.faultstring.startswith(a), ignora_erro_mensagem)) \
					> 0):
					
					resultados[i] = None
				elif tentativas[i] < n_tentativas:
					dados_lock.acquire()
					fila_dados.append(i)
					dados_lock.release()
	
	if num_requisicoes == None:
		semaforo = None
	else:
		semaforo = threading.Semaphore(num_requisicoes)
	
	fila_dados = collections.deque(range(len(dados)))
	dados_lock = threading.Lock()
	tentativas = [0] * len(dados)
	resultados = [False] * len(dados)
	
	threads = [threading.Thread(target=task_wrapper, args=()) for k in \
		range(num_threads)]
	
	for thread in threads:
		thread.start()
	
	for thread in threads:
		thread.join()
	
	sem_resultados = filter(lambda a: resultados[a] == False, \
		range(len(resultados)))
	
	if sem_resultados == []:
		return resultados
	
	raise Exception("Problemas na excecução das threads (dados " \
		"com problemas: %s)" % map(lambda a: dados[a], sem_resultados))

def p_map_aux(argumentos):
	return t_map(func=argumentos[0], dados=argumentos[1], \
		num_requisicoes=argumentos[2])

def p_map(func, dados):
	num_processos = multiprocessing.cpu_count()
	processos = multiprocessing.Pool(num_processos)
	
	sem_resultados = range(len(dados))
	random.shuffle(sem_resultados)
	
	requisicoes_por_processo = int(math.ceil(float(NUM_REQUISICOES_PADRAO) / \
		num_processos))
	dados_processos = float(len(dados)) / num_processos
	
	pedacos = [map(lambda a: dados[a], sem_resultados[int(math.ceil(j * \
		dados_processos)):int(math.ceil((j + 1) * dados_processos))]) \
		for j in range(num_processos)]
	resultados_aux = processos.map(p_map_aux, map(lambda a: [func, a, \
		requisicoes_por_processo], pedacos))
	processos.close()
	resultados_aux = list(itertools.chain(*resultados_aux))
	resultados = [resultados_aux[i] for i in sem_resultados]
	
	sem_resultados = filter(lambda a: resultados[a] == False, \
		range(len(resultados)))
	
	if sem_resultados == []:
		return resultados
	
	raise Exception("Problemas na excecução dos processos (dados " \
		"com problemas: %s)" % map(lambda a: dados[a], sem_resultados))

def salva_dados(dados, nome_arquivo):
	with open(nome_arquivo, 'wb') as arquivo_dados:
		pickle.dump(dados, arquivo_dados)

def carrega_dados(nome_arquivo):
	with open(nome_arquivo, 'rb') as arquivo_dados:
		return pickle.load(arquivo_dados)

def salva_lista_dados(lista, nome_pasta):
	frame = inspect.currentframe()
	var_locais = frame.f_back.f_locals
	
	for item in lista:
		salva_dados(var_locais[item], nome_pasta + '/' + item + '.pkl')
	
	del frame

def carrega_lista_dados(lista, nome_pasta):
	lista_dados = []
	
	for item in lista:
		lista_dados.append(carrega_dados(nome_pasta + '/' + item + '.pkl'))
	
	return lista_dados

def obtem_dados(estado, restaura_execucao, arquivo_estado, pasta_temporaria, \
	pasta_final, ano_final, ano_inicial_proposicoes, ano_inicial_votacoes, \
	ano_inicial_sessoes, ano_inicial_discursos, lote_requisicoes):
	
	if estado[0] == 0:
		print "Obtendo dados da Câmara dos Deputados..."
	
		if estado[1] == 0:
			print "- Obtendo informações de deputados e órgãos da Câmara..."

			partidos, partidos_por_sigla = dados_deputados.get_partidos()
			blocos, blocos_por_sigla = dados_deputados.get_blocos( \
				partidos_por_sigla)
			orgaos, orgaos_por_id = dados_orgaos.get_orgaos()
			deputados, deputados_por_nome = dados_deputados.get_deputados( \
				partidos_por_sigla, orgaos, orgaos_por_id)
			nao_coincide_membros = dados_orgaos.get_orgaos_membros(orgaos, \
				deputados, deputados_por_nome)
			dados_deputados.get_lideres(deputados, deputados_por_nome, \
				partidos, partidos_por_sigla, blocos, blocos_por_sigla)

			lista_nao_encontrado = list(set(dados_deputados. \
				deputado_nao_encontrado))

			for k in nao_coincide_membros.keys():
				[diff1, diff2] = nao_coincide_membros[k]
	
				if len(diff1) > 0 and len(diff2) > 0:
					print "-- Membros de '%s' nao coincidem: dep = %s / " \
						"com = %s" % (k, diff1, diff2)
				elif len(diff1) > 0:
					print "-- Membros de '%s' nao coincidem: dep = %s" % \
						(k, diff1)
				elif len(diff2) > 0:
					print "-- Membros de '%s' nao coincidem: com = %s" % \
						(k, diff2)

			if lista_nao_encontrado != []:
				print "-- Aviso: Deputados não encontrados - %s" % \
					lista_nao_encontrado
			
			salva_lista_dados(['partidos', 'partidos_por_sigla', 'blocos', \
				'blocos_por_sigla', 'orgaos', 'orgaos_por_id', 'deputados', \
				'deputados_por_nome'], pasta_temporaria)
			estado[1:] = [1, 0, None]
			salva_dados(estado, arquivo_estado)

		if estado[1] == 1:
			print "- Obtendo informações de proposições da Câmara..."
			
			proposicoes = {}
			proposicoes_por_nome = {}
			regimes_proposicoes = {}
			regimes_proposicoes_por_nome = {}
			apreciacoes_proposicoes = {}
			apreciacoes_proposicoes_por_nome = {}
			outros_autores_proposicoes = {}
			outros_autores_proposicoes_por_nome = {}
			deputados_antigos = {}
			deputados_antigos_por_nome = {}
			lista_votadas = []
			andamentos = {}
			relatorios_proposicoes = {}
			
			carregou_tudo = False
			
			if restaura_execucao == True:
				[partidos, partidos_por_sigla, blocos, blocos_por_sigla, \
					orgaos, orgaos_por_id, deputados, deputados_por_nome] = \
					carrega_lista_dados(['partidos', 'partidos_por_sigla', \
					'blocos', 'blocos_por_sigla', 'orgaos', 'orgaos_por_id', \
					'deputados', 'deputados_por_nome'], pasta_temporaria)
				
				try:
					[tipos_proposicoes, tipos_situacoes_proposicoes, \
						tipos_autores_proposicoes, proposicoes, \
						proposicoes_por_nome, regimes_proposicoes, \
						regimes_proposicoes_por_nome, apreciacoes_proposicoes, \
						apreciacoes_proposicoes_por_nome, \
						outros_autores_proposicoes, \
						outros_autores_proposicoes_por_nome, \
						deputados_antigos, deputados_antigos_por_nome, \
						lista_votadas] = carrega_lista_dados([ \
						'tipos_proposicoes', 'tipos_situacoes_proposicoes', \
						'tipos_autores_proposicoes', 'proposicoes', \
						'proposicoes_por_nome', 'regimes_proposicoes', \
						'regimes_proposicoes_por_nome', \
						'apreciacoes_proposicoes', \
						'apreciacoes_proposicoes_por_nome', \
						'outros_autores_proposicoes', \
						'outros_autores_proposicoes_por_nome', \
						'deputados_antigos', 'deputados_antigos_por_nome', \
						'lista_votadas'], pasta_temporaria)
					carregou_tudo = True
				except IOError:
					pass
				
				try:
					[andamentos] = carrega_lista_dados(['andamentos'], \
						pasta_temporaria)
				except IOError:
					pass
				
				try:
					[relatorios_proposicoes] = carrega_lista_dados( \
						['relatorios_proposicoes'], pasta_temporaria)
				except IOError:
					pass
				
				restaura_execucao = False
				
			if not carregou_tudo:
				tipos_proposicoes, tipos_situacoes_proposicoes, \
					tipos_autores_proposicoes = dados_proposicoes. \
					get_metadados()
			
			if estado[2] == 0:
				if estado[3] == None:
					tipos_obtidos, tipo_obtendo, ano_obtendo_salvo = \
						[[], None, None]
					tipos_proposicoes_aux = tipos_proposicoes.keys()
				else:
					tipos_obtidos, tipo_obtendo, ano_obtendo_salvo = estado[3]
					tipos_proposicoes_aux = [tipo_obtendo] + \
						list(set(tipos_proposicoes.keys()) - \
						set(tipos_obtidos + [tipo_obtendo]))
				
				ano_obtendo = ano_obtendo_salvo if ano_obtendo_salvo != None \
					else ano_inicial_proposicoes
				conta_tipos_proposicoes = len(tipos_obtidos) + 1
				total_tipos_proposicoes = len(tipos_proposicoes)
				
				n_proposicoes_ant = n_proposicoes = len(proposicoes)
				
				for tipo_proposicoes in tipos_proposicoes_aux:
					print "-- Obtendo dados de proposições do tipo %s " \
						"(%s/%s):" % (tipo_proposicoes, \
						conta_tipos_proposicoes, total_tipos_proposicoes)
					
					for ano in range(ano_obtendo, ano_final + 1):
						print "--- Ano %s" % ano,
						
						dados_proposicoes.get_proposicoes_tipo_ano( \
							tipo_proposicoes, ano, proposicoes, \
							proposicoes_por_nome, regimes_proposicoes, \
							regimes_proposicoes_por_nome, \
							apreciacoes_proposicoes, \
							apreciacoes_proposicoes_por_nome, orgaos, \
							orgaos_por_id, deputados, deputados_por_nome, \
							deputados_antigos, deputados_antigos_por_nome, \
							partidos_por_sigla, outros_autores_proposicoes, \
							outros_autores_proposicoes_por_nome, aux_map=t_map)
						
						n_proposicoes = len(proposicoes)
						proposicoes_dif = n_proposicoes - n_proposicoes_ant
						print '(%s proposições)' % (proposicoes_dif)
						n_proposicoes_ant = n_proposicoes
						
						if proposicoes_dif > 0:
							salva_lista_dados(['proposicoes', \
								'proposicoes_por_nome', 'regimes_proposicoes', \
								'regimes_proposicoes_por_nome', \
								'apreciacoes_proposicoes', \
								'apreciacoes_proposicoes_por_nome', 'orgaos', \
								'orgaos_por_id', 'deputados', \
								'deputados_por_nome', 'deputados_antigos', \
								'deputados_antigos_por_nome', \
								'partidos_por_sigla', \
								'outros_autores_proposicoes', \
								'outros_autores_proposicoes_por_nome'], \
								pasta_temporaria)
						
						estado[2:] = [0, [tipos_obtidos, tipo_proposicoes, \
							ano + 1]]
						salva_dados(estado, arquivo_estado)
					
					conta_tipos_proposicoes += 1
					ano_obtendo = ano_inicial_proposicoes
					tipos_obtidos.append(tipo_proposicoes)
			
				estado[2:] = [1, None]
				salva_dados(estado, arquivo_estado)
			
			if estado[2] == 1:
				ano_obtendo = ano_inicial_votacoes if estado[3] == None else \
					estado[3]
		
				for ano in range(ano_obtendo, ano_final + 1):
					print "-- Obtendo votações de proposições em %s" % ano,
	
					lista_votadas_ano = dados_proposicoes.get_votacoes(ano, \
						proposicoes, proposicoes_por_nome, \
						regimes_proposicoes, regimes_proposicoes_por_nome, \
						apreciacoes_proposicoes, \
						apreciacoes_proposicoes_por_nome, deputados, \
						deputados_por_nome, partidos_por_sigla, blocos, \
						blocos_por_sigla, orgaos, orgaos_por_id, \
						outros_autores_proposicoes, \
						outros_autores_proposicoes_por_nome, \
						deputados_antigos, deputados_antigos_por_nome, t_map)
					
					lista_votadas += lista_votadas_ano
			
					print "(%s proposições)" % len(lista_votadas_ano)
					
					if len(lista_votadas_ano) > 0:
						salva_lista_dados(['proposicoes', \
							'proposicoes_por_nome', 'regimes_proposicoes', \
							'regimes_proposicoes_por_nome', \
							'apreciacoes_proposicoes', \
							'apreciacoes_proposicoes_por_nome', 'deputados', \
							'deputados_por_nome', 'partidos_por_sigla', \
							'blocos', 'blocos_por_sigla', 'orgaos', \
							'orgaos_por_id', 'outros_autores_proposicoes', \
							'outros_autores_proposicoes_por_nome', \
							'deputados_antigos', \
							'deputados_antigos_por_nome'], pasta_temporaria)
					
					estado[2:] = [1, ano + 1]
					salva_dados(estado, arquivo_estado)
			
				estado[2:] = [2]
				salva_dados(estado, arquivo_estado)
			
			if estado[2] == 2: # TODO Adicionar aos dados
				n_proposicoes = len(proposicoes)

				print "-- Obtendo dados de referências entre %s proposições" \
					% n_proposicoes
				
				proposicoes_dados = filter(lambda a: not a['tipo'] in \
					dados_proposicoes.NAO_REFERENCIAVEIS, filter(lambda a: \
					'emendas' not in a.keys(), proposicoes.values()))
				n_lotes = int(math.ceil(float(len(proposicoes_dados)) / \
					lote_requisicoes))
				
				for i in range(n_lotes):
					print "--- Lote %s de %s" % (i + 1, n_lotes)
					
					dados_orgaos.obter_proposicoes_referentes( \
						proposicoes_dados[i * lote_requisicoes:(i + 1) * \
						lote_requisicoes], proposicoes, proposicoes_por_nome, \
						regimes_proposicoes, regimes_proposicoes_por_nome, \
						apreciacoes_proposicoes, \
						apreciacoes_proposicoes_por_nome, deputados, \
						deputados_por_nome, partidos_por_sigla, blocos, \
						blocos_por_sigla, orgaos, orgaos_por_id, \
						outros_autores_proposicoes, \
						outros_autores_proposicoes_por_nome, \
						deputados_antigos, deputados_antigos_por_nome)
					
					salva_lista_dados(['proposicoes', 'proposicoes_por_nome', \
						'regimes_proposicoes', 'regimes_proposicoes_por_nome', \
						'apreciacoes_proposicoes', \
						'apreciacoes_proposicoes_por_nome', 'deputados', \
						'deputados_por_nome', 'partidos_por_sigla', 'blocos', \
						'blocos_por_sigla', 'orgaos', 'orgaos_por_id', \
						'outros_autores_proposicoes', \
						'outros_autores_proposicoes_por_nome', \
						'deputados_antigos', 'deputados_antigos_por_nome'], \
						pasta_temporaria)
					estado[2:] = [2]
					salva_dados(estado, arquivo_estado)
				
				estado[2:] = [3]
				salva_dados(estado, arquivo_estado)
			
			if estado[2] == 3: # TODO Adicionar aos dados
				n_proposicoes = len(proposicoes)
				
				print "-- Obtendo tramitações das %s proposições" % \
					n_proposicoes
				
				proposicoes_chaves = list(set(proposicoes.keys()) - \
					set(andamentos.keys()))
				n_lotes = int(math.ceil(float(len(proposicoes_chaves)) / \
					lote_requisicoes))
				
				for i in range(n_lotes):
					print "--- Lote %s de %s" % (i + 1, n_lotes)
					
					dados_orgaos.obter_andamentos(andamentos, \
						proposicoes_chaves[i * lote_requisicoes:(i + 1) * \
						lote_requisicoes], proposicoes, orgaos, orgaos_por_id, \
						aux_map=t_map)
					
					salva_lista_dados(['andamentos', 'orgaos', \
						'orgaos_por_id'], pasta_temporaria)
					estado[2:] = [3]
					salva_dados(estado, arquivo_estado)
				
				estado[2:] = [4]
				salva_dados(estado, arquivo_estado)

			if estado[2] == 4: # TODO Adicionar aos dados
				n_proposicoes = len(proposicoes)

				print "-- Obtendo relatórios das %s proposições" % \
					n_proposicoes
				
				proposicoes_chaves = list(set(proposicoes.keys()) - \
					set(relatorios_proposicoes.keys()))
				n_lotes = int(math.ceil(float(len(proposicoes_chaves)) / \
					lote_requisicoes))
				
				for i in range(n_lotes):
					print "--- Lote %s de %s" % (i + 1, n_lotes)
					
					proposicoes_sem_link = filter(lambda a: not 'link_teor' in \
						proposicoes[a].keys(), proposicoes_chaves[i * \
						lote_requisicoes:(i + 1) * lote_requisicoes])
					
					dados_orgaos.obter_relatorios(relatorios_proposicoes, \
						proposicoes_chaves[i * lote_requisicoes:(i + 1) * \
						lote_requisicoes], proposicoes, deputados, \
						deputados_por_nome, deputados_antigos, \
						deputados_antigos_por_nome, partidos_por_sigla, \
						orgaos, orgaos_por_id, aux_map=t_map)
					
					salva_lista_dados(['relatorios_proposicoes', 'deputados', \
						'deputados_por_nome', 'deputados_antigos', \
						'deputados_antigos_por_nome', 'partidos_por_sigla', \
						'orgaos', 'orgaos_por_id'], pasta_temporaria)
					
					if True in map(lambda a: 'link_teor' in a.keys(), \
						proposicoes_sem_link):
						
						salva_lista_dados(['proposicoes'], pasta_temporaria)
					
					estado[2:] = [4]
					salva_dados(estado, arquivo_estado)
				
				estado[1:] = [2, 0, None]
				salva_dados(estado, arquivo_estado)
		
		if estado[1] == 2:
			print "- Obtendo informações de sessões da Câmara..."

			if estado[2] == 0: # TODO Adicionar aos dados
				presencas = {}
				
				if restaura_execucao == True:
					[partidos, partidos_por_sigla, blocos, blocos_por_sigla, \
						orgaos, orgaos_por_id, deputados, deputados_por_nome, \
						tipos_proposicoes, tipos_situacoes_proposicoes, \
						tipos_autores_proposicoes, proposicoes, \
						proposicoes_por_nome, regimes_proposicoes, \
						regimes_proposicoes_por_nome, apreciacoes_proposicoes, \
						apreciacoes_proposicoes_por_nome, \
						outros_autores_proposicoes, \
						outros_autores_proposicoes_por_nome, \
						deputados_antigos, deputados_antigos_por_nome, \
						lista_votadas] = carrega_lista_dados(['partidos', \
						'partidos_por_sigla', 'blocos', 'blocos_por_sigla', \
						'orgaos', 'orgaos_por_id', 'deputados', \
						'deputados_por_nome', 'tipos_proposicoes', \
						'tipos_situacoes_proposicoes', \
						'tipos_autores_proposicoes', 'proposicoes', \
						'proposicoes_por_nome', 'regimes_proposicoes', \
						'regimes_proposicoes_por_nome', \
						'apreciacoes_proposicoes', \
						'apreciacoes_proposicoes_por_nome', \
						'outros_autores_proposicoes', \
						'outros_autores_proposicoes_por_nome', \
						'deputados_antigos', 'deputados_antigos_por_nome', \
						'lista_votadas'], pasta_temporaria)
					
					try:
						[presencas] = carrega_lista_dados(['presencas'], \
							pasta_temporaria)
					except IOError:
						pass
					
					restaura_execucao = False
			
				ano_obtendo_salvo = estado[3]
				ano_obtendo = ano_obtendo_salvo if ano_obtendo_salvo != None \
					else ano_inicial_sessoes
			
				for ano in range(ano_obtendo, ano_final + 1):
					print "-- Obtendo presenças em sessoes em %s" % ano,
				
					data_inicio = datetime.date(ano, 1, 1)
					data_final = datetime.date(ano, 12, 31)
				
					presencas_ano = dados_sessoes.get_presencas(deputados, \
						deputados_por_nome, deputados_antigos, \
						deputados_antigos_por_nome, partidos_por_sigla, \
						data_inicio, data_final, aux_map=t_map)
				
					presencas = dict(presencas.items() + presencas_ano.items())
					
					print "(%s sessoes)" % len(presencas_ano.keys())
				
					salva_lista_dados(['presencas', 'deputados', \
						'deputados_por_nome', 'deputados_antigos', \
						'deputados_antigos_por_nome'], pasta_temporaria)
					estado[2:] = [0, ano + 1]
					salva_dados(estado, arquivo_estado)
				
				estado[2:] = [1, None]
				salva_dados(estado, arquivo_estado)
			
			if estado[2] == 1: # TODO Adicionar aos dados
				discursos = []
			
				if restaura_execucao == True:
					[partidos_por_sigla, deputados, deputados_por_nome, \
						deputados_antigos, deputados_antigos_por_nome, \
						proposicoes, proposicoes_por_nome, \
						regimes_proposicoes, regimes_proposicoes_por_nome, \
						apreciacoes_proposicoes, \
						apreciacoes_proposicoes_por_nome, orgaos, \
						orgaos_por_id, outros_autores_proposicoes, \
						outros_autores_proposicoes_por_nome, blocos_por_sigla] \
						= carrega_lista_dados(['partidos_por_sigla', \
						'deputados', 'deputados_por_nome', \
						'deputados_antigos', 'deputados_antigos_por_nome', \
						'proposicoes', 'proposicoes_por_nome', \
						'regimes_proposicoes', 'regimes_proposicoes_por_nome', \
						'apreciacoes_proposicoes', \
						'apreciacoes_proposicoes_por_nome', 'orgaos', \
						'orgaos_por_id', 'outros_autores_proposicoes', \
						'outros_autores_proposicoes_por_nome', \
						'blocos_por_sigla'], pasta_temporaria)
					
					try:
						[discursos] = carrega_lista_dados(['discursos'], \
							pasta_temporaria)
					except IOError:
						pass

					restaura_execucao = False
			
				ano_obtendo_salvo = estado[3]
				ano_obtendo = ano_obtendo_salvo if ano_obtendo_salvo != None \
					else ano_inicial_discursos
			
				for ano in range(ano_obtendo, ano_final + 1):
					print "-- Obtendo discursos feitos em %s" % ano,
				
					data_inicio = datetime.date(ano, 1, 1)
					data_final = datetime.date(ano, 12, 31)
					
					discursos_ano = dados_sessoes.get_discursos(deputados, \
						deputados_por_nome, deputados_antigos, \
						deputados_antigos_por_nome, partidos_por_sigla, \
						data_inicio, data_final, aux_map=t_map)
				
					discursos = discursos + discursos_ano
				
					print "(%s discursos)" % len(discursos_ano)
				
					salva_lista_dados(['discursos', 'deputados', \
						'deputados_por_nome', 'deputados_antigos', \
						'deputados_antigos_por_nome'], pasta_temporaria)
					estado[2:] = [1, ano + 1]
					salva_dados(estado, arquivo_estado)
			
			estado[1:] = [3]
			salva_dados(estado, arquivo_estado)

		if estado[1] == 3:
			print "- Obtendo informações de pautas dos órgãos da Câmara..."

			if restaura_execucao == True:
				[partidos_por_sigla, deputados, deputados_por_nome, \
					deputados_antigos, deputados_antigos_por_nome, \
					proposicoes, proposicoes_por_nome, regimes_proposicoes, \
					regimes_proposicoes_por_nome, apreciacoes_proposicoes, \
					apreciacoes_proposicoes_por_nome, orgaos, orgaos_por_id, \
					outros_autores_proposicoes, \
					outros_autores_proposicoes_por_nome, blocos_por_sigla] = \
					carrega_lista_dados(['partidos_por_sigla', 'deputados', \
					'deputados_por_nome', 'deputados_antigos', \
					'deputados_antigos_por_nome', 'proposicoes', \
					'proposicoes_por_nome', 'regimes_proposicoes', \
					'regimes_proposicoes_por_nome', 'apreciacoes_proposicoes', \
					'apreciacoes_proposicoes_por_nome', 'orgaos', \
					'orgaos_por_id', 'outros_autores_proposicoes', \
					'outros_autores_proposicoes_por_nome', \
					'blocos_por_sigla'], pasta_temporaria)
				restaura_execucao = False
			
			data_inicio = datetime.date(ano_inicial_sessoes, 1, 1)
			data_final = datetime.date(ano_final, 12, 31)
			
			orgaos_aux = filter(lambda a: not 'reunioes' in a.keys(), \
				orgaos.values())
			tamanho_lote_aux = 5 * NUM_THREADS_PADRAO
			n_lotes = int(math.ceil(float(len(orgaos_aux)) / tamanho_lote_aux))
			
			for i in range(n_lotes):
				print "-- Lote %s de %s" % (i + 1, n_lotes)
				
				dados_orgaos.obter_pautas_reunioes(data_inicio, data_final, \
					orgaos_aux[i * tamanho_lote_aux:(i + 1) * \
					tamanho_lote_aux], orgaos, orgaos_por_id, proposicoes, \
					proposicoes_por_nome, regimes_proposicoes, \
					regimes_proposicoes_por_nome, apreciacoes_proposicoes, \
					apreciacoes_proposicoes_por_nome, deputados, \
					deputados_por_nome, deputados_antigos, \
					deputados_antigos_por_nome, partidos_por_sigla, \
					outros_autores_proposicoes, \
					outros_autores_proposicoes_por_nome, aux_map=t_map)
					
				salva_lista_dados(['proposicoes', 'proposicoes_por_nome', \
					'regimes_proposicoes', 'regimes_proposicoes_por_nome', \
					'apreciacoes_proposicoes', \
					'apreciacoes_proposicoes_por_nome', 'orgaos', \
					'orgaos_por_id', 'outros_autores_proposicoes', \
					'outros_autores_proposicoes_por_nome'], \
					pasta_temporaria)
				estado[1:] = [3]
				salva_dados(estado, arquivo_estado)

			estado[1:] = [4]
			salva_dados(estado, arquivo_estado)

		if estado[1] == 4:
			chaves_inteiros_teores = []
			
			if restaura_execucao == True:
				[partidos_por_sigla, deputados, deputados_por_nome, \
					deputados_antigos, deputados_antigos_por_nome, \
					proposicoes, blocos_por_sigla, orgaos, orgaos_por_id] = \
					carrega_lista_dados(['partidos_por_sigla', 'deputados', \
					'deputados_por_nome', 'deputados_antigos', \
					'deputados_antigos_por_nome', 'proposicoes', \
					'blocos_por_sigla', 'orgaos', 'orgaos_por_id'], \
					pasta_temporaria)
				
				try:
					[chaves_inteiros_teores] = carrega_lista_dados( \
						['chaves_inteiros_teores'], pasta_temporaria)
				except IOError:
					pass
				
				restaura_execucao = False
			
			n_proposicoes = len(proposicoes)
			
			print "- Obtendo teores de %s proposições" % n_proposicoes
			
			proposicoes_chaves = sorted(list(set(proposicoes.keys()) - \
				set(chaves_inteiros_teores)), key=lambda i: proposicoes[i] \
				['data_apresentacao'], reverse=True)
			
			n_lotes = int(math.ceil(float(len(proposicoes_chaves)) / \
				lote_requisicoes))
			
			def salva_inteiros_teores(inteiros_teores, chaves, nome_pasta):
				salva_dados(inteiros_teores, nome_pasta + '/inteiros_teores_' \
					+ str(chaves[0]) + '_' + str(chaves[-1]) + '.pkl')
			
			for i in range(n_lotes):
				print "-- Lote %s de %s" % (i + 1, n_lotes)
				
				inteiros_teores = {}
				chaves_aux = proposicoes_chaves[i * lote_requisicoes:(i + 1) * \
					lote_requisicoes]
				dados_proposicoes.get_teores(inteiros_teores, chaves_aux, \
					proposicoes, aux_map=p_map)
				chaves_inteiros_teores += chaves_aux

				salva_inteiros_teores(inteiros_teores, chaves_aux, \
					pasta_temporaria)
				salva_lista_dados(['chaves_inteiros_teores'], pasta_temporaria)
				estado[1:] = [4]
				salva_dados(estado, arquivo_estado)
			
			estado[1:] = [5, None]
			salva_dados(estado, arquivo_estado)
		
		if estado[1] == 5:
			if restaura_execucao == True:
				[partidos_por_sigla, deputados, deputados_por_nome, \
					deputados_antigos, deputados_antigos_por_nome, \
					blocos_por_sigla, orgaos, orgaos_por_id] = \
					carrega_lista_dados(['partidos_por_sigla', 'deputados', \
					'deputados_por_nome', 'deputados_antigos', \
					'deputados_antigos_por_nome', 'blocos_por_sigla', \
					'orgaos', 'orgaos_por_id'], pasta_temporaria)
				restaura_execucao = False
			
			print "- Obtendo dados de gastos das cotas parlamentares..."
			
			despesas = dados_cotas_parlamentares.get_despesas(deputados, \
				deputados_por_nome, deputados_antigos, \
				deputados_antigos_por_nome, partidos_por_sigla, \
				blocos_por_sigla, orgaos, orgaos_por_id)

			salva_lista_dados(['despesas', 'deputados', 'deputados_por_nome', \
				'deputados_antigos', 'deputados_antigos_por_nome', \
				'blocos_por_sigla', 'orgaos', 'orgaos_por_id'], \
				pasta_temporaria)
		
		estado = [1]
		salva_dados(estado, arquivo_estado)

	if estado[0] == 1:
		if restaura_execucao == True:
			[deputados] = carrega_lista_dados(['deputados'], pasta_temporaria)
			restaura_execucao = False

		print "Obtendo dados do IBGE..."

		municipios, municipios_por_cod_tse = dados_ibge.get_municipios()
		
		salva_lista_dados(['municipios', 'municipios_por_cod_tse'], \
			pasta_temporaria)
		estado = [2]
		salva_dados(estado, arquivo_estado)

	if estado[0] == 2:
		if restaura_execucao == True:
			[deputados, municipios, municipios_por_cod_tse] = \
				carrega_lista_dados(['deputados', 'municipios', \
				'municipios_por_cod_tse'], pasta_temporaria)
			restaura_execucao = False

		print "Obtendo arquivos do TSE..."

		dados_tse.obtem_arquivos()

		print "Processando arquivos do TSE..."

		deputados_por_nome_completo, deputados_por_nome_completo_na = \
			dados_tse.indices_deputados(deputados)
		deputados_por_seq, deputados_por_nome_tse = dados_tse.get_candidatos( \
			deputados, deputados_por_nome_completo, \
			deputados_por_nome_completo_na)
		dados_tse.get_bens_candidatos(deputados, deputados_por_seq)
		votacoes = dados_tse.get_votacoes(deputados_por_seq, municipios, \
			municipios_por_cod_tse)
		dados_tse.get_receitas(deputados, deputados_por_nome_tse)
		dados_tse.get_despesas(deputados, deputados_por_nome_tse)

		salva_lista_dados(['deputados_por_nome_completo', \
			'deputados_por_nome_completo_na', 'deputados_por_seq', \
			'deputados_por_nome_tse', 'deputados', 'municipios', \
			'municipios_por_cod_tse'], pasta_temporaria)

	print "Salvando dados..."
	
	shutil.copytree(pasta_temporaria, pasta_final)
	
	print "Finalizado com sucesso!"

def cria_parser():
	parser = argparse.ArgumentParser(description="Obtem e cruza dados sobre " \
		"deputados federais.")

	parser.add_argument('-e', '--arquivo-estado', action='store', \
		default='estado.part', help='Arquivo que contém informação sobre o ' \
		'estado da execução, para reinício em caso de problemas')
	parser.add_argument('-r', '--restaura-estado', action='store_true', \
		help='Restaura o estado da execução a partir do arquivo de estado ' \
		'indicado pelo parâmetro "-e", recuperando as informações já ' \
		'obtidas a partir do arquivo indicado pelo parâmetro "-t"')
	parser.add_argument('-t', '--dados-temporario', action='store', \
		default='dados_deputados.part', help='Pasta onde devem ser salvos os ' \
		'dados parciais já obtidos, para restauro da execução em caso de ' \
		'problemas')
	parser.add_argument('-f', '--dados-final', action='store', \
		default='dados_deputados', help='Pasta onde devem ser salvos os dados' \
		' obtidos ao final da execução')
	parser.add_argument('-a', '--ano-final', action='store', type=int, \
		default=datetime.datetime.now().year, help='Último ano para o qual ' \
		'devem ser obtidos dados sobre proposições e votações')
	parser.add_argument('-v', '--periodo-votacoes', action='store', \
		type=int, default=PERIODO_VOTACOES_PADRAO, help='Quantidade de anos ' \
		'anteriores para os quais devem ser obtidos dados de votações')
	parser.add_argument('-p', '--periodo-proposicoes', action='store', \
		type=int, default=PERIODO_PROPOSICOES_PADRAO, help='Quantidade de ' \
		'anos anteriores para os quais devem ser obtidos todos os dados de ' \
		'proposições')
	parser.add_argument('-s', '--periodo-sessoes', action='store', \
		type=int, default=PERIODO_SESSOES_PADRAO, help='Quantidade de anos ' \
		'anteriores para os quais devem ser obtidos todos os dados de sessões')
	parser.add_argument('-d', '--periodo-discursos', action='store', \
		type=int, default=PERIODO_DISCURSOS_PADRAO, help='Quantidade de anos ' \
		'anteriores para os quais devem ser obtidos todos os discursos ' \
		'realizados')
	parser.add_argument('-l', '--lote-requisicoes', action='store', \
		type=int, default=LOTE_REQUISICOES_PADRAO, help='Define o número ' \
		'máximo de requisições realizadas entre o salvamento dos dados ao ' \
		'fazer uma operação com um número muito grande de requisições')
	parser.add_argument('-n', '--num-threads', action='store', \
		type=int, default=NUM_THREADS_PADRAO, help='Número de threads a ' \
		'serem usadas para obter os dados')
	
	return parser

if __name__ == "__main__":
	parser = cria_parser()
	args = parser.parse_args()
	
	restaura_execucao = args.restaura_estado
	arquivo_estado = args.arquivo_estado
	pasta_temporaria = args.dados_temporario
	pasta_final = args.dados_final
	ano_final = args.ano_final
	ano_inicial_proposicoes = ano_final - args.periodo_proposicoes
	ano_inicial_votacoes = ano_final - args.periodo_votacoes
	ano_inicial_sessoes = ano_final - args.periodo_sessoes
	ano_inicial_discursos = ano_final - args.periodo_discursos
	lote_requisicoes = args.lote_requisicoes
	num_threads = args.num_threads
	
	estado = [0] * 3
	
	if restaura_execucao:
		estado = carrega_dados(arquivo_estado)
	else:
		if os.path.exists(arquivo_estado):
			resposta = raw_input("O arquivo de estado '%s' existe. Você "  \
				"deseja carregar o estado de execução a partir dele? [s/n] " % \
				arquivo_estado).upper().strip()
		
			if resposta == "SIM" or resposta == "S":
				restaura_execucao = True
				estado = carrega_dados(arquivo_estado)
			elif not (resposta == "NÃO" or resposta == "NAO" or \
				resposta == "N"):
				
				raise ValueError("Resposta inválida!")
	
	logging.getLogger('suds.client').setLevel(logging.CRITICAL)
	obtem_dados(estado, restaura_execucao, arquivo_estado, pasta_temporaria, \
		pasta_final, ano_final, ano_inicial_proposicoes, \
		ano_inicial_votacoes, ano_inicial_sessoes, ano_inicial_discursos, \
		lote_requisicoes)

