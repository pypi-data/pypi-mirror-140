#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   performance.py    
@Contact :   wangcc@csc.com.cn
@License :   (C)Copyright 2017-2018, CSC

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/11/3 18:14   wangcc     1.0         None
'''


import pandas as pd
import numpy as np
from pandas import DataFrame
from datetime import date, datetime
pd.options.mode.chained_assignment = None


def calculate_statistics(df: DataFrame = None, prin_output=False, output=print, risk_free=0.023, perf_cal_return="gross return"):
    """"""
    # Check for init DataFrame
    # default perf_cal_return = "gross return"
    if (df is None) | (df.empty):
        # Set all statistics to 0 if no trade.
        start_date = pd.to_datetime(datetime.now())
        end_date = pd.to_datetime(datetime.now())
        total_days = 0
        profit_days = 0
        loss_days = 0
        end_balance = 0
        max_drawdown = 0
        max_drawdown_duration = 0
        total_commission = 0
        daily_commission = 0
        total_turnover = 0
        daily_turnover = 0
        total_return = 0
        annual_return = 0
        daily_return = 0
        return_std = 0
        sharpe_ratio = 0
        return_drawdown_ratio = 0
        ic = 0
        Rankic = 0
        net_return = 0
        return_turnover_ratio = 0
    else:
        # Calculate balance related time series data
        df.loc[:, ("balance")] = df[perf_cal_return].cumsum() + 1

        # When balance falls below 0, set daily return to 0

        df.loc[:, ("highlevel")] = (
            df["balance"].rolling(
                min_periods=1, window=len(df), center=False).max()
        )
        df.loc[:, ("drawdown")] = df["balance"] - df["highlevel"]

        # Calculate statistics value
        start_date = df.index[0]
        end_date = df.index[-1]

        total_days = len(df)
        profit_days = len(df[df[perf_cal_return] > 0])
        loss_days = len(df[df[perf_cal_return] < 0])

        end_balance = df["balance"].iloc[-1]
        max_drawdown = df["drawdown"].min()
        max_drawdown_end = df["drawdown"].idxmin()

        if isinstance(max_drawdown_end, date):
            max_drawdown_start = df["balance"][:max_drawdown_end].idxmax()
            max_drawdown_duration = (max_drawdown_end - max_drawdown_start).days
        else:
            max_drawdown_duration = 0

        total_commission = df["commission"].sum()
        daily_commission = total_commission / total_days

        total_turnover = df["turnover"].sum()
        daily_turnover = total_turnover / total_days

        total_return = df[perf_cal_return].sum()
        daily_return = df[perf_cal_return].mean() * 100
        return_std = df[perf_cal_return].std() * 100
        annual_return = daily_return * 250
        net_return = df["return"].mean() * 250 * 100

        daily_risk_free = risk_free / 240  # np.sqrt(240)
        sharpe_ratio = (daily_return - daily_risk_free) / max(return_std, 0.0001) * np.sqrt(240)

        return_drawdown_ratio = -total_return / max_drawdown
        return_turnover_ratio = daily_return / daily_turnover * 100

        if "ic" in df.columns:
            ic = df["ic"].mean()
        else:
            ic = np.nan
        if "Rankic" in df.columns:
            Rankic = df["Rankic"].mean()
        else:
            Rankic = np.nan

    # Output
    if prin_output:
        output("-" * 30)

        output(f"日均收益率：\t{daily_return:,.2f}%")
        output(f"收益标准差：\t{return_std:,.2f}%")
        output(f"Sharpe Ratio：\t{sharpe_ratio:,.2f}")
        output(f"收益回撤比：\t{return_drawdown_ratio:,.2f}")
        output(f"bp收益换手比：\t{return_turnover_ratio:,.2f}")
        output(f"净年化收益率: \t{net_return}:,.2f")

        output(f"IC：\t{ic:,.2f}")
        output(f"RankIC：\t{Rankic:,.2f}")

        output(f"首个交易日：\t{start_date}")
        output(f"最后交易日：\t{end_date}")

        output(f"总交易日：\t{total_days}")
        output(f"盈利交易日：\t{profit_days}")
        output(f"亏损交易日：\t{loss_days}")

        output(f"起始资金：\t{1:,.2f}")
        output(f"结束资金：\t{end_balance:,.2f}")

        output(f"总收益率：\t{total_return:,.2f}%")
        output(f"年化收益：\t{annual_return:,.2f}%")
        output(f"最大回撤: \t{max_drawdown:,.2f}")
        output(f"最长回撤天数: \t{max_drawdown_duration}")

        output(f"总手续费：\t{total_commission:,.2f}")
        output(f"总换手%：\t{total_turnover:,.2f}")

        output(f"日均手续费：\t{daily_commission:,.2f}")
        output(f"日均换手%：\t{daily_turnover:,.2f}")

    statistics = {
        "total_return%": total_return * 100,
        "annual_return%": annual_return,
        "daily_return%": daily_return,
        "return_std%": return_std,
        "sharpe_ratio": sharpe_ratio,
        "ic": ic,
        "Rankic": Rankic,
        "net_annual_return%": net_return,
        "total_commission": total_commission,
        "daily_commission": daily_commission,
        "total_turnover%": total_turnover * 100,
        "daily_turnover%": daily_turnover * 100,
        "max_drawdown": max_drawdown,
        "max_drawdown_duration": max_drawdown_duration,
        "return_drawdown_ratio": return_drawdown_ratio,
        "bpMargin": return_turnover_ratio,
        "start_date": start_date,
        "end_date": end_date,
        "total_days": total_days,
        "profit_days": profit_days,
        "loss_days": loss_days,
        "capital": 1,
        "end_balance": end_balance,
    }

    # Filter potential error infinite value
    for key, value in statistics.items():
        if value in (np.inf, -np.inf):
            value = 0
        statistics[key] = np.nan_to_num(value)

    groupretre = df[df.columns[df.columns.str.startswith('group_')]]
    if not groupretre.empty:
        g_retr_dict = groupretre.sum(axis=0).to_dict()
        if prin_output:
            for key, value in g_retr_dict.items():
                output(key, f": \t{value:,.2f}")
        statistics = {**statistics, **g_retr_dict}

    return pd.Series(statistics)