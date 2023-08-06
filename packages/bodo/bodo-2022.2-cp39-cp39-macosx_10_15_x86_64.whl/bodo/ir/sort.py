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
            self.na_position_b = tuple([(True if whh__alqi == 'last' else 
                False) for whh__alqi in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_arrs)
        self.ascending_list = ascending_list
        self.loc = loc

    def __repr__(self):
        bzjet__egz = ''
        for mpxv__kahre, ojhov__nsyt in self.df_in_vars.items():
            bzjet__egz += "'{}':{}, ".format(mpxv__kahre, ojhov__nsyt.name)
        plel__webky = '{}{{{}}}'.format(self.df_in, bzjet__egz)
        hqfg__mqf = ''
        for mpxv__kahre, ojhov__nsyt in self.df_out_vars.items():
            hqfg__mqf += "'{}':{}, ".format(mpxv__kahre, ojhov__nsyt.name)
        gkmdd__wemrl = '{}{{{}}}'.format(self.df_out, hqfg__mqf)
        return 'sort: [key: {}] {} [key: {}] {}'.format(', '.join(
            ojhov__nsyt.name for ojhov__nsyt in self.key_arrs), plel__webky,
            ', '.join(ojhov__nsyt.name for ojhov__nsyt in self.out_key_arrs
            ), gkmdd__wemrl)


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    zfxd__bmgo = []
    fhr__tmfw = sort_node.key_arrs + list(sort_node.df_in_vars.values())
    for mcf__bpz in fhr__tmfw:
        ahxb__jejtv = equiv_set.get_shape(mcf__bpz)
        if ahxb__jejtv is not None:
            zfxd__bmgo.append(ahxb__jejtv[0])
    if len(zfxd__bmgo) > 1:
        equiv_set.insert_equiv(*zfxd__bmgo)
    oczt__rkkff = []
    zfxd__bmgo = []
    oro__wjy = sort_node.out_key_arrs + list(sort_node.df_out_vars.values())
    for mcf__bpz in oro__wjy:
        wpnwx__qhujx = typemap[mcf__bpz.name]
        nvbdt__ugglw = array_analysis._gen_shape_call(equiv_set, mcf__bpz,
            wpnwx__qhujx.ndim, None, oczt__rkkff)
        equiv_set.insert_equiv(mcf__bpz, nvbdt__ugglw)
        zfxd__bmgo.append(nvbdt__ugglw[0])
        equiv_set.define(mcf__bpz, set())
    if len(zfxd__bmgo) > 1:
        equiv_set.insert_equiv(*zfxd__bmgo)
    return [], oczt__rkkff


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    fhr__tmfw = sort_node.key_arrs + list(sort_node.df_in_vars.values())
    dympt__okyzc = sort_node.out_key_arrs + list(sort_node.df_out_vars.values()
        )
    basr__rcxa = Distribution.OneD
    for mcf__bpz in fhr__tmfw:
        basr__rcxa = Distribution(min(basr__rcxa.value, array_dists[
            mcf__bpz.name].value))
    kwpwp__kxsij = Distribution(min(basr__rcxa.value, Distribution.OneD_Var
        .value))
    for mcf__bpz in dympt__okyzc:
        if mcf__bpz.name in array_dists:
            kwpwp__kxsij = Distribution(min(kwpwp__kxsij.value, array_dists
                [mcf__bpz.name].value))
    if kwpwp__kxsij != Distribution.OneD_Var:
        basr__rcxa = kwpwp__kxsij
    for mcf__bpz in fhr__tmfw:
        array_dists[mcf__bpz.name] = basr__rcxa
    for mcf__bpz in dympt__okyzc:
        array_dists[mcf__bpz.name] = kwpwp__kxsij
    return


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for nig__enamg, tsalw__myge in zip(sort_node.key_arrs, sort_node.
        out_key_arrs):
        typeinferer.constraints.append(typeinfer.Propagate(dst=tsalw__myge.
            name, src=nig__enamg.name, loc=sort_node.loc))
    for itpvq__uipip, mcf__bpz in sort_node.df_in_vars.items():
        ljju__efle = sort_node.df_out_vars[itpvq__uipip]
        typeinferer.constraints.append(typeinfer.Propagate(dst=ljju__efle.
            name, src=mcf__bpz.name, loc=sort_node.loc))
    return


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for mcf__bpz in (sort_node.out_key_arrs + list(sort_node.
            df_out_vars.values())):
            definitions[mcf__bpz.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    if debug_prints():
        print('visiting sort vars for:', sort_node)
        print('cbdata: ', sorted(cbdata.items()))
    for svf__opx in range(len(sort_node.key_arrs)):
        sort_node.key_arrs[svf__opx] = visit_vars_inner(sort_node.key_arrs[
            svf__opx], callback, cbdata)
        sort_node.out_key_arrs[svf__opx] = visit_vars_inner(sort_node.
            out_key_arrs[svf__opx], callback, cbdata)
    for itpvq__uipip in list(sort_node.df_in_vars.keys()):
        sort_node.df_in_vars[itpvq__uipip] = visit_vars_inner(sort_node.
            df_in_vars[itpvq__uipip], callback, cbdata)
    for itpvq__uipip in list(sort_node.df_out_vars.keys()):
        sort_node.df_out_vars[itpvq__uipip] = visit_vars_inner(sort_node.
            df_out_vars[itpvq__uipip], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    nsq__mhmsy = []
    for itpvq__uipip, mcf__bpz in sort_node.df_out_vars.items():
        if mcf__bpz.name not in lives:
            nsq__mhmsy.append(itpvq__uipip)
    for pkycm__aso in nsq__mhmsy:
        sort_node.df_in_vars.pop(pkycm__aso)
        sort_node.df_out_vars.pop(pkycm__aso)
    if len(sort_node.df_out_vars) == 0 and all(ojhov__nsyt.name not in
        lives for ojhov__nsyt in sort_node.out_key_arrs):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({ojhov__nsyt.name for ojhov__nsyt in sort_node.key_arrs})
    use_set.update({ojhov__nsyt.name for ojhov__nsyt in sort_node.
        df_in_vars.values()})
    if not sort_node.inplace:
        def_set.update({ojhov__nsyt.name for ojhov__nsyt in sort_node.
            out_key_arrs})
        def_set.update({ojhov__nsyt.name for ojhov__nsyt in sort_node.
            df_out_vars.values()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    jdpy__jlv = set()
    if not sort_node.inplace:
        jdpy__jlv = set(ojhov__nsyt.name for ojhov__nsyt in sort_node.
            df_out_vars.values())
        jdpy__jlv.update({ojhov__nsyt.name for ojhov__nsyt in sort_node.
            out_key_arrs})
    return set(), jdpy__jlv


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for svf__opx in range(len(sort_node.key_arrs)):
        sort_node.key_arrs[svf__opx] = replace_vars_inner(sort_node.
            key_arrs[svf__opx], var_dict)
        sort_node.out_key_arrs[svf__opx] = replace_vars_inner(sort_node.
            out_key_arrs[svf__opx], var_dict)
    for itpvq__uipip in list(sort_node.df_in_vars.keys()):
        sort_node.df_in_vars[itpvq__uipip] = replace_vars_inner(sort_node.
            df_in_vars[itpvq__uipip], var_dict)
    for itpvq__uipip in list(sort_node.df_out_vars.keys()):
        sort_node.df_out_vars[itpvq__uipip] = replace_vars_inner(sort_node.
            df_out_vars[itpvq__uipip], var_dict)
    return


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    xgz__kdkib = False
    ods__gtc = list(sort_node.df_in_vars.values())
    oro__wjy = list(sort_node.df_out_vars.values())
    if array_dists is not None:
        xgz__kdkib = True
        for ojhov__nsyt in (sort_node.key_arrs + sort_node.out_key_arrs +
            ods__gtc + oro__wjy):
            if array_dists[ojhov__nsyt.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                ojhov__nsyt.name] != distributed_pass.Distribution.OneD_Var:
                xgz__kdkib = False
    loc = sort_node.loc
    tnq__bfd = sort_node.key_arrs[0].scope
    nodes = []
    key_arrs = sort_node.key_arrs
    if not sort_node.inplace:
        syf__mvgai = []
        for ojhov__nsyt in key_arrs:
            tbld__byba = _copy_array_nodes(ojhov__nsyt, nodes, typingctx,
                targetctx, typemap, calltypes)
            syf__mvgai.append(tbld__byba)
        key_arrs = syf__mvgai
        jko__qyij = []
        for ojhov__nsyt in ods__gtc:
            fjjt__lbk = _copy_array_nodes(ojhov__nsyt, nodes, typingctx,
                targetctx, typemap, calltypes)
            jko__qyij.append(fjjt__lbk)
        ods__gtc = jko__qyij
    key_name_args = [('key' + str(svf__opx)) for svf__opx in range(len(
        key_arrs))]
    mvi__eryo = ', '.join(key_name_args)
    col_name_args = [('c' + str(svf__opx)) for svf__opx in range(len(ods__gtc))
        ]
    rwucd__uqdun = ', '.join(col_name_args)
    ejs__sbij = 'def f({}, {}):\n'.format(mvi__eryo, rwucd__uqdun)
    ejs__sbij += get_sort_cpp_section(key_name_args, col_name_args,
        sort_node.ascending_list, sort_node.na_position_b, xgz__kdkib)
    ejs__sbij += '  return key_arrs, data\n'
    nmdiy__prii = {}
    exec(ejs__sbij, {}, nmdiy__prii)
    lavf__igyc = nmdiy__prii['f']
    mqfid__edrfo = types.Tuple([typemap[ojhov__nsyt.name] for ojhov__nsyt in
        key_arrs])
    gegu__bpqwq = types.Tuple([typemap[ojhov__nsyt.name] for ojhov__nsyt in
        ods__gtc])
    vheq__bmtoe = compile_to_numba_ir(lavf__igyc, {'bodo': bodo, 'np': np,
        'to_list_if_immutable_arr': to_list_if_immutable_arr,
        'cp_str_list_to_array': cp_str_list_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'sort_values_table':
        sort_values_table, 'arr_info_list_to_table': arr_info_list_to_table,
        'array_to_info': array_to_info}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=tuple(list(mqfid__edrfo.types) + list(
        gegu__bpqwq.types)), typemap=typemap, calltypes=calltypes
        ).blocks.popitem()[1]
    replace_arg_nodes(vheq__bmtoe, key_arrs + ods__gtc)
    nodes += vheq__bmtoe.body[:-2]
    rlc__eot = nodes[-1].target
    lnfu__ugg = ir.Var(tnq__bfd, mk_unique_var('key_data'), loc)
    typemap[lnfu__ugg.name] = mqfid__edrfo
    gen_getitem(lnfu__ugg, rlc__eot, 0, calltypes, nodes)
    cpmj__hxcf = ir.Var(tnq__bfd, mk_unique_var('sort_data'), loc)
    typemap[cpmj__hxcf.name] = gegu__bpqwq
    gen_getitem(cpmj__hxcf, rlc__eot, 1, calltypes, nodes)
    for svf__opx, var in enumerate(sort_node.out_key_arrs):
        gen_getitem(var, lnfu__ugg, svf__opx, calltypes, nodes)
    for svf__opx, var in enumerate(oro__wjy):
        gen_getitem(var, cpmj__hxcf, svf__opx, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes):

    def _impl(arr):
        return arr.copy()
    vheq__bmtoe = compile_to_numba_ir(_impl, {}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(vheq__bmtoe, [var])
    nodes += vheq__bmtoe.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(key_name_args, col_name_args, ascending_list,
    na_position_b, parallel_b):
    nndk__xqv = len(key_name_args)
    tzlr__mpzv = ['array_to_info({})'.format(vlb__pdcp) for vlb__pdcp in
        key_name_args] + ['array_to_info({})'.format(vlb__pdcp) for
        vlb__pdcp in col_name_args]
    ejs__sbij = '  info_list_total = [{}]\n'.format(','.join(tzlr__mpzv))
    ejs__sbij += '  table_total = arr_info_list_to_table(info_list_total)\n'
    ejs__sbij += '  vect_ascending = np.array([{}])\n'.format(','.join('1' if
        qjvvx__hpfb else '0' for qjvvx__hpfb in ascending_list))
    ejs__sbij += '  na_position = np.array([{}])\n'.format(','.join('1' if
        qjvvx__hpfb else '0' for qjvvx__hpfb in na_position_b))
    ejs__sbij += (
        """  out_table = sort_values_table(table_total, {}, vect_ascending.ctypes, na_position.ctypes, {})
"""
        .format(nndk__xqv, parallel_b))
    itzdk__vzrey = 0
    tgo__mmsaq = []
    for vlb__pdcp in key_name_args:
        tgo__mmsaq.append('info_to_array(info_from_table(out_table, {}), {})'
            .format(itzdk__vzrey, vlb__pdcp))
        itzdk__vzrey += 1
    ejs__sbij += '  key_arrs = ({},)\n'.format(','.join(tgo__mmsaq))
    pvmq__tax = []
    for vlb__pdcp in col_name_args:
        pvmq__tax.append('info_to_array(info_from_table(out_table, {}), {})'
            .format(itzdk__vzrey, vlb__pdcp))
        itzdk__vzrey += 1
    if len(pvmq__tax) > 0:
        ejs__sbij += '  data = ({},)\n'.format(','.join(pvmq__tax))
    else:
        ejs__sbij += '  data = ()\n'
    ejs__sbij += '  delete_table(out_table)\n'
    ejs__sbij += '  delete_table(table_total)\n'
    return ejs__sbij
