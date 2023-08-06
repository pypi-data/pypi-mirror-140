#!/usr/bin/env python -W ignore::DeprecationWarning 
# 2022.2.17, upgrade of sntbs, spacy 3.1.1-based, one single file
import sqlite3,json,collections, fire, traceback,sys
from collections import	UserDict,Counter,defaultdict
from tqdm import tqdm

from en import * #import en # need 3.1.1
from en import terms,verbnet
attach = lambda doc: ( terms.attach(doc), verbnet.attach(doc), doc.user_data )[-1]  # return ssv, defaultdict(dict)

class Spacybs(UserDict): # change to a neutral name, such as Dbdict ?  then Docbs(Dbdict),   add compress later ? 2021-2-3
	def	__init__(self, filename, tablename='spacybs'): 
		self.filename =	filename
		self.tablename = tablename
		self.conn =	sqlite3.connect(self.filename, check_same_thread=False) 
		self.conn.execute(f'CREATE TABLE IF NOT EXISTS {self.tablename} (key varchar(512) PRIMARY KEY, value blob)')
		self.conn.execute('PRAGMA synchronous=OFF')
		self.conn.commit()

	def	__str__(self): 	return "SqliteDict(%s)"	% (self.filename)
	def	__repr__(self): return str(self)  #	no need	of something complex
	def	__len__(self):	return self.conn.execute('SELECT COUNT(*) FROM	"%s"' %	self.tablename).fetchone()[0]
	def	count(self):	return self.conn.execute('SELECT count(*) FROM "%s"'% self.tablename).fetchone()[0]

	def	keys(self, start=0, len=-1):  
		for key in self.conn.execute(f'SELECT key FROM {self.tablename} ORDER BY rowid limit {start},{len}' ).fetchall(): yield key[0]
	def	values(self, start=0, len=-1): 
		for	value in self.conn.execute(f'SELECT value FROM {self.tablename} ORDER BY rowid  limit {start},{len}').fetchall(): yield value[0]
	def	items(self, start=0, len=-1): 
		for rowid, key, value in self.conn.execute(f'SELECT rowid, key, value FROM	{self.tablename} ORDER BY rowid limit {start},{len}' ).fetchall(): 	yield rowid, key, value
	def	docs(self, start=0, len=-1): 
		for	value in self.conn.execute(f'SELECT value FROM {self.tablename} ORDER BY rowid  limit {start},{len}').fetchall(): yield from_docbin(value[0])

	def	__contains__(self, key): return self.conn.execute('SELECT 1 FROM "%s" WHERE key = ?' %	self.tablename, (key,)).fetchone() is not None

	def	__getitem__(self, key):
		item = self.conn.execute(f'SELECT value FROM "{self.tablename}" WHERE key = ? limit 1', (key,)).fetchone()
		return None if item	is None else item[0] # else json.loads(...)
	def get(self, key): return self[key]

	def	__setitem__(self, key, value): 	self.conn.execute('REPLACE	INTO "%s" (key,	value) VALUES (?,?)' % self.tablename,	(key, value))
	def set(self, key, value): self[key] = value
	def	__delitem__(self, key): self.conn.execute('DELETE FROM	"%s" WHERE key = ?'	% self.tablename,	(key,))
	def	__iter__(self): 		return self.keys()
	def	close(self): 	self.conn.commit()

class util(object):

	def train(self, sntfile, dbfile=None): 
		''' train clec.snt => clec.sntbs, 2021.8.1 '''
		if not dbfile : dbfile = sntfile.split(".")[0].lower() + ".spacybs"
		print("started:", sntfile, dbfile,flush=True)
		db = Spacybs(dbfile)
		for line in tqdm(open(sntfile,'r').readlines()):
			try:
				snt = line.strip()
				if snt and not snt in db: 
					db[snt] = tobs(nlp(snt))
			except Exception as e:
				print ("parse ex:", e, line)
		db.close()
		print("finished:", sntfile, dbfile)

	def topika(self,dbfile, name=None, host='127.0.0.1', port=9311, db_bs=0, db_dm=5):  
		''' clec.spacybs -> :  snt:clec(list) , {snt}:bs(hash),  2022.1.20 '''
		import redis
		rdm = redis.Redis(host=host, port=port, db=db_dm, decode_responses=True)
		rbs = redis.Redis(host=host, port=port, db=db_bs)
		if not name: name = dbfile.split('.')[0].lower()
		rdm.delete(f"snts:{name}")
		for rowid, snt, bs in tqdm(Spacybs(dbfile).items()) :
			try:
				doc = frombs(bs)
				rdm.rpush(f"snts:{name}", snt ) 
				rbs.setnx(snt, tobs(doc))
			except Exception as e:
				print ("ex:", e, rowid, snt)
		print (f"[tobs] finished, {dbfile}, {name}")

	def idsource(self,dbfile, outfile=None ):  
		''' clec.spacybs -> clec.idsource , 2022.2.11
			{"_id": "140948871-9", "_source": {"rid": "10", "uid": "25110374", "sc": 14, "md5": "da891a7d81f7a5e43b571168cc483b6c dba0b4c99ef37cadfc4bacd61fcefa5b d6b199bfae35246564c598ac78d84c91 38a945eeff5b5a587a26dcc6560e0061 58605af6b50b01f15c0cc3ee2aa75e33 c30566c355ae09ea68673e2940d49d0a 7972c906aef51380310363093e141ef8 dabdd545400415da6d29125bf872"}}
			Then submit:  es.py idsource  clec.idsource
		'''
		if not outfile: outfile = dbfile.split(".")[0] + ".idsource"
		with open(outfile, 'w') as fw:
			for rowid, snt, bs in tqdm(Spacybs(dbfile).items()) :
				try:
					doc = frombs(bs) 
					ssv = attach(doc) 
					for id, source in ssv.items():
						source.update({"src": rowid})
						fw.write(json.dumps({"_id": f"{rowid}-{id}", "_source":source}) + "\n") 
				except Exception as ex:
					print(">>idsource ex:", ex,"\t|", rowid, snt)
		print("submit idsource finished:", dbfile, outfile)

	def toes(self,dbfile, idxname=None, eshost='127.0.0.1', esport=9200, batch=100000 , refresh=True):  
		''' clec.spacybs -> es/clec directly, 2022.2.15
			{"_id": "140948871-9", "_source": {"rid": "10", "uid": "25110374", "sc": 14, "md5": "da891a7d81f7a5e43b571168cc483b6c dba0b4c99ef37cadfc4bacd61fcefa5b d6b199bfae35246564c598ac78d84c91 38a945eeff5b5a587a26dcc6560e0061 58605af6b50b01f15c0cc3ee2aa75e33 c30566c355ae09ea68673e2940d49d0a 7972c906aef51380310363093e141ef8 dabdd545400415da6d29125bf872"}}
		'''
		from elasticsearch import Elasticsearch,helpers
		from so import config
		es	= Elasticsearch([ f"http://{eshost}:{esport}" ])  
		if not idxname : idxname = dbfile.split('.')[0].lower()
		if refresh and es.indices.exists(idxname): es.indices.delete(idxname)
		if not es.indices.exists(idxname): es.indices.create(idxname, config) 
		print ("toes started:", dbfile, idxname, es, flush=True)
		actions=[]
		for rowid, snt, bs in tqdm(Spacybs(dbfile).items()) :
			try:
				doc = frombs(bs) 
				actions.append({'_op_type':'index', '_index':idxname, '_id': rowid, '_source':{'type':'snt', 'snt':snt,
				'postag':'^ ' + ' '.join([f"{t.text}_{t.lemma_}_{t.pos_}_{t.tag_}" if t.text == t.text.lower() else f"{t.text}_{t.text.lower()}_{t.lemma_}_{t.pos_}_{t.tag_}" for t in doc]) + ' $',
				'src': rowid,  'tc': len(doc)}}) #'sid': rowid,
				ssv = attach(doc) 
				for id, source in ssv.items():
					source.update({"src":rowid}) # sid doesnot work  "sid": rowid, 
					actions.append({'_op_type':'index', '_index':idxname, '_id': f"{rowid}-{id}", '_source':source})
				if len(actions) > batch : 
					helpers.bulk(client=es,actions=actions, raise_on_error=False)
					actions = []
					print (rowid, snt , flush=True) 
			except Exception as ex:
				print(">>toes ex:", ex,"\t|", rowid, snt)
				exc_type, exc_value, exc_traceback_obj = sys.exc_info()
				traceback.print_tb(exc_traceback_obj)

		helpers.bulk(client=es,actions=actions, raise_on_error=False)
		print("toes finished:", dbfile, idxname)

	def tosnt(self,dbfile):  
		''' dump snt to console '''
		for snt in Spacybs(dbfile).keys() :
			print(snt)
			
if __name__	== '__main__':
	fire.Fire(util)

'''
def es_source(name, snt, doc, skip_punct:bool=True): 
	id  = hashlib.md5(snt.strip().encode("utf-8")).hexdigest()
	sntlen = len(doc)
	arr = {f"{name}-{id}": {"snt": snt, "type":"snt", "tc": sntlen, "awl":  sum([ len(t.text) for t in doc])/sntlen, 'postag': ' '.join(['^'] + [f"{t.text}_{t.lemma_}_{t.tag_}_{t.pos_}" for t in doc] + ['$']) } }
	
	[ arr.update({ f"{name}-{id}-trp-{t.i}" : {"src":f"{name}-{id}",'type':'trp','gov': t.head.lemma_, 'rel': f"{t.dep_}_{t.head.pos_}_{t.pos_}", 'dep': t.lemma_ }}) for t in doc if not skip_punct or t.dep_ not in ('punct')]
	[ arr.update({ f"{name}-{id}-tok-{t.i}" : {'type':'tok', 'src': f"{name}-{id}", 'lex': t.text, 'low': t.text.lower(), 'lem': t.lemma_, 'pos': t.pos_, 'tag': t.tag_, 'i':t.i, 'head': t.head.i }}) for t in doc]
	[ arr.update({ f"{name}-{id}-np-{np.start}" : {'type':'np', 'src': f"{name}-{id}", 'lem': doc[np.end-1].lemma_, 'chunk': np.text, }}) for np in doc.noun_chunks]
	return arr 
'''