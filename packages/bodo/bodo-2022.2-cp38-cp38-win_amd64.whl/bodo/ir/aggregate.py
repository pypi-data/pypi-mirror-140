"""IR node for the groupby, pivot and cross_tabulation"""
import ctypes
import operator
import types as pytypes
from collections import defaultdict, namedtuple
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, compiler, ir, ir_utils, types
from numba.core.analysis import compute_use_defs
from numba.core.ir_utils import build_definitions, compile_to_numba_ir, find_callname, find_const, find_topo_order, get_definition, get_ir_of_code, get_name_var_table, guard, is_getitem, mk_unique_var, next_label, remove_dels, replace_arg_nodes, replace_var_names, replace_vars_inner, visit_vars_inner
from numba.core.typing import signature
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import intrinsic, lower_builtin, overload
from numba.parfors.parfor import Parfor, unwrap_parfor_blocks, wrap_parfor_blocks
import bodo
from bodo.hiframes.datetime_date_ext import DatetimeDateArrayType
from bodo.hiframes.pd_series_ext import SeriesType
from bodo.libs.array import arr_info_list_to_table, array_to_info, compute_node_partition_by_hash, delete_info_decref_array, delete_table, delete_table_decref_arrays, groupby_and_aggregate, info_from_table, info_to_array, pivot_groupby_and_aggregate
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, pre_alloc_array_item_array
from bodo.libs.binary_arr_ext import BinaryArrayType, pre_alloc_binary_array
from bodo.libs.bool_arr_ext import BooleanArrayType
from bodo.libs.decimal_arr_ext import DecimalArrayType, alloc_decimal_array
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, pre_alloc_string_array, string_array_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.utils.transform import get_call_expr_arg
from bodo.utils.typing import BodoError, get_literal_value, get_overload_const_func, get_overload_const_str, get_overload_constant_dict, is_overload_constant_dict, is_overload_constant_str, list_cumulative
from bodo.utils.utils import debug_prints, incref, is_assign, is_call_assign, is_expr, is_null_pointer, is_var_assign, sanitize_varname, unliteral_all
gb_agg_cfunc = {}
gb_agg_cfunc_addr = {}


@intrinsic
def add_agg_cfunc_sym(typingctx, func, sym):

    def codegen(context, builder, signature, args):
        sig = func.signature
        if sig == types.none(types.voidptr):
            oidjx__rsga = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer()])
            tjrd__rjky = cgutils.get_or_insert_function(builder.module,
                oidjx__rsga, sym._literal_value)
            builder.call(tjrd__rjky, [context.get_constant_null(sig.args[0])])
        elif sig == types.none(types.int64, types.voidptr, types.voidptr):
            oidjx__rsga = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            tjrd__rjky = cgutils.get_or_insert_function(builder.module,
                oidjx__rsga, sym._literal_value)
            builder.call(tjrd__rjky, [context.get_constant(types.int64, 0),
                context.get_constant_null(sig.args[1]), context.
                get_constant_null(sig.args[2])])
        else:
            oidjx__rsga = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64).
                as_pointer()])
            tjrd__rjky = cgutils.get_or_insert_function(builder.module,
                oidjx__rsga, sym._literal_value)
            builder.call(tjrd__rjky, [context.get_constant_null(sig.args[0]
                ), context.get_constant_null(sig.args[1]), context.
                get_constant_null(sig.args[2])])
        context.add_linking_libs([gb_agg_cfunc[sym._literal_value]._library])
        return
    return types.none(func, sym), codegen


@numba.jit
def get_agg_udf_addr(name):
    with numba.objmode(addr='int64'):
        addr = gb_agg_cfunc_addr[name]
    return addr


class AggUDFStruct(object):

    def __init__(self, regular_udf_funcs=None, general_udf_funcs=None):
        assert regular_udf_funcs is not None or general_udf_funcs is not None
        self.regular_udfs = False
        self.general_udfs = False
        self.regular_udf_cfuncs = None
        self.general_udf_cfunc = None
        if regular_udf_funcs is not None:
            (self.var_typs, self.init_func, self.update_all_func, self.
                combine_all_func, self.eval_all_func) = regular_udf_funcs
            self.regular_udfs = True
        if general_udf_funcs is not None:
            self.general_udf_funcs = general_udf_funcs
            self.general_udfs = True

    def set_regular_cfuncs(self, update_cb, combine_cb, eval_cb):
        assert self.regular_udfs and self.regular_udf_cfuncs is None
        self.regular_udf_cfuncs = [update_cb, combine_cb, eval_cb]

    def set_general_cfunc(self, general_udf_cb):
        assert self.general_udfs and self.general_udf_cfunc is None
        self.general_udf_cfunc = general_udf_cb


AggFuncStruct = namedtuple('AggFuncStruct', ['func', 'ftype'])
supported_agg_funcs = ['no_op', 'head', 'transform', 'size', 'shift', 'sum',
    'count', 'nunique', 'median', 'cumsum', 'cumprod', 'cummin', 'cummax',
    'mean', 'min', 'max', 'prod', 'first', 'last', 'idxmin', 'idxmax',
    'var', 'std', 'udf', 'gen_udf']
supported_transform_funcs = ['no_op', 'sum', 'count', 'nunique', 'median',
    'mean', 'min', 'max', 'prod', 'first', 'last', 'var', 'std']


def get_agg_func(func_ir, func_name, rhs, series_type=None, typemap=None):
    if func_name == 'no_op':
        raise BodoError('Unknown aggregation function used in groupby.')
    if series_type is None:
        series_type = SeriesType(types.float64)
    if func_name in {'var', 'std'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 3
        func.ncols_post_shuffle = 4
        return func
    if func_name in {'first', 'last'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        return func
    if func_name in {'idxmin', 'idxmax'}:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 2
        func.ncols_post_shuffle = 2
        return func
    if func_name in supported_agg_funcs[:-8]:
        func = pytypes.SimpleNamespace()
        func.ftype = func_name
        func.fname = func_name
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        cigo__pvrrn = True
        aembe__oqcmx = 1
        igah__zpwq = -1
        if isinstance(rhs, ir.Expr):
            for eabx__oip in rhs.kws:
                if func_name in list_cumulative:
                    if eabx__oip[0] == 'skipna':
                        cigo__pvrrn = guard(find_const, func_ir, eabx__oip[1])
                        if not isinstance(cigo__pvrrn, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if eabx__oip[0] == 'dropna':
                        cigo__pvrrn = guard(find_const, func_ir, eabx__oip[1])
                        if not isinstance(cigo__pvrrn, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            aembe__oqcmx = get_call_expr_arg('shift', rhs.args, dict(rhs.
                kws), 0, 'periods', aembe__oqcmx)
            aembe__oqcmx = guard(find_const, func_ir, aembe__oqcmx)
        if func_name == 'head':
            igah__zpwq = get_call_expr_arg('head', rhs.args, dict(rhs.kws),
                0, 'n', 5)
            if not isinstance(igah__zpwq, int):
                igah__zpwq = guard(find_const, func_ir, igah__zpwq)
            if igah__zpwq < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = cigo__pvrrn
        func.periods = aembe__oqcmx
        func.head_n = igah__zpwq
        if func_name == 'transform':
            kws = dict(rhs.kws)
            jhr__tvx = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            kvvoh__jxoy = typemap[jhr__tvx.name]
            onas__ufeud = None
            if isinstance(kvvoh__jxoy, str):
                onas__ufeud = kvvoh__jxoy
            elif is_overload_constant_str(kvvoh__jxoy):
                onas__ufeud = get_overload_const_str(kvvoh__jxoy)
            elif bodo.utils.typing.is_builtin_function(kvvoh__jxoy):
                onas__ufeud = bodo.utils.typing.get_builtin_function_name(
                    kvvoh__jxoy)
            if onas__ufeud not in bodo.ir.aggregate.supported_transform_funcs[:
                ]:
                raise BodoError(f'unsupported transform function {onas__ufeud}'
                    )
            func.transform_func = supported_agg_funcs.index(onas__ufeud)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    jhr__tvx = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if jhr__tvx == '':
        kvvoh__jxoy = types.none
    else:
        kvvoh__jxoy = typemap[jhr__tvx.name]
    if is_overload_constant_dict(kvvoh__jxoy):
        cbvcd__rci = get_overload_constant_dict(kvvoh__jxoy)
        hbll__vka = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in cbvcd__rci.values()]
        return hbll__vka
    if kvvoh__jxoy == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(kvvoh__jxoy, types.BaseTuple):
        hbll__vka = []
        nqhsf__aru = 0
        for t in kvvoh__jxoy.types:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                hbll__vka.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>':
                    func.fname = '<lambda_' + str(nqhsf__aru) + '>'
                    nqhsf__aru += 1
                hbll__vka.append(func)
        return [hbll__vka]
    if is_overload_constant_str(kvvoh__jxoy):
        func_name = get_overload_const_str(kvvoh__jxoy)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(kvvoh__jxoy):
        func_name = bodo.utils.typing.get_builtin_function_name(kvvoh__jxoy)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    assert typemap is not None, 'typemap is required for agg UDF handling'
    func = _get_const_agg_func(typemap[rhs.args[0].name], func_ir)
    func.ftype = 'udf'
    func.fname = _get_udf_name(func)
    return func


def get_agg_func_udf(func_ir, f_val, rhs, series_type, typemap):
    if isinstance(f_val, str):
        return get_agg_func(func_ir, f_val, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(f_val):
        func_name = bodo.utils.typing.get_builtin_function_name(f_val)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if isinstance(f_val, (tuple, list)):
        nqhsf__aru = 0
        xqqm__nflpt = []
        for omkrm__xwvnq in f_val:
            func = get_agg_func_udf(func_ir, omkrm__xwvnq, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{nqhsf__aru}>'
                nqhsf__aru += 1
            xqqm__nflpt.append(func)
        return xqqm__nflpt
    else:
        assert is_expr(f_val, 'make_function') or isinstance(f_val, (numba.
            core.registry.CPUDispatcher, types.Dispatcher))
        assert typemap is not None, 'typemap is required for agg UDF handling'
        func = _get_const_agg_func(f_val, func_ir)
        func.ftype = 'udf'
        func.fname = _get_udf_name(func)
        return func


def _get_udf_name(func):
    code = func.code if hasattr(func, 'code') else func.__code__
    onas__ufeud = code.co_name
    return onas__ufeud


def _get_const_agg_func(func_typ, func_ir):
    agg_func = get_overload_const_func(func_typ, func_ir)
    if is_expr(agg_func, 'make_function'):

        def agg_func_wrapper(A):
            return A
        agg_func_wrapper.__code__ = agg_func.code
        agg_func = agg_func_wrapper
        return agg_func
    return agg_func


@infer_global(type)
class TypeDt64(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        if len(args) == 1 and isinstance(args[0], (types.NPDatetime, types.
            NPTimedelta)):
            xkh__ybzu = types.DType(args[0])
            return signature(xkh__ybzu, *args)


@numba.njit(no_cpython_wrapper=True)
def _var_combine(ssqdm_a, mean_a, nobs_a, ssqdm_b, mean_b, nobs_b):
    jzwe__igk = nobs_a + nobs_b
    gsyui__lxs = (nobs_a * mean_a + nobs_b * mean_b) / jzwe__igk
    unoq__aoww = mean_b - mean_a
    cclj__fguf = (ssqdm_a + ssqdm_b + unoq__aoww * unoq__aoww * nobs_a *
        nobs_b / jzwe__igk)
    return cclj__fguf, gsyui__lxs, jzwe__igk


def __special_combine(*args):
    return


@infer_global(__special_combine)
class SpecialCombineTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *unliteral_all(args))


@lower_builtin(__special_combine, types.VarArg(types.Any))
def lower_special_combine(context, builder, sig, args):
    return context.get_dummy_value()


class Aggregate(ir.Stmt):

    def __init__(self, df_out, df_in, key_names, gb_info_in, gb_info_out,
        out_key_vars, df_out_vars, df_in_vars, key_arrs, input_has_index,
        same_index, return_key, loc, func_name, dropna=True, pivot_arr=None,
        pivot_values=None, is_crosstab=False):
        self.df_out = df_out
        self.df_in = df_in
        self.key_names = key_names
        self.gb_info_in = gb_info_in
        self.gb_info_out = gb_info_out
        self.out_key_vars = out_key_vars
        self.df_out_vars = df_out_vars
        self.df_in_vars = df_in_vars
        self.key_arrs = key_arrs
        self.input_has_index = input_has_index
        self.same_index = same_index
        self.return_key = return_key
        self.loc = loc
        self.func_name = func_name
        self.dropna = dropna
        self.pivot_arr = pivot_arr
        self.pivot_values = pivot_values
        self.is_crosstab = is_crosstab

    def __repr__(self):
        aeuy__oktve = ''
        for asrq__ieao, v in self.df_out_vars.items():
            aeuy__oktve += "'{}':{}, ".format(asrq__ieao, v.name)
        xigpf__zxpi = '{}{{{}}}'.format(self.df_out, aeuy__oktve)
        evl__nlycv = ''
        for asrq__ieao, v in self.df_in_vars.items():
            evl__nlycv += "'{}':{}, ".format(asrq__ieao, v.name)
        ymg__auhgy = '{}{{{}}}'.format(self.df_in, evl__nlycv)
        hujq__wzobf = 'pivot {}:{}'.format(self.pivot_arr.name, self.
            pivot_values) if self.pivot_arr is not None else ''
        key_names = ','.join(self.key_names)
        kogng__kxm = ','.join([v.name for v in self.key_arrs])
        return 'aggregate: {} = {} [key: {}:{}] {}'.format(xigpf__zxpi,
            ymg__auhgy, key_names, kogng__kxm, hujq__wzobf)

    def remove_out_col(self, out_col_name):
        self.df_out_vars.pop(out_col_name)
        sonh__lftzm, zcke__ijem = self.gb_info_out.pop(out_col_name)
        if sonh__lftzm is None and not self.is_crosstab:
            return
        viz__uktw = self.gb_info_in[sonh__lftzm]
        if self.pivot_arr is not None:
            self.pivot_values.remove(out_col_name)
            for i, (func, aeuy__oktve) in enumerate(viz__uktw):
                try:
                    aeuy__oktve.remove(out_col_name)
                    if len(aeuy__oktve) == 0:
                        viz__uktw.pop(i)
                        break
                except ValueError as nvn__fdku:
                    continue
        else:
            for i, (func, zoza__wmdhd) in enumerate(viz__uktw):
                if zoza__wmdhd == out_col_name:
                    viz__uktw.pop(i)
                    break
        if len(viz__uktw) == 0:
            self.gb_info_in.pop(sonh__lftzm)
            self.df_in_vars.pop(sonh__lftzm)


def aggregate_usedefs(aggregate_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({v.name for v in aggregate_node.key_arrs})
    use_set.update({v.name for v in aggregate_node.df_in_vars.values()})
    if aggregate_node.pivot_arr is not None:
        use_set.add(aggregate_node.pivot_arr.name)
    def_set.update({v.name for v in aggregate_node.df_out_vars.values()})
    if aggregate_node.out_key_vars is not None:
        def_set.update({v.name for v in aggregate_node.out_key_vars})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Aggregate] = aggregate_usedefs


def remove_dead_aggregate(aggregate_node, lives_no_aliases, lives,
    arg_aliases, alias_map, func_ir, typemap):
    ova__cfco = [iypof__fiaq for iypof__fiaq, oyzzn__sct in aggregate_node.
        df_out_vars.items() if oyzzn__sct.name not in lives]
    for qyuh__hxcc in ova__cfco:
        aggregate_node.remove_out_col(qyuh__hxcc)
    out_key_vars = aggregate_node.out_key_vars
    if out_key_vars is not None and all(v.name not in lives for v in
        out_key_vars):
        aggregate_node.out_key_vars = None
    if len(aggregate_node.df_out_vars
        ) == 0 and aggregate_node.out_key_vars is None:
        return None
    return aggregate_node


ir_utils.remove_dead_extensions[Aggregate] = remove_dead_aggregate


def get_copies_aggregate(aggregate_node, typemap):
    ozzxj__fkn = set(v.name for v in aggregate_node.df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        ozzxj__fkn.update({v.name for v in aggregate_node.out_key_vars})
    return set(), ozzxj__fkn


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for i in range(len(aggregate_node.key_arrs)):
        aggregate_node.key_arrs[i] = replace_vars_inner(aggregate_node.
            key_arrs[i], var_dict)
    for iypof__fiaq in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[iypof__fiaq] = replace_vars_inner(
            aggregate_node.df_in_vars[iypof__fiaq], var_dict)
    for iypof__fiaq in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[iypof__fiaq] = replace_vars_inner(
            aggregate_node.df_out_vars[iypof__fiaq], var_dict)
    if aggregate_node.out_key_vars is not None:
        for i in range(len(aggregate_node.out_key_vars)):
            aggregate_node.out_key_vars[i] = replace_vars_inner(aggregate_node
                .out_key_vars[i], var_dict)
    if aggregate_node.pivot_arr is not None:
        aggregate_node.pivot_arr = replace_vars_inner(aggregate_node.
            pivot_arr, var_dict)


ir_utils.apply_copy_propagate_extensions[Aggregate] = apply_copies_aggregate


def visit_vars_aggregate(aggregate_node, callback, cbdata):
    if debug_prints():
        print('visiting aggregate vars for:', aggregate_node)
        print('cbdata: ', sorted(cbdata.items()))
    for i in range(len(aggregate_node.key_arrs)):
        aggregate_node.key_arrs[i] = visit_vars_inner(aggregate_node.
            key_arrs[i], callback, cbdata)
    for iypof__fiaq in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[iypof__fiaq] = visit_vars_inner(
            aggregate_node.df_in_vars[iypof__fiaq], callback, cbdata)
    for iypof__fiaq in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[iypof__fiaq] = visit_vars_inner(
            aggregate_node.df_out_vars[iypof__fiaq], callback, cbdata)
    if aggregate_node.out_key_vars is not None:
        for i in range(len(aggregate_node.out_key_vars)):
            aggregate_node.out_key_vars[i] = visit_vars_inner(aggregate_node
                .out_key_vars[i], callback, cbdata)
    if aggregate_node.pivot_arr is not None:
        aggregate_node.pivot_arr = visit_vars_inner(aggregate_node.
            pivot_arr, callback, cbdata)


ir_utils.visit_vars_extensions[Aggregate] = visit_vars_aggregate


def aggregate_array_analysis(aggregate_node, equiv_set, typemap, array_analysis
    ):
    assert len(aggregate_node.df_out_vars
        ) > 0 or aggregate_node.out_key_vars is not None or aggregate_node.is_crosstab, 'empty aggregate in array analysis'
    uxg__hait = []
    for legg__vyu in aggregate_node.key_arrs:
        bsv__graop = equiv_set.get_shape(legg__vyu)
        if bsv__graop:
            uxg__hait.append(bsv__graop[0])
    if aggregate_node.pivot_arr is not None:
        bsv__graop = equiv_set.get_shape(aggregate_node.pivot_arr)
        if bsv__graop:
            uxg__hait.append(bsv__graop[0])
    for oyzzn__sct in aggregate_node.df_in_vars.values():
        bsv__graop = equiv_set.get_shape(oyzzn__sct)
        if bsv__graop:
            uxg__hait.append(bsv__graop[0])
    if len(uxg__hait) > 1:
        equiv_set.insert_equiv(*uxg__hait)
    jhe__gkwh = []
    uxg__hait = []
    gkmc__wdfzp = list(aggregate_node.df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        gkmc__wdfzp.extend(aggregate_node.out_key_vars)
    for oyzzn__sct in gkmc__wdfzp:
        pmdqb__nom = typemap[oyzzn__sct.name]
        omxds__fhmdl = array_analysis._gen_shape_call(equiv_set, oyzzn__sct,
            pmdqb__nom.ndim, None, jhe__gkwh)
        equiv_set.insert_equiv(oyzzn__sct, omxds__fhmdl)
        uxg__hait.append(omxds__fhmdl[0])
        equiv_set.define(oyzzn__sct, set())
    if len(uxg__hait) > 1:
        equiv_set.insert_equiv(*uxg__hait)
    return [], jhe__gkwh


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    ndwnu__bxu = Distribution.OneD
    for oyzzn__sct in aggregate_node.df_in_vars.values():
        ndwnu__bxu = Distribution(min(ndwnu__bxu.value, array_dists[
            oyzzn__sct.name].value))
    for legg__vyu in aggregate_node.key_arrs:
        ndwnu__bxu = Distribution(min(ndwnu__bxu.value, array_dists[
            legg__vyu.name].value))
    if aggregate_node.pivot_arr is not None:
        ndwnu__bxu = Distribution(min(ndwnu__bxu.value, array_dists[
            aggregate_node.pivot_arr.name].value))
        array_dists[aggregate_node.pivot_arr.name] = ndwnu__bxu
    for oyzzn__sct in aggregate_node.df_in_vars.values():
        array_dists[oyzzn__sct.name] = ndwnu__bxu
    for legg__vyu in aggregate_node.key_arrs:
        array_dists[legg__vyu.name] = ndwnu__bxu
    ueg__hxl = Distribution.OneD_Var
    for oyzzn__sct in aggregate_node.df_out_vars.values():
        if oyzzn__sct.name in array_dists:
            ueg__hxl = Distribution(min(ueg__hxl.value, array_dists[
                oyzzn__sct.name].value))
    if aggregate_node.out_key_vars is not None:
        for oyzzn__sct in aggregate_node.out_key_vars:
            if oyzzn__sct.name in array_dists:
                ueg__hxl = Distribution(min(ueg__hxl.value, array_dists[
                    oyzzn__sct.name].value))
    ueg__hxl = Distribution(min(ueg__hxl.value, ndwnu__bxu.value))
    for oyzzn__sct in aggregate_node.df_out_vars.values():
        array_dists[oyzzn__sct.name] = ueg__hxl
    if aggregate_node.out_key_vars is not None:
        for tqnq__uti in aggregate_node.out_key_vars:
            array_dists[tqnq__uti.name] = ueg__hxl
    if ueg__hxl != Distribution.OneD_Var:
        for legg__vyu in aggregate_node.key_arrs:
            array_dists[legg__vyu.name] = ueg__hxl
        if aggregate_node.pivot_arr is not None:
            array_dists[aggregate_node.pivot_arr.name] = ueg__hxl
        for oyzzn__sct in aggregate_node.df_in_vars.values():
            array_dists[oyzzn__sct.name] = ueg__hxl


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for oyzzn__sct in agg_node.df_out_vars.values():
        definitions[oyzzn__sct.name].append(agg_node)
    if agg_node.out_key_vars is not None:
        for tqnq__uti in agg_node.out_key_vars:
            definitions[tqnq__uti.name].append(agg_node)
    return definitions


ir_utils.build_defs_extensions[Aggregate] = build_agg_definitions


def __update_redvars():
    pass


@infer_global(__update_redvars)
class UpdateDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *args)


def __combine_redvars():
    pass


@infer_global(__combine_redvars)
class CombineDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(types.void, *args)


def __eval_res():
    pass


@infer_global(__eval_res)
class EvalDummyTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        return signature(args[0].dtype, *args)


def agg_distributed_run(agg_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    if array_dists is not None:
        parallel = True
        for v in (list(agg_node.df_in_vars.values()) + list(agg_node.
            df_out_vars.values()) + agg_node.key_arrs):
            if array_dists[v.name
                ] != distributed_pass.Distribution.OneD and array_dists[v.name
                ] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    nmy__ifr = tuple(typemap[v.name] for v in agg_node.key_arrs)
    dyfgj__efq = [v for bzt__lbx, v in agg_node.df_in_vars.items()]
    yrmi__dyb = [v for bzt__lbx, v in agg_node.df_out_vars.items()]
    in_col_typs = []
    hbll__vka = []
    if agg_node.pivot_arr is not None:
        for sonh__lftzm, viz__uktw in agg_node.gb_info_in.items():
            for func, zcke__ijem in viz__uktw:
                if sonh__lftzm is not None:
                    in_col_typs.append(typemap[agg_node.df_in_vars[
                        sonh__lftzm].name])
                hbll__vka.append(func)
    else:
        for sonh__lftzm, func in agg_node.gb_info_out.values():
            if sonh__lftzm is not None:
                in_col_typs.append(typemap[agg_node.df_in_vars[sonh__lftzm]
                    .name])
            hbll__vka.append(func)
    out_col_typs = tuple(typemap[v.name] for v in yrmi__dyb)
    pivot_typ = types.none if agg_node.pivot_arr is None else typemap[agg_node
        .pivot_arr.name]
    arg_typs = tuple(nmy__ifr + tuple(typemap[v.name] for v in dyfgj__efq) +
        (pivot_typ,))
    bndx__aregc = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for i, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            bndx__aregc.update({f'in_cat_dtype_{i}': in_col_typ})
    for i, qlt__rzy in enumerate(out_col_typs):
        if isinstance(qlt__rzy, bodo.CategoricalArrayType):
            bndx__aregc.update({f'out_cat_dtype_{i}': qlt__rzy})
    udf_func_struct = get_udf_func_struct(hbll__vka, agg_node.
        input_has_index, in_col_typs, out_col_typs, typingctx, targetctx,
        pivot_typ, agg_node.pivot_values, agg_node.is_crosstab)
    oyp__cfiul = gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs,
        parallel, udf_func_struct)
    bndx__aregc.update({'pd': pd, 'pre_alloc_string_array':
        pre_alloc_string_array, 'pre_alloc_binary_array':
        pre_alloc_binary_array, 'pre_alloc_array_item_array':
        pre_alloc_array_item_array, 'string_array_type': string_array_type,
        'alloc_decimal_array': alloc_decimal_array, 'array_to_info':
        array_to_info, 'arr_info_list_to_table': arr_info_list_to_table,
        'coerce_to_array': bodo.utils.conversion.coerce_to_array,
        'groupby_and_aggregate': groupby_and_aggregate,
        'pivot_groupby_and_aggregate': pivot_groupby_and_aggregate,
        'compute_node_partition_by_hash': compute_node_partition_by_hash,
        'info_from_table': info_from_table, 'info_to_array': info_to_array,
        'delete_info_decref_array': delete_info_decref_array,
        'delete_table': delete_table, 'add_agg_cfunc_sym':
        add_agg_cfunc_sym, 'get_agg_udf_addr': get_agg_udf_addr,
        'delete_table_decref_arrays': delete_table_decref_arrays})
    if udf_func_struct is not None:
        if udf_func_struct.regular_udfs:
            bndx__aregc.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            bndx__aregc.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    kcfo__vgbq = compile_to_numba_ir(oyp__cfiul, bndx__aregc, typingctx=
        typingctx, targetctx=targetctx, arg_typs=arg_typs, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    xbc__yayg = []
    if agg_node.pivot_arr is None:
        phoz__shz = agg_node.key_arrs[0].scope
        loc = agg_node.loc
        iiik__lzxr = ir.Var(phoz__shz, mk_unique_var('dummy_none'), loc)
        typemap[iiik__lzxr.name] = types.none
        xbc__yayg.append(ir.Assign(ir.Const(None, loc), iiik__lzxr, loc))
        dyfgj__efq.append(iiik__lzxr)
    else:
        dyfgj__efq.append(agg_node.pivot_arr)
    replace_arg_nodes(kcfo__vgbq, agg_node.key_arrs + dyfgj__efq)
    cdhed__nccow = kcfo__vgbq.body[-3]
    assert is_assign(cdhed__nccow) and isinstance(cdhed__nccow.value, ir.Expr
        ) and cdhed__nccow.value.op == 'build_tuple'
    xbc__yayg += kcfo__vgbq.body[:-3]
    gkmc__wdfzp = list(agg_node.df_out_vars.values())
    if agg_node.out_key_vars is not None:
        gkmc__wdfzp += agg_node.out_key_vars
    for i, lky__zog in enumerate(gkmc__wdfzp):
        rsyik__smbw = cdhed__nccow.value.items[i]
        xbc__yayg.append(ir.Assign(rsyik__smbw, lky__zog, lky__zog.loc))
    return xbc__yayg


distributed_pass.distributed_run_extensions[Aggregate] = agg_distributed_run


def get_numba_set(dtype):
    pass


@infer_global(get_numba_set)
class GetNumbaSetTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        arr = args[0]
        dtype = types.Tuple([t.dtype for t in arr.types]) if isinstance(arr,
            types.BaseTuple) else arr.dtype
        if isinstance(arr, types.BaseTuple) and len(arr.types) == 1:
            dtype = arr.types[0].dtype
        return signature(types.Set(dtype), *args)


@lower_builtin(get_numba_set, types.Any)
def lower_get_numba_set(context, builder, sig, args):
    return numba.cpython.setobj.set_empty_constructor(context, builder, sig,
        args)


@infer_global(bool)
class BoolNoneTyper(AbstractTemplate):

    def generic(self, args, kws):
        assert not kws
        assert len(args) == 1
        iijp__cocx = args[0]
        if iijp__cocx == types.none:
            return signature(types.boolean, *args)


@lower_builtin(bool, types.none)
def lower_column_mean_impl(context, builder, sig, args):
    rvce__zson = context.compile_internal(builder, lambda a: False, sig, args)
    return rvce__zson


def setitem_array_with_str(arr, i, v):
    return


@overload(setitem_array_with_str)
def setitem_array_with_str_overload(arr, i, val):
    if arr == string_array_type:

        def setitem_str_arr(arr, i, val):
            arr[i] = val
        return setitem_str_arr
    if val == string_type:
        return lambda arr, i, val: None

    def setitem_impl(arr, i, val):
        arr[i] = val
    return setitem_impl


def _gen_dummy_alloc(t, colnum=0, is_input=False):
    if isinstance(t, IntegerArrayType):
        fft__pssen = IntDtype(t.dtype).name
        assert fft__pssen.endswith('Dtype()')
        fft__pssen = fft__pssen[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{fft__pssen}'))"
            )
    elif isinstance(t, BooleanArrayType):
        return (
            'bodo.libs.bool_arr_ext.init_bool_array(np.empty(0, np.bool_), np.empty(0, np.uint8))'
            )
    elif isinstance(t, StringArrayType):
        return 'pre_alloc_string_array(1, 1)'
    elif isinstance(t, BinaryArrayType):
        return 'pre_alloc_binary_array(1, 1)'
    elif t == ArrayItemArrayType(string_array_type):
        return 'pre_alloc_array_item_array(1, (1, 1), string_array_type)'
    elif isinstance(t, DecimalArrayType):
        return 'alloc_decimal_array(1, {}, {})'.format(t.precision, t.scale)
    elif isinstance(t, DatetimeDateArrayType):
        return (
            'bodo.hiframes.datetime_date_ext.init_datetime_date_array(np.empty(1, np.int64), np.empty(1, np.uint8))'
            )
    elif isinstance(t, bodo.CategoricalArrayType):
        if t.dtype.categories is None:
            raise BodoError(
                'Groupby agg operations on Categorical types require constant categories'
                )
        jtoi__ikk = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {jtoi__ikk}_cat_dtype_{colnum})')
    else:
        return 'np.empty(1, {})'.format(_get_np_dtype(t.dtype))


def _get_np_dtype(t):
    if t == types.bool_:
        return 'np.bool_'
    if t == types.NPDatetime('ns'):
        return 'dt64_dtype'
    if t == types.NPTimedelta('ns'):
        return 'td64_dtype'
    return 'np.{}'.format(t)


def gen_update_cb(udf_func_struct, allfuncs, n_keys, data_in_typs_,
    out_data_typs, do_combine, func_idx_to_in_col, label_suffix):
    qif__dsz = udf_func_struct.var_typs
    ejsa__obv = len(qif__dsz)
    rrmx__ptq = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    rrmx__ptq += '    if is_null_pointer(in_table):\n'
    rrmx__ptq += '        return\n'
    rrmx__ptq += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in qif__dsz]), ',' if
        len(qif__dsz) == 1 else '')
    rmkrv__dybla = n_keys
    mxun__fqbx = []
    redvar_offsets = []
    jcvwt__ugck = []
    if do_combine:
        for i, omkrm__xwvnq in enumerate(allfuncs):
            if omkrm__xwvnq.ftype != 'udf':
                rmkrv__dybla += omkrm__xwvnq.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(rmkrv__dybla, rmkrv__dybla +
                    omkrm__xwvnq.n_redvars))
                rmkrv__dybla += omkrm__xwvnq.n_redvars
                jcvwt__ugck.append(data_in_typs_[func_idx_to_in_col[i]])
                mxun__fqbx.append(func_idx_to_in_col[i] + n_keys)
    else:
        for i, omkrm__xwvnq in enumerate(allfuncs):
            if omkrm__xwvnq.ftype != 'udf':
                rmkrv__dybla += omkrm__xwvnq.ncols_post_shuffle
            else:
                redvar_offsets += list(range(rmkrv__dybla + 1, rmkrv__dybla +
                    1 + omkrm__xwvnq.n_redvars))
                rmkrv__dybla += omkrm__xwvnq.n_redvars + 1
                jcvwt__ugck.append(data_in_typs_[func_idx_to_in_col[i]])
                mxun__fqbx.append(func_idx_to_in_col[i] + n_keys)
    assert len(redvar_offsets) == ejsa__obv
    zwbb__vgszi = len(jcvwt__ugck)
    cvxd__irxna = []
    for i, t in enumerate(jcvwt__ugck):
        cvxd__irxna.append(_gen_dummy_alloc(t, i, True))
    rrmx__ptq += '    data_in_dummy = ({}{})\n'.format(','.join(cvxd__irxna
        ), ',' if len(jcvwt__ugck) == 1 else '')
    rrmx__ptq += """
    # initialize redvar cols
"""
    rrmx__ptq += '    init_vals = __init_func()\n'
    for i in range(ejsa__obv):
        rrmx__ptq += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(i, redvar_offsets[i], i))
        rrmx__ptq += '    incref(redvar_arr_{})\n'.format(i)
        rrmx__ptq += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(i, i)
    rrmx__ptq += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(i) for i in range(ejsa__obv)]), ',' if ejsa__obv == 1 else '')
    rrmx__ptq += '\n'
    for i in range(zwbb__vgszi):
        rrmx__ptq += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(i, mxun__fqbx[i], i))
        rrmx__ptq += '    incref(data_in_{})\n'.format(i)
    rrmx__ptq += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(i) for i in range(zwbb__vgszi)]), ',' if zwbb__vgszi == 1 else
        '')
    rrmx__ptq += '\n'
    rrmx__ptq += '    for i in range(len(data_in_0)):\n'
    rrmx__ptq += '        w_ind = row_to_group[i]\n'
    rrmx__ptq += '        if w_ind != -1:\n'
    rrmx__ptq += (
        '            __update_redvars(redvars, data_in, w_ind, i, pivot_arr=None)\n'
        )
    yfz__fzxg = {}
    exec(rrmx__ptq, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, yfz__fzxg)
    return yfz__fzxg['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, out_data_typs,
    label_suffix):
    qif__dsz = udf_func_struct.var_typs
    ejsa__obv = len(qif__dsz)
    rrmx__ptq = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    rrmx__ptq += '    if is_null_pointer(in_table):\n'
    rrmx__ptq += '        return\n'
    rrmx__ptq += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in qif__dsz]), ',' if
        len(qif__dsz) == 1 else '')
    bmnrq__aduok = n_keys
    jgu__wvgxp = n_keys
    lfkn__mumqp = []
    zyqd__lob = []
    for omkrm__xwvnq in allfuncs:
        if omkrm__xwvnq.ftype != 'udf':
            bmnrq__aduok += omkrm__xwvnq.ncols_pre_shuffle
            jgu__wvgxp += omkrm__xwvnq.ncols_post_shuffle
        else:
            lfkn__mumqp += list(range(bmnrq__aduok, bmnrq__aduok +
                omkrm__xwvnq.n_redvars))
            zyqd__lob += list(range(jgu__wvgxp + 1, jgu__wvgxp + 1 +
                omkrm__xwvnq.n_redvars))
            bmnrq__aduok += omkrm__xwvnq.n_redvars
            jgu__wvgxp += 1 + omkrm__xwvnq.n_redvars
    assert len(lfkn__mumqp) == ejsa__obv
    rrmx__ptq += """
    # initialize redvar cols
"""
    rrmx__ptq += '    init_vals = __init_func()\n'
    for i in range(ejsa__obv):
        rrmx__ptq += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(i, zyqd__lob[i], i))
        rrmx__ptq += '    incref(redvar_arr_{})\n'.format(i)
        rrmx__ptq += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(i, i)
    rrmx__ptq += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(i) for i in range(ejsa__obv)]), ',' if ejsa__obv == 1 else '')
    rrmx__ptq += '\n'
    for i in range(ejsa__obv):
        rrmx__ptq += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(i, lfkn__mumqp[i], i))
        rrmx__ptq += '    incref(recv_redvar_arr_{})\n'.format(i)
    rrmx__ptq += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(i) for i in range(ejsa__obv)]), ',' if 
        ejsa__obv == 1 else '')
    rrmx__ptq += '\n'
    if ejsa__obv:
        rrmx__ptq += '    for i in range(len(recv_redvar_arr_0)):\n'
        rrmx__ptq += '        w_ind = row_to_group[i]\n'
        rrmx__ptq += (
            '        __combine_redvars(redvars, recv_redvars, w_ind, i, pivot_arr=None)\n'
            )
    yfz__fzxg = {}
    exec(rrmx__ptq, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, yfz__fzxg)
    return yfz__fzxg['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    qif__dsz = udf_func_struct.var_typs
    ejsa__obv = len(qif__dsz)
    rmkrv__dybla = n_keys
    redvar_offsets = []
    kntvc__otns = []
    out_data_typs = []
    for i, omkrm__xwvnq in enumerate(allfuncs):
        if omkrm__xwvnq.ftype != 'udf':
            rmkrv__dybla += omkrm__xwvnq.ncols_post_shuffle
        else:
            kntvc__otns.append(rmkrv__dybla)
            redvar_offsets += list(range(rmkrv__dybla + 1, rmkrv__dybla + 1 +
                omkrm__xwvnq.n_redvars))
            rmkrv__dybla += 1 + omkrm__xwvnq.n_redvars
            out_data_typs.append(out_data_typs_[i])
    assert len(redvar_offsets) == ejsa__obv
    zwbb__vgszi = len(out_data_typs)
    rrmx__ptq = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    rrmx__ptq += '    if is_null_pointer(table):\n'
    rrmx__ptq += '        return\n'
    rrmx__ptq += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in qif__dsz]), ',' if
        len(qif__dsz) == 1 else '')
    rrmx__ptq += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in
        out_data_typs]), ',' if len(out_data_typs) == 1 else '')
    for i in range(ejsa__obv):
        rrmx__ptq += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(i, redvar_offsets[i], i))
        rrmx__ptq += '    incref(redvar_arr_{})\n'.format(i)
    rrmx__ptq += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(i) for i in range(ejsa__obv)]), ',' if ejsa__obv == 1 else '')
    rrmx__ptq += '\n'
    for i in range(zwbb__vgszi):
        rrmx__ptq += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(i, kntvc__otns[i], i))
        rrmx__ptq += '    incref(data_out_{})\n'.format(i)
    rrmx__ptq += '    data_out = ({}{})\n'.format(','.join(['data_out_{}'.
        format(i) for i in range(zwbb__vgszi)]), ',' if zwbb__vgszi == 1 else
        '')
    rrmx__ptq += '\n'
    rrmx__ptq += '    for i in range(len(data_out_0)):\n'
    rrmx__ptq += '        __eval_res(redvars, data_out, i)\n'
    yfz__fzxg = {}
    exec(rrmx__ptq, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, yfz__fzxg)
    return yfz__fzxg['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    rmkrv__dybla = n_keys
    uwa__sexzi = []
    for i, omkrm__xwvnq in enumerate(allfuncs):
        if omkrm__xwvnq.ftype == 'gen_udf':
            uwa__sexzi.append(rmkrv__dybla)
            rmkrv__dybla += 1
        elif omkrm__xwvnq.ftype != 'udf':
            rmkrv__dybla += omkrm__xwvnq.ncols_post_shuffle
        else:
            rmkrv__dybla += omkrm__xwvnq.n_redvars + 1
    rrmx__ptq = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    rrmx__ptq += '    if num_groups == 0:\n'
    rrmx__ptq += '        return\n'
    for i, func in enumerate(udf_func_struct.general_udf_funcs):
        rrmx__ptq += '    # col {}\n'.format(i)
        rrmx__ptq += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(uwa__sexzi[i], i))
        rrmx__ptq += '    incref(out_col)\n'
        rrmx__ptq += '    for j in range(num_groups):\n'
        rrmx__ptq += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(i, i))
        rrmx__ptq += '        incref(in_col)\n'
        rrmx__ptq += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(i))
    bndx__aregc = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    zjz__rhemo = 0
    for i, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[zjz__rhemo]
        bndx__aregc['func_{}'.format(zjz__rhemo)] = func
        bndx__aregc['in_col_{}_typ'.format(zjz__rhemo)] = in_col_typs[
            func_idx_to_in_col[i]]
        bndx__aregc['out_col_{}_typ'.format(zjz__rhemo)] = out_col_typs[i]
        zjz__rhemo += 1
    yfz__fzxg = {}
    exec(rrmx__ptq, bndx__aregc, yfz__fzxg)
    omkrm__xwvnq = yfz__fzxg['bodo_gb_apply_general_udfs{}'.format(
        label_suffix)]
    rgpqs__pecjx = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(rgpqs__pecjx, nopython=True)(omkrm__xwvnq)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs, parallel,
    udf_func_struct):
    nqrt__qop = agg_node.pivot_arr is not None
    if agg_node.same_index:
        assert agg_node.input_has_index
    if agg_node.pivot_values is None:
        ysgw__hpkb = 1
    else:
        ysgw__hpkb = len(agg_node.pivot_values)
    qbgay__nxvg = tuple('key_' + sanitize_varname(asrq__ieao) for
        asrq__ieao in agg_node.key_names)
    lylnr__vph = {asrq__ieao: 'in_{}'.format(sanitize_varname(asrq__ieao)) for
        asrq__ieao in agg_node.gb_info_in.keys() if asrq__ieao is not None}
    ypeev__vfkzj = {asrq__ieao: ('out_' + sanitize_varname(asrq__ieao)) for
        asrq__ieao in agg_node.gb_info_out.keys()}
    n_keys = len(agg_node.key_names)
    dexg__sgi = ', '.join(qbgay__nxvg)
    koh__wab = ', '.join(lylnr__vph.values())
    if koh__wab != '':
        koh__wab = ', ' + koh__wab
    rrmx__ptq = 'def agg_top({}{}{}, pivot_arr):\n'.format(dexg__sgi,
        koh__wab, ', index_arg' if agg_node.input_has_index else '')
    if nqrt__qop:
        ibv__egvlj = []
        for sonh__lftzm, viz__uktw in agg_node.gb_info_in.items():
            if sonh__lftzm is not None:
                for func, zcke__ijem in viz__uktw:
                    ibv__egvlj.append(lylnr__vph[sonh__lftzm])
    else:
        ibv__egvlj = tuple(lylnr__vph[sonh__lftzm] for sonh__lftzm,
            zcke__ijem in agg_node.gb_info_out.values() if sonh__lftzm is not
            None)
    fpc__yun = qbgay__nxvg + tuple(ibv__egvlj)
    rrmx__ptq += '    info_list = [{}{}{}]\n'.format(', '.join(
        'array_to_info({})'.format(a) for a in fpc__yun), 
        ', array_to_info(index_arg)' if agg_node.input_has_index else '', 
        ', array_to_info(pivot_arr)' if agg_node.is_crosstab else '')
    rrmx__ptq += '    table = arr_info_list_to_table(info_list)\n'
    for i, asrq__ieao in enumerate(agg_node.gb_info_out.keys()):
        oombz__ujtj = ypeev__vfkzj[asrq__ieao] + '_dummy'
        qlt__rzy = out_col_typs[i]
        sonh__lftzm, func = agg_node.gb_info_out[asrq__ieao]
        if isinstance(func, pytypes.SimpleNamespace) and func.fname in ['min',
            'max', 'shift'] and isinstance(qlt__rzy, bodo.CategoricalArrayType
            ):
            rrmx__ptq += '    {} = {}\n'.format(oombz__ujtj, lylnr__vph[
                sonh__lftzm])
        else:
            rrmx__ptq += '    {} = {}\n'.format(oombz__ujtj,
                _gen_dummy_alloc(qlt__rzy, i, False))
    do_combine = parallel
    allfuncs = []
    lon__sgqlj = []
    func_idx_to_in_col = []
    hthp__zcyy = []
    cigo__pvrrn = False
    jccbs__tdnqu = 1
    igah__zpwq = -1
    arjwg__lhpoj = 0
    stir__ivxs = 0
    if not nqrt__qop:
        hbll__vka = [func for zcke__ijem, func in agg_node.gb_info_out.values()
            ]
    else:
        hbll__vka = [func for func, zcke__ijem in viz__uktw for viz__uktw in
            agg_node.gb_info_in.values()]
    for lrkka__jfy, func in enumerate(hbll__vka):
        lon__sgqlj.append(len(allfuncs))
        if func.ftype in {'median', 'nunique'}:
            do_combine = False
        if func.ftype in list_cumulative:
            arjwg__lhpoj += 1
        if hasattr(func, 'skipdropna'):
            cigo__pvrrn = func.skipdropna
        if func.ftype == 'shift':
            jccbs__tdnqu = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            stir__ivxs = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            igah__zpwq = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(lrkka__jfy)
        if func.ftype == 'udf':
            hthp__zcyy.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            hthp__zcyy.append(0)
            do_combine = False
    lon__sgqlj.append(len(allfuncs))
    if agg_node.is_crosstab:
        assert len(agg_node.gb_info_out
            ) == ysgw__hpkb, 'invalid number of groupby outputs for pivot'
    else:
        assert len(agg_node.gb_info_out) == len(allfuncs
            ) * ysgw__hpkb, 'invalid number of groupby outputs'
    if arjwg__lhpoj > 0:
        if arjwg__lhpoj != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    if udf_func_struct is not None:
        udtf__wzac = next_label()
        if udf_func_struct.regular_udfs:
            rgpqs__pecjx = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            npc__yfmzm = numba.cfunc(rgpqs__pecjx, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs,
                out_col_typs, do_combine, func_idx_to_in_col, udtf__wzac))
            fcy__lla = numba.cfunc(rgpqs__pecjx, nopython=True)(gen_combine_cb
                (udf_func_struct, allfuncs, n_keys, out_col_typs, udtf__wzac))
            gqftb__osge = numba.cfunc('void(voidptr)', nopython=True)(
                gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_col_typs,
                udtf__wzac))
            udf_func_struct.set_regular_cfuncs(npc__yfmzm, fcy__lla,
                gqftb__osge)
            for sny__nyc in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[sny__nyc.native_name] = sny__nyc
                gb_agg_cfunc_addr[sny__nyc.native_name] = sny__nyc.address
        if udf_func_struct.general_udfs:
            ndm__uus = gen_general_udf_cb(udf_func_struct, allfuncs, n_keys,
                in_col_typs, out_col_typs, func_idx_to_in_col, udtf__wzac)
            udf_func_struct.set_general_cfunc(ndm__uus)
        ouc__cwnzt = []
        ylo__dnrr = 0
        i = 0
        for oombz__ujtj, omkrm__xwvnq in zip(ypeev__vfkzj.values(), allfuncs):
            if omkrm__xwvnq.ftype in ('udf', 'gen_udf'):
                ouc__cwnzt.append(oombz__ujtj + '_dummy')
                for cjkvi__enjp in range(ylo__dnrr, ylo__dnrr + hthp__zcyy[i]):
                    ouc__cwnzt.append('data_redvar_dummy_' + str(cjkvi__enjp))
                ylo__dnrr += hthp__zcyy[i]
                i += 1
        if udf_func_struct.regular_udfs:
            qif__dsz = udf_func_struct.var_typs
            for i, t in enumerate(qif__dsz):
                rrmx__ptq += ('    data_redvar_dummy_{} = np.empty(1, {})\n'
                    .format(i, _get_np_dtype(t)))
        rrmx__ptq += '    out_info_list_dummy = [{}]\n'.format(', '.join(
            'array_to_info({})'.format(a) for a in ouc__cwnzt))
        rrmx__ptq += (
            '    udf_table_dummy = arr_info_list_to_table(out_info_list_dummy)\n'
            )
        if udf_func_struct.regular_udfs:
            rrmx__ptq += "    add_agg_cfunc_sym(cpp_cb_update, '{}')\n".format(
                npc__yfmzm.native_name)
            rrmx__ptq += ("    add_agg_cfunc_sym(cpp_cb_combine, '{}')\n".
                format(fcy__lla.native_name))
            rrmx__ptq += "    add_agg_cfunc_sym(cpp_cb_eval, '{}')\n".format(
                gqftb__osge.native_name)
            rrmx__ptq += ("    cpp_cb_update_addr = get_agg_udf_addr('{}')\n"
                .format(npc__yfmzm.native_name))
            rrmx__ptq += ("    cpp_cb_combine_addr = get_agg_udf_addr('{}')\n"
                .format(fcy__lla.native_name))
            rrmx__ptq += ("    cpp_cb_eval_addr = get_agg_udf_addr('{}')\n"
                .format(gqftb__osge.native_name))
        else:
            rrmx__ptq += '    cpp_cb_update_addr = 0\n'
            rrmx__ptq += '    cpp_cb_combine_addr = 0\n'
            rrmx__ptq += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            sny__nyc = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[sny__nyc.native_name] = sny__nyc
            gb_agg_cfunc_addr[sny__nyc.native_name] = sny__nyc.address
            rrmx__ptq += ("    add_agg_cfunc_sym(cpp_cb_general, '{}')\n".
                format(sny__nyc.native_name))
            rrmx__ptq += ("    cpp_cb_general_addr = get_agg_udf_addr('{}')\n"
                .format(sny__nyc.native_name))
        else:
            rrmx__ptq += '    cpp_cb_general_addr = 0\n'
    else:
        rrmx__ptq += (
            '    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])\n'
            )
        rrmx__ptq += '    cpp_cb_update_addr = 0\n'
        rrmx__ptq += '    cpp_cb_combine_addr = 0\n'
        rrmx__ptq += '    cpp_cb_eval_addr = 0\n'
        rrmx__ptq += '    cpp_cb_general_addr = 0\n'
    rrmx__ptq += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(', '
        .join([str(supported_agg_funcs.index(omkrm__xwvnq.ftype)) for
        omkrm__xwvnq in allfuncs] + ['0']))
    rrmx__ptq += '    func_offsets = np.array({}, dtype=np.int32)\n'.format(str
        (lon__sgqlj))
    if len(hthp__zcyy) > 0:
        rrmx__ptq += '    udf_ncols = np.array({}, dtype=np.int32)\n'.format(
            str(hthp__zcyy))
    else:
        rrmx__ptq += '    udf_ncols = np.array([0], np.int32)\n'
    if nqrt__qop:
        rrmx__ptq += '    arr_type = coerce_to_array({})\n'.format(agg_node
            .pivot_values)
        rrmx__ptq += '    arr_info = array_to_info(arr_type)\n'
        rrmx__ptq += (
            '    dispatch_table = arr_info_list_to_table([arr_info])\n')
        rrmx__ptq += '    pivot_info = array_to_info(pivot_arr)\n'
        rrmx__ptq += (
            '    dispatch_info = arr_info_list_to_table([pivot_info])\n')
        rrmx__ptq += (
            """    out_table = pivot_groupby_and_aggregate(table, {}, dispatch_table, dispatch_info, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, agg_node.
            is_crosstab, cigo__pvrrn, agg_node.return_key, agg_node.same_index)
            )
        rrmx__ptq += '    delete_info_decref_array(pivot_info)\n'
        rrmx__ptq += '    delete_info_decref_array(arr_info)\n'
    else:
        rrmx__ptq += (
            """    out_table = groupby_and_aggregate(table, {}, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, cigo__pvrrn,
            jccbs__tdnqu, stir__ivxs, igah__zpwq, agg_node.return_key,
            agg_node.same_index, agg_node.dropna))
    qdqpl__gagj = 0
    if agg_node.return_key:
        for i, xqdh__coyxc in enumerate(qbgay__nxvg):
            rrmx__ptq += (
                '    {} = info_to_array(info_from_table(out_table, {}), {})\n'
                .format(xqdh__coyxc, qdqpl__gagj, xqdh__coyxc))
            qdqpl__gagj += 1
    for oombz__ujtj in ypeev__vfkzj.values():
        rrmx__ptq += (
            '    {} = info_to_array(info_from_table(out_table, {}), {})\n'.
            format(oombz__ujtj, qdqpl__gagj, oombz__ujtj + '_dummy'))
        qdqpl__gagj += 1
    if agg_node.same_index:
        rrmx__ptq += (
            """    out_index_arg = info_to_array(info_from_table(out_table, {}), index_arg)
"""
            .format(qdqpl__gagj))
        qdqpl__gagj += 1
    rrmx__ptq += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    rrmx__ptq += '    delete_table_decref_arrays(table)\n'
    rrmx__ptq += '    delete_table_decref_arrays(udf_table_dummy)\n'
    rrmx__ptq += '    delete_table(out_table)\n'
    rrmx__ptq += f'    ev_clean.finalize()\n'
    ptf__yyj = tuple(ypeev__vfkzj.values())
    if agg_node.return_key:
        ptf__yyj += tuple(qbgay__nxvg)
    rrmx__ptq += '    return ({},{})\n'.format(', '.join(ptf__yyj), 
        ' out_index_arg,' if agg_node.same_index else '')
    yfz__fzxg = {}
    exec(rrmx__ptq, {}, yfz__fzxg)
    ulpo__adc = yfz__fzxg['agg_top']
    return ulpo__adc


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for mdv__chom in block.body:
            if is_call_assign(mdv__chom) and find_callname(f_ir, mdv__chom.
                value) == ('len', 'builtins') and mdv__chom.value.args[0
                ].name == f_ir.arg_names[0]:
                dsmki__xpdpm = get_definition(f_ir, mdv__chom.value.func)
                dsmki__xpdpm.name = 'dummy_agg_count'
                dsmki__xpdpm.value = dummy_agg_count
    ect__lopg = get_name_var_table(f_ir.blocks)
    ach__mymv = {}
    for name, zcke__ijem in ect__lopg.items():
        ach__mymv[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, ach__mymv)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    kkda__gqdpl = numba.core.compiler.Flags()
    kkda__gqdpl.nrt = True
    fcatl__pmar = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, kkda__gqdpl)
    fcatl__pmar.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, ekdk__vec, calltypes, zcke__ijem = (numba.core.typed_passes.
        type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    wncjy__ldlc = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    smpo__ikvqb = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    bvoby__beb = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    htkqv__ocq = bvoby__beb(typemap, calltypes)
    pm = smpo__ikvqb(typingctx, targetctx, None, f_ir, typemap, ekdk__vec,
        calltypes, htkqv__ocq, {}, kkda__gqdpl, None)
    lucv__eojiq = (numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline(pm))
    pm = smpo__ikvqb(typingctx, targetctx, None, f_ir, typemap, ekdk__vec,
        calltypes, htkqv__ocq, {}, kkda__gqdpl, lucv__eojiq)
    hdtay__xxnn = numba.core.typed_passes.InlineOverloads()
    hdtay__xxnn.run_pass(pm)
    spf__gjf = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    spf__gjf.run()
    for block in f_ir.blocks.values():
        for mdv__chom in block.body:
            if is_assign(mdv__chom) and isinstance(mdv__chom.value, (ir.Arg,
                ir.Var)) and isinstance(typemap[mdv__chom.target.name],
                SeriesType):
                pmdqb__nom = typemap.pop(mdv__chom.target.name)
                typemap[mdv__chom.target.name] = pmdqb__nom.data
            if is_call_assign(mdv__chom) and find_callname(f_ir, mdv__chom.
                value) == ('get_series_data', 'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[mdv__chom.target.name].remove(mdv__chom.value
                    )
                mdv__chom.value = mdv__chom.value.args[0]
                f_ir._definitions[mdv__chom.target.name].append(mdv__chom.value
                    )
            if is_call_assign(mdv__chom) and find_callname(f_ir, mdv__chom.
                value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[mdv__chom.target.name].remove(mdv__chom.value
                    )
                mdv__chom.value = ir.Const(False, mdv__chom.loc)
                f_ir._definitions[mdv__chom.target.name].append(mdv__chom.value
                    )
            if is_call_assign(mdv__chom) and find_callname(f_ir, mdv__chom.
                value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[mdv__chom.target.name].remove(mdv__chom.value
                    )
                mdv__chom.value = ir.Const(False, mdv__chom.loc)
                f_ir._definitions[mdv__chom.target.name].append(mdv__chom.value
                    )
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    dhlvo__nsjr = numba.parfors.parfor.PreParforPass(f_ir, typemap,
        calltypes, typingctx, targetctx, wncjy__ldlc)
    dhlvo__nsjr.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    wrbxf__koelp = numba.core.compiler.StateDict()
    wrbxf__koelp.func_ir = f_ir
    wrbxf__koelp.typemap = typemap
    wrbxf__koelp.calltypes = calltypes
    wrbxf__koelp.typingctx = typingctx
    wrbxf__koelp.targetctx = targetctx
    wrbxf__koelp.return_type = ekdk__vec
    numba.core.rewrites.rewrite_registry.apply('after-inference', wrbxf__koelp)
    rjxx__wstj = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        ekdk__vec, typingctx, targetctx, wncjy__ldlc, kkda__gqdpl, {})
    rjxx__wstj.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            kvxs__eao = ctypes.pythonapi.PyCell_Get
            kvxs__eao.restype = ctypes.py_object
            kvxs__eao.argtypes = ctypes.py_object,
            cbvcd__rci = tuple(kvxs__eao(hcpu__pkqf) for hcpu__pkqf in closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            cbvcd__rci = closure.items
        assert len(code.co_freevars) == len(cbvcd__rci)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks, cbvcd__rci
            )


class RegularUDFGenerator(object):

    def __init__(self, in_col_types, out_col_types, pivot_typ, pivot_values,
        is_crosstab, typingctx, targetctx):
        self.in_col_types = in_col_types
        self.out_col_types = out_col_types
        self.pivot_typ = pivot_typ
        self.pivot_values = pivot_values
        self.is_crosstab = is_crosstab
        self.typingctx = typingctx
        self.targetctx = targetctx
        self.all_reduce_vars = []
        self.all_vartypes = []
        self.all_init_nodes = []
        self.all_eval_funcs = []
        self.all_update_funcs = []
        self.all_combine_funcs = []
        self.curr_offset = 0
        self.redvar_offsets = [0]

    def add_udf(self, in_col_typ, func):
        tyr__hlg = SeriesType(in_col_typ.dtype, in_col_typ, None, string_type)
        f_ir, pm = compile_to_optimized_ir(func, (tyr__hlg,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        ycmwn__ncp, arr_var = _rm_arg_agg_block(block, pm.typemap)
        kpf__xyw = -1
        for i, mdv__chom in enumerate(ycmwn__ncp):
            if isinstance(mdv__chom, numba.parfors.parfor.Parfor):
                assert kpf__xyw == -1, 'only one parfor for aggregation function'
                kpf__xyw = i
        parfor = None
        if kpf__xyw != -1:
            parfor = ycmwn__ncp[kpf__xyw]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = ycmwn__ncp[:kpf__xyw] + parfor.init_block.body
        eval_nodes = ycmwn__ncp[kpf__xyw + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for mdv__chom in init_nodes:
            if is_assign(mdv__chom) and mdv__chom.target.name in redvars:
                ind = redvars.index(mdv__chom.target.name)
                reduce_vars[ind] = mdv__chom.target
        var_types = [pm.typemap[v] for v in redvars]
        yzc__vcfm = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        qotvi__efmrd = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        cco__szogj = gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types,
            pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(cco__szogj)
        self.all_update_funcs.append(qotvi__efmrd)
        self.all_combine_funcs.append(yzc__vcfm)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        self.all_vartypes = self.all_vartypes * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_vartypes
        self.all_reduce_vars = self.all_reduce_vars * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_reduce_vars
        utid__qqkzp = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        afhya__ryoq = gen_all_update_func(self.all_update_funcs, self.
            all_vartypes, self.in_col_types, self.redvar_offsets, self.
            typingctx, self.targetctx, self.pivot_typ, self.pivot_values,
            self.is_crosstab)
        msj__vub = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.
            targetctx, self.pivot_typ, self.pivot_values)
        ylhkx__lgwhz = gen_all_eval_func(self.all_eval_funcs, self.
            all_vartypes, self.redvar_offsets, self.out_col_types, self.
            typingctx, self.targetctx, self.pivot_values)
        return (self.all_vartypes, utid__qqkzp, afhya__ryoq, msj__vub,
            ylhkx__lgwhz)


class GeneralUDFGenerator(object):

    def __init__(self):
        self.funcs = []

    def add_udf(self, func):
        self.funcs.append(bodo.jit(distributed=False)(func))
        func.ncols_pre_shuffle = 1
        func.ncols_post_shuffle = 1
        func.n_redvars = 0

    def gen_all_func(self):
        if len(self.funcs) > 0:
            return self.funcs
        else:
            return None


def get_udf_func_struct(agg_func, input_has_index, in_col_types,
    out_col_types, typingctx, targetctx, pivot_typ, pivot_values, is_crosstab):
    if is_crosstab and len(in_col_types) == 0:
        in_col_types = [types.Array(types.intp, 1, 'C')]
    eevk__ldy = []
    for t, omkrm__xwvnq in zip(in_col_types, agg_func):
        eevk__ldy.append((t, omkrm__xwvnq))
    chgpv__etlc = RegularUDFGenerator(in_col_types, out_col_types,
        pivot_typ, pivot_values, is_crosstab, typingctx, targetctx)
    mlq__mom = GeneralUDFGenerator()
    for in_col_typ, func in eevk__ldy:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            chgpv__etlc.add_udf(in_col_typ, func)
        except:
            mlq__mom.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = chgpv__etlc.gen_all_func()
    general_udf_funcs = mlq__mom.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    ggc__qiiyy = compute_use_defs(parfor.loop_body)
    mqh__lexwe = set()
    for dluv__lezbr in ggc__qiiyy.usemap.values():
        mqh__lexwe |= dluv__lezbr
    rlm__suxxv = set()
    for dluv__lezbr in ggc__qiiyy.defmap.values():
        rlm__suxxv |= dluv__lezbr
    nzz__tvvcs = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    nzz__tvvcs.body = eval_nodes
    byqv__tmxkd = compute_use_defs({(0): nzz__tvvcs})
    egqit__anct = byqv__tmxkd.usemap[0]
    bqogj__pwuj = set()
    btmce__pao = []
    oxfa__yvq = []
    for mdv__chom in reversed(init_nodes):
        cbkz__lvj = {v.name for v in mdv__chom.list_vars()}
        if is_assign(mdv__chom):
            v = mdv__chom.target.name
            cbkz__lvj.remove(v)
            if (v in mqh__lexwe and v not in bqogj__pwuj and v not in
                egqit__anct and v not in rlm__suxxv):
                oxfa__yvq.append(mdv__chom)
                mqh__lexwe |= cbkz__lvj
                rlm__suxxv.add(v)
                continue
        bqogj__pwuj |= cbkz__lvj
        btmce__pao.append(mdv__chom)
    oxfa__yvq.reverse()
    btmce__pao.reverse()
    tjm__ums = min(parfor.loop_body.keys())
    avdp__iqbc = parfor.loop_body[tjm__ums]
    avdp__iqbc.body = oxfa__yvq + avdp__iqbc.body
    return btmce__pao


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    ikim__poq = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    dwh__intnx = set()
    hrsn__uofz = []
    for mdv__chom in init_nodes:
        if is_assign(mdv__chom) and isinstance(mdv__chom.value, ir.Global
            ) and isinstance(mdv__chom.value.value, pytypes.FunctionType
            ) and mdv__chom.value.value in ikim__poq:
            dwh__intnx.add(mdv__chom.target.name)
        elif is_call_assign(mdv__chom
            ) and mdv__chom.value.func.name in dwh__intnx:
            pass
        else:
            hrsn__uofz.append(mdv__chom)
    init_nodes = hrsn__uofz
    fhgm__ekusc = types.Tuple(var_types)
    iiss__yklb = lambda : None
    f_ir = compile_to_numba_ir(iiss__yklb, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    fuoq__hat = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    yeb__zbhg = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc), fuoq__hat, loc
        )
    block.body = block.body[-2:]
    block.body = init_nodes + [yeb__zbhg] + block.body
    block.body[-2].value.value = fuoq__hat
    soa__tzw = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        fhgm__ekusc, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    lfvli__wtbox = numba.core.target_extension.dispatcher_registry[cpu_target](
        iiss__yklb)
    lfvli__wtbox.add_overload(soa__tzw)
    return lfvli__wtbox


def gen_all_update_func(update_funcs, reduce_var_types, in_col_types,
    redvar_offsets, typingctx, targetctx, pivot_typ, pivot_values, is_crosstab
    ):
    nuxhn__uciv = len(update_funcs)
    fjci__dsfb = len(in_col_types)
    if pivot_values is not None:
        assert fjci__dsfb == 1
    rrmx__ptq = (
        'def update_all_f(redvar_arrs, data_in, w_ind, i, pivot_arr):\n')
    if pivot_values is not None:
        vapk__tnyo = redvar_offsets[fjci__dsfb]
        rrmx__ptq += '  pv = pivot_arr[i]\n'
        for cjkvi__enjp, jxyei__ixtjy in enumerate(pivot_values):
            ile__jeu = 'el' if cjkvi__enjp != 0 else ''
            rrmx__ptq += "  {}if pv == '{}':\n".format(ile__jeu, jxyei__ixtjy)
            kwn__wlbvr = vapk__tnyo * cjkvi__enjp
            rqu__pjrdg = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for
                i in range(kwn__wlbvr + redvar_offsets[0], kwn__wlbvr +
                redvar_offsets[1])])
            vtov__zofse = 'data_in[0][i]'
            if is_crosstab:
                vtov__zofse = '0'
            rrmx__ptq += '    {} = update_vars_0({}, {})\n'.format(rqu__pjrdg,
                rqu__pjrdg, vtov__zofse)
    else:
        for cjkvi__enjp in range(nuxhn__uciv):
            rqu__pjrdg = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for
                i in range(redvar_offsets[cjkvi__enjp], redvar_offsets[
                cjkvi__enjp + 1])])
            if rqu__pjrdg:
                rrmx__ptq += ('  {} = update_vars_{}({},  data_in[{}][i])\n'
                    .format(rqu__pjrdg, cjkvi__enjp, rqu__pjrdg, 0 if 
                    fjci__dsfb == 1 else cjkvi__enjp))
    rrmx__ptq += '  return\n'
    bndx__aregc = {}
    for i, omkrm__xwvnq in enumerate(update_funcs):
        bndx__aregc['update_vars_{}'.format(i)] = omkrm__xwvnq
    yfz__fzxg = {}
    exec(rrmx__ptq, bndx__aregc, yfz__fzxg)
    abg__xkjic = yfz__fzxg['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(abg__xkjic)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx, pivot_typ, pivot_values):
    ybbr__hcuez = types.Tuple([types.Array(t, 1, 'C') for t in
        reduce_var_types])
    arg_typs = ybbr__hcuez, ybbr__hcuez, types.intp, types.intp, pivot_typ
    eyfmx__nki = len(redvar_offsets) - 1
    vapk__tnyo = redvar_offsets[eyfmx__nki]
    rrmx__ptq = (
        'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i, pivot_arr):\n')
    if pivot_values is not None:
        assert eyfmx__nki == 1
        for oqazh__naz in range(len(pivot_values)):
            kwn__wlbvr = vapk__tnyo * oqazh__naz
            rqu__pjrdg = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for
                i in range(kwn__wlbvr + redvar_offsets[0], kwn__wlbvr +
                redvar_offsets[1])])
            abwbe__fnyuy = ', '.join(['recv_arrs[{}][i]'.format(i) for i in
                range(kwn__wlbvr + redvar_offsets[0], kwn__wlbvr +
                redvar_offsets[1])])
            rrmx__ptq += '  {} = combine_vars_0({}, {})\n'.format(rqu__pjrdg,
                rqu__pjrdg, abwbe__fnyuy)
    else:
        for cjkvi__enjp in range(eyfmx__nki):
            rqu__pjrdg = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for
                i in range(redvar_offsets[cjkvi__enjp], redvar_offsets[
                cjkvi__enjp + 1])])
            abwbe__fnyuy = ', '.join(['recv_arrs[{}][i]'.format(i) for i in
                range(redvar_offsets[cjkvi__enjp], redvar_offsets[
                cjkvi__enjp + 1])])
            if abwbe__fnyuy:
                rrmx__ptq += '  {} = combine_vars_{}({}, {})\n'.format(
                    rqu__pjrdg, cjkvi__enjp, rqu__pjrdg, abwbe__fnyuy)
    rrmx__ptq += '  return\n'
    bndx__aregc = {}
    for i, omkrm__xwvnq in enumerate(combine_funcs):
        bndx__aregc['combine_vars_{}'.format(i)] = omkrm__xwvnq
    yfz__fzxg = {}
    exec(rrmx__ptq, bndx__aregc, yfz__fzxg)
    ryo__dzxd = yfz__fzxg['combine_all_f']
    f_ir = compile_to_numba_ir(ryo__dzxd, bndx__aregc)
    msj__vub = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    lfvli__wtbox = numba.core.target_extension.dispatcher_registry[cpu_target](
        ryo__dzxd)
    lfvli__wtbox.add_overload(msj__vub)
    return lfvli__wtbox


def gen_all_eval_func(eval_funcs, reduce_var_types, redvar_offsets,
    out_col_typs, typingctx, targetctx, pivot_values):
    ybbr__hcuez = types.Tuple([types.Array(t, 1, 'C') for t in
        reduce_var_types])
    out_col_typs = types.Tuple(out_col_typs)
    eyfmx__nki = len(redvar_offsets) - 1
    vapk__tnyo = redvar_offsets[eyfmx__nki]
    rrmx__ptq = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    if pivot_values is not None:
        assert eyfmx__nki == 1
        for cjkvi__enjp in range(len(pivot_values)):
            kwn__wlbvr = vapk__tnyo * cjkvi__enjp
            rqu__pjrdg = ', '.join(['redvar_arrs[{}][j]'.format(i) for i in
                range(kwn__wlbvr + redvar_offsets[0], kwn__wlbvr +
                redvar_offsets[1])])
            rrmx__ptq += '  out_arrs[{}][j] = eval_vars_0({})\n'.format(
                cjkvi__enjp, rqu__pjrdg)
    else:
        for cjkvi__enjp in range(eyfmx__nki):
            rqu__pjrdg = ', '.join(['redvar_arrs[{}][j]'.format(i) for i in
                range(redvar_offsets[cjkvi__enjp], redvar_offsets[
                cjkvi__enjp + 1])])
            rrmx__ptq += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(
                cjkvi__enjp, cjkvi__enjp, rqu__pjrdg)
    rrmx__ptq += '  return\n'
    bndx__aregc = {}
    for i, omkrm__xwvnq in enumerate(eval_funcs):
        bndx__aregc['eval_vars_{}'.format(i)] = omkrm__xwvnq
    yfz__fzxg = {}
    exec(rrmx__ptq, bndx__aregc, yfz__fzxg)
    qhss__ydip = yfz__fzxg['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(qhss__ydip)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    qzsj__xcy = len(var_types)
    iguic__bbq = [f'in{i}' for i in range(qzsj__xcy)]
    fhgm__ekusc = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    bviau__fjple = fhgm__ekusc(0)
    rrmx__ptq = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        iguic__bbq))
    yfz__fzxg = {}
    exec(rrmx__ptq, {'_zero': bviau__fjple}, yfz__fzxg)
    qahej__iuae = yfz__fzxg['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(qahej__iuae, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': bviau__fjple}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    ycxky__tdxlb = []
    for i, v in enumerate(reduce_vars):
        ycxky__tdxlb.append(ir.Assign(block.body[i].target, v, v.loc))
        for cna__rznz in v.versioned_names:
            ycxky__tdxlb.append(ir.Assign(v, ir.Var(v.scope, cna__rznz, v.
                loc), v.loc))
    block.body = block.body[:qzsj__xcy] + ycxky__tdxlb + eval_nodes
    cco__szogj = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        fhgm__ekusc, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    lfvli__wtbox = numba.core.target_extension.dispatcher_registry[cpu_target](
        qahej__iuae)
    lfvli__wtbox.add_overload(cco__szogj)
    return lfvli__wtbox


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    qzsj__xcy = len(redvars)
    ohm__weli = [f'v{i}' for i in range(qzsj__xcy)]
    iguic__bbq = [f'in{i}' for i in range(qzsj__xcy)]
    rrmx__ptq = 'def agg_combine({}):\n'.format(', '.join(ohm__weli +
        iguic__bbq))
    hmlcl__abcuq = wrap_parfor_blocks(parfor)
    ryk__lcii = find_topo_order(hmlcl__abcuq)
    ryk__lcii = ryk__lcii[1:]
    unwrap_parfor_blocks(parfor)
    hbvc__gbsh = {}
    htrg__bkj = []
    for bich__sbds in ryk__lcii:
        ysit__kqr = parfor.loop_body[bich__sbds]
        for mdv__chom in ysit__kqr.body:
            if is_call_assign(mdv__chom) and guard(find_callname, f_ir,
                mdv__chom.value) == ('__special_combine', 'bodo.ir.aggregate'):
                args = mdv__chom.value.args
                pkcln__hwk = []
                gwl__qwe = []
                for v in args[:-1]:
                    ind = redvars.index(v.name)
                    htrg__bkj.append(ind)
                    pkcln__hwk.append('v{}'.format(ind))
                    gwl__qwe.append('in{}'.format(ind))
                bgv__qwdlb = '__special_combine__{}'.format(len(hbvc__gbsh))
                rrmx__ptq += '    ({},) = {}({})\n'.format(', '.join(
                    pkcln__hwk), bgv__qwdlb, ', '.join(pkcln__hwk + gwl__qwe))
                bmi__fqnn = ir.Expr.call(args[-1], [], (), ysit__kqr.loc)
                xjxz__sxw = guard(find_callname, f_ir, bmi__fqnn)
                assert xjxz__sxw == ('_var_combine', 'bodo.ir.aggregate')
                xjxz__sxw = bodo.ir.aggregate._var_combine
                hbvc__gbsh[bgv__qwdlb] = xjxz__sxw
            if is_assign(mdv__chom) and mdv__chom.target.name in redvars:
                zkp__jhszq = mdv__chom.target.name
                ind = redvars.index(zkp__jhszq)
                if ind in htrg__bkj:
                    continue
                if len(f_ir._definitions[zkp__jhszq]) == 2:
                    var_def = f_ir._definitions[zkp__jhszq][0]
                    rrmx__ptq += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[zkp__jhszq][1]
                    rrmx__ptq += _match_reduce_def(var_def, f_ir, ind)
    rrmx__ptq += '    return {}'.format(', '.join(['v{}'.format(i) for i in
        range(qzsj__xcy)]))
    yfz__fzxg = {}
    exec(rrmx__ptq, {}, yfz__fzxg)
    qdv__qygp = yfz__fzxg['agg_combine']
    arg_typs = tuple(2 * var_types)
    bndx__aregc = {'numba': numba, 'bodo': bodo, 'np': np}
    bndx__aregc.update(hbvc__gbsh)
    f_ir = compile_to_numba_ir(qdv__qygp, bndx__aregc, typingctx=typingctx,
        targetctx=targetctx, arg_typs=arg_typs, typemap=pm.typemap,
        calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    fhgm__ekusc = pm.typemap[block.body[-1].value.name]
    yzc__vcfm = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        fhgm__ekusc, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    lfvli__wtbox = numba.core.target_extension.dispatcher_registry[cpu_target](
        qdv__qygp)
    lfvli__wtbox.add_overload(yzc__vcfm)
    return lfvli__wtbox


def _match_reduce_def(var_def, f_ir, ind):
    rrmx__ptq = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        rrmx__ptq = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        jtpw__ihl = guard(find_callname, f_ir, var_def)
        if jtpw__ihl == ('min', 'builtins'):
            rrmx__ptq = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if jtpw__ihl == ('max', 'builtins'):
            rrmx__ptq = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return rrmx__ptq


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    qzsj__xcy = len(redvars)
    yjhr__irvny = 1
    dmvcn__jrttv = []
    for i in range(yjhr__irvny):
        cfxt__hxqsj = ir.Var(arr_var.scope, f'$input{i}', arr_var.loc)
        dmvcn__jrttv.append(cfxt__hxqsj)
    egqio__dqj = parfor.loop_nests[0].index_variable
    uzqk__fojzg = [0] * qzsj__xcy
    for ysit__kqr in parfor.loop_body.values():
        wnl__wuj = []
        for mdv__chom in ysit__kqr.body:
            if is_var_assign(mdv__chom
                ) and mdv__chom.value.name == egqio__dqj.name:
                continue
            if is_getitem(mdv__chom
                ) and mdv__chom.value.value.name == arr_var.name:
                mdv__chom.value = dmvcn__jrttv[0]
            if is_call_assign(mdv__chom) and guard(find_callname, pm.
                func_ir, mdv__chom.value) == ('isna', 'bodo.libs.array_kernels'
                ) and mdv__chom.value.args[0].name == arr_var.name:
                mdv__chom.value = ir.Const(False, mdv__chom.target.loc)
            if is_assign(mdv__chom) and mdv__chom.target.name in redvars:
                ind = redvars.index(mdv__chom.target.name)
                uzqk__fojzg[ind] = mdv__chom.target
            wnl__wuj.append(mdv__chom)
        ysit__kqr.body = wnl__wuj
    ohm__weli = ['v{}'.format(i) for i in range(qzsj__xcy)]
    iguic__bbq = ['in{}'.format(i) for i in range(yjhr__irvny)]
    rrmx__ptq = 'def agg_update({}):\n'.format(', '.join(ohm__weli +
        iguic__bbq))
    rrmx__ptq += '    __update_redvars()\n'
    rrmx__ptq += '    return {}'.format(', '.join(['v{}'.format(i) for i in
        range(qzsj__xcy)]))
    yfz__fzxg = {}
    exec(rrmx__ptq, {}, yfz__fzxg)
    ahjhy__zvyh = yfz__fzxg['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * yjhr__irvny)
    f_ir = compile_to_numba_ir(ahjhy__zvyh, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    frpt__rlbh = f_ir.blocks.popitem()[1].body
    fhgm__ekusc = pm.typemap[frpt__rlbh[-1].value.name]
    hmlcl__abcuq = wrap_parfor_blocks(parfor)
    ryk__lcii = find_topo_order(hmlcl__abcuq)
    ryk__lcii = ryk__lcii[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    avdp__iqbc = f_ir.blocks[ryk__lcii[0]]
    izng__tud = f_ir.blocks[ryk__lcii[-1]]
    pykz__ctur = frpt__rlbh[:qzsj__xcy + yjhr__irvny]
    if qzsj__xcy > 1:
        bjnu__fcpv = frpt__rlbh[-3:]
        assert is_assign(bjnu__fcpv[0]) and isinstance(bjnu__fcpv[0].value,
            ir.Expr) and bjnu__fcpv[0].value.op == 'build_tuple'
    else:
        bjnu__fcpv = frpt__rlbh[-2:]
    for i in range(qzsj__xcy):
        oqnnr__bbl = frpt__rlbh[i].target
        wqvg__qvj = ir.Assign(oqnnr__bbl, uzqk__fojzg[i], oqnnr__bbl.loc)
        pykz__ctur.append(wqvg__qvj)
    for i in range(qzsj__xcy, qzsj__xcy + yjhr__irvny):
        oqnnr__bbl = frpt__rlbh[i].target
        wqvg__qvj = ir.Assign(oqnnr__bbl, dmvcn__jrttv[i - qzsj__xcy],
            oqnnr__bbl.loc)
        pykz__ctur.append(wqvg__qvj)
    avdp__iqbc.body = pykz__ctur + avdp__iqbc.body
    qywgd__pgz = []
    for i in range(qzsj__xcy):
        oqnnr__bbl = frpt__rlbh[i].target
        wqvg__qvj = ir.Assign(uzqk__fojzg[i], oqnnr__bbl, oqnnr__bbl.loc)
        qywgd__pgz.append(wqvg__qvj)
    izng__tud.body += qywgd__pgz + bjnu__fcpv
    dumt__athe = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        fhgm__ekusc, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    lfvli__wtbox = numba.core.target_extension.dispatcher_registry[cpu_target](
        ahjhy__zvyh)
    lfvli__wtbox.add_overload(dumt__athe)
    return lfvli__wtbox


def _rm_arg_agg_block(block, typemap):
    ycmwn__ncp = []
    arr_var = None
    for i, mdv__chom in enumerate(block.body):
        if is_assign(mdv__chom) and isinstance(mdv__chom.value, ir.Arg):
            arr_var = mdv__chom.target
            nke__eqq = typemap[arr_var.name]
            if not isinstance(nke__eqq, types.ArrayCompatible):
                ycmwn__ncp += block.body[i + 1:]
                break
            phfhj__gly = block.body[i + 1]
            assert is_assign(phfhj__gly) and isinstance(phfhj__gly.value,
                ir.Expr
                ) and phfhj__gly.value.op == 'getattr' and phfhj__gly.value.attr == 'shape' and phfhj__gly.value.value.name == arr_var.name
            yua__keub = phfhj__gly.target
            mrzj__cyim = block.body[i + 2]
            assert is_assign(mrzj__cyim) and isinstance(mrzj__cyim.value,
                ir.Expr
                ) and mrzj__cyim.value.op == 'static_getitem' and mrzj__cyim.value.value.name == yua__keub.name
            ycmwn__ncp += block.body[i + 3:]
            break
        ycmwn__ncp.append(mdv__chom)
    return ycmwn__ncp, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    hmlcl__abcuq = wrap_parfor_blocks(parfor)
    ryk__lcii = find_topo_order(hmlcl__abcuq)
    ryk__lcii = ryk__lcii[1:]
    unwrap_parfor_blocks(parfor)
    for bich__sbds in reversed(ryk__lcii):
        for mdv__chom in reversed(parfor.loop_body[bich__sbds].body):
            if isinstance(mdv__chom, ir.Assign) and (mdv__chom.target.name in
                parfor_params or mdv__chom.target.name in var_to_param):
                iilkc__vdxn = mdv__chom.target.name
                rhs = mdv__chom.value
                ntg__naw = (iilkc__vdxn if iilkc__vdxn in parfor_params else
                    var_to_param[iilkc__vdxn])
                ljs__tszac = []
                if isinstance(rhs, ir.Var):
                    ljs__tszac = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    ljs__tszac = [v.name for v in mdv__chom.value.list_vars()]
                param_uses[ntg__naw].extend(ljs__tszac)
                for v in ljs__tszac:
                    var_to_param[v] = ntg__naw
            if isinstance(mdv__chom, Parfor):
                get_parfor_reductions(mdv__chom, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for jpjbp__doa, ljs__tszac in param_uses.items():
        if jpjbp__doa in ljs__tszac and jpjbp__doa not in reduce_varnames:
            reduce_varnames.append(jpjbp__doa)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
