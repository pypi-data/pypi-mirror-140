import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.libs.str_ext import string_type
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.utils.utils import check_java_installation
from bodo.utils.utils import sanitize_varname


class JsonReader(ir.Stmt):

    def __init__(self, df_out, loc, out_vars, out_types, file_name,
        df_colnames, orient, convert_dates, precise_float, lines, compression):
        self.connector_typ = 'json'
        self.df_out = df_out
        self.loc = loc
        self.out_vars = out_vars
        self.out_types = out_types
        self.file_name = file_name
        self.df_colnames = df_colnames
        self.orient = orient
        self.convert_dates = convert_dates
        self.precise_float = precise_float
        self.lines = lines
        self.compression = compression

    def __repr__(self):
        return ('{} = ReadJson(file={}, col_names={}, types={}, vars={})'.
            format(self.df_out, self.file_name, self.df_colnames, self.
            out_types, self.out_vars))


import llvmlite.binding as ll
from bodo.io import json_cpp
ll.add_symbol('json_file_chunk_reader', json_cpp.json_file_chunk_reader)
json_file_chunk_reader = types.ExternalFunction('json_file_chunk_reader',
    bodo.ir.connector.stream_reader_type(types.voidptr, types.bool_, types.
    bool_, types.int64, types.voidptr, types.voidptr))


def remove_dead_json(json_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    pdr__iqt = []
    dkt__knih = []
    vyyo__rsort = []
    for kutm__hvcbi, nar__ldf in enumerate(json_node.out_vars):
        if nar__ldf.name in lives:
            pdr__iqt.append(json_node.df_colnames[kutm__hvcbi])
            dkt__knih.append(json_node.out_vars[kutm__hvcbi])
            vyyo__rsort.append(json_node.out_types[kutm__hvcbi])
    json_node.df_colnames = pdr__iqt
    json_node.out_vars = dkt__knih
    json_node.out_types = vyyo__rsort
    if len(json_node.out_vars) == 0:
        return None
    return json_node


def json_distributed_run(json_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    if array_dists is not None:
        parallel = True
        for rqd__yegy in json_node.out_vars:
            if array_dists[rqd__yegy.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                rqd__yegy.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    yfamx__wjeby = len(json_node.out_vars)
    byqdv__jay = ', '.join('arr' + str(kutm__hvcbi) for kutm__hvcbi in
        range(yfamx__wjeby))
    lzu__icrq = 'def json_impl(fname):\n'
    lzu__icrq += '    ({},) = _json_reader_py(fname)\n'.format(byqdv__jay)
    acn__dyni = {}
    exec(lzu__icrq, {}, acn__dyni)
    dfh__jymo = acn__dyni['json_impl']
    jzha__puqe = _gen_json_reader_py(json_node.df_colnames, json_node.
        out_types, typingctx, targetctx, parallel, json_node.orient,
        json_node.convert_dates, json_node.precise_float, json_node.lines,
        json_node.compression)
    qdbvh__evc = compile_to_numba_ir(dfh__jymo, {'_json_reader_py':
        jzha__puqe}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type,), typemap=typemap, calltypes=calltypes).blocks.popitem()[1
        ]
    replace_arg_nodes(qdbvh__evc, [json_node.file_name])
    uiu__luqpt = qdbvh__evc.body[:-3]
    for kutm__hvcbi in range(len(json_node.out_vars)):
        uiu__luqpt[-len(json_node.out_vars) + kutm__hvcbi
            ].target = json_node.out_vars[kutm__hvcbi]
    return uiu__luqpt


numba.parfors.array_analysis.array_analysis_extensions[JsonReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[JsonReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[JsonReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[JsonReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[JsonReader] = remove_dead_json
numba.core.analysis.ir_extension_usedefs[JsonReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[JsonReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[JsonReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[JsonReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[JsonReader] = json_distributed_run
compiled_funcs = []


def _gen_json_reader_py(col_names, col_typs, typingctx, targetctx, parallel,
    orient, convert_dates, precise_float, lines, compression):
    hxe__wvjbk = [sanitize_varname(ngpl__qmh) for ngpl__qmh in col_names]
    hrb__qozu = ', '.join(str(kutm__hvcbi) for kutm__hvcbi, kctg__rpdx in
        enumerate(col_typs) if kctg__rpdx.dtype == types.NPDatetime('ns'))
    fnyv__yxpw = ', '.join(["{}='{}'".format(mtez__quodt, bodo.ir.csv_ext.
        _get_dtype_str(kctg__rpdx)) for mtez__quodt, kctg__rpdx in zip(
        hxe__wvjbk, col_typs)])
    qmoa__adpfk = ', '.join(["'{}':{}".format(bvruj__pre, bodo.ir.csv_ext.
        _get_pd_dtype_str(kctg__rpdx)) for bvruj__pre, kctg__rpdx in zip(
        col_names, col_typs)])
    if compression is None:
        compression = 'uncompressed'
    lzu__icrq = 'def json_reader_py(fname):\n'
    lzu__icrq += '  check_java_installation(fname)\n'
    lzu__icrq += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    lzu__icrq += (
        '  f_reader = bodo.ir.json_ext.json_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    lzu__icrq += (
        """    {}, {}, -1, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region) )
"""
        .format(lines, parallel, compression))
    lzu__icrq += '  bodo.utils.utils.check_and_propagate_cpp_exception()\n'
    lzu__icrq += '  if bodo.utils.utils.is_null_pointer(f_reader):\n'
    lzu__icrq += "      raise FileNotFoundError('File does not exist')\n"
    lzu__icrq += '  with objmode({}):\n'.format(fnyv__yxpw)
    lzu__icrq += "    df = pd.read_json(f_reader, orient='{}',\n".format(orient
        )
    lzu__icrq += '       convert_dates = {}, \n'.format(convert_dates)
    lzu__icrq += '       precise_float={}, \n'.format(precise_float)
    lzu__icrq += '       lines={}, \n'.format(lines)
    lzu__icrq += '       dtype={{{}}},\n'.format(qmoa__adpfk)
    lzu__icrq += '       )\n'
    for mtez__quodt, bvruj__pre in zip(hxe__wvjbk, col_names):
        lzu__icrq += '    if len(df) > 0:\n'
        lzu__icrq += "        {} = df['{}'].values\n".format(mtez__quodt,
            bvruj__pre)
        lzu__icrq += '    else:\n'
        lzu__icrq += '        {} = np.array([])\n'.format(mtez__quodt)
    lzu__icrq += '  return ({},)\n'.format(', '.join(tqna__sqj for
        tqna__sqj in hxe__wvjbk))
    bms__fxcg = globals()
    acn__dyni = {}
    exec(lzu__icrq, bms__fxcg, acn__dyni)
    jzha__puqe = acn__dyni['json_reader_py']
    pfn__girru = numba.njit(jzha__puqe)
    compiled_funcs.append(pfn__girru)
    return pfn__girru
