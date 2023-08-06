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
    uahhk__cwfel = []
    glm__ncq = []
    wwaxl__cxem = []
    for agqv__ylpcu, eqo__xkhg in enumerate(json_node.out_vars):
        if eqo__xkhg.name in lives:
            uahhk__cwfel.append(json_node.df_colnames[agqv__ylpcu])
            glm__ncq.append(json_node.out_vars[agqv__ylpcu])
            wwaxl__cxem.append(json_node.out_types[agqv__ylpcu])
    json_node.df_colnames = uahhk__cwfel
    json_node.out_vars = glm__ncq
    json_node.out_types = wwaxl__cxem
    if len(json_node.out_vars) == 0:
        return None
    return json_node


def json_distributed_run(json_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    if array_dists is not None:
        parallel = True
        for hid__xre in json_node.out_vars:
            if array_dists[hid__xre.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                hid__xre.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    updk__bjdt = len(json_node.out_vars)
    loly__pnswi = ', '.join('arr' + str(agqv__ylpcu) for agqv__ylpcu in
        range(updk__bjdt))
    doi__izt = 'def json_impl(fname):\n'
    doi__izt += '    ({},) = _json_reader_py(fname)\n'.format(loly__pnswi)
    tbek__gzrhd = {}
    exec(doi__izt, {}, tbek__gzrhd)
    qwclg__ufng = tbek__gzrhd['json_impl']
    jppu__qna = _gen_json_reader_py(json_node.df_colnames, json_node.
        out_types, typingctx, targetctx, parallel, json_node.orient,
        json_node.convert_dates, json_node.precise_float, json_node.lines,
        json_node.compression)
    ujxos__ylia = compile_to_numba_ir(qwclg__ufng, {'_json_reader_py':
        jppu__qna}, typingctx=typingctx, targetctx=targetctx, arg_typs=(
        string_type,), typemap=typemap, calltypes=calltypes).blocks.popitem()[1
        ]
    replace_arg_nodes(ujxos__ylia, [json_node.file_name])
    ljfc__opjrs = ujxos__ylia.body[:-3]
    for agqv__ylpcu in range(len(json_node.out_vars)):
        ljfc__opjrs[-len(json_node.out_vars) + agqv__ylpcu
            ].target = json_node.out_vars[agqv__ylpcu]
    return ljfc__opjrs


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
    ufh__zgd = [sanitize_varname(fbli__dix) for fbli__dix in col_names]
    mnaf__mhjrv = ', '.join(str(agqv__ylpcu) for agqv__ylpcu, tfe__njz in
        enumerate(col_typs) if tfe__njz.dtype == types.NPDatetime('ns'))
    ekizd__abv = ', '.join(["{}='{}'".format(lruab__hxcbu, bodo.ir.csv_ext.
        _get_dtype_str(tfe__njz)) for lruab__hxcbu, tfe__njz in zip(
        ufh__zgd, col_typs)])
    unk__knht = ', '.join(["'{}':{}".format(ziakb__chz, bodo.ir.csv_ext.
        _get_pd_dtype_str(tfe__njz)) for ziakb__chz, tfe__njz in zip(
        col_names, col_typs)])
    if compression is None:
        compression = 'uncompressed'
    doi__izt = 'def json_reader_py(fname):\n'
    doi__izt += '  check_java_installation(fname)\n'
    doi__izt += f"""  bucket_region = bodo.io.fs_io.get_s3_bucket_region_njit(fname, parallel={parallel})
"""
    doi__izt += (
        '  f_reader = bodo.ir.json_ext.json_file_chunk_reader(bodo.libs.str_ext.unicode_to_utf8(fname), '
        )
    doi__izt += (
        """    {}, {}, -1, bodo.libs.str_ext.unicode_to_utf8('{}'), bodo.libs.str_ext.unicode_to_utf8(bucket_region) )
"""
        .format(lines, parallel, compression))
    doi__izt += '  bodo.utils.utils.check_and_propagate_cpp_exception()\n'
    doi__izt += '  if bodo.utils.utils.is_null_pointer(f_reader):\n'
    doi__izt += "      raise FileNotFoundError('File does not exist')\n"
    doi__izt += '  with objmode({}):\n'.format(ekizd__abv)
    doi__izt += "    df = pd.read_json(f_reader, orient='{}',\n".format(orient)
    doi__izt += '       convert_dates = {}, \n'.format(convert_dates)
    doi__izt += '       precise_float={}, \n'.format(precise_float)
    doi__izt += '       lines={}, \n'.format(lines)
    doi__izt += '       dtype={{{}}},\n'.format(unk__knht)
    doi__izt += '       )\n'
    for lruab__hxcbu, ziakb__chz in zip(ufh__zgd, col_names):
        doi__izt += '    if len(df) > 0:\n'
        doi__izt += "        {} = df['{}'].values\n".format(lruab__hxcbu,
            ziakb__chz)
        doi__izt += '    else:\n'
        doi__izt += '        {} = np.array([])\n'.format(lruab__hxcbu)
    doi__izt += '  return ({},)\n'.format(', '.join(epweo__eqjx for
        epweo__eqjx in ufh__zgd))
    lqypn__rimt = globals()
    tbek__gzrhd = {}
    exec(doi__izt, lqypn__rimt, tbek__gzrhd)
    jppu__qna = tbek__gzrhd['json_reader_py']
    wozs__ejfo = numba.njit(jppu__qna)
    compiled_funcs.append(wozs__ejfo)
    return wozs__ejfo
