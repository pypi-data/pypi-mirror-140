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
    dxtem__usku = StructArrayType((map_type.key_arr_type, map_type.
        value_arr_type), ('key', 'value'))
    return ArrayItemArrayType(dxtem__usku)


@register_model(MapArrayType)
class MapArrayModel(models.StructModel):

    def __init__(self, dmm, fe_type):
        aeye__wsm = _get_map_arr_data_type(fe_type)
        qew__wmt = [('data', aeye__wsm)]
        models.StructModel.__init__(self, dmm, fe_type, qew__wmt)


make_attribute_wrapper(MapArrayType, 'data', '_data')


@unbox(MapArrayType)
def unbox_map_array(typ, val, c):
    n_maps = bodo.utils.utils.object_length(c, val)
    qwob__pbebp = all(isinstance(rjvbu__vccin, types.Array) and 
        rjvbu__vccin.dtype in (types.int64, types.float64, types.bool_,
        datetime_date_type) for rjvbu__vccin in (typ.key_arr_type, typ.
        value_arr_type))
    if qwob__pbebp:
        spdv__tzed = lir.FunctionType(lir.IntType(64), [lir.IntType(8).
            as_pointer()])
        okba__vle = cgutils.get_or_insert_function(c.builder.module,
            spdv__tzed, name='count_total_elems_list_array')
        epore__yzu = cgutils.pack_array(c.builder, [n_maps, c.builder.call(
            okba__vle, [val])])
    else:
        epore__yzu = get_array_elem_counts(c, c.builder, c.context, val, typ)
    aeye__wsm = _get_map_arr_data_type(typ)
    data_arr = gen_allocate_array(c.context, c.builder, aeye__wsm,
        epore__yzu, c)
    mws__ikjpl = _get_array_item_arr_payload(c.context, c.builder,
        aeye__wsm, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, mws__ikjpl.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, mws__ikjpl.offsets).data
    qjymt__gzrv = _get_struct_arr_payload(c.context, c.builder, aeye__wsm.
        dtype, mws__ikjpl.data)
    key_arr = c.builder.extract_value(qjymt__gzrv.data, 0)
    value_arr = c.builder.extract_value(qjymt__gzrv.data, 1)
    sig = types.none(types.Array(types.uint8, 1, 'C'))
    ipdm__ywec, dsdgf__qqgvp = c.pyapi.call_jit_code(lambda A: A.fill(255),
        sig, [qjymt__gzrv.null_bitmap])
    if qwob__pbebp:
        axnqo__aiuv = c.context.make_array(aeye__wsm.dtype.data[0])(c.
            context, c.builder, key_arr).data
        alpfj__gmj = c.context.make_array(aeye__wsm.dtype.data[1])(c.
            context, c.builder, value_arr).data
        spdv__tzed = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(offset_type.bitwidth).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
        rttkq__rpqk = cgutils.get_or_insert_function(c.builder.module,
            spdv__tzed, name='map_array_from_sequence')
        jwer__fukq = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        yjd__yczv = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        c.builder.call(rttkq__rpqk, [val, c.builder.bitcast(axnqo__aiuv,
            lir.IntType(8).as_pointer()), c.builder.bitcast(alpfj__gmj, lir
            .IntType(8).as_pointer()), offsets_ptr, null_bitmap_ptr, lir.
            Constant(lir.IntType(32), jwer__fukq), lir.Constant(lir.IntType
            (32), yjd__yczv)])
    else:
        _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
            offsets_ptr, null_bitmap_ptr)
    rsfdw__bldje = c.context.make_helper(c.builder, typ)
    rsfdw__bldje.data = data_arr
    mew__ptqc = cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return NativeValue(rsfdw__bldje._getvalue(), is_error=mew__ptqc)


def _unbox_map_array_generic(typ, val, c, n_maps, key_arr, value_arr,
    offsets_ptr, null_bitmap_ptr):
    from bodo.libs.array_item_arr_ext import _unbox_array_item_array_copy_data
    context = c.context
    builder = c.builder
    nsd__ejaih = context.insert_const_string(builder.module, 'pandas')
    melz__jtnei = c.pyapi.import_module_noblock(nsd__ejaih)
    vtq__bqv = c.pyapi.object_getattr_string(melz__jtnei, 'NA')
    ihyti__bkfhb = c.context.get_constant(offset_type, 0)
    builder.store(ihyti__bkfhb, offsets_ptr)
    cdb__yydp = cgutils.alloca_once_value(builder, context.get_constant(
        types.int64, 0))
    with cgutils.for_range(builder, n_maps) as loop:
        ukgej__lfzc = loop.index
        item_ind = builder.load(cdb__yydp)
        builder.store(builder.trunc(item_ind, lir.IntType(offset_type.
            bitwidth)), builder.gep(offsets_ptr, [ukgej__lfzc]))
        lgntv__qrws = seq_getitem(builder, context, val, ukgej__lfzc)
        set_bitmap_bit(builder, null_bitmap_ptr, ukgej__lfzc, 0)
        gcnhs__tcm = is_na_value(builder, context, lgntv__qrws, vtq__bqv)
        yio__uyhtv = builder.icmp_unsigned('!=', gcnhs__tcm, lir.Constant(
            gcnhs__tcm.type, 1))
        with builder.if_then(yio__uyhtv):
            set_bitmap_bit(builder, null_bitmap_ptr, ukgej__lfzc, 1)
            ngz__wjwx = dict_keys(builder, context, lgntv__qrws)
            uuu__doekq = dict_values(builder, context, lgntv__qrws)
            n_items = bodo.utils.utils.object_length(c, ngz__wjwx)
            _unbox_array_item_array_copy_data(typ.key_arr_type, ngz__wjwx,
                c, key_arr, item_ind, n_items)
            _unbox_array_item_array_copy_data(typ.value_arr_type,
                uuu__doekq, c, value_arr, item_ind, n_items)
            builder.store(builder.add(item_ind, n_items), cdb__yydp)
            c.pyapi.decref(ngz__wjwx)
            c.pyapi.decref(uuu__doekq)
        c.pyapi.decref(lgntv__qrws)
    builder.store(builder.trunc(builder.load(cdb__yydp), lir.IntType(
        offset_type.bitwidth)), builder.gep(offsets_ptr, [n_maps]))
    c.pyapi.decref(melz__jtnei)
    c.pyapi.decref(vtq__bqv)


@box(MapArrayType)
def box_map_arr(typ, val, c):
    rsfdw__bldje = c.context.make_helper(c.builder, typ, val)
    data_arr = rsfdw__bldje.data
    aeye__wsm = _get_map_arr_data_type(typ)
    mws__ikjpl = _get_array_item_arr_payload(c.context, c.builder,
        aeye__wsm, data_arr)
    null_bitmap_ptr = c.context.make_array(types.Array(types.uint8, 1, 'C'))(c
        .context, c.builder, mws__ikjpl.null_bitmap).data
    offsets_ptr = c.context.make_array(types.Array(offset_type, 1, 'C'))(c.
        context, c.builder, mws__ikjpl.offsets).data
    qjymt__gzrv = _get_struct_arr_payload(c.context, c.builder, aeye__wsm.
        dtype, mws__ikjpl.data)
    key_arr = c.builder.extract_value(qjymt__gzrv.data, 0)
    value_arr = c.builder.extract_value(qjymt__gzrv.data, 1)
    if all(isinstance(rjvbu__vccin, types.Array) and rjvbu__vccin.dtype in
        (types.int64, types.float64, types.bool_, datetime_date_type) for
        rjvbu__vccin in (typ.key_arr_type, typ.value_arr_type)):
        axnqo__aiuv = c.context.make_array(aeye__wsm.dtype.data[0])(c.
            context, c.builder, key_arr).data
        alpfj__gmj = c.context.make_array(aeye__wsm.dtype.data[1])(c.
            context, c.builder, value_arr).data
        spdv__tzed = lir.FunctionType(c.context.get_argument_type(types.
            pyobject), [lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(offset_type.bitwidth).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32), lir
            .IntType(32)])
        asptv__adm = cgutils.get_or_insert_function(c.builder.module,
            spdv__tzed, name='np_array_from_map_array')
        jwer__fukq = bodo.utils.utils.numba_to_c_type(typ.key_arr_type.dtype)
        yjd__yczv = bodo.utils.utils.numba_to_c_type(typ.value_arr_type.dtype)
        arr = c.builder.call(asptv__adm, [mws__ikjpl.n_arrays, c.builder.
            bitcast(axnqo__aiuv, lir.IntType(8).as_pointer()), c.builder.
            bitcast(alpfj__gmj, lir.IntType(8).as_pointer()), offsets_ptr,
            null_bitmap_ptr, lir.Constant(lir.IntType(32), jwer__fukq), lir
            .Constant(lir.IntType(32), yjd__yczv)])
    else:
        arr = _box_map_array_generic(typ, c, mws__ikjpl.n_arrays, key_arr,
            value_arr, offsets_ptr, null_bitmap_ptr)
    c.context.nrt.decref(c.builder, typ, val)
    return arr


def _box_map_array_generic(typ, c, n_maps, key_arr, value_arr, offsets_ptr,
    null_bitmap_ptr):
    context = c.context
    builder = c.builder
    nsd__ejaih = context.insert_const_string(builder.module, 'numpy')
    emzoz__uspie = c.pyapi.import_module_noblock(nsd__ejaih)
    sbrrb__kvele = c.pyapi.object_getattr_string(emzoz__uspie, 'object_')
    jlekd__qfws = c.pyapi.long_from_longlong(n_maps)
    ainjw__qsy = c.pyapi.call_method(emzoz__uspie, 'ndarray', (jlekd__qfws,
        sbrrb__kvele))
    tqcnh__jnkb = c.pyapi.object_getattr_string(emzoz__uspie, 'nan')
    qvwvw__jup = c.pyapi.unserialize(c.pyapi.serialize_object(zip))
    cdb__yydp = cgutils.alloca_once_value(builder, lir.Constant(lir.IntType
        (64), 0))
    with cgutils.for_range(builder, n_maps) as loop:
        uug__dyx = loop.index
        pyarray_setitem(builder, context, ainjw__qsy, uug__dyx, tqcnh__jnkb)
        sslmk__lzbm = get_bitmap_bit(builder, null_bitmap_ptr, uug__dyx)
        vroj__jsjx = builder.icmp_unsigned('!=', sslmk__lzbm, lir.Constant(
            lir.IntType(8), 0))
        with builder.if_then(vroj__jsjx):
            n_items = builder.sext(builder.sub(builder.load(builder.gep(
                offsets_ptr, [builder.add(uug__dyx, lir.Constant(uug__dyx.
                type, 1))])), builder.load(builder.gep(offsets_ptr, [
                uug__dyx]))), lir.IntType(64))
            item_ind = builder.load(cdb__yydp)
            lgntv__qrws = c.pyapi.dict_new()
            kvu__atcck = lambda data_arr, item_ind, n_items: data_arr[item_ind
                :item_ind + n_items]
            ipdm__ywec, frywr__hfqsp = c.pyapi.call_jit_code(kvu__atcck,
                typ.key_arr_type(typ.key_arr_type, types.int64, types.int64
                ), [key_arr, item_ind, n_items])
            ipdm__ywec, kvrkf__ajlts = c.pyapi.call_jit_code(kvu__atcck,
                typ.value_arr_type(typ.value_arr_type, types.int64, types.
                int64), [value_arr, item_ind, n_items])
            wtsx__nhs = c.pyapi.from_native_value(typ.key_arr_type,
                frywr__hfqsp, c.env_manager)
            eeu__gpqew = c.pyapi.from_native_value(typ.value_arr_type,
                kvrkf__ajlts, c.env_manager)
            tbq__xmda = c.pyapi.call_function_objargs(qvwvw__jup, (
                wtsx__nhs, eeu__gpqew))
            dict_merge_from_seq2(builder, context, lgntv__qrws, tbq__xmda)
            builder.store(builder.add(item_ind, n_items), cdb__yydp)
            pyarray_setitem(builder, context, ainjw__qsy, uug__dyx, lgntv__qrws
                )
            c.pyapi.decref(tbq__xmda)
            c.pyapi.decref(wtsx__nhs)
            c.pyapi.decref(eeu__gpqew)
            c.pyapi.decref(lgntv__qrws)
    c.pyapi.decref(qvwvw__jup)
    c.pyapi.decref(emzoz__uspie)
    c.pyapi.decref(sbrrb__kvele)
    c.pyapi.decref(jlekd__qfws)
    c.pyapi.decref(tqcnh__jnkb)
    return ainjw__qsy


def init_map_arr_codegen(context, builder, sig, args):
    data_arr, = args
    rsfdw__bldje = context.make_helper(builder, sig.return_type)
    rsfdw__bldje.data = data_arr
    context.nrt.incref(builder, sig.args[0], data_arr)
    return rsfdw__bldje._getvalue()


@intrinsic
def init_map_arr(typingctx, data_typ=None):
    assert isinstance(data_typ, ArrayItemArrayType) and isinstance(data_typ
        .dtype, StructArrayType)
    mke__heka = MapArrayType(data_typ.dtype.data[0], data_typ.dtype.data[1])
    return mke__heka(data_typ), init_map_arr_codegen


def alias_ext_init_map_arr(lhs_name, args, alias_map, arg_aliases):
    assert len(args) == 1
    numba.core.ir_utils._add_alias(lhs_name, args[0].name, alias_map,
        arg_aliases)


numba.core.ir_utils.alias_func_extensions['init_map_arr',
    'bodo.libs.map_arr_ext'] = alias_ext_init_map_arr


@numba.njit
def pre_alloc_map_array(num_maps, nested_counts, struct_typ):
    okseh__kgac = bodo.libs.array_item_arr_ext.pre_alloc_array_item_array(
        num_maps, nested_counts, struct_typ)
    return init_map_arr(okseh__kgac)


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
    sgoaj__rqd = arr.key_arr_type, arr.value_arr_type
    if isinstance(ind, types.Integer):

        def map_arr_setitem_impl(arr, ind, val):
            ipm__fzjeu = val.keys()
            egjy__wimed = bodo.libs.struct_arr_ext.pre_alloc_struct_array(len
                (val), (-1,), sgoaj__rqd, ('key', 'value'))
            for wgv__wvudt, jqr__vdj in enumerate(ipm__fzjeu):
                egjy__wimed[wgv__wvudt] = bodo.libs.struct_arr_ext.init_struct(
                    (jqr__vdj, val[jqr__vdj]), ('key', 'value'))
            arr._data[ind] = egjy__wimed
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
            uxaey__bora = dict()
            vialx__bmpyv = bodo.libs.array_item_arr_ext.get_offsets(arr._data)
            egjy__wimed = bodo.libs.array_item_arr_ext.get_data(arr._data)
            kxt__wbm, cux__dtdfq = bodo.libs.struct_arr_ext.get_data(
                egjy__wimed)
            wvo__aco = vialx__bmpyv[ind]
            civqq__evnjb = vialx__bmpyv[ind + 1]
            for wgv__wvudt in range(wvo__aco, civqq__evnjb):
                uxaey__bora[kxt__wbm[wgv__wvudt]] = cux__dtdfq[wgv__wvudt]
            return uxaey__bora
        return map_arr_getitem_impl
    raise BodoError(
        'operator.getitem with MapArrays is only supported with an integer index.'
        )
