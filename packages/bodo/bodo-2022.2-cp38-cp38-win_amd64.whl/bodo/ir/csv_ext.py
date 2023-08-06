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
    zbtc__xjbj = typemap[node.file_name.name]
    if types.unliteral(zbtc__xjbj) != types.unicode_type:
        raise BodoError(
            f"pd.read_csv(): 'filepath_or_buffer' must be a string. Found type: {zbtc__xjbj}."
            , node.file_name.loc)
    if not isinstance(node.skiprows, ir.Const):
        kkvxy__ntbei = typemap[node.skiprows.name]
        if isinstance(kkvxy__ntbei, types.Dispatcher):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' callable not supported yet.",
                node.file_name.loc)
        elif not isinstance(kkvxy__ntbei, types.Integer) and not (isinstance
            (kkvxy__ntbei, (types.List, types.Tuple)) and isinstance(
            kkvxy__ntbei.dtype, types.Integer)) and not isinstance(kkvxy__ntbei
            , (types.LiteralList, bodo.utils.typing.ListLiteral)):
            raise BodoError(
                f"pd.read_csv(): 'skiprows' must be an integer or list of integers. Found type {kkvxy__ntbei}."
                , loc=node.skiprows.loc)
        elif isinstance(kkvxy__ntbei, (types.List, types.Tuple)):
            node.is_skiprows_list = True
    if not isinstance(node.nrows, ir.Const):
        vyi__iaeu = typemap[node.nrows.name]
        if not isinstance(vyi__iaeu, types.Integer):
            raise BodoError(
                f"pd.read_csv(): 'nrows' must be an integer. Found type {vyi__iaeu}."
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
        acq__thw = csv_node.out_vars[0]
        if acq__thw.name not in lives:
            return None
    else:
        dsoo__qiqzb = csv_node.out_vars[0]
        slx__rtap = csv_node.out_vars[1]
        if dsoo__qiqzb.name not in lives and slx__rtap.name not in lives:
            return None
        elif slx__rtap.name not in lives:
            csv_node.index_column_index = None
            csv_node.index_column_typ = types.none
        elif dsoo__qiqzb.name not in lives:
            csv_node.usecols = []
            csv_node.out_types = []
            csv_node.type_usecol_offset = []
    return csv_node


def csv_distributed_run(csv_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    kkvxy__ntbei = types.int64 if isinstance(csv_node.skiprows, ir.Const
        ) else types.unliteral(typemap[csv_node.skiprows.name])
    if csv_node.chunksize is not None:
        if array_dists is not None:
            pyr__pyut = csv_node.out_vars[0].name
            parallel = array_dists[pyr__pyut] in (distributed_pass.
                Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        reo__tgg = 'def csv_iterator_impl(fname, nrows, skiprows):\n'
        reo__tgg += f'    reader = _csv_reader_init(fname, nrows, skiprows)\n'
        reo__tgg += (
            f'    iterator = init_csv_iterator(reader, csv_iterator_type)\n')
        wfyy__seh = {}
        from bodo.io.csv_iterator_ext import init_csv_iterator
        exec(reo__tgg, {}, wfyy__seh)
        nshsm__cdhmq = wfyy__seh['csv_iterator_impl']
        lfrvc__jlc = 'def csv_reader_init(fname, nrows, skiprows):\n'
        lfrvc__jlc += _gen_csv_file_reader_init(parallel, csv_node.header,
            csv_node.compression, csv_node.chunksize, csv_node.
            is_skiprows_list, csv_node.pd_low_memory)
        lfrvc__jlc += '  return f_reader\n'
        exec(lfrvc__jlc, globals(), wfyy__seh)
        fgbp__ctl = wfyy__seh['csv_reader_init']
        vmrnx__vqau = numba.njit(fgbp__ctl)
        compiled_funcs.append(vmrnx__vqau)
        imfd__wek = compile_to_numba_ir(nshsm__cdhmq, {'_csv_reader_init':
            vmrnx__vqau, 'init_csv_iterator': init_csv_iterator,
            'csv_iterator_type': typemap[csv_node.out_vars[0].name]},
            typingctx=typingctx, targetctx=targetctx, arg_typs=(string_type,
            types.int64, kkvxy__ntbei), typemap=typemap, calltypes=calltypes
            ).blocks.popitem()[1]
        replace_arg_nodes(imfd__wek, [csv_node.file_name, csv_node.nrows,
            csv_node.skiprows])
        yzvtv__kyv = imfd__wek.body[:-3]
        yzvtv__kyv[-1].target = csv_node.out_vars[0]
        return yzvtv__kyv
    if array_dists is not None:
        eehyd__jbhy = csv_node.out_vars[0].name
        parallel = array_dists[eehyd__jbhy] in (distributed_pass.
            Distribution.OneD, distributed_pass.Distribution.OneD_Var)
        yuzya__ktjy = csv_node.out_vars[1].name
        assert typemap[yuzya__ktjy
            ] == types.none or not parallel or array_dists[yuzya__ktjy] in (
            distributed_pass.Distribution.OneD, distributed_pass.
            Distribution.OneD_Var
            ), 'pq data/index parallelization does not match'
    reo__tgg = 'def csv_impl(fname, nrows, skiprows):\n'
    reo__tgg += (
        f'    (table_val, idx_col) = _csv_reader_py(fname, nrows, skiprows)\n')
    wfyy__seh = {}
    exec(reo__tgg, {}, wfyy__seh)
    xgpfe__hoh = wfyy__seh['csv_impl']
    lkfve__xrdb = csv_node.usecols
    if lkfve__xrdb:
        lkfve__xrdb = [csv_node.usecols[wey__xgrfj] for wey__xgrfj in
            csv_node.type_usecol_offset]
    juv__ezsm = _gen_csv_reader_py(csv_node.df_colnames, csv_node.out_types,
        lkfve__xrdb, csv_node.type_usecol_offset, csv_node.sep, parallel,
        csv_node.header, csv_node.compression, csv_node.is_skiprows_list,
        csv_node.pd_low_memory, csv_node.escapechar, idx_col_index=csv_node
        .index_column_index, idx_col_typ=csv_node.index_column_typ)
    imfd__wek = compile_to_numba_ir(xgpfe__hoh, {'_csv_reader_py':
        juv__ezsm}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type, types.int64, kkvxy__ntbei), typemap=typemap, calltypes
        =calltypes).blocks.popitem()[1]
    replace_arg_nodes(imfd__wek, [csv_node.file_name, csv_node.nrows,
        csv_node.skiprows, csv_node.is_skiprows_list])
    yzvtv__kyv = imfd__wek.body[:-3]
    yzvtv__kyv[-1].target = csv_node.out_vars[1]
    yzvtv__kyv[-2].target = csv_node.out_vars[0]
    if csv_node.index_column_index is None:
        yzvtv__kyv.pop(-1)
    elif not lkfve__xrdb:
        yzvtv__kyv.pop(-2)
    return yzvtv__kyv


def csv_remove_dead_column(csv_node, column_live_map, equiv_vars, typemap):
    if csv_node.chunksize is not None:
        return False
    assert len(csv_node.out_vars) == 2, 'invalid CsvReader node'
    bkd__mwfwi = csv_node.out_vars[0].name
    if isinstance(typemap[bkd__mwfwi], TableType) and csv_node.usecols:
        lpyyn__djws, efge__ngy = get_live_column_nums_block(column_live_map,
            equiv_vars, bkd__mwfwi)
        lpyyn__djws = bodo.ir.connector.trim_extra_used_columns(lpyyn__djws,
            len(csv_node.usecols))
        if not efge__ngy and not lpyyn__djws:
            lpyyn__djws = [0]
        if not efge__ngy and len(lpyyn__djws) != len(csv_node.
            type_usecol_offset):
            csv_node.type_usecol_offset = lpyyn__djws
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
    iyc__dyf = t.dtype
    if isinstance(iyc__dyf, PDCategoricalDtype):
        vsh__pwxrk = CategoricalArrayType(iyc__dyf)
        yafv__pqvh = 'CategoricalArrayType' + str(ir_utils.next_label())
        setattr(types, yafv__pqvh, vsh__pwxrk)
        return yafv__pqvh
    if iyc__dyf == types.NPDatetime('ns'):
        iyc__dyf = 'NPDatetime("ns")'
    if t == string_array_type:
        types.string_array_type = string_array_type
        return 'string_array_type'
    if isinstance(t, IntegerArrayType):
        wgu__kuvm = 'int_arr_{}'.format(iyc__dyf)
        setattr(types, wgu__kuvm, t)
        return wgu__kuvm
    if t == boolean_array:
        types.boolean_array = boolean_array
        return 'boolean_array'
    if iyc__dyf == types.bool_:
        iyc__dyf = 'bool_'
    if iyc__dyf == datetime_date_type:
        return 'datetime_date_array_type'
    if isinstance(t, ArrayItemArrayType) and isinstance(iyc__dyf, (
        StringArrayType, ArrayItemArrayType)):
        zts__mrfd = f'ArrayItemArrayType{str(ir_utils.next_label())}'
        setattr(types, zts__mrfd, t)
        return zts__mrfd
    return '{}[::1]'.format(iyc__dyf)


def _get_pd_dtype_str(t):
    iyc__dyf = t.dtype
    if isinstance(iyc__dyf, PDCategoricalDtype):
        return 'pd.CategoricalDtype({})'.format(iyc__dyf.categories)
    if iyc__dyf == types.NPDatetime('ns'):
        return 'str'
    if t == string_array_type:
        return 'str'
    if isinstance(t, IntegerArrayType):
        return '"{}Int{}"'.format('' if iyc__dyf.signed else 'U', iyc__dyf.
            bitwidth)
    if t == boolean_array:
        return 'np.bool_'
    if isinstance(t, ArrayItemArrayType) and isinstance(iyc__dyf, (
        StringArrayType, ArrayItemArrayType)):
        return 'object'
    return 'np.{}'.format(iyc__dyf)


compiled_funcs = []


@numba.njit
def check_nrows_skiprows_value(nrows, skiprows):
    if nrows < -1:
        raise ValueError('pd.read_csv: nrows must be integer >= 0.')
    if skiprows[0] < 0:
        raise ValueError('pd.read_csv: skiprows must be integer >= 0.')


def astype(df, typemap, parallel):
    difd__rjjx = ''
    from collections import defaultdict
    mvf__plbf = defaultdict(list)
    for wmjke__eqidh, yhxse__dxkxk in typemap.items():
        mvf__plbf[yhxse__dxkxk].append(wmjke__eqidh)
    jxzvg__dqwe = df.columns.to_list()
    mtcp__gqwb = []
    for yhxse__dxkxk, opmmv__ghen in mvf__plbf.items():
        try:
            mtcp__gqwb.append(df.loc[:, opmmv__ghen].astype(yhxse__dxkxk,
                copy=False))
            df = df.drop(opmmv__ghen, axis=1)
        except (ValueError, TypeError) as xiluq__hhw:
            difd__rjjx = (
                f"Caught the runtime error '{xiluq__hhw}' on columns {opmmv__ghen}. Consider setting the 'dtype' argument in 'read_csv' or investigate if the data is corrupted."
                )
            break
    pdmz__npwq = bool(difd__rjjx)
    if parallel:
        dagxj__kfz = MPI.COMM_WORLD
        pdmz__npwq = dagxj__kfz.allreduce(pdmz__npwq, op=MPI.LOR)
    if pdmz__npwq:
        lsqka__wgg = 'pd.read_csv(): Bodo could not infer dtypes correctly.'
        if difd__rjjx:
            raise TypeError(f'{lsqka__wgg}\n{difd__rjjx}')
        else:
            raise TypeError(
                f'{lsqka__wgg}\nPlease refer to errors on other ranks.')
    df = pd.concat(mtcp__gqwb + [df], axis=1)
    xwa__neqnk = df.loc[:, jxzvg__dqwe]
    return xwa__neqnk


def _gen_csv_file_reader_init(parallel, header, compression, chunksize,
    is_skiprows_list, pd_low_memory):
    qhucf__kukjf = header == 0
    if compression is None:
        compression = 'uncompressed'
    if is_skiprows_list:
        reo__tgg = '  skiprows = sorted(set(skiprows))\n'
    else:
        reo__tgg = '  skiprows = [skiprows]\n'
    reo__tgg += '  skiprows_list_len = len(skiprows)\n'
    reo__tgg += '  check_nrows_skiprows_value(nrows, skiprows)\n'
    reo__tgg += '  check_java_installation(fname)\n'
    reo__tgg += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    reo__tgg += (
        '  f_reader = bodo.ir.csv_ext.csv_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    reo__tgg += (
        """    {}, bodo.utils.conversion.coerce_to_ndarray(skiprows, scalar_to_arr_len=1).ctypes, nrows, {}, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region), {}, {}, skiprows_list_len, {})
"""
        .format(parallel, qhucf__kukjf, compression, chunksize,
        is_skiprows_list, pd_low_memory))
    reo__tgg += '  bodo.utils.utils.check_and_propagate_cpp_exception()\n'
    reo__tgg += '  if bodo.utils.utils.is_null_pointer(f_reader):\n'
    reo__tgg += "      raise FileNotFoundError('File does not exist')\n"
    return reo__tgg


def _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs, usecols,
    type_usecol_offset, sep, escapechar, call_id, glbs, parallel,
    check_parallel_runtime, idx_col_index, idx_col_typ):
    ovrg__uboub = [str(ezi__zdhnp) for wey__xgrfj, ezi__zdhnp in enumerate(
        usecols) if col_typs[type_usecol_offset[wey__xgrfj]].dtype == types
        .NPDatetime('ns')]
    if idx_col_typ == types.NPDatetime('ns'):
        assert not idx_col_index is None
        ovrg__uboub.append(str(idx_col_index))
    mtr__xrxrr = ', '.join(ovrg__uboub)
    hrux__tfjh = _gen_parallel_flag_name(sanitized_cnames)
    hmj__ffec = f"{hrux__tfjh}='bool_'" if check_parallel_runtime else ''
    pjxat__epb = [_get_pd_dtype_str(col_typs[type_usecol_offset[wey__xgrfj]
        ]) for wey__xgrfj in range(len(usecols))]
    nnr__byeh = None if idx_col_index is None else _get_pd_dtype_str(
        idx_col_typ)
    awer__izrp = [ezi__zdhnp for wey__xgrfj, ezi__zdhnp in enumerate(
        usecols) if pjxat__epb[wey__xgrfj] == 'str']
    if idx_col_index is not None and nnr__byeh == 'str':
        awer__izrp.append(idx_col_index)
    brjn__sgih = np.array(awer__izrp, dtype=np.int64)
    glbs[f'str_col_nums_{call_id}'] = brjn__sgih
    reo__tgg = f'  str_col_nums_{call_id}_2 = str_col_nums_{call_id}\n'
    nok__iwant = np.array(usecols + ([idx_col_index] if idx_col_index is not
        None else []))
    glbs[f'usecols_arr_{call_id}'] = nok__iwant
    reo__tgg += f'  usecols_arr_{call_id}_2 = usecols_arr_{call_id}\n'
    gvpor__zytyz = np.array(type_usecol_offset, dtype=np.int64)
    if usecols:
        glbs[f'type_usecols_offsets_arr_{call_id}'] = gvpor__zytyz
        reo__tgg += (
            f'  type_usecols_offsets_arr_{call_id}_2 = type_usecols_offsets_arr_{call_id}\n'
            )
    klwnt__yhe = defaultdict(list)
    for wey__xgrfj, ezi__zdhnp in enumerate(usecols):
        if pjxat__epb[wey__xgrfj] == 'str':
            continue
        klwnt__yhe[pjxat__epb[wey__xgrfj]].append(ezi__zdhnp)
    if idx_col_index is not None and nnr__byeh != 'str':
        klwnt__yhe[nnr__byeh].append(idx_col_index)
    for wey__xgrfj, ovg__hqbo in enumerate(klwnt__yhe.values()):
        glbs[f't_arr_{wey__xgrfj}_{call_id}'] = np.asarray(ovg__hqbo)
        reo__tgg += (
            f'  t_arr_{wey__xgrfj}_{call_id}_2 = t_arr_{wey__xgrfj}_{call_id}\n'
            )
    if idx_col_index != None:
        reo__tgg += (
            f'  with objmode(T=table_type_{call_id}, idx_arr=idx_array_typ, {hmj__ffec}):\n'
            )
    else:
        reo__tgg += f'  with objmode(T=table_type_{call_id}, {hmj__ffec}):\n'
    reo__tgg += f'    typemap = {{}}\n'
    for wey__xgrfj, aiyxe__vrfa in enumerate(klwnt__yhe.keys()):
        reo__tgg += f"""    typemap.update({{i:{aiyxe__vrfa} for i in t_arr_{wey__xgrfj}_{call_id}_2}})
"""
    reo__tgg += '    if f_reader.get_chunk_size() == 0:\n'
    reo__tgg += (
        f'      df = pd.DataFrame(columns=usecols_arr_{call_id}_2, dtype=str)\n'
        )
    reo__tgg += '    else:\n'
    reo__tgg += '      df = pd.read_csv(f_reader,\n'
    reo__tgg += '        header=None,\n'
    reo__tgg += '        parse_dates=[{}],\n'.format(mtr__xrxrr)
    reo__tgg += f'        dtype={{i:str for i in str_col_nums_{call_id}_2}},\n'
    reo__tgg += f"""        usecols=usecols_arr_{call_id}_2, sep={sep!r}, low_memory=False, escapechar={escapechar!r})
"""
    if check_parallel_runtime:
        reo__tgg += f'    {hrux__tfjh} = f_reader.is_parallel()\n'
    else:
        reo__tgg += f'    {hrux__tfjh} = {parallel}\n'
    reo__tgg += f'    df = astype(df, typemap, {hrux__tfjh})\n'
    if idx_col_index != None:
        hsbdw__qqmxq = sorted(nok__iwant).index(idx_col_index)
        reo__tgg += f'    idx_arr = df.iloc[:, {hsbdw__qqmxq}].values\n'
        reo__tgg += (
            f'    df.drop(columns=df.columns[{hsbdw__qqmxq}], inplace=True)\n')
    if len(usecols) == 0:
        reo__tgg += f'    T = None\n'
    else:
        reo__tgg += f'    arrs = []\n'
        reo__tgg += f'    for i in range(df.shape[1]):\n'
        reo__tgg += f'      arrs.append(df.iloc[:, i].values)\n'
        reo__tgg += (
            f'    T = Table(arrs, type_usecols_offsets_arr_{call_id}_2, {len(col_names)})\n'
            )
    return reo__tgg


def _gen_parallel_flag_name(sanitized_cnames):
    hrux__tfjh = '_parallel_value'
    while hrux__tfjh in sanitized_cnames:
        hrux__tfjh = '_' + hrux__tfjh
    return hrux__tfjh


def _gen_csv_reader_py(col_names, col_typs, usecols, type_usecol_offset,
    sep, parallel, header, compression, is_skiprows_list, pd_low_memory,
    escapechar, idx_col_index=None, idx_col_typ=types.none):
    sanitized_cnames = [sanitize_varname(hgkux__nskqf) for hgkux__nskqf in
        col_names]
    reo__tgg = 'def csv_reader_py(fname, nrows, skiprows):\n'
    reo__tgg += _gen_csv_file_reader_init(parallel, header, compression, -1,
        is_skiprows_list, pd_low_memory)
    call_id = ir_utils.next_label()
    vsgq__qcib = globals()
    if idx_col_typ != types.none:
        vsgq__qcib[f'idx_array_typ'] = idx_col_typ
    if len(usecols) == 0:
        vsgq__qcib[f'table_type_{call_id}'] = types.none
    else:
        vsgq__qcib[f'table_type_{call_id}'] = TableType(tuple(col_typs))
    reo__tgg += _gen_read_csv_objmode(col_names, sanitized_cnames, col_typs,
        usecols, type_usecol_offset, sep, escapechar, call_id, vsgq__qcib,
        parallel=parallel, check_parallel_runtime=False, idx_col_index=
        idx_col_index, idx_col_typ=idx_col_typ)
    if idx_col_index != None:
        reo__tgg += '  return (T, idx_arr)\n'
    else:
        reo__tgg += '  return (T, None)\n'
    wfyy__seh = {}
    exec(reo__tgg, vsgq__qcib, wfyy__seh)
    juv__ezsm = wfyy__seh['csv_reader_py']
    vmrnx__vqau = numba.njit(juv__ezsm)
    compiled_funcs.append(vmrnx__vqau)
    return vmrnx__vqau
