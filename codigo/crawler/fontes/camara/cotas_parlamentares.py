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

import xml.etree.ElementTree as et
import deputados as dados_deputados
import datetime
import urllib
import zipfile
import numpy as np
import os
from fontes.geral import *
import fontes.camara.orgaos as dados_orgaos

def atributo(estrutura, campo):
	try:
		dado = estrutura.find(campo).text
	except AttributeError:
		dado = ''
	
	return dado if dado != None else ''

def atributo2(estrutura, campo):
	dado = estrutura.find(campo).text
	
	if dado == None:
		raise AttributeError()
	
	return dado

def atributo_tipo(tipo, estrutura, campo):
	try:
		return tipo(atributo(estrutura, campo))
	except ValueError:
		return 0

def obtem_dados(arquivo, despesas, deputados, deputados_por_nome, \
	deputados_antigos, deputados_antigos_por_nome, partidos_por_sigla, \
	blocos_por_sigla, orgaos, orgaos_por_id):
	
	dados_arquivo = et.parse(arquivo)
	raiz_dados = dados_arquivo.getroot()
	
	for despesa in raiz_dados[0].iter('DESPESA'):
		nome_origem = normaliza(atributo(despesa, 'txNomeParlamentar'))
		
		try:
			uf = normaliza(atributo2(despesa, 'sgUF'))
			partido = normaliza(atributo2(despesa, 'sgPartido'))
			id_origem = dados_deputados.obtem_deputado_por_nome(nome_origem, \
				partido, uf, deputados, deputados_por_nome, deputados_antigos, \
				deputados_antigos_por_nome, partidos_por_sigla)
	
			if id_origem < 0:
				deputado = deputados_antigos[id_origem]
			else:
				deputado = deputados[id_origem]
	
			deputado['matricula'] = \
				atributo_tipo(int, despesa, 'nuCarteiraParlamentar')
			deputado['legislaturas'].add(atributo_tipo(int, despesa, \
				'codLegislatura'))
			
			tipo_origem = 'deputado'
		except AttributeError:
			try:
				id_origem = partidos_por_sigla[nome_origem.replace(' ', '')]
				tipo_origem = 'partidos'
			except KeyError:
				if normaliza(nome_origem) in orgaos.keys():
					tipo_origem = 'orgaos'
					id_origem = normaliza(nome_origem)
				elif nome_origem[:4] == uniformiza('LID.') or \
					nome_origem[:9] == uniformiza(u'LIDERANÇA') or \
					nome_origem == uniformiza('MINORIA-CN') or \
					nome_origem == uniformiza('LIDMIN'):
				
					if nome_origem[:3] == 'LID':
						if not (' ' in nome_origem or '.' in nome_origem):
							aux = nome_origem[3:]
						else:
							aux = nome_origem.split(' ')[-1].split('.')[-1]
					else:
						aux = 'MIN-CN'
				
					try:
						aux2 = aux.split('-')
						tipo_origem = 'lideranca_cn' if aux2[1] == 'CN' else \
							'lideranca_cd'
						aux = aux2[0]
					except IndexError:
						tipo_origem = 'lideranca_cd'
				
					try:
						id_origem = partidos_por_sigla[aux.replace(' ', '')]
						tipo = 'lideranca_part'
					except KeyError:
						if aux[:3] == 'MIN':
							id_origem = blocos_por_sigla['MINORIA']
						elif aux[:3] == 'GOV':
							id_origem = blocos_por_sigla['GOVERNO']
				else:
					dados_orgaos.adiciona_orgao(orgaos, orgaos_por_id, \
						nome_origem)
					id_origem = nome_origem
					tipo_origem = 'orgao'
		
		if not tipo_origem in despesas.keys():
			despesas[tipo_origem] = {}
		
		if not id_origem in despesas[tipo_origem].keys():
			despesas[tipo_origem][id_origem] = []
		
		aux_cpf_cnpj = atributo(despesa, 'txtCNPJCPF')
		descricao_detalhada = atributo(despesa, 'txtDescricaoEspecificacao')
		valor_documento = despesa.find('vlrDocumento')
		
		try:
			data_emissao = datetime.datetime.strptime(atributo(despesa, \
				'datEmissao').split('.')[0], '%Y-%m-%dT%H:%M:%S')
		except ValueError:
			data_emissao = None
		
		despesas[tipo_origem][id_origem].append({ \
			'cod_tipo_despesa': atributo_tipo(int, despesa, 'numSubCota'), \
			'cod_tipo_detalhado': \
				atributo_tipo(int, despesa, 'numEspecificacaoSubCota'), \
			'descricao': atributo(despesa, 'txtDescricao'). \
				encode('iso-8859-1'), \
			'descricao_detalhada': descricao_detalhada.encode('iso-8859-1'), \
			'beneficiario': \
				atributo(despesa, 'txtBeneficiario').encode('iso-8859-1'), \
			'pessoa_fisica': len(aux_cpf_cnpj) == 11, \
			'cpf_cnpj': int(aux_cpf_cnpj) if aux_cpf_cnpj != '' else -1, \
			'tipo_documento': \
				atributo_tipo(int, despesa, 'indTipoDocumento'), \
			'numero_documento': \
				atributo(despesa, 'txtNumero').encode('iso-8859-1'), \
			'data_emissao': data_emissao, \
			'valor_documento': float(valor_documento.text) if \
				valor_documento != None else 0., \
			'valor_glosa': atributo_tipo(float, despesa, 'vlrGlosa'), \
			'valor_liquido': atributo_tipo(float, despesa, 'vlrLiquido'), \
			'mes_debito': atributo_tipo(int, despesa, 'numMes'), \
			'ano_debito': atributo_tipo(int, despesa, 'numAno'), \
			'num_parcela': atributo_tipo(int, despesa, 'numParcela'), \
			'num_lote': atributo_tipo(int, despesa, 'numLote'), \
			'num_ressarcimento': \
				atributo_tipo(int, despesa, 'numRessarcimento')})

def get_despesas(deputados, deputados_por_nome, deputados_antigos, \
	deputados_antigos_por_nome, partidos_por_sigla, blocos_por_sigla, orgaos, \
	orgaos_por_id):
	
	fontes = [{ \
		'link': 'http://www.camara.gov.br/cotas/AnoAtual.zip', \
		'arquivo': 'AnoAtual.xml'}, { \
		'link': 'http://www.camara.gov.br/cotas/AnoAnterior.zip', \
		'arquivo': 'AnoAnterior.xml'}]#, { \
	#	'link': 'http://www.camara.gov.br/cotas/AnosAnteriores.zip', \
	#	'arquivo': 'AnosAnteriores.xml'}]
	
	dir_dados = "/tmp/camara_dados_%d/" % (np.random.random() * \
		np.iinfo(np.int32).max)
	os.makedirs(dir_dados)
	
	despesas = {}
	
	for fonte in fontes:
		arquivo_nome, dummy = urllib.urlretrieve(fonte['link'])
		
		with zipfile.ZipFile(arquivo_nome, 'r') as arquivo_zip:
			arquivo_zip.extractall(path=dir_dados)
		
		obtem_dados(dir_dados + fonte['arquivo'], despesas, deputados, \
			deputados_por_nome, deputados_antigos, deputados_antigos_por_nome, \
			partidos_por_sigla, blocos_por_sigla, orgaos, orgaos_por_id)
	
	return despesas

