import os,sys
import jieba,codecs,math
import jieba.posseg as pseg

names={} #姓名字典{姓名:occurrence number}
relationships={}    #关系字典{ egde-sourcename:{egde-targetname:weight}}
lineNames=[]    #每个段里的姓名

#get all names
jieba.load_userdict("dict.txt")
with codecs.open("Train to Busan.txt",'r','utf8') as f:
    for line in f.readlines():
        poss=pseg.cut(line)
        lineNames.append([])
        for w in poss:
            if w.flag!='nr' or len(w.word)<2:
                continue
            lineNames[-1].append(w.word)
            if names.get(w.word) is None:
                names[w.word]=0
                relationships[w.word]={}
            names[w.word]+=1

#show 
for name,times in names.items():
    print(name,times)

#connection
for line in lineNames:
    for name1 in line:
        for name2 in line:
            if name1==name2:
                continue
            elif relationships[name1].get(name2) is None:
                relationships[name1][name2]=1
            else:
                relationships[name1][name2]+=1
        
#filter,output
with codecs.open('busan_node.txt','w','utf8') as f:
    f.write('Id\tLabel\tWeight\r\n')
    for name,times in names.items():
        f.write(name+'\t'+name+'\t'+str(times)+'\r\n')

with codecs.open('busan_edge.txt','w','utf8') as f:
    f.write('Source\tTarget\tWeight\r\n')
    for name,edges in relationships.items():
        for v,w in edges.items():
            if w>3:
                f.write(name+'\t'+v+'\t'+str(w)+'\r\n')




