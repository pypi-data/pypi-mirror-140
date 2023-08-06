"""IR node for the join and merge"""
from collections import defaultdict
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba import generated_jit
from numba.core import cgutils, ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, next_label, replace_arg_nodes, replace_vars_inner, visit_vars_inner
from numba.extending import intrinsic, overload
import bodo
from bodo.libs.array import arr_info_list_to_table, array_to_info, compute_node_partition_by_hash, delete_table, delete_table_decref_arrays, hash_join_table, info_from_table, info_to_array
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.int_arr_ext import IntDtype, IntegerArrayType
from bodo.libs.str_arr_ext import copy_str_arr_slice, cp_str_list_to_array, get_bit_bitmap, get_null_bitmap_ptr, get_str_arr_item_length, get_str_arr_item_ptr, get_utf8_size, getitem_str_offset, num_total_chars, pre_alloc_string_array, set_bit_to, str_copy_ptr, string_array_type, to_list_if_immutable_arr
from bodo.libs.str_ext import string_type
from bodo.libs.timsort import getitem_arr_tup, setitem_arr_tup
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.distributed_analysis import Distribution
from bodo.utils.shuffle import _get_data_tup, _get_keys_tup, alloc_pre_shuffle_metadata, alltoallv_tup, finalize_shuffle_meta, getitem_arr_tup_single, update_shuffle_meta
from bodo.utils.typing import BodoError, dtype_to_array_type, find_common_np_dtype, is_dtype_nullable, is_nullable_type, to_nullable_type
from bodo.utils.utils import alloc_arr_tup, debug_prints, is_null_pointer
join_gen_cond_cfunc = {}
join_gen_cond_cfunc_addr = {}


@intrinsic
def add_join_gen_cond_cfunc_sym(typingctx, func, sym):

    def codegen(context, builder, signature, args):
        gsymd__nlaa = func.signature
        qtae__byi = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        ibu__yji = cgutils.get_or_insert_function(builder.module, qtae__byi,
            sym._literal_value)
        builder.call(ibu__yji, [context.get_constant_null(gsymd__nlaa.args[
            0]), context.get_constant_null(gsymd__nlaa.args[1]), context.
            get_constant_null(gsymd__nlaa.args[2]), context.
            get_constant_null(gsymd__nlaa.args[3]), context.
            get_constant_null(gsymd__nlaa.args[4]), context.
            get_constant_null(gsymd__nlaa.args[5]), context.get_constant(
            types.int64, 0), context.get_constant(types.int64, 0)])
        context.add_linking_libs([join_gen_cond_cfunc[sym._literal_value].
            _library])
        return
    return types.none(func, sym), codegen


@numba.jit
def get_join_cond_addr(name):
    with numba.objmode(addr='int64'):
        addr = join_gen_cond_cfunc_addr[name]
    return addr


class Join(ir.Stmt):

    def __init__(self, df_out, left_df, right_df, left_keys, right_keys,
        out_data_vars, left_vars, right_vars, how, suffix_x, suffix_y, loc,
        is_left, is_right, is_join, left_index, right_index, indicator,
        is_na_equal, gen_cond_expr):
        self.df_out = df_out
        self.left_df = left_df
        self.right_df = right_df
        self.left_keys = left_keys
        self.right_keys = right_keys
        self.out_data_vars = out_data_vars
        self.left_vars = left_vars
        self.right_vars = right_vars
        self.how = how
        self.suffix_x = suffix_x
        self.suffix_y = suffix_y
        self.loc = loc
        self.is_left = is_left
        self.is_right = is_right
        self.is_join = is_join
        self.left_index = left_index
        self.right_index = right_index
        self.indicator = indicator
        self.is_na_equal = is_na_equal
        self.gen_cond_expr = gen_cond_expr
        self.left_cond_cols = set(ynwd__scc for ynwd__scc in left_vars.keys
            () if f'(left.{ynwd__scc})' in gen_cond_expr)
        self.right_cond_cols = set(ynwd__scc for ynwd__scc in right_vars.
            keys() if f'(right.{ynwd__scc})' in gen_cond_expr)
        daeg__zcp = set(left_keys) & set(right_keys)
        sbxst__qzcs = set(left_vars.keys()) & set(right_vars.keys())
        wduv__lzjyl = sbxst__qzcs - daeg__zcp
        vect_same_key = []
        n_keys = len(left_keys)
        for jiay__iiwgz in range(n_keys):
            ofawb__ymbak = left_keys[jiay__iiwgz]
            pmfeu__yvtje = right_keys[jiay__iiwgz]
            vect_same_key.append(ofawb__ymbak == pmfeu__yvtje)
        self.vect_same_key = vect_same_key
        self.column_origins = {(str(ynwd__scc) + suffix_x if ynwd__scc in
            wduv__lzjyl else ynwd__scc): ('left', ynwd__scc) for ynwd__scc in
            left_vars.keys()}
        self.column_origins.update({(str(ynwd__scc) + suffix_y if ynwd__scc in
            wduv__lzjyl else ynwd__scc): ('right', ynwd__scc) for ynwd__scc in
            right_vars.keys()})
        if '$_bodo_index_' in wduv__lzjyl:
            wduv__lzjyl.remove('$_bodo_index_')
        self.add_suffix = wduv__lzjyl

    def __repr__(self):
        nbmx__gwr = ''
        for ynwd__scc, xlpyy__dnbb in self.out_data_vars.items():
            nbmx__gwr += "'{}':{}, ".format(ynwd__scc, xlpyy__dnbb.name)
        ndm__mnqvk = '{}{{{}}}'.format(self.df_out, nbmx__gwr)
        rrhf__izh = ''
        for ynwd__scc, xlpyy__dnbb in self.left_vars.items():
            rrhf__izh += "'{}':{}, ".format(ynwd__scc, xlpyy__dnbb.name)
        pvi__dhqfi = '{}{{{}}}'.format(self.left_df, rrhf__izh)
        rrhf__izh = ''
        for ynwd__scc, xlpyy__dnbb in self.right_vars.items():
            rrhf__izh += "'{}':{}, ".format(ynwd__scc, xlpyy__dnbb.name)
        thor__dcst = '{}{{{}}}'.format(self.right_df, rrhf__izh)
        return 'join [{}={}]: {} , {}, {}'.format(self.left_keys, self.
            right_keys, ndm__mnqvk, pvi__dhqfi, thor__dcst)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    kqli__nzial = []
    assert len(join_node.out_data_vars) > 0, 'empty join in array analysis'
    daavo__zhf = []
    alcp__mkehc = list(join_node.left_vars.values())
    for oniom__rod in alcp__mkehc:
        lpbw__ehh = typemap[oniom__rod.name]
        opqq__frtc = equiv_set.get_shape(oniom__rod)
        if opqq__frtc:
            daavo__zhf.append(opqq__frtc[0])
    if len(daavo__zhf) > 1:
        equiv_set.insert_equiv(*daavo__zhf)
    daavo__zhf = []
    alcp__mkehc = list(join_node.right_vars.values())
    for oniom__rod in alcp__mkehc:
        lpbw__ehh = typemap[oniom__rod.name]
        opqq__frtc = equiv_set.get_shape(oniom__rod)
        if opqq__frtc:
            daavo__zhf.append(opqq__frtc[0])
    if len(daavo__zhf) > 1:
        equiv_set.insert_equiv(*daavo__zhf)
    daavo__zhf = []
    for oniom__rod in join_node.out_data_vars.values():
        lpbw__ehh = typemap[oniom__rod.name]
        toz__knao = array_analysis._gen_shape_call(equiv_set, oniom__rod,
            lpbw__ehh.ndim, None, kqli__nzial)
        equiv_set.insert_equiv(oniom__rod, toz__knao)
        daavo__zhf.append(toz__knao[0])
        equiv_set.define(oniom__rod, set())
    if len(daavo__zhf) > 1:
        equiv_set.insert_equiv(*daavo__zhf)
    return [], kqli__nzial


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    tqw__wrekb = Distribution.OneD
    jqpy__vmaig = Distribution.OneD
    for oniom__rod in join_node.left_vars.values():
        tqw__wrekb = Distribution(min(tqw__wrekb.value, array_dists[
            oniom__rod.name].value))
    for oniom__rod in join_node.right_vars.values():
        jqpy__vmaig = Distribution(min(jqpy__vmaig.value, array_dists[
            oniom__rod.name].value))
    lgg__tjo = Distribution.OneD_Var
    for oniom__rod in join_node.out_data_vars.values():
        if oniom__rod.name in array_dists:
            lgg__tjo = Distribution(min(lgg__tjo.value, array_dists[
                oniom__rod.name].value))
    lxkq__zdua = Distribution(min(lgg__tjo.value, tqw__wrekb.value))
    nlr__tbuuk = Distribution(min(lgg__tjo.value, jqpy__vmaig.value))
    lgg__tjo = Distribution(max(lxkq__zdua.value, nlr__tbuuk.value))
    for oniom__rod in join_node.out_data_vars.values():
        array_dists[oniom__rod.name] = lgg__tjo
    if lgg__tjo != Distribution.OneD_Var:
        tqw__wrekb = lgg__tjo
        jqpy__vmaig = lgg__tjo
    for oniom__rod in join_node.left_vars.values():
        array_dists[oniom__rod.name] = tqw__wrekb
    for oniom__rod in join_node.right_vars.values():
        array_dists[oniom__rod.name] = jqpy__vmaig
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def join_typeinfer(join_node, typeinferer):
    daeg__zcp = set(join_node.left_keys) & set(join_node.right_keys)
    sbxst__qzcs = set(join_node.left_vars.keys()) & set(join_node.
        right_vars.keys())
    wduv__lzjyl = sbxst__qzcs - daeg__zcp
    for xvwnx__jpyi, vfgb__xfmm in join_node.out_data_vars.items():
        if join_node.indicator and xvwnx__jpyi == '_merge':
            continue
        if not xvwnx__jpyi in join_node.column_origins:
            raise BodoError('join(): The variable ' + xvwnx__jpyi +
                ' is absent from the output')
        nvbt__ztt = join_node.column_origins[xvwnx__jpyi]
        if nvbt__ztt[0] == 'left':
            oniom__rod = join_node.left_vars[nvbt__ztt[1]]
        else:
            oniom__rod = join_node.right_vars[nvbt__ztt[1]]
        typeinferer.constraints.append(typeinfer.Propagate(dst=vfgb__xfmm.
            name, src=oniom__rod.name, loc=join_node.loc))
    return


typeinfer.typeinfer_extensions[Join] = join_typeinfer


def visit_vars_join(join_node, callback, cbdata):
    if debug_prints():
        print('visiting join vars for:', join_node)
        print('cbdata: ', sorted(cbdata.items()))
    for opg__hvf in list(join_node.left_vars.keys()):
        join_node.left_vars[opg__hvf] = visit_vars_inner(join_node.
            left_vars[opg__hvf], callback, cbdata)
    for opg__hvf in list(join_node.right_vars.keys()):
        join_node.right_vars[opg__hvf] = visit_vars_inner(join_node.
            right_vars[opg__hvf], callback, cbdata)
    for opg__hvf in list(join_node.out_data_vars.keys()):
        join_node.out_data_vars[opg__hvf] = visit_vars_inner(join_node.
            out_data_vars[opg__hvf], callback, cbdata)


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    hvzd__cbwpw = []
    xkfow__xnwgw = True
    for opg__hvf, oniom__rod in join_node.out_data_vars.items():
        if oniom__rod.name in lives:
            xkfow__xnwgw = False
            continue
        if opg__hvf == '$_bodo_index_':
            continue
        if join_node.indicator and opg__hvf == '_merge':
            hvzd__cbwpw.append('_merge')
            join_node.indicator = False
            continue
        oabj__ieh, wose__wve = join_node.column_origins[opg__hvf]
        if (oabj__ieh == 'left' and wose__wve not in join_node.left_keys and
            wose__wve not in join_node.left_cond_cols):
            join_node.left_vars.pop(wose__wve)
            hvzd__cbwpw.append(opg__hvf)
        if (oabj__ieh == 'right' and wose__wve not in join_node.right_keys and
            wose__wve not in join_node.right_cond_cols):
            join_node.right_vars.pop(wose__wve)
            hvzd__cbwpw.append(opg__hvf)
    for cname in hvzd__cbwpw:
        join_node.out_data_vars.pop(cname)
    if xkfow__xnwgw:
        return None
    return join_node


ir_utils.remove_dead_extensions[Join] = remove_dead_join


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({xlpyy__dnbb.name for xlpyy__dnbb in join_node.left_vars
        .values()})
    use_set.update({xlpyy__dnbb.name for xlpyy__dnbb in join_node.
        right_vars.values()})
    def_set.update({xlpyy__dnbb.name for xlpyy__dnbb in join_node.
        out_data_vars.values()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    iwxx__ouat = set(xlpyy__dnbb.name for xlpyy__dnbb in join_node.
        out_data_vars.values())
    return set(), iwxx__ouat


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for opg__hvf in list(join_node.left_vars.keys()):
        join_node.left_vars[opg__hvf] = replace_vars_inner(join_node.
            left_vars[opg__hvf], var_dict)
    for opg__hvf in list(join_node.right_vars.keys()):
        join_node.right_vars[opg__hvf] = replace_vars_inner(join_node.
            right_vars[opg__hvf], var_dict)
    for opg__hvf in list(join_node.out_data_vars.keys()):
        join_node.out_data_vars[opg__hvf] = replace_vars_inner(join_node.
            out_data_vars[opg__hvf], var_dict)
    return


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for oniom__rod in join_node.out_data_vars.values():
        definitions[oniom__rod.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    n_keys = len(join_node.left_keys)
    mwvss__duczs = tuple(join_node.left_vars[ynwd__scc] for ynwd__scc in
        join_node.left_keys)
    fab__pekjc = tuple(join_node.right_vars[ynwd__scc] for ynwd__scc in
        join_node.right_keys)
    lcefl__rbke = tuple(join_node.left_vars.keys())
    ibyk__bwo = tuple(join_node.right_vars.keys())
    gdwm__umvpa = ()
    sao__htnnb = ()
    optional_column = False
    if (join_node.left_index and not join_node.right_index and not
        join_node.is_join):
        lnnn__hwzx = join_node.right_keys[0]
        if lnnn__hwzx in lcefl__rbke:
            sao__htnnb = lnnn__hwzx,
            gdwm__umvpa = join_node.right_vars[lnnn__hwzx],
            optional_column = True
    if (join_node.right_index and not join_node.left_index and not
        join_node.is_join):
        lnnn__hwzx = join_node.left_keys[0]
        if lnnn__hwzx in ibyk__bwo:
            sao__htnnb = lnnn__hwzx,
            gdwm__umvpa = join_node.left_vars[lnnn__hwzx],
            optional_column = True
    miurz__qijxt = tuple(join_node.out_data_vars[cname] for cname in sao__htnnb
        )
    iwvi__udj = tuple(xlpyy__dnbb for mmfe__kyaoo, xlpyy__dnbb in sorted(
        join_node.left_vars.items(), key=lambda a: str(a[0])) if 
        mmfe__kyaoo not in join_node.left_keys)
    zamfz__afz = tuple(xlpyy__dnbb for mmfe__kyaoo, xlpyy__dnbb in sorted(
        join_node.right_vars.items(), key=lambda a: str(a[0])) if 
        mmfe__kyaoo not in join_node.right_keys)
    ydx__fhf = gdwm__umvpa + mwvss__duczs + fab__pekjc + iwvi__udj + zamfz__afz
    qzib__dyt = tuple(typemap[xlpyy__dnbb.name] for xlpyy__dnbb in ydx__fhf)
    nfmg__ijq = tuple('opti_c' + str(i) for i in range(len(gdwm__umvpa)))
    left_other_names = tuple('t1_c' + str(i) for i in range(len(iwvi__udj)))
    right_other_names = tuple('t2_c' + str(i) for i in range(len(zamfz__afz)))
    left_other_types = tuple([typemap[ynwd__scc.name] for ynwd__scc in
        iwvi__udj])
    right_other_types = tuple([typemap[ynwd__scc.name] for ynwd__scc in
        zamfz__afz])
    left_key_names = tuple('t1_key' + str(i) for i in range(n_keys))
    right_key_names = tuple('t2_key' + str(i) for i in range(n_keys))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}{}, {},{}{}{}):\n'.format('{},'.format(nfmg__ijq[0
        ]) if len(nfmg__ijq) == 1 else '', ','.join(left_key_names), ','.
        join(right_key_names), ','.join(left_other_names), ',' if len(
        left_other_names) != 0 else '', ','.join(right_other_names))
    left_key_types = tuple(typemap[xlpyy__dnbb.name] for xlpyy__dnbb in
        mwvss__duczs)
    right_key_types = tuple(typemap[xlpyy__dnbb.name] for xlpyy__dnbb in
        fab__pekjc)
    for i in range(n_keys):
        glbs[f'key_type_{i}'] = _match_join_key_types(left_key_types[i],
            right_key_types[i], loc)
    func_text += '    t1_keys = ({},)\n'.format(', '.join(
        f'bodo.utils.utils.astype({left_key_names[i]}, key_type_{i})' for i in
        range(n_keys)))
    func_text += '    t2_keys = ({},)\n'.format(', '.join(
        f'bodo.utils.utils.astype({right_key_names[i]}, key_type_{i})' for
        i in range(n_keys)))
    func_text += '    data_left = ({}{})\n'.format(','.join(
        left_other_names), ',' if len(left_other_names) != 0 else '')
    func_text += '    data_right = ({}{})\n'.format(','.join(
        right_other_names), ',' if len(right_other_names) != 0 else '')
    jchsi__rpee = []
    for cname in join_node.left_keys:
        if cname in join_node.add_suffix:
            otmn__lwal = str(cname) + join_node.suffix_x
        else:
            otmn__lwal = cname
        assert otmn__lwal in join_node.out_data_vars
        jchsi__rpee.append(join_node.out_data_vars[otmn__lwal])
    for i, cname in enumerate(join_node.right_keys):
        if not join_node.vect_same_key[i] and not join_node.is_join:
            if cname in join_node.add_suffix:
                otmn__lwal = str(cname) + join_node.suffix_y
            else:
                otmn__lwal = cname
            assert otmn__lwal in join_node.out_data_vars
            jchsi__rpee.append(join_node.out_data_vars[otmn__lwal])

    def _get_out_col_var(cname, is_left):
        if cname in join_node.add_suffix:
            if is_left:
                otmn__lwal = str(cname) + join_node.suffix_x
            else:
                otmn__lwal = str(cname) + join_node.suffix_y
        else:
            otmn__lwal = cname
        return join_node.out_data_vars[otmn__lwal]
    npna__vioaa = miurz__qijxt + tuple(jchsi__rpee)
    npna__vioaa += tuple(_get_out_col_var(mmfe__kyaoo, True) for 
        mmfe__kyaoo, xlpyy__dnbb in sorted(join_node.left_vars.items(), key
        =lambda a: str(a[0])) if mmfe__kyaoo not in join_node.left_keys)
    npna__vioaa += tuple(_get_out_col_var(mmfe__kyaoo, False) for 
        mmfe__kyaoo, xlpyy__dnbb in sorted(join_node.right_vars.items(),
        key=lambda a: str(a[0])) if mmfe__kyaoo not in join_node.right_keys)
    if join_node.indicator:
        npna__vioaa += _get_out_col_var('_merge', False),
    unhgl__qiv = [('t3_c' + str(i)) for i in range(len(npna__vioaa))]
    general_cond_cfunc, left_col_nums, right_col_nums = (
        _gen_general_cond_cfunc(join_node, typemap))
    if join_node.how == 'asof':
        if left_parallel or right_parallel:
            assert left_parallel and right_parallel
            func_text += """    t2_keys, data_right = parallel_asof_comm(t1_keys, t2_keys, data_right)
"""
        func_text += """    out_t1_keys, out_t2_keys, out_data_left, out_data_right = bodo.ir.join.local_merge_asof(t1_keys, t2_keys, data_left, data_right)
"""
    else:
        func_text += _gen_local_hash_join(optional_column, left_key_names,
            right_key_names, left_key_types, right_key_types,
            left_other_names, right_other_names, left_other_types,
            right_other_types, join_node.vect_same_key, join_node.is_left,
            join_node.is_right, join_node.is_join, left_parallel,
            right_parallel, glbs, [typemap[xlpyy__dnbb.name] for
            xlpyy__dnbb in npna__vioaa], join_node.loc, join_node.indicator,
            join_node.is_na_equal, general_cond_cfunc, left_col_nums,
            right_col_nums)
    if join_node.how == 'asof':
        for i in range(len(left_other_names)):
            func_text += '    left_{} = out_data_left[{}]\n'.format(i, i)
        for i in range(len(right_other_names)):
            func_text += '    right_{} = out_data_right[{}]\n'.format(i, i)
        for i in range(n_keys):
            func_text += f'    t1_keys_{i} = out_t1_keys[{i}]\n'
        for i in range(n_keys):
            func_text += f'    t2_keys_{i} = out_t2_keys[{i}]\n'
    idx = 0
    if optional_column:
        func_text += f'    {unhgl__qiv[idx]} = opti_0\n'
        idx += 1
    for i in range(n_keys):
        func_text += f'    {unhgl__qiv[idx]} = t1_keys_{i}\n'
        idx += 1
    for i in range(n_keys):
        if not join_node.vect_same_key[i] and not join_node.is_join:
            func_text += f'    {unhgl__qiv[idx]} = t2_keys_{i}\n'
            idx += 1
    for i in range(len(left_other_names)):
        func_text += f'    {unhgl__qiv[idx]} = left_{i}\n'
        idx += 1
    for i in range(len(right_other_names)):
        func_text += f'    {unhgl__qiv[idx]} = right_{i}\n'
        idx += 1
    if join_node.indicator:
        func_text += f'    {unhgl__qiv[idx]} = indicator_col\n'
        idx += 1
    grr__arsl = {}
    exec(func_text, {}, grr__arsl)
    juwrz__dhzdd = grr__arsl['f']
    glbs.update({'bodo': bodo, 'np': np, 'pd': pd,
        'to_list_if_immutable_arr': to_list_if_immutable_arr,
        'cp_str_list_to_array': cp_str_list_to_array, 'parallel_asof_comm':
        parallel_asof_comm, 'array_to_info': array_to_info,
        'arr_info_list_to_table': arr_info_list_to_table, 'hash_join_table':
        hash_join_table, 'info_from_table': info_from_table,
        'info_to_array': info_to_array, 'delete_table': delete_table,
        'delete_table_decref_arrays': delete_table_decref_arrays,
        'add_join_gen_cond_cfunc_sym': add_join_gen_cond_cfunc_sym,
        'get_join_cond_addr': get_join_cond_addr})
    if general_cond_cfunc:
        glbs.update({'general_cond_cfunc': general_cond_cfunc})
    xiu__komcs = compile_to_numba_ir(juwrz__dhzdd, glbs, typingctx=
        typingctx, targetctx=targetctx, arg_typs=qzib__dyt, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(xiu__komcs, ydx__fhf)
    mizm__nbqnn = xiu__komcs.body[:-3]
    for i in range(len(npna__vioaa)):
        mizm__nbqnn[-len(npna__vioaa) + i].target = npna__vioaa[i]
    return mizm__nbqnn


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    yoah__vcabo = next_label()
    xmjx__bzt = _get_col_to_ind(join_node.left_keys, join_node.left_vars)
    eict__xaosz = _get_col_to_ind(join_node.right_keys, join_node.right_vars)
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{yoah__vcabo}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
"""
    func_text += '  if is_null_pointer(left_table):\n'
    func_text += '    return False\n'
    expr, func_text, left_col_nums = _replace_column_accesses(expr,
        xmjx__bzt, typemap, join_node.left_vars, table_getitem_funcs,
        func_text, 'left', len(join_node.left_keys), na_check_name)
    expr, func_text, right_col_nums = _replace_column_accesses(expr,
        eict__xaosz, typemap, join_node.right_vars, table_getitem_funcs,
        func_text, 'right', len(join_node.right_keys), na_check_name)
    func_text += f'  return {expr}'
    grr__arsl = {}
    exec(func_text, table_getitem_funcs, grr__arsl)
    nwqnt__wxc = grr__arsl[f'bodo_join_gen_cond{yoah__vcabo}']
    cdr__kjcs = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    dikqg__kevb = numba.cfunc(cdr__kjcs, nopython=True)(nwqnt__wxc)
    join_gen_cond_cfunc[dikqg__kevb.native_name] = dikqg__kevb
    join_gen_cond_cfunc_addr[dikqg__kevb.native_name] = dikqg__kevb.address
    return dikqg__kevb, left_col_nums, right_col_nums


def _replace_column_accesses(expr, col_to_ind, typemap, col_vars,
    table_getitem_funcs, func_text, table_name, n_keys, na_check_name):
    gld__zff = []
    for ynwd__scc, gri__qbt in col_to_ind.items():
        cname = f'({table_name}.{ynwd__scc})'
        if cname not in expr:
            continue
        qcbdl__pjsvm = f'getitem_{table_name}_val_{gri__qbt}'
        lzh__czysk = f'_bodo_{table_name}_val_{gri__qbt}'
        pngl__pivx = typemap[col_vars[ynwd__scc].name].dtype
        if pngl__pivx == types.unicode_type:
            func_text += f"""  {lzh__czysk}, {lzh__czysk}_size = {qcbdl__pjsvm}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {lzh__czysk} = bodo.libs.str_arr_ext.decode_utf8({lzh__czysk}, {lzh__czysk}_size)
"""
        else:
            func_text += (
                f'  {lzh__czysk} = {qcbdl__pjsvm}({table_name}_data1, {table_name}_ind)\n'
                )
        table_getitem_funcs[qcbdl__pjsvm
            ] = bodo.libs.array._gen_row_access_intrinsic(pngl__pivx, gri__qbt)
        expr = expr.replace(cname, lzh__czysk)
        pnwz__xcp = f'({na_check_name}.{table_name}.{ynwd__scc})'
        if pnwz__xcp in expr:
            lfzrj__nfxyl = typemap[col_vars[ynwd__scc].name]
            zrvy__dzek = f'nacheck_{table_name}_val_{gri__qbt}'
            kux__ktl = f'_bodo_isna_{table_name}_val_{gri__qbt}'
            if isinstance(lfzrj__nfxyl, bodo.libs.int_arr_ext.IntegerArrayType
                ) or lfzrj__nfxyl in [bodo.libs.bool_arr_ext.boolean_array,
                bodo.libs.str_arr_ext.string_array_type]:
                func_text += f"""  {kux__ktl} = {zrvy__dzek}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += (
                    f'  {kux__ktl} = {zrvy__dzek}({table_name}_data1, {table_name}_ind)\n'
                    )
            table_getitem_funcs[zrvy__dzek
                ] = bodo.libs.array._gen_row_na_check_intrinsic(lfzrj__nfxyl,
                gri__qbt)
            expr = expr.replace(pnwz__xcp, kux__ktl)
        if gri__qbt >= n_keys:
            gld__zff.append(gri__qbt)
    return expr, func_text, gld__zff


def _get_col_to_ind(key_names, col_vars):
    n_keys = len(key_names)
    col_to_ind = {ynwd__scc: i for i, ynwd__scc in enumerate(key_names)}
    i = n_keys
    for ynwd__scc in sorted(col_vars, key=lambda a: str(a)):
        if ynwd__scc in key_names:
            continue
        col_to_ind[ynwd__scc] = i
        i += 1
    return col_to_ind


def _match_join_key_types(t1, t2, loc):
    if t1 == t2:
        return t1
    try:
        arr = dtype_to_array_type(find_common_np_dtype([t1, t2]))
        return to_nullable_type(arr) if is_nullable_type(t1
            ) or is_nullable_type(t2) else arr
    except:
        raise BodoError(f'Join key types {t1} and {t2} do not match', loc=loc)


def _get_table_parallel_flags(join_node, array_dists):
    nzao__ihcy = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[xlpyy__dnbb.name] in nzao__ihcy for
        xlpyy__dnbb in join_node.left_vars.values())
    right_parallel = all(array_dists[xlpyy__dnbb.name] in nzao__ihcy for
        xlpyy__dnbb in join_node.right_vars.values())
    if not left_parallel:
        assert not any(array_dists[xlpyy__dnbb.name] in nzao__ihcy for
            xlpyy__dnbb in join_node.left_vars.values())
    if not right_parallel:
        assert not any(array_dists[xlpyy__dnbb.name] in nzao__ihcy for
            xlpyy__dnbb in join_node.right_vars.values())
    if left_parallel or right_parallel:
        assert all(array_dists[xlpyy__dnbb.name] in nzao__ihcy for
            xlpyy__dnbb in join_node.out_data_vars.values())
    return left_parallel, right_parallel


def _gen_local_hash_join(optional_column, left_key_names, right_key_names,
    left_key_types, right_key_types, left_other_names, right_other_names,
    left_other_types, right_other_types, vect_same_key, is_left, is_right,
    is_join, left_parallel, right_parallel, glbs, out_types, loc, indicator,
    is_na_equal, general_cond_cfunc, left_col_nums, right_col_nums):

    def needs_typechange(in_type, need_nullable, is_same_key):
        return isinstance(in_type, types.Array) and not is_dtype_nullable(
            in_type.dtype) and need_nullable and not is_same_key
    ewptn__jsa = []
    for i in range(len(left_key_names)):
        lxn__ypotm = _match_join_key_types(left_key_types[i],
            right_key_types[i], loc)
        ewptn__jsa.append(needs_typechange(lxn__ypotm, is_right,
            vect_same_key[i]))
    for i in range(len(left_other_names)):
        ewptn__jsa.append(needs_typechange(left_other_types[i], is_right, 
            False))
    for i in range(len(right_key_names)):
        if not vect_same_key[i] and not is_join:
            lxn__ypotm = _match_join_key_types(left_key_types[i],
                right_key_types[i], loc)
            ewptn__jsa.append(needs_typechange(lxn__ypotm, is_left, False))
    for i in range(len(right_other_names)):
        ewptn__jsa.append(needs_typechange(right_other_types[i], is_left, 
            False))

    def get_out_type(idx, in_type, in_name, need_nullable, is_same_key):
        if isinstance(in_type, types.Array) and not is_dtype_nullable(in_type
            .dtype) and need_nullable and not is_same_key:
            if isinstance(in_type.dtype, types.Integer):
                dqcf__ivjy = IntDtype(in_type.dtype).name
                assert dqcf__ivjy.endswith('Dtype()')
                dqcf__ivjy = dqcf__ivjy[:-7]
                tni__uklpf = f"""    typ_{idx} = bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype="{dqcf__ivjy}"))
"""
                xayt__oxi = f'typ_{idx}'
            else:
                assert in_type.dtype == types.bool_, 'unexpected non-nullable type in join'
                tni__uklpf = (
                    f'    typ_{idx} = bodo.libs.bool_arr_ext.alloc_bool_array(1)\n'
                    )
                xayt__oxi = f'typ_{idx}'
        else:
            tni__uklpf = ''
            xayt__oxi = in_name
        return tni__uklpf, xayt__oxi
    n_keys = len(left_key_names)
    func_text = '    # beginning of _gen_local_hash_join\n'
    lrosk__jyluy = []
    for i in range(n_keys):
        lrosk__jyluy.append('t1_keys[{}]'.format(i))
    for i in range(len(left_other_names)):
        lrosk__jyluy.append('data_left[{}]'.format(i))
    func_text += '    info_list_total_l = [{}]\n'.format(','.join(
        'array_to_info({})'.format(a) for a in lrosk__jyluy))
    func_text += '    table_left = arr_info_list_to_table(info_list_total_l)\n'
    fnnv__lti = []
    for i in range(n_keys):
        fnnv__lti.append('t2_keys[{}]'.format(i))
    for i in range(len(right_other_names)):
        fnnv__lti.append('data_right[{}]'.format(i))
    func_text += '    info_list_total_r = [{}]\n'.format(','.join(
        'array_to_info({})'.format(a) for a in fnnv__lti))
    func_text += (
        '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    func_text += '    vect_same_key = np.array([{}])\n'.format(','.join('1' if
        ajsz__huvrx else '0' for ajsz__huvrx in vect_same_key))
    func_text += '    vect_need_typechange = np.array([{}])\n'.format(','.
        join('1' if ajsz__huvrx else '0' for ajsz__huvrx in ewptn__jsa))
    func_text += f"""    left_table_cond_columns = np.array({left_col_nums if len(left_col_nums) > 0 else [-1]}, dtype=np.int64)
"""
    func_text += f"""    right_table_cond_columns = np.array({right_col_nums if len(right_col_nums) > 0 else [-1]}, dtype=np.int64)
"""
    if general_cond_cfunc:
        func_text += f"""    cfunc_cond = add_join_gen_cond_cfunc_sym(general_cond_cfunc, '{general_cond_cfunc.native_name}')
"""
        func_text += (
            f"    cfunc_cond = get_join_cond_addr('{general_cond_cfunc.native_name}')\n"
            )
    else:
        func_text += '    cfunc_cond = 0\n'
    func_text += (
        """    out_table = hash_join_table(table_left, table_right, {}, {}, {}, {}, {}, vect_same_key.ctypes, vect_need_typechange.ctypes, {}, {}, {}, {}, {}, {}, cfunc_cond, left_table_cond_columns.ctypes, {}, right_table_cond_columns.ctypes, {})
"""
        .format(left_parallel, right_parallel, n_keys, len(left_other_names
        ), len(right_other_names), is_left, is_right, is_join,
        optional_column, indicator, is_na_equal, len(left_col_nums), len(
        right_col_nums)))
    func_text += '    delete_table(table_left)\n'
    func_text += '    delete_table(table_right)\n'
    idx = 0
    if optional_column:
        func_text += (
            f'    opti_0 = info_to_array(info_from_table(out_table, {idx}), opti_c0)\n'
            )
        idx += 1
    for i, cos__ixmf in enumerate(left_key_names):
        lxn__ypotm = _match_join_key_types(left_key_types[i],
            right_key_types[i], loc)
        xbqe__fehcm = get_out_type(idx, lxn__ypotm, f't1_keys[{i}]',
            is_right, vect_same_key[i])
        func_text += xbqe__fehcm[0]
        glbs[f'out_type_{idx}'] = out_types[idx]
        if lxn__ypotm != left_key_types[i]:
            func_text += f"""    t1_keys_{i} = bodo.utils.utils.astype(info_to_array(info_from_table(out_table, {idx}), {xbqe__fehcm[1]}), out_type_{idx})
"""
        else:
            func_text += f"""    t1_keys_{i} = info_to_array(info_from_table(out_table, {idx}), {xbqe__fehcm[1]})
"""
        idx += 1
    for i, cos__ixmf in enumerate(left_other_names):
        xbqe__fehcm = get_out_type(idx, left_other_types[i], cos__ixmf,
            is_right, False)
        func_text += xbqe__fehcm[0]
        func_text += (
            '    left_{} = info_to_array(info_from_table(out_table, {}), {})\n'
            .format(i, idx, xbqe__fehcm[1]))
        idx += 1
    for i, cos__ixmf in enumerate(right_key_names):
        if not vect_same_key[i] and not is_join:
            lxn__ypotm = _match_join_key_types(left_key_types[i],
                right_key_types[i], loc)
            xbqe__fehcm = get_out_type(idx, lxn__ypotm, f't2_keys[{i}]',
                is_left, False)
            func_text += xbqe__fehcm[0]
            glbs[f'out_type_{idx}'] = out_types[idx - len(left_other_names)]
            if lxn__ypotm != right_key_types[i]:
                func_text += f"""    t2_keys_{i} = bodo.utils.utils.astype(info_to_array(info_from_table(out_table, {idx}), {xbqe__fehcm[1]}), out_type_{idx})
"""
            else:
                func_text += f"""    t2_keys_{i} = info_to_array(info_from_table(out_table, {idx}), {xbqe__fehcm[1]})
"""
            idx += 1
    for i, cos__ixmf in enumerate(right_other_names):
        xbqe__fehcm = get_out_type(idx, right_other_types[i], cos__ixmf,
            is_left, False)
        func_text += xbqe__fehcm[0]
        func_text += (
            '    right_{} = info_to_array(info_from_table(out_table, {}), {})\n'
            .format(i, idx, xbqe__fehcm[1]))
        idx += 1
    if indicator:
        func_text += f"""    typ_{idx} = pd.Categorical(values=['both'], categories=('left_only', 'right_only', 'both'))
"""
        func_text += f"""    indicator_col = info_to_array(info_from_table(out_table, {idx}), typ_{idx})
"""
        idx += 1
    func_text += '    delete_table(out_table)\n'
    return func_text


def parallel_join_impl(key_arrs, data):
    phhk__ymict = bodo.libs.distributed_api.get_size()
    ckg__pcvd = alloc_pre_shuffle_metadata(key_arrs, data, phhk__ymict, False)
    mmfe__kyaoo = len(key_arrs[0])
    pcyk__fwbbw = np.empty(mmfe__kyaoo, np.int32)
    eabfc__ehae = arr_info_list_to_table([array_to_info(key_arrs[0])])
    mhjjk__mkl = 1
    nvh__fiaj = compute_node_partition_by_hash(eabfc__ehae, mhjjk__mkl,
        phhk__ymict)
    wsto__ypwu = np.empty(1, np.int32)
    qcpfc__fkbux = info_to_array(info_from_table(nvh__fiaj, 0), wsto__ypwu)
    delete_table(nvh__fiaj)
    delete_table(eabfc__ehae)
    for i in range(mmfe__kyaoo):
        val = getitem_arr_tup_single(key_arrs, i)
        node_id = qcpfc__fkbux[i]
        pcyk__fwbbw[i] = node_id
        update_shuffle_meta(ckg__pcvd, node_id, i, key_arrs, data, False)
    shuffle_meta = finalize_shuffle_meta(key_arrs, data, ckg__pcvd,
        phhk__ymict, False)
    for i in range(mmfe__kyaoo):
        node_id = pcyk__fwbbw[i]
        write_send_buff(shuffle_meta, node_id, i, key_arrs, data)
        shuffle_meta.tmp_offset[node_id] += 1
    qbbie__azea = alltoallv_tup(key_arrs + data, shuffle_meta, key_arrs)
    jchsi__rpee = _get_keys_tup(qbbie__azea, key_arrs)
    ads__ncx = _get_data_tup(qbbie__azea, key_arrs)
    return jchsi__rpee, ads__ncx


@generated_jit(nopython=True, cache=True)
def parallel_shuffle(key_arrs, data):
    return parallel_join_impl


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    phhk__ymict = bodo.libs.distributed_api.get_size()
    ivv__afx = np.empty(phhk__ymict, left_key_arrs[0].dtype)
    bpcx__jirdz = np.empty(phhk__ymict, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(ivv__afx, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(bpcx__jirdz, left_key_arrs[0][-1])
    deqmx__trpwz = np.zeros(phhk__ymict, np.int32)
    ozno__ayclp = np.zeros(phhk__ymict, np.int32)
    ghxjt__irb = np.zeros(phhk__ymict, np.int32)
    efbd__rql = right_key_arrs[0][0]
    flw__waql = right_key_arrs[0][-1]
    smug__zraad = -1
    i = 0
    while i < phhk__ymict - 1 and bpcx__jirdz[i] < efbd__rql:
        i += 1
    while i < phhk__ymict and ivv__afx[i] <= flw__waql:
        smug__zraad, hpmfk__jwh = _count_overlap(right_key_arrs[0],
            ivv__afx[i], bpcx__jirdz[i])
        if smug__zraad != 0:
            smug__zraad -= 1
            hpmfk__jwh += 1
        deqmx__trpwz[i] = hpmfk__jwh
        ozno__ayclp[i] = smug__zraad
        i += 1
    while i < phhk__ymict:
        deqmx__trpwz[i] = 1
        ozno__ayclp[i] = len(right_key_arrs[0]) - 1
        i += 1
    bodo.libs.distributed_api.alltoall(deqmx__trpwz, ghxjt__irb, 1)
    ymwp__lsh = ghxjt__irb.sum()
    zggc__mmnh = np.empty(ymwp__lsh, right_key_arrs[0].dtype)
    ifrci__anko = alloc_arr_tup(ymwp__lsh, right_data)
    auovp__peib = bodo.ir.join.calc_disp(ghxjt__irb)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], zggc__mmnh,
        deqmx__trpwz, ghxjt__irb, ozno__ayclp, auovp__peib)
    bodo.libs.distributed_api.alltoallv_tup(right_data, ifrci__anko,
        deqmx__trpwz, ghxjt__irb, ozno__ayclp, auovp__peib)
    return (zggc__mmnh,), ifrci__anko


@numba.njit
def _count_overlap(r_key_arr, start, end):
    hpmfk__jwh = 0
    smug__zraad = 0
    lou__mry = 0
    while lou__mry < len(r_key_arr) and r_key_arr[lou__mry] < start:
        smug__zraad += 1
        lou__mry += 1
    while lou__mry < len(r_key_arr) and start <= r_key_arr[lou__mry] <= end:
        lou__mry += 1
        hpmfk__jwh += 1
    return smug__zraad, hpmfk__jwh


def write_send_buff(shuffle_meta, node_id, i, key_arrs, data):
    return i


@overload(write_send_buff, no_unliteral=True)
def write_data_buff_overload(meta, node_id, i, key_arrs, data):
    func_text = 'def f(meta, node_id, i, key_arrs, data):\n'
    func_text += (
        '  w_ind = meta.send_disp[node_id] + meta.tmp_offset[node_id]\n')
    n_keys = len(key_arrs.types)
    for i, lpbw__ehh in enumerate(key_arrs.types + data.types):
        arr = 'key_arrs[{}]'.format(i) if i < n_keys else 'data[{}]'.format(
            i - n_keys)
        if not lpbw__ehh in (string_type, string_array_type,
            binary_array_type, bytes_type):
            func_text += '  meta.send_buff_tup[{}][w_ind] = {}[i]\n'.format(i,
                arr)
        else:
            func_text += ('  n_chars_{} = get_str_arr_item_length({}, i)\n'
                .format(i, arr))
            func_text += ('  meta.send_arr_lens_tup[{}][w_ind] = n_chars_{}\n'
                .format(i, i))
            if i >= n_keys:
                func_text += (
                    """  out_bitmap = meta.send_arr_nulls_tup[{}][meta.send_disp_nulls[node_id]:].ctypes
"""
                    .format(i))
                func_text += (
                    '  bit_val = get_bit_bitmap(get_null_bitmap_ptr(data[{}]), i)\n'
                    .format(i - n_keys))
                func_text += (
                    '  set_bit_to(out_bitmap, meta.tmp_offset[node_id], bit_val)\n'
                    )
            func_text += (
                """  indc_{} = meta.send_disp_char_tup[{}][node_id] + meta.tmp_offset_char_tup[{}][node_id]
"""
                .format(i, i, i))
            func_text += ('  item_ptr_{} = get_str_arr_item_ptr({}, i)\n'.
                format(i, arr))
            func_text += (
                """  str_copy_ptr(meta.send_arr_chars_tup[{}], indc_{}, item_ptr_{}, n_chars_{})
"""
                .format(i, i, i, i))
            func_text += (
                '  meta.tmp_offset_char_tup[{}][node_id] += n_chars_{}\n'.
                format(i, i))
    func_text += '  return w_ind\n'
    grr__arsl = {}
    exec(func_text, {'str_copy_ptr': str_copy_ptr, 'get_null_bitmap_ptr':
        get_null_bitmap_ptr, 'get_bit_bitmap': get_bit_bitmap, 'set_bit_to':
        set_bit_to, 'get_str_arr_item_length': get_str_arr_item_length,
        'get_str_arr_item_ptr': get_str_arr_item_ptr}, grr__arsl)
    piqdn__whtz = grr__arsl['f']
    return piqdn__whtz


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    ehsnd__oidj = np.empty_like(arr)
    ehsnd__oidj[0] = 0
    for i in range(1, len(arr)):
        ehsnd__oidj[i] = ehsnd__oidj[i - 1] + arr[i - 1]
    return ehsnd__oidj


def ensure_capacity(arr, new_size):
    hyyjr__tgx = arr
    mkmf__fab = len(arr)
    if mkmf__fab < new_size:
        xcwtd__gqusm = 2 * mkmf__fab
        hyyjr__tgx = bodo.utils.utils.alloc_type(xcwtd__gqusm, arr)
        hyyjr__tgx[:mkmf__fab] = arr
    return hyyjr__tgx


@overload(ensure_capacity, no_unliteral=True)
def ensure_capacity_overload(arr, new_size):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return ensure_capacity
    assert isinstance(arr, types.BaseTuple)
    hpmfk__jwh = arr.count
    func_text = 'def f(arr, new_size):\n'
    func_text += '  return ({}{})\n'.format(','.join([
        'ensure_capacity(arr[{}], new_size)'.format(i) for i in range(
        hpmfk__jwh)]), ',' if hpmfk__jwh == 1 else '')
    grr__arsl = {}
    exec(func_text, {'ensure_capacity': ensure_capacity}, grr__arsl)
    dkzqs__eraip = grr__arsl['f']
    return dkzqs__eraip


@numba.njit
def ensure_capacity_str(arr, new_size, n_chars):
    hyyjr__tgx = arr
    mkmf__fab = len(arr)
    grq__fbzbx = num_total_chars(arr)
    bup__kcpbg = getitem_str_offset(arr, new_size - 1) + n_chars
    if mkmf__fab < new_size or bup__kcpbg > grq__fbzbx:
        xcwtd__gqusm = int(2 * mkmf__fab if mkmf__fab < new_size else mkmf__fab
            )
        fjpg__etiw = int(2 * grq__fbzbx + n_chars if bup__kcpbg >
            grq__fbzbx else grq__fbzbx)
        hyyjr__tgx = pre_alloc_string_array(xcwtd__gqusm, fjpg__etiw)
        copy_str_arr_slice(hyyjr__tgx, arr, new_size - 1)
    return hyyjr__tgx


def trim_arr_tup(data, new_size):
    return data


@overload(trim_arr_tup, no_unliteral=True)
def trim_arr_tup_overload(data, new_size):
    assert isinstance(data, types.BaseTuple)
    hpmfk__jwh = data.count
    func_text = 'def f(data, new_size):\n'
    func_text += '  return ({}{})\n'.format(','.join([
        'trim_arr(data[{}], new_size)'.format(i) for i in range(hpmfk__jwh)
        ]), ',' if hpmfk__jwh == 1 else '')
    grr__arsl = {}
    exec(func_text, {'trim_arr': trim_arr}, grr__arsl)
    dkzqs__eraip = grr__arsl['f']
    return dkzqs__eraip


def copy_elem_buff(arr, ind, val):
    hyyjr__tgx = ensure_capacity(arr, ind + 1)
    hyyjr__tgx[ind] = val
    return hyyjr__tgx


@overload(copy_elem_buff, no_unliteral=True)
def copy_elem_buff_overload(arr, ind, val):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return copy_elem_buff
    assert arr == string_array_type

    def copy_elem_buff_str(arr, ind, val):
        hyyjr__tgx = ensure_capacity_str(arr, ind + 1, get_utf8_size(val))
        hyyjr__tgx[ind] = val
        return hyyjr__tgx
    return copy_elem_buff_str


def copy_elem_buff_tup(arr, ind, val):
    return arr


@overload(copy_elem_buff_tup, no_unliteral=True)
def copy_elem_buff_tup_overload(data, ind, val):
    assert isinstance(data, types.BaseTuple)
    hpmfk__jwh = data.count
    func_text = 'def f(data, ind, val):\n'
    for i in range(hpmfk__jwh):
        func_text += ('  arr_{} = copy_elem_buff(data[{}], ind, val[{}])\n'
            .format(i, i, i))
    func_text += '  return ({}{})\n'.format(','.join(['arr_{}'.format(i) for
        i in range(hpmfk__jwh)]), ',' if hpmfk__jwh == 1 else '')
    grr__arsl = {}
    exec(func_text, {'copy_elem_buff': copy_elem_buff}, grr__arsl)
    obad__vpls = grr__arsl['f']
    return obad__vpls


def trim_arr(arr, size):
    return arr[:size]


@overload(trim_arr, no_unliteral=True)
def trim_arr_overload(arr, size):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return trim_arr
    assert arr == string_array_type

    def trim_arr_str(arr, size):
        hyyjr__tgx = pre_alloc_string_array(size, np.int64(
            getitem_str_offset(arr, size)))
        copy_str_arr_slice(hyyjr__tgx, arr, size)
        return hyyjr__tgx
    return trim_arr_str


def setnan_elem_buff(arr, ind):
    hyyjr__tgx = ensure_capacity(arr, ind + 1)
    bodo.libs.array_kernels.setna(hyyjr__tgx, ind)
    return hyyjr__tgx


@overload(setnan_elem_buff, no_unliteral=True)
def setnan_elem_buff_overload(arr, ind):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return setnan_elem_buff
    assert arr == string_array_type

    def setnan_elem_buff_str(arr, ind):
        hyyjr__tgx = ensure_capacity_str(arr, ind + 1, 0)
        hyyjr__tgx[ind] = ''
        bodo.libs.array_kernels.setna(hyyjr__tgx, ind)
        return hyyjr__tgx
    return setnan_elem_buff_str


def setnan_elem_buff_tup(arr, ind):
    return arr


@overload(setnan_elem_buff_tup, no_unliteral=True)
def setnan_elem_buff_tup_overload(data, ind):
    assert isinstance(data, types.BaseTuple)
    hpmfk__jwh = data.count
    func_text = 'def f(data, ind):\n'
    for i in range(hpmfk__jwh):
        func_text += '  arr_{} = setnan_elem_buff(data[{}], ind)\n'.format(i, i
            )
    func_text += '  return ({}{})\n'.format(','.join(['arr_{}'.format(i) for
        i in range(hpmfk__jwh)]), ',' if hpmfk__jwh == 1 else '')
    grr__arsl = {}
    exec(func_text, {'setnan_elem_buff': setnan_elem_buff}, grr__arsl)
    obad__vpls = grr__arsl['f']
    return obad__vpls


@generated_jit(nopython=True, cache=True)
def _check_ind_if_hashed(right_keys, r_ind, l_key):
    if right_keys == types.Tuple((types.intp[::1],)):
        return lambda right_keys, r_ind, l_key: r_ind

    def _impl(right_keys, r_ind, l_key):
        wuugv__ubuqw = getitem_arr_tup(right_keys, r_ind)
        if wuugv__ubuqw != l_key:
            return -1
        return r_ind
    return _impl


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    erxqw__fjuzm = len(left_keys[0])
    nou__qcp = len(right_keys[0])
    gbcc__yss = alloc_arr_tup(erxqw__fjuzm, left_keys)
    myv__djkn = alloc_arr_tup(erxqw__fjuzm, right_keys)
    grwa__ojxom = alloc_arr_tup(erxqw__fjuzm, data_left)
    mwq__wwi = alloc_arr_tup(erxqw__fjuzm, data_right)
    pacep__kszdu = 0
    dgnf__wxbgb = 0
    for pacep__kszdu in range(erxqw__fjuzm):
        if dgnf__wxbgb < 0:
            dgnf__wxbgb = 0
        while dgnf__wxbgb < nou__qcp and getitem_arr_tup(right_keys,
            dgnf__wxbgb) <= getitem_arr_tup(left_keys, pacep__kszdu):
            dgnf__wxbgb += 1
        dgnf__wxbgb -= 1
        setitem_arr_tup(gbcc__yss, pacep__kszdu, getitem_arr_tup(left_keys,
            pacep__kszdu))
        setitem_arr_tup(grwa__ojxom, pacep__kszdu, getitem_arr_tup(
            data_left, pacep__kszdu))
        if dgnf__wxbgb >= 0:
            setitem_arr_tup(myv__djkn, pacep__kszdu, getitem_arr_tup(
                right_keys, dgnf__wxbgb))
            setitem_arr_tup(mwq__wwi, pacep__kszdu, getitem_arr_tup(
                data_right, dgnf__wxbgb))
        else:
            bodo.libs.array_kernels.setna_tup(myv__djkn, pacep__kszdu)
            bodo.libs.array_kernels.setna_tup(mwq__wwi, pacep__kszdu)
    return gbcc__yss, myv__djkn, grwa__ojxom, mwq__wwi


def copy_arr_tup(arrs):
    return tuple(a.copy() for a in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    hpmfk__jwh = arrs.count
    func_text = 'def f(arrs):\n'
    func_text += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(hpmfk__jwh)))
    grr__arsl = {}
    exec(func_text, {}, grr__arsl)
    impl = grr__arsl['f']
    return impl


def get_nan_bits(arr, ind):
    return 0


@overload(get_nan_bits, no_unliteral=True)
def overload_get_nan_bits(arr, ind):
    if arr == string_array_type:

        def impl_str(arr, ind):
            degi__ogzt = get_null_bitmap_ptr(arr)
            return get_bit_bitmap(degi__ogzt, ind)
        return impl_str
    if isinstance(arr, IntegerArrayType) or arr == boolean_array:

        def impl(arr, ind):
            return bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr.
                _null_bitmap, ind)
        return impl
    return lambda arr, ind: False


def get_nan_bits_tup(arr_tup, ind):
    return tuple(get_nan_bits(arr, ind) for arr in arr_tup)


@overload(get_nan_bits_tup, no_unliteral=True)
def overload_get_nan_bits_tup(arr_tup, ind):
    hpmfk__jwh = arr_tup.count
    func_text = 'def f(arr_tup, ind):\n'
    func_text += '  return ({}{})\n'.format(','.join([
        'get_nan_bits(arr_tup[{}], ind)'.format(i) for i in range(
        hpmfk__jwh)]), ',' if hpmfk__jwh == 1 else '')
    grr__arsl = {}
    exec(func_text, {'get_nan_bits': get_nan_bits}, grr__arsl)
    impl = grr__arsl['f']
    return impl


def set_nan_bits(arr, ind, na_val):
    return 0


@overload(set_nan_bits, no_unliteral=True)
def overload_set_nan_bits(arr, ind, na_val):
    if arr == string_array_type:

        def impl_str(arr, ind, na_val):
            degi__ogzt = get_null_bitmap_ptr(arr)
            set_bit_to(degi__ogzt, ind, na_val)
        return impl_str
    if isinstance(arr, IntegerArrayType) or arr == boolean_array:

        def impl(arr, ind, na_val):
            bodo.libs.int_arr_ext.set_bit_to_arr(arr._null_bitmap, ind, na_val)
        return impl
    return lambda arr, ind, na_val: None


def set_nan_bits_tup(arr_tup, ind, na_val):
    return tuple(set_nan_bits(arr, ind, na_val) for arr in arr_tup)


@overload(set_nan_bits_tup, no_unliteral=True)
def overload_set_nan_bits_tup(arr_tup, ind, na_val):
    hpmfk__jwh = arr_tup.count
    func_text = 'def f(arr_tup, ind, na_val):\n'
    for i in range(hpmfk__jwh):
        func_text += '  set_nan_bits(arr_tup[{}], ind, na_val[{}])\n'.format(i,
            i)
    func_text += '  return\n'
    grr__arsl = {}
    exec(func_text, {'set_nan_bits': set_nan_bits}, grr__arsl)
    impl = grr__arsl['f']
    return impl
