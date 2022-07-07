import time
from threading import Thread

import flagship
from flagship.constants import TAG_BUCKETING, INFO_BUCKETING_POLLING
from flagship.decision_manager import DecisionManager
from flagship.utils import log
from flagship.log_manager import LogLevel
from flagship.status import Status


class BucketingManager(DecisionManager):

    def __init__(self, config, update_status):
        super(BucketingManager, self).__init__(config, update_status)
        self._thread = None
        if flagship.Flagship.status().value < Status.READY.value:
            self.update_status(Status.POLLING)

    def init(self):
        if self._thread is None:
            self._thread = self.BucketingThread(self.flagship_config, None)
        self._thread.start_running()

    def stop(self):
        if self._thread is not None:
            self._thread.stop()

    def get_campaigns_modifications(self, visitor):
        pass

    class BucketingThread(Thread):

        def __init__(self, config, last_modified):
            Thread.__init__(self)
            self.flagship_config = config
            self.daemon = True
            self.is_running = False
            self.delay = config.polling_interval / 1000

        def run(self):
            while self.is_running:
                log(TAG_BUCKETING, LogLevel.DEBUG, INFO_BUCKETING_POLLING)
                time.sleep(self.delay)

        def start_running(self):
            if self.is_running is False:
                self.is_running = True
                self.start()

        def stop_running(self):
            self.is_running = False
