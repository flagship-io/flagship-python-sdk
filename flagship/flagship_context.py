from enum import Enum

from flagship import log, LogLevel
from flagship.constants import TAG_UPDATE_CONTEXT, TAG_VISITOR, ERROR_UPDATE_CONTEXT_RESERVED, ERROR_UPDATE_CONTEXT_TYPE


def get_version():
    from flagship import __version__
    return __version__

class FlagshipContext(Enum):
    """
    DEVICE_LOCALE = Define the current device locale in the visitor context. (must be a iso3 code str)

    DEVICE_TYPE = Define the current device type in the visitor context. Must be a DeviceType value.

    DEVICE_MODEL = Define the current device model (Google Pixel 3) in the visitor context. Must be a str.

    LOCATION_CITY = Define the current city location in the visitor context. Must be a str.

    LOCATION_REGION = Define the current region location in the visitor context. Must be a str.

    LOCATION_COUNTRY = Define the current country location in the visitor context. Must be a str.

    LOCATION_LAT = Define the current latitude location in the visitor context. Must be a float.

    LOCATION_LONG = Define the current longitude location in the visitor context. Must be a float.

    OS_NAME = Define the current OS name in the visitor context. Must be a str.

    OS_VERSION_NAME = Define the current OS version name in the visitor context. Must be a str.

    CARRIER_NAME = Define the current carrier name in the visitor context. Must be str.

    INTERNET_CONNECTION = Define the current connection type in the visitor context. Must be a str.

    APP_VERSION_NAME = Define the current app version in the visitor context. Must be a str.

    APP_VERSION_CODE = Define the current app version in the visitor context. Must be an int >= 0.

    INTERFACE_NAME = Define the current interface name or URL in the visitor context. Must be a str.

    FLAGSHIP_CLIENT = Reserved by Flagship.

    FLAGSHIP_VERSION = Reserved by Flagship.
    """

    DEVICE_LOCALE = 'sdk_deviceLanguage', '', str
    DEVICE_TYPE = 'sdk_deviceType', ''
    DEVICE_MODEL = 'sdk_deviceModel', '', str
    LOCATION_CITY = 'sdk_city', '', str
    LOCATION_REGION = 'sdk_region', '', str
    LOCATION_COUNTRY = 'sdk_country', '', str
    LOCATION_LAT = 'sdk_lat', '', float
    LOCATION_LONG = 'sdk_long', '', float
    OS_NAME = 'sdk_osName', '', str
    OS_VERSION = 'sdk_osVersionName', '', str
    CARRIER_NAME = 'sdk_carrierName', '', str
    INTERNET_CONNECTION = 'sdk_internetConnection', '', str
    APP_VERSION_NAME = 'sdk_versionName', '', str
    APP_VERSION_CODE = 'sdk_versionCode', '', int
    INTERFACE_NAME = 'sdk_interfaceName', '', str
    FLAGSHIP_CLIENT = 'fs_client', 'python', str
    FLAGSHIP_VERSION = 'fs_version', get_version(), str

    @staticmethod
    def load():
        context = {}
        for item in FlagshipContext:
            key = item.value[0]
            value = item.value[1]
            if value is not None and len(str(value)) > 0 and FlagshipContext.is_valid(None, item, value, False):
                context[key] = value
        return context

    @staticmethod
    def exists(key):
        if isinstance(key, FlagshipContext):
            return key
        for item in FlagshipContext:
            if key == item.value[0]:
                return item
        return None

    @staticmethod
    def is_valid(visitor, flagship_context, value, check_type=True):
        try:
            if flagship_context.value[0].startswith("fs_"):
                if visitor is not None:
                    log(TAG_UPDATE_CONTEXT, LogLevel.ERROR, "[" + TAG_VISITOR.format(visitor._visitor_id) + "] " +
                        ERROR_UPDATE_CONTEXT_RESERVED.format(flagship_context.value[0]))
                return False
            if flagship_context is not None and check_type and not isinstance(value, flagship_context.value[2]):
                if visitor is not None:
                    log(TAG_UPDATE_CONTEXT, LogLevel.ERROR, "[" + TAG_VISITOR.format(visitor._visitor_id) + "] " +
                        ERROR_UPDATE_CONTEXT_TYPE.format(flagship_context, str(flagship_context.value[2])))
                return False
            return True
        except Exception as e:
            return False




