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


class DecisionManager(IDecisionManager):
    __metaclass__ = ABCMeta

    def __init__(self, config, update_status):
        self.update_status = update_status
        self.flagship_config = config
        self.panic = False

    def init(self):
        pass

    def parse_campaign_response(self, content):
        if content is not None:
            campaigns = None
            try:
                campaigns_json = json.loads(content)
                if 'panic' in campaigns_json and campaigns_json['json'] is True:
                    self.panic = True
                    self.update_status(Status.PANIC)
                    log(TAG_PANIC, LogLevel.WARNING, WARNING_PANIC)
                if not self.panic:
                    campaigns = Campaign.parse_campaigns(campaigns_json['campaigns'])
                self.update_status(Status.READY)
                return campaigns
            except Exception as e:
                log_exception(TAG_PARSING, e, traceback.format_exc())
        return None

    @abstractmethod
    def stop(self):
        pass
