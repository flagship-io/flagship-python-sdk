import traceback
import uuid
from enum import Enum

from flagship import Status, LogLevel
from flagship.constants import TAG_GET_FLAG, TAG_FLAG_USER_EXPOSITION, TAG_UPDATE_CONTEXT, TAG_VISITOR, \
    ERROR_UPDATE_CONTEXT_TYPE, ERROR_UPDATE_CONTEXT_EMPTY_KEY
from flagship.errors import FlagNotFoundException, FlagExpositionNotFoundException, FlagTypeException
from flagship.hits import _Activate
from flagship.utils import pretty_dict, log_exception, log
from flagship.visitor_strategies import IVisitorStrategy, PanicStrategy, DefaultStrategy, NoConsentStrategy, \
    NotReadyStrategy


class Visitor(IVisitorStrategy):
    class Instance(Enum):
        """
        This class specifies how Flagship SDK should handle the newly created visitor instance.
        """

        SINGLE_INSTANCE = "SINGLE_INSTANCE",
        """
        The  newly created visitor instance will be returned and saved into the Flagship singleton.
        Call `Flagship.get_visitor()` to retrieve the instance.
        This option should be adopted on applications that handle only one visitor at the same time.
        """

        NEW_INSTANCE = "NEW_INSTANCE"
        """
        The newly created visitor instance wont be saved and will simply be returned. Any previous visitor instance will
        have to be recreated. This option should be adopted on applications that handle multiple visitors at the same 
        time.
        """

    def __init__(self, configuration_manager, visitor_id, **kwargs):
        """
        Flagship visitor representation.
        @param configuration_manager:
        @param visitor_id:
        @param kwargs:
        """
        super(Visitor, self).__init__(self)
        self._configuration_manager = configuration_manager
        self._config = configuration_manager.flagship_config

        self.is_authenticated = self._get_arg(kwargs, 'authenticated', bool, False)
        self.visitor_id = visitor_id
        self.anonymous_id = str(uuid.uuid4()) if self.is_authenticated is True else None
        from flagship.flagship_context import FlagshipContext
        self.context = FlagshipContext.load()
        self._modifications = dict()
        self.has_consented = self._get_arg(kwargs, 'consent', bool, True)
        self.set_consent(self.has_consented)
        self.update_context(self._get_arg(kwargs, 'context', dict, {}))
        self.exposed_variations = []
        self.assignations = {}
        self.lookup_visitor()
        print('d')

    # @param_types_validator(True, str, [int, float, str])
    def _update_context(self, key, value):
        from flagship.flagship_context import FlagshipContext
        existing_context = FlagshipContext.exists(key)
        if existing_context:
            if FlagshipContext.is_valid(self, existing_context, value, True):
                self.context[existing_context.value[0]] = value
        else:
            if key is None or len(str(key)) <= 0 or (not isinstance(key, str) and not isinstance(key, FlagshipContext)):
                log(TAG_UPDATE_CONTEXT, LogLevel.ERROR, "[" + TAG_VISITOR.format(self.visitor_id) + "] " +
                    ERROR_UPDATE_CONTEXT_EMPTY_KEY)
            elif not isinstance(value, str) and not isinstance(value, int) and not isinstance(value, float) \
                    and not isinstance(value, bool):
                log(TAG_UPDATE_CONTEXT, LogLevel.ERROR, "[" + TAG_VISITOR.format(self.visitor_id) + "] " +
                    ERROR_UPDATE_CONTEXT_TYPE.format(key, "str, int, float, bool"))
            else:
                self.context[key] = value

    def _expose_flag(self, key):
        try:
            modification = self._get_modification(key)
            if modification is None:
                raise FlagExpositionNotFoundException(self.visitor_id, key)
            # HttpHelper.send_activates(self._config, _Activate(self.visitor_id, self.anonymous_id,
            #                                                   modification.variation_group_id,
            #                                                   modification.variation_id))
            self.send_hit(_Activate(self.visitor_id, self.anonymous_id,
                                    modification.variation_group_id,
                                    modification.variation_id))
            if modification.variation_id not in self.exposed_variations:
                self.exposed_variations.append(modification.variation_id)
                self.cache_visitor()
        except Exception as e:
            log_exception(TAG_FLAG_USER_EXPOSITION, e, traceback.format_exc())

    def _get_modification(self, key):
        if key not in self._modifications:
            return None
        return self._modifications[key]

    def _get_flag_value(self, key, default):
        try:
            modification = self._get_modification(key)
            if modification is None:
                raise FlagNotFoundException(self.visitor_id, key)
            if not isinstance(default, type(modification.value)):
                raise FlagTypeException(self.visitor_id, key)
            value = modification.value if modification is not None else default
            return value
        except Exception as e:
            log_exception(TAG_GET_FLAG, e, traceback.format_exc())
            return default

    def _get_strategy(self):
        import flagship
        if flagship.Flagship.status().value < Status.PANIC.value:
            return NotReadyStrategy(visitor=self)
        elif flagship.Flagship.status() == Status.PANIC:
            return PanicStrategy(visitor=self)
        elif self.has_consented is False:
            return NoConsentStrategy(visitor=self)
        else:
            return DefaultStrategy(visitor=self)

    # def _send_context_request(self):
    #     self._get_strategy().send_hit(_Segment(self._context))

    def __str__(self):
        return pretty_dict({
            "visitor_id": self.visitor_id,
            "anonymous_id": self.anonymous_id,
            "has_consented": self.has_consented,
            "is_authenticated": self.is_authenticated,
            "context": self.context,
            "flags": self._flags_to_dict()
        })

    def _get_arg(self, kwargs, name, c_type, default, ):
        return kwargs[name] if name in kwargs and isinstance(kwargs[name], c_type) else default

    def _flags_to_dict(self):
        flags = dict()
        for k, v in self._modifications.items():
            flags[k] = v.value
        return flags

    def add_new_assignment_to_history(self, variation_group_id, variation_id):
        pass

    #     Methods from Visitor Strategy

    def update_context(self, context):
        """
        Update the visitor context values, matching the given keys, used for targeting.

        A new context value associated with this key will be created if there is no previous matching value.
        Context keys must be Str, and values types must be one of the following : Number, Bool, Str.

        Once the visitor context is updated, it is required to update the current flags by calling fetch_flags().

        @param context: Tuple (key, value) or dict.
        @return:
        """
        return self._get_strategy().update_context(context)

    def fetch_flags(self):
        """
        This function will update all the campaigns flags from the server according to the visitor context.
        @return:
        """
        return self._get_strategy().fetch_flags()

    def get_flag(self, key, default):
        """
        This function will return a flag object containing the current value returned by Flagship and the associated
        campaign information. If the key is not found an empty Flag object with the default value will be returned.

        @param key: key associated to the flag.
        @param default: fallback default value to use
        @return: Flag
        """
        return self._get_strategy().get_flag(key, default)

    def send_hit(self, hit):
        """
        Send a Hit to Flagship servers for reporting.
        @param hit: Hit to track.
        @return:
        """
        return self._get_strategy().send_hit(hit)

    def set_consent(self, consent):
        """
        Specify if the visitor has consented for personal data usage. When false some features will be deactivated,
        cache will be deactivated and cleared.
        @param consent: bool for consent.
        @return:
        """
        self._get_strategy().set_consent(consent)
        if not consent:
            self.flush_visitor()
            self.flush_hits()

    def authenticate(self, visitor_id):
        """
        Tag the current visitor as authenticated, This will insure to keep the same experience after fetch_flags().

        Once authenticated, it is required to update the current flags by calling fetch_flags() again.

        @param visitor_id of the current authenticated visitor.
        @return:
        """
        self._get_strategy().authenticate(visitor_id)

    def unauthenticate(self):
        """
        Tag the current visitor as unauthenticated, This will insure to get back to the initial experience after
        fetch flags.

        Once unauthenticated, it is required to update the current flags by calling fetch_flags() again.

        @return:
        """
        self._get_strategy().unauthenticate()

    def cache_visitor(self):
        self._get_strategy().cache_visitor()

    def lookup_visitor(self):
        self._get_strategy().lookup_visitor()

    def flush_visitor(self):
        self._get_strategy().flush_visitor()

    def flush_hits(self):
        self._get_strategy().flush_hits()


