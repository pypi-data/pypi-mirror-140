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
    wyor__xtucg = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(wyor__xtucg)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        kygbo__gmo = _get_map_arr_data_type(fe_type)
        daux__bagq = [('data', kygbo__gmo)]
        models.StructModel.__init__(self, dmm, fe_type, daux__bagq)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    kdsn__ejd = all(isinstance(ije__dccz, types.Array) and ije__dccz.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) for
        ije__dccz in (typ.key_arr_type, typ.value_arr_type))
    if kdsn__ejd:
        cdb__wqb = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        mftp__iaig = cgutils.get_or_insert_function(c.builder.module,
            cdb__wqb, name='count_total_elems_list_array')
        hufj__hgq = cgutils.pack_array(c.builder, [n_maps, c.builder.call(
            mftp__iaig, [val])])
    else:
        hufj__hgq = get_array_elem_counts(c, c.builder, c.context, val, typ)
    kygbo__gmo = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, kygbo__gmo,
        hufj__hgq, c)
    ezvz__qocfu = _get_array_item_arr_payload(c.context, c.builder,
        kygbo__gmo, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, ezvz__qocfu.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, ezvz__qocfu.offsets).data
    ggxs__fdim = _get_struct_arr_payload(c.context, c.builder, kygbo__gmo.
        dtype, ezvz__qocfu.data)
    key_arr = c.builder.extract_value(ggxs__fdim.data, 0)
    value_arr = c.builder.extract_value(ggxs__fdim.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    ipb__obb, pexhl__qpid = c.pyapi.call_jit_code(lambda A: A.fill(255),
        sig, [ggxs__fdim.null_bitmap])
    if kdsn__ejd:
        bucvf__eger = c.context.make_array(kygbo__gmo.dtype.data[0])(c.
            context, c.builder, key_arr).data
        xmvu__fowm = c.context.make_array(kygbo__gmo.dtype.data[1])(c.
            context, c.builder, value_arr).data
        cdb__wqb = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        var__sut = cgutils.get_or_insert_function(c.builder.module,
            cdb__wqb, name='map_array_from_sequence')
        nzun__pbyfb = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        spcb__yinfn = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype
            )
        c.builder.call(var__sut, [val, c.builder.bitcast(bucvf__eger, lir.
            IntType(8).as_pointer()), c.builder.bitcast(xmvu__fowm, lir.
            IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), nzun__pbyfb), lir.Constant(lir.
            IntType(32), spcb__yinfn)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    luffv__plsw = c.context.make_helper(c.builder, typ)
    luffv__plsw.data = data_arr
    xzl__xvh = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(luffv__plsw._getvalue(), is_error=xzl__xvh)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    rzk__dvxt = context.insert_const_string(builder.module, 'pandas')
    afpm__pfnnp = c.pyapi.import_module_noblock(rzk__dvxt)
    tdgxq__vszx = c.pyapi.object_getattr_string(afpm__pfnnp, 'NA')
    aubqs__pbj = c.context.get_constant(offset_type, 0)
    builder.store(aubqs__pbj, offsets_ptr)
    zqrs__zvsuk = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as loop:
        eevfn__neib = loop.index
        item_ind = builder.load(zqrs__zvsuk)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [eevfn__neib]))
        fukh__vkskh = seq_getitem(builder, context, val, eevfn__neib)
        set_bitmap_bit(builder, null_bitmap_ptr, eevfn__neib, 0)
        hebz__elezi = is_na_value(builder, context, fukh__vkskh, tdgxq__vszx)
        vyjc__wwgid = builder.icmp_unsigned('!=', hebz__elezi, lir.Constant
            (hebz__elezi.type, 1))
        with builder.if_then(vyjc__wwgid):
            set_bitmap_bit(builder, null_bitmap_ptr, eevfn__neib, 1)
            twcj__afv = dict_keys(builder, context, fukh__vkskh)
            miq__wfz = dict_values(builder, context, fukh__vkskh)
            n_items = bodo.utils.utils.object_length(c, twcj__afv)
            _unbox_array_item_array_copy_data(typ.key_arr_type, twcj__afv,
                c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type, miq__wfz,
                c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), zqrs__zvsuk)
            c.pyapi.decref(twcj__afv)
            c.pyapi.decref(miq__wfz)
        c.pyapi.decref(fukh__vkskh)
    builder.store(builder.trunc(builder.load(zqrs__zvsuk), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(afpm__pfnnp)
    c.pyapi.decref(tdgxq__vszx)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    luffv__plsw = c.context.make_helper(c.builder, typ, val)
    data_arr = luffv__plsw.data
    kygbo__gmo = _get_map_arr_data_type(typ)
    ezvz__qocfu = _get_array_item_arr_payload(c.context, c.builder,
        kygbo__gmo, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, ezvz__qocfu.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, ezvz__qocfu.offsets).data
    ggxs__fdim = _get_struct_arr_payload(c.context, c.builder, kygbo__gmo.
        dtype, ezvz__qocfu.data)
    key_arr = c.builder.extract_value(ggxs__fdim.data, 0)
    value_arr = c.builder.extract_value(ggxs__fdim.data, 1)
    if all(isinstance(ije__dccz, types.Array) and ije__dccz.dtype in (types
        .int64, types.float64, types.bool_, datetime_date_type) for
        ije__dccz in (typ.key_arr_type, typ.value_arr_type)):
        bucvf__eger = c.context.make_array(kygbo__gmo.dtype.data[0])(c.
            context, c.builder, key_arr).data
        xmvu__fowm = c.context.make_array(kygbo__gmo.dtype.data[1])(c.
            context, c.builder, value_arr).data
        cdb__wqb = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        tce__ihz = cgutils.get_or_insert_function(c.builder.module,
            cdb__wqb, name='np_array_from_map_array')
        nzun__pbyfb = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        spcb__yinfn = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype
            )
        arr = c.builder.call(tce__ihz, [ezvz__qocfu.n_arrays, c.builder.
            bitcast(bucvf__eger, lir.IntType(8).as_pointer()), c.builder.
            bitcast(xmvu__fowm, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), nzun__pbyfb),
            lir.Constant(lir.IntType(32), spcb__yinfn)])
    else:
        arr = _box_map_array_generic(typ, c, ezvz__qocfu.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    rzk__dvxt = context.insert_const_string(builder.module, 'numpy')
    pxkw__eea = c.pyapi.import_module_noblock(rzk__dvxt)
    ayvfa__hjfyw = c.pyapi.object_getattr_string(pxkw__eea, 'object_')
    fdi__pjt = c.pyapi.long_from_longlong(n_maps)
    ieq__xul = c.pyapi.call_method(pxkw__eea, 'ndarray', (fdi__pjt,
        ayvfa__hjfyw))
    lgr__wosr = c.pyapi.object_getattr_string(pxkw__eea, 'nan')
    hzqka__hcxr = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    zqrs__zvsuk = cgutils.alloca_once_value(builder, lir.Constant(lir.
        IntType(64), 0))
    with cgutils.for_range(builder, n_maps) as loop:
        jeyf__kzspb = loop.index
        pyarray_setitem(builder, context, ieq__xul, jeyf__kzspb, lgr__wosr)
        gux__byi = get_bitmap_bit(builder, null_bitmap_ptr, jeyf__kzspb)
        gjt__klsor = builder.icmp_unsigned('!=', gux__byi, lir.Constant(lir
            .IntType(8), 0))
        with builder.if_then(gjt__klsor):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(jeyf__kzspb, lir.Constant(
                jeyf__kzspb.type, 1))])), builder.load(builder.gep(
                offsets_ptr, [jeyf__kzspb]))), lir.IntType(64))
            item_ind = builder.load(zqrs__zvsuk)
            fukh__vkskh = c.pyapi.dict_new()
            uuj__ifw = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            ipb__obb, byldf__llfgd = c.pyapi.call_jit_code(uuj__ifw, typ.
                key_arr_type(typ.key_arr_type, types.int64, types.int64), [
                key_arr, item_ind, n_items])
            ipb__obb, iantm__zyvc = c.pyapi.call_jit_code(uuj__ifw, typ.
                value_arr_type(typ.value_arr_type, types.int64, types.int64
                ), [value_arr, item_ind, n_items])
            qqmrn__zhwa = c.pyapi.from_native_value(typ.key_arr_type,
                byldf__llfgd, c.env_manager)
            ovjf__ifqi = c.pyapi.from_native_value(typ.value_arr_type,
                iantm__zyvc, c.env_manager)
            wne__qinah = c.pyapi.call_function_objargs(hzqka__hcxr, (
                qqmrn__zhwa, ovjf__ifqi))
            dict_merge_from_seq2(builder, context, fukh__vkskh, wne__qinah)
            builder.store(builder.add(item_ind, n_items), zqrs__zvsuk)
            pyarray_setitem(builder, context, ieq__xul, jeyf__kzspb,
                fukh__vkskh)
            c.pyapi.decref(wne__qinah)
            c.pyapi.decref(qqmrn__zhwa)
            c.pyapi.decref(ovjf__ifqi)
            c.pyapi.decref(fukh__vkskh)
    c.pyapi.decref(hzqka__hcxr)
    c.pyapi.decref(pxkw__eea)
    c.pyapi.decref(ayvfa__hjfyw)
    c.pyapi.decref(fdi__pjt)
    c.pyapi.decref(lgr__wosr)
    return ieq__xul


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    luffv__plsw = context.make_helper(builder, sig.return_type)
    luffv__plsw.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return luffv__plsw._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    igds__opvt = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return igds__opvt(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    zxg__yyrv = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        num_maps, nested_counts, struct_typ)
    return init_map_arr(zxg__yyrv)


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
    lcc__ujmt = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            rnr__hoa = val.keys()
            jbe__bforl = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len
                (val), (-1,), lcc__ujmt, ('key', 'value'))
            for pozj__byj, uumqt__evsq in enumerate(rnr__hoa):
                jbe__bforl[pozj__byj] = bodo.libs.struct_arr_ext.init_struct((
                    uumqt__evsq, val[uumqt__evsq]), ('key', 'value'))
            arr._data[ind] = jbe__bforl
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
            jqyz__aix = dict()
            qpad__bjbdi = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            jbe__bforl = bodo.libs.array_item_arr_ext.get_data(arr._data)
            addjn__urfne, pvdsr__psb = bodo.libs.struct_arr_ext.get_data(
                jbe__bforl)
            baxsh__mqg = qpad__bjbdi[ind]
            qvz__iysb = qpad__bjbdi[ind + 1]
            for pozj__byj in range(baxsh__mqg, qvz__iysb):
                jqyz__aix[addjn__urfne[pozj__byj]] = pvdsr__psb[pozj__byj]
            return jqyz__aix
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
