# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['excel_model_runner']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.4,<9.0.0', 'formulas>=1.2.2,<2.0.0', 'openpyxl>=3.0.9,<4.0.0']

entry_points = \
{'console_scripts': ['run-excel-model = excel_model_runner.command:main']}

setup_kwargs = {
    'name': 'excel-model-runner',
    'version': '0.1.0',
    'description': 'Runs an Excel model (.xlsx) with parameters',
    'long_description': '# excel-model-runner\n\nThis tool will take an Excel model (.xlsx), update any parameters as defined in the parameters file\nand calculate all cells, resulting in an Excel spreadsheet resembling the original, but with all\nformula cells replaced by the calculated values.\n\nThe parameter file can be either JSON file or a CSV file in the following format:\n\n<br> \n\n## Config file\n\nJSON:\n```\n{\n   "Sheet name.Cell1": "Replacement value string",\n   "Sheet name.Cell2": Replacement value float\n}\n```\n\nExample: `params.json`\n```\n{\n    "Variables.C2": "red",\n    "Variables.C3": 0.8\n}\n```\n\n<br> \n<br> \n\nCSV:\n```\nSheet name.Cell1,Replacement value string\nSheet name.Cell2,Replacement value float\n```\n\nExample: `params.csv`\n```\nVariables.C2,red\nVariables.C3,0.8\n```\nNOTE: Do NOT include a header row in the CSV\n\n<br> \n<br> \n\n## Usage:\n\n```\nusage: run-excel-model [-h] [--output_dir OUTPUT_DIR] [--run_dir RUN_DIR] source_file parameter_file\n\npositional arguments:\n  source_file           Excel (xlsx) file that contains\n  parameter_file        Path to json or csv parameter file\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --output_dir OUTPUT_DIR\n                        Optional output location. (Default: output)\n  --run_dir RUN_DIR     Optional directory to store intermediate files. (Default: runs)\n```\n',
    'author': 'Matthew Printz',
    'author_email': 'matt@jataware.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dojo-modeling/excel-model-runner',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
