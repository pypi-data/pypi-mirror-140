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
        fdnss__edowk = [('n_arrays', types.int64), ('data', fe_type.
            array_type.dtype), ('offsets', types.Array(offset_type, 1, 'C')
            ), ('null_bitmap', types.Array(types.uint8, 1, 'C'))]
        models.StructModel.__init__(self, dmm, fe_type, fdnss__edowk)


@register_model(ArrayItemArrayType)
class ArrayItemArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        payload_type = ArrayItemArrayPayloadType(fe_type)
        fdnss__edowk = [('meminfo', types.MemInfoPointer(payload_type))]
        models.StructModel.__init__(self, dmm, fe_type, fdnss__edowk)


def define_array_item_dtor(context, builder, array_item_type, payload_type):
    xow__ngi = builder.module
    jsu__nmm = lir.FunctionType(lir.VoidType(), [cgutils.voidptr_t])
    ezp__fhzaa = cgutils.get_or_insert_function(xow__ngi, jsu__nmm, name=
        '.dtor.array_item.{}'.format(array_item_type.dtype))
    if not ezp__fhzaa.is_declaration:
        return ezp__fhzaa
    ezp__fhzaa.linkage = 'linkonce_odr'
    builder = lir.IRBuilder(ezp__fhzaa.append_basic_block())
    fdhv__uvlh = ezp__fhzaa.args[0]
    mqghw__sxzy = context.get_value_type(payload_type).as_pointer()
    fse__ndtmc = builder.bitcast(fdhv__uvlh, mqghw__sxzy)
    mnfzq__dvbk = context.make_helper(builder, payload_type, ref=fse__ndtmc)
    context.nrt.decref(builder, array_item_type.dtype, mnfzq__dvbk.data)
    context.nrt.decref(builder, types.Array(offset_type, 1, 'C'),
        mnfzq__dvbk.offsets)
    context.nrt.decref(builder, types.Array(types.uint8, 1, 'C'),
        mnfzq__dvbk.null_bitmap)
    builder.ret_void()
    return ezp__fhzaa


def construct_array_item_array(context, builder, array_item_type, n_arrays,
    n_elems, c=None):
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    fikz__yxdkj = context.get_value_type(payload_type)
    kgu__jdffy = context.get_abi_sizeof(fikz__yxdkj)
    pzgx__rhn = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    cwa__pfmx = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, kgu__jdffy), pzgx__rhn)
    ypyh__saztw = context.nrt.meminfo_data(builder, cwa__pfmx)
    lpmp__kpduf = builder.bitcast(ypyh__saztw, fikz__yxdkj.as_pointer())
    mnfzq__dvbk = cgutils.create_struct_proxy(payload_type)(context, builder)
    mnfzq__dvbk.n_arrays = n_arrays
    pupte__szaf = n_elems.type.count
    psm__apf = builder.extract_value(n_elems, 0)
    mbw__cpmxx = cgutils.alloca_once_value(builder, psm__apf)
    auvw__lqtq = builder.icmp_signed('==', psm__apf, lir.Constant(psm__apf.
        type, -1))
    with builder.if_then(auvw__lqtq):
        builder.store(n_arrays, mbw__cpmxx)
    n_elems = cgutils.pack_array(builder, [builder.load(mbw__cpmxx)] + [
        builder.extract_value(n_elems, kegd__eyp) for kegd__eyp in range(1,
        pupte__szaf)])
    mnfzq__dvbk.data = gen_allocate_array(context, builder, array_item_type
        .dtype, n_elems, c)
    sax__ilnsi = builder.add(n_arrays, lir.Constant(lir.IntType(64), 1))
    fuif__yid = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(offset_type, 1, 'C'), [sax__ilnsi])
    offsets_ptr = fuif__yid.data
    builder.store(context.get_constant(offset_type, 0), offsets_ptr)
    builder.store(builder.trunc(builder.extract_value(n_elems, 0), lir.
        IntType(offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    mnfzq__dvbk.offsets = fuif__yid._getvalue()
    zqsh__bbya = builder.udiv(builder.add(n_arrays, lir.Constant(lir.
        IntType(64), 7)), lir.Constant(lir.IntType(64), 8))
    gudrm__fvw = bodo.utils.utils._empty_nd_impl(context, builder, types.
        Array(types.uint8, 1, 'C'), [zqsh__bbya])
    null_bitmap_ptr = gudrm__fvw.data
    mnfzq__dvbk.null_bitmap = gudrm__fvw._getvalue()
    builder.store(mnfzq__dvbk._getvalue(), lpmp__kpduf)
    return cwa__pfmx, mnfzq__dvbk.data, offsets_ptr, null_bitmap_ptr


def _unbox_array_item_array_copy_data(arr_typ, arr_obj, c, data_arr,
    item_ind, n_items):
    context = c.context
    builder = c.builder
    arr_obj = to_arr_obj_if_list_obj(c, context, builder, arr_obj, arr_typ)
    arr_val = c.pyapi.to_native_value(arr_typ, arr_obj).value
    sig = types.none(arr_typ, types.int64, types.int64, arr_typ)

    def copy_data(data_arr, item_ind, n_items, arr_val):
        data_arr[item_ind:item_ind + n_items] = arr_val
    fqlk__ikd, fnxu__ownov = c.pyapi.call_jit_code(copy_data, sig, [
        data_arr, item_ind, n_items, arr_val])
    c.context.nrt.decref(builder, arr_typ, arr_val)


def _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
    offsets_ptr, null_bitmap_ptr):
    context = c.context
    builder = c.builder
    yhct__jane = context.insert_const_string(builder.module, 'pandas')
    qakdn__bizyg = c.pyapi.import_module_noblock(yhct__jane)
    kvf__wzh = c.pyapi.object_getattr_string(qakdn__bizyg, 'NA')
    bqw__lccz = c.context.get_constant(offset_type, 0)
    builder.store(bqw__lccz, offsets_ptr)
    adv__mqif = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_arrays) as loop:
        vagn__xsgbb = loop.index
        item_ind = builder.load(adv__mqif)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [vagn__xsgbb]))
        arr_obj = seq_getitem(builder, context, val, vagn__xsgbb)
        set_bitmap_bit(builder, null_bitmap_ptr, vagn__xsgbb, 0)
        liyv__fipy = is_na_value(builder, context, arr_obj, kvf__wzh)
        zgx__rhxgw = builder.icmp_unsigned('!=', liyv__fipy, lir.Constant(
            liyv__fipy.type, 1))
        with builder.if_then(zgx__rhxgw):
            set_bitmap_bit(builder, null_bitmap_ptr, vagn__xsgbb, 1)
            n_items = bodo.utils.utils.object_length(c, arr_obj)
            _unbox_array_item_array_copy_data(typ.dtype, arr_obj, c,
                data_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), adv__mqif)
        c.pyapi.decref(arr_obj)
    builder.store(builder.trunc(builder.load(adv__mqif), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_arrays]))
    c.pyapi.decref(qakdn__bizyg)
    c.pyapi.decref(kvf__wzh)


@unbox(ArrayItemArrayType)
def unbox_array_item_array(typ, val, c):
    klpnp__bmr = isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (
        types.int64, types.float64, types.bool_, datetime_date_type)
    n_arrays = bodo.utils.utils.object_length(c, val)
    if klpnp__bmr:
        jsu__nmm = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        mqbn__vgrc = cgutils.get_or_insert_function(c.builder.module,
            jsu__nmm, name='count_total_elems_list_array')
        n_elems = cgutils.pack_array(c.builder, [c.builder.call(mqbn__vgrc,
            [val])])
    else:
        lhtit__vwg = get_array_elem_counts(c, c.builder, c.context, val, typ)
        n_elems = cgutils.pack_array(c.builder, [c.builder.extract_value(
            lhtit__vwg, kegd__eyp) for kegd__eyp in range(1, lhtit__vwg.
            type.count)])
    cwa__pfmx, data_arr, offsets_ptr, null_bitmap_ptr = (
        construct_array_item_array(c.context, c.builder, typ, n_arrays,
        n_elems, c))
    if klpnp__bmr:
        wrrb__hlmor = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        glz__okyvm = c.context.make_array(typ.dtype)(c.context, c.builder,
            data_arr).data
        jsu__nmm = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(
            offset_type.bitwidth).as_pointer(), lir.IntType(8).as_pointer(),
            lir.IntType(32)])
        ezp__fhzaa = cgutils.get_or_insert_function(c.builder.module,
            jsu__nmm, name='array_item_array_from_sequence')
        c.builder.call(ezp__fhzaa, [val, c.builder.bitcast(glz__okyvm, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), wrrb__hlmor)])
    else:
        _unbox_array_item_array_generic(typ, val, c, n_arrays, data_arr,
            offsets_ptr, null_bitmap_ptr)
    whmn__ntbb = c.context.make_helper(c.builder, typ)
    whmn__ntbb.meminfo = cwa__pfmx
    ujgna__ugaeg = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(whmn__ntbb._getvalue(), is_error=ujgna__ugaeg)


def _get_array_item_arr_payload(context, builder, arr_typ, arr):
    whmn__ntbb = context.make_helper(builder, arr_typ, arr)
    payload_type = ArrayItemArrayPayloadType(arr_typ)
    ypyh__saztw = context.nrt.meminfo_data(builder, whmn__ntbb.meminfo)
    lpmp__kpduf = builder.bitcast(ypyh__saztw, context.get_value_type(
        payload_type).as_pointer())
    mnfzq__dvbk = cgutils.create_struct_proxy(payload_type)(context,
        builder, builder.load(lpmp__kpduf))
    return mnfzq__dvbk


def _box_array_item_array_generic(typ, c, n_arrays, data_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    yhct__jane = context.insert_const_string(builder.module, 'numpy')
    biihy__mmgti = c.pyapi.import_module_noblock(yhct__jane)
    slm__kfip = c.pyapi.object_getattr_string(biihy__mmgti, 'object_')
    wokke__nbes = c.pyapi.long_from_longlong(n_arrays)
    ttv__rxc = c.pyapi.call_method(biihy__mmgti, 'ndarray', (wokke__nbes,
        slm__kfip))
    beocb__kac = c.pyapi.object_getattr_string(biihy__mmgti, 'nan')
    adv__mqif = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType
        (64), 0))
    with cgutils.for_range(builder, n_arrays) as loop:
        vagn__xsgbb = loop.index
        pyarray_setitem(builder, context, ttv__rxc, vagn__xsgbb, beocb__kac)
        ahgc__oct = get_bitmap_bit(builder, null_bitmap_ptr, vagn__xsgbb)
        imczw__vbfc = builder.icmp_unsigned('!=', ahgc__oct, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(imczw__vbfc):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(vagn__xsgbb, lir.Constant(
                vagn__xsgbb.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [vagn__xsgbb]))), lir.IntType(64))
            item_ind = builder.load(adv__mqif)
            fqlk__ikd, xcnaa__oluhu = c.pyapi.call_jit_code(lambda data_arr,
                item_ind, n_items: data_arr[item_ind:item_ind + n_items],
                typ.dtype(typ.dtype, types.int64, types.int64), [data_arr,
                item_ind, n_items])
            builder.store(builder.add(item_ind, n_items), adv__mqif)
            arr_obj = c.pyapi.from_native_value(typ.dtype, xcnaa__oluhu, c.
                env_manager)
            pyarray_setitem(builder, context, ttv__rxc, vagn__xsgbb, arr_obj)
            c.pyapi.decref(arr_obj)
    c.pyapi.decref(biihy__mmgti)
    c.pyapi.decref(slm__kfip)
    c.pyapi.decref(wokke__nbes)
    c.pyapi.decref(beocb__kac)
    return ttv__rxc


@box(ArrayItemArrayType)
def box_array_item_arr(typ, val, c):
    mnfzq__dvbk = _get_array_item_arr_payload(c.context, c.builder, typ, val)
    data_arr = mnfzq__dvbk.data
    offsets_ptr = c.context.make_helper(c.builder, types.Array(offset_type,
        1, 'C'), mnfzq__dvbk.offsets).data
    null_bitmap_ptr = c.context.make_helper(c.builder, types.Array(types.
        uint8, 1, 'C'), mnfzq__dvbk.null_bitmap).data
    if isinstance(typ.dtype, types.Array) and typ.dtype.dtype in (types.
        int64, types.float64, types.bool_, datetime_date_type):
        wrrb__hlmor = bodo.utils.utils.numba_to_c_type(typ.dtype.dtype)
        glz__okyvm = c.context.make_helper(c.builder, typ.dtype, data_arr).data
        jsu__nmm = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32)])
        oflm__tatx = cgutils.get_or_insert_function(c.builder.module,
            jsu__nmm, name='np_array_from_array_item_array')
        arr = c.builder.call(oflm__tatx, [mnfzq__dvbk.n_arrays, c.builder.
            bitcast(glz__okyvm, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), wrrb__hlmor)])
    else:
        arr = _box_array_item_array_generic(typ, c, mnfzq__dvbk.n_arrays,
            data_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def lower_pre_alloc_array_item_array(context, builder, sig, args):
    array_item_type = sig.return_type
    rnemm__orqd, izep__emnhj, eowu__uoi = args
    xvost__rnvrm = bodo.utils.transform.get_type_alloc_counts(array_item_type
        .dtype)
    bbsj__vrqyl = sig.args[1]
    if not isinstance(bbsj__vrqyl, types.UniTuple):
        izep__emnhj = cgutils.pack_array(builder, [lir.Constant(lir.IntType
            (64), -1) for eowu__uoi in range(xvost__rnvrm)])
    elif bbsj__vrqyl.count < xvost__rnvrm:
        izep__emnhj = cgutils.pack_array(builder, [builder.extract_value(
            izep__emnhj, kegd__eyp) for kegd__eyp in range(bbsj__vrqyl.
            count)] + [lir.Constant(lir.IntType(64), -1) for eowu__uoi in
            range(xvost__rnvrm - bbsj__vrqyl.count)])
    cwa__pfmx, eowu__uoi, eowu__uoi, eowu__uoi = construct_array_item_array(
        context, builder, array_item_type, rnemm__orqd, izep__emnhj)
    whmn__ntbb = context.make_helper(builder, array_item_type)
    whmn__ntbb.meminfo = cwa__pfmx
    return whmn__ntbb._getvalue()


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
    n_arrays, epczr__ttc, fuif__yid, gudrm__fvw = args
    array_item_type = signature.return_type
    payload_type = ArrayItemArrayPayloadType(array_item_type)
    fikz__yxdkj = context.get_value_type(payload_type)
    kgu__jdffy = context.get_abi_sizeof(fikz__yxdkj)
    pzgx__rhn = define_array_item_dtor(context, builder, array_item_type,
        payload_type)
    cwa__pfmx = context.nrt.meminfo_alloc_dtor(builder, context.
        get_constant(types.uintp, kgu__jdffy), pzgx__rhn)
    ypyh__saztw = context.nrt.meminfo_data(builder, cwa__pfmx)
    lpmp__kpduf = builder.bitcast(ypyh__saztw, fikz__yxdkj.as_pointer())
    mnfzq__dvbk = cgutils.create_struct_proxy(payload_type)(context, builder)
    mnfzq__dvbk.n_arrays = n_arrays
    mnfzq__dvbk.data = epczr__ttc
    mnfzq__dvbk.offsets = fuif__yid
    mnfzq__dvbk.null_bitmap = gudrm__fvw
    builder.store(mnfzq__dvbk._getvalue(), lpmp__kpduf)
    context.nrt.incref(builder, signature.args[1], epczr__ttc)
    context.nrt.incref(builder, signature.args[2], fuif__yid)
    context.nrt.incref(builder, signature.args[3], gudrm__fvw)
    whmn__ntbb = context.make_helper(builder, array_item_type)
    whmn__ntbb.meminfo = cwa__pfmx
    return whmn__ntbb._getvalue()


@intrinsic
def init_array_item_array(typingctx, n_arrays_typ, data_type, offsets_typ,
    null_bitmap_typ=None):
    assert null_bitmap_typ == types.Array(types.uint8, 1, 'C')
    dfxzt__qnvd = ArrayItemArrayType(data_type)
    sig = dfxzt__qnvd(types.int64, data_type, offsets_typ, null_bitmap_typ)
    return sig, init_array_item_array_codegen


@intrinsic
def get_offsets(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        mnfzq__dvbk = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            mnfzq__dvbk.offsets)
    return types.Array(offset_type, 1, 'C')(arr_typ), codegen


@intrinsic
def get_offsets_ind(typingctx, arr_typ, ind_t=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, ind = args
        mnfzq__dvbk = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        glz__okyvm = context.make_array(types.Array(offset_type, 1, 'C'))(
            context, builder, mnfzq__dvbk.offsets).data
        fuif__yid = builder.bitcast(glz__okyvm, lir.IntType(offset_type.
            bitwidth).as_pointer())
        return builder.load(builder.gep(fuif__yid, [ind]))
    return offset_type(arr_typ, types.int64), codegen


@intrinsic
def get_data(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        mnfzq__dvbk = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            mnfzq__dvbk.data)
    return arr_typ.dtype(arr_typ), codegen


@intrinsic
def get_null_bitmap(typingctx, arr_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType)

    def codegen(context, builder, sig, args):
        arr, = args
        mnfzq__dvbk = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return impl_ret_borrowed(context, builder, sig.return_type,
            mnfzq__dvbk.null_bitmap)
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
        mnfzq__dvbk = _get_array_item_arr_payload(context, builder, arr_typ,
            arr)
        return mnfzq__dvbk.n_arrays
    return types.int64(arr_typ), codegen


@intrinsic
def replace_data_arr(typingctx, arr_typ, data_typ=None):
    assert isinstance(arr_typ, ArrayItemArrayType
        ) and data_typ == arr_typ.dtype

    def codegen(context, builder, sig, args):
        arr, ygrq__icpa = args
        whmn__ntbb = context.make_helper(builder, arr_typ, arr)
        payload_type = ArrayItemArrayPayloadType(arr_typ)
        ypyh__saztw = context.nrt.meminfo_data(builder, whmn__ntbb.meminfo)
        lpmp__kpduf = builder.bitcast(ypyh__saztw, context.get_value_type(
            payload_type).as_pointer())
        mnfzq__dvbk = cgutils.create_struct_proxy(payload_type)(context,
            builder, builder.load(lpmp__kpduf))
        context.nrt.decref(builder, data_typ, mnfzq__dvbk.data)
        mnfzq__dvbk.data = ygrq__icpa
        context.nrt.incref(builder, data_typ, ygrq__icpa)
        builder.store(mnfzq__dvbk._getvalue(), lpmp__kpduf)
    return types.none(arr_typ, data_typ), codegen


@numba.njit(no_cpython_wrapper=True)
def ensure_data_capacity(arr, old_size, new_size):
    epczr__ttc = get_data(arr)
    ulgy__upo = len(epczr__ttc)
    if ulgy__upo < new_size:
        onru__ivo = max(2 * ulgy__upo, new_size)
        ygrq__icpa = bodo.libs.array_kernels.resize_and_copy(epczr__ttc,
            old_size, onru__ivo)
        replace_data_arr(arr, ygrq__icpa)


@numba.njit(no_cpython_wrapper=True)
def trim_excess_data(arr):
    epczr__ttc = get_data(arr)
    fuif__yid = get_offsets(arr)
    hhi__qejzj = len(epczr__ttc)
    imk__krydp = fuif__yid[-1]
    if hhi__qejzj != imk__krydp:
        ygrq__icpa = bodo.libs.array_kernels.resize_and_copy(epczr__ttc,
            imk__krydp, imk__krydp)
        replace_data_arr(arr, ygrq__icpa)


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
            fuif__yid = get_offsets(arr)
            epczr__ttc = get_data(arr)
            yalp__frw = fuif__yid[ind]
            gmbn__efpf = fuif__yid[ind + 1]
            return epczr__ttc[yalp__frw:gmbn__efpf]
        return array_item_arr_getitem_impl
    if is_list_like_index_type(ind) and ind.dtype == types.bool_:
        lxmrp__wlu = arr.dtype

        def impl_bool(arr, ind):
            ayzxx__ncgry = len(arr)
            if ayzxx__ncgry != len(ind):
                raise IndexError(
                    'boolean index did not match indexed array along dimension 0'
                    )
            gudrm__fvw = get_null_bitmap(arr)
            n_arrays = 0
            pfidm__vvd = init_nested_counts(lxmrp__wlu)
            for kegd__eyp in range(ayzxx__ncgry):
                if ind[kegd__eyp]:
                    n_arrays += 1
                    pvy__ktgmv = arr[kegd__eyp]
                    pfidm__vvd = add_nested_counts(pfidm__vvd, pvy__ktgmv)
            ttv__rxc = pre_alloc_array_item_array(n_arrays, pfidm__vvd,
                lxmrp__wlu)
            ctd__kuhm = get_null_bitmap(ttv__rxc)
            sbzp__ptio = 0
            for xcag__cna in range(ayzxx__ncgry):
                if ind[xcag__cna]:
                    ttv__rxc[sbzp__ptio] = arr[xcag__cna]
                    vpazb__dhaoi = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                        gudrm__fvw, xcag__cna)
                    bodo.libs.int_arr_ext.set_bit_to_arr(ctd__kuhm,
                        sbzp__ptio, vpazb__dhaoi)
                    sbzp__ptio += 1
            return ttv__rxc
        return impl_bool
    if is_list_like_index_type(ind) and isinstance(ind.dtype, types.Integer):
        lxmrp__wlu = arr.dtype

        def impl_int(arr, ind):
            gudrm__fvw = get_null_bitmap(arr)
            ayzxx__ncgry = len(ind)
            n_arrays = ayzxx__ncgry
            pfidm__vvd = init_nested_counts(lxmrp__wlu)
            for muyu__nju in range(ayzxx__ncgry):
                kegd__eyp = ind[muyu__nju]
                pvy__ktgmv = arr[kegd__eyp]
                pfidm__vvd = add_nested_counts(pfidm__vvd, pvy__ktgmv)
            ttv__rxc = pre_alloc_array_item_array(n_arrays, pfidm__vvd,
                lxmrp__wlu)
            ctd__kuhm = get_null_bitmap(ttv__rxc)
            for pqfp__kmm in range(ayzxx__ncgry):
                xcag__cna = ind[pqfp__kmm]
                ttv__rxc[pqfp__kmm] = arr[xcag__cna]
                vpazb__dhaoi = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    gudrm__fvw, xcag__cna)
                bodo.libs.int_arr_ext.set_bit_to_arr(ctd__kuhm, pqfp__kmm,
                    vpazb__dhaoi)
            return ttv__rxc
        return impl_int
    if isinstance(ind, types.SliceType):

        def impl_slice(arr, ind):
            ayzxx__ncgry = len(arr)
            pstpa__zzt = numba.cpython.unicode._normalize_slice(ind,
                ayzxx__ncgry)
            grj__dycx = np.arange(pstpa__zzt.start, pstpa__zzt.stop,
                pstpa__zzt.step)
            return arr[grj__dycx]
        return impl_slice


@overload(operator.setitem)
def array_item_arr_setitem(A, idx, val):
    if not isinstance(A, ArrayItemArrayType):
        return
    if isinstance(idx, types.Integer):

        def impl_scalar(A, idx, val):
            fuif__yid = get_offsets(A)
            gudrm__fvw = get_null_bitmap(A)
            if idx == 0:
                fuif__yid[0] = 0
            n_items = len(val)
            ois__qbdia = fuif__yid[idx] + n_items
            ensure_data_capacity(A, fuif__yid[idx], ois__qbdia)
            epczr__ttc = get_data(A)
            fuif__yid[idx + 1] = fuif__yid[idx] + n_items
            epczr__ttc[fuif__yid[idx]:fuif__yid[idx + 1]] = val
            bodo.libs.int_arr_ext.set_bit_to_arr(gudrm__fvw, idx, 1)
        return impl_scalar
    if isinstance(idx, types.SliceType) and A.dtype == val:

        def impl_slice_elem(A, idx, val):
            pstpa__zzt = numba.cpython.unicode._normalize_slice(idx, len(A))
            for kegd__eyp in range(pstpa__zzt.start, pstpa__zzt.stop,
                pstpa__zzt.step):
                A[kegd__eyp] = val
        return impl_slice_elem
    if isinstance(idx, types.SliceType) and is_iterable_type(val):

        def impl_slice(A, idx, val):
            val = bodo.utils.conversion.coerce_to_array(val,
                use_nullable_array=True)
            fuif__yid = get_offsets(A)
            gudrm__fvw = get_null_bitmap(A)
            gmygf__roxfg = get_offsets(val)
            hmfz__bohy = get_data(val)
            oxh__mkl = get_null_bitmap(val)
            ayzxx__ncgry = len(A)
            pstpa__zzt = numba.cpython.unicode._normalize_slice(idx,
                ayzxx__ncgry)
            rufe__ilo, jzzo__rveu = pstpa__zzt.start, pstpa__zzt.stop
            assert pstpa__zzt.step == 1
            if rufe__ilo == 0:
                fuif__yid[rufe__ilo] = 0
            rip__jqyu = fuif__yid[rufe__ilo]
            ois__qbdia = rip__jqyu + len(hmfz__bohy)
            ensure_data_capacity(A, rip__jqyu, ois__qbdia)
            epczr__ttc = get_data(A)
            epczr__ttc[rip__jqyu:rip__jqyu + len(hmfz__bohy)] = hmfz__bohy
            fuif__yid[rufe__ilo:jzzo__rveu + 1] = gmygf__roxfg + rip__jqyu
            vxb__jdtgq = 0
            for kegd__eyp in range(rufe__ilo, jzzo__rveu):
                vpazb__dhaoi = bodo.libs.int_arr_ext.get_bit_bitmap_arr(
                    oxh__mkl, vxb__jdtgq)
                bodo.libs.int_arr_ext.set_bit_to_arr(gudrm__fvw, kegd__eyp,
                    vpazb__dhaoi)
                vxb__jdtgq += 1
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
