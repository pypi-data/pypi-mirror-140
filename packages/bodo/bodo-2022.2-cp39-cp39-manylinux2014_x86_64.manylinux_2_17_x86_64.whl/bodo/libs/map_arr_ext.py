"""Array implementation for map values.
Corresponds to Spark's MapType: https://spark.apache.org/docs/latest/sql-reference.html
Corresponds to Arrow's Map arrays: https://github.com/apache/arrow/blob/master/format/Schema.fbs

The implementation uses an array(struct) array underneath similar to Spark and Arrow.
For example: [{1: 2.1, 3: 1.1}, {5: -1.0}]
[[{"key": 1, "value" 2.1}, {"key": 3, "value": 1.1}], [{"key": 5, "value": -1.0}]]
"""
import operator
import llvmlite.binding as ll
import numba
import numpy as np
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.extending import NativeValue, box, intrinsic, make_attribute_wrapper, models, overload, overload_attribute, overload_method, register_model, unbox
from numba.parfors.array_analysis import ArrayAnalysis
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_type
from bodo.libs.array_item_arr_ext import ArrayItemArrayType, _get_array_item_arr_payload, offset_type
from bodo.libs.struct_arr_ext import StructArrayType, _get_struct_arr_payload
from bodo.utils.cg_helpers import dict_keys, dict_merge_from_seq2, dict_values, gen_allocate_array, get_array_elem_counts, get_bitmap_bit, is_na_value, pyarray_setitem, seq_getitem, set_bitmap_bit
from bodo.utils.typing import BodoError
from bodo.libs import array_ext, hdist
ll.add_symbol('count_total_elems_list_array', array_ext.
    count_total_elems_list_array)
ll.add_symbol('map_array_from_sequence', array_ext.map_array_from_sequence)
ll.add_symbol('np_array_from_map_array', array_ext.np_array_from_map_array)


class MapArrayType(types.ArrayCompatible):

    def __init__(self, key_arr_type, value_arr_type):
        self.key_arr_type = key_arr_type
        self.value_arr_type = value_arr_type
        super(MapArrayType, self).__init__(name='MapArrayType({}, {})'.
            format(key_arr_type, value_arr_type))

    @property
    def as_array(self):
        return types.Array(types.undefined, 1, 'C')

    @property
    def dtype(self):
        return types.DictType(self.key_arr_type.dtype, self.value_arr_type.
            dtype)

    def copy(self):
        return MapArrayType(self.key_arr_type, self.value_arr_type)

    @property
    def mangling_args(self):
        return self.__class__.__name__, (self._code,)


def _get_map_arr_data_type(map_type):
    yirsg__uaic = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(yirsg__uaic)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        zpz__cgfv = _get_map_arr_data_type(fe_type)
        qxg__huukh = [('data', zpz__cgfv)]
        models.StructModel.__init__(self, dmm, fe_type, qxg__huukh)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    jeo__ber = all(isinstance(maud__qqy, types.Array) and maud__qqy.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) for
        maud__qqy in (typ.key_arr_type, typ.value_arr_type))
    if jeo__ber:
        xic__qedou = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        vdl__uyny = cgutils.get_or_insert_function(c.builder.module,
            xic__qedou, name='count_total_elems_list_array')
        xgl__rlxk = cgutils.pack_array(c.builder, [n_maps, c.builder.call(
            vdl__uyny, [val])])
    else:
        xgl__rlxk = get_array_elem_counts(c, c.builder, c.context, val, typ)
    zpz__cgfv = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, zpz__cgfv, xgl__rlxk, c
        )
    osxmg__ikbb = _get_array_item_arr_payload(c.context, c.builder,
        zpz__cgfv, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, osxmg__ikbb.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, osxmg__ikbb.offsets).data
    hcpmg__gdxi = _get_struct_arr_payload(c.context, c.builder, zpz__cgfv.
        dtype, osxmg__ikbb.data)
    key_arr = c.builder.extract_value(hcpmg__gdxi.data, 0)
    value_arr = c.builder.extract_value(hcpmg__gdxi.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    oge__cnewg, gphg__rdt = c.pyapi.call_jit_code(lambda A: A.fill(255),
        sig, [hcpmg__gdxi.null_bitmap])
    if jeo__ber:
        ecn__iiw = c.context.make_array(zpz__cgfv.dtype.data[0])(c.context,
            c.builder, key_arr).data
        wgo__xkgf = c.context.make_array(zpz__cgfv.dtype.data[1])(c.context,
            c.builder, value_arr).data
        xic__qedou = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        zfmq__eajm = cgutils.get_or_insert_function(c.builder.module,
            xic__qedou, name='map_array_from_sequence')
        askyf__ikwn = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        zecpc__qaclc = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.
            dtype)
        c.builder.call(zfmq__eajm, [val, c.builder.bitcast(ecn__iiw, lir.
            IntType(8).as_pointer()), c.builder.bitcast(wgo__xkgf, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), askyf__ikwn), lir.Constant(lir.
            IntType(32), zecpc__qaclc)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    uqbp__knutn = c.context.make_helper(c.builder, typ)
    uqbp__knutn.data = data_arr
    vdvf__uysq = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(uqbp__knutn._getvalue(), is_error=vdvf__uysq)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    ggjn__ojx = context.insert_const_string(builder.module, 'pandas')
    gfgg__sshw = c.pyapi.import_module_noblock(ggjn__ojx)
    uymk__bcpo = c.pyapi.object_getattr_string(gfgg__sshw, 'NA')
    chw__qcl = c.context.get_constant(offset_type, 0)
    builder.store(chw__qcl, offsets_ptr)
    ulu__oos = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as loop:
        azye__nrbll = loop.index
        item_ind = builder.load(ulu__oos)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [azye__nrbll]))
        zti__ddgs = seq_getitem(builder, context, val, azye__nrbll)
        set_bitmap_bit(builder, null_bitmap_ptr, azye__nrbll, 0)
        stewe__qyk = is_na_value(builder, context, zti__ddgs, uymk__bcpo)
        kkras__nij = builder.icmp_unsigned('!=', stewe__qyk, lir.Constant(
            stewe__qyk.type, 1))
        with builder.if_then(kkras__nij):
            set_bitmap_bit(builder, null_bitmap_ptr, azye__nrbll, 1)
            bcfaw__ekeqa = dict_keys(builder, context, zti__ddgs)
            xpj__wbs = dict_values(builder, context, zti__ddgs)
            n_items = bodo.utils.utils.object_length(c, bcfaw__ekeqa)
            _unbox_array_item_array_copy_data(typ.key_arr_type,
                bcfaw__ekeqa, c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type, xpj__wbs,
                c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), ulu__oos)
            c.pyapi.decref(bcfaw__ekeqa)
            c.pyapi.decref(xpj__wbs)
        c.pyapi.decref(zti__ddgs)
    builder.store(builder.trunc(builder.load(ulu__oos), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(gfgg__sshw)
    c.pyapi.decref(uymk__bcpo)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    uqbp__knutn = c.context.make_helper(c.builder, typ, val)
    data_arr = uqbp__knutn.data
    zpz__cgfv = _get_map_arr_data_type(typ)
    osxmg__ikbb = _get_array_item_arr_payload(c.context, c.builder,
        zpz__cgfv, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, osxmg__ikbb.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, osxmg__ikbb.offsets).data
    hcpmg__gdxi = _get_struct_arr_payload(c.context, c.builder, zpz__cgfv.
        dtype, osxmg__ikbb.data)
    key_arr = c.builder.extract_value(hcpmg__gdxi.data, 0)
    value_arr = c.builder.extract_value(hcpmg__gdxi.data, 1)
    if all(isinstance(maud__qqy, types.Array) and maud__qqy.dtype in (types
        .int64, types.float64, types.bool_, datetime_date_type) for
        maud__qqy in (typ.key_arr_type, typ.value_arr_type)):
        ecn__iiw = c.context.make_array(zpz__cgfv.dtype.data[0])(c.context,
            c.builder, key_arr).data
        wgo__xkgf = c.context.make_array(zpz__cgfv.dtype.data[1])(c.context,
            c.builder, value_arr).data
        xic__qedou = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        okc__oemu = cgutils.get_or_insert_function(c.builder.module,
            xic__qedou, name='np_array_from_map_array')
        askyf__ikwn = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        zecpc__qaclc = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.
            dtype)
        arr = c.builder.call(okc__oemu, [osxmg__ikbb.n_arrays, c.builder.
            bitcast(ecn__iiw, lir.IntType(8).as_pointer()), c.builder.
            bitcast(wgo__xkgf, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), askyf__ikwn),
            lir.Constant(lir.IntType(32), zecpc__qaclc)])
    else:
        arr = _box_map_array_generic(typ, c, osxmg__ikbb.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    ggjn__ojx = context.insert_const_string(builder.module, 'numpy')
    jsku__dvbc = c.pyapi.import_module_noblock(ggjn__ojx)
    zarm__kvqhl = c.pyapi.object_getattr_string(jsku__dvbc, 'object_')
    qlxec__ohiap = c.pyapi.long_from_longlong(n_maps)
    oaac__zlf = c.pyapi.call_method(jsku__dvbc, 'ndarray', (qlxec__ohiap,
        zarm__kvqhl))
    ojk__rsnf = c.pyapi.object_getattr_string(jsku__dvbc, 'nan')
    yqy__pzjdb = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    ulu__oos = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType(
        64), 0))
    with cgutils.for_range(builder, n_maps) as loop:
        bcfdo__fwsw = loop.index
        pyarray_setitem(builder, context, oaac__zlf, bcfdo__fwsw, ojk__rsnf)
        udli__scdx = get_bitmap_bit(builder, null_bitmap_ptr, bcfdo__fwsw)
        kfy__yhij = builder.icmp_unsigned('!=', udli__scdx, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(kfy__yhij):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(bcfdo__fwsw, lir.Constant(
                bcfdo__fwsw.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [bcfdo__fwsw]))), lir.IntType(64))
            item_ind = builder.load(ulu__oos)
            zti__ddgs = c.pyapi.dict_new()
            wuwjx__npu = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            oge__cnewg, mykr__bhaf = c.pyapi.call_jit_code(wuwjx__npu, typ.
                key_arr_type(typ.key_arr_type, types.int64, types.int64), [
                key_arr, item_ind, n_items])
            oge__cnewg, wqnjz__xfa = c.pyapi.call_jit_code(wuwjx__npu, typ.
                value_arr_type(typ.value_arr_type, types.int64, types.int64
                ), [value_arr, item_ind, n_items])
            cwhm__qidy = c.pyapi.from_native_value(typ.key_arr_type,
                mykr__bhaf, c.env_manager)
            xtjm__zis = c.pyapi.from_native_value(typ.value_arr_type,
                wqnjz__xfa, c.env_manager)
            vlehv__ctb = c.pyapi.call_function_objargs(yqy__pzjdb, (
                cwhm__qidy, xtjm__zis))
            dict_merge_from_seq2(builder, context, zti__ddgs, vlehv__ctb)
            builder.store(builder.add(item_ind, n_items), ulu__oos)
            pyarray_setitem(builder, context, oaac__zlf, bcfdo__fwsw, zti__ddgs
                )
            c.pyapi.decref(vlehv__ctb)
            c.pyapi.decref(cwhm__qidy)
            c.pyapi.decref(xtjm__zis)
            c.pyapi.decref(zti__ddgs)
    c.pyapi.decref(yqy__pzjdb)
    c.pyapi.decref(jsku__dvbc)
    c.pyapi.decref(zarm__kvqhl)
    c.pyapi.decref(qlxec__ohiap)
    c.pyapi.decref(ojk__rsnf)
    return oaac__zlf


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    uqbp__knutn = context.make_helper(builder, sig.return_type)
    uqbp__knutn.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return uqbp__knutn._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    ktj__prqv = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return ktj__prqv(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    gkqi__ypxjf = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        num_maps, nested_counts, struct_typ)
    return init_map_arr(gkqi__ypxjf)


def pre_alloc_map_array_equiv(self, scope, equiv_set, loc, args, kws):
    assert len(args) == 3 and not kws
    return ArrayAnalysis.AnalyzeResult(shape=args[0], pre=[])


(ArrayAnalysis._analyze_op_call_bodo_libs_map_arr_ext_pre_alloc_map_array
    ) = pre_alloc_map_array_equiv


@overload(len, no_unliteral=True)
def overload_map_arr_len(A):
    if isinstance(A, MapArrayType):
        return lambda A: len(A._data)


@overload_attribute(MapArrayType, 'shape')
def overload_map_arr_shape(A):
    return lambda A: (len(A._data),)


@overload_attribute(MapArrayType, 'dtype')
def overload_map_arr_dtype(A):
    return lambda A: np.object_


@overload_attribute(MapArrayType, 'ndim')
def overload_map_arr_ndim(A):
    return lambda A: 1


@overload_attribute(MapArrayType, 'nbytes')
def overload_map_arr_nbytes(A):
    return lambda A: A._data.nbytes


@overload_method(MapArrayType, 'copy')
def overload_map_arr_copy(A):
    return lambda A: init_map_arr(A._data.copy())


@overload(operator.setitem, no_unliteral=True)
def map_arr_setitem(arr, ind, val):
    if not isinstance(arr, MapArrayType):
        return
    qtymp__nslni = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            hqy__shke = val.keys()
            grwzu__ity = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len
                (val), (-1,), qtymp__nslni, ('key', 'value'))
            for huzi__ihjei, zhqm__unff in enumerate(hqy__shke):
                grwzu__ity[huzi__ihjei] = bodo.libs.struct_arr_ext.init_struct(
                    (zhqm__unff, val[zhqm__unff]), ('key', 'value'))
            arr._data[ind] = grwzu__ity
        return map_arr_setitem_impl
    raise BodoError(
        'operator.setitem with MapArrays is only supported with an integer index.'
        )


@overload(operator.getitem, no_unliteral=True)
def map_arr_getitem(arr, ind):
    if not isinstance(arr, MapArrayType):
        return
    if isinstance(ind, types.Integer):

        def map_arr_getitem_impl(arr, ind):
            if ind < 0:
                ind += len(arr)
            swyya__lmqb = dict()
            kentp__qdff = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            grwzu__ity = bodo.libs.array_item_arr_ext.get_data(arr._data)
            yowck__wiz, evbkw__ipovc = bodo.libs.struct_arr_ext.get_data(
                grwzu__ity)
            lazau__ony = kentp__qdff[ind]
            qxrl__zdx = kentp__qdff[ind + 1]
            for huzi__ihjei in range(lazau__ony, qxrl__zdx):
                swyya__lmqb[yowck__wiz[huzi__ihjei]] = evbkw__ipovc[huzi__ihjei
                    ]
            return swyya__lmqb
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
