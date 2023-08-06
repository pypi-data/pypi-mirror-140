#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   read_hdf.py
@Time    :   2022/01/15 15:46:05
@Author  :   DingWenjie
@Contact :   359582058@qq.com
@Desc    :   None
'''

import pandas as pd
import os

pt = os.path.dirname(os.path.realpath(__file__))
files = {
        'A': os.path.join(pt, 'get_data_from_wind/option_50_data_wind.h5'),
        'B': os.path.join(pt, 'get_data_from_wind/etf_50_data_wind.h5'),
}
def read_data():
    # option_data = pd.read_hdf('get_data_from_wind/option_50_data_wind.h5')
    # etf_data = pd.read_hdf('get_data_from_wind/etf_50_data_wind.h5')
    option_data = pd.read_hdf(files['A'])
    etf_data = pd.read_hdf(files['B'])
    return option_data, etf_data

if __name__ == '__main__':
    pass