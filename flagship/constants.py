# URLS
URL_DECISION_API = "https://decision.flagship.io/v2/"
URL_CAMPAIGNS = "/campaigns/?exposeAllKeys=true"
URL_TRACKING = "https://events.flagship.io/"
URL_ACTIVATE = URL_DECISION_API + "activate"
URL_BUCKETING = "https://cdn.flagship.io/{}/bucketing.json"
URL_CONTEXT = "https://decision.flagship.io/v2/{}/events"
# URL_CONTEXT_PARAM = "&sendContextEvent=false"

# TAGS
TAG_MAIN = "Flagship"
TAG_INITIALIZATION = "Initialization"
TAG_STATUS = "Status"
TAG_VISITOR = "Visitor:{}"
TAG_UPDATE_CONTEXT = "Update Context"
TAG_TRACKING = "Tracking"
TAG_HTTP_REQUEST = "Http Request"
TAG_PARSING = "Parsing api response"
TAG_PARSING_CAMPAIGNS = "Campaigns parsing"
TAG_PARSING_VARIATION_GROUP = "Variation group parsing"
TAG_PARSING_VARIATION = "Variation parsing"
TAG_PARSING_MODIFICATION = "Modification parsing"
TAG_PANIC = "Panic Status"
TAG_FETCH_FLAGS = "FetchFlags"
TAG_GET_FLAG = "GetFlag"
TAG_FLAG_USER_EXPOSITION = "ExposeFlag"
TAG_FLAG = "Flag"
TAG_BUCKETING = "Bucketing"
TAG_AUTHENTICATE = "Authenticate"
TAG_UNAUTHENTICATE = "Unauthenticate"
TAG_TRACKING_MANAGER = 'Tracking Manager'

# INFO
INFO_STATUS_CHANGED = "SDK status has changed ({})"
INFO_READY = "Flagship version {} has started successfully.\nConfiguration: {}"
INFO_BUCKETING_POLLING = "Polling event."

# DEBUG
DEBUG_CONTEXT = "Context have been updated with success.\n{}"
DEBUG_REQUEST = "{} {} {} {}ms\n"
DEBUG_FETCH_FLAGS = "Flags have been updated.\n{}"

# WARNING
WARNING_PANIC = "Panic mode is enabled : all features are disabled except 'fetchFlags()'."
WARNING_DEFAULT_CONFIG = "No flagship configuration is passed. Default configuration will be used."

# ERRORS
ERROR_INITIALIZATION_PARAM = "Params 'envId' and 'apiKey' must not be None or emtpy."
ERROR_CONFIGURATION = "Configuration has failed, the SDK has not been initialized successfully."
ERROR_PARAM_TYPE = "Parameter '{}' for function '{}' is not valid. Expecting {} type."
ERROR_PARSING_CAMPAIGN = "An error occurred while parsing campaign json object."
ERROR_PARSING_VARIATION_GROUP = "An error occurred while parsing variation group json object."
ERROR_PARSING_VARIATION = "An error occurred while parsing variation json object."
ERROR_PARSING_MODIFICATION = "An error occurred while parsing modification json object."
ERROR_UPDATE_CONTEXT_RESERVED = "Context key '{}' is reserved by flagship and can't be overridden."
ERROR_UPDATE_CONTEXT_TYPE = "Context key '{}' value must be of type: '{}'."
ERROR_UPDATE_CONTEXT_EMPTY = "Context key '{}' will be ignored as its value is empty'."
ERROR_UPDATE_CONTEXT_EMPTY_KEY = "Context key must be a non null or empty 'str'."

ERROR_FLAG_NOT_FOUND = "Flag key '{}' has not been found for visitor '{}'. Default value have been returned."
ERROR_FLAG_TYPE_DIFFERENT = "Flag key '{}' has been found for visitor '{}' but with a different type. " \
                            "Default value have been returned."
ERROR_FLAG_EXPOSITION_FLAG_NOT_FOUND = "Flag key '{}' has not been found for visitor '{}'. No flag exposition will be " \
                                       "sent. "
ERROR_METHOD_DEACTIVATED = "Method '{}' have been deactivated: {}"
ERROR_FLAG_METHOD_DEACTIVATED = "Flag '{}' method '{}' have been deactivated: {}"
ERROR_METHOD_DEACTIVATED_PANIC = "SDK is running in panic mode."
ERROR_METHOD_DEACTIVATED_NOT_READY = "SDK is not started yet."
ERROR_METHOD_DEACTIVATED_NO_CONSENT = "visitor '{}' has not given his consent."

ERROR_BUCKETING_REQUEST = "An error occurred happened during decision file request."
ERROR_BUCKETING_XPC_DISABLED = "The '{}' method is disabled in Bucketing configuration."

ERROR_TRACKING_HIT_SUBCLASS = "send_hit() param must be a subclass of Hit."
ERROR_INVALID_HIT = "Hit {} {} has invalid data and wont be sent."
