# Django Hawk DRF

This package provides [Django Rest Framework](https://github.com/encode/django-rest-framework/) helper classes for use with [Django Hawk](https://github.com/uktrade/django-hawk).

## Installation

Read the [Django Hawk installation](https://github.com/uktrade/django-hawk#installation) documentation.

## Example usage

Read the [Django Hawk example usage](https://github.com/uktrade/django-hawk#example-usage) documentation.

```python
from django_hawk_drf.authentication import HawkAuthentication
from django_hawk.middleware import HawkResponseMiddleware

from django.utils.decorators import decorator_from_middleware

from rest_framework.viewsets import ViewSet


class ExampleViewSet(ViewSet):
    authentication_classes = (HawkAuthentication,)
    permission_classes = ()

    @decorator_from_middleware(HawkResponseMiddleware)
    def list(self, request):
        return super().list(request)
```

## Testing

Tests belong in the `/django_hawk_drf/tests/` directory. You can run the tests by installing the requirements like so:

```
pip install -r dev-requirements.txt
```

Now you can run the tests using the following command:

```
./manage.py test
```

### Tox tests

We use [tox](https://pypi.org/project/tox/) to test compatibility across different Django versions.

To run these tests with tox, just run the following:

```
tox
```

## Pushing to PyPI

- [PyPI Package](https://pypi.org/project/django-hawk-drf/)
- [Test PyPI Package](https://test.pypi.org/project/django-hawk-drf/)

Running `make build` will build the package into the `dist/` directory
Running `make push-pypi-test` will push the built package to Test PyPI
Running `make push-pypi` will push the built package to PyPI
