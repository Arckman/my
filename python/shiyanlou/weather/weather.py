#data:http://labfile.oss.aliyuncs.com/courses/780/WeatherData.zip
import pandas as pd
import numpy as np
import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser

df_asti=pd.read_csv("WeatherData/asti_270615.csv")
df_bologna=pd.read_csv("WeatherData/bologna_270615.csv")
df_cesena=pd.read_csv("WeatherData/cesena_270615.csv")
df_faenza=pd.read_csv("WeatherData/faenza_270615.csv")
df_ferrara=pd.read_csv("WeatherData/ferrara_270615.csv")
df_mantova=pd.read_csv("WeatherData/mantova_270615.csv")
df_milano=pd.read_csv("WeatherData/milano_270615.csv")
df_piacenza=pd.read_csv("WeatherData/piacenza_270615.csv")
df_ravenna=pd.read_csv("WeatherData/ravenna_270615.csv")
df_torino=pd.read_csv("WeatherData/torino_270615.csv")

#subplots函数，fig是图像，ax是坐标轴对象
fig,ax=plt.subplots(3,4)
#调整x轴坐标刻度，旋转70度，方便查看
plt.xticks(rotation=70)

'''
plot1:画温度plot,3个离海最近的城市和3个离海最远的城市
'''
#读取温度数据
y1=df_ravenna['temp']
x1=df_ravenna['day']
y2=df_faenza['temp']
x2=df_faenza['day']
y3=df_cesena['temp']
x3=df_cesena['day']
y4=df_milano['temp']
x4=df_milano['day']
y5=df_asti['temp']
x5=df_asti['day']
y6=df_torino['temp']
x6=df_torino['day']
#将日期格式转成datetime格式
day_ravenna=[parser.parse(x) for x in x1]
day_faenza=[parser.parse(x) for x in x2]
day_cesena=[parser.parse(x) for x in x3]
day_milano=[parser.parse(x) for x in x4]
day_asti=[parser.parse(x) for x in x5]
day_torino=[parser.parse(x) for x in x6]

#调整时间格式
hours=mdates.DateFormatter("%H:%M")

#设置x轴显示格式
ax[0,0].xaxis.set_major_formatter(hours)

#画出图像，day_milano是x轴数据，y1是y轴数据，r代表红色
ax[0,0].plot(day_ravenna,y1,'r',day_faenza,y2,'r',day_cesena,y3,'r')
ax[0,0].plot(day_milano,y4,'g',day_asti,y5,'g',day_torino,y6,'g')


'''
plot2:画温度最值和离海距离的图
'''
#dist
dist=[df_ravenna['dist'][0],
    df_cesena['dist'][0],
    df_faenza['dist'][0],
    df_ferrara['dist'][0],
    df_bologna['dist'][0],
    df_mantova['dist'][0],
    df_piacenza['dist'][0],
    df_milano['dist'][0],
    df_asti['dist'][0],
    df_torino['dist'][0]]
#max temp
temp_max=[df_ravenna['temp'].max(),
    df_cesena['temp'].max(),
    df_faenza['temp'].max(),
    df_ferrara['temp'].max(),
    df_bologna['temp'].max(),
    df_mantova['temp'].max(),
    df_piacenza['temp'].max(),
    df_milano['temp'].max(),
    df_asti['temp'].max(),
    df_torino['temp'].max()]
#min temp                                                                                                                                                                                               
temp_min=[df_ravenna['temp'].min(),
    df_cesena['temp'].min(),
    df_faenza['temp'].min(),
    df_ferrara['temp'].min(),
    df_bologna['temp'].min(),
    df_mantova['temp'].min(),
    df_piacenza['temp'].min(),
    df_milano['temp'].min(),
    df_asti['temp'].min(),
    df_torino['temp'].min()]

ax[0,1].plot(dist,temp_max,'ro')

#线性回归计算
from sklearn.svm import SVR

dist1=dist[:5]
dist2=dist[5:]
dist1=[[x] for x in dist1]
dist2=[[x] for x in dist2]

temp_max1=temp_max[:5]
temp_max2=temp_max[5:]

#创建线性拟合
svr_lin1=SVR(kernel='linear',C=1e3)
svr_lin2=SVR(kernel='linear',C=1e3)
#加入数据
svr_lin1.fit(dist1,temp_max1)
svr_lin2.fit(dist2,temp_max2)

xp1=np.arange(10,100,10).reshape((9,1))
xp2=np.arange(50,400,50).reshape((7,1))
yp1=svr_lin1.predict(xp1)
yp2=svr_lin2.predict(xp2)

ax[0,1].set_xlim(0,400)
ax[0,1].plot(xp1,yp1,c='b',label='Strong sea effect')
ax[0,1].plot(xp2,yp2,c='g',label='Light sea effect')

print(svr_lin1.coef_,svr_lin1.intercept_)
print(svr_lin2.coef_,svr_lin2.intercept_)

'''
plot3:线性回归直线交点
'''
from scipy.optimize import fsolve
#第一条拟合直线
def line1(x):
    a1=svr_lin1.coef_[0][0]
    b1=svr_lin1.intercept_[0]
    return a1*x+b1

#第二条拟合直线
def line2(x):
    a2=svr_lin2.coef_[0][0]
    b2=svr_lin2.intercept_[0]
    return a2*x+b2

#计算两条线交点
def findIntersection(fun1,fun2,x0):
    return fsolve(lambda x:fun1(x)-fun2(x),x0)

result=findIntersection(line1,line2,0.0)
print("[x,y]=[%d,%d]"%(result,line1(result)))
x=np.linspace(0,300,31)
ax[0,2].plot(x,line1(x),x,line2(x),result,line1(result),'ro')

'''
plot4:最低温度和离海距离
'''
ax[0,3].axis((0,400,15,25))
ax[0,3].plot(dist,temp_min,'bo')

'''
plot5:湿度数据分析
'''
y1=df_ravenna['humidity']
y2=df_faenza['humidity']
y3=df_cesena['humidity']
y4=df_milano['humidity']
y5=df_asti['humidity']
y6=df_torino['humidity']
ax[1,0].xaxis.set_major_formatter(hours)
ax[1,0].plot(day_ravenna,y1,'r',day_faenza,x2,'r',day_cesena,x3,'r')
ax[1,0].plot(day_milano,x4,'g',day_asti,x5,'g',day_torino,x6,'g')

'''
plot6:湿度最大值和离海距离
'''
hum_max=[df_ravenna['humidity'].max(),
    df_cesena['humidity'].max(),
    df_faenza['humidity'].max(),
    df_faenza['humidity'].max(),
    df_bologna['humidity'].max(),
    df_mantova['humidity'].max(),
    df_piacenza['humidity'].max(),
    df_milano['humidity'].max(),
    df_asti['humidity'].max(),
    df_torino['humidity'].max()]
ax[1,1].plot(dist,hum_max,'bo')

'''
plot7:湿度最小值和离海距离
'''
hum_min=[df_ravenna['humidity'].min(),
    df_cesena['humidity'].min(),
    df_faenza['humidity'].min(),
    df_faenza['humidity'].min(),
    df_bologna['humidity'].min(),
    df_mantova['humidity'].min(),
    df_piacenza['humidity'].min(),
    df_milano['humidity'].min(),
    df_asti['humidity'].min(),
    df_torino['humidity'].min()]
ax[1,2].plot(dist,hum_min,'bo')

'''
plot8:ravenna风力信息图
'''
ax[1,3].plot(df_ravenna['wind_deg'],df_ravenna['wind_speed'],'ro')

'''
plot9:ravenna风力极区图
'''
def showRoseWind(value,city_name,max_value,plot_index):
    N=8
    theta=np.arange(0.,2*np.pi,2*np.pi/N)
    radii=np.array(value)
    #构建极区图的坐标系
    # _axes=plt.axes([0.025,0.025,0.95,0.95],polar=True)
    ax[plot_index[0],plot_index[1]].axis((0.025,0.025,0.95,0.95))
    #设置颜色，x越大，越接近蓝色
    colors=[(1-x/max_value,1-x/max_value,0.75) for x in radii]
    #画扇区
    # _axes.bar(theta,radii,width=(2*np.pi/N),bottom=0.0,color=colors)
    ax[plot_index[0],plot_index[1]].bar(theta,radii,width=(2*np.pi/N),bottom=0.0,color=colors)
    #设置标题
    # _axes.set_title(city_name,x=0.2,fontsize=20)
    ax[plot_index[0],plot_index[1]].set_title(city_name,x=0.2,fontsize=20)


hist,bin=np.histogram(df_ravenna['wind_deg'],8,[0,360])
print([hist,bin])
showRoseWind(hist,'Ravenna',max(hist),(2,0))

'''
plot10:ferrara风力极区图
'''
hist,bin=np.histogram(df_ferrara['wind_deg'],8,[0,360])
print([hist,bin])
showRoseWind(hist,'Ferrara',max(hist),(2,1))

'''
plot11:ferrara平均风力极区图
'''
def roseWind_avgSpeed(df_city):
    degs=np.arange(45,361,35)
    tmp=[]
    for deg in degs:
        tmp.append(df_city[(df_city['wind_deg']>(deg-46)) & (df_city['wind_deg']<deg)]['wind_speed'].mean())
    return np.array(tmp)
# showRoseWind(roseWind_avgSpeed(df_ferrara),'Ferrara',max(hist),(2,2))

#显示图像
plt.show()

