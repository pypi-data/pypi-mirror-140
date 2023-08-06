"""Tools for handling bodo arrays, e.g. passing to C/C++ code
"""
import llvmlite.binding as ll
import numba
import numpy as np
import pandas as pd
from llvmlite import ir as lir
from numba.core import cgutils, types
from numba.core.typing.templates import signature
from numba.cpython.listobj import ListInstance
from numba.extending import intrinsic, models, register_model
from numba.np.arrayobj import _getitem_array_single_int
import bodo
from bodo.hiframes.datetime_date_ext import datetime_date_array_type
from bodo.hiframes.pd_categorical_ext import CategoricalArrayType, get_categories_int_type
from bodo.libs import array_ext
from bodo.libs.array_item_arr_ext import ArrayItemArrayPayloadType, ArrayItemArrayType, _get_array_item_arr_payload, define_array_item_dtor, offset_type
from bodo.libs.binary_arr_ext import binary_array_type
from bodo.libs.bool_arr_ext import boolean_array
from bodo.libs.decimal_arr_ext import DecimalArrayType, int128_type
from bodo.libs.int_arr_ext import IntegerArrayType
from bodo.libs.interval_arr_ext import IntervalArrayType
from bodo.libs.map_arr_ext import MapArrayType, _get_map_arr_data_type, init_map_arr_codegen
from bodo.libs.str_arr_ext import _get_str_binary_arr_payload, char_arr_type, null_bitmap_arr_type, offset_arr_type, string_array_type
from bodo.libs.struct_arr_ext import StructArrayPayloadType, StructArrayType, StructType, _get_struct_arr_payload, define_struct_arr_dtor
from bodo.libs.tuple_arr_ext import TupleArrayType
from bodo.utils.typing import BodoError, MetaType
from bodo.utils.utils import CTypeEnum, check_and_propagate_cpp_exception, numba_to_c_type
ll.add_symbol('list_string_array_to_info', array_ext.list_string_array_to_info)
ll.add_symbol('nested_array_to_info', array_ext.nested_array_to_info)
ll.add_symbol('string_array_to_info', array_ext.string_array_to_info)
ll.add_symbol('numpy_array_to_info', array_ext.numpy_array_to_info)
ll.add_symbol('categorical_array_to_info', array_ext.categorical_array_to_info)
ll.add_symbol('nullable_array_to_info', array_ext.nullable_array_to_info)
ll.add_symbol('interval_array_to_info', array_ext.interval_array_to_info)
ll.add_symbol('decimal_array_to_info', array_ext.decimal_array_to_info)
ll.add_symbol('info_to_nested_array', array_ext.info_to_nested_array)
ll.add_symbol('info_to_list_string_array', array_ext.info_to_list_string_array)
ll.add_symbol('info_to_string_array', array_ext.info_to_string_array)
ll.add_symbol('info_to_numpy_array', array_ext.info_to_numpy_array)
ll.add_symbol('info_to_nullable_array', array_ext.info_to_nullable_array)
ll.add_symbol('info_to_interval_array', array_ext.info_to_interval_array)
ll.add_symbol('alloc_numpy', array_ext.alloc_numpy)
ll.add_symbol('alloc_string_array', array_ext.alloc_string_array)
ll.add_symbol('arr_info_list_to_table', array_ext.arr_info_list_to_table)
ll.add_symbol('info_from_table', array_ext.info_from_table)
ll.add_symbol('delete_info_decref_array', array_ext.delete_info_decref_array)
ll.add_symbol('delete_table_decref_arrays', array_ext.
    delete_table_decref_arrays)
ll.add_symbol('delete_table', array_ext.delete_table)
ll.add_symbol('shuffle_table', array_ext.shuffle_table)
ll.add_symbol('get_shuffle_info', array_ext.get_shuffle_info)
ll.add_symbol('delete_shuffle_info', array_ext.delete_shuffle_info)
ll.add_symbol('reverse_shuffle_table', array_ext.reverse_shuffle_table)
ll.add_symbol('hash_join_table', array_ext.hash_join_table)
ll.add_symbol('drop_duplicates_table', array_ext.drop_duplicates_table)
ll.add_symbol('sort_values_table', array_ext.sort_values_table)
ll.add_symbol('sample_table', array_ext.sample_table)
ll.add_symbol('shuffle_renormalization', array_ext.shuffle_renormalization)
ll.add_symbol('shuffle_renormalization_group', array_ext.
    shuffle_renormalization_group)
ll.add_symbol('groupby_and_aggregate', array_ext.groupby_and_aggregate)
ll.add_symbol('pivot_groupby_and_aggregate', array_ext.
    pivot_groupby_and_aggregate)
ll.add_symbol('get_groupby_labels', array_ext.get_groupby_labels)
ll.add_symbol('array_isin', array_ext.array_isin)
ll.add_symbol('get_search_regex', array_ext.get_search_regex)
ll.add_symbol('compute_node_partition_by_hash', array_ext.
    compute_node_partition_by_hash)
ll.add_symbol('array_info_getitem', array_ext.array_info_getitem)


class ArrayInfoType(types.Type):

    def __init__(self):
        super(ArrayInfoType, self).__init__(name='ArrayInfoType()')


array_info_type = ArrayInfoType()
register_model(ArrayInfoType)(models.OpaqueModel)


class TableTypeCPP(types.Type):

    def __init__(self):
        super(TableTypeCPP, self).__init__(name='TableTypeCPP()')


table_type = TableTypeCPP()
register_model(TableTypeCPP)(models.OpaqueModel)


@intrinsic
def array_to_info(typingctx, arr_type_t=None):
    return array_info_type(arr_type_t), array_to_info_codegen


def array_to_info_codegen(context, builder, sig, args):
    in_arr, = args
    arr_type = sig.args[0]
    if isinstance(arr_type, TupleArrayType):
        tjb__exuvh = context.make_helper(builder, arr_type, in_arr)
        in_arr = tjb__exuvh.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        nrygz__arehk = context.make_helper(builder, arr_type, in_arr)
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='list_string_array_to_info')
        return builder.call(cbem__lxgz, [nrygz__arehk.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                kdogr__dlcn = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for imstc__jkcz in arr_typ.data:
                    kdogr__dlcn += get_types(imstc__jkcz)
                return kdogr__dlcn
            elif isinstance(arr_typ, (types.Array, IntegerArrayType)
                ) or arr_typ == boolean_array:
                return get_types(arr_typ.dtype)
            elif arr_typ == string_array_type:
                return [CTypeEnum.STRING.value]
            elif arr_typ == binary_array_type:
                return [CTypeEnum.BINARY.value]
            elif isinstance(arr_typ, DecimalArrayType):
                return [CTypeEnum.Decimal.value, arr_typ.precision, arr_typ
                    .scale]
            else:
                return [numba_to_c_type(arr_typ)]

        def get_lengths(arr_typ, arr):
            dnvq__tnmls = context.compile_internal(builder, lambda a: len(a
                ), types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                uom__rjiv = context.make_helper(builder, arr_typ, value=arr)
                ubrs__ybggo = get_lengths(_get_map_arr_data_type(arr_typ),
                    uom__rjiv.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                egrg__kiqik = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                ubrs__ybggo = get_lengths(arr_typ.dtype, egrg__kiqik.data)
                ubrs__ybggo = cgutils.pack_array(builder, [egrg__kiqik.
                    n_arrays] + [builder.extract_value(ubrs__ybggo,
                    qqee__ged) for qqee__ged in range(ubrs__ybggo.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                egrg__kiqik = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                ubrs__ybggo = []
                for qqee__ged, imstc__jkcz in enumerate(arr_typ.data):
                    xcrl__xemn = get_lengths(imstc__jkcz, builder.
                        extract_value(egrg__kiqik.data, qqee__ged))
                    ubrs__ybggo += [builder.extract_value(xcrl__xemn,
                        wgryi__mthxc) for wgryi__mthxc in range(xcrl__xemn.
                        type.count)]
                ubrs__ybggo = cgutils.pack_array(builder, [dnvq__tnmls,
                    context.get_constant(types.int64, -1)] + ubrs__ybggo)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                ubrs__ybggo = cgutils.pack_array(builder, [dnvq__tnmls])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray')
            return ubrs__ybggo

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                uom__rjiv = context.make_helper(builder, arr_typ, value=arr)
                aqrwv__dchv = get_buffers(_get_map_arr_data_type(arr_typ),
                    uom__rjiv.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                egrg__kiqik = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                gni__xpgk = get_buffers(arr_typ.dtype, egrg__kiqik.data)
                ulv__rbjc = context.make_array(types.Array(offset_type, 1, 'C')
                    )(context, builder, egrg__kiqik.offsets)
                ecu__mne = builder.bitcast(ulv__rbjc.data, lir.IntType(8).
                    as_pointer())
                zfkxf__ceeyv = context.make_array(types.Array(types.uint8, 
                    1, 'C'))(context, builder, egrg__kiqik.null_bitmap)
                nhqc__dwel = builder.bitcast(zfkxf__ceeyv.data, lir.IntType
                    (8).as_pointer())
                aqrwv__dchv = cgutils.pack_array(builder, [ecu__mne,
                    nhqc__dwel] + [builder.extract_value(gni__xpgk,
                    qqee__ged) for qqee__ged in range(gni__xpgk.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                egrg__kiqik = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                gni__xpgk = []
                for qqee__ged, imstc__jkcz in enumerate(arr_typ.data):
                    davc__brfog = get_buffers(imstc__jkcz, builder.
                        extract_value(egrg__kiqik.data, qqee__ged))
                    gni__xpgk += [builder.extract_value(davc__brfog,
                        wgryi__mthxc) for wgryi__mthxc in range(davc__brfog
                        .type.count)]
                zfkxf__ceeyv = context.make_array(types.Array(types.uint8, 
                    1, 'C'))(context, builder, egrg__kiqik.null_bitmap)
                nhqc__dwel = builder.bitcast(zfkxf__ceeyv.data, lir.IntType
                    (8).as_pointer())
                aqrwv__dchv = cgutils.pack_array(builder, [nhqc__dwel] +
                    gni__xpgk)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                dauu__emgli = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    dauu__emgli = int128_type
                elif arr_typ == datetime_date_array_type:
                    dauu__emgli = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                syhv__qeezd = context.make_array(types.Array(dauu__emgli, 1,
                    'C'))(context, builder, arr.data)
                zfkxf__ceeyv = context.make_array(types.Array(types.uint8, 
                    1, 'C'))(context, builder, arr.null_bitmap)
                isnuf__qit = builder.bitcast(syhv__qeezd.data, lir.IntType(
                    8).as_pointer())
                nhqc__dwel = builder.bitcast(zfkxf__ceeyv.data, lir.IntType
                    (8).as_pointer())
                aqrwv__dchv = cgutils.pack_array(builder, [nhqc__dwel,
                    isnuf__qit])
            elif arr_typ in (string_array_type, binary_array_type):
                egrg__kiqik = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                juhqc__ulm = context.make_helper(builder, offset_arr_type,
                    egrg__kiqik.offsets).data
                xcuzt__wng = context.make_helper(builder, char_arr_type,
                    egrg__kiqik.data).data
                unvno__kvbtx = context.make_helper(builder,
                    null_bitmap_arr_type, egrg__kiqik.null_bitmap).data
                aqrwv__dchv = cgutils.pack_array(builder, [builder.bitcast(
                    juhqc__ulm, lir.IntType(8).as_pointer()), builder.
                    bitcast(unvno__kvbtx, lir.IntType(8).as_pointer()),
                    builder.bitcast(xcuzt__wng, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                isnuf__qit = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                irr__vvz = lir.Constant(lir.IntType(8).as_pointer(), None)
                aqrwv__dchv = cgutils.pack_array(builder, [irr__vvz,
                    isnuf__qit])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return aqrwv__dchv

        def get_field_names(arr_typ):
            ejr__dvwfh = []
            if isinstance(arr_typ, StructArrayType):
                for qjo__xaktp, mxom__xymj in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    ejr__dvwfh.append(qjo__xaktp)
                    ejr__dvwfh += get_field_names(mxom__xymj)
            elif isinstance(arr_typ, ArrayItemArrayType):
                ejr__dvwfh += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                ejr__dvwfh += get_field_names(_get_map_arr_data_type(arr_typ))
            return ejr__dvwfh
        kdogr__dlcn = get_types(arr_type)
        ulm__eoeky = cgutils.pack_array(builder, [context.get_constant(
            types.int32, t) for t in kdogr__dlcn])
        kitfg__sqqx = cgutils.alloca_once_value(builder, ulm__eoeky)
        ubrs__ybggo = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, ubrs__ybggo)
        aqrwv__dchv = get_buffers(arr_type, in_arr)
        nllf__nxx = cgutils.alloca_once_value(builder, aqrwv__dchv)
        ejr__dvwfh = get_field_names(arr_type)
        if len(ejr__dvwfh) == 0:
            ejr__dvwfh = ['irrelevant']
        oanm__cibu = cgutils.pack_array(builder, [context.
            insert_const_string(builder.module, a) for a in ejr__dvwfh])
        xak__zqm = cgutils.alloca_once_value(builder, oanm__cibu)
        if isinstance(arr_type, MapArrayType):
            mbnci__esx = _get_map_arr_data_type(arr_type)
            fbgkn__blu = context.make_helper(builder, arr_type, value=in_arr)
            omlw__fxoh = fbgkn__blu.data
        else:
            mbnci__esx = arr_type
            omlw__fxoh = in_arr
        ijb__mpo = context.make_helper(builder, mbnci__esx, omlw__fxoh)
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='nested_array_to_info')
        jcbj__szff = builder.call(cbem__lxgz, [builder.bitcast(kitfg__sqqx,
            lir.IntType(32).as_pointer()), builder.bitcast(nllf__nxx, lir.
            IntType(8).as_pointer().as_pointer()), builder.bitcast(
            lengths_ptr, lir.IntType(64).as_pointer()), builder.bitcast(
            xak__zqm, lir.IntType(8).as_pointer()), ijb__mpo.meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jcbj__szff
    if arr_type in (string_array_type, binary_array_type):
        abnp__pszas = context.make_helper(builder, arr_type, in_arr)
        sza__pjk = ArrayItemArrayType(char_arr_type)
        nrygz__arehk = context.make_helper(builder, sza__pjk, abnp__pszas.data)
        egrg__kiqik = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        juhqc__ulm = context.make_helper(builder, offset_arr_type,
            egrg__kiqik.offsets).data
        xcuzt__wng = context.make_helper(builder, char_arr_type,
            egrg__kiqik.data).data
        unvno__kvbtx = context.make_helper(builder, null_bitmap_arr_type,
            egrg__kiqik.null_bitmap).data
        syqcg__urwjr = builder.zext(builder.load(builder.gep(juhqc__ulm, [
            egrg__kiqik.n_arrays])), lir.IntType(64))
        zzds__vyxk = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='string_array_to_info')
        return builder.call(cbem__lxgz, [egrg__kiqik.n_arrays, syqcg__urwjr,
            xcuzt__wng, juhqc__ulm, unvno__kvbtx, nrygz__arehk.meminfo,
            zzds__vyxk])
    tmw__kwm = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        lotse__fronw = context.compile_internal(builder, lambda a: len(a.
            dtype.categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        ewe__vgflf = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(ewe__vgflf, 1, 'C')
        tmw__kwm = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        dnvq__tnmls = builder.extract_value(arr.shape, 0)
        iekem__ymyx = arr_type.dtype
        kfv__hcq = numba_to_c_type(iekem__ymyx)
        henh__ddu = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), kfv__hcq))
        if tmw__kwm:
            xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(64), lir.IntType(8).as_pointer()])
            cbem__lxgz = cgutils.get_or_insert_function(builder.module,
                xcgpc__zgtgb, name='categorical_array_to_info')
            return builder.call(cbem__lxgz, [dnvq__tnmls, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                henh__ddu), lotse__fronw, arr.meminfo])
        else:
            xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer()])
            cbem__lxgz = cgutils.get_or_insert_function(builder.module,
                xcgpc__zgtgb, name='numpy_array_to_info')
            return builder.call(cbem__lxgz, [dnvq__tnmls, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                henh__ddu), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        iekem__ymyx = arr_type.dtype
        dauu__emgli = iekem__ymyx
        if isinstance(arr_type, DecimalArrayType):
            dauu__emgli = int128_type
        if arr_type == datetime_date_array_type:
            dauu__emgli = types.int64
        syhv__qeezd = context.make_array(types.Array(dauu__emgli, 1, 'C'))(
            context, builder, arr.data)
        dnvq__tnmls = builder.extract_value(syhv__qeezd.shape, 0)
        edjmr__pedby = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, arr.null_bitmap)
        kfv__hcq = numba_to_c_type(iekem__ymyx)
        henh__ddu = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), kfv__hcq))
        if isinstance(arr_type, DecimalArrayType):
            xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer
                (), lir.IntType(8).as_pointer(), lir.IntType(32), lir.
                IntType(32)])
            cbem__lxgz = cgutils.get_or_insert_function(builder.module,
                xcgpc__zgtgb, name='decimal_array_to_info')
            return builder.call(cbem__lxgz, [dnvq__tnmls, builder.bitcast(
                syhv__qeezd.data, lir.IntType(8).as_pointer()), builder.
                load(henh__ddu), builder.bitcast(edjmr__pedby.data, lir.
                IntType(8).as_pointer()), syhv__qeezd.meminfo, edjmr__pedby
                .meminfo, context.get_constant(types.int32, arr_type.
                precision), context.get_constant(types.int32, arr_type.scale)])
        else:
            xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer
                (), lir.IntType(8).as_pointer()])
            cbem__lxgz = cgutils.get_or_insert_function(builder.module,
                xcgpc__zgtgb, name='nullable_array_to_info')
            return builder.call(cbem__lxgz, [dnvq__tnmls, builder.bitcast(
                syhv__qeezd.data, lir.IntType(8).as_pointer()), builder.
                load(henh__ddu), builder.bitcast(edjmr__pedby.data, lir.
                IntType(8).as_pointer()), syhv__qeezd.meminfo, edjmr__pedby
                .meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        tnqi__eyn = context.make_array(arr_type.arr_type)(context, builder,
            arr.left)
        pno__ztpc = context.make_array(arr_type.arr_type)(context, builder,
            arr.right)
        dnvq__tnmls = builder.extract_value(tnqi__eyn.shape, 0)
        kfv__hcq = numba_to_c_type(arr_type.arr_type.dtype)
        henh__ddu = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), kfv__hcq))
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='interval_array_to_info')
        return builder.call(cbem__lxgz, [dnvq__tnmls, builder.bitcast(
            tnqi__eyn.data, lir.IntType(8).as_pointer()), builder.bitcast(
            pno__ztpc.data, lir.IntType(8).as_pointer()), builder.load(
            henh__ddu), tnqi__eyn.meminfo, pno__ztpc.meminfo])
    raise BodoError(f'array_to_info(): array type {arr_type} is not supported')


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    dtv__sucd = cgutils.alloca_once(builder, lir.IntType(64))
    isnuf__qit = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    wralm__alr = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    xcgpc__zgtgb = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    cbem__lxgz = cgutils.get_or_insert_function(builder.module,
        xcgpc__zgtgb, name='info_to_numpy_array')
    builder.call(cbem__lxgz, [in_info, dtv__sucd, isnuf__qit, wralm__alr])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    scfu__vsv = context.get_value_type(types.intp)
    vnv__vlc = cgutils.pack_array(builder, [builder.load(dtv__sucd)], ty=
        scfu__vsv)
    xwiv__pdtm = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    jpw__ctq = cgutils.pack_array(builder, [xwiv__pdtm], ty=scfu__vsv)
    xcuzt__wng = builder.bitcast(builder.load(isnuf__qit), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=xcuzt__wng, shape=vnv__vlc,
        strides=jpw__ctq, itemsize=xwiv__pdtm, meminfo=builder.load(wralm__alr)
        )
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    zaz__mojnu = context.make_helper(builder, arr_type)
    xcgpc__zgtgb = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    cbem__lxgz = cgutils.get_or_insert_function(builder.module,
        xcgpc__zgtgb, name='info_to_list_string_array')
    builder.call(cbem__lxgz, [in_info, zaz__mojnu._get_ptr_by_name('meminfo')])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return zaz__mojnu._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    jytvd__lupvn = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        wvs__cqpee = lengths_pos
        dafw__guoyp = infos_pos
        yfab__wzzwh, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        oxygt__zqa = ArrayItemArrayPayloadType(arr_typ)
        bcrd__hjc = context.get_data_type(oxygt__zqa)
        htfv__yew = context.get_abi_sizeof(bcrd__hjc)
        oqpvo__qjfg = define_array_item_dtor(context, builder, arr_typ,
            oxygt__zqa)
        mgqq__owzku = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, htfv__yew), oqpvo__qjfg)
        qxtjk__vdf = context.nrt.meminfo_data(builder, mgqq__owzku)
        hrcww__ovzyc = builder.bitcast(qxtjk__vdf, bcrd__hjc.as_pointer())
        egrg__kiqik = cgutils.create_struct_proxy(oxygt__zqa)(context, builder)
        egrg__kiqik.n_arrays = builder.extract_value(builder.load(
            lengths_ptr), wvs__cqpee)
        egrg__kiqik.data = yfab__wzzwh
        cmza__harom = builder.load(array_infos_ptr)
        oiz__psq = builder.bitcast(builder.extract_value(cmza__harom,
            dafw__guoyp), jytvd__lupvn)
        egrg__kiqik.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, oiz__psq)
        vfy__dkd = builder.bitcast(builder.extract_value(cmza__harom, 
            dafw__guoyp + 1), jytvd__lupvn)
        egrg__kiqik.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, vfy__dkd)
        builder.store(egrg__kiqik._getvalue(), hrcww__ovzyc)
        nrygz__arehk = context.make_helper(builder, arr_typ)
        nrygz__arehk.meminfo = mgqq__owzku
        return nrygz__arehk._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        eqmv__ahw = []
        dafw__guoyp = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for kdtf__nzcxs in arr_typ.data:
            yfab__wzzwh, lengths_pos, infos_pos = nested_to_array(context,
                builder, kdtf__nzcxs, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            eqmv__ahw.append(yfab__wzzwh)
        oxygt__zqa = StructArrayPayloadType(arr_typ.data)
        bcrd__hjc = context.get_value_type(oxygt__zqa)
        htfv__yew = context.get_abi_sizeof(bcrd__hjc)
        oqpvo__qjfg = define_struct_arr_dtor(context, builder, arr_typ,
            oxygt__zqa)
        mgqq__owzku = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, htfv__yew), oqpvo__qjfg)
        qxtjk__vdf = context.nrt.meminfo_data(builder, mgqq__owzku)
        hrcww__ovzyc = builder.bitcast(qxtjk__vdf, bcrd__hjc.as_pointer())
        egrg__kiqik = cgutils.create_struct_proxy(oxygt__zqa)(context, builder)
        egrg__kiqik.data = cgutils.pack_array(builder, eqmv__ahw
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, eqmv__ahw)
        cmza__harom = builder.load(array_infos_ptr)
        vfy__dkd = builder.bitcast(builder.extract_value(cmza__harom,
            dafw__guoyp), jytvd__lupvn)
        egrg__kiqik.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, vfy__dkd)
        builder.store(egrg__kiqik._getvalue(), hrcww__ovzyc)
        rjdxr__adf = context.make_helper(builder, arr_typ)
        rjdxr__adf.meminfo = mgqq__owzku
        return rjdxr__adf._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        cmza__harom = builder.load(array_infos_ptr)
        gbed__xmwqe = builder.bitcast(builder.extract_value(cmza__harom,
            infos_pos), jytvd__lupvn)
        abnp__pszas = context.make_helper(builder, arr_typ)
        sza__pjk = ArrayItemArrayType(char_arr_type)
        nrygz__arehk = context.make_helper(builder, sza__pjk)
        xcgpc__zgtgb = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='info_to_string_array')
        builder.call(cbem__lxgz, [gbed__xmwqe, nrygz__arehk.
            _get_ptr_by_name('meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        abnp__pszas.data = nrygz__arehk._getvalue()
        return abnp__pszas._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        cmza__harom = builder.load(array_infos_ptr)
        jvaob__lawhd = builder.bitcast(builder.extract_value(cmza__harom, 
            infos_pos + 1), jytvd__lupvn)
        return _lower_info_to_array_numpy(arr_typ, context, builder,
            jvaob__lawhd), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        dauu__emgli = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            dauu__emgli = int128_type
        elif arr_typ == datetime_date_array_type:
            dauu__emgli = types.int64
        cmza__harom = builder.load(array_infos_ptr)
        vfy__dkd = builder.bitcast(builder.extract_value(cmza__harom,
            infos_pos), jytvd__lupvn)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, vfy__dkd)
        jvaob__lawhd = builder.bitcast(builder.extract_value(cmza__harom, 
            infos_pos + 1), jytvd__lupvn)
        arr.data = _lower_info_to_array_numpy(types.Array(dauu__emgli, 1,
            'C'), context, builder, jvaob__lawhd)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


@intrinsic
def info_to_array(typingctx, info_type, array_type):
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    assert info_type == array_info_type

    def codegen(context, builder, sig, args):
        in_info, lfd__hrub = args
        if isinstance(arr_type, ArrayItemArrayType
            ) and arr_type.dtype == string_array_type:
            return _lower_info_to_array_list_string_array(arr_type, context,
                builder, in_info)
        if isinstance(arr_type, (MapArrayType, ArrayItemArrayType,
            StructArrayType, TupleArrayType)):

            def get_num_arrays(arr_typ):
                if isinstance(arr_typ, ArrayItemArrayType):
                    return 1 + get_num_arrays(arr_typ.dtype)
                elif isinstance(arr_typ, StructArrayType):
                    return 1 + sum([get_num_arrays(kdtf__nzcxs) for
                        kdtf__nzcxs in arr_typ.data])
                else:
                    return 1

            def get_num_infos(arr_typ):
                if isinstance(arr_typ, ArrayItemArrayType):
                    return 2 + get_num_infos(arr_typ.dtype)
                elif isinstance(arr_typ, StructArrayType):
                    return 1 + sum([get_num_infos(kdtf__nzcxs) for
                        kdtf__nzcxs in arr_typ.data])
                elif arr_typ in (string_array_type, binary_array_type):
                    return 1
                else:
                    return 2
            if isinstance(arr_type, TupleArrayType):
                pro__fvy = StructArrayType(arr_type.data, ('dummy',) * len(
                    arr_type.data))
            elif isinstance(arr_type, MapArrayType):
                pro__fvy = _get_map_arr_data_type(arr_type)
            else:
                pro__fvy = arr_type
            huu__lnsh = get_num_arrays(pro__fvy)
            ubrs__ybggo = cgutils.pack_array(builder, [lir.Constant(lir.
                IntType(64), 0) for lfd__hrub in range(huu__lnsh)])
            lengths_ptr = cgutils.alloca_once_value(builder, ubrs__ybggo)
            irr__vvz = lir.Constant(lir.IntType(8).as_pointer(), None)
            jlvqu__byrhx = cgutils.pack_array(builder, [irr__vvz for
                lfd__hrub in range(get_num_infos(pro__fvy))])
            array_infos_ptr = cgutils.alloca_once_value(builder, jlvqu__byrhx)
            xcgpc__zgtgb = lir.FunctionType(lir.VoidType(), [lir.IntType(8)
                .as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8)
                .as_pointer().as_pointer()])
            cbem__lxgz = cgutils.get_or_insert_function(builder.module,
                xcgpc__zgtgb, name='info_to_nested_array')
            builder.call(cbem__lxgz, [in_info, builder.bitcast(lengths_ptr,
                lir.IntType(64).as_pointer()), builder.bitcast(
                array_infos_ptr, lir.IntType(8).as_pointer().as_pointer())])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            arr, lfd__hrub, lfd__hrub = nested_to_array(context, builder,
                pro__fvy, lengths_ptr, array_infos_ptr, 0, 0)
            if isinstance(arr_type, TupleArrayType):
                tjb__exuvh = context.make_helper(builder, arr_type)
                tjb__exuvh.data = arr
                context.nrt.incref(builder, pro__fvy, arr)
                arr = tjb__exuvh._getvalue()
            elif isinstance(arr_type, MapArrayType):
                sig = signature(arr_type, pro__fvy)
                arr = init_map_arr_codegen(context, builder, sig, (arr,))
            return arr
        if arr_type in (string_array_type, binary_array_type):
            abnp__pszas = context.make_helper(builder, arr_type)
            sza__pjk = ArrayItemArrayType(char_arr_type)
            nrygz__arehk = context.make_helper(builder, sza__pjk)
            xcgpc__zgtgb = lir.FunctionType(lir.VoidType(), [lir.IntType(8)
                .as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
            cbem__lxgz = cgutils.get_or_insert_function(builder.module,
                xcgpc__zgtgb, name='info_to_string_array')
            builder.call(cbem__lxgz, [in_info, nrygz__arehk.
                _get_ptr_by_name('meminfo')])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            abnp__pszas.data = nrygz__arehk._getvalue()
            return abnp__pszas._getvalue()
        if isinstance(arr_type, CategoricalArrayType):
            out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
            ewe__vgflf = get_categories_int_type(arr_type.dtype)
            fve__guid = types.Array(ewe__vgflf, 1, 'C')
            out_arr.codes = _lower_info_to_array_numpy(fve__guid, context,
                builder, in_info)
            if isinstance(array_type, types.TypeRef):
                assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
                is_ordered = arr_type.dtype.ordered
                exuys__pqvvf = pd.CategoricalDtype(arr_type.dtype.
                    categories, is_ordered).categories.values
                new_cats_tup = MetaType(tuple(exuys__pqvvf))
                int_type = arr_type.dtype.int_type
                dlznn__vgnd = bodo.typeof(exuys__pqvvf)
                dpa__iwza = context.get_constant_generic(builder,
                    dlznn__vgnd, exuys__pqvvf)
                iekem__ymyx = context.compile_internal(builder, lambda
                    c_arr: bodo.hiframes.pd_categorical_ext.init_cat_dtype(
                    bodo.utils.conversion.index_from_array(c_arr),
                    is_ordered, int_type, new_cats_tup), arr_type.dtype(
                    dlznn__vgnd), [dpa__iwza])
            else:
                iekem__ymyx = cgutils.create_struct_proxy(arr_type)(context,
                    builder, args[1]).dtype
                context.nrt.incref(builder, arr_type.dtype, iekem__ymyx)
            out_arr.dtype = iekem__ymyx
            return out_arr._getvalue()
        if isinstance(arr_type, types.Array):
            return _lower_info_to_array_numpy(arr_type, context, builder,
                in_info)
        if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
            ) or arr_type in (boolean_array, datetime_date_array_type):
            arr = cgutils.create_struct_proxy(arr_type)(context, builder)
            dauu__emgli = arr_type.dtype
            if isinstance(arr_type, DecimalArrayType):
                dauu__emgli = int128_type
            elif arr_type == datetime_date_array_type:
                dauu__emgli = types.int64
            exm__ndldu = types.Array(dauu__emgli, 1, 'C')
            syhv__qeezd = context.make_array(exm__ndldu)(context, builder)
            rxz__fyvf = types.Array(types.uint8, 1, 'C')
            fwizg__arpff = context.make_array(rxz__fyvf)(context, builder)
            dtv__sucd = cgutils.alloca_once(builder, lir.IntType(64))
            lax__pbmis = cgutils.alloca_once(builder, lir.IntType(64))
            isnuf__qit = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            zam__ybo = cgutils.alloca_once(builder, lir.IntType(8).as_pointer()
                )
            wralm__alr = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            mzg__xlea = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            xcgpc__zgtgb = lir.FunctionType(lir.VoidType(), [lir.IntType(8)
                .as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64
                ).as_pointer(), lir.IntType(8).as_pointer().as_pointer(),
                lir.IntType(8).as_pointer().as_pointer(), lir.IntType(8).
                as_pointer().as_pointer(), lir.IntType(8).as_pointer().
                as_pointer()])
            cbem__lxgz = cgutils.get_or_insert_function(builder.module,
                xcgpc__zgtgb, name='info_to_nullable_array')
            builder.call(cbem__lxgz, [in_info, dtv__sucd, lax__pbmis,
                isnuf__qit, zam__ybo, wralm__alr, mzg__xlea])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            scfu__vsv = context.get_value_type(types.intp)
            vnv__vlc = cgutils.pack_array(builder, [builder.load(dtv__sucd)
                ], ty=scfu__vsv)
            xwiv__pdtm = context.get_constant(types.intp, context.
                get_abi_sizeof(context.get_data_type(dauu__emgli)))
            jpw__ctq = cgutils.pack_array(builder, [xwiv__pdtm], ty=scfu__vsv)
            xcuzt__wng = builder.bitcast(builder.load(isnuf__qit), context.
                get_data_type(dauu__emgli).as_pointer())
            numba.np.arrayobj.populate_array(syhv__qeezd, data=xcuzt__wng,
                shape=vnv__vlc, strides=jpw__ctq, itemsize=xwiv__pdtm,
                meminfo=builder.load(wralm__alr))
            arr.data = syhv__qeezd._getvalue()
            vnv__vlc = cgutils.pack_array(builder, [builder.load(lax__pbmis
                )], ty=scfu__vsv)
            xwiv__pdtm = context.get_constant(types.intp, context.
                get_abi_sizeof(context.get_data_type(types.uint8)))
            jpw__ctq = cgutils.pack_array(builder, [xwiv__pdtm], ty=scfu__vsv)
            xcuzt__wng = builder.bitcast(builder.load(zam__ybo), context.
                get_data_type(types.uint8).as_pointer())
            numba.np.arrayobj.populate_array(fwizg__arpff, data=xcuzt__wng,
                shape=vnv__vlc, strides=jpw__ctq, itemsize=xwiv__pdtm,
                meminfo=builder.load(mzg__xlea))
            arr.null_bitmap = fwizg__arpff._getvalue()
            return arr._getvalue()
        if isinstance(arr_type, IntervalArrayType):
            arr = cgutils.create_struct_proxy(arr_type)(context, builder)
            tnqi__eyn = context.make_array(arr_type.arr_type)(context, builder)
            pno__ztpc = context.make_array(arr_type.arr_type)(context, builder)
            dtv__sucd = cgutils.alloca_once(builder, lir.IntType(64))
            hbuv__jupy = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            gnc__axcoo = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            sltf__yrcc = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            ocss__rvw = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            xcgpc__zgtgb = lir.FunctionType(lir.VoidType(), [lir.IntType(8)
                .as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8)
                .as_pointer().as_pointer(), lir.IntType(8).as_pointer().
                as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir
                .IntType(8).as_pointer().as_pointer()])
            cbem__lxgz = cgutils.get_or_insert_function(builder.module,
                xcgpc__zgtgb, name='info_to_interval_array')
            builder.call(cbem__lxgz, [in_info, dtv__sucd, hbuv__jupy,
                gnc__axcoo, sltf__yrcc, ocss__rvw])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            scfu__vsv = context.get_value_type(types.intp)
            vnv__vlc = cgutils.pack_array(builder, [builder.load(dtv__sucd)
                ], ty=scfu__vsv)
            xwiv__pdtm = context.get_constant(types.intp, context.
                get_abi_sizeof(context.get_data_type(arr_type.arr_type.dtype)))
            jpw__ctq = cgutils.pack_array(builder, [xwiv__pdtm], ty=scfu__vsv)
            qhbu__ngi = builder.bitcast(builder.load(hbuv__jupy), context.
                get_data_type(arr_type.arr_type.dtype).as_pointer())
            numba.np.arrayobj.populate_array(tnqi__eyn, data=qhbu__ngi,
                shape=vnv__vlc, strides=jpw__ctq, itemsize=xwiv__pdtm,
                meminfo=builder.load(sltf__yrcc))
            arr.left = tnqi__eyn._getvalue()
            judhd__ttbow = builder.bitcast(builder.load(gnc__axcoo),
                context.get_data_type(arr_type.arr_type.dtype).as_pointer())
            numba.np.arrayobj.populate_array(pno__ztpc, data=judhd__ttbow,
                shape=vnv__vlc, strides=jpw__ctq, itemsize=xwiv__pdtm,
                meminfo=builder.load(ocss__rvw))
            arr.right = pno__ztpc._getvalue()
            return arr._getvalue()
        raise BodoError(
            f'info_to_array(): array type {arr_type} is not supported')
    return arr_type(info_type, array_type), codegen


@intrinsic
def test_alloc_np(typingctx, len_typ, arr_type):
    array_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type

    def codegen(context, builder, sig, args):
        dnvq__tnmls, lfd__hrub = args
        kfv__hcq = numba_to_c_type(array_type.dtype)
        henh__ddu = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), kfv__hcq))
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='alloc_numpy')
        return builder.call(cbem__lxgz, [dnvq__tnmls, builder.load(henh__ddu)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        dnvq__tnmls, qxco__lgsze = args
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='alloc_string_array')
        return builder.call(cbem__lxgz, [dnvq__tnmls, qxco__lgsze])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    tsniu__znv, = args
    jag__fck = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], tsniu__znv)
    xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer().as_pointer(), lir.IntType(64)])
    cbem__lxgz = cgutils.get_or_insert_function(builder.module,
        xcgpc__zgtgb, name='arr_info_list_to_table')
    return builder.call(cbem__lxgz, [jag__fck.data, jag__fck.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='info_from_table')
        return builder.call(cbem__lxgz, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    vlgw__ykg = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        mgbcm__taxei, mxy__yff, lfd__hrub = args
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='info_from_table')
        mcua__xmlzk = cgutils.create_struct_proxy(vlgw__ykg)(context, builder)
        mcua__xmlzk.parent = cgutils.get_null_value(mcua__xmlzk.parent.type)
        gpw__oub = context.make_array(table_idx_arr_t)(context, builder,
            mxy__yff)
        ppoy__kjp = context.get_constant(types.int64, -1)
        alcwt__pylhv = context.get_constant(types.int64, 0)
        uto__inyn = cgutils.alloca_once_value(builder, alcwt__pylhv)
        for t, hoh__fvj in vlgw__ykg.type_to_blk.items():
            mgvx__atmoa = context.get_constant(types.int64, len(vlgw__ykg.
                block_to_arr_ind[hoh__fvj]))
            lfd__hrub, omd__pez = ListInstance.allocate_ex(context, builder,
                types.List(t), mgvx__atmoa)
            omd__pez.size = mgvx__atmoa
            tyo__zhd = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(vlgw__ykg.block_to_arr_ind[
                hoh__fvj], dtype=np.int64))
            pyf__bts = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, tyo__zhd)
            with cgutils.for_range(builder, mgvx__atmoa) as loop:
                qqee__ged = loop.index
                zpgtn__uqvwv = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'), pyf__bts,
                    qqee__ged)
                txflp__wvasd = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, gpw__oub, zpgtn__uqvwv)
                gdzii__vqw = builder.icmp_unsigned('!=', txflp__wvasd,
                    ppoy__kjp)
                with builder.if_else(gdzii__vqw) as (then, orelse):
                    with then:
                        bqv__fnn = builder.call(cbem__lxgz, [mgbcm__taxei,
                            txflp__wvasd])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            bqv__fnn])
                        omd__pez.inititem(qqee__ged, arr, incref=False)
                        dnvq__tnmls = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(dnvq__tnmls, uto__inyn)
                    with orelse:
                        xspfu__qztw = context.get_constant_null(t)
                        omd__pez.inititem(qqee__ged, xspfu__qztw, incref=False)
            setattr(mcua__xmlzk, f'block_{hoh__fvj}', omd__pez.value)
        mcua__xmlzk.len = builder.load(uto__inyn)
        return mcua__xmlzk._getvalue()
    return vlgw__ykg(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    vlgw__ykg = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        ihgt__uerq, lfd__hrub = args
        eislg__xsgbd = lir.Constant(lir.IntType(64), len(vlgw__ykg.arr_types))
        lfd__hrub, sio__pgpoe = ListInstance.allocate_ex(context, builder,
            types.List(array_info_type), eislg__xsgbd)
        sio__pgpoe.size = eislg__xsgbd
        swdda__lhcc = cgutils.create_struct_proxy(vlgw__ykg)(context,
            builder, ihgt__uerq)
        for t, hoh__fvj in vlgw__ykg.type_to_blk.items():
            mgvx__atmoa = context.get_constant(types.int64, len(vlgw__ykg.
                block_to_arr_ind[hoh__fvj]))
            fni__trngp = getattr(swdda__lhcc, f'block_{hoh__fvj}')
            eaz__zpa = ListInstance(context, builder, types.List(t), fni__trngp
                )
            tyo__zhd = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(vlgw__ykg.block_to_arr_ind[
                hoh__fvj], dtype=np.int64))
            pyf__bts = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, tyo__zhd)
            with cgutils.for_range(builder, mgvx__atmoa) as loop:
                qqee__ged = loop.index
                zpgtn__uqvwv = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'), pyf__bts,
                    qqee__ged)
                afdmp__kwt = signature(types.none, vlgw__ykg, types.List(t),
                    types.int64, types.int64)
                zwqnt__zhpnq = ihgt__uerq, fni__trngp, qqee__ged, zpgtn__uqvwv
                bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                    builder, afdmp__kwt, zwqnt__zhpnq)
                arr = eaz__zpa.getitem(qqee__ged)
                xmzg__fzvmi = signature(array_info_type, t)
                yyk__mrv = arr,
                ves__rmuel = array_to_info_codegen(context, builder,
                    xmzg__fzvmi, yyk__mrv)
                sio__pgpoe.inititem(zpgtn__uqvwv, ves__rmuel, incref=False)
        wfez__mtk = sio__pgpoe.value
        hdtj__yurac = signature(table_type, types.List(array_info_type))
        mic__dcrz = wfez__mtk,
        mgbcm__taxei = arr_info_list_to_table_codegen(context, builder,
            hdtj__yurac, mic__dcrz)
        context.nrt.decref(builder, types.List(array_info_type), wfez__mtk)
        return mgbcm__taxei
    return table_type(vlgw__ykg, py_table_type_t), codegen


delete_info_decref_array = types.ExternalFunction('delete_info_decref_array',
    types.void(array_info_type))
delete_table_decref_arrays = types.ExternalFunction(
    'delete_table_decref_arrays', types.void(table_type))


@intrinsic
def delete_table(typingctx, table_t=None):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        xcgpc__zgtgb = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='delete_table')
        builder.call(cbem__lxgz, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='shuffle_table')
        jcbj__szff = builder.call(cbem__lxgz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jcbj__szff
    return table_type(table_t, types.int64, types.boolean, types.int32
        ), codegen


class ShuffleInfoType(types.Type):

    def __init__(self):
        super(ShuffleInfoType, self).__init__(name='ShuffleInfoType()')


shuffle_info_type = ShuffleInfoType()
register_model(ShuffleInfoType)(models.OpaqueModel)
get_shuffle_info = types.ExternalFunction('get_shuffle_info',
    shuffle_info_type(table_type))


@intrinsic
def delete_shuffle_info(typingctx, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[0] == types.none:
            return
        xcgpc__zgtgb = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='delete_shuffle_info')
        return builder.call(cbem__lxgz, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='reverse_shuffle_table')
        return builder.call(cbem__lxgz, args)
    return table_type(table_type, shuffle_info_t), codegen


@intrinsic
def get_null_shuffle_info(typingctx):

    def codegen(context, builder, sig, args):
        return context.get_constant_null(sig.return_type)
    return shuffle_info_type(), codegen


@intrinsic
def hash_join_table(typingctx, left_table_t, right_table_t, left_parallel_t,
    right_parallel_t, n_keys_t, n_data_left_t, n_data_right_t, same_vect_t,
    same_need_typechange_t, is_left_t, is_right_t, is_join_t,
    optional_col_t, indicator, _bodo_na_equal, cond_func, left_col_nums,
    left_col_nums_len, right_col_nums, right_col_nums_len):
    assert left_table_t == table_type
    assert right_table_t == table_type

    def codegen(context, builder, sig, args):
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1), lir.IntType(1), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(8).as_pointer(), lir.IntType(64)])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='hash_join_table')
        jcbj__szff = builder.call(cbem__lxgz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jcbj__szff
    return table_type(left_table_t, right_table_t, types.boolean, types.
        boolean, types.int64, types.int64, types.int64, types.voidptr,
        types.voidptr, types.boolean, types.boolean, types.boolean, types.
        boolean, types.boolean, types.boolean, types.voidptr, types.voidptr,
        types.int64, types.voidptr, types.int64), codegen


@intrinsic
def compute_node_partition_by_hash(typingctx, table_t, n_keys_t, n_pes_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='compute_node_partition_by_hash')
        jcbj__szff = builder.call(cbem__lxgz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jcbj__szff
    return table_type(table_t, types.int64, types.int64), codegen


@intrinsic
def sort_values_table(typingctx, table_t, n_keys_t, vect_ascending_t,
    na_position_b_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='sort_values_table')
        jcbj__szff = builder.call(cbem__lxgz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jcbj__szff
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='sample_table')
        jcbj__szff = builder.call(cbem__lxgz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jcbj__szff
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='shuffle_renormalization')
        jcbj__szff = builder.call(cbem__lxgz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jcbj__szff
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='shuffle_renormalization_group')
        jcbj__szff = builder.call(cbem__lxgz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jcbj__szff
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1)])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='drop_duplicates_table')
        jcbj__szff = builder.call(cbem__lxgz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jcbj__szff
    return table_type(table_t, types.boolean, types.int64, types.int64,
        types.boolean), codegen


@intrinsic
def pivot_groupby_and_aggregate(typingctx, table_t, n_keys_t,
    dispatch_table_t, dispatch_info_t, input_has_index, ftypes,
    func_offsets, udf_n_redvars, is_parallel, is_crosstab, skipdropna_t,
    return_keys, return_index, update_cb, combine_cb, eval_cb,
    udf_table_dummy_t):
    assert table_t == table_type
    assert dispatch_table_t == table_type
    assert dispatch_info_t == table_type
    assert udf_table_dummy_t == table_type

    def codegen(context, builder, sig, args):
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='pivot_groupby_and_aggregate')
        jcbj__szff = builder.call(cbem__lxgz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jcbj__szff
    return table_type(table_t, types.int64, table_t, table_t, types.boolean,
        types.voidptr, types.voidptr, types.voidptr, types.boolean, types.
        boolean, types.boolean, types.boolean, types.boolean, types.voidptr,
        types.voidptr, types.voidptr, table_t), codegen


@intrinsic
def groupby_and_aggregate(typingctx, table_t, n_keys_t, input_has_index,
    ftypes, func_offsets, udf_n_redvars, is_parallel, skipdropna_t,
    shift_periods_t, transform_func, head_n, return_keys, return_index,
    dropna, update_cb, combine_cb, eval_cb, general_udfs_cb, udf_table_dummy_t
    ):
    assert table_t == table_type
    assert udf_table_dummy_t == table_type

    def codegen(context, builder, sig, args):
        xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        cbem__lxgz = cgutils.get_or_insert_function(builder.module,
            xcgpc__zgtgb, name='groupby_and_aggregate')
        jcbj__szff = builder.call(cbem__lxgz, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return jcbj__szff
    return table_type(table_t, types.int64, types.boolean, types.voidptr,
        types.voidptr, types.voidptr, types.boolean, types.boolean, types.
        int64, types.int64, types.int64, types.boolean, types.boolean,
        types.boolean, types.voidptr, types.voidptr, types.voidptr, types.
        voidptr, table_t), codegen


get_groupby_labels = types.ExternalFunction('get_groupby_labels', types.
    int64(table_type, types.voidptr, types.voidptr, types.boolean, types.bool_)
    )
_array_isin = types.ExternalFunction('array_isin', types.void(
    array_info_type, array_info_type, array_info_type, types.bool_))


@numba.njit
def array_isin(out_arr, in_arr, in_values, is_parallel):
    mcd__lyf = array_to_info(in_arr)
    unad__vmyo = array_to_info(in_values)
    xwey__yfq = array_to_info(out_arr)
    jqt__spa = arr_info_list_to_table([mcd__lyf, unad__vmyo, xwey__yfq])
    _array_isin(xwey__yfq, mcd__lyf, unad__vmyo, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(jqt__spa)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.voidptr, array_info_type))


@numba.njit
def get_search_regex(in_arr, case, pat, out_arr):
    mcd__lyf = array_to_info(in_arr)
    xwey__yfq = array_to_info(out_arr)
    _get_search_regex(mcd__lyf, case, pat, xwey__yfq)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_dtype, c_ind):
    from llvmlite import ir as lir
    if isinstance(col_dtype, types.Number) or col_dtype in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                mcua__xmlzk, crqlj__uxkn = args
                mcua__xmlzk = builder.bitcast(mcua__xmlzk, lir.IntType(8).
                    as_pointer().as_pointer())
                konxv__ncuou = lir.Constant(lir.IntType(64), c_ind)
                byeql__mwd = builder.load(builder.gep(mcua__xmlzk, [
                    konxv__ncuou]))
                byeql__mwd = builder.bitcast(byeql__mwd, context.
                    get_data_type(col_dtype).as_pointer())
                return builder.load(builder.gep(byeql__mwd, [crqlj__uxkn]))
            return col_dtype(types.voidptr, types.int64), codegen
        return getitem_func
    if col_dtype == types.unicode_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                mcua__xmlzk, crqlj__uxkn = args
                xcgpc__zgtgb = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64), lir.IntType(64).as_pointer()])
                ywfzl__guqis = cgutils.get_or_insert_function(builder.
                    module, xcgpc__zgtgb, name='array_info_getitem')
                konxv__ncuou = lir.Constant(lir.IntType(64), c_ind)
                cfbil__etn = cgutils.alloca_once(builder, lir.IntType(64))
                args = mcua__xmlzk, konxv__ncuou, crqlj__uxkn, cfbil__etn
                isnuf__qit = builder.call(ywfzl__guqis, args)
                return context.make_tuple(builder, sig.return_type, [
                    isnuf__qit, builder.load(cfbil__etn)])
            return types.Tuple([types.voidptr, types.int64])(types.voidptr,
                types.int64), codegen
        return getitem_func
    raise BodoError(
        f"General Join Conditions with '{col_dtype}' column data type not supported"
        )


def _gen_row_na_check_intrinsic(col_array_dtype, c_ind):
    if isinstance(col_array_dtype, bodo.libs.int_arr_ext.IntegerArrayType
        ) or col_array_dtype in [bodo.libs.bool_arr_ext.boolean_array, bodo
        .libs.str_arr_ext.string_array_type] or isinstance(col_array_dtype,
        types.Array) and col_array_dtype.dtype == bodo.datetime_date_type:

        @intrinsic
        def checkna_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                hyy__gnb, crqlj__uxkn = args
                hyy__gnb = builder.bitcast(hyy__gnb, lir.IntType(8).
                    as_pointer().as_pointer())
                konxv__ncuou = lir.Constant(lir.IntType(64), c_ind)
                byeql__mwd = builder.load(builder.gep(hyy__gnb, [konxv__ncuou])
                    )
                unvno__kvbtx = builder.bitcast(byeql__mwd, context.
                    get_data_type(types.bool_).as_pointer())
                kswm__dgf = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    unvno__kvbtx, crqlj__uxkn)
                nmk__xfam = builder.icmp_unsigned('!=', kswm__dgf, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(nmk__xfam, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        col_dtype = col_array_dtype.dtype
        if col_dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    mcua__xmlzk, crqlj__uxkn = args
                    mcua__xmlzk = builder.bitcast(mcua__xmlzk, lir.IntType(
                        8).as_pointer().as_pointer())
                    konxv__ncuou = lir.Constant(lir.IntType(64), c_ind)
                    byeql__mwd = builder.load(builder.gep(mcua__xmlzk, [
                        konxv__ncuou]))
                    byeql__mwd = builder.bitcast(byeql__mwd, context.
                        get_data_type(col_dtype).as_pointer())
                    kjq__qnxqa = builder.load(builder.gep(byeql__mwd, [
                        crqlj__uxkn]))
                    nmk__xfam = builder.icmp_unsigned('!=', kjq__qnxqa, lir
                        .Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(nmk__xfam, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(col_dtype, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    mcua__xmlzk, crqlj__uxkn = args
                    mcua__xmlzk = builder.bitcast(mcua__xmlzk, lir.IntType(
                        8).as_pointer().as_pointer())
                    konxv__ncuou = lir.Constant(lir.IntType(64), c_ind)
                    byeql__mwd = builder.load(builder.gep(mcua__xmlzk, [
                        konxv__ncuou]))
                    byeql__mwd = builder.bitcast(byeql__mwd, context.
                        get_data_type(col_dtype).as_pointer())
                    kjq__qnxqa = builder.load(builder.gep(byeql__mwd, [
                        crqlj__uxkn]))
                    nkh__pccfm = signature(types.bool_, col_dtype)
                    kswm__dgf = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, nkh__pccfm, (kjq__qnxqa,))
                    return builder.not_(builder.sext(kswm__dgf, lir.IntType(8))
                        )
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
