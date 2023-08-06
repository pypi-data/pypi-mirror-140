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
    lqs__nognh = tuple(call_list)
    if lqs__nognh in no_side_effect_call_tuples:
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
    if len(lqs__nognh) == 1 and tuple in getattr(lqs__nognh[0], '__mro__', ()):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=True):
    thntb__mrwca = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd,
        'math': math}
    if extra_globals is not None:
        thntb__mrwca.update(extra_globals)
    if not replace_globals:
        thntb__mrwca = func.__globals__
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, thntb__mrwca, typingctx=
            typing_info.typingctx, targetctx=typing_info.targetctx,
            arg_typs=tuple(typing_info.typemap[jsn__xrj.name] for jsn__xrj in
            args), typemap=typing_info.typemap, calltypes=typing_info.calltypes
            )
    else:
        f_ir = compile_to_numba_ir(func, thntb__mrwca)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        klk__kgbuz = tuple(typing_info.typemap[jsn__xrj.name] for jsn__xrj in
            args)
        vvv__cmro = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, klk__kgbuz, {}, {}, flags)
        vvv__cmro.run()
    psb__iunt = f_ir.blocks.popitem()[1]
    replace_arg_nodes(psb__iunt, args)
    motrd__hfnom = psb__iunt.body[:-2]
    update_locs(motrd__hfnom[len(args):], loc)
    for stmt in motrd__hfnom[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        fmgf__kznpq = psb__iunt.body[-2]
        assert is_assign(fmgf__kznpq) and is_expr(fmgf__kznpq.value, 'cast')
        qxths__ixmnf = fmgf__kznpq.value.value
        motrd__hfnom.append(ir.Assign(qxths__ixmnf, ret_var, loc))
    return motrd__hfnom


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for zwgfv__ludq in stmt.list_vars():
            zwgfv__ludq.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        wevmp__etpbb = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        mhnw__azgzw, mzri__rkcba = wevmp__etpbb(stmt)
        return mzri__rkcba
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        thps__pmc = get_const_value_inner(func_ir, var, arg_types, typemap,
            file_info=file_info)
        if isinstance(thps__pmc, ir.UndefinedType):
            xhz__mgta = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{xhz__mgta}' is not defined", loc=loc)
    except GuardException as nbnp__xtsd:
        raise BodoError(err_msg, loc=loc)
    return thps__pmc


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    nvvx__lvvab = get_definition(func_ir, var)
    mxiy__ysmv = None
    if typemap is not None:
        mxiy__ysmv = typemap.get(var.name, None)
    if isinstance(nvvx__lvvab, ir.Arg) and arg_types is not None:
        mxiy__ysmv = arg_types[nvvx__lvvab.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(mxiy__ysmv):
        return get_literal_value(mxiy__ysmv)
    if isinstance(nvvx__lvvab, (ir.Const, ir.Global, ir.FreeVar)):
        thps__pmc = nvvx__lvvab.value
        return thps__pmc
    if literalize_args and isinstance(nvvx__lvvab, ir.Arg
        ) and can_literalize_type(mxiy__ysmv, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({nvvx__lvvab.index}, loc=
            var.loc, file_infos={nvvx__lvvab.index: file_info} if file_info
             is not None else None)
    if is_expr(nvvx__lvvab, 'binop'):
        if file_info and nvvx__lvvab.fn == operator.add:
            try:
                aaux__zzvm = get_const_value_inner(func_ir, nvvx__lvvab.lhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(aaux__zzvm, True)
                llbr__houq = get_const_value_inner(func_ir, nvvx__lvvab.rhs,
                    arg_types, typemap, updated_containers, file_info)
                return nvvx__lvvab.fn(aaux__zzvm, llbr__houq)
            except (GuardException, BodoConstUpdatedError) as nbnp__xtsd:
                pass
            try:
                llbr__houq = get_const_value_inner(func_ir, nvvx__lvvab.rhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(llbr__houq, False)
                aaux__zzvm = get_const_value_inner(func_ir, nvvx__lvvab.lhs,
                    arg_types, typemap, updated_containers, file_info)
                return nvvx__lvvab.fn(aaux__zzvm, llbr__houq)
            except (GuardException, BodoConstUpdatedError) as nbnp__xtsd:
                pass
        aaux__zzvm = get_const_value_inner(func_ir, nvvx__lvvab.lhs,
            arg_types, typemap, updated_containers)
        llbr__houq = get_const_value_inner(func_ir, nvvx__lvvab.rhs,
            arg_types, typemap, updated_containers)
        return nvvx__lvvab.fn(aaux__zzvm, llbr__houq)
    if is_expr(nvvx__lvvab, 'unary'):
        thps__pmc = get_const_value_inner(func_ir, nvvx__lvvab.value,
            arg_types, typemap, updated_containers)
        return nvvx__lvvab.fn(thps__pmc)
    if is_expr(nvvx__lvvab, 'getattr') and typemap:
        rwsoh__lrlcc = typemap.get(nvvx__lvvab.value.name, None)
        if isinstance(rwsoh__lrlcc, bodo.hiframes.pd_dataframe_ext.
            DataFrameType) and nvvx__lvvab.attr == 'columns':
            return pd.Index(rwsoh__lrlcc.columns)
        if isinstance(rwsoh__lrlcc, types.SliceType):
            jncwa__ztyhw = get_definition(func_ir, nvvx__lvvab.value)
            require(is_call(jncwa__ztyhw))
            kytxh__rizg = find_callname(func_ir, jncwa__ztyhw)
            hqre__zcizn = False
            if kytxh__rizg == ('_normalize_slice', 'numba.cpython.unicode'):
                require(nvvx__lvvab.attr in ('start', 'step'))
                jncwa__ztyhw = get_definition(func_ir, jncwa__ztyhw.args[0])
                hqre__zcizn = True
            require(find_callname(func_ir, jncwa__ztyhw) == ('slice',
                'builtins'))
            if len(jncwa__ztyhw.args) == 1:
                if nvvx__lvvab.attr == 'start':
                    return 0
                if nvvx__lvvab.attr == 'step':
                    return 1
                require(nvvx__lvvab.attr == 'stop')
                return get_const_value_inner(func_ir, jncwa__ztyhw.args[0],
                    arg_types, typemap, updated_containers)
            if nvvx__lvvab.attr == 'start':
                thps__pmc = get_const_value_inner(func_ir, jncwa__ztyhw.
                    args[0], arg_types, typemap, updated_containers)
                if thps__pmc is None:
                    thps__pmc = 0
                if hqre__zcizn:
                    require(thps__pmc == 0)
                return thps__pmc
            if nvvx__lvvab.attr == 'stop':
                assert not hqre__zcizn
                return get_const_value_inner(func_ir, jncwa__ztyhw.args[1],
                    arg_types, typemap, updated_containers)
            require(nvvx__lvvab.attr == 'step')
            if len(jncwa__ztyhw.args) == 2:
                return 1
            else:
                thps__pmc = get_const_value_inner(func_ir, jncwa__ztyhw.
                    args[2], arg_types, typemap, updated_containers)
                if thps__pmc is None:
                    thps__pmc = 1
                if hqre__zcizn:
                    require(thps__pmc == 1)
                return thps__pmc
    if is_expr(nvvx__lvvab, 'getattr'):
        return getattr(get_const_value_inner(func_ir, nvvx__lvvab.value,
            arg_types, typemap, updated_containers), nvvx__lvvab.attr)
    if is_expr(nvvx__lvvab, 'getitem'):
        value = get_const_value_inner(func_ir, nvvx__lvvab.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, nvvx__lvvab.index, arg_types,
            typemap, updated_containers)
        return value[index]
    dri__mxox = guard(find_callname, func_ir, nvvx__lvvab, typemap)
    if dri__mxox is not None and len(dri__mxox) == 2 and dri__mxox[0
        ] == 'keys' and isinstance(dri__mxox[1], ir.Var):
        xvqj__arjd = nvvx__lvvab.func
        nvvx__lvvab = get_definition(func_ir, dri__mxox[1])
        rwh__cbor = dri__mxox[1].name
        if updated_containers and rwh__cbor in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                rwh__cbor, updated_containers[rwh__cbor]))
        require(is_expr(nvvx__lvvab, 'build_map'))
        vals = [zwgfv__ludq[0] for zwgfv__ludq in nvvx__lvvab.items]
        czjvo__sru = guard(get_definition, func_ir, xvqj__arjd)
        assert isinstance(czjvo__sru, ir.Expr) and czjvo__sru.attr == 'keys'
        czjvo__sru.attr = 'copy'
        return [get_const_value_inner(func_ir, zwgfv__ludq, arg_types,
            typemap, updated_containers) for zwgfv__ludq in vals]
    if is_expr(nvvx__lvvab, 'build_map'):
        return {get_const_value_inner(func_ir, zwgfv__ludq[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            zwgfv__ludq[1], arg_types, typemap, updated_containers) for
            zwgfv__ludq in nvvx__lvvab.items}
    if is_expr(nvvx__lvvab, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, zwgfv__ludq, arg_types,
            typemap, updated_containers) for zwgfv__ludq in nvvx__lvvab.items)
    if is_expr(nvvx__lvvab, 'build_list'):
        return [get_const_value_inner(func_ir, zwgfv__ludq, arg_types,
            typemap, updated_containers) for zwgfv__ludq in nvvx__lvvab.items]
    if is_expr(nvvx__lvvab, 'build_set'):
        return {get_const_value_inner(func_ir, zwgfv__ludq, arg_types,
            typemap, updated_containers) for zwgfv__ludq in nvvx__lvvab.items}
    if dri__mxox == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, nvvx__lvvab.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if dri__mxox == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, nvvx__lvvab.args[0],
            arg_types, typemap, updated_containers))
    if dri__mxox == ('range', 'builtins') and len(nvvx__lvvab.args) == 1:
        return range(get_const_value_inner(func_ir, nvvx__lvvab.args[0],
            arg_types, typemap, updated_containers))
    if dri__mxox == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, zwgfv__ludq,
            arg_types, typemap, updated_containers) for zwgfv__ludq in
            nvvx__lvvab.args))
    if dri__mxox == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, nvvx__lvvab.args[0],
            arg_types, typemap, updated_containers))
    if dri__mxox == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, nvvx__lvvab.args[0],
            arg_types, typemap, updated_containers))
    if dri__mxox == ('format', 'builtins'):
        jsn__xrj = get_const_value_inner(func_ir, nvvx__lvvab.args[0],
            arg_types, typemap, updated_containers)
        zquvg__qng = get_const_value_inner(func_ir, nvvx__lvvab.args[1],
            arg_types, typemap, updated_containers) if len(nvvx__lvvab.args
            ) > 1 else ''
        return format(jsn__xrj, zquvg__qng)
    if dri__mxox in (('init_binary_str_index', 'bodo.hiframes.pd_index_ext'
        ), ('init_numeric_index', 'bodo.hiframes.pd_index_ext'), (
        'init_categorical_index', 'bodo.hiframes.pd_index_ext'), (
        'init_datetime_index', 'bodo.hiframes.pd_index_ext'), (
        'init_timedelta_index', 'bodo.hiframes.pd_index_ext'), (
        'init_heter_index', 'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, nvvx__lvvab.args[0],
            arg_types, typemap, updated_containers))
    if dri__mxox == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, nvvx__lvvab.args[0],
            arg_types, typemap, updated_containers))
    if dri__mxox == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, nvvx__lvvab.
            args[0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, nvvx__lvvab.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            nvvx__lvvab.args[2], arg_types, typemap, updated_containers))
    if dri__mxox == ('len', 'builtins') and typemap and isinstance(typemap.
        get(nvvx__lvvab.args[0].name, None), types.BaseTuple):
        return len(typemap[nvvx__lvvab.args[0].name])
    if dri__mxox == ('len', 'builtins'):
        pos__qfr = guard(get_definition, func_ir, nvvx__lvvab.args[0])
        if isinstance(pos__qfr, ir.Expr) and pos__qfr.op in ('build_tuple',
            'build_list', 'build_set', 'build_map'):
            return len(pos__qfr.items)
        return len(get_const_value_inner(func_ir, nvvx__lvvab.args[0],
            arg_types, typemap, updated_containers))
    if dri__mxox == ('CategoricalDtype', 'pandas'):
        kws = dict(nvvx__lvvab.kws)
        wlnx__srb = get_call_expr_arg('CategoricalDtype', nvvx__lvvab.args,
            kws, 0, 'categories', '')
        jlg__nydmn = get_call_expr_arg('CategoricalDtype', nvvx__lvvab.args,
            kws, 1, 'ordered', False)
        if jlg__nydmn is not False:
            jlg__nydmn = get_const_value_inner(func_ir, jlg__nydmn,
                arg_types, typemap, updated_containers)
        if wlnx__srb == '':
            wlnx__srb = None
        else:
            wlnx__srb = get_const_value_inner(func_ir, wlnx__srb, arg_types,
                typemap, updated_containers)
        return pd.CategoricalDtype(wlnx__srb, jlg__nydmn)
    if dri__mxox == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, nvvx__lvvab.args[0],
            arg_types, typemap, updated_containers))
    if dri__mxox is not None and len(dri__mxox) == 2 and dri__mxox[1
        ] == 'pandas' and dri__mxox[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, dri__mxox[0])()
    if dri__mxox is not None and len(dri__mxox) == 2 and isinstance(dri__mxox
        [1], ir.Var):
        thps__pmc = get_const_value_inner(func_ir, dri__mxox[1], arg_types,
            typemap, updated_containers)
        args = [get_const_value_inner(func_ir, zwgfv__ludq, arg_types,
            typemap, updated_containers) for zwgfv__ludq in nvvx__lvvab.args]
        kws = {vaocb__zch[0]: get_const_value_inner(func_ir, vaocb__zch[1],
            arg_types, typemap, updated_containers) for vaocb__zch in
            nvvx__lvvab.kws}
        return getattr(thps__pmc, dri__mxox[0])(*args, **kws)
    if dri__mxox is not None and len(dri__mxox) == 2 and dri__mxox[1
        ] == 'bodo' and dri__mxox[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, zwgfv__ludq, arg_types,
            typemap, updated_containers) for zwgfv__ludq in nvvx__lvvab.args)
        kwargs = {xhz__mgta: get_const_value_inner(func_ir, zwgfv__ludq,
            arg_types, typemap, updated_containers) for xhz__mgta,
            zwgfv__ludq in dict(nvvx__lvvab.kws).items()}
        return getattr(bodo, dri__mxox[0])(*args, **kwargs)
    if is_call(nvvx__lvvab) and typemap and isinstance(typemap.get(
        nvvx__lvvab.func.name, None), types.Dispatcher):
        py_func = typemap[nvvx__lvvab.func.name].dispatcher.py_func
        require(nvvx__lvvab.vararg is None)
        args = tuple(get_const_value_inner(func_ir, zwgfv__ludq, arg_types,
            typemap, updated_containers) for zwgfv__ludq in nvvx__lvvab.args)
        kwargs = {xhz__mgta: get_const_value_inner(func_ir, zwgfv__ludq,
            arg_types, typemap, updated_containers) for xhz__mgta,
            zwgfv__ludq in dict(nvvx__lvvab.kws).items()}
        arg_types = tuple(bodo.typeof(zwgfv__ludq) for zwgfv__ludq in args)
        kw_types = {bly__hoov: bodo.typeof(zwgfv__ludq) for bly__hoov,
            zwgfv__ludq in kwargs.items()}
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
    f_ir, typemap, wjrp__ytuc, wjrp__ytuc = bodo.compiler.get_func_type_info(
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
                    dik__iwcyi = guard(get_definition, f_ir, rhs.func)
                    if isinstance(dik__iwcyi, ir.Const) and isinstance(
                        dik__iwcyi.value, numba.core.dispatcher.
                        ObjModeLiftedWith):
                        return False
                    ctwtk__uoqg = guard(find_callname, f_ir, rhs)
                    if ctwtk__uoqg is None:
                        return False
                    func_name, xcp__vfm = ctwtk__uoqg
                    if xcp__vfm == 'pandas' and func_name.startswith('read_'):
                        return False
                    if ctwtk__uoqg in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if ctwtk__uoqg == ('File', 'h5py'):
                        return False
                    if isinstance(xcp__vfm, ir.Var):
                        mxiy__ysmv = typemap[xcp__vfm.name]
                        if isinstance(mxiy__ysmv, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(mxiy__ysmv, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(mxiy__ysmv, bodo.LoggingLoggerType):
                            return False
                        if str(mxiy__ysmv).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir, xcp__vfm
                            ), ir.Arg)):
                            return False
                    if xcp__vfm in ('numpy.random', 'time', 'logging',
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
        dtpwk__uuitr = func.literal_value.code
        xxmfa__iodpl = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            xxmfa__iodpl = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(xxmfa__iodpl, dtpwk__uuitr)
        fix_struct_return(f_ir)
        typemap, vcmtf__yvohs, hgwnp__rzo, wjrp__ytuc = (numba.core.
            typed_passes.type_inference_stage(typing_context,
            target_context, f_ir, arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, hgwnp__rzo, vcmtf__yvohs = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, hgwnp__rzo, vcmtf__yvohs = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, hgwnp__rzo, vcmtf__yvohs = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    if is_udf and isinstance(vcmtf__yvohs, types.DictType):
        nyo__ukw = guard(get_struct_keynames, f_ir, typemap)
        if nyo__ukw is not None:
            vcmtf__yvohs = StructType((vcmtf__yvohs.value_type,) * len(
                nyo__ukw), nyo__ukw)
    if is_udf and isinstance(vcmtf__yvohs, (SeriesType,
        HeterogeneousSeriesType)):
        myopz__ybwki = numba.core.registry.cpu_target.typing_context
        zufv__pvb = numba.core.registry.cpu_target.target_context
        vfi__txv = bodo.transforms.series_pass.SeriesPass(f_ir,
            myopz__ybwki, zufv__pvb, typemap, hgwnp__rzo, {})
        vfi__txv.run()
        vfi__txv.run()
        vfi__txv.run()
        qrci__kdz = compute_cfg_from_blocks(f_ir.blocks)
        fbun__tiul = [guard(_get_const_series_info, f_ir.blocks[mli__hbka],
            f_ir, typemap) for mli__hbka in qrci__kdz.exit_points() if
            isinstance(f_ir.blocks[mli__hbka].body[-1], ir.Return)]
        if None in fbun__tiul or len(pd.Series(fbun__tiul).unique()) != 1:
            vcmtf__yvohs.const_info = None
        else:
            vcmtf__yvohs.const_info = fbun__tiul[0]
    return vcmtf__yvohs


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    owfwo__osbdp = block.body[-1].value
    ufib__eaun = get_definition(f_ir, owfwo__osbdp)
    require(is_expr(ufib__eaun, 'cast'))
    ufib__eaun = get_definition(f_ir, ufib__eaun.value)
    require(is_call(ufib__eaun) and find_callname(f_ir, ufib__eaun) == (
        'init_series', 'bodo.hiframes.pd_series_ext'))
    imm__hwq = ufib__eaun.args[1]
    uagtx__vxzz = tuple(get_const_value_inner(f_ir, imm__hwq, typemap=typemap))
    if isinstance(typemap[owfwo__osbdp.name], HeterogeneousSeriesType):
        return len(typemap[owfwo__osbdp.name].data), uagtx__vxzz
    cqjvf__xsk = ufib__eaun.args[0]
    smf__xebn = get_definition(f_ir, cqjvf__xsk)
    func_name, ixvy__xgen = find_callname(f_ir, smf__xebn)
    if is_call(smf__xebn) and bodo.utils.utils.is_alloc_callname(func_name,
        ixvy__xgen):
        jpmu__sbmot = smf__xebn.args[0]
        xoue__xpt = get_const_value_inner(f_ir, jpmu__sbmot, typemap=typemap)
        return xoue__xpt, uagtx__vxzz
    if is_call(smf__xebn) and find_callname(f_ir, smf__xebn) in [('asarray',
        'numpy'), ('str_arr_from_sequence', 'bodo.libs.str_arr_ext')]:
        cqjvf__xsk = smf__xebn.args[0]
        smf__xebn = get_definition(f_ir, cqjvf__xsk)
    require(is_expr(smf__xebn, 'build_tuple') or is_expr(smf__xebn,
        'build_list'))
    return len(smf__xebn.items), uagtx__vxzz


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    maoqk__ixayg = []
    zuma__woati = []
    values = []
    for bly__hoov, zwgfv__ludq in build_map.items:
        pdb__kkqfd = find_const(f_ir, bly__hoov)
        require(isinstance(pdb__kkqfd, str))
        zuma__woati.append(pdb__kkqfd)
        maoqk__ixayg.append(bly__hoov)
        values.append(zwgfv__ludq)
    glni__zmpoj = ir.Var(scope, mk_unique_var('val_tup'), loc)
    lkwft__quzs = ir.Assign(ir.Expr.build_tuple(values, loc), glni__zmpoj, loc)
    f_ir._definitions[glni__zmpoj.name] = [lkwft__quzs.value]
    wenas__evpe = ir.Var(scope, mk_unique_var('key_tup'), loc)
    bjqbi__rav = ir.Assign(ir.Expr.build_tuple(maoqk__ixayg, loc),
        wenas__evpe, loc)
    f_ir._definitions[wenas__evpe.name] = [bjqbi__rav.value]
    if typemap is not None:
        typemap[glni__zmpoj.name] = types.Tuple([typemap[zwgfv__ludq.name] for
            zwgfv__ludq in values])
        typemap[wenas__evpe.name] = types.Tuple([typemap[zwgfv__ludq.name] for
            zwgfv__ludq in maoqk__ixayg])
    return zuma__woati, glni__zmpoj, lkwft__quzs, wenas__evpe, bjqbi__rav


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    qctqx__ivmz = block.body[-1].value
    bpas__botji = guard(get_definition, f_ir, qctqx__ivmz)
    require(is_expr(bpas__botji, 'cast'))
    ufib__eaun = guard(get_definition, f_ir, bpas__botji.value)
    require(is_expr(ufib__eaun, 'build_map'))
    require(len(ufib__eaun.items) > 0)
    loc = block.loc
    scope = block.scope
    zuma__woati, glni__zmpoj, lkwft__quzs, wenas__evpe, bjqbi__rav = (
        extract_keyvals_from_struct_map(f_ir, ufib__eaun, loc, scope))
    yfym__zoohc = ir.Var(scope, mk_unique_var('conv_call'), loc)
    rth__soxpl = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), yfym__zoohc, loc)
    f_ir._definitions[yfym__zoohc.name] = [rth__soxpl.value]
    iol__djn = ir.Var(scope, mk_unique_var('struct_val'), loc)
    rzu__rtfz = ir.Assign(ir.Expr.call(yfym__zoohc, [glni__zmpoj,
        wenas__evpe], {}, loc), iol__djn, loc)
    f_ir._definitions[iol__djn.name] = [rzu__rtfz.value]
    bpas__botji.value = iol__djn
    ufib__eaun.items = [(bly__hoov, bly__hoov) for bly__hoov, wjrp__ytuc in
        ufib__eaun.items]
    block.body = block.body[:-2] + [lkwft__quzs, bjqbi__rav, rth__soxpl,
        rzu__rtfz] + block.body[-2:]
    return tuple(zuma__woati)


def get_struct_keynames(f_ir, typemap):
    qrci__kdz = compute_cfg_from_blocks(f_ir.blocks)
    kxi__bfpm = list(qrci__kdz.exit_points())[0]
    block = f_ir.blocks[kxi__bfpm]
    require(isinstance(block.body[-1], ir.Return))
    qctqx__ivmz = block.body[-1].value
    bpas__botji = guard(get_definition, f_ir, qctqx__ivmz)
    require(is_expr(bpas__botji, 'cast'))
    ufib__eaun = guard(get_definition, f_ir, bpas__botji.value)
    require(is_call(ufib__eaun) and find_callname(f_ir, ufib__eaun) == (
        'struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[ufib__eaun.args[1].name])


def fix_struct_return(f_ir):
    czt__hlda = None
    qrci__kdz = compute_cfg_from_blocks(f_ir.blocks)
    for kxi__bfpm in qrci__kdz.exit_points():
        czt__hlda = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            kxi__bfpm], kxi__bfpm)
    return czt__hlda


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    rgkz__ivmqf = ir.Block(ir.Scope(None, loc), loc)
    rgkz__ivmqf.body = node_list
    build_definitions({(0): rgkz__ivmqf}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(zwgfv__ludq) for zwgfv__ludq in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    ous__afay = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(ous__afay, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for afji__jekb in range(len(vals) - 1, -1, -1):
        zwgfv__ludq = vals[afji__jekb]
        if isinstance(zwgfv__ludq, str) and zwgfv__ludq.startswith(
            NESTED_TUP_SENTINEL):
            unun__lqf = int(zwgfv__ludq[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:afji__jekb]) + (
                tuple(vals[afji__jekb + 1:afji__jekb + unun__lqf + 1]),) +
                tuple(vals[afji__jekb + unun__lqf + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    jsn__xrj = None
    if len(args) > arg_no and arg_no >= 0:
        jsn__xrj = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        jsn__xrj = kws[arg_name]
    if jsn__xrj is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return jsn__xrj


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
    thntb__mrwca = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        thntb__mrwca.update(extra_globals)
    func.__globals__.update(thntb__mrwca)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            jmbm__knp = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[jmbm__knp.name] = types.literal(default)
            except:
                pass_info.typemap[jmbm__knp.name] = numba.typeof(default)
            srr__ixni = ir.Assign(ir.Const(default, loc), jmbm__knp, loc)
            pre_nodes.append(srr__ixni)
            return jmbm__knp
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    klk__kgbuz = tuple(pass_info.typemap[zwgfv__ludq.name] for zwgfv__ludq in
        args)
    if const:
        uizk__kvlb = []
        for afji__jekb, jsn__xrj in enumerate(args):
            thps__pmc = guard(find_const, pass_info.func_ir, jsn__xrj)
            if thps__pmc:
                uizk__kvlb.append(types.literal(thps__pmc))
            else:
                uizk__kvlb.append(klk__kgbuz[afji__jekb])
        klk__kgbuz = tuple(uizk__kvlb)
    return ReplaceFunc(func, klk__kgbuz, args, thntb__mrwca,
        inline_bodo_calls, run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(pxs__ebld) for pxs__ebld in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        jgr__tiz = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {jgr__tiz} = 0\n', (jgr__tiz,)
    if isinstance(t, ArrayItemArrayType):
        gypc__xeqou, wowgl__syz = gen_init_varsize_alloc_sizes(t.dtype)
        jgr__tiz = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {jgr__tiz} = 0\n' + gypc__xeqou, (jgr__tiz,) + wowgl__syz
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
        return 1 + sum(get_type_alloc_counts(pxs__ebld.dtype) for pxs__ebld in
            t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(pxs__ebld) for pxs__ebld in t.data)
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(pxs__ebld) for pxs__ebld in t.types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    ksns__vmbbv = typing_context.resolve_getattr(obj_dtype, func_name)
    if ksns__vmbbv is None:
        ekjhj__cfc = types.misc.Module(np)
        try:
            ksns__vmbbv = typing_context.resolve_getattr(ekjhj__cfc, func_name)
        except AttributeError as nbnp__xtsd:
            ksns__vmbbv = None
        if ksns__vmbbv is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return ksns__vmbbv


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    ksns__vmbbv = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(ksns__vmbbv, types.BoundFunction):
        if axis is not None:
            nxxjf__qwrcd = ksns__vmbbv.get_call_type(typing_context, (), {
                'axis': axis})
        else:
            nxxjf__qwrcd = ksns__vmbbv.get_call_type(typing_context, (), {})
        return nxxjf__qwrcd.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(ksns__vmbbv):
            nxxjf__qwrcd = ksns__vmbbv.get_call_type(typing_context, (
                obj_dtype,), {})
            return nxxjf__qwrcd.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    ksns__vmbbv = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(ksns__vmbbv, types.BoundFunction):
        hqn__msahz = ksns__vmbbv.template
        if axis is not None:
            return hqn__msahz._overload_func(obj_dtype, axis=axis)
        else:
            return hqn__msahz._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    qagtf__cwvf = get_definition(func_ir, dict_var)
    require(isinstance(qagtf__cwvf, ir.Expr))
    require(qagtf__cwvf.op == 'build_map')
    mrwh__lfdy = qagtf__cwvf.items
    maoqk__ixayg = []
    values = []
    eqnmv__ojw = False
    for afji__jekb in range(len(mrwh__lfdy)):
        rusf__gscm, value = mrwh__lfdy[afji__jekb]
        try:
            bqsn__gyn = get_const_value_inner(func_ir, rusf__gscm,
                arg_types, typemap, updated_containers)
            maoqk__ixayg.append(bqsn__gyn)
            values.append(value)
        except GuardException as nbnp__xtsd:
            require_const_map[rusf__gscm] = label
            eqnmv__ojw = True
    if eqnmv__ojw:
        raise GuardException
    return maoqk__ixayg, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        maoqk__ixayg = tuple(get_const_value_inner(func_ir, t[0], args) for
            t in build_map.items)
    except GuardException as nbnp__xtsd:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in maoqk__ixayg):
        raise BodoError(err_msg, loc)
    return maoqk__ixayg


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    maoqk__ixayg = _get_const_keys_from_dict(args, func_ir, build_map,
        err_msg, loc)
    kvdph__fmg = []
    xufi__oop = [bodo.transforms.typing_pass._create_const_var(bly__hoov,
        'dict_key', scope, loc, kvdph__fmg) for bly__hoov in maoqk__ixayg]
    nfjb__mjqui = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        sfrwq__hry = ir.Var(scope, mk_unique_var('sentinel'), loc)
        riwk__lti = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        kvdph__fmg.append(ir.Assign(ir.Const('__bodo_tup', loc), sfrwq__hry,
            loc))
        kkelo__wuokp = [sfrwq__hry] + xufi__oop + nfjb__mjqui
        kvdph__fmg.append(ir.Assign(ir.Expr.build_tuple(kkelo__wuokp, loc),
            riwk__lti, loc))
        return (riwk__lti,), kvdph__fmg
    else:
        jqjcx__wwxfs = ir.Var(scope, mk_unique_var('values_tup'), loc)
        emmji__zqw = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        kvdph__fmg.append(ir.Assign(ir.Expr.build_tuple(nfjb__mjqui, loc),
            jqjcx__wwxfs, loc))
        kvdph__fmg.append(ir.Assign(ir.Expr.build_tuple(xufi__oop, loc),
            emmji__zqw, loc))
        return (jqjcx__wwxfs, emmji__zqw), kvdph__fmg
