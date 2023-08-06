from urllib.parse import parse_qsl, urlparse
import snowflake.connector
import bodo
from bodo.utils import tracing


def get_connection_params(conn_str):
    import json
    hkkjy__fjge = urlparse(conn_str)
    tquk__zqe = {}
    if hkkjy__fjge.username:
        tquk__zqe['user'] = hkkjy__fjge.username
    if hkkjy__fjge.password:
        tquk__zqe['password'] = hkkjy__fjge.password
    if hkkjy__fjge.hostname:
        tquk__zqe['account'] = hkkjy__fjge.hostname
    if hkkjy__fjge.port:
        tquk__zqe['port'] = hkkjy__fjge.port
    if hkkjy__fjge.path:
        cied__xlj = hkkjy__fjge.path
        if cied__xlj.startswith('/'):
            cied__xlj = cied__xlj[1:]
        loca__cal, schema = cied__xlj.split('/')
        tquk__zqe['database'] = loca__cal
        if schema:
            tquk__zqe['schema'] = schema
    if hkkjy__fjge.query:
        for izesr__ebb, yplxn__ksqb in parse_qsl(hkkjy__fjge.query):
            tquk__zqe[izesr__ebb] = yplxn__ksqb
            if izesr__ebb == 'session_parameters':
                tquk__zqe[izesr__ebb] = json.loads(yplxn__ksqb)
    tquk__zqe['application'] = 'bodo'
    return tquk__zqe


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for akfln__ztvu in batches:
            akfln__ztvu._bodo_num_rows = akfln__ztvu.rowcount
            self._bodo_total_rows += akfln__ztvu._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    dwg__muu = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    jgyc__wcl = MPI.COMM_WORLD
    yok__klzzl = tracing.Event('snowflake_connect', is_parallel=False)
    labbj__feigm = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**labbj__feigm)
    yok__klzzl.finalize()
    if bodo.get_rank() == 0:
        wdc__jps = conn.cursor()
        uba__tywtg = tracing.Event('get_schema', is_parallel=False)
        pyl__aofi = f'select * from ({query}) x LIMIT {100}'
        schema = wdc__jps.execute(pyl__aofi).fetch_arrow_all().schema
        uba__tywtg.finalize()
        wcb__xgbc = tracing.Event('execute_query', is_parallel=False)
        wdc__jps.execute(query)
        wcb__xgbc.finalize()
        batches = wdc__jps.get_result_batches()
        jgyc__wcl.bcast((batches, schema))
    else:
        batches, schema = jgyc__wcl.bcast(None)
    cmf__pxem = SnowflakeDataset(batches, schema, conn)
    dwg__muu.finalize()
    return cmf__pxem
