# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pyeuropeana', 'pyeuropeana.apis', 'pyeuropeana.utils']

package_data = \
{'': ['*']}

install_requires = \
['fire>=0.4,<0.5', 'pandas>=1.3,<2.0', 'requests>=2.27,<3.0']

setup_kwargs = {
    'name': 'pyeuropeana',
    'version': '0.1.7',
    'description': 'A Python wrapper around Europeana APIs',
    'long_description': '# Python interface for Europeana\'s APIs\n\nThis package is a Python client library for [several APIs](https://pro.europeana.eu/page/apis) from [Europeana](https://pro.europeana.eu/):\n\n* [Search API](https://pro.europeana.eu/page/search)\n* [Record API](https://pro.europeana.eu/page/record)\n* [Entity API](https://pro.europeana.eu/page/entity)\n* [IIIF API](https://pro.europeana.eu/page/iiif)\n\nWith this tool you can access in python the data and metadata from our collections. Learn more about the Europeana Data Model [here](https://pro.europeana.eu/page/edm-documentation)\n\n## Installation\n\n### Using pip\n\n`pip install pyeuropeana`\n\n### From source\n\n```\n(.venv) $ git clone https://github.com/europeana/rd-europeana-python-api.git\n(.venv) $ cd rd-europeana-python-api\n(.venv) $ pip install .\n```\n\n## Authentication\n\nGet your API key [here](https://pro.europeana.eu/pages/get-api)\n\nSet `EUROPEANA_API_KEY` as an environment variable running `export EUROPEANA_API_KEY=yourapikey` in the terminal.\n\nIf running in Google Colab use `os.environ[\'EUROPEANA_API_KEY\'] = \'yourapikey\'`\n\n## Usage\n\n### [Search API](https://pro.europeana.eu/page/search)\n\n```python\nimport pyeuropeana.apis as apis\nimport pyeuropeana.utils as utils\n\n# use this function to search our collections\nresult = apis.search(\n    query = \'*\',\n    qf = \'(skos_concept:"http://data.europeana.eu/concept/base/48" AND TYPE:IMAGE)\',\n    reusability = \'open AND permission\',\n    media = True,\n    thumbnail = True,\n    landingpage = True,\n    colourpalette = \'#0000FF\',\n    theme = \'photography\',\n    sort = \'europeana_id\',\n    profile = \'rich\',\n    rows = 1000,\n    ) # this gives you full response metadata along with cultural heritage object metadata\n\n    # use this utility function to transform a subset of the cultural heritage object metadata\n    # into a readable Pandas DataFrame\ndataframe = utils.search2df(result)\n```\n\n### [Record API](https://pro.europeana.eu/page/record)\n\n```python\nimport pyeuropeana.apis as apis\n\n# gets the metadata from an object using its europeana id\ndata = apis.record(\'/79/resource_document_museumboerhaave_V35167\')\n```\n\n### [Entity API](https://pro.europeana.eu/page/entity)\n\n```python\nimport pyeuropeana.apis as apis\n\n# suggests an entity based on a text query\ndata = apis.entity.suggest(\n  text = \'leonardo\',\n  TYPE = \'agent\',\n  language = \'es\'\n)\n\n# retrieves the data from an entity using the identifier\ndata = apis.entity.retrieve(\n  TYPE = \'agent\',\n  IDENTIFIER = 3\n)\n\n# resolves entities from an input URI\ndata = apis.entity.resolve(\'http://dbpedia.org/resource/Leonardo_da_Vinci\')\n```\n\n### [IIIF API](https://pro.europeana.eu/page/iiif)\n\n```python\nimport pyeuropeana.apis as apis\n\n# The IIIF API is mostly used to access newspapers collections at Europeana\n\n# returns a minimal set of metadata for an object\ndata = apis.iiif.manifest(\'/9200356/BibliographicResource_3000118390149\')\n\n# returns text and annotations for a given page of an object\ndata = apis.iiif.annopage(\n  RECORD_ID = \'/9200356/BibliographicResource_3000118390149\',\n  PAGE_ID = 1\n)\n\n# returns the transciption of a single page of a newspaper\ndata = apis.iiif.fulltext(\n  RECORD_ID = \'/9200396/BibliographicResource_3000118435063\',\n  FULLTEXT_ID = \'8ebb67ccf9f8a1dcc2ea119c60954111\'\n)\n\n```\n\n## Documentation\n\nThe documentation is available at [Read the Docs](https://rd-europeana-python-api.readthedocs.io/en/stable/index.html)\n\nYou can also [build the docs](docs/README.md)\n',
    'author': 'José Eduardo Cejudo Grano de Oro',
    'author_email': 'joseed.cejudo@europeana.eu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/europeana/rd-europeana-python-api',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
