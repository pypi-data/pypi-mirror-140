#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   data_utils.py    
@Contact :   wangcc@csc.com.cn
@License :   (C)Copyright 2017-2018, CSC

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/11/2 14:57   wangcc     1.0         None
'''

# import lib
import numpy as np
from BBData import D
from BBData.reader_utils import Cal, Inst
from BBData.config import cal_config
from .config import up_bound_r, dn_bound_r, markets


class EngineData:

    def __init__(self, start_date=None, end_date=None):
        self.start_date = start_date
        self.end_date = end_date
        self.H = {}

    def get_info(self, field, freq="Tday"):
        if field in self.H:
            return self.H[field]
        mat = D.features(field, self.start_date, self.end_date, freq=freq, return_mat=True)[field]
        self.H[field] = mat
        return mat

    @property
    def st_info(self):
        return np.isnan(self.get_info("ndns_st"))

    @property
    def sus_info(self):
        return np.isnan(self.get_info("ndns_sus"))

    @property
    def ipo_info(self):
        return self.get_info("ndns_ipo") == 1

    @property
    def ret_info(self):
        return self.get_info("pctchange")

    @property
    def mv_info(self):
        return self.get_info("ndns_mv")

    @property
    def idu_info(self):
        return self.get_info("ndns_indu")

    @property
    def valmv_info(self):
        return self.get_info("ndns_valmv")

    @property
    def stk_univ(self):
        return self.get_info("ndns_indu")

    def trade_status(self, stk_univ, si, ei):
        assert stk_univ in markets, "stk_univ not exist"
        if stk_univ in self.H:
            stk_univ_, tradable = self.H[stk_univ]
        else:
            stk_univ_ = self.st_info & self.ipo_info & self.sus_info
            tradable = (self.ret_info > dn_bound_r) & (self.ret_info < up_bound_r) & self.sus_info
            if stk_univ != "all":
                stk_univ_ &= (self.get_info(f"univ_mask_{stk_univ}") == 1)
            self.H[stk_univ] = (stk_univ_, tradable)
        return stk_univ_[si: ei+1], tradable[si: ei+1]


ED = EngineData()


if __name__ == '__main__':
    pass