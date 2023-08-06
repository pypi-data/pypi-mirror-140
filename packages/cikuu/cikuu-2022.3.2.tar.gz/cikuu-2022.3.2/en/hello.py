#2022.2.17
from en import * 
from en import terms 
from en import verbnet 

doc = getdoc("The quick fox jumped over the lazy dog.")
terms.attach(doc) 
verbnet.attach(doc)
print(doc.user_data)