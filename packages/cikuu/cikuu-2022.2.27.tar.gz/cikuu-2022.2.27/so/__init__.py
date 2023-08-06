# 2022.2.13
import requests,json, os, math,re
from elasticsearch import Elasticsearch,helpers
from collections import	Counter

#os.environ['eshost'] = 'es.corpusly.com'
#from so imoprt *
eshost	= os.getenv("eshost", "127.0.0.1") 
esport	= int(os.getenv("esport", 9200))
requests.put(f"http://{eshost}:{esport}/_cluster/settings", json={"persistent": {"search.max_buckets": 1000000}}).text

config = {  
		"settings" : {
			"refresh_interval": "1s",
			"number_of_shards": "3",
			"max_result_window":"2147483647",
			"index.mapping.ignore_malformed": "true",
			"analysis": {
			  "filter": {
				"postag_filter": {
				  "type": "pattern_capture",
				  "preserve_original": "false",
				  "patterns": [
					"(^([^_]+)_[a-z]+[,\\.$]?)",
					"(_[a-z\\-\\.\\'\\$0-9]+)$",
					"(_[a-z\\-\\.\\'\\$]+)",
					"(_[^\\w]+)_",
					"([^\\w])_"
				  ]
				},
				"postag_filter2": {
				  "type": "word_delimiter",
				  "type_table": [
					"^ => ALPHA",
					", => ALPHA",
					"$ => ALPHA",
					"_ => ALPHA",
					". => ALPHA",
					"- => ALPHA",
					"! => ALPHA",
					"? => ALPHA",
					"' => ALPHA",
					"0 => ALPHA",
					"1 => ALPHA",
					"2 => ALPHA",
					"3 => ALPHA",
					"4 => ALPHA",
					"5 => ALPHA",
					"6 => ALPHA",
					"7 => ALPHA",
					"8 => ALPHA",
					"9 => ALPHA"
				  ]
				},
				"unique_filter": {
				  "type": "unique",
				  "only_on_same_position": "true"
				}
			  },
			  "analyzer": {
				"postag_ana": {"filter": ["lowercase","postag_filter", "postag_filter2", "unique_filter"], "type": "custom", "tokenizer": "whitespace" },
				"path_ana": {"type": "custom", "tokenizer": "path-tokenizer"},
				"feedback_ana": {"type": "custom", "tokenizer": "feedback-tokenizer"},
				"err_ana": {"type": "custom",  "tokenizer": "path-tokenizer1"  },
				"chunk_ana": {"type": "custom", "tokenizer": "path-tokenizer2" },
				"kp_ana": { "filter": ["lowercase"], "type": "custom", "tokenizer": "keyword"}
			  },
			  "tokenizer": {
				"path-tokenizer": { "type": "path_hierarchy",  "delimiter": "/" },
				"path-tokenizer1": {"type": "path_hierarchy",  "delimiter": "|" },
				"path-tokenizer2": {"type": "path_hierarchy",  "delimiter": "/" },
				"feedback-tokenizer": { "type": "path_hierarchy",  "delimiter": "." }
				}
			},
			"number_of_replicas": "0"
		},
		"mappings" : {
			"_source": {"excludes": ["md5"]},
			"properties": {
			 "@timestamp":{"format":"strict_date_optional_time||epoch_millis", "type":"date"},
			"errs": { "type": "text", "analyzer": "path_ana" ,"fielddata":"true" },
			"feedback": { "type": "text", "analyzer": "feedback_ana" ,"fielddata":"true" },
			"kps": { "type": "text", "analyzer": "path_ana" ,"fielddata":"true" },
			"postag": { "type": "text", "analyzer": "postag_ana","fielddata":"true"},
			"np": { "type": "text", "analyzer": "postag_ana","fielddata":"true"},
			"ske": { "type": "text", "analyzer": "postag_ana","fielddata":"true"},
			"i": { "type": "integer"},
			"start": { "type": "integer"},
			"end": { "type": "integer"},
			"score": { "type": "float"},
			"offset": { "type": "float"},
			"final_score": { "type": "float"},
			"sid": { "type": "keyword"},
			"id": { "type": "keyword"},
			"rid": { "type": "integer"},
			"did": { "type": "integer"},
			"docid": { "type": "keyword"},
			"uid": { "type": "integer"},
			"eid": { "type": "integer"},
			"sntnum": { "type": "integer"},
			"wordnum": { "type": "integer"},
			"awl": { "type": "float"},
			"cnt": { "type": "long"},
			"vers": { "type": "integer"},
			"ver": { "type": "integer"},
			"ct": { "type": "integer"},
			"lem": { "type": "keyword"},
			"lex": { "type": "keyword"},
			"low": { "type": "keyword"},
			"pos": { "type": "keyword"},
			"tag": { "type": "keyword"},
			"term": { "type": "keyword"},

			"ap": { "type": "keyword"},
			"page": { "type": "keyword"},
			"pen": { "type": "keyword"},
			"label": { "type": "keyword"},
			"item": { "type": "keyword"},
			"lang": { "type": "keyword"},
			"key": { "type": "keyword"},
			"item_key": { "type": "keyword"},
			"score": { "type": "float"},
			"tmf": { "type": "float"},
			"stroke": { "type": "keyword", "index": "false"},
			"strokes": { "type": "keyword", "index": "false"},
			"en": { "type": "text", "analyzer": "standard","fielddata":"true"},
			"content": { "type": "text", "analyzer": "standard","fielddata":"true"},
			"zhseg": { "type": "text", "analyzer": "standard"},
			"zh": { "type": "text", "index": "false"},

			"src": { "type": "keyword"},
			"srcsnt": { "type": "keyword"},
			"segtype": { "type": "keyword"},
			"filename": { "type": "keyword"},
			"fullname": { "type": "keyword"},
			"sect": { "type": "keyword"},
			"index": { "type": "keyword"},
			"corpus": { "type": "keyword"},
			"folder": { "type": "keyword"},
			"head": { "type": "keyword"},
			"chunk": { "type": "keyword"},
			"type": { "type": "keyword"},
			"fn": { "type": "keyword"},
			"cat": { "type": "keyword"},
			"rel": { "type": "keyword"},
			"gov": { "type": "keyword"},
			"dep": { "type": "keyword"},
			"vp": { "type": "keyword"},
			"ap": { "type": "keyword"},
			"dp": { "type": "keyword"},
			"kp": { "type": "keyword"},
			"cate": { "type": "keyword"},
			"feedback": { "type": "keyword"},
			"tail":{ "type": "keyword"},
			"govpos":{ "type": "keyword"},
			"deppos":{ "type": "keyword"},
			"fd": { "type": "keyword"},
			"si": {
				   "type": "nested",
				   "properties": {
					  "s": {"type": "keyword"},
					  "i": {"type": "integer"}
				   }
				},
			"err": {"type": "text",  "analyzer": "err_ana"},
			"fd": { "type": "keyword"},
			"short_msg": { "type": "keyword"},
			"arr": { "type": "keyword", "index": "false" }, # dim arr of dsk
			"info": { "type": "keyword", "index": "false" ,"store": "false"},
			"kw": { "type": "keyword", "index": "false" ,"store": "false", "ignore_above": 60},
			"meta": { "type": "keyword", "index": "false" ,"store": "false"},
			"tc": {"type": "integer" , "index": "false"},
			"sc": {"type": "integer" , "index": "false"},
			"isum": {"type": "integer" , "index": "false"},
			"md5": { "type": "text", "store": "false", "norms":"false"},
			"toks": { "type": "keyword", "index": "false" ,"store": "false"},
			"snts": { "type": "keyword", "index": "false" },
			"blob": { "type": "binary", "store": "false"},
			"zlib": { "type": "binary", "store": "false"},
			"title": { "type": "text", "analyzer": "standard"},
			"essay": { "type": "text", "analyzer": "standard"},
			"body": { "type": "text", "index": "false" },
			"doc": { "type": "text", "index": "false" },#"doc": { "type": "keyword", "index": "false" ,"store": "false"}, # dim arr of dsk
			"tm": { "type": "date"}, #"format": "yyyy-MM-dd HH:mm:ss || yyyy-MM-dd || yyyy/MM/dd HH:mm:ss|| yyyy/MM/dd ||epoch_millis"
			"sdate": { "type": "date",  "format": "yyyy-MM-dd"},
			"csv": { "type": "keyword",  "index": "false"},
			"tsv": { "type": "keyword",  "index": "false"},
			"pair": { "type": "keyword",  "index": "false"},
			"json": { "type": "keyword",  "index": "false"},
			"v": { "type": "keyword",  "index": "false"},
			"n": { "type": "keyword",  "index": "false"},
			"adj": { "type": "keyword",  "index": "false"},
			"snt": { "type": "text", "analyzer": "standard","fielddata":"true"}
		  }
		}
	}

#if eshost: 
es		= Elasticsearch([ f"http://{eshost}:{esport}" ])  
newindex= lambda idxname : (es.indices.delete(idxname) if es.indices.exists(idxname) else None, es.indices.create(idxname, config))[1] # body=
rows	= lambda query: requests.post(f"http://{eshost}:{esport}/_sql",json={"query": query}).json().get('rows',[]) 
sql		= lambda query: requests.post(f"http://{eshost}:{esport}/_sql",json={"query": query}).json().get('rows',[]) 
sntnum	= lambda cp: sql(f"select count(*) cnt from {cp} where type = 'snt'" )[0][0] #75222
lexnum	= lambda w,cp: sql(f"select count(*) cnt from {cp} where low = '{w}' and type = 'tok'")[0][0] # opened = 70
lemnum	= lambda w,cp: sql(f"select count(*) cnt from {cp} where lem = '{w}' and type = 'tok'")[0][0] 
sqlsi	= lambda query: (si:=Counter(), [si.update({row[0]:1}) for row in sql(query)])[0]
warmup  = lambda host, port: requests.put(f"http://{host}:{port}/_cluster/settings", json={"persistent": {"search.max_buckets": 1000000}}).text

def readline(infile, sepa=None):
	with open(infile, 'r') as fp:
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

def likelihood(a,b,c,d, minus=None):  #from: http://ucrel.lancs.ac.uk/llwizard.html
	try:
		if a is None or a <= 0 : a = 0.000001
		if b is None or b <= 0 : b = 0.000001
		E1 = c * (a + b) / (c + d)
		E2 = d * (a + b) / (c + d)
		G2 = round(2 * ((a * math.log(a / E1)) + (b * math.log(b / E2))), 2)
		if minus or  (minus is None and a/c < b/d): G2 = 0 - G2
		return G2
	except Exception as e:
		print ("likelihood ex:",e, a,b,c,d)
		return 0

#PUT twitter/_mapping {  "properties": {  "email": { "type": "keyword"  }  }}
#"stroke": { "type": "keyword", "index": "false"},
def delete_index(cp:str='testidx'): 
	return requests.delete(f"http://{eshost}:{esport}/{cp}").text #DELETE /twitter
def new_empty_index(cp:str='testidx', delete:bool=True): 
	if delete: requests.delete(f"http://{eshost}:{esport}/{cp}").text
	return requests.put(f"http://{eshost}:{esport}/{cp}", data={}).text #PUT twitter  {}
def add_mapping_keyword(kws:list, cp:str='testidx'): 
	return [requests.put(f"http://{eshost}:{esport}/{cp}/_mapping/", data={"properties": {  f"{kw}": { "type": "keyword"  }  }}).text for kw in kws]
def add_mapping_keyword_noindex(kws:list, cp:str='testidx'): 
	return [requests.put(f"http://{eshost}:{esport}/{cp}/_mapping/", data={"properties": {  f"{kw}": { "type": "keyword", "index": "false"} }}).text for kw in kws]
def add_mapping_float(kws:list, cp:str='testidx'): 
	return [requests.put(f"http://{eshost}:{esport}/{cp}/_mapping/", data={"properties": {  f"{kw}": { "type": "float"  }  }}).text for kw in kws]
def add_mapping_integer(kws:list, cp:str='testidx'): 
	return [requests.put(f"http://{eshost}:{esport}/{cp}/_mapping/", data={"properties": {  f"{kw}": { "type": "integer"  }  }}).text for kw in kws]
def add_mapping(dic:dict, cp:str='testidx'): 
	''' {"num":"integer", "awl":"float", "tag":"keyword"} '''
	return [requests.put(f"http://{eshost}:{esport}/{cp}/_mapping/", data={"properties": {  f"{k}": { "type": "{v}"  }  }}).text for k,v in dic.items()]

def ids(_ids:list, cp:str='inau'): 
	''' ["one","two"] '''
	sql	= { 
    "query": {
        "ids" : {
            "type" : "_doc",
            "values" : _ids
			}
		}
	}
	return requests.post(f"http://{eshost}:{esport}/{cp}/_search/", json=sql).json()

def term_to_snts(sql): 
	rows = es.sql(sql) #f"select src from {cp} where type = 'trp' and gov='{gov}' and rel='{rel}' and dep='{dep}' limit {topk}"
	sql	= {
    "query": {
        "ids" : {
            "type" : "_doc",
            "values" : [row[0] for row in rows] #clec:snt-34993,  clec:snt-32678
			}
		}
	}
	return requests.post(f"http://{eshost}:{esport}/{cp}/_search/", json=sql).json()

def match_phrase(phrase:str='opened the box', cp:str='clec', topk:int=10): 
	''' '''
	sql	= {
  "query": {
    "match_phrase": {
      "snt": phrase
    }
  }
  , "size": topk
}
	return requests.post(f"http://{eshost}:{esport}/{cp}/_search/", json=sql).json()

phrase_num = lambda phrase, cp='clec', topk=10: match_phrase(phrase, cp, topk)["hits"]["total"]["value"]

addpat	= lambda s : f"{s}_[^ ]*" if not s.startswith('_') else f"[^ ]*{s}_[^ ]*"   # if the last one, add $ 
rehyb   = lambda hyb: ' '.join([ addpat(s) for s in hyb.split()])  #'the_[^ ]* [^ ]*_NNS_[^ ]* of_[^ ]*'
heads   = lambda chunk:  ' '.join([s.split('_')[0].lower() for s in chunk.split()])		#the_the_DT_DET adventures_adventure_NNS_NOUN of_of_IN_ADP
def hybchunk(hyb:str='the _NNS of', index:str='gzjc', size:int= -1, topk:int=10):
	''' the _NNS of -> {the books of: 13, the doors of: 7} , added 2021.10.13 '''
	sql= {
  "query": { 
    "bool": { 
      "must": [
        { "match_phrase": { "postag":  hyb}},
        { "match": { "type":"snt" }}
      ]
    }
  },
  "size":  size
}
	res = requests.post(f"http://{eshost}:{esport}/{index}/_search/", json=sql).json()
	si = Counter()
	repat = rehyb(hyb)
	for ar in res['hits']['hits']: 
		postag =  ar["_source"]['postag']
		m= re.search(repat,postag) #the_the_DT_DET adventures_adventure_NNS_NOUN of_of_IN_ADP
		if m : si.update({ heads(m.group()):1})
	return si.most_common(topk)

if __name__ == "__main__": 
	print(es)

'''
PUT twitter/_mapping 
{
  "properties": {
    "email": {
      "type": "keyword"
    }
  }
}
'''