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
            fciop__mwngd = 0
            kqdcy__cqq = []
            for i in range(usecols[-1] + 1):
                if i == usecols[fciop__mwngd]:
                    kqdcy__cqq.append(arrs[fciop__mwngd])
                    fciop__mwngd += 1
                else:
                    kqdcy__cqq.append(None)
            for ysdlt__nsfu in range(usecols[-1] + 1, num_arrs):
                kqdcy__cqq.append(None)
            self.arrays = kqdcy__cqq
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((ulof__myb == hwmlh__jtvkw).all() for ulof__myb,
            hwmlh__jtvkw in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        coe__vhla = len(self.arrays)
        sks__qou = dict(zip(range(coe__vhla), self.arrays))
        df = pd.DataFrame(sks__qou, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        bsf__xzq = []
        ukp__ovx = []
        ztokx__xlnc = {}
        nbgh__zrn = defaultdict(int)
        ofh__uwb = defaultdict(list)
        if not has_runtime_cols:
            for i, nub__uoj in enumerate(arr_types):
                if nub__uoj not in ztokx__xlnc:
                    ztokx__xlnc[nub__uoj] = len(ztokx__xlnc)
                eujg__mry = ztokx__xlnc[nub__uoj]
                bsf__xzq.append(eujg__mry)
                ukp__ovx.append(nbgh__zrn[eujg__mry])
                nbgh__zrn[eujg__mry] += 1
                ofh__uwb[eujg__mry].append(i)
        self.block_nums = bsf__xzq
        self.block_offsets = ukp__ovx
        self.type_to_blk = ztokx__xlnc
        self.block_to_arr_ind = ofh__uwb
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
    return TableType(tuple(numba.typeof(php__cwcd) for php__cwcd in val.arrays)
        )


@register_model(TableType)
class TableTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        if fe_type.has_runtime_cols:
            stlc__rlg = [(f'block_{i}', types.List(nub__uoj)) for i,
                nub__uoj in enumerate(fe_type.arr_types)]
        else:
            stlc__rlg = [(f'block_{eujg__mry}', types.List(nub__uoj)) for 
                nub__uoj, eujg__mry in fe_type.type_to_blk.items()]
        stlc__rlg.append(('parent', types.pyobject))
        stlc__rlg.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, stlc__rlg)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    cgn__tfa = c.pyapi.object_getattr_string(val, 'arrays')
    pkfk__evgej = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    pkfk__evgej.parent = cgutils.get_null_value(pkfk__evgej.parent.type)
    afj__nzark = c.pyapi.make_none()
    avn__byxhd = c.context.get_constant(types.int64, 0)
    ymato__qwhso = cgutils.alloca_once_value(c.builder, avn__byxhd)
    for nub__uoj, eujg__mry in typ.type_to_blk.items():
        vqgn__kag = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[eujg__mry]))
        ysdlt__nsfu, rsc__eywoa = ListInstance.allocate_ex(c.context, c.
            builder, types.List(nub__uoj), vqgn__kag)
        rsc__eywoa.size = vqgn__kag
        hck__isedu = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[eujg__mry],
            dtype=np.int64))
        siwoc__kek = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, hck__isedu)
        with cgutils.for_range(c.builder, vqgn__kag) as loop:
            i = loop.index
            ust__scuyj = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), siwoc__kek, i)
            vhldr__fsu = c.pyapi.long_from_longlong(ust__scuyj)
            fcyhf__pwu = c.pyapi.object_getitem(cgn__tfa, vhldr__fsu)
            ibnnt__irfw = c.builder.icmp_unsigned('==', fcyhf__pwu, afj__nzark)
            with c.builder.if_else(ibnnt__irfw) as (then, orelse):
                with then:
                    lxmep__qjh = c.context.get_constant_null(nub__uoj)
                    rsc__eywoa.inititem(i, lxmep__qjh, incref=False)
                with orelse:
                    vtc__vyo = c.pyapi.call_method(fcyhf__pwu, '__len__', ())
                    hyv__wiaf = c.pyapi.long_as_longlong(vtc__vyo)
                    c.builder.store(hyv__wiaf, ymato__qwhso)
                    c.pyapi.decref(vtc__vyo)
                    php__cwcd = c.pyapi.to_native_value(nub__uoj, fcyhf__pwu
                        ).value
                    rsc__eywoa.inititem(i, php__cwcd, incref=False)
            c.pyapi.decref(fcyhf__pwu)
            c.pyapi.decref(vhldr__fsu)
        setattr(pkfk__evgej, f'block_{eujg__mry}', rsc__eywoa.value)
    pkfk__evgej.len = c.builder.load(ymato__qwhso)
    c.pyapi.decref(cgn__tfa)
    c.pyapi.decref(afj__nzark)
    qsit__vceh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(pkfk__evgej._getvalue(), is_error=qsit__vceh)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    pkfk__evgej = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        wfqc__paplr = c.context.get_constant(types.int64, 0)
        for i, nub__uoj in enumerate(typ.arr_types):
            kqdcy__cqq = getattr(pkfk__evgej, f'block_{i}')
            ixtqj__hctkf = ListInstance(c.context, c.builder, types.List(
                nub__uoj), kqdcy__cqq)
            wfqc__paplr = c.builder.add(wfqc__paplr, ixtqj__hctkf.size)
        ptrg__skwe = c.pyapi.list_new(wfqc__paplr)
        yrutj__uvp = c.context.get_constant(types.int64, 0)
        for i, nub__uoj in enumerate(typ.arr_types):
            kqdcy__cqq = getattr(pkfk__evgej, f'block_{i}')
            ixtqj__hctkf = ListInstance(c.context, c.builder, types.List(
                nub__uoj), kqdcy__cqq)
            with cgutils.for_range(c.builder, ixtqj__hctkf.size) as loop:
                i = loop.index
                php__cwcd = ixtqj__hctkf.getitem(i)
                c.context.nrt.incref(c.builder, nub__uoj, php__cwcd)
                idx = c.builder.add(yrutj__uvp, i)
                c.pyapi.list_setitem(ptrg__skwe, idx, c.pyapi.
                    from_native_value(nub__uoj, php__cwcd, c.env_manager))
            yrutj__uvp = c.builder.add(yrutj__uvp, ixtqj__hctkf.size)
        lmcir__nbjr = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        rtl__ghtm = c.pyapi.call_function_objargs(lmcir__nbjr, (ptrg__skwe,))
        c.pyapi.decref(lmcir__nbjr)
        c.pyapi.decref(ptrg__skwe)
        c.context.nrt.decref(c.builder, typ, val)
        return rtl__ghtm
    ptrg__skwe = c.pyapi.list_new(c.context.get_constant(types.int64, len(
        typ.arr_types)))
    rcmqr__sbg = cgutils.is_not_null(c.builder, pkfk__evgej.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for nub__uoj, eujg__mry in typ.type_to_blk.items():
        kqdcy__cqq = getattr(pkfk__evgej, f'block_{eujg__mry}')
        ixtqj__hctkf = ListInstance(c.context, c.builder, types.List(
            nub__uoj), kqdcy__cqq)
        hck__isedu = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[eujg__mry],
            dtype=np.int64))
        siwoc__kek = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, hck__isedu)
        with cgutils.for_range(c.builder, ixtqj__hctkf.size) as loop:
            i = loop.index
            ust__scuyj = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), siwoc__kek, i)
            php__cwcd = ixtqj__hctkf.getitem(i)
            cqnys__qzqy = cgutils.alloca_once_value(c.builder, php__cwcd)
            whqmk__dkl = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(nub__uoj))
            vlp__fnpyg = is_ll_eq(c.builder, cqnys__qzqy, whqmk__dkl)
            with c.builder.if_else(c.builder.and_(vlp__fnpyg, c.builder.
                not_(ensure_unboxed))) as (then, orelse):
                with then:
                    afj__nzark = c.pyapi.make_none()
                    c.pyapi.list_setitem(ptrg__skwe, ust__scuyj, afj__nzark)
                with orelse:
                    fcyhf__pwu = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(vlp__fnpyg,
                        rcmqr__sbg)) as (arr_then, arr_orelse):
                        with arr_then:
                            wlnrp__qfth = get_df_obj_column_codegen(c.
                                context, c.builder, c.pyapi, pkfk__evgej.
                                parent, ust__scuyj, nub__uoj)
                            c.builder.store(wlnrp__qfth, fcyhf__pwu)
                        with arr_orelse:
                            c.context.nrt.incref(c.builder, nub__uoj, php__cwcd
                                )
                            c.builder.store(c.pyapi.from_native_value(
                                nub__uoj, php__cwcd, c.env_manager), fcyhf__pwu
                                )
                    c.pyapi.list_setitem(ptrg__skwe, ust__scuyj, c.builder.
                        load(fcyhf__pwu))
    lmcir__nbjr = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    rtl__ghtm = c.pyapi.call_function_objargs(lmcir__nbjr, (ptrg__skwe,))
    c.pyapi.decref(lmcir__nbjr)
    c.pyapi.decref(ptrg__skwe)
    c.context.nrt.decref(c.builder, typ, val)
    return rtl__ghtm


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
        pkfk__evgej = cgutils.create_struct_proxy(table_type)(context,
            builder, table_arg)
        jexoe__tqbr = context.get_constant(types.int64, 0)
        for i, nub__uoj in enumerate(table_type.arr_types):
            kqdcy__cqq = getattr(pkfk__evgej, f'block_{i}')
            ixtqj__hctkf = ListInstance(context, builder, types.List(
                nub__uoj), kqdcy__cqq)
            jexoe__tqbr = builder.add(jexoe__tqbr, ixtqj__hctkf.size)
        return jexoe__tqbr
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    pkfk__evgej = cgutils.create_struct_proxy(table_type)(context, builder,
        table_arg)
    eujg__mry = table_type.block_nums[col_ind]
    vozqo__sxch = table_type.block_offsets[col_ind]
    kqdcy__cqq = getattr(pkfk__evgej, f'block_{eujg__mry}')
    ixtqj__hctkf = ListInstance(context, builder, types.List(arr_type),
        kqdcy__cqq)
    php__cwcd = ixtqj__hctkf.getitem(vozqo__sxch)
    return php__cwcd


@intrinsic
def get_table_data(typingctx, table_type, ind_typ=None):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, ysdlt__nsfu = args
        php__cwcd = get_table_data_codegen(context, builder, table_arg,
            col_ind, table_type)
        return impl_ret_borrowed(context, builder, arr_type, php__cwcd)
    sig = arr_type(table_type, ind_typ)
    return sig, codegen


@intrinsic
def del_column(typingctx, table_type, ind_typ=None):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, ysdlt__nsfu = args
        pkfk__evgej = cgutils.create_struct_proxy(table_type)(context,
            builder, table_arg)
        eujg__mry = table_type.block_nums[col_ind]
        vozqo__sxch = table_type.block_offsets[col_ind]
        kqdcy__cqq = getattr(pkfk__evgej, f'block_{eujg__mry}')
        ixtqj__hctkf = ListInstance(context, builder, types.List(arr_type),
            kqdcy__cqq)
        php__cwcd = ixtqj__hctkf.getitem(vozqo__sxch)
        context.nrt.decref(builder, arr_type, php__cwcd)
        lxmep__qjh = context.get_constant_null(arr_type)
        ixtqj__hctkf.inititem(vozqo__sxch, lxmep__qjh, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    avn__byxhd = context.get_constant(types.int64, 0)
    ihb__rik = context.get_constant(types.int64, 1)
    xrayr__gncwc = arr_type not in in_table_type.type_to_blk
    for nub__uoj, eujg__mry in out_table_type.type_to_blk.items():
        if nub__uoj in in_table_type.type_to_blk:
            rxkdy__aflhn = in_table_type.type_to_blk[nub__uoj]
            rsc__eywoa = ListInstance(context, builder, types.List(nub__uoj
                ), getattr(in_table, f'block_{rxkdy__aflhn}'))
            context.nrt.incref(builder, types.List(nub__uoj), rsc__eywoa.value)
            setattr(out_table, f'block_{eujg__mry}', rsc__eywoa.value)
    if xrayr__gncwc:
        ysdlt__nsfu, rsc__eywoa = ListInstance.allocate_ex(context, builder,
            types.List(arr_type), ihb__rik)
        rsc__eywoa.size = ihb__rik
        rsc__eywoa.inititem(avn__byxhd, arr_arg, incref=True)
        eujg__mry = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{eujg__mry}', rsc__eywoa.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        eujg__mry = out_table_type.type_to_blk[arr_type]
        rsc__eywoa = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{eujg__mry}'))
        if is_new_col:
            n = rsc__eywoa.size
            zdmxh__sid = builder.add(n, ihb__rik)
            rsc__eywoa.resize(zdmxh__sid)
            rsc__eywoa.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            ngm__tbf = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            rsc__eywoa.setitem(ngm__tbf, arr_arg, True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            ngm__tbf = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = rsc__eywoa.size
            zdmxh__sid = builder.add(n, ihb__rik)
            rsc__eywoa.resize(zdmxh__sid)
            context.nrt.incref(builder, arr_type, rsc__eywoa.getitem(ngm__tbf))
            rsc__eywoa.move(builder.add(ngm__tbf, ihb__rik), ngm__tbf,
                builder.sub(n, ngm__tbf))
            rsc__eywoa.setitem(ngm__tbf, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    tvojk__iisea = in_table_type.arr_types[col_ind]
    if tvojk__iisea in out_table_type.type_to_blk:
        eujg__mry = out_table_type.type_to_blk[tvojk__iisea]
        etme__pne = getattr(out_table, f'block_{eujg__mry}')
        itrk__yuhen = types.List(tvojk__iisea)
        ngm__tbf = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        mqbkx__mbnsj = itrk__yuhen.dtype(itrk__yuhen, types.intp)
        rngjv__dmjds = context.compile_internal(builder, lambda lst, i: lst
            .pop(i), mqbkx__mbnsj, (etme__pne, ngm__tbf))
        context.nrt.decref(builder, tvojk__iisea, rngjv__dmjds)


@intrinsic
def set_table_data(typingctx, table_type, ind_type, arr_type=None):
    assert isinstance(table_type, TableType), 'invalid input to set_table_data'
    assert is_overload_constant_int(ind_type
        ), 'set_table_data expects const index'
    col_ind = get_overload_const_int(ind_type)
    is_new_col = col_ind == len(table_type.arr_types)
    yiyx__lywcg = list(table_type.arr_types)
    if is_new_col:
        yiyx__lywcg.append(arr_type)
    else:
        yiyx__lywcg[col_ind] = arr_type
    out_table_type = TableType(tuple(yiyx__lywcg))

    def codegen(context, builder, sig, args):
        table_arg, ysdlt__nsfu, zttj__ctg = args
        out_table = set_table_data_codegen(context, builder, table_type,
            table_arg, out_table_type, arr_type, zttj__ctg, col_ind, is_new_col
            )
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
    pqml__cowif = args[0]
    if equiv_set.has_shape(pqml__cowif):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            pqml__cowif)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    fle__akipb = []
    for nub__uoj, eujg__mry in table_type.type_to_blk.items():
        vknjo__lcmfc = len(table_type.block_to_arr_ind[eujg__mry])
        ivjq__iizkf = []
        for i in range(vknjo__lcmfc):
            ust__scuyj = table_type.block_to_arr_ind[eujg__mry][i]
            ivjq__iizkf.append(pyval.arrays[ust__scuyj])
        fle__akipb.append(context.get_constant_generic(builder, types.List(
            nub__uoj), ivjq__iizkf))
    vof__wqp = context.get_constant_null(types.pyobject)
    gydlp__avp = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(fle__akipb + [vof__wqp, gydlp__avp])


@intrinsic
def init_table(typingctx, table_type=None):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        pkfk__evgej = cgutils.create_struct_proxy(table_type)(context, builder)
        for nub__uoj, eujg__mry in table_type.type_to_blk.items():
            srojf__mawnf = context.get_constant_null(types.List(nub__uoj))
            setattr(pkfk__evgej, f'block_{eujg__mry}', srojf__mawnf)
        return pkfk__evgej._getvalue()
    sig = table_type(table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type=None):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    eujg__mry = get_overload_const_int(blk_type)
    arr_type = None
    for nub__uoj, hwmlh__jtvkw in table_type.type_to_blk.items():
        if hwmlh__jtvkw == eujg__mry:
            arr_type = nub__uoj
            break
    assert arr_type is not None, 'invalid table type block'
    hth__cchmv = types.List(arr_type)

    def codegen(context, builder, sig, args):
        pkfk__evgej = cgutils.create_struct_proxy(table_type)(context,
            builder, args[0])
        kqdcy__cqq = getattr(pkfk__evgej, f'block_{eujg__mry}')
        return impl_ret_borrowed(context, builder, hth__cchmv, kqdcy__cqq)
    sig = hth__cchmv(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_column_unboxed(typingctx, table_type, arr_list_t, ind_t,
    arr_ind_t=None):
    assert isinstance(table_type, TableType), 'table type expected'
    sig = types.none(table_type, arr_list_t, ind_t, arr_ind_t)
    return sig, ensure_column_unboxed_codegen


def ensure_column_unboxed_codegen(context, builder, sig, args):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table_arg, zkgx__vdvs, fwci__fxv, hcng__ueogm = args
    cqts__tdmx = context.get_python_api(builder)
    pkfk__evgej = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    rcmqr__sbg = cgutils.is_not_null(builder, pkfk__evgej.parent)
    ixtqj__hctkf = ListInstance(context, builder, sig.args[1], zkgx__vdvs)
    emyav__snar = ixtqj__hctkf.getitem(fwci__fxv)
    cqnys__qzqy = cgutils.alloca_once_value(builder, emyav__snar)
    whqmk__dkl = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    vlp__fnpyg = is_ll_eq(builder, cqnys__qzqy, whqmk__dkl)
    with builder.if_then(vlp__fnpyg):
        with builder.if_else(rcmqr__sbg) as (then, orelse):
            with then:
                fcyhf__pwu = get_df_obj_column_codegen(context, builder,
                    cqts__tdmx, pkfk__evgej.parent, hcng__ueogm, sig.args[1
                    ].dtype)
                php__cwcd = cqts__tdmx.to_native_value(sig.args[1].dtype,
                    fcyhf__pwu).value
                ixtqj__hctkf.inititem(fwci__fxv, php__cwcd, incref=False)
                cqts__tdmx.decref(fcyhf__pwu)
            with orelse:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type=None):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    eujg__mry = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, fjmo__joet, ysdlt__nsfu = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{eujg__mry}', fjmo__joet)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type=None):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, bqt__nwaeg = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = bqt__nwaeg
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type=None):
    assert isinstance(list_type, types.List), 'list type expected'

    def codegen(context, builder, sig, args):
        pxlm__kri = ListInstance(context, builder, list_type, args[0])
        nxgfl__yjj = pxlm__kri.size
        ysdlt__nsfu, rsc__eywoa = ListInstance.allocate_ex(context, builder,
            list_type, nxgfl__yjj)
        rsc__eywoa.size = nxgfl__yjj
        return rsc__eywoa.value
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
        ypqv__spqxr = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(ypqv__spqxr)
    return impl


def gen_table_filter(T, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    cigp__ssjg = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if used_cols is not None:
        cigp__ssjg['used_cols'] = np.array(used_cols, dtype=np.int64)
    tsskr__jjz = 'def impl(T, idx):\n'
    tsskr__jjz += f'  T2 = init_table(T)\n'
    tsskr__jjz += f'  l = 0\n'
    if used_cols is not None and len(used_cols) == 0:
        tsskr__jjz += f'  l = _get_idx_length(idx, len(T))\n'
        tsskr__jjz += f'  T2 = set_table_len(T2, l)\n'
        tsskr__jjz += f'  return T2\n'
        abp__tdoa = {}
        exec(tsskr__jjz, cigp__ssjg, abp__tdoa)
        return abp__tdoa['impl']
    if used_cols is not None:
        tsskr__jjz += f'  used_set = set(used_cols)\n'
    for eujg__mry in T.type_to_blk.values():
        cigp__ssjg[f'arr_inds_{eujg__mry}'] = np.array(T.block_to_arr_ind[
            eujg__mry], dtype=np.int64)
        tsskr__jjz += (
            f'  arr_list_{eujg__mry} = get_table_block(T, {eujg__mry})\n')
        tsskr__jjz += (
            f'  out_arr_list_{eujg__mry} = alloc_list_like(arr_list_{eujg__mry})\n'
            )
        tsskr__jjz += f'  for i in range(len(arr_list_{eujg__mry})):\n'
        tsskr__jjz += f'    arr_ind_{eujg__mry} = arr_inds_{eujg__mry}[i]\n'
        if used_cols is not None:
            tsskr__jjz += (
                f'    if arr_ind_{eujg__mry} not in used_set: continue\n')
        tsskr__jjz += f"""    ensure_column_unboxed(T, arr_list_{eujg__mry}, i, arr_ind_{eujg__mry})
"""
        tsskr__jjz += f"""    out_arr_{eujg__mry} = ensure_contig_if_np(arr_list_{eujg__mry}[i][idx])
"""
        tsskr__jjz += f'    l = len(out_arr_{eujg__mry})\n'
        tsskr__jjz += (
            f'    out_arr_list_{eujg__mry}[i] = out_arr_{eujg__mry}\n')
        tsskr__jjz += (
            f'  T2 = set_table_block(T2, out_arr_list_{eujg__mry}, {eujg__mry})\n'
            )
    tsskr__jjz += f'  T2 = set_table_len(T2, l)\n'
    tsskr__jjz += f'  return T2\n'
    abp__tdoa = {}
    exec(tsskr__jjz, cigp__ssjg, abp__tdoa)
    return abp__tdoa['impl']


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
        vunqa__ajyd = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        vunqa__ajyd = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            vunqa__ajyd.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        lcn__maes, grjxf__eem = args
        pkfk__evgej = cgutils.create_struct_proxy(table_type)(context, builder)
        pkfk__evgej.len = grjxf__eem
        fle__akipb = cgutils.unpack_tuple(builder, lcn__maes)
        for i, kqdcy__cqq in enumerate(fle__akipb):
            setattr(pkfk__evgej, f'block_{i}', kqdcy__cqq)
            context.nrt.incref(builder, types.List(vunqa__ajyd[i]), kqdcy__cqq)
        return pkfk__evgej._getvalue()
    table_type = TableType(tuple(vunqa__ajyd), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen
