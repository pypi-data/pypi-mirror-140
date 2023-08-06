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
    mbz__uic = typemap[node.file_name.name]
    if types.unliteral(mbz__uic) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {mbz__uic}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        jdt__grcc = typemap[node.skiprows.name]
        if isinstance(jdt__grcc, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(jdt__grcc, types.Integer) and not (isinstance(
            jdt__grcc, (types.List, types.Tuple)) and isinstance(jdt__grcc.
            dtype, types.Integer)) and not isinstance(jdt__grcc, (types.
            LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {jdt__grcc}."
                , loc=node.skiprows.loc)
        elif isinstance(jdt__grcc, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        ysw__yje = typemap[node.nrows.name]
        if not isinstance(ysw__yje, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {ysw__yje}."
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
        clqbp__hlxz = csv_node.out_vars[0]
        if clqbp__hlxz.name not in lives:
            return None
    else:
        zth__srpo = csv_node.out_vars[0]
        tbj__jtcfl = csv_node.out_vars[1]
        if zth__srpo.name not in lives and tbj__jtcfl.name not in lives:
            return None
        elif tbj__jtcfl.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif zth__srpo.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.type_usecol_offset = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    jdt__grcc = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        if array_dists is not None:
            gcz__yqet = csv_node.out_vars[0].name
            parallel = array_dists[gcz__yqet] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        kncdf__gveq = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        kncdf__gveq += (
            f'    reader = _csv_reader_init(fname, nrows, skiprows)\n')
        kncdf__gveq += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        jqr__nuhfq = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(kncdf__gveq, {}, jqr__nuhfq)
        dhe__trzc = jqr__nuhfq['csv_iterator_impl']
        dxl__wqqe = 'def csv_reader_init(fname, nrows, skiprows):\n'
        dxl__wqqe += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory)
        dxl__wqqe += '  return f_reader\n'
        exec(dxl__wqqe, globals(), jqr__nuhfq)
        ewtp__qnhbe = jqr__nuhfq['csv_reader_init']
        pat__exfq = numba.njit(ewtp__qnhbe)
        compiled_funcs.append(pat__exfq)
        coua__yxq = compile_to_numba_ir(dhe__trzc, {'_csv_reader_init':
            pat__exfq, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, jdt__grcc), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(coua__yxq, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        qacdl__tcn = coua__yxq.body[:-3]
        qacdl__tcn[-1].target = csv_node.out_vars[0]
        return qacdl__tcn
    if array_dists is not None:
        fsfm__tfk = csv_node.out_vars[0].name
        parallel = array_dists[fsfm__tfk] in (distributed_pass.Distribution
            .OneD, distributed_pass.Distribution.OneD_Var)
        rcxs__qiw = csv_node.out_vars[1].name
        assert typemap[rcxs__qiw] == types.none or not parallel or array_dists[
            rcxs__qiw] in (distributed_pass.Distribution.OneD,
            distributed_pass.Distribution.OneD_Var
            ), 'pq data/index parallelization does not match'
    kncdf__gveq = 'def csv_impl(fname, nrows, skiprows):\n'
    kncdf__gveq += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    jqr__nuhfq = {}
    exec(kncdf__gveq, {}, jqr__nuhfq)
    vlq__jmkqp = jqr__nuhfq['csv_impl']
    oqf__qbp = csv_node.usecols
    if oqf__qbp:
        oqf__qbp = [csv_node.usecols[mfu__covlf] for mfu__covlf in csv_node
            .type_usecol_offset]
    cjkd__lpe = _gen_csv_reader_py(csv_node.df_colnames, csv_node.out_types,
        oqf__qbp, csv_node.type_usecol_offset, csv_node.sep, parallel,
        csv_node.header, csv_node.compression, csv_node.is_skiprows_list,
        csv_node.pd_low_memory, csv_node.escapechar, idx_col_index=csv_node
        .index_column_index, idx_col_typ=csv_node.index_column_typ)
    coua__yxq = compile_to_numba_ir(vlq__jmkqp, {'_csv_reader_py':
        cjkd__lpe}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, jdt__grcc), typemap=typemap, calltypes=
        calltypes).blocks.popitem()[1]
    replace_arg_nodes(coua__yxq, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    qacdl__tcn = coua__yxq.body[:-3]
    qacdl__tcn[-1].target = csv_node.out_vars[1]
    qacdl__tcn[-2].target = csv_node.out_vars[0]
    if csv_node.index_column_index is None:
        qacdl__tcn.pop(-1)
    elif not oqf__qbp:
        qacdl__tcn.pop(-2)
    return qacdl__tcn


def csv_remove_dead_column(csv_node, column_live_map, equiv_vars, typemap):
    if csv_node.chunksize is not None:
        return False
    assert len(csv_node.out_vars) == 2, 'invalid CsvReader node'
    scs__ngt = csv_node.out_vars[0].name
    if isinstance(typemap[scs__ngt], TableType) and csv_node.usecols:
        neggc__ufl, rnl__fcjk = get_live_column_nums_block(column_live_map,
            equiv_vars, scs__ngt)
        neggc__ufl = bodo.ir.connector.trim_extra_used_columns(neggc__ufl,
            len(csv_node.usecols))
        if not rnl__fcjk and not neggc__ufl:
            neggc__ufl = [0]
        if not rnl__fcjk and len(neggc__ufl) != len(csv_node.type_usecol_offset
            ):
            csv_node.type_usecol_offset = neggc__ufl
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
    bbe__gjqt = t.dtype
    if isinstance(bbe__gjqt, PDCategoricalDtype):
        expr__moo = CategoricalArrayType(bbe__gjqt)
        cudtp__fxet = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, cudtp__fxet, expr__moo)
        return cudtp__fxet
    if bbe__gjqt == types.NPDatetime('ns'):
        bbe__gjqt = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        nnc__sukv = 'int_arr_{}'.format(bbe__gjqt)
        setattr(types, nnc__sukv, t)
        return nnc__sukv
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if bbe__gjqt == types.bool_:
        bbe__gjqt = 'bool_'
    if bbe__gjqt == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(bbe__gjqt, (
        StringArrayType, ArrayItemArrayType)):
        uvfqj__uvuk = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, uvfqj__uvuk, t)
        return uvfqj__uvuk
    return '{}[::1]'.format(bbe__gjqt)


def _get_pd_dtype_str(t):
    bbe__gjqt = t.dtype
    if isinstance(bbe__gjqt, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(bbe__gjqt.categories)
    if bbe__gjqt == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if bbe__gjqt.signed else 'U',
            bbe__gjqt.bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(bbe__gjqt, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(bbe__gjqt)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    nbx__uiek = ''
    from collections import defaultdict
    czavn__tvozx = defaultdict(list)
    for muuo__aoy, fzsqu__ygpra in typemap.items():
        czavn__tvozx[fzsqu__ygpra].append(muuo__aoy)
    kkjs__gdzex = df.columns.to_list()
    joeey__gca = []
    for fzsqu__ygpra, ciupb__vtt in czavn__tvozx.items():
        try:
            joeey__gca.append(df.loc[:, ciupb__vtt].astype(fzsqu__ygpra,
                copy=False))
            df = df.drop(ciupb__vtt, axis=1)
        except (ValueError, TypeError) as xqd__vfch:
            nbx__uiek = (
                f"Caught the runtime error '{xqd__vfch}' on columns {ciupb__vtt}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    nqyb__tefl = bool(nbx__uiek)
    if parallel:
        rhe__swczh = MPI.COMM_WORLD
        nqyb__tefl = rhe__swczh.allreduce(nqyb__tefl, op=MPI.LOR)
    if nqyb__tefl:
        lqo__rcp = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if nbx__uiek:
            raise TypeError(f'{lqo__rcp}\n{nbx__uiek}')
        else:
            raise TypeError(
                f'{lqo__rcp}\nPlease refer to errors on other ranks.')
    df = pd.concat(joeey__gca + [df], axis=1)
    dcgyg__bscsk = df.loc[:, kkjs__gdzex]
    return dcgyg__bscsk


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory):
    htm__rekwl = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        kncdf__gveq = '  skiprows = sorted(set(skiprows))\n'
    else:
        kncdf__gveq = '  skiprows = [skiprows]\n'
    kncdf__gveq += '  skiprows_list_len = len(skiprows)\n'
    kncdf__gveq += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    kncdf__gveq += '  check_java_installation(fname)\n'
    kncdf__gveq += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    kncdf__gveq += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    kncdf__gveq += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), {}, {}, skiprows_list_len, {})
"""
        .format(parallel, htm__rekwl, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    kncdf__gveq += '  bodo.utils.utils.check_and_propagate_cpp_exception()\n'
    kncdf__gveq += '  if bodo.utils.utils.is_null_pointer(f_reader):\n'
    kncdf__gveq += "      raise FileNotFoundError('File does not exist')\n"
    return kncdf__gveq


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    type_usecol_offset, sep, escapechar, call_id, glbs, parallel,
    check_parallel_runtime, idx_col_index, idx_col_typ):
    slr__nnbr = [str(eibf__opttz) for mfu__covlf, eibf__opttz in enumerate(
        usecols) if col_typs[type_usecol_offset[mfu__covlf]].dtype == types
        .NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        slr__nnbr.append(str(idx_col_index))
    zcw__anpr = ', '.join(slr__nnbr)
    xjqb__vlzar = _gen_parallel_flag_name(sanitized_cnames)
    yiehk__lqu = f"{xjqb__vlzar}='bool_'" if check_parallel_runtime else ''
    blf__ntcd = [_get_pd_dtype_str(col_typs[type_usecol_offset[mfu__covlf]]
        ) for mfu__covlf in range(len(usecols))]
    rlgn__ezt = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    drp__wea = [eibf__opttz for mfu__covlf, eibf__opttz in enumerate(
        usecols) if blf__ntcd[mfu__covlf] == 'str']
    if idx_col_index is not None and rlgn__ezt == 'str':
        drp__wea.append(idx_col_index)
    nwuxp__qbbh = np.array(drp__wea, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = nwuxp__qbbh
    kncdf__gveq = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    tca__goq = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []))
    glbs[f'usecols_arr_{call_id}'] = tca__goq
    kncdf__gveq += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    nhtqe__nygj = np.array(type_usecol_offset, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = nhtqe__nygj
        kncdf__gveq += f"""  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}
"""
    kmvyd__php = defaultdict(list)
    for mfu__covlf, eibf__opttz in enumerate(usecols):
        if blf__ntcd[mfu__covlf] == 'str':
            continue
        kmvyd__php[blf__ntcd[mfu__covlf]].append(eibf__opttz)
    if idx_col_index is not None and rlgn__ezt != 'str':
        kmvyd__php[rlgn__ezt].append(idx_col_index)
    for mfu__covlf, chwv__lbs in enumerate(kmvyd__php.values()):
        glbs[f't_arr_{mfu__covlf}_{call_id}'] = np.asarray(chwv__lbs)
        kncdf__gveq += (
            f'  t_arr_{mfu__covlf}_{call_id}_2 = t_arr_{mfu__covlf}_{call_id}\n'
            )
    if idx_col_index != None:
        kncdf__gveq += f"""  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {yiehk__lqu}):
"""
    else:
        kncdf__gveq += (
            f'  with objmode(T=table_type_{call_id}, {yiehk__lqu}):\n')
    kncdf__gveq += f'    typemap = {{}}\n'
    for mfu__covlf, nubpd__fvb in enumerate(kmvyd__php.keys()):
        kncdf__gveq += f"""    typemap.update({{i:{nubpd__fvb} for i in t_arr_{mfu__covlf}_{call_id}_2}})
"""
    kncdf__gveq += '    if f_reader.get_chunk_size() == 0:\n'
    kncdf__gveq += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    kncdf__gveq += '    else:\n'
    kncdf__gveq += '      df = pd.read_csv(f_reader,\n'
    kncdf__gveq += '        header=None,\n'
    kncdf__gveq += '        parse_dates=[{}],\n'.format(zcw__anpr)
    kncdf__gveq += (
        f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n')
    kncdf__gveq += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        kncdf__gveq += f'    {xjqb__vlzar} = f_reader.is_parallel()\n'
    else:
        kncdf__gveq += f'    {xjqb__vlzar} = {parallel}\n'
    kncdf__gveq += f'    df = astype(df, typemap, {xjqb__vlzar})\n'
    if idx_col_index != None:
        ebg__ulvbv = sorted(tca__goq).index(idx_col_index)
        kncdf__gveq += f'    idx_arr = df.iloc[:, {ebg__ulvbv}].values\n'
        kncdf__gveq += (
            f'    df.drop(columns=df.columns[{ebg__ulvbv}], inplace=True)\n')
    if len(usecols) == 0:
        kncdf__gveq += f'    T = None\n'
    else:
        kncdf__gveq += f'    arrs = []\n'
        kncdf__gveq += f'    for i in range(df.shape[1]):\n'
        kncdf__gveq += f'      arrs.append(df.iloc[:, i].values)\n'
        kncdf__gveq += f"""    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})
"""
    return kncdf__gveq


def _gen_parallel_flag_name(sanitized_cnames):
    xjqb__vlzar = '_parallel_value'
    while xjqb__vlzar in sanitized_cnames:
        xjqb__vlzar = '_' + xjqb__vlzar
    return xjqb__vlzar


def _gen_csv_reader_py(col_names, col_typs, usecols, type_usecol_offset,
    sep, parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(dvwm__hyonc) for dvwm__hyonc in
        col_names]
    kncdf__gveq = 'def csv_reader_py(fname, nrows, skiprows):\n'
    kncdf__gveq += _gen_csv_file_reader_init(parallel, header, compression,
        -1, is_skiprows_list, pd_low_memory)
    call_id = ir_utils.next_label()
    yxfx__gceki = globals()
    if idx_col_typ != types.none:
        yxfx__gceki[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        yxfx__gceki[f'table_type_{call_id}'] = types.none
    else:
        yxfx__gceki[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    kncdf__gveq += _gen_read_csv_objmode(col_names, sanitized_cnames,
        col_typs, usecols, type_usecol_offset, sep, escapechar, call_id,
        yxfx__gceki, parallel=parallel, check_parallel_runtime=False,
        idx_col_index=idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        kncdf__gveq += '  return (T, idx_arr)\n'
    else:
        kncdf__gveq += '  return (T, None)\n'
    jqr__nuhfq = {}
    exec(kncdf__gveq, yxfx__gceki, jqr__nuhfq)
    cjkd__lpe = jqr__nuhfq['csv_reader_py']
    pat__exfq = numba.njit(cjkd__lpe)
    compiled_funcs.append(pat__exfq)
    return pat__exfq
