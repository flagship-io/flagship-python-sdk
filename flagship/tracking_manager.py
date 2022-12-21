import time

from flagship.log_manager import LogLevel
from flagship.utils import log
from flagship.constants import TAG_TRACKING_MANAGER, ERROR_INVALID_HIT

try:
    from Queue import Queue
except ImportError:
    from queue import Queue
from abc import ABCMeta, abstractmethod
from enum import Enum
from threading import Thread

from flagship.hits import _Consent, _Batch
from flagship.http_helper import HttpHelper


class TrackingManagerCacheStrategyInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def add_hit(self, hit):
        pass

    @abstractmethod
    def add_hits(self, hits):
        pass

    @abstractmethod
    def delete_hits_by_id(self, ids):
        pass

    @abstractmethod
    def delete_hits_by_visitor_id(self, visitor_id):
        pass

    @abstractmethod
    def lookup_pool(self):
        pass

    @abstractmethod
    def cache_pool(self):
        pass

    @abstractmethod
    def send_batch(self):
        pass


class TrackingManagerStrategy(Enum):
    BATCHING_WITH_CONTINUOUS_CACHING_STRATEGY = 'BATCHING_WITH_CONTINUOUS_CACHING_STRATEGY'


class TrackingManagerConfig:

    DEFAULT_MAX_POOL_SIZE = 20
    DEFAULT_TIME_INTERVAL = 10000  # time in ms

    def __init__(self, **kwargs):
        self.strategy = kwargs['strategy'] if 'strategy' in kwargs \
            else TrackingManagerStrategy.BATCHING_WITH_CONTINUOUS_CACHING_STRATEGY
        self.time_interval = kwargs['time_interval'] if 'time_interval' in kwargs else self.DEFAULT_TIME_INTERVAL
        self.max_pool_size = kwargs['max_pool_size'] if 'max_pool_size' in kwargs else self.DEFAULT_MAX_POOL_SIZE


class TrackingManager(TrackingManagerCacheStrategyInterface, Thread):
    BATCH_MAX_SIZE = 2500000
    HIT_EXPIRATION = 14400000

    is_running = False
    hitQueue = Queue()

    def __init__(self, config):
        Thread.__init__(self)
        TrackingManagerCacheStrategyInterface.__init__(self)
        self.daemon = True  # Attach the thread to main thread
        self.config = config
        self.tracking_manager_config = config.tracking_manager_config
        self.time_interval = config.tracking_manager_config.time_interval
        self.strategy = self.get_strategy()

    def init(self, config):
        self.config = config
        self.tracking_manager_config = config.tracking_manager_config
        self.time_interval = config.tracking_manager_config.time_interval
        self.strategy = self.get_strategy()

        if self.time_interval > 0:
            self.start_running()

    def start_running(self):
        if self.is_running is False:
            self.is_running = True
            self.start()

    def run(self):
        while self.is_running:
            self.send_batch()
            time.sleep(self.time_interval / 1000.0)

    def stop_running(self):
        self.is_running = False

    def add_hit(self, hit):
        return self.strategy.add_hit(hit)

    def add_hits(self, hits):
        return self.strategy.add_hits(hits)

    def delete_hits_by_id(self, ids, delete_consent_hits=True):
        return self.strategy.delete_hits_by_id(ids, delete_consent_hits)

    def delete_hits_by_visitor_id(self, visitor_id, delete_consent_hits=True):
        return self.strategy.delete_hits_by_visitor_id(visitor_id, delete_consent_hits)

    def lookup_pool(self):
        return self.strategy.lookup_pool()

    def cache_pool(self):
        return self.strategy.cache_pool()

    def send_batch(self):
        return self.strategy.send_batch()

    def get_strategy(self):
        if self.tracking_manager_config.strategy == TrackingManagerStrategy.BATCHING_WITH_CONTINUOUS_CACHING_STRATEGY:
            return ContinuousCacheStrategy(self)


class TrackingManagerCacheStrategyAbstract(TrackingManagerCacheStrategyInterface):
    __metaclass__ = ABCMeta

    def __init__(self, tracking_manager):
        TrackingManagerCacheStrategyInterface.__init__(self)
        self.tracking_manager = tracking_manager

    def add_hit(self, hit, new=True):
        if hit.check_data_validity():
            if new and isinstance(hit, _Consent) and hit.consent is False:
                self.delete_hits_by_visitor_id(hit.visitor_id, False)
            self.tracking_manager.hitQueue.put(hit, block=False)
            log("DEBUG", LogLevel.WARNING, '#DB1 put hit: ' + str(hit.data()))
            log("DEBUG", LogLevel.WARNING, '#DB1 Queue size: ' + str(self.tracking_manager.hitQueue.qsize()))
            if self.tracking_manager.hitQueue.qsize() >= self.tracking_manager.tracking_manager_config.max_pool_size:
                log("DEBUG", LogLevel.WARNING, '#DB2 MAX LIMIT REACHED: ')
                self.send_batch()
            return True
        else:
            log(TAG_TRACKING_MANAGER, LogLevel.ERROR, ERROR_INVALID_HIT.format(hit.type, hit.id))
            # delete hit
            self.delete_hits_by_id([hit.id])
            return False

    def add_hits(self, hits):
        success_hits = list()
        for h in hits:
            if self.add_hit(h) is True:
                success_hits.append(h)
        return success_hits

    def delete_hits_by_id(self, ids, delete_consent_hits=True):
        removed_ids = list()
        for item in list(self.tracking_manager.hitQueue.queue):
            if item.id in ids:
                if isinstance(item, _Consent) and delete_consent_hits is False:
                    break
                else:
                    removed_ids.append(item.id)
                    self.tracking_manager.hitQueue.queue.remove(item)
        return removed_ids

    def delete_hits_by_visitor_id(self, visitor_id, delete_consent_hits=True):
        removed_ids = list()
        log("DEBUG", LogLevel.WARNING, '#DB3 delete queue: ' + str(self.tracking_manager.hitQueue.qsize()))
        log("DEBUG", LogLevel.WARNING, '#DB3.1 delete queue: ' + str(list(self.tracking_manager.hitQueue.queue)))
        for item in list(self.tracking_manager.hitQueue.queue):
            if item.visitor_id != visitor_id:
                log("DEBUG", LogLevel.WARNING,
                    '#DB3.1.1 delete: ' + str(item.visitor_id))
            if item.visitor_id == visitor_id:
                log("DEBUG", LogLevel.WARNING,
                    '#DB3.2 visitor_id: ' + str(visitor_id))
                # if isinstance(item, _Consent) and delete_consent_hits is False:
                #     break
                # else:
                if delete_consent_hits is not True and not isinstance(item, _Consent):
                    log("DEBUG", LogLevel.WARNING,
                        '#DB3.3 to delete: ' + str(item))
                    removed_ids.append(item.id)
                    self.tracking_manager.hitQueue.queue.remove(item)
                    log("DEBUG", LogLevel.WARNING,
                        '#DB3.4 delete queue: ' + str(list(self.tracking_manager.hitQueue.queue)))
        return removed_ids

    def lookup_pool(self):
        pass

    def cache_pool(self):
        # do nothing
        pass

    @abstractmethod
    def send_batch(self):
        batch = _Batch()
        while not self.tracking_manager.hitQueue.empty():
            h = self.tracking_manager.hitQueue.get(block=False)
            if h:
                batch.add_child(h)
            self.tracking_manager.hitQueue.task_done()
        if batch.size() > 0:
            log("DEBUG", LogLevel.WARNING, '#DB2 Send batch: ' + str(len(batch.hits)))
            HttpHelper.send_batch(self.tracking_manager.config, batch)


class ContinuousCacheStrategy(TrackingManagerCacheStrategyAbstract):

    def __init__(self, tracking_manager):
        TrackingManagerCacheStrategyAbstract.__init__(self, tracking_manager)
        self.tracking_manager = tracking_manager

    def add_hit(self, hit):
        return TrackingManagerCacheStrategyAbstract.add_hit(self, hit)

    def add_hits(self, hits):
        pass

    def delete_hits_by_id(self, ids, delete_consent_hits=True):
        pass

    def delete_hits_by_visitor_id(self, visitor_id, delete_consent_hits=True):
        return TrackingManagerCacheStrategyAbstract.delete_hits_by_visitor_id(self, visitor_id, delete_consent_hits)

    def lookup_pool(self):
        pass

    def cache_pool(self):
        pass

    def send_batch(self):
        return TrackingManagerCacheStrategyAbstract.send_batch(self)
