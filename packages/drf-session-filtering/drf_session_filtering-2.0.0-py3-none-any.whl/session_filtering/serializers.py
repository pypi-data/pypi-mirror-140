# -*- coding: utf-8 -*-

from collections import OrderedDict
import copy

from django.forms import fields

from rest_framework.fields import (
    BooleanField,
    CharField,
    ChoiceField,
    DecimalField,
    DateField,
    DateTimeField,
    EmailField,
    FileField,
    FilePathField,
    FloatField,
    ImageField,
    IntegerField,
    IPAddressField,
    # ModelField,  # maybe will be used in the future;
    MultipleChoiceField,
    NullBooleanField,
    # SkipField,  # maybe will be used in the future;
    SlugField,
    TimeField,
    URLField,
)
from rest_framework.serializers import Serializer
from rest_framework.utils.field_mapping import ClassLookupDict

from .field_mapping import get_field_kwargs


class SessionSaveFilterMixin(object):
    instance = None

    def create(self, validated_data):
        session_class = self.context['view'].filter_session_model
        return session_class(validated_data)

    def to_representation(self, instance):
        ret = super(SessionSaveFilterMixin, self).to_representation(instance)
        ret.update({'id': instance.id})
        return ret

    def save(self, **kwargs):
        assert self.is_valid()

        if self.instance is not None:
            self.instance.data_dictionary.update(self.validated_data)
        else:
            self.instance = self.create(self.validated_data)

        self.instance.store(session=self._context['request'].session, serializer=self)


class FilterBaseSerializer(Serializer):
    serializer_field_mapping = {
        fields.CharField: CharField,
        fields.BooleanField: BooleanField,
        fields.IntegerField: IntegerField,
        fields.DateField: DateField,
        fields.DateTimeField: DateTimeField,
        fields.DecimalField: DecimalField,
        fields.FileField: FileField,
        fields.EmailField: EmailField,
        fields.FloatField: FloatField,
        fields.ImageField: ImageField,
        fields.NullBooleanField: NullBooleanField,
        fields.SlugField: SlugField,
        fields.TimeField: TimeField,
        fields.URLField: URLField,
        fields.GenericIPAddressField: IPAddressField,
        fields.ChoiceField: ChoiceField,
        fields.MultipleChoiceField: MultipleChoiceField,
        fields.TypedChoiceField: ChoiceField,
        fields.TypedMultipleChoiceField: MultipleChoiceField,
        fields.FilePathField: FilePathField,
    }
    serializer_choice_field = ChoiceField

    def get_fields(self):
        """Prepare dict of field names mapped to field instances

        Return the dict of field names -> field instances that should be
        used for `self.fields` when instantiating the serializer.
        """
        assert hasattr(self, 'Meta'), (
            'Class {serializer_class} missing "Meta" attribute'.format(
                serializer_class=self.__class__.__name__
            )
        )
        assert hasattr(self.Meta, 'filter_class'), (
            'Class {serializer_class} missing "Meta.filter_class" attribute'.format(
                serializer_class=self.__class__.__name__
            )
        )

        declared_fields = copy.deepcopy(self._declared_fields)
        FilterClass = getattr(self.Meta, 'filter_class')

        # Retrieve metadata about fields & relationships on the model class.

        field_names = self.get_field_names(declared_fields)

        # Determine the fields that should be included on the serializer.
        fields = OrderedDict()

        for field_name in field_names:
            # If the field is explicitly declared on the class then use that.
            if field_name in declared_fields:
                fields[field_name] = declared_fields[field_name]
                continue

            # Determine the serializer field class and keyword arguments.
            field_class, field_kwargs = self.build_field(
                field_name, FilterClass
            )

            # Create the serializer field.
            fields[field_name] = field_class(**field_kwargs)

        return fields

    def get_field_names(self, declared_fields):
        filter_class = getattr(self.Meta, 'filter_class', None)
        field_names = filter_class().filters.keys()
        for fname in declared_fields:
            if fname not in field_names:
                field_names.append(fname)
        return field_names

    def build_field(self, field_name, filter_class):
        filter_instance = filter_class()
        if field_name in filter_instance.filters:
            form_filter_field = filter_instance.form.fields[field_name]
            return self.build_standard_field(field_name, form_filter_field)

        raise Exception('Field Not Found.')

    def build_standard_field(self, field_name, filter_field):
        """Create regular model fields."""

        is_not_choice_field = not isinstance(filter_field, fields.ChoiceField)

        if is_not_choice_field and hasattr(filter_field, 'choices'):
            field_class = self.serializer_choice_field
        else:
            field_mapping = ClassLookupDict(self.serializer_field_mapping)
            field_class = field_mapping[filter_field]

        # write here a custom method which will get the kwargs
        field_kwargs = get_field_kwargs(filter_field)

        if 'choices' in field_kwargs:
            if field_class is NullBooleanField:
                field_kwargs['allow_null'] = True
            if is_not_choice_field:
                field_class = self.serializer_choice_field
            valid_kwargs = {
                'read_only', 'write_only',
                'required', 'default', 'initial', 'source',
                'label', 'help_text', 'style',
                'error_messages', 'validators', 'allow_null', 'allow_blank',
                'choices',
            }
            for key in list(field_kwargs.keys()):
                if key not in valid_kwargs:
                    field_kwargs.pop(key)

        return field_class, field_kwargs
