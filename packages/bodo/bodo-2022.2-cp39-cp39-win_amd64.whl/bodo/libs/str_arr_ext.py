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
        omoxn__twn = ArrayItemArrayType(char_arr_type)
        qkx__ijt = [('data', omoxn__twn)]
        models.StructModel.__init__(self, dmm, fe_type, qkx__ijt)


make_attribute_wrapper(StringArrayType, 'data', '_data')
make_attribute_wrapper(BinaryArrayType, 'data', '_data')


@intrinsic
def init_str_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType
        ) and data_typ.dtype == types.Array(char_type, 1, 'C')

    def codegen(context, builder, sig, args):
        mivg__jipko, = args
        xaoe__xdhcn = context.make_helper(builder, string_array_type)
        xaoe__xdhcn.data = mivg__jipko
        context.nrt.incref(builder, data_typ, mivg__jipko)
        return xaoe__xdhcn._getvalue()
    return string_array_type(data_typ), codegen


class StringDtype(types.Number):

    def __init__(self):
        super(StringDtype, self).__init__('StringDtype')


string_dtype = StringDtype()
register_model(StringDtype)(models.OpaqueModel)


@box(StringDtype)
def box_string_dtype(typ, val, c):
    fvqh__eshqj = c.context.insert_const_string(c.builder.module, 'pandas')
    wkqfa__tmjh = c.pyapi.import_module_noblock(fvqh__eshqj)
    tit__jll = c.pyapi.call_method(wkqfa__tmjh, 'StringDtype', ())
    c.pyapi.decref(wkqfa__tmjh)
    return tit__jll


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
                cxcd__sys = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(cxcd__sys)
                for i in numba.parfors.parfor.internal_prange(cxcd__sys):
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
                cxcd__sys = len(lhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(cxcd__sys)
                for i in numba.parfors.parfor.internal_prange(cxcd__sys):
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
                cxcd__sys = len(rhs)
                out_arr = bodo.libs.bool_arr_ext.alloc_bool_array(cxcd__sys)
                for i in numba.parfors.parfor.internal_prange(cxcd__sys):
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
    nffvp__tkpbn = lhs == string_array_type or isinstance(lhs, types.Array
        ) and lhs.dtype == string_type
    hvde__bfkvp = rhs == string_array_type or isinstance(rhs, types.Array
        ) and rhs.dtype == string_type
    if (lhs == string_array_type and hvde__bfkvp or nffvp__tkpbn and rhs ==
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
        clujo__wra = 'iter(String)'
        kyfjd__zjmw = string_type
        super(StringArrayIterator, self).__init__(clujo__wra, kyfjd__zjmw)


@register_model(StringArrayIterator)
class StrArrayIteratorModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        qkx__ijt = [('index', types.EphemeralPointer(types.uintp)), (
            'array', string_array_type)]
        super(StrArrayIteratorModel, self).__init__(dmm, fe_type, qkx__ijt)


lower_builtin('getiter', string_array_type)(numba.np.arrayobj.getiter_array)


@lower_builtin('iternext', StringArrayIterator)
@iternext_impl(RefType.NEW)
def iternext_str_array(context, builder, sig, args, result):
    [ntifo__zhtn] = sig.args
    [hzli__pltbw] = args
    vebs__nhd = context.make_helper(builder, ntifo__zhtn, value=hzli__pltbw)
    tpo__rwh = signature(types.intp, string_array_type)
    ifbvu__znnh = context.compile_internal(builder, lambda a: len(a),
        tpo__rwh, [vebs__nhd.array])
    pytow__cgya = builder.load(vebs__nhd.index)
    cya__dtv = builder.icmp(lc.ICMP_SLT, pytow__cgya, ifbvu__znnh)
    result.set_valid(cya__dtv)
    with builder.if_then(cya__dtv):
        moc__dlo = signature(string_type, string_array_type, types.intp)
        value = context.compile_internal(builder, lambda a, i: a[i],
            moc__dlo, [vebs__nhd.array, pytow__cgya])
        result.yield_(value)
        som__oxqvt = cgutils.increment_index(builder, pytow__cgya)
        builder.store(som__oxqvt, vebs__nhd.index)


def _get_str_binary_arr_payload(context, builder, arr_value, arr_typ):
    assert arr_typ == string_array_type or arr_typ == binary_array_type
    vik__xagk = context.make_helper(builder, arr_typ, arr_value)
    omoxn__twn = ArrayItemArrayType(char_arr_type)
    lmaw__shg = _get_array_item_arr_payload(context, builder, omoxn__twn,
        vik__xagk.data)
    return lmaw__shg


@intrinsic
def num_strings(typingctx, str_arr_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        lmaw__shg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        return lmaw__shg.n_arrays
    return types.int64(string_array_type), codegen


def _get_num_total_chars(builder, offsets, num_strings):
    return builder.zext(builder.load(builder.gep(offsets, [num_strings])),
        lir.IntType(64))


@intrinsic
def num_total_chars(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        lmaw__shg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        rviha__htwtv = context.make_helper(builder, offset_arr_type,
            lmaw__shg.offsets).data
        return _get_num_total_chars(builder, rviha__htwtv, lmaw__shg.n_arrays)
    return types.uint64(in_arr_typ), codegen


@intrinsic
def get_offset_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        lmaw__shg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        oozmc__koqi = context.make_helper(builder, offset_arr_type,
            lmaw__shg.offsets)
        zgyu__zxxb = context.make_helper(builder, offset_ctypes_type)
        zgyu__zxxb.data = builder.bitcast(oozmc__koqi.data, lir.IntType(
            offset_type.bitwidth).as_pointer())
        zgyu__zxxb.meminfo = oozmc__koqi.meminfo
        tit__jll = zgyu__zxxb._getvalue()
        return impl_ret_borrowed(context, builder, offset_ctypes_type, tit__jll
            )
    return offset_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        lmaw__shg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        mivg__jipko = context.make_helper(builder, char_arr_type, lmaw__shg
            .data)
        zgyu__zxxb = context.make_helper(builder, data_ctypes_type)
        zgyu__zxxb.data = mivg__jipko.data
        zgyu__zxxb.meminfo = mivg__jipko.meminfo
        tit__jll = zgyu__zxxb._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, tit__jll)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def get_data_ptr_ind(typingctx, in_arr_typ, int_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        wcrv__cqav, ind = args
        lmaw__shg = _get_str_binary_arr_payload(context, builder,
            wcrv__cqav, sig.args[0])
        mivg__jipko = context.make_helper(builder, char_arr_type, lmaw__shg
            .data)
        zgyu__zxxb = context.make_helper(builder, data_ctypes_type)
        zgyu__zxxb.data = builder.gep(mivg__jipko.data, [ind])
        zgyu__zxxb.meminfo = mivg__jipko.meminfo
        tit__jll = zgyu__zxxb._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, tit__jll)
    return data_ctypes_type(in_arr_typ, types.intp), codegen


@intrinsic
def copy_single_char(typingctx, dst_ptr_t, dst_ind_t, src_ptr_t, src_ind_t=None
    ):

    def codegen(context, builder, sig, args):
        vhqbr__yqa, cthc__cnkn, kfrrr__hvzef, nbx__thrin = args
        flk__yon = builder.bitcast(builder.gep(vhqbr__yqa, [cthc__cnkn]),
            lir.IntType(8).as_pointer())
        nyqc__uuh = builder.bitcast(builder.gep(kfrrr__hvzef, [nbx__thrin]),
            lir.IntType(8).as_pointer())
        mwvz__eha = builder.load(nyqc__uuh)
        builder.store(mwvz__eha, flk__yon)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@intrinsic
def get_null_bitmap_ptr(typingctx, in_arr_typ=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        lmaw__shg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        xkcs__lyvuo = context.make_helper(builder, null_bitmap_arr_type,
            lmaw__shg.null_bitmap)
        zgyu__zxxb = context.make_helper(builder, data_ctypes_type)
        zgyu__zxxb.data = xkcs__lyvuo.data
        zgyu__zxxb.meminfo = xkcs__lyvuo.meminfo
        tit__jll = zgyu__zxxb._getvalue()
        return impl_ret_borrowed(context, builder, data_ctypes_type, tit__jll)
    return data_ctypes_type(in_arr_typ), codegen


@intrinsic
def getitem_str_offset(typingctx, in_arr_typ, ind_t=None):
    assert in_arr_typ in [binary_array_type, string_array_type]

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        lmaw__shg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        rviha__htwtv = context.make_helper(builder, offset_arr_type,
            lmaw__shg.offsets).data
        return builder.load(builder.gep(rviha__htwtv, [ind]))
    return offset_type(in_arr_typ, ind_t), codegen


@intrinsic
def setitem_str_offset(typingctx, str_arr_typ, ind_t, val_t=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind, val = args
        lmaw__shg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, lmaw__shg.
            offsets).data
        builder.store(val, builder.gep(offsets, [ind]))
        return context.get_dummy_value()
    return types.void(string_array_type, ind_t, offset_type), codegen


@intrinsic
def getitem_str_bitmap(typingctx, in_bitmap_typ, ind_t=None):

    def codegen(context, builder, sig, args):
        iqak__smyps, ind = args
        if in_bitmap_typ == data_ctypes_type:
            zgyu__zxxb = context.make_helper(builder, data_ctypes_type,
                iqak__smyps)
            iqak__smyps = zgyu__zxxb.data
        return builder.load(builder.gep(iqak__smyps, [ind]))
    return char_type(in_bitmap_typ, ind_t), codegen


@intrinsic
def setitem_str_bitmap(typingctx, in_bitmap_typ, ind_t, val_t=None):

    def codegen(context, builder, sig, args):
        iqak__smyps, ind, val = args
        if in_bitmap_typ == data_ctypes_type:
            zgyu__zxxb = context.make_helper(builder, data_ctypes_type,
                iqak__smyps)
            iqak__smyps = zgyu__zxxb.data
        builder.store(val, builder.gep(iqak__smyps, [ind]))
        return context.get_dummy_value()
    return types.void(in_bitmap_typ, ind_t, char_type), codegen


@intrinsic
def copy_str_arr_slice(typingctx, out_str_arr_typ, in_str_arr_typ, ind_t=None):
    assert out_str_arr_typ == string_array_type and in_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr, ind = args
        ctq__vwa = _get_str_binary_arr_payload(context, builder, in_str_arr,
            string_array_type)
        wdzbu__utoae = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        mdpu__zoby = context.make_helper(builder, offset_arr_type, ctq__vwa
            .offsets).data
        okonf__pcjk = context.make_helper(builder, offset_arr_type,
            wdzbu__utoae.offsets).data
        eiry__ukp = context.make_helper(builder, char_arr_type, ctq__vwa.data
            ).data
        xuzkh__wjsur = context.make_helper(builder, char_arr_type,
            wdzbu__utoae.data).data
        peq__qxbob = context.make_helper(builder, null_bitmap_arr_type,
            ctq__vwa.null_bitmap).data
        rfei__djc = context.make_helper(builder, null_bitmap_arr_type,
            wdzbu__utoae.null_bitmap).data
        ziht__dyu = builder.add(ind, context.get_constant(types.intp, 1))
        cgutils.memcpy(builder, okonf__pcjk, mdpu__zoby, ziht__dyu)
        cgutils.memcpy(builder, xuzkh__wjsur, eiry__ukp, builder.load(
            builder.gep(mdpu__zoby, [ind])))
        ihrg__hvtdj = builder.add(ind, lir.Constant(lir.IntType(64), 7))
        uakmt__ona = builder.lshr(ihrg__hvtdj, lir.Constant(lir.IntType(64), 3)
            )
        cgutils.memcpy(builder, rfei__djc, peq__qxbob, uakmt__ona)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type, ind_t), codegen


@intrinsic
def copy_data(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        ctq__vwa = _get_str_binary_arr_payload(context, builder, in_str_arr,
            string_array_type)
        wdzbu__utoae = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        mdpu__zoby = context.make_helper(builder, offset_arr_type, ctq__vwa
            .offsets).data
        eiry__ukp = context.make_helper(builder, char_arr_type, ctq__vwa.data
            ).data
        xuzkh__wjsur = context.make_helper(builder, char_arr_type,
            wdzbu__utoae.data).data
        num_total_chars = _get_num_total_chars(builder, mdpu__zoby,
            ctq__vwa.n_arrays)
        cgutils.memcpy(builder, xuzkh__wjsur, eiry__ukp, num_total_chars)
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def copy_non_null_offsets(typingctx, str_arr_typ, out_str_arr_typ=None):
    assert str_arr_typ == string_array_type and out_str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        out_str_arr, in_str_arr = args
        ctq__vwa = _get_str_binary_arr_payload(context, builder, in_str_arr,
            string_array_type)
        wdzbu__utoae = _get_str_binary_arr_payload(context, builder,
            out_str_arr, string_array_type)
        mdpu__zoby = context.make_helper(builder, offset_arr_type, ctq__vwa
            .offsets).data
        okonf__pcjk = context.make_helper(builder, offset_arr_type,
            wdzbu__utoae.offsets).data
        peq__qxbob = context.make_helper(builder, null_bitmap_arr_type,
            ctq__vwa.null_bitmap).data
        cxcd__sys = ctq__vwa.n_arrays
        wytj__arajd = context.get_constant(offset_type, 0)
        mgatx__jthmt = cgutils.alloca_once_value(builder, wytj__arajd)
        with cgutils.for_range(builder, cxcd__sys) as loop:
            ilnca__zpde = lower_is_na(context, builder, peq__qxbob, loop.index)
            with cgutils.if_likely(builder, builder.not_(ilnca__zpde)):
                hnq__tihj = builder.load(builder.gep(mdpu__zoby, [loop.index]))
                luuok__jhxn = builder.load(mgatx__jthmt)
                builder.store(hnq__tihj, builder.gep(okonf__pcjk, [
                    luuok__jhxn]))
                builder.store(builder.add(luuok__jhxn, lir.Constant(context
                    .get_value_type(offset_type), 1)), mgatx__jthmt)
        luuok__jhxn = builder.load(mgatx__jthmt)
        hnq__tihj = builder.load(builder.gep(mdpu__zoby, [cxcd__sys]))
        builder.store(hnq__tihj, builder.gep(okonf__pcjk, [luuok__jhxn]))
        return context.get_dummy_value()
    return types.void(string_array_type, string_array_type), codegen


@intrinsic
def str_copy(typingctx, buff_arr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        tcq__wvf, ind, str, tcmq__uuhyf = args
        tcq__wvf = context.make_array(sig.args[0])(context, builder, tcq__wvf)
        ahl__kvkof = builder.gep(tcq__wvf.data, [ind])
        cgutils.raw_memcpy(builder, ahl__kvkof, str, tcmq__uuhyf, 1)
        return context.get_dummy_value()
    return types.void(null_bitmap_arr_type, types.intp, types.voidptr,
        types.intp), codegen


@intrinsic
def str_copy_ptr(typingctx, ptr_typ, ind_typ, str_typ, len_typ=None):

    def codegen(context, builder, sig, args):
        ahl__kvkof, ind, ctb__ybea, tcmq__uuhyf = args
        ahl__kvkof = builder.gep(ahl__kvkof, [ind])
        cgutils.raw_memcpy(builder, ahl__kvkof, ctb__ybea, tcmq__uuhyf, 1)
        return context.get_dummy_value()
    return types.void(types.voidptr, types.intp, types.voidptr, types.intp
        ), codegen


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_length(A, i):
    return np.int64(getitem_str_offset(A, i + 1) - getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_str_length(A, i):
    jkuxk__cuex = np.int64(getitem_str_offset(A, i))
    ubq__wejrh = np.int64(getitem_str_offset(A, i + 1))
    l = ubq__wejrh - jkuxk__cuex
    hmdz__owqn = get_data_ptr_ind(A, jkuxk__cuex)
    for j in range(l):
        if bodo.hiframes.split_impl.getitem_c_arr(hmdz__owqn, j) >= 128:
            return len(A[i])
    return l


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_ptr(A, i):
    return get_data_ptr_ind(A, getitem_str_offset(A, i))


@numba.njit(no_cpython_wrapper=True)
def get_str_arr_item_copy(B, j, A, i):
    if j == 0:
        setitem_str_offset(B, 0, 0)
    cnhz__zfl = getitem_str_offset(A, i)
    jfkrn__niv = getitem_str_offset(A, i + 1)
    hnlc__cbrj = jfkrn__niv - cnhz__zfl
    iwyl__bnu = getitem_str_offset(B, j)
    ftni__gyw = iwyl__bnu + hnlc__cbrj
    setitem_str_offset(B, j + 1, ftni__gyw)
    if str_arr_is_na(A, i):
        str_arr_set_na(B, j)
    else:
        str_arr_set_not_na(B, j)
    if hnlc__cbrj != 0:
        mivg__jipko = B._data
        bodo.libs.array_item_arr_ext.ensure_data_capacity(mivg__jipko, np.
            int64(iwyl__bnu), np.int64(ftni__gyw))
        ftgb__eyzs = get_data_ptr(B).data
        vuq__emr = get_data_ptr(A).data
        memcpy_region(ftgb__eyzs, iwyl__bnu, vuq__emr, cnhz__zfl, hnlc__cbrj, 1
            )


@numba.njit(no_cpython_wrapper=True)
def get_str_null_bools(str_arr):
    cxcd__sys = len(str_arr)
    gftrp__jbbm = np.empty(cxcd__sys, np.bool_)
    for i in range(cxcd__sys):
        gftrp__jbbm[i] = bodo.libs.array_kernels.isna(str_arr, i)
    return gftrp__jbbm


def to_list_if_immutable_arr(arr, str_null_bools=None):
    return arr


@overload(to_list_if_immutable_arr, no_unliteral=True)
def to_list_if_immutable_arr_overload(data, str_null_bools=None):
    if data in [string_array_type, binary_array_type]:

        def to_list_impl(data, str_null_bools=None):
            cxcd__sys = len(data)
            l = []
            for i in range(cxcd__sys):
                l.append(data[i])
            return l
        return to_list_impl
    if isinstance(data, types.BaseTuple):
        rlx__xygje = data.count
        txjg__tkgf = ['to_list_if_immutable_arr(data[{}])'.format(i) for i in
            range(rlx__xygje)]
        if is_overload_true(str_null_bools):
            txjg__tkgf += ['get_str_null_bools(data[{}])'.format(i) for i in
                range(rlx__xygje) if data.types[i] in [string_array_type,
                binary_array_type]]
        hwzev__kcj = 'def f(data, str_null_bools=None):\n'
        hwzev__kcj += '  return ({}{})\n'.format(', '.join(txjg__tkgf), ',' if
            rlx__xygje == 1 else '')
        goosh__xrlbb = {}
        exec(hwzev__kcj, {'to_list_if_immutable_arr':
            to_list_if_immutable_arr, 'get_str_null_bools':
            get_str_null_bools, 'bodo': bodo}, goosh__xrlbb)
        gdgl__mfsj = goosh__xrlbb['f']
        return gdgl__mfsj
    return lambda data, str_null_bools=None: data


def cp_str_list_to_array(str_arr, str_list, str_null_bools=None):
    return


@overload(cp_str_list_to_array, no_unliteral=True)
def cp_str_list_to_array_overload(str_arr, list_data, str_null_bools=None):
    if str_arr == string_array_type:
        if is_overload_none(str_null_bools):

            def cp_str_list_impl(str_arr, list_data, str_null_bools=None):
                cxcd__sys = len(list_data)
                for i in range(cxcd__sys):
                    ctb__ybea = list_data[i]
                    str_arr[i] = ctb__ybea
            return cp_str_list_impl
        else:

            def cp_str_list_impl_null(str_arr, list_data, str_null_bools=None):
                cxcd__sys = len(list_data)
                for i in range(cxcd__sys):
                    ctb__ybea = list_data[i]
                    str_arr[i] = ctb__ybea
                    if str_null_bools[i]:
                        str_arr_set_na(str_arr, i)
                    else:
                        str_arr_set_not_na(str_arr, i)
            return cp_str_list_impl_null
    if isinstance(str_arr, types.BaseTuple):
        rlx__xygje = str_arr.count
        xspi__ethv = 0
        hwzev__kcj = 'def f(str_arr, list_data, str_null_bools=None):\n'
        for i in range(rlx__xygje):
            if is_overload_true(str_null_bools) and str_arr.types[i
                ] == string_array_type:
                hwzev__kcj += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}], list_data[{}])\n'
                    .format(i, i, rlx__xygje + xspi__ethv))
                xspi__ethv += 1
            else:
                hwzev__kcj += (
                    '  cp_str_list_to_array(str_arr[{}], list_data[{}])\n'.
                    format(i, i))
        hwzev__kcj += '  return\n'
        goosh__xrlbb = {}
        exec(hwzev__kcj, {'cp_str_list_to_array': cp_str_list_to_array},
            goosh__xrlbb)
        pma__sbkhu = goosh__xrlbb['f']
        return pma__sbkhu
    return lambda str_arr, list_data, str_null_bools=None: None


def str_list_to_array(str_list):
    return str_list


@overload(str_list_to_array, no_unliteral=True)
def str_list_to_array_overload(str_list):
    if isinstance(str_list, types.List) and str_list.dtype == bodo.string_type:

        def str_list_impl(str_list):
            cxcd__sys = len(str_list)
            str_arr = pre_alloc_string_array(cxcd__sys, -1)
            for i in range(cxcd__sys):
                ctb__ybea = str_list[i]
                str_arr[i] = ctb__ybea
            return str_arr
        return str_list_impl
    return lambda str_list: str_list


def get_num_total_chars(A):
    pass


@overload(get_num_total_chars)
def overload_get_num_total_chars(A):
    if isinstance(A, types.List) and A.dtype == string_type:

        def str_list_impl(A):
            cxcd__sys = len(A)
            xabj__ioky = 0
            for i in range(cxcd__sys):
                ctb__ybea = A[i]
                xabj__ioky += get_utf8_size(ctb__ybea)
            return xabj__ioky
        return str_list_impl
    assert A == string_array_type
    return lambda A: num_total_chars(A)


@overload_method(StringArrayType, 'copy', no_unliteral=True)
def str_arr_copy_overload(arr):

    def copy_impl(arr):
        cxcd__sys = len(arr)
        n_chars = num_total_chars(arr)
        idxs__vjouy = pre_alloc_string_array(cxcd__sys, np.int64(n_chars))
        copy_str_arr_slice(idxs__vjouy, arr, cxcd__sys)
        return idxs__vjouy
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
    hwzev__kcj = 'def f(in_seq):\n'
    hwzev__kcj += '    n_strs = len(in_seq)\n'
    hwzev__kcj += '    A = pre_alloc_string_array(n_strs, -1)\n'
    hwzev__kcj += '    return A\n'
    goosh__xrlbb = {}
    exec(hwzev__kcj, {'pre_alloc_string_array': pre_alloc_string_array},
        goosh__xrlbb)
    gcl__cibiq = goosh__xrlbb['f']
    return gcl__cibiq


@numba.generated_jit(nopython=True)
def str_arr_from_sequence(in_seq):
    if in_seq.dtype == bodo.bytes_type:
        sxwxn__bvij = 'pre_alloc_binary_array'
    else:
        sxwxn__bvij = 'pre_alloc_string_array'
    hwzev__kcj = 'def f(in_seq):\n'
    hwzev__kcj += '    n_strs = len(in_seq)\n'
    hwzev__kcj += f'    A = {sxwxn__bvij}(n_strs, -1)\n'
    hwzev__kcj += '    for i in range(n_strs):\n'
    hwzev__kcj += '        A[i] = in_seq[i]\n'
    hwzev__kcj += '    return A\n'
    goosh__xrlbb = {}
    exec(hwzev__kcj, {'pre_alloc_string_array': pre_alloc_string_array,
        'pre_alloc_binary_array': pre_alloc_binary_array}, goosh__xrlbb)
    gcl__cibiq = goosh__xrlbb['f']
    return gcl__cibiq


@intrinsic
def set_all_offsets_to_0(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_all_offsets_to_0 requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        lmaw__shg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        sfs__ips = builder.add(lmaw__shg.n_arrays, lir.Constant(lir.IntType
            (64), 1))
        utbel__cjy = builder.lshr(lir.Constant(lir.IntType(64), offset_type
            .bitwidth), lir.Constant(lir.IntType(64), 3))
        uakmt__ona = builder.mul(sfs__ips, utbel__cjy)
        ivwc__ddga = context.make_array(offset_arr_type)(context, builder,
            lmaw__shg.offsets).data
        cgutils.memset(builder, ivwc__ddga, uakmt__ona, 0)
        return context.get_dummy_value()
    return types.none(arr_typ), codegen


@intrinsic
def set_bitmap_all_NA(typingctx, arr_typ=None):
    assert arr_typ in (string_array_type, binary_array_type
        ), 'set_bitmap_all_NA requires a string or binary array'

    def codegen(context, builder, sig, args):
        in_str_arr, = args
        lmaw__shg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, sig.args[0])
        xvf__ofotf = lmaw__shg.n_arrays
        uakmt__ona = builder.lshr(builder.add(xvf__ofotf, lir.Constant(lir.
            IntType(64), 7)), lir.Constant(lir.IntType(64), 3))
        lyb__ojwg = context.make_array(null_bitmap_arr_type)(context,
            builder, lmaw__shg.null_bitmap).data
        cgutils.memset(builder, lyb__ojwg, uakmt__ona, 0)
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
    xxc__zbrte = 0
    xadnj__osvh = len(len_arr)
    for i in range(xadnj__osvh):
        offsets[i] = xxc__zbrte
        xxc__zbrte += len_arr[i]
    offsets[xadnj__osvh] = xxc__zbrte
    return str_arr


kBitmask = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


@numba.njit
def set_bit_to(bits, i, bit_is_set):
    ojoik__jwnr = i // 8
    tpo__nnssg = getitem_str_bitmap(bits, ojoik__jwnr)
    tpo__nnssg ^= np.uint8(-np.uint8(bit_is_set) ^ tpo__nnssg) & kBitmask[i % 8
        ]
    setitem_str_bitmap(bits, ojoik__jwnr, tpo__nnssg)


@numba.njit
def get_bit_bitmap(bits, i):
    return getitem_str_bitmap(bits, i >> 3) >> (i & 7) & 1


@numba.njit
def copy_nulls_range(out_str_arr, in_str_arr, out_start):
    fti__nkbmr = get_null_bitmap_ptr(out_str_arr)
    oiu__vqdju = get_null_bitmap_ptr(in_str_arr)
    for j in range(len(in_str_arr)):
        nqr__wxxl = get_bit_bitmap(oiu__vqdju, j)
        set_bit_to(fti__nkbmr, out_start + j, nqr__wxxl)


@intrinsic
def set_string_array_range(typingctx, out_typ, in_typ, curr_str_typ,
    curr_chars_typ=None):
    assert out_typ == string_array_type and in_typ == string_array_type or out_typ == binary_array_type and in_typ == binary_array_type, 'set_string_array_range requires string or binary arrays'
    assert isinstance(curr_str_typ, types.Integer) and isinstance(
        curr_chars_typ, types.Integer
        ), 'set_string_array_range requires integer indices'

    def codegen(context, builder, sig, args):
        out_arr, wcrv__cqav, pkeij__lcbh, zxj__vrvlj = args
        ctq__vwa = _get_str_binary_arr_payload(context, builder, wcrv__cqav,
            string_array_type)
        wdzbu__utoae = _get_str_binary_arr_payload(context, builder,
            out_arr, string_array_type)
        mdpu__zoby = context.make_helper(builder, offset_arr_type, ctq__vwa
            .offsets).data
        okonf__pcjk = context.make_helper(builder, offset_arr_type,
            wdzbu__utoae.offsets).data
        eiry__ukp = context.make_helper(builder, char_arr_type, ctq__vwa.data
            ).data
        xuzkh__wjsur = context.make_helper(builder, char_arr_type,
            wdzbu__utoae.data).data
        num_total_chars = _get_num_total_chars(builder, mdpu__zoby,
            ctq__vwa.n_arrays)
        zhqwp__xhcvv = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64), lir.IntType(64), lir.IntType(64),
            lir.IntType(64)])
        udf__dmnz = cgutils.get_or_insert_function(builder.module,
            zhqwp__xhcvv, name='set_string_array_range')
        builder.call(udf__dmnz, [okonf__pcjk, xuzkh__wjsur, mdpu__zoby,
            eiry__ukp, pkeij__lcbh, zxj__vrvlj, ctq__vwa.n_arrays,
            num_total_chars])
        hfqn__pjb = context.typing_context.resolve_value_type(copy_nulls_range)
        bqy__zxxwq = hfqn__pjb.get_call_type(context.typing_context, (
            string_array_type, string_array_type, types.int64), {})
        mqsmz__aeaun = context.get_function(hfqn__pjb, bqy__zxxwq)
        mqsmz__aeaun(builder, (out_arr, wcrv__cqav, pkeij__lcbh))
        return context.get_dummy_value()
    sig = types.void(out_typ, in_typ, types.intp, types.intp)
    return sig, codegen


@box(BinaryArrayType)
@box(StringArrayType)
def box_str_arr(typ, val, c):
    assert typ in [binary_array_type, string_array_type]
    jfm__wci = c.context.make_helper(c.builder, typ, val)
    omoxn__twn = ArrayItemArrayType(char_arr_type)
    lmaw__shg = _get_array_item_arr_payload(c.context, c.builder,
        omoxn__twn, jfm__wci.data)
    snpj__gtl = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    ifgmr__fasp = 'np_array_from_string_array'
    if use_pd_string_array and typ != binary_array_type:
        ifgmr__fasp = 'pd_array_from_string_array'
    zhqwp__xhcvv = lir.FunctionType(c.context.get_argument_type(types.
        pyobject), [lir.IntType(64), lir.IntType(offset_type.bitwidth).
        as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
        as_pointer(), lir.IntType(32)])
    zrf__pqy = cgutils.get_or_insert_function(c.builder.module,
        zhqwp__xhcvv, name=ifgmr__fasp)
    rviha__htwtv = c.context.make_array(offset_arr_type)(c.context, c.
        builder, lmaw__shg.offsets).data
    hmdz__owqn = c.context.make_array(char_arr_type)(c.context, c.builder,
        lmaw__shg.data).data
    lyb__ojwg = c.context.make_array(null_bitmap_arr_type)(c.context, c.
        builder, lmaw__shg.null_bitmap).data
    arr = c.builder.call(zrf__pqy, [lmaw__shg.n_arrays, rviha__htwtv,
        hmdz__owqn, lyb__ojwg, snpj__gtl])
    c.context.nrt.decref(c.builder, typ, val)
    return arr


@intrinsic
def str_arr_is_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        lmaw__shg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        lyb__ojwg = context.make_array(null_bitmap_arr_type)(context,
            builder, lmaw__shg.null_bitmap).data
        jdh__qxha = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        ezuc__vbs = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        tpo__nnssg = builder.load(builder.gep(lyb__ojwg, [jdh__qxha],
            inbounds=True))
        xrws__npcp = lir.ArrayType(lir.IntType(8), 8)
        hvk__dhjqm = cgutils.alloca_once_value(builder, lir.Constant(
            xrws__npcp, (1, 2, 4, 8, 16, 32, 64, 128)))
        bpgj__thbo = builder.load(builder.gep(hvk__dhjqm, [lir.Constant(lir
            .IntType(64), 0), ezuc__vbs], inbounds=True))
        return builder.icmp_unsigned('==', builder.and_(tpo__nnssg,
            bpgj__thbo), lir.Constant(lir.IntType(8), 0))
    return types.bool_(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        lmaw__shg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        jdh__qxha = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        ezuc__vbs = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        lyb__ojwg = context.make_array(null_bitmap_arr_type)(context,
            builder, lmaw__shg.null_bitmap).data
        offsets = context.make_helper(builder, offset_arr_type, lmaw__shg.
            offsets).data
        xclt__dxe = builder.gep(lyb__ojwg, [jdh__qxha], inbounds=True)
        tpo__nnssg = builder.load(xclt__dxe)
        xrws__npcp = lir.ArrayType(lir.IntType(8), 8)
        hvk__dhjqm = cgutils.alloca_once_value(builder, lir.Constant(
            xrws__npcp, (1, 2, 4, 8, 16, 32, 64, 128)))
        bpgj__thbo = builder.load(builder.gep(hvk__dhjqm, [lir.Constant(lir
            .IntType(64), 0), ezuc__vbs], inbounds=True))
        bpgj__thbo = builder.xor(bpgj__thbo, lir.Constant(lir.IntType(8), -1))
        builder.store(builder.and_(tpo__nnssg, bpgj__thbo), xclt__dxe)
        if str_arr_typ == string_array_type:
            fxbsn__fvoad = builder.add(ind, lir.Constant(lir.IntType(64), 1))
            fnfgm__hzi = builder.icmp_unsigned('!=', fxbsn__fvoad,
                lmaw__shg.n_arrays)
            with builder.if_then(fnfgm__hzi):
                builder.store(builder.load(builder.gep(offsets, [ind])),
                    builder.gep(offsets, [fxbsn__fvoad]))
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def str_arr_set_not_na(typingctx, str_arr_typ, ind_typ=None):
    assert str_arr_typ == string_array_type

    def codegen(context, builder, sig, args):
        in_str_arr, ind = args
        lmaw__shg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        jdh__qxha = builder.lshr(ind, lir.Constant(lir.IntType(64), 3))
        ezuc__vbs = builder.urem(ind, lir.Constant(lir.IntType(64), 8))
        lyb__ojwg = context.make_array(null_bitmap_arr_type)(context,
            builder, lmaw__shg.null_bitmap).data
        xclt__dxe = builder.gep(lyb__ojwg, [jdh__qxha], inbounds=True)
        tpo__nnssg = builder.load(xclt__dxe)
        xrws__npcp = lir.ArrayType(lir.IntType(8), 8)
        hvk__dhjqm = cgutils.alloca_once_value(builder, lir.Constant(
            xrws__npcp, (1, 2, 4, 8, 16, 32, 64, 128)))
        bpgj__thbo = builder.load(builder.gep(hvk__dhjqm, [lir.Constant(lir
            .IntType(64), 0), ezuc__vbs], inbounds=True))
        builder.store(builder.or_(tpo__nnssg, bpgj__thbo), xclt__dxe)
        return context.get_dummy_value()
    return types.void(str_arr_typ, types.intp), codegen


@intrinsic
def set_null_bits_to_value(typingctx, arr_typ, value_typ=None):
    assert (arr_typ == string_array_type or arr_typ == binary_array_type
        ) and is_overload_constant_int(value_typ)

    def codegen(context, builder, sig, args):
        in_str_arr, value = args
        lmaw__shg = _get_str_binary_arr_payload(context, builder,
            in_str_arr, string_array_type)
        uakmt__ona = builder.udiv(builder.add(lmaw__shg.n_arrays, lir.
            Constant(lir.IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
        lyb__ojwg = context.make_array(null_bitmap_arr_type)(context,
            builder, lmaw__shg.null_bitmap).data
        cgutils.memset(builder, lyb__ojwg, uakmt__ona, value)
        return context.get_dummy_value()
    return types.none(arr_typ, types.int8), codegen


def _get_str_binary_arr_data_payload_ptr(context, builder, str_arr):
    mjn__subdt = context.make_helper(builder, string_array_type, str_arr)
    omoxn__twn = ArrayItemArrayType(char_arr_type)
    nxym__pavf = context.make_helper(builder, omoxn__twn, mjn__subdt.data)
    kig__youp = ArrayItemArrayPayloadType(omoxn__twn)
    sgq__lxua = context.nrt.meminfo_data(builder, nxym__pavf.meminfo)
    wufx__hjhgw = builder.bitcast(sgq__lxua, context.get_value_type(
        kig__youp).as_pointer())
    return wufx__hjhgw


@intrinsic
def move_str_binary_arr_payload(typingctx, to_arr_typ, from_arr_typ=None):
    assert to_arr_typ == string_array_type and from_arr_typ == string_array_type or to_arr_typ == binary_array_type and from_arr_typ == binary_array_type

    def codegen(context, builder, sig, args):
        mxkxv__glxl, nvfw__aeapn = args
        ezwy__ldtn = _get_str_binary_arr_data_payload_ptr(context, builder,
            nvfw__aeapn)
        enbk__sowef = _get_str_binary_arr_data_payload_ptr(context, builder,
            mxkxv__glxl)
        cxrkf__kipmd = _get_str_binary_arr_payload(context, builder,
            nvfw__aeapn, sig.args[1])
        petb__zknu = _get_str_binary_arr_payload(context, builder,
            mxkxv__glxl, sig.args[0])
        context.nrt.incref(builder, char_arr_type, cxrkf__kipmd.data)
        context.nrt.incref(builder, offset_arr_type, cxrkf__kipmd.offsets)
        context.nrt.incref(builder, null_bitmap_arr_type, cxrkf__kipmd.
            null_bitmap)
        context.nrt.decref(builder, char_arr_type, petb__zknu.data)
        context.nrt.decref(builder, offset_arr_type, petb__zknu.offsets)
        context.nrt.decref(builder, null_bitmap_arr_type, petb__zknu.
            null_bitmap)
        builder.store(builder.load(ezwy__ldtn), enbk__sowef)
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
        cxcd__sys = _get_utf8_size(s._data, s._length, s._kind)
        dummy_use(s)
        return cxcd__sys
    return impl


@intrinsic
def setitem_str_arr_ptr(typingctx, str_arr_t, ind_t, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        arr, ind, ahl__kvkof, efcf__pfus = args
        lmaw__shg = _get_str_binary_arr_payload(context, builder, arr, sig.
            args[0])
        offsets = context.make_helper(builder, offset_arr_type, lmaw__shg.
            offsets).data
        data = context.make_helper(builder, char_arr_type, lmaw__shg.data).data
        zhqwp__xhcvv = lir.FunctionType(lir.VoidType(), [lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(64),
            lir.IntType(32), lir.IntType(32), lir.IntType(64)])
        olm__cbqc = cgutils.get_or_insert_function(builder.module,
            zhqwp__xhcvv, name='setitem_string_array')
        jxsvc__fuj = context.get_constant(types.int32, -1)
        mzqg__lqqv = context.get_constant(types.int32, 1)
        num_total_chars = _get_num_total_chars(builder, offsets, lmaw__shg.
            n_arrays)
        builder.call(olm__cbqc, [offsets, data, num_total_chars, builder.
            extract_value(ahl__kvkof, 0), efcf__pfus, jxsvc__fuj,
            mzqg__lqqv, ind])
        return context.get_dummy_value()
    return types.void(str_arr_t, ind_t, ptr_t, len_t), codegen


def lower_is_na(context, builder, bull_bitmap, ind):
    zhqwp__xhcvv = lir.FunctionType(lir.IntType(1), [lir.IntType(8).
        as_pointer(), lir.IntType(64)])
    cya__yxb = cgutils.get_or_insert_function(builder.module, zhqwp__xhcvv,
        name='is_na')
    return builder.call(cya__yxb, [bull_bitmap, ind])


@intrinsic
def _memcpy(typingctx, dest_t, src_t, count_t, item_size_t=None):

    def codegen(context, builder, sig, args):
        flk__yon, nyqc__uuh, rlx__xygje, gdxgw__cbwf = args
        cgutils.raw_memcpy(builder, flk__yon, nyqc__uuh, rlx__xygje,
            gdxgw__cbwf)
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
        cny__xecgi, kasmz__deho = unicode_to_utf8_and_len(val)
        blkg__awxt = getitem_str_offset(A, ind)
        axulp__cpu = getitem_str_offset(A, ind + 1)
        qjf__lbts = axulp__cpu - blkg__awxt
        if qjf__lbts != kasmz__deho:
            return False
        ahl__kvkof = get_data_ptr_ind(A, blkg__awxt)
        return memcmp(ahl__kvkof, cny__xecgi, kasmz__deho) == 0
    return impl


def str_arr_setitem_int_to_str(A, ind, value):
    A[ind] = str(value)


@overload(str_arr_setitem_int_to_str)
def overload_str_arr_setitem_int_to_str(A, ind, val):

    def impl(A, ind, val):
        blkg__awxt = getitem_str_offset(A, ind)
        qjf__lbts = bodo.libs.str_ext.int_to_str_len(val)
        vgvuy__ljqho = blkg__awxt + qjf__lbts
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            blkg__awxt, vgvuy__ljqho)
        ahl__kvkof = get_data_ptr_ind(A, blkg__awxt)
        inplace_int64_to_str(ahl__kvkof, qjf__lbts, val)
        setitem_str_offset(A, ind + 1, blkg__awxt + qjf__lbts)
        str_arr_set_not_na(A, ind)
    return impl


@intrinsic
def inplace_set_NA_str(typingctx, ptr_typ=None):

    def codegen(context, builder, sig, args):
        ahl__kvkof, = args
        btcdx__jbdjr = context.insert_const_string(builder.module, '<NA>')
        hrti__ahx = lir.Constant(lir.IntType(64), len('<NA>'))
        cgutils.raw_memcpy(builder, ahl__kvkof, btcdx__jbdjr, hrti__ahx, 1)
    return types.none(types.voidptr), codegen


def str_arr_setitem_NA_str(A, ind):
    A[ind] = '<NA>'


@overload(str_arr_setitem_NA_str)
def overload_str_arr_setitem_NA_str(A, ind):
    womj__ari = len('<NA>')

    def impl(A, ind):
        blkg__awxt = getitem_str_offset(A, ind)
        vgvuy__ljqho = blkg__awxt + womj__ari
        bodo.libs.array_item_arr_ext.ensure_data_capacity(A._data,
            blkg__awxt, vgvuy__ljqho)
        ahl__kvkof = get_data_ptr_ind(A, blkg__awxt)
        inplace_set_NA_str(ahl__kvkof)
        setitem_str_offset(A, ind + 1, blkg__awxt + womj__ari)
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
            blkg__awxt = getitem_str_offset(A, ind)
            axulp__cpu = getitem_str_offset(A, ind + 1)
            efcf__pfus = axulp__cpu - blkg__awxt
            ahl__kvkof = get_data_ptr_ind(A, blkg__awxt)
            lxs__jtqv = decode_utf8(ahl__kvkof, efcf__pfus)
            return lxs__jtqv
        return str_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:

        def bool_impl(A, ind):
            ind = bodo.utils.conversion.coerce_to_ndarray(ind)
            cxcd__sys = len(A)
            n_strs = 0
            n_chars = 0
            for i in range(cxcd__sys):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    n_strs += 1
                    n_chars += get_str_arr_item_length(A, i)
            out_arr = pre_alloc_string_array(n_strs, n_chars)
            ftgb__eyzs = get_data_ptr(out_arr).data
            vuq__emr = get_data_ptr(A).data
            xspi__ethv = 0
            luuok__jhxn = 0
            setitem_str_offset(out_arr, 0, 0)
            for i in range(cxcd__sys):
                if not bodo.libs.array_kernels.isna(ind, i) and ind[i]:
                    aced__ryzy = get_str_arr_item_length(A, i)
                    if aced__ryzy == 1:
                        copy_single_char(ftgb__eyzs, luuok__jhxn, vuq__emr,
                            getitem_str_offset(A, i))
                    else:
                        memcpy_region(ftgb__eyzs, luuok__jhxn, vuq__emr,
                            getitem_str_offset(A, i), aced__ryzy, 1)
                    luuok__jhxn += aced__ryzy
                    setitem_str_offset(out_arr, xspi__ethv + 1, luuok__jhxn)
                    if str_arr_is_na(A, i):
                        str_arr_set_na(out_arr, xspi__ethv)
                    else:
                        str_arr_set_not_na(out_arr, xspi__ethv)
                    xspi__ethv += 1
            return out_arr
        return bool_impl
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):

        def str_arr_arr_impl(A, ind):
            cxcd__sys = len(ind)
            out_arr = pre_alloc_string_array(cxcd__sys, -1)
            xspi__ethv = 0
            for i in range(cxcd__sys):
                ctb__ybea = A[ind[i]]
                out_arr[xspi__ethv] = ctb__ybea
                if str_arr_is_na(A, ind[i]):
                    str_arr_set_na(out_arr, xspi__ethv)
                xspi__ethv += 1
            return out_arr
        return str_arr_arr_impl
    if isinstance(ind, types.SliceType):

        def str_arr_slice_impl(A, ind):
            cxcd__sys = len(A)
            nkn__fwssj = numba.cpython.unicode._normalize_slice(ind, cxcd__sys)
            wmzt__netvk = numba.cpython.unicode._slice_span(nkn__fwssj)
            if nkn__fwssj.step == 1:
                blkg__awxt = getitem_str_offset(A, nkn__fwssj.start)
                axulp__cpu = getitem_str_offset(A, nkn__fwssj.stop)
                n_chars = axulp__cpu - blkg__awxt
                idxs__vjouy = pre_alloc_string_array(wmzt__netvk, np.int64(
                    n_chars))
                for i in range(wmzt__netvk):
                    idxs__vjouy[i] = A[nkn__fwssj.start + i]
                    if str_arr_is_na(A, nkn__fwssj.start + i):
                        str_arr_set_na(idxs__vjouy, i)
                return idxs__vjouy
            else:
                idxs__vjouy = pre_alloc_string_array(wmzt__netvk, -1)
                for i in range(wmzt__netvk):
                    idxs__vjouy[i] = A[nkn__fwssj.start + i * nkn__fwssj.step]
                    if str_arr_is_na(A, nkn__fwssj.start + i * nkn__fwssj.step
                        ):
                        str_arr_set_na(idxs__vjouy, i)
                return idxs__vjouy
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
    troc__bzk = (
        f'StringArray setitem with index {idx} and value {val} not supported yet.'
        )
    if isinstance(idx, types.Integer):
        if val != string_type:
            raise BodoError(troc__bzk)
        nhea__urqir = 4

        def impl_scalar(A, idx, val):
            fomi__gijmo = (val._length if val._is_ascii else nhea__urqir *
                val._length)
            mivg__jipko = A._data
            blkg__awxt = np.int64(getitem_str_offset(A, idx))
            vgvuy__ljqho = blkg__awxt + fomi__gijmo
            bodo.libs.array_item_arr_ext.ensure_data_capacity(mivg__jipko,
                blkg__awxt, vgvuy__ljqho)
            setitem_string_array(get_offset_ptr(A), get_data_ptr(A),
                vgvuy__ljqho, val._data, val._length, val._kind, val.
                _is_ascii, idx)
            str_arr_set_not_na(A, idx)
            dummy_use(A)
            dummy_use(val)
        return impl_scalar
    if isinstance(idx, types.SliceType):
        if val == string_array_type:

            def impl_slice(A, idx, val):
                nkn__fwssj = numba.cpython.unicode._normalize_slice(idx, len(A)
                    )
                jkuxk__cuex = nkn__fwssj.start
                mivg__jipko = A._data
                blkg__awxt = np.int64(getitem_str_offset(A, jkuxk__cuex))
                vgvuy__ljqho = blkg__awxt + np.int64(num_total_chars(val))
                bodo.libs.array_item_arr_ext.ensure_data_capacity(mivg__jipko,
                    blkg__awxt, vgvuy__ljqho)
                set_string_array_range(A, val, jkuxk__cuex, blkg__awxt)
                ljpd__obnvd = 0
                for i in range(nkn__fwssj.start, nkn__fwssj.stop,
                    nkn__fwssj.step):
                    if str_arr_is_na(val, ljpd__obnvd):
                        str_arr_set_na(A, i)
                    else:
                        str_arr_set_not_na(A, i)
                    ljpd__obnvd += 1
            return impl_slice
        elif isinstance(val, types.List) and val.dtype == string_type:

            def impl_slice_list(A, idx, val):
                qdff__pcea = str_list_to_array(val)
                A[idx] = qdff__pcea
            return impl_slice_list
        elif val == string_type:

            def impl_slice(A, idx, val):
                nkn__fwssj = numba.cpython.unicode._normalize_slice(idx, len(A)
                    )
                for i in range(nkn__fwssj.start, nkn__fwssj.stop,
                    nkn__fwssj.step):
                    A[i] = val
            return impl_slice
        else:
            raise BodoError(troc__bzk)
    if is_list_like_index_type(idx) and idx.dtype == types.bool_:
        if val == string_type:

            def impl_bool_scalar(A, idx, val):
                cxcd__sys = len(A)
                idx = bodo.utils.conversion.coerce_to_ndarray(idx)
                out_arr = pre_alloc_string_array(cxcd__sys, -1)
                for i in numba.parfors.parfor.internal_prange(cxcd__sys):
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
                cxcd__sys = len(A)
                idx = bodo.utils.conversion.coerce_to_array(idx,
                    use_nullable_array=True)
                out_arr = pre_alloc_string_array(cxcd__sys, -1)
                ecjrw__meevv = 0
                for i in numba.parfors.parfor.internal_prange(cxcd__sys):
                    if not bodo.libs.array_kernels.isna(idx, i) and idx[i]:
                        if bodo.libs.array_kernels.isna(val, ecjrw__meevv):
                            out_arr[i] = ''
                            str_arr_set_na(out_arr, ecjrw__meevv)
                        else:
                            out_arr[i] = str(val[ecjrw__meevv])
                        ecjrw__meevv += 1
                    elif bodo.libs.array_kernels.isna(A, i):
                        out_arr[i] = ''
                        str_arr_set_na(out_arr, i)
                    else:
                        get_str_arr_item_copy(out_arr, i, A, i)
                move_str_binary_arr_payload(A, out_arr)
            return impl_bool_arr
        else:
            raise BodoError(troc__bzk)
    raise BodoError(troc__bzk)


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
    kfg__irh = parse_dtype(dtype, 'StringArray.astype')
    if not isinstance(kfg__irh, (types.Float, types.Integer)):
        raise BodoError('invalid dtype in StringArray.astype()')
    if isinstance(kfg__irh, types.Float):

        def impl_float(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            cxcd__sys = len(A)
            B = np.empty(cxcd__sys, kfg__irh)
            for i in numba.parfors.parfor.internal_prange(cxcd__sys):
                if bodo.libs.array_kernels.isna(A, i):
                    B[i] = np.nan
                else:
                    B[i] = float(A[i])
            return B
        return impl_float
    else:

        def impl_int(A, dtype, copy=True):
            numba.parfors.parfor.init_prange()
            cxcd__sys = len(A)
            B = np.empty(cxcd__sys, kfg__irh)
            for i in numba.parfors.parfor.internal_prange(cxcd__sys):
                B[i] = int(A[i])
            return B
        return impl_int


@intrinsic
def decode_utf8(typingctx, ptr_t, len_t=None):

    def codegen(context, builder, sig, args):
        ahl__kvkof, efcf__pfus = args
        get__kyo = context.get_python_api(builder)
        hem__laa = get__kyo.string_from_string_and_size(ahl__kvkof, efcf__pfus)
        ttaz__xdid = get__kyo.to_native_value(string_type, hem__laa).value
        zykum__rabji = cgutils.create_struct_proxy(string_type)(context,
            builder, ttaz__xdid)
        zykum__rabji.hash = zykum__rabji.hash.type(-1)
        get__kyo.decref(hem__laa)
        return zykum__rabji._getvalue()
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
        ewbm__bnlnx, arr, ind, tcmq__kne = args
        lmaw__shg = _get_str_binary_arr_payload(context, builder, arr,
            string_array_type)
        offsets = context.make_helper(builder, offset_arr_type, lmaw__shg.
            offsets).data
        data = context.make_helper(builder, char_arr_type, lmaw__shg.data).data
        zhqwp__xhcvv = lir.FunctionType(lir.IntType(32), [ewbm__bnlnx.type,
            lir.IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(64)])
        geu__vrxqc = 'str_arr_to_int64'
        if sig.args[3].dtype == types.float64:
            geu__vrxqc = 'str_arr_to_float64'
        else:
            assert sig.args[3].dtype == types.int64
        dfkq__cwqoq = cgutils.get_or_insert_function(builder.module,
            zhqwp__xhcvv, geu__vrxqc)
        return builder.call(dfkq__cwqoq, [ewbm__bnlnx, offsets, data, ind])
    return types.int32(out_ptr_t, string_array_type, types.int64, out_dtype_t
        ), codegen


@unbox(BinaryArrayType)
@unbox(StringArrayType)
def unbox_str_series(typ, val, c):
    snpj__gtl = c.context.get_constant(types.int32, int(typ ==
        binary_array_type))
    zhqwp__xhcvv = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer(), lir.IntType(32)])
    bksvo__fptm = cgutils.get_or_insert_function(c.builder.module,
        zhqwp__xhcvv, name='string_array_from_sequence')
    lfik__wran = c.builder.call(bksvo__fptm, [val, snpj__gtl])
    omoxn__twn = ArrayItemArrayType(char_arr_type)
    nxym__pavf = c.context.make_helper(c.builder, omoxn__twn)
    nxym__pavf.meminfo = lfik__wran
    mjn__subdt = c.context.make_helper(c.builder, typ)
    mivg__jipko = nxym__pavf._getvalue()
    mjn__subdt.data = mivg__jipko
    sqep__gtt = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(mjn__subdt._getvalue(), is_error=sqep__gtt)


@lower_constant(BinaryArrayType)
@lower_constant(StringArrayType)
def lower_constant_str_arr(context, builder, typ, pyval):
    cxcd__sys = len(pyval)
    luuok__jhxn = 0
    djzsh__votn = np.empty(cxcd__sys + 1, np_offset_type)
    opsta__sai = []
    rnyhh__nzq = np.empty(cxcd__sys + 7 >> 3, np.uint8)
    for i, s in enumerate(pyval):
        djzsh__votn[i] = luuok__jhxn
        xcyj__lni = pd.isna(s)
        bodo.libs.int_arr_ext.set_bit_to_arr(rnyhh__nzq, i, int(not xcyj__lni))
        if xcyj__lni:
            continue
        pejo__yrfc = list(s.encode()) if isinstance(s, str) else list(s)
        opsta__sai.extend(pejo__yrfc)
        luuok__jhxn += len(pejo__yrfc)
    djzsh__votn[cxcd__sys] = luuok__jhxn
    lmf__huajx = np.array(opsta__sai, np.uint8)
    ejdhb__fne = context.get_constant(types.int64, cxcd__sys)
    ddr__abz = context.get_constant_generic(builder, char_arr_type, lmf__huajx)
    fsvzq__jyxax = context.get_constant_generic(builder, offset_arr_type,
        djzsh__votn)
    xfa__vye = context.get_constant_generic(builder, null_bitmap_arr_type,
        rnyhh__nzq)
    lmaw__shg = lir.Constant.literal_struct([ejdhb__fne, ddr__abz,
        fsvzq__jyxax, xfa__vye])
    lmaw__shg = cgutils.global_constant(builder, '.const.payload', lmaw__shg
        ).bitcast(cgutils.voidptr_t)
    vwnb__utiap = context.get_constant(types.int64, -1)
    quuyq__ugn = context.get_constant_null(types.voidptr)
    rzngj__oxhnm = lir.Constant.literal_struct([vwnb__utiap, quuyq__ugn,
        quuyq__ugn, lmaw__shg, vwnb__utiap])
    rzngj__oxhnm = cgutils.global_constant(builder, '.const.meminfo',
        rzngj__oxhnm).bitcast(cgutils.voidptr_t)
    mivg__jipko = lir.Constant.literal_struct([rzngj__oxhnm])
    mjn__subdt = lir.Constant.literal_struct([mivg__jipko])
    return mjn__subdt


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
