# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2022 European Synchrotron Radiation Facility
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
__date__ = "10/01/2022"


from tomoscan.identifier import DatasetIdentifier
import os
from tomoscan.utils import docstring


class HDF5TomoScanIdentifier(DatasetIdentifier):
    def __init__(self, dataset, hdf5_file, entry):
        super().__init__(dataset)
        self._hdf5_file = os.path.realpath(os.path.abspath(hdf5_file))
        self._entry = entry

    @docstring(DatasetIdentifier)
    def short_description(self) -> str:
        return f"{self.scheme}:{self._entry}@{os.path.basename(self._hdf5_file)}"

    @property
    def hdf5_file(self):
        return self._hdf5_file

    @property
    def entry(self):
        return self._entry

    @property
    @docstring(DatasetIdentifier)
    def scheme(self) -> str:
        return "hdf5"

    def __str__(self):
        return f"{self.scheme}:{self._entry}@{self._hdf5_file}"

    @staticmethod
    def from_str(identifier):
        identifier_no_scheme = identifier.split(":")[-1]
        entry, hdf5_file = identifier_no_scheme.split("@")
        from tomoscan.esrf.hdf5scan import HDF5TomoScan

        return HDF5TomoScanIdentifier(
            dataset=HDF5TomoScan, hdf5_file=hdf5_file, entry=entry
        )

    def __eq__(self, other):
        if isinstance(other, HDF5TomoScanIdentifier):
            return self._hdf5_file == other._hdf5_file and self._entry == other._entry
        else:
            return False

    def __hash__(self):
        return hash((self._hdf5_file, self._entry))
