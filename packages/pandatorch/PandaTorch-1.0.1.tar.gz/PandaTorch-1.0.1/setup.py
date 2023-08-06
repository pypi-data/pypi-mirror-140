# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pandatorch']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.1,<4.0.0', 'pandas>=1.4.1,<2.0.0']

setup_kwargs = {
    'name': 'pandatorch',
    'version': '1.0.1',
    'description': 'A flexible simple library that makes it easier to use the extrememly popular pandas package with the other extremely popular framework PyTorch. ',
    'long_description': 'PandaTorch\n==========\n\nA flexible simple library that makes it easier to use the extrememly\npopular pandas package with the other extremely popular framework\nPyTorch.\n\nFunctions\n---------\n\n1. Converts a Pandas DataFrame into a usable PyTorch dataset.\n2. Allows use of all usual Pandas functions\n\nUsage\n-----\n\n::\n\n   import pandas as pd\n   from pandatorch import data\n   df=pd.read_csv("path_to_dataset")\n   torch_df=data.DataFrame(X=df.drop("<Target Column>",axis=1),y=df["<Target Column>"])\n\n**Note:** Check out the notebooks folder for a full end-to-end training\nexample of a tabular dataset using PandaTorch\n',
    'author': 'Ashwin Iyer',
    'author_email': 'ashwiniyer1706@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
