# 2022-2-13  cp from cikuu/bin/es.py 
import json,fire,sys, redis,os #, spacy
#from elasticsearch import helpers,Elasticsearch
#from .config import config, readline
from so import * 

class ES(object):

	def __init__(self, host='127.0.0.1',port=9200): 
		self.es = Elasticsearch([ f"http://{host}:{port}" ])  

	def hello(self): print (self.es)

	def addfolder(self, folder:str, corpus:str, pattern=".txt", idxname:str='docbase'): 
		''' folder -> docbase, 2022.1.23 '''
		print("addfolder started:", folder, idxname, self.es, flush=True)
		if not self.es.indices.exists(idxname): self.es.indices.create(idxname, config)
		for root, dirs, files in os.walk(folder):
			for file in files: 
				if file.endswith(pattern):
					self.es.index(index=idxname,id = f"{corpus}-{file}",  body = {"filename":file,'corpus':corpus,'body':open(f"{folder}/{file}",'r', encoding='utf-8').read().strip() })
					print (file, folder, flush=True)
		print("addfolder finished:", folder, idxname, self.es, flush=True)

	def loadjukuu(self, infile, idxname, batch=100000): 
		''' 2022.1.11 '''
		print("loadsource started:", infile, idxname, self.es, flush=True)
		if not self.es.indices.exists(idxname): self.es.indices.create(idxname, config)
		actions=[]
		for line in readline(infile):  #{"_id": "140948871-9", "_source": {"rid": "10", "uid": "25110374", "sc": 14, "md5": "da891a7d81f7a5e43b571168cc483b6c dba0b4c99ef37cadfc4bacd61fcefa5b d6b199bfae35246564c598ac78d84c91 38a945eeff5b5a587a26dcc6560e0061 58605af6b50b01f15c0cc3ee2aa75e33 c30566c355ae09ea68673e2940d49d0a 7972c906aef51380310363093e141ef8 dabdd545400415da6d29125bf872"}}
			try:
				arr = json.loads(line)
				arr['content'] = arr['en'] + ' ' + arr['zhseg']
				del arr['zhseg'] 
				actions.append({'_op_type':'index', '_index':idxname, "_source": arr})
				if len(actions) > batch : 
					helpers.bulk(client=self.es,actions=actions, raise_on_error=False)
					actions=[]
					print(arr, flush=True) 
			except Exception as ex:
				print(">>callback ex:", ex, line)
		helpers.bulk(client=self.es,actions=actions, raise_on_error=False)
		print("loadsource finished:", infile,idxname)

	def idsource(self, infile, idxname, batch=100000): 
		''' {"_id": "140948871-9", "_source": {"rid": "10", "uid": "25110374", "sc": 14, "md5": "da891a7d81f7a5e43b571168cc483b6c dba0b4c99ef37cadfc4bacd61fcefa5b d6b199bfae35246564c598ac78d84c91 38a945eeff5b5a587a26dcc6560e0061 58605af6b50b01f15c0cc3ee2aa75e33 c30566c355ae09ea68673e2940d49d0a 7972c906aef51380310363093e141ef8 dabdd545400415da6d29125bf872"}}
		added 2022.2.11 '''
		print("idsource started:", infile, idxname, self.es, flush=True)
		if not self.es.indices.exists(idxname): self.es.indices.create(idxname, config)
		actions=[]
		for line in readline(infile):  
			try:
				arr = json.loads(line)
				if not '_source' in arr : arr = {"_source": arr} # source only njson 
				arr.update({'_op_type':'index', '_index':idxname})
				actions.append(arr)
				if len(actions) > batch : 
					helpers.bulk(client=self.es,actions=actions, raise_on_error=False)
					actions=[]
					print(arr["_id"], flush=True) 
			except Exception as ex:
				print(">>callback ex:", ex, line)
		helpers.bulk(client=self.es,actions=actions, raise_on_error=False)
		print("idsource finished:", infile,idxname)

	def loadsnts(self, infile, idxname, batch=100000): 
		''' {"eid": 63885890, "ver": "20", "rid": 10, "uid": 6641784, "sc": 28, "snts": ["Robinson was born in an honest, middle - class -- added 2021.12.1 '''
		print("loadsnts started:", infile, flush=True)
		if not self.es.indices.exists(idxname): self.es.indices.create(idxname, config)
		actions=[]
		for line in readline(infile):  #{"_id": "140948871-9", "_source": {"rid": "10", "uid": "25110374", "sc": 14, "md5": "da891a7d81f7a5e43b571168cc483b6c dba0b4c99ef37cadfc4bacd61fcefa5b d6b199bfae35246564c598ac78d84c91 38a945eeff5b5a587a26dcc6560e0061 58605af6b50b01f15c0cc3ee2aa75e33 c30566c355ae09ea68673e2940d49d0a 7972c906aef51380310363093e141ef8 dabdd545400415da6d29125bf872"}}
			try:
				arr = json.loads(line)
				arr["md5"] = sntmd5( arr['snts'])
				id = f"{arr['eid']}-{arr['ver']}"
				del arr['snts']
				del arr['eid']
				del arr['ver']
				actions.append({'_op_type':'index', '_index':idxname,  "_id": id, "_source": arr})
				if len(actions) > batch : 
					helpers.bulk(client=self.es,actions=actions, raise_on_error=False)
					actions=[]
					print(line) 
			except Exception as ex:
				print(">>callback ex:", ex, line)
		helpers.bulk(client=self.es,actions=actions, raise_on_error=False)
		print("index_json finished:", infile,idxname)

	def eevjson(self, infile, idxname, batch=100000,  rhost='127.0.0.1', rport=6662, rdb=0): 
		''' 2021.12.8 '''
		r = redis.Redis(rhost, port=rport, db=rdb, decode_responses=True)
		print("load eevjson started:", infile, r, self.es, flush=True)
		if not self.es.indices.exists(idxname): self.es.indices.create(idxname, config)
		actions=[]
		for line in readline(infile):  #{"_id": "140948871-9", "_source": {"rid": "10", "uid": "25110374", "sc": 14, "md5": "da891a7d81f7a5e43b571168cc483b6c dba0b4c99ef37cadfc4bacd61fcefa5b d6b199bfae35246564c598ac78d84c91 38a945eeff5b5a587a26dcc6560e0061 58605af6b50b01f15c0cc3ee2aa75e33 c30566c355ae09ea68673e2940d49d0a 7972c906aef51380310363093e141ef8 dabdd545400415da6d29125bf872"}}
			try:
				arr = json.loads(line.strip().replace(', null,',',0,'))
				eid = int(arr.get('essay_id', 0))
				ver = str(arr.get('version',0))
				rid = arr.get('request_id',0)
				uid = arr.get('user_id',0)
				ct = arr.get('ctime',0)
				
				row = r.get(eid)
				row = json.loads(row) if row else {}
				if not ver in row: 
					print(">> snts missed:", eid, ver, arr['id'], flush=True)
					row[ver] = spacy.snts(arr['essay'])
					r.set(eid, json.dumps(row))

				snts = row[ver] 
				sour = {"rid": int(rid), "uid": int(uid), "sc":len(snts), "md5": sntmd5(snts), "ct": int(ct)}
				actions.append({'_op_type':'index', '_index':idxname,  "_id": f"{eid}-{ver}", "_source": sour})
				if len(actions) > batch : 
					helpers.bulk(client=self.es,actions=actions, raise_on_error=False)
					actions=[]
					print(eid, ver, rid, uid, flush=True) 
			except Exception as ex:
				print(">>callback ex:", ex, line)
		helpers.bulk(client=self.es,actions=actions, raise_on_error=False)
		print("load eevjson finished:", infile,idxname)

	def load_pika_eev(self, ibeg, iend, idxname = 'eevsim', pikahost='192.168.121.3', port=9221, db=2, batch=100000): 
		''' id: [ibeg, iend) , added 2021.12.2 '''
		r = redis.Redis(pikahost, port=port, db=db, decode_responses=True)
		print("index pika started:", ibeg,iend, r)
		if not self.es.indices.exists(idxname): self.es.indices.create(idxname, config)
		#{"_id": "140948871-9", "_source": {"rid": "10", "uid": "25110374", "sc": 14, "md5": "da891a7d81f7a5e43b571168cc483b6c dba0b4c99ef37cadfc4bacd61fcefa5b d6b199bfae35246564c598ac78d84c91 38a945eeff5b5a587a26dcc6560e0061 58605af6b50b01f15c0cc3ee2aa75e33 c30566c355ae09ea68673e2940d49d0a 7972c906aef51380310363093e141ef8 dabdd545400415da6d29125bf872"}}
		for eidv in r.zrangebyscore("eids", ibeg, iend): 
			try:
				arr = eidv.strip().split(':') #149304158:15
				if len(arr) != 2 : continue
				eid,ver = arr 
				snts = json.loads(r.hget(eid,'snts'))[ver]
				self.es.index(index = idxname, id = f"{eid}-{ver}", body = {'rid': int(r.hget(eid,'rid')), 'uid': int(r.hget(eid,'uid')), 'md5': sntmd5(snts), 'sc':len(snts)})
				print (eidv) 
			except Exception as ex:
				print(">>callback ex:", ex, eidv)
		print("load_pika_eev finished:", ibeg, iend,idxname)

	def init(self, idxname):
		''' init a new index '''
		try:
			if self.es.indices.exists(idxname):
				print("already exists", idxname)
				self.es.indices.delete(idxname)
			self.es.indices.create(idxname, config) #, body=snt_mapping
		except Exception as e:
			print("exception,", str(e))
		print(">>finished " + idxname )

	def clear(self, idxname):
		self.es.delete_by_query(idxname, body={"query": {"match_all": {}}})

	def dump(self, idxname):
		''' --- dump index name to JSON file,ie: pigai06 '''
		for a in helpers.scan(self.es,query={"query": {"match_all": {}}}, index=idxname):
			print (a['_id'] + "\t" + json.dumps(a['_source'])) #{'_index': 'pigai06', '_type': '_doc', '_id': '0_40088501_2_0', '_score': None, '_source': {'snt': 'Whether of courses in psychology .', 'postag': 'Whether_IN of_IN courses_NNS in_IN psychology_NN ._.', 'np': ['courses', 'psychology']}, 'sort': [82714]}
		print(">>finished " , idxname, file=sys.stderr)

	def ids(self, idxname):
		''' --- dump _id to file,ie: eev '''
		for a in helpers.scan(self.es,query={"query": {"match_all": {}}}, index=idxname):
			print(a['_id']) 
		print(">>finished " , idxname, file=sys.stderr)

	def load(self, kv_json , idxname):
		''' submit kv_json to es_index, format: _id<TAB><JSON> 20-2-19 '''
		with open(kv_json,'r') as fp:
			actions=[]
			for line in fp.readlines():
				arr = line.strip().split("\t")
				if len(arr) >= 2:
					try:
						d = json.loads(arr[1])
						actions.append({'_op_type':'index', '_index':idxname, '_id':arr[0].strip() , '_source':d})
					except Exception as e:
						print("ex:", e, line)
			helpers.bulk(client=es,actions=actions, raise_on_error=False)
		print(">>finished " , kv_json, idxname )

	def keys(self, idxname):
		''' --- dump index name,ie: pigai06 '''
		query={"query" : {"match_all" : {}}}
		scanResp= helpers.scan(client= es, query=query, scroll= "10m", index= idxname , timeout="10m")
		for resp in scanResp:
			print(resp['_id'])

if __name__ == '__main__':
	fire.Fire(ES)

def test(): #https://elasticsearch-py.readthedocs.io/en/master/
	doc = {
    'author': 'kimchy',
    'text': 'Elasticsearch: cool. bonsai cool.',
    'timestamp': '2020-6-24',}
	res = es.index(index="test-index", id=2, body=doc)
	print("result", res['result'])

	res = es.get(index="test-index", id=1)
	print(res['_source'])

	es.indices.refresh(index="test-index")

	res = es.search(index="test-index", body={"query": {"match_all": {}}})
	print("Got %d Hits:" % res['hits']['total']['value'])
	for hit in res['hits']['hits']:
		print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])


def submit(jsonfile, idxname ='docsim', host='127.0.0.1', id='eid'):
	''' {"eid": "1", "rid": "1419931", "uid": "19704146", "snts": ["Next Monday, a foreign friend will come to meet me.", "I want to give him some representative gifts.", "The 
first thing I want to send is tea.", "The tea culture in Sichuan is very deep.", "On the one hand, Sichuan tea has a strong aroma and a good taste.", "On the other hand
, tea also reflects the relaxed and elegant life culture of Sichuan people.", "The second thing I want to send is the hot pot bottom.", "It is a very symbolic symbol of
 Sichuan.", "Also reflects the food culture of Scihua"]} '''
	print(r, infile, host, idxname, flush=True)
	es = Elasticsearch([host]) 
	file = open(infile, 'r')
	while True:
		line = file.readline()
		if not line: break; 
		try:
			arr = json.loads(line.strip())
			eid = arr[id]
			del arr[id]
			es.index(index=idxname, id=eid, body=arr)
		except Exception as e:# skip those speical keys 
			print("ex:", e)	
	file.close()
	print(">> finished:", infile, flush=True)

def submit_batch(jsonfile, idxname ='sntsim', es_host='127.0.0.1', id='eid', batch=100000):
	from elasticsearch import helpers
	print(r, infile, es_host, idxname, flush=True)
	es = Elasticsearch([es_host]) 
	actions=[]
	file = open(infile, 'r')
	while True:
		line = file.readline()
		if not line: break; 
		try:
			arr = json.loads(line.strip())
			eid = arr[id]
			del arr[id]
			actions.append({'_op_type':'index', '_index':idxname, '_id':eid , '_source':d})
			if len(actions) > 0  : 
				helpers.bulk(client=es,actions=actions, raise_on_error=False)
				actions=[]					
		except Exception as e:# skip those speical keys 
			print("ex:", e)	
	file.close()
	if len(actions) > 0  : 
		helpers.bulk(client=es,actions=actions, raise_on_error=False)
	print(">> finished:", infile, flush=True)


'''
 "mappings": {
    "_source": {
      "includes": [
        "*.count",
        "meta.*"
      ],
      "excludes": [
        "meta.description",
        "meta.other.*"
      ]
    }
  }

	def bulk_submit(self, actions):
		helpers.bulk(client=self.es,actions=actions) #, raise_on_error=False

PUT my_index/_doc/1
{
  "name": "Some binary blob",
  "blob": "U29tZSBiaW5hcnkgYmxvYg==" 
}


PUT maptest/_mapping/test
{
    "dynamic_templates": [
        {
            "en": {
                "match": "*_json",
                "match_mapping_type": "keyword",
                "mapping": {
                    "type": "keyword",
                    "store": "yes",
                    "index": "not_analyzed"
                }
            }
        }
    ]
}

PUT /my_index
{
    "mappings": {
        "my_type": {
            "dynamic_templates": [
                { "es": {
                      "match":              "*_es", 
                      "match_mapping_type": "string",
                      "mapping": {
                          "type":           "string",
                          "analyzer":       "spanish"
                      }
                }},
                { "en": {
                      "match":              "*", 
                      "match_mapping_type": "string",
                      "mapping": {
                          "type":           "string",
                          "analyzer":       "english"
                      }
                }}
            ]
}}}
https://www.elastic.co/guide/cn/elasticsearch/guide/current/custom-dynamic-mapping.html

GET /eevsim/_search
{
  "query": {
    "bool": {
    "must_not":{"term" : {"uid": "123"} },  
    "should": [
        {
          "match": {
            "md5": {
              "query": "201f2e517903766f7c41b90ef27f346f",
              "boost": 2
            }
          }
        },
        {
          "match": {
            "md5": {
              "query": "35179a54ea587953021400eb0cd23201", 
              "boost": 3
            }
          }
        }
      ],
       
      "minimum_should_match": "90%"
    }
  }
}

{"_id": "3-20", "_source": {"rid": 11386, "uid": 21, "sc": 13, "md5": "0f4d9831fee517c2b4223e4ebf6d0930 bfd2f212e4fdbc1b4b9e3c4d14fa42b1 20b30ac261d74904e7b9b3e2cf313728 a0
04c0a2b3e048968cea61002c71b1c6 83f565eac47ede4b022a77cd08d85bc5 a269cf9ee7c15792566a9c4953aed1a6 f380b022b086b477e6f1f6882fcf3b07 fa74e6c1cded62fad1c99999b6d613e0 c4da8d100
6203cb7ba6103ec55c12edc 7af1c8021855d7605e6e7b3d1c370372 d33a962163197dda27c395925a2d1d48 232d21f3b22d6d6fbb6b7fd035e03053 c9dbf1351587627236c0893aac2d1573"}}

12.2 , wrong program's id range 
127.0.0.1:9221[2]> zrevrange ids 0 10
 1) "811997267"
 2) "811997259"
 3) "811997255"
 4) "811997251"
 5) "811997231"
 6) "811997229"
 7) "811997215"
 8) "811997213"
 9) "811997195"
10) "811997191"
11) "811997185"

if spacy: 
	from spacy.lang import en
	spacy.sntbr		= (inst := en.English(), inst.add_pipe("sentencizer"))[0]
	spacy.snts		= lambda essay: [ snt.text.strip() for snt in  spacy.sntbr(essay).sents]
	spacy.nlp		= spacy.load('en_core_web_sm')
	spacy.frombs	= lambda bs: list(spacy.tokens.DocBin().from_bytes(bs).get_docs(spacy.nlp.vocab))[0] if bs else None
	spacy.tobs		= lambda doc: ( doc_bin:= spacy.tokens.DocBin(), doc_bin.add(doc), doc_bin.to_bytes())[-1]
	spacy.vplem		= lambda doc,ibeg,iend: doc[ibeg].lemma_ + " " + doc[ibeg+1:iend].text.lower()
	spacy.getdoc	= lambda snt: ( bs := redis.bs.get(snt), doc := spacy.frombs(bs) if bs else spacy.nlp(snt), redis.bs.setnx(snt, spacy.tobs(doc)) if not bs else None )[1]
	spacy.sntdocs	= lambda hkey: [spacy.getdoc(snt) for snt in json.loads(redis.r.hget(hkey,'snts'))] #'doc:inau:inau/1893-Cleveland.txt'

2021.12.12
ubuntu@ubuntu:/ftp/esmd5$ nohup python3 -m cikuu.bin.es loadjson eev2021.esmd5 eevsim & 
[1] 47096

 "_doc": {
				  "dynamic_templates": [
					{
					  "strings_as_keywords": { # only map string to keyword, not text 
						"match_mapping_type": "string",
						"mapping": {
						  "type": "keyword"
						}
					  }
					}
				  ]
				},

'''