# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nmdc_schema']

package_data = \
{'': ['*']}

install_requires = \
['linkml-runtime>=1.1.6', 'linkml>=1.1.13', 'openpyxl==3.0.7', 'pandoc']

entry_points = \
{'console_scripts': ['fetch-nmdc-schema = '
                     'nmdc_schema.nmdc_data:get_nmdc_jsonschema',
                     'nmdc-data = nmdc_schema.nmdc_data:cli',
                     'nmdc-version = nmdc_schema.nmdc_version:cli',
                     'validate-nmdc-json = nmdc_schema.validate_nmdc_json:cli']}

setup_kwargs = {
    'name': 'nmdc-schema',
    'version': '2.2.0',
    'description': 'Schema resources for the National Microbiome Data Collaborative (NMDC)',
    'long_description': "# National Microbiome Data Collaborative Schema\n\n[![PyPI - License](https://img.shields.io/pypi/l/nmdc-schema)](https://github.com/microbiomedata/nmdc-schema/blob/main/LICENSE)\n[![GitHub last commit](https://img.shields.io/github/last-commit/microbiomedata/nmdc-schema?branch=main&kill_cache=1)](https://github.com/microbiomedata/nmdc-schema/commits)\n[![GitHub issues](https://img.shields.io/github/issues/microbiomedata/nmdc-schema?branch=master&kill_cache=1)](https://github.com/microbiomedata/nmdc-schema/issues)\n[![GitHub closed issues](https://img.shields.io/github/issues-closed-raw/microbiomedata/nmdc-schema?branch=main&kill_cache=1)](https://github.com/microbiomedata/nmdc-schema/issues?q=is%3Aissue+is%3Aclosed)\n[![GitHub pull requests](https://img.shields.io/github/issues-pr-raw/microbiomedata/nmdc-schema?branch=main&kill_cache=1)](https://github.com/microbiomedata/nmdc-schema/pulls)\n\n![Deploy Documentation](https://github.com/microbiomedata/nmdc-schema/workflows/Build%20and%20Deploy%20Static%20Mkdocs%20Documentation/badge.svg?branch=main)\n\nThis repository defines a [linkml](https://github.com/linkml/linkml) schema for managing metadata from the [National Microbiome Data Collaborative (NMDC)](https://microbiomedata.org/). The NMDC is a multi-organizational effort to integrate microbiome data across diverse areas in medicine, agriculture, bioenergy, and the environment. This integrated platform facilitates comprehensive discovery of and access to multidisciplinary microbiome data in order to unlock new possibilities with microbiome data science. \n\nTasks managed by the repository are:\n\n-   Generating the schema\n-   Converting the schema from it's native LinkML/YAML format into other artifacts\n    -   [JSON-Schema](jsonschema/nmdc.schema.json)\n-   Deploying the schema as a PyPI package\n-   Deploying the [documentation](https://microbiomedata.github.io/nmdc-schema/) \n\n## Background\n\nThe NMDC [Introduction to metadata and ontologies](https://microbiomedata.org/introduction-to-metadata-and-ontologies/) primer provides some the context for this project.\n\nSee also [these slides](https://microbiomedata.github.io/nmdc-schema/schema-slides.html) ![](images/16px-External.svg.png) describing the schema.\n\n## Dependencies\nIn order to make new release of the schema, you must have the following installed on your sytem:\n- [pipenv](https://pypi.org/project/pipenv/)\n- [pandoc](https://pandoc.org/installing.html)\n\nA Pipfile.lock is include in the repository, but you can rebuild the lock file by executing `pipenv install -d`.\n\n## Maintaining the Schema\n\nSee [MAINTAINERS.md](MAINTAINERS.md) for instructions on maintaining and updating the schema.\n\n## NMDC metadata downloads\n\nSee https://github.com/microbiomedata/nmdc-runtime/#data-exports\n",
    'author': 'Bill Duncan',
    'author_email': 'wdduncan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://microbiomedata.github.io/nmdc-schema/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
