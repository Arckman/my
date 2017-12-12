from PIL import Image

im=Image.open("captcha.gif")
assert isinstance(im,Image.Image)
im.convert("P")
'''
#checkout key color from histogram
his=im.histogram()
values={}
for i in range(256):
    values[i]=his[i]
for j,k in sorted(values.items(),key=lambda x:x[1],reverse=True)[:10]:
    print(j,k)
'''
#im2 is a filter image of im,filtering background
im2=Image.new("P",im.size,255)
for y in range(im.size[1]):
    for x in range(im.size[0]):
        pix=im.getpixel((x,y))
        if pix==220 or pix==227: #focus on key color value
            im2.putpixel((x,y),0)
# im2.show()
# print(im2.size)

#cut out numbers from picture
inletter=False
foundletter=False
start,end=0,0
letterrange=[]
for x in range(im2.size[0]):
    for y in range(im2.size[1]):
        pix=im2.getpixel((x,y))
        if pix!=255:
            inletter=True
            break
    if foundletter==False and inletter==True:
        foundletter=True
        start=x
    if foundletter==True and inletter==False:
        foundletter=False
        end=x
        letterrange.append((start,end))
    inletter=False
# print(letterrange)


#a vector space search engine doc:http://ondoc.logand.com/d/2697/pdf
#vector space search engine is a simple function for computing the relativity/correlation of two vectors using cosine

import numpy as np
import math
#vector space search engine compute object
class VectorCompare:
    @staticmethod
    def buildvector(img):
        d1={}
        for i,v in enumerate(img.getdata()):
            d1[i]=v
        return d1

    @staticmethod
    def magnitude(concordance):
        total=0
        for word,count in concordance.items():
            total+=count**2
        return math.sqrt(total)

    @staticmethod
    def relation(concordance1,concordance2):
        '''
        compute cosine of two vectors, they must have the same size and sharp
        '''
        relevance,topvalue=0,0
        for word,count in concordance1.items():
            if word in concordance2.keys():
                topvalue+=count*concordance2[word]
        return topvalue/(VectorCompare.magnitude(concordance1)*VectorCompare.magnitude(concordance2))

#precompute vector space search engine training data
import string
import os
iconset=string.ascii_lowercase+string.digits
imageset=[] #trained data
for letter in iconset:
    tmp=[]
    for img in os.listdir("./iconset/%s/"%(letter)):
        if img != "Thumbs.db" and img != ".DS_Store":# windows check...
            tmp.append(VectorCompare.buildvector(Image.open("./iconset/%s/%s"%(letter,img))))
    imageset.append({letter:tmp})


import time
count =0
t=time.time()
for letter in letterrange:
    im3=im2.crop((letter[0],0,letter[1],im2.size[1]))
    # im3.save("./img/%f-%d.gif"%(t,count))
    # count+=1

    #now,compute relativity(cosine) using VectorCompare.relation()
    im3_vector=VectorCompare.buildvector(im3)
    guess=[]
    for image in imageset:
        for l,vector in image.items():
            guess.append((VectorCompare.relation(vector[0],im3_vector),l))
    guess.sort(reverse=True)
    print(guess[0])


