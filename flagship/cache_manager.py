# try:
#     from abc import ABC, abstractmethod
# except ImportError:
import json
import sqlite3 as sl
import time
import traceback
from abc import abstractmethod, ABC

from flagship.constants import TAG_CACHE_MANAGER
from flagship.utils import log_exception


class VisitorCacheImplementation(ABC):

    def __init__(self):
        """
        VisitorCacheImplementation is an abstract class which helps to connect the Flagship SDK and an existing database
        in order to provide a custom cache implementation for visitors information.

        Caching visitors information will prevent any re-allocation.
        """
        pass

    @abstractmethod
    async def cache_visitor(self, visitor_id: str, data: dict):
        """
        This method is called when the Flagship SDK needs to save visitor's data into cache.
        @param visitor_id: Identifier of the visitor whose data must be cached.
        @param data: Visitor's data to be cached.
        """
        pass

    @abstractmethod
    async def lookup_visitor(self, visitor_id: str):
        """
        This method is called when the Flagship SDK needs to load visitor's data from cache.
        @param visitor_id: Identifier of the visitor whose cache must be loaded.
        @return Cached data corresponding to the given visitor id. Please check the documentation for the expected format.
        """
        pass

    @abstractmethod
    async def flush_visitor(self, visitor_id: str):
        """
        This method is called when the Flagship SDK needs to flush visitor's data from cache.
        @param visitor_id: Identifier of the visitor whose cache must be flushed.
        """
        pass


class HitCacheImplementation:

    def __init__(self):
        """
        HitCacheImplementation is an abstract class which helps to connect the Flagship SDK and an existing database
        in order to provide a custom cache implementation for visitors hits.

        Caching visitors hits will prevent any data loss in case of errors or network failures.
        """
        pass

    @abstractmethod
    def cache_hits(self, hits):
        """
        This method is called when the Flagship SDK needs to save visitors hits into cache.
        @param hits: dictionary of hits that need to be saved into cache.
        """
        pass

    @abstractmethod
    async def lookup_hits(self):
        """
        This method is called when the Flagship SDK needs to load visitors hits from the cache.
        @return dictionary of previously cached visitors hits. Please check the documentation for the expected format.
        """
        pass

    @abstractmethod
    def flush_hits(self, hits_ids):
        """
        This method is called when the Flagship SDK needs to flush specific hits.
        @param hits_ids: hits ids that need to be flushed from cache.
        """
        pass

    @abstractmethod
    def flush_all_hits(self):
        """
        This method is called when the Flagship SDK needs to flush all the hits from cache.
        """
        pass


class CacheManager(ABC):

    def __init__(self, **kwargs):
        """
        Abstract class to extend in order to provide a custom CacheManager and link the Flagship SDK to an existing
        database. Your custom class must implement VisitorCacheImplementation class to manage Visitor cache and/or
        HitCacheImplementation class to manager visitor hits.
        @param kwargs: <br><br>
        'timeout' (int) : timeout for database operation in milliseconds. Default is 100.
        """
        self.timeout = (kwargs['timeout'] if 'timeout' in kwargs and isinstance(kwargs['timeout'],
                                                                                int) else 100.0) / 1000.0

    def init(self, flagship_config):
        self.env_id = flagship_config.env_id if flagship_config is not None else None
        self.open_database(self.env_id)

    @abstractmethod
    def open_database(self, env_id):
        pass

    @abstractmethod
    def close_database(self):
        pass


class SqliteCacheManager(CacheManager, VisitorCacheImplementation, HitCacheImplementation):

    full_db_path = None
    db_version = 1
    con = None

    def __init__(self, **kwargs):
        """
        SqliteCacheManager provide a built-in cache manager using local SQLITE database.
        This implementation is designed for client-side applications (one visitor at a time), for server-side
        applications (multiple visitors at a time) it is possible to provide a custom CacheManager implementation.
        @see CacheManager<br>

        <br><br><b>@param kwargs</b><br><br>
        <b>'local_db_patch'</b> (str): destination of the database file. Default is './cache/'. <br>
        <b>'timeout'</b> (int): time delay for reading and writing in the database in milliseconds. Default is 100ms.
        """

        self.db_path = kwargs[
            'local_db_path'] if 'local_db_path' in kwargs and isinstance(
            kwargs['local_db_path'], str) else "./cache/"
        CacheManager.__init__(self, **kwargs)

    def open_database(self, env_id):
        super().open_database(env_id)
        import os
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
        self.full_db_path = self.db_path + '/' + self.env_id + "-cache.db"
        con = sl.connect(self.full_db_path)
        self.create_db_info_table(con)
        self.create_visitor_table(con)
        self.create_hits_table(con)
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

    def create_hits_table(self, con):
        with con:
            con.execute("""
                            CREATE TABLE IF NOT EXISTS HITS (
                                id TEXT UNIQUE,
                                visitor_id TEXT,
                                data TEXT
                            );
                        """)
            con.commit()

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

    async def cache_visitor(self, visitor_id, visitor_data):
        try:
            con = sl.connect(self.full_db_path)
            with con:
                sql = """INSERT OR REPLACE INTO VISITORS (visitor_id, data, last_update) values(?, ?, ?)"""
                data = [visitor_id, json.dumps(visitor_data), int(time.time() * 1000)]
                con.execute(sql, data)
                con.commit()
        except Exception as e:
            log_exception(TAG_CACHE_MANAGER, e, traceback.format_exc())

    async def lookup_visitor(self, visitor_id):
        try:
            con = sl.connect(self.full_db_path)
            with con:
                cursor = con.cursor()
                cursor.execute("SELECT * FROM VISITORS WHERE visitor_id=?", (visitor_id,))
                result = cursor.fetchone()
                if result:
                    cursor.close()
                    return json.loads(result[1])
        except Exception as e:
            log_exception(TAG_CACHE_MANAGER, e, traceback.format_exc())
        return None

    async def flush_visitor(self, visitor_id):
        try:
            con = sl.connect(self.full_db_path)
            with con:
                cursor = con.cursor()
                cursor.execute("DELETE FROM VISITORS WHERE visitor_id=?", (visitor_id,))
                con.commit()
        except Exception as e:
            log_exception(TAG_CACHE_MANAGER, e, traceback.format_exc())

    def __print_hits__(self, tag=""):
        try:
            con = sl.connect(self.full_db_path)
            with con:
                cursor = con.cursor()
                cursor.execute("SELECT id, data FROM HITS")
                result_as_dict = {}
                result = cursor.fetchall()
                if result:
                    cursor.close()
                    for k, v in result:
                        print(tag + " / " + str(v))
                        result_as_dict[k] = json.loads(v)
                return result_as_dict
        except:
            print(traceback.format_exc())
            return None

    def cache_hits(self, hits):
        try:
            con = sl.connect(self.full_db_path)
            records = []
            if len(hits) > 0:
                for k, v in hits.items():
                    records.append((k, v['data']['visitorId'], json.dumps(v)))
                with con:
                    cursor = con.cursor()
                    cursor.executemany("INSERT OR REPLACE INTO HITS VALUES (?, ?, ?)", records)
                    con.commit()
        except Exception as e:
            log_exception(TAG_CACHE_MANAGER + " _1", e, traceback.format_exc())

    async def lookup_hits(self):
        try:
            con = sl.connect(self.full_db_path)
            with con:
                cursor = con.cursor()
                cursor.execute("SELECT id, data FROM HITS")
                result = cursor.fetchall()
                if result:
                    cursor.close()
                    result_as_dict = {}
                    for k, v in result:
                        result_as_dict[k] = json.loads(v)
                    return result_as_dict
        except Exception as e:
            log_exception(TAG_CACHE_MANAGER, e, traceback.format_exc())
        return None

    def flush_hits(self, hits_ids):
        try:
            print("_FLUSH_" + str(hits_ids))
            con = sl.connect(self.full_db_path)
            if len(hits_ids) > 0:
                with con:
                    cursor = con.cursor()
                    cursor.execute("DELETE FROM HITS WHERE id IN ({})".format(", ".join("?" * len(hits_ids))), hits_ids)
                    con.commit()
                    print('_FLUSH_ cnt : ' + str(cursor.rowcount))
        except Exception as e:
            log_exception(TAG_CACHE_MANAGER, e, traceback.format_exc())

    def flush_all_hits(self):
        try:
            con = sl.connect(self.full_db_path)
            with con:
                cursor = con.cursor()
                cursor.execute("DELETE FROM HITS")
                con.commit()
        except Exception as e:
            log_exception(TAG_CACHE_MANAGER, e, traceback.format_exc())

    def close_database(self):
        CacheManager.close_database(self)
        if self.con is not None:
            with self.con:
                self.con.close()
