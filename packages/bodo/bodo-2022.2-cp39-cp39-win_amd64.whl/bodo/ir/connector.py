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
    emt__tpnao = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    pinf__jhf = []
    for paem__plsbj in node.out_vars:
        typ = typemap[paem__plsbj.name]
        if typ == types.none:
            continue
        hfldq__lun = array_analysis._gen_shape_call(equiv_set, paem__plsbj,
            typ.ndim, None, emt__tpnao)
        equiv_set.insert_equiv(paem__plsbj, hfldq__lun)
        pinf__jhf.append(hfldq__lun[0])
        equiv_set.define(paem__plsbj, set())
    if len(pinf__jhf) > 1:
        equiv_set.insert_equiv(*pinf__jhf)
    return [], emt__tpnao


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and node.limit is not None:
        atmw__ojws = Distribution.OneD_Var
    else:
        atmw__ojws = Distribution.OneD
    for nwe__xynd in node.out_vars:
        if nwe__xynd.name in array_dists:
            atmw__ojws = Distribution(min(atmw__ojws.value, array_dists[
                nwe__xynd.name].value))
    for nwe__xynd in node.out_vars:
        array_dists[nwe__xynd.name] = atmw__ojws


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
    for paem__plsbj, typ in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(paem__plsbj.name, typ, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    brku__utn = []
    for paem__plsbj in node.out_vars:
        xas__sotal = visit_vars_inner(paem__plsbj, callback, cbdata)
        brku__utn.append(xas__sotal)
    node.out_vars = brku__utn
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for abt__ijj in node.filters:
            for yksr__vgpe in range(len(abt__ijj)):
                val = abt__ijj[yksr__vgpe]
                abt__ijj[yksr__vgpe] = val[0], val[1], visit_vars_inner(val
                    [2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({nwe__xynd.name for nwe__xynd in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for cwuf__imzeb in node.filters:
            for nwe__xynd in cwuf__imzeb:
                if isinstance(nwe__xynd[2], ir.Var):
                    use_set.add(nwe__xynd[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    niv__mak = set(nwe__xynd.name for nwe__xynd in node.out_vars)
    return set(), niv__mak


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    brku__utn = []
    for paem__plsbj in node.out_vars:
        xas__sotal = replace_vars_inner(paem__plsbj, var_dict)
        brku__utn.append(xas__sotal)
    node.out_vars = brku__utn
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for abt__ijj in node.filters:
            for yksr__vgpe in range(len(abt__ijj)):
                val = abt__ijj[yksr__vgpe]
                abt__ijj[yksr__vgpe] = val[0], val[1], replace_vars_inner(val
                    [2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for paem__plsbj in node.out_vars:
        bpkm__zwu = definitions[paem__plsbj.name]
        if node not in bpkm__zwu:
            bpkm__zwu.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        rjkr__tbht = []
        nzlug__ehj = [nwe__xynd[2] for cwuf__imzeb in filters for nwe__xynd in
            cwuf__imzeb]
        avg__wsk = set()
        for otut__fipfg in nzlug__ehj:
            if isinstance(otut__fipfg, ir.Var):
                if otut__fipfg.name not in avg__wsk:
                    rjkr__tbht.append(otut__fipfg)
                avg__wsk.add(otut__fipfg.name)
        return {nwe__xynd.name: f'f{yksr__vgpe}' for yksr__vgpe, nwe__xynd in
            enumerate(rjkr__tbht)}, rjkr__tbht
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
    gwwc__qyjfn = len(used_columns)
    for yksr__vgpe in range(len(used_columns) - 1, -1, -1):
        if used_columns[yksr__vgpe] < num_columns:
            break
        gwwc__qyjfn = yksr__vgpe
    return used_columns[:gwwc__qyjfn]
