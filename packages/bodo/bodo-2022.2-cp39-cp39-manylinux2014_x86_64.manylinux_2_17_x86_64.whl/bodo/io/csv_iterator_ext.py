"""
Class information for DataFrame iterators returned by pd.read_csv. This is used
to handle situations in which pd.read_csv is used to return chunks with separate
read calls instead of just a single read.
"""
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, ir_utils, types
from numba.core.imputils import RefType, impl_ret_borrowed, iternext_impl
from numba.core.typing.templates import signature
from numba.extending import intrinsic, lower_builtin, models, register_model
import bodo
import bodo.ir.connector
import bodo.ir.csv_ext
from bodo import objmode
from bodo.hiframes.pd_dataframe_ext import DataFrameType
from bodo.hiframes.table import Table, TableType
from bodo.io import csv_cpp
from bodo.ir.csv_ext import _gen_read_csv_objmode, astype
from bodo.utils.utils import check_java_installation
from bodo.utils.utils import sanitize_varname
ll.add_symbol('update_csv_reader', csv_cpp.update_csv_reader)
ll.add_symbol('initialize_csv_reader', csv_cpp.initialize_csv_reader)


class CSVIteratorType(types.SimpleIteratorType):

    def __init__(self, df_type, out_colnames, out_types, usecols, sep,
        index_ind, index_arr_typ, index_name, escapechar):
        assert isinstance(df_type, DataFrameType
            ), 'CSVIterator must return a DataFrame'
        tws__dmn = (
            f'CSVIteratorType({df_type}, {out_colnames}, {out_types}, {usecols}, {sep}, {index_ind}, {index_arr_typ}, {index_name}, {escapechar})'
            )
        super(types.SimpleIteratorType, self).__init__(tws__dmn)
        self._yield_type = df_type
        self._out_colnames = out_colnames
        self._out_types = out_types
        self._usecols = usecols
        self._sep = sep
        self._index_ind = index_ind
        self._index_arr_typ = index_arr_typ
        self._index_name = index_name
        self._escapechar = escapechar

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(CSVIteratorType)
class CSVIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zhqz__pgg = [('csv_reader', bodo.ir.connector.stream_reader_type),
            ('index', types.EphemeralPointer(types.uintp))]
        super(CSVIteratorModel, self).__init__(dmm, fe_type, zhqz__pgg)


@lower_builtin('getiter', CSVIteratorType)
def getiter_csv_iterator(context, builder, sig, args):
    quumc__wds = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    lsfd__ukltc = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer()])
    swox__tep = cgutils.get_or_insert_function(builder.module, lsfd__ukltc,
        name='initialize_csv_reader')
    builder.call(swox__tep, [quumc__wds.csv_reader])
    builder.store(context.get_constant(types.uint64, 0), quumc__wds.index)
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', CSVIteratorType)
@iternext_impl(RefType.NEW)
def iternext_csv_iterator(context, builder, sig, args, result):
    [xrxy__jfi] = sig.args
    [oys__xbqj] = args
    quumc__wds = cgutils.create_struct_proxy(xrxy__jfi)(context, builder,
        value=oys__xbqj)
    lsfd__ukltc = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer()])
    swox__tep = cgutils.get_or_insert_function(builder.module, lsfd__ukltc,
        name='update_csv_reader')
    rxep__jzp = builder.call(swox__tep, [quumc__wds.csv_reader])
    result.set_valid(rxep__jzp)
    with builder.if_then(rxep__jzp):
        lqsaj__bqb = builder.load(quumc__wds.index)
        exro__wga = types.Tuple([sig.return_type.first_type, types.int64])
        zjtt__etgu = gen_read_csv_objmode(sig.args[0])
        noeh__wbau = signature(exro__wga, bodo.ir.connector.
            stream_reader_type, types.int64)
        vyjn__rxzzu = context.compile_internal(builder, zjtt__etgu,
            noeh__wbau, [quumc__wds.csv_reader, lqsaj__bqb])
        orq__uodsd, rjaq__idz = cgutils.unpack_tuple(builder, vyjn__rxzzu)
        zqe__dse = builder.add(lqsaj__bqb, rjaq__idz, flags=['nsw'])
        builder.store(zqe__dse, quumc__wds.index)
        result.yield_(orq__uodsd)


@intrinsic
def init_csv_iterator(typingctx, csv_reader, csv_iterator_typeref):

    def codegen(context, builder, signature, args):
        totyc__fmb = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        totyc__fmb.csv_reader = args[0]
        keg__lpn = context.get_constant(types.uintp, 0)
        totyc__fmb.index = cgutils.alloca_once_value(builder, keg__lpn)
        return totyc__fmb._getvalue()
    assert isinstance(csv_iterator_typeref, types.TypeRef
        ), 'Initializing a csv iterator requires a typeref'
    yyc__yzgj = csv_iterator_typeref.instance_type
    sig = signature(yyc__yzgj, csv_reader, csv_iterator_typeref)
    return sig, codegen


def gen_read_csv_objmode(csv_iterator_type):
    kifeh__azz = 'def read_csv_objmode(f_reader):\n'
    qydm__fiqlr = [sanitize_varname(heat__hijkj) for heat__hijkj in
        csv_iterator_type._out_colnames]
    oqcs__ceyve = ir_utils.next_label()
    jpcrr__nfxwq = globals()
    out_types = csv_iterator_type._out_types
    jpcrr__nfxwq[f'table_type_{oqcs__ceyve}'] = TableType(tuple(out_types))
    jpcrr__nfxwq[f'idx_array_typ'] = csv_iterator_type._index_arr_typ
    swqf__hptay = list(range(len(csv_iterator_type._usecols)))
    kifeh__azz += _gen_read_csv_objmode(csv_iterator_type._out_colnames,
        qydm__fiqlr, out_types, csv_iterator_type._usecols, swqf__hptay,
        csv_iterator_type._sep, csv_iterator_type._escapechar, oqcs__ceyve,
        jpcrr__nfxwq, parallel=False, check_parallel_runtime=True,
        idx_col_index=csv_iterator_type._index_ind, idx_col_typ=
        csv_iterator_type._index_arr_typ)
    frqpt__vxf = bodo.ir.csv_ext._gen_parallel_flag_name(qydm__fiqlr)
    lqag__kscwi = ['T'] + (['idx_arr'] if csv_iterator_type._index_ind is not
        None else []) + [frqpt__vxf]
    kifeh__azz += f"  return {', '.join(lqag__kscwi)}"
    jpcrr__nfxwq = globals()
    wefcs__doo = {}
    exec(kifeh__azz, jpcrr__nfxwq, wefcs__doo)
    dfe__uzeq = wefcs__doo['read_csv_objmode']
    ywnjk__edkk = numba.njit(dfe__uzeq)
    bodo.ir.csv_ext.compiled_funcs.append(ywnjk__edkk)
    jywkp__mezgp = 'def read_func(reader, local_start):\n'
    jywkp__mezgp += f"  {', '.join(lqag__kscwi)} = objmode_func(reader)\n"
    index_ind = csv_iterator_type._index_ind
    if index_ind is None:
        jywkp__mezgp += f'  local_len = len(T)\n'
        jywkp__mezgp += '  total_size = local_len\n'
        jywkp__mezgp += f'  if ({frqpt__vxf}):\n'
        jywkp__mezgp += """    local_start = local_start + bodo.libs.distributed_api.dist_exscan(local_len, _op)
"""
        jywkp__mezgp += (
            '    total_size = bodo.libs.distributed_api.dist_reduce(local_len, _op)\n'
            )
        mjeau__equac = (
            f'bodo.hiframes.pd_index_ext.init_range_index(local_start, local_start + local_len, 1, None)'
            )
    else:
        jywkp__mezgp += '  total_size = 0\n'
        mjeau__equac = (
            f'bodo.utils.conversion.convert_to_index({lqag__kscwi[1]}, {csv_iterator_type._index_name!r})'
            )
    jywkp__mezgp += f"""  return (bodo.hiframes.pd_dataframe_ext.init_dataframe(({lqag__kscwi[0]},), {mjeau__equac}, out_df_typ), total_size)
"""
    exec(jywkp__mezgp, {'bodo': bodo, 'objmode_func': ywnjk__edkk, '_op':
        np.int32(bodo.libs.distributed_api.Reduce_Type.Sum.value),
        'out_df_typ': csv_iterator_type.yield_type}, wefcs__doo)
    return wefcs__doo['read_func']
