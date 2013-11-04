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
import cPickle as pickle
import datetime
import re
import itertools

usuario = ''
senha = ''
banco = ''

pasta = 'dados_deputados/'

def salva_dados(dados, nome_arquivo):
	with open(nome_arquivo, 'wb') as arquivo_dados:
		pickle.dump(dados, arquivo_dados)

def carrega_dados(nome_arquivo):
	with open(nome_arquivo, 'rb') as arquivo_dados:
		return pickle.load(arquivo_dados)

def decode(texto):
	for encoding in ['utf8', 'iso-8859-1']:
		try:
			texto = texto.decode(encoding)
			break
		except UnicodeEncodeError:
			pass
	
	return texto.replace(u'‘', '\'').replace(u'’', '\'').replace(u'“', '"'). \
		replace(u'”', '"').replace(u'–', '-').replace(u'—', '-'). \
		replace(u'…', '...')

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

def executa_query(query, dados, conexao=None):
	if conexao == None:
		conexao = dados
		cursor = conexao.cursor()
		
		try:
			cursor.execute(query)
		except:
			print query
			raise
		return
	
	cursor = conexao.cursor()
	
	try:
		cursor.execute(query, dados)
	except:
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
		
		executa_query('INSERT INTO blocos (id_bloco, sigla, data_criacao, ' \
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
		'eleicao' in d.keys()])
	
	for grau in graus:
		executa_query('INSERT INTO graus_instrucao (id_grau, descricao) ' \
			'VALUES (%s, %s)', (grau[0], grau[1]), conexao)

	profissoes_tse = set([(d['eleicao']['ocupacao_codigo'], decode( \
		d['eleicao']['ocupacao_descr']).capitalize()) for d in \
		deputados.values() if 'eleicao' in d.keys()])
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
		
		if 'eleicao' in deputado.keys():
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
	
	bancada_bloco['MinoriaCD'] = 107
	bancada_bloco['MaioriaCD'] = 108
	
	bancada_bloco['M'] = bancada_bloco['Minoria']
	bancada_bloco['I'] = bancada_bloco['MinoriaCD']
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
		if 'eleicao' not in deputado.keys():
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
				cpf = arruma_campo(despesa, 'cpf_cnpj')
				cpf = None if cpf < 0 else cpf
				
				recibo = arruma_campo(despesa, 'recibo')
				recibo = None if recibo < 0 else recibo
				
				no_documento = arruma_campo(despesa, 'no_documento')
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

try:
	# TODO discursos
	"""
	print 'Salvando apreciacoes...'
	salva_apreciacoes(conexao)
	
	print 'Salvando partidos...'
	bancada_partido, bancada_bloco = salva_partidos(conexao)
	
	print 'Salvando deputados...'
	salva_deputados(conexao)
	
	print 'Salvando autores de proposicoes...'
	salva_autores_proposicoes(conexao)
	
	print 'Salvando orgaos...'
	salva_orgaos(conexao)
	
	print 'Salvando proposicões...'
	salva_proposicoes(conexao)
	
	print 'Salvando dados de topicos de proposicoes...'
	ultimo_topico = salva_proposicoes_topicos(conexao)
	
	print 'Salvando detalhes de deputados...'
	salva_deputados_extra(conexao, bancada_partido, bancada_bloco)
	
	print 'Salvando dados das eleicoes...'
	salva_dados_eleicoes(conexao)
	"""
	#conexao.rollback()
	conexao.commit()
except:
	conexao.rollback()
	raise

conexao.close()

print 'Finalizado!'

