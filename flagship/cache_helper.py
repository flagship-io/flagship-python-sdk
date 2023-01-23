__VISITOR_CACHE_VERSION__ = 1

import json
import traceback
from collections import OrderedDict

from flagship.constants import TAG_CACHE_MANAGER
from flagship.modification import Modification
from flagship.utils import log_exception


def visitor_to_cache_json(visitor):
    json = OrderedDict({
        'version': __VISITOR_CACHE_VERSION__,
        'data': {
            'visitorId': visitor.visitor_id,
            'anonymousId': visitor.anonymous_id,
            'isAuthenticated': visitor.is_authenticated,
            'consent': visitor.has_consented,
            'context': visitor.context,
            'campaigns': visitor_campaigns_to_json(visitor),
            'assignations': visitor.assignations
        }
    })
    return json


def visitor_campaigns_to_json(visitor):
    result = []

    for k, m in visitor._modifications.items():
        exists = False
        for result_campaign in result:
            if result_campaign['campaignId'] == m.campaign_id and result_campaign['variationGroupId'] \
                    == m.variation_group_id and result_campaign['variationId'] == m.variation_id:
                exists = True
                result_campaign['flags'][m.key] = m.value or None
                break
        if not exists:
            result.append({
                'campaignId': m.campaign_id,
                'variationGroupId': m.variation_group_id,
                'variationId': m.variation_id,
                'isReference': m.reference,
                'type': m.type,
                'slug': m.slug,
                'exposed': m.variation_id in visitor.exposed_variations,
                'flags': {
                    m.key: m.value or None
                }
            })
    return result


def load_visitor_from_json(visitor, visitor_data):

    def migration_1(visitor_m, data_m):
        campaigns = data_m['campaigns']
        for campaign in campaigns:
            campaign_id = campaign['campaignId']
            variation_group_id = campaign['variationGroupId']
            variation_id = campaign['variationId']
            is_reference = campaign['isReference']
            campaign_type = campaign['type']
            campaign_slug = campaign['slug']
            exposed = campaign['exposed']
            if exposed is True and variation_id not in visitor_m.exposed_variations:
                visitor_m.exposed_variations.append(variation_id)
            for key, value in campaign['flags'].items():
                visitor_m._modifications[key] = Modification(key, campaign_id, campaign_type, campaign_slug,
                                                             variation_group_id, variation_id, is_reference, value)
        visitor_m.assignations.update(data_m['assignations'])

    try:
        migrations = [migration_1, ]
        visitor_json = json.loads(visitor_data)
        version = visitor_json['version']
        data = visitor_json['data']
        migrations[version - 1](visitor, data)
    except Exception as e:
        log_exception(TAG_CACHE_MANAGER, e, traceback.format_exc())
