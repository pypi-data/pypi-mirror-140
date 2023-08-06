# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pyrosimple',
 'pyrosimple.daemon',
 'pyrosimple.data.config',
 'pyrosimple.io',
 'pyrosimple.scripts',
 'pyrosimple.torrent',
 'pyrosimple.ui',
 'pyrosimple.util']

package_data = \
{'': ['*'],
 'pyrosimple': ['data/htdocs/*',
                'data/htdocs/css/*',
                'data/htdocs/img/*',
                'data/htdocs/js/*',
                'data/img/*',
                'data/screenlet/*',
                'data/screenlet/themes/blueish/*',
                'data/screenlet/themes/default/*'],
 'pyrosimple.data.config': ['color-schemes/*',
                            'rtorrent.d/*',
                            'templates/*',
                            'templates/conky/*']}

install_requires = \
['Tempita>=0.5.2,<0.6.0', 'bencode.py>=4.0.0,<5.0.0']

extras_require = \
{'torque': ['APScheduler>=3.9.0,<4.0.0', 'pyinotify>=0.9.6,<0.10.0']}

entry_points = \
{'console_scripts': ['chtor = pyrosimple.scripts.chtor:run',
                     'lstor = pyrosimple.scripts.lstor:run',
                     'mktor = pyrosimple.scripts.mktor:run',
                     'pyrotorque = pyrosimple.scripts.pyrotorque:run',
                     'rtcontrol = pyrosimple.scripts.rtcontrol:run',
                     'rtxmlrpc = pyrosimple.scripts.rtxmlrpc:run']}

setup_kwargs = {
    'name': 'pyrosimple',
    'version': '1.2.0',
    'description': '',
    'long_description': "# What is this?\n\nA simplified and python-3 oriented version of the pyrocore tools.\n\n# Why should I use this?\n\nYou probably shouldn't, the pyrocore tools are perfectly fine and better supported.\n\n# What's the point of this then?\n\nI needed something simpler for use with personal tools, this allows me to keep the code base mostly compatible while\ncompletely dropping features I have no need for. There are also several changes that would break existing\nintegrations, and as such aren't easily suitable for upstream changes.\n\ntl;dr I want to move fast and break things.\n\n# Significant changes\n\n- Simpler poetry-based build/install system\n- Everything in one package, no separate pyrobase\n  - Use external lib for bencode\n- Only supports python 3 and rtorrent 0.9.8\n- `lstor --raw` prints json\n- No testing because I like to live on the edge\n",
    'author': 'kannibalox',
    'author_email': 'kannibalox@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kannibalox/pyrosimple',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>3.6,<4',
}


setup(**setup_kwargs)
