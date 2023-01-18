# try:
#     from abc import ABC, abstractmethod
# except ImportError:
from abc import abstractmethod, ABCMeta
import sqlite3 as sl



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
    def flush_hits(self, hits):
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

    db_version = 1
    con = None

    def __init__(self):
        CacheManager.__init__(self, visitor_cache_implementation=self, hit_cache_implementation=self)

    def create(self, env_id):
        CacheManager.create(self, env_id)
        import os
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
        self.con = sl.connect(self.db_path + '/' + self.env_id + "-cache.db")
        self.create_db_info_table()
        self.create_visitor_table()

    def create_visitor_table(self):
        with self.con:
            self.con.execute("""
                CREATE TABLE IF NOT EXISTS VISITORS (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    last_update INT,
                    visitor_id TEXT,
                    data TEXT
                );
            """)

    def create_db_info_table(self):
        import time
        self.con.execute("""
                        CREATE TABLE IF NOT EXISTS DB_INFO (
                            creation_date INT,
                            version INT
                        );
                    """)
        add_info_sql = """INSERT INTO DB_INFO (creation_date, version) values(?, ?)"""
        data = [
            int(time.time()*1000), self.db_version
        ]
        self.con.execute(add_info_sql, data)

    def cache_visitor(self, visitor_id, data):
        print("__ cache visitor __ = " + visitor_id)

    def lookup_visitor(self, visitor_id):
        pass

    def flush_visitor(self, visitor_id):
        pass

    def cache_hits(self, hits):
        pass

    def lookup_hits(self):
        pass

    def flush_hits(self, hits):
        pass

    def flush_all_hits(self):
        pass

    def close(self):
        CacheManager.close(self)
        with self.con:
            self.con.close()
