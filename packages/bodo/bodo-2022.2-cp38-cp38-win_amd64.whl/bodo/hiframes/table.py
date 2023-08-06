"""Table data type for storing dataframe column arrays. Supports storing many columns
(e.g. >10k) efficiently.
"""
import operator
from collections import defaultdict
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.cpython.listobj import ListInstance
from numba.extending import NativeValue, box, infer_getattr, intrinsic, lower_builtin, lower_getattr, make_attribute_wrapper, models, overload, register_model, typeof_impl, unbox
from numba.np.arrayobj import _getitem_array_single_int
from numba.parfors.array_analysis import ArrayAnalysis
from bodo.utils.cg_helpers import is_ll_eq
from bodo.utils.templates import OverloadedKeyAttributeTemplate
from bodo.utils.typing import BodoError, get_overload_const_int, is_list_like_index_type, is_overload_constant_int


class Table:

    def __init__(self, arrs, usecols=None, num_arrs=-1):
        if usecols is not None:
            assert num_arrs != -1, 'num_arrs must be provided if usecols is not None'
            gdy__bxzo = 0
            ulky__kxuq = []
            for i in range(usecols[-1] + 1):
                if i == usecols[gdy__bxzo]:
                    ulky__kxuq.append(arrs[gdy__bxzo])
                    gdy__bxzo += 1
                else:
                    ulky__kxuq.append(None)
            for tdvm__wfiea in range(usecols[-1] + 1, num_arrs):
                ulky__kxuq.append(None)
            self.arrays = ulky__kxuq
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((lmhld__lem == jeq__iruzt).all() for lmhld__lem,
            jeq__iruzt in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        amw__lhhgw = len(self.arrays)
        xasp__pndf = dict(zip(range(amw__lhhgw), self.arrays))
        df = pd.DataFrame(xasp__pndf, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        ifyqm__thj = []
        zxump__vpzi = []
        sdkh__ukpq = {}
        ehq__ulzoa = defaultdict(int)
        opwz__rch = defaultdict(list)
        if not has_runtime_cols:
            for i, pmefd__khn in enumerate(arr_types):
                if pmefd__khn not in sdkh__ukpq:
                    sdkh__ukpq[pmefd__khn] = len(sdkh__ukpq)
                parm__avfve = sdkh__ukpq[pmefd__khn]
                ifyqm__thj.append(parm__avfve)
                zxump__vpzi.append(ehq__ulzoa[parm__avfve])
                ehq__ulzoa[parm__avfve] += 1
                opwz__rch[parm__avfve].append(i)
        self.block_nums = ifyqm__thj
        self.block_offsets = zxump__vpzi
        self.type_to_blk = sdkh__ukpq
        self.block_to_arr_ind = opwz__rch
        super(TableType, self).__init__(name=
            f'TableType({arr_types}, {has_runtime_cols})')

    @property
    def as_array(self):
        return types.Array(types.undefined, 2, 'C')

    @property
    def key(self):
        return self.arr_types, self.has_runtime_cols

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@typeof_impl.register(Table)
def typeof_table(val, c):
    return TableType(tuple(numba.typeof(zpyx__juw) for zpyx__juw in val.arrays)
        )


@register_model(TableType)
class TableTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        if fe_type.has_runtime_cols:
            gmzzh__swis = [(f'block_{i}', types.List(pmefd__khn)) for i,
                pmefd__khn in enumerate(fe_type.arr_types)]
        else:
            gmzzh__swis = [(f'block_{parm__avfve}', types.List(pmefd__khn)) for
                pmefd__khn, parm__avfve in fe_type.type_to_blk.items()]
        gmzzh__swis.append(('parent', types.pyobject))
        gmzzh__swis.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, gmzzh__swis)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    fhet__xel = c.pyapi.object_getattr_string(val, 'arrays')
    jwvu__swfby = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    jwvu__swfby.parent = cgutils.get_null_value(jwvu__swfby.parent.type)
    nvee__onx = c.pyapi.make_none()
    xomh__jnpac = c.context.get_constant(types.int64, 0)
    tyd__wjphe = cgutils.alloca_once_value(c.builder, xomh__jnpac)
    for pmefd__khn, parm__avfve in typ.type_to_blk.items():
        jysca__aagp = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[parm__avfve]))
        tdvm__wfiea, wsyec__ari = ListInstance.allocate_ex(c.context, c.
            builder, types.List(pmefd__khn), jysca__aagp)
        wsyec__ari.size = jysca__aagp
        ywpv__orhpq = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[parm__avfve
            ], dtype=np.int64))
        dyei__hct = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, ywpv__orhpq)
        with cgutils.for_range(c.builder, jysca__aagp) as loop:
            i = loop.index
            ola__rytud = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), dyei__hct, i)
            jvwfp__msw = c.pyapi.long_from_longlong(ola__rytud)
            zeei__wold = c.pyapi.object_getitem(fhet__xel, jvwfp__msw)
            uwo__tqnsv = c.builder.icmp_unsigned('==', zeei__wold, nvee__onx)
            with c.builder.if_else(uwo__tqnsv) as (then, orelse):
                with then:
                    oig__kfsiq = c.context.get_constant_null(pmefd__khn)
                    wsyec__ari.inititem(i, oig__kfsiq, incref=False)
                with orelse:
                    awy__dwi = c.pyapi.call_method(zeei__wold, '__len__', ())
                    qfpzy__dcr = c.pyapi.long_as_longlong(awy__dwi)
                    c.builder.store(qfpzy__dcr, tyd__wjphe)
                    c.pyapi.decref(awy__dwi)
                    zpyx__juw = c.pyapi.to_native_value(pmefd__khn, zeei__wold
                        ).value
                    wsyec__ari.inititem(i, zpyx__juw, incref=False)
            c.pyapi.decref(zeei__wold)
            c.pyapi.decref(jvwfp__msw)
        setattr(jwvu__swfby, f'block_{parm__avfve}', wsyec__ari.value)
    jwvu__swfby.len = c.builder.load(tyd__wjphe)
    c.pyapi.decref(fhet__xel)
    c.pyapi.decref(nvee__onx)
    wcjfu__zmey = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(jwvu__swfby._getvalue(), is_error=wcjfu__zmey)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    jwvu__swfby = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        cot__bokcr = c.context.get_constant(types.int64, 0)
        for i, pmefd__khn in enumerate(typ.arr_types):
            ulky__kxuq = getattr(jwvu__swfby, f'block_{i}')
            eoiw__ncmi = ListInstance(c.context, c.builder, types.List(
                pmefd__khn), ulky__kxuq)
            cot__bokcr = c.builder.add(cot__bokcr, eoiw__ncmi.size)
        mrb__tjsk = c.pyapi.list_new(cot__bokcr)
        nzqqw__enze = c.context.get_constant(types.int64, 0)
        for i, pmefd__khn in enumerate(typ.arr_types):
            ulky__kxuq = getattr(jwvu__swfby, f'block_{i}')
            eoiw__ncmi = ListInstance(c.context, c.builder, types.List(
                pmefd__khn), ulky__kxuq)
            with cgutils.for_range(c.builder, eoiw__ncmi.size) as loop:
                i = loop.index
                zpyx__juw = eoiw__ncmi.getitem(i)
                c.context.nrt.incref(c.builder, pmefd__khn, zpyx__juw)
                idx = c.builder.add(nzqqw__enze, i)
                c.pyapi.list_setitem(mrb__tjsk, idx, c.pyapi.
                    from_native_value(pmefd__khn, zpyx__juw, c.env_manager))
            nzqqw__enze = c.builder.add(nzqqw__enze, eoiw__ncmi.size)
        wotk__pzkd = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        adep__dlkig = c.pyapi.call_function_objargs(wotk__pzkd, (mrb__tjsk,))
        c.pyapi.decref(wotk__pzkd)
        c.pyapi.decref(mrb__tjsk)
        c.context.nrt.decref(c.builder, typ, val)
        return adep__dlkig
    mrb__tjsk = c.pyapi.list_new(c.context.get_constant(types.int64, len(
        typ.arr_types)))
    mmdp__dbpqj = cgutils.is_not_null(c.builder, jwvu__swfby.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for pmefd__khn, parm__avfve in typ.type_to_blk.items():
        ulky__kxuq = getattr(jwvu__swfby, f'block_{parm__avfve}')
        eoiw__ncmi = ListInstance(c.context, c.builder, types.List(
            pmefd__khn), ulky__kxuq)
        ywpv__orhpq = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[parm__avfve
            ], dtype=np.int64))
        dyei__hct = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, ywpv__orhpq)
        with cgutils.for_range(c.builder, eoiw__ncmi.size) as loop:
            i = loop.index
            ola__rytud = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), dyei__hct, i)
            zpyx__juw = eoiw__ncmi.getitem(i)
            dzze__jnqn = cgutils.alloca_once_value(c.builder, zpyx__juw)
            izw__goz = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(pmefd__khn))
            lehxd__wponv = is_ll_eq(c.builder, dzze__jnqn, izw__goz)
            with c.builder.if_else(c.builder.and_(lehxd__wponv, c.builder.
                not_(ensure_unboxed))) as (then, orelse):
                with then:
                    nvee__onx = c.pyapi.make_none()
                    c.pyapi.list_setitem(mrb__tjsk, ola__rytud, nvee__onx)
                with orelse:
                    zeei__wold = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(lehxd__wponv,
                        mmdp__dbpqj)) as (arr_then, arr_orelse):
                        with arr_then:
                            inlhg__zrbc = get_df_obj_column_codegen(c.
                                context, c.builder, c.pyapi, jwvu__swfby.
                                parent, ola__rytud, pmefd__khn)
                            c.builder.store(inlhg__zrbc, zeei__wold)
                        with arr_orelse:
                            c.context.nrt.incref(c.builder, pmefd__khn,
                                zpyx__juw)
                            c.builder.store(c.pyapi.from_native_value(
                                pmefd__khn, zpyx__juw, c.env_manager),
                                zeei__wold)
                    c.pyapi.list_setitem(mrb__tjsk, ola__rytud, c.builder.
                        load(zeei__wold))
    wotk__pzkd = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    adep__dlkig = c.pyapi.call_function_objargs(wotk__pzkd, (mrb__tjsk,))
    c.pyapi.decref(wotk__pzkd)
    c.pyapi.decref(mrb__tjsk)
    c.context.nrt.decref(c.builder, typ, val)
    return adep__dlkig


@lower_builtin(len, TableType)
def table_len_lower(context, builder, sig, args):
    impl = table_len_overload(*sig.args)
    return context.compile_internal(builder, impl, sig, args)


def table_len_overload(T):
    if not isinstance(T, TableType):
        return

    def impl(T):
        return T._len
    return impl


@lower_getattr(TableType, 'shape')
def lower_table_shape(context, builder, typ, val):
    impl = table_shape_overload(typ)
    return context.compile_internal(builder, impl, types.Tuple([types.int64,
        types.int64])(typ), (val,))


def table_shape_overload(T):
    if T.has_runtime_cols:

        def impl(T):
            return T._len, compute_num_runtime_columns(T)
        return impl
    ncols = len(T.arr_types)
    return lambda T: (T._len, types.int64(ncols))


@intrinsic
def compute_num_runtime_columns(typingctx, table_type):
    assert isinstance(table_type, TableType)

    def codegen(context, builder, sig, args):
        table_arg, = args
        jwvu__swfby = cgutils.create_struct_proxy(table_type)(context,
            builder, table_arg)
        zugjn__elx = context.get_constant(types.int64, 0)
        for i, pmefd__khn in enumerate(table_type.arr_types):
            ulky__kxuq = getattr(jwvu__swfby, f'block_{i}')
            eoiw__ncmi = ListInstance(context, builder, types.List(
                pmefd__khn), ulky__kxuq)
            zugjn__elx = builder.add(zugjn__elx, eoiw__ncmi.size)
        return zugjn__elx
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    jwvu__swfby = cgutils.create_struct_proxy(table_type)(context, builder,
        table_arg)
    parm__avfve = table_type.block_nums[col_ind]
    qxjo__snm = table_type.block_offsets[col_ind]
    ulky__kxuq = getattr(jwvu__swfby, f'block_{parm__avfve}')
    eoiw__ncmi = ListInstance(context, builder, types.List(arr_type),
        ulky__kxuq)
    zpyx__juw = eoiw__ncmi.getitem(qxjo__snm)
    return zpyx__juw


@intrinsic
def get_table_data(typingctx, table_type, ind_typ=None):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, tdvm__wfiea = args
        zpyx__juw = get_table_data_codegen(context, builder, table_arg,
            col_ind, table_type)
        return impl_ret_borrowed(context, builder, arr_type, zpyx__juw)
    sig = arr_type(table_type, ind_typ)
    return sig, codegen


@intrinsic
def del_column(typingctx, table_type, ind_typ=None):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, tdvm__wfiea = args
        jwvu__swfby = cgutils.create_struct_proxy(table_type)(context,
            builder, table_arg)
        parm__avfve = table_type.block_nums[col_ind]
        qxjo__snm = table_type.block_offsets[col_ind]
        ulky__kxuq = getattr(jwvu__swfby, f'block_{parm__avfve}')
        eoiw__ncmi = ListInstance(context, builder, types.List(arr_type),
            ulky__kxuq)
        zpyx__juw = eoiw__ncmi.getitem(qxjo__snm)
        context.nrt.decref(builder, arr_type, zpyx__juw)
        oig__kfsiq = context.get_constant_null(arr_type)
        eoiw__ncmi.inititem(qxjo__snm, oig__kfsiq, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    xomh__jnpac = context.get_constant(types.int64, 0)
    hbw__xlisq = context.get_constant(types.int64, 1)
    qoid__oghkt = arr_type not in in_table_type.type_to_blk
    for pmefd__khn, parm__avfve in out_table_type.type_to_blk.items():
        if pmefd__khn in in_table_type.type_to_blk:
            oxbi__hsqko = in_table_type.type_to_blk[pmefd__khn]
            wsyec__ari = ListInstance(context, builder, types.List(
                pmefd__khn), getattr(in_table, f'block_{oxbi__hsqko}'))
            context.nrt.incref(builder, types.List(pmefd__khn), wsyec__ari.
                value)
            setattr(out_table, f'block_{parm__avfve}', wsyec__ari.value)
    if qoid__oghkt:
        tdvm__wfiea, wsyec__ari = ListInstance.allocate_ex(context, builder,
            types.List(arr_type), hbw__xlisq)
        wsyec__ari.size = hbw__xlisq
        wsyec__ari.inititem(xomh__jnpac, arr_arg, incref=True)
        parm__avfve = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{parm__avfve}', wsyec__ari.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        parm__avfve = out_table_type.type_to_blk[arr_type]
        wsyec__ari = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{parm__avfve}'))
        if is_new_col:
            n = wsyec__ari.size
            kdwe__bocz = builder.add(n, hbw__xlisq)
            wsyec__ari.resize(kdwe__bocz)
            wsyec__ari.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            nwkh__lvxl = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            wsyec__ari.setitem(nwkh__lvxl, arr_arg, True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            nwkh__lvxl = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = wsyec__ari.size
            kdwe__bocz = builder.add(n, hbw__xlisq)
            wsyec__ari.resize(kdwe__bocz)
            context.nrt.incref(builder, arr_type, wsyec__ari.getitem(
                nwkh__lvxl))
            wsyec__ari.move(builder.add(nwkh__lvxl, hbw__xlisq), nwkh__lvxl,
                builder.sub(n, nwkh__lvxl))
            wsyec__ari.setitem(nwkh__lvxl, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    ubu__wyiys = in_table_type.arr_types[col_ind]
    if ubu__wyiys in out_table_type.type_to_blk:
        parm__avfve = out_table_type.type_to_blk[ubu__wyiys]
        jtywg__xrp = getattr(out_table, f'block_{parm__avfve}')
        jshx__xxmq = types.List(ubu__wyiys)
        nwkh__lvxl = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        vkii__cubsp = jshx__xxmq.dtype(jshx__xxmq, types.intp)
        mona__cyxj = context.compile_internal(builder, lambda lst, i: lst.
            pop(i), vkii__cubsp, (jtywg__xrp, nwkh__lvxl))
        context.nrt.decref(builder, ubu__wyiys, mona__cyxj)


@intrinsic
def set_table_data(typingctx, table_type, ind_type, arr_type=None):
    assert isinstance(table_type, TableType), 'invalid input to set_table_data'
    assert is_overload_constant_int(ind_type
        ), 'set_table_data expects const index'
    col_ind = get_overload_const_int(ind_type)
    is_new_col = col_ind == len(table_type.arr_types)
    vatf__qbf = list(table_type.arr_types)
    if is_new_col:
        vatf__qbf.append(arr_type)
    else:
        vatf__qbf[col_ind] = arr_type
    out_table_type = TableType(tuple(vatf__qbf))

    def codegen(context, builder, sig, args):
        table_arg, tdvm__wfiea, uzt__fak = args
        out_table = set_table_data_codegen(context, builder, table_type,
            table_arg, out_table_type, arr_type, uzt__fak, col_ind, is_new_col)
        return out_table
    return out_table_type(table_type, ind_type, arr_type), codegen


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_table_data',
    'bodo.hiframes.table'] = alias_ext_dummy_func


def get_table_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    jhek__xjy = args[0]
    if equiv_set.has_shape(jhek__xjy):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            jhek__xjy)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    ogzif__wjvc = []
    for pmefd__khn, parm__avfve in table_type.type_to_blk.items():
        pzno__ykiya = len(table_type.block_to_arr_ind[parm__avfve])
        sptp__jhe = []
        for i in range(pzno__ykiya):
            ola__rytud = table_type.block_to_arr_ind[parm__avfve][i]
            sptp__jhe.append(pyval.arrays[ola__rytud])
        ogzif__wjvc.append(context.get_constant_generic(builder, types.List
            (pmefd__khn), sptp__jhe))
    yjxz__agsqw = context.get_constant_null(types.pyobject)
    lphq__alr = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(ogzif__wjvc + [yjxz__agsqw, lphq__alr])


@intrinsic
def init_table(typingctx, table_type=None):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        jwvu__swfby = cgutils.create_struct_proxy(table_type)(context, builder)
        for pmefd__khn, parm__avfve in table_type.type_to_blk.items():
            ggm__gso = context.get_constant_null(types.List(pmefd__khn))
            setattr(jwvu__swfby, f'block_{parm__avfve}', ggm__gso)
        return jwvu__swfby._getvalue()
    sig = table_type(table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type=None):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    parm__avfve = get_overload_const_int(blk_type)
    arr_type = None
    for pmefd__khn, jeq__iruzt in table_type.type_to_blk.items():
        if jeq__iruzt == parm__avfve:
            arr_type = pmefd__khn
            break
    assert arr_type is not None, 'invalid table type block'
    fmvnk__gxkdn = types.List(arr_type)

    def codegen(context, builder, sig, args):
        jwvu__swfby = cgutils.create_struct_proxy(table_type)(context,
            builder, args[0])
        ulky__kxuq = getattr(jwvu__swfby, f'block_{parm__avfve}')
        return impl_ret_borrowed(context, builder, fmvnk__gxkdn, ulky__kxuq)
    sig = fmvnk__gxkdn(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_column_unboxed(typingctx, table_type, arr_list_t, ind_t,
    arr_ind_t=None):
    assert isinstance(table_type, TableType), 'table type expected'
    sig = types.none(table_type, arr_list_t, ind_t, arr_ind_t)
    return sig, ensure_column_unboxed_codegen


def ensure_column_unboxed_codegen(context, builder, sig, args):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table_arg, cqhrx__upd, douin__kmj, ffyhu__ywdao = args
    eodgt__tykq = context.get_python_api(builder)
    jwvu__swfby = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    mmdp__dbpqj = cgutils.is_not_null(builder, jwvu__swfby.parent)
    eoiw__ncmi = ListInstance(context, builder, sig.args[1], cqhrx__upd)
    samd__xuvt = eoiw__ncmi.getitem(douin__kmj)
    dzze__jnqn = cgutils.alloca_once_value(builder, samd__xuvt)
    izw__goz = cgutils.alloca_once_value(builder, context.get_constant_null
        (sig.args[1].dtype))
    lehxd__wponv = is_ll_eq(builder, dzze__jnqn, izw__goz)
    with builder.if_then(lehxd__wponv):
        with builder.if_else(mmdp__dbpqj) as (then, orelse):
            with then:
                zeei__wold = get_df_obj_column_codegen(context, builder,
                    eodgt__tykq, jwvu__swfby.parent, ffyhu__ywdao, sig.args
                    [1].dtype)
                zpyx__juw = eodgt__tykq.to_native_value(sig.args[1].dtype,
                    zeei__wold).value
                eoiw__ncmi.inititem(douin__kmj, zpyx__juw, incref=False)
                eodgt__tykq.decref(zeei__wold)
            with orelse:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type=None):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    parm__avfve = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, jtwri__jvtd, tdvm__wfiea = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{parm__avfve}', jtwri__jvtd)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type=None):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, muni__xgs = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = muni__xgs
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type=None):
    assert isinstance(list_type, types.List), 'list type expected'

    def codegen(context, builder, sig, args):
        itls__lnj = ListInstance(context, builder, list_type, args[0])
        jkgn__raxvo = itls__lnj.size
        tdvm__wfiea, wsyec__ari = ListInstance.allocate_ex(context, builder,
            list_type, jkgn__raxvo)
        wsyec__ari.size = jkgn__raxvo
        return wsyec__ari.value
    sig = list_type(list_type)
    return sig, codegen


def _get_idx_length(idx):
    pass


@overload(_get_idx_length)
def overload_get_idx_length(idx, n):
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        return lambda idx, n: idx.sum()
    assert isinstance(idx, types.SliceType), 'slice index expected'

    def impl(idx, n):
        xxiay__wgug = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(xxiay__wgug)
    return impl


def gen_table_filter(T, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    kdv__amxjz = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if used_cols is not None:
        kdv__amxjz['used_cols'] = np.array(used_cols, dtype=np.int64)
    cpnh__hayxe = 'def impl(T, idx):\n'
    cpnh__hayxe += f'  T2 = init_table(T)\n'
    cpnh__hayxe += f'  l = 0\n'
    if used_cols is not None and len(used_cols) == 0:
        cpnh__hayxe += f'  l = _get_idx_length(idx, len(T))\n'
        cpnh__hayxe += f'  T2 = set_table_len(T2, l)\n'
        cpnh__hayxe += f'  return T2\n'
        jqqa__bmumj = {}
        exec(cpnh__hayxe, kdv__amxjz, jqqa__bmumj)
        return jqqa__bmumj['impl']
    if used_cols is not None:
        cpnh__hayxe += f'  used_set = set(used_cols)\n'
    for parm__avfve in T.type_to_blk.values():
        kdv__amxjz[f'arr_inds_{parm__avfve}'] = np.array(T.block_to_arr_ind
            [parm__avfve], dtype=np.int64)
        cpnh__hayxe += (
            f'  arr_list_{parm__avfve} = get_table_block(T, {parm__avfve})\n')
        cpnh__hayxe += (
            f'  out_arr_list_{parm__avfve} = alloc_list_like(arr_list_{parm__avfve})\n'
            )
        cpnh__hayxe += f'  for i in range(len(arr_list_{parm__avfve})):\n'
        cpnh__hayxe += (
            f'    arr_ind_{parm__avfve} = arr_inds_{parm__avfve}[i]\n')
        if used_cols is not None:
            cpnh__hayxe += (
                f'    if arr_ind_{parm__avfve} not in used_set: continue\n')
        cpnh__hayxe += f"""    ensure_column_unboxed(T, arr_list_{parm__avfve}, i, arr_ind_{parm__avfve})
"""
        cpnh__hayxe += f"""    out_arr_{parm__avfve} = ensure_contig_if_np(arr_list_{parm__avfve}[i][idx])
"""
        cpnh__hayxe += f'    l = len(out_arr_{parm__avfve})\n'
        cpnh__hayxe += (
            f'    out_arr_list_{parm__avfve}[i] = out_arr_{parm__avfve}\n')
        cpnh__hayxe += (
            f'  T2 = set_table_block(T2, out_arr_list_{parm__avfve}, {parm__avfve})\n'
            )
    cpnh__hayxe += f'  T2 = set_table_len(T2, l)\n'
    cpnh__hayxe += f'  return T2\n'
    jqqa__bmumj = {}
    exec(cpnh__hayxe, kdv__amxjz, jqqa__bmumj)
    return jqqa__bmumj['impl']


@overload(operator.getitem, no_unliteral=True)
def table_getitem(T, idx):
    if not isinstance(T, TableType):
        return
    return gen_table_filter(T)


@intrinsic
def init_runtime_table_from_lists(typingctx, arr_list_tup_typ, nrows_typ=None):
    assert isinstance(arr_list_tup_typ, types.BaseTuple
        ), 'init_runtime_table_from_lists requires a tuple of list of arrays'
    if isinstance(arr_list_tup_typ, types.UniTuple):
        if arr_list_tup_typ.dtype.dtype == types.undefined:
            return
        ptkeh__oue = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        ptkeh__oue = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            ptkeh__oue.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        ctca__lbg, bwpc__velc = args
        jwvu__swfby = cgutils.create_struct_proxy(table_type)(context, builder)
        jwvu__swfby.len = bwpc__velc
        ogzif__wjvc = cgutils.unpack_tuple(builder, ctca__lbg)
        for i, ulky__kxuq in enumerate(ogzif__wjvc):
            setattr(jwvu__swfby, f'block_{i}', ulky__kxuq)
            context.nrt.incref(builder, types.List(ptkeh__oue[i]), ulky__kxuq)
        return jwvu__swfby._getvalue()
    table_type = TableType(tuple(ptkeh__oue), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen
