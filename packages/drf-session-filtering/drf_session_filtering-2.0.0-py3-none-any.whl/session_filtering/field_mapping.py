# -*- coding: utf-8 -*-

from django.forms import fields
from django.template.defaultfilters import capfirst
from django.utils.translation import ugettext_lazy as _

from django.core import validators
from rest_framework.utils.field_mapping import NUMERIC_FIELD_TYPES
from rest_framework.validators import UniqueValidator


def get_field_kwargs(form_field):  # noqa
    kwargs = {}
    validator_kwarg = list(form_field.validators)

    # The following will only be used by ModelField classes.
    # Gets removed for everything else.
    # kwargs['form_field'] = form_field

    kwargs['label'] = capfirst(form_field.label)

    if form_field.help_text:
        kwargs['help_text'] = form_field.help_text

    max_digits = getattr(form_field, 'max_digits', None)
    if max_digits is not None or isinstance(form_field, fields.DecimalField):
        kwargs['max_digits'] = max_digits

    decimal_places = getattr(form_field, 'decimal_places', None)
    if decimal_places is not None or isinstance(form_field, fields.DecimalField):
        kwargs['decimal_places'] = decimal_places

    kwargs['required'] = form_field.required

    if not form_field.required:
        if not isinstance(form_field, fields.NullBooleanField):
            kwargs['allow_null'] = True

        if isinstance(form_field, fields.CharField):
            kwargs['allow_blank'] = True

    choices = getattr(form_field, 'choices', None)
    if isinstance(form_field, fields.NullBooleanField):
        choices = [
            (None, _('session_filtering.field_mapping.none')),
            (True, _('session_filtering.field_mapping.true')),
            (False, _('session_filtering.field_mapping.false')),
        ]

    if choices is not None:
        # If this model field contains choices, then return early.
        # Further keyword arguments are not valid.
        choices = list(choices)
        kwargs['choices'] = choices
        if choices and not form_field.required:
            first_value, first_label = choices[0]  # pylint: disable=unused-variable
            kwargs['default'] = first_value
        if isinstance(form_field, fields.MultipleChoiceField):
            kwargs['default'] = []
        return kwargs

    # Ensure that max_length is passed explicitly as a keyword arg,
    # rather than as a validator.
    max_length = getattr(form_field, 'max_length', None)
    if max_length is not None and isinstance(form_field, fields.CharField):
        kwargs['max_length'] = max_length
        validator_kwarg = [
            validator for validator in validator_kwarg
            if not isinstance(validator, validators.MaxLengthValidator)
        ]

    # Ensure that min_length is passed explicitly as a keyword arg,
    # rather than as a validator.
    min_length = next((
        validator.limit_value for validator in validator_kwarg
        if isinstance(validator, validators.MinLengthValidator)
    ), None)
    if min_length is not None and isinstance(form_field, fields.CharField):
        kwargs['min_length'] = min_length
        validator_kwarg = [
            validator for validator in validator_kwarg
            if not isinstance(validator, validators.MinLengthValidator)
        ]

    # Ensure that max_value is passed explicitly as a keyword arg,
    # rather than as a validator.
    max_value = next((
        validator.limit_value for validator in validator_kwarg
        if isinstance(validator, validators.MaxValueValidator)
    ), None)
    if max_value is not None and isinstance(form_field, NUMERIC_FIELD_TYPES):
        kwargs['max_value'] = max_value
        validator_kwarg = [
            validator for validator in validator_kwarg
            if not isinstance(validator, validators.MaxValueValidator)
        ]

    # Ensure that max_value is passed explicitly as a keyword arg,
    # rather than as a validator.
    min_value = next((
        validator.limit_value for validator in validator_kwarg
        if isinstance(validator, validators.MinValueValidator)
    ), None)
    if min_value is not None and isinstance(form_field, NUMERIC_FIELD_TYPES):
        kwargs['min_value'] = min_value
        validator_kwarg = [
            validator for validator in validator_kwarg
            if not isinstance(validator, validators.MinValueValidator)
        ]

    # URLField does not need to include the URLValidator argument,
    # as it is explicitly added in.
    if isinstance(form_field, fields.URLField):
        validator_kwarg = [
            validator for validator in validator_kwarg
            if not isinstance(validator, validators.URLValidator)
        ]

    # EmailField does not need to include the validate_email argument,
    # as it is explicitly added in.
    if isinstance(form_field, fields.EmailField):
        validator_kwarg = [
            validator for validator in validator_kwarg
            if validator is not validators.validate_email
        ]

    # SlugField do not need to include the 'validate_slug' argument,
    if isinstance(form_field, fields.SlugField):
        validator_kwarg = [
            validator for validator in validator_kwarg
            if validator is not validators.validate_slug
        ]

    if getattr(form_field, 'unique', False):
        validator = UniqueValidator(queryset=form_field.model._default_manager)
        validator_kwarg.append(validator)

    if validator_kwarg:
        kwargs['validators'] = validator_kwarg

    return kwargs
