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
            ufhdh__hng = list()
            for zrgqo__vscf in range(len(S)):
                ufhdh__hng.append(S.iat[zrgqo__vscf])
            return ufhdh__hng
        return impl_float

    def impl(S):
        ufhdh__hng = list()
        for zrgqo__vscf in range(len(S)):
            if bodo.libs.array_kernels.isna(S.values, zrgqo__vscf):
                raise ValueError(
                    'Series.to_list(): Not supported for NA values with non-float dtypes'
                    )
            ufhdh__hng.append(S.iat[zrgqo__vscf])
        return ufhdh__hng
    return impl


@overload_method(SeriesType, 'to_numpy', inline='always', no_unliteral=True)
def overload_series_to_numpy(S, dtype=None, copy=False, na_value=None):
    jvj__mfiy = dict(dtype=dtype, copy=copy, na_value=na_value)
    ufkf__cznec = dict(dtype=None, copy=False, na_value=None)
    check_unsupported_args('Series.to_numpy', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')

    def impl(S, dtype=None, copy=False, na_value=None):
        return S.values
    return impl


@overload_method(SeriesType, 'reset_index', inline='always', no_unliteral=True)
def overload_series_reset_index(S, level=None, drop=False, name=None,
    inplace=False):
    jvj__mfiy = dict(name=name, inplace=inplace)
    ufkf__cznec = dict(name=None, inplace=False)
    check_unsupported_args('Series.reset_index', jvj__mfiy, ufkf__cznec,
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
    elpd__onbh = get_name_literal(S.index.name_typ, True, series_name)
    columns = [elpd__onbh, series_name]
    kgre__ctvk = (
        'def _impl(S, level=None, drop=False, name=None, inplace=False):\n')
    kgre__ctvk += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    kgre__ctvk += """    index = bodo.utils.conversion.index_to_array(bodo.hiframes.pd_series_ext.get_series_index(S))
"""
    kgre__ctvk += """    df_index = bodo.hiframes.pd_index_ext.init_range_index(0, len(S), 1, None)
"""
    kgre__ctvk += '    col_var = {}\n'.format(gen_const_tup(columns))
    kgre__ctvk += """    return bodo.hiframes.pd_dataframe_ext.init_dataframe((index, arr), df_index, col_var)
"""
    qgrcw__fuy = {}
    exec(kgre__ctvk, {'bodo': bodo}, qgrcw__fuy)
    pmcm__cxacd = qgrcw__fuy['_impl']
    return pmcm__cxacd


@overload_method(SeriesType, 'isna', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'isnull', inline='always', no_unliteral=True)
def overload_series_isna(S):

    def impl(S):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        frmz__qgre = bodo.libs.array_ops.array_op_isna(arr)
        return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, index, name)
    return impl


@overload_method(SeriesType, 'round', inline='always', no_unliteral=True)
def overload_series_round(S, decimals=0):

    def impl(S, decimals=0):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        numba.parfors.parfor.init_prange()
        n = len(arr)
        frmz__qgre = bodo.utils.utils.alloc_type(n, arr, (-1,))
        for zrgqo__vscf in numba.parfors.parfor.internal_prange(n):
            if pd.isna(arr[zrgqo__vscf]):
                bodo.libs.array_kernels.setna(frmz__qgre, zrgqo__vscf)
            else:
                frmz__qgre[zrgqo__vscf] = np.round(arr[zrgqo__vscf], decimals)
        return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, index, name)
    return impl


@overload_method(SeriesType, 'sum', inline='always', no_unliteral=True)
def overload_series_sum(S, axis=None, skipna=True, level=None, numeric_only
    =None, min_count=0):
    jvj__mfiy = dict(level=level, numeric_only=numeric_only)
    ufkf__cznec = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sum', jvj__mfiy, ufkf__cznec,
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
    jvj__mfiy = dict(level=level, numeric_only=numeric_only)
    ufkf__cznec = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.product', jvj__mfiy, ufkf__cznec,
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
    jvj__mfiy = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=level
        )
    ufkf__cznec = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.any', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        lsz__ncsvz = 0
        for zrgqo__vscf in numba.parfors.parfor.internal_prange(len(A)):
            jlv__vte = 0
            if not bodo.libs.array_kernels.isna(A, zrgqo__vscf):
                jlv__vte = int(A[zrgqo__vscf])
            lsz__ncsvz += jlv__vte
        return lsz__ncsvz != 0
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
        qpd__mcw = bodo.hiframes.pd_series_ext.get_series_data(S)
        jry__ond = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        lsz__ncsvz = 0
        for zrgqo__vscf in numba.parfors.parfor.internal_prange(len(qpd__mcw)):
            jlv__vte = 0
            ohtn__aufac = bodo.libs.array_kernels.isna(qpd__mcw, zrgqo__vscf)
            qpj__ooiws = bodo.libs.array_kernels.isna(jry__ond, zrgqo__vscf)
            if (ohtn__aufac and not qpj__ooiws or not ohtn__aufac and
                qpj__ooiws):
                jlv__vte = 1
            elif not ohtn__aufac:
                if qpd__mcw[zrgqo__vscf] != jry__ond[zrgqo__vscf]:
                    jlv__vte = 1
            lsz__ncsvz += jlv__vte
        return lsz__ncsvz == 0
    return impl


@overload_method(SeriesType, 'all', inline='always', no_unliteral=True)
def overload_series_all(S, axis=0, bool_only=None, skipna=True, level=None):
    jvj__mfiy = dict(axis=axis, bool_only=bool_only, skipna=skipna, level=level
        )
    ufkf__cznec = dict(axis=0, bool_only=None, skipna=True, level=None)
    check_unsupported_args('Series.all', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, bool_only=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        lsz__ncsvz = 0
        for zrgqo__vscf in numba.parfors.parfor.internal_prange(len(A)):
            jlv__vte = 0
            if not bodo.libs.array_kernels.isna(A, zrgqo__vscf):
                jlv__vte = int(not A[zrgqo__vscf])
            lsz__ncsvz += jlv__vte
        return lsz__ncsvz == 0
    return impl


@overload_method(SeriesType, 'mad', inline='always', no_unliteral=True)
def overload_series_mad(S, axis=None, skipna=True, level=None):
    jvj__mfiy = dict(level=level)
    ufkf__cznec = dict(level=None)
    check_unsupported_args('Series.mad', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')
    if not is_overload_bool(skipna):
        raise BodoError("Series.mad(): 'skipna' argument must be a boolean")
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.mad(): axis argument not supported')
    irwjc__axsd = types.float64
    hyebr__kgdk = types.float64
    if S.dtype == types.float32:
        irwjc__axsd = types.float32
        hyebr__kgdk = types.float32
    yvyqw__bpntw = irwjc__axsd(0)
    qow__fvn = hyebr__kgdk(0)
    ccfa__kkux = hyebr__kgdk(1)

    def impl(S, axis=None, skipna=True, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        ofhu__faoy = yvyqw__bpntw
        lsz__ncsvz = qow__fvn
        for zrgqo__vscf in numba.parfors.parfor.internal_prange(len(A)):
            jlv__vte = yvyqw__bpntw
            ppx__wrhhu = qow__fvn
            if not bodo.libs.array_kernels.isna(A, zrgqo__vscf) or not skipna:
                jlv__vte = A[zrgqo__vscf]
                ppx__wrhhu = ccfa__kkux
            ofhu__faoy += jlv__vte
            lsz__ncsvz += ppx__wrhhu
        qrl__ddz = bodo.hiframes.series_kernels._mean_handle_nan(ofhu__faoy,
            lsz__ncsvz)
        inkr__csr = yvyqw__bpntw
        for zrgqo__vscf in numba.parfors.parfor.internal_prange(len(A)):
            jlv__vte = yvyqw__bpntw
            if not bodo.libs.array_kernels.isna(A, zrgqo__vscf) or not skipna:
                jlv__vte = abs(A[zrgqo__vscf] - qrl__ddz)
            inkr__csr += jlv__vte
        kug__qhm = bodo.hiframes.series_kernels._mean_handle_nan(inkr__csr,
            lsz__ncsvz)
        return kug__qhm
    return impl


@overload_method(SeriesType, 'mean', inline='always', no_unliteral=True)
def overload_series_mean(S, axis=None, skipna=None, level=None,
    numeric_only=None):
    if not isinstance(S.dtype, types.Number) and S.dtype not in [bodo.
        datetime64ns, types.bool_]:
        raise BodoError(f"Series.mean(): Series with type '{S}' not supported")
    jvj__mfiy = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    ufkf__cznec = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.mean', jvj__mfiy, ufkf__cznec,
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
    jvj__mfiy = dict(level=level, numeric_only=numeric_only)
    ufkf__cznec = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.sem', jvj__mfiy, ufkf__cznec,
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
        uxo__uip = 0
        xegkd__qxm = 0
        lsz__ncsvz = 0
        for zrgqo__vscf in numba.parfors.parfor.internal_prange(len(A)):
            jlv__vte = 0
            ppx__wrhhu = 0
            if not bodo.libs.array_kernels.isna(A, zrgqo__vscf) or not skipna:
                jlv__vte = A[zrgqo__vscf]
                ppx__wrhhu = 1
            uxo__uip += jlv__vte
            xegkd__qxm += jlv__vte * jlv__vte
            lsz__ncsvz += ppx__wrhhu
        oykxz__gzo = bodo.hiframes.series_kernels._compute_var_nan_count_ddof(
            uxo__uip, xegkd__qxm, lsz__ncsvz, ddof)
        tumpf__hjca = bodo.hiframes.series_kernels._sem_handle_nan(oykxz__gzo,
            lsz__ncsvz)
        return tumpf__hjca
    return impl


@overload_method(SeriesType, 'kurt', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'kurtosis', inline='always', no_unliteral=True)
def overload_series_kurt(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    jvj__mfiy = dict(level=level, numeric_only=numeric_only)
    ufkf__cznec = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.kurtosis', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.kurtosis(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError(
            "Series.kurtosis(): 'skipna' argument must be a boolean")

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        uxo__uip = 0.0
        xegkd__qxm = 0.0
        ama__sjzfb = 0.0
        leho__pvcj = 0.0
        lsz__ncsvz = 0
        for zrgqo__vscf in numba.parfors.parfor.internal_prange(len(A)):
            jlv__vte = 0.0
            ppx__wrhhu = 0
            if not bodo.libs.array_kernels.isna(A, zrgqo__vscf) or not skipna:
                jlv__vte = np.float64(A[zrgqo__vscf])
                ppx__wrhhu = 1
            uxo__uip += jlv__vte
            xegkd__qxm += jlv__vte ** 2
            ama__sjzfb += jlv__vte ** 3
            leho__pvcj += jlv__vte ** 4
            lsz__ncsvz += ppx__wrhhu
        oykxz__gzo = bodo.hiframes.series_kernels.compute_kurt(uxo__uip,
            xegkd__qxm, ama__sjzfb, leho__pvcj, lsz__ncsvz)
        return oykxz__gzo
    return impl


@overload_method(SeriesType, 'skew', inline='always', no_unliteral=True)
def overload_series_skew(S, axis=None, skipna=True, level=None,
    numeric_only=None):
    jvj__mfiy = dict(level=level, numeric_only=numeric_only)
    ufkf__cznec = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.skew', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error('Series.skew(): axis argument not supported')
    if not is_overload_bool(skipna):
        raise BodoError('Series.skew(): skipna argument must be a boolean')

    def impl(S, axis=None, skipna=True, level=None, numeric_only=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        numba.parfors.parfor.init_prange()
        uxo__uip = 0.0
        xegkd__qxm = 0.0
        ama__sjzfb = 0.0
        lsz__ncsvz = 0
        for zrgqo__vscf in numba.parfors.parfor.internal_prange(len(A)):
            jlv__vte = 0.0
            ppx__wrhhu = 0
            if not bodo.libs.array_kernels.isna(A, zrgqo__vscf) or not skipna:
                jlv__vte = np.float64(A[zrgqo__vscf])
                ppx__wrhhu = 1
            uxo__uip += jlv__vte
            xegkd__qxm += jlv__vte ** 2
            ama__sjzfb += jlv__vte ** 3
            lsz__ncsvz += ppx__wrhhu
        oykxz__gzo = bodo.hiframes.series_kernels.compute_skew(uxo__uip,
            xegkd__qxm, ama__sjzfb, lsz__ncsvz)
        return oykxz__gzo
    return impl


@overload_method(SeriesType, 'var', inline='always', no_unliteral=True)
def overload_series_var(S, axis=None, skipna=True, level=None, ddof=1,
    numeric_only=None):
    jvj__mfiy = dict(level=level, numeric_only=numeric_only)
    ufkf__cznec = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.var', jvj__mfiy, ufkf__cznec,
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
    jvj__mfiy = dict(level=level, numeric_only=numeric_only)
    ufkf__cznec = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.std', jvj__mfiy, ufkf__cznec,
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
        qpd__mcw = bodo.hiframes.pd_series_ext.get_series_data(S)
        jry__ond = bodo.hiframes.pd_series_ext.get_series_data(other)
        numba.parfors.parfor.init_prange()
        roaai__jitm = 0
        for zrgqo__vscf in numba.parfors.parfor.internal_prange(len(qpd__mcw)):
            ibtz__phcv = qpd__mcw[zrgqo__vscf]
            weq__aubyp = jry__ond[zrgqo__vscf]
            roaai__jitm += ibtz__phcv * weq__aubyp
        return roaai__jitm
    return impl


@overload_method(SeriesType, 'cumsum', inline='always', no_unliteral=True)
def overload_series_cumsum(S, axis=None, skipna=True):
    jvj__mfiy = dict(skipna=skipna)
    ufkf__cznec = dict(skipna=True)
    check_unsupported_args('Series.cumsum', jvj__mfiy, ufkf__cznec,
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
    jvj__mfiy = dict(skipna=skipna)
    ufkf__cznec = dict(skipna=True)
    check_unsupported_args('Series.cumprod', jvj__mfiy, ufkf__cznec,
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
    jvj__mfiy = dict(skipna=skipna)
    ufkf__cznec = dict(skipna=True)
    check_unsupported_args('Series.cummin', jvj__mfiy, ufkf__cznec,
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
    jvj__mfiy = dict(skipna=skipna)
    ufkf__cznec = dict(skipna=True)
    check_unsupported_args('Series.cummax', jvj__mfiy, ufkf__cznec,
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
    jvj__mfiy = dict(copy=copy, inplace=inplace, level=level, errors=errors)
    ufkf__cznec = dict(copy=True, inplace=False, level=None, errors='ignore')
    check_unsupported_args('Series.rename', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')

    def impl(S, index=None, axis=None, copy=True, inplace=False, level=None,
        errors='ignore'):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        chlw__bzx = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_series_ext.init_series(A, chlw__bzx, index)
    return impl


@overload_method(SeriesType, 'rename_axis', inline='always', no_unliteral=True)
def overload_series_rename_axis(S, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False):
    jvj__mfiy = dict(index=index, columns=columns, axis=axis, copy=copy,
        inplace=inplace)
    ufkf__cznec = dict(index=None, columns=None, axis=None, copy=True,
        inplace=False)
    check_unsupported_args('Series.rename_axis', jvj__mfiy, ufkf__cznec,
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
    jvj__mfiy = dict(level=level)
    ufkf__cznec = dict(level=None)
    check_unsupported_args('Series.count', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')

    def impl(S, level=None):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        return bodo.libs.array_ops.array_op_count(A)
    return impl


@overload_method(SeriesType, 'corr', inline='always', no_unliteral=True)
def overload_series_corr(S, other, method='pearson', min_periods=None):
    jvj__mfiy = dict(method=method, min_periods=min_periods)
    ufkf__cznec = dict(method='pearson', min_periods=None)
    check_unsupported_args('Series.corr', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')

    def impl(S, other, method='pearson', min_periods=None):
        n = S.count()
        mxhpd__hmby = S.sum()
        mufa__ujmva = other.sum()
        a = n * (S * other).sum() - mxhpd__hmby * mufa__ujmva
        slihk__lvjva = n * (S ** 2).sum() - mxhpd__hmby ** 2
        zgldf__oiti = n * (other ** 2).sum() - mufa__ujmva ** 2
        return a / np.sqrt(slihk__lvjva * zgldf__oiti)
    return impl


@overload_method(SeriesType, 'cov', inline='always', no_unliteral=True)
def overload_series_cov(S, other, min_periods=None, ddof=1):
    jvj__mfiy = dict(min_periods=min_periods)
    ufkf__cznec = dict(min_periods=None)
    check_unsupported_args('Series.cov', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')

    def impl(S, other, min_periods=None, ddof=1):
        mxhpd__hmby = S.mean()
        mufa__ujmva = other.mean()
        scjn__yimwr = ((S - mxhpd__hmby) * (other - mufa__ujmva)).sum()
        N = np.float64(S.count() - ddof)
        nonzero_len = S.count() * other.count()
        return _series_cov_helper(scjn__yimwr, N, nonzero_len)
    return impl


def _series_cov_helper(sum_val, N, nonzero_len):
    return


@overload(_series_cov_helper, no_unliteral=True)
def _overload_series_cov_helper(sum_val, N, nonzero_len):

    def impl(sum_val, N, nonzero_len):
        if not nonzero_len:
            return np.nan
        if N <= 0.0:
            bcxz__hos = np.sign(sum_val)
            return np.inf * bcxz__hos
        return sum_val / N
    return impl


@overload_method(SeriesType, 'min', inline='always', no_unliteral=True)
def overload_series_min(S, axis=None, skipna=None, level=None, numeric_only
    =None):
    jvj__mfiy = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    ufkf__cznec = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.min', jvj__mfiy, ufkf__cznec,
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
    jvj__mfiy = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    ufkf__cznec = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('Series.max', jvj__mfiy, ufkf__cznec,
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
    jvj__mfiy = dict(axis=axis, skipna=skipna)
    ufkf__cznec = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmin', jvj__mfiy, ufkf__cznec,
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
    jvj__mfiy = dict(axis=axis, skipna=skipna)
    ufkf__cznec = dict(axis=0, skipna=True)
    check_unsupported_args('Series.idxmax', jvj__mfiy, ufkf__cznec,
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
    jvj__mfiy = dict(level=level, numeric_only=numeric_only)
    ufkf__cznec = dict(level=None, numeric_only=None)
    check_unsupported_args('Series.median', jvj__mfiy, ufkf__cznec,
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
        mwg__bvtoi = arr[:n]
        bzxl__sbtx = index[:n]
        return bodo.hiframes.pd_series_ext.init_series(mwg__bvtoi,
            bzxl__sbtx, name)
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
        bsqu__iod = tail_slice(len(S), n)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        mwg__bvtoi = arr[bsqu__iod:]
        bzxl__sbtx = index[bsqu__iod:]
        return bodo.hiframes.pd_series_ext.init_series(mwg__bvtoi,
            bzxl__sbtx, name)
    return impl


@overload_method(SeriesType, 'first', inline='always', no_unliteral=True)
def overload_series_first(S, offset):
    szr__kqv = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in szr__kqv:
        raise BodoError(
            "Series.first(): 'offset' must be a string or a DateOffset")

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            nktsv__mluvu = index[0]
            gbsu__tmwc = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset,
                nktsv__mluvu, False))
        else:
            gbsu__tmwc = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        mwg__bvtoi = arr[:gbsu__tmwc]
        bzxl__sbtx = index[:gbsu__tmwc]
        return bodo.hiframes.pd_series_ext.init_series(mwg__bvtoi,
            bzxl__sbtx, name)
    return impl


@overload_method(SeriesType, 'last', inline='always', no_unliteral=True)
def overload_series_last(S, offset):
    szr__kqv = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if types.unliteral(offset) not in szr__kqv:
        raise BodoError(
            "Series.last(): 'offset' must be a string or a DateOffset")

    def impl(S, offset):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        if len(index):
            skdb__lwb = index[-1]
            gbsu__tmwc = (bodo.libs.array_kernels.
                get_valid_entries_from_date_offset(index, offset, skdb__lwb,
                True))
        else:
            gbsu__tmwc = 0
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        mwg__bvtoi = arr[len(arr) - gbsu__tmwc:]
        bzxl__sbtx = index[len(arr) - gbsu__tmwc:]
        return bodo.hiframes.pd_series_ext.init_series(mwg__bvtoi,
            bzxl__sbtx, name)
    return impl


@overload_method(SeriesType, 'nlargest', inline='always', no_unliteral=True)
def overload_series_nlargest(S, n=5, keep='first'):
    jvj__mfiy = dict(keep=keep)
    ufkf__cznec = dict(keep='first')
    check_unsupported_args('Series.nlargest', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nlargest(): n argument must be an integer')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        hyv__fuxa = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        frmz__qgre, ylw__bgqey = bodo.libs.array_kernels.nlargest(arr,
            hyv__fuxa, n, True, bodo.hiframes.series_kernels.gt_f)
        yjr__gjb = bodo.utils.conversion.convert_to_index(ylw__bgqey)
        return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, yjr__gjb,
            name)
    return impl


@overload_method(SeriesType, 'nsmallest', inline='always', no_unliteral=True)
def overload_series_nsmallest(S, n=5, keep='first'):
    jvj__mfiy = dict(keep=keep)
    ufkf__cznec = dict(keep='first')
    check_unsupported_args('Series.nsmallest', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')
    if not is_overload_int(n):
        raise BodoError('Series.nsmallest(): n argument must be an integer')

    def impl(S, n=5, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        hyv__fuxa = bodo.utils.conversion.coerce_to_ndarray(index)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        frmz__qgre, ylw__bgqey = bodo.libs.array_kernels.nlargest(arr,
            hyv__fuxa, n, False, bodo.hiframes.series_kernels.lt_f)
        yjr__gjb = bodo.utils.conversion.convert_to_index(ylw__bgqey)
        return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, yjr__gjb,
            name)
    return impl


@overload_method(SeriesType, 'notnull', inline='always', no_unliteral=True)
@overload_method(SeriesType, 'notna', inline='always', no_unliteral=True)
def overload_series_notna(S):
    return lambda S: S.isna() == False


@overload_method(SeriesType, 'astype', inline='always', no_unliteral=True)
def overload_series_astype(S, dtype, copy=True, errors='raise',
    _bodo_nan_to_str=True):
    jvj__mfiy = dict(errors=errors)
    ufkf__cznec = dict(errors='raise')
    check_unsupported_args('Series.astype', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "Series.astype(): 'dtype' when passed as string must be a constant value"
            )

    def impl(S, dtype, copy=True, errors='raise', _bodo_nan_to_str=True):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        frmz__qgre = bodo.utils.conversion.fix_arr_dtype(arr, dtype, copy,
            nan_to_str=_bodo_nan_to_str, from_series=True)
        return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, index, name)
    return impl


@overload_method(SeriesType, 'take', inline='always', no_unliteral=True)
def overload_series_take(S, indices, axis=0, is_copy=True):
    jvj__mfiy = dict(axis=axis, is_copy=is_copy)
    ufkf__cznec = dict(axis=0, is_copy=True)
    check_unsupported_args('Series.take', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')
    if not (is_iterable_type(indices) and isinstance(indices.dtype, types.
        Integer)):
        raise BodoError(
            f"Series.take() 'indices' must be an array-like and contain integers. Found type {indices}."
            )

    def impl(S, indices, axis=0, is_copy=True):
        uner__ypna = bodo.utils.conversion.coerce_to_ndarray(indices)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        return bodo.hiframes.pd_series_ext.init_series(arr[uner__ypna],
            index[uner__ypna], name)
    return impl


@overload_method(SeriesType, 'argsort', inline='always', no_unliteral=True)
def overload_series_argsort(S, axis=0, kind='quicksort', order=None):
    jvj__mfiy = dict(axis=axis, kind=kind, order=order)
    ufkf__cznec = dict(axis=0, kind='quicksort', order=None)
    check_unsupported_args('Series.argsort', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')

    def impl(S, axis=0, kind='quicksort', order=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        n = len(arr)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        aphsh__caad = S.notna().values
        if not aphsh__caad.all():
            frmz__qgre = np.full(n, -1, np.int64)
            frmz__qgre[aphsh__caad] = argsort(arr[aphsh__caad])
        else:
            frmz__qgre = argsort(arr)
        return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, index, name)
    return impl


@overload_method(SeriesType, 'sort_index', inline='always', no_unliteral=True)
def overload_series_sort_index(S, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    jvj__mfiy = dict(axis=axis, level=level, inplace=inplace, kind=kind,
        sort_remaining=sort_remaining, ignore_index=ignore_index, key=key)
    ufkf__cznec = dict(axis=0, level=None, inplace=False, kind='quicksort',
        sort_remaining=True, ignore_index=False, key=None)
    check_unsupported_args('Series.sort_index', jvj__mfiy, ufkf__cznec,
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
        ccpcb__polib = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, ('$_bodo_col3_',))
        ixcqy__qcw = ccpcb__polib.sort_index(ascending=ascending, inplace=
            inplace, na_position=na_position)
        frmz__qgre = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            ixcqy__qcw, 0)
        yjr__gjb = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            ixcqy__qcw)
        return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, yjr__gjb,
            name)
    return impl


@overload_method(SeriesType, 'sort_values', inline='always', no_unliteral=True)
def overload_series_sort_values(S, axis=0, ascending=True, inplace=False,
    kind='quicksort', na_position='last', ignore_index=False, key=None):
    jvj__mfiy = dict(axis=axis, inplace=inplace, kind=kind, ignore_index=
        ignore_index, key=key)
    ufkf__cznec = dict(axis=0, inplace=False, kind='quicksort',
        ignore_index=False, key=None)
    check_unsupported_args('Series.sort_values', jvj__mfiy, ufkf__cznec,
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
        ccpcb__polib = bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,),
            index, ('$_bodo_col_',))
        ixcqy__qcw = ccpcb__polib.sort_values(['$_bodo_col_'], ascending=
            ascending, inplace=inplace, na_position=na_position)
        frmz__qgre = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(
            ixcqy__qcw, 0)
        yjr__gjb = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(
            ixcqy__qcw)
        return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, yjr__gjb,
            name)
    return impl


def get_bin_inds(bins, arr):
    return arr


@overload(get_bin_inds, inline='always', no_unliteral=True)
def overload_get_bin_inds(bins, arr, is_nullable=True, include_lowest=True):
    assert is_overload_constant_bool(is_nullable)
    pbwjg__ujdwe = is_overload_true(is_nullable)
    kgre__ctvk = (
        'def impl(bins, arr, is_nullable=True, include_lowest=True):\n')
    kgre__ctvk += '  numba.parfors.parfor.init_prange()\n'
    kgre__ctvk += '  n = len(arr)\n'
    if pbwjg__ujdwe:
        kgre__ctvk += (
            '  out_arr = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)\n')
    else:
        kgre__ctvk += '  out_arr = np.empty(n, np.int64)\n'
    kgre__ctvk += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    kgre__ctvk += '    if bodo.libs.array_kernels.isna(arr, i):\n'
    if pbwjg__ujdwe:
        kgre__ctvk += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        kgre__ctvk += '      out_arr[i] = -1\n'
    kgre__ctvk += '      continue\n'
    kgre__ctvk += '    val = arr[i]\n'
    kgre__ctvk += '    if include_lowest and val == bins[0]:\n'
    kgre__ctvk += '      ind = 1\n'
    kgre__ctvk += '    else:\n'
    kgre__ctvk += '      ind = np.searchsorted(bins, val)\n'
    kgre__ctvk += '    if ind == 0 or ind == len(bins):\n'
    if pbwjg__ujdwe:
        kgre__ctvk += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    else:
        kgre__ctvk += '      out_arr[i] = -1\n'
    kgre__ctvk += '    else:\n'
    kgre__ctvk += '      out_arr[i] = ind - 1\n'
    kgre__ctvk += '  return out_arr\n'
    qgrcw__fuy = {}
    exec(kgre__ctvk, {'bodo': bodo, 'np': np, 'numba': numba}, qgrcw__fuy)
    impl = qgrcw__fuy['impl']
    return impl


@register_jitable
def _round_frac(x, precision: int):
    if not np.isfinite(x) or x == 0:
        return x
    else:
        btf__ztiew, ozha__vulo = np.divmod(x, 1)
        if btf__ztiew == 0:
            nsxvz__zda = -int(np.floor(np.log10(abs(ozha__vulo)))
                ) - 1 + precision
        else:
            nsxvz__zda = precision
        return np.around(x, nsxvz__zda)


@register_jitable
def _infer_precision(base_precision: int, bins) ->int:
    for precision in range(base_precision, 20):
        gtbzk__xqkys = np.array([_round_frac(b, precision) for b in bins])
        if len(np.unique(gtbzk__xqkys)) == len(bins):
            return precision
    return base_precision


def get_bin_labels(bins):
    pass


@overload(get_bin_labels, no_unliteral=True)
def overload_get_bin_labels(bins, right=True, include_lowest=True):
    dtype = np.float64 if isinstance(bins.dtype, types.Integer) else bins.dtype
    if dtype == bodo.datetime64ns:
        nji__ytm = bodo.timedelta64ns(1)

        def impl_dt64(bins, right=True, include_lowest=True):
            iebgn__tna = bins.copy()
            if right and include_lowest:
                iebgn__tna[0] = iebgn__tna[0] - nji__ytm
            chnkq__sem = bodo.libs.interval_arr_ext.init_interval_array(
                iebgn__tna[:-1], iebgn__tna[1:])
            return bodo.hiframes.pd_index_ext.init_interval_index(chnkq__sem,
                None)
        return impl_dt64

    def impl(bins, right=True, include_lowest=True):
        base_precision = 3
        precision = _infer_precision(base_precision, bins)
        iebgn__tna = np.array([_round_frac(b, precision) for b in bins],
            dtype=dtype)
        if right and include_lowest:
            iebgn__tna[0] = iebgn__tna[0] - 10.0 ** -precision
        chnkq__sem = bodo.libs.interval_arr_ext.init_interval_array(iebgn__tna
            [:-1], iebgn__tna[1:])
        return bodo.hiframes.pd_index_ext.init_interval_index(chnkq__sem, None)
    return impl


def get_output_bin_counts(count_series, nbins):
    pass


@overload(get_output_bin_counts, no_unliteral=True)
def overload_get_output_bin_counts(count_series, nbins):

    def impl(count_series, nbins):
        icw__fnc = bodo.hiframes.pd_series_ext.get_series_data(count_series)
        ztmz__ubzlg = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(count_series))
        frmz__qgre = np.zeros(nbins, np.int64)
        for zrgqo__vscf in range(len(icw__fnc)):
            frmz__qgre[ztmz__ubzlg[zrgqo__vscf]] = icw__fnc[zrgqo__vscf]
        return frmz__qgre
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
            wiv__wql = (max_val - min_val) * 0.001
            if right:
                bins[0] -= wiv__wql
            else:
                bins[-1] += wiv__wql
        return bins
    return impl


@overload_method(SeriesType, 'value_counts', inline='always', no_unliteral=True
    )
def overload_series_value_counts(S, normalize=False, sort=True, ascending=
    False, bins=None, dropna=True, _index_name=None):
    jvj__mfiy = dict(dropna=dropna)
    ufkf__cznec = dict(dropna=True)
    check_unsupported_args('Series.value_counts', jvj__mfiy, ufkf__cznec,
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
    qzr__ysv = not is_overload_none(bins)
    kgre__ctvk = 'def impl(\n'
    kgre__ctvk += '    S,\n'
    kgre__ctvk += '    normalize=False,\n'
    kgre__ctvk += '    sort=True,\n'
    kgre__ctvk += '    ascending=False,\n'
    kgre__ctvk += '    bins=None,\n'
    kgre__ctvk += '    dropna=True,\n'
    kgre__ctvk += (
        '    _index_name=None,  # bodo argument. See groupby.value_counts\n')
    kgre__ctvk += '):\n'
    kgre__ctvk += '    arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n'
    kgre__ctvk += (
        '    index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
    kgre__ctvk += '    name = bodo.hiframes.pd_series_ext.get_series_name(S)\n'
    if qzr__ysv:
        kgre__ctvk += '    right = True\n'
        kgre__ctvk += _gen_bins_handling(bins, S.dtype)
        kgre__ctvk += '    arr = get_bin_inds(bins, arr)\n'
    kgre__ctvk += (
        '    in_df = bodo.hiframes.pd_dataframe_ext.init_dataframe(\n')
    kgre__ctvk += "        (arr,), index, ('$_bodo_col2_',)\n"
    kgre__ctvk += '    )\n'
    kgre__ctvk += "    count_series = in_df.groupby('$_bodo_col2_').size()\n"
    if qzr__ysv:
        kgre__ctvk += """    count_series = bodo.gatherv(count_series, allgather=True, warn_if_rep=False)
"""
        kgre__ctvk += (
            '    count_arr = get_output_bin_counts(count_series, len(bins) - 1)\n'
            )
        kgre__ctvk += '    index = get_bin_labels(bins)\n'
    else:
        kgre__ctvk += (
            '    count_arr = bodo.hiframes.pd_series_ext.get_series_data(count_series)\n'
            )
        kgre__ctvk += '    ind_arr = bodo.utils.conversion.coerce_to_array(\n'
        kgre__ctvk += (
            '        bodo.hiframes.pd_series_ext.get_series_index(count_series)\n'
            )
        kgre__ctvk += '    )\n'
        kgre__ctvk += """    index = bodo.utils.conversion.index_from_array(ind_arr, name=_index_name)
"""
    kgre__ctvk += (
        '    res = bodo.hiframes.pd_series_ext.init_series(count_arr, index, name)\n'
        )
    if is_overload_true(sort):
        kgre__ctvk += '    res = res.sort_values(ascending=ascending)\n'
    if is_overload_true(normalize):
        kmn__kafnj = 'len(S)' if qzr__ysv else 'count_arr.sum()'
        kgre__ctvk += f'    res = res / float({kmn__kafnj})\n'
    kgre__ctvk += '    return res\n'
    qgrcw__fuy = {}
    exec(kgre__ctvk, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, qgrcw__fuy)
    impl = qgrcw__fuy['impl']
    return impl


def _gen_bins_handling(bins, dtype):
    kgre__ctvk = ''
    if isinstance(bins, types.Integer):
        kgre__ctvk += '    min_val = bodo.libs.array_ops.array_op_min(arr)\n'
        kgre__ctvk += '    max_val = bodo.libs.array_ops.array_op_max(arr)\n'
        if dtype == bodo.datetime64ns:
            kgre__ctvk += '    min_val = min_val.value\n'
            kgre__ctvk += '    max_val = max_val.value\n'
        kgre__ctvk += (
            '    bins = compute_bins(bins, min_val, max_val, right)\n')
        if dtype == bodo.datetime64ns:
            kgre__ctvk += (
                "    bins = bins.astype(np.int64).view(np.dtype('datetime64[ns]'))\n"
                )
    else:
        kgre__ctvk += (
            '    bins = bodo.utils.conversion.coerce_to_ndarray(bins)\n')
    return kgre__ctvk


@overload(pd.cut, inline='always', no_unliteral=True)
def overload_cut(x, bins, right=True, labels=None, retbins=False, precision
    =3, include_lowest=False, duplicates='raise', ordered=True):
    jvj__mfiy = dict(right=right, labels=labels, retbins=retbins, precision
        =precision, duplicates=duplicates, ordered=ordered)
    ufkf__cznec = dict(right=True, labels=None, retbins=False, precision=3,
        duplicates='raise', ordered=True)
    check_unsupported_args('pandas.cut', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='General')
    kgre__ctvk = 'def impl(\n'
    kgre__ctvk += '    x,\n'
    kgre__ctvk += '    bins,\n'
    kgre__ctvk += '    right=True,\n'
    kgre__ctvk += '    labels=None,\n'
    kgre__ctvk += '    retbins=False,\n'
    kgre__ctvk += '    precision=3,\n'
    kgre__ctvk += '    include_lowest=False,\n'
    kgre__ctvk += "    duplicates='raise',\n"
    kgre__ctvk += '    ordered=True\n'
    kgre__ctvk += '):\n'
    if isinstance(x, SeriesType):
        kgre__ctvk += (
            '    arr = bodo.hiframes.pd_series_ext.get_series_data(x)\n')
        kgre__ctvk += (
            '    index = bodo.hiframes.pd_series_ext.get_series_index(x)\n')
        kgre__ctvk += (
            '    name = bodo.hiframes.pd_series_ext.get_series_name(x)\n')
    else:
        kgre__ctvk += '    arr = bodo.utils.conversion.coerce_to_array(x)\n'
    kgre__ctvk += _gen_bins_handling(bins, x.dtype)
    kgre__ctvk += '    arr = get_bin_inds(bins, arr, False, include_lowest)\n'
    kgre__ctvk += (
        '    label_index = get_bin_labels(bins, right, include_lowest)\n')
    kgre__ctvk += """    cat_dtype = bodo.hiframes.pd_categorical_ext.init_cat_dtype(label_index, ordered, None, None)
"""
    kgre__ctvk += """    out_arr = bodo.hiframes.pd_categorical_ext.init_categorical_array(arr, cat_dtype)
"""
    if isinstance(x, SeriesType):
        kgre__ctvk += (
            '    res = bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        kgre__ctvk += '    return res\n'
    else:
        kgre__ctvk += '    return out_arr\n'
    qgrcw__fuy = {}
    exec(kgre__ctvk, {'bodo': bodo, 'pd': pd, 'np': np, 'get_bin_inds':
        get_bin_inds, 'get_bin_labels': get_bin_labels,
        'get_output_bin_counts': get_output_bin_counts, 'compute_bins':
        compute_bins}, qgrcw__fuy)
    impl = qgrcw__fuy['impl']
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
    jvj__mfiy = dict(labels=labels, retbins=retbins, precision=precision,
        duplicates=duplicates)
    ufkf__cznec = dict(labels=None, retbins=False, precision=3, duplicates=
        'raise')
    check_unsupported_args('pandas.qcut', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='General')
    if not (is_overload_int(q) or is_iterable_type(q)):
        raise BodoError(
            "pd.qcut(): 'q' should be an integer or a list of quantiles")

    def impl(x, q, labels=None, retbins=False, precision=3, duplicates='raise'
        ):
        unhnt__indp = _get_q_list(q)
        arr = bodo.utils.conversion.coerce_to_array(x)
        bins = bodo.libs.array_ops.array_op_quantile(arr, unhnt__indp)
        return pd.cut(x, bins, include_lowest=True)
    return impl


@overload_method(SeriesType, 'groupby', inline='always', no_unliteral=True)
def overload_series_groupby(S, by=None, axis=0, level=None, as_index=True,
    sort=True, group_keys=True, squeeze=False, observed=True, dropna=True):
    jvj__mfiy = dict(axis=axis, sort=sort, group_keys=group_keys, squeeze=
        squeeze, observed=observed, dropna=dropna)
    ufkf__cznec = dict(axis=0, sort=True, group_keys=True, squeeze=False,
        observed=True, dropna=True)
    check_unsupported_args('Series.groupby', jvj__mfiy, ufkf__cznec,
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
            tbqj__bkq = bodo.utils.conversion.coerce_to_array(index)
            ccpcb__polib = bodo.hiframes.pd_dataframe_ext.init_dataframe((
                tbqj__bkq, arr), index, (' ', ''))
            return ccpcb__polib.groupby(' ')['']
        return impl_index
    bkrgt__blhg = by
    if isinstance(by, SeriesType):
        bkrgt__blhg = by.data
    if isinstance(bkrgt__blhg, DecimalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with decimal type is not supported yet.'
            )
    if isinstance(by, bodo.hiframes.pd_categorical_ext.CategoricalArrayType):
        raise BodoError(
            'Series.groupby(): by argument with categorical type is not supported yet.'
            )

    def impl(S, by=None, axis=0, level=None, as_index=True, sort=True,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        tbqj__bkq = bodo.utils.conversion.coerce_to_array(by)
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        ccpcb__polib = bodo.hiframes.pd_dataframe_ext.init_dataframe((
            tbqj__bkq, arr), index, (' ', ''))
        return ccpcb__polib.groupby(' ')['']
    return impl


@overload_method(SeriesType, 'append', inline='always', no_unliteral=True)
def overload_series_append(S, to_append, ignore_index=False,
    verify_integrity=False):
    jvj__mfiy = dict(verify_integrity=verify_integrity)
    ufkf__cznec = dict(verify_integrity=False)
    check_unsupported_args('Series.append', jvj__mfiy, ufkf__cznec,
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
            mvclc__bywke = bodo.utils.conversion.coerce_to_array(values)
            A = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(A)
            frmz__qgre = np.empty(n, np.bool_)
            bodo.libs.array.array_isin(frmz__qgre, A, mvclc__bywke, False)
            return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                index, name)
        return impl_arr
    if not isinstance(values, (types.Set, types.List)):
        raise BodoError(
            "Series.isin(): 'values' parameter should be a set or a list")

    def impl(S, values):
        A = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        frmz__qgre = bodo.libs.array_ops.array_op_isin(A, values)
        return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, index, name)
    return impl


@overload_method(SeriesType, 'quantile', inline='always', no_unliteral=True)
def overload_series_quantile(S, q=0.5, interpolation='linear'):
    jvj__mfiy = dict(interpolation=interpolation)
    ufkf__cznec = dict(interpolation='linear')
    check_unsupported_args('Series.quantile', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')
    if is_iterable_type(q) and isinstance(q.dtype, types.Number):

        def impl_list(S, q=0.5, interpolation='linear'):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            frmz__qgre = bodo.libs.array_ops.array_op_quantile(arr, q)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            index = bodo.hiframes.pd_index_ext.init_numeric_index(bodo.
                utils.conversion.coerce_to_array(q), None)
            return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
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
        dxbx__kkx = bodo.libs.array_kernels.unique(arr)
        return bodo.allgatherv(dxbx__kkx, False)
    return impl


@overload_method(SeriesType, 'describe', inline='always', no_unliteral=True)
def overload_series_describe(S, percentiles=None, include=None, exclude=
    None, datetime_is_numeric=True):
    jvj__mfiy = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    ufkf__cznec = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('Series.describe', jvj__mfiy, ufkf__cznec,
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
        ljkyx__vqx = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        ljkyx__vqx = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    kgre__ctvk = '\n'.join(('def impl(', '    S,', '    value=None,',
        '    method=None,', '    axis=None,', '    inplace=False,',
        '    limit=None,', '    downcast=None,', '):',
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)',
        '    fill_arr = bodo.hiframes.pd_series_ext.get_series_data(value)',
        '    n = len(in_arr)', '    nf = len(fill_arr)',
        "    assert n == nf, 'fillna() requires same length arrays'",
        f'    out_arr = {ljkyx__vqx}(n, -1)',
        '    for j in numba.parfors.parfor.internal_prange(n):',
        '        s = in_arr[j]',
        '        if bodo.libs.array_kernels.isna(in_arr, j) and not bodo.libs.array_kernels.isna('
        , '            fill_arr, j', '        ):',
        '            s = fill_arr[j]', '        out_arr[j] = s',
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)'
        ))
    lfe__jogfq = dict()
    exec(kgre__ctvk, {'bodo': bodo, 'numba': numba}, lfe__jogfq)
    erta__xwwl = lfe__jogfq['impl']
    return erta__xwwl


def binary_str_fillna_inplace_impl(is_binary=False):
    if is_binary:
        ljkyx__vqx = 'bodo.libs.binary_arr_ext.pre_alloc_binary_array'
    else:
        ljkyx__vqx = 'bodo.libs.str_arr_ext.pre_alloc_string_array'
    kgre__ctvk = 'def impl(S,\n'
    kgre__ctvk += '     value=None,\n'
    kgre__ctvk += '    method=None,\n'
    kgre__ctvk += '    axis=None,\n'
    kgre__ctvk += '    inplace=False,\n'
    kgre__ctvk += '    limit=None,\n'
    kgre__ctvk += '   downcast=None,\n'
    kgre__ctvk += '):\n'
    kgre__ctvk += (
        '    in_arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
    kgre__ctvk += '    n = len(in_arr)\n'
    kgre__ctvk += f'    out_arr = {ljkyx__vqx}(n, -1)\n'
    kgre__ctvk += '    for j in numba.parfors.parfor.internal_prange(n):\n'
    kgre__ctvk += '        s = in_arr[j]\n'
    kgre__ctvk += '        if bodo.libs.array_kernels.isna(in_arr, j):\n'
    kgre__ctvk += '            s = value\n'
    kgre__ctvk += '        out_arr[j] = s\n'
    kgre__ctvk += (
        '    bodo.libs.str_arr_ext.move_str_binary_arr_payload(in_arr, out_arr)\n'
        )
    lfe__jogfq = dict()
    exec(kgre__ctvk, {'bodo': bodo, 'numba': numba}, lfe__jogfq)
    erta__xwwl = lfe__jogfq['impl']
    return erta__xwwl


def fillna_inplace_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    jjft__olz = bodo.hiframes.pd_series_ext.get_series_data(S)
    rsl__ogirx = bodo.hiframes.pd_series_ext.get_series_data(value)
    for zrgqo__vscf in numba.parfors.parfor.internal_prange(len(jjft__olz)):
        s = jjft__olz[zrgqo__vscf]
        if bodo.libs.array_kernels.isna(jjft__olz, zrgqo__vscf
            ) and not bodo.libs.array_kernels.isna(rsl__ogirx, zrgqo__vscf):
            s = rsl__ogirx[zrgqo__vscf]
        jjft__olz[zrgqo__vscf] = s


def fillna_inplace_impl(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    jjft__olz = bodo.hiframes.pd_series_ext.get_series_data(S)
    for zrgqo__vscf in numba.parfors.parfor.internal_prange(len(jjft__olz)):
        s = jjft__olz[zrgqo__vscf]
        if bodo.libs.array_kernels.isna(jjft__olz, zrgqo__vscf):
            s = value
        jjft__olz[zrgqo__vscf] = s


def str_fillna_alloc_series_impl(S, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    jjft__olz = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    rsl__ogirx = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(jjft__olz)
    frmz__qgre = bodo.libs.str_arr_ext.pre_alloc_string_array(n, -1)
    for ifq__gfcw in numba.parfors.parfor.internal_prange(n):
        s = jjft__olz[ifq__gfcw]
        if bodo.libs.array_kernels.isna(jjft__olz, ifq__gfcw
            ) and not bodo.libs.array_kernels.isna(rsl__ogirx, ifq__gfcw):
            s = rsl__ogirx[ifq__gfcw]
        frmz__qgre[ifq__gfcw] = s
        if bodo.libs.array_kernels.isna(jjft__olz, ifq__gfcw
            ) and bodo.libs.array_kernels.isna(rsl__ogirx, ifq__gfcw):
            bodo.libs.array_kernels.setna(frmz__qgre, ifq__gfcw)
    return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, index, name)


def fillna_series_impl(S, value=None, method=None, axis=None, inplace=False,
    limit=None, downcast=None):
    jjft__olz = bodo.hiframes.pd_series_ext.get_series_data(S)
    index = bodo.hiframes.pd_series_ext.get_series_index(S)
    name = bodo.hiframes.pd_series_ext.get_series_name(S)
    rsl__ogirx = bodo.hiframes.pd_series_ext.get_series_data(value)
    n = len(jjft__olz)
    frmz__qgre = bodo.utils.utils.alloc_type(n, jjft__olz.dtype, (-1,))
    for zrgqo__vscf in numba.parfors.parfor.internal_prange(n):
        s = jjft__olz[zrgqo__vscf]
        if bodo.libs.array_kernels.isna(jjft__olz, zrgqo__vscf
            ) and not bodo.libs.array_kernels.isna(rsl__ogirx, zrgqo__vscf):
            s = rsl__ogirx[zrgqo__vscf]
        frmz__qgre[zrgqo__vscf] = s
    return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, index, name)


@overload_method(SeriesType, 'fillna', no_unliteral=True)
def overload_series_fillna(S, value=None, method=None, axis=None, inplace=
    False, limit=None, downcast=None):
    jvj__mfiy = dict(limit=limit, downcast=downcast)
    ufkf__cznec = dict(limit=None, downcast=None)
    check_unsupported_args('Series.fillna', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')
    krpsh__jpu = not is_overload_none(value)
    xzjnq__rvaw = not is_overload_none(method)
    if krpsh__jpu and xzjnq__rvaw:
        raise BodoError(
            "Series.fillna(): Cannot specify both 'value' and 'method'.")
    if not krpsh__jpu and not xzjnq__rvaw:
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
    if xzjnq__rvaw:
        if is_overload_true(inplace):
            raise BodoError(
                "Series.fillna() with inplace=True not supported with 'method' argument yet."
                )
        mbos__lyfk = (
            "Series.fillna(): 'method' argument if provided must be a constant string and one of ('backfill', 'bfill', 'pad' 'ffill')."
            )
        if not is_overload_constant_str(method):
            raise_bodo_error(mbos__lyfk)
        elif get_overload_const_str(method) not in ('backfill', 'bfill',
            'pad', 'ffill'):
            raise BodoError(mbos__lyfk)
    mjekg__lvr = element_type(S.data)
    smo__mrrox = None
    if krpsh__jpu:
        smo__mrrox = element_type(types.unliteral(value))
    if smo__mrrox and not can_replace(mjekg__lvr, smo__mrrox):
        raise BodoError(
            f'Series.fillna(): Cannot use value type {smo__mrrox} with series type {mjekg__lvr}'
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
        xrggx__vdd = S.data
        if isinstance(value, SeriesType):

            def fillna_series_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                jjft__olz = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                rsl__ogirx = bodo.hiframes.pd_series_ext.get_series_data(value)
                n = len(jjft__olz)
                frmz__qgre = bodo.utils.utils.alloc_type(n, xrggx__vdd, (-1,))
                for zrgqo__vscf in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(jjft__olz, zrgqo__vscf
                        ) and bodo.libs.array_kernels.isna(rsl__ogirx,
                        zrgqo__vscf):
                        bodo.libs.array_kernels.setna(frmz__qgre, zrgqo__vscf)
                        continue
                    if bodo.libs.array_kernels.isna(jjft__olz, zrgqo__vscf):
                        frmz__qgre[zrgqo__vscf
                            ] = bodo.utils.conversion.unbox_if_timestamp(
                            rsl__ogirx[zrgqo__vscf])
                        continue
                    frmz__qgre[zrgqo__vscf
                        ] = bodo.utils.conversion.unbox_if_timestamp(jjft__olz
                        [zrgqo__vscf])
                return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                    index, name)
            return fillna_series_impl
        if xzjnq__rvaw:
            bnb__akx = (types.unicode_type, types.bool_, bodo.datetime64ns,
                bodo.timedelta64ns)
            if not isinstance(mjekg__lvr, (types.Integer, types.Float)
                ) and mjekg__lvr not in bnb__akx:
                raise BodoError(
                    f"Series.fillna(): series of type {mjekg__lvr} are not supported with 'method' argument."
                    )

            def fillna_method_impl(S, value=None, method=None, axis=None,
                inplace=False, limit=None, downcast=None):
                jjft__olz = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                frmz__qgre = bodo.libs.array_kernels.ffill_bfill_arr(jjft__olz,
                    method)
                return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                    index, name)
            return fillna_method_impl

        def fillna_impl(S, value=None, method=None, axis=None, inplace=
            False, limit=None, downcast=None):
            value = bodo.utils.conversion.unbox_if_timestamp(value)
            jjft__olz = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            n = len(jjft__olz)
            frmz__qgre = bodo.utils.utils.alloc_type(n, xrggx__vdd, (-1,))
            for zrgqo__vscf in numba.parfors.parfor.internal_prange(n):
                s = bodo.utils.conversion.unbox_if_timestamp(jjft__olz[
                    zrgqo__vscf])
                if bodo.libs.array_kernels.isna(jjft__olz, zrgqo__vscf):
                    s = value
                frmz__qgre[zrgqo__vscf] = s
            return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                index, name)
        return fillna_impl


def create_fillna_specific_method_overload(overload_name):

    def overload_series_fillna_specific_method(S, axis=None, inplace=False,
        limit=None, downcast=None):
        ttvw__pzalu = {'ffill': 'ffill', 'bfill': 'bfill', 'pad': 'ffill',
            'backfill': 'bfill'}[overload_name]
        jvj__mfiy = dict(limit=limit, downcast=downcast)
        ufkf__cznec = dict(limit=None, downcast=None)
        check_unsupported_args(f'Series.{overload_name}', jvj__mfiy,
            ufkf__cznec, package_name='pandas', module_name='Series')
        if not (is_overload_none(axis) or is_overload_zero(axis)):
            raise BodoError(
                f'Series.{overload_name}(): axis argument not supported')
        mjekg__lvr = element_type(S.data)
        bnb__akx = (types.unicode_type, types.bool_, bodo.datetime64ns,
            bodo.timedelta64ns)
        if not isinstance(mjekg__lvr, (types.Integer, types.Float)
            ) and mjekg__lvr not in bnb__akx:
            raise BodoError(
                f'Series.{overload_name}(): series of type {mjekg__lvr} are not supported.'
                )

        def impl(S, axis=None, inplace=False, limit=None, downcast=None):
            jjft__olz = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            frmz__qgre = bodo.libs.array_kernels.ffill_bfill_arr(jjft__olz,
                ttvw__pzalu)
            return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                index, name)
        return impl
    return overload_series_fillna_specific_method


fillna_specific_methods = 'ffill', 'bfill', 'pad', 'backfill'


def _install_fillna_specific_methods():
    for overload_name in fillna_specific_methods:
        kod__fgq = create_fillna_specific_method_overload(overload_name)
        overload_method(SeriesType, overload_name, no_unliteral=True)(kod__fgq)


_install_fillna_specific_methods()


def check_unsupported_types(S, to_replace, value):
    if any(bodo.utils.utils.is_array_typ(x, True) for x in [S.dtype,
        to_replace, value]):
        zvqmn__sfa = (
            'Series.replace(): only support with Scalar, List, or Dictionary')
        raise BodoError(zvqmn__sfa)
    elif isinstance(to_replace, types.DictType) and not is_overload_none(value
        ):
        zvqmn__sfa = (
            "Series.replace(): 'value' must be None when 'to_replace' is a dictionary"
            )
        raise BodoError(zvqmn__sfa)
    elif any(isinstance(x, (PandasTimestampType, PDTimeDeltaType)) for x in
        [to_replace, value]):
        zvqmn__sfa = (
            f'Series.replace(): Not supported for types {to_replace} and {value}'
            )
        raise BodoError(zvqmn__sfa)


def series_replace_error_checking(S, to_replace, value, inplace, limit,
    regex, method):
    jvj__mfiy = dict(inplace=inplace, limit=limit, regex=regex, method=method)
    cys__fyt = dict(inplace=False, limit=None, regex=False, method='pad')
    check_unsupported_args('Series.replace', jvj__mfiy, cys__fyt,
        package_name='pandas', module_name='Series')
    check_unsupported_types(S, to_replace, value)


@overload_method(SeriesType, 'replace', inline='always', no_unliteral=True)
def overload_series_replace(S, to_replace=None, value=None, inplace=False,
    limit=None, regex=False, method='pad'):
    series_replace_error_checking(S, to_replace, value, inplace, limit,
        regex, method)
    mjekg__lvr = element_type(S.data)
    if isinstance(to_replace, types.DictType):
        fpqq__qeoh = element_type(to_replace.key_type)
        smo__mrrox = element_type(to_replace.value_type)
    else:
        fpqq__qeoh = element_type(to_replace)
        smo__mrrox = element_type(value)
    ucxe__sez = None
    if mjekg__lvr != types.unliteral(fpqq__qeoh):
        if bodo.utils.typing.equality_always_false(mjekg__lvr, types.
            unliteral(fpqq__qeoh)
            ) or not bodo.utils.typing.types_equality_exists(mjekg__lvr,
            fpqq__qeoh):

            def impl(S, to_replace=None, value=None, inplace=False, limit=
                None, regex=False, method='pad'):
                return S.copy()
            return impl
        if isinstance(mjekg__lvr, (types.Float, types.Integer)
            ) or mjekg__lvr == np.bool_:
            ucxe__sez = mjekg__lvr
    if not can_replace(mjekg__lvr, types.unliteral(smo__mrrox)):

        def impl(S, to_replace=None, value=None, inplace=False, limit=None,
            regex=False, method='pad'):
            return S.copy()
        return impl
    wseoo__pdkk = S.data
    if isinstance(wseoo__pdkk, CategoricalArrayType):

        def cat_impl(S, to_replace=None, value=None, inplace=False, limit=
            None, regex=False, method='pad'):
            jjft__olz = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            return bodo.hiframes.pd_series_ext.init_series(jjft__olz.
                replace(to_replace, value), index, name)
        return cat_impl

    def impl(S, to_replace=None, value=None, inplace=False, limit=None,
        regex=False, method='pad'):
        jjft__olz = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        n = len(jjft__olz)
        frmz__qgre = bodo.utils.utils.alloc_type(n, wseoo__pdkk, (-1,))
        akaoc__qaide = build_replace_dict(to_replace, value, ucxe__sez)
        for zrgqo__vscf in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(jjft__olz, zrgqo__vscf):
                bodo.libs.array_kernels.setna(frmz__qgre, zrgqo__vscf)
                continue
            s = jjft__olz[zrgqo__vscf]
            if s in akaoc__qaide:
                s = akaoc__qaide[s]
            frmz__qgre[zrgqo__vscf] = s
        return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, index, name)
    return impl


def build_replace_dict(to_replace, value, key_dtype_conv):
    pass


@overload(build_replace_dict)
def _build_replace_dict(to_replace, value, key_dtype_conv):
    dgra__poqzo = isinstance(to_replace, (types.Number, Decimal128Type)
        ) or to_replace in [bodo.string_type, types.boolean, bodo.bytes_type]
    usli__qfso = is_iterable_type(to_replace)
    rnuf__wjxo = isinstance(value, (types.Number, Decimal128Type)
        ) or value in [bodo.string_type, bodo.bytes_type, types.boolean]
    hwzt__huvur = is_iterable_type(value)
    if dgra__poqzo and rnuf__wjxo:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                akaoc__qaide = {}
                akaoc__qaide[key_dtype_conv(to_replace)] = value
                return akaoc__qaide
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            akaoc__qaide = {}
            akaoc__qaide[to_replace] = value
            return akaoc__qaide
        return impl
    if usli__qfso and rnuf__wjxo:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                akaoc__qaide = {}
                for maax__lmaqj in to_replace:
                    akaoc__qaide[key_dtype_conv(maax__lmaqj)] = value
                return akaoc__qaide
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            akaoc__qaide = {}
            for maax__lmaqj in to_replace:
                akaoc__qaide[maax__lmaqj] = value
            return akaoc__qaide
        return impl
    if usli__qfso and hwzt__huvur:
        if not is_overload_none(key_dtype_conv):

            def impl_cast(to_replace, value, key_dtype_conv):
                akaoc__qaide = {}
                assert len(to_replace) == len(value
                    ), 'To_replace and value lengths must be the same'
                for zrgqo__vscf in range(len(to_replace)):
                    akaoc__qaide[key_dtype_conv(to_replace[zrgqo__vscf])
                        ] = value[zrgqo__vscf]
                return akaoc__qaide
            return impl_cast

        def impl(to_replace, value, key_dtype_conv):
            akaoc__qaide = {}
            assert len(to_replace) == len(value
                ), 'To_replace and value lengths must be the same'
            for zrgqo__vscf in range(len(to_replace)):
                akaoc__qaide[to_replace[zrgqo__vscf]] = value[zrgqo__vscf]
            return akaoc__qaide
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
            frmz__qgre = bodo.hiframes.series_impl.dt64_arr_sub(arr, bodo.
                hiframes.rolling.shift(arr, periods, False))
            return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                index, name)
        return impl_datetime

    def impl(S, periods=1):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        frmz__qgre = arr - bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, index, name)
    return impl


@overload_method(SeriesType, 'explode', inline='always', no_unliteral=True)
def overload_series_explode(S, ignore_index=False):
    from bodo.hiframes.split_impl import string_array_split_view_type
    jvj__mfiy = dict(ignore_index=ignore_index)
    cvb__ghu = dict(ignore_index=False)
    check_unsupported_args('Series.explode', jvj__mfiy, cvb__ghu,
        package_name='pandas', module_name='Series')
    if not (isinstance(S.data, ArrayItemArrayType) or S.data ==
        string_array_split_view_type):
        return lambda S, ignore_index=False: S.copy()

    def impl(S, ignore_index=False):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hyv__fuxa = bodo.utils.conversion.index_to_array(index)
        frmz__qgre, ayopr__xtqj = bodo.libs.array_kernels.explode(arr,
            hyv__fuxa)
        yjr__gjb = bodo.utils.conversion.index_from_array(ayopr__xtqj)
        return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, yjr__gjb,
            name)
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
            pvcba__wvosh = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for zrgqo__vscf in numba.parfors.parfor.internal_prange(n):
                pvcba__wvosh[zrgqo__vscf] = np.argmax(a[zrgqo__vscf])
            return pvcba__wvosh
        return impl


@overload(np.argmin, inline='always', no_unliteral=True)
def argmin_overload(a, axis=None, out=None):
    if isinstance(a, types.Array) and is_overload_constant_int(axis
        ) and get_overload_const_int(axis) == 1:

        def impl(a, axis=None, out=None):
            niwr__bobwh = np.empty(len(a), a.dtype)
            numba.parfors.parfor.init_prange()
            n = len(a)
            for zrgqo__vscf in numba.parfors.parfor.internal_prange(n):
                niwr__bobwh[zrgqo__vscf] = np.argmin(a[zrgqo__vscf])
            return niwr__bobwh
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
    jvj__mfiy = dict(axis=axis, inplace=inplace, how=how)
    xvcec__frxql = dict(axis=0, inplace=False, how=None)
    check_unsupported_args('Series.dropna', jvj__mfiy, xvcec__frxql,
        package_name='pandas', module_name='Series')
    if S.dtype == bodo.string_type:

        def dropna_str_impl(S, axis=0, inplace=False, how=None):
            jjft__olz = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            aphsh__caad = S.notna().values
            hyv__fuxa = bodo.utils.conversion.extract_index_array(S)
            yjr__gjb = bodo.utils.conversion.convert_to_index(hyv__fuxa[
                aphsh__caad])
            frmz__qgre = (bodo.hiframes.series_kernels.
                _series_dropna_str_alloc_impl_inner(jjft__olz))
            return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                yjr__gjb, name)
        return dropna_str_impl
    else:

        def dropna_impl(S, axis=0, inplace=False, how=None):
            jjft__olz = bodo.hiframes.pd_series_ext.get_series_data(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            hyv__fuxa = bodo.utils.conversion.extract_index_array(S)
            aphsh__caad = S.notna().values
            yjr__gjb = bodo.utils.conversion.convert_to_index(hyv__fuxa[
                aphsh__caad])
            frmz__qgre = jjft__olz[aphsh__caad]
            return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                yjr__gjb, name)
        return dropna_impl


@overload_method(SeriesType, 'shift', inline='always', no_unliteral=True)
def overload_series_shift(S, periods=1, freq=None, axis=0, fill_value=None):
    jvj__mfiy = dict(freq=freq, axis=axis, fill_value=fill_value)
    ufkf__cznec = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('Series.shift', jvj__mfiy, ufkf__cznec,
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
        frmz__qgre = bodo.hiframes.rolling.shift(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, index, name)
    return impl


@overload_method(SeriesType, 'pct_change', inline='always', no_unliteral=True)
def overload_series_pct_change(S, periods=1, fill_method='pad', limit=None,
    freq=None):
    jvj__mfiy = dict(fill_method=fill_method, limit=limit, freq=freq)
    ufkf__cznec = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('Series.pct_change', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')
    if not is_overload_int(periods):
        raise BodoError(
            'Series.pct_change(): periods argument must be an Integer')

    def impl(S, periods=1, fill_method='pad', limit=None, freq=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        frmz__qgre = bodo.hiframes.rolling.pct_change(arr, periods, False)
        return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, index, name)
    return impl


def create_series_mask_where_overload(func_name):

    def overload_series_mask_where(S, cond, other=np.nan, inplace=False,
        axis=None, level=None, errors='raise', try_cast=False):
        _validate_arguments_mask_where(f'Series.{func_name}', S, cond,
            other, inplace, axis, level, errors, try_cast)
        if is_overload_constant_nan(other):
            ftjr__itsyz = 'None'
        else:
            ftjr__itsyz = 'other'
        kgre__ctvk = """def impl(S, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise',try_cast=False):
"""
        if func_name == 'mask':
            kgre__ctvk += '  cond = ~cond\n'
        kgre__ctvk += (
            '  arr = bodo.hiframes.pd_series_ext.get_series_data(S)\n')
        kgre__ctvk += (
            '  index = bodo.hiframes.pd_series_ext.get_series_index(S)\n')
        kgre__ctvk += (
            '  name = bodo.hiframes.pd_series_ext.get_series_name(S)\n')
        kgre__ctvk += f"""  out_arr = bodo.hiframes.series_impl.where_impl(cond, arr, {ftjr__itsyz})
"""
        kgre__ctvk += (
            '  return bodo.hiframes.pd_series_ext.init_series(out_arr, index, name)\n'
            )
        qgrcw__fuy = {}
        exec(kgre__ctvk, {'bodo': bodo, 'np': np}, qgrcw__fuy)
        impl = qgrcw__fuy['impl']
        return impl
    return overload_series_mask_where


def _install_series_mask_where_overload():
    for func_name in ('mask', 'where'):
        kod__fgq = create_series_mask_where_overload(func_name)
        overload_method(SeriesType, func_name, no_unliteral=True)(kod__fgq)


_install_series_mask_where_overload()


def _validate_arguments_mask_where(func_name, S, cond, other, inplace, axis,
    level, errors, try_cast):
    jvj__mfiy = dict(inplace=inplace, level=level, errors=errors, try_cast=
        try_cast)
    ufkf__cznec = dict(inplace=False, level=None, errors='raise', try_cast=
        False)
    check_unsupported_args(f'{func_name}', jvj__mfiy, ufkf__cznec,
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
    syepu__zqdx = is_overload_constant_nan(other)
    if not (is_default or syepu__zqdx or is_scalar_type(other) or 
        isinstance(other, types.Array) and other.ndim >= 1 and other.ndim <=
        max_ndim or isinstance(other, SeriesType) and (isinstance(arr,
        types.Array) or arr.dtype in [bodo.string_type, bodo.bytes_type]) or
        isinstance(other, StringArrayType) and (arr.dtype == bodo.
        string_type or isinstance(arr, bodo.CategoricalArrayType) and arr.
        dtype.elem_type == bodo.string_type) or isinstance(other,
        BinaryArrayType) and (arr.dtype == bodo.bytes_type or isinstance(
        arr, bodo.CategoricalArrayType) and arr.dtype.elem_type == bodo.
        bytes_type) or (not isinstance(other, (StringArrayType,
        BinaryArrayType)) and (isinstance(arr.dtype, types.Integer) and (
        bodo.utils.utils.is_array_typ(other) and isinstance(other.dtype,
        types.Integer) or is_series_type(other) and isinstance(other.dtype,
        types.Integer))) or (bodo.utils.utils.is_array_typ(other) and arr.
        dtype == other.dtype or is_series_type(other) and arr.dtype ==
        other.dtype)) and (isinstance(arr, BooleanArrayType) or isinstance(
        arr, IntegerArrayType))):
        raise BodoError(
            f"{func_name}() 'other' must be a scalar, non-categorical series, 1-dim numpy array or StringArray with a matching type for Series."
            )
    if not is_default:
        if isinstance(arr.dtype, bodo.PDCategoricalDtype):
            ziph__pnozs = arr.dtype.elem_type
        else:
            ziph__pnozs = arr.dtype
        if is_iterable_type(other):
            rta__llh = other.dtype
        elif syepu__zqdx:
            rta__llh = types.float64
        else:
            rta__llh = types.unliteral(other)
        if not syepu__zqdx and not is_common_scalar_dtype([ziph__pnozs,
            rta__llh]):
            raise BodoError(
                f"{func_name}() series and 'other' must share a common type.")


def create_explicit_binary_op_overload(op):

    def overload_series_explicit_binary_op(S, other, level=None, fill_value
        =None, axis=0):
        jvj__mfiy = dict(level=level, axis=axis)
        ufkf__cznec = dict(level=None, axis=0)
        check_unsupported_args('series.{}'.format(op.__name__), jvj__mfiy,
            ufkf__cznec, package_name='pandas', module_name='Series')
        vqpm__hoo = other == string_type or is_overload_constant_str(other)
        ujgkm__agy = is_iterable_type(other) and other.dtype == string_type
        fcf__bslg = S.dtype == string_type and (op == operator.add and (
            vqpm__hoo or ujgkm__agy) or op == operator.mul and isinstance(
            other, types.Integer))
        sns__vph = S.dtype == bodo.timedelta64ns
        lpx__rav = S.dtype == bodo.datetime64ns
        ufqt__dbl = is_iterable_type(other) and (other.dtype ==
            datetime_timedelta_type or other.dtype == bodo.timedelta64ns)
        lcds__eyw = is_iterable_type(other) and (other.dtype ==
            datetime_datetime_type or other.dtype == pd_timestamp_type or 
            other.dtype == bodo.datetime64ns)
        wfqj__uyl = sns__vph and (ufqt__dbl or lcds__eyw
            ) or lpx__rav and ufqt__dbl
        wfqj__uyl = wfqj__uyl and op == operator.add
        if not (isinstance(S.dtype, types.Number) or fcf__bslg or wfqj__uyl):
            raise BodoError(f'Unsupported types for Series.{op.__name__}')
        kmbxm__yqxq = numba.core.registry.cpu_target.typing_context
        if is_scalar_type(other):
            args = S.data, other
            wseoo__pdkk = kmbxm__yqxq.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and wseoo__pdkk == types.Array(types.bool_, 1, 'C'):
                wseoo__pdkk = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                other = bodo.utils.conversion.unbox_if_timestamp(other)
                n = len(arr)
                frmz__qgre = bodo.utils.utils.alloc_type(n, wseoo__pdkk, (-1,))
                for zrgqo__vscf in numba.parfors.parfor.internal_prange(n):
                    suqcy__gjer = bodo.libs.array_kernels.isna(arr, zrgqo__vscf
                        )
                    if suqcy__gjer:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(frmz__qgre,
                                zrgqo__vscf)
                        else:
                            frmz__qgre[zrgqo__vscf] = op(fill_value, other)
                    else:
                        frmz__qgre[zrgqo__vscf] = op(arr[zrgqo__vscf], other)
                return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                    index, name)
            return impl_scalar
        args = S.data, types.Array(other.dtype, 1, 'C')
        wseoo__pdkk = kmbxm__yqxq.resolve_function_type(op, args, {}
            ).return_type
        if isinstance(S.data, IntegerArrayType) and wseoo__pdkk == types.Array(
            types.bool_, 1, 'C'):
            wseoo__pdkk = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            xnaw__jemq = bodo.utils.conversion.coerce_to_array(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            frmz__qgre = bodo.utils.utils.alloc_type(n, wseoo__pdkk, (-1,))
            for zrgqo__vscf in numba.parfors.parfor.internal_prange(n):
                suqcy__gjer = bodo.libs.array_kernels.isna(arr, zrgqo__vscf)
                xejw__jat = bodo.libs.array_kernels.isna(xnaw__jemq,
                    zrgqo__vscf)
                if suqcy__gjer and xejw__jat:
                    bodo.libs.array_kernels.setna(frmz__qgre, zrgqo__vscf)
                elif suqcy__gjer:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(frmz__qgre, zrgqo__vscf)
                    else:
                        frmz__qgre[zrgqo__vscf] = op(fill_value, xnaw__jemq
                            [zrgqo__vscf])
                elif xejw__jat:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(frmz__qgre, zrgqo__vscf)
                    else:
                        frmz__qgre[zrgqo__vscf] = op(arr[zrgqo__vscf],
                            fill_value)
                else:
                    frmz__qgre[zrgqo__vscf] = op(arr[zrgqo__vscf],
                        xnaw__jemq[zrgqo__vscf])
            return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
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
        kmbxm__yqxq = numba.core.registry.cpu_target.typing_context
        if isinstance(other, types.Number):
            args = other, S.data
            wseoo__pdkk = kmbxm__yqxq.resolve_function_type(op, args, {}
                ).return_type
            if isinstance(S.data, IntegerArrayType
                ) and wseoo__pdkk == types.Array(types.bool_, 1, 'C'):
                wseoo__pdkk = boolean_array

            def impl_scalar(S, other, level=None, fill_value=None, axis=0):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                numba.parfors.parfor.init_prange()
                n = len(arr)
                frmz__qgre = bodo.utils.utils.alloc_type(n, wseoo__pdkk, None)
                for zrgqo__vscf in numba.parfors.parfor.internal_prange(n):
                    suqcy__gjer = bodo.libs.array_kernels.isna(arr, zrgqo__vscf
                        )
                    if suqcy__gjer:
                        if fill_value is None:
                            bodo.libs.array_kernels.setna(frmz__qgre,
                                zrgqo__vscf)
                        else:
                            frmz__qgre[zrgqo__vscf] = op(other, fill_value)
                    else:
                        frmz__qgre[zrgqo__vscf] = op(other, arr[zrgqo__vscf])
                return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                    index, name)
            return impl_scalar
        args = types.Array(other.dtype, 1, 'C'), S.data
        wseoo__pdkk = kmbxm__yqxq.resolve_function_type(op, args, {}
            ).return_type
        if isinstance(S.data, IntegerArrayType) and wseoo__pdkk == types.Array(
            types.bool_, 1, 'C'):
            wseoo__pdkk = boolean_array

        def impl(S, other, level=None, fill_value=None, axis=0):
            arr = bodo.hiframes.pd_series_ext.get_series_data(S)
            index = bodo.hiframes.pd_series_ext.get_series_index(S)
            name = bodo.hiframes.pd_series_ext.get_series_name(S)
            xnaw__jemq = bodo.hiframes.pd_series_ext.get_series_data(other)
            numba.parfors.parfor.init_prange()
            n = len(arr)
            frmz__qgre = bodo.utils.utils.alloc_type(n, wseoo__pdkk, None)
            for zrgqo__vscf in numba.parfors.parfor.internal_prange(n):
                suqcy__gjer = bodo.libs.array_kernels.isna(arr, zrgqo__vscf)
                xejw__jat = bodo.libs.array_kernels.isna(xnaw__jemq,
                    zrgqo__vscf)
                frmz__qgre[zrgqo__vscf] = op(xnaw__jemq[zrgqo__vscf], arr[
                    zrgqo__vscf])
                if suqcy__gjer and xejw__jat:
                    bodo.libs.array_kernels.setna(frmz__qgre, zrgqo__vscf)
                elif suqcy__gjer:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(frmz__qgre, zrgqo__vscf)
                    else:
                        frmz__qgre[zrgqo__vscf] = op(xnaw__jemq[zrgqo__vscf
                            ], fill_value)
                elif xejw__jat:
                    if fill_value is None:
                        bodo.libs.array_kernels.setna(frmz__qgre, zrgqo__vscf)
                    else:
                        frmz__qgre[zrgqo__vscf] = op(fill_value, arr[
                            zrgqo__vscf])
                else:
                    frmz__qgre[zrgqo__vscf] = op(xnaw__jemq[zrgqo__vscf],
                        arr[zrgqo__vscf])
            return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
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
    for op, uzvk__pasgr in explicit_binop_funcs_two_ways.items():
        for name in uzvk__pasgr:
            kod__fgq = create_explicit_binary_op_overload(op)
            ddwqz__mqbq = create_explicit_binary_reverse_op_overload(op)
            ado__ljwj = 'r' + name
            overload_method(SeriesType, name, no_unliteral=True)(kod__fgq)
            overload_method(SeriesType, ado__ljwj, no_unliteral=True)(
                ddwqz__mqbq)
            explicit_binop_funcs.add(name)
    for op, name in explicit_binop_funcs_single.items():
        kod__fgq = create_explicit_binary_op_overload(op)
        overload_method(SeriesType, name, no_unliteral=True)(kod__fgq)
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
                ndso__xicl = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                frmz__qgre = dt64_arr_sub(arr, ndso__xicl)
                return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
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
                frmz__qgre = np.empty(n, np.dtype('datetime64[ns]'))
                for zrgqo__vscf in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(arr, zrgqo__vscf):
                        bodo.libs.array_kernels.setna(frmz__qgre, zrgqo__vscf)
                        continue
                    hao__fxd = (bodo.hiframes.pd_timestamp_ext.
                        convert_datetime64_to_timestamp(arr[zrgqo__vscf]))
                    zbdbv__mccwf = op(hao__fxd, rhs)
                    frmz__qgre[zrgqo__vscf
                        ] = bodo.hiframes.pd_timestamp_ext.integer_to_dt64(
                        zbdbv__mccwf.value)
                return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
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
                    ndso__xicl = (bodo.utils.conversion.
                        get_array_if_series_or_index(rhs))
                    frmz__qgre = op(arr, bodo.utils.conversion.
                        unbox_if_timestamp(ndso__xicl))
                    return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(lhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(lhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(lhs)
                ndso__xicl = (bodo.utils.conversion.
                    get_array_if_series_or_index(rhs))
                frmz__qgre = op(arr, ndso__xicl)
                return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                    index, name)
            return impl
        if isinstance(rhs, SeriesType):
            if rhs.dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

                def impl(lhs, rhs):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                    index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                    name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                    dvr__hhl = (bodo.utils.conversion.
                        get_array_if_series_or_index(lhs))
                    frmz__qgre = op(bodo.utils.conversion.
                        unbox_if_timestamp(dvr__hhl), arr)
                    return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                        index, name)
                return impl

            def impl(lhs, rhs):
                arr = bodo.hiframes.pd_series_ext.get_series_data(rhs)
                index = bodo.hiframes.pd_series_ext.get_series_index(rhs)
                name = bodo.hiframes.pd_series_ext.get_series_name(rhs)
                dvr__hhl = bodo.utils.conversion.get_array_if_series_or_index(
                    lhs)
                frmz__qgre = op(dvr__hhl, arr)
                return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                    index, name)
            return impl
    return overload_series_binary_op


skips = list(explicit_binop_funcs_two_ways.keys()) + list(
    explicit_binop_funcs_single.keys()) + split_logical_binops_funcs


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        kod__fgq = create_binary_op_overload(op)
        overload(op)(kod__fgq)


_install_binary_ops()


def dt64_arr_sub(arg1, arg2):
    return arg1 - arg2


@overload(dt64_arr_sub, no_unliteral=True)
def overload_dt64_arr_sub(arg1, arg2):
    assert arg1 == types.Array(bodo.datetime64ns, 1, 'C'
        ) and arg2 == types.Array(bodo.datetime64ns, 1, 'C')
    oxnk__awkt = np.dtype('timedelta64[ns]')

    def impl(arg1, arg2):
        numba.parfors.parfor.init_prange()
        n = len(arg1)
        S = np.empty(n, oxnk__awkt)
        for zrgqo__vscf in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(arg1, zrgqo__vscf
                ) or bodo.libs.array_kernels.isna(arg2, zrgqo__vscf):
                bodo.libs.array_kernels.setna(S, zrgqo__vscf)
                continue
            S[zrgqo__vscf
                ] = bodo.hiframes.pd_timestamp_ext.integer_to_timedelta64(
                bodo.hiframes.pd_timestamp_ext.dt64_to_integer(arg1[
                zrgqo__vscf]) - bodo.hiframes.pd_timestamp_ext.
                dt64_to_integer(arg2[zrgqo__vscf]))
        return S
    return impl


def create_inplace_binary_op_overload(op):

    def overload_series_inplace_binary_op(S, other):
        if isinstance(S, SeriesType) or isinstance(other, SeriesType):

            def impl(S, other):
                arr = bodo.utils.conversion.get_array_if_series_or_index(S)
                xnaw__jemq = (bodo.utils.conversion.
                    get_array_if_series_or_index(other))
                op(arr, xnaw__jemq)
                return S
            return impl
    return overload_series_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        kod__fgq = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(kod__fgq)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_series_unary_op(S):
        if isinstance(S, SeriesType):

            def impl(S):
                arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                index = bodo.hiframes.pd_series_ext.get_series_index(S)
                name = bodo.hiframes.pd_series_ext.get_series_name(S)
                frmz__qgre = op(arr)
                return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                    index, name)
            return impl
    return overload_series_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        kod__fgq = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(kod__fgq)


_install_unary_ops()


def create_ufunc_overload(ufunc):
    if ufunc.nin == 1:

        def overload_series_ufunc_nin_1(S):
            if isinstance(S, SeriesType):

                def impl(S):
                    arr = bodo.hiframes.pd_series_ext.get_series_data(S)
                    index = bodo.hiframes.pd_series_ext.get_series_index(S)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S)
                    frmz__qgre = ufunc(arr)
                    return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
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
                    xnaw__jemq = (bodo.utils.conversion.
                        get_array_if_series_or_index(S2))
                    frmz__qgre = ufunc(arr, xnaw__jemq)
                    return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                        index, name)
                return impl
            elif isinstance(S2, SeriesType):

                def impl(S1, S2):
                    arr = bodo.utils.conversion.get_array_if_series_or_index(S1
                        )
                    xnaw__jemq = bodo.hiframes.pd_series_ext.get_series_data(S2
                        )
                    index = bodo.hiframes.pd_series_ext.get_series_index(S2)
                    name = bodo.hiframes.pd_series_ext.get_series_name(S2)
                    frmz__qgre = ufunc(arr, xnaw__jemq)
                    return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                        index, name)
                return impl
        return overload_series_ufunc_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for ufunc in numba.np.ufunc_db.get_ufuncs():
        kod__fgq = create_ufunc_overload(ufunc)
        overload(ufunc, no_unliteral=True)(kod__fgq)


_install_np_ufuncs()


def argsort(A):
    return np.argsort(A)


@overload(argsort, no_unliteral=True)
def overload_argsort(A):

    def impl(A):
        n = len(A)
        pes__iyici = bodo.libs.str_arr_ext.to_list_if_immutable_arr((A.copy(),)
            )
        pwox__xyfml = np.arange(n),
        bodo.libs.timsort.sort(pes__iyici, 0, n, pwox__xyfml)
        return pwox__xyfml[0]
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
        fizvi__oprv = get_overload_const_str(downcast)
        if fizvi__oprv in ('integer', 'signed'):
            out_dtype = types.int64
        elif fizvi__oprv == 'unsigned':
            out_dtype = types.uint64
        else:
            assert fizvi__oprv == 'float'
    if isinstance(arg_a, (types.Array, IntegerArrayType)):
        return lambda arg_a, errors='raise', downcast=None: arg_a.astype(
            out_dtype)
    if isinstance(arg_a, SeriesType):

        def impl_series(arg_a, errors='raise', downcast=None):
            jjft__olz = bodo.hiframes.pd_series_ext.get_series_data(arg_a)
            index = bodo.hiframes.pd_series_ext.get_series_index(arg_a)
            name = bodo.hiframes.pd_series_ext.get_series_name(arg_a)
            frmz__qgre = pd.to_numeric(jjft__olz, errors, downcast)
            return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                index, name)
        return impl_series
    if arg_a != string_array_type:
        raise BodoError('pd.to_numeric(): invalid argument type {}'.format(
            arg_a))
    if out_dtype == types.float64:

        def to_numeric_float_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            nugh__ekw = np.empty(n, np.float64)
            for zrgqo__vscf in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, zrgqo__vscf):
                    bodo.libs.array_kernels.setna(nugh__ekw, zrgqo__vscf)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(nugh__ekw,
                        zrgqo__vscf, arg_a, zrgqo__vscf)
            return nugh__ekw
        return to_numeric_float_impl
    else:

        def to_numeric_int_impl(arg_a, errors='raise', downcast=None):
            numba.parfors.parfor.init_prange()
            n = len(arg_a)
            nugh__ekw = bodo.libs.int_arr_ext.alloc_int_array(n, np.int64)
            for zrgqo__vscf in numba.parfors.parfor.internal_prange(n):
                if bodo.libs.array_kernels.isna(arg_a, zrgqo__vscf):
                    bodo.libs.array_kernels.setna(nugh__ekw, zrgqo__vscf)
                else:
                    bodo.libs.str_arr_ext.str_arr_item_to_numeric(nugh__ekw,
                        zrgqo__vscf, arg_a, zrgqo__vscf)
            return nugh__ekw
        return to_numeric_int_impl


def series_filter_bool(arr, bool_arr):
    return arr[bool_arr]


@infer_global(series_filter_bool)
class SeriesFilterBoolInfer(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 2
        juq__vmc = if_series_to_array_type(args[0])
        if isinstance(juq__vmc, types.Array) and isinstance(juq__vmc.dtype,
            types.Integer):
            juq__vmc = types.Array(types.float64, 1, 'C')
        return juq__vmc(*args)


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
    dalx__omuh = bodo.utils.utils.is_array_typ(x, True)
    birl__aduqi = bodo.utils.utils.is_array_typ(y, True)
    kgre__ctvk = 'def _impl(condition, x, y):\n'
    if isinstance(condition, SeriesType):
        kgre__ctvk += (
            '  condition = bodo.hiframes.pd_series_ext.get_series_data(condition)\n'
            )
    if dalx__omuh and not bodo.utils.utils.is_array_typ(x, False):
        kgre__ctvk += '  x = bodo.utils.conversion.coerce_to_array(x)\n'
    if birl__aduqi and not bodo.utils.utils.is_array_typ(y, False):
        kgre__ctvk += '  y = bodo.utils.conversion.coerce_to_array(y)\n'
    kgre__ctvk += '  n = len(condition)\n'
    nizf__zjwjm = x.dtype if dalx__omuh else types.unliteral(x)
    egd__wxmpn = y.dtype if birl__aduqi else types.unliteral(y)
    if not isinstance(x, CategoricalArrayType):
        nizf__zjwjm = element_type(x)
    if not isinstance(y, CategoricalArrayType):
        egd__wxmpn = element_type(y)

    def get_data(x):
        if isinstance(x, SeriesType):
            return x.data
        elif isinstance(x, types.Array):
            return x
        return types.unliteral(x)
    ulbq__ycmsx = get_data(x)
    tuou__yok = get_data(y)
    is_nullable = any(bodo.utils.typing.is_nullable(pwox__xyfml) for
        pwox__xyfml in [ulbq__ycmsx, tuou__yok])
    if tuou__yok == types.none:
        if isinstance(nizf__zjwjm, types.Number):
            out_dtype = types.Array(types.float64, 1, 'C')
        else:
            out_dtype = to_nullable_type(x)
    elif ulbq__ycmsx == tuou__yok and not is_nullable:
        out_dtype = dtype_to_array_type(nizf__zjwjm)
    elif nizf__zjwjm == string_type or egd__wxmpn == string_type:
        out_dtype = bodo.string_array_type
    elif ulbq__ycmsx == bytes_type or (dalx__omuh and nizf__zjwjm == bytes_type
        ) and (tuou__yok == bytes_type or birl__aduqi and egd__wxmpn ==
        bytes_type):
        out_dtype = binary_array_type
    elif isinstance(nizf__zjwjm, bodo.PDCategoricalDtype):
        out_dtype = None
    elif nizf__zjwjm in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(nizf__zjwjm, 1, 'C')
    elif egd__wxmpn in [bodo.timedelta64ns, bodo.datetime64ns]:
        out_dtype = types.Array(egd__wxmpn, 1, 'C')
    else:
        out_dtype = numba.from_dtype(np.promote_types(numba.np.
            numpy_support.as_dtype(nizf__zjwjm), numba.np.numpy_support.
            as_dtype(egd__wxmpn)))
        out_dtype = types.Array(out_dtype, 1, 'C')
        if is_nullable:
            out_dtype = bodo.utils.typing.to_nullable_type(out_dtype)
    if isinstance(nizf__zjwjm, bodo.PDCategoricalDtype):
        brx__ywky = 'x'
    else:
        brx__ywky = 'out_dtype'
    kgre__ctvk += (
        f'  out_arr = bodo.utils.utils.alloc_type(n, {brx__ywky}, (-1,))\n')
    if isinstance(nizf__zjwjm, bodo.PDCategoricalDtype):
        kgre__ctvk += """  out_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(out_arr)
"""
        kgre__ctvk += (
            '  x_codes = bodo.hiframes.pd_categorical_ext.get_categorical_arr_codes(x)\n'
            )
    kgre__ctvk += '  for j in numba.parfors.parfor.internal_prange(n):\n'
    kgre__ctvk += (
        '    if not bodo.libs.array_kernels.isna(condition, j) and condition[j]:\n'
        )
    if dalx__omuh:
        kgre__ctvk += '      if bodo.libs.array_kernels.isna(x, j):\n'
        kgre__ctvk += '        setna(out_arr, j)\n'
        kgre__ctvk += '        continue\n'
    if isinstance(nizf__zjwjm, bodo.PDCategoricalDtype):
        kgre__ctvk += '      out_codes[j] = x_codes[j]\n'
    else:
        kgre__ctvk += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('x[j]' if dalx__omuh else 'x'))
    kgre__ctvk += '    else:\n'
    if birl__aduqi:
        kgre__ctvk += '      if bodo.libs.array_kernels.isna(y, j):\n'
        kgre__ctvk += '        setna(out_arr, j)\n'
        kgre__ctvk += '        continue\n'
    if tuou__yok == types.none:
        if isinstance(nizf__zjwjm, bodo.PDCategoricalDtype):
            kgre__ctvk += '      out_codes[j] = -1\n'
        else:
            kgre__ctvk += '      setna(out_arr, j)\n'
    else:
        kgre__ctvk += (
            '      out_arr[j] = bodo.utils.conversion.unbox_if_timestamp({})\n'
            .format('y[j]' if birl__aduqi else 'y'))
    kgre__ctvk += '  return out_arr\n'
    qgrcw__fuy = {}
    exec(kgre__ctvk, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'out_dtype': out_dtype}, qgrcw__fuy)
    pmcm__cxacd = qgrcw__fuy['_impl']
    return pmcm__cxacd


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
        uwgi__xtyb = choicelist.dtype
        if not bodo.utils.utils.is_array_typ(uwgi__xtyb, True):
            raise BodoError(
                "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                )
        if is_series_type(uwgi__xtyb):
            qlxew__seza = uwgi__xtyb.data.dtype
        else:
            qlxew__seza = uwgi__xtyb.dtype
        if isinstance(qlxew__seza, bodo.PDCategoricalDtype):
            raise BodoError(
                'np.select(): data with choicelist of type Categorical not yet supported'
                )
        whl__rpxva = uwgi__xtyb
    else:
        wdmc__sqrnc = []
        for uwgi__xtyb in choicelist:
            if not bodo.utils.utils.is_array_typ(uwgi__xtyb, True):
                raise BodoError(
                    "np.select(): 'choicelist' argument must be list or tuple of series/arrays types"
                    )
            if is_series_type(uwgi__xtyb):
                qlxew__seza = uwgi__xtyb.data.dtype
            else:
                qlxew__seza = uwgi__xtyb.dtype
            if isinstance(qlxew__seza, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            wdmc__sqrnc.append(qlxew__seza)
        if not is_common_scalar_dtype(wdmc__sqrnc):
            raise BodoError(
                f"np.select(): 'choicelist' items must be arrays with a commmon data type. Found a tuple with the following data types {choicelist}."
                )
        whl__rpxva = choicelist[0]
    if is_series_type(whl__rpxva):
        whl__rpxva = whl__rpxva.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        pass
    else:
        if not is_scalar_type(default):
            raise BodoError(
                "np.select(): 'default' argument must be scalar type")
        if not (is_common_scalar_dtype([default, whl__rpxva.dtype]) or 
            default == types.none or is_overload_constant_nan(default)):
            raise BodoError(
                f"np.select(): 'default' is not type compatible with the array types in choicelist. Choicelist type: {choicelist}, Default type: {default}"
                )
    if not (isinstance(whl__rpxva, types.Array) or isinstance(whl__rpxva,
        BooleanArrayType) or isinstance(whl__rpxva, IntegerArrayType) or 
        bodo.utils.utils.is_array_typ(whl__rpxva, False) and whl__rpxva.
        dtype in [bodo.string_type, bodo.bytes_type]):
        raise BodoError(
            f'np.select(): data with choicelist of type {whl__rpxva} not yet supported'
            )


@overload(np.select)
def overload_np_select(condlist, choicelist, default=0):
    _verify_np_select_arg_typs(condlist, choicelist, default)
    unp__lyiax = isinstance(choicelist, (types.List, types.UniTuple)
        ) and isinstance(condlist, (types.List, types.UniTuple))
    if isinstance(choicelist, (types.List, types.UniTuple)):
        rofo__cye = choicelist.dtype
    else:
        cil__opye = False
        wdmc__sqrnc = []
        for uwgi__xtyb in choicelist:
            if is_nullable_type(uwgi__xtyb):
                cil__opye = True
            if is_series_type(uwgi__xtyb):
                qlxew__seza = uwgi__xtyb.data.dtype
            else:
                qlxew__seza = uwgi__xtyb.dtype
            if isinstance(qlxew__seza, bodo.PDCategoricalDtype):
                raise BodoError(
                    'np.select(): data with choicelist of type Categorical not yet supported'
                    )
            wdmc__sqrnc.append(qlxew__seza)
        mfnx__rml, vob__wci = get_common_scalar_dtype(wdmc__sqrnc)
        if not vob__wci:
            raise BodoError('Internal error in overload_np_select')
        mttms__xqrig = dtype_to_array_type(mfnx__rml)
        if cil__opye:
            mttms__xqrig = to_nullable_type(mttms__xqrig)
        rofo__cye = mttms__xqrig
    if isinstance(rofo__cye, SeriesType):
        rofo__cye = rofo__cye.data
    if is_overload_constant_int(default) and get_overload_const_int(default
        ) == 0:
        vmkhn__zded = True
    else:
        vmkhn__zded = False
    bas__bspr = False
    eyhg__slcrr = False
    if vmkhn__zded:
        if isinstance(rofo__cye.dtype, types.Number):
            pass
        elif rofo__cye.dtype == types.bool_:
            eyhg__slcrr = True
        else:
            bas__bspr = True
            rofo__cye = to_nullable_type(rofo__cye)
    elif default == types.none or is_overload_constant_nan(default):
        bas__bspr = True
        rofo__cye = to_nullable_type(rofo__cye)
    kgre__ctvk = 'def np_select_impl(condlist, choicelist, default=0):\n'
    kgre__ctvk += '  if len(condlist) != len(choicelist):\n'
    kgre__ctvk += """    raise ValueError('list of cases must be same length as list of conditions')
"""
    kgre__ctvk += '  output_len = len(choicelist[0])\n'
    kgre__ctvk += (
        '  out = bodo.utils.utils.alloc_type(output_len, alloc_typ, (-1,))\n')
    kgre__ctvk += '  for i in range(output_len):\n'
    if bas__bspr:
        kgre__ctvk += '    bodo.libs.array_kernels.setna(out, i)\n'
    elif eyhg__slcrr:
        kgre__ctvk += '    out[i] = False\n'
    else:
        kgre__ctvk += '    out[i] = default\n'
    if unp__lyiax:
        kgre__ctvk += '  for i in range(len(condlist) - 1, -1, -1):\n'
        kgre__ctvk += '    cond = condlist[i]\n'
        kgre__ctvk += '    choice = choicelist[i]\n'
        kgre__ctvk += '    out = np.where(cond, choice, out)\n'
    else:
        for zrgqo__vscf in range(len(choicelist) - 1, -1, -1):
            kgre__ctvk += f'  cond = condlist[{zrgqo__vscf}]\n'
            kgre__ctvk += f'  choice = choicelist[{zrgqo__vscf}]\n'
            kgre__ctvk += f'  out = np.where(cond, choice, out)\n'
    kgre__ctvk += '  return out'
    qgrcw__fuy = dict()
    exec(kgre__ctvk, {'bodo': bodo, 'numba': numba, 'setna': bodo.libs.
        array_kernels.setna, 'np': np, 'alloc_typ': rofo__cye}, qgrcw__fuy)
    impl = qgrcw__fuy['np_select_impl']
    return impl


@overload_method(SeriesType, 'duplicated', inline='always', no_unliteral=True)
def overload_series_duplicated(S, keep='first'):

    def impl(S, keep='first'):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        frmz__qgre = bodo.libs.array_kernels.duplicated((arr,))
        return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, index, name)
    return impl


@overload_method(SeriesType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_series_drop_duplicates(S, subset=None, keep='first', inplace=False
    ):
    jvj__mfiy = dict(subset=subset, keep=keep, inplace=inplace)
    ufkf__cznec = dict(subset=None, keep='first', inplace=False)
    check_unsupported_args('Series.drop_duplicates', jvj__mfiy, ufkf__cznec,
        package_name='pandas', module_name='Series')

    def impl(S, subset=None, keep='first', inplace=False):
        zjd__jhmwv = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        (zjd__jhmwv,), hyv__fuxa = bodo.libs.array_kernels.drop_duplicates((
            zjd__jhmwv,), index, 1)
        index = bodo.utils.conversion.index_from_array(hyv__fuxa)
        return bodo.hiframes.pd_series_ext.init_series(zjd__jhmwv, index, name)
    return impl


@overload_method(SeriesType, 'between', inline='always', no_unliteral=True)
def overload_series_between(S, left, right, inclusive='both'):
    tncbx__ihbfq = element_type(S.data)
    if not is_common_scalar_dtype([tncbx__ihbfq, left]):
        raise_bodo_error(
            "Series.between(): 'left' must be compariable with the Series data"
            )
    if not is_common_scalar_dtype([tncbx__ihbfq, right]):
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
        frmz__qgre = np.empty(n, np.bool_)
        for zrgqo__vscf in numba.parfors.parfor.internal_prange(n):
            jlv__vte = bodo.utils.conversion.box_if_dt64(arr[zrgqo__vscf])
            if inclusive == 'both':
                frmz__qgre[zrgqo__vscf
                    ] = jlv__vte <= right and jlv__vte >= left
            else:
                frmz__qgre[zrgqo__vscf] = jlv__vte < right and jlv__vte > left
        return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, index, name)
    return impl


@overload_method(SeriesType, 'repeat', inline='always', no_unliteral=True)
def overload_series_repeat(S, repeats, axis=None):
    jvj__mfiy = dict(axis=axis)
    ufkf__cznec = dict(axis=None)
    check_unsupported_args('Series.repeat', jvj__mfiy, ufkf__cznec,
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
            hyv__fuxa = bodo.utils.conversion.index_to_array(index)
            frmz__qgre = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
            ayopr__xtqj = bodo.libs.array_kernels.repeat_kernel(hyv__fuxa,
                repeats)
            yjr__gjb = bodo.utils.conversion.index_from_array(ayopr__xtqj)
            return bodo.hiframes.pd_series_ext.init_series(frmz__qgre,
                yjr__gjb, name)
        return impl_int

    def impl_arr(S, repeats, axis=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        name = bodo.hiframes.pd_series_ext.get_series_name(S)
        hyv__fuxa = bodo.utils.conversion.index_to_array(index)
        repeats = bodo.utils.conversion.coerce_to_array(repeats)
        frmz__qgre = bodo.libs.array_kernels.repeat_kernel(arr, repeats)
        ayopr__xtqj = bodo.libs.array_kernels.repeat_kernel(hyv__fuxa, repeats)
        yjr__gjb = bodo.utils.conversion.index_from_array(ayopr__xtqj)
        return bodo.hiframes.pd_series_ext.init_series(frmz__qgre, yjr__gjb,
            name)
    return impl_arr


@overload_method(SeriesType, 'to_dict', no_unliteral=True)
def overload_to_dict(S, into=None):

    def impl(S, into=None):
        pwox__xyfml = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.utils.conversion.index_to_array(bodo.hiframes.
            pd_series_ext.get_series_index(S))
        n = len(pwox__xyfml)
        ytdf__lgv = {}
        for zrgqo__vscf in range(n):
            jlv__vte = bodo.utils.conversion.box_if_dt64(pwox__xyfml[
                zrgqo__vscf])
            ytdf__lgv[index[zrgqo__vscf]] = jlv__vte
        return ytdf__lgv
    return impl


@overload_method(SeriesType, 'to_frame', inline='always', no_unliteral=True)
def overload_series_to_frame(S, name=None):
    mbos__lyfk = (
        "Series.to_frame(): output column name should be known at compile time. Set 'name' to a constant value."
        )
    if is_overload_none(name):
        if is_literal_type(S.name_typ):
            ofj__uojs = get_literal_value(S.name_typ)
        else:
            raise_bodo_error(mbos__lyfk)
    elif is_literal_type(name):
        ofj__uojs = get_literal_value(name)
    else:
        raise_bodo_error(mbos__lyfk)
    ofj__uojs = 0 if ofj__uojs is None else ofj__uojs

    def impl(S, name=None):
        arr = bodo.hiframes.pd_series_ext.get_series_data(S)
        index = bodo.hiframes.pd_series_ext.get_series_index(S)
        return bodo.hiframes.pd_dataframe_ext.init_dataframe((arr,), index,
            (ofj__uojs,))
    return impl


@overload_method(SeriesType, 'keys', inline='always', no_unliteral=True)
def overload_series_keys(S):

    def impl(S):
        return bodo.hiframes.pd_series_ext.get_series_index(S)
    return impl
