"""
Implementation of pd.read_sql in BODO.
We piggyback on the pandas implementation. Future plan is to have a faster
version for this task.
"""
import numba
import numpy as np
import pandas as pd
from numba.core import ir, ir_utils, typeinfer, types
from numba.core.ir_utils import compile_to_numba_ir, replace_arg_nodes
import bodo
import bodo.ir.connector
from bodo import objmode
from bodo.ir.csv_ext import _get_dtype_str
from bodo.libs.array import delete_table, info_from_table, info_to_array, table_type
from bodo.libs.distributed_api import bcast, bcast_scalar
from bodo.libs.str_ext import string_type, unicode_to_utf8
from bodo.transforms import distributed_analysis, distributed_pass
from bodo.utils.typing import BodoError
from bodo.utils.utils import check_and_propagate_cpp_exception, sanitize_varname
MPI_ROOT = 0


class SqlReader(ir.Stmt):

    def __init__(self, sql_request, connection, df_out, df_colnames,
        out_vars, out_types, converted_colnames, db_type, loc):
        self.connector_typ = 'sql'
        self.sql_request = sql_request
        self.connection = connection
        self.df_out = df_out
        self.df_colnames = df_colnames
        self.out_vars = out_vars
        self.out_types = out_types
        self.converted_colnames = converted_colnames
        self.loc = loc
        self.limit = req_limit(sql_request)
        self.db_type = db_type
        self.filters = None

    def __repr__(self):
        return (
            '{} = ReadSql(sql_request={}, connection={}, col_names={}, types={}, vars={}, limit={})'
            .format(self.df_out, self.sql_request, self.connection, self.
            df_colnames, self.out_types, self.out_vars, self.limit))


def remove_dead_sql(sql_node, lives_no_aliases, lives, arg_aliases,
    alias_map, func_ir, typemap):
    nuqw__pqrtn = []
    gyo__cccqb = []
    ynws__xic = []
    for aio__rzztf, jtoe__hacft in enumerate(sql_node.out_vars):
        if jtoe__hacft.name in lives:
            nuqw__pqrtn.append(sql_node.df_colnames[aio__rzztf])
            gyo__cccqb.append(sql_node.out_vars[aio__rzztf])
            ynws__xic.append(sql_node.out_types[aio__rzztf])
    sql_node.df_colnames = nuqw__pqrtn
    sql_node.out_vars = gyo__cccqb
    sql_node.out_types = ynws__xic
    if len(sql_node.out_vars) == 0:
        return None
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    if array_dists is not None:
        parallel = True
        for lml__okxd in sql_node.out_vars:
            if array_dists[lml__okxd.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                lml__okxd.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    fxg__ifc = len(sql_node.out_vars)
    hdxsb__sfb = ', '.join('arr' + str(aio__rzztf) for aio__rzztf in range(
        fxg__ifc))
    wzbma__aouvy, cljpd__cha = bodo.ir.connector.generate_filter_map(sql_node
        .filters)
    btp__razqs = ', '.join(wzbma__aouvy.values())
    tyuc__nms = f'def sql_impl(sql_request, conn, {btp__razqs}):\n'
    if sql_node.filters:
        mmbo__iccv = []
        for hhbcu__zthak in sql_node.filters:
            qlxgf__beib = [' '.join(['(', xxh__rhh[0], xxh__rhh[1], '{' +
                wzbma__aouvy[xxh__rhh[2].name] + '}' if isinstance(xxh__rhh
                [2], ir.Var) else xxh__rhh[2], ')']) for xxh__rhh in
                hhbcu__zthak]
            mmbo__iccv.append(' ( ' + ' AND '.join(qlxgf__beib) + ' ) ')
        msprl__njlex = ' WHERE ' + ' OR '.join(mmbo__iccv)
        for aio__rzztf, jjn__bpjov in enumerate(wzbma__aouvy.values()):
            tyuc__nms += f'    {jjn__bpjov} = get_sql_literal({jjn__bpjov})\n'
        tyuc__nms += f'    sql_request = f"{{sql_request}} {msprl__njlex}"\n'
    tyuc__nms += '    ({},) = _sql_reader_py(sql_request, conn)\n'.format(
        hdxsb__sfb)
    dfzf__vhzu = {}
    exec(tyuc__nms, {}, dfzf__vhzu)
    pbum__ptvlq = dfzf__vhzu['sql_impl']
    ikeva__fraw = _gen_sql_reader_py(sql_node.df_colnames, sql_node.
        out_types, typingctx, targetctx, sql_node.db_type, sql_node.limit,
        sql_node.converted_colnames, parallel)
    rbkq__fezpt = compile_to_numba_ir(pbum__ptvlq, {'_sql_reader_py':
        ikeva__fraw, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type) + tuple(
        typemap[lml__okxd.name] for lml__okxd in cljpd__cha), typemap=
        typemap, calltypes=calltypes).blocks.popitem()[1]
    niosw__box = escape_column_names(sql_node.df_colnames, sql_node.db_type,
        sql_node.converted_colnames)
    if sql_node.db_type == 'oracle':
        dvfo__kbvhg = ('SELECT ' + niosw__box + ' FROM (' + sql_node.
            sql_request + ') TEMP')
    else:
        dvfo__kbvhg = ('SELECT ' + niosw__box + ' FROM (' + sql_node.
            sql_request + ') as TEMP')
    replace_arg_nodes(rbkq__fezpt, [ir.Const(dvfo__kbvhg, sql_node.loc), ir
        .Const(sql_node.connection, sql_node.loc)] + cljpd__cha)
    gpu__osmg = rbkq__fezpt.body[:-3]
    for aio__rzztf in range(len(sql_node.out_vars)):
        gpu__osmg[-len(sql_node.out_vars) + aio__rzztf
            ].target = sql_node.out_vars[aio__rzztf]
    return gpu__osmg


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        qcy__nak = [(nrc__dqyha.upper() if nrc__dqyha in converted_colnames
             else nrc__dqyha) for nrc__dqyha in col_names]
        niosw__box = ', '.join([f'"{nrc__dqyha}"' for nrc__dqyha in qcy__nak])
    elif db_type == 'mysql' or db_type == 'mysql+pymysql':
        niosw__box = ', '.join([f'`{nrc__dqyha}`' for nrc__dqyha in col_names])
    else:
        niosw__box = ', '.join([f'"{nrc__dqyha}"' for nrc__dqyha in col_names])
    return niosw__box


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    rfi__lsbrb = types.unliteral(filter_value)
    if rfi__lsbrb == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(rfi__lsbrb, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif rfi__lsbrb == bodo.pd_timestamp_type:

        def impl(filter_value):
            uex__zjv = filter_value.nanosecond
            msty__qxiny = ''
            if uex__zjv < 10:
                msty__qxiny = '00'
            elif uex__zjv < 100:
                msty__qxiny = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{msty__qxiny}{uex__zjv}'"
                )
        return impl
    elif rfi__lsbrb == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {rfi__lsbrb} used in filter pushdown.'
            )


numba.parfors.array_analysis.array_analysis_extensions[SqlReader
    ] = bodo.ir.connector.connector_array_analysis
distributed_analysis.distributed_analysis_extensions[SqlReader
    ] = bodo.ir.connector.connector_distributed_analysis
typeinfer.typeinfer_extensions[SqlReader
    ] = bodo.ir.connector.connector_typeinfer
ir_utils.visit_vars_extensions[SqlReader
    ] = bodo.ir.connector.visit_vars_connector
ir_utils.remove_dead_extensions[SqlReader] = remove_dead_sql
numba.core.analysis.ir_extension_usedefs[SqlReader
    ] = bodo.ir.connector.connector_usedefs
ir_utils.copy_propagate_extensions[SqlReader
    ] = bodo.ir.connector.get_copies_connector
ir_utils.apply_copy_propagate_extensions[SqlReader
    ] = bodo.ir.connector.apply_copies_connector
ir_utils.build_defs_extensions[SqlReader
    ] = bodo.ir.connector.build_connector_definitions
distributed_pass.distributed_run_extensions[SqlReader] = sql_distributed_run
compiled_funcs = []


@numba.njit
def sqlalchemy_check():
    with numba.objmode():
        sqlalchemy_check_()


def sqlalchemy_check_():
    try:
        import sqlalchemy
    except ImportError as yts__rvh:
        iwgq__iru = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(iwgq__iru)


def req_limit(sql_request):
    import re
    uxpdd__pqj = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    atufl__eahy = uxpdd__pqj.search(sql_request)
    if atufl__eahy:
        return int(atufl__eahy.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names, col_typs, typingctx, targetctx, db_type,
    limit, converted_colnames, parallel):
    qyt__ptrvc = [sanitize_varname(ycc__palgs) for ycc__palgs in col_names]
    mrs__voupw = ["{}='{}'".format(uhyx__frnaz, _get_dtype_str(lsgmy__nvtl)
        ) for uhyx__frnaz, lsgmy__nvtl in zip(qyt__ptrvc, col_typs)]
    if bodo.sql_access_method == 'multiple_access_by_block':
        tyuc__nms = 'def sql_reader_py(sql_request,conn):\n'
        tyuc__nms += '  sqlalchemy_check()\n'
        tyuc__nms += '  rank = bodo.libs.distributed_api.get_rank()\n'
        tyuc__nms += '  n_pes = bodo.libs.distributed_api.get_size()\n'
        tyuc__nms += '  with objmode({}):\n'.format(', '.join(mrs__voupw))
        tyuc__nms += '    list_df_block = []\n'
        tyuc__nms += '    block_size = 50000\n'
        tyuc__nms += '    iter = 0\n'
        tyuc__nms += '    while(True):\n'
        tyuc__nms += '      offset = (iter * n_pes + rank) * block_size\n'
        if db_type == 'oracle':
            tyuc__nms += """      sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(block_size) + ' ROWS ONLY'
"""
        else:
            tyuc__nms += """      sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(block_size) + ' OFFSET ' + str(offset)
"""
        tyuc__nms += '      df_block = pd.read_sql(sql_cons, conn)\n'
        tyuc__nms += '      if df_block.size == 0:\n'
        tyuc__nms += '        break\n'
        tyuc__nms += '      list_df_block.append(df_block)\n'
        tyuc__nms += '      iter += 1\n'
        tyuc__nms += '    df_ret = pd.concat(list_df_block)\n'
        for uhyx__frnaz, pob__qej in zip(qyt__ptrvc, col_names):
            tyuc__nms += "    {} = df_ret['{}'].values\n".format(uhyx__frnaz,
                pob__qej)
        tyuc__nms += '  return ({},)\n'.format(', '.join(luzl__jfeh for
            luzl__jfeh in qyt__ptrvc))
    if bodo.sql_access_method == 'multiple_access_nb_row_first':
        tyuc__nms = 'def sql_reader_py(sql_request, conn):\n'
        if db_type == 'snowflake':
            tca__znhh = {}
            for aio__rzztf, ejple__rtj in enumerate(col_typs):
                tca__znhh[f'col_{aio__rzztf}_type'] = ejple__rtj
            tyuc__nms += (
                f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n"
                )

            def is_nullable(typ):
                return bodo.utils.utils.is_array_typ(typ, False
                    ) and not isinstance(typ, types.Array)
            ngo__qbjcv = [int(is_nullable(ejple__rtj)) for ejple__rtj in
                col_typs]
            tyuc__nms += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(col_names)}, np.array({ngo__qbjcv}, dtype=np.int32).ctypes)
"""
            tyuc__nms += '  check_and_propagate_cpp_exception()\n'
            for aio__rzztf, penb__xnt in enumerate(qyt__ptrvc):
                tyuc__nms += f"""  {penb__xnt} = info_to_array(info_from_table(out_table, {aio__rzztf}), col_{aio__rzztf}_type)
"""
            tyuc__nms += '  delete_table(out_table)\n'
            tyuc__nms += f'  ev.finalize()\n'
        else:
            tyuc__nms += '  sqlalchemy_check()\n'
            if parallel:
                tyuc__nms += '  rank = bodo.libs.distributed_api.get_rank()\n'
                if limit is not None:
                    tyuc__nms += f'  nb_row = {limit}\n'
                else:
                    tyuc__nms += '  with objmode(nb_row="int64"):\n'
                    tyuc__nms += f'     if rank == {MPI_ROOT}:\n'
                    tyuc__nms += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                    tyuc__nms += (
                        '         frame = pd.read_sql(sql_cons, conn)\n')
                    tyuc__nms += '         nb_row = frame.iat[0,0]\n'
                    tyuc__nms += '     else:\n'
                    tyuc__nms += '         nb_row = 0\n'
                    tyuc__nms += '  nb_row = bcast_scalar(nb_row)\n'
                tyuc__nms += '  with objmode({}):\n'.format(', '.join(
                    mrs__voupw))
                tyuc__nms += """    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)
"""
                niosw__box = escape_column_names(col_names, db_type,
                    converted_colnames)
                if db_type == 'oracle':
                    tyuc__nms += f"""    sql_cons = 'select {niosw__box} from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
                else:
                    tyuc__nms += f"""    sql_cons = 'select {niosw__box} from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
                tyuc__nms += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            else:
                tyuc__nms += '  with objmode({}):\n'.format(', '.join(
                    mrs__voupw))
                tyuc__nms += '    df_ret = pd.read_sql(sql_request, conn)\n'
            for uhyx__frnaz, pob__qej in zip(qyt__ptrvc, col_names):
                tyuc__nms += "    {} = df_ret['{}'].values\n".format(
                    uhyx__frnaz, pob__qej)
        tyuc__nms += '  return ({},)\n'.format(', '.join(luzl__jfeh for
            luzl__jfeh in qyt__ptrvc))
    mufp__ilhi = {'bodo': bodo}
    if db_type == 'snowflake':
        mufp__ilhi.update(tca__znhh)
        mufp__ilhi.update({'np': np, 'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'snowflake_read':
            _snowflake_read, 'info_to_array': info_to_array,
            'info_from_table': info_from_table, 'delete_table': delete_table})
    else:
        mufp__ilhi.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar})
    dfzf__vhzu = {}
    exec(tyuc__nms, mufp__ilhi, dfzf__vhzu)
    ikeva__fraw = dfzf__vhzu['sql_reader_py']
    cctx__dujt = numba.njit(ikeva__fraw)
    compiled_funcs.append(cctx__dujt)
    return cctx__dujt


_snowflake_read = types.ExternalFunction('snowflake_read', table_type(types
    .voidptr, types.voidptr, types.boolean, types.int64, types.voidptr))
import llvmlite.binding as ll
from bodo.io import arrow_cpp
ll.add_symbol('snowflake_read', arrow_cpp.snowflake_read)
