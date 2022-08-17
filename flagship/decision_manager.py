import traceback
from abc import ABCMeta, abstractmethod

from flagship.status import Status
from flagship.log_manager import LogLevel
from flagship.campaign import Campaign
from flagship.utils import log, log_exception
from flagship.constants import TAG_PARSING, WARNING_PANIC, TAG_PANIC
import json


class IDecisionManager:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_campaigns_modifications(self, visitor):
        pass

    @abstractmethod
    def update_status(self):
        pass

    @abstractmethod
    def authenticate(self, visitor, authenticated_id):
        pass

    @abstractmethod
    def unauthenticate(self, visitor):
        pass

class DecisionManager(IDecisionManager):
    __metaclass__ = ABCMeta

    def __init__(self, config, update_status_callback):
        self.update_status_callback = update_status_callback
        self.flagship_config = config
        self.panic = False

    def init(self):
        pass

    def parse_campaign_response(self, campaigns_json):
        if campaigns_json is not None:
            campaigns = None
            try:
                if 'panic' in campaigns_json and campaigns_json['panic'] is True:
                    self.panic = True
                else:
                    self.panic = False
                    campaigns = Campaign.parse_campaigns(campaigns_json)
                return campaigns
            except Exception as e:
                log_exception(TAG_PARSING, e, traceback.format_exc())
        return None

    def update_status(self):
        if self.update_status_callback is not None:
            if self.panic is True:
                self.update_status_callback(self.flagship_config, Status.PANIC)
                log(TAG_PANIC, LogLevel.WARNING, WARNING_PANIC)
            else:
                self.update_status_callback(self.flagship_config, Status.READY)


    @abstractmethod
    def stop(self):
        pass


