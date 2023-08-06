#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2019  David Arroyo Menéndez

# Author: David Arroyo Menéndez <davidam@gnu.org>
# Maintainer: David Arroyo Menéndez <davidam@gnu.org>

# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.

# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with dameformats; see the file LICENSE.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA,

import unittest
import pandas as pd

from src.dame_formats import DameFormats


class TestDameCsv(unittest.TestCase):

    def test_damecsv_csvcolumn2list(self):
        du = DameFormats()
        l1 = du.csvcolumn2list('files/partial.csv', 0, header=True)
        self.assertEqual(len(l1), 21)
        self.assertEqual(['"pierre"', '"raul"', '"adriano"', '"ralf"',
                          '"teppei"', '"guillermo"', '"catherine"', '"sabina"',
                          '"ralf"', '"karl"', '"sushil"', '"clemens"',
                          '"gregory"', '"lester"', '"claude"', '"martin"',
                          '"vlad"', '"pasquale"', '"lourdes"', '"bruno"',
                          '"thomas"'], l1)

    def test_damecsv_csv2list(self):
        du = DameFormats()
        l1 = du.csv2list('files/min.csv')
        self.assertEqual(['"first_name"', '"middle_name"',
                          '"last_name"', '"full_name"', '"gender"',
                          '"origin"'], l1[0])
        self.assertEqual(['"pierre"', '"paul"', '"grivel"',
                          '"pierre paul grivel"', '"m"', '"zbmath"'],
                         l1[1])
        self.assertEqual(['"raul"', '""', '"serapioni"', '"raul serapioni"',
                          '"m"', '"zbmath"'], l1[2])

    def test_damecsv_num_columns_in_csv(self):
        du = DameFormats()
        n = du.num_columns_in_csv('files/partial.csv')
        self.assertEqual(n, 6)


if __name__ == '__main__':
    unittest.main()
