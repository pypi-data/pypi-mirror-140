# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['strictdoc',
 'strictdoc.backend',
 'strictdoc.backend.reqif',
 'strictdoc.backend.reqif.export',
 'strictdoc.backend.reqif.import_',
 'strictdoc.backend.sdoc',
 'strictdoc.backend.sdoc.errors',
 'strictdoc.backend.sdoc.grammar',
 'strictdoc.backend.sdoc.models',
 'strictdoc.backend.sdoc.validations',
 'strictdoc.backend.source_file_syntax',
 'strictdoc.backend.source_file_syntax.models',
 'strictdoc.cli',
 'strictdoc.commands',
 'strictdoc.core',
 'strictdoc.core.actions',
 'strictdoc.core.finders',
 'strictdoc.export',
 'strictdoc.export.excel',
 'strictdoc.export.html',
 'strictdoc.export.html.generators',
 'strictdoc.export.html.renderers',
 'strictdoc.export.html.tools',
 'strictdoc.export.rst',
 'strictdoc.helpers']

package_data = \
{'': ['*'],
 'strictdoc.export.html': ['_static/*',
                           '_static_extra/mathjax/*',
                           '_static_extra/mathjax/output/chtml/fonts/*',
                           '_static_extra/mathjax/output/chtml/fonts/woff-v2/*',
                           'templates/*',
                           'templates/_shared/*',
                           'templates/_shared/requirement_block/*',
                           'templates/document_tree/*',
                           'templates/requirements_coverage/*',
                           'templates/single_document/*',
                           'templates/single_document_table/*',
                           'templates/single_document_traceability/*',
                           'templates/single_document_traceability_deep/*',
                           'templates/source_file_coverage/*',
                           'templates/source_file_view/*']}

install_requires = \
['XlsxWriter>=1.3.7,<2.0.0',
 'beautifulsoup4>=4.9.3,<5.0.0',
 'docutils>=0.16,<0.17',
 'jinja2>=2.11.2,<4.0',
 'lxml>=4.6.2,<5.0.0',
 'pygments>=2.10.0,<3.0.0',
 'python-datauri>=0.2.9,<0.3.0',
 'reqif>=0.0.18,<0.0.19',
 'textx==2.3.0']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.7,<0.8']}

entry_points = \
{'console_scripts': ['strictdoc = strictdoc.cli.main:main']}

setup_kwargs = {
    'name': 'strictdoc',
    'version': '0.0.20',
    'description': 'Software for writing technical requirements and specifications.',
    'long_description': '# StrictDoc\n\n![](https://github.com/stanislaw/strictdoc/workflows/StrictDoc%20on%20macOS/badge.svg?branch=master)\n![](https://github.com/stanislaw/strictdoc/workflows/StrictDoc%20on%20Linux/badge.svg?branch=master)\n![](https://github.com/stanislaw/strictdoc/workflows/StrictDoc%20on%20Windows/badge.svg?branch=master)\n\nThe documentation is hosted on Read the Docs:\n[StrictDoc documentation](https://strictdoc.readthedocs.io/en/stable/).\n',
    'author': 'Stanislav Pankevich',
    'author_email': 's.pankevich@gmail.com',
    'maintainer': 'Stanislav Pankevich',
    'maintainer_email': 's.pankevich@gmail.com',
    'url': 'https://github.com/stanislaw/strictdoc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
