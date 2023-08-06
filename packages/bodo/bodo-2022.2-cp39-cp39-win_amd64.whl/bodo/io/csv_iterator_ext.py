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
        lgytl__mtf = (
            f'CSVIteratorType({df_type}, {out_colnames}, {out_types}, {usecols}, {sep}, {index_ind}, {index_arr_typ}, {index_name}, {escapechar})'
            )
        super(types.SimpleIteratorType, self).__init__(lgytl__mtf)
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
        clp__osikb = [('csv_reader', bodo.ir.connector.stream_reader_type),
            ('index', types.EphemeralPointer(types.uintp))]
        super(CSVIteratorModel, self).__init__(dmm, fe_type, clp__osikb)


@lower_builtin('getiter', CSVIteratorType)
def getiter_csv_iterator(context, builder, sig, args):
    aoo__wpf = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    gyrj__cxj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer()])
    sajq__hdlhp = cgutils.get_or_insert_function(builder.module, gyrj__cxj,
        name='initialize_csv_reader')
    builder.call(sajq__hdlhp, [aoo__wpf.csv_reader])
    builder.store(context.get_constant(types.uint64, 0), aoo__wpf.index)
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', CSVIteratorType)
@iternext_impl(RefType.NEW)
def iternext_csv_iterator(context, builder, sig, args, result):
    [hdqzd__iynt] = sig.args
    [roljk__oxl] = args
    aoo__wpf = cgutils.create_struct_proxy(hdqzd__iynt)(context, builder,
        value=roljk__oxl)
    gyrj__cxj = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer()])
    sajq__hdlhp = cgutils.get_or_insert_function(builder.module, gyrj__cxj,
        name='update_csv_reader')
    dzwbk__vhw = builder.call(sajq__hdlhp, [aoo__wpf.csv_reader])
    result.set_valid(dzwbk__vhw)
    with builder.if_then(dzwbk__vhw):
        ktj__fjne = builder.load(aoo__wpf.index)
        jivd__swjmo = types.Tuple([sig.return_type.first_type, types.int64])
        setrx__qtum = gen_read_csv_objmode(sig.args[0])
        zvw__cesa = signature(jivd__swjmo, bodo.ir.connector.
            stream_reader_type, types.int64)
        ruh__foxj = context.compile_internal(builder, setrx__qtum,
            zvw__cesa, [aoo__wpf.csv_reader, ktj__fjne])
        zow__sxmjy, naaj__udkd = cgutils.unpack_tuple(builder, ruh__foxj)
        uyxr__xbmd = builder.add(ktj__fjne, naaj__udkd, flags=['nsw'])
        builder.store(uyxr__xbmd, aoo__wpf.index)
        result.yield_(zow__sxmjy)


@intrinsic
def init_csv_iterator(typingctx, csv_reader, csv_iterator_typeref):

    def codegen(context, builder, signature, args):
        ftxv__gtbti = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        ftxv__gtbti.csv_reader = args[0]
        wbkc__mba = context.get_constant(types.uintp, 0)
        ftxv__gtbti.index = cgutils.alloca_once_value(builder, wbkc__mba)
        return ftxv__gtbti._getvalue()
    assert isinstance(csv_iterator_typeref, types.TypeRef
        ), 'Initializing a csv iterator requires a typeref'
    hlnxg__xacc = csv_iterator_typeref.instance_type
    sig = signature(hlnxg__xacc, csv_reader, csv_iterator_typeref)
    return sig, codegen


def gen_read_csv_objmode(csv_iterator_type):
    pqb__bxdou = 'def read_csv_objmode(f_reader):\n'
    zwv__vkru = [sanitize_varname(dllj__olq) for dllj__olq in
        csv_iterator_type._out_colnames]
    qhrfn__idp = ir_utils.next_label()
    ktf__cpj = globals()
    out_types = csv_iterator_type._out_types
    ktf__cpj[f'table_type_{qhrfn__idp}'] = TableType(tuple(out_types))
    ktf__cpj[f'idx_array_typ'] = csv_iterator_type._index_arr_typ
    fmoy__cvms = list(range(len(csv_iterator_type._usecols)))
    pqb__bxdou += _gen_read_csv_objmode(csv_iterator_type._out_colnames,
        zwv__vkru, out_types, csv_iterator_type._usecols, fmoy__cvms,
        csv_iterator_type._sep, csv_iterator_type._escapechar, qhrfn__idp,
        ktf__cpj, parallel=False, check_parallel_runtime=True,
        idx_col_index=csv_iterator_type._index_ind, idx_col_typ=
        csv_iterator_type._index_arr_typ)
    ffpft__ryc = bodo.ir.csv_ext._gen_parallel_flag_name(zwv__vkru)
    cuj__qyeu = ['T'] + (['idx_arr'] if csv_iterator_type._index_ind is not
        None else []) + [ffpft__ryc]
    pqb__bxdou += f"  return {', '.join(cuj__qyeu)}"
    ktf__cpj = globals()
    upb__ghlro = {}
    exec(pqb__bxdou, ktf__cpj, upb__ghlro)
    fpndo__fok = upb__ghlro['read_csv_objmode']
    fpic__nat = numba.njit(fpndo__fok)
    bodo.ir.csv_ext.compiled_funcs.append(fpic__nat)
    bys__csws = 'def read_func(reader, local_start):\n'
    bys__csws += f"  {', '.join(cuj__qyeu)} = objmode_func(reader)\n"
    index_ind = csv_iterator_type._index_ind
    if index_ind is None:
        bys__csws += f'  local_len = len(T)\n'
        bys__csws += '  total_size = local_len\n'
        bys__csws += f'  if ({ffpft__ryc}):\n'
        bys__csws += """    local_start = local_start + bodo.libs.distributed_api.dist_exscan(local_len, _op)
"""
        bys__csws += (
            '    total_size = bodo.libs.distributed_api.dist_reduce(local_len, _op)\n'
            )
        wkx__aps = (
            f'bodo.hiframes.pd_index_ext.init_range_index(local_start, local_start + local_len, 1, None)'
            )
    else:
        bys__csws += '  total_size = 0\n'
        wkx__aps = (
            f'bodo.utils.conversion.convert_to_index({cuj__qyeu[1]}, {csv_iterator_type._index_name!r})'
            )
    bys__csws += f"""  return (bodo.hiframes.pd_dataframe_ext.init_dataframe(({cuj__qyeu[0]},), {wkx__aps}, out_df_typ), total_size)
"""
    exec(bys__csws, {'bodo': bodo, 'objmode_func': fpic__nat, '_op': np.
        int32(bodo.libs.distributed_api.Reduce_Type.Sum.value),
        'out_df_typ': csv_iterator_type.yield_type}, upb__ghlro)
    return upb__ghlro['read_func']
