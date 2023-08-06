# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hela',
 'hela._utils',
 'hela.datasets',
 'hela.math',
 'hela.plots',
 'hela.test_suite',
 'hela.web_page']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0', 'numpy>=1,<2', 'pandas>=1,<2']

extras_require = \
{'bigquery': ['google-cloud-bigquery>=2,<3'],
 'glue': ['aws-cdk.aws-glue>=1,<2'],
 'spark': ['pyspark>=3,<4']}

setup_kwargs = {
    'name': 'hela',
    'version': '0.2.3',
    'description': 'Your data catalog as code and one schema to rule them all.',
    'long_description': '# `hela`: write your data catalog as code\n![Unit Tests](https://github.com/erikmunkby/hela/actions/workflows/unit_tests.yaml/badge.svg)\n![Spark](https://github.com/erikmunkby/hela/actions/workflows/test_spark.yaml/badge.svg)\n![BigQuery](https://github.com/erikmunkby/hela/actions/workflows/test_bigquery.yaml/badge.svg)\n![AWS Glue](https://github.com/erikmunkby/hela/actions/workflows/test_aws_glue.yaml/badge.svg)\n\nYou probably already have your data job scripts version controlled, but what about your data catalog?\nThe answer: **write your data catalog as code!** Storing your data catalog and data documentation as code makes your catalog searchable, referenceable, reliable, platform agnostic, sets you up for easy collaboration and much more! \nThis library is built to fit small and large data landscapes, but is happiest when included from the start.\n\n`Hela` (or Hel) is the norse mythological collector of souls, and the Swedish word for "whole" or "all of it". `Hela`\nis designed to give everyone a chance to build a data catalog, with a low entry barrier: pure python code.\n\nLinks:\n* [docs](https://erikmunkby.github.io/hela/)\n* [pypi](https://pypi.org/project/hela/)\n* [showcase catalog](https://erikmunkby.github.io/hela-showcase/)\n\n## Installing\nUsing pip:\n\n`pip install hela`\n\nUsing poetry:\n\n`poetry add hela`\n\n## Roadmap\nThese are up-coming features in no particular order, but contributions towards these milestones are highly appreciated! To read more about contributing check out `CONTRIBUTING.md`.\n\n* Search functionality in web app\n* More integrations (Snowflake, Redshift)\n* More feature rich dataset classes\n* Data lineage functionality (both visualized in notebooks and web app)\n* Prettier docs page\n\n\n## (Mega) Quick start\nIf you want to read more check out the [docs page](https://erikmunkby.github.io/hela/). If you do not have patience for that, the following is all you need to get started.\n\nFirst of all build your own dataset class by inheriting the `BaseDataset` class. This class will hold most of your project specific functionality such as read/write, authentication etc.\n\n```python\nfrom hela import BaseDataset, Col\nfrom hela.data_types import String\n\nclass MyDatasetClass(BaseDataset):\n    def __init__(\n        self,\n        name: str, # Required\n        description: str, # Optional but recommended\n        columns: list, # Optional but recommended\n        rich_description_path: str = None, # Optional, used for web app\n        partition_cols: list = None,  # Optional but recommended\n        # folder: str = None, # Only do one of either folder or database\n        database: str, # Optional, can also be enriched via Catalog\n    ) -> None:\n        super().__init__(\n            name,\n            data_type=\'bigquery\',\n            folder=None,\n            database=database,\n            description=description,\n            rich_description_path=rich_description_path,\n            partition_cols=partition_cols,\n            dependencies=None,\n            columns=columns\n        )\n        # Do more of your own init stuff\n\n    def my_func(self) -> None:\n        # Your own dataset function\n        pass\n        \n# Now instantiate your dataset class with one example column\nmy_dataset = MyDatasetClass(\'my_dataset\', \'An example dataset.\', [\n    Col(\'my_column\', String(), \'An example column.\')\n])\n```\n\nNow that you have a dataset class, and instantiated your first dataset, you can start populating your\ndata catalog.\n\n```python\nfrom hela import Catalog\n\nclass MyCatalog(Catalog):\n    my_dataset = my_dataset\n```\n\nThat\'s it! You now have a small catalog to keep building on. To view it as a web page you can\nadd the following code to a python script, and in the future add it in whichever CI/CD tool you use.\nThis will generate an `index.html` file that you can view in your browser or host on e.g. github pages.\n\n```python\nfrom hela import generate_webpage\n\ngenerate_webpage(MyCatalog, output_folder=\'.\')\n```\n\nTo view what a bigger data catalog can look like check out the [showcase catalog](https://erikmunkby.github.io/hela-showcase/).',
    'author': 'Erik Munkby',
    'author_email': 'erik.munkby@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/erikmunkby/hela',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
