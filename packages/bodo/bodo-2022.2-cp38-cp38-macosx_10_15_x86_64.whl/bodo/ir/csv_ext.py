from collections import defaultdict
import numba
import numpy as np
import pandas as pd
from mpi4py import MPI
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, PDCategoricalDtype
from bodo.hiframes.table import Table, TableType
from bodo.libs.array_item_arr_ext import ArrayItemArrayType
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.str_arr_ext import StringArrayType, string_array_type
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.transforms.table_column_del_pass import get_live_column_nums_block, ir_extension_table_column_use, remove_dead_column_extensions
from bodo.utils.typing import BodoError
from bodo.utils.utils import check_java_installation
from bodo.utils.utils import sanitize_varname


class CsvReader(ir.Stmt):

    def __init__(self, file_name, df_out, sep, df_colnames, out_vars,
        out_types, usecols, loc, header, compression, nrows, skiprows,
        chunksize, is_skiprows_list, low_memory, escapechar,
        index_column_index=None, index_column_typ=types.none):
        self.connector_typ = 'csv'
        self.file_name = file_name
        self.df_out = df_out
        self.sep = sep
        self.df_colnames = df_colnames
        self.out_vars = out_vars
        self.out_types = out_types
        self.usecols = usecols
        self.loc = loc
        self.skiprows = skiprows
        self.nrows = nrows
        self.header = header
        self.compression = compression
        self.chunksize = chunksize
        self.is_skiprows_list = is_skiprows_list
        self.pd_low_memory = low_memory
        self.escapechar = escapechar
        self.index_column_index = index_column_index
        self.index_column_typ = index_column_typ
        self.type_usecol_offset = list(range(len(usecols)))

    def __repr__(self):
        return (
            '{} = ReadCsv(file={}, col_names={}, types={}, vars={}, nrows={}, skiprows={}, chunksize={}, is_skiprows_list={}, pd_low_memory={}, index_column_index={}, index_colum_typ = {}, type_usecol_offsets={})'
            .format(self.df_out, self.file_name, self.df_colnames, self.
            out_types, self.out_vars, self.nrows, self.skiprows, self.
            chunksize, self.is_skiprows_list, self.pd_low_memory, self.
            index_column_index, self.index_column_typ, self.type_usecol_offset)
            )


def check_node_typing(node, typemap):
    ouynq__zfm = typemap[node.file_name.name]
    if types.unliteral(ouynq__zfm) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {ouynq__zfm}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        rifvu__irdxw = typemap[node.skiprows.name]
        if isinstance(rifvu__irdxw, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(rifvu__irdxw, types.Integer) and not (isinstance
            (rifvu__irdxw, (types.List, types.Tuple)) and isinstance(
            rifvu__irdxw.dtype, types.Integer)) and not isinstance(rifvu__irdxw
            , (types.LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {rifvu__irdxw}."
                , loc=node.skiprows.loc)
        elif isinstance(rifvu__irdxw, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        wwxyu__pdkvi = typemap[node.nrows.name]
        if not isinstance(wwxyu__pdkvi, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {wwxyu__pdkvi}."
                , loc=node.nrows.loc)


import llvmlite.binding as ll
from bodo.io import csv_cpp
ll.add_symbol('csv_file_chunk_reader', csv_cpp.csv_file_chunk_reader)
csv_file_chunk_reader = types.ExternalFunction('csv_file_chunk_reader',
    bodo.ir.connector.stream_reader_type(types.voidptr, types.bool_, types.
    voidptr, types.int64, types.bool_, types.voidptr, types.voidptr, types.
    int64, types.bool_, types.int64, types.bool_))


def remove_dead_csv(csv_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    if csv_node.chunksize is not None:
        ldlme__fyoep = csv_node.out_vars[0]
        if ldlme__fyoep.name not in lives:
            return None
    else:
        zdcr__ubjjr = csv_node.out_vars[0]
        cqh__frpvj = csv_node.out_vars[1]
        if zdcr__ubjjr.name not in lives and cqh__frpvj.name not in lives:
            return None
        elif cqh__frpvj.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif zdcr__ubjjr.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.type_usecol_offset = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    rifvu__irdxw = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        if array_dists is not None:
            mif__pzgk = csv_node.out_vars[0].name
            parallel = array_dists[mif__pzgk] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        yhl__yje = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        yhl__yje += f'    reader = _csv_reader_init(fname, nrows, skiprows)\n'
        yhl__yje += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        nxru__jraa = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(yhl__yje, {}, nxru__jraa)
        vyh__qhlz = nxru__jraa['csv_iterator_impl']
        rui__mykv = 'def csv_reader_init(fname, nrows, skiprows):\n'
        rui__mykv += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory)
        rui__mykv += '  return f_reader\n'
        exec(rui__mykv, globals(), nxru__jraa)
        fgzz__nzro = nxru__jraa['csv_reader_init']
        wmp__ocv = numba.njit(fgzz__nzro)
        compiled_funcs.append(wmp__ocv)
        aqzbh__almuc = compile_to_numba_ir(vyh__qhlz, {'_csv_reader_init':
            wmp__ocv, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, rifvu__irdxw), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(aqzbh__almuc, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        ngii__cuisc = aqzbh__almuc.body[:-3]
        ngii__cuisc[-1].target = csv_node.out_vars[0]
        return ngii__cuisc
    if array_dists is not None:
        lhlo__vlg = csv_node.out_vars[0].name
        parallel = array_dists[lhlo__vlg] in (distributed_pass.Distribution
            .OneD, distributed_pass.Distribution.OneD_Var)
        ucwme__mxr = csv_node.out_vars[1].name
        assert typemap[ucwme__mxr
            ] == types.none or not parallel or array_dists[ucwme__mxr] in (
            distributed_pass.Distribution.OneD, distributed_pass.
            Distribution.OneD_Var
            ), 'pq data/index parallelization does not match'
    yhl__yje = 'def csv_impl(fname, nrows, skiprows):\n'
    yhl__yje += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    nxru__jraa = {}
    exec(yhl__yje, {}, nxru__jraa)
    zxi__qlzs = nxru__jraa['csv_impl']
    zgrsy__wwat = csv_node.usecols
    if zgrsy__wwat:
        zgrsy__wwat = [csv_node.usecols[zer__nzq] for zer__nzq in csv_node.
            type_usecol_offset]
    dttou__ugip = _gen_csv_reader_py(csv_node.df_colnames, csv_node.
        out_types, zgrsy__wwat, csv_node.type_usecol_offset, csv_node.sep,
        parallel, csv_node.header, csv_node.compression, csv_node.
        is_skiprows_list, csv_node.pd_low_memory, csv_node.escapechar,
        idx_col_index=csv_node.index_column_index, idx_col_typ=csv_node.
        index_column_typ)
    aqzbh__almuc = compile_to_numba_ir(zxi__qlzs, {'_csv_reader_py':
        dttou__ugip}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, rifvu__irdxw), typemap=typemap, calltypes
        =calltypes).blocks.popitem()[1]
    replace_arg_nodes(aqzbh__almuc, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    ngii__cuisc = aqzbh__almuc.body[:-3]
    ngii__cuisc[-1].target = csv_node.out_vars[1]
    ngii__cuisc[-2].target = csv_node.out_vars[0]
    if csv_node.index_column_index is None:
        ngii__cuisc.pop(-1)
    elif not zgrsy__wwat:
        ngii__cuisc.pop(-2)
    return ngii__cuisc


def csv_remove_dead_column(csv_node, column_live_map, equiv_vars, typemap):
    if csv_node.chunksize is not None:
        return False
    assert len(csv_node.out_vars) == 2, 'invalid CsvReader node'
    bmyk__xyk = csv_node.out_vars[0].name
    if isinstance(typemap[bmyk__xyk], TableType) and csv_node.usecols:
        exng__huam, cdn__mapbx = get_live_column_nums_block(column_live_map,
            equiv_vars, bmyk__xyk)
        exng__huam = bodo.ir.connector.trim_extra_used_columns(exng__huam,
            len(csv_node.usecols))
        if not cdn__mapbx and not exng__huam:
            exng__huam = [0]
        if not cdn__mapbx and len(exng__huam) != len(csv_node.
            type_usecol_offset):
            csv_node.type_usecol_offset = exng__huam
            return True
    return False


def csv_table_column_use(csv_node, block_use_map, equiv_vars, typemap):
    return


numba.parfors.array_analysis.array_analysis_extensions[CsvReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[CsvReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[CsvReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[CsvReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[CsvReader] = remove_dead_csv
numba.core.analysis.ir_extension_usedefs[CsvReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[CsvReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[CsvReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[CsvReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[CsvReader] = csv_distributed_run
remove_dead_column_extensions[CsvReader] = csv_remove_dead_column
ir_extension_table_column_use[CsvReader] = csv_table_column_use


def _get_dtype_str(t):
    ryzgw__svve = t.dtype
    if isinstance(ryzgw__svve, PDCategoricalDtype):
        wzz__fxh = CategoricalArrayType(ryzgw__svve)
        ytr__nlg = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, ytr__nlg, wzz__fxh)
        return ytr__nlg
    if ryzgw__svve == types.NPDatetime('ns'):
        ryzgw__svve = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        nli__pjf = 'int_arr_{}'.format(ryzgw__svve)
        setattr(types, nli__pjf, t)
        return nli__pjf
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if ryzgw__svve == types.bool_:
        ryzgw__svve = 'bool_'
    if ryzgw__svve == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(ryzgw__svve, (
        StringArrayType, ArrayItemArrayType)):
        ytdgd__wves = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, ytdgd__wves, t)
        return ytdgd__wves
    return '{}[::1]'.format(ryzgw__svve)


def _get_pd_dtype_str(t):
    ryzgw__svve = t.dtype
    if isinstance(ryzgw__svve, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(ryzgw__svve.categories)
    if ryzgw__svve == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if ryzgw__svve.signed else 'U',
            ryzgw__svve.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(ryzgw__svve, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(ryzgw__svve)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    gvmw__ftlsk = ''
    from collections import defaultdict
    zdowq__uwmda = defaultdict(list)
    for jspfs__ssgye, vzc__zwdf in typemap.items():
        zdowq__uwmda[vzc__zwdf].append(jspfs__ssgye)
    hng__zzqd = df.columns.to_list()
    yktto__ijp = []
    for vzc__zwdf, pyfcx__umhy in zdowq__uwmda.items():
        try:
            yktto__ijp.append(df.loc[:, pyfcx__umhy].astype(vzc__zwdf, copy
                =False))
            df = df.drop(pyfcx__umhy, axis=1)
        except (ValueError, TypeError) as zdyj__dzu:
            gvmw__ftlsk = (
                f"Caught the runtime error '{zdyj__dzu}' on columns {pyfcx__umhy}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    nafkj__nri = bool(gvmw__ftlsk)
    if parallel:
        xzo__dvw = MPI.COMM_WORLD
        nafkj__nri = xzo__dvw.allreduce(nafkj__nri, op=MPI.LOR)
    if nafkj__nri:
        fei__hyyv = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if gvmw__ftlsk:
            raise TypeError(f'{fei__hyyv}\n{gvmw__ftlsk}')
        else:
            raise TypeError(
                f'{fei__hyyv}\nPlease refer to errors on other ranks.')
    df = pd.concat(yktto__ijp + [df], axis=1)
    kdwig__ucygw = df.loc[:, hng__zzqd]
    return kdwig__ucygw


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory):
    uox__mgg = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        yhl__yje = '  skiprows = sorted(set(skiprows))\n'
    else:
        yhl__yje = '  skiprows = [skiprows]\n'
    yhl__yje += '  skiprows_list_len = len(skiprows)\n'
    yhl__yje += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    yhl__yje += '  check_java_installation(fname)\n'
    yhl__yje += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    yhl__yje += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    yhl__yje += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), {}, {}, skiprows_list_len, {})
"""
        .format(parallel, uox__mgg, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    yhl__yje += '  bodo.utils.utils.check_and_propagate_cpp_exception()\n'
    yhl__yje += '  if bodo.utils.utils.is_null_pointer(f_reader):\n'
    yhl__yje += "      raise FileNotFoundError('File does not exist')\n"
    return yhl__yje


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    type_usecol_offset, sep, escapechar, call_id, glbs, parallel,
    check_parallel_runtime, idx_col_index, idx_col_typ):
    ywqe__ewpxp = [str(lmog__xsbj) for zer__nzq, lmog__xsbj in enumerate(
        usecols) if col_typs[type_usecol_offset[zer__nzq]].dtype == types.
        NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        ywqe__ewpxp.append(str(idx_col_index))
    viqwe__oev = ', '.join(ywqe__ewpxp)
    jhqjl__vdp = _gen_parallel_flag_name(sanitized_cnames)
    bpcam__ncvx = f"{jhqjl__vdp}='bool_'" if check_parallel_runtime else ''
    ntc__lzgi = [_get_pd_dtype_str(col_typs[type_usecol_offset[zer__nzq]]) for
        zer__nzq in range(len(usecols))]
    zbsqw__sehab = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    thizd__lmrw = [lmog__xsbj for zer__nzq, lmog__xsbj in enumerate(usecols
        ) if ntc__lzgi[zer__nzq] == 'str']
    if idx_col_index is not None and zbsqw__sehab == 'str':
        thizd__lmrw.append(idx_col_index)
    ojfb__bglb = np.array(thizd__lmrw, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = ojfb__bglb
    yhl__yje = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    qlp__xqlew = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []))
    glbs[f'usecols_arr_{call_id}'] = qlp__xqlew
    yhl__yje += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    cqih__ezoo = np.array(type_usecol_offset, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = cqih__ezoo
        yhl__yje += (
            f'  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}\n'
            )
    xvoc__jkx = defaultdict(list)
    for zer__nzq, lmog__xsbj in enumerate(usecols):
        if ntc__lzgi[zer__nzq] == 'str':
            continue
        xvoc__jkx[ntc__lzgi[zer__nzq]].append(lmog__xsbj)
    if idx_col_index is not None and zbsqw__sehab != 'str':
        xvoc__jkx[zbsqw__sehab].append(idx_col_index)
    for zer__nzq, pbfg__bxw in enumerate(xvoc__jkx.values()):
        glbs[f't_arr_{zer__nzq}_{call_id}'] = np.asarray(pbfg__bxw)
        yhl__yje += (
            f'  t_arr_{zer__nzq}_{call_id}_2 = t_arr_{zer__nzq}_{call_id}\n')
    if idx_col_index != None:
        yhl__yje += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {bpcam__ncvx}):
"""
    else:
        yhl__yje += f'  with objmode(T=table_type_{call_id}, {bpcam__ncvx}):\n'
    yhl__yje += f'    typemap = {{}}\n'
    for zer__nzq, qbcqm__kzkro in enumerate(xvoc__jkx.keys()):
        yhl__yje += f"""    typemap.update({{i:{qbcqm__kzkro} for i in t_arr_{zer__nzq}_{call_id}_2}})
"""
    yhl__yje += '    if f_reader.get_chunk_size() == 0:\n'
    yhl__yje += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    yhl__yje += '    else:\n'
    yhl__yje += '      df = pd.read_csv(f_reader,\n'
    yhl__yje += '        header=None,\n'
    yhl__yje += '        parse_dates=[{}],\n'.format(viqwe__oev)
    yhl__yje += f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n'
    yhl__yje += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        yhl__yje += f'    {jhqjl__vdp} = f_reader.is_parallel()\n'
    else:
        yhl__yje += f'    {jhqjl__vdp} = {parallel}\n'
    yhl__yje += f'    df = astype(df, typemap, {jhqjl__vdp})\n'
    if idx_col_index != None:
        zckd__kat = sorted(qlp__xqlew).index(idx_col_index)
        yhl__yje += f'    idx_arr = df.iloc[:, {zckd__kat}].values\n'
        yhl__yje += (
            f'    df.drop(columns=df.columns[{zckd__kat}], inplace=True)\n')
    if len(usecols) == 0:
        yhl__yje += f'    T = None\n'
    else:
        yhl__yje += f'    arrs = []\n'
        yhl__yje += f'    for i in range(df.shape[1]):\n'
        yhl__yje += f'      arrs.append(df.iloc[:, i].values)\n'
        yhl__yje += (
            f'    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})\n'
            )
    return yhl__yje


def _gen_parallel_flag_name(sanitized_cnames):
    jhqjl__vdp = '_parallel_value'
    while jhqjl__vdp in sanitized_cnames:
        jhqjl__vdp = '_' + jhqjl__vdp
    return jhqjl__vdp


def _gen_csv_reader_py(col_names, col_typs, usecols, type_usecol_offset,
    sep, parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(aleb__zblpc) for aleb__zblpc in
        col_names]
    yhl__yje = 'def csv_reader_py(fname, nrows, skiprows):\n'
    yhl__yje += _gen_csv_file_reader_init(parallel, header, compression, -1,
        is_skiprows_list, pd_low_memory)
    call_id = ir_utils.next_label()
    lgss__ivjm = globals()
    if idx_col_typ != types.none:
        lgss__ivjm[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        lgss__ivjm[f'table_type_{call_id}'] = types.none
    else:
        lgss__ivjm[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    yhl__yje += _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs,
        usecols, type_usecol_offset, sep, escapechar, call_id, lgss__ivjm,
        parallel=parallel, check_parallel_runtime=False, idx_col_index=
        idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        yhl__yje += '  return (T, idx_arr)\n'
    else:
        yhl__yje += '  return (T, None)\n'
    nxru__jraa = {}
    exec(yhl__yje, lgss__ivjm, nxru__jraa)
    dttou__ugip = nxru__jraa['csv_reader_py']
    wmp__ocv = numba.njit(dttou__ugip)
    compiled_funcs.append(wmp__ocv)
    return wmp__ocv
