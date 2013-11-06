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

import deputados as dados_deputados
import datetime
import urllib
import zipfile
import numpy as np
import os
import re
from fontes.geral import *
import fontes.camara.orgaos as dados_orgaos

TAMANHO_BUFFER_DESPESA = 1000

def atributo(estrutura, campo):
	try:
		dado = estrutura[campo]
	except KeyError:
		dado = ''
	
	return dado if dado != None else ''

def atributo_tipo(tipo, estrutura, campo):
	try:
		return tipo(atributo(estrutura, campo))
	except ValueError:
		return 0

def obtem_dados(nome_arquivo, despesas, deputados, deputados_por_nome, \
	deputados_antigos, deputados_antigos_por_nome, partidos_por_sigla, \
	blocos_por_sigla, orgaos, orgaos_por_id):
	
	arquivo_despesas = open(nome_arquivo, 'r')
	buffer_texto = ''
	
	while True:
		# Processa o arquivo
		blocos_despesas = buffer_texto.split('</DESPESA>', 1)
	
		if len(blocos_despesas) <= 1:
			lido = arquivo_despesas.read(TAMANHO_BUFFER_DESPESA). \
				decode('cp852').encode('utf8')
		
			if lido == '':
				break
		
			buffer_texto += lido
			continue
		
		buffer_texto = blocos_despesas[1]
		
		texto_despesa = blocos_despesas[0].split('<DESPESA>')[1]
		partes_despesa = re.split(r'\<([^\>]+[^\/])\>', texto_despesa)
		chaves_sem_dados = [p[1:-2] for p in partes_despesa[::4] if p != '']
		
		despesa = dict(zip(partes_despesa[1::4] + chaves_sem_dados, \
			partes_despesa[2::4] + ([''] * len(chaves_sem_dados))))
		
		# Registra despesa
		nome_origem = uniformiza(atributo(despesa, 'txNomeParlamentar'))
		
		try:
			uf = normaliza(despesa['sgUF'])
			partido = normaliza(despesa['sgPartido'])
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
		except KeyError:
			try:
				id_origem = partidos_por_sigla[nome_origem.replace(' ', '')]
				tipo_origem = 'partido'
			except KeyError:
				if normaliza(nome_origem) in orgaos.keys():
					tipo_origem = 'orgao'
					id_origem = normaliza(nome_origem)
				elif nome_origem[:4] == uniformiza('LID.') or \
					nome_origem[:5] == uniformiza(u'LIDER') or \
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
						tipo_origem = 'lideranca_part'
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
		
		try:
			valor_documento = despesa['vlrDocumento']
		except KeyError:
			valor_documento = 0.
		
		try:
			data_emissao = datetime.datetime.strptime(atributo(despesa, \
				'datEmissao').split('.')[0], '%Y-%m-%dT%H:%M:%S')
		except ValueError:
			data_emissao = None
		
		despesas[tipo_origem][id_origem].append({ \
			'cod_tipo_despesa': atributo_tipo(int, despesa, 'numSubCota'), \
			'cod_tipo_detalhado': \
				atributo_tipo(int, despesa, 'numEspecificacaoSubCota'), \
			'descricao': atributo(despesa, 'txtDescricao'), \
			'descricao_detalhada': descricao_detalhada, \
			'beneficiario': atributo(despesa, 'txtBeneficiario'), \
			'pessoa_fisica': len(aux_cpf_cnpj) == 11, \
			'cpf_cnpj': int(aux_cpf_cnpj) if aux_cpf_cnpj != '' else -1, \
			'tipo_documento': \
				atributo_tipo(int, despesa, 'indTipoDocumento'), \
			'numero_documento': atributo(despesa, 'txtNumero'), \
			'data_emissao': data_emissao, \
			'valor_documento': float(valor_documento) if \
				valor_documento != None else 0., \
			'valor_glosa': atributo_tipo(float, despesa, 'vlrGlosa'), \
			'valor_liquido': atributo_tipo(float, despesa, 'vlrLiquido'), \
			'mes_debito': atributo_tipo(int, despesa, 'numMes'), \
			'ano_debito': atributo_tipo(int, despesa, 'numAno'), \
			'num_parcela': atributo_tipo(int, despesa, 'numParcela'), \
			'num_lote': atributo_tipo(int, despesa, 'numLote'), \
			'num_ressarcimento': \
				atributo_tipo(int, despesa, 'numRessarcimento')})

FONTES = { \
	'ano_atual': { \
		'link': 'http://www.camara.gov.br/cotas/AnoAtual.zip', \
		'arquivo': 'AnoAtual.xml'}, \
	'ano_anterior': { \
		'link': 'http://www.camara.gov.br/cotas/AnoAnterior.zip', \
		'arquivo': 'AnoAnterior.xml'}, \
	'anos_anteriores': { \
		'link': 'http://www.camara.gov.br/cotas/AnosAnteriores.zip', \
		'arquivo': 'AnosAnteriores.xml'} \
	}

def get_despesas(deputados, deputados_por_nome, deputados_antigos, \
	deputados_antigos_por_nome, partidos_por_sigla, blocos_por_sigla, orgaos, \
	orgaos_por_id, fonte):
	
	despesas = {}
	
	dir_dados = "/tmp/camara_dados_%d/" % (np.random.random() * \
		np.iinfo(np.int32).max)
	os.makedirs(dir_dados)
	
	if fonte == FONTES['anos_anteriores']:
		arquivo_xml = '/tmp/camara_dados_1208382974/AnosAnteriores.xml'
	else:
		arquivo_nome, dummy = urllib.urlretrieve(fonte['link'])
	
		with zipfile.ZipFile(arquivo_nome, 'r') as arquivo_zip:
			arquivo_zip.extractall(path=dir_dados)
		
		arquivo_xml = dir_dados + fonte['arquivo']
	
	obtem_dados(arquivo_xml, despesas, deputados, \
		deputados_por_nome, deputados_antigos, deputados_antigos_por_nome, \
		partidos_por_sigla, blocos_por_sigla, orgaos, orgaos_por_id)
	
	return despesas

