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

import suds
import suds.client as soap
import deputados as dados_deputados
import datetime
import re
import base64
import math
import itertools
from fontes.geral import *

MAX_DISCURSOS_POR_REQ = 100

wsdl_sessoes_file = "http://www.camara.gov.br/SitCamaraWS/" \
	"SessoesReunioes.asmx?wsdl"
cliente_sessoes = soap.Client(wsdl_sessoes_file)

def get_metadados():
	situacoes_reuniao = cliente_sessoes.service.situacaoReuniaoSessao()
	
	dict_situacoes = {}
	
	for situacao in certifica_lista(situacoes_reuniao, 'situacaoReuniao'):
		dict_situacoes[int(situacao._id)] = uniformiza(situacao._descricao)
	
	return dict_situacoes

def texto_do_rtf(dado):
	texto = base64.b64decode(dado)
	texto = re.sub(r'\{[^}]*\}+', '', texto)
	lista = re.split(r"\\\'([a-f0-9]{2})", texto)
	
	for i in range(len(lista) / 2):
		lista[2 * i + 1] = unichr(int(lista[2 * i + 1], 16))
	
	texto = "".join(lista)
	texto = re.sub(r'\\[A-Za-z0-9]+', '', texto)
	texto = re.sub(r'\}\s*\Z', '', texto)
	
	return re.sub(r'(\A\s+|\s+\Z)', '', re.sub(r'\}[^\}]+\Z', '', \
		re.sub(r'(\n\ *)+', '\n', re.sub(r'[\ \t\r]+', ' ', texto))))

def _get_discursos(datas):
	sessoes = cliente_sessoes.service.ListarDiscursosPlenario( \
		datas[0].strftime("%d/%m/%Y"), datas[1].strftime("%d/%m/%Y"))
	
	return certifica_lista(sessoes.sessoesDiscursos, 'sessao')

def get_discursos(deputados, deputados_por_nome, deputados_antigos, \
	deputados_antigos_por_nome, partidos_por_sigla, data_inicio, data_final, \
	aux_map=map):
	
	discursos = []
	
	n_iters = int(math.ceil((data_final - data_inicio).days / \
		float(MAX_DISCURSOS_POR_REQ)))
	
	datas_sessoes = [[data_inicio + datetime.timedelta(i * \
		MAX_DISCURSOS_POR_REQ), min(data_final, data_inicio + \
		datetime.timedelta((i + 1) * MAX_DISCURSOS_POR_REQ))] \
		for i in range(n_iters)]
		
	lista_sessoes = itertools.chain(*aux_map(_get_discursos, datas_sessoes))
	
	for sessao in lista_sessoes:
		cod_sessao = uniformiza(sessao.codigo)
		data_sessao = formata_data(sessao.data)
		numero_sessao = int(sessao.numero)
		tipo_sessao = uniformiza(sessao.tipo)
	
		lista_fases = certifica_lista(sessao.fasesSessao, 'faseSessao')
	
		for fase in lista_fases:
			cod_fase = uniformiza(fase.codigo)
			descricao_fase = uniformiza(fase.descricao)
		
			lista_discursos = certifica_lista(fase.discursos, 'discurso')
		
			for discurso in lista_discursos:
				nome_orador = uniformiza(discurso.orador.nome)
				partido_orador = normaliza(discurso.orador.partido)
				uf_orador = uniformiza(discurso.orador.uf)

				if uf_orador == '' or partido_orador == '':
					continue
			
				nome_orador = re.sub(r'\ *\([A-Z]+\)', '', nome_orador)
				
				id_deputado = dados_deputados.obtem_deputado_por_nome( \
					nome_orador, partido_orador, uf_orador, deputados, \
					deputados_por_nome, deputados_antigos, \
					deputados_antigos_por_nome, partidos_por_sigla)
				
				if id_deputado == None:
					continue
				
				numero_orador = int(discurso.orador.numero)
				numero_quarto = int(discurso.numeroQuarto)
				numero_insercao = int(discurso.numeroInsercao)
				
				try:
					inteiro_teor = texto_do_rtf(cliente_sessoes.service. \
						obterInteiroTeorDiscursosPlenario(cod_sessao, \
						numero_orador, numero_quarto, numero_insercao). \
						sessao.discursoRTFBase64)
				except suds.WebFault:
					inteiro_teor = None
			
				discurso_deputado = { \
					'id_deputado': id_deputado, \
					'cod_sessao': cod_sessao, \
					'data_sessao': data_sessao, \
					'numero_sessao': numero_sessao, \
					'tipo_sessao': tipo_sessao, \
					'cod_fase': cod_fase, \
					'descricao_fase': descricao_fase, \
					'numero_orador': numero_orador, \
					'numero_quarto': numero_quarto, \
					'numero_insercao': numero_insercao, \
					'hora_inicio': formata_data(discurso.horaInicioDiscurso), \
					'sumario': discurso.sumario.strip().encode("utf-8"), \
					'inteiro_teor': inteiro_teor}
				
				discursos.append(discurso_deputado)
	
	return discursos

def _get_presencas(data_sessao):
	return cliente_sessoes.service.ListarPresencasDia(data_sessao. \
		strftime("%d/%m/%Y"))

def get_presencas(deputados, deputados_por_nome, deputados_antigos, \
	deputados_antigos_por_nome, partidos_por_sigla, data_inicio, data_final, \
	aux_map=map):
	
	dict_reunioes = {}
	
	lista_presencas = aux_map(_get_presencas, map(lambda a: data_inicio + \
		datetime.timedelta(a), range((data_final - data_inicio).days + 1)))
	
	for i in range(len(lista_presencas)):
		data_sessao = data_inicio + datetime.timedelta(i)
		presencas = lista_presencas[i]
		
		try:
			legislatura = int(presencas.dia.legislatura)
		except AttributeError:
			continue
		
		dict_reunioes[data_sessao] = { \
			'legislatura': legislatura, \
			'deputados': {}, \
			'sessoes': {}}
		info_reuniao = dict_reunioes[data_sessao]
		
		lista_deputados = certifica_lista(presencas.dia.parlamentares, \
			'parlamentar')
		
		for dados_deputado in lista_deputados:
			nome_parlamentar = re.split(r'\-[A-Za-z\.]+\/[A-Z]{2}', \
				uniformiza(dados_deputado.nomeParlamentar))[0]
			
			id_deputado = dados_deputados.obtem_deputado_por_nome( \
				nome_parlamentar, uniformiza(dados_deputado.siglaPartido), \
				dados_deputado.siglaUF.strip().upper(), deputados, \
				deputados_por_nome, deputados_antigos, \
				deputados_antigos_por_nome, partidos_por_sigla)
			
			if id_deputado == None:
				continue
			
			if id_deputado >= 0:
				deputado = deputados[id_deputado]
			else:
				deputado = deputados_antigos[id_deputado]
			
			deputado['legislaturas'].add(legislatura)
			info_reuniao['deputados'][id_deputado] = { \
				"frequencia": \
					normaliza(dados_deputado.descricaoFrequenciaDia), \
				"justificativa": \
					dados_deputado.justificativa.strip().encode("utf-8"), \
				"presenca_externa": int(dados_deputado.presencaExterna), \
				"sessoes": {}}
			info_deputado = info_reuniao['deputados'][id_deputado]
			
			lista_sessoes = certifica_lista(dados_deputado.sessoesDia, \
				'sessaoDia')
			
			for sessao in lista_sessoes:
				info_deputado['sessoes'][uniformiza(sessao.descricao)] = { \
					'presenca': normaliza(sessao.frequencia)}
				
				info_reuniao['sessoes'][uniformiza(sessao.descricao)] = { \
					'inicio': formata_data(sessao.inicio)}
	
	return dict_reunioes

