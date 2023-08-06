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
        mknw__uaivz = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, mknw__uaivz)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    lcl__rqs = 8 * val.dtype.itemsize
    wlyju__ifj = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(wlyju__ifj, lcl__rqs))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        kvacp__oxozj = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(kvacp__oxozj)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    yub__yud = c.context.insert_const_string(c.builder.module, 'pandas')
    rff__aronz = c.pyapi.import_module_noblock(yub__yud)
    yrdt__govzh = c.pyapi.call_method(rff__aronz, str(typ)[:-2], ())
    c.pyapi.decref(rff__aronz)
    return yrdt__govzh


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    lcl__rqs = 8 * val.itemsize
    wlyju__ifj = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(wlyju__ifj, lcl__rqs))
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
    ontj__ftj = n + 7 >> 3
    dgd__ggex = np.empty(ontj__ftj, np.uint8)
    for i in range(n):
        zsl__edl = i // 8
        dgd__ggex[zsl__edl] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            dgd__ggex[zsl__edl]) & kBitmask[i % 8]
    return dgd__ggex


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    vybvf__yvhh = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(vybvf__yvhh)
    c.pyapi.decref(vybvf__yvhh)
    xhont__khz = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    ontj__ftj = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64
        ), 7)), lir.Constant(lir.IntType(64), 8))
    xpyvz__nrk = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [ontj__ftj])
    icq__loob = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    onj__aevmm = cgutils.get_or_insert_function(c.builder.module, icq__loob,
        name='is_pd_int_array')
    fft__yhqi = c.builder.call(onj__aevmm, [obj])
    jkt__irx = c.builder.icmp_unsigned('!=', fft__yhqi, fft__yhqi.type(0))
    with c.builder.if_else(jkt__irx) as (pd_then, pd_otherwise):
        with pd_then:
            bxuz__sap = c.pyapi.object_getattr_string(obj, '_data')
            xhont__khz.data = c.pyapi.to_native_value(types.Array(typ.dtype,
                1, 'C'), bxuz__sap).value
            vgp__eppp = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), vgp__eppp).value
            c.pyapi.decref(bxuz__sap)
            c.pyapi.decref(vgp__eppp)
            juxsr__yzb = c.context.make_array(types.Array(types.bool_, 1, 'C')
                )(c.context, c.builder, mask_arr)
            icq__loob = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            onj__aevmm = cgutils.get_or_insert_function(c.builder.module,
                icq__loob, name='mask_arr_to_bitmap')
            c.builder.call(onj__aevmm, [xpyvz__nrk.data, juxsr__yzb.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with pd_otherwise:
            eyfei__ekjt = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            icq__loob = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            uez__jiuzv = cgutils.get_or_insert_function(c.builder.module,
                icq__loob, name='int_array_from_sequence')
            c.builder.call(uez__jiuzv, [obj, c.builder.bitcast(eyfei__ekjt.
                data, lir.IntType(8).as_pointer()), xpyvz__nrk.data])
            xhont__khz.data = eyfei__ekjt._getvalue()
    xhont__khz.null_bitmap = xpyvz__nrk._getvalue()
    xqjja__tnb = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(xhont__khz._getvalue(), is_error=xqjja__tnb)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    xhont__khz = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        xhont__khz.data, c.env_manager)
    ighul__dujj = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, xhont__khz.null_bitmap).data
    vybvf__yvhh = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(vybvf__yvhh)
    yub__yud = c.context.insert_const_string(c.builder.module, 'numpy')
    jpag__ripe = c.pyapi.import_module_noblock(yub__yud)
    xkc__pax = c.pyapi.object_getattr_string(jpag__ripe, 'bool_')
    mask_arr = c.pyapi.call_method(jpag__ripe, 'empty', (vybvf__yvhh, xkc__pax)
        )
    xzkg__rohxv = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    uvhx__gsixh = c.pyapi.object_getattr_string(xzkg__rohxv, 'data')
    pxw__qtx = c.builder.inttoptr(c.pyapi.long_as_longlong(uvhx__gsixh),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as loop:
        i = loop.index
        dobig__wwaf = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        yhw__hcj = c.builder.load(cgutils.gep(c.builder, ighul__dujj,
            dobig__wwaf))
        bzol__ibkeo = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(yhw__hcj, bzol__ibkeo), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        nxl__vtrq = cgutils.gep(c.builder, pxw__qtx, i)
        c.builder.store(val, nxl__vtrq)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        xhont__khz.null_bitmap)
    yub__yud = c.context.insert_const_string(c.builder.module, 'pandas')
    rff__aronz = c.pyapi.import_module_noblock(yub__yud)
    qth__byafm = c.pyapi.object_getattr_string(rff__aronz, 'arrays')
    yrdt__govzh = c.pyapi.call_method(qth__byafm, 'IntegerArray', (data,
        mask_arr))
    c.pyapi.decref(rff__aronz)
    c.pyapi.decref(vybvf__yvhh)
    c.pyapi.decref(jpag__ripe)
    c.pyapi.decref(xkc__pax)
    c.pyapi.decref(xzkg__rohxv)
    c.pyapi.decref(uvhx__gsixh)
    c.pyapi.decref(qth__byafm)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return yrdt__govzh


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        fpxqx__sswhx, kbnmv__akz = args
        xhont__khz = cgutils.create_struct_proxy(signature.return_type)(context
            , builder)
        xhont__khz.data = fpxqx__sswhx
        xhont__khz.null_bitmap = kbnmv__akz
        context.nrt.incref(builder, signature.args[0], fpxqx__sswhx)
        context.nrt.incref(builder, signature.args[1], kbnmv__akz)
        return xhont__khz._getvalue()
    aok__kmim = IntegerArrayType(data.dtype)
    tfasn__nkuuq = aok__kmim(data, null_bitmap)
    return tfasn__nkuuq, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    ifukr__onfz = np.empty(n, pyval.dtype.type)
    eewr__isxje = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        fxn__pxnnc = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(eewr__isxje, i, int(not
            fxn__pxnnc))
        if not fxn__pxnnc:
            ifukr__onfz[i] = s
    cxpo__xmdu = context.get_constant_generic(builder, types.Array(typ.
        dtype, 1, 'C'), ifukr__onfz)
    dkh__pdb = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), eewr__isxje)
    return lir.Constant.literal_struct([cxpo__xmdu, dkh__pdb])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    nsta__bjkb = args[0]
    if equiv_set.has_shape(nsta__bjkb):
        return ArrayAnalysis.AnalyzeResult(shape=nsta__bjkb, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    nsta__bjkb = args[0]
    if equiv_set.has_shape(nsta__bjkb):
        return ArrayAnalysis.AnalyzeResult(shape=nsta__bjkb, pre=[])
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
    ifukr__onfz = np.empty(n, dtype)
    guoj__qujb = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(ifukr__onfz, guoj__qujb)


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
            bcwth__xiop, pjhd__umd = array_getitem_bool_index(A, ind)
            return init_integer_array(bcwth__xiop, pjhd__umd)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            bcwth__xiop, pjhd__umd = array_getitem_int_index(A, ind)
            return init_integer_array(bcwth__xiop, pjhd__umd)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            bcwth__xiop, pjhd__umd = array_getitem_slice_index(A, ind)
            return init_integer_array(bcwth__xiop, pjhd__umd)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    lzb__scvw = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    hnbun__ttoke = isinstance(val, (types.Integer, types.Boolean))
    if isinstance(idx, types.Integer):
        if hnbun__ttoke:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(lzb__scvw)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or hnbun__ttoke):
        raise BodoError(lzb__scvw)
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
            nlkt__yfnl = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                nlkt__yfnl[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    nlkt__yfnl[i] = np.nan
            return nlkt__yfnl
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
                zcxt__qydi = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                zhjp__wrc = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                jkz__krobu = zcxt__qydi & zhjp__wrc
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, jkz__krobu)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        ontj__ftj = n + 7 >> 3
        nlkt__yfnl = np.empty(ontj__ftj, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            zcxt__qydi = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            zhjp__wrc = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            jkz__krobu = zcxt__qydi & zhjp__wrc
            bodo.libs.int_arr_ext.set_bit_to_arr(nlkt__yfnl, i, jkz__krobu)
        return nlkt__yfnl
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
    for kggbx__fru in numba.np.ufunc_db.get_ufuncs():
        vah__dpiay = create_op_overload(kggbx__fru, kggbx__fru.nin)
        overload(kggbx__fru, no_unliteral=True)(vah__dpiay)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        vah__dpiay = create_op_overload(op, 2)
        overload(op)(vah__dpiay)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        vah__dpiay = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(vah__dpiay)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        vah__dpiay = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(vah__dpiay)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    fkk__xvcd = len(arrs.types)
    owem__kmsd = 'def f(arrs):\n'
    yrdt__govzh = ', '.join('arrs[{}]._data'.format(i) for i in range(
        fkk__xvcd))
    owem__kmsd += '  return ({}{})\n'.format(yrdt__govzh, ',' if fkk__xvcd ==
        1 else '')
    tsl__xrma = {}
    exec(owem__kmsd, {}, tsl__xrma)
    impl = tsl__xrma['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    fkk__xvcd = len(arrs.types)
    ampju__atg = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        fkk__xvcd))
    owem__kmsd = 'def f(arrs):\n'
    owem__kmsd += '  n = {}\n'.format(ampju__atg)
    owem__kmsd += '  n_bytes = (n + 7) >> 3\n'
    owem__kmsd += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    owem__kmsd += '  curr_bit = 0\n'
    for i in range(fkk__xvcd):
        owem__kmsd += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        owem__kmsd += '  for j in range(len(arrs[{}])):\n'.format(i)
        owem__kmsd += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        owem__kmsd += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        owem__kmsd += '    curr_bit += 1\n'
    owem__kmsd += '  return new_mask\n'
    tsl__xrma = {}
    exec(owem__kmsd, {'np': np, 'bodo': bodo}, tsl__xrma)
    impl = tsl__xrma['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    uljk__xoph = dict(skipna=skipna, min_count=min_count)
    dxc__caq = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', uljk__xoph, dxc__caq)

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
        bzol__ibkeo = []
        xhvvr__bbp = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not xhvvr__bbp:
                    data.append(dtype(1))
                    bzol__ibkeo.append(False)
                    xhvvr__bbp = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                bzol__ibkeo.append(True)
        bcwth__xiop = np.array(data)
        n = len(bcwth__xiop)
        ontj__ftj = n + 7 >> 3
        pjhd__umd = np.empty(ontj__ftj, np.uint8)
        for pems__weco in range(n):
            set_bit_to_arr(pjhd__umd, pems__weco, bzol__ibkeo[pems__weco])
        return init_integer_array(bcwth__xiop, pjhd__umd)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    phvb__oax = numba.core.registry.cpu_target.typing_context
    pqcm__nqlf = phvb__oax.resolve_function_type(op, (types.Array(A.dtype, 
        1, 'C'),), {}).return_type
    pqcm__nqlf = to_nullable_type(pqcm__nqlf)

    def impl(A):
        n = len(A)
        ecgbm__ickpc = bodo.utils.utils.alloc_type(n, pqcm__nqlf, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(ecgbm__ickpc, i)
                continue
            ecgbm__ickpc[i] = op(A[i])
        return ecgbm__ickpc
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    uha__rwn = isinstance(lhs, (types.Number, types.Boolean))
    dhqv__aivsp = isinstance(rhs, (types.Number, types.Boolean))
    btkmw__wnm = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    tsdym__utwh = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    phvb__oax = numba.core.registry.cpu_target.typing_context
    pqcm__nqlf = phvb__oax.resolve_function_type(op, (btkmw__wnm,
        tsdym__utwh), {}).return_type
    pqcm__nqlf = to_nullable_type(pqcm__nqlf)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    qii__aaxd = 'lhs' if uha__rwn else 'lhs[i]'
    xvp__fuwy = 'rhs' if dhqv__aivsp else 'rhs[i]'
    zwyes__crnj = ('False' if uha__rwn else
        'bodo.libs.array_kernels.isna(lhs, i)')
    agd__udk = ('False' if dhqv__aivsp else
        'bodo.libs.array_kernels.isna(rhs, i)')
    owem__kmsd = 'def impl(lhs, rhs):\n'
    owem__kmsd += '  n = len({})\n'.format('lhs' if not uha__rwn else 'rhs')
    if inplace:
        owem__kmsd += '  out_arr = {}\n'.format('lhs' if not uha__rwn else
            'rhs')
    else:
        owem__kmsd += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    owem__kmsd += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    owem__kmsd += '    if ({}\n'.format(zwyes__crnj)
    owem__kmsd += '        or {}):\n'.format(agd__udk)
    owem__kmsd += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    owem__kmsd += '      continue\n'
    owem__kmsd += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(qii__aaxd, xvp__fuwy))
    owem__kmsd += '  return out_arr\n'
    tsl__xrma = {}
    exec(owem__kmsd, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        pqcm__nqlf, 'op': op}, tsl__xrma)
    impl = tsl__xrma['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        uha__rwn = lhs in [pd_timedelta_type]
        dhqv__aivsp = rhs in [pd_timedelta_type]
        if uha__rwn:

            def impl(lhs, rhs):
                n = len(rhs)
                ecgbm__ickpc = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(ecgbm__ickpc, i)
                        continue
                    ecgbm__ickpc[i] = bodo.utils.conversion.unbox_if_timestamp(
                        op(lhs, rhs[i]))
                return ecgbm__ickpc
            return impl
        elif dhqv__aivsp:

            def impl(lhs, rhs):
                n = len(lhs)
                ecgbm__ickpc = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(ecgbm__ickpc, i)
                        continue
                    ecgbm__ickpc[i] = bodo.utils.conversion.unbox_if_timestamp(
                        op(lhs[i], rhs))
                return ecgbm__ickpc
            return impl
    return impl
