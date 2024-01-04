from __future__ import unicode_literals
import io
import json
import os
import time
import traceback
from threading import Thread

import flagship
from flagship.constants import TAG_BUCKETING, INFO_BUCKETING_POLLING, ERROR_BUCKETING_REQUEST, TAG_AUTHENTICATE, \
    TAG_UNAUTHENTICATE, ERROR_BUCKETING_XPC_DISABLED
from flagship.decision_manager import DecisionManager
from flagship.hits import _Segment
from flagship.http_helper import HttpHelper
from flagship.utils import log, pretty_dict, log_exception
from flagship.log_manager import LogLevel
from flagship.status import Status


class BucketingManager(DecisionManager, Thread):

    local_decision_file_name = ".{}.decision"

    def __init__(self, config, update_status_callback):
        Thread.__init__(self)
        super(BucketingManager, self).__init__(config, update_status_callback)
        self.flagship_config = config
        self.daemon = True  # Attach the thread to main thread
        self.campaigns = None
        self.bucketing_file = None
        self.last_modified = None
        self.is_running = False
        if config.polling_interval > 0:
            self.delay = config.polling_interval / 1000.0
        else:
            self.delay = None
        if flagship.Flagship.status().value < Status.READY.value:
            self.update_status_callback(self.flagship_config, Status.POLLING)
        self.load_local_decision_file()

    def start_running(self):
        if self.delay is None:
            self.run_task()
        else:
            if self.is_running is False:
                self.is_running = True
                self.start()

    def run(self):
        while self.is_running:
            log(TAG_BUCKETING, LogLevel.DEBUG, INFO_BUCKETING_POLLING)
            self.run_task()
            time.sleep(self.delay)

    def run_task(self):
        try:
            self.update_bucketing_file()
        except Exception as e:
            log_exception(TAG_BUCKETING, e, traceback.format_exc())

    def stop_running(self):
        self.is_running = False

    def update_bucketing_file(self):
        try:
            last_modified, results = HttpHelper.send_bucketing_request(self.flagship_config, self.last_modified)
            if last_modified is not None and results is not None:
                self.last_modified = last_modified
                self.bucketing_file = json.loads(results)
                self.cache_local_decision_file()
            if self.bucketing_file is not None:
                campaigns = self.parse_campaign_response(self.bucketing_file)
                if campaigns is not None:
                    self.campaigns = campaigns
                self.update_status()
        except Exception as e:
            # log(TAG_BUCKETING, LogLevel.ERROR, ERROR_BUCKETING_REQUEST)
            log_exception(TAG_BUCKETING, e, traceback.format_exc())

    def get_campaigns_modifications(self, visitor):
        campaign_modifications = dict()
        try:
            if self.campaigns is not None:
                for campaign in self.campaigns:
                    for variation_group in campaign.variation_groups:
                        if variation_group.is_targeting_valid(dict(visitor.context)):
                            variation = variation_group.select_variation(visitor)
                            if variation is not None:
                                visitor.assignations[variation.variation_group_id] = variation.variation_id
                                modification_values = variation.get_modification_values()
                                if modification_values is not None:
                                    campaign_modifications.update(modification_values)
                                break
                self.send_context_hit(visitor)
            return True, campaign_modifications
        except Exception as e:
            log_exception(TAG_BUCKETING, e, traceback.format_exc())
        return False, None

    def send_context_hit(self, visitor):
        visitor.send_hit(_Segment(visitor.visitor_id, visitor.context))

    def load_local_decision_file(self):
        file_name = self.local_decision_file_name.format(self.flagship_config.env_id)
        if os.path.isfile(file_name):
            try:
                with open(file_name, 'r') as f:
                    json_data = json.loads(f.read())
                    if 'data' in json_data and 'last_modified' in json_data:
                        self.last_modified = json_data['last_modified']
                        self.bucketing_file = json_data['data']
            except Exception as e:
                log_exception(TAG_BUCKETING, e, traceback.format_exc())
                pass

    def cache_local_decision_file(self):
        try:
            file_name = self.local_decision_file_name.format(self.flagship_config.env_id)
            json_object = {
                'last_modified': self.last_modified,
                'data': self.bucketing_file
            }
            with open(file_name, 'w') as f:
                f.write(pretty_dict(json_object))
        except Exception as e:
            log_exception(TAG_BUCKETING, e, traceback.format_exc())

    def authenticate(self, visitor, authenticated_id):
        log(TAG_AUTHENTICATE, LogLevel.ERROR, ERROR_BUCKETING_XPC_DISABLED.format("authenticate()"))

    def unauthenticate(self, visitor):
        log(TAG_UNAUTHENTICATE, LogLevel.ERROR, ERROR_BUCKETING_XPC_DISABLED.format("unauthenticate()"))
