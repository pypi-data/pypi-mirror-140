"""
Implements array operations for usage by DataFrames and Series
such as count and max.
"""
import numba
import numpy as np
import pandas as pd
from numba import generated_jit
from numba.core import types
from numba.extending import overload
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.utils.typing import element_type, is_hashable_type, is_iterable_type, is_overload_true, is_overload_zero


@numba.njit
def array_op_median(arr, skipna=True, parallel=False):
    syz__zheg = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(syz__zheg.ctypes, arr,
        parallel, skipna)
    return syz__zheg[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        zomai__stcl = len(arr)
        zifzo__cru = np.empty(zomai__stcl, np.bool_)
        for hwbw__oihm in numba.parfors.parfor.internal_prange(zomai__stcl):
            zifzo__cru[hwbw__oihm] = bodo.libs.array_kernels.isna(arr,
                hwbw__oihm)
        return zifzo__cru
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        pbe__tmrq = 0
        for hwbw__oihm in numba.parfors.parfor.internal_prange(len(arr)):
            jvn__flg = 0
            if not bodo.libs.array_kernels.isna(arr, hwbw__oihm):
                jvn__flg = 1
            pbe__tmrq += jvn__flg
        syz__zheg = pbe__tmrq
        return syz__zheg
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    vemww__its = array_op_count(arr)
    wrcym__mgyi = array_op_min(arr)
    ckp__crcx = array_op_max(arr)
    aswl__dmx = array_op_mean(arr)
    kbb__hnjcu = array_op_std(arr)
    yunjw__otaa = array_op_quantile(arr, 0.25)
    zyn__ldh = array_op_quantile(arr, 0.5)
    tzs__dash = array_op_quantile(arr, 0.75)
    return (vemww__its, aswl__dmx, kbb__hnjcu, wrcym__mgyi, yunjw__otaa,
        zyn__ldh, tzs__dash, ckp__crcx)


def array_op_describe_dt_impl(arr):
    vemww__its = array_op_count(arr)
    wrcym__mgyi = array_op_min(arr)
    ckp__crcx = array_op_max(arr)
    aswl__dmx = array_op_mean(arr)
    yunjw__otaa = array_op_quantile(arr, 0.25)
    zyn__ldh = array_op_quantile(arr, 0.5)
    tzs__dash = array_op_quantile(arr, 0.75)
    return (vemww__its, aswl__dmx, wrcym__mgyi, yunjw__otaa, zyn__ldh,
        tzs__dash, ckp__crcx)


@overload(array_op_describe)
def overload_array_op_describe(arr):
    if arr.dtype == bodo.datetime64ns:
        return array_op_describe_dt_impl
    return array_op_describe_impl


def array_op_min(arr):
    pass


@overload(array_op_min)
def overload_array_op_min(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            splrq__tair = numba.cpython.builtins.get_type_max_value(np.int64)
            pbe__tmrq = 0
            for hwbw__oihm in numba.parfors.parfor.internal_prange(len(arr)):
                isim__zzg = splrq__tair
                jvn__flg = 0
                if not bodo.libs.array_kernels.isna(arr, hwbw__oihm):
                    isim__zzg = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[hwbw__oihm]))
                    jvn__flg = 1
                splrq__tair = min(splrq__tair, isim__zzg)
                pbe__tmrq += jvn__flg
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(splrq__tair,
                pbe__tmrq)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            splrq__tair = numba.cpython.builtins.get_type_max_value(np.int64)
            pbe__tmrq = 0
            for hwbw__oihm in numba.parfors.parfor.internal_prange(len(arr)):
                isim__zzg = splrq__tair
                jvn__flg = 0
                if not bodo.libs.array_kernels.isna(arr, hwbw__oihm):
                    isim__zzg = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[hwbw__oihm])
                    jvn__flg = 1
                splrq__tair = min(splrq__tair, isim__zzg)
                pbe__tmrq += jvn__flg
            return bodo.hiframes.pd_index_ext._dti_val_finalize(splrq__tair,
                pbe__tmrq)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            ffjjp__gmcsl = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            splrq__tair = numba.cpython.builtins.get_type_max_value(np.int64)
            pbe__tmrq = 0
            for hwbw__oihm in numba.parfors.parfor.internal_prange(len(
                ffjjp__gmcsl)):
                uqp__txvj = ffjjp__gmcsl[hwbw__oihm]
                if uqp__txvj == -1:
                    continue
                splrq__tair = min(splrq__tair, uqp__txvj)
                pbe__tmrq += 1
            syz__zheg = bodo.hiframes.series_kernels._box_cat_val(splrq__tair,
                arr.dtype, pbe__tmrq)
            return syz__zheg
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            splrq__tair = bodo.hiframes.series_kernels._get_date_max_value()
            pbe__tmrq = 0
            for hwbw__oihm in numba.parfors.parfor.internal_prange(len(arr)):
                isim__zzg = splrq__tair
                jvn__flg = 0
                if not bodo.libs.array_kernels.isna(arr, hwbw__oihm):
                    isim__zzg = arr[hwbw__oihm]
                    jvn__flg = 1
                splrq__tair = min(splrq__tair, isim__zzg)
                pbe__tmrq += jvn__flg
            syz__zheg = bodo.hiframes.series_kernels._sum_handle_nan(
                splrq__tair, pbe__tmrq)
            return syz__zheg
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        splrq__tair = bodo.hiframes.series_kernels._get_type_max_value(arr.
            dtype)
        pbe__tmrq = 0
        for hwbw__oihm in numba.parfors.parfor.internal_prange(len(arr)):
            isim__zzg = splrq__tair
            jvn__flg = 0
            if not bodo.libs.array_kernels.isna(arr, hwbw__oihm):
                isim__zzg = arr[hwbw__oihm]
                jvn__flg = 1
            splrq__tair = min(splrq__tair, isim__zzg)
            pbe__tmrq += jvn__flg
        syz__zheg = bodo.hiframes.series_kernels._sum_handle_nan(splrq__tair,
            pbe__tmrq)
        return syz__zheg
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            splrq__tair = numba.cpython.builtins.get_type_min_value(np.int64)
            pbe__tmrq = 0
            for hwbw__oihm in numba.parfors.parfor.internal_prange(len(arr)):
                isim__zzg = splrq__tair
                jvn__flg = 0
                if not bodo.libs.array_kernels.isna(arr, hwbw__oihm):
                    isim__zzg = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[hwbw__oihm]))
                    jvn__flg = 1
                splrq__tair = max(splrq__tair, isim__zzg)
                pbe__tmrq += jvn__flg
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(splrq__tair,
                pbe__tmrq)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            splrq__tair = numba.cpython.builtins.get_type_min_value(np.int64)
            pbe__tmrq = 0
            for hwbw__oihm in numba.parfors.parfor.internal_prange(len(arr)):
                isim__zzg = splrq__tair
                jvn__flg = 0
                if not bodo.libs.array_kernels.isna(arr, hwbw__oihm):
                    isim__zzg = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[hwbw__oihm])
                    jvn__flg = 1
                splrq__tair = max(splrq__tair, isim__zzg)
                pbe__tmrq += jvn__flg
            return bodo.hiframes.pd_index_ext._dti_val_finalize(splrq__tair,
                pbe__tmrq)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            ffjjp__gmcsl = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            splrq__tair = -1
            for hwbw__oihm in numba.parfors.parfor.internal_prange(len(
                ffjjp__gmcsl)):
                splrq__tair = max(splrq__tair, ffjjp__gmcsl[hwbw__oihm])
            syz__zheg = bodo.hiframes.series_kernels._box_cat_val(splrq__tair,
                arr.dtype, 1)
            return syz__zheg
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            splrq__tair = bodo.hiframes.series_kernels._get_date_min_value()
            pbe__tmrq = 0
            for hwbw__oihm in numba.parfors.parfor.internal_prange(len(arr)):
                isim__zzg = splrq__tair
                jvn__flg = 0
                if not bodo.libs.array_kernels.isna(arr, hwbw__oihm):
                    isim__zzg = arr[hwbw__oihm]
                    jvn__flg = 1
                splrq__tair = max(splrq__tair, isim__zzg)
                pbe__tmrq += jvn__flg
            syz__zheg = bodo.hiframes.series_kernels._sum_handle_nan(
                splrq__tair, pbe__tmrq)
            return syz__zheg
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        splrq__tair = bodo.hiframes.series_kernels._get_type_min_value(arr.
            dtype)
        pbe__tmrq = 0
        for hwbw__oihm in numba.parfors.parfor.internal_prange(len(arr)):
            isim__zzg = splrq__tair
            jvn__flg = 0
            if not bodo.libs.array_kernels.isna(arr, hwbw__oihm):
                isim__zzg = arr[hwbw__oihm]
                jvn__flg = 1
            splrq__tair = max(splrq__tair, isim__zzg)
            pbe__tmrq += jvn__flg
        syz__zheg = bodo.hiframes.series_kernels._sum_handle_nan(splrq__tair,
            pbe__tmrq)
        return syz__zheg
    return impl


def array_op_mean(arr):
    pass


@overload(array_op_mean)
def overload_array_op_mean(arr):
    if arr.dtype == bodo.datetime64ns:

        def impl(arr):
            return pd.Timestamp(types.int64(bodo.libs.array_ops.
                array_op_mean(arr.view(np.int64))))
        return impl
    wnbb__cfd = types.float64
    cgd__uqezh = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        wnbb__cfd = types.float32
        cgd__uqezh = types.float32
    nbd__fdc = wnbb__cfd(0)
    kznn__qyyg = cgd__uqezh(0)
    ohv__uew = cgd__uqezh(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        splrq__tair = nbd__fdc
        pbe__tmrq = kznn__qyyg
        for hwbw__oihm in numba.parfors.parfor.internal_prange(len(arr)):
            isim__zzg = nbd__fdc
            jvn__flg = kznn__qyyg
            if not bodo.libs.array_kernels.isna(arr, hwbw__oihm):
                isim__zzg = arr[hwbw__oihm]
                jvn__flg = ohv__uew
            splrq__tair += isim__zzg
            pbe__tmrq += jvn__flg
        syz__zheg = bodo.hiframes.series_kernels._mean_handle_nan(splrq__tair,
            pbe__tmrq)
        return syz__zheg
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        acnrr__izy = 0.0
        dmixf__lmzpo = 0.0
        pbe__tmrq = 0
        for hwbw__oihm in numba.parfors.parfor.internal_prange(len(arr)):
            isim__zzg = 0.0
            jvn__flg = 0
            if not bodo.libs.array_kernels.isna(arr, hwbw__oihm) or not skipna:
                isim__zzg = arr[hwbw__oihm]
                jvn__flg = 1
            acnrr__izy += isim__zzg
            dmixf__lmzpo += isim__zzg * isim__zzg
            pbe__tmrq += jvn__flg
        syz__zheg = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            acnrr__izy, dmixf__lmzpo, pbe__tmrq, ddof)
        return syz__zheg
    return impl


def array_op_std(arr, skipna=True, ddof=1):
    pass


@overload(array_op_std)
def overload_array_op_std(arr, skipna=True, ddof=1):
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr, skipna=True, ddof=1):
            return pd.Timedelta(types.int64(array_op_var(arr.view(np.int64),
                skipna, ddof) ** 0.5))
        return impl_dt64
    return lambda arr, skipna=True, ddof=1: array_op_var(arr, skipna, ddof
        ) ** 0.5


def array_op_quantile(arr, q):
    pass


@overload(array_op_quantile)
def overload_array_op_quantile(arr, q):
    if is_iterable_type(q):
        if arr.dtype == bodo.datetime64ns:

            def _impl_list_dt(arr, q):
                zifzo__cru = np.empty(len(q), np.int64)
                for hwbw__oihm in range(len(q)):
                    axerc__nll = np.float64(q[hwbw__oihm])
                    zifzo__cru[hwbw__oihm] = bodo.libs.array_kernels.quantile(
                        arr.view(np.int64), axerc__nll)
                return zifzo__cru.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            zifzo__cru = np.empty(len(q), np.float64)
            for hwbw__oihm in range(len(q)):
                axerc__nll = np.float64(q[hwbw__oihm])
                zifzo__cru[hwbw__oihm] = bodo.libs.array_kernels.quantile(arr,
                    axerc__nll)
            return zifzo__cru
        return impl_list
    if arr.dtype == bodo.datetime64ns:

        def _impl_dt(arr, q):
            return pd.Timestamp(bodo.libs.array_kernels.quantile(arr.view(
                np.int64), np.float64(q)))
        return _impl_dt

    def impl(arr, q):
        return bodo.libs.array_kernels.quantile(arr, np.float64(q))
    return impl


def array_op_sum(arr, skipna, min_count):
    pass


@overload(array_op_sum, no_unliteral=True)
def overload_array_op_sum(arr, skipna, min_count):
    if isinstance(arr.dtype, types.Integer):
        ukr__wqru = types.intp
    elif arr.dtype == types.bool_:
        ukr__wqru = np.int64
    else:
        ukr__wqru = arr.dtype
    eevm__kfiak = ukr__wqru(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            splrq__tair = eevm__kfiak
            zomai__stcl = len(arr)
            pbe__tmrq = 0
            for hwbw__oihm in numba.parfors.parfor.internal_prange(zomai__stcl
                ):
                isim__zzg = eevm__kfiak
                jvn__flg = 0
                if not bodo.libs.array_kernels.isna(arr, hwbw__oihm
                    ) or not skipna:
                    isim__zzg = arr[hwbw__oihm]
                    jvn__flg = 1
                splrq__tair += isim__zzg
                pbe__tmrq += jvn__flg
            syz__zheg = bodo.hiframes.series_kernels._var_handle_mincount(
                splrq__tair, pbe__tmrq, min_count)
            return syz__zheg
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            splrq__tair = eevm__kfiak
            zomai__stcl = len(arr)
            for hwbw__oihm in numba.parfors.parfor.internal_prange(zomai__stcl
                ):
                isim__zzg = eevm__kfiak
                if not bodo.libs.array_kernels.isna(arr, hwbw__oihm):
                    isim__zzg = arr[hwbw__oihm]
                splrq__tair += isim__zzg
            return splrq__tair
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    vvop__asbwz = arr.dtype(1)
    if arr.dtype == types.bool_:
        vvop__asbwz = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            splrq__tair = vvop__asbwz
            pbe__tmrq = 0
            for hwbw__oihm in numba.parfors.parfor.internal_prange(len(arr)):
                isim__zzg = vvop__asbwz
                jvn__flg = 0
                if not bodo.libs.array_kernels.isna(arr, hwbw__oihm
                    ) or not skipna:
                    isim__zzg = arr[hwbw__oihm]
                    jvn__flg = 1
                pbe__tmrq += jvn__flg
                splrq__tair *= isim__zzg
            syz__zheg = bodo.hiframes.series_kernels._var_handle_mincount(
                splrq__tair, pbe__tmrq, min_count)
            return syz__zheg
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            splrq__tair = vvop__asbwz
            for hwbw__oihm in numba.parfors.parfor.internal_prange(len(arr)):
                isim__zzg = vvop__asbwz
                if not bodo.libs.array_kernels.isna(arr, hwbw__oihm):
                    isim__zzg = arr[hwbw__oihm]
                splrq__tair *= isim__zzg
            return splrq__tair
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        hwbw__oihm = bodo.libs.array_kernels._nan_argmax(arr)
        return index[hwbw__oihm]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        hwbw__oihm = bodo.libs.array_kernels._nan_argmin(arr)
        return index[hwbw__oihm]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            hov__yfl = {}
            for bre__dkgf in values:
                hov__yfl[bodo.utils.conversion.box_if_dt64(bre__dkgf)] = 0
            return hov__yfl
        return impl
    else:

        def impl(values, use_hash_impl):
            return values
        return impl


def array_op_isin(arr, values):
    pass


@overload(array_op_isin, inline='always')
def overload_array_op_isin(arr, values):
    use_hash_impl = element_type(values) == element_type(arr
        ) and is_hashable_type(element_type(values))

    def impl(arr, values):
        values = bodo.libs.array_ops._convert_isin_values(values, use_hash_impl
            )
        numba.parfors.parfor.init_prange()
        zomai__stcl = len(arr)
        zifzo__cru = np.empty(zomai__stcl, np.bool_)
        for hwbw__oihm in numba.parfors.parfor.internal_prange(zomai__stcl):
            zifzo__cru[hwbw__oihm] = bodo.utils.conversion.box_if_dt64(arr[
                hwbw__oihm]) in values
        return zifzo__cru
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    lso__wkec = len(in_arr_tup) != 1
    etxgt__vvfe = list(in_arr_tup.types)
    ybxn__igo = 'def impl(in_arr_tup):\n'
    ybxn__igo += '  n = len(in_arr_tup[0])\n'
    if lso__wkec:
        bwei__axi = ', '.join([f'in_arr_tup[{hwbw__oihm}][unused]' for
            hwbw__oihm in range(len(in_arr_tup))])
        tlxme__wkjr = ', '.join(['False' for qeadj__jms in range(len(
            in_arr_tup))])
        ybxn__igo += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({bwei__axi},), ({tlxme__wkjr},)): 0 for unused in range(0)}}
"""
        ybxn__igo += '  map_vector = np.empty(n, np.int64)\n'
        for hwbw__oihm, aqat__oepd in enumerate(etxgt__vvfe):
            ybxn__igo += f'  in_lst_{hwbw__oihm} = []\n'
            if aqat__oepd == bodo.string_array_type:
                ybxn__igo += f'  total_len_{hwbw__oihm} = 0\n'
            ybxn__igo += f'  null_in_lst_{hwbw__oihm} = []\n'
        ybxn__igo += '  for i in range(n):\n'
        etmvq__xndi = ', '.join([f'in_arr_tup[{hwbw__oihm}][i]' for
            hwbw__oihm in range(len(etxgt__vvfe))])
        ewloc__fiwnt = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{hwbw__oihm}], i)' for
            hwbw__oihm in range(len(etxgt__vvfe))])
        ybxn__igo += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({etmvq__xndi},), ({ewloc__fiwnt},))
"""
        ybxn__igo += '    if data_val not in arr_map:\n'
        ybxn__igo += '      set_val = len(arr_map)\n'
        ybxn__igo += '      values_tup = data_val._data\n'
        ybxn__igo += '      nulls_tup = data_val._null_values\n'
        for hwbw__oihm, aqat__oepd in enumerate(etxgt__vvfe):
            ybxn__igo += (
                f'      in_lst_{hwbw__oihm}.append(values_tup[{hwbw__oihm}])\n'
                )
            ybxn__igo += (
                f'      null_in_lst_{hwbw__oihm}.append(nulls_tup[{hwbw__oihm}])\n'
                )
            if aqat__oepd == bodo.string_array_type:
                ybxn__igo += f"""      total_len_{hwbw__oihm}  += nulls_tup[{hwbw__oihm}] * len(values_tup[{hwbw__oihm}])
"""
        ybxn__igo += '      arr_map[data_val] = len(arr_map)\n'
        ybxn__igo += '    else:\n'
        ybxn__igo += '      set_val = arr_map[data_val]\n'
        ybxn__igo += '    map_vector[i] = set_val\n'
        ybxn__igo += '  n_rows = len(arr_map)\n'
        for hwbw__oihm, aqat__oepd in enumerate(etxgt__vvfe):
            if aqat__oepd == bodo.string_array_type:
                ybxn__igo += f"""  out_arr_{hwbw__oihm} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{hwbw__oihm})
"""
            else:
                ybxn__igo += f"""  out_arr_{hwbw__oihm} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{hwbw__oihm}], (-1,))
"""
        ybxn__igo += '  for j in range(len(arr_map)):\n'
        for hwbw__oihm in range(len(etxgt__vvfe)):
            ybxn__igo += f'    if null_in_lst_{hwbw__oihm}[j]:\n'
            ybxn__igo += (
                f'      bodo.libs.array_kernels.setna(out_arr_{hwbw__oihm}, j)\n'
                )
            ybxn__igo += '    else:\n'
            ybxn__igo += (
                f'      out_arr_{hwbw__oihm}[j] = in_lst_{hwbw__oihm}[j]\n')
        abjts__bgay = ', '.join([f'out_arr_{hwbw__oihm}' for hwbw__oihm in
            range(len(etxgt__vvfe))])
        ybxn__igo += f'  return ({abjts__bgay},), map_vector\n'
    else:
        ybxn__igo += '  in_arr = in_arr_tup[0]\n'
        ybxn__igo += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        ybxn__igo += '  map_vector = np.empty(n, np.int64)\n'
        ybxn__igo += '  is_na = 0\n'
        ybxn__igo += '  in_lst = []\n'
        if etxgt__vvfe[0] == bodo.string_array_type:
            ybxn__igo += '  total_len = 0\n'
        ybxn__igo += '  for i in range(n):\n'
        ybxn__igo += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        ybxn__igo += '      is_na = 1\n'
        ybxn__igo += (
            '      # Always put NA in the last location. We can safely use\n')
        ybxn__igo += (
            '      # -1 because in_arr[-1] == in_arr[len(in_arr) - 1]\n')
        ybxn__igo += '      set_val = -1\n'
        ybxn__igo += '    else:\n'
        ybxn__igo += '      data_val = in_arr[i]\n'
        ybxn__igo += '      if data_val not in arr_map:\n'
        ybxn__igo += '        set_val = len(arr_map)\n'
        ybxn__igo += '        in_lst.append(data_val)\n'
        if etxgt__vvfe[0] == bodo.string_array_type:
            ybxn__igo += '        total_len += len(data_val)\n'
        ybxn__igo += '        arr_map[data_val] = len(arr_map)\n'
        ybxn__igo += '      else:\n'
        ybxn__igo += '        set_val = arr_map[data_val]\n'
        ybxn__igo += '    map_vector[i] = set_val\n'
        ybxn__igo += '  n_rows = len(arr_map) + is_na\n'
        if etxgt__vvfe[0] == bodo.string_array_type:
            ybxn__igo += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            ybxn__igo += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        ybxn__igo += '  for j in range(len(arr_map)):\n'
        ybxn__igo += '    out_arr[j] = in_lst[j]\n'
        ybxn__igo += '  if is_na:\n'
        ybxn__igo += '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n'
        ybxn__igo += f'  return (out_arr,), map_vector\n'
    wsndc__czelb = {}
    exec(ybxn__igo, {'bodo': bodo, 'np': np}, wsndc__czelb)
    impl = wsndc__czelb['impl']
    return impl
