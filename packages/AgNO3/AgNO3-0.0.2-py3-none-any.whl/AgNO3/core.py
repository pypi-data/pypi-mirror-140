from requests import *
import re
from ua_info import *
import random
import time
from tqdm import *
import os


class WP_Spyder(object):

    def __init__(self):
        self.url = "https://wallhaven.cc/toplist"
        self.ua = {'User-Agent': random.choice(ua_list)}
        print(self.ua)

    def Break(self):
        time.sleep(random.choice([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]))
        
    def get_html(self, url): # 通过url获取html静态页面
        res = get(url, headers=self.ua)
        return res.text

    def refunc(self,bds,cont): # 通过正则匹配页面内的元素
        pp = re.compile(bds,re.S)
        rl = pp.findall(cont)
        return rl

    def getInnerHtml(self, url): # 分析里层页面，找到图片下载地址
        h2 = get(url,headers=self.ua)
        bds = '''<img id="wallpaper" src="(.*?)" alt='''
        imgurl = self.refunc(bds,h2.text)
        #print(imgurl)
        return imgurl

    def Download(self, url, name): # 下载并保存
        rr = get(url, headers=self.ua)
        with open(name,'wb') as img:
            img.write(rr.content)
            #print(f'{url[-10:-4]}.jpg download over.')

    def parse_html(self, url): # 分析外层页面，找到每一个图片的入口
        h1 = get(url,headers=self.ua).text
        bds = '''<a class="preview" href="(https://wallhaven.cc/w/\w{6})"  target="_blank"  ></a>'''
        imgList = self.refunc(bds, h1)
        #print(imgList)
        print(f'Find {len(imgList)} Images.')
        return imgList

    def run(self):
        for page in range(1, 10):
            os.makedirs(f"Image\\toplist\\{page}")
            files = os.listdir(f"Image\\toplist\\{page}")
            exists = [i.split('.')[0] for i in files]
            #创建文件夹并记录哪些文件以及下载过了
            #网络问题可能导致程序跑着就断了，下一次运行没必要全部重新下
            
            uurl = self.url+f'?page={page}'
            print('Page',page)
            imgList = self.parse_html(uurl)
            time.sleep(0.01)
            #print('\n'.join(imgList))
            b = tqdm(imgList)
            for imgPage in b:
                b.set_description("Downloading %s" % imgPage[-6:])
                if imgPage[-6:] in exists: # 已经下载过
                    print(imgPage[-6:],'already exists.')
                    continue
                
                self.Break()
                imgUrl = self.getInnerHtml(imgPage)[0]
                fn = f"Image\\toplist\\{page}\\{imgUrl[-10:-4]}.jpg"
                self.Download(imgUrl,fn)#[0])
            self.Break()


if __name__ == "__main__":
    spd = WP_Spyder()
    spd.run()
    #print(os.listdir())

