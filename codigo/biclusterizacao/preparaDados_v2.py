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
import cPickle
import datetime

with open('proposicoes.pkl', 'rb') as prop:
    proposicoes = cPickle.load(prop)

deputados = set()
props = set()
dados = dict()
print('Comecando a computar o dicionario dados\n')
for a in proposicoes.keys():
    proposicao = proposicoes[a]
    votacoes = proposicao['votacoes']
    i_vota = 0
    for votacao in votacoes:
        if votacao['data'] < datetime.datetime(2007, 1, 1):
            continue
        votos = votacao['votos']
        chave = str(a) + '\t' + str(i_vota)
        props.add(chave)
        for deputado in votos.keys():
            deputados.add(deputado)
            if deputado == None:
                print('ta aqueeee')
                raw_input('Press Enter to continue')
            voto = votos[deputado]
            valor = 0; #ART. 17, OBSTRUCAO, NAO, SIM, ABSTENCAO
            if (voto['voto'] == 'SIM'):
                valor = 1
            elif (voto['voto'] == 'ABSTENCAO' or voto['voto'] == 'ART. 17'):
                valor = 0.5
            dados[(deputado, chave)] = valor
        i_vota = i_vota + 1
print(len(deputados))
print(len(props))

data = open ('dados_v2.txt' , 'w')
lbl_deputados = open ('label_deputados_v2.txt' , 'w')
lbl_proposicoes = open ('label_proposicoes_v2.txt' , 'w')
texto = []
lbl_dep = []
lbl_prop = []

for i in props:
    lbl_prop.append(str(i) + '\n')
for i in deputados:
    lbl_dep.append(str(i) + '\n')
    for prop in props:
        texto.append(str(dados[(i,prop)]) if ((i, prop) in dados) else '0.5')
        texto.append('\t')
    texto.append('\n')

data.writelines(texto)
data.close()

lbl_deputados.writelines(lbl_dep)
lbl_deputados.close()

lbl_proposicoes.writelines(lbl_prop)
lbl_proposicoes.close()
