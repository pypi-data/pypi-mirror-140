from rest_framework.generics import GenericAPIView

from drf_fields_limiting.mixins import LimitedFieldsViewMixin


class LimitedFieldsView(LimitedFieldsViewMixin, GenericAPIView):
    pass
