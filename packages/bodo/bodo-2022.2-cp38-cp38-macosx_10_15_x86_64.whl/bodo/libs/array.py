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
        pwu__qlzl = context.make_helper(builder, arr_type, in_arr)
        in_arr = pwu__qlzl.data
        arr_type = StructArrayType(arr_type.data, ('dummy',) * len(arr_type
            .data))
    context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, ArrayItemArrayType
        ) and arr_type.dtype == string_array_type:
        xmn__xmf = context.make_helper(builder, arr_type, in_arr)
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer()])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='list_string_array_to_info')
        return builder.call(ywn__xfxpn, [xmn__xmf.meminfo])
    if isinstance(arr_type, (MapArrayType, ArrayItemArrayType, StructArrayType)
        ):

        def get_types(arr_typ):
            if isinstance(arr_typ, MapArrayType):
                return get_types(_get_map_arr_data_type(arr_typ))
            elif isinstance(arr_typ, ArrayItemArrayType):
                return [CTypeEnum.LIST.value] + get_types(arr_typ.dtype)
            elif isinstance(arr_typ, (StructType, StructArrayType)):
                vrr__jghw = [CTypeEnum.STRUCT.value, len(arr_typ.names)]
                for bmg__mta in arr_typ.data:
                    vrr__jghw += get_types(bmg__mta)
                return vrr__jghw
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
            nerq__hfjn = context.compile_internal(builder, lambda a: len(a),
                types.intp(arr_typ), [arr])
            if isinstance(arr_typ, MapArrayType):
                sfq__xna = context.make_helper(builder, arr_typ, value=arr)
                csxpt__cvn = get_lengths(_get_map_arr_data_type(arr_typ),
                    sfq__xna.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                iji__kmjl = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                csxpt__cvn = get_lengths(arr_typ.dtype, iji__kmjl.data)
                csxpt__cvn = cgutils.pack_array(builder, [iji__kmjl.
                    n_arrays] + [builder.extract_value(csxpt__cvn, fpb__qjk
                    ) for fpb__qjk in range(csxpt__cvn.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                iji__kmjl = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                csxpt__cvn = []
                for fpb__qjk, bmg__mta in enumerate(arr_typ.data):
                    tlw__yipau = get_lengths(bmg__mta, builder.
                        extract_value(iji__kmjl.data, fpb__qjk))
                    csxpt__cvn += [builder.extract_value(tlw__yipau,
                        ihi__hrrpz) for ihi__hrrpz in range(tlw__yipau.type
                        .count)]
                csxpt__cvn = cgutils.pack_array(builder, [nerq__hfjn,
                    context.get_constant(types.int64, -1)] + csxpt__cvn)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType,
                types.Array)) or arr_typ in (boolean_array,
                datetime_date_array_type, string_array_type, binary_array_type
                ):
                csxpt__cvn = cgutils.pack_array(builder, [nerq__hfjn])
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray')
            return csxpt__cvn

        def get_buffers(arr_typ, arr):
            if isinstance(arr_typ, MapArrayType):
                sfq__xna = context.make_helper(builder, arr_typ, value=arr)
                ogz__udqm = get_buffers(_get_map_arr_data_type(arr_typ),
                    sfq__xna.data)
            elif isinstance(arr_typ, ArrayItemArrayType):
                iji__kmjl = _get_array_item_arr_payload(context, builder,
                    arr_typ, arr)
                aemed__utkeh = get_buffers(arr_typ.dtype, iji__kmjl.data)
                xmt__ura = context.make_array(types.Array(offset_type, 1, 'C')
                    )(context, builder, iji__kmjl.offsets)
                lmbmz__odto = builder.bitcast(xmt__ura.data, lir.IntType(8)
                    .as_pointer())
                hkmi__hjn = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, iji__kmjl.null_bitmap)
                vfzkh__dty = builder.bitcast(hkmi__hjn.data, lir.IntType(8)
                    .as_pointer())
                ogz__udqm = cgutils.pack_array(builder, [lmbmz__odto,
                    vfzkh__dty] + [builder.extract_value(aemed__utkeh,
                    fpb__qjk) for fpb__qjk in range(aemed__utkeh.type.count)])
            elif isinstance(arr_typ, StructArrayType):
                iji__kmjl = _get_struct_arr_payload(context, builder,
                    arr_typ, arr)
                aemed__utkeh = []
                for fpb__qjk, bmg__mta in enumerate(arr_typ.data):
                    xpwdh__lrs = get_buffers(bmg__mta, builder.
                        extract_value(iji__kmjl.data, fpb__qjk))
                    aemed__utkeh += [builder.extract_value(xpwdh__lrs,
                        ihi__hrrpz) for ihi__hrrpz in range(xpwdh__lrs.type
                        .count)]
                hkmi__hjn = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, iji__kmjl.null_bitmap)
                vfzkh__dty = builder.bitcast(hkmi__hjn.data, lir.IntType(8)
                    .as_pointer())
                ogz__udqm = cgutils.pack_array(builder, [vfzkh__dty] +
                    aemed__utkeh)
            elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
                ) or arr_typ in (boolean_array, datetime_date_array_type):
                frkan__wbea = arr_typ.dtype
                if isinstance(arr_typ, DecimalArrayType):
                    frkan__wbea = int128_type
                elif arr_typ == datetime_date_array_type:
                    frkan__wbea = types.int64
                arr = cgutils.create_struct_proxy(arr_typ)(context, builder,
                    arr)
                obvjh__cjts = context.make_array(types.Array(frkan__wbea, 1,
                    'C'))(context, builder, arr.data)
                hkmi__hjn = context.make_array(types.Array(types.uint8, 1, 'C')
                    )(context, builder, arr.null_bitmap)
                rlc__pzs = builder.bitcast(obvjh__cjts.data, lir.IntType(8)
                    .as_pointer())
                vfzkh__dty = builder.bitcast(hkmi__hjn.data, lir.IntType(8)
                    .as_pointer())
                ogz__udqm = cgutils.pack_array(builder, [vfzkh__dty, rlc__pzs])
            elif arr_typ in (string_array_type, binary_array_type):
                iji__kmjl = _get_str_binary_arr_payload(context, builder,
                    arr, arr_typ)
                jvz__bzntw = context.make_helper(builder, offset_arr_type,
                    iji__kmjl.offsets).data
                eeq__uaes = context.make_helper(builder, char_arr_type,
                    iji__kmjl.data).data
                pdf__kumlk = context.make_helper(builder,
                    null_bitmap_arr_type, iji__kmjl.null_bitmap).data
                ogz__udqm = cgutils.pack_array(builder, [builder.bitcast(
                    jvz__bzntw, lir.IntType(8).as_pointer()), builder.
                    bitcast(pdf__kumlk, lir.IntType(8).as_pointer()),
                    builder.bitcast(eeq__uaes, lir.IntType(8).as_pointer())])
            elif isinstance(arr_typ, types.Array):
                arr = context.make_array(arr_typ)(context, builder, arr)
                rlc__pzs = builder.bitcast(arr.data, lir.IntType(8).
                    as_pointer())
                oond__keyzy = lir.Constant(lir.IntType(8).as_pointer(), None)
                ogz__udqm = cgutils.pack_array(builder, [oond__keyzy, rlc__pzs]
                    )
            else:
                raise RuntimeError(
                    'array_to_info: unsupported type for subarray ' + str(
                    arr_typ))
            return ogz__udqm

        def get_field_names(arr_typ):
            hcyu__yfph = []
            if isinstance(arr_typ, StructArrayType):
                for ibxwj__lcbq, krie__ypcp in zip(arr_typ.dtype.names,
                    arr_typ.data):
                    hcyu__yfph.append(ibxwj__lcbq)
                    hcyu__yfph += get_field_names(krie__ypcp)
            elif isinstance(arr_typ, ArrayItemArrayType):
                hcyu__yfph += get_field_names(arr_typ.dtype)
            elif isinstance(arr_typ, MapArrayType):
                hcyu__yfph += get_field_names(_get_map_arr_data_type(arr_typ))
            return hcyu__yfph
        vrr__jghw = get_types(arr_type)
        smdus__kln = cgutils.pack_array(builder, [context.get_constant(
            types.int32, t) for t in vrr__jghw])
        mdee__jtopt = cgutils.alloca_once_value(builder, smdus__kln)
        csxpt__cvn = get_lengths(arr_type, in_arr)
        lengths_ptr = cgutils.alloca_once_value(builder, csxpt__cvn)
        ogz__udqm = get_buffers(arr_type, in_arr)
        fjy__zybop = cgutils.alloca_once_value(builder, ogz__udqm)
        hcyu__yfph = get_field_names(arr_type)
        if len(hcyu__yfph) == 0:
            hcyu__yfph = ['irrelevant']
        efk__cegf = cgutils.pack_array(builder, [context.
            insert_const_string(builder.module, a) for a in hcyu__yfph])
        oxhq__rhduh = cgutils.alloca_once_value(builder, efk__cegf)
        if isinstance(arr_type, MapArrayType):
            kjbb__grlio = _get_map_arr_data_type(arr_type)
            pjte__nthku = context.make_helper(builder, arr_type, value=in_arr)
            knokd__lxby = pjte__nthku.data
        else:
            kjbb__grlio = arr_type
            knokd__lxby = in_arr
        upg__uss = context.make_helper(builder, kjbb__grlio, knokd__lxby)
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(32).as_pointer(), lir.IntType(8).as_pointer().
            as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='nested_array_to_info')
        asgp__btiya = builder.call(ywn__xfxpn, [builder.bitcast(mdee__jtopt,
            lir.IntType(32).as_pointer()), builder.bitcast(fjy__zybop, lir.
            IntType(8).as_pointer().as_pointer()), builder.bitcast(
            lengths_ptr, lir.IntType(64).as_pointer()), builder.bitcast(
            oxhq__rhduh, lir.IntType(8).as_pointer()), upg__uss.meminfo])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return asgp__btiya
    if arr_type in (string_array_type, binary_array_type):
        blhcu__nowiz = context.make_helper(builder, arr_type, in_arr)
        xmsye__ndc = ArrayItemArrayType(char_arr_type)
        xmn__xmf = context.make_helper(builder, xmsye__ndc, blhcu__nowiz.data)
        iji__kmjl = _get_str_binary_arr_payload(context, builder, in_arr,
            arr_type)
        jvz__bzntw = context.make_helper(builder, offset_arr_type,
            iji__kmjl.offsets).data
        eeq__uaes = context.make_helper(builder, char_arr_type, iji__kmjl.data
            ).data
        pdf__kumlk = context.make_helper(builder, null_bitmap_arr_type,
            iji__kmjl.null_bitmap).data
        gmdc__zsy = builder.zext(builder.load(builder.gep(jvz__bzntw, [
            iji__kmjl.n_arrays])), lir.IntType(64))
        rkbdk__idf = context.get_constant(types.int32, int(arr_type ==
            binary_array_type))
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64), lir.IntType(8).as_pointer(), lir.
            IntType(offset_type.bitwidth).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(32)])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='string_array_to_info')
        return builder.call(ywn__xfxpn, [iji__kmjl.n_arrays, gmdc__zsy,
            eeq__uaes, jvz__bzntw, pdf__kumlk, xmn__xmf.meminfo, rkbdk__idf])
    bdsmp__xlz = False
    if isinstance(arr_type, CategoricalArrayType):
        context.nrt.decref(builder, arr_type, in_arr)
        tpg__cfs = context.compile_internal(builder, lambda a: len(a.dtype.
            categories), types.intp(arr_type), [in_arr])
        in_arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr
            ).codes
        jqpgk__umxf = get_categories_int_type(arr_type.dtype)
        arr_type = types.Array(jqpgk__umxf, 1, 'C')
        bdsmp__xlz = True
        context.nrt.incref(builder, arr_type, in_arr)
    if isinstance(arr_type, types.Array):
        arr = context.make_array(arr_type)(context, builder, in_arr)
        assert arr_type.ndim == 1, 'only 1D array shuffle supported'
        nerq__hfjn = builder.extract_value(arr.shape, 0)
        mva__opxzt = arr_type.dtype
        ooo__slv = numba_to_c_type(mva__opxzt)
        xnbe__etu = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), ooo__slv))
        if bdsmp__xlz:
            rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(64), lir.IntType(8).as_pointer()])
            ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
                rdbcc__ngyql, name='categorical_array_to_info')
            return builder.call(ywn__xfxpn, [nerq__hfjn, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                xnbe__etu), tpg__cfs, arr.meminfo])
        else:
            rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer()])
            ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
                rdbcc__ngyql, name='numpy_array_to_info')
            return builder.call(ywn__xfxpn, [nerq__hfjn, builder.bitcast(
                arr.data, lir.IntType(8).as_pointer()), builder.load(
                xnbe__etu), arr.meminfo])
    if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
        ) or arr_type in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        mva__opxzt = arr_type.dtype
        frkan__wbea = mva__opxzt
        if isinstance(arr_type, DecimalArrayType):
            frkan__wbea = int128_type
        if arr_type == datetime_date_array_type:
            frkan__wbea = types.int64
        obvjh__cjts = context.make_array(types.Array(frkan__wbea, 1, 'C'))(
            context, builder, arr.data)
        nerq__hfjn = builder.extract_value(obvjh__cjts.shape, 0)
        qzwni__lnhm = context.make_array(types.Array(types.uint8, 1, 'C'))(
            context, builder, arr.null_bitmap)
        ooo__slv = numba_to_c_type(mva__opxzt)
        xnbe__etu = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), ooo__slv))
        if isinstance(arr_type, DecimalArrayType):
            rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer
                (), lir.IntType(8).as_pointer(), lir.IntType(32), lir.
                IntType(32)])
            ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
                rdbcc__ngyql, name='decimal_array_to_info')
            return builder.call(ywn__xfxpn, [nerq__hfjn, builder.bitcast(
                obvjh__cjts.data, lir.IntType(8).as_pointer()), builder.
                load(xnbe__etu), builder.bitcast(qzwni__lnhm.data, lir.
                IntType(8).as_pointer()), obvjh__cjts.meminfo, qzwni__lnhm.
                meminfo, context.get_constant(types.int32, arr_type.
                precision), context.get_constant(types.int32, arr_type.scale)])
        else:
            rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [
                lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(
                32), lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer
                (), lir.IntType(8).as_pointer()])
            ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
                rdbcc__ngyql, name='nullable_array_to_info')
            return builder.call(ywn__xfxpn, [nerq__hfjn, builder.bitcast(
                obvjh__cjts.data, lir.IntType(8).as_pointer()), builder.
                load(xnbe__etu), builder.bitcast(qzwni__lnhm.data, lir.
                IntType(8).as_pointer()), obvjh__cjts.meminfo, qzwni__lnhm.
                meminfo])
    if isinstance(arr_type, IntervalArrayType):
        assert isinstance(arr_type.arr_type, types.Array
            ), 'array_to_info(): only IntervalArrayType with Numpy arrays supported'
        arr = cgutils.create_struct_proxy(arr_type)(context, builder, in_arr)
        vvun__osker = context.make_array(arr_type.arr_type)(context,
            builder, arr.left)
        fkafc__oyk = context.make_array(arr_type.arr_type)(context, builder,
            arr.right)
        nerq__hfjn = builder.extract_value(vvun__osker.shape, 0)
        ooo__slv = numba_to_c_type(arr_type.arr_type.dtype)
        xnbe__etu = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), ooo__slv))
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(32), lir.IntType(8).as_pointer(), lir
            .IntType(8).as_pointer()])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='interval_array_to_info')
        return builder.call(ywn__xfxpn, [nerq__hfjn, builder.bitcast(
            vvun__osker.data, lir.IntType(8).as_pointer()), builder.bitcast
            (fkafc__oyk.data, lir.IntType(8).as_pointer()), builder.load(
            xnbe__etu), vvun__osker.meminfo, fkafc__oyk.meminfo])
    raise BodoError(f'array_to_info(): array type {arr_type} is not supported')


def _lower_info_to_array_numpy(arr_type, context, builder, in_info):
    assert arr_type.ndim == 1, 'only 1D array supported'
    arr = context.make_array(arr_type)(context, builder)
    vhas__kbeqj = cgutils.alloca_once(builder, lir.IntType(64))
    rlc__pzs = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    huvt__fazaq = cgutils.alloca_once(builder, lir.IntType(8).as_pointer())
    rdbcc__ngyql = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8).
        as_pointer().as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
        rdbcc__ngyql, name='info_to_numpy_array')
    builder.call(ywn__xfxpn, [in_info, vhas__kbeqj, rlc__pzs, huvt__fazaq])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    tcrue__suspl = context.get_value_type(types.intp)
    rkttq__jhs = cgutils.pack_array(builder, [builder.load(vhas__kbeqj)],
        ty=tcrue__suspl)
    ywp__rebqt = context.get_constant(types.intp, context.get_abi_sizeof(
        context.get_data_type(arr_type.dtype)))
    bwtt__zsuim = cgutils.pack_array(builder, [ywp__rebqt], ty=tcrue__suspl)
    eeq__uaes = builder.bitcast(builder.load(rlc__pzs), context.
        get_data_type(arr_type.dtype).as_pointer())
    numba.np.arrayobj.populate_array(arr, data=eeq__uaes, shape=rkttq__jhs,
        strides=bwtt__zsuim, itemsize=ywp__rebqt, meminfo=builder.load(
        huvt__fazaq))
    return arr._getvalue()


def _lower_info_to_array_list_string_array(arr_type, context, builder, in_info
    ):
    lib__woekf = context.make_helper(builder, arr_type)
    rdbcc__ngyql = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
        as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
    ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
        rdbcc__ngyql, name='info_to_list_string_array')
    builder.call(ywn__xfxpn, [in_info, lib__woekf._get_ptr_by_name('meminfo')])
    context.compile_internal(builder, lambda :
        check_and_propagate_cpp_exception(), types.none(), [])
    return lib__woekf._getvalue()


def nested_to_array(context, builder, arr_typ, lengths_ptr, array_infos_ptr,
    lengths_pos, infos_pos):
    lgcz__bjey = context.get_data_type(array_info_type)
    if isinstance(arr_typ, ArrayItemArrayType):
        ryyf__lgs = lengths_pos
        spp__gklg = infos_pos
        tbi__spkwj, lengths_pos, infos_pos = nested_to_array(context,
            builder, arr_typ.dtype, lengths_ptr, array_infos_ptr, 
            lengths_pos + 1, infos_pos + 2)
        kofi__akcv = ArrayItemArrayPayloadType(arr_typ)
        nkwj__bwp = context.get_data_type(kofi__akcv)
        xpo__rnjro = context.get_abi_sizeof(nkwj__bwp)
        tpax__henlg = define_array_item_dtor(context, builder, arr_typ,
            kofi__akcv)
        keqx__quvv = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, xpo__rnjro), tpax__henlg)
        lyy__zkcp = context.nrt.meminfo_data(builder, keqx__quvv)
        wlnhl__mbd = builder.bitcast(lyy__zkcp, nkwj__bwp.as_pointer())
        iji__kmjl = cgutils.create_struct_proxy(kofi__akcv)(context, builder)
        iji__kmjl.n_arrays = builder.extract_value(builder.load(lengths_ptr
            ), ryyf__lgs)
        iji__kmjl.data = tbi__spkwj
        cshpj__ivrzc = builder.load(array_infos_ptr)
        jzx__icfaq = builder.bitcast(builder.extract_value(cshpj__ivrzc,
            spp__gklg), lgcz__bjey)
        iji__kmjl.offsets = _lower_info_to_array_numpy(types.Array(
            offset_type, 1, 'C'), context, builder, jzx__icfaq)
        xgblt__wwf = builder.bitcast(builder.extract_value(cshpj__ivrzc, 
            spp__gklg + 1), lgcz__bjey)
        iji__kmjl.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, xgblt__wwf)
        builder.store(iji__kmjl._getvalue(), wlnhl__mbd)
        xmn__xmf = context.make_helper(builder, arr_typ)
        xmn__xmf.meminfo = keqx__quvv
        return xmn__xmf._getvalue(), lengths_pos, infos_pos
    elif isinstance(arr_typ, StructArrayType):
        qvm__xhksl = []
        spp__gklg = infos_pos
        lengths_pos += 1
        infos_pos += 1
        for tkszv__eesk in arr_typ.data:
            tbi__spkwj, lengths_pos, infos_pos = nested_to_array(context,
                builder, tkszv__eesk, lengths_ptr, array_infos_ptr,
                lengths_pos, infos_pos)
            qvm__xhksl.append(tbi__spkwj)
        kofi__akcv = StructArrayPayloadType(arr_typ.data)
        nkwj__bwp = context.get_value_type(kofi__akcv)
        xpo__rnjro = context.get_abi_sizeof(nkwj__bwp)
        tpax__henlg = define_struct_arr_dtor(context, builder, arr_typ,
            kofi__akcv)
        keqx__quvv = context.nrt.meminfo_alloc_dtor(builder, context.
            get_constant(types.uintp, xpo__rnjro), tpax__henlg)
        lyy__zkcp = context.nrt.meminfo_data(builder, keqx__quvv)
        wlnhl__mbd = builder.bitcast(lyy__zkcp, nkwj__bwp.as_pointer())
        iji__kmjl = cgutils.create_struct_proxy(kofi__akcv)(context, builder)
        iji__kmjl.data = cgutils.pack_array(builder, qvm__xhksl
            ) if types.is_homogeneous(*arr_typ.data) else cgutils.pack_struct(
            builder, qvm__xhksl)
        cshpj__ivrzc = builder.load(array_infos_ptr)
        xgblt__wwf = builder.bitcast(builder.extract_value(cshpj__ivrzc,
            spp__gklg), lgcz__bjey)
        iji__kmjl.null_bitmap = _lower_info_to_array_numpy(types.Array(
            types.uint8, 1, 'C'), context, builder, xgblt__wwf)
        builder.store(iji__kmjl._getvalue(), wlnhl__mbd)
        esyjo__tldwg = context.make_helper(builder, arr_typ)
        esyjo__tldwg.meminfo = keqx__quvv
        return esyjo__tldwg._getvalue(), lengths_pos, infos_pos
    elif arr_typ in (string_array_type, binary_array_type):
        cshpj__ivrzc = builder.load(array_infos_ptr)
        wjh__dfur = builder.bitcast(builder.extract_value(cshpj__ivrzc,
            infos_pos), lgcz__bjey)
        blhcu__nowiz = context.make_helper(builder, arr_typ)
        xmsye__ndc = ArrayItemArrayType(char_arr_type)
        xmn__xmf = context.make_helper(builder, xmsye__ndc)
        rdbcc__ngyql = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='info_to_string_array')
        builder.call(ywn__xfxpn, [wjh__dfur, xmn__xmf._get_ptr_by_name(
            'meminfo')])
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        blhcu__nowiz.data = xmn__xmf._getvalue()
        return blhcu__nowiz._getvalue(), lengths_pos + 1, infos_pos + 1
    elif isinstance(arr_typ, types.Array):
        cshpj__ivrzc = builder.load(array_infos_ptr)
        inns__tvgqx = builder.bitcast(builder.extract_value(cshpj__ivrzc, 
            infos_pos + 1), lgcz__bjey)
        return _lower_info_to_array_numpy(arr_typ, context, builder,
            inns__tvgqx), lengths_pos + 1, infos_pos + 2
    elif isinstance(arr_typ, (IntegerArrayType, DecimalArrayType)
        ) or arr_typ in (boolean_array, datetime_date_array_type):
        arr = cgutils.create_struct_proxy(arr_typ)(context, builder)
        frkan__wbea = arr_typ.dtype
        if isinstance(arr_typ, DecimalArrayType):
            frkan__wbea = int128_type
        elif arr_typ == datetime_date_array_type:
            frkan__wbea = types.int64
        cshpj__ivrzc = builder.load(array_infos_ptr)
        xgblt__wwf = builder.bitcast(builder.extract_value(cshpj__ivrzc,
            infos_pos), lgcz__bjey)
        arr.null_bitmap = _lower_info_to_array_numpy(types.Array(types.
            uint8, 1, 'C'), context, builder, xgblt__wwf)
        inns__tvgqx = builder.bitcast(builder.extract_value(cshpj__ivrzc, 
            infos_pos + 1), lgcz__bjey)
        arr.data = _lower_info_to_array_numpy(types.Array(frkan__wbea, 1,
            'C'), context, builder, inns__tvgqx)
        return arr._getvalue(), lengths_pos + 1, infos_pos + 2


@intrinsic
def info_to_array(typingctx, info_type, array_type):
    arr_type = array_type.instance_type if isinstance(array_type, types.TypeRef
        ) else array_type
    assert info_type == array_info_type

    def codegen(context, builder, sig, args):
        in_info, pqlkn__prjj = args
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
                    return 1 + sum([get_num_arrays(tkszv__eesk) for
                        tkszv__eesk in arr_typ.data])
                else:
                    return 1

            def get_num_infos(arr_typ):
                if isinstance(arr_typ, ArrayItemArrayType):
                    return 2 + get_num_infos(arr_typ.dtype)
                elif isinstance(arr_typ, StructArrayType):
                    return 1 + sum([get_num_infos(tkszv__eesk) for
                        tkszv__eesk in arr_typ.data])
                elif arr_typ in (string_array_type, binary_array_type):
                    return 1
                else:
                    return 2
            if isinstance(arr_type, TupleArrayType):
                krw__ule = StructArrayType(arr_type.data, ('dummy',) * len(
                    arr_type.data))
            elif isinstance(arr_type, MapArrayType):
                krw__ule = _get_map_arr_data_type(arr_type)
            else:
                krw__ule = arr_type
            zgc__boaii = get_num_arrays(krw__ule)
            csxpt__cvn = cgutils.pack_array(builder, [lir.Constant(lir.
                IntType(64), 0) for pqlkn__prjj in range(zgc__boaii)])
            lengths_ptr = cgutils.alloca_once_value(builder, csxpt__cvn)
            oond__keyzy = lir.Constant(lir.IntType(8).as_pointer(), None)
            xzds__gbkot = cgutils.pack_array(builder, [oond__keyzy for
                pqlkn__prjj in range(get_num_infos(krw__ule))])
            array_infos_ptr = cgutils.alloca_once_value(builder, xzds__gbkot)
            rdbcc__ngyql = lir.FunctionType(lir.VoidType(), [lir.IntType(8)
                .as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8)
                .as_pointer().as_pointer()])
            ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
                rdbcc__ngyql, name='info_to_nested_array')
            builder.call(ywn__xfxpn, [in_info, builder.bitcast(lengths_ptr,
                lir.IntType(64).as_pointer()), builder.bitcast(
                array_infos_ptr, lir.IntType(8).as_pointer().as_pointer())])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            arr, pqlkn__prjj, pqlkn__prjj = nested_to_array(context,
                builder, krw__ule, lengths_ptr, array_infos_ptr, 0, 0)
            if isinstance(arr_type, TupleArrayType):
                pwu__qlzl = context.make_helper(builder, arr_type)
                pwu__qlzl.data = arr
                context.nrt.incref(builder, krw__ule, arr)
                arr = pwu__qlzl._getvalue()
            elif isinstance(arr_type, MapArrayType):
                sig = signature(arr_type, krw__ule)
                arr = init_map_arr_codegen(context, builder, sig, (arr,))
            return arr
        if arr_type in (string_array_type, binary_array_type):
            blhcu__nowiz = context.make_helper(builder, arr_type)
            xmsye__ndc = ArrayItemArrayType(char_arr_type)
            xmn__xmf = context.make_helper(builder, xmsye__ndc)
            rdbcc__ngyql = lir.FunctionType(lir.VoidType(), [lir.IntType(8)
                .as_pointer(), lir.IntType(8).as_pointer().as_pointer()])
            ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
                rdbcc__ngyql, name='info_to_string_array')
            builder.call(ywn__xfxpn, [in_info, xmn__xmf._get_ptr_by_name(
                'meminfo')])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            blhcu__nowiz.data = xmn__xmf._getvalue()
            return blhcu__nowiz._getvalue()
        if isinstance(arr_type, CategoricalArrayType):
            out_arr = cgutils.create_struct_proxy(arr_type)(context, builder)
            jqpgk__umxf = get_categories_int_type(arr_type.dtype)
            evtfy__ruksu = types.Array(jqpgk__umxf, 1, 'C')
            out_arr.codes = _lower_info_to_array_numpy(evtfy__ruksu,
                context, builder, in_info)
            if isinstance(array_type, types.TypeRef):
                assert arr_type.dtype.categories is not None, 'info_to_array: unknown categories'
                is_ordered = arr_type.dtype.ordered
                goc__nfvq = pd.CategoricalDtype(arr_type.dtype.categories,
                    is_ordered).categories.values
                new_cats_tup = MetaType(tuple(goc__nfvq))
                int_type = arr_type.dtype.int_type
                hfmr__tdsw = bodo.typeof(goc__nfvq)
                nof__pzo = context.get_constant_generic(builder, hfmr__tdsw,
                    goc__nfvq)
                mva__opxzt = context.compile_internal(builder, lambda c_arr:
                    bodo.hiframes.pd_categorical_ext.init_cat_dtype(bodo.
                    utils.conversion.index_from_array(c_arr), is_ordered,
                    int_type, new_cats_tup), arr_type.dtype(hfmr__tdsw), [
                    nof__pzo])
            else:
                mva__opxzt = cgutils.create_struct_proxy(arr_type)(context,
                    builder, args[1]).dtype
                context.nrt.incref(builder, arr_type.dtype, mva__opxzt)
            out_arr.dtype = mva__opxzt
            return out_arr._getvalue()
        if isinstance(arr_type, types.Array):
            return _lower_info_to_array_numpy(arr_type, context, builder,
                in_info)
        if isinstance(arr_type, (IntegerArrayType, DecimalArrayType)
            ) or arr_type in (boolean_array, datetime_date_array_type):
            arr = cgutils.create_struct_proxy(arr_type)(context, builder)
            frkan__wbea = arr_type.dtype
            if isinstance(arr_type, DecimalArrayType):
                frkan__wbea = int128_type
            elif arr_type == datetime_date_array_type:
                frkan__wbea = types.int64
            twwn__caffh = types.Array(frkan__wbea, 1, 'C')
            obvjh__cjts = context.make_array(twwn__caffh)(context, builder)
            ktjhw__sry = types.Array(types.uint8, 1, 'C')
            nlu__eofz = context.make_array(ktjhw__sry)(context, builder)
            vhas__kbeqj = cgutils.alloca_once(builder, lir.IntType(64))
            xfcx__dvyq = cgutils.alloca_once(builder, lir.IntType(64))
            rlc__pzs = cgutils.alloca_once(builder, lir.IntType(8).as_pointer()
                )
            aybzn__fvj = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            huvt__fazaq = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            usxf__ipc = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            rdbcc__ngyql = lir.FunctionType(lir.VoidType(), [lir.IntType(8)
                .as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(64
                ).as_pointer(), lir.IntType(8).as_pointer().as_pointer(),
                lir.IntType(8).as_pointer().as_pointer(), lir.IntType(8).
                as_pointer().as_pointer(), lir.IntType(8).as_pointer().
                as_pointer()])
            ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
                rdbcc__ngyql, name='info_to_nullable_array')
            builder.call(ywn__xfxpn, [in_info, vhas__kbeqj, xfcx__dvyq,
                rlc__pzs, aybzn__fvj, huvt__fazaq, usxf__ipc])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            tcrue__suspl = context.get_value_type(types.intp)
            rkttq__jhs = cgutils.pack_array(builder, [builder.load(
                vhas__kbeqj)], ty=tcrue__suspl)
            ywp__rebqt = context.get_constant(types.intp, context.
                get_abi_sizeof(context.get_data_type(frkan__wbea)))
            bwtt__zsuim = cgutils.pack_array(builder, [ywp__rebqt], ty=
                tcrue__suspl)
            eeq__uaes = builder.bitcast(builder.load(rlc__pzs), context.
                get_data_type(frkan__wbea).as_pointer())
            numba.np.arrayobj.populate_array(obvjh__cjts, data=eeq__uaes,
                shape=rkttq__jhs, strides=bwtt__zsuim, itemsize=ywp__rebqt,
                meminfo=builder.load(huvt__fazaq))
            arr.data = obvjh__cjts._getvalue()
            rkttq__jhs = cgutils.pack_array(builder, [builder.load(
                xfcx__dvyq)], ty=tcrue__suspl)
            ywp__rebqt = context.get_constant(types.intp, context.
                get_abi_sizeof(context.get_data_type(types.uint8)))
            bwtt__zsuim = cgutils.pack_array(builder, [ywp__rebqt], ty=
                tcrue__suspl)
            eeq__uaes = builder.bitcast(builder.load(aybzn__fvj), context.
                get_data_type(types.uint8).as_pointer())
            numba.np.arrayobj.populate_array(nlu__eofz, data=eeq__uaes,
                shape=rkttq__jhs, strides=bwtt__zsuim, itemsize=ywp__rebqt,
                meminfo=builder.load(usxf__ipc))
            arr.null_bitmap = nlu__eofz._getvalue()
            return arr._getvalue()
        if isinstance(arr_type, IntervalArrayType):
            arr = cgutils.create_struct_proxy(arr_type)(context, builder)
            vvun__osker = context.make_array(arr_type.arr_type)(context,
                builder)
            fkafc__oyk = context.make_array(arr_type.arr_type)(context, builder
                )
            vhas__kbeqj = cgutils.alloca_once(builder, lir.IntType(64))
            gpsro__eua = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            psun__nni = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            uhboz__dykf = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            vvayf__ilsu = cgutils.alloca_once(builder, lir.IntType(8).
                as_pointer())
            rdbcc__ngyql = lir.FunctionType(lir.VoidType(), [lir.IntType(8)
                .as_pointer(), lir.IntType(64).as_pointer(), lir.IntType(8)
                .as_pointer().as_pointer(), lir.IntType(8).as_pointer().
                as_pointer(), lir.IntType(8).as_pointer().as_pointer(), lir
                .IntType(8).as_pointer().as_pointer()])
            ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
                rdbcc__ngyql, name='info_to_interval_array')
            builder.call(ywn__xfxpn, [in_info, vhas__kbeqj, gpsro__eua,
                psun__nni, uhboz__dykf, vvayf__ilsu])
            context.compile_internal(builder, lambda :
                check_and_propagate_cpp_exception(), types.none(), [])
            tcrue__suspl = context.get_value_type(types.intp)
            rkttq__jhs = cgutils.pack_array(builder, [builder.load(
                vhas__kbeqj)], ty=tcrue__suspl)
            ywp__rebqt = context.get_constant(types.intp, context.
                get_abi_sizeof(context.get_data_type(arr_type.arr_type.dtype)))
            bwtt__zsuim = cgutils.pack_array(builder, [ywp__rebqt], ty=
                tcrue__suspl)
            eaw__loe = builder.bitcast(builder.load(gpsro__eua), context.
                get_data_type(arr_type.arr_type.dtype).as_pointer())
            numba.np.arrayobj.populate_array(vvun__osker, data=eaw__loe,
                shape=rkttq__jhs, strides=bwtt__zsuim, itemsize=ywp__rebqt,
                meminfo=builder.load(uhboz__dykf))
            arr.left = vvun__osker._getvalue()
            yvzo__fhzc = builder.bitcast(builder.load(psun__nni), context.
                get_data_type(arr_type.arr_type.dtype).as_pointer())
            numba.np.arrayobj.populate_array(fkafc__oyk, data=yvzo__fhzc,
                shape=rkttq__jhs, strides=bwtt__zsuim, itemsize=ywp__rebqt,
                meminfo=builder.load(vvayf__ilsu))
            arr.right = fkafc__oyk._getvalue()
            return arr._getvalue()
        raise BodoError(
            f'info_to_array(): array type {arr_type} is not supported')
    return arr_type(info_type, array_type), codegen


@intrinsic
def test_alloc_np(typingctx, len_typ, arr_type):
    array_type = arr_type.instance_type if isinstance(arr_type, types.TypeRef
        ) else arr_type

    def codegen(context, builder, sig, args):
        nerq__hfjn, pqlkn__prjj = args
        ooo__slv = numba_to_c_type(array_type.dtype)
        xnbe__etu = cgutils.alloca_once_value(builder, lir.Constant(lir.
            IntType(32), ooo__slv))
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(32)])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='alloc_numpy')
        return builder.call(ywn__xfxpn, [nerq__hfjn, builder.load(xnbe__etu)])
    return array_info_type(len_typ, arr_type), codegen


@intrinsic
def test_alloc_string(typingctx, len_typ, n_chars_typ):

    def codegen(context, builder, sig, args):
        nerq__hfjn, saz__dfyb = args
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(64), lir.IntType(64)])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='alloc_string_array')
        return builder.call(ywn__xfxpn, [nerq__hfjn, saz__dfyb])
    return array_info_type(len_typ, n_chars_typ), codegen


@intrinsic
def arr_info_list_to_table(typingctx, list_arr_info_typ=None):
    assert list_arr_info_typ == types.List(array_info_type)
    return table_type(list_arr_info_typ), arr_info_list_to_table_codegen


def arr_info_list_to_table_codegen(context, builder, sig, args):
    surhc__fxh, = args
    wsi__fxjt = numba.cpython.listobj.ListInstance(context, builder, sig.
        args[0], surhc__fxh)
    rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
        IntType(8).as_pointer().as_pointer(), lir.IntType(64)])
    ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
        rdbcc__ngyql, name='arr_info_list_to_table')
    return builder.call(ywn__xfxpn, [wsi__fxjt.data, wsi__fxjt.size])


@intrinsic
def info_from_table(typingctx, table_t, ind_t):

    def codegen(context, builder, sig, args):
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='info_from_table')
        return builder.call(ywn__xfxpn, args)
    return array_info_type(table_t, ind_t), codegen


@intrinsic
def cpp_table_to_py_table(typingctx, cpp_table_t, table_idx_arr_t,
    py_table_type_t):
    assert cpp_table_t == table_type, 'invalid cpp table type'
    assert isinstance(table_idx_arr_t, types.Array
        ) and table_idx_arr_t.dtype == types.int64, 'invalid table index array'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    dkx__joas = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        yjh__qwoin, mmz__hxc, pqlkn__prjj = args
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64)])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='info_from_table')
        igy__hrgxy = cgutils.create_struct_proxy(dkx__joas)(context, builder)
        igy__hrgxy.parent = cgutils.get_null_value(igy__hrgxy.parent.type)
        qnd__uzz = context.make_array(table_idx_arr_t)(context, builder,
            mmz__hxc)
        sryv__ctdgn = context.get_constant(types.int64, -1)
        biae__ggdq = context.get_constant(types.int64, 0)
        afscy__kwuij = cgutils.alloca_once_value(builder, biae__ggdq)
        for t, zyn__lss in dkx__joas.type_to_blk.items():
            vtrm__ulfb = context.get_constant(types.int64, len(dkx__joas.
                block_to_arr_ind[zyn__lss]))
            pqlkn__prjj, lwbff__hub = ListInstance.allocate_ex(context,
                builder, types.List(t), vtrm__ulfb)
            lwbff__hub.size = vtrm__ulfb
            omgdq__cxi = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(dkx__joas.block_to_arr_ind[
                zyn__lss], dtype=np.int64))
            ttmby__uyid = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, omgdq__cxi)
            with cgutils.for_range(builder, vtrm__ulfb) as loop:
                fpb__qjk = loop.index
                bztdh__yoe = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    ttmby__uyid, fpb__qjk)
                yme__fubuz = _getitem_array_single_int(context, builder,
                    types.int64, table_idx_arr_t, qnd__uzz, bztdh__yoe)
                qjc__lmfqa = builder.icmp_unsigned('!=', yme__fubuz,
                    sryv__ctdgn)
                with builder.if_else(qjc__lmfqa) as (then, orelse):
                    with then:
                        ksg__rveg = builder.call(ywn__xfxpn, [yjh__qwoin,
                            yme__fubuz])
                        arr = context.compile_internal(builder, lambda info:
                            info_to_array(info, t), t(array_info_type), [
                            ksg__rveg])
                        lwbff__hub.inititem(fpb__qjk, arr, incref=False)
                        nerq__hfjn = context.compile_internal(builder, lambda
                            arr: len(arr), types.int64(t), [arr])
                        builder.store(nerq__hfjn, afscy__kwuij)
                    with orelse:
                        bqg__dqgf = context.get_constant_null(t)
                        lwbff__hub.inititem(fpb__qjk, bqg__dqgf, incref=False)
            setattr(igy__hrgxy, f'block_{zyn__lss}', lwbff__hub.value)
        igy__hrgxy.len = builder.load(afscy__kwuij)
        return igy__hrgxy._getvalue()
    return dkx__joas(cpp_table_t, table_idx_arr_t, py_table_type_t), codegen


@intrinsic
def py_table_to_cpp_table(typingctx, py_table_t, py_table_type_t):
    assert isinstance(py_table_t, bodo.hiframes.table.TableType
        ), 'invalid py table type'
    assert isinstance(py_table_type_t, types.TypeRef), 'invalid py table ref'
    dkx__joas = py_table_type_t.instance_type

    def codegen(context, builder, sig, args):
        oyqza__isx, pqlkn__prjj = args
        tkhah__vtkh = lir.Constant(lir.IntType(64), len(dkx__joas.arr_types))
        pqlkn__prjj, hzzz__jiz = ListInstance.allocate_ex(context, builder,
            types.List(array_info_type), tkhah__vtkh)
        hzzz__jiz.size = tkhah__vtkh
        kbc__tna = cgutils.create_struct_proxy(dkx__joas)(context, builder,
            oyqza__isx)
        for t, zyn__lss in dkx__joas.type_to_blk.items():
            vtrm__ulfb = context.get_constant(types.int64, len(dkx__joas.
                block_to_arr_ind[zyn__lss]))
            wmyl__toe = getattr(kbc__tna, f'block_{zyn__lss}')
            aydf__qxif = ListInstance(context, builder, types.List(t),
                wmyl__toe)
            omgdq__cxi = context.make_constant_array(builder, types.Array(
                types.int64, 1, 'C'), np.array(dkx__joas.block_to_arr_ind[
                zyn__lss], dtype=np.int64))
            ttmby__uyid = context.make_array(types.Array(types.int64, 1, 'C'))(
                context, builder, omgdq__cxi)
            with cgutils.for_range(builder, vtrm__ulfb) as loop:
                fpb__qjk = loop.index
                bztdh__yoe = _getitem_array_single_int(context, builder,
                    types.int64, types.Array(types.int64, 1, 'C'),
                    ttmby__uyid, fpb__qjk)
                bvv__ybti = signature(types.none, dkx__joas, types.List(t),
                    types.int64, types.int64)
                miv__xsju = oyqza__isx, wmyl__toe, fpb__qjk, bztdh__yoe
                bodo.hiframes.table.ensure_column_unboxed_codegen(context,
                    builder, bvv__ybti, miv__xsju)
                arr = aydf__qxif.getitem(fpb__qjk)
                ypdj__pgdsb = signature(array_info_type, t)
                tiu__pijwn = arr,
                bwsnh__dctn = array_to_info_codegen(context, builder,
                    ypdj__pgdsb, tiu__pijwn)
                hzzz__jiz.inititem(bztdh__yoe, bwsnh__dctn, incref=False)
        bqho__dcgy = hzzz__jiz.value
        xgee__ltrx = signature(table_type, types.List(array_info_type))
        ymgl__brv = bqho__dcgy,
        yjh__qwoin = arr_info_list_to_table_codegen(context, builder,
            xgee__ltrx, ymgl__brv)
        context.nrt.decref(builder, types.List(array_info_type), bqho__dcgy)
        return yjh__qwoin
    return table_type(dkx__joas, py_table_type_t), codegen


delete_info_decref_array = types.ExternalFunction('delete_info_decref_array',
    types.void(array_info_type))
delete_table_decref_arrays = types.ExternalFunction(
    'delete_table_decref_arrays', types.void(table_type))


@intrinsic
def delete_table(typingctx, table_t=None):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        rdbcc__ngyql = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='delete_table')
        builder.call(ywn__xfxpn, args)
    return types.void(table_t), codegen


@intrinsic
def shuffle_table(typingctx, table_t, n_keys_t, _is_parallel, keep_comm_info_t
    ):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(32)])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='shuffle_table')
        asgp__btiya = builder.call(ywn__xfxpn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return asgp__btiya
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
        rdbcc__ngyql = lir.FunctionType(lir.VoidType(), [lir.IntType(8).
            as_pointer()])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='delete_shuffle_info')
        return builder.call(ywn__xfxpn, args)
    return types.void(shuffle_info_t), codegen


@intrinsic
def reverse_shuffle_table(typingctx, table_t, shuffle_info_t=None):

    def codegen(context, builder, sig, args):
        if sig.args[-1] == types.none:
            return context.get_constant_null(table_type)
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='reverse_shuffle_table')
        return builder.call(ywn__xfxpn, args)
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
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(1), lir.IntType(1), lir.IntType(64), lir.IntType(64),
            lir.IntType(64), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(1), lir.IntType(1), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(64), lir
            .IntType(8).as_pointer(), lir.IntType(64)])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='hash_join_table')
        asgp__btiya = builder.call(ywn__xfxpn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return asgp__btiya
    return table_type(left_table_t, right_table_t, types.boolean, types.
        boolean, types.int64, types.int64, types.int64, types.voidptr,
        types.voidptr, types.boolean, types.boolean, types.boolean, types.
        boolean, types.boolean, types.boolean, types.voidptr, types.voidptr,
        types.int64, types.voidptr, types.int64), codegen


@intrinsic
def compute_node_partition_by_hash(typingctx, table_t, n_keys_t, n_pes_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(64)])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='compute_node_partition_by_hash')
        asgp__btiya = builder.call(ywn__xfxpn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return asgp__btiya
    return table_type(table_t, types.int64, types.int64), codegen


@intrinsic
def sort_values_table(typingctx, table_t, n_keys_t, vect_ascending_t,
    na_position_b_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1)])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='sort_values_table')
        asgp__btiya = builder.call(ywn__xfxpn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return asgp__btiya
    return table_type(table_t, types.int64, types.voidptr, types.voidptr,
        types.boolean), codegen


@intrinsic
def sample_table(typingctx, table_t, n_keys_t, frac_t, replace_t, parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.DoubleType(), lir
            .IntType(1), lir.IntType(1)])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='sample_table')
        asgp__btiya = builder.call(ywn__xfxpn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return asgp__btiya
    return table_type(table_t, types.int64, types.float64, types.boolean,
        types.boolean), codegen


@intrinsic
def shuffle_renormalization(typingctx, table_t, random_t, random_seed_t,
    is_parallel_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1)])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='shuffle_renormalization')
        asgp__btiya = builder.call(ywn__xfxpn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return asgp__btiya
    return table_type(table_t, types.int32, types.int64, types.boolean
        ), codegen


@intrinsic
def shuffle_renormalization_group(typingctx, table_t, random_t,
    random_seed_t, is_parallel_t, num_ranks_t, ranks_t):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(32), lir.IntType(64), lir.
            IntType(1), lir.IntType(64), lir.IntType(8).as_pointer()])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='shuffle_renormalization_group')
        asgp__btiya = builder.call(ywn__xfxpn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return asgp__btiya
    return table_type(table_t, types.int32, types.int64, types.boolean,
        types.int64, types.voidptr), codegen


@intrinsic
def drop_duplicates_table(typingctx, table_t, parallel_t, nkey_t, keep_t,
    dropna):
    assert table_t == table_type

    def codegen(context, builder, sig, args):
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(64), lir.
            IntType(64), lir.IntType(1)])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='drop_duplicates_table')
        asgp__btiya = builder.call(ywn__xfxpn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return asgp__btiya
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
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(1), lir.IntType(1), lir.IntType(1), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer(), lir.IntType(8).
            as_pointer(), lir.IntType(8).as_pointer()])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='pivot_groupby_and_aggregate')
        asgp__btiya = builder.call(ywn__xfxpn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return asgp__btiya
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
        rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(), [lir.
            IntType(8).as_pointer(), lir.IntType(64), lir.IntType(1), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(1), lir.IntType(1), lir.
            IntType(64), lir.IntType(64), lir.IntType(64), lir.IntType(1),
            lir.IntType(1), lir.IntType(1), lir.IntType(8).as_pointer(),
            lir.IntType(8).as_pointer(), lir.IntType(8).as_pointer(), lir.
            IntType(8).as_pointer(), lir.IntType(8).as_pointer()])
        ywn__xfxpn = cgutils.get_or_insert_function(builder.module,
            rdbcc__ngyql, name='groupby_and_aggregate')
        asgp__btiya = builder.call(ywn__xfxpn, args)
        context.compile_internal(builder, lambda :
            check_and_propagate_cpp_exception(), types.none(), [])
        return asgp__btiya
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
    yur__mdam = array_to_info(in_arr)
    ubyh__rukiq = array_to_info(in_values)
    skf__qqjei = array_to_info(out_arr)
    jsx__sdtuh = arr_info_list_to_table([yur__mdam, ubyh__rukiq, skf__qqjei])
    _array_isin(skf__qqjei, yur__mdam, ubyh__rukiq, is_parallel)
    check_and_propagate_cpp_exception()
    delete_table(jsx__sdtuh)


_get_search_regex = types.ExternalFunction('get_search_regex', types.void(
    array_info_type, types.bool_, types.voidptr, array_info_type))


@numba.njit
def get_search_regex(in_arr, case, pat, out_arr):
    yur__mdam = array_to_info(in_arr)
    skf__qqjei = array_to_info(out_arr)
    _get_search_regex(yur__mdam, case, pat, skf__qqjei)
    check_and_propagate_cpp_exception()


def _gen_row_access_intrinsic(col_dtype, c_ind):
    from llvmlite import ir as lir
    if isinstance(col_dtype, types.Number) or col_dtype in [bodo.
        datetime_date_type, bodo.datetime64ns, bodo.timedelta64ns, types.bool_
        ]:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                igy__hrgxy, egei__hkg = args
                igy__hrgxy = builder.bitcast(igy__hrgxy, lir.IntType(8).
                    as_pointer().as_pointer())
                duuw__vhjt = lir.Constant(lir.IntType(64), c_ind)
                rrosv__eztgt = builder.load(builder.gep(igy__hrgxy, [
                    duuw__vhjt]))
                rrosv__eztgt = builder.bitcast(rrosv__eztgt, context.
                    get_data_type(col_dtype).as_pointer())
                return builder.load(builder.gep(rrosv__eztgt, [egei__hkg]))
            return col_dtype(types.voidptr, types.int64), codegen
        return getitem_func
    if col_dtype == types.unicode_type:

        @intrinsic
        def getitem_func(typingctx, table_t, ind_t):

            def codegen(context, builder, sig, args):
                igy__hrgxy, egei__hkg = args
                rdbcc__ngyql = lir.FunctionType(lir.IntType(8).as_pointer(),
                    [lir.IntType(8).as_pointer(), lir.IntType(64), lir.
                    IntType(64), lir.IntType(64).as_pointer()])
                ecl__hvic = cgutils.get_or_insert_function(builder.module,
                    rdbcc__ngyql, name='array_info_getitem')
                duuw__vhjt = lir.Constant(lir.IntType(64), c_ind)
                baws__olq = cgutils.alloca_once(builder, lir.IntType(64))
                args = igy__hrgxy, duuw__vhjt, egei__hkg, baws__olq
                rlc__pzs = builder.call(ecl__hvic, args)
                return context.make_tuple(builder, sig.return_type, [
                    rlc__pzs, builder.load(baws__olq)])
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
                dhq__ejl, egei__hkg = args
                dhq__ejl = builder.bitcast(dhq__ejl, lir.IntType(8).
                    as_pointer().as_pointer())
                duuw__vhjt = lir.Constant(lir.IntType(64), c_ind)
                rrosv__eztgt = builder.load(builder.gep(dhq__ejl, [duuw__vhjt])
                    )
                pdf__kumlk = builder.bitcast(rrosv__eztgt, context.
                    get_data_type(types.bool_).as_pointer())
                aieb__qra = bodo.utils.cg_helpers.get_bitmap_bit(builder,
                    pdf__kumlk, egei__hkg)
                rck__lxfce = builder.icmp_unsigned('!=', aieb__qra, lir.
                    Constant(lir.IntType(8), 0))
                return builder.sext(rck__lxfce, lir.IntType(8))
            return types.int8(types.voidptr, types.int64), codegen
        return checkna_func
    elif isinstance(col_array_dtype, types.Array):
        col_dtype = col_array_dtype.dtype
        if col_dtype in [bodo.datetime64ns, bodo.timedelta64ns]:

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    igy__hrgxy, egei__hkg = args
                    igy__hrgxy = builder.bitcast(igy__hrgxy, lir.IntType(8)
                        .as_pointer().as_pointer())
                    duuw__vhjt = lir.Constant(lir.IntType(64), c_ind)
                    rrosv__eztgt = builder.load(builder.gep(igy__hrgxy, [
                        duuw__vhjt]))
                    rrosv__eztgt = builder.bitcast(rrosv__eztgt, context.
                        get_data_type(col_dtype).as_pointer())
                    fokjj__jrxk = builder.load(builder.gep(rrosv__eztgt, [
                        egei__hkg]))
                    rck__lxfce = builder.icmp_unsigned('!=', fokjj__jrxk,
                        lir.Constant(lir.IntType(64), pd._libs.iNaT))
                    return builder.sext(rck__lxfce, lir.IntType(8))
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
        elif isinstance(col_dtype, types.Float):

            @intrinsic
            def checkna_func(typingctx, table_t, ind_t):

                def codegen(context, builder, sig, args):
                    igy__hrgxy, egei__hkg = args
                    igy__hrgxy = builder.bitcast(igy__hrgxy, lir.IntType(8)
                        .as_pointer().as_pointer())
                    duuw__vhjt = lir.Constant(lir.IntType(64), c_ind)
                    rrosv__eztgt = builder.load(builder.gep(igy__hrgxy, [
                        duuw__vhjt]))
                    rrosv__eztgt = builder.bitcast(rrosv__eztgt, context.
                        get_data_type(col_dtype).as_pointer())
                    fokjj__jrxk = builder.load(builder.gep(rrosv__eztgt, [
                        egei__hkg]))
                    mpe__nxqm = signature(types.bool_, col_dtype)
                    aieb__qra = numba.np.npyfuncs.np_real_isnan_impl(context,
                        builder, mpe__nxqm, (fokjj__jrxk,))
                    return builder.not_(builder.sext(aieb__qra, lir.IntType(8))
                        )
                return types.int8(types.voidptr, types.int64), codegen
            return checkna_func
    raise BodoError(
        f"General Join Conditions with '{col_array_dtype}' column type not supported"
        )
