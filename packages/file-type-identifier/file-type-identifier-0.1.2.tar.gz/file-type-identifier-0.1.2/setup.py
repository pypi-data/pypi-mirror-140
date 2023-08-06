# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fti', 'fti.file_type_getters']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.22.0,<0.23.0']

setup_kwargs = {
    'name': 'file-type-identifier',
    'version': '0.1.2',
    'description': 'Library for identifying file type',
    'long_description': '# file-type-indentifier\n\nLibrary for identifying file type\n\n## Examples\n\n```\nimport asyncio\n\nfrom fti import FileTypes, get_file_types, get_file_types_async\n\n\n# sync\nfile_types = get_file_types("http://example.com/download_pdf")\n\nFileTypes.PDF in file_types\n\n\n# async\nfile_types = asyncio.run(\n    get_file_types_async("http://example.com/download_pdf")\n)\n\nFileTypes.PDF in file_types\n```',
    'author': 'Kurbanov Bulat',
    'author_email': 'b.kurbanov@speechki.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
