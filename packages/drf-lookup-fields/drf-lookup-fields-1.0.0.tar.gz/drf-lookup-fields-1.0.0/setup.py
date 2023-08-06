# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lookup_fields']

package_data = \
{'': ['*'],
 'lookup_fields': ['locale/en/LC_MESSAGES/*', 'locale/pl/LC_MESSAGES/*']}

install_requires = \
['Django>=2.0,<3.0', 'djangorestframework>=3.3.2']

setup_kwargs = {
    'name': 'drf-lookup-fields',
    'version': '1.0.0',
    'description': 'A package supplying tools for custom foreign-key fields lookup in drf-created WebAPI.',
    'long_description': '# Lookup Fields\n\n![Test package](https://github.com/innovationinit/drf-lookup-fields/actions/workflows/test-package.yml/badge.svg?branch=main)\n[![Coverage Status](https://coveralls.io/repos/github/innovationinit/drf-lookup-fields/badge.svg)](https://coveralls.io/github/innovationinit/drf-lookup-fields)\n\nThis package provides utils for changing lookup fields in requests to Django Rest Framework endpoints. It supports choosing lookup field for identifier of endpoint and identifiers used in related fields of serializers.\n\n## Per field lookup usage\n\nData for field should be supplied in `Content-Lookup-Fields` HTTP header as base64 encoded json object where keys are serializer fields names (if nested use dotted notation) and values are intended lookup fields:\n```json\n{\n  "some_field": "uuid",\n  "other.nested.field": "pk",\n}\n```\n\n### Field\n```python\nfrom lookup_fields.fields import CustomizableLookupRelatedField\nfrom rest_framework import serializers\n\n\nclass Serializer(serializers.ModelSerializer):\n    field = CustomizableLookupRelatedField(\n        lookup_fields={\n            \'some_field\': serializers.CharField(),\n            \'uuid\': serializers.UUIDField(),\n            \'other_field\': serializers.IntegerField(),\n            \'another_field_with_custom_filter_lookup_suffix\': {\n                \'field\': serializers.CharField(max_length=20),\n                \'filter_lookup_suffix\': \'__icontains\',\n            }\n        },\n        no_pk_lookup=True,\n        default_lookup_field_name=\'uuid\',\n    )\n```\n\ndefault_lookup_field_name is \'pk\', integer pk field is always added to lookup_fields. If you don\'t want this behavior set no_pk_lookup to True. Even then you can still add pk to lookup_fields when instantiate field.\n\nYou can specify optional parameters to lookup_fields by passing a dict instead of Field instance. Field has to be passed under \'field\' key.\n\n### Serializer\n\nSerializers uses `CustomizableLookupRelatedField` as default related field.\n\n```python\nfrom lookup_fields.fields import CustomizableLookupRelatedField\nfrom rest_framework import serializers\n\n\nclass Serializer(CustomizableLookupRelatedField):\n    class Meta:\n        model = SomeModel\n        fields = (\n            \'relation\',\n        )\n        extra_kwargs = {\n            \'relation\': {\n                \'lookup_fields\': {\n                    \'some_field\': serializers.CharField(),\n                },\n            },\n        }\n```\n\n## View mixin usage\nName of lookup field should be supplied in `Lookup-Field` HTTP header.\n\n### View\n```python\nfrom lookup_fields.views import CustomizableLookupFieldMixin\nfrom rest_framework.generics import GenericAPIView\n\n\nclass View(CustomizableLookupFieldMixin, GenericAPIView):\n    ALLOWED_LOOKUP_FIELDS = [\n        \'pk\',\n        \'uuid\',\n        \'some_field\',\n        WithPermissions(\n            \'other_field\',\n            permissions=[\'some_app.can_use_other_field_as_lookup_field\'],\n        )\n    ]\n    LOOKUP_FIELD_VALIDATORS = {\n        \'some_field\': [validator],\n    }\n```\n\n## License\nThe Django Rest Framework Lookup Fields package is licensed under the [FreeBSD\nLicense](https://opensource.org/licenses/BSD-2-Clause).\n',
    'author': 'IIIT',
    'author_email': 'github@iiit.pl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/innovationinit/drf-lookup-fields',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
