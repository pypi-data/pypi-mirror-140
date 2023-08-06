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
        ahm__urtxt = func.signature
        xre__pspjt = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(64)])
        lza__oko = cgutils.get_or_insert_function(builder.module,
            xre__pspjt, sym._literal_value)
        builder.call(lza__oko, [context.get_constant_null(ahm__urtxt.args[0
            ]), context.get_constant_null(ahm__urtxt.args[1]), context.
            get_constant_null(ahm__urtxt.args[2]), context.
            get_constant_null(ahm__urtxt.args[3]), context.
            get_constant_null(ahm__urtxt.args[4]), context.
            get_constant_null(ahm__urtxt.args[5]), context.get_constant(
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
        self.left_cond_cols = set(kmjh__aukba for kmjh__aukba in left_vars.
            keys() if f'(left.{kmjh__aukba})' in gen_cond_expr)
        self.right_cond_cols = set(kmjh__aukba for kmjh__aukba in
            right_vars.keys() if f'(right.{kmjh__aukba})' in gen_cond_expr)
        yhvvu__appwl = set(left_keys) & set(right_keys)
        rrc__ljzs = set(left_vars.keys()) & set(right_vars.keys())
        lzbo__gtfi = rrc__ljzs - yhvvu__appwl
        vect_same_key = []
        n_keys = len(left_keys)
        for ysne__ndzm in range(n_keys):
            rwzb__tya = left_keys[ysne__ndzm]
            pcv__and = right_keys[ysne__ndzm]
            vect_same_key.append(rwzb__tya == pcv__and)
        self.vect_same_key = vect_same_key
        self.column_origins = {(str(kmjh__aukba) + suffix_x if kmjh__aukba in
            lzbo__gtfi else kmjh__aukba): ('left', kmjh__aukba) for
            kmjh__aukba in left_vars.keys()}
        self.column_origins.update({(str(kmjh__aukba) + suffix_y if 
            kmjh__aukba in lzbo__gtfi else kmjh__aukba): ('right',
            kmjh__aukba) for kmjh__aukba in right_vars.keys()})
        if '$_bodo_index_' in lzbo__gtfi:
            lzbo__gtfi.remove('$_bodo_index_')
        self.add_suffix = lzbo__gtfi

    def __repr__(self):
        ajipo__ybnlg = ''
        for kmjh__aukba, eigob__pvx in self.out_data_vars.items():
            ajipo__ybnlg += "'{}':{}, ".format(kmjh__aukba, eigob__pvx.name)
        mjmgr__awrfj = '{}{{{}}}'.format(self.df_out, ajipo__ybnlg)
        mxfq__lryvt = ''
        for kmjh__aukba, eigob__pvx in self.left_vars.items():
            mxfq__lryvt += "'{}':{}, ".format(kmjh__aukba, eigob__pvx.name)
        qbu__ycp = '{}{{{}}}'.format(self.left_df, mxfq__lryvt)
        mxfq__lryvt = ''
        for kmjh__aukba, eigob__pvx in self.right_vars.items():
            mxfq__lryvt += "'{}':{}, ".format(kmjh__aukba, eigob__pvx.name)
        kqb__dqdb = '{}{{{}}}'.format(self.right_df, mxfq__lryvt)
        return 'join [{}={}]: {} , {}, {}'.format(self.left_keys, self.
            right_keys, mjmgr__awrfj, qbu__ycp, kqb__dqdb)


def join_array_analysis(join_node, equiv_set, typemap, array_analysis):
    gsom__iqwre = []
    assert len(join_node.out_data_vars) > 0, 'empty join in array analysis'
    gsv__gyl = []
    kaoln__sri = list(join_node.left_vars.values())
    for zuk__qeqf in kaoln__sri:
        ikjg__ipcxo = typemap[zuk__qeqf.name]
        hga__nnuv = equiv_set.get_shape(zuk__qeqf)
        if hga__nnuv:
            gsv__gyl.append(hga__nnuv[0])
    if len(gsv__gyl) > 1:
        equiv_set.insert_equiv(*gsv__gyl)
    gsv__gyl = []
    kaoln__sri = list(join_node.right_vars.values())
    for zuk__qeqf in kaoln__sri:
        ikjg__ipcxo = typemap[zuk__qeqf.name]
        hga__nnuv = equiv_set.get_shape(zuk__qeqf)
        if hga__nnuv:
            gsv__gyl.append(hga__nnuv[0])
    if len(gsv__gyl) > 1:
        equiv_set.insert_equiv(*gsv__gyl)
    gsv__gyl = []
    for zuk__qeqf in join_node.out_data_vars.values():
        ikjg__ipcxo = typemap[zuk__qeqf.name]
        damt__asmvy = array_analysis._gen_shape_call(equiv_set, zuk__qeqf,
            ikjg__ipcxo.ndim, None, gsom__iqwre)
        equiv_set.insert_equiv(zuk__qeqf, damt__asmvy)
        gsv__gyl.append(damt__asmvy[0])
        equiv_set.define(zuk__qeqf, set())
    if len(gsv__gyl) > 1:
        equiv_set.insert_equiv(*gsv__gyl)
    return [], gsom__iqwre


numba.parfors.array_analysis.array_analysis_extensions[Join
    ] = join_array_analysis


def join_distributed_analysis(join_node, array_dists):
    brp__uuzol = Distribution.OneD
    apt__sneh = Distribution.OneD
    for zuk__qeqf in join_node.left_vars.values():
        brp__uuzol = Distribution(min(brp__uuzol.value, array_dists[
            zuk__qeqf.name].value))
    for zuk__qeqf in join_node.right_vars.values():
        apt__sneh = Distribution(min(apt__sneh.value, array_dists[zuk__qeqf
            .name].value))
    hmwq__reif = Distribution.OneD_Var
    for zuk__qeqf in join_node.out_data_vars.values():
        if zuk__qeqf.name in array_dists:
            hmwq__reif = Distribution(min(hmwq__reif.value, array_dists[
                zuk__qeqf.name].value))
    tfrsj__kivkp = Distribution(min(hmwq__reif.value, brp__uuzol.value))
    kbi__pcw = Distribution(min(hmwq__reif.value, apt__sneh.value))
    hmwq__reif = Distribution(max(tfrsj__kivkp.value, kbi__pcw.value))
    for zuk__qeqf in join_node.out_data_vars.values():
        array_dists[zuk__qeqf.name] = hmwq__reif
    if hmwq__reif != Distribution.OneD_Var:
        brp__uuzol = hmwq__reif
        apt__sneh = hmwq__reif
    for zuk__qeqf in join_node.left_vars.values():
        array_dists[zuk__qeqf.name] = brp__uuzol
    for zuk__qeqf in join_node.right_vars.values():
        array_dists[zuk__qeqf.name] = apt__sneh
    return


distributed_analysis.distributed_analysis_extensions[Join
    ] = join_distributed_analysis


def join_typeinfer(join_node, typeinferer):
    yhvvu__appwl = set(join_node.left_keys) & set(join_node.right_keys)
    rrc__ljzs = set(join_node.left_vars.keys()) & set(join_node.right_vars.
        keys())
    lzbo__gtfi = rrc__ljzs - yhvvu__appwl
    for qxgbk__udj, drvb__udecz in join_node.out_data_vars.items():
        if join_node.indicator and qxgbk__udj == '_merge':
            continue
        if not qxgbk__udj in join_node.column_origins:
            raise BodoError('join(): The variable ' + qxgbk__udj +
                ' is absent from the output')
        itc__xbks = join_node.column_origins[qxgbk__udj]
        if itc__xbks[0] == 'left':
            zuk__qeqf = join_node.left_vars[itc__xbks[1]]
        else:
            zuk__qeqf = join_node.right_vars[itc__xbks[1]]
        typeinferer.constraints.append(typeinfer.Propagate(dst=drvb__udecz.
            name, src=zuk__qeqf.name, loc=join_node.loc))
    return


typeinfer.typeinfer_extensions[Join] = join_typeinfer


def visit_vars_join(join_node, callback, cbdata):
    if debug_prints():
        print('visiting join vars for:', join_node)
        print('cbdata: ', sorted(cbdata.items()))
    for nikcd__kon in list(join_node.left_vars.keys()):
        join_node.left_vars[nikcd__kon] = visit_vars_inner(join_node.
            left_vars[nikcd__kon], callback, cbdata)
    for nikcd__kon in list(join_node.right_vars.keys()):
        join_node.right_vars[nikcd__kon] = visit_vars_inner(join_node.
            right_vars[nikcd__kon], callback, cbdata)
    for nikcd__kon in list(join_node.out_data_vars.keys()):
        join_node.out_data_vars[nikcd__kon] = visit_vars_inner(join_node.
            out_data_vars[nikcd__kon], callback, cbdata)


ir_utils.visit_vars_extensions[Join] = visit_vars_join


def remove_dead_join(join_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    aztu__mgj = []
    qtfl__qkfo = True
    for nikcd__kon, zuk__qeqf in join_node.out_data_vars.items():
        if zuk__qeqf.name in lives:
            qtfl__qkfo = False
            continue
        if nikcd__kon == '$_bodo_index_':
            continue
        if join_node.indicator and nikcd__kon == '_merge':
            aztu__mgj.append('_merge')
            join_node.indicator = False
            continue
        cfoz__oyyx, gjta__tzwy = join_node.column_origins[nikcd__kon]
        if (cfoz__oyyx == 'left' and gjta__tzwy not in join_node.left_keys and
            gjta__tzwy not in join_node.left_cond_cols):
            join_node.left_vars.pop(gjta__tzwy)
            aztu__mgj.append(nikcd__kon)
        if (cfoz__oyyx == 'right' and gjta__tzwy not in join_node.
            right_keys and gjta__tzwy not in join_node.right_cond_cols):
            join_node.right_vars.pop(gjta__tzwy)
            aztu__mgj.append(nikcd__kon)
    for cname in aztu__mgj:
        join_node.out_data_vars.pop(cname)
    if qtfl__qkfo:
        return None
    return join_node


ir_utils.remove_dead_extensions[Join] = remove_dead_join


def join_usedefs(join_node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    use_set.update({eigob__pvx.name for eigob__pvx in join_node.left_vars.
        values()})
    use_set.update({eigob__pvx.name for eigob__pvx in join_node.right_vars.
        values()})
    def_set.update({eigob__pvx.name for eigob__pvx in join_node.
        out_data_vars.values()})
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


numba.core.analysis.ir_extension_usedefs[Join] = join_usedefs


def get_copies_join(join_node, typemap):
    xiv__oev = set(eigob__pvx.name for eigob__pvx in join_node.
        out_data_vars.values())
    return set(), xiv__oev


ir_utils.copy_propagate_extensions[Join] = get_copies_join


def apply_copies_join(join_node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    for nikcd__kon in list(join_node.left_vars.keys()):
        join_node.left_vars[nikcd__kon] = replace_vars_inner(join_node.
            left_vars[nikcd__kon], var_dict)
    for nikcd__kon in list(join_node.right_vars.keys()):
        join_node.right_vars[nikcd__kon] = replace_vars_inner(join_node.
            right_vars[nikcd__kon], var_dict)
    for nikcd__kon in list(join_node.out_data_vars.keys()):
        join_node.out_data_vars[nikcd__kon] = replace_vars_inner(join_node.
            out_data_vars[nikcd__kon], var_dict)
    return


ir_utils.apply_copy_propagate_extensions[Join] = apply_copies_join


def build_join_definitions(join_node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for zuk__qeqf in join_node.out_data_vars.values():
        definitions[zuk__qeqf.name].append(join_node)
    return definitions


ir_utils.build_defs_extensions[Join] = build_join_definitions


def join_distributed_run(join_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    left_parallel, right_parallel = False, False
    if array_dists is not None:
        left_parallel, right_parallel = _get_table_parallel_flags(join_node,
            array_dists)
    n_keys = len(join_node.left_keys)
    dflbl__vhbsf = tuple(join_node.left_vars[kmjh__aukba] for kmjh__aukba in
        join_node.left_keys)
    gvh__dqt = tuple(join_node.right_vars[kmjh__aukba] for kmjh__aukba in
        join_node.right_keys)
    jfb__kke = tuple(join_node.left_vars.keys())
    szjzl__yhlpw = tuple(join_node.right_vars.keys())
    ols__ieep = ()
    qejwo__vicfr = ()
    optional_column = False
    if (join_node.left_index and not join_node.right_index and not
        join_node.is_join):
        ggr__aeh = join_node.right_keys[0]
        if ggr__aeh in jfb__kke:
            qejwo__vicfr = ggr__aeh,
            ols__ieep = join_node.right_vars[ggr__aeh],
            optional_column = True
    if (join_node.right_index and not join_node.left_index and not
        join_node.is_join):
        ggr__aeh = join_node.left_keys[0]
        if ggr__aeh in szjzl__yhlpw:
            qejwo__vicfr = ggr__aeh,
            ols__ieep = join_node.left_vars[ggr__aeh],
            optional_column = True
    rbq__vdy = tuple(join_node.out_data_vars[cname] for cname in qejwo__vicfr)
    mltu__gls = tuple(eigob__pvx for sef__ztyv, eigob__pvx in sorted(
        join_node.left_vars.items(), key=lambda a: str(a[0])) if sef__ztyv
         not in join_node.left_keys)
    emho__czil = tuple(eigob__pvx for sef__ztyv, eigob__pvx in sorted(
        join_node.right_vars.items(), key=lambda a: str(a[0])) if sef__ztyv
         not in join_node.right_keys)
    ffsc__ilazs = ols__ieep + dflbl__vhbsf + gvh__dqt + mltu__gls + emho__czil
    wtxq__tbxc = tuple(typemap[eigob__pvx.name] for eigob__pvx in ffsc__ilazs)
    agb__ijcit = tuple('opti_c' + str(i) for i in range(len(ols__ieep)))
    left_other_names = tuple('t1_c' + str(i) for i in range(len(mltu__gls)))
    right_other_names = tuple('t2_c' + str(i) for i in range(len(emho__czil)))
    left_other_types = tuple([typemap[kmjh__aukba.name] for kmjh__aukba in
        mltu__gls])
    right_other_types = tuple([typemap[kmjh__aukba.name] for kmjh__aukba in
        emho__czil])
    left_key_names = tuple('t1_key' + str(i) for i in range(n_keys))
    right_key_names = tuple('t2_key' + str(i) for i in range(n_keys))
    glbs = {}
    loc = join_node.loc
    func_text = 'def f({}{}, {},{}{}{}):\n'.format('{},'.format(agb__ijcit[
        0]) if len(agb__ijcit) == 1 else '', ','.join(left_key_names), ','.
        join(right_key_names), ','.join(left_other_names), ',' if len(
        left_other_names) != 0 else '', ','.join(right_other_names))
    left_key_types = tuple(typemap[eigob__pvx.name] for eigob__pvx in
        dflbl__vhbsf)
    right_key_types = tuple(typemap[eigob__pvx.name] for eigob__pvx in gvh__dqt
        )
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
    yynqc__dhkn = []
    for cname in join_node.left_keys:
        if cname in join_node.add_suffix:
            fnajx__mtn = str(cname) + join_node.suffix_x
        else:
            fnajx__mtn = cname
        assert fnajx__mtn in join_node.out_data_vars
        yynqc__dhkn.append(join_node.out_data_vars[fnajx__mtn])
    for i, cname in enumerate(join_node.right_keys):
        if not join_node.vect_same_key[i] and not join_node.is_join:
            if cname in join_node.add_suffix:
                fnajx__mtn = str(cname) + join_node.suffix_y
            else:
                fnajx__mtn = cname
            assert fnajx__mtn in join_node.out_data_vars
            yynqc__dhkn.append(join_node.out_data_vars[fnajx__mtn])

    def _get_out_col_var(cname, is_left):
        if cname in join_node.add_suffix:
            if is_left:
                fnajx__mtn = str(cname) + join_node.suffix_x
            else:
                fnajx__mtn = str(cname) + join_node.suffix_y
        else:
            fnajx__mtn = cname
        return join_node.out_data_vars[fnajx__mtn]
    lwej__hfmm = rbq__vdy + tuple(yynqc__dhkn)
    lwej__hfmm += tuple(_get_out_col_var(sef__ztyv, True) for sef__ztyv,
        eigob__pvx in sorted(join_node.left_vars.items(), key=lambda a: str
        (a[0])) if sef__ztyv not in join_node.left_keys)
    lwej__hfmm += tuple(_get_out_col_var(sef__ztyv, False) for sef__ztyv,
        eigob__pvx in sorted(join_node.right_vars.items(), key=lambda a:
        str(a[0])) if sef__ztyv not in join_node.right_keys)
    if join_node.indicator:
        lwej__hfmm += _get_out_col_var('_merge', False),
    cmr__gkzvd = [('t3_c' + str(i)) for i in range(len(lwej__hfmm))]
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
            right_parallel, glbs, [typemap[eigob__pvx.name] for eigob__pvx in
            lwej__hfmm], join_node.loc, join_node.indicator, join_node.
            is_na_equal, general_cond_cfunc, left_col_nums, right_col_nums)
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
        func_text += f'    {cmr__gkzvd[idx]} = opti_0\n'
        idx += 1
    for i in range(n_keys):
        func_text += f'    {cmr__gkzvd[idx]} = t1_keys_{i}\n'
        idx += 1
    for i in range(n_keys):
        if not join_node.vect_same_key[i] and not join_node.is_join:
            func_text += f'    {cmr__gkzvd[idx]} = t2_keys_{i}\n'
            idx += 1
    for i in range(len(left_other_names)):
        func_text += f'    {cmr__gkzvd[idx]} = left_{i}\n'
        idx += 1
    for i in range(len(right_other_names)):
        func_text += f'    {cmr__gkzvd[idx]} = right_{i}\n'
        idx += 1
    if join_node.indicator:
        func_text += f'    {cmr__gkzvd[idx]} = indicator_col\n'
        idx += 1
    rqs__cahv = {}
    exec(func_text, {}, rqs__cahv)
    djtm__cqntp = rqs__cahv['f']
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
    qkeii__bti = compile_to_numba_ir(djtm__cqntp, glbs, typingctx=typingctx,
        targetctx=targetctx, arg_typs=wtxq__tbxc, typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(qkeii__bti, ffsc__ilazs)
    xhy__expm = qkeii__bti.body[:-3]
    for i in range(len(lwej__hfmm)):
        xhy__expm[-len(lwej__hfmm) + i].target = lwej__hfmm[i]
    return xhy__expm


distributed_pass.distributed_run_extensions[Join] = join_distributed_run


def _gen_general_cond_cfunc(join_node, typemap):
    expr = join_node.gen_cond_expr
    if not expr:
        return None, [], []
    mukr__tjspl = next_label()
    vinsg__cfb = _get_col_to_ind(join_node.left_keys, join_node.left_vars)
    zah__dfnlj = _get_col_to_ind(join_node.right_keys, join_node.right_vars)
    table_getitem_funcs = {'bodo': bodo, 'numba': numba, 'is_null_pointer':
        is_null_pointer}
    na_check_name = 'NOT_NA'
    func_text = f"""def bodo_join_gen_cond{mukr__tjspl}(left_table, right_table, left_data1, right_data1, left_null_bitmap, right_null_bitmap, left_ind, right_ind):
"""
    func_text += '  if is_null_pointer(left_table):\n'
    func_text += '    return False\n'
    expr, func_text, left_col_nums = _replace_column_accesses(expr,
        vinsg__cfb, typemap, join_node.left_vars, table_getitem_funcs,
        func_text, 'left', len(join_node.left_keys), na_check_name)
    expr, func_text, right_col_nums = _replace_column_accesses(expr,
        zah__dfnlj, typemap, join_node.right_vars, table_getitem_funcs,
        func_text, 'right', len(join_node.right_keys), na_check_name)
    func_text += f'  return {expr}'
    rqs__cahv = {}
    exec(func_text, table_getitem_funcs, rqs__cahv)
    fmi__gldz = rqs__cahv[f'bodo_join_gen_cond{mukr__tjspl}']
    pet__guwza = types.bool_(types.voidptr, types.voidptr, types.voidptr,
        types.voidptr, types.voidptr, types.voidptr, types.int64, types.int64)
    kxtjn__npyh = numba.cfunc(pet__guwza, nopython=True)(fmi__gldz)
    join_gen_cond_cfunc[kxtjn__npyh.native_name] = kxtjn__npyh
    join_gen_cond_cfunc_addr[kxtjn__npyh.native_name] = kxtjn__npyh.address
    return kxtjn__npyh, left_col_nums, right_col_nums


def _replace_column_accesses(expr, col_to_ind, typemap, col_vars,
    table_getitem_funcs, func_text, table_name, n_keys, na_check_name):
    tupp__joh = []
    for kmjh__aukba, dvoot__kuco in col_to_ind.items():
        cname = f'({table_name}.{kmjh__aukba})'
        if cname not in expr:
            continue
        wsf__ier = f'getitem_{table_name}_val_{dvoot__kuco}'
        dskpt__xwjw = f'_bodo_{table_name}_val_{dvoot__kuco}'
        srth__flucn = typemap[col_vars[kmjh__aukba].name].dtype
        if srth__flucn == types.unicode_type:
            func_text += f"""  {dskpt__xwjw}, {dskpt__xwjw}_size = {wsf__ier}({table_name}_table, {table_name}_ind)
"""
            func_text += f"""  {dskpt__xwjw} = bodo.libs.str_arr_ext.decode_utf8({dskpt__xwjw}, {dskpt__xwjw}_size)
"""
        else:
            func_text += (
                f'  {dskpt__xwjw} = {wsf__ier}({table_name}_data1, {table_name}_ind)\n'
                )
        table_getitem_funcs[wsf__ier
            ] = bodo.libs.array._gen_row_access_intrinsic(srth__flucn,
            dvoot__kuco)
        expr = expr.replace(cname, dskpt__xwjw)
        svys__cisg = f'({na_check_name}.{table_name}.{kmjh__aukba})'
        if svys__cisg in expr:
            tff__dui = typemap[col_vars[kmjh__aukba].name]
            tgsds__yzua = f'nacheck_{table_name}_val_{dvoot__kuco}'
            byy__ewgd = f'_bodo_isna_{table_name}_val_{dvoot__kuco}'
            if isinstance(tff__dui, bodo.libs.int_arr_ext.IntegerArrayType
                ) or tff__dui in [bodo.libs.bool_arr_ext.boolean_array,
                bodo.libs.str_arr_ext.string_array_type]:
                func_text += f"""  {byy__ewgd} = {tgsds__yzua}({table_name}_null_bitmap, {table_name}_ind)
"""
            else:
                func_text += f"""  {byy__ewgd} = {tgsds__yzua}({table_name}_data1, {table_name}_ind)
"""
            table_getitem_funcs[tgsds__yzua
                ] = bodo.libs.array._gen_row_na_check_intrinsic(tff__dui,
                dvoot__kuco)
            expr = expr.replace(svys__cisg, byy__ewgd)
        if dvoot__kuco >= n_keys:
            tupp__joh.append(dvoot__kuco)
    return expr, func_text, tupp__joh


def _get_col_to_ind(key_names, col_vars):
    n_keys = len(key_names)
    col_to_ind = {kmjh__aukba: i for i, kmjh__aukba in enumerate(key_names)}
    i = n_keys
    for kmjh__aukba in sorted(col_vars, key=lambda a: str(a)):
        if kmjh__aukba in key_names:
            continue
        col_to_ind[kmjh__aukba] = i
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
    mdo__ifhb = (distributed_pass.Distribution.OneD, distributed_pass.
        Distribution.OneD_Var)
    left_parallel = all(array_dists[eigob__pvx.name] in mdo__ifhb for
        eigob__pvx in join_node.left_vars.values())
    right_parallel = all(array_dists[eigob__pvx.name] in mdo__ifhb for
        eigob__pvx in join_node.right_vars.values())
    if not left_parallel:
        assert not any(array_dists[eigob__pvx.name] in mdo__ifhb for
            eigob__pvx in join_node.left_vars.values())
    if not right_parallel:
        assert not any(array_dists[eigob__pvx.name] in mdo__ifhb for
            eigob__pvx in join_node.right_vars.values())
    if left_parallel or right_parallel:
        assert all(array_dists[eigob__pvx.name] in mdo__ifhb for eigob__pvx in
            join_node.out_data_vars.values())
    return left_parallel, right_parallel


def _gen_local_hash_join(optional_column, left_key_names, right_key_names,
    left_key_types, right_key_types, left_other_names, right_other_names,
    left_other_types, right_other_types, vect_same_key, is_left, is_right,
    is_join, left_parallel, right_parallel, glbs, out_types, loc, indicator,
    is_na_equal, general_cond_cfunc, left_col_nums, right_col_nums):

    def needs_typechange(in_type, need_nullable, is_same_key):
        return isinstance(in_type, types.Array) and not is_dtype_nullable(
            in_type.dtype) and need_nullable and not is_same_key
    nrc__zlpos = []
    for i in range(len(left_key_names)):
        vzhii__nqat = _match_join_key_types(left_key_types[i],
            right_key_types[i], loc)
        nrc__zlpos.append(needs_typechange(vzhii__nqat, is_right,
            vect_same_key[i]))
    for i in range(len(left_other_names)):
        nrc__zlpos.append(needs_typechange(left_other_types[i], is_right, 
            False))
    for i in range(len(right_key_names)):
        if not vect_same_key[i] and not is_join:
            vzhii__nqat = _match_join_key_types(left_key_types[i],
                right_key_types[i], loc)
            nrc__zlpos.append(needs_typechange(vzhii__nqat, is_left, False))
    for i in range(len(right_other_names)):
        nrc__zlpos.append(needs_typechange(right_other_types[i], is_left, 
            False))

    def get_out_type(idx, in_type, in_name, need_nullable, is_same_key):
        if isinstance(in_type, types.Array) and not is_dtype_nullable(in_type
            .dtype) and need_nullable and not is_same_key:
            if isinstance(in_type.dtype, types.Integer):
                szlhw__ncgtm = IntDtype(in_type.dtype).name
                assert szlhw__ncgtm.endswith('Dtype()')
                szlhw__ncgtm = szlhw__ncgtm[:-7]
                veflo__vxoa = f"""    typ_{idx} = bodo.hiframes.pd_series_ext.get_series_data(pd.Series([1], dtype="{szlhw__ncgtm}"))
"""
                twsbp__congz = f'typ_{idx}'
            else:
                assert in_type.dtype == types.bool_, 'unexpected non-nullable type in join'
                veflo__vxoa = (
                    f'    typ_{idx} = bodo.libs.bool_arr_ext.alloc_bool_array(1)\n'
                    )
                twsbp__congz = f'typ_{idx}'
        else:
            veflo__vxoa = ''
            twsbp__congz = in_name
        return veflo__vxoa, twsbp__congz
    n_keys = len(left_key_names)
    func_text = '    # beginning of _gen_local_hash_join\n'
    frg__ovs = []
    for i in range(n_keys):
        frg__ovs.append('t1_keys[{}]'.format(i))
    for i in range(len(left_other_names)):
        frg__ovs.append('data_left[{}]'.format(i))
    func_text += '    info_list_total_l = [{}]\n'.format(','.join(
        'array_to_info({})'.format(a) for a in frg__ovs))
    func_text += '    table_left = arr_info_list_to_table(info_list_total_l)\n'
    sctn__bhss = []
    for i in range(n_keys):
        sctn__bhss.append('t2_keys[{}]'.format(i))
    for i in range(len(right_other_names)):
        sctn__bhss.append('data_right[{}]'.format(i))
    func_text += '    info_list_total_r = [{}]\n'.format(','.join(
        'array_to_info({})'.format(a) for a in sctn__bhss))
    func_text += (
        '    table_right = arr_info_list_to_table(info_list_total_r)\n')
    func_text += '    vect_same_key = np.array([{}])\n'.format(','.join('1' if
        fmkhj__cypi else '0' for fmkhj__cypi in vect_same_key))
    func_text += '    vect_need_typechange = np.array([{}])\n'.format(','.
        join('1' if fmkhj__cypi else '0' for fmkhj__cypi in nrc__zlpos))
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
    for i, qfb__wzkd in enumerate(left_key_names):
        vzhii__nqat = _match_join_key_types(left_key_types[i],
            right_key_types[i], loc)
        svp__sjsz = get_out_type(idx, vzhii__nqat, f't1_keys[{i}]',
            is_right, vect_same_key[i])
        func_text += svp__sjsz[0]
        glbs[f'out_type_{idx}'] = out_types[idx]
        if vzhii__nqat != left_key_types[i]:
            func_text += f"""    t1_keys_{i} = bodo.utils.utils.astype(info_to_array(info_from_table(out_table, {idx}), {svp__sjsz[1]}), out_type_{idx})
"""
        else:
            func_text += f"""    t1_keys_{i} = info_to_array(info_from_table(out_table, {idx}), {svp__sjsz[1]})
"""
        idx += 1
    for i, qfb__wzkd in enumerate(left_other_names):
        svp__sjsz = get_out_type(idx, left_other_types[i], qfb__wzkd,
            is_right, False)
        func_text += svp__sjsz[0]
        func_text += (
            '    left_{} = info_to_array(info_from_table(out_table, {}), {})\n'
            .format(i, idx, svp__sjsz[1]))
        idx += 1
    for i, qfb__wzkd in enumerate(right_key_names):
        if not vect_same_key[i] and not is_join:
            vzhii__nqat = _match_join_key_types(left_key_types[i],
                right_key_types[i], loc)
            svp__sjsz = get_out_type(idx, vzhii__nqat, f't2_keys[{i}]',
                is_left, False)
            func_text += svp__sjsz[0]
            glbs[f'out_type_{idx}'] = out_types[idx - len(left_other_names)]
            if vzhii__nqat != right_key_types[i]:
                func_text += f"""    t2_keys_{i} = bodo.utils.utils.astype(info_to_array(info_from_table(out_table, {idx}), {svp__sjsz[1]}), out_type_{idx})
"""
            else:
                func_text += f"""    t2_keys_{i} = info_to_array(info_from_table(out_table, {idx}), {svp__sjsz[1]})
"""
            idx += 1
    for i, qfb__wzkd in enumerate(right_other_names):
        svp__sjsz = get_out_type(idx, right_other_types[i], qfb__wzkd,
            is_left, False)
        func_text += svp__sjsz[0]
        func_text += (
            '    right_{} = info_to_array(info_from_table(out_table, {}), {})\n'
            .format(i, idx, svp__sjsz[1]))
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
    qdms__isyw = bodo.libs.distributed_api.get_size()
    piww__mge = alloc_pre_shuffle_metadata(key_arrs, data, qdms__isyw, False)
    sef__ztyv = len(key_arrs[0])
    efx__wouzh = np.empty(sef__ztyv, np.int32)
    pujq__cesap = arr_info_list_to_table([array_to_info(key_arrs[0])])
    gdzn__vxo = 1
    vpy__hkjv = compute_node_partition_by_hash(pujq__cesap, gdzn__vxo,
        qdms__isyw)
    xqf__hclbt = np.empty(1, np.int32)
    gqjt__fdf = info_to_array(info_from_table(vpy__hkjv, 0), xqf__hclbt)
    delete_table(vpy__hkjv)
    delete_table(pujq__cesap)
    for i in range(sef__ztyv):
        val = getitem_arr_tup_single(key_arrs, i)
        node_id = gqjt__fdf[i]
        efx__wouzh[i] = node_id
        update_shuffle_meta(piww__mge, node_id, i, key_arrs, data, False)
    shuffle_meta = finalize_shuffle_meta(key_arrs, data, piww__mge,
        qdms__isyw, False)
    for i in range(sef__ztyv):
        node_id = efx__wouzh[i]
        write_send_buff(shuffle_meta, node_id, i, key_arrs, data)
        shuffle_meta.tmp_offset[node_id] += 1
    jyqz__vhwwd = alltoallv_tup(key_arrs + data, shuffle_meta, key_arrs)
    yynqc__dhkn = _get_keys_tup(jyqz__vhwwd, key_arrs)
    gewxi__mad = _get_data_tup(jyqz__vhwwd, key_arrs)
    return yynqc__dhkn, gewxi__mad


@generated_jit(nopython=True, cache=True)
def parallel_shuffle(key_arrs, data):
    return parallel_join_impl


@numba.njit
def parallel_asof_comm(left_key_arrs, right_key_arrs, right_data):
    qdms__isyw = bodo.libs.distributed_api.get_size()
    xgwl__uxn = np.empty(qdms__isyw, left_key_arrs[0].dtype)
    rxg__kqn = np.empty(qdms__isyw, left_key_arrs[0].dtype)
    bodo.libs.distributed_api.allgather(xgwl__uxn, left_key_arrs[0][0])
    bodo.libs.distributed_api.allgather(rxg__kqn, left_key_arrs[0][-1])
    osex__kls = np.zeros(qdms__isyw, np.int32)
    ekbx__dauc = np.zeros(qdms__isyw, np.int32)
    rxf__stjg = np.zeros(qdms__isyw, np.int32)
    eol__hhs = right_key_arrs[0][0]
    knpo__niglh = right_key_arrs[0][-1]
    eqlnk__fhxh = -1
    i = 0
    while i < qdms__isyw - 1 and rxg__kqn[i] < eol__hhs:
        i += 1
    while i < qdms__isyw and xgwl__uxn[i] <= knpo__niglh:
        eqlnk__fhxh, vlnt__orl = _count_overlap(right_key_arrs[0],
            xgwl__uxn[i], rxg__kqn[i])
        if eqlnk__fhxh != 0:
            eqlnk__fhxh -= 1
            vlnt__orl += 1
        osex__kls[i] = vlnt__orl
        ekbx__dauc[i] = eqlnk__fhxh
        i += 1
    while i < qdms__isyw:
        osex__kls[i] = 1
        ekbx__dauc[i] = len(right_key_arrs[0]) - 1
        i += 1
    bodo.libs.distributed_api.alltoall(osex__kls, rxf__stjg, 1)
    hbu__ivrdp = rxf__stjg.sum()
    fbonc__fvjmh = np.empty(hbu__ivrdp, right_key_arrs[0].dtype)
    gyjsu__jxo = alloc_arr_tup(hbu__ivrdp, right_data)
    egxhh__niuyy = bodo.ir.join.calc_disp(rxf__stjg)
    bodo.libs.distributed_api.alltoallv(right_key_arrs[0], fbonc__fvjmh,
        osex__kls, rxf__stjg, ekbx__dauc, egxhh__niuyy)
    bodo.libs.distributed_api.alltoallv_tup(right_data, gyjsu__jxo,
        osex__kls, rxf__stjg, ekbx__dauc, egxhh__niuyy)
    return (fbonc__fvjmh,), gyjsu__jxo


@numba.njit
def _count_overlap(r_key_arr, start, end):
    vlnt__orl = 0
    eqlnk__fhxh = 0
    dph__orlj = 0
    while dph__orlj < len(r_key_arr) and r_key_arr[dph__orlj] < start:
        eqlnk__fhxh += 1
        dph__orlj += 1
    while dph__orlj < len(r_key_arr) and start <= r_key_arr[dph__orlj] <= end:
        dph__orlj += 1
        vlnt__orl += 1
    return eqlnk__fhxh, vlnt__orl


def write_send_buff(shuffle_meta, node_id, i, key_arrs, data):
    return i


@overload(write_send_buff, no_unliteral=True)
def write_data_buff_overload(meta, node_id, i, key_arrs, data):
    func_text = 'def f(meta, node_id, i, key_arrs, data):\n'
    func_text += (
        '  w_ind = meta.send_disp[node_id] + meta.tmp_offset[node_id]\n')
    n_keys = len(key_arrs.types)
    for i, ikjg__ipcxo in enumerate(key_arrs.types + data.types):
        arr = 'key_arrs[{}]'.format(i) if i < n_keys else 'data[{}]'.format(
            i - n_keys)
        if not ikjg__ipcxo in (string_type, string_array_type,
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
    rqs__cahv = {}
    exec(func_text, {'str_copy_ptr': str_copy_ptr, 'get_null_bitmap_ptr':
        get_null_bitmap_ptr, 'get_bit_bitmap': get_bit_bitmap, 'set_bit_to':
        set_bit_to, 'get_str_arr_item_length': get_str_arr_item_length,
        'get_str_arr_item_ptr': get_str_arr_item_ptr}, rqs__cahv)
    fqwa__wmdb = rqs__cahv['f']
    return fqwa__wmdb


import llvmlite.binding as ll
from bodo.libs import hdist
ll.add_symbol('c_alltoallv', hdist.c_alltoallv)


@numba.njit
def calc_disp(arr):
    hfn__tpkr = np.empty_like(arr)
    hfn__tpkr[0] = 0
    for i in range(1, len(arr)):
        hfn__tpkr[i] = hfn__tpkr[i - 1] + arr[i - 1]
    return hfn__tpkr


def ensure_capacity(arr, new_size):
    acnzn__kjm = arr
    mjbqh__mkl = len(arr)
    if mjbqh__mkl < new_size:
        fib__xwmk = 2 * mjbqh__mkl
        acnzn__kjm = bodo.utils.utils.alloc_type(fib__xwmk, arr)
        acnzn__kjm[:mjbqh__mkl] = arr
    return acnzn__kjm


@overload(ensure_capacity, no_unliteral=True)
def ensure_capacity_overload(arr, new_size):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return ensure_capacity
    assert isinstance(arr, types.BaseTuple)
    vlnt__orl = arr.count
    func_text = 'def f(arr, new_size):\n'
    func_text += '  return ({}{})\n'.format(','.join([
        'ensure_capacity(arr[{}], new_size)'.format(i) for i in range(
        vlnt__orl)]), ',' if vlnt__orl == 1 else '')
    rqs__cahv = {}
    exec(func_text, {'ensure_capacity': ensure_capacity}, rqs__cahv)
    pall__qtv = rqs__cahv['f']
    return pall__qtv


@numba.njit
def ensure_capacity_str(arr, new_size, n_chars):
    acnzn__kjm = arr
    mjbqh__mkl = len(arr)
    hghby__iijuh = num_total_chars(arr)
    ziqq__twqc = getitem_str_offset(arr, new_size - 1) + n_chars
    if mjbqh__mkl < new_size or ziqq__twqc > hghby__iijuh:
        fib__xwmk = int(2 * mjbqh__mkl if mjbqh__mkl < new_size else mjbqh__mkl
            )
        bwz__tsin = int(2 * hghby__iijuh + n_chars if ziqq__twqc >
            hghby__iijuh else hghby__iijuh)
        acnzn__kjm = pre_alloc_string_array(fib__xwmk, bwz__tsin)
        copy_str_arr_slice(acnzn__kjm, arr, new_size - 1)
    return acnzn__kjm


def trim_arr_tup(data, new_size):
    return data


@overload(trim_arr_tup, no_unliteral=True)
def trim_arr_tup_overload(data, new_size):
    assert isinstance(data, types.BaseTuple)
    vlnt__orl = data.count
    func_text = 'def f(data, new_size):\n'
    func_text += '  return ({}{})\n'.format(','.join([
        'trim_arr(data[{}], new_size)'.format(i) for i in range(vlnt__orl)]
        ), ',' if vlnt__orl == 1 else '')
    rqs__cahv = {}
    exec(func_text, {'trim_arr': trim_arr}, rqs__cahv)
    pall__qtv = rqs__cahv['f']
    return pall__qtv


def copy_elem_buff(arr, ind, val):
    acnzn__kjm = ensure_capacity(arr, ind + 1)
    acnzn__kjm[ind] = val
    return acnzn__kjm


@overload(copy_elem_buff, no_unliteral=True)
def copy_elem_buff_overload(arr, ind, val):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return copy_elem_buff
    assert arr == string_array_type

    def copy_elem_buff_str(arr, ind, val):
        acnzn__kjm = ensure_capacity_str(arr, ind + 1, get_utf8_size(val))
        acnzn__kjm[ind] = val
        return acnzn__kjm
    return copy_elem_buff_str


def copy_elem_buff_tup(arr, ind, val):
    return arr


@overload(copy_elem_buff_tup, no_unliteral=True)
def copy_elem_buff_tup_overload(data, ind, val):
    assert isinstance(data, types.BaseTuple)
    vlnt__orl = data.count
    func_text = 'def f(data, ind, val):\n'
    for i in range(vlnt__orl):
        func_text += ('  arr_{} = copy_elem_buff(data[{}], ind, val[{}])\n'
            .format(i, i, i))
    func_text += '  return ({}{})\n'.format(','.join(['arr_{}'.format(i) for
        i in range(vlnt__orl)]), ',' if vlnt__orl == 1 else '')
    rqs__cahv = {}
    exec(func_text, {'copy_elem_buff': copy_elem_buff}, rqs__cahv)
    qxtzc__fldx = rqs__cahv['f']
    return qxtzc__fldx


def trim_arr(arr, size):
    return arr[:size]


@overload(trim_arr, no_unliteral=True)
def trim_arr_overload(arr, size):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return trim_arr
    assert arr == string_array_type

    def trim_arr_str(arr, size):
        acnzn__kjm = pre_alloc_string_array(size, np.int64(
            getitem_str_offset(arr, size)))
        copy_str_arr_slice(acnzn__kjm, arr, size)
        return acnzn__kjm
    return trim_arr_str


def setnan_elem_buff(arr, ind):
    acnzn__kjm = ensure_capacity(arr, ind + 1)
    bodo.libs.array_kernels.setna(acnzn__kjm, ind)
    return acnzn__kjm


@overload(setnan_elem_buff, no_unliteral=True)
def setnan_elem_buff_overload(arr, ind):
    if isinstance(arr, types.Array) or arr == boolean_array:
        return setnan_elem_buff
    assert arr == string_array_type

    def setnan_elem_buff_str(arr, ind):
        acnzn__kjm = ensure_capacity_str(arr, ind + 1, 0)
        acnzn__kjm[ind] = ''
        bodo.libs.array_kernels.setna(acnzn__kjm, ind)
        return acnzn__kjm
    return setnan_elem_buff_str


def setnan_elem_buff_tup(arr, ind):
    return arr


@overload(setnan_elem_buff_tup, no_unliteral=True)
def setnan_elem_buff_tup_overload(data, ind):
    assert isinstance(data, types.BaseTuple)
    vlnt__orl = data.count
    func_text = 'def f(data, ind):\n'
    for i in range(vlnt__orl):
        func_text += '  arr_{} = setnan_elem_buff(data[{}], ind)\n'.format(i, i
            )
    func_text += '  return ({}{})\n'.format(','.join(['arr_{}'.format(i) for
        i in range(vlnt__orl)]), ',' if vlnt__orl == 1 else '')
    rqs__cahv = {}
    exec(func_text, {'setnan_elem_buff': setnan_elem_buff}, rqs__cahv)
    qxtzc__fldx = rqs__cahv['f']
    return qxtzc__fldx


@generated_jit(nopython=True, cache=True)
def _check_ind_if_hashed(right_keys, r_ind, l_key):
    if right_keys == types.Tuple((types.intp[::1],)):
        return lambda right_keys, r_ind, l_key: r_ind

    def _impl(right_keys, r_ind, l_key):
        ujx__prx = getitem_arr_tup(right_keys, r_ind)
        if ujx__prx != l_key:
            return -1
        return r_ind
    return _impl


@numba.njit
def local_merge_asof(left_keys, right_keys, data_left, data_right):
    fduqh__bzd = len(left_keys[0])
    wwgxf__vzsqb = len(right_keys[0])
    jnv__nirhv = alloc_arr_tup(fduqh__bzd, left_keys)
    nbtsp__oaj = alloc_arr_tup(fduqh__bzd, right_keys)
    ynujc__ssxld = alloc_arr_tup(fduqh__bzd, data_left)
    sad__lxqs = alloc_arr_tup(fduqh__bzd, data_right)
    furw__igg = 0
    ozs__fgjta = 0
    for furw__igg in range(fduqh__bzd):
        if ozs__fgjta < 0:
            ozs__fgjta = 0
        while ozs__fgjta < wwgxf__vzsqb and getitem_arr_tup(right_keys,
            ozs__fgjta) <= getitem_arr_tup(left_keys, furw__igg):
            ozs__fgjta += 1
        ozs__fgjta -= 1
        setitem_arr_tup(jnv__nirhv, furw__igg, getitem_arr_tup(left_keys,
            furw__igg))
        setitem_arr_tup(ynujc__ssxld, furw__igg, getitem_arr_tup(data_left,
            furw__igg))
        if ozs__fgjta >= 0:
            setitem_arr_tup(nbtsp__oaj, furw__igg, getitem_arr_tup(
                right_keys, ozs__fgjta))
            setitem_arr_tup(sad__lxqs, furw__igg, getitem_arr_tup(
                data_right, ozs__fgjta))
        else:
            bodo.libs.array_kernels.setna_tup(nbtsp__oaj, furw__igg)
            bodo.libs.array_kernels.setna_tup(sad__lxqs, furw__igg)
    return jnv__nirhv, nbtsp__oaj, ynujc__ssxld, sad__lxqs


def copy_arr_tup(arrs):
    return tuple(a.copy() for a in arrs)


@overload(copy_arr_tup, no_unliteral=True)
def copy_arr_tup_overload(arrs):
    vlnt__orl = arrs.count
    func_text = 'def f(arrs):\n'
    func_text += '  return ({},)\n'.format(','.join('arrs[{}].copy()'.
        format(i) for i in range(vlnt__orl)))
    rqs__cahv = {}
    exec(func_text, {}, rqs__cahv)
    impl = rqs__cahv['f']
    return impl


def get_nan_bits(arr, ind):
    return 0


@overload(get_nan_bits, no_unliteral=True)
def overload_get_nan_bits(arr, ind):
    if arr == string_array_type:

        def impl_str(arr, ind):
            gtj__sboi = get_null_bitmap_ptr(arr)
            return get_bit_bitmap(gtj__sboi, ind)
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
    vlnt__orl = arr_tup.count
    func_text = 'def f(arr_tup, ind):\n'
    func_text += '  return ({}{})\n'.format(','.join([
        'get_nan_bits(arr_tup[{}], ind)'.format(i) for i in range(vlnt__orl
        )]), ',' if vlnt__orl == 1 else '')
    rqs__cahv = {}
    exec(func_text, {'get_nan_bits': get_nan_bits}, rqs__cahv)
    impl = rqs__cahv['f']
    return impl


def set_nan_bits(arr, ind, na_val):
    return 0


@overload(set_nan_bits, no_unliteral=True)
def overload_set_nan_bits(arr, ind, na_val):
    if arr == string_array_type:

        def impl_str(arr, ind, na_val):
            gtj__sboi = get_null_bitmap_ptr(arr)
            set_bit_to(gtj__sboi, ind, na_val)
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
    vlnt__orl = arr_tup.count
    func_text = 'def f(arr_tup, ind, na_val):\n'
    for i in range(vlnt__orl):
        func_text += '  set_nan_bits(arr_tup[{}], ind, na_val[{}])\n'.format(i,
            i)
    func_text += '  return\n'
    rqs__cahv = {}
    exec(func_text, {'set_nan_bits': set_nan_bits}, rqs__cahv)
    impl = rqs__cahv['f']
    return impl
