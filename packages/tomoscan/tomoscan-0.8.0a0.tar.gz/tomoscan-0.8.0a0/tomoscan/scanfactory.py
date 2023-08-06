# coding: utf-8
# /*##########################################################################
# Copyright (C) 2016-2020 European Synchrotron Radiation Facility
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
#############################################################################
"""Contains the ScanFactory class and dedicated functions"""

__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "27/02/2019"


from .scanbase import TomoScanBase
from .esrf.edfscan import EDFTomoScan
from .esrf.hdf5scan import HDF5TomoScan
from .esrf.identifier.edfidentifier import EDFTomoScanIdentifier
from .esrf.identifier.hdf5Identifier import HDF5TomoScanIdentifier
from tomoscan.identifier import DatasetIdentifier
from typing import Union
import os


class ScanFactory:
    """
    Factory for TomoScanBase instances
    """

    @staticmethod
    def create_scan_object_from_identifier(
        identifier: Union[str, DatasetIdentifier]
    ) -> TomoScanBase:
        """
        Create an instance of TomoScanBase from his identifier if possible

        :param str identifier: identifier of the TomoScanBase
        :raises: TypeError if identifier is not a str
        :raises: ValueError if identifier cannot be converted back to an instance of TomoScanBase
        """
        if not isinstance(identifier, (str, DatasetIdentifier)):
            raise TypeError(
                f"identifier is expected to be a str or an instance of {DatasetIdentifier} not {type(identifier)}"
            )

        if isinstance(identifier, str):
            scheme = identifier.split(":")[0]
            if scheme == "edf":
                identifier = EDFTomoScanIdentifier.from_str(identifier=identifier)
            elif scheme == "hdf5":
                identifier = HDF5TomoScanIdentifier.from_str(identifier=identifier)
            else:
                raise ValueError(f"Scheme {scheme} not recognized")
        else:
            scheme = DatasetIdentifier.scheme()

        if scheme == "edf":
            return EDFTomoScan.from_dataset_identifier(identifier=identifier)
        elif scheme == "hdf5":
            return HDF5TomoScan.from_dataset_identifier(identifier=identifier)
        else:
            raise ValueError(f"Scheme {scheme} not recognized")

    @staticmethod
    def create_scan_object(scan_path: str) -> TomoScanBase:
        """

        :param str scan_path: path to the scan directory or file
        :return: ScanBase instance fitting the scan folder or scan path
        :rtype: TomoScanBase
        """
        # remove any final separator (otherwise basename might fail)
        scan_path = scan_path.rstrip(os.path.sep)
        if EDFTomoScan.is_tomoscan_dir(scan_path):
            return EDFTomoScan(scan=scan_path)
        elif HDF5TomoScan.is_tomoscan_dir(scan_path):
            return HDF5TomoScan(scan=scan_path)
        else:
            raise ValueError("%s is not a valid scan path" % scan_path)

    @staticmethod
    def create_scan_objects(scan_path: str) -> tuple:
        """

        :param str scan_path: path to the scan directory or file
        :return: all possible instances of TomoScanBase contained in the given
                 path
        :rtype: tuple
        """
        scan_path = scan_path.rstrip(os.path.sep)
        if EDFTomoScan.is_tomoscan_dir(scan_path):
            return (EDFTomoScan(scan=scan_path),)
        elif HDF5TomoScan.is_tomoscan_dir(scan_path):
            scans = []
            master_file = HDF5TomoScan.get_master_file(scan_path=scan_path)
            entries = HDF5TomoScan.get_valid_entries(master_file)
            for entry in entries:
                scans.append(HDF5TomoScan(scan=scan_path, entry=entry, index=None))
            return tuple(scans)

        raise ValueError("%s is not a valid scan path" % scan_path)

    @staticmethod
    def create_scan_object_frm_dict(_dict: dict) -> TomoScanBase:
        """
        Create a TomoScanBase instance from a dictionary. It should contains
        the TomoScanBase._DICT_TYPE_KEY key at least.

        :param _dict: dictionary to be converted
        :return: instance of TomoScanBase
        :rtype: TomoScanBase
        """
        if TomoScanBase.DICT_TYPE_KEY not in _dict:
            raise ValueError(
                "given dict is not recognized. Cannot find" "",
                TomoScanBase.DICT_TYPE_KEY,
            )
        elif _dict[TomoScanBase.DICT_TYPE_KEY] == EDFTomoScan._TYPE:
            return EDFTomoScan(scan=None).load_from_dict(_dict)
        else:
            raise ValueError(
                f"Scan type: {_dict[TomoScanBase.DICT_TYPE_KEY]} is not managed"
            )

    @staticmethod
    def is_tomoscan_dir(scan_path: str) -> bool:
        """

        :param str scan_path: path to the scan directory or file
        :return: True if the given path is a root folder of an acquisition.
        :rtype: bool
        """
        return HDF5TomoScan.is_tomoscan_dir(scan_path) or EDFTomoScan.is_tomoscan_dir(
            scan_path
        )
