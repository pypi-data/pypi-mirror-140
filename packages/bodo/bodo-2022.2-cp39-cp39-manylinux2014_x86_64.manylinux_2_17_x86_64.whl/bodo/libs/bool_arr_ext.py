"""Nullable boolean array that stores data in Numpy format (1 byte per value)
but nulls are stored in bit arrays (1 bit per value) similar to Arrow's nulls.
Pandas converts boolean array to object when NAs are introduced.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, lower_constant
from numba.core.typing.templates import AbstractTemplate, infer_global
from numba.extending import NativeValue, box, intrinsic, lower_builtin, lower_cast, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, type_callable, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs import hstr_ext
from bodo.libs.str_arr_ext import string_array_type
from bodo.utils.typing import is_list_like_index_type
ll.add_symbol('is_bool_array', hstr_ext.is_bool_array)
ll.add_symbol('is_pd_boolean_array', hstr_ext.is_pd_boolean_array)
ll.add_symbol('unbox_bool_array_obj', hstr_ext.unbox_bool_array_obj)
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, is_iterable_type, is_overload_false, is_overload_true, parse_dtype, raise_bodo_error


class BooleanArrayType(types.ArrayCompatible):

    def __init__(self):
        super(BooleanArrayType, self).__init__(name='BooleanArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.bool_

    def copy(self):
        return BooleanArrayType()


boolean_array = BooleanArrayType()


@typeof_impl.register(pd.arrays.BooleanArray)
def typeof_boolean_array(val, c):
    return boolean_array


data_type = types.Array(types.bool_, 1, 'C')
nulls_type = types.Array(types.uint8, 1, 'C')


@register_model(BooleanArrayType)
class BooleanArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zujqn__crztv = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, zujqn__crztv)


make_attribute_wrapper(BooleanArrayType, 'data', '_data')
make_attribute_wrapper(BooleanArrayType, 'null_bitmap', '_null_bitmap')


class BooleanDtype(types.Number):

    def __init__(self):
        self.dtype = types.bool_
        super(BooleanDtype, self).__init__('BooleanDtype')


boolean_dtype = BooleanDtype()
register_model(BooleanDtype)(models.OpaqueModel)


@box(BooleanDtype)
def box_boolean_dtype(typ, val, c):
    eoyjn__xsdy = c.context.insert_const_string(c.builder.module, 'pandas')
    owmen__ztaok = c.pyapi.import_module_noblock(eoyjn__xsdy)
    wag__lwuo = c.pyapi.call_method(owmen__ztaok, 'BooleanDtype', ())
    c.pyapi.decref(owmen__ztaok)
    return wag__lwuo


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    wne__iqppi = n + 7 >> 3
    return np.full(wne__iqppi, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    scml__owwx = c.context.typing_context.resolve_value_type(func)
    awzm__zuf = scml__owwx.get_call_type(c.context.typing_context, arg_typs, {}
        )
    nfty__whho = c.context.get_function(scml__owwx, awzm__zuf)
    pelvp__famh = c.context.call_conv.get_function_type(awzm__zuf.
        return_type, awzm__zuf.args)
    pxth__vmpy = c.builder.module
    qhiun__tltd = lir.Function(pxth__vmpy, pelvp__famh, name=pxth__vmpy.
        get_unique_name('.func_conv'))
    qhiun__tltd.linkage = 'internal'
    ksf__oqh = lir.IRBuilder(qhiun__tltd.append_basic_block())
    fjucn__bcy = c.context.call_conv.decode_arguments(ksf__oqh, awzm__zuf.
        args, qhiun__tltd)
    jtax__dfkw = nfty__whho(ksf__oqh, fjucn__bcy)
    c.context.call_conv.return_value(ksf__oqh, jtax__dfkw)
    njxm__vvl, qcur__wtze = c.context.call_conv.call_function(c.builder,
        qhiun__tltd, awzm__zuf.return_type, awzm__zuf.args, args)
    return qcur__wtze


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    vhqvg__frle = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(vhqvg__frle)
    c.pyapi.decref(vhqvg__frle)
    pelvp__famh = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    rmd__fgde = cgutils.get_or_insert_function(c.builder.module,
        pelvp__famh, name='is_bool_array')
    pelvp__famh = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
        as_pointer()])
    qhiun__tltd = cgutils.get_or_insert_function(c.builder.module,
        pelvp__famh, name='is_pd_boolean_array')
    zhki__nmuk = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    qem__vlwg = c.builder.call(qhiun__tltd, [obj])
    cso__ycgv = c.builder.icmp_unsigned('!=', qem__vlwg, qem__vlwg.type(0))
    with c.builder.if_else(cso__ycgv) as (pd_then, pd_otherwise):
        with pd_then:
            rje__kga = c.pyapi.object_getattr_string(obj, '_data')
            zhki__nmuk.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), rje__kga).value
            kxpkw__ptjr = c.pyapi.object_getattr_string(obj, '_mask')
            gtzyg__vwcyb = c.pyapi.to_native_value(types.Array(types.bool_,
                1, 'C'), kxpkw__ptjr).value
            wne__iqppi = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            rhad__qmwgq = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, gtzyg__vwcyb)
            aexqr__rnbgc = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [wne__iqppi])
            pelvp__famh = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            qhiun__tltd = cgutils.get_or_insert_function(c.builder.module,
                pelvp__famh, name='mask_arr_to_bitmap')
            c.builder.call(qhiun__tltd, [aexqr__rnbgc.data, rhad__qmwgq.
                data, n])
            zhki__nmuk.null_bitmap = aexqr__rnbgc._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), gtzyg__vwcyb)
            c.pyapi.decref(rje__kga)
            c.pyapi.decref(kxpkw__ptjr)
        with pd_otherwise:
            sytiv__ctne = c.builder.call(rmd__fgde, [obj])
            dtaj__hogq = c.builder.icmp_unsigned('!=', sytiv__ctne,
                sytiv__ctne.type(0))
            with c.builder.if_else(dtaj__hogq) as (then, otherwise):
                with then:
                    zhki__nmuk.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    zhki__nmuk.null_bitmap = call_func_in_unbox(gen_full_bitmap
                        , (n,), (types.int64,), c)
                with otherwise:
                    zhki__nmuk.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    wne__iqppi = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    zhki__nmuk.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [wne__iqppi])._getvalue()
                    vdbu__wsc = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, zhki__nmuk.data
                        ).data
                    sxk__fjysw = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, zhki__nmuk.
                        null_bitmap).data
                    pelvp__famh = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    qhiun__tltd = cgutils.get_or_insert_function(c.builder.
                        module, pelvp__famh, name='unbox_bool_array_obj')
                    c.builder.call(qhiun__tltd, [obj, vdbu__wsc, sxk__fjysw, n]
                        )
    return NativeValue(zhki__nmuk._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    zhki__nmuk = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        zhki__nmuk.data, c.env_manager)
    nol__hdn = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, zhki__nmuk.null_bitmap).data
    vhqvg__frle = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(vhqvg__frle)
    eoyjn__xsdy = c.context.insert_const_string(c.builder.module, 'numpy')
    evijs__ibstx = c.pyapi.import_module_noblock(eoyjn__xsdy)
    smne__gzlrv = c.pyapi.object_getattr_string(evijs__ibstx, 'bool_')
    gtzyg__vwcyb = c.pyapi.call_method(evijs__ibstx, 'empty', (vhqvg__frle,
        smne__gzlrv))
    wsyk__kqsaz = c.pyapi.object_getattr_string(gtzyg__vwcyb, 'ctypes')
    umayt__agfwh = c.pyapi.object_getattr_string(wsyk__kqsaz, 'data')
    gmy__qwc = c.builder.inttoptr(c.pyapi.long_as_longlong(umayt__agfwh),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as loop:
        btdiw__hdph = loop.index
        inxi__ogkou = c.builder.lshr(btdiw__hdph, lir.Constant(lir.IntType(
            64), 3))
        repq__xhi = c.builder.load(cgutils.gep(c.builder, nol__hdn,
            inxi__ogkou))
        ccz__czc = c.builder.trunc(c.builder.and_(btdiw__hdph, lir.Constant
            (lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(repq__xhi, ccz__czc), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        wja__jbf = cgutils.gep(c.builder, gmy__qwc, btdiw__hdph)
        c.builder.store(val, wja__jbf)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        zhki__nmuk.null_bitmap)
    eoyjn__xsdy = c.context.insert_const_string(c.builder.module, 'pandas')
    owmen__ztaok = c.pyapi.import_module_noblock(eoyjn__xsdy)
    tckt__woji = c.pyapi.object_getattr_string(owmen__ztaok, 'arrays')
    wag__lwuo = c.pyapi.call_method(tckt__woji, 'BooleanArray', (data,
        gtzyg__vwcyb))
    c.pyapi.decref(owmen__ztaok)
    c.pyapi.decref(vhqvg__frle)
    c.pyapi.decref(evijs__ibstx)
    c.pyapi.decref(smne__gzlrv)
    c.pyapi.decref(wsyk__kqsaz)
    c.pyapi.decref(umayt__agfwh)
    c.pyapi.decref(tckt__woji)
    c.pyapi.decref(data)
    c.pyapi.decref(gtzyg__vwcyb)
    return wag__lwuo


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    ajtm__qxpo = np.empty(n, np.bool_)
    jehmm__zjv = np.empty(n + 7 >> 3, np.uint8)
    for btdiw__hdph, s in enumerate(pyval):
        cood__cul = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(jehmm__zjv, btdiw__hdph, int(
            not cood__cul))
        if not cood__cul:
            ajtm__qxpo[btdiw__hdph] = s
    ezx__squ = context.get_constant_generic(builder, data_type, ajtm__qxpo)
    ctqhc__qyk = context.get_constant_generic(builder, nulls_type, jehmm__zjv)
    return lir.Constant.literal_struct([ezx__squ, ctqhc__qyk])


def lower_init_bool_array(context, builder, signature, args):
    snp__igu, haujm__poygr = args
    zhki__nmuk = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    zhki__nmuk.data = snp__igu
    zhki__nmuk.null_bitmap = haujm__poygr
    context.nrt.incref(builder, signature.args[0], snp__igu)
    context.nrt.incref(builder, signature.args[1], haujm__poygr)
    return zhki__nmuk._getvalue()


@intrinsic
def init_bool_array(typingctx, data, null_bitmap=None):
    assert data == types.Array(types.bool_, 1, 'C')
    assert null_bitmap == types.Array(types.uint8, 1, 'C')
    sig = boolean_array(data, null_bitmap)
    return sig, lower_init_bool_array


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_bool_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_bool_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_bool_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    tgwb__vli = args[0]
    if equiv_set.has_shape(tgwb__vli):
        return ArrayAnalysis.AnalyzeResult(shape=tgwb__vli, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    tgwb__vli = args[0]
    if equiv_set.has_shape(tgwb__vli):
        return ArrayAnalysis.AnalyzeResult(shape=tgwb__vli, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_init_bool_array = (
    init_bool_array_equiv)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


def alias_ext_init_bool_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_bool_array',
    'bodo.libs.bool_arr_ext'] = alias_ext_init_bool_array
numba.core.ir_utils.alias_func_extensions['get_bool_arr_data',
    'bodo.libs.bool_arr_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_bool_arr_bitmap',
    'bodo.libs.bool_arr_ext'] = alias_ext_dummy_func


@numba.njit(no_cpython_wrapper=True)
def alloc_bool_array(n):
    ajtm__qxpo = np.empty(n, dtype=np.bool_)
    oppd__qgys = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(ajtm__qxpo, oppd__qgys)


def alloc_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_alloc_bool_array = (
    alloc_bool_array_equiv)


@overload(operator.getitem, no_unliteral=True)
def bool_arr_getitem(A, ind):
    if A != boolean_array:
        return
    if isinstance(types.unliteral(ind), types.Integer):
        return lambda A, ind: A._data[ind]
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            plbyx__ejn, zwa__qzy = array_getitem_bool_index(A, ind)
            return init_bool_array(plbyx__ejn, zwa__qzy)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            plbyx__ejn, zwa__qzy = array_getitem_int_index(A, ind)
            return init_bool_array(plbyx__ejn, zwa__qzy)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            plbyx__ejn, zwa__qzy = array_getitem_slice_index(A, ind)
            return init_bool_array(plbyx__ejn, zwa__qzy)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    ztcf__isqj = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(ztcf__isqj)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(ztcf__isqj)
    if is_list_like_index_type(idx) and isinstance(idx.dtype, types.Integer):

        def impl_arr_ind_mask(A, idx, val):
            array_setitem_int_index(A, idx, val)
        return impl_arr_ind_mask
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:

        def impl_bool_ind_mask(A, idx, val):
            array_setitem_bool_index(A, idx, val)
        return impl_bool_ind_mask
    if isinstance(idx, types.SliceType):

        def impl_slice_mask(A, idx, val):
            array_setitem_slice_index(A, idx, val)
        return impl_slice_mask
    raise BodoError(
        f'setitem for BooleanArray with indexing type {idx} not supported.')


@overload(len, no_unliteral=True)
def overload_bool_arr_len(A):
    if A == boolean_array:
        return lambda A: len(A._data)


@overload_attribute(BooleanArrayType, 'shape')
def overload_bool_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(BooleanArrayType, 'dtype')
def overload_bool_arr_dtype(A):
    return lambda A: pd.BooleanDtype()


@overload_attribute(BooleanArrayType, 'ndim')
def overload_bool_arr_ndim(A):
    return lambda A: 1


@overload_attribute(BooleanArrayType, 'nbytes')
def bool_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


@overload_method(BooleanArrayType, 'copy', no_unliteral=True)
def overload_bool_arr_copy(A):
    return lambda A: bodo.libs.bool_arr_ext.init_bool_array(bodo.libs.
        bool_arr_ext.get_bool_arr_data(A).copy(), bodo.libs.bool_arr_ext.
        get_bool_arr_bitmap(A).copy())


@overload_method(BooleanArrayType, 'sum', no_unliteral=True, inline='always')
def overload_bool_sum(A):

    def impl(A):
        numba.parfors.parfor.init_prange()
        s = 0
        for btdiw__hdph in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, btdiw__hdph):
                val = A[btdiw__hdph]
            s += val
        return s
    return impl


@overload_method(BooleanArrayType, 'astype', no_unliteral=True)
def overload_bool_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "BooleanArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if dtype == types.bool_:
        if is_overload_false(copy):
            return lambda A, dtype, copy=True: A
        elif is_overload_true(copy):
            return lambda A, dtype, copy=True: A.copy()
        else:

            def impl(A, dtype, copy=True):
                if copy:
                    return A.copy()
                else:
                    return A
            return impl
    nb_dtype = parse_dtype(dtype, 'BooleanArray.astype')
    if isinstance(nb_dtype, types.Float):

        def impl_float(A, dtype, copy=True):
            data = bodo.libs.bool_arr_ext.get_bool_arr_data(A)
            n = len(data)
            gzqsq__pvipd = np.empty(n, nb_dtype)
            for btdiw__hdph in numba.parfors.parfor.internal_prange(n):
                gzqsq__pvipd[btdiw__hdph] = data[btdiw__hdph]
                if bodo.libs.array_kernels.isna(A, btdiw__hdph):
                    gzqsq__pvipd[btdiw__hdph] = np.nan
            return gzqsq__pvipd
        return impl_float
    return (lambda A, dtype, copy=True: bodo.libs.bool_arr_ext.
        get_bool_arr_data(A).astype(nb_dtype))


@overload(str, no_unliteral=True)
def overload_str_bool(val):
    if val == types.bool_:

        def impl(val):
            if val:
                return 'True'
            return 'False'
        return impl


ufunc_aliases = {'equal': 'eq', 'not_equal': 'ne', 'less': 'lt',
    'less_equal': 'le', 'greater': 'gt', 'greater_equal': 'ge'}


def create_op_overload(op, n_inputs):
    mpx__gvmkn = op.__name__
    mpx__gvmkn = ufunc_aliases.get(mpx__gvmkn, mpx__gvmkn)
    if n_inputs == 1:

        def overload_bool_arr_op_nin_1(A):
            if isinstance(A, BooleanArrayType):
                return bodo.libs.int_arr_ext.get_nullable_array_unary_impl(op,
                    A)
        return overload_bool_arr_op_nin_1
    elif n_inputs == 2:

        def overload_bool_arr_op_nin_2(lhs, rhs):
            if lhs == boolean_array or rhs == boolean_array:
                return bodo.libs.int_arr_ext.get_nullable_array_binary_impl(op,
                    lhs, rhs)
        return overload_bool_arr_op_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for xxben__ignh in numba.np.ufunc_db.get_ufuncs():
        vizsz__mtf = create_op_overload(xxben__ignh, xxben__ignh.nin)
        overload(xxben__ignh, no_unliteral=True)(vizsz__mtf)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        vizsz__mtf = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(vizsz__mtf)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        vizsz__mtf = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(vizsz__mtf)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        vizsz__mtf = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(vizsz__mtf)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        ccz__czc = []
        gpk__evb = False
        aksc__oxqc = False
        mfdk__lyd = False
        for btdiw__hdph in range(len(A)):
            if bodo.libs.array_kernels.isna(A, btdiw__hdph):
                if not gpk__evb:
                    data.append(False)
                    ccz__czc.append(False)
                    gpk__evb = True
                continue
            val = A[btdiw__hdph]
            if val and not aksc__oxqc:
                data.append(True)
                ccz__czc.append(True)
                aksc__oxqc = True
            if not val and not mfdk__lyd:
                data.append(False)
                ccz__czc.append(True)
                mfdk__lyd = True
            if gpk__evb and aksc__oxqc and mfdk__lyd:
                break
        plbyx__ejn = np.array(data)
        n = len(plbyx__ejn)
        wne__iqppi = 1
        zwa__qzy = np.empty(wne__iqppi, np.uint8)
        for wae__bjuri in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(zwa__qzy, wae__bjuri,
                ccz__czc[wae__bjuri])
        return init_bool_array(plbyx__ejn, zwa__qzy)
    return impl_bool_arr


@overload(operator.getitem, no_unliteral=True)
def bool_arr_ind_getitem(A, ind):
    if ind == boolean_array and (isinstance(A, (types.Array, bodo.libs.
        int_arr_ext.IntegerArrayType)) or isinstance(A, bodo.libs.
        struct_arr_ext.StructArrayType) or isinstance(A, bodo.libs.
        array_item_arr_ext.ArrayItemArrayType) or isinstance(A, bodo.libs.
        map_arr_ext.MapArrayType) or A in (string_array_type, bodo.hiframes
        .split_impl.string_array_split_view_type, boolean_array)):
        return lambda A, ind: A[ind._data]


@lower_cast(types.Array(types.bool_, 1, 'C'), boolean_array)
def cast_np_bool_arr_to_bool_arr(context, builder, fromty, toty, val):
    func = lambda A: bodo.libs.bool_arr_ext.init_bool_array(A, np.full(len(
        A) + 7 >> 3, 255, np.uint8))
    wag__lwuo = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, wag__lwuo)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    iiwpv__txwn = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        dtldo__cnw = bodo.utils.utils.is_array_typ(val1, False)
        qfgii__qvf = bodo.utils.utils.is_array_typ(val2, False)
        jqyd__ddxyr = 'val1' if dtldo__cnw else 'val2'
        nsq__viyls = 'def impl(val1, val2):\n'
        nsq__viyls += f'  n = len({jqyd__ddxyr})\n'
        nsq__viyls += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        nsq__viyls += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if dtldo__cnw:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            ndydy__rjkh = 'val1[i]'
        else:
            null1 = 'False\n'
            ndydy__rjkh = 'val1'
        if qfgii__qvf:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            fve__qme = 'val2[i]'
        else:
            null2 = 'False\n'
            fve__qme = 'val2'
        if iiwpv__txwn:
            nsq__viyls += f"""    result, isna_val = compute_or_body({null1}, {null2}, {ndydy__rjkh}, {fve__qme})
"""
        else:
            nsq__viyls += f"""    result, isna_val = compute_and_body({null1}, {null2}, {ndydy__rjkh}, {fve__qme})
"""
        nsq__viyls += '    out_arr[i] = result\n'
        nsq__viyls += '    if isna_val:\n'
        nsq__viyls += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        nsq__viyls += '      continue\n'
        nsq__viyls += '  return out_arr\n'
        aapuz__aehf = {}
        exec(nsq__viyls, {'bodo': bodo, 'numba': numba, 'compute_and_body':
            compute_and_body, 'compute_or_body': compute_or_body}, aapuz__aehf)
        impl = aapuz__aehf['impl']
        return impl
    return bool_array_impl


def compute_or_body(null1, null2, val1, val2):
    pass


@overload(compute_or_body)
def overload_compute_or_body(null1, null2, val1, val2):

    def impl(null1, null2, val1, val2):
        if null1 and null2:
            return False, True
        elif null1:
            return val2, val2 == False
        elif null2:
            return val1, val1 == False
        else:
            return val1 | val2, False
    return impl


def compute_and_body(null1, null2, val1, val2):
    pass


@overload(compute_and_body)
def overload_compute_and_body(null1, null2, val1, val2):

    def impl(null1, null2, val1, val2):
        if null1 and null2:
            return False, True
        elif null1:
            return val2, val2 == True
        elif null2:
            return val1, val1 == True
        else:
            return val1 & val2, False
    return impl


def create_boolean_array_logical_lower_impl(op):

    def logical_lower_impl(context, builder, sig, args):
        impl = create_nullable_logical_op_overload(op)(*sig.args)
        return context.compile_internal(builder, impl, sig, args)
    return logical_lower_impl


class BooleanArrayLogicalOperatorTemplate(AbstractTemplate):

    def generic(self, args, kws):
        assert len(args) == 2
        assert not kws
        if not is_valid_boolean_array_logical_op(args[0], args[1]):
            return
        giq__cog = boolean_array
        return giq__cog(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    tva__vaj = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array) and (
        bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype == types.
        bool_ or typ1 == types.bool_) and (bodo.utils.utils.is_array_typ(
        typ2, False) and typ2.dtype == types.bool_ or typ2 == types.bool_)
    return tva__vaj


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        pofg__rpe = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(pofg__rpe)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(pofg__rpe)


_install_nullable_logical_lowering()
