import os
import time
import m3u8
import requests
from glob import iglob
from natsort import natsorted
from urllib.parse import urljoin
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
 
 
@dataclass
class DownLoad_M3U8(object):
    m3u8_url  : str
    file_name : str
 
    def __post_init__(self):
        #self.headers   = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',}
        self.headers   = {'Upgrade-Insecure-Requests': 1, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',}
        self.threadpool = ThreadPoolExecutor(max_workers=10)
        if not self.file_name:
            self.file_name = 'new.mp4'
 
    def get_ts_url(self):
        m3u8_obj = m3u8.load(self.m3u8_url)
        base_uri = m3u8_obj.base_uri
 
        for seg in m3u8_obj.segments:
            yield urljoin(base_uri,seg.uri)
            
    def download_single_ts(self,urlinfo):
        url,ts_name = urlinfo
        res = requests.get(url,headers = self.headers)
        with open(ts_name,'wb') as fp:
            fp.write(res.content)
    
 
    def download_all_ts(self):
        ts_urls = self.get_ts_url()
        for index,ts_url in enumerate(ts_urls):
            print (ts_url)
            self.threadpool.submit(self.download_single_ts,[ts_url,f'{index}.ts'])
        self.threadpool.shutdown()
 
    def run(self):
        self.download_all_ts()
        ts_path = '*.ts'
        with open(self.file_name,'wb') as fn:
            for ts in natsorted(iglob(ts_path)):
                with open(ts,'rb') as ft:
                    scline = ft.read()
                    fn.write(scline)
        for ts in iglob(ts_path):
            os.remove(ts)
 
if __name__ == '__main__':
    
    m3u8_url  = 'http://vod2.xiaoe-tech.com/9764a7a5vodtransgzp1252524126/39b094d55285890789702775124/drm/v.f230.m3u8?t=5db31647&us=917564&sign=e8952e35abada98cf2bb762bfbb44c8a'
    file_name = '1.mp4'
 
    start = time.time()
 
    M3U8 = DownLoad_M3U8(m3u8_url,file_name)
    M3U8.run()
 
    end = time.time()
    print ('耗时:',end - start)
