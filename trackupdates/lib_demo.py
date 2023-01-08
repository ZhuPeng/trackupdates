# -*- coding: utf-8 -*-

from trackupdates import Downloader, ListCrawl
import logging


# downloader = Downloader()
#
url = 'https://getyarn.io/yarn-find?text=what%20do%20you%20want%20from%20me&type=movies'
# res = downloader.get('https://getyarn.io/yarn-find?text=what%20do%20you%20want%20from%20me&type=movies', {})
#
# print res

logger = logging.getLogger()
logger.setLevel('DEBUG')

config = {
    'name': 'download_video',
    'url': {
        'target': url,
    },
    'parser_config': {
        'base_url': 'https://getyarn.io',
        'base_xpath': ["//div[@class='card tight bg-w']"],
        'attr': {
            'content': "a[2]/div",
            'url': 'a[1]/@href',
            'title': 'a[1]/div/div[1]',
        }
    }
}
crawl = ListCrawl(config)
crawl.run()

import requests

def downloadfile(name, url):
    name = name+".mp4"
    r = requests.get(url)
    print("****Connected****")
    f=open(name, 'wb');
    print("Donloading.....")
    for chunk in r.iter_content(chunk_size=255):
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
    print("Done")
    f.close()

for res in crawl.get_result():
    for r in res[::-1]:
        print(r)
        video_url = 'https://y.yarn.co/' + r['url'].split('/')[-1] + '.mp4'
        print(video_url)
        downloadfile(r['title'], video_url)
        break
    break
