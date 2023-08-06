# -*- coding: utf-8 -*-

from django_filters.filters import (
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ParseError


class SessionFilterBackendDataMixin(object):

    """A mixin that create model instance from serializer."""

    @staticmethod
    def get_filter_model_instance(request, view, serializer):
        session_class = getattr(view, 'filter_session_model')
        filter_model_instance = session_class.restore(
            session=request.session,
            object_id=request.query_params.get(view.filter_lookup_field),
            serializer=serializer,
        )
        if not filter_model_instance and request.query_params.get(view.filter_lookup_field):
            raise ParseError('Filter ID not found in session')
        return filter_model_instance


class SessionFilterBackend(
    DjangoFilterBackend,
    SessionFilterBackendDataMixin,
):

    """A session filter backend that uses django-filter."""

    def filter_queryset(self, request, queryset, view):
        result_queryset = self.apply_filtering(request, queryset, view)
        return result_queryset

    def get_filter_data(self, request, view):
        filter_model_instance = self.get_filter_model_instance(request, view, serializer=view.filter_serializer_class())
        filter_class = getattr(view, 'filterset_class', None) or getattr(view, 'filter_class', None)
        multiple_choice_keys = self.get_multiple_choice_keys(filter_class)
        data = {}
        if filter_model_instance:
            data = filter_model_instance.data_dictionary
            for k, v in data.items():
                # this needs to be done because serializer
                # parses MultipleChoice fields values as sets,
                # which would broke during form validation
                if isinstance(v, set):
                    data[k] = list(v)
        for k, v in request.query_params.items():
            if k in multiple_choice_keys:
                # MultipleChoice fields need to be handled
                # separately because of Django's
                # MultiValueDict implementation
                data[k] = request.query_params.getlist(k)
            else:
                data[k] = v
        return data

    def apply_filtering(self, request, queryset, view):
        get_filter_class_method = getattr(self, 'get_filterset_class') if hasattr(self, 'get_filterset_class') else getattr(self, 'get_filter_class')
        filter_class = get_filter_class_method(view, queryset)
        if not filter_class:
            return queryset
        return filter_class(self.get_filter_data(request, view), queryset=queryset, request=request).qs

    @staticmethod
    def get_multiple_choice_keys(filter_class):
        return [
            key for key, filter_ in filter_class.base_filters.items()
            if isinstance(filter_, (MultipleChoiceFilter, ModelMultipleChoiceFilter))
        ]
