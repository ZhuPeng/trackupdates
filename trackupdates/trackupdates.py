# -*- coding: utf-8 -*-
"""
Usage:
  trackupdates.py <yaml> [--test] [--runjobs=<runjobs>] [--log=<level>] [--runoneloop] [--noserver] [--threadcount=<threadcount>]
  trackupdates.py (-h | --help)
  trackupdates.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --log=<level>    log level [default: INFO].
  --test        Test parse webpage content in local.
  --runoneloop  Run only one loop.
  --noserver    Donot runserver
  --threadcount Thread Count for downloader, defalut 3.
  --runjobs=<runjobs>    Specify job name with comma, default run all jobs [default: ].
"""
from docopt import docopt
import yaml
import logging
import utils
from datetime import datetime, timedelta
import database
import server
import random
import thread
from threading import Thread
import urllib
from Queue import Queue
logging.basicConfig()
logger = logging.getLogger(__file__)
ThreadCount = 3


class Settings:
    def __init__(self, path):
        logger.info('yaml config file path: %s' % path)
        self.path = path
        with open(path, 'r') as stream:
            self.yml_dict = yaml.load(stream)
        for k, v in self.yml_dict.items():
            setattr(self, k, v)
        for k, v in self.yml_dict['global'].items():
            setattr(self, k, v)

    def __getitem__(self, key):
        return self.yml_dict[key]

    def get_job(self, name):
        for c in self.yml_dict['jobs']:
            if c['name'] == name:
                return self._complete_job_config(c)

    def _complete_job_config(self, config):
        config['parser_config'] = self.get_parser(config['parser'])
        if 'update' not in config or config['update'] is None:
            config['update'] = {}
        if 'cron' not in config:
            config['cron'] = '*|%d' % random.randint(0, 59)
        rec_name = config['update'].get('receiver', '')
        config['update']['emails'] = self.get_receivers(rec_name)
        return config

    def get_receivers(self, name):
        for r in self.yml_dict.get('receivers', []):
            if r['name'] == name:
                return r['email_configs']['to']
        return []

    def get_daily_report_receivers(self):
        return self.get_receivers(self.yml_dict['global'].get('daily_report_receivers', ''))

    def get_all_job_configs(self):
        for config in self.yml_dict['jobs']:
            job = self._complete_job_config(config)
            yield job

    def get_parser(self, name):
        for p in self.yml_dict['parsers']:
            if p['name'] == name:
                return p

    def get_parser_format(self, name):
        parser = self.get_parser(self.get_job(name)['parser'])
        return parser['format']


def new_mailer_from_settings(settings):
    glob = settings['global']
    if 'smtp_smarthost' not in glob:
        return None

    smtp = glob.get('smtp_smarthost').split(':')
    user = glob.get('smtp_auth_username', '')
    fromaddr = glob.get('smtp_from', user)
    passwd = glob.get('smtp_auth_password', '')

    return utils.Email(fromaddr, (smtp[0], int(smtp[1])), (user, passwd))


class Parser:
    def __init__(self, config):
        self.config = config
        self.base_url = config['base_url']

    def parse(self, content):
        items = []
        dom = utils.transfer2dom(content)
        base_xpath = self.config['base_xpath']
        for bx in base_xpath:
            for ele in dom.xpath(bx.lower()):
                items.append(self._parse_item(ele))
        return items

    def _parse_item(self, ele):
        d = {}
        concat = []
        for k, v in self.config['attr'].items():
            if '+' in v:
                concat.append((k, v))
                continue
            res = utils.get_xpath(ele, v.lower())
            if hasattr(res, 'itertext'):
                res = ' '.join([r.strip() for r in res.itertext()])
            elif hasattr(res, 'text'):
                res = res.text()

            res = unicode(res).strip()
            if k.endswith('url') and not res.startswith('http'):
                res = self.base_url.rstrip('/') + '/' + res.lstrip('/')
            d[k] = res
        d['_crawl_time'] = datetime.now()
        for k, v in concat:
            d[k] = eval(v, d.copy())
        return d


class Downloader:
    def __init__(self):
        self.queue = Queue()
        self.output = Queue()
        # self.thread_pool_size = 3
        self.daemon()

    def daemon(self):
        for i in range(ThreadCount):
            t = Thread(name = 'Thread-' + str(i), target=self.thread_get, args=())
            t.daemon = True
            t.start()

    def add(self, url, param):
        logger.debug("pre add queue size: %d", self.queue.qsize())
        self.queue.put((url, param))
        logger.debug("post add queue size: %d", self.queue.qsize())

    def get(self, url, param, retry=3):
        logger.info('Crawl content url: %s, %s', url, str(param))
        if not url.startswith('http'):
            return utils.read_content(url)
        return utils.get_data(url, param, retry)

    def thread_get(self):
        while True:
            logger.debug("pre get queue size: %d", self.queue.qsize())
            url, param = self.queue.get()
            logger.debug("post get queue size: %d", self.queue.qsize())
            self.output.put(self.get(url, param))
            self.queue.task_done()

    def get_result(self):
        while True:
            yield self.output.get()

    def isqueueempty(self):
        while not self.queue.empty():
            pass
        logger.info("queue was empty")


class ListCrawl:
    def __init__(self, config, test=False):
        self.config = config
        self.test = test
        self.pconfig = config['parser_config']
        self.parser = Parser(self.config['parser_config'])
        self.downloader = Downloader()

    def gen_value_set(self, parm_var):
        values_list = []
        for qp in parm_var:
            if qp['type'] == 'string':
                for s in str(qp['value']).split(','):
                    values_list.append(s)
            elif qp['type'] == 'range':
                for r in range(int(qp['from']), int(qp['to'])):
                    values_list.append(str(r))
            elif qp['type'] == 'distinct':
                table = qp.get('table', self.config['name'])
                col = qp['value']
                job = self.sched.get_job(table)
                for v in job.store.distinct(col):
                    if v[0]:
                        values_list.append(v[0])
        return set(values_list)

    def gen_crawl_urls(self):
        self.url_format = self.config['url']['test_target'] if self.test else self.config['url']['target']
        logger.info('Crawl content from format: ' + self.url_format)
        param = self.config['url'].get('post_body', {})
        param['withjs'] = self.config['url'].get('withjs', False)
        param['init_cookies'] = self.config['url'].get('init_cookies', {})
        if not self.url_format.startswith('http') and '{' not in self.url_format:
            self.downloader.add(self.url_format, param)
            return

        for k, v in self.config['url'].get('post_body_parameter', {}).items():
            values_set = self.gen_value_set(v)
            tmp = param.copy()
            for vs in values_set:
                tmp[k] = vs
                self.downloader.add(self.url_format, tmp.copy())

        query = self.config['url'].get('query_parameter', {})
        if len(query) == 0:
            self.downloader.add(self.url_format, param)
            return

        # TODO: Now only support one query parameter with enumerate value
        for k, v in query.items():
            values_set = self.gen_value_set(v)
            for vs in values_set:
                if not vs.startswith('http'):
                    vs = urllib.quote_plus(vs)
                d = {k: vs}
                url = unicode(self.url_format).format(**d)
                self.downloader.add(url, param)

    def run(self, sched=None):
        self.sched = sched
        self.gen_crawl_urls()

    def get_result(self):
        for r in self.downloader.get_result():
            yield self.parser.parse(r)


class Job:
    def __init__(self, config, db, mailer=None, test=False):
        self.config = config
        self.db = db
        self.mailer = mailer
        self.name = self.config['name']
        self.crawl = ListCrawl(config, test)
        self.receivers = self.config['update']['emails']
        self.match = self.config['update'].get('match', {})
        self.filter_funcs = []
        for k, v in self.match.items():
            self.filter_funcs.append(keyword_contains(k, v))
        self.test = test
        self.col_map = config['parser_config']['attr']
        self.fmt = config['parser_config'].get('format', {})
        self._init_store()
        thread.start_new_thread(self.daemon, ())

    def _init_store(self):
        tname = self.name
        if self.test:
            tname = 'test_' + self.name
        self.item_class = self.db.create_table_if_not_exists(tname, self.col_map.keys(), self.fmt)
        self.store = database.Table(self.db, self.item_class, ['url'])

    def run(self, sche=None, filterbykeyword=True):
        logger.info('[%s]: job run' % self.name)
        self.crawl.run(sche)

    def daemon(self, filterbykeyword=True):
        logger.info('[%s] daemon run job', self.name)
        for items in self.crawl.get_result():
            if self.test:
                print_items(items)
                continue
            update = []
            for i in items[::-1]:
                t = self.item_class(**i)
                # TODO: Need a simple and efficient method, now use attribute url
                # for default distinguish value
                key = t.url
                if self.store.get(key) is not None:
                    continue
                update.append(self.store.set(key, t))
            if len(update) == 0:
                continue
            logger.info('[%s]: crawl new updates: %d' % (self.name, len(update)))
            if filterbykeyword:
                update = filter(self._filter, update)
            if not self.test and len(update):
                logger.info('[%s]: track notify updates: %d' % (self.name, len(update)))
                self.send_mail(update)

    def _filter(self, item):
        if len(self.filter_funcs) == 0:
            return True
        return any(map(lambda f: f(item), self.filter_funcs))

    def send_mail(self, update_items, head="New Update From", receivers=[]):
        if self.mailer is None:
            logger.warn('[%s]: email not config' % self.name)
            return
        if len(receivers) == 0:
            receivers = self.receivers

        if len(receivers) == 0:
            logger.warn('[%s]: receiver not specified' % self.name)
            return
        if len(update_items) == 0:
            return

        logger.info('[%s]: Send mail update count %d' % (self.name, len(update_items)))
        html = utils.markdown2html(update_items)
        subject = '%s [%s]' % (head, self.name)
        self.mailer.send(receivers, subject, html, fmt='html')


def keyword_contains(k, v):
    vlist = v.split(',')

    def c(item):
        for v in vlist:
            iattr = getattr(item, k)
            logger.debug('%s: %s' % (v, iattr))
            if v.lower() in iattr.lower():
                return True
        else:
            return False
    return c


def print_items(items):
    for i in items:
        logger.info(i)


class Scheduler:
    def __init__(self, config_path, blocking=True, test=False, runjobs=None, runoneloop=False):
        self.settings = Settings(config_path)
        self.blocking = blocking
        if blocking and not runoneloop:
            from apscheduler.schedulers.blocking import BlockingScheduler
            self.sched = BlockingScheduler()
        else:
            from apscheduler.schedulers.background import BackgroundScheduler
            self.sched = BackgroundScheduler()
        self.test = test
        self.runoneloop = runoneloop
        self.runjobs = runjobs.split(',') if type(runjobs) == str and len(runjobs) else []
        self.jobs = {}
        self.mailer = new_mailer_from_settings(self.settings)
        self.db = database.Database(self.settings['global'].get('store', 'track.db'))
        self._init_job()
        self.sched.add_job(self.daily_report, 'cron', **parse_job_cron('18|30'))

    def get_job(self, name):
        return self.jobs[name]

    def daily_report(self):
        receivers = self.settings.get_daily_report_receivers()
        if len(receivers) == 0:
            return
        for k, job in self.jobs.items():
            items = job.store.iter(starttime=datetime.now()-timedelta(days=1), num=50)
            job.send_mail(items, head="Daily Report From", receivers=receivers)

    def add_job(self, *args, **kws):
        self.sched.add_job(*args, **kws)

    def _init_job(self):
        for config in self.settings.get_all_job_configs():
            name = config['name']
            if len(self.runjobs) and name not in self.runjobs:
                continue
            job = Job(config, self.db, self.mailer, self.test)
            self.jobs[name] = job
            cron = parse_job_cron(config['cron'])
            self.sched.add_job(job.run, 'cron', [self], **cron)

    def first_run(self):
        for k, job in self.jobs.items():
            def f(j):
                j.run(self)
            f(job)

        if self.runoneloop:
            for k, job in self.jobs.items():
                if job.crawl.downloader.isqueueempty():
                    continue

    def run(self):
        try:
            self.first_run()
            if not self.test:
                self.sched.start()
        except (KeyboardInterrupt, SystemExit):
            self.sched.shutdown()


def parse_job_cron(cron_str):
    d = {}
    d['hour'], d['minute'] = cron_str.split('|')
    return d


__version__ = '0.0.9'


def main():
    args = docopt(__doc__, version=__version__)
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, args['--log'].upper()))
    if '--threadcount' in args and args['--threadcount'] is not None and args['--threadcount'].isdigit():
        global ThreadCount
        ThreadCount = int(args['--threadcount'])
        logger.info('Set Thread Count: %d' % ThreadCount)

    runoneloop = args['--runoneloop']
    noserver = args['--noserver']
    sched = Scheduler(args['<yaml>'], test=args['--test'], runjobs=args['--runjobs'], blocking=False or noserver, runoneloop=runoneloop)
    sched.run()
    if not runoneloop and not noserver:
        server.Server(sched).run()


if __name__ == '__main__':
    main()
