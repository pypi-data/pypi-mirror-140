#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   object.py    
@Contact :   wangcc@csc.com.cn
@License :   (C)Copyright 2017-2018, CSC

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/11/3 18:46   wangcc     1.0         None
'''
from functools import wraps

import pandas as pd
from BBData import D, FeatureSaver
from BBData.config import cal_config
from .lib import winsorize, standardize, neutralize, mypivot
import types
import numpy as np
import copy

glb_start_dt = cal_config["Tday"]["si"]
glb_end_dt = cal_config["Tday"]["ei"]


class context:
    """
    DEFAULTS :
    """
    def __init__(self):
        self.author = "common"
        self.factor_type = ""
        self.factor_name = ""
        self.alpha_class = ""
        self.description = ""
        self.stk_univ = "all"
        self.start_date = 20070104
        self.end_date = 20210521
        self.out_sample_date = 20190101
        self.cache_size = 20

        self.commision_rate = 0.002
        self.benchmark = "000905.SH"
        self.shift = 1
        self.quantile = 0.5
        self.groups = 5

        self.winsorize = True
        self.standardize = True
        self.mv_neutral = True
        self.idu_neutral = True

        self.control_single_share_weight = True
        self.weight_limit = 0.05

        self.preprocess_in_univ = True
        self.cal_ic = True

    @property
    def attrs(self):
        return {k: v for k, v in self.__dict__.items() if "__" not in k}

    def _replace_attrs(self, attrs):
        for k, v in attrs.items():
            setattr(self, k, v)
        return self


class GeneratorCallBacks:

    def __init__(self, cache=False, name="temp", config=None, callbacks=None):
        """ apply winsorize, standardize, indu_neutral, mv_neutral, indu_and_mv_neutral"""
        self.cache = cache
        self.name = name
        self.config = config
        self.callbacks = callbacks
        self.tidx = D.calendar(freq="Tday")
        self.stks = np.array(D.list_instruments(instruments="all", freq="Tday", as_list=True))

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            factor = func(*args, **kwargs)
            if self.cache:
                self.save_factor(factor, self.name, self.config)
            kws = {}
            if self.callbacks is None:
                return factor
            if np.any(np.in1d(["indu_neutral", "mv_neutral", "indu_and_mv_neutral"], self.callbacks)):
                mv_mat = D.features("ndns_mv", return_mat=True)["ndns_mv"]
                indu_mat = D.features("ndns_indu", return_mat=True)["ndns_indu"]
                kws = {"sqmv": mv_mat, "indu": indu_mat}
            factor_mat = mypivot(factor, self.tidx, self.stks, index="trade_dt", columns="stockcode", values="value")
            for ops in self.callbacks:
                factor_mat = self.ops(factor_mat, ops, **copy.deepcopy(kws))
            return self.to_columnar(factor_mat, self.tidx, self.stks)
        return wrapper

    @staticmethod
    def ops(factor_mat, ops_str, *args, **kwargs):
        if ops_str == "winsorize":
            return winsorize(factor_mat)
        if ops_str == "standardize":
            return standardize(factor_mat)
        if ops_str == "indu_neutral":
            return neutralize(factor_mat, mv_neutral=False, idu_neutral=True, *args, **kwargs)
        if ops_str == "mv_neutral":
            return neutralize(factor_mat, mv_neutral=True, idu_neutral=False, *args, **kwargs)
        if ops_str == "indu_and_mv_neutral":
            return neutralize(factor_mat, mv_neutral=True, idu_neutral=True, *args, **kwargs)

    @staticmethod
    def to_columnar(mat, index, column):
        df = pd.DataFrame(mat, index=index, columns=column).unstack()\
            .reset_index().rename(columns={"level_0": "stockcode", "level_1": "trade_dt", 0: "value"})
        return df

    @staticmethod
    def save_factor(df: pd.DataFrame, name, config=None):
        fs = FeatureSaver("Tday")
        fs.save_values(df.rename(columns={"value": name}), "trade_dt", "stockcode", config={name: config})

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return types.MethodType(self, instance)

















if __name__ == '__main__':
    pass