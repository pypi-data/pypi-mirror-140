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
    gvo__igaa = np.empty(1, types.float64)
    bodo.libs.array_kernels.median_series_computation(gvo__igaa.ctypes, arr,
        parallel, skipna)
    return gvo__igaa[0]


def array_op_isna(arr):
    pass


@overload(array_op_isna)
def overload_array_op_isna(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        pgstq__nbm = len(arr)
        xtp__dbst = np.empty(pgstq__nbm, np.bool_)
        for pwrt__nxxuo in numba.parfors.parfor.internal_prange(pgstq__nbm):
            xtp__dbst[pwrt__nxxuo] = bodo.libs.array_kernels.isna(arr,
                pwrt__nxxuo)
        return xtp__dbst
    return impl


def array_op_count(arr):
    pass


@overload(array_op_count)
def overload_array_op_count(arr):

    def impl(arr):
        numba.parfors.parfor.init_prange()
        pfhg__coyl = 0
        for pwrt__nxxuo in numba.parfors.parfor.internal_prange(len(arr)):
            yjdcq__yhq = 0
            if not bodo.libs.array_kernels.isna(arr, pwrt__nxxuo):
                yjdcq__yhq = 1
            pfhg__coyl += yjdcq__yhq
        gvo__igaa = pfhg__coyl
        return gvo__igaa
    return impl


def array_op_describe(arr):
    pass


def array_op_describe_impl(arr):
    yhytu__kcumm = array_op_count(arr)
    kydjg__gpio = array_op_min(arr)
    zmnzj__pjt = array_op_max(arr)
    zwht__zorvs = array_op_mean(arr)
    fonak__qxaf = array_op_std(arr)
    wcwc__orxv = array_op_quantile(arr, 0.25)
    mte__gzr = array_op_quantile(arr, 0.5)
    yzi__bckf = array_op_quantile(arr, 0.75)
    return (yhytu__kcumm, zwht__zorvs, fonak__qxaf, kydjg__gpio, wcwc__orxv,
        mte__gzr, yzi__bckf, zmnzj__pjt)


def array_op_describe_dt_impl(arr):
    yhytu__kcumm = array_op_count(arr)
    kydjg__gpio = array_op_min(arr)
    zmnzj__pjt = array_op_max(arr)
    zwht__zorvs = array_op_mean(arr)
    wcwc__orxv = array_op_quantile(arr, 0.25)
    mte__gzr = array_op_quantile(arr, 0.5)
    yzi__bckf = array_op_quantile(arr, 0.75)
    return (yhytu__kcumm, zwht__zorvs, kydjg__gpio, wcwc__orxv, mte__gzr,
        yzi__bckf, zmnzj__pjt)


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
            orvi__tsmv = numba.cpython.builtins.get_type_max_value(np.int64)
            pfhg__coyl = 0
            for pwrt__nxxuo in numba.parfors.parfor.internal_prange(len(arr)):
                knzv__hlbxs = orvi__tsmv
                yjdcq__yhq = 0
                if not bodo.libs.array_kernels.isna(arr, pwrt__nxxuo):
                    knzv__hlbxs = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[pwrt__nxxuo]))
                    yjdcq__yhq = 1
                orvi__tsmv = min(orvi__tsmv, knzv__hlbxs)
                pfhg__coyl += yjdcq__yhq
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(orvi__tsmv,
                pfhg__coyl)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            orvi__tsmv = numba.cpython.builtins.get_type_max_value(np.int64)
            pfhg__coyl = 0
            for pwrt__nxxuo in numba.parfors.parfor.internal_prange(len(arr)):
                knzv__hlbxs = orvi__tsmv
                yjdcq__yhq = 0
                if not bodo.libs.array_kernels.isna(arr, pwrt__nxxuo):
                    knzv__hlbxs = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[pwrt__nxxuo]))
                    yjdcq__yhq = 1
                orvi__tsmv = min(orvi__tsmv, knzv__hlbxs)
                pfhg__coyl += yjdcq__yhq
            return bodo.hiframes.pd_index_ext._dti_val_finalize(orvi__tsmv,
                pfhg__coyl)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            tmdt__oqasl = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            orvi__tsmv = numba.cpython.builtins.get_type_max_value(np.int64)
            pfhg__coyl = 0
            for pwrt__nxxuo in numba.parfors.parfor.internal_prange(len(
                tmdt__oqasl)):
                gewcl__xjmo = tmdt__oqasl[pwrt__nxxuo]
                if gewcl__xjmo == -1:
                    continue
                orvi__tsmv = min(orvi__tsmv, gewcl__xjmo)
                pfhg__coyl += 1
            gvo__igaa = bodo.hiframes.series_kernels._box_cat_val(orvi__tsmv,
                arr.dtype, pfhg__coyl)
            return gvo__igaa
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            orvi__tsmv = bodo.hiframes.series_kernels._get_date_max_value()
            pfhg__coyl = 0
            for pwrt__nxxuo in numba.parfors.parfor.internal_prange(len(arr)):
                knzv__hlbxs = orvi__tsmv
                yjdcq__yhq = 0
                if not bodo.libs.array_kernels.isna(arr, pwrt__nxxuo):
                    knzv__hlbxs = arr[pwrt__nxxuo]
                    yjdcq__yhq = 1
                orvi__tsmv = min(orvi__tsmv, knzv__hlbxs)
                pfhg__coyl += yjdcq__yhq
            gvo__igaa = bodo.hiframes.series_kernels._sum_handle_nan(orvi__tsmv
                , pfhg__coyl)
            return gvo__igaa
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        orvi__tsmv = bodo.hiframes.series_kernels._get_type_max_value(arr.dtype
            )
        pfhg__coyl = 0
        for pwrt__nxxuo in numba.parfors.parfor.internal_prange(len(arr)):
            knzv__hlbxs = orvi__tsmv
            yjdcq__yhq = 0
            if not bodo.libs.array_kernels.isna(arr, pwrt__nxxuo):
                knzv__hlbxs = arr[pwrt__nxxuo]
                yjdcq__yhq = 1
            orvi__tsmv = min(orvi__tsmv, knzv__hlbxs)
            pfhg__coyl += yjdcq__yhq
        gvo__igaa = bodo.hiframes.series_kernels._sum_handle_nan(orvi__tsmv,
            pfhg__coyl)
        return gvo__igaa
    return impl


def array_op_max(arr):
    pass


@overload(array_op_max)
def overload_array_op_max(arr):
    if arr.dtype == bodo.timedelta64ns:

        def impl_td64(arr):
            numba.parfors.parfor.init_prange()
            orvi__tsmv = numba.cpython.builtins.get_type_min_value(np.int64)
            pfhg__coyl = 0
            for pwrt__nxxuo in numba.parfors.parfor.internal_prange(len(arr)):
                knzv__hlbxs = orvi__tsmv
                yjdcq__yhq = 0
                if not bodo.libs.array_kernels.isna(arr, pwrt__nxxuo):
                    knzv__hlbxs = (bodo.hiframes.pd_timestamp_ext.
                        timedelta64_to_integer(arr[pwrt__nxxuo]))
                    yjdcq__yhq = 1
                orvi__tsmv = max(orvi__tsmv, knzv__hlbxs)
                pfhg__coyl += yjdcq__yhq
            return bodo.hiframes.pd_index_ext._tdi_val_finalize(orvi__tsmv,
                pfhg__coyl)
        return impl_td64
    if arr.dtype == bodo.datetime64ns:

        def impl_dt64(arr):
            numba.parfors.parfor.init_prange()
            orvi__tsmv = numba.cpython.builtins.get_type_min_value(np.int64)
            pfhg__coyl = 0
            for pwrt__nxxuo in numba.parfors.parfor.internal_prange(len(arr)):
                knzv__hlbxs = orvi__tsmv
                yjdcq__yhq = 0
                if not bodo.libs.array_kernels.isna(arr, pwrt__nxxuo):
                    knzv__hlbxs = (bodo.hiframes.pd_timestamp_ext.
                        dt64_to_integer(arr[pwrt__nxxuo]))
                    yjdcq__yhq = 1
                orvi__tsmv = max(orvi__tsmv, knzv__hlbxs)
                pfhg__coyl += yjdcq__yhq
            return bodo.hiframes.pd_index_ext._dti_val_finalize(orvi__tsmv,
                pfhg__coyl)
        return impl_dt64
    if isinstance(arr, CategoricalArrayType):

        def impl_cat(arr):
            tmdt__oqasl = (bodo.hiframes.pd_categorical_ext.
                get_categorical_arr_codes(arr))
            numba.parfors.parfor.init_prange()
            orvi__tsmv = -1
            for pwrt__nxxuo in numba.parfors.parfor.internal_prange(len(
                tmdt__oqasl)):
                orvi__tsmv = max(orvi__tsmv, tmdt__oqasl[pwrt__nxxuo])
            gvo__igaa = bodo.hiframes.series_kernels._box_cat_val(orvi__tsmv,
                arr.dtype, 1)
            return gvo__igaa
        return impl_cat
    if arr == datetime_date_array_type:

        def impl_date(arr):
            numba.parfors.parfor.init_prange()
            orvi__tsmv = bodo.hiframes.series_kernels._get_date_min_value()
            pfhg__coyl = 0
            for pwrt__nxxuo in numba.parfors.parfor.internal_prange(len(arr)):
                knzv__hlbxs = orvi__tsmv
                yjdcq__yhq = 0
                if not bodo.libs.array_kernels.isna(arr, pwrt__nxxuo):
                    knzv__hlbxs = arr[pwrt__nxxuo]
                    yjdcq__yhq = 1
                orvi__tsmv = max(orvi__tsmv, knzv__hlbxs)
                pfhg__coyl += yjdcq__yhq
            gvo__igaa = bodo.hiframes.series_kernels._sum_handle_nan(orvi__tsmv
                , pfhg__coyl)
            return gvo__igaa
        return impl_date

    def impl(arr):
        numba.parfors.parfor.init_prange()
        orvi__tsmv = bodo.hiframes.series_kernels._get_type_min_value(arr.dtype
            )
        pfhg__coyl = 0
        for pwrt__nxxuo in numba.parfors.parfor.internal_prange(len(arr)):
            knzv__hlbxs = orvi__tsmv
            yjdcq__yhq = 0
            if not bodo.libs.array_kernels.isna(arr, pwrt__nxxuo):
                knzv__hlbxs = arr[pwrt__nxxuo]
                yjdcq__yhq = 1
            orvi__tsmv = max(orvi__tsmv, knzv__hlbxs)
            pfhg__coyl += yjdcq__yhq
        gvo__igaa = bodo.hiframes.series_kernels._sum_handle_nan(orvi__tsmv,
            pfhg__coyl)
        return gvo__igaa
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
    sgeof__dcsnh = types.float64
    uth__ycia = types.float64
    if isinstance(arr, types.Array) and arr.dtype == types.float32:
        sgeof__dcsnh = types.float32
        uth__ycia = types.float32
    zwc__puzs = sgeof__dcsnh(0)
    qdxwa__ugk = uth__ycia(0)
    kjm__shb = uth__ycia(1)

    def impl(arr):
        numba.parfors.parfor.init_prange()
        orvi__tsmv = zwc__puzs
        pfhg__coyl = qdxwa__ugk
        for pwrt__nxxuo in numba.parfors.parfor.internal_prange(len(arr)):
            knzv__hlbxs = zwc__puzs
            yjdcq__yhq = qdxwa__ugk
            if not bodo.libs.array_kernels.isna(arr, pwrt__nxxuo):
                knzv__hlbxs = arr[pwrt__nxxuo]
                yjdcq__yhq = kjm__shb
            orvi__tsmv += knzv__hlbxs
            pfhg__coyl += yjdcq__yhq
        gvo__igaa = bodo.hiframes.series_kernels._mean_handle_nan(orvi__tsmv,
            pfhg__coyl)
        return gvo__igaa
    return impl


def array_op_var(arr, skipna, ddof):
    pass


@overload(array_op_var)
def overload_array_op_var(arr, skipna, ddof):

    def impl(arr, skipna, ddof):
        numba.parfors.parfor.init_prange()
        qvpag__rfo = 0.0
        uysq__xxm = 0.0
        pfhg__coyl = 0
        for pwrt__nxxuo in numba.parfors.parfor.internal_prange(len(arr)):
            knzv__hlbxs = 0.0
            yjdcq__yhq = 0
            if not bodo.libs.array_kernels.isna(arr, pwrt__nxxuo
                ) or not skipna:
                knzv__hlbxs = arr[pwrt__nxxuo]
                yjdcq__yhq = 1
            qvpag__rfo += knzv__hlbxs
            uysq__xxm += knzv__hlbxs * knzv__hlbxs
            pfhg__coyl += yjdcq__yhq
        gvo__igaa = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            qvpag__rfo, uysq__xxm, pfhg__coyl, ddof)
        return gvo__igaa
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
                xtp__dbst = np.empty(len(q), np.int64)
                for pwrt__nxxuo in range(len(q)):
                    mrhy__lcsww = np.float64(q[pwrt__nxxuo])
                    xtp__dbst[pwrt__nxxuo] = bodo.libs.array_kernels.quantile(
                        arr.view(np.int64), mrhy__lcsww)
                return xtp__dbst.view(np.dtype('datetime64[ns]'))
            return _impl_list_dt

        def impl_list(arr, q):
            xtp__dbst = np.empty(len(q), np.float64)
            for pwrt__nxxuo in range(len(q)):
                mrhy__lcsww = np.float64(q[pwrt__nxxuo])
                xtp__dbst[pwrt__nxxuo] = bodo.libs.array_kernels.quantile(arr,
                    mrhy__lcsww)
            return xtp__dbst
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
        guzsp__pbbz = types.intp
    elif arr.dtype == types.bool_:
        guzsp__pbbz = np.int64
    else:
        guzsp__pbbz = arr.dtype
    zuv__mir = guzsp__pbbz(0)
    if isinstance(arr.dtype, types.Float) and (not is_overload_true(skipna) or
        not is_overload_zero(min_count)):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            orvi__tsmv = zuv__mir
            pgstq__nbm = len(arr)
            pfhg__coyl = 0
            for pwrt__nxxuo in numba.parfors.parfor.internal_prange(pgstq__nbm
                ):
                knzv__hlbxs = zuv__mir
                yjdcq__yhq = 0
                if not bodo.libs.array_kernels.isna(arr, pwrt__nxxuo
                    ) or not skipna:
                    knzv__hlbxs = arr[pwrt__nxxuo]
                    yjdcq__yhq = 1
                orvi__tsmv += knzv__hlbxs
                pfhg__coyl += yjdcq__yhq
            gvo__igaa = bodo.hiframes.series_kernels._var_handle_mincount(
                orvi__tsmv, pfhg__coyl, min_count)
            return gvo__igaa
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            orvi__tsmv = zuv__mir
            pgstq__nbm = len(arr)
            for pwrt__nxxuo in numba.parfors.parfor.internal_prange(pgstq__nbm
                ):
                knzv__hlbxs = zuv__mir
                if not bodo.libs.array_kernels.isna(arr, pwrt__nxxuo):
                    knzv__hlbxs = arr[pwrt__nxxuo]
                orvi__tsmv += knzv__hlbxs
            return orvi__tsmv
    return impl


def array_op_prod(arr, skipna, min_count):
    pass


@overload(array_op_prod)
def overload_array_op_prod(arr, skipna, min_count):
    otrre__shz = arr.dtype(1)
    if arr.dtype == types.bool_:
        otrre__shz = 1
    if isinstance(arr.dtype, types.Float):

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            orvi__tsmv = otrre__shz
            pfhg__coyl = 0
            for pwrt__nxxuo in numba.parfors.parfor.internal_prange(len(arr)):
                knzv__hlbxs = otrre__shz
                yjdcq__yhq = 0
                if not bodo.libs.array_kernels.isna(arr, pwrt__nxxuo
                    ) or not skipna:
                    knzv__hlbxs = arr[pwrt__nxxuo]
                    yjdcq__yhq = 1
                pfhg__coyl += yjdcq__yhq
                orvi__tsmv *= knzv__hlbxs
            gvo__igaa = bodo.hiframes.series_kernels._var_handle_mincount(
                orvi__tsmv, pfhg__coyl, min_count)
            return gvo__igaa
    else:

        def impl(arr, skipna, min_count):
            numba.parfors.parfor.init_prange()
            orvi__tsmv = otrre__shz
            for pwrt__nxxuo in numba.parfors.parfor.internal_prange(len(arr)):
                knzv__hlbxs = otrre__shz
                if not bodo.libs.array_kernels.isna(arr, pwrt__nxxuo):
                    knzv__hlbxs = arr[pwrt__nxxuo]
                orvi__tsmv *= knzv__hlbxs
            return orvi__tsmv
    return impl


def array_op_idxmax(arr, index):
    pass


@overload(array_op_idxmax, inline='always')
def overload_array_op_idxmax(arr, index):

    def impl(arr, index):
        pwrt__nxxuo = bodo.libs.array_kernels._nan_argmax(arr)
        return index[pwrt__nxxuo]
    return impl


def array_op_idxmin(arr, index):
    pass


@overload(array_op_idxmin, inline='always')
def overload_array_op_idxmin(arr, index):

    def impl(arr, index):
        pwrt__nxxuo = bodo.libs.array_kernels._nan_argmin(arr)
        return index[pwrt__nxxuo]
    return impl


def _convert_isin_values(values, use_hash_impl):
    pass


@overload(_convert_isin_values, no_unliteral=True)
def overload_convert_isin_values(values, use_hash_impl):
    if is_overload_true(use_hash_impl):

        def impl(values, use_hash_impl):
            gmdap__kix = {}
            for kgdi__qog in values:
                gmdap__kix[bodo.utils.conversion.box_if_dt64(kgdi__qog)] = 0
            return gmdap__kix
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
        pgstq__nbm = len(arr)
        xtp__dbst = np.empty(pgstq__nbm, np.bool_)
        for pwrt__nxxuo in numba.parfors.parfor.internal_prange(pgstq__nbm):
            xtp__dbst[pwrt__nxxuo] = bodo.utils.conversion.box_if_dt64(arr[
                pwrt__nxxuo]) in values
        return xtp__dbst
    return impl


@generated_jit(nopython=True)
def array_unique_vector_map(in_arr_tup):
    ayov__beztm = len(in_arr_tup) != 1
    nkr__yvjn = list(in_arr_tup.types)
    rnas__oohx = 'def impl(in_arr_tup):\n'
    rnas__oohx += '  n = len(in_arr_tup[0])\n'
    if ayov__beztm:
        sppsh__jwulh = ', '.join([f'in_arr_tup[{pwrt__nxxuo}][unused]' for
            pwrt__nxxuo in range(len(in_arr_tup))])
        bqu__ngp = ', '.join(['False' for pqtwr__vbwtl in range(len(
            in_arr_tup))])
        rnas__oohx += f"""  arr_map = {{bodo.libs.nullable_tuple_ext.build_nullable_tuple(({sppsh__jwulh},), ({bqu__ngp},)): 0 for unused in range(0)}}
"""
        rnas__oohx += '  map_vector = np.empty(n, np.int64)\n'
        for pwrt__nxxuo, mvo__nqzbj in enumerate(nkr__yvjn):
            rnas__oohx += f'  in_lst_{pwrt__nxxuo} = []\n'
            if mvo__nqzbj == bodo.string_array_type:
                rnas__oohx += f'  total_len_{pwrt__nxxuo} = 0\n'
            rnas__oohx += f'  null_in_lst_{pwrt__nxxuo} = []\n'
        rnas__oohx += '  for i in range(n):\n'
        xmri__swotp = ', '.join([f'in_arr_tup[{pwrt__nxxuo}][i]' for
            pwrt__nxxuo in range(len(nkr__yvjn))])
        qafga__yiyt = ', '.join([
            f'bodo.libs.array_kernels.isna(in_arr_tup[{pwrt__nxxuo}], i)' for
            pwrt__nxxuo in range(len(nkr__yvjn))])
        rnas__oohx += f"""    data_val = bodo.libs.nullable_tuple_ext.build_nullable_tuple(({xmri__swotp},), ({qafga__yiyt},))
"""
        rnas__oohx += '    if data_val not in arr_map:\n'
        rnas__oohx += '      set_val = len(arr_map)\n'
        rnas__oohx += '      values_tup = data_val._data\n'
        rnas__oohx += '      nulls_tup = data_val._null_values\n'
        for pwrt__nxxuo, mvo__nqzbj in enumerate(nkr__yvjn):
            rnas__oohx += (
                f'      in_lst_{pwrt__nxxuo}.append(values_tup[{pwrt__nxxuo}])\n'
                )
            rnas__oohx += (
                f'      null_in_lst_{pwrt__nxxuo}.append(nulls_tup[{pwrt__nxxuo}])\n'
                )
            if mvo__nqzbj == bodo.string_array_type:
                rnas__oohx += f"""      total_len_{pwrt__nxxuo}  += nulls_tup[{pwrt__nxxuo}] * len(values_tup[{pwrt__nxxuo}])
"""
        rnas__oohx += '      arr_map[data_val] = len(arr_map)\n'
        rnas__oohx += '    else:\n'
        rnas__oohx += '      set_val = arr_map[data_val]\n'
        rnas__oohx += '    map_vector[i] = set_val\n'
        rnas__oohx += '  n_rows = len(arr_map)\n'
        for pwrt__nxxuo, mvo__nqzbj in enumerate(nkr__yvjn):
            if mvo__nqzbj == bodo.string_array_type:
                rnas__oohx += f"""  out_arr_{pwrt__nxxuo} = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len_{pwrt__nxxuo})
"""
            else:
                rnas__oohx += f"""  out_arr_{pwrt__nxxuo} = bodo.utils.utils.alloc_type(n_rows, in_arr_tup[{pwrt__nxxuo}], (-1,))
"""
        rnas__oohx += '  for j in range(len(arr_map)):\n'
        for pwrt__nxxuo in range(len(nkr__yvjn)):
            rnas__oohx += f'    if null_in_lst_{pwrt__nxxuo}[j]:\n'
            rnas__oohx += (
                f'      bodo.libs.array_kernels.setna(out_arr_{pwrt__nxxuo}, j)\n'
                )
            rnas__oohx += '    else:\n'
            rnas__oohx += (
                f'      out_arr_{pwrt__nxxuo}[j] = in_lst_{pwrt__nxxuo}[j]\n')
        ziuxe__uht = ', '.join([f'out_arr_{pwrt__nxxuo}' for pwrt__nxxuo in
            range(len(nkr__yvjn))])
        rnas__oohx += f'  return ({ziuxe__uht},), map_vector\n'
    else:
        rnas__oohx += '  in_arr = in_arr_tup[0]\n'
        rnas__oohx += (
            f'  arr_map = {{in_arr[unused]: 0 for unused in range(0)}}\n')
        rnas__oohx += '  map_vector = np.empty(n, np.int64)\n'
        rnas__oohx += '  is_na = 0\n'
        rnas__oohx += '  in_lst = []\n'
        if nkr__yvjn[0] == bodo.string_array_type:
            rnas__oohx += '  total_len = 0\n'
        rnas__oohx += '  for i in range(n):\n'
        rnas__oohx += '    if bodo.libs.array_kernels.isna(in_arr, i):\n'
        rnas__oohx += '      is_na = 1\n'
        rnas__oohx += (
            '      # Always put NA in the last location. We can safely use\n')
        rnas__oohx += (
            '      # -1 because in_arr[-1] == in_arr[len(in_arr) - 1]\n')
        rnas__oohx += '      set_val = -1\n'
        rnas__oohx += '    else:\n'
        rnas__oohx += '      data_val = in_arr[i]\n'
        rnas__oohx += '      if data_val not in arr_map:\n'
        rnas__oohx += '        set_val = len(arr_map)\n'
        rnas__oohx += '        in_lst.append(data_val)\n'
        if nkr__yvjn[0] == bodo.string_array_type:
            rnas__oohx += '        total_len += len(data_val)\n'
        rnas__oohx += '        arr_map[data_val] = len(arr_map)\n'
        rnas__oohx += '      else:\n'
        rnas__oohx += '        set_val = arr_map[data_val]\n'
        rnas__oohx += '    map_vector[i] = set_val\n'
        rnas__oohx += '  n_rows = len(arr_map) + is_na\n'
        if nkr__yvjn[0] == bodo.string_array_type:
            rnas__oohx += """  out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(n_rows, total_len)
"""
        else:
            rnas__oohx += (
                '  out_arr = bodo.utils.utils.alloc_type(n_rows, in_arr, (-1,))\n'
                )
        rnas__oohx += '  for j in range(len(arr_map)):\n'
        rnas__oohx += '    out_arr[j] = in_lst[j]\n'
        rnas__oohx += '  if is_na:\n'
        rnas__oohx += (
            '    bodo.libs.array_kernels.setna(out_arr, n_rows - 1)\n')
        rnas__oohx += f'  return (out_arr,), map_vector\n'
    vboi__ldd = {}
    exec(rnas__oohx, {'bodo': bodo, 'np': np}, vboi__ldd)
    impl = vboi__ldd['impl']
    return impl
