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
        except OSError as eor__mziqe:
            if 'non-file path' in str(eor__mziqe):
                raise FileNotFoundError(str(eor__mziqe))
            raise


class ParquetHandler:

    def __init__(self, func_ir, typingctx, args, _locals):
        self.func_ir = func_ir
        self.typingctx = typingctx
        self.args = args
        self.locals = _locals

    def gen_parquet_read(self, file_name, lhs, columns, storage_options=None):
        zdasj__jku = lhs.scope
        ahmmw__hfpc = lhs.loc
        sinc__oxme = None
        if lhs.name in self.locals:
            sinc__oxme = self.locals[lhs.name]
            self.locals.pop(lhs.name)
        lux__fxv = {}
        if lhs.name + ':convert' in self.locals:
            lux__fxv = self.locals[lhs.name + ':convert']
            self.locals.pop(lhs.name + ':convert')
        if sinc__oxme is None:
            bsyxe__ubcw = (
                'Parquet schema not available. Either path argument should be constant for Bodo to look at the file at compile time or schema should be provided. For more information, see: https://docs.bodo.ai/latest/source/programming_with_bodo/file_io.html#non-constant-filepaths'
                )
            tkzqf__rdlei = get_const_value(file_name, self.func_ir,
                bsyxe__ubcw, arg_types=self.args, file_info=ParquetFileInfo
                (columns, storage_options=storage_options))
            hra__hlpxk = False
            blm__jmy = guard(get_definition, self.func_ir, file_name)
            if isinstance(blm__jmy, ir.Arg):
                typ = self.args[blm__jmy.index]
                if isinstance(typ, types.FilenameType):
                    (col_names, rmd__isf, hrfy__cnras, col_indices,
                        partition_names) = typ.schema
                    hra__hlpxk = True
            if not hra__hlpxk:
                (col_names, rmd__isf, hrfy__cnras, col_indices, partition_names
                    ) = (parquet_file_schema(tkzqf__rdlei, columns,
                    storage_options=storage_options))
        else:
            raabo__ilf = list(sinc__oxme.keys())
            wvdir__gwm = {c: gdmse__cdjb for gdmse__cdjb, c in enumerate(
                raabo__ilf)}
            hgcrd__bspc = [dqjcj__cny for dqjcj__cny in sinc__oxme.values()]
            hrfy__cnras = 'index' if 'index' in wvdir__gwm else None
            if columns is None:
                selected_columns = raabo__ilf
            else:
                selected_columns = columns
            col_indices = [wvdir__gwm[c] for c in selected_columns]
            rmd__isf = [hgcrd__bspc[wvdir__gwm[c]] for c in selected_columns]
            col_names = selected_columns
            hrfy__cnras = hrfy__cnras if hrfy__cnras in col_names else None
            partition_names = []
        wsw__lkxc = None if isinstance(hrfy__cnras, dict
            ) or hrfy__cnras is None else hrfy__cnras
        index_column_index = None
        index_column_type = types.none
        if wsw__lkxc:
            fyzpt__hcvhs = col_names.index(wsw__lkxc)
            col_indices = col_indices.copy()
            rmd__isf = rmd__isf.copy()
            index_column_index = col_indices.pop(fyzpt__hcvhs)
            index_column_type = rmd__isf.pop(fyzpt__hcvhs)
        for gdmse__cdjb, c in enumerate(col_names):
            if c in lux__fxv:
                rmd__isf[gdmse__cdjb] = lux__fxv[c]
        jydj__wza = [ir.Var(zdasj__jku, mk_unique_var('pq_table'),
            ahmmw__hfpc), ir.Var(zdasj__jku, mk_unique_var('pq_index'),
            ahmmw__hfpc)]
        zyik__msdex = [bodo.ir.parquet_ext.ParquetReader(file_name, lhs.
            name, col_names, col_indices, rmd__isf, jydj__wza, ahmmw__hfpc,
            partition_names, storage_options, index_column_index,
            index_column_type)]
        return (col_names, jydj__wza, hrfy__cnras, zyik__msdex, rmd__isf,
            index_column_type)


def determine_filter_cast(pq_node, typemap, filter_val, orig_colname_map):
    rop__hmcj = filter_val[0]
    qgx__krmir = pq_node.original_out_types[orig_colname_map[rop__hmcj]]
    zdsqb__axq = bodo.utils.typing.element_type(qgx__krmir)
    if rop__hmcj in pq_node.partition_names:
        if zdsqb__axq == types.unicode_type:
            bakq__qjdi = '.cast(pyarrow.string(), safe=False)'
        elif isinstance(zdsqb__axq, types.Integer):
            bakq__qjdi = f'.cast(pyarrow.{zdsqb__axq.name}(), safe=False)'
        else:
            bakq__qjdi = ''
    else:
        bakq__qjdi = ''
    aye__krffw = typemap[filter_val[2].name]
    if not bodo.utils.typing.is_common_scalar_dtype([zdsqb__axq, aye__krffw]):
        if not bodo.utils.typing.is_safe_arrow_cast(zdsqb__axq, aye__krffw):
            raise BodoError(
                f'Unsupport Arrow cast from {zdsqb__axq} to {aye__krffw} in filter pushdown. Please try a comparison that avoids casting the column.'
                )
        if zdsqb__axq == types.unicode_type:
            return ".cast(pyarrow.timestamp('ns'), safe=False)", ''
        elif zdsqb__axq in (bodo.datetime64ns, bodo.pd_timestamp_type):
            return bakq__qjdi, ".cast(pyarrow.timestamp('ns'), safe=False)"
    return bakq__qjdi, ''


def pq_distributed_run(pq_node, array_dists, typemap, calltypes, typingctx,
    targetctx, meta_head_only_info=None):
    xuvp__ojnxj = len(pq_node.out_vars)
    extra_args = ''
    dnf_filter_str = 'None'
    expr_filter_str = 'None'
    xft__opips, bha__dprpx = bodo.ir.connector.generate_filter_map(pq_node.
        filters)
    if pq_node.filters:
        vwk__whzax = []
        rbe__zbqf = []
        nrgk__tkc = False
        gos__iro = None
        orig_colname_map = {c: gdmse__cdjb for gdmse__cdjb, c in enumerate(
            pq_node.original_df_colnames)}
        for bpjhr__lwml in pq_node.filters:
            vjza__off = []
            enewz__vxqd = []
            wfkxe__upwb = set()
            for tpaa__famc in bpjhr__lwml:
                if isinstance(tpaa__famc[2], ir.Var):
                    tgv__oqzy, rogyv__kkxk = determine_filter_cast(pq_node,
                        typemap, tpaa__famc, orig_colname_map)
                    enewz__vxqd.append(
                        f"(ds.field('{tpaa__famc[0]}'){tgv__oqzy} {tpaa__famc[1]} ds.scalar({xft__opips[tpaa__famc[2].name]}){rogyv__kkxk})"
                        )
                else:
                    assert tpaa__famc[2
                        ] == 'NULL', 'unsupport constant used in filter pushdown'
                    if tpaa__famc[1] == 'is not':
                        prefix = '~'
                    else:
                        prefix = ''
                    enewz__vxqd.append(
                        f"({prefix}ds.field('{tpaa__famc[0]}').is_null())")
                if tpaa__famc[0] in pq_node.partition_names and isinstance(
                    tpaa__famc[2], ir.Var):
                    lxc__wkudd = (
                        f"('{tpaa__famc[0]}', '{tpaa__famc[1]}', {xft__opips[tpaa__famc[2].name]})"
                        )
                    vjza__off.append(lxc__wkudd)
                    wfkxe__upwb.add(lxc__wkudd)
                else:
                    nrgk__tkc = True
            if gos__iro is None:
                gos__iro = wfkxe__upwb
            else:
                gos__iro.intersection_update(wfkxe__upwb)
            yfsu__iyr = ', '.join(vjza__off)
            kvp__umk = ' & '.join(enewz__vxqd)
            if yfsu__iyr:
                vwk__whzax.append(f'[{yfsu__iyr}]')
            rbe__zbqf.append(f'({kvp__umk})')
        nzzo__pjqem = ', '.join(vwk__whzax)
        ajzl__tbvcy = ' | '.join(rbe__zbqf)
        if nrgk__tkc:
            if gos__iro:
                gpdn__rxv = sorted(gos__iro)
                dnf_filter_str = f"[[{', '.join(gpdn__rxv)}]]"
        elif nzzo__pjqem:
            dnf_filter_str = f'[{nzzo__pjqem}]'
        expr_filter_str = f'({ajzl__tbvcy})'
        extra_args = ', '.join(xft__opips.values())
    fqpz__ehoy = ', '.join(f'out{gdmse__cdjb}' for gdmse__cdjb in range(
        xuvp__ojnxj))
    ihbz__uehh = f'def pq_impl(fname, {extra_args}):\n'
    ihbz__uehh += (
        f'    (total_rows, {fqpz__ehoy},) = _pq_reader_py(fname, {extra_args})\n'
        )
    gybs__vecp = {}
    exec(ihbz__uehh, {}, gybs__vecp)
    oxr__nwbst = gybs__vecp['pq_impl']
    parallel = False
    if array_dists is not None:
        biw__ehpxy = pq_node.out_vars[0].name
        parallel = array_dists[biw__ehpxy] in (distributed_pass.
            Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        slaf__jhl = pq_node.out_vars[1].name
        assert typemap[slaf__jhl] == types.none or not parallel or array_dists[
            slaf__jhl] in (distributed_pass.Distribution.OneD,
            distributed_pass.Distribution.OneD_Var
            ), 'pq data/index parallelization does not match'
    fcth__gtua = _gen_pq_reader_py(pq_node.df_colnames, pq_node.col_indices,
        pq_node.type_usecol_offset, pq_node.out_types, pq_node.
        storage_options, pq_node.partition_names, dnf_filter_str,
        expr_filter_str, extra_args, parallel, meta_head_only_info, pq_node
        .index_column_index, pq_node.index_column_type)
    htvxk__gefa = typemap[pq_node.file_name.name]
    nqlwk__hjjo = (htvxk__gefa,) + tuple(typemap[tpaa__famc.name] for
        tpaa__famc in bha__dprpx)
    krcx__wkn = compile_to_numba_ir(oxr__nwbst, {'_pq_reader_py':
        fcth__gtua}, typingctx=typingctx, targetctx=targetctx, arg_typs=
        nqlwk__hjjo, typemap=typemap, calltypes=calltypes).blocks.popitem()[1]
    replace_arg_nodes(krcx__wkn, [pq_node.file_name] + bha__dprpx)
    zyik__msdex = krcx__wkn.body[:-3]
    if meta_head_only_info:
        zyik__msdex[-1 - xuvp__ojnxj].target = meta_head_only_info[1]
    zyik__msdex[-2].target = pq_node.out_vars[0]
    zyik__msdex[-1].target = pq_node.out_vars[1]
    return zyik__msdex


distributed_pass.distributed_run_extensions[bodo.ir.parquet_ext.ParquetReader
    ] = pq_distributed_run


def get_filters_pyobject(dnf_filter_str, expr_filter_str, vars):
    pass


@overload(get_filters_pyobject, no_unliteral=True)
def overload_get_filters_pyobject(dnf_filter_str, expr_filter_str, var_tup):
    thz__hwo = get_overload_const_str(dnf_filter_str)
    vwh__zddd = get_overload_const_str(expr_filter_str)
    hjoq__imle = ', '.join(f'f{gdmse__cdjb}' for gdmse__cdjb in range(len(
        var_tup)))
    ihbz__uehh = 'def impl(dnf_filter_str, expr_filter_str, var_tup):\n'
    if len(var_tup):
        ihbz__uehh += f'  {hjoq__imle}, = var_tup\n'
    ihbz__uehh += """  with numba.objmode(dnf_filters_py='parquet_predicate_type', expr_filters_py='parquet_predicate_type'):
"""
    ihbz__uehh += f'    dnf_filters_py = {thz__hwo}\n'
    ihbz__uehh += f'    expr_filters_py = {vwh__zddd}\n'
    ihbz__uehh += '  return (dnf_filters_py, expr_filters_py)\n'
    gybs__vecp = {}
    exec(ihbz__uehh, globals(), gybs__vecp)
    return gybs__vecp['impl']


@numba.njit
def get_fname_pyobject(fname):
    with numba.objmode(fname_py='read_parquet_fpath_type'):
        fname_py = fname
    return fname_py


def get_storage_options_pyobject(storage_options):
    pass


@overload(get_storage_options_pyobject, no_unliteral=True)
def overload_get_storage_options_pyobject(storage_options):
    agymr__jnnrf = get_overload_constant_dict(storage_options)
    ihbz__uehh = 'def impl(storage_options):\n'
    ihbz__uehh += (
        "  with numba.objmode(storage_options_py='storage_options_dict_type'):\n"
        )
    ihbz__uehh += f'    storage_options_py = {str(agymr__jnnrf)}\n'
    ihbz__uehh += '  return storage_options_py\n'
    gybs__vecp = {}
    exec(ihbz__uehh, globals(), gybs__vecp)
    return gybs__vecp['impl']


def _gen_pq_reader_py(col_names, col_indices, type_usecol_offset, out_types,
    storage_options, partition_names, dnf_filter_str, expr_filter_str,
    extra_args, is_parallel, meta_head_only_info, index_column_index,
    index_column_type):
    ufude__nxkby = next_label()
    srxx__mtn = ',' if extra_args else ''
    ihbz__uehh = f'def pq_reader_py(fname,{extra_args}):\n'
    ihbz__uehh += (
        f"    ev = bodo.utils.tracing.Event('read_parquet', {is_parallel})\n")
    ihbz__uehh += "    ev.add_attribute('fname', fname)\n"
    ihbz__uehh += f"""    bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={is_parallel})
"""
    ihbz__uehh += f"""    dnf_filters, expr_filters = get_filters_pyobject("{dnf_filter_str}", "{expr_filter_str}", ({extra_args}{srxx__mtn}))
"""
    ihbz__uehh += '    fname_py = get_fname_pyobject(fname)\n'
    storage_options['bodo_dummy'] = 'dummy'
    ihbz__uehh += (
        f'    storage_options_py = get_storage_options_pyobject({str(storage_options)})\n'
        )
    tot_rows_to_read = -1
    if meta_head_only_info and meta_head_only_info[0] is not None:
        tot_rows_to_read = meta_head_only_info[0]
    bno__ntl = not type_usecol_offset
    cpp__eqrul = [sanitize_varname(c) for c in col_names]
    partition_names = [sanitize_varname(c) for c in partition_names]
    twq__czkmt = {c: gdmse__cdjb for gdmse__cdjb, c in enumerate(col_indices)}
    qsg__bhy = {c: gdmse__cdjb for gdmse__cdjb, c in enumerate(cpp__eqrul)}
    oky__ovmwm = []
    uzg__tkayc = set()
    for gdmse__cdjb in type_usecol_offset:
        if cpp__eqrul[gdmse__cdjb] not in partition_names:
            oky__ovmwm.append(col_indices[gdmse__cdjb])
        else:
            uzg__tkayc.add(col_indices[gdmse__cdjb])
    if index_column_index is not None:
        oky__ovmwm.append(index_column_index)
    oky__ovmwm = sorted(oky__ovmwm)
    dbm__encry = {c: gdmse__cdjb for gdmse__cdjb, c in enumerate(oky__ovmwm)}

    def is_nullable(typ):
        return bodo.utils.utils.is_array_typ(typ, False) and not isinstance(typ
            , types.Array)
    npleq__yhxxe = [(int(is_nullable(out_types[twq__czkmt[scvb__lbogk]])) if
        scvb__lbogk != index_column_index else int(is_nullable(
        index_column_type))) for scvb__lbogk in oky__ovmwm]
    sxa__lgfw = []
    qxjoh__tyw = {}
    wyg__qye = []
    xys__abq = []
    for gdmse__cdjb, tbwqe__tptw in enumerate(partition_names):
        try:
            dcnz__cpezx = qsg__bhy[tbwqe__tptw]
            if col_indices[dcnz__cpezx] not in uzg__tkayc:
                continue
        except (KeyError, ValueError) as luf__mvsg:
            continue
        qxjoh__tyw[tbwqe__tptw] = len(sxa__lgfw)
        sxa__lgfw.append(tbwqe__tptw)
        wyg__qye.append(gdmse__cdjb)
        ipwcf__xurvg = out_types[dcnz__cpezx].dtype
        scq__qgtfp = bodo.hiframes.pd_categorical_ext.get_categories_int_type(
            ipwcf__xurvg)
        xys__abq.append(numba_to_c_type(scq__qgtfp))
    ihbz__uehh += f'    total_rows_np = np.array([0], dtype=np.int64)\n'
    if len(wyg__qye) > 0:
        ihbz__uehh += f"""    out_table = pq_read(fname_py, {is_parallel}, unicode_to_utf8(bucket_region), dnf_filters, expr_filters, storage_options_py, {tot_rows_to_read}, selected_cols_arr_{ufude__nxkby}.ctypes, {len(oky__ovmwm)}, nullable_cols_arr_{ufude__nxkby}.ctypes, np.array({wyg__qye}, dtype=np.int32).ctypes, np.array({xys__abq}, dtype=np.int32).ctypes, {len(wyg__qye)}, total_rows_np.ctypes)
"""
    else:
        ihbz__uehh += f"""    out_table = pq_read(fname_py, {is_parallel}, unicode_to_utf8(bucket_region), dnf_filters, expr_filters, storage_options_py, {tot_rows_to_read}, selected_cols_arr_{ufude__nxkby}.ctypes, {len(oky__ovmwm)}, nullable_cols_arr_{ufude__nxkby}.ctypes, 0, 0, 0, total_rows_np.ctypes)
"""
    ihbz__uehh += '    check_and_propagate_cpp_exception()\n'
    lryfe__guh = 'None'
    pxh__yxlo = index_column_type
    fgo__jgmcg = TableType(tuple(out_types))
    if bno__ntl:
        fgo__jgmcg = types.none
    if index_column_index is not None:
        yerhf__pcsdq = dbm__encry[index_column_index]
        lryfe__guh = (
            f'info_to_array(info_from_table(out_table, {yerhf__pcsdq}), index_arr_type)'
            )
    ihbz__uehh += f'    index_arr = {lryfe__guh}\n'
    if bno__ntl:
        wvp__sken = None
    else:
        wvp__sken = []
        kfbd__pip = 0
        for gdmse__cdjb, ngk__iqnpm in enumerate(col_indices):
            if kfbd__pip < len(type_usecol_offset
                ) and gdmse__cdjb == type_usecol_offset[kfbd__pip]:
                heey__zujc = col_indices[gdmse__cdjb]
                if heey__zujc in uzg__tkayc:
                    sfqi__xtbu = cpp__eqrul[gdmse__cdjb]
                    wvp__sken.append(len(oky__ovmwm) + qxjoh__tyw[sfqi__xtbu])
                else:
                    wvp__sken.append(dbm__encry[ngk__iqnpm])
                kfbd__pip += 1
            else:
                wvp__sken.append(-1)
        wvp__sken = np.array(wvp__sken, dtype=np.int64)
    if bno__ntl:
        ihbz__uehh += '    T = None\n'
    else:
        ihbz__uehh += f"""    T = cpp_table_to_py_table(out_table, table_idx_{ufude__nxkby}, py_table_type_{ufude__nxkby})
"""
    ihbz__uehh += '    delete_table(out_table)\n'
    ihbz__uehh += f'    total_rows = total_rows_np[0]\n'
    ihbz__uehh += f'    ev.finalize()\n'
    ihbz__uehh += '    return (total_rows, T, index_arr)\n'
    gybs__vecp = {}
    gokg__ljh = {f'py_table_type_{ufude__nxkby}': fgo__jgmcg,
        f'table_idx_{ufude__nxkby}': wvp__sken,
        f'selected_cols_arr_{ufude__nxkby}': np.array(oky__ovmwm, np.int32),
        f'nullable_cols_arr_{ufude__nxkby}': np.array(npleq__yhxxe, np.
        int32), 'index_arr_type': pxh__yxlo, 'cpp_table_to_py_table':
        cpp_table_to_py_table, 'info_to_array': info_to_array,
        'info_from_table': info_from_table, 'delete_table': delete_table,
        'check_and_propagate_cpp_exception':
        check_and_propagate_cpp_exception, 'pq_read': _pq_read,
        'unicode_to_utf8': unicode_to_utf8, 'get_filters_pyobject':
        get_filters_pyobject, 'get_storage_options_pyobject':
        get_storage_options_pyobject, 'get_fname_pyobject':
        get_fname_pyobject, 'np': np, 'pd': pd, 'bodo': bodo}
    exec(ihbz__uehh, gokg__ljh, gybs__vecp)
    fcth__gtua = gybs__vecp['pq_reader_py']
    ddnfd__gyz = numba.njit(fcth__gtua, no_cpython_wrapper=True)
    return ddnfd__gyz


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
        gnd__mnlur = []
        zcni__vpbj = []
        for ianr__uam in pa_typ.flatten():
            zcni__vpbj.append(ianr__uam.name.split('.')[-1])
            gnd__mnlur.append(_get_numba_typ_from_pa_typ(ianr__uam,
                is_index, nullable_from_metadata, category_info))
        return StructArrayType(tuple(gnd__mnlur), tuple(zcni__vpbj))
    if isinstance(pa_typ.type, pa.Decimal128Type):
        return DecimalArrayType(pa_typ.type.precision, pa_typ.type.scale)
    if isinstance(pa_typ.type, pa.DictionaryType):
        if pa_typ.type.value_type != pa.string():
            raise BodoError(
                f'Parquet Categorical data type should be string, not {pa_typ.type.value_type}'
                )
        nng__dzpqx = _pa_numba_typ_map[pa_typ.type.index_type]
        nhpj__ynsep = PDCategoricalDtype(category_info[pa_typ.name], bodo.
            string_type, pa_typ.type.ordered, int_type=nng__dzpqx)
        return CategoricalArrayType(nhpj__ynsep)
    if pa_typ.type not in _pa_numba_typ_map:
        raise BodoError('Arrow data type {} not supported yet'.format(
            pa_typ.type))
    gmnxr__jzmz = _pa_numba_typ_map[pa_typ.type]
    if gmnxr__jzmz == datetime_date_type:
        return datetime_date_array_type
    if gmnxr__jzmz == bytes_type:
        return binary_array_type
    hkslx__edr = (string_array_type if gmnxr__jzmz == string_type else
        types.Array(gmnxr__jzmz, 1, 'C'))
    if gmnxr__jzmz == types.bool_:
        hkslx__edr = boolean_array
    if nullable_from_metadata is not None:
        xfox__gefi = nullable_from_metadata
    else:
        xfox__gefi = use_nullable_int_arr
    if xfox__gefi and not is_index and isinstance(gmnxr__jzmz, types.Integer
        ) and pa_typ.nullable:
        hkslx__edr = IntegerArrayType(gmnxr__jzmz)
    return hkslx__edr


def get_parquet_dataset(fpath, get_row_counts=True, dnf_filters=None,
    expr_filters=None, storage_options=None, read_categories=False,
    is_parallel=False, tot_rows_to_read=None):
    if get_row_counts:
        xvtx__rnxr = tracing.Event('get_parquet_dataset')
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    from mpi4py import MPI
    bmmy__ifsc = MPI.COMM_WORLD
    if isinstance(fpath, list):
        mjs__eilli = urlparse(fpath[0])
        protocol = mjs__eilli.scheme
        koyt__vtu = mjs__eilli.netloc
        for gdmse__cdjb in range(len(fpath)):
            sdx__zxvhg = fpath[gdmse__cdjb]
            vgziw__qrag = urlparse(sdx__zxvhg)
            if vgziw__qrag.scheme != protocol:
                raise BodoError(
                    'All parquet files must use the same filesystem protocol')
            if vgziw__qrag.netloc != koyt__vtu:
                raise BodoError(
                    'All parquet files must be in the same S3 bucket')
            fpath[gdmse__cdjb] = sdx__zxvhg.rstrip('/')
    else:
        mjs__eilli = urlparse(fpath)
        protocol = mjs__eilli.scheme
        fpath = fpath.rstrip('/')
    if protocol in {'gcs', 'gs'}:
        try:
            import gcsfs
        except ImportError as luf__mvsg:
            cyvk__yosps = """Couldn't import gcsfs, which is required for Google cloud access. gcsfs can be installed by calling 'conda install -c conda-forge gcsfs'.
"""
            raise BodoError(cyvk__yosps)
    if protocol == 'http':
        try:
            import fsspec
        except ImportError as luf__mvsg:
            cyvk__yosps = """Couldn't import fsspec, which is required for http access. fsspec can be installed by calling 'conda install -c conda-forge fsspec'.
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
            deu__eedd = gcsfs.GCSFileSystem(token=None)
            fs.append(deu__eedd)
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
                prefix = f'{protocol}://{mjs__eilli.netloc}'
                path = path[len(prefix):]
            gvy__obdjn = fs.glob(path)
            if protocol == 's3':
                gvy__obdjn = [('s3://' + sdx__zxvhg) for sdx__zxvhg in
                    gvy__obdjn if not sdx__zxvhg.startswith('s3://')]
            elif protocol in {'hdfs', 'abfs', 'abfss'}:
                gvy__obdjn = [(prefix + sdx__zxvhg) for sdx__zxvhg in
                    gvy__obdjn]
        except:
            raise BodoError(
                f'glob pattern expansion not supported for {protocol}')
        if len(gvy__obdjn) == 0:
            raise BodoError('No files found matching glob pattern')
        return gvy__obdjn
    royjx__bjyh = False
    if get_row_counts:
        uizhu__kul = getfs(parallel=True)
        royjx__bjyh = bodo.parquet_validate_schema
    if bodo.get_rank() == 0:
        qgg__ifow = 1
        iimuf__ysya = os.cpu_count()
        if iimuf__ysya is not None and iimuf__ysya > 1:
            qgg__ifow = iimuf__ysya // 2
        try:
            if get_row_counts:
                tdz__rzww = tracing.Event('pq.ParquetDataset', is_parallel=
                    False)
                if tracing.is_tracing():
                    tdz__rzww.add_attribute('dnf_filter', str(dnf_filters))
            cie__solif = pa.io_thread_count()
            pa.set_io_thread_count(qgg__ifow)
            if '*' in fpath:
                fpath = glob(protocol, getfs(), fpath)
            if protocol == 's3':
                if isinstance(fpath, list):
                    get_legacy_fs().info(fpath[0])
                else:
                    get_legacy_fs().info(fpath)
            if protocol in {'hdfs', 'abfs', 'abfss'}:
                prefix = f'{protocol}://{mjs__eilli.netloc}'
                if isinstance(fpath, list):
                    mbsje__pfdu = [sdx__zxvhg[len(prefix):] for sdx__zxvhg in
                        fpath]
                else:
                    mbsje__pfdu = fpath[len(prefix):]
            else:
                mbsje__pfdu = fpath
            fwscp__nbo = pq.ParquetDataset(mbsje__pfdu, filesystem=
                get_legacy_fs(), filters=None, use_legacy_dataset=True,
                validate_schema=False, metadata_nthreads=qgg__ifow)
            pa.set_io_thread_count(cie__solif)
            wtmdv__potuq = bodo.io.pa_parquet.get_dataset_schema(fwscp__nbo)
            if dnf_filters:
                if get_row_counts:
                    tdz__rzww.add_attribute('num_pieces_before_filter', len
                        (fwscp__nbo.pieces))
                dwev__vnfti = time.time()
                fwscp__nbo._filter(dnf_filters)
                if get_row_counts:
                    tdz__rzww.add_attribute('dnf_filter_time', time.time() -
                        dwev__vnfti)
                    tdz__rzww.add_attribute('num_pieces_after_filter', len(
                        fwscp__nbo.pieces))
            if get_row_counts:
                tdz__rzww.finalize()
            fwscp__nbo._metadata.fs = None
        except Exception as eor__mziqe:
            bmmy__ifsc.bcast(eor__mziqe)
            raise BodoError(
                f'error from pyarrow: {type(eor__mziqe).__name__}: {str(eor__mziqe)}\n'
                )
        if get_row_counts:
            hphbr__mwpm = tracing.Event('bcast dataset')
        bmmy__ifsc.bcast(fwscp__nbo)
        bmmy__ifsc.bcast(wtmdv__potuq)
    else:
        if get_row_counts:
            hphbr__mwpm = tracing.Event('bcast dataset')
        fwscp__nbo = bmmy__ifsc.bcast(None)
        if isinstance(fwscp__nbo, Exception):
            emltn__imsl = fwscp__nbo
            raise BodoError(
                f"""error from pyarrow: {type(emltn__imsl).__name__}: {str(emltn__imsl)}
"""
                )
        wtmdv__potuq = bmmy__ifsc.bcast(None)
    if get_row_counts:
        hphbr__mwpm.finalize()
    fwscp__nbo._bodo_total_rows = 0
    if get_row_counts and tot_rows_to_read == 0:
        get_row_counts = royjx__bjyh = False
        for scd__vdxt in fwscp__nbo.pieces:
            scd__vdxt._bodo_num_rows = 0
    if get_row_counts or royjx__bjyh:
        if get_row_counts and tracing.is_tracing():
            iur__hsum = tracing.Event('get_row_counts')
            iur__hsum.add_attribute('g_num_pieces', len(fwscp__nbo.pieces))
            iur__hsum.add_attribute('g_expr_filters', str(expr_filters))
        ega__xdxvm = 0.0
        num_pieces = len(fwscp__nbo.pieces)
        start = get_start(num_pieces, bodo.get_size(), bodo.get_rank())
        qjwj__wlp = get_end(num_pieces, bodo.get_size(), bodo.get_rank())
        rlf__cwtab = 0
        bqjef__amz = 0
        xxyjo__vjymy = 0
        qkues__plkvy = True
        fwscp__nbo._metadata.fs = getfs()
        if expr_filters is not None:
            import random
            random.seed(37)
            chts__qwezv = random.sample(fwscp__nbo.pieces, k=len(fwscp__nbo
                .pieces))
        else:
            chts__qwezv = fwscp__nbo.pieces
        for scd__vdxt in chts__qwezv:
            scd__vdxt._bodo_num_rows = 0
        fpaths = [scd__vdxt.path for scd__vdxt in chts__qwezv[start:qjwj__wlp]]
        if protocol == 's3':
            koyt__vtu = mjs__eilli.netloc
            prefix = 's3://' + koyt__vtu + '/'
            fpaths = [sdx__zxvhg[len(prefix):] for sdx__zxvhg in fpaths]
            ykg__qbl = get_s3_subtree_fs(koyt__vtu, region=getfs().region,
                storage_options=storage_options)
        else:
            ykg__qbl = getfs()
        pa.set_io_thread_count(4)
        pa.set_cpu_count(4)
        ouu__qnju = ds.dataset(fpaths, filesystem=ykg__qbl, partitioning=ds
            .partitioning(flavor='hive'))
        for wlx__umtm, wftz__cfyl in zip(chts__qwezv[start:qjwj__wlp],
            ouu__qnju.get_fragments()):
            dwev__vnfti = time.time()
            mlqyz__tihoc = wftz__cfyl.scanner(schema=ouu__qnju.schema,
                filter=expr_filters, use_threads=True).count_rows()
            ega__xdxvm += time.time() - dwev__vnfti
            wlx__umtm._bodo_num_rows = mlqyz__tihoc
            rlf__cwtab += mlqyz__tihoc
            bqjef__amz += wftz__cfyl.num_row_groups
            xxyjo__vjymy += sum(uye__ycb.total_byte_size for uye__ycb in
                wftz__cfyl.row_groups)
            if royjx__bjyh:
                iemq__hkhc = wftz__cfyl.metadata.schema.to_arrow_schema()
                if wtmdv__potuq != iemq__hkhc:
                    print('Schema in {!s} was different. \n{!s}\n\nvs\n\n{!s}'
                        .format(wlx__umtm, iemq__hkhc, wtmdv__potuq))
                    qkues__plkvy = False
                    break
        if royjx__bjyh:
            qkues__plkvy = bmmy__ifsc.allreduce(qkues__plkvy, op=MPI.LAND)
            if not qkues__plkvy:
                raise BodoError("Schema in parquet files don't match")
        if get_row_counts:
            fwscp__nbo._bodo_total_rows = bmmy__ifsc.allreduce(rlf__cwtab,
                op=MPI.SUM)
            eya__lih = bmmy__ifsc.allreduce(bqjef__amz, op=MPI.SUM)
            wkc__awtm = bmmy__ifsc.allreduce(xxyjo__vjymy, op=MPI.SUM)
            twxqk__afkdx = np.array([scd__vdxt._bodo_num_rows for scd__vdxt in
                fwscp__nbo.pieces])
            twxqk__afkdx = bmmy__ifsc.allreduce(twxqk__afkdx, op=MPI.SUM)
            for scd__vdxt, jujk__axoqd in zip(fwscp__nbo.pieces, twxqk__afkdx):
                scd__vdxt._bodo_num_rows = jujk__axoqd
            if is_parallel and bodo.get_rank(
                ) == 0 and eya__lih < bodo.get_size() and eya__lih != 0:
                warnings.warn(BodoWarning(
                    f"""Total number of row groups in parquet dataset {fpath} ({eya__lih}) is too small for effective IO parallelization.
For best performance the number of row groups should be greater than the number of workers ({bodo.get_size()})
"""
                    ))
            if eya__lih == 0:
                vrt__wukn = 0
            else:
                vrt__wukn = wkc__awtm // eya__lih
            if (bodo.get_rank() == 0 and wkc__awtm >= 20 * 1048576 and 
                vrt__wukn < 1048576 and protocol in REMOTE_FILESYSTEMS):
                warnings.warn(BodoWarning(
                    f'Parquet average row group size is small ({vrt__wukn} bytes) and can have negative impact on performance when reading from remote sources'
                    ))
            if tracing.is_tracing():
                iur__hsum.add_attribute('g_total_num_row_groups', eya__lih)
                if expr_filters is not None:
                    iur__hsum.add_attribute('total_scan_time', ega__xdxvm)
                pssb__spunu = np.array([scd__vdxt._bodo_num_rows for
                    scd__vdxt in fwscp__nbo.pieces])
                zwaj__tdymr = np.percentile(pssb__spunu, [25, 50, 75])
                iur__hsum.add_attribute('g_row_counts_min', pssb__spunu.min())
                iur__hsum.add_attribute('g_row_counts_Q1', zwaj__tdymr[0])
                iur__hsum.add_attribute('g_row_counts_median', zwaj__tdymr[1])
                iur__hsum.add_attribute('g_row_counts_Q3', zwaj__tdymr[2])
                iur__hsum.add_attribute('g_row_counts_max', pssb__spunu.max())
                iur__hsum.add_attribute('g_row_counts_mean', pssb__spunu.mean()
                    )
                iur__hsum.add_attribute('g_row_counts_std', pssb__spunu.std())
                iur__hsum.add_attribute('g_row_counts_sum', pssb__spunu.sum())
                iur__hsum.finalize()
    fwscp__nbo._prefix = ''
    if protocol in {'hdfs', 'abfs', 'abfss'}:
        prefix = f'{protocol}://{mjs__eilli.netloc}'
        if len(fwscp__nbo.pieces) > 0:
            wlx__umtm = fwscp__nbo.pieces[0]
            if not wlx__umtm.path.startswith(prefix):
                fwscp__nbo._prefix = prefix
    if read_categories:
        _add_categories_to_pq_dataset(fwscp__nbo)
    if get_row_counts:
        xvtx__rnxr.finalize()
    return fwscp__nbo


def get_scanner_batches(fpaths, expr_filters, selected_fields,
    avg_num_pieces, is_parallel, storage_options, region, prefix):
    import pyarrow as pa
    iimuf__ysya = os.cpu_count()
    if iimuf__ysya is None or iimuf__ysya == 0:
        iimuf__ysya = 2
    zewxf__mzm = min(4, iimuf__ysya)
    wmmd__dxrw = min(16, iimuf__ysya)
    if is_parallel and len(fpaths) > wmmd__dxrw and len(fpaths
        ) / avg_num_pieces >= 2.0:
        pa.set_io_thread_count(wmmd__dxrw)
        pa.set_cpu_count(wmmd__dxrw)
    else:
        pa.set_io_thread_count(zewxf__mzm)
        pa.set_cpu_count(zewxf__mzm)
    if fpaths[0].startswith('s3://'):
        koyt__vtu = urlparse(fpaths[0]).netloc
        prefix = 's3://' + koyt__vtu + '/'
        fpaths = [sdx__zxvhg[len(prefix):] for sdx__zxvhg in fpaths]
        ykg__qbl = get_s3_subtree_fs(koyt__vtu, region=region,
            storage_options=storage_options)
    elif prefix and prefix.startswith(('hdfs', 'abfs', 'abfss')):
        ykg__qbl = get_hdfs_fs(prefix + fpaths[0])
    elif fpaths[0].startswith(('gcs', 'gs')):
        import gcsfs
        ykg__qbl = gcsfs.GCSFileSystem(token=None)
    else:
        ykg__qbl = None
    fwscp__nbo = ds.dataset(fpaths, filesystem=ykg__qbl, partitioning=ds.
        partitioning(flavor='hive'))
    col_names = fwscp__nbo.schema.names
    jad__jfef = [col_names[lcgqc__ayd] for lcgqc__ayd in selected_fields]
    qsock__dij = fwscp__nbo.scanner(columns=jad__jfef, filter=expr_filters,
        use_threads=True).to_reader()
    return fwscp__nbo, qsock__dij


def _add_categories_to_pq_dataset(pq_dataset):
    import pyarrow as pa
    from mpi4py import MPI
    if len(pq_dataset.pieces) < 1:
        raise BodoError(
            'No pieces found in Parquet dataset. Cannot get read categorical values'
            )
    ufhgi__ljeoa = pq_dataset.schema.to_arrow_schema()
    fonl__qedgd = [c for c in ufhgi__ljeoa.names if isinstance(ufhgi__ljeoa
        .field(c).type, pa.DictionaryType)]
    if len(fonl__qedgd) == 0:
        pq_dataset._category_info = {}
        return
    bmmy__ifsc = MPI.COMM_WORLD
    if bodo.get_rank() == 0:
        try:
            gbjw__zeu = pq_dataset.pieces[0].open()
            uye__ycb = gbjw__zeu.read_row_group(0, fonl__qedgd)
            category_info = {c: tuple(uye__ycb.column(c).chunk(0).
                dictionary.to_pylist()) for c in fonl__qedgd}
            del gbjw__zeu, uye__ycb
        except Exception as eor__mziqe:
            bmmy__ifsc.bcast(eor__mziqe)
            raise eor__mziqe
        bmmy__ifsc.bcast(category_info)
    else:
        category_info = bmmy__ifsc.bcast(None)
        if isinstance(category_info, Exception):
            emltn__imsl = category_info
            raise emltn__imsl
    pq_dataset._category_info = category_info


def get_pandas_metadata(schema, num_pieces):
    hrfy__cnras = None
    nullable_from_metadata = defaultdict(lambda : None)
    zav__hpt = b'pandas'
    if schema.metadata is not None and zav__hpt in schema.metadata:
        import json
        smjvy__tvm = json.loads(schema.metadata[zav__hpt].decode('utf8'))
        dhtk__uhrhf = len(smjvy__tvm['index_columns'])
        if dhtk__uhrhf > 1:
            raise BodoError('read_parquet: MultiIndex not supported yet')
        hrfy__cnras = smjvy__tvm['index_columns'][0] if dhtk__uhrhf else None
        if not isinstance(hrfy__cnras, str) and (not isinstance(hrfy__cnras,
            dict) or num_pieces != 1):
            hrfy__cnras = None
        for mhqub__fzuu in smjvy__tvm['columns']:
            hhxyw__lqrxz = mhqub__fzuu['name']
            if mhqub__fzuu['pandas_type'].startswith('int'
                ) and hhxyw__lqrxz is not None:
                if mhqub__fzuu['numpy_type'].startswith('Int'):
                    nullable_from_metadata[hhxyw__lqrxz] = True
                else:
                    nullable_from_metadata[hhxyw__lqrxz] = False
    return hrfy__cnras, nullable_from_metadata


def parquet_file_schema(file_name, selected_columns, storage_options=None):
    col_names = []
    rmd__isf = []
    pq_dataset = get_parquet_dataset(file_name, get_row_counts=False,
        storage_options=storage_options, read_categories=True)
    partition_names = [] if pq_dataset.partitions is None else [pq_dataset.
        partitions.levels[gdmse__cdjb].name for gdmse__cdjb in range(len(
        pq_dataset.partitions.partition_names))]
    ufhgi__ljeoa = pq_dataset.schema.to_arrow_schema()
    num_pieces = len(pq_dataset.pieces)
    col_names = ufhgi__ljeoa.names
    hrfy__cnras, nullable_from_metadata = get_pandas_metadata(ufhgi__ljeoa,
        num_pieces)
    hgcrd__bspc = [_get_numba_typ_from_pa_typ(ufhgi__ljeoa.field(c), c ==
        hrfy__cnras, nullable_from_metadata[c], pq_dataset._category_info) for
        c in col_names]
    if partition_names:
        col_names += partition_names
        hgcrd__bspc += [_get_partition_cat_dtype(pq_dataset.partitions.
            levels[gdmse__cdjb]) for gdmse__cdjb in range(len(partition_names))
            ]
    yaw__lskq = {c: gdmse__cdjb for gdmse__cdjb, c in enumerate(col_names)}
    if selected_columns is None:
        selected_columns = col_names
    for c in selected_columns:
        if c not in yaw__lskq:
            raise BodoError(f'Selected column {c} not in Parquet file schema')
    if hrfy__cnras and not isinstance(hrfy__cnras, dict
        ) and hrfy__cnras not in selected_columns:
        selected_columns.append(hrfy__cnras)
    col_indices = [yaw__lskq[c] for c in selected_columns]
    rmd__isf = [hgcrd__bspc[yaw__lskq[c]] for c in selected_columns]
    col_names = selected_columns
    return col_names, rmd__isf, hrfy__cnras, col_indices, partition_names


def _get_partition_cat_dtype(part_set):
    bnc__ycfbp = part_set.dictionary.to_pandas()
    bif__wevqb = bodo.typeof(bnc__ycfbp).dtype
    nhpj__ynsep = PDCategoricalDtype(tuple(bnc__ycfbp), bif__wevqb, False)
    return CategoricalArrayType(nhpj__ynsep)


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
        ukelr__blda = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(32), lir.IntType(32),
            lir.IntType(32), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer()])
        dlb__vqqlz = cgutils.get_or_insert_function(builder.module,
            ukelr__blda, name='pq_write')
        builder.call(dlb__vqqlz, args)
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
        ukelr__blda = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(8).as_pointer(), lir.IntType(1), lir.IntType(8).
            as_pointer()])
        dlb__vqqlz = cgutils.get_or_insert_function(builder.module,
            ukelr__blda, name='pq_write_partitioned')
        builder.call(dlb__vqqlz, args)
        bodo.utils.utils.inlined_check_and_propagate_cpp_exception(context,
            builder)
    return types.void(types.voidptr, data_table_t, col_names_t,
        col_names_no_partitions_t, cat_table_t, types.voidptr, types.int32,
        types.voidptr, types.boolean, types.voidptr), codegen
