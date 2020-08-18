# -*- coding: utf-8 -*-
import requests
import sys
import datetime
from urllib import quote
weekAgo = (datetime.datetime.now() - datetime.timedelta(days=7))
weekAgoStr = weekAgo.strftime("%Y-%m-%d")
qrcode = u'扫码关注如下微信公众号，定期获取开源项目或书籍推荐。\n\n![wechat](https://7465-test-3c9b5e-1258459492.tcb.qcloud.la/common/ultrabot-qrcode.png)\n'
# footer = u'*****\n[点击查看自动插入小程序链接指南](https://github.com/ZhuPeng/mp-transform-public)\n\n以上就是本期周报的内容，我们下周见。欢迎大家与我交流，点击访问 [GitHub 小程序](https://github.com/) 。%s' % qrcode
footer = u'*****\n\n以上就是本期推荐的内容，欢迎留言交流。%s' % qrcode


def md(lang, jobname='python'):
    url = 'http://39.106.218.104:5000/api/items?jobname=%s&lang=%s&num=99999&starttime=%s' \
        % (jobname, quote(lang), weekAgoStr)
    res = requests.get(url).json()['data']
    md = u'大家好！我是超级机器人 UltraBot，今天给大家推送本周 %s 开源项目 GitHub 趋势周报，本周更新开源项目 %d。\n\n' \
        % (lang, len(res))
    collect = []
    for r in res:
        tmp = [
            '[%s](%s)\n' % (r['repo'], r['url']),
            'Star: %s, Fork: %s\n' % (r['star'], r['fork']),
            r['desc'],
        ]
        topics = getTopic(r['url'])
        for t in topics:
            tmp.append('\n>%s\n>%s-- %s' % (t['content'].replace('\n', '\n>'), ' '*40, t['username']))
        tmp = '\n'.join(tmp) + '\n\n\n\n'
        if len(topics) == 0:
            collect.append(tmp)
        else:
            collect.insert(0, tmp)
    md += ''.join(collect[:47])
    md += footer
    print md.encode('utf-8')


def genBlog(r):
    url = r['url'].replace('http://', 'https://')
    tmp = [
        '[%s](%s)\n' % (r['title'], r['url'].replace('http://', 'https://')),
        r.get('abstract', ''),
    ]
    if r.get('article-image_url', '') != '':
        tmp.append('![](%s)' % r['article-image_url'])
    if r.get('content', '') != '':
        tmp.append('\n' + r['content'])
    tmp.append(u'\n[点击阅读详情](%s)' % url)
    return '\n'.join(tmp) + '\n\n\n\n'


def book_md():
    md = u'大家好！我是超级机器人 UltraBot，今天给大家一些值得阅读的开源书籍和项目。\n\n'
    blogs = getBlog(server='http://localhost:8081')
    for b in blogs:
        md += genBlog(b)
    md += footer
    print md.encode('utf-8')


def tech_bolg_md(jobname='jianshu'):
    md = u'大家好！我是超级机器人 UltraBot，今天给大家推送本周技术博客周刊。\n\n'
    blogs = getBlog()
    for b in blogs:
        md += genBlog(b)

    url = 'http://39.106.218.104:5000/api/items?jobname=%s&num=99999&starttime=%s' \
        % (jobname, weekAgoStr)
    res = requests.get(url).json()['data']
    count = 0
    for r in res:
        if not isTech(r):
            continue
        count += 1
        if count > 40:
            continue
        md += genBlog(r)
    md += footer
    print md.encode('utf-8')


def isTech(r):
    for k in ['GitHub', 'StackOverflow', 'k8s', 'kubernetes', 'docker', u'程序', u'代码', u'开发', 'API', u'源码',
              u'架构师']:
        for a in ['title', 'abstract']:
            if k.lower() in r[a].lower():
                return True
    return False


def getBlog(server="http://localhost:8888"):
    target = server + '/blog?page=1&order_time=asc&page_size=5'
    res = requests.get(target).json()['data']
    return res


def getTopic(githuburl, server="http://localhost:8888"):
    try:
        target = "%s/topic?url=%s" % (server, githuburl)
        res = requests.get(target).json()['data']
        return res
    except:
        return []


if __name__ == '__main__':
    if len(sys.argv) != 2:
        exit(1)
    if sys.argv[1] == u"TECHBLOG":
        tech_bolg_md()
    if sys.argv[1] == u"book":
        book_md()
    else:
        md(sys.argv[1])
