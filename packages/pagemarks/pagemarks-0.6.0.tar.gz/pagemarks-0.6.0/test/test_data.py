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

import datetime
import os.path
import unittest

from framework.globals import DEFAULT_COLL_NAME
from framework.repo import Collection, CollectionReader



class CollectionReaderTestCase(unittest.TestCase):
    dummy_collection = Collection(os.path.join('demo_repo', DEFAULT_COLL_NAME))


    def test_parse_timestamp_nominal(self):
        actual = CollectionReader(self.dummy_collection).parse_timestamp('2021-11-26 21:22:03')
        expected = datetime.datetime(2021, 11, 26, hour=21, minute=22, second=3, microsecond=0)
        self.assertEqual(expected, actual)


    def test_parse_timestamp_dateonly(self):
        actual = CollectionReader(self.dummy_collection).parse_timestamp('2021-11-26')
        expected = datetime.datetime(2021, 11, 26, hour=0, minute=0, second=0, microsecond=0)
        self.assertEqual(expected, actual)


    def test_parse_timestamp_noseconds(self):
        actual = CollectionReader(self.dummy_collection).parse_timestamp('2021-11-26 21:22')
        expected = datetime.datetime(2021, 11, 26, hour=21, minute=22, second=0, microsecond=0)
        self.assertEqual(expected, actual)


    def test_parse_timestamp_noseconds_unpadded(self):
        actual = CollectionReader(self.dummy_collection).parse_timestamp('2021-11-26 9:22')
        expected = datetime.datetime(2021, 11, 26, hour=9, minute=22, second=0, microsecond=0)
        self.assertEqual(expected, actual)


    def test_parse_timestamp_syntaxerror(self):
        with self.assertRaises(ValueError):
            CollectionReader(self.dummy_collection).parse_timestamp('the year of the cat')


    def test_parse_timestamp_ampm(self):
        actual = CollectionReader(self.dummy_collection).parse_timestamp('2021-11-26 09:22:03 pm')
        expected = datetime.datetime(2021, 11, 26, hour=21, minute=22, second=3, microsecond=0)
        self.assertEqual(expected, actual)


    def test_parse_timestamp_noseconds_ampm(self):
        actual = CollectionReader(self.dummy_collection).parse_timestamp('2021-11-26 09:22 PM')
        expected = datetime.datetime(2021, 11, 26, hour=21, minute=22, second=0, microsecond=0)
        self.assertEqual(expected, actual)


    def test_parse_timestamp_noseconds_ampm_unpadded(self):
        actual = CollectionReader(self.dummy_collection).parse_timestamp('2021-11-26 9:22 pm')
        expected = datetime.datetime(2021, 11, 26, hour=21, minute=22, second=0, microsecond=0)
        self.assertEqual(expected, actual)
