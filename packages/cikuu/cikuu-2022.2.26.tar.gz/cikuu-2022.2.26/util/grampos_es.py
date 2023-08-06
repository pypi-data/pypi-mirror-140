#
import json, fire, sqlite3

def dump(dbfile, outfile):
	''' '''
	print(">> started:", dbfile, flush=True)
	conn = sqlite3.connect(dbfile)
	with open(outfile, 'w') as fw : 
		for row in conn.execute(f"select * from sv" ):
			try:
				arr = {"_id": f"{row[0]}", "_source": {"v": f"{row[1]}"}}
				fw.write(json.dumps(arr) + "\n") 
			except Exception as e:
				print("ex:", e, row[0])
	print(">> finished:", dbfile)

if __name__ == '__main__': 
	fire.Fire(dump) 

'''
PUT grampos
{
 "mappings": {
   "properties": { 
     "v":{"type": "keyword", "index":false }
	 }
 }
}
'''