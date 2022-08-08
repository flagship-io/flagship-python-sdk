import json
import os
import time
import traceback
from threading import Thread

import flagship
from flagship.constants import TAG_BUCKETING, INFO_BUCKETING_POLLING, ERROR_BUCKETING_REQUEST, TAG_AUTHENTICATE, \
    TAG_UNAUTHENTICATE, ERROR_BUCKETING_XPC_DISABLED
from flagship.decision_manager import DecisionManager
from flagship.http_helper import HttpHelper
from flagship.utils import log, pretty_dict, log_exception
from flagship.log_manager import LogLevel
from flagship.status import Status


class BucketingManager(DecisionManager, Thread):

    local_decision_file_name = ".{}.decision"

    def __init__(self, config, update_status):
        Thread.__init__(self)
        super(BucketingManager, self).__init__(config, update_status)
        self.flagship_config = config
        self.daemon = True  # Attach the thread to main thread
        self.campaigns = None
        self.bucketing_file = None
        self.last_modified = None
        self.is_running = False
        self.delay = config.polling_interval / 1000
        if flagship.Flagship.status().value < Status.READY.value:
            self.update_status(Status.POLLING)
        self.load_local_decision_file()

    def init(self):
        if self.is_running is False:
            self.is_running = True
            self.start()

    def run(self):
        while self.is_running:
            log(TAG_BUCKETING, LogLevel.DEBUG, INFO_BUCKETING_POLLING)
            try:
                self.update_bucketing_file()
            except:
                pass
            time.sleep(self.delay)

    def stop(self):
        self.is_running = False
        self.stop()

    def update_bucketing_file(self):
        try:
            last_modified, results = HttpHelper.send_bucketing_request(self.flagship_config, self.last_modified)
            if last_modified is not None and results is not None:
                self.last_modified = last_modified
                # self.bucketing_file = json.loads(results)
                self.bucketing_file = results
                self.cache_local_decision_file()
            if self.bucketing_file is not None:
                bucketing_file_json = json.loads(self.bucketing_file)
                campaigns = self.parse_campaign_response(bucketing_file_json)
                if campaigns is not None:
                    self.campaigns = campaigns


        except:
            log(TAG_BUCKETING, LogLevel.ERROR, ERROR_BUCKETING_REQUEST)

    def get_campaigns_modifications(self, visitor):
        campaign_modifications = dict()
        try:
            for campaign in self.campaigns:
                for variation_group in campaign.variation_groups:
                    if variation_group.is_targeting_valid(dict(visitor._context)):
                        variation = variation_group.select_variation(visitor)
                        if variation is not None:
                            visitor.add_new_assignment_to_history(variation.variation_group_id, variation.variation_id)
                            modification_values = variation.get_modification_values()
                            if modification_values is not None:
                                campaign_modifications.update(modification_values)
                            break
            # send context event
            visitor._send_context_request()
            return True, campaign_modifications
        except Exception as e:
            log_exception(TAG_BUCKETING, e, traceback.format_exc())
        return False, None

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
                pass

    def cache_local_decision_file(self):
        try:
            file_name = self.local_decision_file_name.format(self.flagship_config.env_id)
            json_object = {
                "last_modified": self.last_modified,
                "data": self.bucketing_file
            }
            with open(file_name, 'w') as f:
                json.dump(json_object, f, indent=2)
        except:
            pass

    def authenticate(self, visitor, authenticated_id):
        log(TAG_AUTHENTICATE, LogLevel.ERROR, ERROR_BUCKETING_XPC_DISABLED.format("authenticate()"))

    def unauthenticate(self, visitor):
        log(TAG_UNAUTHENTICATE, LogLevel.ERROR, ERROR_BUCKETING_XPC_DISABLED.format("unauthenticate()"))
