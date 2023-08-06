"""Array implementation for variable-size array items.
Corresponds to Spark's ArrayType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Variable-size List: https://arrow.apache.org/docs/format/Columnar.html

The values are stored in a contingous data array, while an offsets array marks the
individual arrays. For example:
value:             [[1, 2], [3], None, [5, 4, 6], []]
data:              [1, 2, 3, 5, 4, 6]
offsets:           [0, 2, 3, 3, 6, 6]
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.imputils import impl_ret_borrowed
from numba.extending import NativeValue, box, intrinsic, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs import array_ext
from bodo.utils.cg_helpers import gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit, to_arr_obj_if_list_obj
from bodo.utils.indexing import add_nested_counts, init_nested_counts
from bodo.utils.typing import BodoError, is_iterable_type, is_list_like_index_type
ll.add_symbol('count_total_elems_list_array', array_ext.
    count_total_elems_list_array)
ll.add_symbol('array_item_array_from_sequence', array_ext.
    array_item_array_from_sequence)
ll.add_symbol('np_array_from_array_item_array', array_ext.
    np_array_from_array_item_array)
offset_type = types.uint64
np_offset_type = numba.np.numpy_support.as_dtype(offset_type)


class ArrayItemArrayType(types.ArrayCompatible):

    def __init__(self, dtype):
        assert bodo.utils.utils.is_array_typ(dtype, False)
        self.dtype = dtype
        super(ArrayItemArrayType, self).__init__(name=
            'ArrayItemArrayType({})'.format(dtype))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    def copy(self):
        return ArrayItemArrayType(self.dtype)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


class ArrayItemArrayPayloadType(types.Type):

    def __init__(self, array_type):
        self.array_type = array_type
        super(ArrayItemArrayPayloadType, self).__init__(name=
            'ArrayItemArrayPayloadType({})'.format(array_type))

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


@register_model(ArrayItemArrayPayloadType)
class ArrayItemArrayPayloadModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        uoj__kzx = [('n_arrays', types.int64), ('data', fe_type.array_type.
            dtype), ('offsets', types.Array(offset_type, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, uoj__kzx)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        uoj__kzx = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, uoj__kzx)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    ffb__pttfo = builder.module
    oft__ewawy = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    xnoe__lxs = cgutils.get_or_insert_function(ffb__pttfo, oft__ewawy, name
        ='.dtor.array_item.{}'.format(array_item_type.dtype))
    if not xnoe__lxs.is_declaration:
        return xnoe__lxs
    xnoe__lxs.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(xnoe__lxs.append_basic_block())
    fxdy__ggp = xnoe__lxs.args[0]
    jfml__xbsuc = context.get_value_type(payload_type).as_pointer()
    romz__tyk = builder.bitcast(fxdy__ggp, jfml__xbsuc)
    aits__fdpfq = context.make_helper(builder, payload_type, ref=romz__tyk)
    context.nrt.decref(builder, array_item_type.dtype, aits__fdpfq.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'),
        aits__fdpfq.offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        aits__fdpfq.null_bitmap)
    builder.ret_void()
    return xnoe__lxs


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    xgez__wpdq = context.get_value_type(payload_type)
    xhhop__zvkje = context.get_abi_sizeof(xgez__wpdq)
    ucvmz__tytt = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    tlgya__upnp = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, xhhop__zvkje), ucvmz__tytt)
    bavjl__iyma = context.nrt.meminfo_data(builder, tlgya__upnp)
    sgz__hel = builder.bitcast(bavjl__iyma, xgez__wpdq.as_pointer())
    aits__fdpfq = cgutils.create_struct_proxy(payload_type)(context, builder)
    aits__fdpfq.n_arrays = n_arrays
    kpfr__zlxbl = n_elems.type.count
    ksv__udbno = builder.extract_value(n_elems, 0)
    zmnl__cdx = cgutils.alloca_once_value(builder, ksv__udbno)
    yfwt__emd = builder.icmp_signed('==', ksv__udbno, lir.Constant(
        ksv__udbno.type, -1))
    with builder.if_then(yfwt__emd):
        builder.store(n_arrays, zmnl__cdx)
    n_elems = cgutils.pack_array(builder, [builder.load(zmnl__cdx)] + [
        builder.extract_value(n_elems, epk__cksnk) for epk__cksnk in range(
        1, kpfr__zlxbl)])
    aits__fdpfq.data = gen_allocate_array(context, builder, array_item_type
        .dtype, n_elems, c)
    khu__xykc = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    apasv__efnr = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [khu__xykc])
    offsets_ptr = apasv__efnr.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    aits__fdpfq.offsets = apasv__efnr._getvalue()
    eul__wzhqn = builder.udiv(builder.add(n_arrays, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    xukur__ghhxt = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [eul__wzhqn])
    null_bitmap_ptr = xukur__ghhxt.data
    aits__fdpfq.null_bitmap = xukur__ghhxt._getvalue()
    builder.store(aits__fdpfq._getvalue(), sgz__hel)
    return tlgya__upnp, aits__fdpfq.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    oqlo__mezug, yrzx__ktr = c.pyapi.call_jit_code(copy_data, sig, [
        data_arr, item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    mzba__yzg = context.insert_const_string(builder.module, 'pandas')
    qtfh__lkmhx = c.pyapi.import_module_noblock(mzba__yzg)
    zgndl__cyzex = c.pyapi.object_getattr_string(qtfh__lkmhx, 'NA')
    mzyud__ivmfv = c.context.get_constant(offset_type, 0)
    builder.store(mzyud__ivmfv, offsets_ptr)
    neiin__sjsr = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as loop:
        cftjp__qftnb = loop.index
        item_ind = builder.load(neiin__sjsr)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [cftjp__qftnb]))
        arr_obj = seq_getitem(builder, context, val, cftjp__qftnb)
        set_bitmap_bit(builder, null_bitmap_ptr, cftjp__qftnb, 0)
        onhg__tqp = is_na_value(builder, context, arr_obj, zgndl__cyzex)
        beox__rlzmf = builder.icmp_unsigned('!=', onhg__tqp, lir.Constant(
            onhg__tqp.type, 1))
        with builder.if_then(beox__rlzmf):
            set_bitmap_bit(builder, null_bitmap_ptr, cftjp__qftnb, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), neiin__sjsr)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(neiin__sjsr), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(qtfh__lkmhx)
    c.pyapi.decref(zgndl__cyzex)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    lic__zkacl = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if lic__zkacl:
        oft__ewawy = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        oimk__bncio = cgutils.get_or_insert_function(c.builder.module,
            oft__ewawy, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(oimk__bncio,
            [val])])
    else:
        pxfq__hvcrd = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            pxfq__hvcrd, epk__cksnk) for epk__cksnk in range(1, pxfq__hvcrd
            .type.count)])
    tlgya__upnp, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if lic__zkacl:
        fxmi__qiw = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        acmi__okw = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        oft__ewawy = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        xnoe__lxs = cgutils.get_or_insert_function(c.builder.module,
            oft__ewawy, name='array_item_array_from_sequence')
        c.builder.call(xnoe__lxs, [val, c.builder.bitcast(acmi__okw, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), fxmi__qiw)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    zmqdm__wnoay = c.context.make_helper(c.builder, typ)
    zmqdm__wnoay.meminfo = tlgya__upnp
    zndjx__pzj = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(zmqdm__wnoay._getvalue(), is_error=zndjx__pzj)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    zmqdm__wnoay = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    bavjl__iyma = context.nrt.meminfo_data(builder, zmqdm__wnoay.meminfo)
    sgz__hel = builder.bitcast(bavjl__iyma, context.get_value_type(
        payload_type).as_pointer())
    aits__fdpfq = cgutils.create_struct_proxy(payload_type)(context,
        builder, builder.load(sgz__hel))
    return aits__fdpfq


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    mzba__yzg = context.insert_const_string(builder.module, 'numpy')
    rgvg__nya = c.pyapi.import_module_noblock(mzba__yzg)
    fqq__tmvd = c.pyapi.object_getattr_string(rgvg__nya, 'object_')
    ebsws__zszpb = c.pyapi.long_from_longlong(n_arrays)
    bqre__zppf = c.pyapi.call_method(rgvg__nya, 'ndarray', (ebsws__zszpb,
        fqq__tmvd))
    zaigj__gyyh = c.pyapi.object_getattr_string(rgvg__nya, 'nan')
    neiin__sjsr = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_arrays) as loop:
        cftjp__qftnb = loop.index
        pyarray_setitem(builder, context, bqre__zppf, cftjp__qftnb, zaigj__gyyh
            )
        valj__nvcht = get_bitmap_bit(builder, null_bitmap_ptr, cftjp__qftnb)
        qqwzw__rdu = builder.icmp_unsigned('!=', valj__nvcht, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(qqwzw__rdu):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(cftjp__qftnb, lir.Constant(
                cftjp__qftnb.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [cftjp__qftnb]))), lir.IntType(64))
            item_ind = builder.load(neiin__sjsr)
            oqlo__mezug, cgo__nefv = c.pyapi.call_jit_code(lambda data_arr,
                item_ind, n_items: data_arr[item_ind:item_ind + n_items],
                typ.dtype(typ.dtype, types.int64, types.int64), [data_arr,
                item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), neiin__sjsr)
            arr_obj = c.pyapi.from_native_value(typ.dtype, cgo__nefv, c.
                env_manager)
            pyarray_setitem(builder, context, bqre__zppf, cftjp__qftnb, arr_obj
                )
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(rgvg__nya)
    c.pyapi.decref(fqq__tmvd)
    c.pyapi.decref(ebsws__zszpb)
    c.pyapi.decref(zaigj__gyyh)
    return bqre__zppf


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    aits__fdpfq = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = aits__fdpfq.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), aits__fdpfq.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), aits__fdpfq.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        fxmi__qiw = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        acmi__okw = c.context.make_helper(c.builder, typ.dtype, data_arr).data
        oft__ewawy = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        awp__ugzvp = cgutils.get_or_insert_function(c.builder.module,
            oft__ewawy, name='np_array_from_array_item_array')
        arr = c.builder.call(awp__ugzvp, [aits__fdpfq.n_arrays, c.builder.
            bitcast(acmi__okw, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), fxmi__qiw)])
    else:
        arr = _box_array_item_array_generic(typ, c, aits__fdpfq.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    mdrl__hfdm, nvn__nbqu, ong__ele = args
    smvm__kvzj = bodo.utils.transform.get_type_alloc_counts(array_item_type
        .dtype)
    qvcxw__ntw = sig.args[1]
    if not isinstance(qvcxw__ntw, types.UniTuple):
        nvn__nbqu = cgutils.pack_array(builder, [lir.Constant(lir.IntType(
            64), -1) for ong__ele in range(smvm__kvzj)])
    elif qvcxw__ntw.count < smvm__kvzj:
        nvn__nbqu = cgutils.pack_array(builder, [builder.extract_value(
            nvn__nbqu, epk__cksnk) for epk__cksnk in range(qvcxw__ntw.count
            )] + [lir.Constant(lir.IntType(64), -1) for ong__ele in range(
            smvm__kvzj - qvcxw__ntw.count)])
    tlgya__upnp, ong__ele, ong__ele, ong__ele = construct_array_item_array(
        context, builder, array_item_type, mdrl__hfdm, nvn__nbqu)
    zmqdm__wnoay = context.make_helper(builder, array_item_type)
    zmqdm__wnoay.meminfo = tlgya__upnp
    return zmqdm__wnoay._getvalue()


@intrinsic
def pre_alloc_array_item_array(typingctx, num_arrs_typ, num_values_typ,
    dtype_typ=None):
    assert isinstance(num_arrs_typ, types.Integer)
    array_item_type = ArrayItemArrayType(dtype_typ.instance_type)
    num_values_typ = types.unliteral(num_values_typ)
    return array_item_type(types.int64, num_values_typ, dtype_typ
        ), lower_pre_alloc_array_item_array


def pre_alloc_array_item_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis.
    _analyze_op_call_bodo_libs_array_item_arr_ext_pre_alloc_array_item_array
    ) = pre_alloc_array_item_array_equiv


def init_array_item_array_codegen(context, builder, signature, args):
    n_arrays, hug__zmcxh, apasv__efnr, xukur__ghhxt = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    xgez__wpdq = context.get_value_type(payload_type)
    xhhop__zvkje = context.get_abi_sizeof(xgez__wpdq)
    ucvmz__tytt = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    tlgya__upnp = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, xhhop__zvkje), ucvmz__tytt)
    bavjl__iyma = context.nrt.meminfo_data(builder, tlgya__upnp)
    sgz__hel = builder.bitcast(bavjl__iyma, xgez__wpdq.as_pointer())
    aits__fdpfq = cgutils.create_struct_proxy(payload_type)(context, builder)
    aits__fdpfq.n_arrays = n_arrays
    aits__fdpfq.data = hug__zmcxh
    aits__fdpfq.offsets = apasv__efnr
    aits__fdpfq.null_bitmap = xukur__ghhxt
    builder.store(aits__fdpfq._getvalue(), sgz__hel)
    context.nrt.incref(builder, signature.args[1], hug__zmcxh)
    context.nrt.incref(builder, signature.args[2], apasv__efnr)
    context.nrt.incref(builder, signature.args[3], xukur__ghhxt)
    zmqdm__wnoay = context.make_helper(builder, array_item_type)
    zmqdm__wnoay.meminfo = tlgya__upnp
    return zmqdm__wnoay._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    psvfn__jzbwc = ArrayItemArrayType(data_type)
    sig = psvfn__jzbwc(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        aits__fdpfq = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            aits__fdpfq.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        aits__fdpfq = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        acmi__okw = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, aits__fdpfq.offsets).data
        apasv__efnr = builder.bitcast(acmi__okw, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(apasv__efnr, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        aits__fdpfq = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            aits__fdpfq.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        aits__fdpfq = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            aits__fdpfq.null_bitmap)
    return types.Array(types.uint8, 1, 'C')(arr_typ), codegen


def alias_ext_single_array(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['get_offsets',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array
numba.core.ir_utils.alias_func_extensions['get_data',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array
numba.core.ir_utils.alias_func_extensions['get_null_bitmap',
    'bodo.libs.array_item_arr_ext'] = alias_ext_single_array


@intrinsic
def get_n_arrays(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        aits__fdpfq = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return aits__fdpfq.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, ptm__rblg = args
        zmqdm__wnoay = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        bavjl__iyma = context.nrt.meminfo_data(builder, zmqdm__wnoay.meminfo)
        sgz__hel = builder.bitcast(bavjl__iyma, context.get_value_type(
            payload_type).as_pointer())
        aits__fdpfq = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(sgz__hel))
        context.nrt.decref(builder, data_typ, aits__fdpfq.data)
        aits__fdpfq.data = ptm__rblg
        context.nrt.incref(builder, data_typ, ptm__rblg)
        builder.store(aits__fdpfq._getvalue(), sgz__hel)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    hug__zmcxh = get_data(arr)
    wwgyb__joow = len(hug__zmcxh)
    if wwgyb__joow < new_size:
        nwlaw__ech = max(2 * wwgyb__joow, new_size)
        ptm__rblg = bodo.libs.array_kernels.resize_and_copy(hug__zmcxh,
            old_size, nwlaw__ech)
        replace_data_arr(arr, ptm__rblg)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    hug__zmcxh = get_data(arr)
    apasv__efnr = get_offsets(arr)
    dys__zdl = len(hug__zmcxh)
    cqzh__cnk = apasv__efnr[-1]
    if dys__zdl != cqzh__cnk:
        ptm__rblg = bodo.libs.array_kernels.resize_and_copy(hug__zmcxh,
            cqzh__cnk, cqzh__cnk)
        replace_data_arr(arr, ptm__rblg)


@overload(len, no_unliteral=True)
def overload_array_item_arr_len(A):
    if isinstance(A, ArrayItemArrayType):
        return lambda A: get_n_arrays(A)


@overload_attribute(ArrayItemArrayType, 'shape')
def overload_array_item_arr_shape(A):
    return lambda A: (get_n_arrays(A),)


@overload_attribute(ArrayItemArrayType, 'dtype')
def overload_array_item_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(ArrayItemArrayType, 'ndim')
def overload_array_item_arr_ndim(A):
    return lambda A: 1


@overload_attribute(ArrayItemArrayType, 'nbytes')
def overload_array_item_arr_nbytes(A):
    return lambda A: get_data(A).nbytes + get_offsets(A
        ).nbytes + get_null_bitmap(A).nbytes


@overload(operator.getitem, no_unliteral=True)
def array_item_arr_getitem_array(arr, ind):
    if not isinstance(arr, ArrayItemArrayType):
        return
    if isinstance(ind, types.Integer):

        def array_item_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            apasv__efnr = get_offsets(arr)
            hug__zmcxh = get_data(arr)
            oddgu__gzjn = apasv__efnr[ind]
            kyuu__uzgl = apasv__efnr[ind + 1]
            return hug__zmcxh[oddgu__gzjn:kyuu__uzgl]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        fprjx__ukwu = arr.dtype

        def impl_bool(arr, ind):
            iyfa__gcw = len(arr)
            if iyfa__gcw != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            xukur__ghhxt = get_null_bitmap(arr)
            n_arrays = 0
            vheaf__gsc = init_nested_counts(fprjx__ukwu)
            for epk__cksnk in range(iyfa__gcw):
                if ind[epk__cksnk]:
                    n_arrays += 1
                    gmhnf__kdkfv = arr[epk__cksnk]
                    vheaf__gsc = add_nested_counts(vheaf__gsc, gmhnf__kdkfv)
            bqre__zppf = pre_alloc_array_item_array(n_arrays, vheaf__gsc,
                fprjx__ukwu)
            dhkm__ylog = get_null_bitmap(bqre__zppf)
            pdp__sxrz = 0
            for vos__zgdal in range(iyfa__gcw):
                if ind[vos__zgdal]:
                    bqre__zppf[pdp__sxrz] = arr[vos__zgdal]
                    odpqj__ciubo = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        xukur__ghhxt, vos__zgdal)
                    bodo.libs.int_arr_ext.set_bit_to_arr(dhkm__ylog,
                        pdp__sxrz, odpqj__ciubo)
                    pdp__sxrz += 1
            return bqre__zppf
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        fprjx__ukwu = arr.dtype

        def impl_int(arr, ind):
            xukur__ghhxt = get_null_bitmap(arr)
            iyfa__gcw = len(ind)
            n_arrays = iyfa__gcw
            vheaf__gsc = init_nested_counts(fprjx__ukwu)
            for jdgq__rtq in range(iyfa__gcw):
                epk__cksnk = ind[jdgq__rtq]
                gmhnf__kdkfv = arr[epk__cksnk]
                vheaf__gsc = add_nested_counts(vheaf__gsc, gmhnf__kdkfv)
            bqre__zppf = pre_alloc_array_item_array(n_arrays, vheaf__gsc,
                fprjx__ukwu)
            dhkm__ylog = get_null_bitmap(bqre__zppf)
            for jeu__hxfp in range(iyfa__gcw):
                vos__zgdal = ind[jeu__hxfp]
                bqre__zppf[jeu__hxfp] = arr[vos__zgdal]
                odpqj__ciubo = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    xukur__ghhxt, vos__zgdal)
                bodo.libs.int_arr_ext.set_bit_to_arr(dhkm__ylog, jeu__hxfp,
                    odpqj__ciubo)
            return bqre__zppf
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            iyfa__gcw = len(arr)
            akbzq__kcsm = numba.cpython.unicode._normalize_slice(ind, iyfa__gcw
                )
            pujqn__xaqg = np.arange(akbzq__kcsm.start, akbzq__kcsm.stop,
                akbzq__kcsm.step)
            return arr[pujqn__xaqg]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            apasv__efnr = get_offsets(A)
            xukur__ghhxt = get_null_bitmap(A)
            if idx == 0:
                apasv__efnr[0] = 0
            n_items = len(val)
            tteq__rqkx = apasv__efnr[idx] + n_items
            ensure_data_capacity(A, apasv__efnr[idx], tteq__rqkx)
            hug__zmcxh = get_data(A)
            apasv__efnr[idx + 1] = apasv__efnr[idx] + n_items
            hug__zmcxh[apasv__efnr[idx]:apasv__efnr[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(xukur__ghhxt, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            akbzq__kcsm = numba.cpython.unicode._normalize_slice(idx, len(A))
            for epk__cksnk in range(akbzq__kcsm.start, akbzq__kcsm.stop,
                akbzq__kcsm.step):
                A[epk__cksnk] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            apasv__efnr = get_offsets(A)
            xukur__ghhxt = get_null_bitmap(A)
            hxly__nrv = get_offsets(val)
            mafp__jxth = get_data(val)
            gowkk__msiug = get_null_bitmap(val)
            iyfa__gcw = len(A)
            akbzq__kcsm = numba.cpython.unicode._normalize_slice(idx, iyfa__gcw
                )
            idur__eqv, bvv__zgdwy = akbzq__kcsm.start, akbzq__kcsm.stop
            assert akbzq__kcsm.step == 1
            if idur__eqv == 0:
                apasv__efnr[idur__eqv] = 0
            eir__gwt = apasv__efnr[idur__eqv]
            tteq__rqkx = eir__gwt + len(mafp__jxth)
            ensure_data_capacity(A, eir__gwt, tteq__rqkx)
            hug__zmcxh = get_data(A)
            hug__zmcxh[eir__gwt:eir__gwt + len(mafp__jxth)] = mafp__jxth
            apasv__efnr[idur__eqv:bvv__zgdwy + 1] = hxly__nrv + eir__gwt
            dpgt__zuoh = 0
            for epk__cksnk in range(idur__eqv, bvv__zgdwy):
                odpqj__ciubo = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    gowkk__msiug, dpgt__zuoh)
                bodo.libs.int_arr_ext.set_bit_to_arr(xukur__ghhxt,
                    epk__cksnk, odpqj__ciubo)
                dpgt__zuoh += 1
        return impl_slice
    raise BodoError(
        'only setitem with scalar index is currently supported for list arrays'
        )


@overload_method(ArrayItemArrayType, 'copy', no_unliteral=True)
def overload_array_item_arr_copy(A):

    def copy_impl(A):
        return init_array_item_array(len(A), get_data(A).copy(),
            get_offsets(A).copy(), get_null_bitmap(A).copy())
    return copy_impl
