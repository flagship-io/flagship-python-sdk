#URLS
URL_DECISION_API = "https://decision.flagship.io/v2/"
URL_CAMPAIGNS = "/campaigns/?exposeAllKeys=true"
URL_ARIANE = "https://ariane.abtasty.com/"


#TAGS
TAG_MAIN = "Flagship"
TAG_INITIALIZATION = "Initialization"
TAG_STATUS = "Status"
TAG_VISITOR = "Visitor:{}"
TAG_UPDATE_CONTEXT = "Update Context"
TAG_HTTP_REQUEST = "Http Request"
TAG_PARSING = "Parsing api response"
TAG_PARSING_CAMPAIGNS = "Campaigns parsing"
TAG_PARSING_VARIATION_GROUP = "Variation group parsing"
TAG_PARSING_VARIATION = "Variation parsing"
TAG_PARSING_MODIFICATION = "Modification parsing"
TAG_PANIC = "Panic Status"
TAG_FETCH_FLAGS = "Fetch flags"
TAG_GET_FLAG = "Fetch flags"
TAG_FLAG_USER_EXPOSITION = "Flag user exposition"


# INFO
INFO_STATUS_CHANGED = "SDK status has changed ({})"
INFO_READY = "Flagship version {} has started successfully.\nConfiguration: {}"

#DEBUG
DEBUG_CONTEXT = "Context have been updated with success.\n{}"
DEBUG_REQUEST = "{} {} {} {}ms\n"
DEBUG_FETCH_FLAGS = "Flags have been updated.\n{}"

#WARNING
WARNING_PANIC = "Panic mode is enabled : all features are disabled except 'fetchFlags()'."

# ERRORS
ERROR_PARAM_TYPE = "Parameter '{}' for function '{}' is not valid. Expecting {} type."
ERROR_PARSING_CAMPAIGN = "An error occurred while parsing campaign json object."
ERROR_PARSING_VARIATION_GROUP = "An error occurred while parsing variation group json object."
ERROR_PARSING_VARIATION = "An error occurred while parsing variation json object."
ERROR_PARSING_MODIFICATION = "An error occurred while parsing modification json object."
ERROR_FLAG_NOT_FOUND = "Flag key '{}' has not been found for visitor '{}'. Default value have been returned."
ERROR_FLAG_EXPOSITION_FLAG_NOT_FOUND = "Flag key '{}' has not been found for visitor '{}'. No flag exposition will be "\
                                       "sent. "



