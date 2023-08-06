# 2022.2.7, cp from dmssi.py , pure rule files 
import spacy , traceback, sys
from spacy.matcher import Matcher,DependencyMatcher
from collections import	Counter, defaultdict

if not hasattr(spacy,'nlp'): spacy.nlp	= spacy.load('en_core_web_sm') #if not 'nlp' in dir(): nlp	= spacy.load('en_core_web_sm')
vp_span = lambda doc,ibeg,iend: doc[ibeg].lemma_ + " " + doc[ibeg+1:iend].text.lower()

def new_matcher(patterns, name='pat'):
	matcher = Matcher(spacy.nlp.vocab)
	matcher.add(name, patterns, greedy ='LONGEST')
	return matcher
matchers = {
"vend":new_matcher([[{"POS": {"IN": ["AUX","VERB"]}},{"POS": {"IN": ["ADV"]}, "OP": "*"}, {"POS": {"IN": ["ADJ","VERB"]}, "OP": "*"},{"POS": {"IN": ["PART","ADP","TO"]}, "OP": "*"},{"POS": 'VERB'}]]), # could hardly wait to meet
"vp":  new_matcher([[{'POS': 'VERB'},{"POS": {"IN": ["DET","ADP","ADJ"]}, "OP": "*"},{"POS": 'NOUN'}, {"POS": {"IN": ["ADP","TO"]}, "OP": "*"}], #He paid a close attention to the book. |He looked up from the side. | make use of
                     [{'POS': 'VERB'},{"POS": {"IN": ["DET","ADP","ADJ","TO","PART"]}, "OP": "*"},{"POS": 'VERB'}]]), # wait to meet
"pp":  new_matcher([[{'POS': 'ADP'},{"POS": {"IN": ["DET","NUM","ADJ",'PUNCT','CONJ']}, "OP": "*"},{"POS": {"IN": ["NOUN","PART"]}, "OP": "+"}]]),    
"ap":  new_matcher([[{"POS": {"IN": ["ADV"]}, "OP": "*"}, {"POS": 'ADJ'}]]),  
"vprt": new_matcher([[{"POS": 'VERB'}, {"POS": {"IN": ["PREP", "ADP",'TO']}, "OP": "+"}]]),   # look up /look up from,  computed twice
#"vtov":  new_matcher([[{"POS": 'VERB'}, {"TAG": 'TO'},{"TAG": 'VB'}]]),   # plan to go
#"vvbg":  new_matcher([[{"POS": 'VERB'}, {"TAG": 'VBG'}]]),   # consider going
"vpg":  new_matcher([[{"POS": 'VERB'}, {"POS": {"IN": ["PREP", "ADP",'PART']}, "OP": "+"},{"TAG": 'VBG'}]]),   # insisted on going
#"vAp":  new_matcher([[{'LEMMA': 'be'},{"TAG": {"IN": ["VBN"]}}, {"POS": {"IN": ["PREP", "ADP",'PART']}}]]),   # be based on   
#"vap":  new_matcher([[{'LEMMA': 'be'},{"POS": {"IN": ["ADJ"]}}, {"POS": {"IN": ["PREP", "ADP",'PART']}}]]),   # be angry with
} #for name, ibeg,iend in matchers['ap'](doc) : print(doc[ibeg:iend].text)

def new_depmatcher(pattern, name='pat'):
	matcher = DependencyMatcher(spacy.nlp.vocab)
	matcher.add(name, [pattern])
	return matcher
depmatchers = {
"svo":new_depmatcher([ 
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "nsubj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "dobj"}
  }
]), # [(4851363122962674176, [2, 0, 4])]
"sva":new_depmatcher([ 
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "nsubj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "acomp"}
  }
]), 
"svx":new_depmatcher([  # plan to go , enjoy swimming 
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "nsubj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "xcomp"}
  }
]), 
"svc":new_depmatcher([  # I think it is right.
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "nsubj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "ccomp"}
  }
]), 
"sattr":new_depmatcher([  #She is  a girl.
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"LEMMA": "be"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "nsubj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "attr"}
  }
]), 
"vpn":new_depmatcher([ # turn off the light
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "prt"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "dobj"}
  }
]), 
"vap":new_depmatcher([ # be happy with
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "acomp",
    "RIGHT_ATTRS": {"DEP": "acomp"}
  },
  {
    "LEFT_ID": "acomp",
    "REL_OP": ">",
    "RIGHT_ID": "prep",
    "RIGHT_ATTRS": {"DEP": "prep"}
  }
]), 
"vdp":new_depmatcher([ # be based on
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"TAG": "VBN"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "be",
    "RIGHT_ATTRS": {"LEMMA": "be"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "prep",
    "RIGHT_ATTRS": {"DEP": "prep"}
  }
]), 
"vppn":new_depmatcher([ # look up from phone
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "prt",
    "RIGHT_ATTRS": {"DEP": "prt"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "prep",
    "RIGHT_ATTRS": {"DEP": "prep"}
  },
  {
    "LEFT_ID": "prep",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "pobj"}
  }
]), 
"vpnpn":new_depmatcher([ # vary from A to B
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "prep1",
    "RIGHT_ATTRS": {"DEP": "prep"}
  },
  {
    "LEFT_ID": "prep1",
    "REL_OP": ">",
    "RIGHT_ID": "object1",
    "RIGHT_ATTRS": {"DEP": "pobj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "prep2",
    "RIGHT_ATTRS": {"DEP": "prep"}
  },
  {
    "LEFT_ID": "prep2",
    "REL_OP": ">",
    "RIGHT_ID": "object2",
    "RIGHT_ATTRS": {"DEP": "pobj"}
  }
]), 
"vnp":new_depmatcher([ # turn it down
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "dobj"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "subject",
    "RIGHT_ATTRS": {"DEP": "prt"}
  }
]), 
"vnpn":new_depmatcher([  # make use of books, take sth into account
  {
    "RIGHT_ID": "v",
    "RIGHT_ATTRS": {"POS": "VERB"}
  },
  {
    "LEFT_ID": "v",
    "REL_OP": ">",
    "RIGHT_ID": "object",
    "RIGHT_ATTRS": {"DEP": "dobj"}
  },
  {
    "LEFT_ID": "object",
    "REL_OP": ">",
    "RIGHT_ID": "prep",
    "RIGHT_ATTRS": {"DEP": "prep"}
  },
  {
    "LEFT_ID": "prep",
    "REL_OP": ">",
    "RIGHT_ID": "pobj",
    "RIGHT_ATTRS": {"DEP": "pobj"}
  }  
]), 
} # for name, ar in depmatchers['svx'](doc) : print(doc[ar[1]], doc[ar[0]], doc[ar[2]])

def attach(doc):
	ssv = defaultdict(dict)
	try:
		[ ssv[f"tok-{t.i}"].update ({"type":"tok", "lex": t.text, "low":t.text.lower(), "lem": t.lemma_, 
			"pos":t.pos_, "tag":t.tag_, "dep":t.dep_ , "head":t.head.lemma_, "offset":round(t.i/len(doc),2)}) for t in doc]
		[ ssv[f"trp-{t.i}"].update ({"type":"trp", "gov": t.head.lemma_, "rel":f"{t.dep_}_{t.head.pos_}_{t.pos_}", "dep":t.lemma_, "govpos":t.head.pos_, "deppos":t.pos_}) for t in doc if t.dep_ not in ('ROOT','punct') and t.pos_ not in ('PUNCT','SPACE')] 
		[ ssv[f"rootv-{t.i}"].update ({"type":"rootv", "lem": t.lemma_, "pos":t.pos_, "tag":t.tag_}) for t in doc if t.dep_ =='ROOT']
		[ ssv[f"vvbg-{t.i}"].update ({"type":"vvbg", "lem": t.head.lemma_, "chunk":f"{t.head.lemma_} {t.text.lower()}", "tail":t.lemma})
			 for t in doc if t.dep_ =='xcomp' and t.head.pos_ == 'VERB' and t.tag_ == 'VBG' and t.lemma_.isalpha() and t.head.lemma_.isalpha()]   #I enjoy smiling. 
		[ ssv[f"vtov-{t.i}"].update ({"type":"vtov", "lem": t.head.lemma_, "tail":t.text.lower(), "chunk":f"{t.head.lemma_} to {t.text.lower()}"})
			 for t in doc if t.dep_ =='xcomp' and t.head.pos_ == 'VERB' and t.tag_ == 'VB' and t.i > 1 and t.doc[t.i-1].tag_ == 'TO' and t.head.text.isalpha() and t.head.lemma_.isalpha()]   #I plan to go. 
		[ ssv[f"mdv-{t.i}"].update ({"type":"mdv","lem":t.head.lemma_, "chunk":f"{t.head.lemma_} {t.lemma_}"}) for t in doc  if t.tag_ == 'MD' and t.dep_ =='aux' and t.head.pos_ == 'VERB' and t.head.lemma_.isalpha()]
		[ ssv[f"np-{sp.start}"].update ({"type":"np","lem":sp.root.lemma_.lower(), "chunk":sp.text.lower()})
			 for sp in doc.noun_chunks if sp.end - sp.start > 1] # add  #book:np , f"#{sp.root.lemma_.lower()}:np" 
		[ ssv[f"npone-{sp.start}"].update ({"type":"np","lem":sp.root.lemma_.lower(),"chunk":sp.text.lower()}) for sp in doc.noun_chunks  if sp.end - sp.start <= 1]
		[ ssv[f"vp-{ibeg}"].update ({"type":"vp","lem":doc[ibeg].lemma_,"chunk":vp_span(doc,ibeg,iend), "tail":doc[iend-1].lemma_}) for name, ibeg,iend in matchers['vp'](doc)]
		[ ssv[f"vprt-{ibeg}"].update ({"type":"vprt","lem":doc[ibeg].lemma_,"chunk":vp_span(doc,ibeg,iend),})
			 for name, ibeg,iend in matchers['vprt'](doc)]
		[ ssv[f"pp-{ibeg}"].update ({"type":"pp","lem":doc[iend-1].lemma_.lower(), "chunk":doc[ibeg:iend].text.lower(),})
			 for name, ibeg,iend in matchers['pp'](doc)]
		[ ssv[f"ap-{ibeg}"].update ({"type":"ap","lem":doc[iend-1].lemma_.lower(),"chunk":doc[ibeg:iend].text.lower(), })
			for name, ibeg,iend in matchers['ap'](doc)]
		[ ssv[f"vend-{ibeg}"].update ({"type":"vend","lem":doc[iend-1].lemma_,"chunk":vp_span(doc,ibeg,iend), })
			for name, ibeg,iend in matchers['vend'](doc)]
		[ ssv[f"vpg-{ibeg}"].update ({"type":"vpg","lem":doc[ibeg+1].lemma_,"chunk":vp_span(doc,ibeg,iend)})
			for name, ibeg,iend in matchers['vpg'](doc)]
		[ ssv[f"svo-{doc[x[0]].i}"].update ({"type":"svo", "chunk":f"{doc[x[1]].lemma_} {doc[x[0]].lemma_} {doc[x[2]].lemma_}", "lem":doc[x[0]].lemma_, }) 
			for name, x in depmatchers['svo'](doc) ]
		[ ssv[f"sva-{doc[x[0]].i}"].update ({"type":"sva","lem":doc[x[0]].lemma_,"chunk":f"{doc[x[1]].lemma_} {doc[x[0]].lemma_} {doc[x[2]].lemma_}"})
			for name, x in depmatchers['sva'](doc) ]
		[ ssv[f"svx-{doc[x[0]].i}"].update ({"type":"svx","lem":doc[x[0]].lemma_,"chunk":doc[x[1]].lemma_+' '+doc[x[0]].lemma_+' '+doc[x[2]].lemma_, })
			for name, x in depmatchers['svx'](doc) ]
		[ ssv[f"sva-{doc[x[0]].i}"].update ({"type":"sva","lem":doc[x[0]].lemma_,"chunk":doc[x[1]].lemma_+' '+doc[x[0]].lemma_+' '+doc[x[2]].lemma_, })
			for name, x in depmatchers['svc'](doc) ]
		[ ssv[f"sattr-{doc[x[0]].i}"].update ({"type":"sattr","lem":doc[x[0]].lemma_,"chunk":doc[x[1]].lemma_+' '+doc[x[0]].lemma_+' '+doc[x[2]].lemma_, })
			for name, x in depmatchers['sattr'](doc) ]
		[ ssv[f"vpn-{doc[x[0]].i}"].update ({"type":"vpn","lem":doc[x[0]].lemma_,"chunk":doc[x[0]].lemma_+' '+doc[x[1]].lemma_+' '+doc[x[2]].lemma_, })
			for name, x in depmatchers['vpn'](doc) ]
		[ ssv[f"vap-{doc[x[0]].i}"].update ({"type":"vap","lem":doc[x[1]].lemma_,"chunk":doc[x[0]].lemma_+' '+doc[x[1]].lemma_+' '+doc[x[2]].lemma_, })
			for name, x in depmatchers['vap'](doc) ]
		[ ssv[f"vdp-{doc[x[0]].i}"].update ({"type":"vdp","lem":doc[x[0]].lemma_,"chunk":doc[x[0]].lemma_+' '+doc[x[1]].lemma_+' '+doc[x[2]].lemma_, })
			for name, x in depmatchers['vdp'](doc) ]
		[ ssv[f"vnp-{doc[x[0]].i}"].update ({"type":"vnp","lem":doc[x[0]].lemma_,"chunk":doc[x[0]].lemma_+' '+doc[x[1]].lemma_+' '+doc[x[2]].lemma_, })
			for name, x in depmatchers['vnp'](doc) ]
		[ ssv[f"vnpn-{doc[x[0]].i}"].update ({"type":"vnpn","lem":doc[x[0]].lemma_,"chunk":doc[x[0]].lemma_+' '+doc[x[1]].text.lower()+' '+doc[x[2]].text.lower()+' '+doc[x[3]].text.lower(), })
			for name, x in depmatchers['vnpn'](doc) ]
		[ ssv[f"vppn-{doc[x[0]].i}"].update ({"type":"vppn","lem":doc[x[0]].lemma_,"chunk":doc[x[0]].lemma_+' '+doc[x[1]].text.lower()+' '+doc[x[2]].text.lower()+' '+doc[x[3]].text.lower(), })
			for name, x in depmatchers['vppn'](doc) ]
		[ ssv[f"vpnpn-{doc[x[0]].i}"].update ({"type":"vpnpn","lem":doc[x[0]].lemma_,"chunk":doc[x[0]].lemma_+' '+doc[x[1]].text.lower()+' '+doc[x[2]].text.lower()+' '+doc[x[3]].text.lower()+' '+doc[x[4]].lemma_, })
			for name, x in depmatchers['vpnpn'](doc) ]
	except Exception as e:
		print ( "ex:", e) 
		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		traceback.print_tb(exc_traceback_obj)

	for k,v in ssv.items():
		doc.user_data[k] = v 

if __name__ == "__main__":  
	doc = spacy.nlp("I am happy with the box.")
	attach(doc)
	print (doc.user_data) 

'''
from nlp import terms 
terms.attach(doc) 

#from verbnet import submit_verbnet  # added 2022.2.11
def id_source(sid, doc):
	ssv = defaultdict(dict)
	es_source(sid, doc, ssv)
	submit_verbnet(sid, doc, ssv) # added 2022.2.11
	return ssv

#{"_id": "140948871-9", "_source": {"rid": "10", "uid": "25110374", "sc": 14, "md5": "da891a7d81f7a5e43b571168cc483b6c dba0b4c99ef37cadfc4bacd61fcefa5b d6b199bfae35246564c598ac78d84c91 38a945eeff5b5a587a26dcc6560e0061 58605af6b50b01f15c0cc3ee2aa75e33 c30566c355ae09ea68673e2940d49d0a 7972c906aef51380310363093e141ef8 dabdd545400415da6d29125bf872"}}

curl -H "Content-Type: application/json" -XPOST "localhost:9200/how2java/product/_bulk?refresh" --data-binary "@products.json"

{ "index" : { "_index" : "zhouls", "_type" : "user", "_id" : "6" } }
{ "name" : "mayun" , "age" : "51" }
{ "update" : { "_index" : "zhouls", "_type" : "user", "_id" : "6" } }
{ "doc" : { "age" : 52 }}

$ cat requests
{ "index" : { "_index" : "test", "_id" : "1" } }
{ "field1" : "value1" }
$ curl -s -H "Content-Type: application/x-ndjson" -XPOST localhost:9200/_bulk --data-binary "@requests"; echo
{"took":7, "errors": false, "items":[{"index":{"_index":"test","_id":"1","_version":1,"result":"created","forced_refresh":false}}]}
'''