import pytest

from django.urls import (
    include,
    path,
)

from rest_framework import (
    serializers,
    status,
)
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.routers import SimpleRouter
from rest_framework.test import APIRequestFactory

from drf_fields_limiting.operations import (
    ChainOperations,
    Noop,
    Only,
    PrefetchRelated,
    SelectRelated,
)
from drf_fields_limiting.serializers import LimitedFieldsSerializer
from drf_fields_limiting.viewsets import LimitedFieldsViewSet

from .models import (
    ExampleComplexModel,
    ExampleM2MModel,
    ExampleModel,
    ExampleNested,
    NestedM2MModel,
)

factory = APIRequestFactory()


class ExampleModelSerializer(LimitedFieldsSerializer, serializers.ModelSerializer):

    class Meta:
        model = ExampleModel
        fields = '__all__'


class ExampleComplexModelSerializer(LimitedFieldsSerializer, serializers.ModelSerializer):

    count = serializers.SerializerMethodField()

    class Meta:
        model = ExampleComplexModel
        fields = '__all__'

    def get_count(self, value):
        return 100


class ExampleViewSet(LimitedFieldsViewSet, RetrieveModelMixin, CreateModelMixin, ListModelMixin):

    serializer_class = ExampleModelSerializer
    queryset = ExampleModel.objects.all()

    @action(detail=True, methods=['GET'])
    def action(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ExampleComplexViewSet(LimitedFieldsViewSet, RetrieveModelMixin, CreateModelMixin, ListModelMixin):

    serializer_class = ExampleComplexModelSerializer
    queryset = ExampleComplexModel.objects.all()
    LIMITED_FIELDS_CONFIG = {
        'id': Only('id'),
        'text': Only('text'),
        'foreign': SelectRelated('foreign'),
        'nested': ChainOperations(
            SelectRelated('nested'),
            PrefetchRelated('nested__many_to_many'),
        ),
        'many_to_many': PrefetchRelated('many_to_many'),
        'count': Noop()
    }


router = SimpleRouter()
router.register(r'example', ExampleViewSet)
router.register(r'complex-example', ExampleComplexViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]


@pytest.fixture
@pytest.mark.django_db
def example_model():
    return ExampleModel.objects.create(text='text', number=3)


@pytest.fixture
@pytest.mark.django_db
def example_nested_model():
    m = ExampleNested.objects.create()
    m.many_to_many.add(NestedM2MModel.objects.create(number=1))
    return m


@pytest.fixture
@pytest.mark.django_db
def example_complex_model(example_model, example_nested_model):
    m = ExampleComplexModel.objects.create(text='text', foreign=example_model, nested=example_nested_model)
    m.many_to_many.add(ExampleM2MModel.objects.create(number=3))
    return m


@pytest.mark.django_db
@pytest.mark.parametrize("fields,expected", [
    (None, {'id': 1, 'text': 'text', 'number': 3}),
    ('text', {'text': 'text'}),
])
def test_retrieve_with_fields_limiting(settings, client, example_model, fields, expected):
    settings.ROOT_URLCONF='tests.test_viewsets'
    params = {}
    if fields:
        params['HTTP_FIELDS'] = fields
    response = client.get(f'/api/example/{example_model.id}/', **params)
    assert response.status_code == status.HTTP_200_OK, response.data
    assert response.data == expected


@pytest.mark.django_db
@pytest.mark.parametrize("fields,expected", [
    (None, [{'id': 1, 'text': 'text', 'number': 3}]),
    ('text', [{'text': 'text'}]),
])
def test_list_with_fields_limiting(settings, client, example_model, fields, expected):
    settings.ROOT_URLCONF='tests.test_viewsets'
    params = {}
    if fields:
        params['HTTP_FIELDS'] = fields
    response = client.get(f'/api/example/', **params)
    assert response.status_code == status.HTTP_200_OK, response.data
    assert response.data == expected


@pytest.mark.django_db
def test_create_with_fields_limiting(settings, client):
    settings.ROOT_URLCONF = 'tests.test_viewsets'
    response = client.post(f'/api/example/', {'text': 'xyz'}, HTTP_FIELDS='text')
    assert response.status_code == status.HTTP_201_CREATED, response.data
    assert response.data == {'id': 1, 'text': 'xyz', 'number': 1}


@pytest.mark.django_db
def test_action_with_fields_limiting(settings, client, example_model):
    settings.ROOT_URLCONF = 'tests.test_viewsets'
    response = client.get(f'/api/example/{example_model.id}/action/', HTTP_FIELDS='text')
    assert response.status_code == status.HTTP_200_OK, response.data
    assert response.data == {'text': 'text'}


@pytest.mark.django_db
@pytest.mark.parametrize("fields", ['', 'other_field'])
def test_invalid_fields_limiting(settings, client, example_model, fields):
    settings.ROOT_URLCONF = 'tests.test_viewsets'
    response = client.get(f'/api/example/{example_model.id}/', HTTP_FIELDS=fields)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, ExampleModel.objects.all().values_list('id', 'text')
    assert response.data == {'detail': 'Bad content of Fields HTTP Header.'}


@pytest.mark.django_db
@pytest.mark.parametrize("fields,expected,num_queries", [
    (None, {'id': 1, 'text': 'text', 'foreign': 1, 'nested': 1, 'many_to_many': [1], 'count': 100}, 3),
    ('text', {'text': 'text'}, 1),
])
def test_retrieve_complex_with_fields_limiting(settings, client, django_assert_num_queries, example_complex_model, fields, expected, num_queries):
    settings.ROOT_URLCONF='tests.test_viewsets'
    params = {}
    if fields:
        params['HTTP_FIELDS'] = fields
    with django_assert_num_queries(num_queries):
        response = client.get(f'/api/complex-example/{example_complex_model.id}/', **params)
    assert response.status_code == status.HTTP_200_OK, response.data
    assert response.data == expected
