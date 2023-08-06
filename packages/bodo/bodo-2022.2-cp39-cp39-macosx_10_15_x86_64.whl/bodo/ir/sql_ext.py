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
    iyi__moh = []
    xkqh__qniuu = []
    nzg__digc = []
    for cxrqe__mua, seh__klfh in enumerate(sql_node.out_vars):
        if seh__klfh.name in lives:
            iyi__moh.append(sql_node.df_colnames[cxrqe__mua])
            xkqh__qniuu.append(sql_node.out_vars[cxrqe__mua])
            nzg__digc.append(sql_node.out_types[cxrqe__mua])
    sql_node.df_colnames = iyi__moh
    sql_node.out_vars = xkqh__qniuu
    sql_node.out_types = nzg__digc
    if len(sql_node.out_vars) == 0:
        return None
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    if array_dists is not None:
        parallel = True
        for foae__yvkah in sql_node.out_vars:
            if array_dists[foae__yvkah.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                foae__yvkah.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    kqp__vnq = len(sql_node.out_vars)
    ipuzq__wjf = ', '.join('arr' + str(cxrqe__mua) for cxrqe__mua in range(
        kqp__vnq))
    qftl__abhp, kno__kgl = bodo.ir.connector.generate_filter_map(sql_node.
        filters)
    djdt__urz = ', '.join(qftl__abhp.values())
    yslo__ani = f'def sql_impl(sql_request, conn, {djdt__urz}):\n'
    if sql_node.filters:
        igs__osbe = []
        for asm__jbgk in sql_node.filters:
            lsv__gxu = [' '.join(['(', rjt__yvhoa[0], rjt__yvhoa[1], '{' +
                qftl__abhp[rjt__yvhoa[2].name] + '}' if isinstance(
                rjt__yvhoa[2], ir.Var) else rjt__yvhoa[2], ')']) for
                rjt__yvhoa in asm__jbgk]
            igs__osbe.append(' ( ' + ' AND '.join(lsv__gxu) + ' ) ')
        dnby__kgylk = ' WHERE ' + ' OR '.join(igs__osbe)
        for cxrqe__mua, vflc__pjn in enumerate(qftl__abhp.values()):
            yslo__ani += f'    {vflc__pjn} = get_sql_literal({vflc__pjn})\n'
        yslo__ani += f'    sql_request = f"{{sql_request}} {dnby__kgylk}"\n'
    yslo__ani += '    ({},) = _sql_reader_py(sql_request, conn)\n'.format(
        ipuzq__wjf)
    mvyd__yfaon = {}
    exec(yslo__ani, {}, mvyd__yfaon)
    okqc__ofp = mvyd__yfaon['sql_impl']
    ijufd__wll = _gen_sql_reader_py(sql_node.df_colnames, sql_node.
        out_types, typingctx, targetctx, sql_node.db_type, sql_node.limit,
        sql_node.converted_colnames, parallel)
    cns__yafb = compile_to_numba_ir(okqc__ofp, {'_sql_reader_py':
        ijufd__wll, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type) + tuple(
        typemap[foae__yvkah.name] for foae__yvkah in kno__kgl), typemap=
        typemap, calltypes=calltypes).blocks.popitem()[1]
    sgac__feb = escape_column_names(sql_node.df_colnames, sql_node.db_type,
        sql_node.converted_colnames)
    if sql_node.db_type == 'oracle':
        jqls__yaahy = ('SELECT ' + sgac__feb + ' FROM (' + sql_node.
            sql_request + ') TEMP')
    else:
        jqls__yaahy = ('SELECT ' + sgac__feb + ' FROM (' + sql_node.
            sql_request + ') as TEMP')
    replace_arg_nodes(cns__yafb, [ir.Const(jqls__yaahy, sql_node.loc), ir.
        Const(sql_node.connection, sql_node.loc)] + kno__kgl)
    dceq__cwf = cns__yafb.body[:-3]
    for cxrqe__mua in range(len(sql_node.out_vars)):
        dceq__cwf[-len(sql_node.out_vars) + cxrqe__mua
            ].target = sql_node.out_vars[cxrqe__mua]
    return dceq__cwf


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        uec__zoob = [(ftual__psklz.upper() if ftual__psklz in
            converted_colnames else ftual__psklz) for ftual__psklz in col_names
            ]
        sgac__feb = ', '.join([f'"{ftual__psklz}"' for ftual__psklz in
            uec__zoob])
    elif db_type == 'mysql' or db_type == 'mysql+pymysql':
        sgac__feb = ', '.join([f'`{ftual__psklz}`' for ftual__psklz in
            col_names])
    else:
        sgac__feb = ', '.join([f'"{ftual__psklz}"' for ftual__psklz in
            col_names])
    return sgac__feb


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    qfprh__plbn = types.unliteral(filter_value)
    if qfprh__plbn == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(qfprh__plbn, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif qfprh__plbn == bodo.pd_timestamp_type:

        def impl(filter_value):
            btji__rtwxx = filter_value.nanosecond
            odos__xzi = ''
            if btji__rtwxx < 10:
                odos__xzi = '00'
            elif btji__rtwxx < 100:
                odos__xzi = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{odos__xzi}{btji__rtwxx}'"
                )
        return impl
    elif qfprh__plbn == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {qfprh__plbn} used in filter pushdown.'
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
    except ImportError as almlf__rib:
        dzfes__abys = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(dzfes__abys)


def req_limit(sql_request):
    import re
    smi__rgqoq = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    hvb__cktr = smi__rgqoq.search(sql_request)
    if hvb__cktr:
        return int(hvb__cktr.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names, col_typs, typingctx, targetctx, db_type,
    limit, converted_colnames, parallel):
    yrgx__teizt = [sanitize_varname(hxow__upf) for hxow__upf in col_names]
    vzsyj__bbso = ["{}='{}'".format(tfrz__chsmz, _get_dtype_str(gvtr__dkd)) for
        tfrz__chsmz, gvtr__dkd in zip(yrgx__teizt, col_typs)]
    if bodo.sql_access_method == 'multiple_access_by_block':
        yslo__ani = 'def sql_reader_py(sql_request,conn):\n'
        yslo__ani += '  sqlalchemy_check()\n'
        yslo__ani += '  rank = bodo.libs.distributed_api.get_rank()\n'
        yslo__ani += '  n_pes = bodo.libs.distributed_api.get_size()\n'
        yslo__ani += '  with objmode({}):\n'.format(', '.join(vzsyj__bbso))
        yslo__ani += '    list_df_block = []\n'
        yslo__ani += '    block_size = 50000\n'
        yslo__ani += '    iter = 0\n'
        yslo__ani += '    while(True):\n'
        yslo__ani += '      offset = (iter * n_pes + rank) * block_size\n'
        if db_type == 'oracle':
            yslo__ani += """      sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(block_size) + ' ROWS ONLY'
"""
        else:
            yslo__ani += """      sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(block_size) + ' OFFSET ' + str(offset)
"""
        yslo__ani += '      df_block = pd.read_sql(sql_cons, conn)\n'
        yslo__ani += '      if df_block.size == 0:\n'
        yslo__ani += '        break\n'
        yslo__ani += '      list_df_block.append(df_block)\n'
        yslo__ani += '      iter += 1\n'
        yslo__ani += '    df_ret = pd.concat(list_df_block)\n'
        for tfrz__chsmz, oulqh__uhk in zip(yrgx__teizt, col_names):
            yslo__ani += "    {} = df_ret['{}'].values\n".format(tfrz__chsmz,
                oulqh__uhk)
        yslo__ani += '  return ({},)\n'.format(', '.join(dhx__wqds for
            dhx__wqds in yrgx__teizt))
    if bodo.sql_access_method == 'multiple_access_nb_row_first':
        yslo__ani = 'def sql_reader_py(sql_request, conn):\n'
        if db_type == 'snowflake':
            klo__clvh = {}
            for cxrqe__mua, dboi__hexv in enumerate(col_typs):
                klo__clvh[f'col_{cxrqe__mua}_type'] = dboi__hexv
            yslo__ani += (
                f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n"
                )

            def is_nullable(typ):
                return bodo.utils.utils.is_array_typ(typ, False
                    ) and not isinstance(typ, types.Array)
            avaxm__gnb = [int(is_nullable(dboi__hexv)) for dboi__hexv in
                col_typs]
            yslo__ani += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(col_names)}, np.array({avaxm__gnb}, dtype=np.int32).ctypes)
"""
            yslo__ani += '  check_and_propagate_cpp_exception()\n'
            for cxrqe__mua, pame__uug in enumerate(yrgx__teizt):
                yslo__ani += f"""  {pame__uug} = info_to_array(info_from_table(out_table, {cxrqe__mua}), col_{cxrqe__mua}_type)
"""
            yslo__ani += '  delete_table(out_table)\n'
            yslo__ani += f'  ev.finalize()\n'
        else:
            yslo__ani += '  sqlalchemy_check()\n'
            if parallel:
                yslo__ani += '  rank = bodo.libs.distributed_api.get_rank()\n'
                if limit is not None:
                    yslo__ani += f'  nb_row = {limit}\n'
                else:
                    yslo__ani += '  with objmode(nb_row="int64"):\n'
                    yslo__ani += f'     if rank == {MPI_ROOT}:\n'
                    yslo__ani += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                    yslo__ani += (
                        '         frame = pd.read_sql(sql_cons, conn)\n')
                    yslo__ani += '         nb_row = frame.iat[0,0]\n'
                    yslo__ani += '     else:\n'
                    yslo__ani += '         nb_row = 0\n'
                    yslo__ani += '  nb_row = bcast_scalar(nb_row)\n'
                yslo__ani += '  with objmode({}):\n'.format(', '.join(
                    vzsyj__bbso))
                yslo__ani += """    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)
"""
                sgac__feb = escape_column_names(col_names, db_type,
                    converted_colnames)
                if db_type == 'oracle':
                    yslo__ani += f"""    sql_cons = 'select {sgac__feb} from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
                else:
                    yslo__ani += f"""    sql_cons = 'select {sgac__feb} from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
                yslo__ani += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            else:
                yslo__ani += '  with objmode({}):\n'.format(', '.join(
                    vzsyj__bbso))
                yslo__ani += '    df_ret = pd.read_sql(sql_request, conn)\n'
            for tfrz__chsmz, oulqh__uhk in zip(yrgx__teizt, col_names):
                yslo__ani += "    {} = df_ret['{}'].values\n".format(
                    tfrz__chsmz, oulqh__uhk)
        yslo__ani += '  return ({},)\n'.format(', '.join(dhx__wqds for
            dhx__wqds in yrgx__teizt))
    ktkf__nrah = {'bodo': bodo}
    if db_type == 'snowflake':
        ktkf__nrah.update(klo__clvh)
        ktkf__nrah.update({'np': np, 'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'snowflake_read':
            _snowflake_read, 'info_to_array': info_to_array,
            'info_from_table': info_from_table, 'delete_table': delete_table})
    else:
        ktkf__nrah.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar})
    mvyd__yfaon = {}
    exec(yslo__ani, ktkf__nrah, mvyd__yfaon)
    ijufd__wll = mvyd__yfaon['sql_reader_py']
    vpoi__cdx = numba.njit(ijufd__wll)
    compiled_funcs.append(vpoi__cdx)
    return vpoi__cdx


_snowflake_read = types.ExternalFunction('snowflake_read', table_type(types
    .voidptr, types.voidptr, types.boolean, types.int64, types.voidptr))
import llvmlite.binding as ll
from bodo.io import arrow_cpp
ll.add_symbol('snowflake_read', arrow_cpp.snowflake_read)
