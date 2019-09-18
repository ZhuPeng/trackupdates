# -*- coding: utf-8 -*-
import urllib2
import urllib
import lxml.html as html
from lxml import etree
import HTMLParser
import markdown2
import time
import chardet
import smtplib
import requests
import time
import xmltodict
import json
import string  # for tls add this line
from email.mime.text import MIMEText
from email.header import Header
import threading
import logging
logger = logging.getLogger(__file__)
LOCK = threading.Lock()
SESSION = {}
NOT_INCLUDE = set(['Origin', 'Content-Length', 'Connection', 'Content-Type'])


def get_session_request(url):
    LOCK.acquire()
    request = None
    if url not in SESSION:
        request = requests.Session()
        from selenium import webdriver
        driver = webdriver.PhantomJS()

        driver.get(url)
        time.sleep(3)
        cookies = driver.get_cookies()
        for cookie in cookies:
            request.cookies.set(cookie['name'], cookie['value'])

        for l in driver.get_log('har'):
            har = json.loads(l['message'])
            for e in har['log']['entries']:
                for h in e['request']['headers']:
                    if h['name'] in NOT_INCLUDE:
                        continue
                    request.headers.update({h['name']: h['value']})
        request.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'})
        print 'request cookies: ' + str(request.cookies)
        print 'request headers: ' + str(request.headers)
        driver.quit()
        SESSION[url] = request
    else:
        request = SESSION[url]
    LOCK.release()
    return request


class Email():
    def __init__(self, fromaddr, smtphost, user_passwd):
        self.fromaddr = fromaddr
        self.mailhost, self.mailport = smtphost
        self.username, self.password = user_passwd

    def send(self, toaddrs, subject, content, fmt='plain'):
        try:
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port)

            msg = MIMEText(content.encode('utf-8'), fmt, 'utf-8')
            msg['From'] = Header(self.fromaddr, 'utf-8')
            msg['To'] = Header(string.join(toaddrs, ","), 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')

            if self.username:
                smtp.ehlo()  # for tls add this line
                smtp.starttls()  # for tls add this line
                smtp.ehlo()  # for tls add this line
                smtp.login(self.username, self.password)
            smtp.sendmail(self.fromaddr, toaddrs, msg.as_string())
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            raise


def deco_markdown2html(fn):
    def deco(*args, **kw):
        return markdown2.markdown(fn(*args, **kw))
    return deco


@deco_markdown2html
def page_markdown(store, num=20):
    m = gen_markdown(store.iter(num=num))
    return m


def gen_markdown(items):
    m = ''
    for item in items:
        m += "* %s\n\n" % item.markdown()
    return m

markdown2html = deco_markdown2html(gen_markdown)


def json2xml(j):
    x = xmltodict.unparse({'json': j})
    # print 'xml:', x.encode('utf-8')
    return x


def ajax(url, p):
    request = get_session_request(p['init_cookies']['url'])
    res = request.post(url, data=p)
    logger.debug("crawl content: %s (%s) => %s", url, p, res.content)
    return json2xml(res.json())


def get_rss(url):
    import feedparser
    feed = feedparser.parse(url)
    return json2xml(dict(feed))


def get_data(url, param, retry=3):
    try:
        p = param.copy()
        res = ''
        if p.get('withjs', False):
            res = get_data_with_js(url)
        elif len(p.get('init_cookies', {})) > 0:
            res = ajax(url, p)
        elif p.get('type') == 'rss':
            res = get_rss(url)
        else:
            res = get_data_without_js(url, p, retry)
        # print "%s result => %s" % (url, res)
        return res
    except Exception as e:
        print 'get_data(%s) Exception: %s' % (url, e)
    return ''


def get_data_with_js(url):
    res = ''
    driver = None
    try:
        from selenium import webdriver
        driver = webdriver.PhantomJS()
        driver.get(url)
        time.sleep(3)
        res = driver.page_source
    except Exception as e:
        print 'get_data_with_js(%s) Exception: %s' % (url, e)
    finally:
        driver.quit()
    return res


def get_data_without_js(url, param, retry=3):
    result = ''
    while retry:
        retry -= 1
        try:
            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            f = opener.open(url, None, 120)

            rawdata = f.read()
            result = decode_rawdata(rawdata)
            break
        except Exception as e:
            print 'get_data(%s) Exception: %s' % (url, e)
    return result


none = etree.Element("none")
none.text = ""


def get_xpath(ele, path, idx=0):
    l = ele.xpath(path)
    if len(l) > idx:
        e = l[idx]
    else:
        e = none
    return e


def transfer2dom(content):
    if '<html>' not in content:
        content = '<html>' + content + '</html>'
    html_parser = HTMLParser.HTMLParser()
    content = html_parser.unescape(content)
    dom = html.fromstring(content)
    return dom


def _detect_encodes(rawdata):
    yield 'utf-8'
    yield 'gbk'
    det = chardet.detect(rawdata)
    yield det['encoding']


def decode_rawdata(rawdata):
    decode_text = None
    for en in _detect_encodes(rawdata):
        try:
            decode_text = rawdata.decode(en)
        except:
            continue
        break
    if decode_text is None:
        raise Exception('Decode Error')
    return decode_text


def read_content(filename):
    print 'read content from local file: %s' % filename
    f = open(filename, 'r')
    rawdata = f.read()
    f.close()
    return decode_rawdata(rawdata)

if __name__ == '__main__':
    print get_data('https://github.com/trending/Vue?since=daily', {'withjs': False})
