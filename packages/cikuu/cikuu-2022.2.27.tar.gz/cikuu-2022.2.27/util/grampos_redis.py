#
import json, fire, redis,sqlite3

def readline(infile, sepa=None):
	with open(infile, 'r') as fp:
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

def dump(infile):
	''' '''
	r	= redis.Redis(host='127.0.0.1', port=9221, db=0, decode_responses=True)
	print(">> started:", infile, r, flush=True)
	for line in readline(infile):
		try:
			arr = line.strip().split("\t")
			r.set(arr[0].strip(), arr[1].strip())
		except Exception as e:
			print("ex:", e, line)
	print(">> finished:", infile)

if __name__ == '__main__': 
	fire.Fire(dump) 

'''
def dump(dbfile):
	r	= redis.Redis(host='127.0.0.1', port=9221, db=0, decode_responses=True)
	print(">> started:", dbfile, r, flush=True)
	conn = sqlite3.connect(dbfile)
	for row in conn.execute(f"select * from sv" ):
		try:
			r.set(row[0], row[1])
		except Exception as e:
			print("ex:", e, row[0])
	print(">> finished:", dbfile)
'''