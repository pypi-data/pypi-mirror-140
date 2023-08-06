#
# pagemarks - Free, git-backed, self-hosted bookmarks
# Copyright (c) 2019-2021 the pagemarks contributors
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License, version 3, as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/gpl.html>.
#

import json
import os

from setuptools import setup



def check_preparations():
    if not os.path.isfile('src/resources/css/pagemarks_minty.css') \
            or not os.path.isfile('src/resources/css/pagemarks_darkly.css'):
        print('ERROR: Generated files not found. Please run \'python prepare.py\' from the project root.')
        exit(1)



def read_version() -> str:
    with open('package.json', 'r', encoding='utf-8') as f:
        json_obj = json.load(f)
    if 'version' in json_obj:
        return json_obj['version']
    else:
        raise Exception('ERROR: Failed to read version from package.json')



check_preparations()

__version__ = read_version()
setup(version=__version__)
