"""
Implementation of DataFrame attributes and methods using overload.
"""
import operator
import re
import warnings
from collections import namedtuple
from typing import Tuple
import llvmlite.llvmpy.core as lc
import numba
import numpy as np
import pandas as pd
from numba.core import cgutils, ir, types
from numba.core.imputils import RefType, impl_ret_borrowed, impl_ret_new_ref, iternext_impl, lower_builtin
from numba.core.ir_utils import mk_unique_var, next_label
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import lower_getattr, models, overload, overload_attribute, overload_method, register_model, type_callable
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.datetime_timedelta_ext import _no_input, datetime_timedelta_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType
from bodo.hiframes.pd_dataframe_ext import DataFrameType, check_runtime_cols_unsupported, handle_inplace_df_type_change
from bodo.hiframes.pd_index_ext import DatetimeIndexType, RangeIndexType, StringIndexType, is_pd_index_type
from bodo.hiframes.pd_multi_index_ext import MultiIndexType
from bodo.hiframes.pd_series_ext import SeriesType, if_series_to_array_type
from bodo.hiframes.pd_timestamp_ext import pd_timestamp_type
from bodo.hiframes.rolling import is_supported_shift_array_type
from bodo.hiframes.split_impl import string_array_split_view_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import BooleanArrayType, boolean_array, boolean_dtype
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.utils.transform import bodo_types_with_params, gen_const_tup, no_side_effect_call_tuples
from bodo.utils.typing import BodoError, BodoWarning, check_unsupported_args, dtype_to_array_type, ensure_constant_arg, ensure_constant_values, get_index_data_arr_types, get_index_names, get_literal_value, get_nullable_and_non_nullable_types, get_overload_const_bool, get_overload_const_int, get_overload_const_list, get_overload_const_str, get_overload_const_tuple, get_overload_constant_dict, get_overload_constant_series, is_common_scalar_dtype, is_literal_type, is_overload_bool, is_overload_bool_list, is_overload_constant_bool, is_overload_constant_dict, is_overload_constant_int, is_overload_constant_list, is_overload_constant_series, is_overload_constant_str, is_overload_constant_tuple, is_overload_false, is_overload_int, is_overload_none, is_overload_true, is_overload_zero, parse_dtype, raise_bodo_error, raise_const_error, unliteral_val
from bodo.utils.utils import is_array_typ


@overload_attribute(DataFrameType, 'index', inline='always')
def overload_dataframe_index(df):
    return lambda df: bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)


def generate_col_to_index_func_text(col_names: Tuple):
    if all(isinstance(a, str) for a in col_names) or all(isinstance(a,
        bytes) for a in col_names):
        uvvp__jsqp = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({uvvp__jsqp})\n'
            )
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    check_runtime_cols_unsupported(df, 'DataFrame.columns')
    kycfi__xdkq = 'def impl(df):\n'
    txr__ylvl = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    kycfi__xdkq += f'  return {txr__ylvl}'
    iof__pfjls = {}
    exec(kycfi__xdkq, {'bodo': bodo}, iof__pfjls)
    impl = iof__pfjls['impl']
    return impl


@overload_attribute(DataFrameType, 'values')
def overload_dataframe_values(df):
    check_runtime_cols_unsupported(df, 'DataFrame.values')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.values: only supported for dataframes containing numeric values'
            )
    zcxqk__htbhk = len(df.columns)
    dczjn__fbxf = set(i for i in range(zcxqk__htbhk) if isinstance(df.data[
        i], IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in dczjn__fbxf else '') for i in
        range(zcxqk__htbhk))
    kycfi__xdkq = 'def f(df):\n'.format()
    kycfi__xdkq += '    return np.stack(({},), 1)\n'.format(data_args)
    iof__pfjls = {}
    exec(kycfi__xdkq, {'bodo': bodo, 'np': np}, iof__pfjls)
    xuud__gzk = iof__pfjls['f']
    return xuud__gzk


@overload_method(DataFrameType, 'to_numpy', inline='always', no_unliteral=True)
def overload_dataframe_to_numpy(df, dtype=None, copy=False, na_value=_no_input
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.to_numpy()')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.to_numpy(): only supported for dataframes containing numeric values'
            )
    twuih__aewpa = {'dtype': dtype, 'na_value': na_value}
    qwly__bqkra = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', twuih__aewpa, qwly__bqkra,
        package_name='pandas', module_name='DataFrame')

    def impl(df, dtype=None, copy=False, na_value=_no_input):
        return df.values
    return impl


@overload_attribute(DataFrameType, 'ndim', inline='always')
def overload_dataframe_ndim(df):
    return lambda df: 2


@overload_attribute(DataFrameType, 'size')
def overload_dataframe_size(df):
    if df.has_runtime_cols:

        def impl(df):
            t = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            yxmj__jpb = bodo.hiframes.table.compute_num_runtime_columns(t)
            return yxmj__jpb * len(t)
        return impl
    ncols = len(df.columns)
    return lambda df: ncols * len(df)


@lower_getattr(DataFrameType, 'shape')
def lower_dataframe_shape(context, builder, typ, val):
    impl = overload_dataframe_shape(typ)
    return context.compile_internal(builder, impl, types.Tuple([types.int64,
        types.int64])(typ), (val,))


def overload_dataframe_shape(df):
    if df.has_runtime_cols:

        def impl(df):
            t = bodo.hiframes.pd_dataframe_ext.get_dataframe_table(df)
            yxmj__jpb = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), yxmj__jpb
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), types.int64(ncols))


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    kycfi__xdkq = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    ywkpj__qxpdm = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    kycfi__xdkq += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{ywkpj__qxpdm}), {index}, None)
"""
    iof__pfjls = {}
    exec(kycfi__xdkq, {'bodo': bodo}, iof__pfjls)
    impl = iof__pfjls['impl']
    return impl


@overload_attribute(DataFrameType, 'empty')
def overload_dataframe_empty(df):
    check_runtime_cols_unsupported(df, 'DataFrame.empty')
    if len(df.columns) == 0:
        return lambda df: True
    return lambda df: len(df) == 0


@overload_method(DataFrameType, 'assign', no_unliteral=True)
def overload_dataframe_assign(df, **kwargs):
    check_runtime_cols_unsupported(df, 'DataFrame.assign()')
    raise_bodo_error('Invalid df.assign() call')


@overload_method(DataFrameType, 'insert', no_unliteral=True)
def overload_dataframe_insert(df, loc, column, value, allow_duplicates=False):
    check_runtime_cols_unsupported(df, 'DataFrame.insert()')
    raise_bodo_error('Invalid df.insert() call')


def _get_dtype_str(dtype):
    if isinstance(dtype, types.Function):
        if dtype.key[0] == str:
            return "'str'"
        elif dtype.key[0] == float:
            return 'float'
        elif dtype.key[0] == int:
            return 'int'
        elif dtype.key[0] == bool:
            return 'bool'
        else:
            raise BodoError(f'invalid dtype: {dtype}')
    if isinstance(dtype, types.DTypeSpec):
        dtype = dtype.dtype
    if isinstance(dtype, types.functions.NumberClass):
        return f"'{dtype.key}'"
    if isinstance(dtype, types.PyObject) or dtype in (object, 'object'):
        return "'object'"
    if dtype in (bodo.libs.str_arr_ext.string_dtype, pd.StringDtype()):
        return 'str'
    return f"'{dtype}'"


@overload_method(DataFrameType, 'astype', inline='always', no_unliteral=True)
def overload_dataframe_astype(df, dtype, copy=True, errors='raise',
    _bodo_nan_to_str=True, _bodo_object_typeref=None):
    check_runtime_cols_unsupported(df, 'DataFrame.astype()')
    twuih__aewpa = {'copy': copy, 'errors': errors}
    qwly__bqkra = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', twuih__aewpa, qwly__bqkra,
        package_name='pandas', module_name='DataFrame')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "DataFrame.astype(): 'dtype' when passed as string must be a constant value"
            )
    extra_globals = None
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        elnl__gyp = _bodo_object_typeref.instance_type
        assert isinstance(elnl__gyp, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        extra_globals = {}
        eha__vjipl = {}
        for i, name in enumerate(elnl__gyp.columns):
            arr_typ = elnl__gyp.data[i]
            if isinstance(arr_typ, IntegerArrayType):
                ldiqj__kfrez = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype)
            elif arr_typ == boolean_array:
                ldiqj__kfrez = boolean_dtype
            else:
                ldiqj__kfrez = arr_typ.dtype
            extra_globals[f'_bodo_schema{i}'] = ldiqj__kfrez
            eha__vjipl[name] = f'_bodo_schema{i}'
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {eha__vjipl[lsd__lxj]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             if lsd__lxj in eha__vjipl else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})' for
            i, lsd__lxj in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        fixq__eskp = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(fixq__eskp[lsd__lxj])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             if lsd__lxj in fixq__eskp else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})' for
            i, lsd__lxj in enumerate(df.columns))
    else:
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dtype, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             for i in range(len(df.columns)))
    header = """def impl(df, dtype, copy=True, errors='raise', _bodo_nan_to_str=True, _bodo_object_typeref=None):
"""
    return _gen_init_df(header, df.columns, data_args, extra_globals=
        extra_globals)


@overload_method(DataFrameType, 'copy', inline='always', no_unliteral=True)
def overload_dataframe_copy(df, deep=True):
    check_runtime_cols_unsupported(df, 'DataFrame.copy()')
    ctsv__ozs = []
    for i in range(len(df.columns)):
        arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
        if is_overload_true(deep):
            ctsv__ozs.append(arr + '.copy()')
        elif is_overload_false(deep):
            ctsv__ozs.append(arr)
        else:
            ctsv__ozs.append(f'{arr}.copy() if deep else {arr}')
    header = 'def impl(df, deep=True):\n'
    return _gen_init_df(header, df.columns, ', '.join(ctsv__ozs))


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    twuih__aewpa = {'index': index, 'level': level, 'errors': errors}
    qwly__bqkra = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', twuih__aewpa, qwly__bqkra,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_constant_bool(inplace):
        raise BodoError(
            "DataFrame.rename(): 'inplace' keyword only supports boolean constant assignment"
            )
    if not is_overload_none(mapper):
        if not is_overload_none(columns):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'mapper' and 'columns'"
                )
        if not (is_overload_constant_int(axis) and get_overload_const_int(
            axis) == 1):
            raise BodoError(
                "DataFrame.rename(): 'mapper' only supported with axis=1")
        if not is_overload_constant_dict(mapper):
            raise_bodo_error(
                "'mapper' argument to DataFrame.rename() should be a constant dictionary"
                )
        lrj__bft = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        lrj__bft = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    lhdr__kivep = [lrj__bft.get(df.columns[i], df.columns[i]) for i in
        range(len(df.columns))]
    ctsv__ozs = []
    for i in range(len(df.columns)):
        arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
        if is_overload_true(copy):
            ctsv__ozs.append(arr + '.copy()')
        elif is_overload_false(copy):
            ctsv__ozs.append(arr)
        else:
            ctsv__ozs.append(f'{arr}.copy() if copy else {arr}')
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    return _gen_init_df(header, lhdr__kivep, ', '.join(ctsv__ozs))


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    eow__vddp = not is_overload_none(items)
    qau__yqjvg = not is_overload_none(like)
    uwyvq__wbq = not is_overload_none(regex)
    hxde__upitj = eow__vddp ^ qau__yqjvg ^ uwyvq__wbq
    eivu__wnio = not (eow__vddp or qau__yqjvg or uwyvq__wbq)
    if eivu__wnio:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not hxde__upitj:
        raise BodoError(
            'DataFrame.filter(): keyword arguments `items`, `like`, and `regex` are mutually exclusive'
            )
    if is_overload_none(axis):
        axis = 'columns'
    if is_overload_constant_str(axis):
        axis = get_overload_const_str(axis)
        if axis not in {'index', 'columns'}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either "index" or "columns" if string'
                )
        etmtd__uofp = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        etmtd__uofp = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert etmtd__uofp in {0, 1}
    kycfi__xdkq = (
        'def impl(df, items=None, like=None, regex=None, axis=None):\n')
    if etmtd__uofp == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if etmtd__uofp == 1:
        bzrd__xly = []
        hktb__hzus = []
        eih__ydut = []
        if eow__vddp:
            if is_overload_constant_list(items):
                lemu__ikhty = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if qau__yqjvg:
            if is_overload_constant_str(like):
                qrvv__ljaw = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if uwyvq__wbq:
            if is_overload_constant_str(regex):
                pey__xuept = get_overload_const_str(regex)
                ezibs__ioxp = re.compile(pey__xuept)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, lsd__lxj in enumerate(df.columns):
            if not is_overload_none(items
                ) and lsd__lxj in lemu__ikhty or not is_overload_none(like
                ) and qrvv__ljaw in str(lsd__lxj) or not is_overload_none(regex
                ) and ezibs__ioxp.search(str(lsd__lxj)):
                hktb__hzus.append(lsd__lxj)
                eih__ydut.append(i)
        for i in eih__ydut:
            sqqpl__qezq = f'data_{i}'
            bzrd__xly.append(sqqpl__qezq)
            kycfi__xdkq += f"""  {sqqpl__qezq} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(bzrd__xly)
        return _gen_init_df(kycfi__xdkq, hktb__hzus, data_args)


@overload_method(DataFrameType, 'isna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'isnull', inline='always', no_unliteral=True)
def overload_dataframe_isna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.isna()')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_isna(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'select_dtypes', inline='always',
    no_unliteral=True)
def overload_dataframe_select_dtypes(df, include=None, exclude=None):
    check_runtime_cols_unsupported(df, 'DataFrame.select_dtypes')
    tfe__mcfyy = is_overload_none(include)
    axjj__pawd = is_overload_none(exclude)
    gasx__ckx = 'DataFrame.select_dtypes'
    if tfe__mcfyy and axjj__pawd:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not tfe__mcfyy:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            svo__wue = [dtype_to_array_type(parse_dtype(elem, gasx__ckx)) for
                elem in include]
        elif is_legal_input(include):
            svo__wue = [dtype_to_array_type(parse_dtype(include, gasx__ckx))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        svo__wue = get_nullable_and_non_nullable_types(svo__wue)
        ywzvp__otv = tuple(lsd__lxj for i, lsd__lxj in enumerate(df.columns
            ) if df.data[i] in svo__wue)
    else:
        ywzvp__otv = df.columns
    if not axjj__pawd:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            hxwsi__nbljq = [dtype_to_array_type(parse_dtype(elem, gasx__ckx
                )) for elem in exclude]
        elif is_legal_input(exclude):
            hxwsi__nbljq = [dtype_to_array_type(parse_dtype(exclude,
                gasx__ckx))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        hxwsi__nbljq = get_nullable_and_non_nullable_types(hxwsi__nbljq)
        ywzvp__otv = tuple(lsd__lxj for lsd__lxj in ywzvp__otv if df.data[
            df.columns.index(lsd__lxj)] not in hxwsi__nbljq)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(lsd__lxj)})'
         for lsd__lxj in ywzvp__otv)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, ywzvp__otv, data_args)


@overload_method(DataFrameType, 'notna', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'notnull', inline='always', no_unliteral=True)
def overload_dataframe_notna(df):
    check_runtime_cols_unsupported(df, 'DataFrame.notna()')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_isna(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})) == False'
         for i in range(len(df.columns)))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_head(df, n=5):
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[:n]' for
        i in range(len(df.columns)))
    header = 'def impl(df, n=5):\n'
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[:n]'
    return _gen_init_df(header, df.columns, data_args, index)


@lower_builtin('df.head', DataFrameType, types.Integer)
@lower_builtin('df.head', DataFrameType, types.Omitted)
def dataframe_head_lower(context, builder, sig, args):
    impl = overload_dataframe_head(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'tail', inline='always', no_unliteral=True)
def overload_dataframe_tail(df, n=5):
    check_runtime_cols_unsupported(df, 'DataFrame.tail()')
    if not is_overload_int(n):
        raise BodoError("Dataframe.tail(): 'n' must be an Integer")
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[m:]' for
        i in range(len(df.columns)))
    header = 'def impl(df, n=5):\n'
    header += '  m = bodo.hiframes.series_impl.tail_slice(len(df), n)\n'
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[m:]'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'first', inline='always', no_unliteral=True)
def overload_dataframe_first(df, offset):
    check_runtime_cols_unsupported(df, 'DataFrame.first()')
    dex__oyzj = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in dex__oyzj:
        raise BodoError(
            "DataFrame.first(): 'offset' must be an string or DateOffset")
    index = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[:valid_entries]'
        )
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[:valid_entries]'
         for i in range(len(df.columns)))
    header = 'def impl(df, offset):\n'
    header += (
        '  df_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
        )
    header += '  if len(df_index):\n'
    header += '    start_date = df_index[0]\n'
    header += """    valid_entries = bodo.libs.array_kernels.get_valid_entries_from_date_offset(df_index, offset, start_date, False)
"""
    header += '  else:\n'
    header += '    valid_entries = 0\n'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'last', inline='always', no_unliteral=True)
def overload_dataframe_last(df, offset):
    check_runtime_cols_unsupported(df, 'DataFrame.last()')
    dex__oyzj = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in dex__oyzj:
        raise BodoError(
            "DataFrame.last(): 'offset' must be an string or DateOffset")
    index = (
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[len(df)-valid_entries:]'
        )
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})[len(df)-valid_entries:]'
         for i in range(len(df.columns)))
    header = 'def impl(df, offset):\n'
    header += (
        '  df_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
        )
    header += '  if len(df_index):\n'
    header += '    final_date = df_index[-1]\n'
    header += """    valid_entries = bodo.libs.array_kernels.get_valid_entries_from_date_offset(df_index, offset, final_date, True)
"""
    header += '  else:\n'
    header += '    valid_entries = 0\n'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'to_string', no_unliteral=True)
def to_string_overload(df, buf=None, columns=None, col_space=None, header=
    True, index=True, na_rep='NaN', formatters=None, float_format=None,
    sparsify=None, index_names=True, justify=None, max_rows=None, min_rows=
    None, max_cols=None, show_dimensions=False, decimal='.', line_width=
    None, max_colwidth=None, encoding=None):
    check_runtime_cols_unsupported(df, 'DataFrame.to_string()')

    def impl(df, buf=None, columns=None, col_space=None, header=True, index
        =True, na_rep='NaN', formatters=None, float_format=None, sparsify=
        None, index_names=True, justify=None, max_rows=None, min_rows=None,
        max_cols=None, show_dimensions=False, decimal='.', line_width=None,
        max_colwidth=None, encoding=None):
        with numba.objmode(res='string'):
            res = df.to_string(buf=buf, columns=columns, col_space=
                col_space, header=header, index=index, na_rep=na_rep,
                formatters=formatters, float_format=float_format, sparsify=
                sparsify, index_names=index_names, justify=justify,
                max_rows=max_rows, min_rows=min_rows, max_cols=max_cols,
                show_dimensions=show_dimensions, decimal=decimal,
                line_width=line_width, max_colwidth=max_colwidth, encoding=
                encoding)
        return res
    return impl


@overload_method(DataFrameType, 'isin', inline='always', no_unliteral=True)
def overload_dataframe_isin(df, values):
    check_runtime_cols_unsupported(df, 'DataFrame.isin()')
    from bodo.utils.typing import is_iterable_type
    kycfi__xdkq = 'def impl(df, values):\n'
    asnkf__xjrtq = {}
    oas__ioge = False
    if isinstance(values, DataFrameType):
        oas__ioge = True
        for i, lsd__lxj in enumerate(df.columns):
            if lsd__lxj in values.columns:
                fgaek__mvm = 'val{}'.format(i)
                kycfi__xdkq += (
                    """  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {})
"""
                    .format(fgaek__mvm, values.columns.index(lsd__lxj)))
                asnkf__xjrtq[lsd__lxj] = fgaek__mvm
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        asnkf__xjrtq = {lsd__lxj: 'values' for lsd__lxj in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        fgaek__mvm = 'data{}'.format(i)
        kycfi__xdkq += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(fgaek__mvm, i))
        data.append(fgaek__mvm)
    qnwk__viu = ['out{}'.format(i) for i in range(len(df.columns))]
    ezds__ymdg = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    oazw__pyo = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    kha__yabi = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, kdw__yep) in enumerate(zip(df.columns, data)):
        if cname in asnkf__xjrtq:
            jvraq__tlew = asnkf__xjrtq[cname]
            if oas__ioge:
                kycfi__xdkq += ezds__ymdg.format(kdw__yep, jvraq__tlew,
                    qnwk__viu[i])
            else:
                kycfi__xdkq += oazw__pyo.format(kdw__yep, jvraq__tlew,
                    qnwk__viu[i])
        else:
            kycfi__xdkq += kha__yabi.format(qnwk__viu[i])
    return _gen_init_df(kycfi__xdkq, df.columns, ','.join(qnwk__viu))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    zcxqk__htbhk = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(zcxqk__htbhk))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    mzmn__ankuh = [lsd__lxj for lsd__lxj, egz__saa in zip(df.columns, df.
        data) if bodo.utils.typing._is_pandas_numeric_dtype(egz__saa.dtype)]
    assert len(mzmn__ankuh) != 0
    xpn__zll = ''
    if not any(egz__saa == types.float64 for egz__saa in df.data):
        xpn__zll = '.astype(np.float64)'
    iai__fyq = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.columns.index(lsd__lxj), '.astype(np.float64)' if 
        isinstance(df.data[df.columns.index(lsd__lxj)], IntegerArrayType) or
        df.data[df.columns.index(lsd__lxj)] == boolean_array else '') for
        lsd__lxj in mzmn__ankuh)
    slo__eyxef = 'np.stack(({},), 1){}'.format(iai__fyq, xpn__zll)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(
        mzmn__ankuh)))
    index = f'{generate_col_to_index_func_text(mzmn__ankuh)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(slo__eyxef)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, mzmn__ankuh, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    zlf__szil = dict(ddof=ddof)
    rzyk__hfls = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    gkiv__knl = '1' if is_overload_none(min_periods) else 'min_periods'
    mzmn__ankuh = [lsd__lxj for lsd__lxj, egz__saa in zip(df.columns, df.
        data) if bodo.utils.typing._is_pandas_numeric_dtype(egz__saa.dtype)]
    if len(mzmn__ankuh) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    xpn__zll = ''
    if not any(egz__saa == types.float64 for egz__saa in df.data):
        xpn__zll = '.astype(np.float64)'
    iai__fyq = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.columns.index(lsd__lxj), '.astype(np.float64)' if 
        isinstance(df.data[df.columns.index(lsd__lxj)], IntegerArrayType) or
        df.data[df.columns.index(lsd__lxj)] == boolean_array else '') for
        lsd__lxj in mzmn__ankuh)
    slo__eyxef = 'np.stack(({},), 1){}'.format(iai__fyq, xpn__zll)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(
        mzmn__ankuh)))
    index = f'pd.Index({mzmn__ankuh})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(slo__eyxef)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        gkiv__knl)
    return _gen_init_df(header, mzmn__ankuh, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    zlf__szil = dict(axis=axis, level=level, numeric_only=numeric_only)
    rzyk__hfls = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    kycfi__xdkq = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    kycfi__xdkq += '  data = np.array([{}])\n'.format(data_args)
    txr__ylvl = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    kycfi__xdkq += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {txr__ylvl})\n'
        )
    iof__pfjls = {}
    exec(kycfi__xdkq, {'bodo': bodo, 'np': np}, iof__pfjls)
    impl = iof__pfjls['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    zlf__szil = dict(axis=axis)
    rzyk__hfls = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    kycfi__xdkq = 'def impl(df, axis=0, dropna=True):\n'
    kycfi__xdkq += '  data = np.asarray(({},))\n'.format(data_args)
    txr__ylvl = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    kycfi__xdkq += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {txr__ylvl})\n'
        )
    iof__pfjls = {}
    exec(kycfi__xdkq, {'bodo': bodo, 'np': np}, iof__pfjls)
    impl = iof__pfjls['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    zlf__szil = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    rzyk__hfls = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    zlf__szil = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    rzyk__hfls = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    zlf__szil = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    rzyk__hfls = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    zlf__szil = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    rzyk__hfls = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    zlf__szil = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    rzyk__hfls = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    zlf__szil = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    rzyk__hfls = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    zlf__szil = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    rzyk__hfls = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    zlf__szil = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    rzyk__hfls = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    zlf__szil = dict(numeric_only=numeric_only, interpolation=interpolation)
    rzyk__hfls = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    zlf__szil = dict(axis=axis, skipna=skipna)
    rzyk__hfls = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    for aiu__qmm in df.data:
        if not (bodo.utils.utils.is_np_array_typ(aiu__qmm) and (aiu__qmm.
            dtype in [bodo.datetime64ns, bodo.timedelta64ns] or isinstance(
            aiu__qmm.dtype, (types.Number, types.Boolean))) or isinstance(
            aiu__qmm, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or
            aiu__qmm in [bodo.boolean_array, bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {aiu__qmm} not supported.'
                )
        if isinstance(aiu__qmm, bodo.CategoricalArrayType
            ) and not aiu__qmm.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    zlf__szil = dict(axis=axis, skipna=skipna)
    rzyk__hfls = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    for aiu__qmm in df.data:
        if not (bodo.utils.utils.is_np_array_typ(aiu__qmm) and (aiu__qmm.
            dtype in [bodo.datetime64ns, bodo.timedelta64ns] or isinstance(
            aiu__qmm.dtype, (types.Number, types.Boolean))) or isinstance(
            aiu__qmm, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or
            aiu__qmm in [bodo.boolean_array, bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {aiu__qmm} not supported.'
                )
        if isinstance(aiu__qmm, bodo.CategoricalArrayType
            ) and not aiu__qmm.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmin(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmin', axis=axis)


@overload_method(DataFrameType, 'infer_objects', inline='always')
def overload_dataframe_infer_objects(df):
    check_runtime_cols_unsupported(df, 'DataFrame.infer_objects()')
    return lambda df: df.copy()


def _gen_reduce_impl(df, func_name, args=None, axis=None):
    args = '' if is_overload_none(args) else args
    if is_overload_none(axis):
        axis = 0
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
    else:
        raise_bodo_error(
            f'DataFrame.{func_name}: axis must be a constant Integer')
    assert axis in (0, 1), f'invalid axis argument for DataFrame.{func_name}'
    if func_name in ('idxmax', 'idxmin'):
        out_colnames = df.columns
    else:
        mzmn__ankuh = tuple(lsd__lxj for lsd__lxj, egz__saa in zip(df.
            columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype
            (egz__saa.dtype))
        out_colnames = mzmn__ankuh
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            lpk__uely = [numba.np.numpy_support.as_dtype(df.data[df.columns
                .index(lsd__lxj)].dtype) for lsd__lxj in out_colnames]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(lpk__uely, []))
    except NotImplementedError as mtqbt__zow:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    qaygo__vuf = ''
    if func_name in ('sum', 'prod'):
        qaygo__vuf = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    kycfi__xdkq = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, qaygo__vuf))
    if func_name == 'quantile':
        kycfi__xdkq = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        kycfi__xdkq = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        kycfi__xdkq += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        kycfi__xdkq += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    iof__pfjls = {}
    exec(kycfi__xdkq, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        iof__pfjls)
    impl = iof__pfjls['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    zyr__ptxz = ''
    if func_name in ('min', 'max'):
        zyr__ptxz = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        zyr__ptxz = ', dtype=np.float32'
    ndk__avya = f'bodo.libs.array_ops.array_op_{func_name}'
    dehah__oapn = ''
    if func_name in ['sum', 'prod']:
        dehah__oapn = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        dehah__oapn = 'index'
    elif func_name == 'quantile':
        dehah__oapn = 'q'
    elif func_name in ['std', 'var']:
        dehah__oapn = 'True, ddof'
    elif func_name == 'median':
        dehah__oapn = 'True'
    data_args = ', '.join(
        f'{ndk__avya}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(lsd__lxj)}), {dehah__oapn})'
         for lsd__lxj in out_colnames)
    kycfi__xdkq = ''
    if func_name in ('idxmax', 'idxmin'):
        kycfi__xdkq += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        kycfi__xdkq += (
            '  data = bodo.utils.conversion.coerce_to_array(({},))\n'.
            format(data_args))
    else:
        kycfi__xdkq += '  data = np.asarray(({},){})\n'.format(data_args,
            zyr__ptxz)
    kycfi__xdkq += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return kycfi__xdkq


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    hqbp__mamo = [df_type.columns.index(lsd__lxj) for lsd__lxj in out_colnames]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in hqbp__mamo)
    isrjy__zezzb = '\n        '.join(f'row[{i}] = arr_{hqbp__mamo[i]}[i]' for
        i in range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    cjjwi__jxfrh = f'len(arr_{hqbp__mamo[0]})'
    weoqj__wfjwq = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum':
        'np.nansum', 'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in weoqj__wfjwq:
        uowl__uwgq = weoqj__wfjwq[func_name]
        vpou__fgzf = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        kycfi__xdkq = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {cjjwi__jxfrh}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{vpou__fgzf})
    for i in numba.parfors.parfor.internal_prange(n):
        {isrjy__zezzb}
        A[i] = {uowl__uwgq}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return kycfi__xdkq
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    zlf__szil = dict(fill_method=fill_method, limit=limit, freq=freq)
    rzyk__hfls = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.hiframes.rolling.pct_change(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), periods, False)'
         for i in range(len(df.columns)))
    header = (
        "def impl(df, periods=1, fill_method='pad', limit=None, freq=None):\n")
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'cumprod', inline='always', no_unliteral=True)
def overload_dataframe_cumprod(df, axis=None, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.cumprod()')
    zlf__szil = dict(axis=axis, skipna=skipna)
    rzyk__hfls = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).cumprod()'
         for i in range(len(df.columns)))
    header = 'def impl(df, axis=None, skipna=True):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'cumsum', inline='always', no_unliteral=True)
def overload_dataframe_cumsum(df, axis=None, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.cumsum()')
    zlf__szil = dict(skipna=skipna)
    rzyk__hfls = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).cumsum()'
         for i in range(len(df.columns)))
    header = 'def impl(df, axis=None, skipna=True):\n'
    return _gen_init_df(header, df.columns, data_args)


def _is_describe_type(data):
    return isinstance(data, IntegerArrayType) or isinstance(data, types.Array
        ) and isinstance(data.dtype, types.Number
        ) or data.dtype == bodo.datetime64ns


@overload_method(DataFrameType, 'describe', inline='always', no_unliteral=True)
def overload_dataframe_describe(df, percentiles=None, include=None, exclude
    =None, datetime_is_numeric=True):
    check_runtime_cols_unsupported(df, 'DataFrame.describe()')
    zlf__szil = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    rzyk__hfls = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    mzmn__ankuh = [lsd__lxj for lsd__lxj, egz__saa in zip(df.columns, df.
        data) if _is_describe_type(egz__saa)]
    if len(mzmn__ankuh) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    ogps__lccnd = sum(df.data[df.columns.index(lsd__lxj)].dtype == bodo.
        datetime64ns for lsd__lxj in mzmn__ankuh)

    def _get_describe(col_ind):
        sachm__dcdm = df.data[col_ind].dtype == bodo.datetime64ns
        if ogps__lccnd and ogps__lccnd != len(mzmn__ankuh):
            if sachm__dcdm:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for lsd__lxj in mzmn__ankuh:
        col_ind = df.columns.index(lsd__lxj)
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.columns.index(lsd__lxj)) for
        lsd__lxj in mzmn__ankuh)
    suwuk__qchmv = (
        "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']")
    if ogps__lccnd == len(mzmn__ankuh):
        suwuk__qchmv = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif ogps__lccnd:
        suwuk__qchmv = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({suwuk__qchmv})'
    return _gen_init_df(header, mzmn__ankuh, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    zlf__szil = dict(axis=axis, convert=convert, is_copy=is_copy)
    rzyk__hfls = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})[indices_t]'
        .format(i) for i in range(len(df.columns)))
    header = 'def impl(df, indices, axis=0, convert=None, is_copy=True):\n'
    header += (
        '  indices_t = bodo.utils.conversion.coerce_to_ndarray(indices)\n')
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)[indices_t]'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'shift', inline='always', no_unliteral=True)
def overload_dataframe_shift(df, periods=1, freq=None, axis=0, fill_value=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.shift()')
    zlf__szil = dict(freq=freq, axis=axis, fill_value=fill_value)
    rzyk__hfls = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    for uzub__etpp in df.data:
        if not is_supported_shift_array_type(uzub__etpp):
            raise BodoError(
                f'Dataframe.shift() column input type {uzub__etpp.dtype} not supported yet.'
                )
    if not is_overload_int(periods):
        raise BodoError(
            "DataFrame.shift(): 'periods' input must be an integer.")
    data_args = ', '.join(
        f'bodo.hiframes.rolling.shift(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), periods, False)'
         for i in range(len(df.columns)))
    header = 'def impl(df, periods=1, freq=None, axis=0, fill_value=None):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'diff', inline='always', no_unliteral=True)
def overload_dataframe_diff(df, periods=1, axis=0):
    check_runtime_cols_unsupported(df, 'DataFrame.diff()')
    zlf__szil = dict(axis=axis)
    rzyk__hfls = dict(axis=0)
    check_unsupported_args('DataFrame.diff', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    for uzub__etpp in df.data:
        if not (isinstance(uzub__etpp, types.Array) and (isinstance(
            uzub__etpp.dtype, types.Number) or uzub__etpp.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {uzub__etpp.dtype} not supported.'
                )
    if not is_overload_int(periods):
        raise BodoError("DataFrame.diff(): 'periods' input must be an integer."
            )
    header = 'def impl(df, periods=1, axis= 0):\n'
    for i in range(len(df.columns)):
        header += (
            f'  data_{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})\n'
            )
    data_args = ', '.join(
        f'bodo.hiframes.series_impl.dt64_arr_sub(data_{i}, bodo.hiframes.rolling.shift(data_{i}, periods, False))'
         if df.data[i] == types.Array(bodo.datetime64ns, 1, 'C') else
        f'data_{i} - bodo.hiframes.rolling.shift(data_{i}, periods, False)' for
        i in range(len(df.columns)))
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'explode', inline='always', no_unliteral=True)
def overload_dataframe_explode(df, column, ignore_index=False):
    lgzuu__dmadg = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(lgzuu__dmadg)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        aasen__bfra = get_overload_const_list(column)
    else:
        aasen__bfra = [get_literal_value(column)]
    anwvx__uby = {lsd__lxj: i for i, lsd__lxj in enumerate(df.columns)}
    ldh__bdmy = [anwvx__uby[lsd__lxj] for lsd__lxj in aasen__bfra]
    for i in ldh__bdmy:
        if not isinstance(df.data[i], ArrayItemArrayType) and df.data[i
            ].dtype != string_array_split_view_type:
            raise BodoError(
                f'DataFrame.explode(): columns must have array-like entries')
    n = len(df.columns)
    header = 'def impl(df, column, ignore_index=False):\n'
    header += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    header += '  index_arr = bodo.utils.conversion.index_to_array(index)\n'
    for i in range(n):
        header += (
            f'  data{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})\n'
            )
    header += (
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{ldh__bdmy[0]})\n'
        )
    for i in range(n):
        if i in ldh__bdmy:
            header += (
                f'  out_data{i} = bodo.libs.array_kernels.explode_no_index(data{i}, counts)\n'
                )
        else:
            header += (
                f'  out_data{i} = bodo.libs.array_kernels.repeat_kernel(data{i}, counts)\n'
                )
    header += (
        '  new_index = bodo.libs.array_kernels.repeat_kernel(index_arr, counts)\n'
        )
    data_args = ', '.join(f'out_data{i}' for i in range(n))
    index = 'bodo.utils.conversion.convert_to_index(new_index)'
    return _gen_init_df(header, df.columns, data_args, index)


@overload_method(DataFrameType, 'set_index', inline='always', no_unliteral=True
    )
def overload_dataframe_set_index(df, keys, drop=True, append=False, inplace
    =False, verify_integrity=False):
    check_runtime_cols_unsupported(df, 'DataFrame.set_index()')
    twuih__aewpa = {'inplace': inplace, 'append': append,
        'verify_integrity': verify_integrity}
    qwly__bqkra = {'inplace': False, 'append': False, 'verify_integrity': False
        }
    check_unsupported_args('DataFrame.set_index', twuih__aewpa, qwly__bqkra,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_constant_str(keys):
        raise_bodo_error(
            "DataFrame.set_index(): 'keys' must be a constant string")
    col_name = get_overload_const_str(keys)
    col_ind = df.columns.index(col_name)
    if len(df.columns) == 1:
        raise BodoError(
            'DataFrame.set_index(): Not supported on single column DataFrames.'
            )
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})'.format(
        i) for i in range(len(df.columns)) if i != col_ind)
    header = """def impl(df, keys, drop=True, append=False, inplace=False, verify_integrity=False):
"""
    columns = tuple(lsd__lxj for lsd__lxj in df.columns if lsd__lxj != col_name
        )
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    twuih__aewpa = {'inplace': inplace}
    qwly__bqkra = {'inplace': False}
    check_unsupported_args('query', twuih__aewpa, qwly__bqkra, package_name
        ='pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        yhqne__imxp = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[yhqne__imxp]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    twuih__aewpa = {'subset': subset, 'keep': keep}
    qwly__bqkra = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', twuih__aewpa,
        qwly__bqkra, package_name='pandas', module_name='DataFrame')
    zcxqk__htbhk = len(df.columns)
    kycfi__xdkq = "def impl(df, subset=None, keep='first'):\n"
    for i in range(zcxqk__htbhk):
        kycfi__xdkq += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    kycfi__xdkq += (
        '  duplicated = bodo.libs.array_kernels.duplicated(({},))\n'.format
        (', '.join('data_{}'.format(i) for i in range(zcxqk__htbhk))))
    kycfi__xdkq += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    kycfi__xdkq += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    iof__pfjls = {}
    exec(kycfi__xdkq, {'bodo': bodo}, iof__pfjls)
    impl = iof__pfjls['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    twuih__aewpa = {'keep': keep, 'inplace': inplace, 'ignore_index':
        ignore_index}
    qwly__bqkra = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    kzi__cebg = []
    if is_overload_constant_list(subset):
        kzi__cebg = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        kzi__cebg = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        kzi__cebg = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    rck__kcr = []
    for col_name in kzi__cebg:
        if col_name not in df.columns:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        rck__kcr.append(df.columns.index(col_name))
    check_unsupported_args('DataFrame.drop_duplicates', twuih__aewpa,
        qwly__bqkra, package_name='pandas', module_name='DataFrame')
    wann__jndn = []
    if rck__kcr:
        for ebkzj__uoodc in rck__kcr:
            if isinstance(df.data[ebkzj__uoodc], bodo.MapArrayType):
                wann__jndn.append(df.columns[ebkzj__uoodc])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                wann__jndn.append(col_name)
    if wann__jndn:
        raise BodoError(
            f'DataFrame.drop_duplicates(): Columns {wann__jndn} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    zcxqk__htbhk = len(df.columns)
    qnie__nffw = ['data_{}'.format(i) for i in rck__kcr]
    hrqw__vvueb = ['data_{}'.format(i) for i in range(zcxqk__htbhk) if i not in
        rck__kcr]
    if qnie__nffw:
        ahn__mws = len(qnie__nffw)
    else:
        ahn__mws = zcxqk__htbhk
    nlm__jkdl = ', '.join(qnie__nffw + hrqw__vvueb)
    data_args = ', '.join('data_{}'.format(i) for i in range(zcxqk__htbhk))
    kycfi__xdkq = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(zcxqk__htbhk):
        kycfi__xdkq += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    kycfi__xdkq += (
        """  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})
"""
        .format(nlm__jkdl, index, ahn__mws))
    kycfi__xdkq += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(kycfi__xdkq, df.columns, data_args, 'index')


def create_dataframe_mask_where_overload(func_name):

    def overload_dataframe_mask_where(df, cond, other=np.nan, inplace=False,
        axis=None, level=None, errors='raise', try_cast=False):
        _validate_arguments_mask_where(f'DataFrame.{func_name}', df, cond,
            other, inplace, axis, level, errors, try_cast)
        header = """def impl(df, cond, other=np.nan, inplace=False, axis=None, level=None, errors='raise', try_cast=False):
"""
        if func_name == 'mask':
            header += '  cond = ~cond\n'
        gen_all_false = [False]
        if cond.ndim == 1:
            cond_str = lambda i, _: 'cond'
        elif cond.ndim == 2:
            if isinstance(cond, DataFrameType):
                klik__zkhfg = {lsd__lxj: i for i, lsd__lxj in enumerate(
                    cond.columns)}

                def cond_str(i, gen_all_false):
                    if df.columns[i] in klik__zkhfg:
                        return (
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(cond, {klik__zkhfg[df.columns[i]]})'
                            )
                    else:
                        gen_all_false[0] = True
                        return 'all_false'
            elif isinstance(cond, types.Array):
                cond_str = lambda i, _: f'cond[:,{i}]'
        if not hasattr(other, 'ndim') or other.ndim == 1:
            lemy__nut = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                other_map = {lsd__lxj: i for i, lsd__lxj in enumerate(other
                    .columns)}
                lemy__nut = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other_map[df.columns[i]]})'
                     if df.columns[i] in other_map else 'None')
            elif isinstance(other, types.Array):
                lemy__nut = lambda i: f'other[:,{i}]'
        zcxqk__htbhk = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {lemy__nut(i)})'
             for i in range(zcxqk__htbhk))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        mntv__kup = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(mntv__kup)


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    zlf__szil = dict(inplace=inplace, level=level, errors=errors, try_cast=
        try_cast)
    rzyk__hfls = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise_bodo_error(f'{func_name}(): axis argument not supported')
    if not (isinstance(cond, (SeriesType, types.Array, BooleanArrayType)) and
        (cond.ndim == 1 or cond.ndim == 2) and cond.dtype == types.bool_
        ) and not (isinstance(cond, DataFrameType) and cond.ndim == 2 and
        all(cond.data[i].dtype == types.bool_ for i in range(len(df.columns)))
        ):
        raise BodoError(
            f"{func_name}(): 'cond' argument must be a DataFrame, Series, 1- or 2-dimensional array of booleans"
            )
    zcxqk__htbhk = len(df.columns)
    if hasattr(other, 'ndim') and (other.ndim != 1 or other.ndim != 2):
        if other.ndim == 2:
            if not isinstance(other, (DataFrameType, types.Array)):
                raise BodoError(
                    f"{func_name}(): 'other', if 2-dimensional, must be a DataFrame or array."
                    )
        elif other.ndim != 1:
            raise BodoError(
                f"{func_name}(): 'other' must be either 1 or 2-dimensional")
    if isinstance(other, DataFrameType):
        other_map = {lsd__lxj: i for i, lsd__lxj in enumerate(other.columns)}
        for i in range(zcxqk__htbhk):
            if df.columns[i] in other_map:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, df.data[i], other.data[other_map[df.columns[i]]]
                    )
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(zcxqk__htbhk):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , df.data[i], other.data)
    else:
        for i in range(zcxqk__htbhk):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , df.data[i], other, max_ndim=2)


def _gen_init_df(header, columns, data_args, index=None, extra_globals=None,
    out_df_type=None):
    if index is None:
        index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    if extra_globals is None:
        extra_globals = {}
    if out_df_type is not None:
        extra_globals['out_df_type'] = out_df_type
        qnr__bua = 'out_df_type'
    else:
        qnr__bua = gen_const_tup(columns)
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    kycfi__xdkq = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, {qnr__bua})
"""
    iof__pfjls = {}
    kwi__ftbm = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba}
    kwi__ftbm.update(extra_globals)
    exec(kycfi__xdkq, kwi__ftbm, iof__pfjls)
    impl = iof__pfjls['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        ikmt__mimk = pd.Index(lhs.columns)
        ptal__qzdw = pd.Index(rhs.columns)
        zcka__hkb, ewbs__jstfv, xtncq__ile = ikmt__mimk.join(ptal__qzdw,
            how='left' if is_inplace else 'outer', level=None,
            return_indexers=True)
        return tuple(zcka__hkb), ewbs__jstfv, xtncq__ile
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        vja__gyiil = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        wprkb__rhd = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, vja__gyiil)
        check_runtime_cols_unsupported(rhs, vja__gyiil)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                zcka__hkb, ewbs__jstfv, xtncq__ile = _get_binop_columns(lhs,
                    rhs)
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {stux__gsl}) {vja__gyiil}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {bbbr__wse})'
                     if stux__gsl != -1 and bbbr__wse != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for stux__gsl, bbbr__wse in zip(ewbs__jstfv, xtncq__ile))
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, zcka__hkb, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            qug__iha = []
            oozhx__tca = []
            if op in wprkb__rhd:
                for i, xwax__jvb in enumerate(lhs.data):
                    if is_common_scalar_dtype([xwax__jvb.dtype, rhs]):
                        qug__iha.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {vja__gyiil} rhs'
                            )
                    else:
                        ycp__oyz = f'arr{i}'
                        oozhx__tca.append(ycp__oyz)
                        qug__iha.append(ycp__oyz)
                data_args = ', '.join(qug__iha)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {vja__gyiil} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(oozhx__tca) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {ycp__oyz} = np.empty(n, dtype=np.bool_)\n' for
                    ycp__oyz in oozhx__tca)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(ycp__oyz, op ==
                    operator.ne) for ycp__oyz in oozhx__tca)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            qug__iha = []
            oozhx__tca = []
            if op in wprkb__rhd:
                for i, xwax__jvb in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, xwax__jvb.dtype]):
                        qug__iha.append(
                            f'lhs {vja__gyiil} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        ycp__oyz = f'arr{i}'
                        oozhx__tca.append(ycp__oyz)
                        qug__iha.append(ycp__oyz)
                data_args = ', '.join(qug__iha)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, vja__gyiil) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(oozhx__tca) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(ycp__oyz) for ycp__oyz in oozhx__tca)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(ycp__oyz, op ==
                    operator.ne) for ycp__oyz in oozhx__tca)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(rhs)'
            return _gen_init_df(header, rhs.columns, data_args, index)
    return overload_dataframe_binary_op


skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_binary_ops:
        if op in skips:
            continue
        mntv__kup = create_binary_op_overload(op)
        overload(op)(mntv__kup)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        vja__gyiil = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, vja__gyiil)
        check_runtime_cols_unsupported(right, vja__gyiil)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                zcka__hkb, _, xtncq__ile = _get_binop_columns(left, right, True
                    )
                kycfi__xdkq = 'def impl(left, right):\n'
                for i, bbbr__wse in enumerate(xtncq__ile):
                    if bbbr__wse == -1:
                        kycfi__xdkq += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    kycfi__xdkq += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    kycfi__xdkq += f"""  df_arr{i} {vja__gyiil} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {bbbr__wse})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    zcka__hkb)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(kycfi__xdkq, zcka__hkb, data_args,
                    index, extra_globals={'float64_arr_type': types.Array(
                    types.float64, 1, 'C')})
            kycfi__xdkq = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                kycfi__xdkq += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                kycfi__xdkq += '  df_arr{0} {1} right\n'.format(i, vja__gyiil)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(kycfi__xdkq, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        mntv__kup = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(mntv__kup)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            vja__gyiil = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, vja__gyiil)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, vja__gyiil) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        mntv__kup = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(mntv__kup)


_install_unary_ops()


def overload_isna(obj):
    check_runtime_cols_unsupported(obj, 'pd.isna()')
    if isinstance(obj, (DataFrameType, SeriesType)
        ) or bodo.hiframes.pd_index_ext.is_pd_index_type(obj):
        return lambda obj: obj.isna()
    if is_array_typ(obj):

        def impl(obj):
            numba.parfors.parfor.init_prange()
            n = len(obj)
            daym__lxlg = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                daym__lxlg[i] = bodo.libs.array_kernels.isna(obj, i)
            return daym__lxlg
        return impl


overload(pd.isna, inline='always')(overload_isna)
overload(pd.isnull, inline='always')(overload_isna)


@overload(pd.isna)
@overload(pd.isnull)
def overload_isna_scalar(obj):
    if isinstance(obj, (DataFrameType, SeriesType)
        ) or bodo.hiframes.pd_index_ext.is_pd_index_type(obj) or is_array_typ(
        obj):
        return
    if isinstance(obj, (types.List, types.UniTuple)):

        def impl(obj):
            n = len(obj)
            daym__lxlg = np.empty(n, np.bool_)
            for i in range(n):
                daym__lxlg[i] = pd.isna(obj[i])
            return daym__lxlg
        return impl
    obj = types.unliteral(obj)
    if obj == bodo.string_type:
        return lambda obj: unliteral_val(False)
    if isinstance(obj, types.Integer):
        return lambda obj: unliteral_val(False)
    if isinstance(obj, types.Float):
        return lambda obj: np.isnan(obj)
    if isinstance(obj, (types.NPDatetime, types.NPTimedelta)):
        return lambda obj: np.isnat(obj)
    if obj == types.none:
        return lambda obj: unliteral_val(True)
    if obj == bodo.hiframes.pd_timestamp_ext.pd_timestamp_type:
        return lambda obj: np.isnat(bodo.hiframes.pd_timestamp_ext.
            integer_to_dt64(obj.value))
    if obj == bodo.hiframes.datetime_timedelta_ext.pd_timedelta_type:
        return lambda obj: np.isnat(bodo.hiframes.pd_timestamp_ext.
            integer_to_timedelta64(obj.value))
    if isinstance(obj, types.Optional):
        return lambda obj: obj is None
    return lambda obj: unliteral_val(False)


@overload(operator.setitem, no_unliteral=True)
def overload_setitem_arr_none(A, idx, val):
    if is_array_typ(A, False) and isinstance(idx, types.Integer
        ) and val == types.none:
        return lambda A, idx, val: bodo.libs.array_kernels.setna(A, idx)


def overload_notna(obj):
    check_runtime_cols_unsupported(obj, 'pd.notna()')
    if isinstance(obj, DataFrameType):
        return lambda obj: obj.notna()
    if isinstance(obj, (SeriesType, types.Array, types.List, types.UniTuple)
        ) or bodo.hiframes.pd_index_ext.is_pd_index_type(obj
        ) or obj == bodo.string_array_type:
        return lambda obj: ~pd.isna(obj)
    return lambda obj: not pd.isna(obj)


overload(pd.notna, inline='always', no_unliteral=True)(overload_notna)
overload(pd.notnull, inline='always', no_unliteral=True)(overload_notna)


def _get_pd_dtype_str(t):
    if t.dtype == types.NPDatetime('ns'):
        return "'datetime64[ns]'"
    return bodo.ir.csv_ext._get_pd_dtype_str(t)


@overload_method(DataFrameType, 'replace', inline='always', no_unliteral=True)
def overload_dataframe_replace(df, to_replace=None, value=None, inplace=
    False, limit=None, regex=False, method='pad'):
    check_runtime_cols_unsupported(df, 'DataFrame.replace()')
    if is_overload_none(to_replace):
        raise BodoError('replace(): to_replace value of None is not supported')
    twuih__aewpa = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    qwly__bqkra = {'inplace': False, 'limit': None, 'regex': False,
        'method': 'pad'}
    check_unsupported_args('replace', twuih__aewpa, qwly__bqkra,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    gem__yxwb = str(expr_node)
    return gem__yxwb.startswith('left.') or gem__yxwb.startswith('right.')


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    dtua__qgbtg = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (dtua__qgbtg,))
    igi__aoqr = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        ckpm__llw = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        btrsp__leyw = {('NOT_NA', igi__aoqr(xwax__jvb)): xwax__jvb for
            xwax__jvb in null_set}
        lpaav__bhcm, _, _ = _parse_query_expr(ckpm__llw, env, [], [], None,
            join_cleaned_cols=btrsp__leyw)
        zngk__exjnm = (pd.core.computation.ops.BinOp.
            _disallow_scalar_only_bool_ops)
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            ehidm__kcscq = pd.core.computation.ops.BinOp('&', lpaav__bhcm,
                expr_node)
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = zngk__exjnm
        return ehidm__kcscq

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                zpgk__ezld = set()
                wvvcq__yhchv = set()
                utipe__yxxp = _insert_NA_cond_body(expr_node.lhs, zpgk__ezld)
                yjqv__jrg = _insert_NA_cond_body(expr_node.rhs, wvvcq__yhchv)
                ukv__wxi = zpgk__ezld.intersection(wvvcq__yhchv)
                zpgk__ezld.difference_update(ukv__wxi)
                wvvcq__yhchv.difference_update(ukv__wxi)
                null_set.update(ukv__wxi)
                expr_node.lhs = append_null_checks(utipe__yxxp, zpgk__ezld)
                expr_node.rhs = append_null_checks(yjqv__jrg, wvvcq__yhchv)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            taw__cca = expr_node.name
            keci__hzl, col_name = taw__cca.split('.')
            if keci__hzl == 'left':
                wayyd__jra = left_columns
                data = left_data
            else:
                wayyd__jra = right_columns
                data = right_data
            mpct__sysdw = data[wayyd__jra.index(col_name)]
            if bodo.utils.typing.is_nullable(mpct__sysdw):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    tsoln__ziq = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        xcpdt__jcw = str(expr_node.lhs)
        afkg__xce = str(expr_node.rhs)
        if xcpdt__jcw.startswith('left.') and afkg__xce.startswith('left.'
            ) or xcpdt__jcw.startswith('right.') and afkg__xce.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [xcpdt__jcw.split('.')[1]]
        right_on = [afkg__xce.split('.')[1]]
        if xcpdt__jcw.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        zfnpj__gxflp, tfza__ipji, hoj__phqk = _extract_equal_conds(expr_node
            .lhs)
        pwbi__zrxew, sjly__vdb, zesle__rvpxa = _extract_equal_conds(expr_node
            .rhs)
        left_on = zfnpj__gxflp + pwbi__zrxew
        right_on = tfza__ipji + sjly__vdb
        if hoj__phqk is None:
            return left_on, right_on, zesle__rvpxa
        if zesle__rvpxa is None:
            return left_on, right_on, hoj__phqk
        expr_node.lhs = hoj__phqk
        expr_node.rhs = zesle__rvpxa
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    dtua__qgbtg = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (dtua__qgbtg,))
    lrj__bft = dict()
    igi__aoqr = pd.core.computation.parsing.clean_column_name
    for name, ggxia__vcbt in (('left', left_columns), ('right', right_columns)
        ):
        for xwax__jvb in ggxia__vcbt:
            eglu__vwrq = igi__aoqr(xwax__jvb)
            zgtw__wxrai = name, eglu__vwrq
            if zgtw__wxrai in lrj__bft:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{xwax__jvb}' and '{lrj__bft[eglu__vwrq]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            lrj__bft[zgtw__wxrai] = xwax__jvb
    sztg__evy, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=lrj__bft)
    left_on, right_on, qxdg__twc = _extract_equal_conds(sztg__evy.terms)
    return left_on, right_on, _insert_NA_cond(qxdg__twc, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    zlf__szil = dict(sort=sort, copy=copy, validate=validate)
    rzyk__hfls = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    cpjxr__qlq = tuple(sorted(set(left.columns) & set(right.columns), key=
        lambda k: str(k)))
    vvj__rjd = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in cpjxr__qlq and ('left.' in on_str or 'right.' in
                on_str):
                left_on, right_on, neq__oyn = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if neq__oyn is None:
                    vvj__rjd = ''
                else:
                    vvj__rjd = str(neq__oyn)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = cpjxr__qlq
        right_keys = cpjxr__qlq
    else:
        if is_overload_true(left_index):
            left_keys = ['$_bodo_index_']
        else:
            left_keys = get_overload_const_list(left_on)
            validate_keys(left_keys, left)
        if is_overload_true(right_index):
            right_keys = ['$_bodo_index_']
        else:
            right_keys = get_overload_const_list(right_on)
            validate_keys(right_keys, right)
    if (not left_on or not right_on) and not is_overload_none(on):
        raise BodoError(
            f"DataFrame.merge(): Merge condition '{get_overload_const_str(on)}' requires a cross join to implement, but cross join is not supported."
            )
    if not is_overload_bool(indicator):
        raise_bodo_error(
            'DataFrame.merge(): indicator must be a constant boolean')
    indicator_val = get_overload_const_bool(indicator)
    if not is_overload_bool(_bodo_na_equal):
        raise_bodo_error(
            'DataFrame.merge(): bodo extension _bodo_na_equal must be a constant boolean'
            )
    jnkx__lhav = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        vmz__pbfd = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        vmz__pbfd = list(get_overload_const_list(suffixes))
    suffix_x = vmz__pbfd[0]
    suffix_y = vmz__pbfd[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    kycfi__xdkq = (
        "def _impl(left, right, how='inner', on=None, left_on=None,\n")
    kycfi__xdkq += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    kycfi__xdkq += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    kycfi__xdkq += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, jnkx__lhav, vvj__rjd))
    iof__pfjls = {}
    exec(kycfi__xdkq, {'bodo': bodo}, iof__pfjls)
    _impl = iof__pfjls['_impl']
    return _impl


def common_validate_merge_merge_asof_spec(name_func, left, right, on,
    left_on, right_on, left_index, right_index, suffixes):
    if not isinstance(left, DataFrameType) or not isinstance(right,
        DataFrameType):
        raise BodoError(name_func + '() requires dataframe inputs')
    valid_dataframe_column_types = (ArrayItemArrayType, MapArrayType,
        StructArrayType, CategoricalArrayType, types.Array,
        IntegerArrayType, DecimalArrayType, IntervalArrayType)
    pnms__eakn = {string_array_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    ydzf__guxhv = {get_overload_const_str(bsd__nsdi) for bsd__nsdi in (
        left_on, right_on, on) if is_overload_constant_str(bsd__nsdi)}
    for df in (left, right):
        for i, xwax__jvb in enumerate(df.data):
            if not isinstance(xwax__jvb, valid_dataframe_column_types
                ) and xwax__jvb not in pnms__eakn:
                raise BodoError(
                    f'{name_func}(): use of column with {type(xwax__jvb)} in merge unsupported'
                    )
            if df.columns[i] in ydzf__guxhv and isinstance(xwax__jvb,
                MapArrayType):
                raise BodoError(
                    f'{name_func}(): merge on MapArrayType unsupported')
    ensure_constant_arg(name_func, 'left_index', left_index, bool)
    ensure_constant_arg(name_func, 'right_index', right_index, bool)
    if not is_overload_constant_tuple(suffixes
        ) and not is_overload_constant_list(suffixes):
        raise_const_error(name_func +
            "(): suffixes parameters should be ['_left', '_right']")
    if is_overload_constant_tuple(suffixes):
        vmz__pbfd = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        vmz__pbfd = list(get_overload_const_list(suffixes))
    if len(vmz__pbfd) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    cpjxr__qlq = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        yvg__qjpv = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            yvg__qjpv = on_str not in cpjxr__qlq and ('left.' in on_str or 
                'right.' in on_str)
        if len(cpjxr__qlq) == 0 and not yvg__qjpv:
            raise_bodo_error(name_func +
                '(): No common columns to perform merge on. Merge options: left_on={lon}, right_on={ron}, left_index={lidx}, right_index={ridx}'
                .format(lon=is_overload_true(left_on), ron=is_overload_true
                (right_on), lidx=is_overload_true(left_index), ridx=
                is_overload_true(right_index)))
        if not is_overload_none(left_on) or not is_overload_none(right_on):
            raise BodoError(name_func +
                '(): Can only pass argument "on" OR "left_on" and "right_on", not a combination of both.'
                )
    if (is_overload_true(left_index) or not is_overload_none(left_on)
        ) and is_overload_none(right_on) and not is_overload_true(right_index):
        raise BodoError(name_func +
            '(): Must pass right_on or right_index=True')
    if (is_overload_true(right_index) or not is_overload_none(right_on)
        ) and is_overload_none(left_on) and not is_overload_true(left_index):
        raise BodoError(name_func + '(): Must pass left_on or left_index=True')


def validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
    right_index, sort, suffixes, copy, indicator, validate):
    common_validate_merge_merge_asof_spec('merge', left, right, on, left_on,
        right_on, left_index, right_index, suffixes)
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))


def validate_merge_asof_spec(left, right, on, left_on, right_on, left_index,
    right_index, by, left_by, right_by, suffixes, tolerance,
    allow_exact_matches, direction):
    common_validate_merge_merge_asof_spec('merge_asof', left, right, on,
        left_on, right_on, left_index, right_index, suffixes)
    if not is_overload_true(allow_exact_matches):
        raise BodoError(
            'merge_asof(): allow_exact_matches parameter only supports default value True'
            )
    if not is_overload_none(tolerance):
        raise BodoError(
            'merge_asof(): tolerance parameter only supports default value None'
            )
    if not is_overload_none(by):
        raise BodoError(
            'merge_asof(): by parameter only supports default value None')
    if not is_overload_none(left_by):
        raise BodoError(
            'merge_asof(): left_by parameter only supports default value None')
    if not is_overload_none(right_by):
        raise BodoError(
            'merge_asof(): right_by parameter only supports default value None'
            )
    if not is_overload_constant_str(direction):
        raise BodoError(
            'merge_asof(): direction parameter should be of type str')
    else:
        direction = get_overload_const_str(direction)
        if direction != 'backward':
            raise BodoError(
                "merge_asof(): direction parameter only supports default value 'backward'"
                )


def validate_merge_asof_keys_length(left_on, right_on, left_index,
    right_index, left_keys, right_keys):
    if not is_overload_true(left_index) and not is_overload_true(right_index):
        if len(right_keys) != len(left_keys):
            raise BodoError('merge(): len(right_on) must equal len(left_on)')
    if not is_overload_none(left_on) and is_overload_true(right_index):
        raise BodoError(
            'merge(): right_index = True and specifying left_on is not suppported yet.'
            )
    if not is_overload_none(right_on) and is_overload_true(left_index):
        raise BodoError(
            'merge(): left_index = True and specifying right_on is not suppported yet.'
            )


def validate_keys_length(left_index, right_index, left_keys, right_keys):
    if not is_overload_true(left_index) and not is_overload_true(right_index):
        if len(right_keys) != len(left_keys):
            raise BodoError('merge(): len(right_on) must equal len(left_on)')
    if is_overload_true(right_index):
        if len(left_keys) != 1:
            raise BodoError(
                'merge(): len(left_on) must equal the number of levels in the index of "right", which is 1'
                )
    if is_overload_true(left_index):
        if len(right_keys) != 1:
            raise BodoError(
                'merge(): len(right_on) must equal the number of levels in the index of "left", which is 1'
                )


def validate_keys_dtypes(left, right, left_index, right_index, left_keys,
    right_keys):
    fblr__pgnv = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            dhz__jbuk = left.index
            gxtg__bye = isinstance(dhz__jbuk, StringIndexType)
            cibr__ycnx = right.index
            duo__yabmy = isinstance(cibr__ycnx, StringIndexType)
        elif is_overload_true(left_index):
            dhz__jbuk = left.index
            gxtg__bye = isinstance(dhz__jbuk, StringIndexType)
            cibr__ycnx = right.data[right.columns.index(right_keys[0])]
            duo__yabmy = cibr__ycnx.dtype == string_type
        elif is_overload_true(right_index):
            dhz__jbuk = left.data[left.columns.index(left_keys[0])]
            gxtg__bye = dhz__jbuk.dtype == string_type
            cibr__ycnx = right.index
            duo__yabmy = isinstance(cibr__ycnx, StringIndexType)
        if gxtg__bye and duo__yabmy:
            return
        dhz__jbuk = dhz__jbuk.dtype
        cibr__ycnx = cibr__ycnx.dtype
        try:
            fkl__fcqnz = fblr__pgnv.resolve_function_type(operator.eq, (
                dhz__jbuk, cibr__ycnx), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=dhz__jbuk, rk_dtype=cibr__ycnx))
    else:
        for xix__eiepz, ljn__mjzyp in zip(left_keys, right_keys):
            dhz__jbuk = left.data[left.columns.index(xix__eiepz)].dtype
            mklz__uaj = left.data[left.columns.index(xix__eiepz)]
            cibr__ycnx = right.data[right.columns.index(ljn__mjzyp)].dtype
            tnbhh__pbjf = right.data[right.columns.index(ljn__mjzyp)]
            if mklz__uaj == tnbhh__pbjf:
                continue
            vjuw__rvlz = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=xix__eiepz, lk_dtype=dhz__jbuk, rk=ljn__mjzyp,
                rk_dtype=cibr__ycnx))
            mdljd__frng = dhz__jbuk == string_type
            ndf__khzsk = cibr__ycnx == string_type
            if mdljd__frng ^ ndf__khzsk:
                raise_bodo_error(vjuw__rvlz)
            try:
                fkl__fcqnz = fblr__pgnv.resolve_function_type(operator.eq,
                    (dhz__jbuk, cibr__ycnx), {})
            except:
                raise_bodo_error(vjuw__rvlz)


def validate_keys(keys, df):
    aial__hax = set(keys).difference(set(df.columns))
    if len(aial__hax) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in aial__hax:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {aial__hax} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    zlf__szil = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    rzyk__hfls = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort)
    how = get_overload_const_str(how)
    if not is_overload_none(on):
        left_keys = get_overload_const_list(on)
    else:
        left_keys = ['$_bodo_index_']
    right_keys = ['$_bodo_index_']
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    kycfi__xdkq = "def _impl(left, other, on=None, how='left',\n"
    kycfi__xdkq += "    lsuffix='', rsuffix='', sort=False):\n"
    kycfi__xdkq += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    iof__pfjls = {}
    exec(kycfi__xdkq, {'bodo': bodo}, iof__pfjls)
    _impl = iof__pfjls['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        fkg__dtmki = get_overload_const_list(on)
        validate_keys(fkg__dtmki, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    cpjxr__qlq = tuple(set(left.columns) & set(other.columns))
    if len(cpjxr__qlq) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=cpjxr__qlq))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    efq__yqwg = set(left_keys) & set(right_keys)
    zgxw__xjw = set(left_columns) & set(right_columns)
    uex__vmd = zgxw__xjw - efq__yqwg
    zqge__xta = set(left_columns) - zgxw__xjw
    zmxr__szcmk = set(right_columns) - zgxw__xjw
    mpjj__pai = {}

    def insertOutColumn(col_name):
        if col_name in mpjj__pai:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        mpjj__pai[col_name] = 0
    for hkrx__byz in efq__yqwg:
        insertOutColumn(hkrx__byz)
    for hkrx__byz in uex__vmd:
        ujthn__bpq = str(hkrx__byz) + suffix_x
        catnr__ovwv = str(hkrx__byz) + suffix_y
        insertOutColumn(ujthn__bpq)
        insertOutColumn(catnr__ovwv)
    for hkrx__byz in zqge__xta:
        insertOutColumn(hkrx__byz)
    for hkrx__byz in zmxr__szcmk:
        insertOutColumn(hkrx__byz)
    if indicator_val:
        insertOutColumn('_merge')


@overload(pd.merge_asof, inline='always', no_unliteral=True)
def overload_dataframe_merge_asof(left, right, on=None, left_on=None,
    right_on=None, left_index=False, right_index=False, by=None, left_by=
    None, right_by=None, suffixes=('_x', '_y'), tolerance=None,
    allow_exact_matches=True, direction='backward'):
    validate_merge_asof_spec(left, right, on, left_on, right_on, left_index,
        right_index, by, left_by, right_by, suffixes, tolerance,
        allow_exact_matches, direction)
    if not isinstance(left, DataFrameType) or not isinstance(right,
        DataFrameType):
        raise BodoError('merge_asof() requires dataframe inputs')
    cpjxr__qlq = tuple(sorted(set(left.columns) & set(right.columns), key=
        lambda k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = cpjxr__qlq
        right_keys = cpjxr__qlq
    else:
        if is_overload_true(left_index):
            left_keys = ['$_bodo_index_']
        else:
            left_keys = get_overload_const_list(left_on)
            validate_keys(left_keys, left)
        if is_overload_true(right_index):
            right_keys = ['$_bodo_index_']
        else:
            right_keys = get_overload_const_list(right_on)
            validate_keys(right_keys, right)
    validate_merge_asof_keys_length(left_on, right_on, left_index,
        right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    if isinstance(suffixes, tuple):
        vmz__pbfd = suffixes
    if is_overload_constant_list(suffixes):
        vmz__pbfd = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        vmz__pbfd = suffixes.value
    suffix_x = vmz__pbfd[0]
    suffix_y = vmz__pbfd[1]
    kycfi__xdkq = (
        'def _impl(left, right, on=None, left_on=None, right_on=None,\n')
    kycfi__xdkq += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    kycfi__xdkq += (
        "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n")
    kycfi__xdkq += "    allow_exact_matches=True, direction='backward'):\n"
    kycfi__xdkq += '  suffix_x = suffixes[0]\n'
    kycfi__xdkq += '  suffix_y = suffixes[1]\n'
    kycfi__xdkq += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    iof__pfjls = {}
    exec(kycfi__xdkq, {'bodo': bodo}, iof__pfjls)
    _impl = iof__pfjls['_impl']
    return _impl


@overload_method(DataFrameType, 'groupby', inline='always', no_unliteral=True)
def overload_dataframe_groupby(df, by=None, axis=0, level=None, as_index=
    True, sort=False, group_keys=True, squeeze=False, observed=True, dropna
    =True):
    check_runtime_cols_unsupported(df, 'DataFrame.groupby()')
    validate_groupby_spec(df, by, axis, level, as_index, sort, group_keys,
        squeeze, observed, dropna)

    def _impl(df, by=None, axis=0, level=None, as_index=True, sort=False,
        group_keys=True, squeeze=False, observed=True, dropna=True):
        return bodo.hiframes.pd_groupby_ext.init_groupby(df, by, as_index,
            dropna)
    return _impl


def validate_groupby_spec(df, by, axis, level, as_index, sort, group_keys,
    squeeze, observed, dropna):
    if is_overload_none(by):
        raise BodoError("groupby(): 'by' must be supplied.")
    if not is_overload_zero(axis):
        raise BodoError(
            "groupby(): 'axis' parameter only supports integer value 0.")
    if not is_overload_none(level):
        raise BodoError(
            "groupby(): 'level' is not supported since MultiIndex is not supported."
            )
    if not is_literal_type(by) and not is_overload_constant_list(by):
        raise_const_error(
            f"groupby(): 'by' parameter only supports a constant column label or column labels, not {by}."
            )
    if len(set(get_overload_const_list(by)).difference(set(df.columns))) > 0:
        raise_const_error(
            "groupby(): invalid key {} for 'by' (not available in columns {})."
            .format(get_overload_const_list(by), df.columns))
    if not is_overload_constant_bool(as_index):
        raise_const_error(
            "groupby(): 'as_index' parameter must be a constant bool, not {}."
            .format(as_index))
    if not is_overload_constant_bool(dropna):
        raise_const_error(
            "groupby(): 'dropna' parameter must be a constant bool, not {}."
            .format(dropna))
    zlf__szil = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    oog__qpyl = dict(sort=False, group_keys=True, squeeze=False, observed=True)
    check_unsupported_args('Dataframe.groupby', zlf__szil, oog__qpyl,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    gelg__fuo = func_name == 'DataFrame.pivot_table'
    if gelg__fuo:
        if is_overload_none(index) or not is_literal_type(index):
            raise BodoError(
                f"DataFrame.pivot_table(): 'index' argument is required and must be constant column labels"
                )
    elif not is_overload_none(index) and not is_literal_type(index):
        raise BodoError(
            f"{func_name}(): if 'index' argument is provided it must be constant column labels"
            )
    if is_overload_none(columns) or not is_literal_type(columns):
        raise BodoError(
            f"{func_name}(): 'columns' argument is required and must be a constant column label"
            )
    if not is_overload_none(values) and not is_literal_type(values):
        raise BodoError(
            f"{func_name}(): if 'values' argument is provided it must be constant column labels"
            )
    mbgsx__vnix = get_literal_value(columns)
    if isinstance(mbgsx__vnix, (list, tuple)):
        if len(mbgsx__vnix) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {mbgsx__vnix}"
                )
        mbgsx__vnix = mbgsx__vnix[0]
    if mbgsx__vnix not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {mbgsx__vnix} not found in DataFrame {df}."
            )
    jwc__mxipc = {lsd__lxj: i for i, lsd__lxj in enumerate(df.columns)}
    arxny__sryj = jwc__mxipc[mbgsx__vnix]
    if is_overload_none(index):
        smse__pmjj = []
        bkqll__yrl = []
    else:
        bkqll__yrl = get_literal_value(index)
        if not isinstance(bkqll__yrl, (list, tuple)):
            bkqll__yrl = [bkqll__yrl]
        smse__pmjj = []
        for index in bkqll__yrl:
            if index not in jwc__mxipc:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            smse__pmjj.append(jwc__mxipc[index])
    if not (all(isinstance(lsd__lxj, int) for lsd__lxj in bkqll__yrl) or
        all(isinstance(lsd__lxj, str) for lsd__lxj in bkqll__yrl)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        olgiz__wpd = []
        uwk__jkixr = []
        rzc__sgzsg = smse__pmjj + [arxny__sryj]
        for i, lsd__lxj in enumerate(df.columns):
            if i not in rzc__sgzsg:
                olgiz__wpd.append(i)
                uwk__jkixr.append(lsd__lxj)
    else:
        uwk__jkixr = get_literal_value(values)
        if not isinstance(uwk__jkixr, (list, tuple)):
            uwk__jkixr = [uwk__jkixr]
        olgiz__wpd = []
        for val in uwk__jkixr:
            if val not in jwc__mxipc:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            olgiz__wpd.append(jwc__mxipc[val])
    if all(isinstance(lsd__lxj, int) for lsd__lxj in uwk__jkixr):
        uwk__jkixr = np.array(uwk__jkixr, 'int64')
    elif all(isinstance(lsd__lxj, str) for lsd__lxj in uwk__jkixr):
        uwk__jkixr = pd.array(uwk__jkixr, 'string')
    else:
        raise BodoError(
            f"{func_name}(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    oogvv__ecgjd = set(olgiz__wpd) | set(smse__pmjj) | {arxny__sryj}
    if len(oogvv__ecgjd) != len(olgiz__wpd) + len(smse__pmjj) + 1:
        raise BodoError(
            f"{func_name}(): 'index', 'columns', and 'values' must all refer to different columns"
            )

    def check_valid_index_typ(index_column):
        if isinstance(index_column, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType, bodo.
            IntervalArrayType)):
            raise BodoError(
                f"{func_name}(): 'index' DataFrame column must have scalar rows"
                )
        if isinstance(index_column, bodo.CategoricalArrayType):
            raise BodoError(
                f"{func_name}(): 'index' DataFrame column does not support categorical data"
                )
    if len(smse__pmjj) == 0:
        index = df.index
        if isinstance(index, MultiIndexType):
            raise BodoError(
                f"{func_name}(): 'index' cannot be None with a DataFrame with a multi-index"
                )
        if not isinstance(index, RangeIndexType):
            check_valid_index_typ(index.data)
        if not is_literal_type(df.index.name_typ):
            raise BodoError(
                f"{func_name}(): If 'index' is None, the name of the DataFrame's Index must be constant at compile-time"
                )
    else:
        for giu__vdged in smse__pmjj:
            index_column = df.data[giu__vdged]
            check_valid_index_typ(index_column)
    sxprf__fehmz = df.data[arxny__sryj]
    if isinstance(sxprf__fehmz, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(sxprf__fehmz, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for dqtfw__qqfa in olgiz__wpd:
        ljnks__zpwmc = df.data[dqtfw__qqfa]
        if isinstance(ljnks__zpwmc, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType)
            ) or ljnks__zpwmc == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return (bkqll__yrl, mbgsx__vnix, uwk__jkixr, smse__pmjj, arxny__sryj,
        olgiz__wpd)


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    (bkqll__yrl, mbgsx__vnix, uwk__jkixr, giu__vdged, arxny__sryj, iki__cbnlw
        ) = (pivot_error_checking(data, index, columns, values,
        'DataFrame.pivot'))
    if len(bkqll__yrl) == 0:
        if is_overload_none(data.index.name_typ):
            bkqll__yrl = [None]
        else:
            bkqll__yrl = [get_literal_value(data.index.name_typ)]
    if len(uwk__jkixr) == 1:
        msdl__bdj = None
    else:
        msdl__bdj = uwk__jkixr
    kycfi__xdkq = 'def impl(data, index=None, columns=None, values=None):\n'
    kycfi__xdkq += f'    pivot_values = data.iloc[:, {arxny__sryj}].unique()\n'
    kycfi__xdkq += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(giu__vdged) == 0:
        kycfi__xdkq += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        kycfi__xdkq += '        (\n'
        for edglf__gfvvb in giu__vdged:
            kycfi__xdkq += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {edglf__gfvvb}),
"""
        kycfi__xdkq += '        ),\n'
    kycfi__xdkq += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {arxny__sryj}),),
"""
    kycfi__xdkq += '        (\n'
    for dqtfw__qqfa in iki__cbnlw:
        kycfi__xdkq += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {dqtfw__qqfa}),
"""
    kycfi__xdkq += '        ),\n'
    kycfi__xdkq += '        pivot_values,\n'
    kycfi__xdkq += '        index_lit_tup,\n'
    kycfi__xdkq += '        columns_lit,\n'
    kycfi__xdkq += '        values_name_const,\n'
    kycfi__xdkq += '    )\n'
    iof__pfjls = {}
    exec(kycfi__xdkq, {'bodo': bodo, 'index_lit_tup': tuple(bkqll__yrl),
        'columns_lit': mbgsx__vnix, 'values_name_const': msdl__bdj}, iof__pfjls
        )
    impl = iof__pfjls['impl']
    return impl


@overload(pd.pivot_table, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot_table', inline='always',
    no_unliteral=True)
def overload_dataframe_pivot_table(data, values=None, index=None, columns=
    None, aggfunc='mean', fill_value=None, margins=False, dropna=True,
    margins_name='All', observed=False, sort=True, _pivot_values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot_table()')
    zlf__szil = dict(fill_value=fill_value, margins=margins, dropna=dropna,
        margins_name=margins_name, observed=observed, sort=sort)
    rzyk__hfls = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    if _pivot_values is None:
        (bkqll__yrl, mbgsx__vnix, uwk__jkixr, giu__vdged, arxny__sryj,
            iki__cbnlw) = (pivot_error_checking(data, index, columns,
            values, 'DataFrame.pivot_table'))
        if len(uwk__jkixr) == 1:
            msdl__bdj = None
        else:
            msdl__bdj = uwk__jkixr
        kycfi__xdkq = 'def impl(\n'
        kycfi__xdkq += '    data,\n'
        kycfi__xdkq += '    values=None,\n'
        kycfi__xdkq += '    index=None,\n'
        kycfi__xdkq += '    columns=None,\n'
        kycfi__xdkq += '    aggfunc="mean",\n'
        kycfi__xdkq += '    fill_value=None,\n'
        kycfi__xdkq += '    margins=False,\n'
        kycfi__xdkq += '    dropna=True,\n'
        kycfi__xdkq += '    margins_name="All",\n'
        kycfi__xdkq += '    observed=False,\n'
        kycfi__xdkq += '    sort=True,\n'
        kycfi__xdkq += '    _pivot_values=None,\n'
        kycfi__xdkq += '):\n'
        xmpg__iro = giu__vdged + [arxny__sryj] + iki__cbnlw
        kycfi__xdkq += f'    data = data.iloc[:, {xmpg__iro}]\n'
        noc__vlh = bkqll__yrl + [mbgsx__vnix]
        kycfi__xdkq += (
            f'    data = data.groupby({noc__vlh!r}, as_index=False).agg(aggfunc)\n'
            )
        kycfi__xdkq += (
            f'    pivot_values = data.iloc[:, {len(giu__vdged)}].unique()\n')
        kycfi__xdkq += (
            '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n')
        kycfi__xdkq += '        (\n'
        for i in range(0, len(giu__vdged)):
            kycfi__xdkq += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),
"""
        kycfi__xdkq += '        ),\n'
        kycfi__xdkq += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(giu__vdged)}),),
"""
        kycfi__xdkq += '        (\n'
        for i in range(len(giu__vdged) + 1, len(iki__cbnlw) + len(
            giu__vdged) + 1):
            kycfi__xdkq += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),
"""
        kycfi__xdkq += '        ),\n'
        kycfi__xdkq += '        pivot_values,\n'
        kycfi__xdkq += '        index_lit_tup,\n'
        kycfi__xdkq += '        columns_lit,\n'
        kycfi__xdkq += '        values_name_const,\n'
        kycfi__xdkq += '        check_duplicates=False,\n'
        kycfi__xdkq += '    )\n'
        iof__pfjls = {}
        exec(kycfi__xdkq, {'bodo': bodo, 'numba': numba, 'index_lit_tup':
            tuple(bkqll__yrl), 'columns_lit': mbgsx__vnix,
            'values_name_const': msdl__bdj}, iof__pfjls)
        impl = iof__pfjls['impl']
        return impl
    if aggfunc == 'mean':

        def _impl(data, values=None, index=None, columns=None, aggfunc=
            'mean', fill_value=None, margins=False, dropna=True,
            margins_name='All', observed=False, sort=True, _pivot_values=None):
            return bodo.hiframes.pd_groupby_ext.pivot_table_dummy(data,
                values, index, columns, 'mean', _pivot_values)
        return _impl

    def _impl(data, values=None, index=None, columns=None, aggfunc='mean',
        fill_value=None, margins=False, dropna=True, margins_name='All',
        observed=False, sort=True, _pivot_values=None):
        return bodo.hiframes.pd_groupby_ext.pivot_table_dummy(data, values,
            index, columns, aggfunc, _pivot_values)
    return _impl


@overload(pd.crosstab, inline='always', no_unliteral=True)
def crosstab_overload(index, columns, values=None, rownames=None, colnames=
    None, aggfunc=None, margins=False, margins_name='All', dropna=True,
    normalize=False, _pivot_values=None):
    zlf__szil = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    rzyk__hfls = dict(values=None, rownames=None, colnames=None, aggfunc=
        None, margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(index, SeriesType):
        raise BodoError(
            f"pandas.crosstab(): 'index' argument only supported for Series types, found {index}"
            )
    if not isinstance(columns, SeriesType):
        raise BodoError(
            f"pandas.crosstab(): 'columns' argument only supported for Series types, found {columns}"
            )

    def _impl(index, columns, values=None, rownames=None, colnames=None,
        aggfunc=None, margins=False, margins_name='All', dropna=True,
        normalize=False, _pivot_values=None):
        return bodo.hiframes.pd_groupby_ext.crosstab_dummy(index, columns,
            _pivot_values)
    return _impl


@overload_method(DataFrameType, 'sort_values', inline='always',
    no_unliteral=True)
def overload_dataframe_sort_values(df, by, axis=0, ascending=True, inplace=
    False, kind='quicksort', na_position='last', ignore_index=False, key=
    None, _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.sort_values()')
    zlf__szil = dict(ignore_index=ignore_index, key=key)
    rzyk__hfls = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'sort_values')
    validate_sort_values_spec(df, by, axis, ascending, inplace, kind,
        na_position)

    def _impl(df, by, axis=0, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', ignore_index=False, key=None,
        _bodo_transformed=False):
        return bodo.hiframes.pd_dataframe_ext.sort_values_dummy(df, by,
            ascending, inplace, na_position)
    return _impl


def validate_sort_values_spec(df, by, axis, ascending, inplace, kind,
    na_position):
    if is_overload_none(by) or not is_literal_type(by
        ) and not is_overload_constant_list(by):
        raise_const_error(
            "sort_values(): 'by' parameter only supports a constant column label or column labels. by={}"
            .format(by))
    clqql__otp = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        clqql__otp.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        vuqs__kclp = [get_overload_const_tuple(by)]
    else:
        vuqs__kclp = get_overload_const_list(by)
    vuqs__kclp = set((k, '') if (k, '') in clqql__otp else k for k in
        vuqs__kclp)
    if len(vuqs__kclp.difference(clqql__otp)) > 0:
        cagn__comqn = list(set(get_overload_const_list(by)).difference(
            clqql__otp))
        raise_bodo_error(f'sort_values(): invalid keys {cagn__comqn} for by.')
    if not is_overload_zero(axis):
        raise_bodo_error(
            "sort_values(): 'axis' parameter only supports integer value 0.")
    if not is_overload_bool(ascending) and not is_overload_bool_list(ascending
        ):
        raise_bodo_error(
            "sort_values(): 'ascending' parameter must be of type bool or list of bool, not {}."
            .format(ascending))
    if not is_overload_bool(inplace):
        raise_bodo_error(
            "sort_values(): 'inplace' parameter must be of type bool, not {}."
            .format(inplace))
    if kind != 'quicksort' and not isinstance(kind, types.Omitted):
        warnings.warn(BodoWarning(
            'sort_values(): specifying sorting algorithm is not supported in Bodo. Bodo uses stable sort.'
            ))
    if is_overload_constant_str(na_position):
        na_position = get_overload_const_str(na_position)
        if na_position not in ('first', 'last'):
            raise BodoError(
                "sort_values(): na_position should either be 'first' or 'last'"
                )
    elif is_overload_constant_list(na_position):
        sda__uvci = get_overload_const_list(na_position)
        for na_position in sda__uvci:
            if na_position not in ('first', 'last'):
                raise BodoError(
                    "sort_values(): Every value in na_position should either be 'first' or 'last'"
                    )
    else:
        raise_const_error(
            f'sort_values(): na_position parameter must be a literal constant of type str or a constant list of str with 1 entry per key column, not {na_position}'
            )
    na_position = get_overload_const_str(na_position)
    if na_position not in ['first', 'last']:
        raise BodoError(
            "sort_values(): na_position should either be 'first' or 'last'")


@overload_method(DataFrameType, 'sort_index', inline='always', no_unliteral
    =True)
def overload_dataframe_sort_index(df, axis=0, level=None, ascending=True,
    inplace=False, kind='quicksort', na_position='last', sort_remaining=
    True, ignore_index=False, key=None):
    check_runtime_cols_unsupported(df, 'DataFrame.sort_index()')
    zlf__szil = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    rzyk__hfls = dict(axis=0, level=None, kind='quicksort', sort_remaining=
        True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_bool(ascending):
        raise BodoError(
            "DataFrame.sort_index(): 'ascending' parameter must be of type bool"
            )
    if not is_overload_bool(inplace):
        raise BodoError(
            "DataFrame.sort_index(): 'inplace' parameter must be of type bool")
    if not is_overload_constant_str(na_position) or get_overload_const_str(
        na_position) not in ('first', 'last'):
        raise_bodo_error(
            "DataFrame.sort_index(): 'na_position' should either be 'first' or 'last'"
            )

    def _impl(df, axis=0, level=None, ascending=True, inplace=False, kind=
        'quicksort', na_position='last', sort_remaining=True, ignore_index=
        False, key=None):
        return bodo.hiframes.pd_dataframe_ext.sort_values_dummy(df,
            '$_bodo_index_', ascending, inplace, na_position)
    return _impl


@overload_method(DataFrameType, 'fillna', inline='always', no_unliteral=True)
def overload_dataframe_fillna(df, value=None, method=None, axis=None,
    inplace=False, limit=None, downcast=None):
    check_runtime_cols_unsupported(df, 'DataFrame.fillna()')
    zlf__szil = dict(limit=limit, downcast=downcast)
    rzyk__hfls = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    lcaax__tqxx = not is_overload_none(value)
    likcl__aalsl = not is_overload_none(method)
    if lcaax__tqxx and likcl__aalsl:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not lcaax__tqxx and not likcl__aalsl:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if lcaax__tqxx:
        nrqzl__rbhe = 'value=value'
    else:
        nrqzl__rbhe = 'method=method'
    data_args = [(
        f"df['{lsd__lxj}'].fillna({nrqzl__rbhe}, inplace=inplace)" if
        isinstance(lsd__lxj, str) else
        f'df[{lsd__lxj}].fillna({nrqzl__rbhe}, inplace=inplace)') for
        lsd__lxj in df.columns]
    kycfi__xdkq = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        kycfi__xdkq += '  ' + '  \n'.join(data_args) + '\n'
        iof__pfjls = {}
        exec(kycfi__xdkq, {}, iof__pfjls)
        impl = iof__pfjls['impl']
        return impl
    else:
        return _gen_init_df(kycfi__xdkq, df.columns, ', '.join(egz__saa +
            '.values' for egz__saa in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    zlf__szil = dict(col_level=col_level, col_fill=col_fill)
    rzyk__hfls = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'reset_index')
    if not _is_all_levels(df, level):
        raise_bodo_error(
            'DataFrame.reset_index(): only dropping all index levels supported'
            )
    if not is_overload_constant_bool(drop):
        raise BodoError(
            "DataFrame.reset_index(): 'drop' parameter should be a constant boolean value"
            )
    if not is_overload_constant_bool(inplace):
        raise BodoError(
            "DataFrame.reset_index(): 'inplace' parameter should be a constant boolean value"
            )
    kycfi__xdkq = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    kycfi__xdkq += (
        '  index = bodo.hiframes.pd_index_ext.init_range_index(0, len(df), 1, None)\n'
        )
    drop = is_overload_true(drop)
    inplace = is_overload_true(inplace)
    columns = df.columns
    data_args = [
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}\n'.
        format(i, '' if inplace else '.copy()') for i in range(len(df.columns))
        ]
    if not drop:
        gbrit__gwgi = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            gbrit__gwgi)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            kycfi__xdkq += (
                '  m_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
                )
            jxbu__iwx = ['m_index._data[{}]'.format(i) for i in range(df.
                index.nlevels)]
            data_args = jxbu__iwx + data_args
        else:
            iwnnv__vooly = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [iwnnv__vooly] + data_args
    return _gen_init_df(kycfi__xdkq, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    mxop__gpi = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and mxop__gpi == 1 or is_overload_constant_list(level) and list(
        get_overload_const_list(level)) == list(range(mxop__gpi))


@overload_method(DataFrameType, 'dropna', inline='always', no_unliteral=True)
def overload_dataframe_dropna(df, axis=0, how='any', thresh=None, subset=
    None, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.dropna()')
    if not is_overload_constant_bool(inplace) or is_overload_true(inplace):
        raise BodoError('DataFrame.dropna(): inplace=True is not supported')
    if not is_overload_zero(axis):
        raise_bodo_error(f'df.dropna(): only axis=0 supported')
    ensure_constant_values('dropna', 'how', how, ('any', 'all'))
    if is_overload_none(subset):
        sfon__tiwsl = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        ulp__oor = get_overload_const_list(subset)
        sfon__tiwsl = []
        for tdg__mrzg in ulp__oor:
            if tdg__mrzg not in df.columns:
                raise_bodo_error(
                    f"df.dropna(): column '{tdg__mrzg}' not in data frame columns {df}"
                    )
            sfon__tiwsl.append(df.columns.index(tdg__mrzg))
    zcxqk__htbhk = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(zcxqk__htbhk))
    kycfi__xdkq = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(zcxqk__htbhk):
        kycfi__xdkq += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    kycfi__xdkq += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in sfon__tiwsl)))
    kycfi__xdkq += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(kycfi__xdkq, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    zlf__szil = dict(index=index, level=level, errors=errors)
    rzyk__hfls = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', zlf__szil, rzyk__hfls,
        package_name='pandas', module_name='DataFrame')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'drop')
    if not is_overload_constant_bool(inplace):
        raise_bodo_error(
            "DataFrame.drop(): 'inplace' parameter should be a constant bool")
    if not is_overload_none(labels):
        if not is_overload_none(columns):
            raise BodoError(
                "Dataframe.drop(): Cannot specify both 'labels' and 'columns'")
        if not is_overload_constant_int(axis) or get_overload_const_int(axis
            ) != 1:
            raise_bodo_error('DataFrame.drop(): only axis=1 supported')
        if is_overload_constant_str(labels):
            lzohb__dne = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            lzohb__dne = get_overload_const_list(labels)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    else:
        if is_overload_none(columns):
            raise BodoError(
                "DataFrame.drop(): Need to specify at least one of 'labels' or 'columns'"
                )
        if is_overload_constant_str(columns):
            lzohb__dne = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            lzohb__dne = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for lsd__lxj in lzohb__dne:
        if lsd__lxj not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(lsd__lxj, df.columns))
    if len(set(lzohb__dne)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    lhdr__kivep = tuple(lsd__lxj for lsd__lxj in df.columns if lsd__lxj not in
        lzohb__dne)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.columns.index(lsd__lxj), '.copy()' if not inplace else ''
        ) for lsd__lxj in lhdr__kivep)
    kycfi__xdkq = (
        'def impl(df, labels=None, axis=0, index=None, columns=None,\n')
    kycfi__xdkq += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(kycfi__xdkq, lhdr__kivep, data_args, index)


@overload_method(DataFrameType, 'append', inline='always', no_unliteral=True)
def overload_dataframe_append(df, other, ignore_index=False,
    verify_integrity=False, sort=None):
    check_runtime_cols_unsupported(df, 'DataFrame.append()')
    check_runtime_cols_unsupported(other, 'DataFrame.append()')
    if isinstance(other, DataFrameType):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat((df, other), ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    if isinstance(other, types.BaseTuple):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat((df,) + other, ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    if isinstance(other, types.List) and isinstance(other.dtype, DataFrameType
        ):
        return (lambda df, other, ignore_index=False, verify_integrity=
            False, sort=None: pd.concat([df] + other, ignore_index=
            ignore_index, verify_integrity=verify_integrity))
    raise BodoError(
        'invalid df.append() input. Only dataframe and list/tuple of dataframes supported'
        )


@overload_method(DataFrameType, 'sample', inline='always', no_unliteral=True)
def overload_dataframe_sample(df, n=None, frac=None, replace=False, weights
    =None, random_state=None, axis=None, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.sample()')
    zlf__szil = dict(random_state=random_state, weights=weights, axis=axis,
        ignore_index=ignore_index)
    meebc__ujfmp = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', zlf__szil, meebc__ujfmp,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    zcxqk__htbhk = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(zcxqk__htbhk))
    kycfi__xdkq = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    for i in range(zcxqk__htbhk):
        kycfi__xdkq += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    kycfi__xdkq += '  if frac is None:\n'
    kycfi__xdkq += '    frac_d = -1.0\n'
    kycfi__xdkq += '  else:\n'
    kycfi__xdkq += '    frac_d = frac\n'
    kycfi__xdkq += '  if n is None:\n'
    kycfi__xdkq += '    n_i = 0\n'
    kycfi__xdkq += '  else:\n'
    kycfi__xdkq += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    kycfi__xdkq += (
        """  ({0},), index_arr = bodo.libs.array_kernels.sample_table_operation(({0},), {1}, n_i, frac_d, replace)
"""
        .format(data_args, index))
    kycfi__xdkq += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return bodo.hiframes.dataframe_impl._gen_init_df(kycfi__xdkq, df.
        columns, data_args, 'index')


@numba.njit
def _sizeof_fmt(num, size_qualifier=''):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return f'{num:3.1f}{size_qualifier} {x}'
        num /= 1024.0
    return f'{num:3.1f}{size_qualifier} PB'


@overload_method(DataFrameType, 'info', no_unliteral=True)
def overload_dataframe_info(df, verbose=None, buf=None, max_cols=None,
    memory_usage=None, show_counts=None, null_counts=None):
    check_runtime_cols_unsupported(df, 'DataFrame.info()')
    twuih__aewpa = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    qwly__bqkra = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', twuih__aewpa, qwly__bqkra,
        package_name='pandas', module_name='DataFrame')
    nlx__vjm = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            kabo__mlwe = nlx__vjm + '\n'
            kabo__mlwe += 'Index: 0 entries\n'
            kabo__mlwe += 'Empty DataFrame'
            print(kabo__mlwe)
        return _info_impl
    else:
        kycfi__xdkq = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        kycfi__xdkq += '    ncols = df.shape[1]\n'
        kycfi__xdkq += f'    lines = "{nlx__vjm}\\n"\n'
        kycfi__xdkq += f'    lines += "{df.index}: "\n'
        kycfi__xdkq += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            kycfi__xdkq += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            kycfi__xdkq += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            kycfi__xdkq += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        kycfi__xdkq += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        kycfi__xdkq += (
            f'    space = {max(len(str(k)) for k in df.columns) + 1}\n')
        kycfi__xdkq += '    column_width = max(space, 7)\n'
        kycfi__xdkq += '    column= "Column"\n'
        kycfi__xdkq += '    underl= "------"\n'
        kycfi__xdkq += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        kycfi__xdkq += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        kycfi__xdkq += '    mem_size = 0\n'
        kycfi__xdkq += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        kycfi__xdkq += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        kycfi__xdkq += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        vckwt__vbx = dict()
        for i in range(len(df.columns)):
            kycfi__xdkq += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            ouqyu__sbw = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                ouqyu__sbw = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                kysqg__onhz = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                ouqyu__sbw = f'{kysqg__onhz[:-7]}'
            kycfi__xdkq += f'    col_dtype[{i}] = "{ouqyu__sbw}"\n'
            if ouqyu__sbw in vckwt__vbx:
                vckwt__vbx[ouqyu__sbw] += 1
            else:
                vckwt__vbx[ouqyu__sbw] = 1
            kycfi__xdkq += f'    col_name[{i}] = "{df.columns[i]}"\n'
            kycfi__xdkq += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        kycfi__xdkq += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        kycfi__xdkq += '    for i in column_info:\n'
        kycfi__xdkq += "        lines += f'{i}\\n'\n"
        qajar__rlsn = ', '.join(f'{k}({vckwt__vbx[k]})' for k in sorted(
            vckwt__vbx))
        kycfi__xdkq += f"    lines += 'dtypes: {qajar__rlsn}\\n'\n"
        kycfi__xdkq += '    mem_size += df.index.nbytes\n'
        kycfi__xdkq += '    total_size = _sizeof_fmt(mem_size)\n'
        kycfi__xdkq += "    lines += f'memory usage: {total_size}'\n"
        kycfi__xdkq += '    print(lines)\n'
        iof__pfjls = {}
        exec(kycfi__xdkq, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo':
            bodo, 'np': np}, iof__pfjls)
        _info_impl = iof__pfjls['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    kycfi__xdkq = 'def impl(df, index=True, deep=False):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes'
         for i in range(len(df.columns)))
    if is_overload_true(index):
        hzzkq__oyulz = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes\n,')
        cret__atjxv = ','.join(f"'{lsd__lxj}'" for lsd__lxj in df.columns)
        arr = f"bodo.utils.conversion.coerce_to_array(('Index',{cret__atjxv}))"
        index = f'bodo.hiframes.pd_index_ext.init_binary_str_index({arr})'
        kycfi__xdkq += f"""  return bodo.hiframes.pd_series_ext.init_series(({hzzkq__oyulz}{data}), {index}, None)
"""
    else:
        ywkpj__qxpdm = ',' if len(df.columns) == 1 else ''
        qnr__bua = gen_const_tup(df.columns)
        kycfi__xdkq += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{ywkpj__qxpdm}), pd.Index({qnr__bua}), None)
"""
    iof__pfjls = {}
    exec(kycfi__xdkq, {'bodo': bodo, 'pd': pd}, iof__pfjls)
    impl = iof__pfjls['impl']
    return impl


@overload(pd.read_excel, no_unliteral=True)
def overload_read_excel(io, sheet_name=0, header=0, names=None, index_col=
    None, usecols=None, squeeze=False, dtype=None, engine=None, converters=
    None, true_values=None, false_values=None, skiprows=None, nrows=None,
    na_values=None, keep_default_na=True, na_filter=True, verbose=False,
    parse_dates=False, date_parser=None, thousands=None, comment=None,
    skipfooter=0, convert_float=True, mangle_dupe_cols=True, _bodo_df_type=None
    ):
    df_type = _bodo_df_type.instance_type
    pvlsz__rhl = 'read_excel_df{}'.format(next_label())
    setattr(types, pvlsz__rhl, df_type)
    mqe__zyl = False
    if is_overload_constant_list(parse_dates):
        mqe__zyl = get_overload_const_list(parse_dates)
    xvfb__htoot = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    kycfi__xdkq = (
        """
def impl(
    io,
    sheet_name=0,
    header=0,
    names=None,
    index_col=None,
    usecols=None,
    squeeze=False,
    dtype=None,
    engine=None,
    converters=None,
    true_values=None,
    false_values=None,
    skiprows=None,
    nrows=None,
    na_values=None,
    keep_default_na=True,
    na_filter=True,
    verbose=False,
    parse_dates=False,
    date_parser=None,
    thousands=None,
    comment=None,
    skipfooter=0,
    convert_float=True,
    mangle_dupe_cols=True,
    _bodo_df_type=None,
):
    with numba.objmode(df="{}"):
        df = pd.read_excel(
            io,
            sheet_name,
            header,
            {},
            index_col,
            usecols,
            squeeze,
            {{{}}},
            engine,
            converters,
            true_values,
            false_values,
            skiprows,
            nrows,
            na_values,
            keep_default_na,
            na_filter,
            verbose,
            {},
            date_parser,
            thousands,
            comment,
            skipfooter,
            convert_float,
            mangle_dupe_cols,
        )
    return df
    """
        .format(pvlsz__rhl, list(df_type.columns), xvfb__htoot, mqe__zyl))
    iof__pfjls = {}
    exec(kycfi__xdkq, globals(), iof__pfjls)
    impl = iof__pfjls['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as mtqbt__zow:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    kycfi__xdkq = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    kycfi__xdkq += (
        '    ylabel=None, title=None, legend=True, fontsize=None, \n')
    kycfi__xdkq += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        kycfi__xdkq += '   fig, ax = plt.subplots()\n'
    else:
        kycfi__xdkq += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        kycfi__xdkq += '   fig.set_figwidth(figsize[0])\n'
        kycfi__xdkq += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        kycfi__xdkq += '   xlabel = x\n'
    kycfi__xdkq += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        kycfi__xdkq += '   ylabel = y\n'
    else:
        kycfi__xdkq += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        kycfi__xdkq += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        kycfi__xdkq += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    kycfi__xdkq += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            kycfi__xdkq += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            egwp__njg = get_overload_const_str(x)
            pdcz__jot = df.columns.index(egwp__njg)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if pdcz__jot != i:
                        kycfi__xdkq += f"""   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])
"""
        else:
            kycfi__xdkq += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        kycfi__xdkq += '   ax.scatter(df[x], df[y], s=20)\n'
        kycfi__xdkq += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        kycfi__xdkq += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        kycfi__xdkq += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        kycfi__xdkq += '   ax.legend()\n'
    kycfi__xdkq += '   return ax\n'
    iof__pfjls = {}
    exec(kycfi__xdkq, {'bodo': bodo, 'plt': plt}, iof__pfjls)
    impl = iof__pfjls['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for ulwfs__nilmy in df_typ.data:
        if not (isinstance(ulwfs__nilmy, IntegerArrayType) or isinstance(
            ulwfs__nilmy.dtype, types.Number) or ulwfs__nilmy.dtype in (
            bodo.datetime64ns, bodo.timedelta64ns)):
            return False
    return True


def typeref_to_type(v):
    if isinstance(v, types.BaseTuple):
        return types.BaseTuple.from_types(tuple(typeref_to_type(a) for a in v))
    return v.instance_type if isinstance(v, (types.TypeRef, types.NumberClass)
        ) else v


def _install_typer_for_type(type_name, typ):

    @type_callable(typ)
    def type_call_type(context):

        def typer(*args, **kws):
            args = tuple(typeref_to_type(v) for v in args)
            kws = {name: typeref_to_type(v) for name, v in kws.items()}
            return types.TypeRef(typ(*args, **kws))
        return typer
    no_side_effect_call_tuples.add((type_name, bodo))
    no_side_effect_call_tuples.add((typ,))


def _install_type_call_typers():
    for type_name in bodo_types_with_params:
        typ = getattr(bodo, type_name)
        _install_typer_for_type(type_name, typ)


_install_type_call_typers()


def set_df_col(df, cname, arr, inplace):
    df[cname] = arr


@infer_global(set_df_col)
class SetDfColInfer(AbstractTemplate):

    def generic(self, args, kws):
        from bodo.hiframes.pd_dataframe_ext import DataFrameType
        assert not kws
        assert len(args) == 4
        assert isinstance(args[1], types.Literal)
        pty__xbf = args[0]
        omzxr__zzdqk = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        vos__uea = pty__xbf
        check_runtime_cols_unsupported(pty__xbf, 'set_df_col()')
        if isinstance(pty__xbf, DataFrameType):
            index = pty__xbf.index
            if len(pty__xbf.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(pty__xbf.columns) == 0:
                    index = val.index
                val = val.data
            if is_pd_index_type(val):
                val = bodo.utils.typing.get_index_data_arr_types(val)[0]
            if isinstance(val, types.List):
                val = dtype_to_array_type(val.dtype)
            if not is_array_typ(val):
                val = dtype_to_array_type(val)
            if omzxr__zzdqk in pty__xbf.columns:
                lhdr__kivep = pty__xbf.columns
                nagl__uwtd = pty__xbf.columns.index(omzxr__zzdqk)
                zzdus__wgrlo = list(pty__xbf.data)
                zzdus__wgrlo[nagl__uwtd] = val
                zzdus__wgrlo = tuple(zzdus__wgrlo)
            else:
                lhdr__kivep = pty__xbf.columns + (omzxr__zzdqk,)
                zzdus__wgrlo = pty__xbf.data + (val,)
            vos__uea = DataFrameType(zzdus__wgrlo, index, lhdr__kivep,
                pty__xbf.dist, pty__xbf.is_table_format)
        return vos__uea(*args)


SetDfColInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    cxug__tuc = {}

    def _rewrite_membership_op(self, node, left, right):
        bywuz__vpfr = node.op
        op = self.visit(bywuz__vpfr)
        return op, bywuz__vpfr, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    dbpos__cfdrg = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in dbpos__cfdrg:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in dbpos__cfdrg:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        lyjqs__iceeo = node.attr
        value = node.value
        uoms__whnr = pd.core.computation.ops.LOCAL_TAG
        if lyjqs__iceeo in ('str', 'dt'):
            try:
                dsqm__cwa = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as imhyq__sfjh:
                col_name = imhyq__sfjh.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            dsqm__cwa = str(self.visit(value))
        zgtw__wxrai = dsqm__cwa, lyjqs__iceeo
        if zgtw__wxrai in join_cleaned_cols:
            lyjqs__iceeo = join_cleaned_cols[zgtw__wxrai]
        name = dsqm__cwa + '.' + lyjqs__iceeo
        if name.startswith(uoms__whnr):
            name = name[len(uoms__whnr):]
        if lyjqs__iceeo in ('str', 'dt'):
            eitsg__dmyj = columns[cleaned_columns.index(dsqm__cwa)]
            cxug__tuc[eitsg__dmyj] = dsqm__cwa
            self.env.scope[name] = 0
            return self.term_type(uoms__whnr + name, self.env)
        dbpos__cfdrg.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in dbpos__cfdrg:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        dvpir__vfvnu = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        omzxr__zzdqk = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(dvpir__vfvnu), omzxr__zzdqk))

    def op__str__(self):
        aszh__ayfp = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            wbyi__auoo)) for wbyi__auoo in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(aszh__ayfp)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(aszh__ayfp)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(aszh__ayfp))
    jyfxx__crg = (pd.core.computation.expr.BaseExprVisitor.
        _rewrite_membership_op)
    cby__izkyg = pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop
    ivi__khf = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    jqcey__ekmw = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    mqizt__rttt = pd.core.computation.ops.Term.__str__
    geua__gald = pd.core.computation.ops.MathCall.__str__
    fgr__fybja = pd.core.computation.ops.Op.__str__
    zngk__exjnm = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
    try:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            _rewrite_membership_op)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            _maybe_evaluate_binop)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = (
            visit_Attribute)
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = lambda self, left, right: (left, right)
        pd.core.computation.ops.Term.__str__ = __str__
        pd.core.computation.ops.MathCall.__str__ = math__str__
        pd.core.computation.ops.Op.__str__ = op__str__
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        sztg__evy = pd.core.computation.expr.Expr(expr, env=env)
        ftiwa__qci = str(sztg__evy)
    except pd.core.computation.ops.UndefinedVariableError as imhyq__sfjh:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == imhyq__sfjh.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {imhyq__sfjh}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            jyfxx__crg)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            cby__izkyg)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = ivi__khf
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = jqcey__ekmw
        pd.core.computation.ops.Term.__str__ = mqizt__rttt
        pd.core.computation.ops.MathCall.__str__ = geua__gald
        pd.core.computation.ops.Op.__str__ = fgr__fybja
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (
            zngk__exjnm)
    sblz__vpli = pd.core.computation.parsing.clean_column_name
    cxug__tuc.update({lsd__lxj: sblz__vpli(lsd__lxj) for lsd__lxj in
        columns if sblz__vpli(lsd__lxj) in sztg__evy.names})
    return sztg__evy, ftiwa__qci, cxug__tuc


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        ajtrf__tpuv = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(ajtrf__tpuv))
        asjpp__rze = namedtuple('Pandas', col_names)
        fifyu__ped = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], asjpp__rze)
        super(DataFrameTupleIterator, self).__init__(name, fifyu__ped)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


def _get_series_dtype(arr_typ):
    if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
        return pd_timestamp_type
    return arr_typ.dtype


def get_itertuples():
    pass


@infer_global(get_itertuples)
class TypeIterTuples(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) % 2 == 0, 'name and column pairs expected'
        col_names = [a.literal_value for a in args[:len(args) // 2]]
        lneby__qclwo = [if_series_to_array_type(a) for a in args[len(args) //
            2:]]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        lneby__qclwo = [types.Array(types.int64, 1, 'C')] + lneby__qclwo
        jiob__ikc = DataFrameTupleIterator(col_names, lneby__qclwo)
        return jiob__ikc(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        ctdvb__xvd = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            ctdvb__xvd)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    hni__qsa = args[len(args) // 2:]
    hlirb__abr = sig.args[len(sig.args) // 2:]
    sjv__frmzr = context.make_helper(builder, sig.return_type)
    pwwg__ekg = context.get_constant(types.intp, 0)
    zuc__mwo = cgutils.alloca_once_value(builder, pwwg__ekg)
    sjv__frmzr.index = zuc__mwo
    for i, arr in enumerate(hni__qsa):
        setattr(sjv__frmzr, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(hni__qsa, hlirb__abr):
        context.nrt.incref(builder, arr_typ, arr)
    res = sjv__frmzr._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    wao__fwqg, = sig.args
    dhji__ybmu, = args
    sjv__frmzr = context.make_helper(builder, wao__fwqg, value=dhji__ybmu)
    lvrpn__fuddx = signature(types.intp, wao__fwqg.array_types[1])
    tffw__hffl = context.compile_internal(builder, lambda a: len(a),
        lvrpn__fuddx, [sjv__frmzr.array0])
    index = builder.load(sjv__frmzr.index)
    lojsu__uxzy = builder.icmp(lc.ICMP_SLT, index, tffw__hffl)
    result.set_valid(lojsu__uxzy)
    with builder.if_then(lojsu__uxzy):
        values = [index]
        for i, arr_typ in enumerate(wao__fwqg.array_types[1:]):
            bwpd__velzd = getattr(sjv__frmzr, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                shy__dfv = signature(pd_timestamp_type, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    shy__dfv, [bwpd__velzd, index])
            else:
                shy__dfv = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    shy__dfv, [bwpd__velzd, index])
            values.append(val)
        value = context.make_tuple(builder, wao__fwqg.yield_type, values)
        result.yield_(value)
        wjjz__ckg = cgutils.increment_index(builder, index)
        builder.store(wjjz__ckg, sjv__frmzr.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    qkbt__cavdw = ir.Assign(rhs, lhs, expr.loc)
    rxdk__etmp = lhs
    hskfy__oechd = []
    xijf__pgkj = []
    xwth__rzty = typ.count
    for i in range(xwth__rzty):
        qnyc__pefj = ir.Var(rxdk__etmp.scope, mk_unique_var('{}_size{}'.
            format(rxdk__etmp.name, i)), rxdk__etmp.loc)
        ctda__wpca = ir.Expr.static_getitem(lhs, i, None, rxdk__etmp.loc)
        self.calltypes[ctda__wpca] = None
        hskfy__oechd.append(ir.Assign(ctda__wpca, qnyc__pefj, rxdk__etmp.loc))
        self._define(equiv_set, qnyc__pefj, types.intp, ctda__wpca)
        xijf__pgkj.append(qnyc__pefj)
    ttig__faou = tuple(xijf__pgkj)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        ttig__faou, pre=[qkbt__cavdw] + hskfy__oechd)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
