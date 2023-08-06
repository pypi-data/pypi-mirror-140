"""
Implementation of Series attributes and methods using overload.
"""
import operator
import numba
import numpy as np
import pandas as pd
from numba.core import types
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import lower_builtin, overload, overload_attribute, overload_method, register_jitable
import bodo
from bodo.hiframes.datetime_datetime_ext import datetime_datetime_type
from bodo.hiframes.datetime_timedelta_ext import PDTimeDeltaType, datetime_timedelta_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.pd_offsets_ext import is_offsets_type
from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType, if_series_to_array_type, is_series_type
from bodo.hiframes.pd_timestamp_ext import PandasTimestampType, pd_timestamp_type
from bodo.hiframes.rolling import is_supported_shift_array_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import BinaryArrayType, binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array
from bodo.libs.decimal_arr_ext import Decimal128Type, DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, string_array_type
from bodo.libs.str_ext import string_type
from bodo.utils.transform import gen_const_tup, is_var_size_item_array_type
from bodo.utils.typing import BodoError, can_replace, check_unsupported_args, dtype_to_array_type, element_type, get_common_scalar_dtype, get_literal_value, get_overload_const_bytes, get_overload_const_int, get_overload_const_str, is_common_scalar_dtype, is_iterable_type, is_literal_type, is_nullable_type, is_overload_bool, is_overload_constant_bool, is_overload_constant_bytes, is_overload_constant_int, is_overload_constant_nan, is_overload_constant_str, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_overload_zero, is_scalar_type, raise_bodo_error, to_nullable_type


@overload_attribute(HeterogeneousSeriesType, 'index', inline='always')
@overload_attribute(SeriesType, 'index', inline='always')
def overload_series_index(s):
    return lambda s: bodo.hiframes.pd_series_ext.get_series_index(s)


@overload_attribute(HeterogeneousSeriesType, 'values', inline='always')
@overload_attribute(SeriesType, 'values', inline='always')
def overload_series_values(s):
    return lambda s: bodo.hiframes.pd_series_ext.get_series_data(s)


@overload_attribute(SeriesType, 'dtype', inline='always')
def overload_series_dtype(s):
    if s.dtype == bodo.string_type:
        raise BodoError('Series.dtype not supported for string Series yet')
    return lambda s: bodo.hiframes.pd_series_ext.get_series_data(s).dtype


@overload_attribute(HeterogeneousSeriesType, 'shape')
@overload_attribute(SeriesType, 'shape')
def overload_series_shape(s):
    return lambda s: (len(bodo.hiframes.pd_series_ext.get_series_data(s)),)


@overload_attribute(HeterogeneousSeriesType, 'ndim', inline='always')
@overload_attribute(SeriesType, 'ndim', inline='always')
def overload_series_ndim(s):
    return lambda s: 1


@overload_attribute(HeterogeneousSeriesType, 'size')
@overload_attribute(SeriesType, 'size')
def overload_series_size(s):
    return lambda s: len(bodo.hiframes.pd_series_ext.get_series_data(s))


@overload_attribute(HeterogeneousSeriesType, 'T', inline='always')
@overload_attribute(SeriesType, 'T', inline='always')
def overload_series_T(s):
    return lambda s: s


@overload_attribute(SeriesType, 'hasnans', inline='always')
def overload_series_hasnans(s):
    return lambda s: s.isna().sum() != 0


@overload_attribute(HeterogeneousSeriesType, 'empty')
@overload_attribute(SeriesType, 'empty')
def overload_series_empty(s):
    return lambda s: len(bodo.hiframes.pd_series_ext.get_series_data(s)) == 0


@overload_attribute(SeriesType, 'dtypes', inline='always')
def overload_series_dtypes(s):
    return lambda s: s.dtype


@overload_attribute(HeterogeneousSeriesType, 'name', inline='always')
@overload_attribute(SeriesType, 'name', inline='always')
def overload_series_name(s):
    return lambda s: bodo.hiframes.pd_series_ext.get_series_name(s)


@overload(len, no_unliteral=True)
def overload_series_len(S):
    if isinstance(S, (SeriesType, HeterogeneousSeriesType)):
        return lambda S: len(bodo.hiframes.pd_series_ext.get_series_data(S))


@overload_method(SeriesType, 'copy', inline='always', no_unliteral=True)
def overload_series_copy(S, deep=True):
    if is_overload_true(deep):

        def impl1(S, deep=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr.copy(),
                index, name)
        return impl1
    if is_overload_false(deep):

        def impl2(S, deep=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
        return impl2

    def impl(S, deep=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        if deep:
            arr = arr.copy()
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
    return impl


@overload_method(SeriesType, 'to_list', no_unliteral=True)
@overload_method(SeriesType, 'tolist', no_unliteral=True)
def overload_series_to_list(S):
    if isinstance(S.dtype, types.Float):

        def impl_float(S):
            ycehi__sueou = list()
            for hhbvt__hyqt in range(len(S)):
                ycehi__sueou.append(S.iat[hhbvt__hyqt])
            return ycehi__sueou
        return impl_float

    def impl(S):
        ycehi__sueou = list()
        for hhbvt__hyqt in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, hhbvt__hyqt):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            ycehi__sueou.append(S.iat[hhbvt__hyqt])
        return ycehi__sueou
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    nlmgr__mfol = dict(dtype=dtype, copy=copy, na_value=na_value)
    keda__kbt = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    nlmgr__mfol = dict(name=name, inplace=inplace)
    keda__kbt = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not bodo.hiframes.dataframe_impl._is_all_levels(S, level):
        raise_bodo_error(
            'Series.reset_index(): only dropping all index levels supported')
    if not is_overload_constant_bool(drop):
        raise_bodo_error(
            "Series.reset_index(): 'drop' parameter should be a constant boolean value"
            )
    if is_overload_true(drop):

        def impl_drop(S, level=None, drop=False, name=None, inplace=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_index_ext.init_range_index(0, len(arr),
                1, None)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
        return impl_drop

    def get_name_literal(name_typ, is_index=False, series_name=None):
        if is_overload_none(name_typ):
            if is_index:
                return 'index' if series_name != 'index' else 'level_0'
            return 0
        if is_literal_type(name_typ):
            return get_literal_value(name_typ)
        else:
            raise BodoError(
                'Series.reset_index() not supported for non-literal series names'
                )
    series_name = get_name_literal(S.name_typ)
    yue__rxpu = get_name_literal(S.index.name_typ, True, series_name)
    columns = [yue__rxpu, series_name]
    zfqqw__pyfn = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    zfqqw__pyfn += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    zfqqw__pyfn += """    index = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S))
"""
    zfqqw__pyfn += """    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)
"""
    zfqqw__pyfn += '    col_var = {}\n'.format(gen_const_tup(columns))
    zfqqw__pyfn += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe((index, arr), df_index, col_var)
"""
    kfbzh__raf = {}
    exec(zfqqw__pyfn, {'bodo': bodo}, kfbzh__raf)
    dvv__kyeby = kfbzh__raf['_impl']
    return dvv__kyeby


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nqg__czir = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index, name)
    return impl


@overload_method(SeriesType, 'round', inline='always', no_unliteral=True)
def overload_series_round(S, decimals=0):

    def impl(S, decimals=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(arr)
        nqg__czir = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for hhbvt__hyqt in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[hhbvt__hyqt]):
                bodo.libs.array_kernels.setna(nqg__czir, hhbvt__hyqt)
            else:
                nqg__czir[hhbvt__hyqt] = np.round(arr[hhbvt__hyqt], decimals)
        return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index, name)
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    nlmgr__mfol = dict(level=level, numeric_only=numeric_only)
    keda__kbt = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.sum(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.sum(): skipna argument must be a boolean')
    if not is_overload_int(min_count):
        raise BodoError('Series.sum(): min_count argument must be an integer')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None,
        min_count=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_sum(arr, skipna, min_count)
    return impl


@overload_method(SeriesType, 'prod', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'product', inline='always', no_unliteral=True)
def overload_series_prod(S, axis=None, skipna=True, level=None,
    numeric_only=None, min_count=0):
    nlmgr__mfol = dict(level=level, numeric_only=numeric_only)
    keda__kbt = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.product(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.product(): skipna argument must be a boolean')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None,
        min_count=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_prod(arr, skipna, min_count)
    return impl


@overload_method(SeriesType, 'any', inline='always', no_unliteral=True)
def overload_series_any(S, axis=0, bool_only=None, skipna=True, level=None):
    nlmgr__mfol = dict(axis=axis, bool_only=bool_only, skipna=skipna, level
        =level)
    keda__kbt = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        kccpj__hhlgg = 0
        for hhbvt__hyqt in numba.parfors.parfor.internal_prange(len(A)):
            zrv__finos = 0
            if not bodo.libs.array_kernels.isna(A, hhbvt__hyqt):
                zrv__finos = int(A[hhbvt__hyqt])
            kccpj__hhlgg += zrv__finos
        return kccpj__hhlgg != 0
    return impl


@overload_method(SeriesType, 'equals', inline='always', no_unliteral=True)
def overload_series_equals(S, other):
    if not isinstance(other, SeriesType):
        raise BodoError("Series.equals() 'other' must be a Series")
    if isinstance(S.data, bodo.ArrayItemArrayType):
        raise BodoError(
            'Series.equals() not supported for Series where each element is an array or list'
            )
    if S.data != other.data:
        return lambda S, other: False

    def impl(S, other):
        wudi__lme = bodo.hiframes.pd_series_ext.get_series_data(S)
        kxvc__sus = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        kccpj__hhlgg = 0
        for hhbvt__hyqt in numba.parfors.parfor.internal_prange(len(wudi__lme)
            ):
            zrv__finos = 0
            yvfcx__zxf = bodo.libs.array_kernels.isna(wudi__lme, hhbvt__hyqt)
            fhijq__zcst = bodo.libs.array_kernels.isna(kxvc__sus, hhbvt__hyqt)
            if (yvfcx__zxf and not fhijq__zcst or not yvfcx__zxf and
                fhijq__zcst):
                zrv__finos = 1
            elif not yvfcx__zxf:
                if wudi__lme[hhbvt__hyqt] != kxvc__sus[hhbvt__hyqt]:
                    zrv__finos = 1
            kccpj__hhlgg += zrv__finos
        return kccpj__hhlgg == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    nlmgr__mfol = dict(axis=axis, bool_only=bool_only, skipna=skipna, level
        =level)
    keda__kbt = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        kccpj__hhlgg = 0
        for hhbvt__hyqt in numba.parfors.parfor.internal_prange(len(A)):
            zrv__finos = 0
            if not bodo.libs.array_kernels.isna(A, hhbvt__hyqt):
                zrv__finos = int(not A[hhbvt__hyqt])
            kccpj__hhlgg += zrv__finos
        return kccpj__hhlgg == 0
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    nlmgr__mfol = dict(level=level)
    keda__kbt = dict(level=None)
    check_unsupported_args('Series.mad', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    ljrno__iqdw = types.float64
    bfgyi__lmt = types.float64
    if S.dtype == types.float32:
        ljrno__iqdw = types.float32
        bfgyi__lmt = types.float32
    sibpb__btc = ljrno__iqdw(0)
    sgvtr__gxpbv = bfgyi__lmt(0)
    knsau__xstdx = bfgyi__lmt(1)

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        bcam__syjrp = sibpb__btc
        kccpj__hhlgg = sgvtr__gxpbv
        for hhbvt__hyqt in numba.parfors.parfor.internal_prange(len(A)):
            zrv__finos = sibpb__btc
            vfw__fzug = sgvtr__gxpbv
            if not bodo.libs.array_kernels.isna(A, hhbvt__hyqt) or not skipna:
                zrv__finos = A[hhbvt__hyqt]
                vfw__fzug = knsau__xstdx
            bcam__syjrp += zrv__finos
            kccpj__hhlgg += vfw__fzug
        hxs__gqxv = bodo.hiframes.series_kernels._mean_handle_nan(bcam__syjrp,
            kccpj__hhlgg)
        jwtnj__xfql = sibpb__btc
        for hhbvt__hyqt in numba.parfors.parfor.internal_prange(len(A)):
            zrv__finos = sibpb__btc
            if not bodo.libs.array_kernels.isna(A, hhbvt__hyqt) or not skipna:
                zrv__finos = abs(A[hhbvt__hyqt] - hxs__gqxv)
            jwtnj__xfql += zrv__finos
        mjdhm__fbypu = bodo.hiframes.series_kernels._mean_handle_nan(
            jwtnj__xfql, kccpj__hhlgg)
        return mjdhm__fbypu
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    nlmgr__mfol = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    keda__kbt = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mean(): axis argument not supported')

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_mean(arr)
    return impl


@overload_method(SeriesType, 'sem', inline='always', no_unliteral=True)
def overload_series_sem(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    nlmgr__mfol = dict(level=level, numeric_only=numeric_only)
    keda__kbt = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.sem(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.sem(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.sem(): ddof argument must be an integer')

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        mtvrc__lxsbn = 0
        mux__jro = 0
        kccpj__hhlgg = 0
        for hhbvt__hyqt in numba.parfors.parfor.internal_prange(len(A)):
            zrv__finos = 0
            vfw__fzug = 0
            if not bodo.libs.array_kernels.isna(A, hhbvt__hyqt) or not skipna:
                zrv__finos = A[hhbvt__hyqt]
                vfw__fzug = 1
            mtvrc__lxsbn += zrv__finos
            mux__jro += zrv__finos * zrv__finos
            kccpj__hhlgg += vfw__fzug
        diso__wsws = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            mtvrc__lxsbn, mux__jro, kccpj__hhlgg, ddof)
        ykkl__soz = bodo.hiframes.series_kernels._sem_handle_nan(diso__wsws,
            kccpj__hhlgg)
        return ykkl__soz
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    nlmgr__mfol = dict(level=level, numeric_only=numeric_only)
    keda__kbt = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.kurtosis(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError(
            "Series.kurtosis(): 'skipna' argument must be a boolean")

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        mtvrc__lxsbn = 0.0
        mux__jro = 0.0
        tfswz__yfw = 0.0
        zwgu__ole = 0.0
        kccpj__hhlgg = 0
        for hhbvt__hyqt in numba.parfors.parfor.internal_prange(len(A)):
            zrv__finos = 0.0
            vfw__fzug = 0
            if not bodo.libs.array_kernels.isna(A, hhbvt__hyqt) or not skipna:
                zrv__finos = np.float64(A[hhbvt__hyqt])
                vfw__fzug = 1
            mtvrc__lxsbn += zrv__finos
            mux__jro += zrv__finos ** 2
            tfswz__yfw += zrv__finos ** 3
            zwgu__ole += zrv__finos ** 4
            kccpj__hhlgg += vfw__fzug
        diso__wsws = bodo.hiframes.series_kernels.compute_kurt(mtvrc__lxsbn,
            mux__jro, tfswz__yfw, zwgu__ole, kccpj__hhlgg)
        return diso__wsws
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    nlmgr__mfol = dict(level=level, numeric_only=numeric_only)
    keda__kbt = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.skew(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.skew(): skipna argument must be a boolean')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        mtvrc__lxsbn = 0.0
        mux__jro = 0.0
        tfswz__yfw = 0.0
        kccpj__hhlgg = 0
        for hhbvt__hyqt in numba.parfors.parfor.internal_prange(len(A)):
            zrv__finos = 0.0
            vfw__fzug = 0
            if not bodo.libs.array_kernels.isna(A, hhbvt__hyqt) or not skipna:
                zrv__finos = np.float64(A[hhbvt__hyqt])
                vfw__fzug = 1
            mtvrc__lxsbn += zrv__finos
            mux__jro += zrv__finos ** 2
            tfswz__yfw += zrv__finos ** 3
            kccpj__hhlgg += vfw__fzug
        diso__wsws = bodo.hiframes.series_kernels.compute_skew(mtvrc__lxsbn,
            mux__jro, tfswz__yfw, kccpj__hhlgg)
        return diso__wsws
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    nlmgr__mfol = dict(level=level, numeric_only=numeric_only)
    keda__kbt = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.var(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.var(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.var(): ddof argument must be an integer')

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_var(arr, skipna, ddof)
    return impl


@overload_method(SeriesType, 'std', inline='always', no_unliteral=True)
def overload_series_std(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    nlmgr__mfol = dict(level=level, numeric_only=numeric_only)
    keda__kbt = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.std(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.std(): skipna argument must be a boolean')
    if not is_overload_int(ddof):
        raise BodoError('Series.std(): ddof argument must be an integer')

    def impl(S, axis=None, skipna=True, level=None, ddof=1, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_std(arr, skipna, ddof)
    return impl


@overload_method(SeriesType, 'dot', inline='always', no_unliteral=True)
def overload_series_dot(S, other):

    def impl(S, other):
        wudi__lme = bodo.hiframes.pd_series_ext.get_series_data(S)
        kxvc__sus = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        eksrh__uieq = 0
        for hhbvt__hyqt in numba.parfors.parfor.internal_prange(len(wudi__lme)
            ):
            zumms__xsf = wudi__lme[hhbvt__hyqt]
            zqmwk__tbuwa = kxvc__sus[hhbvt__hyqt]
            eksrh__uieq += zumms__xsf * zqmwk__tbuwa
        return eksrh__uieq
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    nlmgr__mfol = dict(skipna=skipna)
    keda__kbt = dict(skipna=True)
    check_unsupported_args('Series.cumsum', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cumsum(): axis argument not supported')

    def impl(S, axis=None, skipna=True):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(A.cumsum(), index, name)
    return impl


@overload_method(SeriesType, 'cumprod', inline='always', no_unliteral=True)
def overload_series_cumprod(S, axis=None, skipna=True):
    nlmgr__mfol = dict(skipna=skipna)
    keda__kbt = dict(skipna=True)
    check_unsupported_args('Series.cumprod', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cumprod(): axis argument not supported')

    def impl(S, axis=None, skipna=True):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(A.cumprod(), index, name
            )
    return impl


@overload_method(SeriesType, 'cummin', inline='always', no_unliteral=True)
def overload_series_cummin(S, axis=None, skipna=True):
    nlmgr__mfol = dict(skipna=skipna)
    keda__kbt = dict(skipna=True)
    check_unsupported_args('Series.cummin', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cummin(): axis argument not supported')

    def impl(S, axis=None, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
            array_kernels.cummin(arr), index, name)
    return impl


@overload_method(SeriesType, 'cummax', inline='always', no_unliteral=True)
def overload_series_cummax(S, axis=None, skipna=True):
    nlmgr__mfol = dict(skipna=skipna)
    keda__kbt = dict(skipna=True)
    check_unsupported_args('Series.cummax', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.cummax(): axis argument not supported')

    def impl(S, axis=None, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
            array_kernels.cummax(arr), index, name)
    return impl


@overload_method(SeriesType, 'rename', inline='always', no_unliteral=True)
def overload_series_rename(S, index=None, axis=None, copy=True, inplace=
    False, level=None, errors='ignore'):
    if not (index == bodo.string_type or isinstance(index, types.StringLiteral)
        ):
        raise BodoError("Series.rename() 'index' can only be a string")
    nlmgr__mfol = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    keda__kbt = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        admzt__jqr = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, admzt__jqr, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    nlmgr__mfol = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    keda__kbt = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if is_overload_none(mapper) or not is_scalar_type(mapper):
        raise BodoError(
            "Series.rename_axis(): 'mapper' is required and must be a scalar type."
            )

    def impl(S, mapper=None, index=None, columns=None, axis=None, copy=True,
        inplace=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        index = index.rename(mapper)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr, index, name)
    return impl


@overload_method(SeriesType, 'abs', inline='always', no_unliteral=True)
def overload_series_abs(S):

    def impl(S):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(np.abs(A), index, name)
    return impl


@overload_method(SeriesType, 'count', no_unliteral=True)
def overload_series_count(S, level=None):
    nlmgr__mfol = dict(level=level)
    keda__kbt = dict(level=None)
    check_unsupported_args('Series.count', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    nlmgr__mfol = dict(method=method, min_periods=min_periods)
    keda__kbt = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        xwex__dew = S.sum()
        ynjpf__whd = other.sum()
        a = n * (S * other).sum() - xwex__dew * ynjpf__whd
        vgshv__jus = n * (S ** 2).sum() - xwex__dew ** 2
        oxcw__rgpv = n * (other ** 2).sum() - ynjpf__whd ** 2
        return a / np.sqrt(vgshv__jus * oxcw__rgpv)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    nlmgr__mfol = dict(min_periods=min_periods)
    keda__kbt = dict(min_periods=None)
    check_unsupported_args('Series.cov', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')

    def impl(S, other, min_periods=None, ddof=1):
        xwex__dew = S.mean()
        ynjpf__whd = other.mean()
        pzvz__znqm = ((S - xwex__dew) * (other - ynjpf__whd)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(pzvz__znqm, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            khd__kwxfa = np.sign(sum_val)
            return np.inf * khd__kwxfa
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    nlmgr__mfol = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    keda__kbt = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.min(): axis argument not supported')
    if isinstance(S.dtype, PDCategoricalDtype):
        if not S.dtype.ordered:
            raise BodoError(
                'Series.min(): only ordered categoricals are possible')

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_min(arr)
    return impl


@overload(max, no_unliteral=True)
def overload_series_builtins_max(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.max()
        return impl


@overload(min, no_unliteral=True)
def overload_series_builtins_min(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.min()
        return impl


@overload(sum, no_unliteral=True)
def overload_series_builtins_sum(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.sum()
        return impl


@overload(np.prod, inline='always', no_unliteral=True)
def overload_series_np_prod(S):
    if isinstance(S, SeriesType):

        def impl(S):
            return S.prod()
        return impl


@overload_method(SeriesType, 'max', inline='always', no_unliteral=True)
def overload_series_max(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    nlmgr__mfol = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    keda__kbt = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.max(): axis argument not supported')
    if isinstance(S.dtype, PDCategoricalDtype):
        if not S.dtype.ordered:
            raise BodoError(
                'Series.max(): only ordered categoricals are possible')

    def impl(S, axis=None, skipna=None, level=None, numeric_only=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_max(arr)
    return impl


@overload_method(SeriesType, 'idxmin', inline='always', no_unliteral=True)
def overload_series_idxmin(S, axis=0, skipna=True):
    nlmgr__mfol = dict(axis=axis, skipna=skipna)
    keda__kbt = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (S.dtype == types.none or bodo.utils.utils.is_np_array_typ(S.
        data) and (S.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
        isinstance(S.dtype, (types.Number, types.Boolean))) or isinstance(S
        .data, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or S.
        data in [bodo.boolean_array, bodo.datetime_date_array_type]):
        raise BodoError(
            f'Series.idxmin() only supported for numeric array types. Array type: {S.data} not supported.'
            )
    if isinstance(S.data, bodo.CategoricalArrayType) and not S.dtype.ordered:
        raise BodoError(
            'Series.idxmin(): only ordered categoricals are possible')

    def impl(S, axis=0, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.libs.array_ops.array_op_idxmin(arr, index)
    return impl


@overload_method(SeriesType, 'idxmax', inline='always', no_unliteral=True)
def overload_series_idxmax(S, axis=0, skipna=True):
    nlmgr__mfol = dict(axis=axis, skipna=skipna)
    keda__kbt = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (S.dtype == types.none or bodo.utils.utils.is_np_array_typ(S.
        data) and (S.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
        isinstance(S.dtype, (types.Number, types.Boolean))) or isinstance(S
        .data, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or S.
        data in [bodo.boolean_array, bodo.datetime_date_array_type]):
        raise BodoError(
            f'Series.idxmax() only supported for numeric array types. Array type: {S.data} not supported.'
            )
    if isinstance(S.data, bodo.CategoricalArrayType) and not S.dtype.ordered:
        raise BodoError(
            'Series.idxmax(): only ordered categoricals are possible')

    def impl(S, axis=0, skipna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.libs.array_ops.array_op_idxmax(arr, index)
    return impl


@overload_method(SeriesType, 'infer_objects', inline='always')
def overload_series_infer_objects(S):
    return lambda S: S.copy()


@overload_attribute(SeriesType, 'is_monotonic', inline='always')
@overload_attribute(SeriesType, 'is_monotonic_increasing', inline='always')
def overload_series_is_monotonic_increasing(S):
    return lambda S: bodo.libs.array_kernels.series_monotonicity(bodo.
        hiframes.pd_series_ext.get_series_data(S), 1)


@overload_attribute(SeriesType, 'is_monotonic_decreasing', inline='always')
def overload_series_is_monotonic_decreasing(S):
    return lambda S: bodo.libs.array_kernels.series_monotonicity(bodo.
        hiframes.pd_series_ext.get_series_data(S), 2)


@overload_attribute(SeriesType, 'nbytes', inline='always')
def overload_series_nbytes(S):
    return lambda S: bodo.hiframes.pd_series_ext.get_series_data(S).nbytes


@overload_method(SeriesType, 'autocorr', inline='always', no_unliteral=True)
def overload_series_autocorr(S, lag=1):
    return lambda S, lag=1: bodo.libs.array_kernels.autocorr(bodo.hiframes.
        pd_series_ext.get_series_data(S), lag)


@overload_method(SeriesType, 'median', inline='always', no_unliteral=True)
def overload_series_median(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    nlmgr__mfol = dict(level=level, numeric_only=numeric_only)
    keda__kbt = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.median(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.median(): skipna argument must be a boolean')
    return (lambda S, axis=None, skipna=True, level=None, numeric_only=None:
        bodo.libs.array_ops.array_op_median(bodo.hiframes.pd_series_ext.
        get_series_data(S), skipna))


def overload_series_head(S, n=5):

    def impl(S, n=5):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        mfyj__qlrn = arr[:n]
        wfnmt__iaizu = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(mfyj__qlrn,
            wfnmt__iaizu, name)
    return impl


@lower_builtin('series.head', SeriesType, types.Integer)
@lower_builtin('series.head', SeriesType, types.Omitted)
def series_head_lower(context, builder, sig, args):
    impl = overload_series_head(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@numba.extending.register_jitable
def tail_slice(k, n):
    if n == 0:
        return k
    return -n


@overload_method(SeriesType, 'tail', inline='always', no_unliteral=True)
def overload_series_tail(S, n=5):
    if not is_overload_int(n):
        raise BodoError("Series.tail(): 'n' must be an Integer")

    def impl(S, n=5):
        zjdv__wyr = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        mfyj__qlrn = arr[zjdv__wyr:]
        wfnmt__iaizu = index[zjdv__wyr:]
        return bodo.hiframes.pd_series_ext.init_series(mfyj__qlrn,
            wfnmt__iaizu, name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    dvl__cuiw = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in dvl__cuiw:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            cle__snth = index[0]
            jqaa__dda = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset, cle__snth,
                False))
        else:
            jqaa__dda = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        mfyj__qlrn = arr[:jqaa__dda]
        wfnmt__iaizu = index[:jqaa__dda]
        return bodo.hiframes.pd_series_ext.init_series(mfyj__qlrn,
            wfnmt__iaizu, name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    dvl__cuiw = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in dvl__cuiw:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            yzu__kkgs = index[-1]
            jqaa__dda = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset, yzu__kkgs,
                True))
        else:
            jqaa__dda = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        mfyj__qlrn = arr[len(arr) - jqaa__dda:]
        wfnmt__iaizu = index[len(arr) - jqaa__dda:]
        return bodo.hiframes.pd_series_ext.init_series(mfyj__qlrn,
            wfnmt__iaizu, name)
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    nlmgr__mfol = dict(keep=keep)
    keda__kbt = dict(keep='first')
    check_unsupported_args('Series.nlargest', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        clzh__gzq = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nqg__czir, pgu__qzgw = bodo.libs.array_kernels.nlargest(arr,
            clzh__gzq, n, True, bodo.hiframes.series_kernels.gt_f)
        owwu__ykbb = bodo.utils.conversion.convert_to_index(pgu__qzgw)
        return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
            owwu__ykbb, name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    nlmgr__mfol = dict(keep=keep)
    keda__kbt = dict(keep='first')
    check_unsupported_args('Series.nsmallest', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        clzh__gzq = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nqg__czir, pgu__qzgw = bodo.libs.array_kernels.nlargest(arr,
            clzh__gzq, n, False, bodo.hiframes.series_kernels.lt_f)
        owwu__ykbb = bodo.utils.conversion.convert_to_index(pgu__qzgw)
        return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
            owwu__ykbb, name)
    return impl


@overload_method(SeriesType, 'notnull', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'notna', inline='always', no_unliteral=True)
def overload_series_notna(S):
    return lambda S: S.isna() == False


@overload_method(SeriesType, 'astype', inline='always', no_unliteral=True)
def overload_series_astype(S, dtype, copy=True, errors='raise',
    _bodo_nan_to_str=True):
    nlmgr__mfol = dict(errors=errors)
    keda__kbt = dict(errors='raise')
    check_unsupported_args('Series.astype', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "Series.astype(): 'dtype' when passed as string must be a constant value"
            )

    def impl(S, dtype, copy=True, errors='raise', _bodo_nan_to_str=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nqg__czir = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index, name)
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    nlmgr__mfol = dict(axis=axis, is_copy=is_copy)
    keda__kbt = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        xlxz__mej = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[xlxz__mej],
            index[xlxz__mej], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    nlmgr__mfol = dict(axis=axis, kind=kind, order=order)
    keda__kbt = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        tcu__xrb = S.notna().values
        if not tcu__xrb.all():
            nqg__czir = np.full(n, -1, np.int64)
            nqg__czir[tcu__xrb] = argsort(arr[tcu__xrb])
        else:
            nqg__czir = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index, name)
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    nlmgr__mfol = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    keda__kbt = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_index(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_index(): 'na_position' should either be 'first' or 'last'"
            )

    def impl(S, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ybpbx__bet = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, ('$_bodo_col3_',))
        fyo__gsp = ybpbx__bet.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        nqg__czir = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(fyo__gsp,
            0)
        owwu__ykbb = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            fyo__gsp)
        return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
            owwu__ykbb, name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    nlmgr__mfol = dict(axis=axis, inplace=inplace, kind=kind, ignore_index=
        ignore_index, key=key)
    keda__kbt = dict(axis=0, inplace=False, kind='quicksort', ignore_index=
        False, key=None)
    check_unsupported_args('Series.sort_values', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(ascending):
        raise BodoError(
            "Series.sort_values(): 'ascending' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "Series.sort_values(): 'na_position' should either be 'first' or 'last'"
            )

    def impl(S, axis=0, ascending=True, inplace=False, kind='quicksort',
        na_position='last', ignore_index=False, key=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        ybpbx__bet = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, ('$_bodo_col_',))
        fyo__gsp = ybpbx__bet.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        nqg__czir = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(fyo__gsp,
            0)
        owwu__ykbb = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            fyo__gsp)
        return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
            owwu__ykbb, name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    qvq__tkfv = is_overload_true(is_nullable)
    zfqqw__pyfn = (
        'def impl(bins, arr, is_nullable=True, include_lowest=True):\n')
    zfqqw__pyfn += '  numba.parfors.parfor.init_prange()\n'
    zfqqw__pyfn += '  n = len(arr)\n'
    if qvq__tkfv:
        zfqqw__pyfn += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        zfqqw__pyfn += '  out_arr = np.empty(n, np.int64)\n'
    zfqqw__pyfn += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    zfqqw__pyfn += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if qvq__tkfv:
        zfqqw__pyfn += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        zfqqw__pyfn += '      out_arr[i] = -1\n'
    zfqqw__pyfn += '      continue\n'
    zfqqw__pyfn += '    val = arr[i]\n'
    zfqqw__pyfn += '    if include_lowest and val == bins[0]:\n'
    zfqqw__pyfn += '      ind = 1\n'
    zfqqw__pyfn += '    else:\n'
    zfqqw__pyfn += '      ind = np.searchsorted(bins, val)\n'
    zfqqw__pyfn += '    if ind == 0 or ind == len(bins):\n'
    if qvq__tkfv:
        zfqqw__pyfn += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        zfqqw__pyfn += '      out_arr[i] = -1\n'
    zfqqw__pyfn += '    else:\n'
    zfqqw__pyfn += '      out_arr[i] = ind - 1\n'
    zfqqw__pyfn += '  return out_arr\n'
    kfbzh__raf = {}
    exec(zfqqw__pyfn, {'bodo': bodo, 'np': np, 'numba': numba}, kfbzh__raf)
    impl = kfbzh__raf['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        rev__hhp, ggupw__jwnsm = np.divmod(x, 1)
        if rev__hhp == 0:
            zkm__omp = -int(np.floor(np.log10(abs(ggupw__jwnsm)))
                ) - 1 + precision
        else:
            zkm__omp = precision
        return np.around(x, zkm__omp)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        pyv__saxp = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(pyv__saxp)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        llrw__ysqlf = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            rmx__ajem = bins.copy()
            if right and include_lowest:
                rmx__ajem[0] = rmx__ajem[0] - llrw__ysqlf
            lvr__tfpb = bodo.libs.interval_arr_ext.init_interval_array(
                rmx__ajem[:-1], rmx__ajem[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(lvr__tfpb,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        rmx__ajem = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            rmx__ajem[0] = rmx__ajem[0] - 10.0 ** -precision
        lvr__tfpb = bodo.libs.interval_arr_ext.init_interval_array(rmx__ajem
            [:-1], rmx__ajem[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(lvr__tfpb, None)
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        klcc__kkvj = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        patxz__dcvs = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        nqg__czir = np.zeros(nbins, np.int64)
        for hhbvt__hyqt in range(len(klcc__kkvj)):
            nqg__czir[patxz__dcvs[hhbvt__hyqt]] = klcc__kkvj[hhbvt__hyqt]
        return nqg__czir
    return impl


def compute_bins(nbins, min_val, max_val):
    pass


@overload(compute_bins, no_unliteral=True)
def overload_compute_bins(nbins, min_val, max_val, right=True):

    def impl(nbins, min_val, max_val, right=True):
        if nbins < 1:
            raise ValueError('`bins` should be a positive integer.')
        min_val = min_val + 0.0
        max_val = max_val + 0.0
        if np.isinf(min_val) or np.isinf(max_val):
            raise ValueError(
                'cannot specify integer `bins` when input data contains infinity'
                )
        elif min_val == max_val:
            min_val -= 0.001 * abs(min_val) if min_val != 0 else 0.001
            max_val += 0.001 * abs(max_val) if max_val != 0 else 0.001
            bins = np.linspace(min_val, max_val, nbins + 1, endpoint=True)
        else:
            bins = np.linspace(min_val, max_val, nbins + 1, endpoint=True)
            lbbbf__diz = (max_val - min_val) * 0.001
            if right:
                bins[0] -= lbbbf__diz
            else:
                bins[-1] += lbbbf__diz
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    nlmgr__mfol = dict(dropna=dropna)
    keda__kbt = dict(dropna=True)
    check_unsupported_args('Series.value_counts', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not is_overload_constant_bool(normalize):
        raise_bodo_error(
            'Series.value_counts(): normalize argument must be a constant boolean'
            )
    if not is_overload_constant_bool(sort):
        raise_bodo_error(
            'Series.value_counts(): sort argument must be a constant boolean')
    if not is_overload_bool(ascending):
        raise_bodo_error(
            'Series.value_counts(): ascending argument must be a constant boolean'
            )
    ydwj__wfp = not is_overload_none(bins)
    zfqqw__pyfn = 'def impl(\n'
    zfqqw__pyfn += '    S,\n'
    zfqqw__pyfn += '    normalize=False,\n'
    zfqqw__pyfn += '    sort=True,\n'
    zfqqw__pyfn += '    ascending=False,\n'
    zfqqw__pyfn += '    bins=None,\n'
    zfqqw__pyfn += '    dropna=True,\n'
    zfqqw__pyfn += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    zfqqw__pyfn += '):\n'
    zfqqw__pyfn += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    zfqqw__pyfn += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    zfqqw__pyfn += (
        '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    if ydwj__wfp:
        zfqqw__pyfn += '    right = True\n'
        zfqqw__pyfn += _gen_bins_handling(bins, S.dtype)
        zfqqw__pyfn += '    arr = get_bin_inds(bins, arr)\n'
    zfqqw__pyfn += (
        '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
    zfqqw__pyfn += "        (arr,), index, ('$_bodo_col2_',)\n"
    zfqqw__pyfn += '    )\n'
    zfqqw__pyfn += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if ydwj__wfp:
        zfqqw__pyfn += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        zfqqw__pyfn += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        zfqqw__pyfn += '    index = get_bin_labels(bins)\n'
    else:
        zfqqw__pyfn += """    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)
"""
        zfqqw__pyfn += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        zfqqw__pyfn += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        zfqqw__pyfn += '    )\n'
        zfqqw__pyfn += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    zfqqw__pyfn += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        zfqqw__pyfn += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        ypulz__jgxgl = 'len(S)' if ydwj__wfp else 'count_arr.sum()'
        zfqqw__pyfn += f'    res = res / float({ypulz__jgxgl})\n'
    zfqqw__pyfn += '    return res\n'
    kfbzh__raf = {}
    exec(zfqqw__pyfn, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, kfbzh__raf)
    impl = kfbzh__raf['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    zfqqw__pyfn = ''
    if isinstance(bins, types.Integer):
        zfqqw__pyfn += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        zfqqw__pyfn += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            zfqqw__pyfn += '    min_val = min_val.value\n'
            zfqqw__pyfn += '    max_val = max_val.value\n'
        zfqqw__pyfn += (
            '    bins = compute_bins(bins, min_val, max_val, right)\n')
        if dtype == bodo.datetime64ns:
            zfqqw__pyfn += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        zfqqw__pyfn += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return zfqqw__pyfn


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    nlmgr__mfol = dict(right=right, labels=labels, retbins=retbins,
        precision=precision, duplicates=duplicates, ordered=ordered)
    keda__kbt = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='General')
    zfqqw__pyfn = 'def impl(\n'
    zfqqw__pyfn += '    x,\n'
    zfqqw__pyfn += '    bins,\n'
    zfqqw__pyfn += '    right=True,\n'
    zfqqw__pyfn += '    labels=None,\n'
    zfqqw__pyfn += '    retbins=False,\n'
    zfqqw__pyfn += '    precision=3,\n'
    zfqqw__pyfn += '    include_lowest=False,\n'
    zfqqw__pyfn += "    duplicates='raise',\n"
    zfqqw__pyfn += '    ordered=True\n'
    zfqqw__pyfn += '):\n'
    if isinstance(x, SeriesType):
        zfqqw__pyfn += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        zfqqw__pyfn += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        zfqqw__pyfn += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        zfqqw__pyfn += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    zfqqw__pyfn += _gen_bins_handling(bins, x.dtype)
    zfqqw__pyfn += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    zfqqw__pyfn += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    zfqqw__pyfn += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    zfqqw__pyfn += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        zfqqw__pyfn += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        zfqqw__pyfn += '    return res\n'
    else:
        zfqqw__pyfn += '    return out_arr\n'
    kfbzh__raf = {}
    exec(zfqqw__pyfn, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, kfbzh__raf)
    impl = kfbzh__raf['impl']
    return impl


def _get_q_list(q):
    return q


@overload(_get_q_list, no_unliteral=True)
def get_q_list_overload(q):
    if is_overload_int(q):
        return lambda q: np.linspace(0, 1, q + 1)
    return lambda q: q


@overload(pd.qcut, inline='always', no_unliteral=True)
def overload_qcut(x, q, labels=None, retbins=False, precision=3, duplicates
    ='raise'):
    nlmgr__mfol = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    keda__kbt = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        uhfcv__rvy = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, uhfcv__rvy)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    nlmgr__mfol = dict(axis=axis, sort=sort, group_keys=group_keys, squeeze
        =squeeze, observed=observed, dropna=dropna)
    keda__kbt = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='GroupBy')
    if not is_overload_true(as_index):
        raise BodoError('as_index=False only valid with DataFrame')
    if is_overload_none(by) and is_overload_none(level):
        raise BodoError("You have to supply one of 'by' and 'level'")
    if not is_overload_none(by) and not is_overload_none(level):
        raise BodoError(
            "Series.groupby(): 'level' argument should be None if 'by' is not None"
            )
    if not is_overload_none(level):
        if not (is_overload_constant_int(level) and get_overload_const_int(
            level) == 0) or isinstance(S.index, bodo.hiframes.
            pd_multi_index_ext.MultiIndexType):
            raise BodoError(
                "Series.groupby(): MultiIndex case or 'level' other than 0 not supported yet"
                )

        def impl_index(S, by=None, axis=0, level=None, as_index=True, sort=
            True, group_keys=True, squeeze=False, observed=True, dropna=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            zdct__ibi = bodo.utils.conversion.coerce_to_array(index)
            ybpbx__bet = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                zdct__ibi, arr), index, (' ', ''))
            return ybpbx__bet.groupby(' ')['']
        return impl_index
    bnx__enrdb = by
    if isinstance(by, SeriesType):
        bnx__enrdb = by.data
    if isinstance(bnx__enrdb, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        zdct__ibi = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        ybpbx__bet = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            zdct__ibi, arr), index, (' ', ''))
        return ybpbx__bet.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    nlmgr__mfol = dict(verify_integrity=verify_integrity)
    keda__kbt = dict(verify_integrity=False)
    check_unsupported_args('Series.append', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if isinstance(to_append, SeriesType):
        return (lambda S, to_append, ignore_index=False, verify_integrity=
            False: pd.concat((S, to_append), ignore_index=ignore_index,
            verify_integrity=verify_integrity))
    if isinstance(to_append, types.BaseTuple):
        return (lambda S, to_append, ignore_index=False, verify_integrity=
            False: pd.concat((S,) + to_append, ignore_index=ignore_index,
            verify_integrity=verify_integrity))
    return (lambda S, to_append, ignore_index=False, verify_integrity=False:
        pd.concat([S] + to_append, ignore_index=ignore_index,
        verify_integrity=verify_integrity))


@overload_method(SeriesType, 'isin', inline='always', no_unliteral=True)
def overload_series_isin(S, values):
    if bodo.utils.utils.is_array_typ(values):

        def impl_arr(S, values):
            lxxwz__duv = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            nqg__czir = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(nqg__czir, A, lxxwz__duv, False)
            return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index,
                name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nqg__czir = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index, name)
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    nlmgr__mfol = dict(interpolation=interpolation)
    keda__kbt = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            nqg__czir = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index,
                name)
        return impl_list
    elif isinstance(q, (float, types.Number)) or is_overload_constant_int(q):

        def impl(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            return bodo.libs.array_ops.array_op_quantile(arr, q)
        return impl
    else:
        raise BodoError(
            f'Series.quantile() q type must be float or iterable of floats only.'
            )


@overload_method(SeriesType, 'nunique', inline='always', no_unliteral=True)
def overload_series_nunique(S, dropna=True):
    if not is_overload_bool(dropna):
        raise BodoError('Series.nunique: dropna must be a boolean value')

    def impl(S, dropna=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_kernels.nunique(arr, dropna)
    return impl


@overload_method(SeriesType, 'unique', inline='always', no_unliteral=True)
def overload_series_unique(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        uwm__ueh = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(uwm__ueh, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    nlmgr__mfol = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    keda__kbt = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, types.Array) and (isinstance(S.data.dtype,
        types.Number) or S.data.dtype == bodo.datetime64ns)
        ) and not isinstance(S.data, IntegerArrayType):
        raise BodoError(f'describe() column input type {S.data} not supported.'
            )
    if S.data.dtype == bodo.datetime64ns:

        def impl_dt(S, percentiles=None, include=None, exclude=None,
            datetime_is_numeric=True):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(bodo.libs.
                array_ops.array_op_describe(arr), bodo.utils.conversion.
                convert_to_index(['count', 'mean', 'min', '25%', '50%',
                '75%', 'max']), name)
        return impl_dt

    def impl(S, percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(bodo.libs.array_ops.
            array_op_describe(arr), bodo.utils.conversion.convert_to_index(
            ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']), name)
    return impl


@overload_method(SeriesType, 'memory_usage', inline='always', no_unliteral=True
    )
def overload_series_memory_usage(S, index=True, deep=False):
    if is_overload_true(index):

        def impl(S, index=True, deep=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            return arr.nbytes + index.nbytes
        return impl
    else:

        def impl(S, index=True, deep=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            return arr.nbytes
        return impl


def binary_str_fillna_inplace_series_impl(is_binary=False):
    if is_binary:
        bnbaz__gtjpt = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        bnbaz__gtjpt = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    zfqqw__pyfn = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {bnbaz__gtjpt}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    wyj__zdtml = dict()
    exec(zfqqw__pyfn, {'bodo': bodo, 'numba': numba}, wyj__zdtml)
    pimoy__anh = wyj__zdtml['impl']
    return pimoy__anh


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        bnbaz__gtjpt = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        bnbaz__gtjpt = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    zfqqw__pyfn = 'def impl(S,\n'
    zfqqw__pyfn += '     value=None,\n'
    zfqqw__pyfn += '    method=None,\n'
    zfqqw__pyfn += '    axis=None,\n'
    zfqqw__pyfn += '    inplace=False,\n'
    zfqqw__pyfn += '    limit=None,\n'
    zfqqw__pyfn += '   downcast=None,\n'
    zfqqw__pyfn += '):\n'
    zfqqw__pyfn += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    zfqqw__pyfn += '    n = len(in_arr)\n'
    zfqqw__pyfn += f'    out_arr = {bnbaz__gtjpt}(n, -1)\n'
    zfqqw__pyfn += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    zfqqw__pyfn += '        s = in_arr[j]\n'
    zfqqw__pyfn += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    zfqqw__pyfn += '            s = value\n'
    zfqqw__pyfn += '        out_arr[j] = s\n'
    zfqqw__pyfn += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    wyj__zdtml = dict()
    exec(zfqqw__pyfn, {'bodo': bodo, 'numba': numba}, wyj__zdtml)
    pimoy__anh = wyj__zdtml['impl']
    return pimoy__anh


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    pak__kysff = bodo.hiframes.pd_series_ext.get_series_data(S)
    gsj__zpe = bodo.hiframes.pd_series_ext.get_series_data(value)
    for hhbvt__hyqt in numba.parfors.parfor.internal_prange(len(pak__kysff)):
        s = pak__kysff[hhbvt__hyqt]
        if bodo.libs.array_kernels.isna(pak__kysff, hhbvt__hyqt
            ) and not bodo.libs.array_kernels.isna(gsj__zpe, hhbvt__hyqt):
            s = gsj__zpe[hhbvt__hyqt]
        pak__kysff[hhbvt__hyqt] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    pak__kysff = bodo.hiframes.pd_series_ext.get_series_data(S)
    for hhbvt__hyqt in numba.parfors.parfor.internal_prange(len(pak__kysff)):
        s = pak__kysff[hhbvt__hyqt]
        if bodo.libs.array_kernels.isna(pak__kysff, hhbvt__hyqt):
            s = value
        pak__kysff[hhbvt__hyqt] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    pak__kysff = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    gsj__zpe = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(pak__kysff)
    nqg__czir = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for benq__zhevn in numba.parfors.parfor.internal_prange(n):
        s = pak__kysff[benq__zhevn]
        if bodo.libs.array_kernels.isna(pak__kysff, benq__zhevn
            ) and not bodo.libs.array_kernels.isna(gsj__zpe, benq__zhevn):
            s = gsj__zpe[benq__zhevn]
        nqg__czir[benq__zhevn] = s
        if bodo.libs.array_kernels.isna(pak__kysff, benq__zhevn
            ) and bodo.libs.array_kernels.isna(gsj__zpe, benq__zhevn):
            bodo.libs.array_kernels.setna(nqg__czir, benq__zhevn)
    return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    pak__kysff = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    gsj__zpe = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(pak__kysff)
    nqg__czir = bodo.utils.utils.alloc_type(n, pak__kysff.dtype, (-1,))
    for hhbvt__hyqt in numba.parfors.parfor.internal_prange(n):
        s = pak__kysff[hhbvt__hyqt]
        if bodo.libs.array_kernels.isna(pak__kysff, hhbvt__hyqt
            ) and not bodo.libs.array_kernels.isna(gsj__zpe, hhbvt__hyqt):
            s = gsj__zpe[hhbvt__hyqt]
        nqg__czir[hhbvt__hyqt] = s
    return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    nlmgr__mfol = dict(limit=limit, downcast=downcast)
    keda__kbt = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    miocr__ulqs = not is_overload_none(value)
    wza__ybag = not is_overload_none(method)
    if miocr__ulqs and wza__ybag:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not miocr__ulqs and not wza__ybag:
        raise BodoError(
            "Series.fillna(): Must specify one of 'value' and 'method'.")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.fillna(): axis argument not supported')
    elif is_iterable_type(value) and not isinstance(value, SeriesType):
        raise BodoError('Series.fillna(): "value" parameter cannot be a list')
    elif is_var_size_item_array_type(S.data
        ) and not S.dtype == bodo.string_type:
        raise BodoError(
            f'Series.fillna() with inplace=True not supported for {S.dtype} values yet.'
            )
    if not is_overload_constant_bool(inplace):
        raise_bodo_error(
            "Series.fillna(): 'inplace' argument must be a constant boolean")
    if wza__ybag:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        mwlhm__gzoqz = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(mwlhm__gzoqz)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(mwlhm__gzoqz)
    qordp__nqi = element_type(S.data)
    buka__gtbr = None
    if miocr__ulqs:
        buka__gtbr = element_type(types.unliteral(value))
    if buka__gtbr and not can_replace(qordp__nqi, buka__gtbr):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {buka__gtbr} with series type {qordp__nqi}'
            )
    if is_overload_true(inplace):
        if S.dtype == bodo.string_type:
            if is_overload_constant_str(value) and get_overload_const_str(value
                ) == '':
                return (lambda S, value=None, method=None, axis=None,
                    inplace=False, limit=None, downcast=None: bodo.libs.
                    str_arr_ext.set_null_bits_to_value(bodo.hiframes.
                    pd_series_ext.get_series_data(S), -1))
            if isinstance(value, SeriesType):
                return binary_str_fillna_inplace_series_impl(is_binary=False)
            return binary_str_fillna_inplace_impl(is_binary=False)
        if S.dtype == bodo.bytes_type:
            if is_overload_constant_bytes(value) and get_overload_const_bytes(
                value) == b'':
                return (lambda S, value=None, method=None, axis=None,
                    inplace=False, limit=None, downcast=None: bodo.libs.
                    str_arr_ext.set_null_bits_to_value(bodo.hiframes.
                    pd_series_ext.get_series_data(S), -1))
            if isinstance(value, SeriesType):
                return binary_str_fillna_inplace_series_impl(is_binary=True)
            return binary_str_fillna_inplace_impl(is_binary=True)
        else:
            if isinstance(value, SeriesType):
                return fillna_inplace_series_impl
            return fillna_inplace_impl
    else:
        evci__vepdd = S.data
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                pak__kysff = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                gsj__zpe = bodo.hiframes.pd_series_ext.get_series_data(value)
                n = len(pak__kysff)
                nqg__czir = bodo.utils.utils.alloc_type(n, evci__vepdd, (-1,))
                for hhbvt__hyqt in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(pak__kysff, hhbvt__hyqt
                        ) and bodo.libs.array_kernels.isna(gsj__zpe,
                        hhbvt__hyqt):
                        bodo.libs.array_kernels.setna(nqg__czir, hhbvt__hyqt)
                        continue
                    if bodo.libs.array_kernels.isna(pak__kysff, hhbvt__hyqt):
                        nqg__czir[hhbvt__hyqt
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            gsj__zpe[hhbvt__hyqt])
                        continue
                    nqg__czir[hhbvt__hyqt
                        ] = bodo.utils.conversion.unbox_if_timestamp(pak__kysff
                        [hhbvt__hyqt])
                return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
                    index, name)
            return fillna_series_impl
        if wza__ybag:
            urux__tymil = (types.unicode_type, types.bool_, bodo.
                datetime64ns, bodo.timedelta64ns)
            if not isinstance(qordp__nqi, (types.Integer, types.Float)
                ) and qordp__nqi not in urux__tymil:
                raise BodoError(
                    f"Series.fillna(): series of type {qordp__nqi} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                pak__kysff = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                nqg__czir = bodo.libs.array_kernels.ffill_bfill_arr(pak__kysff,
                    method)
                return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            pak__kysff = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(pak__kysff)
            nqg__czir = bodo.utils.utils.alloc_type(n, evci__vepdd, (-1,))
            for hhbvt__hyqt in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(pak__kysff[
                    hhbvt__hyqt])
                if bodo.libs.array_kernels.isna(pak__kysff, hhbvt__hyqt):
                    s = value
                nqg__czir[hhbvt__hyqt] = s
            return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index,
                name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        asit__wslz = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        nlmgr__mfol = dict(limit=limit, downcast=downcast)
        keda__kbt = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', nlmgr__mfol,
            keda__kbt, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        qordp__nqi = element_type(S.data)
        urux__tymil = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(qordp__nqi, (types.Integer, types.Float)
            ) and qordp__nqi not in urux__tymil:
            raise BodoError(
                f'Series.{overload_name}(): series of type {qordp__nqi} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            pak__kysff = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            nqg__czir = bodo.libs.array_kernels.ffill_bfill_arr(pak__kysff,
                asit__wslz)
            return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index,
                name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        dcapn__jun = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(
            dcapn__jun)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        xlj__rryb = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(xlj__rryb)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        xlj__rryb = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(xlj__rryb)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        xlj__rryb = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(xlj__rryb)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    nlmgr__mfol = dict(inplace=inplace, limit=limit, regex=regex, method=method
        )
    kqp__pgky = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', nlmgr__mfol, kqp__pgky,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    qordp__nqi = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        ofnt__yvr = element_type(to_replace.key_type)
        buka__gtbr = element_type(to_replace.value_type)
    else:
        ofnt__yvr = element_type(to_replace)
        buka__gtbr = element_type(value)
    fbfnr__xmbg = None
    if qordp__nqi != types.unliteral(ofnt__yvr):
        if bodo.utils.typing.equality_always_false(qordp__nqi, types.
            unliteral(ofnt__yvr)
            ) or not bodo.utils.typing.types_equality_exists(qordp__nqi,
            ofnt__yvr):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(qordp__nqi, (types.Float, types.Integer)
            ) or qordp__nqi == np.bool_:
            fbfnr__xmbg = qordp__nqi
    if not can_replace(qordp__nqi, types.unliteral(buka__gtbr)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    cla__jke = S.data
    if isinstance(cla__jke, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            pak__kysff = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(pak__kysff.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        pak__kysff = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(pak__kysff)
        nqg__czir = bodo.utils.utils.alloc_type(n, cla__jke, (-1,))
        rqo__exva = build_replace_dict(to_replace, value, fbfnr__xmbg)
        for hhbvt__hyqt in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(pak__kysff, hhbvt__hyqt):
                bodo.libs.array_kernels.setna(nqg__czir, hhbvt__hyqt)
                continue
            s = pak__kysff[hhbvt__hyqt]
            if s in rqo__exva:
                s = rqo__exva[s]
            nqg__czir[hhbvt__hyqt] = s
        return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index, name)
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    jnuwh__mkz = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    wiiaf__ufra = is_iterable_type(to_replace)
    qfw__offz = isinstance(value, (types.Number, Decimal128Type)) or value in [
        bodo.string_type, bodo.bytes_type, types.boolean]
    tap__skj = is_iterable_type(value)
    if jnuwh__mkz and qfw__offz:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                rqo__exva = {}
                rqo__exva[key_dtype_conv(to_replace)] = value
                return rqo__exva
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            rqo__exva = {}
            rqo__exva[to_replace] = value
            return rqo__exva
        return impl
    if wiiaf__ufra and qfw__offz:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                rqo__exva = {}
                for ewcpx__iaip in to_replace:
                    rqo__exva[key_dtype_conv(ewcpx__iaip)] = value
                return rqo__exva
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            rqo__exva = {}
            for ewcpx__iaip in to_replace:
                rqo__exva[ewcpx__iaip] = value
            return rqo__exva
        return impl
    if wiiaf__ufra and tap__skj:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                rqo__exva = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for hhbvt__hyqt in range(len(to_replace)):
                    rqo__exva[key_dtype_conv(to_replace[hhbvt__hyqt])] = value[
                        hhbvt__hyqt]
                return rqo__exva
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            rqo__exva = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for hhbvt__hyqt in range(len(to_replace)):
                rqo__exva[to_replace[hhbvt__hyqt]] = value[hhbvt__hyqt]
            return rqo__exva
        return impl
    if isinstance(to_replace, numba.types.DictType) and is_overload_none(value
        ):
        return lambda to_replace, value, key_dtype_conv: to_replace
    raise BodoError(
        'Series.replace(): Not supported for types to_replace={} and value={}'
        .format(to_replace, value))


@overload_method(SeriesType, 'diff', inline='always', no_unliteral=True)
def overload_series_diff(S, periods=1):
    if not (isinstance(S.data, types.Array) and (isinstance(S.data.dtype,
        types.Number) or S.data.dtype == bodo.datetime64ns)):
        raise BodoError(
            f'Series.diff() column input type {S.data} not supported.')
    if not is_overload_int(periods):
        raise BodoError("Series.diff(): 'periods' input must be an integer.")
    if S.data == types.Array(bodo.datetime64ns, 1, 'C'):

        def impl_datetime(S, periods=1):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            nqg__czir = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index,
                name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nqg__czir = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index, name)
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    nlmgr__mfol = dict(ignore_index=ignore_index)
    gsewc__kwvv = dict(ignore_index=False)
    check_unsupported_args('Series.explode', nlmgr__mfol, gsewc__kwvv,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        clzh__gzq = bodo.utils.conversion.index_to_array(index)
        nqg__czir, jabxl__lpje = bodo.libs.array_kernels.explode(arr, clzh__gzq
            )
        owwu__ykbb = bodo.utils.conversion.index_from_array(jabxl__lpje)
        return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
            owwu__ykbb, name)
    return impl


@overload(np.digitize, inline='always', no_unliteral=True)
def overload_series_np_digitize(x, bins, right=False):
    if isinstance(x, SeriesType):

        def impl(x, bins, right=False):
            arr = bodo.hiframes.pd_series_ext.get_series_data(x)
            return np.digitize(arr, bins, right)
        return impl


@overload(np.argmax, inline='always', no_unliteral=True)
def argmax_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            opfj__jsp = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for hhbvt__hyqt in numba.parfors.parfor.internal_prange(n):
                opfj__jsp[hhbvt__hyqt] = np.argmax(a[hhbvt__hyqt])
            return opfj__jsp
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            gsjhv__nvjqa = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for hhbvt__hyqt in numba.parfors.parfor.internal_prange(n):
                gsjhv__nvjqa[hhbvt__hyqt] = np.argmin(a[hhbvt__hyqt])
            return gsjhv__nvjqa
        return impl


def overload_series_np_dot(a, b, out=None):
    if (isinstance(a, SeriesType) or isinstance(b, SeriesType)
        ) and not is_overload_none(out):
        raise BodoError("np.dot(): 'out' parameter not supported yet")
    if isinstance(a, SeriesType):

        def impl(a, b, out=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(a)
            return np.dot(arr, b)
        return impl
    if isinstance(b, SeriesType):

        def impl(a, b, out=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(b)
            return np.dot(a, arr)
        return impl


overload(np.dot, inline='always', no_unliteral=True)(overload_series_np_dot)
overload(operator.matmul, inline='always', no_unliteral=True)(
    overload_series_np_dot)


@overload_method(SeriesType, 'dropna', inline='always', no_unliteral=True)
def overload_series_dropna(S, axis=0, inplace=False, how=None):
    nlmgr__mfol = dict(axis=axis, inplace=inplace, how=how)
    vafmz__qopo = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', nlmgr__mfol, vafmz__qopo,
        package_name='pandas', module_name='Series')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            pak__kysff = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            tcu__xrb = S.notna().values
            clzh__gzq = bodo.utils.conversion.extract_index_array(S)
            owwu__ykbb = bodo.utils.conversion.convert_to_index(clzh__gzq[
                tcu__xrb])
            nqg__czir = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(pak__kysff))
            return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
                owwu__ykbb, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            pak__kysff = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            clzh__gzq = bodo.utils.conversion.extract_index_array(S)
            tcu__xrb = S.notna().values
            owwu__ykbb = bodo.utils.conversion.convert_to_index(clzh__gzq[
                tcu__xrb])
            nqg__czir = pak__kysff[tcu__xrb]
            return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
                owwu__ykbb, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    nlmgr__mfol = dict(freq=freq, axis=axis, fill_value=fill_value)
    keda__kbt = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not is_supported_shift_array_type(S.data):
        raise BodoError(
            f"Series.shift(): Series input type '{S.data.dtype}' not supported yet."
            )
    if not is_overload_int(periods):
        raise BodoError("Series.shift(): 'periods' input must be an integer.")

    def impl(S, periods=1, freq=None, axis=0, fill_value=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nqg__czir = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index, name)
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    nlmgr__mfol = dict(fill_method=fill_method, limit=limit, freq=freq)
    keda__kbt = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not is_overload_int(periods):
        raise BodoError(
            'Series.pct_change(): periods argument must be an Integer')

    def impl(S, periods=1, fill_method='pad', limit=None, freq=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nqg__czir = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index, name)
    return impl


def create_series_mask_where_overload(func_name):

    def overload_series_mask_where(S, cond, other=np.nan, inplace=False,
        axis=None, level=None, errors='raise', try_cast=False):
        _validate_arguments_mask_where(f'Series.{func_name}', S, cond,
            other, inplace, axis, level, errors, try_cast)
        if is_overload_constant_nan(other):
            wlw__yxq = 'None'
        else:
            wlw__yxq = 'other'
        zfqqw__pyfn = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            zfqqw__pyfn += '  cond = ~cond\n'
        zfqqw__pyfn += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        zfqqw__pyfn += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        zfqqw__pyfn += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        zfqqw__pyfn += (
            f'  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {wlw__yxq})\n'
            )
        zfqqw__pyfn += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        kfbzh__raf = {}
        exec(zfqqw__pyfn, {'bodo': bodo, 'np': np}, kfbzh__raf)
        impl = kfbzh__raf['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        dcapn__jun = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(dcapn__jun)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, S, cond, other, inplace, axis,
    level, errors, try_cast):
    nlmgr__mfol = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    keda__kbt = dict(inplace=False, level=None, errors='raise', try_cast=False)
    check_unsupported_args(f'{func_name}', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error(f'{func_name}(): axis argument not supported')
    if isinstance(other, SeriesType):
        _validate_self_other_mask_where(func_name, S.data, other.data)
    else:
        _validate_self_other_mask_where(func_name, S.data, other)
    if not (isinstance(cond, (SeriesType, types.Array, BooleanArrayType)) and
        cond.ndim == 1 and cond.dtype == types.bool_):
        raise BodoError(
            f"{func_name}() 'cond' argument must be a Series or 1-dim array of booleans"
            )


def _validate_self_other_mask_where(func_name, arr, other, max_ndim=1,
    is_default=False):
    if not (isinstance(arr, types.Array) or isinstance(arr,
        BooleanArrayType) or isinstance(arr, IntegerArrayType) or bodo.
        utils.utils.is_array_typ(arr, False) and arr.dtype in [bodo.
        string_type, bodo.bytes_type] or isinstance(arr, bodo.
        CategoricalArrayType) and arr.dtype.elem_type not in [bodo.
        datetime64ns, bodo.timedelta64ns, bodo.pd_timestamp_type, bodo.
        pd_timedelta_type]):
        raise BodoError(
            f'{func_name}() Series data with type {arr} not yet supported')
    fprd__gcs = is_overload_constant_nan(other)
    if not (is_default or fprd__gcs or is_scalar_type(other) or isinstance(
        other, types.Array) and other.ndim >= 1 and other.ndim <= max_ndim or
        isinstance(other, SeriesType) and (isinstance(arr, types.Array) or 
        arr.dtype in [bodo.string_type, bodo.bytes_type]) or isinstance(
        other, StringArrayType) and (arr.dtype == bodo.string_type or 
        isinstance(arr, bodo.CategoricalArrayType) and arr.dtype.elem_type ==
        bodo.string_type) or isinstance(other, BinaryArrayType) and (arr.
        dtype == bodo.bytes_type or isinstance(arr, bodo.
        CategoricalArrayType) and arr.dtype.elem_type == bodo.bytes_type) or
        (not isinstance(other, (StringArrayType, BinaryArrayType)) and (
        isinstance(arr.dtype, types.Integer) and (bodo.utils.utils.
        is_array_typ(other) and isinstance(other.dtype, types.Integer) or 
        is_series_type(other) and isinstance(other.dtype, types.Integer))) or
        (bodo.utils.utils.is_array_typ(other) and arr.dtype == other.dtype or
        is_series_type(other) and arr.dtype == other.dtype)) and (
        isinstance(arr, BooleanArrayType) or isinstance(arr, IntegerArrayType))
        ):
        raise BodoError(
            f"{func_name}() 'other' must be a scalar, non-categorical series, 1-dim numpy array or StringArray with a matching type for Series."
            )
    if not is_default:
        if isinstance(arr.dtype, bodo.PDCategoricalDtype):
            ltkc__hphx = arr.dtype.elem_type
        else:
            ltkc__hphx = arr.dtype
        if is_iterable_type(other):
            gtxvr__bcr = other.dtype
        elif fprd__gcs:
            gtxvr__bcr = types.float64
        else:
            gtxvr__bcr = types.unliteral(other)
        if not fprd__gcs and not is_common_scalar_dtype([ltkc__hphx,
            gtxvr__bcr]):
            raise BodoError(
                f"{func_name}() series and 'other' must share a common type.")


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        nlmgr__mfol = dict(level=level, axis=axis)
        keda__kbt = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__), nlmgr__mfol,
            keda__kbt, package_name='pandas', module_name='Series')
        etd__kwryb = other == string_type or is_overload_constant_str(other)
        lwv__nthd = is_iterable_type(other) and other.dtype == string_type
        ytg__eqgze = S.dtype == string_type and (op == operator.add and (
            etd__kwryb or lwv__nthd) or op == operator.mul and isinstance(
            other, types.Integer))
        esu__mgcyi = S.dtype == bodo.timedelta64ns
        vjum__viw = S.dtype == bodo.datetime64ns
        yyfp__hqxhs = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        yfh__ibrw = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        bnrck__hnvj = esu__mgcyi and (yyfp__hqxhs or yfh__ibrw
            ) or vjum__viw and yyfp__hqxhs
        bnrck__hnvj = bnrck__hnvj and op == operator.add
        if not (isinstance(S.dtype, types.Number) or ytg__eqgze or bnrck__hnvj
            ):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        rpey__fjdqq = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            cla__jke = rpey__fjdqq.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and cla__jke == types.Array(types.bool_, 1, 'C'):
                cla__jke = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                nqg__czir = bodo.utils.utils.alloc_type(n, cla__jke, (-1,))
                for hhbvt__hyqt in numba.parfors.parfor.internal_prange(n):
                    qzq__abdiu = bodo.libs.array_kernels.isna(arr, hhbvt__hyqt)
                    if qzq__abdiu:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(nqg__czir,
                                hhbvt__hyqt)
                        else:
                            nqg__czir[hhbvt__hyqt] = op(fill_value, other)
                    else:
                        nqg__czir[hhbvt__hyqt] = op(arr[hhbvt__hyqt], other)
                return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        cla__jke = rpey__fjdqq.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and cla__jke == types.Array(
            types.bool_, 1, 'C'):
            cla__jke = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            cff__bxn = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            nqg__czir = bodo.utils.utils.alloc_type(n, cla__jke, (-1,))
            for hhbvt__hyqt in numba.parfors.parfor.internal_prange(n):
                qzq__abdiu = bodo.libs.array_kernels.isna(arr, hhbvt__hyqt)
                gppm__eohrq = bodo.libs.array_kernels.isna(cff__bxn,
                    hhbvt__hyqt)
                if qzq__abdiu and gppm__eohrq:
                    bodo.libs.array_kernels.setna(nqg__czir, hhbvt__hyqt)
                elif qzq__abdiu:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(nqg__czir, hhbvt__hyqt)
                    else:
                        nqg__czir[hhbvt__hyqt] = op(fill_value, cff__bxn[
                            hhbvt__hyqt])
                elif gppm__eohrq:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(nqg__czir, hhbvt__hyqt)
                    else:
                        nqg__czir[hhbvt__hyqt] = op(arr[hhbvt__hyqt],
                            fill_value)
                else:
                    nqg__czir[hhbvt__hyqt] = op(arr[hhbvt__hyqt], cff__bxn[
                        hhbvt__hyqt])
            return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index,
                name)
        return impl
    return overload_series_explicit_binary_op


def create_explicit_binary_reverse_op_overload(op):

    def overload_series_explicit_binary_reverse_op(S, other, level=None,
        fill_value=None, axis=0):
        if not is_overload_none(level):
            raise BodoError('level argument not supported')
        if not is_overload_zero(axis):
            raise BodoError('axis argument not supported')
        if not isinstance(S.dtype, types.Number):
            raise BodoError('only numeric values supported')
        rpey__fjdqq = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            cla__jke = rpey__fjdqq.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and cla__jke == types.Array(types.bool_, 1, 'C'):
                cla__jke = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                nqg__czir = bodo.utils.utils.alloc_type(n, cla__jke, None)
                for hhbvt__hyqt in numba.parfors.parfor.internal_prange(n):
                    qzq__abdiu = bodo.libs.array_kernels.isna(arr, hhbvt__hyqt)
                    if qzq__abdiu:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(nqg__czir,
                                hhbvt__hyqt)
                        else:
                            nqg__czir[hhbvt__hyqt] = op(other, fill_value)
                    else:
                        nqg__czir[hhbvt__hyqt] = op(other, arr[hhbvt__hyqt])
                return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        cla__jke = rpey__fjdqq.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and cla__jke == types.Array(
            types.bool_, 1, 'C'):
            cla__jke = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            cff__bxn = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            nqg__czir = bodo.utils.utils.alloc_type(n, cla__jke, None)
            for hhbvt__hyqt in numba.parfors.parfor.internal_prange(n):
                qzq__abdiu = bodo.libs.array_kernels.isna(arr, hhbvt__hyqt)
                gppm__eohrq = bodo.libs.array_kernels.isna(cff__bxn,
                    hhbvt__hyqt)
                nqg__czir[hhbvt__hyqt] = op(cff__bxn[hhbvt__hyqt], arr[
                    hhbvt__hyqt])
                if qzq__abdiu and gppm__eohrq:
                    bodo.libs.array_kernels.setna(nqg__czir, hhbvt__hyqt)
                elif qzq__abdiu:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(nqg__czir, hhbvt__hyqt)
                    else:
                        nqg__czir[hhbvt__hyqt] = op(cff__bxn[hhbvt__hyqt],
                            fill_value)
                elif gppm__eohrq:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(nqg__czir, hhbvt__hyqt)
                    else:
                        nqg__czir[hhbvt__hyqt] = op(fill_value, arr[
                            hhbvt__hyqt])
                else:
                    nqg__czir[hhbvt__hyqt] = op(cff__bxn[hhbvt__hyqt], arr[
                        hhbvt__hyqt])
            return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index,
                name)
        return impl
    return overload_series_explicit_binary_reverse_op


explicit_binop_funcs_two_ways = {operator.add: {'add'}, operator.sub: {
    'sub'}, operator.mul: {'mul'}, operator.truediv: {'div', 'truediv'},
    operator.floordiv: {'floordiv'}, operator.mod: {'mod'}, operator.pow: {
    'pow'}}
explicit_binop_funcs_single = {operator.lt: 'lt', operator.gt: 'gt',
    operator.le: 'le', operator.ge: 'ge', operator.ne: 'ne', operator.eq: 'eq'}
explicit_binop_funcs = set()
split_logical_binops_funcs = [operator.or_, operator.and_]


def _install_explicit_binary_ops():
    for op, xtb__nrm in explicit_binop_funcs_two_ways.items():
        for name in xtb__nrm:
            dcapn__jun = create_explicit_binary_op_overload(op)
            njv__unx = create_explicit_binary_reverse_op_overload(op)
            uxq__znbc = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(dcapn__jun)
            overload_method(SeriesType, uxq__znbc, no_unliteral=True)(njv__unx)
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        dcapn__jun = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(dcapn__jun)
        explicit_binop_funcs.add(name)


_install_explicit_binary_ops()


def create_binary_op_overload(op):

    def overload_series_binary_op(lhs, rhs):
        if (isinstance(lhs, SeriesType) and isinstance(rhs, SeriesType) and
            lhs.dtype == bodo.datetime64ns and rhs.dtype == bodo.
            datetime64ns and op == operator.sub):

            def impl_dt64(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                duho__cgid = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                nqg__czir = dt64_arr_sub(arr, duho__cgid)
                return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
                    index, name)
            return impl_dt64
        if op in [operator.add, operator.sub] and isinstance(lhs, SeriesType
            ) and lhs.dtype == bodo.datetime64ns and is_offsets_type(rhs):

            def impl_offsets(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                numba.parfors.parfor.init_prange()
                n = len(lhs)
                nqg__czir = np.empty(n, np.dtype('datetime64[ns]'))
                for hhbvt__hyqt in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, hhbvt__hyqt):
                        bodo.libs.array_kernels.setna(nqg__czir, hhbvt__hyqt)
                        continue
                    tfv__vxa = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[hhbvt__hyqt]))
                    ziv__qlg = op(tfv__vxa, rhs)
                    nqg__czir[hhbvt__hyqt
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        ziv__qlg.value)
                return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
                    index, name)
            return impl_offsets
        if op == operator.add and is_offsets_type(lhs) and isinstance(rhs,
            SeriesType) and rhs.dtype == bodo.datetime64ns:

            def impl(lhs, rhs):
                return op(rhs, lhs)
            return impl
        if isinstance(lhs, SeriesType):
            if lhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                    duho__cgid = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    nqg__czir = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(duho__cgid))
                    return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                duho__cgid = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                nqg__czir = op(arr, duho__cgid)
                return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    ccspc__bby = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    nqg__czir = op(bodo.utils.conversion.unbox_if_timestamp
                        (ccspc__bby), arr)
                    return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                ccspc__bby = (bodo.utils.conversion.
                    get_array_if_series_or_index(lhs))
                nqg__czir = op(ccspc__bby, arr)
                return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        dcapn__jun = create_binary_op_overload(op)
        overload(op)(dcapn__jun)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    igfy__tmyay = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, igfy__tmyay)
        for hhbvt__hyqt in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, hhbvt__hyqt
                ) or bodo.libs.array_kernels.isna(arg2, hhbvt__hyqt):
                bodo.libs.array_kernels.setna(S, hhbvt__hyqt)
                continue
            S[hhbvt__hyqt
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                hhbvt__hyqt]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[hhbvt__hyqt]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                cff__bxn = bodo.utils.conversion.get_array_if_series_or_index(
                    other)
                op(arr, cff__bxn)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        dcapn__jun = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(dcapn__jun)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                nqg__czir = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        dcapn__jun = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(dcapn__jun)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    nqg__czir = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
                        index, name)
                return impl
        return overload_series_ufunc_nin_1
    elif ufunc.nin == 2:

        def overload_series_ufunc_nin_2(S1, S2):
            if isinstance(S1, SeriesType):

                def impl(S1, S2):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S1)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S1)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S1)
                    cff__bxn = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    nqg__czir = ufunc(arr, cff__bxn)
                    return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    cff__bxn = bodo.hiframes.pd_series_ext.get_series_data(S2)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    nqg__czir = ufunc(arr, cff__bxn)
                    return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        dcapn__jun = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(dcapn__jun)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        pdsfz__ubc = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.copy(),)
            )
        ybq__ihhj = np.arange(n),
        bodo.libs.timsort.sort(pdsfz__ubc, 0, n, ybq__ihhj)
        return ybq__ihhj[0]
    return impl


@overload(pd.to_numeric, inline='always', no_unliteral=True)
def overload_to_numeric(arg_a, errors='raise', downcast=None):
    if not is_overload_none(downcast) and not (is_overload_constant_str(
        downcast) and get_overload_const_str(downcast) in ('integer',
        'signed', 'unsigned', 'float')):
        raise BodoError(
            'pd.to_numeric(): invalid downcasting method provided {}'.
            format(downcast))
    out_dtype = types.float64
    if not is_overload_none(downcast):
        fwnci__rzfd = get_overload_const_str(downcast)
        if fwnci__rzfd in ('integer', 'signed'):
            out_dtype = types.int64
        elif fwnci__rzfd == 'unsigned':
            out_dtype = types.uint64
        else:
            assert fwnci__rzfd == 'float'
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            pak__kysff = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            nqg__czir = pd.to_numeric(pak__kysff, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index,
                name)
        return impl_series
    if arg_a != string_array_type:
        raise BodoError('pd.to_numeric(): invalid argument type {}'.format(
            arg_a))
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            oujb__wkd = np.empty(n, np.float64)
            for hhbvt__hyqt in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, hhbvt__hyqt):
                    bodo.libs.array_kernels.setna(oujb__wkd, hhbvt__hyqt)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(oujb__wkd,
                        hhbvt__hyqt, arg_a, hhbvt__hyqt)
            return oujb__wkd
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            oujb__wkd = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for hhbvt__hyqt in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, hhbvt__hyqt):
                    bodo.libs.array_kernels.setna(oujb__wkd, hhbvt__hyqt)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(oujb__wkd,
                        hhbvt__hyqt, arg_a, hhbvt__hyqt)
            return oujb__wkd
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        dcbk__dxu = if_series_to_array_type(args[0])
        if isinstance(dcbk__dxu, types.Array) and isinstance(dcbk__dxu.
            dtype, types.Integer):
            dcbk__dxu = types.Array(types.float64, 1, 'C')
        return dcbk__dxu(*args)


def where_impl_one_arg(c):
    return np.where(c)


@overload(where_impl_one_arg, no_unliteral=True)
def overload_where_unsupported_one_arg(condition):
    if isinstance(condition, SeriesType) or bodo.utils.utils.is_array_typ(
        condition, False):
        return lambda condition: np.where(condition)


def overload_np_where_one_arg(condition):
    if isinstance(condition, SeriesType):

        def impl_series(condition):
            condition = bodo.hiframes.pd_series_ext.get_series_data(condition)
            return bodo.libs.array_kernels.nonzero(condition)
        return impl_series
    elif bodo.utils.utils.is_array_typ(condition, False):

        def impl(condition):
            return bodo.libs.array_kernels.nonzero(condition)
        return impl


overload(np.where, inline='always', no_unliteral=True)(
    overload_np_where_one_arg)
overload(where_impl_one_arg, inline='always', no_unliteral=True)(
    overload_np_where_one_arg)


def where_impl(c, x, y):
    return np.where(c, x, y)


@overload(where_impl, no_unliteral=True)
def overload_where_unsupported(condition, x, y):
    if not isinstance(condition, (SeriesType, types.Array, BooleanArrayType)
        ) or condition.ndim != 1:
        return lambda condition, x, y: np.where(condition, x, y)


@overload(where_impl, no_unliteral=True)
@overload(np.where, no_unliteral=True)
def overload_np_where(condition, x, y):
    if not isinstance(condition, (SeriesType, types.Array, BooleanArrayType)
        ) or condition.ndim != 1:
        return
    assert condition.dtype == types.bool_, 'invalid condition dtype'
    subn__gglm = bodo.utils.utils.is_array_typ(x, True)
    vgslx__fcgi = bodo.utils.utils.is_array_typ(y, True)
    zfqqw__pyfn = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        zfqqw__pyfn += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if subn__gglm and not bodo.utils.utils.is_array_typ(x, False):
        zfqqw__pyfn += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if vgslx__fcgi and not bodo.utils.utils.is_array_typ(y, False):
        zfqqw__pyfn += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    zfqqw__pyfn += '  n = len(condition)\n'
    ijk__vqg = x.dtype if subn__gglm else types.unliteral(x)
    opmii__cyti = y.dtype if vgslx__fcgi else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        ijk__vqg = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        opmii__cyti = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    ltdub__cllkl = get_data(x)
    eys__giw = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(ybq__ihhj) for
        ybq__ihhj in [ltdub__cllkl, eys__giw])
    if eys__giw == types.none:
        if isinstance(ijk__vqg, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif ltdub__cllkl == eys__giw and not is_nullable:
        out_dtype = dtype_to_array_type(ijk__vqg)
    elif ijk__vqg == string_type or opmii__cyti == string_type:
        out_dtype = bodo.string_array_type
    elif ltdub__cllkl == bytes_type or (subn__gglm and ijk__vqg == bytes_type
        ) and (eys__giw == bytes_type or vgslx__fcgi and opmii__cyti ==
        bytes_type):
        out_dtype = binary_array_type
    elif isinstance(ijk__vqg, bodo.PDCategoricalDtype):
        out_dtype = None
    elif ijk__vqg in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(ijk__vqg, 1, 'C')
    elif opmii__cyti in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(opmii__cyti, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(ijk__vqg), numba.np.numpy_support.
            as_dtype(opmii__cyti)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(ijk__vqg, bodo.PDCategoricalDtype):
        txs__csn = 'x'
    else:
        txs__csn = 'out_dtype'
    zfqqw__pyfn += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {txs__csn}, (-1,))\n')
    if isinstance(ijk__vqg, bodo.PDCategoricalDtype):
        zfqqw__pyfn += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        zfqqw__pyfn += """  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)
"""
    zfqqw__pyfn += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    zfqqw__pyfn += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if subn__gglm:
        zfqqw__pyfn += '      if bodo.libs.array_kernels.isna(x, j):\n'
        zfqqw__pyfn += '        setna(out_arr, j)\n'
        zfqqw__pyfn += '        continue\n'
    if isinstance(ijk__vqg, bodo.PDCategoricalDtype):
        zfqqw__pyfn += '      out_codes[j] = x_codes[j]\n'
    else:
        zfqqw__pyfn += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if subn__gglm else 'x'))
    zfqqw__pyfn += '    else:\n'
    if vgslx__fcgi:
        zfqqw__pyfn += '      if bodo.libs.array_kernels.isna(y, j):\n'
        zfqqw__pyfn += '        setna(out_arr, j)\n'
        zfqqw__pyfn += '        continue\n'
    if eys__giw == types.none:
        if isinstance(ijk__vqg, bodo.PDCategoricalDtype):
            zfqqw__pyfn += '      out_codes[j] = -1\n'
        else:
            zfqqw__pyfn += '      setna(out_arr, j)\n'
    else:
        zfqqw__pyfn += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if vgslx__fcgi else 'y'))
    zfqqw__pyfn += '  return out_arr\n'
    kfbzh__raf = {}
    exec(zfqqw__pyfn, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, kfbzh__raf)
    dvv__kyeby = kfbzh__raf['_impl']
    return dvv__kyeby


def _verify_np_select_arg_typs(condlist, choicelist, default):
    if isinstance(condlist, (types.List, types.UniTuple)):
        if not (bodo.utils.utils.is_np_array_typ(condlist.dtype) and 
            condlist.dtype.dtype == types.bool_):
            raise BodoError(
                "np.select(): 'condlist' argument must be list or tuple of boolean ndarrays. If passing a Series, please convert with pd.Series.to_numpy()."
                )
    else:
        raise BodoError(
            "np.select(): 'condlist' argument must be list or tuple of boolean ndarrays. If passing a Series, please convert with pd.Series.to_numpy()."
            )
    if not isinstance(choicelist, (types.List, types.UniTuple, types.BaseTuple)
        ):
        raise BodoError(
            "np.select(): 'choicelist' argument must be list or tuple type")
    if isinstance(choicelist, (types.List, types.UniTuple)):
        qez__wdm = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(qez__wdm, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(qez__wdm):
            tixx__ufy = qez__wdm.data.dtype
        else:
            tixx__ufy = qez__wdm.dtype
        if isinstance(tixx__ufy, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        nvnq__nms = qez__wdm
    else:
        qzko__ipjb = []
        for qez__wdm in choicelist:
            if not bodo.utils.utils.is_array_typ(qez__wdm, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(qez__wdm):
                tixx__ufy = qez__wdm.data.dtype
            else:
                tixx__ufy = qez__wdm.dtype
            if isinstance(tixx__ufy, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            qzko__ipjb.append(tixx__ufy)
        if not is_common_scalar_dtype(qzko__ipjb):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        nvnq__nms = choicelist[0]
    if is_series_type(nvnq__nms):
        nvnq__nms = nvnq__nms.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, nvnq__nms.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(nvnq__nms, types.Array) or isinstance(nvnq__nms,
        BooleanArrayType) or isinstance(nvnq__nms, IntegerArrayType) or 
        bodo.utils.utils.is_array_typ(nvnq__nms, False) and nvnq__nms.dtype in
        [bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {nvnq__nms} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    cnjzo__qvwpi = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        wmy__xrq = choicelist.dtype
    else:
        jtwk__dfww = False
        qzko__ipjb = []
        for qez__wdm in choicelist:
            if is_nullable_type(qez__wdm):
                jtwk__dfww = True
            if is_series_type(qez__wdm):
                tixx__ufy = qez__wdm.data.dtype
            else:
                tixx__ufy = qez__wdm.dtype
            if isinstance(tixx__ufy, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            qzko__ipjb.append(tixx__ufy)
        cdy__hukw, skre__xnm = get_common_scalar_dtype(qzko__ipjb)
        if not skre__xnm:
            raise BodoError('Internal error in overload_np_select')
        ijd__fscod = dtype_to_array_type(cdy__hukw)
        if jtwk__dfww:
            ijd__fscod = to_nullable_type(ijd__fscod)
        wmy__xrq = ijd__fscod
    if isinstance(wmy__xrq, SeriesType):
        wmy__xrq = wmy__xrq.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        ixfv__aum = True
    else:
        ixfv__aum = False
    ylj__tvej = False
    kfja__dkirr = False
    if ixfv__aum:
        if isinstance(wmy__xrq.dtype, types.Number):
            pass
        elif wmy__xrq.dtype == types.bool_:
            kfja__dkirr = True
        else:
            ylj__tvej = True
            wmy__xrq = to_nullable_type(wmy__xrq)
    elif default == types.none or is_overload_constant_nan(default):
        ylj__tvej = True
        wmy__xrq = to_nullable_type(wmy__xrq)
    zfqqw__pyfn = 'def np_select_impl(condlist, choicelist, default=0):\n'
    zfqqw__pyfn += '  if len(condlist) != len(choicelist):\n'
    zfqqw__pyfn += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    zfqqw__pyfn += '  output_len = len(choicelist[0])\n'
    zfqqw__pyfn += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    zfqqw__pyfn += '  for i in range(output_len):\n'
    if ylj__tvej:
        zfqqw__pyfn += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif kfja__dkirr:
        zfqqw__pyfn += '    out[i] = False\n'
    else:
        zfqqw__pyfn += '    out[i] = default\n'
    if cnjzo__qvwpi:
        zfqqw__pyfn += '  for i in range(len(condlist) - 1, -1, -1):\n'
        zfqqw__pyfn += '    cond = condlist[i]\n'
        zfqqw__pyfn += '    choice = choicelist[i]\n'
        zfqqw__pyfn += '    out = np.where(cond, choice, out)\n'
    else:
        for hhbvt__hyqt in range(len(choicelist) - 1, -1, -1):
            zfqqw__pyfn += f'  cond = condlist[{hhbvt__hyqt}]\n'
            zfqqw__pyfn += f'  choice = choicelist[{hhbvt__hyqt}]\n'
            zfqqw__pyfn += f'  out = np.where(cond, choice, out)\n'
    zfqqw__pyfn += '  return out'
    kfbzh__raf = dict()
    exec(zfqqw__pyfn, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': wmy__xrq}, kfbzh__raf)
    impl = kfbzh__raf['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nqg__czir = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index, name)
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    nlmgr__mfol = dict(subset=subset, keep=keep, inplace=inplace)
    keda__kbt = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        fwj__wfy = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (fwj__wfy,), clzh__gzq = bodo.libs.array_kernels.drop_duplicates((
            fwj__wfy,), index, 1)
        index = bodo.utils.conversion.index_from_array(clzh__gzq)
        return bodo.hiframes.pd_series_ext.init_series(fwj__wfy, index, name)
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    wsa__dnr = element_type(S.data)
    if not is_common_scalar_dtype([wsa__dnr, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([wsa__dnr, right]):
        raise_bodo_error(
            "Series.between(): 'right' must be compariable with the Series data"
            )
    if not is_overload_constant_str(inclusive) or get_overload_const_str(
        inclusive) not in ('both', 'neither'):
        raise_bodo_error(
            "Series.between(): 'inclusive' must be a constant string and one of ('both', 'neither')"
            )

    def impl(S, left, right, inclusive='both'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(arr)
        nqg__czir = np.empty(n, np.bool_)
        for hhbvt__hyqt in numba.parfors.parfor.internal_prange(n):
            zrv__finos = bodo.utils.conversion.box_if_dt64(arr[hhbvt__hyqt])
            if inclusive == 'both':
                nqg__czir[hhbvt__hyqt
                    ] = zrv__finos <= right and zrv__finos >= left
            else:
                nqg__czir[hhbvt__hyqt
                    ] = zrv__finos < right and zrv__finos > left
        return bodo.hiframes.pd_series_ext.init_series(nqg__czir, index, name)
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    nlmgr__mfol = dict(axis=axis)
    keda__kbt = dict(axis=None)
    check_unsupported_args('Series.repeat', nlmgr__mfol, keda__kbt,
        package_name='pandas', module_name='Series')
    if not (isinstance(repeats, types.Integer) or is_iterable_type(repeats) and
        isinstance(repeats.dtype, types.Integer)):
        raise BodoError(
            "Series.repeat(): 'repeats' should be an integer or array of integers"
            )
    if isinstance(repeats, types.Integer):

        def impl_int(S, repeats, axis=None):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            clzh__gzq = bodo.utils.conversion.index_to_array(index)
            nqg__czir = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            jabxl__lpje = bodo.libs.array_kernels.repeat_kernel(clzh__gzq,
                repeats)
            owwu__ykbb = bodo.utils.conversion.index_from_array(jabxl__lpje)
            return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
                owwu__ykbb, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        clzh__gzq = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        nqg__czir = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        jabxl__lpje = bodo.libs.array_kernels.repeat_kernel(clzh__gzq, repeats)
        owwu__ykbb = bodo.utils.conversion.index_from_array(jabxl__lpje)
        return bodo.hiframes.pd_series_ext.init_series(nqg__czir,
            owwu__ykbb, name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        ybq__ihhj = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(ybq__ihhj)
        ebe__diiac = {}
        for hhbvt__hyqt in range(n):
            zrv__finos = bodo.utils.conversion.box_if_dt64(ybq__ihhj[
                hhbvt__hyqt])
            ebe__diiac[index[hhbvt__hyqt]] = zrv__finos
        return ebe__diiac
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    mwlhm__gzoqz = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            urptw__myeip = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(mwlhm__gzoqz)
    elif is_literal_type(name):
        urptw__myeip = get_literal_value(name)
    else:
        raise_bodo_error(mwlhm__gzoqz)
    urptw__myeip = 0 if urptw__myeip is None else urptw__myeip

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            (urptw__myeip,))
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
