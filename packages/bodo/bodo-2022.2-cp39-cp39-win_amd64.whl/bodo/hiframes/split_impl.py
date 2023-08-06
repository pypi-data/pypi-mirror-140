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
        kmute__pqeu = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, kmute__pqeu)


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
    nbg__xsls = context.get_value_type(str_arr_split_view_payload_type)
    gnwfd__ytj = context.get_abi_sizeof(nbg__xsls)
    belav__lns = context.get_value_type(types.voidptr)
    kjtg__zdbve = context.get_value_type(types.uintp)
    ayjiq__skus = lir.FunctionType(lir.VoidType(), [belav__lns, kjtg__zdbve,
        belav__lns])
    ggic__gvwoi = cgutils.get_or_insert_function(builder.module,
        ayjiq__skus, name='dtor_str_arr_split_view')
    natl__kjuiv = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, gnwfd__ytj), ggic__gvwoi)
    luax__pqzmn = context.nrt.meminfo_data(builder, natl__kjuiv)
    gcl__yzd = builder.bitcast(luax__pqzmn, nbg__xsls.as_pointer())
    return natl__kjuiv, gcl__yzd


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        dkmj__ixnf, xdx__jns = args
        natl__kjuiv, gcl__yzd = construct_str_arr_split_view(context, builder)
        wln__vwjg = _get_str_binary_arr_payload(context, builder,
            dkmj__ixnf, string_array_type)
        iljd__apyw = lir.FunctionType(lir.VoidType(), [gcl__yzd.type, lir.
            IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        cdpfd__iqcuw = cgutils.get_or_insert_function(builder.module,
            iljd__apyw, name='str_arr_split_view_impl')
        lbe__qkpy = context.make_helper(builder, offset_arr_type, wln__vwjg
            .offsets).data
        slqh__jxwmj = context.make_helper(builder, char_arr_type, wln__vwjg
            .data).data
        ihdu__ztg = context.make_helper(builder, null_bitmap_arr_type,
            wln__vwjg.null_bitmap).data
        utp__iqt = context.get_constant(types.int8, ord(sep_typ.literal_value))
        builder.call(cdpfd__iqcuw, [gcl__yzd, wln__vwjg.n_arrays, lbe__qkpy,
            slqh__jxwmj, ihdu__ztg, utp__iqt])
        ioos__mhrai = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(gcl__yzd))
        ahhbq__nfhjr = context.make_helper(builder,
            string_array_split_view_type)
        ahhbq__nfhjr.num_items = wln__vwjg.n_arrays
        ahhbq__nfhjr.index_offsets = ioos__mhrai.index_offsets
        ahhbq__nfhjr.data_offsets = ioos__mhrai.data_offsets
        ahhbq__nfhjr.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [dkmj__ixnf])
        ahhbq__nfhjr.null_bitmap = ioos__mhrai.null_bitmap
        ahhbq__nfhjr.meminfo = natl__kjuiv
        hmx__nuzg = ahhbq__nfhjr._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, hmx__nuzg)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    nlq__gnkg = context.make_helper(builder, string_array_split_view_type, val)
    jhfoc__lbf = context.insert_const_string(builder.module, 'numpy')
    akle__rrnuv = c.pyapi.import_module_noblock(jhfoc__lbf)
    dtype = c.pyapi.object_getattr_string(akle__rrnuv, 'object_')
    cxq__lsrag = builder.sext(nlq__gnkg.num_items, c.pyapi.longlong)
    iysgb__ikb = c.pyapi.long_from_longlong(cxq__lsrag)
    uom__idv = c.pyapi.call_method(akle__rrnuv, 'ndarray', (iysgb__ikb, dtype))
    kvw__ftl = LLType.function(lir.IntType(8).as_pointer(), [c.pyapi.pyobj,
        c.pyapi.py_ssize_t])
    ldplq__wqqmn = c.pyapi._get_function(kvw__ftl, name='array_getptr1')
    weigk__duul = LLType.function(lir.VoidType(), [c.pyapi.pyobj, lir.
        IntType(8).as_pointer(), c.pyapi.pyobj])
    wpqa__noqp = c.pyapi._get_function(weigk__duul, name='array_setitem')
    qzw__rmdc = c.pyapi.object_getattr_string(akle__rrnuv, 'nan')
    with cgutils.for_range(builder, nlq__gnkg.num_items) as loop:
        str_ind = loop.index
        wzwev__sck = builder.sext(builder.load(builder.gep(nlq__gnkg.
            index_offsets, [str_ind])), lir.IntType(64))
        iexr__jkwu = builder.sext(builder.load(builder.gep(nlq__gnkg.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        cnp__kdzl = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        acsr__gdep = builder.gep(nlq__gnkg.null_bitmap, [cnp__kdzl])
        nme__xyleu = builder.load(acsr__gdep)
        jgj__vqpv = builder.trunc(builder.and_(str_ind, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(nme__xyleu, jgj__vqpv), lir.
            Constant(lir.IntType(8), 1))
        hmvzg__ulezb = builder.sub(iexr__jkwu, wzwev__sck)
        hmvzg__ulezb = builder.sub(hmvzg__ulezb, hmvzg__ulezb.type(1))
        fykn__vlfb = builder.call(ldplq__wqqmn, [uom__idv, str_ind])
        nbym__yhk = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(nbym__yhk) as (then, otherwise):
            with then:
                izn__dext = c.pyapi.list_new(hmvzg__ulezb)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    izn__dext), likely=True):
                    with cgutils.for_range(c.builder, hmvzg__ulezb) as loop:
                        vsi__yaty = builder.add(wzwev__sck, loop.index)
                        data_start = builder.load(builder.gep(nlq__gnkg.
                            data_offsets, [vsi__yaty]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        csq__cajw = builder.load(builder.gep(nlq__gnkg.
                            data_offsets, [builder.add(vsi__yaty, vsi__yaty
                            .type(1))]))
                        eyjom__qqu = builder.gep(builder.extract_value(
                            nlq__gnkg.data, 0), [data_start])
                        immf__fsqdp = builder.sext(builder.sub(csq__cajw,
                            data_start), lir.IntType(64))
                        isy__ejcev = c.pyapi.string_from_string_and_size(
                            eyjom__qqu, immf__fsqdp)
                        c.pyapi.list_setitem(izn__dext, loop.index, isy__ejcev)
                builder.call(wpqa__noqp, [uom__idv, fykn__vlfb, izn__dext])
            with otherwise:
                builder.call(wpqa__noqp, [uom__idv, fykn__vlfb, qzw__rmdc])
    c.pyapi.decref(akle__rrnuv)
    c.pyapi.decref(dtype)
    c.pyapi.decref(qzw__rmdc)
    return uom__idv


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        ieq__bbyxx, hblt__wot, eyjom__qqu = args
        natl__kjuiv, gcl__yzd = construct_str_arr_split_view(context, builder)
        iljd__apyw = lir.FunctionType(lir.VoidType(), [gcl__yzd.type, lir.
            IntType(64), lir.IntType(64)])
        cdpfd__iqcuw = cgutils.get_or_insert_function(builder.module,
            iljd__apyw, name='str_arr_split_view_alloc')
        builder.call(cdpfd__iqcuw, [gcl__yzd, ieq__bbyxx, hblt__wot])
        ioos__mhrai = cgutils.create_struct_proxy(
            str_arr_split_view_payload_type)(context, builder, value=
            builder.load(gcl__yzd))
        ahhbq__nfhjr = context.make_helper(builder,
            string_array_split_view_type)
        ahhbq__nfhjr.num_items = ieq__bbyxx
        ahhbq__nfhjr.index_offsets = ioos__mhrai.index_offsets
        ahhbq__nfhjr.data_offsets = ioos__mhrai.data_offsets
        ahhbq__nfhjr.data = eyjom__qqu
        ahhbq__nfhjr.null_bitmap = ioos__mhrai.null_bitmap
        context.nrt.incref(builder, data_t, eyjom__qqu)
        ahhbq__nfhjr.meminfo = natl__kjuiv
        hmx__nuzg = ahhbq__nfhjr._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, hmx__nuzg)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        weype__ibwqd, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            weype__ibwqd = builder.extract_value(weype__ibwqd, 0)
        return builder.bitcast(builder.gep(weype__ibwqd, [ind]), lir.
            IntType(8).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        weype__ibwqd, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            weype__ibwqd = builder.extract_value(weype__ibwqd, 0)
        return builder.load(builder.gep(weype__ibwqd, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        weype__ibwqd, ind, gdfv__qdpai = args
        chnhh__mxzb = builder.gep(weype__ibwqd, [ind])
        builder.store(gdfv__qdpai, chnhh__mxzb)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        dqun__svs, ind = args
        outu__bhnlk = context.make_helper(builder, arr_ctypes_t, dqun__svs)
        caklq__rlozx = context.make_helper(builder, arr_ctypes_t)
        caklq__rlozx.data = builder.gep(outu__bhnlk.data, [ind])
        caklq__rlozx.meminfo = outu__bhnlk.meminfo
        sttv__hyh = caklq__rlozx._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, sttv__hyh)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    okuv__fmhy = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr._null_bitmap,
        item_ind)
    if not okuv__fmhy:
        return 0, 0, 0
    vsi__yaty = getitem_c_arr(arr._index_offsets, item_ind)
    hmf__bfdj = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    kjxzg__sfjxf = hmf__bfdj - vsi__yaty
    if str_ind >= kjxzg__sfjxf:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, vsi__yaty + str_ind)
    data_start += 1
    if vsi__yaty + str_ind == 0:
        data_start = 0
    csq__cajw = getitem_c_arr(arr._data_offsets, vsi__yaty + str_ind + 1)
    rjls__klyr = csq__cajw - data_start
    return 1, data_start, rjls__klyr


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
        nhtfm__duou = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            vsi__yaty = getitem_c_arr(A._index_offsets, ind)
            hmf__bfdj = getitem_c_arr(A._index_offsets, ind + 1)
            ckc__tydr = hmf__bfdj - vsi__yaty - 1
            dkmj__ixnf = bodo.libs.str_arr_ext.pre_alloc_string_array(ckc__tydr
                , -1)
            for rala__ondhj in range(ckc__tydr):
                data_start = getitem_c_arr(A._data_offsets, vsi__yaty +
                    rala__ondhj)
                data_start += 1
                if vsi__yaty + rala__ondhj == 0:
                    data_start = 0
                csq__cajw = getitem_c_arr(A._data_offsets, vsi__yaty +
                    rala__ondhj + 1)
                rjls__klyr = csq__cajw - data_start
                chnhh__mxzb = get_array_ctypes_ptr(A._data, data_start)
                qnx__irihw = bodo.libs.str_arr_ext.decode_utf8(chnhh__mxzb,
                    rjls__klyr)
                dkmj__ixnf[rala__ondhj] = qnx__irihw
            return dkmj__ixnf
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        cmqde__sui = offset_type.bitwidth // 8

        def _impl(A, ind):
            ckc__tydr = len(A)
            if ckc__tydr != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            ieq__bbyxx = 0
            hblt__wot = 0
            for rala__ondhj in range(ckc__tydr):
                if ind[rala__ondhj]:
                    ieq__bbyxx += 1
                    vsi__yaty = getitem_c_arr(A._index_offsets, rala__ondhj)
                    hmf__bfdj = getitem_c_arr(A._index_offsets, rala__ondhj + 1
                        )
                    hblt__wot += hmf__bfdj - vsi__yaty
            uom__idv = pre_alloc_str_arr_view(ieq__bbyxx, hblt__wot, A._data)
            item_ind = 0
            umcm__jsln = 0
            for rala__ondhj in range(ckc__tydr):
                if ind[rala__ondhj]:
                    vsi__yaty = getitem_c_arr(A._index_offsets, rala__ondhj)
                    hmf__bfdj = getitem_c_arr(A._index_offsets, rala__ondhj + 1
                        )
                    fsx__cxy = hmf__bfdj - vsi__yaty
                    setitem_c_arr(uom__idv._index_offsets, item_ind, umcm__jsln
                        )
                    chnhh__mxzb = get_c_arr_ptr(A._data_offsets, vsi__yaty)
                    aqig__lnz = get_c_arr_ptr(uom__idv._data_offsets,
                        umcm__jsln)
                    _memcpy(aqig__lnz, chnhh__mxzb, fsx__cxy, cmqde__sui)
                    okuv__fmhy = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A
                        ._null_bitmap, rala__ondhj)
                    bodo.libs.int_arr_ext.set_bit_to_arr(uom__idv.
                        _null_bitmap, item_ind, okuv__fmhy)
                    item_ind += 1
                    umcm__jsln += fsx__cxy
            setitem_c_arr(uom__idv._index_offsets, item_ind, umcm__jsln)
            return uom__idv
        return _impl
