from abc import ABCMeta, abstractmethod


class VisitorCacheManager:
    __metaclass__ = ABCMeta
    __version__ = 1

    class __VisitorCacheMigration:
        __metaclass__ = ABCMeta

        def __init__(self, from_version, to_version):
            self.from_version = from_version
            self.to_version = to_version

        @abstractmethod
        def migrate(self, visitor_data):
            pass

        @abstractmethod
        def check_validity(self, visitor_data):
            pass

    class __Migration_0_1(__VisitorCacheMigration):

        def migrate(self, visitor_data):
            visitor_data['version'] = self.to_version
            visitor_data['migration'] = "migration"
            return visitor_data

        def check_validity(self, visitor_data):
            if 'version' not in visitor_data or (isinstance(visitor_data['version'], int) is False):
                return False
            if 'data' not in visitor_data or (isinstance(visitor_data['data'], dict) is False):
                return False
            if 'vId' not in visitor_data['data'] or (len(visitor_data['data']['vId']) <= 0) or\
                    ((isinstance(visitor_data['data']['vId'], str) is False) and (isinstance(visitor_data['data']['vId'], unicode) is False)):
                return False
            if 'vaIds' not in visitor_data['data'] or (isinstance(visitor_data['data']['vaIds'], list) is False):
                return False
            return True

    def __init__(self):
        self.__migrations = dict()
        self.__migrations[1] = VisitorCacheManager.__Migration_0_1(0, 1)
        # self.__migrations[2] = VisitorCacheManager.__Migration_0_1(0, 1)
        if len(self.__migrations) != VisitorCacheManager.__version__:
            raise Exception("VisitorCacheManager : migration is missing")

    def __build_visitor_data(self, visitor_id, variations):
        visitor_data = dict()
        visitor_data['version'] = VisitorCacheManager.__version__
        visitor_data['data'] = dict()
        visitor_data['data']['vId'] = visitor_id
        visitor_data['data']['vaIds'] = variations
        return visitor_data

    def migrate_and_check_validity(self, visitor_id, visitor_data):
        try:
            data = visitor_data
            version = data['version']
            if version < VisitorCacheManager.__version__:
                for v in range(version, VisitorCacheManager.__version__):
                    if v in self.__migrations:
                        migration = self.__migrations[v]
                        data = migration.migrate(data)
                        if migration.check_validity(data) is False:
                            return None
            elif version not in self.__migrations or self.__migrations[version].check_validity(data) is False:
                return None
            elif visitor_id != data['data']['vId']:
                return None
            return data
        except Exception as e:
            print(e)
            return None

    def _save_visitor_data(self, visitor_id, variations):
        visitor_data = self.__build_visitor_data(visitor_id, variations)
        self.save(visitor_id, visitor_data)

    def _lookup_visitor_data(self, visitor_id):
        visitor_data = self.lookup(visitor_id)
        verified_visitor_data = self.migrate_and_check_validity(visitor_id, visitor_data)
        return verified_visitor_data

    @abstractmethod
    def save(self, visitor_id, visitor_data):
        pass

    @abstractmethod
    def lookup(self, visitor_id):
        pass
