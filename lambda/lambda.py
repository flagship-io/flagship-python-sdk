from flagship import Flagship, LogLevel
from flagship.config import Bucketing
from flagship.hits import Screen
from flagship.tracking_manager import TrackingManagerConfig

Flagship.start('__env_id__', '__api_key__', Bucketing(timeout=3000,
                                                      log_level=LogLevel.ALL,
                                                      tracking_manager_config=TrackingManagerConfig(
                                                          time_interval=5000,
                                                          max_pool_size=5)))


def lambda_handler(event, context):
    visitor = Flagship.new_visitor('visitor-AAA', context={'isVIPUser': True})
    visitor.fetch_flags()
    value = visitor.get_flag("featureEnabled", False).value()

    visitor.send_hit(Screen("screen 1"))

    Flagship.stop()
    return value
