# try:
#     from abc import ABC, abstractmethod
# except ImportError:
import json
import time
import traceback
from abc import abstractmethod, ABCMeta
import sqlite3 as sl

from flagship.constants import TAG_CACHE_MANAGER
from flagship.utils import log_exception


class VisitorCacheImplementation:

    @abstractmethod
    def cache_visitor(self, visitor_id, data):
        pass

    @abstractmethod
    def lookup_visitor(self, visitor_id):
        pass

    @abstractmethod
    def flush_visitor(self, visitor_id):
        pass


class HitCacheImplementation:

    @abstractmethod
    def cache_hits(self, hits):
        pass

    @abstractmethod
    def lookup_hits(self):
        pass

    @abstractmethod
    def flush_hits(self, hits_ids):
        pass

    @abstractmethod
    def flush_all_hits(self):
        pass


class CacheManager(object):
    __metaclass__ = ABCMeta
    env_id = None

    def __init__(self, **kwargs):
        self.visitor_cache_interface = kwargs[
            'visitor_cache_implementation'] if 'visitor_cache_implementation' in kwargs and isinstance(
            kwargs['visitor_cache_implementation'], VisitorCacheImplementation) else None

        self.hit_cache_interface = kwargs[
            'hit_cache_implementation'] if 'hit_cache_implementation' in kwargs and isinstance(
            kwargs['hit_cache_implementation'], HitCacheImplementation) else None

        self.db_path = kwargs[
            'local_db_path'] if 'local_db_path' in kwargs and isinstance(
            kwargs['local_db_path'], str) else "./cache/"

    def create(self, env_id):
        self.env_id = env_id

    def close(self):
        pass


class DefaultCacheManager(CacheManager, VisitorCacheImplementation, HitCacheImplementation):
    full_db_path = None
    db_version = 1
    con = None

    def __init__(self):
        CacheManager.__init__(self, visitor_cache_implementation=self, hit_cache_implementation=self)

    def create(self, env_id):
        CacheManager.create(self, env_id)
        import os
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
        self.full_db_path = self.db_path + '/' + self.env_id + "-cache.db"
        con = sl.connect(self.full_db_path)
        self.create_db_info_table(con)
        self.create_visitor_table(con)
        con.close()

    def create_visitor_table(self, con):

        with con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS VISITORS (
                    visitor_id TEXT UNIQUE PRIMARY KEY,
                    data TEXT,
                    last_update INTEGER
                );
            """)

    def create_db_info_table(self, con):
        with con:
            con.execute("""
                            CREATE TABLE IF NOT EXISTS DB_INFO (
                                id INTEGER UNIQUE,
                                creation_date INTEGER,
                                version INTEGER
                            );
                        """)
            sql = """INSERT OR REPLACE INTO DB_INFO (id, creation_date, version) values(?, ?, ?)"""
            data = [0, int(time.time() * 1000), self.db_version]
            con.execute(sql, data)
            con.commit()

    def cache_visitor(self, visitor_id, visitor_data):
        try:
            print("== cache visitor {} ==".format(visitor_id))
            con = sl.connect(self.full_db_path)
            with con:
                sql = """INSERT OR REPLACE INTO VISITORS (visitor_id, data, last_update) values(?, ?, ?)"""
                data = [visitor_id, json.dumps(visitor_data), int(time.time() * 1000)]
                con.execute(sql, data)
                con.commit()
        except Exception as e:
            log_exception(TAG_CACHE_MANAGER, e, traceback.format_exc())

    def lookup_visitor(self, visitor_id):
        try:
            con = sl.connect(self.full_db_path)
            with con:
                cursor = con.cursor()
                cursor.execute("SELECT * FROM VISITORS WHERE visitor_id=?", (visitor_id,))
                result = cursor.fetchone()
                if result:
                    cursor.close()
                    return result[1]
        except Exception as e:
            log_exception(TAG_CACHE_MANAGER, e, traceback.format_exc())
        return None

    def flush_visitor(self, visitor_id):
        try:
            con = sl.connect(self.full_db_path)
            with con:
                cursor = con.cursor()
                cursor.execute("DELETE FROM VISITORS WHERE visitor_id=?", (visitor_id,))
                con.commit()
        except Exception as e:
            log_exception(TAG_CACHE_MANAGER, e, traceback.format_exc())

    def cache_hits(self, hits):
        pass

    def lookup_hits(self):
        pass

    def flush_hits(self, hits_ids):
        pass

    def flush_all_hits(self):
        pass

    def close(self):
        CacheManager.close(self)
        with self.con:
            self.con.close()
