# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['noo',
 'noo.cli',
 'noo.cli.components',
 'noo.impl',
 'noo.impl.core',
 'noo.impl.models',
 'noo.impl.packager',
 'noo.impl.packager.runners',
 'noo.impl.resolvers',
 'noo.impl.utils']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'pydantic>=1.9.0,<2.0.0',
 'requests>=2.27.1,<3.0.0',
 'tomli>=1.2.3,<2.0.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['noo = noo:app']}

setup_kwargs = {
    'name': 'pynoo',
    'version': '1.4.2',
    'description': 'Easily create new projects.',
    'long_description': '# noo\n\nEasily create new projects.\n\n![Lint](https://github.com/py-noo/noo/actions/workflows/black.yml/badge.svg)\n\n## Installation\n\n```sh\npip install pynoo\n```\n\nor install from github\n\n```sh\npip install git+https://github.com/py-noo/noo\n```\n\n## Contributing\n\nSee [contributing](./.github/CONTRIBUTING.md).\n\n## Usage\n\n```sh\nnoo clone <name> <ref>\n```\n\n## Noofile Specification\n\n```yml\nname: str\nremote: str\nread: [Read]\nsteps: [Step]\n```\n\n| Field  | Type                | Description                            |\n|--------|---------------------|----------------------------------------|\n| name   | str                 | The name of the noofile definition     |\n| remote | str                 | The remote location of the template    |\n| read   | list[[Read](#read)] | The list of variables to read on setup |\n| steps  | list[[Step](#step)] | The list of steps to run               |\n\n### Read\n\n```yml\nname: str\nprompt: str\ndefault: ?str\n```\n\n| Field   | Type | Description                                     |\n|---------|------|-------------------------------------------------|\n| name    | str  | The name of the variable to read                |\n| prompt  | str  | The prompt to display when reading the variable |\n| default | ?str | An optional default value                       |\n\n### Step\n\nA step defines a single step in the process of setting up a project.\n\n```yml\nname: str\nactions: [Action]\nconditions: ?[Condition]\n```\n\n| Field      | Type                           | Description                                                 |\n|------------|--------------------------------|-------------------------------------------------------------|\n| name       | str                            | The name of the setup step                                  |\n| actions    | list[[Action](#action)]        | The list of actions in the step                             |\n| conditions | ?list[[Condition](#condition)] | An optional list of conditions required for the step to run |\n\n### Condition\n\nA condition is a function that must be true for a step to run.\n\n```yml\nop: eq | ne | gt | lt | ge | le\nvar: str\nvalue: str\n```\n\n| Field | Type                       | Description                            |\n|-------|----------------------------|----------------------------------------|\n| op    | Literal[[OpType](#optype)] | The operation to perform               |\n| var   | str                        | The variable to compare, i.e. noo:year |\n| value | str                        | The value to compare to                |\n\n### OpType\n\nList of operation types:\n\n| Name | Operation              |\n|------|------------------------|\n| eq   | Equals                 |\n| ne   | Not Equals             |\n| gt   | Greater Than           |\n| lt   | Less Than              |\n| ge   | Greater Than or Equals |\n| le   | Less Than or Equals    |\n\n### Action\n\nAn action defined a single action within a step. This is the base of all steps, for example replacing a string with a different given string.\n\n#### Replace action\n\nReplace actions are used to replace a specific string in a file. The `src` field specifies the string that should be replaced in the file, and the `dest` field specifices the string to replace it with. The `dest` field is formatted with defined variables.\n\nA list of files can be provided, and each file will have the same transform applied to them.\n\n```yml\n- action: replace\n  files: [str]\n  src: str\n  dest: str\n```\n\n#### Delete action\n\nDelete actions are used to delete files.\n\n```yml\n- action: delete\n  files: [str]\n```\n\n#### Create action\n\nCreate actions are used to create files. The `file` field specifies the file to be created, and the `content` field specifics the content to be placed into the file. The `content` field is formatted with defined variables.\n\n```yml\n- action: create\n  file: str\n  content: ?str\n```\n\n#### Rename action\n\nRename actions are used to rename files. The `file` field specifies the file to be renamed, and the `dest` field specifies the new name of the file. The `dest` field is formatted with defined variables.\n\n```yml\n- action: rename\n  file: str\n  dest: str\n```\n\n### Variables\n\nVariables are defined in the `read` section of the noofile. All variables set in the `read` section will be available in the `steps` section.\n\nVariables are used in the format `$${scope}:{name}`, for example `$$noo:year` or `$$var:author`. Variables with the `noo` scope are built into noo and will always be available. Variables with the `var` scope are defined in the `read` section.\n\nThe variables defined by noo are:\n\n- `noo:year` - The current year\n- `noo:month` - The current month\n- `noo:day` - The current day\n- `noo:hour` - The current hour\n- `noo:minute` - The current minute\n- `noo:second` - The current second\n- `noo:name` - The name of the project\n',
    'author': 'vcokltfre',
    'author_email': 'vcokltfre@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/py-noo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
