"""Array implementation for string objects, which are usually immutable.
The characters are stored in a contingous data array, and an offsets array marks the
the individual strings. For example:
value:             ['a', 'bc', '', 'abc', None, 'bb']
data:              [a, b, c, a, b, c, b, b]
offsets:           [0, 1, 3, 3, 6, 6, 8]
"""
import glob
import operator
import llvmlite.llvmpy.core as lc
import numba
import numba.core.typing.typeof
import numpy as np
import pandas as pd
from numba.core import cgutils, types
from numba.core.imputils import RefType, impl_ret_borrowed, iternext_impl, lower_constant
from numba.core.typing.templates import signature
from numba.core.unsafe.bytes import memcpy_region
from numba.extending import NativeValue, box, intrinsic, lower_builtin, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_jitable, register_model, type_callable, typeof_impl, unbox
import bodo
from bodo.libs.array_item_arr_ext import ArrayItemArrayPayloadType, ArrayItemArrayType, _get_array_item_arr_payload, np_offset_type, offset_type
from bodo.libs.binary_arr_ext import BinaryArrayType, binary_array_type, pre_alloc_binary_array
from bodo.libs.str_ext import memcmp, string_type, unicode_to_utf8_and_len
from bodo.utils.typing import BodoError, is_list_like_index_type, is_overload_constant_int, is_overload_none, is_overload_true, parse_dtype, raise_bodo_error
use_pd_string_array = False
char_type = types.uint8
char_arr_type = types.Array(char_type, 1, 'C')
offset_arr_type = types.Array(offset_type, 1, 'C')
null_bitmap_arr_type = types.Array(types.uint8, 1, 'C')
data_ctypes_type = types.ArrayCTypes(char_arr_type)
offset_ctypes_type = types.ArrayCTypes(offset_arr_type)


class StringArrayType(types.IterableType, types.ArrayCompatible):

    def __init__(self):
        super(StringArrayType, self).__init__(name='StringArrayType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_type

    @property
    def iterator_type(self):
        return StringArrayIterator()

    def copy(self):
        return StringArrayType()


string_array_type = StringArrayType()


@typeof_impl.register(pd.arrays.StringArray)
def typeof_string_array(val, c):
    return string_array_type


@register_model(BinaryArrayType)
@register_model(StringArrayType)
class StringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        uzb__uyjrv = ArrayItemArrayType(char_arr_type)
        qyak__kohd = [('data', uzb__uyjrv)]
        models.StructModel.__init__(self, dmm, fe_type, qyak__kohd)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        qkv__dec, = args
        uaw__ulyx = context.make_helper(builder, string_array_type)
        uaw__ulyx.data = qkv__dec
        context.nrt.incref(builder, data_typ, qkv__dec)
        return uaw__ulyx._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    gcd__poj = c.context.insert_const_string(c.builder.module, 'pandas')
    vcf__dxsud = c.pyapi.import_module_noblock(gcd__poj)
    nbara__qpdjs = c.pyapi.call_method(vcf__dxsud, 'StringDtype', ())
    c.pyapi.decref(vcf__dxsud)
    return nbara__qpdjs


@unbox(StringDtype)
def unbox_string_dtype(typ, val, c):
    return NativeValue(c.context.get_dummy_value())


typeof_impl.register(pd.StringDtype)(lambda a, b: string_dtype)
type_callable(pd.StringDtype)(lambda c: lambda : string_dtype)
lower_builtin(pd.StringDtype)(lambda c, b, s, a: c.get_dummy_value())


def create_binary_op_overload(op):

    def overload_string_array_binary_op(lhs, rhs):
        if lhs == string_array_type and rhs == string_array_type:

            def impl_both(lhs, rhs):
                numba.parfors.parfor.init_prange()
                vdp__chy = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(vdp__chy)
                for i in numba.parfors.parfor.internal_prange(vdp__chy):
                    if bodo.libs.array_kernels.isna(lhs, i
                        ) or bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs[i], rhs[i])
                    out_arr[i] = val
                return out_arr
            return impl_both
        if lhs == string_array_type and types.unliteral(rhs) == string_type:

            def impl_left(lhs, rhs):
                numba.parfors.parfor.init_prange()
                vdp__chy = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(vdp__chy)
                for i in numba.parfors.parfor.internal_prange(vdp__chy):
                    if bodo.libs.array_kernels.isna(lhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs[i], rhs)
                    out_arr[i] = val
                return out_arr
            return impl_left
        if types.unliteral(lhs) == string_type and rhs == string_array_type:

            def impl_right(lhs, rhs):
                numba.parfors.parfor.init_prange()
                vdp__chy = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(vdp__chy)
                for i in numba.parfors.parfor.internal_prange(vdp__chy):
                    if bodo.libs.array_kernels.isna(rhs, i):
                        bodo.libs.array_kernels.setna(out_arr, i)
                        continue
                    val = op(lhs, rhs[i])
                    out_arr[i] = val
                return out_arr
            return impl_right
        raise BodoError(
            f'{op} operator not supported for data types {lhs} and {rhs}.')
    return overload_string_array_binary_op


def overload_add_operator_string_array(lhs, rhs):
    ghzh__qiaq = lhs == string_array_type or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    nnjg__uyyp = rhs == string_array_type or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if (lhs == string_array_type and nnjg__uyyp or ghzh__qiaq and rhs ==
        string_array_type):

        def impl_both(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j
                    ) or bodo.libs.array_kernels.isna(rhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] + rhs[j]
            return out_arr
        return impl_both
    if lhs == string_array_type and types.unliteral(rhs) == string_type:

        def impl_left(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] + rhs
            return out_arr
        return impl_left
    if types.unliteral(lhs) == string_type and rhs == string_array_type:

        def impl_right(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(rhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(rhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs + rhs[j]
            return out_arr
        return impl_right


def overload_mul_operator_str_arr(lhs, rhs):
    if lhs == string_array_type and isinstance(rhs, types.Integer):

        def impl(lhs, rhs):
            numba.parfors.parfor.init_prange()
            l = len(lhs)
            out_arr = bodo.libs.str_arr_ext.pre_alloc_string_array(l, -1)
            for j in numba.parfors.parfor.internal_prange(l):
                if bodo.libs.array_kernels.isna(lhs, j):
                    out_arr[j] = ''
                    bodo.libs.array_kernels.setna(out_arr, j)
                else:
                    out_arr[j] = lhs[j] * rhs
            return out_arr
        return impl
    if isinstance(lhs, types.Integer) and rhs == string_array_type:

        def impl(lhs, rhs):
            return rhs * lhs
        return impl


class StringArrayIterator(types.SimpleIteratorType):

    def __init__(self):
        tfnal__fsyq = 'iter(String)'
        eina__nso = string_type
        super(StringArrayIterator, self).__init__(tfnal__fsyq, eina__nso)


@register_model(StringArrayIterator)
class StrArrayIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qyak__kohd = [('index', types.EphemeralPointer(types.uintp)), (
            'array', string_array_type)]
        super(StrArrayIteratorModel, self).__init__(dmm, fe_type, qyak__kohd)


lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@lower_builtin('iternext', StringArrayIterator)
@iternext_impl(RefType.NEW)
def iternext_str_array(context, builder, sig, args, result):
    [pgok__empkl] = sig.args
    [gbiwx__hob] = args
    azthd__bdnx = context.make_helper(builder, pgok__empkl, value=gbiwx__hob)
    cuj__kbm = signature(types.intp, string_array_type)
    qjd__fcca = context.compile_internal(builder, lambda a: len(a),
        cuj__kbm, [azthd__bdnx.array])
    gowtk__lvkg = builder.load(azthd__bdnx.index)
    iii__eynr = builder.icmp(lc.ICMP_SLT, gowtk__lvkg, qjd__fcca)
    result.set_valid(iii__eynr)
    with builder.if_then(iii__eynr):
        lzasn__tqr = signature(string_type, string_array_type, types.intp)
        value = context.compile_internal(builder, lambda a, i: a[i],
            lzasn__tqr, [azthd__bdnx.array, gowtk__lvkg])
        result.yield_(value)
        rcev__sfce = cgutils.increment_index(builder, gowtk__lvkg)
        builder.store(rcev__sfce, azthd__bdnx.index)


def _get_str_binary_arr_payload(context, builder, arr_value, arr_typ):
    assert arr_typ == string_array_type or arr_typ == binary_array_type
    pyuko__bqbrn = context.make_helper(builder, arr_typ, arr_value)
    uzb__uyjrv = ArrayItemArrayType(char_arr_type)
    rfxot__gnsxf = _get_array_item_arr_payload(context, builder, uzb__uyjrv,
        pyuko__bqbrn.data)
    return rfxot__gnsxf


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        rfxot__gnsxf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return rfxot__gnsxf.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        rfxot__gnsxf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        ihb__rcm = context.make_helper(builder, offset_arr_type,
            rfxot__gnsxf.offsets).data
        return _get_num_total_chars(builder, ihb__rcm, rfxot__gnsxf.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        rfxot__gnsxf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        xto__githt = context.make_helper(builder, offset_arr_type,
            rfxot__gnsxf.offsets)
        hhey__jfzjy = context.make_helper(builder, offset_ctypes_type)
        hhey__jfzjy.data = builder.bitcast(xto__githt.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        hhey__jfzjy.meminfo = xto__githt.meminfo
        nbara__qpdjs = hhey__jfzjy._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type,
            nbara__qpdjs)
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        rfxot__gnsxf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        qkv__dec = context.make_helper(builder, char_arr_type, rfxot__gnsxf
            .data)
        hhey__jfzjy = context.make_helper(builder, data_ctypes_type)
        hhey__jfzjy.data = qkv__dec.data
        hhey__jfzjy.meminfo = qkv__dec.meminfo
        nbara__qpdjs = hhey__jfzjy._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            nbara__qpdjs)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        std__excm, ind = args
        rfxot__gnsxf = _get_str_binary_arr_payload(context, builder,
            std__excm, sig.args[0])
        qkv__dec = context.make_helper(builder, char_arr_type, rfxot__gnsxf
            .data)
        hhey__jfzjy = context.make_helper(builder, data_ctypes_type)
        hhey__jfzjy.data = builder.gep(qkv__dec.data, [ind])
        hhey__jfzjy.meminfo = qkv__dec.meminfo
        nbara__qpdjs = hhey__jfzjy._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            nbara__qpdjs)
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        urxl__pkibn, saipj__ujxli, fdn__cne, jcd__tndie = args
        zkiox__gozj = builder.bitcast(builder.gep(urxl__pkibn, [
            saipj__ujxli]), lir.IntType(8).as_pointer())
        lhhct__yxonf = builder.bitcast(builder.gep(fdn__cne, [jcd__tndie]),
            lir.IntType(8).as_pointer())
        aag__czsvi = builder.load(lhhct__yxonf)
        builder.store(aag__czsvi, zkiox__gozj)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        rfxot__gnsxf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        alkg__pimz = context.make_helper(builder, null_bitmap_arr_type,
            rfxot__gnsxf.null_bitmap)
        hhey__jfzjy = context.make_helper(builder, data_ctypes_type)
        hhey__jfzjy.data = alkg__pimz.data
        hhey__jfzjy.meminfo = alkg__pimz.meminfo
        nbara__qpdjs = hhey__jfzjy._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type,
            nbara__qpdjs)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        rfxot__gnsxf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        ihb__rcm = context.make_helper(builder, offset_arr_type,
            rfxot__gnsxf.offsets).data
        return builder.load(builder.gep(ihb__rcm, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        rfxot__gnsxf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type,
            rfxot__gnsxf.offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        zrvkq__oci, ind = args
        if in_bitmap_typ == data_ctypes_type:
            hhey__jfzjy = context.make_helper(builder, data_ctypes_type,
                zrvkq__oci)
            zrvkq__oci = hhey__jfzjy.data
        return builder.load(builder.gep(zrvkq__oci, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        zrvkq__oci, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            hhey__jfzjy = context.make_helper(builder, data_ctypes_type,
                zrvkq__oci)
            zrvkq__oci = hhey__jfzjy.data
        builder.store(val, builder.gep(zrvkq__oci, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        bhevp__fdtlx = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        pdki__omaf = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        wcfjv__qbhu = context.make_helper(builder, offset_arr_type,
            bhevp__fdtlx.offsets).data
        mcnc__yjzp = context.make_helper(builder, offset_arr_type,
            pdki__omaf.offsets).data
        rfv__zwlpc = context.make_helper(builder, char_arr_type,
            bhevp__fdtlx.data).data
        rtsy__htit = context.make_helper(builder, char_arr_type, pdki__omaf
            .data).data
        zcl__njhxw = context.make_helper(builder, null_bitmap_arr_type,
            bhevp__fdtlx.null_bitmap).data
        mbb__dld = context.make_helper(builder, null_bitmap_arr_type,
            pdki__omaf.null_bitmap).data
        mnsr__jemgm = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, mcnc__yjzp, wcfjv__qbhu, mnsr__jemgm)
        cgutils.memcpy(builder, rtsy__htit, rfv__zwlpc, builder.load(
            builder.gep(wcfjv__qbhu, [ind])))
        nvi__qjyr = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        ibzw__qgyps = builder.lshr(nvi__qjyr, lir.Constant(lir.IntType(64), 3))
        cgutils.memcpy(builder, mbb__dld, zcl__njhxw, ibzw__qgyps)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        bhevp__fdtlx = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        pdki__omaf = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        wcfjv__qbhu = context.make_helper(builder, offset_arr_type,
            bhevp__fdtlx.offsets).data
        rfv__zwlpc = context.make_helper(builder, char_arr_type,
            bhevp__fdtlx.data).data
        rtsy__htit = context.make_helper(builder, char_arr_type, pdki__omaf
            .data).data
        num_total_chars = _get_num_total_chars(builder, wcfjv__qbhu,
            bhevp__fdtlx.n_arrays)
        cgutils.memcpy(builder, rtsy__htit, rfv__zwlpc, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        bhevp__fdtlx = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        pdki__omaf = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        wcfjv__qbhu = context.make_helper(builder, offset_arr_type,
            bhevp__fdtlx.offsets).data
        mcnc__yjzp = context.make_helper(builder, offset_arr_type,
            pdki__omaf.offsets).data
        zcl__njhxw = context.make_helper(builder, null_bitmap_arr_type,
            bhevp__fdtlx.null_bitmap).data
        vdp__chy = bhevp__fdtlx.n_arrays
        bazp__cfgb = context.get_constant(offset_type, 0)
        yqb__bxw = cgutils.alloca_once_value(builder, bazp__cfgb)
        with cgutils.for_range(builder, vdp__chy) as loop:
            jzsq__zsivo = lower_is_na(context, builder, zcl__njhxw, loop.index)
            with cgutils.if_likely(builder, builder.not_(jzsq__zsivo)):
                bzr__rbcp = builder.load(builder.gep(wcfjv__qbhu, [loop.index])
                    )
                cakzg__tea = builder.load(yqb__bxw)
                builder.store(bzr__rbcp, builder.gep(mcnc__yjzp, [cakzg__tea]))
                builder.store(builder.add(cakzg__tea, lir.Constant(context.
                    get_value_type(offset_type), 1)), yqb__bxw)
        cakzg__tea = builder.load(yqb__bxw)
        bzr__rbcp = builder.load(builder.gep(wcfjv__qbhu, [vdp__chy]))
        builder.store(bzr__rbcp, builder.gep(mcnc__yjzp, [cakzg__tea]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        fpkid__opn, ind, str, uzd__jgq = args
        fpkid__opn = context.make_array(sig.args[0])(context, builder,
            fpkid__opn)
        bacj__meez = builder.gep(fpkid__opn.data, [ind])
        cgutils.raw_memcpy(builder, bacj__meez, str, uzd__jgq, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        bacj__meez, ind, btlc__byad, uzd__jgq = args
        bacj__meez = builder.gep(bacj__meez, [ind])
        cgutils.raw_memcpy(builder, bacj__meez, btlc__byad, uzd__jgq, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_length(A, i):
    return np.int64(getitem_str_offset(A, i + 1) - getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_str_length(A, i):
    rawsx__bsmpi = np.int64(getitem_str_offset(A, i))
    wla__prqzb = np.int64(getitem_str_offset(A, i + 1))
    l = wla__prqzb - rawsx__bsmpi
    jsrov__uay = get_data_ptr_ind(A, rawsx__bsmpi)
    for j in range(l):
        if bodo.hiframes.split_impl.getitem_c_arr(jsrov__uay, j) >= 128:
            return len(A[i])
    return l


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_ptr(A, i):
    return get_data_ptr_ind(A, getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_copy(B, j, A, i):
    if j == 0:
        setitem_str_offset(B, 0, 0)
    duei__arepd = getitem_str_offset(A, i)
    cuvck__scfeq = getitem_str_offset(A, i + 1)
    cehdh__bxqvt = cuvck__scfeq - duei__arepd
    gsl__pmp = getitem_str_offset(B, j)
    glviw__dpre = gsl__pmp + cehdh__bxqvt
    setitem_str_offset(B, j + 1, glviw__dpre)
    if str_arr_is_na(A, i):
        str_arr_set_na(B, j)
    else:
        str_arr_set_not_na(B, j)
    if cehdh__bxqvt != 0:
        qkv__dec = B._data
        bodo.libs.array_item_arr_ext.ensure_data_capacity(qkv__dec, np.
            int64(gsl__pmp), np.int64(glviw__dpre))
        rxn__ctedj = get_data_ptr(B).data
        qey__oonp = get_data_ptr(A).data
        memcpy_region(rxn__ctedj, gsl__pmp, qey__oonp, duei__arepd,
            cehdh__bxqvt, 1)


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    vdp__chy = len(str_arr)
    qsyeo__jzhh = np.empty(vdp__chy, np.bool_)
    for i in range(vdp__chy):
        qsyeo__jzhh[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return qsyeo__jzhh


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if data in [string_array_type, binary_array_type]:

        def to_list_impl(data, str_null_bools=None):
            vdp__chy = len(data)
            l = []
            for i in range(vdp__chy):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        wkx__tbbn = data.count
        kslz__ahn = ['to_list_if_immutable_arr(data[{}])'.format(i) for i in
            range(wkx__tbbn)]
        if is_overload_true(str_null_bools):
            kslz__ahn += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(wkx__tbbn) if data.types[i] in [string_array_type,
                binary_array_type]]
        ltnzk__zpx = 'def f(data, str_null_bools=None):\n'
        ltnzk__zpx += '  return ({}{})\n'.format(', '.join(kslz__ahn), ',' if
            wkx__tbbn == 1 else '')
        bdqb__hnqqm = {}
        exec(ltnzk__zpx, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, bdqb__hnqqm)
        nuyp__tydfw = bdqb__hnqqm['f']
        return nuyp__tydfw
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                vdp__chy = len(list_data)
                for i in range(vdp__chy):
                    btlc__byad = list_data[i]
                    str_arr[i] = btlc__byad
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                vdp__chy = len(list_data)
                for i in range(vdp__chy):
                    btlc__byad = list_data[i]
                    str_arr[i] = btlc__byad
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        wkx__tbbn = str_arr.count
        syb__lvgp = 0
        ltnzk__zpx = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(wkx__tbbn):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                ltnzk__zpx += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])\n'
                    .format(i, i, wkx__tbbn + syb__lvgp))
                syb__lvgp += 1
            else:
                ltnzk__zpx += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        ltnzk__zpx += '  return\n'
        bdqb__hnqqm = {}
        exec(ltnzk__zpx, {'cp_str_list_to_array': cp_str_list_to_array},
            bdqb__hnqqm)
        mdfe__ctnb = bdqb__hnqqm['f']
        return mdfe__ctnb
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            vdp__chy = len(str_list)
            str_arr = pre_alloc_string_array(vdp__chy, -1)
            for i in range(vdp__chy):
                btlc__byad = str_list[i]
                str_arr[i] = btlc__byad
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            vdp__chy = len(A)
            oco__stg = 0
            for i in range(vdp__chy):
                btlc__byad = A[i]
                oco__stg += get_utf8_size(btlc__byad)
            return oco__stg
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        vdp__chy = len(arr)
        n_chars = num_total_chars(arr)
        uthuc__tyd = pre_alloc_string_array(vdp__chy, np.int64(n_chars))
        copy_str_arr_slice(uthuc__tyd, arr, vdp__chy)
        return uthuc__tyd
    return copy_impl


@overload(len, no_unliteral=True)
def str_arr_len_overload(str_arr):
    if str_arr == string_array_type:

        def str_arr_len(str_arr):
            return str_arr.size
        return str_arr_len


@overload_attribute(StringArrayType, 'size')
def str_arr_size_overload(str_arr):
    return lambda str_arr: len(str_arr._data)


@overload_attribute(StringArrayType, 'shape')
def str_arr_shape_overload(str_arr):
    return lambda str_arr: (str_arr.size,)


@overload_attribute(StringArrayType, 'nbytes')
def str_arr_nbytes_overload(str_arr):
    return lambda str_arr: str_arr._data.nbytes


@overload_method(types.Array, 'tolist', no_unliteral=True)
@overload_method(StringArrayType, 'tolist', no_unliteral=True)
def overload_to_list(arr):
    return lambda arr: list(arr)


import llvmlite.binding as ll
from llvmlite import ir as lir
from bodo.libs import array_ext, hstr_ext
ll.add_symbol('get_str_len', hstr_ext.get_str_len)
ll.add_symbol('setitem_string_array', hstr_ext.setitem_string_array)
ll.add_symbol('is_na', hstr_ext.is_na)
ll.add_symbol('string_array_from_sequence', array_ext.
    string_array_from_sequence)
ll.add_symbol('pd_array_from_string_array', hstr_ext.pd_array_from_string_array
    )
ll.add_symbol('np_array_from_string_array', hstr_ext.np_array_from_string_array
    )
ll.add_symbol('convert_len_arr_to_offset32', hstr_ext.
    convert_len_arr_to_offset32)
ll.add_symbol('convert_len_arr_to_offset', hstr_ext.convert_len_arr_to_offset)
ll.add_symbol('set_string_array_range', hstr_ext.set_string_array_range)
ll.add_symbol('str_arr_to_int64', hstr_ext.str_arr_to_int64)
ll.add_symbol('str_arr_to_float64', hstr_ext.str_arr_to_float64)
ll.add_symbol('get_utf8_size', hstr_ext.get_utf8_size)
ll.add_symbol('print_str_arr', hstr_ext.print_str_arr)
ll.add_symbol('inplace_int64_to_str', hstr_ext.inplace_int64_to_str)
inplace_int64_to_str = types.ExternalFunction('inplace_int64_to_str', types
    .void(types.voidptr, types.int64, types.int64))
convert_len_arr_to_offset32 = types.ExternalFunction(
    'convert_len_arr_to_offset32', types.void(types.voidptr, types.intp))
convert_len_arr_to_offset = types.ExternalFunction('convert_len_arr_to_offset',
    types.void(types.voidptr, types.voidptr, types.intp))
setitem_string_array = types.ExternalFunction('setitem_string_array', types
    .void(types.CPointer(offset_type), types.CPointer(char_type), types.
    uint64, types.voidptr, types.intp, offset_type, offset_type, types.intp))
_get_utf8_size = types.ExternalFunction('get_utf8_size', types.intp(types.
    voidptr, types.intp, offset_type))
_print_str_arr = types.ExternalFunction('print_str_arr', types.void(types.
    uint64, types.uint64, types.CPointer(offset_type), types.CPointer(
    char_type)))


@numba.generated_jit(nopython=True)
def empty_str_arr(in_seq):
    ltnzk__zpx = 'def f(in_seq):\n'
    ltnzk__zpx += '    n_strs = len(in_seq)\n'
    ltnzk__zpx += '    A = pre_alloc_string_array(n_strs, -1)\n'
    ltnzk__zpx += '    return A\n'
    bdqb__hnqqm = {}
    exec(ltnzk__zpx, {'pre_alloc_string_array': pre_alloc_string_array},
        bdqb__hnqqm)
    fkfj__gglo = bdqb__hnqqm['f']
    return fkfj__gglo


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    if in_seq.dtype == bodo.bytes_type:
        xxq__ckf = 'pre_alloc_binary_array'
    else:
        xxq__ckf = 'pre_alloc_string_array'
    ltnzk__zpx = 'def f(in_seq):\n'
    ltnzk__zpx += '    n_strs = len(in_seq)\n'
    ltnzk__zpx += f'    A = {xxq__ckf}(n_strs, -1)\n'
    ltnzk__zpx += '    for i in range(n_strs):\n'
    ltnzk__zpx += '        A[i] = in_seq[i]\n'
    ltnzk__zpx += '    return A\n'
    bdqb__hnqqm = {}
    exec(ltnzk__zpx, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, bdqb__hnqqm)
    fkfj__gglo = bdqb__hnqqm['f']
    return fkfj__gglo


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        rfxot__gnsxf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        niyz__ujaid = builder.add(rfxot__gnsxf.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        lsfbq__zjirk = builder.lshr(lir.Constant(lir.IntType(64),
            offset_type.bitwidth), lir.Constant(lir.IntType(64), 3))
        ibzw__qgyps = builder.mul(niyz__ujaid, lsfbq__zjirk)
        ebgta__azhje = context.make_array(offset_arr_type)(context, builder,
            rfxot__gnsxf.offsets).data
        cgutils.memset(builder, ebgta__azhje, ibzw__qgyps, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        rfxot__gnsxf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        fhtn__btxa = rfxot__gnsxf.n_arrays
        ibzw__qgyps = builder.lshr(builder.add(fhtn__btxa, lir.Constant(lir
            .IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        nfp__vjfmv = context.make_array(null_bitmap_arr_type)(context,
            builder, rfxot__gnsxf.null_bitmap).data
        cgutils.memset(builder, nfp__vjfmv, ibzw__qgyps, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@numba.njit
def pre_alloc_string_array(n_strs, n_chars):
    if n_chars is None:
        n_chars = -1
    str_arr = init_str_arr(bodo.libs.array_item_arr_ext.
        pre_alloc_array_item_array(np.int64(n_strs), (np.int64(n_chars),),
        char_arr_type))
    if n_chars == 0:
        set_all_offsets_to_0(str_arr)
    return str_arr


@register_jitable
def gen_na_str_array_lens(n_strs, total_len, len_arr):
    str_arr = pre_alloc_string_array(n_strs, total_len)
    set_bitmap_all_NA(str_arr)
    offsets = bodo.libs.array_item_arr_ext.get_offsets(str_arr._data)
    urvem__hus = 0
    xuc__hlouy = len(len_arr)
    for i in range(xuc__hlouy):
        offsets[i] = urvem__hus
        urvem__hus += len_arr[i]
    offsets[xuc__hlouy] = urvem__hus
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    fysp__zivsk = i // 8
    kncv__dbrqe = getitem_str_bitmap(bits, fysp__zivsk)
    kncv__dbrqe ^= np.uint8(-np.uint8(bit_is_set) ^ kncv__dbrqe) & kBitmask[
        i % 8]
    setitem_str_bitmap(bits, fysp__zivsk, kncv__dbrqe)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    glso__cam = get_null_bitmap_ptr(out_str_arr)
    ynrq__dzmy = get_null_bitmap_ptr(in_str_arr)
    for j in range(len(in_str_arr)):
        xxq__onqd = get_bit_bitmap(ynrq__dzmy, j)
        set_bit_to(glso__cam, out_start + j, xxq__onqd)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type, 'set_string_array_range requires string or binary arrays'
    assert isinstance(curr_str_typ, types.Integer) and isinstance(
        curr_chars_typ, types.Integer
        ), 'set_string_array_range requires integer indices'

    def codegen(context, builder, sig, args):
        out_arr, std__excm, tptzn__cpfuk, fyuae__jtxrj = args
        bhevp__fdtlx = _get_str_binary_arr_payload(context, builder,
            std__excm, string_array_type)
        pdki__omaf = _get_str_binary_arr_payload(context, builder, out_arr,
            string_array_type)
        wcfjv__qbhu = context.make_helper(builder, offset_arr_type,
            bhevp__fdtlx.offsets).data
        mcnc__yjzp = context.make_helper(builder, offset_arr_type,
            pdki__omaf.offsets).data
        rfv__zwlpc = context.make_helper(builder, char_arr_type,
            bhevp__fdtlx.data).data
        rtsy__htit = context.make_helper(builder, char_arr_type, pdki__omaf
            .data).data
        num_total_chars = _get_num_total_chars(builder, wcfjv__qbhu,
            bhevp__fdtlx.n_arrays)
        nrfw__gkia = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        mgyhf__wzl = cgutils.get_or_insert_function(builder.module,
            nrfw__gkia, name='set_string_array_range')
        builder.call(mgyhf__wzl, [mcnc__yjzp, rtsy__htit, wcfjv__qbhu,
            rfv__zwlpc, tptzn__cpfuk, fyuae__jtxrj, bhevp__fdtlx.n_arrays,
            num_total_chars])
        jgqs__jyh = context.typing_context.resolve_value_type(copy_nulls_range)
        wpmeq__igjr = jgqs__jyh.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        tumyb__qjp = context.get_function(jgqs__jyh, wpmeq__igjr)
        tumyb__qjp(builder, (out_arr, std__excm, tptzn__cpfuk))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    yhtk__uacx = c.context.make_helper(c.builder, typ, val)
    uzb__uyjrv = ArrayItemArrayType(char_arr_type)
    rfxot__gnsxf = _get_array_item_arr_payload(c.context, c.builder,
        uzb__uyjrv, yhtk__uacx.data)
    druqa__bhwp = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    hyxv__fjdoe = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        hyxv__fjdoe = 'pd_array_from_string_array'
    nrfw__gkia = lir.FunctionType(c.context.get_argument_type(types.
        pyobject), [lir.IntType(64), lir.IntType(offset_type.bitwidth).
        as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
        as_pointer(), lir.IntType(32)])
    zii__tox = cgutils.get_or_insert_function(c.builder.module, nrfw__gkia,
        name=hyxv__fjdoe)
    ihb__rcm = c.context.make_array(offset_arr_type)(c.context, c.builder,
        rfxot__gnsxf.offsets).data
    jsrov__uay = c.context.make_array(char_arr_type)(c.context, c.builder,
        rfxot__gnsxf.data).data
    nfp__vjfmv = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, rfxot__gnsxf.null_bitmap).data
    arr = c.builder.call(zii__tox, [rfxot__gnsxf.n_arrays, ihb__rcm,
        jsrov__uay, nfp__vjfmv, druqa__bhwp])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        rfxot__gnsxf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        nfp__vjfmv = context.make_array(null_bitmap_arr_type)(context,
            builder, rfxot__gnsxf.null_bitmap).data
        pogts__hvhd = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        rkl__ksk = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        kncv__dbrqe = builder.load(builder.gep(nfp__vjfmv, [pogts__hvhd],
            inbounds=True))
        sqfa__lcuj = lir.ArrayType(lir.IntType(8), 8)
        jthp__qysck = cgutils.alloca_once_value(builder, lir.Constant(
            sqfa__lcuj, (1, 2, 4, 8, 16, 32, 64, 128)))
        ievz__cmlz = builder.load(builder.gep(jthp__qysck, [lir.Constant(
            lir.IntType(64), 0), rkl__ksk], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(kncv__dbrqe,
            ievz__cmlz), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        rfxot__gnsxf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        pogts__hvhd = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        rkl__ksk = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        nfp__vjfmv = context.make_array(null_bitmap_arr_type)(context,
            builder, rfxot__gnsxf.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type,
            rfxot__gnsxf.offsets).data
        pdp__vns = builder.gep(nfp__vjfmv, [pogts__hvhd], inbounds=True)
        kncv__dbrqe = builder.load(pdp__vns)
        sqfa__lcuj = lir.ArrayType(lir.IntType(8), 8)
        jthp__qysck = cgutils.alloca_once_value(builder, lir.Constant(
            sqfa__lcuj, (1, 2, 4, 8, 16, 32, 64, 128)))
        ievz__cmlz = builder.load(builder.gep(jthp__qysck, [lir.Constant(
            lir.IntType(64), 0), rkl__ksk], inbounds=True))
        ievz__cmlz = builder.xor(ievz__cmlz, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(kncv__dbrqe, ievz__cmlz), pdp__vns)
        if str_arr_typ == string_array_type:
            padkh__tvur = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            dpwz__orw = builder.icmp_unsigned('!=', padkh__tvur,
                rfxot__gnsxf.n_arrays)
            with builder.if_then(dpwz__orw):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [padkh__tvur]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        rfxot__gnsxf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        pogts__hvhd = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        rkl__ksk = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        nfp__vjfmv = context.make_array(null_bitmap_arr_type)(context,
            builder, rfxot__gnsxf.null_bitmap).data
        pdp__vns = builder.gep(nfp__vjfmv, [pogts__hvhd], inbounds=True)
        kncv__dbrqe = builder.load(pdp__vns)
        sqfa__lcuj = lir.ArrayType(lir.IntType(8), 8)
        jthp__qysck = cgutils.alloca_once_value(builder, lir.Constant(
            sqfa__lcuj, (1, 2, 4, 8, 16, 32, 64, 128)))
        ievz__cmlz = builder.load(builder.gep(jthp__qysck, [lir.Constant(
            lir.IntType(64), 0), rkl__ksk], inbounds=True))
        builder.store(builder.or_(kncv__dbrqe, ievz__cmlz), pdp__vns)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        rfxot__gnsxf = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        ibzw__qgyps = builder.udiv(builder.add(rfxot__gnsxf.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        nfp__vjfmv = context.make_array(null_bitmap_arr_type)(context,
            builder, rfxot__gnsxf.null_bitmap).data
        cgutils.memset(builder, nfp__vjfmv, ibzw__qgyps, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    ccwi__ghktb = context.make_helper(builder, string_array_type, str_arr)
    uzb__uyjrv = ArrayItemArrayType(char_arr_type)
    efct__lqr = context.make_helper(builder, uzb__uyjrv, ccwi__ghktb.data)
    xwygw__mrde = ArrayItemArrayPayloadType(uzb__uyjrv)
    phlut__cynue = context.nrt.meminfo_data(builder, efct__lqr.meminfo)
    onq__knrp = builder.bitcast(phlut__cynue, context.get_value_type(
        xwygw__mrde).as_pointer())
    return onq__knrp


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        aszs__cxaiq, fdwhv__zip = args
        cqig__swfew = _get_str_binary_arr_data_payload_ptr(context, builder,
            fdwhv__zip)
        megn__xqa = _get_str_binary_arr_data_payload_ptr(context, builder,
            aszs__cxaiq)
        mwljk__bwwr = _get_str_binary_arr_payload(context, builder,
            fdwhv__zip, sig.args[1])
        ktgjv__qfp = _get_str_binary_arr_payload(context, builder,
            aszs__cxaiq, sig.args[0])
        context.nrt.incref(builder, char_arr_type, mwljk__bwwr.data)
        context.nrt.incref(builder, offset_arr_type, mwljk__bwwr.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, mwljk__bwwr.
            null_bitmap)
        context.nrt.decref(builder, char_arr_type, ktgjv__qfp.data)
        context.nrt.decref(builder, offset_arr_type, ktgjv__qfp.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, ktgjv__qfp.
            null_bitmap)
        builder.store(builder.load(cqig__swfew), megn__xqa)
        return context.get_dummy_value()
    return types.none(to_arr_typ, from_arr_typ), codegen


dummy_use = numba.njit(lambda a: None)


@numba.generated_jit(nopython=True, no_cpython_wrapper=True)
def get_utf8_size(s):
    if isinstance(s, types.StringLiteral):
        l = len(s.literal_value.encode())
        return lambda s: l

    def impl(s):
        if s is None:
            return 0
        s = bodo.utils.indexing.unoptional(s)
        if s._is_ascii == 1:
            return len(s)
        vdp__chy = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return vdp__chy
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, bacj__meez, gktns__ojlir = args
        rfxot__gnsxf = _get_str_binary_arr_payload(context, builder, arr,
            sig.args[0])
        offsets = context.make_helper(builder, offset_arr_type,
            rfxot__gnsxf.offsets).data
        data = context.make_helper(builder, char_arr_type, rfxot__gnsxf.data
            ).data
        nrfw__gkia = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        oty__jbhny = cgutils.get_or_insert_function(builder.module,
            nrfw__gkia, name='setitem_string_array')
        wkter__rqqzy = context.get_constant(types.int32, -1)
        jilw__gow = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets,
            rfxot__gnsxf.n_arrays)
        builder.call(oty__jbhny, [offsets, data, num_total_chars, builder.
            extract_value(bacj__meez, 0), gktns__ojlir, wkter__rqqzy,
            jilw__gow, ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    nrfw__gkia = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64)])
    gmqbf__jpoaa = cgutils.get_or_insert_function(builder.module,
        nrfw__gkia, name='is_na')
    return builder.call(gmqbf__jpoaa, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        zkiox__gozj, lhhct__yxonf, wkx__tbbn, prat__hafu = args
        cgutils.raw_memcpy(builder, zkiox__gozj, lhhct__yxonf, wkx__tbbn,
            prat__hafu)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.voidptr, types.intp, types.intp
        ), codegen


@numba.njit
def print_str_arr(arr):
    _print_str_arr(num_strings(arr), num_total_chars(arr), get_offset_ptr(
        arr), get_data_ptr(arr))


def inplace_eq(A, i, val):
    return A[i] == val


@overload(inplace_eq)
def inplace_eq_overload(A, ind, val):

    def impl(A, ind, val):
        gok__qbec, ckkf__afdf = unicode_to_utf8_and_len(val)
        ndw__uwen = getitem_str_offset(A, ind)
        kcr__mig = getitem_str_offset(A, ind + 1)
        ckt__uyq = kcr__mig - ndw__uwen
        if ckt__uyq != ckkf__afdf:
            return False
        bacj__meez = get_data_ptr_ind(A, ndw__uwen)
        return memcmp(bacj__meez, gok__qbec, ckkf__afdf) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        ndw__uwen = getitem_str_offset(A, ind)
        ckt__uyq = bodo.libs.str_ext.int_to_str_len(val)
        qkno__qjo = ndw__uwen + ckt__uyq
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            ndw__uwen, qkno__qjo)
        bacj__meez = get_data_ptr_ind(A, ndw__uwen)
        inplace_int64_to_str(bacj__meez, ckt__uyq, val)
        setitem_str_offset(A, ind + 1, ndw__uwen + ckt__uyq)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        bacj__meez, = args
        siy__zxc = context.insert_const_string(builder.module, '<NA>')
        ygmph__pnbf = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, bacj__meez, siy__zxc, ygmph__pnbf, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    xetuj__tcjnr = len('<NA>')

    def impl(A, ind):
        ndw__uwen = getitem_str_offset(A, ind)
        qkno__qjo = ndw__uwen + xetuj__tcjnr
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            ndw__uwen, qkno__qjo)
        bacj__meez = get_data_ptr_ind(A, ndw__uwen)
        inplace_set_NA_str(bacj__meez)
        setitem_str_offset(A, ind + 1, ndw__uwen + xetuj__tcjnr)
        str_arr_set_not_na(A, ind)
    return impl


@overload(operator.getitem, no_unliteral=True)
def str_arr_getitem_int(A, ind):
    if A != string_array_type:
        return
    if isinstance(ind, types.Integer):

        def str_arr_getitem_impl(A, ind):
            if ind < 0:
                ind += A.size
            ndw__uwen = getitem_str_offset(A, ind)
            kcr__mig = getitem_str_offset(A, ind + 1)
            gktns__ojlir = kcr__mig - ndw__uwen
            bacj__meez = get_data_ptr_ind(A, ndw__uwen)
            dxtb__gse = decode_utf8(bacj__meez, gktns__ojlir)
            return dxtb__gse
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            vdp__chy = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(vdp__chy):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            rxn__ctedj = get_data_ptr(out_arr).data
            qey__oonp = get_data_ptr(A).data
            syb__lvgp = 0
            cakzg__tea = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(vdp__chy):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    pape__gykao = get_str_arr_item_length(A, i)
                    if pape__gykao == 1:
                        copy_single_char(rxn__ctedj, cakzg__tea, qey__oonp,
                            getitem_str_offset(A, i))
                    else:
                        memcpy_region(rxn__ctedj, cakzg__tea, qey__oonp,
                            getitem_str_offset(A, i), pape__gykao, 1)
                    cakzg__tea += pape__gykao
                    setitem_str_offset(out_arr, syb__lvgp + 1, cakzg__tea)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, syb__lvgp)
                    else:
                        str_arr_set_not_na(out_arr, syb__lvgp)
                    syb__lvgp += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            vdp__chy = len(ind)
            out_arr = pre_alloc_string_array(vdp__chy, -1)
            syb__lvgp = 0
            for i in range(vdp__chy):
                btlc__byad = A[ind[i]]
                out_arr[syb__lvgp] = btlc__byad
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, syb__lvgp)
                syb__lvgp += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            vdp__chy = len(A)
            fzomk__raltm = numba.cpython.unicode._normalize_slice(ind, vdp__chy
                )
            odug__zytg = numba.cpython.unicode._slice_span(fzomk__raltm)
            if fzomk__raltm.step == 1:
                ndw__uwen = getitem_str_offset(A, fzomk__raltm.start)
                kcr__mig = getitem_str_offset(A, fzomk__raltm.stop)
                n_chars = kcr__mig - ndw__uwen
                uthuc__tyd = pre_alloc_string_array(odug__zytg, np.int64(
                    n_chars))
                for i in range(odug__zytg):
                    uthuc__tyd[i] = A[fzomk__raltm.start + i]
                    if str_arr_is_na(A, fzomk__raltm.start + i):
                        str_arr_set_na(uthuc__tyd, i)
                return uthuc__tyd
            else:
                uthuc__tyd = pre_alloc_string_array(odug__zytg, -1)
                for i in range(odug__zytg):
                    uthuc__tyd[i] = A[fzomk__raltm.start + i * fzomk__raltm
                        .step]
                    if str_arr_is_na(A, fzomk__raltm.start + i *
                        fzomk__raltm.step):
                        str_arr_set_na(uthuc__tyd, i)
                return uthuc__tyd
        return str_arr_slice_impl
    raise BodoError(
        f'getitem for StringArray with indexing type {ind} not supported.')


dummy_use = numba.njit(lambda a: None)


@overload(operator.setitem)
def str_arr_setitem(A, idx, val):
    if A != string_array_type:
        return
    if val == types.none or isinstance(val, types.optional):
        return
    egq__jyjnh = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(egq__jyjnh)
        oomt__ydjd = 4

        def impl_scalar(A, idx, val):
            zbqn__xrn = (val._length if val._is_ascii else oomt__ydjd * val
                ._length)
            qkv__dec = A._data
            ndw__uwen = np.int64(getitem_str_offset(A, idx))
            qkno__qjo = ndw__uwen + zbqn__xrn
            bodo.libs.array_item_arr_ext.ensure_data_capacity(qkv__dec,
                ndw__uwen, qkno__qjo)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                qkno__qjo, val._data, val._length, val._kind, val._is_ascii,
                idx)
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                fzomk__raltm = numba.cpython.unicode._normalize_slice(idx,
                    len(A))
                rawsx__bsmpi = fzomk__raltm.start
                qkv__dec = A._data
                ndw__uwen = np.int64(getitem_str_offset(A, rawsx__bsmpi))
                qkno__qjo = ndw__uwen + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(qkv__dec,
                    ndw__uwen, qkno__qjo)
                set_string_array_range(A, val, rawsx__bsmpi, ndw__uwen)
                mbai__lzic = 0
                for i in range(fzomk__raltm.start, fzomk__raltm.stop,
                    fzomk__raltm.step):
                    if str_arr_is_na(val, mbai__lzic):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    mbai__lzic += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                poiji__ipqr = str_list_to_array(val)
                A[idx] = poiji__ipqr
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                fzomk__raltm = numba.cpython.unicode._normalize_slice(idx,
                    len(A))
                for i in range(fzomk__raltm.start, fzomk__raltm.stop,
                    fzomk__raltm.step):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(egq__jyjnh)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                vdp__chy = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(vdp__chy, -1)
                for i in numba.parfors.parfor.internal_prange(vdp__chy):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        out_arr[i] = val
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_scalar
        elif val == string_array_type or isinstance(val, types.Array
            ) and isinstance(val.dtype, types.UnicodeCharSeq):

            def impl_bool_arr(A, idx, val):
                vdp__chy = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(vdp__chy, -1)
                hcftu__wzkih = 0
                for i in numba.parfors.parfor.internal_prange(vdp__chy):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, hcftu__wzkih):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, hcftu__wzkih)
                        else:
                            out_arr[i] = str(val[hcftu__wzkih])
                        hcftu__wzkih += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(egq__jyjnh)
    raise BodoError(egq__jyjnh)


@overload_attribute(StringArrayType, 'dtype')
def overload_str_arr_dtype(A):
    return lambda A: pd.StringDtype()


@overload_attribute(StringArrayType, 'ndim')
def overload_str_arr_ndim(A):
    return lambda A: 1


@overload_method(StringArrayType, 'astype', no_unliteral=True)
def overload_str_arr_astype(A, dtype, copy=True):
    if dtype == types.unicode_type:
        raise_bodo_error(
            "StringArray.astype(): 'dtype' when passed as string must be a constant value"
            )
    if isinstance(dtype, types.Function) and dtype.key[0] == str:
        return lambda A, dtype, copy=True: A
    chvww__ntj = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(chvww__ntj, (types.Float, types.Integer)):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(chvww__ntj, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            vdp__chy = len(A)
            B = np.empty(vdp__chy, chvww__ntj)
            for i in numba.parfors.parfor.internal_prange(vdp__chy):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = np.nan
                else:
                    B[i] = float(A[i])
            return B
        return impl_float
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            vdp__chy = len(A)
            B = np.empty(vdp__chy, chvww__ntj)
            for i in numba.parfors.parfor.internal_prange(vdp__chy):
                B[i] = int(A[i])
            return B
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        bacj__meez, gktns__ojlir = args
        yab__rxjt = context.get_python_api(builder)
        brd__secct = yab__rxjt.string_from_string_and_size(bacj__meez,
            gktns__ojlir)
        ycbz__gcc = yab__rxjt.to_native_value(string_type, brd__secct).value
        uzyq__tyus = cgutils.create_struct_proxy(string_type)(context,
            builder, ycbz__gcc)
        uzyq__tyus.hash = uzyq__tyus.hash.type(-1)
        yab__rxjt.decref(brd__secct)
        return uzyq__tyus._getvalue()
    return string_type(types.voidptr, types.intp), codegen


def get_arr_data_ptr(arr, ind):
    return arr


@overload(get_arr_data_ptr, no_unliteral=True)
def overload_get_arr_data_ptr(arr, ind):
    assert isinstance(types.unliteral(ind), types.Integer)
    if isinstance(arr, bodo.libs.int_arr_ext.IntegerArrayType):

        def impl_int(arr, ind):
            return bodo.hiframes.split_impl.get_c_arr_ptr(arr._data.ctypes, ind
                )
        return impl_int
    assert isinstance(arr, types.Array)

    def impl_np(arr, ind):
        return bodo.hiframes.split_impl.get_c_arr_ptr(arr.ctypes, ind)
    return impl_np


def set_to_numeric_out_na_err(out_arr, out_ind, err_code):
    pass


@overload(set_to_numeric_out_na_err)
def set_to_numeric_out_na_err_overload(out_arr, out_ind, err_code):
    if isinstance(out_arr, bodo.libs.int_arr_ext.IntegerArrayType):

        def impl_int(out_arr, out_ind, err_code):
            bodo.libs.int_arr_ext.set_bit_to_arr(out_arr._null_bitmap,
                out_ind, 0 if err_code == -1 else 1)
        return impl_int
    assert isinstance(out_arr, types.Array)
    if isinstance(out_arr.dtype, types.Float):

        def impl_np(out_arr, out_ind, err_code):
            if err_code == -1:
                out_arr[out_ind] = np.nan
        return impl_np
    return lambda out_arr, out_ind, err_code: None


@numba.njit(no_cpython_wrapper=True)
def str_arr_item_to_numeric(out_arr, out_ind, str_arr, ind):
    err_code = _str_arr_item_to_numeric(get_arr_data_ptr(out_arr, out_ind),
        str_arr, ind, out_arr.dtype)
    set_to_numeric_out_na_err(out_arr, out_ind, err_code)


@intrinsic
def _str_arr_item_to_numeric(typingctx, out_ptr_t, str_arr_t, ind_t,
    out_dtype_t=None):
    assert str_arr_t == string_array_type
    assert ind_t == types.int64

    def codegen(context, builder, sig, args):
        tmbbm__dnipg, arr, ind, ejif__bvsmm = args
        rfxot__gnsxf = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type,
            rfxot__gnsxf.offsets).data
        data = context.make_helper(builder, char_arr_type, rfxot__gnsxf.data
            ).data
        nrfw__gkia = lir.FunctionType(lir.IntType(32), [tmbbm__dnipg.type,
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        ijbj__jrmv = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            ijbj__jrmv = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        ovvs__tcmt = cgutils.get_or_insert_function(builder.module,
            nrfw__gkia, ijbj__jrmv)
        return builder.call(ovvs__tcmt, [tmbbm__dnipg, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    druqa__bhwp = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    nrfw__gkia = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer(), lir.IntType(32)])
    kdhx__hjdo = cgutils.get_or_insert_function(c.builder.module,
        nrfw__gkia, name='string_array_from_sequence')
    ivnu__cjdc = c.builder.call(kdhx__hjdo, [val, druqa__bhwp])
    uzb__uyjrv = ArrayItemArrayType(char_arr_type)
    efct__lqr = c.context.make_helper(c.builder, uzb__uyjrv)
    efct__lqr.meminfo = ivnu__cjdc
    ccwi__ghktb = c.context.make_helper(c.builder, typ)
    qkv__dec = efct__lqr._getvalue()
    ccwi__ghktb.data = qkv__dec
    vjnsc__dugtl = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ccwi__ghktb._getvalue(), is_error=vjnsc__dugtl)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    vdp__chy = len(pyval)
    cakzg__tea = 0
    kjp__mfze = np.empty(vdp__chy + 1, np_offset_type)
    bvc__lpn = []
    tico__ietko = np.empty(vdp__chy + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        kjp__mfze[i] = cakzg__tea
        kyarv__kse = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(tico__ietko, i, int(not
            kyarv__kse))
        if kyarv__kse:
            continue
        zvnb__wzcl = list(s.encode()) if isinstance(s, str) else list(s)
        bvc__lpn.extend(zvnb__wzcl)
        cakzg__tea += len(zvnb__wzcl)
    kjp__mfze[vdp__chy] = cakzg__tea
    vgtic__sco = np.array(bvc__lpn, np.uint8)
    nyv__crlg = context.get_constant(types.int64, vdp__chy)
    nmumb__phy = context.get_constant_generic(builder, char_arr_type,
        vgtic__sco)
    cyuq__uipu = context.get_constant_generic(builder, offset_arr_type,
        kjp__mfze)
    xeyeu__vkrql = context.get_constant_generic(builder,
        null_bitmap_arr_type, tico__ietko)
    rfxot__gnsxf = lir.Constant.literal_struct([nyv__crlg, nmumb__phy,
        cyuq__uipu, xeyeu__vkrql])
    rfxot__gnsxf = cgutils.global_constant(builder, '.const.payload',
        rfxot__gnsxf).bitcast(cgutils.voidptr_t)
    wzmm__gsv = context.get_constant(types.int64, -1)
    tsr__zdiwd = context.get_constant_null(types.voidptr)
    htwk__qfymz = lir.Constant.literal_struct([wzmm__gsv, tsr__zdiwd,
        tsr__zdiwd, rfxot__gnsxf, wzmm__gsv])
    htwk__qfymz = cgutils.global_constant(builder, '.const.meminfo',
        htwk__qfymz).bitcast(cgutils.voidptr_t)
    qkv__dec = lir.Constant.literal_struct([htwk__qfymz])
    ccwi__ghktb = lir.Constant.literal_struct([qkv__dec])
    return ccwi__ghktb


def pre_alloc_str_arr_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 2 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


from numba.parfors.array_analysis import ArrayAnalysis
(ArrayAnalysis._analyze_op_call_bodo_libs_str_arr_ext_pre_alloc_string_array
    ) = pre_alloc_str_arr_equiv


@overload(glob.glob, no_unliteral=True)
def overload_glob_glob(pathname, recursive=False):

    def _glob_glob_impl(pathname, recursive=False):
        with numba.objmode(l='list_str_type'):
            l = glob.glob(pathname, recursive=recursive)
        return l
    return _glob_glob_impl
