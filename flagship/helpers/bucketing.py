import json
import logging
import os
import time
from threading import Thread
from flagship.helpers.api import ApiManager


class BucketingObserver:

    def __init__(self):
        pass

    def bucketing_updated(self, last_modified, bucketing_file):
        pass

    def panic_mode_enabled(self, panic_mode):
        pass


class BucketingManager(BucketingObserver):
    file_name = 'bucketing.json'

    def __init__(self, config):
        BucketingObserver.__init__(self)
        self._config = config
        self._bucketing_data = None
        self._bucketing_thread = None
        self._last_modified = None
        self.panic_mode = False

    def init_bucketing(self):
        self._bucketing_data = BucketingManager.update_bucketing_data(self._config, self._last_modified)
        self.panic_mode = self.check_for_panic(self._bucketing_data)
        if self._bucketing_data is not None and 'last_modified' in self._bucketing_data:
            self._last_modified = self._bucketing_data['last_modified']
        if self._bucketing_thread is None:
            if self._config.bucketing_refresh_interval > 0:
                self._bucketing_thread = self.BucketingThread(self._config, self._last_modified)
                self._bucketing_thread.start_thread()
                self._bucketing_thread.attach(self)
            else:
                self._config.event_handler.on_log(logging.WARNING,
                                                  "Bucketing polling is disabled, panic mode will only "
                                                  "be activable/deactivable at start time.")

    def is_bucketing_thread_running(self):
        if self._bucketing_thread is not None:
            return self._bucketing_thread.is_running
        return False

    @staticmethod
    def check_for_panic(bucketing_data):
        if bucketing_data is not None and 'content' in bucketing_data:
            content = bucketing_data['content']
            return 'panic' in content
        return False

    def get_bucketing_data(self):
        return self._bucketing_data

    @staticmethod
    def load_bucketing_file():
        if os.path.isfile(BucketingManager.file_name):
            try:
                with open(BucketingManager.file_name, 'r') as f:
                    json_data = json.loads(f.read())
                    if 'content' in json_data and 'last_modified' in json_data:
                        return json_data
            except Exception as e:
                return None
        return None

    @staticmethod
    def update_bucketing_data(config, last_modified):

        bucketing_data = None
        if last_modified is None:
            bucketing_data = BucketingManager.load_bucketing_file()
            if bucketing_data is not None and 'last_modified' in bucketing_data:
                last_modified = bucketing_data['last_modified']
        code, last_modified, content = ApiManager.send_bucketing_request(config, last_modified)
        if code == 200 and last_modified is not None and content is not None:
            json_object = {
                'last_modified': last_modified,
                'content': content
            }
            with open(BucketingManager.file_name, 'w') as f:
                json.dump(json_object, f, indent=4)
            bucketing_data = json_object
        return bucketing_data

    def bucketing_updated(self, last_modified, bucketing_data):
        self._last_modified = last_modified
        self._bucketing_data = bucketing_data

    def panic_mode_enabled(self, panic_mode):
        self.panic_mode = panic_mode

    def close(self):
        if self._bucketing_thread is not None:
            self._bucketing_thread.stop_thread()

    class BucketingThread(Thread):

        _observers = []
        _last_modified = None
        is_running = False
        delay = 60
        panic_mode = False

        def __init__(self, config, last_modified):
            Thread.__init__(self)
            self.daemon = True
            self.config = config
            self.delay = self.config.bucketing_refresh_interval
            self._last_modified = last_modified

        def run(self):
            while self.is_running:
                bucketing_data = BucketingManager.update_bucketing_data(self.config, self._last_modified)
                if bucketing_data is not None:
                    try:
                        self.config.event_handler.on_log(logging.INFO, "[Bucketing] Bucketing data have been updated.")
                        panic_mode = BucketingManager.check_for_panic(bucketing_data)

                        if panic_mode != self.panic_mode:
                            self.panic_mode = panic_mode
                            self.notify_all_panic_mode(self.panic_mode)
                            self.config.event_handler.on_log(logging.INFO, "[Bucketing] Panic mode is " +
                                                             ("disabled." if self.panic_mode is False else "enabled."))

                        self._last_modified = bucketing_data['last_modified']
                        self.notify_all(self._last_modified, bucketing_data)
                    except Exception as e:
                        self.config.event_handler.on_log(logging.ERROR, "Bucketing update error.")
                time.sleep(self.delay)

        def start_thread(self):
            if self.is_running is False:
                self.is_running = True
                self.start()

        def stop_thread(self):
            del self._observers[:]
            self.is_running = False

        def attach(self, observer):
            self._observers.append(observer)

        def detach(self, observer):
            self._observers.remove(observer)

        def notify_all_panic_mode(self, panic_mode):
            for o in self._observers:
                o.panic_mode_enabled(panic_mode)

        def notify_all(self, last_modified, bucketing_data):
            for o in self._observers:
                o.bucketing_updated(last_modified, bucketing_data)
