#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
fp=open("conn.txt")
dbname=fp.readline()
dbuser=fp.readline()
dbpass=fp.readline()
dbconn=mdb.connect(db=dbname,host='127.0.0.1',user=dbuser,passwd=dbpass,port=2306)

def testConn(dbconn):
	with dbconn:
		cur = dbconn.cursor()
		cur.execute("select t.id_topico, t.peso, tp.palavra from (select tp.id_topico, group_concat(tp.palavra) as palavra from ml_topicos_palavras as tp group by tp.id_topico) as tp, ml_topicos as t where tp.id_topico = t.id_topico order by  t.peso desc")
		rows=cur.fetchall()
		desc = cur.description
		
		for descol in desc[:][0]:
			print descol,
		print
		
		for row in rows:
			for rowi in row:
				print rowi,
			print

def updateList(listid,listvalue,idname,colname,tablename,dbconn):
	with dbconn:
		cur = dbconn.cursor()
		try:
			for (idval,colval) in zip(listid,listvalue):
				cur.execute (""" UPDATE $s SET $s=%s WHERE %s=%s """, (tablename, colname, colval, idname , idval ) )
			cur.commit()
		except:
			cur.rollback()

def insertList(dbconn,listcolname,listvalue,tablename):
	with dbconn:
		cur = dbconn.cursor()
		try:
			colnames = ",".join(listcolname)
			for vals in listvalue:
				try:
					values=",".join(["'"+str(x)+"'" for x in vals])
					querystr= "INSERT INTO "+tablename+"("+colnames+") VALUES ("+values+")"
					print querystr
					cur.execute(querystr)
					dbconn.commit()
				except:
					print 'erro'
					dbconn.rollback()
			
		except:
			print 'erro grande'
 
#testConn(dbconn)
