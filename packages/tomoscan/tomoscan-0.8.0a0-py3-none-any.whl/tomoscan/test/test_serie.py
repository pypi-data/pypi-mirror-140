# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "10/01/2021"


import pytest
from tomoscan.serie import Serie
from tomoscan.esrf.mock import MockHDF5
import tempfile


@pytest.mark.parametrize("use_identifiers", [True, False])
def test_serie_scan(use_identifiers):
    """simple test of a serie"""
    with tempfile.TemporaryDirectory() as dir:
        serie1 = Serie(use_identifiers=use_identifiers)
        assert isinstance(serie1.name, str)
        serie2 = Serie("test", use_identifiers=use_identifiers)
        assert serie2.name == "test"
        assert len(serie2) == 0
        scan1 = MockHDF5(dir, n_proj=2).scan
        scan2 = MockHDF5(dir, n_proj=2).scan
        serie3 = Serie("test", [scan1, scan2], use_identifiers=use_identifiers)
        assert serie3.name == "test"
        assert len(serie3) == 2

        with pytest.raises(TypeError):
            serie1.append("toto")

        assert scan1 not in serie1
        serie1.append(scan1)
        assert len(serie1) == 1
        assert scan1 in serie1
        serie1.append(scan1)
        serie1.remove(scan1)
        serie1.name = "toto"
        serie1.append(scan2)
        serie1.append(scan1)
        assert len(serie1) == 3
        serie1.remove(scan1)
        assert len(serie1) == 2
        serie1 == Serie("toto", (scan1, scan2), use_identifiers=use_identifiers)
        assert scan1 in serie1
        assert scan2 in serie1

        identifiers_list = serie1.to_dict_of_str()
        assert type(identifiers_list["scans"]) is list
        assert len(identifiers_list["scans"]) == 2
        for id_str in identifiers_list["scans"]:
            assert isinstance(id_str, str)
