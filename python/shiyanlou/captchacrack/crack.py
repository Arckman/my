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

import time
count =0
t=time.time()
for letter in letterrange:
    im3=im2.crop((letter[0],0,letter[1],im2.size[1]))
    im3.save("./img/%f-%d.gif"%(t,count))
    count+=1

