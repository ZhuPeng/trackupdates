# -*- coding: utf-8 -*-
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
import logging
import os
logger = logging.getLogger(__file__)


class Database(object):
    def __init__(self, name):
        target = 'sqlite:///%s/%s' % (os.getcwd(), name)
        self.engine = create_engine(target, echo=False)
        self._session = scoped_session(sessionmaker(bind=self.engine))
        self.base = declarative_base()

    def get_session(self):
        return self._session()

    def close_session(self):
        self._session.remove()

    def get_class_by_tablename(self, tablename):
        """Return class reference mapped to table.

        :param tablename: String with name of table.
        :return: Class reference or None.
        """
        for c in self.base._decl_class_registry.values():
            if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
                return c
        return None

    def create_table_if_not_exists(self, tablename, columns, format={}, create=True):
        # TODO: if donot create, same tablename will raise exception
        table_class = self.get_class_by_tablename(tablename)
        if table_class is not None:
            return table_class

        def repr(cls):
            return ('|'.join(getattr(cls, c) for c in columns)).encode('utf-8')

        mapper = {
            'id': Column(Integer, primary_key=True),
            '__tablename__': tablename,
            '_crawl_time': Column(DateTime, nullable=False)
        }
        for c in columns:
            mapper[c] = Column(String(255), nullable=True)

        def json(cls):
            res = {}
            for c in mapper:
                res[c] = getattr(cls, c)
            return res

        table_class = type(tablename, (self.base,), mapper)
        table_class.__repr__ = repr
        setattr(table_class, 'json', json)
        for k, fmt in format.items():
            setattr(table_class, k, format_wrapper(fmt, mapper))

        if create:
            table_class.__table__.create(bind=self.engine, checkfirst=True)
        return table_class

    def _get(self, session, primary_keys, item):
        model = type(item)
        query = session.query(model)
        for col in primary_keys:
            query = query.filter(getattr(model, col) == getattr(item, col))
        res = query.first()
        if res:
            return res
        return None

    def last(self, item_class, order_by='_crawl_time', num=10, starttime=None, id=None):
        def q(session):
            query = session.query(item_class)
            if id is not None:
                query = query.filter(getattr(item_class, 'id') == id)
            if starttime is not None:
                query = query.filter(getattr(item_class, '_crawl_time') > starttime)
            if hasattr(item_class, order_by):
                order = desc(getattr(item_class, order_by))
                query = query.order_by(order)
            return query.limit(num).all()
        return self.session_run(q)

    def distinct(self, item_class, column):
        def q(session):
            return session.query(getattr(item_class, column)).distinct().all()
        return self.session_run(q)

    def session_run(self, func):
        try:
            session = self.get_session()
            return func(session)
        except Exception as e:
            session.rollback()
            logger.warning("Exception: %s" % e)
        finally:
            self.close_session()

    def store(self, *args, **kwds):
        def real_decorator(fn):
            def wrapped(*a, **kw):
                return self.set(fn(*a, **kw), kwds.get('primary_keys', []))
            return wrapped
        return real_decorator

    def get(self, compare_keys, item):
        def q(session):
            return self._get(session, compare_keys, item)
        return self.session_run(q)

    def set(self, item, compare_keys):
        def q(session):
            tmp = self._get(session, compare_keys, item)
            if tmp is not None:
                return tmp
            session.add(item)
            session.commit()
            logger.debug('ADD item: %s' % item)
            return item
        return self.session_run(q)

    def __call__(self): return self.store()

    def drop(self, item_class):
        return item_class.__table__.drop(self.engine)


def format_wrapper(fmt, columns):
    def f(cls):
        data = {}
        for c in columns:
            data[c] = getattr(cls, c, '')
        return unicode(fmt).format(**data)
    return f


class Table(Database):
    def __init__(self, db, item_class, primary_keys):
        self.db = db
        self.item_class = item_class
        self.primary_keys = primary_keys

    def set(self, key, val, **kw):
        return self.db.set(val, self.primary_keys)

    def get(self, key):
        d = {}
        # TODO: support multikey
        d[self.primary_keys[0]] = key
        return self.db.get(self.primary_keys, self.item_class(**d))

    def iter(self, **kw):
        num = kw.get('num', 20)
        starttime = kw.get('starttime', None)
        id = kw.get('id', None)
        return self.db.last(self.item_class, num=num, starttime=starttime, id=id)

    def drop(self):
        return self.db.drop(self.item_class)

    def distinct(self, col):
        logger.info('get distinct %s from table %s', col, self.item_class.__tablename__)
        return self.db.distinct(self.item_class, col)
