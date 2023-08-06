import functools

from django.db.models import Prefetch as DBPrefetch
from django.db.models.constants import LOOKUP_SEP


class BaseQuerysetOperation(object):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, queryset):
        raise NotImplementedError()


class ChainOperations(BaseQuerysetOperation):

    def __init__(self, *operations, **kwargs):
        assert operations
        self.operations = operations
        super().__init__(**kwargs)

    def __call__(self, queryset):
        return functools.reduce(lambda q, operation: operation(q), self.operations, queryset)


class Only(BaseQuerysetOperation):

    def __call__(self, queryset):
        return self.set_only(queryset, self.args)

    @staticmethod
    def set_only(queryset, fields):
        # Try to retrieve already set only fields and merge them with new ones if necessary
        old_fields, defer = queryset.query.deferred_loading
        new_fields = set(fields)

        if not defer:
            new_fields |= set(old_fields)

        return queryset.only(*new_fields)


class SelectRelated(BaseQuerysetOperation):

    def __call__(self, queryset):
        # Firstly set only on queryset to ensure presence of related fields in query
        qs = Only.set_only(queryset, {field.split(LOOKUP_SEP)[0] for field in self.args})
        return qs.select_related(*self.args)


def queryset_operation_factory(name, operation):
    return type(name, (BaseQuerysetOperation,), {'__call__': operation})


PrefetchRelated = queryset_operation_factory('PrefetchRelated', lambda self, q: q.prefetch_related(*self.args))
PrefetchObject = queryset_operation_factory('PrefetchObject', lambda self, q: q.prefetch_related(DBPrefetch(*self.args, **self.kwargs)))
Noop = queryset_operation_factory('Noop', lambda self, q: q)
