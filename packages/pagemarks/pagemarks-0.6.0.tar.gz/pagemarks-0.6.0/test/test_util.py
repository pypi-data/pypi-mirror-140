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

import unittest
from framework.util import normalize_url


class NormalizeUrlTestCase(unittest.TestCase):
    def test_normalize_trivial(self):
        actual = normalize_url('http://example.com')
        expected = 'http://example.com'
        self.assertEqual(expected, actual)

    def test_normalize_case_slash(self):
        actual = normalize_url('hTTPs://examPLE.Com/FooBar/')
        expected = 'https://example.com/FooBar'
        self.assertEqual(expected, actual)

    def test_normalize_case_slash_query(self):
        actual = normalize_url('hTTPs://examPLE.Com/Foo/Bar?path=baz/')
        expected = 'https://example.com/Foo/Bar?path=baz/'
        self.assertEqual(expected, actual)

    def test_normalize_case_creds_hash(self):
        actual = normalize_url('hTTPs://user:PaSSWord@example.Com#sdFsdjf8/')
        expected = 'https://user:PaSSWord@example.com#sdFsdjf8/'
        self.assertEqual(expected, actual)

    def test_normalize_trivial_slash(self):
        actual = normalize_url('http://example.com/')
        expected = 'http://example.com'
        self.assertEqual(expected, actual)

    def test_normalize_trivial_hash(self):
        actual = normalize_url('http://example.com#')
        expected = 'http://example.com#'
        self.assertEqual(expected, actual)

    def test_normalize_trivial_query(self):
        actual = normalize_url('http://example.com?')
        expected = 'http://example.com?'
        self.assertEqual(expected, actual)
