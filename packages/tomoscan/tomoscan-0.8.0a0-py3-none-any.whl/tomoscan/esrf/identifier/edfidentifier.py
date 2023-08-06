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


class EDFTomoScanIdentifier(DatasetIdentifier):
    """Identifier specific to EDF TomoScan"""

    def __init__(self, dataset, edf_folder):
        super().__init__(dataset)
        self._edf_folder = os.path.realpath(os.path.abspath(edf_folder))

    @docstring(DatasetIdentifier)
    def short_description(self) -> str:
        return f"{self.scheme}:{os.path.basename(self.edf_folder)}"

    @property
    def edf_folder(self):
        return self._edf_folder

    @property
    @docstring(DatasetIdentifier)
    def scheme(self) -> str:
        return "edf"

    @staticmethod
    def from_str(identifier):
        identifier_no_scheme = identifier.split(":")[-1]
        edf_folder = identifier_no_scheme
        from tomoscan.esrf.edfscan import EDFTomoScan

        return EDFTomoScanIdentifier(dataset=EDFTomoScan, edf_folder=edf_folder)

    def __str__(self):
        return f"{self.scheme}:{self._edf_folder}"

    def __eq__(self, other):
        if isinstance(other, EDFTomoScanIdentifier):
            return self._edf_folder == other._edf_folder
        else:
            return False

    def __hash__(self):
        return hash(self.edf_folder)
