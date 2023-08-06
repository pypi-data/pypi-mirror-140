import numpy as np
import os
from ..utilities import Utilities


class TOF(object):
    """This class handles the loading of the TOF and the automatic conversion to 's'"""
    
    tof_array = []
    counts_array = []
    
    def __init__(self, filename=None, tof_array=None, units='s'):
        """Constructor of the TOF class
        
        Arguments:
        * filename: optional input file name. If file exist, data will be automatically loaded 
        (only CSV file is supported so far)
           example: file_tof.txt
                    #first row of the file
                    1.0  34
                    2.2  31
                    3.4  5
                    4.5  10
                    5.6  22
                    ...

            or      #first column, second column
                    1.0,34
                    2.2,31
                    3.4,5
                    4.5,10
                    5.6,22
                    ...

        * tof_array: optional tof array. This argument will be ignored if filename is not None
        * units: optional units of the input tof array (default to 'seconds')

        Raises:
        * ValueError: - input file provided as the wrong format
                      - neither input file and tof_array are provided
                      
        * IOError: - file does not exist
        
        """

        if filename is not None:
            if os.path.isfile(filename):
                self.filename = filename
                self.load_data()
            else:
                raise IOError("File does not exist")
        else:
            if tof_array is not None:
                if not type(tof_array) is np.ndarray:
                    self.tof_array = np.array(tof_array)
                else:
                    self.tof_array = tof_array
            else:
                raise ValueError("Please provide a tof array")

        if units is not 's':
            self.tof_array = Utilities.convert_time_units(data=self.tof_array,
                                                          from_units=units,
                                                          to_units='s')

    @staticmethod
    def _first_line_number_with_real_data(line):
        str_line = str(line)
        if str_line.startswith("#"):
            return 1
        else:
            return 0

    @staticmethod
    def _is_this_numeric(value_to_evaluate):
        if not np.isfinite(value_to_evaluate):
            return False

        try:
            float(value_to_evaluate)
            return True
        except ValueError:
            return False

    def load_data(self):
        """Load the data from the filename name provided"""
        
        # only loader implemented so far !
        try:
            _ascii_array = Utilities.load_ascii(filename=self.filename, sep='')
            start_row = TOF._first_line_number_with_real_data(_ascii_array[0, 0])

            _tof_column = _ascii_array[start_row:, 0]

            if not TOF._is_this_numeric(_tof_column[0]):
                start_row += 1

            _tof_column = _ascii_array[start_row:, 0]
            _counts_column = _ascii_array[start_row:, 1]

            self.tof_array = _tof_column
            self.counts_array = _counts_column
            return

        except IndexError:
            pass  # try another format

        try:
            _ascii_array = Utilities.load_ascii(filename=self.filename, sep=',')
            start_row = TOF._first_line_number_with_real_data(_ascii_array[0, 0])

            _tof_column = _ascii_array[start_row:, 0]  # first row must be excluded in this format

            if not TOF._is_this_numeric(_tof_column[0]):
                start_row += 1

            _tof_column = _ascii_array[start_row:, 0]
            _counts_column = _ascii_array[start_row:, 1]

            self.tof_array = _tof_column
            self.counts_array = _counts_column
            return

        except IndexError:
            raise IndexError("Format not implemented!")
