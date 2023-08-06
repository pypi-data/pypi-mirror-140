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
        drig__xbh = context.make_helper(builder, arr_type, in_arr)
        in_arr = drig__xbh.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        qoe__prz = context.make_helper(builder, arr_type, in_arr)
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='list_string_array_to_info')
        return builder.call(ycoq__numu, [qoe__prz.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                djdns__eyj = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for zdtv__lmpkx in arr_typ.data:
                    djdns__eyj += get_types(zdtv__lmpkx)
                return djdns__eyj
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
            ntxns__isc = context.compile_internal(builder, lambda a: len(a),
                types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                vof__lvis = context.make_helper(builder, arr_typ, value=arr)
                tme__dftj = get_lengths(_get_map_arr_data_type(arr_typ),
                    vof__lvis.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                keun__ovjp = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                tme__dftj = get_lengths(arr_typ.dtype, keun__ovjp.data)
                tme__dftj = cgutils.pack_array(builder, [keun__ovjp.
                    n_arrays] + [builder.extract_value(tme__dftj,
                    tnfov__racgi) for tnfov__racgi in range(tme__dftj.type.
                    count)])
            elif isinstance(arr_typ, StructArrayType):
                keun__ovjp = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                tme__dftj = []
                for tnfov__racgi, zdtv__lmpkx in enumerate(arr_typ.data):
                    hqtgx__bswzn = get_lengths(zdtv__lmpkx, builder.
                        extract_value(keun__ovjp.data, tnfov__racgi))
                    tme__dftj += [builder.extract_value(hqtgx__bswzn,
                        zmr__jvjh) for zmr__jvjh in range(hqtgx__bswzn.type
                        .count)]
                tme__dftj = cgutils.pack_array(builder, [ntxns__isc,
                    context.get_constant(types.int64, -1)] + tme__dftj)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                tme__dftj = cgutils.pack_array(builder, [ntxns__isc])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray')
            return tme__dftj

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                vof__lvis = context.make_helper(builder, arr_typ, value=arr)
                oma__jnwe = get_buffers(_get_map_arr_data_type(arr_typ),
                    vof__lvis.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                keun__ovjp = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                vnjz__syda = get_buffers(arr_typ.dtype, keun__ovjp.data)
                ffy__qieoh = context.make_array(types.Array(offset_type, 1,
                    'C'))(context, builder, keun__ovjp.offsets)
                xzgi__hnlsa = builder.bitcast(ffy__qieoh.data, lir.IntType(
                    8).as_pointer())
                vytb__ywnx = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, keun__ovjp.null_bitmap)
                vryi__nka = builder.bitcast(vytb__ywnx.data, lir.IntType(8)
                    .as_pointer())
                oma__jnwe = cgutils.pack_array(builder, [xzgi__hnlsa,
                    vryi__nka] + [builder.extract_value(vnjz__syda,
                    tnfov__racgi) for tnfov__racgi in range(vnjz__syda.type
                    .count)])
            elif isinstance(arr_typ, StructArrayType):
                keun__ovjp = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                vnjz__syda = []
                for tnfov__racgi, zdtv__lmpkx in enumerate(arr_typ.data):
                    tfhad__xrgp = get_buffers(zdtv__lmpkx, builder.
                        extract_value(keun__ovjp.data, tnfov__racgi))
                    vnjz__syda += [builder.extract_value(tfhad__xrgp,
                        zmr__jvjh) for zmr__jvjh in range(tfhad__xrgp.type.
                        count)]
                vytb__ywnx = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, keun__ovjp.null_bitmap)
                vryi__nka = builder.bitcast(vytb__ywnx.data, lir.IntType(8)
                    .as_pointer())
                oma__jnwe = cgutils.pack_array(builder, [vryi__nka] +
                    vnjz__syda)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                bdrte__oipaj = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    bdrte__oipaj = int128_type
                elif arr_typ == datetime_date_array_type:
                    bdrte__oipaj = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                mnah__mqd = context.make_array(types.Array(bdrte__oipaj, 1,
                    'C'))(context, builder, arr.data)
                vytb__ywnx = context.make_array(types.Array(types.uint8, 1,
                    'C'))(context, builder, arr.null_bitmap)
                ibw__yrn = builder.bitcast(mnah__mqd.data, lir.IntType(8).
                    as_pointer())
                vryi__nka = builder.bitcast(vytb__ywnx.data, lir.IntType(8)
                    .as_pointer())
                oma__jnwe = cgutils.pack_array(builder, [vryi__nka, ibw__yrn])
            elif arr_typ in (string_array_type, binary_array_type):
                keun__ovjp = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                kju__bpkzg = context.make_helper(builder, offset_arr_type,
                    keun__ovjp.offsets).data
                xsihp__qxk = context.make_helper(builder, char_arr_type,
                    keun__ovjp.data).data
                ohjkm__qnkc = context.make_helper(builder,
                    null_bitmap_arr_type, keun__ovjp.null_bitmap).data
                oma__jnwe = cgutils.pack_array(builder, [builder.bitcast(
                    kju__bpkzg, lir.IntType(8).as_pointer()), builder.
                    bitcast(ohjkm__qnkc, lir.IntType(8).as_pointer()),
                    builder.bitcast(xsihp__qxk, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                ibw__yrn = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                agt__nam = lir.Constant(lir.IntType(8).as_pointer(), None)
                oma__jnwe = cgutils.pack_array(builder, [agt__nam, ibw__yrn])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return oma__jnwe

        def get_field_names(arr_typ):
            ruydl__rurak = []
            if isinstance(arr_typ, StructArrayType):
                for cppck__zroab, rafcm__ojq in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    ruydl__rurak.append(cppck__zroab)
                    ruydl__rurak += get_field_names(rafcm__ojq)
            elif isinstance(arr_typ, ArrayItemArrayType):
                ruydl__rurak += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                ruydl__rurak += get_field_names(_get_map_arr_data_type(arr_typ)
                    )
            return ruydl__rurak
        djdns__eyj = get_types(arr_type)
        ifwy__ccmfz = cgutils.pack_array(builder, [context.get_constant(
            types.int32, t) for t in djdns__eyj])
        itx__ktmie = cgutils.alloca_once_value(builder, ifwy__ccmfz)
        tme__dftj = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, tme__dftj)
        oma__jnwe = get_buffers(arr_type, in_arr)
        polvw__wvpw = cgutils.alloca_once_value(builder, oma__jnwe)
        ruydl__rurak = get_field_names(arr_type)
        if len(ruydl__rurak) == 0:
            ruydl__rurak = ['irrelevant']
        iufqy__otc = cgutils.pack_array(builder, [context.
            insert_const_string(builder.module, a) for a in ruydl__rurak])
        fpni__yfa = cgutils.alloca_once_value(builder, iufqy__otc)
        if isinstance(arr_type, MapArrayType):
            kuts__oqw = _get_map_arr_data_type(arr_type)
            mmy__lkinx = context.make_helper(builder, arr_type, value=in_arr)
            jdeyn__cfvf = mmy__lkinx.data
        else:
            kuts__oqw = arr_type
            jdeyn__cfvf = in_arr
        avjkt__orh = context.make_helper(builder, kuts__oqw, jdeyn__cfvf)
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='nested_array_to_info')
        lcso__gtrnw = builder.call(ycoq__numu, [builder.bitcast(itx__ktmie,
            lir.IntType(32).as_pointer()), builder.bitcast(polvw__wvpw, lir
            .IntType(8).as_pointer().as_pointer()), builder.bitcast(
            lengths_ptr, lir.IntType(64).as_pointer()), builder.bitcast(
            fpni__yfa, lir.IntType(8).as_pointer()), avjkt__orh.meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return lcso__gtrnw
    if arr_type in (string_array_type, binary_array_type):
        kzky__wwst = context.make_helper(builder, arr_type, in_arr)
        rmbqy__wwy = ArrayItemArrayType(char_arr_type)
        qoe__prz = context.make_helper(builder, rmbqy__wwy, kzky__wwst.data)
        keun__ovjp = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        kju__bpkzg = context.make_helper(builder, offset_arr_type,
            keun__ovjp.offsets).data
        xsihp__qxk = context.make_helper(builder, char_arr_type, keun__ovjp
            .data).data
        ohjkm__qnkc = context.make_helper(builder, null_bitmap_arr_type,
            keun__ovjp.null_bitmap).data
        rmva__jojd = builder.zext(builder.load(builder.gep(kju__bpkzg, [
            keun__ovjp.n_arrays])), lir.IntType(64))
        wlu__tqsq = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='string_array_to_info')
        return builder.call(ycoq__numu, [keun__ovjp.n_arrays, rmva__jojd,
            xsihp__qxk, kju__bpkzg, ohjkm__qnkc, qoe__prz.meminfo, wlu__tqsq])
    ixnji__sdett = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        tmm__tozc = context.compile_internal(builder, lambda a: len(a.dtype
            .categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        mbgvy__crvql = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(mbgvy__crvql, 1, 'C')
        ixnji__sdett = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        ntxns__isc = builder.extract_value(arr.shape, 0)
        btn__fia = arr_type.dtype
        mbnu__txm = numba_to_c_type(btn__fia)
        guhhn__aue = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), mbnu__txm))
        if ixnji__sdett:
            uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(64), lir.IntType(8).as_pointer()])
            ycoq__numu = cgutils.get_or_insert_function(builder.module,
                uyku__uafj, name='categorical_array_to_info')
            return builder.call(ycoq__numu, [ntxns__isc, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                guhhn__aue), tmm__tozc, arr.meminfo])
        else:
            uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer()])
            ycoq__numu = cgutils.get_or_insert_function(builder.module,
                uyku__uafj, name='numpy_array_to_info')
            return builder.call(ycoq__numu, [ntxns__isc, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                guhhn__aue), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        btn__fia = arr_type.dtype
        bdrte__oipaj = btn__fia
        if isinstance(arr_type, DecimalArrayType):
            bdrte__oipaj = int128_type
        if arr_type == datetime_date_array_type:
            bdrte__oipaj = types.int64
        mnah__mqd = context.make_array(types.Array(bdrte__oipaj, 1, 'C'))(
            context, builder, arr.data)
        ntxns__isc = builder.extract_value(mnah__mqd.shape, 0)
        cwf__amiz = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, arr.null_bitmap)
        mbnu__txm = numba_to_c_type(btn__fia)
        guhhn__aue = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), mbnu__txm))
        if isinstance(arr_type, DecimalArrayType):
            uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer(), lir.IntType(32), lir.IntType(32)])
            ycoq__numu = cgutils.get_or_insert_function(builder.module,
                uyku__uafj, name='decimal_array_to_info')
            return builder.call(ycoq__numu, [ntxns__isc, builder.bitcast(
                mnah__mqd.data, lir.IntType(8).as_pointer()), builder.load(
                guhhn__aue), builder.bitcast(cwf__amiz.data, lir.IntType(8)
                .as_pointer()), mnah__mqd.meminfo, cwf__amiz.meminfo,
                context.get_constant(types.int32, arr_type.precision),
                context.get_constant(types.int32, arr_type.scale)])
        else:
            uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir
                .IntType(64), lir.IntType(8).as_pointer(), lir.IntType(32),
                lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(),
                lir.IntType(8).as_pointer()])
            ycoq__numu = cgutils.get_or_insert_function(builder.module,
                uyku__uafj, name='nullable_array_to_info')
            return builder.call(ycoq__numu, [ntxns__isc, builder.bitcast(
                mnah__mqd.data, lir.IntType(8).as_pointer()), builder.load(
                guhhn__aue), builder.bitcast(cwf__amiz.data, lir.IntType(8)
                .as_pointer()), mnah__mqd.meminfo, cwf__amiz.meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        jfnlm__lpb = context.make_array(arr_type.arr_type)(context, builder,
            arr.left)
        xhty__djfzl = context.make_array(arr_type.arr_type)(context,
            builder, arr.right)
        ntxns__isc = builder.extract_value(jfnlm__lpb.shape, 0)
        mbnu__txm = numba_to_c_type(arr_type.arr_type.dtype)
        guhhn__aue = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), mbnu__txm))
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='interval_array_to_info')
        return builder.call(ycoq__numu, [ntxns__isc, builder.bitcast(
            jfnlm__lpb.data, lir.IntType(8).as_pointer()), builder.bitcast(
            xhty__djfzl.data, lir.IntType(8).as_pointer()), builder.load(
            guhhn__aue), jfnlm__lpb.meminfo, xhty__djfzl.meminfo])
    raise BodoError(f'array_to_info(): array type {arr_type} is not supported')


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    kivf__zzf = cgutils.alloca_once(builder, lir.IntType(64))
    ibw__yrn = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    cry__fgfy = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    uyku__uafj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    ycoq__numu = cgutils.get_or_insert_function(builder.module, uyku__uafj,
        name='info_to_numpy_array')
    builder.call(ycoq__numu, [in_info, kivf__zzf, ibw__yrn, cry__fgfy])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    iaq__qxgob = context.get_value_type(types.intp)
    mwk__hbk = cgutils.pack_array(builder, [builder.load(kivf__zzf)], ty=
        iaq__qxgob)
    exsyw__tsukk = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    jtc__tnfde = cgutils.pack_array(builder, [exsyw__tsukk], ty=iaq__qxgob)
    xsihp__qxk = builder.bitcast(builder.load(ibw__yrn), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=xsihp__qxk, shape=mwk__hbk,
        strides=jtc__tnfde, itemsize=exsyw__tsukk, meminfo=builder.load(
        cry__fgfy))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    awfe__hocqi = context.make_helper(builder, arr_type)
    uyku__uafj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    ycoq__numu = cgutils.get_or_insert_function(builder.module, uyku__uafj,
        name='info_to_list_string_array')
    builder.call(ycoq__numu, [in_info, awfe__hocqi._get_ptr_by_name('meminfo')]
        )
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return awfe__hocqi._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    nyy__gkymw = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        imh__qofg = lengths_pos
        ygqfo__tzmhe = infos_pos
        ilkp__ktf, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        hvswi__jzcu = ArrayItemArrayPayloadType(arr_typ)
        wvql__vcdl = context.get_data_type(hvswi__jzcu)
        own__ykqw = context.get_abi_sizeof(wvql__vcdl)
        evu__die = define_array_item_dtor(context, builder, arr_typ,
            hvswi__jzcu)
        vgc__jvyy = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, own__ykqw), evu__die)
        asooh__jzht = context.nrt.meminfo_data(builder, vgc__jvyy)
        lzl__myie = builder.bitcast(asooh__jzht, wvql__vcdl.as_pointer())
        keun__ovjp = cgutils.create_struct_proxy(hvswi__jzcu)(context, builder)
        keun__ovjp.n_arrays = builder.extract_value(builder.load(
            lengths_ptr), imh__qofg)
        keun__ovjp.data = ilkp__ktf
        usuan__mbn = builder.load(array_infos_ptr)
        hjq__ckhn = builder.bitcast(builder.extract_value(usuan__mbn,
            ygqfo__tzmhe), nyy__gkymw)
        keun__ovjp.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, hjq__ckhn)
        degor__rfr = builder.bitcast(builder.extract_value(usuan__mbn, 
            ygqfo__tzmhe + 1), nyy__gkymw)
        keun__ovjp.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, degor__rfr)
        builder.store(keun__ovjp._getvalue(), lzl__myie)
        qoe__prz = context.make_helper(builder, arr_typ)
        qoe__prz.meminfo = vgc__jvyy
        return qoe__prz._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        xjk__rai = []
        ygqfo__tzmhe = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for tpf__qqcar in arr_typ.data:
            ilkp__ktf, lengths_pos, infos_pos = nested_to_array(context,
                builder, tpf__qqcar, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            xjk__rai.append(ilkp__ktf)
        hvswi__jzcu = StructArrayPayloadType(arr_typ.data)
        wvql__vcdl = context.get_value_type(hvswi__jzcu)
        own__ykqw = context.get_abi_sizeof(wvql__vcdl)
        evu__die = define_struct_arr_dtor(context, builder, arr_typ,
            hvswi__jzcu)
        vgc__jvyy = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, own__ykqw), evu__die)
        asooh__jzht = context.nrt.meminfo_data(builder, vgc__jvyy)
        lzl__myie = builder.bitcast(asooh__jzht, wvql__vcdl.as_pointer())
        keun__ovjp = cgutils.create_struct_proxy(hvswi__jzcu)(context, builder)
        keun__ovjp.data = cgutils.pack_array(builder, xjk__rai
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, xjk__rai)
        usuan__mbn = builder.load(array_infos_ptr)
        degor__rfr = builder.bitcast(builder.extract_value(usuan__mbn,
            ygqfo__tzmhe), nyy__gkymw)
        keun__ovjp.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, degor__rfr)
        builder.store(keun__ovjp._getvalue(), lzl__myie)
        negy__hldie = context.make_helper(builder, arr_typ)
        negy__hldie.meminfo = vgc__jvyy
        return negy__hldie._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        usuan__mbn = builder.load(array_infos_ptr)
        gdtry__fycgm = builder.bitcast(builder.extract_value(usuan__mbn,
            infos_pos), nyy__gkymw)
        kzky__wwst = context.make_helper(builder, arr_typ)
        rmbqy__wwy = ArrayItemArrayType(char_arr_type)
        qoe__prz = context.make_helper(builder, rmbqy__wwy)
        uyku__uafj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='info_to_string_array')
        builder.call(ycoq__numu, [gdtry__fycgm, qoe__prz._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        kzky__wwst.data = qoe__prz._getvalue()
        return kzky__wwst._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        usuan__mbn = builder.load(array_infos_ptr)
        dwd__sow = builder.bitcast(builder.extract_value(usuan__mbn, 
            infos_pos + 1), nyy__gkymw)
        return _lower_info_to_array_numpy(arr_typ, context, builder, dwd__sow
            ), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        bdrte__oipaj = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            bdrte__oipaj = int128_type
        elif arr_typ == datetime_date_array_type:
            bdrte__oipaj = types.int64
        usuan__mbn = builder.load(array_infos_ptr)
        degor__rfr = builder.bitcast(builder.extract_value(usuan__mbn,
            infos_pos), nyy__gkymw)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, degor__rfr)
        dwd__sow = builder.bitcast(builder.extract_value(usuan__mbn, 
            infos_pos + 1), nyy__gkymw)
        arr.data = _lower_info_to_array_numpy(types.Array(bdrte__oipaj, 1,
            'C'), context, builder, dwd__sow)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


@intrinsic
def info_to_array(typingctx, info_type, array_type):
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    assert info_type == array_info_type

    def codegen(context, builder, sig, args):
        in_info, lucb__ldbnq = args
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
                    return 1 + sum([get_num_arrays(tpf__qqcar) for
                        tpf__qqcar in arr_typ.data])
                else:
                    return 1

            def get_num_infos(arr_typ):
                if isinstance(arr_typ, ArrayItemArrayType):
                    return 2 + get_num_infos(arr_typ.dtype)
                elif isinstance(arr_typ, StructArrayType):
                    return 1 + sum([get_num_infos(tpf__qqcar) for
                        tpf__qqcar in arr_typ.data])
                elif arr_typ in (string_array_type, binary_array_type):
                    return 1
                else:
                    return 2
            if isinstance(arr_type, TupleArrayType):
                bxuo__ovrji = StructArrayType(arr_type.data, ('dummy',) *
                    len(arr_type.data))
            elif isinstance(arr_type, MapArrayType):
                bxuo__ovrji = _get_map_arr_data_type(arr_type)
            else:
                bxuo__ovrji = arr_type
            pgtf__jkpxt = get_num_arrays(bxuo__ovrji)
            tme__dftj = cgutils.pack_array(builder, [lir.Constant(lir.
                IntType(64), 0) for lucb__ldbnq in range(pgtf__jkpxt)])
            lengths_ptr = cgutils.alloca_once_value(builder, tme__dftj)
            agt__nam = lir.Constant(lir.IntType(8).as_pointer(), None)
            gtcky__brm = cgutils.pack_array(builder, [agt__nam for
                lucb__ldbnq in range(get_num_infos(bxuo__ovrji))])
            array_infos_ptr = cgutils.alloca_once_value(builder, gtcky__brm)
            uyku__uafj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
                as_pointer().as_pointer()])
            ycoq__numu = cgutils.get_or_insert_function(builder.module,
                uyku__uafj, name='info_to_nested_array')
            builder.call(ycoq__numu, [in_info, builder.bitcast(lengths_ptr,
                lir.IntType(64).as_pointer()), builder.bitcast(
                array_infos_ptr, lir.IntType(8).as_pointer().as_pointer())])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            arr, lucb__ldbnq, lucb__ldbnq = nested_to_array(context,
                builder, bxuo__ovrji, lengths_ptr, array_infos_ptr, 0, 0)
            if isinstance(arr_type, TupleArrayType):
                drig__xbh = context.make_helper(builder, arr_type)
                drig__xbh.data = arr
                context.nrt.incref(builder, bxuo__ovrji, arr)
                arr = drig__xbh._getvalue()
            elif isinstance(arr_type, MapArrayType):
                sig = signature(arr_type, bxuo__ovrji)
                arr = init_map_arr_codegen(context, builder, sig, (arr,))
            return arr
        if arr_type in (string_array_type, binary_array_type):
            kzky__wwst = context.make_helper(builder, arr_type)
            rmbqy__wwy = ArrayItemArrayType(char_arr_type)
            qoe__prz = context.make_helper(builder, rmbqy__wwy)
            uyku__uafj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
            ycoq__numu = cgutils.get_or_insert_function(builder.module,
                uyku__uafj, name='info_to_string_array')
            builder.call(ycoq__numu, [in_info, qoe__prz._get_ptr_by_name(
                'meminfo')])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            kzky__wwst.data = qoe__prz._getvalue()
            return kzky__wwst._getvalue()
        if isinstance(arr_type, CategoricalArrayType):
            out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
            mbgvy__crvql = get_categories_int_type(arr_type.dtype)
            tcv__mfwms = types.Array(mbgvy__crvql, 1, 'C')
            out_arr.codes = _lower_info_to_array_numpy(tcv__mfwms, context,
                builder, in_info)
            if isinstance(array_type, types.TypeRef):
                assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
                is_ordered = arr_type.dtype.ordered
                mxgpq__zagrb = pd.CategoricalDtype(arr_type.dtype.
                    categories, is_ordered).categories.values
                new_cats_tup = MetaType(tuple(mxgpq__zagrb))
                int_type = arr_type.dtype.int_type
                jyg__jfn = bodo.typeof(mxgpq__zagrb)
                bea__rfnbt = context.get_constant_generic(builder, jyg__jfn,
                    mxgpq__zagrb)
                btn__fia = context.compile_internal(builder, lambda c_arr:
                    bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.
                    utils.conversion.index_from_array(c_arr), is_ordered,
                    int_type, new_cats_tup), arr_type.dtype(jyg__jfn), [
                    bea__rfnbt])
            else:
                btn__fia = cgutils.create_struct_proxy(arr_type)(context,
                    builder, args[1]).dtype
                context.nrt.incref(builder, arr_type.dtype, btn__fia)
            out_arr.dtype = btn__fia
            return out_arr._getvalue()
        if isinstance(arr_type, types.Array):
            return _lower_info_to_array_numpy(arr_type, context, builder,
                in_info)
        if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
            ) or arr_type in (boolean_array, datetime_date_array_type):
            arr = cgutils.create_struct_proxy(arr_type)(context, builder)
            bdrte__oipaj = arr_type.dtype
            if isinstance(arr_type, DecimalArrayType):
                bdrte__oipaj = int128_type
            elif arr_type == datetime_date_array_type:
                bdrte__oipaj = types.int64
            yawl__gyhwp = types.Array(bdrte__oipaj, 1, 'C')
            mnah__mqd = context.make_array(yawl__gyhwp)(context, builder)
            lctf__nugd = types.Array(types.uint8, 1, 'C')
            hcq__elor = context.make_array(lctf__nugd)(context, builder)
            kivf__zzf = cgutils.alloca_once(builder, lir.IntType(64))
            atq__idw = cgutils.alloca_once(builder, lir.IntType(64))
            ibw__yrn = cgutils.alloca_once(builder, lir.IntType(8).as_pointer()
                )
            xlwc__rkn = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            cry__fgfy = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            rbfho__dpwh = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            uyku__uafj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64)
                .as_pointer(), lir.IntType(8).as_pointer().as_pointer(),
                lir.IntType(8).as_pointer().as_pointer(), lir.IntType(8).
                as_pointer().as_pointer(), lir.IntType(8).as_pointer().
                as_pointer()])
            ycoq__numu = cgutils.get_or_insert_function(builder.module,
                uyku__uafj, name='info_to_nullable_array')
            builder.call(ycoq__numu, [in_info, kivf__zzf, atq__idw,
                ibw__yrn, xlwc__rkn, cry__fgfy, rbfho__dpwh])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            iaq__qxgob = context.get_value_type(types.intp)
            mwk__hbk = cgutils.pack_array(builder, [builder.load(kivf__zzf)
                ], ty=iaq__qxgob)
            exsyw__tsukk = context.get_constant(types.intp, context.
                get_abi_sizeof(context.get_data_type(bdrte__oipaj)))
            jtc__tnfde = cgutils.pack_array(builder, [exsyw__tsukk], ty=
                iaq__qxgob)
            xsihp__qxk = builder.bitcast(builder.load(ibw__yrn), context.
                get_data_type(bdrte__oipaj).as_pointer())
            numba.np.arrayobj.populate_array(mnah__mqd, data=xsihp__qxk,
                shape=mwk__hbk, strides=jtc__tnfde, itemsize=exsyw__tsukk,
                meminfo=builder.load(cry__fgfy))
            arr.data = mnah__mqd._getvalue()
            mwk__hbk = cgutils.pack_array(builder, [builder.load(atq__idw)],
                ty=iaq__qxgob)
            exsyw__tsukk = context.get_constant(types.intp, context.
                get_abi_sizeof(context.get_data_type(types.uint8)))
            jtc__tnfde = cgutils.pack_array(builder, [exsyw__tsukk], ty=
                iaq__qxgob)
            xsihp__qxk = builder.bitcast(builder.load(xlwc__rkn), context.
                get_data_type(types.uint8).as_pointer())
            numba.np.arrayobj.populate_array(hcq__elor, data=xsihp__qxk,
                shape=mwk__hbk, strides=jtc__tnfde, itemsize=exsyw__tsukk,
                meminfo=builder.load(rbfho__dpwh))
            arr.null_bitmap = hcq__elor._getvalue()
            return arr._getvalue()
        if isinstance(arr_type, IntervalArrayType):
            arr = cgutils.create_struct_proxy(arr_type)(context, builder)
            jfnlm__lpb = context.make_array(arr_type.arr_type)(context, builder
                )
            xhty__djfzl = context.make_array(arr_type.arr_type)(context,
                builder)
            kivf__zzf = cgutils.alloca_once(builder, lir.IntType(64))
            frxi__lebr = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            iplcr__xcg = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            tkxw__hfwri = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            noiq__zmpj = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            uyku__uafj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
                as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
                as_pointer().as_pointer(), lir.IntType(8).as_pointer().
                as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir
                .IntType(8).as_pointer().as_pointer()])
            ycoq__numu = cgutils.get_or_insert_function(builder.module,
                uyku__uafj, name='info_to_interval_array')
            builder.call(ycoq__numu, [in_info, kivf__zzf, frxi__lebr,
                iplcr__xcg, tkxw__hfwri, noiq__zmpj])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            iaq__qxgob = context.get_value_type(types.intp)
            mwk__hbk = cgutils.pack_array(builder, [builder.load(kivf__zzf)
                ], ty=iaq__qxgob)
            exsyw__tsukk = context.get_constant(types.intp, context.
                get_abi_sizeof(context.get_data_type(arr_type.arr_type.dtype)))
            jtc__tnfde = cgutils.pack_array(builder, [exsyw__tsukk], ty=
                iaq__qxgob)
            ozc__drq = builder.bitcast(builder.load(frxi__lebr), context.
                get_data_type(arr_type.arr_type.dtype).as_pointer())
            numba.np.arrayobj.populate_array(jfnlm__lpb, data=ozc__drq,
                shape=mwk__hbk, strides=jtc__tnfde, itemsize=exsyw__tsukk,
                meminfo=builder.load(tkxw__hfwri))
            arr.left = jfnlm__lpb._getvalue()
            pmd__rsmao = builder.bitcast(builder.load(iplcr__xcg), context.
                get_data_type(arr_type.arr_type.dtype).as_pointer())
            numba.np.arrayobj.populate_array(xhty__djfzl, data=pmd__rsmao,
                shape=mwk__hbk, strides=jtc__tnfde, itemsize=exsyw__tsukk,
                meminfo=builder.load(noiq__zmpj))
            arr.right = xhty__djfzl._getvalue()
            return arr._getvalue()
        raise BodoError(
            f'info_to_array(): array type {arr_type} is not supported')
    return arr_type(info_type, array_type), codegen


@intrinsic
def test_alloc_np(typingctx, len_typ, arr_type):
    array_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type

    def codegen(context, builder, sig, args):
        ntxns__isc, lucb__ldbnq = args
        mbnu__txm = numba_to_c_type(array_type.dtype)
        guhhn__aue = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), mbnu__txm))
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='alloc_numpy')
        return builder.call(ycoq__numu, [ntxns__isc, builder.load(guhhn__aue)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        ntxns__isc, wrkj__jesxq = args
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='alloc_string_array')
        return builder.call(ycoq__numu, [ntxns__isc, wrkj__jesxq])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    vwigv__hrw, = args
    ieh__vsjwv = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], vwigv__hrw)
    uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.IntType
        (8).as_pointer().as_pointer(), lir.IntType(64)])
    ycoq__numu = cgutils.get_or_insert_function(builder.module, uyku__uafj,
        name='arr_info_list_to_table')
    return builder.call(ycoq__numu, [ieh__vsjwv.data, ieh__vsjwv.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='info_from_table')
        return builder.call(ycoq__numu, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    cgyj__zfb = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        wrce__wkmgq, ewsmc__jizy, lucb__ldbnq = args
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='info_from_table')
        njoa__uvimg = cgutils.create_struct_proxy(cgyj__zfb)(context, builder)
        njoa__uvimg.parent = cgutils.get_null_value(njoa__uvimg.parent.type)
        efgzz__hsdmr = context.make_array(table_idx_arr_t)(context, builder,
            ewsmc__jizy)
        myi__xuf = context.get_constant(types.int64, -1)
        jteq__vvvh = context.get_constant(types.int64, 0)
        ega__timjr = cgutils.alloca_once_value(builder, jteq__vvvh)
        for t, pcntm__ykz in cgyj__zfb.type_to_blk.items():
            odfdw__fxq = context.get_constant(types.int64, len(cgyj__zfb.
                block_to_arr_ind[pcntm__ykz]))
            lucb__ldbnq, pct__mpu = ListInstance.allocate_ex(context,
                builder, types.List(t), odfdw__fxq)
            pct__mpu.size = odfdw__fxq
            yzm__rix = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(cgyj__zfb.block_to_arr_ind[
                pcntm__ykz], dtype=np.int64))
            wiif__elhfh = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, yzm__rix)
            with cgutils.for_range(builder, odfdw__fxq) as loop:
                tnfov__racgi = loop.index
                dpec__mytm = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    wiif__elhfh, tnfov__racgi)
                ynnj__ece = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, efgzz__hsdmr, dpec__mytm)
                gvah__vemoj = builder.icmp_unsigned('!=', ynnj__ece, myi__xuf)
                with builder.if_else(gvah__vemoj) as (then, orelse):
                    with then:
                        sicn__dhy = builder.call(ycoq__numu, [wrce__wkmgq,
                            ynnj__ece])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            sicn__dhy])
                        pct__mpu.inititem(tnfov__racgi, arr, incref=False)
                        ntxns__isc = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(ntxns__isc, ega__timjr)
                    with orelse:
                        cmn__ejdl = context.get_constant_null(t)
                        pct__mpu.inititem(tnfov__racgi, cmn__ejdl, incref=False
                            )
            setattr(njoa__uvimg, f'block_{pcntm__ykz}', pct__mpu.value)
        njoa__uvimg.len = builder.load(ega__timjr)
        return njoa__uvimg._getvalue()
    return cgyj__zfb(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    cgyj__zfb = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        ljoau__tpl, lucb__ldbnq = args
        umpfb__tdzlv = lir.Constant(lir.IntType(64), len(cgyj__zfb.arr_types))
        lucb__ldbnq, tjgtb__nejjp = ListInstance.allocate_ex(context,
            builder, types.List(array_info_type), umpfb__tdzlv)
        tjgtb__nejjp.size = umpfb__tdzlv
        nxck__ochn = cgutils.create_struct_proxy(cgyj__zfb)(context,
            builder, ljoau__tpl)
        for t, pcntm__ykz in cgyj__zfb.type_to_blk.items():
            odfdw__fxq = context.get_constant(types.int64, len(cgyj__zfb.
                block_to_arr_ind[pcntm__ykz]))
            vwkol__jncx = getattr(nxck__ochn, f'block_{pcntm__ykz}')
            pyqm__ivnq = ListInstance(context, builder, types.List(t),
                vwkol__jncx)
            yzm__rix = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(cgyj__zfb.block_to_arr_ind[
                pcntm__ykz], dtype=np.int64))
            wiif__elhfh = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, yzm__rix)
            with cgutils.for_range(builder, odfdw__fxq) as loop:
                tnfov__racgi = loop.index
                dpec__mytm = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    wiif__elhfh, tnfov__racgi)
                uqz__ufdc = signature(types.none, cgyj__zfb, types.List(t),
                    types.int64, types.int64)
                oyo__uhli = ljoau__tpl, vwkol__jncx, tnfov__racgi, dpec__mytm
                bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                    builder, uqz__ufdc, oyo__uhli)
                arr = pyqm__ivnq.getitem(tnfov__racgi)
                vthnv__uhvg = signature(array_info_type, t)
                plap__ncci = arr,
                jwuv__jqy = array_to_info_codegen(context, builder,
                    vthnv__uhvg, plap__ncci)
                tjgtb__nejjp.inititem(dpec__mytm, jwuv__jqy, incref=False)
        ougmf__tit = tjgtb__nejjp.value
        msy__amf = signature(table_type, types.List(array_info_type))
        fvpg__bbpt = ougmf__tit,
        wrce__wkmgq = arr_info_list_to_table_codegen(context, builder,
            msy__amf, fvpg__bbpt)
        context.nrt.decref(builder, types.List(array_info_type), ougmf__tit)
        return wrce__wkmgq
    return table_type(cgyj__zfb, py_table_type_t), codegen


delete_info_decref_array = types.ExternalFunction('delete_info_decref_array',
    types.void(array_info_type))
delete_table_decref_arrays = types.ExternalFunction(
    'delete_table_decref_arrays', types.void(table_type))


@intrinsic
def delete_table(typingctx, table_t=None):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        uyku__uafj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='delete_table')
        builder.call(ycoq__numu, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='shuffle_table')
        lcso__gtrnw = builder.call(ycoq__numu, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return lcso__gtrnw
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
        uyku__uafj = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='delete_shuffle_info')
        return builder.call(ycoq__numu, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='reverse_shuffle_table')
        return builder.call(ycoq__numu, args)
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
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1), lir.IntType(1), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(8).as_pointer(), lir.IntType(64)])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='hash_join_table')
        lcso__gtrnw = builder.call(ycoq__numu, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return lcso__gtrnw
    return table_type(left_table_t, right_table_t, types.boolean, types.
        boolean, types.int64, types.int64, types.int64, types.voidptr,
        types.voidptr, types.boolean, types.boolean, types.boolean, types.
        boolean, types.boolean, types.boolean, types.voidptr, types.voidptr,
        types.int64, types.voidptr, types.int64), codegen


@intrinsic
def compute_node_partition_by_hash(typingctx, table_t, n_keys_t, n_pes_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='compute_node_partition_by_hash')
        lcso__gtrnw = builder.call(ycoq__numu, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return lcso__gtrnw
    return table_type(table_t, types.int64, types.int64), codegen


@intrinsic
def sort_values_table(typingctx, table_t, n_keys_t, vect_ascending_t,
    na_position_b_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='sort_values_table')
        lcso__gtrnw = builder.call(ycoq__numu, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return lcso__gtrnw
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='sample_table')
        lcso__gtrnw = builder.call(ycoq__numu, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return lcso__gtrnw
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='shuffle_renormalization')
        lcso__gtrnw = builder.call(ycoq__numu, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return lcso__gtrnw
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='shuffle_renormalization_group')
        lcso__gtrnw = builder.call(ycoq__numu, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return lcso__gtrnw
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1)])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='drop_duplicates_table')
        lcso__gtrnw = builder.call(ycoq__numu, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return lcso__gtrnw
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
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='pivot_groupby_and_aggregate')
        lcso__gtrnw = builder.call(ycoq__numu, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return lcso__gtrnw
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
        uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        ycoq__numu = cgutils.get_or_insert_function(builder.module,
            uyku__uafj, name='groupby_and_aggregate')
        lcso__gtrnw = builder.call(ycoq__numu, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return lcso__gtrnw
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
    wsogu__vpo = array_to_info(in_arr)
    auh__ygtz = array_to_info(in_values)
    asbh__eel = array_to_info(out_arr)
    grwt__qtxj = arr_info_list_to_table([wsogu__vpo, auh__ygtz, asbh__eel])
    _array_isin(asbh__eel, wsogu__vpo, auh__ygtz, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(grwt__qtxj)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.voidptr, array_info_type))


@numba.njit
def get_search_regex(in_arr, case, pat, out_arr):
    wsogu__vpo = array_to_info(in_arr)
    asbh__eel = array_to_info(out_arr)
    _get_search_regex(wsogu__vpo, case, pat, asbh__eel)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_dtype, c_ind):
    from llvmlite import ir as lir
    if isinstance(col_dtype, types.Number) or col_dtype in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                njoa__uvimg, abk__kye = args
                njoa__uvimg = builder.bitcast(njoa__uvimg, lir.IntType(8).
                    as_pointer().as_pointer())
                fbj__igsjr = lir.Constant(lir.IntType(64), c_ind)
                qxa__qrgm = builder.load(builder.gep(njoa__uvimg, [fbj__igsjr])
                    )
                qxa__qrgm = builder.bitcast(qxa__qrgm, context.
                    get_data_type(col_dtype).as_pointer())
                return builder.load(builder.gep(qxa__qrgm, [abk__kye]))
            return col_dtype(types.voidptr, types.int64), codegen
        return getitem_func
    if col_dtype == types.unicode_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                njoa__uvimg, abk__kye = args
                uyku__uafj = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64), lir.IntType(64).as_pointer()])
                tjohk__slipf = cgutils.get_or_insert_function(builder.
                    module, uyku__uafj, name='array_info_getitem')
                fbj__igsjr = lir.Constant(lir.IntType(64), c_ind)
                gkqu__tug = cgutils.alloca_once(builder, lir.IntType(64))
                args = njoa__uvimg, fbj__igsjr, abk__kye, gkqu__tug
                ibw__yrn = builder.call(tjohk__slipf, args)
                return context.make_tuple(builder, sig.return_type, [
                    ibw__yrn, builder.load(gkqu__tug)])
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
                xail__dynd, abk__kye = args
                xail__dynd = builder.bitcast(xail__dynd, lir.IntType(8).
                    as_pointer().as_pointer())
                fbj__igsjr = lir.Constant(lir.IntType(64), c_ind)
                qxa__qrgm = builder.load(builder.gep(xail__dynd, [fbj__igsjr]))
                ohjkm__qnkc = builder.bitcast(qxa__qrgm, context.
                    get_data_type(types.bool_).as_pointer())
                cfzdw__jtp = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    ohjkm__qnkc, abk__kye)
                klhd__rcc = builder.icmp_unsigned('!=', cfzdw__jtp, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(klhd__rcc, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        col_dtype = col_array_dtype.dtype
        if col_dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    njoa__uvimg, abk__kye = args
                    njoa__uvimg = builder.bitcast(njoa__uvimg, lir.IntType(
                        8).as_pointer().as_pointer())
                    fbj__igsjr = lir.Constant(lir.IntType(64), c_ind)
                    qxa__qrgm = builder.load(builder.gep(njoa__uvimg, [
                        fbj__igsjr]))
                    qxa__qrgm = builder.bitcast(qxa__qrgm, context.
                        get_data_type(col_dtype).as_pointer())
                    wrfcn__gdqti = builder.load(builder.gep(qxa__qrgm, [
                        abk__kye]))
                    klhd__rcc = builder.icmp_unsigned('!=', wrfcn__gdqti,
                        lir.Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(klhd__rcc, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(col_dtype, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    njoa__uvimg, abk__kye = args
                    njoa__uvimg = builder.bitcast(njoa__uvimg, lir.IntType(
                        8).as_pointer().as_pointer())
                    fbj__igsjr = lir.Constant(lir.IntType(64), c_ind)
                    qxa__qrgm = builder.load(builder.gep(njoa__uvimg, [
                        fbj__igsjr]))
                    qxa__qrgm = builder.bitcast(qxa__qrgm, context.
                        get_data_type(col_dtype).as_pointer())
                    wrfcn__gdqti = builder.load(builder.gep(qxa__qrgm, [
                        abk__kye]))
                    niz__xnn = signature(types.bool_, col_dtype)
                    cfzdw__jtp = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, niz__xnn, (wrfcn__gdqti,))
                    return builder.not_(builder.sext(cfzdw__jtp, lir.
                        IntType(8)))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
