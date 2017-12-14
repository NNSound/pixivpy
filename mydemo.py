from pixivpy3 import *
import os
import pprint 


path = "C:/Users/wl019/Pictures/pixiv/DailyTop/"
directory = path+"1214"
if not os.path.exists(directory):
        os.makedirs(directory)


papi = PixivAPI()
aapi = AppPixivAPI()
papi.login(username="hwt30911@yahoo.com.tw",password="wl01994570")
json_result = papi.ranking_all()
#pprint.pprint (json_result.response[0].works[0].work.image_urls.large)

for row in json_result.response[0].works:
    url = row.work.image_urls.large
    print (url)
    aapi.download(url,path=directory)