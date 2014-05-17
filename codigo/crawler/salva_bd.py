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

import MySQLdb
import _mysql_exceptions
import cPickle as pickle
import datetime
import re
import itertools
import math
from fontes.geral import *

usuario = 'root'
senha = 'There15NoFreeLunch'
banco = 'dadosabertos'

pasta = '../v9/dados_deputados/'

def salva_dados(dados, nome_arquivo):
	with open(nome_arquivo, 'wb') as arquivo_dados:
		pickle.dump(dados, arquivo_dados)

def carrega_dados(nome_arquivo):
	with open(nome_arquivo, 'rb') as arquivo_dados:
		return pickle.load(arquivo_dados)

latin1=False

def decode(texto):
	global latin1
	
	for encoding in ['utf8', 'iso-8859-1']:
		try:
			texto = texto.decode(encoding)
			break
		except UnicodeEncodeError:
			pass
	
	texto = texto.replace(u'‘', '\'').replace(u'’', '\'').replace(u'“', '"'). \
		replace(u'”', '"').replace(u'–', '-').replace(u'—', '-'). \
		replace(u'…', '...')
	
	if latin1:
		return texto.encode('latin1', 'ignore')
	
	return texto

def arruma_campo(dicionario, chave=None):
	if chave == None:
		campo = dicionario
	else:
		try:
			campo = dicionario[chave]
		except KeyError:
			return None
	
	if campo == None:
		return None

	if isinstance(campo, str) or isinstance(campo, unicode):
		return decode(campo)
	
	if isinstance(campo, list):
		return ', '.join([decode(a) for a in campo])

	if isinstance(campo, datetime.datetime) or isinstance(campo, datetime.date):
		if campo.year < 100:
			return campo.replace(year=campo.year+2000)
	
	return campo

def executa_query(query, dados, conexao=None, debug=True):
	if conexao == None:
		conexao = dados
		cursor = conexao.cursor()
		
		try:
			cursor.execute(query)
		except:
			if debug:
				print query
			
			raise
		return
	
	cursor = conexao.cursor()
	
	try:
		cursor.execute(query, dados)
	except:
		if debug:
			print query % dados
		
		raise

def salva_apreciacoes(conexao):
	apreciacoes_proposicoes = carrega_dados(pasta + \
		'apreciacoes_proposicoes.pkl')

	for i in apreciacoes_proposicoes.keys():
		executa_query('INSERT INTO apreciacoes (id_apreciacao, descricao) ' \
			'VALUES (%s, %s)', (arruma_campo(i), arruma_campo( \
			apreciacoes_proposicoes[i], 'nome')), conexao)

def salva_partidos(conexao):
	id_bancada = 0
	
	partidos = carrega_dados(pasta + 'partidos.pkl')
	bancada_partido = {}
	
	for i in partidos.keys():
		executa_query('INSERT INTO partidos (id_partido, sigla_partido, ' \
			'nome_partido, data_criacao, data_extincao) VALUES (%s, %s, %s, ' \
			'%s, %s)', (i.upper(), arruma_campo(partidos[i], 'sigla_partido'), \
			arruma_campo(partidos[i], 'nome_partido'), arruma_campo( \
			partidos[i], 'data_criacao'), arruma_campo(partidos[i], \
			'data_extincao')), conexao)

		executa_query('INSERT INTO bancadas (id_bancada, id_partido) VALUES ' \
			'(%s, %s)', (arruma_campo(id_bancada), arruma_campo(i)), conexao)
		bancada_partido[i.upper()] = id_bancada
		id_bancada += 1	

	blocos = carrega_dados(pasta + 'blocos.pkl')
	bancada_bloco = {}
	
	for id_bloco in blocos.keys():
		bloco = blocos[id_bloco]
		
		executa_query('INSERT INTO blocos (id_bloco, nome, data_criacao, ' \
			'data_extincao) VALUES (%s, %s, %s, %s)', (arruma_campo( \
			id_bloco), arruma_campo(bloco, 'sigla_bloco'), arruma_campo(bloco, \
			'data_criacao'), arruma_campo(bloco, 'sigla_bloco')), conexao)
		
		executa_query('INSERT INTO bancadas (id_bancada, id_bloco) VALUES ' \
			'(%s, %s)', (arruma_campo(id_bancada), arruma_campo(id_bloco)), \
			conexao)
		bancada_bloco[id_bloco] = id_bancada
		id_bancada += 1	
		
		if bloco['partidos'] == None:
			continue
		
		for partido in bloco['partidos']:
			executa_query('INSERT INTO partidos_blocos (id_bloco, id_partido,' \
				' data_adesao, data_desligamento) VALUES (%s, %s, %s, %s)', \
				(arruma_campo(id_bloco), arruma_campo(partido, 'partido'), \
				arruma_campo(partido, 'data_adesao'), arruma_campo(partido, \
				'data_desligamento')), conexao)
	
	return bancada_partido, bancada_bloco

def salva_deputados(conexao):
	deputados = carrega_dados(pasta + 'deputados.pkl')
	deputados_antigos = carrega_dados(pasta + 'deputados_antigos.pkl')
	
	graus = set([(d['eleicao']['grau_instrucao_codigo'], decode(d['eleicao'] \
		['grau_instrucao_descr']).capitalize()) for d in deputados.values() if \
		'eleicao' in d.keys() and d['eleicao'] != {}])
	
	for grau in graus:
		executa_query('INSERT INTO graus_instrucao (id_grau, descricao) ' \
			'VALUES (%s, %s)', (grau[0], grau[1]), conexao)

	profissoes_tse = set([(d['eleicao']['ocupacao_codigo'], decode( \
		d['eleicao']['ocupacao_descr']).capitalize()) for d in \
		deputados.values() if 'eleicao' in d.keys() and d['eleicao'] != {}])
	profissoes_cd = carrega_dados(pasta + 'profissoes.pkl')
	profissoes_cd = set([(p, decode(profissoes_cd[p]).capitalize()) \
		for p in profissoes_cd.keys()])
	profissoes_nomes = list(set(zip(*profissoes_tse)[1]) | \
		set(zip(*profissoes_cd)[1]))
	
	profissao_tse_por_cod = {}
	
	for p in profissoes_tse:
		profissao_tse_por_cod[p[0]] = profissoes_nomes.index(p[1])
	
	profissao_cd_por_cod = {}
	
	for p in profissoes_cd:
		profissao_cd_por_cod[p[0]] = profissoes_nomes.index(p[1])
	
	for i in range(len(profissoes_nomes)):
		executa_query('INSERT INTO profissoes (id_profissao, nome_profissao) ' \
			'VALUES (%s, %s)', (arruma_campo(i), \
			arruma_campo(profissoes_nomes[i])), conexao)
	
	for id_deputado in deputados.keys():
		deputado = deputados[id_deputado]
		
		if 'eleicao' in deputado.keys() and deputado['eleicao'] != {}:
			seq_candidato = deputado["eleicao"]["seq_candidato"]
			ocupacao = profissao_tse_por_cod[deputado["eleicao"] \
				["ocupacao_codigo"]]
			grau_instrucao = deputado["eleicao"]["grau_instrucao_codigo"]
			eleicao_partido = deputado["eleicao"]["partido_eleito"].upper(). \
				replace(' ', '')
		else:
			seq_candidato = ocupacao = grau_instrucao = eleicao_partido = None
		
		nome = arruma_campo(deputado, 'nome')
		nome = nome.title() if nome != None else nome
		
		nome_parlamentar = arruma_campo(deputado, 'nome_parlamentar')
		nome_parlamentar = nome_parlamentar.title() if nome_parlamentar != \
			None else nome_parlamentar
		
		telefone = arruma_campo(deputado, 'fone')
		telefone = '(61) ' + telefone if telefone != None else telefone
		
		partido = arruma_campo(deputado, 'partido')
		partido = partido.upper() if partido != None else partido
		
		eleicao_partido = arruma_campo(eleicao_partido)
		eleicao_partido = eleicao_partido.upper() if eleicao_partido != None \
			else eleicao_partido
		
		executa_query('INSERT INTO deputados (id_deputado, matricula, ' \
			'id_parlamentar, cpf, titulo_eleitoral, nome_completo, ' \
			'nome_parlamentar, uf, partido_atual, situacao, gabinete, anexo, ' \
			'telefone, email, profissao, data_nascimento, data_falecimento, ' \
			'sexo, url_foto, eleicao_seq_candidato, eleicao_ocupacao, ' \
			'eleicao_grau_instrucao, eleicao_partido) VALUES (%s, %s, %s, %s,' \
			' %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,' \
			' %s, %s, %s)', (id_deputado, arruma_campo(deputado, \
			'matricula'), arruma_campo(deputado, 'id_parlamentar'), \
			arruma_campo(deputado, 'cpf'), arruma_campo(deputado, \
			'titulo_eleitoral'), nome, nome_parlamentar, arruma_campo( \
			deputado, 'uf'), partido, arruma_campo(deputado, 'situacao'), \
			arruma_campo(deputado, 'gabinete'), arruma_campo(deputado, \
			'anexo'), telefone, arruma_campo(deputado, 'email'), arruma_campo( \
			profissao_cd_por_cod[deputado['profissao']]) if 'profissao' in \
			deputado.keys() else None, arruma_campo(deputado, \
			'data_nascimento'), arruma_campo(deputado, 'data_falecimento'), \
			arruma_campo(deputado, 'sexo'), arruma_campo(deputado, \
			'url_foto'), arruma_campo(seq_candidato), arruma_campo(ocupacao), \
			arruma_campo(grau_instrucao), eleicao_partido), conexao)
	
	for id_deputado in deputados_antigos.keys():
		deputado = deputados_antigos[id_deputado]

		nome_parlamentar = arruma_campo(deputado, 'nome_deputado')
		nome_parlamentar = nome_parlamentar.title() if nome_parlamentar != \
			None else nome_parlamentar
		
		executa_query('INSERT INTO deputados (id_deputado, nome_parlamentar, ' \
			'uf, partido_atual) VALUES (%s, %s, %s, %s)', (id_deputado, \
			nome_parlamentar, arruma_campo(deputado, 'uf'), arruma_campo( \
			deputado, 'partido')), conexao)

def salva_autores_proposicoes(conexao):
	tipos_autores_proposicoes = carrega_dados(pasta + \
		'tipos_autores_proposicoes.pkl')
	
	for t in tipos_autores_proposicoes.keys():
		executa_query('INSERT INTO autores_tipos (tipo_autor, descricao) ' \
			'VALUES (%s, %s)', (arruma_campo(t), arruma_campo( \
			tipos_autores_proposicoes[t], 'descricao')), conexao)
	
	outros_autores_proposicoes = carrega_dados(pasta + \
		'outros_autores_proposicoes.pkl')
	deputados = carrega_dados(pasta + 'deputados.pkl')
	deputados_antigos = carrega_dados(pasta + 'deputados_antigos.pkl')
	
	for i in outros_autores_proposicoes.keys():
		executa_query('INSERT INTO autores_proposicoes (id_autor, nome) ' \
			'VALUES (%s, %s)', (arruma_campo(i - 100000), arruma_campo( \
			outros_autores_proposicoes[i], 'nome').title()), conexao)
	
	for i in deputados.keys():
		executa_query('INSERT INTO autores_proposicoes (id_autor, ' \
			'id_deputado, tipo) VALUES (%s, %s, %s)', (arruma_campo(i), \
			arruma_campo(i), arruma_campo('TipoParlamentar_10000')), conexao)
	
	for i in deputados_antigos.keys():
		executa_query('INSERT INTO autores_proposicoes (id_autor, ' \
			'id_deputado, tipo) VALUES (%s, %s, %s)', (arruma_campo(i), \
			arruma_campo(i), arruma_campo('TipoParlamentar_10000')), conexao)

def salva_orgaos(conexao):
	orgaos = carrega_dados(pasta + 'orgaos.pkl')
	
	for o in orgaos.keys():
		orgao = orgaos[o]
		
		executa_query('INSERT INTO orgaos (id_orgao, sigla, descricao) VALUES' \
			' (%s, %s, %s)', (arruma_campo(orgao, 'id'), arruma_campo(o), \
			arruma_campo(orgao, 'descricao')), conexao)

def salva_proposicoes(conexao):
	tipos_proposicoes = carrega_dados(pasta + 'tipos_proposicoes.pkl')
	
	for t in tipos_proposicoes.keys():
		tipo = tipos_proposicoes[t]
		executa_query('INSERT INTO proposicoes_tipos (tipo, descricao, ativa,' \
			' genero) VALUES (%s, %s, %s, %s)', (arruma_campo(t), \
			arruma_campo(tipo, 'descricao'), arruma_campo(tipo, 'ativa'), \
			arruma_campo(tipo, 'genero')), conexao)
	
	regimes_proposicoes = carrega_dados(pasta + 'regimes_proposicoes.pkl')
	
	for r in regimes_proposicoes.keys():
		regime = regimes_proposicoes[r]
		executa_query('INSERT INTO regimes (id_regime, descricao) VALUES (%s,' \
			' %s)', (arruma_campo(r), arruma_campo(regime, 'nome')), conexao)
	
	tipos_situacoes_proposicoes = carrega_dados(pasta + \
		'tipos_situacoes_proposicoes.pkl')
	
	for s in tipos_situacoes_proposicoes.keys():
		situacao = tipos_situacoes_proposicoes[s]
		executa_query('INSERT INTO situacoes (id_situacao, descricao, ativa) ' \
			'VALUES (%s, %s, %s)', (arruma_campo(s), arruma_campo(situacao, \
			'descricao'), arruma_campo(situacao, 'ativa')), conexao)
	
	proposicoes = carrega_dados(pasta + 'proposicoes.pkl')
	indices_inteiros_teores_aux = carrega_dados(pasta + \
		'indices_inteiros_teores.pkl')
	indices_inteiros_teores = {}
	
	for arquivo in indices_inteiros_teores_aux.keys():
		for chave in indices_inteiros_teores_aux[arquivo]:
			indices_inteiros_teores[chave] = arquivo
	
	chaves_arquivos = {}
	
	for p in proposicoes.keys():
		proposicao = proposicoes[p]
		
		try:
			arquivo_proposicao = indices_inteiros_teores[p]
		
			if arquivo_proposicao not in chaves_arquivos.keys():
				chaves_arquivos[arquivo_proposicao] = carrega_dados(pasta + \
					arquivo_proposicao)
			
			inteiro_teor = chaves_arquivos[arquivo_proposicao][p]
		except KeyError:
			inteiro_teor = None
		
		if proposicao['autor1_deputado']:
			id_autor = proposicao['autor1']
		else:
			id_autor = proposicao['autor1'] - 100000
		
		if 'despacho' in proposicao.keys():
			despacho_data = arruma_campo(proposicao['despacho'], 'data')
			despacho_texto = arruma_campo(proposicao['despacho'], 'texto')
		else:
			despacho_data = despacho_texto = None
		
		if inteiro_teor == None:
			link_conteudo = formato_teor = inteiro_texto = None
		else:
			link_conteudo = arruma_campo(inteiro_teor, 'link')
			formato_teor = arruma_campo(inteiro_teor, 'tipo_origem')
			
			if formato_teor == 'msword':
				inteiro_texto = arruma_campo(re.sub( \
					r'picscalex[0-9a-f]+\n[0-9]+\n', '', inteiro_teor['texto']))
			else:
				inteiro_texto = arruma_campo(inteiro_teor, 'texto')
			
			if inteiro_texto != None:
				inteiro_texto = inteiro_texto.encode('latin-1', 'ignore'). \
					decode('latin-1')
		
		proposicao_principal = arruma_campo(proposicao['proposicao_principal'] \
			if proposicao['proposicao_principal'] != 0 or \
			proposicao['proposicao_principal'] == None else None)
		
		executa_query('INSERT INTO proposicoes (id_proposicao, nome, tipo, ' \
			'numero, ano, orgao_num, data_apresentacao, ementa, ' \
			'explicacao_ementa, regime, apreciacao, qtd_autores, autor1, ' \
			'proposicao_principal, despacho_data, despacho_texto, situacao, ' \
			'orgao_estado, indices, link_teor, link_conteudo, formato_teor, ' \
			'inteiro_teor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ' \
			'%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', \
			(arruma_campo(p), arruma_campo(proposicao, 'nome'), \
			arruma_campo(proposicao, 'tipo'), arruma_campo(proposicao, \
			'numero'), arruma_campo(proposicao, 'ano'), \
			arruma_campo(proposicao, 'orgao_num'), arruma_campo(proposicao, \
			'data_apresentacao'), arruma_campo(proposicao, 'ementa'), \
			arruma_campo(proposicao, 'explicacao_ementa'), \
			arruma_campo(proposicao, 'regime'), arruma_campo(proposicao, \
			'apreciacao'), arruma_campo(proposicao, 'qtd_autores'), \
			arruma_campo(id_autor), proposicao_principal, despacho_data, \
			despacho_texto, arruma_campo(proposicao, 'situacao'), \
			arruma_campo(proposicao, 'orgao_estado'), arruma_campo(proposicao, \
			'indices'), arruma_campo(proposicao, 'link_teor'), link_conteudo, \
			formato_teor, inteiro_texto), conexao)

def salva_deputados_extra(conexao, bancada_partido, bancada_bloco):
	deputados = carrega_dados(pasta + 'deputados.pkl')
	
	bancada_bloco['M'] = bancada_bloco['Minoria']
	bancada_bloco['I'] = bancada_bloco['MinoriaCN']
	bancada_bloco['G'] = bancada_bloco['Governo']
	
	for b in bancada_partido.keys():
		bancada_partido[b.upper()] = bancada_partido[b]
	
	for id_deputado in deputados.keys():
		deputado = deputados[id_deputado]
		
		legislaturas = deputado['legislaturas']
		
		for legislatura in legislaturas:
			ano_inicio = 2011 - 4 * (54 - legislatura)
			executa_query('INSERT INTO deputados_legislaturas (id_deputado, ' \
				'ano_inicio) VALUES (%s, %s)', (arruma_campo(id_deputado), \
				ano_inicio), conexao)
		
		if 'exercicios' not in deputado.keys():
			continue
		
		exercicios = deputado['exercicios']
		
		for exercicio in exercicios:
			executa_query('INSERT INTO deputados_exercicios (id_deputado, ' \
				'data_inicio, data_fim, uf, situacao, causa_fim, ' \
				'causa_fim_descr) VALUES (%s, %s, %s, %s, %s, %s, %s)', \
				(arruma_campo(id_deputado), arruma_campo(exercicio, \
				'data_inicio'), arruma_campo(exercicio, 'data_fim'), \
				arruma_campo(exercicio, 'uf'), arruma_campo(exercicio, \
				'situacao'), arruma_campo(exercicio, 'causa_fim'), \
				arruma_campo(exercicio, 'causa_fim_descr')), conexao)
		
		comissoes = deputado['comissoes']
		
		for id_comissao in comissoes.keys():
			comissao_aux = comissoes[id_comissao]
			
			for comissao in comissao_aux:
				condicao = arruma_campo(comissao, 'condicao')
				
				if condicao != None:
					executa_query('INSERT INTO deputados_orgaos (id_deputado,' \
						' sigla_orgao, data_entrada, data_saida, condicao) ' \
						'VALUES (%s, %s, %s, %s, %s)', ( \
						arruma_campo(id_deputado), arruma_campo(id_comissao), \
						arruma_campo(comissao, 'data_entrada'), \
						arruma_campo(comissao, 'data_saida'), condicao), \
						conexao)
				
				for cargo in comissao['cargos']:
					executa_query('INSERT INTO deputados_orgaos_cargos ' \
						'(id_deputado, sigla_orgao, data_entrada, ' \
						'data_saida, id_cargo) VALUES (%s, %s, %s, %s, %s)', \
						(arruma_campo(id_deputado), arruma_campo(id_comissao), \
						arruma_campo(cargo, 'data_entrada'), \
						arruma_campo(cargo, 'data_saida'), arruma_campo(cargo, \
						'cargo')), conexao)
		
		partidos = deputado['partidos_anteriores']
		
		for partido in partidos:
			executa_query('INSERT INTO deputados_partidos (id_deputado, ' \
				'id_partido, data_saida) VALUES (%s, %s, %s)', \
				(arruma_campo(id_deputado), arruma_campo(partido, 'partido'), \
				arruma_campo(partido, 'data_saida')), conexao)
		
		liderancas = deputado['lideranca']
		
		for lideranca in liderancas:
			executa_query('INSERT INTO deputados_lideranca (id_deputado, ' \
				'id_bancada, data_inicio, data_fim, cargo, num_ordem) VALUES ' \
				'(%s, %s, %s, %s, %s, %s)', \
				(arruma_campo(id_deputado), bancada_partido[ \
				lideranca['bancada']] if lideranca['tipo'] == 'P' else \
				bancada_bloco[lideranca['bancada']], arruma_campo(lideranca, \
				'data_inicio'), arruma_campo(lideranca, 'data_fim'), \
				arruma_campo(lideranca, 'cargo'), arruma_campo(lideranca, \
				'num_ordem')), conexao)
		
		nomes_parlamentares = deputado['nomes_parlamentares_anteriores']
		
		for nome_parlamentar in nomes_parlamentares:
			executa_query('INSERT INTO deputados_historico_nomes ' \
				'(id_deputado, nome_parlamentar, fim_uso) VALUES (%s, %s, ' \
				'%s)', (arruma_campo(id_deputado), arruma_campo( \
				nome_parlamentar, 'nome_parlamentar'), arruma_campo( \
				nome_parlamentar, 'fim_uso')), conexao)

def salva_proposicoes_topicos(conexao):
	topicos_proposicoes = carrega_dados('ml_' + pasta + \
		'proposicoes_topicos.pkl')
	
	for i in range(len(topicos_proposicoes)):
		topico = topicos_proposicoes[i]
		executa_query('INSERT INTO ml_topicos (id_topico, peso, tipo) ' \
			'VALUES (%s, %s, %s)', (i, sum(zip(*topico)[1]), 'P'), conexao)
		
		for palavra in topico:
			executa_query('INSERT INTO ml_topicos_palavras ' \
				'(id_topico, palavra, peso) VALUES (%s, %s, %s)', (i, \
				arruma_campo(palavra[0]), palavra[1]), conexao)
	
	return len(topicos_proposicoes)

def salva_dados_eleicoes(conexao):
	deputados = carrega_dados(pasta + 'deputados.pkl')
	
	pessoas = {}
	tipo_bens = {}
	
	for deputado in deputados.values():
		if 'eleicao' not in deputado.keys() or deputado['eleicao'] == {}:
			continue
		
		try:
			for bem in deputado['eleicao']['bens']:
				tipo_bens[bem['cod_tipo_bem']] = bem['descr_tipo_bem']
		except KeyError:
			pass
		
		try:
			for despesa in deputado['eleicao']['despesas']:
				pessoas[despesa['cpf_cnpj']] = (despesa['nome_fornecedor'], \
					despesa['pessoa_fisica'])
		except KeyError:
			pass
		
		try:
			for receita in deputado['eleicao']['receitas']:
				pessoas[receita['cpf_cnpj']] = (receita['nome_doador'], \
					receita['pessoa_fisica'])
		except KeyError:
			pass

	for tipo_bem in tipo_bens.keys():
		executa_query('INSERT INTO tipos_bens (id_tipo_bem, descricao) ' \
			'VALUES (%s, %s)', (tipo_bem, arruma_campo(tipo_bens[tipo_bem])), \
			conexao)
	
	for cpf in pessoas.keys():
		executa_query('INSERT INTO pessoas (cpf_cnpj, nome, tipo_pessoa) ' \
			'VALUES (%s, %s, %s)', (cpf, pessoas[cpf][0], 'F' if \
			pessoas[cpf][1] else 'J'), conexao)
		
	for id_deputado in deputados.keys():
		try:
			eleicao = deputados[id_deputado]['eleicao']
		except KeyError:
			continue
		
		if 'bens' in eleicao.keys():
			for bem in eleicao['bens']:
				executa_query('INSERT INTO deputados_eleicoes_bens ' \
					'(id_deputado, id_eleicao, id_tipo_bem, descricao, valor)' \
					' VALUES (%s, %s, %s, %s, %s)', \
					(arruma_campo(id_deputado), 2010, arruma_campo(bem, \
					'cod_tipo_bem'), arruma_campo(bem, 'descr_bem'), \
					arruma_campo(bem, 'valor')), conexao)
		
		if 'despesas' in eleicao.keys():
			for despesa in eleicao['despesas']:
				cpf = arruma_campo(despesa, 'cpf_cnpj')
				cpf = None if cpf < 0 else cpf
				
				no_documento = arruma_campo(despesa, 'no_documento')
				no_documento = None if no_documento < 0 else no_documento
				
				executa_query('INSERT INTO deputados_eleicoes_despesas ' \
					'(id_deputado, id_eleicao, tipo_documento, num_documento,' \
					' cpf_cnpj, data_despesa, valor, tipo, fonte, especie, ' \
					'descricao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, ' \
					'%s, %s)', (arruma_campo(id_deputado), 2010, arruma_campo( \
					despesa, 'tipo_documento'), no_documento, cpf, \
					arruma_campo(despesa, 'data_despesa'), \
					arruma_campo(despesa, 'valor'), arruma_campo(despesa, \
					'tipo'), arruma_campo(despesa, 'fonte'), \
					arruma_campo(despesa, 'especie'), arruma_campo(despesa, \
					'descricao')), conexao)
		
		if 'receitas' in eleicao.keys():
			for receita in eleicao['receitas']:
				cpf = arruma_campo(receita, 'cpf_cnpj')
				cpf = None if cpf < 0 else cpf
				
				recibo = arruma_campo(receita, 'recibo')
				recibo = None if recibo < 0 else recibo
				
				no_documento = arruma_campo(receita, 'no_documento')
				no_documento = None if no_documento < 0 else no_documento

				executa_query('INSERT INTO deputados_eleicoes_receitas ' \
					'(id_deputado, id_eleicao, recibo, num_documento, ' \
					'cpf_cnpj, data_doacao, valor, tipo, fonte, especie, ' \
					'descricao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, ' \
					'%s, %s)', (arruma_campo(id_deputado), 2010, recibo, \
					no_documento, cpf, arruma_campo(receita, 'data_doacao'), \
					arruma_campo(receita, 'valor'), arruma_campo(receita, \
					'tipo'), arruma_campo(receita, 'fonte'), \
					arruma_campo(receita, 'especie'), arruma_campo(receita, \
					'descricao')), conexao)

def salva_proposicoes_detalhes(conexao):
	proposicoes = carrega_dados(pasta + 'proposicoes.pkl')
	
	for id_proposicao in proposicoes.keys():
		for chave in ['substitutivos', 'redacoes_finais', 'emendas']:
			if chave not in proposicoes[id_proposicao].keys():
				continue
			
			for id_menor in proposicoes[id_proposicao][chave]:
				executa_query('INSERT INTO proposicoes_referencias ' \
					'(id_proposicao_menor, id_proposicao_referida, tipo) ' \
					'VALUES (%s, %s, %s)', (arruma_campo(id_menor), \
					arruma_campo(id_proposicao), arruma_campo(chave[0]. \
					upper())), conexao)
	
	relatorios_proposicoes = carrega_dados(pasta + 'relatorios_proposicoes.pkl')
	
	for id_proposicao in relatorios_proposicoes.keys():
		for id_orgao in relatorios_proposicoes[id_proposicao].keys():
			relatorio = relatorios_proposicoes[id_proposicao][id_orgao]
			
			executa_query('INSERT INTO proposicoes_relatorios (id_proposicao,' \
				' sigla_orgao, id_relator, parecer) VALUES (%s, %s, %s, %s)', \
				(arruma_campo(id_proposicao), arruma_campo(id_orgao), \
				arruma_campo(relatorio, 'relator'), arruma_campo(relatorio, \
				'parecer')), conexao)
	
	andamentos = carrega_dados(pasta + 'andamentos.pkl')
	
	for id_proposicao in andamentos.keys():
		andamento = andamentos[id_proposicao]
		
		for tipo in andamento.keys():
			for aux in andamento[tipo]:
				executa_query('INSERT INTO proposicoes_tramitacoes ' \
					'(id_proposicao, sigla_orgao, data, descricao, tipo) ' \
					'VALUES (%s, %s, %s, %s, %s)', (id_proposicao, id_orgao, \
					arruma_campo(aux, 'data'), arruma_campo(aux, 'descricao'), \
					arruma_campo(tipo[0].upper())), conexao)

def salva_despesas_cota(conexao, bancada_partido, bancada_bloco):
	deputados_por_nome = carrega_dados(pasta + 'deputados_por_nome.pkl')
	despesas = {}
	
	for instante in ['outros', 'anterior', 'atual']:
		despesas[instante] = carrega_dados(pasta + 'despesas_' + instante + \
			'.pkl')
	
	tipos = set(itertools.chain(*[list(itertools.chain(*[list( \
		itertools.chain(*[[(d['cod_tipo_despesa'], d['descricao']) for d in \
		dc] for dc in dt.values()])) for dt in di.values()])) for di in \
		despesas.values()]))
	
	for tipo in tipos:
		executa_query('INSERT INTO despesas_cota_tipos (cod_tipo_despesa, ' \
			'descricao) VALUES (%s, %s)', (arruma_campo(tipo[0]), \
			arruma_campo(tipo[1])), conexao)
	
	tipos_detalhados = set(itertools.chain(*[list(itertools.chain(*[list( \
		itertools.chain(*[[(d['cod_tipo_detalhado'], d['descricao_detalhada']) \
		for d in dc] for dc in dt.values()])) for dt in di.values()])) for di \
		in despesas.values()]))
	
	for tipo_detalhado in tipos_detalhados:
		executa_query('INSERT INTO despesas_cota_tipos_detalhados ' \
			'(cod_tipo_detalhado, descricao) VALUES (%s, %s)', \
			(arruma_campo(tipo_detalhado[0]), arruma_campo( \
			tipo_detalhado[1])), conexao)
	
	pessoas = set(itertools.chain(*[list(itertools.chain(*[list( \
		itertools.chain(*[[(d['cpf_cnpj'], d['beneficiario'], \
		d['pessoa_fisica']) for d in dc] for dc in dt.values()])) for dt in \
		di.values()])) for di in despesas.values()]))
	
	for pessoa in pessoas:
		if pessoa[0] < 0:
			continue
		
		try:
			executa_query('INSERT INTO pessoas (cpf_cnpj, nome, tipo_pessoa) ' \
				'VALUES (%s, %s, %s)', (arruma_campo(pessoa[0]), \
				arruma_campo(pessoa[1]), 'F' if pessoa[2] else 'J'), conexao, \
				False)
		except _mysql_exceptions.IntegrityError:
			pass
	
	id_centro_custo = 0
	equivalencia = {}
	origens = set(itertools.chain(*[list(itertools.chain(*[[(t, o) for o in \
		di[t].keys()] for t in di.keys()])) for di in despesas.values()]))
	
	for (tipo_origem, id_origem) in origens:
		try:
			equivalencia[tipo_origem][id_origem] = id_centro_custo
		except KeyError:
			equivalencia[tipo_origem] = {}
			equivalencia[tipo_origem][id_origem] = id_centro_custo
		
		if tipo_origem == 'deputado':
			campo = 'id_deputado'
		elif tipo_origem in ['partido', 'lideranca_part']:
			id_origem = bancada_partido[id_origem.upper()]
			campo = 'id_bancada'
		elif tipo_origem == 'orgao':
			campo = 'sigla_orgao'
		else:
			if tipo_origem == 'lideranca_cn':
				id_origem = bancada_bloco[id_origem + 'CN']
			else:
				id_origem = bancada_bloco[id_origem]
			
			campo = 'id_bancada'
		
		executa_query('INSERT INTO centros_custos (id_centro_custo, ' + campo \
			+ ', tipo) VALUES (%s, %s, %s)', (arruma_campo(id_centro_custo), \
			arruma_campo(id_origem), arruma_campo(tipo_origem)), conexao)
		
		id_centro_custo += 1
	
	id_despesa = 0
	
	for instante in despesas.keys():
		for tipo_origem in despesas[instante].keys():
			for id_origem in despesas[instante][tipo_origem].keys():
				id_centro_custo = equivalencia[tipo_origem][id_origem]
				
				for despesa in despesas[instante][tipo_origem][id_origem]:
					cpf = arruma_campo(despesa, 'cpf_cnpj')
					cpf = None if cpf < 0 else cpf
					
					executa_query('INSERT INTO despesas_cota (id_despesa, ' \
						'id_centro_custo, cod_tipo_despesa, ' \
						'cod_tipo_detalhado, cpf_cnpj, tipo_documento, ' \
						'numero_documento, data_emissao, valor_documento, ' \
						'valor_glosa, valor_liquido, mes_debito, ano_debito, ' \
						'num_parcela, num_lote, num_ressarcimento) VALUES ' \
						'(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,' \
						' %s, %s, %s)', (arruma_campo(id_despesa), \
						arruma_campo(id_centro_custo), arruma_campo(despesa, \
						'cod_tipo_despesa'), arruma_campo(despesa, \
						'cod_tipo_detalhado'), cpf, arruma_campo(despesa, \
						'tipo_documento'), arruma_campo(despesa, \
						'numero_documento'), arruma_campo(despesa, \
						'data_emissao'), arruma_campo(despesa, \
						'valor_documento'), arruma_campo(despesa, \
						'valor_glosa'), arruma_campo(despesa, \
						'valor_liquido'), arruma_campo(despesa, 'mes_debito'), \
						arruma_campo(despesa, 'ano_debito'), arruma_campo( \
						despesa, 'num_parcela'), arruma_campo(despesa, \
						'num_lote'), arruma_campo(despesa, \
						'num_ressarcimento')), conexao)
				
					id_despesa += 1

def _int(valor):
	try:
		return int(valor)
	except ValueError:
		return None

def _bloco(nome, blocos, blocos_por_nome, bancada_partido, bancada_bloco, \
	conexao):
	
	if nome in blocos.keys():
		return nome
	
	partidos_aux = nome.split("/")
	
	if len(partidos_aux) > 1:
		partidos = map(lambda a: uniformiza(a), partidos_aux)
	else:
		partidos_aux = re.split(r'([A-Z][a-z]+)', nome)
		partidos = [normaliza(p) for p in partidos_aux[1::2]]
	
	nome = ', '.join(partidos)
	
	if nome in blocos_por_nome.keys():
		return blocos_por_nome[nome]
	
	# TODO Inserir blocos, partidos nos blocos e bancadas
	id_bloco = min([b for b in [_int(b) for b in blocos.keys()] if b != None]) \
		- 1
	id_bancada = max(bancada_partido.values() + bancada_bloco.values()) + 1
	
	executa_query('INSERT INTO blocos (id_bloco, nome) VALUES (%s, %s)', \
		(arruma_campo(id_bloco), arruma_campo(nome)), conexao)
	
	executa_query('INSERT INTO bancadas (id_bancada, id_bloco) VALUES ' \
		'(%s, %s)', (arruma_campo(id_bancada), arruma_campo(id_bloco)), \
		conexao)
	bancada_bloco[id_bloco] = id_bancada
	
	for partido in partidos:
		executa_query('INSERT INTO partidos_blocos (id_bloco, id_partido) ' \
			'VALUES (%s, %s)', (arruma_campo(id_bloco), arruma_campo( \
			partido)), conexao)
	
	blocos[id_bloco] =  { \
		"sigla_bloco": nome, \
		"nome_bloco": nome, \
		"representante": None, \
		"data_criacao": None, \
		"data_extincao": None, \
		"partidos": [{ \
			'partido': p, \
			'data_adesao': None, \
			'data_desligamento': None \
			} for p in partidos]}
	blocos_por_nome[nome] = id_bloco
	
	return id_bloco

equivalencias_voto = {'SIM': 0, 'NAO': 1, 'ABSTENCAO': 2, 'ART. 17': 3, \
	'OBSTRUCAO': 4, 'LIBERADO': 5}

def salva_votacoes_proposicoes(conexao, blocos, blocos_por_nome, \
	bancada_partido, bancada_bloco):
	
	proposicoes = carrega_dados(pasta + 'proposicoes.pkl')
	id_votacao = 0
	
	for id_proposicao in proposicoes.keys():
		proposicao = proposicoes[id_proposicao]
		
		for votacao in proposicao['votacoes']:
			
			votos_favor = len([v for v in votacao['votos'].values() \
				if v['voto'] == 'SIM'])
			votos_contra = len([v for v in votacao['votos'].values() \
				if v['voto'] == 'NAO'])
			
			executa_query('INSERT INTO votacoes (id_votacao, id_proposicao, ' \
				'resumo, data_votacao, votos_favor, votos_contra) VALUES (%s,' \
				' %s, %s, %s, %s, %s)', (arruma_campo(id_votacao), \
				arruma_campo(id_proposicao), arruma_campo(votacao, 'resumo'), 
				arruma_campo(votacao, 'data'), arruma_campo(votos_favor), \
				arruma_campo(votos_contra)), conexao)
			
			for id_partido in votacao['orientacao_bancada']['partidos'].keys():
				orientacao = equivalencias_voto[votacao['orientacao_bancada'] \
					['partidos'][id_partido]]
				
				executa_query('INSERT INTO orientacoes_votos (id_votacao, ' \
					'id_bancada, orientacao) VALUES (%s, %s, %s)', \
					(arruma_campo(id_votacao), arruma_campo(bancada_partido[ \
					id_partido.upper()]), arruma_campo(orientacao)), conexao)
			
			for nome_bloco in votacao['orientacao_bancada']['blocos'].keys():
				orientacao = equivalencias_voto[votacao['orientacao_bancada'] \
					['blocos'][nome_bloco]]
				id_bloco = _bloco(nome_bloco, blocos, blocos_por_nome, \
					bancada_partido, bancada_bloco, conexao)
				
				executa_query('INSERT INTO orientacoes_votos (id_votacao, ' \
					'id_bancada, orientacao) VALUES (%s, %s, %s)', \
					(arruma_campo(id_votacao), arruma_campo(bancada_bloco[ \
					id_bloco]), arruma_campo(orientacao)), conexao)
			
			for id_deputado in votacao['votos'].keys():
				voto = votacao['votos'][id_deputado]
				
				executa_query('INSERT INTO votos (id_votacao, id_deputado, ' \
					'id_partido, voto) VALUES (%s, %s, %s, %s)', \
					(arruma_campo(id_votacao), arruma_campo(id_deputado), \
					arruma_campo(voto, 'partido'), arruma_campo( \
					equivalencias_voto[voto['voto']])), conexao)
			
			id_votacao += 1

def salva_votacoes_eleicoes(conexao):
	municipios = carrega_dados(pasta + 'municipios.pkl')
	
	for id_municipio in municipios.keys():
		municipio = municipios[id_municipio]
		
		executa_query('INSERT INTO municipios (id_municipio, ' \
			'id_municipio_tse, uf, nome, latitude, longitude) VALUES (%s, %s,' \
			' %s, %s, %s, %s)', (arruma_campo(id_municipio), \
			arruma_campo(municipio, 'cod_tse'), arruma_campo(municipio, 'uf'), \
			arruma_campo(municipio, 'nome'), arruma_campo(municipio, \
			'latitude'), arruma_campo(municipio, 'longitude')), conexao)
		
		for chave in set(municipio.keys()) - set(['cod_tse', 'uf', 'nome', \
			'latitude', 'longitude']):

			executa_query('INSERT INTO municipios_dados (id_municipio, ' \
				'chave, valor, unidades) VALUES (%s, %s, %s, %s)', \
				(arruma_campo(id_municipio), arruma_campo(chave), \
				arruma_campo(municipio[chave][0]), arruma_campo( \
				municipio[chave][1])), conexao)
	
	votacoes = carrega_dados(pasta + 'votacoes.pkl')
	
	for id_municipio in votacoes.keys():
		votacao = votacoes[id_municipio]
		
		for zona in votacao.keys():
			for id_deputado in votacao[zona].keys():
				executa_query('INSERT INTO deputados_eleicoes_votacoes ' \
					'(id_municipio, zona, id_deputado, id_eleicao, votos) ' \
					'VALUES (%s, %s, %s, %s, %s)', \
					(arruma_campo(id_municipio), arruma_campo(zona), \
					arruma_campo(id_deputado), arruma_campo(2010), \
					arruma_campo(votacao[zona][id_deputado])), conexao)

equivalencia_frequencia = {'PRESENCA': 0, 'AUSENCIA': 1, \
	'AUSENCIA JUSTIFICADA': 2, 'ORDEM DO DIA CANCELADA': 3, '--------': 4}

def salva_sessoes(conexao):
	reunioes = carrega_dados(pasta + 'presencas.pkl')
	discursos = carrega_dados(pasta + 'discursos.pkl')
	
	codigos_sessoes = {}
	reunioes_sessoes_falta = {}
	reunioes_falta = set([d['data_sessao'].date() for d in discursos])
	
	for (data, cod) in set([(d['data_sessao'], d['cod_sessao']) for d in \
		discursos]):
		
		id_sessao = int(cod.split('.')[0])
		data = data.date()
		
		try:
			codigos_sessoes[data][id_sessao] = cod
			reunioes_sessoes_falta[data].add(id_sessao)
		except KeyError:
			codigos_sessoes[data] = {id_sessao: cod}
			reunioes_sessoes_falta[data] = set([id_sessao])
	
	for data_reuniao in reunioes.keys():
		reuniao = reunioes[data_reuniao]
		
		try:
			reunioes_falta.remove(data_reuniao)
		except KeyError:
			pass
		
		executa_query('INSERT INTO reunioes (data_reuniao, legislatura) ' \
			'VALUES (%s, %s)', (arruma_campo(data_reuniao), \
			arruma_campo(reuniao, 'legislatura')), conexao)
		
		for descr_sessao in reuniao['sessoes'].keys():
			id_sessao = - (hash(descr_sessao) % 1000)
			limpa = re.sub(r'[0-9]{2}\.?\ ?\/\ ?[0-9]{2}\ ?\/\ ?[0-9]{2}' \
				'([0-9]{2})?', '', descr_sessao)
			partes = re.findall(r'[0-9]+', limpa)
			
			if len(partes) == 1:
				id_sessao = int(partes[0])
			
			try:
				reunioes_sessoes_falta[data_reuniao].remove(id_sessao)
			except KeyError:
				pass
			
			try:
				cod_sessao = codigos_sessoes[data_reuniao][id_sessao]
			except KeyError:
				cod_sessao = None
			
			executa_query('INSERT INTO sessoes (id_sessao, reuniao, codigo, ' \
				'inicio, descricao) VALUES (%s, %s, %s, %s, %s)', \
				(arruma_campo(id_sessao), arruma_campo(data_reuniao), \
				cod_sessao, arruma_campo(reuniao['sessoes'][descr_sessao], \
				'inicio'), descr_sessao), conexao)
		
		for id_deputado in reuniao['deputados'].keys():
			info_deputado = reuniao['deputados'][id_deputado]

			executa_query('INSERT INTO deputados_reunioes_presencas ' \
				'(id_deputado, data_reuniao, frequencia, justificativa, ' \
				'presenca_externa) VALUES (%s, %s, %s, %s, %s)', \
				(arruma_campo(id_deputado), arruma_campo(data_reuniao), \
				arruma_campo(equivalencia_frequencia[info_deputado[ \
				'frequencia']]), arruma_campo(info_deputado, 'justificativa'), \
				arruma_campo(info_deputado, 'presenca_externa')), conexao)
			
			for descr_sessao in info_deputado['sessoes'].keys():
				id_sessao = - (hash(descr_sessao) % 1000)
				limpa = re.sub(r'[0-9]{2}\.?\ ?\/\ ?[0-9]{2}\ ?\/\ ?[0-9]{2}' \
					'([0-9]{2})?', '', descr_sessao)
				partes = re.findall(r'[0-9]+', limpa)
			
				if len(partes) == 1:
					id_sessao = int(partes[0])
				
				executa_query('INSERT INTO deputados_sessoes_presencas ' \
					'(id_deputado, data_reuniao, id_sessao, frequencia) ' \
					'VALUES (%s, %s, %s, %s)', (arruma_campo(id_deputado), \
					arruma_campo(data_reuniao), arruma_campo(id_sessao), \
					arruma_campo(equivalencia_frequencia[info_deputado \
					['sessoes'][descr_sessao]['presenca']])), conexao)
	
	fases = set([(d['cod_fase'], d['descricao_fase']) for d in discursos])
	
	for fase in fases:
		executa_query('INSERT INTO fases_sessoes (cod_fase, descricao) ' \
			'VALUES (%s, %s)', (arruma_campo(fase[0]), arruma_campo(fase[1])), \
			conexao)
	
	id_discurso = 0
	
	for discurso in discursos:
		id_sessao = int(discurso['cod_sessao'].split('.')[0])
		data_sessao = discurso['data_sessao'].date()
		
		if data_sessao in reunioes_falta:
			legislatura = int(54 - math.ceil((2010 - (data_sessao - \
				datetime.timedelta(days=31)).year) / 4))
			executa_query('INSERT INTO reunioes (data_reuniao, legislatura) ' \
				'VALUES (%s, %s)', (arruma_campo(data_sessao), \
				arruma_campo(legislatura)), conexao)
			reunioes_falta.remove(data_sessao)
		
		if id_sessao in reunioes_sessoes_falta[data_sessao]:
			executa_query('INSERT INTO sessoes (id_sessao, reuniao, codigo, ' \
				'inicio, descricao) VALUES (%s, %s, %s, %s, %s)', \
				(arruma_campo(id_sessao), arruma_campo(data_sessao), \
				arruma_campo(discurso, 'cod_sessao'), None, None), conexao)
			reunioes_sessoes_falta[data_sessao].remove(id_sessao)
		
		executa_query('INSERT INTO discursos (id_discurso, id_deputado, ' \
			'data_reuniao, id_sessao, numero_sessao, tipo_sessao, cod_fase, ' \
			'numero_orador, numero_quarto, numero_insercao, hora_inicio, ' \
			'sumario, inteiro_teor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, ' \
			'%s, %s, %s, %s, %s)', (arruma_campo(id_discurso), \
			arruma_campo(discurso, 'id_deputado'), data_sessao, \
			arruma_campo(id_sessao), arruma_campo(discurso, \
			'numero_sessao'), arruma_campo(discurso, 'tipo_sessao'), \
			arruma_campo(discurso, 'cod_fase'), arruma_campo(discurso, \
			'numero_orador'), arruma_campo(discurso, 'numero_quarto'), \
			arruma_campo(discurso, 'numero_insercao'), arruma_campo(discurso, \
			'hora_inicio'), arruma_campo(discurso, 'sumario'), \
			arruma_campo(discurso, 'inteiro_teor')), conexao)
		
		id_discurso += 1

def salva_reunioes_orgaos(conexao):
	orgaos = carrega_dados(pasta + 'orgaos.pkl')
	
	id_reuniao_orgao = 0
	
	for id_orgao in orgaos.keys():
		orgao = orgaos[id_orgao]
		
		if 'reunioes' not in orgao.keys():
			continue
		
		for cod_reuniao in orgao['reunioes'].keys():
			reuniao = orgao['reunioes'][cod_reuniao]
			
			executa_query('INSERT INTO orgaos_reunioes (id_reuniao_orgao, ' \
				'sigla_orgao, cod_reuniao, data_hora, local, estado, tipo, ' \
				'objeto) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', \
				(arruma_campo(id_reuniao_orgao), arruma_campo(id_orgao), \
				arruma_campo(cod_reuniao), arruma_campo(reuniao, 'data_hora'), \
				arruma_campo(reuniao, 'local'), arruma_campo(reuniao, \
				'estado'), arruma_campo(reuniao, 'tipo'), \
				arruma_campo(reuniao, 'objeto')), conexao)
			
			for id_proposicao in reuniao['proposicoes']:
				executa_query('INSERT INTO orgaos_reunioes_proposicoes \
					(id_reuniao_orgao, id_proposicao) VALUES (%s, %s)', \
					(arruma_campo(id_reuniao_orgao), \
					arruma_campo(id_proposicao)), conexao)
			
			id_reuniao_orgao += 1


def salva_dados_eleicoes2(conexao):
	deputados = carrega_dados(pasta + 'deputados.pkl')
	executa_query('TRUNCATE TABLE deputados_eleicoes_receitas', conexao)
	
	for id_deputado in deputados.keys():
		try:
			eleicao = deputados[id_deputado]['eleicao']
		except KeyError:
			continue
		
		if 'receitas' in eleicao.keys():
			for receita in eleicao['receitas']:
				cpf = arruma_campo(receita, 'cpf_cnpj')
				cpf = None if cpf < 0 else cpf
				
				recibo = arruma_campo(receita, 'recibo')
				recibo = None if recibo < 0 else recibo
				
				no_documento = arruma_campo(receita, 'no_documento')
				no_documento = None if no_documento < 0 else no_documento

				executa_query('INSERT INTO deputados_eleicoes_receitas ' \
					'(id_deputado, id_eleicao, recibo, num_documento, ' \
					'cpf_cnpj, data_doacao, valor, tipo, fonte, especie, ' \
					'descricao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, ' \
					'%s, %s)', (arruma_campo(id_deputado), 2010, recibo, \
					no_documento, cpf, arruma_campo(receita, 'data_doacao'), \
					arruma_campo(receita, 'valor'), arruma_campo(receita, \
					'tipo'), arruma_campo(receita, 'fonte'), \
					arruma_campo(receita, 'especie'), arruma_campo(receita, \
					'descricao')), conexao)



conexao = MySQLdb.connect(host='localhost', user=usuario, passwd=senha, db=banco)

remove = False

if remove:
	queries_remocao = ['DELETE FROM proposicoes WHERE 1', \
		'DELETE FROM situacoes WHERE 1', \
		'DELETE FROM regimes WHERE 1', \
		'DELETE FROM proposicoes_tipos WHERE 1', \
		'DELETE FROM orgaos WHERE 1', \
		'DELETE FROM autores_proposicoes WHERE 1', \
		'DELETE FROM autores_tipos WHERE 1', \
		'DELETE FROM deputados WHERE 1', \
		'DELETE FROM profissoes WHERE 1', \
		'DELETE FROM graus_instrucao WHERE 1', \
		'DELETE FROM partidos WHERE 1', \
		'DELETE FROM apreciacoes WHERE 1']

	for query in queries_remocao:
		executa_query(query, conexao)

blocos = carrega_dados(pasta + 'blocos.pkl')
blocos_por_nome = dict([(blocos[b]['sigla_bloco'], b) for b in blocos.keys()])
blocos_por_nome['GOVERNO'] = blocos_por_nome['GOV'] = blocos_por_nome['Gov.']

try:
	print 'Salvando dados eleitorais dos deputados...'
	salva_dados_eleicoes2(conexao)
	"""
	print 'Salvando apreciacoes...'
	salva_apreciacoes(conexao)
	
	print 'Salvando partidos...'
	bancada_partido, bancada_bloco = salva_partidos(conexao)
	
	salva_dados(bancada_partido, pasta + 'bancada_partido.pkl')
	salva_dados(bancada_bloco, pasta + 'bancada_bloco.pkl')
	
	print 'Salvando orgaos...'
	salva_orgaos(conexao)
	
	print 'Salvando deputados...'
	salva_deputados(conexao)

	print 'Salvando detalhes de deputados...'
	salva_deputados_extra(conexao, bancada_partido, bancada_bloco)
	
	print 'Salvando dados eleitorais dos deputados...'
	salva_dados_eleicoes(conexao)
	
	print 'Salvando autores de proposicoes...'
	salva_autores_proposicoes(conexao)
	conexao.commit()
	
	print 'Salvando proposicões...'
	salva_proposicoes(conexao)
	conexao.commit()
	
	print 'Salvando detalhes de proposicoes...'
	salva_proposicoes_detalhes(conexao)
	
	print 'Salvando dados de topicos de proposicoes...'
	ultimo_topico = salva_proposicoes_topicos(conexao)
	conexao.commit()
	
	print 'Salvando detalhes de gasto da cota...'
	latin1 = True
	salva_despesas_cota(conexao, bancada_partido, bancada_bloco)
	conexao.commit()
	latin1 = False
	
	print 'Salvando dados de votacoes de proposicoes...'
	salva_votacoes_proposicoes(conexao, blocos, blocos_por_nome, \
		bancada_partido, bancada_bloco)
	salva_dados(bancada_bloco, pasta + 'bancada_bloco.pkl')
	salva_dados(blocos, pasta + 'blocos.pkl')
	conexao.commit()
	
	print 'Salvando dados de votacoes em eleicoes...'
	salva_votacoes_eleicoes(conexao)
	conexao.commit()
	
	print 'Salvando dados de sessoes e reunioes...'
	salva_sessoes(conexao)
	conexao.commit()
	
	print 'Salvando dados de reunioes de orgaos...'
	salva_reunioes_orgaos(conexao)
	"""
	conexao.commit()
except:
	conexao.rollback()
	raise

conexao.close()

print 'Finalizado!'

