import operator
import llvmlite.binding as ll
import numba
import numba.core.typing.typeof
import numpy as np
from llvmlite import ir as lir
from llvmlite.llvmpy.core import Type as LLType
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed, impl_ret_new_ref
from numba.extending import box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, register_model
import bodo
from bodo.libs import hstr_ext
from bodo.libs.array_item_arr_ext import offset_type
from bodo.libs.str_arr_ext import _get_str_binary_arr_payload, _memcpy, char_arr_type, get_data_ptr, null_bitmap_arr_type, offset_arr_type, string_array_type
ll.add_symbol('array_setitem', hstr_ext.array_setitem)
ll.add_symbol('array_getptr1', hstr_ext.array_getptr1)
ll.add_symbol('dtor_str_arr_split_view', hstr_ext.dtor_str_arr_split_view)
ll.add_symbol('str_arr_split_view_impl', hstr_ext.str_arr_split_view_impl)
ll.add_symbol('str_arr_split_view_alloc', hstr_ext.str_arr_split_view_alloc)
char_typ = types.uint8
data_ctypes_type = types.ArrayCTypes(types.Array(char_typ, 1, 'C'))
offset_ctypes_type = types.ArrayCTypes(types.Array(offset_type, 1, 'C'))


class StringArraySplitViewType(types.ArrayCompatible):

    def __init__(self):
        super(StringArraySplitViewType, self).__init__(name=
            'StringArraySplitViewType()')

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return string_array_type

    def copy(self):
        return StringArraySplitViewType()


string_array_split_view_type = StringArraySplitViewType()


class StringArraySplitViewPayloadType(types.Type):

    def __init__(self):
        super(StringArraySplitViewPayloadType, self).__init__(name=
            'StringArraySplitViewPayloadType()')


str_arr_split_view_payload_type = StringArraySplitViewPayloadType()


@register_model(StringArraySplitViewPayloadType)
class StringArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        efya__hwuc = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, efya__hwuc)


str_arr_model_members = [('num_items', types.uint64), ('index_offsets',
    types.CPointer(offset_type)), ('data_offsets', types.CPointer(
    offset_type)), ('data', data_ctypes_type), ('null_bitmap', types.
    CPointer(char_typ)), ('meminfo', types.MemInfoPointer(
    str_arr_split_view_payload_type))]


@register_model(StringArraySplitViewType)
class StringArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        models.StructModel.__init__(self, dmm, fe_type, str_arr_model_members)


make_attribute_wrapper(StringArraySplitViewType, 'num_items', '_num_items')
make_attribute_wrapper(StringArraySplitViewType, 'index_offsets',
    '_index_offsets')
make_attribute_wrapper(StringArraySplitViewType, 'data_offsets',
    '_data_offsets')
make_attribute_wrapper(StringArraySplitViewType, 'data', '_data')
make_attribute_wrapper(StringArraySplitViewType, 'null_bitmap', '_null_bitmap')


def construct_str_arr_split_view(context, builder):
    wtqt__zimj = context.get_value_type(str_arr_split_view_payload_type)
    tjn__lsngc = context.get_abi_sizeof(wtqt__zimj)
    tjvop__oxge = context.get_value_type(types.voidptr)
    lexgi__yhzc = context.get_value_type(types.uintp)
    rpqk__jwnu = lir.FunctionType(lir.VoidType(), [tjvop__oxge, lexgi__yhzc,
        tjvop__oxge])
    hfby__vtp = cgutils.get_or_insert_function(builder.module, rpqk__jwnu,
        name='dtor_str_arr_split_view')
    ezl__xgfet = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, tjn__lsngc), hfby__vtp)
    saiyk__tvqv = context.nrt.meminfo_data(builder, ezl__xgfet)
    tlu__pthfc = builder.bitcast(saiyk__tvqv, wtqt__zimj.as_pointer())
    return ezl__xgfet, tlu__pthfc


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        sdw__ktd, mnn__jwdn = args
        ezl__xgfet, tlu__pthfc = construct_str_arr_split_view(context, builder)
        urn__rlpo = _get_str_binary_arr_payload(context, builder, sdw__ktd,
            string_array_type)
        zzw__suqo = lir.FunctionType(lir.VoidType(), [tlu__pthfc.type, lir.
            IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        zcv__cisbb = cgutils.get_or_insert_function(builder.module,
            zzw__suqo, name='str_arr_split_view_impl')
        uxg__ogzsa = context.make_helper(builder, offset_arr_type,
            urn__rlpo.offsets).data
        ksk__bjnc = context.make_helper(builder, char_arr_type, urn__rlpo.data
            ).data
        qhoxj__howwp = context.make_helper(builder, null_bitmap_arr_type,
            urn__rlpo.null_bitmap).data
        wpdtf__yiy = context.get_constant(types.int8, ord(sep_typ.
            literal_value))
        builder.call(zcv__cisbb, [tlu__pthfc, urn__rlpo.n_arrays,
            uxg__ogzsa, ksk__bjnc, qhoxj__howwp, wpdtf__yiy])
        zeum__vsj = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(tlu__pthfc))
        yudho__jgaeq = context.make_helper(builder,
            string_array_split_view_type)
        yudho__jgaeq.num_items = urn__rlpo.n_arrays
        yudho__jgaeq.index_offsets = zeum__vsj.index_offsets
        yudho__jgaeq.data_offsets = zeum__vsj.data_offsets
        yudho__jgaeq.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [sdw__ktd])
        yudho__jgaeq.null_bitmap = zeum__vsj.null_bitmap
        yudho__jgaeq.meminfo = ezl__xgfet
        kafm__dbb = yudho__jgaeq._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, kafm__dbb)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    kkan__fcv = context.make_helper(builder, string_array_split_view_type, val)
    mmg__wucr = context.insert_const_string(builder.module, 'numpy')
    dksm__qda = c.pyapi.import_module_noblock(mmg__wucr)
    dtype = c.pyapi.object_getattr_string(dksm__qda, 'object_')
    sqex__tnvmg = builder.sext(kkan__fcv.num_items, c.pyapi.longlong)
    pzc__xezf = c.pyapi.long_from_longlong(sqex__tnvmg)
    rwsl__jyyd = c.pyapi.call_method(dksm__qda, 'ndarray', (pzc__xezf, dtype))
    rjrz__qpon = LLType.function(lir.IntType(8).as_pointer(), [c.pyapi.
        pyobj, c.pyapi.py_ssize_t])
    tkjh__wjv = c.pyapi._get_function(rjrz__qpon, name='array_getptr1')
    cgv__jsxzs = LLType.function(lir.VoidType(), [c.pyapi.pyobj, lir.
        IntType(8).as_pointer(), c.pyapi.pyobj])
    kvz__oof = c.pyapi._get_function(cgv__jsxzs, name='array_setitem')
    hxka__old = c.pyapi.object_getattr_string(dksm__qda, 'nan')
    with cgutils.for_range(builder, kkan__fcv.num_items) as loop:
        str_ind = loop.index
        qpe__rfv = builder.sext(builder.load(builder.gep(kkan__fcv.
            index_offsets, [str_ind])), lir.IntType(64))
        zuaq__pah = builder.sext(builder.load(builder.gep(kkan__fcv.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        ggxe__mzczo = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        gcvqb__xqsu = builder.gep(kkan__fcv.null_bitmap, [ggxe__mzczo])
        nmeay__ywz = builder.load(gcvqb__xqsu)
        iws__nzsu = builder.trunc(builder.and_(str_ind, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(nmeay__ywz, iws__nzsu), lir.
            Constant(lir.IntType(8), 1))
        xfavn__xen = builder.sub(zuaq__pah, qpe__rfv)
        xfavn__xen = builder.sub(xfavn__xen, xfavn__xen.type(1))
        rzg__mbd = builder.call(tkjh__wjv, [rwsl__jyyd, str_ind])
        wzhpr__ayjo = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(wzhpr__ayjo) as (then, otherwise):
            with then:
                rji__vufj = c.pyapi.list_new(xfavn__xen)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    rji__vufj), likely=True):
                    with cgutils.for_range(c.builder, xfavn__xen) as loop:
                        uvbrn__xmmk = builder.add(qpe__rfv, loop.index)
                        data_start = builder.load(builder.gep(kkan__fcv.
                            data_offsets, [uvbrn__xmmk]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        qojm__qyrxw = builder.load(builder.gep(kkan__fcv.
                            data_offsets, [builder.add(uvbrn__xmmk,
                            uvbrn__xmmk.type(1))]))
                        irbrh__odt = builder.gep(builder.extract_value(
                            kkan__fcv.data, 0), [data_start])
                        hbsv__sngr = builder.sext(builder.sub(qojm__qyrxw,
                            data_start), lir.IntType(64))
                        rxzd__hegou = c.pyapi.string_from_string_and_size(
                            irbrh__odt, hbsv__sngr)
                        c.pyapi.list_setitem(rji__vufj, loop.index, rxzd__hegou
                            )
                builder.call(kvz__oof, [rwsl__jyyd, rzg__mbd, rji__vufj])
            with otherwise:
                builder.call(kvz__oof, [rwsl__jyyd, rzg__mbd, hxka__old])
    c.pyapi.decref(dksm__qda)
    c.pyapi.decref(dtype)
    c.pyapi.decref(hxka__old)
    return rwsl__jyyd


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        xooi__ahidg, qav__cvld, irbrh__odt = args
        ezl__xgfet, tlu__pthfc = construct_str_arr_split_view(context, builder)
        zzw__suqo = lir.FunctionType(lir.VoidType(), [tlu__pthfc.type, lir.
            IntType(64), lir.IntType(64)])
        zcv__cisbb = cgutils.get_or_insert_function(builder.module,
            zzw__suqo, name='str_arr_split_view_alloc')
        builder.call(zcv__cisbb, [tlu__pthfc, xooi__ahidg, qav__cvld])
        zeum__vsj = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(tlu__pthfc))
        yudho__jgaeq = context.make_helper(builder,
            string_array_split_view_type)
        yudho__jgaeq.num_items = xooi__ahidg
        yudho__jgaeq.index_offsets = zeum__vsj.index_offsets
        yudho__jgaeq.data_offsets = zeum__vsj.data_offsets
        yudho__jgaeq.data = irbrh__odt
        yudho__jgaeq.null_bitmap = zeum__vsj.null_bitmap
        context.nrt.incref(builder, data_t, irbrh__odt)
        yudho__jgaeq.meminfo = ezl__xgfet
        kafm__dbb = yudho__jgaeq._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, kafm__dbb)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        yzvl__tdj, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            yzvl__tdj = builder.extract_value(yzvl__tdj, 0)
        return builder.bitcast(builder.gep(yzvl__tdj, [ind]), lir.IntType(8
            ).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        yzvl__tdj, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            yzvl__tdj = builder.extract_value(yzvl__tdj, 0)
        return builder.load(builder.gep(yzvl__tdj, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        yzvl__tdj, ind, vuxou__zfowz = args
        yua__oqwhg = builder.gep(yzvl__tdj, [ind])
        builder.store(vuxou__zfowz, yua__oqwhg)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        szl__ieupk, ind = args
        wglm__dwon = context.make_helper(builder, arr_ctypes_t, szl__ieupk)
        rtswj__tjc = context.make_helper(builder, arr_ctypes_t)
        rtswj__tjc.data = builder.gep(wglm__dwon.data, [ind])
        rtswj__tjc.meminfo = wglm__dwon.meminfo
        yneo__djyy = rtswj__tjc._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, yneo__djyy)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    fifjn__jpxz = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr._null_bitmap,
        item_ind)
    if not fifjn__jpxz:
        return 0, 0, 0
    uvbrn__xmmk = getitem_c_arr(arr._index_offsets, item_ind)
    aloq__uisur = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    gld__kam = aloq__uisur - uvbrn__xmmk
    if str_ind >= gld__kam:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, uvbrn__xmmk + str_ind)
    data_start += 1
    if uvbrn__xmmk + str_ind == 0:
        data_start = 0
    qojm__qyrxw = getitem_c_arr(arr._data_offsets, uvbrn__xmmk + str_ind + 1)
    geraf__dofjq = qojm__qyrxw - data_start
    return 1, data_start, geraf__dofjq


@numba.njit(no_cpython_wrapper=True)
def get_split_view_data_ptr(arr, data_start):
    return get_array_ctypes_ptr(arr._data, data_start)


@overload(len, no_unliteral=True)
def str_arr_split_view_len_overload(arr):
    if arr == string_array_split_view_type:
        return lambda arr: np.int64(arr._num_items)


@overload_attribute(StringArraySplitViewType, 'shape')
def overload_split_view_arr_shape(A):
    return lambda A: (np.int64(A._num_items),)


@overload(operator.getitem, no_unliteral=True)
def str_arr_split_view_getitem_overload(A, ind):
    if A != string_array_split_view_type:
        return
    if A == string_array_split_view_type and isinstance(ind, types.Integer):
        ngwq__kqxq = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            uvbrn__xmmk = getitem_c_arr(A._index_offsets, ind)
            aloq__uisur = getitem_c_arr(A._index_offsets, ind + 1)
            bxh__til = aloq__uisur - uvbrn__xmmk - 1
            sdw__ktd = bodo.libs.str_arr_ext.pre_alloc_string_array(bxh__til,
                -1)
            for ryqp__kyd in range(bxh__til):
                data_start = getitem_c_arr(A._data_offsets, uvbrn__xmmk +
                    ryqp__kyd)
                data_start += 1
                if uvbrn__xmmk + ryqp__kyd == 0:
                    data_start = 0
                qojm__qyrxw = getitem_c_arr(A._data_offsets, uvbrn__xmmk +
                    ryqp__kyd + 1)
                geraf__dofjq = qojm__qyrxw - data_start
                yua__oqwhg = get_array_ctypes_ptr(A._data, data_start)
                lxu__zxu = bodo.libs.str_arr_ext.decode_utf8(yua__oqwhg,
                    geraf__dofjq)
                sdw__ktd[ryqp__kyd] = lxu__zxu
            return sdw__ktd
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        aec__oylo = offset_type.bitwidth // 8

        def _impl(A, ind):
            bxh__til = len(A)
            if bxh__til != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            xooi__ahidg = 0
            qav__cvld = 0
            for ryqp__kyd in range(bxh__til):
                if ind[ryqp__kyd]:
                    xooi__ahidg += 1
                    uvbrn__xmmk = getitem_c_arr(A._index_offsets, ryqp__kyd)
                    aloq__uisur = getitem_c_arr(A._index_offsets, ryqp__kyd + 1
                        )
                    qav__cvld += aloq__uisur - uvbrn__xmmk
            rwsl__jyyd = pre_alloc_str_arr_view(xooi__ahidg, qav__cvld, A._data
                )
            item_ind = 0
            peee__iduwu = 0
            for ryqp__kyd in range(bxh__til):
                if ind[ryqp__kyd]:
                    uvbrn__xmmk = getitem_c_arr(A._index_offsets, ryqp__kyd)
                    aloq__uisur = getitem_c_arr(A._index_offsets, ryqp__kyd + 1
                        )
                    vwppb__utq = aloq__uisur - uvbrn__xmmk
                    setitem_c_arr(rwsl__jyyd._index_offsets, item_ind,
                        peee__iduwu)
                    yua__oqwhg = get_c_arr_ptr(A._data_offsets, uvbrn__xmmk)
                    dcbd__mehy = get_c_arr_ptr(rwsl__jyyd._data_offsets,
                        peee__iduwu)
                    _memcpy(dcbd__mehy, yua__oqwhg, vwppb__utq, aec__oylo)
                    fifjn__jpxz = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, ryqp__kyd)
                    bodo.libs.int_arr_ext.set_bit_to_arr(rwsl__jyyd.
                        _null_bitmap, item_ind, fifjn__jpxz)
                    item_ind += 1
                    peee__iduwu += vwppb__utq
            setitem_c_arr(rwsl__jyyd._index_offsets, item_ind, peee__iduwu)
            return rwsl__jyyd
        return _impl
