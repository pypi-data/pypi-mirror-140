from rest_framework import serializers

from drf_fields_limiting.constants import ALL_FIELDS


class LimitedFieldsSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        self._fields_limited_to = kwargs.pop('fields_limited_to', ALL_FIELDS)
        super().__init__(*args, **kwargs)

    def get_fields(self):
        fields = super().get_fields()

        if self._fields_limited_to != ALL_FIELDS:
            limited_fields = {}
            for field in self._fields_limited_to:
                limited_fields[field] = fields[field]
            return limited_fields

        return fields
