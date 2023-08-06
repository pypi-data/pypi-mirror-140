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
    anfk__hwhn = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(anfk__hwhn.ctypes,
        arr, parallel, skipna)
    return anfk__hwhn[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        ejyfk__oirpe = len(arr)
        gytj__mvi = np.empty(ejyfk__oirpe, np.bool_)
        for kwo__rkpc in numba.parfors.parfor.internal_prange(ejyfk__oirpe):
            gytj__mvi[kwo__rkpc] = bodo.libs.array_kernels.isna(arr, kwo__rkpc)
        return gytj__mvi
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        ubcw__vvn = 0
        for kwo__rkpc in numba.parfors.parfor.internal_prange(len(arr)):
            gaxh__kuv = 0
            if not bodo.libs.array_kernels.isna(arr, kwo__rkpc):
                gaxh__kuv = 1
            ubcw__vvn += gaxh__kuv
        anfk__hwhn = ubcw__vvn
        return anfk__hwhn
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    tslvj__dqqd = array_op_count(arr)
    ufb__hlzlg = array_op_min(arr)
    xlf__eik = array_op_max(arr)
    vzjln__fee = array_op_mean(arr)
    mlt__xiq = array_op_std(arr)
    djx__qbvah = array_op_quantile(arr, 0.25)
    gtv__nkiyy = array_op_quantile(arr, 0.5)
    loq__drp = array_op_quantile(arr, 0.75)
    return (tslvj__dqqd, vzjln__fee, mlt__xiq, ufb__hlzlg, djx__qbvah,
        gtv__nkiyy, loq__drp, xlf__eik)


def array_op_describe_dt_impl(arr):
    tslvj__dqqd = array_op_count(arr)
    ufb__hlzlg = array_op_min(arr)
    xlf__eik = array_op_max(arr)
    vzjln__fee = array_op_mean(arr)
    djx__qbvah = array_op_quantile(arr, 0.25)
    gtv__nkiyy = array_op_quantile(arr, 0.5)
    loq__drp = array_op_quantile(arr, 0.75)
    return (tslvj__dqqd, vzjln__fee, ufb__hlzlg, djx__qbvah, gtv__nkiyy,
        loq__drp, xlf__eik)


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
            xpa__wfz = numba.cpython.builtins.get_type_max_value(np.int64)
            ubcw__vvn = 0
            for kwo__rkpc in numba.parfors.parfor.internal_prange(len(arr)):
                sxj__jfo = xpa__wfz
                gaxh__kuv = 0
                if not bodo.libs.array_kernels.isna(arr, kwo__rkpc):
                    sxj__jfo = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[kwo__rkpc]))
                    gaxh__kuv = 1
                xpa__wfz = min(xpa__wfz, sxj__jfo)
                ubcw__vvn += gaxh__kuv
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(xpa__wfz,
                ubcw__vvn)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            xpa__wfz = numba.cpython.builtins.get_type_max_value(np.int64)
            ubcw__vvn = 0
            for kwo__rkpc in numba.parfors.parfor.internal_prange(len(arr)):
                sxj__jfo = xpa__wfz
                gaxh__kuv = 0
                if not bodo.libs.array_kernels.isna(arr, kwo__rkpc):
                    sxj__jfo = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[kwo__rkpc])
                    gaxh__kuv = 1
                xpa__wfz = min(xpa__wfz, sxj__jfo)
                ubcw__vvn += gaxh__kuv
            return bodo.hiframes.pd_index_ext._dti_val_finalize(xpa__wfz,
                ubcw__vvn)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            keze__luke = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            xpa__wfz = numba.cpython.builtins.get_type_max_value(np.int64)
            ubcw__vvn = 0
            for kwo__rkpc in numba.parfors.parfor.internal_prange(len(
                keze__luke)):
                kdg__ejku = keze__luke[kwo__rkpc]
                if kdg__ejku == -1:
                    continue
                xpa__wfz = min(xpa__wfz, kdg__ejku)
                ubcw__vvn += 1
            anfk__hwhn = bodo.hiframes.series_kernels._box_cat_val(xpa__wfz,
                arr.dtype, ubcw__vvn)
            return anfk__hwhn
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            xpa__wfz = bodo.hiframes.series_kernels._get_date_max_value()
            ubcw__vvn = 0
            for kwo__rkpc in numba.parfors.parfor.internal_prange(len(arr)):
                sxj__jfo = xpa__wfz
                gaxh__kuv = 0
                if not bodo.libs.array_kernels.isna(arr, kwo__rkpc):
                    sxj__jfo = arr[kwo__rkpc]
                    gaxh__kuv = 1
                xpa__wfz = min(xpa__wfz, sxj__jfo)
                ubcw__vvn += gaxh__kuv
            anfk__hwhn = bodo.hiframes.series_kernels._sum_handle_nan(xpa__wfz,
                ubcw__vvn)
            return anfk__hwhn
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        xpa__wfz = bodo.hiframes.series_kernels._get_type_max_value(arr.dtype)
        ubcw__vvn = 0
        for kwo__rkpc in numba.parfors.parfor.internal_prange(len(arr)):
            sxj__jfo = xpa__wfz
            gaxh__kuv = 0
            if not bodo.libs.array_kernels.isna(arr, kwo__rkpc):
                sxj__jfo = arr[kwo__rkpc]
                gaxh__kuv = 1
            xpa__wfz = min(xpa__wfz, sxj__jfo)
            ubcw__vvn += gaxh__kuv
        anfk__hwhn = bodo.hiframes.series_kernels._sum_handle_nan(xpa__wfz,
            ubcw__vvn)
        return anfk__hwhn
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            xpa__wfz = numba.cpython.builtins.get_type_min_value(np.int64)
            ubcw__vvn = 0
            for kwo__rkpc in numba.parfors.parfor.internal_prange(len(arr)):
                sxj__jfo = xpa__wfz
                gaxh__kuv = 0
                if not bodo.libs.array_kernels.isna(arr, kwo__rkpc):
                    sxj__jfo = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[kwo__rkpc]))
                    gaxh__kuv = 1
                xpa__wfz = max(xpa__wfz, sxj__jfo)
                ubcw__vvn += gaxh__kuv
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(xpa__wfz,
                ubcw__vvn)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            xpa__wfz = numba.cpython.builtins.get_type_min_value(np.int64)
            ubcw__vvn = 0
            for kwo__rkpc in numba.parfors.parfor.internal_prange(len(arr)):
                sxj__jfo = xpa__wfz
                gaxh__kuv = 0
                if not bodo.libs.array_kernels.isna(arr, kwo__rkpc):
                    sxj__jfo = bodo.hiframes.pd_timestamp_ext.dt64_to_integer(
                        arr[kwo__rkpc])
                    gaxh__kuv = 1
                xpa__wfz = max(xpa__wfz, sxj__jfo)
                ubcw__vvn += gaxh__kuv
            return bodo.hiframes.pd_index_ext._dti_val_finalize(xpa__wfz,
                ubcw__vvn)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            keze__luke = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            xpa__wfz = -1
            for kwo__rkpc in numba.parfors.parfor.internal_prange(len(
                keze__luke)):
                xpa__wfz = max(xpa__wfz, keze__luke[kwo__rkpc])
            anfk__hwhn = bodo.hiframes.series_kernels._box_cat_val(xpa__wfz,
                arr.dtype, 1)
            return anfk__hwhn
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            xpa__wfz = bodo.hiframes.series_kernels._get_date_min_value()
            ubcw__vvn = 0
            for kwo__rkpc in numba.parfors.parfor.internal_prange(len(arr)):
                sxj__jfo = xpa__wfz
                gaxh__kuv = 0
                if not bodo.libs.array_kernels.isna(arr, kwo__rkpc):
                    sxj__jfo = arr[kwo__rkpc]
                    gaxh__kuv = 1
                xpa__wfz = max(xpa__wfz, sxj__jfo)
                ubcw__vvn += gaxh__kuv
            anfk__hwhn = bodo.hiframes.series_kernels._sum_handle_nan(xpa__wfz,
                ubcw__vvn)
            return anfk__hwhn
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        xpa__wfz = bodo.hiframes.series_kernels._get_type_min_value(arr.dtype)
        ubcw__vvn = 0
        for kwo__rkpc in numba.parfors.parfor.internal_prange(len(arr)):
            sxj__jfo = xpa__wfz
            gaxh__kuv = 0
            if not bodo.libs.array_kernels.isna(arr, kwo__rkpc):
                sxj__jfo = arr[kwo__rkpc]
                gaxh__kuv = 1
            xpa__wfz = max(xpa__wfz, sxj__jfo)
            ubcw__vvn += gaxh__kuv
        anfk__hwhn = bodo.hiframes.series_kernels._sum_handle_nan(xpa__wfz,
            ubcw__vvn)
        return anfk__hwhn
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
    egifz__mku = types.float64
    ule__awppw = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        egifz__mku = types.float32
        ule__awppw = types.float32
    coa__jcq = egifz__mku(0)
    eav__xtqmr = ule__awppw(0)
    eazs__mgxya = ule__awppw(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        xpa__wfz = coa__jcq
        ubcw__vvn = eav__xtqmr
        for kwo__rkpc in numba.parfors.parfor.internal_prange(len(arr)):
            sxj__jfo = coa__jcq
            gaxh__kuv = eav__xtqmr
            if not bodo.libs.array_kernels.isna(arr, kwo__rkpc):
                sxj__jfo = arr[kwo__rkpc]
                gaxh__kuv = eazs__mgxya
            xpa__wfz += sxj__jfo
            ubcw__vvn += gaxh__kuv
        anfk__hwhn = bodo.hiframes.series_kernels._mean_handle_nan(xpa__wfz,
            ubcw__vvn)
        return anfk__hwhn
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        kmxw__slw = 0.0
        xzxqc__xcskr = 0.0
        ubcw__vvn = 0
        for kwo__rkpc in numba.parfors.parfor.internal_prange(len(arr)):
            sxj__jfo = 0.0
            gaxh__kuv = 0
            if not bodo.libs.array_kernels.isna(arr, kwo__rkpc) or not skipna:
                sxj__jfo = arr[kwo__rkpc]
                gaxh__kuv = 1
            kmxw__slw += sxj__jfo
            xzxqc__xcskr += sxj__jfo * sxj__jfo
            ubcw__vvn += gaxh__kuv
        anfk__hwhn = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            kmxw__slw, xzxqc__xcskr, ubcw__vvn, ddof)
        return anfk__hwhn
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
                gytj__mvi = np.empty(len(q), np.int64)
                for kwo__rkpc in range(len(q)):
                    cbn__xop = np.float64(q[kwo__rkpc])
                    gytj__mvi[kwo__rkpc] = bodo.libs.array_kernels.quantile(arr
                        .view(np.int64), cbn__xop)
                return gytj__mvi.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            gytj__mvi = np.empty(len(q), np.float64)
            for kwo__rkpc in range(len(q)):
                cbn__xop = np.float64(q[kwo__rkpc])
                gytj__mvi[kwo__rkpc] = bodo.libs.array_kernels.quantile(arr,
                    cbn__xop)
            return gytj__mvi
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
        tcpb__mavc = types.intp
    elif arr.dtype == types.bool_:
        tcpb__mavc = np.int64
    else:
        tcpb__mavc = arr.dtype
    xsucg__swm = tcpb__mavc(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            xpa__wfz = xsucg__swm
            ejyfk__oirpe = len(arr)
            ubcw__vvn = 0
            for kwo__rkpc in numba.parfors.parfor.internal_prange(ejyfk__oirpe
                ):
                sxj__jfo = xsucg__swm
                gaxh__kuv = 0
                if not bodo.libs.array_kernels.isna(arr, kwo__rkpc
                    ) or not skipna:
                    sxj__jfo = arr[kwo__rkpc]
                    gaxh__kuv = 1
                xpa__wfz += sxj__jfo
                ubcw__vvn += gaxh__kuv
            anfk__hwhn = bodo.hiframes.series_kernels._var_handle_mincount(
                xpa__wfz, ubcw__vvn, min_count)
            return anfk__hwhn
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            xpa__wfz = xsucg__swm
            ejyfk__oirpe = len(arr)
            for kwo__rkpc in numba.parfors.parfor.internal_prange(ejyfk__oirpe
                ):
                sxj__jfo = xsucg__swm
                if not bodo.libs.array_kernels.isna(arr, kwo__rkpc):
                    sxj__jfo = arr[kwo__rkpc]
                xpa__wfz += sxj__jfo
            return xpa__wfz
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    cobj__riqdf = arr.dtype(1)
    if arr.dtype == types.bool_:
        cobj__riqdf = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            xpa__wfz = cobj__riqdf
            ubcw__vvn = 0
            for kwo__rkpc in numba.parfors.parfor.internal_prange(len(arr)):
                sxj__jfo = cobj__riqdf
                gaxh__kuv = 0
                if not bodo.libs.array_kernels.isna(arr, kwo__rkpc
                    ) or not skipna:
                    sxj__jfo = arr[kwo__rkpc]
                    gaxh__kuv = 1
                ubcw__vvn += gaxh__kuv
                xpa__wfz *= sxj__jfo
            anfk__hwhn = bodo.hiframes.series_kernels._var_handle_mincount(
                xpa__wfz, ubcw__vvn, min_count)
            return anfk__hwhn
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            xpa__wfz = cobj__riqdf
            for kwo__rkpc in numba.parfors.parfor.internal_prange(len(arr)):
                sxj__jfo = cobj__riqdf
                if not bodo.libs.array_kernels.isna(arr, kwo__rkpc):
                    sxj__jfo = arr[kwo__rkpc]
                xpa__wfz *= sxj__jfo
            return xpa__wfz
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        kwo__rkpc = bodo.libs.array_kernels._nan_argmax(arr)
        return index[kwo__rkpc]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        kwo__rkpc = bodo.libs.array_kernels._nan_argmin(arr)
        return index[kwo__rkpc]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            dydas__myfn = {}
            for fvsmv__ibbp in values:
                dydas__myfn[bodo.utils.conversion.box_if_dt64(fvsmv__ibbp)] = 0
            return dydas__myfn
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
        ejyfk__oirpe = len(arr)
        gytj__mvi = np.empty(ejyfk__oirpe, np.bool_)
        for kwo__rkpc in numba.parfors.parfor.internal_prange(ejyfk__oirpe):
            gytj__mvi[kwo__rkpc] = bodo.utils.conversion.box_if_dt64(arr[
                kwo__rkpc]) in values
        return gytj__mvi
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    unxow__vbbdm = len(in_arr_tup) != 1
    avm__veioz = list(in_arr_tup.types)
    upxte__qbvo = 'def impl(in_arr_tup):\n'
    upxte__qbvo += '  n = len(in_arr_tup[0])\n'
    if unxow__vbbdm:
        ibyz__fvuv = ', '.join([f'in_arr_tup[{kwo__rkpc}][unused]' for
            kwo__rkpc in range(len(in_arr_tup))])
        exjm__tjh = ', '.join(['False' for krd__bqwsl in range(len(
            in_arr_tup))])
        upxte__qbvo += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({ibyz__fvuv},), ({exjm__tjh},)): 0 for unused in range(0)}}
"""
        upxte__qbvo += '  map_vector = np.empty(n, np.int64)\n'
        for kwo__rkpc, kjrx__kpki in enumerate(avm__veioz):
            upxte__qbvo += f'  in_lst_{kwo__rkpc} = []\n'
            if kjrx__kpki == bodo.string_array_type:
                upxte__qbvo += f'  total_len_{kwo__rkpc} = 0\n'
            upxte__qbvo += f'  null_in_lst_{kwo__rkpc} = []\n'
        upxte__qbvo += '  for i in range(n):\n'
        hqcl__pvb = ', '.join([f'in_arr_tup[{kwo__rkpc}][i]' for kwo__rkpc in
            range(len(avm__veioz))])
        slks__rwyn = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{kwo__rkpc}], i)' for
            kwo__rkpc in range(len(avm__veioz))])
        upxte__qbvo += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({hqcl__pvb},), ({slks__rwyn},))
"""
        upxte__qbvo += '    if data_val not in arr_map:\n'
        upxte__qbvo += '      set_val = len(arr_map)\n'
        upxte__qbvo += '      values_tup = data_val._data\n'
        upxte__qbvo += '      nulls_tup = data_val._null_values\n'
        for kwo__rkpc, kjrx__kpki in enumerate(avm__veioz):
            upxte__qbvo += (
                f'      in_lst_{kwo__rkpc}.append(values_tup[{kwo__rkpc}])\n')
            upxte__qbvo += (
                f'      null_in_lst_{kwo__rkpc}.append(nulls_tup[{kwo__rkpc}])\n'
                )
            if kjrx__kpki == bodo.string_array_type:
                upxte__qbvo += f"""      total_len_{kwo__rkpc}  += nulls_tup[{kwo__rkpc}] * len(values_tup[{kwo__rkpc}])
"""
        upxte__qbvo += '      arr_map[data_val] = len(arr_map)\n'
        upxte__qbvo += '    else:\n'
        upxte__qbvo += '      set_val = arr_map[data_val]\n'
        upxte__qbvo += '    map_vector[i] = set_val\n'
        upxte__qbvo += '  n_rows = len(arr_map)\n'
        for kwo__rkpc, kjrx__kpki in enumerate(avm__veioz):
            if kjrx__kpki == bodo.string_array_type:
                upxte__qbvo += f"""  out_arr_{kwo__rkpc} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{kwo__rkpc})
"""
            else:
                upxte__qbvo += f"""  out_arr_{kwo__rkpc} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{kwo__rkpc}], (-1,))
"""
        upxte__qbvo += '  for j in range(len(arr_map)):\n'
        for kwo__rkpc in range(len(avm__veioz)):
            upxte__qbvo += f'    if null_in_lst_{kwo__rkpc}[j]:\n'
            upxte__qbvo += (
                f'      bodo.libs.array_kernels.setna(out_arr_{kwo__rkpc}, j)\n'
                )
            upxte__qbvo += '    else:\n'
            upxte__qbvo += (
                f'      out_arr_{kwo__rkpc}[j] = in_lst_{kwo__rkpc}[j]\n')
        uqm__xybgg = ', '.join([f'out_arr_{kwo__rkpc}' for kwo__rkpc in
            range(len(avm__veioz))])
        upxte__qbvo += f'  return ({uqm__xybgg},), map_vector\n'
    else:
        upxte__qbvo += '  in_arr = in_arr_tup[0]\n'
        upxte__qbvo += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        upxte__qbvo += '  map_vector = np.empty(n, np.int64)\n'
        upxte__qbvo += '  is_na = 0\n'
        upxte__qbvo += '  in_lst = []\n'
        if avm__veioz[0] == bodo.string_array_type:
            upxte__qbvo += '  total_len = 0\n'
        upxte__qbvo += '  for i in range(n):\n'
        upxte__qbvo += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        upxte__qbvo += '      is_na = 1\n'
        upxte__qbvo += (
            '      # Always put NA in the last location. We can safely use\n')
        upxte__qbvo += (
            '      # -1 because in_arr[-1] == in_arr[len(in_arr) - 1]\n')
        upxte__qbvo += '      set_val = -1\n'
        upxte__qbvo += '    else:\n'
        upxte__qbvo += '      data_val = in_arr[i]\n'
        upxte__qbvo += '      if data_val not in arr_map:\n'
        upxte__qbvo += '        set_val = len(arr_map)\n'
        upxte__qbvo += '        in_lst.append(data_val)\n'
        if avm__veioz[0] == bodo.string_array_type:
            upxte__qbvo += '        total_len += len(data_val)\n'
        upxte__qbvo += '        arr_map[data_val] = len(arr_map)\n'
        upxte__qbvo += '      else:\n'
        upxte__qbvo += '        set_val = arr_map[data_val]\n'
        upxte__qbvo += '    map_vector[i] = set_val\n'
        upxte__qbvo += '  n_rows = len(arr_map) + is_na\n'
        if avm__veioz[0] == bodo.string_array_type:
            upxte__qbvo += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            upxte__qbvo += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        upxte__qbvo += '  for j in range(len(arr_map)):\n'
        upxte__qbvo += '    out_arr[j] = in_lst[j]\n'
        upxte__qbvo += '  if is_na:\n'
        upxte__qbvo += (
            '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n')
        upxte__qbvo += f'  return (out_arr,), map_vector\n'
    ivtv__mzxi = {}
    exec(upxte__qbvo, {'bodo': bodo, 'np': np}, ivtv__mzxi)
    impl = ivtv__mzxi['impl']
    return impl
