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
        ylmo__lfcs = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, ylmo__lfcs)


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
    nbt__syg = c.context.insert_const_string(c.builder.module, 'pandas')
    wqa__ilp = c.pyapi.import_module_noblock(nbt__syg)
    qzztb__yaz = c.pyapi.call_method(wqa__ilp, 'BooleanDtype', ())
    c.pyapi.decref(wqa__ilp)
    return qzztb__yaz


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    ycuos__qkwt = n + 7 >> 3
    return np.full(ycuos__qkwt, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    ufmru__rgble = c.context.typing_context.resolve_value_type(func)
    xrq__rhk = ufmru__rgble.get_call_type(c.context.typing_context,
        arg_typs, {})
    zbkhg__kwsc = c.context.get_function(ufmru__rgble, xrq__rhk)
    put__ithx = c.context.call_conv.get_function_type(xrq__rhk.return_type,
        xrq__rhk.args)
    uvnq__mnk = c.builder.module
    qpbb__yrtdt = lir.Function(uvnq__mnk, put__ithx, name=uvnq__mnk.
        get_unique_name('.func_conv'))
    qpbb__yrtdt.linkage = 'internal'
    pokj__hfkv = lir.IRBuilder(qpbb__yrtdt.append_basic_block())
    lhw__jewb = c.context.call_conv.decode_arguments(pokj__hfkv, xrq__rhk.
        args, qpbb__yrtdt)
    usd__blsy = zbkhg__kwsc(pokj__hfkv, lhw__jewb)
    c.context.call_conv.return_value(pokj__hfkv, usd__blsy)
    pwcl__anpp, useg__qwjg = c.context.call_conv.call_function(c.builder,
        qpbb__yrtdt, xrq__rhk.return_type, xrq__rhk.args, args)
    return useg__qwjg


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    eglz__pwza = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(eglz__pwza)
    c.pyapi.decref(eglz__pwza)
    put__ithx = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    gewzs__otwbf = cgutils.get_or_insert_function(c.builder.module,
        put__ithx, name='is_bool_array')
    put__ithx = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    qpbb__yrtdt = cgutils.get_or_insert_function(c.builder.module,
        put__ithx, name='is_pd_boolean_array')
    yfdt__hlojv = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    dsd__qvmx = c.builder.call(qpbb__yrtdt, [obj])
    fxmzw__wkms = c.builder.icmp_unsigned('!=', dsd__qvmx, dsd__qvmx.type(0))
    with c.builder.if_else(fxmzw__wkms) as (pd_then, pd_otherwise):
        with pd_then:
            ufk__parmg = c.pyapi.object_getattr_string(obj, '_data')
            yfdt__hlojv.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), ufk__parmg).value
            qvm__hozze = c.pyapi.object_getattr_string(obj, '_mask')
            cmxm__izqni = c.pyapi.to_native_value(types.Array(types.bool_, 
                1, 'C'), qvm__hozze).value
            ycuos__qkwt = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            kyzx__zfkzl = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, cmxm__izqni)
            rhccd__onjv = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [ycuos__qkwt])
            put__ithx = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            qpbb__yrtdt = cgutils.get_or_insert_function(c.builder.module,
                put__ithx, name='mask_arr_to_bitmap')
            c.builder.call(qpbb__yrtdt, [rhccd__onjv.data, kyzx__zfkzl.data, n]
                )
            yfdt__hlojv.null_bitmap = rhccd__onjv._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), cmxm__izqni)
            c.pyapi.decref(ufk__parmg)
            c.pyapi.decref(qvm__hozze)
        with pd_otherwise:
            fgocf__quyc = c.builder.call(gewzs__otwbf, [obj])
            wfv__wli = c.builder.icmp_unsigned('!=', fgocf__quyc,
                fgocf__quyc.type(0))
            with c.builder.if_else(wfv__wli) as (then, otherwise):
                with then:
                    yfdt__hlojv.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    yfdt__hlojv.null_bitmap = call_func_in_unbox(
                        gen_full_bitmap, (n,), (types.int64,), c)
                with otherwise:
                    yfdt__hlojv.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    ycuos__qkwt = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    yfdt__hlojv.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [ycuos__qkwt])._getvalue()
                    aey__bdi = c.context.make_array(types.Array(types.bool_,
                        1, 'C'))(c.context, c.builder, yfdt__hlojv.data).data
                    zmw__lpm = c.context.make_array(types.Array(types.uint8,
                        1, 'C'))(c.context, c.builder, yfdt__hlojv.null_bitmap
                        ).data
                    put__ithx = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    qpbb__yrtdt = cgutils.get_or_insert_function(c.builder.
                        module, put__ithx, name='unbox_bool_array_obj')
                    c.builder.call(qpbb__yrtdt, [obj, aey__bdi, zmw__lpm, n])
    return NativeValue(yfdt__hlojv._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    yfdt__hlojv = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        yfdt__hlojv.data, c.env_manager)
    gces__nzya = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, yfdt__hlojv.null_bitmap).data
    eglz__pwza = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(eglz__pwza)
    nbt__syg = c.context.insert_const_string(c.builder.module, 'numpy')
    kawz__bdek = c.pyapi.import_module_noblock(nbt__syg)
    papr__clk = c.pyapi.object_getattr_string(kawz__bdek, 'bool_')
    cmxm__izqni = c.pyapi.call_method(kawz__bdek, 'empty', (eglz__pwza,
        papr__clk))
    mqbt__ozenm = c.pyapi.object_getattr_string(cmxm__izqni, 'ctypes')
    agwqn__mjvge = c.pyapi.object_getattr_string(mqbt__ozenm, 'data')
    jmf__tsiid = c.builder.inttoptr(c.pyapi.long_as_longlong(agwqn__mjvge),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as loop:
        wjeyz__nkdro = loop.index
        vboy__gqe = c.builder.lshr(wjeyz__nkdro, lir.Constant(lir.IntType(
            64), 3))
        vsrpl__depwf = c.builder.load(cgutils.gep(c.builder, gces__nzya,
            vboy__gqe))
        lbtbs__upmh = c.builder.trunc(c.builder.and_(wjeyz__nkdro, lir.
            Constant(lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(vsrpl__depwf, lbtbs__upmh), lir
            .Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        nynl__mxmgs = cgutils.gep(c.builder, jmf__tsiid, wjeyz__nkdro)
        c.builder.store(val, nynl__mxmgs)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        yfdt__hlojv.null_bitmap)
    nbt__syg = c.context.insert_const_string(c.builder.module, 'pandas')
    wqa__ilp = c.pyapi.import_module_noblock(nbt__syg)
    jfdso__nsh = c.pyapi.object_getattr_string(wqa__ilp, 'arrays')
    qzztb__yaz = c.pyapi.call_method(jfdso__nsh, 'BooleanArray', (data,
        cmxm__izqni))
    c.pyapi.decref(wqa__ilp)
    c.pyapi.decref(eglz__pwza)
    c.pyapi.decref(kawz__bdek)
    c.pyapi.decref(papr__clk)
    c.pyapi.decref(mqbt__ozenm)
    c.pyapi.decref(agwqn__mjvge)
    c.pyapi.decref(jfdso__nsh)
    c.pyapi.decref(data)
    c.pyapi.decref(cmxm__izqni)
    return qzztb__yaz


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    qfh__tza = np.empty(n, np.bool_)
    yvy__mad = np.empty(n + 7 >> 3, np.uint8)
    for wjeyz__nkdro, s in enumerate(pyval):
        kbiq__taslg = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(yvy__mad, wjeyz__nkdro, int(
            not kbiq__taslg))
        if not kbiq__taslg:
            qfh__tza[wjeyz__nkdro] = s
    xun__gtw = context.get_constant_generic(builder, data_type, qfh__tza)
    gtn__mumuh = context.get_constant_generic(builder, nulls_type, yvy__mad)
    return lir.Constant.literal_struct([xun__gtw, gtn__mumuh])


def lower_init_bool_array(context, builder, signature, args):
    gtl__szjra, dkkdn__zebqi = args
    yfdt__hlojv = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    yfdt__hlojv.data = gtl__szjra
    yfdt__hlojv.null_bitmap = dkkdn__zebqi
    context.nrt.incref(builder, signature.args[0], gtl__szjra)
    context.nrt.incref(builder, signature.args[1], dkkdn__zebqi)
    return yfdt__hlojv._getvalue()


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
    ssv__vyrc = args[0]
    if equiv_set.has_shape(ssv__vyrc):
        return ArrayAnalysis.AnalyzeResult(shape=ssv__vyrc, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    ssv__vyrc = args[0]
    if equiv_set.has_shape(ssv__vyrc):
        return ArrayAnalysis.AnalyzeResult(shape=ssv__vyrc, pre=[])
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
    qfh__tza = np.empty(n, dtype=np.bool_)
    hdjf__ezyez = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(qfh__tza, hdjf__ezyez)


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
            mdx__ltp, gehpb__xmkg = array_getitem_bool_index(A, ind)
            return init_bool_array(mdx__ltp, gehpb__xmkg)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            mdx__ltp, gehpb__xmkg = array_getitem_int_index(A, ind)
            return init_bool_array(mdx__ltp, gehpb__xmkg)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            mdx__ltp, gehpb__xmkg = array_getitem_slice_index(A, ind)
            return init_bool_array(mdx__ltp, gehpb__xmkg)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    bsqpy__edov = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(bsqpy__edov)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(bsqpy__edov)
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
        for wjeyz__nkdro in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, wjeyz__nkdro):
                val = A[wjeyz__nkdro]
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
            rlzs__jzstt = np.empty(n, nb_dtype)
            for wjeyz__nkdro in numba.parfors.parfor.internal_prange(n):
                rlzs__jzstt[wjeyz__nkdro] = data[wjeyz__nkdro]
                if bodo.libs.array_kernels.isna(A, wjeyz__nkdro):
                    rlzs__jzstt[wjeyz__nkdro] = np.nan
            return rlzs__jzstt
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
    mevoj__jahff = op.__name__
    mevoj__jahff = ufunc_aliases.get(mevoj__jahff, mevoj__jahff)
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
    for fbel__dxx in numba.np.ufunc_db.get_ufuncs():
        ywlw__ufwft = create_op_overload(fbel__dxx, fbel__dxx.nin)
        overload(fbel__dxx, no_unliteral=True)(ywlw__ufwft)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        ywlw__ufwft = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(ywlw__ufwft)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        ywlw__ufwft = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(ywlw__ufwft)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        ywlw__ufwft = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(ywlw__ufwft)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        lbtbs__upmh = []
        pyzc__mrl = False
        dpma__bzgv = False
        heyck__tmyh = False
        for wjeyz__nkdro in range(len(A)):
            if bodo.libs.array_kernels.isna(A, wjeyz__nkdro):
                if not pyzc__mrl:
                    data.append(False)
                    lbtbs__upmh.append(False)
                    pyzc__mrl = True
                continue
            val = A[wjeyz__nkdro]
            if val and not dpma__bzgv:
                data.append(True)
                lbtbs__upmh.append(True)
                dpma__bzgv = True
            if not val and not heyck__tmyh:
                data.append(False)
                lbtbs__upmh.append(True)
                heyck__tmyh = True
            if pyzc__mrl and dpma__bzgv and heyck__tmyh:
                break
        mdx__ltp = np.array(data)
        n = len(mdx__ltp)
        ycuos__qkwt = 1
        gehpb__xmkg = np.empty(ycuos__qkwt, np.uint8)
        for sdc__fijd in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(gehpb__xmkg, sdc__fijd,
                lbtbs__upmh[sdc__fijd])
        return init_bool_array(mdx__ltp, gehpb__xmkg)
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
    qzztb__yaz = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, qzztb__yaz)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    wmm__mxikv = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        lkj__auxv = bodo.utils.utils.is_array_typ(val1, False)
        rdmv__wsugp = bodo.utils.utils.is_array_typ(val2, False)
        bpch__wifxh = 'val1' if lkj__auxv else 'val2'
        hhu__ugb = 'def impl(val1, val2):\n'
        hhu__ugb += f'  n = len({bpch__wifxh})\n'
        hhu__ugb += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        hhu__ugb += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if lkj__auxv:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            aklk__gfptn = 'val1[i]'
        else:
            null1 = 'False\n'
            aklk__gfptn = 'val1'
        if rdmv__wsugp:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            cwmt__bsv = 'val2[i]'
        else:
            null2 = 'False\n'
            cwmt__bsv = 'val2'
        if wmm__mxikv:
            hhu__ugb += f"""    result, isna_val = compute_or_body({null1}, {null2}, {aklk__gfptn}, {cwmt__bsv})
"""
        else:
            hhu__ugb += f"""    result, isna_val = compute_and_body({null1}, {null2}, {aklk__gfptn}, {cwmt__bsv})
"""
        hhu__ugb += '    out_arr[i] = result\n'
        hhu__ugb += '    if isna_val:\n'
        hhu__ugb += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        hhu__ugb += '      continue\n'
        hhu__ugb += '  return out_arr\n'
        ugvi__yseu = {}
        exec(hhu__ugb, {'bodo': bodo, 'numba': numba, 'compute_and_body':
            compute_and_body, 'compute_or_body': compute_or_body}, ugvi__yseu)
        impl = ugvi__yseu['impl']
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
        xlna__clb = boolean_array
        return xlna__clb(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    wsggl__tatd = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array
        ) and (bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype ==
        types.bool_ or typ1 == types.bool_) and (bodo.utils.utils.
        is_array_typ(typ2, False) and typ2.dtype == types.bool_ or typ2 ==
        types.bool_)
    return wsggl__tatd


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        bvmjh__xrp = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(bvmjh__xrp)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(bvmjh__xrp)


_install_nullable_logical_lowering()
