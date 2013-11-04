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
import proposicoes as dados_proposicoes
import xml
from fontes.geral import *

wsdl_orgaos_file = "http://www.camara.gov.br/SitCamaraWS/Orgaos.asmx?wsdl"
cliente_orgaos = soap.Client(wsdl_orgaos_file, timeout=3*60)

def get_metadados():
	tipos_orgaos = cliente_orgaos.service.ListarTiposOrgao()
	
	dict_tipos_orgaos = {}
	
	for tipo in certifica_lista(tipos_orgaos.tiposOrgaos, 'tipoOrgao'):
		dict_tipos_orgaos[int(tipo._id)] = uniformiza(tipo._descricao)
	
	cargos_orgaos = cliente_orgaos.service.ListarCargosOrgaosLegislativosCD()
	
	dict_cargos_orgaos = {}
	
	for cargo in certifica_lista(cargos_orgaos.cargosOrgaos, 'cargo'):
		dict_cargos_orgaos[int(cargo._id)] = uniformiza(cargo._descricao)
	
	return dict_tipos_orgaos, dict_cargos_orgaos

def get_orgaos():
	orgaos = cliente_orgaos.service.ObterOrgaos()
	
	dict_orgaos = {}
	dict_orgaos_por_id = {}
	
	for orgao in orgaos.orgaos.orgao:
		adiciona_orgao(dict_orgaos, dict_orgaos_por_id, orgao._sigla, \
			orgao._id, orgao._descricao)
	
	return dict_orgaos, dict_orgaos_por_id

def _obter_pautas_reunioes(dados):
	data_inicio, data_final, orgao = dados
	
	if orgao['id'] == None:
		return None
	
	try:
		return cliente_orgaos.service.ObterPauta(orgao['id'], \
			data_inicio.strftime("%d/%m/%Y"), data_final.strftime("%d/%m/%Y"))
	except xml.sax._exceptions.SAXParseException:
		return None

def obter_pautas_reunioes(data_inicio, data_final, orgaos_dados, orgaos, \
	orgaos_por_id, proposicoes, proposicoes_por_nome, regimes, \
	regimes_por_nome, apreciacoes, apreciacoes_por_nome, deputados, \
	deputados_por_nome, deputados_antigos, deputados_antigos_por_nome, \
	partidos_por_sigla, outros_autores, outros_autores_por_nome, aux_map=map):
	
	dados_pautas = aux_map(_obter_pautas_reunioes, map(lambda a: [data_inicio, \
		data_final, a], orgaos_dados))
	
	for i in range(len(orgaos_dados)):
		orgao = orgaos_dados[i]
		pautas = dados_pautas[i]
		orgao['reunioes'] = {}
		
		if pautas == None:
			continue
		
		try:
			descricao_orgao = ' - '.join(pautas.pauta._orgao.strip(). \
				split(' - ')[1:]).encode('utf-8')
		
			if orgao['descricao'] == None:
				orgao['descricao'] = descricao_orgao
		except AttributeError:
			continue
		
		lista_reunioes = certifica_lista(pautas.pauta, 'reuniao')
	
		for dados_reuniao in lista_reunioes:
			id_reuniao = int(dados_reuniao.codReuniao)
		
			lista_proposicoes = certifica_lista(dados_reuniao.proposicoes, \
				'proposicao')
		
			reuniao_proposicoes = []
		
			for proposicao in lista_proposicoes:
				try:
					reuniao_proposicoes.append(proposicoes_por_nome[normaliza( \
						proposicao.sigla)])
				except KeyError:
					# Recuperar os dados das proposições faltantes
					dados_proposicoes.get_proposicao_por_nome( \
						normaliza(proposicao.sigla), proposicoes, \
						proposicoes_por_nome, regimes, regimes_por_nome, \
						apreciacoes, apreciacoes_por_nome, orgaos, \
						orgaos_por_id, deputados, deputados_por_nome, \
						deputados_antigos, deputados_antigos_por_nome, \
						partidos_por_sigla, outros_autores, \
						outros_autores_por_nome)
					reuniao_proposicoes.append(proposicoes_por_nome[normaliza( \
						proposicao.sigla)])
			
			orgao['reunioes'][id_reuniao] = { \
				'data_hora': formata_data(dados_reuniao.data + ' ' + \
					dados_reuniao.horario + ':00'), \
				'local': uniformiza(dados_reuniao.local), \
				'estado': uniformiza(dados_reuniao.estado), \
				'tipo': uniformiza(dados_reuniao.tipo), \
				'objeto': dados_reuniao.objeto.encode('utf-8'), \
				'proposicoes': set(reuniao_proposicoes)}

def _obter_andamento(dados):
	proposicao = dados[0]
	orgao_num = dados[1][proposicao['orgao_num']]['id']
	orgao_num = orgao_num if orgao_num != None and \
		proposicao['orgao_num'] != '' else ''
	
	try:
		return cliente_orgaos.service.ObterAndamento(proposicao['tipo'], \
			proposicao['numero'], proposicao['ano'], '', orgao_num)
	except suds.WebFault:
		return None

def obter_andamentos(andamentos, proposicoes_chaves, proposicoes, orgaos, \
	orgaos_por_id, aux_map=map):
	
	dados_andamentos = aux_map(_obter_andamento, \
		map(lambda i: [proposicoes[i], orgaos], proposicoes_chaves))
	
	for i in range(len(proposicoes_chaves)):
		id_proposicao = proposicoes_chaves[i]
		proposicao = proposicoes[id_proposicao]
		andamento = dados_andamentos[i]
		
		andamentos[id_proposicao] = {'ultima_acao': [], 'andamento': []}
		chave_acao = {'ultimaAcao': 'ultima_acao', 'andamento': 'andamento'}
		
		if andamento == None:
			continue
		
		for fonte_acao in ['ultimaAcao', 'andamento']:
			lista_andamentos = certifica_lista( \
				andamento.proposicao[fonte_acao], 'tramitacao')
		
			for dados_andamento in lista_andamentos:
				data_andamento = formata_data(dados_andamento.data)
				descr_andamento = dados_andamento.descricao.encode("utf-8")
			
				aux_orgao = dados_andamento.orgao.split(' - ')
				orgao_sigla = uniformiza(aux_orgao[0])
				orgao_nome = None if len(orgao_sigla) == 0 else \
					' - '.join(aux_orgao[1:])
			
				adiciona_orgao(orgaos, orgaos_por_id, orgao_sigla, \
					dados_andamento.codOrgao, orgao_nome)
			
				andamentos[id_proposicao][chave_acao[fonte_acao]].append({ \
					'data': data_andamento, \
					'orgao': orgao_sigla, \
					'descricao': descr_andamento})

def _obter_relatorio(proposicao):
	try:
		return cliente_orgaos.service.ObterIntegraComissoesRelator( \
			proposicao['tipo'], proposicao['numero'], proposicao['ano'])
	except suds.WebFault:
		return None

def obter_relatorios(relatorios, proposicoes_chaves, proposicoes, deputados, \
	deputados_por_nome, deputados_antigos, deputados_antigos_por_nome, \
	partidos_por_sigla, orgaos, orgaos_por_id, aux_map=map):
	
	relatorios_dados = aux_map(_obter_relatorio, map(lambda a: proposicoes[a], \
		proposicoes_chaves))
	
	for i in range(len(proposicoes_chaves)):
		id_proposicao = proposicoes_chaves[i]
		proposicao = proposicoes[id_proposicao]
		relatorio = relatorios_dados[i]
		
		if 'link_teor' not in proposicao.keys():
			proposicao['link_teor'] = relatorio.proposicao.integra. \
				_LinkArquivo.encode("utf-8")
	
		relatorios[id_proposicao] = {}
		
		if relatorio == None:
			continue
		
		lista_relatorios = certifica_lista(relatorio.proposicao.comissoes, \
			'comissao')
	
		for dados_relatorio in lista_relatorios:
			orgao_sigla = uniformiza(dados_relatorio._sigla)
		
			adiciona_orgao(orgaos, orgaos_por_id, orgao_sigla, None, \
				dados_relatorio._nome)
		
			id_relator = dados_deputados.obtem_deputado_por_nome( \
				uniformiza(dados_relatorio.relator), None, None, deputados, \
				deputados_por_nome, deputados_antigos, \
				deputados_antigos_por_nome, partidos_por_sigla)
			texto_parecer = dados_relatorio.parecer.encode("utf-8").strip()
		
			if id_relator == None and texto_parecer == '':
				continue
		
			relatorios[id_proposicao][orgao_sigla] = {
				'relator': id_relator, \
				'parecer': texto_parecer}

def _obter_proposicoes_referentes(proposicao):
	return cliente_orgaos.service.ObterEmendasSubstitutivoRedacaoFinal( \
		proposicao['tipo'], proposicao['numero'], proposicao['ano'])

def obter_proposicoes_referentes(proposicoes_verifica, proposicoes, \
	proposicoes_por_nome, regimes, regimes_por_nome, apreciacoes, \
	apreciacoes_por_nome, deputados,  deputados_por_nome, partidos_por_sigla, \
	blocos, blocos_por_sigla, orgaos, orgaos_por_id, outros_autores, \
	outros_autores_por_nome, deputados_antigos, deputados_antigos_por_nome, \
	aux_map=map):
	
	referentes_verifica = aux_map(_obter_proposicoes_referentes, \
		proposicoes_verifica)
	
	for i in range(len(proposicoes_verifica)):
		proposicao = proposicoes_verifica[i]
		referentes = referentes_verifica[i]
	
		nao_listadas = set([])
		set_proposicoes = set(proposicoes.keys())
	
		tipos = [{ \
			'chave1': 'Substitutivos', \
			'chave2': 'Substitutivo', \
			'campo': 'substitutivos'}, { \
			'chave1': 'RedacoesFinais', \
			'chave2': 'RedacaoFinal', \
			'campo': 'redacoes_finais'}, { \
			'chave1': 'Emendas', \
			'chave2': 'Emenda', \
			'campo': 'emendas'}]
	
		for tipo in tipos:
			lista_referentes = certifica_lista( \
				referentes.Proposicao[tipo['chave1']], tipo['chave2'])
			proposicao[tipo['campo']] = set(map(lambda a: \
				int(a._CodProposicao), lista_referentes))
		
			nao_listadas |= proposicao[tipo['campo']] - set_proposicoes
	
		for cod_proposicao in list(nao_listadas):
			dados_proposicoes.get_proposicao_por_id(cod_proposicao, \
				proposicoes, proposicoes_por_nome, regimes, regimes_por_nome, \
				apreciacoes, apreciacoes_por_nome, blocos, blocos_por_sigla, \
				orgaos, orgaos_por_id, deputados, deputados_por_nome, \
				deputados_antigos, deputados_antigos_por_nome, \
				partidos_por_sigla, outros_autores, outros_autores_por_nome)

def adiciona_a_orgao(membros, tipo, deputados_por_nome):
	try:
		if tipo != None:
			membro = membros[tipo]
		else:
			membro = membros
	except (AttributeError, TypeError):
		return None
	
	try:
		return {"id": deputados_por_nome[uniformiza(membro.nome)], \
			"situacao": membro.situacao[0].upper()}
	except KeyError:
		dados_deputados.deputado_nao_encontrado.append( \
			membro.nome.encode("utf-8"))
		return None

def adiciona_orgao(orgaos, orgaos_por_id, sigla, id_orgao=None, descricao=None):
	try:
		orgao_atual = orgaos[uniformiza(sigla)]
	except KeyError:
		orgaos[uniformiza(sigla)] = { \
			'id': None, \
			'descricao': None, \
			'membros': {'titular': [], 'suplente': []}}
		orgao_atual = orgaos[uniformiza(sigla)]
	
	if id_orgao != None:
		id_orgao = id_orgao.strip()
		
		if id_orgao == '':
			id_orgao = None
	
	if descricao != None:
		descricao = descricao.strip()
		
		if descricao == '':
			descricao = None
	
	if id_orgao != None:
		id_orgao = int(id_orgao)
	
	orgao_atual['id'] = id_orgao if orgao_atual['id'] == None else \
		orgao_atual['id']
	orgao_atual['descricao'] = descricao if orgao_atual['descricao'] == None \
		else orgao_atual['descricao']
	
	if id_orgao != None:
		orgaos_por_id[id_orgao] = uniformiza(sigla)

def get_orgaos_membros(orgaos, deputados, deputados_por_nome):
	nao_coincide_membros = {}
	
	for sigla in orgaos.keys():
		id_orgao = orgaos[sigla]['id']
		
		if id_orgao == None:
			continue
		
		orgao = cliente_orgaos.service.ObterMembrosOrgao(id_orgao).orgao
		
		a = set(orgaos[sigla]["membros"]["titular"] + \
			orgaos[sigla]["membros"]["suplente"])
		
		orgaos[sigla]["membros"]["presidente"] = \
			adiciona_a_orgao(orgao.membros, "Presidente", deputados_por_nome)
		orgaos[sigla]["membros"]["primeiro-vice-presidente"] = \
			adiciona_a_orgao(orgao.membros, "PrimeiroVice-Presidente", \
			deputados_por_nome)
		orgaos[sigla]["membros"]["segundo-vice-presidente"] = \
			adiciona_a_orgao(orgao.membros, "SegundoVice-Presidente", \
			deputados_por_nome)
		orgaos[sigla]["membros"]["terceiro-vice-presidente"] = \
			adiciona_a_orgao(orgao.membros, "TerceiroVice-Presidente", \
			deputados_por_nome)
		orgaos[sigla]["membros"]["relator"] = adiciona_a_orgao(orgao.membros, \
			"Relator", deputados_por_nome)
		
		membros = certifica_lista(orgao.membros, "membro")
		orgaos[sigla]["membros"]["outros"] = []
		
		for membro in membros:
			membro_aux = adiciona_a_orgao(membro, None, deputados_por_nome)
			
			if membro_aux != None:
				orgaos[sigla]["membros"]["outros"].append(membro_aux)
		
		# TODO Desnecessario conferir!
		
		teste = []
		
		for k in orgaos[sigla]["membros"].keys():
			if k == "titular" or k == "suplente":
				continue
			
			membro = orgaos[sigla]["membros"][k]
			
			if isinstance(membro, list):
				teste += map(lambda a: a["id"], membro)
				continue
			# TODO Colocar essa informação de comissão nos membros!
			try:
				teste.append(membro["id"])
			except TypeError:
				pass
		
		b = set(teste)
		
		if len(a ^ b) > 0:
			nao_coincide_membros[sigla] = [list(a - b), list(b - a)]
	
	return nao_coincide_membros

