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
            self.na_position_b = tuple([(True if iydn__vmn == 'last' else 
                False) for iydn__vmn in na_position])
        if isinstance(ascending_list, bool):
            ascending_list = (ascending_list,) * len(key_arrs)
        self.ascending_list = ascending_list
        self.loc = loc

    def __repr__(self):
        ayayi__avex = ''
        for pfgc__cixc, spsa__dfjd in self.df_in_vars.items():
            ayayi__avex += "'{}':{}, ".format(pfgc__cixc, spsa__dfjd.name)
        tzybm__tbgrs = '{}{{{}}}'.format(self.df_in, ayayi__avex)
        twm__jhjbf = ''
        for pfgc__cixc, spsa__dfjd in self.df_out_vars.items():
            twm__jhjbf += "'{}':{}, ".format(pfgc__cixc, spsa__dfjd.name)
        qjaz__elvn = '{}{{{}}}'.format(self.df_out, twm__jhjbf)
        return 'sort: [key: {}] {} [key: {}] {}'.format(', '.join(
            spsa__dfjd.name for spsa__dfjd in self.key_arrs), tzybm__tbgrs,
            ', '.join(spsa__dfjd.name for spsa__dfjd in self.out_key_arrs),
            qjaz__elvn)


def sort_array_analysis(sort_node, equiv_set, typemap, array_analysis):
    lwy__vxrx = []
    geky__gis = sort_node.key_arrs + list(sort_node.df_in_vars.values())
    for fnder__oyvr in geky__gis:
        dzv__qmafj = equiv_set.get_shape(fnder__oyvr)
        if dzv__qmafj is not None:
            lwy__vxrx.append(dzv__qmafj[0])
    if len(lwy__vxrx) > 1:
        equiv_set.insert_equiv(*lwy__vxrx)
    ese__ilhho = []
    lwy__vxrx = []
    vnk__ahbz = sort_node.out_key_arrs + list(sort_node.df_out_vars.values())
    for fnder__oyvr in vnk__ahbz:
        yne__smmpv = typemap[fnder__oyvr.name]
        ipu__kffm = array_analysis._gen_shape_call(equiv_set, fnder__oyvr,
            yne__smmpv.ndim, None, ese__ilhho)
        equiv_set.insert_equiv(fnder__oyvr, ipu__kffm)
        lwy__vxrx.append(ipu__kffm[0])
        equiv_set.define(fnder__oyvr, set())
    if len(lwy__vxrx) > 1:
        equiv_set.insert_equiv(*lwy__vxrx)
    return [], ese__ilhho


numba.parfors.array_analysis.array_analysis_extensions[Sort
    ] = sort_array_analysis


def sort_distributed_analysis(sort_node, array_dists):
    geky__gis = sort_node.key_arrs + list(sort_node.df_in_vars.values())
    lobc__jqfdu = sort_node.out_key_arrs + list(sort_node.df_out_vars.values())
    jhb__jbeap = Distribution.OneD
    for fnder__oyvr in geky__gis:
        jhb__jbeap = Distribution(min(jhb__jbeap.value, array_dists[
            fnder__oyvr.name].value))
    fnoh__lvz = Distribution(min(jhb__jbeap.value, Distribution.OneD_Var.value)
        )
    for fnder__oyvr in lobc__jqfdu:
        if fnder__oyvr.name in array_dists:
            fnoh__lvz = Distribution(min(fnoh__lvz.value, array_dists[
                fnder__oyvr.name].value))
    if fnoh__lvz != Distribution.OneD_Var:
        jhb__jbeap = fnoh__lvz
    for fnder__oyvr in geky__gis:
        array_dists[fnder__oyvr.name] = jhb__jbeap
    for fnder__oyvr in lobc__jqfdu:
        array_dists[fnder__oyvr.name] = fnoh__lvz
    return


distributed_analysis.distributed_analysis_extensions[Sort
    ] = sort_distributed_analysis


def sort_typeinfer(sort_node, typeinferer):
    for wmid__riep, fteb__cvdt in zip(sort_node.key_arrs, sort_node.
        out_key_arrs):
        typeinferer.constraints.append(typeinfer.Propagate(dst=fteb__cvdt.
            name, src=wmid__riep.name, loc=sort_node.loc))
    for sce__itvrk, fnder__oyvr in sort_node.df_in_vars.items():
        rhdbn__qzi = sort_node.df_out_vars[sce__itvrk]
        typeinferer.constraints.append(typeinfer.Propagate(dst=rhdbn__qzi.
            name, src=fnder__oyvr.name, loc=sort_node.loc))
    return


typeinfer.typeinfer_extensions[Sort] = sort_typeinfer


def build_sort_definitions(sort_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    if not sort_node.inplace:
        for fnder__oyvr in (sort_node.out_key_arrs + list(sort_node.
            df_out_vars.values())):
            definitions[fnder__oyvr.name].append(sort_node)
    return definitions


ir_utils.build_defs_extensions[Sort] = build_sort_definitions


def visit_vars_sort(sort_node, callback, cbdata):
    if debug_prints():
        print('visiting sort vars for:', sort_node)
        print('cbdata: ', sorted(cbdata.items()))
    for ymc__oitk in range(len(sort_node.key_arrs)):
        sort_node.key_arrs[ymc__oitk] = visit_vars_inner(sort_node.key_arrs
            [ymc__oitk], callback, cbdata)
        sort_node.out_key_arrs[ymc__oitk] = visit_vars_inner(sort_node.
            out_key_arrs[ymc__oitk], callback, cbdata)
    for sce__itvrk in list(sort_node.df_in_vars.keys()):
        sort_node.df_in_vars[sce__itvrk] = visit_vars_inner(sort_node.
            df_in_vars[sce__itvrk], callback, cbdata)
    for sce__itvrk in list(sort_node.df_out_vars.keys()):
        sort_node.df_out_vars[sce__itvrk] = visit_vars_inner(sort_node.
            df_out_vars[sce__itvrk], callback, cbdata)


ir_utils.visit_vars_extensions[Sort] = visit_vars_sort


def remove_dead_sort(sort_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    pxog__kgnw = []
    for sce__itvrk, fnder__oyvr in sort_node.df_out_vars.items():
        if fnder__oyvr.name not in lives:
            pxog__kgnw.append(sce__itvrk)
    for uvuk__lexn in pxog__kgnw:
        sort_node.df_in_vars.pop(uvuk__lexn)
        sort_node.df_out_vars.pop(uvuk__lexn)
    if len(sort_node.df_out_vars) == 0 and all(spsa__dfjd.name not in lives for
        spsa__dfjd in sort_node.out_key_arrs):
        return None
    return sort_node


ir_utils.remove_dead_extensions[Sort] = remove_dead_sort


def sort_usedefs(sort_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({spsa__dfjd.name for spsa__dfjd in sort_node.key_arrs})
    use_set.update({spsa__dfjd.name for spsa__dfjd in sort_node.df_in_vars.
        values()})
    if not sort_node.inplace:
        def_set.update({spsa__dfjd.name for spsa__dfjd in sort_node.
            out_key_arrs})
        def_set.update({spsa__dfjd.name for spsa__dfjd in sort_node.
            df_out_vars.values()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Sort] = sort_usedefs


def get_copies_sort(sort_node, typemap):
    efjd__ttru = set()
    if not sort_node.inplace:
        efjd__ttru = set(spsa__dfjd.name for spsa__dfjd in sort_node.
            df_out_vars.values())
        efjd__ttru.update({spsa__dfjd.name for spsa__dfjd in sort_node.
            out_key_arrs})
    return set(), efjd__ttru


ir_utils.copy_propagate_extensions[Sort] = get_copies_sort


def apply_copies_sort(sort_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for ymc__oitk in range(len(sort_node.key_arrs)):
        sort_node.key_arrs[ymc__oitk] = replace_vars_inner(sort_node.
            key_arrs[ymc__oitk], var_dict)
        sort_node.out_key_arrs[ymc__oitk] = replace_vars_inner(sort_node.
            out_key_arrs[ymc__oitk], var_dict)
    for sce__itvrk in list(sort_node.df_in_vars.keys()):
        sort_node.df_in_vars[sce__itvrk] = replace_vars_inner(sort_node.
            df_in_vars[sce__itvrk], var_dict)
    for sce__itvrk in list(sort_node.df_out_vars.keys()):
        sort_node.df_out_vars[sce__itvrk] = replace_vars_inner(sort_node.
            df_out_vars[sce__itvrk], var_dict)
    return


ir_utils.apply_copy_propagate_extensions[Sort] = apply_copies_sort


def sort_distributed_run(sort_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    exn__cdz = False
    kido__snk = list(sort_node.df_in_vars.values())
    vnk__ahbz = list(sort_node.df_out_vars.values())
    if array_dists is not None:
        exn__cdz = True
        for spsa__dfjd in (sort_node.key_arrs + sort_node.out_key_arrs +
            kido__snk + vnk__ahbz):
            if array_dists[spsa__dfjd.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                spsa__dfjd.name] != distributed_pass.Distribution.OneD_Var:
                exn__cdz = False
    loc = sort_node.loc
    jkwh__mhxf = sort_node.key_arrs[0].scope
    nodes = []
    key_arrs = sort_node.key_arrs
    if not sort_node.inplace:
        uzzmm__xve = []
        for spsa__dfjd in key_arrs:
            vzs__eaz = _copy_array_nodes(spsa__dfjd, nodes, typingctx,
                targetctx, typemap, calltypes)
            uzzmm__xve.append(vzs__eaz)
        key_arrs = uzzmm__xve
        locq__cyx = []
        for spsa__dfjd in kido__snk:
            fyio__eig = _copy_array_nodes(spsa__dfjd, nodes, typingctx,
                targetctx, typemap, calltypes)
            locq__cyx.append(fyio__eig)
        kido__snk = locq__cyx
    key_name_args = [('key' + str(ymc__oitk)) for ymc__oitk in range(len(
        key_arrs))]
    yhnig__ppq = ', '.join(key_name_args)
    col_name_args = [('c' + str(ymc__oitk)) for ymc__oitk in range(len(
        kido__snk))]
    hrkx__ihqux = ', '.join(col_name_args)
    iyd__vvmp = 'def f({}, {}):\n'.format(yhnig__ppq, hrkx__ihqux)
    iyd__vvmp += get_sort_cpp_section(key_name_args, col_name_args,
        sort_node.ascending_list, sort_node.na_position_b, exn__cdz)
    iyd__vvmp += '  return key_arrs, data\n'
    pzkb__icx = {}
    exec(iyd__vvmp, {}, pzkb__icx)
    zyesz__xoq = pzkb__icx['f']
    jke__uiy = types.Tuple([typemap[spsa__dfjd.name] for spsa__dfjd in
        key_arrs])
    ono__spyeh = types.Tuple([typemap[spsa__dfjd.name] for spsa__dfjd in
        kido__snk])
    othcr__pvqeo = compile_to_numba_ir(zyesz__xoq, {'bodo': bodo, 'np': np,
        'to_list_if_immutable_arr': to_list_if_immutable_arr,
        'cp_str_list_to_array': cp_str_list_to_array, 'delete_table':
        delete_table, 'delete_table_decref_arrays':
        delete_table_decref_arrays, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'sort_values_table':
        sort_values_table, 'arr_info_list_to_table': arr_info_list_to_table,
        'array_to_info': array_to_info}, typingctx=typingctx, targetctx=
        targetctx, arg_typs=tuple(list(jke__uiy.types) + list(ono__spyeh.
        types)), typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(othcr__pvqeo, key_arrs + kido__snk)
    nodes += othcr__pvqeo.body[:-2]
    rkv__grzkg = nodes[-1].target
    zxa__dolsk = ir.Var(jkwh__mhxf, mk_unique_var('key_data'), loc)
    typemap[zxa__dolsk.name] = jke__uiy
    gen_getitem(zxa__dolsk, rkv__grzkg, 0, calltypes, nodes)
    qqztw__zhtrp = ir.Var(jkwh__mhxf, mk_unique_var('sort_data'), loc)
    typemap[qqztw__zhtrp.name] = ono__spyeh
    gen_getitem(qqztw__zhtrp, rkv__grzkg, 1, calltypes, nodes)
    for ymc__oitk, var in enumerate(sort_node.out_key_arrs):
        gen_getitem(var, zxa__dolsk, ymc__oitk, calltypes, nodes)
    for ymc__oitk, var in enumerate(vnk__ahbz):
        gen_getitem(var, qqztw__zhtrp, ymc__oitk, calltypes, nodes)
    return nodes


distributed_pass.distributed_run_extensions[Sort] = sort_distributed_run


def _copy_array_nodes(var, nodes, typingctx, targetctx, typemap, calltypes):

    def _impl(arr):
        return arr.copy()
    othcr__pvqeo = compile_to_numba_ir(_impl, {}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(typemap[var.name],), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(othcr__pvqeo, [var])
    nodes += othcr__pvqeo.body[:-2]
    return nodes[-1].target


def get_sort_cpp_section(key_name_args, col_name_args, ascending_list,
    na_position_b, parallel_b):
    clwpe__rds = len(key_name_args)
    yorc__vbe = ['array_to_info({})'.format(pyx__rhx) for pyx__rhx in
        key_name_args] + ['array_to_info({})'.format(pyx__rhx) for pyx__rhx in
        col_name_args]
    iyd__vvmp = '  info_list_total = [{}]\n'.format(','.join(yorc__vbe))
    iyd__vvmp += '  table_total = arr_info_list_to_table(info_list_total)\n'
    iyd__vvmp += '  vect_ascending = np.array([{}])\n'.format(','.join('1' if
        vovha__kqato else '0' for vovha__kqato in ascending_list))
    iyd__vvmp += '  na_position = np.array([{}])\n'.format(','.join('1' if
        vovha__kqato else '0' for vovha__kqato in na_position_b))
    iyd__vvmp += (
        """  out_table = sort_values_table(table_total, {}, vect_ascending.ctypes, na_position.ctypes, {})
"""
        .format(clwpe__rds, parallel_b))
    lme__wtycg = 0
    waq__iose = []
    for pyx__rhx in key_name_args:
        waq__iose.append('info_to_array(info_from_table(out_table, {}), {})'
            .format(lme__wtycg, pyx__rhx))
        lme__wtycg += 1
    iyd__vvmp += '  key_arrs = ({},)\n'.format(','.join(waq__iose))
    kzlb__bdw = []
    for pyx__rhx in col_name_args:
        kzlb__bdw.append('info_to_array(info_from_table(out_table, {}), {})'
            .format(lme__wtycg, pyx__rhx))
        lme__wtycg += 1
    if len(kzlb__bdw) > 0:
        iyd__vvmp += '  data = ({},)\n'.format(','.join(kzlb__bdw))
    else:
        iyd__vvmp += '  data = ()\n'
    iyd__vvmp += '  delete_table(out_table)\n'
    iyd__vvmp += '  delete_table(table_total)\n'
    return iyd__vvmp
