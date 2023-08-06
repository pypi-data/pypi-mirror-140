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
        utlq__psng = func.signature
        uyyrq__pfpo = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        saveh__qxqmm = cgutils.get_or_insert_function(builder.module,
            uyyrq__pfpo, sym._literal_value)
        builder.call(saveh__qxqmm, [context.get_constant_null(utlq__psng.
            args[0]), context.get_constant_null(utlq__psng.args[1]),
            context.get_constant_null(utlq__psng.args[2]), context.
            get_constant_null(utlq__psng.args[3]), context.
            get_constant_null(utlq__psng.args[4]), context.
            get_constant_null(utlq__psng.args[5]), context.get_constant(
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
        self.left_cond_cols = set(vvd__unr for vvd__unr in left_vars.keys() if
            f'(left.{vvd__unr})' in gen_cond_expr)
        self.right_cond_cols = set(vvd__unr for vvd__unr in right_vars.keys
            () if f'(right.{vvd__unr})' in gen_cond_expr)
        rjycc__vvqis = set(left_keys) & set(right_keys)
        vwqk__fap = set(left_vars.keys()) & set(right_vars.keys())
        vhqhq__ntnxe = vwqk__fap - rjycc__vvqis
        vect_same_key = []
        n_keys = len(left_keys)
        for tvys__nnml in range(n_keys):
            hndgb__nidlq = left_keys[tvys__nnml]
            jbcn__xqaw = right_keys[tvys__nnml]
            vect_same_key.append(hndgb__nidlq == jbcn__xqaw)
        self.vect_same_key = vect_same_key
        self.column_origins = {(str(vvd__unr) + suffix_x if vvd__unr in
            vhqhq__ntnxe else vvd__unr): ('left', vvd__unr) for vvd__unr in
            left_vars.keys()}
        self.column_origins.update({(str(vvd__unr) + suffix_y if vvd__unr in
            vhqhq__ntnxe else vvd__unr): ('right', vvd__unr) for vvd__unr in
            right_vars.keys()})
        if '$_bodo_index_' in vhqhq__ntnxe:
            vhqhq__ntnxe.remove('$_bodo_index_')
        self.add_suffix = vhqhq__ntnxe

    def __repr__(self):
        snal__yol = ''
        for vvd__unr, xlda__alztm in self.out_data_vars.items():
            snal__yol += "'{}':{}, ".format(vvd__unr, xlda__alztm.name)
        ygi__wffbe = '{}{{{}}}'.format(self.df_out, snal__yol)
        hch__woim = ''
        for vvd__unr, xlda__alztm in self.left_vars.items():
            hch__woim += "'{}':{}, ".format(vvd__unr, xlda__alztm.name)
        xhdu__xygl = '{}{{{}}}'.format(self.left_df, hch__woim)
        hch__woim = ''
        for vvd__unr, xlda__alztm in self.right_vars.items():
            hch__woim += "'{}':{}, ".format(vvd__unr, xlda__alztm.name)
        llfz__zci = '{}{{{}}}'.format(self.right_df, hch__woim)
        return 'join [{}={}]: {} , {}, {}'.format(self.left_keys, self.
            right_keys, ygi__wffbe, xhdu__xygl, llfz__zci)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    zzv__ugdnh = []
    assert len(join_node.out_data_vars) > 0, 'empty join in array analysis'
    nxv__iztrw = []
    nwntq__glb = list(join_node.left_vars.values())
    for nmd__ijo in nwntq__glb:
        dfev__fjwje = typemap[nmd__ijo.name]
        ryxb__gdj = equiv_set.get_shape(nmd__ijo)
        if ryxb__gdj:
            nxv__iztrw.append(ryxb__gdj[0])
    if len(nxv__iztrw) > 1:
        equiv_set.insert_equiv(*nxv__iztrw)
    nxv__iztrw = []
    nwntq__glb = list(join_node.right_vars.values())
    for nmd__ijo in nwntq__glb:
        dfev__fjwje = typemap[nmd__ijo.name]
        ryxb__gdj = equiv_set.get_shape(nmd__ijo)
        if ryxb__gdj:
            nxv__iztrw.append(ryxb__gdj[0])
    if len(nxv__iztrw) > 1:
        equiv_set.insert_equiv(*nxv__iztrw)
    nxv__iztrw = []
    for nmd__ijo in join_node.out_data_vars.values():
        dfev__fjwje = typemap[nmd__ijo.name]
        yit__uyqwi = array_analysis._gen_shape_call(equiv_set, nmd__ijo,
            dfev__fjwje.ndim, None, zzv__ugdnh)
        equiv_set.insert_equiv(nmd__ijo, yit__uyqwi)
        nxv__iztrw.append(yit__uyqwi[0])
        equiv_set.define(nmd__ijo, set())
    if len(nxv__iztrw) > 1:
        equiv_set.insert_equiv(*nxv__iztrw)
    return [], zzv__ugdnh


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    cooc__krc = Distribution.OneD
    nbq__vytb = Distribution.OneD
    for nmd__ijo in join_node.left_vars.values():
        cooc__krc = Distribution(min(cooc__krc.value, array_dists[nmd__ijo.
            name].value))
    for nmd__ijo in join_node.right_vars.values():
        nbq__vytb = Distribution(min(nbq__vytb.value, array_dists[nmd__ijo.
            name].value))
    acvf__pbyc = Distribution.OneD_Var
    for nmd__ijo in join_node.out_data_vars.values():
        if nmd__ijo.name in array_dists:
            acvf__pbyc = Distribution(min(acvf__pbyc.value, array_dists[
                nmd__ijo.name].value))
    hnp__abhge = Distribution(min(acvf__pbyc.value, cooc__krc.value))
    upi__jehv = Distribution(min(acvf__pbyc.value, nbq__vytb.value))
    acvf__pbyc = Distribution(max(hnp__abhge.value, upi__jehv.value))
    for nmd__ijo in join_node.out_data_vars.values():
        array_dists[nmd__ijo.name] = acvf__pbyc
    if acvf__pbyc != Distribution.OneD_Var:
        cooc__krc = acvf__pbyc
        nbq__vytb = acvf__pbyc
    for nmd__ijo in join_node.left_vars.values():
        array_dists[nmd__ijo.name] = cooc__krc
    for nmd__ijo in join_node.right_vars.values():
        array_dists[nmd__ijo.name] = nbq__vytb
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def join_typeinfer(join_node, typeinferer):
    rjycc__vvqis = set(join_node.left_keys) & set(join_node.right_keys)
    vwqk__fap = set(join_node.left_vars.keys()) & set(join_node.right_vars.
        keys())
    vhqhq__ntnxe = vwqk__fap - rjycc__vvqis
    for cmsk__dym, lch__lyuas in join_node.out_data_vars.items():
        if join_node.indicator and cmsk__dym == '_merge':
            continue
        if not cmsk__dym in join_node.column_origins:
            raise BodoError('join(): The variable ' + cmsk__dym +
                ' is absent from the output')
        roelg__udbrq = join_node.column_origins[cmsk__dym]
        if roelg__udbrq[0] == 'left':
            nmd__ijo = join_node.left_vars[roelg__udbrq[1]]
        else:
            nmd__ijo = join_node.right_vars[roelg__udbrq[1]]
        typeinferer.constraints.append(typeinfer.Propagate(dst=lch__lyuas.
            name, src=nmd__ijo.name, loc=join_node.loc))
    return


typeinfer.typeinfer_extensions[Join] = join_typeinfer


def visit_vars_join(join_node, callback, cbdata):
    if debug_prints():
        print('visiting join vars for:', join_node)
        print('cbdata: ', sorted(cbdata.items()))
    for nyuw__vyry in list(join_node.left_vars.keys()):
        join_node.left_vars[nyuw__vyry] = visit_vars_inner(join_node.
            left_vars[nyuw__vyry], callback, cbdata)
    for nyuw__vyry in list(join_node.right_vars.keys()):
        join_node.right_vars[nyuw__vyry] = visit_vars_inner(join_node.
            right_vars[nyuw__vyry], callback, cbdata)
    for nyuw__vyry in list(join_node.out_data_vars.keys()):
        join_node.out_data_vars[nyuw__vyry] = visit_vars_inner(join_node.
            out_data_vars[nyuw__vyry], callback, cbdata)


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    exy__sllx = []
    rkhh__odpx = True
    for nyuw__vyry, nmd__ijo in join_node.out_data_vars.items():
        if nmd__ijo.name in lives:
            rkhh__odpx = False
            continue
        if nyuw__vyry == '$_bodo_index_':
            continue
        if join_node.indicator and nyuw__vyry == '_merge':
            exy__sllx.append('_merge')
            join_node.indicator = False
            continue
        tpp__aeol, kzi__yhsmy = join_node.column_origins[nyuw__vyry]
        if (tpp__aeol == 'left' and kzi__yhsmy not in join_node.left_keys and
            kzi__yhsmy not in join_node.left_cond_cols):
            join_node.left_vars.pop(kzi__yhsmy)
            exy__sllx.append(nyuw__vyry)
        if (tpp__aeol == 'right' and kzi__yhsmy not in join_node.right_keys and
            kzi__yhsmy not in join_node.right_cond_cols):
            join_node.right_vars.pop(kzi__yhsmy)
            exy__sllx.append(nyuw__vyry)
    for cname in exy__sllx:
        join_node.out_data_vars.pop(cname)
    if rkhh__odpx:
        return None
    return join_node


ir_utils.remove_dead_extensions[Join] = remove_dead_join


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({xlda__alztm.name for xlda__alztm in join_node.left_vars
        .values()})
    use_set.update({xlda__alztm.name for xlda__alztm in join_node.
        right_vars.values()})
    def_set.update({xlda__alztm.name for xlda__alztm in join_node.
        out_data_vars.values()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    snv__tgdyn = set(xlda__alztm.name for xlda__alztm in join_node.
        out_data_vars.values())
    return set(), snv__tgdyn


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for nyuw__vyry in list(join_node.left_vars.keys()):
        join_node.left_vars[nyuw__vyry] = replace_vars_inner(join_node.
            left_vars[nyuw__vyry], var_dict)
    for nyuw__vyry in list(join_node.right_vars.keys()):
        join_node.right_vars[nyuw__vyry] = replace_vars_inner(join_node.
            right_vars[nyuw__vyry], var_dict)
    for nyuw__vyry in list(join_node.out_data_vars.keys()):
        join_node.out_data_vars[nyuw__vyry] = replace_vars_inner(join_node.
            out_data_vars[nyuw__vyry], var_dict)
    return


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for nmd__ijo in join_node.out_data_vars.values():
        definitions[nmd__ijo.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    n_keys = len(join_node.left_keys)
    rgyhu__sfkfm = tuple(join_node.left_vars[vvd__unr] for vvd__unr in
        join_node.left_keys)
    zesa__lsge = tuple(join_node.right_vars[vvd__unr] for vvd__unr in
        join_node.right_keys)
    mcow__jzlxa = tuple(join_node.left_vars.keys())
    eoqa__wqnt = tuple(join_node.right_vars.keys())
    yfr__fac = ()
    tjnci__qmzuo = ()
    optional_column = False
    if (join_node.left_index and not join_node.right_index and not
        join_node.is_join):
        ttf__ikb = join_node.right_keys[0]
        if ttf__ikb in mcow__jzlxa:
            tjnci__qmzuo = ttf__ikb,
            yfr__fac = join_node.right_vars[ttf__ikb],
            optional_column = True
    if (join_node.right_index and not join_node.left_index and not
        join_node.is_join):
        ttf__ikb = join_node.left_keys[0]
        if ttf__ikb in eoqa__wqnt:
            tjnci__qmzuo = ttf__ikb,
            yfr__fac = join_node.left_vars[ttf__ikb],
            optional_column = True
    eva__xwcyn = tuple(join_node.out_data_vars[cname] for cname in tjnci__qmzuo
        )
    gln__jbjn = tuple(xlda__alztm for nnxo__day, xlda__alztm in sorted(
        join_node.left_vars.items(), key=lambda a: str(a[0])) if nnxo__day
         not in join_node.left_keys)
    jctsx__ivqo = tuple(xlda__alztm for nnxo__day, xlda__alztm in sorted(
        join_node.right_vars.items(), key=lambda a: str(a[0])) if nnxo__day
         not in join_node.right_keys)
    maos__lew = yfr__fac + rgyhu__sfkfm + zesa__lsge + gln__jbjn + jctsx__ivqo
    pub__qiwo = tuple(typemap[xlda__alztm.name] for xlda__alztm in maos__lew)
    hddy__ocyhu = tuple('opti_c' + str(i) for i in range(len(yfr__fac)))
    left_other_names = tuple('t1_c' + str(i) for i in range(len(gln__jbjn)))
    right_other_names = tuple('t2_c' + str(i) for i in range(len(jctsx__ivqo)))
    left_other_types = tuple([typemap[vvd__unr.name] for vvd__unr in gln__jbjn]
        )
    right_other_types = tuple([typemap[vvd__unr.name] for vvd__unr in
        jctsx__ivqo])
    left_key_names = tuple('t1_key' + str(i) for i in range(n_keys))
    right_key_names = tuple('t2_key' + str(i) for i in range(n_keys))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}{}, {},{}{}{}):\n'.format('{},'.format(hddy__ocyhu
        [0]) if len(hddy__ocyhu) == 1 else '', ','.join(left_key_names),
        ','.join(right_key_names), ','.join(left_other_names), ',' if len(
        left_other_names) != 0 else '', ','.join(right_other_names))
    left_key_types = tuple(typemap[xlda__alztm.name] for xlda__alztm in
        rgyhu__sfkfm)
    right_key_types = tuple(typemap[xlda__alztm.name] for xlda__alztm in
        zesa__lsge)
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
    fex__cquve = []
    for cname in join_node.left_keys:
        if cname in join_node.add_suffix:
            ojp__mees = str(cname) + join_node.suffix_x
        else:
            ojp__mees = cname
        assert ojp__mees in join_node.out_data_vars
        fex__cquve.append(join_node.out_data_vars[ojp__mees])
    for i, cname in enumerate(join_node.right_keys):
        if not join_node.vect_same_key[i] and not join_node.is_join:
            if cname in join_node.add_suffix:
                ojp__mees = str(cname) + join_node.suffix_y
            else:
                ojp__mees = cname
            assert ojp__mees in join_node.out_data_vars
            fex__cquve.append(join_node.out_data_vars[ojp__mees])

    def _get_out_col_var(cname, is_left):
        if cname in join_node.add_suffix:
            if is_left:
                ojp__mees = str(cname) + join_node.suffix_x
            else:
                ojp__mees = str(cname) + join_node.suffix_y
        else:
            ojp__mees = cname
        return join_node.out_data_vars[ojp__mees]
    aswd__eunz = eva__xwcyn + tuple(fex__cquve)
    aswd__eunz += tuple(_get_out_col_var(nnxo__day, True) for nnxo__day,
        xlda__alztm in sorted(join_node.left_vars.items(), key=lambda a:
        str(a[0])) if nnxo__day not in join_node.left_keys)
    aswd__eunz += tuple(_get_out_col_var(nnxo__day, False) for nnxo__day,
        xlda__alztm in sorted(join_node.right_vars.items(), key=lambda a:
        str(a[0])) if nnxo__day not in join_node.right_keys)
    if join_node.indicator:
        aswd__eunz += _get_out_col_var('_merge', False),
    bwo__weem = [('t3_c' + str(i)) for i in range(len(aswd__eunz))]
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
            right_parallel, glbs, [typemap[xlda__alztm.name] for
            xlda__alztm in aswd__eunz], join_node.loc, join_node.indicator,
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
        func_text += f'    {bwo__weem[idx]} = opti_0\n'
        idx += 1
    for i in range(n_keys):
        func_text += f'    {bwo__weem[idx]} = t1_keys_{i}\n'
        idx += 1
    for i in range(n_keys):
        if not join_node.vect_same_key[i] and not join_node.is_join:
            func_text += f'    {bwo__weem[idx]} = t2_keys_{i}\n'
            idx += 1
    for i in range(len(left_other_names)):
        func_text += f'    {bwo__weem[idx]} = left_{i}\n'
        idx += 1
    for i in range(len(right_other_names)):
        func_text += f'    {bwo__weem[idx]} = right_{i}\n'
        idx += 1
    if join_node.indicator:
        func_text += f'    {bwo__weem[idx]} = indicator_col\n'
        idx += 1
    dttro__rjn = {}
    exec(func_text, {}, dttro__rjn)
    ezi__oin = dttro__rjn['f']
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
    ngon__kfe = compile_to_numba_ir(ezi__oin, glbs, typingctx=typingctx,
        targetctx=targetctx, arg_typs=pub__qiwo, typemap=typemap, calltypes
        =calltypes).blocks.popitem()[1]
    replace_arg_nodes(ngon__kfe, maos__lew)
    rrnp__adibm = ngon__kfe.body[:-3]
    for i in range(len(aswd__eunz)):
        rrnp__adibm[-len(aswd__eunz) + i].target = aswd__eunz[i]
    return rrnp__adibm


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    avng__zuva = next_label()
    xuxpk__uqyn = _get_col_to_ind(join_node.left_keys, join_node.left_vars)
    lolo__gip = _get_col_to_ind(join_node.right_keys, join_node.right_vars)
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{avng__zuva}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
"""
    func_text += '  if is_null_pointer(left_table):\n'
    func_text += '    return False\n'
    expr, func_text, left_col_nums = _replace_column_accesses(expr,
        xuxpk__uqyn, typemap, join_node.left_vars, table_getitem_funcs,
        func_text, 'left', len(join_node.left_keys), na_check_name)
    expr, func_text, right_col_nums = _replace_column_accesses(expr,
        lolo__gip, typemap, join_node.right_vars, table_getitem_funcs,
        func_text, 'right', len(join_node.right_keys), na_check_name)
    func_text += f'  return {expr}'
    dttro__rjn = {}
    exec(func_text, table_getitem_funcs, dttro__rjn)
    shg__dpqw = dttro__rjn[f'bodo_join_gen_cond{avng__zuva}']
    wvo__bwx = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    guhs__cxk = numba.cfunc(wvo__bwx, nopython=True)(shg__dpqw)
    join_gen_cond_cfunc[guhs__cxk.native_name] = guhs__cxk
    join_gen_cond_cfunc_addr[guhs__cxk.native_name] = guhs__cxk.address
    return guhs__cxk, left_col_nums, right_col_nums


def _replace_column_accesses(expr, col_to_ind, typemap, col_vars,
    table_getitem_funcs, func_text, table_name, n_keys, na_check_name):
    xyxls__vnc = []
    for vvd__unr, ojf__dwev in col_to_ind.items():
        cname = f'({table_name}.{vvd__unr})'
        if cname not in expr:
            continue
        xjdpp__zrshk = f'getitem_{table_name}_val_{ojf__dwev}'
        sqarl__qihj = f'_bodo_{table_name}_val_{ojf__dwev}'
        ygvxn__xxsoh = typemap[col_vars[vvd__unr].name].dtype
        if ygvxn__xxsoh == types.unicode_type:
            func_text += f"""  {sqarl__qihj}, {sqarl__qihj}_size = {xjdpp__zrshk}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {sqarl__qihj} = bodo.libs.str_arr_ext.decode_utf8({sqarl__qihj}, {sqarl__qihj}_size)
"""
        else:
            func_text += (
                f'  {sqarl__qihj} = {xjdpp__zrshk}({table_name}_data1, {table_name}_ind)\n'
                )
        table_getitem_funcs[xjdpp__zrshk
            ] = bodo.libs.array._gen_row_access_intrinsic(ygvxn__xxsoh,
            ojf__dwev)
        expr = expr.replace(cname, sqarl__qihj)
        kebks__eecd = f'({na_check_name}.{table_name}.{vvd__unr})'
        if kebks__eecd in expr:
            cvcj__zwx = typemap[col_vars[vvd__unr].name]
            iygxb__rqwoa = f'nacheck_{table_name}_val_{ojf__dwev}'
            xvfy__mcft = f'_bodo_isna_{table_name}_val_{ojf__dwev}'
            if isinstance(cvcj__zwx, bodo.libs.int_arr_ext.IntegerArrayType
                ) or cvcj__zwx in [bodo.libs.bool_arr_ext.boolean_array,
                bodo.libs.str_arr_ext.string_array_type]:
                func_text += f"""  {xvfy__mcft} = {iygxb__rqwoa}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += f"""  {xvfy__mcft} = {iygxb__rqwoa}({table_name}_data1, {table_name}_ind)
"""
            table_getitem_funcs[iygxb__rqwoa
                ] = bodo.libs.array._gen_row_na_check_intrinsic(cvcj__zwx,
                ojf__dwev)
            expr = expr.replace(kebks__eecd, xvfy__mcft)
        if ojf__dwev >= n_keys:
            xyxls__vnc.append(ojf__dwev)
    return expr, func_text, xyxls__vnc


def _get_col_to_ind(key_names, col_vars):
    n_keys = len(key_names)
    col_to_ind = {vvd__unr: i for i, vvd__unr in enumerate(key_names)}
    i = n_keys
    for vvd__unr in sorted(col_vars, key=lambda a: str(a)):
        if vvd__unr in key_names:
            continue
        col_to_ind[vvd__unr] = i
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
    vqdfo__jzwti = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[xlda__alztm.name] in vqdfo__jzwti for
        xlda__alztm in join_node.left_vars.values())
    right_parallel = all(array_dists[xlda__alztm.name] in vqdfo__jzwti for
        xlda__alztm in join_node.right_vars.values())
    if not left_parallel:
        assert not any(array_dists[xlda__alztm.name] in vqdfo__jzwti for
            xlda__alztm in join_node.left_vars.values())
    if not right_parallel:
        assert not any(array_dists[xlda__alztm.name] in vqdfo__jzwti for
            xlda__alztm in join_node.right_vars.values())
    if left_parallel or right_parallel:
        assert all(array_dists[xlda__alztm.name] in vqdfo__jzwti for
            xlda__alztm in join_node.out_data_vars.values())
    return left_parallel, right_parallel


def _gen_local_hash_join(optional_column, left_key_names, right_key_names,
    left_key_types, right_key_types, left_other_names, right_other_names,
    left_other_types, right_other_types, vect_same_key, is_left, is_right,
    is_join, left_parallel, right_parallel, glbs, out_types, loc, indicator,
    is_na_equal, general_cond_cfunc, left_col_nums, right_col_nums):

    def needs_typechange(in_type, need_nullable, is_same_key):
        return isinstance(in_type, types.Array) and not is_dtype_nullable(
            in_type.dtype) and need_nullable and not is_same_key
    eze__rbtq = []
    for i in range(len(left_key_names)):
        iqha__qchc = _match_join_key_types(left_key_types[i],
            right_key_types[i], loc)
        eze__rbtq.append(needs_typechange(iqha__qchc, is_right,
            vect_same_key[i]))
    for i in range(len(left_other_names)):
        eze__rbtq.append(needs_typechange(left_other_types[i], is_right, False)
            )
    for i in range(len(right_key_names)):
        if not vect_same_key[i] and not is_join:
            iqha__qchc = _match_join_key_types(left_key_types[i],
                right_key_types[i], loc)
            eze__rbtq.append(needs_typechange(iqha__qchc, is_left, False))
    for i in range(len(right_other_names)):
        eze__rbtq.append(needs_typechange(right_other_types[i], is_left, False)
            )

    def get_out_type(idx, in_type, in_name, need_nullable, is_same_key):
        if isinstance(in_type, types.Array) and not is_dtype_nullable(in_type
            .dtype) and need_nullable and not is_same_key:
            if isinstance(in_type.dtype, types.Integer):
                pjon__uaew = IntDtype(in_type.dtype).name
                assert pjon__uaew.endswith('Dtype()')
                pjon__uaew = pjon__uaew[:-7]
                jeu__yvs = f"""    typ_{idx} = bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype="{pjon__uaew}"))
"""
                izova__kxqlm = f'typ_{idx}'
            else:
                assert in_type.dtype == types.bool_, 'unexpected non-nullable type in join'
                jeu__yvs = (
                    f'    typ_{idx} = bodo.libs.bool_arr_ext.alloc_bool_array(1)\n'
                    )
                izova__kxqlm = f'typ_{idx}'
        else:
            jeu__yvs = ''
            izova__kxqlm = in_name
        return jeu__yvs, izova__kxqlm
    n_keys = len(left_key_names)
    func_text = '    # beginning of _gen_local_hash_join\n'
    qpvsn__cur = []
    for i in range(n_keys):
        qpvsn__cur.append('t1_keys[{}]'.format(i))
    for i in range(len(left_other_names)):
        qpvsn__cur.append('data_left[{}]'.format(i))
    func_text += '    info_list_total_l = [{}]\n'.format(','.join(
        'array_to_info({})'.format(a) for a in qpvsn__cur))
    func_text += '    table_left = arr_info_list_to_table(info_list_total_l)\n'
    dthze__eohjc = []
    for i in range(n_keys):
        dthze__eohjc.append('t2_keys[{}]'.format(i))
    for i in range(len(right_other_names)):
        dthze__eohjc.append('data_right[{}]'.format(i))
    func_text += '    info_list_total_r = [{}]\n'.format(','.join(
        'array_to_info({})'.format(a) for a in dthze__eohjc))
    func_text += (
        '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    func_text += '    vect_same_key = np.array([{}])\n'.format(','.join('1' if
        xsxew__gzo else '0' for xsxew__gzo in vect_same_key))
    func_text += '    vect_need_typechange = np.array([{}])\n'.format(','.
        join('1' if xsxew__gzo else '0' for xsxew__gzo in eze__rbtq))
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
    for i, faiht__mpt in enumerate(left_key_names):
        iqha__qchc = _match_join_key_types(left_key_types[i],
            right_key_types[i], loc)
        glahe__vcjp = get_out_type(idx, iqha__qchc, f't1_keys[{i}]',
            is_right, vect_same_key[i])
        func_text += glahe__vcjp[0]
        glbs[f'out_type_{idx}'] = out_types[idx]
        if iqha__qchc != left_key_types[i]:
            func_text += f"""    t1_keys_{i} = bodo.utils.utils.astype(info_to_array(info_from_table(out_table, {idx}), {glahe__vcjp[1]}), out_type_{idx})
"""
        else:
            func_text += f"""    t1_keys_{i} = info_to_array(info_from_table(out_table, {idx}), {glahe__vcjp[1]})
"""
        idx += 1
    for i, faiht__mpt in enumerate(left_other_names):
        glahe__vcjp = get_out_type(idx, left_other_types[i], faiht__mpt,
            is_right, False)
        func_text += glahe__vcjp[0]
        func_text += (
            '    left_{} = info_to_array(info_from_table(out_table, {}), {})\n'
            .format(i, idx, glahe__vcjp[1]))
        idx += 1
    for i, faiht__mpt in enumerate(right_key_names):
        if not vect_same_key[i] and not is_join:
            iqha__qchc = _match_join_key_types(left_key_types[i],
                right_key_types[i], loc)
            glahe__vcjp = get_out_type(idx, iqha__qchc, f't2_keys[{i}]',
                is_left, False)
            func_text += glahe__vcjp[0]
            glbs[f'out_type_{idx}'] = out_types[idx - len(left_other_names)]
            if iqha__qchc != right_key_types[i]:
                func_text += f"""    t2_keys_{i} = bodo.utils.utils.astype(info_to_array(info_from_table(out_table, {idx}), {glahe__vcjp[1]}), out_type_{idx})
"""
            else:
                func_text += f"""    t2_keys_{i} = info_to_array(info_from_table(out_table, {idx}), {glahe__vcjp[1]})
"""
            idx += 1
    for i, faiht__mpt in enumerate(right_other_names):
        glahe__vcjp = get_out_type(idx, right_other_types[i], faiht__mpt,
            is_left, False)
        func_text += glahe__vcjp[0]
        func_text += (
            '    right_{} = info_to_array(info_from_table(out_table, {}), {})\n'
            .format(i, idx, glahe__vcjp[1]))
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
    jnfgx__kvzf = bodo.libs.distributed_api.get_size()
    aiu__eiop = alloc_pre_shuffle_metadata(key_arrs, data, jnfgx__kvzf, False)
    nnxo__day = len(key_arrs[0])
    ntvm__znwl = np.empty(nnxo__day, np.int32)
    wkb__qhqj = arr_info_list_to_table([array_to_info(key_arrs[0])])
    gge__luaqq = 1
    ztd__dnv = compute_node_partition_by_hash(wkb__qhqj, gge__luaqq,
        jnfgx__kvzf)
    buqs__fsbtv = np.empty(1, np.int32)
    xlvz__pos = info_to_array(info_from_table(ztd__dnv, 0), buqs__fsbtv)
    delete_table(ztd__dnv)
    delete_table(wkb__qhqj)
    for i in range(nnxo__day):
        val = getitem_arr_tup_single(key_arrs, i)
        node_id = xlvz__pos[i]
        ntvm__znwl[i] = node_id
        update_shuffle_meta(aiu__eiop, node_id, i, key_arrs, data, False)
    shuffle_meta = finalize_shuffle_meta(key_arrs, data, aiu__eiop,
        jnfgx__kvzf, False)
    for i in range(nnxo__day):
        node_id = ntvm__znwl[i]
        write_send_buff(shuffle_meta, node_id, i, key_arrs, data)
        shuffle_meta.tmp_offset[node_id] += 1
    iaz__wyqzd = alltoallv_tup(key_arrs + data, shuffle_meta, key_arrs)
    fex__cquve = _get_keys_tup(iaz__wyqzd, key_arrs)
    ispm__ptq = _get_data_tup(iaz__wyqzd, key_arrs)
    return fex__cquve, ispm__ptq


@generated_jit(nopython=True, cache=True)
def parallel_shuffle(key_arrs, data):
    return parallel_join_impl


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    jnfgx__kvzf = bodo.libs.distributed_api.get_size()
    ytho__ybdrz = np.empty(jnfgx__kvzf, left_key_arrs[0].dtype)
    rtq__boq = np.empty(jnfgx__kvzf, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(ytho__ybdrz, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(rtq__boq, left_key_arrs[0][-1])
    tneic__xfk = np.zeros(jnfgx__kvzf, np.int32)
    pnyam__kynn = np.zeros(jnfgx__kvzf, np.int32)
    zii__oba = np.zeros(jnfgx__kvzf, np.int32)
    zujwz__che = right_key_arrs[0][0]
    wnuj__gphy = right_key_arrs[0][-1]
    dfk__zopl = -1
    i = 0
    while i < jnfgx__kvzf - 1 and rtq__boq[i] < zujwz__che:
        i += 1
    while i < jnfgx__kvzf and ytho__ybdrz[i] <= wnuj__gphy:
        dfk__zopl, qirap__aeyy = _count_overlap(right_key_arrs[0],
            ytho__ybdrz[i], rtq__boq[i])
        if dfk__zopl != 0:
            dfk__zopl -= 1
            qirap__aeyy += 1
        tneic__xfk[i] = qirap__aeyy
        pnyam__kynn[i] = dfk__zopl
        i += 1
    while i < jnfgx__kvzf:
        tneic__xfk[i] = 1
        pnyam__kynn[i] = len(right_key_arrs[0]) - 1
        i += 1
    bodo.libs.distributed_api.alltoall(tneic__xfk, zii__oba, 1)
    skp__xur = zii__oba.sum()
    qtq__dexib = np.empty(skp__xur, right_key_arrs[0].dtype)
    rrjy__rqewa = alloc_arr_tup(skp__xur, right_data)
    tfhgd__rwcf = bodo.ir.join.calc_disp(zii__oba)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], qtq__dexib,
        tneic__xfk, zii__oba, pnyam__kynn, tfhgd__rwcf)
    bodo.libs.distributed_api.alltoallv_tup(right_data, rrjy__rqewa,
        tneic__xfk, zii__oba, pnyam__kynn, tfhgd__rwcf)
    return (qtq__dexib,), rrjy__rqewa


@numba.njit
def _count_overlap(r_key_arr, start, end):
    qirap__aeyy = 0
    dfk__zopl = 0
    yqjxo__cvpc = 0
    while yqjxo__cvpc < len(r_key_arr) and r_key_arr[yqjxo__cvpc] < start:
        dfk__zopl += 1
        yqjxo__cvpc += 1
    while yqjxo__cvpc < len(r_key_arr) and start <= r_key_arr[yqjxo__cvpc
        ] <= end:
        yqjxo__cvpc += 1
        qirap__aeyy += 1
    return dfk__zopl, qirap__aeyy


def write_send_buff(shuffle_meta, node_id, i, key_arrs, data):
    return i


@overload(write_send_buff, no_unliteral=True)
def write_data_buff_overload(meta, node_id, i, key_arrs, data):
    func_text = 'def f(meta, node_id, i, key_arrs, data):\n'
    func_text += (
        '  w_ind = meta.send_disp[node_id] + meta.tmp_offset[node_id]\n')
    n_keys = len(key_arrs.types)
    for i, dfev__fjwje in enumerate(key_arrs.types + data.types):
        arr = 'key_arrs[{}]'.format(i) if i < n_keys else 'data[{}]'.format(
            i - n_keys)
        if not dfev__fjwje in (string_type, string_array_type,
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
    dttro__rjn = {}
    exec(func_text, {'str_copy_ptr': str_copy_ptr, 'get_null_bitmap_ptr':
        get_null_bitmap_ptr, 'get_bit_bitmap': get_bit_bitmap, 'set_bit_to':
        set_bit_to, 'get_str_arr_item_length': get_str_arr_item_length,
        'get_str_arr_item_ptr': get_str_arr_item_ptr}, dttro__rjn)
    pkjs__sxxwf = dttro__rjn['f']
    return pkjs__sxxwf


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    tbzhj__jdqh = np.empty_like(arr)
    tbzhj__jdqh[0] = 0
    for i in range(1, len(arr)):
        tbzhj__jdqh[i] = tbzhj__jdqh[i - 1] + arr[i - 1]
    return tbzhj__jdqh


def ensure_capacity(arr, new_size):
    fsyi__ibosr = arr
    wknbp__doh = len(arr)
    if wknbp__doh < new_size:
        assbo__oec = 2 * wknbp__doh
        fsyi__ibosr = bodo.utils.utils.alloc_type(assbo__oec, arr)
        fsyi__ibosr[:wknbp__doh] = arr
    return fsyi__ibosr


@overload(ensure_capacity, no_unliteral=True)
def ensure_capacity_overload(arr, new_size):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return ensure_capacity
    assert isinstance(arr, types.BaseTuple)
    qirap__aeyy = arr.count
    func_text = 'def f(arr, new_size):\n'
    func_text += '  return ({}{})\n'.format(','.join([
        'ensure_capacity(arr[{}], new_size)'.format(i) for i in range(
        qirap__aeyy)]), ',' if qirap__aeyy == 1 else '')
    dttro__rjn = {}
    exec(func_text, {'ensure_capacity': ensure_capacity}, dttro__rjn)
    iddwx__afcca = dttro__rjn['f']
    return iddwx__afcca


@numba.njit
def ensure_capacity_str(arr, new_size, n_chars):
    fsyi__ibosr = arr
    wknbp__doh = len(arr)
    wkee__fgub = num_total_chars(arr)
    pqz__mbxwj = getitem_str_offset(arr, new_size - 1) + n_chars
    if wknbp__doh < new_size or pqz__mbxwj > wkee__fgub:
        assbo__oec = int(2 * wknbp__doh if wknbp__doh < new_size else
            wknbp__doh)
        izt__jfi = int(2 * wkee__fgub + n_chars if pqz__mbxwj > wkee__fgub else
            wkee__fgub)
        fsyi__ibosr = pre_alloc_string_array(assbo__oec, izt__jfi)
        copy_str_arr_slice(fsyi__ibosr, arr, new_size - 1)
    return fsyi__ibosr


def trim_arr_tup(data, new_size):
    return data


@overload(trim_arr_tup, no_unliteral=True)
def trim_arr_tup_overload(data, new_size):
    assert isinstance(data, types.BaseTuple)
    qirap__aeyy = data.count
    func_text = 'def f(data, new_size):\n'
    func_text += '  return ({}{})\n'.format(','.join([
        'trim_arr(data[{}], new_size)'.format(i) for i in range(qirap__aeyy
        )]), ',' if qirap__aeyy == 1 else '')
    dttro__rjn = {}
    exec(func_text, {'trim_arr': trim_arr}, dttro__rjn)
    iddwx__afcca = dttro__rjn['f']
    return iddwx__afcca


def copy_elem_buff(arr, ind, val):
    fsyi__ibosr = ensure_capacity(arr, ind + 1)
    fsyi__ibosr[ind] = val
    return fsyi__ibosr


@overload(copy_elem_buff, no_unliteral=True)
def copy_elem_buff_overload(arr, ind, val):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return copy_elem_buff
    assert arr == string_array_type

    def copy_elem_buff_str(arr, ind, val):
        fsyi__ibosr = ensure_capacity_str(arr, ind + 1, get_utf8_size(val))
        fsyi__ibosr[ind] = val
        return fsyi__ibosr
    return copy_elem_buff_str


def copy_elem_buff_tup(arr, ind, val):
    return arr


@overload(copy_elem_buff_tup, no_unliteral=True)
def copy_elem_buff_tup_overload(data, ind, val):
    assert isinstance(data, types.BaseTuple)
    qirap__aeyy = data.count
    func_text = 'def f(data, ind, val):\n'
    for i in range(qirap__aeyy):
        func_text += ('  arr_{} = copy_elem_buff(data[{}], ind, val[{}])\n'
            .format(i, i, i))
    func_text += '  return ({}{})\n'.format(','.join(['arr_{}'.format(i) for
        i in range(qirap__aeyy)]), ',' if qirap__aeyy == 1 else '')
    dttro__rjn = {}
    exec(func_text, {'copy_elem_buff': copy_elem_buff}, dttro__rjn)
    lpq__yug = dttro__rjn['f']
    return lpq__yug


def trim_arr(arr, size):
    return arr[:size]


@overload(trim_arr, no_unliteral=True)
def trim_arr_overload(arr, size):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return trim_arr
    assert arr == string_array_type

    def trim_arr_str(arr, size):
        fsyi__ibosr = pre_alloc_string_array(size, np.int64(
            getitem_str_offset(arr, size)))
        copy_str_arr_slice(fsyi__ibosr, arr, size)
        return fsyi__ibosr
    return trim_arr_str


def setnan_elem_buff(arr, ind):
    fsyi__ibosr = ensure_capacity(arr, ind + 1)
    bodo.libs.array_kernels.setna(fsyi__ibosr, ind)
    return fsyi__ibosr


@overload(setnan_elem_buff, no_unliteral=True)
def setnan_elem_buff_overload(arr, ind):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return setnan_elem_buff
    assert arr == string_array_type

    def setnan_elem_buff_str(arr, ind):
        fsyi__ibosr = ensure_capacity_str(arr, ind + 1, 0)
        fsyi__ibosr[ind] = ''
        bodo.libs.array_kernels.setna(fsyi__ibosr, ind)
        return fsyi__ibosr
    return setnan_elem_buff_str


def setnan_elem_buff_tup(arr, ind):
    return arr


@overload(setnan_elem_buff_tup, no_unliteral=True)
def setnan_elem_buff_tup_overload(data, ind):
    assert isinstance(data, types.BaseTuple)
    qirap__aeyy = data.count
    func_text = 'def f(data, ind):\n'
    for i in range(qirap__aeyy):
        func_text += '  arr_{} = setnan_elem_buff(data[{}], ind)\n'.format(i, i
            )
    func_text += '  return ({}{})\n'.format(','.join(['arr_{}'.format(i) for
        i in range(qirap__aeyy)]), ',' if qirap__aeyy == 1 else '')
    dttro__rjn = {}
    exec(func_text, {'setnan_elem_buff': setnan_elem_buff}, dttro__rjn)
    lpq__yug = dttro__rjn['f']
    return lpq__yug


@generated_jit(nopython=True, cache=True)
def _check_ind_if_hashed(right_keys, r_ind, l_key):
    if right_keys == types.Tuple((types.intp[::1],)):
        return lambda right_keys, r_ind, l_key: r_ind

    def _impl(right_keys, r_ind, l_key):
        dgvt__ovlt = getitem_arr_tup(right_keys, r_ind)
        if dgvt__ovlt != l_key:
            return -1
        return r_ind
    return _impl


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    ifcfk__kktw = len(left_keys[0])
    afn__mfg = len(right_keys[0])
    wkpf__nnvj = alloc_arr_tup(ifcfk__kktw, left_keys)
    uwi__leihn = alloc_arr_tup(ifcfk__kktw, right_keys)
    pdkp__pymv = alloc_arr_tup(ifcfk__kktw, data_left)
    fvhae__dqg = alloc_arr_tup(ifcfk__kktw, data_right)
    gjjpa__mrzjr = 0
    vrcmk__izrd = 0
    for gjjpa__mrzjr in range(ifcfk__kktw):
        if vrcmk__izrd < 0:
            vrcmk__izrd = 0
        while vrcmk__izrd < afn__mfg and getitem_arr_tup(right_keys,
            vrcmk__izrd) <= getitem_arr_tup(left_keys, gjjpa__mrzjr):
            vrcmk__izrd += 1
        vrcmk__izrd -= 1
        setitem_arr_tup(wkpf__nnvj, gjjpa__mrzjr, getitem_arr_tup(left_keys,
            gjjpa__mrzjr))
        setitem_arr_tup(pdkp__pymv, gjjpa__mrzjr, getitem_arr_tup(data_left,
            gjjpa__mrzjr))
        if vrcmk__izrd >= 0:
            setitem_arr_tup(uwi__leihn, gjjpa__mrzjr, getitem_arr_tup(
                right_keys, vrcmk__izrd))
            setitem_arr_tup(fvhae__dqg, gjjpa__mrzjr, getitem_arr_tup(
                data_right, vrcmk__izrd))
        else:
            bodo.libs.array_kernels.setna_tup(uwi__leihn, gjjpa__mrzjr)
            bodo.libs.array_kernels.setna_tup(fvhae__dqg, gjjpa__mrzjr)
    return wkpf__nnvj, uwi__leihn, pdkp__pymv, fvhae__dqg


def copy_arr_tup(arrs):
    return tuple(a.copy() for a in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    qirap__aeyy = arrs.count
    func_text = 'def f(arrs):\n'
    func_text += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(qirap__aeyy)))
    dttro__rjn = {}
    exec(func_text, {}, dttro__rjn)
    impl = dttro__rjn['f']
    return impl


def get_nan_bits(arr, ind):
    return 0


@overload(get_nan_bits, no_unliteral=True)
def overload_get_nan_bits(arr, ind):
    if arr == string_array_type:

        def impl_str(arr, ind):
            bktn__alff = get_null_bitmap_ptr(arr)
            return get_bit_bitmap(bktn__alff, ind)
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
    qirap__aeyy = arr_tup.count
    func_text = 'def f(arr_tup, ind):\n'
    func_text += '  return ({}{})\n'.format(','.join([
        'get_nan_bits(arr_tup[{}], ind)'.format(i) for i in range(
        qirap__aeyy)]), ',' if qirap__aeyy == 1 else '')
    dttro__rjn = {}
    exec(func_text, {'get_nan_bits': get_nan_bits}, dttro__rjn)
    impl = dttro__rjn['f']
    return impl


def set_nan_bits(arr, ind, na_val):
    return 0


@overload(set_nan_bits, no_unliteral=True)
def overload_set_nan_bits(arr, ind, na_val):
    if arr == string_array_type:

        def impl_str(arr, ind, na_val):
            bktn__alff = get_null_bitmap_ptr(arr)
            set_bit_to(bktn__alff, ind, na_val)
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
    qirap__aeyy = arr_tup.count
    func_text = 'def f(arr_tup, ind, na_val):\n'
    for i in range(qirap__aeyy):
        func_text += '  set_nan_bits(arr_tup[{}], ind, na_val[{}])\n'.format(i,
            i)
    func_text += '  return\n'
    dttro__rjn = {}
    exec(func_text, {'set_nan_bits': set_nan_bits}, dttro__rjn)
    impl = dttro__rjn['f']
    return impl
