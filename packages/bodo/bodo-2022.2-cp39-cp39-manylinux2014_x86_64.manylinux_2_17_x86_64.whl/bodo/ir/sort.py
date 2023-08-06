"""IR node for the data sorting"""
from collections import defaultdict
import numba
import numpy as np
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, mk_unique_var, replace_arg_nodes, replace_vars_inner, visit_vars_inner
import bodo
import bodo.libs.timsort
from bodo.libs.array import arr_info_list_to_table, array_to_info, delete_table, delete_table_decref_arrays, info_from_table, info_to_array, sort_values_table
from bodo.libs.str_arr_ext import cp_str_list_to_array, to_list_if_immutable_arr
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.utils.utils import debug_prints, gen_getitem
MIN_SAMPLES = 1000000
samplePointsPerPartitionHint = 20
MPI_ROOT = 0


class Sort(ir.Stmt):

    def __init__(self, df_in, df_out, key_arrs, out_key_arrs, df_in_vars,
        df_out_vars, inplace, loc, ascending_list=True, na_position='last'):
        self.df_in = df_in
        self.df_out = df_out
        self.key_arrs = key_arrs
        self.out_key_arrs = out_key_arrs
        self.df_in_vars = df_in_vars
        self.df_out_vars = df_out_vars
        self.inplace = inplace
        if isinstance(na_position, str):
            if na_position == 'last':
                self.na_position_b = (True,) * len(key_arrs)
            else:
                self.na_position_b = (False,) * len(key_arrs)
        else:
            self.na_position_b = tuple([(True if wbgfn__lmaos == 'last' else
                False) for wbgfn__lmaos in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_arrs)
        self.ascending_list = ascending_list
        self.loc = loc

    def __repr__(self):
        qijqi__jotq = ''
        for zngs__qrryq, ytuv__rtbtf in self.df_in_vars.items():
            qijqi__jotq += "'{}':{}, ".format(zngs__qrryq, ytuv__rtbtf.name)
        lmcfx__mift = '{}{{{}}}'.format(self.df_in, qijqi__jotq)
        cggou__rvsqq = ''
        for zngs__qrryq, ytuv__rtbtf in self.df_out_vars.items():
            cggou__rvsqq += "'{}':{}, ".format(zngs__qrryq, ytuv__rtbtf.name)
        lgg__too = '{}{{{}}}'.format(self.df_out, cggou__rvsqq)
        return 'sort: [key: {}] {} [key: {}] {}'.format(', '.join(
            ytuv__rtbtf.name for ytuv__rtbtf in self.key_arrs), lmcfx__mift,
            ', '.join(ytuv__rtbtf.name for ytuv__rtbtf in self.out_key_arrs
            ), lgg__too)


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    cgto__faud = []
    sdkk__wuax = sort_node.key_arrs + list(sort_node.df_in_vars.values())
    for fpioh__iihl in sdkk__wuax:
        sjjlw__ijqv = equiv_set.get_shape(fpioh__iihl)
        if sjjlw__ijqv is not None:
            cgto__faud.append(sjjlw__ijqv[0])
    if len(cgto__faud) > 1:
        equiv_set.insert_equiv(*cgto__faud)
    kod__afuq = []
    cgto__faud = []
    qekjy__oiolz = sort_node.out_key_arrs + list(sort_node.df_out_vars.values()
        )
    for fpioh__iihl in qekjy__oiolz:
        chc__rqfb = typemap[fpioh__iihl.name]
        aeflp__cvw = array_analysis._gen_shape_call(equiv_set, fpioh__iihl,
            chc__rqfb.ndim, None, kod__afuq)
        equiv_set.insert_equiv(fpioh__iihl, aeflp__cvw)
        cgto__faud.append(aeflp__cvw[0])
        equiv_set.define(fpioh__iihl, set())
    if len(cgto__faud) > 1:
        equiv_set.insert_equiv(*cgto__faud)
    return [], kod__afuq


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    sdkk__wuax = sort_node.key_arrs + list(sort_node.df_in_vars.values())
    lxu__ljv = sort_node.out_key_arrs + list(sort_node.df_out_vars.values())
    str__btbkd = Distribution.OneD
    for fpioh__iihl in sdkk__wuax:
        str__btbkd = Distribution(min(str__btbkd.value, array_dists[
            fpioh__iihl.name].value))
    ubnfb__yqljg = Distribution(min(str__btbkd.value, Distribution.OneD_Var
        .value))
    for fpioh__iihl in lxu__ljv:
        if fpioh__iihl.name in array_dists:
            ubnfb__yqljg = Distribution(min(ubnfb__yqljg.value, array_dists
                [fpioh__iihl.name].value))
    if ubnfb__yqljg != Distribution.OneD_Var:
        str__btbkd = ubnfb__yqljg
    for fpioh__iihl in sdkk__wuax:
        array_dists[fpioh__iihl.name] = str__btbkd
    for fpioh__iihl in lxu__ljv:
        array_dists[fpioh__iihl.name] = ubnfb__yqljg
    return


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for epxf__foc, iodp__vjzdl in zip(sort_node.key_arrs, sort_node.
        out_key_arrs):
        typeinferer.constraints.append(typeinfer.Propagate(dst=iodp__vjzdl.
            name, src=epxf__foc.name, loc=sort_node.loc))
    for zjgar__jgqgb, fpioh__iihl in sort_node.df_in_vars.items():
        naz__clk = sort_node.df_out_vars[zjgar__jgqgb]
        typeinferer.constraints.append(typeinfer.Propagate(dst=naz__clk.
            name, src=fpioh__iihl.name, loc=sort_node.loc))
    return


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for fpioh__iihl in (sort_node.out_key_arrs + list(sort_node.
            df_out_vars.values())):
            definitions[fpioh__iihl.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    if debug_prints():
        print('visiting sort vars for:', sort_node)
        print('cbdata: ', sorted(cbdata.items()))
    for clks__dxscq in range(len(sort_node.key_arrs)):
        sort_node.key_arrs[clks__dxscq] = visit_vars_inner(sort_node.
            key_arrs[clks__dxscq], callback, cbdata)
        sort_node.out_key_arrs[clks__dxscq] = visit_vars_inner(sort_node.
            out_key_arrs[clks__dxscq], callback, cbdata)
    for zjgar__jgqgb in list(sort_node.df_in_vars.keys()):
        sort_node.df_in_vars[zjgar__jgqgb] = visit_vars_inner(sort_node.
            df_in_vars[zjgar__jgqgb], callback, cbdata)
    for zjgar__jgqgb in list(sort_node.df_out_vars.keys()):
        sort_node.df_out_vars[zjgar__jgqgb] = visit_vars_inner(sort_node.
            df_out_vars[zjgar__jgqgb], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    oph__msn = []
    for zjgar__jgqgb, fpioh__iihl in sort_node.df_out_vars.items():
        if fpioh__iihl.name not in lives:
            oph__msn.append(zjgar__jgqgb)
    for sfun__suj in oph__msn:
        sort_node.df_in_vars.pop(sfun__suj)
        sort_node.df_out_vars.pop(sfun__suj)
    if len(sort_node.df_out_vars) == 0 and all(ytuv__rtbtf.name not in
        lives for ytuv__rtbtf in sort_node.out_key_arrs):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({ytuv__rtbtf.name for ytuv__rtbtf in sort_node.key_arrs})
    use_set.update({ytuv__rtbtf.name for ytuv__rtbtf in sort_node.
        df_in_vars.values()})
    if not sort_node.inplace:
        def_set.update({ytuv__rtbtf.name for ytuv__rtbtf in sort_node.
            out_key_arrs})
        def_set.update({ytuv__rtbtf.name for ytuv__rtbtf in sort_node.
            df_out_vars.values()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    ogu__luoa = set()
    if not sort_node.inplace:
        ogu__luoa = set(ytuv__rtbtf.name for ytuv__rtbtf in sort_node.
            df_out_vars.values())
        ogu__luoa.update({ytuv__rtbtf.name for ytuv__rtbtf in sort_node.
            out_key_arrs})
    return set(), ogu__luoa


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for clks__dxscq in range(len(sort_node.key_arrs)):
        sort_node.key_arrs[clks__dxscq] = replace_vars_inner(sort_node.
            key_arrs[clks__dxscq], var_dict)
        sort_node.out_key_arrs[clks__dxscq] = replace_vars_inner(sort_node.
            out_key_arrs[clks__dxscq], var_dict)
    for zjgar__jgqgb in list(sort_node.df_in_vars.keys()):
        sort_node.df_in_vars[zjgar__jgqgb] = replace_vars_inner(sort_node.
            df_in_vars[zjgar__jgqgb], var_dict)
    for zjgar__jgqgb in list(sort_node.df_out_vars.keys()):
        sort_node.df_out_vars[zjgar__jgqgb] = replace_vars_inner(sort_node.
            df_out_vars[zjgar__jgqgb], var_dict)
    return


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    kuj__vqj = False
    qfpf__uevrq = list(sort_node.df_in_vars.values())
    qekjy__oiolz = list(sort_node.df_out_vars.values())
    if array_dists is not None:
        kuj__vqj = True
        for ytuv__rtbtf in (sort_node.key_arrs + sort_node.out_key_arrs +
            qfpf__uevrq + qekjy__oiolz):
            if array_dists[ytuv__rtbtf.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                ytuv__rtbtf.name] != distributed_pass.Distribution.OneD_Var:
                kuj__vqj = False
    loc = sort_node.loc
    izey__slepc = sort_node.key_arrs[0].scope
    nodes = []
    key_arrs = sort_node.key_arrs
    if not sort_node.inplace:
        abor__dpfi = []
        for ytuv__rtbtf in key_arrs:
            najdc__uxba = _copy_array_nodes(ytuv__rtbtf, nodes, typingctx,
                targetctx, typemap, calltypes)
            abor__dpfi.append(najdc__uxba)
        key_arrs = abor__dpfi
        ocxh__dyxq = []
        for ytuv__rtbtf in qfpf__uevrq:
            mdwyl__gxnuo = _copy_array_nodes(ytuv__rtbtf, nodes, typingctx,
                targetctx, typemap, calltypes)
            ocxh__dyxq.append(mdwyl__gxnuo)
        qfpf__uevrq = ocxh__dyxq
    key_name_args = [('key' + str(clks__dxscq)) for clks__dxscq in range(
        len(key_arrs))]
    nqldc__vpw = ', '.join(key_name_args)
    col_name_args = [('c' + str(clks__dxscq)) for clks__dxscq in range(len(
        qfpf__uevrq))]
    leckf__hww = ', '.join(col_name_args)
    tszs__csjz = 'def f({}, {}):\n'.format(nqldc__vpw, leckf__hww)
    tszs__csjz += get_sort_cpp_section(key_name_args, col_name_args,
        sort_node.ascending_list, sort_node.na_position_b, kuj__vqj)
    tszs__csjz += '  return key_arrs, data\n'
    send__xogo = {}
    exec(tszs__csjz, {}, send__xogo)
    lhcp__uxqmm = send__xogo['f']
    rjbe__mqakn = types.Tuple([typemap[ytuv__rtbtf.name] for ytuv__rtbtf in
        key_arrs])
    lehdi__uyo = types.Tuple([typemap[ytuv__rtbtf.name] for ytuv__rtbtf in
        qfpf__uevrq])
    ghkjt__ouxcp = compile_to_numba_ir(lhcp__uxqmm, {'bodo': bodo, 'np': np,
        'to_list_if_immutable_arr': to_list_if_immutable_arr,
        'cp_str_list_to_array': cp_str_list_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'sort_values_table':
        sort_values_table, 'arr_info_list_to_table': arr_info_list_to_table,
        'array_to_info': array_to_info}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=tuple(list(rjbe__mqakn.types) + list(lehdi__uyo
        .types)), typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(ghkjt__ouxcp, key_arrs + qfpf__uevrq)
    nodes += ghkjt__ouxcp.body[:-2]
    czxud__zdfn = nodes[-1].target
    sala__iynk = ir.Var(izey__slepc, mk_unique_var('key_data'), loc)
    typemap[sala__iynk.name] = rjbe__mqakn
    gen_getitem(sala__iynk, czxud__zdfn, 0, calltypes, nodes)
    lcu__nthu = ir.Var(izey__slepc, mk_unique_var('sort_data'), loc)
    typemap[lcu__nthu.name] = lehdi__uyo
    gen_getitem(lcu__nthu, czxud__zdfn, 1, calltypes, nodes)
    for clks__dxscq, var in enumerate(sort_node.out_key_arrs):
        gen_getitem(var, sala__iynk, clks__dxscq, calltypes, nodes)
    for clks__dxscq, var in enumerate(qekjy__oiolz):
        gen_getitem(var, lcu__nthu, clks__dxscq, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes):

    def _impl(arr):
        return arr.copy()
    ghkjt__ouxcp = compile_to_numba_ir(_impl, {}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(ghkjt__ouxcp, [var])
    nodes += ghkjt__ouxcp.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(key_name_args, col_name_args, ascending_list,
    na_position_b, parallel_b):
    aifw__eowvf = len(key_name_args)
    rky__xyze = ['array_to_info({})'.format(isz__erla) for isz__erla in
        key_name_args] + ['array_to_info({})'.format(isz__erla) for
        isz__erla in col_name_args]
    tszs__csjz = '  info_list_total = [{}]\n'.format(','.join(rky__xyze))
    tszs__csjz += '  table_total = arr_info_list_to_table(info_list_total)\n'
    tszs__csjz += '  vect_ascending = np.array([{}])\n'.format(','.join('1' if
        kljoi__mcaae else '0' for kljoi__mcaae in ascending_list))
    tszs__csjz += '  na_position = np.array([{}])\n'.format(','.join('1' if
        kljoi__mcaae else '0' for kljoi__mcaae in na_position_b))
    tszs__csjz += (
        """  out_table = sort_values_table(table_total, {}, vect_ascending.ctypes, na_position.ctypes, {})
"""
        .format(aifw__eowvf, parallel_b))
    lexyf__aegp = 0
    aiew__opum = []
    for isz__erla in key_name_args:
        aiew__opum.append('info_to_array(info_from_table(out_table, {}), {})'
            .format(lexyf__aegp, isz__erla))
        lexyf__aegp += 1
    tszs__csjz += '  key_arrs = ({},)\n'.format(','.join(aiew__opum))
    nsmoq__yvefc = []
    for isz__erla in col_name_args:
        nsmoq__yvefc.append('info_to_array(info_from_table(out_table, {}), {})'
            .format(lexyf__aegp, isz__erla))
        lexyf__aegp += 1
    if len(nsmoq__yvefc) > 0:
        tszs__csjz += '  data = ({},)\n'.format(','.join(nsmoq__yvefc))
    else:
        tszs__csjz += '  data = ()\n'
    tszs__csjz += '  delete_table(out_table)\n'
    tszs__csjz += '  delete_table(table_total)\n'
    return tszs__csjz
