#
import json, fire, redislite,sqlite3

r = redislite.Redis('./grampos.redislite')

def readline(infile, sepa=None):
	with open(infile, 'r') as fp:
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

def dump(infile):
	''' '''
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
