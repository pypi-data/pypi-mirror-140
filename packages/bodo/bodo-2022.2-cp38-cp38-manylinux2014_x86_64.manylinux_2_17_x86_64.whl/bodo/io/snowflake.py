from urllib.parse import parse_qsl, urlparse
import snowflake.connector
import bodo
from bodo.utils import tracing


def get_connection_params(conn_str):
    import json
    bhnp__hqdoh = urlparse(conn_str)
    fsh__vvkpy = {}
    if bhnp__hqdoh.username:
        fsh__vvkpy['user'] = bhnp__hqdoh.username
    if bhnp__hqdoh.password:
        fsh__vvkpy['password'] = bhnp__hqdoh.password
    if bhnp__hqdoh.hostname:
        fsh__vvkpy['account'] = bhnp__hqdoh.hostname
    if bhnp__hqdoh.port:
        fsh__vvkpy['port'] = bhnp__hqdoh.port
    if bhnp__hqdoh.path:
        giaw__doi = bhnp__hqdoh.path
        if giaw__doi.startswith('/'):
            giaw__doi = giaw__doi[1:]
        hvl__lohg, schema = giaw__doi.split('/')
        fsh__vvkpy['database'] = hvl__lohg
        if schema:
            fsh__vvkpy['schema'] = schema
    if bhnp__hqdoh.query:
        for kqje__gzwl, hdqnd__apd in parse_qsl(bhnp__hqdoh.query):
            fsh__vvkpy[kqje__gzwl] = hdqnd__apd
            if kqje__gzwl == 'session_parameters':
                fsh__vvkpy[kqje__gzwl] = json.loads(hdqnd__apd)
    fsh__vvkpy['application'] = 'bodo'
    return fsh__vvkpy


class SnowflakeDataset(object):

    def __init__(self, batches, schema, conn):
        self.pieces = batches
        self._bodo_total_rows = 0
        for bweb__depen in batches:
            bweb__depen._bodo_num_rows = bweb__depen.rowcount
            self._bodo_total_rows += bweb__depen._bodo_num_rows
        self.schema = schema
        self.conn = conn


def get_dataset(query, conn_str):
    bruq__mod = tracing.Event('get_snowflake_dataset')
    from mpi4py import MPI
    qli__rwu = MPI.COMM_WORLD
    syygi__gdvz = tracing.Event('snowflake_connect', is_parallel=False)
    kwo__uhna = get_connection_params(conn_str)
    conn = snowflake.connector.connect(**kwo__uhna)
    syygi__gdvz.finalize()
    if bodo.get_rank() == 0:
        zof__vsc = conn.cursor()
        kwsts__ynl = tracing.Event('get_schema', is_parallel=False)
        sxxd__rzdo = f'select * from ({query}) x LIMIT {100}'
        schema = zof__vsc.execute(sxxd__rzdo).fetch_arrow_all().schema
        kwsts__ynl.finalize()
        scsx__qxu = tracing.Event('execute_query', is_parallel=False)
        zof__vsc.execute(query)
        scsx__qxu.finalize()
        batches = zof__vsc.get_result_batches()
        qli__rwu.bcast((batches, schema))
    else:
        batches, schema = qli__rwu.bcast(None)
    xedk__cqf = SnowflakeDataset(batches, schema, conn)
    bruq__mod.finalize()
    return xedk__cqf
