import asyncio
import json
import time
import traceback

from flagship import cache_helper
from flagship.cache_manager import HitCacheImplementation, CacheManager, VisitorCacheImplementation
from flagship.constants import TAG_TRACKING_MANAGER, ERROR_INVALID_HIT, TAG_CACHE_MANAGER, INFO_TRACKING_MANAGER, \
    DEBUG_TRACKING_MANAGER_STOPPED, DEBUG_TRACKING_MANAGER_STARTED, DEBUG_TRACKING_MANAGER_LOOKUP_HITS, \
    DEBUG_TRACKING_MANAGER_ADDED_HITS, DEBUG_TRACKING_MANAGER_CACHE_HITS
from flagship.errors import HitCacheTimeoutException
from flagship.log_manager import LogLevel
from flagship.utils import log, log_exception, get_args_or_default, get_args_or_default_with_min_max, pretty_dict

try:
    from Queue import Queue
except ImportError:
    from queue import Queue
from abc import ABCMeta, abstractmethod
from enum import Enum
from threading import Thread

from flagship.hits import _Consent, _Batch, _Activate
from flagship.http_helper import HttpHelper


class TrackingManagerCacheStrategyInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def add_hit(self, hit, new=True):
        pass

    @abstractmethod
    def add_hits(self, hits, new=True):
        pass

    @abstractmethod
    def delete_hits_by_id(self, ids):
        pass

    @abstractmethod
    def delete_hits_by_visitor_id(self, visitor_id, delete_consent_hits=True):
        pass

    @abstractmethod
    def lookup_pool(self):
        pass

    @abstractmethod
    def cache_pool(self):
        pass

    @abstractmethod
    def polling(self):
        pass

    @abstractmethod
    def send_hits_batch(self):
        pass

    @abstractmethod
    def send_activates_batch(self, hit=None):
        pass


class CacheStrategy(Enum):

    def __init__(self, *args):
        """
        This class specify the hits caching strategy to adopt into the TrackingManager and relies on the
        HitCacheImplementation class that must be implemented in the CacheManager. Depending on the strategy the
        TrackingManager will request the CacheManager to CACHE, LOOK-UP or FLUSH hits from the linked database.
        """
        pass
    
    CONTINUOUS_CACHING = 'CONTINUOUS_CACHING'
    """
    Hits will be continuously cached and flushed from the database.
    The database linked to the HitCacheImplementation class implemented in the provided CacheManager will be required 
    each time time a hit is added or flushed 
    from the TrackingManager pool.
    """

    PERIODIC_CACHING = 'PERIODIC_CACHING'
    """
    Hits will be cached and flushed from the database periodically.
    The database linked to the HitCacheImplementation class implemented in the provided CacheManager will be required to
    cache/look-up/flush hits at regular time intervals. The time intervals relies on the TrackingManager 'time_interval' 
    option.
    """

    _NO_BATCHING_CONTINUOUS_CACHING = '_NO_BATCHING_CONTINUOUS_CACHING'


class TrackingManagerConfig:

    DEFAULT_MAX_POOL_SIZE = 20
    DEFAULT_TIME_INTERVAL = 10000  # time in ms
    DEFAULT_TIMEOUT = 200  # time in ms

    def __init__(self, **kwargs):
        """
        This class configure the Flagship SDK Tracking Manager which gathers all visitors emitted hits in a pool and
        fire them in batch requests at regular time intervals withing a dedicated thread.

        <br><br><b>@param kwargs: </b><br><br>
        <b>'cache_strategy'</b> (CacheStrategy): Specifies the strategy to use for hits caching. An implementation of
        HitCacheImplementation is required in the provided CacheManager. <br>
        <b>'timeout' (int)</b>: Specifies a timeout for hits https requests in milliseconds. Default is 200ms. <br>
        <b>'time_interval' (int)</b>: Specifies a time delay between each batched hit requests in milliseconds.
        Default is 10000ms<br>
        <b>'max_pool_size' (int)</b>: Specifies a max hit pool size that will trigger a batch request once reached.
        Default is 20.
        """
        self.strategy = get_args_or_default('cache_strategy', CacheStrategy, CacheStrategy.CONTINUOUS_CACHING, kwargs)
        self.timeout = get_args_or_default('timeout', int, self.DEFAULT_TIMEOUT, kwargs)
        self.time_interval = get_args_or_default_with_min_max('time_interval', int, self.DEFAULT_TIME_INTERVAL, kwargs, 200, 10800000)
        self.max_pool_size = get_args_or_default_with_min_max('max_pool_size', int, self.DEFAULT_MAX_POOL_SIZE, kwargs, 0, 5000)

    def to_dict(self):
        return {
            'strategy': str(self.strategy),
            'timeout': self.timeout,
            'time_interval': self.time_interval,
            'max_pool_size': self.max_pool_size
        }


class TrackingManager(TrackingManagerCacheStrategyInterface, Thread):
    """
    The Tracking Manager gathers all visitors emitted hits in a pool and fire them in batch requests at regular time
    intervals withing a dedicated thread.
    """

    BATCH_MAX_SIZE = 2500000
    HIT_EXPIRATION = 14400000

    def __init__(self, flagship_config, cache_manager=None):
        Thread.__init__(self)
        TrackingManagerCacheStrategyInterface.__init__(self)
        self.daemon = True  # Attach the thread to main thread
        self.config = flagship_config
        self.first_round = True
        self.running = False
        self.hitQueue = Queue()
        self.activateQueue = Queue()
        self.tracking_manager_config = flagship_config.tracking_manager_config
        self.time_interval = flagship_config.tracking_manager_config.time_interval
        self.cache_manager = cache_manager
        self.strategy = self.get_strategy()

    def init(self, flagship_config, cache_manager):
        self.config = flagship_config
        self.tracking_manager_config = flagship_config.tracking_manager_config
        self.time_interval = flagship_config.tracking_manager_config.time_interval
        self.cache_manager = cache_manager
        self.strategy = self.get_strategy()
        if self.strategy == CacheStrategy._NO_BATCHING_CONTINUOUS_CACHING:
            self.lookup_pool()
            self.polling()
            pass
        elif self.time_interval > 0:
            self.start_running()

    def start_running(self):
        if self.running is False:
            log(TAG_TRACKING_MANAGER, LogLevel.DEBUG, DEBUG_TRACKING_MANAGER_STARTED)
            self.running = True
            self.start()

    def run(self):
        while self.running:
            if self.first_round:
                self.lookup_pool()
                self.first_round = False
            self.polling()
            time.sleep(self.time_interval / 1000.0)

    def print_pool(self, tag=""):
        print(tag + " pool size : " + str(self.hitQueue.qsize()))
        if self.hitQueue.qsize() > 0:
            for h in self.hitQueue.queue:
                print(str(tag) + " / " + str(h))

    def stop_running(self, do_last_polling=True):
        if self.strategy == CacheStrategy._NO_BATCHING_CONTINUOUS_CACHING:
            if do_last_polling:
                self.cache_pool()
        if self.running is True:
            self.running = False
            if do_last_polling:
                self.cache_pool()
            log(TAG_TRACKING_MANAGER, LogLevel.DEBUG, DEBUG_TRACKING_MANAGER_STOPPED)

    def add_hit(self, hit, new=True):
        return self.strategy.add_hit(hit, new)

    def add_hits(self, hits, new=True):
        return self.strategy.add_hits(hits, new)

    def delete_hits_by_id(self, ids, delete_consent_hits=True):
        return self.strategy.delete_hits_by_id(ids, delete_consent_hits)

    def delete_hits_by_visitor_id(self, visitor_id, delete_consent_hits=True):
        return self.strategy.delete_hits_by_visitor_id(visitor_id, delete_consent_hits)

    def lookup_pool(self):
        return self.strategy.lookup_pool()

    def cache_pool(self):
        return self.strategy.cache_pool()

    def polling(self):
        return self.strategy.polling()

    def send_hits_batch(self):
        return self.strategy.send_hits_batch()

    def send_activates_batch(self, hit=None):
        return self.strategy.send_activates_batch(hit)

    def get_strategy(self):
        if self.tracking_manager_config.strategy == CacheStrategy.CONTINUOUS_CACHING:
            return ContinuousCacheStrategy(self)
        elif self.tracking_manager_config.strategy == CacheStrategy.PERIODIC_CACHING:
            return PeriodicCacheStrategy(self)
        elif self.tracking_manager_config.strategy == CacheStrategy._NO_BATCHING_CONTINUOUS_CACHING:
            return NoBatchingCacheStrategy(self)

    def is_running(self):
        return self.running


class TrackingManagerCacheStrategyAbstract(TrackingManagerCacheStrategyInterface):
    __metaclass__ = ABCMeta

    def __init__(self, tracking_manager):
        TrackingManagerCacheStrategyInterface.__init__(self)
        self.tracking_manager = tracking_manager
        cache_manager = self.tracking_manager.cache_manager
        self.timeout = cache_manager.timeout if cache_manager is not None else self.tracking_manager.config.timeout

    def add_hit(self, hit, new=True):
        if hit.check_data_validity():
            if isinstance(hit, _Activate):
                self.send_activates_batch(hit)
            else:
                self.tracking_manager.hitQueue.put(hit, block=False)
                log(TAG_TRACKING_MANAGER, LogLevel.DEBUG, DEBUG_TRACKING_MANAGER_ADDED_HITS + self.__hits_to_str__(hit))
            return True
        else:
            log(TAG_TRACKING_MANAGER, LogLevel.ERROR, ERROR_INVALID_HIT.format(hit.type, hit.id))
            # delete hit
            self.delete_hits_by_id([hit.id])
            return False

    def add_hits(self, hits, new=True):
        success_hits = list()
        for h in hits:
            if self.add_hit(h, new) is True:
                success_hits.append(h)
        return success_hits

    def check_max_pool_size(self):
        if self.tracking_manager.hitQueue.qsize() >= self.tracking_manager.tracking_manager_config.max_pool_size:
            self.send_hits_batch()

    def delete_hits_by_id(self, ids, delete_consent_hits=True):
        removed_ids = list()
        for item in list(self.tracking_manager.hitQueue.queue):
            if item.id in ids:
                if delete_consent_hits is not True and not isinstance(item, _Consent):
                    removed_ids.append(item.id)
                    self.tracking_manager.hitQueue.queue.remove(item)
        return removed_ids

    def delete_hits_by_visitor_id(self, visitor_id, delete_consent_hits=True):
        removed_ids = list()
        # Hits
        for item in list(self.tracking_manager.hitQueue.queue):
            if item.visitor_id == visitor_id:
                if delete_consent_hits is not True and not isinstance(item, _Consent):
                    removed_ids.append(item.id)
                    self.tracking_manager.hitQueue.queue.remove(item)
        # Activates
        for item in list(self.tracking_manager.activateQueue.queue):
            if item.visitor_id == visitor_id:
                removed_ids.append(item.id)
                self.tracking_manager.activateQueue.queue.remove(item)
        return removed_ids

    def lookup_pool(self):
        hit_cache_interface = self.get_hit_cache_interface()
        if hit_cache_interface is not None:
            try:
                cached_hits = asyncio.run(asyncio.wait_for(hit_cache_interface.lookup_hits(), timeout=self.timeout))
                # cached_hits = hit_cache_interface.lookup_hits()
                if cached_hits and isinstance(cached_hits, dict) and len(cached_hits) > 0:
                    hits = cache_helper.hits_from_cache_json(cached_hits)
                    log(TAG_TRACKING_MANAGER, LogLevel.DEBUG, DEBUG_TRACKING_MANAGER_LOOKUP_HITS + self.__hits_to_str__(hits))
                    self.add_hits(hits)
            except Exception as e:
                if type(e) is asyncio.exceptions.TimeoutError:
                    log(TAG_CACHE_MANAGER, LogLevel.ERROR, str(HitCacheTimeoutException("lookup_hits()")))
                else:
                    log(TAG_CACHE_MANAGER, LogLevel.ERROR, str(e))

    def cache_pool(self):
        hits = list(self.tracking_manager.hitQueue.queue) + list(self.tracking_manager.activateQueue.queue)
        if len(hits) > 0:
            log(TAG_TRACKING_MANAGER, LogLevel.DEBUG, DEBUG_TRACKING_MANAGER_CACHE_HITS + self.__hits_to_str__(hits))
            self.cache_hits(hits)

    @abstractmethod
    def polling(self):
        log(TAG_TRACKING_MANAGER, LogLevel.DEBUG, INFO_TRACKING_MANAGER)
        self.send_hits_batch()
        self.send_activates_batch()

    def __hits_to_str__(self, hits):
        results = ""
        if isinstance(hits, list):
            for h in hits:
                results += "\t" + str(h) + "\n"
        else:
            results += "\t" + str(hits) + "\n"
        return results[:-1]


    @abstractmethod
    def send_hits_batch(self):
        batch = _Batch()
        while not self.tracking_manager.hitQueue.empty():
            h = self.tracking_manager.hitQueue.get(block=False)
            if h:
                batch.add_child(h)
        if batch.size() > 0:
            response = HttpHelper.send_hit(self.tracking_manager.config, batch)
            if response is None or response.status_code >= 400:
                for h in batch.hits:
                    self.tracking_manager.hitQueue.put(h, block=False)
            return response, batch
        return None, batch

    def cache_hits(self, hits_to_cache):
        try:
            hit_cache_interface = self.get_hit_cache_interface()
            if hit_cache_interface is not None:
                hits = cache_helper.hits_to_cache_json(hits_to_cache)
                hit_cache_interface.cache_hits(hits)
        except Exception as e:
            log_exception(TAG_CACHE_MANAGER, e, traceback.format_exc())

    def flush_hits(self, hits_to_flush):
        try:
            hit_cache_interface = self.get_hit_cache_interface()
            if hit_cache_interface is not None:
                hit_cache_interface.flush_hits(hits_to_flush)
        except Exception as e:
            log_exception(TAG_CACHE_MANAGER, e, traceback.format_exc())

    @abstractmethod
    def send_activates_batch(self, hit=None):

        activates = list()
        if hit:
            activates.append(hit)
        while not self.tracking_manager.activateQueue.empty():
            activate = self.tracking_manager.activateQueue.get(block=False)
            if activate:
                activates.append(activate)
        if len(activates) > 0:
            response = HttpHelper.send_activates(self.tracking_manager.config, activates)
            if response is None or response.status_code >= 400:
                for h in activates:
                    self.tracking_manager.activateQueue.put(h, block=False)
            return response, activates
        return None, activates

    # def _print_pool(self, tag=""):
    #     self.tracking_manager._print_pool(tag)

    def get_hit_cache_interface(self):
        if self.tracking_manager.cache_manager is not None:
            if isinstance(self.tracking_manager.cache_manager, HitCacheImplementation):
                return self.tracking_manager.cache_manager
        return None


class ContinuousCacheStrategy(TrackingManagerCacheStrategyAbstract):

    def __init__(self, tracking_manager):
        TrackingManagerCacheStrategyAbstract.__init__(self, tracking_manager)
        self.tracking_manager = tracking_manager
        self.hit_cache_interface = TrackingManagerCacheStrategyAbstract.get_hit_cache_interface(self)

    def add_hit(self, hit, new=True):
        if hit.check_data_validity():
            TrackingManagerCacheStrategyAbstract.cache_hits(self, [hit])
            if TrackingManagerCacheStrategyAbstract.add_hit(self, hit, new):
                # TrackingManagerCacheStrategyAbstract.cache_hits(self, [hit])
                TrackingManagerCacheStrategyAbstract.check_max_pool_size(self)

    def add_hits(self, hits, new=True):
        added_hits = TrackingManagerCacheStrategyAbstract.add_hits(self, hits, new)
        TrackingManagerCacheStrategyAbstract.check_max_pool_size(self)  # todo test with TF
        return added_hits

    def delete_hits_by_id(self, ids, delete_consent_hits=True):
        removed_ids = TrackingManagerCacheStrategyAbstract.delete_hits_by_visitor_id(self, ids, delete_consent_hits)
        if len(removed_ids) > 0:
            try:
                if self.hit_cache_interface is not None:
                    self.hit_cache_interface.flush_hits(removed_ids)
            except Exception as e:
                log_exception(TAG_CACHE_MANAGER, e, traceback.format_exc())
        return removed_ids

    def delete_hits_by_visitor_id(self, visitor_id, delete_consent_hits=True):
        removed_ids = TrackingManagerCacheStrategyAbstract.delete_hits_by_visitor_id(self, visitor_id,
                                                                                     delete_consent_hits)
        if len(removed_ids) > 0:
            try:
                if self.hit_cache_interface is not None:
                    self.hit_cache_interface.flush_hits(removed_ids)
            except Exception as e:
                log_exception(TAG_CACHE_MANAGER, e, traceback.format_exc())
        return removed_ids

    def lookup_pool(self):
        return TrackingManagerCacheStrategyAbstract.lookup_pool(self)

    def cache_pool(self):
        return TrackingManagerCacheStrategyAbstract.cache_pool(self)

    def send_hits_batch(self):
        response, batch = TrackingManagerCacheStrategyAbstract.send_hits_batch(self)
        if response is not None and response.status_code <= 400:
            batch_hits_ids = [item.id for item in batch.hits]
            if self.hit_cache_interface is not None:
                self.hit_cache_interface.flush_hits(batch_hits_ids)

    def send_activates_batch(self, hit=None):
        response, activates = TrackingManagerCacheStrategyAbstract.send_activates_batch(self, hit)
        if response is not None and response.status_code <= 400:
            activates_ids = [item.id for item in activates]
            if self.hit_cache_interface is not None:
                print("TM FLUSH ACTIVATE : " + str(activates_ids))
                self.hit_cache_interface.flush_hits(activates_ids)

    def polling(self):
        return TrackingManagerCacheStrategyAbstract.polling(self)


class PeriodicCacheStrategy(TrackingManagerCacheStrategyAbstract):

    def __init__(self, tracking_manager):
        TrackingManagerCacheStrategyAbstract.__init__(self, tracking_manager)
        self.tracking_manager = tracking_manager
        self.hit_cache_interface = TrackingManagerCacheStrategyAbstract.get_hit_cache_interface(self)

    def add_hit(self, hit, new=True):
        if TrackingManagerCacheStrategyAbstract.add_hit(self, hit, new):
            TrackingManagerCacheStrategyAbstract.check_max_pool_size(self)

    def add_hits(self, hits, new=True):
        added_hits = TrackingManagerCacheStrategyAbstract.add_hits(self, hits, new)
        TrackingManagerCacheStrategyAbstract.check_max_pool_size(self)  # todo test with TF
        return added_hits

    def delete_hits_by_id(self, ids, delete_consent_hits=True):
        removed_ids = TrackingManagerCacheStrategyAbstract.delete_hits_by_visitor_id(self, ids, delete_consent_hits)
        return removed_ids

    def delete_hits_by_visitor_id(self, visitor_id, delete_consent_hits=True):
        removed_ids = TrackingManagerCacheStrategyAbstract.delete_hits_by_visitor_id(self, visitor_id,
                                                                                     delete_consent_hits)
        return removed_ids

    def lookup_pool(self):
        return TrackingManagerCacheStrategyAbstract.lookup_pool(self)

    def cache_pool(self):
        return TrackingManagerCacheStrategyAbstract.cache_pool(self)

    def send_hits_batch(self):
        response, batch = TrackingManagerCacheStrategyAbstract.send_hits_batch(self)

    def send_activates_batch(self, hit=None):
        response, activates = TrackingManagerCacheStrategyAbstract.send_activates_batch(self, hit)

    def polling(self):
        TrackingManagerCacheStrategyAbstract.polling(self)
        if self.hit_cache_interface is not None:
            self.hit_cache_interface.flush_all_hits()
        self.cache_pool()


class NoBatchingCacheStrategy(TrackingManagerCacheStrategyAbstract):

    def __init__(self, tracking_manager):
        TrackingManagerCacheStrategyAbstract.__init__(self, tracking_manager)
        self.tracking_manager = tracking_manager
        self.hit_cache_interface = TrackingManagerCacheStrategyAbstract.get_hit_cache_interface(self)

    def add_hit(self, hit, new=True):
        if hit.check_data_validity():
            if isinstance(hit, _Activate):
                response = HttpHelper.send_activates(self.tracking_manager.config, hit)
            else:
                response = HttpHelper.send_hit(self.tracking_manager.config, hit)
            if response is None or response.status_code >= 400:
                TrackingManagerCacheStrategyAbstract.cache_hits(self, [hit])
            return True
        else:
            log(TAG_TRACKING_MANAGER, LogLevel.ERROR, ERROR_INVALID_HIT.format(hit.type, hit.id))
            TrackingManagerCacheStrategyAbstract.delete_hits_by_visitor_id(self, [hit.id], True)
            return False

    def send_hits_batch(self, hit=None):
        response, batch = TrackingManagerCacheStrategyAbstract.send_hits_batch(self)
        if response is not None and response.status_code <= 400:
            batch_hits_ids = [item.id for item in batch.hits]
            if self.hit_cache_interface is not None:
                self.hit_cache_interface.flush_hits(batch_hits_ids)

    def send_activates_batch(self, hit=None):
        response, activates = TrackingManagerCacheStrategyAbstract.send_activates_batch(self, hit)
        if response is not None and response.status_code <= 400:
            activates_ids = [item.id for item in activates]
            if self.hit_cache_interface is not None:
                self.hit_cache_interface.flush_hits(activates_ids)

    def polling(self):
        return TrackingManagerCacheStrategyAbstract.polling(self)
