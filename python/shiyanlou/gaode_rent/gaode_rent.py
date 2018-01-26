from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import csv

url='http://bj.58.com/pinpaigongyu/pn/{page}/?minprice=2000_4000&PGTID=0d3111f6-0000-1d5d-e51f-66e0c1dce691&ClickID=1'
page=0

csv_file=open('rent.csv','w')
csv_writer=csv.writer(csv_file,delimiter=',')

while True:
    page+=1
    print("fetch:"+url.format(page=page))
    response=requests.get(url.format(page=page))
    html=BeautifulSoup(response.text,'lxml')
    house_list=html.select(".list > li")

    if not house_list:
        break

    for house in house_list:
        house_title=house.select("h2")[0].string
        house_url=urljoin(url,house.select("a")[0]["href"])
        house_info_list=house_title.split()

        #判断公寓名称
        '''
        if '公寓' in house_info_list[1] or '青年社区' in house_info_list[1]:
            house_location=house_info_list[0]
        else:
            house_location=house_info_list[1]
        '''
        house_type=house_info_list[0][:4]
        house_location=house_info_list[0][4:]

        house_money=house.select(".money")[0].select("b")[0].string
        csv_writer.writerow([house_title,house_type,house_location,house_money,house_url])
csv_file.close()

