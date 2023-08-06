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
            lmhbr__rycp = list()
            for ggx__dlf in range(len(S)):
                lmhbr__rycp.append(S.iat[ggx__dlf])
            return lmhbr__rycp
        return impl_float

    def impl(S):
        lmhbr__rycp = list()
        for ggx__dlf in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, ggx__dlf):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            lmhbr__rycp.append(S.iat[ggx__dlf])
        return lmhbr__rycp
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    jxbju__zduyv = dict(dtype=dtype, copy=copy, na_value=na_value)
    lae__ifmvw = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    jxbju__zduyv = dict(name=name, inplace=inplace)
    lae__ifmvw = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', jxbju__zduyv, lae__ifmvw,
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
    vfc__iyfot = get_name_literal(S.index.name_typ, True, series_name)
    columns = [vfc__iyfot, series_name]
    zaet__qrwld = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    zaet__qrwld += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    zaet__qrwld += """    index = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S))
"""
    zaet__qrwld += """    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)
"""
    zaet__qrwld += '    col_var = {}\n'.format(gen_const_tup(columns))
    zaet__qrwld += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe((index, arr), df_index, col_var)
"""
    unl__vor = {}
    exec(zaet__qrwld, {'bodo': bodo}, unl__vor)
    zivru__dic = unl__vor['_impl']
    return zivru__dic


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nofp__jsiu = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu, index, name)
    return impl


@overload_method(SeriesType, 'round', inline='always', no_unliteral=True)
def overload_series_round(S, decimals=0):

    def impl(S, decimals=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(arr)
        nofp__jsiu = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for ggx__dlf in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[ggx__dlf]):
                bodo.libs.array_kernels.setna(nofp__jsiu, ggx__dlf)
            else:
                nofp__jsiu[ggx__dlf] = np.round(arr[ggx__dlf], decimals)
        return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu, index, name)
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    jxbju__zduyv = dict(level=level, numeric_only=numeric_only)
    lae__ifmvw = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', jxbju__zduyv, lae__ifmvw,
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
    jxbju__zduyv = dict(level=level, numeric_only=numeric_only)
    lae__ifmvw = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', jxbju__zduyv, lae__ifmvw,
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
    jxbju__zduyv = dict(axis=axis, bool_only=bool_only, skipna=skipna,
        level=level)
    lae__ifmvw = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        qumb__umh = 0
        for ggx__dlf in numba.parfors.parfor.internal_prange(len(A)):
            yef__cxpny = 0
            if not bodo.libs.array_kernels.isna(A, ggx__dlf):
                yef__cxpny = int(A[ggx__dlf])
            qumb__umh += yef__cxpny
        return qumb__umh != 0
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
        jdz__jbw = bodo.hiframes.pd_series_ext.get_series_data(S)
        pnlrw__uul = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        qumb__umh = 0
        for ggx__dlf in numba.parfors.parfor.internal_prange(len(jdz__jbw)):
            yef__cxpny = 0
            vvvmg__hlhp = bodo.libs.array_kernels.isna(jdz__jbw, ggx__dlf)
            rujm__mmzc = bodo.libs.array_kernels.isna(pnlrw__uul, ggx__dlf)
            if (vvvmg__hlhp and not rujm__mmzc or not vvvmg__hlhp and
                rujm__mmzc):
                yef__cxpny = 1
            elif not vvvmg__hlhp:
                if jdz__jbw[ggx__dlf] != pnlrw__uul[ggx__dlf]:
                    yef__cxpny = 1
            qumb__umh += yef__cxpny
        return qumb__umh == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    jxbju__zduyv = dict(axis=axis, bool_only=bool_only, skipna=skipna,
        level=level)
    lae__ifmvw = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        qumb__umh = 0
        for ggx__dlf in numba.parfors.parfor.internal_prange(len(A)):
            yef__cxpny = 0
            if not bodo.libs.array_kernels.isna(A, ggx__dlf):
                yef__cxpny = int(not A[ggx__dlf])
            qumb__umh += yef__cxpny
        return qumb__umh == 0
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    jxbju__zduyv = dict(level=level)
    lae__ifmvw = dict(level=None)
    check_unsupported_args('Series.mad', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    fzne__lgpw = types.float64
    oudh__rhy = types.float64
    if S.dtype == types.float32:
        fzne__lgpw = types.float32
        oudh__rhy = types.float32
    tmin__xzh = fzne__lgpw(0)
    zcg__rbiz = oudh__rhy(0)
    fxifu__fdyef = oudh__rhy(1)

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        wrt__kmfu = tmin__xzh
        qumb__umh = zcg__rbiz
        for ggx__dlf in numba.parfors.parfor.internal_prange(len(A)):
            yef__cxpny = tmin__xzh
            epong__jpx = zcg__rbiz
            if not bodo.libs.array_kernels.isna(A, ggx__dlf) or not skipna:
                yef__cxpny = A[ggx__dlf]
                epong__jpx = fxifu__fdyef
            wrt__kmfu += yef__cxpny
            qumb__umh += epong__jpx
        jzud__eay = bodo.hiframes.series_kernels._mean_handle_nan(wrt__kmfu,
            qumb__umh)
        vovqw__ivj = tmin__xzh
        for ggx__dlf in numba.parfors.parfor.internal_prange(len(A)):
            yef__cxpny = tmin__xzh
            if not bodo.libs.array_kernels.isna(A, ggx__dlf) or not skipna:
                yef__cxpny = abs(A[ggx__dlf] - jzud__eay)
            vovqw__ivj += yef__cxpny
        ajw__adfaw = bodo.hiframes.series_kernels._mean_handle_nan(vovqw__ivj,
            qumb__umh)
        return ajw__adfaw
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    jxbju__zduyv = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    lae__ifmvw = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', jxbju__zduyv, lae__ifmvw,
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
    jxbju__zduyv = dict(level=level, numeric_only=numeric_only)
    lae__ifmvw = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', jxbju__zduyv, lae__ifmvw,
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
        evcbg__aor = 0
        jsn__snyiv = 0
        qumb__umh = 0
        for ggx__dlf in numba.parfors.parfor.internal_prange(len(A)):
            yef__cxpny = 0
            epong__jpx = 0
            if not bodo.libs.array_kernels.isna(A, ggx__dlf) or not skipna:
                yef__cxpny = A[ggx__dlf]
                epong__jpx = 1
            evcbg__aor += yef__cxpny
            jsn__snyiv += yef__cxpny * yef__cxpny
            qumb__umh += epong__jpx
        dysk__tjopc = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            evcbg__aor, jsn__snyiv, qumb__umh, ddof)
        kbk__zubja = bodo.hiframes.series_kernels._sem_handle_nan(dysk__tjopc,
            qumb__umh)
        return kbk__zubja
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    jxbju__zduyv = dict(level=level, numeric_only=numeric_only)
    lae__ifmvw = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.kurtosis(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError(
            "Series.kurtosis(): 'skipna' argument must be a boolean")

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        evcbg__aor = 0.0
        jsn__snyiv = 0.0
        zzti__ape = 0.0
        ztjv__jxgo = 0.0
        qumb__umh = 0
        for ggx__dlf in numba.parfors.parfor.internal_prange(len(A)):
            yef__cxpny = 0.0
            epong__jpx = 0
            if not bodo.libs.array_kernels.isna(A, ggx__dlf) or not skipna:
                yef__cxpny = np.float64(A[ggx__dlf])
                epong__jpx = 1
            evcbg__aor += yef__cxpny
            jsn__snyiv += yef__cxpny ** 2
            zzti__ape += yef__cxpny ** 3
            ztjv__jxgo += yef__cxpny ** 4
            qumb__umh += epong__jpx
        dysk__tjopc = bodo.hiframes.series_kernels.compute_kurt(evcbg__aor,
            jsn__snyiv, zzti__ape, ztjv__jxgo, qumb__umh)
        return dysk__tjopc
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    jxbju__zduyv = dict(level=level, numeric_only=numeric_only)
    lae__ifmvw = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.skew(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.skew(): skipna argument must be a boolean')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        evcbg__aor = 0.0
        jsn__snyiv = 0.0
        zzti__ape = 0.0
        qumb__umh = 0
        for ggx__dlf in numba.parfors.parfor.internal_prange(len(A)):
            yef__cxpny = 0.0
            epong__jpx = 0
            if not bodo.libs.array_kernels.isna(A, ggx__dlf) or not skipna:
                yef__cxpny = np.float64(A[ggx__dlf])
                epong__jpx = 1
            evcbg__aor += yef__cxpny
            jsn__snyiv += yef__cxpny ** 2
            zzti__ape += yef__cxpny ** 3
            qumb__umh += epong__jpx
        dysk__tjopc = bodo.hiframes.series_kernels.compute_skew(evcbg__aor,
            jsn__snyiv, zzti__ape, qumb__umh)
        return dysk__tjopc
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    jxbju__zduyv = dict(level=level, numeric_only=numeric_only)
    lae__ifmvw = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', jxbju__zduyv, lae__ifmvw,
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
    jxbju__zduyv = dict(level=level, numeric_only=numeric_only)
    lae__ifmvw = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', jxbju__zduyv, lae__ifmvw,
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
        jdz__jbw = bodo.hiframes.pd_series_ext.get_series_data(S)
        pnlrw__uul = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        ktujm__ogwex = 0
        for ggx__dlf in numba.parfors.parfor.internal_prange(len(jdz__jbw)):
            pkd__ynfgp = jdz__jbw[ggx__dlf]
            tmbgp__azbna = pnlrw__uul[ggx__dlf]
            ktujm__ogwex += pkd__ynfgp * tmbgp__azbna
        return ktujm__ogwex
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    jxbju__zduyv = dict(skipna=skipna)
    lae__ifmvw = dict(skipna=True)
    check_unsupported_args('Series.cumsum', jxbju__zduyv, lae__ifmvw,
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
    jxbju__zduyv = dict(skipna=skipna)
    lae__ifmvw = dict(skipna=True)
    check_unsupported_args('Series.cumprod', jxbju__zduyv, lae__ifmvw,
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
    jxbju__zduyv = dict(skipna=skipna)
    lae__ifmvw = dict(skipna=True)
    check_unsupported_args('Series.cummin', jxbju__zduyv, lae__ifmvw,
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
    jxbju__zduyv = dict(skipna=skipna)
    lae__ifmvw = dict(skipna=True)
    check_unsupported_args('Series.cummax', jxbju__zduyv, lae__ifmvw,
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
    jxbju__zduyv = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    lae__ifmvw = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        xbhf__rpj = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, xbhf__rpj, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    jxbju__zduyv = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    lae__ifmvw = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', jxbju__zduyv, lae__ifmvw,
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
    jxbju__zduyv = dict(level=level)
    lae__ifmvw = dict(level=None)
    check_unsupported_args('Series.count', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    jxbju__zduyv = dict(method=method, min_periods=min_periods)
    lae__ifmvw = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        ssqij__lzxcq = S.sum()
        ualp__fpo = other.sum()
        a = n * (S * other).sum() - ssqij__lzxcq * ualp__fpo
        mnjvn__dsa = n * (S ** 2).sum() - ssqij__lzxcq ** 2
        znln__lbhj = n * (other ** 2).sum() - ualp__fpo ** 2
        return a / np.sqrt(mnjvn__dsa * znln__lbhj)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    jxbju__zduyv = dict(min_periods=min_periods)
    lae__ifmvw = dict(min_periods=None)
    check_unsupported_args('Series.cov', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')

    def impl(S, other, min_periods=None, ddof=1):
        ssqij__lzxcq = S.mean()
        ualp__fpo = other.mean()
        haivc__qno = ((S - ssqij__lzxcq) * (other - ualp__fpo)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(haivc__qno, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            flu__qsik = np.sign(sum_val)
            return np.inf * flu__qsik
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    jxbju__zduyv = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    lae__ifmvw = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', jxbju__zduyv, lae__ifmvw,
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
    jxbju__zduyv = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    lae__ifmvw = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', jxbju__zduyv, lae__ifmvw,
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
    jxbju__zduyv = dict(axis=axis, skipna=skipna)
    lae__ifmvw = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', jxbju__zduyv, lae__ifmvw,
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
    jxbju__zduyv = dict(axis=axis, skipna=skipna)
    lae__ifmvw = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', jxbju__zduyv, lae__ifmvw,
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
    jxbju__zduyv = dict(level=level, numeric_only=numeric_only)
    lae__ifmvw = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', jxbju__zduyv, lae__ifmvw,
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
        qpvt__pbb = arr[:n]
        xcyr__ydci = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(qpvt__pbb,
            xcyr__ydci, name)
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
        tgsz__xxy = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        qpvt__pbb = arr[tgsz__xxy:]
        xcyr__ydci = index[tgsz__xxy:]
        return bodo.hiframes.pd_series_ext.init_series(qpvt__pbb,
            xcyr__ydci, name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    xqpx__exgk = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in xqpx__exgk:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            cgbpf__npxb = index[0]
            tpf__vgdi = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                cgbpf__npxb, False))
        else:
            tpf__vgdi = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        qpvt__pbb = arr[:tpf__vgdi]
        xcyr__ydci = index[:tpf__vgdi]
        return bodo.hiframes.pd_series_ext.init_series(qpvt__pbb,
            xcyr__ydci, name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    xqpx__exgk = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in xqpx__exgk:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            qxwrq__euutd = index[-1]
            tpf__vgdi = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                qxwrq__euutd, True))
        else:
            tpf__vgdi = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        qpvt__pbb = arr[len(arr) - tpf__vgdi:]
        xcyr__ydci = index[len(arr) - tpf__vgdi:]
        return bodo.hiframes.pd_series_ext.init_series(qpvt__pbb,
            xcyr__ydci, name)
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    jxbju__zduyv = dict(keep=keep)
    lae__ifmvw = dict(keep='first')
    check_unsupported_args('Series.nlargest', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        yku__jhfj = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nofp__jsiu, lqfv__zjj = bodo.libs.array_kernels.nlargest(arr,
            yku__jhfj, n, True, bodo.hiframes.series_kernels.gt_f)
        xqqw__myot = bodo.utils.conversion.convert_to_index(lqfv__zjj)
        return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
            xqqw__myot, name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    jxbju__zduyv = dict(keep=keep)
    lae__ifmvw = dict(keep='first')
    check_unsupported_args('Series.nsmallest', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        yku__jhfj = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nofp__jsiu, lqfv__zjj = bodo.libs.array_kernels.nlargest(arr,
            yku__jhfj, n, False, bodo.hiframes.series_kernels.lt_f)
        xqqw__myot = bodo.utils.conversion.convert_to_index(lqfv__zjj)
        return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
            xqqw__myot, name)
    return impl


@overload_method(SeriesType, 'notnull', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'notna', inline='always', no_unliteral=True)
def overload_series_notna(S):
    return lambda S: S.isna() == False


@overload_method(SeriesType, 'astype', inline='always', no_unliteral=True)
def overload_series_astype(S, dtype, copy=True, errors='raise',
    _bodo_nan_to_str=True):
    jxbju__zduyv = dict(errors=errors)
    lae__ifmvw = dict(errors='raise')
    check_unsupported_args('Series.astype', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "Series.astype(): 'dtype' when passed as string must be a constant value"
            )

    def impl(S, dtype, copy=True, errors='raise', _bodo_nan_to_str=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nofp__jsiu = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu, index, name)
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    jxbju__zduyv = dict(axis=axis, is_copy=is_copy)
    lae__ifmvw = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        nzy__iutf = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[nzy__iutf],
            index[nzy__iutf], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    jxbju__zduyv = dict(axis=axis, kind=kind, order=order)
    lae__ifmvw = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        dygiu__ste = S.notna().values
        if not dygiu__ste.all():
            nofp__jsiu = np.full(n, -1, np.int64)
            nofp__jsiu[dygiu__ste] = argsort(arr[dygiu__ste])
        else:
            nofp__jsiu = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu, index, name)
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    jxbju__zduyv = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    lae__ifmvw = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', jxbju__zduyv, lae__ifmvw,
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
        zmsv__etp = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, ('$_bodo_col3_',))
        jkzln__wnkya = zmsv__etp.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        nofp__jsiu = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            jkzln__wnkya, 0)
        xqqw__myot = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            jkzln__wnkya)
        return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
            xqqw__myot, name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    jxbju__zduyv = dict(axis=axis, inplace=inplace, kind=kind, ignore_index
        =ignore_index, key=key)
    lae__ifmvw = dict(axis=0, inplace=False, kind='quicksort', ignore_index
        =False, key=None)
    check_unsupported_args('Series.sort_values', jxbju__zduyv, lae__ifmvw,
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
        zmsv__etp = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, ('$_bodo_col_',))
        jkzln__wnkya = zmsv__etp.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        nofp__jsiu = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            jkzln__wnkya, 0)
        xqqw__myot = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            jkzln__wnkya)
        return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
            xqqw__myot, name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    wkbki__ago = is_overload_true(is_nullable)
    zaet__qrwld = (
        'def impl(bins, arr, is_nullable=True, include_lowest=True):\n')
    zaet__qrwld += '  numba.parfors.parfor.init_prange()\n'
    zaet__qrwld += '  n = len(arr)\n'
    if wkbki__ago:
        zaet__qrwld += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        zaet__qrwld += '  out_arr = np.empty(n, np.int64)\n'
    zaet__qrwld += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    zaet__qrwld += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if wkbki__ago:
        zaet__qrwld += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        zaet__qrwld += '      out_arr[i] = -1\n'
    zaet__qrwld += '      continue\n'
    zaet__qrwld += '    val = arr[i]\n'
    zaet__qrwld += '    if include_lowest and val == bins[0]:\n'
    zaet__qrwld += '      ind = 1\n'
    zaet__qrwld += '    else:\n'
    zaet__qrwld += '      ind = np.searchsorted(bins, val)\n'
    zaet__qrwld += '    if ind == 0 or ind == len(bins):\n'
    if wkbki__ago:
        zaet__qrwld += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        zaet__qrwld += '      out_arr[i] = -1\n'
    zaet__qrwld += '    else:\n'
    zaet__qrwld += '      out_arr[i] = ind - 1\n'
    zaet__qrwld += '  return out_arr\n'
    unl__vor = {}
    exec(zaet__qrwld, {'bodo': bodo, 'np': np, 'numba': numba}, unl__vor)
    impl = unl__vor['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        ujc__cxfw, tkomc__cupvx = np.divmod(x, 1)
        if ujc__cxfw == 0:
            spg__cypm = -int(np.floor(np.log10(abs(tkomc__cupvx)))
                ) - 1 + precision
        else:
            spg__cypm = precision
        return np.around(x, spg__cypm)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        rwz__rtry = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(rwz__rtry)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        yflhz__wknv = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            zxhkq__sphy = bins.copy()
            if right and include_lowest:
                zxhkq__sphy[0] = zxhkq__sphy[0] - yflhz__wknv
            otrmt__iedzs = bodo.libs.interval_arr_ext.init_interval_array(
                zxhkq__sphy[:-1], zxhkq__sphy[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(otrmt__iedzs,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        zxhkq__sphy = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            zxhkq__sphy[0] = zxhkq__sphy[0] - 10.0 ** -precision
        otrmt__iedzs = bodo.libs.interval_arr_ext.init_interval_array(
            zxhkq__sphy[:-1], zxhkq__sphy[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(otrmt__iedzs,
            None)
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        ehfl__orf = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        qog__uhqxx = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        nofp__jsiu = np.zeros(nbins, np.int64)
        for ggx__dlf in range(len(ehfl__orf)):
            nofp__jsiu[qog__uhqxx[ggx__dlf]] = ehfl__orf[ggx__dlf]
        return nofp__jsiu
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
            lvshr__fkkp = (max_val - min_val) * 0.001
            if right:
                bins[0] -= lvshr__fkkp
            else:
                bins[-1] += lvshr__fkkp
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    jxbju__zduyv = dict(dropna=dropna)
    lae__ifmvw = dict(dropna=True)
    check_unsupported_args('Series.value_counts', jxbju__zduyv, lae__ifmvw,
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
    lxg__eohrc = not is_overload_none(bins)
    zaet__qrwld = 'def impl(\n'
    zaet__qrwld += '    S,\n'
    zaet__qrwld += '    normalize=False,\n'
    zaet__qrwld += '    sort=True,\n'
    zaet__qrwld += '    ascending=False,\n'
    zaet__qrwld += '    bins=None,\n'
    zaet__qrwld += '    dropna=True,\n'
    zaet__qrwld += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    zaet__qrwld += '):\n'
    zaet__qrwld += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    zaet__qrwld += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    zaet__qrwld += (
        '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
    if lxg__eohrc:
        zaet__qrwld += '    right = True\n'
        zaet__qrwld += _gen_bins_handling(bins, S.dtype)
        zaet__qrwld += '    arr = get_bin_inds(bins, arr)\n'
    zaet__qrwld += (
        '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
    zaet__qrwld += "        (arr,), index, ('$_bodo_col2_',)\n"
    zaet__qrwld += '    )\n'
    zaet__qrwld += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if lxg__eohrc:
        zaet__qrwld += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        zaet__qrwld += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        zaet__qrwld += '    index = get_bin_labels(bins)\n'
    else:
        zaet__qrwld += """    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)
"""
        zaet__qrwld += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        zaet__qrwld += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        zaet__qrwld += '    )\n'
        zaet__qrwld += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    zaet__qrwld += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        zaet__qrwld += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        vroc__pqqn = 'len(S)' if lxg__eohrc else 'count_arr.sum()'
        zaet__qrwld += f'    res = res / float({vroc__pqqn})\n'
    zaet__qrwld += '    return res\n'
    unl__vor = {}
    exec(zaet__qrwld, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, unl__vor)
    impl = unl__vor['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    zaet__qrwld = ''
    if isinstance(bins, types.Integer):
        zaet__qrwld += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        zaet__qrwld += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            zaet__qrwld += '    min_val = min_val.value\n'
            zaet__qrwld += '    max_val = max_val.value\n'
        zaet__qrwld += (
            '    bins = compute_bins(bins, min_val, max_val, right)\n')
        if dtype == bodo.datetime64ns:
            zaet__qrwld += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        zaet__qrwld += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return zaet__qrwld


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    jxbju__zduyv = dict(right=right, labels=labels, retbins=retbins,
        precision=precision, duplicates=duplicates, ordered=ordered)
    lae__ifmvw = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='General')
    zaet__qrwld = 'def impl(\n'
    zaet__qrwld += '    x,\n'
    zaet__qrwld += '    bins,\n'
    zaet__qrwld += '    right=True,\n'
    zaet__qrwld += '    labels=None,\n'
    zaet__qrwld += '    retbins=False,\n'
    zaet__qrwld += '    precision=3,\n'
    zaet__qrwld += '    include_lowest=False,\n'
    zaet__qrwld += "    duplicates='raise',\n"
    zaet__qrwld += '    ordered=True\n'
    zaet__qrwld += '):\n'
    if isinstance(x, SeriesType):
        zaet__qrwld += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        zaet__qrwld += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        zaet__qrwld += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        zaet__qrwld += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    zaet__qrwld += _gen_bins_handling(bins, x.dtype)
    zaet__qrwld += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    zaet__qrwld += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    zaet__qrwld += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    zaet__qrwld += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        zaet__qrwld += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        zaet__qrwld += '    return res\n'
    else:
        zaet__qrwld += '    return out_arr\n'
    unl__vor = {}
    exec(zaet__qrwld, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, unl__vor)
    impl = unl__vor['impl']
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
    jxbju__zduyv = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    lae__ifmvw = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        avio__lfu = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, avio__lfu)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    jxbju__zduyv = dict(axis=axis, sort=sort, group_keys=group_keys,
        squeeze=squeeze, observed=observed, dropna=dropna)
    lae__ifmvw = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', jxbju__zduyv, lae__ifmvw,
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
            wprf__ydzgb = bodo.utils.conversion.coerce_to_array(index)
            zmsv__etp = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                wprf__ydzgb, arr), index, (' ', ''))
            return zmsv__etp.groupby(' ')['']
        return impl_index
    rdo__qeyyh = by
    if isinstance(by, SeriesType):
        rdo__qeyyh = by.data
    if isinstance(rdo__qeyyh, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        wprf__ydzgb = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        zmsv__etp = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            wprf__ydzgb, arr), index, (' ', ''))
        return zmsv__etp.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    jxbju__zduyv = dict(verify_integrity=verify_integrity)
    lae__ifmvw = dict(verify_integrity=False)
    check_unsupported_args('Series.append', jxbju__zduyv, lae__ifmvw,
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
            ddz__svvug = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            nofp__jsiu = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(nofp__jsiu, A, ddz__svvug, False)
            return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                index, name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nofp__jsiu = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu, index, name)
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    jxbju__zduyv = dict(interpolation=interpolation)
    lae__ifmvw = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            nofp__jsiu = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                index, name)
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
        czahr__jrm = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(czahr__jrm, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    jxbju__zduyv = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    lae__ifmvw = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', jxbju__zduyv, lae__ifmvw,
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
        lcbm__qnaol = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        lcbm__qnaol = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    zaet__qrwld = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {lcbm__qnaol}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    ouf__ulo = dict()
    exec(zaet__qrwld, {'bodo': bodo, 'numba': numba}, ouf__ulo)
    pup__cxmf = ouf__ulo['impl']
    return pup__cxmf


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        lcbm__qnaol = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        lcbm__qnaol = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    zaet__qrwld = 'def impl(S,\n'
    zaet__qrwld += '     value=None,\n'
    zaet__qrwld += '    method=None,\n'
    zaet__qrwld += '    axis=None,\n'
    zaet__qrwld += '    inplace=False,\n'
    zaet__qrwld += '    limit=None,\n'
    zaet__qrwld += '   downcast=None,\n'
    zaet__qrwld += '):\n'
    zaet__qrwld += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    zaet__qrwld += '    n = len(in_arr)\n'
    zaet__qrwld += f'    out_arr = {lcbm__qnaol}(n, -1)\n'
    zaet__qrwld += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    zaet__qrwld += '        s = in_arr[j]\n'
    zaet__qrwld += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    zaet__qrwld += '            s = value\n'
    zaet__qrwld += '        out_arr[j] = s\n'
    zaet__qrwld += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    ouf__ulo = dict()
    exec(zaet__qrwld, {'bodo': bodo, 'numba': numba}, ouf__ulo)
    pup__cxmf = ouf__ulo['impl']
    return pup__cxmf


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    onqc__rtcbg = bodo.hiframes.pd_series_ext.get_series_data(S)
    avk__mrdeh = bodo.hiframes.pd_series_ext.get_series_data(value)
    for ggx__dlf in numba.parfors.parfor.internal_prange(len(onqc__rtcbg)):
        s = onqc__rtcbg[ggx__dlf]
        if bodo.libs.array_kernels.isna(onqc__rtcbg, ggx__dlf
            ) and not bodo.libs.array_kernels.isna(avk__mrdeh, ggx__dlf):
            s = avk__mrdeh[ggx__dlf]
        onqc__rtcbg[ggx__dlf] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    onqc__rtcbg = bodo.hiframes.pd_series_ext.get_series_data(S)
    for ggx__dlf in numba.parfors.parfor.internal_prange(len(onqc__rtcbg)):
        s = onqc__rtcbg[ggx__dlf]
        if bodo.libs.array_kernels.isna(onqc__rtcbg, ggx__dlf):
            s = value
        onqc__rtcbg[ggx__dlf] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    onqc__rtcbg = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    avk__mrdeh = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(onqc__rtcbg)
    nofp__jsiu = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for fcv__dgb in numba.parfors.parfor.internal_prange(n):
        s = onqc__rtcbg[fcv__dgb]
        if bodo.libs.array_kernels.isna(onqc__rtcbg, fcv__dgb
            ) and not bodo.libs.array_kernels.isna(avk__mrdeh, fcv__dgb):
            s = avk__mrdeh[fcv__dgb]
        nofp__jsiu[fcv__dgb] = s
        if bodo.libs.array_kernels.isna(onqc__rtcbg, fcv__dgb
            ) and bodo.libs.array_kernels.isna(avk__mrdeh, fcv__dgb):
            bodo.libs.array_kernels.setna(nofp__jsiu, fcv__dgb)
    return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    onqc__rtcbg = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    avk__mrdeh = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(onqc__rtcbg)
    nofp__jsiu = bodo.utils.utils.alloc_type(n, onqc__rtcbg.dtype, (-1,))
    for ggx__dlf in numba.parfors.parfor.internal_prange(n):
        s = onqc__rtcbg[ggx__dlf]
        if bodo.libs.array_kernels.isna(onqc__rtcbg, ggx__dlf
            ) and not bodo.libs.array_kernels.isna(avk__mrdeh, ggx__dlf):
            s = avk__mrdeh[ggx__dlf]
        nofp__jsiu[ggx__dlf] = s
    return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    jxbju__zduyv = dict(limit=limit, downcast=downcast)
    lae__ifmvw = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')
    xio__pbv = not is_overload_none(value)
    tnq__iuyv = not is_overload_none(method)
    if xio__pbv and tnq__iuyv:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not xio__pbv and not tnq__iuyv:
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
    if tnq__iuyv:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        pyh__mvepe = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(pyh__mvepe)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(pyh__mvepe)
    rifzh__mqkvb = element_type(S.data)
    kxr__tuzrb = None
    if xio__pbv:
        kxr__tuzrb = element_type(types.unliteral(value))
    if kxr__tuzrb and not can_replace(rifzh__mqkvb, kxr__tuzrb):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {kxr__tuzrb} with series type {rifzh__mqkvb}'
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
        vpm__wzsyn = S.data
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                onqc__rtcbg = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                avk__mrdeh = bodo.hiframes.pd_series_ext.get_series_data(value)
                n = len(onqc__rtcbg)
                nofp__jsiu = bodo.utils.utils.alloc_type(n, vpm__wzsyn, (-1,))
                for ggx__dlf in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(onqc__rtcbg, ggx__dlf
                        ) and bodo.libs.array_kernels.isna(avk__mrdeh, ggx__dlf
                        ):
                        bodo.libs.array_kernels.setna(nofp__jsiu, ggx__dlf)
                        continue
                    if bodo.libs.array_kernels.isna(onqc__rtcbg, ggx__dlf):
                        nofp__jsiu[ggx__dlf
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            avk__mrdeh[ggx__dlf])
                        continue
                    nofp__jsiu[ggx__dlf
                        ] = bodo.utils.conversion.unbox_if_timestamp(
                        onqc__rtcbg[ggx__dlf])
                return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                    index, name)
            return fillna_series_impl
        if tnq__iuyv:
            zhy__ofg = (types.unicode_type, types.bool_, bodo.datetime64ns,
                bodo.timedelta64ns)
            if not isinstance(rifzh__mqkvb, (types.Integer, types.Float)
                ) and rifzh__mqkvb not in zhy__ofg:
                raise BodoError(
                    f"Series.fillna(): series of type {rifzh__mqkvb} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                onqc__rtcbg = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                nofp__jsiu = bodo.libs.array_kernels.ffill_bfill_arr(
                    onqc__rtcbg, method)
                return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            onqc__rtcbg = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(onqc__rtcbg)
            nofp__jsiu = bodo.utils.utils.alloc_type(n, vpm__wzsyn, (-1,))
            for ggx__dlf in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(onqc__rtcbg[
                    ggx__dlf])
                if bodo.libs.array_kernels.isna(onqc__rtcbg, ggx__dlf):
                    s = value
                nofp__jsiu[ggx__dlf] = s
            return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                index, name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        gfie__sdcqa = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        jxbju__zduyv = dict(limit=limit, downcast=downcast)
        lae__ifmvw = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', jxbju__zduyv,
            lae__ifmvw, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        rifzh__mqkvb = element_type(S.data)
        zhy__ofg = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(rifzh__mqkvb, (types.Integer, types.Float)
            ) and rifzh__mqkvb not in zhy__ofg:
            raise BodoError(
                f'Series.{overload_name}(): series of type {rifzh__mqkvb} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            onqc__rtcbg = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            nofp__jsiu = bodo.libs.array_kernels.ffill_bfill_arr(onqc__rtcbg,
                gfie__sdcqa)
            return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                index, name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        rsogt__fxq = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(
            rsogt__fxq)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        qupav__bhitk = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(qupav__bhitk)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        qupav__bhitk = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(qupav__bhitk)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        qupav__bhitk = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(qupav__bhitk)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    jxbju__zduyv = dict(inplace=inplace, limit=limit, regex=regex, method=
        method)
    wpsz__pwtun = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', jxbju__zduyv, wpsz__pwtun,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    rifzh__mqkvb = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        ere__tdgvr = element_type(to_replace.key_type)
        kxr__tuzrb = element_type(to_replace.value_type)
    else:
        ere__tdgvr = element_type(to_replace)
        kxr__tuzrb = element_type(value)
    ibwuh__eflil = None
    if rifzh__mqkvb != types.unliteral(ere__tdgvr):
        if bodo.utils.typing.equality_always_false(rifzh__mqkvb, types.
            unliteral(ere__tdgvr)
            ) or not bodo.utils.typing.types_equality_exists(rifzh__mqkvb,
            ere__tdgvr):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(rifzh__mqkvb, (types.Float, types.Integer)
            ) or rifzh__mqkvb == np.bool_:
            ibwuh__eflil = rifzh__mqkvb
    if not can_replace(rifzh__mqkvb, types.unliteral(kxr__tuzrb)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    fiie__etq = S.data
    if isinstance(fiie__etq, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            onqc__rtcbg = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(onqc__rtcbg.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        onqc__rtcbg = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(onqc__rtcbg)
        nofp__jsiu = bodo.utils.utils.alloc_type(n, fiie__etq, (-1,))
        ffe__mpyuh = build_replace_dict(to_replace, value, ibwuh__eflil)
        for ggx__dlf in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(onqc__rtcbg, ggx__dlf):
                bodo.libs.array_kernels.setna(nofp__jsiu, ggx__dlf)
                continue
            s = onqc__rtcbg[ggx__dlf]
            if s in ffe__mpyuh:
                s = ffe__mpyuh[s]
            nofp__jsiu[ggx__dlf] = s
        return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu, index, name)
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    txkqv__rby = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    jtpn__kui = is_iterable_type(to_replace)
    foy__gzle = isinstance(value, (types.Number, Decimal128Type)) or value in [
        bodo.string_type, bodo.bytes_type, types.boolean]
    douar__yngt = is_iterable_type(value)
    if txkqv__rby and foy__gzle:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                ffe__mpyuh = {}
                ffe__mpyuh[key_dtype_conv(to_replace)] = value
                return ffe__mpyuh
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            ffe__mpyuh = {}
            ffe__mpyuh[to_replace] = value
            return ffe__mpyuh
        return impl
    if jtpn__kui and foy__gzle:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                ffe__mpyuh = {}
                for yolbg__alkx in to_replace:
                    ffe__mpyuh[key_dtype_conv(yolbg__alkx)] = value
                return ffe__mpyuh
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            ffe__mpyuh = {}
            for yolbg__alkx in to_replace:
                ffe__mpyuh[yolbg__alkx] = value
            return ffe__mpyuh
        return impl
    if jtpn__kui and douar__yngt:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                ffe__mpyuh = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for ggx__dlf in range(len(to_replace)):
                    ffe__mpyuh[key_dtype_conv(to_replace[ggx__dlf])] = value[
                        ggx__dlf]
                return ffe__mpyuh
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            ffe__mpyuh = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for ggx__dlf in range(len(to_replace)):
                ffe__mpyuh[to_replace[ggx__dlf]] = value[ggx__dlf]
            return ffe__mpyuh
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
            nofp__jsiu = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                index, name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nofp__jsiu = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu, index, name)
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    jxbju__zduyv = dict(ignore_index=ignore_index)
    sot__ige = dict(ignore_index=False)
    check_unsupported_args('Series.explode', jxbju__zduyv, sot__ige,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        yku__jhfj = bodo.utils.conversion.index_to_array(index)
        nofp__jsiu, mnj__bghl = bodo.libs.array_kernels.explode(arr, yku__jhfj)
        xqqw__myot = bodo.utils.conversion.index_from_array(mnj__bghl)
        return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
            xqqw__myot, name)
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
            igge__bcoa = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for ggx__dlf in numba.parfors.parfor.internal_prange(n):
                igge__bcoa[ggx__dlf] = np.argmax(a[ggx__dlf])
            return igge__bcoa
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            ckgr__rugq = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for ggx__dlf in numba.parfors.parfor.internal_prange(n):
                ckgr__rugq[ggx__dlf] = np.argmin(a[ggx__dlf])
            return ckgr__rugq
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
    jxbju__zduyv = dict(axis=axis, inplace=inplace, how=how)
    gqq__wur = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', jxbju__zduyv, gqq__wur,
        package_name='pandas', module_name='Series')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            onqc__rtcbg = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            dygiu__ste = S.notna().values
            yku__jhfj = bodo.utils.conversion.extract_index_array(S)
            xqqw__myot = bodo.utils.conversion.convert_to_index(yku__jhfj[
                dygiu__ste])
            nofp__jsiu = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(onqc__rtcbg))
            return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                xqqw__myot, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            onqc__rtcbg = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            yku__jhfj = bodo.utils.conversion.extract_index_array(S)
            dygiu__ste = S.notna().values
            xqqw__myot = bodo.utils.conversion.convert_to_index(yku__jhfj[
                dygiu__ste])
            nofp__jsiu = onqc__rtcbg[dygiu__ste]
            return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                xqqw__myot, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    jxbju__zduyv = dict(freq=freq, axis=axis, fill_value=fill_value)
    lae__ifmvw = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', jxbju__zduyv, lae__ifmvw,
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
        nofp__jsiu = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu, index, name)
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    jxbju__zduyv = dict(fill_method=fill_method, limit=limit, freq=freq)
    lae__ifmvw = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', jxbju__zduyv, lae__ifmvw,
        package_name='pandas', module_name='Series')
    if not is_overload_int(periods):
        raise BodoError(
            'Series.pct_change(): periods argument must be an Integer')

    def impl(S, periods=1, fill_method='pad', limit=None, freq=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nofp__jsiu = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu, index, name)
    return impl


def create_series_mask_where_overload(func_name):

    def overload_series_mask_where(S, cond, other=np.nan, inplace=False,
        axis=None, level=None, errors='raise', try_cast=False):
        _validate_arguments_mask_where(f'Series.{func_name}', S, cond,
            other, inplace, axis, level, errors, try_cast)
        if is_overload_constant_nan(other):
            fhkf__gkbb = 'None'
        else:
            fhkf__gkbb = 'other'
        zaet__qrwld = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            zaet__qrwld += '  cond = ~cond\n'
        zaet__qrwld += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        zaet__qrwld += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        zaet__qrwld += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        zaet__qrwld += f"""  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {fhkf__gkbb})
"""
        zaet__qrwld += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        unl__vor = {}
        exec(zaet__qrwld, {'bodo': bodo, 'np': np}, unl__vor)
        impl = unl__vor['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        rsogt__fxq = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(rsogt__fxq)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, S, cond, other, inplace, axis,
    level, errors, try_cast):
    jxbju__zduyv = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    lae__ifmvw = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', jxbju__zduyv, lae__ifmvw,
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
    fmv__bos = is_overload_constant_nan(other)
    if not (is_default or fmv__bos or is_scalar_type(other) or isinstance(
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
            lofef__eolvr = arr.dtype.elem_type
        else:
            lofef__eolvr = arr.dtype
        if is_iterable_type(other):
            lsyae__uky = other.dtype
        elif fmv__bos:
            lsyae__uky = types.float64
        else:
            lsyae__uky = types.unliteral(other)
        if not fmv__bos and not is_common_scalar_dtype([lofef__eolvr,
            lsyae__uky]):
            raise BodoError(
                f"{func_name}() series and 'other' must share a common type.")


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        jxbju__zduyv = dict(level=level, axis=axis)
        lae__ifmvw = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__),
            jxbju__zduyv, lae__ifmvw, package_name='pandas', module_name=
            'Series')
        pyvs__ofln = other == string_type or is_overload_constant_str(other)
        ylfb__xktjk = is_iterable_type(other) and other.dtype == string_type
        cpq__eqsgx = S.dtype == string_type and (op == operator.add and (
            pyvs__ofln or ylfb__xktjk) or op == operator.mul and isinstance
            (other, types.Integer))
        xznny__xex = S.dtype == bodo.timedelta64ns
        gbq__ylyi = S.dtype == bodo.datetime64ns
        vkt__zlj = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        plnb__yymgg = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        pmqz__xev = xznny__xex and (vkt__zlj or plnb__yymgg
            ) or gbq__ylyi and vkt__zlj
        pmqz__xev = pmqz__xev and op == operator.add
        if not (isinstance(S.dtype, types.Number) or cpq__eqsgx or pmqz__xev):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        ujm__wsyp = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            fiie__etq = ujm__wsyp.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and fiie__etq == types.Array(types.bool_, 1, 'C'):
                fiie__etq = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                nofp__jsiu = bodo.utils.utils.alloc_type(n, fiie__etq, (-1,))
                for ggx__dlf in numba.parfors.parfor.internal_prange(n):
                    yaf__hapq = bodo.libs.array_kernels.isna(arr, ggx__dlf)
                    if yaf__hapq:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(nofp__jsiu, ggx__dlf)
                        else:
                            nofp__jsiu[ggx__dlf] = op(fill_value, other)
                    else:
                        nofp__jsiu[ggx__dlf] = op(arr[ggx__dlf], other)
                return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        fiie__etq = ujm__wsyp.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and fiie__etq == types.Array(
            types.bool_, 1, 'C'):
            fiie__etq = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            jlp__wfrs = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            nofp__jsiu = bodo.utils.utils.alloc_type(n, fiie__etq, (-1,))
            for ggx__dlf in numba.parfors.parfor.internal_prange(n):
                yaf__hapq = bodo.libs.array_kernels.isna(arr, ggx__dlf)
                eihz__wbedg = bodo.libs.array_kernels.isna(jlp__wfrs, ggx__dlf)
                if yaf__hapq and eihz__wbedg:
                    bodo.libs.array_kernels.setna(nofp__jsiu, ggx__dlf)
                elif yaf__hapq:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(nofp__jsiu, ggx__dlf)
                    else:
                        nofp__jsiu[ggx__dlf] = op(fill_value, jlp__wfrs[
                            ggx__dlf])
                elif eihz__wbedg:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(nofp__jsiu, ggx__dlf)
                    else:
                        nofp__jsiu[ggx__dlf] = op(arr[ggx__dlf], fill_value)
                else:
                    nofp__jsiu[ggx__dlf] = op(arr[ggx__dlf], jlp__wfrs[
                        ggx__dlf])
            return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                index, name)
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
        ujm__wsyp = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            fiie__etq = ujm__wsyp.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and fiie__etq == types.Array(types.bool_, 1, 'C'):
                fiie__etq = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                nofp__jsiu = bodo.utils.utils.alloc_type(n, fiie__etq, None)
                for ggx__dlf in numba.parfors.parfor.internal_prange(n):
                    yaf__hapq = bodo.libs.array_kernels.isna(arr, ggx__dlf)
                    if yaf__hapq:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(nofp__jsiu, ggx__dlf)
                        else:
                            nofp__jsiu[ggx__dlf] = op(other, fill_value)
                    else:
                        nofp__jsiu[ggx__dlf] = op(other, arr[ggx__dlf])
                return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        fiie__etq = ujm__wsyp.resolve_function_type(op, args, {}).return_type
        if isinstance(S.data, IntegerArrayType) and fiie__etq == types.Array(
            types.bool_, 1, 'C'):
            fiie__etq = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            jlp__wfrs = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            nofp__jsiu = bodo.utils.utils.alloc_type(n, fiie__etq, None)
            for ggx__dlf in numba.parfors.parfor.internal_prange(n):
                yaf__hapq = bodo.libs.array_kernels.isna(arr, ggx__dlf)
                eihz__wbedg = bodo.libs.array_kernels.isna(jlp__wfrs, ggx__dlf)
                nofp__jsiu[ggx__dlf] = op(jlp__wfrs[ggx__dlf], arr[ggx__dlf])
                if yaf__hapq and eihz__wbedg:
                    bodo.libs.array_kernels.setna(nofp__jsiu, ggx__dlf)
                elif yaf__hapq:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(nofp__jsiu, ggx__dlf)
                    else:
                        nofp__jsiu[ggx__dlf] = op(jlp__wfrs[ggx__dlf],
                            fill_value)
                elif eihz__wbedg:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(nofp__jsiu, ggx__dlf)
                    else:
                        nofp__jsiu[ggx__dlf] = op(fill_value, arr[ggx__dlf])
                else:
                    nofp__jsiu[ggx__dlf] = op(jlp__wfrs[ggx__dlf], arr[
                        ggx__dlf])
            return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                index, name)
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
    for op, jchu__zhqzd in explicit_binop_funcs_two_ways.items():
        for name in jchu__zhqzd:
            rsogt__fxq = create_explicit_binary_op_overload(op)
            jzcde__jrwkd = create_explicit_binary_reverse_op_overload(op)
            choi__nvuqk = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(rsogt__fxq)
            overload_method(SeriesType, choi__nvuqk, no_unliteral=True)(
                jzcde__jrwkd)
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        rsogt__fxq = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(rsogt__fxq)
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
                ohbgz__abyta = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                nofp__jsiu = dt64_arr_sub(arr, ohbgz__abyta)
                return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
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
                nofp__jsiu = np.empty(n, np.dtype('datetime64[ns]'))
                for ggx__dlf in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, ggx__dlf):
                        bodo.libs.array_kernels.setna(nofp__jsiu, ggx__dlf)
                        continue
                    rsr__hgr = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[ggx__dlf]))
                    nbftn__pscfh = op(rsr__hgr, rhs)
                    nofp__jsiu[ggx__dlf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        nbftn__pscfh.value)
                return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
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
                    ohbgz__abyta = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    nofp__jsiu = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(ohbgz__abyta))
                    return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ohbgz__abyta = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                nofp__jsiu = op(arr, ohbgz__abyta)
                return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    afggq__aqprt = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    nofp__jsiu = op(bodo.utils.conversion.
                        unbox_if_timestamp(afggq__aqprt), arr)
                    return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                afggq__aqprt = (bodo.utils.conversion.
                    get_array_if_series_or_index(lhs))
                nofp__jsiu = op(afggq__aqprt, arr)
                return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        rsogt__fxq = create_binary_op_overload(op)
        overload(op)(rsogt__fxq)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    onvfq__ewrx = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, onvfq__ewrx)
        for ggx__dlf in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, ggx__dlf
                ) or bodo.libs.array_kernels.isna(arg2, ggx__dlf):
                bodo.libs.array_kernels.setna(S, ggx__dlf)
                continue
            S[ggx__dlf
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                ggx__dlf]) - bodo.hiframes.pd_timestamp_ext.dt64_to_integer
                (arg2[ggx__dlf]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                jlp__wfrs = bodo.utils.conversion.get_array_if_series_or_index(
                    other)
                op(arr, jlp__wfrs)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        rsogt__fxq = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(rsogt__fxq)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                nofp__jsiu = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        rsogt__fxq = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(rsogt__fxq)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    nofp__jsiu = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
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
                    jlp__wfrs = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    nofp__jsiu = ufunc(arr, jlp__wfrs)
                    return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    jlp__wfrs = bodo.hiframes.pd_series_ext.get_series_data(S2)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    nofp__jsiu = ufunc(arr, jlp__wfrs)
                    return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        rsogt__fxq = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(rsogt__fxq)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        mfnvx__uda = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.copy(),)
            )
        oicl__zuf = np.arange(n),
        bodo.libs.timsort.sort(mfnvx__uda, 0, n, oicl__zuf)
        return oicl__zuf[0]
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
        onz__hrclk = get_overload_const_str(downcast)
        if onz__hrclk in ('integer', 'signed'):
            out_dtype = types.int64
        elif onz__hrclk == 'unsigned':
            out_dtype = types.uint64
        else:
            assert onz__hrclk == 'float'
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            onqc__rtcbg = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            nofp__jsiu = pd.to_numeric(onqc__rtcbg, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                index, name)
        return impl_series
    if arg_a != string_array_type:
        raise BodoError('pd.to_numeric(): invalid argument type {}'.format(
            arg_a))
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            dasv__vct = np.empty(n, np.float64)
            for ggx__dlf in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, ggx__dlf):
                    bodo.libs.array_kernels.setna(dasv__vct, ggx__dlf)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(dasv__vct,
                        ggx__dlf, arg_a, ggx__dlf)
            return dasv__vct
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            dasv__vct = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for ggx__dlf in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, ggx__dlf):
                    bodo.libs.array_kernels.setna(dasv__vct, ggx__dlf)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(dasv__vct,
                        ggx__dlf, arg_a, ggx__dlf)
            return dasv__vct
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        stbrk__ayfw = if_series_to_array_type(args[0])
        if isinstance(stbrk__ayfw, types.Array) and isinstance(stbrk__ayfw.
            dtype, types.Integer):
            stbrk__ayfw = types.Array(types.float64, 1, 'C')
        return stbrk__ayfw(*args)


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
    zhqjl__tey = bodo.utils.utils.is_array_typ(x, True)
    xsnzj__fff = bodo.utils.utils.is_array_typ(y, True)
    zaet__qrwld = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        zaet__qrwld += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if zhqjl__tey and not bodo.utils.utils.is_array_typ(x, False):
        zaet__qrwld += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if xsnzj__fff and not bodo.utils.utils.is_array_typ(y, False):
        zaet__qrwld += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    zaet__qrwld += '  n = len(condition)\n'
    xrf__oja = x.dtype if zhqjl__tey else types.unliteral(x)
    sucug__gyeyi = y.dtype if xsnzj__fff else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        xrf__oja = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        sucug__gyeyi = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    zkmlk__amnur = get_data(x)
    fmi__xiim = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(oicl__zuf) for
        oicl__zuf in [zkmlk__amnur, fmi__xiim])
    if fmi__xiim == types.none:
        if isinstance(xrf__oja, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif zkmlk__amnur == fmi__xiim and not is_nullable:
        out_dtype = dtype_to_array_type(xrf__oja)
    elif xrf__oja == string_type or sucug__gyeyi == string_type:
        out_dtype = bodo.string_array_type
    elif zkmlk__amnur == bytes_type or (zhqjl__tey and xrf__oja == bytes_type
        ) and (fmi__xiim == bytes_type or xsnzj__fff and sucug__gyeyi ==
        bytes_type):
        out_dtype = binary_array_type
    elif isinstance(xrf__oja, bodo.PDCategoricalDtype):
        out_dtype = None
    elif xrf__oja in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(xrf__oja, 1, 'C')
    elif sucug__gyeyi in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(sucug__gyeyi, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(xrf__oja), numba.np.numpy_support.
            as_dtype(sucug__gyeyi)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(xrf__oja, bodo.PDCategoricalDtype):
        wlnhh__ccm = 'x'
    else:
        wlnhh__ccm = 'out_dtype'
    zaet__qrwld += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {wlnhh__ccm}, (-1,))\n')
    if isinstance(xrf__oja, bodo.PDCategoricalDtype):
        zaet__qrwld += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        zaet__qrwld += """  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)
"""
    zaet__qrwld += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    zaet__qrwld += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if zhqjl__tey:
        zaet__qrwld += '      if bodo.libs.array_kernels.isna(x, j):\n'
        zaet__qrwld += '        setna(out_arr, j)\n'
        zaet__qrwld += '        continue\n'
    if isinstance(xrf__oja, bodo.PDCategoricalDtype):
        zaet__qrwld += '      out_codes[j] = x_codes[j]\n'
    else:
        zaet__qrwld += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if zhqjl__tey else 'x'))
    zaet__qrwld += '    else:\n'
    if xsnzj__fff:
        zaet__qrwld += '      if bodo.libs.array_kernels.isna(y, j):\n'
        zaet__qrwld += '        setna(out_arr, j)\n'
        zaet__qrwld += '        continue\n'
    if fmi__xiim == types.none:
        if isinstance(xrf__oja, bodo.PDCategoricalDtype):
            zaet__qrwld += '      out_codes[j] = -1\n'
        else:
            zaet__qrwld += '      setna(out_arr, j)\n'
    else:
        zaet__qrwld += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if xsnzj__fff else 'y'))
    zaet__qrwld += '  return out_arr\n'
    unl__vor = {}
    exec(zaet__qrwld, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, unl__vor)
    zivru__dic = unl__vor['_impl']
    return zivru__dic


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
        jjpvb__ydqcj = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(jjpvb__ydqcj, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(jjpvb__ydqcj):
            bixq__hinn = jjpvb__ydqcj.data.dtype
        else:
            bixq__hinn = jjpvb__ydqcj.dtype
        if isinstance(bixq__hinn, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        iuywz__awllu = jjpvb__ydqcj
    else:
        qxuwn__lzbcn = []
        for jjpvb__ydqcj in choicelist:
            if not bodo.utils.utils.is_array_typ(jjpvb__ydqcj, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(jjpvb__ydqcj):
                bixq__hinn = jjpvb__ydqcj.data.dtype
            else:
                bixq__hinn = jjpvb__ydqcj.dtype
            if isinstance(bixq__hinn, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            qxuwn__lzbcn.append(bixq__hinn)
        if not is_common_scalar_dtype(qxuwn__lzbcn):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        iuywz__awllu = choicelist[0]
    if is_series_type(iuywz__awllu):
        iuywz__awllu = iuywz__awllu.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, iuywz__awllu.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(iuywz__awllu, types.Array) or isinstance(
        iuywz__awllu, BooleanArrayType) or isinstance(iuywz__awllu,
        IntegerArrayType) or bodo.utils.utils.is_array_typ(iuywz__awllu, 
        False) and iuywz__awllu.dtype in [bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {iuywz__awllu} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    dax__htyxa = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        gesl__ppzpn = choicelist.dtype
    else:
        iehi__dwd = False
        qxuwn__lzbcn = []
        for jjpvb__ydqcj in choicelist:
            if is_nullable_type(jjpvb__ydqcj):
                iehi__dwd = True
            if is_series_type(jjpvb__ydqcj):
                bixq__hinn = jjpvb__ydqcj.data.dtype
            else:
                bixq__hinn = jjpvb__ydqcj.dtype
            if isinstance(bixq__hinn, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            qxuwn__lzbcn.append(bixq__hinn)
        dtu__bpreo, zxcw__msih = get_common_scalar_dtype(qxuwn__lzbcn)
        if not zxcw__msih:
            raise BodoError('Internal error in overload_np_select')
        sqwm__xwqtd = dtype_to_array_type(dtu__bpreo)
        if iehi__dwd:
            sqwm__xwqtd = to_nullable_type(sqwm__xwqtd)
        gesl__ppzpn = sqwm__xwqtd
    if isinstance(gesl__ppzpn, SeriesType):
        gesl__ppzpn = gesl__ppzpn.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pgnv__wiasy = True
    else:
        pgnv__wiasy = False
    zfev__gko = False
    zip__jgni = False
    if pgnv__wiasy:
        if isinstance(gesl__ppzpn.dtype, types.Number):
            pass
        elif gesl__ppzpn.dtype == types.bool_:
            zip__jgni = True
        else:
            zfev__gko = True
            gesl__ppzpn = to_nullable_type(gesl__ppzpn)
    elif default == types.none or is_overload_constant_nan(default):
        zfev__gko = True
        gesl__ppzpn = to_nullable_type(gesl__ppzpn)
    zaet__qrwld = 'def np_select_impl(condlist, choicelist, default=0):\n'
    zaet__qrwld += '  if len(condlist) != len(choicelist):\n'
    zaet__qrwld += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    zaet__qrwld += '  output_len = len(choicelist[0])\n'
    zaet__qrwld += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    zaet__qrwld += '  for i in range(output_len):\n'
    if zfev__gko:
        zaet__qrwld += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif zip__jgni:
        zaet__qrwld += '    out[i] = False\n'
    else:
        zaet__qrwld += '    out[i] = default\n'
    if dax__htyxa:
        zaet__qrwld += '  for i in range(len(condlist) - 1, -1, -1):\n'
        zaet__qrwld += '    cond = condlist[i]\n'
        zaet__qrwld += '    choice = choicelist[i]\n'
        zaet__qrwld += '    out = np.where(cond, choice, out)\n'
    else:
        for ggx__dlf in range(len(choicelist) - 1, -1, -1):
            zaet__qrwld += f'  cond = condlist[{ggx__dlf}]\n'
            zaet__qrwld += f'  choice = choicelist[{ggx__dlf}]\n'
            zaet__qrwld += f'  out = np.where(cond, choice, out)\n'
    zaet__qrwld += '  return out'
    unl__vor = dict()
    exec(zaet__qrwld, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': gesl__ppzpn}, unl__vor)
    impl = unl__vor['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        nofp__jsiu = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu, index, name)
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    jxbju__zduyv = dict(subset=subset, keep=keep, inplace=inplace)
    lae__ifmvw = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', jxbju__zduyv,
        lae__ifmvw, package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        exhf__onssl = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (exhf__onssl,), yku__jhfj = bodo.libs.array_kernels.drop_duplicates((
            exhf__onssl,), index, 1)
        index = bodo.utils.conversion.index_from_array(yku__jhfj)
        return bodo.hiframes.pd_series_ext.init_series(exhf__onssl, index, name
            )
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    dmrn__bui = element_type(S.data)
    if not is_common_scalar_dtype([dmrn__bui, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([dmrn__bui, right]):
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
        nofp__jsiu = np.empty(n, np.bool_)
        for ggx__dlf in numba.parfors.parfor.internal_prange(n):
            yef__cxpny = bodo.utils.conversion.box_if_dt64(arr[ggx__dlf])
            if inclusive == 'both':
                nofp__jsiu[ggx__dlf
                    ] = yef__cxpny <= right and yef__cxpny >= left
            else:
                nofp__jsiu[ggx__dlf] = yef__cxpny < right and yef__cxpny > left
        return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu, index, name)
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    jxbju__zduyv = dict(axis=axis)
    lae__ifmvw = dict(axis=None)
    check_unsupported_args('Series.repeat', jxbju__zduyv, lae__ifmvw,
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
            yku__jhfj = bodo.utils.conversion.index_to_array(index)
            nofp__jsiu = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            mnj__bghl = bodo.libs.array_kernels.repeat_kernel(yku__jhfj,
                repeats)
            xqqw__myot = bodo.utils.conversion.index_from_array(mnj__bghl)
            return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
                xqqw__myot, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        yku__jhfj = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        nofp__jsiu = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        mnj__bghl = bodo.libs.array_kernels.repeat_kernel(yku__jhfj, repeats)
        xqqw__myot = bodo.utils.conversion.index_from_array(mnj__bghl)
        return bodo.hiframes.pd_series_ext.init_series(nofp__jsiu,
            xqqw__myot, name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        oicl__zuf = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(oicl__zuf)
        oykd__jxx = {}
        for ggx__dlf in range(n):
            yef__cxpny = bodo.utils.conversion.box_if_dt64(oicl__zuf[ggx__dlf])
            oykd__jxx[index[ggx__dlf]] = yef__cxpny
        return oykd__jxx
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    pyh__mvepe = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            emo__dqn = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(pyh__mvepe)
    elif is_literal_type(name):
        emo__dqn = get_literal_value(name)
    else:
        raise_bodo_error(pyh__mvepe)
    emo__dqn = 0 if emo__dqn is None else emo__dqn

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            (emo__dqn,))
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
