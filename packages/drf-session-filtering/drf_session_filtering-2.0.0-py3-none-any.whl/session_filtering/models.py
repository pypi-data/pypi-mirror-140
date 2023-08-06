# -*- coding: utf-8 -*-

import json
import uuid

from django.conf import settings

from rest_framework.renderers import JSONRenderer


class BaseSessionModel(object):

    def __init__(self, data):
        """Save given data as property and generate unique id"""
        if not isinstance(data, dict):
            raise Exception('Data should be a dict instance')
        self.data_dictionary = data
        self.data_dictionary['id'] = data.get('id', uuid.uuid4().hex)

    def __getattribute__(self, name):
        """Firstly return attribute from data_dictionary"""
        data_dictionary = super(BaseSessionModel, self).__getattribute__('data_dictionary')
        if name in data_dictionary:
            return data_dictionary[name]
        return super(BaseSessionModel, self).__getattribute__(name)

    def store(self, session, serializer):
        serialized = JSONRenderer().render(serializer.to_representation(self)).decode('utf-8')
        model_container = session.get(settings.SESSION_MODEL_CONTAINER_KEY, {})
        model_container[self.id] = serialized
        session[settings.SESSION_MODEL_CONTAINER_KEY] = model_container
        session.save()

    @classmethod
    def restore(cls, session, object_id, serializer):
        if not object_id:
            return
        session_data = session.get(settings.SESSION_MODEL_CONTAINER_KEY, {}).get(object_id)
        if not session_data:
            return
        deserialized = json.loads(session_data)
        internal_data = serializer.to_internal_value(deserialized)
        internal_data['id'] = object_id
        return cls(internal_data)
