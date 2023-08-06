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
        lroz__tldw = [('data', types.Array(fe_type.dtype, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, lroz__tldw)


make_attribute_wrapper(IntegerArrayType, 'data', '_data')
make_attribute_wrapper(IntegerArrayType, 'null_bitmap', '_null_bitmap')


@typeof_impl.register(pd.arrays.IntegerArray)
def _typeof_pd_int_array(val, c):
    acqpd__zhkzl = 8 * val.dtype.itemsize
    drlzf__cwu = '' if val.dtype.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(drlzf__cwu, acqpd__zhkzl))
    return IntegerArrayType(dtype)


class IntDtype(types.Number):

    def __init__(self, dtype):
        assert isinstance(dtype, types.Integer)
        self.dtype = dtype
        kffn__jhnqm = '{}Int{}Dtype()'.format('' if dtype.signed else 'U',
            dtype.bitwidth)
        super(IntDtype, self).__init__(kffn__jhnqm)


register_model(IntDtype)(models.OpaqueModel)


@box(IntDtype)
def box_intdtype(typ, val, c):
    emvnq__jznn = c.context.insert_const_string(c.builder.module, 'pandas')
    ypmub__rfy = c.pyapi.import_module_noblock(emvnq__jznn)
    gttas__whkg = c.pyapi.call_method(ypmub__rfy, str(typ)[:-2], ())
    c.pyapi.decref(ypmub__rfy)
    return gttas__whkg


@unbox(IntDtype)
def unbox_intdtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


def typeof_pd_int_dtype(val, c):
    acqpd__zhkzl = 8 * val.itemsize
    drlzf__cwu = '' if val.kind == 'i' else 'u'
    dtype = getattr(types, '{}int{}'.format(drlzf__cwu, acqpd__zhkzl))
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
    uwmn__foj = n + 7 >> 3
    iqrjz__vlul = np.empty(uwmn__foj, np.uint8)
    for i in range(n):
        wkaal__lqt = i // 8
        iqrjz__vlul[wkaal__lqt] ^= np.uint8(-np.uint8(not mask_arr[i]) ^
            iqrjz__vlul[wkaal__lqt]) & kBitmask[i % 8]
    return iqrjz__vlul


@unbox(IntegerArrayType)
def unbox_int_array(typ, obj, c):
    ldgvp__ijp = c.pyapi.call_method(obj, '__len__', ())
    n = c.pyapi.long_as_longlong(ldgvp__ijp)
    c.pyapi.decref(ldgvp__ijp)
    ckips__plxzr = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    uwmn__foj = c.builder.udiv(c.builder.add(n, lir.Constant(lir.IntType(64
        ), 7)), lir.Constant(lir.IntType(64), 8))
    pfuyd__gwr = bodo.utils.utils._empty_nd_impl(c.context, c.builder,
        types.Array(types.uint8, 1, 'C'), [uwmn__foj])
    xyfa__sle = lir.FunctionType(lir.IntType(32), [lir.IntType(8).as_pointer()]
        )
    oss__cnzq = cgutils.get_or_insert_function(c.builder.module, xyfa__sle,
        name='is_pd_int_array')
    vhw__wkatv = c.builder.call(oss__cnzq, [obj])
    ajdnt__fexg = c.builder.icmp_unsigned('!=', vhw__wkatv, vhw__wkatv.type(0))
    with c.builder.if_else(ajdnt__fexg) as (pd_then, pd_otherwise):
        with pd_then:
            nget__zrtz = c.pyapi.object_getattr_string(obj, '_data')
            ckips__plxzr.data = c.pyapi.to_native_value(types.Array(typ.
                dtype, 1, 'C'), nget__zrtz).value
            sihme__qoty = c.pyapi.object_getattr_string(obj, '_mask')
            mask_arr = c.pyapi.to_native_value(types.Array(types.bool_, 1,
                'C'), sihme__qoty).value
            c.pyapi.decref(nget__zrtz)
            c.pyapi.decref(sihme__qoty)
            yhl__zpd = c.context.make_array(types.Array(types.bool_, 1, 'C'))(c
                .context, c.builder, mask_arr)
            xyfa__sle = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64)])
            oss__cnzq = cgutils.get_or_insert_function(c.builder.module,
                xyfa__sle, name='mask_arr_to_bitmap')
            c.builder.call(oss__cnzq, [pfuyd__gwr.data, yhl__zpd.data, n])
            c.context.nrt.decref(c.builder, types.Array(types.bool_, 1, 'C'
                ), mask_arr)
        with pd_otherwise:
            piuzu__upabl = bodo.utils.utils._empty_nd_impl(c.context, c.
                builder, types.Array(typ.dtype, 1, 'C'), [n])
            xyfa__sle = lir.FunctionType(lir.IntType(32), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
                as_pointer()])
            vmgdo__smrs = cgutils.get_or_insert_function(c.builder.module,
                xyfa__sle, name='int_array_from_sequence')
            c.builder.call(vmgdo__smrs, [obj, c.builder.bitcast(
                piuzu__upabl.data, lir.IntType(8).as_pointer()), pfuyd__gwr
                .data])
            ckips__plxzr.data = piuzu__upabl._getvalue()
    ckips__plxzr.null_bitmap = pfuyd__gwr._getvalue()
    lytl__trtf = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ckips__plxzr._getvalue(), is_error=lytl__trtf)


@box(IntegerArrayType)
def box_int_arr(typ, val, c):
    ckips__plxzr = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    data = c.pyapi.from_native_value(types.Array(typ.dtype, 1, 'C'),
        ckips__plxzr.data, c.env_manager)
    lsf__wwfug = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c.
        context, c.builder, ckips__plxzr.null_bitmap).data
    ldgvp__ijp = c.pyapi.call_method(data, '__len__', ())
    n = c.pyapi.long_as_longlong(ldgvp__ijp)
    emvnq__jznn = c.context.insert_const_string(c.builder.module, 'numpy')
    ont__lpd = c.pyapi.import_module_noblock(emvnq__jznn)
    pdxky__vrv = c.pyapi.object_getattr_string(ont__lpd, 'bool_')
    mask_arr = c.pyapi.call_method(ont__lpd, 'empty', (ldgvp__ijp, pdxky__vrv))
    iaq__rlmb = c.pyapi.object_getattr_string(mask_arr, 'ctypes')
    ztkti__qpe = c.pyapi.object_getattr_string(iaq__rlmb, 'data')
    uvecb__qnhr = c.builder.inttoptr(c.pyapi.long_as_longlong(ztkti__qpe),
        lir.IntType(8).as_pointer())
    with cgutils.for_range(c.builder, n) as loop:
        i = loop.index
        fzpc__cfwvc = c.builder.lshr(i, lir.Constant(lir.IntType(64), 3))
        vlun__ybnb = c.builder.load(cgutils.gep(c.builder, lsf__wwfug,
            fzpc__cfwvc))
        rbi__dbez = c.builder.trunc(c.builder.and_(i, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = c.builder.and_(c.builder.lshr(vlun__ybnb, rbi__dbez), lir.
            Constant(lir.IntType(8), 1))
        val = c.builder.xor(val, lir.Constant(lir.IntType(8), 1))
        omwh__bbsbk = cgutils.gep(c.builder, uvecb__qnhr, i)
        c.builder.store(val, omwh__bbsbk)
    c.context.nrt.decref(c.builder, types.Array(types.uint8, 1, 'C'),
        ckips__plxzr.null_bitmap)
    emvnq__jznn = c.context.insert_const_string(c.builder.module, 'pandas')
    ypmub__rfy = c.pyapi.import_module_noblock(emvnq__jznn)
    xie__rgkwi = c.pyapi.object_getattr_string(ypmub__rfy, 'arrays')
    gttas__whkg = c.pyapi.call_method(xie__rgkwi, 'IntegerArray', (data,
        mask_arr))
    c.pyapi.decref(ypmub__rfy)
    c.pyapi.decref(ldgvp__ijp)
    c.pyapi.decref(ont__lpd)
    c.pyapi.decref(pdxky__vrv)
    c.pyapi.decref(iaq__rlmb)
    c.pyapi.decref(ztkti__qpe)
    c.pyapi.decref(xie__rgkwi)
    c.pyapi.decref(data)
    c.pyapi.decref(mask_arr)
    return gttas__whkg


@intrinsic
def init_integer_array(typingctx, data, null_bitmap=None):
    assert isinstance(data, types.Array)
    assert null_bitmap == types.Array(types.uint8, 1, 'C')

    def codegen(context, builder, signature, args):
        okxx__vuow, nhh__dxb = args
        ckips__plxzr = cgutils.create_struct_proxy(signature.return_type)(
            context, builder)
        ckips__plxzr.data = okxx__vuow
        ckips__plxzr.null_bitmap = nhh__dxb
        context.nrt.incref(builder, signature.args[0], okxx__vuow)
        context.nrt.incref(builder, signature.args[1], nhh__dxb)
        return ckips__plxzr._getvalue()
    eksh__wujgr = IntegerArrayType(data.dtype)
    keqhr__wus = eksh__wujgr(data, null_bitmap)
    return keqhr__wus, codegen


@lower_constant(IntegerArrayType)
def lower_constant_int_arr(context, builder, typ, pyval):
    n = len(pyval)
    mzw__mvowv = np.empty(n, pyval.dtype.type)
    ksj__jauo = np.empty(n + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        gdg__vhnpm = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(ksj__jauo, i, int(not gdg__vhnpm))
        if not gdg__vhnpm:
            mzw__mvowv[i] = s
    cob__ciiqs = context.get_constant_generic(builder, types.Array(typ.
        dtype, 1, 'C'), mzw__mvowv)
    yrsys__gaw = context.get_constant_generic(builder, types.Array(types.
        uint8, 1, 'C'), ksj__jauo)
    return lir.Constant.literal_struct([cob__ciiqs, yrsys__gaw])


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data(A):
    return lambda A: A._data


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_bitmap(A):
    return lambda A: A._null_bitmap


def get_int_arr_data_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 1 and not kws
    lyb__ggpgc = args[0]
    if equiv_set.has_shape(lyb__ggpgc):
        return ArrayAnalysis.AnalyzeResult(shape=lyb__ggpgc, pre=[])
    return None


ArrayAnalysis._analyze_op_call_bodo_libs_int_arr_ext_get_int_arr_data = (
    get_int_arr_data_equiv)


def init_integer_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    lyb__ggpgc = args[0]
    if equiv_set.has_shape(lyb__ggpgc):
        return ArrayAnalysis.AnalyzeResult(shape=lyb__ggpgc, pre=[])
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
    mzw__mvowv = np.empty(n, dtype)
    yywyd__pjcme = np.empty(n + 7 >> 3, dtype=np.uint8)
    return init_integer_array(mzw__mvowv, yywyd__pjcme)


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
            evcue__jtrm, bujsk__jlrl = array_getitem_bool_index(A, ind)
            return init_integer_array(evcue__jtrm, bujsk__jlrl)
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def impl(A, ind):
            evcue__jtrm, bujsk__jlrl = array_getitem_int_index(A, ind)
            return init_integer_array(evcue__jtrm, bujsk__jlrl)
        return impl
    if isinstance(ind, types.SliceType):

        def impl_slice(A, ind):
            evcue__jtrm, bujsk__jlrl = array_getitem_slice_index(A, ind)
            return init_integer_array(evcue__jtrm, bujsk__jlrl)
        return impl_slice
    raise BodoError(
        f'getitem for IntegerArray with indexing type {ind} not supported.')


@overload(operator.setitem, no_unliteral=True)
def int_arr_setitem(A, idx, val):
    if not isinstance(A, IntegerArrayType):
        return
    if val == types.none or isinstance(val, types.optional):
        return
    tbm__trnhq = (
        f"setitem for IntegerArray with indexing type {idx} received an incorrect 'value' type {val}."
        )
    ufhwl__rdyc = isinstance(val, (types.Integer, types.Boolean))
    if isinstance(idx, types.Integer):
        if ufhwl__rdyc:

            def impl_scalar(A, idx, val):
                A._data[idx] = val
                bodo.libs.int_arr_ext.set_bit_to_arr(A._null_bitmap, idx, 1)
            return impl_scalar
        else:
            raise BodoError(tbm__trnhq)
    if not (is_iterable_type(val) and isinstance(val.dtype, (types.Integer,
        types.Boolean)) or ufhwl__rdyc):
        raise BodoError(tbm__trnhq)
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
            eost__ojm = np.empty(n, nb_dtype)
            for i in numba.parfors.parfor.internal_prange(n):
                eost__ojm[i] = data[i]
                if bodo.libs.array_kernels.isna(A, i):
                    eost__ojm[i] = np.nan
            return eost__ojm
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
                yhke__pmckl = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
                uiwdl__gzkgj = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
                mqt__skkfd = yhke__pmckl & uiwdl__gzkgj
                bodo.libs.int_arr_ext.set_bit_to_arr(B1, i, mqt__skkfd)
            return B1
        return impl_inplace

    def impl(B1, B2, n, inplace):
        numba.parfors.parfor.init_prange()
        uwmn__foj = n + 7 >> 3
        eost__ojm = np.empty(uwmn__foj, np.uint8)
        for i in numba.parfors.parfor.internal_prange(n):
            yhke__pmckl = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B1, i)
            uiwdl__gzkgj = bodo.libs.int_arr_ext.get_bit_bitmap_arr(B2, i)
            mqt__skkfd = yhke__pmckl & uiwdl__gzkgj
            bodo.libs.int_arr_ext.set_bit_to_arr(eost__ojm, i, mqt__skkfd)
        return eost__ojm
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
    for sndgj__mba in numba.np.ufunc_db.get_ufuncs():
        kco__wmt = create_op_overload(sndgj__mba, sndgj__mba.nin)
        overload(sndgj__mba, no_unliteral=True)(kco__wmt)


_install_np_ufuncs()
skips = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt,
    operator.ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.pow, operator.mod]


def _install_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesArrayOperator._op_map.keys():
        if op in skips:
            continue
        kco__wmt = create_op_overload(op, 2)
        overload(op)(kco__wmt)


_install_binary_ops()


def _install_inplace_binary_ops():
    for op in numba.core.typing.npydecl.NumpyRulesInplaceArrayOperator._op_map.keys(
        ):
        kco__wmt = create_op_overload(op, 2)
        overload(op, no_unliteral=True)(kco__wmt)


_install_inplace_binary_ops()


def _install_unary_ops():
    for op in (operator.neg, operator.invert, operator.pos):
        kco__wmt = create_op_overload(op, 1)
        overload(op, no_unliteral=True)(kco__wmt)


_install_unary_ops()


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_int_arr_data_tup(arrs):
    hked__mrgp = len(arrs.types)
    wzelt__aamuu = 'def f(arrs):\n'
    gttas__whkg = ', '.join('arrs[{}]._data'.format(i) for i in range(
        hked__mrgp))
    wzelt__aamuu += '  return ({}{})\n'.format(gttas__whkg, ',' if 
        hked__mrgp == 1 else '')
    coc__fbr = {}
    exec(wzelt__aamuu, {}, coc__fbr)
    impl = coc__fbr['f']
    return impl


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def concat_bitmap_tup(arrs):
    hked__mrgp = len(arrs.types)
    moyu__dvkbk = '+'.join('len(arrs[{}]._data)'.format(i) for i in range(
        hked__mrgp))
    wzelt__aamuu = 'def f(arrs):\n'
    wzelt__aamuu += '  n = {}\n'.format(moyu__dvkbk)
    wzelt__aamuu += '  n_bytes = (n + 7) >> 3\n'
    wzelt__aamuu += '  new_mask = np.empty(n_bytes, np.uint8)\n'
    wzelt__aamuu += '  curr_bit = 0\n'
    for i in range(hked__mrgp):
        wzelt__aamuu += '  old_mask = arrs[{}]._null_bitmap\n'.format(i)
        wzelt__aamuu += '  for j in range(len(arrs[{}])):\n'.format(i)
        wzelt__aamuu += (
            '    bit = bodo.libs.int_arr_ext.get_bit_bitmap_arr(old_mask, j)\n'
            )
        wzelt__aamuu += (
            '    bodo.libs.int_arr_ext.set_bit_to_arr(new_mask, curr_bit, bit)\n'
            )
        wzelt__aamuu += '    curr_bit += 1\n'
    wzelt__aamuu += '  return new_mask\n'
    coc__fbr = {}
    exec(wzelt__aamuu, {'np': np, 'bodo': bodo}, coc__fbr)
    impl = coc__fbr['f']
    return impl


@overload_method(IntegerArrayType, 'sum', no_unliteral=True)
def overload_int_arr_sum(A, skipna=True, min_count=0):
    nhcmu__mtsw = dict(skipna=skipna, min_count=min_count)
    xgoal__jvq = dict(skipna=True, min_count=0)
    check_unsupported_args('IntegerArray.sum', nhcmu__mtsw, xgoal__jvq)

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
        rbi__dbez = []
        wgtoh__pugm = False
        s = set()
        for i in range(len(A)):
            val = A[i]
            if bodo.libs.array_kernels.isna(A, i):
                if not wgtoh__pugm:
                    data.append(dtype(1))
                    rbi__dbez.append(False)
                    wgtoh__pugm = True
                continue
            if val not in s:
                s.add(val)
                data.append(val)
                rbi__dbez.append(True)
        evcue__jtrm = np.array(data)
        n = len(evcue__jtrm)
        uwmn__foj = n + 7 >> 3
        bujsk__jlrl = np.empty(uwmn__foj, np.uint8)
        for nxw__cqkub in range(n):
            set_bit_to_arr(bujsk__jlrl, nxw__cqkub, rbi__dbez[nxw__cqkub])
        return init_integer_array(evcue__jtrm, bujsk__jlrl)
    return impl_int_arr


def get_nullable_array_unary_impl(op, A):
    ogyd__otdlq = numba.core.registry.cpu_target.typing_context
    crrte__evil = ogyd__otdlq.resolve_function_type(op, (types.Array(A.
        dtype, 1, 'C'),), {}).return_type
    crrte__evil = to_nullable_type(crrte__evil)

    def impl(A):
        n = len(A)
        bhaf__vbfwb = bodo.utils.utils.alloc_type(n, crrte__evil, None)
        for i in numba.parfors.parfor.internal_prange(n):
            if bodo.libs.array_kernels.isna(A, i):
                bodo.libs.array_kernels.setna(bhaf__vbfwb, i)
                continue
            bhaf__vbfwb[i] = op(A[i])
        return bhaf__vbfwb
    return impl


def get_nullable_array_binary_impl(op, lhs, rhs):
    inplace = (op in numba.core.typing.npydecl.
        NumpyRulesInplaceArrayOperator._op_map.keys())
    grr__evr = isinstance(lhs, (types.Number, types.Boolean))
    vcqpz__uqvql = isinstance(rhs, (types.Number, types.Boolean))
    ntyj__cvzmb = types.Array(getattr(lhs, 'dtype', lhs), 1, 'C')
    byk__dft = types.Array(getattr(rhs, 'dtype', rhs), 1, 'C')
    ogyd__otdlq = numba.core.registry.cpu_target.typing_context
    crrte__evil = ogyd__otdlq.resolve_function_type(op, (ntyj__cvzmb,
        byk__dft), {}).return_type
    crrte__evil = to_nullable_type(crrte__evil)
    if op in (operator.truediv, operator.itruediv):
        op = np.true_divide
    elif op in (operator.floordiv, operator.ifloordiv):
        op = np.floor_divide
    cvgoz__ynx = 'lhs' if grr__evr else 'lhs[i]'
    dagr__ypkzw = 'rhs' if vcqpz__uqvql else 'rhs[i]'
    rugc__faf = 'False' if grr__evr else 'bodo.libs.array_kernels.isna(lhs, i)'
    vgx__wwx = ('False' if vcqpz__uqvql else
        'bodo.libs.array_kernels.isna(rhs, i)')
    wzelt__aamuu = 'def impl(lhs, rhs):\n'
    wzelt__aamuu += '  n = len({})\n'.format('lhs' if not grr__evr else 'rhs')
    if inplace:
        wzelt__aamuu += '  out_arr = {}\n'.format('lhs' if not grr__evr else
            'rhs')
    else:
        wzelt__aamuu += (
            '  out_arr = bodo.utils.utils.alloc_type(n, ret_dtype, None)\n')
    wzelt__aamuu += '  for i in numba.parfors.parfor.internal_prange(n):\n'
    wzelt__aamuu += '    if ({}\n'.format(rugc__faf)
    wzelt__aamuu += '        or {}):\n'.format(vgx__wwx)
    wzelt__aamuu += '      bodo.libs.array_kernels.setna(out_arr, i)\n'
    wzelt__aamuu += '      continue\n'
    wzelt__aamuu += (
        '    out_arr[i] = bodo.utils.conversion.unbox_if_timestamp(op({}, {}))\n'
        .format(cvgoz__ynx, dagr__ypkzw))
    wzelt__aamuu += '  return out_arr\n'
    coc__fbr = {}
    exec(wzelt__aamuu, {'bodo': bodo, 'numba': numba, 'np': np, 'ret_dtype':
        crrte__evil, 'op': op}, coc__fbr)
    impl = coc__fbr['impl']
    return impl


def get_int_array_op_pd_td(op):

    def impl(lhs, rhs):
        grr__evr = lhs in [pd_timedelta_type]
        vcqpz__uqvql = rhs in [pd_timedelta_type]
        if grr__evr:

            def impl(lhs, rhs):
                n = len(rhs)
                bhaf__vbfwb = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(bhaf__vbfwb, i)
                        continue
                    bhaf__vbfwb[i] = bodo.utils.conversion.unbox_if_timestamp(
                        op(lhs, rhs[i]))
                return bhaf__vbfwb
            return impl
        elif vcqpz__uqvql:

            def impl(lhs, rhs):
                n = len(lhs)
                bhaf__vbfwb = np.empty(n, 'timedelta64[ns]')
                for i in numba.parfors.parfor.internal_prange(n):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(bhaf__vbfwb, i)
                        continue
                    bhaf__vbfwb[i] = bodo.utils.conversion.unbox_if_timestamp(
                        op(lhs[i], rhs))
                return bhaf__vbfwb
            return impl
    return impl
