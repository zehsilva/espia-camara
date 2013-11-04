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
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm as cm
import pylab as pl
import os
import cPickle

#from sklearn.cluster.bicluster import SpectralBiclustering
from sklearn.cluster.bicluster import SpectralCoclustering

os.mkdir('solution')

#n_clusters = (3, 2)
n_clusters = 20

arq = open('dados_v2.txt')
dados = np.array([map(float, a.split('\t')[:-1]) for a in arq.readlines()])

plt.matshow(zip(*dados), cmap=cm.PiYG)
plt.title("Original dataset")
pl.savefig('solution/original.png', bbox_inches=0)

#model = SpectralBiclustering(n_clusters=n_clusters, method='log', random_state=0)
model = SpectralCoclustering(n_clusters=n_clusters, svd_method='arpack', random_state=0)
model.fit(dados)
fit_data = dados[np.argsort(model.row_labels_)]
fit_data = fit_data[:, np.argsort(model.column_labels_)]

plt.matshow(zip(*fit_data), cmap=cm.PiYG)
pl.savefig('solution/biclustered.png', bbox_inches=0)
plt.title("After biclustering; rearranged to show biclusters")
plt.matshow(zip(*np.outer(np.sort(model.row_labels_) + 1, np.sort(model.column_labels_) + 1)),
            cmap=plt.cm.PiYG)
plt.title("Checkerboard structure of rearranged data")
pl.savefig('solution/biclustered and rearranged.png', bbox_inches=0)


#resolvendo as labels
label_deputados = open('label_deputados_v2.txt')
label_proposicoes = open('label_proposicoes_v2.txt')
#montando o dict dos deputados, a chave e o indice [0:n]
depdict = dict()
ind = 0
for line in label_deputados:
	depdict[ind] = line
	ind += 1

proposicoes = dict()
ind = 0
for line in label_proposicoes:
	proposicoes[ind] = line
	ind += 1

with open('deputados.pkl', 'rb') as dep:
    deputados = cPickle.load(dep)
with open('deputados_antigos.pkl', 'rb') as dep:
    deputados_antigos = cPickle.load(dep)

#salvando os biclusters
for i in range(n_clusters):
	indices = model.get_indices(i)
	linhas = map(lambda a: int(depdict[a]), indices[0])
	colunas = [proposicoes[a] for a in indices[1]]
	salva = open('solution/' + str(n_clusters) + 'bics_' + str(i) + '.txt','w')
	conteudo = []#map(lambda a: str(a), linhas);
	for l in linhas:
		if l > 0:
			a = deputados[l]
			nome_parlamentar = a['nome_parlamentar']
			partido = a['partido']
			uf = a['uf']
			#if not(isinstance(nome_parlamentar, str) and isinstance(partido, str) and isinstance(uf, str)) :
			#	print(type(nome_parlamentar), type(partido), type(uf))
			texto = [nome_parlamentar, partido, uf]
		else:
			a = deputados_antigos[l]
			texto = [a['nome_deputado'], a['partido'], a['uf']]
		conteudo.append(texto)
		conteudo.append('\n')
	conteudo.append('\n')
	conteudo += map(lambda a: unicode(a, encoding='utf8'), colunas)
	salva.writelines([str(c) for c in conteudo])
	salva.close()
	print('fechou o arquivo ' + str(i) + '\t' + str(len(linhas)) + '\t' + str(len(colunas)))