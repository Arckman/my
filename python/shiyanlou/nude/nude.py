import sys
import os
import _io  #built-in module
from collections import namedtuple
from PIL import Image

Skin=namedtuple("Skin","id skin region x y")

class Nude:
    def __init__(self,path_or_image):
        if isinstance(path_or_image,Image.Image):
            self.image=path_or_image
        elif isinstance(path_or_image,str):
            self.image=Image.open(path_or_image)
        assert isinstance(self.image,Image.Image)
        bands=self.image.getbands()
        if len(bands)==1:
            #new a RGB pic from gray and paste
            new_img=Image.new('RGB',self.image.size)
            new_img.paste(self.image)
            f=self.image.filename
            self.image=new_img
            self.image.filename=f
        像素对应的Skin对象
        self.skin_map=[]
        #检测到的所有皮肤区域，索引号就是皮肤区域编号，值为Skin对象列表
        self.detected_regions=[]
        #待合并的皮肤区域编号列表
        self.merge_regions=[]
        #整合后的皮肤区域，索引号是皮肤区域编号，值为Skin对象列表
        self.skin_regions=[]
        #最近正好的皮肤区域编号，初始化为-1
        self.last_from,self.last_to=-1,-1
        #result
        self.result=None
        #
        self.message=None
        #height,width
        self.width,self.height=self.image.size
        #total pixels
        self.total_pixels=self.width*self.height

    def resize(self,maxwidth=1000,maxheight=1000):
        '''
        基于长宽比缩小图片
        注：可能影响结果
        如果图片没有变化，返回0
        宽度大于maxwidth，返回1
        长度大于maxheight，返回2
        长宽都大于最大值，返回3
        '''
        ret=0
        if maxwidth:
            if self.image.width>maxwidth:
                wpercent=maxwidth/self.image.width
                h=int(self.image.height*wpercent)
                fname=self.image.filename
                #Image.LANCZOS 重采样滤波器，用于抗锯齿
                self.image=self.image.resize((maxwidth,h),Image.LANCZOS)
                self.image.filename=fname
                self.width,self.height=self.image.size
                self.total_pixels=self.width*self.height
                ret+=1
        if maxheight:
            if self.image.height>maxheight:
                hpercent=maxheight/self.image.height
                w=int(self.image.width*hpercent)
                fname=self.image.filename
                self.image=self.image.resize((w,maxheight),Image.LANCZOS)
                self.image.filename=fname
                self.width,self.height=self.image.size
                self.total_pixels=self.width*self.height
                ret+=2
        return ret

    def parse(self):
        if self.result is not None:
            return self
        
        #针对每个pixel创建Skin对象
        pixels=self.image.load()
        for y in self.height:
            for x in self.width:
                r,g,b=pixels[x,y]
                #判断是否肤色像素
                isSkin=True if self._classify_skin(r,g,b) else False
                #id for pixel
                _id=x+1+y*self.width
                self.skin_map.append(Skin(_id,isSkin,None,x,y))
                
                if not isSkin:
                    continue
                
                #检查4个相邻位置是否isSkin，并添加区域
                check_indexes=[_id-1-1, #left
                _id-1-self.width-1, #up and left
                _id-1-self.width,   #up
                _id-1-self.width+1] #up and right
                region_id=1
                for index in check_indexes:
                    try:
                        self.skin_map[index]
                    except:
                        continue    #break?
                    if self.skin_map[index].skin:
                        if (self.skin_map[index].region!=None and
                        region!=None and region!=-1 and
                        self.skin_map[index].region!=region and
                        self.last_from!=region and 
                        self.last_to!=self.skin_map[index].region):
                            #像素相邻的像素点属于多个region时，需要将这几个region进行合并
                            self._add_merge(region,self.skin_map[index].region)
                        region=self.skin_map[index].region
                
                #遍历完4个相邻像素，如果region=-1，说明周围没有有效的region;如果region!=-1，说明周围存在有效的region，将当前像素纳入到该region中。
                if region==-1:
                    

                    
