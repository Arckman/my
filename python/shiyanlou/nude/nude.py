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
                    _skin=self.skin_map[_id-1]._replace(region=len(self.detected_regions))
                    self.skin_map[_id-1]=_skin
                    self.detected_regions[_id-1].append([self.skin_map[_id-1]])
                elif region!=None:
                    _skin=self.skin_map[_id-1]._replace(region=region)
                    self.skin_map[_id-1]=_skin
                    self.detected_regions[region].append(self.skin_map[_id-1])

        #遍历后所有像素之后，每个像素已经归属region，但是self.merge_regions里还有待合并的region
        self._merge(self.detected_regions,self.merge_regions)
        self._analyse_regions()
        return self
    
    def _classify_skin(self,r,g,b):
        '''
        检测像素是否为皮肤，可以修正效果
        '''
        #RGB模式判定
        rgb_classifier = r >95 and g >40 and g<100 and b>20 and \
            max([r,g,b])-min([r,g,b])>15 and \
            abs(r-g)>15 and \
            r>g and r>b
        nr,ng,nb=self._to_normalized(r,g,b)
        norm_rgb_classifier=nr/ng>1.185 and \
            float(r*b)/((r+g+b)**2)>0.107 and \
            float(r*g)/((r+g+b)**2)>0.112
        
        #HSV模式判定
        h,s,v=self._to_hsv(r,g,b)
        hsv_classifier=h>0 and h<35 and s>0.23 and s<0.68

        #YCbCr模式判定
        y,cb,cr=self._to_ycbcr(r,g,b)
        ycbcr_classifier=97.5<=cb<=142.5 and 134<=cr<=176

        return rgb_classifier or norm_rgb_classifier or hsv_classifier or ycbcr_classifier
        #return rgb_classifier
    
    def _to_normalized(self,r,g,b):
        if r==0:
            r=0.0001
        if g==0:
            g=0.0001
        if b==0:
            b=0.0001
        _sum=float(r+g+b)
        return [r/_sum,g/_sum,b/_sum]

    def _to_ycbcr(self,r,g,b):
        y=.299*r+.587*g+.114*b
        cb=128-0.168736*r-0.331364*g+0.5*b
        cr=128+0.5*r-0.418688*g-0.081312*b
        return y,cb,cr

    def _to_hsv(self,r,g,b):
        h=0
        _sum=float(r+g+b)
        _max=float(max([r,g,b]))
        _min=float(min([r,g,b]))
        diff=float(_max-_min)
        if _sum==0:
            _sum=0.0001
        if _max==r:
            if diff==0:
                h=sys.maxsize
            else:
                h=(g-b)/diff
        elif _max==g:
            h=2+((g-r)/diff)
        else:
            h=4+((r-g)/diff)
        h*=60
        if h<0:
            h+=360
        return [h,1.0-(3.0*(_min/_sum)),(1.0/3.0)*_max]

    def _add_merge(self,_from,_to):
        self.last_from=_from
        self.last_to=_to
        from_index,to_index=-1,-1   #self.merge_regions的索引值
        for index,region in enumerate(self.merge_regions):
            for r_index in region:
                if r_index ==_from:
                    from_index=index
                if r_index==_to:
                    to_index=index
        
        #分3种情况
        #_from and _to in self.merge_regions
        if from_index!=-1 and to_index!=-1:
            if from_index!=to_index:
                self.merge_regions[from_index].extend(self.merge_regions[to_index])
                del(self.merge_regions[to_index])
            return

        #none of _from and _to in self.merge_regions
        if from_index==-1 and to_index==-1:
            self.merge_regions.append([_from,_to])
            retrun

        #one of _from and _to in self.merge_regions
        if from_index!=-1 and to_index==-1:
            self.merge_regions[from_index].append(_to)
            return
        if from_index==-1 and to_index!=-1:
            self.merge_regions[to_index].append(_from)
            return

    def _merge(self,detected_regions,merge_regions):
        new_detected_regions=[] #皮肤区域列表，包含Skin对象列表，
        for index,regions in enumerate(merge_regions):
            new_detected_regions.append([])
            for r_index in regions:
                new_detected_regions[index].extend(detected_regions[r_index])
                detected_regions[r_index]=[]
        for region in detected_regions:
            if len(region)>0:
                new_detected_regions.append(region)
        self._clear_regions(new_detected_regions)

    def _clear_regions(self,detected_regions):
        '''
        只保存像素大于制定数量的皮肤区域？
        '''
        for region in detected_regions:
            if len(region)>30:
                self.skin_regions.append(region)
    
    def _analyse_regions(self):
        #皮肤区域小于3（阈值）时，不是色情图片
        if len(self.skin_regions)<3:
            self.message="Less than 3 skin regions ({_skin_regions_size})".format(_skin_regions_size=len(self.skin_regions))
            self.result=False
            return self.result

        self.skin_regions=sorted(self.skin_regions,key=lambda x :len(x),reverse=True)

        total_skin=float(sum([len(skin_region) for skin_region in self.skin_regions]))

        #如果皮肤区域与整个图像的比值小于15%，不是色情图片
        if total_skin/self.total_pixels*100<15:
            self.message="Total skin percentage less than 15 ({:.2f})".format(total_skin/self.total_pixels*100)
            self.result=False
            return self.result

        #如果最大皮肤区域小鱼总皮肤面积的45%，不是色情图片
        if len(self.skin_regions[0])/total_skin*100<45:
            self.message="The biggest region contains less than 45 ({:.2f})".format(len(self.skin_regions[0])/total_skin*100)
            self.result=False
            return self.result

        #皮肤区域数量超过60个，不是色情图片
        if len(self.skin_regions)>60:
            self.message="More than 60 skin regions ({})".format(len(self.skin_regions))
            self.result=False
            return self.result

        #其他情况为色情图片
        self.message="Nude!"
        self.result=True
        return self.result

    def inspect(self):
        _image="{} {} {}*{}".format(self.image.filename,self.image.format,self.width,self.height)
        return "{_image}: result={_result} message='{_message}'".format(_image=_image,_result=self.result,_message=self.message)

    def showSkinRegions(self):
        if self.result is Nonde:
            return 

        skinIdSet=set()
        simage=self.image
        simageData=simage.load()

        for sr in self.skin_regions:
            for pixel in sr:
                skinIdSet.add(pixel.id)
        
        for pixel in self.skin_map:
            if pixel.id not in skinIdSet:
                simageData[pixel.x,pixel.y]=0,0,0
            else:
                simageData[pixel.x,pixel.y]=255,255,255
        
        filePath=os.path.abspath(self.image.filename)
        fileDirecotry=os.path.dirname(filePath)+"/"
        fileFullname=os.path.basename(filePath)
        fileName,fileExtName=os.path.splitext(fileFullname)
        simage.save('{}{}_{}{}'.format(fileDirecotry,filename,'Nude' if self.result else 'Normal',fileExtName))
    
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Dectect Nudity in images.')
    parser.add_argument('files',metavar='image',nargs='+',help="Images you wish to test")
    parser.add_argument('-r','--resize',action='store_true',help="Reduce image size to increase speed of scanning")
    parser.add_argument('-v','--visualization',action='store_true',help="Generating areas of skin image")
    args=parser.parse_args()

    for fname in args.fies:
        if os.path.isfile(fname):
            n=Node(fname)
            if args.resize:
                n.resize(maxheight=800,maxwidth=600)
            n.parse()
            if args.visualization:
                n.showSkinRegions()
            print(n.result,n.inspect())
        else:
            print(fname,"is not a file")

        



                    
