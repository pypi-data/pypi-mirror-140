# DRF session filtering

![example workflow](https://github.com/innovationinit/drf-session-filtering/actions/workflows/test-package.yml/badge.svg?branch=main)
[![Coverage Status](https://coveralls.io/repos/github/innovationinit/drf-session-filtering/badge.svg)](https://coveralls.io/github/innovationinit/drf-session-filtering)


## About

This package provides a Custom Models, Serializers, Backends and Views to facilitate saving filters in sessions.

## Install

```bash
pip install drf-session-filtering
```

## Usage

Define a `SESSION_MODEL_CONTAINER_KEY` setting:

```python
# settings.py

SESSION_MODEL_CONTAINER_KEY = 'session_objects'
```

Define a models and filter models that will be stored in session.

```python
# models.py 

from django.db import models

from session_filtering.models import BaseSessionModel


class Book(models.Model):
    title = models.CharField(max_length=100)
    issue_year = models.IntegerField()
    publisher = models.TextField()
    price = models.FloatField()
    ...

class BookFilterSessionModel(BaseSessionModel):
   pass
```

Define a filter set.

```python
# filters.py

from django_filters.rest_framework import FilterSet

from .models import Book


class BookFilter(FilterSet):
    
    class Meta:
        model = Book
        fields = {
            'title': ['exact', 'icontains'],
            'issue_year': ['gt'],
            'price': ['lt'],
            'publisher': ['exact', 'contains'],
        }

```

Define a serializers for models and filter models.

```python
# serializers.py

from rest_framework import serializers
from session_filtering.serializers import (
    FilterBaseSerializer,
    SessionSaveFilterMixin,
)

from .filters import BookFilter
from .models import Book


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = '__all__'


class BookFilterSerializer(SessionSaveFilterMixin, FilterBaseSerializer):

    class Meta:
        filter_class = BookFilter
```

Define a filter view and a model viewset using filter serializer and filter model defined before.

```python
# views.py

from rest_framework.generics import GenericAPIView
from rest_framework.mixins import *
from rest_framework.viewsets import *

from session_filtering.views import BaseFilterMixin
from session_filtering.backends import SessionFilterBackend

from .filters import BookFilter
from .models import Book, BookFilterSessionModel
from .serializers import BookSerializer, BookFilterSerializer

    
class BookFilterViewSet(
    BaseFilterMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    filter_class = BookFilter
    serializer_class = BookFilterSerializer
    filter_session_model = BookFilterSessionModel

    
class BooksViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    ViewSetMixin,
    GenericAPIView,
):
    serializer_class = BookSerializer
    filter_backends = [SessionFilterBackend]
    filter_class = BookFilter
    filter_session_model = BookFilterSessionModel
    filter_serializer_class = BookFilterSerializer
    filter_lookup_field = 'filterset_id'
    queryset = Book.objects.all()

```

## License
The Django Wicked Historian package is licensed under the [FreeBSD
License](https://opensource.org/licenses/BSD-2-Clause).
