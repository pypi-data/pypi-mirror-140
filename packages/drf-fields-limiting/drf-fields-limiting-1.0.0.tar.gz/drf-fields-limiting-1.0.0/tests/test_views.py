import pytest

from rest_framework import (
    serializers,
    status,
)
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from drf_fields_limiting.views import LimitedFieldsView


factory = APIRequestFactory()


class ExampleSerializer(serializers.Serializer):
    choice_field = serializers.ChoiceField(['circle', 'triangle', 'square'])
    integer_field = serializers.IntegerField(min_value=1, max_value=1024)
    char_field = serializers.CharField(required=False, min_length=2, max_length=20)


class ExampleView(LimitedFieldsView):
    """Example view."""
    serializer_class = ExampleSerializer
    use_defaults_in_limited_fields_config = False

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={'choice_field': 'circle', 'integer_field': 1, 'char_field': 'abc'})
        serializer.is_valid()
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


@pytest.mark.parametrize("fields,expected", [
    (None, {'choice_field': 'circle', 'integer_field': 1, 'char_field': 'abc'}),
    ('choice_field,integer_field', {'choice_field': 'circle', 'integer_field': 1}),
])
def test_fields_limiting(fields, expected):
    params = {}
    if fields:
        params['HTTP_FIELDS'] = fields
    request = factory.get('/', **params)

    view = ExampleView.as_view()
    response = view(request=request)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected


def test_post_method():
    request = factory.post('/', {}, HTTP_FIELDS='choice_field,integer_field')

    view = ExampleView.as_view()
    response = view(request=request)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {'choice_field': 'circle', 'integer_field': 1, 'char_field': 'abc'}


@pytest.mark.parametrize("fields", ['', 'other_field'])
def test_invalid_fields_limiting(fields):
    request = factory.get('/', HTTP_FIELDS=fields)
    view = ExampleView.as_view()
    response = view(request=request)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {'detail': 'Bad content of Fields HTTP Header.'}
