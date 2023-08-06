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
    ckqv__meuuz = []
    assert len(node.out_vars) > 0, 'empty {} in array analysis'.format(node
        .connector_typ)
    if node.connector_typ == 'csv' and node.chunksize is not None:
        return [], []
    avfsj__tvtj = []
    for pbc__cchzv in node.out_vars:
        typ = typemap[pbc__cchzv.name]
        if typ == types.none:
            continue
        grvyq__plnrp = array_analysis._gen_shape_call(equiv_set, pbc__cchzv,
            typ.ndim, None, ckqv__meuuz)
        equiv_set.insert_equiv(pbc__cchzv, grvyq__plnrp)
        avfsj__tvtj.append(grvyq__plnrp[0])
        equiv_set.define(pbc__cchzv, set())
    if len(avfsj__tvtj) > 1:
        equiv_set.insert_equiv(*avfsj__tvtj)
    return [], ckqv__meuuz


def connector_distributed_analysis(node, array_dists):
    from bodo.ir.sql_ext import SqlReader
    if isinstance(node, SqlReader) and node.limit is not None:
        imng__hgn = Distribution.OneD_Var
    else:
        imng__hgn = Distribution.OneD
    for hya__hghgm in node.out_vars:
        if hya__hghgm.name in array_dists:
            imng__hgn = Distribution(min(imng__hgn.value, array_dists[
                hya__hghgm.name].value))
    for hya__hghgm in node.out_vars:
        array_dists[hya__hghgm.name] = imng__hgn


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
    for pbc__cchzv, typ in zip(node.out_vars, node.out_types):
        typeinferer.lock_type(pbc__cchzv.name, typ, loc=node.loc)


def visit_vars_connector(node, callback, cbdata):
    if debug_prints():
        print('visiting {} vars for:'.format(node.connector_typ), node)
        print('cbdata: ', sorted(cbdata.items()))
    zjpz__rup = []
    for pbc__cchzv in node.out_vars:
        lskep__rkz = visit_vars_inner(pbc__cchzv, callback, cbdata)
        zjpz__rup.append(lskep__rkz)
    node.out_vars = zjpz__rup
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = visit_vars_inner(node.file_name, callback, cbdata)
    if node.connector_typ == 'csv':
        node.nrows = visit_vars_inner(node.nrows, callback, cbdata)
        node.skiprows = visit_vars_inner(node.skiprows, callback, cbdata)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for fkqpk__qur in node.filters:
            for zhoi__whje in range(len(fkqpk__qur)):
                val = fkqpk__qur[zhoi__whje]
                fkqpk__qur[zhoi__whje] = val[0], val[1], visit_vars_inner(val
                    [2], callback, cbdata)


def connector_usedefs(node, use_set=None, def_set=None):
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    def_set.update({hya__hghgm.name for hya__hghgm in node.out_vars})
    if node.connector_typ in ('csv', 'parquet', 'json'):
        use_set.add(node.file_name.name)
    if node.connector_typ == 'csv':
        if isinstance(node.nrows, numba.core.ir.Var):
            use_set.add(node.nrows.name)
        if isinstance(node.skiprows, numba.core.ir.Var):
            use_set.add(node.skiprows.name)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for ptmm__oliv in node.filters:
            for hya__hghgm in ptmm__oliv:
                if isinstance(hya__hghgm[2], ir.Var):
                    use_set.add(hya__hghgm[2].name)
    return numba.core.analysis._use_defs_result(usemap=use_set, defmap=def_set)


def get_copies_connector(node, typemap):
    neq__rqz = set(hya__hghgm.name for hya__hghgm in node.out_vars)
    return set(), neq__rqz


def apply_copies_connector(node, var_dict, name_var_table, typemap,
    calltypes, save_copies):
    zjpz__rup = []
    for pbc__cchzv in node.out_vars:
        lskep__rkz = replace_vars_inner(pbc__cchzv, var_dict)
        zjpz__rup.append(lskep__rkz)
    node.out_vars = zjpz__rup
    if node.connector_typ in ('csv', 'parquet', 'json'):
        node.file_name = replace_vars_inner(node.file_name, var_dict)
    if node.connector_typ in ('parquet', 'sql') and node.filters:
        for fkqpk__qur in node.filters:
            for zhoi__whje in range(len(fkqpk__qur)):
                val = fkqpk__qur[zhoi__whje]
                fkqpk__qur[zhoi__whje] = val[0], val[1], replace_vars_inner(val
                    [2], var_dict)
    if node.connector_typ == 'csv':
        node.nrows = replace_vars_inner(node.nrows, var_dict)
        node.skiprows = replace_vars_inner(node.skiprows, var_dict)


def build_connector_definitions(node, definitions=None):
    if definitions is None:
        definitions = defaultdict(list)
    for pbc__cchzv in node.out_vars:
        wgh__pwp = definitions[pbc__cchzv.name]
        if node not in wgh__pwp:
            wgh__pwp.append(node)
    return definitions


def generate_filter_map(filters):
    if filters:
        lqjq__wwnc = []
        pqwx__btkhu = [hya__hghgm[2] for ptmm__oliv in filters for
            hya__hghgm in ptmm__oliv]
        gek__itos = set()
        for dhr__uev in pqwx__btkhu:
            if isinstance(dhr__uev, ir.Var):
                if dhr__uev.name not in gek__itos:
                    lqjq__wwnc.append(dhr__uev)
                gek__itos.add(dhr__uev.name)
        return {hya__hghgm.name: f'f{zhoi__whje}' for zhoi__whje,
            hya__hghgm in enumerate(lqjq__wwnc)}, lqjq__wwnc
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
    tmc__nsgbs = len(used_columns)
    for zhoi__whje in range(len(used_columns) - 1, -1, -1):
        if used_columns[zhoi__whje] < num_columns:
            break
        tmc__nsgbs = zhoi__whje
    return used_columns[:tmc__nsgbs]
