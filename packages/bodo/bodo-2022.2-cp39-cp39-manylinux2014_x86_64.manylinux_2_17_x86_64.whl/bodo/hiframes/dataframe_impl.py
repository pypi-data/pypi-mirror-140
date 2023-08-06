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
        xan__ahzc = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return (
            f'bodo.hiframes.pd_index_ext.init_binary_str_index({xan__ahzc})\n')
    elif all(isinstance(a, (int, float)) for a in col_names):
        arr = f'bodo.utils.conversion.coerce_to_array({col_names})'
        return f'bodo.hiframes.pd_index_ext.init_numeric_index({arr})\n'
    else:
        return f'bodo.hiframes.pd_index_ext.init_heter_index({col_names})\n'


@overload_attribute(DataFrameType, 'columns', inline='always')
def overload_dataframe_columns(df):
    check_runtime_cols_unsupported(df, 'DataFrame.columns')
    cwba__ghvsz = 'def impl(df):\n'
    yib__fowln = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(
        df.columns)
    cwba__ghvsz += f'  return {yib__fowln}'
    bxpjm__vul = {}
    exec(cwba__ghvsz, {'bodo': bodo}, bxpjm__vul)
    impl = bxpjm__vul['impl']
    return impl


@overload_attribute(DataFrameType, 'values')
def overload_dataframe_values(df):
    check_runtime_cols_unsupported(df, 'DataFrame.values')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.values: only supported for dataframes containing numeric values'
            )
    fvh__iowla = len(df.columns)
    lznfh__bys = set(i for i in range(fvh__iowla) if isinstance(df.data[i],
        IntegerArrayType))
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(i, '.astype(float)' if i in lznfh__bys else '') for i in
        range(fvh__iowla))
    cwba__ghvsz = 'def f(df):\n'.format()
    cwba__ghvsz += '    return np.stack(({},), 1)\n'.format(data_args)
    bxpjm__vul = {}
    exec(cwba__ghvsz, {'bodo': bodo, 'np': np}, bxpjm__vul)
    jrhpp__ufu = bxpjm__vul['f']
    return jrhpp__ufu


@overload_method(DataFrameType, 'to_numpy', inline='always', no_unliteral=True)
def overload_dataframe_to_numpy(df, dtype=None, copy=False, na_value=_no_input
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.to_numpy()')
    if not is_df_values_numpy_supported_dftyp(df):
        raise_bodo_error(
            'DataFrame.to_numpy(): only supported for dataframes containing numeric values'
            )
    qvw__nqaud = {'dtype': dtype, 'na_value': na_value}
    xwxv__qye = {'dtype': None, 'na_value': _no_input}
    check_unsupported_args('DataFrame.to_numpy', qvw__nqaud, xwxv__qye,
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
            zmlf__txips = bodo.hiframes.table.compute_num_runtime_columns(t)
            return zmlf__txips * len(t)
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
            zmlf__txips = bodo.hiframes.table.compute_num_runtime_columns(t)
            return len(t), zmlf__txips
        return impl
    ncols = len(df.columns)
    return lambda df: (len(df), types.int64(ncols))


@overload_attribute(DataFrameType, 'dtypes')
def overload_dataframe_dtypes(df):
    check_runtime_cols_unsupported(df, 'DataFrame.dtypes')
    cwba__ghvsz = 'def impl(df):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).dtype\n'
         for i in range(len(df.columns)))
    pak__puae = ',' if len(df.columns) == 1 else ''
    index = f'bodo.hiframes.pd_index_ext.init_heter_index({df.columns})'
    cwba__ghvsz += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{pak__puae}), {index}, None)
"""
    bxpjm__vul = {}
    exec(cwba__ghvsz, {'bodo': bodo}, bxpjm__vul)
    impl = bxpjm__vul['impl']
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
    qvw__nqaud = {'copy': copy, 'errors': errors}
    xwxv__qye = {'copy': True, 'errors': 'raise'}
    check_unsupported_args('df.astype', qvw__nqaud, xwxv__qye, package_name
        ='pandas', module_name='DataFrame')
    if dtype == types.unicode_type:
        raise_bodo_error(
            "DataFrame.astype(): 'dtype' when passed as string must be a constant value"
            )
    extra_globals = None
    if _bodo_object_typeref is not None:
        assert isinstance(_bodo_object_typeref, types.TypeRef
            ), 'Bodo schema used in DataFrame.astype should be a TypeRef'
        olf__rpqu = _bodo_object_typeref.instance_type
        assert isinstance(olf__rpqu, DataFrameType
            ), 'Bodo schema used in DataFrame.astype is only supported for DataFrame schemas'
        extra_globals = {}
        dhkmf__tqezq = {}
        for i, name in enumerate(olf__rpqu.columns):
            arr_typ = olf__rpqu.data[i]
            if isinstance(arr_typ, IntegerArrayType):
                oeum__vxkg = bodo.libs.int_arr_ext.IntDtype(arr_typ.dtype)
            elif arr_typ == boolean_array:
                oeum__vxkg = boolean_dtype
            else:
                oeum__vxkg = arr_typ.dtype
            extra_globals[f'_bodo_schema{i}'] = oeum__vxkg
            dhkmf__tqezq[name] = f'_bodo_schema{i}'
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {dhkmf__tqezq[iaj__iwe]}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             if iaj__iwe in dhkmf__tqezq else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})' for
            i, iaj__iwe in enumerate(df.columns))
    elif is_overload_constant_dict(dtype) or is_overload_constant_series(dtype
        ):
        lftlo__ymadm = get_overload_constant_dict(dtype
            ) if is_overload_constant_dict(dtype) else dict(
            get_overload_constant_series(dtype))
        data_args = ', '.join(
            f'bodo.utils.conversion.fix_arr_dtype(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {_get_dtype_str(lftlo__ymadm[iaj__iwe])}, copy, nan_to_str=_bodo_nan_to_str, from_series=True)'
             if iaj__iwe in lftlo__ymadm else
            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})' for
            i, iaj__iwe in enumerate(df.columns))
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
    dsuk__jbk = []
    for i in range(len(df.columns)):
        arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
        if is_overload_true(deep):
            dsuk__jbk.append(arr + '.copy()')
        elif is_overload_false(deep):
            dsuk__jbk.append(arr)
        else:
            dsuk__jbk.append(f'{arr}.copy() if deep else {arr}')
    header = 'def impl(df, deep=True):\n'
    return _gen_init_df(header, df.columns, ', '.join(dsuk__jbk))


@overload_method(DataFrameType, 'rename', inline='always', no_unliteral=True)
def overload_dataframe_rename(df, mapper=None, index=None, columns=None,
    axis=None, copy=True, inplace=False, level=None, errors='ignore',
    _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.rename()')
    handle_inplace_df_type_change(inplace, _bodo_transformed, 'rename')
    qvw__nqaud = {'index': index, 'level': level, 'errors': errors}
    xwxv__qye = {'index': None, 'level': None, 'errors': 'ignore'}
    check_unsupported_args('DataFrame.rename', qvw__nqaud, xwxv__qye,
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
        ysy__zhtgl = get_overload_constant_dict(mapper)
    elif not is_overload_none(columns):
        if not is_overload_none(axis):
            raise BodoError(
                "DataFrame.rename(): Cannot specify both 'axis' and 'columns'")
        if not is_overload_constant_dict(columns):
            raise_bodo_error(
                "'columns' argument to DataFrame.rename() should be a constant dictionary"
                )
        ysy__zhtgl = get_overload_constant_dict(columns)
    else:
        raise_bodo_error(
            "DataFrame.rename(): must pass columns either via 'mapper' and 'axis'=1 or 'columns'"
            )
    fbtvm__xhvg = [ysy__zhtgl.get(df.columns[i], df.columns[i]) for i in
        range(len(df.columns))]
    dsuk__jbk = []
    for i in range(len(df.columns)):
        arr = f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})'
        if is_overload_true(copy):
            dsuk__jbk.append(arr + '.copy()')
        elif is_overload_false(copy):
            dsuk__jbk.append(arr)
        else:
            dsuk__jbk.append(f'{arr}.copy() if copy else {arr}')
    header = """def impl(df, mapper=None, index=None, columns=None, axis=None, copy=True, inplace=False, level=None, errors='ignore', _bodo_transformed=False):
"""
    return _gen_init_df(header, fbtvm__xhvg, ', '.join(dsuk__jbk))


@overload_method(DataFrameType, 'filter', no_unliteral=True)
def overload_dataframe_filter(df, items=None, like=None, regex=None, axis=None
    ):
    check_runtime_cols_unsupported(df, 'DataFrame.filter()')
    shbyt__faqv = not is_overload_none(items)
    pkqwi__zjhli = not is_overload_none(like)
    asrl__nvfl = not is_overload_none(regex)
    zeuu__ylmo = shbyt__faqv ^ pkqwi__zjhli ^ asrl__nvfl
    gnsy__rkmul = not (shbyt__faqv or pkqwi__zjhli or asrl__nvfl)
    if gnsy__rkmul:
        raise BodoError(
            'DataFrame.filter(): one of keyword arguments `items`, `like`, and `regex` must be supplied'
            )
    if not zeuu__ylmo:
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
        qivnc__gcon = 0 if axis == 'index' else 1
    elif is_overload_constant_int(axis):
        axis = get_overload_const_int(axis)
        if axis not in {0, 1}:
            raise_bodo_error(
                'DataFrame.filter(): keyword arguments `axis` must be either 0 or 1 if integer'
                )
        qivnc__gcon = axis
    else:
        raise_bodo_error(
            'DataFrame.filter(): keyword arguments `axis` must be constant string or integer'
            )
    assert qivnc__gcon in {0, 1}
    cwba__ghvsz = (
        'def impl(df, items=None, like=None, regex=None, axis=None):\n')
    if qivnc__gcon == 0:
        raise BodoError(
            'DataFrame.filter(): filtering based on index is not supported.')
    if qivnc__gcon == 1:
        bkjq__jbr = []
        fdu__zchov = []
        uip__ltu = []
        if shbyt__faqv:
            if is_overload_constant_list(items):
                acksw__udo = get_overload_const_list(items)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'items' must be a list of constant strings."
                    )
        if pkqwi__zjhli:
            if is_overload_constant_str(like):
                qvdze__vml = get_overload_const_str(like)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'like' must be a constant string."
                    )
        if asrl__nvfl:
            if is_overload_constant_str(regex):
                xszb__kdmxs = get_overload_const_str(regex)
                yomsf__nds = re.compile(xszb__kdmxs)
            else:
                raise BodoError(
                    "Dataframe.filter(): argument 'regex' must be a constant string."
                    )
        for i, iaj__iwe in enumerate(df.columns):
            if not is_overload_none(items
                ) and iaj__iwe in acksw__udo or not is_overload_none(like
                ) and qvdze__vml in str(iaj__iwe) or not is_overload_none(regex
                ) and yomsf__nds.search(str(iaj__iwe)):
                fdu__zchov.append(iaj__iwe)
                uip__ltu.append(i)
        for i in uip__ltu:
            mia__blsex = f'data_{i}'
            bkjq__jbr.append(mia__blsex)
            cwba__ghvsz += f"""  {mia__blsex} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})
"""
        data_args = ', '.join(bkjq__jbr)
        return _gen_init_df(cwba__ghvsz, fdu__zchov, data_args)


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
    uplt__ucdkg = is_overload_none(include)
    nvyjb__arn = is_overload_none(exclude)
    ttsc__zawm = 'DataFrame.select_dtypes'
    if uplt__ucdkg and nvyjb__arn:
        raise_bodo_error(
            'DataFrame.select_dtypes() At least one of include or exclude must not be none'
            )

    def is_legal_input(elem):
        return is_overload_constant_str(elem) or isinstance(elem, types.
            DTypeSpec) or isinstance(elem, types.Function)
    if not uplt__ucdkg:
        if is_overload_constant_list(include):
            include = get_overload_const_list(include)
            tlw__nsssf = [dtype_to_array_type(parse_dtype(elem, ttsc__zawm)
                ) for elem in include]
        elif is_legal_input(include):
            tlw__nsssf = [dtype_to_array_type(parse_dtype(include, ttsc__zawm))
                ]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        tlw__nsssf = get_nullable_and_non_nullable_types(tlw__nsssf)
        pmj__bkkt = tuple(iaj__iwe for i, iaj__iwe in enumerate(df.columns) if
            df.data[i] in tlw__nsssf)
    else:
        pmj__bkkt = df.columns
    if not nvyjb__arn:
        if is_overload_constant_list(exclude):
            exclude = get_overload_const_list(exclude)
            kfz__rxtp = [dtype_to_array_type(parse_dtype(elem, ttsc__zawm)) for
                elem in exclude]
        elif is_legal_input(exclude):
            kfz__rxtp = [dtype_to_array_type(parse_dtype(exclude, ttsc__zawm))]
        else:
            raise_bodo_error(
                'DataFrame.select_dtypes() only supports constant strings or types as arguments'
                )
        kfz__rxtp = get_nullable_and_non_nullable_types(kfz__rxtp)
        pmj__bkkt = tuple(iaj__iwe for iaj__iwe in pmj__bkkt if df.data[df.
            columns.index(iaj__iwe)] not in kfz__rxtp)
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(iaj__iwe)})'
         for iaj__iwe in pmj__bkkt)
    header = 'def impl(df, include=None, exclude=None):\n'
    return _gen_init_df(header, pmj__bkkt, data_args)


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
    okue__rrqdf = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError(
            'DataFrame.first(): only supports a DatetimeIndex index')
    if types.unliteral(offset) not in okue__rrqdf:
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
    okue__rrqdf = (types.unicode_type, bodo.month_begin_type, bodo.
        month_end_type, bodo.week_type, bodo.date_offset_type)
    if not isinstance(df.index, DatetimeIndexType):
        raise BodoError('DataFrame.last(): only supports a DatetimeIndex index'
            )
    if types.unliteral(offset) not in okue__rrqdf:
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
    cwba__ghvsz = 'def impl(df, values):\n'
    qvrv__fvjf = {}
    kzfdv__mvxaa = False
    if isinstance(values, DataFrameType):
        kzfdv__mvxaa = True
        for i, iaj__iwe in enumerate(df.columns):
            if iaj__iwe in values.columns:
                ljp__kvch = 'val{}'.format(i)
                cwba__ghvsz += (
                    """  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(values, {})
"""
                    .format(ljp__kvch, values.columns.index(iaj__iwe)))
                qvrv__fvjf[iaj__iwe] = ljp__kvch
    elif is_iterable_type(values) and not isinstance(values, SeriesType):
        qvrv__fvjf = {iaj__iwe: 'values' for iaj__iwe in df.columns}
    else:
        raise_bodo_error(f'pd.isin(): not supported for type {values}')
    data = []
    for i in range(len(df.columns)):
        ljp__kvch = 'data{}'.format(i)
        cwba__ghvsz += (
            '  {} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {})\n'
            .format(ljp__kvch, i))
        data.append(ljp__kvch)
    nvjj__kauc = ['out{}'.format(i) for i in range(len(df.columns))]
    onmc__sgns = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  m = len({1})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] == {1}[i] if i < m else False
"""
    lil__xwl = """
  numba.parfors.parfor.init_prange()
  n = len({0})
  {2} = np.empty(n, np.bool_)
  for i in numba.parfors.parfor.internal_prange(n):
    {2}[i] = {0}[i] in {1}
"""
    olbh__axyuy = '  {} = np.zeros(len(df), np.bool_)\n'
    for i, (cname, vjrm__ebfo) in enumerate(zip(df.columns, data)):
        if cname in qvrv__fvjf:
            baomy__ljqkz = qvrv__fvjf[cname]
            if kzfdv__mvxaa:
                cwba__ghvsz += onmc__sgns.format(vjrm__ebfo, baomy__ljqkz,
                    nvjj__kauc[i])
            else:
                cwba__ghvsz += lil__xwl.format(vjrm__ebfo, baomy__ljqkz,
                    nvjj__kauc[i])
        else:
            cwba__ghvsz += olbh__axyuy.format(nvjj__kauc[i])
    return _gen_init_df(cwba__ghvsz, df.columns, ','.join(nvjj__kauc))


@overload_method(DataFrameType, 'abs', inline='always', no_unliteral=True)
def overload_dataframe_abs(df):
    check_runtime_cols_unsupported(df, 'DataFrame.abs()')
    for arr_typ in df.data:
        if not (isinstance(arr_typ.dtype, types.Number) or arr_typ.dtype ==
            bodo.timedelta64ns):
            raise_bodo_error(
                f'DataFrame.abs(): Only supported for numeric and Timedelta. Encountered array with dtype {arr_typ.dtype}'
                )
    fvh__iowla = len(df.columns)
    data_args = ', '.join(
        'np.abs(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}))'
        .format(i) for i in range(fvh__iowla))
    header = 'def impl(df):\n'
    return _gen_init_df(header, df.columns, data_args)


def overload_dataframe_corr(df, method='pearson', min_periods=1):
    mqof__ykrg = [iaj__iwe for iaj__iwe, tgxg__bci in zip(df.columns, df.
        data) if bodo.utils.typing._is_pandas_numeric_dtype(tgxg__bci.dtype)]
    assert len(mqof__ykrg) != 0
    qwf__qjwo = ''
    if not any(tgxg__bci == types.float64 for tgxg__bci in df.data):
        qwf__qjwo = '.astype(np.float64)'
    duam__mvpm = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.columns.index(iaj__iwe), '.astype(np.float64)' if 
        isinstance(df.data[df.columns.index(iaj__iwe)], IntegerArrayType) or
        df.data[df.columns.index(iaj__iwe)] == boolean_array else '') for
        iaj__iwe in mqof__ykrg)
    ehy__xaawf = 'np.stack(({},), 1){}'.format(duam__mvpm, qwf__qjwo)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(mqof__ykrg))
        )
    index = f'{generate_col_to_index_func_text(mqof__ykrg)}\n'
    header = "def impl(df, method='pearson', min_periods=1):\n"
    header += '  mat = {}\n'.format(ehy__xaawf)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 0, min_periods)\n'
    return _gen_init_df(header, mqof__ykrg, data_args, index)


@lower_builtin('df.corr', DataFrameType, types.VarArg(types.Any))
def dataframe_corr_lower(context, builder, sig, args):
    impl = overload_dataframe_corr(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


@overload_method(DataFrameType, 'cov', inline='always', no_unliteral=True)
def overload_dataframe_cov(df, min_periods=None, ddof=1):
    check_runtime_cols_unsupported(df, 'DataFrame.cov()')
    efm__ifn = dict(ddof=ddof)
    fqb__fhajr = dict(ddof=1)
    check_unsupported_args('DataFrame.cov', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    mhjvi__bmak = '1' if is_overload_none(min_periods) else 'min_periods'
    mqof__ykrg = [iaj__iwe for iaj__iwe, tgxg__bci in zip(df.columns, df.
        data) if bodo.utils.typing._is_pandas_numeric_dtype(tgxg__bci.dtype)]
    if len(mqof__ykrg) == 0:
        raise_bodo_error('DataFrame.cov(): requires non-empty dataframe')
    qwf__qjwo = ''
    if not any(tgxg__bci == types.float64 for tgxg__bci in df.data):
        qwf__qjwo = '.astype(np.float64)'
    duam__mvpm = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.columns.index(iaj__iwe), '.astype(np.float64)' if 
        isinstance(df.data[df.columns.index(iaj__iwe)], IntegerArrayType) or
        df.data[df.columns.index(iaj__iwe)] == boolean_array else '') for
        iaj__iwe in mqof__ykrg)
    ehy__xaawf = 'np.stack(({},), 1){}'.format(duam__mvpm, qwf__qjwo)
    data_args = ', '.join('res[:,{}]'.format(i) for i in range(len(mqof__ykrg))
        )
    index = f'pd.Index({mqof__ykrg})\n'
    header = 'def impl(df, min_periods=None, ddof=1):\n'
    header += '  mat = {}\n'.format(ehy__xaawf)
    header += '  res = bodo.libs.array_kernels.nancorr(mat, 1, {})\n'.format(
        mhjvi__bmak)
    return _gen_init_df(header, mqof__ykrg, data_args, index)


@overload_method(DataFrameType, 'count', inline='always', no_unliteral=True)
def overload_dataframe_count(df, axis=0, level=None, numeric_only=False):
    check_runtime_cols_unsupported(df, 'DataFrame.count()')
    efm__ifn = dict(axis=axis, level=level, numeric_only=numeric_only)
    fqb__fhajr = dict(axis=0, level=None, numeric_only=False)
    check_unsupported_args('DataFrame.count', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}))'
         for i in range(len(df.columns)))
    cwba__ghvsz = 'def impl(df, axis=0, level=None, numeric_only=False):\n'
    cwba__ghvsz += '  data = np.array([{}])\n'.format(data_args)
    yib__fowln = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(
        df.columns)
    cwba__ghvsz += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {yib__fowln})\n'
        )
    bxpjm__vul = {}
    exec(cwba__ghvsz, {'bodo': bodo, 'np': np}, bxpjm__vul)
    impl = bxpjm__vul['impl']
    return impl


@overload_method(DataFrameType, 'nunique', inline='always', no_unliteral=True)
def overload_dataframe_nunique(df, axis=0, dropna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.unique()')
    efm__ifn = dict(axis=axis)
    fqb__fhajr = dict(axis=0)
    if not is_overload_bool(dropna):
        raise BodoError('DataFrame.nunique: dropna must be a boolean value')
    check_unsupported_args('DataFrame.nunique', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.libs.array_kernels.nunique(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), dropna)'
         for i in range(len(df.columns)))
    cwba__ghvsz = 'def impl(df, axis=0, dropna=True):\n'
    cwba__ghvsz += '  data = np.asarray(({},))\n'.format(data_args)
    yib__fowln = bodo.hiframes.dataframe_impl.generate_col_to_index_func_text(
        df.columns)
    cwba__ghvsz += (
        f'  return bodo.hiframes.pd_series_ext.init_series(data, {yib__fowln})\n'
        )
    bxpjm__vul = {}
    exec(cwba__ghvsz, {'bodo': bodo, 'np': np}, bxpjm__vul)
    impl = bxpjm__vul['impl']
    return impl


@overload_method(DataFrameType, 'prod', inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'product', inline='always', no_unliteral=True)
def overload_dataframe_prod(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.prod()')
    efm__ifn = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    fqb__fhajr = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.prod', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'prod', axis=axis)


@overload_method(DataFrameType, 'sum', inline='always', no_unliteral=True)
def overload_dataframe_sum(df, axis=None, skipna=None, level=None,
    numeric_only=None, min_count=0):
    check_runtime_cols_unsupported(df, 'DataFrame.sum()')
    efm__ifn = dict(skipna=skipna, level=level, numeric_only=numeric_only,
        min_count=min_count)
    fqb__fhajr = dict(skipna=None, level=None, numeric_only=None, min_count=0)
    check_unsupported_args('DataFrame.sum', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'sum', axis=axis)


@overload_method(DataFrameType, 'max', inline='always', no_unliteral=True)
def overload_dataframe_max(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.max()')
    efm__ifn = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fqb__fhajr = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.max', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'max', axis=axis)


@overload_method(DataFrameType, 'min', inline='always', no_unliteral=True)
def overload_dataframe_min(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.min()')
    efm__ifn = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fqb__fhajr = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.min', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'min', axis=axis)


@overload_method(DataFrameType, 'mean', inline='always', no_unliteral=True)
def overload_dataframe_mean(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.mean()')
    efm__ifn = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fqb__fhajr = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.mean', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'mean', axis=axis)


@overload_method(DataFrameType, 'var', inline='always', no_unliteral=True)
def overload_dataframe_var(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.var()')
    efm__ifn = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    fqb__fhajr = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.var', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'var', axis=axis)


@overload_method(DataFrameType, 'std', inline='always', no_unliteral=True)
def overload_dataframe_std(df, axis=None, skipna=None, level=None, ddof=1,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.std()')
    efm__ifn = dict(skipna=skipna, level=level, ddof=ddof, numeric_only=
        numeric_only)
    fqb__fhajr = dict(skipna=None, level=None, ddof=1, numeric_only=None)
    check_unsupported_args('DataFrame.std', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'std', axis=axis)


@overload_method(DataFrameType, 'median', inline='always', no_unliteral=True)
def overload_dataframe_median(df, axis=None, skipna=None, level=None,
    numeric_only=None):
    check_runtime_cols_unsupported(df, 'DataFrame.median()')
    efm__ifn = dict(skipna=skipna, level=level, numeric_only=numeric_only)
    fqb__fhajr = dict(skipna=None, level=None, numeric_only=None)
    check_unsupported_args('DataFrame.median', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'median', axis=axis)


@overload_method(DataFrameType, 'quantile', inline='always', no_unliteral=True)
def overload_dataframe_quantile(df, q=0.5, axis=0, numeric_only=True,
    interpolation='linear'):
    check_runtime_cols_unsupported(df, 'DataFrame.quantile()')
    efm__ifn = dict(numeric_only=numeric_only, interpolation=interpolation)
    fqb__fhajr = dict(numeric_only=True, interpolation='linear')
    check_unsupported_args('DataFrame.quantile', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    return _gen_reduce_impl(df, 'quantile', 'q', axis=axis)


@overload_method(DataFrameType, 'idxmax', inline='always', no_unliteral=True)
def overload_dataframe_idxmax(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmax()')
    efm__ifn = dict(axis=axis, skipna=skipna)
    fqb__fhajr = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmax', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    for omvqs__nmbhn in df.data:
        if not (bodo.utils.utils.is_np_array_typ(omvqs__nmbhn) and (
            omvqs__nmbhn.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(omvqs__nmbhn.dtype, (types.Number, types.Boolean))) or
            isinstance(omvqs__nmbhn, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or omvqs__nmbhn in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmax() only supported for numeric column types. Column type: {omvqs__nmbhn} not supported.'
                )
        if isinstance(omvqs__nmbhn, bodo.CategoricalArrayType
            ) and not omvqs__nmbhn.dtype.ordered:
            raise BodoError(
                'DataFrame.idxmax(): categorical columns must be ordered')
    return _gen_reduce_impl(df, 'idxmax', axis=axis)


@overload_method(DataFrameType, 'idxmin', inline='always', no_unliteral=True)
def overload_dataframe_idxmin(df, axis=0, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.idxmin()')
    efm__ifn = dict(axis=axis, skipna=skipna)
    fqb__fhajr = dict(axis=0, skipna=True)
    check_unsupported_args('DataFrame.idxmin', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    for omvqs__nmbhn in df.data:
        if not (bodo.utils.utils.is_np_array_typ(omvqs__nmbhn) and (
            omvqs__nmbhn.dtype in [bodo.datetime64ns, bodo.timedelta64ns] or
            isinstance(omvqs__nmbhn.dtype, (types.Number, types.Boolean))) or
            isinstance(omvqs__nmbhn, (bodo.IntegerArrayType, bodo.
            CategoricalArrayType)) or omvqs__nmbhn in [bodo.boolean_array,
            bodo.datetime_date_array_type]):
            raise BodoError(
                f'DataFrame.idxmin() only supported for numeric column types. Column type: {omvqs__nmbhn} not supported.'
                )
        if isinstance(omvqs__nmbhn, bodo.CategoricalArrayType
            ) and not omvqs__nmbhn.dtype.ordered:
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
        mqof__ykrg = tuple(iaj__iwe for iaj__iwe, tgxg__bci in zip(df.
            columns, df.data) if bodo.utils.typing._is_pandas_numeric_dtype
            (tgxg__bci.dtype))
        out_colnames = mqof__ykrg
    assert len(out_colnames) != 0
    try:
        if func_name in ('idxmax', 'idxmin') and axis == 0:
            comm_dtype = None
        else:
            jwe__ifaq = [numba.np.numpy_support.as_dtype(df.data[df.columns
                .index(iaj__iwe)].dtype) for iaj__iwe in out_colnames]
            comm_dtype = numba.np.numpy_support.from_dtype(np.
                find_common_type(jwe__ifaq, []))
    except NotImplementedError as hnsmj__dxsz:
        raise BodoError(
            f'Dataframe.{func_name}() with column types: {df.data} could not be merged to a common type.'
            )
    vlhn__tnkw = ''
    if func_name in ('sum', 'prod'):
        vlhn__tnkw = ', min_count=0'
    ddof = ''
    if func_name in ('var', 'std'):
        ddof = 'ddof=1, '
    cwba__ghvsz = (
        'def impl(df, axis=None, skipna=None, level=None,{} numeric_only=None{}):\n'
        .format(ddof, vlhn__tnkw))
    if func_name == 'quantile':
        cwba__ghvsz = (
            "def impl(df, q=0.5, axis=0, numeric_only=True, interpolation='linear'):\n"
            )
    if func_name in ('idxmax', 'idxmin'):
        cwba__ghvsz = 'def impl(df, axis=0, skipna=True):\n'
    if axis == 0:
        cwba__ghvsz += _gen_reduce_impl_axis0(df, func_name, out_colnames,
            comm_dtype, args)
    else:
        cwba__ghvsz += _gen_reduce_impl_axis1(func_name, out_colnames,
            comm_dtype, df)
    bxpjm__vul = {}
    exec(cwba__ghvsz, {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba},
        bxpjm__vul)
    impl = bxpjm__vul['impl']
    return impl


def _gen_reduce_impl_axis0(df, func_name, out_colnames, comm_dtype, args):
    uoxx__cjhwh = ''
    if func_name in ('min', 'max'):
        uoxx__cjhwh = ', dtype=np.{}'.format(comm_dtype)
    if comm_dtype == types.float32 and func_name in ('sum', 'prod', 'mean',
        'var', 'std', 'median'):
        uoxx__cjhwh = ', dtype=np.float32'
    lhqdo__cbfrr = f'bodo.libs.array_ops.array_op_{func_name}'
    txn__mofsz = ''
    if func_name in ['sum', 'prod']:
        txn__mofsz = 'True, min_count'
    elif func_name in ['idxmax', 'idxmin']:
        txn__mofsz = 'index'
    elif func_name == 'quantile':
        txn__mofsz = 'q'
    elif func_name in ['std', 'var']:
        txn__mofsz = 'True, ddof'
    elif func_name == 'median':
        txn__mofsz = 'True'
    data_args = ', '.join(
        f'{lhqdo__cbfrr}(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {df.columns.index(iaj__iwe)}), {txn__mofsz})'
         for iaj__iwe in out_colnames)
    cwba__ghvsz = ''
    if func_name in ('idxmax', 'idxmin'):
        cwba__ghvsz += (
            '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        cwba__ghvsz += (
            '  data = bodo.utils.conversion.coerce_to_array(({},))\n'.
            format(data_args))
    else:
        cwba__ghvsz += '  data = np.asarray(({},){})\n'.format(data_args,
            uoxx__cjhwh)
    cwba__ghvsz += f"""  return bodo.hiframes.pd_series_ext.init_series(data, pd.Index({out_colnames}))
"""
    return cwba__ghvsz


def _gen_reduce_impl_axis1(func_name, out_colnames, comm_dtype, df_type):
    tev__eyejn = [df_type.columns.index(iaj__iwe) for iaj__iwe in out_colnames]
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    data_args = '\n    '.join(
        'arr_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
        .format(i) for i in tev__eyejn)
    ytnc__mluj = '\n        '.join(f'row[{i}] = arr_{tev__eyejn[i]}[i]' for
        i in range(len(out_colnames)))
    assert len(data_args) > 0, f'empty dataframe in DataFrame.{func_name}()'
    uzsh__fvd = f'len(arr_{tev__eyejn[0]})'
    rbfnj__ujbhv = {'max': 'np.nanmax', 'min': 'np.nanmin', 'sum':
        'np.nansum', 'prod': 'np.nanprod', 'mean': 'np.nanmean', 'median':
        'np.nanmedian', 'var': 'bodo.utils.utils.nanvar_ddof1', 'std':
        'bodo.utils.utils.nanstd_ddof1'}
    if func_name in rbfnj__ujbhv:
        xjxa__amrm = rbfnj__ujbhv[func_name]
        hhj__hpf = 'float64' if func_name in ['mean', 'median', 'std', 'var'
            ] else comm_dtype
        cwba__ghvsz = f"""
    {data_args}
    numba.parfors.parfor.init_prange()
    n = {uzsh__fvd}
    row = np.empty({len(out_colnames)}, np.{comm_dtype})
    A = np.empty(n, np.{hhj__hpf})
    for i in numba.parfors.parfor.internal_prange(n):
        {ytnc__mluj}
        A[i] = {xjxa__amrm}(row)
    return bodo.hiframes.pd_series_ext.init_series(A, {index})
"""
        return cwba__ghvsz
    else:
        raise BodoError(f'DataFrame.{func_name}(): Not supported for axis=1')


@overload_method(DataFrameType, 'pct_change', inline='always', no_unliteral
    =True)
def overload_dataframe_pct_change(df, periods=1, fill_method='pad', limit=
    None, freq=None):
    check_runtime_cols_unsupported(df, 'DataFrame.pct_change()')
    efm__ifn = dict(fill_method=fill_method, limit=limit, freq=freq)
    fqb__fhajr = dict(fill_method='pad', limit=None, freq=None)
    check_unsupported_args('DataFrame.pct_change', efm__ifn, fqb__fhajr,
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
    efm__ifn = dict(axis=axis, skipna=skipna)
    fqb__fhajr = dict(axis=None, skipna=True)
    check_unsupported_args('DataFrame.cumprod', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).cumprod()'
         for i in range(len(df.columns)))
    header = 'def impl(df, axis=None, skipna=True):\n'
    return _gen_init_df(header, df.columns, data_args)


@overload_method(DataFrameType, 'cumsum', inline='always', no_unliteral=True)
def overload_dataframe_cumsum(df, axis=None, skipna=True):
    check_runtime_cols_unsupported(df, 'DataFrame.cumsum()')
    efm__ifn = dict(skipna=skipna)
    fqb__fhajr = dict(skipna=True)
    check_unsupported_args('DataFrame.cumsum', efm__ifn, fqb__fhajr,
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
    efm__ifn = dict(percentiles=percentiles, include=include, exclude=
        exclude, datetime_is_numeric=datetime_is_numeric)
    fqb__fhajr = dict(percentiles=None, include=None, exclude=None,
        datetime_is_numeric=True)
    check_unsupported_args('DataFrame.describe', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    mqof__ykrg = [iaj__iwe for iaj__iwe, tgxg__bci in zip(df.columns, df.
        data) if _is_describe_type(tgxg__bci)]
    if len(mqof__ykrg) == 0:
        raise BodoError('df.describe() only supports numeric columns')
    oih__uvl = sum(df.data[df.columns.index(iaj__iwe)].dtype == bodo.
        datetime64ns for iaj__iwe in mqof__ykrg)

    def _get_describe(col_ind):
        gqvzp__njq = df.data[col_ind].dtype == bodo.datetime64ns
        if oih__uvl and oih__uvl != len(mqof__ykrg):
            if gqvzp__njq:
                return f'des_{col_ind} + (np.nan,)'
            return (
                f'des_{col_ind}[:2] + des_{col_ind}[3:] + (des_{col_ind}[2],)')
        return f'des_{col_ind}'
    header = """def impl(df, percentiles=None, include=None, exclude=None, datetime_is_numeric=True):
"""
    for iaj__iwe in mqof__ykrg:
        col_ind = df.columns.index(iaj__iwe)
        header += f"""  des_{col_ind} = bodo.libs.array_ops.array_op_describe(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {col_ind}))
"""
    data_args = ', '.join(_get_describe(df.columns.index(iaj__iwe)) for
        iaj__iwe in mqof__ykrg)
    mfds__invn = "['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']"
    if oih__uvl == len(mqof__ykrg):
        mfds__invn = "['count', 'mean', 'min', '25%', '50%', '75%', 'max']"
    elif oih__uvl:
        mfds__invn = (
            "['count', 'mean', 'min', '25%', '50%', '75%', 'max', 'std']")
    index = f'bodo.utils.conversion.convert_to_index({mfds__invn})'
    return _gen_init_df(header, mqof__ykrg, data_args, index)


@overload_method(DataFrameType, 'take', inline='always', no_unliteral=True)
def overload_dataframe_take(df, indices, axis=0, convert=None, is_copy=True):
    check_runtime_cols_unsupported(df, 'DataFrame.take()')
    efm__ifn = dict(axis=axis, convert=convert, is_copy=is_copy)
    fqb__fhajr = dict(axis=0, convert=None, is_copy=True)
    check_unsupported_args('DataFrame.take', efm__ifn, fqb__fhajr,
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
    efm__ifn = dict(freq=freq, axis=axis, fill_value=fill_value)
    fqb__fhajr = dict(freq=None, axis=0, fill_value=None)
    check_unsupported_args('DataFrame.shift', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    for fuhp__gufq in df.data:
        if not is_supported_shift_array_type(fuhp__gufq):
            raise BodoError(
                f'Dataframe.shift() column input type {fuhp__gufq.dtype} not supported yet.'
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
    efm__ifn = dict(axis=axis)
    fqb__fhajr = dict(axis=0)
    check_unsupported_args('DataFrame.diff', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    for fuhp__gufq in df.data:
        if not (isinstance(fuhp__gufq, types.Array) and (isinstance(
            fuhp__gufq.dtype, types.Number) or fuhp__gufq.dtype == bodo.
            datetime64ns)):
            raise BodoError(
                f'DataFrame.diff() column input type {fuhp__gufq.dtype} not supported.'
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
    tgr__jwr = (
        "DataFrame.explode(): 'column' must a constant label or list of labels"
        )
    if not is_literal_type(column):
        raise_bodo_error(tgr__jwr)
    if is_overload_constant_list(column) or is_overload_constant_tuple(column):
        dfrtp__wndc = get_overload_const_list(column)
    else:
        dfrtp__wndc = [get_literal_value(column)]
    dae__lcese = {iaj__iwe: i for i, iaj__iwe in enumerate(df.columns)}
    oasvs__vodl = [dae__lcese[iaj__iwe] for iaj__iwe in dfrtp__wndc]
    for i in oasvs__vodl:
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
        f'  counts = bodo.libs.array_kernels.get_arr_lens(data{oasvs__vodl[0]})\n'
        )
    for i in range(n):
        if i in oasvs__vodl:
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
    qvw__nqaud = {'inplace': inplace, 'append': append, 'verify_integrity':
        verify_integrity}
    xwxv__qye = {'inplace': False, 'append': False, 'verify_integrity': False}
    check_unsupported_args('DataFrame.set_index', qvw__nqaud, xwxv__qye,
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
    columns = tuple(iaj__iwe for iaj__iwe in df.columns if iaj__iwe != col_name
        )
    index = (
        'bodo.utils.conversion.index_from_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}), {})'
        .format(col_ind, f"'{col_name}'" if isinstance(col_name, str) else
        col_name))
    return _gen_init_df(header, columns, data_args, index)


@overload_method(DataFrameType, 'query', no_unliteral=True)
def overload_dataframe_query(df, expr, inplace=False):
    check_runtime_cols_unsupported(df, 'DataFrame.query()')
    qvw__nqaud = {'inplace': inplace}
    xwxv__qye = {'inplace': False}
    check_unsupported_args('query', qvw__nqaud, xwxv__qye, package_name=
        'pandas', module_name='DataFrame')
    if not isinstance(expr, (types.StringLiteral, types.UnicodeType)):
        raise BodoError('query(): expr argument should be a string')

    def impl(df, expr, inplace=False):
        dehel__kzvd = bodo.hiframes.pd_dataframe_ext.query_dummy(df, expr)
        return df[dehel__kzvd]
    return impl


@overload_method(DataFrameType, 'duplicated', inline='always', no_unliteral
    =True)
def overload_dataframe_duplicated(df, subset=None, keep='first'):
    check_runtime_cols_unsupported(df, 'DataFrame.duplicated()')
    qvw__nqaud = {'subset': subset, 'keep': keep}
    xwxv__qye = {'subset': None, 'keep': 'first'}
    check_unsupported_args('DataFrame.duplicated', qvw__nqaud, xwxv__qye,
        package_name='pandas', module_name='DataFrame')
    fvh__iowla = len(df.columns)
    cwba__ghvsz = "def impl(df, subset=None, keep='first'):\n"
    for i in range(fvh__iowla):
        cwba__ghvsz += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    cwba__ghvsz += (
        '  duplicated = bodo.libs.array_kernels.duplicated(({},))\n'.format
        (', '.join('data_{}'.format(i) for i in range(fvh__iowla))))
    cwba__ghvsz += (
        '  index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n')
    cwba__ghvsz += (
        '  return bodo.hiframes.pd_series_ext.init_series(duplicated, index)\n'
        )
    bxpjm__vul = {}
    exec(cwba__ghvsz, {'bodo': bodo}, bxpjm__vul)
    impl = bxpjm__vul['impl']
    return impl


@overload_method(DataFrameType, 'drop_duplicates', inline='always',
    no_unliteral=True)
def overload_dataframe_drop_duplicates(df, subset=None, keep='first',
    inplace=False, ignore_index=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop_duplicates()')
    qvw__nqaud = {'keep': keep, 'inplace': inplace, 'ignore_index':
        ignore_index}
    xwxv__qye = {'keep': 'first', 'inplace': False, 'ignore_index': False}
    tqgex__hfgdh = []
    if is_overload_constant_list(subset):
        tqgex__hfgdh = get_overload_const_list(subset)
    elif is_overload_constant_str(subset):
        tqgex__hfgdh = [get_overload_const_str(subset)]
    elif is_overload_constant_int(subset):
        tqgex__hfgdh = [get_overload_const_int(subset)]
    elif not is_overload_none(subset):
        raise_bodo_error(
            'DataFrame.drop_duplicates(): subset must be a constant column name, constant list of column names or None'
            )
    frwx__fvgn = []
    for col_name in tqgex__hfgdh:
        if col_name not in df.columns:
            raise BodoError(
                'DataFrame.drop_duplicates(): All subset columns must be found in the DataFrame.'
                 +
                f'Column {col_name} not found in DataFrame columns {df.columns}'
                )
        frwx__fvgn.append(df.columns.index(col_name))
    check_unsupported_args('DataFrame.drop_duplicates', qvw__nqaud,
        xwxv__qye, package_name='pandas', module_name='DataFrame')
    pfj__rbq = []
    if frwx__fvgn:
        for xmh__viipm in frwx__fvgn:
            if isinstance(df.data[xmh__viipm], bodo.MapArrayType):
                pfj__rbq.append(df.columns[xmh__viipm])
    else:
        for i, col_name in enumerate(df.columns):
            if isinstance(df.data[i], bodo.MapArrayType):
                pfj__rbq.append(col_name)
    if pfj__rbq:
        raise BodoError(f'DataFrame.drop_duplicates(): Columns {pfj__rbq} ' +
            f'have dictionary types which cannot be used to drop duplicates. '
             +
            "Please consider using the 'subset' argument to skip these columns."
            )
    fvh__iowla = len(df.columns)
    zvass__aam = ['data_{}'.format(i) for i in frwx__fvgn]
    kim__mhw = ['data_{}'.format(i) for i in range(fvh__iowla) if i not in
        frwx__fvgn]
    if zvass__aam:
        qmmz__ptxu = len(zvass__aam)
    else:
        qmmz__ptxu = fvh__iowla
    ofy__qghm = ', '.join(zvass__aam + kim__mhw)
    data_args = ', '.join('data_{}'.format(i) for i in range(fvh__iowla))
    cwba__ghvsz = (
        "def impl(df, subset=None, keep='first', inplace=False, ignore_index=False):\n"
        )
    for i in range(fvh__iowla):
        cwba__ghvsz += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    cwba__ghvsz += (
        """  ({0},), index_arr = bodo.libs.array_kernels.drop_duplicates(({0},), {1}, {2})
"""
        .format(ofy__qghm, index, qmmz__ptxu))
    cwba__ghvsz += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(cwba__ghvsz, df.columns, data_args, 'index')


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
                oee__ftok = {iaj__iwe: i for i, iaj__iwe in enumerate(cond.
                    columns)}

                def cond_str(i, gen_all_false):
                    if df.columns[i] in oee__ftok:
                        return (
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(cond, {oee__ftok[df.columns[i]]})'
                            )
                    else:
                        gen_all_false[0] = True
                        return 'all_false'
            elif isinstance(cond, types.Array):
                cond_str = lambda i, _: f'cond[:,{i}]'
        if not hasattr(other, 'ndim') or other.ndim == 1:
            rzet__wwws = lambda i: 'other'
        elif other.ndim == 2:
            if isinstance(other, DataFrameType):
                other_map = {iaj__iwe: i for i, iaj__iwe in enumerate(other
                    .columns)}
                rzet__wwws = (lambda i: 
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(other, {other_map[df.columns[i]]})'
                     if df.columns[i] in other_map else 'None')
            elif isinstance(other, types.Array):
                rzet__wwws = lambda i: f'other[:,{i}]'
        fvh__iowla = len(df.columns)
        data_args = ', '.join(
            f'bodo.hiframes.series_impl.where_impl({cond_str(i, gen_all_false)}, bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}), {rzet__wwws(i)})'
             for i in range(fvh__iowla))
        if gen_all_false[0]:
            header += '  all_false = np.zeros(len(df), dtype=bool)\n'
        return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_mask_where


def _install_dataframe_mask_where_overload():
    for func_name in ('mask', 'where'):
        xzhro__pon = create_dataframe_mask_where_overload(func_name)
        overload_method(DataFrameType, func_name, no_unliteral=True)(xzhro__pon
            )


_install_dataframe_mask_where_overload()


def _validate_arguments_mask_where(func_name, df, cond, other, inplace,
    axis, level, errors, try_cast):
    efm__ifn = dict(inplace=inplace, level=level, errors=errors, try_cast=
        try_cast)
    fqb__fhajr = dict(inplace=False, level=None, errors='raise', try_cast=False
        )
    check_unsupported_args(f'{func_name}', efm__ifn, fqb__fhajr,
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
    fvh__iowla = len(df.columns)
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
        other_map = {iaj__iwe: i for i, iaj__iwe in enumerate(other.columns)}
        for i in range(fvh__iowla):
            if df.columns[i] in other_map:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, df.data[i], other.data[other_map[df.columns[i]]]
                    )
            else:
                bodo.hiframes.series_impl._validate_self_other_mask_where(
                    func_name, df.data[i], None, is_default=True)
    elif isinstance(other, SeriesType):
        for i in range(fvh__iowla):
            bodo.hiframes.series_impl._validate_self_other_mask_where(func_name
                , df.data[i], other.data)
    else:
        for i in range(fvh__iowla):
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
        uih__sqequ = 'out_df_type'
    else:
        uih__sqequ = gen_const_tup(columns)
    data_args = '({}{})'.format(data_args, ',' if data_args else '')
    cwba__ghvsz = f"""{header}  return bodo.hiframes.pd_dataframe_ext.init_dataframe({data_args}, {index}, {uih__sqequ})
"""
    bxpjm__vul = {}
    vni__ehao = {'bodo': bodo, 'np': np, 'pd': pd, 'numba': numba}
    vni__ehao.update(extra_globals)
    exec(cwba__ghvsz, vni__ehao, bxpjm__vul)
    impl = bxpjm__vul['impl']
    return impl


def _get_binop_columns(lhs, rhs, is_inplace=False):
    if lhs.columns != rhs.columns:
        wavq__stum = pd.Index(lhs.columns)
        zfac__qkarb = pd.Index(rhs.columns)
        svx__qiam, bil__erh, wzyt__hliqz = wavq__stum.join(zfac__qkarb, how
            ='left' if is_inplace else 'outer', level=None, return_indexers
            =True)
        return tuple(svx__qiam), bil__erh, wzyt__hliqz
    return lhs.columns, range(len(lhs.columns)), range(len(lhs.columns))


def create_binary_op_overload(op):

    def overload_dataframe_binary_op(lhs, rhs):
        gbza__ukkpj = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        iqey__mzs = operator.eq, operator.ne
        check_runtime_cols_unsupported(lhs, gbza__ukkpj)
        check_runtime_cols_unsupported(rhs, gbza__ukkpj)
        if isinstance(lhs, DataFrameType):
            if isinstance(rhs, DataFrameType):
                svx__qiam, bil__erh, wzyt__hliqz = _get_binop_columns(lhs, rhs)
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {odag__fvk}) {gbza__ukkpj}bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {jwj__efotg})'
                     if odag__fvk != -1 and jwj__efotg != -1 else
                    f'bodo.libs.array_kernels.gen_na_array(len(lhs), float64_arr_type)'
                     for odag__fvk, jwj__efotg in zip(bil__erh, wzyt__hliqz))
                header = 'def impl(lhs, rhs):\n'
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)')
                return _gen_init_df(header, svx__qiam, data_args, index,
                    extra_globals={'float64_arr_type': types.Array(types.
                    float64, 1, 'C')})
            vavfy__gfyj = []
            pfw__bqi = []
            if op in iqey__mzs:
                for i, vtaa__gki in enumerate(lhs.data):
                    if is_common_scalar_dtype([vtaa__gki.dtype, rhs]):
                        vavfy__gfyj.append(
                            f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {gbza__ukkpj} rhs'
                            )
                    else:
                        pmwyr__apnok = f'arr{i}'
                        pfw__bqi.append(pmwyr__apnok)
                        vavfy__gfyj.append(pmwyr__apnok)
                data_args = ', '.join(vavfy__gfyj)
            else:
                data_args = ', '.join(
                    f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(lhs, {i}) {gbza__ukkpj} rhs'
                     for i in range(len(lhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(pfw__bqi) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(lhs)\n'
                header += ''.join(
                    f'  {pmwyr__apnok} = np.empty(n, dtype=np.bool_)\n' for
                    pmwyr__apnok in pfw__bqi)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(pmwyr__apnok,
                    op == operator.ne) for pmwyr__apnok in pfw__bqi)
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(lhs)'
            return _gen_init_df(header, lhs.columns, data_args, index)
        if isinstance(rhs, DataFrameType):
            vavfy__gfyj = []
            pfw__bqi = []
            if op in iqey__mzs:
                for i, vtaa__gki in enumerate(rhs.data):
                    if is_common_scalar_dtype([lhs, vtaa__gki.dtype]):
                        vavfy__gfyj.append(
                            f'lhs {gbza__ukkpj} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {i})'
                            )
                    else:
                        pmwyr__apnok = f'arr{i}'
                        pfw__bqi.append(pmwyr__apnok)
                        vavfy__gfyj.append(pmwyr__apnok)
                data_args = ', '.join(vavfy__gfyj)
            else:
                data_args = ', '.join(
                    'lhs {1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(rhs, {0})'
                    .format(i, gbza__ukkpj) for i in range(len(rhs.columns)))
            header = 'def impl(lhs, rhs):\n'
            if len(pfw__bqi) > 0:
                header += '  numba.parfors.parfor.init_prange()\n'
                header += '  n = len(rhs)\n'
                header += ''.join('  {0} = np.empty(n, dtype=np.bool_)\n'.
                    format(pmwyr__apnok) for pmwyr__apnok in pfw__bqi)
                header += (
                    '  for i in numba.parfors.parfor.internal_prange(n):\n')
                header += ''.join('    {0}[i] = {1}\n'.format(pmwyr__apnok,
                    op == operator.ne) for pmwyr__apnok in pfw__bqi)
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
        xzhro__pon = create_binary_op_overload(op)
        overload(op)(xzhro__pon)


_install_binary_ops()


def create_inplace_binary_op_overload(op):

    def overload_dataframe_inplace_binary_op(left, right):
        gbza__ukkpj = numba.core.utils.OPERATORS_TO_BUILTINS[op]
        check_runtime_cols_unsupported(left, gbza__ukkpj)
        check_runtime_cols_unsupported(right, gbza__ukkpj)
        if isinstance(left, DataFrameType):
            if isinstance(right, DataFrameType):
                svx__qiam, _, wzyt__hliqz = _get_binop_columns(left, right,
                    True)
                cwba__ghvsz = 'def impl(left, right):\n'
                for i, jwj__efotg in enumerate(wzyt__hliqz):
                    if jwj__efotg == -1:
                        cwba__ghvsz += f"""  df_arr{i} = bodo.libs.array_kernels.gen_na_array(len(left), float64_arr_type)
"""
                        continue
                    cwba__ghvsz += f"""  df_arr{i} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {i})
"""
                    cwba__ghvsz += f"""  df_arr{i} {gbza__ukkpj} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(right, {jwj__efotg})
"""
                data_args = ', '.join(f'df_arr{i}' for i in range(len(
                    svx__qiam)))
                index = (
                    'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)')
                return _gen_init_df(cwba__ghvsz, svx__qiam, data_args,
                    index, extra_globals={'float64_arr_type': types.Array(
                    types.float64, 1, 'C')})
            cwba__ghvsz = 'def impl(left, right):\n'
            for i in range(len(left.columns)):
                cwba__ghvsz += (
                    """  df_arr{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(left, {0})
"""
                    .format(i))
                cwba__ghvsz += '  df_arr{0} {1} right\n'.format(i, gbza__ukkpj)
            data_args = ', '.join('df_arr{}'.format(i) for i in range(len(
                left.columns)))
            index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(left)'
            return _gen_init_df(cwba__ghvsz, left.columns, data_args, index)
    return overload_dataframe_inplace_binary_op


def _install_inplace_binary_ops():
    for op in bodo.hiframes.pd_series_ext.series_inplace_binary_ops:
        xzhro__pon = create_inplace_binary_op_overload(op)
        overload(op, no_unliteral=True)(xzhro__pon)


_install_inplace_binary_ops()


def create_unary_op_overload(op):

    def overload_dataframe_unary_op(df):
        if isinstance(df, DataFrameType):
            gbza__ukkpj = numba.core.utils.OPERATORS_TO_BUILTINS[op]
            check_runtime_cols_unsupported(df, gbza__ukkpj)
            data_args = ', '.join(
                '{1} bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})'
                .format(i, gbza__ukkpj) for i in range(len(df.columns)))
            header = 'def impl(df):\n'
            return _gen_init_df(header, df.columns, data_args)
    return overload_dataframe_unary_op


def _install_unary_ops():
    for op in bodo.hiframes.pd_series_ext.series_unary_ops:
        xzhro__pon = create_unary_op_overload(op)
        overload(op, no_unliteral=True)(xzhro__pon)


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
            lchu__bkvp = np.empty(n, np.bool_)
            for i in numba.parfors.parfor.internal_prange(n):
                lchu__bkvp[i] = bodo.libs.array_kernels.isna(obj, i)
            return lchu__bkvp
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
            lchu__bkvp = np.empty(n, np.bool_)
            for i in range(n):
                lchu__bkvp[i] = pd.isna(obj[i])
            return lchu__bkvp
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
    qvw__nqaud = {'inplace': inplace, 'limit': limit, 'regex': regex,
        'method': method}
    xwxv__qye = {'inplace': False, 'limit': None, 'regex': False, 'method':
        'pad'}
    check_unsupported_args('replace', qvw__nqaud, xwxv__qye, package_name=
        'pandas', module_name='DataFrame')
    data_args = ', '.join(
        f'df.iloc[:, {i}].replace(to_replace, value).values' for i in range
        (len(df.columns)))
    header = """def impl(df, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad'):
"""
    return _gen_init_df(header, df.columns, data_args)


def _is_col_access(expr_node):
    btmhy__sryae = str(expr_node)
    return btmhy__sryae.startswith('left.') or btmhy__sryae.startswith('right.'
        )


def _insert_NA_cond(expr_node, left_columns, left_data, right_columns,
    right_data):
    vwx__rys = {'left': 0, 'right': 0, 'NOT_NA': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (vwx__rys,))
    vrxf__tjg = pd.core.computation.parsing.clean_column_name

    def append_null_checks(expr_node, null_set):
        if not null_set:
            return expr_node
        nftq__mmyz = ' & '.join([('NOT_NA.`' + x + '`') for x in null_set])
        ftcxo__vudir = {('NOT_NA', vrxf__tjg(vtaa__gki)): vtaa__gki for
            vtaa__gki in null_set}
        ktoem__tje, _, _ = _parse_query_expr(nftq__mmyz, env, [], [], None,
            join_cleaned_cols=ftcxo__vudir)
        vpu__uqinb = (pd.core.computation.ops.BinOp.
            _disallow_scalar_only_bool_ops)
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (lambda
            self: None)
        try:
            slqnj__lknc = pd.core.computation.ops.BinOp('&', ktoem__tje,
                expr_node)
        finally:
            (pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
                ) = vpu__uqinb
        return slqnj__lknc

    def _insert_NA_cond_body(expr_node, null_set):
        if isinstance(expr_node, pd.core.computation.ops.BinOp):
            if expr_node.op == '|':
                einao__qta = set()
                yhwr__dro = set()
                tgo__klkk = _insert_NA_cond_body(expr_node.lhs, einao__qta)
                kaosd__mbh = _insert_NA_cond_body(expr_node.rhs, yhwr__dro)
                hlmwq__abi = einao__qta.intersection(yhwr__dro)
                einao__qta.difference_update(hlmwq__abi)
                yhwr__dro.difference_update(hlmwq__abi)
                null_set.update(hlmwq__abi)
                expr_node.lhs = append_null_checks(tgo__klkk, einao__qta)
                expr_node.rhs = append_null_checks(kaosd__mbh, yhwr__dro)
                expr_node.operands = expr_node.lhs, expr_node.rhs
            else:
                expr_node.lhs = _insert_NA_cond_body(expr_node.lhs, null_set)
                expr_node.rhs = _insert_NA_cond_body(expr_node.rhs, null_set)
        elif _is_col_access(expr_node):
            rfan__eyk = expr_node.name
            fryk__zex, col_name = rfan__eyk.split('.')
            if fryk__zex == 'left':
                uhm__juwt = left_columns
                data = left_data
            else:
                uhm__juwt = right_columns
                data = right_data
            sfy__nad = data[uhm__juwt.index(col_name)]
            if bodo.utils.typing.is_nullable(sfy__nad):
                null_set.add(expr_node.name)
        return expr_node
    null_set = set()
    jsjxz__cvdc = _insert_NA_cond_body(expr_node, null_set)
    return append_null_checks(expr_node, null_set)


def _extract_equal_conds(expr_node):
    if not hasattr(expr_node, 'op'):
        return [], [], expr_node
    if expr_node.op == '==' and _is_col_access(expr_node.lhs
        ) and _is_col_access(expr_node.rhs):
        ngopd__iaky = str(expr_node.lhs)
        jhny__jthh = str(expr_node.rhs)
        if ngopd__iaky.startswith('left.') and jhny__jthh.startswith('left.'
            ) or ngopd__iaky.startswith('right.') and jhny__jthh.startswith(
            'right.'):
            return [], [], expr_node
        left_on = [ngopd__iaky.split('.')[1]]
        right_on = [jhny__jthh.split('.')[1]]
        if ngopd__iaky.startswith('right.'):
            return right_on, left_on, None
        return left_on, right_on, None
    if expr_node.op == '&':
        azp__tvmh, besp__chyq, dgcnk__gcq = _extract_equal_conds(expr_node.lhs)
        anqne__mzt, sohl__mixcv, idms__hoot = _extract_equal_conds(expr_node
            .rhs)
        left_on = azp__tvmh + anqne__mzt
        right_on = besp__chyq + sohl__mixcv
        if dgcnk__gcq is None:
            return left_on, right_on, idms__hoot
        if idms__hoot is None:
            return left_on, right_on, dgcnk__gcq
        expr_node.lhs = dgcnk__gcq
        expr_node.rhs = idms__hoot
        expr_node.operands = expr_node.lhs, expr_node.rhs
        return left_on, right_on, expr_node
    return [], [], expr_node


def _parse_merge_cond(on_str, left_columns, left_data, right_columns,
    right_data):
    vwx__rys = {'left': 0, 'right': 0}
    env = pd.core.computation.scope.ensure_scope(2, {}, {}, (vwx__rys,))
    ysy__zhtgl = dict()
    vrxf__tjg = pd.core.computation.parsing.clean_column_name
    for name, wfyu__bmi in (('left', left_columns), ('right', right_columns)):
        for vtaa__gki in wfyu__bmi:
            jui__dwqum = vrxf__tjg(vtaa__gki)
            ishs__mswlg = name, jui__dwqum
            if ishs__mswlg in ysy__zhtgl:
                raise_bodo_error(
                    f"pd.merge(): {name} table contains two columns that are escaped to the same Python identifier '{vtaa__gki}' and '{ysy__zhtgl[jui__dwqum]}' Please rename one of these columns. To avoid this issue, please use names that are valid Python identifiers."
                    )
            ysy__zhtgl[ishs__mswlg] = vtaa__gki
    dsa__juoz, _, _ = _parse_query_expr(on_str, env, [], [], None,
        join_cleaned_cols=ysy__zhtgl)
    left_on, right_on, oactp__jwasn = _extract_equal_conds(dsa__juoz.terms)
    return left_on, right_on, _insert_NA_cond(oactp__jwasn, left_columns,
        left_data, right_columns, right_data)


@overload_method(DataFrameType, 'merge', inline='always', no_unliteral=True)
@overload(pd.merge, inline='always', no_unliteral=True)
def overload_dataframe_merge(left, right, how='inner', on=None, left_on=
    None, right_on=None, left_index=False, right_index=False, sort=False,
    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None,
    _bodo_na_equal=True):
    check_runtime_cols_unsupported(left, 'DataFrame.merge()')
    check_runtime_cols_unsupported(right, 'DataFrame.merge()')
    efm__ifn = dict(sort=sort, copy=copy, validate=validate)
    fqb__fhajr = dict(sort=False, copy=True, validate=None)
    check_unsupported_args('DataFrame.merge', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    validate_merge_spec(left, right, how, on, left_on, right_on, left_index,
        right_index, sort, suffixes, copy, indicator, validate)
    how = get_overload_const_str(how)
    chrht__ycgsk = tuple(sorted(set(left.columns) & set(right.columns), key
        =lambda k: str(k)))
    kmv__fbw = ''
    if not is_overload_none(on):
        left_on = right_on = on
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            if on_str not in chrht__ycgsk and ('left.' in on_str or 
                'right.' in on_str):
                left_on, right_on, qpny__lyhy = _parse_merge_cond(on_str,
                    left.columns, left.data, right.columns, right.data)
                if qpny__lyhy is None:
                    kmv__fbw = ''
                else:
                    kmv__fbw = str(qpny__lyhy)
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = chrht__ycgsk
        right_keys = chrht__ycgsk
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
    vdb__xnjsl = get_overload_const_bool(_bodo_na_equal)
    validate_keys_length(left_index, right_index, left_keys, right_keys)
    validate_keys_dtypes(left, right, left_index, right_index, left_keys,
        right_keys)
    if is_overload_constant_tuple(suffixes):
        ils__qbuss = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        ils__qbuss = list(get_overload_const_list(suffixes))
    suffix_x = ils__qbuss[0]
    suffix_y = ils__qbuss[1]
    validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
        right_keys, left.columns, right.columns, indicator_val)
    left_keys = gen_const_tup(left_keys)
    right_keys = gen_const_tup(right_keys)
    cwba__ghvsz = (
        "def _impl(left, right, how='inner', on=None, left_on=None,\n")
    cwba__ghvsz += (
        '    right_on=None, left_index=False, right_index=False, sort=False,\n'
        )
    cwba__ghvsz += """    suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, _bodo_na_equal=True):
"""
    cwba__ghvsz += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, '{}', '{}', '{}', False, {}, {}, '{}')
"""
        .format(left_keys, right_keys, how, suffix_x, suffix_y,
        indicator_val, vdb__xnjsl, kmv__fbw))
    bxpjm__vul = {}
    exec(cwba__ghvsz, {'bodo': bodo}, bxpjm__vul)
    _impl = bxpjm__vul['_impl']
    return _impl


def common_validate_merge_merge_asof_spec(name_func, left, right, on,
    left_on, right_on, left_index, right_index, suffixes):
    if not isinstance(left, DataFrameType) or not isinstance(right,
        DataFrameType):
        raise BodoError(name_func + '() requires dataframe inputs')
    valid_dataframe_column_types = (ArrayItemArrayType, MapArrayType,
        StructArrayType, CategoricalArrayType, types.Array,
        IntegerArrayType, DecimalArrayType, IntervalArrayType)
    hvip__qknb = {string_array_type, binary_array_type,
        datetime_date_array_type, datetime_timedelta_array_type, boolean_array}
    qbqjj__zyrls = {get_overload_const_str(otso__kou) for otso__kou in (
        left_on, right_on, on) if is_overload_constant_str(otso__kou)}
    for df in (left, right):
        for i, vtaa__gki in enumerate(df.data):
            if not isinstance(vtaa__gki, valid_dataframe_column_types
                ) and vtaa__gki not in hvip__qknb:
                raise BodoError(
                    f'{name_func}(): use of column with {type(vtaa__gki)} in merge unsupported'
                    )
            if df.columns[i] in qbqjj__zyrls and isinstance(vtaa__gki,
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
        ils__qbuss = get_overload_const_tuple(suffixes)
    if is_overload_constant_list(suffixes):
        ils__qbuss = list(get_overload_const_list(suffixes))
    if len(ils__qbuss) != 2:
        raise BodoError(name_func +
            '(): The number of suffixes should be exactly 2')
    chrht__ycgsk = tuple(set(left.columns) & set(right.columns))
    if not is_overload_none(on):
        fuvqj__xajl = False
        if is_overload_constant_str(on):
            on_str = get_overload_const_str(on)
            fuvqj__xajl = on_str not in chrht__ycgsk and ('left.' in on_str or
                'right.' in on_str)
        if len(chrht__ycgsk) == 0 and not fuvqj__xajl:
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
    tglb__yeu = numba.core.registry.cpu_target.typing_context
    if is_overload_true(left_index) or is_overload_true(right_index):
        if is_overload_true(left_index) and is_overload_true(right_index):
            jayg__ippq = left.index
            qegg__ocscn = isinstance(jayg__ippq, StringIndexType)
            tmoh__gsbe = right.index
            agqkr__zbvg = isinstance(tmoh__gsbe, StringIndexType)
        elif is_overload_true(left_index):
            jayg__ippq = left.index
            qegg__ocscn = isinstance(jayg__ippq, StringIndexType)
            tmoh__gsbe = right.data[right.columns.index(right_keys[0])]
            agqkr__zbvg = tmoh__gsbe.dtype == string_type
        elif is_overload_true(right_index):
            jayg__ippq = left.data[left.columns.index(left_keys[0])]
            qegg__ocscn = jayg__ippq.dtype == string_type
            tmoh__gsbe = right.index
            agqkr__zbvg = isinstance(tmoh__gsbe, StringIndexType)
        if qegg__ocscn and agqkr__zbvg:
            return
        jayg__ippq = jayg__ippq.dtype
        tmoh__gsbe = tmoh__gsbe.dtype
        try:
            tlvn__sayqu = tglb__yeu.resolve_function_type(operator.eq, (
                jayg__ippq, tmoh__gsbe), {})
        except:
            raise_bodo_error(
                'merge: You are trying to merge on {lk_dtype} and {rk_dtype} columns. If you wish to proceed you should use pd.concat'
                .format(lk_dtype=jayg__ippq, rk_dtype=tmoh__gsbe))
    else:
        for zyprg__xfx, iijpi__drtgt in zip(left_keys, right_keys):
            jayg__ippq = left.data[left.columns.index(zyprg__xfx)].dtype
            lzls__hokl = left.data[left.columns.index(zyprg__xfx)]
            tmoh__gsbe = right.data[right.columns.index(iijpi__drtgt)].dtype
            dvylj__xlvb = right.data[right.columns.index(iijpi__drtgt)]
            if lzls__hokl == dvylj__xlvb:
                continue
            asm__uumrg = (
                'merge: You are trying to merge on column {lk} of {lk_dtype} and column {rk} of {rk_dtype}. If you wish to proceed you should use pd.concat'
                .format(lk=zyprg__xfx, lk_dtype=jayg__ippq, rk=iijpi__drtgt,
                rk_dtype=tmoh__gsbe))
            zpn__lupob = jayg__ippq == string_type
            vepdb__pht = tmoh__gsbe == string_type
            if zpn__lupob ^ vepdb__pht:
                raise_bodo_error(asm__uumrg)
            try:
                tlvn__sayqu = tglb__yeu.resolve_function_type(operator.eq,
                    (jayg__ippq, tmoh__gsbe), {})
            except:
                raise_bodo_error(asm__uumrg)


def validate_keys(keys, df):
    lzlb__ccc = set(keys).difference(set(df.columns))
    if len(lzlb__ccc) > 0:
        if is_overload_constant_str(df.index.name_typ
            ) and get_overload_const_str(df.index.name_typ) in lzlb__ccc:
            raise_bodo_error(
                f'merge(): use of index {df.index.name_typ} as key for on/left_on/right_on is unsupported'
                )
        raise_bodo_error(
            f"""merge(): invalid key {lzlb__ccc} for on/left_on/right_on
merge supports only valid column names {df.columns}"""
            )


@overload_method(DataFrameType, 'join', inline='always', no_unliteral=True)
def overload_dataframe_join(left, other, on=None, how='left', lsuffix='',
    rsuffix='', sort=False):
    check_runtime_cols_unsupported(left, 'DataFrame.join()')
    check_runtime_cols_unsupported(other, 'DataFrame.join()')
    efm__ifn = dict(lsuffix=lsuffix, rsuffix=rsuffix)
    fqb__fhajr = dict(lsuffix='', rsuffix='')
    check_unsupported_args('DataFrame.join', efm__ifn, fqb__fhajr,
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
    cwba__ghvsz = "def _impl(left, other, on=None, how='left',\n"
    cwba__ghvsz += "    lsuffix='', rsuffix='', sort=False):\n"
    cwba__ghvsz += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, other, {}, {}, '{}', '{}', '{}', True, False, True, '')
"""
        .format(left_keys, right_keys, how, lsuffix, rsuffix))
    bxpjm__vul = {}
    exec(cwba__ghvsz, {'bodo': bodo}, bxpjm__vul)
    _impl = bxpjm__vul['_impl']
    return _impl


def validate_join_spec(left, other, on, how, lsuffix, rsuffix, sort):
    if not isinstance(other, DataFrameType):
        raise BodoError('join() requires dataframe inputs')
    ensure_constant_values('merge', 'how', how, ('left', 'right', 'outer',
        'inner'))
    if not is_overload_none(on) and len(get_overload_const_list(on)) != 1:
        raise BodoError('join(): len(on) must equals to 1 when specified.')
    if not is_overload_none(on):
        pqpq__bnovu = get_overload_const_list(on)
        validate_keys(pqpq__bnovu, left)
    if not is_overload_false(sort):
        raise BodoError(
            'join(): sort parameter only supports default value False')
    chrht__ycgsk = tuple(set(left.columns) & set(other.columns))
    if len(chrht__ycgsk) > 0:
        raise_bodo_error(
            'join(): not supporting joining on overlapping columns:{cols} Use DataFrame.merge() instead.'
            .format(cols=chrht__ycgsk))


def validate_unicity_output_column_names(suffix_x, suffix_y, left_keys,
    right_keys, left_columns, right_columns, indicator_val):
    dqmb__jio = set(left_keys) & set(right_keys)
    jyvlu__hiikj = set(left_columns) & set(right_columns)
    spr__giaiy = jyvlu__hiikj - dqmb__jio
    gsv__caxsb = set(left_columns) - jyvlu__hiikj
    sebtf__eil = set(right_columns) - jyvlu__hiikj
    yhv__vxm = {}

    def insertOutColumn(col_name):
        if col_name in yhv__vxm:
            raise_bodo_error(
                'join(): two columns happen to have the same name : {}'.
                format(col_name))
        yhv__vxm[col_name] = 0
    for gveob__nxppz in dqmb__jio:
        insertOutColumn(gveob__nxppz)
    for gveob__nxppz in spr__giaiy:
        dsvt__qkzj = str(gveob__nxppz) + suffix_x
        syt__aoumc = str(gveob__nxppz) + suffix_y
        insertOutColumn(dsvt__qkzj)
        insertOutColumn(syt__aoumc)
    for gveob__nxppz in gsv__caxsb:
        insertOutColumn(gveob__nxppz)
    for gveob__nxppz in sebtf__eil:
        insertOutColumn(gveob__nxppz)
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
    chrht__ycgsk = tuple(sorted(set(left.columns) & set(right.columns), key
        =lambda k: str(k)))
    if not is_overload_none(on):
        left_on = right_on = on
    if is_overload_none(on) and is_overload_none(left_on) and is_overload_none(
        right_on) and is_overload_false(left_index) and is_overload_false(
        right_index):
        left_keys = chrht__ycgsk
        right_keys = chrht__ycgsk
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
        ils__qbuss = suffixes
    if is_overload_constant_list(suffixes):
        ils__qbuss = list(get_overload_const_list(suffixes))
    if isinstance(suffixes, types.Omitted):
        ils__qbuss = suffixes.value
    suffix_x = ils__qbuss[0]
    suffix_y = ils__qbuss[1]
    cwba__ghvsz = (
        'def _impl(left, right, on=None, left_on=None, right_on=None,\n')
    cwba__ghvsz += (
        '    left_index=False, right_index=False, by=None, left_by=None,\n')
    cwba__ghvsz += (
        "    right_by=None, suffixes=('_x', '_y'), tolerance=None,\n")
    cwba__ghvsz += "    allow_exact_matches=True, direction='backward'):\n"
    cwba__ghvsz += '  suffix_x = suffixes[0]\n'
    cwba__ghvsz += '  suffix_y = suffixes[1]\n'
    cwba__ghvsz += (
        """  return bodo.hiframes.pd_dataframe_ext.join_dummy(left, right, {}, {}, 'asof', '{}', '{}', False, False, True, '')
"""
        .format(left_keys, right_keys, suffix_x, suffix_y))
    bxpjm__vul = {}
    exec(cwba__ghvsz, {'bodo': bodo}, bxpjm__vul)
    _impl = bxpjm__vul['_impl']
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
    efm__ifn = dict(sort=sort, group_keys=group_keys, squeeze=squeeze,
        observed=observed)
    xav__otmu = dict(sort=False, group_keys=True, squeeze=False, observed=True)
    check_unsupported_args('Dataframe.groupby', efm__ifn, xav__otmu,
        package_name='pandas', module_name='GroupBy')


def pivot_error_checking(df, index, columns, values, func_name):
    lnafc__sbo = func_name == 'DataFrame.pivot_table'
    if lnafc__sbo:
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
    ocjy__bpqu = get_literal_value(columns)
    if isinstance(ocjy__bpqu, (list, tuple)):
        if len(ocjy__bpqu) > 1:
            raise BodoError(
                f"{func_name}(): 'columns' argument must be a constant column label not a {ocjy__bpqu}"
                )
        ocjy__bpqu = ocjy__bpqu[0]
    if ocjy__bpqu not in df.columns:
        raise BodoError(
            f"{func_name}(): 'columns' column {ocjy__bpqu} not found in DataFrame {df}."
            )
    ulam__ygbnh = {iaj__iwe: i for i, iaj__iwe in enumerate(df.columns)}
    fceeb__rny = ulam__ygbnh[ocjy__bpqu]
    if is_overload_none(index):
        lhf__zgki = []
        rlsk__xjw = []
    else:
        rlsk__xjw = get_literal_value(index)
        if not isinstance(rlsk__xjw, (list, tuple)):
            rlsk__xjw = [rlsk__xjw]
        lhf__zgki = []
        for index in rlsk__xjw:
            if index not in ulam__ygbnh:
                raise BodoError(
                    f"{func_name}(): 'index' column {index} not found in DataFrame {df}."
                    )
            lhf__zgki.append(ulam__ygbnh[index])
    if not (all(isinstance(iaj__iwe, int) for iaj__iwe in rlsk__xjw) or all
        (isinstance(iaj__iwe, str) for iaj__iwe in rlsk__xjw)):
        raise BodoError(
            f"{func_name}(): column names selected for 'index' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    if is_overload_none(values):
        pbk__ovdf = []
        kztm__uzfh = []
        wexsw__ditu = lhf__zgki + [fceeb__rny]
        for i, iaj__iwe in enumerate(df.columns):
            if i not in wexsw__ditu:
                pbk__ovdf.append(i)
                kztm__uzfh.append(iaj__iwe)
    else:
        kztm__uzfh = get_literal_value(values)
        if not isinstance(kztm__uzfh, (list, tuple)):
            kztm__uzfh = [kztm__uzfh]
        pbk__ovdf = []
        for val in kztm__uzfh:
            if val not in ulam__ygbnh:
                raise BodoError(
                    f"{func_name}(): 'values' column {val} not found in DataFrame {df}."
                    )
            pbk__ovdf.append(ulam__ygbnh[val])
    if all(isinstance(iaj__iwe, int) for iaj__iwe in kztm__uzfh):
        kztm__uzfh = np.array(kztm__uzfh, 'int64')
    elif all(isinstance(iaj__iwe, str) for iaj__iwe in kztm__uzfh):
        kztm__uzfh = pd.array(kztm__uzfh, 'string')
    else:
        raise BodoError(
            f"{func_name}(): column names selected for 'values' must all share a common int or string type. Please convert your names to a common type using DataFrame.rename()"
            )
    hpb__uupm = set(pbk__ovdf) | set(lhf__zgki) | {fceeb__rny}
    if len(hpb__uupm) != len(pbk__ovdf) + len(lhf__zgki) + 1:
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
    if len(lhf__zgki) == 0:
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
        for oao__nfaec in lhf__zgki:
            index_column = df.data[oao__nfaec]
            check_valid_index_typ(index_column)
    yod__dyod = df.data[fceeb__rny]
    if isinstance(yod__dyod, (bodo.ArrayItemArrayType, bodo.MapArrayType,
        bodo.StructArrayType, bodo.TupleArrayType, bodo.IntervalArrayType)):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column must have scalar rows")
    if isinstance(yod__dyod, bodo.CategoricalArrayType):
        raise BodoError(
            f"{func_name}(): 'columns' DataFrame column does not support categorical data"
            )
    for vevkr__mkf in pbk__ovdf:
        vxk__wzf = df.data[vevkr__mkf]
        if isinstance(vxk__wzf, (bodo.ArrayItemArrayType, bodo.MapArrayType,
            bodo.StructArrayType, bodo.TupleArrayType)
            ) or vxk__wzf == bodo.binary_array_type:
            raise BodoError(
                f"{func_name}(): 'values' DataFrame column must have scalar rows"
                )
    return rlsk__xjw, ocjy__bpqu, kztm__uzfh, lhf__zgki, fceeb__rny, pbk__ovdf


@overload(pd.pivot, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot', inline='always', no_unliteral=True)
def overload_dataframe_pivot(data, index=None, columns=None, values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot()')
    if not isinstance(data, DataFrameType):
        raise BodoError("pandas.pivot(): 'data' argument must be a DataFrame")
    (rlsk__xjw, ocjy__bpqu, kztm__uzfh, oao__nfaec, fceeb__rny, jwjkl__mmb) = (
        pivot_error_checking(data, index, columns, values, 'DataFrame.pivot'))
    if len(rlsk__xjw) == 0:
        if is_overload_none(data.index.name_typ):
            rlsk__xjw = [None]
        else:
            rlsk__xjw = [get_literal_value(data.index.name_typ)]
    if len(kztm__uzfh) == 1:
        kens__diq = None
    else:
        kens__diq = kztm__uzfh
    cwba__ghvsz = 'def impl(data, index=None, columns=None, values=None):\n'
    cwba__ghvsz += f'    pivot_values = data.iloc[:, {fceeb__rny}].unique()\n'
    cwba__ghvsz += '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n'
    if len(oao__nfaec) == 0:
        cwba__ghvsz += f"""        (bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(data)),),
"""
    else:
        cwba__ghvsz += '        (\n'
        for zfst__asn in oao__nfaec:
            cwba__ghvsz += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {zfst__asn}),
"""
        cwba__ghvsz += '        ),\n'
    cwba__ghvsz += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {fceeb__rny}),),
"""
    cwba__ghvsz += '        (\n'
    for vevkr__mkf in jwjkl__mmb:
        cwba__ghvsz += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {vevkr__mkf}),
"""
    cwba__ghvsz += '        ),\n'
    cwba__ghvsz += '        pivot_values,\n'
    cwba__ghvsz += '        index_lit_tup,\n'
    cwba__ghvsz += '        columns_lit,\n'
    cwba__ghvsz += '        values_name_const,\n'
    cwba__ghvsz += '    )\n'
    bxpjm__vul = {}
    exec(cwba__ghvsz, {'bodo': bodo, 'index_lit_tup': tuple(rlsk__xjw),
        'columns_lit': ocjy__bpqu, 'values_name_const': kens__diq}, bxpjm__vul)
    impl = bxpjm__vul['impl']
    return impl


@overload(pd.pivot_table, inline='always', no_unliteral=True)
@overload_method(DataFrameType, 'pivot_table', inline='always',
    no_unliteral=True)
def overload_dataframe_pivot_table(data, values=None, index=None, columns=
    None, aggfunc='mean', fill_value=None, margins=False, dropna=True,
    margins_name='All', observed=False, sort=True, _pivot_values=None):
    check_runtime_cols_unsupported(data, 'DataFrame.pivot_table()')
    efm__ifn = dict(fill_value=fill_value, margins=margins, dropna=dropna,
        margins_name=margins_name, observed=observed, sort=sort)
    fqb__fhajr = dict(fill_value=None, margins=False, dropna=True,
        margins_name='All', observed=False, sort=True)
    check_unsupported_args('DataFrame.pivot_table', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    if not isinstance(data, DataFrameType):
        raise BodoError(
            "pandas.pivot_table(): 'data' argument must be a DataFrame")
    if _pivot_values is None:
        (rlsk__xjw, ocjy__bpqu, kztm__uzfh, oao__nfaec, fceeb__rny, jwjkl__mmb
            ) = (pivot_error_checking(data, index, columns, values,
            'DataFrame.pivot_table'))
        if len(kztm__uzfh) == 1:
            kens__diq = None
        else:
            kens__diq = kztm__uzfh
        cwba__ghvsz = 'def impl(\n'
        cwba__ghvsz += '    data,\n'
        cwba__ghvsz += '    values=None,\n'
        cwba__ghvsz += '    index=None,\n'
        cwba__ghvsz += '    columns=None,\n'
        cwba__ghvsz += '    aggfunc="mean",\n'
        cwba__ghvsz += '    fill_value=None,\n'
        cwba__ghvsz += '    margins=False,\n'
        cwba__ghvsz += '    dropna=True,\n'
        cwba__ghvsz += '    margins_name="All",\n'
        cwba__ghvsz += '    observed=False,\n'
        cwba__ghvsz += '    sort=True,\n'
        cwba__ghvsz += '    _pivot_values=None,\n'
        cwba__ghvsz += '):\n'
        ayu__upse = oao__nfaec + [fceeb__rny] + jwjkl__mmb
        cwba__ghvsz += f'    data = data.iloc[:, {ayu__upse}]\n'
        wnk__tvxm = rlsk__xjw + [ocjy__bpqu]
        cwba__ghvsz += (
            f'    data = data.groupby({wnk__tvxm!r}, as_index=False).agg(aggfunc)\n'
            )
        cwba__ghvsz += (
            f'    pivot_values = data.iloc[:, {len(oao__nfaec)}].unique()\n')
        cwba__ghvsz += (
            '    return bodo.hiframes.pd_dataframe_ext.pivot_impl(\n')
        cwba__ghvsz += '        (\n'
        for i in range(0, len(oao__nfaec)):
            cwba__ghvsz += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),
"""
        cwba__ghvsz += '        ),\n'
        cwba__ghvsz += f"""        (bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {len(oao__nfaec)}),),
"""
        cwba__ghvsz += '        (\n'
        for i in range(len(oao__nfaec) + 1, len(jwjkl__mmb) + len(
            oao__nfaec) + 1):
            cwba__ghvsz += f"""            bodo.hiframes.pd_dataframe_ext.get_dataframe_data(data, {i}),
"""
        cwba__ghvsz += '        ),\n'
        cwba__ghvsz += '        pivot_values,\n'
        cwba__ghvsz += '        index_lit_tup,\n'
        cwba__ghvsz += '        columns_lit,\n'
        cwba__ghvsz += '        values_name_const,\n'
        cwba__ghvsz += '        check_duplicates=False,\n'
        cwba__ghvsz += '    )\n'
        bxpjm__vul = {}
        exec(cwba__ghvsz, {'bodo': bodo, 'numba': numba, 'index_lit_tup':
            tuple(rlsk__xjw), 'columns_lit': ocjy__bpqu,
            'values_name_const': kens__diq}, bxpjm__vul)
        impl = bxpjm__vul['impl']
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
    efm__ifn = dict(values=values, rownames=rownames, colnames=colnames,
        aggfunc=aggfunc, margins=margins, margins_name=margins_name, dropna
        =dropna, normalize=normalize)
    fqb__fhajr = dict(values=None, rownames=None, colnames=None, aggfunc=
        None, margins=False, margins_name='All', dropna=True, normalize=False)
    check_unsupported_args('pandas.crosstab', efm__ifn, fqb__fhajr,
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
    efm__ifn = dict(ignore_index=ignore_index, key=key)
    fqb__fhajr = dict(ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_values', efm__ifn, fqb__fhajr,
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
    wuufd__eyp = set(df.columns)
    if is_overload_constant_str(df.index.name_typ):
        wuufd__eyp.add(get_overload_const_str(df.index.name_typ))
    if is_overload_constant_tuple(by):
        qwweh__rrzcb = [get_overload_const_tuple(by)]
    else:
        qwweh__rrzcb = get_overload_const_list(by)
    qwweh__rrzcb = set((k, '') if (k, '') in wuufd__eyp else k for k in
        qwweh__rrzcb)
    if len(qwweh__rrzcb.difference(wuufd__eyp)) > 0:
        fpl__eown = list(set(get_overload_const_list(by)).difference(
            wuufd__eyp))
        raise_bodo_error(f'sort_values(): invalid keys {fpl__eown} for by.')
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
        brlt__wpfp = get_overload_const_list(na_position)
        for na_position in brlt__wpfp:
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
    efm__ifn = dict(axis=axis, level=level, kind=kind, sort_remaining=
        sort_remaining, ignore_index=ignore_index, key=key)
    fqb__fhajr = dict(axis=0, level=None, kind='quicksort', sort_remaining=
        True, ignore_index=False, key=None)
    check_unsupported_args('DataFrame.sort_index', efm__ifn, fqb__fhajr,
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
    efm__ifn = dict(limit=limit, downcast=downcast)
    fqb__fhajr = dict(limit=None, downcast=None)
    check_unsupported_args('DataFrame.fillna', efm__ifn, fqb__fhajr,
        package_name='pandas', module_name='DataFrame')
    if not (is_overload_none(axis) or is_overload_zero(axis)):
        raise BodoError("DataFrame.fillna(): 'axis' argument not supported.")
    kfvmj__rzy = not is_overload_none(value)
    zdfm__hyvvz = not is_overload_none(method)
    if kfvmj__rzy and zdfm__hyvvz:
        raise BodoError(
            "DataFrame.fillna(): Cannot specify both 'value' and 'method'.")
    if not kfvmj__rzy and not zdfm__hyvvz:
        raise BodoError(
            "DataFrame.fillna(): Must specify one of 'value' and 'method'.")
    if kfvmj__rzy:
        imu__hung = 'value=value'
    else:
        imu__hung = 'method=method'
    data_args = [(f"df['{iaj__iwe}'].fillna({imu__hung}, inplace=inplace)" if
        isinstance(iaj__iwe, str) else
        f'df[{iaj__iwe}].fillna({imu__hung}, inplace=inplace)') for
        iaj__iwe in df.columns]
    cwba__ghvsz = """def impl(df, value=None, method=None, axis=None, inplace=False, limit=None, downcast=None):
"""
    if is_overload_true(inplace):
        cwba__ghvsz += '  ' + '  \n'.join(data_args) + '\n'
        bxpjm__vul = {}
        exec(cwba__ghvsz, {}, bxpjm__vul)
        impl = bxpjm__vul['impl']
        return impl
    else:
        return _gen_init_df(cwba__ghvsz, df.columns, ', '.join(tgxg__bci +
            '.values' for tgxg__bci in data_args))


@overload_method(DataFrameType, 'reset_index', inline='always',
    no_unliteral=True)
def overload_dataframe_reset_index(df, level=None, drop=False, inplace=
    False, col_level=0, col_fill='', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.reset_index()')
    efm__ifn = dict(col_level=col_level, col_fill=col_fill)
    fqb__fhajr = dict(col_level=0, col_fill='')
    check_unsupported_args('DataFrame.reset_index', efm__ifn, fqb__fhajr,
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
    cwba__ghvsz = """def impl(df, level=None, drop=False, inplace=False, col_level=0, col_fill='', _bodo_transformed=False,):
"""
    cwba__ghvsz += (
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
        thp__mzj = 'index' if 'index' not in columns else 'level_0'
        index_names = get_index_names(df.index, 'DataFrame.reset_index()',
            thp__mzj)
        columns = index_names + columns
        if isinstance(df.index, MultiIndexType):
            cwba__ghvsz += (
                '  m_index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
                )
            krbrb__satvw = ['m_index._data[{}]'.format(i) for i in range(df
                .index.nlevels)]
            data_args = krbrb__satvw + data_args
        else:
            caso__ygaxj = (
                'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
                )
            data_args = [caso__ygaxj] + data_args
    return _gen_init_df(cwba__ghvsz, columns, ', '.join(data_args), 'index')


def _is_all_levels(df, level):
    qwgws__bjnsn = len(get_index_data_arr_types(df.index))
    return is_overload_none(level) or is_overload_constant_int(level
        ) and get_overload_const_int(level
        ) == 0 and qwgws__bjnsn == 1 or is_overload_constant_list(level
        ) and list(get_overload_const_list(level)) == list(range(qwgws__bjnsn))


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
        yrzz__smy = list(range(len(df.columns)))
    elif not is_overload_constant_list(subset):
        raise_bodo_error(
            f'df.dropna(): subset argument should a constant list, not {subset}'
            )
    else:
        zqpbh__agyz = get_overload_const_list(subset)
        yrzz__smy = []
        for klk__flfh in zqpbh__agyz:
            if klk__flfh not in df.columns:
                raise_bodo_error(
                    f"df.dropna(): column '{klk__flfh}' not in data frame columns {df}"
                    )
            yrzz__smy.append(df.columns.index(klk__flfh))
    fvh__iowla = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(fvh__iowla))
    cwba__ghvsz = (
        "def impl(df, axis=0, how='any', thresh=None, subset=None, inplace=False):\n"
        )
    for i in range(fvh__iowla):
        cwba__ghvsz += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    cwba__ghvsz += (
        """  ({0}, index_arr) = bodo.libs.array_kernels.dropna(({0}, {1}), how, thresh, ({2},))
"""
        .format(data_args, index, ', '.join(str(a) for a in yrzz__smy)))
    cwba__ghvsz += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return _gen_init_df(cwba__ghvsz, df.columns, data_args, 'index')


@overload_method(DataFrameType, 'drop', inline='always', no_unliteral=True)
def overload_dataframe_drop(df, labels=None, axis=0, index=None, columns=
    None, level=None, inplace=False, errors='raise', _bodo_transformed=False):
    check_runtime_cols_unsupported(df, 'DataFrame.drop()')
    efm__ifn = dict(index=index, level=level, errors=errors)
    fqb__fhajr = dict(index=None, level=None, errors='raise')
    check_unsupported_args('DataFrame.drop', efm__ifn, fqb__fhajr,
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
            sbfdk__cpn = get_overload_const_str(labels),
        elif is_overload_constant_list(labels):
            sbfdk__cpn = get_overload_const_list(labels)
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
            sbfdk__cpn = get_overload_const_str(columns),
        elif is_overload_constant_list(columns):
            sbfdk__cpn = get_overload_const_list(columns)
        else:
            raise_bodo_error(
                'constant list of columns expected for labels in DataFrame.drop()'
                )
    for iaj__iwe in sbfdk__cpn:
        if iaj__iwe not in df.columns:
            raise_bodo_error(
                'DataFrame.drop(): column {} not in DataFrame columns {}'.
                format(iaj__iwe, df.columns))
    if len(set(sbfdk__cpn)) == len(df.columns):
        raise BodoError('DataFrame.drop(): Dropping all columns not supported.'
            )
    inplace = is_overload_true(inplace)
    fbtvm__xhvg = tuple(iaj__iwe for iaj__iwe in df.columns if iaj__iwe not in
        sbfdk__cpn)
    data_args = ', '.join(
        'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {}){}'.
        format(df.columns.index(iaj__iwe), '.copy()' if not inplace else ''
        ) for iaj__iwe in fbtvm__xhvg)
    cwba__ghvsz = (
        'def impl(df, labels=None, axis=0, index=None, columns=None,\n')
    cwba__ghvsz += (
        "     level=None, inplace=False, errors='raise', _bodo_transformed=False):\n"
        )
    index = 'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)'
    return _gen_init_df(cwba__ghvsz, fbtvm__xhvg, data_args, index)


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
    efm__ifn = dict(random_state=random_state, weights=weights, axis=axis,
        ignore_index=ignore_index)
    krqcf__zvst = dict(random_state=None, weights=None, axis=None,
        ignore_index=False)
    check_unsupported_args('DataFrame.sample', efm__ifn, krqcf__zvst,
        package_name='pandas', module_name='DataFrame')
    if not is_overload_none(n) and not is_overload_none(frac):
        raise BodoError(
            'DataFrame.sample(): only one of n and frac option can be selected'
            )
    fvh__iowla = len(df.columns)
    data_args = ', '.join('data_{}'.format(i) for i in range(fvh__iowla))
    cwba__ghvsz = """def impl(df, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None, ignore_index=False):
"""
    for i in range(fvh__iowla):
        cwba__ghvsz += (
            '  data_{0} = bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {0})\n'
            .format(i))
    cwba__ghvsz += '  if frac is None:\n'
    cwba__ghvsz += '    frac_d = -1.0\n'
    cwba__ghvsz += '  else:\n'
    cwba__ghvsz += '    frac_d = frac\n'
    cwba__ghvsz += '  if n is None:\n'
    cwba__ghvsz += '    n_i = 0\n'
    cwba__ghvsz += '  else:\n'
    cwba__ghvsz += '    n_i = n\n'
    index = (
        'bodo.utils.conversion.index_to_array(bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df))'
        )
    cwba__ghvsz += (
        """  ({0},), index_arr = bodo.libs.array_kernels.sample_table_operation(({0},), {1}, n_i, frac_d, replace)
"""
        .format(data_args, index))
    cwba__ghvsz += (
        '  index = bodo.utils.conversion.index_from_array(index_arr)\n')
    return bodo.hiframes.dataframe_impl._gen_init_df(cwba__ghvsz, df.
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
    qvw__nqaud = {'verbose': verbose, 'buf': buf, 'max_cols': max_cols,
        'memory_usage': memory_usage, 'show_counts': show_counts,
        'null_counts': null_counts}
    xwxv__qye = {'verbose': None, 'buf': None, 'max_cols': None,
        'memory_usage': None, 'show_counts': None, 'null_counts': None}
    check_unsupported_args('DataFrame.info', qvw__nqaud, xwxv__qye,
        package_name='pandas', module_name='DataFrame')
    ubn__kliz = f"<class '{str(type(df)).split('.')[-1]}"
    if len(df.columns) == 0:

        def _info_impl(df, verbose=None, buf=None, max_cols=None,
            memory_usage=None, show_counts=None, null_counts=None):
            fks__xksf = ubn__kliz + '\n'
            fks__xksf += 'Index: 0 entries\n'
            fks__xksf += 'Empty DataFrame'
            print(fks__xksf)
        return _info_impl
    else:
        cwba__ghvsz = """def _info_impl(df, verbose=None, buf=None, max_cols=None, memory_usage=None, show_counts=None, null_counts=None): #pragma: no cover
"""
        cwba__ghvsz += '    ncols = df.shape[1]\n'
        cwba__ghvsz += f'    lines = "{ubn__kliz}\\n"\n'
        cwba__ghvsz += f'    lines += "{df.index}: "\n'
        cwba__ghvsz += (
            '    index = bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df)\n'
            )
        if isinstance(df.index, bodo.hiframes.pd_index_ext.RangeIndexType):
            cwba__ghvsz += """    lines += f"{len(index)} entries, {index.start} to {index.stop-1}\\n\"
"""
        elif isinstance(df.index, bodo.hiframes.pd_index_ext.StringIndexType):
            cwba__ghvsz += """    lines += f"{len(index)} entries, {index[0]} to {index[len(index)-1]}\\n\"
"""
        else:
            cwba__ghvsz += (
                '    lines += f"{len(index)} entries, {index[0]} to {index[-1]}\\n"\n'
                )
        cwba__ghvsz += (
            '    lines += f"Data columns (total {ncols} columns):\\n"\n')
        cwba__ghvsz += (
            f'    space = {max(len(str(k)) for k in df.columns) + 1}\n')
        cwba__ghvsz += '    column_width = max(space, 7)\n'
        cwba__ghvsz += '    column= "Column"\n'
        cwba__ghvsz += '    underl= "------"\n'
        cwba__ghvsz += (
            '    lines += f"#   {column:<{column_width}} Non-Null Count  Dtype\\n"\n'
            )
        cwba__ghvsz += (
            '    lines += f"--- {underl:<{column_width}} --------------  -----\\n"\n'
            )
        cwba__ghvsz += '    mem_size = 0\n'
        cwba__ghvsz += (
            '    col_name = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        cwba__ghvsz += """    non_null_count = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)
"""
        cwba__ghvsz += (
            '    col_dtype = bodo.libs.str_arr_ext.pre_alloc_string_array(ncols, -1)\n'
            )
        vgab__inv = dict()
        for i in range(len(df.columns)):
            cwba__ghvsz += f"""    non_null_count[{i}] = str(bodo.libs.array_ops.array_op_count(bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i})))
"""
            xaoro__mktws = f'{df.data[i].dtype}'
            if isinstance(df.data[i], bodo.CategoricalArrayType):
                xaoro__mktws = 'category'
            elif isinstance(df.data[i], bodo.IntegerArrayType):
                sqkkb__nll = bodo.libs.int_arr_ext.IntDtype(df.data[i].dtype
                    ).name
                xaoro__mktws = f'{sqkkb__nll[:-7]}'
            cwba__ghvsz += f'    col_dtype[{i}] = "{xaoro__mktws}"\n'
            if xaoro__mktws in vgab__inv:
                vgab__inv[xaoro__mktws] += 1
            else:
                vgab__inv[xaoro__mktws] = 1
            cwba__ghvsz += f'    col_name[{i}] = "{df.columns[i]}"\n'
            cwba__ghvsz += f"""    mem_size += bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes
"""
        cwba__ghvsz += """    column_info = [f'{i:^3} {name:<{column_width}} {count} non-null      {dtype}' for i, (name, count, dtype) in enumerate(zip(col_name, non_null_count, col_dtype))]
"""
        cwba__ghvsz += '    for i in column_info:\n'
        cwba__ghvsz += "        lines += f'{i}\\n'\n"
        zhy__pnbvf = ', '.join(f'{k}({vgab__inv[k]})' for k in sorted(
            vgab__inv))
        cwba__ghvsz += f"    lines += 'dtypes: {zhy__pnbvf}\\n'\n"
        cwba__ghvsz += '    mem_size += df.index.nbytes\n'
        cwba__ghvsz += '    total_size = _sizeof_fmt(mem_size)\n'
        cwba__ghvsz += "    lines += f'memory usage: {total_size}'\n"
        cwba__ghvsz += '    print(lines)\n'
        bxpjm__vul = {}
        exec(cwba__ghvsz, {'_sizeof_fmt': _sizeof_fmt, 'pd': pd, 'bodo':
            bodo, 'np': np}, bxpjm__vul)
        _info_impl = bxpjm__vul['_info_impl']
        return _info_impl


@overload_method(DataFrameType, 'memory_usage', inline='always',
    no_unliteral=True)
def overload_dataframe_memory_usage(df, index=True, deep=False):
    check_runtime_cols_unsupported(df, 'DataFrame.memory_usage()')
    cwba__ghvsz = 'def impl(df, index=True, deep=False):\n'
    data = ', '.join(
        f'bodo.hiframes.pd_dataframe_ext.get_dataframe_data(df, {i}).nbytes'
         for i in range(len(df.columns)))
    if is_overload_true(index):
        pry__jxqqa = (
            'bodo.hiframes.pd_dataframe_ext.get_dataframe_index(df).nbytes\n,')
        zgmql__ygewu = ','.join(f"'{iaj__iwe}'" for iaj__iwe in df.columns)
        arr = (
            f"bodo.utils.conversion.coerce_to_array(('Index',{zgmql__ygewu}))")
        index = f'bodo.hiframes.pd_index_ext.init_binary_str_index({arr})'
        cwba__ghvsz += f"""  return bodo.hiframes.pd_series_ext.init_series(({pry__jxqqa}{data}), {index}, None)
"""
    else:
        pak__puae = ',' if len(df.columns) == 1 else ''
        uih__sqequ = gen_const_tup(df.columns)
        cwba__ghvsz += f"""  return bodo.hiframes.pd_series_ext.init_series(({data}{pak__puae}), pd.Index({uih__sqequ}), None)
"""
    bxpjm__vul = {}
    exec(cwba__ghvsz, {'bodo': bodo, 'pd': pd}, bxpjm__vul)
    impl = bxpjm__vul['impl']
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
    plz__ckdn = 'read_excel_df{}'.format(next_label())
    setattr(types, plz__ckdn, df_type)
    hpyw__rmn = False
    if is_overload_constant_list(parse_dates):
        hpyw__rmn = get_overload_const_list(parse_dates)
    zkdi__kia = ', '.join(["'{}':{}".format(cname, _get_pd_dtype_str(t)) for
        cname, t in zip(df_type.columns, df_type.data)])
    cwba__ghvsz = (
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
        .format(plz__ckdn, list(df_type.columns), zkdi__kia, hpyw__rmn))
    bxpjm__vul = {}
    exec(cwba__ghvsz, globals(), bxpjm__vul)
    impl = bxpjm__vul['impl']
    return impl


def overload_dataframe_plot(df, x=None, y=None, kind='line', figsize=None,
    xlabel=None, ylabel=None, title=None, legend=True, fontsize=None,
    xticks=None, yticks=None, ax=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as hnsmj__dxsz:
        raise BodoError('df.plot needs matplotllib which is not installed.')
    cwba__ghvsz = (
        "def impl(df, x=None, y=None, kind='line', figsize=None, xlabel=None, \n"
        )
    cwba__ghvsz += (
        '    ylabel=None, title=None, legend=True, fontsize=None, \n')
    cwba__ghvsz += '    xticks=None, yticks=None, ax=None):\n'
    if is_overload_none(ax):
        cwba__ghvsz += '   fig, ax = plt.subplots()\n'
    else:
        cwba__ghvsz += '   fig = ax.get_figure()\n'
    if not is_overload_none(figsize):
        cwba__ghvsz += '   fig.set_figwidth(figsize[0])\n'
        cwba__ghvsz += '   fig.set_figheight(figsize[1])\n'
    if is_overload_none(xlabel):
        cwba__ghvsz += '   xlabel = x\n'
    cwba__ghvsz += '   ax.set_xlabel(xlabel)\n'
    if is_overload_none(ylabel):
        cwba__ghvsz += '   ylabel = y\n'
    else:
        cwba__ghvsz += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(title):
        cwba__ghvsz += '   ax.set_title(title)\n'
    if not is_overload_none(fontsize):
        cwba__ghvsz += '   ax.tick_params(labelsize=fontsize)\n'
    kind = get_overload_const_str(kind)
    if kind == 'line':
        if is_overload_none(x) and is_overload_none(y):
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    cwba__ghvsz += (
                        f'   ax.plot(df.iloc[:, {i}], label=df.columns[{i}])\n'
                        )
        elif is_overload_none(x):
            cwba__ghvsz += '   ax.plot(df[y], label=y)\n'
        elif is_overload_none(y):
            ughv__osx = get_overload_const_str(x)
            snxcc__qsh = df.columns.index(ughv__osx)
            for i in range(len(df.columns)):
                if isinstance(df.data[i], (types.Array, IntegerArrayType)
                    ) and isinstance(df.data[i].dtype, (types.Integer,
                    types.Float)):
                    if snxcc__qsh != i:
                        cwba__ghvsz += f"""   ax.plot(df[x], df.iloc[:, {i}], label=df.columns[{i}])
"""
        else:
            cwba__ghvsz += '   ax.plot(df[x], df[y], label=y)\n'
    elif kind == 'scatter':
        legend = False
        cwba__ghvsz += '   ax.scatter(df[x], df[y], s=20)\n'
        cwba__ghvsz += '   ax.set_ylabel(ylabel)\n'
    if not is_overload_none(xticks):
        cwba__ghvsz += '   ax.set_xticks(xticks)\n'
    if not is_overload_none(yticks):
        cwba__ghvsz += '   ax.set_yticks(yticks)\n'
    if is_overload_true(legend):
        cwba__ghvsz += '   ax.legend()\n'
    cwba__ghvsz += '   return ax\n'
    bxpjm__vul = {}
    exec(cwba__ghvsz, {'bodo': bodo, 'plt': plt}, bxpjm__vul)
    impl = bxpjm__vul['impl']
    return impl


@lower_builtin('df.plot', DataFrameType, types.VarArg(types.Any))
def dataframe_plot_low(context, builder, sig, args):
    impl = overload_dataframe_plot(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def is_df_values_numpy_supported_dftyp(df_typ):
    for ojewn__svd in df_typ.data:
        if not (isinstance(ojewn__svd, IntegerArrayType) or isinstance(
            ojewn__svd.dtype, types.Number) or ojewn__svd.dtype in (bodo.
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
        miqi__rnp = args[0]
        wbjy__kum = args[1].literal_value
        val = args[2]
        assert val != types.unknown
        wfakg__yrke = miqi__rnp
        check_runtime_cols_unsupported(miqi__rnp, 'set_df_col()')
        if isinstance(miqi__rnp, DataFrameType):
            index = miqi__rnp.index
            if len(miqi__rnp.columns) == 0:
                index = bodo.hiframes.pd_index_ext.RangeIndexType(types.none)
            if isinstance(val, SeriesType):
                if len(miqi__rnp.columns) == 0:
                    index = val.index
                val = val.data
            if is_pd_index_type(val):
                val = bodo.utils.typing.get_index_data_arr_types(val)[0]
            if isinstance(val, types.List):
                val = dtype_to_array_type(val.dtype)
            if not is_array_typ(val):
                val = dtype_to_array_type(val)
            if wbjy__kum in miqi__rnp.columns:
                fbtvm__xhvg = miqi__rnp.columns
                sfmrl__xduz = miqi__rnp.columns.index(wbjy__kum)
                nwp__cgk = list(miqi__rnp.data)
                nwp__cgk[sfmrl__xduz] = val
                nwp__cgk = tuple(nwp__cgk)
            else:
                fbtvm__xhvg = miqi__rnp.columns + (wbjy__kum,)
                nwp__cgk = miqi__rnp.data + (val,)
            wfakg__yrke = DataFrameType(nwp__cgk, index, fbtvm__xhvg,
                miqi__rnp.dist, miqi__rnp.is_table_format)
        return wfakg__yrke(*args)


SetDfColInfer.prefer_literal = True


def _parse_query_expr(expr, env, columns, cleaned_columns, index_name=None,
    join_cleaned_cols=()):
    qifyo__lxfcm = {}

    def _rewrite_membership_op(self, node, left, right):
        ardi__ecbzk = node.op
        op = self.visit(ardi__ecbzk)
        return op, ardi__ecbzk, left, right

    def _maybe_evaluate_binop(self, op, op_class, lhs, rhs, eval_in_python=
        ('in', 'not in'), maybe_eval_in_python=('==', '!=', '<', '>', '<=',
        '>=')):
        res = op(lhs, rhs)
        return res
    yvor__ausfr = []


    class NewFuncNode(pd.core.computation.ops.FuncNode):

        def __init__(self, name):
            if (name not in pd.core.computation.ops.MATHOPS or pd.core.
                computation.check._NUMEXPR_INSTALLED and pd.core.
                computation.check_NUMEXPR_VERSION < pd.core.computation.ops
                .LooseVersion('2.6.9') and name in ('floor', 'ceil')):
                if name not in yvor__ausfr:
                    raise BodoError('"{0}" is not a supported function'.
                        format(name))
            self.name = name
            if name in yvor__ausfr:
                self.func = name
            else:
                self.func = getattr(np, name)

        def __call__(self, *args):
            return pd.core.computation.ops.MathCall(self, args)

        def __repr__(self):
            return pd.io.formats.printing.pprint_thing(self.name)

    def visit_Attribute(self, node, **kwargs):
        crq__lkld = node.attr
        value = node.value
        bgh__abv = pd.core.computation.ops.LOCAL_TAG
        if crq__lkld in ('str', 'dt'):
            try:
                olgw__hnaol = str(self.visit(value))
            except pd.core.computation.ops.UndefinedVariableError as iny__ihsab:
                col_name = iny__ihsab.args[0].split("'")[1]
                raise BodoError(
                    'df.query(): column {} is not found in dataframe columns {}'
                    .format(col_name, columns))
        else:
            olgw__hnaol = str(self.visit(value))
        ishs__mswlg = olgw__hnaol, crq__lkld
        if ishs__mswlg in join_cleaned_cols:
            crq__lkld = join_cleaned_cols[ishs__mswlg]
        name = olgw__hnaol + '.' + crq__lkld
        if name.startswith(bgh__abv):
            name = name[len(bgh__abv):]
        if crq__lkld in ('str', 'dt'):
            dneg__xzqco = columns[cleaned_columns.index(olgw__hnaol)]
            qifyo__lxfcm[dneg__xzqco] = olgw__hnaol
            self.env.scope[name] = 0
            return self.term_type(bgh__abv + name, self.env)
        yvor__ausfr.append(name)
        return NewFuncNode(name)

    def __str__(self):
        if isinstance(self.value, list):
            return '{}'.format(self.value)
        if isinstance(self.value, str):
            return "'{}'".format(self.value)
        return pd.io.formats.printing.pprint_thing(self.name)

    def math__str__(self):
        if self.op in yvor__ausfr:
            return pd.io.formats.printing.pprint_thing('{0}({1})'.format(
                self.op, ','.join(map(str, self.operands))))
        ccgyn__pqvl = map(lambda a:
            'bodo.hiframes.pd_series_ext.get_series_data({})'.format(str(a)
            ), self.operands)
        op = 'np.{}'.format(self.op)
        wbjy__kum = (
            'bodo.hiframes.pd_index_ext.init_range_index(0, len({}), 1, None)'
            .format(str(self.operands[0])))
        return pd.io.formats.printing.pprint_thing(
            'bodo.hiframes.pd_series_ext.init_series({0}({1}), {2})'.format
            (op, ','.join(ccgyn__pqvl), wbjy__kum))

    def op__str__(self):
        xqank__pur = ('({0})'.format(pd.io.formats.printing.pprint_thing(
            skyq__kmpav)) for skyq__kmpav in self.operands)
        if self.op == 'in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_isin_dummy({})'.format(
                ', '.join(xqank__pur)))
        if self.op == 'not in':
            return pd.io.formats.printing.pprint_thing(
                'bodo.hiframes.pd_dataframe_ext.val_notin_dummy({})'.format
                (', '.join(xqank__pur)))
        return pd.io.formats.printing.pprint_thing(' {0} '.format(self.op).
            join(xqank__pur))
    zhr__joj = pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op
    olw__aheev = pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop
    xgirj__fiod = pd.core.computation.expr.BaseExprVisitor.visit_Attribute
    cxzb__uxeeo = (pd.core.computation.expr.BaseExprVisitor.
        _maybe_downcast_constants)
    aumge__jkuzx = pd.core.computation.ops.Term.__str__
    jtayi__wnj = pd.core.computation.ops.MathCall.__str__
    zlmwx__xyja = pd.core.computation.ops.Op.__str__
    vpu__uqinb = pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops
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
        dsa__juoz = pd.core.computation.expr.Expr(expr, env=env)
        uty__evfoh = str(dsa__juoz)
    except pd.core.computation.ops.UndefinedVariableError as iny__ihsab:
        if not is_overload_none(index_name) and get_overload_const_str(
            index_name) == iny__ihsab.args[0].split("'")[1]:
            raise BodoError(
                "df.query(): Refering to named index ('{}') by name is not supported"
                .format(get_overload_const_str(index_name)))
        else:
            raise BodoError(f'df.query(): undefined variable, {iny__ihsab}')
    finally:
        pd.core.computation.expr.BaseExprVisitor._rewrite_membership_op = (
            zhr__joj)
        pd.core.computation.expr.BaseExprVisitor._maybe_evaluate_binop = (
            olw__aheev)
        pd.core.computation.expr.BaseExprVisitor.visit_Attribute = xgirj__fiod
        (pd.core.computation.expr.BaseExprVisitor._maybe_downcast_constants
            ) = cxzb__uxeeo
        pd.core.computation.ops.Term.__str__ = aumge__jkuzx
        pd.core.computation.ops.MathCall.__str__ = jtayi__wnj
        pd.core.computation.ops.Op.__str__ = zlmwx__xyja
        pd.core.computation.ops.BinOp._disallow_scalar_only_bool_ops = (
            vpu__uqinb)
    vchsz__zmn = pd.core.computation.parsing.clean_column_name
    qifyo__lxfcm.update({iaj__iwe: vchsz__zmn(iaj__iwe) for iaj__iwe in
        columns if vchsz__zmn(iaj__iwe) in dsa__juoz.names})
    return dsa__juoz, uty__evfoh, qifyo__lxfcm


class DataFrameTupleIterator(types.SimpleIteratorType):

    def __init__(self, col_names, arr_typs):
        self.array_types = arr_typs
        self.col_names = col_names
        yms__bsi = ['{}={}'.format(col_names[i], arr_typs[i]) for i in
            range(len(col_names))]
        name = 'itertuples({})'.format(','.join(yms__bsi))
        pjp__vpti = namedtuple('Pandas', col_names)
        fhmmn__yfgbr = types.NamedTuple([_get_series_dtype(a) for a in
            arr_typs], pjp__vpti)
        super(DataFrameTupleIterator, self).__init__(name, fhmmn__yfgbr)

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
        htk__fnbxu = [if_series_to_array_type(a) for a in args[len(args) // 2:]
            ]
        assert 'Index' not in col_names[0]
        col_names = ['Index'] + col_names
        htk__fnbxu = [types.Array(types.int64, 1, 'C')] + htk__fnbxu
        emhb__anz = DataFrameTupleIterator(col_names, htk__fnbxu)
        return emhb__anz(*args)


TypeIterTuples.prefer_literal = True


@register_model(DataFrameTupleIterator)
class DataFrameTupleIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        lyqwp__bpu = [('index', types.EphemeralPointer(types.uintp))] + [(
            'array{}'.format(i), arr) for i, arr in enumerate(fe_type.
            array_types[1:])]
        super(DataFrameTupleIteratorModel, self).__init__(dmm, fe_type,
            lyqwp__bpu)

    def from_return(self, builder, value):
        return value


@lower_builtin(get_itertuples, types.VarArg(types.Any))
def get_itertuples_impl(context, builder, sig, args):
    zgthk__iqrs = args[len(args) // 2:]
    czmqd__bsjj = sig.args[len(sig.args) // 2:]
    hvpi__dsyuu = context.make_helper(builder, sig.return_type)
    skoo__jkz = context.get_constant(types.intp, 0)
    gsadl__yyiu = cgutils.alloca_once_value(builder, skoo__jkz)
    hvpi__dsyuu.index = gsadl__yyiu
    for i, arr in enumerate(zgthk__iqrs):
        setattr(hvpi__dsyuu, 'array{}'.format(i), arr)
    for arr, arr_typ in zip(zgthk__iqrs, czmqd__bsjj):
        context.nrt.incref(builder, arr_typ, arr)
    res = hvpi__dsyuu._getvalue()
    return impl_ret_new_ref(context, builder, sig.return_type, res)


@lower_builtin('getiter', DataFrameTupleIterator)
def getiter_itertuples(context, builder, sig, args):
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', DataFrameTupleIterator)
@iternext_impl(RefType.UNTRACKED)
def iternext_itertuples(context, builder, sig, args, result):
    pjam__znji, = sig.args
    tkd__lva, = args
    hvpi__dsyuu = context.make_helper(builder, pjam__znji, value=tkd__lva)
    cak__xir = signature(types.intp, pjam__znji.array_types[1])
    aasw__zbs = context.compile_internal(builder, lambda a: len(a),
        cak__xir, [hvpi__dsyuu.array0])
    index = builder.load(hvpi__dsyuu.index)
    gcym__vdn = builder.icmp(lc.ICMP_SLT, index, aasw__zbs)
    result.set_valid(gcym__vdn)
    with builder.if_then(gcym__vdn):
        values = [index]
        for i, arr_typ in enumerate(pjam__znji.array_types[1:]):
            wwu__xgl = getattr(hvpi__dsyuu, 'array{}'.format(i))
            if arr_typ == types.Array(types.NPDatetime('ns'), 1, 'C'):
                uahj__ynw = signature(pd_timestamp_type, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: bodo.
                    hiframes.pd_timestamp_ext.
                    convert_datetime64_to_timestamp(np.int64(a[i])),
                    uahj__ynw, [wwu__xgl, index])
            else:
                uahj__ynw = signature(arr_typ.dtype, arr_typ, types.intp)
                val = context.compile_internal(builder, lambda a, i: a[i],
                    uahj__ynw, [wwu__xgl, index])
            values.append(val)
        value = context.make_tuple(builder, pjam__znji.yield_type, values)
        result.yield_(value)
        oqgcz__tsi = cgutils.increment_index(builder, index)
        builder.store(oqgcz__tsi, hvpi__dsyuu.index)


def _analyze_op_pair_first(self, scope, equiv_set, expr, lhs):
    typ = self.typemap[expr.value.name].first_type
    if not isinstance(typ, types.NamedTuple):
        return None
    lhs = ir.Var(scope, mk_unique_var('tuple_var'), expr.loc)
    self.typemap[lhs.name] = typ
    rhs = ir.Expr.pair_first(expr.value, expr.loc)
    hvym__sizxb = ir.Assign(rhs, lhs, expr.loc)
    buu__mtt = lhs
    zxdtw__xqugi = []
    fjmue__mve = []
    emup__azlw = typ.count
    for i in range(emup__azlw):
        ljl__jzd = ir.Var(buu__mtt.scope, mk_unique_var('{}_size{}'.format(
            buu__mtt.name, i)), buu__mtt.loc)
        rzi__vrd = ir.Expr.static_getitem(lhs, i, None, buu__mtt.loc)
        self.calltypes[rzi__vrd] = None
        zxdtw__xqugi.append(ir.Assign(rzi__vrd, ljl__jzd, buu__mtt.loc))
        self._define(equiv_set, ljl__jzd, types.intp, rzi__vrd)
        fjmue__mve.append(ljl__jzd)
    jjyu__ubbrz = tuple(fjmue__mve)
    return numba.parfors.array_analysis.ArrayAnalysis.AnalyzeResult(shape=
        jjyu__ubbrz, pre=[hvym__sizxb] + zxdtw__xqugi)


numba.parfors.array_analysis.ArrayAnalysis._analyze_op_pair_first = (
    _analyze_op_pair_first)
