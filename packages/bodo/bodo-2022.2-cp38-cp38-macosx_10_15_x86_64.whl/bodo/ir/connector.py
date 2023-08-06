"""
Common IR extension functions for connectors such as CSV, Parquet and JSON readers.
"""
from collections import defaultdict
import numba
from numba.core import ir, types
from numba.core.ir_utils import replace_vars_inner, visit_vars_inner
from numba.extending import box, models, register_model
from bodo.hiframes.table import TableType
from bodo.transforms.distributed_analysis import Distribution
from bodo.utils.utils import debug_prints


def connector_array_analysis(node, equiv_set, typemap, array_analysis):
    ckhnr__rgbk = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    nmnwq__tifq = []
    for dxv__sak in node.out_vars:
        typ = typemap[dxv__sak.name]
        if typ == types.none:
            continue
        bwp__wrh = array_analysis._gen_shape_call(equiv_set, dxv__sak, typ.
            ndim, None, ckhnr__rgbk)
        equiv_set.insert_equiv(dxv__sak, bwp__wrh)
        nmnwq__tifq.append(bwp__wrh[0])
        equiv_set.define(dxv__sak, set())
    if len(nmnwq__tifq) > 1:
        equiv_set.insert_equiv(*nmnwq__tifq)
    return [], ckhnr__rgbk


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and node.limit is not None:
        xtyn__jyhz = Distribution.OneD_Var
    else:
        xtyn__jyhz = Distribution.OneD
    for itlt__vhqrv in node.out_vars:
        if itlt__vhqrv.name in array_dists:
            xtyn__jyhz = Distribution(min(xtyn__jyhz.value, array_dists[
                itlt__vhqrv.name].value))
    for itlt__vhqrv in node.out_vars:
        array_dists[itlt__vhqrv.name] = xtyn__jyhz


def connector_typeinfer(node, typeinferer):
    if node.connector_typ == 'csv':
        if node.chunksize is not None:
            typeinferer.lock_type(node.out_vars[0].name, node.out_types[0],
                loc=node.loc)
        else:
            typeinferer.lock_type(node.out_vars[0].name, TableType(tuple(
                node.out_types)), loc=node.loc)
            typeinferer.lock_type(node.out_vars[1].name, node.
                index_column_typ, loc=node.loc)
        return
    if node.connector_typ == 'parquet':
        typeinferer.lock_type(node.out_vars[0].name, TableType(tuple(node.
            out_types)), loc=node.loc)
        typeinferer.lock_type(node.out_vars[1].name, node.index_column_type,
            loc=node.loc)
        return
    for dxv__sak, typ in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(dxv__sak.name, typ, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    qtsj__aodhi = []
    for dxv__sak in node.out_vars:
        xpz__ctft = visit_vars_inner(dxv__sak, callback, cbdata)
        qtsj__aodhi.append(xpz__ctft)
    node.out_vars = qtsj__aodhi
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for uuh__kzc in node.filters:
            for ocs__xmsc in range(len(uuh__kzc)):
                val = uuh__kzc[ocs__xmsc]
                uuh__kzc[ocs__xmsc] = val[0], val[1], visit_vars_inner(val[
                    2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({itlt__vhqrv.name for itlt__vhqrv in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for turvj__jauz in node.filters:
            for itlt__vhqrv in turvj__jauz:
                if isinstance(itlt__vhqrv[2], ir.Var):
                    use_set.add(itlt__vhqrv[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    akj__xkcn = set(itlt__vhqrv.name for itlt__vhqrv in node.out_vars)
    return set(), akj__xkcn


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    qtsj__aodhi = []
    for dxv__sak in node.out_vars:
        xpz__ctft = replace_vars_inner(dxv__sak, var_dict)
        qtsj__aodhi.append(xpz__ctft)
    node.out_vars = qtsj__aodhi
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for uuh__kzc in node.filters:
            for ocs__xmsc in range(len(uuh__kzc)):
                val = uuh__kzc[ocs__xmsc]
                uuh__kzc[ocs__xmsc] = val[0], val[1], replace_vars_inner(val
                    [2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for dxv__sak in node.out_vars:
        mhs__ebqj = definitions[dxv__sak.name]
        if node not in mhs__ebqj:
            mhs__ebqj.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        pnvw__rddzg = []
        wmpx__xpoh = [itlt__vhqrv[2] for turvj__jauz in filters for
            itlt__vhqrv in turvj__jauz]
        gnuo__doxz = set()
        for dwdf__oxzv in wmpx__xpoh:
            if isinstance(dwdf__oxzv, ir.Var):
                if dwdf__oxzv.name not in gnuo__doxz:
                    pnvw__rddzg.append(dwdf__oxzv)
                gnuo__doxz.add(dwdf__oxzv.name)
        return {itlt__vhqrv.name: f'f{ocs__xmsc}' for ocs__xmsc,
            itlt__vhqrv in enumerate(pnvw__rddzg)}, pnvw__rddzg
    else:
        return {}, []


class StreamReaderType(types.Opaque):

    def __init__(self):
        super(StreamReaderType, self).__init__(name='StreamReaderType')


stream_reader_type = StreamReaderType()
register_model(StreamReaderType)(models.OpaqueModel)


@box(StreamReaderType)
def box_stream_reader(typ, val, c):
    c.pyapi.incref(val)
    return val


def trim_extra_used_columns(used_columns, num_columns):
    usi__fxrug = len(used_columns)
    for ocs__xmsc in range(len(used_columns) - 1, -1, -1):
        if used_columns[ocs__xmsc] < num_columns:
            break
        usi__fxrug = ocs__xmsc
    return used_columns[:usi__fxrug]
