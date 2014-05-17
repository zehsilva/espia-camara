import dbscripts as db
import pickle as pk

def inserttopicsdiscursos(db):
	dists=pk.load(open('discursos/topics-distribution-lda-discursos-nostemming-sample30-100topics.pk'))
	dists=[x*1.0/max(dists) for x in dists]
	insertiondata = zip([x+300 for x in range(len(dists))],dists,['D']*300)
	colnames = ['id_topico','peso','tipo']
	tablename='ml_topicos'
	db.insertList(db.dbconn,colnames,insertiondata,tablename)

def inserttopicsdiscursospalavras(db):
	nomes=pk.load(open('discursos/topic-words-ordered-discursos-complete-nostemm-sample30-100topics.pkl'))
	data = sum([ [ (i+300,x[0],x[1]) for x in nomes[i] ] for i in range(len(nomes)) ]  , [] )
	colnames = ['id_topico','peso','palavra']
	tablename='ml_topicos_palavras'
	db.insertList(db.dbconn,colnames,data,tablename)

def insertassociationtopicdiscurso(db):
	data=pk.load(open('discursos/topics-associative-tuple-lda-discursos-nostemming-sample30-100topics.pk'))
	colnames = ['id_discurso','id_topico','peso']
	tablename='ml_discursos_topicos'
	db.insertList(db.dbconn,colnames,data,tablename)

insertassociationtopicdiscurso(db)
#inserttopicsdiscursos(db)
#inserttopicsdiscursospalavras(db)
