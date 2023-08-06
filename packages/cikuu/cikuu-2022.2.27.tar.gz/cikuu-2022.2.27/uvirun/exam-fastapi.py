# cp from dsk-fastapi, 2022.2.27
#uvicorn exam-fastapi:app --port 19221 --host 0.0.0.0 --reload
import json,os,uvicorn,time,redis,traceback,spacy
from collections import defaultdict, Counter
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
app	 = FastAPI()

# hash: corpus  = exam01, exam02, ...  Hincrby 
# exam01: set  => {exam01:1
# exam01:1 hash-> {essay: id: snts: 

redis.dsk	= redis.Redis("127.0.0.1", port=9221, db=0, decode_responses=True) 
redis.mkf	= redis.Redis("127.0.0.1", port=9221, db=1, decode_responses=True) 
redis.dm	= redis.Redis("127.0.0.1", port=9221, db=2, decode_responses=True) 
redis.bs	= redis.Redis("127.0.0.1", port=9221, db=3, decode_responses=False)
redis.tag	= redis.Redis("127.0.0.1", port=9221, db=4, decode_responses=True) # key:snt ,hashtable ,  simple_sent ,  [2,5,"NP"] 

if not hasattr(spacy, 'nlp'): 
	spacy.nlp		= spacy.load('en_core_web_sm')
	spacy.frombs	= lambda bs: list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None
	spacy.tobs		= lambda doc: ( doc_bin:= spacy.tokens.DocBin(), doc_bin.add(doc), doc_bin.to_bytes())[-1]
	spacy.getdoc	= lambda snt: ( bs := redis.bs.get(snt), doc := spacy.frombs(bs) if bs else spacy.nlp(snt), redis.bs.setnx(snt, spacy.tobs(doc)) if not bs else None )[1]

eidv_list   = lambda rid: [f"{k}-{v}" for k,v in redis.dsk.hgetall(f"rid:{rid}").items()]
rid_snts	= lambda rid: (	snts := [], [ snts.extend(json.loads(redis.dsk.hget(eidv, 'snts'))) for eidv in eidv_list(rid) ] )[0]
rid_mkfs	= lambda rid: [	json.loads(mkf) for mkf in redis.mkf.mget( rid_snts(rid)) ]
eidv_score  = lambda eidv: json.loads(redis.dsk.hget(eidv,'dsk')).get('info',{}).get('final_score',0.0)

@app.get('/exam/add_new_essay')
def add_new_essay(topk:int=10):  
	''' 输出最新的10个rid	'''
	return redis.dsk.zrevrange("rids", 0,topk, True)

@app.post('/exam/update_sent_tags')
def update_sent_tags(snt:str=""):  
	''' '''
	return redis.dsk.zrevrange("rids", 0,topk, True)

@app.get('/exam/add_sent_tag')
def add_sent_tags(snt:str="Hello world", ibeg:int=0, iend:int=1, tag:str="mytag", comment:str=""):  
	''' [1,3,"NP"]  '''
	return redis.tag.hset(snt, json.dumps([ibeg,iend, tag]), comment ) 

@app.get('/dsk/rids')
def dsk_rids(topk:int=10):  
	''' 输出最新的10个rid	'''
	return redis.dsk.zrevrange("rids", 0,topk, True)
@app.get('/dsk/uids')
def dsk_uids(topk:int=10):  
	''' 输出最新的10个uid	'''
	return redis.dsk.zrevrange("uids", 0,topk, True)

@app.get('/')
def home(): 
	return HTMLResponse(content=f"<h2> dsk 19221  </h2>  data source for dm.pigai.org <br>  <a href='/docs'> docs </a> | <a href='/redoc'> redoc </a>   <br>2022-2-21")

@app.get('/dsk/rid/eidv')
def dsk_rid_eids(rid:int=2573411):  
	''' 对应rid的 eidv  ( eid + version)	'''
	return redis.dsk.hgetall(f"rid:{rid}")
@app.get('/dsk/uid/eidv')
def dsk_uid_eids(uid:int=28722050):  
	''' 对应uid的 eidv  ( eid + version)	'''
	return redis.dsk.hgetall(f"uid:{uid}")

@app.get('/dsk/eidv')
def dsk_eidv(eidv:str="152794993-2"):  
	''' eidv 对应的 dsk 信息 '''
	dsk		= redis.dsk.hgetall(eidv)
	snts	= json.loads(dsk['snts']) # pids
	dsk['snt']  = [json.loads(s) if s else {} for s in redis.mkf.mget(snts)]
	return dsk

@app.get('/dsk/eidv/info')
def dsk_eidv_info(eidv:str="152794993-2"):  
	''' eidv 对应的 dsk info, 包括了 作文信息，用在作文浏览  '''
	return json.loads(redis.dsk.hget(eidv,'dsk'))['info']
@app.get('/dsk/rid/info')
def dsk_rid_info(rid:int=2573411):  
	''' rid 对应的 dsk info, 包括了 作文信息，用在作文浏览  '''
	return { eidv: dsk_eidv_info(eidv) for eidv in eidv_list(rid)}

@app.get('/dsk/eidv/dim')
def dsk_eidv_dim(eidv:str="152794993-2"):  
	''' eidv 对应的 维度 '''
	return json.loads(redis.dsk.hget(eidv,'dsk'))['doc']
@app.get('/dsk/rid/dim')
def dsk_rid_dim(rid:int=2573411):  
	''' 维度概述、词汇丰富度、词汇难度、从句密度、平均句长、拼写正确率 '''
	return { eidv: dsk_eidv_dim(eidv) for eidv in eidv_list(rid)}

@app.get('/dsk/rid/score')
def dsk_rid_score(rid:int=2573411):  
	''' 每个eid对应的score '''
	return { eidv: eidv_score(eidv) for eidv in eidv_list(rid)}

@app.post('/dsk/eidv/scores')
def dsk_eidv_scores(eidv_list:list):  
	''' ["152794993-2","152794993-3"] 对应的分数 '''
	return { eidv: eidv_score(eidv) for eidv in eidv_list}

@app.get('/dsk/rid/feedbacks')
def dsk_rid_feedbacks(rid:int=2573411, topk:int=10):  
	''' 错误分布，需要过滤 confusion 之类错误，然后再映射成中文名称， get cate distribution,  {e_snt.nv_agree:32, ... }  '''
	snts = []
	[ snts.extend(json.loads(redis.dsk.hget(eidv, 'snts'))) for eidv in eidv_list(rid) ]
	si = Counter()
	for mkf in redis.mkf.mget(snts):
		for kp, v in json.loads(mkf)['feedback'].items():
			si.update({v['cate']:1})
	return si.most_common(topk)

@app.get('/dsk/rid/wordlist')
def dsk_rid_wordlist(rid:int=2573411, pos:str='VERB',topk:int=10):  
	''' 不同词性的词列表， pos:  LEX/LEM/VERB/NOUN/ADJ/ADV/dobj_VERB_NOUN 
	动词+ 名词： dobj_VERB_NOUN  
	形容词 + 名词： amod_NOUN_ADJ
	名词+动词：  nsubj_VERB_NOUN
	副词+动词：  advmod_VERB_ADV
	副词+形容词：  advmod_ADJ_ADV
	'''
	si = Counter()
	[ si.update( dict( redis.dm.zrevrange(f"{eidv}:{pos}",0,-1,True) ) ) for eidv in eidv_list(rid) ]
	return si.most_common(topk)	

@app.get('/dsk/rid/wordlevel')
def wordlevel(rid:int=2573411, level:str='awl',topk:int=10):  
	''' 分级词汇， awl/gsl1/gsl2	'''
	import dic
	if not hasattr(wordlevel, 'wl'): wordlevel.wl = dic.word_level()
	si = Counter()
	[ si.update( dict( redis.dm.zrevrange(f"{eidv}:LEM",0,-1,True) ) ) for eidv in eidv_list(rid) ]
	return Counter( {s:i for s,i in si.items() if wordlevel.wl.get(s,'') == level }).most_common(topk) 

@app.get('/dsk/rid/fts')
def fts(rid:int=2573411):  
	'''  '''
	[ redis.dm.delete(k) for k in redis.dm.keys(f"rid:{rid}:*")]
	for eidv in eidv_list(rid):
		try:
			eid = eidv.split('-')[0]
			snts = json.loads(redis.dsk.hget(eidv, 'snts'))
			for idx, snt in enumerate(snts):
				redis.dm.hset(f"rid:{rid}:snts", f"{eidv}-{idx}", snt)
				doc = spacy.getdoc(snt) 
				for t in doc: 
					redis.dm.zincrby(f"rid:{rid}:LEX:{t.text.lower()}",1, f"{eidv}-{idx}")
					redis.dm.zincrby(f"rid:{rid}:LEM:{t.lemma_}",1, f"{eidv}-{idx}")
					redis.dm.zincrby(f"rid:{rid}:{t.pos_}:{t.lemma_}",1, f"{eidv}-{idx}")
					redis.dm.zincrby(f"rid:{rid}:{t.dep_}_{t.head.pos_}_{t.pos_}:{t.head.lemma_} {t.lemma_}",1, f"{eidv}-{idx}")
		except Exception as ex:
			print(">>ex:", ex)
	return rid

@app.get('/dsk/rid/term_snt')
def term_snt(rid:int=1387119, term:str='VERB:make'):  
	''' term -> snt search, LEM:make, VERB:make''' 
	#sntids = redis.dm.zrevrange(f"rid:{rid}:{term}",0,-1)
	sntids = redis.dm.smembers(f"rid:{rid}:{term}") #	rid:1387119:VERB:make
	return redis.dm.hmget(f"rid:{rid}:snts", list(sntids))

@app.get('/dsk/uid/stats')
def dsk_uid_stats(uid:int=28679972):  
	''' term -> snt search, LEM:make, VERB:make''' 
	eidver = redis.dsk.hgetall(f"uid:{uid}") #hver(f"uid:{uid}", eid, ver )
	snts = redis.dm.hgetall(f"uid:{uid}:snts") #{"eidv":eidv, "rid":rid, "idx":idx, "tm":ct,"tc":len(docs[idx])}
	return {"eidver":eidver, 'snts':snts}

from math import log as ln
def likelihood(a,b,c,d, minus=None):  #from: http://ucrel.lancs.ac.uk/llwizard.html
	try:
		if a is None or a <= 0 : a = 0.000001
		if b is None or b <= 0 : b = 0.000001
		E1 = c * (a + b) / (c + d)
		E2 = d * (a + b) / (c + d)
		G2 = round(2 * ((a * ln(a / E1)) + (b * ln(b / E2))), 2)
		if minus or  (minus is None and a/c < b/d): G2 = 0 - G2
		return G2
	except Exception as e:
		print ("likelihood ex:",e, a,b,c,d)
		return 0

@app.post('/dsk/keyness')
def keyness(arr:list):
	''' [[1,2,3,4],[2,3,4,5]],  http://ucrel.lancs.ac.uk/llwizard.html '''
	return [ ( ar[0],ar[1],ar[2],ar[3], likelihood(ar[0],ar[1],ar[2],ar[3]) ) for ar in arr]

@app.get('/dsk/uid/snts')
def dsk_uid_snts(uid:int=28679972, pos:str='VERB',topk:int=None):  
	''' 当前uid 的 verb list '''
	si = Counter()
	for snt, v in redis.dm.hgetall(f"uid:{uid}:snts").items():#hgetall uid:28679972:snts
		doc = spacy.getdoc(snt)
		[ si.update({ t.lemma_:1}) for t in doc if t.pos_ == pos ]
	return si.most_common(topk)

@app.get('/dsk/rid/snts')
def dsk_rid_snts(rid:int=2573411, pos:str='VERB',topk:int=None):  
	''' 当前rid 的 verb list '''
	si = Counter()
	snts = {snt for eidv, snt in redis.dm.hgetall(f"rid:{rid}:snts").items()}
	for snt in snts: 
		doc = spacy.getdoc(snt)
		[ si.update({ t.lemma_:1}) for t in doc if t.pos_ == pos ]
	return si.most_common(topk)

@app.get('/dsk/uid_rid/keyness')
def dsk_uid_stats(uid:int=28679972, rid:int=2573411, exclude:bool=True, pos:str='VERB'): 
	''' ''' 
	#redis.dm.hset(f"uid:{uid}:snts", snt, json.dumps({"eidv":eidv, "rid":rid, "idx":idx, "tm":ct,"tc":len(docs[idx])})) # later overwrite former snt, to build person vocab
	#redis.dm.hset(f"rid:{rid}:snts", f"{eidv}:{idx}", snt)
	uid_si = dict( dsk_uid_snts(uid,pos) )
	rid_si = dict( dsk_rid_snts(uid,pos) ) # how to exclude 
	return [ (s,i ) for s, i in rid_si.items() if not s in uid_si]	

if __name__ == '__main__': 
	print("hello")

'''
@app.get('/dsk/rid/submit_es')
def submit(rid:int=2573411, idxname:str='dsksnt', eshost:str="essaydm.wrask.com", esport:int=9200, poslist:str="ADJ,ADV,NOUN,VERB,dobj_VERB_NOUN,amod_NOUN_ADJ,nsubj_VERB_NOUN.advmod_VERB_ADV,advmod_ADJ_ADV", refresh_index:bool=False):  
	#把当前 rid 的最新 eid 信息投递到 ES， 支持搜索 
	from elasticsearch import Elasticsearch,helpers
	import so 
	if not hasattr(submit, 'es'): submit.es = Elasticsearch([ f"http://{eshost}:{esport}" ])  
	if refresh_index: submit.es.indices.delete(idxname)
	if not submit.es.indices.exists(idxname): submit.es.indices.create(idxname, so.config) 
	submit.es.delete_by_query(index=idxname, conflicts='proceed', body={"query":{"match":{"rid":rid}}})
	actions=[] #{"_id": "140948871-9", "_source": {"rid": "10", "uid": "25110374", "sc": 14, "md5": "da891a7d81f7a5e43b571168cc483b6c dba0b4c99ef37cadfc4bacd61fcefa5b d6b199bfae35246564c598ac78d84c91 38a945eeff5b5a587a26dcc6560e0061 58605af6b50b01f15c0cc3ee2aa75e33 c30566c355ae09ea68673e2940d49d0a 7972c906aef51380310363093e141ef8 dabdd545400415da6d29125bf872"}}
	for eidv in eidv_list(rid):
		try:
			eid = eidv.split('-')[0]
			snts = json.loads(redis.dsk.hget(eidv, 'snts'))
			for idx, snt in enumerate(snts): 
				actions.append({'_op_type':'index', '_index':idxname, "_id":f"{eidv}-{idx}",  "_source": {"rid":rid, "eid":eid, "snt":snt, "type":"snt", "sid": f"{eidv}-{idx}"}}) # add uid 
			for pos in poslist.split(','):
				for w, i in redis.dm.zrevrange(f"{eidv}:{pos}", 0,-1,True):
					actions.append({'_op_type':'index', '_index':idxname,"_id": f"{eidv}-{idx}-{w}",
					"_source": {"rid":rid, "eid":eid, "type":"term", "sid": f"{eidv}-{idx}", "term": w}}) # add uid 
		except Exception as ex:
			print(">>ex:", ex)
	return helpers.bulk(client=submit.es,actions=actions, raise_on_error=False)

redis.r		= redis.Redis("127.0.0.1", port=9221, db=0, decode_responses=True) 
redis.dm	= redis.Redis("127.0.0.1", port=9221, db=1, decode_responses=True)
redis.dsk	= redis.Redis("127.0.0.1", port=9221, db=2, decode_responses=True) 
redis.mkf	= redis.Redis("127.0.0.1", port=9221, db=3, decode_responses=True) 
redis.tag	= redis.Redis("127.0.0.1", port=9221, db=4, decode_responses=True) # key:snt ,hashtable ,  simple_sent ,  [2,5,"NP"] 
redis.bs	= redis.Redis("127.0.0.1", port=9221, db=5, decode_responses=False)

'''