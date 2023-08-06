# DRF fields limiting

![example workflow](https://github.com/innovationinit/drf-fields-limiting/actions/workflows/test-package.yml/badge.svg?branch=main)
[![Coverage Status](https://coveralls.io/repos/github/innovationinit/drf-fields-limiting/badge.svg)](https://coveralls.io/github/innovationinit/drf-fields-limiting)


## About

This package provides utils for Django Rest Framework API views and serializers for limiting fields returned in responses thus limiting size and complexity of database requests.

## Install

```bash
pip install drf-fields-limiting
```

## Usage

Inherit from `LimitedFieldsView` or `LimitedFieldsViewSet` and configure it to enable fields limiting.
View limits fields of serialized object in response with respect to `Fields` HTTP header.

If header is not present or is empty show all fields. Fields limiting works only in GET requests.

LIMITED_FIELDS_CONFIG holds map of field name - operation to perform on queryset (from `fields_limiting.operations`).
It should contains entries for all fields declared in serializer_class.

```python
...
class MySerializer(LimitedFieldsSerializer, serializers.ModelSerializer):
    
    class Meta:
        model = MyModel
        fields = (
            'char_field',
            'int_field',
            'foreign',
        )
    ...

class MyViewSet(LimitedFieldsViewSet, viewsets.ModelViewSet):
    ...
    LIMITED_FIELDS_CONFIG = {
        'char_field': Only('char_field'),
        'int_field': Only('int_field'),
        'foreign': SelectRelated('foreign'),
    }
    serializer_class = MySerializer
    ...
```

All available operations are in `drf_fields_limiting.operations` module.

Example GET query:
```
GET /api/v1/base/my/ HTTP/1.1
Authorization: Token h3r315myt0k3n
Accept: application/json
Content-Type: application/json
Fields: char_field,int_field
```

## License
The DRF complete autocomplete package is licensed under the [FreeBSD
License](https://opensource.org/licenses/BSD-2-Clause).
