# (c) 2021 by Dr. Flavio ABREU ARAUJO. All rights reserved.

import os
import numpy as np
from .binaries import OVF_File_py
from .helper_funcs import size_hrf

# #* Initialise the wraper object (Cython -> C++ connector)
# #* "obj" is a direct link to the C++ object (be careful)
# OVF_raw = OVF_File_py.OVF_File_py()


#* High level OVF read function (safe)
def read(filename):
    if os.path.isfile(filename):
        OVF_raw = OVF_File_py.OVF_File_py()
        OVF_raw.readOVF(filename)
        
        # print("StageSimTime:", OVF_raw.getStageSimTime(),
        #       "("+OVF_raw.getStageSimTimeUnit()+")")
        
        # print("TotalSimTime:", OVF_raw.getTotalSimTime(),
        #       "("+OVF_raw.getTotalSimTimeUnit()+")")
        
        human_readable_size = size_hrf(OVF_raw.getData().nbytes)
        print(f'OVF [{OVF_raw.getTitle()} data] # of elements: '
            f'{OVF_raw.getElementNum()} (size: {human_readable_size})')
        data = np.copy(OVF_raw.getData())
        X_shift = OVF_raw.xstepsize() * OVF_raw.xnodes() / 2
        Y_shift = OVF_raw.ystepsize() * OVF_raw.ynodes() / 2
        X_lin = np.arange(OVF_raw.xbase(),
                            OVF_raw.xstepsize() * OVF_raw.xnodes(),
                            OVF_raw.xstepsize()) - X_shift
        Y_lin = np.arange(OVF_raw.ybase(),
                            OVF_raw.ystepsize() * OVF_raw.ynodes(),
                            OVF_raw.ystepsize()) - Y_shift
        # X_lin = np.linspace(OVF_raw.xbase(),
        #             OVF_raw.xbase() + OVF_raw.xstepsize() * OVF_raw.xnodes(),
        #             OVF_raw.xnodes(), endpoint=False)
        # Y_lin = np.linspace(OVF_raw.ybase(),
        #             OVF_raw.ybase() + OVF_raw.ystepsize() * OVF_raw.ynodes(),
        #             OVF_raw.ynodes(), endpoint=False)
        X, Y = np.meshgrid(X_lin, Y_lin)
        return X, Y, data
    else:
        raise ValueError(filename + " does not exist!")


#* High level OVF read function (only data, safe)
def read_data_only(filename):
    if os.path.isfile(filename):
        OVF_raw = OVF_File_py.OVF_File_py()
        OVF_raw.readOVF(filename)
        human_readable_size = size_hrf(OVF_raw.getData().nbytes)
        print(f'OVF [{OVF_raw.getTitle()} data] # of elements: '
            f'{OVF_raw.getElementNum()} (size: {human_readable_size})')
        data = np.copy(OVF_raw.getData())
        return data.squeeze()
    else:
        raise ValueError(filename + " does not exist!")


#* High level OVF write function (safe)
def write(filename, data, title="m",
          Xlim=[0,1], Ylim=[0,1], Zlim=[0,1]):
    if (np.prod(data.shape) > 120e6):
        file_size_limit_hr = size_hrf(120e6*4)
        file_size_hr = size_hrf(np.prod(data.shape)*4)
        raise ValueError(f'Creating a file larger than {file_size_limit_hr} ' \
            f'is not supported (your request: {file_size_hr}).')
    else:
        if (len(data.shape) > 1) &\
            (len(data.shape) <= 4):
            if len(data.shape) == 2:
                data = data.reshape(
                    tuple(list(data.shape) + [1, 1]))
            else:
                if len(data.shape) == 3:
                    data=data.reshape(
                        tuple(list(data.shape) + [1]))
        else:
            raise ValueError("Dimension not supported, "+
                "it must be 2, 3, or 4!")
        
        OVF_raw = OVF_File_py.OVF_File_py()

        if data.dtype == np.float32: #! Data Binary 4
            OVF_raw.setData(data, title, Xlim, Ylim, Zlim)
        else:
            if data.dtype == np.float64: #! Data Binary 8
                #! "Data Binary 8" (float64) is not yet supported
                #! It's hard coded in OVF_File.h in the C++ code
                #! Data is converted to Data Binary 4 (float32)
                OVF_raw.setData(data.astype(np.float32), title,
                            Xlim, Ylim, Zlim)
            else:
                raise ValueError(f"Data type {data.dtype} is not supported")
    
    OVF_raw.writeOVF(filename)
