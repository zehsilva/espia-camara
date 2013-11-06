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

import orgaos as dados_orgaos
import deputados as dados_deputados
import pdfminer.converter as pdf_converter
import pdfminer.layout as pdf_layout
import pdfminer.pdfinterp as pdf_interp
import pdfminer.pdfparser as pdf_parser
import suds.client as soap
import suds
import datetime
import xml
import re
import cStringIO
import os
import urllib
import HTMLParser
from fontes.geral import *
import time

MAX_PAGINAS_PDF = 50

NAO_REFERENCIAVEIS = ['PAR', 'PRL', 'RIC', 'PPP', 'INC', 'REQ', 'TVR', 'VTS', \
	'RDF', 'CVO', 'MSC', 'DIS']

wsdl_proposicoes_file = "http://www.camara.gov.br/SitCamaraWS/" \
	"Proposicoes.asmx?wsdl"
cliente_proposicoes = soap.Client(wsdl_proposicoes_file)

mensagens_falha = ['Desculpe-nos!', \
	'Por favor tente acessar mais tarde. Ajude-nos a oferecer um melhor', \
	'Envie um e-mail para ceace.cenin@camara.gov.br, contendo:', \
	'sobre o erro, mostradas abaixo (copie e cole no corpo do e-mail): ' \
	'Erro: 503 Tipo:', 'Servidor: www.camara.gov.br']

def mensagem_de_falha(texto):
	for mensagem in mensagens_falha:
		if texto.find(mensagem) == -1:
			return False
	
	return True

def remove_espacos_extras(texto):
	sem_numero_pagina = re.sub(r'\s+Page\s+[0-9]+\s+', ' ', texto, \
		flags=re.IGNORECASE)
	remove_espacos_meio = re.sub(r'\n+', '\n', re.sub(r'[\t\r\ ]+', ' ', \
		re.sub(r'[\t\r\ ]*\n[\t\r\ ]*', '\n', sem_numero_pagina)))
	
	return re.sub(r'(\A\s+|\s+\Z)', '',  remove_espacos_meio)

def converte_msword(nome_arquivo, semaforo=None, profundidade=None, \
	pagina=None):
	
	(arq_entrada, arq_saida, arq_erro) = \
		os.popen3('catdoc -w "%s"' % nome_arquivo)
	
	dados = arq_saida.read()
	erros = arq_erro.read()
	arq_entrada.close()
	arq_saida.close()
	arq_erro.close()
	
	if erros and not (erros.startswith('[This was fast-saved') and \
		erros.endswith('times. Some information is lost]\n')):
		
		return 'msword_erro', None
	
	return 'msword', remove_espacos_extras(dados)

def _converte_html(texto, sep):
	html = HTMLParser.HTMLParser()
	
	try:
		texto_decodificado = texto.decode('utf-8')
	except UnicodeDecodeError:
		try:
			texto_decodificado = texto.decode('iso-8859-1')
		except UnicodeDecodeError:
			texto_decodificado = texto
	
	sem_entidades = html.unescape(texto_decodificado)
	
	try:
		body = re.search(r'\<body(\s+[^\>]*)?\>([^\0]*)\<\/body\>', \
			sem_entidades, flags=re.IGNORECASE).group(0)
	except AttributeError:
		body = sem_entidades
	
	remove_espacos = re.sub(r'\s+', ' ', body)
	adiciona_linhas = re.sub(r'(\<' + sep + '(\ [^\>]+)?\>)', '\n', \
		remove_espacos, flags=re.IGNORECASE)
	sem_style = re.sub(r'\<style(\s+[^\>]*)?\>[^\<]\<\/style\>', '', \
		adiciona_linhas, flags=re.IGNORECASE)
	sem_script = re.sub(r'\<script(\s+[^\>]*)?\>[^\<]\<\/script\>', '', \
		sem_style, flags=re.IGNORECASE)
	remove_tags = re.sub(r'\<[^\>]+\>', '', sem_script)
	
	return remove_espacos_extras(remove_tags)

def converte_html(nome_arquivo, sep='(br|p)', semaforo=None, profundidade=0, \
	pagina=None):
	
	texto_aux = ''.join(open(nome_arquivo, 'r').readlines())
	
	try:
		url_redirec = re.search(r'\<meta\s+http\-equiv\=\"refresh\"\s+content' \
			'\=\"[0-9]+\s*\;\s*URL\=([^\"]*)\"\s*\/\>', texto_aux, \
			re.IGNORECASE).group(1)
		
		return _get_teor(url_redirec, semaforo=semaforo, \
			profundidade=profundidade + 1)
	except (AttributeError, IndexError):
		if re.search('\<APPLET\ CODEBASE\ \=\ ' \
			'\"http\:\/\/imagem\.camara\.gov\.br\/ViewOne\/v1files\"', \
			texto_aux) != None:
			return 'applet', None
		
		resultado = _converte_html(texto_aux, sep)
		
		if mensagem_de_falha(resultado):
			raise Exception('Erro 503: Falha do servidor!')
		
		return 'html', resultado

def converte_pdf(nome_arquivo, semaforo=None, profundidade=None, pagina=None):
	parametros = pdf_layout.LAParams(word_margin=100)
	gerenciador = pdf_interp.PDFResourceManager()
	str_saida = cStringIO.StringIO()
	
	arquivo_pdf = file(nome_arquivo, 'rb')
	
	dispositivo = pdf_converter.HTMLConverter(gerenciador, str_saida, \
		codec='utf-8', laparams=parametros)
	interpretador = pdf_interp.PDFPageInterpreter(gerenciador, dispositivo)
	
	if pagina == None:
		tipo_aux = 'pdf'
		pg_inicio, pg_fim = 0, -1
	else:
		tipo_aux = 'pdf_parte'
		pg_inicio, pg_fim = pagina - 1, pagina + 1
	
	tipo = tipo_aux
	
	try:
		parser = pdf_parser.PDFParser(arquivo_pdf)
		documento = pdf_parser.PDFDocument()
		parser.set_document(documento)
		documento.set_parser(parser)
		
		paginas = [p for p in documento.get_pages()]
		
		if len(paginas) > MAX_PAGINAS_PDF:
			return 'pdf_longo', None
		
		for pagina_atual in paginas[pg_inicio:pg_fim]:
			try:
				interpretador.process_page(pagina_atual)
			except Exception:
				tipo = tipo_aux + '_defeito'
		
		dados_html = str_saida.getvalue()
	except (AssertionError, pdf_parser.PDFSyntaxError):
		return tipo, None
	finally:
		arquivo_pdf.close()
		dispositivo.close()
		str_saida.close()
	
	removido_tags = _converte_html(dados_html, 'div')
	removido_espacos_desnecessarios = re.sub("\ +ç", "ç", removido_tags, \
		flags=re.IGNORECASE)
	sem_numero_pagina = re.sub("\nPage\ [0-9]+\ *\n[0-9]+\ *\n", "\n", \
		removido_espacos_desnecessarios)
	texto_final = re.sub('(\ *\n)+', '\n', re.sub('[\ \t]+', r' ', \
		sem_numero_pagina))
	
	return tipo, texto_final

conversor_tipo = { \
	'pdf': converte_pdf, \
	'msword': converte_msword, \
	'html': converte_html}

def _get_teor(link_teor, semaforo=None, profundidade=0, segundos_espera=0):
	if link_teor == '':
		return None, None
	
	if profundidade >= 3:
		return 'html_redirec', None
	
	try:
		partes_endereco = link_teor.split('#')
		pagina = int(partes_endereco[1].split('=')[1])
		
		# Ignora PDFs com múltiplas proposições
		if partes_endereco[0].endswith('.pdf'):
			return link_teor, 'pdf_parte', None
	except IndexError:
		pagina = None
	
	if semaforo != None:
		semaforo.acquire()
	
	time.sleep(segundos_espera)
	
	try:
		arquivo_nome, dados = urllib.urlretrieve(link_teor)
	except IOError:
		return link_teor, 'nao_encontrado', None
	finally:
		if semaforo != None:
			semaforo.release()
	
	dados = conversor_tipo[dados.getsubtype()](arquivo_nome, \
		semaforo=semaforo, profundidade=profundidade, pagina=pagina)
	
	if len(dados) <= 2:
		return (link_teor,) + dados
	
	return dados
	
def get_teores(inteiros_teores, proposicoes_chaves, proposicoes, aux_map=map):
	proposicoes_chaves_aux = filter(lambda a: proposicoes[a]['link_teor'] != \
		None and proposicoes[a]['link_teor'] != '', proposicoes_chaves)
	
	teores = aux_map(_get_teor, map(lambda a: proposicoes[a]['link_teor'], \
		proposicoes_chaves_aux))

	for i in proposicoes_chaves:
		inteiros_teores[i] = None
	
	for i in range(len(proposicoes_chaves_aux)):
		if teores[i] == None:
			continue
		
		inteiros_teores[proposicoes_chaves_aux[i]] = { \
			'link': teores[i][0], \
			'tipo_origem': teores[i][1], \
			'texto': teores[i][2]}

def get_metadados():
	tipos = cliente_proposicoes.service.ListarSiglasTipoProposicao()
	
	dict_tipos = {}
	
	for tipo in tipos.siglas.sigla:
		dict_tipos[normaliza(tipo._tipoSigla)] = { \
			"descricao": tipo._descricao.encode("utf-8"), \
			"ativa": bool(tipo._ativa), \
			"genero": tipo._genero.upper()}
	
	situacoes = cliente_proposicoes.service.ListarSituacoesProposicao()
	
	dict_situacoes = {}
	
	for situacao in situacoes.situacaoProposicao.situacaoProposicao:
		dict_situacoes[int(situacao._id)] = { \
			"descricao": situacao._descricao.encode("utf-8"), \
			"ativa": bool(situacao._ativa)}
	
	autores = cliente_proposicoes.service.ListarTiposAutores()
	
	dict_autores = {}
	
	for autor in autores.siglas.TipoAutor:
		dict_autores[autor._id] = { \
			"descricao": autor._descricao.title().encode("utf-8")}
	
	return dict_tipos, dict_situacoes, dict_autores

def nova_proposicao(proposicao, dados_proposicao, regimes, regimes_por_nome, \
	apreciacoes, apreciacoes_por_nome, orgaos, orgaos_por_id, deputados, \
	deputados_por_nome, deputados_antigos, deputados_antigos_por_nome, \
	partidos_por_sigla, outros_autores, outros_autores_por_nome):
	
	data_apresentacao = formata_data(proposicao.datApresentacao)
	
	try:
		id_regime = int(proposicao.regime.codRegime)
	except ValueError:
		id_regime = None
	
	nome_regime = uniformiza(proposicao.regime.txtRegime)

	if id_regime in regimes:
		if regimes[id_regime]["nome"] != nome_regime:
			raise Exception("Regimes com mesmo id mas nomes diferentes!")
	elif id_regime != None:
		regimes[id_regime] = {"nome": nome_regime}
		regimes_por_nome[nome_regime] = id_regime
	
	try:
		id_apreciacao = int(proposicao.apreciacao.id)
	except ValueError:
		id_apreciacao = None
	
	nome_apreciacao = uniformiza(proposicao.apreciacao.txtApreciacao)

	if id_apreciacao in apreciacoes:
		if apreciacoes[id_apreciacao]["nome"] != nome_apreciacao:
			raise Exception("Apreciações com mesmo id mas nomes " \
				"diferentes!")
	elif id_apreciacao != None:
		apreciacoes[id_apreciacao] = {"nome": nome_apreciacao}
		apreciacoes_por_nome[nome_apreciacao] = id_apreciacao

	try:
		id_autor1 = dados_deputados.obtem_deputado_por_id( \
			int(proposicao.autor1.idecadastro), \
			uniformiza(proposicao.autor1.txtNomeAutor), \
			uniformiza(proposicao.autor1.txtSiglaPartido), \
			uniformiza(proposicao.autor1.txtSiglaUF), \
			deputados, deputados_por_nome, deputados_antigos, \
			deputados_antigos_por_nome, partidos_por_sigla)
		autor_deputado = True
	except ValueError:
		nome_autor1 = normaliza(proposicao.autor1.txtNomeAutor)
	
		try:
			id_autor1 = outros_autores_por_nome[nome_autor1]
		except KeyError:
			id_autor1 = - (len(outros_autores) + 1)
			outros_autores[id_autor1] = {"nome": nome_autor1}
			outros_autores_por_nome[nome_autor1] = id_autor1
		
		autor_deputado = False

	orgao_num_sigla = uniformiza(proposicao.orgaoNumerador.sigla)
	dados_orgaos.adiciona_orgao(orgaos, orgaos_por_id, orgao_num_sigla, \
		proposicao.orgaoNumerador.id, proposicao.orgaoNumerador.nome)

	nova_proposicao = { \
		"nome": proposicao.nome.encode("utf-8"), \
		"tipo": normaliza(proposicao.tipoProposicao.sigla),
		"numero": int(proposicao.numero), \
		"ano": int(proposicao.ano), \
		"orgao_num": orgao_num_sigla, \
		"data_apresentacao": data_apresentacao, \
		"ementa": proposicao.txtEmenta.encode("utf-8"), \
		"explicacao_ementa": proposicao.txtExplicacaoEmenta.encode("utf-8"), \
		"regime": id_regime, \
		"apreciacao": id_apreciacao, \
		"qtd_autores": int(proposicao.qtdAutores), \
		"autor1": id_autor1, \
		"autor1_deputado": autor_deputado, \
		"proposicao_principal": int(proposicao.situacao.principal. \
			codProposicaoPrincipal), \
		"votacoes": []}

	data_ultimo_despacho = formata_data(proposicao.ultimoDespacho.datDespacho)

	if data_ultimo_despacho != None:
		nova_proposicao["despacho"] = { \
			"data": data_ultimo_despacho, \
			"texto": proposicao.ultimoDespacho.txtDespacho.encode("utf-8")}

	if int(proposicao.qtdOrgaosComEstado) > 0:
		orgao_estado = uniformiza(proposicao.situacao.orgao.codOrgaoEstado)
		dados_orgaos.adiciona_orgao(orgaos, orgaos_por_id, orgao_estado)

		nova_proposicao["situacao"] = int(proposicao.situacao.id)
		nova_proposicao["orgao_estado"] = orgao_estado
	
	if dados_proposicao == None:
		nova_proposicao['indices'] = None
		nova_proposicao['link_teor'] = None
	else:
		indices = map(lambda a: a.strip(), uniformiza(dados_proposicao. \
			proposicao.Indexacao).split(","))
		
		nova_proposicao['indices'] = indices if indices != [''] else []
		nova_proposicao['link_teor'] = dados_proposicao.proposicao. \
			LinkInteiroTeor.encode("utf-8")
	
	return nova_proposicao

def _obtem_proposicao_por_id(cod_proposicao):
	try:
		return cliente_proposicoes.service.ObterProposicaoPorID(cod_proposicao)
	except xml.sax._exceptions.SAXParseException:
		return None

def get_proposicoes_tipo_ano(tipo_proposicoes, ano, dict_proposicoes, \
	proposicoes_por_nome, regimes, regimes_por_nome, apreciacoes, \
	apreciacoes_por_nome, orgaos, orgaos_por_id, deputados, \
	deputados_por_nome, deputados_antigos, deputados_antigos_por_nome, \
	partidos_por_sigla, outros_autores, outros_autores_por_nome, aux_map=map):
	
	data_inicio = datetime.date(ano, 1, 1).strftime("%d/%m/%Y")
	data_final = datetime.date(ano, 12, 31).strftime("%d/%m/%Y")
	
	try:
		# Aproveita de um defeito do web service da Câmara e realiza a busca por
		# data e não por ano (ao usar ano=0, a busca ignora o ano e segue apenas
		# pelos outros critérios). Esse formato permite buscar as proposições
		# que estão com o ano=0 por alguma razão.
		proposicoes = cliente_proposicoes.service.ListarProposicoes( \
			tipo_proposicoes, "", 0, data_inicio, data_final)
	except suds.WebFault:
		return

	lista_proposicoes = certifica_lista(proposicoes.proposicoes, "proposicao")
	
	dados_proposicoes = aux_map(_obtem_proposicao_por_id, \
		aux_map(lambda proposicao: int(proposicao.id), lista_proposicoes))
	
	for i in range(len(lista_proposicoes)):
		proposicao = lista_proposicoes[i]
		dados_proposicao = dados_proposicoes[i]
		cod_proposicao = int(proposicao.id)
		dict_proposicoes[cod_proposicao] = nova_proposicao(proposicao, \
			dados_proposicao, regimes, regimes_por_nome, apreciacoes, \
			apreciacoes_por_nome, orgaos, orgaos_por_id, deputados, \
			deputados_por_nome, deputados_antigos, deputados_antigos_por_nome, \
			partidos_por_sigla, outros_autores, outros_autores_por_nome)
		proposicoes_por_nome[dict_proposicoes[cod_proposicao]['nome']] = \
			cod_proposicao

def _busca_bancada(nome_bancada, data, blocos, blocos_por_sigla, \
	partidos_por_sigla):
	
	if nome_bancada[:5] == "Repr.":
		nome_bancada = nome_bancada[5:]
	
	try:
		return 'P', partidos_por_sigla[uniformiza(nome_bancada)]
	except KeyError:
		pass
	
	try:
		return 'B', blocos_por_sigla[uniformiza(nome_bancada)]
	except KeyError:
		pass
	
	partidos_aux = nome_bancada.split("/")
	
	if len(partidos_aux) > 1:
		partidos = map(lambda a: uniformiza(a), partidos_aux)
	else:
		partidos_aux = re.split(r'([A-Z]+doB)', nome_bancada)
		partidos = []
		
		for i in range(len(partidos_aux)):
			if i % 2 == 1:
				partidos.append(uniformiza(partidos_aux[i]))
			else:
				partidos += filter(lambda a: a != '' and a[0] != '.', \
					map(lambda a: uniformiza(a), re.split(r'([A-Z][a-z]+)', \
					partidos_aux[i])))
	
	for k in blocos.keys():
		dados_bloco = blocos[k]
		
		if dados_bloco['partidos'] == None:
			continue
		
		bloco_data = filter(lambda a: a['data_adesao'].date() <= data.date() \
			and	(a['data_desligamento'] == None or \
			a['data_desligamento'].date() >= data.date()), \
			dados_bloco['partidos'])
		bloco_data = map(lambda a: normaliza(a['partido']), bloco_data)
		
		if set(partidos).issubset(set(bloco_data)):
			return 'B', k
	
	return 'B', None

def get_votacao_proposicao(proposicao, deputados, deputados_por_nome, \
	deputados_antigos, deputados_antigos_por_nome, partidos_por_sigla, blocos, \
	blocos_por_sigla, votacao_proposicao=None):
	
	if votacao_proposicao == None:
		try:
			votacao_proposicao = cliente_proposicoes.service. \
				ObterVotacaoProposicao(proposicao['tipo'], \
				proposicao['numero'], proposicao['ano'])
		except suds.WebFault as e:
			return # Não há dados para essa votação.
	
	lista_votacoes = certifica_lista(votacao_proposicao.proposicao.Votacoes, \
		"Votacao")
	
	for votacao in lista_votacoes:
		data_votacao = formata_data(votacao._Data + " " + votacao._Hora + ":00")
		
		proposicao["votacoes"].append({ \
			"resumo": votacao._Resumo.encode("utf-8"), \
			"data": data_votacao, \
			"orientacao_bancada": {"partidos": {}, "blocos": {}}, \
			"votos": {}})
		
		try:
			lista_orientacao = certifica_lista(votacao.orientacaoBancada, \
				"bancada")
		except AttributeError:
			lista_orientacao = []
		
		dados_orientacao = proposicao["votacoes"][-1]["orientacao_bancada"]
		
		for orientacao_bancada in lista_orientacao:
			tipo, id_bancada = _busca_bancada( \
				orientacao_bancada._Sigla.strip(), data_votacao, blocos, \
				blocos_por_sigla, partidos_por_sigla)
			
			if tipo == 'P':
				dados_orientacao["partidos"][id_bancada] = \
					normaliza(orientacao_bancada._orientacao)
			elif tipo == 'B':
				if id_bancada == None:
					dados_orientacao["blocos"][orientacao_bancada._Sigla. \
						strip()] = normaliza(orientacao_bancada._orientacao)
				else:
					dados_orientacao["blocos"][id_bancada] = \
						normaliza(orientacao_bancada._orientacao)
		
		try:
			lista_votos = certifica_lista(votacao.votos, "Deputado")
		except AttributeError:
			lista_votos = []
		
		dados_voto = proposicao["votacoes"][-1]["votos"]
		votos_favor = 0
		votos_contra = 0
		
		for voto_deputado in lista_votos:
			voto = normaliza(voto_deputado._Voto)
			
			if voto == "SIM":
				votos_favor += 1
			elif voto == "NAO":
				votos_contra += 1
			
			id_deputado = dados_deputados.obtem_deputado_por_id( \
				int(voto_deputado._ideCadastro), \
				uniformiza(voto_deputado._Nome), \
				uniformiza(voto_deputado._Partido), \
				uniformiza(voto_deputado._UF), deputados, deputados_por_nome, \
				deputados_antigos, deputados_antigos_por_nome, \
				partidos_por_sigla)
			
			if id_deputado == None:
				continue
			
			dados_voto[id_deputado] = { \
				"partido": partidos_por_sigla[ \
					uniformiza(voto_deputado._Partido)], \
				"voto": voto}
		
		proposicao["votacoes"][-1]["votos_favor"] = votos_favor
		proposicao["votacoes"][-1]["votos_contra"] = votos_contra

def get_proposicao_por_id(cod_proposicao, proposicoes, proposicoes_por_nome, \
	regimes, regimes_por_nome, apreciacoes, apreciacoes_por_nome, blocos, \
	blocos_por_sigla, orgaos, orgaos_por_id, deputados, deputados_por_nome, \
	deputados_antigos, deputados_antigos_por_nome, partidos_por_sigla, \
	outros_autores, outros_autores_por_nome):
	
	try:
		dados_proposicao = cliente_proposicoes.service. \
			ObterProposicaoPorID(cod_proposicao)
	except xml.sax._exceptions.SAXParseException:
		return None
	
	try:
		proposicoes_aux = cliente_proposicoes.service.ListarProposicoes( \
			normaliza(dados_proposicao.proposicao._tipo), \
			int(dados_proposicao.proposicao._numero), \
			int(dados_proposicao.proposicao._ano))
	except suds.WebFault:
		return None
	
	lista_proposicoes = certifica_lista(proposicoes_aux.proposicoes, \
		'proposicao')
	
	for proposicao in lista_proposicoes:
		if int(proposicao.id) == cod_proposicao:
			proposicao_aux = nova_proposicao(proposicao, dados_proposicao, \
				regimes, regimes_por_nome, apreciacoes, apreciacoes_por_nome, \
				orgaos, orgaos_por_id, deputados, deputados_por_nome, \
				deputados_antigos, deputados_antigos_por_nome, \
				partidos_por_sigla, outros_autores, outros_autores_por_nome)
	
			proposicoes[cod_proposicao] = proposicao_aux
			proposicoes_por_nome[proposicao_aux['nome']] = cod_proposicao
			
			return
	
	raise Exception('Proposição %s não encontrada!' % cod_proposicao)

def get_proposicao_por_nome(nome, dict_proposicoes, proposicoes_por_nome, \
	regimes, regimes_por_nome, apreciacoes, apreciacoes_por_nome, orgaos, \
	orgaos_por_id, deputados, deputados_por_nome, deputados_antigos, \
	deputados_antigos_por_nome, partidos_por_sigla, outros_autores, \
	outros_autores_por_nome):
	
	partes_nome = re.split(r'[\ \/]', nome)
	
	try:
		proposicoes = cliente_proposicoes.service.ListarProposicoes( \
			partes_nome[0], partes_nome[1], partes_nome[2])
	except suds.WebFault:
		return

	lista_proposicoes = certifica_lista(proposicoes.proposicoes, "proposicao")
	
	for proposicao in lista_proposicoes:
		if normaliza(proposicao.nome) == normaliza(nome):
			dados_proposicao = _obtem_proposicao_por_id(proposicao.id)
			cod_proposicao = int(proposicao.id)
			dict_proposicoes[cod_proposicao] = nova_proposicao(proposicao, \
				dados_proposicao, regimes, regimes_por_nome, apreciacoes, \
				apreciacoes_por_nome, orgaos, orgaos_por_id, deputados, \
				deputados_por_nome, deputados_antigos, \
				deputados_antigos_por_nome, partidos_por_sigla, \
				outros_autores, outros_autores_por_nome)
			proposicoes_por_nome[nome] = cod_proposicao
			return
	
	raise Exception('Proposição %s não encontrada!' % nome)

def _get_dados_votacoes(proposicao):
	try:
		return cliente_proposicoes.service. \
			ObterVotacaoProposicao(proposicao['tipo'], \
			proposicao['numero'], proposicao['ano'])
	except suds.WebFault as e:
		return None # Não há dados para essa votação.

def get_votacoes(ano, proposicoes, proposicoes_por_nome, regimes_proposicoes, \
	regimes_proposicoes_por_nome, apreciacoes_proposicoes, \
	apreciacoes_proposicoes_por_nome, deputados, deputados_por_nome, \
	partidos_por_sigla, blocos, blocos_por_sigla, orgaos, orgaos_por_id, \
	outros_autores, outros_autores_por_nome, \
	deputados_antigos, deputados_antigos_por_nome, aux_map=map):
	
	lista_votadas = []
	proposicoes_antigas = []
	proposicoes_obtidas = []
	
	proposicoes_votadas = cliente_proposicoes.service. \
		ListarProposicoesVotadasEmPlenario(ano)
		
	for proposicao in proposicoes_votadas.proposicoes.proposicao:
		cod_proposicao = int(proposicao.codProposicao)
		lista_votadas.append(cod_proposicao)
		
		try:
			proposicoes_obtidas.append(proposicoes[cod_proposicao])
		except KeyError:
			proposicoes_antigas.append(cod_proposicao)
	
	# Obtendo proposições antigas
	for cod_proposicao in proposicoes_antigas:
		get_proposicao_por_id(cod_proposicao, proposicoes, \
			proposicoes_por_nome, regimes_proposicoes, \
			regimes_proposicoes_por_nome, apreciacoes_proposicoes, \
			apreciacoes_proposicoes_por_nome, blocos, blocos_por_sigla, \
			orgaos, orgaos_por_id, deputados, deputados_por_nome, \
			deputados_antigos, deputados_antigos_por_nome, partidos_por_sigla, \
			outros_autores, outros_autores_por_nome)
		proposicoes_obtidas.append(proposicoes[cod_proposicao])
	
	dados_votacoes = aux_map(_get_dados_votacoes, proposicoes_obtidas)
	
	for i in range(len(proposicoes_obtidas)):
		if dados_votacoes[i] == None:
			continue
		
		get_votacao_proposicao(proposicoes_obtidas[i], deputados, \
			deputados_por_nome, deputados_antigos, deputados_antigos_por_nome, \
			partidos_por_sigla, blocos, blocos_por_sigla, \
			votacao_proposicao=dados_votacoes[i])
	
	return lista_votadas

