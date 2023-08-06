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
        qogh__hyjn = ArrayItemArrayType(char_arr_type)
        slysa__scagk = [('data', qogh__hyjn)]
        models.StructModel.__init__(self, dmm, fe_type, slysa__scagk)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        scfz__qeet, = args
        dugt__khzvx = context.make_helper(builder, string_array_type)
        dugt__khzvx.data = scfz__qeet
        context.nrt.incref(builder, data_typ, scfz__qeet)
        return dugt__khzvx._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    rvwup__mrprl = c.context.insert_const_string(c.builder.module, 'pandas')
    bptg__bdmkg = c.pyapi.import_module_noblock(rvwup__mrprl)
    fsp__tdf = c.pyapi.call_method(bptg__bdmkg, 'StringDtype', ())
    c.pyapi.decref(bptg__bdmkg)
    return fsp__tdf


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
                bdhi__oagb = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(bdhi__oagb)
                for i in numba.parfors.parfor.internal_prange(bdhi__oagb):
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
                bdhi__oagb = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(bdhi__oagb)
                for i in numba.parfors.parfor.internal_prange(bdhi__oagb):
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
                bdhi__oagb = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(bdhi__oagb)
                for i in numba.parfors.parfor.internal_prange(bdhi__oagb):
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
    kykc__obql = lhs == string_array_type or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    oyqh__mesfy = rhs == string_array_type or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if (lhs == string_array_type and oyqh__mesfy or kykc__obql and rhs ==
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
        kiagt__tsr = 'iter(String)'
        xrd__nqnxg = string_type
        super(StringArrayIterator, self).__init__(kiagt__tsr, xrd__nqnxg)


@register_model(StringArrayIterator)
class StrArrayIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        slysa__scagk = [('index', types.EphemeralPointer(types.uintp)), (
            'array', string_array_type)]
        super(StrArrayIteratorModel, self).__init__(dmm, fe_type, slysa__scagk)


lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@lower_builtin('iternext', StringArrayIterator)
@iternext_impl(RefType.NEW)
def iternext_str_array(context, builder, sig, args, result):
    [jxho__rxqjh] = sig.args
    [uen__xmlve] = args
    nuchj__yudsf = context.make_helper(builder, jxho__rxqjh, value=uen__xmlve)
    dcpe__xjc = signature(types.intp, string_array_type)
    mjhs__vhwsk = context.compile_internal(builder, lambda a: len(a),
        dcpe__xjc, [nuchj__yudsf.array])
    stch__qmwza = builder.load(nuchj__yudsf.index)
    scg__qtwg = builder.icmp(lc.ICMP_SLT, stch__qmwza, mjhs__vhwsk)
    result.set_valid(scg__qtwg)
    with builder.if_then(scg__qtwg):
        qeka__jjdvc = signature(string_type, string_array_type, types.intp)
        value = context.compile_internal(builder, lambda a, i: a[i],
            qeka__jjdvc, [nuchj__yudsf.array, stch__qmwza])
        result.yield_(value)
        lbgd__afzsn = cgutils.increment_index(builder, stch__qmwza)
        builder.store(lbgd__afzsn, nuchj__yudsf.index)


def _get_str_binary_arr_payload(context, builder, arr_value, arr_typ):
    assert arr_typ == string_array_type or arr_typ == binary_array_type
    cdwsn__ylgl = context.make_helper(builder, arr_typ, arr_value)
    qogh__hyjn = ArrayItemArrayType(char_arr_type)
    gvwi__mbq = _get_array_item_arr_payload(context, builder, qogh__hyjn,
        cdwsn__ylgl.data)
    return gvwi__mbq


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        gvwi__mbq = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return gvwi__mbq.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        gvwi__mbq = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        hrs__eixxn = context.make_helper(builder, offset_arr_type,
            gvwi__mbq.offsets).data
        return _get_num_total_chars(builder, hrs__eixxn, gvwi__mbq.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        gvwi__mbq = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        kfq__vohsb = context.make_helper(builder, offset_arr_type,
            gvwi__mbq.offsets)
        datdg__vln = context.make_helper(builder, offset_ctypes_type)
        datdg__vln.data = builder.bitcast(kfq__vohsb.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        datdg__vln.meminfo = kfq__vohsb.meminfo
        fsp__tdf = datdg__vln._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type, fsp__tdf
            )
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        gvwi__mbq = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        scfz__qeet = context.make_helper(builder, char_arr_type, gvwi__mbq.data
            )
        datdg__vln = context.make_helper(builder, data_ctypes_type)
        datdg__vln.data = scfz__qeet.data
        datdg__vln.meminfo = scfz__qeet.meminfo
        fsp__tdf = datdg__vln._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, fsp__tdf)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        cuwyg__bebsw, ind = args
        gvwi__mbq = _get_str_binary_arr_payload(context, builder,
            cuwyg__bebsw, sig.args[0])
        scfz__qeet = context.make_helper(builder, char_arr_type, gvwi__mbq.data
            )
        datdg__vln = context.make_helper(builder, data_ctypes_type)
        datdg__vln.data = builder.gep(scfz__qeet.data, [ind])
        datdg__vln.meminfo = scfz__qeet.meminfo
        fsp__tdf = datdg__vln._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, fsp__tdf)
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        vvq__anpp, tfvh__fhegg, sziq__xhjzi, ctiqt__zcw = args
        ozhek__nouto = builder.bitcast(builder.gep(vvq__anpp, [tfvh__fhegg]
            ), lir.IntType(8).as_pointer())
        lvph__jkhz = builder.bitcast(builder.gep(sziq__xhjzi, [ctiqt__zcw]),
            lir.IntType(8).as_pointer())
        hojju__dfus = builder.load(lvph__jkhz)
        builder.store(hojju__dfus, ozhek__nouto)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        gvwi__mbq = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        hku__jwt = context.make_helper(builder, null_bitmap_arr_type,
            gvwi__mbq.null_bitmap)
        datdg__vln = context.make_helper(builder, data_ctypes_type)
        datdg__vln.data = hku__jwt.data
        datdg__vln.meminfo = hku__jwt.meminfo
        fsp__tdf = datdg__vln._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, fsp__tdf)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        gvwi__mbq = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        hrs__eixxn = context.make_helper(builder, offset_arr_type,
            gvwi__mbq.offsets).data
        return builder.load(builder.gep(hrs__eixxn, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        gvwi__mbq = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, gvwi__mbq.
            offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        sbyu__eoa, ind = args
        if in_bitmap_typ == data_ctypes_type:
            datdg__vln = context.make_helper(builder, data_ctypes_type,
                sbyu__eoa)
            sbyu__eoa = datdg__vln.data
        return builder.load(builder.gep(sbyu__eoa, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        sbyu__eoa, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            datdg__vln = context.make_helper(builder, data_ctypes_type,
                sbyu__eoa)
            sbyu__eoa = datdg__vln.data
        builder.store(val, builder.gep(sbyu__eoa, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        akz__ocbt = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        dbsx__mbns = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        mea__kgj = context.make_helper(builder, offset_arr_type, akz__ocbt.
            offsets).data
        hojs__smsr = context.make_helper(builder, offset_arr_type,
            dbsx__mbns.offsets).data
        ottwp__yjr = context.make_helper(builder, char_arr_type, akz__ocbt.data
            ).data
        xmt__shefa = context.make_helper(builder, char_arr_type, dbsx__mbns
            .data).data
        ksdwg__jhze = context.make_helper(builder, null_bitmap_arr_type,
            akz__ocbt.null_bitmap).data
        yufdo__jhvya = context.make_helper(builder, null_bitmap_arr_type,
            dbsx__mbns.null_bitmap).data
        nhug__nbfjz = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, hojs__smsr, mea__kgj, nhug__nbfjz)
        cgutils.memcpy(builder, xmt__shefa, ottwp__yjr, builder.load(
            builder.gep(mea__kgj, [ind])))
        egka__tstz = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        bsfux__fvtv = builder.lshr(egka__tstz, lir.Constant(lir.IntType(64), 3)
            )
        cgutils.memcpy(builder, yufdo__jhvya, ksdwg__jhze, bsfux__fvtv)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        akz__ocbt = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        dbsx__mbns = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        mea__kgj = context.make_helper(builder, offset_arr_type, akz__ocbt.
            offsets).data
        ottwp__yjr = context.make_helper(builder, char_arr_type, akz__ocbt.data
            ).data
        xmt__shefa = context.make_helper(builder, char_arr_type, dbsx__mbns
            .data).data
        num_total_chars = _get_num_total_chars(builder, mea__kgj, akz__ocbt
            .n_arrays)
        cgutils.memcpy(builder, xmt__shefa, ottwp__yjr, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        akz__ocbt = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        dbsx__mbns = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        mea__kgj = context.make_helper(builder, offset_arr_type, akz__ocbt.
            offsets).data
        hojs__smsr = context.make_helper(builder, offset_arr_type,
            dbsx__mbns.offsets).data
        ksdwg__jhze = context.make_helper(builder, null_bitmap_arr_type,
            akz__ocbt.null_bitmap).data
        bdhi__oagb = akz__ocbt.n_arrays
        mwfc__shso = context.get_constant(offset_type, 0)
        wfi__kfv = cgutils.alloca_once_value(builder, mwfc__shso)
        with cgutils.for_range(builder, bdhi__oagb) as loop:
            yct__poo = lower_is_na(context, builder, ksdwg__jhze, loop.index)
            with cgutils.if_likely(builder, builder.not_(yct__poo)):
                kkahg__cncy = builder.load(builder.gep(mea__kgj, [loop.index]))
                rfl__hupis = builder.load(wfi__kfv)
                builder.store(kkahg__cncy, builder.gep(hojs__smsr, [
                    rfl__hupis]))
                builder.store(builder.add(rfl__hupis, lir.Constant(context.
                    get_value_type(offset_type), 1)), wfi__kfv)
        rfl__hupis = builder.load(wfi__kfv)
        kkahg__cncy = builder.load(builder.gep(mea__kgj, [bdhi__oagb]))
        builder.store(kkahg__cncy, builder.gep(hojs__smsr, [rfl__hupis]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        lydf__kntv, ind, str, afirv__ykxu = args
        lydf__kntv = context.make_array(sig.args[0])(context, builder,
            lydf__kntv)
        teo__vydl = builder.gep(lydf__kntv.data, [ind])
        cgutils.raw_memcpy(builder, teo__vydl, str, afirv__ykxu, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        teo__vydl, ind, jkp__eiren, afirv__ykxu = args
        teo__vydl = builder.gep(teo__vydl, [ind])
        cgutils.raw_memcpy(builder, teo__vydl, jkp__eiren, afirv__ykxu, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_length(A, i):
    return np.int64(getitem_str_offset(A, i + 1) - getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_str_length(A, i):
    fvv__oyx = np.int64(getitem_str_offset(A, i))
    gutck__bmup = np.int64(getitem_str_offset(A, i + 1))
    l = gutck__bmup - fvv__oyx
    myj__tfyrm = get_data_ptr_ind(A, fvv__oyx)
    for j in range(l):
        if bodo.hiframes.split_impl.getitem_c_arr(myj__tfyrm, j) >= 128:
            return len(A[i])
    return l


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_ptr(A, i):
    return get_data_ptr_ind(A, getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_copy(B, j, A, i):
    if j == 0:
        setitem_str_offset(B, 0, 0)
    lmjx__nrg = getitem_str_offset(A, i)
    xeal__lmc = getitem_str_offset(A, i + 1)
    sjz__lqhm = xeal__lmc - lmjx__nrg
    zayw__gmquc = getitem_str_offset(B, j)
    twcfc__kaskj = zayw__gmquc + sjz__lqhm
    setitem_str_offset(B, j + 1, twcfc__kaskj)
    if str_arr_is_na(A, i):
        str_arr_set_na(B, j)
    else:
        str_arr_set_not_na(B, j)
    if sjz__lqhm != 0:
        scfz__qeet = B._data
        bodo.libs.array_item_arr_ext.ensure_data_capacity(scfz__qeet, np.
            int64(zayw__gmquc), np.int64(twcfc__kaskj))
        nzcz__rhjlh = get_data_ptr(B).data
        ouxos__qspb = get_data_ptr(A).data
        memcpy_region(nzcz__rhjlh, zayw__gmquc, ouxos__qspb, lmjx__nrg,
            sjz__lqhm, 1)


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    bdhi__oagb = len(str_arr)
    wjedj__pfea = np.empty(bdhi__oagb, np.bool_)
    for i in range(bdhi__oagb):
        wjedj__pfea[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return wjedj__pfea


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if data in [string_array_type, binary_array_type]:

        def to_list_impl(data, str_null_bools=None):
            bdhi__oagb = len(data)
            l = []
            for i in range(bdhi__oagb):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        suo__vapn = data.count
        oogc__yxwg = ['to_list_if_immutable_arr(data[{}])'.format(i) for i in
            range(suo__vapn)]
        if is_overload_true(str_null_bools):
            oogc__yxwg += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(suo__vapn) if data.types[i] in [string_array_type,
                binary_array_type]]
        jyuw__mijt = 'def f(data, str_null_bools=None):\n'
        jyuw__mijt += '  return ({}{})\n'.format(', '.join(oogc__yxwg), ',' if
            suo__vapn == 1 else '')
        bjenh__rxdyh = {}
        exec(jyuw__mijt, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, bjenh__rxdyh)
        wjgbz__egpr = bjenh__rxdyh['f']
        return wjgbz__egpr
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                bdhi__oagb = len(list_data)
                for i in range(bdhi__oagb):
                    jkp__eiren = list_data[i]
                    str_arr[i] = jkp__eiren
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                bdhi__oagb = len(list_data)
                for i in range(bdhi__oagb):
                    jkp__eiren = list_data[i]
                    str_arr[i] = jkp__eiren
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        suo__vapn = str_arr.count
        ersa__buneh = 0
        jyuw__mijt = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(suo__vapn):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                jyuw__mijt += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])\n'
                    .format(i, i, suo__vapn + ersa__buneh))
                ersa__buneh += 1
            else:
                jyuw__mijt += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        jyuw__mijt += '  return\n'
        bjenh__rxdyh = {}
        exec(jyuw__mijt, {'cp_str_list_to_array': cp_str_list_to_array},
            bjenh__rxdyh)
        dqc__gdktn = bjenh__rxdyh['f']
        return dqc__gdktn
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            bdhi__oagb = len(str_list)
            str_arr = pre_alloc_string_array(bdhi__oagb, -1)
            for i in range(bdhi__oagb):
                jkp__eiren = str_list[i]
                str_arr[i] = jkp__eiren
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            bdhi__oagb = len(A)
            jna__xjboa = 0
            for i in range(bdhi__oagb):
                jkp__eiren = A[i]
                jna__xjboa += get_utf8_size(jkp__eiren)
            return jna__xjboa
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        bdhi__oagb = len(arr)
        n_chars = num_total_chars(arr)
        cte__syirt = pre_alloc_string_array(bdhi__oagb, np.int64(n_chars))
        copy_str_arr_slice(cte__syirt, arr, bdhi__oagb)
        return cte__syirt
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
    jyuw__mijt = 'def f(in_seq):\n'
    jyuw__mijt += '    n_strs = len(in_seq)\n'
    jyuw__mijt += '    A = pre_alloc_string_array(n_strs, -1)\n'
    jyuw__mijt += '    return A\n'
    bjenh__rxdyh = {}
    exec(jyuw__mijt, {'pre_alloc_string_array': pre_alloc_string_array},
        bjenh__rxdyh)
    gueei__ephqx = bjenh__rxdyh['f']
    return gueei__ephqx


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    if in_seq.dtype == bodo.bytes_type:
        yyoc__znbct = 'pre_alloc_binary_array'
    else:
        yyoc__znbct = 'pre_alloc_string_array'
    jyuw__mijt = 'def f(in_seq):\n'
    jyuw__mijt += '    n_strs = len(in_seq)\n'
    jyuw__mijt += f'    A = {yyoc__znbct}(n_strs, -1)\n'
    jyuw__mijt += '    for i in range(n_strs):\n'
    jyuw__mijt += '        A[i] = in_seq[i]\n'
    jyuw__mijt += '    return A\n'
    bjenh__rxdyh = {}
    exec(jyuw__mijt, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, bjenh__rxdyh)
    gueei__ephqx = bjenh__rxdyh['f']
    return gueei__ephqx


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        gvwi__mbq = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        utovv__ael = builder.add(gvwi__mbq.n_arrays, lir.Constant(lir.
            IntType(64), 1))
        hghcu__fgpo = builder.lshr(lir.Constant(lir.IntType(64),
            offset_type.bitwidth), lir.Constant(lir.IntType(64), 3))
        bsfux__fvtv = builder.mul(utovv__ael, hghcu__fgpo)
        szsqy__pbnv = context.make_array(offset_arr_type)(context, builder,
            gvwi__mbq.offsets).data
        cgutils.memset(builder, szsqy__pbnv, bsfux__fvtv, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        gvwi__mbq = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        whgmw__dsaf = gvwi__mbq.n_arrays
        bsfux__fvtv = builder.lshr(builder.add(whgmw__dsaf, lir.Constant(
            lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        xbn__xsakm = context.make_array(null_bitmap_arr_type)(context,
            builder, gvwi__mbq.null_bitmap).data
        cgutils.memset(builder, xbn__xsakm, bsfux__fvtv, 0)
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
    yvxjc__wmnam = 0
    owklu__lauqs = len(len_arr)
    for i in range(owklu__lauqs):
        offsets[i] = yvxjc__wmnam
        yvxjc__wmnam += len_arr[i]
    offsets[owklu__lauqs] = yvxjc__wmnam
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    xal__jzzd = i // 8
    gtcuf__obv = getitem_str_bitmap(bits, xal__jzzd)
    gtcuf__obv ^= np.uint8(-np.uint8(bit_is_set) ^ gtcuf__obv) & kBitmask[i % 8
        ]
    setitem_str_bitmap(bits, xal__jzzd, gtcuf__obv)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    cngz__cbwu = get_null_bitmap_ptr(out_str_arr)
    xpk__jfjj = get_null_bitmap_ptr(in_str_arr)
    for j in range(len(in_str_arr)):
        ekqyj__lke = get_bit_bitmap(xpk__jfjj, j)
        set_bit_to(cngz__cbwu, out_start + j, ekqyj__lke)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type, 'set_string_array_range requires string or binary arrays'
    assert isinstance(curr_str_typ, types.Integer) and isinstance(
        curr_chars_typ, types.Integer
        ), 'set_string_array_range requires integer indices'

    def codegen(context, builder, sig, args):
        out_arr, cuwyg__bebsw, iqb__lpa, yrlpj__sazx = args
        akz__ocbt = _get_str_binary_arr_payload(context, builder,
            cuwyg__bebsw, string_array_type)
        dbsx__mbns = _get_str_binary_arr_payload(context, builder, out_arr,
            string_array_type)
        mea__kgj = context.make_helper(builder, offset_arr_type, akz__ocbt.
            offsets).data
        hojs__smsr = context.make_helper(builder, offset_arr_type,
            dbsx__mbns.offsets).data
        ottwp__yjr = context.make_helper(builder, char_arr_type, akz__ocbt.data
            ).data
        xmt__shefa = context.make_helper(builder, char_arr_type, dbsx__mbns
            .data).data
        num_total_chars = _get_num_total_chars(builder, mea__kgj, akz__ocbt
            .n_arrays)
        bmpdz__sold = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        dme__qtmg = cgutils.get_or_insert_function(builder.module,
            bmpdz__sold, name='set_string_array_range')
        builder.call(dme__qtmg, [hojs__smsr, xmt__shefa, mea__kgj,
            ottwp__yjr, iqb__lpa, yrlpj__sazx, akz__ocbt.n_arrays,
            num_total_chars])
        bixxt__afdm = context.typing_context.resolve_value_type(
            copy_nulls_range)
        hvjsp__amh = bixxt__afdm.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        kyz__bxx = context.get_function(bixxt__afdm, hvjsp__amh)
        kyz__bxx(builder, (out_arr, cuwyg__bebsw, iqb__lpa))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    xbadz__mgwb = c.context.make_helper(c.builder, typ, val)
    qogh__hyjn = ArrayItemArrayType(char_arr_type)
    gvwi__mbq = _get_array_item_arr_payload(c.context, c.builder,
        qogh__hyjn, xbadz__mgwb.data)
    cszo__undr = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    tig__szlnt = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        tig__szlnt = 'pd_array_from_string_array'
    bmpdz__sold = lir.FunctionType(c.context.get_argument_type(types.
        pyobject), [lir.IntType(64), lir.IntType(offset_type.bitwidth).
        as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
        as_pointer(), lir.IntType(32)])
    bgc__wwcl = cgutils.get_or_insert_function(c.builder.module,
        bmpdz__sold, name=tig__szlnt)
    hrs__eixxn = c.context.make_array(offset_arr_type)(c.context, c.builder,
        gvwi__mbq.offsets).data
    myj__tfyrm = c.context.make_array(char_arr_type)(c.context, c.builder,
        gvwi__mbq.data).data
    xbn__xsakm = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, gvwi__mbq.null_bitmap).data
    arr = c.builder.call(bgc__wwcl, [gvwi__mbq.n_arrays, hrs__eixxn,
        myj__tfyrm, xbn__xsakm, cszo__undr])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        gvwi__mbq = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        xbn__xsakm = context.make_array(null_bitmap_arr_type)(context,
            builder, gvwi__mbq.null_bitmap).data
        itqbc__ygquw = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        asc__odl = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        gtcuf__obv = builder.load(builder.gep(xbn__xsakm, [itqbc__ygquw],
            inbounds=True))
        frob__pze = lir.ArrayType(lir.IntType(8), 8)
        tanle__nvc = cgutils.alloca_once_value(builder, lir.Constant(
            frob__pze, (1, 2, 4, 8, 16, 32, 64, 128)))
        vjxh__vwej = builder.load(builder.gep(tanle__nvc, [lir.Constant(lir
            .IntType(64), 0), asc__odl], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(gtcuf__obv,
            vjxh__vwej), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        gvwi__mbq = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        itqbc__ygquw = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        asc__odl = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        xbn__xsakm = context.make_array(null_bitmap_arr_type)(context,
            builder, gvwi__mbq.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type, gvwi__mbq.
            offsets).data
        xie__qkceb = builder.gep(xbn__xsakm, [itqbc__ygquw], inbounds=True)
        gtcuf__obv = builder.load(xie__qkceb)
        frob__pze = lir.ArrayType(lir.IntType(8), 8)
        tanle__nvc = cgutils.alloca_once_value(builder, lir.Constant(
            frob__pze, (1, 2, 4, 8, 16, 32, 64, 128)))
        vjxh__vwej = builder.load(builder.gep(tanle__nvc, [lir.Constant(lir
            .IntType(64), 0), asc__odl], inbounds=True))
        vjxh__vwej = builder.xor(vjxh__vwej, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(gtcuf__obv, vjxh__vwej), xie__qkceb)
        if str_arr_typ == string_array_type:
            qxv__jsmeh = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            fmobc__hmy = builder.icmp_unsigned('!=', qxv__jsmeh, gvwi__mbq.
                n_arrays)
            with builder.if_then(fmobc__hmy):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [qxv__jsmeh]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        gvwi__mbq = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        itqbc__ygquw = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        asc__odl = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        xbn__xsakm = context.make_array(null_bitmap_arr_type)(context,
            builder, gvwi__mbq.null_bitmap).data
        xie__qkceb = builder.gep(xbn__xsakm, [itqbc__ygquw], inbounds=True)
        gtcuf__obv = builder.load(xie__qkceb)
        frob__pze = lir.ArrayType(lir.IntType(8), 8)
        tanle__nvc = cgutils.alloca_once_value(builder, lir.Constant(
            frob__pze, (1, 2, 4, 8, 16, 32, 64, 128)))
        vjxh__vwej = builder.load(builder.gep(tanle__nvc, [lir.Constant(lir
            .IntType(64), 0), asc__odl], inbounds=True))
        builder.store(builder.or_(gtcuf__obv, vjxh__vwej), xie__qkceb)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        gvwi__mbq = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        bsfux__fvtv = builder.udiv(builder.add(gvwi__mbq.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        xbn__xsakm = context.make_array(null_bitmap_arr_type)(context,
            builder, gvwi__mbq.null_bitmap).data
        cgutils.memset(builder, xbn__xsakm, bsfux__fvtv, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    thpx__xwjdh = context.make_helper(builder, string_array_type, str_arr)
    qogh__hyjn = ArrayItemArrayType(char_arr_type)
    qivjl__uzyyy = context.make_helper(builder, qogh__hyjn, thpx__xwjdh.data)
    qqifh__izwoa = ArrayItemArrayPayloadType(qogh__hyjn)
    njk__lkfiu = context.nrt.meminfo_data(builder, qivjl__uzyyy.meminfo)
    ave__uus = builder.bitcast(njk__lkfiu, context.get_value_type(
        qqifh__izwoa).as_pointer())
    return ave__uus


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        gqnb__xmrci, wqe__jim = args
        zudx__qlx = _get_str_binary_arr_data_payload_ptr(context, builder,
            wqe__jim)
        jrxdq__oqp = _get_str_binary_arr_data_payload_ptr(context, builder,
            gqnb__xmrci)
        ozwrf__icyzd = _get_str_binary_arr_payload(context, builder,
            wqe__jim, sig.args[1])
        vydyl__pes = _get_str_binary_arr_payload(context, builder,
            gqnb__xmrci, sig.args[0])
        context.nrt.incref(builder, char_arr_type, ozwrf__icyzd.data)
        context.nrt.incref(builder, offset_arr_type, ozwrf__icyzd.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, ozwrf__icyzd.
            null_bitmap)
        context.nrt.decref(builder, char_arr_type, vydyl__pes.data)
        context.nrt.decref(builder, offset_arr_type, vydyl__pes.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, vydyl__pes.
            null_bitmap)
        builder.store(builder.load(zudx__qlx), jrxdq__oqp)
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
        bdhi__oagb = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return bdhi__oagb
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, teo__vydl, vvpu__hdptl = args
        gvwi__mbq = _get_str_binary_arr_payload(context, builder, arr, sig.
            args[0])
        offsets = context.make_helper(builder, offset_arr_type, gvwi__mbq.
            offsets).data
        data = context.make_helper(builder, char_arr_type, gvwi__mbq.data).data
        bmpdz__sold = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        isa__ozg = cgutils.get_or_insert_function(builder.module,
            bmpdz__sold, name='setitem_string_array')
        vvh__dyyi = context.get_constant(types.int32, -1)
        jyl__cod = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets, gvwi__mbq.
            n_arrays)
        builder.call(isa__ozg, [offsets, data, num_total_chars, builder.
            extract_value(teo__vydl, 0), vvpu__hdptl, vvh__dyyi, jyl__cod, ind]
            )
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    bmpdz__sold = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64)])
    kku__nhod = cgutils.get_or_insert_function(builder.module, bmpdz__sold,
        name='is_na')
    return builder.call(kku__nhod, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        ozhek__nouto, lvph__jkhz, suo__vapn, sqqhi__oxx = args
        cgutils.raw_memcpy(builder, ozhek__nouto, lvph__jkhz, suo__vapn,
            sqqhi__oxx)
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
        nfn__trzx, zthbf__wjg = unicode_to_utf8_and_len(val)
        siik__gah = getitem_str_offset(A, ind)
        ofnnd__thbh = getitem_str_offset(A, ind + 1)
        ajqc__knjsu = ofnnd__thbh - siik__gah
        if ajqc__knjsu != zthbf__wjg:
            return False
        teo__vydl = get_data_ptr_ind(A, siik__gah)
        return memcmp(teo__vydl, nfn__trzx, zthbf__wjg) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        siik__gah = getitem_str_offset(A, ind)
        ajqc__knjsu = bodo.libs.str_ext.int_to_str_len(val)
        pjste__nne = siik__gah + ajqc__knjsu
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            siik__gah, pjste__nne)
        teo__vydl = get_data_ptr_ind(A, siik__gah)
        inplace_int64_to_str(teo__vydl, ajqc__knjsu, val)
        setitem_str_offset(A, ind + 1, siik__gah + ajqc__knjsu)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        teo__vydl, = args
        aevnz__cbac = context.insert_const_string(builder.module, '<NA>')
        tnd__ppvpg = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, teo__vydl, aevnz__cbac, tnd__ppvpg, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    pebg__shjp = len('<NA>')

    def impl(A, ind):
        siik__gah = getitem_str_offset(A, ind)
        pjste__nne = siik__gah + pebg__shjp
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            siik__gah, pjste__nne)
        teo__vydl = get_data_ptr_ind(A, siik__gah)
        inplace_set_NA_str(teo__vydl)
        setitem_str_offset(A, ind + 1, siik__gah + pebg__shjp)
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
            siik__gah = getitem_str_offset(A, ind)
            ofnnd__thbh = getitem_str_offset(A, ind + 1)
            vvpu__hdptl = ofnnd__thbh - siik__gah
            teo__vydl = get_data_ptr_ind(A, siik__gah)
            dwc__lizsw = decode_utf8(teo__vydl, vvpu__hdptl)
            return dwc__lizsw
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            bdhi__oagb = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(bdhi__oagb):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            nzcz__rhjlh = get_data_ptr(out_arr).data
            ouxos__qspb = get_data_ptr(A).data
            ersa__buneh = 0
            rfl__hupis = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(bdhi__oagb):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    fxok__eemq = get_str_arr_item_length(A, i)
                    if fxok__eemq == 1:
                        copy_single_char(nzcz__rhjlh, rfl__hupis,
                            ouxos__qspb, getitem_str_offset(A, i))
                    else:
                        memcpy_region(nzcz__rhjlh, rfl__hupis, ouxos__qspb,
                            getitem_str_offset(A, i), fxok__eemq, 1)
                    rfl__hupis += fxok__eemq
                    setitem_str_offset(out_arr, ersa__buneh + 1, rfl__hupis)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, ersa__buneh)
                    else:
                        str_arr_set_not_na(out_arr, ersa__buneh)
                    ersa__buneh += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            bdhi__oagb = len(ind)
            out_arr = pre_alloc_string_array(bdhi__oagb, -1)
            ersa__buneh = 0
            for i in range(bdhi__oagb):
                jkp__eiren = A[ind[i]]
                out_arr[ersa__buneh] = jkp__eiren
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, ersa__buneh)
                ersa__buneh += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            bdhi__oagb = len(A)
            zaeux__eupcj = numba.cpython.unicode._normalize_slice(ind,
                bdhi__oagb)
            nxbk__cvu = numba.cpython.unicode._slice_span(zaeux__eupcj)
            if zaeux__eupcj.step == 1:
                siik__gah = getitem_str_offset(A, zaeux__eupcj.start)
                ofnnd__thbh = getitem_str_offset(A, zaeux__eupcj.stop)
                n_chars = ofnnd__thbh - siik__gah
                cte__syirt = pre_alloc_string_array(nxbk__cvu, np.int64(
                    n_chars))
                for i in range(nxbk__cvu):
                    cte__syirt[i] = A[zaeux__eupcj.start + i]
                    if str_arr_is_na(A, zaeux__eupcj.start + i):
                        str_arr_set_na(cte__syirt, i)
                return cte__syirt
            else:
                cte__syirt = pre_alloc_string_array(nxbk__cvu, -1)
                for i in range(nxbk__cvu):
                    cte__syirt[i] = A[zaeux__eupcj.start + i * zaeux__eupcj
                        .step]
                    if str_arr_is_na(A, zaeux__eupcj.start + i *
                        zaeux__eupcj.step):
                        str_arr_set_na(cte__syirt, i)
                return cte__syirt
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
    mmypy__yutes = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(mmypy__yutes)
        djvgk__rrx = 4

        def impl_scalar(A, idx, val):
            gke__lbe = (val._length if val._is_ascii else djvgk__rrx * val.
                _length)
            scfz__qeet = A._data
            siik__gah = np.int64(getitem_str_offset(A, idx))
            pjste__nne = siik__gah + gke__lbe
            bodo.libs.array_item_arr_ext.ensure_data_capacity(scfz__qeet,
                siik__gah, pjste__nne)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                pjste__nne, val._data, val._length, val._kind, val.
                _is_ascii, idx)
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                zaeux__eupcj = numba.cpython.unicode._normalize_slice(idx,
                    len(A))
                fvv__oyx = zaeux__eupcj.start
                scfz__qeet = A._data
                siik__gah = np.int64(getitem_str_offset(A, fvv__oyx))
                pjste__nne = siik__gah + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(scfz__qeet,
                    siik__gah, pjste__nne)
                set_string_array_range(A, val, fvv__oyx, siik__gah)
                font__uwzbi = 0
                for i in range(zaeux__eupcj.start, zaeux__eupcj.stop,
                    zaeux__eupcj.step):
                    if str_arr_is_na(val, font__uwzbi):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    font__uwzbi += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                elrq__fmp = str_list_to_array(val)
                A[idx] = elrq__fmp
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                zaeux__eupcj = numba.cpython.unicode._normalize_slice(idx,
                    len(A))
                for i in range(zaeux__eupcj.start, zaeux__eupcj.stop,
                    zaeux__eupcj.step):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(mmypy__yutes)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                bdhi__oagb = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(bdhi__oagb, -1)
                for i in numba.parfors.parfor.internal_prange(bdhi__oagb):
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
                bdhi__oagb = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(bdhi__oagb, -1)
                zmu__bhiif = 0
                for i in numba.parfors.parfor.internal_prange(bdhi__oagb):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, zmu__bhiif):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, zmu__bhiif)
                        else:
                            out_arr[i] = str(val[zmu__bhiif])
                        zmu__bhiif += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(mmypy__yutes)
    raise BodoError(mmypy__yutes)


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
    hbuqi__uva = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(hbuqi__uva, (types.Float, types.Integer)):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(hbuqi__uva, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            bdhi__oagb = len(A)
            B = np.empty(bdhi__oagb, hbuqi__uva)
            for i in numba.parfors.parfor.internal_prange(bdhi__oagb):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = np.nan
                else:
                    B[i] = float(A[i])
            return B
        return impl_float
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            bdhi__oagb = len(A)
            B = np.empty(bdhi__oagb, hbuqi__uva)
            for i in numba.parfors.parfor.internal_prange(bdhi__oagb):
                B[i] = int(A[i])
            return B
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        teo__vydl, vvpu__hdptl = args
        itq__diqc = context.get_python_api(builder)
        yvz__bjr = itq__diqc.string_from_string_and_size(teo__vydl, vvpu__hdptl
            )
        vkul__tac = itq__diqc.to_native_value(string_type, yvz__bjr).value
        nom__isfey = cgutils.create_struct_proxy(string_type)(context,
            builder, vkul__tac)
        nom__isfey.hash = nom__isfey.hash.type(-1)
        itq__diqc.decref(yvz__bjr)
        return nom__isfey._getvalue()
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
        vvyww__qeu, arr, ind, nyphl__xjd = args
        gvwi__mbq = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, gvwi__mbq.
            offsets).data
        data = context.make_helper(builder, char_arr_type, gvwi__mbq.data).data
        bmpdz__sold = lir.FunctionType(lir.IntType(32), [vvyww__qeu.type,
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        kkib__gouz = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            kkib__gouz = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        rks__ukfow = cgutils.get_or_insert_function(builder.module,
            bmpdz__sold, kkib__gouz)
        return builder.call(rks__ukfow, [vvyww__qeu, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    cszo__undr = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    bmpdz__sold = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer(), lir.IntType(32)])
    zhb__pzt = cgutils.get_or_insert_function(c.builder.module, bmpdz__sold,
        name='string_array_from_sequence')
    jye__zuv = c.builder.call(zhb__pzt, [val, cszo__undr])
    qogh__hyjn = ArrayItemArrayType(char_arr_type)
    qivjl__uzyyy = c.context.make_helper(c.builder, qogh__hyjn)
    qivjl__uzyyy.meminfo = jye__zuv
    thpx__xwjdh = c.context.make_helper(c.builder, typ)
    scfz__qeet = qivjl__uzyyy._getvalue()
    thpx__xwjdh.data = scfz__qeet
    lbenk__nca = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(thpx__xwjdh._getvalue(), is_error=lbenk__nca)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    bdhi__oagb = len(pyval)
    rfl__hupis = 0
    kzlh__fqfzv = np.empty(bdhi__oagb + 1, np_offset_type)
    xyauc__ubz = []
    zrzj__wqyog = np.empty(bdhi__oagb + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        kzlh__fqfzv[i] = rfl__hupis
        gsprh__fkqho = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(zrzj__wqyog, i, int(not
            gsprh__fkqho))
        if gsprh__fkqho:
            continue
        kont__himfk = list(s.encode()) if isinstance(s, str) else list(s)
        xyauc__ubz.extend(kont__himfk)
        rfl__hupis += len(kont__himfk)
    kzlh__fqfzv[bdhi__oagb] = rfl__hupis
    mvj__ilgql = np.array(xyauc__ubz, np.uint8)
    qjcvm__sxo = context.get_constant(types.int64, bdhi__oagb)
    xsuj__hpr = context.get_constant_generic(builder, char_arr_type, mvj__ilgql
        )
    oyjtx__xdf = context.get_constant_generic(builder, offset_arr_type,
        kzlh__fqfzv)
    stbs__awae = context.get_constant_generic(builder, null_bitmap_arr_type,
        zrzj__wqyog)
    gvwi__mbq = lir.Constant.literal_struct([qjcvm__sxo, xsuj__hpr,
        oyjtx__xdf, stbs__awae])
    gvwi__mbq = cgutils.global_constant(builder, '.const.payload', gvwi__mbq
        ).bitcast(cgutils.voidptr_t)
    hlkeo__tkvtq = context.get_constant(types.int64, -1)
    agtdy__pfnt = context.get_constant_null(types.voidptr)
    wgy__tfmqo = lir.Constant.literal_struct([hlkeo__tkvtq, agtdy__pfnt,
        agtdy__pfnt, gvwi__mbq, hlkeo__tkvtq])
    wgy__tfmqo = cgutils.global_constant(builder, '.const.meminfo', wgy__tfmqo
        ).bitcast(cgutils.voidptr_t)
    scfz__qeet = lir.Constant.literal_struct([wgy__tfmqo])
    thpx__xwjdh = lir.Constant.literal_struct([scfz__qeet])
    return thpx__xwjdh


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
