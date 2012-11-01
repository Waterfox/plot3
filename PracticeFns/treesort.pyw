import json

revcatset = [[u'string', u'cats', u'robots'], [u'multistring', u'sheep', u'dogs'], [u'multinumber', u'sheep', u'dogs', u'cats']]
index = []


class node(object):
    parents = []
    children = []
    def addParent(self,p):
        node.parents.append(p)
    
    def addChild(self,c):
        node.children.append(c)
    
    
#cats = node()
#cats.addParent('robots')
#cats.addChild('string')
index = []
def add_to_nodes(index,child,parent,level):
    for entry in index:
        if entry[0] == parent:
            if child not in entry[1]:
                entry[1].append(child)
                if level > entry[2]:
                    entry[2] =level
                return
            else:
                return
    index.append([parent,[child],level])

maxL = 0
for el in revcatset:
    if len(el)-1>maxL:
        maxL=len(el)-1
    for i in range(len(el)-1):
        add_to_nodes(index,el[i],el[i+1],i)

#print index

#for i in xrange(maxL):
#    for item in index:
#lowest = [{'name':revcatset[0][0],'size':1000},{'name':revcatset[1][0],'id':1000},{'name':revcatset[2][0],'size':1000}]
#lower = [{'name':revcatset[0][1],'children':lowest},{'name':revcatset[0][1],'children':lowest}]
#low = {'name':'Robbie Data','children':lower}        
#
#print low['children'][0]['children'][2]
for i in xrange(maxL):
    parents=[]
    for item in index:
        children = []
        if item[2] == i: 
            for name in item[1]:
                children.append({'name':name})
        parents.append({'name':item[0],'children':children})
#print children

print parents  
    