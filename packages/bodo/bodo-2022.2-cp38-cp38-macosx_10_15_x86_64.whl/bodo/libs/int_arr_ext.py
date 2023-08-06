"""Nullable integer array corresponding to Pandas IntegerArray.
However, nulls are stored in bit arrays similar to Arrow's arrays.
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import lower_constant
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, type_callable, typeof_impl, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.libs.str_arr_ext import kBitmask
from bodo.libs import array_ext, hstr_ext
ll.add_symbol('mask_arr_to_bitmap', hstr_ext.mask_arr_to_bitmap)
ll.add_symbol('is_pd_int_array', array_ext.is_pd_int_array)
ll.add_symbol('int_array_from_sequence', array_ext.int_array_from_sequence)
from bodo.hiframes.datetime_timedelta_ext import pd_timedelta_type
from bodo.utils.indexing import array_getitem_bool_index, array_getitem_int_index, array_getitem_slice_index, array_setitem_bool_index, array_setitem_int_index, array_setitem_slice_index
from bodo.utils.typing import BodoError, check_unsupported_args, is_iterable_type, is_list_like_index_type, is_overload_false, is_overload_none, is_overload_true, parse_dtype, raise_bodo_error, to_nullable_type


class IntegerArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        self.dtype = dtype
        super(IntegerArrayType, self).__init__(name='IntegerArrayType({})'.
            format(dtype))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return IntegerArrayType(self.dtype)


@register_model(IntegerArrayType)
class IntegerArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        bcgr__cvkhr = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, bcgr__cvkhr)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    cpuo__gtkgh = 8 * val.dtype.itemsize
    lktnq__avi = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(lktnq__avi, cpuo__gtkgh))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        rwd__dom = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(rwd__dom)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    lal__giys = c.context.insert_const_string(c.builder.module, 'pandas')
    pojv__kzckv = c.pyapi.import_module_noblock(lal__giys)
    dnyd__fck = c.pyapi.call_method(pojv__kzckv, str(typ)[:-2], ())
    c.pyapi.decref(pojv__kzckv)
    return dnyd__fck


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    cpuo__gtkgh = 8 * val.itemsize
    lktnq__avi = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(lktnq__avi, cpuo__gtkgh))
    return IntDtype(dtype)


def _register_int_dtype(t):
    typeof_impl.register(t)(typeof_pd_int_dtype)
    int_dtype = typeof_pd_int_dtype(t(), None)
    type_callable(t)(lambda c: lambda : int_dtype)
    lower_builtin(t)(lambda c, b, s, a: c.get_dummy_value())


pd_int_dtype_classes = (pd.Int8Dtype, pd.Int16Dtype, pd.Int32Dtype, pd.
    Int64Dtype, pd.UInt8Dtype, pd.UInt16Dtype, pd.UInt32Dtype, pd.UInt64Dtype)
for t in pd_int_dtype_classes:
    _register_int_dtype(t)


@numba.extending.register_jitable
def mask_arr_to_bitmap(mask_arr):
    n = len(mask_arr)
    kufav__dwb = n + 7 >> 3
    zxsf__qllb = np.empty(kufav__dwb, np.uint8)
    for i in range(n):
        piqaw__odxyi = i // 8
        zxsf__qllb[piqaw__odxyi] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            zxsf__qllb[piqaw__odxyi]) & kBitmask[i % 8]
    return zxsf__qllb


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    qwbrn__haam = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(qwbrn__haam)
    c.pyapi.decref(qwbrn__haam)
    pnxcg__mvf = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    kufav__dwb = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(
        64), 7)), lir.Constant(lir.IntType(64), 8))
    ixk__ufrp = bodo.utils.utils._empty_nd_impl(c.context, c.builder, types
        .Array(types.uint8, 1, 'C'), [kufav__dwb])
    eau__qtb = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()])
    eslz__ymoq = cgutils.get_or_insert_function(c.builder.module, eau__qtb,
        name='is_pd_int_array')
    ymub__rrzbh = c.builder.call(eslz__ymoq, [obj])
    udnxn__qjsek = c.builder.icmp_unsigned('!=', ymub__rrzbh, ymub__rrzbh.
        type(0))
    with c.builder.if_else(udnxn__qjsek) as (pd_then, pd_otherwise):
        with pd_then:
            bkvxr__rpw = c.pyapi.object_getattr_string(obj, '_data')
            pnxcg__mvf.data = c.pyapi.to_native_value(types.Array(typ.dtype,
                1, 'C'), bkvxr__rpw).value
            ted__fkylz = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), ted__fkylz).value
            c.pyapi.decref(bkvxr__rpw)
            c.pyapi.decref(ted__fkylz)
            uqn__hqq = c.context.make_array(types.Array(types.bool_, 1, 'C'))(c
                .context, c.builder, mask_arr)
            eau__qtb = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            eslz__ymoq = cgutils.get_or_insert_function(c.builder.module,
                eau__qtb, name='mask_arr_to_bitmap')
            c.builder.call(eslz__ymoq, [ixk__ufrp.data, uqn__hqq.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with pd_otherwise:
            mxme__kbexr = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            eau__qtb = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            xbar__zsbsh = cgutils.get_or_insert_function(c.builder.module,
                eau__qtb, name='int_array_from_sequence')
            c.builder.call(xbar__zsbsh, [obj, c.builder.bitcast(mxme__kbexr
                .data, lir.IntType(8).as_pointer()), ixk__ufrp.data])
            pnxcg__mvf.data = mxme__kbexr._getvalue()
    pnxcg__mvf.null_bitmap = ixk__ufrp._getvalue()
    fcdf__taxr = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(pnxcg__mvf._getvalue(), is_error=fcdf__taxr)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    pnxcg__mvf = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        pnxcg__mvf.data, c.env_manager)
    wpezs__qch = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, pnxcg__mvf.null_bitmap).data
    qwbrn__haam = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(qwbrn__haam)
    lal__giys = c.context.insert_const_string(c.builder.module, 'numpy')
    nwnu__neo = c.pyapi.import_module_noblock(lal__giys)
    doa__edtou = c.pyapi.object_getattr_string(nwnu__neo, 'bool_')
    mask_arr = c.pyapi.call_method(nwnu__neo, 'empty', (qwbrn__haam,
        doa__edtou))
    fqh__uafu = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    hkqr__juevw = c.pyapi.object_getattr_string(fqh__uafu, 'data')
    rjg__sttm = c.builder.inttoptr(c.pyapi.long_as_longlong(hkqr__juevw),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as loop:
        i = loop.index
        wih__zuyq = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        jlk__zfx = c.builder.load(cgutils.gep(c.builder, wpezs__qch, wih__zuyq)
            )
        kpc__kwxs = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(jlk__zfx, kpc__kwxs), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        rwvnx__fgz = cgutils.gep(c.builder, rjg__sttm, i)
        c.builder.store(val, rwvnx__fgz)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        pnxcg__mvf.null_bitmap)
    lal__giys = c.context.insert_const_string(c.builder.module, 'pandas')
    pojv__kzckv = c.pyapi.import_module_noblock(lal__giys)
    fox__vhozg = c.pyapi.object_getattr_string(pojv__kzckv, 'arrays')
    dnyd__fck = c.pyapi.call_method(fox__vhozg, 'IntegerArray', (data,
        mask_arr))
    c.pyapi.decref(pojv__kzckv)
    c.pyapi.decref(qwbrn__haam)
    c.pyapi.decref(nwnu__neo)
    c.pyapi.decref(doa__edtou)
    c.pyapi.decref(fqh__uafu)
    c.pyapi.decref(hkqr__juevw)
    c.pyapi.decref(fox__vhozg)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return dnyd__fck


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        nlohn__ful, gqz__rnt = args
        pnxcg__mvf = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        pnxcg__mvf.data = nlohn__ful
        pnxcg__mvf.null_bitmap = gqz__rnt
        context.nrt.incref(builder, signature.args[0], nlohn__ful)
        context.nrt.incref(builder, signature.args[1], gqz__rnt)
        return pnxcg__mvf._getvalue()
    inowo__ikez = IntegerArrayType(data.dtype)
    nkjsk__aoklb = inowo__ikez(data, null_bitmap)
    return nkjsk__aoklb, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    jtpcr__rma = np.empty(n, pyval.dtype.type)
    aydm__nlzca = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        hbfx__hbxu = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(aydm__nlzca, i, int(not
            hbfx__hbxu))
        if not hbfx__hbxu:
            jtpcr__rma[i] = s
    jmriq__cbt = context.get_constant_generic(builder, types.Array(typ.
        dtype, 1, 'C'), jtpcr__rma)
    odw__qtf = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), aydm__nlzca)
    return lir.Constant.literal_struct([jmriq__cbt, odw__qtf])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    ceqsk__dzwk = args[0]
    if equiv_set.has_shape(ceqsk__dzwk):
        return ArrayAnalysis.AnalyzeResult(shape=ceqsk__dzwk, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    ceqsk__dzwk = args[0]
    if equiv_set.has_shape(ceqsk__dzwk):
        return ArrayAnalysis.AnalyzeResult(shape=ceqsk__dzwk, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_init_integer_array = (
    init_integer_array_equiv)


def alias_ext_dummy_func(lhs_name, args, alias_map, arg_aliases):
    assert len(args) >= 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


def alias_ext_init_integer_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 2
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)
    numba.core.ir_utils._add_alias(lhs_name, args[1].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_integer_array',
    'bodo.libs.int_arr_ext'] = alias_ext_init_integer_array
numba.core.ir_utils.alias_func_extensions['get_int_arr_data',
    'bodo.libs.int_arr_ext'] = alias_ext_dummy_func
numba.core.ir_utils.alias_func_extensions['get_int_arr_bitmap',
    'bodo.libs.int_arr_ext'] = alias_ext_dummy_func


@numba.njit(no_cpython_wrapper=True)
def alloc_int_array(n, dtype):
    jtpcr__rma = np.empty(n, dtype)
    qzfs__alwa = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(jtpcr__rma, qzfs__alwa)


def alloc_int_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_alloc_int_array = (
    alloc_int_array_equiv)


@numba.extending.register_jitable
def set_bit_to_arr(bits, i, bit_is_set):
    bits[i // 8] ^= np.uint8(-np.uint8(bit_is_set) ^ bits[i // 8]) & kBitmask[
        i % 8]


@numba.extending.register_jitable
def get_bit_bitmap_arr(bits, i):
    return bits[i >> 3] >> (i & 7) & 1


@overload(operator.getitem, no_unliteral=True)
def int_arr_getitem(A, ind):
    if not isinstance(A, IntegerArrayType):
        return
    if isinstance(ind, types.Integer):
        return lambda A, ind: A._data[ind]
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def impl_bool(A, ind):
            gvceb__uat, xzqbw__mibu = array_getitem_bool_index(A, ind)
            return init_integer_array(gvceb__uat, xzqbw__mibu)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            gvceb__uat, xzqbw__mibu = array_getitem_int_index(A, ind)
            return init_integer_array(gvceb__uat, xzqbw__mibu)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            gvceb__uat, xzqbw__mibu = array_getitem_slice_index(A, ind)
            return init_integer_array(gvceb__uat, xzqbw__mibu)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    olwd__rzehf = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    gxj__nius = isinstance(val, (types.Integer, types.Boolean))
    if isinstance(idx, types.Integer):
        if gxj__nius:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(olwd__rzehf)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or gxj__nius):
        raise BodoError(olwd__rzehf)
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
        f'setitem for IntegerArray with indexing type {idx} not supported.')


@overload(len, no_unliteral=True)
def overload_int_arr_len(A):
    if isinstance(A, IntegerArrayType):
        return lambda A: len(A._data)


@overload_attribute(IntegerArrayType, 'shape')
def overload_int_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(IntegerArrayType, 'dtype')
def overload_int_arr_dtype(A):
    dtype_class = getattr(pd, '{}Int{}Dtype'.format('' if A.dtype.signed else
        'U', A.dtype.bitwidth))
    return lambda A: dtype_class()


@overload_attribute(IntegerArrayType, 'ndim')
def overload_int_arr_ndim(A):
    return lambda A: 1


@overload_attribute(IntegerArrayType, 'nbytes')
def int_arr_nbytes_overload(A):
    return lambda A: A._data.nbytes + A._null_bitmap.nbytes


@overload_method(IntegerArrayType, 'copy', no_unliteral=True)
def overload_int_arr_copy(A, dtype=None):
    if not is_overload_none(dtype):
        return lambda A, dtype=None: A.astype(dtype, copy=True)
    else:
        return lambda A, dtype=None: bodo.libs.int_arr_ext.init_integer_array(
            bodo.libs.int_arr_ext.get_int_arr_data(A).copy(), bodo.libs.
            int_arr_ext.get_int_arr_bitmap(A).copy())


@overload_method(IntegerArrayType, 'astype', no_unliteral=True)
def overload_int_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "IntegerArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if isinstance(dtype, types.NumberClass):
        dtype = dtype.dtype
    if isinstance(dtype, IntDtype) and A.dtype == dtype.dtype:
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
    if isinstance(dtype, IntDtype):
        np_dtype = dtype.dtype
        return (lambda A, dtype, copy=True: bodo.libs.int_arr_ext.
            init_integer_array(bodo.libs.int_arr_ext.get_int_arr_data(A).
            astype(np_dtype), bodo.libs.int_arr_ext.get_int_arr_bitmap(A).
            copy()))
    nb_dtype = parse_dtype(dtype, 'IntegerArray.astype')
    if isinstance(nb_dtype, types.Float):

        def impl_float(A, dtype, copy=True):
            data = bodo.libs.int_arr_ext.get_int_arr_data(A)
            n = len(data)
            qdlix__kmf = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                qdlix__kmf[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    qdlix__kmf[i] = np.nan
            return qdlix__kmf
        return impl_float
    return lambda A, dtype, copy=True: bodo.libs.int_arr_ext.get_int_arr_data(A
        ).astype(nb_dtype)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def apply_null_mask(arr, bitmap, mask_fill, inplace):
    assert isinstance(arr, types.Array)
    if isinstance(arr.dtype, types.Integer):
        if is_overload_none(inplace):
            return (lambda arr, bitmap, mask_fill, inplace: bodo.libs.
                int_arr_ext.init_integer_array(arr, bitmap.copy()))
        else:
            return (lambda arr, bitmap, mask_fill, inplace: bodo.libs.
                int_arr_ext.init_integer_array(arr, bitmap))
    if isinstance(arr.dtype, types.Float):

        def impl(arr, bitmap, mask_fill, inplace):
            n = len(arr)
            for i in numba.parfors.parfor.internal_prange(n):
                if not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bitmap, i):
                    arr[i] = np.nan
            return arr
        return impl
    if arr.dtype == types.bool_:

        def impl_bool(arr, bitmap, mask_fill, inplace):
            n = len(arr)
            for i in numba.parfors.parfor.internal_prange(n):
                if not bodo.libs.int_arr_ext.get_bit_bitmap_arr(bitmap, i):
                    arr[i] = mask_fill
            return arr
        return impl_bool
    return lambda arr, bitmap, mask_fill, inplace: arr


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def merge_bitmaps(B1, B2, n, inplace):
    assert B1 == types.Array(types.uint8, 1, 'C')
    assert B2 == types.Array(types.uint8, 1, 'C')
    if not is_overload_none(inplace):

        def impl_inplace(B1, B2, n, inplace):
            for i in numba.parfors.parfor.internal_prange(n):
                chst__cjw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                djnw__bnadx = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                rfvn__vln = chst__cjw & djnw__bnadx
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, rfvn__vln)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        kufav__dwb = n + 7 >> 3
        qdlix__kmf = np.empty(kufav__dwb, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            chst__cjw = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            djnw__bnadx = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            rfvn__vln = chst__cjw & djnw__bnadx
            bodo.libs.int_arr_ext.set_bit_to_arr(qdlix__kmf, i, rfvn__vln)
        return qdlix__kmf
    return impl


ufunc_aliases = {'subtract': 'sub', 'multiply': 'mul', 'floor_divide':
    'floordiv', 'true_divide': 'truediv', 'power': 'pow', 'remainder':
    'mod', 'divide': 'div', 'equal': 'eq', 'not_equal': 'ne', 'less': 'lt',
    'less_equal': 'le', 'greater': 'gt', 'greater_equal': 'ge'}


def create_op_overload(op, n_inputs):
    if n_inputs == 1:

        def overload_int_arr_op_nin_1(A):
            if isinstance(A, IntegerArrayType):
                return get_nullable_array_unary_impl(op, A)
        return overload_int_arr_op_nin_1
    elif n_inputs == 2:

        def overload_series_op_nin_2(lhs, rhs):
            if isinstance(lhs, IntegerArrayType) or isinstance(rhs,
                IntegerArrayType):
                return get_nullable_array_binary_impl(op, lhs, rhs)
        return overload_series_op_nin_2
    else:
        raise RuntimeError(
            "Don't know how to register ufuncs from ufunc_db with arity > 2")


def _install_np_ufuncs():
    import numba.np.ufunc_db
    for nqz__drtbt in numba.np.ufunc_db.get_ufuncs():
        ltaen__wki = create_op_overload(nqz__drtbt, nqz__drtbt.nin)
        overload(nqz__drtbt, no_unliteral=True)(ltaen__wki)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        ltaen__wki = create_op_overload(op, 2)
        overload(op)(ltaen__wki)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        ltaen__wki = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(ltaen__wki)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        ltaen__wki = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(ltaen__wki)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    rho__nknty = len(arrs.types)
    neq__cmi = 'def f(arrs):\n'
    dnyd__fck = ', '.join('arrs[{}]._data'.format(i) for i in range(rho__nknty)
        )
    neq__cmi += '  return ({}{})\n'.format(dnyd__fck, ',' if rho__nknty == 
        1 else '')
    xzijr__ugksl = {}
    exec(neq__cmi, {}, xzijr__ugksl)
    impl = xzijr__ugksl['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    rho__nknty = len(arrs.types)
    tyqb__vrg = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        rho__nknty))
    neq__cmi = 'def f(arrs):\n'
    neq__cmi += '  n = {}\n'.format(tyqb__vrg)
    neq__cmi += '  n_bytes = (n + 7) >> 3\n'
    neq__cmi += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    neq__cmi += '  curr_bit = 0\n'
    for i in range(rho__nknty):
        neq__cmi += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        neq__cmi += '  for j in range(len(arrs[{}])):\n'.format(i)
        neq__cmi += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        neq__cmi += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        neq__cmi += '    curr_bit += 1\n'
    neq__cmi += '  return new_mask\n'
    xzijr__ugksl = {}
    exec(neq__cmi, {'np': np, 'bodo': bodo}, xzijr__ugksl)
    impl = xzijr__ugksl['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    pnt__bikd = dict(skipna=skipna, min_count=min_count)
    rywah__rlo = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', pnt__bikd, rywah__rlo)

    def impl(A, skipna=True, min_count=0):
        numba.parfors.parfor.init_prange()
        s = 0
        for i in numba.parfors.parfor.internal_prange(len(A)):
            val = 0
            if not bodo.libs.array_kernels.isna(A, i):
                val = A[i]
            s += val
        return s
    return impl


@overload_method(IntegerArrayType, 'unique', no_unliteral=True)
def overload_unique(A):
    dtype = A.dtype

    def impl_int_arr(A):
        data = []
        kpc__kwxs = []
        ckpnp__ttzji = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not ckpnp__ttzji:
                    data.append(dtype(1))
                    kpc__kwxs.append(False)
                    ckpnp__ttzji = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                kpc__kwxs.append(True)
        gvceb__uat = np.array(data)
        n = len(gvceb__uat)
        kufav__dwb = n + 7 >> 3
        xzqbw__mibu = np.empty(kufav__dwb, np.uint8)
        for mow__siz in range(n):
            set_bit_to_arr(xzqbw__mibu, mow__siz, kpc__kwxs[mow__siz])
        return init_integer_array(gvceb__uat, xzqbw__mibu)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    jcgcs__vuysp = numba.core.registry.cpu_target.typing_context
    zhud__nrcw = jcgcs__vuysp.resolve_function_type(op, (types.Array(A.
        dtype, 1, 'C'),), {}).return_type
    zhud__nrcw = to_nullable_type(zhud__nrcw)

    def impl(A):
        n = len(A)
        ktk__efzd = bodo.utils.utils.alloc_type(n, zhud__nrcw, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(ktk__efzd, i)
                continue
            ktk__efzd[i] = op(A[i])
        return ktk__efzd
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    cfo__euxcx = isinstance(lhs, (types.Number, types.Boolean))
    gklsl__yycj = isinstance(rhs, (types.Number, types.Boolean))
    isjoc__far = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    zls__cis = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    jcgcs__vuysp = numba.core.registry.cpu_target.typing_context
    zhud__nrcw = jcgcs__vuysp.resolve_function_type(op, (isjoc__far,
        zls__cis), {}).return_type
    zhud__nrcw = to_nullable_type(zhud__nrcw)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    ubsk__wnm = 'lhs' if cfo__euxcx else 'lhs[i]'
    djcy__nleh = 'rhs' if gklsl__yycj else 'rhs[i]'
    dvin__jfdm = ('False' if cfo__euxcx else
        'bodo.libs.array_kernels.isna(lhs, i)')
    pol__ityuo = ('False' if gklsl__yycj else
        'bodo.libs.array_kernels.isna(rhs, i)')
    neq__cmi = 'def impl(lhs, rhs):\n'
    neq__cmi += '  n = len({})\n'.format('lhs' if not cfo__euxcx else 'rhs')
    if inplace:
        neq__cmi += '  out_arr = {}\n'.format('lhs' if not cfo__euxcx else
            'rhs')
    else:
        neq__cmi += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    neq__cmi += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    neq__cmi += '    if ({}\n'.format(dvin__jfdm)
    neq__cmi += '        or {}):\n'.format(pol__ityuo)
    neq__cmi += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    neq__cmi += '      continue\n'
    neq__cmi += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(ubsk__wnm, djcy__nleh))
    neq__cmi += '  return out_arr\n'
    xzijr__ugksl = {}
    exec(neq__cmi, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        zhud__nrcw, 'op': op}, xzijr__ugksl)
    impl = xzijr__ugksl['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        cfo__euxcx = lhs in [pd_timedelta_type]
        gklsl__yycj = rhs in [pd_timedelta_type]
        if cfo__euxcx:

            def impl(lhs, rhs):
                n = len(rhs)
                ktk__efzd = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(ktk__efzd, i)
                        continue
                    ktk__efzd[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs, rhs[i]))
                return ktk__efzd
            return impl
        elif gklsl__yycj:

            def impl(lhs, rhs):
                n = len(lhs)
                ktk__efzd = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(ktk__efzd, i)
                        continue
                    ktk__efzd[i] = bodo.utils.conversion.unbox_if_timestamp(op
                        (lhs[i], rhs))
                return ktk__efzd
            return impl
    return impl
