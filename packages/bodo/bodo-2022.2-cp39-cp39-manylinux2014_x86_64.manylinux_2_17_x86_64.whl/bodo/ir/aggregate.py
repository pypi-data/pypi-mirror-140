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
            ponow__avwxx = lir.FunctionType(lir.VoidType(), [lir.IntType(8)
                .as_pointer()])
            txsn__med = cgutils.get_or_insert_function(builder.module,
                ponow__avwxx, sym._literal_value)
            builder.call(txsn__med, [context.get_constant_null(sig.args[0])])
        elif sig == types.none(types.int64, types.voidptr, types.voidptr):
            ponow__avwxx = lir.FunctionType(lir.VoidType(), [lir.IntType(64
                ), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            txsn__med = cgutils.get_or_insert_function(builder.module,
                ponow__avwxx, sym._literal_value)
            builder.call(txsn__med, [context.get_constant(types.int64, 0),
                context.get_constant_null(sig.args[1]), context.
                get_constant_null(sig.args[2])])
        else:
            ponow__avwxx = lir.FunctionType(lir.VoidType(), [lir.IntType(8)
                .as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)
                .as_pointer()])
            txsn__med = cgutils.get_or_insert_function(builder.module,
                ponow__avwxx, sym._literal_value)
            builder.call(txsn__med, [context.get_constant_null(sig.args[0]),
                context.get_constant_null(sig.args[1]), context.
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
        uscsd__begp = True
        fde__zvvz = 1
        skfm__obh = -1
        if isinstance(rhs, ir.Expr):
            for hcat__adzny in rhs.kws:
                if func_name in list_cumulative:
                    if hcat__adzny[0] == 'skipna':
                        uscsd__begp = guard(find_const, func_ir, hcat__adzny[1]
                            )
                        if not isinstance(uscsd__begp, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if hcat__adzny[0] == 'dropna':
                        uscsd__begp = guard(find_const, func_ir, hcat__adzny[1]
                            )
                        if not isinstance(uscsd__begp, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            fde__zvvz = get_call_expr_arg('shift', rhs.args, dict(rhs.kws),
                0, 'periods', fde__zvvz)
            fde__zvvz = guard(find_const, func_ir, fde__zvvz)
        if func_name == 'head':
            skfm__obh = get_call_expr_arg('head', rhs.args, dict(rhs.kws), 
                0, 'n', 5)
            if not isinstance(skfm__obh, int):
                skfm__obh = guard(find_const, func_ir, skfm__obh)
            if skfm__obh < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = uscsd__begp
        func.periods = fde__zvvz
        func.head_n = skfm__obh
        if func_name == 'transform':
            kws = dict(rhs.kws)
            gvucr__rap = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            nohrc__fscn = typemap[gvucr__rap.name]
            nhe__uql = None
            if isinstance(nohrc__fscn, str):
                nhe__uql = nohrc__fscn
            elif is_overload_constant_str(nohrc__fscn):
                nhe__uql = get_overload_const_str(nohrc__fscn)
            elif bodo.utils.typing.is_builtin_function(nohrc__fscn):
                nhe__uql = bodo.utils.typing.get_builtin_function_name(
                    nohrc__fscn)
            if nhe__uql not in bodo.ir.aggregate.supported_transform_funcs[:]:
                raise BodoError(f'unsupported transform function {nhe__uql}')
            func.transform_func = supported_agg_funcs.index(nhe__uql)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    gvucr__rap = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if gvucr__rap == '':
        nohrc__fscn = types.none
    else:
        nohrc__fscn = typemap[gvucr__rap.name]
    if is_overload_constant_dict(nohrc__fscn):
        nvye__fnhtw = get_overload_constant_dict(nohrc__fscn)
        lizt__ymd = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in nvye__fnhtw.values()]
        return lizt__ymd
    if nohrc__fscn == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(nohrc__fscn, types.BaseTuple):
        lizt__ymd = []
        dnadj__loy = 0
        for t in nohrc__fscn.types:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                lizt__ymd.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>':
                    func.fname = '<lambda_' + str(dnadj__loy) + '>'
                    dnadj__loy += 1
                lizt__ymd.append(func)
        return [lizt__ymd]
    if is_overload_constant_str(nohrc__fscn):
        func_name = get_overload_const_str(nohrc__fscn)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(nohrc__fscn):
        func_name = bodo.utils.typing.get_builtin_function_name(nohrc__fscn)
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
        dnadj__loy = 0
        llc__zqmlg = []
        for tmr__uxu in f_val:
            func = get_agg_func_udf(func_ir, tmr__uxu, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{dnadj__loy}>'
                dnadj__loy += 1
            llc__zqmlg.append(func)
        return llc__zqmlg
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
    nhe__uql = code.co_name
    return nhe__uql


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
            etp__bwlv = types.DType(args[0])
            return signature(etp__bwlv, *args)


@numba.njit(no_cpython_wrapper=True)
def _var_combine(ssqdm_a, mean_a, nobs_a, ssqdm_b, mean_b, nobs_b):
    etp__vqc = nobs_a + nobs_b
    wfzsg__pdrh = (nobs_a * mean_a + nobs_b * mean_b) / etp__vqc
    mqs__hexqd = mean_b - mean_a
    cov__diouf = (ssqdm_a + ssqdm_b + mqs__hexqd * mqs__hexqd * nobs_a *
        nobs_b / etp__vqc)
    return cov__diouf, wfzsg__pdrh, etp__vqc


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
        yps__wmaag = ''
        for vjkf__znx, v in self.df_out_vars.items():
            yps__wmaag += "'{}':{}, ".format(vjkf__znx, v.name)
        atev__dtxro = '{}{{{}}}'.format(self.df_out, yps__wmaag)
        opwg__mci = ''
        for vjkf__znx, v in self.df_in_vars.items():
            opwg__mci += "'{}':{}, ".format(vjkf__znx, v.name)
        cofsg__lutt = '{}{{{}}}'.format(self.df_in, opwg__mci)
        ztlb__difcl = 'pivot {}:{}'.format(self.pivot_arr.name, self.
            pivot_values) if self.pivot_arr is not None else ''
        key_names = ','.join(self.key_names)
        qog__qjtaz = ','.join([v.name for v in self.key_arrs])
        return 'aggregate: {} = {} [key: {}:{}] {}'.format(atev__dtxro,
            cofsg__lutt, key_names, qog__qjtaz, ztlb__difcl)

    def remove_out_col(self, out_col_name):
        self.df_out_vars.pop(out_col_name)
        caax__kktoz, gbaev__lvoo = self.gb_info_out.pop(out_col_name)
        if caax__kktoz is None and not self.is_crosstab:
            return
        wmms__dbn = self.gb_info_in[caax__kktoz]
        if self.pivot_arr is not None:
            self.pivot_values.remove(out_col_name)
            for i, (func, yps__wmaag) in enumerate(wmms__dbn):
                try:
                    yps__wmaag.remove(out_col_name)
                    if len(yps__wmaag) == 0:
                        wmms__dbn.pop(i)
                        break
                except ValueError as otqgn__ppohs:
                    continue
        else:
            for i, (func, uylzl__nunj) in enumerate(wmms__dbn):
                if uylzl__nunj == out_col_name:
                    wmms__dbn.pop(i)
                    break
        if len(wmms__dbn) == 0:
            self.gb_info_in.pop(caax__kktoz)
            self.df_in_vars.pop(caax__kktoz)


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
    rbq__tlen = [ntpfe__kea for ntpfe__kea, rlbs__dayor in aggregate_node.
        df_out_vars.items() if rlbs__dayor.name not in lives]
    for wyay__uaih in rbq__tlen:
        aggregate_node.remove_out_col(wyay__uaih)
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
    mfv__bri = set(v.name for v in aggregate_node.df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        mfv__bri.update({v.name for v in aggregate_node.out_key_vars})
    return set(), mfv__bri


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for i in range(len(aggregate_node.key_arrs)):
        aggregate_node.key_arrs[i] = replace_vars_inner(aggregate_node.
            key_arrs[i], var_dict)
    for ntpfe__kea in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[ntpfe__kea] = replace_vars_inner(
            aggregate_node.df_in_vars[ntpfe__kea], var_dict)
    for ntpfe__kea in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[ntpfe__kea] = replace_vars_inner(
            aggregate_node.df_out_vars[ntpfe__kea], var_dict)
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
    for ntpfe__kea in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[ntpfe__kea] = visit_vars_inner(aggregate_node
            .df_in_vars[ntpfe__kea], callback, cbdata)
    for ntpfe__kea in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[ntpfe__kea] = visit_vars_inner(
            aggregate_node.df_out_vars[ntpfe__kea], callback, cbdata)
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
    gzrc__zrt = []
    for rxb__kfyd in aggregate_node.key_arrs:
        snqdj__tfleg = equiv_set.get_shape(rxb__kfyd)
        if snqdj__tfleg:
            gzrc__zrt.append(snqdj__tfleg[0])
    if aggregate_node.pivot_arr is not None:
        snqdj__tfleg = equiv_set.get_shape(aggregate_node.pivot_arr)
        if snqdj__tfleg:
            gzrc__zrt.append(snqdj__tfleg[0])
    for rlbs__dayor in aggregate_node.df_in_vars.values():
        snqdj__tfleg = equiv_set.get_shape(rlbs__dayor)
        if snqdj__tfleg:
            gzrc__zrt.append(snqdj__tfleg[0])
    if len(gzrc__zrt) > 1:
        equiv_set.insert_equiv(*gzrc__zrt)
    zfpw__vzaa = []
    gzrc__zrt = []
    xnk__iujgk = list(aggregate_node.df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        xnk__iujgk.extend(aggregate_node.out_key_vars)
    for rlbs__dayor in xnk__iujgk:
        ydxz__wdgbp = typemap[rlbs__dayor.name]
        bmmr__xkjn = array_analysis._gen_shape_call(equiv_set, rlbs__dayor,
            ydxz__wdgbp.ndim, None, zfpw__vzaa)
        equiv_set.insert_equiv(rlbs__dayor, bmmr__xkjn)
        gzrc__zrt.append(bmmr__xkjn[0])
        equiv_set.define(rlbs__dayor, set())
    if len(gzrc__zrt) > 1:
        equiv_set.insert_equiv(*gzrc__zrt)
    return [], zfpw__vzaa


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    olr__vtq = Distribution.OneD
    for rlbs__dayor in aggregate_node.df_in_vars.values():
        olr__vtq = Distribution(min(olr__vtq.value, array_dists[rlbs__dayor
            .name].value))
    for rxb__kfyd in aggregate_node.key_arrs:
        olr__vtq = Distribution(min(olr__vtq.value, array_dists[rxb__kfyd.
            name].value))
    if aggregate_node.pivot_arr is not None:
        olr__vtq = Distribution(min(olr__vtq.value, array_dists[
            aggregate_node.pivot_arr.name].value))
        array_dists[aggregate_node.pivot_arr.name] = olr__vtq
    for rlbs__dayor in aggregate_node.df_in_vars.values():
        array_dists[rlbs__dayor.name] = olr__vtq
    for rxb__kfyd in aggregate_node.key_arrs:
        array_dists[rxb__kfyd.name] = olr__vtq
    wxx__gew = Distribution.OneD_Var
    for rlbs__dayor in aggregate_node.df_out_vars.values():
        if rlbs__dayor.name in array_dists:
            wxx__gew = Distribution(min(wxx__gew.value, array_dists[
                rlbs__dayor.name].value))
    if aggregate_node.out_key_vars is not None:
        for rlbs__dayor in aggregate_node.out_key_vars:
            if rlbs__dayor.name in array_dists:
                wxx__gew = Distribution(min(wxx__gew.value, array_dists[
                    rlbs__dayor.name].value))
    wxx__gew = Distribution(min(wxx__gew.value, olr__vtq.value))
    for rlbs__dayor in aggregate_node.df_out_vars.values():
        array_dists[rlbs__dayor.name] = wxx__gew
    if aggregate_node.out_key_vars is not None:
        for urel__hlo in aggregate_node.out_key_vars:
            array_dists[urel__hlo.name] = wxx__gew
    if wxx__gew != Distribution.OneD_Var:
        for rxb__kfyd in aggregate_node.key_arrs:
            array_dists[rxb__kfyd.name] = wxx__gew
        if aggregate_node.pivot_arr is not None:
            array_dists[aggregate_node.pivot_arr.name] = wxx__gew
        for rlbs__dayor in aggregate_node.df_in_vars.values():
            array_dists[rlbs__dayor.name] = wxx__gew


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for rlbs__dayor in agg_node.df_out_vars.values():
        definitions[rlbs__dayor.name].append(agg_node)
    if agg_node.out_key_vars is not None:
        for urel__hlo in agg_node.out_key_vars:
            definitions[urel__hlo.name].append(agg_node)
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
    twh__wlxuu = tuple(typemap[v.name] for v in agg_node.key_arrs)
    ejfx__gvys = [v for pobyb__noxhe, v in agg_node.df_in_vars.items()]
    njrn__gfze = [v for pobyb__noxhe, v in agg_node.df_out_vars.items()]
    in_col_typs = []
    lizt__ymd = []
    if agg_node.pivot_arr is not None:
        for caax__kktoz, wmms__dbn in agg_node.gb_info_in.items():
            for func, gbaev__lvoo in wmms__dbn:
                if caax__kktoz is not None:
                    in_col_typs.append(typemap[agg_node.df_in_vars[
                        caax__kktoz].name])
                lizt__ymd.append(func)
    else:
        for caax__kktoz, func in agg_node.gb_info_out.values():
            if caax__kktoz is not None:
                in_col_typs.append(typemap[agg_node.df_in_vars[caax__kktoz]
                    .name])
            lizt__ymd.append(func)
    out_col_typs = tuple(typemap[v.name] for v in njrn__gfze)
    pivot_typ = types.none if agg_node.pivot_arr is None else typemap[agg_node
        .pivot_arr.name]
    arg_typs = tuple(twh__wlxuu + tuple(typemap[v.name] for v in ejfx__gvys
        ) + (pivot_typ,))
    lhto__sguf = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for i, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            lhto__sguf.update({f'in_cat_dtype_{i}': in_col_typ})
    for i, xwubn__ttupj in enumerate(out_col_typs):
        if isinstance(xwubn__ttupj, bodo.CategoricalArrayType):
            lhto__sguf.update({f'out_cat_dtype_{i}': xwubn__ttupj})
    udf_func_struct = get_udf_func_struct(lizt__ymd, agg_node.
        input_has_index, in_col_typs, out_col_typs, typingctx, targetctx,
        pivot_typ, agg_node.pivot_values, agg_node.is_crosstab)
    pxvkh__iyog = gen_top_level_agg_func(agg_node, in_col_typs,
        out_col_typs, parallel, udf_func_struct)
    lhto__sguf.update({'pd': pd, 'pre_alloc_string_array':
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
            lhto__sguf.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            lhto__sguf.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    hnmof__awq = compile_to_numba_ir(pxvkh__iyog, lhto__sguf, typingctx=
        typingctx, targetctx=targetctx, arg_typs=arg_typs, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    itj__jvabu = []
    if agg_node.pivot_arr is None:
        xay__qalia = agg_node.key_arrs[0].scope
        loc = agg_node.loc
        qrtk__ghp = ir.Var(xay__qalia, mk_unique_var('dummy_none'), loc)
        typemap[qrtk__ghp.name] = types.none
        itj__jvabu.append(ir.Assign(ir.Const(None, loc), qrtk__ghp, loc))
        ejfx__gvys.append(qrtk__ghp)
    else:
        ejfx__gvys.append(agg_node.pivot_arr)
    replace_arg_nodes(hnmof__awq, agg_node.key_arrs + ejfx__gvys)
    ons__pqnjr = hnmof__awq.body[-3]
    assert is_assign(ons__pqnjr) and isinstance(ons__pqnjr.value, ir.Expr
        ) and ons__pqnjr.value.op == 'build_tuple'
    itj__jvabu += hnmof__awq.body[:-3]
    xnk__iujgk = list(agg_node.df_out_vars.values())
    if agg_node.out_key_vars is not None:
        xnk__iujgk += agg_node.out_key_vars
    for i, onbz__skmr in enumerate(xnk__iujgk):
        lyybk__pxc = ons__pqnjr.value.items[i]
        itj__jvabu.append(ir.Assign(lyybk__pxc, onbz__skmr, onbz__skmr.loc))
    return itj__jvabu


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
        lxzc__myzir = args[0]
        if lxzc__myzir == types.none:
            return signature(types.boolean, *args)


@lower_builtin(bool, types.none)
def lower_column_mean_impl(context, builder, sig, args):
    oako__jgxxv = context.compile_internal(builder, lambda a: False, sig, args)
    return oako__jgxxv


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
        djnr__pwoxi = IntDtype(t.dtype).name
        assert djnr__pwoxi.endswith('Dtype()')
        djnr__pwoxi = djnr__pwoxi[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{djnr__pwoxi}'))"
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
        vug__zptf = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {vug__zptf}_cat_dtype_{colnum})')
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
    lkllf__emf = udf_func_struct.var_typs
    xym__jfot = len(lkllf__emf)
    iquwu__dmgqw = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    iquwu__dmgqw += '    if is_null_pointer(in_table):\n'
    iquwu__dmgqw += '        return\n'
    iquwu__dmgqw += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in lkllf__emf]), 
        ',' if len(lkllf__emf) == 1 else '')
    ccvua__ndpx = n_keys
    qbqi__vwe = []
    redvar_offsets = []
    ekys__yjcf = []
    if do_combine:
        for i, tmr__uxu in enumerate(allfuncs):
            if tmr__uxu.ftype != 'udf':
                ccvua__ndpx += tmr__uxu.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(ccvua__ndpx, ccvua__ndpx +
                    tmr__uxu.n_redvars))
                ccvua__ndpx += tmr__uxu.n_redvars
                ekys__yjcf.append(data_in_typs_[func_idx_to_in_col[i]])
                qbqi__vwe.append(func_idx_to_in_col[i] + n_keys)
    else:
        for i, tmr__uxu in enumerate(allfuncs):
            if tmr__uxu.ftype != 'udf':
                ccvua__ndpx += tmr__uxu.ncols_post_shuffle
            else:
                redvar_offsets += list(range(ccvua__ndpx + 1, ccvua__ndpx +
                    1 + tmr__uxu.n_redvars))
                ccvua__ndpx += tmr__uxu.n_redvars + 1
                ekys__yjcf.append(data_in_typs_[func_idx_to_in_col[i]])
                qbqi__vwe.append(func_idx_to_in_col[i] + n_keys)
    assert len(redvar_offsets) == xym__jfot
    gwt__akll = len(ekys__yjcf)
    koq__nsfw = []
    for i, t in enumerate(ekys__yjcf):
        koq__nsfw.append(_gen_dummy_alloc(t, i, True))
    iquwu__dmgqw += '    data_in_dummy = ({}{})\n'.format(','.join(
        koq__nsfw), ',' if len(ekys__yjcf) == 1 else '')
    iquwu__dmgqw += """
    # initialize redvar cols
"""
    iquwu__dmgqw += '    init_vals = __init_func()\n'
    for i in range(xym__jfot):
        iquwu__dmgqw += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(i, redvar_offsets[i], i))
        iquwu__dmgqw += '    incref(redvar_arr_{})\n'.format(i)
        iquwu__dmgqw += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(i, i)
    iquwu__dmgqw += '    redvars = ({}{})\n'.format(','.join([
        'redvar_arr_{}'.format(i) for i in range(xym__jfot)]), ',' if 
        xym__jfot == 1 else '')
    iquwu__dmgqw += '\n'
    for i in range(gwt__akll):
        iquwu__dmgqw += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(i, qbqi__vwe[i], i))
        iquwu__dmgqw += '    incref(data_in_{})\n'.format(i)
    iquwu__dmgqw += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(i) for i in range(gwt__akll)]), ',' if gwt__akll == 1 else '')
    iquwu__dmgqw += '\n'
    iquwu__dmgqw += '    for i in range(len(data_in_0)):\n'
    iquwu__dmgqw += '        w_ind = row_to_group[i]\n'
    iquwu__dmgqw += '        if w_ind != -1:\n'
    iquwu__dmgqw += (
        '            __update_redvars(redvars, data_in, w_ind, i, pivot_arr=None)\n'
        )
    uvglg__ydnp = {}
    exec(iquwu__dmgqw, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, uvglg__ydnp)
    return uvglg__ydnp['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, out_data_typs,
    label_suffix):
    lkllf__emf = udf_func_struct.var_typs
    xym__jfot = len(lkllf__emf)
    iquwu__dmgqw = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    iquwu__dmgqw += '    if is_null_pointer(in_table):\n'
    iquwu__dmgqw += '        return\n'
    iquwu__dmgqw += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in lkllf__emf]), 
        ',' if len(lkllf__emf) == 1 else '')
    pgzbe__phn = n_keys
    kuknp__afu = n_keys
    oun__jaifs = []
    wuy__laord = []
    for tmr__uxu in allfuncs:
        if tmr__uxu.ftype != 'udf':
            pgzbe__phn += tmr__uxu.ncols_pre_shuffle
            kuknp__afu += tmr__uxu.ncols_post_shuffle
        else:
            oun__jaifs += list(range(pgzbe__phn, pgzbe__phn + tmr__uxu.
                n_redvars))
            wuy__laord += list(range(kuknp__afu + 1, kuknp__afu + 1 +
                tmr__uxu.n_redvars))
            pgzbe__phn += tmr__uxu.n_redvars
            kuknp__afu += 1 + tmr__uxu.n_redvars
    assert len(oun__jaifs) == xym__jfot
    iquwu__dmgqw += """
    # initialize redvar cols
"""
    iquwu__dmgqw += '    init_vals = __init_func()\n'
    for i in range(xym__jfot):
        iquwu__dmgqw += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(i, wuy__laord[i], i))
        iquwu__dmgqw += '    incref(redvar_arr_{})\n'.format(i)
        iquwu__dmgqw += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(i, i)
    iquwu__dmgqw += '    redvars = ({}{})\n'.format(','.join([
        'redvar_arr_{}'.format(i) for i in range(xym__jfot)]), ',' if 
        xym__jfot == 1 else '')
    iquwu__dmgqw += '\n'
    for i in range(xym__jfot):
        iquwu__dmgqw += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(i, oun__jaifs[i], i))
        iquwu__dmgqw += '    incref(recv_redvar_arr_{})\n'.format(i)
    iquwu__dmgqw += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(i) for i in range(xym__jfot)]), ',' if 
        xym__jfot == 1 else '')
    iquwu__dmgqw += '\n'
    if xym__jfot:
        iquwu__dmgqw += '    for i in range(len(recv_redvar_arr_0)):\n'
        iquwu__dmgqw += '        w_ind = row_to_group[i]\n'
        iquwu__dmgqw += """        __combine_redvars(redvars, recv_redvars, w_ind, i, pivot_arr=None)
"""
    uvglg__ydnp = {}
    exec(iquwu__dmgqw, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, uvglg__ydnp)
    return uvglg__ydnp['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    lkllf__emf = udf_func_struct.var_typs
    xym__jfot = len(lkllf__emf)
    ccvua__ndpx = n_keys
    redvar_offsets = []
    asc__ciq = []
    out_data_typs = []
    for i, tmr__uxu in enumerate(allfuncs):
        if tmr__uxu.ftype != 'udf':
            ccvua__ndpx += tmr__uxu.ncols_post_shuffle
        else:
            asc__ciq.append(ccvua__ndpx)
            redvar_offsets += list(range(ccvua__ndpx + 1, ccvua__ndpx + 1 +
                tmr__uxu.n_redvars))
            ccvua__ndpx += 1 + tmr__uxu.n_redvars
            out_data_typs.append(out_data_typs_[i])
    assert len(redvar_offsets) == xym__jfot
    gwt__akll = len(out_data_typs)
    iquwu__dmgqw = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    iquwu__dmgqw += '    if is_null_pointer(table):\n'
    iquwu__dmgqw += '        return\n'
    iquwu__dmgqw += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in lkllf__emf]), 
        ',' if len(lkllf__emf) == 1 else '')
    iquwu__dmgqw += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in
        out_data_typs]), ',' if len(out_data_typs) == 1 else '')
    for i in range(xym__jfot):
        iquwu__dmgqw += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(i, redvar_offsets[i], i))
        iquwu__dmgqw += '    incref(redvar_arr_{})\n'.format(i)
    iquwu__dmgqw += '    redvars = ({}{})\n'.format(','.join([
        'redvar_arr_{}'.format(i) for i in range(xym__jfot)]), ',' if 
        xym__jfot == 1 else '')
    iquwu__dmgqw += '\n'
    for i in range(gwt__akll):
        iquwu__dmgqw += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(i, asc__ciq[i], i))
        iquwu__dmgqw += '    incref(data_out_{})\n'.format(i)
    iquwu__dmgqw += '    data_out = ({}{})\n'.format(','.join([
        'data_out_{}'.format(i) for i in range(gwt__akll)]), ',' if 
        gwt__akll == 1 else '')
    iquwu__dmgqw += '\n'
    iquwu__dmgqw += '    for i in range(len(data_out_0)):\n'
    iquwu__dmgqw += '        __eval_res(redvars, data_out, i)\n'
    uvglg__ydnp = {}
    exec(iquwu__dmgqw, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, uvglg__ydnp)
    return uvglg__ydnp['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    ccvua__ndpx = n_keys
    nrh__hbhfv = []
    for i, tmr__uxu in enumerate(allfuncs):
        if tmr__uxu.ftype == 'gen_udf':
            nrh__hbhfv.append(ccvua__ndpx)
            ccvua__ndpx += 1
        elif tmr__uxu.ftype != 'udf':
            ccvua__ndpx += tmr__uxu.ncols_post_shuffle
        else:
            ccvua__ndpx += tmr__uxu.n_redvars + 1
    iquwu__dmgqw = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    iquwu__dmgqw += '    if num_groups == 0:\n'
    iquwu__dmgqw += '        return\n'
    for i, func in enumerate(udf_func_struct.general_udf_funcs):
        iquwu__dmgqw += '    # col {}\n'.format(i)
        iquwu__dmgqw += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(nrh__hbhfv[i], i))
        iquwu__dmgqw += '    incref(out_col)\n'
        iquwu__dmgqw += '    for j in range(num_groups):\n'
        iquwu__dmgqw += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(i, i))
        iquwu__dmgqw += '        incref(in_col)\n'
        iquwu__dmgqw += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(i))
    lhto__sguf = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    wgb__mcy = 0
    for i, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[wgb__mcy]
        lhto__sguf['func_{}'.format(wgb__mcy)] = func
        lhto__sguf['in_col_{}_typ'.format(wgb__mcy)] = in_col_typs[
            func_idx_to_in_col[i]]
        lhto__sguf['out_col_{}_typ'.format(wgb__mcy)] = out_col_typs[i]
        wgb__mcy += 1
    uvglg__ydnp = {}
    exec(iquwu__dmgqw, lhto__sguf, uvglg__ydnp)
    tmr__uxu = uvglg__ydnp['bodo_gb_apply_general_udfs{}'.format(label_suffix)]
    rftiv__kyvy = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(rftiv__kyvy, nopython=True)(tmr__uxu)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs, parallel,
    udf_func_struct):
    jyqe__neix = agg_node.pivot_arr is not None
    if agg_node.same_index:
        assert agg_node.input_has_index
    if agg_node.pivot_values is None:
        hdw__jbth = 1
    else:
        hdw__jbth = len(agg_node.pivot_values)
    iqbrs__epzyf = tuple('key_' + sanitize_varname(vjkf__znx) for vjkf__znx in
        agg_node.key_names)
    thjel__gqxfu = {vjkf__znx: 'in_{}'.format(sanitize_varname(vjkf__znx)) for
        vjkf__znx in agg_node.gb_info_in.keys() if vjkf__znx is not None}
    zll__wxgk = {vjkf__znx: ('out_' + sanitize_varname(vjkf__znx)) for
        vjkf__znx in agg_node.gb_info_out.keys()}
    n_keys = len(agg_node.key_names)
    fbo__bdu = ', '.join(iqbrs__epzyf)
    yceac__wax = ', '.join(thjel__gqxfu.values())
    if yceac__wax != '':
        yceac__wax = ', ' + yceac__wax
    iquwu__dmgqw = 'def agg_top({}{}{}, pivot_arr):\n'.format(fbo__bdu,
        yceac__wax, ', index_arg' if agg_node.input_has_index else '')
    if jyqe__neix:
        ntxv__gpusd = []
        for caax__kktoz, wmms__dbn in agg_node.gb_info_in.items():
            if caax__kktoz is not None:
                for func, gbaev__lvoo in wmms__dbn:
                    ntxv__gpusd.append(thjel__gqxfu[caax__kktoz])
    else:
        ntxv__gpusd = tuple(thjel__gqxfu[caax__kktoz] for caax__kktoz,
            gbaev__lvoo in agg_node.gb_info_out.values() if caax__kktoz is not
            None)
    yjjn__flgyg = iqbrs__epzyf + tuple(ntxv__gpusd)
    iquwu__dmgqw += '    info_list = [{}{}{}]\n'.format(', '.join(
        'array_to_info({})'.format(a) for a in yjjn__flgyg), 
        ', array_to_info(index_arg)' if agg_node.input_has_index else '', 
        ', array_to_info(pivot_arr)' if agg_node.is_crosstab else '')
    iquwu__dmgqw += '    table = arr_info_list_to_table(info_list)\n'
    for i, vjkf__znx in enumerate(agg_node.gb_info_out.keys()):
        ggn__uonjm = zll__wxgk[vjkf__znx] + '_dummy'
        xwubn__ttupj = out_col_typs[i]
        caax__kktoz, func = agg_node.gb_info_out[vjkf__znx]
        if isinstance(func, pytypes.SimpleNamespace) and func.fname in ['min',
            'max', 'shift'] and isinstance(xwubn__ttupj, bodo.
            CategoricalArrayType):
            iquwu__dmgqw += '    {} = {}\n'.format(ggn__uonjm, thjel__gqxfu
                [caax__kktoz])
        else:
            iquwu__dmgqw += '    {} = {}\n'.format(ggn__uonjm,
                _gen_dummy_alloc(xwubn__ttupj, i, False))
    do_combine = parallel
    allfuncs = []
    uvao__tiouz = []
    func_idx_to_in_col = []
    gtbd__tvo = []
    uscsd__begp = False
    omkt__inf = 1
    skfm__obh = -1
    strj__aurll = 0
    wjm__rwzm = 0
    if not jyqe__neix:
        lizt__ymd = [func for gbaev__lvoo, func in agg_node.gb_info_out.
            values()]
    else:
        lizt__ymd = [func for func, gbaev__lvoo in wmms__dbn for wmms__dbn in
            agg_node.gb_info_in.values()]
    for wbf__aqzx, func in enumerate(lizt__ymd):
        uvao__tiouz.append(len(allfuncs))
        if func.ftype in {'median', 'nunique'}:
            do_combine = False
        if func.ftype in list_cumulative:
            strj__aurll += 1
        if hasattr(func, 'skipdropna'):
            uscsd__begp = func.skipdropna
        if func.ftype == 'shift':
            omkt__inf = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            wjm__rwzm = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            skfm__obh = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(wbf__aqzx)
        if func.ftype == 'udf':
            gtbd__tvo.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            gtbd__tvo.append(0)
            do_combine = False
    uvao__tiouz.append(len(allfuncs))
    if agg_node.is_crosstab:
        assert len(agg_node.gb_info_out
            ) == hdw__jbth, 'invalid number of groupby outputs for pivot'
    else:
        assert len(agg_node.gb_info_out) == len(allfuncs
            ) * hdw__jbth, 'invalid number of groupby outputs'
    if strj__aurll > 0:
        if strj__aurll != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    if udf_func_struct is not None:
        aihxp__hoog = next_label()
        if udf_func_struct.regular_udfs:
            rftiv__kyvy = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            smp__opnub = numba.cfunc(rftiv__kyvy, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs,
                out_col_typs, do_combine, func_idx_to_in_col, aihxp__hoog))
            jaelp__ief = numba.cfunc(rftiv__kyvy, nopython=True)(gen_combine_cb
                (udf_func_struct, allfuncs, n_keys, out_col_typs, aihxp__hoog))
            oid__hcvcz = numba.cfunc('void(voidptr)', nopython=True)(
                gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_col_typs,
                aihxp__hoog))
            udf_func_struct.set_regular_cfuncs(smp__opnub, jaelp__ief,
                oid__hcvcz)
            for aivg__flf in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[aivg__flf.native_name] = aivg__flf
                gb_agg_cfunc_addr[aivg__flf.native_name] = aivg__flf.address
        if udf_func_struct.general_udfs:
            wbncj__fzvj = gen_general_udf_cb(udf_func_struct, allfuncs,
                n_keys, in_col_typs, out_col_typs, func_idx_to_in_col,
                aihxp__hoog)
            udf_func_struct.set_general_cfunc(wbncj__fzvj)
        hlnb__gqkp = []
        furs__sxb = 0
        i = 0
        for ggn__uonjm, tmr__uxu in zip(zll__wxgk.values(), allfuncs):
            if tmr__uxu.ftype in ('udf', 'gen_udf'):
                hlnb__gqkp.append(ggn__uonjm + '_dummy')
                for dbux__zid in range(furs__sxb, furs__sxb + gtbd__tvo[i]):
                    hlnb__gqkp.append('data_redvar_dummy_' + str(dbux__zid))
                furs__sxb += gtbd__tvo[i]
                i += 1
        if udf_func_struct.regular_udfs:
            lkllf__emf = udf_func_struct.var_typs
            for i, t in enumerate(lkllf__emf):
                iquwu__dmgqw += ('    data_redvar_dummy_{} = np.empty(1, {})\n'
                    .format(i, _get_np_dtype(t)))
        iquwu__dmgqw += '    out_info_list_dummy = [{}]\n'.format(', '.join
            ('array_to_info({})'.format(a) for a in hlnb__gqkp))
        iquwu__dmgqw += (
            '    udf_table_dummy = arr_info_list_to_table(out_info_list_dummy)\n'
            )
        if udf_func_struct.regular_udfs:
            iquwu__dmgqw += ("    add_agg_cfunc_sym(cpp_cb_update, '{}')\n"
                .format(smp__opnub.native_name))
            iquwu__dmgqw += ("    add_agg_cfunc_sym(cpp_cb_combine, '{}')\n"
                .format(jaelp__ief.native_name))
            iquwu__dmgqw += ("    add_agg_cfunc_sym(cpp_cb_eval, '{}')\n".
                format(oid__hcvcz.native_name))
            iquwu__dmgqw += (
                "    cpp_cb_update_addr = get_agg_udf_addr('{}')\n".format(
                smp__opnub.native_name))
            iquwu__dmgqw += (
                "    cpp_cb_combine_addr = get_agg_udf_addr('{}')\n".format
                (jaelp__ief.native_name))
            iquwu__dmgqw += ("    cpp_cb_eval_addr = get_agg_udf_addr('{}')\n"
                .format(oid__hcvcz.native_name))
        else:
            iquwu__dmgqw += '    cpp_cb_update_addr = 0\n'
            iquwu__dmgqw += '    cpp_cb_combine_addr = 0\n'
            iquwu__dmgqw += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            aivg__flf = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[aivg__flf.native_name] = aivg__flf
            gb_agg_cfunc_addr[aivg__flf.native_name] = aivg__flf.address
            iquwu__dmgqw += ("    add_agg_cfunc_sym(cpp_cb_general, '{}')\n"
                .format(aivg__flf.native_name))
            iquwu__dmgqw += (
                "    cpp_cb_general_addr = get_agg_udf_addr('{}')\n".format
                (aivg__flf.native_name))
        else:
            iquwu__dmgqw += '    cpp_cb_general_addr = 0\n'
    else:
        iquwu__dmgqw += """    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])
"""
        iquwu__dmgqw += '    cpp_cb_update_addr = 0\n'
        iquwu__dmgqw += '    cpp_cb_combine_addr = 0\n'
        iquwu__dmgqw += '    cpp_cb_eval_addr = 0\n'
        iquwu__dmgqw += '    cpp_cb_general_addr = 0\n'
    iquwu__dmgqw += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(
        ', '.join([str(supported_agg_funcs.index(tmr__uxu.ftype)) for
        tmr__uxu in allfuncs] + ['0']))
    iquwu__dmgqw += '    func_offsets = np.array({}, dtype=np.int32)\n'.format(
        str(uvao__tiouz))
    if len(gtbd__tvo) > 0:
        iquwu__dmgqw += ('    udf_ncols = np.array({}, dtype=np.int32)\n'.
            format(str(gtbd__tvo)))
    else:
        iquwu__dmgqw += '    udf_ncols = np.array([0], np.int32)\n'
    if jyqe__neix:
        iquwu__dmgqw += '    arr_type = coerce_to_array({})\n'.format(agg_node
            .pivot_values)
        iquwu__dmgqw += '    arr_info = array_to_info(arr_type)\n'
        iquwu__dmgqw += (
            '    dispatch_table = arr_info_list_to_table([arr_info])\n')
        iquwu__dmgqw += '    pivot_info = array_to_info(pivot_arr)\n'
        iquwu__dmgqw += (
            '    dispatch_info = arr_info_list_to_table([pivot_info])\n')
        iquwu__dmgqw += (
            """    out_table = pivot_groupby_and_aggregate(table, {}, dispatch_table, dispatch_info, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, agg_node.
            is_crosstab, uscsd__begp, agg_node.return_key, agg_node.same_index)
            )
        iquwu__dmgqw += '    delete_info_decref_array(pivot_info)\n'
        iquwu__dmgqw += '    delete_info_decref_array(arr_info)\n'
    else:
        iquwu__dmgqw += (
            """    out_table = groupby_and_aggregate(table, {}, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, uscsd__begp,
            omkt__inf, wjm__rwzm, skfm__obh, agg_node.return_key, agg_node.
            same_index, agg_node.dropna))
    nmxyg__mdc = 0
    if agg_node.return_key:
        for i, zawfn__fkcja in enumerate(iqbrs__epzyf):
            iquwu__dmgqw += (
                '    {} = info_to_array(info_from_table(out_table, {}), {})\n'
                .format(zawfn__fkcja, nmxyg__mdc, zawfn__fkcja))
            nmxyg__mdc += 1
    for ggn__uonjm in zll__wxgk.values():
        iquwu__dmgqw += (
            '    {} = info_to_array(info_from_table(out_table, {}), {})\n'.
            format(ggn__uonjm, nmxyg__mdc, ggn__uonjm + '_dummy'))
        nmxyg__mdc += 1
    if agg_node.same_index:
        iquwu__dmgqw += (
            """    out_index_arg = info_to_array(info_from_table(out_table, {}), index_arg)
"""
            .format(nmxyg__mdc))
        nmxyg__mdc += 1
    iquwu__dmgqw += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    iquwu__dmgqw += '    delete_table_decref_arrays(table)\n'
    iquwu__dmgqw += '    delete_table_decref_arrays(udf_table_dummy)\n'
    iquwu__dmgqw += '    delete_table(out_table)\n'
    iquwu__dmgqw += f'    ev_clean.finalize()\n'
    eee__rbr = tuple(zll__wxgk.values())
    if agg_node.return_key:
        eee__rbr += tuple(iqbrs__epzyf)
    iquwu__dmgqw += '    return ({},{})\n'.format(', '.join(eee__rbr), 
        ' out_index_arg,' if agg_node.same_index else '')
    uvglg__ydnp = {}
    exec(iquwu__dmgqw, {}, uvglg__ydnp)
    kkbhs__etswm = uvglg__ydnp['agg_top']
    return kkbhs__etswm


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for tnsfg__vxziz in block.body:
            if is_call_assign(tnsfg__vxziz) and find_callname(f_ir,
                tnsfg__vxziz.value) == ('len', 'builtins'
                ) and tnsfg__vxziz.value.args[0].name == f_ir.arg_names[0]:
                gmkm__lxafk = get_definition(f_ir, tnsfg__vxziz.value.func)
                gmkm__lxafk.name = 'dummy_agg_count'
                gmkm__lxafk.value = dummy_agg_count
    beez__uhkyk = get_name_var_table(f_ir.blocks)
    ivdid__nuhn = {}
    for name, gbaev__lvoo in beez__uhkyk.items():
        ivdid__nuhn[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, ivdid__nuhn)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    hzvnk__mmf = numba.core.compiler.Flags()
    hzvnk__mmf.nrt = True
    jmbu__npuv = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, hzvnk__mmf)
    jmbu__npuv.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, lzeax__iwpbv, calltypes, gbaev__lvoo = (numba.core.
        typed_passes.type_inference_stage(typingctx, targetctx, f_ir,
        arg_typs, None))
    cmjm__kdkfh = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    yunlu__dvfcl = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    zuqth__brbc = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    mxqtc__qkzol = zuqth__brbc(typemap, calltypes)
    pm = yunlu__dvfcl(typingctx, targetctx, None, f_ir, typemap,
        lzeax__iwpbv, calltypes, mxqtc__qkzol, {}, hzvnk__mmf, None)
    enxss__xci = (numba.core.compiler.DefaultPassBuilder.
        define_untyped_pipeline(pm))
    pm = yunlu__dvfcl(typingctx, targetctx, None, f_ir, typemap,
        lzeax__iwpbv, calltypes, mxqtc__qkzol, {}, hzvnk__mmf, enxss__xci)
    bbqpx__xquyd = numba.core.typed_passes.InlineOverloads()
    bbqpx__xquyd.run_pass(pm)
    mkl__bksh = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    mkl__bksh.run()
    for block in f_ir.blocks.values():
        for tnsfg__vxziz in block.body:
            if is_assign(tnsfg__vxziz) and isinstance(tnsfg__vxziz.value, (
                ir.Arg, ir.Var)) and isinstance(typemap[tnsfg__vxziz.target
                .name], SeriesType):
                ydxz__wdgbp = typemap.pop(tnsfg__vxziz.target.name)
                typemap[tnsfg__vxziz.target.name] = ydxz__wdgbp.data
            if is_call_assign(tnsfg__vxziz) and find_callname(f_ir,
                tnsfg__vxziz.value) == ('get_series_data',
                'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[tnsfg__vxziz.target.name].remove(tnsfg__vxziz
                    .value)
                tnsfg__vxziz.value = tnsfg__vxziz.value.args[0]
                f_ir._definitions[tnsfg__vxziz.target.name].append(tnsfg__vxziz
                    .value)
            if is_call_assign(tnsfg__vxziz) and find_callname(f_ir,
                tnsfg__vxziz.value) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[tnsfg__vxziz.target.name].remove(tnsfg__vxziz
                    .value)
                tnsfg__vxziz.value = ir.Const(False, tnsfg__vxziz.loc)
                f_ir._definitions[tnsfg__vxziz.target.name].append(tnsfg__vxziz
                    .value)
            if is_call_assign(tnsfg__vxziz) and find_callname(f_ir,
                tnsfg__vxziz.value) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[tnsfg__vxziz.target.name].remove(tnsfg__vxziz
                    .value)
                tnsfg__vxziz.value = ir.Const(False, tnsfg__vxziz.loc)
                f_ir._definitions[tnsfg__vxziz.target.name].append(tnsfg__vxziz
                    .value)
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    siq__mchy = numba.parfors.parfor.PreParforPass(f_ir, typemap, calltypes,
        typingctx, targetctx, cmjm__kdkfh)
    siq__mchy.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    betsw__qhghj = numba.core.compiler.StateDict()
    betsw__qhghj.func_ir = f_ir
    betsw__qhghj.typemap = typemap
    betsw__qhghj.calltypes = calltypes
    betsw__qhghj.typingctx = typingctx
    betsw__qhghj.targetctx = targetctx
    betsw__qhghj.return_type = lzeax__iwpbv
    numba.core.rewrites.rewrite_registry.apply('after-inference', betsw__qhghj)
    jpf__nbpy = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        lzeax__iwpbv, typingctx, targetctx, cmjm__kdkfh, hzvnk__mmf, {})
    jpf__nbpy.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            ccryu__kzz = ctypes.pythonapi.PyCell_Get
            ccryu__kzz.restype = ctypes.py_object
            ccryu__kzz.argtypes = ctypes.py_object,
            nvye__fnhtw = tuple(ccryu__kzz(ukseb__uvj) for ukseb__uvj in
                closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            nvye__fnhtw = closure.items
        assert len(code.co_freevars) == len(nvye__fnhtw)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks,
            nvye__fnhtw)


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
        oje__edv = SeriesType(in_col_typ.dtype, in_col_typ, None, string_type)
        f_ir, pm = compile_to_optimized_ir(func, (oje__edv,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        jxb__ivt, arr_var = _rm_arg_agg_block(block, pm.typemap)
        nnrl__bgylk = -1
        for i, tnsfg__vxziz in enumerate(jxb__ivt):
            if isinstance(tnsfg__vxziz, numba.parfors.parfor.Parfor):
                assert nnrl__bgylk == -1, 'only one parfor for aggregation function'
                nnrl__bgylk = i
        parfor = None
        if nnrl__bgylk != -1:
            parfor = jxb__ivt[nnrl__bgylk]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = jxb__ivt[:nnrl__bgylk] + parfor.init_block.body
        eval_nodes = jxb__ivt[nnrl__bgylk + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for tnsfg__vxziz in init_nodes:
            if is_assign(tnsfg__vxziz) and tnsfg__vxziz.target.name in redvars:
                ind = redvars.index(tnsfg__vxziz.target.name)
                reduce_vars[ind] = tnsfg__vxziz.target
        var_types = [pm.typemap[v] for v in redvars]
        kygh__ulj = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        nur__wos = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        ccs__vbvww = gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types,
            pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(ccs__vbvww)
        self.all_update_funcs.append(nur__wos)
        self.all_combine_funcs.append(kygh__ulj)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        self.all_vartypes = self.all_vartypes * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_vartypes
        self.all_reduce_vars = self.all_reduce_vars * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_reduce_vars
        memb__lqamh = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        iwy__neagg = gen_all_update_func(self.all_update_funcs, self.
            all_vartypes, self.in_col_types, self.redvar_offsets, self.
            typingctx, self.targetctx, self.pivot_typ, self.pivot_values,
            self.is_crosstab)
        xqbl__totpc = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.
            targetctx, self.pivot_typ, self.pivot_values)
        fyro__zskq = gen_all_eval_func(self.all_eval_funcs, self.
            all_vartypes, self.redvar_offsets, self.out_col_types, self.
            typingctx, self.targetctx, self.pivot_values)
        return (self.all_vartypes, memb__lqamh, iwy__neagg, xqbl__totpc,
            fyro__zskq)


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
    ibeox__gajdv = []
    for t, tmr__uxu in zip(in_col_types, agg_func):
        ibeox__gajdv.append((t, tmr__uxu))
    dllr__qipxd = RegularUDFGenerator(in_col_types, out_col_types,
        pivot_typ, pivot_values, is_crosstab, typingctx, targetctx)
    vkuz__koh = GeneralUDFGenerator()
    for in_col_typ, func in ibeox__gajdv:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            dllr__qipxd.add_udf(in_col_typ, func)
        except:
            vkuz__koh.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = dllr__qipxd.gen_all_func()
    general_udf_funcs = vkuz__koh.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    mzs__rjm = compute_use_defs(parfor.loop_body)
    fssp__qkeie = set()
    for pqrv__iou in mzs__rjm.usemap.values():
        fssp__qkeie |= pqrv__iou
    syis__jcai = set()
    for pqrv__iou in mzs__rjm.defmap.values():
        syis__jcai |= pqrv__iou
    xobq__makv = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    xobq__makv.body = eval_nodes
    dfgq__rlc = compute_use_defs({(0): xobq__makv})
    ikkj__xjgsv = dfgq__rlc.usemap[0]
    mtkx__oahgv = set()
    uki__rfdab = []
    hdih__qul = []
    for tnsfg__vxziz in reversed(init_nodes):
        llre__zlpj = {v.name for v in tnsfg__vxziz.list_vars()}
        if is_assign(tnsfg__vxziz):
            v = tnsfg__vxziz.target.name
            llre__zlpj.remove(v)
            if (v in fssp__qkeie and v not in mtkx__oahgv and v not in
                ikkj__xjgsv and v not in syis__jcai):
                hdih__qul.append(tnsfg__vxziz)
                fssp__qkeie |= llre__zlpj
                syis__jcai.add(v)
                continue
        mtkx__oahgv |= llre__zlpj
        uki__rfdab.append(tnsfg__vxziz)
    hdih__qul.reverse()
    uki__rfdab.reverse()
    lyjw__vzb = min(parfor.loop_body.keys())
    sigv__tzmx = parfor.loop_body[lyjw__vzb]
    sigv__tzmx.body = hdih__qul + sigv__tzmx.body
    return uki__rfdab


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    efgbt__lnv = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    eru__qvfnx = set()
    wrd__irlum = []
    for tnsfg__vxziz in init_nodes:
        if is_assign(tnsfg__vxziz) and isinstance(tnsfg__vxziz.value, ir.Global
            ) and isinstance(tnsfg__vxziz.value.value, pytypes.FunctionType
            ) and tnsfg__vxziz.value.value in efgbt__lnv:
            eru__qvfnx.add(tnsfg__vxziz.target.name)
        elif is_call_assign(tnsfg__vxziz
            ) and tnsfg__vxziz.value.func.name in eru__qvfnx:
            pass
        else:
            wrd__irlum.append(tnsfg__vxziz)
    init_nodes = wrd__irlum
    ksifr__qmky = types.Tuple(var_types)
    tmc__ews = lambda : None
    f_ir = compile_to_numba_ir(tmc__ews, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    kuc__opvf = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    tkw__mhi = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc), kuc__opvf, loc)
    block.body = block.body[-2:]
    block.body = init_nodes + [tkw__mhi] + block.body
    block.body[-2].value.value = kuc__opvf
    lfefo__bljkn = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        ksifr__qmky, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    pvky__air = numba.core.target_extension.dispatcher_registry[cpu_target](
        tmc__ews)
    pvky__air.add_overload(lfefo__bljkn)
    return pvky__air


def gen_all_update_func(update_funcs, reduce_var_types, in_col_types,
    redvar_offsets, typingctx, targetctx, pivot_typ, pivot_values, is_crosstab
    ):
    ftmt__fqh = len(update_funcs)
    innmz__dlds = len(in_col_types)
    if pivot_values is not None:
        assert innmz__dlds == 1
    iquwu__dmgqw = (
        'def update_all_f(redvar_arrs, data_in, w_ind, i, pivot_arr):\n')
    if pivot_values is not None:
        riyxm__byjkf = redvar_offsets[innmz__dlds]
        iquwu__dmgqw += '  pv = pivot_arr[i]\n'
        for dbux__zid, kphgz__odaqh in enumerate(pivot_values):
            dfozd__trb = 'el' if dbux__zid != 0 else ''
            iquwu__dmgqw += "  {}if pv == '{}':\n".format(dfozd__trb,
                kphgz__odaqh)
            gxdoy__etgrh = riyxm__byjkf * dbux__zid
            dyh__knhk = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for i in
                range(gxdoy__etgrh + redvar_offsets[0], gxdoy__etgrh +
                redvar_offsets[1])])
            awzc__rgj = 'data_in[0][i]'
            if is_crosstab:
                awzc__rgj = '0'
            iquwu__dmgqw += '    {} = update_vars_0({}, {})\n'.format(dyh__knhk
                , dyh__knhk, awzc__rgj)
    else:
        for dbux__zid in range(ftmt__fqh):
            dyh__knhk = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for i in
                range(redvar_offsets[dbux__zid], redvar_offsets[dbux__zid +
                1])])
            if dyh__knhk:
                iquwu__dmgqw += ('  {} = update_vars_{}({},  data_in[{}][i])\n'
                    .format(dyh__knhk, dbux__zid, dyh__knhk, 0 if 
                    innmz__dlds == 1 else dbux__zid))
    iquwu__dmgqw += '  return\n'
    lhto__sguf = {}
    for i, tmr__uxu in enumerate(update_funcs):
        lhto__sguf['update_vars_{}'.format(i)] = tmr__uxu
    uvglg__ydnp = {}
    exec(iquwu__dmgqw, lhto__sguf, uvglg__ydnp)
    pfsx__kvvcj = uvglg__ydnp['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(pfsx__kvvcj)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx, pivot_typ, pivot_values):
    wwuwt__zuw = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types]
        )
    arg_typs = wwuwt__zuw, wwuwt__zuw, types.intp, types.intp, pivot_typ
    fnxd__tce = len(redvar_offsets) - 1
    riyxm__byjkf = redvar_offsets[fnxd__tce]
    iquwu__dmgqw = (
        'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i, pivot_arr):\n')
    if pivot_values is not None:
        assert fnxd__tce == 1
        for lsji__ksfpm in range(len(pivot_values)):
            gxdoy__etgrh = riyxm__byjkf * lsji__ksfpm
            dyh__knhk = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for i in
                range(gxdoy__etgrh + redvar_offsets[0], gxdoy__etgrh +
                redvar_offsets[1])])
            udrkc__sapd = ', '.join(['recv_arrs[{}][i]'.format(i) for i in
                range(gxdoy__etgrh + redvar_offsets[0], gxdoy__etgrh +
                redvar_offsets[1])])
            iquwu__dmgqw += '  {} = combine_vars_0({}, {})\n'.format(dyh__knhk,
                dyh__knhk, udrkc__sapd)
    else:
        for dbux__zid in range(fnxd__tce):
            dyh__knhk = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for i in
                range(redvar_offsets[dbux__zid], redvar_offsets[dbux__zid +
                1])])
            udrkc__sapd = ', '.join(['recv_arrs[{}][i]'.format(i) for i in
                range(redvar_offsets[dbux__zid], redvar_offsets[dbux__zid +
                1])])
            if udrkc__sapd:
                iquwu__dmgqw += '  {} = combine_vars_{}({}, {})\n'.format(
                    dyh__knhk, dbux__zid, dyh__knhk, udrkc__sapd)
    iquwu__dmgqw += '  return\n'
    lhto__sguf = {}
    for i, tmr__uxu in enumerate(combine_funcs):
        lhto__sguf['combine_vars_{}'.format(i)] = tmr__uxu
    uvglg__ydnp = {}
    exec(iquwu__dmgqw, lhto__sguf, uvglg__ydnp)
    ucau__bfjf = uvglg__ydnp['combine_all_f']
    f_ir = compile_to_numba_ir(ucau__bfjf, lhto__sguf)
    xqbl__totpc = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    pvky__air = numba.core.target_extension.dispatcher_registry[cpu_target](
        ucau__bfjf)
    pvky__air.add_overload(xqbl__totpc)
    return pvky__air


def gen_all_eval_func(eval_funcs, reduce_var_types, redvar_offsets,
    out_col_typs, typingctx, targetctx, pivot_values):
    wwuwt__zuw = types.Tuple([types.Array(t, 1, 'C') for t in reduce_var_types]
        )
    out_col_typs = types.Tuple(out_col_typs)
    fnxd__tce = len(redvar_offsets) - 1
    riyxm__byjkf = redvar_offsets[fnxd__tce]
    iquwu__dmgqw = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    if pivot_values is not None:
        assert fnxd__tce == 1
        for dbux__zid in range(len(pivot_values)):
            gxdoy__etgrh = riyxm__byjkf * dbux__zid
            dyh__knhk = ', '.join(['redvar_arrs[{}][j]'.format(i) for i in
                range(gxdoy__etgrh + redvar_offsets[0], gxdoy__etgrh +
                redvar_offsets[1])])
            iquwu__dmgqw += '  out_arrs[{}][j] = eval_vars_0({})\n'.format(
                dbux__zid, dyh__knhk)
    else:
        for dbux__zid in range(fnxd__tce):
            dyh__knhk = ', '.join(['redvar_arrs[{}][j]'.format(i) for i in
                range(redvar_offsets[dbux__zid], redvar_offsets[dbux__zid +
                1])])
            iquwu__dmgqw += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(
                dbux__zid, dbux__zid, dyh__knhk)
    iquwu__dmgqw += '  return\n'
    lhto__sguf = {}
    for i, tmr__uxu in enumerate(eval_funcs):
        lhto__sguf['eval_vars_{}'.format(i)] = tmr__uxu
    uvglg__ydnp = {}
    exec(iquwu__dmgqw, lhto__sguf, uvglg__ydnp)
    syuva__fqiq = uvglg__ydnp['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(syuva__fqiq)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    bvwb__rpb = len(var_types)
    atvkv__amfnj = [f'in{i}' for i in range(bvwb__rpb)]
    ksifr__qmky = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    jfj__zgwyu = ksifr__qmky(0)
    iquwu__dmgqw = 'def agg_eval({}):\n return _zero\n'.format(', '.join(
        atvkv__amfnj))
    uvglg__ydnp = {}
    exec(iquwu__dmgqw, {'_zero': jfj__zgwyu}, uvglg__ydnp)
    mruj__xhdei = uvglg__ydnp['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(mruj__xhdei, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': jfj__zgwyu}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    ztfk__mewld = []
    for i, v in enumerate(reduce_vars):
        ztfk__mewld.append(ir.Assign(block.body[i].target, v, v.loc))
        for jfxd__hbsf in v.versioned_names:
            ztfk__mewld.append(ir.Assign(v, ir.Var(v.scope, jfxd__hbsf, v.
                loc), v.loc))
    block.body = block.body[:bvwb__rpb] + ztfk__mewld + eval_nodes
    ccs__vbvww = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        ksifr__qmky, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    pvky__air = numba.core.target_extension.dispatcher_registry[cpu_target](
        mruj__xhdei)
    pvky__air.add_overload(ccs__vbvww)
    return pvky__air


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    bvwb__rpb = len(redvars)
    gxs__lybio = [f'v{i}' for i in range(bvwb__rpb)]
    atvkv__amfnj = [f'in{i}' for i in range(bvwb__rpb)]
    iquwu__dmgqw = 'def agg_combine({}):\n'.format(', '.join(gxs__lybio +
        atvkv__amfnj))
    efnp__nlvtm = wrap_parfor_blocks(parfor)
    pru__cyue = find_topo_order(efnp__nlvtm)
    pru__cyue = pru__cyue[1:]
    unwrap_parfor_blocks(parfor)
    nom__rqs = {}
    wnjyt__sjjdy = []
    for gcuqf__biv in pru__cyue:
        cgcu__ptny = parfor.loop_body[gcuqf__biv]
        for tnsfg__vxziz in cgcu__ptny.body:
            if is_call_assign(tnsfg__vxziz) and guard(find_callname, f_ir,
                tnsfg__vxziz.value) == ('__special_combine',
                'bodo.ir.aggregate'):
                args = tnsfg__vxziz.value.args
                zrip__luav = []
                pou__yukb = []
                for v in args[:-1]:
                    ind = redvars.index(v.name)
                    wnjyt__sjjdy.append(ind)
                    zrip__luav.append('v{}'.format(ind))
                    pou__yukb.append('in{}'.format(ind))
                lsnix__ghww = '__special_combine__{}'.format(len(nom__rqs))
                iquwu__dmgqw += '    ({},) = {}({})\n'.format(', '.join(
                    zrip__luav), lsnix__ghww, ', '.join(zrip__luav + pou__yukb)
                    )
                qqh__xhf = ir.Expr.call(args[-1], [], (), cgcu__ptny.loc)
                bsvpg__mukbk = guard(find_callname, f_ir, qqh__xhf)
                assert bsvpg__mukbk == ('_var_combine', 'bodo.ir.aggregate')
                bsvpg__mukbk = bodo.ir.aggregate._var_combine
                nom__rqs[lsnix__ghww] = bsvpg__mukbk
            if is_assign(tnsfg__vxziz) and tnsfg__vxziz.target.name in redvars:
                gyjt__drr = tnsfg__vxziz.target.name
                ind = redvars.index(gyjt__drr)
                if ind in wnjyt__sjjdy:
                    continue
                if len(f_ir._definitions[gyjt__drr]) == 2:
                    var_def = f_ir._definitions[gyjt__drr][0]
                    iquwu__dmgqw += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[gyjt__drr][1]
                    iquwu__dmgqw += _match_reduce_def(var_def, f_ir, ind)
    iquwu__dmgqw += '    return {}'.format(', '.join(['v{}'.format(i) for i in
        range(bvwb__rpb)]))
    uvglg__ydnp = {}
    exec(iquwu__dmgqw, {}, uvglg__ydnp)
    sihxp__qlxmw = uvglg__ydnp['agg_combine']
    arg_typs = tuple(2 * var_types)
    lhto__sguf = {'numba': numba, 'bodo': bodo, 'np': np}
    lhto__sguf.update(nom__rqs)
    f_ir = compile_to_numba_ir(sihxp__qlxmw, lhto__sguf, typingctx=
        typingctx, targetctx=targetctx, arg_typs=arg_typs, typemap=pm.
        typemap, calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    ksifr__qmky = pm.typemap[block.body[-1].value.name]
    kygh__ulj = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        ksifr__qmky, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    pvky__air = numba.core.target_extension.dispatcher_registry[cpu_target](
        sihxp__qlxmw)
    pvky__air.add_overload(kygh__ulj)
    return pvky__air


def _match_reduce_def(var_def, f_ir, ind):
    iquwu__dmgqw = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        iquwu__dmgqw = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        yhl__wwqv = guard(find_callname, f_ir, var_def)
        if yhl__wwqv == ('min', 'builtins'):
            iquwu__dmgqw = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if yhl__wwqv == ('max', 'builtins'):
            iquwu__dmgqw = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return iquwu__dmgqw


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    bvwb__rpb = len(redvars)
    asbf__tto = 1
    ysy__zbk = []
    for i in range(asbf__tto):
        qtgp__wtvwm = ir.Var(arr_var.scope, f'$input{i}', arr_var.loc)
        ysy__zbk.append(qtgp__wtvwm)
    whc__wbczw = parfor.loop_nests[0].index_variable
    belx__zuri = [0] * bvwb__rpb
    for cgcu__ptny in parfor.loop_body.values():
        mjqob__xdzom = []
        for tnsfg__vxziz in cgcu__ptny.body:
            if is_var_assign(tnsfg__vxziz
                ) and tnsfg__vxziz.value.name == whc__wbczw.name:
                continue
            if is_getitem(tnsfg__vxziz
                ) and tnsfg__vxziz.value.value.name == arr_var.name:
                tnsfg__vxziz.value = ysy__zbk[0]
            if is_call_assign(tnsfg__vxziz) and guard(find_callname, pm.
                func_ir, tnsfg__vxziz.value) == ('isna',
                'bodo.libs.array_kernels') and tnsfg__vxziz.value.args[0
                ].name == arr_var.name:
                tnsfg__vxziz.value = ir.Const(False, tnsfg__vxziz.target.loc)
            if is_assign(tnsfg__vxziz) and tnsfg__vxziz.target.name in redvars:
                ind = redvars.index(tnsfg__vxziz.target.name)
                belx__zuri[ind] = tnsfg__vxziz.target
            mjqob__xdzom.append(tnsfg__vxziz)
        cgcu__ptny.body = mjqob__xdzom
    gxs__lybio = ['v{}'.format(i) for i in range(bvwb__rpb)]
    atvkv__amfnj = ['in{}'.format(i) for i in range(asbf__tto)]
    iquwu__dmgqw = 'def agg_update({}):\n'.format(', '.join(gxs__lybio +
        atvkv__amfnj))
    iquwu__dmgqw += '    __update_redvars()\n'
    iquwu__dmgqw += '    return {}'.format(', '.join(['v{}'.format(i) for i in
        range(bvwb__rpb)]))
    uvglg__ydnp = {}
    exec(iquwu__dmgqw, {}, uvglg__ydnp)
    nip__ujral = uvglg__ydnp['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * asbf__tto)
    f_ir = compile_to_numba_ir(nip__ujral, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    shz__yiq = f_ir.blocks.popitem()[1].body
    ksifr__qmky = pm.typemap[shz__yiq[-1].value.name]
    efnp__nlvtm = wrap_parfor_blocks(parfor)
    pru__cyue = find_topo_order(efnp__nlvtm)
    pru__cyue = pru__cyue[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    sigv__tzmx = f_ir.blocks[pru__cyue[0]]
    wir__dtfrw = f_ir.blocks[pru__cyue[-1]]
    vuby__rpzoe = shz__yiq[:bvwb__rpb + asbf__tto]
    if bvwb__rpb > 1:
        edgi__wjpee = shz__yiq[-3:]
        assert is_assign(edgi__wjpee[0]) and isinstance(edgi__wjpee[0].
            value, ir.Expr) and edgi__wjpee[0].value.op == 'build_tuple'
    else:
        edgi__wjpee = shz__yiq[-2:]
    for i in range(bvwb__rpb):
        vlky__tgwpx = shz__yiq[i].target
        csual__whs = ir.Assign(vlky__tgwpx, belx__zuri[i], vlky__tgwpx.loc)
        vuby__rpzoe.append(csual__whs)
    for i in range(bvwb__rpb, bvwb__rpb + asbf__tto):
        vlky__tgwpx = shz__yiq[i].target
        csual__whs = ir.Assign(vlky__tgwpx, ysy__zbk[i - bvwb__rpb],
            vlky__tgwpx.loc)
        vuby__rpzoe.append(csual__whs)
    sigv__tzmx.body = vuby__rpzoe + sigv__tzmx.body
    owi__okq = []
    for i in range(bvwb__rpb):
        vlky__tgwpx = shz__yiq[i].target
        csual__whs = ir.Assign(belx__zuri[i], vlky__tgwpx, vlky__tgwpx.loc)
        owi__okq.append(csual__whs)
    wir__dtfrw.body += owi__okq + edgi__wjpee
    umtd__mew = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        ksifr__qmky, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    pvky__air = numba.core.target_extension.dispatcher_registry[cpu_target](
        nip__ujral)
    pvky__air.add_overload(umtd__mew)
    return pvky__air


def _rm_arg_agg_block(block, typemap):
    jxb__ivt = []
    arr_var = None
    for i, tnsfg__vxziz in enumerate(block.body):
        if is_assign(tnsfg__vxziz) and isinstance(tnsfg__vxziz.value, ir.Arg):
            arr_var = tnsfg__vxziz.target
            sul__oyxc = typemap[arr_var.name]
            if not isinstance(sul__oyxc, types.ArrayCompatible):
                jxb__ivt += block.body[i + 1:]
                break
            nmf__xylfd = block.body[i + 1]
            assert is_assign(nmf__xylfd) and isinstance(nmf__xylfd.value,
                ir.Expr
                ) and nmf__xylfd.value.op == 'getattr' and nmf__xylfd.value.attr == 'shape' and nmf__xylfd.value.value.name == arr_var.name
            esnr__umf = nmf__xylfd.target
            olb__ouyvp = block.body[i + 2]
            assert is_assign(olb__ouyvp) and isinstance(olb__ouyvp.value,
                ir.Expr
                ) and olb__ouyvp.value.op == 'static_getitem' and olb__ouyvp.value.value.name == esnr__umf.name
            jxb__ivt += block.body[i + 3:]
            break
        jxb__ivt.append(tnsfg__vxziz)
    return jxb__ivt, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    efnp__nlvtm = wrap_parfor_blocks(parfor)
    pru__cyue = find_topo_order(efnp__nlvtm)
    pru__cyue = pru__cyue[1:]
    unwrap_parfor_blocks(parfor)
    for gcuqf__biv in reversed(pru__cyue):
        for tnsfg__vxziz in reversed(parfor.loop_body[gcuqf__biv].body):
            if isinstance(tnsfg__vxziz, ir.Assign) and (tnsfg__vxziz.target
                .name in parfor_params or tnsfg__vxziz.target.name in
                var_to_param):
                ijcv__kag = tnsfg__vxziz.target.name
                rhs = tnsfg__vxziz.value
                ijmnt__upygp = (ijcv__kag if ijcv__kag in parfor_params else
                    var_to_param[ijcv__kag])
                mbyco__vesqc = []
                if isinstance(rhs, ir.Var):
                    mbyco__vesqc = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    mbyco__vesqc = [v.name for v in tnsfg__vxziz.value.
                        list_vars()]
                param_uses[ijmnt__upygp].extend(mbyco__vesqc)
                for v in mbyco__vesqc:
                    var_to_param[v] = ijmnt__upygp
            if isinstance(tnsfg__vxziz, Parfor):
                get_parfor_reductions(tnsfg__vxziz, parfor_params,
                    calltypes, reduce_varnames, param_uses, var_to_param)
    for oowb__wgv, mbyco__vesqc in param_uses.items():
        if oowb__wgv in mbyco__vesqc and oowb__wgv not in reduce_varnames:
            reduce_varnames.append(oowb__wgv)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
