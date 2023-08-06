import os
import warnings
from collections import defaultdict
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
import pyarrow
import pyarrow.dataset as ds
from numba.core import ir, types
from numba.core.ir_utils import compile_to_numba_ir, get_definition, guard, mk_unique_var, next_label, replace_arg_nodes
from numba.extending import NativeValue, intrinsic, models, overload, register_model, unbox
from pyarrow import null
import bodo
import bodo.ir.parquet_ext
import bodo.utils.tracing as tracing
from bodo.hiframes.datetime_date_ext import datetime_date_array_type, datetime_date_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.table import TableType
from bodo.io.fs_io import get_hdfs_fs, get_s3_fs_from_path, get_s3_subtree_fs
from bodo.libs.array import cpp_table_to_py_table, delete_table, info_from_table, info_to_array, table_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.binary_arr_ext import binary_array_type, bytes_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType
from bodo.libs.distributed_api import get_end, get_start
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import string_array_type
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.libs.struct_arr_ext import StructArrayType
from bodo.transforms import distributed_pass
from bodo.utils.transform import get_const_value
from bodo.utils.typing import BodoError, BodoWarning, FileInfo, get_overload_const_str, get_overload_constant_dict
from bodo.utils.utils import check_and_propagate_cpp_exception, numba_to_c_type, sanitize_varname
use_nullable_int_arr = True
from urllib.parse import urlparse
import bodo.io.pa_parquet
REMOTE_FILESYSTEMS = {'s3', 'gcs', 'gs', 'http', 'hdfs', 'abfs', 'abfss'}


class ParquetPredicateType(types.Type):

    def __init__(self):
        super(ParquetPredicateType, self).__init__(name=
            'ParquetPredicateType()')


parquet_predicate_type = ParquetPredicateType()
types.parquet_predicate_type = parquet_predicate_type
register_model(ParquetPredicateType)(models.OpaqueModel)


@unbox(ParquetPredicateType)
def unbox_parquet_predicate_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


class ReadParquetFilepathType(types.Opaque):

    def __init__(self):
        super(ReadParquetFilepathType, self).__init__(name=
            'ReadParquetFilepathType')


read_parquet_fpath_type = ReadParquetFilepathType()
types.read_parquet_fpath_type = read_parquet_fpath_type
register_model(ReadParquetFilepathType)(models.OpaqueModel)


@unbox(ReadParquetFilepathType)
def unbox_read_parquet_fpath_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


class StorageOptionsDictType(types.Opaque):

    def __init__(self):
        super(StorageOptionsDictType, self).__init__(name=
            'StorageOptionsDictType')


storage_options_dict_type = StorageOptionsDictType()
types.storage_options_dict_type = storage_options_dict_type
register_model(StorageOptionsDictType)(models.OpaqueModel)


@unbox(StorageOptionsDictType)
def unbox_storage_options_dict_type(typ, val, c):
    c.pyapi.incref(val)
    return NativeValue(val)


class ParquetFileInfo(FileInfo):

    def __init__(self, columns, storage_options=None):
        self.columns = columns
        self.storage_options = storage_options
        super().__init__()

    def _get_schema(self, fname):
        try:
            return parquet_file_schema(fname, selected_columns=self.columns,
                storage_options=self.storage_options)
        except OSError as ybv__ram:
            if 'non-file path' in str(ybv__ram):
                raise FileNotFoundError(str(ybv__ram))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=None):
        dgly__urfel = lhs.scope
        eqc__suwo = lhs.loc
        hddg__zszbj = None
        if lhs.name in self.locals:
            hddg__zszbj = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        sahaj__mphaw = {}
        if lhs.name + ':convert' in self.locals:
            sahaj__mphaw = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if hddg__zszbj is None:
            hqhi__ohfic = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/source/programming_with_bodo/file_io.html#non-constant-filepaths'
                )
            yzst__gawg = get_const_value(file_name, self.func_ir,
                hqhi__ohfic, arg_types=self.args, file_info=ParquetFileInfo
                (columns, storage_options=storage_options))
            phwc__qttn = False
            ojogi__yodj = guard(get_definition, self.func_ir, file_name)
            if isinstance(ojogi__yodj, ir.Arg):
                typ = self.args[ojogi__yodj.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, iyx__goih, zfs__dtm, col_indices,
                        partition_names) = typ.schema
                    phwc__qttn = True
            if not phwc__qttn:
                (col_names, iyx__goih, zfs__dtm, col_indices, partition_names
                    ) = (parquet_file_schema(yzst__gawg, columns,
                    storage_options=storage_options))
        else:
            mzqa__bij = list(hddg__zszbj.keys())
            vvrr__ffo = {c: zidwa__dpnw for zidwa__dpnw, c in enumerate(
                mzqa__bij)}
            rqtn__uoo = [wjfr__ggztl for wjfr__ggztl in hddg__zszbj.values()]
            zfs__dtm = 'index' if 'index' in vvrr__ffo else None
            if columns is None:
                selected_columns = mzqa__bij
            else:
                selected_columns = columns
            col_indices = [vvrr__ffo[c] for c in selected_columns]
            iyx__goih = [rqtn__uoo[vvrr__ffo[c]] for c in selected_columns]
            col_names = selected_columns
            zfs__dtm = zfs__dtm if zfs__dtm in col_names else None
            partition_names = []
        hqh__yha = None if isinstance(zfs__dtm, dict
            ) or zfs__dtm is None else zfs__dtm
        index_column_index = None
        index_column_type = types.none
        if hqh__yha:
            twn__fmefa = col_names.index(hqh__yha)
            col_indices = col_indices.copy()
            iyx__goih = iyx__goih.copy()
            index_column_index = col_indices.pop(twn__fmefa)
            index_column_type = iyx__goih.pop(twn__fmefa)
        for zidwa__dpnw, c in enumerate(col_names):
            if c in sahaj__mphaw:
                iyx__goih[zidwa__dpnw] = sahaj__mphaw[c]
        yjdba__ukf = [ir.Var(dgly__urfel, mk_unique_var('pq_table'),
            eqc__suwo), ir.Var(dgly__urfel, mk_unique_var('pq_index'),
            eqc__suwo)]
        zvj__amu = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.name,
            col_names, col_indices, iyx__goih, yjdba__ukf, eqc__suwo,
            partition_names, storage_options, index_column_index,
            index_column_type)]
        return (col_names, yjdba__ukf, zfs__dtm, zvj__amu, iyx__goih,
            index_column_type)


def determine_filter_cast(pq_node, typemap, filter_val, orig_colname_map):
    bmoed__lnwec = filter_val[0]
    ybld__mfhei = pq_node.original_out_types[orig_colname_map[bmoed__lnwec]]
    fnfvd__xqwk = bodo.utils.typing.element_type(ybld__mfhei)
    if bmoed__lnwec in pq_node.partition_names:
        if fnfvd__xqwk == types.unicode_type:
            yde__iby = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(fnfvd__xqwk, types.Integer):
            yde__iby = f'.cast(pyarrow.{fnfvd__xqwk.name}(), safe=False)'
        else:
            yde__iby = ''
    else:
        yde__iby = ''
    becic__palc = typemap[filter_val[2].name]
    if not bodo.utils.typing.is_common_scalar_dtype([fnfvd__xqwk, becic__palc]
        ):
        if not bodo.utils.typing.is_safe_arrow_cast(fnfvd__xqwk, becic__palc):
            raise BodoError(
                f'Unsupport Arrow cast from {fnfvd__xqwk} to {becic__palc} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if fnfvd__xqwk == types.unicode_type:
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif fnfvd__xqwk in (bodo.datetime64ns, bodo.pd_timestamp_type):
            return yde__iby, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return yde__iby, ''


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    aszcu__qrxg = len(pq_node.out_vars)
    extra_args = ''
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    hbd__mndhq, qfwjq__fej = bodo.ir.connector.generate_filter_map(pq_node.
        filters)
    if pq_node.filters:
        iyqq__vpn = []
        ocuto__ivpfg = []
        xjiax__gslxz = False
        apkol__qnvsq = None
        orig_colname_map = {c: zidwa__dpnw for zidwa__dpnw, c in enumerate(
            pq_node.original_df_colnames)}
        for fjyp__fafgk in pq_node.filters:
            febgm__cmb = []
            nssxs__zaht = []
            mhty__jlqip = set()
            for tpfil__zysa in fjyp__fafgk:
                if isinstance(tpfil__zysa[2], ir.Var):
                    wvp__lbnr, topw__naa = determine_filter_cast(pq_node,
                        typemap, tpfil__zysa, orig_colname_map)
                    nssxs__zaht.append(
                        f"(ds.field('{tpfil__zysa[0]}'){wvp__lbnr} {tpfil__zysa[1]} ds.scalar({hbd__mndhq[tpfil__zysa[2].name]}){topw__naa})"
                        )
                else:
                    assert tpfil__zysa[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if tpfil__zysa[1] == 'is not':
                        prefix = '~'
                    else:
                        prefix = ''
                    nssxs__zaht.append(
                        f"({prefix}ds.field('{tpfil__zysa[0]}').is_null())")
                if tpfil__zysa[0] in pq_node.partition_names and isinstance(
                    tpfil__zysa[2], ir.Var):
                    pgn__aenc = (
                        f"('{tpfil__zysa[0]}', '{tpfil__zysa[1]}', {hbd__mndhq[tpfil__zysa[2].name]})"
                        )
                    febgm__cmb.append(pgn__aenc)
                    mhty__jlqip.add(pgn__aenc)
                else:
                    xjiax__gslxz = True
            if apkol__qnvsq is None:
                apkol__qnvsq = mhty__jlqip
            else:
                apkol__qnvsq.intersection_update(mhty__jlqip)
            iwypf__rql = ', '.join(febgm__cmb)
            fpoi__kdja = ' & '.join(nssxs__zaht)
            if iwypf__rql:
                iyqq__vpn.append(f'[{iwypf__rql}]')
            ocuto__ivpfg.append(f'({fpoi__kdja})')
        ancyn__cida = ', '.join(iyqq__vpn)
        yzhja__jeduj = ' | '.join(ocuto__ivpfg)
        if xjiax__gslxz:
            if apkol__qnvsq:
                tmhkf__vaohj = sorted(apkol__qnvsq)
                dnf_filter_str = f"[[{', '.join(tmhkf__vaohj)}]]"
        elif ancyn__cida:
            dnf_filter_str = f'[{ancyn__cida}]'
        expr_filter_str = f'({yzhja__jeduj})'
        extra_args = ', '.join(hbd__mndhq.values())
    aqb__vill = ', '.join(f'out{zidwa__dpnw}' for zidwa__dpnw in range(
        aszcu__qrxg))
    notii__iqsz = f'def pq_impl(fname, {extra_args}):\n'
    notii__iqsz += (
        f'    (total_rows, {aqb__vill},) = _pq_reader_py(fname, {extra_args})\n'
        )
    tvpj__fvo = {}
    exec(notii__iqsz, {}, tvpj__fvo)
    var__kbo = tvpj__fvo['pq_impl']
    parallel = False
    if array_dists is not None:
        dbe__ugk = pq_node.out_vars[0].name
        parallel = array_dists[dbe__ugk] in (distributed_pass.Distribution.
            OneD, distributed_pass.Distribution.OneD_Var)
        xxuh__xeq = pq_node.out_vars[1].name
        assert typemap[xxuh__xeq] == types.none or not parallel or array_dists[
            xxuh__xeq] in (distributed_pass.Distribution.OneD,
            distributed_pass.Distribution.OneD_Var
            ), 'pq data/index parallelization does not match'
    usl__uojlc = _gen_pq_reader_py(pq_node.df_colnames, pq_node.col_indices,
        pq_node.type_usecol_offset, pq_node.out_types, pq_node.
        storage_options, pq_node.partition_names, dnf_filter_str,
        expr_filter_str, extra_args, parallel, meta_head_only_info, pq_node
        .index_column_index, pq_node.index_column_type)
    tqny__hcn = typemap[pq_node.file_name.name]
    ztehc__slsze = (tqny__hcn,) + tuple(typemap[tpfil__zysa.name] for
        tpfil__zysa in qfwjq__fej)
    vyc__vvh = compile_to_numba_ir(var__kbo, {'_pq_reader_py': usl__uojlc},
        typingctx=typingctx, targetctx=targetctx, arg_typs=ztehc__slsze,
        typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(vyc__vvh, [pq_node.file_name] + qfwjq__fej)
    zvj__amu = vyc__vvh.body[:-3]
    if meta_head_only_info:
        zvj__amu[-1 - aszcu__qrxg].target = meta_head_only_info[1]
    zvj__amu[-2].target = pq_node.out_vars[0]
    zvj__amu[-1].target = pq_node.out_vars[1]
    return zvj__amu


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    eok__dwe = get_overload_const_str(dnf_filter_str)
    zcapy__itzaz = get_overload_const_str(expr_filter_str)
    nii__kcza = ', '.join(f'f{zidwa__dpnw}' for zidwa__dpnw in range(len(
        var_tup)))
    notii__iqsz = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        notii__iqsz += f'  {nii__kcza}, = var_tup\n'
    notii__iqsz += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    notii__iqsz += f'    dnf_filters_py = {eok__dwe}\n'
    notii__iqsz += f'    expr_filters_py = {zcapy__itzaz}\n'
    notii__iqsz += '  return (dnf_filters_py, expr_filters_py)\n'
    tvpj__fvo = {}
    exec(notii__iqsz, globals(), tvpj__fvo)
    return tvpj__fvo['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def get_storage_options_pyobject(storage_options):
    pass


@overload(get_storage_options_pyobject, no_unliteral=True)
def overload_get_storage_options_pyobject(storage_options):
    jbq__qjmpr = get_overload_constant_dict(storage_options)
    notii__iqsz = 'def impl(storage_options):\n'
    notii__iqsz += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    notii__iqsz += f'    storage_options_py = {str(jbq__qjmpr)}\n'
    notii__iqsz += '  return storage_options_py\n'
    tvpj__fvo = {}
    exec(notii__iqsz, globals(), tvpj__fvo)
    return tvpj__fvo['impl']


def _gen_pq_reader_py(col_names, col_indices, type_usecol_offset, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type):
    aycz__xdv = next_label()
    cginb__djzd = ',' if extra_args else ''
    notii__iqsz = f'def pq_reader_py(fname,{extra_args}):\n'
    notii__iqsz += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    notii__iqsz += "    ev.add_attribute('fname', fname)\n"
    notii__iqsz += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={is_parallel})
"""
    notii__iqsz += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{cginb__djzd}))
"""
    notii__iqsz += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    notii__iqsz += f"""    storage_options_py = get_storage_options_pyobject({str(storage_options)})
"""
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    aaw__nshv = not type_usecol_offset
    puq__pqmk = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    lzd__mjo = {c: zidwa__dpnw for zidwa__dpnw, c in enumerate(col_indices)}
    mjs__wzwxy = {c: zidwa__dpnw for zidwa__dpnw, c in enumerate(puq__pqmk)}
    nquc__umvu = []
    gwbh__ieqr = set()
    for zidwa__dpnw in type_usecol_offset:
        if puq__pqmk[zidwa__dpnw] not in partition_names:
            nquc__umvu.append(col_indices[zidwa__dpnw])
        else:
            gwbh__ieqr.add(col_indices[zidwa__dpnw])
    if index_column_index is not None:
        nquc__umvu.append(index_column_index)
    nquc__umvu = sorted(nquc__umvu)
    chkby__ruzd = {c: zidwa__dpnw for zidwa__dpnw, c in enumerate(nquc__umvu)}

    def is_nullable(typ):
        return bodo.utils.utils.is_array_typ(typ, False) and not isinstance(typ
            , types.Array)
    lln__diqia = [(int(is_nullable(out_types[lzd__mjo[geysw__dig]])) if 
        geysw__dig != index_column_index else int(is_nullable(
        index_column_type))) for geysw__dig in nquc__umvu]
    gryd__fmdn = []
    xafbs__nqz = {}
    orpp__prs = []
    miafs__llt = []
    for zidwa__dpnw, uyr__xnfou in enumerate(partition_names):
        try:
            paxa__lce = mjs__wzwxy[uyr__xnfou]
            if col_indices[paxa__lce] not in gwbh__ieqr:
                continue
        except (KeyError, ValueError) as hczk__asji:
            continue
        xafbs__nqz[uyr__xnfou] = len(gryd__fmdn)
        gryd__fmdn.append(uyr__xnfou)
        orpp__prs.append(zidwa__dpnw)
        fko__vnf = out_types[paxa__lce].dtype
        rupto__buke = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            fko__vnf)
        miafs__llt.append(numba_to_c_type(rupto__buke))
    notii__iqsz += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    if len(orpp__prs) > 0:
        notii__iqsz += f"""    out_table = pq_read(fname_py, {is_parallel}, unicode_to_utf8(bucket_region), dnf_filters, expr_filters, storage_options_py, {tot_rows_to_read}, selected_cols_arr_{aycz__xdv}.ctypes, {len(nquc__umvu)}, nullable_cols_arr_{aycz__xdv}.ctypes, np.array({orpp__prs}, dtype=np.int32).ctypes, np.array({miafs__llt}, dtype=np.int32).ctypes, {len(orpp__prs)}, total_rows_np.ctypes)
"""
    else:
        notii__iqsz += f"""    out_table = pq_read(fname_py, {is_parallel}, unicode_to_utf8(bucket_region), dnf_filters, expr_filters, storage_options_py, {tot_rows_to_read}, selected_cols_arr_{aycz__xdv}.ctypes, {len(nquc__umvu)}, nullable_cols_arr_{aycz__xdv}.ctypes, 0, 0, 0, total_rows_np.ctypes)
"""
    notii__iqsz += '    check_and_propagate_cpp_exception()\n'
    useua__fdmp = 'None'
    fjnyt__vifm = index_column_type
    kgxrp__qvov = TableType(tuple(out_types))
    if aaw__nshv:
        kgxrp__qvov = types.none
    if index_column_index is not None:
        bxogf__trk = chkby__ruzd[index_column_index]
        useua__fdmp = (
            f'info_to_array(info_from_table(out_table, {bxogf__trk}), index_arr_type)'
            )
    notii__iqsz += f'    index_arr = {useua__fdmp}\n'
    if aaw__nshv:
        oue__wnid = None
    else:
        oue__wnid = []
        fylaz__uej = 0
        for zidwa__dpnw, mdv__yzs in enumerate(col_indices):
            if fylaz__uej < len(type_usecol_offset
                ) and zidwa__dpnw == type_usecol_offset[fylaz__uej]:
                ggyy__kjgi = col_indices[zidwa__dpnw]
                if ggyy__kjgi in gwbh__ieqr:
                    qzo__qutu = puq__pqmk[zidwa__dpnw]
                    oue__wnid.append(len(nquc__umvu) + xafbs__nqz[qzo__qutu])
                else:
                    oue__wnid.append(chkby__ruzd[mdv__yzs])
                fylaz__uej += 1
            else:
                oue__wnid.append(-1)
        oue__wnid = np.array(oue__wnid, dtype=np.int64)
    if aaw__nshv:
        notii__iqsz += '    T = None\n'
    else:
        notii__iqsz += f"""    T = cpp_table_to_py_table(out_table, table_idx_{aycz__xdv}, py_table_type_{aycz__xdv})
"""
    notii__iqsz += '    delete_table(out_table)\n'
    notii__iqsz += f'    total_rows = total_rows_np[0]\n'
    notii__iqsz += f'    ev.finalize()\n'
    notii__iqsz += '    return (total_rows, T, index_arr)\n'
    tvpj__fvo = {}
    ifdmw__gaeya = {f'py_table_type_{aycz__xdv}': kgxrp__qvov,
        f'table_idx_{aycz__xdv}': oue__wnid,
        f'selected_cols_arr_{aycz__xdv}': np.array(nquc__umvu, np.int32),
        f'nullable_cols_arr_{aycz__xdv}': np.array(lln__diqia, np.int32),
        'index_arr_type': fjnyt__vifm, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo}
    exec(notii__iqsz, ifdmw__gaeya, tvpj__fvo)
    usl__uojlc = tvpj__fvo['pq_reader_py']
    fsj__muht = numba.njit(usl__uojlc, no_cpython_wrapper=True)
    return fsj__muht


import pyarrow as pa
_pa_numba_typ_map = {pa.bool_(): types.bool_, pa.int8(): types.int8, pa.
    int16(): types.int16, pa.int32(): types.int32, pa.int64(): types.int64,
    pa.uint8(): types.uint8, pa.uint16(): types.uint16, pa.uint32(): types.
    uint32, pa.uint64(): types.uint64, pa.float32(): types.float32, pa.
    float64(): types.float64, pa.string(): string_type, pa.binary():
    bytes_type, pa.date32(): datetime_date_type, pa.date64(): types.
    NPDatetime('ns'), pa.timestamp('ns'): types.NPDatetime('ns'), pa.
    timestamp('us'): types.NPDatetime('ns'), pa.timestamp('ms'): types.
    NPDatetime('ns'), pa.timestamp('s'): types.NPDatetime('ns'), null():
    string_type}


def _get_numba_typ_from_pa_typ(pa_typ, is_index, nullable_from_metadata,
    category_info):
    if isinstance(pa_typ.type, pa.ListType):
        return ArrayItemArrayType(_get_numba_typ_from_pa_typ(pa_typ.type.
            value_field, is_index, nullable_from_metadata, category_info))
    if isinstance(pa_typ.type, pa.StructType):
        zbyh__spn = []
        mqrw__ncn = []
        for dkvmi__hcxqi in pa_typ.flatten():
            mqrw__ncn.append(dkvmi__hcxqi.name.split('.')[-1])
            zbyh__spn.append(_get_numba_typ_from_pa_typ(dkvmi__hcxqi,
                is_index, nullable_from_metadata, category_info))
        return StructArrayType(tuple(zbyh__spn), tuple(mqrw__ncn))
    if isinstance(pa_typ.type, pa.Decimal128Type):
        return DecimalArrayType(pa_typ.type.precision, pa_typ.type.scale)
    if isinstance(pa_typ.type, pa.DictionaryType):
        if pa_typ.type.value_type != pa.string():
            raise BodoError(
                f'Parquet Categorical data type should be string, not {pa_typ.type.value_type}'
                )
        mimxs__mouos = _pa_numba_typ_map[pa_typ.type.index_type]
        jhuj__brboh = PDCategoricalDtype(category_info[pa_typ.name], bodo.
            string_type, pa_typ.type.ordered, int_type=mimxs__mouos)
        return CategoricalArrayType(jhuj__brboh)
    if pa_typ.type not in _pa_numba_typ_map:
        raise BodoError('Arrow data type {} not supported yet'.format(
            pa_typ.type))
    emara__kgdz = _pa_numba_typ_map[pa_typ.type]
    if emara__kgdz == datetime_date_type:
        return datetime_date_array_type
    if emara__kgdz == bytes_type:
        return binary_array_type
    mqn__wjpy = (string_array_type if emara__kgdz == string_type else types
        .Array(emara__kgdz, 1, 'C'))
    if emara__kgdz == types.bool_:
        mqn__wjpy = boolean_array
    if nullable_from_metadata is not None:
        geuk__wgjwa = nullable_from_metadata
    else:
        geuk__wgjwa = use_nullable_int_arr
    if geuk__wgjwa and not is_index and isinstance(emara__kgdz, types.Integer
        ) and pa_typ.nullable:
        mqn__wjpy = IntegerArrayType(emara__kgdz)
    return mqn__wjpy


def get_parquet_dataset(fpath, get_row_counts=True, dnf_filters=None,
    expr_filters=None, storage_options=None, read_categories=False,
    is_parallel=False, tot_rows_to_read=None):
    if get_row_counts:
        jvgwn__aqqod = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    gpwfd__uyxkv = MPI.COMM_WORLD
    if isinstance(fpath, list):
        isiji__redi = urlparse(fpath[0])
        protocol = isiji__redi.scheme
        jhyls__ydk = isiji__redi.netloc
        for zidwa__dpnw in range(len(fpath)):
            jeo__qpmbh = fpath[zidwa__dpnw]
            yki__ssjt = urlparse(jeo__qpmbh)
            if yki__ssjt.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if yki__ssjt.netloc != jhyls__ydk:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[zidwa__dpnw] = jeo__qpmbh.rstrip('/')
    else:
        isiji__redi = urlparse(fpath)
        protocol = isiji__redi.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as hczk__asji:
            sznwb__fjmi = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(sznwb__fjmi)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as hczk__asji:
            sznwb__fjmi = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
"""
    fs = []

    def getfs(parallel=False):
        if len(fs) == 1:
            return fs[0]
        if protocol == 's3':
            fs.append(get_s3_fs_from_path(fpath, parallel=parallel,
                storage_options=storage_options) if not isinstance(fpath,
                list) else get_s3_fs_from_path(fpath[0], parallel=parallel,
                storage_options=storage_options))
        elif protocol in {'gcs', 'gs'}:
            oefvu__hvxs = gcsfs.GCSFileSystem(token=None)
            fs.append(oefvu__hvxs)
        elif protocol == 'http':
            fs.append(fsspec.filesystem('http'))
        elif protocol in {'hdfs', 'abfs', 'abfss'}:
            fs.append(get_hdfs_fs(fpath) if not isinstance(fpath, list) else
                get_hdfs_fs(fpath[0]))
        else:
            fs.append(None)
        return fs[0]

    def get_legacy_fs():
        if protocol in {'s3', 'hdfs', 'abfs', 'abfss'}:
            from fsspec.implementations.arrow import ArrowFSWrapper
            return ArrowFSWrapper(getfs())
        else:
            return getfs()

    def glob(protocol, fs, path):
        if not protocol and fs is None:
            from fsspec.implementations.local import LocalFileSystem
            fs = LocalFileSystem()
        if isinstance(fs, pyarrow.fs.FileSystem):
            from fsspec.implementations.arrow import ArrowFSWrapper
            fs = ArrowFSWrapper(fs)
        try:
            if protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{isiji__redi.netloc}'
                path = path[len(prefix):]
            nllx__mhit = fs.glob(path)
            if protocol == 's3':
                nllx__mhit = [('s3://' + jeo__qpmbh) for jeo__qpmbh in
                    nllx__mhit if not jeo__qpmbh.startswith('s3://')]
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                nllx__mhit = [(prefix + jeo__qpmbh) for jeo__qpmbh in
                    nllx__mhit]
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(nllx__mhit) == 0:
            raise BodoError('No files found matching glob pattern')
        return nllx__mhit
    cfu__gpfn = False
    if get_row_counts:
        xmf__ulxi = getfs(parallel=True)
        cfu__gpfn = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        bkjd__ryk = 1
        eycz__ssj = os.cpu_count()
        if eycz__ssj is not None and eycz__ssj > 1:
            bkjd__ryk = eycz__ssj // 2
        try:
            if get_row_counts:
                hxt__awkg = tracing.Event('pq.ParquetDataset', is_parallel=
                    False)
                if tracing.is_tracing():
                    hxt__awkg.add_attribute('dnf_filter', str(dnf_filters))
            eibxg__mcia = pa.io_thread_count()
            pa.set_io_thread_count(bkjd__ryk)
            if '*' in fpath:
                fpath = glob(protocol, getfs(), fpath)
            if protocol == 's3':
                if isinstance(fpath, list):
                    get_legacy_fs().info(fpath[0])
                else:
                    get_legacy_fs().info(fpath)
            if protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{isiji__redi.netloc}'
                if isinstance(fpath, list):
                    zfdz__zfpkq = [jeo__qpmbh[len(prefix):] for jeo__qpmbh in
                        fpath]
                else:
                    zfdz__zfpkq = fpath[len(prefix):]
            else:
                zfdz__zfpkq = fpath
            ktywx__hqrmj = pq.ParquetDataset(zfdz__zfpkq, filesystem=
                get_legacy_fs(), filters=None, use_legacy_dataset=True,
                validate_schema=False, metadata_nthreads=bkjd__ryk)
            pa.set_io_thread_count(eibxg__mcia)
            cuacn__wjhtu = bodo.io.pa_parquet.get_dataset_schema(ktywx__hqrmj)
            if dnf_filters:
                if get_row_counts:
                    hxt__awkg.add_attribute('num_pieces_before_filter', len
                        (ktywx__hqrmj.pieces))
                ctsk__qni = time.time()
                ktywx__hqrmj._filter(dnf_filters)
                if get_row_counts:
                    hxt__awkg.add_attribute('dnf_filter_time', time.time() -
                        ctsk__qni)
                    hxt__awkg.add_attribute('num_pieces_after_filter', len(
                        ktywx__hqrmj.pieces))
            if get_row_counts:
                hxt__awkg.finalize()
            ktywx__hqrmj._metadata.fs = None
        except Exception as ybv__ram:
            gpwfd__uyxkv.bcast(ybv__ram)
            raise BodoError(
                f'error from pyarrow: {type(ybv__ram).__name__}: {str(ybv__ram)}\n'
                )
        if get_row_counts:
            auxk__hmc = tracing.Event('bcast dataset')
        gpwfd__uyxkv.bcast(ktywx__hqrmj)
        gpwfd__uyxkv.bcast(cuacn__wjhtu)
    else:
        if get_row_counts:
            auxk__hmc = tracing.Event('bcast dataset')
        ktywx__hqrmj = gpwfd__uyxkv.bcast(None)
        if isinstance(ktywx__hqrmj, Exception):
            bcchh__rrc = ktywx__hqrmj
            raise BodoError(
                f'error from pyarrow: {type(bcchh__rrc).__name__}: {str(bcchh__rrc)}\n'
                )
        cuacn__wjhtu = gpwfd__uyxkv.bcast(None)
    if get_row_counts:
        auxk__hmc.finalize()
    ktywx__hqrmj._bodo_total_rows = 0
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = cfu__gpfn = False
        for ookpr__euk in ktywx__hqrmj.pieces:
            ookpr__euk._bodo_num_rows = 0
    if get_row_counts or cfu__gpfn:
        if get_row_counts and tracing.is_tracing():
            yzrwf__gbvvh = tracing.Event('get_row_counts')
            yzrwf__gbvvh.add_attribute('g_num_pieces', len(ktywx__hqrmj.pieces)
                )
            yzrwf__gbvvh.add_attribute('g_expr_filters', str(expr_filters))
        enhh__hzf = 0.0
        num_pieces = len(ktywx__hqrmj.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        jbw__zal = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        plvbv__unbu = 0
        chrj__mwmpo = 0
        doy__uwbll = 0
        ycbl__jchoy = True
        ktywx__hqrmj._metadata.fs = getfs()
        if expr_filters is not None:
            import random
            random.seed(37)
            vgv__crp = random.sample(ktywx__hqrmj.pieces, k=len(
                ktywx__hqrmj.pieces))
        else:
            vgv__crp = ktywx__hqrmj.pieces
        for ookpr__euk in vgv__crp:
            ookpr__euk._bodo_num_rows = 0
        fpaths = [ookpr__euk.path for ookpr__euk in vgv__crp[start:jbw__zal]]
        if protocol == 's3':
            jhyls__ydk = isiji__redi.netloc
            prefix = 's3://' + jhyls__ydk + '/'
            fpaths = [jeo__qpmbh[len(prefix):] for jeo__qpmbh in fpaths]
            som__layf = get_s3_subtree_fs(jhyls__ydk, region=getfs().region,
                storage_options=storage_options)
        else:
            som__layf = getfs()
        pa.set_io_thread_count(4)
        pa.set_cpu_count(4)
        bbftk__moyh = ds.dataset(fpaths, filesystem=som__layf, partitioning
            =ds.partitioning(flavor='hive'))
        for jgbfo__qxjw, wceg__cgc in zip(vgv__crp[start:jbw__zal],
            bbftk__moyh.get_fragments()):
            ctsk__qni = time.time()
            iip__osikk = wceg__cgc.scanner(schema=bbftk__moyh.schema,
                filter=expr_filters, use_threads=True).count_rows()
            enhh__hzf += time.time() - ctsk__qni
            jgbfo__qxjw._bodo_num_rows = iip__osikk
            plvbv__unbu += iip__osikk
            chrj__mwmpo += wceg__cgc.num_row_groups
            doy__uwbll += sum(meqd__kkcck.total_byte_size for meqd__kkcck in
                wceg__cgc.row_groups)
            if cfu__gpfn:
                bef__ivio = wceg__cgc.metadata.schema.to_arrow_schema()
                if cuacn__wjhtu != bef__ivio:
                    print('Schema in {!s} was different. \n{!s}\n\nvs\n\n{!s}'
                        .format(jgbfo__qxjw, bef__ivio, cuacn__wjhtu))
                    ycbl__jchoy = False
                    break
        if cfu__gpfn:
            ycbl__jchoy = gpwfd__uyxkv.allreduce(ycbl__jchoy, op=MPI.LAND)
            if not ycbl__jchoy:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            ktywx__hqrmj._bodo_total_rows = gpwfd__uyxkv.allreduce(plvbv__unbu,
                op=MPI.SUM)
            lni__mcfb = gpwfd__uyxkv.allreduce(chrj__mwmpo, op=MPI.SUM)
            wmzq__pjwcv = gpwfd__uyxkv.allreduce(doy__uwbll, op=MPI.SUM)
            tdpur__tfzi = np.array([ookpr__euk._bodo_num_rows for
                ookpr__euk in ktywx__hqrmj.pieces])
            tdpur__tfzi = gpwfd__uyxkv.allreduce(tdpur__tfzi, op=MPI.SUM)
            for ookpr__euk, dibbb__azef in zip(ktywx__hqrmj.pieces, tdpur__tfzi
                ):
                ookpr__euk._bodo_num_rows = dibbb__azef
            if is_parallel and bodo.get_rank(
                ) == 0 and lni__mcfb < bodo.get_size() and lni__mcfb != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({lni__mcfb}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()})
"""
                    ))
            if lni__mcfb == 0:
                uqgy__cyd = 0
            else:
                uqgy__cyd = wmzq__pjwcv // lni__mcfb
            if (bodo.get_rank() == 0 and wmzq__pjwcv >= 20 * 1048576 and 
                uqgy__cyd < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({uqgy__cyd} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                yzrwf__gbvvh.add_attribute('g_total_num_row_groups', lni__mcfb)
                if expr_filters is not None:
                    yzrwf__gbvvh.add_attribute('total_scan_time', enhh__hzf)
                qke__eguxa = np.array([ookpr__euk._bodo_num_rows for
                    ookpr__euk in ktywx__hqrmj.pieces])
                opv__ufmg = np.percentile(qke__eguxa, [25, 50, 75])
                yzrwf__gbvvh.add_attribute('g_row_counts_min', qke__eguxa.min()
                    )
                yzrwf__gbvvh.add_attribute('g_row_counts_Q1', opv__ufmg[0])
                yzrwf__gbvvh.add_attribute('g_row_counts_median', opv__ufmg[1])
                yzrwf__gbvvh.add_attribute('g_row_counts_Q3', opv__ufmg[2])
                yzrwf__gbvvh.add_attribute('g_row_counts_max', qke__eguxa.max()
                    )
                yzrwf__gbvvh.add_attribute('g_row_counts_mean', qke__eguxa.
                    mean())
                yzrwf__gbvvh.add_attribute('g_row_counts_std', qke__eguxa.std()
                    )
                yzrwf__gbvvh.add_attribute('g_row_counts_sum', qke__eguxa.sum()
                    )
                yzrwf__gbvvh.finalize()
    ktywx__hqrmj._prefix = ''
    if protocol in {'hdfs', 'abfs', 'abfss'}:
        prefix = f'{protocol}://{isiji__redi.netloc}'
        if len(ktywx__hqrmj.pieces) > 0:
            jgbfo__qxjw = ktywx__hqrmj.pieces[0]
            if not jgbfo__qxjw.path.startswith(prefix):
                ktywx__hqrmj._prefix = prefix
    if read_categories:
        _add_categories_to_pq_dataset(ktywx__hqrmj)
    if get_row_counts:
        jvgwn__aqqod.finalize()
    return ktywx__hqrmj


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, storage_options, region, prefix):
    import pyarrow as pa
    eycz__ssj = os.cpu_count()
    if eycz__ssj is None or eycz__ssj == 0:
        eycz__ssj = 2
    moy__iyse = min(4, eycz__ssj)
    dbgl__wwmn = min(16, eycz__ssj)
    if is_parallel and len(fpaths) > dbgl__wwmn and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(dbgl__wwmn)
        pa.set_cpu_count(dbgl__wwmn)
    else:
        pa.set_io_thread_count(moy__iyse)
        pa.set_cpu_count(moy__iyse)
    if fpaths[0].startswith('s3://'):
        jhyls__ydk = urlparse(fpaths[0]).netloc
        prefix = 's3://' + jhyls__ydk + '/'
        fpaths = [jeo__qpmbh[len(prefix):] for jeo__qpmbh in fpaths]
        som__layf = get_s3_subtree_fs(jhyls__ydk, region=region,
            storage_options=storage_options)
    elif prefix and prefix.startswith(('hdfs', 'abfs', 'abfss')):
        som__layf = get_hdfs_fs(prefix + fpaths[0])
    elif fpaths[0].startswith(('gcs', 'gs')):
        import gcsfs
        som__layf = gcsfs.GCSFileSystem(token=None)
    else:
        som__layf = None
    ktywx__hqrmj = ds.dataset(fpaths, filesystem=som__layf, partitioning=ds
        .partitioning(flavor='hive'))
    col_names = ktywx__hqrmj.schema.names
    ojveo__txfp = [col_names[fvt__ebqda] for fvt__ebqda in selected_fields]
    twr__ixvvv = ktywx__hqrmj.scanner(columns=ojveo__txfp, filter=
        expr_filters, use_threads=True).to_reader()
    return ktywx__hqrmj, twr__ixvvv


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    rkg__ixt = pq_dataset.schema.to_arrow_schema()
    puffj__wzug = [c for c in rkg__ixt.names if isinstance(rkg__ixt.field(c
        ).type, pa.DictionaryType)]
    if len(puffj__wzug) == 0:
        pq_dataset._category_info = {}
        return
    gpwfd__uyxkv = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            cqzr__hypx = pq_dataset.pieces[0].open()
            meqd__kkcck = cqzr__hypx.read_row_group(0, puffj__wzug)
            category_info = {c: tuple(meqd__kkcck.column(c).chunk(0).
                dictionary.to_pylist()) for c in puffj__wzug}
            del cqzr__hypx, meqd__kkcck
        except Exception as ybv__ram:
            gpwfd__uyxkv.bcast(ybv__ram)
            raise ybv__ram
        gpwfd__uyxkv.bcast(category_info)
    else:
        category_info = gpwfd__uyxkv.bcast(None)
        if isinstance(category_info, Exception):
            bcchh__rrc = category_info
            raise bcchh__rrc
    pq_dataset._category_info = category_info


def get_pandas_metadata(schema, num_pieces):
    zfs__dtm = None
    nullable_from_metadata = defaultdict(lambda : None)
    nzj__pkcx = b'pandas'
    if schema.metadata is not None and nzj__pkcx in schema.metadata:
        import json
        kewod__uwb = json.loads(schema.metadata[nzj__pkcx].decode('utf8'))
        wcmn__gfg = len(kewod__uwb['index_columns'])
        if wcmn__gfg > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        zfs__dtm = kewod__uwb['index_columns'][0] if wcmn__gfg else None
        if not isinstance(zfs__dtm, str) and (not isinstance(zfs__dtm, dict
            ) or num_pieces != 1):
            zfs__dtm = None
        for wpoh__lrfo in kewod__uwb['columns']:
            vtq__jpm = wpoh__lrfo['name']
            if wpoh__lrfo['pandas_type'].startswith('int'
                ) and vtq__jpm is not None:
                if wpoh__lrfo['numpy_type'].startswith('Int'):
                    nullable_from_metadata[vtq__jpm] = True
                else:
                    nullable_from_metadata[vtq__jpm] = False
    return zfs__dtm, nullable_from_metadata


def parquet_file_schema(file_name, selected_columns, storage_options=None):
    col_names = []
    iyx__goih = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = [] if pq_dataset.partitions is None else [pq_dataset.
        partitions.levels[zidwa__dpnw].name for zidwa__dpnw in range(len(
        pq_dataset.partitions.partition_names))]
    rkg__ixt = pq_dataset.schema.to_arrow_schema()
    num_pieces = len(pq_dataset.pieces)
    col_names = rkg__ixt.names
    zfs__dtm, nullable_from_metadata = get_pandas_metadata(rkg__ixt, num_pieces
        )
    rqtn__uoo = [_get_numba_typ_from_pa_typ(rkg__ixt.field(c), c ==
        zfs__dtm, nullable_from_metadata[c], pq_dataset._category_info) for
        c in col_names]
    if partition_names:
        col_names += partition_names
        rqtn__uoo += [_get_partition_cat_dtype(pq_dataset.partitions.levels
            [zidwa__dpnw]) for zidwa__dpnw in range(len(partition_names))]
    jzqb__vnm = {c: zidwa__dpnw for zidwa__dpnw, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in jzqb__vnm:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if zfs__dtm and not isinstance(zfs__dtm, dict
        ) and zfs__dtm not in selected_columns:
        selected_columns.append(zfs__dtm)
    col_indices = [jzqb__vnm[c] for c in selected_columns]
    iyx__goih = [rqtn__uoo[jzqb__vnm[c]] for c in selected_columns]
    col_names = selected_columns
    return col_names, iyx__goih, zfs__dtm, col_indices, partition_names


def _get_partition_cat_dtype(part_set):
    vbaam__qat = part_set.dictionary.to_pandas()
    npobx__tdry = bodo.typeof(vbaam__qat).dtype
    jhuj__brboh = PDCategoricalDtype(tuple(vbaam__qat), npobx__tdry, False)
    return CategoricalArrayType(jhuj__brboh)


_pq_read = types.ExternalFunction('pq_read', table_type(
    read_parquet_fpath_type, types.boolean, types.voidptr,
    parquet_predicate_type, parquet_predicate_type,
    storage_options_dict_type, types.int64, types.voidptr, types.int32,
    types.voidptr, types.voidptr, types.voidptr, types.int32, types.voidptr))
from llvmlite import ir as lir
from numba.core import cgutils
if bodo.utils.utils.has_pyarrow():
    from bodo.io import arrow_cpp
    ll.add_symbol('pq_read', arrow_cpp.pq_read)
    ll.add_symbol('pq_write', arrow_cpp.pq_write)
    ll.add_symbol('pq_write_partitioned', arrow_cpp.pq_write_partitioned)


@intrinsic
def parquet_write_table_cpp(typingctx, filename_t, table_t, col_names_t,
    index_t, write_index, metadata_t, compression_t, is_parallel_t,
    write_range_index, start, stop, step, name, bucket_region):

    def codegen(context, builder, sig, args):
        iyrao__xepd = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer()])
        zkna__rter = cgutils.get_or_insert_function(builder.module,
            iyrao__xepd, name='pq_write')
        builder.call(zkna__rter, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, table_t, col_names_t, index_t, types.
        boolean, types.voidptr, types.voidptr, types.boolean, types.boolean,
        types.int32, types.int32, types.int32, types.voidptr, types.voidptr
        ), codegen


@intrinsic
def parquet_write_table_partitioned_cpp(typingctx, filename_t, data_table_t,
    col_names_t, col_names_no_partitions_t, cat_table_t, part_col_idxs_t,
    num_part_col_t, compression_t, is_parallel_t, bucket_region):

    def codegen(context, builder, sig, args):
        iyrao__xepd = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer()])
        zkna__rter = cgutils.get_or_insert_function(builder.module,
            iyrao__xepd, name='pq_write_partitioned')
        builder.call(zkna__rter, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr), codegen
