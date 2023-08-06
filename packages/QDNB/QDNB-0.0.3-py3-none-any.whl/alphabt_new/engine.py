#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   engine.py    
@Contact :   wangcc@csc.com.cn
@License :   (C)Copyright 2017-2018, CSC

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/11/3 18:14   wangcc     1.0         None
'''


import seaborn as sns
import pandas as pd
import numpy as np
import bottleneck as bn
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdate
from BBData import D
from BBData.reader_utils import Cal
from BBData.config import cal_config
from typing import Callable, Union
from tqdm import tqdm
from pandas import offsets
from functools import partial
import matplotlib.ticker as ticker
from .lib import (mypivot, neutralize, standardize, winsorize, mkt_neutral, weight_control, update_weight, cal_group_return, Nancorr,
                  RankNancorr, equalweight, weightby)
from .performance import calculate_statistics as cs
from .data_utils import ED
from .config import uplimit, dnlimit, defualt_numna, ins_sample_date_str
plt.style.use('ggplot')
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus']=False
glb_start_dt = cal_config["Tday"]["si"]
glb_end_dt = cal_config["Tday"]["ei"]


class BackTestingEngine:

    def __init__(self, ctx=None):
        self.all_timeindex = D.calendar(glb_start_dt, glb_end_dt, freq="Tday") # complete timeindex
        self.stocklist = np.array(D.list_instruments("all", glb_start_dt, glb_end_dt, freq="Tday", as_list=True))
        if ctx is not None:
            self.set_config(ctx)

    def set_config(self, ctx):
        self.ctx = ctx
        self.start_date = max(glb_start_dt, self.ctx.start_date)
        self.end_date = min(glb_end_dt, self.ctx.end_date)
        self.si, self.ei = self.locate_index(self.start_date, self.end_date)
        self.slice = slice(self.si, self.ei + 1)

    def on_init(self):
        """ load requied data for backtesting, all data is cached in ED onced loaded"""
        assert self.ctx is not None, " engine uninited "
        self.stk_univ_, self.tradable = ED.trade_status(self.ctx.stk_univ, self.si, self.ei)
        self.adjperch = ED.ret_info[self.slice]
        self.timeindex = self.all_timeindex[self.slice]       # timeindex

    @staticmethod
    def locate_index(start_date, end_date):
        gsi, _ = Cal.locate_index(glb_start_dt, glb_end_dt)
        si, ei = Cal.locate_index(start_date, end_date)
        return si - gsi, ei - gsi

    def get_idxreturn(self, idxcode):
        """get index return series"""
        if idxcode == "top2500":
            valmv = ED.valmv_info[self.slice]
            valmv[~(self.stk_univ_ == 1)] = np.nan
            valmv /= np.nansum(valmv, axis=1, keepdims=True)
            bcm_retr = self.cal_alpha_pnl(valmv, 1, True, 1, False)["gross_return"]
        else:
            bcm_retr = D.datasets_fl(filt=f"$indexcode=='{idxcode}'", fields='pctchange', dataset="AIndexEODPrices") \
                .set_index('trade_dt')['pctchange']
            if bcm_retr.empty:
                bcm_retr = D.datasets_fl(filt=f"$indexcode=='{idxcode}'", fields='close', dataset="CMFIndexEOD") \
                    .set_index('trade_dt')['close'].pct_change(1).fillna(0)
        return bcm_retr

    def _factor_common_ops(self, factor: Union[pd.DataFrame, Callable], *args, **kws):
        """ common operations for alpha and comb """
        if isinstance(factor, Callable):
            factor = factor(*args, **kws)
        if np.all(np.in1d(["stockcode", "trade_dt", "value"], factor.columns)):
            self.factor = mypivot(factor, self.timeindex, self.stocklist, index='trade_dt', values='value',
                                  columns="stockcode")
        else:
            self.factor = factor.reindex(index=self.timeindex, columns=self.stocklist).values
        self.factor[~self.stk_univ_] = np.nan  # consider universe, st and suspend

    def add_alpha(self, factor: Union[pd.DataFrame, Callable], *args, **kws) -> None:
        """ factor setting and preprocessing
            factor can be either ndns or column oriented. However, if column oriented, the columns must contain
            'trade_dt', 'values' and 'code' or 'stockcode' for ndns transformation. The 'factor' input can
            also be a callable function. If so, args and kws will be delivered to the function """
        self.on_init()
        self._factor_common_ops(factor, *args, **kws)
        if self.ctx.winsorize:
            self.factor = winsorize(self.factor, dnlimit, uplimit, axis=1)
        if self.ctx.standardize:
            self.factor = standardize(self.factor)
        self.factor = neutralize(self.factor, ED.mv_info[self.slice], ED.idu_info[self.slice],
                                 self.ctx.mv_neutral, self.ctx.idu_neutral)

    def add_comb(self, factor: Union[pd.DataFrame, Callable], *args, **kws) -> None:
        """
        :param factor:
        :param args:
        :param kws:
        :return:
        """
        self.on_init()
        self._factor_common_ops(factor, *args, **kws)
        if self.ctx.control_single_share_weight:
            self.factor = weight_control(self.factor, OpParaPercent=self.ctx.weight_limit)

    def cal_alpha_pnl(self, tgt_weight, shift=1, longonly=False, cap_invest_on_each_side=0.5, get_group_contri=True):
        """ calculate returns for shares groupped by factor"""
        nrow, ncol = self.adjperch.shape
        position = np.zeros((ncol,))
        self.factor_bt = tgt_weight
        self.turnover, self.returns, self.g_returns, self.na_log, self.numposi = [], [], [], [], []
        for i in tqdm(range(0, nrow - 1 - shift)):
            fact_i, univ_i, trad_i, retr_i = self.get_bar(i, shift)
            """ check the number of nans"""
            if (~np.isnan(fact_i)).sum() < defualt_numna:
                # 判断 facotr 有效值量，低于一定值返回nan， warning
                self.na_log.append(self.all_timeindex[self.si + i])
                turnover_i = 0
            else:
                if (fact_i[~np.isnan(fact_i)] == 0).all() and longonly:
                    fact_i[univ_i] = 1 / fact_i[univ_i].size  # 防止空指数的时候全部为0
                position, turnover_i = update_weight(position, fact_i, univ_i, trad_i)
            assert (~np.isnan(position)).all(), "position array contains nan"
            assert turnover_i <= 4.01, "unreasonable turnover rate"
            # assert not (position == 0).all()
            pos_retr = position * retr_i
            self.turnover.append(turnover_i * cap_invest_on_each_side)
            self.returns.append(np.nansum(pos_retr) * cap_invest_on_each_side)
            self.numposi.append(np.sum(~(np.isnan(position) | (position == 0))))
            """ calculate the contribution to long short return from different groups """
            if get_group_contri:
                pos_mask = retr_i > 0
                self.g_returns.append([np.nansum(pos_retr[pos_mask]), -np.nansum(pos_retr[~pos_mask])])
        """ result preprocess """
        result = pd.DataFrame({'turnover': self.turnover, "gross_return": self.returns, "num_position": self.numposi},
                              index=self.all_timeindex[self.si + 1 + shift: self.ei + 1])  # 往后取T+1+shift
        if len(self.na_log) > 0:
            print(f"""Warning : {len(self.na_log)} bar data where valid factor values less than {defualt_numna} exist, 
                    see na_log for location""")
        result['commission'] = result['turnover'] * self.ctx.commision_rate
        result['return'] = result['gross_return'] - result['commission']
        if get_group_contri:
            self.g_returns = pd.DataFrame(self.g_returns, index=self.all_timeindex[self.si + 1 + shift: self.ei + 1],
                                          columns=["long", "short"])
            return pd.concat([result, self.g_returns], axis=1)
        else:
            return result

    def run_longt_short(self, shift=None):
        if shift is None:
            shift = self.ctx.shift
        factor = mkt_neutral(self.factor.copy())
        result = self.cal_alpha_pnl(factor, shift, False, 0.5, True)
        result.index = pd.to_datetime(result.index.to_series().astype(str))
        return result

    def run_short_index(self, shift=None, benchmark=None):
        if shift is None:
            shift = self.ctx.shift
        if benchmark is None:
            benchmark = self.ctx.benchmark

        factor = self.factor - np.expand_dims(bn.nanmean(self.factor, axis=1), axis=1)
        factor[factor < 0.000001] = 0
        result = self.cal_alpha_pnl(factor, shift, True, 1, False)
        indexrtr = self.get_idxreturn(benchmark)
        result.gross_return -= indexrtr
        result["return"] -= indexrtr
        result.index = pd.to_datetime(result.index.to_series().astype(str))
        return result

    def run_comb_test(self, shift=None):
        if shift is None:
            shift = self.ctx.shift
        factor = self.factor.copy()
        result = self.cal_alpha_pnl(factor, shift, True, 1, False)
        result.index = pd.to_datetime(result.index.to_series().astype(str))
        return result

    def run_group_test(self, shift=1, groups=5):
        """ calculate returns for shares groupped by factor"""
        if shift is None:
            shift = self.ctx.shift
        if groups is None:
            groups = self.ctx.groups

        nrow, _ = self.adjperch.shape
        group_return = []
        self.na_log = []
        pre_fact_i = None
        self.factor_bt = self.factor
        for i in tqdm(range(0, nrow - 1 - shift)):
            fact_i, univ_i, trad_i, retr_i = self.get_bar(i, shift)
            if (~np.isnan(fact_i)).sum() < defualt_numna:
                self.na_log.append(self.all_timeindex[self.si + i])
                # group_return.append([0.]*groups)
                if pre_fact_i is None:
                    fact_i = np.zeros_like(fact_i)
                else:
                    fact_i = pre_fact_i
            else:
                pre_fact_i = fact_i

            mask_i = univ_i & trad_i & (~np.isnan(fact_i))
            fact_i = fact_i[mask_i]
            retr_i = retr_i[mask_i]
            assert (~np.isnan(fact_i)).all()
            if len(fact_i) < 10:
                group_return.append(np.zeros((groups,)))
                continue
            group_return.append(cal_group_return(fact_i, retr_i, groups))

        group_return = np.stack(group_return, axis=0)
        group_return = pd.DataFrame(group_return, index=self.all_timeindex[self.si + 1 + shift: self.ei + 1],
                                    columns=["group_%s_pnl" % i for i in range(groups)])
        group_return.index = pd.to_datetime(group_return.index.to_series().astype(str))
        if len(self.na_log) > 0:
            print(f"""Warning : {len(self.na_log)} bar data where valid factor values less than {defualt_numna} exist, see
                  na_log for location""")
        return group_return

    def get_bar(self, index, shift):
        """ get daily data
            index: the loc of current time in calendar.
            shift: delay"""
        fact_i = self.factor_bt[index].copy()
        univ_i = self.stk_univ_[index + shift].copy()
        trad_i = self.tradable[index + shift].copy()
        retr_i = self.adjperch[index + shift + 1].copy()
        return fact_i, univ_i, trad_i, retr_i

    def cal_stats(self, result):
        """ 计算效益指标 """
        # 储存IC,RankIC 防止重复计算
        shift = 1 + self.ctx.shift
        if self.ctx.cal_ic:
            result["ic"] = Nancorr(self.factor[:-shift], self.adjperch[shift:])
            result["Rankic"] = RankNancorr(self.factor[:-shift], self.adjperch[shift:])
        return result

    def perf_eval(self, result, perf_cal_return="gross_return"):
        condition = (perf_cal_return in result.columns) | (perf_cal_return == "return")
        assert condition, f"Do not find {perf_cal_return} in result"
        result = self.cal_stats(result)
        # result.index = pd.to_datetime(result.index.astype(str))
        calculate_statistics = partial(cs, perf_cal_return=perf_cal_return)
        sliced_stats = result.groupby(result.index.to_series().dt.year).apply(lambda x: calculate_statistics(x))
        sliced_stats.loc["p5D"] = calculate_statistics(result.iloc[-5:])
        sliced_stats.loc["p1M"] = calculate_statistics(result.iloc[-20:])
        sliced_stats.loc["p3M"] = calculate_statistics(result.iloc[-60:])
        sliced_stats.loc["p250"] = calculate_statistics(result.iloc[-250:])
        sliced_stats.loc["ThisYear"] = calculate_statistics(result.loc[result.index[-1] - offsets.YearBegin():])
        sliced_stats.loc["Total"] = calculate_statistics(result)

        ins_sample_date = pd.to_datetime(ins_sample_date_str)
        out_sample_date = pd.to_datetime(str(self.ctx.out_sample_date))
        sliced_stats.loc["IS"] = calculate_statistics(
            result.loc[ins_sample_date: out_sample_date - pd.Timedelta(days=1)])
        sliced_stats.loc["OS"] = calculate_statistics(result.loc[out_sample_date:])
        print(sliced_stats[['annual_return%', 'sharpe_ratio', 'daily_turnover%', 'max_drawdown',
                            'bpMargin', "ic", "Rankic"]])
        return sliced_stats

    def multidim_backtest(self, shift=None, benchmark=None, groups=None, plotit=False,
                          perf_cal_return="gross_return", **kwargs):
        ls_pnl = self.run_longt_short(shift)
        lsidx_pnl = self.run_short_index(shift, benchmark)
        group_pnl = self.run_group_test(shift, groups)
        print("long-short result".center(40, "#"))
        perf_ls = self.perf_eval(ls_pnl, perf_cal_return)
        print("long-short index result".center(40, "#"))
        perf_lsidx = self.perf_eval(lsidx_pnl, perf_cal_return)
        if plotit:
            self.plot_pnl(ls_pnl, lsidx_pnl, group_pnl, **kwargs)
        return ls_pnl, lsidx_pnl, group_pnl, perf_ls, perf_lsidx

    def combo_backtest(self, shift=None, benchmark=None, plotit=False, perf_cal_return="gross_return", **kwargs):
        if shift is None:
            shift = self.ctx.shift
        if benchmark is None:
            benchmark = self.ctx.benchmark
        l_pnl = self.run_comb_test(shift)
        indexrtr = self.get_idxreturn(benchmark)
        indexrtr.index = pd.to_datetime(indexrtr.index.to_series().astype(str))
        l_pnl["benchmark_return"] = indexrtr.reindex(l_pnl.index)
        lsidx_pnl = l_pnl.copy()
        lsidx_pnl[f"return_over_benchmark"] = lsidx_pnl["return"] - indexrtr
        lsidx_pnl[f"gross_return_over_benchmark"] = lsidx_pnl["gross_return"] - indexrtr
        print("long result".center(40, "#"))
        perf_l = self.perf_eval(l_pnl, perf_cal_return)
        print("long-short index result".center(40, "#"))
        perf_lsidx = self.perf_eval(lsidx_pnl, f"{perf_cal_return}_over_benchmark")
        if plotit:
            self.plot_comb_pnl(l_pnl, lsidx_pnl, **kwargs)
        return l_pnl, lsidx_pnl, perf_l, perf_lsidx

    @staticmethod
    def plot_pnl(ls, lsidx, gprtr, size=(12, 12), save_to=None):
        dateFmt = mdate.DateFormatter('%Y%m%d')
        plt.figure(figsize=size)
        ax1 = plt.subplot(3, 1, 1)
        sns.lineplot(data=ls[["return", "gross_return"]].cumsum(axis=0), ax=ax1)
        ax1.xaxis.set_major_formatter(dateFmt)
        ax1.legend(["prop pnl", "gross pnl"])
        ax1.set_title("ls")

        ax2 = plt.subplot(3, 1, 2)
        sns.lineplot(data=lsidx[["return", "gross_return"]].cumsum(axis=0), ax=ax2)
        ax2.xaxis.set_major_formatter(dateFmt)
        ax2.legend(["prop pnl", "gross pnl"])
        ax2.set_title("lsidx")

        ax3 = plt.subplot(3, 1, 3)
        sns.lineplot(data=gprtr.cumsum(axis=0), ax=ax3)
        ax3.xaxis.set_major_formatter(dateFmt)
        ax3.legend(gprtr.columns)
        ax3.set_title("group")
        if save_to:
            plt.savefig(save_to)
        plt.show()

    @staticmethod
    def plot_comb_pnl(l_pnl, lsidx_pnl, size=(12, 12), save_to=None):
        dateFmt = mdate.DateFormatter('%Y%m%d')
        plt.figure(figsize=size)
        ax1 = plt.subplot(2, 1, 1)
        ax1.xaxis.set_major_formatter(dateFmt)
        sns.lineplot(data=l_pnl[["return", "gross_return", "benchmark_return"]].cumsum(axis=0), ax=ax1)

        ax1.legend(["prop pnl", "gross pnl"])
        ax1.set_title("long pnl")

        ax2 = plt.subplot(2, 1, 2)
        ax2.xaxis.set_major_formatter(dateFmt)
        sns.lineplot(data=lsidx_pnl[["return_over_benchmark", "gross_return_over_benchmark"]].cumsum(axis=0), ax=ax2)
        ax3 = ax2.twinx()
        plt.ylabel("num_position")
        # sns.lineplot(data=lsidx_pnl[["num_position"]], ax=ax3)
        ax3.fill_between(lsidx_pnl.index, 0, lsidx_pnl["num_position"], color='b', alpha=0.2)

        ax2.legend(["prop pnl", "gross pnl"])
        ax2.set_title("long-short-index pnl")
        if save_to:
            plt.savefig(save_to)
        plt.show()


if __name__ == '__main__':
    pass
