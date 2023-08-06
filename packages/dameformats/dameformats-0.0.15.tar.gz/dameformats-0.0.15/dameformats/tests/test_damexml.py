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
from xml.dom import minidom
import xml.etree.ElementTree as ET

class TestDameXml(unittest.TestCase):

    # XML
    def test_damexml_getelementsbytagname(self):
        # using read and loads to open
        xmldoc = minidom.parse('files/items.xml')
        itemlist = xmldoc.getElementsByTagName('item')
        self.assertEqual(len(itemlist), 4)
        l1 = []
        for s in itemlist:
            l1.append(s.attributes['name'].value)
        self.assertEqual(l1, ['item1', 'item2', 'item3', 'item4'])

    def test_damexml_rss_titles(self):
        tree = ET.parse('files/rss.xml')
        l1 = []
        for elem in tree.iter():
            # using elem.tag
            if (elem.tag == "title"):
                l1.append(elem.text)
        self.assertEqual(l1[0:2], ["Richard Stallman's Political Notes",
                                   'Economic growth and fossil fuels'])
    def test_damexml_root(self):
        tree = ET.parse('files/rss.xml')
        root = tree.getroot()
        self.assertEqual(root.tag, 'rss')
        self.assertEqual(root.attrib, {'version': '2.0'})
        l2 = []
        for elem in root.iter():
            if (elem.tag == "title"):
                l2.append(elem.text)
        self.assertEqual(l2[0:2], ["Richard Stallman's Political Notes",
                                   'Economic growth and fossil fuels'])

    def test_damexml_fromstring(self):
        root = ET.fromstring('<a><b /><c><d /></c></a>')
        self.assertEqual(root.tag, 'a')
        self.assertEqual(root[0].tag, 'b')
        self.assertEqual(root[1].tag, 'c')
        self.assertEqual(root[1][0].tag, 'd')

    def test_damexml_xpath(self):
        tree = ET.parse("files/html.html")
        p = tree.find("body/p")
        links = list(p.iter("a"))
        self.assertEqual(len(links), 2)



if __name__ == '__main__':
    unittest.main()
