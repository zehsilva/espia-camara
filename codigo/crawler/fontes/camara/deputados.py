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
import orgaos as dados_orgaos
from fontes.geral import *

deputado_nao_encontrado = []

deputados_muda_uf = {uniformiza('Roberto Freire'): ['SP', 'PE']}

wsdl_deputado_file = "http://www.camara.gov.br/SitCamaraWS/Deputados.asmx?wsdl"
cliente_deputado = soap.Client(wsdl_deputado_file)

def obtem_detalhes_deputados(deputados, orgaos, orgaos_por_id):
	profissoes_por_nome = {}
	profissoes = {}
	max_profissao = 1
	
	for id_deputado in deputados.keys():
		deputado = deputados[id_deputado]
		
		try:
			dados_legislaturas = cliente_deputado.service.ObterDetalhesDeputado( \
				id_deputado, 54)
		except suds.WebFault:
			try:
				dados_legislaturas = cliente_deputado.service.ObterDetalhesDeputado( \
					id_deputado, 53)
			except suds.WebFault:
				continue
		
		dado_legislatura = dados_legislaturas.Deputados.Deputado
		
		deputado['legislaturas'].add(int(dado_legislatura.numLegislatura))
		deputado['email'] = dado_legislatura.email.encode("utf-8").strip()
		
		try:
			id_profissao = profissoes_por_nome[normaliza( \
				dado_legislatura.nomeProfissao)]
		except KeyError:
			id_profissao = max_profissao
			profissoes_por_nome[normaliza(dado_legislatura.nomeProfissao)] \
				= id_profissao
			profissoes[id_profissao] = dado_legislatura.nomeProfissao. \
				encode("utf-8")
			max_profissao += 1
		
		deputado['profissao'] = id_profissao
		deputado['data_nascimento'] = formata_data(dado_legislatura. \
			dataNascimento)
		
		try:
			deputado['data_falecimento'] = formata_data(dado_legislatura. \
				dataFalecimento)
		except ValueError:
			pass
		
		deputado['uf'] = dado_legislatura.ufRepresentacaoAtual.upper(). \
			strip()
		deputado['situacao'] = dado_legislatura.situacaoNaLegislaturaAtual
		deputado['nome_parlamentar'] = dado_legislatura. \
			nomeParlamentarAtual.encode("utf-8").title().strip()
		deputado['nome'] = dado_legislatura.nomeCivil.encode("utf-8"). \
			title().strip()
		deputado['sexo'] = dado_legislatura.sexo.upper().strip()
		deputado['partido'] = normaliza(dado_legislatura.partidoAtual. \
			idPartido)
		deputado['id_parlamentar'] = int(dado_legislatura. \
			idParlamentarDeprecated)
		deputado['gabinete'] = dado_legislatura.gabinete.numero. \
			encode("utf-8").strip()
		deputado['anexo'] = dado_legislatura.gabinete.anexo. \
			encode("utf-8").strip()
		deputado['fone'] = dado_legislatura.gabinete.telefone. \
			encode("utf-8").strip()
		
		dados_comissoes = {}
		deputado['comissoes'] = dados_comissoes
		lista_comissoes = certifica_lista(dado_legislatura.comissoes, \
			'comissao')
		
		for comissao in lista_comissoes:
			sigla = normaliza(comissao.siglaComissao)
			
			if sigla not in orgaos.keys():
				dados_orgaos.adiciona_orgao(orgaos, orgaos_por_id, sigla, \
					comissao.idOrgaoLegislativoCD, \
					comissao.nomeComissao.encode("utf-8").strip())
			
			info_comissao = { \
				'condicao': comissao.condicaoMembro[0].upper(), \
				'data_entrada': formata_data(comissao.dataEntrada), \
				'data_saida': formata_data(comissao.dataSaida), \
				'cargos': []}
			
			try:
				dados_comissoes[sigla].append(info_comissao)
			except KeyError:
				dados_comissoes[sigla] = [info_comissao]
		
		lista_cargos_comissoes = certifica_lista( \
			dado_legislatura.cargosComissoes, 'cargoComissoes')
		
		for cargo_comissao in lista_cargos_comissoes:
			sigla = normaliza(cargo_comissao.siglaComissao)
			
			data_entrada = formata_data(cargo_comissao.dataEntrada)
			data_saida = formata_data(cargo_comissao.dataSaida)
			
			try:
				dados_comissao_sigla = dados_comissoes[sigla]
			except KeyError:
				if sigla not in orgaos.keys():
					dados_orgaos.adiciona_orgao(orgaos, orgaos_por_id, sigla, \
						cargo_comissao.idOrgaoLegislativoCD, \
						cargo_comissao.nomeComissao.encode("utf-8").strip())
				
				dados_comissoes[sigla] = [{ \
					'data_entrada': data_entrada, \
					'data_saida': data_saida, \
					'cargos': []}]
				dados_comissao_sigla = dados_comissoes[sigla]
			
			ok = False
			
			for comissao in dados_comissao_sigla:
				if comissao['data_entrada'] <= data_entrada and \
					(comissao['data_saida'] == None or (data_saida != None and \
					comissao['data_saida'] >= data_saida)):
					
					comissao['cargos'].append({ \
						'cargo': int(cargo_comissao.idCargo), \
						'data_entrada': data_entrada, \
						'data_saida': data_saida})
					ok = True
					break
			
			if not ok:
				dados_comissoes[sigla].append({ \
					'data_entrada': data_entrada, \
					'data_saida': data_saida, \
					'cargos': [{ \
						'cargo': int(cargo_comissao.idCargo), \
						'data_entrada': data_entrada, \
						'data_saida': data_saida}]})
		
		dados_exercicios = []
		deputado['exercicios'] = dados_exercicios
		lista_exercicios = certifica_lista(dado_legislatura. \
			periodosExercicio, 'periodoExercicio')
		
		for exercicio in lista_exercicios:
			try:
				causa_fim = int(exercicio.idCausaFimExercicio)
			except ValueError:
				causa_fim = None
			
			dados_exercicios.append({ \
				'uf': exercicio.siglaUFRepresentacao.upper(), \
				'situacao': exercicio.situacaoExercicio[0].upper(), \
				'data_inicio': formata_data(exercicio.dataInicio), \
				'data_fim': formata_data(exercicio.dataFim), \
				'causa_fim': causa_fim, \
				'causa_fim_descr': exercicio.descricaoCausaFimExercicio. \
					encode("utf-8").strip()})
		
		dados_partidos = []
		deputado['partidos_anteriores'] = dados_partidos
		lista_filiacoes = certifica_lista(dado_legislatura. \
			filiacoesPartidarias, 'filiacaoPartidaria')
		
		for filiacao in lista_filiacoes:
			dados_partidos.append({ \
				'partido': normaliza(filiacao.idPartidoAnterior), \
				'data_saida': formata_data(filiacao. \
					dataFiliacaoPartidoPosterior)})
		
		dados_nomes = []
		deputado['nomes_parlamentares_anteriores'] = dados_nomes
		lista_nomes = certifica_lista( \
			dado_legislatura.historicoNomeParlamentar, \
			'itemHistoricoNomeParlamentar')
		
		for nome in lista_nomes:
			dados_nomes.append({ \
				'nome_parlamentar': nome.nomeParlamentarAnterior. \
					encode("utf-8").title().strip(), \
				'fim_uso': formata_data(nome.dataInicioVigenciaNomePosterior)})
		
		dados_lideranca = []
		deputado['lideranca'] = dados_lideranca
		lista_liderancas = certifica_lista(dado_legislatura.historicoLider, \
			'itemHistoricoLider')
		
		for lideranca in lista_liderancas:
			dados_lideranca.append({ \
				'cargo': lideranca.idCargoLideranca, \
				'num_ordem': int(lideranca.numOrdemCargo), \
				'data_inicio': formata_data(lideranca.dataDesignacao), \
				'data_fim': formata_data(lideranca.dataTermino), \
				'tipo': lideranca.codigoUnidadeLideranca.upper(), \
				'bancada': normaliza(lideranca.idBlocoPartido)})

def get_lideres(deputados, deputados_por_nome, partidos, partidos_por_sigla, \
	blocos, blocos_por_sigla):
	
	lista_bancadas = cliente_deputado.service.ObterLideresBancadas()
	
	for bancada_info in lista_bancadas.bancadas.bancada:
		bloco = (bancada_info._sigla[:6] == "Bloco ")
		bloco = bloco or (bancada_info._sigla == "Governo" or \
			bancada_info._sigla == "Minoria")
		
		if bloco:
			if bancada_info._sigla == "Governo" or \
				bancada_info._sigla == "Minoria":
				
				bancada_id = blocos_por_sigla[uniformiza(bancada_info._sigla)]
			else:
				bancada_id = blocos_por_sigla[ \
					uniformiza(bancada_info._sigla[6:])]
			
			bancada = blocos[bancada_id]
		else:
			bancada_id = partidos_por_sigla[uniformiza(bancada_info._sigla)]
			bancada = partidos[bancada_id]
		
		try:
			id_lider = deputados_por_nome[uniformiza(bancada_info.lider.nome)]
		except AttributeError:
			id_representante = deputados_por_nome[ \
				uniformiza(bancada_info.representante.nome)]
			representante = deputados[id_representante]
		
			lider["representacao"].append({ \
				"bloco": "B" if bloco else "P", \
				"bancada": bancada_id})
		
			bancada["representante"] = id_representante
			
			continue
		
		lider = deputados[id_lider]
		
		lider["lideranca"].append({ \
			"bloco": "B" if bloco else "P", \
			"bancada": bancada_id})
		
		bancada["representante"] = {"lider": id_lider, "vice_lideres": []}
		
		vice_lideres = certifica_lista(bancada_info, "vice_lider")
		
		for vice_lider in vice_lideres:
			try:
				id_deputado = deputados_por_nome[uniformiza(vice_lider.nome)]
			except KeyError:
				continue
			
			deputado = deputados[id_deputado]
			
			deputado["vice_lideranca"].append({ \
				"bloco": "B" if bloco else "P", \
				"bancada": bancada_id})
			
			bancada["representante"]["vice_lideres"].append(id_deputado)

def deputado_antigo(nome_parlamentar, partido, uf, deputados_antigos, \
	deputados_antigos_por_nome, partidos_por_sigla, deputado_id=None):
	
	if nome_parlamentar.strip() == '':
		return None
	
	partes = nome_parlamentar.split('-')
	
	if len(partes) > 1 and partes[-1][:8] == 'S.Part./':
		nome_parlamentar = '-'.join(partes[:-1])
	
	nome_parlamentar = nome_parlamentar.split(',')[0]
	nome_parlamentar_aux = nome_parlamentar
	tentativa = 1
	
	while True:
		try:
			id_deputado = deputados_antigos_por_nome[nome_parlamentar_aux]
			deputado = deputados_antigos[id_deputado]
		
			if deputado['uf'] == None or deputado['uf'] == uf or \
				deputado['uf'] == '':
				
				deputado['uf'] = uf
			
				if deputado['partido'] == None and partido != None:
					deputado['partido'] = partidos_por_sigla[partido]
				
				return id_deputado
		except KeyError:
			pass
		
		if not nome_parlamentar_aux in deputados_antigos_por_nome.keys():
			id_deputado = - (len(deputados_antigos) + 1)
			deputados_antigos[id_deputado] = { \
				'id': deputado_id, \
				'nome_deputado': nome_parlamentar.title(), \
				'partido': partidos_por_sigla[partido] if partido != None and \
					partido != '' else None, \
				'uf': uf, \
				'legislaturas': set([])}
			deputados_antigos_por_nome[nome_parlamentar] = id_deputado
			
			return id_deputado
		
		nome_parlamentar_aux = nome_parlamentar + str(tentativa)
		tentativa += 1

def obtem_deputado_por_id(id_deputado, nome_parlamentar, partido, uf, \
	deputados, deputados_por_nome, deputados_antigos, \
	deputados_antigos_por_nome, partidos_por_sigla):
	
	if id_deputado in deputados.keys():
		return id_deputado
	
	return deputado_antigo(nome_parlamentar, partido, uf, deputados_antigos, \
		deputados_antigos_por_nome, partidos_por_sigla, id_deputado)

def obtem_deputado_por_nome(nome_parlamentar, partido, uf, deputados, \
	deputados_por_nome, deputados_antigos, deputados_antigos_por_nome, \
	partidos_por_sigla):
	
	try:
		id_deputado = deputados_por_nome[nome_parlamentar]
		deputado = deputados[id_deputado]
		
		if uf != None and deputado['uf'] != uf:
			nome_aux = uniformiza(deputado['nome_parlamentar'])
			
			if nome_aux not in deputados_muda_uf.keys() or not uf in \
				deputados_muda_uf[nome_aux]:
				
				id_deputado = deputado_antigo(nome_parlamentar, partido, uf, \
					deputados_antigos, deputados_antigos_por_nome, \
					partidos_por_sigla)
#					raise Exception('Diferencas nos dados do deputado por ' \
#						'nome (dados: %s, %s, %s)' % \
#						(deputado['nome_parlamentar'], deputado['uf'], uf))
	except KeyError:
		id_deputado = deputado_antigo(nome_parlamentar, partido, uf, \
			deputados_antigos, deputados_antigos_por_nome, partidos_por_sigla)
	
	return id_deputado

def get_deputados(partidos_por_sigla, orgaos, orgaos_por_id):
	lista_deputados = cliente_deputado.service.ObterDeputados()
	dict_deputados = {}
	dict_deputados_por_nome = {}

	for deputado in lista_deputados.deputados.deputado:
		id_deputado = int(deputado.ideCadastro)
		
		dict_deputados[id_deputado] = { \
			"condicao": deputado.condicao[0].upper(), \
			"matricula": int(deputado.matricula), \
			"id_parlamentar": int(deputado.idParlamentar), \
			"nome": uniformiza(deputado.nome).title(), \
			"nome_parlamentar": uniformiza(deputado.nomeParlamentar).title(), \
			"sexo": deputado.sexo[0].upper(), \
			"uf": deputado.uf, \
			"url_foto": deputado.urlFoto, \
			"legislaturas": set([]), \
			"partido": partidos_por_sigla[uniformiza(deputado.partido)], \
			"gabinete": deputado.gabinete, \
			"anexo": deputado.anexo, \
			"fone": deputado.fone, \
			"email": deputado.email.encode("utf-8"), \
			"lideranca": [], \
			"vice_lideranca": [], \
			"representacao": [], \
			"comissoes": []}
			
		dict_deputados[id_deputado]["comissoes"] = \
			{"titular": [], "suplente": []}
		
		comissoes_titular = certifica_lista(deputado.comissoes.titular, \
			"comissao")
		
		for comissao in comissoes_titular:
			orgao_sigla = uniformiza(comissao._sigla)
			dict_deputados[id_deputado]["comissoes"]["titular"]. \
				append(orgao_sigla)
			
			try:
				orgaos[orgao_sigla]["membros"]['titular'].append(id_deputado)
			except KeyError:
				# Registra órgãos que não estão no sistema
				dados_orgaos.adiciona_orgao(orgaos, orgaos_por_id, orgao_sigla)
				orgaos[orgao_sigla]["membros"]['titular'].append(id_deputado)
		
		comissoes_suplente = certifica_lista(deputado.comissoes.suplente, \
			"comissao")
		
		for comissao in comissoes_suplente:
			orgao_sigla = uniformiza(comissao._sigla)
			dict_deputados[id_deputado]["comissoes"]["suplente"]. \
				append(orgao_sigla)
			
			try:
				orgaos[orgao_sigla]["membros"]['suplente'].append(id_deputado)
			except KeyError:
				# Registra órgãos que não estão no sistema
				dados_orgaos.adiciona_orgao(orgaos, orgaos_por_id, orgao_sigla)
				orgaos[orgao_sigla]["membros"]['suplente'].append(id_deputado)
		
		dict_deputados_por_nome[uniformiza(deputado.nomeParlamentar)] = \
			id_deputado
	
	return dict_deputados, dict_deputados_por_nome

def get_blocos(partidos_por_sigla):
	dict_blocos = {}
	dict_blocos_por_sigla = {}

	for legislatura in [53, 54]:
		lista_blocos = cliente_deputado.service.ObterPartidosBlocoCD('', \
			legislatura)

		for bloco in lista_blocos.blocos.bloco:
			data_criacao = formata_data(bloco.dataCriacaoBloco)
			data_extincao = formata_data(bloco.dataExtincaoBloco)
		
			dict_blocos[bloco.idBloco] = { \
				"sigla_bloco": bloco.siglaBloco, \
				"nome_bloco": bloco.nomeBloco.encode("utf-8"), \
				"representante": None, \
				"data_criacao": data_criacao, \
				"data_extincao": data_extincao, \
				"partidos": []}
		
			for partido in bloco.Partidos.partido:
				data_adesao = formata_data(partido.dataAdesaoPartido)
				data_desligamento = \
					formata_data(partido.dataDesligamentoPartido)
			
				dict_blocos[bloco.idBloco]["partidos"].append({ \
					"partido": partidos_por_sigla[ \
						uniformiza(partido.siglaPartido)], \
					"data_adesao": data_adesao, \
					"data_desligamento": data_desligamento})
		
			dict_blocos_por_sigla[uniformiza(bloco.siglaBloco)] = bloco.idBloco
	
	# Blocos permanentes
	
	dict_blocos["Governo"] = { \
		"sigla_bloco": "Gov.", \
		"nome_bloco": "Liderança do Governo", \
		"representante": None, \
		"data_criacao": None, \
		"data_extincao": None, \
		"partidos": None}
	
	dict_blocos_por_sigla[uniformiza(dict_blocos["Governo"]['sigla_bloco'])] = \
		"Governo"
	dict_blocos_por_sigla[uniformiza("Governo")] = "Governo"
	dict_blocos_por_sigla[uniformiza("Apoio ao Governo")] = "Governo"
	
	dict_blocos["Minoria"] = { \
		"sigla_bloco": "Minoria", \
		"nome_bloco": "Liderança da Minoria", \
		"representante": None, \
		"data_criacao": None, \
		"data_extincao": None, \
		"partidos": None}
	
	dict_blocos_por_sigla[uniformiza(dict_blocos["Minoria"]['sigla_bloco'])] = \
		"Minoria"
	
	dict_blocos["Maioria"] = { \
		"sigla_bloco": uniformiza("Maioria"), \
		"nome_bloco": "Liderança da Maioria", \
		"representante": None, \
		"data_criacao": None, \
		"data_extincao": None, \
		"partidos": None}
	
	dict_blocos_por_sigla[uniformiza(dict_blocos["Maioria"]['sigla_bloco'])] = \
		"Maioria"
	
	return dict_blocos, dict_blocos_por_sigla

def get_partidos():
	lista_partidos = cliente_deputado.service.ObterPartidosCD()
	dict_partidos = {}
	dict_partidos_por_sigla = {}

	for partido in lista_partidos.partidos.partido:
		data_criacao = formata_data(partido.dataCriacao)
		data_extincao = formata_data(partido.dataExtincao)
		
		dict_partidos[partido.idPartido] = { \
			"sigla_partido": partido.siglaPartido, \
			"nome_partido": partido.nomePartido.encode("utf-8"), \
			"representante": None, \
			"data_criacao": data_criacao, \
			"data_extincao": data_extincao}
		
		try:
			if data_extincao < dict_partidos[dict_partidos_por_sigla[ \
				uniformiza(partido.siglaPartido)]]['data_extincao']:
				
				continue
		except (TypeError, KeyError):
			pass
		
		dict_partidos_por_sigla[uniformiza(partido.siglaPartido)] = \
			partido.idPartido
	
	dict_partidos_por_sigla['SEM PARTIDO'] = dict_partidos_por_sigla['S.PART.']
	
	return dict_partidos, dict_partidos_por_sigla

