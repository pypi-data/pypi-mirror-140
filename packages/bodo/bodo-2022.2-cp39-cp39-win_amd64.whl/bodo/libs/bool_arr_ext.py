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
        tsk__hua = [('data', data_type), ('null_bitmap', nulls_type)]
        models.StructModel.__init__(self, dmm, fe_type, tsk__hua)


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
    sxgad__pnxw = c.context.insert_const_string(c.builder.module, 'pandas')
    eexk__fiaje = c.pyapi.import_module_noblock(sxgad__pnxw)
    bvsi__drget = c.pyapi.call_method(eexk__fiaje, 'BooleanDtype', ())
    c.pyapi.decref(eexk__fiaje)
    return bvsi__drget


@unbox(BooleanDtype)
def unbox_boolean_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.BooleanDtype)(lambda a, b: boolean_dtype)
type_callable(pd.BooleanDtype)(lambda c: lambda : boolean_dtype)
lower_builtin(pd.BooleanDtype)(lambda c, b, s, a: c.get_dummy_value())


@numba.njit
def gen_full_bitmap(n):
    eaxn__zjef = n + 7 >> 3
    return np.full(eaxn__zjef, 255, np.uint8)


def call_func_in_unbox(func, args, arg_typs, c):
    cnr__qwr = c.context.typing_context.resolve_value_type(func)
    nurko__mss = cnr__qwr.get_call_type(c.context.typing_context, arg_typs, {})
    mdl__kpwbc = c.context.get_function(cnr__qwr, nurko__mss)
    cmt__fcgw = c.context.call_conv.get_function_type(nurko__mss.
        return_type, nurko__mss.args)
    kzs__livtd = c.builder.module
    ubtvj__jdnkk = lir.Function(kzs__livtd, cmt__fcgw, name=kzs__livtd.
        get_unique_name('.func_conv'))
    ubtvj__jdnkk.linkage = 'internal'
    lobzp__kddhe = lir.IRBuilder(ubtvj__jdnkk.append_basic_block())
    xsxjg__abe = c.context.call_conv.decode_arguments(lobzp__kddhe,
        nurko__mss.args, ubtvj__jdnkk)
    nezuw__nxsx = mdl__kpwbc(lobzp__kddhe, xsxjg__abe)
    c.context.call_conv.return_value(lobzp__kddhe, nezuw__nxsx)
    qlrsf__kqhz, fplxr__zgt = c.context.call_conv.call_function(c.builder,
        ubtvj__jdnkk, nurko__mss.return_type, nurko__mss.args, args)
    return fplxr__zgt


@unbox(BooleanArrayType)
def unbox_bool_array(typ, obj, c):
    qga__xasxr = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(qga__xasxr)
    c.pyapi.decref(qga__xasxr)
    cmt__fcgw = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    fbqx__pkxju = cgutils.get_or_insert_function(c.builder.module,
        cmt__fcgw, name='is_bool_array')
    cmt__fcgw = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    ubtvj__jdnkk = cgutils.get_or_insert_function(c.builder.module,
        cmt__fcgw, name='is_pd_boolean_array')
    qrzxv__ggr = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    qfuf__kefnw = c.builder.call(ubtvj__jdnkk, [obj])
    hblr__temo = c.builder.icmp_unsigned('!=', qfuf__kefnw, qfuf__kefnw.type(0)
        )
    with c.builder.if_else(hblr__temo) as (pd_then, pd_otherwise):
        with pd_then:
            augge__psz = c.pyapi.object_getattr_string(obj, '_data')
            qrzxv__ggr.data = c.pyapi.to_native_value(types.Array(types.
                bool_, 1, 'C'), augge__psz).value
            kzzl__fbcd = c.pyapi.object_getattr_string(obj, '_mask')
            axyq__sznjy = c.pyapi.to_native_value(types.Array(types.bool_, 
                1, 'C'), kzzl__fbcd).value
            eaxn__zjef = c.builder.udiv(c.builder.add(n, lir.Constant(lir.
                IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
            qwx__btdwa = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, axyq__sznjy)
            anppf__vxttz = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(types.uint8, 1, 'C'), [eaxn__zjef])
            cmt__fcgw = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            ubtvj__jdnkk = cgutils.get_or_insert_function(c.builder.module,
                cmt__fcgw, name='mask_arr_to_bitmap')
            c.builder.call(ubtvj__jdnkk, [anppf__vxttz.data, qwx__btdwa.
                data, n])
            qrzxv__ggr.null_bitmap = anppf__vxttz._getvalue()
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), axyq__sznjy)
            c.pyapi.decref(augge__psz)
            c.pyapi.decref(kzzl__fbcd)
        with pd_otherwise:
            zot__ndjo = c.builder.call(fbqx__pkxju, [obj])
            jlpav__xfzr = c.builder.icmp_unsigned('!=', zot__ndjo,
                zot__ndjo.type(0))
            with c.builder.if_else(jlpav__xfzr) as (then, otherwise):
                with then:
                    qrzxv__ggr.data = c.pyapi.to_native_value(types.Array(
                        types.bool_, 1, 'C'), obj).value
                    qrzxv__ggr.null_bitmap = call_func_in_unbox(gen_full_bitmap
                        , (n,), (types.int64,), c)
                with otherwise:
                    qrzxv__ggr.data = bodo.utils.utils._empty_nd_impl(c.
                        context, c.builder, types.Array(types.bool_, 1, 'C'
                        ), [n])._getvalue()
                    eaxn__zjef = c.builder.udiv(c.builder.add(n, lir.
                        Constant(lir.IntType(64), 7)), lir.Constant(lir.
                        IntType(64), 8))
                    qrzxv__ggr.null_bitmap = bodo.utils.utils._empty_nd_impl(c
                        .context, c.builder, types.Array(types.uint8, 1,
                        'C'), [eaxn__zjef])._getvalue()
                    ulrw__tynd = c.context.make_array(types.Array(types.
                        bool_, 1, 'C'))(c.context, c.builder, qrzxv__ggr.data
                        ).data
                    lht__mxrwk = c.context.make_array(types.Array(types.
                        uint8, 1, 'C'))(c.context, c.builder, qrzxv__ggr.
                        null_bitmap).data
                    cmt__fcgw = lir.FunctionType(lir.VoidType(), [lir.
                        IntType(8).as_pointer(), lir.IntType(8).as_pointer(
                        ), lir.IntType(8).as_pointer(), lir.IntType(64)])
                    ubtvj__jdnkk = cgutils.get_or_insert_function(c.builder
                        .module, cmt__fcgw, name='unbox_bool_array_obj')
                    c.builder.call(ubtvj__jdnkk, [obj, ulrw__tynd,
                        lht__mxrwk, n])
    return NativeValue(qrzxv__ggr._getvalue())


@box(BooleanArrayType)
def box_bool_arr(typ, val, c):
    qrzxv__ggr = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        qrzxv__ggr.data, c.env_manager)
    gmplv__miuz = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, qrzxv__ggr.null_bitmap).data
    qga__xasxr = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(qga__xasxr)
    sxgad__pnxw = c.context.insert_const_string(c.builder.module, 'numpy')
    mmmj__nhw = c.pyapi.import_module_noblock(sxgad__pnxw)
    lvsl__liw = c.pyapi.object_getattr_string(mmmj__nhw, 'bool_')
    axyq__sznjy = c.pyapi.call_method(mmmj__nhw, 'empty', (qga__xasxr,
        lvsl__liw))
    rvgo__ygr = c.pyapi.object_getattr_string(axyq__sznjy, 'ctypes')
    srm__kpmt = c.pyapi.object_getattr_string(rvgo__ygr, 'data')
    wku__fvomh = c.builder.inttoptr(c.pyapi.long_as_longlong(srm__kpmt),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as loop:
        toie__cahq = loop.index
        nat__detyt = c.builder.lshr(toie__cahq, lir.Constant(lir.IntType(64
            ), 3))
        cfbof__dmyz = c.builder.load(cgutils.gep(c.builder, gmplv__miuz,
            nat__detyt))
        jlwxy__kef = c.builder.trunc(c.builder.and_(toie__cahq, lir.
            Constant(lir.IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(cfbof__dmyz, jlwxy__kef), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        ijv__ixk = cgutils.gep(c.builder, wku__fvomh, toie__cahq)
        c.builder.store(val, ijv__ixk)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        qrzxv__ggr.null_bitmap)
    sxgad__pnxw = c.context.insert_const_string(c.builder.module, 'pandas')
    eexk__fiaje = c.pyapi.import_module_noblock(sxgad__pnxw)
    pitpf__mqeev = c.pyapi.object_getattr_string(eexk__fiaje, 'arrays')
    bvsi__drget = c.pyapi.call_method(pitpf__mqeev, 'BooleanArray', (data,
        axyq__sznjy))
    c.pyapi.decref(eexk__fiaje)
    c.pyapi.decref(qga__xasxr)
    c.pyapi.decref(mmmj__nhw)
    c.pyapi.decref(lvsl__liw)
    c.pyapi.decref(rvgo__ygr)
    c.pyapi.decref(srm__kpmt)
    c.pyapi.decref(pitpf__mqeev)
    c.pyapi.decref(data)
    c.pyapi.decref(axyq__sznjy)
    return bvsi__drget


@lower_constant(BooleanArrayType)
def lower_constant_bool_arr(context, builder, typ, pyval):
    n = len(pyval)
    acmlo__qibsy = np.empty(n, np.bool_)
    wxrb__wgsms = np.empty(n + 7 >> 3, np.uint8)
    for toie__cahq, s in enumerate(pyval):
        qnwvv__cdt = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(wxrb__wgsms, toie__cahq, int(
            not qnwvv__cdt))
        if not qnwvv__cdt:
            acmlo__qibsy[toie__cahq] = s
    rwxar__hvakb = context.get_constant_generic(builder, data_type,
        acmlo__qibsy)
    xxpjg__zbigx = context.get_constant_generic(builder, nulls_type,
        wxrb__wgsms)
    return lir.Constant.literal_struct([rwxar__hvakb, xxpjg__zbigx])


def lower_init_bool_array(context, builder, signature, args):
    mxx__lgz, whb__ibgh = args
    qrzxv__ggr = cgutils.create_struct_proxy(signature.return_type)(context,
        builder)
    qrzxv__ggr.data = mxx__lgz
    qrzxv__ggr.null_bitmap = whb__ibgh
    context.nrt.incref(builder, signature.args[0], mxx__lgz)
    context.nrt.incref(builder, signature.args[1], whb__ibgh)
    return qrzxv__ggr._getvalue()


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
    qktvo__inau = args[0]
    if equiv_set.has_shape(qktvo__inau):
        return ArrayAnalysis.AnalyzeResult(shape=qktvo__inau, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_bool_arr_ext_get_bool_arr_data = (
    get_bool_arr_data_equiv)


def init_bool_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    qktvo__inau = args[0]
    if equiv_set.has_shape(qktvo__inau):
        return ArrayAnalysis.AnalyzeResult(shape=qktvo__inau, pre=[])
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
    acmlo__qibsy = np.empty(n, dtype=np.bool_)
    gftaw__vvd = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_bool_array(acmlo__qibsy, gftaw__vvd)


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
            swl__aky, ehm__kxqk = array_getitem_bool_index(A, ind)
            return init_bool_array(swl__aky, ehm__kxqk)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            swl__aky, ehm__kxqk = array_getitem_int_index(A, ind)
            return init_bool_array(swl__aky, ehm__kxqk)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            swl__aky, ehm__kxqk = array_getitem_slice_index(A, ind)
            return init_bool_array(swl__aky, ehm__kxqk)
        return impl_slice
    raise BodoError(
        f'getitem for BooleanArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def bool_arr_setitem(A, idx, val):
    if A != boolean_array:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    ror__xbu = (
        f"setitem for BooleanArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    if isinstance(idx, types.Integer):
        if types.unliteral(val) == types.bool_:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(ror__xbu)
    if not (is_iterable_type(val) and val.dtype == types.bool_ or types.
        unliteral(val) == types.bool_):
        raise BodoError(ror__xbu)
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
        for toie__cahq in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, toie__cahq):
                val = A[toie__cahq]
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
            ltzsj__qtjbl = np.empty(n, nb_dtype)
            for toie__cahq in numba.parfors.parfor.internal_prange(n):
                ltzsj__qtjbl[toie__cahq] = data[toie__cahq]
                if bodo.libs.array_kernels.isna(A, toie__cahq):
                    ltzsj__qtjbl[toie__cahq] = np.nan
            return ltzsj__qtjbl
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
    vasg__ahgt = op.__name__
    vasg__ahgt = ufunc_aliases.get(vasg__ahgt, vasg__ahgt)
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
    for tob__etwi in numba.np.ufunc_db.get_ufuncs():
        ggckt__awca = create_op_overload(tob__etwi, tob__etwi.nin)
        overload(tob__etwi, no_unliteral=True)(ggckt__awca)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod, operator.or_, operator.and_]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        ggckt__awca = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(ggckt__awca)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        ggckt__awca = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(ggckt__awca)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        ggckt__awca = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(ggckt__awca)


_install_unary_ops()


@overload_method(BooleanArrayType, 'unique', no_unliteral=True)
def overload_unique(A):

    def impl_bool_arr(A):
        data = []
        jlwxy__kef = []
        kfzul__hsr = False
        lup__ibit = False
        xiyq__gmv = False
        for toie__cahq in range(len(A)):
            if bodo.libs.array_kernels.isna(A, toie__cahq):
                if not kfzul__hsr:
                    data.append(False)
                    jlwxy__kef.append(False)
                    kfzul__hsr = True
                continue
            val = A[toie__cahq]
            if val and not lup__ibit:
                data.append(True)
                jlwxy__kef.append(True)
                lup__ibit = True
            if not val and not xiyq__gmv:
                data.append(False)
                jlwxy__kef.append(True)
                xiyq__gmv = True
            if kfzul__hsr and lup__ibit and xiyq__gmv:
                break
        swl__aky = np.array(data)
        n = len(swl__aky)
        eaxn__zjef = 1
        ehm__kxqk = np.empty(eaxn__zjef, np.uint8)
        for sgwac__wlgw in range(n):
            bodo.libs.int_arr_ext.set_bit_to_arr(ehm__kxqk, sgwac__wlgw,
                jlwxy__kef[sgwac__wlgw])
        return init_bool_array(swl__aky, ehm__kxqk)
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
    bvsi__drget = context.compile_internal(builder, func, toty(fromty), [val])
    return impl_ret_borrowed(context, builder, toty, bvsi__drget)


@overload(operator.setitem, no_unliteral=True)
def overload_np_array_setitem_bool_arr(A, idx, val):
    if isinstance(A, types.Array) and idx == boolean_array:

        def impl(A, idx, val):
            A[idx._data] = val
        return impl


def create_nullable_logical_op_overload(op):
    mzv__ikk = op == operator.or_

    def bool_array_impl(val1, val2):
        if not is_valid_boolean_array_logical_op(val1, val2):
            return
        tnj__grsmr = bodo.utils.utils.is_array_typ(val1, False)
        xwhv__ejfyu = bodo.utils.utils.is_array_typ(val2, False)
        vghab__epkp = 'val1' if tnj__grsmr else 'val2'
        eoy__cvxza = 'def impl(val1, val2):\n'
        eoy__cvxza += f'  n = len({vghab__epkp})\n'
        eoy__cvxza += (
            '  out_arr = bodo.utils.utils.alloc_type(n, bodo.boolean_array, (-1,))\n'
            )
        eoy__cvxza += '  for i in numba.parfors.parfor.internal_prange(n):\n'
        if tnj__grsmr:
            null1 = 'bodo.libs.array_kernels.isna(val1, i)\n'
            erzuu__zse = 'val1[i]'
        else:
            null1 = 'False\n'
            erzuu__zse = 'val1'
        if xwhv__ejfyu:
            null2 = 'bodo.libs.array_kernels.isna(val2, i)\n'
            jgdqx__tizu = 'val2[i]'
        else:
            null2 = 'False\n'
            jgdqx__tizu = 'val2'
        if mzv__ikk:
            eoy__cvxza += f"""    result, isna_val = compute_or_body({null1}, {null2}, {erzuu__zse}, {jgdqx__tizu})
"""
        else:
            eoy__cvxza += f"""    result, isna_val = compute_and_body({null1}, {null2}, {erzuu__zse}, {jgdqx__tizu})
"""
        eoy__cvxza += '    out_arr[i] = result\n'
        eoy__cvxza += '    if isna_val:\n'
        eoy__cvxza += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
        eoy__cvxza += '      continue\n'
        eoy__cvxza += '  return out_arr\n'
        yvu__ymjt = {}
        exec(eoy__cvxza, {'bodo': bodo, 'numba': numba, 'compute_and_body':
            compute_and_body, 'compute_or_body': compute_or_body}, yvu__ymjt)
        impl = yvu__ymjt['impl']
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
        pnamr__jca = boolean_array
        return pnamr__jca(*args)


def is_valid_boolean_array_logical_op(typ1, typ2):
    cwsn__wspt = (typ1 == bodo.boolean_array or typ2 == bodo.boolean_array
        ) and (bodo.utils.utils.is_array_typ(typ1, False) and typ1.dtype ==
        types.bool_ or typ1 == types.bool_) and (bodo.utils.utils.
        is_array_typ(typ2, False) and typ2.dtype == types.bool_ or typ2 ==
        types.bool_)
    return cwsn__wspt


def _install_nullable_logical_lowering():
    for op in (operator.and_, operator.or_):
        xytu__nbci = create_boolean_array_logical_lower_impl(op)
        infer_global(op)(BooleanArrayLogicalOperatorTemplate)
        for typ1, typ2 in [(boolean_array, boolean_array), (boolean_array,
            types.bool_), (boolean_array, types.Array(types.bool_, 1, 'C'))]:
            lower_builtin(op, typ1, typ2)(xytu__nbci)
            if typ1 != typ2:
                lower_builtin(op, typ2, typ1)(xytu__nbci)


_install_nullable_logical_lowering()
