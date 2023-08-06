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
            hddd__vxkds = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer()])
            cbs__hmb = cgutils.get_or_insert_function(builder.module,
                hddd__vxkds, sym._literal_value)
            builder.call(cbs__hmb, [context.get_constant_null(sig.args[0])])
        elif sig == types.none(types.int64, types.voidptr, types.voidptr):
            hddd__vxkds = lir.FunctionType(lir.VoidType(), [lir.IntType(64),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
            cbs__hmb = cgutils.get_or_insert_function(builder.module,
                hddd__vxkds, sym._literal_value)
            builder.call(cbs__hmb, [context.get_constant(types.int64, 0),
                context.get_constant_null(sig.args[1]), context.
                get_constant_null(sig.args[2])])
        else:
            hddd__vxkds = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64).
                as_pointer()])
            cbs__hmb = cgutils.get_or_insert_function(builder.module,
                hddd__vxkds, sym._literal_value)
            builder.call(cbs__hmb, [context.get_constant_null(sig.args[0]),
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
        leov__lez = True
        pxttw__zhwpe = 1
        jmbw__gkbke = -1
        if isinstance(rhs, ir.Expr):
            for xejmj__nqau in rhs.kws:
                if func_name in list_cumulative:
                    if xejmj__nqau[0] == 'skipna':
                        leov__lez = guard(find_const, func_ir, xejmj__nqau[1])
                        if not isinstance(leov__lez, bool):
                            raise BodoError(
                                'For {} argument of skipna should be a boolean'
                                .format(func_name))
                if func_name == 'nunique':
                    if xejmj__nqau[0] == 'dropna':
                        leov__lez = guard(find_const, func_ir, xejmj__nqau[1])
                        if not isinstance(leov__lez, bool):
                            raise BodoError(
                                'argument of dropna to nunique should be a boolean'
                                )
        if func_name == 'shift' and (len(rhs.args) > 0 or len(rhs.kws) > 0):
            pxttw__zhwpe = get_call_expr_arg('shift', rhs.args, dict(rhs.
                kws), 0, 'periods', pxttw__zhwpe)
            pxttw__zhwpe = guard(find_const, func_ir, pxttw__zhwpe)
        if func_name == 'head':
            jmbw__gkbke = get_call_expr_arg('head', rhs.args, dict(rhs.kws),
                0, 'n', 5)
            if not isinstance(jmbw__gkbke, int):
                jmbw__gkbke = guard(find_const, func_ir, jmbw__gkbke)
            if jmbw__gkbke < 0:
                raise BodoError(
                    f'groupby.{func_name} does not work with negative values.')
        func.skipdropna = leov__lez
        func.periods = pxttw__zhwpe
        func.head_n = jmbw__gkbke
        if func_name == 'transform':
            kws = dict(rhs.kws)
            vdu__tbayw = get_call_expr_arg(func_name, rhs.args, kws, 0,
                'func', '')
            sqw__zzy = typemap[vdu__tbayw.name]
            cbei__jxfbs = None
            if isinstance(sqw__zzy, str):
                cbei__jxfbs = sqw__zzy
            elif is_overload_constant_str(sqw__zzy):
                cbei__jxfbs = get_overload_const_str(sqw__zzy)
            elif bodo.utils.typing.is_builtin_function(sqw__zzy):
                cbei__jxfbs = bodo.utils.typing.get_builtin_function_name(
                    sqw__zzy)
            if cbei__jxfbs not in bodo.ir.aggregate.supported_transform_funcs[:
                ]:
                raise BodoError(f'unsupported transform function {cbei__jxfbs}'
                    )
            func.transform_func = supported_agg_funcs.index(cbei__jxfbs)
        else:
            func.transform_func = supported_agg_funcs.index('no_op')
        return func
    assert func_name in ['agg', 'aggregate']
    assert typemap is not None
    kws = dict(rhs.kws)
    vdu__tbayw = get_call_expr_arg(func_name, rhs.args, kws, 0, 'func', '')
    if vdu__tbayw == '':
        sqw__zzy = types.none
    else:
        sqw__zzy = typemap[vdu__tbayw.name]
    if is_overload_constant_dict(sqw__zzy):
        vywh__mdhwf = get_overload_constant_dict(sqw__zzy)
        kyufa__jwg = [get_agg_func_udf(func_ir, f_val, rhs, series_type,
            typemap) for f_val in vywh__mdhwf.values()]
        return kyufa__jwg
    if sqw__zzy == types.none:
        return [get_agg_func_udf(func_ir, get_literal_value(typemap[f_val.
            name])[1], rhs, series_type, typemap) for f_val in kws.values()]
    if isinstance(sqw__zzy, types.BaseTuple):
        kyufa__jwg = []
        qmx__lolfw = 0
        for t in sqw__zzy.types:
            if is_overload_constant_str(t):
                func_name = get_overload_const_str(t)
                kyufa__jwg.append(get_agg_func(func_ir, func_name, rhs,
                    series_type, typemap))
            else:
                assert typemap is not None, 'typemap is required for agg UDF handling'
                func = _get_const_agg_func(t, func_ir)
                func.ftype = 'udf'
                func.fname = _get_udf_name(func)
                if func.fname == '<lambda>':
                    func.fname = '<lambda_' + str(qmx__lolfw) + '>'
                    qmx__lolfw += 1
                kyufa__jwg.append(func)
        return [kyufa__jwg]
    if is_overload_constant_str(sqw__zzy):
        func_name = get_overload_const_str(sqw__zzy)
        return get_agg_func(func_ir, func_name, rhs, series_type, typemap)
    if bodo.utils.typing.is_builtin_function(sqw__zzy):
        func_name = bodo.utils.typing.get_builtin_function_name(sqw__zzy)
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
        qmx__lolfw = 0
        cdoeg__can = []
        for rapz__bqnl in f_val:
            func = get_agg_func_udf(func_ir, rapz__bqnl, rhs, series_type,
                typemap)
            if func.fname == '<lambda>' and len(f_val) > 1:
                func.fname = f'<lambda_{qmx__lolfw}>'
                qmx__lolfw += 1
            cdoeg__can.append(func)
        return cdoeg__can
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
    cbei__jxfbs = code.co_name
    return cbei__jxfbs


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
            sihcb__rku = types.DType(args[0])
            return signature(sihcb__rku, *args)


@numba.njit(no_cpython_wrapper=True)
def _var_combine(ssqdm_a, mean_a, nobs_a, ssqdm_b, mean_b, nobs_b):
    laq__bozxc = nobs_a + nobs_b
    clizz__sjmbr = (nobs_a * mean_a + nobs_b * mean_b) / laq__bozxc
    ojv__cvrtc = mean_b - mean_a
    tbgp__zxfos = (ssqdm_a + ssqdm_b + ojv__cvrtc * ojv__cvrtc * nobs_a *
        nobs_b / laq__bozxc)
    return tbgp__zxfos, clizz__sjmbr, laq__bozxc


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
        eoqx__konlt = ''
        for avc__jwf, v in self.df_out_vars.items():
            eoqx__konlt += "'{}':{}, ".format(avc__jwf, v.name)
        adkk__czpp = '{}{{{}}}'.format(self.df_out, eoqx__konlt)
        pxvk__brjh = ''
        for avc__jwf, v in self.df_in_vars.items():
            pxvk__brjh += "'{}':{}, ".format(avc__jwf, v.name)
        poyb__hiuyt = '{}{{{}}}'.format(self.df_in, pxvk__brjh)
        clegw__mjbzx = 'pivot {}:{}'.format(self.pivot_arr.name, self.
            pivot_values) if self.pivot_arr is not None else ''
        key_names = ','.join(self.key_names)
        xsz__pku = ','.join([v.name for v in self.key_arrs])
        return 'aggregate: {} = {} [key: {}:{}] {}'.format(adkk__czpp,
            poyb__hiuyt, key_names, xsz__pku, clegw__mjbzx)

    def remove_out_col(self, out_col_name):
        self.df_out_vars.pop(out_col_name)
        wapvs__equqa, rzdp__boj = self.gb_info_out.pop(out_col_name)
        if wapvs__equqa is None and not self.is_crosstab:
            return
        zpi__azeqi = self.gb_info_in[wapvs__equqa]
        if self.pivot_arr is not None:
            self.pivot_values.remove(out_col_name)
            for i, (func, eoqx__konlt) in enumerate(zpi__azeqi):
                try:
                    eoqx__konlt.remove(out_col_name)
                    if len(eoqx__konlt) == 0:
                        zpi__azeqi.pop(i)
                        break
                except ValueError as wcvs__wquhz:
                    continue
        else:
            for i, (func, eysb__pnx) in enumerate(zpi__azeqi):
                if eysb__pnx == out_col_name:
                    zpi__azeqi.pop(i)
                    break
        if len(zpi__azeqi) == 0:
            self.gb_info_in.pop(wapvs__equqa)
            self.df_in_vars.pop(wapvs__equqa)


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
    tqvap__yxul = [zljg__lnce for zljg__lnce, iwm__hzx in aggregate_node.
        df_out_vars.items() if iwm__hzx.name not in lives]
    for dlzlw__ibyq in tqvap__yxul:
        aggregate_node.remove_out_col(dlzlw__ibyq)
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
    nuf__ghki = set(v.name for v in aggregate_node.df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        nuf__ghki.update({v.name for v in aggregate_node.out_key_vars})
    return set(), nuf__ghki


ir_utils.copy_propagate_extensions[Aggregate] = get_copies_aggregate


def apply_copies_aggregate(aggregate_node, var_dict, name_var_table,
    typemap, calltypes, save_copies):
    for i in range(len(aggregate_node.key_arrs)):
        aggregate_node.key_arrs[i] = replace_vars_inner(aggregate_node.
            key_arrs[i], var_dict)
    for zljg__lnce in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[zljg__lnce] = replace_vars_inner(
            aggregate_node.df_in_vars[zljg__lnce], var_dict)
    for zljg__lnce in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[zljg__lnce] = replace_vars_inner(
            aggregate_node.df_out_vars[zljg__lnce], var_dict)
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
    for zljg__lnce in list(aggregate_node.df_in_vars.keys()):
        aggregate_node.df_in_vars[zljg__lnce] = visit_vars_inner(aggregate_node
            .df_in_vars[zljg__lnce], callback, cbdata)
    for zljg__lnce in list(aggregate_node.df_out_vars.keys()):
        aggregate_node.df_out_vars[zljg__lnce] = visit_vars_inner(
            aggregate_node.df_out_vars[zljg__lnce], callback, cbdata)
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
    xrukd__ttah = []
    for gla__jekqz in aggregate_node.key_arrs:
        sbqom__eouyx = equiv_set.get_shape(gla__jekqz)
        if sbqom__eouyx:
            xrukd__ttah.append(sbqom__eouyx[0])
    if aggregate_node.pivot_arr is not None:
        sbqom__eouyx = equiv_set.get_shape(aggregate_node.pivot_arr)
        if sbqom__eouyx:
            xrukd__ttah.append(sbqom__eouyx[0])
    for iwm__hzx in aggregate_node.df_in_vars.values():
        sbqom__eouyx = equiv_set.get_shape(iwm__hzx)
        if sbqom__eouyx:
            xrukd__ttah.append(sbqom__eouyx[0])
    if len(xrukd__ttah) > 1:
        equiv_set.insert_equiv(*xrukd__ttah)
    ubyv__wtp = []
    xrukd__ttah = []
    eylvq__iic = list(aggregate_node.df_out_vars.values())
    if aggregate_node.out_key_vars is not None:
        eylvq__iic.extend(aggregate_node.out_key_vars)
    for iwm__hzx in eylvq__iic:
        jhm__smvfz = typemap[iwm__hzx.name]
        eky__dvc = array_analysis._gen_shape_call(equiv_set, iwm__hzx,
            jhm__smvfz.ndim, None, ubyv__wtp)
        equiv_set.insert_equiv(iwm__hzx, eky__dvc)
        xrukd__ttah.append(eky__dvc[0])
        equiv_set.define(iwm__hzx, set())
    if len(xrukd__ttah) > 1:
        equiv_set.insert_equiv(*xrukd__ttah)
    return [], ubyv__wtp


numba.parfors.array_analysis.array_analysis_extensions[Aggregate
    ] = aggregate_array_analysis


def aggregate_distributed_analysis(aggregate_node, array_dists):
    auzv__bjabh = Distribution.OneD
    for iwm__hzx in aggregate_node.df_in_vars.values():
        auzv__bjabh = Distribution(min(auzv__bjabh.value, array_dists[
            iwm__hzx.name].value))
    for gla__jekqz in aggregate_node.key_arrs:
        auzv__bjabh = Distribution(min(auzv__bjabh.value, array_dists[
            gla__jekqz.name].value))
    if aggregate_node.pivot_arr is not None:
        auzv__bjabh = Distribution(min(auzv__bjabh.value, array_dists[
            aggregate_node.pivot_arr.name].value))
        array_dists[aggregate_node.pivot_arr.name] = auzv__bjabh
    for iwm__hzx in aggregate_node.df_in_vars.values():
        array_dists[iwm__hzx.name] = auzv__bjabh
    for gla__jekqz in aggregate_node.key_arrs:
        array_dists[gla__jekqz.name] = auzv__bjabh
    oebx__ucjj = Distribution.OneD_Var
    for iwm__hzx in aggregate_node.df_out_vars.values():
        if iwm__hzx.name in array_dists:
            oebx__ucjj = Distribution(min(oebx__ucjj.value, array_dists[
                iwm__hzx.name].value))
    if aggregate_node.out_key_vars is not None:
        for iwm__hzx in aggregate_node.out_key_vars:
            if iwm__hzx.name in array_dists:
                oebx__ucjj = Distribution(min(oebx__ucjj.value, array_dists
                    [iwm__hzx.name].value))
    oebx__ucjj = Distribution(min(oebx__ucjj.value, auzv__bjabh.value))
    for iwm__hzx in aggregate_node.df_out_vars.values():
        array_dists[iwm__hzx.name] = oebx__ucjj
    if aggregate_node.out_key_vars is not None:
        for daxz__fwg in aggregate_node.out_key_vars:
            array_dists[daxz__fwg.name] = oebx__ucjj
    if oebx__ucjj != Distribution.OneD_Var:
        for gla__jekqz in aggregate_node.key_arrs:
            array_dists[gla__jekqz.name] = oebx__ucjj
        if aggregate_node.pivot_arr is not None:
            array_dists[aggregate_node.pivot_arr.name] = oebx__ucjj
        for iwm__hzx in aggregate_node.df_in_vars.values():
            array_dists[iwm__hzx.name] = oebx__ucjj


distributed_analysis.distributed_analysis_extensions[Aggregate
    ] = aggregate_distributed_analysis


def build_agg_definitions(agg_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for iwm__hzx in agg_node.df_out_vars.values():
        definitions[iwm__hzx.name].append(agg_node)
    if agg_node.out_key_vars is not None:
        for daxz__fwg in agg_node.out_key_vars:
            definitions[daxz__fwg.name].append(agg_node)
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
    xywvr__biy = tuple(typemap[v.name] for v in agg_node.key_arrs)
    szb__dsvu = [v for hcuwr__fdnqi, v in agg_node.df_in_vars.items()]
    jrha__dmkrg = [v for hcuwr__fdnqi, v in agg_node.df_out_vars.items()]
    in_col_typs = []
    kyufa__jwg = []
    if agg_node.pivot_arr is not None:
        for wapvs__equqa, zpi__azeqi in agg_node.gb_info_in.items():
            for func, rzdp__boj in zpi__azeqi:
                if wapvs__equqa is not None:
                    in_col_typs.append(typemap[agg_node.df_in_vars[
                        wapvs__equqa].name])
                kyufa__jwg.append(func)
    else:
        for wapvs__equqa, func in agg_node.gb_info_out.values():
            if wapvs__equqa is not None:
                in_col_typs.append(typemap[agg_node.df_in_vars[wapvs__equqa
                    ].name])
            kyufa__jwg.append(func)
    out_col_typs = tuple(typemap[v.name] for v in jrha__dmkrg)
    pivot_typ = types.none if agg_node.pivot_arr is None else typemap[agg_node
        .pivot_arr.name]
    arg_typs = tuple(xywvr__biy + tuple(typemap[v.name] for v in szb__dsvu) +
        (pivot_typ,))
    trsgu__req = {'bodo': bodo, 'np': np, 'dt64_dtype': np.dtype(
        'datetime64[ns]'), 'td64_dtype': np.dtype('timedelta64[ns]')}
    for i, in_col_typ in enumerate(in_col_typs):
        if isinstance(in_col_typ, bodo.CategoricalArrayType):
            trsgu__req.update({f'in_cat_dtype_{i}': in_col_typ})
    for i, xhuxh__kysb in enumerate(out_col_typs):
        if isinstance(xhuxh__kysb, bodo.CategoricalArrayType):
            trsgu__req.update({f'out_cat_dtype_{i}': xhuxh__kysb})
    udf_func_struct = get_udf_func_struct(kyufa__jwg, agg_node.
        input_has_index, in_col_typs, out_col_typs, typingctx, targetctx,
        pivot_typ, agg_node.pivot_values, agg_node.is_crosstab)
    daoai__vlodz = gen_top_level_agg_func(agg_node, in_col_typs,
        out_col_typs, parallel, udf_func_struct)
    trsgu__req.update({'pd': pd, 'pre_alloc_string_array':
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
            trsgu__req.update({'__update_redvars': udf_func_struct.
                update_all_func, '__init_func': udf_func_struct.init_func,
                '__combine_redvars': udf_func_struct.combine_all_func,
                '__eval_res': udf_func_struct.eval_all_func,
                'cpp_cb_update': udf_func_struct.regular_udf_cfuncs[0],
                'cpp_cb_combine': udf_func_struct.regular_udf_cfuncs[1],
                'cpp_cb_eval': udf_func_struct.regular_udf_cfuncs[2]})
        if udf_func_struct.general_udfs:
            trsgu__req.update({'cpp_cb_general': udf_func_struct.
                general_udf_cfunc})
    eynh__aprb = compile_to_numba_ir(daoai__vlodz, trsgu__req, typingctx=
        typingctx, targetctx=targetctx, arg_typs=arg_typs, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    fqcj__xqub = []
    if agg_node.pivot_arr is None:
        gkmxq__rte = agg_node.key_arrs[0].scope
        loc = agg_node.loc
        qefy__gqks = ir.Var(gkmxq__rte, mk_unique_var('dummy_none'), loc)
        typemap[qefy__gqks.name] = types.none
        fqcj__xqub.append(ir.Assign(ir.Const(None, loc), qefy__gqks, loc))
        szb__dsvu.append(qefy__gqks)
    else:
        szb__dsvu.append(agg_node.pivot_arr)
    replace_arg_nodes(eynh__aprb, agg_node.key_arrs + szb__dsvu)
    iiz__jbuz = eynh__aprb.body[-3]
    assert is_assign(iiz__jbuz) and isinstance(iiz__jbuz.value, ir.Expr
        ) and iiz__jbuz.value.op == 'build_tuple'
    fqcj__xqub += eynh__aprb.body[:-3]
    eylvq__iic = list(agg_node.df_out_vars.values())
    if agg_node.out_key_vars is not None:
        eylvq__iic += agg_node.out_key_vars
    for i, thal__guq in enumerate(eylvq__iic):
        tpxyc__hqcf = iiz__jbuz.value.items[i]
        fqcj__xqub.append(ir.Assign(tpxyc__hqcf, thal__guq, thal__guq.loc))
    return fqcj__xqub


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
        wyjkg__fdya = args[0]
        if wyjkg__fdya == types.none:
            return signature(types.boolean, *args)


@lower_builtin(bool, types.none)
def lower_column_mean_impl(context, builder, sig, args):
    wxet__eqm = context.compile_internal(builder, lambda a: False, sig, args)
    return wxet__eqm


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
        iii__qhvk = IntDtype(t.dtype).name
        assert iii__qhvk.endswith('Dtype()')
        iii__qhvk = iii__qhvk[:-7]
        return (
            f"bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype='{iii__qhvk}'))"
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
        qxl__dffo = 'in' if is_input else 'out'
        return (
            f'bodo.utils.utils.alloc_type(1, {qxl__dffo}_cat_dtype_{colnum})')
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
    ggu__lzxv = udf_func_struct.var_typs
    ukhei__gjtvb = len(ggu__lzxv)
    mwuz__iod = (
        'def bodo_gb_udf_update_local{}(in_table, out_table, row_to_group):\n'
        .format(label_suffix))
    mwuz__iod += '    if is_null_pointer(in_table):\n'
    mwuz__iod += '        return\n'
    mwuz__iod += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in ggu__lzxv]), 
        ',' if len(ggu__lzxv) == 1 else '')
    gsj__wsucv = n_keys
    fjd__sjnkq = []
    redvar_offsets = []
    myf__qqw = []
    if do_combine:
        for i, rapz__bqnl in enumerate(allfuncs):
            if rapz__bqnl.ftype != 'udf':
                gsj__wsucv += rapz__bqnl.ncols_pre_shuffle
            else:
                redvar_offsets += list(range(gsj__wsucv, gsj__wsucv +
                    rapz__bqnl.n_redvars))
                gsj__wsucv += rapz__bqnl.n_redvars
                myf__qqw.append(data_in_typs_[func_idx_to_in_col[i]])
                fjd__sjnkq.append(func_idx_to_in_col[i] + n_keys)
    else:
        for i, rapz__bqnl in enumerate(allfuncs):
            if rapz__bqnl.ftype != 'udf':
                gsj__wsucv += rapz__bqnl.ncols_post_shuffle
            else:
                redvar_offsets += list(range(gsj__wsucv + 1, gsj__wsucv + 1 +
                    rapz__bqnl.n_redvars))
                gsj__wsucv += rapz__bqnl.n_redvars + 1
                myf__qqw.append(data_in_typs_[func_idx_to_in_col[i]])
                fjd__sjnkq.append(func_idx_to_in_col[i] + n_keys)
    assert len(redvar_offsets) == ukhei__gjtvb
    dppqx__nuowi = len(myf__qqw)
    gvso__ayj = []
    for i, t in enumerate(myf__qqw):
        gvso__ayj.append(_gen_dummy_alloc(t, i, True))
    mwuz__iod += '    data_in_dummy = ({}{})\n'.format(','.join(gvso__ayj),
        ',' if len(myf__qqw) == 1 else '')
    mwuz__iod += """
    # initialize redvar cols
"""
    mwuz__iod += '    init_vals = __init_func()\n'
    for i in range(ukhei__gjtvb):
        mwuz__iod += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(i, redvar_offsets[i], i))
        mwuz__iod += '    incref(redvar_arr_{})\n'.format(i)
        mwuz__iod += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(i, i)
    mwuz__iod += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(i) for i in range(ukhei__gjtvb)]), ',' if ukhei__gjtvb == 1 else
        '')
    mwuz__iod += '\n'
    for i in range(dppqx__nuowi):
        mwuz__iod += (
            """    data_in_{} = info_to_array(info_from_table(in_table, {}), data_in_dummy[{}])
"""
            .format(i, fjd__sjnkq[i], i))
        mwuz__iod += '    incref(data_in_{})\n'.format(i)
    mwuz__iod += '    data_in = ({}{})\n'.format(','.join(['data_in_{}'.
        format(i) for i in range(dppqx__nuowi)]), ',' if dppqx__nuowi == 1 else
        '')
    mwuz__iod += '\n'
    mwuz__iod += '    for i in range(len(data_in_0)):\n'
    mwuz__iod += '        w_ind = row_to_group[i]\n'
    mwuz__iod += '        if w_ind != -1:\n'
    mwuz__iod += (
        '            __update_redvars(redvars, data_in, w_ind, i, pivot_arr=None)\n'
        )
    fzjo__vohg = {}
    exec(mwuz__iod, {'bodo': bodo, 'np': np, 'pd': pd, 'info_to_array':
        info_to_array, 'info_from_table': info_from_table, 'incref': incref,
        'pre_alloc_string_array': pre_alloc_string_array, '__init_func':
        udf_func_struct.init_func, '__update_redvars': udf_func_struct.
        update_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, fzjo__vohg)
    return fzjo__vohg['bodo_gb_udf_update_local{}'.format(label_suffix)]


def gen_combine_cb(udf_func_struct, allfuncs, n_keys, out_data_typs,
    label_suffix):
    ggu__lzxv = udf_func_struct.var_typs
    ukhei__gjtvb = len(ggu__lzxv)
    mwuz__iod = (
        'def bodo_gb_udf_combine{}(in_table, out_table, row_to_group):\n'.
        format(label_suffix))
    mwuz__iod += '    if is_null_pointer(in_table):\n'
    mwuz__iod += '        return\n'
    mwuz__iod += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in ggu__lzxv]), 
        ',' if len(ggu__lzxv) == 1 else '')
    yid__mkvli = n_keys
    weej__zmhx = n_keys
    yak__nams = []
    oddly__nvor = []
    for rapz__bqnl in allfuncs:
        if rapz__bqnl.ftype != 'udf':
            yid__mkvli += rapz__bqnl.ncols_pre_shuffle
            weej__zmhx += rapz__bqnl.ncols_post_shuffle
        else:
            yak__nams += list(range(yid__mkvli, yid__mkvli + rapz__bqnl.
                n_redvars))
            oddly__nvor += list(range(weej__zmhx + 1, weej__zmhx + 1 +
                rapz__bqnl.n_redvars))
            yid__mkvli += rapz__bqnl.n_redvars
            weej__zmhx += 1 + rapz__bqnl.n_redvars
    assert len(yak__nams) == ukhei__gjtvb
    mwuz__iod += """
    # initialize redvar cols
"""
    mwuz__iod += '    init_vals = __init_func()\n'
    for i in range(ukhei__gjtvb):
        mwuz__iod += (
            """    redvar_arr_{} = info_to_array(info_from_table(out_table, {}), data_redvar_dummy[{}])
"""
            .format(i, oddly__nvor[i], i))
        mwuz__iod += '    incref(redvar_arr_{})\n'.format(i)
        mwuz__iod += '    redvar_arr_{}.fill(init_vals[{}])\n'.format(i, i)
    mwuz__iod += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(i) for i in range(ukhei__gjtvb)]), ',' if ukhei__gjtvb == 1 else
        '')
    mwuz__iod += '\n'
    for i in range(ukhei__gjtvb):
        mwuz__iod += (
            """    recv_redvar_arr_{} = info_to_array(info_from_table(in_table, {}), data_redvar_dummy[{}])
"""
            .format(i, yak__nams[i], i))
        mwuz__iod += '    incref(recv_redvar_arr_{})\n'.format(i)
    mwuz__iod += '    recv_redvars = ({}{})\n'.format(','.join([
        'recv_redvar_arr_{}'.format(i) for i in range(ukhei__gjtvb)]), ',' if
        ukhei__gjtvb == 1 else '')
    mwuz__iod += '\n'
    if ukhei__gjtvb:
        mwuz__iod += '    for i in range(len(recv_redvar_arr_0)):\n'
        mwuz__iod += '        w_ind = row_to_group[i]\n'
        mwuz__iod += (
            '        __combine_redvars(redvars, recv_redvars, w_ind, i, pivot_arr=None)\n'
            )
    fzjo__vohg = {}
    exec(mwuz__iod, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__init_func':
        udf_func_struct.init_func, '__combine_redvars': udf_func_struct.
        combine_all_func, 'is_null_pointer': is_null_pointer, 'dt64_dtype':
        np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, fzjo__vohg)
    return fzjo__vohg['bodo_gb_udf_combine{}'.format(label_suffix)]


def gen_eval_cb(udf_func_struct, allfuncs, n_keys, out_data_typs_, label_suffix
    ):
    ggu__lzxv = udf_func_struct.var_typs
    ukhei__gjtvb = len(ggu__lzxv)
    gsj__wsucv = n_keys
    redvar_offsets = []
    uexkq__ffq = []
    out_data_typs = []
    for i, rapz__bqnl in enumerate(allfuncs):
        if rapz__bqnl.ftype != 'udf':
            gsj__wsucv += rapz__bqnl.ncols_post_shuffle
        else:
            uexkq__ffq.append(gsj__wsucv)
            redvar_offsets += list(range(gsj__wsucv + 1, gsj__wsucv + 1 +
                rapz__bqnl.n_redvars))
            gsj__wsucv += 1 + rapz__bqnl.n_redvars
            out_data_typs.append(out_data_typs_[i])
    assert len(redvar_offsets) == ukhei__gjtvb
    dppqx__nuowi = len(out_data_typs)
    mwuz__iod = 'def bodo_gb_udf_eval{}(table):\n'.format(label_suffix)
    mwuz__iod += '    if is_null_pointer(table):\n'
    mwuz__iod += '        return\n'
    mwuz__iod += '    data_redvar_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t)) for t in ggu__lzxv]), 
        ',' if len(ggu__lzxv) == 1 else '')
    mwuz__iod += '    out_data_dummy = ({}{})\n'.format(','.join([
        'np.empty(1, {})'.format(_get_np_dtype(t.dtype)) for t in
        out_data_typs]), ',' if len(out_data_typs) == 1 else '')
    for i in range(ukhei__gjtvb):
        mwuz__iod += (
            """    redvar_arr_{} = info_to_array(info_from_table(table, {}), data_redvar_dummy[{}])
"""
            .format(i, redvar_offsets[i], i))
        mwuz__iod += '    incref(redvar_arr_{})\n'.format(i)
    mwuz__iod += '    redvars = ({}{})\n'.format(','.join(['redvar_arr_{}'.
        format(i) for i in range(ukhei__gjtvb)]), ',' if ukhei__gjtvb == 1 else
        '')
    mwuz__iod += '\n'
    for i in range(dppqx__nuowi):
        mwuz__iod += (
            """    data_out_{} = info_to_array(info_from_table(table, {}), out_data_dummy[{}])
"""
            .format(i, uexkq__ffq[i], i))
        mwuz__iod += '    incref(data_out_{})\n'.format(i)
    mwuz__iod += '    data_out = ({}{})\n'.format(','.join(['data_out_{}'.
        format(i) for i in range(dppqx__nuowi)]), ',' if dppqx__nuowi == 1 else
        '')
    mwuz__iod += '\n'
    mwuz__iod += '    for i in range(len(data_out_0)):\n'
    mwuz__iod += '        __eval_res(redvars, data_out, i)\n'
    fzjo__vohg = {}
    exec(mwuz__iod, {'np': np, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref, '__eval_res':
        udf_func_struct.eval_all_func, 'is_null_pointer': is_null_pointer,
        'dt64_dtype': np.dtype('datetime64[ns]'), 'td64_dtype': np.dtype(
        'timedelta64[ns]')}, fzjo__vohg)
    return fzjo__vohg['bodo_gb_udf_eval{}'.format(label_suffix)]


def gen_general_udf_cb(udf_func_struct, allfuncs, n_keys, in_col_typs,
    out_col_typs, func_idx_to_in_col, label_suffix):
    gsj__wsucv = n_keys
    sxw__mkbux = []
    for i, rapz__bqnl in enumerate(allfuncs):
        if rapz__bqnl.ftype == 'gen_udf':
            sxw__mkbux.append(gsj__wsucv)
            gsj__wsucv += 1
        elif rapz__bqnl.ftype != 'udf':
            gsj__wsucv += rapz__bqnl.ncols_post_shuffle
        else:
            gsj__wsucv += rapz__bqnl.n_redvars + 1
    mwuz__iod = (
        'def bodo_gb_apply_general_udfs{}(num_groups, in_table, out_table):\n'
        .format(label_suffix))
    mwuz__iod += '    if num_groups == 0:\n'
    mwuz__iod += '        return\n'
    for i, func in enumerate(udf_func_struct.general_udf_funcs):
        mwuz__iod += '    # col {}\n'.format(i)
        mwuz__iod += (
            """    out_col = info_to_array(info_from_table(out_table, {}), out_col_{}_typ)
"""
            .format(sxw__mkbux[i], i))
        mwuz__iod += '    incref(out_col)\n'
        mwuz__iod += '    for j in range(num_groups):\n'
        mwuz__iod += (
            """        in_col = info_to_array(info_from_table(in_table, {}*num_groups + j), in_col_{}_typ)
"""
            .format(i, i))
        mwuz__iod += '        incref(in_col)\n'
        mwuz__iod += (
            '        out_col[j] = func_{}(pd.Series(in_col))  # func returns scalar\n'
            .format(i))
    trsgu__req = {'pd': pd, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'incref': incref}
    wmlfb__fst = 0
    for i, func in enumerate(allfuncs):
        if func.ftype != 'gen_udf':
            continue
        func = udf_func_struct.general_udf_funcs[wmlfb__fst]
        trsgu__req['func_{}'.format(wmlfb__fst)] = func
        trsgu__req['in_col_{}_typ'.format(wmlfb__fst)] = in_col_typs[
            func_idx_to_in_col[i]]
        trsgu__req['out_col_{}_typ'.format(wmlfb__fst)] = out_col_typs[i]
        wmlfb__fst += 1
    fzjo__vohg = {}
    exec(mwuz__iod, trsgu__req, fzjo__vohg)
    rapz__bqnl = fzjo__vohg['bodo_gb_apply_general_udfs{}'.format(label_suffix)
        ]
    wpcw__jgsc = types.void(types.int64, types.voidptr, types.voidptr)
    return numba.cfunc(wpcw__jgsc, nopython=True)(rapz__bqnl)


def gen_top_level_agg_func(agg_node, in_col_typs, out_col_typs, parallel,
    udf_func_struct):
    sqbr__yrs = agg_node.pivot_arr is not None
    if agg_node.same_index:
        assert agg_node.input_has_index
    if agg_node.pivot_values is None:
        okm__njlgu = 1
    else:
        okm__njlgu = len(agg_node.pivot_values)
    obce__ggovo = tuple('key_' + sanitize_varname(avc__jwf) for avc__jwf in
        agg_node.key_names)
    cikm__rcvuo = {avc__jwf: 'in_{}'.format(sanitize_varname(avc__jwf)) for
        avc__jwf in agg_node.gb_info_in.keys() if avc__jwf is not None}
    dynws__mqo = {avc__jwf: ('out_' + sanitize_varname(avc__jwf)) for
        avc__jwf in agg_node.gb_info_out.keys()}
    n_keys = len(agg_node.key_names)
    odr__crzc = ', '.join(obce__ggovo)
    rbfx__wgolt = ', '.join(cikm__rcvuo.values())
    if rbfx__wgolt != '':
        rbfx__wgolt = ', ' + rbfx__wgolt
    mwuz__iod = 'def agg_top({}{}{}, pivot_arr):\n'.format(odr__crzc,
        rbfx__wgolt, ', index_arg' if agg_node.input_has_index else '')
    if sqbr__yrs:
        ofoc__orjwa = []
        for wapvs__equqa, zpi__azeqi in agg_node.gb_info_in.items():
            if wapvs__equqa is not None:
                for func, rzdp__boj in zpi__azeqi:
                    ofoc__orjwa.append(cikm__rcvuo[wapvs__equqa])
    else:
        ofoc__orjwa = tuple(cikm__rcvuo[wapvs__equqa] for wapvs__equqa,
            rzdp__boj in agg_node.gb_info_out.values() if wapvs__equqa is not
            None)
    ihsjm__ptqng = obce__ggovo + tuple(ofoc__orjwa)
    mwuz__iod += '    info_list = [{}{}{}]\n'.format(', '.join(
        'array_to_info({})'.format(a) for a in ihsjm__ptqng), 
        ', array_to_info(index_arg)' if agg_node.input_has_index else '', 
        ', array_to_info(pivot_arr)' if agg_node.is_crosstab else '')
    mwuz__iod += '    table = arr_info_list_to_table(info_list)\n'
    for i, avc__jwf in enumerate(agg_node.gb_info_out.keys()):
        cqks__cdkxj = dynws__mqo[avc__jwf] + '_dummy'
        xhuxh__kysb = out_col_typs[i]
        wapvs__equqa, func = agg_node.gb_info_out[avc__jwf]
        if isinstance(func, pytypes.SimpleNamespace) and func.fname in ['min',
            'max', 'shift'] and isinstance(xhuxh__kysb, bodo.
            CategoricalArrayType):
            mwuz__iod += '    {} = {}\n'.format(cqks__cdkxj, cikm__rcvuo[
                wapvs__equqa])
        else:
            mwuz__iod += '    {} = {}\n'.format(cqks__cdkxj,
                _gen_dummy_alloc(xhuxh__kysb, i, False))
    do_combine = parallel
    allfuncs = []
    dwwf__bmuu = []
    func_idx_to_in_col = []
    dctys__tepa = []
    leov__lez = False
    hbv__fjovi = 1
    jmbw__gkbke = -1
    oala__vcb = 0
    dhe__qdr = 0
    if not sqbr__yrs:
        kyufa__jwg = [func for rzdp__boj, func in agg_node.gb_info_out.values()
            ]
    else:
        kyufa__jwg = [func for func, rzdp__boj in zpi__azeqi for zpi__azeqi in
            agg_node.gb_info_in.values()]
    for ehd__qesj, func in enumerate(kyufa__jwg):
        dwwf__bmuu.append(len(allfuncs))
        if func.ftype in {'median', 'nunique'}:
            do_combine = False
        if func.ftype in list_cumulative:
            oala__vcb += 1
        if hasattr(func, 'skipdropna'):
            leov__lez = func.skipdropna
        if func.ftype == 'shift':
            hbv__fjovi = func.periods
            do_combine = False
        if func.ftype in {'transform'}:
            dhe__qdr = func.transform_func
            do_combine = False
        if func.ftype == 'head':
            jmbw__gkbke = func.head_n
            do_combine = False
        allfuncs.append(func)
        func_idx_to_in_col.append(ehd__qesj)
        if func.ftype == 'udf':
            dctys__tepa.append(func.n_redvars)
        elif func.ftype == 'gen_udf':
            dctys__tepa.append(0)
            do_combine = False
    dwwf__bmuu.append(len(allfuncs))
    if agg_node.is_crosstab:
        assert len(agg_node.gb_info_out
            ) == okm__njlgu, 'invalid number of groupby outputs for pivot'
    else:
        assert len(agg_node.gb_info_out) == len(allfuncs
            ) * okm__njlgu, 'invalid number of groupby outputs'
    if oala__vcb > 0:
        if oala__vcb != len(allfuncs):
            raise BodoError(
                f'{agg_node.func_name}(): Cannot mix cumulative operations with other aggregation functions'
                , loc=agg_node.loc)
        do_combine = False
    if udf_func_struct is not None:
        sia__pbd = next_label()
        if udf_func_struct.regular_udfs:
            wpcw__jgsc = types.void(types.voidptr, types.voidptr, types.
                CPointer(types.int64))
            hbb__qbi = numba.cfunc(wpcw__jgsc, nopython=True)(gen_update_cb
                (udf_func_struct, allfuncs, n_keys, in_col_typs,
                out_col_typs, do_combine, func_idx_to_in_col, sia__pbd))
            nodi__wpcrm = numba.cfunc(wpcw__jgsc, nopython=True)(gen_combine_cb
                (udf_func_struct, allfuncs, n_keys, out_col_typs, sia__pbd))
            gic__snc = numba.cfunc('void(voidptr)', nopython=True)(gen_eval_cb
                (udf_func_struct, allfuncs, n_keys, out_col_typs, sia__pbd))
            udf_func_struct.set_regular_cfuncs(hbb__qbi, nodi__wpcrm, gic__snc)
            for aeyk__ukysb in udf_func_struct.regular_udf_cfuncs:
                gb_agg_cfunc[aeyk__ukysb.native_name] = aeyk__ukysb
                gb_agg_cfunc_addr[aeyk__ukysb.native_name
                    ] = aeyk__ukysb.address
        if udf_func_struct.general_udfs:
            nkoew__xfpt = gen_general_udf_cb(udf_func_struct, allfuncs,
                n_keys, in_col_typs, out_col_typs, func_idx_to_in_col, sia__pbd
                )
            udf_func_struct.set_general_cfunc(nkoew__xfpt)
        qcc__tvzz = []
        ccvw__ccl = 0
        i = 0
        for cqks__cdkxj, rapz__bqnl in zip(dynws__mqo.values(), allfuncs):
            if rapz__bqnl.ftype in ('udf', 'gen_udf'):
                qcc__tvzz.append(cqks__cdkxj + '_dummy')
                for cvqf__wjesb in range(ccvw__ccl, ccvw__ccl + dctys__tepa[i]
                    ):
                    qcc__tvzz.append('data_redvar_dummy_' + str(cvqf__wjesb))
                ccvw__ccl += dctys__tepa[i]
                i += 1
        if udf_func_struct.regular_udfs:
            ggu__lzxv = udf_func_struct.var_typs
            for i, t in enumerate(ggu__lzxv):
                mwuz__iod += ('    data_redvar_dummy_{} = np.empty(1, {})\n'
                    .format(i, _get_np_dtype(t)))
        mwuz__iod += '    out_info_list_dummy = [{}]\n'.format(', '.join(
            'array_to_info({})'.format(a) for a in qcc__tvzz))
        mwuz__iod += (
            '    udf_table_dummy = arr_info_list_to_table(out_info_list_dummy)\n'
            )
        if udf_func_struct.regular_udfs:
            mwuz__iod += "    add_agg_cfunc_sym(cpp_cb_update, '{}')\n".format(
                hbb__qbi.native_name)
            mwuz__iod += ("    add_agg_cfunc_sym(cpp_cb_combine, '{}')\n".
                format(nodi__wpcrm.native_name))
            mwuz__iod += "    add_agg_cfunc_sym(cpp_cb_eval, '{}')\n".format(
                gic__snc.native_name)
            mwuz__iod += ("    cpp_cb_update_addr = get_agg_udf_addr('{}')\n"
                .format(hbb__qbi.native_name))
            mwuz__iod += ("    cpp_cb_combine_addr = get_agg_udf_addr('{}')\n"
                .format(nodi__wpcrm.native_name))
            mwuz__iod += ("    cpp_cb_eval_addr = get_agg_udf_addr('{}')\n"
                .format(gic__snc.native_name))
        else:
            mwuz__iod += '    cpp_cb_update_addr = 0\n'
            mwuz__iod += '    cpp_cb_combine_addr = 0\n'
            mwuz__iod += '    cpp_cb_eval_addr = 0\n'
        if udf_func_struct.general_udfs:
            aeyk__ukysb = udf_func_struct.general_udf_cfunc
            gb_agg_cfunc[aeyk__ukysb.native_name] = aeyk__ukysb
            gb_agg_cfunc_addr[aeyk__ukysb.native_name] = aeyk__ukysb.address
            mwuz__iod += ("    add_agg_cfunc_sym(cpp_cb_general, '{}')\n".
                format(aeyk__ukysb.native_name))
            mwuz__iod += ("    cpp_cb_general_addr = get_agg_udf_addr('{}')\n"
                .format(aeyk__ukysb.native_name))
        else:
            mwuz__iod += '    cpp_cb_general_addr = 0\n'
    else:
        mwuz__iod += (
            '    udf_table_dummy = arr_info_list_to_table([array_to_info(np.empty(1))])\n'
            )
        mwuz__iod += '    cpp_cb_update_addr = 0\n'
        mwuz__iod += '    cpp_cb_combine_addr = 0\n'
        mwuz__iod += '    cpp_cb_eval_addr = 0\n'
        mwuz__iod += '    cpp_cb_general_addr = 0\n'
    mwuz__iod += '    ftypes = np.array([{}, 0], dtype=np.int32)\n'.format(', '
        .join([str(supported_agg_funcs.index(rapz__bqnl.ftype)) for
        rapz__bqnl in allfuncs] + ['0']))
    mwuz__iod += '    func_offsets = np.array({}, dtype=np.int32)\n'.format(str
        (dwwf__bmuu))
    if len(dctys__tepa) > 0:
        mwuz__iod += '    udf_ncols = np.array({}, dtype=np.int32)\n'.format(
            str(dctys__tepa))
    else:
        mwuz__iod += '    udf_ncols = np.array([0], np.int32)\n'
    if sqbr__yrs:
        mwuz__iod += '    arr_type = coerce_to_array({})\n'.format(agg_node
            .pivot_values)
        mwuz__iod += '    arr_info = array_to_info(arr_type)\n'
        mwuz__iod += (
            '    dispatch_table = arr_info_list_to_table([arr_info])\n')
        mwuz__iod += '    pivot_info = array_to_info(pivot_arr)\n'
        mwuz__iod += (
            '    dispatch_info = arr_info_list_to_table([pivot_info])\n')
        mwuz__iod += (
            """    out_table = pivot_groupby_and_aggregate(table, {}, dispatch_table, dispatch_info, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, agg_node.
            is_crosstab, leov__lez, agg_node.return_key, agg_node.same_index))
        mwuz__iod += '    delete_info_decref_array(pivot_info)\n'
        mwuz__iod += '    delete_info_decref_array(arr_info)\n'
    else:
        mwuz__iod += (
            """    out_table = groupby_and_aggregate(table, {}, {}, ftypes.ctypes, func_offsets.ctypes, udf_ncols.ctypes, {}, {}, {}, {}, {}, {}, {}, {}, cpp_cb_update_addr, cpp_cb_combine_addr, cpp_cb_eval_addr, cpp_cb_general_addr, udf_table_dummy)
"""
            .format(n_keys, agg_node.input_has_index, parallel, leov__lez,
            hbv__fjovi, dhe__qdr, jmbw__gkbke, agg_node.return_key,
            agg_node.same_index, agg_node.dropna))
    qel__cxyu = 0
    if agg_node.return_key:
        for i, mdadm__syez in enumerate(obce__ggovo):
            mwuz__iod += (
                '    {} = info_to_array(info_from_table(out_table, {}), {})\n'
                .format(mdadm__syez, qel__cxyu, mdadm__syez))
            qel__cxyu += 1
    for cqks__cdkxj in dynws__mqo.values():
        mwuz__iod += (
            '    {} = info_to_array(info_from_table(out_table, {}), {})\n'.
            format(cqks__cdkxj, qel__cxyu, cqks__cdkxj + '_dummy'))
        qel__cxyu += 1
    if agg_node.same_index:
        mwuz__iod += (
            """    out_index_arg = info_to_array(info_from_table(out_table, {}), index_arg)
"""
            .format(qel__cxyu))
        qel__cxyu += 1
    mwuz__iod += (
        f"    ev_clean = bodo.utils.tracing.Event('tables_clean_up', {parallel})\n"
        )
    mwuz__iod += '    delete_table_decref_arrays(table)\n'
    mwuz__iod += '    delete_table_decref_arrays(udf_table_dummy)\n'
    mwuz__iod += '    delete_table(out_table)\n'
    mwuz__iod += f'    ev_clean.finalize()\n'
    nhzr__nfmm = tuple(dynws__mqo.values())
    if agg_node.return_key:
        nhzr__nfmm += tuple(obce__ggovo)
    mwuz__iod += '    return ({},{})\n'.format(', '.join(nhzr__nfmm), 
        ' out_index_arg,' if agg_node.same_index else '')
    fzjo__vohg = {}
    exec(mwuz__iod, {}, fzjo__vohg)
    hntu__oxaz = fzjo__vohg['agg_top']
    return hntu__oxaz


def compile_to_optimized_ir(func, arg_typs, typingctx, targetctx):
    code = func.code if hasattr(func, 'code') else func.__code__
    closure = func.closure if hasattr(func, 'closure') else func.__closure__
    f_ir = get_ir_of_code(func.__globals__, code)
    replace_closures(f_ir, closure, code)
    for block in f_ir.blocks.values():
        for aiw__kvf in block.body:
            if is_call_assign(aiw__kvf) and find_callname(f_ir, aiw__kvf.value
                ) == ('len', 'builtins') and aiw__kvf.value.args[0
                ].name == f_ir.arg_names[0]:
                agp__oua = get_definition(f_ir, aiw__kvf.value.func)
                agp__oua.name = 'dummy_agg_count'
                agp__oua.value = dummy_agg_count
    nab__kljd = get_name_var_table(f_ir.blocks)
    lhnkv__pkskc = {}
    for name, rzdp__boj in nab__kljd.items():
        lhnkv__pkskc[name] = mk_unique_var(name)
    replace_var_names(f_ir.blocks, lhnkv__pkskc)
    f_ir._definitions = build_definitions(f_ir.blocks)
    assert f_ir.arg_count == 1, 'agg function should have one input'
    nhabv__hdt = numba.core.compiler.Flags()
    nhabv__hdt.nrt = True
    ngza__ezrxw = bodo.transforms.untyped_pass.UntypedPass(f_ir, typingctx,
        arg_typs, {}, {}, nhabv__hdt)
    ngza__ezrxw.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    typemap, irs__diwyb, calltypes, rzdp__boj = (numba.core.typed_passes.
        type_inference_stage(typingctx, targetctx, f_ir, arg_typs, None))
    fcg__nskta = numba.core.cpu.ParallelOptions(True)
    targetctx = numba.core.cpu.CPUContext(typingctx)
    aegyd__jexv = namedtuple('DummyPipeline', ['typingctx', 'targetctx',
        'args', 'func_ir', 'typemap', 'return_type', 'calltypes',
        'type_annotation', 'locals', 'flags', 'pipeline'])
    gkkn__omo = namedtuple('TypeAnnotation', ['typemap', 'calltypes'])
    emyi__zlo = gkkn__omo(typemap, calltypes)
    pm = aegyd__jexv(typingctx, targetctx, None, f_ir, typemap, irs__diwyb,
        calltypes, emyi__zlo, {}, nhabv__hdt, None)
    nxsp__ful = numba.core.compiler.DefaultPassBuilder.define_untyped_pipeline(
        pm)
    pm = aegyd__jexv(typingctx, targetctx, None, f_ir, typemap, irs__diwyb,
        calltypes, emyi__zlo, {}, nhabv__hdt, nxsp__ful)
    kza__moazm = numba.core.typed_passes.InlineOverloads()
    kza__moazm.run_pass(pm)
    kpyt__bdkcr = bodo.transforms.series_pass.SeriesPass(f_ir, typingctx,
        targetctx, typemap, calltypes, {}, False)
    kpyt__bdkcr.run()
    for block in f_ir.blocks.values():
        for aiw__kvf in block.body:
            if is_assign(aiw__kvf) and isinstance(aiw__kvf.value, (ir.Arg,
                ir.Var)) and isinstance(typemap[aiw__kvf.target.name],
                SeriesType):
                jhm__smvfz = typemap.pop(aiw__kvf.target.name)
                typemap[aiw__kvf.target.name] = jhm__smvfz.data
            if is_call_assign(aiw__kvf) and find_callname(f_ir, aiw__kvf.value
                ) == ('get_series_data', 'bodo.hiframes.pd_series_ext'):
                f_ir._definitions[aiw__kvf.target.name].remove(aiw__kvf.value)
                aiw__kvf.value = aiw__kvf.value.args[0]
                f_ir._definitions[aiw__kvf.target.name].append(aiw__kvf.value)
            if is_call_assign(aiw__kvf) and find_callname(f_ir, aiw__kvf.value
                ) == ('isna', 'bodo.libs.array_kernels'):
                f_ir._definitions[aiw__kvf.target.name].remove(aiw__kvf.value)
                aiw__kvf.value = ir.Const(False, aiw__kvf.loc)
                f_ir._definitions[aiw__kvf.target.name].append(aiw__kvf.value)
            if is_call_assign(aiw__kvf) and find_callname(f_ir, aiw__kvf.value
                ) == ('setna', 'bodo.libs.array_kernels'):
                f_ir._definitions[aiw__kvf.target.name].remove(aiw__kvf.value)
                aiw__kvf.value = ir.Const(False, aiw__kvf.loc)
                f_ir._definitions[aiw__kvf.target.name].append(aiw__kvf.value)
    bodo.transforms.untyped_pass.remove_dead_branches(f_ir)
    oxlm__oxyuj = numba.parfors.parfor.PreParforPass(f_ir, typemap,
        calltypes, typingctx, targetctx, fcg__nskta)
    oxlm__oxyuj.run()
    f_ir._definitions = build_definitions(f_ir.blocks)
    kghmp__oogp = numba.core.compiler.StateDict()
    kghmp__oogp.func_ir = f_ir
    kghmp__oogp.typemap = typemap
    kghmp__oogp.calltypes = calltypes
    kghmp__oogp.typingctx = typingctx
    kghmp__oogp.targetctx = targetctx
    kghmp__oogp.return_type = irs__diwyb
    numba.core.rewrites.rewrite_registry.apply('after-inference', kghmp__oogp)
    ejio__bdo = numba.parfors.parfor.ParforPass(f_ir, typemap, calltypes,
        irs__diwyb, typingctx, targetctx, fcg__nskta, nhabv__hdt, {})
    ejio__bdo.run()
    remove_dels(f_ir.blocks)
    numba.parfors.parfor.maximize_fusion(f_ir, f_ir.blocks, typemap, False)
    return f_ir, pm


def replace_closures(f_ir, closure, code):
    if closure:
        closure = f_ir.get_definition(closure)
        if isinstance(closure, tuple):
            hkeaq__pwde = ctypes.pythonapi.PyCell_Get
            hkeaq__pwde.restype = ctypes.py_object
            hkeaq__pwde.argtypes = ctypes.py_object,
            vywh__mdhwf = tuple(hkeaq__pwde(qse__ggjft) for qse__ggjft in
                closure)
        else:
            assert isinstance(closure, ir.Expr) and closure.op == 'build_tuple'
            vywh__mdhwf = closure.items
        assert len(code.co_freevars) == len(vywh__mdhwf)
        numba.core.inline_closurecall._replace_freevars(f_ir.blocks,
            vywh__mdhwf)


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
        zou__xnzz = SeriesType(in_col_typ.dtype, in_col_typ, None, string_type)
        f_ir, pm = compile_to_optimized_ir(func, (zou__xnzz,), self.
            typingctx, self.targetctx)
        f_ir._definitions = build_definitions(f_ir.blocks)
        assert len(f_ir.blocks
            ) == 1 and 0 in f_ir.blocks, 'only simple functions with one block supported for aggregation'
        block = f_ir.blocks[0]
        grps__nlqho, arr_var = _rm_arg_agg_block(block, pm.typemap)
        xfio__mqkf = -1
        for i, aiw__kvf in enumerate(grps__nlqho):
            if isinstance(aiw__kvf, numba.parfors.parfor.Parfor):
                assert xfio__mqkf == -1, 'only one parfor for aggregation function'
                xfio__mqkf = i
        parfor = None
        if xfio__mqkf != -1:
            parfor = grps__nlqho[xfio__mqkf]
            remove_dels(parfor.loop_body)
            remove_dels({(0): parfor.init_block})
        init_nodes = []
        if parfor:
            init_nodes = grps__nlqho[:xfio__mqkf] + parfor.init_block.body
        eval_nodes = grps__nlqho[xfio__mqkf + 1:]
        redvars = []
        var_to_redvar = {}
        if parfor:
            redvars, var_to_redvar = get_parfor_reductions(parfor, parfor.
                params, pm.calltypes)
        func.ncols_pre_shuffle = len(redvars)
        func.ncols_post_shuffle = len(redvars) + 1
        func.n_redvars = len(redvars)
        reduce_vars = [0] * len(redvars)
        for aiw__kvf in init_nodes:
            if is_assign(aiw__kvf) and aiw__kvf.target.name in redvars:
                ind = redvars.index(aiw__kvf.target.name)
                reduce_vars[ind] = aiw__kvf.target
        var_types = [pm.typemap[v] for v in redvars]
        rij__mlfa = gen_combine_func(f_ir, parfor, redvars, var_to_redvar,
            var_types, arr_var, pm, self.typingctx, self.targetctx)
        init_nodes = _mv_read_only_init_vars(init_nodes, parfor, eval_nodes)
        nrfv__ksz = gen_update_func(parfor, redvars, var_to_redvar,
            var_types, arr_var, in_col_typ, pm, self.typingctx, self.targetctx)
        zhulp__licrz = gen_eval_func(f_ir, eval_nodes, reduce_vars,
            var_types, pm, self.typingctx, self.targetctx)
        self.all_reduce_vars += reduce_vars
        self.all_vartypes += var_types
        self.all_init_nodes += init_nodes
        self.all_eval_funcs.append(zhulp__licrz)
        self.all_update_funcs.append(nrfv__ksz)
        self.all_combine_funcs.append(rij__mlfa)
        self.curr_offset += len(redvars)
        self.redvar_offsets.append(self.curr_offset)

    def gen_all_func(self):
        if len(self.all_update_funcs) == 0:
            return None
        self.all_vartypes = self.all_vartypes * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_vartypes
        self.all_reduce_vars = self.all_reduce_vars * len(self.pivot_values
            ) if self.pivot_values is not None else self.all_reduce_vars
        qbrtt__icfp = gen_init_func(self.all_init_nodes, self.
            all_reduce_vars, self.all_vartypes, self.typingctx, self.targetctx)
        chkk__zxmi = gen_all_update_func(self.all_update_funcs, self.
            all_vartypes, self.in_col_types, self.redvar_offsets, self.
            typingctx, self.targetctx, self.pivot_typ, self.pivot_values,
            self.is_crosstab)
        rup__dwlr = gen_all_combine_func(self.all_combine_funcs, self.
            all_vartypes, self.redvar_offsets, self.typingctx, self.
            targetctx, self.pivot_typ, self.pivot_values)
        aajv__tkeqs = gen_all_eval_func(self.all_eval_funcs, self.
            all_vartypes, self.redvar_offsets, self.out_col_types, self.
            typingctx, self.targetctx, self.pivot_values)
        return (self.all_vartypes, qbrtt__icfp, chkk__zxmi, rup__dwlr,
            aajv__tkeqs)


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
    uchox__gjji = []
    for t, rapz__bqnl in zip(in_col_types, agg_func):
        uchox__gjji.append((t, rapz__bqnl))
    yomv__xxlky = RegularUDFGenerator(in_col_types, out_col_types,
        pivot_typ, pivot_values, is_crosstab, typingctx, targetctx)
    jgybj__soulv = GeneralUDFGenerator()
    for in_col_typ, func in uchox__gjji:
        if func.ftype not in ('udf', 'gen_udf'):
            continue
        try:
            yomv__xxlky.add_udf(in_col_typ, func)
        except:
            jgybj__soulv.add_udf(func)
            func.ftype = 'gen_udf'
    regular_udf_funcs = yomv__xxlky.gen_all_func()
    general_udf_funcs = jgybj__soulv.gen_all_func()
    if regular_udf_funcs is not None or general_udf_funcs is not None:
        return AggUDFStruct(regular_udf_funcs, general_udf_funcs)
    else:
        return None


def _mv_read_only_init_vars(init_nodes, parfor, eval_nodes):
    if not parfor:
        return init_nodes
    kpfs__boapv = compute_use_defs(parfor.loop_body)
    vlbxo__vkr = set()
    for ljou__pku in kpfs__boapv.usemap.values():
        vlbxo__vkr |= ljou__pku
    gsfe__qja = set()
    for ljou__pku in kpfs__boapv.defmap.values():
        gsfe__qja |= ljou__pku
    faqzn__ifwc = ir.Block(ir.Scope(None, parfor.loc), parfor.loc)
    faqzn__ifwc.body = eval_nodes
    rue__tex = compute_use_defs({(0): faqzn__ifwc})
    tcz__tppc = rue__tex.usemap[0]
    qgi__njaav = set()
    kczwd__vviw = []
    qpznv__kvotr = []
    for aiw__kvf in reversed(init_nodes):
        ztsh__xysbk = {v.name for v in aiw__kvf.list_vars()}
        if is_assign(aiw__kvf):
            v = aiw__kvf.target.name
            ztsh__xysbk.remove(v)
            if (v in vlbxo__vkr and v not in qgi__njaav and v not in
                tcz__tppc and v not in gsfe__qja):
                qpznv__kvotr.append(aiw__kvf)
                vlbxo__vkr |= ztsh__xysbk
                gsfe__qja.add(v)
                continue
        qgi__njaav |= ztsh__xysbk
        kczwd__vviw.append(aiw__kvf)
    qpznv__kvotr.reverse()
    kczwd__vviw.reverse()
    louh__uvtm = min(parfor.loop_body.keys())
    gjdcu__itr = parfor.loop_body[louh__uvtm]
    gjdcu__itr.body = qpznv__kvotr + gjdcu__itr.body
    return kczwd__vviw


def gen_init_func(init_nodes, reduce_vars, var_types, typingctx, targetctx):
    gxd__amolo = (numba.parfors.parfor.max_checker, numba.parfors.parfor.
        min_checker, numba.parfors.parfor.argmax_checker, numba.parfors.
        parfor.argmin_checker)
    owyuj__eac = set()
    obo__qbgh = []
    for aiw__kvf in init_nodes:
        if is_assign(aiw__kvf) and isinstance(aiw__kvf.value, ir.Global
            ) and isinstance(aiw__kvf.value.value, pytypes.FunctionType
            ) and aiw__kvf.value.value in gxd__amolo:
            owyuj__eac.add(aiw__kvf.target.name)
        elif is_call_assign(aiw__kvf
            ) and aiw__kvf.value.func.name in owyuj__eac:
            pass
        else:
            obo__qbgh.append(aiw__kvf)
    init_nodes = obo__qbgh
    hzng__mcn = types.Tuple(var_types)
    igskm__bmyz = lambda : None
    f_ir = compile_to_numba_ir(igskm__bmyz, {})
    block = list(f_ir.blocks.values())[0]
    loc = block.loc
    cxe__gvbl = ir.Var(block.scope, mk_unique_var('init_tup'), loc)
    yym__gfrnz = ir.Assign(ir.Expr.build_tuple(reduce_vars, loc), cxe__gvbl,
        loc)
    block.body = block.body[-2:]
    block.body = init_nodes + [yym__gfrnz] + block.body
    block.body[-2].value.value = cxe__gvbl
    wkkrs__imiq = compiler.compile_ir(typingctx, targetctx, f_ir, (),
        hzng__mcn, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    erjz__pmk = numba.core.target_extension.dispatcher_registry[cpu_target](
        igskm__bmyz)
    erjz__pmk.add_overload(wkkrs__imiq)
    return erjz__pmk


def gen_all_update_func(update_funcs, reduce_var_types, in_col_types,
    redvar_offsets, typingctx, targetctx, pivot_typ, pivot_values, is_crosstab
    ):
    gyb__bfrb = len(update_funcs)
    pmxmi__fcq = len(in_col_types)
    if pivot_values is not None:
        assert pmxmi__fcq == 1
    mwuz__iod = (
        'def update_all_f(redvar_arrs, data_in, w_ind, i, pivot_arr):\n')
    if pivot_values is not None:
        gsyx__udms = redvar_offsets[pmxmi__fcq]
        mwuz__iod += '  pv = pivot_arr[i]\n'
        for cvqf__wjesb, suew__ihg in enumerate(pivot_values):
            xexpw__tne = 'el' if cvqf__wjesb != 0 else ''
            mwuz__iod += "  {}if pv == '{}':\n".format(xexpw__tne, suew__ihg)
            sjvut__eutj = gsyx__udms * cvqf__wjesb
            rfso__iyit = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for
                i in range(sjvut__eutj + redvar_offsets[0], sjvut__eutj +
                redvar_offsets[1])])
            iinr__iwdto = 'data_in[0][i]'
            if is_crosstab:
                iinr__iwdto = '0'
            mwuz__iod += '    {} = update_vars_0({}, {})\n'.format(rfso__iyit,
                rfso__iyit, iinr__iwdto)
    else:
        for cvqf__wjesb in range(gyb__bfrb):
            rfso__iyit = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for
                i in range(redvar_offsets[cvqf__wjesb], redvar_offsets[
                cvqf__wjesb + 1])])
            if rfso__iyit:
                mwuz__iod += ('  {} = update_vars_{}({},  data_in[{}][i])\n'
                    .format(rfso__iyit, cvqf__wjesb, rfso__iyit, 0 if 
                    pmxmi__fcq == 1 else cvqf__wjesb))
    mwuz__iod += '  return\n'
    trsgu__req = {}
    for i, rapz__bqnl in enumerate(update_funcs):
        trsgu__req['update_vars_{}'.format(i)] = rapz__bqnl
    fzjo__vohg = {}
    exec(mwuz__iod, trsgu__req, fzjo__vohg)
    tuwq__sasxx = fzjo__vohg['update_all_f']
    return numba.njit(no_cpython_wrapper=True)(tuwq__sasxx)


def gen_all_combine_func(combine_funcs, reduce_var_types, redvar_offsets,
    typingctx, targetctx, pivot_typ, pivot_values):
    ksasv__gkteq = types.Tuple([types.Array(t, 1, 'C') for t in
        reduce_var_types])
    arg_typs = ksasv__gkteq, ksasv__gkteq, types.intp, types.intp, pivot_typ
    llp__hiws = len(redvar_offsets) - 1
    gsyx__udms = redvar_offsets[llp__hiws]
    mwuz__iod = (
        'def combine_all_f(redvar_arrs, recv_arrs, w_ind, i, pivot_arr):\n')
    if pivot_values is not None:
        assert llp__hiws == 1
        for ckf__vap in range(len(pivot_values)):
            sjvut__eutj = gsyx__udms * ckf__vap
            rfso__iyit = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for
                i in range(sjvut__eutj + redvar_offsets[0], sjvut__eutj +
                redvar_offsets[1])])
            rzs__xen = ', '.join(['recv_arrs[{}][i]'.format(i) for i in
                range(sjvut__eutj + redvar_offsets[0], sjvut__eutj +
                redvar_offsets[1])])
            mwuz__iod += '  {} = combine_vars_0({}, {})\n'.format(rfso__iyit,
                rfso__iyit, rzs__xen)
    else:
        for cvqf__wjesb in range(llp__hiws):
            rfso__iyit = ', '.join(['redvar_arrs[{}][w_ind]'.format(i) for
                i in range(redvar_offsets[cvqf__wjesb], redvar_offsets[
                cvqf__wjesb + 1])])
            rzs__xen = ', '.join(['recv_arrs[{}][i]'.format(i) for i in
                range(redvar_offsets[cvqf__wjesb], redvar_offsets[
                cvqf__wjesb + 1])])
            if rzs__xen:
                mwuz__iod += '  {} = combine_vars_{}({}, {})\n'.format(
                    rfso__iyit, cvqf__wjesb, rfso__iyit, rzs__xen)
    mwuz__iod += '  return\n'
    trsgu__req = {}
    for i, rapz__bqnl in enumerate(combine_funcs):
        trsgu__req['combine_vars_{}'.format(i)] = rapz__bqnl
    fzjo__vohg = {}
    exec(mwuz__iod, trsgu__req, fzjo__vohg)
    yhy__anle = fzjo__vohg['combine_all_f']
    f_ir = compile_to_numba_ir(yhy__anle, trsgu__req)
    rup__dwlr = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        types.none, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    erjz__pmk = numba.core.target_extension.dispatcher_registry[cpu_target](
        yhy__anle)
    erjz__pmk.add_overload(rup__dwlr)
    return erjz__pmk


def gen_all_eval_func(eval_funcs, reduce_var_types, redvar_offsets,
    out_col_typs, typingctx, targetctx, pivot_values):
    ksasv__gkteq = types.Tuple([types.Array(t, 1, 'C') for t in
        reduce_var_types])
    out_col_typs = types.Tuple(out_col_typs)
    llp__hiws = len(redvar_offsets) - 1
    gsyx__udms = redvar_offsets[llp__hiws]
    mwuz__iod = 'def eval_all_f(redvar_arrs, out_arrs, j):\n'
    if pivot_values is not None:
        assert llp__hiws == 1
        for cvqf__wjesb in range(len(pivot_values)):
            sjvut__eutj = gsyx__udms * cvqf__wjesb
            rfso__iyit = ', '.join(['redvar_arrs[{}][j]'.format(i) for i in
                range(sjvut__eutj + redvar_offsets[0], sjvut__eutj +
                redvar_offsets[1])])
            mwuz__iod += '  out_arrs[{}][j] = eval_vars_0({})\n'.format(
                cvqf__wjesb, rfso__iyit)
    else:
        for cvqf__wjesb in range(llp__hiws):
            rfso__iyit = ', '.join(['redvar_arrs[{}][j]'.format(i) for i in
                range(redvar_offsets[cvqf__wjesb], redvar_offsets[
                cvqf__wjesb + 1])])
            mwuz__iod += '  out_arrs[{}][j] = eval_vars_{}({})\n'.format(
                cvqf__wjesb, cvqf__wjesb, rfso__iyit)
    mwuz__iod += '  return\n'
    trsgu__req = {}
    for i, rapz__bqnl in enumerate(eval_funcs):
        trsgu__req['eval_vars_{}'.format(i)] = rapz__bqnl
    fzjo__vohg = {}
    exec(mwuz__iod, trsgu__req, fzjo__vohg)
    rcbnn__rqlbz = fzjo__vohg['eval_all_f']
    return numba.njit(no_cpython_wrapper=True)(rcbnn__rqlbz)


def gen_eval_func(f_ir, eval_nodes, reduce_vars, var_types, pm, typingctx,
    targetctx):
    qie__zoa = len(var_types)
    vef__fml = [f'in{i}' for i in range(qie__zoa)]
    hzng__mcn = types.unliteral(pm.typemap[eval_nodes[-1].value.name])
    gawlj__coq = hzng__mcn(0)
    mwuz__iod = 'def agg_eval({}):\n return _zero\n'.format(', '.join(vef__fml)
        )
    fzjo__vohg = {}
    exec(mwuz__iod, {'_zero': gawlj__coq}, fzjo__vohg)
    fqqwk__otdnr = fzjo__vohg['agg_eval']
    arg_typs = tuple(var_types)
    f_ir = compile_to_numba_ir(fqqwk__otdnr, {'numba': numba, 'bodo': bodo,
        'np': np, '_zero': gawlj__coq}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.
        calltypes)
    block = list(f_ir.blocks.values())[0]
    tqgms__sukkc = []
    for i, v in enumerate(reduce_vars):
        tqgms__sukkc.append(ir.Assign(block.body[i].target, v, v.loc))
        for haomr__gkok in v.versioned_names:
            tqgms__sukkc.append(ir.Assign(v, ir.Var(v.scope, haomr__gkok, v
                .loc), v.loc))
    block.body = block.body[:qie__zoa] + tqgms__sukkc + eval_nodes
    zhulp__licrz = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        hzng__mcn, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    erjz__pmk = numba.core.target_extension.dispatcher_registry[cpu_target](
        fqqwk__otdnr)
    erjz__pmk.add_overload(zhulp__licrz)
    return erjz__pmk


def gen_combine_func(f_ir, parfor, redvars, var_to_redvar, var_types,
    arr_var, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda : ())
    qie__zoa = len(redvars)
    gpri__wvst = [f'v{i}' for i in range(qie__zoa)]
    vef__fml = [f'in{i}' for i in range(qie__zoa)]
    mwuz__iod = 'def agg_combine({}):\n'.format(', '.join(gpri__wvst +
        vef__fml))
    dyef__auqu = wrap_parfor_blocks(parfor)
    jtj__bgjzx = find_topo_order(dyef__auqu)
    jtj__bgjzx = jtj__bgjzx[1:]
    unwrap_parfor_blocks(parfor)
    uoy__gktuu = {}
    ynu__lhn = []
    for pxxb__vlv in jtj__bgjzx:
        qlom__cnmf = parfor.loop_body[pxxb__vlv]
        for aiw__kvf in qlom__cnmf.body:
            if is_call_assign(aiw__kvf) and guard(find_callname, f_ir,
                aiw__kvf.value) == ('__special_combine', 'bodo.ir.aggregate'):
                args = aiw__kvf.value.args
                fmd__hacp = []
                vytkh__ecnza = []
                for v in args[:-1]:
                    ind = redvars.index(v.name)
                    ynu__lhn.append(ind)
                    fmd__hacp.append('v{}'.format(ind))
                    vytkh__ecnza.append('in{}'.format(ind))
                coknn__mkq = '__special_combine__{}'.format(len(uoy__gktuu))
                mwuz__iod += '    ({},) = {}({})\n'.format(', '.join(
                    fmd__hacp), coknn__mkq, ', '.join(fmd__hacp + vytkh__ecnza)
                    )
                nrbt__spu = ir.Expr.call(args[-1], [], (), qlom__cnmf.loc)
                ufiaq__upe = guard(find_callname, f_ir, nrbt__spu)
                assert ufiaq__upe == ('_var_combine', 'bodo.ir.aggregate')
                ufiaq__upe = bodo.ir.aggregate._var_combine
                uoy__gktuu[coknn__mkq] = ufiaq__upe
            if is_assign(aiw__kvf) and aiw__kvf.target.name in redvars:
                jzpm__ofxzr = aiw__kvf.target.name
                ind = redvars.index(jzpm__ofxzr)
                if ind in ynu__lhn:
                    continue
                if len(f_ir._definitions[jzpm__ofxzr]) == 2:
                    var_def = f_ir._definitions[jzpm__ofxzr][0]
                    mwuz__iod += _match_reduce_def(var_def, f_ir, ind)
                    var_def = f_ir._definitions[jzpm__ofxzr][1]
                    mwuz__iod += _match_reduce_def(var_def, f_ir, ind)
    mwuz__iod += '    return {}'.format(', '.join(['v{}'.format(i) for i in
        range(qie__zoa)]))
    fzjo__vohg = {}
    exec(mwuz__iod, {}, fzjo__vohg)
    mofit__dhmq = fzjo__vohg['agg_combine']
    arg_typs = tuple(2 * var_types)
    trsgu__req = {'numba': numba, 'bodo': bodo, 'np': np}
    trsgu__req.update(uoy__gktuu)
    f_ir = compile_to_numba_ir(mofit__dhmq, trsgu__req, typingctx=typingctx,
        targetctx=targetctx, arg_typs=arg_typs, typemap=pm.typemap,
        calltypes=pm.calltypes)
    block = list(f_ir.blocks.values())[0]
    hzng__mcn = pm.typemap[block.body[-1].value.name]
    rij__mlfa = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        hzng__mcn, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    erjz__pmk = numba.core.target_extension.dispatcher_registry[cpu_target](
        mofit__dhmq)
    erjz__pmk.add_overload(rij__mlfa)
    return erjz__pmk


def _match_reduce_def(var_def, f_ir, ind):
    mwuz__iod = ''
    while isinstance(var_def, ir.Var):
        var_def = guard(get_definition, f_ir, var_def)
    if isinstance(var_def, ir.Expr
        ) and var_def.op == 'inplace_binop' and var_def.fn in ('+=',
        operator.iadd):
        mwuz__iod = '    v{} += in{}\n'.format(ind, ind)
    if isinstance(var_def, ir.Expr) and var_def.op == 'call':
        fikb__mpswh = guard(find_callname, f_ir, var_def)
        if fikb__mpswh == ('min', 'builtins'):
            mwuz__iod = '    v{} = min(v{}, in{})\n'.format(ind, ind, ind)
        if fikb__mpswh == ('max', 'builtins'):
            mwuz__iod = '    v{} = max(v{}, in{})\n'.format(ind, ind, ind)
    return mwuz__iod


def gen_update_func(parfor, redvars, var_to_redvar, var_types, arr_var,
    in_col_typ, pm, typingctx, targetctx):
    if not parfor:
        return numba.njit(lambda A: ())
    qie__zoa = len(redvars)
    reza__asqk = 1
    foq__cfu = []
    for i in range(reza__asqk):
        bui__xyrtw = ir.Var(arr_var.scope, f'$input{i}', arr_var.loc)
        foq__cfu.append(bui__xyrtw)
    fkrs__kzsb = parfor.loop_nests[0].index_variable
    txtzx__hehcz = [0] * qie__zoa
    for qlom__cnmf in parfor.loop_body.values():
        qurp__savw = []
        for aiw__kvf in qlom__cnmf.body:
            if is_var_assign(aiw__kvf
                ) and aiw__kvf.value.name == fkrs__kzsb.name:
                continue
            if is_getitem(aiw__kvf
                ) and aiw__kvf.value.value.name == arr_var.name:
                aiw__kvf.value = foq__cfu[0]
            if is_call_assign(aiw__kvf) and guard(find_callname, pm.func_ir,
                aiw__kvf.value) == ('isna', 'bodo.libs.array_kernels'
                ) and aiw__kvf.value.args[0].name == arr_var.name:
                aiw__kvf.value = ir.Const(False, aiw__kvf.target.loc)
            if is_assign(aiw__kvf) and aiw__kvf.target.name in redvars:
                ind = redvars.index(aiw__kvf.target.name)
                txtzx__hehcz[ind] = aiw__kvf.target
            qurp__savw.append(aiw__kvf)
        qlom__cnmf.body = qurp__savw
    gpri__wvst = ['v{}'.format(i) for i in range(qie__zoa)]
    vef__fml = ['in{}'.format(i) for i in range(reza__asqk)]
    mwuz__iod = 'def agg_update({}):\n'.format(', '.join(gpri__wvst + vef__fml)
        )
    mwuz__iod += '    __update_redvars()\n'
    mwuz__iod += '    return {}'.format(', '.join(['v{}'.format(i) for i in
        range(qie__zoa)]))
    fzjo__vohg = {}
    exec(mwuz__iod, {}, fzjo__vohg)
    chn__zfokb = fzjo__vohg['agg_update']
    arg_typs = tuple(var_types + [in_col_typ.dtype] * reza__asqk)
    f_ir = compile_to_numba_ir(chn__zfokb, {'__update_redvars':
        __update_redvars}, typingctx=typingctx, targetctx=targetctx,
        arg_typs=arg_typs, typemap=pm.typemap, calltypes=pm.calltypes)
    f_ir._definitions = build_definitions(f_ir.blocks)
    fhjo__nrz = f_ir.blocks.popitem()[1].body
    hzng__mcn = pm.typemap[fhjo__nrz[-1].value.name]
    dyef__auqu = wrap_parfor_blocks(parfor)
    jtj__bgjzx = find_topo_order(dyef__auqu)
    jtj__bgjzx = jtj__bgjzx[1:]
    unwrap_parfor_blocks(parfor)
    f_ir.blocks = parfor.loop_body
    gjdcu__itr = f_ir.blocks[jtj__bgjzx[0]]
    idlok__kdlj = f_ir.blocks[jtj__bgjzx[-1]]
    vabb__bweyo = fhjo__nrz[:qie__zoa + reza__asqk]
    if qie__zoa > 1:
        nbpxc__xxjt = fhjo__nrz[-3:]
        assert is_assign(nbpxc__xxjt[0]) and isinstance(nbpxc__xxjt[0].
            value, ir.Expr) and nbpxc__xxjt[0].value.op == 'build_tuple'
    else:
        nbpxc__xxjt = fhjo__nrz[-2:]
    for i in range(qie__zoa):
        rvgu__gtyk = fhjo__nrz[i].target
        hikg__kecv = ir.Assign(rvgu__gtyk, txtzx__hehcz[i], rvgu__gtyk.loc)
        vabb__bweyo.append(hikg__kecv)
    for i in range(qie__zoa, qie__zoa + reza__asqk):
        rvgu__gtyk = fhjo__nrz[i].target
        hikg__kecv = ir.Assign(rvgu__gtyk, foq__cfu[i - qie__zoa],
            rvgu__gtyk.loc)
        vabb__bweyo.append(hikg__kecv)
    gjdcu__itr.body = vabb__bweyo + gjdcu__itr.body
    aiesi__ntbe = []
    for i in range(qie__zoa):
        rvgu__gtyk = fhjo__nrz[i].target
        hikg__kecv = ir.Assign(txtzx__hehcz[i], rvgu__gtyk, rvgu__gtyk.loc)
        aiesi__ntbe.append(hikg__kecv)
    idlok__kdlj.body += aiesi__ntbe + nbpxc__xxjt
    lgfm__dilp = compiler.compile_ir(typingctx, targetctx, f_ir, arg_typs,
        hzng__mcn, compiler.DEFAULT_FLAGS, {})
    from numba.core.target_extension import cpu_target
    erjz__pmk = numba.core.target_extension.dispatcher_registry[cpu_target](
        chn__zfokb)
    erjz__pmk.add_overload(lgfm__dilp)
    return erjz__pmk


def _rm_arg_agg_block(block, typemap):
    grps__nlqho = []
    arr_var = None
    for i, aiw__kvf in enumerate(block.body):
        if is_assign(aiw__kvf) and isinstance(aiw__kvf.value, ir.Arg):
            arr_var = aiw__kvf.target
            udwmu__bnh = typemap[arr_var.name]
            if not isinstance(udwmu__bnh, types.ArrayCompatible):
                grps__nlqho += block.body[i + 1:]
                break
            ycspv__mbxtg = block.body[i + 1]
            assert is_assign(ycspv__mbxtg) and isinstance(ycspv__mbxtg.
                value, ir.Expr
                ) and ycspv__mbxtg.value.op == 'getattr' and ycspv__mbxtg.value.attr == 'shape' and ycspv__mbxtg.value.value.name == arr_var.name
            ucn__ahdk = ycspv__mbxtg.target
            sjb__prs = block.body[i + 2]
            assert is_assign(sjb__prs) and isinstance(sjb__prs.value, ir.Expr
                ) and sjb__prs.value.op == 'static_getitem' and sjb__prs.value.value.name == ucn__ahdk.name
            grps__nlqho += block.body[i + 3:]
            break
        grps__nlqho.append(aiw__kvf)
    return grps__nlqho, arr_var


def get_parfor_reductions(parfor, parfor_params, calltypes, reduce_varnames
    =None, param_uses=None, var_to_param=None):
    if reduce_varnames is None:
        reduce_varnames = []
    if param_uses is None:
        param_uses = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}
    dyef__auqu = wrap_parfor_blocks(parfor)
    jtj__bgjzx = find_topo_order(dyef__auqu)
    jtj__bgjzx = jtj__bgjzx[1:]
    unwrap_parfor_blocks(parfor)
    for pxxb__vlv in reversed(jtj__bgjzx):
        for aiw__kvf in reversed(parfor.loop_body[pxxb__vlv].body):
            if isinstance(aiw__kvf, ir.Assign) and (aiw__kvf.target.name in
                parfor_params or aiw__kvf.target.name in var_to_param):
                ing__bpn = aiw__kvf.target.name
                rhs = aiw__kvf.value
                csoes__pbjo = (ing__bpn if ing__bpn in parfor_params else
                    var_to_param[ing__bpn])
                plufl__alue = []
                if isinstance(rhs, ir.Var):
                    plufl__alue = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    plufl__alue = [v.name for v in aiw__kvf.value.list_vars()]
                param_uses[csoes__pbjo].extend(plufl__alue)
                for v in plufl__alue:
                    var_to_param[v] = csoes__pbjo
            if isinstance(aiw__kvf, Parfor):
                get_parfor_reductions(aiw__kvf, parfor_params, calltypes,
                    reduce_varnames, param_uses, var_to_param)
    for kwi__bqi, plufl__alue in param_uses.items():
        if kwi__bqi in plufl__alue and kwi__bqi not in reduce_varnames:
            reduce_varnames.append(kwi__bqi)
    return reduce_varnames, var_to_param


@numba.extending.register_jitable
def dummy_agg_count(A):
    return len(A)
