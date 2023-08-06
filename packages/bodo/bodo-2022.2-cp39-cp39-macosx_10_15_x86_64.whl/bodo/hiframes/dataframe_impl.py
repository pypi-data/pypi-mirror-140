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
        sypih__wimw = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({sypih__wimw})\n'
            )
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    check_runtime_cols_unsupported(df, 'DataFrame.columns')
    difxm__zigq = 'def impl(df):\n'
    coa__skd = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    difxm__zigq += f'  return {coa__skd}'
    rjbb__dfrp = {}
    exec(difxm__zigq, {'bodo': bodo}, rjbb__dfrp)
    impl = rjbb__dfrp['impl']
    return impl


@overload_attribute(DataFrameType, 'values')
def overload_dataframe_values(df):
    check_runtime_cols_unsupported(df, 'DataFrame.values')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.values: only supported for dataframes containing numeric values'
            )
    oihzb__pkzm = len(df.columns)
    hjon__clv = set(i for i in range(oihzb__pkzm) if isinstance(df.data[i],
        IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in hjon__clv else '') for i in
        range(oihzb__pkzm))
    difxm__zigq = 'def f(df):\n'.format()
    difxm__zigq += '    return np.stack(({},), 1)\n'.format(data_args)
    rjbb__dfrp = {}
    exec(difxm__zigq, {'bodo': bodo, 'np': np}, rjbb__dfrp)
    jbr__wjo = rjbb__dfrp['f']
    return jbr__wjo


@overload_method(DataFrameType, 'to_numpy', inline='always', no_unliteral=True)
def overload_dataframe_to_numpy(df, dtype=None, copy=False, na_value=_no_input
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.to_numpy()')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.to_numpy(): only supported for dataframes containing numeric values'
            )
    heu__bfayf = {'dtype': dtype, 'na_value': na_value}
    mba__cqsb = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', heu__bfayf, mba__cqsb,
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
            cuhy__iyhj = bodo.hiframes.table.compute_num_runtime_columns(t)
            return cuhy__iyhj * len(t)
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
            cuhy__iyhj = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), cuhy__iyhj
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), types.int64(ncols))


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    difxm__zigq = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    qzdzc__kjqb = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    difxm__zigq += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{qzdzc__kjqb}), {index}, None)
"""
    rjbb__dfrp = {}
    exec(difxm__zigq, {'bodo': bodo}, rjbb__dfrp)
    impl = rjbb__dfrp['impl']
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
    heu__bfayf = {'copy': copy, 'errors': errors}
    mba__cqsb = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', heu__bfayf, mba__cqsb, package_name
        ='pandas', module_name='DataFrame')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "DataFrame.astype(): 'dtype' when passed as string must be a constant value"
            )
    extra_globals = None
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        cva__vttrs = _bodo_object_typeref.instance_type
        assert isinstance(cva__vttrs, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        extra_globals = {}
        rzwx__zro = {}
        for i, name in enumerate(cva__vttrs.columns):
            arr_typ = cva__vttrs.data[i]
            if isinstance(arr_typ, IntegerArrayType):
                ftqd__vikzj = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype)
            elif arr_typ == boolean_array:
                ftqd__vikzj = boolean_dtype
            else:
                ftqd__vikzj = arr_typ.dtype
            extra_globals[f'_bodo_schema{i}'] = ftqd__vikzj
            rzwx__zro[name] = f'_bodo_schema{i}'
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {rzwx__zro[hhi__auzg]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             if hhi__auzg in rzwx__zro else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})' for
            i, hhi__auzg in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        myiof__vzdf = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(myiof__vzdf[hhi__auzg])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             if hhi__auzg in myiof__vzdf else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})' for
            i, hhi__auzg in enumerate(df.columns))
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
    phcj__qzzts = []
    for i in range(len(df.columns)):
        arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
        if is_overload_true(deep):
            phcj__qzzts.append(arr + '.copy()')
        elif is_overload_false(deep):
            phcj__qzzts.append(arr)
        else:
            phcj__qzzts.append(f'{arr}.copy() if deep else {arr}')
    header = 'def impl(df, deep=True):\n'
    return _gen_init_df(header, df.columns, ', '.join(phcj__qzzts))


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    heu__bfayf = {'index': index, 'level': level, 'errors': errors}
    mba__cqsb = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', heu__bfayf, mba__cqsb,
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
        smjht__lhbh = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        smjht__lhbh = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    moxm__davry = [smjht__lhbh.get(df.columns[i], df.columns[i]) for i in
        range(len(df.columns))]
    phcj__qzzts = []
    for i in range(len(df.columns)):
        arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
        if is_overload_true(copy):
            phcj__qzzts.append(arr + '.copy()')
        elif is_overload_false(copy):
            phcj__qzzts.append(arr)
        else:
            phcj__qzzts.append(f'{arr}.copy() if copy else {arr}')
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    return _gen_init_df(header, moxm__davry, ', '.join(phcj__qzzts))


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    kdvep__hgdfe = not is_overload_none(items)
    hfle__meu = not is_overload_none(like)
    snslr__elx = not is_overload_none(regex)
    ajdd__bpffg = kdvep__hgdfe ^ hfle__meu ^ snslr__elx
    kone__xwhi = not (kdvep__hgdfe or hfle__meu or snslr__elx)
    if kone__xwhi:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not ajdd__bpffg:
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
        zfqo__mwfit = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        zfqo__mwfit = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert zfqo__mwfit in {0, 1}
    difxm__zigq = (
        'def impl(df, items=None, like=None, regex=None, axis=None):\n')
    if zfqo__mwfit == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if zfqo__mwfit == 1:
        jfjne__wjy = []
        gnaw__cyo = []
        nfj__uwev = []
        if kdvep__hgdfe:
            if is_overload_constant_list(items):
                acch__blyba = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if hfle__meu:
            if is_overload_constant_str(like):
                xurl__ywu = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if snslr__elx:
            if is_overload_constant_str(regex):
                redd__gbi = get_overload_const_str(regex)
                xfsrt__obe = re.compile(redd__gbi)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, hhi__auzg in enumerate(df.columns):
            if not is_overload_none(items
                ) and hhi__auzg in acch__blyba or not is_overload_none(like
                ) and xurl__ywu in str(hhi__auzg) or not is_overload_none(regex
                ) and xfsrt__obe.search(str(hhi__auzg)):
                gnaw__cyo.append(hhi__auzg)
                nfj__uwev.append(i)
        for i in nfj__uwev:
            yiuqi__omh = f'data_{i}'
            jfjne__wjy.append(yiuqi__omh)
            difxm__zigq += f"""  {yiuqi__omh} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(jfjne__wjy)
        return _gen_init_df(difxm__zigq, gnaw__cyo, data_args)


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
    wejdo__ynneg = is_overload_none(include)
    tgfue__trqq = is_overload_none(exclude)
    pic__ydl = 'DataFrame.select_dtypes'
    if wejdo__ynneg and tgfue__trqq:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not wejdo__ynneg:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            fhtv__jjmdw = [dtype_to_array_type(parse_dtype(elem, pic__ydl)) for
                elem in include]
        elif is_legal_input(include):
            fhtv__jjmdw = [dtype_to_array_type(parse_dtype(include, pic__ydl))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        fhtv__jjmdw = get_nullable_and_non_nullable_types(fhtv__jjmdw)
        dvtao__xximv = tuple(hhi__auzg for i, hhi__auzg in enumerate(df.
            columns) if df.data[i] in fhtv__jjmdw)
    else:
        dvtao__xximv = df.columns
    if not tgfue__trqq:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            jysto__fdo = [dtype_to_array_type(parse_dtype(elem, pic__ydl)) for
                elem in exclude]
        elif is_legal_input(exclude):
            jysto__fdo = [dtype_to_array_type(parse_dtype(exclude, pic__ydl))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        jysto__fdo = get_nullable_and_non_nullable_types(jysto__fdo)
        dvtao__xximv = tuple(hhi__auzg for hhi__auzg in dvtao__xximv if df.
            data[df.columns.index(hhi__auzg)] not in jysto__fdo)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(hhi__auzg)})'
         for hhi__auzg in dvtao__xximv)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, dvtao__xximv, data_args)


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
    ekm__wmq = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in ekm__wmq:
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
    ekm__wmq = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in ekm__wmq:
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
    difxm__zigq = 'def impl(df, values):\n'
    wfbm__vftf = {}
    aoov__bfxb = False
    if isinstance(values, DataFrameType):
        aoov__bfxb = True
        for i, hhi__auzg in enumerate(df.columns):
            if hhi__auzg in values.columns:
                vfisv__ntc = 'val{}'.format(i)
                difxm__zigq += (
                    """  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {})
"""
                    .format(vfisv__ntc, values.columns.index(hhi__auzg)))
                wfbm__vftf[hhi__auzg] = vfisv__ntc
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        wfbm__vftf = {hhi__auzg: 'values' for hhi__auzg in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        vfisv__ntc = 'data{}'.format(i)
        difxm__zigq += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(vfisv__ntc, i))
        data.append(vfisv__ntc)
    epst__nvgo = ['out{}'.format(i) for i in range(len(df.columns))]
    bkkpf__oyn = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    vzun__hzm = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    hqb__xlju = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, xwo__ork) in enumerate(zip(df.columns, data)):
        if cname in wfbm__vftf:
            tcui__pha = wfbm__vftf[cname]
            if aoov__bfxb:
                difxm__zigq += bkkpf__oyn.format(xwo__ork, tcui__pha,
                    epst__nvgo[i])
            else:
                difxm__zigq += vzun__hzm.format(xwo__ork, tcui__pha,
                    epst__nvgo[i])
        else:
            difxm__zigq += hqb__xlju.format(epst__nvgo[i])
    return _gen_init_df(difxm__zigq, df.columns, ','.join(epst__nvgo))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    oihzb__pkzm = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(oihzb__pkzm))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    lme__hjyko = [hhi__auzg for hhi__auzg, lebd__rqfa in zip(df.columns, df
        .data) if bodo.utils.typing._is_pandas_numeric_dtype(lebd__rqfa.dtype)]
    assert len(lme__hjyko) != 0
    web__oxyl = ''
    if not any(lebd__rqfa == types.float64 for lebd__rqfa in df.data):
        web__oxyl = '.astype(np.float64)'
    exqx__lnni = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.columns.index(hhi__auzg), '.astype(np.float64)' if 
        isinstance(df.data[df.columns.index(hhi__auzg)], IntegerArrayType) or
        df.data[df.columns.index(hhi__auzg)] == boolean_array else '') for
        hhi__auzg in lme__hjyko)
    gho__uwaf = 'np.stack(({},), 1){}'.format(exqx__lnni, web__oxyl)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(lme__hjyko))
        )
    index = f'{generate_col_to_index_func_text(lme__hjyko)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(gho__uwaf)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, lme__hjyko, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    ieaof__gvqci = dict(ddof=ddof)
    qwqv__owx = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    wrmy__ykp = '1' if is_overload_none(min_periods) else 'min_periods'
    lme__hjyko = [hhi__auzg for hhi__auzg, lebd__rqfa in zip(df.columns, df
        .data) if bodo.utils.typing._is_pandas_numeric_dtype(lebd__rqfa.dtype)]
    if len(lme__hjyko) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    web__oxyl = ''
    if not any(lebd__rqfa == types.float64 for lebd__rqfa in df.data):
        web__oxyl = '.astype(np.float64)'
    exqx__lnni = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.columns.index(hhi__auzg), '.astype(np.float64)' if 
        isinstance(df.data[df.columns.index(hhi__auzg)], IntegerArrayType) or
        df.data[df.columns.index(hhi__auzg)] == boolean_array else '') for
        hhi__auzg in lme__hjyko)
    gho__uwaf = 'np.stack(({},), 1){}'.format(exqx__lnni, web__oxyl)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(lme__hjyko))
        )
    index = f'pd.Index({lme__hjyko})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(gho__uwaf)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        wrmy__ykp)
    return _gen_init_df(header, lme__hjyko, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    ieaof__gvqci = dict(axis=axis, level=level, numeric_only=numeric_only)
    qwqv__owx = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    difxm__zigq = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    difxm__zigq += '  data = np.array([{}])\n'.format(data_args)
    coa__skd = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    difxm__zigq += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {coa__skd})\n'
        )
    rjbb__dfrp = {}
    exec(difxm__zigq, {'bodo': bodo, 'np': np}, rjbb__dfrp)
    impl = rjbb__dfrp['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    ieaof__gvqci = dict(axis=axis)
    qwqv__owx = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    difxm__zigq = 'def impl(df, axis=0, dropna=True):\n'
    difxm__zigq += '  data = np.asarray(({},))\n'.format(data_args)
    coa__skd = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(df
        .columns)
    difxm__zigq += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {coa__skd})\n'
        )
    rjbb__dfrp = {}
    exec(difxm__zigq, {'bodo': bodo, 'np': np}, rjbb__dfrp)
    impl = rjbb__dfrp['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    ieaof__gvqci = dict(skipna=skipna, level=level, numeric_only=
        numeric_only, min_count=min_count)
    qwqv__owx = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    ieaof__gvqci = dict(skipna=skipna, level=level, numeric_only=
        numeric_only, min_count=min_count)
    qwqv__owx = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    ieaof__gvqci = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    qwqv__owx = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    ieaof__gvqci = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    qwqv__owx = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    ieaof__gvqci = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    qwqv__owx = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    ieaof__gvqci = dict(skipna=skipna, level=level, ddof=ddof, numeric_only
        =numeric_only)
    qwqv__owx = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    ieaof__gvqci = dict(skipna=skipna, level=level, ddof=ddof, numeric_only
        =numeric_only)
    qwqv__owx = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    ieaof__gvqci = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    qwqv__owx = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    ieaof__gvqci = dict(numeric_only=numeric_only, interpolation=interpolation)
    qwqv__owx = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    ieaof__gvqci = dict(axis=axis, skipna=skipna)
    qwqv__owx = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    for bpj__kme in df.data:
        if not (bodo.utils.utils.is_np_array_typ(bpj__kme) and (bpj__kme.
            dtype in [bodo.datetime64ns, bodo.timedelta64ns] or isinstance(
            bpj__kme.dtype, (types.Number, types.Boolean))) or isinstance(
            bpj__kme, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or
            bpj__kme in [bodo.boolean_array, bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {bpj__kme} not supported.'
                )
        if isinstance(bpj__kme, bodo.CategoricalArrayType
            ) and not bpj__kme.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    ieaof__gvqci = dict(axis=axis, skipna=skipna)
    qwqv__owx = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    for bpj__kme in df.data:
        if not (bodo.utils.utils.is_np_array_typ(bpj__kme) and (bpj__kme.
            dtype in [bodo.datetime64ns, bodo.timedelta64ns] or isinstance(
            bpj__kme.dtype, (types.Number, types.Boolean))) or isinstance(
            bpj__kme, (bodo.IntegerArrayType, bodo.CategoricalArrayType)) or
            bpj__kme in [bodo.boolean_array, bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {bpj__kme} not supported.'
                )
        if isinstance(bpj__kme, bodo.CategoricalArrayType
            ) and not bpj__kme.dtype.ordered:
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
        lme__hjyko = tuple(hhi__auzg for hhi__auzg, lebd__rqfa in zip(df.
            columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype
            (lebd__rqfa.dtype))
        out_colnames = lme__hjyko
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            qlz__tko = [numba.np.numpy_support.as_dtype(df.data[df.columns.
                index(hhi__auzg)].dtype) for hhi__auzg in out_colnames]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(qlz__tko, []))
    except NotImplementedError as asq__mbpn:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    bocnf__lmtr = ''
    if func_name in ('sum', 'prod'):
        bocnf__lmtr = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    difxm__zigq = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, bocnf__lmtr))
    if func_name == 'quantile':
        difxm__zigq = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        difxm__zigq = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        difxm__zigq += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        difxm__zigq += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    rjbb__dfrp = {}
    exec(difxm__zigq, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        rjbb__dfrp)
    impl = rjbb__dfrp['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    vfvur__muz = ''
    if func_name in ('min', 'max'):
        vfvur__muz = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        vfvur__muz = ', dtype=np.float32'
    ctve__myw = f'bodo.libs.array_ops.array_op_{func_name}'
    wjnq__pmaac = ''
    if func_name in ['sum', 'prod']:
        wjnq__pmaac = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        wjnq__pmaac = 'index'
    elif func_name == 'quantile':
        wjnq__pmaac = 'q'
    elif func_name in ['std', 'var']:
        wjnq__pmaac = 'True, ddof'
    elif func_name == 'median':
        wjnq__pmaac = 'True'
    data_args = ', '.join(
        f'{ctve__myw}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(hhi__auzg)}), {wjnq__pmaac})'
         for hhi__auzg in out_colnames)
    difxm__zigq = ''
    if func_name in ('idxmax', 'idxmin'):
        difxm__zigq += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        difxm__zigq += (
            '  data = bodo.utils.conversion.coerce_to_array(({},))\n'.
            format(data_args))
    else:
        difxm__zigq += '  data = np.asarray(({},){})\n'.format(data_args,
            vfvur__muz)
    difxm__zigq += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return difxm__zigq


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    mba__vuirh = [df_type.columns.index(hhi__auzg) for hhi__auzg in
        out_colnames]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in mba__vuirh)
    fpuj__yjdsy = '\n        '.join(f'row[{i}] = arr_{mba__vuirh[i]}[i]' for
        i in range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    rwzv__hinzy = f'len(arr_{mba__vuirh[0]})'
    jeqr__ssfv = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum':
        'np.nansum', 'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in jeqr__ssfv:
        rzf__fdxja = jeqr__ssfv[func_name]
        opeo__querv = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        difxm__zigq = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {rwzv__hinzy}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{opeo__querv})
    for i in numba.parfors.parfor.internal_prange(n):
        {fpuj__yjdsy}
        A[i] = {rzf__fdxja}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return difxm__zigq
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    ieaof__gvqci = dict(fill_method=fill_method, limit=limit, freq=freq)
    qwqv__owx = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', ieaof__gvqci, qwqv__owx,
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
    ieaof__gvqci = dict(axis=axis, skipna=skipna)
    qwqv__owx = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).cumprod()'
         for i in range(len(df.columns)))
    header = 'def impl(df, axis=None, skipna=True):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'cumsum', inline='always', no_unliteral=True)
def overload_dataframe_cumsum(df, axis=None, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.cumsum()')
    ieaof__gvqci = dict(skipna=skipna)
    qwqv__owx = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', ieaof__gvqci, qwqv__owx,
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
    ieaof__gvqci = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    qwqv__owx = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    lme__hjyko = [hhi__auzg for hhi__auzg, lebd__rqfa in zip(df.columns, df
        .data) if _is_describe_type(lebd__rqfa)]
    if len(lme__hjyko) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    bsyd__uyuy = sum(df.data[df.columns.index(hhi__auzg)].dtype == bodo.
        datetime64ns for hhi__auzg in lme__hjyko)

    def _get_describe(col_ind):
        ydn__vhdqk = df.data[col_ind].dtype == bodo.datetime64ns
        if bsyd__uyuy and bsyd__uyuy != len(lme__hjyko):
            if ydn__vhdqk:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for hhi__auzg in lme__hjyko:
        col_ind = df.columns.index(hhi__auzg)
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.columns.index(hhi__auzg)) for
        hhi__auzg in lme__hjyko)
    qdtfj__nia = "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']"
    if bsyd__uyuy == len(lme__hjyko):
        qdtfj__nia = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif bsyd__uyuy:
        qdtfj__nia = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({qdtfj__nia})'
    return _gen_init_df(header, lme__hjyko, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    ieaof__gvqci = dict(axis=axis, convert=convert, is_copy=is_copy)
    qwqv__owx = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', ieaof__gvqci, qwqv__owx,
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
    ieaof__gvqci = dict(freq=freq, axis=axis, fill_value=fill_value)
    qwqv__owx = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    for xqkrs__aioe in df.data:
        if not is_supported_shift_array_type(xqkrs__aioe):
            raise BodoError(
                f'Dataframe.shift() column input type {xqkrs__aioe.dtype} not supported yet.'
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
    ieaof__gvqci = dict(axis=axis)
    qwqv__owx = dict(axis=0)
    check_unsupported_args('DataFrame.diff', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    for xqkrs__aioe in df.data:
        if not (isinstance(xqkrs__aioe, types.Array) and (isinstance(
            xqkrs__aioe.dtype, types.Number) or xqkrs__aioe.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {xqkrs__aioe.dtype} not supported.'
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
    aqe__fzswp = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(aqe__fzswp)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        jeh__hkg = get_overload_const_list(column)
    else:
        jeh__hkg = [get_literal_value(column)]
    qnw__bscx = {hhi__auzg: i for i, hhi__auzg in enumerate(df.columns)}
    wli__jzoy = [qnw__bscx[hhi__auzg] for hhi__auzg in jeh__hkg]
    for i in wli__jzoy:
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
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{wli__jzoy[0]})\n'
        )
    for i in range(n):
        if i in wli__jzoy:
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
    heu__bfayf = {'inplace': inplace, 'append': append, 'verify_integrity':
        verify_integrity}
    mba__cqsb = {'inplace': False, 'append': False, 'verify_integrity': False}
    check_unsupported_args('DataFrame.set_index', heu__bfayf, mba__cqsb,
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
    columns = tuple(hhi__auzg for hhi__auzg in df.columns if hhi__auzg !=
        col_name)
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    heu__bfayf = {'inplace': inplace}
    mba__cqsb = {'inplace': False}
    check_unsupported_args('query', heu__bfayf, mba__cqsb, package_name=
        'pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        lgqoa__gsvwz = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[lgqoa__gsvwz]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    heu__bfayf = {'subset': subset, 'keep': keep}
    mba__cqsb = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', heu__bfayf, mba__cqsb,
        package_name='pandas', module_name='DataFrame')
    oihzb__pkzm = len(df.columns)
    difxm__zigq = "def impl(df, subset=None, keep='first'):\n"
    for i in range(oihzb__pkzm):
        difxm__zigq += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    difxm__zigq += (
        '  duplicated = bodo.libs.array_kernels.duplicated(({},))\n'.format
        (', '.join('data_{}'.format(i) for i in range(oihzb__pkzm))))
    difxm__zigq += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    difxm__zigq += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    rjbb__dfrp = {}
    exec(difxm__zigq, {'bodo': bodo}, rjbb__dfrp)
    impl = rjbb__dfrp['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    heu__bfayf = {'keep': keep, 'inplace': inplace, 'ignore_index':
        ignore_index}
    mba__cqsb = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    yrwll__edqe = []
    if is_overload_constant_list(subset):
        yrwll__edqe = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        yrwll__edqe = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        yrwll__edqe = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    jodbw__gohb = []
    for col_name in yrwll__edqe:
        if col_name not in df.columns:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        jodbw__gohb.append(df.columns.index(col_name))
    check_unsupported_args('DataFrame.drop_duplicates', heu__bfayf,
        mba__cqsb, package_name='pandas', module_name='DataFrame')
    nknp__hkc = []
    if jodbw__gohb:
        for onj__xyn in jodbw__gohb:
            if isinstance(df.data[onj__xyn], bodo.MapArrayType):
                nknp__hkc.append(df.columns[onj__xyn])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                nknp__hkc.append(col_name)
    if nknp__hkc:
        raise BodoError(
            f'DataFrame.drop_duplicates(): Columns {nknp__hkc} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    oihzb__pkzm = len(df.columns)
    fhrj__jnez = ['data_{}'.format(i) for i in jodbw__gohb]
    dxxmr__fmchs = ['data_{}'.format(i) for i in range(oihzb__pkzm) if i not in
        jodbw__gohb]
    if fhrj__jnez:
        sgsb__jab = len(fhrj__jnez)
    else:
        sgsb__jab = oihzb__pkzm
    xacyh__neo = ', '.join(fhrj__jnez + dxxmr__fmchs)
    data_args = ', '.join('data_{}'.format(i) for i in range(oihzb__pkzm))
    difxm__zigq = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(oihzb__pkzm):
        difxm__zigq += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    difxm__zigq += (
        """  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})
"""
        .format(xacyh__neo, index, sgsb__jab))
    difxm__zigq += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(difxm__zigq, df.columns, data_args, 'index')


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
                bhs__hxd = {hhi__auzg: i for i, hhi__auzg in enumerate(cond
                    .columns)}

                def cond_str(i, gen_all_false):
                    if df.columns[i] in bhs__hxd:
                        return (
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(cond, {bhs__hxd[df.columns[i]]})'
                            )
                    else:
                        gen_all_false[0] = True
                        return 'all_false'
            elif isinstance(cond, types.Array):
                cond_str = lambda i, _: f'cond[:,{i}]'
        if not hasattr(other, 'ndim') or other.ndim == 1:
            rbq__uim = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                other_map = {hhi__auzg: i for i, hhi__auzg in enumerate(
                    other.columns)}
                rbq__uim = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other_map[df.columns[i]]})'
                     if df.columns[i] in other_map else 'None')
            elif isinstance(other, types.Array):
                rbq__uim = lambda i: f'other[:,{i}]'
        oihzb__pkzm = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {rbq__uim(i)})'
             for i in range(oihzb__pkzm))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        drvgr__bdp = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(drvgr__bdp
            )


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    ieaof__gvqci = dict(inplace=inplace, level=level, errors=errors,
        try_cast=try_cast)
    qwqv__owx = dict(inplace=False, level=None, errors='raise', try_cast=False)
    check_unsupported_args(f'{func_name}', ieaof__gvqci, qwqv__owx,
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
    oihzb__pkzm = len(df.columns)
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
        other_map = {hhi__auzg: i for i, hhi__auzg in enumerate(other.columns)}
        for i in range(oihzb__pkzm):
            if df.columns[i] in other_map:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, df.data[i], other.data[other_map[df.columns[i]]]
                    )
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(oihzb__pkzm):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , df.data[i], other.data)
    else:
        for i in range(oihzb__pkzm):
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
        yinzi__nnnjz = 'out_df_type'
    else:
        yinzi__nnnjz = gen_const_tup(columns)
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    difxm__zigq = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, {yinzi__nnnjz})
"""
    rjbb__dfrp = {}
    iexyz__aneuw = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba}
    iexyz__aneuw.update(extra_globals)
    exec(difxm__zigq, iexyz__aneuw, rjbb__dfrp)
    impl = rjbb__dfrp['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        gqhmi__uoo = pd.Index(lhs.columns)
        uspzs__nfgoi = pd.Index(rhs.columns)
        qvxou__ywd, kvcve__itfc, qdyvg__nuy = gqhmi__uoo.join(uspzs__nfgoi,
            how='left' if is_inplace else 'outer', level=None,
            return_indexers=True)
        return tuple(qvxou__ywd), kvcve__itfc, qdyvg__nuy
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        yvlt__zyj = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        bxikr__ojlp = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, yvlt__zyj)
        check_runtime_cols_unsupported(rhs, yvlt__zyj)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                qvxou__ywd, kvcve__itfc, qdyvg__nuy = _get_binop_columns(lhs,
                    rhs)
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {qagkb__uoq}) {yvlt__zyj}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {ycnm__tgj})'
                     if qagkb__uoq != -1 and ycnm__tgj != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for qagkb__uoq, ycnm__tgj in zip(kvcve__itfc, qdyvg__nuy))
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, qvxou__ywd, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            ovmh__ldeqm = []
            ocgd__gjfs = []
            if op in bxikr__ojlp:
                for i, wgiqt__berh in enumerate(lhs.data):
                    if is_common_scalar_dtype([wgiqt__berh.dtype, rhs]):
                        ovmh__ldeqm.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {yvlt__zyj} rhs'
                            )
                    else:
                        hpj__wqhd = f'arr{i}'
                        ocgd__gjfs.append(hpj__wqhd)
                        ovmh__ldeqm.append(hpj__wqhd)
                data_args = ', '.join(ovmh__ldeqm)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {yvlt__zyj} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(ocgd__gjfs) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {hpj__wqhd} = np.empty(n, dtype=np.bool_)\n' for
                    hpj__wqhd in ocgd__gjfs)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(hpj__wqhd, op ==
                    operator.ne) for hpj__wqhd in ocgd__gjfs)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            ovmh__ldeqm = []
            ocgd__gjfs = []
            if op in bxikr__ojlp:
                for i, wgiqt__berh in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, wgiqt__berh.dtype]):
                        ovmh__ldeqm.append(
                            f'lhs {yvlt__zyj} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        hpj__wqhd = f'arr{i}'
                        ocgd__gjfs.append(hpj__wqhd)
                        ovmh__ldeqm.append(hpj__wqhd)
                data_args = ', '.join(ovmh__ldeqm)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, yvlt__zyj) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(ocgd__gjfs) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(hpj__wqhd) for hpj__wqhd in ocgd__gjfs)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(hpj__wqhd, op ==
                    operator.ne) for hpj__wqhd in ocgd__gjfs)
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
        drvgr__bdp = create_binary_op_overload(op)
        overload(op)(drvgr__bdp)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        yvlt__zyj = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, yvlt__zyj)
        check_runtime_cols_unsupported(right, yvlt__zyj)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                qvxou__ywd, _, qdyvg__nuy = _get_binop_columns(left, right,
                    True)
                difxm__zigq = 'def impl(left, right):\n'
                for i, ycnm__tgj in enumerate(qdyvg__nuy):
                    if ycnm__tgj == -1:
                        difxm__zigq += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    difxm__zigq += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    difxm__zigq += f"""  df_arr{i} {yvlt__zyj} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {ycnm__tgj})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    qvxou__ywd)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(difxm__zigq, qvxou__ywd, data_args,
                    index, extra_globals={'float64_arr_type': types.Array(
                    types.float64, 1, 'C')})
            difxm__zigq = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                difxm__zigq += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                difxm__zigq += '  df_arr{0} {1} right\n'.format(i, yvlt__zyj)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(difxm__zigq, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        drvgr__bdp = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(drvgr__bdp)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            yvlt__zyj = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, yvlt__zyj)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, yvlt__zyj) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        drvgr__bdp = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(drvgr__bdp)


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
            yugc__hqwei = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                yugc__hqwei[i] = bodo.libs.array_kernels.isna(obj, i)
            return yugc__hqwei
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
            yugc__hqwei = np.empty(n, np.bool_)
            for i in range(n):
                yugc__hqwei[i] = pd.isna(obj[i])
            return yugc__hqwei
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
    heu__bfayf = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    mba__cqsb = {'inplace': False, 'limit': None, 'regex': False, 'method':
        'pad'}
    check_unsupported_args('replace', heu__bfayf, mba__cqsb, package_name=
        'pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    fsgz__pxc = str(expr_node)
    return fsgz__pxc.startswith('left.') or fsgz__pxc.startswith('right.')


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    pihf__msvev = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (pihf__msvev,))
    eac__tbi = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        flxzi__ypy = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        aqikz__lhemw = {('NOT_NA', eac__tbi(wgiqt__berh)): wgiqt__berh for
            wgiqt__berh in null_set}
        mdzh__enp, _, _ = _parse_query_expr(flxzi__ypy, env, [], [], None,
            join_cleaned_cols=aqikz__lhemw)
        xmuif__cmryo = (pd.core.computation.ops.BinOp.
            _disallow_scalar_only_bool_ops)
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            xnjm__hta = pd.core.computation.ops.BinOp('&', mdzh__enp, expr_node
                )
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = xmuif__cmryo
        return xnjm__hta

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                zmbbs__btb = set()
                ndr__elf = set()
                rbwyk__zqfol = _insert_NA_cond_body(expr_node.lhs, zmbbs__btb)
                cqogr__xgz = _insert_NA_cond_body(expr_node.rhs, ndr__elf)
                krl__sbbd = zmbbs__btb.intersection(ndr__elf)
                zmbbs__btb.difference_update(krl__sbbd)
                ndr__elf.difference_update(krl__sbbd)
                null_set.update(krl__sbbd)
                expr_node.lhs = append_null_checks(rbwyk__zqfol, zmbbs__btb)
                expr_node.rhs = append_null_checks(cqogr__xgz, ndr__elf)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            jcph__stw = expr_node.name
            llni__bfjdo, col_name = jcph__stw.split('.')
            if llni__bfjdo == 'left':
                zibj__erk = left_columns
                data = left_data
            else:
                zibj__erk = right_columns
                data = right_data
            bwt__nlkhb = data[zibj__erk.index(col_name)]
            if bodo.utils.typing.is_nullable(bwt__nlkhb):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    dzr__zhjpy = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        ovmyk__dams = str(expr_node.lhs)
        nsag__eks = str(expr_node.rhs)
        if ovmyk__dams.startswith('left.') and nsag__eks.startswith('left.'
            ) or ovmyk__dams.startswith('right.') and nsag__eks.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [ovmyk__dams.split('.')[1]]
        right_on = [nsag__eks.split('.')[1]]
        if ovmyk__dams.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        cqxay__yjrgz, nmfe__reqtb, jvhcd__epfcf = _extract_equal_conds(
            expr_node.lhs)
        miaf__mvy, eij__njtq, qxrfu__iwv = _extract_equal_conds(expr_node.rhs)
        left_on = cqxay__yjrgz + miaf__mvy
        right_on = nmfe__reqtb + eij__njtq
        if jvhcd__epfcf is None:
            return left_on, right_on, qxrfu__iwv
        if qxrfu__iwv is None:
            return left_on, right_on, jvhcd__epfcf
        expr_node.lhs = jvhcd__epfcf
        expr_node.rhs = qxrfu__iwv
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    pihf__msvev = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (pihf__msvev,))
    smjht__lhbh = dict()
    eac__tbi = pd.core.computation.parsing.clean_column_name
    for name, khdwx__gmpgf in (('left', left_columns), ('right', right_columns)
        ):
        for wgiqt__berh in khdwx__gmpgf:
            ndj__rvf = eac__tbi(wgiqt__berh)
            hagli__jxp = name, ndj__rvf
            if hagli__jxp in smjht__lhbh:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{wgiqt__berh}' and '{smjht__lhbh[ndj__rvf]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            smjht__lhbh[hagli__jxp] = wgiqt__berh
    zctu__gxo, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=smjht__lhbh)
    left_on, right_on, yvzp__mhxp = _extract_equal_conds(zctu__gxo.terms)
    return left_on, right_on, _insert_NA_cond(yvzp__mhxp, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    ieaof__gvqci = dict(sort=sort, copy=copy, validate=validate)
    qwqv__owx = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    rndm__yogv = tuple(sorted(set(left.columns) & set(right.columns), key=
        lambda k: str(k)))
    jjhes__wmyf = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in rndm__yogv and ('left.' in on_str or 'right.' in
                on_str):
                left_on, right_on, zzxrn__fdi = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if zzxrn__fdi is None:
                    jjhes__wmyf = ''
                else:
                    jjhes__wmyf = str(zzxrn__fdi)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = rndm__yogv
        right_keys = rndm__yogv
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
    pbkfb__xwdii = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        ialek__fkaie = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        ialek__fkaie = list(get_overload_const_list(suffixes))
    suffix_x = ialek__fkaie[0]
    suffix_y = ialek__fkaie[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    difxm__zigq = (
        "def _impl(left, right, how='inner', on=None, left_on=None,\n")
    difxm__zigq += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    difxm__zigq += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    difxm__zigq += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, pbkfb__xwdii, jjhes__wmyf))
    rjbb__dfrp = {}
    exec(difxm__zigq, {'bodo': bodo}, rjbb__dfrp)
    _impl = rjbb__dfrp['_impl']
    return _impl


def common_validate_merge_merge_asof_spec(name_func, left, right, on,
    left_on, right_on, left_index, right_index, suffixes):
    if not isinstance(left, DataFrameType) or not isinstance(right,
        DataFrameType):
        raise BodoError(name_func + '() requires dataframe inputs')
    valid_dataframe_column_types = (ArrayItemArrayType, MapArrayType,
        StructArrayType, CategoricalArrayType, types.Array,
        IntegerArrayType, DecimalArrayType, IntervalArrayType)
    dauws__emck = {string_array_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    oet__xih = {get_overload_const_str(naf__xhre) for naf__xhre in (left_on,
        right_on, on) if is_overload_constant_str(naf__xhre)}
    for df in (left, right):
        for i, wgiqt__berh in enumerate(df.data):
            if not isinstance(wgiqt__berh, valid_dataframe_column_types
                ) and wgiqt__berh not in dauws__emck:
                raise BodoError(
                    f'{name_func}(): use of column with {type(wgiqt__berh)} in merge unsupported'
                    )
            if df.columns[i] in oet__xih and isinstance(wgiqt__berh,
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
        ialek__fkaie = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        ialek__fkaie = list(get_overload_const_list(suffixes))
    if len(ialek__fkaie) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    rndm__yogv = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        nouoj__tfli = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            nouoj__tfli = on_str not in rndm__yogv and ('left.' in on_str or
                'right.' in on_str)
        if len(rndm__yogv) == 0 and not nouoj__tfli:
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
    zhjpk__qyt = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            rzen__nojxr = left.index
            ordri__lhhc = isinstance(rzen__nojxr, StringIndexType)
            bdwgj__nci = right.index
            hkd__dkd = isinstance(bdwgj__nci, StringIndexType)
        elif is_overload_true(left_index):
            rzen__nojxr = left.index
            ordri__lhhc = isinstance(rzen__nojxr, StringIndexType)
            bdwgj__nci = right.data[right.columns.index(right_keys[0])]
            hkd__dkd = bdwgj__nci.dtype == string_type
        elif is_overload_true(right_index):
            rzen__nojxr = left.data[left.columns.index(left_keys[0])]
            ordri__lhhc = rzen__nojxr.dtype == string_type
            bdwgj__nci = right.index
            hkd__dkd = isinstance(bdwgj__nci, StringIndexType)
        if ordri__lhhc and hkd__dkd:
            return
        rzen__nojxr = rzen__nojxr.dtype
        bdwgj__nci = bdwgj__nci.dtype
        try:
            joks__qub = zhjpk__qyt.resolve_function_type(operator.eq, (
                rzen__nojxr, bdwgj__nci), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=rzen__nojxr, rk_dtype=bdwgj__nci))
    else:
        for dqcd__ynp, xjjqq__nsoaa in zip(left_keys, right_keys):
            rzen__nojxr = left.data[left.columns.index(dqcd__ynp)].dtype
            sxgvw__wjry = left.data[left.columns.index(dqcd__ynp)]
            bdwgj__nci = right.data[right.columns.index(xjjqq__nsoaa)].dtype
            jbjoc__yuc = right.data[right.columns.index(xjjqq__nsoaa)]
            if sxgvw__wjry == jbjoc__yuc:
                continue
            ezar__hingx = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=dqcd__ynp, lk_dtype=rzen__nojxr, rk=xjjqq__nsoaa,
                rk_dtype=bdwgj__nci))
            wyrwt__sujz = rzen__nojxr == string_type
            kqpi__rbnkj = bdwgj__nci == string_type
            if wyrwt__sujz ^ kqpi__rbnkj:
                raise_bodo_error(ezar__hingx)
            try:
                joks__qub = zhjpk__qyt.resolve_function_type(operator.eq, (
                    rzen__nojxr, bdwgj__nci), {})
            except:
                raise_bodo_error(ezar__hingx)


def validate_keys(keys, df):
    bbd__xxdj = set(keys).difference(set(df.columns))
    if len(bbd__xxdj) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in bbd__xxdj:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {bbd__xxdj} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    ieaof__gvqci = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    qwqv__owx = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', ieaof__gvqci, qwqv__owx,
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
    difxm__zigq = "def _impl(left, other, on=None, how='left',\n"
    difxm__zigq += "    lsuffix='', rsuffix='', sort=False):\n"
    difxm__zigq += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    rjbb__dfrp = {}
    exec(difxm__zigq, {'bodo': bodo}, rjbb__dfrp)
    _impl = rjbb__dfrp['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        pnoe__rzjv = get_overload_const_list(on)
        validate_keys(pnoe__rzjv, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    rndm__yogv = tuple(set(left.columns) & set(other.columns))
    if len(rndm__yogv) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=rndm__yogv))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    ldcqk__gviw = set(left_keys) & set(right_keys)
    zaig__ljbp = set(left_columns) & set(right_columns)
    qgbh__zfb = zaig__ljbp - ldcqk__gviw
    bayei__hcy = set(left_columns) - zaig__ljbp
    hywcv__ugcmw = set(right_columns) - zaig__ljbp
    udpdd__sioy = {}

    def insertOutColumn(col_name):
        if col_name in udpdd__sioy:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        udpdd__sioy[col_name] = 0
    for umsor__jeq in ldcqk__gviw:
        insertOutColumn(umsor__jeq)
    for umsor__jeq in qgbh__zfb:
        ujxmx__yfv = str(umsor__jeq) + suffix_x
        gdz__vvje = str(umsor__jeq) + suffix_y
        insertOutColumn(ujxmx__yfv)
        insertOutColumn(gdz__vvje)
    for umsor__jeq in bayei__hcy:
        insertOutColumn(umsor__jeq)
    for umsor__jeq in hywcv__ugcmw:
        insertOutColumn(umsor__jeq)
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
    rndm__yogv = tuple(sorted(set(left.columns) & set(right.columns), key=
        lambda k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = rndm__yogv
        right_keys = rndm__yogv
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
        ialek__fkaie = suffixes
    if is_overload_constant_list(suffixes):
        ialek__fkaie = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        ialek__fkaie = suffixes.value
    suffix_x = ialek__fkaie[0]
    suffix_y = ialek__fkaie[1]
    difxm__zigq = (
        'def _impl(left, right, on=None, left_on=None, right_on=None,\n')
    difxm__zigq += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    difxm__zigq += (
        "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n")
    difxm__zigq += "    allow_exact_matches=True, direction='backward'):\n"
    difxm__zigq += '  suffix_x = suffixes[0]\n'
    difxm__zigq += '  suffix_y = suffixes[1]\n'
    difxm__zigq += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    rjbb__dfrp = {}
    exec(difxm__zigq, {'bodo': bodo}, rjbb__dfrp)
    _impl = rjbb__dfrp['_impl']
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
    ieaof__gvqci = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    szi__fjml = dict(sort=False, group_keys=True, squeeze=False, observed=True)
    check_unsupported_args('Dataframe.groupby', ieaof__gvqci, szi__fjml,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    roo__bmul = func_name == 'DataFrame.pivot_table'
    if roo__bmul:
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
    ugys__ita = get_literal_value(columns)
    if isinstance(ugys__ita, (list, tuple)):
        if len(ugys__ita) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {ugys__ita}"
                )
        ugys__ita = ugys__ita[0]
    if ugys__ita not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {ugys__ita} not found in DataFrame {df}."
            )
    sor__vdcua = {hhi__auzg: i for i, hhi__auzg in enumerate(df.columns)}
    uvpt__cwizj = sor__vdcua[ugys__ita]
    if is_overload_none(index):
        jdl__hkkb = []
        glq__igu = []
    else:
        glq__igu = get_literal_value(index)
        if not isinstance(glq__igu, (list, tuple)):
            glq__igu = [glq__igu]
        jdl__hkkb = []
        for index in glq__igu:
            if index not in sor__vdcua:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            jdl__hkkb.append(sor__vdcua[index])
    if not (all(isinstance(hhi__auzg, int) for hhi__auzg in glq__igu) or
        all(isinstance(hhi__auzg, str) for hhi__auzg in glq__igu)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        ocvh__fuow = []
        yuas__sstoa = []
        qhqg__mhvv = jdl__hkkb + [uvpt__cwizj]
        for i, hhi__auzg in enumerate(df.columns):
            if i not in qhqg__mhvv:
                ocvh__fuow.append(i)
                yuas__sstoa.append(hhi__auzg)
    else:
        yuas__sstoa = get_literal_value(values)
        if not isinstance(yuas__sstoa, (list, tuple)):
            yuas__sstoa = [yuas__sstoa]
        ocvh__fuow = []
        for val in yuas__sstoa:
            if val not in sor__vdcua:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            ocvh__fuow.append(sor__vdcua[val])
    if all(isinstance(hhi__auzg, int) for hhi__auzg in yuas__sstoa):
        yuas__sstoa = np.array(yuas__sstoa, 'int64')
    elif all(isinstance(hhi__auzg, str) for hhi__auzg in yuas__sstoa):
        yuas__sstoa = pd.array(yuas__sstoa, 'string')
    else:
        raise BodoError(
            f"{func_name}(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    jki__rany = set(ocvh__fuow) | set(jdl__hkkb) | {uvpt__cwizj}
    if len(jki__rany) != len(ocvh__fuow) + len(jdl__hkkb) + 1:
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
    if len(jdl__hkkb) == 0:
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
        for jry__dzjr in jdl__hkkb:
            index_column = df.data[jry__dzjr]
            check_valid_index_typ(index_column)
    hgig__opre = df.data[uvpt__cwizj]
    if isinstance(hgig__opre, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(hgig__opre, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for eoz__krcsp in ocvh__fuow:
        pogx__vzqii = df.data[eoz__krcsp]
        if isinstance(pogx__vzqii, (bodo.ArrayItemArrayType, bodo.
            MapArrayType, bodo.StructArrayType, bodo.TupleArrayType)
            ) or pogx__vzqii == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return glq__igu, ugys__ita, yuas__sstoa, jdl__hkkb, uvpt__cwizj, ocvh__fuow


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    glq__igu, ugys__ita, yuas__sstoa, jry__dzjr, uvpt__cwizj, klz__gbe = (
        pivot_error_checking(data, index, columns, values, 'DataFrame.pivot'))
    if len(glq__igu) == 0:
        if is_overload_none(data.index.name_typ):
            glq__igu = [None]
        else:
            glq__igu = [get_literal_value(data.index.name_typ)]
    if len(yuas__sstoa) == 1:
        ujzw__vcc = None
    else:
        ujzw__vcc = yuas__sstoa
    difxm__zigq = 'def impl(data, index=None, columns=None, values=None):\n'
    difxm__zigq += f'    pivot_values = data.iloc[:, {uvpt__cwizj}].unique()\n'
    difxm__zigq += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(jry__dzjr) == 0:
        difxm__zigq += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        difxm__zigq += '        (\n'
        for htfa__lzvha in jry__dzjr:
            difxm__zigq += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {htfa__lzvha}),
"""
        difxm__zigq += '        ),\n'
    difxm__zigq += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {uvpt__cwizj}),),
"""
    difxm__zigq += '        (\n'
    for eoz__krcsp in klz__gbe:
        difxm__zigq += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {eoz__krcsp}),
"""
    difxm__zigq += '        ),\n'
    difxm__zigq += '        pivot_values,\n'
    difxm__zigq += '        index_lit_tup,\n'
    difxm__zigq += '        columns_lit,\n'
    difxm__zigq += '        values_name_const,\n'
    difxm__zigq += '    )\n'
    rjbb__dfrp = {}
    exec(difxm__zigq, {'bodo': bodo, 'index_lit_tup': tuple(glq__igu),
        'columns_lit': ugys__ita, 'values_name_const': ujzw__vcc}, rjbb__dfrp)
    impl = rjbb__dfrp['impl']
    return impl


@overload(pd.pivot_table, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot_table', inline='always',
    no_unliteral=True)
def overload_dataframe_pivot_table(data, values=None, index=None, columns=
    None, aggfunc='mean', fill_value=None, margins=False, dropna=True,
    margins_name='All', observed=False, sort=True, _pivot_values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot_table()')
    ieaof__gvqci = dict(fill_value=fill_value, margins=margins, dropna=
        dropna, margins_name=margins_name, observed=observed, sort=sort)
    qwqv__owx = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    if _pivot_values is None:
        (glq__igu, ugys__ita, yuas__sstoa, jry__dzjr, uvpt__cwizj, klz__gbe
            ) = (pivot_error_checking(data, index, columns, values,
            'DataFrame.pivot_table'))
        if len(yuas__sstoa) == 1:
            ujzw__vcc = None
        else:
            ujzw__vcc = yuas__sstoa
        difxm__zigq = 'def impl(\n'
        difxm__zigq += '    data,\n'
        difxm__zigq += '    values=None,\n'
        difxm__zigq += '    index=None,\n'
        difxm__zigq += '    columns=None,\n'
        difxm__zigq += '    aggfunc="mean",\n'
        difxm__zigq += '    fill_value=None,\n'
        difxm__zigq += '    margins=False,\n'
        difxm__zigq += '    dropna=True,\n'
        difxm__zigq += '    margins_name="All",\n'
        difxm__zigq += '    observed=False,\n'
        difxm__zigq += '    sort=True,\n'
        difxm__zigq += '    _pivot_values=None,\n'
        difxm__zigq += '):\n'
        qknvt__gmt = jry__dzjr + [uvpt__cwizj] + klz__gbe
        difxm__zigq += f'    data = data.iloc[:, {qknvt__gmt}]\n'
        pou__rsd = glq__igu + [ugys__ita]
        difxm__zigq += (
            f'    data = data.groupby({pou__rsd!r}, as_index=False).agg(aggfunc)\n'
            )
        difxm__zigq += (
            f'    pivot_values = data.iloc[:, {len(jry__dzjr)}].unique()\n')
        difxm__zigq += (
            '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n')
        difxm__zigq += '        (\n'
        for i in range(0, len(jry__dzjr)):
            difxm__zigq += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),
"""
        difxm__zigq += '        ),\n'
        difxm__zigq += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(jry__dzjr)}),),
"""
        difxm__zigq += '        (\n'
        for i in range(len(jry__dzjr) + 1, len(klz__gbe) + len(jry__dzjr) + 1):
            difxm__zigq += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),
"""
        difxm__zigq += '        ),\n'
        difxm__zigq += '        pivot_values,\n'
        difxm__zigq += '        index_lit_tup,\n'
        difxm__zigq += '        columns_lit,\n'
        difxm__zigq += '        values_name_const,\n'
        difxm__zigq += '        check_duplicates=False,\n'
        difxm__zigq += '    )\n'
        rjbb__dfrp = {}
        exec(difxm__zigq, {'bodo': bodo, 'numba': numba, 'index_lit_tup':
            tuple(glq__igu), 'columns_lit': ugys__ita, 'values_name_const':
            ujzw__vcc}, rjbb__dfrp)
        impl = rjbb__dfrp['impl']
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
    ieaof__gvqci = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    qwqv__owx = dict(values=None, rownames=None, colnames=None, aggfunc=
        None, margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', ieaof__gvqci, qwqv__owx,
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
    ieaof__gvqci = dict(ignore_index=ignore_index, key=key)
    qwqv__owx = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', ieaof__gvqci, qwqv__owx,
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
    ixx__nfgcf = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        ixx__nfgcf.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        wediq__zeayp = [get_overload_const_tuple(by)]
    else:
        wediq__zeayp = get_overload_const_list(by)
    wediq__zeayp = set((k, '') if (k, '') in ixx__nfgcf else k for k in
        wediq__zeayp)
    if len(wediq__zeayp.difference(ixx__nfgcf)) > 0:
        mlp__lndf = list(set(get_overload_const_list(by)).difference(
            ixx__nfgcf))
        raise_bodo_error(f'sort_values(): invalid keys {mlp__lndf} for by.')
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
        noaa__hup = get_overload_const_list(na_position)
        for na_position in noaa__hup:
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
    ieaof__gvqci = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    qwqv__owx = dict(axis=0, level=None, kind='quicksort', sort_remaining=
        True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', ieaof__gvqci, qwqv__owx,
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
    ieaof__gvqci = dict(limit=limit, downcast=downcast)
    qwqv__owx = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', ieaof__gvqci, qwqv__owx,
        package_name='pandas', module_name='DataFrame')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    ytsa__ueejy = not is_overload_none(value)
    xbki__cmeyd = not is_overload_none(method)
    if ytsa__ueejy and xbki__cmeyd:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not ytsa__ueejy and not xbki__cmeyd:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if ytsa__ueejy:
        nnuqi__jbm = 'value=value'
    else:
        nnuqi__jbm = 'method=method'
    data_args = [(
        f"df['{hhi__auzg}'].fillna({nnuqi__jbm}, inplace=inplace)" if
        isinstance(hhi__auzg, str) else
        f'df[{hhi__auzg}].fillna({nnuqi__jbm}, inplace=inplace)') for
        hhi__auzg in df.columns]
    difxm__zigq = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        difxm__zigq += '  ' + '  \n'.join(data_args) + '\n'
        rjbb__dfrp = {}
        exec(difxm__zigq, {}, rjbb__dfrp)
        impl = rjbb__dfrp['impl']
        return impl
    else:
        return _gen_init_df(difxm__zigq, df.columns, ', '.join(lebd__rqfa +
            '.values' for lebd__rqfa in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    ieaof__gvqci = dict(col_level=col_level, col_fill=col_fill)
    qwqv__owx = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', ieaof__gvqci, qwqv__owx,
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
    difxm__zigq = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    difxm__zigq += (
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
        ubm__xaufc = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            ubm__xaufc)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            difxm__zigq += (
                '  m_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
                )
            blsbs__gwvz = ['m_index._data[{}]'.format(i) for i in range(df.
                index.nlevels)]
            data_args = blsbs__gwvz + data_args
        else:
            mknk__jlxr = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [mknk__jlxr] + data_args
    return _gen_init_df(difxm__zigq, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    fswf__zrgpj = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and fswf__zrgpj == 1 or is_overload_constant_list(level
        ) and list(get_overload_const_list(level)) == list(range(fswf__zrgpj))


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
        facrf__gdtp = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        mwu__uyuek = get_overload_const_list(subset)
        facrf__gdtp = []
        for rps__cdp in mwu__uyuek:
            if rps__cdp not in df.columns:
                raise_bodo_error(
                    f"df.dropna(): column '{rps__cdp}' not in data frame columns {df}"
                    )
            facrf__gdtp.append(df.columns.index(rps__cdp))
    oihzb__pkzm = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(oihzb__pkzm))
    difxm__zigq = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(oihzb__pkzm):
        difxm__zigq += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    difxm__zigq += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in facrf__gdtp)))
    difxm__zigq += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(difxm__zigq, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    ieaof__gvqci = dict(index=index, level=level, errors=errors)
    qwqv__owx = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', ieaof__gvqci, qwqv__owx,
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
            shnyt__qexw = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            shnyt__qexw = get_overload_const_list(labels)
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
            shnyt__qexw = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            shnyt__qexw = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for hhi__auzg in shnyt__qexw:
        if hhi__auzg not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(hhi__auzg, df.columns))
    if len(set(shnyt__qexw)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    moxm__davry = tuple(hhi__auzg for hhi__auzg in df.columns if hhi__auzg
         not in shnyt__qexw)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.columns.index(hhi__auzg), '.copy()' if not inplace else
        '') for hhi__auzg in moxm__davry)
    difxm__zigq = (
        'def impl(df, labels=None, axis=0, index=None, columns=None,\n')
    difxm__zigq += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(difxm__zigq, moxm__davry, data_args, index)


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
    ieaof__gvqci = dict(random_state=random_state, weights=weights, axis=
        axis, ignore_index=ignore_index)
    btnqt__puoj = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', ieaof__gvqci, btnqt__puoj,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    oihzb__pkzm = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(oihzb__pkzm))
    difxm__zigq = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    for i in range(oihzb__pkzm):
        difxm__zigq += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    difxm__zigq += '  if frac is None:\n'
    difxm__zigq += '    frac_d = -1.0\n'
    difxm__zigq += '  else:\n'
    difxm__zigq += '    frac_d = frac\n'
    difxm__zigq += '  if n is None:\n'
    difxm__zigq += '    n_i = 0\n'
    difxm__zigq += '  else:\n'
    difxm__zigq += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    difxm__zigq += (
        """  ({0},), index_arr = bodo.libs.array_kernels.sample_table_operation(({0},), {1}, n_i, frac_d, replace)
"""
        .format(data_args, index))
    difxm__zigq += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return bodo.hiframes.dataframe_impl._gen_init_df(difxm__zigq, df.
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
    heu__bfayf = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    mba__cqsb = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', heu__bfayf, mba__cqsb,
        package_name='pandas', module_name='DataFrame')
    sqzj__xvdl = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            hopj__pbnpm = sqzj__xvdl + '\n'
            hopj__pbnpm += 'Index: 0 entries\n'
            hopj__pbnpm += 'Empty DataFrame'
            print(hopj__pbnpm)
        return _info_impl
    else:
        difxm__zigq = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        difxm__zigq += '    ncols = df.shape[1]\n'
        difxm__zigq += f'    lines = "{sqzj__xvdl}\\n"\n'
        difxm__zigq += f'    lines += "{df.index}: "\n'
        difxm__zigq += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            difxm__zigq += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            difxm__zigq += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            difxm__zigq += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        difxm__zigq += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        difxm__zigq += (
            f'    space = {max(len(str(k)) for k in df.columns) + 1}\n')
        difxm__zigq += '    column_width = max(space, 7)\n'
        difxm__zigq += '    column= "Column"\n'
        difxm__zigq += '    underl= "------"\n'
        difxm__zigq += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        difxm__zigq += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        difxm__zigq += '    mem_size = 0\n'
        difxm__zigq += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        difxm__zigq += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        difxm__zigq += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        wros__vmbgr = dict()
        for i in range(len(df.columns)):
            difxm__zigq += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            viil__pyxy = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                viil__pyxy = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                ecabj__juma = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                viil__pyxy = f'{ecabj__juma[:-7]}'
            difxm__zigq += f'    col_dtype[{i}] = "{viil__pyxy}"\n'
            if viil__pyxy in wros__vmbgr:
                wros__vmbgr[viil__pyxy] += 1
            else:
                wros__vmbgr[viil__pyxy] = 1
            difxm__zigq += f'    col_name[{i}] = "{df.columns[i]}"\n'
            difxm__zigq += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        difxm__zigq += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        difxm__zigq += '    for i in column_info:\n'
        difxm__zigq += "        lines += f'{i}\\n'\n"
        kzf__vzhs = ', '.join(f'{k}({wros__vmbgr[k]})' for k in sorted(
            wros__vmbgr))
        difxm__zigq += f"    lines += 'dtypes: {kzf__vzhs}\\n'\n"
        difxm__zigq += '    mem_size += df.index.nbytes\n'
        difxm__zigq += '    total_size = _sizeof_fmt(mem_size)\n'
        difxm__zigq += "    lines += f'memory usage: {total_size}'\n"
        difxm__zigq += '    print(lines)\n'
        rjbb__dfrp = {}
        exec(difxm__zigq, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo':
            bodo, 'np': np}, rjbb__dfrp)
        _info_impl = rjbb__dfrp['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    difxm__zigq = 'def impl(df, index=True, deep=False):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes'
         for i in range(len(df.columns)))
    if is_overload_true(index):
        oplto__rdzu = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes\n,')
        kkvt__garb = ','.join(f"'{hhi__auzg}'" for hhi__auzg in df.columns)
        arr = f"bodo.utils.conversion.coerce_to_array(('Index',{kkvt__garb}))"
        index = f'bodo.hiframes.pd_index_ext.init_binary_str_index({arr})'
        difxm__zigq += f"""  return bodo.hiframes.pd_series_ext.init_series(({oplto__rdzu}{data}), {index}, None)
"""
    else:
        qzdzc__kjqb = ',' if len(df.columns) == 1 else ''
        yinzi__nnnjz = gen_const_tup(df.columns)
        difxm__zigq += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{qzdzc__kjqb}), pd.Index({yinzi__nnnjz}), None)
"""
    rjbb__dfrp = {}
    exec(difxm__zigq, {'bodo': bodo, 'pd': pd}, rjbb__dfrp)
    impl = rjbb__dfrp['impl']
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
    qjpwn__qnom = 'read_excel_df{}'.format(next_label())
    setattr(types, qjpwn__qnom, df_type)
    dnaq__fud = False
    if is_overload_constant_list(parse_dates):
        dnaq__fud = get_overload_const_list(parse_dates)
    tisy__ehitj = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    difxm__zigq = (
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
        .format(qjpwn__qnom, list(df_type.columns), tisy__ehitj, dnaq__fud))
    rjbb__dfrp = {}
    exec(difxm__zigq, globals(), rjbb__dfrp)
    impl = rjbb__dfrp['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as asq__mbpn:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    difxm__zigq = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    difxm__zigq += (
        '    ylabel=None, title=None, legend=True, fontsize=None, \n')
    difxm__zigq += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        difxm__zigq += '   fig, ax = plt.subplots()\n'
    else:
        difxm__zigq += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        difxm__zigq += '   fig.set_figwidth(figsize[0])\n'
        difxm__zigq += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        difxm__zigq += '   xlabel = x\n'
    difxm__zigq += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        difxm__zigq += '   ylabel = y\n'
    else:
        difxm__zigq += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        difxm__zigq += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        difxm__zigq += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    difxm__zigq += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            difxm__zigq += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            mxt__hlu = get_overload_const_str(x)
            nwiz__xzei = df.columns.index(mxt__hlu)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if nwiz__xzei != i:
                        difxm__zigq += f"""   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])
"""
        else:
            difxm__zigq += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        difxm__zigq += '   ax.scatter(df[x], df[y], s=20)\n'
        difxm__zigq += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        difxm__zigq += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        difxm__zigq += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        difxm__zigq += '   ax.legend()\n'
    difxm__zigq += '   return ax\n'
    rjbb__dfrp = {}
    exec(difxm__zigq, {'bodo': bodo, 'plt': plt}, rjbb__dfrp)
    impl = rjbb__dfrp['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for lbiod__eqdj in df_typ.data:
        if not (isinstance(lbiod__eqdj, IntegerArrayType) or isinstance(
            lbiod__eqdj.dtype, types.Number) or lbiod__eqdj.dtype in (bodo.
            datetime64ns, bodo.timedelta64ns)):
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
        rbk__see = args[0]
        mvmj__eoh = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        jlbsi__hhvq = rbk__see
        check_runtime_cols_unsupported(rbk__see, 'set_df_col()')
        if isinstance(rbk__see, DataFrameType):
            index = rbk__see.index
            if len(rbk__see.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(rbk__see.columns) == 0:
                    index = val.index
                val = val.data
            if is_pd_index_type(val):
                val = bodo.utils.typing.get_index_data_arr_types(val)[0]
            if isinstance(val, types.List):
                val = dtype_to_array_type(val.dtype)
            if not is_array_typ(val):
                val = dtype_to_array_type(val)
            if mvmj__eoh in rbk__see.columns:
                moxm__davry = rbk__see.columns
                imth__cun = rbk__see.columns.index(mvmj__eoh)
                mtrn__hbxt = list(rbk__see.data)
                mtrn__hbxt[imth__cun] = val
                mtrn__hbxt = tuple(mtrn__hbxt)
            else:
                moxm__davry = rbk__see.columns + (mvmj__eoh,)
                mtrn__hbxt = rbk__see.data + (val,)
            jlbsi__hhvq = DataFrameType(mtrn__hbxt, index, moxm__davry,
                rbk__see.dist, rbk__see.is_table_format)
        return jlbsi__hhvq(*args)


SetDfColInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    oyge__msuq = {}

    def _rewrite_membership_op(self, node, left, right):
        aujo__olmmz = node.op
        op = self.visit(aujo__olmmz)
        return op, aujo__olmmz, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    uyper__jizjx = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in uyper__jizjx:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in uyper__jizjx:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        sge__erw = node.attr
        value = node.value
        tkpz__gmx = pd.core.computation.ops.LOCAL_TAG
        if sge__erw in ('str', 'dt'):
            try:
                yfl__sduuc = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as wzhof__oxfu:
                col_name = wzhof__oxfu.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            yfl__sduuc = str(self.visit(value))
        hagli__jxp = yfl__sduuc, sge__erw
        if hagli__jxp in join_cleaned_cols:
            sge__erw = join_cleaned_cols[hagli__jxp]
        name = yfl__sduuc + '.' + sge__erw
        if name.startswith(tkpz__gmx):
            name = name[len(tkpz__gmx):]
        if sge__erw in ('str', 'dt'):
            dqxsb__glmwz = columns[cleaned_columns.index(yfl__sduuc)]
            oyge__msuq[dqxsb__glmwz] = yfl__sduuc
            self.env.scope[name] = 0
            return self.term_type(tkpz__gmx + name, self.env)
        uyper__jizjx.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in uyper__jizjx:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        brf__xbtdx = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        mvmj__eoh = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(brf__xbtdx), mvmj__eoh))

    def op__str__(self):
        xnd__fglzm = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            rwtzi__igctk)) for rwtzi__igctk in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(xnd__fglzm)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(xnd__fglzm)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(xnd__fglzm))
    ayv__gpe = pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op
    yxeuj__tvsmj = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_evaluate_binop)
    bfax__rtfs = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    cnr__lxq = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    zhr__zxzg = pd.core.computation.ops.Term.__str__
    tpk__nob = pd.core.computation.ops.MathCall.__str__
    tyf__opyfs = pd.core.computation.ops.Op.__str__
    xmuif__cmryo = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
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
        zctu__gxo = pd.core.computation.expr.Expr(expr, env=env)
        klju__eqmou = str(zctu__gxo)
    except pd.core.computation.ops.UndefinedVariableError as wzhof__oxfu:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == wzhof__oxfu.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {wzhof__oxfu}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            ayv__gpe)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            yxeuj__tvsmj)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = bfax__rtfs
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = cnr__lxq
        pd.core.computation.ops.Term.__str__ = zhr__zxzg
        pd.core.computation.ops.MathCall.__str__ = tpk__nob
        pd.core.computation.ops.Op.__str__ = tyf__opyfs
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (
            xmuif__cmryo)
    chc__fpk = pd.core.computation.parsing.clean_column_name
    oyge__msuq.update({hhi__auzg: chc__fpk(hhi__auzg) for hhi__auzg in
        columns if chc__fpk(hhi__auzg) in zctu__gxo.names})
    return zctu__gxo, klju__eqmou, oyge__msuq


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        cnrrr__fqdh = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(cnrrr__fqdh))
        miiv__dexpy = namedtuple('Pandas', col_names)
        exba__cmnyq = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], miiv__dexpy)
        super(DataFrameTupleIterator, self).__init__(name, exba__cmnyq)

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
        qepo__njke = [if_series_to_array_type(a) for a in args[len(args) // 2:]
            ]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        qepo__njke = [types.Array(types.int64, 1, 'C')] + qepo__njke
        gzwx__mrch = DataFrameTupleIterator(col_names, qepo__njke)
        return gzwx__mrch(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        njjr__ogvex = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            njjr__ogvex)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    edwvi__ldxl = args[len(args) // 2:]
    xkr__davem = sig.args[len(sig.args) // 2:]
    oaot__zgh = context.make_helper(builder, sig.return_type)
    kiven__omh = context.get_constant(types.intp, 0)
    mpd__bfecx = cgutils.alloca_once_value(builder, kiven__omh)
    oaot__zgh.index = mpd__bfecx
    for i, arr in enumerate(edwvi__ldxl):
        setattr(oaot__zgh, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(edwvi__ldxl, xkr__davem):
        context.nrt.incref(builder, arr_typ, arr)
    res = oaot__zgh._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    ovo__awy, = sig.args
    fso__khho, = args
    oaot__zgh = context.make_helper(builder, ovo__awy, value=fso__khho)
    burn__abi = signature(types.intp, ovo__awy.array_types[1])
    jla__udwtj = context.compile_internal(builder, lambda a: len(a),
        burn__abi, [oaot__zgh.array0])
    index = builder.load(oaot__zgh.index)
    ryjdk__ovok = builder.icmp(lc.ICMP_SLT, index, jla__udwtj)
    result.set_valid(ryjdk__ovok)
    with builder.if_then(ryjdk__ovok):
        values = [index]
        for i, arr_typ in enumerate(ovo__awy.array_types[1:]):
            vqb__eym = getattr(oaot__zgh, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                mfb__mgyk = signature(pd_timestamp_type, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    mfb__mgyk, [vqb__eym, index])
            else:
                mfb__mgyk = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    mfb__mgyk, [vqb__eym, index])
            values.append(val)
        value = context.make_tuple(builder, ovo__awy.yield_type, values)
        result.yield_(value)
        iueg__ywhtu = cgutils.increment_index(builder, index)
        builder.store(iueg__ywhtu, oaot__zgh.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    awy__bww = ir.Assign(rhs, lhs, expr.loc)
    vbfc__yymkv = lhs
    qpgt__nbl = []
    kavus__goesu = []
    dlyb__qtz = typ.count
    for i in range(dlyb__qtz):
        yanu__jxx = ir.Var(vbfc__yymkv.scope, mk_unique_var('{}_size{}'.
            format(vbfc__yymkv.name, i)), vbfc__yymkv.loc)
        lwerb__pdn = ir.Expr.static_getitem(lhs, i, None, vbfc__yymkv.loc)
        self.calltypes[lwerb__pdn] = None
        qpgt__nbl.append(ir.Assign(lwerb__pdn, yanu__jxx, vbfc__yymkv.loc))
        self._define(equiv_set, yanu__jxx, types.intp, lwerb__pdn)
        kavus__goesu.append(yanu__jxx)
    lvnmi__oojc = tuple(kavus__goesu)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        lvnmi__oojc, pre=[awy__bww] + qpgt__nbl)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
