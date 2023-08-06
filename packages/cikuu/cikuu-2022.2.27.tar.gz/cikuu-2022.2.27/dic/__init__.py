# 2021-2-6
import zipfile, pathlib,json

essay = '''   English is a internationaly language which becomes importantly for modern world.
    In China, English is took to be a foreigh language which many student choosed to learn. They begin to studying English at a early age. They use at least one hour to learn English knowledges a day. Even kids in kindergarten have begun learning simple words. That's a good phenomenan, for English is essential nowadays.
    In addition to, some people think English is superior than Chinese. In me opinion, though English is for great significance, but English is after all a foreign language. it is hard for people to see eye to eye. English do help us read English original works, but Chinese helps us learn a true China. Only by characters Chinese literature can send off its brilliance. Learning a country's culture, especial its classic culture, the first thing is learn its language. Because of we are Chinese, why do we give up our mother tongue and learn our owne culture through a foreign language?'''

def readline(infile, sepa=None):
	with open(infile, 'r') as fp:
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

def word_level(): 
	''' {"w":"awl", "w2": "gsl1", "e3":"gsl2"} '''
	from dic import word_awl, word_gsl1, word_gsl2
	dic = {}
	[dic.update({w:"gsl1"}) for w in word_gsl1.word_gsl1]
	[dic.update({w:"gsl2"}) for w in word_gsl2.word_gsl2]
	[dic.update({w:"awl"}) for w in word_awl.word_awl]
	return dic

def readzip(name): # file endswith '.zip'
	z = zipfile.ZipFile( pathlib.Path(__file__).parent / f"{name}.zip" , 'r') 
	lines = z.read(z.namelist()[0]) #bytes 
	return lines.decode().strip().split("\n") #["'tween", "'tween decks", 'a.d.', 'a.k.a.', 'a.m.', 'aback', 'abaft'

def dm_essay(infile = '230537'): # 230537, [ {}, {}]
	lines = readzip(infile)
	return [ json.loads(line.strip().replace(': null, "',': 0, "'))  for line in lines ]

loadset = lambda name="verblist": { w.strip() for w in readzip( name ) if w } # one word, one line 
loadss = lambda name="ecdic": { line.split('\t')[0].strip():line.split('\t')[1].strip()  for line in readzip(name) if line } # s -> s , ecdic 

if __name__ == '__main__':
	print (dm_essay())

def word_map(chunk, idx , attr):  # by academic . | 1 | jj_to_nn 
	toks = chunk.split()
	w = toks[idx]
	toks[idx] = word_attr.get(w, {}).get(attr, '*' + attr)	
	return ' '.join(toks)

def word_attr_add(word, attr, val):
	if word in word_attr : 
		word_attr[word].update({attr:val})
	else :
		word_attr[word] = {attr:val}

stop_dobj_v = lambda : {'have','be','do','get'}
stop_dobj_n = lambda : {'thing'}
#map(f, iterable) ==> [f(x) for x in iterable]

def normalize(dct):
	v_sum = sum(dct.values()) + 1
	return { k:100*v/v_sum for k,v in dct.items()}

def code_dict(filename): 
	print (filename.split(".")[0] + " = {")
	for line in readlines(filename):
		if '"' in line:
			continue
		k,v = line.strip("\n").split("\t")  # one two:2,three:3
		print('"' + k  + '":{"' + v.replace(':','":').replace(',',',"') +"},")
	print ("}")
		
def readlines(filename):
	with open(filename, "r") as fp:
		return fp.readlines()