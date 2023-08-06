from rest_framework.viewsets import GenericViewSet

from drf_fields_limiting.mixins import LimitedFieldsViewSetMixin


class LimitedFieldsViewSet(LimitedFieldsViewSetMixin, GenericViewSet):
    pass
