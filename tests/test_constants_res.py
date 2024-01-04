
DECISION_API_URL = 'https://decision.flagship.io/v2/_env_id_/campaigns/?exposeAllKeys=true'

# NO_CONSENT_PARAM = '&sendContextEvent=false'
EVENTS_URL = 'https://events.flagship.io'
ACTIVATE_URL = 'https://decision.flagship.io/v2/activate'
BUCKETING_URL = 'https://cdn.flagship.io/_env_id_/bucketing.json'
SEGMENT_URL = 'https://decision.flagship.io/v2/_env_id_/events'

API_RESPONSE_1 = '{"campaigns":[{"variationGroupId":"c348750k33nnjpaaaaaa","type":"ab","id":"c348750k33nnjpzzzzzz","variation":{"modifications":{"type":"JSON","value":{"json":{"string":"a","variation":1},"string":null}},"id":"c348750k33nnjpeeeeee","reference":false},"slug":null},{"variationGroupId":"bmsorfe4jaeg0grrrrrr","type":"toggle","id":"bmsorfe4jaeg0gtttttt","variation":{"modifications":{"type":"FLAG","value":{"featureEnabled":true}},"id":"bmsorfe4jaeg0gyyyyyy","reference":false},"slug":"enableFeatureVIP"},{"variationGroupId":"bmsor064jaeg0guuuuuu","type":"ab","id":"bmsor064jaeg0giiiiii","variation":{"modifications":{"type":"JSON","value":{"visitorIdColor":"#E5B21D","title":"Hello"}},"id":"bmsor064jaeg0goooooo","reference":false},"slug":null}],"visitorId":"_visitor_id_x"}'
API_RESPONSE_2 = '{"campaigns":[{"variationGroupId":"c348750k33nnjpwwwwww","type":"ab","id":"c348750k33nnjpxxxxxx","variation":{"modifications":{"type":"JSON","value":{"json":{"variation":2},"string":"b"}},"id":"c3487s7q7be3d7cccccc","reference":false},"slug":null},{"variationGroupId":"bmsor064jaeg0gvvvvvv","type":"ab","id":"bmsor064jaeg0gbbbbbb","variation":{"modifications":{"type":"JSON","value":{"visitorIdColor":"#7300C2","title":"Hey"}},"id":"bmsor064jaeg0gnnnnnn","reference":false},"slug":null}],"visitorId":"_visitor_ze"}'
API_RESPONSE_3 = '{"visitorId":"visitor_xxx","campaigns":[],"panic":true}'

BUCKETING_RESPONSE_1 = '{"campaigns":[{"variationGroups":[{"variations":[{"allocation":100,"modifications":{"type":"FLAG","value":{"featureEnabled":true}},"id":"xxxx"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":true,"key":"isVIPUser"}]}]},"id":"yyyy"},{"variations":[{"allocation":100,"modifications":{"type":"FLAG","value":{"featureEnabled":false}},"id":"cccc"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":false,"key":"isVIPUser"}]}]},"id":"vvvv"}],"type":"toggle","id":"aaaa"},{"id":"bu6lgeu3bdt014iawwww","type":"perso","variationGroups":[{"id":"bu6lgeu3bdt014iaxxxx","targeting":{"targetingGroups":[{"targetings":[{"operator":"CONTAINS","key":"sdk_deviceModel","value":["Google Pixel 3","Google Pixel X","Google Pixel 0"]}]}]},"variations":[{"id":"bu6lgeu3bdt014iacccc","modifications":{"type":"JSON","value":{"target":null}},"reference":true},{"id":"bu6lgeu3bdt014iavvvv","modifications":{"type":"JSON","value":{"target":"is"}},"allocation":100}]},{"id":"bu6lttip17b01emhbbbb","targeting":{"targetingGroups":[{"targetings":[{"operator":"NOT_CONTAINS","key":"sdk_deviceModel","value":["Google Pixel 9","Google Pixel 9000"]}]}]},"variations":[{"id":"bu6lttip17b01emhnnnn","modifications":{"type":"JSON","value":{"target":null}},"reference":true},{"id":"bu6lttip17b01emhqqqq","modifications":{"type":"JSON","value":{"target":"is not"}},"allocation":100}]}]},{"variationGroups":[{"variations":[{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":null}},"id":"zzzz","reference":true},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":1111}},"id":"eeee"},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":3333}},"id":"rrrr"},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":22.22,"rank":2222}},"id":"tttt"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":"password","key":"access"}]}]},"id":"yyyy"}],"type":"ab","id":"iiii"}]}'
BUCKETING_LAST_MODIFIED_1 = "Fri,  05 Jun 2020 12:20:40 GMT"
BUCKETING_CACHED_RESPONSE_1 = '{"last_modified":"Fri,  05 Jun 2020 12:20:40 GMT","data":{"campaigns":[{"variationGroups":[{"variations":[{"allocation":100,"modifications":{"type":"FLAG","value":{"featureEnabled":true}},"id":"xxxx"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":true,"key":"isVIPUser"}]}]},"id":"yyyy"},{"variations":[{"allocation":100,"modifications":{"type":"FLAG","value":{"featureEnabled":false}},"id":"cccc"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":false,"key":"isVIPUser"}]}]},"id":"vvvv"}],"type":"toggle","id":"aaaa"},{"id":"bu6lgeu3bdt014iawwww","type":"perso","variationGroups":[{"id":"bu6lgeu3bdt014iaxxxx","targeting":{"targetingGroups":[{"targetings":[{"operator":"CONTAINS","key":"sdk_deviceModel","value":["Google Pixel 3","Google Pixel X","Google Pixel 0"]}]}]},"variations":[{"id":"bu6lgeu3bdt014iacccc","modifications":{"type":"JSON","value":{"target":null}},"reference":true},{"id":"bu6lgeu3bdt014iavvvv","modifications":{"type":"JSON","value":{"target":"is"}},"allocation":100}]},{"id":"bu6lttip17b01emhbbbb","targeting":{"targetingGroups":[{"targetings":[{"operator":"NOT_CONTAINS","key":"sdk_deviceModel","value":["Google Pixel 9","Google Pixel 9000"]}]}]},"variations":[{"id":"bu6lttip17b01emhnnnn","modifications":{"type":"JSON","value":{"target":null}},"reference":true},{"id":"bu6lttip17b01emhqqqq","modifications":{"type":"JSON","value":{"target":"is not"}},"allocation":100}]}]},{"variationGroups":[{"variations":[{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":null}},"id":"zzzz","reference":true},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":1111}},"id":"eeee"},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":null,"rank":3333}},"id":"rrrr"},{"allocation":25,"modifications":{"type":"JSON","value":{"rank_plus":22.22,"rank":2222}},"id":"tttt"}],"targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","value":"password","key":"access"}]}]},"id":"yyyy"}],"type":"ab","id":"iiii"}]}}'

BUCKETING_RESPONSE_2 = '{"campaigns":[{"id":"bs8qvmo4nlr01fl9aaaa","type":"ab","variationGroups":[{"id":"bs8qvmo4nlr01fl9bbbb","targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","key":"fs_all_users","value":""}]}]},"variations":[{"id":"bs8qvmo4nlr01fl9cccc","modifications":{"type":"JSON","value":{"variation":null}},"reference":true},{"id":"bs8qvmo4nlr01fl9dddd","modifications":{"type":"JSON","value":{"variation":1}},"allocation":25},{"id":"bs8r09g4nlr01c77eeee","modifications":{"type":"JSON","value":{"variation":2}},"allocation":25},{"id":"bs8r09g4nlr01cdkffff","modifications":{"type":"JSON","value":{"variation":3}},"allocation":25},{"id":"bs8r09hsbs4011lbgggg","modifications":{"type":"JSON","value":{"variation":4}},"allocation":25}]}]},{"id":"bs8r119sbs4016mehhhh","type":"ab","variationGroups":[{"id":"bs8r119sbs4016meiiii","targeting":{"targetingGroups":[{"targetings":[{"operator":"EQUALS","key":"fs_all_users","value":""}]}]},"variations":[{"id":"bs8r119sbs4016mejjjj","modifications":{"type":"JSON","value":{"variation50":null}},"reference":true},{"id":"bs8r119sbs4016mekkkk","modifications":{"type":"JSON","value":{"variation50":1}},"allocation":50},{"id":"bs8r119sbs4016mellll","modifications":{"type":"JSON","value":{"variation50":2}},"allocation":50}]}]}]}'
BUCKETING_RESPONSE_PANIC = '{"panic":true,"campaigns":[]}'
BUCKETING_RESPONSE_EMPTY = '{"campaigns":[]}'