import json
from enum import Enum


class HitType(Enum):
    PAGE = 'SCREENVIEW'

class Hit:
    _k_origin = 'dl'  # origin
    _k_env_id = 'cid'  # env_id
    _k_visitor_id = 'vid'  # visitor id
    _k_type = 't'
    _k_ds = 'ds'

    def __init__(self, hit_type):
        self._data = {self._k_type: hit_type.value, self._k_ds: 'APP'}

    def add_config(self, env_id, visitor_id):
        self._data[self._k_env_id] = env_id
        self._data[self._k_visitor_id] = visitor_id

    def z(self):
        return self


class Page(Hit):
    def __init__(self, origin: str):
        super().__init__(HitType.PAGE)
        self._data[self._k_origin] = origin

    def withA(self):
        return self

    def withB(self):
        return self


    def __str__(self):
        return 'Page : ' + json.dumps(self._data)
