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
    pdh__ispoi = []
    dhfaz__rkav = []
    gqcdc__phbnm = []
    for gjpvn__hhxel, yha__ecn in enumerate(json_node.out_vars):
        if yha__ecn.name in lives:
            pdh__ispoi.append(json_node.df_colnames[gjpvn__hhxel])
            dhfaz__rkav.append(json_node.out_vars[gjpvn__hhxel])
            gqcdc__phbnm.append(json_node.out_types[gjpvn__hhxel])
    json_node.df_colnames = pdh__ispoi
    json_node.out_vars = dhfaz__rkav
    json_node.out_types = gqcdc__phbnm
    if len(json_node.out_vars) == 0:
        return None
    return json_node


def json_distributed_run(json_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    if array_dists is not None:
        parallel = True
        for sakm__ftk in json_node.out_vars:
            if array_dists[sakm__ftk.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                sakm__ftk.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    cezer__spp = len(json_node.out_vars)
    xyz__rpq = ', '.join('arr' + str(gjpvn__hhxel) for gjpvn__hhxel in
        range(cezer__spp))
    qsw__apmec = 'def json_impl(fname):\n'
    qsw__apmec += '    ({},) = _json_reader_py(fname)\n'.format(xyz__rpq)
    qxxyu__uyb = {}
    exec(qsw__apmec, {}, qxxyu__uyb)
    ouho__cbk = qxxyu__uyb['json_impl']
    boenu__pre = _gen_json_reader_py(json_node.df_colnames, json_node.
        out_types, typingctx, targetctx, parallel, json_node.orient,
        json_node.convert_dates, json_node.precise_float, json_node.lines,
        json_node.compression)
    vgmlr__cljzi = compile_to_numba_ir(ouho__cbk, {'_json_reader_py':
        boenu__pre}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type,), typemap=typemap, calltypes=calltypes).blocks.popitem()[1
        ]
    replace_arg_nodes(vgmlr__cljzi, [json_node.file_name])
    hmq__tjibz = vgmlr__cljzi.body[:-3]
    for gjpvn__hhxel in range(len(json_node.out_vars)):
        hmq__tjibz[-len(json_node.out_vars) + gjpvn__hhxel
            ].target = json_node.out_vars[gjpvn__hhxel]
    return hmq__tjibz


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
    vngnn__bmchw = [sanitize_varname(dqa__fcmcv) for dqa__fcmcv in col_names]
    dhkkr__xykm = ', '.join(str(gjpvn__hhxel) for gjpvn__hhxel, ngr__hkwp in
        enumerate(col_typs) if ngr__hkwp.dtype == types.NPDatetime('ns'))
    pgnx__xlog = ', '.join(["{}='{}'".format(ebm__osz, bodo.ir.csv_ext.
        _get_dtype_str(ngr__hkwp)) for ebm__osz, ngr__hkwp in zip(
        vngnn__bmchw, col_typs)])
    fmhq__zeaao = ', '.join(["'{}':{}".format(wtm__dznvg, bodo.ir.csv_ext.
        _get_pd_dtype_str(ngr__hkwp)) for wtm__dznvg, ngr__hkwp in zip(
        col_names, col_typs)])
    if compression is None:
        compression = 'uncompressed'
    qsw__apmec = 'def json_reader_py(fname):\n'
    qsw__apmec += '  check_java_installation(fname)\n'
    qsw__apmec += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    qsw__apmec += (
        '  f_reader = bodo.ir.json_ext.json_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    qsw__apmec += (
        """    {}, {}, -1, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region) )
"""
        .format(lines, parallel, compression))
    qsw__apmec += '  bodo.utils.utils.check_and_propagate_cpp_exception()\n'
    qsw__apmec += '  if bodo.utils.utils.is_null_pointer(f_reader):\n'
    qsw__apmec += "      raise FileNotFoundError('File does not exist')\n"
    qsw__apmec += '  with objmode({}):\n'.format(pgnx__xlog)
    qsw__apmec += "    df = pd.read_json(f_reader, orient='{}',\n".format(
        orient)
    qsw__apmec += '       convert_dates = {}, \n'.format(convert_dates)
    qsw__apmec += '       precise_float={}, \n'.format(precise_float)
    qsw__apmec += '       lines={}, \n'.format(lines)
    qsw__apmec += '       dtype={{{}}},\n'.format(fmhq__zeaao)
    qsw__apmec += '       )\n'
    for ebm__osz, wtm__dznvg in zip(vngnn__bmchw, col_names):
        qsw__apmec += '    if len(df) > 0:\n'
        qsw__apmec += "        {} = df['{}'].values\n".format(ebm__osz,
            wtm__dznvg)
        qsw__apmec += '    else:\n'
        qsw__apmec += '        {} = np.array([])\n'.format(ebm__osz)
    qsw__apmec += '  return ({},)\n'.format(', '.join(mqhze__knt for
        mqhze__knt in vngnn__bmchw))
    osd__vnra = globals()
    qxxyu__uyb = {}
    exec(qsw__apmec, osd__vnra, qxxyu__uyb)
    boenu__pre = qxxyu__uyb['json_reader_py']
    qsq__bfv = numba.njit(boenu__pre)
    compiled_funcs.append(qsq__bfv)
    return qsq__bfv
