# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['timexy', 'timexy.languages']

package_data = \
{'': ['*']}

install_requires = \
['spacy>=3.2.2,<4.0.0']

setup_kwargs = {
    'name': 'timexy',
    'version': '0.1.3',
    'description': 'A spaCy custom component that extracts and normalizes dates and other temporal expressions',
    'long_description': '# Timexy 🕙 📅\n\n<a href="https://pypi.org/project/timexy" target="_blank">\n    <img src="https://img.shields.io/pypi/v/timexy?color=%2334D058&label=pypi%20package" alt="Package version">\n</a>\n<a href="https://app.codecov.io/gh/paulrinckens/timexy" target="_blank">\n    <img src="https://img.shields.io/codecov/c/gh/paulrinckens/timexy" alt="Codecov">\n</a>\n\n\nA [spaCy](https://spacy.io/) [custom component](https://spacy.io/usage/processing-pipelines#custom-components) that extracts and normalizes dates and other temporal expressions.\n\n## Features\n- :boom: Extract dates and durations for various languages. See [here](#supported-languages) a list of currently supported languages\n- :boom: Normalize dates to timestamps or normalize dates and durations to the [TimeML TIMEX3 standard](http://www.timeml.org/publications/timeMLdocs/timeml_1.2.1.html#timex3)\n\n## Supported Languages\n- 🇩🇪 German\n- :uk: English\n- 🇫🇷 French\n\n## Installation\n````\npip install timexy\n````\n## Usage\nAfter installation, simply integrate the timexy component in any of your spaCy pipelines to extract and normalize dates and other temporal expressions:\n\n```py\nimport spacy\nfrom timexy import Timexy\n\nnlp = spacy.load("en_core_web_sm")\n\n# Optionally add config if varying from default values\nconfig = {\n    "kb_id_type": "timex3",  # possible values: \'timex3\'(default), \'timestamp\'\n    "label": "timexy",  # default: \'time\'\n    "overwrite": False  # default: False\n}\nnlp.add_pipe("timexy", config=config)\n\ndoc = nlp("Today is the 10.10.2010. I was in Paris for six years.")\nfor e in doc.ents:\n    print(f"{e.text}\\t{e.label_}\\t{e.kb_id_}")    \n```\n\n```bash\n>>> 10.10.2010    timexy    TIMEX3 type="DATE" value="2010-10-10T00:00:00"\n>>> six years     timexy    TIMEX3 type="DURATION" value="P6Y"\n```\n## Contributing\nPlease refer to the contributing guidelines [here](https://github.com/paulrinckens/timexy/blob/main/CONTRIBUTING.md).\n',
    'author': 'Paul Rinckens',
    'author_email': None,
    'maintainer': 'Paul Rinckens',
    'maintainer_email': None,
    'url': 'https://github.com/paulrinckens/timexy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
