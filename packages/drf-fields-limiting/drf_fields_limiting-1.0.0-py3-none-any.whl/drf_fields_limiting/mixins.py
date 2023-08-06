import functools

from rest_framework.exceptions import ParseError

from drf_fields_limiting.operations import Only
from drf_fields_limiting.constants import ALL_FIELDS
from drf_fields_limiting.serializers import LimitedFieldsSerializer


class LimitedFieldsViewMixin(object):

    """Mixin that limits fields of serialized object in response with respect to Fields HTTP header.

    If header is not present or is empty show all fields. Fields limiting works only in GET requests.

    LIMITED_FIELDS_CONFIG holds map of field name - operation to perform on queryset (from fields_limiting.operations).
    It should contains entries for all fields declared in serializer_class.
    """

    LIMITED_FIELDS_CONFIG = {}
    use_defaults_in_limited_fields_config = True

    def __init__(self, **kwargs):
        self.fields_limited_to = ALL_FIELDS
        super().__init__(**kwargs)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self._setup_field_limiting(request)

    def get_serializer_class(self):
        serializer_class = super().get_serializer_class()

        if self.fields_limited_to != ALL_FIELDS:
            serializer_class = self._serializer_with_limited_fields(serializer_class)

        return serializer_class

    def get_serializer(self, *args, **kwargs):
        if self.fields_limited_to != ALL_FIELDS:
            kwargs.setdefault('fields_limited_to', self.fields_limited_to)
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        operations = (self.get_limited_fields_config()[field_name] for field_name in self.fields_limited_to)\
            if self.fields_limited_to != ALL_FIELDS else self.get_limited_fields_config().values()
        return functools.reduce(
            lambda q, operation: operation(q),
            operations,
            queryset,
        )

    def get_serializer_field_names(self, serializer_class=None):
        serializer = serializer_class() if serializer_class else self.get_serializer_class()()
        return serializer.get_fields().keys()

    def get_limited_fields_config(self, raw_config=None):
        raw_config = raw_config or self.LIMITED_FIELDS_CONFIG

        if not self.use_defaults_in_limited_fields_config:
            return raw_config

        config = {}

        for field in self.get_serializer_field_names():
            config[field] = raw_config.get(field, Only(field))

        return config

    def _setup_field_limiting(self, request):
        if hasattr(self, 'action'):
            if self.action in ['create', 'update', 'partial_update', 'metadata']:
                return
        elif request.method != 'GET':  # request is available
            return

        fields = request.META.get('HTTP_FIELDS', ALL_FIELDS)

        if fields == ALL_FIELDS:
            self.fields_limited_to = fields
            return

        limited_to = [field.strip() for field in fields.split(',')]

        if not limited_to or any(field not in self.get_serializer_field_names() for field in limited_to):
            raise ParseError("Bad content of Fields HTTP Header.")

        self.fields_limited_to = limited_to

    @staticmethod
    def _serializer_with_limited_fields(serializer_class):
        """If serializer class is not subclass of LimitedFieldsSerializer, create new class inheriting from both"""
        if issubclass(serializer_class, LimitedFieldsSerializer):
            return serializer_class

        return type(
            'LimitedFields{base}'.format(base=serializer_class.__name__),
            (LimitedFieldsSerializer, serializer_class),
            {'Meta': serializer_class.Meta} if 'Meta' in serializer_class.__dict__ else {},  # Some how some of metaclasses need Meta in dict
        )


class LimitedFieldsViewSetMixin(LimitedFieldsViewMixin):

    """Configure field limiting per action"""

    LIMITED_FIELDS_CONFIG_PER_ACTION = {}
    """Set per action configs. Default config is stored still in LIMITED_FIELDS_CONFIG"""

    def get_limited_fields_config(self, raw_config=None):
        action = self.action_map.get('get', None)

        if action is None or action not in self.LIMITED_FIELDS_CONFIG_PER_ACTION:
            return super(LimitedFieldsViewSetMixin, self).get_limited_fields_config(raw_config or self.LIMITED_FIELDS_CONFIG)

        return super(LimitedFieldsViewSetMixin, self).get_limited_fields_config(raw_config or self.LIMITED_FIELDS_CONFIG_PER_ACTION[action])
