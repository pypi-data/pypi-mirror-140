# 2022.3.3  uvicorn annotate:app --host 0.0.0.0 --port 18000 --reload
import json,requests,hashlib,os
from uvirun import * 
from en import nlp 
from en.terms import *

os.dskurl = os.getenv('dskurl',"gpu120.wrask.com:9102")

@app.get('/annotate/phrase')
def annotate_phrase(text="I think that I am going to go to the cinema. The quick fox jumped over the lazy dog.", classes:str="NP,VP,AP"):  
	''' {"classes":["NP","NP2"],"annotations":[["Terrible customer service.",{"entities":[[0,17,"NP2"],[18,25,"NP"]]}], ''' 
	doc = nlp(text) 
	spans = [ [doc[np.start].idx, doc[np.start].idx + len(np.text), "NP"] for np in doc.noun_chunks if np.end - np.start > 1]
	for name, ibeg,iend in matchers['ap'](doc) :
		spans.append( [doc[ibeg].idx, doc[ibeg].idx + len(doc[ibeg:iend].text), "AP"] )
	for name, ibeg,iend in matchers['vp'](doc) :
		spans.append( [doc[ibeg].idx, doc[ibeg].idx + len(doc[ibeg:iend].text), "VP"] )
	return {"classes":classes.strip().split(','), "annotations":[[text,{"entities":spans}]] }

@app.get('/annotate/pos')
def annotate_pos(text="I think that I am going to go to the cinema. The quick fox jumped over the lazy dog.", classes:str="VERB,NOUN,ADJ,ADV"):  
	''' {"classes":["NP","NP2"],"annotations":[["Terrible customer service.",{"entities":[[0,17,"NP2"],[18,25,"NP"]]}], ''' 
	doc = nlp(text) 
	pos = classes.strip().split(",")
	spans = [ [t.idx, t.idx + len(t.text), t.pos_] for t in doc if t.pos_ in pos]
	return {"classes":pos,"annotations":[[text,{"entities":spans}]] }

@app.get('/annotate/clause')
def annotate_clause(text="I think that I am going to go to the cinema. What I think is right.", classes:str="ccomp,subcl,csubj,xcomp"):  
	''' {"classes":["NP","NP2"],"annotations":[["Terrible customer service.",{"entities":[[0,17,"NP2"],[18,25,"NP"]]}], ''' 
	doc = nlp(text) 
	spans = []
	for v in [t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT' ] : # non-root
		children = list(v.subtree)
		start = children[0].i  	#end = children[-1].i 
		cl = " ".join([c.text for c in v.subtree])
		spans.append ([doc[start].idx, doc[start].idx + len(cl), v.dep_])
	return {"classes":classes.strip().split(','),"annotations":[[text,{"entities":spans}]] }

@app.get('/annotate/non_pred_verb')
def annotate_non_pred_verb(text="I think that I am going to go to the cinema. It is sunken.", classes:str="vtov,VBN,vvbg"):  
	''' {"classes":["NP","NP2"],"annotations":[["Terrible customer service.",{"entities":[[0,17,"NP2"],[18,25,"NP"]]}], ''' 
	doc = nlp(text) 
	spans = [ [t.idx, t.idx + len(t.text), "VBN"] for t in doc if t.tag_ == 'VBN']
	for name, ibeg,iend in matchers['vtov'](doc) :
		spans.append( [doc[ibeg].idx, doc[ibeg].idx + len(doc[ibeg:iend].text), "vtov"] )
	for name, ibeg,iend in matchers['vvbg'](doc) :
		spans.append( [doc[ibeg].idx, doc[ibeg].idx + len(doc[ibeg:iend].text), "vvbg"] )
	return {"classes":classes.strip().split(','),"annotations":[[text,{"entities":spans}]] }

@app.get('/annotate/stype')
def annotate_stype(text="I think that I am going to go to the cinema. What I think is right."):  #, classes:str="simple,complex,compound"
	''' {"classes":["NP","NP2"],"annotations":[["Terrible customer service.",{"entities":[[0,17,"NP2"],[18,25,"NP"]]}], ''' 
	doc = nlp(text)
	stags = []
	for sent in doc.sents:
		spans = []
		sdoc = sent.as_doc()
		spans.append ("simple" if len([t for t in sdoc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 else "complex" )
		if len([t for t in sdoc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0:
			spans.append('compound')
		stags.append( {"start":sent.start, "end":sent.end, "sent": sent.text, "stags": spans })
	return stags
	
feedbacks = lambda dic :  [ v for k,v in dic['feedback'].items() ]
@app.get("/annotate/feedback")
def dsk_feedback(text:str="The quick fox jumped over the lazy dog. The justice delayed is justice denied."):
	''' '''
	dsk = requests.post(f"http://{os.dskurl}/essay/gecdsk", json={"rid":"10", "key": hashlib.md5(text.encode("utf-8")).hexdigest(), "essay":text}).json()
	return  [ ( dic.get('meta',{}).get('snt',''), feedbacks(dic) ) for dic in dsk['snt']]

if __name__ == "__main__":  
	print(dsk_feedback())