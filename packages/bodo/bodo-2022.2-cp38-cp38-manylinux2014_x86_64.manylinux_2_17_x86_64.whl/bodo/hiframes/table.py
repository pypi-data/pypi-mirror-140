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
            bqjxf__fasny = 0
            rox__yriz = []
            for i in range(usecols[-1] + 1):
                if i == usecols[bqjxf__fasny]:
                    rox__yriz.append(arrs[bqjxf__fasny])
                    bqjxf__fasny += 1
                else:
                    rox__yriz.append(None)
            for nfpau__prhdg in range(usecols[-1] + 1, num_arrs):
                rox__yriz.append(None)
            self.arrays = rox__yriz
        else:
            self.arrays = arrs
        self.block_0 = arrs

    def __eq__(self, other):
        return isinstance(other, Table) and len(self.arrays) == len(other.
            arrays) and all((qqz__pgg == bevwm__mud).all() for qqz__pgg,
            bevwm__mud in zip(self.arrays, other.arrays))

    def __str__(self) ->str:
        return str(self.arrays)

    def to_pandas(self, index=None):
        qfym__hrl = len(self.arrays)
        dgo__dqydx = dict(zip(range(qfym__hrl), self.arrays))
        df = pd.DataFrame(dgo__dqydx, index)
        return df


class TableType(types.ArrayCompatible):

    def __init__(self, arr_types, has_runtime_cols=False):
        self.arr_types = arr_types
        self.has_runtime_cols = has_runtime_cols
        lan__xfig = []
        nxv__kubl = []
        nnk__iww = {}
        rvm__absfu = defaultdict(int)
        ufuot__xlfnb = defaultdict(list)
        if not has_runtime_cols:
            for i, xqtpq__wrpj in enumerate(arr_types):
                if xqtpq__wrpj not in nnk__iww:
                    nnk__iww[xqtpq__wrpj] = len(nnk__iww)
                fnw__ajwsf = nnk__iww[xqtpq__wrpj]
                lan__xfig.append(fnw__ajwsf)
                nxv__kubl.append(rvm__absfu[fnw__ajwsf])
                rvm__absfu[fnw__ajwsf] += 1
                ufuot__xlfnb[fnw__ajwsf].append(i)
        self.block_nums = lan__xfig
        self.block_offsets = nxv__kubl
        self.type_to_blk = nnk__iww
        self.block_to_arr_ind = ufuot__xlfnb
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
    return TableType(tuple(numba.typeof(yswo__mluux) for yswo__mluux in val
        .arrays))


@register_model(TableType)
class TableTypeModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        if fe_type.has_runtime_cols:
            vybt__qgj = [(f'block_{i}', types.List(xqtpq__wrpj)) for i,
                xqtpq__wrpj in enumerate(fe_type.arr_types)]
        else:
            vybt__qgj = [(f'block_{fnw__ajwsf}', types.List(xqtpq__wrpj)) for
                xqtpq__wrpj, fnw__ajwsf in fe_type.type_to_blk.items()]
        vybt__qgj.append(('parent', types.pyobject))
        vybt__qgj.append(('len', types.int64))
        super(TableTypeModel, self).__init__(dmm, fe_type, vybt__qgj)


make_attribute_wrapper(TableType, 'block_0', 'block_0')
make_attribute_wrapper(TableType, 'len', '_len')


@infer_getattr
class TableTypeAttribute(OverloadedKeyAttributeTemplate):
    key = TableType

    def resolve_shape(self, df):
        return types.Tuple([types.int64, types.int64])


@unbox(TableType)
def unbox_table(typ, val, c):
    quta__vhv = c.pyapi.object_getattr_string(val, 'arrays')
    oet__xeq = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    oet__xeq.parent = cgutils.get_null_value(oet__xeq.parent.type)
    mfr__ggtse = c.pyapi.make_none()
    hrj__ijju = c.context.get_constant(types.int64, 0)
    hjg__bfq = cgutils.alloca_once_value(c.builder, hrj__ijju)
    for xqtpq__wrpj, fnw__ajwsf in typ.type_to_blk.items():
        dzcl__dquhj = c.context.get_constant(types.int64, len(typ.
            block_to_arr_ind[fnw__ajwsf]))
        nfpau__prhdg, xhkb__kdfk = ListInstance.allocate_ex(c.context, c.
            builder, types.List(xqtpq__wrpj), dzcl__dquhj)
        xhkb__kdfk.size = dzcl__dquhj
        yys__uueg = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[fnw__ajwsf],
            dtype=np.int64))
        wrw__kcis = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, yys__uueg)
        with cgutils.for_range(c.builder, dzcl__dquhj) as loop:
            i = loop.index
            fjxdd__qmxft = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), wrw__kcis, i)
            gsuy__slduw = c.pyapi.long_from_longlong(fjxdd__qmxft)
            xab__klrhb = c.pyapi.object_getitem(quta__vhv, gsuy__slduw)
            igd__taiub = c.builder.icmp_unsigned('==', xab__klrhb, mfr__ggtse)
            with c.builder.if_else(igd__taiub) as (then, orelse):
                with then:
                    wynbl__qxc = c.context.get_constant_null(xqtpq__wrpj)
                    xhkb__kdfk.inititem(i, wynbl__qxc, incref=False)
                with orelse:
                    nodps__xie = c.pyapi.call_method(xab__klrhb, '__len__', ())
                    xxppo__gub = c.pyapi.long_as_longlong(nodps__xie)
                    c.builder.store(xxppo__gub, hjg__bfq)
                    c.pyapi.decref(nodps__xie)
                    yswo__mluux = c.pyapi.to_native_value(xqtpq__wrpj,
                        xab__klrhb).value
                    xhkb__kdfk.inititem(i, yswo__mluux, incref=False)
            c.pyapi.decref(xab__klrhb)
            c.pyapi.decref(gsuy__slduw)
        setattr(oet__xeq, f'block_{fnw__ajwsf}', xhkb__kdfk.value)
    oet__xeq.len = c.builder.load(hjg__bfq)
    c.pyapi.decref(quta__vhv)
    c.pyapi.decref(mfr__ggtse)
    zity__rmw = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(oet__xeq._getvalue(), is_error=zity__rmw)


@box(TableType)
def box_table(typ, val, c, ensure_unboxed=None):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    oet__xeq = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    if typ.has_runtime_cols:
        tlfg__pqy = c.context.get_constant(types.int64, 0)
        for i, xqtpq__wrpj in enumerate(typ.arr_types):
            rox__yriz = getattr(oet__xeq, f'block_{i}')
            kno__xtco = ListInstance(c.context, c.builder, types.List(
                xqtpq__wrpj), rox__yriz)
            tlfg__pqy = c.builder.add(tlfg__pqy, kno__xtco.size)
        aqk__aan = c.pyapi.list_new(tlfg__pqy)
        mpr__fxkp = c.context.get_constant(types.int64, 0)
        for i, xqtpq__wrpj in enumerate(typ.arr_types):
            rox__yriz = getattr(oet__xeq, f'block_{i}')
            kno__xtco = ListInstance(c.context, c.builder, types.List(
                xqtpq__wrpj), rox__yriz)
            with cgutils.for_range(c.builder, kno__xtco.size) as loop:
                i = loop.index
                yswo__mluux = kno__xtco.getitem(i)
                c.context.nrt.incref(c.builder, xqtpq__wrpj, yswo__mluux)
                idx = c.builder.add(mpr__fxkp, i)
                c.pyapi.list_setitem(aqk__aan, idx, c.pyapi.
                    from_native_value(xqtpq__wrpj, yswo__mluux, c.env_manager))
            mpr__fxkp = c.builder.add(mpr__fxkp, kno__xtco.size)
        hzavj__owlyx = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
        mnn__qpow = c.pyapi.call_function_objargs(hzavj__owlyx, (aqk__aan,))
        c.pyapi.decref(hzavj__owlyx)
        c.pyapi.decref(aqk__aan)
        c.context.nrt.decref(c.builder, typ, val)
        return mnn__qpow
    aqk__aan = c.pyapi.list_new(c.context.get_constant(types.int64, len(typ
        .arr_types)))
    ldetx__urfg = cgutils.is_not_null(c.builder, oet__xeq.parent)
    if ensure_unboxed is None:
        ensure_unboxed = c.context.get_constant(types.bool_, False)
    for xqtpq__wrpj, fnw__ajwsf in typ.type_to_blk.items():
        rox__yriz = getattr(oet__xeq, f'block_{fnw__ajwsf}')
        kno__xtco = ListInstance(c.context, c.builder, types.List(
            xqtpq__wrpj), rox__yriz)
        yys__uueg = c.context.make_constant_array(c.builder, types.Array(
            types.int64, 1, 'C'), np.array(typ.block_to_arr_ind[fnw__ajwsf],
            dtype=np.int64))
        wrw__kcis = c.context.make_array(types.Array(types.int64, 1, 'C'))(c
            .context, c.builder, yys__uueg)
        with cgutils.for_range(c.builder, kno__xtco.size) as loop:
            i = loop.index
            fjxdd__qmxft = _getitem_array_single_int(c.context, c.builder,
                types.int64, types.Array(types.int64, 1, 'C'), wrw__kcis, i)
            yswo__mluux = kno__xtco.getitem(i)
            mgooh__hqur = cgutils.alloca_once_value(c.builder, yswo__mluux)
            sge__gcvmg = cgutils.alloca_once_value(c.builder, c.context.
                get_constant_null(xqtpq__wrpj))
            yqs__nqidb = is_ll_eq(c.builder, mgooh__hqur, sge__gcvmg)
            with c.builder.if_else(c.builder.and_(yqs__nqidb, c.builder.
                not_(ensure_unboxed))) as (then, orelse):
                with then:
                    mfr__ggtse = c.pyapi.make_none()
                    c.pyapi.list_setitem(aqk__aan, fjxdd__qmxft, mfr__ggtse)
                with orelse:
                    xab__klrhb = cgutils.alloca_once(c.builder, c.context.
                        get_value_type(types.pyobject))
                    with c.builder.if_else(c.builder.and_(yqs__nqidb,
                        ldetx__urfg)) as (arr_then, arr_orelse):
                        with arr_then:
                            nmd__vwinz = get_df_obj_column_codegen(c.
                                context, c.builder, c.pyapi, oet__xeq.
                                parent, fjxdd__qmxft, xqtpq__wrpj)
                            c.builder.store(nmd__vwinz, xab__klrhb)
                        with arr_orelse:
                            c.context.nrt.incref(c.builder, xqtpq__wrpj,
                                yswo__mluux)
                            c.builder.store(c.pyapi.from_native_value(
                                xqtpq__wrpj, yswo__mluux, c.env_manager),
                                xab__klrhb)
                    c.pyapi.list_setitem(aqk__aan, fjxdd__qmxft, c.builder.
                        load(xab__klrhb))
    hzavj__owlyx = c.pyapi.unserialize(c.pyapi.serialize_object(Table))
    mnn__qpow = c.pyapi.call_function_objargs(hzavj__owlyx, (aqk__aan,))
    c.pyapi.decref(hzavj__owlyx)
    c.pyapi.decref(aqk__aan)
    c.context.nrt.decref(c.builder, typ, val)
    return mnn__qpow


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
        oet__xeq = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        wfr__vne = context.get_constant(types.int64, 0)
        for i, xqtpq__wrpj in enumerate(table_type.arr_types):
            rox__yriz = getattr(oet__xeq, f'block_{i}')
            kno__xtco = ListInstance(context, builder, types.List(
                xqtpq__wrpj), rox__yriz)
            wfr__vne = builder.add(wfr__vne, kno__xtco.size)
        return wfr__vne
    sig = types.int64(table_type)
    return sig, codegen


def get_table_data_codegen(context, builder, table_arg, col_ind, table_type):
    arr_type = table_type.arr_types[col_ind]
    oet__xeq = cgutils.create_struct_proxy(table_type)(context, builder,
        table_arg)
    fnw__ajwsf = table_type.block_nums[col_ind]
    gdkdm__vbmur = table_type.block_offsets[col_ind]
    rox__yriz = getattr(oet__xeq, f'block_{fnw__ajwsf}')
    kno__xtco = ListInstance(context, builder, types.List(arr_type), rox__yriz)
    yswo__mluux = kno__xtco.getitem(gdkdm__vbmur)
    return yswo__mluux


@intrinsic
def get_table_data(typingctx, table_type, ind_typ=None):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, nfpau__prhdg = args
        yswo__mluux = get_table_data_codegen(context, builder, table_arg,
            col_ind, table_type)
        return impl_ret_borrowed(context, builder, arr_type, yswo__mluux)
    sig = arr_type(table_type, ind_typ)
    return sig, codegen


@intrinsic
def del_column(typingctx, table_type, ind_typ=None):
    assert isinstance(table_type, TableType)
    assert is_overload_constant_int(ind_typ)
    col_ind = get_overload_const_int(ind_typ)
    arr_type = table_type.arr_types[col_ind]

    def codegen(context, builder, sig, args):
        table_arg, nfpau__prhdg = args
        oet__xeq = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        fnw__ajwsf = table_type.block_nums[col_ind]
        gdkdm__vbmur = table_type.block_offsets[col_ind]
        rox__yriz = getattr(oet__xeq, f'block_{fnw__ajwsf}')
        kno__xtco = ListInstance(context, builder, types.List(arr_type),
            rox__yriz)
        yswo__mluux = kno__xtco.getitem(gdkdm__vbmur)
        context.nrt.decref(builder, arr_type, yswo__mluux)
        wynbl__qxc = context.get_constant_null(arr_type)
        kno__xtco.inititem(gdkdm__vbmur, wynbl__qxc, incref=False)
    sig = types.void(table_type, ind_typ)
    return sig, codegen


def set_table_data_codegen(context, builder, in_table_type, in_table,
    out_table_type, arr_type, arr_arg, col_ind, is_new_col):
    in_table = cgutils.create_struct_proxy(in_table_type)(context, builder,
        in_table)
    out_table = cgutils.create_struct_proxy(out_table_type)(context, builder)
    out_table.len = in_table.len
    out_table.parent = in_table.parent
    hrj__ijju = context.get_constant(types.int64, 0)
    ksh__ixvl = context.get_constant(types.int64, 1)
    bkax__axl = arr_type not in in_table_type.type_to_blk
    for xqtpq__wrpj, fnw__ajwsf in out_table_type.type_to_blk.items():
        if xqtpq__wrpj in in_table_type.type_to_blk:
            dqg__cvfw = in_table_type.type_to_blk[xqtpq__wrpj]
            xhkb__kdfk = ListInstance(context, builder, types.List(
                xqtpq__wrpj), getattr(in_table, f'block_{dqg__cvfw}'))
            context.nrt.incref(builder, types.List(xqtpq__wrpj), xhkb__kdfk
                .value)
            setattr(out_table, f'block_{fnw__ajwsf}', xhkb__kdfk.value)
    if bkax__axl:
        nfpau__prhdg, xhkb__kdfk = ListInstance.allocate_ex(context,
            builder, types.List(arr_type), ksh__ixvl)
        xhkb__kdfk.size = ksh__ixvl
        xhkb__kdfk.inititem(hrj__ijju, arr_arg, incref=True)
        fnw__ajwsf = out_table_type.type_to_blk[arr_type]
        setattr(out_table, f'block_{fnw__ajwsf}', xhkb__kdfk.value)
        if not is_new_col:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
    else:
        fnw__ajwsf = out_table_type.type_to_blk[arr_type]
        xhkb__kdfk = ListInstance(context, builder, types.List(arr_type),
            getattr(out_table, f'block_{fnw__ajwsf}'))
        if is_new_col:
            n = xhkb__kdfk.size
            nrewe__rkm = builder.add(n, ksh__ixvl)
            xhkb__kdfk.resize(nrewe__rkm)
            xhkb__kdfk.inititem(n, arr_arg, incref=True)
        elif arr_type == in_table_type.arr_types[col_ind]:
            csaf__ozem = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            xhkb__kdfk.setitem(csaf__ozem, arr_arg, True)
        else:
            _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
                context, builder)
            csaf__ozem = context.get_constant(types.int64, out_table_type.
                block_offsets[col_ind])
            n = xhkb__kdfk.size
            nrewe__rkm = builder.add(n, ksh__ixvl)
            xhkb__kdfk.resize(nrewe__rkm)
            context.nrt.incref(builder, arr_type, xhkb__kdfk.getitem(
                csaf__ozem))
            xhkb__kdfk.move(builder.add(csaf__ozem, ksh__ixvl), csaf__ozem,
                builder.sub(n, csaf__ozem))
            xhkb__kdfk.setitem(csaf__ozem, arr_arg, incref=True)
    return out_table._getvalue()


def _rm_old_array(col_ind, out_table_type, out_table, in_table_type,
    context, builder):
    ymlsr__wiph = in_table_type.arr_types[col_ind]
    if ymlsr__wiph in out_table_type.type_to_blk:
        fnw__ajwsf = out_table_type.type_to_blk[ymlsr__wiph]
        yqej__fgx = getattr(out_table, f'block_{fnw__ajwsf}')
        hnn__wlw = types.List(ymlsr__wiph)
        csaf__ozem = context.get_constant(types.int64, in_table_type.
            block_offsets[col_ind])
        mhfw__fwyf = hnn__wlw.dtype(hnn__wlw, types.intp)
        eiyck__xhj = context.compile_internal(builder, lambda lst, i: lst.
            pop(i), mhfw__fwyf, (yqej__fgx, csaf__ozem))
        context.nrt.decref(builder, ymlsr__wiph, eiyck__xhj)


@intrinsic
def set_table_data(typingctx, table_type, ind_type, arr_type=None):
    assert isinstance(table_type, TableType), 'invalid input to set_table_data'
    assert is_overload_constant_int(ind_type
        ), 'set_table_data expects const index'
    col_ind = get_overload_const_int(ind_type)
    is_new_col = col_ind == len(table_type.arr_types)
    sadq__jfj = list(table_type.arr_types)
    if is_new_col:
        sadq__jfj.append(arr_type)
    else:
        sadq__jfj[col_ind] = arr_type
    out_table_type = TableType(tuple(sadq__jfj))

    def codegen(context, builder, sig, args):
        table_arg, nfpau__prhdg, ngrej__fxa = args
        out_table = set_table_data_codegen(context, builder, table_type,
            table_arg, out_table_type, arr_type, ngrej__fxa, col_ind,
            is_new_col)
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
    qmmn__vclgp = args[0]
    if equiv_set.has_shape(qmmn__vclgp):
        return ArrayAnalysis.AnalyzeResult(shape=equiv_set.get_shape(
            qmmn__vclgp)[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_hiframes_table_get_table_data = (
    get_table_data_equiv)


@lower_constant(TableType)
def lower_constant_table(context, builder, table_type, pyval):
    aoyt__rjl = []
    for xqtpq__wrpj, fnw__ajwsf in table_type.type_to_blk.items():
        arvb__atxdw = len(table_type.block_to_arr_ind[fnw__ajwsf])
        ugqa__mmt = []
        for i in range(arvb__atxdw):
            fjxdd__qmxft = table_type.block_to_arr_ind[fnw__ajwsf][i]
            ugqa__mmt.append(pyval.arrays[fjxdd__qmxft])
        aoyt__rjl.append(context.get_constant_generic(builder, types.List(
            xqtpq__wrpj), ugqa__mmt))
    jzbwp__kepgg = context.get_constant_null(types.pyobject)
    tiu__akdsw = context.get_constant(types.int64, 0 if len(pyval.arrays) ==
        0 else len(pyval.arrays[0]))
    return lir.Constant.literal_struct(aoyt__rjl + [jzbwp__kepgg, tiu__akdsw])


@intrinsic
def init_table(typingctx, table_type=None):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        oet__xeq = cgutils.create_struct_proxy(table_type)(context, builder)
        for xqtpq__wrpj, fnw__ajwsf in table_type.type_to_blk.items():
            mwvfe__gki = context.get_constant_null(types.List(xqtpq__wrpj))
            setattr(oet__xeq, f'block_{fnw__ajwsf}', mwvfe__gki)
        return oet__xeq._getvalue()
    sig = table_type(table_type)
    return sig, codegen


@intrinsic
def get_table_block(typingctx, table_type, blk_type=None):
    assert isinstance(table_type, TableType), 'table type expected'
    assert is_overload_constant_int(blk_type)
    fnw__ajwsf = get_overload_const_int(blk_type)
    arr_type = None
    for xqtpq__wrpj, bevwm__mud in table_type.type_to_blk.items():
        if bevwm__mud == fnw__ajwsf:
            arr_type = xqtpq__wrpj
            break
    assert arr_type is not None, 'invalid table type block'
    ailj__pgt = types.List(arr_type)

    def codegen(context, builder, sig, args):
        oet__xeq = cgutils.create_struct_proxy(table_type)(context, builder,
            args[0])
        rox__yriz = getattr(oet__xeq, f'block_{fnw__ajwsf}')
        return impl_ret_borrowed(context, builder, ailj__pgt, rox__yriz)
    sig = ailj__pgt(table_type, blk_type)
    return sig, codegen


@intrinsic
def ensure_column_unboxed(typingctx, table_type, arr_list_t, ind_t,
    arr_ind_t=None):
    assert isinstance(table_type, TableType), 'table type expected'
    sig = types.none(table_type, arr_list_t, ind_t, arr_ind_t)
    return sig, ensure_column_unboxed_codegen


def ensure_column_unboxed_codegen(context, builder, sig, args):
    from bodo.hiframes.boxing import get_df_obj_column_codegen
    table_arg, gfcx__icd, cwe__yin, wqf__ovrpw = args
    aaiix__xwk = context.get_python_api(builder)
    oet__xeq = cgutils.create_struct_proxy(sig.args[0])(context, builder,
        table_arg)
    ldetx__urfg = cgutils.is_not_null(builder, oet__xeq.parent)
    kno__xtco = ListInstance(context, builder, sig.args[1], gfcx__icd)
    gnczf__uhrk = kno__xtco.getitem(cwe__yin)
    mgooh__hqur = cgutils.alloca_once_value(builder, gnczf__uhrk)
    sge__gcvmg = cgutils.alloca_once_value(builder, context.
        get_constant_null(sig.args[1].dtype))
    yqs__nqidb = is_ll_eq(builder, mgooh__hqur, sge__gcvmg)
    with builder.if_then(yqs__nqidb):
        with builder.if_else(ldetx__urfg) as (then, orelse):
            with then:
                xab__klrhb = get_df_obj_column_codegen(context, builder,
                    aaiix__xwk, oet__xeq.parent, wqf__ovrpw, sig.args[1].dtype)
                yswo__mluux = aaiix__xwk.to_native_value(sig.args[1].dtype,
                    xab__klrhb).value
                kno__xtco.inititem(cwe__yin, yswo__mluux, incref=False)
                aaiix__xwk.decref(xab__klrhb)
            with orelse:
                context.call_conv.return_user_exc(builder, BodoError, (
                    'unexpected null table column',))


@intrinsic
def set_table_block(typingctx, table_type, arr_list_type, blk_type=None):
    assert isinstance(table_type, TableType), 'table type expected'
    assert isinstance(arr_list_type, types.List), 'list type expected'
    assert is_overload_constant_int(blk_type), 'blk should be const int'
    fnw__ajwsf = get_overload_const_int(blk_type)

    def codegen(context, builder, sig, args):
        table_arg, dhq__aee, nfpau__prhdg = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        setattr(in_table, f'block_{fnw__ajwsf}', dhq__aee)
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, arr_list_type, blk_type)
    return sig, codegen


@intrinsic
def set_table_len(typingctx, table_type, l_type=None):
    assert isinstance(table_type, TableType), 'table type expected'

    def codegen(context, builder, sig, args):
        table_arg, clb__zvje = args
        in_table = cgutils.create_struct_proxy(table_type)(context, builder,
            table_arg)
        in_table.len = clb__zvje
        return impl_ret_borrowed(context, builder, table_type, in_table.
            _getvalue())
    sig = table_type(table_type, l_type)
    return sig, codegen


@intrinsic
def alloc_list_like(typingctx, list_type=None):
    assert isinstance(list_type, types.List), 'list type expected'

    def codegen(context, builder, sig, args):
        rbjbb__igdy = ListInstance(context, builder, list_type, args[0])
        rgv__ethet = rbjbb__igdy.size
        nfpau__prhdg, xhkb__kdfk = ListInstance.allocate_ex(context,
            builder, list_type, rgv__ethet)
        xhkb__kdfk.size = rgv__ethet
        return xhkb__kdfk.value
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
        nryj__nee = numba.cpython.unicode._normalize_slice(idx, n)
        return numba.cpython.unicode._slice_span(nryj__nee)
    return impl


def gen_table_filter(T, used_cols=None):
    from bodo.utils.conversion import ensure_contig_if_np
    btv__xvtsa = {'init_table': init_table, 'get_table_block':
        get_table_block, 'ensure_column_unboxed': ensure_column_unboxed,
        'set_table_block': set_table_block, 'set_table_len': set_table_len,
        'alloc_list_like': alloc_list_like, '_get_idx_length':
        _get_idx_length, 'ensure_contig_if_np': ensure_contig_if_np}
    if used_cols is not None:
        btv__xvtsa['used_cols'] = np.array(used_cols, dtype=np.int64)
    gav__csup = 'def impl(T, idx):\n'
    gav__csup += f'  T2 = init_table(T)\n'
    gav__csup += f'  l = 0\n'
    if used_cols is not None and len(used_cols) == 0:
        gav__csup += f'  l = _get_idx_length(idx, len(T))\n'
        gav__csup += f'  T2 = set_table_len(T2, l)\n'
        gav__csup += f'  return T2\n'
        ywurt__jhg = {}
        exec(gav__csup, btv__xvtsa, ywurt__jhg)
        return ywurt__jhg['impl']
    if used_cols is not None:
        gav__csup += f'  used_set = set(used_cols)\n'
    for fnw__ajwsf in T.type_to_blk.values():
        btv__xvtsa[f'arr_inds_{fnw__ajwsf}'] = np.array(T.block_to_arr_ind[
            fnw__ajwsf], dtype=np.int64)
        gav__csup += (
            f'  arr_list_{fnw__ajwsf} = get_table_block(T, {fnw__ajwsf})\n')
        gav__csup += (
            f'  out_arr_list_{fnw__ajwsf} = alloc_list_like(arr_list_{fnw__ajwsf})\n'
            )
        gav__csup += f'  for i in range(len(arr_list_{fnw__ajwsf})):\n'
        gav__csup += f'    arr_ind_{fnw__ajwsf} = arr_inds_{fnw__ajwsf}[i]\n'
        if used_cols is not None:
            gav__csup += (
                f'    if arr_ind_{fnw__ajwsf} not in used_set: continue\n')
        gav__csup += f"""    ensure_column_unboxed(T, arr_list_{fnw__ajwsf}, i, arr_ind_{fnw__ajwsf})
"""
        gav__csup += f"""    out_arr_{fnw__ajwsf} = ensure_contig_if_np(arr_list_{fnw__ajwsf}[i][idx])
"""
        gav__csup += f'    l = len(out_arr_{fnw__ajwsf})\n'
        gav__csup += (
            f'    out_arr_list_{fnw__ajwsf}[i] = out_arr_{fnw__ajwsf}\n')
        gav__csup += (
            f'  T2 = set_table_block(T2, out_arr_list_{fnw__ajwsf}, {fnw__ajwsf})\n'
            )
    gav__csup += f'  T2 = set_table_len(T2, l)\n'
    gav__csup += f'  return T2\n'
    ywurt__jhg = {}
    exec(gav__csup, btv__xvtsa, ywurt__jhg)
    return ywurt__jhg['impl']


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
        ksclx__moprb = [arr_list_tup_typ.dtype.dtype] * len(arr_list_tup_typ)
    else:
        ksclx__moprb = []
        for typ in arr_list_tup_typ:
            if typ.dtype == types.undefined:
                return
            ksclx__moprb.append(typ.dtype)
    assert isinstance(nrows_typ, types.Integer
        ), 'init_runtime_table_from_lists requires an integer length'

    def codegen(context, builder, sig, args):
        ownz__ezhq, nugw__jyd = args
        oet__xeq = cgutils.create_struct_proxy(table_type)(context, builder)
        oet__xeq.len = nugw__jyd
        aoyt__rjl = cgutils.unpack_tuple(builder, ownz__ezhq)
        for i, rox__yriz in enumerate(aoyt__rjl):
            setattr(oet__xeq, f'block_{i}', rox__yriz)
            context.nrt.incref(builder, types.List(ksclx__moprb[i]), rox__yriz)
        return oet__xeq._getvalue()
    table_type = TableType(tuple(ksclx__moprb), True)
    sig = table_type(arr_list_tup_typ, nrows_typ)
    return sig, codegen
