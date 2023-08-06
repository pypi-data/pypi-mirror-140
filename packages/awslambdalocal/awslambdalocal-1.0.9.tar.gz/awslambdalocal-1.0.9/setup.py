# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['awslambdalocal']

package_data = \
{'': ['*']}

install_requires = \
['python-dotenv>=0.19.2,<0.20.0']

setup_kwargs = {
    'name': 'awslambdalocal',
    'version': '1.0.9',
    'description': 'A tool to simulate running an AWS Lambda locally',
    'long_description': '# awslambdalocal\nawslambdalocal is a tool to simulate running an AWS Lambda locally, for lambda functions in Python.\n\n\n## Table of Contents\n\n* [Requirements](#requirements)\n* [Installation](#install)\n* [About: CLI](#about-cli)\n    * [Positional Arguments](#positional-arguments)\n    * [Optional Arguments](#optional-arguments)\n    * [CLI Examples](#cli-examples)\n* [Tutorials](#tutorials)\n    * [Debug Python in VSCode](#debug-python-in-vscode)\n\n\n## Requirements\n\n* Python => 3.8\n* Poetry => 1.1.12 or another package manager that supports direct git dependencies\n\n\n## Install\n\nTo install awslambdalocal, we recommend adding it to your pyproject.toml in the dev-dependencies section as shown in the example below.\n\n```bash\npip install awslambdalocal\n```\n**Obs.:** We recommend using Poetry. See https://python-poetry.org/docs/ \n\n\n## About: CLI\n\n### Positional Arguments:\n| Argument    | Description                                                                  |\n|-------------|------------------------------------------------------------------------------|\n| file        | Specify Lambda function file name                                            |\n\n### Optional Arguments:\n| Argument    | Description                                                                  |\n|-------------|------------------------------------------------------------------------------|\n| --help      | Show this help message and exit                                              |\n| -e          | Specify Event data file name. REQUIRED without param -w                      |\n| -h          | Lambda function handler name. Default is "handler"                           |\n| -p          | Read the AWS profile of the file.                                            |\n| -r          | Sets the AWS region, defaults to us-east-1.                                  |\n| -t          | Sets lambda timeout. default: 3                                              |\n| -w          | Starts lambda-local in watch mode listening to the specified port [1-65535]. |\n\n\n### CLI Examples\n```sh\n# Simple usage\npyhton -m awslambdalocal main.py test-event.json\n\n# Input all arguments\npyhton -m awslambdalocal main.py test-event.json -p my_profile -r my_region -h lambda_handler -t 30\n```\n\n\n## Tutorials\n---\nThis session contains a collection of tutorials.\n\n### Debug Python in VSCode\nTo use vscode debug with awslambdalocal follow the steps below\n\n1. Click run and debug\n2. Click create a launch.json file\n\n    ![](https://github.com/miqueiasbrs/py-aws-lambda-local/raw/master/docs/step_1.png)\n3. Choose Python\n\n    ![](https://github.com/miqueiasbrs/py-aws-lambda-local/raw/master/docs/step_2.png)\n4. Choose Module\n\n    ![](https://github.com/miqueiasbrs/py-aws-lambda-local/raw/master/docs/step_3.png)\n5. Set the module name "awslambdalocal"\n\n    ![](https://github.com/miqueiasbrs/py-aws-lambda-local/raw/master/docs/step_4.png)\n6. After this process, VSCode will create a file called launch.json in the .vscode folder located at the root of the project\n\n    ![](https://github.com/miqueiasbrs/py-aws-lambda-local/raw/master/docs/step_5.png)\n6. Copy and paste the json below into the launch.json file, this file aims to call the awslambdalocal module and passes the necessary and optional parameters as arguments\n\n    ```json\n    {\n        // Use o IntelliSense para saber mais sobre os atributos possíveis.\n        // Focalizar para exibir as descrições dos atributos existentes.\n        // Para obter mais informações, acesse: https://go.microsoft.com/fwlink/?linkid=830387\n        "version": "0.2.0",\n        "configurations": [\n            {\n                "name": "Lambda Local", // Debug configuration name\n                "type": "python", // Type of configuration. Python, Node and etc.\n                "request": "launch",\n                "module": "awslambdalocal", // Module that will be called,\n                "cwd": "${workspaceFolder}", // Your project\'s root folder\n                "args": [\n                    "file_python.py", // Main file that will be called by lambda\n                    "your_test_event.json", //Input in json format that will be received by lambda\n                    // Optional args ...\n                    "-h",\n                    "handler",\n                    "-p",\n                    "your_profile",\n                    "-r",\n                    "us-east-1"\n                ]\n            }\n        ]\n    }\n    ```',
    'author': 'Miqueias BRS',
    'author_email': 'miqueias@capybaracode.com.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
