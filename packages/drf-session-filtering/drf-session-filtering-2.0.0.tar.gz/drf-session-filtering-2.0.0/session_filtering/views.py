# -*- coding: utf-8 -*-

from django.http import Http404


class BaseFilterMixin(object):
    lookup_field = 'filterset_id'
    filter_lookup_field = 'filterset_id'

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        object_id = self.request.query_params.get(self.filter_lookup_field) or self.kwargs.get(self.filter_lookup_field)
        filter_model_instance = self.filter_session_model.restore(
            session=self.request.session, object_id=object_id, serializer=self.get_serializer())

        if not filter_model_instance:
            raise Http404()

        return filter_model_instance
