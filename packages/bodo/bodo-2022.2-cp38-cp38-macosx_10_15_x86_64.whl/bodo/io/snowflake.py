from urllib.parse import parse_qsl, urlparse
import snowflake.connector
import bodo
from bodo.utils import tracing


def get_connection_params(conn_str):
    import json
    ztep__zvt = urlparse(conn_str)
    usbk__mkjoz = {}
    if ztep__zvt.username:
        usbk__mkjoz['user'] = ztep__zvt.username
    if ztep__zvt.password:
        usbk__mkjoz['password'] = ztep__zvt.password
    if ztep__zvt.hostname:
        usbk__mkjoz['account'] = ztep__zvt.hostname
    if ztep__zvt.port:
        usbk__mkjoz['port'] = ztep__zvt.port
    if ztep__zvt.path:
        zuj__oba = ztep__zvt.path
        if zuj__oba.startswith('/'):
            zuj__oba = zuj__oba[1:]
        zczeo__sihx, schema = zuj__oba.split('/')
        usbk__mkjoz['database'] = zczeo__sihx
        if schema:
            usbk__mkjoz['schema'] = schema
    if ztep__zvt.query:
        for rwka__iyu, pdo__szfq in parse_qsl(ztep__zvt.query):
            usbk__mkjoz[rwka__iyu] = pdo__szfq
            if rwka__iyu == 'session_parameters':
                usbk__mkjoz[rwka__iyu] = json.loads(pdo__szfq)
    usbk__mkjoz['application'] = 'bodo'
    return usbk__mkjoz


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for vrgt__ifefz in batches:
            vrgt__ifefz._bodo_num_rows = vrgt__ifefz.rowcount
            self._bodo_total_rows += vrgt__ifefz._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    ajiky__yreen = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    vjb__xpb = MPI.COMM_WORLD
    iszaj__sjycq = tracing.Event('snowflake_connect', is_parallel=False)
    hnh__jvsx = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**hnh__jvsx)
    iszaj__sjycq.finalize()
    if bodo.get_rank() == 0:
        tat__lhfng = conn.cursor()
        lkv__odxi = tracing.Event('get_schema', is_parallel=False)
        trt__nsor = f'select * from ({query}) x LIMIT {100}'
        schema = tat__lhfng.execute(trt__nsor).fetch_arrow_all().schema
        lkv__odxi.finalize()
        cqg__kbqg = tracing.Event('execute_query', is_parallel=False)
        tat__lhfng.execute(query)
        cqg__kbqg.finalize()
        batches = tat__lhfng.get_result_batches()
        vjb__xpb.bcast((batches, schema))
    else:
        batches, schema = vjb__xpb.bcast(None)
    unbli__avol = SnowflakeDataset(batches, schema, conn)
    ajiky__yreen.finalize()
    return unbli__avol
