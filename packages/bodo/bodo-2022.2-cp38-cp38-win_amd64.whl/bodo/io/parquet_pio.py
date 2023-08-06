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
        except OSError as sdo__nkp:
            if 'non-file path' in str(sdo__nkp):
                raise FileNotFoundError(str(sdo__nkp))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=None):
        qqly__tzta = lhs.scope
        zvppo__zkkx = lhs.loc
        kbi__qssq = None
        if lhs.name in self.locals:
            kbi__qssq = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        nmqe__lvg = {}
        if lhs.name + ':convert' in self.locals:
            nmqe__lvg = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if kbi__qssq is None:
            fbur__kqag = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/source/programming_with_bodo/file_io.html#non-constant-filepaths'
                )
            ads__tnwil = get_const_value(file_name, self.func_ir,
                fbur__kqag, arg_types=self.args, file_info=ParquetFileInfo(
                columns, storage_options=storage_options))
            yiiye__aqbf = False
            tbfdo__mvx = guard(get_definition, self.func_ir, file_name)
            if isinstance(tbfdo__mvx, ir.Arg):
                typ = self.args[tbfdo__mvx.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, cjcka__kkxjf, xxr__wty, col_indices,
                        partition_names) = typ.schema
                    yiiye__aqbf = True
            if not yiiye__aqbf:
                (col_names, cjcka__kkxjf, xxr__wty, col_indices,
                    partition_names) = (parquet_file_schema(ads__tnwil,
                    columns, storage_options=storage_options))
        else:
            zzlhi__kra = list(kbi__qssq.keys())
            hrpvn__iyi = {c: agika__gfpno for agika__gfpno, c in enumerate(
                zzlhi__kra)}
            nqmzt__wfybv = [uazk__enlmy for uazk__enlmy in kbi__qssq.values()]
            xxr__wty = 'index' if 'index' in hrpvn__iyi else None
            if columns is None:
                selected_columns = zzlhi__kra
            else:
                selected_columns = columns
            col_indices = [hrpvn__iyi[c] for c in selected_columns]
            cjcka__kkxjf = [nqmzt__wfybv[hrpvn__iyi[c]] for c in
                selected_columns]
            col_names = selected_columns
            xxr__wty = xxr__wty if xxr__wty in col_names else None
            partition_names = []
        uods__txps = None if isinstance(xxr__wty, dict
            ) or xxr__wty is None else xxr__wty
        index_column_index = None
        index_column_type = types.none
        if uods__txps:
            zci__iify = col_names.index(uods__txps)
            col_indices = col_indices.copy()
            cjcka__kkxjf = cjcka__kkxjf.copy()
            index_column_index = col_indices.pop(zci__iify)
            index_column_type = cjcka__kkxjf.pop(zci__iify)
        for agika__gfpno, c in enumerate(col_names):
            if c in nmqe__lvg:
                cjcka__kkxjf[agika__gfpno] = nmqe__lvg[c]
        mjrs__pwwx = [ir.Var(qqly__tzta, mk_unique_var('pq_table'),
            zvppo__zkkx), ir.Var(qqly__tzta, mk_unique_var('pq_index'),
            zvppo__zkkx)]
        zwmd__vbxo = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.name,
            col_names, col_indices, cjcka__kkxjf, mjrs__pwwx, zvppo__zkkx,
            partition_names, storage_options, index_column_index,
            index_column_type)]
        return (col_names, mjrs__pwwx, xxr__wty, zwmd__vbxo, cjcka__kkxjf,
            index_column_type)


def determine_filter_cast(pq_node, typemap, filter_val, orig_colname_map):
    voiml__tmspb = filter_val[0]
    oqpcr__gxqlm = pq_node.original_out_types[orig_colname_map[voiml__tmspb]]
    ycxw__mlbx = bodo.utils.typing.element_type(oqpcr__gxqlm)
    if voiml__tmspb in pq_node.partition_names:
        if ycxw__mlbx == types.unicode_type:
            ghqfn__usn = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(ycxw__mlbx, types.Integer):
            ghqfn__usn = f'.cast(pyarrow.{ycxw__mlbx.name}(), safe=False)'
        else:
            ghqfn__usn = ''
    else:
        ghqfn__usn = ''
    ybmsp__clmz = typemap[filter_val[2].name]
    if not bodo.utils.typing.is_common_scalar_dtype([ycxw__mlbx, ybmsp__clmz]):
        if not bodo.utils.typing.is_safe_arrow_cast(ycxw__mlbx, ybmsp__clmz):
            raise BodoError(
                f'Unsupport Arrow cast from {ycxw__mlbx} to {ybmsp__clmz} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if ycxw__mlbx == types.unicode_type:
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif ycxw__mlbx in (bodo.datetime64ns, bodo.pd_timestamp_type):
            return ghqfn__usn, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return ghqfn__usn, ''


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    jyy__xzi = len(pq_node.out_vars)
    extra_args = ''
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    lngt__cyu, yacwp__yjp = bodo.ir.connector.generate_filter_map(pq_node.
        filters)
    if pq_node.filters:
        lsbc__ktk = []
        djmx__wabo = []
        wfpan__ndc = False
        iijp__xnshz = None
        orig_colname_map = {c: agika__gfpno for agika__gfpno, c in
            enumerate(pq_node.original_df_colnames)}
        for fin__axreu in pq_node.filters:
            fplbo__sqq = []
            xfq__rgmyl = []
            kjaa__gljks = set()
            for pch__aah in fin__axreu:
                if isinstance(pch__aah[2], ir.Var):
                    dpfjy__esxl, voaqa__hbafy = determine_filter_cast(pq_node,
                        typemap, pch__aah, orig_colname_map)
                    xfq__rgmyl.append(
                        f"(ds.field('{pch__aah[0]}'){dpfjy__esxl} {pch__aah[1]} ds.scalar({lngt__cyu[pch__aah[2].name]}){voaqa__hbafy})"
                        )
                else:
                    assert pch__aah[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if pch__aah[1] == 'is not':
                        prefix = '~'
                    else:
                        prefix = ''
                    xfq__rgmyl.append(
                        f"({prefix}ds.field('{pch__aah[0]}').is_null())")
                if pch__aah[0] in pq_node.partition_names and isinstance(
                    pch__aah[2], ir.Var):
                    pztz__mbjzs = (
                        f"('{pch__aah[0]}', '{pch__aah[1]}', {lngt__cyu[pch__aah[2].name]})"
                        )
                    fplbo__sqq.append(pztz__mbjzs)
                    kjaa__gljks.add(pztz__mbjzs)
                else:
                    wfpan__ndc = True
            if iijp__xnshz is None:
                iijp__xnshz = kjaa__gljks
            else:
                iijp__xnshz.intersection_update(kjaa__gljks)
            snc__uax = ', '.join(fplbo__sqq)
            ergxn__nfqdj = ' & '.join(xfq__rgmyl)
            if snc__uax:
                lsbc__ktk.append(f'[{snc__uax}]')
            djmx__wabo.append(f'({ergxn__nfqdj})')
        iutw__fyoe = ', '.join(lsbc__ktk)
        qejut__eqdq = ' | '.join(djmx__wabo)
        if wfpan__ndc:
            if iijp__xnshz:
                ego__jpib = sorted(iijp__xnshz)
                dnf_filter_str = f"[[{', '.join(ego__jpib)}]]"
        elif iutw__fyoe:
            dnf_filter_str = f'[{iutw__fyoe}]'
        expr_filter_str = f'({qejut__eqdq})'
        extra_args = ', '.join(lngt__cyu.values())
    akdi__pfjyh = ', '.join(f'out{agika__gfpno}' for agika__gfpno in range(
        jyy__xzi))
    gqb__bhm = f'def pq_impl(fname, {extra_args}):\n'
    gqb__bhm += (
        f'    (total_rows, {akdi__pfjyh},) = _pq_reader_py(fname, {extra_args})\n'
        )
    xydt__iyq = {}
    exec(gqb__bhm, {}, xydt__iyq)
    ukr__xkqo = xydt__iyq['pq_impl']
    parallel = False
    if array_dists is not None:
        yhceq__gxp = pq_node.out_vars[0].name
        parallel = array_dists[yhceq__gxp] in (distributed_pass.
            Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        ftjq__dear = pq_node.out_vars[1].name
        assert typemap[ftjq__dear
            ] == types.none or not parallel or array_dists[ftjq__dear] in (
            distributed_pass.Distribution.OneD, distributed_pass.
            Distribution.OneD_Var
            ), 'pq data/index parallelization does not match'
    qeq__eeu = _gen_pq_reader_py(pq_node.df_colnames, pq_node.col_indices,
        pq_node.type_usecol_offset, pq_node.out_types, pq_node.
        storage_options, pq_node.partition_names, dnf_filter_str,
        expr_filter_str, extra_args, parallel, meta_head_only_info, pq_node
        .index_column_index, pq_node.index_column_type)
    gqmod__hbf = typemap[pq_node.file_name.name]
    wfpe__wwfd = (gqmod__hbf,) + tuple(typemap[pch__aah.name] for pch__aah in
        yacwp__yjp)
    graz__nlob = compile_to_numba_ir(ukr__xkqo, {'_pq_reader_py': qeq__eeu},
        typingctx=typingctx, targetctx=targetctx, arg_typs=wfpe__wwfd,
        typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(graz__nlob, [pq_node.file_name] + yacwp__yjp)
    zwmd__vbxo = graz__nlob.body[:-3]
    if meta_head_only_info:
        zwmd__vbxo[-1 - jyy__xzi].target = meta_head_only_info[1]
    zwmd__vbxo[-2].target = pq_node.out_vars[0]
    zwmd__vbxo[-1].target = pq_node.out_vars[1]
    return zwmd__vbxo


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    ajcvg__huzl = get_overload_const_str(dnf_filter_str)
    nml__jpkel = get_overload_const_str(expr_filter_str)
    flng__qst = ', '.join(f'f{agika__gfpno}' for agika__gfpno in range(len(
        var_tup)))
    gqb__bhm = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        gqb__bhm += f'  {flng__qst}, = var_tup\n'
    gqb__bhm += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    gqb__bhm += f'    dnf_filters_py = {ajcvg__huzl}\n'
    gqb__bhm += f'    expr_filters_py = {nml__jpkel}\n'
    gqb__bhm += '  return (dnf_filters_py, expr_filters_py)\n'
    xydt__iyq = {}
    exec(gqb__bhm, globals(), xydt__iyq)
    return xydt__iyq['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def get_storage_options_pyobject(storage_options):
    pass


@overload(get_storage_options_pyobject, no_unliteral=True)
def overload_get_storage_options_pyobject(storage_options):
    xswo__frcrr = get_overload_constant_dict(storage_options)
    gqb__bhm = 'def impl(storage_options):\n'
    gqb__bhm += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    gqb__bhm += f'    storage_options_py = {str(xswo__frcrr)}\n'
    gqb__bhm += '  return storage_options_py\n'
    xydt__iyq = {}
    exec(gqb__bhm, globals(), xydt__iyq)
    return xydt__iyq['impl']


def _gen_pq_reader_py(col_names, col_indices, type_usecol_offset, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type):
    ovq__zqfjj = next_label()
    azmtu__gqkeq = ',' if extra_args else ''
    gqb__bhm = f'def pq_reader_py(fname,{extra_args}):\n'
    gqb__bhm += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    gqb__bhm += "    ev.add_attribute('fname', fname)\n"
    gqb__bhm += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={is_parallel})
"""
    gqb__bhm += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{azmtu__gqkeq}))
"""
    gqb__bhm += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    gqb__bhm += (
        f'    storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    jbi__pet = not type_usecol_offset
    niw__eedrp = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    bxm__ngd = {c: agika__gfpno for agika__gfpno, c in enumerate(col_indices)}
    qloa__ipcz = {c: agika__gfpno for agika__gfpno, c in enumerate(niw__eedrp)}
    dhzyb__msva = []
    mqdsn__glyr = set()
    for agika__gfpno in type_usecol_offset:
        if niw__eedrp[agika__gfpno] not in partition_names:
            dhzyb__msva.append(col_indices[agika__gfpno])
        else:
            mqdsn__glyr.add(col_indices[agika__gfpno])
    if index_column_index is not None:
        dhzyb__msva.append(index_column_index)
    dhzyb__msva = sorted(dhzyb__msva)
    ybx__lyr = {c: agika__gfpno for agika__gfpno, c in enumerate(dhzyb__msva)}

    def is_nullable(typ):
        return bodo.utils.utils.is_array_typ(typ, False) and not isinstance(typ
            , types.Array)
    ocqjr__glka = [(int(is_nullable(out_types[bxm__ngd[pjxh__jbazg]])) if 
        pjxh__jbazg != index_column_index else int(is_nullable(
        index_column_type))) for pjxh__jbazg in dhzyb__msva]
    uuxy__jaw = []
    sqm__utnr = {}
    xzjdq__hqbni = []
    uizj__wub = []
    for agika__gfpno, rrco__ygiwe in enumerate(partition_names):
        try:
            iqyof__iudgk = qloa__ipcz[rrco__ygiwe]
            if col_indices[iqyof__iudgk] not in mqdsn__glyr:
                continue
        except (KeyError, ValueError) as zxzh__zyovn:
            continue
        sqm__utnr[rrco__ygiwe] = len(uuxy__jaw)
        uuxy__jaw.append(rrco__ygiwe)
        xzjdq__hqbni.append(agika__gfpno)
        bscpq__bvy = out_types[iqyof__iudgk].dtype
        tpnu__ohifh = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            bscpq__bvy)
        uizj__wub.append(numba_to_c_type(tpnu__ohifh))
    gqb__bhm += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    if len(xzjdq__hqbni) > 0:
        gqb__bhm += f"""    out_table = pq_read(fname_py, {is_parallel}, unicode_to_utf8(bucket_region), dnf_filters, expr_filters, storage_options_py, {tot_rows_to_read}, selected_cols_arr_{ovq__zqfjj}.ctypes, {len(dhzyb__msva)}, nullable_cols_arr_{ovq__zqfjj}.ctypes, np.array({xzjdq__hqbni}, dtype=np.int32).ctypes, np.array({uizj__wub}, dtype=np.int32).ctypes, {len(xzjdq__hqbni)}, total_rows_np.ctypes)
"""
    else:
        gqb__bhm += f"""    out_table = pq_read(fname_py, {is_parallel}, unicode_to_utf8(bucket_region), dnf_filters, expr_filters, storage_options_py, {tot_rows_to_read}, selected_cols_arr_{ovq__zqfjj}.ctypes, {len(dhzyb__msva)}, nullable_cols_arr_{ovq__zqfjj}.ctypes, 0, 0, 0, total_rows_np.ctypes)
"""
    gqb__bhm += '    check_and_propagate_cpp_exception()\n'
    apmzf__bsm = 'None'
    emqq__rggb = index_column_type
    bqrs__kft = TableType(tuple(out_types))
    if jbi__pet:
        bqrs__kft = types.none
    if index_column_index is not None:
        oqmhu__swi = ybx__lyr[index_column_index]
        apmzf__bsm = (
            f'info_to_array(info_from_table(out_table, {oqmhu__swi}), index_arr_type)'
            )
    gqb__bhm += f'    index_arr = {apmzf__bsm}\n'
    if jbi__pet:
        eusfh__suvq = None
    else:
        eusfh__suvq = []
        cek__icnr = 0
        for agika__gfpno, ryvq__jdgq in enumerate(col_indices):
            if cek__icnr < len(type_usecol_offset
                ) and agika__gfpno == type_usecol_offset[cek__icnr]:
                giukx__uski = col_indices[agika__gfpno]
                if giukx__uski in mqdsn__glyr:
                    hbqq__owu = niw__eedrp[agika__gfpno]
                    eusfh__suvq.append(len(dhzyb__msva) + sqm__utnr[hbqq__owu])
                else:
                    eusfh__suvq.append(ybx__lyr[ryvq__jdgq])
                cek__icnr += 1
            else:
                eusfh__suvq.append(-1)
        eusfh__suvq = np.array(eusfh__suvq, dtype=np.int64)
    if jbi__pet:
        gqb__bhm += '    T = None\n'
    else:
        gqb__bhm += f"""    T = cpp_table_to_py_table(out_table, table_idx_{ovq__zqfjj}, py_table_type_{ovq__zqfjj})
"""
    gqb__bhm += '    delete_table(out_table)\n'
    gqb__bhm += f'    total_rows = total_rows_np[0]\n'
    gqb__bhm += f'    ev.finalize()\n'
    gqb__bhm += '    return (total_rows, T, index_arr)\n'
    xydt__iyq = {}
    xcfyj__teqph = {f'py_table_type_{ovq__zqfjj}': bqrs__kft,
        f'table_idx_{ovq__zqfjj}': eusfh__suvq,
        f'selected_cols_arr_{ovq__zqfjj}': np.array(dhzyb__msva, np.int32),
        f'nullable_cols_arr_{ovq__zqfjj}': np.array(ocqjr__glka, np.int32),
        'index_arr_type': emqq__rggb, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo}
    exec(gqb__bhm, xcfyj__teqph, xydt__iyq)
    qeq__eeu = xydt__iyq['pq_reader_py']
    rzlub__pioc = numba.njit(qeq__eeu, no_cpython_wrapper=True)
    return rzlub__pioc


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
        nzq__gcc = []
        fofoe__hpsr = []
        for nfwht__qjday in pa_typ.flatten():
            fofoe__hpsr.append(nfwht__qjday.name.split('.')[-1])
            nzq__gcc.append(_get_numba_typ_from_pa_typ(nfwht__qjday,
                is_index, nullable_from_metadata, category_info))
        return StructArrayType(tuple(nzq__gcc), tuple(fofoe__hpsr))
    if isinstance(pa_typ.type, pa.Decimal128Type):
        return DecimalArrayType(pa_typ.type.precision, pa_typ.type.scale)
    if isinstance(pa_typ.type, pa.DictionaryType):
        if pa_typ.type.value_type != pa.string():
            raise BodoError(
                f'Parquet Categorical data type should be string, not {pa_typ.type.value_type}'
                )
        lcs__xpijk = _pa_numba_typ_map[pa_typ.type.index_type]
        gmer__gzhlf = PDCategoricalDtype(category_info[pa_typ.name], bodo.
            string_type, pa_typ.type.ordered, int_type=lcs__xpijk)
        return CategoricalArrayType(gmer__gzhlf)
    if pa_typ.type not in _pa_numba_typ_map:
        raise BodoError('Arrow data type {} not supported yet'.format(
            pa_typ.type))
    gpcx__vhy = _pa_numba_typ_map[pa_typ.type]
    if gpcx__vhy == datetime_date_type:
        return datetime_date_array_type
    if gpcx__vhy == bytes_type:
        return binary_array_type
    bfqk__ttqeb = (string_array_type if gpcx__vhy == string_type else types
        .Array(gpcx__vhy, 1, 'C'))
    if gpcx__vhy == types.bool_:
        bfqk__ttqeb = boolean_array
    if nullable_from_metadata is not None:
        xpfaq__uvo = nullable_from_metadata
    else:
        xpfaq__uvo = use_nullable_int_arr
    if xpfaq__uvo and not is_index and isinstance(gpcx__vhy, types.Integer
        ) and pa_typ.nullable:
        bfqk__ttqeb = IntegerArrayType(gpcx__vhy)
    return bfqk__ttqeb


def get_parquet_dataset(fpath, get_row_counts=True, dnf_filters=None,
    expr_filters=None, storage_options=None, read_categories=False,
    is_parallel=False, tot_rows_to_read=None):
    if get_row_counts:
        ckkif__hqzyi = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    pxji__waf = MPI.COMM_WORLD
    if isinstance(fpath, list):
        iktm__wvgsu = urlparse(fpath[0])
        protocol = iktm__wvgsu.scheme
        kzcuo__upu = iktm__wvgsu.netloc
        for agika__gfpno in range(len(fpath)):
            uke__qjhd = fpath[agika__gfpno]
            pnxr__gkra = urlparse(uke__qjhd)
            if pnxr__gkra.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if pnxr__gkra.netloc != kzcuo__upu:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[agika__gfpno] = uke__qjhd.rstrip('/')
    else:
        iktm__wvgsu = urlparse(fpath)
        protocol = iktm__wvgsu.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as zxzh__zyovn:
            otedk__vusm = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(otedk__vusm)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as zxzh__zyovn:
            otedk__vusm = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
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
            ranrd__qzeb = gcsfs.GCSFileSystem(token=None)
            fs.append(ranrd__qzeb)
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
                prefix = f'{protocol}://{iktm__wvgsu.netloc}'
                path = path[len(prefix):]
            zwl__gsn = fs.glob(path)
            if protocol == 's3':
                zwl__gsn = [('s3://' + uke__qjhd) for uke__qjhd in zwl__gsn if
                    not uke__qjhd.startswith('s3://')]
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                zwl__gsn = [(prefix + uke__qjhd) for uke__qjhd in zwl__gsn]
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(zwl__gsn) == 0:
            raise BodoError('No files found matching glob pattern')
        return zwl__gsn
    xnx__pntwd = False
    if get_row_counts:
        hnlmx__mnuy = getfs(parallel=True)
        xnx__pntwd = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        lpou__bjd = 1
        ztc__qpu = os.cpu_count()
        if ztc__qpu is not None and ztc__qpu > 1:
            lpou__bjd = ztc__qpu // 2
        try:
            if get_row_counts:
                qkfo__hon = tracing.Event('pq.ParquetDataset', is_parallel=
                    False)
                if tracing.is_tracing():
                    qkfo__hon.add_attribute('dnf_filter', str(dnf_filters))
            tnhw__ihxr = pa.io_thread_count()
            pa.set_io_thread_count(lpou__bjd)
            if '*' in fpath:
                fpath = glob(protocol, getfs(), fpath)
            if protocol == 's3':
                if isinstance(fpath, list):
                    get_legacy_fs().info(fpath[0])
                else:
                    get_legacy_fs().info(fpath)
            if protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{iktm__wvgsu.netloc}'
                if isinstance(fpath, list):
                    jxx__trlq = [uke__qjhd[len(prefix):] for uke__qjhd in fpath
                        ]
                else:
                    jxx__trlq = fpath[len(prefix):]
            else:
                jxx__trlq = fpath
            amm__nwrpr = pq.ParquetDataset(jxx__trlq, filesystem=
                get_legacy_fs(), filters=None, use_legacy_dataset=True,
                validate_schema=False, metadata_nthreads=lpou__bjd)
            pa.set_io_thread_count(tnhw__ihxr)
            nkzm__tzz = bodo.io.pa_parquet.get_dataset_schema(amm__nwrpr)
            if dnf_filters:
                if get_row_counts:
                    qkfo__hon.add_attribute('num_pieces_before_filter', len
                        (amm__nwrpr.pieces))
                kwyoy__ato = time.time()
                amm__nwrpr._filter(dnf_filters)
                if get_row_counts:
                    qkfo__hon.add_attribute('dnf_filter_time', time.time() -
                        kwyoy__ato)
                    qkfo__hon.add_attribute('num_pieces_after_filter', len(
                        amm__nwrpr.pieces))
            if get_row_counts:
                qkfo__hon.finalize()
            amm__nwrpr._metadata.fs = None
        except Exception as sdo__nkp:
            pxji__waf.bcast(sdo__nkp)
            raise BodoError(
                f'error from pyarrow: {type(sdo__nkp).__name__}: {str(sdo__nkp)}\n'
                )
        if get_row_counts:
            ych__oxzp = tracing.Event('bcast dataset')
        pxji__waf.bcast(amm__nwrpr)
        pxji__waf.bcast(nkzm__tzz)
    else:
        if get_row_counts:
            ych__oxzp = tracing.Event('bcast dataset')
        amm__nwrpr = pxji__waf.bcast(None)
        if isinstance(amm__nwrpr, Exception):
            qnfiu__btzq = amm__nwrpr
            raise BodoError(
                f"""error from pyarrow: {type(qnfiu__btzq).__name__}: {str(qnfiu__btzq)}
"""
                )
        nkzm__tzz = pxji__waf.bcast(None)
    if get_row_counts:
        ych__oxzp.finalize()
    amm__nwrpr._bodo_total_rows = 0
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = xnx__pntwd = False
        for yiiw__ffu in amm__nwrpr.pieces:
            yiiw__ffu._bodo_num_rows = 0
    if get_row_counts or xnx__pntwd:
        if get_row_counts and tracing.is_tracing():
            rvzr__arwb = tracing.Event('get_row_counts')
            rvzr__arwb.add_attribute('g_num_pieces', len(amm__nwrpr.pieces))
            rvzr__arwb.add_attribute('g_expr_filters', str(expr_filters))
        sqlv__slq = 0.0
        num_pieces = len(amm__nwrpr.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        wclv__kaupp = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        iogl__rczz = 0
        reako__kao = 0
        lti__potyf = 0
        jfw__wwmq = True
        amm__nwrpr._metadata.fs = getfs()
        if expr_filters is not None:
            import random
            random.seed(37)
            cdsb__qlh = random.sample(amm__nwrpr.pieces, k=len(amm__nwrpr.
                pieces))
        else:
            cdsb__qlh = amm__nwrpr.pieces
        for yiiw__ffu in cdsb__qlh:
            yiiw__ffu._bodo_num_rows = 0
        fpaths = [yiiw__ffu.path for yiiw__ffu in cdsb__qlh[start:wclv__kaupp]]
        if protocol == 's3':
            kzcuo__upu = iktm__wvgsu.netloc
            prefix = 's3://' + kzcuo__upu + '/'
            fpaths = [uke__qjhd[len(prefix):] for uke__qjhd in fpaths]
            iuy__bxtk = get_s3_subtree_fs(kzcuo__upu, region=getfs().region,
                storage_options=storage_options)
        else:
            iuy__bxtk = getfs()
        pa.set_io_thread_count(4)
        pa.set_cpu_count(4)
        vdehq__hod = ds.dataset(fpaths, filesystem=iuy__bxtk, partitioning=
            ds.partitioning(flavor='hive'))
        for phxgk__nsjbx, wdjyg__txlg in zip(cdsb__qlh[start:wclv__kaupp],
            vdehq__hod.get_fragments()):
            kwyoy__ato = time.time()
            pff__gnpel = wdjyg__txlg.scanner(schema=vdehq__hod.schema,
                filter=expr_filters, use_threads=True).count_rows()
            sqlv__slq += time.time() - kwyoy__ato
            phxgk__nsjbx._bodo_num_rows = pff__gnpel
            iogl__rczz += pff__gnpel
            reako__kao += wdjyg__txlg.num_row_groups
            lti__potyf += sum(jyji__fymfq.total_byte_size for jyji__fymfq in
                wdjyg__txlg.row_groups)
            if xnx__pntwd:
                yuxtb__hnlc = wdjyg__txlg.metadata.schema.to_arrow_schema()
                if nkzm__tzz != yuxtb__hnlc:
                    print('Schema in {!s} was different. \n{!s}\n\nvs\n\n{!s}'
                        .format(phxgk__nsjbx, yuxtb__hnlc, nkzm__tzz))
                    jfw__wwmq = False
                    break
        if xnx__pntwd:
            jfw__wwmq = pxji__waf.allreduce(jfw__wwmq, op=MPI.LAND)
            if not jfw__wwmq:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            amm__nwrpr._bodo_total_rows = pxji__waf.allreduce(iogl__rczz,
                op=MPI.SUM)
            dnl__vzgw = pxji__waf.allreduce(reako__kao, op=MPI.SUM)
            intgi__ujl = pxji__waf.allreduce(lti__potyf, op=MPI.SUM)
            izvfr__cqayh = np.array([yiiw__ffu._bodo_num_rows for yiiw__ffu in
                amm__nwrpr.pieces])
            izvfr__cqayh = pxji__waf.allreduce(izvfr__cqayh, op=MPI.SUM)
            for yiiw__ffu, ekerc__gol in zip(amm__nwrpr.pieces, izvfr__cqayh):
                yiiw__ffu._bodo_num_rows = ekerc__gol
            if is_parallel and bodo.get_rank(
                ) == 0 and dnl__vzgw < bodo.get_size() and dnl__vzgw != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({dnl__vzgw}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()})
"""
                    ))
            if dnl__vzgw == 0:
                ixni__yveg = 0
            else:
                ixni__yveg = intgi__ujl // dnl__vzgw
            if (bodo.get_rank() == 0 and intgi__ujl >= 20 * 1048576 and 
                ixni__yveg < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({ixni__yveg} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                rvzr__arwb.add_attribute('g_total_num_row_groups', dnl__vzgw)
                if expr_filters is not None:
                    rvzr__arwb.add_attribute('total_scan_time', sqlv__slq)
                brjxm__xbr = np.array([yiiw__ffu._bodo_num_rows for
                    yiiw__ffu in amm__nwrpr.pieces])
                saql__jncyr = np.percentile(brjxm__xbr, [25, 50, 75])
                rvzr__arwb.add_attribute('g_row_counts_min', brjxm__xbr.min())
                rvzr__arwb.add_attribute('g_row_counts_Q1', saql__jncyr[0])
                rvzr__arwb.add_attribute('g_row_counts_median', saql__jncyr[1])
                rvzr__arwb.add_attribute('g_row_counts_Q3', saql__jncyr[2])
                rvzr__arwb.add_attribute('g_row_counts_max', brjxm__xbr.max())
                rvzr__arwb.add_attribute('g_row_counts_mean', brjxm__xbr.mean()
                    )
                rvzr__arwb.add_attribute('g_row_counts_std', brjxm__xbr.std())
                rvzr__arwb.add_attribute('g_row_counts_sum', brjxm__xbr.sum())
                rvzr__arwb.finalize()
    amm__nwrpr._prefix = ''
    if protocol in {'hdfs', 'abfs', 'abfss'}:
        prefix = f'{protocol}://{iktm__wvgsu.netloc}'
        if len(amm__nwrpr.pieces) > 0:
            phxgk__nsjbx = amm__nwrpr.pieces[0]
            if not phxgk__nsjbx.path.startswith(prefix):
                amm__nwrpr._prefix = prefix
    if read_categories:
        _add_categories_to_pq_dataset(amm__nwrpr)
    if get_row_counts:
        ckkif__hqzyi.finalize()
    return amm__nwrpr


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, storage_options, region, prefix):
    import pyarrow as pa
    ztc__qpu = os.cpu_count()
    if ztc__qpu is None or ztc__qpu == 0:
        ztc__qpu = 2
    drb__utx = min(4, ztc__qpu)
    lbohg__gxc = min(16, ztc__qpu)
    if is_parallel and len(fpaths) > lbohg__gxc and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(lbohg__gxc)
        pa.set_cpu_count(lbohg__gxc)
    else:
        pa.set_io_thread_count(drb__utx)
        pa.set_cpu_count(drb__utx)
    if fpaths[0].startswith('s3://'):
        kzcuo__upu = urlparse(fpaths[0]).netloc
        prefix = 's3://' + kzcuo__upu + '/'
        fpaths = [uke__qjhd[len(prefix):] for uke__qjhd in fpaths]
        iuy__bxtk = get_s3_subtree_fs(kzcuo__upu, region=region,
            storage_options=storage_options)
    elif prefix and prefix.startswith(('hdfs', 'abfs', 'abfss')):
        iuy__bxtk = get_hdfs_fs(prefix + fpaths[0])
    elif fpaths[0].startswith(('gcs', 'gs')):
        import gcsfs
        iuy__bxtk = gcsfs.GCSFileSystem(token=None)
    else:
        iuy__bxtk = None
    amm__nwrpr = ds.dataset(fpaths, filesystem=iuy__bxtk, partitioning=ds.
        partitioning(flavor='hive'))
    col_names = amm__nwrpr.schema.names
    nvdq__ifps = [col_names[bbmqb__vkqup] for bbmqb__vkqup in selected_fields]
    xlwf__zong = amm__nwrpr.scanner(columns=nvdq__ifps, filter=expr_filters,
        use_threads=True).to_reader()
    return amm__nwrpr, xlwf__zong


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    rrjl__yalcx = pq_dataset.schema.to_arrow_schema()
    rwsp__lzhe = [c for c in rrjl__yalcx.names if isinstance(rrjl__yalcx.
        field(c).type, pa.DictionaryType)]
    if len(rwsp__lzhe) == 0:
        pq_dataset._category_info = {}
        return
    pxji__waf = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            uirm__zik = pq_dataset.pieces[0].open()
            jyji__fymfq = uirm__zik.read_row_group(0, rwsp__lzhe)
            category_info = {c: tuple(jyji__fymfq.column(c).chunk(0).
                dictionary.to_pylist()) for c in rwsp__lzhe}
            del uirm__zik, jyji__fymfq
        except Exception as sdo__nkp:
            pxji__waf.bcast(sdo__nkp)
            raise sdo__nkp
        pxji__waf.bcast(category_info)
    else:
        category_info = pxji__waf.bcast(None)
        if isinstance(category_info, Exception):
            qnfiu__btzq = category_info
            raise qnfiu__btzq
    pq_dataset._category_info = category_info


def get_pandas_metadata(schema, num_pieces):
    xxr__wty = None
    nullable_from_metadata = defaultdict(lambda : None)
    esnea__nwe = b'pandas'
    if schema.metadata is not None and esnea__nwe in schema.metadata:
        import json
        uwutc__vqyy = json.loads(schema.metadata[esnea__nwe].decode('utf8'))
        atd__teagi = len(uwutc__vqyy['index_columns'])
        if atd__teagi > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        xxr__wty = uwutc__vqyy['index_columns'][0] if atd__teagi else None
        if not isinstance(xxr__wty, str) and (not isinstance(xxr__wty, dict
            ) or num_pieces != 1):
            xxr__wty = None
        for naya__rjnc in uwutc__vqyy['columns']:
            xcom__htbj = naya__rjnc['name']
            if naya__rjnc['pandas_type'].startswith('int'
                ) and xcom__htbj is not None:
                if naya__rjnc['numpy_type'].startswith('Int'):
                    nullable_from_metadata[xcom__htbj] = True
                else:
                    nullable_from_metadata[xcom__htbj] = False
    return xxr__wty, nullable_from_metadata


def parquet_file_schema(file_name, selected_columns, storage_options=None):
    col_names = []
    cjcka__kkxjf = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = [] if pq_dataset.partitions is None else [pq_dataset.
        partitions.levels[agika__gfpno].name for agika__gfpno in range(len(
        pq_dataset.partitions.partition_names))]
    rrjl__yalcx = pq_dataset.schema.to_arrow_schema()
    num_pieces = len(pq_dataset.pieces)
    col_names = rrjl__yalcx.names
    xxr__wty, nullable_from_metadata = get_pandas_metadata(rrjl__yalcx,
        num_pieces)
    nqmzt__wfybv = [_get_numba_typ_from_pa_typ(rrjl__yalcx.field(c), c ==
        xxr__wty, nullable_from_metadata[c], pq_dataset._category_info) for
        c in col_names]
    if partition_names:
        col_names += partition_names
        nqmzt__wfybv += [_get_partition_cat_dtype(pq_dataset.partitions.
            levels[agika__gfpno]) for agika__gfpno in range(len(
            partition_names))]
    ugdip__pjcp = {c: agika__gfpno for agika__gfpno, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in ugdip__pjcp:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if xxr__wty and not isinstance(xxr__wty, dict
        ) and xxr__wty not in selected_columns:
        selected_columns.append(xxr__wty)
    col_indices = [ugdip__pjcp[c] for c in selected_columns]
    cjcka__kkxjf = [nqmzt__wfybv[ugdip__pjcp[c]] for c in selected_columns]
    col_names = selected_columns
    return col_names, cjcka__kkxjf, xxr__wty, col_indices, partition_names


def _get_partition_cat_dtype(part_set):
    xwd__atwem = part_set.dictionary.to_pandas()
    cjt__ipqe = bodo.typeof(xwd__atwem).dtype
    gmer__gzhlf = PDCategoricalDtype(tuple(xwd__atwem), cjt__ipqe, False)
    return CategoricalArrayType(gmer__gzhlf)


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
        hezi__svfa = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer()])
        bqy__npbub = cgutils.get_or_insert_function(builder.module,
            hezi__svfa, name='pq_write')
        builder.call(bqy__npbub, args)
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
        hezi__svfa = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer()])
        bqy__npbub = cgutils.get_or_insert_function(builder.module,
            hezi__svfa, name='pq_write_partitioned')
        builder.call(bqy__npbub, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr), codegen
