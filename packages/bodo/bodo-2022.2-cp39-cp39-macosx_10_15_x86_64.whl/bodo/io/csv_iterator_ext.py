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
        igvg__ykgf = (
            f'CSVIteratorType({df_type}, {out_colnames}, {out_types}, {usecols}, {sep}, {index_ind}, {index_arr_typ}, {index_name}, {escapechar})'
            )
        super(types.SimpleIteratorType, self).__init__(igvg__ykgf)
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
        kvbqa__lbl = [('csv_reader', bodo.ir.connector.stream_reader_type),
            ('index', types.EphemeralPointer(types.uintp))]
        super(CSVIteratorModel, self).__init__(dmm, fe_type, kvbqa__lbl)


@lower_builtin('getiter', CSVIteratorType)
def getiter_csv_iterator(context, builder, sig, args):
    fyzo__bsvjo = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        value=args[0])
    rma__hxnpg = lir.FunctionType(lir.VoidType(), [lir.IntType(8).as_pointer()]
        )
    vfeae__fdozj = cgutils.get_or_insert_function(builder.module,
        rma__hxnpg, name='initialize_csv_reader')
    builder.call(vfeae__fdozj, [fyzo__bsvjo.csv_reader])
    builder.store(context.get_constant(types.uint64, 0), fyzo__bsvjo.index)
    return impl_ret_borrowed(context, builder, sig.return_type, args[0])


@lower_builtin('iternext', CSVIteratorType)
@iternext_impl(RefType.NEW)
def iternext_csv_iterator(context, builder, sig, args, result):
    [iaa__ukqq] = sig.args
    [zct__ouzw] = args
    fyzo__bsvjo = cgutils.create_struct_proxy(iaa__ukqq)(context, builder,
        value=zct__ouzw)
    rma__hxnpg = lir.FunctionType(lir.IntType(1), [lir.IntType(8).as_pointer()]
        )
    vfeae__fdozj = cgutils.get_or_insert_function(builder.module,
        rma__hxnpg, name='update_csv_reader')
    ywdc__yrpb = builder.call(vfeae__fdozj, [fyzo__bsvjo.csv_reader])
    result.set_valid(ywdc__yrpb)
    with builder.if_then(ywdc__yrpb):
        phr__lazm = builder.load(fyzo__bsvjo.index)
        cjz__voyx = types.Tuple([sig.return_type.first_type, types.int64])
        agnz__kezm = gen_read_csv_objmode(sig.args[0])
        icfgi__izhw = signature(cjz__voyx, bodo.ir.connector.
            stream_reader_type, types.int64)
        aqmt__alty = context.compile_internal(builder, agnz__kezm,
            icfgi__izhw, [fyzo__bsvjo.csv_reader, phr__lazm])
        vjym__vcnac, rtvmu__rfy = cgutils.unpack_tuple(builder, aqmt__alty)
        nwm__keru = builder.add(phr__lazm, rtvmu__rfy, flags=['nsw'])
        builder.store(nwm__keru, fyzo__bsvjo.index)
        result.yield_(vjym__vcnac)


@intrinsic
def init_csv_iterator(typingctx, csv_reader, csv_iterator_typeref):

    def codegen(context, builder, signature, args):
        jbp__kfxd = cgutils.create_struct_proxy(signature.return_type)(context,
            builder)
        jbp__kfxd.csv_reader = args[0]
        hjj__vsnwx = context.get_constant(types.uintp, 0)
        jbp__kfxd.index = cgutils.alloca_once_value(builder, hjj__vsnwx)
        return jbp__kfxd._getvalue()
    assert isinstance(csv_iterator_typeref, types.TypeRef
        ), 'Initializing a csv iterator requires a typeref'
    thhe__msmyk = csv_iterator_typeref.instance_type
    sig = signature(thhe__msmyk, csv_reader, csv_iterator_typeref)
    return sig, codegen


def gen_read_csv_objmode(csv_iterator_type):
    kxio__iukd = 'def read_csv_objmode(f_reader):\n'
    hdy__vcfck = [sanitize_varname(udtl__gggj) for udtl__gggj in
        csv_iterator_type._out_colnames]
    gsg__ttdq = ir_utils.next_label()
    qgoe__uaf = globals()
    out_types = csv_iterator_type._out_types
    qgoe__uaf[f'table_type_{gsg__ttdq}'] = TableType(tuple(out_types))
    qgoe__uaf[f'idx_array_typ'] = csv_iterator_type._index_arr_typ
    xsemh__wuv = list(range(len(csv_iterator_type._usecols)))
    kxio__iukd += _gen_read_csv_objmode(csv_iterator_type._out_colnames,
        hdy__vcfck, out_types, csv_iterator_type._usecols, xsemh__wuv,
        csv_iterator_type._sep, csv_iterator_type._escapechar, gsg__ttdq,
        qgoe__uaf, parallel=False, check_parallel_runtime=True,
        idx_col_index=csv_iterator_type._index_ind, idx_col_typ=
        csv_iterator_type._index_arr_typ)
    fbof__ytzr = bodo.ir.csv_ext._gen_parallel_flag_name(hdy__vcfck)
    low__hpikh = ['T'] + (['idx_arr'] if csv_iterator_type._index_ind is not
        None else []) + [fbof__ytzr]
    kxio__iukd += f"  return {', '.join(low__hpikh)}"
    qgoe__uaf = globals()
    hcqx__aieq = {}
    exec(kxio__iukd, qgoe__uaf, hcqx__aieq)
    ftcw__ebn = hcqx__aieq['read_csv_objmode']
    cnad__zyhuh = numba.njit(ftcw__ebn)
    bodo.ir.csv_ext.compiled_funcs.append(cnad__zyhuh)
    iht__mmop = 'def read_func(reader, local_start):\n'
    iht__mmop += f"  {', '.join(low__hpikh)} = objmode_func(reader)\n"
    index_ind = csv_iterator_type._index_ind
    if index_ind is None:
        iht__mmop += f'  local_len = len(T)\n'
        iht__mmop += '  total_size = local_len\n'
        iht__mmop += f'  if ({fbof__ytzr}):\n'
        iht__mmop += """    local_start = local_start + bodo.libs.distributed_api.dist_exscan(local_len, _op)
"""
        iht__mmop += (
            '    total_size = bodo.libs.distributed_api.dist_reduce(local_len, _op)\n'
            )
        oto__vvemi = (
            f'bodo.hiframes.pd_index_ext.init_range_index(local_start, local_start + local_len, 1, None)'
            )
    else:
        iht__mmop += '  total_size = 0\n'
        oto__vvemi = (
            f'bodo.utils.conversion.convert_to_index({low__hpikh[1]}, {csv_iterator_type._index_name!r})'
            )
    iht__mmop += f"""  return (bodo.hiframes.pd_dataframe_ext.init_dataframe(({low__hpikh[0]},), {oto__vvemi}, out_df_typ), total_size)
"""
    exec(iht__mmop, {'bodo': bodo, 'objmode_func': cnad__zyhuh, '_op': np.
        int32(bodo.libs.distributed_api.Reduce_Type.Sum.value),
        'out_df_typ': csv_iterator_type.yield_type}, hcqx__aieq)
    return hcqx__aieq['read_func']
