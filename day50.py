from pixivpy3 import *
import os

path = "C:/Users/wl019/Pictures/pixiv/DailyTop/"
directory = path+"1111"
if not os.path.exists(directory):
        os.makedirs(directory)

papi=PixivAPI()
aapi = AppPixivAPI()
aapi.illust_follow()
a= aapi.illust_follow()
print (a)