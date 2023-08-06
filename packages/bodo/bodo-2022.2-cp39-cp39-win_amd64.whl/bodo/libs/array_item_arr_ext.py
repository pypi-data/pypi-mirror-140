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
        jgm__rkhu = [('n_arrays', types.int64), ('data', fe_type.array_type
            .dtype), ('offsets', types.Array(offset_type, 1, 'C')), (
            'null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, jgm__rkhu)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        jgm__rkhu = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, jgm__rkhu)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    qoc__otqw = builder.module
    uvrdu__mcfzx = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    vago__mttdf = cgutils.get_or_insert_function(qoc__otqw, uvrdu__mcfzx,
        name='.dtor.array_item.{}'.format(array_item_type.dtype))
    if not vago__mttdf.is_declaration:
        return vago__mttdf
    vago__mttdf.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(vago__mttdf.append_basic_block())
    gedtq__aqe = vago__mttdf.args[0]
    xlw__xst = context.get_value_type(payload_type).as_pointer()
    ovfjs__abr = builder.bitcast(gedtq__aqe, xlw__xst)
    qgx__eoxr = context.make_helper(builder, payload_type, ref=ovfjs__abr)
    context.nrt.decref(builder, array_item_type.dtype, qgx__eoxr.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'), qgx__eoxr
        .offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'), qgx__eoxr
        .null_bitmap)
    builder.ret_void()
    return vago__mttdf


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    kdmmk__iyb = context.get_value_type(payload_type)
    sle__lghbv = context.get_abi_sizeof(kdmmk__iyb)
    gemw__kxi = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    fpq__isl = context.nrt.meminfo_alloc_dtor(builder, context.get_constant
        (types.uintp, sle__lghbv), gemw__kxi)
    thkoy__eddbe = context.nrt.meminfo_data(builder, fpq__isl)
    buljl__pzwa = builder.bitcast(thkoy__eddbe, kdmmk__iyb.as_pointer())
    qgx__eoxr = cgutils.create_struct_proxy(payload_type)(context, builder)
    qgx__eoxr.n_arrays = n_arrays
    fgw__yfz = n_elems.type.count
    otnm__bjy = builder.extract_value(n_elems, 0)
    lulvk__bchi = cgutils.alloca_once_value(builder, otnm__bjy)
    tdbi__hjns = builder.icmp_signed('==', otnm__bjy, lir.Constant(
        otnm__bjy.type, -1))
    with builder.if_then(tdbi__hjns):
        builder.store(n_arrays, lulvk__bchi)
    n_elems = cgutils.pack_array(builder, [builder.load(lulvk__bchi)] + [
        builder.extract_value(n_elems, qunqa__eqt) for qunqa__eqt in range(
        1, fgw__yfz)])
    qgx__eoxr.data = gen_allocate_array(context, builder, array_item_type.
        dtype, n_elems, c)
    ersi__fbojo = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    ikonk__mnvq = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [ersi__fbojo])
    offsets_ptr = ikonk__mnvq.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    qgx__eoxr.offsets = ikonk__mnvq._getvalue()
    ibdm__loek = builder.udiv(builder.add(n_arrays, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    ikkcj__zdu = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [ibdm__loek])
    null_bitmap_ptr = ikkcj__zdu.data
    qgx__eoxr.null_bitmap = ikkcj__zdu._getvalue()
    builder.store(qgx__eoxr._getvalue(), buljl__pzwa)
    return fpq__isl, qgx__eoxr.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    wqgem__fnnha, cogv__nnxag = c.pyapi.call_jit_code(copy_data, sig, [
        data_arr, item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    kglem__kczxt = context.insert_const_string(builder.module, 'pandas')
    mihz__jtj = c.pyapi.import_module_noblock(kglem__kczxt)
    oen__zfot = c.pyapi.object_getattr_string(mihz__jtj, 'NA')
    jtbov__znxr = c.context.get_constant(offset_type, 0)
    builder.store(jtbov__znxr, offsets_ptr)
    vnl__ysn = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as loop:
        rtyxt__uruh = loop.index
        item_ind = builder.load(vnl__ysn)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [rtyxt__uruh]))
        arr_obj = seq_getitem(builder, context, val, rtyxt__uruh)
        set_bitmap_bit(builder, null_bitmap_ptr, rtyxt__uruh, 0)
        vvw__bxflf = is_na_value(builder, context, arr_obj, oen__zfot)
        nnfi__xrt = builder.icmp_unsigned('!=', vvw__bxflf, lir.Constant(
            vvw__bxflf.type, 1))
        with builder.if_then(nnfi__xrt):
            set_bitmap_bit(builder, null_bitmap_ptr, rtyxt__uruh, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), vnl__ysn)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(vnl__ysn), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(mihz__jtj)
    c.pyapi.decref(oen__zfot)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    vrvo__fpje = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if vrvo__fpje:
        uvrdu__mcfzx = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        frvu__cnqm = cgutils.get_or_insert_function(c.builder.module,
            uvrdu__mcfzx, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(frvu__cnqm,
            [val])])
    else:
        hcjk__nvq = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            hcjk__nvq, qunqa__eqt) for qunqa__eqt in range(1, hcjk__nvq.
            type.count)])
    fpq__isl, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if vrvo__fpje:
        reod__mikng = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        vdqnp__njddi = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        uvrdu__mcfzx = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        vago__mttdf = cgutils.get_or_insert_function(c.builder.module,
            uvrdu__mcfzx, name='array_item_array_from_sequence')
        c.builder.call(vago__mttdf, [val, c.builder.bitcast(vdqnp__njddi,
            lir.IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir
            .Constant(lir.IntType(32), reod__mikng)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    ssrld__pejue = c.context.make_helper(c.builder, typ)
    ssrld__pejue.meminfo = fpq__isl
    htde__sgvkg = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(ssrld__pejue._getvalue(), is_error=htde__sgvkg)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    ssrld__pejue = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    thkoy__eddbe = context.nrt.meminfo_data(builder, ssrld__pejue.meminfo)
    buljl__pzwa = builder.bitcast(thkoy__eddbe, context.get_value_type(
        payload_type).as_pointer())
    qgx__eoxr = cgutils.create_struct_proxy(payload_type)(context, builder,
        builder.load(buljl__pzwa))
    return qgx__eoxr


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    kglem__kczxt = context.insert_const_string(builder.module, 'numpy')
    tsvk__ucotc = c.pyapi.import_module_noblock(kglem__kczxt)
    wwz__nas = c.pyapi.object_getattr_string(tsvk__ucotc, 'object_')
    dskj__cxs = c.pyapi.long_from_longlong(n_arrays)
    yjo__rtyaa = c.pyapi.call_method(tsvk__ucotc, 'ndarray', (dskj__cxs,
        wwz__nas))
    uoac__ypl = c.pyapi.object_getattr_string(tsvk__ucotc, 'nan')
    vnl__ysn = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType(
        64), 0))
    with cgutils.for_range(builder, n_arrays) as loop:
        rtyxt__uruh = loop.index
        pyarray_setitem(builder, context, yjo__rtyaa, rtyxt__uruh, uoac__ypl)
        gnzh__pefwd = get_bitmap_bit(builder, null_bitmap_ptr, rtyxt__uruh)
        pld__gsrq = builder.icmp_unsigned('!=', gnzh__pefwd, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(pld__gsrq):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(rtyxt__uruh, lir.Constant(
                rtyxt__uruh.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [rtyxt__uruh]))), lir.IntType(64))
            item_ind = builder.load(vnl__ysn)
            wqgem__fnnha, bblnx__nyjf = c.pyapi.call_jit_code(lambda
                data_arr, item_ind, n_items: data_arr[item_ind:item_ind +
                n_items], typ.dtype(typ.dtype, types.int64, types.int64), [
                data_arr, item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), vnl__ysn)
            arr_obj = c.pyapi.from_native_value(typ.dtype, bblnx__nyjf, c.
                env_manager)
            pyarray_setitem(builder, context, yjo__rtyaa, rtyxt__uruh, arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(tsvk__ucotc)
    c.pyapi.decref(wwz__nas)
    c.pyapi.decref(dskj__cxs)
    c.pyapi.decref(uoac__ypl)
    return yjo__rtyaa


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    qgx__eoxr = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = qgx__eoxr.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), qgx__eoxr.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), qgx__eoxr.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        reod__mikng = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        vdqnp__njddi = c.context.make_helper(c.builder, typ.dtype, data_arr
            ).data
        uvrdu__mcfzx = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        enb__pze = cgutils.get_or_insert_function(c.builder.module,
            uvrdu__mcfzx, name='np_array_from_array_item_array')
        arr = c.builder.call(enb__pze, [qgx__eoxr.n_arrays, c.builder.
            bitcast(vdqnp__njddi, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), reod__mikng)])
    else:
        arr = _box_array_item_array_generic(typ, c, qgx__eoxr.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    vxsg__fpyg, docrk__meqp, tygy__lxcex = args
    hgr__hhbwf = bodo.utils.transform.get_type_alloc_counts(array_item_type
        .dtype)
    epz__hnank = sig.args[1]
    if not isinstance(epz__hnank, types.UniTuple):
        docrk__meqp = cgutils.pack_array(builder, [lir.Constant(lir.IntType
            (64), -1) for tygy__lxcex in range(hgr__hhbwf)])
    elif epz__hnank.count < hgr__hhbwf:
        docrk__meqp = cgutils.pack_array(builder, [builder.extract_value(
            docrk__meqp, qunqa__eqt) for qunqa__eqt in range(epz__hnank.
            count)] + [lir.Constant(lir.IntType(64), -1) for tygy__lxcex in
            range(hgr__hhbwf - epz__hnank.count)])
    fpq__isl, tygy__lxcex, tygy__lxcex, tygy__lxcex = (
        construct_array_item_array(context, builder, array_item_type,
        vxsg__fpyg, docrk__meqp))
    ssrld__pejue = context.make_helper(builder, array_item_type)
    ssrld__pejue.meminfo = fpq__isl
    return ssrld__pejue._getvalue()


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
    n_arrays, tux__kxss, ikonk__mnvq, ikkcj__zdu = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    kdmmk__iyb = context.get_value_type(payload_type)
    sle__lghbv = context.get_abi_sizeof(kdmmk__iyb)
    gemw__kxi = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    fpq__isl = context.nrt.meminfo_alloc_dtor(builder, context.get_constant
        (types.uintp, sle__lghbv), gemw__kxi)
    thkoy__eddbe = context.nrt.meminfo_data(builder, fpq__isl)
    buljl__pzwa = builder.bitcast(thkoy__eddbe, kdmmk__iyb.as_pointer())
    qgx__eoxr = cgutils.create_struct_proxy(payload_type)(context, builder)
    qgx__eoxr.n_arrays = n_arrays
    qgx__eoxr.data = tux__kxss
    qgx__eoxr.offsets = ikonk__mnvq
    qgx__eoxr.null_bitmap = ikkcj__zdu
    builder.store(qgx__eoxr._getvalue(), buljl__pzwa)
    context.nrt.incref(builder, signature.args[1], tux__kxss)
    context.nrt.incref(builder, signature.args[2], ikonk__mnvq)
    context.nrt.incref(builder, signature.args[3], ikkcj__zdu)
    ssrld__pejue = context.make_helper(builder, array_item_type)
    ssrld__pejue.meminfo = fpq__isl
    return ssrld__pejue._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    rfvp__qkkz = ArrayItemArrayType(data_type)
    sig = rfvp__qkkz(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        qgx__eoxr = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            qgx__eoxr.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        qgx__eoxr = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        vdqnp__njddi = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, qgx__eoxr.offsets).data
        ikonk__mnvq = builder.bitcast(vdqnp__njddi, lir.IntType(offset_type
            .bitwidth).as_pointer())
        return builder.load(builder.gep(ikonk__mnvq, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        qgx__eoxr = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            qgx__eoxr.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        qgx__eoxr = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            qgx__eoxr.null_bitmap)
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
        qgx__eoxr = _get_array_item_arr_payload(context, builder, arr_typ, arr)
        return qgx__eoxr.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, viqvi__ijvnd = args
        ssrld__pejue = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        thkoy__eddbe = context.nrt.meminfo_data(builder, ssrld__pejue.meminfo)
        buljl__pzwa = builder.bitcast(thkoy__eddbe, context.get_value_type(
            payload_type).as_pointer())
        qgx__eoxr = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(buljl__pzwa))
        context.nrt.decref(builder, data_typ, qgx__eoxr.data)
        qgx__eoxr.data = viqvi__ijvnd
        context.nrt.incref(builder, data_typ, viqvi__ijvnd)
        builder.store(qgx__eoxr._getvalue(), buljl__pzwa)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    tux__kxss = get_data(arr)
    esgd__fpax = len(tux__kxss)
    if esgd__fpax < new_size:
        mbo__knpl = max(2 * esgd__fpax, new_size)
        viqvi__ijvnd = bodo.libs.array_kernels.resize_and_copy(tux__kxss,
            old_size, mbo__knpl)
        replace_data_arr(arr, viqvi__ijvnd)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    tux__kxss = get_data(arr)
    ikonk__mnvq = get_offsets(arr)
    spg__cqi = len(tux__kxss)
    uobe__ygy = ikonk__mnvq[-1]
    if spg__cqi != uobe__ygy:
        viqvi__ijvnd = bodo.libs.array_kernels.resize_and_copy(tux__kxss,
            uobe__ygy, uobe__ygy)
        replace_data_arr(arr, viqvi__ijvnd)


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
            ikonk__mnvq = get_offsets(arr)
            tux__kxss = get_data(arr)
            bejdj__sann = ikonk__mnvq[ind]
            ldxv__uspjw = ikonk__mnvq[ind + 1]
            return tux__kxss[bejdj__sann:ldxv__uspjw]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        gcu__qvr = arr.dtype

        def impl_bool(arr, ind):
            ygik__genx = len(arr)
            if ygik__genx != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            ikkcj__zdu = get_null_bitmap(arr)
            n_arrays = 0
            oja__tut = init_nested_counts(gcu__qvr)
            for qunqa__eqt in range(ygik__genx):
                if ind[qunqa__eqt]:
                    n_arrays += 1
                    vfruf__hclu = arr[qunqa__eqt]
                    oja__tut = add_nested_counts(oja__tut, vfruf__hclu)
            yjo__rtyaa = pre_alloc_array_item_array(n_arrays, oja__tut,
                gcu__qvr)
            kcvlx__edkif = get_null_bitmap(yjo__rtyaa)
            vbh__joqcd = 0
            for oxy__bah in range(ygik__genx):
                if ind[oxy__bah]:
                    yjo__rtyaa[vbh__joqcd] = arr[oxy__bah]
                    act__twso = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        ikkcj__zdu, oxy__bah)
                    bodo.libs.int_arr_ext.set_bit_to_arr(kcvlx__edkif,
                        vbh__joqcd, act__twso)
                    vbh__joqcd += 1
            return yjo__rtyaa
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        gcu__qvr = arr.dtype

        def impl_int(arr, ind):
            ikkcj__zdu = get_null_bitmap(arr)
            ygik__genx = len(ind)
            n_arrays = ygik__genx
            oja__tut = init_nested_counts(gcu__qvr)
            for srlg__jgxm in range(ygik__genx):
                qunqa__eqt = ind[srlg__jgxm]
                vfruf__hclu = arr[qunqa__eqt]
                oja__tut = add_nested_counts(oja__tut, vfruf__hclu)
            yjo__rtyaa = pre_alloc_array_item_array(n_arrays, oja__tut,
                gcu__qvr)
            kcvlx__edkif = get_null_bitmap(yjo__rtyaa)
            for wimov__dpyd in range(ygik__genx):
                oxy__bah = ind[wimov__dpyd]
                yjo__rtyaa[wimov__dpyd] = arr[oxy__bah]
                act__twso = bodo.libs.int_arr_ext.get_bit_bitmap_arr(ikkcj__zdu
                    , oxy__bah)
                bodo.libs.int_arr_ext.set_bit_to_arr(kcvlx__edkif,
                    wimov__dpyd, act__twso)
            return yjo__rtyaa
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            ygik__genx = len(arr)
            psw__aqsx = numba.cpython.unicode._normalize_slice(ind, ygik__genx)
            fofz__jrktx = np.arange(psw__aqsx.start, psw__aqsx.stop,
                psw__aqsx.step)
            return arr[fofz__jrktx]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            ikonk__mnvq = get_offsets(A)
            ikkcj__zdu = get_null_bitmap(A)
            if idx == 0:
                ikonk__mnvq[0] = 0
            n_items = len(val)
            kpq__kpat = ikonk__mnvq[idx] + n_items
            ensure_data_capacity(A, ikonk__mnvq[idx], kpq__kpat)
            tux__kxss = get_data(A)
            ikonk__mnvq[idx + 1] = ikonk__mnvq[idx] + n_items
            tux__kxss[ikonk__mnvq[idx]:ikonk__mnvq[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(ikkcj__zdu, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            psw__aqsx = numba.cpython.unicode._normalize_slice(idx, len(A))
            for qunqa__eqt in range(psw__aqsx.start, psw__aqsx.stop,
                psw__aqsx.step):
                A[qunqa__eqt] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            ikonk__mnvq = get_offsets(A)
            ikkcj__zdu = get_null_bitmap(A)
            mkh__qachv = get_offsets(val)
            zhub__pllu = get_data(val)
            hrvu__vbl = get_null_bitmap(val)
            ygik__genx = len(A)
            psw__aqsx = numba.cpython.unicode._normalize_slice(idx, ygik__genx)
            mdbf__lcbo, rsml__qoc = psw__aqsx.start, psw__aqsx.stop
            assert psw__aqsx.step == 1
            if mdbf__lcbo == 0:
                ikonk__mnvq[mdbf__lcbo] = 0
            yxft__tga = ikonk__mnvq[mdbf__lcbo]
            kpq__kpat = yxft__tga + len(zhub__pllu)
            ensure_data_capacity(A, yxft__tga, kpq__kpat)
            tux__kxss = get_data(A)
            tux__kxss[yxft__tga:yxft__tga + len(zhub__pllu)] = zhub__pllu
            ikonk__mnvq[mdbf__lcbo:rsml__qoc + 1] = mkh__qachv + yxft__tga
            dqkcl__hmrr = 0
            for qunqa__eqt in range(mdbf__lcbo, rsml__qoc):
                act__twso = bodo.libs.int_arr_ext.get_bit_bitmap_arr(hrvu__vbl,
                    dqkcl__hmrr)
                bodo.libs.int_arr_ext.set_bit_to_arr(ikkcj__zdu, qunqa__eqt,
                    act__twso)
                dqkcl__hmrr += 1
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
