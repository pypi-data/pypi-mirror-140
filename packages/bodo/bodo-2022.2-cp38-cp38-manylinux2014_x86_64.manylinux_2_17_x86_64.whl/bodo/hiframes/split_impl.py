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
        gzs__cjdkf = [('index_offsets', types.CPointer(offset_type)), (
            'data_offsets', types.CPointer(offset_type)), ('null_bitmap',
            types.CPointer(char_typ))]
        models.StructModel.__init__(self, dmm, fe_type, gzs__cjdkf)


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
    sgfxo__timc = context.get_value_type(str_arr_split_view_payload_type)
    wdd__rsqoh = context.get_abi_sizeof(sgfxo__timc)
    unzcn__shsj = context.get_value_type(types.voidptr)
    bbx__jfv = context.get_value_type(types.uintp)
    qfj__rsjya = lir.FunctionType(lir.VoidType(), [unzcn__shsj, bbx__jfv,
        unzcn__shsj])
    aur__wgg = cgutils.get_or_insert_function(builder.module, qfj__rsjya,
        name='dtor_str_arr_split_view')
    ozw__yikah = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, wdd__rsqoh), aur__wgg)
    foh__eufw = context.nrt.meminfo_data(builder, ozw__yikah)
    cec__gdy = builder.bitcast(foh__eufw, sgfxo__timc.as_pointer())
    return ozw__yikah, cec__gdy


@intrinsic
def compute_split_view(typingctx, str_arr_typ, sep_typ=None):
    assert str_arr_typ == string_array_type and isinstance(sep_typ, types.
        StringLiteral)

    def codegen(context, builder, sig, args):
        hxob__zmwx, xrffi__uvzi = args
        ozw__yikah, cec__gdy = construct_str_arr_split_view(context, builder)
        zhik__mvf = _get_str_binary_arr_payload(context, builder,
            hxob__zmwx, string_array_type)
        mkbcb__kypy = lir.FunctionType(lir.VoidType(), [cec__gdy.type, lir.
            IntType(64), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8)])
        derj__jzp = cgutils.get_or_insert_function(builder.module,
            mkbcb__kypy, name='str_arr_split_view_impl')
        nxlm__hpdkn = context.make_helper(builder, offset_arr_type,
            zhik__mvf.offsets).data
        fsdo__sjui = context.make_helper(builder, char_arr_type, zhik__mvf.data
            ).data
        xlxj__znh = context.make_helper(builder, null_bitmap_arr_type,
            zhik__mvf.null_bitmap).data
        kti__gviyg = context.get_constant(types.int8, ord(sep_typ.
            literal_value))
        builder.call(derj__jzp, [cec__gdy, zhik__mvf.n_arrays, nxlm__hpdkn,
            fsdo__sjui, xlxj__znh, kti__gviyg])
        zem__zgjb = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(cec__gdy))
        tgtgx__auqg = context.make_helper(builder, string_array_split_view_type
            )
        tgtgx__auqg.num_items = zhik__mvf.n_arrays
        tgtgx__auqg.index_offsets = zem__zgjb.index_offsets
        tgtgx__auqg.data_offsets = zem__zgjb.data_offsets
        tgtgx__auqg.data = context.compile_internal(builder, lambda S:
            get_data_ptr(S), data_ctypes_type(string_array_type), [hxob__zmwx])
        tgtgx__auqg.null_bitmap = zem__zgjb.null_bitmap
        tgtgx__auqg.meminfo = ozw__yikah
        sbyj__eilnd = tgtgx__auqg._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, sbyj__eilnd)
    return string_array_split_view_type(string_array_type, sep_typ), codegen


@box(StringArraySplitViewType)
def box_str_arr_split_view(typ, val, c):
    context = c.context
    builder = c.builder
    tttv__nvk = context.make_helper(builder, string_array_split_view_type, val)
    qvt__geap = context.insert_const_string(builder.module, 'numpy')
    tkzt__dxwsi = c.pyapi.import_module_noblock(qvt__geap)
    dtype = c.pyapi.object_getattr_string(tkzt__dxwsi, 'object_')
    tsil__txmou = builder.sext(tttv__nvk.num_items, c.pyapi.longlong)
    znxvt__era = c.pyapi.long_from_longlong(tsil__txmou)
    hgg__tszn = c.pyapi.call_method(tkzt__dxwsi, 'ndarray', (znxvt__era, dtype)
        )
    nge__duaw = LLType.function(lir.IntType(8).as_pointer(), [c.pyapi.pyobj,
        c.pyapi.py_ssize_t])
    oymp__jpavo = c.pyapi._get_function(nge__duaw, name='array_getptr1')
    yof__cfo = LLType.function(lir.VoidType(), [c.pyapi.pyobj, lir.IntType(
        8).as_pointer(), c.pyapi.pyobj])
    nmlz__buq = c.pyapi._get_function(yof__cfo, name='array_setitem')
    bsy__iaqq = c.pyapi.object_getattr_string(tkzt__dxwsi, 'nan')
    with cgutils.for_range(builder, tttv__nvk.num_items) as loop:
        str_ind = loop.index
        pxf__ygqmb = builder.sext(builder.load(builder.gep(tttv__nvk.
            index_offsets, [str_ind])), lir.IntType(64))
        sggjh__bby = builder.sext(builder.load(builder.gep(tttv__nvk.
            index_offsets, [builder.add(str_ind, str_ind.type(1))])), lir.
            IntType(64))
        vigto__chdd = builder.lshr(str_ind, lir.Constant(lir.IntType(64), 3))
        vmdb__vbe = builder.gep(tttv__nvk.null_bitmap, [vigto__chdd])
        hvaa__igg = builder.load(vmdb__vbe)
        jcdl__cavbw = builder.trunc(builder.and_(str_ind, lir.Constant(lir.
            IntType(64), 7)), lir.IntType(8))
        val = builder.and_(builder.lshr(hvaa__igg, jcdl__cavbw), lir.
            Constant(lir.IntType(8), 1))
        jjxdh__gyf = builder.sub(sggjh__bby, pxf__ygqmb)
        jjxdh__gyf = builder.sub(jjxdh__gyf, jjxdh__gyf.type(1))
        lzi__ddj = builder.call(oymp__jpavo, [hgg__tszn, str_ind])
        vsix__cxdp = c.builder.icmp_unsigned('!=', val, val.type(0))
        with c.builder.if_else(vsix__cxdp) as (then, otherwise):
            with then:
                znhva__phtwn = c.pyapi.list_new(jjxdh__gyf)
                with c.builder.if_then(cgutils.is_not_null(c.builder,
                    znhva__phtwn), likely=True):
                    with cgutils.for_range(c.builder, jjxdh__gyf) as loop:
                        qmq__hgoc = builder.add(pxf__ygqmb, loop.index)
                        data_start = builder.load(builder.gep(tttv__nvk.
                            data_offsets, [qmq__hgoc]))
                        data_start = builder.add(data_start, data_start.type(1)
                            )
                        alrx__okhqw = builder.load(builder.gep(tttv__nvk.
                            data_offsets, [builder.add(qmq__hgoc, qmq__hgoc
                            .type(1))]))
                        naix__ejsev = builder.gep(builder.extract_value(
                            tttv__nvk.data, 0), [data_start])
                        aidz__fjev = builder.sext(builder.sub(alrx__okhqw,
                            data_start), lir.IntType(64))
                        ynjum__ifwdn = c.pyapi.string_from_string_and_size(
                            naix__ejsev, aidz__fjev)
                        c.pyapi.list_setitem(znhva__phtwn, loop.index,
                            ynjum__ifwdn)
                builder.call(nmlz__buq, [hgg__tszn, lzi__ddj, znhva__phtwn])
            with otherwise:
                builder.call(nmlz__buq, [hgg__tszn, lzi__ddj, bsy__iaqq])
    c.pyapi.decref(tkzt__dxwsi)
    c.pyapi.decref(dtype)
    c.pyapi.decref(bsy__iaqq)
    return hgg__tszn


@intrinsic
def pre_alloc_str_arr_view(typingctx, num_items_t, num_offsets_t, data_t=None):
    assert num_items_t == types.intp and num_offsets_t == types.intp

    def codegen(context, builder, sig, args):
        qpm__ylim, dkau__uytgc, naix__ejsev = args
        ozw__yikah, cec__gdy = construct_str_arr_split_view(context, builder)
        mkbcb__kypy = lir.FunctionType(lir.VoidType(), [cec__gdy.type, lir.
            IntType(64), lir.IntType(64)])
        derj__jzp = cgutils.get_or_insert_function(builder.module,
            mkbcb__kypy, name='str_arr_split_view_alloc')
        builder.call(derj__jzp, [cec__gdy, qpm__ylim, dkau__uytgc])
        zem__zgjb = cgutils.create_struct_proxy(str_arr_split_view_payload_type
            )(context, builder, value=builder.load(cec__gdy))
        tgtgx__auqg = context.make_helper(builder, string_array_split_view_type
            )
        tgtgx__auqg.num_items = qpm__ylim
        tgtgx__auqg.index_offsets = zem__zgjb.index_offsets
        tgtgx__auqg.data_offsets = zem__zgjb.data_offsets
        tgtgx__auqg.data = naix__ejsev
        tgtgx__auqg.null_bitmap = zem__zgjb.null_bitmap
        context.nrt.incref(builder, data_t, naix__ejsev)
        tgtgx__auqg.meminfo = ozw__yikah
        sbyj__eilnd = tgtgx__auqg._getvalue()
        return impl_ret_new_ref(context, builder,
            string_array_split_view_type, sbyj__eilnd)
    return string_array_split_view_type(types.intp, types.intp, data_t
        ), codegen


@intrinsic
def get_c_arr_ptr(typingctx, c_arr, ind_t=None):
    assert isinstance(c_arr, (types.CPointer, types.ArrayCTypes))

    def codegen(context, builder, sig, args):
        mhlaj__vmg, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            mhlaj__vmg = builder.extract_value(mhlaj__vmg, 0)
        return builder.bitcast(builder.gep(mhlaj__vmg, [ind]), lir.IntType(
            8).as_pointer())
    return types.voidptr(c_arr, ind_t), codegen


@intrinsic
def getitem_c_arr(typingctx, c_arr, ind_t=None):

    def codegen(context, builder, sig, args):
        mhlaj__vmg, ind = args
        if isinstance(sig.args[0], types.ArrayCTypes):
            mhlaj__vmg = builder.extract_value(mhlaj__vmg, 0)
        return builder.load(builder.gep(mhlaj__vmg, [ind]))
    return c_arr.dtype(c_arr, ind_t), codegen


@intrinsic
def setitem_c_arr(typingctx, c_arr, ind_t, item_t=None):

    def codegen(context, builder, sig, args):
        mhlaj__vmg, ind, vosi__lsf = args
        xndh__zsc = builder.gep(mhlaj__vmg, [ind])
        builder.store(vosi__lsf, xndh__zsc)
    return types.void(c_arr, ind_t, c_arr.dtype), codegen


@intrinsic
def get_array_ctypes_ptr(typingctx, arr_ctypes_t, ind_t=None):

    def codegen(context, builder, sig, args):
        xgxx__bfzv, ind = args
        jsq__dvbkj = context.make_helper(builder, arr_ctypes_t, xgxx__bfzv)
        fwv__golu = context.make_helper(builder, arr_ctypes_t)
        fwv__golu.data = builder.gep(jsq__dvbkj.data, [ind])
        fwv__golu.meminfo = jsq__dvbkj.meminfo
        deb__han = fwv__golu._getvalue()
        return impl_ret_borrowed(context, builder, arr_ctypes_t, deb__han)
    return arr_ctypes_t(arr_ctypes_t, ind_t), codegen


@numba.njit(no_cpython_wrapper=True)
def get_split_view_index(arr, item_ind, str_ind):
    vzub__jmc = bodo.libs.int_arr_ext.get_bit_bitmap_arr(arr._null_bitmap,
        item_ind)
    if not vzub__jmc:
        return 0, 0, 0
    qmq__hgoc = getitem_c_arr(arr._index_offsets, item_ind)
    lyd__yiz = getitem_c_arr(arr._index_offsets, item_ind + 1) - 1
    kykfb__iumfk = lyd__yiz - qmq__hgoc
    if str_ind >= kykfb__iumfk:
        return 0, 0, 0
    data_start = getitem_c_arr(arr._data_offsets, qmq__hgoc + str_ind)
    data_start += 1
    if qmq__hgoc + str_ind == 0:
        data_start = 0
    alrx__okhqw = getitem_c_arr(arr._data_offsets, qmq__hgoc + str_ind + 1)
    fbsup__fhzyt = alrx__okhqw - data_start
    return 1, data_start, fbsup__fhzyt


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
        kuej__wtv = numba.cpython.unicode.PY_UNICODE_1BYTE_KIND

        def _impl(A, ind):
            qmq__hgoc = getitem_c_arr(A._index_offsets, ind)
            lyd__yiz = getitem_c_arr(A._index_offsets, ind + 1)
            qfqj__vtjge = lyd__yiz - qmq__hgoc - 1
            hxob__zmwx = bodo.libs.str_arr_ext.pre_alloc_string_array(
                qfqj__vtjge, -1)
            for vhx__eqx in range(qfqj__vtjge):
                data_start = getitem_c_arr(A._data_offsets, qmq__hgoc +
                    vhx__eqx)
                data_start += 1
                if qmq__hgoc + vhx__eqx == 0:
                    data_start = 0
                alrx__okhqw = getitem_c_arr(A._data_offsets, qmq__hgoc +
                    vhx__eqx + 1)
                fbsup__fhzyt = alrx__okhqw - data_start
                xndh__zsc = get_array_ctypes_ptr(A._data, data_start)
                dljh__oyp = bodo.libs.str_arr_ext.decode_utf8(xndh__zsc,
                    fbsup__fhzyt)
                hxob__zmwx[vhx__eqx] = dljh__oyp
            return hxob__zmwx
        return _impl
    if A == string_array_split_view_type and ind == types.Array(types.bool_,
        1, 'C'):
        uiqy__gomfx = offset_type.bitwidth // 8

        def _impl(A, ind):
            qfqj__vtjge = len(A)
            if qfqj__vtjge != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            qpm__ylim = 0
            dkau__uytgc = 0
            for vhx__eqx in range(qfqj__vtjge):
                if ind[vhx__eqx]:
                    qpm__ylim += 1
                    qmq__hgoc = getitem_c_arr(A._index_offsets, vhx__eqx)
                    lyd__yiz = getitem_c_arr(A._index_offsets, vhx__eqx + 1)
                    dkau__uytgc += lyd__yiz - qmq__hgoc
            hgg__tszn = pre_alloc_str_arr_view(qpm__ylim, dkau__uytgc, A._data)
            item_ind = 0
            mtei__upbr = 0
            for vhx__eqx in range(qfqj__vtjge):
                if ind[vhx__eqx]:
                    qmq__hgoc = getitem_c_arr(A._index_offsets, vhx__eqx)
                    lyd__yiz = getitem_c_arr(A._index_offsets, vhx__eqx + 1)
                    pne__iapao = lyd__yiz - qmq__hgoc
                    setitem_c_arr(hgg__tszn._index_offsets, item_ind,
                        mtei__upbr)
                    xndh__zsc = get_c_arr_ptr(A._data_offsets, qmq__hgoc)
                    oyli__oyo = get_c_arr_ptr(hgg__tszn._data_offsets,
                        mtei__upbr)
                    _memcpy(oyli__oyo, xndh__zsc, pne__iapao, uiqy__gomfx)
                    vzub__jmc = bodo.libs.int_arr_ext.get_bit_bitmap_arr(A.
                        _null_bitmap, vhx__eqx)
                    bodo.libs.int_arr_ext.set_bit_to_arr(hgg__tszn.
                        _null_bitmap, item_ind, vzub__jmc)
                    item_ind += 1
                    mtei__upbr += pne__iapao
            setitem_c_arr(hgg__tszn._index_offsets, item_ind, mtei__upbr)
            return hgg__tszn
        return _impl
