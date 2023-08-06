"""
Helper functions for transformations.
"""
import itertools
import math
import operator
import types as pytypes
from collections import namedtuple
import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, types
from numba.core.ir_utils import GuardException, build_definitions, compile_to_numba_ir, compute_cfg_from_blocks, find_callname, find_const, get_definition, guard, is_setitem, mk_unique_var, replace_arg_nodes, require
from numba.core.registry import CPUDispatcher
from numba.core.typing.templates import fold_arguments
import bodo
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.map_arr_ext import MapArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.struct_arr_ext import StructArrayType, StructType
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoConstUpdatedError, BodoError, can_literalize_type, get_literal_value, get_overload_const_bool, get_overload_const_list, is_literal_type, is_overload_constant_bool
from bodo.utils.utils import is_array_typ, is_assign, is_call, is_expr
ReplaceFunc = namedtuple('ReplaceFunc', ['func', 'arg_types', 'args',
    'glbls', 'inline_bodo_calls', 'run_full_pipeline', 'pre_nodes'])
bodo_types_with_params = {'ArrayItemArrayType', 'CSRMatrixType',
    'CategoricalArrayType', 'CategoricalIndexType', 'DataFrameType',
    'DatetimeIndexType', 'Decimal128Type', 'DecimalArrayType',
    'IntegerArrayType', 'IntervalArrayType', 'IntervalIndexType', 'List',
    'MapArrayType', 'NumericIndexType', 'PDCategoricalDtype',
    'PeriodIndexType', 'RangeIndexType', 'SeriesType', 'StringIndexType',
    'BinaryIndexType', 'StructArrayType', 'TimedeltaIndexType',
    'TupleArrayType'}
container_update_method_names = ('clear', 'pop', 'popitem', 'update', 'add',
    'difference_update', 'discard', 'intersection_update', 'remove',
    'symmetric_difference_update', 'append', 'extend', 'insert', 'reverse',
    'sort')
no_side_effect_call_tuples = {(int,), (list,), (set,), (dict,), (min,), (
    max,), (abs,), (len,), (bool,), (str,), ('ceil', math), ('init_series',
    'pd_series_ext', 'hiframes', bodo), ('get_series_data', 'pd_series_ext',
    'hiframes', bodo), ('get_series_index', 'pd_series_ext', 'hiframes',
    bodo), ('get_series_name', 'pd_series_ext', 'hiframes', bodo), (
    'get_index_data', 'pd_index_ext', 'hiframes', bodo), ('get_index_name',
    'pd_index_ext', 'hiframes', bodo), ('init_binary_str_index',
    'pd_index_ext', 'hiframes', bodo), ('init_numeric_index',
    'pd_index_ext', 'hiframes', bodo), ('init_categorical_index',
    'pd_index_ext', 'hiframes', bodo), ('_dti_val_finalize', 'pd_index_ext',
    'hiframes', bodo), ('init_datetime_index', 'pd_index_ext', 'hiframes',
    bodo), ('init_timedelta_index', 'pd_index_ext', 'hiframes', bodo), (
    'init_range_index', 'pd_index_ext', 'hiframes', bodo), (
    'init_heter_index', 'pd_index_ext', 'hiframes', bodo), (
    'get_int_arr_data', 'int_arr_ext', 'libs', bodo), ('get_int_arr_bitmap',
    'int_arr_ext', 'libs', bodo), ('init_integer_array', 'int_arr_ext',
    'libs', bodo), ('alloc_int_array', 'int_arr_ext', 'libs', bodo), (
    'inplace_eq', 'str_arr_ext', 'libs', bodo), ('get_bool_arr_data',
    'bool_arr_ext', 'libs', bodo), ('get_bool_arr_bitmap', 'bool_arr_ext',
    'libs', bodo), ('init_bool_array', 'bool_arr_ext', 'libs', bodo), (
    'alloc_bool_array', 'bool_arr_ext', 'libs', bodo), (bodo.libs.
    bool_arr_ext.compute_or_body,), (bodo.libs.bool_arr_ext.
    compute_and_body,), ('alloc_datetime_date_array', 'datetime_date_ext',
    'hiframes', bodo), ('alloc_datetime_timedelta_array',
    'datetime_timedelta_ext', 'hiframes', bodo), ('cat_replace',
    'pd_categorical_ext', 'hiframes', bodo), ('init_categorical_array',
    'pd_categorical_ext', 'hiframes', bodo), ('alloc_categorical_array',
    'pd_categorical_ext', 'hiframes', bodo), ('get_categorical_arr_codes',
    'pd_categorical_ext', 'hiframes', bodo), ('_sum_handle_nan',
    'series_kernels', 'hiframes', bodo), ('_box_cat_val', 'series_kernels',
    'hiframes', bodo), ('_mean_handle_nan', 'series_kernels', 'hiframes',
    bodo), ('_var_handle_mincount', 'series_kernels', 'hiframes', bodo), (
    '_handle_nan_count', 'series_kernels', 'hiframes', bodo), (
    '_compute_var_nan_count_ddof', 'series_kernels', 'hiframes', bodo), (
    '_sem_handle_nan', 'series_kernels', 'hiframes', bodo), ('dist_return',
    'distributed_api', 'libs', bodo), ('init_dataframe', 'pd_dataframe_ext',
    'hiframes', bodo), ('get_dataframe_data', 'pd_dataframe_ext',
    'hiframes', bodo), ('get_dataframe_table', 'pd_dataframe_ext',
    'hiframes', bodo), ('get_table_data', 'table', 'hiframes', bodo), (
    'get_dataframe_index', 'pd_dataframe_ext', 'hiframes', bodo), (
    'init_rolling', 'pd_rolling_ext', 'hiframes', bodo), ('init_groupby',
    'pd_groupby_ext', 'hiframes', bodo), ('calc_nitems', 'array_kernels',
    'libs', bodo), ('concat', 'array_kernels', 'libs', bodo), ('unique',
    'array_kernels', 'libs', bodo), ('nunique', 'array_kernels', 'libs',
    bodo), ('quantile', 'array_kernels', 'libs', bodo), ('explode',
    'array_kernels', 'libs', bodo), ('explode_no_index', 'array_kernels',
    'libs', bodo), ('get_arr_lens', 'array_kernels', 'libs', bodo), (
    'str_arr_from_sequence', 'str_arr_ext', 'libs', bodo), (
    'get_str_arr_str_length', 'str_arr_ext', 'libs', bodo), (
    'parse_datetime_str', 'pd_timestamp_ext', 'hiframes', bodo), (
    'integer_to_dt64', 'pd_timestamp_ext', 'hiframes', bodo), (
    'dt64_to_integer', 'pd_timestamp_ext', 'hiframes', bodo), (
    'timedelta64_to_integer', 'pd_timestamp_ext', 'hiframes', bodo), (
    'integer_to_timedelta64', 'pd_timestamp_ext', 'hiframes', bodo), (
    'npy_datetimestruct_to_datetime', 'pd_timestamp_ext', 'hiframes', bodo),
    ('isna', 'array_kernels', 'libs', bodo), ('copy',), (
    'from_iterable_impl', 'typing', 'utils', bodo), ('chain', itertools), (
    'groupby',), ('rolling',), (pd.CategoricalDtype,), (bodo.hiframes.
    pd_categorical_ext.get_code_for_value,), ('asarray', np), ('int32', np),
    ('int64', np), ('float64', np), ('float32', np), ('bool_', np), ('full',
    np), ('round', np), ('isnan', np), ('isnat', np), ('internal_prange',
    'parfor', numba), ('internal_prange', 'parfor', 'parfors', numba), (
    'empty_inferred', 'ndarray', 'unsafe', numba), ('_slice_span',
    'unicode', numba), ('_normalize_slice', 'unicode', numba), (
    'init_session_builder', 'pyspark_ext', 'libs', bodo), ('init_session',
    'pyspark_ext', 'libs', bodo), ('init_spark_df', 'pyspark_ext', 'libs',
    bodo), ('h5size', 'h5_api', 'io', bodo), ('pre_alloc_struct_array',
    'struct_arr_ext', 'libs', bodo), (bodo.libs.struct_arr_ext.
    pre_alloc_struct_array,), ('pre_alloc_tuple_array', 'tuple_arr_ext',
    'libs', bodo), (bodo.libs.tuple_arr_ext.pre_alloc_tuple_array,), (
    'pre_alloc_array_item_array', 'array_item_arr_ext', 'libs', bodo), (
    bodo.libs.array_item_arr_ext.pre_alloc_array_item_array,), (
    'dist_reduce', 'distributed_api', 'libs', bodo), (bodo.libs.
    distributed_api.dist_reduce,), ('pre_alloc_string_array', 'str_arr_ext',
    'libs', bodo), (bodo.libs.str_arr_ext.pre_alloc_string_array,), (
    'pre_alloc_binary_array', 'binary_arr_ext', 'libs', bodo), (bodo.libs.
    binary_arr_ext.pre_alloc_binary_array,), ('pre_alloc_map_array',
    'map_arr_ext', 'libs', bodo), (bodo.libs.map_arr_ext.
    pre_alloc_map_array,), ('prange', bodo), (bodo.prange,), ('objmode',
    bodo), (bodo.objmode,), ('get_label_dict_from_categories',
    'pd_categorial_ext', 'hiframes', bodo), (
    'get_label_dict_from_categories_no_duplicates', 'pd_categorial_ext',
    'hiframes', bodo), ('build_nullable_tuple', 'nullable_tuple_ext',
    'libs', bodo)}


def remove_hiframes(rhs, lives, call_list):
    djw__invot = tuple(call_list)
    if djw__invot in no_side_effect_call_tuples:
        return True
    if len(call_list) == 4 and call_list[1:] == ['conversion', 'utils', bodo]:
        return True
    if isinstance(call_list[-1], pytypes.ModuleType) and call_list[-1
        ].__name__ == 'bodosql':
        return True
    if len(call_list) == 2 and call_list[0] == 'copy':
        return True
    if call_list == ['h5read', 'h5_api', 'io', bodo] and rhs.args[5
        ].name not in lives:
        return True
    if call_list == ['move_str_binary_arr_payload', 'str_arr_ext', 'libs', bodo
        ] and rhs.args[0].name not in lives:
        return True
    if call_list == ['setna', 'array_kernels', 'libs', bodo] and rhs.args[0
        ].name not in lives:
        return True
    if call_list == ['set_table_data', 'table', 'hiframes', bodo] and rhs.args[
        0].name not in lives:
        return True
    if len(djw__invot) == 1 and tuple in getattr(djw__invot[0], '__mro__', ()):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=True):
    oftjr__fxzie = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
        'math': math}
    if extra_globals is not None:
        oftjr__fxzie.update(extra_globals)
    if not replace_globals:
        oftjr__fxzie = func.__globals__
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, oftjr__fxzie, typingctx=
            typing_info.typingctx, targetctx=typing_info.targetctx,
            arg_typs=tuple(typing_info.typemap[wmny__ptb.name] for
            wmny__ptb in args), typemap=typing_info.typemap, calltypes=
            typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, oftjr__fxzie)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        pcp__sngqt = tuple(typing_info.typemap[wmny__ptb.name] for
            wmny__ptb in args)
        tolrg__huisk = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, pcp__sngqt, {}, {}, flags)
        tolrg__huisk.run()
    gvxad__ljftw = f_ir.blocks.popitem()[1]
    replace_arg_nodes(gvxad__ljftw, args)
    ens__mrz = gvxad__ljftw.body[:-2]
    update_locs(ens__mrz[len(args):], loc)
    for stmt in ens__mrz[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        qmndj__dmf = gvxad__ljftw.body[-2]
        assert is_assign(qmndj__dmf) and is_expr(qmndj__dmf.value, 'cast')
        moth__tgba = qmndj__dmf.value.value
        ens__mrz.append(ir.Assign(moth__tgba, ret_var, loc))
    return ens__mrz


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for focz__iphyu in stmt.list_vars():
            focz__iphyu.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        uqfd__ednc = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        ymlx__sfqk, reqwz__kmbd = uqfd__ednc(stmt)
        return reqwz__kmbd
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        djcr__qzge = get_const_value_inner(func_ir, var, arg_types, typemap,
            file_info=file_info)
        if isinstance(djcr__qzge, ir.UndefinedType):
            woye__woqr = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{woye__woqr}' is not defined", loc=loc)
    except GuardException as enbje__raic:
        raise BodoError(err_msg, loc=loc)
    return djcr__qzge


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    dnael__horh = get_definition(func_ir, var)
    roqd__fplhd = None
    if typemap is not None:
        roqd__fplhd = typemap.get(var.name, None)
    if isinstance(dnael__horh, ir.Arg) and arg_types is not None:
        roqd__fplhd = arg_types[dnael__horh.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(roqd__fplhd):
        return get_literal_value(roqd__fplhd)
    if isinstance(dnael__horh, (ir.Const, ir.Global, ir.FreeVar)):
        djcr__qzge = dnael__horh.value
        return djcr__qzge
    if literalize_args and isinstance(dnael__horh, ir.Arg
        ) and can_literalize_type(roqd__fplhd, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({dnael__horh.index}, loc=
            var.loc, file_infos={dnael__horh.index: file_info} if file_info
             is not None else None)
    if is_expr(dnael__horh, 'binop'):
        if file_info and dnael__horh.fn == operator.add:
            try:
                exgj__qcxq = get_const_value_inner(func_ir, dnael__horh.lhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(exgj__qcxq, True)
                uamz__ujwgx = get_const_value_inner(func_ir, dnael__horh.
                    rhs, arg_types, typemap, updated_containers, file_info)
                return dnael__horh.fn(exgj__qcxq, uamz__ujwgx)
            except (GuardException, BodoConstUpdatedError) as enbje__raic:
                pass
            try:
                uamz__ujwgx = get_const_value_inner(func_ir, dnael__horh.
                    rhs, arg_types, typemap, updated_containers,
                    literalize_args=False)
                file_info.set_concat(uamz__ujwgx, False)
                exgj__qcxq = get_const_value_inner(func_ir, dnael__horh.lhs,
                    arg_types, typemap, updated_containers, file_info)
                return dnael__horh.fn(exgj__qcxq, uamz__ujwgx)
            except (GuardException, BodoConstUpdatedError) as enbje__raic:
                pass
        exgj__qcxq = get_const_value_inner(func_ir, dnael__horh.lhs,
            arg_types, typemap, updated_containers)
        uamz__ujwgx = get_const_value_inner(func_ir, dnael__horh.rhs,
            arg_types, typemap, updated_containers)
        return dnael__horh.fn(exgj__qcxq, uamz__ujwgx)
    if is_expr(dnael__horh, 'unary'):
        djcr__qzge = get_const_value_inner(func_ir, dnael__horh.value,
            arg_types, typemap, updated_containers)
        return dnael__horh.fn(djcr__qzge)
    if is_expr(dnael__horh, 'getattr') and typemap:
        tfmq__giyre = typemap.get(dnael__horh.value.name, None)
        if isinstance(tfmq__giyre, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and dnael__horh.attr == 'columns':
            return pd.Index(tfmq__giyre.columns)
        if isinstance(tfmq__giyre, types.SliceType):
            kebo__nueio = get_definition(func_ir, dnael__horh.value)
            require(is_call(kebo__nueio))
            gcj__rvz = find_callname(func_ir, kebo__nueio)
            tsoq__lzelg = False
            if gcj__rvz == ('_normalize_slice', 'numba.cpython.unicode'):
                require(dnael__horh.attr in ('start', 'step'))
                kebo__nueio = get_definition(func_ir, kebo__nueio.args[0])
                tsoq__lzelg = True
            require(find_callname(func_ir, kebo__nueio) == ('slice',
                'builtins'))
            if len(kebo__nueio.args) == 1:
                if dnael__horh.attr == 'start':
                    return 0
                if dnael__horh.attr == 'step':
                    return 1
                require(dnael__horh.attr == 'stop')
                return get_const_value_inner(func_ir, kebo__nueio.args[0],
                    arg_types, typemap, updated_containers)
            if dnael__horh.attr == 'start':
                djcr__qzge = get_const_value_inner(func_ir, kebo__nueio.
                    args[0], arg_types, typemap, updated_containers)
                if djcr__qzge is None:
                    djcr__qzge = 0
                if tsoq__lzelg:
                    require(djcr__qzge == 0)
                return djcr__qzge
            if dnael__horh.attr == 'stop':
                assert not tsoq__lzelg
                return get_const_value_inner(func_ir, kebo__nueio.args[1],
                    arg_types, typemap, updated_containers)
            require(dnael__horh.attr == 'step')
            if len(kebo__nueio.args) == 2:
                return 1
            else:
                djcr__qzge = get_const_value_inner(func_ir, kebo__nueio.
                    args[2], arg_types, typemap, updated_containers)
                if djcr__qzge is None:
                    djcr__qzge = 1
                if tsoq__lzelg:
                    require(djcr__qzge == 1)
                return djcr__qzge
    if is_expr(dnael__horh, 'getattr'):
        return getattr(get_const_value_inner(func_ir, dnael__horh.value,
            arg_types, typemap, updated_containers), dnael__horh.attr)
    if is_expr(dnael__horh, 'getitem'):
        value = get_const_value_inner(func_ir, dnael__horh.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, dnael__horh.index, arg_types,
            typemap, updated_containers)
        return value[index]
    iklml__ntf = guard(find_callname, func_ir, dnael__horh, typemap)
    if iklml__ntf is not None and len(iklml__ntf) == 2 and iklml__ntf[0
        ] == 'keys' and isinstance(iklml__ntf[1], ir.Var):
        yun__zyod = dnael__horh.func
        dnael__horh = get_definition(func_ir, iklml__ntf[1])
        eouk__jranw = iklml__ntf[1].name
        if updated_containers and eouk__jranw in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                eouk__jranw, updated_containers[eouk__jranw]))
        require(is_expr(dnael__horh, 'build_map'))
        vals = [focz__iphyu[0] for focz__iphyu in dnael__horh.items]
        joi__dne = guard(get_definition, func_ir, yun__zyod)
        assert isinstance(joi__dne, ir.Expr) and joi__dne.attr == 'keys'
        joi__dne.attr = 'copy'
        return [get_const_value_inner(func_ir, focz__iphyu, arg_types,
            typemap, updated_containers) for focz__iphyu in vals]
    if is_expr(dnael__horh, 'build_map'):
        return {get_const_value_inner(func_ir, focz__iphyu[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            focz__iphyu[1], arg_types, typemap, updated_containers) for
            focz__iphyu in dnael__horh.items}
    if is_expr(dnael__horh, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, focz__iphyu, arg_types,
            typemap, updated_containers) for focz__iphyu in dnael__horh.items)
    if is_expr(dnael__horh, 'build_list'):
        return [get_const_value_inner(func_ir, focz__iphyu, arg_types,
            typemap, updated_containers) for focz__iphyu in dnael__horh.items]
    if is_expr(dnael__horh, 'build_set'):
        return {get_const_value_inner(func_ir, focz__iphyu, arg_types,
            typemap, updated_containers) for focz__iphyu in dnael__horh.items}
    if iklml__ntf == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, dnael__horh.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if iklml__ntf == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, dnael__horh.args[0],
            arg_types, typemap, updated_containers))
    if iklml__ntf == ('range', 'builtins') and len(dnael__horh.args) == 1:
        return range(get_const_value_inner(func_ir, dnael__horh.args[0],
            arg_types, typemap, updated_containers))
    if iklml__ntf == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, focz__iphyu,
            arg_types, typemap, updated_containers) for focz__iphyu in
            dnael__horh.args))
    if iklml__ntf == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, dnael__horh.args[0],
            arg_types, typemap, updated_containers))
    if iklml__ntf == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, dnael__horh.args[0],
            arg_types, typemap, updated_containers))
    if iklml__ntf == ('format', 'builtins'):
        wmny__ptb = get_const_value_inner(func_ir, dnael__horh.args[0],
            arg_types, typemap, updated_containers)
        dfyh__odrk = get_const_value_inner(func_ir, dnael__horh.args[1],
            arg_types, typemap, updated_containers) if len(dnael__horh.args
            ) > 1 else ''
        return format(wmny__ptb, dfyh__odrk)
    if iklml__ntf in (('init_binary_str_index',
        'bodo.hiframes.pd_index_ext'), ('init_numeric_index',
        'bodo.hiframes.pd_index_ext'), ('init_categorical_index',
        'bodo.hiframes.pd_index_ext'), ('init_datetime_index',
        'bodo.hiframes.pd_index_ext'), ('init_timedelta_index',
        'bodo.hiframes.pd_index_ext'), ('init_heter_index',
        'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, dnael__horh.args[0],
            arg_types, typemap, updated_containers))
    if iklml__ntf == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, dnael__horh.args[0],
            arg_types, typemap, updated_containers))
    if iklml__ntf == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, dnael__horh.
            args[0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, dnael__horh.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            dnael__horh.args[2], arg_types, typemap, updated_containers))
    if iklml__ntf == ('len', 'builtins') and typemap and isinstance(typemap
        .get(dnael__horh.args[0].name, None), types.BaseTuple):
        return len(typemap[dnael__horh.args[0].name])
    if iklml__ntf == ('len', 'builtins'):
        odppn__avh = guard(get_definition, func_ir, dnael__horh.args[0])
        if isinstance(odppn__avh, ir.Expr) and odppn__avh.op in ('build_tuple',
            'build_list', 'build_set', 'build_map'):
            return len(odppn__avh.items)
        return len(get_const_value_inner(func_ir, dnael__horh.args[0],
            arg_types, typemap, updated_containers))
    if iklml__ntf == ('CategoricalDtype', 'pandas'):
        kws = dict(dnael__horh.kws)
        qzwcu__gnze = get_call_expr_arg('CategoricalDtype', dnael__horh.
            args, kws, 0, 'categories', '')
        qyyzw__ihl = get_call_expr_arg('CategoricalDtype', dnael__horh.args,
            kws, 1, 'ordered', False)
        if qyyzw__ihl is not False:
            qyyzw__ihl = get_const_value_inner(func_ir, qyyzw__ihl,
                arg_types, typemap, updated_containers)
        if qzwcu__gnze == '':
            qzwcu__gnze = None
        else:
            qzwcu__gnze = get_const_value_inner(func_ir, qzwcu__gnze,
                arg_types, typemap, updated_containers)
        return pd.CategoricalDtype(qzwcu__gnze, qyyzw__ihl)
    if iklml__ntf == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, dnael__horh.args[0],
            arg_types, typemap, updated_containers))
    if iklml__ntf is not None and len(iklml__ntf) == 2 and iklml__ntf[1
        ] == 'pandas' and iklml__ntf[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, iklml__ntf[0])()
    if iklml__ntf is not None and len(iklml__ntf) == 2 and isinstance(
        iklml__ntf[1], ir.Var):
        djcr__qzge = get_const_value_inner(func_ir, iklml__ntf[1],
            arg_types, typemap, updated_containers)
        args = [get_const_value_inner(func_ir, focz__iphyu, arg_types,
            typemap, updated_containers) for focz__iphyu in dnael__horh.args]
        kws = {jcvlp__himi[0]: get_const_value_inner(func_ir, jcvlp__himi[1
            ], arg_types, typemap, updated_containers) for jcvlp__himi in
            dnael__horh.kws}
        return getattr(djcr__qzge, iklml__ntf[0])(*args, **kws)
    if iklml__ntf is not None and len(iklml__ntf) == 2 and iklml__ntf[1
        ] == 'bodo' and iklml__ntf[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, focz__iphyu, arg_types,
            typemap, updated_containers) for focz__iphyu in dnael__horh.args)
        kwargs = {woye__woqr: get_const_value_inner(func_ir, focz__iphyu,
            arg_types, typemap, updated_containers) for woye__woqr,
            focz__iphyu in dict(dnael__horh.kws).items()}
        return getattr(bodo, iklml__ntf[0])(*args, **kwargs)
    if is_call(dnael__horh) and typemap and isinstance(typemap.get(
        dnael__horh.func.name, None), types.Dispatcher):
        py_func = typemap[dnael__horh.func.name].dispatcher.py_func
        require(dnael__horh.vararg is None)
        args = tuple(get_const_value_inner(func_ir, focz__iphyu, arg_types,
            typemap, updated_containers) for focz__iphyu in dnael__horh.args)
        kwargs = {woye__woqr: get_const_value_inner(func_ir, focz__iphyu,
            arg_types, typemap, updated_containers) for woye__woqr,
            focz__iphyu in dict(dnael__horh.kws).items()}
        arg_types = tuple(bodo.typeof(focz__iphyu) for focz__iphyu in args)
        kw_types = {evvk__vncf: bodo.typeof(focz__iphyu) for evvk__vncf,
            focz__iphyu in kwargs.items()}
        require(_func_is_pure(py_func, arg_types, kw_types))
        return py_func(*args, **kwargs)
    raise GuardException('Constant value not found')


def _func_is_pure(py_func, arg_types, kw_types):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    from bodo.hiframes.pd_series_ext import SeriesType
    from bodo.ir.csv_ext import CsvReader
    from bodo.ir.json_ext import JsonReader
    from bodo.ir.parquet_ext import ParquetReader
    from bodo.ir.sql_ext import SqlReader
    f_ir, typemap, plm__wfm, plm__wfm = bodo.compiler.get_func_type_info(
        py_func, arg_types, kw_types)
    for block in f_ir.blocks.values():
        for stmt in block.body:
            if isinstance(stmt, ir.Print):
                return False
            if isinstance(stmt, (CsvReader, JsonReader, ParquetReader,
                SqlReader)):
                return False
            if is_setitem(stmt) and isinstance(guard(get_definition, f_ir,
                stmt.target), ir.Arg):
                return False
            if is_assign(stmt):
                rhs = stmt.value
                if isinstance(rhs, ir.Yield):
                    return False
                if is_call(rhs):
                    yhca__qhadl = guard(get_definition, f_ir, rhs.func)
                    if isinstance(yhca__qhadl, ir.Const) and isinstance(
                        yhca__qhadl.value, numba.core.dispatcher.
                        ObjModeLiftedWith):
                        return False
                    isae__hrvci = guard(find_callname, f_ir, rhs)
                    if isae__hrvci is None:
                        return False
                    func_name, hwc__cxau = isae__hrvci
                    if hwc__cxau == 'pandas' and func_name.startswith('read_'):
                        return False
                    if isae__hrvci in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if isae__hrvci == ('File', 'h5py'):
                        return False
                    if isinstance(hwc__cxau, ir.Var):
                        roqd__fplhd = typemap[hwc__cxau.name]
                        if isinstance(roqd__fplhd, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(roqd__fplhd, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(roqd__fplhd, bodo.LoggingLoggerType):
                            return False
                        if str(roqd__fplhd).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            hwc__cxau), ir.Arg)):
                            return False
                    if hwc__cxau in ('numpy.random', 'time', 'logging',
                        'matplotlib.pyplot'):
                        return False
    return True


def fold_argument_types(pysig, args, kws):

    def normal_handler(index, param, value):
        return value

    def default_handler(index, param, default):
        return types.Omitted(default)

    def stararg_handler(index, param, values):
        return types.StarArgTuple(values)
    args = fold_arguments(pysig, args, kws, normal_handler, default_handler,
        stararg_handler)
    return args


def get_const_func_output_type(func, arg_types, kw_types, typing_context,
    target_context, is_udf=True):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType, SeriesType
    py_func = None
    if isinstance(func, types.MakeFunctionLiteral):
        qgyd__lrdk = func.literal_value.code
        wrd__xobgp = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            wrd__xobgp = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(wrd__xobgp, qgyd__lrdk)
        fix_struct_return(f_ir)
        typemap, gqka__lihqv, grke__hcayn, plm__wfm = (numba.core.
            typed_passes.type_inference_stage(typing_context,
            target_context, f_ir, arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, grke__hcayn, gqka__lihqv = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, grke__hcayn, gqka__lihqv = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, grke__hcayn, gqka__lihqv = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    if is_udf and isinstance(gqka__lihqv, types.DictType):
        ntz__toqon = guard(get_struct_keynames, f_ir, typemap)
        if ntz__toqon is not None:
            gqka__lihqv = StructType((gqka__lihqv.value_type,) * len(
                ntz__toqon), ntz__toqon)
    if is_udf and isinstance(gqka__lihqv, (SeriesType, HeterogeneousSeriesType)
        ):
        pkdl__gfk = numba.core.registry.cpu_target.typing_context
        ujd__ltbx = numba.core.registry.cpu_target.target_context
        yewpp__ghm = bodo.transforms.series_pass.SeriesPass(f_ir, pkdl__gfk,
            ujd__ltbx, typemap, grke__hcayn, {})
        yewpp__ghm.run()
        yewpp__ghm.run()
        yewpp__ghm.run()
        hnqz__qowk = compute_cfg_from_blocks(f_ir.blocks)
        rsmlz__mbsd = [guard(_get_const_series_info, f_ir.blocks[
            xkcr__hczvf], f_ir, typemap) for xkcr__hczvf in hnqz__qowk.
            exit_points() if isinstance(f_ir.blocks[xkcr__hczvf].body[-1],
            ir.Return)]
        if None in rsmlz__mbsd or len(pd.Series(rsmlz__mbsd).unique()) != 1:
            gqka__lihqv.const_info = None
        else:
            gqka__lihqv.const_info = rsmlz__mbsd[0]
    return gqka__lihqv


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    wwheg__wjul = block.body[-1].value
    yiyuh__iitau = get_definition(f_ir, wwheg__wjul)
    require(is_expr(yiyuh__iitau, 'cast'))
    yiyuh__iitau = get_definition(f_ir, yiyuh__iitau.value)
    require(is_call(yiyuh__iitau) and find_callname(f_ir, yiyuh__iitau) ==
        ('init_series', 'bodo.hiframes.pd_series_ext'))
    fexmb__iqft = yiyuh__iitau.args[1]
    tjcr__kxie = tuple(get_const_value_inner(f_ir, fexmb__iqft, typemap=
        typemap))
    if isinstance(typemap[wwheg__wjul.name], HeterogeneousSeriesType):
        return len(typemap[wwheg__wjul.name].data), tjcr__kxie
    iyoon__sjsnh = yiyuh__iitau.args[0]
    xkcgl__nuz = get_definition(f_ir, iyoon__sjsnh)
    func_name, mfum__gjsh = find_callname(f_ir, xkcgl__nuz)
    if is_call(xkcgl__nuz) and bodo.utils.utils.is_alloc_callname(func_name,
        mfum__gjsh):
        dvx__fjd = xkcgl__nuz.args[0]
        strw__mcs = get_const_value_inner(f_ir, dvx__fjd, typemap=typemap)
        return strw__mcs, tjcr__kxie
    if is_call(xkcgl__nuz) and find_callname(f_ir, xkcgl__nuz) in [(
        'asarray', 'numpy'), ('str_arr_from_sequence', 'bodo.libs.str_arr_ext')
        ]:
        iyoon__sjsnh = xkcgl__nuz.args[0]
        xkcgl__nuz = get_definition(f_ir, iyoon__sjsnh)
    require(is_expr(xkcgl__nuz, 'build_tuple') or is_expr(xkcgl__nuz,
        'build_list'))
    return len(xkcgl__nuz.items), tjcr__kxie


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    pomly__aisv = []
    sbuco__hgxob = []
    values = []
    for evvk__vncf, focz__iphyu in build_map.items:
        ygufi__zamna = find_const(f_ir, evvk__vncf)
        require(isinstance(ygufi__zamna, str))
        sbuco__hgxob.append(ygufi__zamna)
        pomly__aisv.append(evvk__vncf)
        values.append(focz__iphyu)
    fup__qda = ir.Var(scope, mk_unique_var('val_tup'), loc)
    bqgj__clpr = ir.Assign(ir.Expr.build_tuple(values, loc), fup__qda, loc)
    f_ir._definitions[fup__qda.name] = [bqgj__clpr.value]
    xsykw__xdv = ir.Var(scope, mk_unique_var('key_tup'), loc)
    sjwon__yskdh = ir.Assign(ir.Expr.build_tuple(pomly__aisv, loc),
        xsykw__xdv, loc)
    f_ir._definitions[xsykw__xdv.name] = [sjwon__yskdh.value]
    if typemap is not None:
        typemap[fup__qda.name] = types.Tuple([typemap[focz__iphyu.name] for
            focz__iphyu in values])
        typemap[xsykw__xdv.name] = types.Tuple([typemap[focz__iphyu.name] for
            focz__iphyu in pomly__aisv])
    return sbuco__hgxob, fup__qda, bqgj__clpr, xsykw__xdv, sjwon__yskdh


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    wwp__jlrkd = block.body[-1].value
    kfxon__egy = guard(get_definition, f_ir, wwp__jlrkd)
    require(is_expr(kfxon__egy, 'cast'))
    yiyuh__iitau = guard(get_definition, f_ir, kfxon__egy.value)
    require(is_expr(yiyuh__iitau, 'build_map'))
    require(len(yiyuh__iitau.items) > 0)
    loc = block.loc
    scope = block.scope
    sbuco__hgxob, fup__qda, bqgj__clpr, xsykw__xdv, sjwon__yskdh = (
        extract_keyvals_from_struct_map(f_ir, yiyuh__iitau, loc, scope))
    eymf__crzce = ir.Var(scope, mk_unique_var('conv_call'), loc)
    sur__smwc = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), eymf__crzce, loc)
    f_ir._definitions[eymf__crzce.name] = [sur__smwc.value]
    eabrm__mqpzs = ir.Var(scope, mk_unique_var('struct_val'), loc)
    lrwmq__vxbb = ir.Assign(ir.Expr.call(eymf__crzce, [fup__qda, xsykw__xdv
        ], {}, loc), eabrm__mqpzs, loc)
    f_ir._definitions[eabrm__mqpzs.name] = [lrwmq__vxbb.value]
    kfxon__egy.value = eabrm__mqpzs
    yiyuh__iitau.items = [(evvk__vncf, evvk__vncf) for evvk__vncf, plm__wfm in
        yiyuh__iitau.items]
    block.body = block.body[:-2] + [bqgj__clpr, sjwon__yskdh, sur__smwc,
        lrwmq__vxbb] + block.body[-2:]
    return tuple(sbuco__hgxob)


def get_struct_keynames(f_ir, typemap):
    hnqz__qowk = compute_cfg_from_blocks(f_ir.blocks)
    bfdg__oldmn = list(hnqz__qowk.exit_points())[0]
    block = f_ir.blocks[bfdg__oldmn]
    require(isinstance(block.body[-1], ir.Return))
    wwp__jlrkd = block.body[-1].value
    kfxon__egy = guard(get_definition, f_ir, wwp__jlrkd)
    require(is_expr(kfxon__egy, 'cast'))
    yiyuh__iitau = guard(get_definition, f_ir, kfxon__egy.value)
    require(is_call(yiyuh__iitau) and find_callname(f_ir, yiyuh__iitau) ==
        ('struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[yiyuh__iitau.args[1].name])


def fix_struct_return(f_ir):
    ytvh__haolm = None
    hnqz__qowk = compute_cfg_from_blocks(f_ir.blocks)
    for bfdg__oldmn in hnqz__qowk.exit_points():
        ytvh__haolm = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            bfdg__oldmn], bfdg__oldmn)
    return ytvh__haolm


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    cqimh__ryy = ir.Block(ir.Scope(None, loc), loc)
    cqimh__ryy.body = node_list
    build_definitions({(0): cqimh__ryy}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(focz__iphyu) for focz__iphyu in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    pukz__szxd = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(pukz__szxd, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for juvqw__ivbhp in range(len(vals) - 1, -1, -1):
        focz__iphyu = vals[juvqw__ivbhp]
        if isinstance(focz__iphyu, str) and focz__iphyu.startswith(
            NESTED_TUP_SENTINEL):
            rae__ohvir = int(focz__iphyu[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:juvqw__ivbhp]) + (
                tuple(vals[juvqw__ivbhp + 1:juvqw__ivbhp + rae__ohvir + 1])
                ,) + tuple(vals[juvqw__ivbhp + rae__ohvir + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    wmny__ptb = None
    if len(args) > arg_no and arg_no >= 0:
        wmny__ptb = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        wmny__ptb = kws[arg_name]
    if wmny__ptb is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return wmny__ptb


def set_call_expr_arg(var, args, kws, arg_no, arg_name, add_if_missing=False):
    if len(args) > arg_no:
        args[arg_no] = var
    elif add_if_missing or arg_name in kws:
        kws[arg_name] = var
    else:
        raise BodoError('cannot set call argument since does not exist')


def avoid_udf_inline(py_func, arg_types, kw_types):
    from bodo.hiframes.pd_dataframe_ext import DataFrameType
    f_ir = numba.core.compiler.run_frontend(py_func, inline_closures=True)
    if '_bodo_inline' in kw_types and is_overload_constant_bool(kw_types[
        '_bodo_inline']):
        return not get_overload_const_bool(kw_types['_bodo_inline'])
    if any(isinstance(t, DataFrameType) for t in arg_types + tuple(kw_types
        .values())):
        return True
    for block in f_ir.blocks.values():
        if isinstance(block.body[-1], (ir.Raise, ir.StaticRaise)):
            return True
        for stmt in block.body:
            if isinstance(stmt, ir.EnterWith):
                return True
    return False


def replace_func(pass_info, func, args, const=False, pre_nodes=None,
    extra_globals=None, pysig=None, kws=None, inline_bodo_calls=False,
    run_full_pipeline=False):
    oftjr__fxzie = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        oftjr__fxzie.update(extra_globals)
    func.__globals__.update(oftjr__fxzie)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            kvbbk__panq = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[kvbbk__panq.name] = types.literal(default)
            except:
                pass_info.typemap[kvbbk__panq.name] = numba.typeof(default)
            xreua__nwdzk = ir.Assign(ir.Const(default, loc), kvbbk__panq, loc)
            pre_nodes.append(xreua__nwdzk)
            return kvbbk__panq
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    pcp__sngqt = tuple(pass_info.typemap[focz__iphyu.name] for focz__iphyu in
        args)
    if const:
        cjkwf__znpi = []
        for juvqw__ivbhp, wmny__ptb in enumerate(args):
            djcr__qzge = guard(find_const, pass_info.func_ir, wmny__ptb)
            if djcr__qzge:
                cjkwf__znpi.append(types.literal(djcr__qzge))
            else:
                cjkwf__znpi.append(pcp__sngqt[juvqw__ivbhp])
        pcp__sngqt = tuple(cjkwf__znpi)
    return ReplaceFunc(func, pcp__sngqt, args, oftjr__fxzie,
        inline_bodo_calls, run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(haosl__ovlp) for haosl__ovlp in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        gqcml__bny = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {gqcml__bny} = 0\n', (gqcml__bny,)
    if isinstance(t, ArrayItemArrayType):
        hkd__ftpu, kejd__eack = gen_init_varsize_alloc_sizes(t.dtype)
        gqcml__bny = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {gqcml__bny} = 0\n' + hkd__ftpu, (gqcml__bny,) + kejd__eack
    return '', ()


def gen_varsize_item_sizes(t, item, var_names):
    if t == string_array_type:
        return '    {} += bodo.libs.str_arr_ext.get_utf8_size({})\n'.format(
            var_names[0], item)
    if isinstance(t, ArrayItemArrayType):
        return '    {} += len({})\n'.format(var_names[0], item
            ) + gen_varsize_array_counts(t.dtype, item, var_names[1:])
    return ''


def gen_varsize_array_counts(t, item, var_names):
    if t == string_array_type:
        return ('    {} += bodo.libs.str_arr_ext.get_num_total_chars({})\n'
            .format(var_names[0], item))
    return ''


def get_type_alloc_counts(t):
    if isinstance(t, (StructArrayType, TupleArrayType)):
        return 1 + sum(get_type_alloc_counts(haosl__ovlp.dtype) for
            haosl__ovlp in t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(haosl__ovlp) for haosl__ovlp in t.data
            )
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(haosl__ovlp) for haosl__ovlp in t.
            types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    cuqft__rrqqa = typing_context.resolve_getattr(obj_dtype, func_name)
    if cuqft__rrqqa is None:
        eclz__doalc = types.misc.Module(np)
        try:
            cuqft__rrqqa = typing_context.resolve_getattr(eclz__doalc,
                func_name)
        except AttributeError as enbje__raic:
            cuqft__rrqqa = None
        if cuqft__rrqqa is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return cuqft__rrqqa


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    cuqft__rrqqa = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(cuqft__rrqqa, types.BoundFunction):
        if axis is not None:
            omrke__hva = cuqft__rrqqa.get_call_type(typing_context, (), {
                'axis': axis})
        else:
            omrke__hva = cuqft__rrqqa.get_call_type(typing_context, (), {})
        return omrke__hva.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(cuqft__rrqqa):
            omrke__hva = cuqft__rrqqa.get_call_type(typing_context, (
                obj_dtype,), {})
            return omrke__hva.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    cuqft__rrqqa = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(cuqft__rrqqa, types.BoundFunction):
        axau__aawcz = cuqft__rrqqa.template
        if axis is not None:
            return axau__aawcz._overload_func(obj_dtype, axis=axis)
        else:
            return axau__aawcz._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    vezv__qan = get_definition(func_ir, dict_var)
    require(isinstance(vezv__qan, ir.Expr))
    require(vezv__qan.op == 'build_map')
    lqiv__ily = vezv__qan.items
    pomly__aisv = []
    values = []
    amnx__btlgx = False
    for juvqw__ivbhp in range(len(lqiv__ily)):
        ekqt__merai, value = lqiv__ily[juvqw__ivbhp]
        try:
            cjarg__xsh = get_const_value_inner(func_ir, ekqt__merai,
                arg_types, typemap, updated_containers)
            pomly__aisv.append(cjarg__xsh)
            values.append(value)
        except GuardException as enbje__raic:
            require_const_map[ekqt__merai] = label
            amnx__btlgx = True
    if amnx__btlgx:
        raise GuardException
    return pomly__aisv, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        pomly__aisv = tuple(get_const_value_inner(func_ir, t[0], args) for
            t in build_map.items)
    except GuardException as enbje__raic:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in pomly__aisv):
        raise BodoError(err_msg, loc)
    return pomly__aisv


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    pomly__aisv = _get_const_keys_from_dict(args, func_ir, build_map,
        err_msg, loc)
    lige__nrua = []
    lumfm__zss = [bodo.transforms.typing_pass._create_const_var(evvk__vncf,
        'dict_key', scope, loc, lige__nrua) for evvk__vncf in pomly__aisv]
    yci__azte = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        nhpx__wug = ir.Var(scope, mk_unique_var('sentinel'), loc)
        ftpm__ajad = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        lige__nrua.append(ir.Assign(ir.Const('__bodo_tup', loc), nhpx__wug,
            loc))
        pawvp__dkccg = [nhpx__wug] + lumfm__zss + yci__azte
        lige__nrua.append(ir.Assign(ir.Expr.build_tuple(pawvp__dkccg, loc),
            ftpm__ajad, loc))
        return (ftpm__ajad,), lige__nrua
    else:
        ixkb__azhu = ir.Var(scope, mk_unique_var('values_tup'), loc)
        abcye__zfdqd = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        lige__nrua.append(ir.Assign(ir.Expr.build_tuple(yci__azte, loc),
            ixkb__azhu, loc))
        lige__nrua.append(ir.Assign(ir.Expr.build_tuple(lumfm__zss, loc),
            abcye__zfdqd, loc))
        return (ixkb__azhu, abcye__zfdqd), lige__nrua
