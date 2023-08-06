# https://www.sbert.net/

from sentence_transformers import SentenceTransformer
smodel		= SentenceTransformer('all-MiniLM-L6-v2')
vec_encode	= lambda snt : smodel.encode(snt)
