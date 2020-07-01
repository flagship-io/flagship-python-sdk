import json

from flagship.helpers.api import APIClient
from flagship.model.campaign import Campaign


class Bucketing:
    file_name = 'bucketing.json'

    @staticmethod
    def check_bucketing_file():
        import os
        return os.path.isfile(Bucketing.file_name)

    @staticmethod
    def updateBucketingFile(config):

        last_modified = None
        if Bucketing.check_bucketing_file():
            with open(Bucketing.file_name, 'r') as f:
                json_object = json.loads(f.read())
                last_modified = json_object['last_modified']
        code, last_modified, content = APIClient.update_bucketing_file(config, last_modified)
        if code == 200 and last_modified is not None and content is not None:
            json_object = {
                'last_modified': last_modified,
                'content': json.loads(content)
            }
            with open(Bucketing.file_name, 'w') as f:
                json.dump(json_object, f, indent=4)
            return True
        elif code == 304:
            return True
        else:
            return False

    @staticmethod
    def synchronize_modifications(config, visitor_id, context):
        if Bucketing.check_bucketing_file() is False:
            Bucketing.updateBucketingFile(config)
        with open(Bucketing.file_name, 'r') as f:
            json_object = json.loads(f.read())
            campaigns = Campaign.parse_campaigns(json_object['content'], visitor_id)
            return campaigns
