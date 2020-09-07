from enum import Enum


class PresetContext(Enum):

    FS_ALL_USERS = 'fs_all_users'
    FS_USERS = 'fs_users'
    DEVICE_LOCALE = 'sdk_deviceLanguage'
    DEVICE_TYPE = 'sdk_deviceType'
    DEVICE_MODEL = 'sdk_deviceModel'
    LOCATION_CITY = 'sdk_city'
    LOCATION_REGION = 'sdk_region'
    LOCATION_COUNTRY = 'sdk_country'
    LOCATION_LAT = 'sdk_lat'
    LOCATION_LONG = 'sdk_long'
    IP = 'sdk_ip'
    OS_NAME = 'sdk_osName'
    OS_VERSION = 'sdk_osVersion'
    API_LEVEL = 'sdk_apiLevel'
    PYTHON_VERSION = 'sdk_pythonVersion'
    CARRIER_NAME = 'sdk_carrierName'
    DEV_MODE = 'sdk_devMode'
    FIRST_TIME_INIT = 'sdk_firstTimeInit'
    VISITOR_ID = 'sdk_visitorId'
    INTERNET_CONNECTION = 'sdk_internetConnection'
    APP_VERSION_NAME = 'sdk_versionName'
    APP_VERSION_CODE = 'sdk_versionCode'
    FS_VERSION = 'sdk_fsVersion'
    INTERFACE_NAME = 'sdk_interfaceName'

    @staticmethod
    def load():
        context = {}
        for k in PresetContext:
            context[k.value] = ""
        return context
