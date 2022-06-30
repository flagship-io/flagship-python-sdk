#URLS
_URL_DECISION_API = "https://decision.flagship.io/v2/"
_URL_CAMPAIGNS = "/campaigns/?exposeAllKeys=true"


#TAGS
_TAG_MAIN = "Flagship"
_TAG_INITIALIZATION = "Initialization"
_TAG_STATUS = "Status"
_TAG_VISITOR = "Visitor:{}"
_TAG_UPDATE_CONTEXT = "Update Context"
_TAG_HTTP_REQUEST = "Http Request"
_TAG_PARSING = "Parsing api response"
_TAG_PARSING_CAMPAIGNS = "Campaigns parsing"
_TAG_PARSING_VARIATION_GROUP = "Variation group parsing"
_TAG_PARSING_VARIATION = "Variation parsing"
_TAG_PARSING_MODIFICATION = "Modification parsing"
_TAG_PANIC = "Panic Status"
_TAG_FETCH_FLAGS = "Fetch flags"


# INFO
_INFO_STATUS_CHANGED = "SDK status has changed ({})"
_INFO_READY = "Flagship version {} has started successfully.\nConfiguration: {}"

#DEBUG
_DEBUG_CONTEXT = "Context have been updated with success.\n{}"
_DEBUG_REQUEST = "{} {} {} {}ms\n"
_DEBUG_FETCH_FLAGS = "Flags have been updated.\n{}"

#WARNING
_WARNING_PANIC = "Panic mode is enabled : all features are disabled except 'fetchFlags()'."

# ERRORS
_ERROR_PARAM_TYPE = "Parameter '{}' for function '{}' is not valid. Expecting {} type."
_ERROR_PARSING_CAMPAIGN = "An error occurred while parsing campaign json object."
_ERROR_PARSING_VARIATION_GROUP = "An error occurred while parsing variation group json object."
_ERROR_PARSING_VARIATION = "An error occurred while parsing variation json object."
_ERROR_PARSING_MODIFICATION = "An error occurred while parsing modification json object."



