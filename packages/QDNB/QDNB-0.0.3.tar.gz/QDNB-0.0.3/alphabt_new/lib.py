#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   lib.py    
@Contact :   wangcc@csc.com.cn
@License :   (C)Copyright 2017-2018, CSC

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/11/3 13:26   wangcc     1.0         None
'''

import sys

sys.path.append("..")
import numpy as np
import numba as nb
import pandas as pd
import bottleneck as bn
from .data_utils import ED
from datetime import datetime
from time import time
from numpy.linalg import LinAlgError
from scipy.stats import rankdata


def indu_neutral(values, indu):
    """ minus industry mean"""
    tmp = np.full_like(values, np.nan)
    for i, (y, dummy) in enumerate(zip(values, indu)):
        dummy[np.isnan(dummy)] = 9988877
        mask = ~np.isnan(y)
        y, dummy = y[mask], dummy[mask]
        if y.size > 0:
            uniq, indices = np.unique(dummy, return_inverse=True)
            groups = np.full((uniq.shape[0], indices.shape[0]), np.nan)
            arrs = np.arange(indices.shape[0])
            groups[indices, arrs] = y
            tmp[i, mask] = y - np.nanmean(groups, axis=1)[indices]
    return tmp


def mv_neutral(mat, sqmv):
    """ get residual after regression with sqmv """
    tmp = np.full_like(mat, np.nan)
    for i, (y, x) in enumerate(zip(mat, sqmv)):
        mask = ~(np.isnan(y) | np.isnan(x))
        y, x = y[None, mask], x[None, mask]
        x = np.concatenate([x, np.ones((1, x.shape[1]))], axis=0)
        try:
            tmp[i, mask] = reg_residual(y, x)
        except np.linalg.LinAlgError:
            tmp[i] = np.full_like(mask, np.nan)
    return mat


def indu_encode(indu):
    """ indu: 1d array """
    uniq, indices = np.unique(indu, return_inverse=True)
    groups = np.full((uniq.size, indices.size), 0.)
    arrs = np.arange(indices.size)
    groups[indices, arrs] = 1.
    return groups.astype(np.float32)


@nb.jit(nopython=True)
def reg_residual(y_arr, x_arr):
    """get residual after regression with market value
    :param y_arr:
    :param x_arr:
    :return:
    """
    if y_arr.size == 0:
        return y_arr
    beta = np.linalg.inv(x_arr @ x_arr.T) @ x_arr @ y_arr.T
    return y_arr - beta.T @ x_arr


def wash_outliers(mat: np.ndarray, num_sigma: int):
    """清除outlier"""
    mean_arr = np.expand_dims(bn.nanmean(mat, axis=1), axis=1)
    std_arr = np.expand_dims(bn.nanstd(mat, axis=1), axis=1)
    outlier_mask = np.abs(mat - mean_arr) > mean_arr + std_arr * num_sigma

    mat_copy = mat.copy()
    mat_copy[outlier_mask] = np.nan
    mean_arr_cp = np.expand_dims(bn.nanmean(mat, axis=1), axis=1)
    std_arr_cp = np.expand_dims(bn.nanstd(mat, axis=1), axis=1)
    mat = np.clip(mat, mean_arr_cp - std_arr_cp * num_sigma, mean_arr_cp + std_arr_cp * num_sigma)
    return mat


def winsorize(mat: np.ndarray, dnlimit=0.025, uplimit=0.975, axis=1) -> np.ndarray:
    """ 将极值替换分位点数 """
    dnq = np.nanquantile(mat, dnlimit, axis=axis, keepdims=True)
    upq = np.nanquantile(mat, uplimit, axis=axis, keepdims=True)
    mat = np.clip(mat, dnq, upq)
    return mat


def standardize(mat):
    """ minus mean divide std"""
    mean = np.expand_dims(bn.nanmean(mat, axis=1), axis=1)
    stdn = np.expand_dims(bn.nanstd(mat, axis=1), axis=1)
    equal = stdn == 0
    stdn[equal] = 1
    return (mat - mean) / stdn


def mkt_neutral(factor):
    """ 返回多空booksize中性(值中性）"""
    alpha = factor - np.nanmean(factor, axis=1, keepdims=True)
    pos_mask, neg_mask = alpha > 0.000000001, alpha < -0.000000001
    zero_mask = ~(pos_mask | neg_mask | (np.isnan(alpha)))
    alpha = alpha * pos_mask / np.expand_dims(bn.nansum(alpha * pos_mask, axis=1), axis=1) \
        - alpha * neg_mask / np.expand_dims(bn.nansum(alpha * neg_mask, axis=1), axis=1)
    alpha[np.isinf(alpha)] = np.nan
    alpha[zero_mask] = 0
    alpha *= 0.5
    return alpha


def weight_control(FactorMonlix, OpParaPercent=0.05, OpParaNumIteration4Truncate=4):
    TotalNumRow, TotalNumCol = FactorMonlix.shape
    #
    if np.array([OpParaPercent]).shape.__len__() == 1:
        assert OpParaPercent > 0
        OpParaPercent = np.ones((TotalNumRow, TotalNumCol), dtype=float) * OpParaPercent
    else:
        assert OpParaPercent.shape == (TotalNumRow, TotalNumCol)
    #
    OpParaPercent[np.isnan(FactorMonlix)] = np.nan
    #
    assert OpParaNumIteration4Truncate > 0
    #
    OpedFactorMonlix = np.empty_like(FactorMonlix) * np.nan
    id4allok = True
    #
    for i in range(TotalNumRow):
        temp_vector = FactorMonlix[i, :]
        temp_ceil_vector = OpParaPercent[i, :]
        temp_notnan_vector = ~np.isnan(temp_vector)
        if not any(temp_notnan_vector):
            continue
        #
        temp_id_pos_vector = temp_vector > 0
        if any(temp_id_pos_vector):
            temp_pos_sum = np.sum(temp_vector[temp_id_pos_vector])
        else:
            temp_pos_sum = 0
        #
        temp_id_neg_vector = temp_vector < 0
        if any(temp_id_neg_vector):
            temp_neg_sum = np.sum(temp_vector[temp_id_neg_vector])
        else:
            temp_neg_sum = 0
        #
        temp_sum = temp_pos_sum - temp_neg_sum
        #
        if temp_sum == 0:
            continue
        #
        if temp_sum > 0:
            temp_c_value = temp_sum * temp_ceil_vector
            #
            temp_id_vector = temp_vector > temp_c_value
            if any(temp_id_vector):
                id4allok = False
                temp_vector[temp_id_vector] = temp_c_value[temp_id_vector]
            #
            temp_id_vector = temp_vector < -temp_c_value
            if any(temp_id_vector):
                id4allok = False
                temp_vector[temp_id_vector] = -temp_c_value[temp_id_vector]
            #
            if any(temp_id_pos_vector):
                temp_temp_sum = np.sum(temp_vector[temp_id_pos_vector])
                temp_vector[temp_id_pos_vector] = temp_pos_sum * temp_vector[temp_id_pos_vector] / temp_temp_sum
            if any(temp_id_neg_vector):
                temp_temp_sum = np.sum(temp_vector[temp_id_neg_vector])
                temp_vector[temp_id_neg_vector] = temp_neg_sum * temp_vector[temp_id_neg_vector] / temp_temp_sum
            #
            OpedFactorMonlix[i, :] = temp_vector

    # Iteration
    OpParaNumIteration4Truncate = OpParaNumIteration4Truncate - 1
    if id4allok:
        OpParaNumIteration4Truncate = 0

    if OpParaNumIteration4Truncate == 0:
        return OpedFactorMonlix
    #
    OpedFactorMonlix = weight_control(OpedFactorMonlix, OpParaPercent=OpParaPercent,
                                      OpParaNumIteration4Truncate=OpParaNumIteration4Truncate)
    return OpedFactorMonlix


@nb.jit(nopython=True)
def dropna_val(y_arr, mv_arr, idu_arr):
    idu_arr[np.isnan(idu_arr)] = 99887766
    mask = ~(np.isnan(y_arr) | np.isnan(mv_arr))  # | np.isnan(idu_arr))
    y_arr, mv_arr, idu_arr = y_arr[mask], mv_arr[mask], idu_arr[mask]
    y_arr, mv_arr = np.expand_dims(y_arr, axis=0), np.expand_dims(mv_arr, axis=0)
    return y_arr, mv_arr, idu_arr, mask


def neutralize(mat, sqmv, indu, mv_neutral=True, idu_neutral=True):
    if not (mv_neutral | idu_neutral):
        return mat
    print('[%s][start: factor neurtral]' % datetime.fromtimestamp(time()).strftime('%T'))
    one_arr = 100 * np.ones_like(mat[[0]])
    for i, (y_arr, mv_arr, idu_arr) in enumerate(zip(mat, sqmv, indu)):
        y_arr, mv_arr, idu_arr, mask = dropna_val(y_arr, mv_arr, idu_arr)
        x_arr = [one_arr[:, : y_arr.size] / y_arr.size]
        if mv_neutral:
            ln_mv = np.log(mv_arr)
            mv_arr = 100 * ln_mv / (np.mean(ln_mv) * ln_mv.size)
            x_arr.append(mv_arr)
        if idu_neutral:
            x_arr.append(indu_encode(idu_arr))
        x_arr = np.concatenate(x_arr, axis=0)
        try:
            mat[i, mask] = reg_residual(y_arr, x_arr)
        except LinAlgError:
            mat[i] = np.full_like(mask, np.nan)
    return mat


def mypivot(df, timeindex, instruments, index, columns, values):
    calidx = {c: i for i, c in enumerate(timeindex)}
    instidx = {inst: i for i, inst in enumerate(instruments)}

    df['calidx'] = df[index].map(calidx)
    df['instidx'] = df[columns].map(instidx)

    df = df.dropna(subset=['calidx', 'instidx'], axis=0, how='any')

    mat = np.full((timeindex.size, instruments.size), np.nan)
    mat[df.calidx.values.astype(int), df.instidx.values.astype(int)] = df[values].values
    return mat


def update_weight(position, factor, univ, tradable):
    new_weight = np.zeros_like(position)
    new_weight[tradable] = get_tgt_weight(factor[tradable], univ[tradable])

    frozen_posi = position[~tradable]
    new_weight[new_weight < 0] *= 1 + frozen_posi[frozen_posi < 0].sum()
    new_weight[new_weight > 0] *= 1 - frozen_posi[frozen_posi > 0].sum()

    new_weight[~tradable] = position[~tradable]
    turnover = np.abs(new_weight - position).sum()
    # assert np.sum(new_weight) < 0.0000000001
    # assert np.sum(new_weight) < 0.0000000001
    # assert np.sum(new_weight) < 0.0000000001
    return new_weight, turnover


def get_tgt_weight(fact_i, univ_i):
    """ cal target weight"""
    fact_i[~univ_i] = 0
    fact_i[np.isnan(fact_i)] = 0
    l_posi = fact_i > 0
    s_posi = fact_i < 0
    fact_i[l_posi] /= np.nansum(fact_i[l_posi])
    fact_i[s_posi] /= - np.nansum(fact_i[s_posi])
    return fact_i


def weightby(arr1, arr2, mmin=True):
    if mmin:
        arr2 -= arr2.min()
    arr2_sum = arr2.sum()
    if arr2_sum == 0:
        return arr1.mean()
    return np.dot(arr1, arr2) / arr2_sum


def equalweight(arr1, arr2):
    return np.nanmean(arr1)


def cal_group_return(fact_i, retr_i, ngroups):
    tmp = np.full((ngroups, ), 0, dtype=np.float64)
    rank = bn.nanrankdata(fact_i)
    nrange = np.sum(~np.isnan(rank))
    norm_rank = (ngroups * (rank - 1) / (nrange - 1)).astype(int)
    norm_rank = np.fmin(norm_rank, ngroups - 1)

    uniq, indices = np.unique(norm_rank, return_inverse=True)
    groups = np.full((uniq.shape[0], indices.shape[0]), np.nan)
    arrs = np.arange(indices.shape[0])
    groups[indices, arrs] = retr_i
    groupret = np.nanmean(groups, axis=1)
    if uniq.size == ngroups:
        return groupret
    tmp[uniq.astype(int)] = groupret
    return tmp


@nb.jit(nopython=True)
def nancorr(arr1, arr2):
    mask = np.isnan(arr1) | np.isnan(arr2)
    if mask.all():
        return np.nan
    arr1 = arr1[~mask]
    arr2 = arr2[~mask]
    arr1 = arr1 - np.mean(arr1)
    arr2 = arr2 - np.mean(arr2)
    std1 = max(np.sqrt(np.mean(arr1 * arr1)), 0.001)
    std2 = max(np.sqrt(np.mean(arr2 * arr2)), 0.001)
    return np.mean(arr1 * arr2) / (std1 * std2)


@nb.jit(nopython=True)
def Nancorr(mat1, mat2):
    nrow, _ = mat1.shape
    temp_data = np.zeros((nrow,))
    for i in np.arange(nrow):
        arr1 = mat1[i]
        arr2 = mat2[i]
        ic = nancorr(arr1, arr2)
        temp_data[i] = ic
    return temp_data


def ranknancorr(arr1, arr2):
    mask = np.isnan(arr1) | np.isnan(arr2)
    if mask.all():
        return np.nan
    arr1, arr2 = arr1[~mask], arr2[~mask]
    arr1, arr2 = bn.rankdata(arr1), bn.rankdata(arr2)
    arr1, arr2 = arr1 - np.mean(arr1), arr2 - np.mean(arr2)
    std = np.std(arr1) * np.std(arr2)
    if std == 0:
        return 0
    return np.mean(arr1 * arr2) / std


def RankNancorr(mat1, mat2):
    nrow, _ = mat1.shape
    temp_data = np.zeros((nrow,))
    for i in np.arange(nrow):
        arr1 = mat1[i]
        arr2 = mat2[i]
        ic = ranknancorr(arr1, arr2)
        temp_data[i] = ic
    return temp_data


if __name__ == '__main__':
    indu = ED.idu_info
    sqmv = ED.mv_info
    mat = ED.ret_info
    mat = neutralize(mat, sqmv, indu, True, True)
    pass
