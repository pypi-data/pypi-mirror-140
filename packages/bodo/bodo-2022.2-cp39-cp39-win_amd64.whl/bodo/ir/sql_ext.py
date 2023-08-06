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
    vkvnb__imo = []
    hhqjr__thce = []
    ofp__tcouc = []
    for jpvs__ghbn, rzrhv__kgw in enumerate(sql_node.out_vars):
        if rzrhv__kgw.name in lives:
            vkvnb__imo.append(sql_node.df_colnames[jpvs__ghbn])
            hhqjr__thce.append(sql_node.out_vars[jpvs__ghbn])
            ofp__tcouc.append(sql_node.out_types[jpvs__ghbn])
    sql_node.df_colnames = vkvnb__imo
    sql_node.out_vars = hhqjr__thce
    sql_node.out_types = ofp__tcouc
    if len(sql_node.out_vars) == 0:
        return None
    return sql_node


def sql_distributed_run(sql_node, array_dists, typemap, calltypes,
    typingctx, targetctx):
    parallel = False
    if array_dists is not None:
        parallel = True
        for ozr__fhc in sql_node.out_vars:
            if array_dists[ozr__fhc.name
                ] != distributed_pass.Distribution.OneD and array_dists[
                ozr__fhc.name] != distributed_pass.Distribution.OneD_Var:
                parallel = False
    otc__akuf = len(sql_node.out_vars)
    dgmq__rfts = ', '.join('arr' + str(jpvs__ghbn) for jpvs__ghbn in range(
        otc__akuf))
    lusx__crzoz, uebj__yvvd = bodo.ir.connector.generate_filter_map(sql_node
        .filters)
    pro__zggj = ', '.join(lusx__crzoz.values())
    btn__sjgvt = f'def sql_impl(sql_request, conn, {pro__zggj}):\n'
    if sql_node.filters:
        fxdxn__rmh = []
        for kepl__atne in sql_node.filters:
            ffr__mgzy = [' '.join(['(', joef__xhay[0], joef__xhay[1], '{' +
                lusx__crzoz[joef__xhay[2].name] + '}' if isinstance(
                joef__xhay[2], ir.Var) else joef__xhay[2], ')']) for
                joef__xhay in kepl__atne]
            fxdxn__rmh.append(' ( ' + ' AND '.join(ffr__mgzy) + ' ) ')
        equx__oxtk = ' WHERE ' + ' OR '.join(fxdxn__rmh)
        for jpvs__ghbn, cyyps__ohj in enumerate(lusx__crzoz.values()):
            btn__sjgvt += f'    {cyyps__ohj} = get_sql_literal({cyyps__ohj})\n'
        btn__sjgvt += f'    sql_request = f"{{sql_request}} {equx__oxtk}"\n'
    btn__sjgvt += '    ({},) = _sql_reader_py(sql_request, conn)\n'.format(
        dgmq__rfts)
    gfn__rem = {}
    exec(btn__sjgvt, {}, gfn__rem)
    fzy__cbn = gfn__rem['sql_impl']
    pxob__gpoze = _gen_sql_reader_py(sql_node.df_colnames, sql_node.
        out_types, typingctx, targetctx, sql_node.db_type, sql_node.limit,
        sql_node.converted_colnames, parallel)
    iatt__gmo = compile_to_numba_ir(fzy__cbn, {'_sql_reader_py':
        pxob__gpoze, 'bcast_scalar': bcast_scalar, 'bcast': bcast,
        'get_sql_literal': _get_snowflake_sql_literal}, typingctx=typingctx,
        targetctx=targetctx, arg_typs=(string_type, string_type) + tuple(
        typemap[ozr__fhc.name] for ozr__fhc in uebj__yvvd), typemap=typemap,
        calltypes=calltypes).blocks.popitem()[1]
    phve__beecj = escape_column_names(sql_node.df_colnames, sql_node.
        db_type, sql_node.converted_colnames)
    if sql_node.db_type == 'oracle':
        xhtui__ezu = ('SELECT ' + phve__beecj + ' FROM (' + sql_node.
            sql_request + ') TEMP')
    else:
        xhtui__ezu = ('SELECT ' + phve__beecj + ' FROM (' + sql_node.
            sql_request + ') as TEMP')
    replace_arg_nodes(iatt__gmo, [ir.Const(xhtui__ezu, sql_node.loc), ir.
        Const(sql_node.connection, sql_node.loc)] + uebj__yvvd)
    vya__kzbm = iatt__gmo.body[:-3]
    for jpvs__ghbn in range(len(sql_node.out_vars)):
        vya__kzbm[-len(sql_node.out_vars) + jpvs__ghbn
            ].target = sql_node.out_vars[jpvs__ghbn]
    return vya__kzbm


def escape_column_names(col_names, db_type, converted_colnames):
    if db_type in ('snowflake', 'oracle'):
        ude__aadiu = [(iayo__cncg.upper() if iayo__cncg in
            converted_colnames else iayo__cncg) for iayo__cncg in col_names]
        phve__beecj = ', '.join([f'"{iayo__cncg}"' for iayo__cncg in
            ude__aadiu])
    elif db_type == 'mysql' or db_type == 'mysql+pymysql':
        phve__beecj = ', '.join([f'`{iayo__cncg}`' for iayo__cncg in col_names]
            )
    else:
        phve__beecj = ', '.join([f'"{iayo__cncg}"' for iayo__cncg in col_names]
            )
    return phve__beecj


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def _get_snowflake_sql_literal(filter_value):
    irb__dxd = types.unliteral(filter_value)
    if irb__dxd == types.unicode_type:
        return lambda filter_value: f'$${filter_value}$$'
    elif isinstance(irb__dxd, (types.Integer, types.Float)
        ) or filter_value == types.bool_:
        return lambda filter_value: str(filter_value)
    elif irb__dxd == bodo.pd_timestamp_type:

        def impl(filter_value):
            lgcjk__ofaa = filter_value.nanosecond
            utua__rvgf = ''
            if lgcjk__ofaa < 10:
                utua__rvgf = '00'
            elif lgcjk__ofaa < 100:
                utua__rvgf = '0'
            return (
                f"timestamp '{filter_value.strftime('%Y-%m-%d %H:%M:%S.%f')}{utua__rvgf}{lgcjk__ofaa}'"
                )
        return impl
    elif irb__dxd == bodo.datetime_date_type:
        return (lambda filter_value:
            f"date '{filter_value.strftime('%Y-%m-%d')}'")
    else:
        raise BodoError(
            f'pd.read_sql(): Internal error, unsupported type {irb__dxd} used in filter pushdown.'
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
    except ImportError as xplw__forxs:
        rdu__ycits = (
            "Using URI string without sqlalchemy installed. sqlalchemy can be installed by calling 'conda install -c conda-forge sqlalchemy'."
            )
        raise BodoError(rdu__ycits)


def req_limit(sql_request):
    import re
    tsy__fxb = re.compile('LIMIT\\s+(\\d+)\\s*$', re.IGNORECASE)
    ydbpc__hnxpc = tsy__fxb.search(sql_request)
    if ydbpc__hnxpc:
        return int(ydbpc__hnxpc.group(1))
    else:
        return None


def _gen_sql_reader_py(col_names, col_typs, typingctx, targetctx, db_type,
    limit, converted_colnames, parallel):
    sqtz__hal = [sanitize_varname(syy__tpufe) for syy__tpufe in col_names]
    zqec__aikf = ["{}='{}'".format(spy__xpq, _get_dtype_str(vevrr__bmw)) for
        spy__xpq, vevrr__bmw in zip(sqtz__hal, col_typs)]
    if bodo.sql_access_method == 'multiple_access_by_block':
        btn__sjgvt = 'def sql_reader_py(sql_request,conn):\n'
        btn__sjgvt += '  sqlalchemy_check()\n'
        btn__sjgvt += '  rank = bodo.libs.distributed_api.get_rank()\n'
        btn__sjgvt += '  n_pes = bodo.libs.distributed_api.get_size()\n'
        btn__sjgvt += '  with objmode({}):\n'.format(', '.join(zqec__aikf))
        btn__sjgvt += '    list_df_block = []\n'
        btn__sjgvt += '    block_size = 50000\n'
        btn__sjgvt += '    iter = 0\n'
        btn__sjgvt += '    while(True):\n'
        btn__sjgvt += '      offset = (iter * n_pes + rank) * block_size\n'
        if db_type == 'oracle':
            btn__sjgvt += """      sql_cons = 'select * from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(block_size) + ' ROWS ONLY'
"""
        else:
            btn__sjgvt += """      sql_cons = 'select * from (' + sql_request + ') x LIMIT ' + str(block_size) + ' OFFSET ' + str(offset)
"""
        btn__sjgvt += '      df_block = pd.read_sql(sql_cons, conn)\n'
        btn__sjgvt += '      if df_block.size == 0:\n'
        btn__sjgvt += '        break\n'
        btn__sjgvt += '      list_df_block.append(df_block)\n'
        btn__sjgvt += '      iter += 1\n'
        btn__sjgvt += '    df_ret = pd.concat(list_df_block)\n'
        for spy__xpq, nftdw__bhxhw in zip(sqtz__hal, col_names):
            btn__sjgvt += "    {} = df_ret['{}'].values\n".format(spy__xpq,
                nftdw__bhxhw)
        btn__sjgvt += '  return ({},)\n'.format(', '.join(xwp__wimr for
            xwp__wimr in sqtz__hal))
    if bodo.sql_access_method == 'multiple_access_nb_row_first':
        btn__sjgvt = 'def sql_reader_py(sql_request, conn):\n'
        if db_type == 'snowflake':
            eeo__evddc = {}
            for jpvs__ghbn, tep__mgys in enumerate(col_typs):
                eeo__evddc[f'col_{jpvs__ghbn}_type'] = tep__mgys
            btn__sjgvt += (
                f"  ev = bodo.utils.tracing.Event('read_snowflake', {parallel})\n"
                )

            def is_nullable(typ):
                return bodo.utils.utils.is_array_typ(typ, False
                    ) and not isinstance(typ, types.Array)
            phbk__vyt = [int(is_nullable(tep__mgys)) for tep__mgys in col_typs]
            btn__sjgvt += f"""  out_table = snowflake_read(unicode_to_utf8(sql_request), unicode_to_utf8(conn), {parallel}, {len(col_names)}, np.array({phbk__vyt}, dtype=np.int32).ctypes)
"""
            btn__sjgvt += '  check_and_propagate_cpp_exception()\n'
            for jpvs__ghbn, hgmp__ybk in enumerate(sqtz__hal):
                btn__sjgvt += f"""  {hgmp__ybk} = info_to_array(info_from_table(out_table, {jpvs__ghbn}), col_{jpvs__ghbn}_type)
"""
            btn__sjgvt += '  delete_table(out_table)\n'
            btn__sjgvt += f'  ev.finalize()\n'
        else:
            btn__sjgvt += '  sqlalchemy_check()\n'
            if parallel:
                btn__sjgvt += '  rank = bodo.libs.distributed_api.get_rank()\n'
                if limit is not None:
                    btn__sjgvt += f'  nb_row = {limit}\n'
                else:
                    btn__sjgvt += '  with objmode(nb_row="int64"):\n'
                    btn__sjgvt += f'     if rank == {MPI_ROOT}:\n'
                    btn__sjgvt += """         sql_cons = 'select count(*) from (' + sql_request + ') x'
"""
                    btn__sjgvt += (
                        '         frame = pd.read_sql(sql_cons, conn)\n')
                    btn__sjgvt += '         nb_row = frame.iat[0,0]\n'
                    btn__sjgvt += '     else:\n'
                    btn__sjgvt += '         nb_row = 0\n'
                    btn__sjgvt += '  nb_row = bcast_scalar(nb_row)\n'
                btn__sjgvt += '  with objmode({}):\n'.format(', '.join(
                    zqec__aikf))
                btn__sjgvt += """    offset, limit = bodo.libs.distributed_api.get_start_count(nb_row)
"""
                phve__beecj = escape_column_names(col_names, db_type,
                    converted_colnames)
                if db_type == 'oracle':
                    btn__sjgvt += f"""    sql_cons = 'select {phve__beecj} from (' + sql_request + ') OFFSET ' + str(offset) + ' ROWS FETCH NEXT ' + str(limit) + ' ROWS ONLY'
"""
                else:
                    btn__sjgvt += f"""    sql_cons = 'select {phve__beecj} from (' + sql_request + ') x LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
"""
                btn__sjgvt += '    df_ret = pd.read_sql(sql_cons, conn)\n'
            else:
                btn__sjgvt += '  with objmode({}):\n'.format(', '.join(
                    zqec__aikf))
                btn__sjgvt += '    df_ret = pd.read_sql(sql_request, conn)\n'
            for spy__xpq, nftdw__bhxhw in zip(sqtz__hal, col_names):
                btn__sjgvt += "    {} = df_ret['{}'].values\n".format(spy__xpq,
                    nftdw__bhxhw)
        btn__sjgvt += '  return ({},)\n'.format(', '.join(xwp__wimr for
            xwp__wimr in sqtz__hal))
    gki__cmxka = {'bodo': bodo}
    if db_type == 'snowflake':
        gki__cmxka.update(eeo__evddc)
        gki__cmxka.update({'np': np, 'unicode_to_utf8': unicode_to_utf8,
            'check_and_propagate_cpp_exception':
            check_and_propagate_cpp_exception, 'snowflake_read':
            _snowflake_read, 'info_to_array': info_to_array,
            'info_from_table': info_from_table, 'delete_table': delete_table})
    else:
        gki__cmxka.update({'sqlalchemy_check': sqlalchemy_check, 'pd': pd,
            'objmode': objmode, 'bcast_scalar': bcast_scalar})
    gfn__rem = {}
    exec(btn__sjgvt, gki__cmxka, gfn__rem)
    pxob__gpoze = gfn__rem['sql_reader_py']
    ipygt__ioujm = numba.njit(pxob__gpoze)
    compiled_funcs.append(ipygt__ioujm)
    return ipygt__ioujm


_snowflake_read = types.ExternalFunction('snowflake_read', table_type(types
    .voidptr, types.voidptr, types.boolean, types.int64, types.voidptr))
import llvmlite.binding as ll
from bodo.io import arrow_cpp
ll.add_symbol('snowflake_read', arrow_cpp.snowflake_read)
