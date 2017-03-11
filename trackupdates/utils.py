# encoding: utf-8
import urllib2
import urllib
import lxml.html as html
from lxml import etree
import HTMLParser
import markdown2
import chardet
import smtplib
import string  # for tls add this line
from email.mime.text import MIMEText
from email.header import Header


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


def get_data(url, param, retry=3):
    result = ''
    while retry:
        retry -= 1
        try:
            opener = urllib2.build_opener()
            if len(param) != 0:
                f = opener.open(url, urllib.urlencode(param), 120)
            else:
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
