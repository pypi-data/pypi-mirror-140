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
    exh__xca = tuple(call_list)
    if exh__xca in no_side_effect_call_tuples:
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
    if len(exh__xca) == 1 and tuple in getattr(exh__xca[0], '__mro__', ()):
        return True
    return False


numba.core.ir_utils.remove_call_handlers.append(remove_hiframes)


def compile_func_single_block(func, args, ret_var, typing_info=None,
    extra_globals=None, infer_types=True, run_untyped_pass=False, flags=
    None, replace_globals=True):
    hdz__hoguu = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd, 'math':
        math}
    if extra_globals is not None:
        hdz__hoguu.update(extra_globals)
    if not replace_globals:
        hdz__hoguu = func.__globals__
    loc = ir.Loc('', 0)
    if ret_var:
        loc = ret_var.loc
    if typing_info and infer_types:
        loc = typing_info.curr_loc
        f_ir = compile_to_numba_ir(func, hdz__hoguu, typingctx=typing_info.
            typingctx, targetctx=typing_info.targetctx, arg_typs=tuple(
            typing_info.typemap[xmqlg__kjce.name] for xmqlg__kjce in args),
            typemap=typing_info.typemap, calltypes=typing_info.calltypes)
    else:
        f_ir = compile_to_numba_ir(func, hdz__hoguu)
    assert len(f_ir.blocks
        ) == 1, 'only single block functions supported in compile_func_single_block()'
    if run_untyped_pass:
        gqg__ptx = tuple(typing_info.typemap[xmqlg__kjce.name] for
            xmqlg__kjce in args)
        pmvy__hgfv = bodo.transforms.untyped_pass.UntypedPass(f_ir,
            typing_info.typingctx, gqg__ptx, {}, {}, flags)
        pmvy__hgfv.run()
    gwsq__lane = f_ir.blocks.popitem()[1]
    replace_arg_nodes(gwsq__lane, args)
    ebpwu__vejw = gwsq__lane.body[:-2]
    update_locs(ebpwu__vejw[len(args):], loc)
    for stmt in ebpwu__vejw[:len(args)]:
        stmt.target.loc = loc
    if ret_var is not None:
        jlvz__vddok = gwsq__lane.body[-2]
        assert is_assign(jlvz__vddok) and is_expr(jlvz__vddok.value, 'cast')
        ltc__iir = jlvz__vddok.value.value
        ebpwu__vejw.append(ir.Assign(ltc__iir, ret_var, loc))
    return ebpwu__vejw


def update_locs(node_list, loc):
    for stmt in node_list:
        stmt.loc = loc
        for vif__jzt in stmt.list_vars():
            vif__jzt.loc = loc
        if is_assign(stmt):
            stmt.value.loc = loc


def get_stmt_defs(stmt):
    if is_assign(stmt):
        return set([stmt.target.name])
    if type(stmt) in numba.core.analysis.ir_extension_usedefs:
        aeq__nnoxn = numba.core.analysis.ir_extension_usedefs[type(stmt)]
        rpc__lwjo, oqtw__jwybc = aeq__nnoxn(stmt)
        return oqtw__jwybc
    return set()


def get_const_value(var, func_ir, err_msg, typemap=None, arg_types=None,
    file_info=None):
    if hasattr(var, 'loc'):
        loc = var.loc
    else:
        loc = None
    try:
        ebvce__tmu = get_const_value_inner(func_ir, var, arg_types, typemap,
            file_info=file_info)
        if isinstance(ebvce__tmu, ir.UndefinedType):
            oel__zpjm = func_ir.get_definition(var.name).name
            raise BodoError(f"name '{oel__zpjm}' is not defined", loc=loc)
    except GuardException as shshf__azd:
        raise BodoError(err_msg, loc=loc)
    return ebvce__tmu


def get_const_value_inner(func_ir, var, arg_types=None, typemap=None,
    updated_containers=None, file_info=None, pyobject_to_literal=False,
    literalize_args=True):
    require(isinstance(var, ir.Var))
    fgu__wqyte = get_definition(func_ir, var)
    jtgcy__mrkcj = None
    if typemap is not None:
        jtgcy__mrkcj = typemap.get(var.name, None)
    if isinstance(fgu__wqyte, ir.Arg) and arg_types is not None:
        jtgcy__mrkcj = arg_types[fgu__wqyte.index]
    if updated_containers and var.name in updated_containers:
        raise BodoConstUpdatedError(
            f"variable '{var.name}' is updated inplace using '{updated_containers[var.name]}'"
            )
    if is_literal_type(jtgcy__mrkcj):
        return get_literal_value(jtgcy__mrkcj)
    if isinstance(fgu__wqyte, (ir.Const, ir.Global, ir.FreeVar)):
        ebvce__tmu = fgu__wqyte.value
        return ebvce__tmu
    if literalize_args and isinstance(fgu__wqyte, ir.Arg
        ) and can_literalize_type(jtgcy__mrkcj, pyobject_to_literal):
        raise numba.core.errors.ForceLiteralArg({fgu__wqyte.index}, loc=var
            .loc, file_infos={fgu__wqyte.index: file_info} if file_info is not
            None else None)
    if is_expr(fgu__wqyte, 'binop'):
        if file_info and fgu__wqyte.fn == operator.add:
            try:
                dcqn__zwv = get_const_value_inner(func_ir, fgu__wqyte.lhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(dcqn__zwv, True)
                kwzo__pop = get_const_value_inner(func_ir, fgu__wqyte.rhs,
                    arg_types, typemap, updated_containers, file_info)
                return fgu__wqyte.fn(dcqn__zwv, kwzo__pop)
            except (GuardException, BodoConstUpdatedError) as shshf__azd:
                pass
            try:
                kwzo__pop = get_const_value_inner(func_ir, fgu__wqyte.rhs,
                    arg_types, typemap, updated_containers, literalize_args
                    =False)
                file_info.set_concat(kwzo__pop, False)
                dcqn__zwv = get_const_value_inner(func_ir, fgu__wqyte.lhs,
                    arg_types, typemap, updated_containers, file_info)
                return fgu__wqyte.fn(dcqn__zwv, kwzo__pop)
            except (GuardException, BodoConstUpdatedError) as shshf__azd:
                pass
        dcqn__zwv = get_const_value_inner(func_ir, fgu__wqyte.lhs,
            arg_types, typemap, updated_containers)
        kwzo__pop = get_const_value_inner(func_ir, fgu__wqyte.rhs,
            arg_types, typemap, updated_containers)
        return fgu__wqyte.fn(dcqn__zwv, kwzo__pop)
    if is_expr(fgu__wqyte, 'unary'):
        ebvce__tmu = get_const_value_inner(func_ir, fgu__wqyte.value,
            arg_types, typemap, updated_containers)
        return fgu__wqyte.fn(ebvce__tmu)
    if is_expr(fgu__wqyte, 'getattr') and typemap:
        nbbxm__glly = typemap.get(fgu__wqyte.value.name, None)
        if isinstance(nbbxm__glly, bodo.hiframes.pd_dataframe_ext.DataFrameType
            ) and fgu__wqyte.attr == 'columns':
            return pd.Index(nbbxm__glly.columns)
        if isinstance(nbbxm__glly, types.SliceType):
            pjco__taf = get_definition(func_ir, fgu__wqyte.value)
            require(is_call(pjco__taf))
            xzmc__hxqfd = find_callname(func_ir, pjco__taf)
            qrd__gygq = False
            if xzmc__hxqfd == ('_normalize_slice', 'numba.cpython.unicode'):
                require(fgu__wqyte.attr in ('start', 'step'))
                pjco__taf = get_definition(func_ir, pjco__taf.args[0])
                qrd__gygq = True
            require(find_callname(func_ir, pjco__taf) == ('slice', 'builtins'))
            if len(pjco__taf.args) == 1:
                if fgu__wqyte.attr == 'start':
                    return 0
                if fgu__wqyte.attr == 'step':
                    return 1
                require(fgu__wqyte.attr == 'stop')
                return get_const_value_inner(func_ir, pjco__taf.args[0],
                    arg_types, typemap, updated_containers)
            if fgu__wqyte.attr == 'start':
                ebvce__tmu = get_const_value_inner(func_ir, pjco__taf.args[
                    0], arg_types, typemap, updated_containers)
                if ebvce__tmu is None:
                    ebvce__tmu = 0
                if qrd__gygq:
                    require(ebvce__tmu == 0)
                return ebvce__tmu
            if fgu__wqyte.attr == 'stop':
                assert not qrd__gygq
                return get_const_value_inner(func_ir, pjco__taf.args[1],
                    arg_types, typemap, updated_containers)
            require(fgu__wqyte.attr == 'step')
            if len(pjco__taf.args) == 2:
                return 1
            else:
                ebvce__tmu = get_const_value_inner(func_ir, pjco__taf.args[
                    2], arg_types, typemap, updated_containers)
                if ebvce__tmu is None:
                    ebvce__tmu = 1
                if qrd__gygq:
                    require(ebvce__tmu == 1)
                return ebvce__tmu
    if is_expr(fgu__wqyte, 'getattr'):
        return getattr(get_const_value_inner(func_ir, fgu__wqyte.value,
            arg_types, typemap, updated_containers), fgu__wqyte.attr)
    if is_expr(fgu__wqyte, 'getitem'):
        value = get_const_value_inner(func_ir, fgu__wqyte.value, arg_types,
            typemap, updated_containers)
        index = get_const_value_inner(func_ir, fgu__wqyte.index, arg_types,
            typemap, updated_containers)
        return value[index]
    kokn__wbh = guard(find_callname, func_ir, fgu__wqyte, typemap)
    if kokn__wbh is not None and len(kokn__wbh) == 2 and kokn__wbh[0
        ] == 'keys' and isinstance(kokn__wbh[1], ir.Var):
        gxq__bdu = fgu__wqyte.func
        fgu__wqyte = get_definition(func_ir, kokn__wbh[1])
        lxlai__zuumo = kokn__wbh[1].name
        if updated_containers and lxlai__zuumo in updated_containers:
            raise BodoConstUpdatedError(
                "variable '{}' is updated inplace using '{}'".format(
                lxlai__zuumo, updated_containers[lxlai__zuumo]))
        require(is_expr(fgu__wqyte, 'build_map'))
        vals = [vif__jzt[0] for vif__jzt in fgu__wqyte.items]
        egf__ubicr = guard(get_definition, func_ir, gxq__bdu)
        assert isinstance(egf__ubicr, ir.Expr) and egf__ubicr.attr == 'keys'
        egf__ubicr.attr = 'copy'
        return [get_const_value_inner(func_ir, vif__jzt, arg_types, typemap,
            updated_containers) for vif__jzt in vals]
    if is_expr(fgu__wqyte, 'build_map'):
        return {get_const_value_inner(func_ir, vif__jzt[0], arg_types,
            typemap, updated_containers): get_const_value_inner(func_ir,
            vif__jzt[1], arg_types, typemap, updated_containers) for
            vif__jzt in fgu__wqyte.items}
    if is_expr(fgu__wqyte, 'build_tuple'):
        return tuple(get_const_value_inner(func_ir, vif__jzt, arg_types,
            typemap, updated_containers) for vif__jzt in fgu__wqyte.items)
    if is_expr(fgu__wqyte, 'build_list'):
        return [get_const_value_inner(func_ir, vif__jzt, arg_types, typemap,
            updated_containers) for vif__jzt in fgu__wqyte.items]
    if is_expr(fgu__wqyte, 'build_set'):
        return {get_const_value_inner(func_ir, vif__jzt, arg_types, typemap,
            updated_containers) for vif__jzt in fgu__wqyte.items}
    if kokn__wbh == ('list', 'builtins'):
        values = get_const_value_inner(func_ir, fgu__wqyte.args[0],
            arg_types, typemap, updated_containers)
        if isinstance(values, set):
            values = sorted(values)
        return list(values)
    if kokn__wbh == ('set', 'builtins'):
        return set(get_const_value_inner(func_ir, fgu__wqyte.args[0],
            arg_types, typemap, updated_containers))
    if kokn__wbh == ('range', 'builtins') and len(fgu__wqyte.args) == 1:
        return range(get_const_value_inner(func_ir, fgu__wqyte.args[0],
            arg_types, typemap, updated_containers))
    if kokn__wbh == ('slice', 'builtins'):
        return slice(*tuple(get_const_value_inner(func_ir, vif__jzt,
            arg_types, typemap, updated_containers) for vif__jzt in
            fgu__wqyte.args))
    if kokn__wbh == ('str', 'builtins'):
        return str(get_const_value_inner(func_ir, fgu__wqyte.args[0],
            arg_types, typemap, updated_containers))
    if kokn__wbh == ('bool', 'builtins'):
        return bool(get_const_value_inner(func_ir, fgu__wqyte.args[0],
            arg_types, typemap, updated_containers))
    if kokn__wbh == ('format', 'builtins'):
        xmqlg__kjce = get_const_value_inner(func_ir, fgu__wqyte.args[0],
            arg_types, typemap, updated_containers)
        dnb__tgttt = get_const_value_inner(func_ir, fgu__wqyte.args[1],
            arg_types, typemap, updated_containers) if len(fgu__wqyte.args
            ) > 1 else ''
        return format(xmqlg__kjce, dnb__tgttt)
    if kokn__wbh in (('init_binary_str_index', 'bodo.hiframes.pd_index_ext'
        ), ('init_numeric_index', 'bodo.hiframes.pd_index_ext'), (
        'init_categorical_index', 'bodo.hiframes.pd_index_ext'), (
        'init_datetime_index', 'bodo.hiframes.pd_index_ext'), (
        'init_timedelta_index', 'bodo.hiframes.pd_index_ext'), (
        'init_heter_index', 'bodo.hiframes.pd_index_ext')):
        return pd.Index(get_const_value_inner(func_ir, fgu__wqyte.args[0],
            arg_types, typemap, updated_containers))
    if kokn__wbh == ('str_arr_from_sequence', 'bodo.libs.str_arr_ext'):
        return np.array(get_const_value_inner(func_ir, fgu__wqyte.args[0],
            arg_types, typemap, updated_containers))
    if kokn__wbh == ('init_range_index', 'bodo.hiframes.pd_index_ext'):
        return pd.RangeIndex(get_const_value_inner(func_ir, fgu__wqyte.args
            [0], arg_types, typemap, updated_containers),
            get_const_value_inner(func_ir, fgu__wqyte.args[1], arg_types,
            typemap, updated_containers), get_const_value_inner(func_ir,
            fgu__wqyte.args[2], arg_types, typemap, updated_containers))
    if kokn__wbh == ('len', 'builtins') and typemap and isinstance(typemap.
        get(fgu__wqyte.args[0].name, None), types.BaseTuple):
        return len(typemap[fgu__wqyte.args[0].name])
    if kokn__wbh == ('len', 'builtins'):
        rzit__vbl = guard(get_definition, func_ir, fgu__wqyte.args[0])
        if isinstance(rzit__vbl, ir.Expr) and rzit__vbl.op in ('build_tuple',
            'build_list', 'build_set', 'build_map'):
            return len(rzit__vbl.items)
        return len(get_const_value_inner(func_ir, fgu__wqyte.args[0],
            arg_types, typemap, updated_containers))
    if kokn__wbh == ('CategoricalDtype', 'pandas'):
        kws = dict(fgu__wqyte.kws)
        hfu__hnd = get_call_expr_arg('CategoricalDtype', fgu__wqyte.args,
            kws, 0, 'categories', '')
        dnv__huia = get_call_expr_arg('CategoricalDtype', fgu__wqyte.args,
            kws, 1, 'ordered', False)
        if dnv__huia is not False:
            dnv__huia = get_const_value_inner(func_ir, dnv__huia, arg_types,
                typemap, updated_containers)
        if hfu__hnd == '':
            hfu__hnd = None
        else:
            hfu__hnd = get_const_value_inner(func_ir, hfu__hnd, arg_types,
                typemap, updated_containers)
        return pd.CategoricalDtype(hfu__hnd, dnv__huia)
    if kokn__wbh == ('dtype', 'numpy'):
        return np.dtype(get_const_value_inner(func_ir, fgu__wqyte.args[0],
            arg_types, typemap, updated_containers))
    if kokn__wbh is not None and len(kokn__wbh) == 2 and kokn__wbh[1
        ] == 'pandas' and kokn__wbh[0] in ('Int8Dtype', 'Int16Dtype',
        'Int32Dtype', 'Int64Dtype', 'UInt8Dtype', 'UInt16Dtype',
        'UInt32Dtype', 'UInt64Dtype'):
        return getattr(pd, kokn__wbh[0])()
    if kokn__wbh is not None and len(kokn__wbh) == 2 and isinstance(kokn__wbh
        [1], ir.Var):
        ebvce__tmu = get_const_value_inner(func_ir, kokn__wbh[1], arg_types,
            typemap, updated_containers)
        args = [get_const_value_inner(func_ir, vif__jzt, arg_types, typemap,
            updated_containers) for vif__jzt in fgu__wqyte.args]
        kws = {kyva__udyo[0]: get_const_value_inner(func_ir, kyva__udyo[1],
            arg_types, typemap, updated_containers) for kyva__udyo in
            fgu__wqyte.kws}
        return getattr(ebvce__tmu, kokn__wbh[0])(*args, **kws)
    if kokn__wbh is not None and len(kokn__wbh) == 2 and kokn__wbh[1
        ] == 'bodo' and kokn__wbh[0] in bodo_types_with_params:
        args = tuple(get_const_value_inner(func_ir, vif__jzt, arg_types,
            typemap, updated_containers) for vif__jzt in fgu__wqyte.args)
        kwargs = {oel__zpjm: get_const_value_inner(func_ir, vif__jzt,
            arg_types, typemap, updated_containers) for oel__zpjm, vif__jzt in
            dict(fgu__wqyte.kws).items()}
        return getattr(bodo, kokn__wbh[0])(*args, **kwargs)
    if is_call(fgu__wqyte) and typemap and isinstance(typemap.get(
        fgu__wqyte.func.name, None), types.Dispatcher):
        py_func = typemap[fgu__wqyte.func.name].dispatcher.py_func
        require(fgu__wqyte.vararg is None)
        args = tuple(get_const_value_inner(func_ir, vif__jzt, arg_types,
            typemap, updated_containers) for vif__jzt in fgu__wqyte.args)
        kwargs = {oel__zpjm: get_const_value_inner(func_ir, vif__jzt,
            arg_types, typemap, updated_containers) for oel__zpjm, vif__jzt in
            dict(fgu__wqyte.kws).items()}
        arg_types = tuple(bodo.typeof(vif__jzt) for vif__jzt in args)
        kw_types = {hrpz__zgny: bodo.typeof(vif__jzt) for hrpz__zgny,
            vif__jzt in kwargs.items()}
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
    f_ir, typemap, ruzp__shsvz, ruzp__shsvz = bodo.compiler.get_func_type_info(
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
                    amvcq__nmuua = guard(get_definition, f_ir, rhs.func)
                    if isinstance(amvcq__nmuua, ir.Const) and isinstance(
                        amvcq__nmuua.value, numba.core.dispatcher.
                        ObjModeLiftedWith):
                        return False
                    dfrx__elz = guard(find_callname, f_ir, rhs)
                    if dfrx__elz is None:
                        return False
                    func_name, btwef__ufs = dfrx__elz
                    if btwef__ufs == 'pandas' and func_name.startswith('read_'
                        ):
                        return False
                    if dfrx__elz in (('fromfile', 'numpy'), ('file_read',
                        'bodo.io.np_io')):
                        return False
                    if dfrx__elz == ('File', 'h5py'):
                        return False
                    if isinstance(btwef__ufs, ir.Var):
                        jtgcy__mrkcj = typemap[btwef__ufs.name]
                        if isinstance(jtgcy__mrkcj, (DataFrameType, SeriesType)
                            ) and func_name in ('to_csv', 'to_excel',
                            'to_json', 'to_sql', 'to_pickle', 'to_parquet',
                            'info'):
                            return False
                        if isinstance(jtgcy__mrkcj, types.Array
                            ) and func_name == 'tofile':
                            return False
                        if isinstance(jtgcy__mrkcj, bodo.LoggingLoggerType):
                            return False
                        if str(jtgcy__mrkcj).startswith('Mpl'):
                            return False
                        if (func_name in container_update_method_names and
                            isinstance(guard(get_definition, f_ir,
                            btwef__ufs), ir.Arg)):
                            return False
                    if btwef__ufs in ('numpy.random', 'time', 'logging',
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
        slww__zvg = func.literal_value.code
        koir__zdsxk = {'np': np, 'pd': pd, 'numba': numba, 'bodo': bodo}
        if hasattr(func.literal_value, 'globals'):
            koir__zdsxk = func.literal_value.globals
        f_ir = numba.core.ir_utils.get_ir_of_code(koir__zdsxk, slww__zvg)
        fix_struct_return(f_ir)
        typemap, avike__cqogq, hrbk__rhlaw, ruzp__shsvz = (numba.core.
            typed_passes.type_inference_stage(typing_context,
            target_context, f_ir, arg_types, None))
    elif isinstance(func, bodo.utils.typing.FunctionLiteral):
        py_func = func.literal_value
        f_ir, typemap, hrbk__rhlaw, avike__cqogq = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    elif isinstance(func, CPUDispatcher):
        py_func = func.py_func
        f_ir, typemap, hrbk__rhlaw, avike__cqogq = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    else:
        if not isinstance(func, types.Dispatcher):
            if isinstance(func, types.Function):
                raise BodoError(
                    f'Bodo does not support built-in functions yet, {func}')
            else:
                raise BodoError(f'Function type expected, not {func}')
        py_func = func.dispatcher.py_func
        f_ir, typemap, hrbk__rhlaw, avike__cqogq = (bodo.compiler.
            get_func_type_info(py_func, arg_types, kw_types))
    if is_udf and isinstance(avike__cqogq, types.DictType):
        qwog__iczmp = guard(get_struct_keynames, f_ir, typemap)
        if qwog__iczmp is not None:
            avike__cqogq = StructType((avike__cqogq.value_type,) * len(
                qwog__iczmp), qwog__iczmp)
    if is_udf and isinstance(avike__cqogq, (SeriesType,
        HeterogeneousSeriesType)):
        fhy__jehn = numba.core.registry.cpu_target.typing_context
        xqz__sah = numba.core.registry.cpu_target.target_context
        fme__rfu = bodo.transforms.series_pass.SeriesPass(f_ir, fhy__jehn,
            xqz__sah, typemap, hrbk__rhlaw, {})
        fme__rfu.run()
        fme__rfu.run()
        fme__rfu.run()
        vuz__mjxjx = compute_cfg_from_blocks(f_ir.blocks)
        txo__frmxi = [guard(_get_const_series_info, f_ir.blocks[ftgi__vsf],
            f_ir, typemap) for ftgi__vsf in vuz__mjxjx.exit_points() if
            isinstance(f_ir.blocks[ftgi__vsf].body[-1], ir.Return)]
        if None in txo__frmxi or len(pd.Series(txo__frmxi).unique()) != 1:
            avike__cqogq.const_info = None
        else:
            avike__cqogq.const_info = txo__frmxi[0]
    return avike__cqogq


def _get_const_series_info(block, f_ir, typemap):
    from bodo.hiframes.pd_series_ext import HeterogeneousSeriesType
    assert isinstance(block.body[-1], ir.Return)
    qjqip__rdrnn = block.body[-1].value
    mcfl__owujx = get_definition(f_ir, qjqip__rdrnn)
    require(is_expr(mcfl__owujx, 'cast'))
    mcfl__owujx = get_definition(f_ir, mcfl__owujx.value)
    require(is_call(mcfl__owujx) and find_callname(f_ir, mcfl__owujx) == (
        'init_series', 'bodo.hiframes.pd_series_ext'))
    joyr__rbu = mcfl__owujx.args[1]
    aft__dvurk = tuple(get_const_value_inner(f_ir, joyr__rbu, typemap=typemap))
    if isinstance(typemap[qjqip__rdrnn.name], HeterogeneousSeriesType):
        return len(typemap[qjqip__rdrnn.name].data), aft__dvurk
    hpvtt__loy = mcfl__owujx.args[0]
    ineom__kemr = get_definition(f_ir, hpvtt__loy)
    func_name, cda__flmu = find_callname(f_ir, ineom__kemr)
    if is_call(ineom__kemr) and bodo.utils.utils.is_alloc_callname(func_name,
        cda__flmu):
        wdxqz__zocb = ineom__kemr.args[0]
        ido__banh = get_const_value_inner(f_ir, wdxqz__zocb, typemap=typemap)
        return ido__banh, aft__dvurk
    if is_call(ineom__kemr) and find_callname(f_ir, ineom__kemr) in [(
        'asarray', 'numpy'), ('str_arr_from_sequence', 'bodo.libs.str_arr_ext')
        ]:
        hpvtt__loy = ineom__kemr.args[0]
        ineom__kemr = get_definition(f_ir, hpvtt__loy)
    require(is_expr(ineom__kemr, 'build_tuple') or is_expr(ineom__kemr,
        'build_list'))
    return len(ineom__kemr.items), aft__dvurk


def extract_keyvals_from_struct_map(f_ir, build_map, loc, scope, typemap=None):
    nfvrk__edpt = []
    gkzec__aov = []
    values = []
    for hrpz__zgny, vif__jzt in build_map.items:
        eqj__zfznn = find_const(f_ir, hrpz__zgny)
        require(isinstance(eqj__zfznn, str))
        gkzec__aov.append(eqj__zfznn)
        nfvrk__edpt.append(hrpz__zgny)
        values.append(vif__jzt)
    kpta__cyxgk = ir.Var(scope, mk_unique_var('val_tup'), loc)
    pcw__ezsul = ir.Assign(ir.Expr.build_tuple(values, loc), kpta__cyxgk, loc)
    f_ir._definitions[kpta__cyxgk.name] = [pcw__ezsul.value]
    gtvvp__ydk = ir.Var(scope, mk_unique_var('key_tup'), loc)
    haoln__fcza = ir.Assign(ir.Expr.build_tuple(nfvrk__edpt, loc),
        gtvvp__ydk, loc)
    f_ir._definitions[gtvvp__ydk.name] = [haoln__fcza.value]
    if typemap is not None:
        typemap[kpta__cyxgk.name] = types.Tuple([typemap[vif__jzt.name] for
            vif__jzt in values])
        typemap[gtvvp__ydk.name] = types.Tuple([typemap[vif__jzt.name] for
            vif__jzt in nfvrk__edpt])
    return gkzec__aov, kpta__cyxgk, pcw__ezsul, gtvvp__ydk, haoln__fcza


def _replace_const_map_return(f_ir, block, label):
    require(isinstance(block.body[-1], ir.Return))
    vevht__psl = block.body[-1].value
    pmtol__atfxl = guard(get_definition, f_ir, vevht__psl)
    require(is_expr(pmtol__atfxl, 'cast'))
    mcfl__owujx = guard(get_definition, f_ir, pmtol__atfxl.value)
    require(is_expr(mcfl__owujx, 'build_map'))
    require(len(mcfl__owujx.items) > 0)
    loc = block.loc
    scope = block.scope
    gkzec__aov, kpta__cyxgk, pcw__ezsul, gtvvp__ydk, haoln__fcza = (
        extract_keyvals_from_struct_map(f_ir, mcfl__owujx, loc, scope))
    vxutb__appgv = ir.Var(scope, mk_unique_var('conv_call'), loc)
    qllvc__xcqf = ir.Assign(ir.Global('struct_if_heter_dict', bodo.utils.
        conversion.struct_if_heter_dict, loc), vxutb__appgv, loc)
    f_ir._definitions[vxutb__appgv.name] = [qllvc__xcqf.value]
    mrq__ihg = ir.Var(scope, mk_unique_var('struct_val'), loc)
    oiwuo__nbfsw = ir.Assign(ir.Expr.call(vxutb__appgv, [kpta__cyxgk,
        gtvvp__ydk], {}, loc), mrq__ihg, loc)
    f_ir._definitions[mrq__ihg.name] = [oiwuo__nbfsw.value]
    pmtol__atfxl.value = mrq__ihg
    mcfl__owujx.items = [(hrpz__zgny, hrpz__zgny) for hrpz__zgny,
        ruzp__shsvz in mcfl__owujx.items]
    block.body = block.body[:-2] + [pcw__ezsul, haoln__fcza, qllvc__xcqf,
        oiwuo__nbfsw] + block.body[-2:]
    return tuple(gkzec__aov)


def get_struct_keynames(f_ir, typemap):
    vuz__mjxjx = compute_cfg_from_blocks(f_ir.blocks)
    lqnn__pdlky = list(vuz__mjxjx.exit_points())[0]
    block = f_ir.blocks[lqnn__pdlky]
    require(isinstance(block.body[-1], ir.Return))
    vevht__psl = block.body[-1].value
    pmtol__atfxl = guard(get_definition, f_ir, vevht__psl)
    require(is_expr(pmtol__atfxl, 'cast'))
    mcfl__owujx = guard(get_definition, f_ir, pmtol__atfxl.value)
    require(is_call(mcfl__owujx) and find_callname(f_ir, mcfl__owujx) == (
        'struct_if_heter_dict', 'bodo.utils.conversion'))
    return get_overload_const_list(typemap[mcfl__owujx.args[1].name])


def fix_struct_return(f_ir):
    egjtm__ncbr = None
    vuz__mjxjx = compute_cfg_from_blocks(f_ir.blocks)
    for lqnn__pdlky in vuz__mjxjx.exit_points():
        egjtm__ncbr = guard(_replace_const_map_return, f_ir, f_ir.blocks[
            lqnn__pdlky], lqnn__pdlky)
    return egjtm__ncbr


def update_node_list_definitions(node_list, func_ir):
    loc = ir.Loc('', 0)
    xcgra__lrlev = ir.Block(ir.Scope(None, loc), loc)
    xcgra__lrlev.body = node_list
    build_definitions({(0): xcgra__lrlev}, func_ir._definitions)
    return


NESTED_TUP_SENTINEL = '$BODO_NESTED_TUP'


def gen_const_val_str(c):
    if isinstance(c, tuple):
        return "'{}{}', ".format(NESTED_TUP_SENTINEL, len(c)) + ', '.join(
            gen_const_val_str(vif__jzt) for vif__jzt in c)
    if isinstance(c, str):
        return "'{}'".format(c)
    if isinstance(c, (pd.Timestamp, pd.Timedelta, float)):
        return "'{}'".format(c)
    return str(c)


def gen_const_tup(vals):
    gryey__jlji = ', '.join(gen_const_val_str(c) for c in vals)
    return '({}{})'.format(gryey__jlji, ',' if len(vals) == 1 else '')


def get_const_tup_vals(c_typ):
    vals = get_overload_const_list(c_typ)
    return _get_original_nested_tups(vals)


def _get_original_nested_tups(vals):
    for hgmyf__khah in range(len(vals) - 1, -1, -1):
        vif__jzt = vals[hgmyf__khah]
        if isinstance(vif__jzt, str) and vif__jzt.startswith(
            NESTED_TUP_SENTINEL):
            mvvb__eaima = int(vif__jzt[len(NESTED_TUP_SENTINEL):])
            return _get_original_nested_tups(tuple(vals[:hgmyf__khah]) + (
                tuple(vals[hgmyf__khah + 1:hgmyf__khah + mvvb__eaima + 1]),
                ) + tuple(vals[hgmyf__khah + mvvb__eaima + 1:]))
    return tuple(vals)


def get_call_expr_arg(f_name, args, kws, arg_no, arg_name, default=None,
    err_msg=None, use_default=False):
    xmqlg__kjce = None
    if len(args) > arg_no and arg_no >= 0:
        xmqlg__kjce = args[arg_no]
        if arg_name in kws:
            err_msg = (
                f"{f_name}() got multiple values for argument '{arg_name}'")
            raise BodoError(err_msg)
    elif arg_name in kws:
        xmqlg__kjce = kws[arg_name]
    if xmqlg__kjce is None:
        if use_default or default is not None:
            return default
        if err_msg is None:
            err_msg = "{} requires '{}' argument".format(f_name, arg_name)
        raise BodoError(err_msg)
    return xmqlg__kjce


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
    hdz__hoguu = {'numba': numba, 'np': np, 'bodo': bodo, 'pd': pd}
    if extra_globals is not None:
        hdz__hoguu.update(extra_globals)
    func.__globals__.update(hdz__hoguu)
    if pysig is not None:
        pre_nodes = [] if pre_nodes is None else pre_nodes
        scope = next(iter(pass_info.func_ir.blocks.values())).scope
        loc = scope.loc

        def normal_handler(index, param, default):
            return default

        def default_handler(index, param, default):
            gma__frrto = ir.Var(scope, mk_unique_var('defaults'), loc)
            try:
                pass_info.typemap[gma__frrto.name] = types.literal(default)
            except:
                pass_info.typemap[gma__frrto.name] = numba.typeof(default)
            vnua__hyyo = ir.Assign(ir.Const(default, loc), gma__frrto, loc)
            pre_nodes.append(vnua__hyyo)
            return gma__frrto
        args = numba.core.typing.fold_arguments(pysig, args, kws,
            normal_handler, default_handler, normal_handler)
    gqg__ptx = tuple(pass_info.typemap[vif__jzt.name] for vif__jzt in args)
    if const:
        gveg__slu = []
        for hgmyf__khah, xmqlg__kjce in enumerate(args):
            ebvce__tmu = guard(find_const, pass_info.func_ir, xmqlg__kjce)
            if ebvce__tmu:
                gveg__slu.append(types.literal(ebvce__tmu))
            else:
                gveg__slu.append(gqg__ptx[hgmyf__khah])
        gqg__ptx = tuple(gveg__slu)
    return ReplaceFunc(func, gqg__ptx, args, hdz__hoguu, inline_bodo_calls,
        run_full_pipeline, pre_nodes)


def is_var_size_item_array_type(t):
    assert is_array_typ(t, False)
    return t == string_array_type or isinstance(t, ArrayItemArrayType
        ) or isinstance(t, StructArrayType) and any(
        is_var_size_item_array_type(axp__ytm) for axp__ytm in t.data)


def gen_init_varsize_alloc_sizes(t):
    if t == string_array_type:
        dtdcg__dfk = 'num_chars_{}'.format(ir_utils.next_label())
        return f'  {dtdcg__dfk} = 0\n', (dtdcg__dfk,)
    if isinstance(t, ArrayItemArrayType):
        uqx__osmg, bhnp__jjr = gen_init_varsize_alloc_sizes(t.dtype)
        dtdcg__dfk = 'num_items_{}'.format(ir_utils.next_label())
        return f'  {dtdcg__dfk} = 0\n' + uqx__osmg, (dtdcg__dfk,) + bhnp__jjr
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
        return 1 + sum(get_type_alloc_counts(axp__ytm.dtype) for axp__ytm in
            t.data)
    if isinstance(t, ArrayItemArrayType) or t == string_array_type:
        return 1 + get_type_alloc_counts(t.dtype)
    if isinstance(t, MapArrayType):
        return get_type_alloc_counts(t.key_arr_type) + get_type_alloc_counts(t
            .value_arr_type)
    if bodo.utils.utils.is_array_typ(t, False) or t == bodo.string_type:
        return 1
    if isinstance(t, StructType):
        return sum(get_type_alloc_counts(axp__ytm) for axp__ytm in t.data)
    if isinstance(t, types.BaseTuple):
        return sum(get_type_alloc_counts(axp__ytm) for axp__ytm in t.types)
    return 0


def find_udf_str_name(obj_dtype, func_name, typing_context, caller_name):
    jzzl__hkdog = typing_context.resolve_getattr(obj_dtype, func_name)
    if jzzl__hkdog is None:
        lbt__iaz = types.misc.Module(np)
        try:
            jzzl__hkdog = typing_context.resolve_getattr(lbt__iaz, func_name)
        except AttributeError as shshf__azd:
            jzzl__hkdog = None
        if jzzl__hkdog is None:
            raise BodoError(
                f"{caller_name}(): No Pandas method or Numpy function found with the name '{func_name}'."
                )
    return jzzl__hkdog


def get_udf_str_return_type(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    jzzl__hkdog = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(jzzl__hkdog, types.BoundFunction):
        if axis is not None:
            vdmj__pdocp = jzzl__hkdog.get_call_type(typing_context, (), {
                'axis': axis})
        else:
            vdmj__pdocp = jzzl__hkdog.get_call_type(typing_context, (), {})
        return vdmj__pdocp.return_type
    else:
        if bodo.utils.typing.is_numpy_ufunc(jzzl__hkdog):
            vdmj__pdocp = jzzl__hkdog.get_call_type(typing_context, (
                obj_dtype,), {})
            return vdmj__pdocp.return_type
        raise BodoError(
            f"{caller_name}(): Only Pandas methods and np.ufunc are supported as string literals. '{func_name}' not supported."
            )


def get_pandas_method_str_impl(obj_dtype, func_name, typing_context,
    caller_name, axis=None):
    jzzl__hkdog = find_udf_str_name(obj_dtype, func_name, typing_context,
        caller_name)
    if isinstance(jzzl__hkdog, types.BoundFunction):
        zspre__aaan = jzzl__hkdog.template
        if axis is not None:
            return zspre__aaan._overload_func(obj_dtype, axis=axis)
        else:
            return zspre__aaan._overload_func(obj_dtype)
    return None


def dict_to_const_keys_var_values_lists(dict_var, func_ir, arg_types,
    typemap, updated_containers, require_const_map, label):
    require(isinstance(dict_var, ir.Var))
    dptl__blo = get_definition(func_ir, dict_var)
    require(isinstance(dptl__blo, ir.Expr))
    require(dptl__blo.op == 'build_map')
    bwiwc__klmec = dptl__blo.items
    nfvrk__edpt = []
    values = []
    wto__nselz = False
    for hgmyf__khah in range(len(bwiwc__klmec)):
        uhku__wkq, value = bwiwc__klmec[hgmyf__khah]
        try:
            qku__mfvb = get_const_value_inner(func_ir, uhku__wkq, arg_types,
                typemap, updated_containers)
            nfvrk__edpt.append(qku__mfvb)
            values.append(value)
        except GuardException as shshf__azd:
            require_const_map[uhku__wkq] = label
            wto__nselz = True
    if wto__nselz:
        raise GuardException
    return nfvrk__edpt, values


def _get_const_keys_from_dict(args, func_ir, build_map, err_msg, loc):
    try:
        nfvrk__edpt = tuple(get_const_value_inner(func_ir, t[0], args) for
            t in build_map.items)
    except GuardException as shshf__azd:
        raise BodoError(err_msg, loc)
    if not all(isinstance(c, (str, int)) for c in nfvrk__edpt):
        raise BodoError(err_msg, loc)
    return nfvrk__edpt


def _convert_const_key_dict(args, func_ir, build_map, err_msg, scope, loc,
    output_sentinel_tuple=False):
    nfvrk__edpt = _get_const_keys_from_dict(args, func_ir, build_map,
        err_msg, loc)
    fwxb__tudxt = []
    qfby__aax = [bodo.transforms.typing_pass._create_const_var(hrpz__zgny,
        'dict_key', scope, loc, fwxb__tudxt) for hrpz__zgny in nfvrk__edpt]
    ayfwq__adt = [t[1] for t in build_map.items]
    if output_sentinel_tuple:
        vex__ksurm = ir.Var(scope, mk_unique_var('sentinel'), loc)
        ptj__gsta = ir.Var(scope, mk_unique_var('dict_tup'), loc)
        fwxb__tudxt.append(ir.Assign(ir.Const('__bodo_tup', loc),
            vex__ksurm, loc))
        koxup__stdi = [vex__ksurm] + qfby__aax + ayfwq__adt
        fwxb__tudxt.append(ir.Assign(ir.Expr.build_tuple(koxup__stdi, loc),
            ptj__gsta, loc))
        return (ptj__gsta,), fwxb__tudxt
    else:
        dpghd__naex = ir.Var(scope, mk_unique_var('values_tup'), loc)
        fko__prr = ir.Var(scope, mk_unique_var('idx_tup'), loc)
        fwxb__tudxt.append(ir.Assign(ir.Expr.build_tuple(ayfwq__adt, loc),
            dpghd__naex, loc))
        fwxb__tudxt.append(ir.Assign(ir.Expr.build_tuple(qfby__aax, loc),
            fko__prr, loc))
        return (dpghd__naex, fko__prr), fwxb__tudxt
